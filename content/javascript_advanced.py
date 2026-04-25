"""JavaScript · Advanced · Detailed answers. Each value is an HTML snippet."""

ANSWERS = {}

ANSWERS[1] = r'''
<p><strong>Prototypal</strong> inheritance delegates: objects link to other objects, and property lookups walk up this chain dynamically. <strong>Classical</strong> inheritance (Java, C++) uses classes as templates that are copied/instantiated at compile time.</p>
<pre><code>// Prototypal
const animal = { eats: true };
const rabbit = Object.create(animal);
rabbit.jumps = true;
rabbit.eats;    // found via delegation — not copied

// ES6 class is still prototypal under the hood
class Animal { eat() {} }
class Rabbit extends Animal { jump() {} }</code></pre>
<table>
  <thead><tr><th>Prototypal</th><th>Classical</th></tr></thead>
  <tbody>
    <tr><td>Dynamic — change prototype at runtime</td><td>Static — shape fixed at compile time</td></tr>
    <tr><td>Per-object delegation</td><td>Per-class template</td></tr>
    <tr><td>Memory-efficient (methods shared via proto)</td><td>Methods defined once on class</td></tr>
    <tr><td>Simpler primitives, flexible composition</td><td>Rigid hierarchies, compile-time type checks</td></tr>
  </tbody>
</table>
<p>JavaScript's model favors composition and mixins. Deep class hierarchies tend to feel unnatural.</p>
'''

ANSWERS[2] = r'''
<p><strong>Event delegation</strong> places one listener on a common ancestor and uses <code>event.target</code> (plus <code>closest()</code>) to identify which descendant fired the event. It works because most DOM events bubble.</p>
<pre><code>document.querySelector("#list").addEventListener("click", (e) =&gt; {
  const item = e.target.closest(".item");
  if (!item) return;
  const id = item.dataset.id;
  handle(id);
});</code></pre>
<p>Advantages:</p>
<ul>
  <li><strong>Fewer listeners</strong> — less memory, faster setup.</li>
  <li><strong>Dynamic children</strong> — newly added items work without re-binding.</li>
  <li><strong>Cleaner teardown</strong> — one <code>removeEventListener</code> unhooks everything.</li>
</ul>
<p>Caveats: some events don't bubble (<code>focus</code>, <code>blur</code>, <code>mouseenter</code>). Use their bubbling versions (<code>focusin</code>, <code>mouseover</code>) or capture phase (<code>addEventListener(type, fn, { capture: true })</code>).</p>
'''

ANSWERS[3] = r'''
<p>Both create objects, but they differ in <em>what</em> is set and <em>how</em>.</p>
<pre><code>// Constructor — sets instance via `this` AND prototype chain
function User(name) { this.name = name; }
User.prototype.greet = function () { return `hi ${this.name}`; };
const a = new User("Ana");

// Object.create — sets prototype directly, no constructor call
const proto = { greet() { return `hi ${this.name}`; } };
const b = Object.create(proto);
b.name = "Bob";</code></pre>
<table>
  <thead><tr><th></th><th>Constructor</th><th>Object.create</th></tr></thead>
  <tbody>
    <tr><td>Calls function body</td><td>Yes</td><td>No</td></tr>
    <tr><td>Sets prototype</td><td>From <code>Fn.prototype</code></td><td>From the arg</td></tr>
    <tr><td>Initializes fields</td><td>Via <code>this</code></td><td>Manual after</td></tr>
    <tr><td>Works with <code>instanceof</code></td><td>Yes</td><td>Chain-based check</td></tr>
  </tbody>
</table>
<p><code>Object.create(null)</code> makes a dictionary with no prototype — safe for untrusted keys (no <code>__proto__</code> traps).</p>
'''

ANSWERS[4] = r'''
<p>A <strong>mixin</strong> shares behavior across unrelated classes without inheritance.</p>
<pre><code>// Object mixin — copy methods
const serializable = {
  toJSON() { return JSON.stringify(this); },
  fromJSON(s) { return Object.assign(this, JSON.parse(s)); }
};
Object.assign(User.prototype, serializable);

// Functional mixin — takes a base class, returns an extended one
const Timestamped = (Base) =&gt; class extends Base {
  constructor(...args) { super(...args); this.createdAt = Date.now(); }
};
const Loggable = (Base) =&gt; class extends Base {
  log() { console.log(this); }
};
class Order extends Loggable(Timestamped(Base)) {}</code></pre>
<p>Functional mixins compose cleanly (<code>A(B(C))</code>), avoid deep prototype chains, and let you &ldquo;mix&rdquo; only what each class needs. Watch out for method-name collisions — later mixins overwrite earlier ones.</p>
'''

ANSWERS[5] = r'''
<p>A <strong>synchronous exception</strong> propagates up the call stack until caught by a <code>try/catch</code>. An <strong>asynchronous exception</strong> occurs after the synchronous call has returned — there's no stack to unwind to.</p>
<pre><code>// Sync — caught
try { throw new Error("boom"); } catch (e) { /* here */ }

// Async — NOT caught by outer try/catch
try {
  setTimeout(() =&gt; { throw new Error("boom"); }, 0);
} catch (e) { /* never runs */ }

// Promise rejection — caught by .catch or try/await
try {
  await doAsync();   // rejections ARE caught here
} catch (e) { /* here */ }</code></pre>
<p>Async errors must be caught at the site that scheduled them: <code>.catch</code> on promises, error listeners on emitters, <code>try/catch</code> around <code>await</code>. Unhandled cases go to <code>window.onerror</code>, <code>process.on("unhandledRejection")</code>, or the console.</p>
'''

ANSWERS[6] = r'''
<p>The runtime (browser or Node) has non-JS threads for I/O, timers, and network. JS stays single-threaded, coordinating through queues.</p>
<ol>
  <li>JS calls an async API (e.g., <code>fetch</code>, <code>setTimeout</code>, <code>fs.readFile</code>). The API hands work to the runtime.</li>
  <li>The runtime performs the work off the main thread. When done, it pushes a callback/microtask into the appropriate queue.</li>
  <li>The <strong>event loop</strong> runs: when the call stack is empty, drain all microtasks, then take one macrotask, then repeat.</li>
</ol>
<pre><code>console.log("1");
setTimeout(() =&gt; console.log("2"), 0);   // macrotask
Promise.resolve().then(() =&gt; console.log("3")); // microtask
console.log("4");
// Order: 1, 4, 3, 2</code></pre>
<p>Microtasks (promise <code>.then</code>, <code>queueMicrotask</code>) run before the next macrotask. Long synchronous work blocks everything because the loop never gets to drain queues.</p>
'''

ANSWERS[7] = r'''
<p>Both take an iterable of promises. They differ in when they settle.</p>
<table>
  <thead><tr><th></th><th><code>Promise.all</code></th><th><code>Promise.race</code></th></tr></thead>
  <tbody>
    <tr><td>Resolves when</td><td>All fulfill</td><td>Any settles (fulfill or reject)</td></tr>
    <tr><td>Rejects when</td><td>Any reject (fast-fail)</td><td>Any rejects first</td></tr>
    <tr><td>Value</td><td>Array of all values</td><td>First settled value</td></tr>
    <tr><td>Use case</td><td>Parallel fetches, wait for all</td><td>Timeouts, first-response wins</td></tr>
  </tbody>
</table>
<pre><code>// all — wait for complete dataset
const [user, posts] = await Promise.all([fetchUser(), fetchPosts()]);

// race — timeout pattern
const result = await Promise.race([
  fetch(url),
  new Promise((_, rej) =&gt; setTimeout(() =&gt; rej(new Error("timeout")), 5000))
]);</code></pre>
<p>Companions: <code>Promise.allSettled</code> (never rejects, array of status objects), <code>Promise.any</code> (first fulfillment wins; ignores rejections).</p>
'''

ANSWERS[8] = r'''
<p>Listen for unhandled rejections at the top level.</p>
<pre><code>// Browser
window.addEventListener("unhandledrejection", (event) =&gt; {
  console.error("Unhandled:", event.reason);
  reportToServer(event.reason);
  event.preventDefault();
});

// Node.js
process.on("unhandledRejection", (reason, promise) =&gt; {
  console.error("Unhandled rejection:", reason);
});
process.on("uncaughtException", (err) =&gt; {
  logger.fatal(err);
  process.exit(1);           // let the process manager restart you
});</code></pre>
<p>Strategy:</p>
<ul>
  <li>Always put <code>.catch()</code> on promise chains, or <code>try/catch</code> around <code>await</code>.</li>
  <li>Use <code>Promise.allSettled</code> when partial failures are acceptable.</li>
  <li>In Node, treat <code>uncaughtException</code> as fatal — log and exit; the process is in an unknown state.</li>
  <li>Surface async errors in structured observability (Sentry, Rollbar, etc.).</li>
</ul>
'''

ANSWERS[9] = r'''
<p>The <strong>microtask queue</strong> holds callbacks from <code>Promise.then/catch/finally</code>, <code>queueMicrotask</code>, and <code>MutationObserver</code>. The event loop drains <em>all</em> microtasks between each macrotask (timer, I/O, UI event).</p>
<pre><code>setTimeout(() =&gt; console.log("macro"), 0);
Promise.resolve().then(() =&gt; {
  console.log("micro 1");
  Promise.resolve().then(() =&gt; console.log("micro 2"));
});
console.log("sync");
// sync, micro 1, micro 2, macro</code></pre>
<p>Key implications:</p>
<ul>
  <li>Microtasks have <strong>priority</strong> over macrotasks — a flood of microtasks can starve timers and rendering.</li>
  <li>Awaiting a resolved promise yields control but reruns very soon (next microtask tick), not on the next macrotask.</li>
  <li>DOM updates happen on macrotask boundaries, so a long microtask chain delays repaint.</li>
</ul>
'''

ANSWERS[10] = r'''
<p><strong>Monkey patching</strong> means mutating built-ins or someone else's code at runtime (<code>Array.prototype.myFn = ...</code>).</p>
<p>Risks:</p>
<ul>
  <li><strong>Name collisions</strong> — two patches compete; whichever loads last wins.</li>
  <li><strong>Future-proof breakage</strong> — the language may later ship a native method with the same name but different semantics (this killed lots of pre-ES6 polyfills).</li>
  <li><strong>Non-local reasoning</strong> — code that looks like plain <code>arr.map(...)</code> can behave differently in any file.</li>
  <li><strong>Harder debugging</strong> — a &ldquo;mysterious&rdquo; method has no obvious definition site.</li>
  <li><strong>Performance</strong> — engine optimizations that rely on built-in shapes can deopt.</li>
</ul>
<p>Safer alternatives: utility modules (<code>lodash</code>), subclasses (<code>class MyArr extends Array</code>), wrapper functions, or explicit <code>Symbol</code>-keyed extensions when you must patch.</p>
'''

ANSWERS[11] = r'''
<p>Maintain a <code>WeakMap</code> from &ldquo;original → copy&rdquo; to detect revisits.</p>
<pre><code>function deepClone(v, seen = new WeakMap()) {
  if (v === null || typeof v !== "object") return v;
  if (seen.has(v)) return seen.get(v);       // break the cycle

  const copy = Array.isArray(v) ? [] : Object.create(Object.getPrototypeOf(v));
  seen.set(v, copy);                          // record BEFORE recursing

  for (const k of Reflect.ownKeys(v)) {
    copy[k] = deepClone(v[k], seen);
  }
  return copy;
}

// Modern alternative — handles cycles natively
const copy = structuredClone(obj);</code></pre>
<p>The critical ordering: record the copy in <code>seen</code> <em>before</em> recursing. Otherwise a cycle back to <code>v</code> would recurse forever. <code>WeakMap</code> is ideal because it doesn't prevent garbage collection of the originals once cloning finishes.</p>
'''

ANSWERS[12] = r'''
<p><code>Symbol</code> is a primitive type that produces <strong>unique, immutable</strong> identifiers. Two symbols with the same description are still distinct.</p>
<pre><code>const id = Symbol("id");
const obj = { [id]: 123 };
Object.keys(obj);          // [] — symbols are skipped
obj[id];                   // 123</code></pre>
<p>Uses:</p>
<ul>
  <li><strong>Collision-proof keys</strong> for libraries: <code>lib[Symbol("_cache")]</code> won't clash with user keys.</li>
  <li><strong>Protocol hooks</strong> via well-known symbols: <code>Symbol.iterator</code>, <code>Symbol.asyncIterator</code>, <code>Symbol.toPrimitive</code>, <code>Symbol.hasInstance</code>.</li>
  <li><strong>Private-ish state</strong> (not truly private — <code>Object.getOwnPropertySymbols</code> still finds them).</li>
  <li><strong>Global registry</strong>: <code>Symbol.for("x")</code> returns the same symbol across realms.</li>
</ul>
<pre><code>class Range {
  constructor(n) { this.n = n; }
  *[Symbol.iterator]() { for (let i = 0; i &lt; this.n; i++) yield i; }
}
[...new Range(3)];   // [0, 1, 2]</code></pre>
'''

ANSWERS[13] = r'''
<p>A lightweight pub/sub bus.</p>
<pre><code>class EventBus {
  constructor() { this.handlers = new Map(); }

  on(event, fn) {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set());
    this.handlers.get(event).add(fn);
    return () =&gt; this.off(event, fn);         // unsubscribe handle
  }

  off(event, fn) {
    this.handlers.get(event)?.delete(fn);
  }

  emit(event, payload) {
    for (const fn of this.handlers.get(event) ?? []) {
      try { fn(payload); }
      catch (e) { console.error(e); }
    }
  }
}

const bus = new EventBus();
const unsub = bus.on("user:login", (u) =&gt; console.log("hi", u));
bus.emit("user:login", { name: "Ana" });
unsub();</code></pre>
<p>Using a <code>Set</code> dedupes handlers. Wrapping emit calls in try/catch prevents one bad subscriber from breaking the rest.</p>
'''

ANSWERS[14] = r'''
<p>Both iterate object keys, but they differ in scope.</p>
<table>
  <thead><tr><th></th><th><code>for...in</code></th><th><code>Object.keys()</code></th></tr></thead>
  <tbody>
    <tr><td>Walks prototype chain</td><td>Yes</td><td>No — own keys only</td></tr>
    <tr><td>Non-enumerable keys</td><td>Skipped</td><td>Skipped</td></tr>
    <tr><td>Symbol keys</td><td>Skipped</td><td>Skipped</td></tr>
    <tr><td>Returns</td><td>Iteration over keys</td><td>Array of keys</td></tr>
    <tr><td>Use with arrays</td><td>Avoid (includes index-like strings)</td><td>Avoid (use array methods)</td></tr>
  </tbody>
</table>
<pre><code>const parent = { inherited: 1 };
const obj = Object.create(parent);
obj.own = 2;

for (const k in obj) console.log(k);  // "own", "inherited"
Object.keys(obj);                     // ["own"]</code></pre>
<p>Prefer <code>Object.keys / entries / values</code> for deterministic, own-property iteration. Use <code>Reflect.ownKeys</code> to also include symbols and non-enumerables.</p>
'''

ANSWERS[15] = r'''
<p>A state machine is a set of <em>states</em>, an <em>initial state</em>, and transitions triggered by events.</p>
<pre><code>function createMachine(config) {
  let state = config.initial;
  return {
    get state() { return state; },
    send(event) {
      const transitions = config.states[state]?.on;
      const next = transitions?.[event];
      if (next) {
        config.states[state]?.onExit?.();
        state = next;
        config.states[state]?.onEntry?.();
      }
    }
  };
}

const traffic = createMachine({
  initial: "red",
  states: {
    red:    { on: { TICK: "green"  } },
    green:  { on: { TICK: "yellow" } },
    yellow: { on: { TICK: "red"    } }
  }
});
traffic.send("TICK"); traffic.state;  // "green"</code></pre>
<p>For production UI, use XState — it handles hierarchical states, guards, context, and history out of the box.</p>
'''

ANSWERS[16] = r'''
<p>V8 and similar engines group objects by their &ldquo;shape&rdquo; (also called <em>hidden class</em> or <em>map</em>). Objects with the same property order share the same shape, enabling fast inline-cached property access.</p>
<pre><code>function Point(x, y) { this.x = x; this.y = y; }
const p1 = new Point(1, 2);   // shape: {x, y}
const p2 = new Point(3, 4);   // same shape — cached access

// Adding a property in a different order breaks the cache
p1.z = 5;   // shape: {x, y, z}
p2.w = 6;   // shape: {x, y, w} — different!</code></pre>
<p>Optimizations:</p>
<ul>
  <li><strong>Inline caches</strong> — after seeing the same shape N times, property access compiles to a direct offset lookup.</li>
  <li><strong>Hidden class transitions</strong> — adding properties in a consistent order keeps objects on the same shape chain.</li>
  <li><strong>Deoptimization</strong> triggers: deleting properties, adding properties out of order, using <code>with</code> or <code>eval</code>, mixed types on the same slot.</li>
</ul>
<p>Practical advice: initialize all fields in the constructor in the same order; don't <code>delete</code> properties from hot objects.</p>
'''

ANSWERS[17] = r'''
<p>Cache results keyed by arguments.</p>
<pre><code>function memoize(fn, keyFn = JSON.stringify) {
  const cache = new Map();
  return function (...args) {
    const k = keyFn(args);
    if (cache.has(k)) return cache.get(k);
    const result = fn.apply(this, args);
    cache.set(k, result);
    return result;
  };
}

// With LRU eviction
function memoizeLRU(fn, max = 100) {
  const cache = new Map();
  return function (...args) {
    const k = JSON.stringify(args);
    if (cache.has(k)) {
      const v = cache.get(k);
      cache.delete(k); cache.set(k, v);   // promote to &ldquo;most recent&rdquo;
      return v;
    }
    const result = fn.apply(this, args);
    cache.set(k, result);
    if (cache.size &gt; max) cache.delete(cache.keys().next().value);  // evict oldest
    return result;
  };
}</code></pre>
<p>Caveats: <code>JSON.stringify</code> can't key functions/Symbols; the cache can leak memory if the function accepts many unique inputs. Prefer <code>WeakMap</code> when arguments are objects you want to allow GC on.</p>
'''

ANSWERS[18] = r'''
<p>Three broad categories:</p>
<h4>1. Reduce main-thread work</h4>
<ul>
  <li>Debounce / throttle event handlers.</li>
  <li>Use <code>requestIdleCallback</code> / <code>requestAnimationFrame</code> to schedule non-urgent work.</li>
  <li>Move CPU-heavy tasks to Web Workers.</li>
  <li>Virtualize long lists — render only what's visible.</li>
</ul>
<h4>2. Ship less code faster</h4>
<ul>
  <li>Code splitting + dynamic <code>import()</code>.</li>
  <li>Tree shaking and dead-code elimination.</li>
  <li>Minify, compress (gzip/brotli), HTTP/2 or HTTP/3.</li>
  <li>Preload / prefetch critical assets.</li>
</ul>
<h4>3. Runtime hygiene</h4>
<ul>
  <li>Avoid repeated DOM reads/writes — batch via <code>DocumentFragment</code> or layout-thrashing libraries.</li>
  <li>Cache expensive computations (memoization).</li>
  <li>Avoid memory leaks (detached nodes, forgotten listeners/intervals).</li>
  <li>Use monomorphic functions — don't mix types on the same call site.</li>
</ul>
<p>Measure with Lighthouse, DevTools Performance panel, and RUM data before optimizing — assumptions about bottlenecks are usually wrong.</p>
'''

ANSWERS[19] = r'''
<p>Chunk the file and upload in parallel, with resume support.</p>
<pre><code>async function uploadInChunks(file, url, chunkSize = 5 * 1024 * 1024) {
  const total = Math.ceil(file.size / chunkSize);
  const uploadId = crypto.randomUUID();

  for (let i = 0; i &lt; total; i++) {
    const blob = file.slice(i * chunkSize, (i + 1) * chunkSize);
    const fd = new FormData();
    fd.append("chunk", blob);
    fd.append("uploadId", uploadId);
    fd.append("index", i);
    fd.append("total", total);

    await fetch(url, { method: "POST", body: fd });
    report((i + 1) / total);
  }
  await fetch(url + "/complete", { method: "POST", body: JSON.stringify({ uploadId }) });
}</code></pre>
<p>Production considerations:</p>
<ul>
  <li><strong>Parallelism</strong> — upload N chunks concurrently (limit so you don't saturate bandwidth).</li>
  <li><strong>Resume</strong> — server reports which chunks it already has; skip those on retry.</li>
  <li><strong>Checksum</strong> each chunk (SHA-256) to catch corruption.</li>
  <li><strong>Streaming alternative</strong> — <code>ReadableStream</code> + <code>fetch</code> for direct pipe-through.</li>
  <li>Use signed URLs for direct-to-S3 uploads to skip your server entirely.</li>
</ul>
'''

ANSWERS[20] = r'''
<p><strong>Web Workers</strong> run JavaScript in a separate thread with no DOM access. They communicate with the main thread via <code>postMessage</code> (structured-cloned, or zero-copy via <code>Transferable</code>).</p>
<pre><code>// main.js
const worker = new Worker("heavy.js");
worker.postMessage({ data });
worker.onmessage = (e) =&gt; render(e.data);

// heavy.js
self.onmessage = (e) =&gt; {
  const result = expensive(e.data);
  self.postMessage(result);
};</code></pre>
<p>When to use:</p>
<ul>
  <li>Parsing huge JSON / CSV files.</li>
  <li>Image/video processing, encryption, compression.</li>
  <li>Pathfinding, physics, ML inference.</li>
  <li>Any compute that would block the UI for more than ~50ms.</li>
</ul>
<p>Variants: <strong>Shared Workers</strong> (shared across tabs of the same origin), <strong>Service Workers</strong> (network proxy, offline cache), <strong>Worklets</strong> (audio, paint, layout — even more restricted). Overhead of <code>postMessage</code> makes workers unhelpful for very small tasks.</p>
'''

ANSWERS[21] = r'''
<p>The GC can only free what it proves is unreachable. Leaks happen when code unintentionally keeps references alive.</p>
<h4>Common sources</h4>
<ul>
  <li><strong>Accidental globals</strong> — missing <code>let</code>/<code>const</code> creates a global.</li>
  <li><strong>Detached DOM</strong> — nodes removed from the DOM but still referenced by JS (e.g., in an array or closure).</li>
  <li><strong>Event listeners</strong> not removed when a component unmounts.</li>
  <li><strong>Timers/intervals</strong> that outlive the object they reference.</li>
  <li><strong>Closures</strong> capturing large scopes.</li>
  <li><strong>Caches without eviction</strong> — <code>Map</code> keyed by objects grows forever.</li>
</ul>
<h4>Mitigations</h4>
<ul>
  <li>Use <code>WeakMap</code>/<code>WeakSet</code>/<code>WeakRef</code> when the map/set shouldn't keep its keys alive.</li>
  <li>Always pair <code>addEventListener</code> with <code>removeEventListener</code> (or use <code>AbortController</code>).</li>
  <li>Clear timers on cleanup.</li>
  <li>Use Chrome DevTools heap snapshots: take two snapshots, diff them, look for unexpectedly retained objects.</li>
</ul>
'''

ANSWERS[22] = r'''
<p><strong>Tail call optimization (TCO)</strong> reuses the current stack frame for a function call in tail position, allowing unbounded recursion without stack overflow.</p>
<pre><code>// Tail call — return is the ONLY thing around the call
function fact(n, acc = 1) {
  if (n &lt;= 1) return acc;
  return fact(n - 1, acc * n);   // tail call
}

// Not a tail call — must add 1 after return
function length(list) {
  if (!list) return 0;
  return 1 + length(list.next);  // not a tail call
}</code></pre>
<p><strong>Reality check:</strong> TCO is in the ES6 spec, but only Safari/WebKit implements it. V8 (Chrome, Node) explicitly doesn't, citing concerns about debugging (lost stack frames). In practice you cannot rely on TCO in the browser — rewrite deep recursion as iteration or manual stacks.</p>
<pre><code>// Iterative equivalent — always safe
function factIter(n) {
  let acc = 1;
  while (n &gt; 1) acc *= n--;
  return acc;
}</code></pre>
'''

ANSWERS[23] = r'''
<p>Three levels of freezing, in increasing strictness.</p>
<table>
  <thead><tr><th></th><th>Add props?</th><th>Remove props?</th><th>Modify existing?</th><th>Reconfigure?</th></tr></thead>
  <tbody>
    <tr><td><code>preventExtensions</code></td><td>No</td><td>Yes</td><td>Yes</td><td>Yes</td></tr>
    <tr><td><code>seal</code></td><td>No</td><td>No</td><td>Yes</td><td>No</td></tr>
    <tr><td><code>freeze</code></td><td>No</td><td>No</td><td>No</td><td>No</td></tr>
  </tbody>
</table>
<pre><code>const a = {x: 1};
Object.freeze(a);
a.x = 99;          // silently ignored (throws in strict mode)
a.y = 1;           // silently ignored
delete a.x;        // silently ignored</code></pre>
<p>All three are <strong>shallow</strong> — nested objects are still mutable.</p>
<pre><code>function deepFreeze(o) {
  for (const v of Object.values(o)) {
    if (v && typeof v === "object") deepFreeze(v);
  }
  return Object.freeze(o);
}</code></pre>
<p>Check with <code>Object.isExtensible</code>, <code>Object.isSealed</code>, <code>Object.isFrozen</code>.</p>
'''

ANSWERS[24] = r'''
<p>An iterable implements <code>Symbol.iterator</code> returning an iterator (an object with <code>next()</code> → <code>{value, done}</code>).</p>
<pre><code>class Range {
  constructor(start, end, step = 1) {
    this.start = start; this.end = end; this.step = step;
  }
  [Symbol.iterator]() {
    let i = this.start, end = this.end, step = this.step;
    return {
      next() {
        return i &lt; end
          ? { value: (i += step) - step, done: false }
          : { value: undefined, done: true };
      },
      return() { return { done: true }; }  // optional — runs on early exit
    };
  }
}

for (const n of new Range(1, 5)) console.log(n);  // 1, 2, 3, 4
[...new Range(1, 4)];                              // [1, 2, 3]</code></pre>
<p>Generators make this easier — they return iterators automatically.</p>
<pre><code>class Range2 {
  constructor(start, end) { this.start = start; this.end = end; }
  *[Symbol.iterator]() {
    for (let i = this.start; i &lt; this.end; i++) yield i;
  }
}</code></pre>
<p>Once iterable, your object works with <code>for...of</code>, spread, destructuring, <code>Array.from</code>, and <code>new Map/Set</code>.</p>
'''

ANSWERS[25] = r'''
<table>
  <thead><tr><th></th><th>Monolithic</th><th>Modular</th></tr></thead>
  <tbody>
    <tr><td>Code organization</td><td>Single deployable unit</td><td>Multiple packages / services</td></tr>
    <tr><td>Initial complexity</td><td>Low</td><td>Higher — needs tooling</td></tr>
    <tr><td>Coordination overhead</td><td>Low — one repo, one build</td><td>Versioning, contracts between modules</td></tr>
    <tr><td>Scalability (team)</td><td>Gets painful past ~10 devs</td><td>Teams own modules independently</td></tr>
    <tr><td>Scalability (runtime)</td><td>Scale the whole thing</td><td>Scale hot services independently</td></tr>
    <tr><td>Deployment</td><td>Deploy everything together</td><td>Deploy modules independently</td></tr>
    <tr><td>Debugging</td><td>Stack trace crosses whole app</td><td>Distributed — harder to trace</td></tr>
  </tbody>
</table>
<p><strong>Practical advice:</strong> start monolithic. Most teams don't need microservices; premature modularization creates more pain than it solves. Extract a module/service when boundaries become obvious (team friction, scale hotspots, tech-stack divergence). Martin Fowler's &ldquo;monolith first&rdquo; is the safer default.</p>
'''

ANSWERS[26] = r'''
<p>Currying transforms <code>f(a, b, c)</code> into <code>f(a)(b)(c)</code> — a chain of unary functions.</p>
<pre><code>const curry = (fn) =&gt; {
  return function curried(...args) {
    if (args.length &gt;= fn.length) return fn.apply(this, args);
    return (...more) =&gt; curried.apply(this, [...args, ...more]);
  };
};

const add = (a, b, c) =&gt; a + b + c;
const cadd = curry(add);

cadd(1)(2)(3);      // 6
cadd(1, 2)(3);      // 6
cadd(1)(2, 3);      // 6</code></pre>
<p>Why it's useful:</p>
<ul>
  <li><strong>Partial application</strong>: fix some args, specialize for later.</li>
  <li><strong>Point-free style</strong> in pipelines: <code>map(multiply(2))</code> instead of <code>map(x =&gt; x * 2)</code>.</li>
  <li><strong>Composability</strong>: curried functions fit together without adapters.</li>
</ul>
<p>Lodash's <code>_.curry</code> handles placeholders (<code>_.curry(fn)(_, 2)(1)</code>). <code>fn.bind(null, arg)</code> gives you partial application without the multi-step chain.</p>
'''

ANSWERS[27] = r'''
<p>Recursive structural comparison, handling cycles and special types.</p>
<pre><code>function deepEqual(a, b, seen = new WeakMap()) {
  if (Object.is(a, b)) return true;

  if (typeof a !== "object" || typeof b !== "object" ||
      a === null || b === null) return false;

  if (a.constructor !== b.constructor) return false;

  // Special types
  if (a instanceof Date)   return a.getTime() === b.getTime();
  if (a instanceof RegExp) return a.source === b.source && a.flags === b.flags;
  if (a instanceof Map) {
    if (a.size !== b.size) return false;
    for (const [k, v] of a) if (!b.has(k) || !deepEqual(v, b.get(k), seen)) return false;
    return true;
  }
  if (a instanceof Set) {
    if (a.size !== b.size) return false;
    for (const v of a) if (!b.has(v)) return false;   // shallow for sets
    return true;
  }

  // Cycle detection
  if (seen.get(a) === b) return true;
  seen.set(a, b);

  const ka = Reflect.ownKeys(a);
  const kb = Reflect.ownKeys(b);
  if (ka.length !== kb.length) return false;
  for (const k of ka) {
    if (!Reflect.has(b, k) || !deepEqual(a[k], b[k], seen)) return false;
  }
  return true;
}</code></pre>
'''

ANSWERS[28] = r'''
<p>Both limit call frequency but behave differently.</p>
<pre><code>// Debounce — wait for activity to stop, then fire
const debounce = (fn, wait) =&gt; {
  let t;
  return (...args) =&gt; { clearTimeout(t); t = setTimeout(() =&gt; fn(...args), wait); };
};

// Throttle — fire at most once per interval
const throttle = (fn, wait) =&gt; {
  let last = 0;
  return (...args) =&gt; {
    const now = Date.now();
    if (now - last &gt;= wait) { last = now; fn(...args); }
  };
};</code></pre>
<table>
  <thead><tr><th>When to use</th><th>Debounce</th><th>Throttle</th></tr></thead>
  <tbody>
    <tr><td>Trigger only after user pauses</td><td>✓</td><td></td></tr>
    <tr><td>Uniform update rate</td><td></td><td>✓</td></tr>
    <tr><td>Search input, validation</td><td>✓</td><td></td></tr>
    <tr><td>Scroll, mousemove, resize</td><td></td><td>✓</td></tr>
    <tr><td>Rate-limited API calls</td><td></td><td>✓</td></tr>
  </tbody>
</table>
<p>Lodash adds leading/trailing edge options — <code>_.debounce(fn, 200, { leading: true })</code> fires once immediately and then waits.</p>
'''

ANSWERS[29] = r'''
<pre><code>class BSTNode {
  constructor(val) { this.val = val; this.left = null; this.right = null; }
}

class BST {
  constructor() { this.root = null; }

  insert(val) {
    const node = new BSTNode(val);
    if (!this.root) { this.root = node; return; }
    let cur = this.root;
    while (true) {
      if (val &lt; cur.val) {
        if (!cur.left) { cur.left = node; return; }
        cur = cur.left;
      } else {
        if (!cur.right) { cur.right = node; return; }
        cur = cur.right;
      }
    }
  }

  has(val) {
    let cur = this.root;
    while (cur) {
      if (val === cur.val) return true;
      cur = val &lt; cur.val ? cur.left : cur.right;
    }
    return false;
  }

  *inorder(node = this.root) {
    if (!node) return;
    yield* this.inorder(node.left);
    yield node.val;
    yield* this.inorder(node.right);
  }
}</code></pre>
<p>Average O(log n) operations; worst case O(n) if the tree degenerates into a list. Use a self-balancing variant (Red-Black, AVL) for guaranteed O(log n).</p>
'''

ANSWERS[30] = r'''
<p><strong>Reactive programming</strong> treats data as streams over time; changes propagate automatically to dependents.</p>
<pre><code>// RxJS example
import { fromEvent, debounceTime, map, switchMap } from "rxjs";

fromEvent(input, "input").pipe(
  map(e =&gt; e.target.value),
  debounceTime(300),
  switchMap(q =&gt; fetch(`/search?q=${q}`).then(r =&gt; r.json()))
).subscribe(renderResults);</code></pre>
<p>Key ideas:</p>
<ul>
  <li><strong>Observable</strong> — a lazy stream you subscribe to.</li>
  <li><strong>Operators</strong> — transform streams (map, filter, merge, debounce).</li>
  <li><strong>Backpressure-aware</strong> — streams can express &ldquo;slow down.&rdquo;</li>
</ul>
<p>Use cases: event-heavy UIs (search, drag/drop, autocompletion), real-time data, coordinating many async sources. Frameworks: RxJS, MobX, Signals (Preact/Solid/Angular). The tradeoff is a learning curve and sometimes-awkward debugging. Modern Signals offer most of the reactivity benefit with much less complexity.</p>
'''

ANSWERS[31] = r'''
<p>Circular deps happen when module A imports B and B imports A. Behavior depends on the module system.</p>
<ul>
  <li><strong>ES modules</strong> — partial values: whatever's been evaluated so far is visible. Function references resolve lazily, so method calls usually work; direct value access may see <code>undefined</code>.</li>
  <li><strong>CommonJS</strong> — returns the partially-populated <code>exports</code> object. Reading a name that hasn't been assigned yet yields <code>undefined</code>.</li>
</ul>
<p>Fixes:</p>
<ul>
  <li><strong>Extract</strong> the shared type/constant to a third module both depend on.</li>
  <li><strong>Dependency injection</strong> — accept the dependency as a parameter instead of importing it.</li>
  <li><strong>Late imports</strong> — <code>import()</code> inside a function defers evaluation until called.</li>
  <li><strong>Re-architect</strong> — a cycle usually hints at a misplaced responsibility.</li>
</ul>
<pre><code>// Bad — circular
// a.js: import { b } from "./b.js";
// b.js: import { a } from "./a.js";

// Better — shared module
// shared.js: export const config = {...};
// a.js: import { config } from "./shared.js";
// b.js: import { config } from "./shared.js";</code></pre>
'''

ANSWERS[32] = r'''
<p>Immutable data is never modified in place — changes produce new objects.</p>
<h4>Benefits</h4>
<ul>
  <li><strong>Predictable state</strong> — no spooky action at a distance; a reference's value is frozen.</li>
  <li><strong>Cheap change detection</strong> — reference equality tells you something changed (critical for React's <code>===</code> checks).</li>
  <li><strong>Time-travel debugging</strong> — each state is a snapshot.</li>
  <li><strong>Thread/async safety</strong> — no race conditions from shared mutation.</li>
  <li><strong>Easier testing</strong> — pure transforms are trivial to test.</li>
</ul>
<h4>Techniques</h4>
<pre><code>// Manual with spread
const next = { ...state, count: state.count + 1 };
const addedItem = [...items, newItem];

// Object.freeze for runtime enforcement
const cfg = Object.freeze({ debug: true });

// Immer — write &ldquo;mutating&rdquo; code, get an immutable update
import produce from "immer";
const next = produce(state, (draft) =&gt; { draft.count++; });

// Immutable.js / Records & Tuples (proposal)</code></pre>
<p>Tradeoff: garbage pressure from allocating new objects. Structural sharing (Immer, Immutable.js) minimizes copies.</p>
'''

ANSWERS[33] = r'''
<p>Binary heap backing an array — bubble up on insert, sift down on extract.</p>
<pre><code>class MinHeap {
  constructor(cmp = (a, b) =&gt; a - b) { this.arr = []; this.cmp = cmp; }
  get size() { return this.arr.length; }

  push(val) {
    this.arr.push(val);
    this.#bubbleUp(this.arr.length - 1);
  }

  pop() {
    if (!this.arr.length) return undefined;
    const top = this.arr[0];
    const last = this.arr.pop();
    if (this.arr.length) {
      this.arr[0] = last;
      this.#siftDown(0);
    }
    return top;
  }

  peek() { return this.arr[0]; }

  #bubbleUp(i) {
    while (i &gt; 0) {
      const p = (i - 1) &gt;&gt; 1;
      if (this.cmp(this.arr[i], this.arr[p]) &gt;= 0) break;
      [this.arr[i], this.arr[p]] = [this.arr[p], this.arr[i]];
      i = p;
    }
  }

  #siftDown(i) {
    const n = this.arr.length;
    while (true) {
      const l = 2*i + 1, r = 2*i + 2;
      let smallest = i;
      if (l &lt; n && this.cmp(this.arr[l], this.arr[smallest]) &lt; 0) smallest = l;
      if (r &lt; n && this.cmp(this.arr[r], this.arr[smallest]) &lt; 0) smallest = r;
      if (smallest === i) break;
      [this.arr[i], this.arr[smallest]] = [this.arr[smallest], this.arr[i]];
      i = smallest;
    }
  }
}</code></pre>
<p>O(log n) push/pop, O(1) peek. Use for Dijkstra, task schedulers, top-K selections.</p>
'''

ANSWERS[34] = r'''
<p><strong>Virtual DOM</strong> is a lightweight in-memory representation of the UI. On update, the framework diffs the new tree against the previous one and applies only the necessary real-DOM changes.</p>
<pre><code>// Conceptual flow in React
function App() { return &lt;div&gt;{count}&lt;/div&gt;; }

// 1. Render → new VDOM tree
// 2. Diff against previous VDOM tree
// 3. Compute minimal set of real-DOM mutations
// 4. Apply patches</code></pre>
<p>Why it helps:</p>
<ul>
  <li><strong>Batched updates</strong> — many state changes collapse into one DOM mutation cycle.</li>
  <li><strong>Declarative programming model</strong> — you describe &ldquo;what,&rdquo; framework handles &ldquo;how.&rdquo;</li>
  <li><strong>Cross-platform</strong> — same model drives React Native, Electron, etc.</li>
</ul>
<p>Tradeoffs: diffing has overhead; not free. Modern frameworks (Solid, Svelte) skip the VDOM, compiling directly to fine-grained reactive updates and often winning on raw performance.</p>
'''

ANSWERS[35] = r'''
<h4>Render pipeline</h4>
<ul>
  <li>Minimize layout thrashing — batch DOM reads (<code>getBoundingClientRect</code>) and writes.</li>
  <li>Use CSS <code>transform</code> and <code>opacity</code> for animation — they're composited, no repaint.</li>
  <li><code>will-change</code> sparingly to hint compositor promotion.</li>
  <li>Avoid forced synchronous layout (reading geometry after a write).</li>
</ul>
<h4>Component / state</h4>
<ul>
  <li>Memoize expensive computations (<code>useMemo</code>, <code>useCallback</code>).</li>
  <li>Virtualize long lists (react-window, tanstack-virtual).</li>
  <li>Split heavy routes behind dynamic <code>import()</code>.</li>
  <li>Stable keys in list items to avoid full re-mounts.</li>
</ul>
<h4>Assets & network</h4>
<ul>
  <li>Lazy-load images (<code>loading="lazy"</code>) and below-the-fold components.</li>
  <li>Serve modern image formats (AVIF, WebP) and <code>srcset</code>.</li>
  <li>HTTP caching, CDN, service worker for repeat visits.</li>
</ul>
<h4>Measurement</h4>
<p>Use Chrome DevTools Performance tab, Lighthouse, Core Web Vitals (LCP, CLS, INP). Measure before optimizing — render perf is rarely where you expect.</p>
'''

ANSWERS[36] = r'''
<table>
  <thead><tr><th></th><th><code>setTimeout</code></th><th><code>requestAnimationFrame</code></th></tr></thead>
  <tbody>
    <tr><td>Fires</td><td>After a delay (macrotask)</td><td>Before next repaint (~60fps)</td></tr>
    <tr><td>Throttled on hidden tab</td><td>No (throttled to ~1s)</td><td>Yes — pauses entirely</td></tr>
    <tr><td>Tied to display refresh</td><td>No</td><td>Yes</td></tr>
    <tr><td>Use for</td><td>Deferred work, timeouts</td><td>Animations, visual updates</td></tr>
  </tbody>
</table>
<pre><code>// Janky — setTimeout can fire in the middle of a frame
setTimeout(step, 16);

// Smooth — rAF syncs with the browser's repaint
function step(t) {
  update(t);
  draw();
  requestAnimationFrame(step);
}
requestAnimationFrame(step);</code></pre>
<p>rAF callbacks receive the current timestamp (<code>DOMHighResTimeStamp</code>) so you can animate by elapsed time rather than assuming a constant frame rate.</p>
'''

ANSWERS[37] = r'''
<p>A minimal <code>{{ placeholder }}</code> engine.</p>
<pre><code>function template(str, data) {
  return str.replace(/\{\{\s*(\w+(?:\.\w+)*)\s*\}\}/g, (_, path) =&gt; {
    return path.split(".").reduce((o, k) =&gt; o?.[k] ?? "", data);
  });
}

template("Hello, {{ user.name }}!", { user: { name: "Ana" } });
// "Hello, Ana!"</code></pre>
<p>For loops and conditionals, you need a real tokenizer. A compiled-function approach is fast:</p>
<pre><code>function compile(str) {
  const body = "return `" + str
    .replace(/`/g, "\\`")
    .replace(/\{\{(.+?)\}\}/g, (_, x) =&gt; "${" + x + "}") + "`;";
  return new Function("data", `with (data) { ${body} }`);
}

const render = compile("Hello, ${name}!");
render({ name: "Ana" });</code></pre>
<p><strong>Security:</strong> never compile untrusted templates — it's arbitrary code execution. For user content, always HTML-escape the interpolated values. Real engines (Handlebars, Nunjucks) handle this.</p>
'''

ANSWERS[38] = r'''
<p>An <strong>HOC</strong> is a function that takes a component and returns a new component with extended behavior.</p>
<pre><code>function withAuth(Wrapped) {
  return function AuthWrapped(props) {
    const user = useUser();
    if (!user) return &lt;Login /&gt;;
    return &lt;Wrapped {...props} user={user} /&gt;;
  };
}

const DashboardWithAuth = withAuth(Dashboard);</code></pre>
<p>Benefits:</p>
<ul>
  <li><strong>Reusable cross-cutting concerns</strong> — auth, logging, styling, data loading.</li>
  <li><strong>Separation of concerns</strong> — wrapped components stay focused.</li>
</ul>
<p>Downsides (and the reason hooks won):</p>
<ul>
  <li>&ldquo;Wrapper hell&rdquo; in React DevTools.</li>
  <li>Prop collision between HOCs.</li>
  <li>Static type limitations with generics.</li>
</ul>
<p>Modern React prefers <strong>custom hooks</strong> (<code>useAuth()</code>) for the same use cases — less indirection, easier to compose. HOCs are still fine when the component tree itself needs to change (adding wrappers, error boundaries).</p>
'''

ANSWERS[39] = r'''
<p>i18n = internationalization (code supports multiple languages); l10n = localization (actual translations).</p>
<pre><code>// Simple: load translations by locale
const translations = {
  en: { greeting: "Hello, {name}!" },
  es: { greeting: "¡Hola, {name}!" },
};
function t(key, data = {}, locale = "en") {
  return translations[locale][key].replace(/\{(\w+)\}/g, (_, k) =&gt; data[k]);
}
t("greeting", { name: "Ana" }, "es"); // "¡Hola, Ana!"

// Built-in: Intl API
new Intl.DateTimeFormat("de-DE").format(new Date());
new Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY" }).format(1200);
new Intl.PluralRules("en").select(1);     // "one"
new Intl.RelativeTimeFormat("en").format(-1, "day"); // "1 day ago"</code></pre>
<p>Libraries: react-intl, i18next, LinguiJS, FormatJS. Concerns: pluralization rules differ per language; RTL layout (<code>dir="rtl"</code>); date/number/currency formatting; collation order for sorting; lazy-loading translation bundles; fallback locales.</p>
'''

ANSWERS[40] = r'''
<h4>Code lazy-loading</h4>
<pre><code>// Dynamic import
const { heavy } = await import("./heavy.js");

// React
const Chart = React.lazy(() =&gt; import("./Chart"));

// Route-level splitting (Next.js, React Router)
// Each route becomes its own chunk.</code></pre>
<h4>Asset lazy-loading</h4>
<pre><code>&lt;img src="hero.jpg" loading="lazy" /&gt;
&lt;iframe src="map.html" loading="lazy"&gt;&lt;/iframe&gt;</code></pre>
<h4>On-demand rendering</h4>
<pre><code>// Render components only when they scroll into view
const obs = new IntersectionObserver((entries) =&gt; {
  for (const e of entries) {
    if (e.isIntersecting) loadIt(e.target);
  }
});
obs.observe(element);</code></pre>
<h4>Preloading</h4>
<p>Prefetch likely-next routes during idle time (<code>requestIdleCallback</code>, <code>&lt;link rel="prefetch"&gt;</code>) so navigation feels instant without increasing initial payload.</p>
<p>Balance: too much lazy loading creates waterfalls (chunk → chunk → chunk). Measure with your build tool's bundle analyzer.</p>
'''

ANSWERS[41] = r'''
<p>Token bucket or leaky bucket pattern. Token bucket lets bursts through; leaky bucket smooths to a constant rate.</p>
<pre><code>// Token bucket
class RateLimiter {
  constructor(capacity, refillPerSec) {
    this.capacity = capacity;
    this.tokens = capacity;
    this.rate = refillPerSec;
    this.last = Date.now();
  }

  take() {
    this.#refill();
    if (this.tokens &lt; 1) return false;
    this.tokens--;
    return true;
  }

  #refill() {
    const now = Date.now();
    const add = ((now - this.last) / 1000) * this.rate;
    this.tokens = Math.min(this.capacity, this.tokens + add);
    this.last = now;
  }
}

const lim = new RateLimiter(10, 2);  // burst 10, refill 2/s
if (!lim.take()) throw new Error("rate limited");</code></pre>
<p>For async queuing instead of rejection, wrap calls in a promise queue that awaits the next available token. For distributed limits, use Redis INCR with an expiry or a sorted set of timestamps.</p>
'''

ANSWERS[42] = r'''
<p><strong>SSR</strong> renders HTML on the server and ships it ready-to-display; the client then &ldquo;hydrates&rdquo; by attaching interactivity.</p>
<h4>Advantages</h4>
<ul>
  <li><strong>Faster first paint / LCP</strong> — users see content without waiting for the JS bundle.</li>
  <li><strong>SEO</strong> — crawlers see full content (less important now, but still matters for social previews).</li>
  <li><strong>Works with JS disabled / on slow devices</strong> — core content still rendered.</li>
</ul>
<h4>Tradeoffs</h4>
<ul>
  <li><strong>Server cost</strong> — each request does render work.</li>
  <li><strong>Hydration overhead</strong> — users see content but can't interact for a moment (TTI).</li>
  <li><strong>Data fetching must move server-side</strong> — more coordination.</li>
</ul>
<h4>Variants</h4>
<ul>
  <li><strong>SSG</strong> — render at build time. Cheapest, but stale until rebuild.</li>
  <li><strong>ISR</strong> — rebuild on demand / revalidate in the background.</li>
  <li><strong>Streaming SSR + React Server Components</strong> — stream HTML as it's ready; server-only components never ship JS.</li>
</ul>
<p>Frameworks: Next.js, Remix, Nuxt, SvelteKit.</p>
'''

ANSWERS[43] = r'''
<p>Three common approaches:</p>
<pre><code>// 1. Module-level (simplest — ES modules are singletons by nature)
// config.js
export const config = loadConfig();

// 2. Closure-based
const Singleton = (() =&gt; {
  let instance = null;
  return {
    getInstance() {
      if (!instance) instance = { data: [], createdAt: Date.now() };
      return instance;
    }
  };
})();

// 3. Class with static field
class Db {
  static #instance = null;
  static get instance() {
    return Db.#instance ??= new Db();
  }
  #constructor() { this.pool = createPool(); }
}</code></pre>
<p><strong>Warning:</strong> singletons are often an anti-pattern. They make testing hard (global state), hide dependencies, and don't scale across worker threads or server instances. Prefer dependency injection where possible; use singletons for truly global resources (loggers, DB pools, config).</p>
'''

ANSWERS[44] = r'''
<table>
  <thead><tr><th></th><th>Client-side</th><th>Server-side</th></tr></thead>
  <tbody>
    <tr><td>Examples</td><td>localStorage, IndexedDB, cookies</td><td>SQL, NoSQL, Redis, S3</td></tr>
    <tr><td>Capacity</td><td>~5-10 MB (Local/Session), 50 MB+ (IDB)</td><td>Effectively unlimited</td></tr>
    <tr><td>Persistence</td><td>Per-browser; can be cleared anytime</td><td>Durable, backed up</td></tr>
    <tr><td>Security</td><td>Accessible via JS (XSS risk)</td><td>Access controlled, auditable</td></tr>
    <tr><td>Latency</td><td>Instant</td><td>Network round-trip</td></tr>
    <tr><td>Sharing across devices</td><td>No</td><td>Yes</td></tr>
    <tr><td>Offline</td><td>Yes</td><td>No (without sync)</td></tr>
  </tbody>
</table>
<p><strong>Rules of thumb:</strong></p>
<ul>
  <li>Never store secrets/tokens in <code>localStorage</code> — use <code>HttpOnly</code> cookies.</li>
  <li>Use <code>IndexedDB</code> for structured, larger client data (offline-first PWAs).</li>
  <li>Session/local storage for UI preferences, cached lookups.</li>
  <li>Source of truth → server. Client copies are caches.</li>
</ul>
'''

ANSWERS[45] = r'''
<p>A <strong>polyfill</strong> adds a feature to older environments by implementing it in standard JS.</p>
<pre><code>// Polyfill Array.prototype.at (which fails on negative indexes)
if (!Array.prototype.at) {
  Object.defineProperty(Array.prototype, "at", {
    value: function (i) {
      i = Math.trunc(i) || 0;
      if (i &lt; 0) i += this.length;
      return i &lt; 0 || i &gt;= this.length ? undefined : this[i];
    },
    writable: true, configurable: true
  });
}

// Object.groupBy (recent)
Object.groupBy ??= function (items, keyFn) {
  return items.reduce((acc, item) =&gt; {
    const k = keyFn(item);
    (acc[k] ??= []).push(item);
    return acc;
  }, Object.create(null));
};</code></pre>
<p>Principles:</p>
<ul>
  <li><strong>Feature-detect</strong>, don't browser-detect.</li>
  <li>Use <code>Object.defineProperty</code> with non-enumerable — avoid polluting <code>for...in</code>.</li>
  <li>Match the spec exactly (edge cases, error types).</li>
  <li>Prefer built-in polyfill libraries (<code>core-js</code>) over hand-written ones — they're battle-tested.</li>
</ul>
'''

ANSWERS[46] = r'''
<p>JSON has overhead: it's text, and it can't encode binary or complex types. Binary formats are smaller and faster.</p>
<pre><code>// MessagePack (JS: msgpack-lite, @msgpack/msgpack)
import { encode, decode } from "@msgpack/msgpack";
const buf = encode({ x: 1, data: new Uint8Array([1, 2, 3]) });
const obj = decode(buf);

// Protobuf (schema-driven, used in gRPC)
// Define in .proto, compile to JS.

// BSON (MongoDB format)
// Built-in browser option — DataView for hand-rolled formats
const buf = new ArrayBuffer(8);
const view = new DataView(buf);
view.setUint32(0, 1234);
view.setFloat32(4, 3.14);</code></pre>
<p>When to use:</p>
<ul>
  <li><strong>MessagePack</strong> — drop-in JSON replacement, ~30% smaller.</li>
  <li><strong>Protobuf</strong> — typed contracts across services; smallest and fastest.</li>
  <li><strong>Avro / Cap'n Proto</strong> — schema evolution, zero-copy reads.</li>
</ul>
<p>Tradeoff: not human-readable, needs tooling. Stick with JSON unless profiling shows serialization is a bottleneck.</p>
'''

ANSWERS[47] = r'''
<pre><code>class Router {
  constructor() {
    this.routes = new Map();
    window.addEventListener("popstate", () =&gt; this.#render());
    document.addEventListener("click", (e) =&gt; {
      const a = e.target.closest("a[data-link]");
      if (a) { e.preventDefault(); this.navigate(a.href); }
    });
  }

  add(path, component) {
    this.routes.set(path, component);
    return this;
  }

  navigate(url) {
    history.pushState(null, "", url);
    this.#render();
  }

  #render() {
    const path = location.pathname;
    const comp = this.routes.get(path) ?? this.routes.get("*");
    comp?.(document.querySelector("#app"));
  }

  start() { this.#render(); }
}

new Router()
  .add("/", Home)
  .add("/about", About)
  .add("*", NotFound)
  .start();</code></pre>
<p>Extensions for real use: dynamic params (<code>/users/:id</code>), nested routes, route guards, lazy route loading with <code>import()</code>, hash-mode fallback. Libraries: React Router, Vue Router, Wouter (minimal).</p>
'''

ANSWERS[48] = r'''
<table>
  <thead><tr><th></th><th>WebSockets</th><th>Server-Sent Events (SSE)</th></tr></thead>
  <tbody>
    <tr><td>Direction</td><td>Full duplex</td><td>Server → client only</td></tr>
    <tr><td>Protocol</td><td><code>ws://</code> / <code>wss://</code> (custom)</td><td>HTTP (long-lived response)</td></tr>
    <tr><td>Auto-reconnect</td><td>Manual</td><td>Built-in (<code>EventSource</code>)</td></tr>
    <tr><td>Binary data</td><td>Yes</td><td>Text only</td></tr>
    <tr><td>Message types</td><td>Open — you define</td><td>Named events</td></tr>
    <tr><td>Proxy friendliness</td><td>Sometimes awkward</td><td>Plain HTTP — works through most proxies</td></tr>
    <tr><td>Use case</td><td>Chat, collab, games</td><td>Live feeds, notifications, log tails</td></tr>
  </tbody>
</table>
<pre><code>// SSE client
const es = new EventSource("/events");
es.addEventListener("update", (e) =&gt; console.log(JSON.parse(e.data)));

// WebSocket client
const ws = new WebSocket("wss://example.com/chat");
ws.onmessage = (e) =&gt; handle(e.data);
ws.send(JSON.stringify({ type: "msg", text: "hi" }));</code></pre>
<p>Rule of thumb: SSE for one-way streams (simpler, built-in reconnect). WebSockets when you need bidirectional or binary. Consider long-polling or HTTP/2 streams (gRPC-Web) for specific needs.</p>
'''

ANSWERS[49] = r'''
<p>JavaScript is single-threaded, so &ldquo;concurrency&rdquo; means interleaved async work, not true parallelism.</p>
<h4>Patterns</h4>
<ul>
  <li><strong>Promise.all / allSettled</strong> — launch parallel async ops, await them together.</li>
  <li><strong>Promise pools</strong> — limit concurrent in-flight operations (e.g., 10 at a time).</li>
  <li><strong>Queues</strong> — serialize access to a resource.</li>
  <li><strong>AbortController</strong> — cancel outstanding ops when superseded.</li>
  <li><strong>Web Workers / Worker Threads</strong> — true parallelism for CPU-bound work.</li>
</ul>
<pre><code>// Pool pattern — max 5 concurrent
async function pool(items, fn, limit) {
  const results = [];
  const executing = new Set();
  for (const item of items) {
    const p = Promise.resolve().then(() =&gt; fn(item));
    results.push(p);
    executing.add(p);
    p.finally(() =&gt; executing.delete(p));
    if (executing.size &gt;= limit) await Promise.race(executing);
  }
  return Promise.all(results);
}</code></pre>
<p>Shared state across workers needs <code>SharedArrayBuffer</code> + <code>Atomics</code>. Most JS apps can avoid this complexity — message passing suffices.</p>
'''

ANSWERS[50] = r'''
<p><strong>DI</strong> means a class receives its dependencies from outside rather than constructing them internally.</p>
<pre><code>// Without DI — tightly coupled
class OrderService {
  constructor() {
    this.db = new MySQLDb();         // hard-coded
    this.emailer = new SendGrid();   // hard-coded
  }
}

// With DI
class OrderService {
  constructor(db, emailer) {
    this.db = db;
    this.emailer = emailer;
  }
}
new OrderService(new MySQLDb(), new SendGrid());
// Tests: new OrderService(new FakeDb(), new FakeEmailer());</code></pre>
<p>Benefits:</p>
<ul>
  <li><strong>Testable</strong> — swap real services for fakes/mocks.</li>
  <li><strong>Flexible</strong> — change implementations without touching callers.</li>
  <li><strong>Explicit dependencies</strong> — clear what a class needs.</li>
  <li><strong>Inversion of control</strong> — higher-level code composes the graph.</li>
</ul>
<p>In JS this is usually done manually or with factories. DI containers (InversifyJS, Awilix, NestJS built-in) help with large trees, but often feel over-engineered for small apps. Function parameters are JavaScript's natural DI mechanism.</p>
'''

ANSWERS[51] = r'''
<pre><code>class EventEmitter {
  constructor() { this.events = new Map(); }

  on(event, listener) {
    if (!this.events.has(event)) this.events.set(event, new Set());
    this.events.get(event).add(listener);
    return () =&gt; this.off(event, listener);
  }

  once(event, listener) {
    const wrapper = (...args) =&gt; {
      this.off(event, wrapper);
      listener(...args);
    };
    return this.on(event, wrapper);
  }

  off(event, listener) {
    this.events.get(event)?.delete(listener);
  }

  emit(event, ...args) {
    const listeners = this.events.get(event);
    if (!listeners) return false;
    for (const l of [...listeners]) {    // clone — listener may unsubscribe
      try { l(...args); }
      catch (e) { console.error("listener error:", e); }
    }
    return true;
  }
}</code></pre>
<p>Node's built-in <code>EventEmitter</code> follows this pattern with extras: max-listener warnings, <code>prependListener</code>, error-event conventions. Clone the listener set before iterating so that a listener that unsubscribes itself doesn't corrupt the iteration.</p>
'''

ANSWERS[52] = r'''
<p><strong>WebAssembly</strong> is a binary instruction format that runs at near-native speed in the browser, callable from JavaScript.</p>
<h4>Benefits</h4>
<ul>
  <li><strong>Performance</strong> — 2-10× faster than JS for CPU-bound work (image processing, crypto, physics, ML).</li>
  <li><strong>Language choice</strong> — compile Rust, C/C++, Go, AssemblyScript to the browser.</li>
  <li><strong>Reuse</strong> — port existing native libraries (ffmpeg, SQLite, TensorFlow) to the browser.</li>
  <li><strong>Determinism</strong> — avoids JS engine warmup and deopt variability.</li>
</ul>
<h4>Drawbacks</h4>
<ul>
  <li><strong>No direct DOM access</strong> — must call through JS. Chatty interop kills the speedup.</li>
  <li><strong>Larger bundles</strong> — binaries can be bigger than equivalent JS.</li>
  <li><strong>Debugging is harder</strong> — source maps help, but tooling lags.</li>
  <li><strong>Not faster for everything</strong> — string/DOM/network-heavy code often won't win.</li>
</ul>
<p>Use WASM when you've measured a hot path that JS can't match. Don't port an entire app to WASM for hypothetical gains.</p>
'''

ANSWERS[53] = r'''
<p><code>Map</code> preserves insertion order. Move-to-end on access gives LRU semantics for free.</p>
<pre><code>class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.cache = new Map();
  }

  get(key) {
    if (!this.cache.has(key)) return -1;
    const v = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, v);          // re-insert → most recent
    return v;
  }

  put(key, value) {
    if (this.cache.has(key)) this.cache.delete(key);
    else if (this.cache.size &gt;= this.capacity) {
      this.cache.delete(this.cache.keys().next().value);   // evict oldest
    }
    this.cache.set(key, value);
  }
}

const lru = new LRUCache(3);
lru.put("a", 1); lru.put("b", 2); lru.put("c", 3);
lru.get("a");                    // 1, moves 'a' to most recent
lru.put("d", 4);                 // evicts 'b' (least recent)</code></pre>
<p>All operations are O(1) — <code>Map</code> insertion/deletion and order-preserving iteration are constant time. Classic interview question.</p>
'''

ANSWERS[54] = r'''
<p><strong>Module Federation</strong> (Webpack 5) lets independently built/deployed apps share code at runtime. Team A ships a module; Team B's app loads it on demand over HTTP.</p>
<pre><code>// Team A: host.config.js
new ModuleFederationPlugin({
  name: "shell",
  remotes: { checkout: "checkout@https://cdn.example.com/checkout.js" }
});

// Team A source:
const Checkout = await import("checkout/Widget");
</code></pre>
<p>Key ideas:</p>
<ul>
  <li><strong>Independent deploys</strong> — teams ship at their own cadence.</li>
  <li><strong>Shared dependencies</strong> — React, design system loaded once across remotes.</li>
  <li><strong>Version resolution</strong> — runtime picks compatible shared versions.</li>
</ul>
<p>Use cases: micro-frontends, large orgs with many teams, plugin systems. Costs: setup complexity, versioning contracts, performance (runtime resolution, network hops), typing across boundaries. Most startups don't need it — a good monorepo solves the same problem simpler.</p>
'''

ANSWERS[55] = r'''
<p>Key levers: chunking, parallelism, direct-to-storage, and resumability.</p>
<pre><code>// 1. Chunk + upload with concurrency limit
async function uploadLarge(file) {
  const CHUNK = 5 * 1024 * 1024;
  const total = Math.ceil(file.size / CHUNK);
  const uploadId = (await fetch("/uploads", { method: "POST" }).then(r =&gt; r.json())).id;

  const queue = Array.from({ length: total }, (_, i) =&gt; i);
  const workers = Array(4).fill().map(async () =&gt; {
    while (queue.length) {
      const i = queue.shift();
      const chunk = file.slice(i * CHUNK, (i + 1) * CHUNK);
      await fetch(`/uploads/${uploadId}/${i}`, { method: "PUT", body: chunk });
    }
  });
  await Promise.all(workers);
  await fetch(`/uploads/${uploadId}/complete`, { method: "POST" });
}</code></pre>
<h4>Scale checklist</h4>
<ul>
  <li><strong>Direct-to-S3 with presigned URLs</strong> — don't proxy file bytes through your server.</li>
  <li><strong>Resumable protocols</strong> — tus.io, S3 multipart upload.</li>
  <li><strong>Client-side checksums</strong> — catch corruption early.</li>
  <li><strong>Progress/backpressure</strong> — track per-chunk progress; throttle on failures.</li>
  <li><strong>Background / Service Worker uploads</strong> for resilience to page refreshes.</li>
</ul>
'''

ANSWERS[56] = r'''
<table>
  <thead><tr><th></th><th>REST</th><th>GraphQL</th></tr></thead>
  <tbody>
    <tr><td>Endpoints</td><td>Many — one per resource</td><td>One — <code>/graphql</code></td></tr>
    <tr><td>Client chooses fields</td><td>No — fixed shape</td><td>Yes — exactly what's asked</td></tr>
    <tr><td>Over/under-fetching</td><td>Common</td><td>Solved by design</td></tr>
    <tr><td>Multiple resources in one call</td><td>N+1 calls</td><td>One request</td></tr>
    <tr><td>Caching (HTTP)</td><td>Natural — URL as key</td><td>Needs custom (often Apollo Client)</td></tr>
    <tr><td>Schema / typing</td><td>OpenAPI (external)</td><td>Built in, introspectable</td></tr>
    <tr><td>Complexity</td><td>Low</td><td>Higher — schema, resolvers, N+1 risks</td></tr>
  </tbody>
</table>
<p><strong>REST</strong> when: simple CRUD, cacheable, public APIs, you control the client-server shape.</p>
<p><strong>GraphQL</strong> when: mobile clients with diverse needs, UI composes many resources, federation across teams, rapidly evolving UI.</p>
<p><strong>Don't pick &ldquo;the trendy one.&rdquo;</strong> Many teams run REST fine at massive scale; GraphQL has real operational overhead.</p>
'''

ANSWERS[57] = r'''
<h4>Client</h4>
<pre><code>const ws = new WebSocket("wss://example.com/chat");
ws.addEventListener("message", (e) =&gt; {
  const msg = JSON.parse(e.data);
  renderMessage(msg);
});
sendBtn.onclick = () =&gt; ws.send(JSON.stringify({ text: input.value }));</code></pre>
<h4>Server (Node + ws)</h4>
<pre><code>import { WebSocketServer } from "ws";
const wss = new WebSocketServer({ port: 8080 });
const rooms = new Map();          // roomId → Set&lt;ws&gt;

wss.on("connection", (ws, req) =&gt; {
  const room = new URL(req.url, "http://x").searchParams.get("room");
  if (!rooms.has(room)) rooms.set(room, new Set());
  rooms.get(room).add(ws);

  ws.on("message", (buf) =&gt; {
    const msg = JSON.parse(buf);
    for (const peer of rooms.get(room)) {
      if (peer.readyState === peer.OPEN) peer.send(JSON.stringify(msg));
    }
  });

  ws.on("close", () =&gt; rooms.get(room).delete(ws));
});</code></pre>
<p>Production concerns: auth on connect, persist history to DB, rate limit, auto-reconnect, presence/typing indicators, scale with Redis pub/sub or a dedicated service (Pusher, Ably, Socket.IO with Redis adapter).</p>
'''

ANSWERS[58] = r'''
<p>A <strong>service worker</strong> is a background script that intercepts network requests for its scope — an offline-first proxy and cache.</p>
<pre><code>// register
navigator.serviceWorker.register("/sw.js");

// sw.js
self.addEventListener("install", (e) =&gt; {
  e.waitUntil(caches.open("v1").then(c =&gt; c.addAll(["/", "/app.js"])));
});

self.addEventListener("fetch", (e) =&gt; {
  e.respondWith(
    caches.match(e.request).then(r =&gt; r || fetch(e.request))
  );
});</code></pre>
<p>Use cases:</p>
<ul>
  <li><strong>Offline support</strong> and PWAs (installable web apps).</li>
  <li><strong>Caching strategies</strong>: cache-first, network-first, stale-while-revalidate.</li>
  <li><strong>Background sync</strong> — retry failed requests when connectivity returns.</li>
  <li><strong>Push notifications</strong> (in conjunction with the Push API).</li>
  <li><strong>Precaching</strong> critical assets for instant second visits.</li>
</ul>
<p>Rules: HTTPS only (except localhost), scoped to path, lifecycle has <code>install</code>/<code>activate</code>/<code>fetch</code>, update by changing the file hash. Libraries: Workbox generates robust caching SWs.</p>
'''

ANSWERS[59] = r'''
<h4>Prefer CSS over JS</h4>
<ul>
  <li>Animate <code>transform</code> and <code>opacity</code> — they're composited on the GPU; no layout/paint.</li>
  <li>Avoid animating <code>width</code>, <code>height</code>, <code>top</code>, <code>left</code>, <code>background-color</code> — they trigger layout or paint.</li>
  <li><code>will-change: transform</code> sparingly — hints compositor promotion.</li>
</ul>
<h4>JS animations</h4>
<ul>
  <li>Use <code>requestAnimationFrame</code>, not <code>setTimeout</code>.</li>
  <li>Drive by elapsed time (<code>const t = (now - start) / duration</code>), not frame count.</li>
  <li>Batch DOM reads vs writes — read all layout-forcing props first, write after.</li>
  <li>Web Animations API for declarative animations with runtime control.</li>
</ul>
<h4>Diagnose jank</h4>
<ul>
  <li>DevTools Performance — look for long tasks, purple layout/paint bars, GC pauses.</li>
  <li>Rendering panel: Paint flashing, Layer borders, FPS meter.</li>
</ul>
<pre><code>// Good — transform (GPU), measured by time
const start = performance.now();
function step(now) {
  const t = Math.min(1, (now - start) / 1000);
  el.style.transform = `translateX(${t * 300}px)`;
  if (t &lt; 1) requestAnimationFrame(step);
}
requestAnimationFrame(step);</code></pre>
'''

ANSWERS[60] = r'''
<ul>
  <li><strong>Static types catch bugs early</strong> — typos, wrong signatures, null/undefined confusion surface at compile time.</li>
  <li><strong>Better refactoring</strong> — rename symbols across a codebase with confidence.</li>
  <li><strong>Self-documenting APIs</strong> — types are always in sync with code; IDEs show exact signatures.</li>
  <li><strong>Autocompletion / IntelliSense</strong> — massively faster exploration of unfamiliar code and libraries.</li>
  <li><strong>Safer enums, generics, discriminated unions</strong> — model state machines and API responses precisely.</li>
  <li><strong>Gradual adoption</strong> — <code>allowJs</code>, JSDoc types let you migrate file by file.</li>
</ul>
<pre><code>type User = { id: string; email: string; role: "admin" | "user" };

function canEdit(user: User, post: { authorId: string }): boolean {
  return user.role === "admin" || user.id === post.authorId;
}</code></pre>
<p>Costs: build step, type definitions for untyped libs, learning curve, &ldquo;fighting the types&rdquo; on edge cases. Most teams find the tradeoff pays off beyond ~3 engineers or ~5k lines of code. Runtime validation (Zod, Valibot) complements TypeScript for external data.</p>
'''

ANSWERS[61] = r'''
<h4>Virtualize the view</h4>
<p>Render only the subset visible on screen. Libraries: react-window, @tanstack/virtual.</p>
<h4>Stream instead of load-all</h4>
<pre><code>// Streaming JSON with fetch + NDJSON parser
const res = await fetch("/big");
const reader = res.body.getReader();
const decoder = new TextDecoder();
let buf = "";
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  const lines = buf.split("\n");
  buf = lines.pop();
  for (const line of lines) processRow(JSON.parse(line));
}</code></pre>
<h4>Process in chunks / off-main-thread</h4>
<ul>
  <li>Split work into 10-50ms slices; yield to the browser between slices.</li>
  <li>Move parsing, sorting, filtering to a Web Worker.</li>
  <li>Use <code>IndexedDB</code> as a local database instead of keeping everything in memory.</li>
</ul>
<h4>Reduce the data</h4>
<ul>
  <li>Paginate or infinite-scroll from the server.</li>
  <li>Projection — fetch only the fields you render.</li>
  <li>Pre-aggregate on the server rather than transferring raw rows.</li>
</ul>
'''

ANSWERS[62] = r'''
<p>A <strong>closure</strong> is a function bundled with the lexical environment where it was defined — it retains access to those outer variables after the outer function returns.</p>
<pre><code>function makeCounter() {
  let n = 0;
  return () =&gt; ++n;
}
const c = makeCounter();
c(); c(); c();   // 1, 2, 3 — `n` lives on in the closure</code></pre>
<p>Common uses:</p>
<ul>
  <li><strong>Data privacy</strong> — the outer variable is only touchable through returned functions.</li>
  <li><strong>Factories</strong> — <code>makeMultiplier(2)</code> returns a function that remembers <code>2</code>.</li>
  <li><strong>Callbacks</strong> capture the state they need: event handlers, <code>setTimeout</code> callbacks.</li>
  <li><strong>Memoization, debouncing, throttling</strong> — all rely on closures holding cache/timer state.</li>
  <li><strong>Partial application</strong> — <code>bind</code>/curry-style specialization.</li>
</ul>
<p>Memory gotcha: closures keep the entire scope alive, so large captured objects can prevent GC. Scope only what you need, and null out references if lifespan is long.</p>
'''

ANSWERS[63] = r'''
<p>A custom hook is a function starting with <code>use</code> that composes React's built-in hooks. It extracts reusable stateful logic.</p>
<pre><code>function useLocalStorage(key, initial) {
  const [value, setValue] = useState(() =&gt; {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : initial;
  });

  useEffect(() =&gt; {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// Use
function Settings() {
  const [theme, setTheme] = useLocalStorage("theme", "light");
  return &lt;button onClick={() =&gt; setTheme(t =&gt; t === "light" ? "dark" : "light")}&gt;{theme}&lt;/button&gt;;
}</code></pre>
<p>Rules:</p>
<ul>
  <li>Name must start with <code>use</code> (linting + React dev warnings depend on this).</li>
  <li>Call other hooks only at the top level — not inside conditions, loops, or nested functions.</li>
  <li>Hooks encapsulate behavior, not layout — a good hook returns data + actions, not JSX.</li>
</ul>
<p>Custom hooks replaced render props and HOCs as the idiomatic way to share logic in React.</p>
'''

ANSWERS[64] = r'''
<table>
  <thead><tr><th></th><th>Imperative</th><th>Declarative</th></tr></thead>
  <tbody>
    <tr><td>Expresses</td><td><em>How</em> to do something</td><td><em>What</em> you want</td></tr>
    <tr><td>Control flow</td><td>Explicit loops, mutation</td><td>Built-ins, expressions</td></tr>
    <tr><td>Example</td><td>Manual for-loop to double</td><td><code>arr.map(x =&gt; x * 2)</code></td></tr>
  </tbody>
</table>
<pre><code>// Imperative
const doubled = [];
for (let i = 0; i &lt; nums.length; i++) doubled.push(nums[i] * 2);

// Declarative
const doubled = nums.map(x =&gt; x * 2);

// UI: imperative (old jQuery)
$("#btn").on("click", () =&gt; $("#msg").text("saved"));

// UI: declarative (React)
&lt;div&gt;{saved ? "saved" : null}&lt;/div&gt;</code></pre>
<p>Declarative code is usually shorter and more composable but can hide performance (<code>filter().map().reduce()</code> walks the array three times). Imperative code gives more control at the cost of bookkeeping.</p>
'''

ANSWERS[65] = r'''
<p>A <strong>middleware</strong> is a function that receives a request + a <code>next</code> callback; it does something, then calls <code>next</code> to pass control on.</p>
<pre><code>function compose(middlewares) {
  return function (ctx) {
    let i = -1;
    const dispatch = (idx) =&gt; {
      if (idx &lt;= i) throw new Error("next() called twice");
      i = idx;
      const mw = middlewares[idx];
      if (!mw) return Promise.resolve();
      return Promise.resolve(mw(ctx, () =&gt; dispatch(idx + 1)));
    };
    return dispatch(0);
  };
}

// Usage (Express/Koa-style)
const app = compose([
  async (ctx, next) =&gt; { console.time("req"); await next(); console.timeEnd("req"); },
  async (ctx, next) =&gt; { if (!ctx.user) throw new Error("unauth"); await next(); },
  async (ctx) =&gt; { ctx.body = await loadData(ctx.params.id); },
]);

app({ params: { id: 1 }, user: { id: 42 } });</code></pre>
<p>This &ldquo;onion&rdquo; model lets each middleware wrap the rest — it can run code before and after, short-circuit (by not calling <code>next</code>), or catch errors from downstream. Seen in Express, Koa, Redux, and most server frameworks.</p>
'''

ANSWERS[66] = r'''
<p>A <strong>monorepo</strong> keeps multiple projects in one repository, with shared build tooling.</p>
<h4>Advantages</h4>
<ul>
  <li><strong>Atomic cross-project changes</strong> — update a library and its consumers in one commit.</li>
  <li><strong>Consistent tooling</strong> — one ESLint, one Prettier, one CI.</li>
  <li><strong>Easy refactoring</strong> — rename across everything at once.</li>
  <li><strong>Less overhead</strong> — no package publishing for internal shared code.</li>
  <li><strong>Shared dependencies</strong> — de-dupe <code>node_modules</code> with workspaces.</li>
</ul>
<h4>Drawbacks</h4>
<ul>
  <li>CI becomes slower (needs smart skip-unchanged logic).</li>
  <li>Repository size grows — checkout times, IDE indexing.</li>
  <li>Access control is coarser.</li>
  <li>Git history becomes mixed.</li>
</ul>
<h4>Tools</h4>
<p>pnpm workspaces (fast, strict hoisting), Nx, Turborepo, Lerna (legacy), Bazel (huge-scale). Yarn workspaces and npm workspaces are built in too.</p>
<p>Google, Meta, and Microsoft run massive monorepos. Smaller teams do fine with polyrepo too — pick based on coordination cost.</p>
'''

ANSWERS[67] = r'''
<h4>Authentication (who are you?)</h4>
<ul>
  <li><strong>Session cookies</strong> — server-issued opaque ID, stored in <code>HttpOnly; Secure; SameSite=Lax</code> cookie. Simple, battle-tested.</li>
  <li><strong>JWT</strong> — signed token, stateless. Easier to scale but harder to revoke; keep short-lived and refresh with a longer-lived refresh token.</li>
  <li><strong>OAuth 2.0 / OIDC</strong> — delegate to Google, GitHub, Auth0.</li>
</ul>
<h4>Authorization (what can you do?)</h4>
<ul>
  <li><strong>RBAC</strong> — roles carry permissions. Simple, scales to moderate complexity.</li>
  <li><strong>ABAC</strong> — policies over attributes. More flexible, more complex.</li>
  <li><strong>Check on the server for every action</strong> — never trust the client.</li>
</ul>
<h4>Client-side rules</h4>
<ul>
  <li>Prefer <code>HttpOnly</code> cookies over <code>localStorage</code> for tokens (XSS-resistant).</li>
  <li>CSRF protection: <code>SameSite=Lax</code> cookies + double-submit token for state-changing requests.</li>
  <li>Hide UI for actions the user can't perform, but always enforce on the server.</li>
</ul>
<p>Don't roll your own crypto. Use libraries: NextAuth, Lucia, Auth0, Clerk, Supabase Auth.</p>
'''

ANSWERS[68] = r'''
<h4>Don't trust client input</h4>
<ul>
  <li>Validate and sanitize on the server — always.</li>
  <li>Client-side validation is UX, not security.</li>
</ul>
<h4>XSS</h4>
<ul>
  <li>Frameworks escape by default — never use <code>innerHTML</code> / <code>dangerouslySetInnerHTML</code> with untrusted data.</li>
  <li>Content Security Policy (<code>Content-Security-Policy</code> header) to whitelist script sources.</li>
  <li>Sanitize rich text with DOMPurify if you must accept HTML.</li>
</ul>
<h4>CSRF</h4>
<ul>
  <li><code>SameSite=Lax</code> cookies + CSRF tokens on state-changing requests.</li>
</ul>
<h4>Auth & secrets</h4>
<ul>
  <li>Never commit API keys or secrets — use env vars, secret managers.</li>
  <li>Store tokens in <code>HttpOnly</code> cookies, not <code>localStorage</code>.</li>
  <li>Rate-limit sensitive endpoints; use argon2/bcrypt for passwords.</li>
</ul>
<h4>Dependencies</h4>
<ul>
  <li><code>npm audit</code>, Dependabot, Snyk — keep deps patched.</li>
  <li>Lockfiles in git; verify integrity hashes.</li>
</ul>
<h4>Transport & headers</h4>
<ul>
  <li>HTTPS only; HSTS.</li>
  <li>Set security headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.</li>
</ul>
'''

ANSWERS[69] = r'''
<p>Native HTML5 drag-and-drop API.</p>
<pre><code>// Source
draggableEl.draggable = true;
draggableEl.addEventListener("dragstart", (e) =&gt; {
  e.dataTransfer.setData("text/plain", draggableEl.id);
  e.dataTransfer.effectAllowed = "move";
});

// Target
dropZoneEl.addEventListener("dragover", (e) =&gt; {
  e.preventDefault();                     // REQUIRED to enable drop
  e.dataTransfer.dropEffect = "move";
});

dropZoneEl.addEventListener("drop", (e) =&gt; {
  e.preventDefault();
  const id = e.dataTransfer.getData("text/plain");
  const el = document.getElementById(id);
  dropZoneEl.appendChild(el);
});</code></pre>
<p><strong>Gotchas:</strong> you MUST call <code>preventDefault</code> in <code>dragover</code> or the drop won't fire. Custom drag preview via <code>e.dataTransfer.setDragImage()</code>. Styling is tricky — many teams use pointer events + transform for smoother results (react-dnd, @dnd-kit, SortableJS do this).</p>
<p>For touch support, native HTML5 DnD historically didn't work — mobile-first libraries (dnd-kit, Framer Motion) use pointer events.</p>
'''

ANSWERS[70] = r'''
<p>A <code>Proxy</code> intercepts fundamental operations (property access, assignment, function calls) on a target object.</p>
<pre><code>const logged = new Proxy({}, {
  get(target, key)   { console.log("read", key);       return target[key]; },
  set(target, key, v){ console.log("write", key, v);    target[key] = v; return true; },
  has(target, key)   { console.log("has", key);         return key in target; },
  deleteProperty(target, key) { console.log("del", key); return delete target[key]; }
});
logged.name = "Ana"; logged.name; "name" in logged; delete logged.name;</code></pre>
<p>Use cases:</p>
<ul>
  <li><strong>Reactive state</strong> — Vue 3's reactivity and MobX both use Proxies to auto-track reads and notify on writes.</li>
  <li><strong>Lazy / remote objects</strong> — <code>new Proxy({}, { get: (_, prop) =&gt; fetchField(prop) })</code>.</li>
  <li><strong>Validation / default values</strong> — intercept writes to enforce invariants.</li>
  <li><strong>Observation / logging</strong> — transparent instrumentation.</li>
  <li><strong>API clients</strong> — turn <code>api.users.list()</code> into <code>fetch("/users")</code> dynamically.</li>
</ul>
<p>Costs: slower than plain property access; harder debugging; not all operations are trappable.</p>
'''

ANSWERS[71] = r'''
<h4>Detect before you work around</h4>
<ul>
  <li>Feature-detect: <code>if ("IntersectionObserver" in window)</code> — don't UA-sniff.</li>
  <li><code>caniuse.com</code> for coverage; your analytics for your actual audience.</li>
</ul>
<h4>Standardize output</h4>
<ul>
  <li>Babel + targets (<code>browserslist</code>) transpiles syntax.</li>
  <li>core-js polyfills runtime APIs (<code>Array.prototype.at</code>, <code>Object.hasOwn</code>).</li>
  <li>Autoprefixer handles CSS vendor prefixes.</li>
  <li>Differential serving: modern bundle for evergreen browsers, legacy bundle as fallback.</li>
</ul>
<h4>Graceful degradation</h4>
<pre><code>if ("showOpenFilePicker" in window) useModernPicker();
else fallbackToInput();</code></pre>
<h4>Test across real browsers</h4>
<ul>
  <li>BrowserStack, Sauce Labs, Playwright-managed runners.</li>
  <li>Progressive enhancement — baseline HTML/CSS works everywhere; JS enhances.</li>
</ul>
<h4>Decide a support policy</h4>
<p>Explicit browserslist in <code>package.json</code>: <code>"&gt; 0.5%, last 2 versions, Firefox ESR, not dead"</code>. Drop IE11 if you can — most teams have.</p>
'''

ANSWERS[72] = r'''
<p>See also Q1. Short summary:</p>
<pre><code>// Classical (Java-like syntax, but JS is prototypal underneath)
class Animal { eat() {} }
class Dog extends Animal { bark() {} }

// Prototypal (what actually runs)
const animal = { eat() {} };
const dog = Object.create(animal);
dog.bark = function () {};</code></pre>
<table>
  <thead><tr><th>Classical</th><th>Prototypal</th></tr></thead>
  <tbody>
    <tr><td>Blueprint → instances</td><td>Object → linked object</td></tr>
    <tr><td>Static shape</td><td>Dynamic — add/change links at runtime</td></tr>
    <tr><td>Methods on class definition</td><td>Methods on prototype chain, shared</td></tr>
    <tr><td>Type is fixed at creation</td><td>Type is the whole chain</td></tr>
  </tbody>
</table>
<p>The ES6 <code>class</code> keyword is syntactic sugar over the prototype chain. You can still do things classical inheritance can't (change prototypes at runtime with <code>Object.setPrototypeOf</code>), though it's usually a bad idea for perf reasons.</p>
'''

ANSWERS[73] = r'''
<p>See Q33 for implementation. Summary:</p>
<p>A <strong>binary heap</strong> is a complete binary tree where each parent compares as ≤ (min-heap) or ≥ (max-heap) to its children. Stored as a flat array: parent at <code>i</code>, children at <code>2i+1</code> and <code>2i+2</code>.</p>
<ul>
  <li><code>push</code> — append to array, bubble up until heap property holds. O(log n).</li>
  <li><code>pop</code> — remove root, move last element to root, sift down. O(log n).</li>
  <li><code>peek</code> — return root. O(1).</li>
  <li><code>heapify(arr)</code> — bottom-up sift-down. O(n), not O(n log n).</li>
</ul>
<p>Uses:</p>
<ul>
  <li><strong>Priority queues</strong> — tasks with priorities, event scheduling.</li>
  <li><strong>Dijkstra / A*</strong> — shortest-path algorithms.</li>
  <li><strong>Top-K / running median</strong> (two heaps).</li>
  <li><strong>Heapsort</strong> — O(n log n) in-place sort.</li>
</ul>
<p>JS has no built-in heap. Libraries: <code>mnemonist</code>, <code>heap-js</code>, <code>@datastructures-js/priority-queue</code>.</p>
'''

ANSWERS[74] = r'''
<p><strong>Functional programming</strong> treats computation as evaluation of pure functions on immutable data.</p>
<h4>Principles</h4>
<ul>
  <li><strong>Pure functions</strong> — output depends only on input; no side effects.</li>
  <li><strong>Immutability</strong> — don't mutate, produce new values.</li>
  <li><strong>First-class functions</strong> — pass, return, store functions.</li>
  <li><strong>Composition</strong> — small pieces combine into bigger ones.</li>
  <li><strong>Referential transparency</strong> — swap a call with its result without changing behavior.</li>
</ul>
<h4>Benefits</h4>
<ul>
  <li>Easier to reason about — no hidden state.</li>
  <li>Trivial to test — inputs in, outputs out.</li>
  <li>Parallelism-friendly — no shared state to fight over.</li>
  <li>Predictable change detection — if the reference changed, something changed.</li>
</ul>
<pre><code>// Functional pipeline
const total = orders
  .filter(o =&gt; o.status === "paid")
  .map(o =&gt; o.amount)
  .reduce((sum, a) =&gt; sum + a, 0);</code></pre>
<p>JS is a multi-paradigm language — lean functional where it helps, escape to imperative for performance or where mutation is clearer. Libraries: Ramda, Lodash/fp, RxJS, Immer.</p>
'''

ANSWERS[75] = r'''
<pre><code>// Custom error classes
class AppError extends Error {
  constructor(message, options = {}) {
    super(message, options);
    this.name = this.constructor.name;
    this.code = options.code;
  }
}

class ValidationError extends AppError {}
class NotFoundError extends AppError {}

// Global handlers
window.addEventListener("error", (e) =&gt; {
  log.error(e.error);
  showToast("Something went wrong");
});
window.addEventListener("unhandledrejection", (e) =&gt; {
  log.error(e.reason);
});

// At the boundary — HTTP middleware (Express)
app.use((err, req, res, next) =&gt; {
  const status = err instanceof ValidationError ? 400
               : err instanceof NotFoundError   ? 404
               : 500;
  res.status(status).json({ error: err.message, code: err.code });
});</code></pre>
<p>Principles:</p>
<ul>
  <li>Throw specific subclasses — code that catches can discriminate.</li>
  <li>Use <code>cause</code> to chain errors without losing context: <code>throw new Error("x", { cause: err })</code>.</li>
  <li>One global handler for truly unexpected failures; structured handling at the boundaries (HTTP, UI).</li>
  <li>Log structured data, not stringified errors — keep stack traces.</li>
  <li>Report to observability (Sentry, Rollbar, Datadog).</li>
</ul>
'''

ANSWERS[76] = r'''
<table>
  <thead><tr><th></th><th>Sync iteration</th><th>Async iteration</th></tr></thead>
  <tbody>
    <tr><td>Protocol</td><td><code>Symbol.iterator</code> → <code>next()</code> returns <code>{value, done}</code></td><td><code>Symbol.asyncIterator</code> → <code>next()</code> returns a Promise</td></tr>
    <tr><td>Consumed with</td><td><code>for...of</code></td><td><code>for await...of</code></td></tr>
    <tr><td>Use case</td><td>Arrays, strings, Maps, Sets</td><td>Streams, paginated APIs, event streams</td></tr>
  </tbody>
</table>
<pre><code>// Async generator — build an async iterable
async function* pages(url) {
  let next = url;
  while (next) {
    const res = await fetch(next).then(r =&gt; r.json());
    yield* res.items;
    next = res.nextCursor;
  }
}

for await (const item of pages("/api/items")) {
  process(item);
}

// Node streams are async iterables since Node 10
for await (const chunk of fs.createReadStream("big.log")) {
  parse(chunk);
}</code></pre>
<p>Async iteration shines with lazy, backpressure-aware data: you pull one item at a time, awaiting only what you use. Compare to <code>Promise.all</code> (everything up front) — cleaner memory profile for large streams.</p>
'''

ANSWERS[77] = r'''
<pre><code>class Trie {
  constructor() { this.root = Object.create(null); this.root.end = false; }

  insert(word) {
    let node = this.root;
    for (const ch of word) {
      if (!node[ch]) node[ch] = Object.create(null);
      node = node[ch];
    }
    node.end = true;
  }

  has(word) {
    const node = this.#find(word);
    return !!node && node.end;
  }

  startsWith(prefix) {
    return !!this.#find(prefix);
  }

  #find(str) {
    let node = this.root;
    for (const ch of str) {
      if (!node[ch]) return null;
      node = node[ch];
    }
    return node;
  }
}

const t = new Trie();
t.insert("apple");
t.has("app");        // false
t.startsWith("app"); // true
t.insert("app");
t.has("app");        // true</code></pre>
<p>Uses: autocomplete, spell check, IP routing, word-break problems. Space-efficient when words share prefixes. For huge dictionaries, consider radix trees (compressed tries) or DAWGs.</p>
'''

ANSWERS[78] = r'''
<p><strong>Backpressure</strong> is the signal from a slow consumer to a fast producer saying &ldquo;slow down.&rdquo;</p>
<pre><code>// Node streams — pipe handles backpressure automatically
readStream.pipe(writeStream);

// Manual — check return value of write()
writeStream.on("drain", () =&gt; resume());
function send(chunk) {
  const ok = writeStream.write(chunk);
  if (!ok) pause();   // buffer is full — wait for "drain"
}

// Web Streams — .desiredSize signals pressure
const writable = new WritableStream({
  write(chunk, controller) { /* chunks await here */ }
}, { highWaterMark: 100 });</code></pre>
<h4>Strategies when backpressure hits</h4>
<ul>
  <li><strong>Pause upstream</strong> — readable streams emit <code>pause</code>/<code>resume</code> events.</li>
  <li><strong>Buffer with a cap</strong> and drop on overflow (telemetry / logging pipelines).</li>
  <li><strong>Sample / coalesce</strong> — keep only the latest reading.</li>
  <li><strong>Apply backpressure end-to-end</strong> — TCP, HTTP/2 support it natively.</li>
</ul>
<p>Ignoring backpressure leads to unbounded buffers and OOM kills. Always prefer <code>pipe</code>/<code>pipeTo</code> over manual writes when possible.</p>
'''

ANSWERS[79] = r'''
<h4>Reduce bytes</h4>
<ul>
  <li>Tree-shaking, dead-code elimination, minification, gzip/brotli.</li>
  <li>Code split routes with dynamic <code>import()</code>.</li>
  <li>Swap heavy libs for lighter alternatives (<code>dayjs</code> over <code>moment</code>, <code>zustand</code> over Redux for small apps).</li>
</ul>
<h4>Parallelize downloads</h4>
<ul>
  <li>HTTP/2 or HTTP/3 — multiplex many requests over one connection.</li>
  <li><code>&lt;link rel="preload"&gt;</code> for critical resources; <code>preconnect</code> for third-party origins.</li>
</ul>
<h4>Defer non-critical</h4>
<ul>
  <li><code>&lt;script defer&gt;</code> / <code>async</code>, lazy-load below-the-fold.</li>
  <li>Inline critical CSS, defer the rest.</li>
</ul>
<h4>Cache aggressively</h4>
<ul>
  <li>Long cache with content-hashed filenames.</li>
  <li>Service Worker for repeat visits.</li>
</ul>
<h4>Render fast</h4>
<ul>
  <li>SSR / static generation → HTML in first packet.</li>
  <li>Stream the response and hydrate progressively.</li>
</ul>
<h4>Measure</h4>
<p>Core Web Vitals: LCP, CLS, INP. Use Lighthouse, WebPageTest, RUM.</p>
'''

ANSWERS[80] = r'''
<h4>Match the scope to the need</h4>
<ul>
  <li><strong>Local (useState, useReducer)</strong> — component-owned state. Don't over-lift.</li>
  <li><strong>Shared (Context, zustand, Jotai, Redux Toolkit)</strong> — cross-component state.</li>
  <li><strong>Server state (TanStack Query, SWR, RTK Query)</strong> — data fetched from APIs. Treat separately from UI state — it's a cache, not a source of truth.</li>
  <li><strong>URL state</strong> — filters, current tab, modal open. Use the query string and <code>history</code> so deep-links work.</li>
  <li><strong>Form state</strong> — ephemeral; libraries like React Hook Form keep it out of the global tree.</li>
</ul>
<h4>Good habits</h4>
<ul>
  <li>Minimize derived state — compute from sources when rendering, don't store copies.</li>
  <li>Immutable updates (spread, Immer) — predictable equality checks.</li>
  <li>Normalize collections (<code>{ byId, allIds }</code>) for easy lookups.</li>
  <li>Co-locate state with usage first; promote to shared state only when genuinely shared.</li>
  <li>For cross-tab sync, use <code>BroadcastChannel</code> or <code>storage</code> event.</li>
</ul>
'''

ANSWERS[81] = r'''
<pre><code>const rules = {
  required: (v) =&gt; (v != null && v !== "") || "required",
  email:    (v) =&gt; /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || "invalid email",
  minLength: (n) =&gt; (v) =&gt; v.length &gt;= n || `min length ${n}`,
  pattern:   (re, msg) =&gt; (v) =&gt; re.test(v) || msg,
};

function validate(data, schema) {
  const errors = {};
  for (const [field, checks] of Object.entries(schema)) {
    for (const check of checks) {
      const ok = check(data[field], data);
      if (ok !== true) { errors[field] = ok; break; }
    }
  }
  return { valid: !Object.keys(errors).length, errors };
}

validate(
  { email: "not-an-email", password: "short" },
  {
    email:    [rules.required, rules.email],
    password: [rules.required, rules.minLength(8)],
  }
);</code></pre>
<p>Design principles: validators are pure functions returning <code>true</code> or an error message. Composable (a rule is a function; rules compose via arrays). Async validators return Promises. Collect all errors vs fail-fast as needed. Consider production libraries — Zod, Valibot, Yup, Joi — for schema definition, type inference, and comprehensive rule sets.</p>
'''

ANSWERS[82] = r'''
<p>The system around <code>package.json</code>, registries, and lockfiles.</p>
<h4>Key concepts</h4>
<ul>
  <li><strong>Semver</strong>: <code>^1.2.3</code> (compatible), <code>~1.2.3</code> (patches only), <code>1.2.3</code> (exact).</li>
  <li><strong>Lockfile</strong> — records exact resolved versions. Commit <code>package-lock.json</code>/<code>pnpm-lock.yaml</code>/<code>yarn.lock</code>.</li>
  <li><strong>dependencies</strong> vs <strong>devDependencies</strong> — runtime vs build/test only.</li>
  <li><strong>peerDependencies</strong> — host must provide this (common for plugins).</li>
  <li><strong>Workspaces</strong> — share deps across packages in a monorepo.</li>
</ul>
<h4>Package managers</h4>
<p><strong>npm</strong> (built-in, solid), <strong>pnpm</strong> (fast, strict, hard-linked <code>node_modules</code>), <strong>Yarn</strong> (mature, plug-n-play mode).</p>
<h4>Security</h4>
<ul>
  <li><code>npm audit</code>, Dependabot, Snyk for vuln reports.</li>
  <li>Pin versions for critical deps; use <code>overrides</code> to force patched transitive deps.</li>
  <li>Review new deps — supply-chain attacks are real.</li>
</ul>
<h4>Reproducibility</h4>
<p>Commit lockfile, use <code>npm ci</code> in CI, pin Node version (<code>.nvmrc</code>, <code>engines</code>).</p>
'''

ANSWERS[83] = r'''
<p>See Coding Q14 for the full implementation. Key points:</p>
<pre><code>function binarySearch(arr, target) {
  let lo = 0, hi = arr.length - 1;
  while (lo &lt;= hi) {
    const mid = (lo + hi) &gt;&gt; 1;
    if (arr[mid] === target) return mid;
    if (arr[mid] &lt; target) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}</code></pre>
<ul>
  <li>O(log n), O(1) space.</li>
  <li>Requires a sorted array.</li>
  <li>Variants: first occurrence (use <code>&lt;=</code> and keep searching left), last occurrence, insertion point (<code>lo</code> after loop).</li>
  <li>Binary search generalizes: search on the answer space (&ldquo;smallest X such that predicate is true&rdquo;).</li>
  <li>Watch out for overflow with <code>(lo + hi) / 2</code> in fixed-width languages; use <code>lo + (hi - lo) / 2</code>.</li>
</ul>
<p>Under-appreciated: binary search works on <em>predicates</em>, not just values. Example: smallest <code>d</code> such that you can eat all bananas in <code>h</code> hours eating <code>d</code>/hr.</p>
'''

ANSWERS[84] = r'''
<p>ES6 (2015) was the biggest revision in the language's history. Later years added small updates; ES5 was where things stood for a decade before.</p>
<h4>Major additions in ES6+</h4>
<ul>
  <li><code>let</code> / <code>const</code> — block scope, immutable bindings.</li>
  <li>Arrow functions, lexical <code>this</code>.</li>
  <li>Classes (sugar over prototypes).</li>
  <li>Template literals, destructuring, default parameters, spread/rest.</li>
  <li>Modules (<code>import</code>/<code>export</code>).</li>
  <li>Promises, <code>async</code>/<code>await</code> (ES2017).</li>
  <li>Generators, iterators, <code>Symbol</code>.</li>
  <li>New collections: <code>Map</code>, <code>Set</code>, <code>WeakMap</code>, <code>WeakSet</code>.</li>
  <li>Optional chaining <code>?.</code>, nullish coalescing <code>??</code> (ES2020).</li>
  <li><code>BigInt</code>, private class fields, top-level <code>await</code>.</li>
</ul>
<h4>Impact</h4>
<ul>
  <li>Dramatically more expressive — less boilerplate.</li>
  <li>Transpilers (Babel, TypeScript) let you use new features while targeting old browsers.</li>
  <li>Build tooling now assumed: bundler + transpiler + polyfills via <code>browserslist</code>.</li>
</ul>
<p>Most projects are ES2018+ at source. IE11 is dead; modern targets are usually safe.</p>
'''

ANSWERS[85] = r'''
<p>Implements the core spec: <code>.then</code>, <code>.catch</code>, state machine.</p>
<pre><code>class MyPromise {
  constructor(executor) {
    this.state = "pending";
    this.value = undefined;
    this.callbacks = [];
    const resolve = (v) =&gt; this.#settle("fulfilled", v);
    const reject  = (e) =&gt; this.#settle("rejected",  e);
    try { executor(resolve, reject); }
    catch (e) { reject(e); }
  }

  #settle(state, value) {
    if (this.state !== "pending") return;
    this.state = state;
    this.value = value;
    queueMicrotask(() =&gt; this.callbacks.forEach(cb =&gt; cb()));
  }

  then(onFulfilled, onRejected) {
    return new MyPromise((resolve, reject) =&gt; {
      const run = () =&gt; {
        try {
          const handler = this.state === "fulfilled" ? onFulfilled : onRejected;
          if (!handler) {
            this.state === "fulfilled" ? resolve(this.value) : reject(this.value);
            return;
          }
          const result = handler(this.value);
          result instanceof MyPromise ? result.then(resolve, reject) : resolve(result);
        } catch (e) { reject(e); }
      };
      if (this.state === "pending") this.callbacks.push(run);
      else queueMicrotask(run);
    });
  }

  catch(fn) { return this.then(null, fn); }
}</code></pre>
<p>A full Promises/A+ implementation is harder — thenable assimilation, cross-resolution with custom promises, and edge cases around re-entrant callbacks. Classic interview exercise, rarely needed in practice.</p>
'''

ANSWERS[86] = r'''
<p>See Q86 in Tricky and Basic — this is the canonical &ldquo;async/await vs promises&rdquo; question.</p>
<h4>Advantages over <code>.then</code> chains</h4>
<ul>
  <li><strong>Linear reading order</strong> — code looks top-to-bottom instead of callback-nested.</li>
  <li><strong>Try/catch unification</strong> — sync and async errors share the same handling path.</li>
  <li><strong>Normal control flow</strong> — loops, conditionals, destructuring all work without contortions.</li>
  <li><strong>Better stack traces</strong> — engines reconstruct logical call stacks across awaits.</li>
</ul>
<pre><code>// Promise chain
fetchUser(id)
  .then(u =&gt; fetchOrders(u.id))
  .then(o =&gt; fetchItems(o[0].id))
  .then(process)
  .catch(handle);

// async/await
try {
  const u = await fetchUser(id);
  const o = await fetchOrders(u.id);
  const i = await fetchItems(o[0].id);
  return await process(i);
} catch (e) { handle(e); }</code></pre>
<p>Pitfalls: unnecessary sequentialization (use <code>Promise.all</code> for independent work); forgetting to await (silent swallowed errors); top-level <code>await</code> only in modules.</p>
'''

ANSWERS[87] = r'''
<p><strong>CORS</strong> lets browsers request cross-origin resources while protecting users. The browser enforces the same-origin policy; servers opt in via response headers.</p>
<h4>Server response</h4>
<pre><code>Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true    // for cookies
Access-Control-Max-Age: 86400              // cache preflight</code></pre>
<h4>Flow</h4>
<ul>
  <li><strong>Simple requests</strong> (GET/HEAD/POST with safe content-types) — browser sends directly, server responds with CORS headers, browser checks.</li>
  <li><strong>Preflighted requests</strong> — browser sends OPTIONS first with <code>Access-Control-Request-Method</code>. Server must respond OK before the real request is sent.</li>
</ul>
<h4>Common mistakes</h4>
<ul>
  <li>Using <code>*</code> with credentials — forbidden. Must specify exact origin when <code>credentials: include</code>.</li>
  <li>Forgetting to handle OPTIONS on custom routes.</li>
  <li>Reverse-proxying to hide cross-origin — usually cleaner than configuring CORS.</li>
  <li>Server-to-server calls don't have CORS — CORS is a browser concept.</li>
</ul>
'''

ANSWERS[88] = r'''
<h4>Test pyramid</h4>
<ul>
  <li><strong>Unit tests</strong> — many, fast. Pure logic, reducers, utilities. Vitest / Jest.</li>
  <li><strong>Integration tests</strong> — some. Component trees, API clients with mocked HTTP. Testing Library, MSW.</li>
  <li><strong>E2E tests</strong> — a few. Critical user journeys against the real app. Playwright, Cypress.</li>
</ul>
<h4>Principles</h4>
<ul>
  <li>Test behavior, not implementation — queries like &ldquo;find button by text,&rdquo; not &ldquo;find by class.&rdquo;</li>
  <li>Arrange-Act-Assert structure.</li>
  <li>Each test independent — no shared mutable state.</li>
  <li>Fast feedback — watch mode, focused runs, parallelism.</li>
  <li>Flake hunting — quarantine, debug, or delete flaky tests; don't retry-until-green.</li>
</ul>
<h4>Tools</h4>
<ul>
  <li>Unit/integration: Vitest (faster), Jest (most common).</li>
  <li>Component: @testing-library/react.</li>
  <li>E2E: Playwright (mostly wins now), Cypress.</li>
  <li>Mock HTTP: MSW (Mock Service Worker) — intercepts at the network level, same mocks for dev and tests.</li>
  <li>Coverage: built into Vitest/Jest; don't chase 100%.</li>
</ul>
'''

ANSWERS[89] = r'''
<p>Fixed-size ring buffer — writes wrap around, overwriting the oldest.</p>
<pre><code>class CircularBuffer {
  constructor(capacity) {
    this.capacity = capacity;
    this.buf = new Array(capacity);
    this.head = 0;
    this.count = 0;
  }

  push(value) {
    const tail = (this.head + this.count) % this.capacity;
    this.buf[tail] = value;
    if (this.count &lt; this.capacity) this.count++;
    else this.head = (this.head + 1) % this.capacity;   // overwrite oldest
  }

  shift() {
    if (this.count === 0) return undefined;
    const v = this.buf[this.head];
    this.buf[this.head] = undefined;
    this.head = (this.head + 1) % this.capacity;
    this.count--;
    return v;
  }

  get size() { return this.count; }

  *[Symbol.iterator]() {
    for (let i = 0; i &lt; this.count; i++) {
      yield this.buf[(this.head + i) % this.capacity];
    }
  }
}

const cb = new CircularBuffer(3);
cb.push(1); cb.push(2); cb.push(3); cb.push(4);
[...cb];     // [2, 3, 4]</code></pre>
<p>Uses: audio/video buffering, rolling metrics, last-N log lines, producer/consumer pipes.</p>
'''

ANSWERS[90] = r'''
<p>See Q65 for the implementation. Key uses:</p>
<ul>
  <li><strong>HTTP servers</strong> — auth, logging, body parsing, error handling each as separate middleware (Express, Koa, Fastify).</li>
  <li><strong>Redux</strong> — <code>applyMiddleware</code> composes thunks, sagas, loggers around dispatch.</li>
  <li><strong>GraphQL</strong> — field middleware for auth, caching, timing.</li>
  <li><strong>Client request libs</strong> — axios interceptors, fetch wrappers for retries/tokens.</li>
  <li><strong>Build tools</strong> — webpack plugins, Vite plugins, Babel presets.</li>
</ul>
<p>Benefits:</p>
<ul>
  <li>Separation of concerns — each middleware does one thing.</li>
  <li>Reusable across routes/handlers.</li>
  <li>Composable order — the sequence of middlewares shapes behavior.</li>
  <li>Central point for cross-cutting concerns (auth, logging, metrics).</li>
</ul>
<p>Downside: nontrivial debugging when many middlewares touch the same request. Keep each one thin and single-purpose.</p>
'''

ANSWERS[91] = r'''
<h4>Don't load it all</h4>
<ul>
  <li><strong>Server-side pagination / filtering</strong> — best approach. Push the problem server-side where it belongs.</li>
  <li><strong>Streaming JSON</strong> — NDJSON (one JSON object per line) or <code>JSONStream</code> / <code>clarinet</code> parsers. Process as data arrives.</li>
</ul>
<pre><code>// NDJSON over fetch
const res = await fetch("/big");
const reader = res.body.getReader();
const dec = new TextDecoder();
let buf = "";
for (;;) {
  const { value, done } = await reader.read();
  if (done) break;
  buf += dec.decode(value, { stream: true });
  const lines = buf.split("\n");
  buf = lines.pop();
  for (const line of lines) if (line) process(JSON.parse(line));
}</code></pre>
<h4>If you must parse the whole thing</h4>
<ul>
  <li>Do it in a Web Worker so parsing doesn't block the main thread.</li>
  <li>Consider a binary format (MessagePack, Protobuf) that's cheaper to parse.</li>
  <li>Use JSON SIMD parsers (simdjson) in Node for ~2-3× speedup.</li>
</ul>
<h4>Server-side (Node)</h4>
<p>Don't build a giant string before parsing. Pipe: request → parser → transform → response. Memory stays flat regardless of size.</p>
'''

ANSWERS[92] = r'''
<p>See Q23 in this level and Q93 in Basic. Short form:</p>
<pre><code>// Shallow — nested objects shared by reference
const shallow = { ...obj };
const shallow2 = Object.assign({}, obj);
const shallow3 = [...arr];
const shallow4 = arr.slice();

// Deep — recursive copy
const deep = structuredClone(obj);   // modern, handles most types + cycles

// JSON round-trip — OK for pure data, drops functions/Dates/Maps
const deep2 = JSON.parse(JSON.stringify(obj));

// Custom recursive
function deepClone(v, seen = new WeakMap()) {
  if (v === null || typeof v !== "object") return v;
  if (seen.has(v)) return seen.get(v);
  const copy = Array.isArray(v) ? [] : {};
  seen.set(v, copy);
  for (const k of Object.keys(v)) copy[k] = deepClone(v[k], seen);
  return copy;
}</code></pre>
<p>When shallow is enough: you're going to replace nested parts wholesale. When you need deep: you'll mutate nested objects independently. Prefer immutable updates (<code>{ ...state, nested: { ...state.nested, x: 1 } }</code>) — you rarely need true deep clones.</p>
'''

ANSWERS[93] = r'''
<h4>Pick the right loop</h4>
<ul>
  <li>Classic <code>for</code> is the fastest for hot paths — no iterator allocation.</li>
  <li><code>for...of</code> is almost as fast and cleaner; use it unless benchmarks say otherwise.</li>
  <li><code>forEach</code> creates a function call per iteration; slower and can't <code>break</code>.</li>
</ul>
<h4>Don't recompute inside the loop</h4>
<pre><code>// Bad
for (let i = 0; i &lt; arr.length; i++) {  // length read every iteration
  doSomething(getConfig().x, arr[i]);   // called every iteration
}

// Better
const len = arr.length;
const { x } = getConfig();
for (let i = 0; i &lt; len; i++) {
  doSomething(x, arr[i]);
}</code></pre>
<h4>Keep functions monomorphic</h4>
<p>Don't mix types on the same call site (sometimes strings, sometimes numbers) — it forces the engine to deoptimize.</p>
<h4>Batch the work</h4>
<ul>
  <li>For huge arrays, process in chunks and yield with <code>await new Promise(r =&gt; setTimeout(r, 0))</code> to keep the UI responsive.</li>
  <li>Move hot loops to Web Workers.</li>
</ul>
<h4>Avoid allocation in the loop</h4>
<p>Pre-allocate arrays (<code>new Array(n)</code>) when size is known. Avoid intermediate arrays (<code>filter().map().reduce()</code>) on perf-critical code; do it in one pass.</p>
'''

ANSWERS[94] = r'''
<p><strong>AOP</strong> separates cross-cutting concerns (logging, timing, caching, transactions) from business logic by weaving them in at defined points.</p>
<pre><code>// Decorator-style wrapper
function withLogging(fn) {
  return function (...args) {
    console.log(`[${fn.name}] args:`, args);
    const t0 = performance.now();
    const result = fn.apply(this, args);
    console.log(`[${fn.name}] took ${performance.now() - t0}ms`);
    return result;
  };
}

const loggedProcess = withLogging(process);

// Stage 3 decorators (TC39)
function log(_, context) {
  return function (...args) {
    console.log(`calling ${context.name}`);
    return _.apply(this, args);
  };
}

class Service {
  @log
  process(x) { /* ... */ }
}</code></pre>
<p>Without dedicated AOP frameworks, JS achieves the same thing with HOCs, decorators, and proxies. NestJS has a more formal AOP system with <code>@Injectable</code> providers and interceptors. Overuse makes behavior hard to trace — keep the aspects few and obvious.</p>
'''

ANSWERS[95] = r'''
<p>Serialization = object → transportable form. JSON is the default, but you can customize.</p>
<pre><code>// toJSON hook — called by JSON.stringify
class Money {
  constructor(amount, currency) { this.amount = amount; this.currency = currency; }
  toJSON() { return `${this.amount} ${this.currency}`; }
}
JSON.stringify({ price: new Money(5, "USD") });   // {"price":"5 USD"}

// Replacer / reviver for full control
const data = { d: new Date(), m: new Map([["a", 1]]) };

const text = JSON.stringify(data, (key, value) =&gt; {
  if (value instanceof Date) return { __type: "Date", v: value.toISOString() };
  if (value instanceof Map)  return { __type: "Map",  v: [...value] };
  return value;
});

const parsed = JSON.parse(text, (key, value) =&gt; {
  if (value?.__type === "Date") return new Date(value.v);
  if (value?.__type === "Map")  return new Map(value.v);
  return value;
});</code></pre>
<p>For binary / efficiency: MessagePack, Protobuf, BSON, CBOR. For secure: sign with HMAC so you can detect tampering. Versioned schemas let you evolve formats without breaking old data.</p>
'''

ANSWERS[96] = r'''
<p>Both yield values lazily. Sync generators yield synchronously; async generators <code>await</code> between yields.</p>
<pre><code>// Sync generator
function* range(n) {
  for (let i = 0; i &lt; n; i++) yield i;
}
for (const v of range(3)) console.log(v);

// Async generator
async function* pages(baseUrl) {
  let next = baseUrl;
  while (next) {
    const res = await fetch(next);
    const data = await res.json();
    yield* data.items;
    next = data.nextCursor;
  }
}

for await (const item of pages("/api/items")) {
  console.log(item);
}</code></pre>
<table>
  <thead><tr><th></th><th>Sync generator</th><th>Async generator</th></tr></thead>
  <tbody>
    <tr><td>Syntax</td><td><code>function*</code></td><td><code>async function*</code></td></tr>
    <tr><td>Return type</td><td>Iterator</td><td>Async iterator</td></tr>
    <tr><td>Consumed with</td><td><code>for...of</code></td><td><code>for await...of</code></td></tr>
    <tr><td>Use case</td><td>Lazy computation, infinite sequences</td><td>Paginated APIs, streams, event sources</td></tr>
  </tbody>
</table>
<p>Async generators are ideal for paginated endpoints or I/O streams — backpressure is built in (the consumer pulls when ready).</p>
'''

ANSWERS[97] = r'''
<p>A self-balancing BST with height guarantee O(log n). Full production-ready code is ~150 lines; here's the structure.</p>
<pre><code>class RBNode {
  constructor(val, color = "red") {
    this.val = val;
    this.color = color;
    this.left = this.right = this.parent = null;
  }
}

class RedBlackTree {
  constructor() {
    this.NIL = new RBNode(null, "black");
    this.root = this.NIL;
  }

  insert(val) {
    const node = new RBNode(val);
    node.left = node.right = this.NIL;
    // BST insert...
    node.color = "red";
    this.#fixInsert(node);
  }

  #fixInsert(node) {
    while (node.parent?.color === "red") {
      // Case 1: uncle red → recolor
      // Case 2: uncle black, node on &ldquo;inside&rdquo; → rotate to outside
      // Case 3: uncle black, node on &ldquo;outside&rdquo; → rotate grandparent
    }
    this.root.color = "black";
  }

  #leftRotate(x) { /* ... */ }
  #rightRotate(x) { /* ... */ }
}</code></pre>
<p>Rules: every node red or black; root black; red nodes have black children; every path from root to leaf has the same black depth. Invariants guarantee height ≤ 2·log(n+1).</p>
<p>Rarely hand-written in JS — use libraries (<code>@datastructures-js/red-black-tree</code>) or a simpler AVL tree, which has similar perf characteristics.</p>
'''

ANSWERS[98] = r'''
<p><strong>Code splitting</strong> breaks a bundle into smaller chunks loaded on demand.</p>
<h4>Strategies</h4>
<ul>
  <li><strong>Route-level</strong> — each page is its own chunk. Biggest win for most apps.</li>
  <li><strong>Component-level</strong> — heavy components (charts, editors) behind <code>React.lazy</code>.</li>
  <li><strong>Vendor split</strong> — third-party deps in a separate long-cacheable chunk.</li>
  <li><strong>Dynamic feature loading</strong> — admin panel, modals, A/B tests.</li>
</ul>
<pre><code>// Route split
const Admin = React.lazy(() =&gt; import("./Admin"));

// On-interaction
button.onclick = async () =&gt; {
  const { openEditor } = await import("./editor");
  openEditor();
};</code></pre>
<h4>Benefits</h4>
<ul>
  <li>Smaller initial bundle → faster first paint / TTI.</li>
  <li>Users download only what they use.</li>
  <li>Long-cacheable vendor chunks — app updates don't invalidate <code>react-dom</code>.</li>
</ul>
<h4>Watch out for</h4>
<ul>
  <li>Too many small chunks → waterfalls (chunk A requests chunk B requests chunk C). Preload eagerly where sensible.</li>
  <li>Show a skeleton/loader while chunks load — don't flash.</li>
  <li>Warm up likely-next chunks with <code>&lt;link rel="prefetch"&gt;</code>.</li>
</ul>
'''

ANSWERS[99] = r'''
<h4>Session types</h4>
<ul>
  <li><strong>Server-side sessions</strong> — server stores session data keyed by an opaque ID. The client holds only the ID in an <code>HttpOnly</code> cookie. Simple to revoke.</li>
  <li><strong>JWT / stateless</strong> — session data signed and sent to the client. Easy to scale; harder to revoke. Short-lived access + long-lived refresh tokens mitigates.</li>
</ul>
<h4>Client-side storage</h4>
<ul>
  <li>Prefer <code>HttpOnly; Secure; SameSite=Lax</code> cookies — invisible to JS, resistant to XSS.</li>
  <li><code>localStorage</code> for tokens is risky (XSS exfiltration).</li>
  <li>CSRF: same-site cookies help, or use CSRF tokens for state-changing requests.</li>
</ul>
<h4>Lifecycle</h4>
<ul>
  <li>Idle timeout — log out after N minutes of inactivity.</li>
  <li>Absolute timeout — force re-auth after M hours regardless.</li>
  <li>Rotate session IDs on privilege change (login, role switch) to prevent session fixation.</li>
  <li>Invalidate on logout both client and server side.</li>
</ul>
<h4>Cross-tab sync</h4>
<p><code>BroadcastChannel</code> or the <code>storage</code> event lets one tab notice when another logs out.</p>
<p>Libraries: NextAuth, Lucia, Clerk, Auth0 — use these instead of rolling your own.</p>
'''

ANSWERS[100] = r'''
<h4>Lockfile discipline</h4>
<ul>
  <li>Commit <code>package-lock.json</code>/<code>pnpm-lock.yaml</code>/<code>yarn.lock</code>.</li>
  <li>CI uses <code>npm ci</code>/<code>pnpm install --frozen-lockfile</code> — reproducible builds.</li>
  <li>Pin Node version: <code>.nvmrc</code>, <code>"engines"</code> field.</li>
</ul>
<h4>Keep deps current but safe</h4>
<ul>
  <li>Dependabot / Renovate for automated PRs.</li>
  <li><code>npm audit</code> + Snyk for security scans.</li>
  <li>Renovate in &ldquo;grouped&rdquo; mode avoids PR flood.</li>
</ul>
<h4>Minimize surface</h4>
<ul>
  <li>Review new deps — supply-chain attacks are real (npm malware incidents).</li>
  <li>Prefer deps that are well-maintained, small, zero-dep themselves.</li>
  <li>Dedupe with <code>npm dedupe</code>, workspace protocols in monorepos.</li>
</ul>
<h4>Semver hygiene</h4>
<ul>
  <li><code>^</code> for libs (auto-bump non-breaking), <code>~</code> or exact for tooling where surprises are painful.</li>
  <li>Use <code>overrides</code> to force-patch vulnerable transitive deps.</li>
</ul>
<h4>Types</h4>
<p>Install <code>@types/*</code> alongside untyped libs; keep TS versions aligned.</p>
<h4>Avoid install-time scripts</h4>
<p>Some packages run scripts on install — audit them. <code>pnpm</code> is stricter by default.</p>
'''
