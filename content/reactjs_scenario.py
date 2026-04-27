"""ReactJS Scenario Based answers.

Each answer is HTML-formatted prose for the chapter renderer.
Style: Scenario-Based — Situation → Approach → Trade-offs structure.
"""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>Situation:</strong> a list of items needs to filter as the user types in a search bar. The dataset can range from a few dozen items (client-side filter is fine) to hundreds of thousands (server-side, with debouncing) &mdash; the right architecture depends on size, freshness, and query complexity.</p>

<p><strong>Approach:</strong> for small client datasets, filter in <code>useMemo</code>; for large or server-backed datasets, debounce the query and fetch from an API. Use <code>useDeferredValue</code> (React 18+) to keep the input responsive when filtering is expensive.</p>

<pre><code>import { useState, useDeferredValue, useMemo } from "react";

function SearchableList({ items }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);   // input updates immediately

  const results = useMemo(() =&gt; {
    if (!deferredQuery) return items;
    const q = deferredQuery.toLowerCase();
    return items.filter(item =&gt;
      item.name.toLowerCase().includes(q) ||
      item.description?.toLowerCase().includes(q)
    );
  }, [items, deferredQuery]);

  return (
    &lt;&gt;
      &lt;input
        type="search"
        value={query}
        onChange={e =&gt; setQuery(e.target.value)}
        placeholder="Search..."
        autoFocus
      /&gt;
      &lt;p&gt;{results.length} of {items.length} results&lt;/p&gt;
      &lt;ul&gt;{results.map(r =&gt; &lt;li key={r.id}&gt;{r.name}&lt;/li&gt;)}&lt;/ul&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Server-side variant with debounce + TanStack Query:</strong></p>

<pre><code>import { useDebounce } from "use-debounce";

function ServerSearch() {
  const [query, setQuery] = useState("");
  const [debouncedQuery] = useDebounce(query, 300);

  const { data, isFetching } = useQuery({
    queryKey: ["search", debouncedQuery],
    queryFn: () =&gt; fetch(`/api/search?q=${encodeURIComponent(debouncedQuery)}`).then(r =&gt; r.json()),
    enabled: debouncedQuery.length &gt;= 2,
    placeholderData: keepPreviousData    // smooth typing — keeps old results visible during refetch
  });

  return (
    &lt;&gt;
      &lt;input value={query} onChange={e =&gt; setQuery(e.target.value)} /&gt;
      {isFetching &amp;&amp; &lt;Spinner /&gt;}
      &lt;Results items={data || []} /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Best for</th><th>Limit</th></tr>
  <tr><td>Client-side <code>filter</code></td><td>&lt; 1,000 items</td><td>Slows on large datasets; no fuzzy match</td></tr>
  <tr><td>Client + Fuse.js</td><td>1k-100k items, typo tolerance</td><td>Index size; load all data first</td></tr>
  <tr><td>Server-side debounced</td><td>Any size; real-time data</td><td>Network latency on every search</td></tr>
  <tr><td>Algolia / Meilisearch</td><td>Millions of items, full-text, ranking</td><td>External service, cost</td></tr>
</table>

<p><strong>Production polish:</strong> debounce 250-400ms (catches typing pauses without feeling laggy); cancel stale requests (TanStack Query auto-handles via query keys); URL-sync via <code>useSearchParams</code> for shareable searches; show "no results for X" with suggestions; preserve previous results during refetch (prevents flickering).</p>
'''

ANSWERS[2] = r'''
<p><strong>Situation:</strong> displaying server data in a paginated table is one of the most common React patterns &mdash; admin panels, e-commerce listings, log viewers. Real production tables also need sorting, filtering, column resizing, row selection, and accessibility. Roll-your-own works to ~500 rows with simple needs; for production, a headless table library scales better.</p>

<p><strong>Approach:</strong> use <strong>TanStack Query</strong> for server fetching with <code>keepPreviousData</code> (smooth pagination), <strong>TanStack Table</strong> for sorting/filtering/columns, and URL state via <code>useSearchParams</code> for shareability.</p>

<pre><code>import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";

function ProductsTable() {
  const [params, setParams] = useSearchParams();
  const page = Number(params.get("page") || 1);
  const sortBy = params.get("sort") || "name";
  const limit = 20;

  const { data, isLoading, isFetching, isError } = useQuery({
    queryKey: ["products", { page, sortBy, limit }],
    queryFn: () =&gt; fetch(`/api/products?page=${page}&amp;sort=${sortBy}&amp;limit=${limit}`).then(r =&gt; r.json()),
    placeholderData: keepPreviousData    // keeps previous page visible during fetch
  });

  if (isLoading) return &lt;TableSkeleton rows={limit} /&gt;;
  if (isError)   return &lt;ErrorBanner onRetry={refetch} /&gt;;

  const totalPages = Math.ceil(data.total / limit);

  const setSort = (col) =&gt; setParams(p =&gt; { p.set("sort", col); p.set("page", "1"); return p; });
  const setPage = (n) =&gt; setParams(p =&gt; { p.set("page", String(n)); return p; });

  return (
    &lt;div&gt;
      {isFetching &amp;&amp; &lt;ProgressBar /&gt;}

      &lt;table&gt;
        &lt;thead&gt;
          &lt;tr&gt;
            &lt;th onClick={() =&gt; setSort("name")}&gt;Name {sortBy === "name" &amp;&amp; "▼"}&lt;/th&gt;
            &lt;th onClick={() =&gt; setSort("price")}&gt;Price&lt;/th&gt;
            &lt;th onClick={() =&gt; setSort("stock")}&gt;Stock&lt;/th&gt;
          &lt;/tr&gt;
        &lt;/thead&gt;
        &lt;tbody&gt;
          {data.items.map(p =&gt; (
            &lt;tr key={p.id}&gt;
              &lt;td&gt;{p.name}&lt;/td&gt;&lt;td&gt;${p.price}&lt;/td&gt;&lt;td&gt;{p.stock}&lt;/td&gt;
            &lt;/tr&gt;
          ))}
        &lt;/tbody&gt;
      &lt;/table&gt;

      &lt;Pagination
        page={page}
        totalPages={totalPages}
        onChange={setPage}
      /&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Options</th></tr>
  <tr><td>Pagination style</td><td>Numbered (knowable total) vs cursor-based (better for changing data)</td></tr>
  <tr><td>Where state lives</td><td>URL (shareable, refresh-safe) vs component (simpler, not sharable)</td></tr>
  <tr><td>Server vs client filter</td><td>Server scales; client gives instant filtering on already-loaded data</td></tr>
  <tr><td>Skeleton vs spinner</td><td>Skeletons feel faster; spinners are simpler</td></tr>
  <tr><td>Roll-your-own vs library</td><td>TanStack Table for production (column resize, sort, virtualization)</td></tr>
</table>

<p><strong>Production polish:</strong> URL-driven state means the back button works correctly, refreshes preserve the page, and links can be shared. <code>keepPreviousData</code> prevents the table from flashing empty between pages. Cursor pagination beats offset for fast-changing lists (offset can show duplicates or skip rows when items are added/deleted between fetches). For 10k+ visible rows, virtualize with TanStack Virtual.</p>
'''

ANSWERS[3] = r'''
<p><strong>Situation:</strong> multi-step forms (checkout flows, onboarding wizards, application forms) require accumulating data across steps, validating each step before advancing, allowing back navigation without losing data, and ideally surviving accidental refresh. Common pitfalls: losing data on back, validating incorrectly when fields aren&rsquo;t shown, and breaking on browser back/refresh.</p>

<p><strong>Approach:</strong> single source of truth for accumulated form state (<code>useReducer</code> or React Hook Form), validation per-step with Zod schemas, persistence to <code>sessionStorage</code> for refresh resilience, URL-driven step (so browser back works).</p>

<pre><code>import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, useParams } from "react-router-dom";

const personalSchema = z.object({
  name: z.string().min(2),
  email: z.string().email()
});
const addressSchema = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  zip: z.string().regex(/^\d{5}$/)
});
const paymentSchema = z.object({
  cardNumber: z.string().regex(/^\d{13,19}$/),
  expiry: z.string().regex(/^(0[1-9]|1[0-2])\/\d{2}$/)
});

const SCHEMAS = { personal: personalSchema, address: addressSchema, payment: paymentSchema };
const STEPS = ["personal", "address", "payment"];

function CheckoutWizard() {
  const { step = "personal" } = useParams();
  const navigate = useNavigate();

  // Persist accumulated data so refresh doesn&rsquo;t wipe progress
  const methods = useForm({
    resolver: zodResolver(SCHEMAS[step]),
    defaultValues: () =&gt; JSON.parse(sessionStorage.getItem("checkout") || "{}")
  });

  const onValid = methods.handleSubmit(async (data) =&gt; {
    const merged = { ...JSON.parse(sessionStorage.getItem("checkout") || "{}"), ...data };
    sessionStorage.setItem("checkout", JSON.stringify(merged));

    const next = STEPS[STEPS.indexOf(step) + 1];
    if (next) {
      navigate(`/checkout/${next}`);
    } else {
      await fetch("/api/checkout", { method: "POST", body: JSON.stringify(merged) });
      sessionStorage.removeItem("checkout");
      navigate("/checkout/success");
    }
  });

  return (
    &lt;FormProvider {...methods}&gt;
      &lt;ProgressBar current={STEPS.indexOf(step)} total={STEPS.length} /&gt;
      &lt;form onSubmit={onValid}&gt;
        {step === "personal" &amp;&amp; &lt;PersonalStep /&gt;}
        {step === "address"  &amp;&amp; &lt;AddressStep /&gt;}
        {step === "payment"  &amp;&amp; &lt;PaymentStep /&gt;}

        &lt;button type="button" onClick={() =&gt; navigate(-1)} disabled={step === "personal"}&gt;
          Back
        &lt;/button&gt;
        &lt;button type="submit"&gt;
          {step === "payment" ? "Complete order" : "Continue"}
        &lt;/button&gt;
      &lt;/form&gt;
    &lt;/FormProvider&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Choice</th><th>Trade-off</th></tr>
  <tr><td>URL-driven step (<code>/checkout/payment</code>)</td><td>Browser back works; users can&rsquo;t skip ahead via URL manipulation alone &mdash; gate via redirect if previous data missing</td></tr>
  <tr><td>State-only step (<code>useState</code>)</td><td>Simpler but breaks browser back / refresh / shareable links</td></tr>
  <tr><td>Per-step schema (Zod)</td><td>Only validates fields shown; <strong>plus</strong> server validates the whole shape on submit (defense in depth)</td></tr>
  <tr><td><code>sessionStorage</code> persistence</td><td>Survives accidental refresh but cleared on tab close; <code>localStorage</code> persists too long (tab abandonment)</td></tr>
  <tr><td>One <code>useForm</code> per step vs one shared</td><td>Per-step is simpler with RHF; one shared keeps the type as a single object</td></tr>
</table>

<p><strong>Production polish:</strong> always re-validate on the server &mdash; client validation is UX, not security. Show progress (step N of M) so users know how far they have to go. For long forms, save partial progress server-side after each step so users can resume on a different device. <strong>Final-step idempotency:</strong> use a request key to prevent double-submit (a payment step that double-charges is a serious bug).</p>
'''

ANSWERS[4] = r'''
<p><strong>Situation:</strong> infinite scroll loads more items as the user reaches the bottom of a list. Used in social feeds, search results, image galleries. Common pitfalls: scroll-event listeners that fire too often (kill performance), missing cleanup (memory leaks), forgetting "no more data" state, and breaking accessibility (keyboard users can&rsquo;t reach footer content below an infinite list).</p>

<p><strong>Approach:</strong> <strong>IntersectionObserver</strong> with a sentinel element &mdash; far better than scroll listeners. Pair with <strong>TanStack Query&rsquo;s <code>useInfiniteQuery</code></strong> for server-backed pagination; for tiny client datasets, manually batch.</p>

<pre><code>import { useInfiniteQuery } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

function InfiniteFeed() {
  const sentinelRef = useRef(null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError
  } = useInfiniteQuery({
    queryKey: ["feed"],
    queryFn: ({ pageParam = null }) =&gt;
      fetch(`/api/feed?cursor=${pageParam || ""}`).then(r =&gt; r.json()),
    getNextPageParam: (last) =&gt; last.nextCursor   // null when no more pages
  });

  // IntersectionObserver triggers next page when sentinel is near viewport
  useEffect(() =&gt; {
    if (!hasNextPage || isFetchingNextPage) return;

    const observer = new IntersectionObserver(
      ([entry]) =&gt; {
        if (entry.isIntersecting) fetchNextPage();
      },
      { rootMargin: "200px" }   // start loading 200px before sentinel enters viewport
    );

    if (sentinelRef.current) observer.observe(sentinelRef.current);
    return () =&gt; observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  if (isLoading) return &lt;FeedSkeleton /&gt;;
  if (isError)   return &lt;ErrorBanner /&gt;;

  return (
    &lt;&gt;
      &lt;ul&gt;
        {data.pages.flatMap(page =&gt; page.items).map(item =&gt; (
          &lt;li key={item.id}&gt;{item.title}&lt;/li&gt;
        ))}
      &lt;/ul&gt;

      {/* Sentinel — invisible div that triggers fetch when scrolled near */}
      {hasNextPage &amp;&amp; &lt;div ref={sentinelRef} style={{ height: 20 }} /&gt;}

      {isFetchingNextPage &amp;&amp; &lt;LoadingSpinner /&gt;}
      {!hasNextPage &amp;&amp; &lt;p&gt;You&rsquo;re all caught up&lt;/p&gt;}
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pattern</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>Pure infinite scroll</td><td>Maximum engagement; mobile-friendly</td><td>No footer access; lost-place problem on back; bad for SEO</td></tr>
  <tr><td>Load-more button</td><td>Better accessibility; controlled load</td><td>Extra click; less seamless</td></tr>
  <tr><td>Hybrid (auto + button)</td><td>Auto-loads N pages, then asks user</td><td>More logic; sweet spot for many apps</td></tr>
  <tr><td>Numbered pagination</td><td>Sharable URLs; jump to page; works for crawlers</td><td>Less natural for feeds</td></tr>
</table>

<p><strong>Production concerns:</strong></p>
<ul>
  <li><strong>Cursor over offset</strong> &mdash; offset (<code>page=5</code>) breaks when items are added/deleted between fetches (duplicates or skips). Cursor-based pagination uses an opaque pointer (last item&rsquo;s ID or timestamp).</li>
  <li><strong>Virtualization</strong> &mdash; for 1000+ items rendered at once, use <strong>TanStack Virtual</strong> to render only visible rows. Without it, the DOM bloats and scrolling lags.</li>
  <li><strong>Restore scroll position</strong> &mdash; when user clicks a feed item, drills into detail, then comes back, scroll to where they were. React Router v6.4+ has scroll restoration; otherwise track manually.</li>
  <li><strong>Accessibility</strong> &mdash; provide a "Skip to footer" link. Add <code>aria-busy</code> on the list during load. Make sure the sentinel never has focusable content (would trap keyboard users).</li>
  <li><strong>Sentinel positioning</strong> &mdash; <code>rootMargin: "200px"</code> starts loading <em>before</em> the sentinel enters viewport, so users see no pause.</li>
</ul>
'''

ANSWERS[5] = r'''
<p><strong>Situation:</strong> a large React app has state that needs to be shared across many components &mdash; auth, user preferences, shopping cart, notifications, server data. Wrong choice creates either prop-drilling hell, performance disasters, or unmaintainable spaghetti. The right architecture separates <strong>server state</strong> (cached API data) from <strong>client state</strong> (UI/auth/user choices) and uses different tools for each.</p>

<p><strong>Approach:</strong> the modern 2026 stack &mdash; <strong>TanStack Query</strong> for server state, <strong>Zustand</strong> for global client state, <strong>Context</strong> for tree-scoped values (theme, locale, auth), <strong><code>useState</code>/<code>useReducer</code></strong> for component-local state. Use the simplest tool that fits each piece.</p>

<pre><code>// Server state — TanStack Query
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

function useUserProfile(userId) {
  return useQuery({
    queryKey: ["user", userId],
    queryFn: () =&gt; api.fetchUser(userId),
    staleTime: 5 * 60 * 1000     // fresh for 5 minutes
  });
}

// Global client state — Zustand
import { create } from "zustand";

const useAppStore = create((set) =&gt; ({
  cart: [],
  notifications: [],
  addToCart: (item) =&gt; set((s) =&gt; ({ cart: [...s.cart, item] })),
  removeFromCart: (id) =&gt; set((s) =&gt; ({ cart: s.cart.filter(i =&gt; i.id !== id) })),
  notify: (msg) =&gt; set((s) =&gt; ({
    notifications: [...s.notifications, { id: Date.now(), msg }]
  }))
}));

// Components subscribe selectively — only re-render when their slice changes
function CartBadge() {
  const count = useAppStore(state =&gt; state.cart.length);
  return &lt;span&gt;{count}&lt;/span&gt;;
}

// Tree-scoped — Context for theme, auth, locale
const AuthContext = createContext(null);
function App() {
  return (
    &lt;AuthProvider&gt;
      &lt;ThemeProvider&gt;
        &lt;Routes /&gt;
      &lt;/ThemeProvider&gt;
    &lt;/AuthProvider&gt;
  );
}</code></pre>

<p><strong>The rule of thumb &mdash; what goes where:</strong></p>

<table>
  <tr><th>State type</th><th>Tool</th><th>Why</th></tr>
  <tr><td>Server data (API responses)</td><td>TanStack Query</td><td>Auto-cache, refetch, dedup; never duplicate in client store</td></tr>
  <tr><td>Cross-route global state (cart, prefs)</td><td>Zustand</td><td>Lightweight, selective subscriptions, no provider tree</td></tr>
  <tr><td>App-wide infrequent (theme, auth, i18n)</td><td>Context</td><td>Built-in, low-update, semantic</td></tr>
  <tr><td>Form state</td><td>React Hook Form</td><td>Performance, validation, dirty tracking</td></tr>
  <tr><td>URL state (filters, page, search)</td><td>Router search params</td><td>Shareable, refresh-safe</td></tr>
  <tr><td>Component-local UI state</td><td><code>useState</code></td><td>Simplest tool; doesn&rsquo;t bleed</td></tr>
</table>

<p><strong>Anti-patterns to avoid:</strong></p>
<ul>
  <li><strong>Server data in Redux/Zustand:</strong> you re-implement caching, refetch, and stale-while-revalidate. Use TanStack Query.</li>
  <li><strong>Context for high-frequency state:</strong> every consumer re-renders on any change. A live counter in Context tanks performance.</li>
  <li><strong>One giant Zustand store:</strong> split by domain (auth store, cart store, ui store). Easier to reason about; cleaner devtools.</li>
  <li><strong>State everywhere:</strong> if state can be derived from other state, derive it; don&rsquo;t store it.</li>
</ul>

<p><strong>When Redux Toolkit still wins:</strong> large apps with strong action-log requirements (audit trails, time-travel debugging), complex middleware pipelines, or teams already familiar with Redux. RTK Query gives you Redux + TanStack-Query-like server caching in one package.</p>

<p><strong>For very small apps</strong>, you may not need any of this &mdash; <code>useState</code> + Context is fine until proven otherwise. Premature global state is technical debt.</p>
'''

ANSWERS[6] = r'''
<p><strong>Situation:</strong> a list with hundreds or thousands of items renders slowly &mdash; scrolling stutters, typing in search lags, the page freezes during updates. Common causes: rendering all items even though only ~20 are visible, expensive computations on every render, deep object props that defeat memoization, and inefficient key strategy.</p>

<p><strong>Approach:</strong> apply optimizations in order of impact: <strong>virtualization</strong> first (biggest win), then memoization (specific bottlenecks), then concurrent features (smooth interactions). <strong>Profile with React DevTools first</strong> &mdash; don&rsquo;t guess.</p>

<pre><code>// 1. VIRTUALIZATION — render only visible rows
import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef } from "react";

function VirtualList({ items }) {
  const parentRef = useRef(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () =&gt; parentRef.current,
    estimateSize: () =&gt; 60,    // estimated row height
    overscan: 5                  // render 5 extra rows above/below viewport
  });

  return (
    &lt;div ref={parentRef} style={{ height: 600, overflow: "auto" }}&gt;
      &lt;div style={{ height: virtualizer.getTotalSize(), position: "relative" }}&gt;
        {virtualizer.getVirtualItems().map(virtualRow =&gt; (
          &lt;div
            key={virtualRow.key}
            style={{
              position: "absolute",
              top: 0,
              transform: `translateY(${virtualRow.start}px)`,
              width: "100%"
            }}
          &gt;
            &lt;Row item={items[virtualRow.index]} /&gt;
          &lt;/div&gt;
        ))}
      &lt;/div&gt;
    &lt;/div&gt;
  );
}

// 2. MEMOIZE expensive rows
const Row = memo(function Row({ item }) {
  return &lt;div className="row"&gt;{item.name} &mdash; {item.price}&lt;/div&gt;;
}, (prev, next) =&gt; prev.item.id === next.item.id &amp;&amp; prev.item.version === next.item.version);

// 3. STABLE props from parent — useCallback for handlers, useMemo for derived data
function ParentList({ items }) {
  const handleClick = useCallback((id) =&gt; { ... }, []);
  const sortedItems = useMemo(() =&gt; [...items].sort(byName), [items]);
  return &lt;VirtualList items={sortedItems} onItemClick={handleClick} /&gt;;
}</code></pre>

<p><strong>The diagnosis playbook &mdash; what to optimize and how to know:</strong></p>

<table>
  <tr><th>Symptom</th><th>Diagnosis</th><th>Fix</th></tr>
  <tr><td>Slow scroll on long list</td><td>Profiler shows all rows render</td><td>Virtualize (<strong>biggest win</strong>)</td></tr>
  <tr><td>Lag while typing in search</td><td>Filter runs on every keystroke</td><td><code>useDeferredValue</code> + <code>useMemo</code></td></tr>
  <tr><td>Whole list re-renders on item update</td><td>Profiler "why did this render"</td><td><code>memo</code> rows; stable keys</td></tr>
  <tr><td>Memo doesn&rsquo;t help</td><td>New object/array prop every render</td><td>Wrap in <code>useMemo</code> at parent</td></tr>
  <tr><td>Initial bundle huge</td><td>Bundle analyzer shows big imports</td><td>Code split with <code>lazy()</code> + dynamic imports</td></tr>
  <tr><td>Index-based keys cause issues on reorder</td><td>React reuses wrong DOM nodes</td><td>Use stable IDs as keys</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>Virtualization</strong> is the single biggest performance win for long lists, but breaks Ctrl+F (browser search), screen-reader sequential reading, and copy-paste of off-screen content. For accessibility-critical apps (long forms, e-commerce checkout), keep all DOM but virtualize only the truly massive parts.</li>
  <li><strong>React.memo</strong> only helps when the component would actually re-render unnecessarily. Profile first &mdash; cheap components don&rsquo;t benefit, and tracking equality has its own cost.</li>
  <li><strong>React Compiler</strong> (React 19+) auto-applies memoization where beneficial &mdash; in compiler-enabled projects, manual <code>memo</code>/<code>useMemo</code>/<code>useCallback</code> become rare. The biggest hand-tuning need shifts to virtualization and code splitting.</li>
  <li><strong>Don&rsquo;t over-engineer:</strong> a 100-item list doesn&rsquo;t need virtualization. Apply techniques where measurements show pain.</li>
</ul>

<p>Use <strong>React DevTools Profiler</strong> with "Highlight updates when components render" enabled to actually see what&rsquo;s happening. Performance optimization based on speculation almost always misses the real bottleneck.</p>
'''

ANSWERS[7] = r'''
<p><strong>Situation:</strong> a React app needs login/logout, persistent sessions across page reloads, protected routes, and authenticated API calls. The wrong approach (storing tokens in localStorage, no refresh logic, weak server validation) creates both UX problems and real security vulnerabilities.</p>

<p><strong>Approach:</strong> for new apps in 2026, use a managed service &mdash; <strong>Clerk</strong>, <strong>Supabase Auth</strong>, <strong>Auth0</strong>, or <strong>Firebase Auth</strong> &mdash; rather than rolling your own. They handle token rotation, OAuth flows, MFA, and security audits. For self-hosted, use <strong>httpOnly cookies</strong> with backend session validation, never localStorage tokens.</p>

<pre><code>// === Auth context with httpOnly cookie session ===
import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount, ask backend if we have a session
  useEffect(() =&gt; {
    fetch("/api/auth/me", { credentials: "include" })
      .then(r =&gt; r.ok ? r.json() : null)
      .then(setUser)
      .finally(() =&gt; setIsLoading(false));
  }, []);

  const login = async (email, password) =&gt; {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "include",   // send/receive cookies
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error("Invalid credentials");
    setUser(await res.json());
  };

  const logout = async () =&gt; {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
    setUser(null);
  };

  return (
    &lt;AuthContext.Provider value={{ user, isLoading, login, logout }}&gt;
      {children}
    &lt;/AuthContext.Provider&gt;
  );
}

const useAuth = () =&gt; useContext(AuthContext);

// === Protected route ===
function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return &lt;LoadingScreen /&gt;;
  if (!user) return &lt;Navigate to="/login" state={{ from: location }} replace /&gt;;
  return children;
}</code></pre>

<p><strong>Token storage &mdash; the security trade-off:</strong></p>

<table>
  <tr><th>Storage</th><th>XSS vulnerability</th><th>CSRF vulnerability</th><th>Use when</th></tr>
  <tr><td>localStorage</td><td>HIGH (any JS reads it)</td><td>None</td><td>Avoid for production auth tokens</td></tr>
  <tr><td>sessionStorage</td><td>HIGH</td><td>None</td><td>Same as above</td></tr>
  <tr><td>httpOnly cookie</td><td>None (JS can&rsquo;t read)</td><td>Possible — mitigate with SameSite + CSRF token</td><td>Production: best balance</td></tr>
  <tr><td>In-memory only</td><td>None</td><td>None</td><td>Lost on refresh; pair with refresh endpoint</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>Managed service vs self-hosted:</strong> Clerk/Auth0 handle the hard parts (token rotation, MFA, social, password reset, audit logs). Self-hosted gives full control and avoids vendor lock-in but you own all the security details. For most teams in 2026, managed wins.</li>
  <li><strong>JWT vs server sessions:</strong> JWTs are stateless (server doesn&rsquo;t track sessions) but can&rsquo;t be revoked instantly. Server sessions can be revoked (logout truly logs out everywhere) but require session storage. Refresh tokens bridge the gap.</li>
  <li><strong>Refresh strategy:</strong> short-lived access token (15 min) + longer refresh token (days). Auto-refresh in interceptor when API returns 401. Avoid the user being logged out mid-session.</li>
  <li><strong>SSO/Enterprise:</strong> SAML, OIDC, SCIM provisioning &mdash; managed services support these out of the box. Self-rolling is many weeks of work.</li>
</ul>

<p><strong>Critical: server-side validation is mandatory.</strong> Client-side route guards are UX, not security. Anyone can disable JS or call your API directly. Every protected endpoint must verify the session/token on the server. Never trust the client&rsquo;s claim about the current user.</p>

<p><strong>For Next.js apps:</strong> use middleware (<code>middleware.ts</code>) to protect routes at the edge before any React code runs &mdash; faster than client-side guards and harder to bypass.</p>
'''

ANSWERS[8] = r'''
<p><strong>Situation:</strong> users want light/dark theme switching with respect for OS preference, persistence across visits, no flash of wrong theme on load, and integration with all styling (Tailwind, CSS variables, component libraries). The naive implementation flashes the wrong theme on every page load &mdash; jarring UX.</p>

<p><strong>Approach:</strong> drive everything from a single CSS attribute (<code>data-theme</code> or class on <code>&lt;html&gt;</code>); use CSS variables so all styling responds; persist to localStorage; <strong>set the attribute before React hydrates</strong> via inline script in HTML head to prevent flash.</p>

<pre><code>// === Inline script in index.html (before React loads) ===
&lt;script&gt;
  (function() {
    const stored = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = stored || (prefersDark ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();
&lt;/script&gt;

// === ThemeContext ===
import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext(null);

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() =&gt;
    document.documentElement.getAttribute("data-theme") || "light"
  );

  // Sync attribute and localStorage when theme changes
  useEffect(() =&gt; {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Respect OS changes when user hasn&rsquo;t set explicit preference
  useEffect(() =&gt; {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () =&gt; {
      if (!localStorage.getItem("theme-explicit")) {
        setTheme(mq.matches ? "dark" : "light");
      }
    };
    mq.addEventListener("change", handler);
    return () =&gt; mq.removeEventListener("change", handler);
  }, []);

  const toggle = () =&gt; {
    setTheme(t =&gt; t === "light" ? "dark" : "light");
    localStorage.setItem("theme-explicit", "1");
  };

  return (
    &lt;ThemeContext.Provider value={{ theme, toggle }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

const useTheme = () =&gt; useContext(ThemeContext);</code></pre>

<pre><code>/* CSS — variables drive appearance */
:root {
  --bg: #ffffff;
  --text: #111111;
  --primary: #007bff;
  --border: #e5e7eb;
}

[data-theme="dark"] {
  --bg: #0f172a;
  --text: #f1f5f9;
  --primary: #60a5fa;
  --border: #334155;
}

body {
  background: var(--bg);
  color: var(--text);
  transition: background 200ms, color 200ms;
}</code></pre>

<p><strong>Tailwind integration</strong> (Tailwind v4):</p>

<pre><code>// tailwind.config.js
module.exports = {
  darkMode: ["class", '[data-theme="dark"]']    // sync with our attribute
};

// Components
&lt;div className="bg-white dark:bg-slate-900 text-gray-900 dark:text-gray-100"&gt;
  Content
&lt;/div&gt;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Trade-off</th></tr>
  <tr><td>CSS variables vs JS-driven styles</td><td>CSS variables: no re-render needed, instant transition, works with all frameworks. JS: more dynamic but every consumer re-renders on toggle.</td></tr>
  <tr><td>Inline script for SSR/static</td><td>Prevents flash but adds blocking script. Acceptable cost for the UX win.</td></tr>
  <tr><td>Three-state (light/dark/auto) vs two</td><td>Three respects user&rsquo;s OS choice while letting them override; better for accessibility.</td></tr>
  <tr><td>localStorage vs cookie</td><td>localStorage: client-only, simpler. Cookie: works with SSR (read on server, render correctly first paint).</td></tr>
</table>

<p><strong>Production polish:</strong></p>
<ul>
  <li><strong>Three-mode toggle</strong> (light / dark / system) is more inclusive than binary &mdash; users can match their OS while still allowing override per-app.</li>
  <li><strong>Test in both modes</strong> &mdash; Storybook&rsquo;s background addon, Chromatic, or visual regression testing across themes catches contrast bugs.</li>
  <li><strong>Color-mix() and oklch()</strong> in modern CSS make creating semantic color systems easier &mdash; define a single hue, derive shades automatically.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; transition between themes can be jarring for vestibular-sensitive users.</li>
  <li><strong>System images</strong> &mdash; SVG icons should adapt via <code>currentColor</code> or theme-aware fills. Don&rsquo;t hardcode colors in SVG.</li>
</ul>

<p><strong>Server-rendered apps</strong> (Next.js): use <code>next-themes</code> &mdash; it handles the &ldquo;no flash&rdquo; problem automatically with proper SSR support.</p>
'''

ANSWERS[9] = r'''
<p><strong>Situation:</strong> users need to upload files (images, documents, videos) with progress feedback, multiple file support, and clear error handling. The Fetch API doesn&rsquo;t support upload progress &mdash; you need <code>XMLHttpRequest</code> or <code>axios</code>. Production also needs file-type validation, size limits, drag-and-drop, and resumable uploads for large files.</p>

<p><strong>Approach:</strong> use <strong>axios</strong> for the progress callback. Validate on the client (UX) and server (security). For files &gt; 50MB, use chunked/resumable uploads via <strong>tus-js-client</strong> or platform SDKs. For images, use a service like Cloudinary/Uploadcare/UploadThing in production.</p>

<pre><code>import { useState, useRef } from "react";
import axios from "axios";

const ACCEPT = "image/png,image/jpeg,image/webp,application/pdf";
const MAX_BYTES = 10 * 1024 * 1024;   // 10 MB

function FileUploader({ onComplete }) {
  const [files, setFiles] = useState([]);
  const inputRef = useRef(null);

  const handleSelect = (selected) =&gt; {
    const valid = [];
    const errors = [];

    Array.from(selected).forEach(f =&gt; {
      if (!ACCEPT.split(",").includes(f.type)) {
        errors.push(`${f.name}: unsupported type`);
        return;
      }
      if (f.size &gt; MAX_BYTES) {
        errors.push(`${f.name}: too large (max 10MB)`);
        return;
      }
      valid.push({
        id: `${f.name}-${f.lastModified}`,
        file: f,
        progress: 0,
        status: "pending",
        error: null
      });
    });

    if (errors.length) alert(errors.join("\n"));
    setFiles(prev =&gt; [...prev, ...valid]);
  };

  const upload = async (entry) =&gt; {
    setFiles(prev =&gt; prev.map(f =&gt; f.id === entry.id ? { ...f, status: "uploading" } : f));

    const formData = new FormData();
    formData.append("file", entry.file);

    try {
      const { data } = await axios.post("/api/upload", formData, {
        onUploadProgress: (e) =&gt; {
          const progress = Math.round((e.loaded / e.total) * 100);
          setFiles(prev =&gt; prev.map(f =&gt; f.id === entry.id ? { ...f, progress } : f));
        }
      });

      setFiles(prev =&gt; prev.map(f =&gt; f.id === entry.id ? { ...f, status: "done", url: data.url } : f));
      onComplete?.(data);
    } catch (err) {
      setFiles(prev =&gt; prev.map(f =&gt; f.id === entry.id ? { ...f, status: "error", error: err.message } : f));
    }
  };

  return (
    &lt;div&gt;
      &lt;input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPT}
        onChange={e =&gt; handleSelect(e.target.files)}
      /&gt;

      {/* Drag-and-drop zone */}
      &lt;div
        onDragOver={e =&gt; e.preventDefault()}
        onDrop={e =&gt; { e.preventDefault(); handleSelect(e.dataTransfer.files); }}
        style={{ border: "2px dashed #ccc", padding: 32, textAlign: "center" }}
      &gt;
        Drop files here or &lt;button onClick={() =&gt; inputRef.current.click()}&gt;browse&lt;/button&gt;
      &lt;/div&gt;

      &lt;ul&gt;
        {files.map(f =&gt; (
          &lt;li key={f.id}&gt;
            &lt;span&gt;{f.file.name} ({(f.file.size / 1024).toFixed(0)} KB)&lt;/span&gt;
            {f.status === "pending"    &amp;&amp; &lt;button onClick={() =&gt; upload(f)}&gt;Upload&lt;/button&gt;}
            {f.status === "uploading"  &amp;&amp; &lt;ProgressBar value={f.progress} /&gt;}
            {f.status === "done"       &amp;&amp; &lt;span&gt;✓ Done&lt;/span&gt;}
            {f.status === "error"      &amp;&amp; &lt;span&gt;✗ {f.error}&lt;/span&gt;}
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Decision</th></tr>
  <tr><td>Backend storage</td><td>Direct upload to S3/R2 with pre-signed URL (fast, no proxy) vs upload to your server (validation, virus scan)</td></tr>
  <tr><td>Large files</td><td>tus.io / S3 multipart for 50MB+; resumable on connection drops</td></tr>
  <tr><td>Image-heavy app</td><td>Use a service (Cloudinary, Uploadcare, UploadThing, Vercel Blob) for resize/format/CDN automatically</td></tr>
  <tr><td>Concurrent uploads</td><td>Limit to 3-5 parallel; queue the rest. Otherwise users with slow uplinks get all uploads stuck</td></tr>
</table>

<p><strong>Production polish:</strong></p>
<ul>
  <li><strong>Server validates everything &mdash; type, size, content.</strong> Client validation is UX. Even with proper Content-Type checking, scan for malicious payloads (use a virus scanner, sandbox content rendering).</li>
  <li><strong>Pre-signed URLs</strong> let users upload directly to S3/Cloudflare R2 without proxying through your server. Faster, cheaper, no upload size limits.</li>
  <li><strong>Resumable uploads (tus protocol):</strong> for large files (videos, datasets), use <code>tus-js-client</code> &mdash; survives connection drops, resumes from where it stopped.</li>
  <li><strong>Image preview before upload:</strong> <code>URL.createObjectURL(file)</code> lets users see what they selected. Remember to <code>URL.revokeObjectURL</code> on cleanup.</li>
  <li><strong>Cancel in-flight uploads:</strong> <code>AbortController</code> with axios; clean state when user removes a file mid-upload.</li>
  <li><strong>Accessibility:</strong> visible file picker, keyboard-accessible drop zone, progress as <code>aria-valuenow</code>, status updates announced via <code>aria-live</code>.</li>
</ul>
'''

ANSWERS[10] = r'''
<p><strong>Situation:</strong> a runtime error in any component (failed render, undefined access, third-party library crash) tears down the entire React tree &mdash; users see a blank white page. Error boundaries catch render errors in their child subtree and show a fallback UI, scoping the damage and preserving the rest of the app.</p>

<p><strong>Approach:</strong> use the <strong><code>react-error-boundary</code></strong> library (cleaner API than rolling your own class component), place boundaries strategically (page-level, feature-level, around third-party widgets), report errors to <strong>Sentry</strong> in production, and ensure the boundary UI itself can&rsquo;t throw.</p>

<pre><code>// Install: npm install react-error-boundary

import { ErrorBoundary } from "react-error-boundary";
import * as Sentry from "@sentry/react";

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    &lt;div role="alert" className="error-fallback"&gt;
      &lt;h2&gt;Something went wrong&lt;/h2&gt;
      &lt;p&gt;{error.message}&lt;/p&gt;
      &lt;button onClick={resetErrorBoundary}&gt;Try again&lt;/button&gt;
    &lt;/div&gt;
  );
}

function App() {
  return (
    &lt;ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, info) =&gt; {
        Sentry.captureException(error, {
          contexts: { react: { componentStack: info.componentStack } }
        });
      }}
      onReset={() =&gt; {
        // Clear bad state if needed
      }}
    &gt;
      &lt;Layout&gt;
        &lt;Header /&gt;

        {/* Feature-scoped boundary — sidebar bug doesn&rsquo;t kill main content */}
        &lt;ErrorBoundary fallback={&lt;SidebarFallback /&gt;}&gt;
          &lt;Sidebar /&gt;
        &lt;/ErrorBoundary&gt;

        &lt;ErrorBoundary fallback={&lt;MainFallback /&gt;}&gt;
          &lt;Main /&gt;
        &lt;/ErrorBoundary&gt;
      &lt;/Layout&gt;
    &lt;/ErrorBoundary&gt;
  );
}</code></pre>

<p><strong>Strategic placement:</strong></p>

<table>
  <tr><th>Where</th><th>Why</th></tr>
  <tr><td>App root (top-level)</td><td>Last-resort safety net; replaces blank white page</td></tr>
  <tr><td>Per route / page</td><td>One broken page doesn&rsquo;t kill the rest of the app</td></tr>
  <tr><td>Per feature widget</td><td>Sidebar/footer/sidebar widget can fail independently</td></tr>
  <tr><td>Around third-party components</td><td>Buggy chart library or embed doesn&rsquo;t crash your app</td></tr>
  <tr><td>Around dynamically loaded sections</td><td>Pair with <code>Suspense</code> for full async-failure handling</td></tr>
</table>

<p><strong>Critical &mdash; what error boundaries DON&rsquo;T catch:</strong></p>
<ul>
  <li><strong>Event handlers</strong> (use <code>try/catch</code> in handlers).</li>
  <li><strong>Async code</strong> (<code>setTimeout</code>, promises &mdash; use <code>.catch</code> or try/catch with await).</li>
  <li><strong>Server-side rendering errors</strong> (boundary only catches on client).</li>
  <li><strong>Errors in the boundary itself</strong> (would cause infinite loop &mdash; React unmounts the boundary).</li>
</ul>

<p><strong>For these gaps:</strong></p>

<pre><code>// Async errors caught manually, then bubbled to nearest boundary via state
import { useErrorBoundary } from "react-error-boundary";

function DataLoader() {
  const { showBoundary } = useErrorBoundary();

  useEffect(() =&gt; {
    fetchData().catch(showBoundary);   // route error to boundary fallback
  }, []);
}

// Global handlers for uncaught
window.addEventListener("unhandledrejection", (e) =&gt; Sentry.captureException(e.reason));
window.addEventListener("error", (e) =&gt; Sentry.captureException(e.error));</code></pre>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>Granularity:</strong> too few boundaries = whole app crashes; too many = unfocused fallbacks. Aim for "isolate features that can fail independently."</li>
  <li><strong>Reset strategy:</strong> <code>resetErrorBoundary</code> re-renders the children; if state is corrupt, the same error happens immediately. Use <code>resetKeys</code> to force unmount/remount when an external value changes (e.g., URL).</li>
  <li><strong>Fallback UX:</strong> generic "something went wrong" is fine for unexpected bugs; specific "We couldn&rsquo;t load your dashboard &mdash; try again" is better when you know what failed. Always offer a recovery path.</li>
  <li><strong>Don&rsquo;t hide the error:</strong> in development, show the stack trace. In production, hide details (security) but tell the user something useful and have detailed logs in Sentry.</li>
</ul>

<p><strong>For Suspense + error combinations</strong> (data loading): wrap with <code>ErrorBoundary</code> outside <code>Suspense</code> &mdash; loading states inside, errors outside. The pattern handles "loading," "error," and "success" cleanly with no manual state.</p>
'''

ANSWERS[11] = r'''
<p><strong>Situation:</strong> a navigation menu must work across mobile (hamburger toggle, drawer or full-screen overlay), tablet (collapsed or full), and desktop (full inline menu). It needs keyboard navigation, focus trapping when open on mobile, click-outside-to-close, escape-to-close, and active-route highlighting. Accessibility-first design is essential &mdash; navigation is the most-used element on every page.</p>

<p><strong>Approach:</strong> CSS-driven layout for the breakpoint behavior (don&rsquo;t use JS to detect screen size); React state for the mobile open/close; <code>NavLink</code> for active styling; focus trap when mobile menu is open.</p>

<pre><code>import { useState, useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";

const NAV = [
  { to: "/",         label: "Home" },
  { to: "/products", label: "Products" },
  { to: "/pricing",  label: "Pricing" },
  { to: "/about",    label: "About" },
  { to: "/contact",  label: "Contact" }
];

function Nav() {
  const [open, setOpen] = useState(false);
  const navRef = useRef(null);

  // Close on Escape
  useEffect(() =&gt; {
    if (!open) return;
    const handleKey = (e) =&gt; e.key === "Escape" &amp;&amp; setOpen(false);
    document.addEventListener("keydown", handleKey);
    return () =&gt; document.removeEventListener("keydown", handleKey);
  }, [open]);

  // Lock body scroll when mobile drawer open
  useEffect(() =&gt; {
    document.body.style.overflow = open ? "hidden" : "";
    return () =&gt; { document.body.style.overflow = ""; };
  }, [open]);

  return (
    &lt;nav ref={navRef} className="nav"&gt;
      &lt;a href="/" className="nav__logo"&gt;Logo&lt;/a&gt;

      &lt;button
        className="nav__hamburger"
        onClick={() =&gt; setOpen(o =&gt; !o)}
        aria-expanded={open}
        aria-controls="main-menu"
        aria-label={open ? "Close menu" : "Open menu"}
      &gt;
        {open ? "✕" : "☰"}
      &lt;/button&gt;

      &lt;ul id="main-menu" className={open ? "nav__list nav__list--open" : "nav__list"}&gt;
        {NAV.map(item =&gt; (
          &lt;li key={item.to}&gt;
            &lt;NavLink
              to={item.to}
              end={item.to === "/"}
              onClick={() =&gt; setOpen(false)}
              className={({ isActive }) =&gt; isActive ? "nav__link nav__link--active" : "nav__link"}
            &gt;
              {item.label}
            &lt;/NavLink&gt;
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;

      {/* Backdrop for mobile drawer */}
      {open &amp;&amp; &lt;div className="nav__backdrop" onClick={() =&gt; setOpen(false)} /&gt;}
    &lt;/nav&gt;
  );
}</code></pre>

<pre><code>/* CSS — drives behavior per breakpoint */
.nav { display: flex; align-items: center; padding: 12px 24px; }
.nav__list { display: flex; gap: 24px; list-style: none; }
.nav__hamburger { display: none; }
.nav__link { color: inherit; text-decoration: none; }
.nav__link--active { color: var(--primary); font-weight: 600; }

@media (max-width: 768px) {
  .nav__hamburger { display: block; background: none; border: none; font-size: 24px; }

  .nav__list {
    position: fixed;
    top: 60px; left: 0; right: 0; bottom: 0;
    flex-direction: column;
    background: var(--bg);
    padding: 24px;
    transform: translateX(-100%);
    transition: transform 250ms ease;
    z-index: 100;
  }

  .nav__list--open { transform: translateX(0); }

  .nav__backdrop {
    position: fixed; inset: 60px 0 0 0;
    background: rgba(0,0,0,0.4);
    z-index: 99;
  }
}</code></pre>

<p><strong>Accessibility checklist:</strong></p>

<table>
  <tr><th>Concern</th><th>Implementation</th></tr>
  <tr><td>Keyboard navigation</td><td>Tab through links works automatically with <code>&lt;a&gt;</code> tags</td></tr>
  <tr><td>Hamburger button is a real button</td><td><code>&lt;button&gt;</code> not <code>&lt;div onClick&gt;</code></td></tr>
  <tr><td>Active state communicated to screen readers</td><td><code>aria-current="page"</code> via NavLink (auto)</td></tr>
  <tr><td>Open/close state announced</td><td><code>aria-expanded</code>, <code>aria-controls</code></td></tr>
  <tr><td>Focus trap on mobile drawer</td><td>For deep accessibility, use <code>focus-trap-react</code> library</td></tr>
  <tr><td>Escape closes</td><td>Document-level keydown listener</td></tr>
  <tr><td>Click outside closes</td><td>Backdrop click handler</td></tr>
  <tr><td>Body scroll locked when drawer open</td><td>Set <code>overflow: hidden</code> on body</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>CSS breakpoints vs JS detection:</strong> CSS is faster, declarative, and works without JS. <code>matchMedia</code> in JS is sometimes useful for behavioral changes (e.g., disable mobile-only features) but layout should be CSS-driven.</li>
  <li><strong>Drawer vs full-screen mobile menu:</strong> drawer is more familiar; full-screen gives more space but feels heavier.</li>
  <li><strong>Sticky/transparent header:</strong> trade-offs with content scrolling underneath; backdrop-filter for "glassmorphism" is popular but consumes performance.</li>
  <li><strong>Use a library for production:</strong> <strong>Radix Navigation Menu</strong> or <strong>shadcn/ui Sheet</strong> handle focus management, animations, sub-menus, ARIA &mdash; covering edge cases that hand-rolled menus often miss.</li>
</ul>
'''

ANSWERS[12] = r'''
<p><strong>Situation:</strong> a dashboard or analytics page needs charts &mdash; bar, line, pie, scatter, geo. Native SVG is too low-level for most cases. Library choice involves trade-offs: declarative React API vs imperative D3, bundle size, customization depth, server rendering, and animation support.</p>

<p><strong>Approach:</strong> for most React projects in 2026, <strong>Recharts</strong> is the sweet spot &mdash; declarative React components, responsive, built on D3. For full design control or scientific visualization, drop down to <strong>visx</strong> (React + D3 wrappers) or raw <strong>D3</strong>. <strong>Chart.js + react-chartjs-2</strong> is canvas-based (faster for huge datasets); <strong>Tremor</strong> and <strong>Nivo</strong> offer beautiful defaults.</p>

<pre><code>// === Recharts — declarative React API ===
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";

function RevenueDashboard({ data }) {
  return (
    &lt;div style={{ width: "100%", height: 400 }}&gt;
      &lt;ResponsiveContainer&gt;
        &lt;LineChart data={data}&gt;
          &lt;CartesianGrid strokeDasharray="3 3" stroke="#eee" /&gt;
          &lt;XAxis dataKey="month" /&gt;
          &lt;YAxis tickFormatter={(v) =&gt; `$${(v / 1000).toFixed(0)}k`} /&gt;
          &lt;Tooltip
            formatter={(v) =&gt; `$${v.toLocaleString()}`}
            labelStyle={{ color: "#333" }}
          /&gt;
          &lt;Legend /&gt;
          &lt;Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} /&gt;
          &lt;Line type="monotone" dataKey="costs" stroke="#ef4444" strokeWidth={2} /&gt;
        &lt;/LineChart&gt;
      &lt;/ResponsiveContainer&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>For full custom design &mdash; D3 inside React (the right way):</strong></p>

<pre><code>import { useEffect, useRef } from "react";
import * as d3 from "d3";

function CustomChart({ data }) {
  const svgRef = useRef(null);

  useEffect(() =&gt; {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();   // clear on re-render

    const width = 600, height = 400, margin = 40;

    const x = d3.scaleBand()
      .domain(data.map(d =&gt; d.label))
      .range([margin, width - margin])
      .padding(0.1);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d =&gt; d.value)])
      .range([height - margin, margin]);

    svg.selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", d =&gt; x(d.label))
      .attr("y", d =&gt; y(d.value))
      .attr("width", x.bandwidth())
      .attr("height", d =&gt; height - margin - y(d.value))
      .attr("fill", "#3b82f6");

    // Axes
    svg.append("g")
      .attr("transform", `translate(0,${height - margin})`)
      .call(d3.axisBottom(x));

    svg.append("g")
      .attr("transform", `translate(${margin},0)`)
      .call(d3.axisLeft(y));
  }, [data]);

  return &lt;svg ref={svgRef} width={600} height={400} /&gt;;
}</code></pre>

<p><strong>Key principle: let React own the DOM where possible, let D3 do the math.</strong> The pattern above gives D3 control of the SVG, but React owns rendering it. For more React-idiomatic D3, use <strong>visx</strong> (D3 utilities wrapped in React components).</p>

<p><strong>Library comparison (2026):</strong></p>

<table>
  <tr><th>Library</th><th>Strengths</th><th>Weaknesses</th></tr>
  <tr><td>Recharts</td><td>Declarative, easy, responsive, good defaults</td><td>Limited extreme customization; SVG-only</td></tr>
  <tr><td>Nivo</td><td>Beautiful defaults; many chart types</td><td>Larger bundle</td></tr>
  <tr><td>Chart.js + react-chartjs-2</td><td>Canvas (fast for big data); familiar API</td><td>Less React-idiomatic</td></tr>
  <tr><td>visx</td><td>D3 power + React composability</td><td>More code; lower-level</td></tr>
  <tr><td>Tremor</td><td>Tailwind-styled, dashboard-focused</td><td>Tightly coupled to Tailwind</td></tr>
  <tr><td>Plotly.js</td><td>Scientific charts (3D, contour, etc.)</td><td>Heavy bundle (~3MB)</td></tr>
  <tr><td>D3 directly</td><td>Total control; vast capability</td><td>Steep learning curve; manual</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>SVG vs Canvas:</strong> SVG is good up to ~10k points; canvas wins beyond that. SVG is accessible by default; canvas requires manual ARIA and a hidden table for screen readers.</li>
  <li><strong>Data shape:</strong> most libraries expect <code>[{ x, y }, ...]</code>. Pre-process your data once before passing to the chart &mdash; don&rsquo;t reshape on every render.</li>
  <li><strong>Animations</strong>: defaults are subtle in Recharts. For heavy animation, Framer Motion overlays or D3 transitions work better.</li>
  <li><strong>SSR:</strong> Recharts and Chart.js require client-only rendering (use <code>ssr: false</code> in Next.js dynamic imports). visx supports SSR.</li>
  <li><strong>Accessibility:</strong> all charts need a <strong>data table fallback</strong> or text alternative for screen readers. SVG charts can include <code>&lt;title&gt;</code> and <code>&lt;desc&gt;</code> elements; data tables are most accessible.</li>
</ul>
'''

ANSWERS[13] = r'''
<p><strong>Situation:</strong> a React app needs SSR (or SSG) for: SEO (search engines see real content), faster first paint, social media link previews, and improved Core Web Vitals. Roll-your-own SSR is months of work; for production, use <strong>Next.js</strong>, <strong>Remix</strong>, or <strong>TanStack Start</strong> rather than building custom infrastructure on Vite/Webpack.</p>

<p><strong>Approach for new projects in 2026:</strong> Next.js App Router with React Server Components (default rendering on server), opting into client components only for interactivity. Streaming rendering with Suspense delivers HTML progressively.</p>

<pre><code>// Next.js App Router — default Server Component
// app/products/[id]/page.tsx
async function ProductPage({ params }: { params: { id: string } }) {
  // Runs on server — no client-side fetch needed
  const product = await fetch(`https://api.example.com/products/${params.id}`, {
    next: { revalidate: 60 }   // cache for 60 seconds (ISR)
  }).then(r =&gt; r.json());

  return (
    &lt;article&gt;
      &lt;h1&gt;{product.name}&lt;/h1&gt;
      &lt;p&gt;${product.price}&lt;/p&gt;
      &lt;p&gt;{product.description}&lt;/p&gt;

      {/* Client component — only this part is interactive */}
      &lt;AddToCartButton productId={product.id} /&gt;
    &lt;/article&gt;
  );
}

// Generate metadata for SEO and social
export async function generateMetadata({ params }) {
  const product = await fetch(`https://api/products/${params.id}`).then(r =&gt; r.json());
  return {
    title: `${product.name} | Store`,
    description: product.description,
    openGraph: {
      images: [product.imageUrl]
    }
  };
}

export default ProductPage;</code></pre>

<pre><code>// app/products/[id]/AddToCartButton.tsx
"use client";   // marks as Client Component
import { useState } from "react";

export function AddToCartButton({ productId }) {
  const [adding, setAdding] = useState(false);

  return (
    &lt;button onClick={() =&gt; setAdding(true)} disabled={adding}&gt;
      {adding ? "Adding..." : "Add to cart"}
    &lt;/button&gt;
  );
}</code></pre>

<p><strong>Rendering strategy options in Next.js:</strong></p>

<table>
  <tr><th>Strategy</th><th>When data fetches</th><th>Use for</th></tr>
  <tr><td>SSG (static)</td><td>At build time</td><td>Marketing, blog, docs &mdash; rarely changes</td></tr>
  <tr><td>ISR (incremental)</td><td>Revalidate periodically</td><td>Mostly-static with infrequent changes</td></tr>
  <tr><td>SSR (per request)</td><td>On each request</td><td>User-specific dashboards, personalized content</td></tr>
  <tr><td>Streaming (Suspense)</td><td>Progressively as ready</td><td>Pages with mix of fast and slow data</td></tr>
  <tr><td>CSR (client-side)</td><td>After hydration</td><td>Truly interactive parts; private dashboards</td></tr>
</table>

<p><strong>Hydration &mdash; the bridge between server HTML and client interactivity:</strong></p>
<ol>
  <li>Server renders complete HTML; sends to browser.</li>
  <li>Browser displays HTML immediately (fast first paint).</li>
  <li>JavaScript bundle downloads in parallel.</li>
  <li>React "hydrates" the existing DOM &mdash; attaches event listeners without re-rendering.</li>
  <li>App becomes interactive.</li>
</ol>

<p><strong>Trade-offs and gotchas:</strong></p>

<table>
  <tr><th>Concern</th><th>Detail</th></tr>
  <tr><td>Hydration mismatches</td><td>Server HTML must match initial client render exactly. <code>Date.now()</code>, <code>Math.random()</code>, browser APIs differ &mdash; gate them with <code>useEffect</code>.</td></tr>
  <tr><td>Bundle size still matters</td><td>SSR sends HTML fast, but JS still must hydrate. Code split aggressively.</td></tr>
  <tr><td>No DOM on server</td><td><code>window</code>, <code>document</code>, <code>localStorage</code> don&rsquo;t exist. Use <code>useEffect</code> for browser-only code.</td></tr>
  <tr><td>Server bandwidth/CPU</td><td>SSR uses server resources per request. Cache aggressively; use ISR or CDN.</td></tr>
  <tr><td>Slower deploys (build time)</td><td>SSG with thousands of pages builds slowly. ISR fixes this by deferring to first request.</td></tr>
</table>

<p><strong>For non-Next.js apps:</strong></p>
<ul>
  <li><strong>Remix:</strong> different philosophy &mdash; web fundamentals, nested routes with loaders/actions, no React Server Components yet.</li>
  <li><strong>TanStack Start:</strong> newer, type-safe, file-based routing, full SSR/SSG support; great for SPAs that need SEO.</li>
  <li><strong>Astro:</strong> for content-heavy sites with islands of React interactivity. Ships almost zero JS by default.</li>
  <li><strong>Vite SSR:</strong> roll your own with Vite&rsquo;s SSR APIs &mdash; only justified if you have unusual requirements that frameworks don&rsquo;t fit.</li>
</ul>

<p><strong>For 95% of React apps in 2026 needing SSR, Next.js is the answer.</strong> The framework absorbs the complexity (build, deploy, caching, streaming, image optimization) so you can focus on product code.</p>
'''

ANSWERS[14] = r'''
<p><strong>Situation:</strong> users want to "Sign in with Google" or "Sign in with GitHub" instead of yet another username/password. Implementing OAuth from scratch involves PKCE, state parameter verification, token rotation, account linking, and security pitfalls that take months to get right. Modern services solve this in an afternoon.</p>

<p><strong>Approach for 2026:</strong> use a managed auth provider &mdash; <strong>Clerk</strong>, <strong>Supabase Auth</strong>, <strong>Firebase Auth</strong>, <strong>Auth0</strong>, or <strong>NextAuth.js</strong>. Each handles social provider integration, session management, account linking, and security audits. Self-rolling is rarely justified.</p>

<pre><code>// === Approach 1: Clerk (most popular for new React apps in 2026) ===
// Install: npm install @clerk/clerk-react

import { ClerkProvider, SignInButton, UserButton, useUser } from "@clerk/clerk-react";

function Root() {
  return (
    &lt;ClerkProvider publishableKey={import.meta.env.VITE_CLERK_KEY}&gt;
      &lt;App /&gt;
    &lt;/ClerkProvider&gt;
  );
}

function Header() {
  const { isSignedIn, user } = useUser();
  return (
    &lt;header&gt;
      &lt;h1&gt;My App&lt;/h1&gt;
      {isSignedIn ? (
        &lt;&gt;
          &lt;span&gt;Hi, {user.firstName}&lt;/span&gt;
          &lt;UserButton /&gt;     {/* Clerk-rendered profile menu */}
        &lt;/&gt;
      ) : (
        &lt;SignInButton mode="modal"&gt;
          &lt;button&gt;Sign in&lt;/button&gt;
        &lt;/SignInButton&gt;
      )}
    &lt;/header&gt;
  );
}

// Calling APIs with Clerk session token
import { useAuth } from "@clerk/clerk-react";

function useAuthenticatedFetch() {
  const { getToken } = useAuth();
  return async (url, options = {}) =&gt; {
    const token = await getToken();
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`
      }
    });
  };
}</code></pre>

<p><strong>Approach 2: Firebase Auth (great for Firebase ecosystem):</strong></p>

<pre><code>import { initializeApp } from "firebase/app";
import {
  getAuth, GoogleAuthProvider, GithubAuthProvider,
  signInWithPopup, signOut, onAuthStateChanged
} from "firebase/auth";

const auth = getAuth(initializeApp({ /* config */ }));

const signInWithGoogle = () =&gt; signInWithPopup(auth, new GoogleAuthProvider());
const signInWithGithub = () =&gt; signInWithPopup(auth, new GithubAuthProvider());

function AuthListener() {
  useEffect(() =&gt; onAuthStateChanged(auth, setUser), []);
}</code></pre>

<p><strong>The OAuth flow (under the hood):</strong></p>
<ol>
  <li>User clicks "Sign in with Google."</li>
  <li>App redirects to Google&rsquo;s OAuth consent page (with state + PKCE code verifier).</li>
  <li>User approves; Google redirects back to your app with auth code.</li>
  <li>App exchanges code for ID token (verifies state matches; verifies PKCE).</li>
  <li>App receives signed JWT with user info; signs the user in.</li>
</ol>

<p><strong>Provider comparison (2026):</strong></p>

<table>
  <tr><th>Service</th><th>Best for</th><th>Pricing model</th></tr>
  <tr><td>Clerk</td><td>Modern apps; excellent UX out of the box; pre-built UI components</td><td>Free tier 10k MAU; paid scales</td></tr>
  <tr><td>Supabase Auth</td><td>Open-source; pairs with Postgres; self-hostable</td><td>Free tier; pay-as-you-go</td></tr>
  <tr><td>Auth0</td><td>Enterprise (SAML, SCIM, regulated industries)</td><td>Expensive at scale</td></tr>
  <tr><td>Firebase Auth</td><td>Google ecosystem; quick prototypes</td><td>Free + Google Cloud-style billing</td></tr>
  <tr><td>NextAuth.js / Auth.js</td><td>Self-hosted; Next.js apps; full control</td><td>Free (you host)</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>Managed vs self-hosted:</strong> managed handles MFA, password resets, audit logs, compliance. Self-hosted is cheaper at scale but you own all the security details.</li>
  <li><strong>Account linking:</strong> users sign up via Google, then later try email/password &mdash; should they merge or stay separate? Most providers handle this, but the UX needs design.</li>
  <li><strong>Vendor lock-in:</strong> migration between providers is painful. Mitigate by abstracting auth calls behind your own interface; keep user IDs stable; export user data periodically.</li>
  <li><strong>Token storage:</strong> Clerk uses httpOnly cookies (XSS-safe). Firebase uses localStorage (XSS-vulnerable). Match your security posture.</li>
  <li><strong>OAuth callback URLs</strong> must be configured per-environment (dev, staging, prod). Wildcard URLs are forbidden by most providers; production app must register exact URLs.</li>
</ul>

<p><strong>Critical security &mdash; never trust client claims about identity.</strong> Server-side, verify the JWT signature using the provider&rsquo;s public keys. Don&rsquo;t use unverified token contents for authorization. Rate-limit auth endpoints to prevent abuse. Log sign-ins for audit and anomaly detection.</p>
'''

ANSWERS[15] = r'''
<p><strong>Situation:</strong> the app needs modal dialogs throughout &mdash; confirmation prompts, forms, image lightboxes, settings panels. A reusable modal component should: render via portal (escape parent CSS constraints), trap focus when open, close on Escape, lock body scroll, restore focus to the trigger when closed, and meet ARIA dialog requirements.</p>

<p><strong>Approach:</strong> for production, <strong>don&rsquo;t roll your own.</strong> Use <strong>Radix Dialog</strong>, <strong>shadcn/ui Dialog</strong>, <strong>Headless UI Dialog</strong>, or the native <strong><code>&lt;dialog&gt;</code></strong> element with <code>showModal()</code>. Hand-rolled modals frequently miss focus management or accessibility details. Below is a roll-your-own for understanding, plus the production recommendation.</p>

<pre><code>import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";

function Modal({ isOpen, onClose, title, children }) {
  const dialogRef = useRef(null);
  const previousFocusRef = useRef(null);

  useEffect(() =&gt; {
    if (!isOpen) return;

    // Save previous focus; restore on close
    previousFocusRef.current = document.activeElement;

    // Lock body scroll
    document.body.style.overflow = "hidden";

    // Focus first focusable element in dialog
    setTimeout(() =&gt; {
      const focusable = dialogRef.current?.querySelector(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      focusable?.focus();
    }, 0);

    // Escape key to close
    const handleKey = (e) =&gt; {
      if (e.key === "Escape") onClose();

      // Focus trap: cycle within dialog
      if (e.key === "Tab" &amp;&amp; dialogRef.current) {
        const focusables = dialogRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const first = focusables[0];
        const last = focusables[focusables.length - 1];

        if (e.shiftKey &amp;&amp; document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey &amp;&amp; document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener("keydown", handleKey);

    return () =&gt; {
      document.removeEventListener("keydown", handleKey);
      document.body.style.overflow = "";
      previousFocusRef.current?.focus();   // restore focus
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    &lt;div className="modal-overlay" onClick={onClose}&gt;
      &lt;div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="modal-content"
        onClick={e =&gt; e.stopPropagation()}
      &gt;
        &lt;header&gt;
          &lt;h2 id="modal-title"&gt;{title}&lt;/h2&gt;
          &lt;button onClick={onClose} aria-label="Close"&gt;✕&lt;/button&gt;
        &lt;/header&gt;
        &lt;div className="modal-body"&gt;{children}&lt;/div&gt;
      &lt;/div&gt;
    &lt;/div&gt;,
    document.body
  );
}</code></pre>

<p><strong>Production recommendation &mdash; Radix Dialog:</strong></p>

<pre><code>// Install: npm install @radix-ui/react-dialog
import * as Dialog from "@radix-ui/react-dialog";

function ConfirmDialog({ open, onOpenChange, onConfirm }) {
  return (
    &lt;Dialog.Root open={open} onOpenChange={onOpenChange}&gt;
      &lt;Dialog.Portal&gt;
        &lt;Dialog.Overlay className="overlay" /&gt;
        &lt;Dialog.Content className="dialog"&gt;
          &lt;Dialog.Title&gt;Are you sure?&lt;/Dialog.Title&gt;
          &lt;Dialog.Description&gt;This action cannot be undone.&lt;/Dialog.Description&gt;

          &lt;div className="actions"&gt;
            &lt;Dialog.Close asChild&gt;
              &lt;button&gt;Cancel&lt;/button&gt;
            &lt;/Dialog.Close&gt;
            &lt;button onClick={onConfirm}&gt;Confirm&lt;/button&gt;
          &lt;/div&gt;
        &lt;/Dialog.Content&gt;
      &lt;/Dialog.Portal&gt;
    &lt;/Dialog.Root&gt;
  );
}</code></pre>

<p>All accessibility &mdash; focus management, ARIA, scroll lock, keyboard handling &mdash; is built in. Style it with CSS or Tailwind.</p>

<p><strong>Native <code>&lt;dialog&gt;</code> element (modern, browser-native)</strong>:</p>

<pre><code>function NativeModal({ open }) {
  const ref = useRef(null);
  useEffect(() =&gt; {
    if (open) ref.current?.showModal();
    else ref.current?.close();
  }, [open]);

  return (
    &lt;dialog ref={ref}&gt;
      &lt;form method="dialog"&gt;     {/* form with method="dialog" closes on submit */}
        &lt;p&gt;Confirm action?&lt;/p&gt;
        &lt;button value="confirm"&gt;Yes&lt;/button&gt;
        &lt;button value="cancel"&gt;No&lt;/button&gt;
      &lt;/form&gt;
    &lt;/dialog&gt;
  );
}</code></pre>

<p>Browser handles focus, Escape, top-layer rendering. Universal support since 2022.</p>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>Roll-your-own</td><td>Total control; no dependency</td><td>Easy to miss accessibility details</td></tr>
  <tr><td>Radix / shadcn/ui</td><td>Production-quality a11y; styleable</td><td>~10KB dependency</td></tr>
  <tr><td>Native <code>&lt;dialog&gt;</code></td><td>Zero JS for behavior; best a11y</td><td>Limited animation/styling control vs custom</td></tr>
  <tr><td>React Aria</td><td>Adobe&rsquo;s a11y-first hooks; very flexible</td><td>More verbose; requires composition</td></tr>
</table>

<p><strong>Common pitfalls in roll-your-own:</strong> not trapping focus (Tab escapes the modal), not restoring focus on close (jumps to top of page), missing ARIA roles, scroll bar shifts, multiple modals stacking. Libraries solve all of these.</p>
'''

ANSWERS[16] = r'''
<p><strong>Situation:</strong> a deeply nested component tree needs to share state &mdash; e.g., a settings dropdown 5 levels deep needs to update theme; a "sidebar collapse" state in the layout affects components 4 levels down; a notification toast triggered from a leaf component must appear at the app root. Passing props through every intermediate level (prop drilling) becomes painful and tightly couples components.</p>

<p><strong>Approach:</strong> the right tool depends on the relationship and update frequency. Common solutions: <strong>Context</strong> for tree-scoped values, <strong>composition (children prop)</strong> to flatten trees, <strong>Zustand</strong> for cross-feature global state, and <strong>event-based pub/sub</strong> for decoupled cross-tree communication.</p>

<pre><code>// === Pattern 1: Context for tree-scoped state ===
const SidebarContext = createContext(null);

function Layout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  return (
    &lt;SidebarContext.Provider value={{ collapsed, setCollapsed }}&gt;
      {children}
    &lt;/SidebarContext.Provider&gt;
  );
}

// 5 levels deep — no prop drilling needed
function DeepNestedToggle() {
  const { collapsed, setCollapsed } = useContext(SidebarContext);
  return &lt;button onClick={() =&gt; setCollapsed(c =&gt; !c)}&gt;{collapsed ? "Expand" : "Collapse"}&lt;/button&gt;;
}

// === Pattern 2: Composition flattens trees ===
// Instead of:
&lt;Layout user={user} theme={theme} cart={cart}&gt;
  &lt;Sidebar user={user} theme={theme} /&gt;
  &lt;Main user={user} cart={cart} /&gt;
&lt;/Layout&gt;

// Compose with children — no need to thread props through Layout:
&lt;Layout&gt;
  &lt;Sidebar /&gt;     {/* Reads its own context for user, theme */}
  &lt;Main /&gt;        {/* Reads its own context for user, cart */}
&lt;/Layout&gt;

// === Pattern 3: Zustand for cross-feature global state ===
import { create } from "zustand";

const useNotificationStore = create((set) =&gt; ({
  notifications: [],
  notify: (msg, type = "info") =&gt; set((s) =&gt; ({
    notifications: [...s.notifications, { id: Date.now(), msg, type }]
  })),
  dismiss: (id) =&gt; set((s) =&gt; ({
    notifications: s.notifications.filter(n =&gt; n.id !== id)
  }))
}));

// Trigger from anywhere in the tree:
function DeleteButton({ item }) {
  const notify = useNotificationStore(s =&gt; s.notify);
  const handleDelete = async () =&gt; {
    await api.delete(item.id);
    notify("Item deleted", "success");   // appears in NotificationToast at app root
  };
  return &lt;button onClick={handleDelete}&gt;Delete&lt;/button&gt;;
}

// Listen at app root:
function NotificationToast() {
  const notifications = useNotificationStore(s =&gt; s.notifications);
  return notifications.map(n =&gt; &lt;Toast key={n.id} {...n} /&gt;);
}</code></pre>

<p><strong>Decision matrix:</strong></p>

<table>
  <tr><th>Communication need</th><th>Best tool</th></tr>
  <tr><td>Parent &rarr; child (one level)</td><td>Props</td></tr>
  <tr><td>Parent &rarr; deep descendant</td><td>Context (tree-scoped) or composition</td></tr>
  <tr><td>Sibling &harr; sibling</td><td>Lift state to parent (or Context)</td></tr>
  <tr><td>Distant cousins (different subtrees)</td><td>Zustand / Jotai / Redux</td></tr>
  <tr><td>One-shot events (notifications, errors)</td><td>Zustand store + listener at root</td></tr>
  <tr><td>Server data shared across components</td><td>TanStack Query (cache deduplicates)</td></tr>
  <tr><td>URL state shared across pages</td><td>Router search params</td></tr>
</table>

<p><strong>Composition &mdash; the most underused pattern:</strong> instead of threading props through wrapper components, accept <code>children</code> and let the consumer place children where they need data. Many "context vs Redux" debates dissolve when you realize composition was the right answer.</p>

<pre><code>// PROBLEM: Layout doesn&rsquo;t need user, but threads it through to Header
function Layout({ user, children }) {
  return (
    &lt;div&gt;
      &lt;Header user={user} /&gt;
      &lt;main&gt;{children}&lt;/main&gt;
    &lt;/div&gt;
  );
}

// SOLUTION: Layout takes Header as a slot; consumer provides Header with user
function Layout({ header, children }) {
  return (
    &lt;div&gt;
      {header}
      &lt;main&gt;{children}&lt;/main&gt;
    &lt;/div&gt;
  );
}

// Usage
&lt;Layout header={&lt;Header user={user} /&gt;}&gt;...&lt;/Layout&gt;</code></pre>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>Context performance:</strong> all consumers re-render on any context value change. Split into multiple contexts (theme, auth, locale) so unrelated components don&rsquo;t re-render together. For high-frequency state, use Zustand &mdash; selective subscriptions skip re-renders.</li>
  <li><strong>Avoid Redux as a prop-drilling cure</strong>: Redux solves complex state, not "I need to share a value." Reach for Context first; only graduate to Redux/Zustand when state has cross-cutting complexity.</li>
  <li><strong>Custom events / pub-sub:</strong> rarely needed in React. The framework&rsquo;s data flow handles 99% of cases. Custom events are useful for cross-iframe or cross-window messaging, but not within a single React tree.</li>
</ul>
'''

ANSWERS[17] = r'''
<p><strong>Situation:</strong> light/dark theme switching across the app, with values (colors, spacing) accessible to any component. Themes can extend beyond colors &mdash; spacing scales, typography, border radii. The ThemeProvider pattern via Context keeps the implementation decoupled from any styling library.</p>

<p><strong>Approach:</strong> Context provider wraps the app; theme value is a JS object describing the design tokens; persistent via localStorage; CSS variables drive actual styles (so even non-React parts respond). Pair with a theming-aware UI library (Tailwind dark mode, MUI ThemeProvider, etc.) for full integration.</p>

<pre><code>import { createContext, useContext, useState, useEffect } from "react";

// === Theme tokens — single source of truth ===
const lightTheme = {
  name: "light",
  colors: {
    bg: "#ffffff",
    text: "#111111",
    primary: "#3b82f6",
    border: "#e5e7eb",
    muted: "#6b7280"
  },
  spacing: { xs: "4px", sm: "8px", md: "16px", lg: "24px", xl: "32px" },
  radius: { sm: "4px", md: "8px", lg: "12px" },
  shadow: {
    sm: "0 1px 2px rgba(0,0,0,0.05)",
    md: "0 4px 6px rgba(0,0,0,0.1)"
  }
};

const darkTheme = {
  ...lightTheme,
  name: "dark",
  colors: {
    bg: "#0f172a",
    text: "#f1f5f9",
    primary: "#60a5fa",
    border: "#334155",
    muted: "#94a3b8"
  }
};

const themes = { light: lightTheme, dark: darkTheme };

// === ThemeContext ===
const ThemeContext = createContext(null);

function ThemeProvider({ children }) {
  const [themeName, setThemeName] = useState(() =&gt; {
    const stored = localStorage.getItem("theme");
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  const theme = themes[themeName];

  // Sync to CSS variables and localStorage
  useEffect(() =&gt; {
    const root = document.documentElement;
    Object.entries(theme.colors).forEach(([k, v]) =&gt; root.style.setProperty(`--color-${k}`, v));
    Object.entries(theme.spacing).forEach(([k, v]) =&gt; root.style.setProperty(`--space-${k}`, v));
    root.setAttribute("data-theme", themeName);
    localStorage.setItem("theme", themeName);
  }, [theme, themeName]);

  const toggle = () =&gt; setThemeName(t =&gt; t === "light" ? "dark" : "light");

  return (
    &lt;ThemeContext.Provider value={{ theme, themeName, toggle }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

const useTheme = () =&gt; useContext(ThemeContext);

// === Component using the theme ===
function Card({ children }) {
  const { theme } = useTheme();
  return (
    &lt;div style={{
      background: theme.colors.bg,
      color: theme.colors.text,
      padding: theme.spacing.md,
      borderRadius: theme.radius.md,
      boxShadow: theme.shadow.md
    }}&gt;
      {children}
    &lt;/div&gt;
  );
}

// Or use CSS variables (preferred — works without JS in component)
// .card { background: var(--color-bg); padding: var(--space-md); }</code></pre>

<p><strong>Why CSS variables matter</strong>: components reference <code>var(--color-bg)</code>; the variable is set globally by the provider. Changing themes is a single CSS variable update, no component re-renders required. Works seamlessly with Tailwind, CSS Modules, or plain CSS.</p>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Trade-off</th></tr>
  <tr><td>JS theme object only</td><td>Components access via <code>useTheme()</code>. Re-renders on theme change. Strong typing.</td></tr>
  <tr><td>CSS variables only</td><td>No re-renders. Works without React. Less type-safe.</td></tr>
  <tr><td>Both (JS object + CSS variables)</td><td>Best of both: type-safe access from JS, performant CSS. <strong>Recommended.</strong></td></tr>
  <tr><td>Tailwind&rsquo;s <code>dark:</code> prefix</td><td>Class-based; integrates if Tailwind is your styling.</td></tr>
</table>

<p><strong>Production polish:</strong></p>
<ul>
  <li><strong>Three modes (light / dark / system):</strong> system follows OS; explicit picks override. Clear toggle UI helps users.</li>
  <li><strong>Prevent flash on load:</strong> set <code>data-theme</code> attribute via inline script in HTML head before React hydrates &mdash; otherwise users see light theme briefly even when dark is preferred.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; transition between themes can be jarring. Skip the transition for vestibular-sensitive users.</li>
  <li><strong>Test all themes</strong> &mdash; Storybook + visual regression catches contrast issues. Ensure WCAG AA contrast in both light and dark modes.</li>
  <li><strong>SSR:</strong> for Next.js, use <code>next-themes</code> &mdash; handles server-rendered theme, no flash, system preference detection.</li>
  <li><strong>Multi-brand themes:</strong> if you support white-label/multi-tenant, the same Context pattern works &mdash; just have more themes in the map.</li>
</ul>

<p><strong>For component libraries:</strong> Material UI, Chakra, Mantine all have ThemeProvider built in. If you&rsquo;re using one, use its provider rather than duplicating the system.</p>
'''

ANSWERS[18] = r'''
<p><strong>Situation:</strong> some routes (dashboard, admin pages) require authentication; some require specific roles (admin, billing manager). Without protection, anyone can navigate to <code>/admin</code> and see the UI &mdash; even if API calls would fail, the brief flash of authenticated content is a security and UX problem.</p>

<p><strong>Approach:</strong> a <code>ProtectedRoute</code> wrapper that checks auth before rendering, redirects to <code>/login</code> with the intended destination preserved, supports role-based access. For React Router v6.4+, use <strong>loaders</strong> &mdash; they run before render, eliminating any flash of unauthenticated content. Always re-validate on the server &mdash; client guards are UX, not security.</p>

<pre><code>import { Navigate, useLocation, useNavigate, BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";

// === ProtectedRoute wrapper ===
function ProtectedRoute({ children, requiredRole }) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return &lt;LoadingScreen /&gt;;   // important — without this, brief flash to /login

  if (!user) {
    // Save destination so login can redirect back
    return &lt;Navigate to="/login" state={{ from: location }} replace /&gt;;
  }

  if (requiredRole &amp;&amp; user.role !== requiredRole) {
    return &lt;Navigate to="/forbidden" replace /&gt;;
  }

  return children;
}

// === Layout wrapper for nested protected routes ===
function ProtectedLayout() {
  return (
    &lt;ProtectedRoute&gt;
      &lt;Header /&gt;
      &lt;Outlet /&gt;     {/* nested routes render here */}
    &lt;/ProtectedRoute&gt;
  );
}

// === Routes ===
function App() {
  return (
    &lt;BrowserRouter&gt;
      &lt;Routes&gt;
        {/* Public */}
        &lt;Route path="/" element={&lt;Home /&gt;} /&gt;
        &lt;Route path="/login" element={&lt;Login /&gt;} /&gt;

        {/* All authenticated users */}
        &lt;Route element={&lt;ProtectedLayout /&gt;}&gt;
          &lt;Route path="/dashboard" element={&lt;Dashboard /&gt;} /&gt;
          &lt;Route path="/profile" element={&lt;Profile /&gt;} /&gt;
        &lt;/Route&gt;

        {/* Admin only */}
        &lt;Route path="/admin" element={
          &lt;ProtectedRoute requiredRole="admin"&gt;
            &lt;AdminLayout /&gt;
          &lt;/ProtectedRoute&gt;
        }&gt;
          &lt;Route index element={&lt;AdminHome /&gt;} /&gt;
          &lt;Route path="users" element={&lt;UserManagement /&gt;} /&gt;
        &lt;/Route&gt;
      &lt;/Routes&gt;
    &lt;/BrowserRouter&gt;
  );
}

// === Login redirects back to original destination ===
function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const handleLogin = async (creds) =&gt; {
    await login(creds);
    navigate(from, { replace: true });
  };
}</code></pre>

<p><strong>Modern approach &mdash; React Router v6.4+ loaders (preferred):</strong></p>

<pre><code>import { createBrowserRouter, redirect, RouterProvider } from "react-router-dom";

const protectedLoader = async () =&gt; {
  const user = await getCurrentUser();
  if (!user) throw redirect("/login");
  return user;
};

const adminLoader = async () =&gt; {
  const user = await getCurrentUser();
  if (!user) throw redirect("/login");
  if (user.role !== "admin") throw redirect("/forbidden");
  return user;
};

const router = createBrowserRouter([
  { path: "/login",     element: &lt;Login /&gt; },
  { path: "/dashboard", element: &lt;Dashboard /&gt;, loader: protectedLoader },
  { path: "/admin",     element: &lt;Admin /&gt;,     loader: adminLoader }
]);</code></pre>

<p>Loaders run <em>before</em> the component renders &mdash; no flash of "checking auth" UI. Auth check happens during navigation; user sees either the destination or the redirect, never the in-between.</p>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Trade-off</th></tr>
  <tr><td>Wrapper component</td><td>Simple; works in v6+. Brief loading screen during async auth check.</td></tr>
  <tr><td>v6.4+ loaders</td><td>No flash; cleaner separation. Requires <code>createBrowserRouter</code> data API.</td></tr>
  <tr><td>Next.js middleware</td><td>Runs at edge before any React. Best for SSR apps.</td></tr>
  <tr><td>Server-side checks</td><td>Mandatory layer (any of above is UX-only). Every protected API endpoint verifies auth.</td></tr>
</table>

<p><strong>Critical &mdash; never trust the client.</strong> Anyone can disable JS, modify the bundle, or hit your API directly. Client-side route guards prevent UI flicker; they do not provide security. Every protected API endpoint must verify authentication and authorization on the server. Test by calling APIs directly with a non-authenticated session &mdash; if anything sensitive returns successfully, you have a vulnerability.</p>

<p><strong>Production patterns:</strong></p>
<ul>
  <li><strong>Permissions per feature, not just per route</strong> &mdash; <code>can(user, "edit", post)</code> rather than just <code>user.role === "admin"</code>. Use a library like <strong>CASL</strong> for fine-grained permissions.</li>
  <li><strong>Stale auth state</strong>: when a user&rsquo;s role changes server-side, their client may still show the old UI. Use short token lifetimes + refresh; consider WebSocket push for instant role updates.</li>
  <li><strong>Forbidden page UX</strong>: explain why access was denied. "You need admin access to view this page" is more helpful than a generic 403.</li>
  <li><strong>Audit log</strong> &mdash; log access attempts to sensitive routes server-side. Helps detect attacks and unauthorized access patterns.</li>
</ul>
'''

ANSWERS[19] = r'''
<p><strong>Situation:</strong> a form with multiple fields, validation rules, async submission, and clear error display. The naive approach (manual <code>useState</code> for every field) doesn&rsquo;t scale &mdash; validation logic spreads across handlers, error timing is awkward, and the code becomes hard to maintain. Production forms benefit from <strong>React Hook Form + Zod</strong>: schema-first validation, performance via uncontrolled inputs, integrated error handling.</p>

<p><strong>Approach:</strong> Zod schema defines validation rules and types in one place; React Hook Form handles state, errors, and submission orchestration; React 19&rsquo;s <code>useFormStatus</code> can layer in pending state for nested buttons.</p>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// === Schema = single source of truth ===
const schema = z.object({
  name:    z.string().min(2, "Name must be at least 2 characters"),
  email:   z.string().email("Please enter a valid email"),
  age:     z.coerce.number().int("Whole number").min(13, "Must be 13+").max(120),
  password: z.string()
    .min(8, "At least 8 characters")
    .regex(/[A-Z]/, "Must include uppercase")
    .regex(/[0-9]/, "Must include number"),
  agree: z.literal(true, { errorMap: () =&gt; ({ message: "You must agree" }) })
});

type FormValues = z.infer&lt;typeof schema&gt;;   // TypeScript type from schema

function SignupForm({ onSuccess }: { onSuccess?: () =&gt; void }) {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting, isSubmitSuccessful, isDirty }
  } = useForm&lt;FormValues&gt;({
    resolver: zodResolver(schema)
  });

  const onSubmit = async (data: FormValues) =&gt; {
    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (!res.ok) {
        const { field, message } = await res.json().catch(() =&gt; ({}));
        if (field) {
          setError(field, { message });   // server-side error attached to specific field
        } else {
          setError("root", { message: message || "Submission failed" });
        }
        return;
      }
      onSuccess?.();
    } catch (err) {
      setError("root", { message: "Network error &mdash; please try again" });
    }
  };

  if (isSubmitSuccessful) {
    return &lt;p&gt;✓ Account created! Check your email to verify.&lt;/p&gt;;
  }

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)} noValidate&gt;
      &lt;label&gt;
        Name
        &lt;input {...register("name")} disabled={isSubmitting} aria-invalid={!!errors.name} /&gt;
        {errors.name &amp;&amp; &lt;p className="err"&gt;{errors.name.message}&lt;/p&gt;}
      &lt;/label&gt;

      &lt;label&gt;
        Email
        &lt;input type="email" {...register("email")} disabled={isSubmitting} aria-invalid={!!errors.email} /&gt;
        {errors.email &amp;&amp; &lt;p className="err"&gt;{errors.email.message}&lt;/p&gt;}
      &lt;/label&gt;

      &lt;label&gt;
        Age
        &lt;input type="number" {...register("age")} disabled={isSubmitting} aria-invalid={!!errors.age} /&gt;
        {errors.age &amp;&amp; &lt;p className="err"&gt;{errors.age.message}&lt;/p&gt;}
      &lt;/label&gt;

      &lt;label&gt;
        Password
        &lt;input type="password" {...register("password")} disabled={isSubmitting} aria-invalid={!!errors.password} /&gt;
        {errors.password &amp;&amp; &lt;p className="err"&gt;{errors.password.message}&lt;/p&gt;}
      &lt;/label&gt;

      &lt;label&gt;
        &lt;input type="checkbox" {...register("agree")} /&gt;
        I accept the terms
        {errors.agree &amp;&amp; &lt;p className="err"&gt;{errors.agree.message}&lt;/p&gt;}
      &lt;/label&gt;

      {errors.root &amp;&amp; &lt;p className="err"&gt;✗ {errors.root.message}&lt;/p&gt;}

      &lt;button type="submit" disabled={isSubmitting || !isDirty}&gt;
        {isSubmitting ? "Creating account..." : "Sign up"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Why this stack wins:</strong></p>

<table>
  <tr><th>Concern</th><th>Solved by</th></tr>
  <tr><td>Validation rules</td><td>Zod schema &mdash; one place, declarative, composable</td></tr>
  <tr><td>TypeScript types</td><td><code>z.infer</code> &mdash; types from schema, no duplication</td></tr>
  <tr><td>Performance</td><td>RHF uses uncontrolled inputs &mdash; no re-render on every keystroke</td></tr>
  <tr><td>Error display timing</td><td>Errors only after blur/submit, not while typing first time</td></tr>
  <tr><td>Server errors</td><td><code>setError(field, ...)</code> attaches errors to specific fields</td></tr>
  <tr><td>Submit state</td><td><code>isSubmitting</code>, <code>isSubmitSuccessful</code>, <code>isDirty</code></td></tr>
  <tr><td>Reuse schema on server</td><td>Same Zod schema validates on Next.js server / API routes</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>RHF vs Formik:</strong> RHF is more performant (less re-rendering) and the dominant choice in 2026. Formik is older but still maintained; smaller communities/codebases.</li>
  <li><strong>Zod vs Yup:</strong> Zod has better TypeScript inference (types come from schema). Yup has wider ecosystem but inferior types. Joi for backend-only.</li>
  <li><strong>Controlled vs uncontrolled:</strong> RHF is uncontrolled by default (better performance). For dependent fields ("if user picks A, show B"), controlled mode via <code>control</code> + <code>Controller</code>.</li>
  <li><strong>React 19 form actions</strong>: <code>useActionState</code> + <code>useFormStatus</code> &mdash; cleaner for forms tied to server actions; the simpler choice when forms POST to a server endpoint and don&rsquo;t need complex client validation.</li>
</ul>

<p><strong>Critical &mdash; always re-validate on the server.</strong> Client validation is UX. The server&rsquo;s Zod schema (which can be the SAME schema imported into both) is the security boundary.</p>
'''

ANSWERS[20] = r'''
<p><strong>Situation:</strong> a React app uses Redux for state management. In 2026, this means <strong>Redux Toolkit (RTK)</strong> &mdash; the official, recommended approach. Classic Redux (manual action types, switch reducers, immutable spreading) is legacy. RTK reduces boilerplate by ~80%, includes Redux DevTools, has TypeScript-first APIs, and ships RTK Query for server data.</p>

<p><strong>Approach:</strong> <code>configureStore</code> for the store, <code>createSlice</code> for reducers + actions, <code>createAsyncThunk</code> for async actions (or RTK Query for server data), typed hooks for <code>useSelector</code>/<code>useDispatch</code>. Split state into domain slices.</p>

<pre><code>// === store/cartSlice.ts ===
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface CartItem { id: string; name: string; price: number; qty: number; }
interface CartState { items: CartItem[]; }

const cartSlice = createSlice({
  name: "cart",
  initialState: { items: [] } as CartState,
  reducers: {
    addItem(state, action: PayloadAction&lt;Omit&lt;CartItem, "qty"&gt;&gt;) {
      const existing = state.items.find(i =&gt; i.id === action.payload.id);
      if (existing) existing.qty += 1;            // looks mutable; Immer handles immutability
      else state.items.push({ ...action.payload, qty: 1 });
    },
    removeItem(state, action: PayloadAction&lt;string&gt;) {
      state.items = state.items.filter(i =&gt; i.id !== action.payload);
    },
    updateQty(state, action: PayloadAction&lt;{ id: string; qty: number }&gt;) {
      const item = state.items.find(i =&gt; i.id === action.payload.id);
      if (item) item.qty = Math.max(1, action.payload.qty);
    },
    clearCart(state) {
      state.items = [];
    }
  }
});

export const { addItem, removeItem, updateQty, clearCart } = cartSlice.actions;
export default cartSlice.reducer;

// === store/index.ts ===
import { configureStore } from "@reduxjs/toolkit";
import cartReducer from "./cartSlice";
import authReducer from "./authSlice";
import { api } from "./api";

export const store = configureStore({
  reducer: {
    cart: cartReducer,
    auth: authReducer,
    [api.reducerPath]: api.reducer
  },
  middleware: (getDefault) =&gt; getDefault().concat(api.middleware)
});

export type RootState = ReturnType&lt;typeof store.getState&gt;;
export type AppDispatch = typeof store.dispatch;

// === Typed hooks (define once, import everywhere) ===
import { useDispatch, useSelector, type TypedUseSelectorHook } from "react-redux";

export const useAppDispatch: () =&gt; AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;

// === Component using the store ===
function Cart() {
  const items = useAppSelector(s =&gt; s.cart.items);
  const total = useAppSelector(s =&gt; s.cart.items.reduce((sum, i) =&gt; sum + i.price * i.qty, 0));
  const dispatch = useAppDispatch();

  return (
    &lt;div&gt;
      {items.map(item =&gt; (
        &lt;div key={item.id}&gt;
          {item.name} × {item.qty} = ${(item.price * item.qty).toFixed(2)}
          &lt;button onClick={() =&gt; dispatch(removeItem(item.id))}&gt;Remove&lt;/button&gt;
        &lt;/div&gt;
      ))}
      &lt;p&gt;Total: ${total.toFixed(2)}&lt;/p&gt;
      &lt;button onClick={() =&gt; dispatch(clearCart())}&gt;Clear&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>RTK Query for server data &mdash; the modern Redux pattern</strong>:</p>

<pre><code>import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  tagTypes: ["Product"],
  endpoints: (builder) =&gt; ({
    getProducts: builder.query&lt;Product[], void&gt;({
      query: () =&gt; "/products",
      providesTags: ["Product"]
    }),
    addProduct: builder.mutation&lt;Product, Partial&lt;Product&gt;&gt;({
      query: (body) =&gt; ({ url: "/products", method: "POST", body }),
      invalidatesTags: ["Product"]   // refetches getProducts after success
    })
  })
});

export const { useGetProductsQuery, useAddProductMutation } = api;

// Usage — no manual loading/error state, no manual refetch
function ProductList() {
  const { data, isLoading, error } = useGetProductsQuery();
  const [addProduct] = useAddProductMutation();

  if (isLoading) return &lt;p&gt;Loading...&lt;/p&gt;;
  return data.map(p =&gt; &lt;div key={p.id}&gt;{p.name}&lt;/div&gt;);
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Trade-off</th></tr>
  <tr><td>Redux vs Zustand vs Context</td><td>Redux for complex apps with action-log requirements; Zustand for lightweight global; Context for low-frequency tree-scoped</td></tr>
  <tr><td>RTK Query vs TanStack Query</td><td>RTK Query: integrated with Redux store. TanStack Query: lighter, more popular, used standalone</td></tr>
  <tr><td>Single store vs feature stores</td><td>Single store always &mdash; that&rsquo;s Redux&rsquo;s model. Split via slices, not multiple stores</td></tr>
  <tr><td>Async via Thunk vs Saga</td><td>Thunk for 90% of cases (built into RTK). Saga for complex orchestration (cancellation, debouncing, race conditions)</td></tr>
</table>

<p><strong>2026 reality:</strong> Redux is no longer the default for new apps. Most projects start with Zustand + TanStack Query. Redux remains the right choice for: (1) large existing codebases, (2) apps requiring strict action logs / time-travel debugging, (3) teams with deep Redux experience. <strong>If you choose Redux, choose RTK</strong> &mdash; classic Redux is unnecessary boilerplate in 2026. <strong>Don&rsquo;t put server data in Redux state</strong> &mdash; use RTK Query for that and keep client state in slices.</p>
'''

ANSWERS[21] = r'''
<p><strong>Situation:</strong> any data fetch can be in three states &mdash; loading, error, or success. Naive code shows blank screens during load, generic "Error" messages on failure, and breaks when the user navigates mid-fetch. Production patterns handle all three states with clear UI, retry capability, and proper cleanup.</p>

<p><strong>Approach:</strong> use <strong>TanStack Query</strong> as the production tool &mdash; it handles loading/error/success states, caching, retries, and refetching declaratively. For learning the underlying pattern, the manual <code>useState</code> + <code>useEffect</code> approach shows what&rsquo;s happening.</p>

<pre><code>// === Production: TanStack Query ===
import { useQuery } from "@tanstack/react-query";

function UserProfile({ userId }) {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ["user", userId],
    queryFn: () =&gt; fetch(`/api/users/${userId}`).then(r =&gt; {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    }),
    staleTime: 5 * 60 * 1000,
    retry: (failureCount, err) =&gt; {
      // Don&rsquo;t retry 4xx — those are client errors, not transient
      if (err.message.includes("HTTP 4")) return false;
      return failureCount &lt; 3;
    }
  });

  if (isLoading) return &lt;UserSkeleton /&gt;;          // initial load
  if (isError) {
    return (
      &lt;div role="alert"&gt;
        &lt;p&gt;⚠️ Couldn&rsquo;t load user: {error.message}&lt;/p&gt;
        &lt;button onClick={() =&gt; refetch()}&gt;Retry&lt;/button&gt;
      &lt;/div&gt;
    );
  }

  return (
    &lt;article&gt;
      {isFetching &amp;&amp; &lt;ProgressBar /&gt;}        {/* refetching in background */}
      &lt;h1&gt;{data.name}&lt;/h1&gt;
      &lt;p&gt;{data.bio}&lt;/p&gt;
    &lt;/article&gt;
  );
}</code></pre>

<p><strong>Manual implementation (for learning the underlying pattern)</strong>:</p>

<pre><code>function UserProfile({ userId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() =&gt; {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);

    fetch(`/api/users/${userId}`, { signal: controller.signal })
      .then(r =&gt; {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch(err =&gt; {
        if (err.name !== "AbortError") setError(err);
      })
      .finally(() =&gt; setIsLoading(false));

    return () =&gt; controller.abort();   // cancel on unmount/dep change
  }, [userId]);

  if (isLoading) return &lt;Spinner /&gt;;
  if (error)     return &lt;ErrorState error={error} /&gt;;
  return &lt;UserCard user={data} /&gt;;
}</code></pre>

<p><strong>Three error categories to distinguish:</strong></p>

<table>
  <tr><th>Error type</th><th>HTTP / cause</th><th>UI response</th></tr>
  <tr><td>Network error</td><td>No connection, DNS, CORS</td><td>"No internet connection. Try again." Retry button.</td></tr>
  <tr><td>Auth required</td><td>401</td><td>Redirect to login</td></tr>
  <tr><td>Permission denied</td><td>403</td><td>"You don&rsquo;t have access" + contact info</td></tr>
  <tr><td>Not found</td><td>404</td><td>"Resource not found" + back link</td></tr>
  <tr><td>Server error</td><td>500-599</td><td>"Something went wrong on our end. We&rsquo;re looking into it." Retry.</td></tr>
  <tr><td>Validation</td><td>400, 422</td><td>Show field-level errors</td></tr>
</table>

<p><strong>Loading state design:</strong></p>

<table>
  <tr><th>Pattern</th><th>When to use</th></tr>
  <tr><td>Skeleton screen</td><td>Lists, cards, predictable layouts &mdash; feels faster than spinners</td></tr>
  <tr><td>Spinner</td><td>Indeterminate operations; small areas where skeletons would be cluttered</td></tr>
  <tr><td>Progress bar</td><td>Long operations (uploads); when you know percentage</td></tr>
  <tr><td>Inline indicator (subtle)</td><td>Background refetch &mdash; don&rsquo;t replace existing content</td></tr>
  <tr><td>Optimistic UI</td><td>User actions where rollback is acceptable on error (likes, toggles)</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>Show stale data while refetching</strong> &mdash; better than empty/spinner. Users keep working while fresh data loads.</li>
  <li><strong>Skeleton vs spinner</strong> &mdash; skeletons feel ~30% faster (research-backed). Worth the implementation effort for above-the-fold content.</li>
  <li><strong>Silent retries vs visible</strong> &mdash; retry transient errors silently up to N times; show error UI only after exhausting retries.</li>
  <li><strong>AbortController in manual code</strong> &mdash; without it, navigation while fetching causes "can&rsquo;t setState on unmounted component" warnings + race conditions.</li>
  <li><strong>Error boundaries for unexpected errors</strong> + try/catch / state for expected ones &mdash; cover both layers.</li>
</ul>

<p><strong>Production polish:</strong> log all errors to Sentry with context (user id, request URL, response body); rate-limit retries (exponential backoff &mdash; 1s, 2s, 4s); don&rsquo;t retry 4xx (client errors, retrying won&rsquo;t help); preserve existing data during refetch (don&rsquo;t flash empty); test error states explicitly (force 500 in DevTools network conditions).</p>
'''

ANSWERS[22] = r'''
<p><strong>Situation:</strong> users perform an action (like, follow, add to cart) and the UI should respond instantly &mdash; not wait 200-500ms for the server. Optimistic updates show the new state immediately, fire the request in the background, and revert on failure. Critical for perceived performance: a like button that lags feels broken; one that updates instantly feels native.</p>

<p><strong>Approach:</strong> use <strong>TanStack Query mutations with optimistic updates</strong> (the production pattern) or <strong>React 19&rsquo;s <code>useOptimistic</code> hook</strong> for simpler cases. Both implement: snapshot current state, apply optimistic change, fire request, revert on error.</p>

<pre><code>// === TanStack Query — optimistic mutations with cache update ===
import { useMutation, useQueryClient } from "@tanstack/react-query";

function useLikePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (postId) =&gt; fetch(`/api/posts/${postId}/like`, { method: "POST" }),

    onMutate: async (postId) =&gt; {
      // Cancel outgoing refetches so they don&rsquo;t overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: ["posts"] });

      // Snapshot previous value for rollback
      const previousPosts = queryClient.getQueryData(["posts"]);

      // Optimistically update cache
      queryClient.setQueryData(["posts"], (old) =&gt;
        old.map(post =&gt;
          post.id === postId
            ? { ...post, likes: post.likes + 1, likedByMe: true }
            : post
        )
      );

      return { previousPosts };   // context for onError
    },

    onError: (err, postId, context) =&gt; {
      // Rollback to previous state
      queryClient.setQueryData(["posts"], context.previousPosts);
      toast.error("Couldn&rsquo;t like &mdash; try again");
    },

    onSettled: () =&gt; {
      // Refetch in the background to sync with server (handles concurrent likes from other clients)
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    }
  });
}

function LikeButton({ post }) {
  const { mutate, isPending } = useLikePost();

  return (
    &lt;button onClick={() =&gt; mutate(post.id)} disabled={isPending}&gt;
      ❤ {post.likes}
    &lt;/button&gt;
  );
}</code></pre>

<p><strong>React 19&rsquo;s <code>useOptimistic</code> hook (simpler API):</strong></p>

<pre><code>import { useOptimistic, useState } from "react";

function LikeButton({ postId, initialLikes }) {
  const [likes, setLikes] = useState(initialLikes);
  const [optimisticLikes, addOptimisticLike] = useOptimistic(likes);

  const handleLike = async () =&gt; {
    addOptimisticLike(optimisticLikes + 1);   // instant UI update

    try {
      const newCount = await api.likePost(postId);
      setLikes(newCount);                      // confirm with server value
    } catch (err) {
      // useOptimistic auto-reverts on error or next render
      toast.error("Failed to like");
    }
  };

  return &lt;button onClick={handleLike}&gt;❤ {optimisticLikes}&lt;/button&gt;;
}</code></pre>

<p><strong>When to use optimistic updates:</strong></p>

<table>
  <tr><th>Good fit</th><th>Bad fit</th></tr>
  <tr><td>Likes, hearts, votes</td><td>Payment processing</td></tr>
  <tr><td>Adding/deleting list items</td><td>Form submissions with server validation</td></tr>
  <tr><td>Reordering, drag-and-drop</td><td>Email/notification sending (rollback would confuse)</td></tr>
  <tr><td>Toggle states (subscribe, follow, mute)</td><td>Critical financial operations</td></tr>
  <tr><td>Comments, replies</td><td>Anything with side effects users notice</td></tr>
</table>

<p><strong>Trade-offs and pitfalls:</strong></p>
<ul>
  <li><strong>Rollback UX matters:</strong> if a like reverts after 2 seconds, users notice. Show a toast explaining the failure with retry. Don&rsquo;t silently revert.</li>
  <li><strong>Concurrent updates:</strong> two users like simultaneously &mdash; client predicts +1 each, server returns +2. The <code>onSettled</code> refetch reconciles. Without it, the local count diverges from server reality.</li>
  <li><strong>Don&rsquo;t use for high-stakes operations:</strong> payments, deletion of important data, account changes. Use loading states + confirm on success.</li>
  <li><strong>Idempotent operations only:</strong> the request should be safe to retry. POST that creates duplicates on retry isn&rsquo;t a good optimistic candidate without an idempotency key.</li>
  <li><strong>Unique IDs for created items:</strong> when adding optimistic items, generate a temporary ID; replace with real ID when server response arrives. Otherwise React&rsquo;s key tracking breaks.</li>
</ul>

<p><strong>Real-time considerations:</strong> if your app receives real-time updates via WebSocket (live like counts), the optimistic update can race with the WebSocket event. Use a "pending mutations" flag to prefer client&rsquo;s prediction during the in-flight window; sync to server truth on settle.</p>

<p><strong>Production polish:</strong></p>
<ul>
  <li><strong>Disable button during in-flight</strong> only if the action is non-idempotent or user shouldn&rsquo;t spam. For likes, allow rapid clicks.</li>
  <li><strong>Visual feedback</strong>: subtle scale animation, color change &mdash; reinforces "your action registered."</li>
  <li><strong>Telemetry</strong>: track optimistic-update failure rates. High failures = unreliable backend or aggressive validation; investigate.</li>
  <li><strong>Server idempotency</strong>: send a request key with mutations; server dedups. Prevents duplicate submissions on retry.</li>
</ul>
'''

ANSWERS[23] = r'''
<p><strong>Situation:</strong> the React app&rsquo;s initial JavaScript bundle is hundreds of KB (or MB) because it includes code for every page, every modal, every chart library &mdash; even though most users only see a small subset on first load. The fix is <strong>code splitting</strong>: load chunks on-demand rather than all upfront. Smaller initial bundle means faster first paint, faster Time to Interactive, better Core Web Vitals.</p>

<p><strong>Approach:</strong> <strong>route-based splitting</strong> (every top-level route as its own chunk) is the highest-leverage starting point; then split on <strong>modals</strong>, <strong>tabs</strong>, and <strong>heavy below-the-fold features</strong>. Modern bundlers (Vite, Next.js) handle the actual splitting; your job is to use <code>React.lazy()</code> + dynamic imports.</p>

<pre><code>import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Each lazy() call → separate chunk
const Home      = lazy(() =&gt; import("./pages/Home"));
const Dashboard = lazy(() =&gt; import("./pages/Dashboard"));
const Settings  = lazy(() =&gt; import("./pages/Settings"));
const Admin     = lazy(() =&gt; import("./pages/Admin"));

function App() {
  return (
    &lt;BrowserRouter&gt;
      &lt;Suspense fallback={&lt;PageSkeleton /&gt;}&gt;
        &lt;Routes&gt;
          &lt;Route path="/" element={&lt;Home /&gt;} /&gt;
          &lt;Route path="/dashboard" element={&lt;Dashboard /&gt;} /&gt;
          &lt;Route path="/settings" element={&lt;Settings /&gt;} /&gt;
          &lt;Route path="/admin/*" element={&lt;Admin /&gt;} /&gt;
        &lt;/Routes&gt;
      &lt;/Suspense&gt;
    &lt;/BrowserRouter&gt;
  );
}</code></pre>

<p><strong>Component-level splitting for heavy features:</strong></p>

<pre><code>// Modal only loads when opened
const ImageEditor = lazy(() =&gt; import("./ImageEditor"));   // 400KB chunk

function App() {
  const [editing, setEditing] = useState(false);
  return (
    &lt;&gt;
      &lt;button onClick={() =&gt; setEditing(true)}&gt;Edit image&lt;/button&gt;
      {editing &amp;&amp; (
        &lt;Suspense fallback={&lt;Spinner /&gt;}&gt;
          &lt;ImageEditor onClose={() =&gt; setEditing(false)} /&gt;
        &lt;/Suspense&gt;
      )}
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Preload on hover &mdash; the perceived-performance trick:</strong></p>

<pre><code>function NavLink({ to, children, lazyComponent }) {
  // Trigger import() when user hovers a link — chunk loads while they hover
  const handleHover = () =&gt; lazyComponent.preload?.();

  return &lt;Link to={to} onMouseEnter={handleHover}&gt;{children}&lt;/Link&gt;;
}

// preload pattern via custom helper
function lazyWithPreload(importFn) {
  const Component = lazy(importFn);
  Component.preload = importFn;
  return Component;
}

const Dashboard = lazyWithPreload(() =&gt; import("./Dashboard"));</code></pre>

<p>By the time the user clicks the link, the chunk is often already loaded &mdash; navigation feels instant.</p>

<p><strong>Common patterns to split:</strong></p>

<table>
  <tr><th>Pattern</th><th>Reason</th></tr>
  <tr><td>Route-level</td><td>Pages users may never visit (admin, account settings)</td></tr>
  <tr><td>Modals / dialogs</td><td>Only loaded when triggered</td></tr>
  <tr><td>Below-the-fold sections</td><td>Hero is visible immediately; carousel/footer can defer</td></tr>
  <tr><td>Heavy libraries (chart, editor, video player)</td><td>Replace 200KB+ chunks with on-demand</td></tr>
  <tr><td>Authentication-gated UIs</td><td>Public users don&rsquo;t need authenticated bundle</td></tr>
  <tr><td>Feature flags / experiments</td><td>Don&rsquo;t ship inactive features to all users</td></tr>
</table>

<p><strong>Bundle analysis &mdash; know what you&rsquo;re shipping:</strong></p>

<pre><code>// Vite
npm install --save-dev rollup-plugin-visualizer

// vite.config.js
import { visualizer } from "rollup-plugin-visualizer";
plugins: [react(), visualizer({ open: true })]
// Build, then visualize: npm run build → opens treemap

// Next.js
ANALYZE=true npm run build   // with @next/bundle-analyzer</code></pre>

<p>Look for: large libraries that could be replaced with smaller alternatives, code that ended up in the wrong chunk, duplicate dependencies, vendor bundles that could split further.</p>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Trade-off</th></tr>
  <tr><td>Too few chunks</td><td>Big initial bundle; slow first paint</td></tr>
  <tr><td>Too many chunks</td><td>Many small network requests; HTTP/2 mitigates but doesn&rsquo;t eliminate</td></tr>
  <tr><td>Dynamic imports add complexity</td><td>Need <code>Suspense</code> boundaries; loading states; error handling</td></tr>
  <tr><td>Default exports required for <code>React.lazy</code></td><td>Workaround: <code>lazy(() =&gt; import("./X").then(m =&gt; ({ default: m.Named })))</code></td></tr>
  <tr><td>Cache invalidation on deploy</td><td>Content-hashed filenames mean changed code = new chunk hash; old chunks cached forever (good)</td></tr>
</table>

<p><strong>Common pitfalls:</strong></p>
<ul>
  <li><strong>Loading state placement:</strong> too high in the tree = whole page replaced with spinner; too low = layout jumps. Place <code>Suspense</code> at the boundary that makes sense for users.</li>
  <li><strong>Forgetting error boundaries:</strong> chunk load can fail (network blip, server hiccup, deploy mismatch). Wrap with <code>react-error-boundary</code> with retry; otherwise users see broken pages.</li>
  <li><strong>Over-splitting tiny components:</strong> 5KB chunk creates a network roundtrip cost that exceeds the savings. Group related components.</li>
  <li><strong>Bundle-of-bundles problem:</strong> shared dependencies (React, lodash) end up in every chunk. Configure your bundler&rsquo;s shared chunk strategy (<code>splitChunks</code> in Webpack; automatic in Vite/Next.js).</li>
</ul>
'''

ANSWERS[24] = r'''
<p><strong>Situation:</strong> drag-and-drop is needed for: reordering list items (todos, kanban cards), file uploads (drag files into drop zone), moving items between containers (Trello-like boards), or sortable grids (image galleries). Native HTML5 drag API works on desktop but fails on mobile; <strong>react-beautiful-dnd</strong> is unmaintained as of late 2023; <strong>dnd-kit</strong> is the modern replacement.</p>

<p><strong>Approach:</strong> use <strong>dnd-kit</strong> for production. It supports mouse, touch, keyboard navigation (a11y), works on mobile, animates smoothly, supports list/grid/multi-container patterns. Native HTML5 only for trivial cases or file-drop zones.</p>

<pre><code>// Install: npm install @dnd-kit/core @dnd-kit/sortable

import {
  DndContext, closestCenter, KeyboardSensor, PointerSensor, TouchSensor,
  useSensor, useSensors
} from "@dnd-kit/core";
import {
  arrayMove, SortableContext, sortableKeyboardCoordinates,
  useSortable, verticalListSortingStrategy
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useState } from "react";

function SortableItem({ id, content }) {
  const {
    attributes, listeners, setNodeRef, transform, transition, isDragging
  } = useSortable({ id });

  return (
    &lt;li
      ref={setNodeRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
        background: "#f5f5f5",
        padding: 12,
        margin: "4px 0",
        cursor: "grab"
      }}
      {...attributes}
      {...listeners}
    &gt;
      ⋮⋮ {content}
    &lt;/li&gt;
  );
}

function SortableList() {
  const [items, setItems] = useState([
    { id: "1", content: "Buy groceries" },
    { id: "2", content: "Walk dog" },
    { id: "3", content: "Write code" },
    { id: "4", content: "Read book" }
  ]);

  // Multiple sensors handle mouse, touch, and keyboard
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event) =&gt; {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    setItems(prev =&gt; {
      const oldIndex = prev.findIndex(i =&gt; i.id === active.id);
      const newIndex = prev.findIndex(i =&gt; i.id === over.id);
      return arrayMove(prev, oldIndex, newIndex);
    });

    // Persist new order to server
    persistOrder(items.map(i =&gt; i.id));
  };

  return (
    &lt;DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    &gt;
      &lt;SortableContext items={items} strategy={verticalListSortingStrategy}&gt;
        &lt;ul&gt;
          {items.map(item =&gt; (
            &lt;SortableItem key={item.id} id={item.id} content={item.content} /&gt;
          ))}
        &lt;/ul&gt;
      &lt;/SortableContext&gt;
    &lt;/DndContext&gt;
  );
}</code></pre>

<p><strong>Multi-container drag (Trello-style):</strong></p>

<pre><code>// Each column is its own SortableContext;
// items can move between columns
&lt;DndContext onDragEnd={handleCrossColumnDrag}&gt;
  &lt;div className="board"&gt;
    {columns.map(col =&gt; (
      &lt;SortableContext
        key={col.id}
        items={col.items.map(i =&gt; i.id)}
        id={col.id}
      &gt;
        &lt;Column id={col.id} items={col.items} /&gt;
      &lt;/SortableContext&gt;
    ))}
  &lt;/div&gt;
&lt;/DndContext&gt;</code></pre>

<p><strong>File drop zones &mdash; just native HTML5</strong>:</p>

<pre><code>function DropZone({ onFiles }) {
  const [isOver, setIsOver] = useState(false);

  return (
    &lt;div
      onDragEnter={() =&gt; setIsOver(true)}
      onDragLeave={() =&gt; setIsOver(false)}
      onDragOver={e =&gt; e.preventDefault()}    // required to allow drop
      onDrop={(e) =&gt; {
        e.preventDefault();
        setIsOver(false);
        onFiles(e.dataTransfer.files);
      }}
      style={{
        border: isOver ? "2px solid blue" : "2px dashed #ccc",
        padding: 32, textAlign: "center"
      }}
    &gt;
      Drop files here
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Library comparison (2026):</strong></p>

<table>
  <tr><th>Library</th><th>Status</th><th>Use for</th></tr>
  <tr><td>dnd-kit</td><td>Active, recommended</td><td>List/grid sorting, multi-container, full a11y</td></tr>
  <tr><td>react-beautiful-dnd</td><td>UNMAINTAINED (Atlassian dropped support 2023)</td><td>Avoid for new projects</td></tr>
  <tr><td>react-dnd</td><td>Active but complex API</td><td>Custom drag types, advanced use cases</td></tr>
  <tr><td>HTML5 native</td><td>Built into browser</td><td>File drop zones; simple desktop-only patterns</td></tr>
  <tr><td>react-sortablejs</td><td>Active, simpler than dnd-kit</td><td>Quick lists; less power than dnd-kit</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>Touch support:</strong> mandatory for mobile. dnd-kit&rsquo;s TouchSensor with delay (~200ms press-and-hold) prevents accidental drags during scroll.</li>
  <li><strong>Keyboard accessibility:</strong> arrow keys to move, Space to pick up, Enter to drop. Without this, keyboard users can&rsquo;t reorder. dnd-kit ships this.</li>
  <li><strong>Activation constraint:</strong> require 5px movement before drag starts (prevents accidental drags on click).</li>
  <li><strong>Persist order:</strong> on each drag end, save the new order to server. Use a debounce or batch if rapid reorders are common.</li>
  <li><strong>Optimistic update:</strong> apply the new order immediately client-side; revert on server error.</li>
  <li><strong>Animation:</strong> dnd-kit auto-animates the swap. For Framer Motion-style transitions, use <code>AnimatePresence</code> with item layout animations.</li>
  <li><strong>Virtualization compatibility:</strong> dnd-kit works with TanStack Virtual via the SortableContext + virtualizer integration; non-trivial setup but possible.</li>
</ul>
'''

ANSWERS[25] = r'''
<p><strong>Situation:</strong> a React app needs real-time data &mdash; chat messages, live notifications, collaborative editing, presence indicators, stock tickers. WebSockets enable bi-directional communication; alternatives include Server-Sent Events (one-way), long-polling, and managed services that abstract the protocol.</p>

<p><strong>Approach:</strong> for new apps in 2026, prefer <strong>managed real-time services</strong> &mdash; <strong>Liveblocks</strong> (collaboration), <strong>Pusher</strong>/<strong>Ably</strong> (pub/sub), <strong>Supabase Realtime</strong>, <strong>Convex</strong>, or <strong>Firebase Realtime Database/Firestore</strong> &mdash; rather than building from raw WebSockets. They handle reconnection, scaling, presence, message ordering. Roll-your-own only if you have specific protocol or self-hosting requirements.</p>

<pre><code>// === Pattern: WebSocket connection in a custom hook ===
import { useEffect, useState, useRef, useCallback } from "react";

function useWebSocket(url) {
  const [readyState, setReadyState] = useState(WebSocket.CONNECTING);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() =&gt; {
    let cancelled = false;

    function connect() {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen    = () =&gt; setReadyState(WebSocket.OPEN);
      ws.onmessage = (event) =&gt; setLastMessage(JSON.parse(event.data));
      ws.onerror   = (err) =&gt; console.error("WS error", err);
      ws.onclose   = () =&gt; {
        setReadyState(WebSocket.CLOSED);
        // Reconnect with exponential backoff
        if (!cancelled) {
          reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
      };
    }

    connect();

    return () =&gt; {
      cancelled = true;
      clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [url]);

  const send = useCallback((data) =&gt; {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { readyState, lastMessage, send };
}

// === Chat component ===
function Chat({ roomId }) {
  const { readyState, lastMessage, send } = useWebSocket(
    `wss://api.example.com/chat/${roomId}`
  );
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Append new messages
  useEffect(() =&gt; {
    if (lastMessage?.type === "message") {
      setMessages(prev =&gt; [...prev, lastMessage]);
    }
  }, [lastMessage]);

  const handleSend = () =&gt; {
    if (!input.trim()) return;
    send({ type: "message", text: input, timestamp: Date.now() });
    setInput("");
  };

  return (
    &lt;div&gt;
      &lt;ConnectionIndicator state={readyState} /&gt;
      &lt;ul&gt;{messages.map(m =&gt; &lt;li key={m.id}&gt;{m.text}&lt;/li&gt;)}&lt;/ul&gt;
      &lt;input value={input} onChange={e =&gt; setInput(e.target.value)} /&gt;
      &lt;button onClick={handleSend} disabled={readyState !== WebSocket.OPEN}&gt;Send&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Managed alternative &mdash; Pusher Channels (much less code):</strong></p>

<pre><code>import Pusher from "pusher-js";

const pusher = new Pusher(import.meta.env.VITE_PUSHER_KEY, { cluster: "us2" });

function Chat({ roomId }) {
  const [messages, setMessages] = useState([]);

  useEffect(() =&gt; {
    const channel = pusher.subscribe(`chat-${roomId}`);
    channel.bind("message", (msg) =&gt; setMessages(prev =&gt; [...prev, msg]));
    return () =&gt; pusher.unsubscribe(`chat-${roomId}`);
  }, [roomId]);

  const send = (text) =&gt; fetch("/api/chat", {
    method: "POST",
    body: JSON.stringify({ roomId, text })
  });

  // ...
}</code></pre>

<p><strong>Real-time service comparison (2026):</strong></p>

<table>
  <tr><th>Service</th><th>Best for</th></tr>
  <tr><td>Liveblocks</td><td>Collaborative editing (cursors, selections, conflict resolution); CRDTs</td></tr>
  <tr><td>Pusher / Ably</td><td>Pub/sub, simple real-time events; mature</td></tr>
  <tr><td>Supabase Realtime</td><td>Postgres change streams; pairs with Supabase Auth/DB</td></tr>
  <tr><td>Convex</td><td>Real-time queries; reactive backend; great DX</td></tr>
  <tr><td>Firebase Realtime DB / Firestore</td><td>Quick setup; tight Google ecosystem integration</td></tr>
  <tr><td>Socket.io</td><td>Self-hosted; abstraction over WebSockets with reconnect built in</td></tr>
  <tr><td>Roll-your-own WebSockets</td><td>Existing infra; specific protocol needs</td></tr>
</table>

<p><strong>Trade-offs and production concerns:</strong></p>

<table>
  <tr><th>Concern</th><th>Solution</th></tr>
  <tr><td>Reconnection on network drop</td><td>Exponential backoff; visual indicator; queued messages</td></tr>
  <tr><td>Authentication</td><td>Send JWT in connection URL or first message; server validates</td></tr>
  <tr><td>Message ordering</td><td>Sequence numbers; resync after reconnect</td></tr>
  <tr><td>Backpressure (slow consumer)</td><td>Drop messages, batch, or buffer with limits</td></tr>
  <tr><td>Stale state on reconnect</td><td>Refetch initial state via REST after reconnect; merge with new events</td></tr>
  <tr><td>Mobile background</td><td>iOS/Android suspends WebSockets when app is backgrounded; reconnect on resume</td></tr>
  <tr><td>Server scaling</td><td>WebSockets are stateful — sticky sessions or pub/sub layer (Redis) for horizontal scale</td></tr>
  <tr><td>Bandwidth</td><td>Send minimal payloads; binary frames for high-volume; compress with permessage-deflate</td></tr>
</table>

<p><strong>SSE vs WebSockets:</strong> Server-Sent Events are simpler when you only need server-to-client (notifications, live feed). They auto-reconnect, work over standard HTTP, no special server. Use SSE first; reach for WebSockets only when client needs to send messages too.</p>

<p><strong>For collaborative apps</strong> (multiple users editing same doc), don&rsquo;t roll your own conflict resolution &mdash; use <strong>Liveblocks</strong>, <strong>Yjs</strong>, or <strong>Automerge</strong>. CRDTs handle merges correctly; manual approaches reliably create bugs at scale.</p>
'''

ANSWERS[26] = r'''
<p><strong>Situation:</strong> the app needs notifications visible app-wide &mdash; success after save, error after failed request, info when something happens in another tab. They should appear from anywhere (deep components, hooks, async code), stack visually, auto-dismiss, and be accessible.</p>

<p><strong>Approach:</strong> a singleton notification store (Zustand or Context) + a portal-rendered <code>&lt;NotificationCenter&gt;</code> at the app root. Any code can <code>notify.success("Saved!")</code> &mdash; the store updates, the center re-renders. For 2026 production, <strong>react-hot-toast</strong> or <strong>Sonner</strong> ship this pattern with great UX out of the box.</p>

<pre><code>// store.ts — Zustand
import { create } from "zustand";

type Toast = { id: string; type: "success"|"error"|"info"; message: string; duration: number };

type Store = {
  toasts: Toast[];
  show: (type: Toast["type"], message: string, duration?: number) =&gt; void;
  dismiss: (id: string) =&gt; void;
};

export const useToastStore = create&lt;Store&gt;((set) =&gt; ({
  toasts: [],
  show: (type, message, duration = 4000) =&gt; {
    const id = crypto.randomUUID();
    set(s =&gt; ({ toasts: [...s.toasts, { id, type, message, duration }] }));
    if (duration &gt; 0) {
      setTimeout(() =&gt; set(s =&gt; ({ toasts: s.toasts.filter(t =&gt; t.id !== id) })), duration);
    }
  },
  dismiss: (id) =&gt; set(s =&gt; ({ toasts: s.toasts.filter(t =&gt; t.id !== id) }))
}));

// Convenience API — callable from anywhere, no hook needed
export const notify = {
  success: (msg: string) =&gt; useToastStore.getState().show("success", msg),
  error:   (msg: string) =&gt; useToastStore.getState().show("error", msg, 6000),
  info:    (msg: string) =&gt; useToastStore.getState().show("info", msg)
};</code></pre>

<pre><code>// NotificationCenter.tsx — render-once at app root
import { createPortal } from "react-dom";
import { useToastStore } from "./store";

export function NotificationCenter() {
  const { toasts, dismiss } = useToastStore();

  return createPortal(
    &lt;div role="region" aria-live="polite" aria-label="Notifications"
         style={{ position: "fixed", top: 16, right: 16, display: "grid", gap: 8 }}&gt;
      {toasts.map(t =&gt; (
        &lt;div key={t.id} role={t.type === "error" ? "alert" : "status"}
             className={`toast toast-${t.type}`}&gt;
          {t.message}
          &lt;button onClick={() =&gt; dismiss(t.id)} aria-label="Dismiss"&gt;✕&lt;/button&gt;
        &lt;/div&gt;
      ))}
    &lt;/div&gt;,
    document.body
  );
}

// Usage from anywhere:
async function handleSave() {
  try {
    await api.save(form);
    notify.success("Profile saved");
  } catch (e) {
    notify.error(e.message);
  }
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Portal escapes parent CSS</td><td>Render into document.body via <code>createPortal</code></td></tr>
  <tr><td>Accessibility</td><td><code>role="status"</code> for info, <code>role="alert"</code> for errors; <code>aria-live="polite"</code> on container</td></tr>
  <tr><td>Avoiding spam</td><td>De-duplicate identical messages within a window; cap visible toasts at 3-5</td></tr>
  <tr><td>Action toasts</td><td>Support optional <code>action: { label, onClick }</code> for &ldquo;Undo&rdquo; patterns</td></tr>
  <tr><td>Long-running ops</td><td>Promise toast: <code>notify.promise(fetch(...), { loading, success, error })</code></td></tr>
  <tr><td>Don&rsquo;t roll your own</td><td>react-hot-toast or Sonner have all this + animations + stacking + reduced-motion support</td></tr>
</table>

<p><strong>For Sonner (the 2026 default)</strong>: <code>toast.success("Saved!")</code> from anywhere; <code>&lt;Toaster /&gt;</code> at root. Done. Roll-your-own only if you have specific design constraints.</p>
'''

ANSWERS[27] = r'''
<p><strong>Situation:</strong> the app must support multiple languages: translated strings, locale-aware date/number/currency formats, plurals, and right-to-left layouts for Arabic/Hebrew. Translation strings live in JSON files; the active locale switches at runtime; URL routes per locale (<code>/en/about</code>, <code>/es/about</code>) for SEO and shareability.</p>

<p><strong>Approach:</strong> use <strong>react-i18next</strong> for string translation + native <code>Intl</code> APIs for formatting. Keep formatting OUT of translation files &mdash; <code>Intl.NumberFormat</code> handles currency/number/date locale-correctly. For Next.js, use App Router with <code>[lang]</code> dynamic segment and middleware for locale detection.</p>

<pre><code>// i18n.ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import HttpBackend from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";

i18n
  .use(HttpBackend)            // load /locales/{lng}/{ns}.json on demand
  .use(LanguageDetector)        // detect from URL, cookie, browser
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    supportedLngs: ["en", "es", "fr", "de", "ja", "ar"],
    ns: ["common", "checkout", "dashboard"],
    defaultNS: "common",
    interpolation: { escapeValue: false }   // React handles escaping
  });

export default i18n;</code></pre>

<pre><code>// /public/locales/en/common.json
{
  "welcome": "Hello, {{name}}!",
  "items_one": "{{count}} item",
  "items_other": "{{count}} items",
  "items_zero": "No items"
}

// Component
import { useTranslation } from "react-i18next";

function Header() {
  const { t, i18n } = useTranslation();
  const isRtl = ["ar", "he", "fa"].includes(i18n.language);

  return (
    &lt;header dir={isRtl ? "rtl" : "ltr"}&gt;
      &lt;h1&gt;{t("welcome", { name: "Alice" })}&lt;/h1&gt;
      &lt;p&gt;{t("items", { count: cart.length })}&lt;/p&gt;

      &lt;select value={i18n.language} onChange={e =&gt; i18n.changeLanguage(e.target.value)}&gt;
        &lt;option value="en"&gt;English&lt;/option&gt;
        &lt;option value="es"&gt;Español&lt;/option&gt;
        &lt;option value="ja"&gt;日本語&lt;/option&gt;
        &lt;option value="ar"&gt;العربية&lt;/option&gt;
      &lt;/select&gt;
    &lt;/header&gt;
  );
}

// Formatting via Intl — never put numbers in translation strings
function Price({ amount, currency }) {
  const { i18n } = useTranslation();
  return (
    &lt;span&gt;
      {new Intl.NumberFormat(i18n.language, { style: "currency", currency }).format(amount)}
    &lt;/span&gt;
  );
}</code></pre>

<p><strong>RTL with CSS logical properties:</strong></p>

<pre><code>/* Logical properties auto-flip in RTL */
.card {
  margin-inline-start: 16px;       /* left in LTR, right in RTL */
  padding-inline: 12px;
  text-align: start;
  border-inline-end: 1px solid #ddd;
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Bundle size</td><td>Lazy-load translation namespaces by route; only load active locale</td></tr>
  <tr><td>Translator workflow</td><td>Use a TMS (Lokalise, Crowdin, Phrase) &mdash; not raw JSON files in PRs</td></tr>
  <tr><td>Plurals</td><td>ICU MessageFormat (built into i18next) handles language-specific plural rules (Russian has 4)</td></tr>
  <tr><td>Hardcoded English strings</td><td>Test with pseudo-locale (<code>en-XA</code>) &mdash; surfaces missed strings as <code>[Ŵĕļčōmé!]</code></td></tr>
  <tr><td>SEO per locale</td><td>Server-rendered routes per locale; <code>&lt;link rel="alternate" hreflang&gt;</code> tags</td></tr>
  <tr><td>Date/time/number</td><td>Native Intl APIs &mdash; never delegate to translation strings</td></tr>
</table>

<p><strong>2026 alternatives:</strong> <strong>FormatJS / react-intl</strong> (mature, FormatJS spec); <strong>Lingui</strong> (compile-time extraction). For Next.js App Router, <strong>next-intl</strong> integrates cleanly with Server Components. Don&rsquo;t store translation strings in components &mdash; extract them to JSON or you&rsquo;ll repeat the work when adding the next language.</p>
'''

ANSWERS[28] = r'''
<p><strong>Situation:</strong> a component fetches data on mount and renders loading, success, and error states. Tests must verify all three paths work, without hitting the real API. Standard practice: <strong>Vitest + React Testing Library + MSW</strong> (Mock Service Worker) for HTTP mocking at the network layer.</p>

<p><strong>Approach:</strong> MSW intercepts fetch/XHR calls in tests and returns the responses you define &mdash; so tests verify the component-network integration, not just unit behavior. Tests focus on what users see (rendered output) rather than implementation details (which hook called which fn).</p>

<pre><code>// UserList.tsx — the component under test
import { useEffect, useState } from "react";

export function UserList() {
  const [users, setUsers] = useState&lt;User[] | null&gt;(null);
  const [error, setError] = useState&lt;string | null&gt;(null);

  useEffect(() =&gt; {
    fetch("/api/users")
      .then(r =&gt; { if (!r.ok) throw new Error("Failed"); return r.json(); })
      .then(setUsers)
      .catch(e =&gt; setError(e.message));
  }, []);

  if (error) return &lt;p&gt;Error: {error}&lt;/p&gt;;
  if (!users) return &lt;p&gt;Loading...&lt;/p&gt;;
  return (
    &lt;ul&gt;{users.map(u =&gt; &lt;li key={u.id}&gt;{u.name}&lt;/li&gt;)}&lt;/ul&gt;
  );
}</code></pre>

<pre><code>// test/setup.ts — MSW server setup
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import { afterAll, afterEach, beforeAll } from "vitest";

export const server = setupServer();
beforeAll(() =&gt; server.listen({ onUnhandledRequest: "error" }));
afterEach(() =&gt; server.resetHandlers());
afterAll(() =&gt; server.close());</code></pre>

<pre><code>// UserList.test.tsx
import { render, screen } from "@testing-library/react";
import { http, HttpResponse, delay } from "msw";
import { describe, it, expect } from "vitest";
import { server } from "./setup";
import { UserList } from "./UserList";

describe("&lt;UserList /&gt;", () =&gt; {
  it("shows loading initially", async () =&gt; {
    server.use(
      http.get("/api/users", async () =&gt; {
        await delay(50);
        return HttpResponse.json([]);
      })
    );
    render(&lt;UserList /&gt;);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders users on success", async () =&gt; {
    server.use(
      http.get("/api/users", () =&gt;
        HttpResponse.json([
          { id: 1, name: "Alice" },
          { id: 2, name: "Bob"   }
        ])
      )
    );
    render(&lt;UserList /&gt;);
    expect(await screen.findByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
  });

  it("shows error on 500", async () =&gt; {
    server.use(
      http.get("/api/users", () =&gt; new HttpResponse(null, { status: 500 }))
    );
    render(&lt;UserList /&gt;);
    expect(await screen.findByText(/Error: Failed/)).toBeInTheDocument();
  });
});</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>When</th></tr>
  <tr><td>MSW (network-level mock)</td><td>Default. Tests integrate fetch + parsing + rendering &mdash; closest to production</td></tr>
  <tr><td>Mock fetch directly (<code>vi.spyOn</code>)</td><td>Quick unit test; bypasses MSW setup. Less realistic</td></tr>
  <tr><td>Mock the data hook (<code>vi.mock("./useUsers")</code>)</td><td>When testing UI logic in isolation, not data flow</td></tr>
  <tr><td>Test the real backend</td><td>E2E tests with Playwright; not unit tests</td></tr>
</table>

<p><strong>Critical RTL principles:</strong> query by accessible roles/labels (<code>getByRole</code>, <code>getByLabelText</code>) &mdash; not classes/test-ids; use <code>findBy*</code> for async appearance; <code>userEvent</code> over <code>fireEvent</code> for typing/clicking; never query by component instance &mdash; query by what users see. <strong>Don&rsquo;t mock everything</strong> &mdash; over-mocked tests pass even when production fails. MSW gives realistic integration without flake. Old &ldquo;Enzyme + shallow render&rdquo; pattern is now legacy; RTL is the standard.</p>
'''

ANSWERS[29] = r'''
<p><strong>Situation:</strong> functional components don&rsquo;t have lifecycle methods. The hook equivalents handle mount, update, unmount, and other patterns &mdash; but the model is different: instead of "do X at lifecycle phase Y," you express "synchronize this side effect with these dependencies."</p>

<p><strong>Approach:</strong> map each class lifecycle need to a hook pattern. <code>useEffect</code> handles 90% of cases; <code>useLayoutEffect</code> for DOM-measurement; refs for instance variables. The mental shift: stop thinking in phases, start thinking in synchronization.</p>

<table>
  <tr><th>Class lifecycle</th><th>Hook equivalent</th></tr>
  <tr><td><code>componentDidMount</code></td><td><code>useEffect(() =&gt; {...}, [])</code></td></tr>
  <tr><td><code>componentDidUpdate</code> (any change)</td><td><code>useEffect(() =&gt; {...})</code> (no deps array)</td></tr>
  <tr><td><code>componentDidUpdate</code> (specific prop)</td><td><code>useEffect(() =&gt; {...}, [propName])</code></td></tr>
  <tr><td><code>componentWillUnmount</code></td><td>cleanup function returned by <code>useEffect</code></td></tr>
  <tr><td><code>shouldComponentUpdate</code></td><td><code>React.memo</code> + <code>useCallback</code>/<code>useMemo</code></td></tr>
  <tr><td><code>getDerivedStateFromProps</code></td><td>compute during render or use <code>useMemo</code></td></tr>
  <tr><td><code>componentDidCatch</code></td><td>(no hook yet &mdash; class still required for error boundaries)</td></tr>
</table>

<pre><code>// === Mount + unmount in one effect ===
function Chat({ userId }) {
  useEffect(() =&gt; {
    const subscription = api.subscribe(userId);
    return () =&gt; subscription.unsubscribe();   // unmount cleanup
  }, [userId]);
  // Re-runs when userId changes: cleans up old subscription, sets up new one
}

// === DOM measurement (layout phase, before paint) ===
function MeasureBox() {
  const ref = useRef(null);
  const [size, setSize] = useState(null);

  useLayoutEffect(() =&gt; {
    const { width, height } = ref.current.getBoundingClientRect();
    setSize({ width, height });
  }, []);

  return &lt;div ref={ref}&gt;{size &amp;&amp; `${size.width} × ${size.height}`}&lt;/div&gt;;
}

// === Instance variables (mutable, no re-render on change) ===
function Stopwatch() {
  const intervalRef = useRef(null);
  const [seconds, setSeconds] = useState(0);

  const start = () =&gt; {
    intervalRef.current = setInterval(() =&gt; setSeconds(s =&gt; s + 1), 1000);
  };
  const stop = () =&gt; clearInterval(intervalRef.current);

  useEffect(() =&gt; () =&gt; clearInterval(intervalRef.current), []);   // cleanup on unmount

  return &lt;&gt;&lt;p&gt;{seconds}s&lt;/p&gt;&lt;button onClick={start}&gt;Start&lt;/button&gt;&lt;button onClick={stop}&gt;Stop&lt;/button&gt;&lt;/&gt;;
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pitfall</th><th>Fix</th></tr>
  <tr><td>Stale closures</td><td>Use updater form (<code>setX(prev =&gt; ...)</code>) or include the value in deps</td></tr>
  <tr><td>Missing dependencies</td><td>Enable <code>react-hooks/exhaustive-deps</code> ESLint rule &mdash; never silence it</td></tr>
  <tr><td>Effect runs twice (Strict Mode dev)</td><td>That&rsquo;s intentional &mdash; surfaces missing cleanups. Production runs once.</td></tr>
  <tr><td>Effect on every render</td><td>Forgot deps array. <code>useEffect(() =&gt; {})</code> with no array re-runs every render.</td></tr>
  <tr><td>Race conditions in async effects</td><td>AbortController or cancelled flag in cleanup</td></tr>
</table>

<p><strong>The synchronization model</strong>: <code>useEffect(setup, deps)</code> means "ensure setup matches deps; if deps change, clean up the old setup and run a new one." This unifies mount/update/unmount &mdash; one effect, three phases automatically. <strong>For error boundaries</strong>, classes are still required (no hook yet); use <code>react-error-boundary</code> for the friendliest API. Otherwise, hooks fully replace lifecycle methods in 2026 codebases.</p>
'''

ANSWERS[30] = r'''
<p><strong>Situation:</strong> the app needs different config per environment (development, staging, production) &mdash; API URLs, feature flags, third-party keys. The pattern: env files committed for dev/staging defaults, secrets injected at build time, prefixes to control client exposure.</p>

<p><strong>Approach:</strong> <code>.env</code> files with build-tool prefix (<code>VITE_</code>, <code>NEXT_PUBLIC_</code>). Variables WITHOUT the prefix stay server-only. Production secrets come from the host&rsquo;s dashboard (Vercel, Netlify, AWS), never committed.</p>

<pre><code># .env (committed defaults)
VITE_APP_NAME=My App
VITE_API_URL=http://localhost:3000

# .env.development (committed; loaded with npm run dev)
VITE_API_URL=http://localhost:3000

# .env.production (committed; loaded with npm run build)
VITE_API_URL=https://api.example.com

# .env.local (gitignored; personal overrides)
VITE_API_URL=http://192.168.1.5:3000</code></pre>

<pre><code>// Access in code
const apiUrl = import.meta.env.VITE_API_URL;
console.log(import.meta.env.MODE);    // "development" | "production"
console.log(import.meta.env.DEV);     // true in dev
console.log(import.meta.env.PROD);    // true in prod

// Validate on startup — fail fast if config is wrong
import { z } from "zod";

const envSchema = z.object({
  VITE_API_URL: z.string().url(),
  VITE_STRIPE_PUBLIC_KEY: z.string().regex(/^pk_(test|live)_/),
  VITE_SENTRY_DSN: z.string().url().optional()
});

const env = envSchema.parse(import.meta.env);
export default env;   // typed, validated config

// TypeScript autocomplete
// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_STRIPE_PUBLIC_KEY: string;
  readonly VITE_SENTRY_DSN: string;
}</code></pre>

<p><strong>Trade-offs &mdash; the security boundary:</strong></p>

<table>
  <tr><th>Safe to expose (client-side)</th><th>Server-only (no prefix)</th></tr>
  <tr><td>Public API base URL</td><td>Database password</td></tr>
  <tr><td>Stripe publishable key (<code>pk_*</code>)</td><td>Stripe secret key (<code>sk_*</code>)</td></tr>
  <tr><td>Google Analytics ID</td><td>JWT signing secret</td></tr>
  <tr><td>Feature flag identifiers</td><td>OAuth client secrets</td></tr>
  <tr><td>Public Firebase config</td><td>Service account credentials</td></tr>
</table>

<p>The bundler bakes <code>import.meta.env.VITE_*</code> into the JS bundle as literal strings &mdash; anything with the prefix ends up visible to users. Don&rsquo;t name a server secret with <code>VITE_</code>.</p>

<p><strong>Build-time vs runtime:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Same image, different envs</td><td>Build-time vars don&rsquo;t support this; need runtime config (see below)</td></tr>
  <tr><td>Runtime config without rebuild</td><td>Server endpoint <code>/api/config</code> the app fetches on startup</td></tr>
  <tr><td>Feature flags</td><td>Don&rsquo;t use env vars &mdash; use LaunchDarkly, Statsig, or a lightweight self-hosted flag service</td></tr>
  <tr><td>Per-environment secrets in CI</td><td>Vercel/Netlify/GitHub Actions encrypted env vars; injected at build</td></tr>
  <tr><td>Forgotten env var on deploy</td><td>Schema validation throws on missing values &mdash; deployment fails fast instead of crashing later</td></tr>
</table>

<p><strong>For Next.js</strong>: prefix with <code>NEXT_PUBLIC_</code> for client; no prefix for server-only (Server Components, API routes, middleware). Don&rsquo;t access server-only env in Client Components &mdash; you&rsquo;ll get <code>undefined</code> in the browser. <strong>For monorepos</strong> (Turborepo, Nx): <code>turbo.json</code>&rsquo;s <code>globalEnv</code> declares which vars affect builds &mdash; cache invalidates correctly when vars change.</p>
'''

ANSWERS[31] = r'''
<p><strong>Situation:</strong> the app fetches data in many components (user lists, products, etc.). Repeating <code>useState</code>+<code>useEffect</code>+fetch+abort+error boilerplate everywhere is wasteful. A custom hook centralizes the pattern.</p>

<p><strong>Approach:</strong> roll a <code>useFetch</code> hook for understanding (the boilerplate it eliminates is the lesson). For production, use <strong>TanStack Query</strong> &mdash; it provides cache, deduplication, refetch on focus, retry, stale-while-revalidate &mdash; all of which matter and none of which a roll-your-own hook does.</p>

<pre><code>// useFetch.ts — the pedagogical version
import { useState, useEffect, useCallback } from "react";

export function useFetch&lt;T&gt;(url: string | null, options?: RequestInit) {
  const [data, setData] = useState&lt;T | null&gt;(null);
  const [error, setError] = useState&lt;string | null&gt;(null);
  const [loading, setLoading] = useState(false);
  const [refetchKey, setRefetchKey] = useState(0);

  const refetch = useCallback(() =&gt; setRefetchKey(k =&gt; k + 1), []);

  useEffect(() =&gt; {
    if (!url) return;

    const ctrl = new AbortController();
    setLoading(true);
    setError(null);

    fetch(url, { ...options, signal: ctrl.signal })
      .then(r =&gt; {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise&lt;T&gt;;
      })
      .then(setData)
      .catch(e =&gt; {
        if (e.name !== "AbortError") setError(e.message);
      })
      .finally(() =&gt; setLoading(false));

    return () =&gt; ctrl.abort();
  }, [url, refetchKey]);

  return { data, error, loading, refetch };
}

// Usage
function UserProfile({ id }) {
  const { data: user, error, loading, refetch } = useFetch&lt;User&gt;(`/api/users/${id}`);

  if (loading) return &lt;p&gt;Loading...&lt;/p&gt;;
  if (error)   return &lt;&gt;&lt;p&gt;{error}&lt;/p&gt;&lt;button onClick={refetch}&gt;Retry&lt;/button&gt;&lt;/&gt;;
  return &lt;h1&gt;{user?.name}&lt;/h1&gt;;
}</code></pre>

<p><strong>The TanStack Query equivalent &mdash; what production looks like:</strong></p>

<pre><code>import { useQuery } from "@tanstack/react-query";

function UserProfile({ id }) {
  const { data: user, error, isPending, refetch } = useQuery({
    queryKey: ["users", id],
    queryFn: ({ signal }) =&gt; fetch(`/api/users/${id}`, { signal }).then(r =&gt; r.json()),
    staleTime: 60_000,           // fresh for 60s
    retry: 2                      // auto-retry on transient failure
  });

  if (isPending) return &lt;p&gt;Loading...&lt;/p&gt;;
  if (error)     return &lt;&gt;&lt;p&gt;{error.message}&lt;/p&gt;&lt;button onClick={() =&gt; refetch()}&gt;Retry&lt;/button&gt;&lt;/&gt;;
  return &lt;h1&gt;{user.name}&lt;/h1&gt;;
}</code></pre>

<p><strong>Trade-offs &mdash; what roll-your-own misses:</strong></p>

<table>
  <tr><th>Feature</th><th>Roll-your-own</th><th>TanStack Query</th></tr>
  <tr><td>Cache across components</td><td>No (each call refetches)</td><td>Yes (shared cache by query key)</td></tr>
  <tr><td>Request deduplication</td><td>No (5 components = 5 fetches)</td><td>Yes (1 fetch shared)</td></tr>
  <tr><td>Refetch on window focus</td><td>No</td><td>Yes (configurable)</td></tr>
  <tr><td>Auto-retry on failure</td><td>No</td><td>Yes (with exponential backoff)</td></tr>
  <tr><td>Stale-while-revalidate</td><td>No</td><td>Yes (show stale, refetch in background)</td></tr>
  <tr><td>Optimistic updates</td><td>Manual</td><td>Built-in mutation API</td></tr>
  <tr><td>Pagination / infinite scroll</td><td>Manual</td><td><code>useInfiniteQuery</code></td></tr>
  <tr><td>Cache invalidation</td><td>Manual</td><td><code>queryClient.invalidateQueries</code></td></tr>
  <tr><td>DevTools</td><td>None</td><td>Excellent</td></tr>
</table>

<p><strong>When roll-your-own is correct:</strong> a tiny app where you literally fetch one or two endpoints and don&rsquo;t care about cache. <strong>When TanStack Query is correct:</strong> any app with more than a handful of endpoints, or any app where stale data, refetch behavior, or cache invalidation matters. <strong>SWR</strong> is similar (smaller, slightly less feature-rich); pick either &mdash; both are excellent.</p>
'''

ANSWERS[32] = r'''
<p><strong>Situation:</strong> the API returns paginated data (page 1 of 50). Users navigate via Prev/Next buttons or page numbers. Implementation must keep URL synced (<code>?page=3</code> shareable), preserve scroll position, prefetch next page for instant feel.</p>

<p><strong>Approach:</strong> use TanStack Query with <code>keepPreviousData</code> for smooth transitions + <code>useSearchParams</code> for URL state. Server returns <code>{ items, total, page, pageSize }</code>; UI computes total pages and disabled states.</p>

<pre><code>import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";

const PAGE_SIZE = 20;

function PaginatedProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get("page") ?? 1);

  const { data, isPending, isFetching, isPlaceholderData } = useQuery({
    queryKey: ["products", page],
    queryFn: () =&gt;
      fetch(`/api/products?page=${page}&amp;pageSize=${PAGE_SIZE}`).then(r =&gt; r.json()),
    placeholderData: keepPreviousData,    // keep showing previous page while next loads
    staleTime: 30_000
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  const goTo = (newPage: number) =&gt; {
    setSearchParams({ page: String(newPage) });
    window.scrollTo({ top: 0 });
  };

  // Prefetch the next page when current page is loaded
  const queryClient = useQueryClient();
  useEffect(() =&gt; {
    if (page &lt; totalPages) {
      queryClient.prefetchQuery({
        queryKey: ["products", page + 1],
        queryFn: () =&gt; fetch(`/api/products?page=${page + 1}&amp;pageSize=${PAGE_SIZE}`).then(r =&gt; r.json())
      });
    }
  }, [page, totalPages, queryClient]);

  if (isPending) return &lt;p&gt;Loading...&lt;/p&gt;;

  return (
    &lt;&gt;
      {isFetching &amp;&amp; isPlaceholderData &amp;&amp; (
        &lt;div className="loading-strip" /&gt;     /* subtle indicator without flashing */
      )}

      &lt;ul&gt;
        {data.items.map(p =&gt; (
          &lt;li key={p.id}&gt;{p.name}&lt;/li&gt;
        ))}
      &lt;/ul&gt;

      &lt;nav aria-label="Pagination"&gt;
        &lt;button onClick={() =&gt; goTo(1)} disabled={page === 1}&gt;« First&lt;/button&gt;
        &lt;button onClick={() =&gt; goTo(page - 1)} disabled={page === 1}&gt;‹ Prev&lt;/button&gt;
        &lt;span&gt;Page {page} of {totalPages}&lt;/span&gt;
        &lt;button onClick={() =&gt; goTo(page + 1)} disabled={page === totalPages}&gt;Next ›&lt;/button&gt;
        &lt;button onClick={() =&gt; goTo(totalPages)} disabled={page === totalPages}&gt;Last »&lt;/button&gt;
      &lt;/nav&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Flashing on page change</td><td><code>keepPreviousData</code> &mdash; old page stays visible during fetch</td></tr>
  <tr><td>URL not shareable</td><td>Sync to <code>?page=N</code> with <code>useSearchParams</code></td></tr>
  <tr><td>Scroll position retention</td><td>Reset scroll on page change; preserve list scroll between renders</td></tr>
  <tr><td>Slow next page</td><td>Prefetch next page in background &mdash; click feels instant</td></tr>
  <tr><td>User on page 5, total drops to 3</td><td>Server returns empty; redirect to last valid page</td></tr>
  <tr><td>Page numbers vs cursor</td><td>Page numbers OK for stable datasets; cursor (after_id, before_id) for streams that change</td></tr>
  <tr><td>Filters + pagination</td><td>Reset to page 1 when filters change &mdash; otherwise out-of-bounds page</td></tr>
</table>

<p><strong>Page numbers vs cursor pagination:</strong></p>

<table>
  <tr><th></th><th>Page numbers</th><th>Cursor (after_id)</th></tr>
  <tr><td>Best for</td><td>Stable datasets, jump-to-page, total count needed</td><td>Real-time feeds, infinite scroll, large datasets</td></tr>
  <tr><td>Stability</td><td>Items can shift between pages (insert at start moves item 20 → 21)</td><td>Stable: cursor anchors position</td></tr>
  <tr><td>Database cost</td><td><code>OFFSET 1000 LIMIT 20</code> scans 1000 rows &mdash; expensive at large offsets</td><td><code>WHERE id &gt; cursor LIMIT 20</code> &mdash; constant time with index</td></tr>
  <tr><td>Total count</td><td>Available</td><td>Usually approximate or omitted</td></tr>
</table>

<p><strong>For social feeds and large datasets, prefer cursor pagination</strong>. For admin dashboards where users want page 47, page numbers are fine. <strong>Don&rsquo;t mix</strong>: use one approach consistently per endpoint.</p>
'''

ANSWERS[33] = r'''
<p><strong>Situation:</strong> the app has noticeable lag when typing, scrolling, or interacting. React DevTools Profiler shows many components re-rendering on every state change &mdash; even ones whose data hasn&rsquo;t changed. Goal: cut wasteful re-renders while keeping code readable.</p>

<p><strong>Approach:</strong> profile first to identify actual hotspots; apply targeted fixes (state placement, memoization, list virtualization, lifting computation out of render). Don&rsquo;t pre-optimize everything &mdash; most of the codebase doesn&rsquo;t need it.</p>

<p><strong>Diagnostic process:</strong></p>

<ol>
  <li>Open <strong>React DevTools Profiler</strong>. Record an interaction. Look at the flamegraph.</li>
  <li>Sort by &ldquo;Render time&rdquo;. The expensive components are at top.</li>
  <li>Click the component. The right pane shows &ldquo;Why did this render?&rdquo; (props that changed).</li>
  <li>If a component renders with no real change, its props/context aren&rsquo;t stable.</li>
</ol>

<p><strong>Six fixes by symptom:</strong></p>

<table>
  <tr><th>Symptom</th><th>Fix</th></tr>
  <tr><td>Whole tree re-renders on typing</td><td>State is too high &mdash; move it down to where it&rsquo;s used. Or split components.</td></tr>
  <tr><td>Memoized child still re-renders</td><td>Parent passes new object/array each render &mdash; wrap with useMemo, or move outside</td></tr>
  <tr><td>Memoized child re-renders on callback prop</td><td>Wrap callback with useCallback</td></tr>
  <tr><td>List of 1000+ items slow to render</td><td>Virtualize with TanStack Virtual or react-window</td></tr>
  <tr><td>Expensive calculation runs every render</td><td><code>useMemo</code> with proper deps</td></tr>
  <tr><td>Context update re-renders unrelated consumers</td><td>Split contexts or migrate to Zustand with selectors</td></tr>
</table>

<pre><code>// Before — entire app re-renders when input changes
function App() {
  const [search, setSearch] = useState("");
  return (
    &lt;&gt;
      &lt;input value={search} onChange={e =&gt; setSearch(e.target.value)} /&gt;
      &lt;ExpensiveDashboard /&gt;       {/* re-renders every keystroke! */}
      &lt;ResultsList query={search} /&gt;
    &lt;/&gt;
  );
}

// After — search state is local to where it&rsquo;s used
function App() {
  return (
    &lt;&gt;
      &lt;ExpensiveDashboard /&gt;
      &lt;SearchSection /&gt;            {/* search state lives here */}
    &lt;/&gt;
  );
}

function SearchSection() {
  const [search, setSearch] = useState("");
  return (
    &lt;&gt;
      &lt;input value={search} onChange={e =&gt; setSearch(e.target.value)} /&gt;
      &lt;ResultsList query={search} /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>List virtualization (the biggest single fix for big-list apps):</strong></p>

<pre><code>import { useVirtualizer } from "@tanstack/react-virtual";

function VirtualList({ items }) {
  const parentRef = useRef(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () =&gt; parentRef.current,
    estimateSize: () =&gt; 50,
    overscan: 5
  });

  return (
    &lt;div ref={parentRef} style={{ height: 600, overflow: "auto" }}&gt;
      &lt;div style={{ height: virtualizer.getTotalSize(), position: "relative" }}&gt;
        {virtualizer.getVirtualItems().map(v =&gt; (
          &lt;div key={v.key} style={{
            position: "absolute", top: 0, transform: `translateY(${v.start}px)`,
            height: v.size, width: "100%"
          }}&gt;
            {items[v.index].name}
          &lt;/div&gt;
        ))}
      &lt;/div&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Tactic</th><th>When to apply</th></tr>
  <tr><td>Move state down</td><td>Always &mdash; first thing to try</td></tr>
  <tr><td>useMemo / useCallback</td><td>When passing to memoized children, or actual expensive computation</td></tr>
  <tr><td>React.memo</td><td>Component renders often with stable props</td></tr>
  <tr><td>Virtualization</td><td>Lists &gt; 100 items, especially heavy items</td></tr>
  <tr><td>useTransition / useDeferredValue</td><td>Expensive renders that shouldn&rsquo;t block input</td></tr>
  <tr><td>Code splitting</td><td>Large feature areas not used on first page load</td></tr>
</table>

<p><strong>2026 reality with React Compiler:</strong> auto-applies memoization where beneficial &mdash; many manual fixes become unnecessary. State placement still matters; virtualization still required for big lists. <strong>Don&rsquo;t memoize everything &ldquo;to be safe&rdquo;</strong> &mdash; that adds bookkeeping overhead with no benefit and obscures which components actually needed it. Profile, identify, fix; rinse and repeat.</p>
'''

ANSWERS[34] = r'''
<p><strong>Situation:</strong> the app has hierarchical pages: <code>/dashboard</code> with sub-pages <code>/dashboard/users</code>, <code>/dashboard/users/:id</code>, <code>/dashboard/settings</code>. Each level shares chrome (sidebar, breadcrumbs). Hard-coding layout in every page leads to duplication and bugs.</p>

<p><strong>Approach:</strong> use React Router&rsquo;s nested routes with <code>&lt;Outlet /&gt;</code>. Parent layout renders shared chrome and an <code>&lt;Outlet /&gt;</code> placeholder; matching child route fills in. URL structure mirrors UI hierarchy. With v6.4+ data routers, add per-route loaders for parallel data fetching.</p>

<pre><code>import { createBrowserRouter, RouterProvider, Outlet, NavLink, useLoaderData } from "react-router-dom";

// === Layout components ===
function DashboardLayout() {
  return (
    &lt;div className="dashboard"&gt;
      &lt;aside&gt;
        &lt;NavLink to="/dashboard"&gt;Overview&lt;/NavLink&gt;
        &lt;NavLink to="/dashboard/users"&gt;Users&lt;/NavLink&gt;
        &lt;NavLink to="/dashboard/settings"&gt;Settings&lt;/NavLink&gt;
      &lt;/aside&gt;
      &lt;main&gt;
        &lt;Outlet /&gt;     {/* nested route renders here */}
      &lt;/main&gt;
    &lt;/div&gt;
  );
}

function UsersLayout() {
  return (
    &lt;div&gt;
      &lt;h2&gt;Users&lt;/h2&gt;
      &lt;Outlet /&gt;     {/* /users (list) or /users/:id (detail) */}
    &lt;/div&gt;
  );
}

// === Page components ===
function DashboardHome()  { return &lt;p&gt;Welcome to the dashboard&lt;/p&gt;; }
function UsersList()       { const { users } = useLoaderData(); return &lt;ul&gt;{users.map(u =&gt; &lt;li key={u.id}&gt;{u.name}&lt;/li&gt;)}&lt;/ul&gt;; }
function UserDetail()      { const { user } = useLoaderData(); return &lt;h3&gt;{user.name}&lt;/h3&gt;; }

// === Router config with nested routes + loaders ===
const router = createBrowserRouter([
  {
    path: "/dashboard",
    element: &lt;DashboardLayout /&gt;,
    loader: async () =&gt; ({ user: await fetchCurrentUser() }),
    errorElement: &lt;ErrorPage /&gt;,
    children: [
      { index: true, element: &lt;DashboardHome /&gt; },

      {
        path: "users",
        element: &lt;UsersLayout /&gt;,
        children: [
          {
            index: true,
            element: &lt;UsersList /&gt;,
            loader: async () =&gt; ({ users: await api.getUsers() })
          },
          {
            path: ":userId",
            element: &lt;UserDetail /&gt;,
            loader: async ({ params }) =&gt; ({ user: await api.getUser(params.userId) })
          }
        ]
      },

      { path: "settings", element: &lt;Settings /&gt; }
    ]
  }
]);

function App() {
  return &lt;RouterProvider router={router} /&gt;;
}</code></pre>

<p><strong>How URLs map to rendering:</strong></p>

<table>
  <tr><th>URL</th><th>Renders</th></tr>
  <tr><td><code>/dashboard</code></td><td>DashboardLayout + DashboardHome (index)</td></tr>
  <tr><td><code>/dashboard/users</code></td><td>DashboardLayout + UsersLayout + UsersList (index)</td></tr>
  <tr><td><code>/dashboard/users/42</code></td><td>DashboardLayout + UsersLayout + UserDetail</td></tr>
  <tr><td><code>/dashboard/settings</code></td><td>DashboardLayout + Settings</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Fetching cascades</td><td>v6.4+ loaders run in parallel for nested routes &mdash; not waterfalled</td></tr>
  <tr><td>Auth on protected routes</td><td>Throw <code>redirect("/login")</code> from loader; happens before render</td></tr>
  <tr><td>Layout state preserved across nav</td><td>DashboardLayout doesn&rsquo;t unmount when going /users → /settings &mdash; sidebar scroll, etc. preserved</td></tr>
  <tr><td>Lazy-loaded nested routes</td><td><code>lazy: () =&gt; import("./Settings")</code> in route config</td></tr>
  <tr><td>404 within section</td><td>Add <code>{ path: "*", element: &lt;NotFound /&gt; }</code> as last child</td></tr>
  <tr><td>Forgot <code>&lt;Outlet /&gt;</code></td><td>Nothing renders &mdash; classic gotcha</td></tr>
</table>

<p><strong>For Next.js (App Router)</strong>: the same pattern is file-system-based. Folders define routes; <code>layout.tsx</code> per folder is the layout; <code>page.tsx</code> is the leaf; <code>loading.tsx</code> and <code>error.tsx</code> handle states. Server-side by default, with streaming. The mental model is identical &mdash; just expressed via the file system instead of route config.</p>
'''

ANSWERS[35] = r'''
<p><strong>Situation:</strong> the app has a search input that suggests results as the user types &mdash; like Google&rsquo;s search box. Suggestions update on each keystroke, fetched from a server-side endpoint. UI must stay responsive (no laggy input), avoid hammering the API, and handle keyboard navigation (arrow keys + Enter).</p>

<p><strong>Approach:</strong> debounce input → fetch with TanStack Query → render suggestions list → handle keyboard nav. Cancel in-flight requests when input changes. <code>placeholderData: keepPreviousData</code> keeps suggestions visible during refetch.</p>

<pre><code>import { useState, useEffect, useRef } from "react";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";

function Typeahead() {
  const [query, setQuery] = useState("");
  const [debouncedQuery] = useDebounce(query, 250);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [open, setOpen] = useState(false);

  const { data: suggestions = [], isFetching } = useQuery({
    queryKey: ["typeahead", debouncedQuery],
    queryFn: ({ signal }) =&gt;
      fetch(`/api/suggest?q=${encodeURIComponent(debouncedQuery)}`, { signal })
        .then(r =&gt; r.json()),
    enabled: debouncedQuery.length &gt;= 2,
    placeholderData: keepPreviousData,
    staleTime: 60_000
  });

  const handleKeyDown = (e) =&gt; {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex(i =&gt; Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex(i =&gt; Math.max(i - 1, -1));
    } else if (e.key === "Enter" &amp;&amp; activeIndex &gt;= 0) {
      e.preventDefault();
      handleSelect(suggestions[activeIndex]);
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  const handleSelect = (item) =&gt; {
    setQuery(item.name);
    setOpen(false);
    onSelect(item);   // do something with the choice
  };

  return (
    &lt;div className="typeahead" role="combobox" aria-expanded={open}
         aria-controls="typeahead-list" aria-haspopup="listbox"&gt;
      &lt;input
        type="search"
        value={query}
        onChange={e =&gt; { setQuery(e.target.value); setOpen(true); setActiveIndex(-1); }}
        onKeyDown={handleKeyDown}
        onFocus={() =&gt; setOpen(true)}
        onBlur={() =&gt; setTimeout(() =&gt; setOpen(false), 150)}
        aria-autocomplete="list"
        aria-activedescendant={activeIndex &gt;= 0 ? `option-${activeIndex}` : undefined}
        placeholder="Search..."
      /&gt;

      {isFetching &amp;&amp; &lt;Spinner /&gt;}

      {open &amp;&amp; suggestions.length &gt; 0 &amp;&amp; (
        &lt;ul id="typeahead-list" role="listbox"&gt;
          {suggestions.map((s, i) =&gt; (
            &lt;li
              key={s.id}
              id={`option-${i}`}
              role="option"
              aria-selected={i === activeIndex}
              onMouseDown={() =&gt; handleSelect(s)}      /* mousedown beats blur */
              className={i === activeIndex ? "active" : ""}
            &gt;
              {s.name}
            &lt;/li&gt;
          ))}
        &lt;/ul&gt;
      )}

      {open &amp;&amp; debouncedQuery.length &gt;= 2 &amp;&amp; suggestions.length === 0 &amp;&amp; !isFetching &amp;&amp; (
        &lt;p&gt;No results for &ldquo;{debouncedQuery}&rdquo;&lt;/p&gt;
      )}
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Hammering API on every keystroke</td><td>Debounce 200-300ms (sweet spot for typing)</td></tr>
  <tr><td>Stale results after fast typing</td><td>TanStack Query auto-cancels obsolete requests via signal</td></tr>
  <tr><td>Flicker between requests</td><td><code>keepPreviousData</code> &mdash; smooth experience</td></tr>
  <tr><td>Click on suggestion vs blur</td><td><code>onMouseDown</code> fires before blur; <code>onClick</code> fires after blur (blur closes the list, click never lands)</td></tr>
  <tr><td>Keyboard accessibility</td><td>Full ARIA combobox pattern: <code>role="combobox"</code>, <code>aria-activedescendant</code>, <code>role="listbox"</code>/<code>option</code></td></tr>
  <tr><td>Empty/short queries</td><td>Don&rsquo;t fetch &mdash; <code>enabled: query.length &gt;= 2</code></td></tr>
</table>

<p><strong>For production-grade typeahead</strong>: use <strong>Headless UI Combobox</strong>, <strong>Radix Combobox</strong>, <strong>shadcn/ui Combobox</strong>, or <strong>Downshift</strong>. ARIA combobox is one of the trickiest patterns &mdash; libraries get it right. <strong>For very fast typeahead at scale</strong>, use <strong>Algolia</strong> or <strong>Meilisearch</strong> &mdash; sub-50ms responses with typo tolerance, ranking, faceting. Roll-your-own for the learning experience; ship libraries for production.</p>
'''

ANSWERS[36] = r'''
<p><strong>Situation:</strong> the app needs many buttons across many features &mdash; primary, secondary, danger, ghost; small, medium, large; with optional icons, loading states, full-width variants. Without a reusable component, you get inconsistent styles and dozens of one-off buttons.</p>

<p><strong>Approach:</strong> a single <code>&lt;Button&gt;</code> with <code>variant</code> + <code>size</code> + state props, polymorphism via <code>asChild</code> for rendering as <code>&lt;a&gt;</code> or <code>&lt;Link&gt;</code>, type-safe variants via <code>cva</code> (class-variance-authority). This is exactly the shadcn/ui pattern &mdash; production-ready primitives.</p>

<pre><code>// Button.tsx
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "@radix-ui/react-slot";
import { forwardRef } from "react";

const buttonVariants = cva(
  // base — always applied
  "inline-flex items-center justify-center gap-2 rounded font-medium transition-colors " +
  "disabled:opacity-50 disabled:pointer-events-none focus-visible:ring-2 focus-visible:ring-offset-2",
  {
    variants: {
      variant: {
        primary:   "bg-blue-600 text-white hover:bg-blue-700",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
        danger:    "bg-red-600 text-white hover:bg-red-700",
        ghost:     "hover:bg-gray-100"
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg"
      },
      fullWidth: {
        true: "w-full"
      }
    },
    defaultVariants: { variant: "primary", size: "md" }
  }
);

type ButtonProps = React.ButtonHTMLAttributes&lt;HTMLButtonElement&gt;
  &amp; VariantProps&lt;typeof buttonVariants&gt;
  &amp; { asChild?: boolean; loading?: boolean; icon?: React.ReactNode };

export const Button = forwardRef&lt;HTMLButtonElement, ButtonProps&gt;(
  ({ variant, size, fullWidth, asChild, loading, icon, children, disabled, className, ...props }, ref) =&gt; {
    const Comp = asChild ? Slot : "button";

    return (
      &lt;Comp
        ref={ref}
        className={`${buttonVariants({ variant, size, fullWidth })} ${className ?? ""}`}
        disabled={disabled || loading}
        {...props}
      &gt;
        {loading ? &lt;Spinner size={size} /&gt; : icon}
        {children}
      &lt;/Comp&gt;
    );
  }
);
Button.displayName = "Button";</code></pre>

<pre><code>// Usage
&lt;Button&gt;Save&lt;/Button&gt;                                    {/* primary md */}
&lt;Button variant="danger" size="sm"&gt;Delete&lt;/Button&gt;
&lt;Button variant="secondary" icon={&lt;PlusIcon /&gt;}&gt;Add&lt;/Button&gt;
&lt;Button loading&gt;Saving...&lt;/Button&gt;
&lt;Button fullWidth&gt;Continue&lt;/Button&gt;

{/* Render as a link instead of button */}
&lt;Button asChild variant="ghost"&gt;
  &lt;Link to="/about"&gt;About&lt;/Link&gt;
&lt;/Button&gt;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th></tr>
  <tr><td><code>asChild</code> via Slot</td><td>Same styling, different element (<code>&lt;a&gt;</code>, <code>&lt;Link&gt;</code>, <code>&lt;NavLink&gt;</code>) without prop forwarding gymnastics</td></tr>
  <tr><td><code>cva</code> for variants</td><td>Type-safe variant API; autocomplete; one source of truth for class strings</td></tr>
  <tr><td><code>forwardRef</code></td><td>Letting consumers attach refs (focus management, scroll-into-view)</td></tr>
  <tr><td>Loading replaces icon</td><td>Spinner where icon was &mdash; consistent layout</td></tr>
  <tr><td><code>disabled || loading</code></td><td>Loading buttons can&rsquo;t be clicked; disabled visually too</td></tr>
  <tr><td>Spreading <code>...props</code></td><td>All native button attrs work: type, name, form, aria-*</td></tr>
</table>

<p><strong>Common variants beyond this:</strong> compound buttons (icon + label), button groups (Toolbar), split buttons (action + dropdown), loading with progress (file upload). Each is a small extension of this pattern.</p>

<p><strong>Don&rsquo;t reinvent for production.</strong> <strong>shadcn/ui Button</strong> is exactly this pattern &mdash; copy it into your project and customize. <strong>Radix UI</strong> provides unstyled accessible primitives. <strong>Mantine</strong>, <strong>Chakra UI</strong>, <strong>Mui</strong> bundle complete design systems. The only reason to roll your own is design uniqueness; even then, start from a primitive and customize. The accessibility plumbing (focus rings, disabled handling, asChild slotting) is the value &mdash; not the styling.</p>
'''

ANSWERS[37] = r'''
<p><strong>Situation:</strong> a countdown timer counts down to a target date or duration, updating every second, displaying days/hours/minutes/seconds. When zero, fires a callback. Common uses: launch countdowns, sale timers, exam timers, OTP expiry indicators.</p>

<p><strong>Approach:</strong> use <code>setInterval</code> in <code>useEffect</code> with cleanup. Re-compute time-left on each tick from the current timestamp &mdash; not by decrementing state &mdash; so it stays accurate even if the tab was backgrounded (browsers throttle <code>setInterval</code> to 1/min when hidden). Return tick cleanup on unmount.</p>

<pre><code>import { useState, useEffect, useCallback } from "react";

type Duration = { days: number; hours: number; mins: number; secs: number; total: number };

function calc(target: Date | number): Duration {
  const total = +new Date(target) - Date.now();
  if (total &lt;= 0) return { total: 0, days: 0, hours: 0, mins: 0, secs: 0 };
  return {
    total,
    days:  Math.floor(total / 86_400_000),
    hours: Math.floor(total / 3_600_000) % 24,
    mins:  Math.floor(total / 60_000) % 60,
    secs:  Math.floor(total / 1_000) % 60
  };
}

function Countdown({ targetDate, onComplete }: { targetDate: Date; onComplete?: () =&gt; void }) {
  const [time, setTime] = useState(() =&gt; calc(targetDate));

  useEffect(() =&gt; {
    if (time.total &lt;= 0) return;

    const id = setInterval(() =&gt; {
      const next = calc(targetDate);
      setTime(next);
      if (next.total &lt;= 0) {
        clearInterval(id);
        onComplete?.();
      }
    }, 1000);

    return () =&gt; clearInterval(id);
  }, [targetDate, onComplete, time.total]);

  if (time.total &lt;= 0) return &lt;p&gt;Time&rsquo;s up!&lt;/p&gt;;

  const pad = (n: number) =&gt; String(n).padStart(2, "0");

  return (
    &lt;div className="countdown" aria-live="polite"&gt;
      &lt;span&gt;&lt;strong&gt;{pad(time.days)}&lt;/strong&gt; days&lt;/span&gt;
      &lt;span&gt;&lt;strong&gt;{pad(time.hours)}&lt;/strong&gt; hours&lt;/span&gt;
      &lt;span&gt;&lt;strong&gt;{pad(time.mins)}&lt;/strong&gt; min&lt;/span&gt;
      &lt;span&gt;&lt;strong&gt;{pad(time.secs)}&lt;/strong&gt; sec&lt;/span&gt;
    &lt;/div&gt;
  );
}

// Usage
&lt;Countdown
  targetDate={new Date("2026-12-31T23:59:59")}
  onComplete={() =&gt; alert("Happy new year!")}
/&gt;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Background-tab drift</td><td>Compute from <code>Date.now()</code> each tick &mdash; not <code>seconds--</code>. Re-syncs on visibility.</td></tr>
  <tr><td>Refresh resilience</td><td>Pass an absolute target date; survives reloads. Don&rsquo;t store remaining seconds.</td></tr>
  <tr><td>Server vs client clock skew</td><td>Send target ISO from server; <code>Date.now()</code> on client may differ &mdash; sync with a server time endpoint if precision matters</td></tr>
  <tr><td>1-second update vs animation</td><td>For sub-second visual updates (animation), use <code>requestAnimationFrame</code> instead</td></tr>
  <tr><td>Tab inactive throttling</td><td>Browsers throttle background <code>setInterval</code> to 1/min &mdash; recompute pattern handles this; you&rsquo;ll just see a jump on focus</td></tr>
  <tr><td>OTP expiry case (short countdown)</td><td>1-second tick is fine; for &lt;5 sec countdowns, 100ms tick gives smoother UX</td></tr>
</table>

<p><strong>For complex needs</strong>: <strong>react-countdown</strong> handles edge cases (auto-start, completed callback, custom renderer, onTick). <strong>For game timers / animations</strong>, use <code>requestAnimationFrame</code> with timestamps &mdash; ~60fps and no <code>setInterval</code> drift. The pattern of computing from current time (not decrementing state) is the key takeaway &mdash; works in every variant.</p>
'''

ANSWERS[38] = r'''
<p><strong>Situation:</strong> the app has multiple user roles (viewer, editor, admin) with permissions: viewers read; editors read+write; admins do everything. UI must hide actions users can&rsquo;t perform; routes must block unauthorized access; API must enforce on the server (UI hiding is UX, not security).</p>

<p><strong>Approach:</strong> permissions as discrete strings (<code>"posts:create"</code>, <code>"users:delete"</code>) attached to the user. Roles are bundles of permissions. UI checks <code>hasPermission(user, perm)</code> for show/hide. Routes use guards. Server independently validates every API call.</p>

<pre><code>// auth/permissions.ts
export type Permission =
  | "posts:read" | "posts:create" | "posts:update" | "posts:delete"
  | "users:read" | "users:update" | "users:delete"
  | "billing:manage";

export const ROLE_PERMISSIONS: Record&lt;string, Permission[]&gt; = {
  viewer: ["posts:read", "users:read"],
  editor: ["posts:read", "posts:create", "posts:update", "users:read"],
  admin:  ["posts:read", "posts:create", "posts:update", "posts:delete",
           "users:read", "users:update", "users:delete", "billing:manage"]
};

export function hasPermission(user: User, perm: Permission): boolean {
  if (!user) return false;
  const granted = ROLE_PERMISSIONS[user.role] ?? [];
  return granted.includes(perm);
}</code></pre>

<pre><code>// hooks/usePermission.ts
import { useAuth } from "./AuthContext";

export function usePermission(perm: Permission) {
  const { user } = useAuth();
  return hasPermission(user, perm);
}

// Components
function Can({ perm, children, fallback = null }) {
  return usePermission(perm) ? children : fallback;
}

// Usage in UI
function PostActions({ post }) {
  return (
    &lt;&gt;
      &lt;Can perm="posts:update"&gt;
        &lt;button&gt;Edit&lt;/button&gt;
      &lt;/Can&gt;
      &lt;Can perm="posts:delete"&gt;
        &lt;button className="danger"&gt;Delete&lt;/button&gt;
      &lt;/Can&gt;
    &lt;/&gt;
  );
}</code></pre>

<pre><code>// Route guards (React Router v6.4+ loader)
const adminLoader = async () =&gt; {
  const user = await getCurrentUser();
  if (!user) throw redirect("/login");
  if (!hasPermission(user, "billing:manage")) throw redirect("/forbidden");
  return user;
};

createBrowserRouter([
  {
    path: "/admin",
    loader: adminLoader,
    element: &lt;AdminPanel /&gt;
  }
]);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Role-based vs permission-based</td><td>Permissions are more flexible. Roles are bundles &mdash; check by permission, not by role name (decouples UI from role definitions)</td></tr>
  <tr><td>Resource ownership (user owns this post)</td><td>Add resource-level checks: <code>canEdit(user, post)</code> &mdash; admin OR <code>post.authorId === user.id</code></td></tr>
  <tr><td>UI vs server enforcement</td><td>UI hiding is UX. Server MUST validate every action independently &mdash; clients can be modified.</td></tr>
  <tr><td>Performance &mdash; many permission checks per render</td><td><code>useMemo</code> the permissions Set; checks become O(1)</td></tr>
  <tr><td>Permission updates without re-login</td><td>Refetch user on focus; show explicit reload toast if role changes</td></tr>
  <tr><td>Hierarchies (admin includes editor)</td><td>Don&rsquo;t inherit by name &mdash; flatten to permission lists</td></tr>
  <tr><td>Multi-tenant (different roles per org)</td><td>Permissions scoped per org/workspace context</td></tr>
</table>

<p><strong>Open-source RBAC libraries</strong>: <strong>CASL</strong> (declarative abilities, conditions on fields), <strong>Permify</strong> (centralized service, Zanzibar-style). <strong>Auth services with built-in RBAC</strong>: Clerk, Auth0, Permit.io. <strong>For complex hierarchies and resource-level rules</strong>, attribute-based access control (ABAC) generalizes RBAC &mdash; rules over user attributes + resource attributes. <strong>Critical reminder</strong>: client checks are optimization for UX. Every protected operation must be re-validated server-side. Don&rsquo;t trust the client.</p>
'''

ANSWERS[39] = r'''
<p><strong>Situation:</strong> the app needs animations &mdash; element entrance/exit, layout transitions, gesture-driven interactions, page transitions. Manual CSS works for simple cases but breaks for entrance/exit animation (element gone before animation finishes), layout animations, and gesture choreography.</p>

<p><strong>Approach:</strong> default to <strong>CSS transitions</strong> for hover/focus/state changes (cheapest, GPU-friendly). Use <strong>Framer Motion</strong> for component entrance/exit, layout animations, gestures. Use <strong>view-transitions API</strong> for page transitions (browser-native).</p>

<pre><code>// === CSS — for hover/focus/simple state changes ===
.button {
  transition: transform 200ms ease, background 150ms;
}
.button:hover {
  transform: translateY(-2px);
  background: #2563eb;
}

// === Framer Motion — entrance/exit ===
import { motion, AnimatePresence } from "framer-motion";

function NotificationList({ notifications }) {
  return (
    &lt;ul&gt;
      &lt;AnimatePresence&gt;
        {notifications.map(n =&gt; (
          &lt;motion.li
            key={n.id}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: 200 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
          &gt;
            {n.message}
          &lt;/motion.li&gt;
        ))}
      &lt;/AnimatePresence&gt;
    &lt;/ul&gt;
  );
}

// === Framer Motion — layout animations (FLIP for free) ===
function Card({ expanded, onClick }) {
  return (
    &lt;motion.div
      layout                                 /* auto-animates layout changes */
      onClick={onClick}
      transition={{ duration: 0.3, type: "spring" }}
      style={{ width: expanded ? 400 : 200, height: expanded ? 400 : 100 }}
    &gt;
      Card content
    &lt;/motion.div&gt;
  );
}

// === Framer Motion — gestures ===
function DraggableCard() {
  return (
    &lt;motion.div
      drag="x"
      dragConstraints={{ left: -100, right: 100 }}
      whileDrag={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    &gt;
      Drag me
    &lt;/motion.div&gt;
  );
}</code></pre>

<p><strong>Page transitions with the View Transitions API:</strong></p>

<pre><code>// Browser-native, no library needed (Chrome 111+, Safari 18+, Firefox via flag)
function navigate(href) {
  if (!document.startViewTransition) {
    location.href = href;
    return;
  }

  document.startViewTransition(() =&gt; {
    location.href = href;     // or React Router navigate
  });
}

/* CSS for the transition */
::view-transition-old(root), ::view-transition-new(root) {
  animation-duration: 250ms;
  animation-timing-function: ease-in-out;
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Tool</th><th>Best for</th><th>Cost</th></tr>
  <tr><td>CSS transitions</td><td>Hover, focus, visible state changes</td><td>Free; can&rsquo;t animate exit</td></tr>
  <tr><td>CSS keyframes</td><td>Looping animations (spinner, shimmer)</td><td>Free; not interactive</td></tr>
  <tr><td>Framer Motion</td><td>Entrance/exit, layout, gestures, orchestration</td><td>~50KB; great DX</td></tr>
  <tr><td>React Spring</td><td>Physics-based animations, fine-grained control</td><td>~25KB; steeper API</td></tr>
  <tr><td>GSAP</td><td>Complex timelines, SVG morphing, scroll-driven</td><td>~70KB+; not React-native</td></tr>
  <tr><td>View Transitions API</td><td>Page-level transitions, shared element morph</td><td>Free; limited browser support</td></tr>
</table>

<p><strong>Performance principles:</strong></p>

<ul>
  <li><strong>Animate <code>transform</code> and <code>opacity</code> only</strong> &mdash; GPU-accelerated, doesn&rsquo;t trigger layout. Animating <code>width</code>/<code>height</code>/<code>top</code> is jank-prone.</li>
  <li><strong>Respect <code>prefers-reduced-motion</code></strong> &mdash; disable or shorten animations for users who request it.</li>
  <li><strong>Don&rsquo;t over-animate</strong> &mdash; pages full of bouncy interactions feel chaotic. Animation should communicate (something appeared, moved, can be dragged), not decorate.</li>
  <li><strong>Test on slow devices</strong> &mdash; what feels smooth on a Mac M3 may be janky on a 3-year-old Android. Chrome DevTools CPU throttling is your friend.</li>
</ul>

<p><strong>2026 default:</strong> CSS for the basics, Framer Motion for the interesting parts, View Transitions API for page-level. Reach for GSAP/React Spring only when those don&rsquo;t fit. Skip Lottie unless you specifically need designer-authored vector animations.</p>
'''

ANSWERS[40] = r'''
<p><strong>Situation:</strong> the app needs unit tests for components and hooks, integration tests for flows, and E2E tests for critical paths. Setup must be fast, debuggable, run on CI, and produce clear failures. The 2026 standard: <strong>Vitest + React Testing Library + MSW + Playwright</strong>.</p>

<p><strong>Approach:</strong> Vitest replaces Jest (faster, native ESM, same API). RTL for component tests (user-centric queries). MSW for API mocks at network layer. Playwright for E2E. <code>userEvent</code> over <code>fireEvent</code> for realistic interactions.</p>

<pre><code>// package.json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test"
  },
  "devDependencies": {
    "vitest": "^2.0.0",
    "@vitest/ui": "^2.0.0",
    "@vitest/coverage-v8": "^2.0.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/user-event": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "msw": "^2.0.0",
    "jsdom": "^24.0.0",
    "@playwright/test": "^1.45.0"
  }
}</code></pre>

<pre><code>// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    globals: true,
    coverage: {
      reporter: ["text", "html", "lcov"],
      exclude: ["**/*.config.*", "**/types.ts", "**/*.d.ts"]
    }
  }
});

// src/test/setup.ts
import "@testing-library/jest-dom/vitest";
import { setupServer } from "msw/node";
import { afterAll, afterEach, beforeAll } from "vitest";

export const server = setupServer();
beforeAll(() =&gt; server.listen({ onUnhandledRequest: "error" }));
afterEach(() =&gt; server.resetHandlers());
afterAll(() =&gt; server.close());</code></pre>

<pre><code>// LoginForm.test.tsx — full component test with API mock
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { server } from "./setup";

it("logs in with valid credentials", async () =&gt; {
  server.use(
    http.post("/api/login", () =&gt; HttpResponse.json({ token: "x", user: { name: "Alice" } }))
  );

  const user = userEvent.setup();
  render(&lt;LoginForm /&gt;);

  await user.type(screen.getByLabelText(/email/i), "alice@example.com");
  await user.type(screen.getByLabelText(/password/i), "secret123");
  await user.click(screen.getByRole("button", { name: /sign in/i }));

  expect(await screen.findByText(/welcome, alice/i)).toBeInTheDocument();
});

it("shows error on bad credentials", async () =&gt; {
  server.use(
    http.post("/api/login", () =&gt; HttpResponse.json({ error: "Invalid" }, { status: 401 }))
  );

  const user = userEvent.setup();
  render(&lt;LoginForm /&gt;);
  await user.type(screen.getByLabelText(/email/i), "x@x.com");
  await user.type(screen.getByLabelText(/password/i), "bad");
  await user.click(screen.getByRole("button", { name: /sign in/i }));

  expect(await screen.findByText(/invalid/i)).toBeInTheDocument();
});</code></pre>

<p><strong>Testing pyramid (2026):</strong></p>

<table>
  <tr><th>Layer</th><th>Volume</th><th>Tools</th><th>Goal</th></tr>
  <tr><td>Unit (pure fns, hooks, reducers)</td><td>Many</td><td>Vitest + renderHook</td><td>Cover edge cases cheaply</td></tr>
  <tr><td>Component (render + interact)</td><td>Many</td><td>Vitest + RTL + MSW</td><td>Verify component contract</td></tr>
  <tr><td>Integration (multi-component flows)</td><td>Some</td><td>Vitest + RTL + MSW</td><td>Verify features work together</td></tr>
  <tr><td>E2E (real browser, real backend)</td><td>Few</td><td>Playwright</td><td>Verify critical paths</td></tr>
</table>

<p><strong>RTL principles &mdash; the difference between robust tests and brittle tests:</strong></p>

<ul>
  <li>Query by accessible role/label/text &mdash; not classes/test-ids. Tests survive refactors.</li>
  <li><code>userEvent</code> over <code>fireEvent</code> &mdash; simulates real keyboard/mouse, not synthetic events.</li>
  <li><code>findBy*</code> for async appearance, <code>queryBy*</code> for &ldquo;should not exist.&rdquo;</li>
  <li>Don&rsquo;t test implementation (which hook, which state). Test what users see.</li>
</ul>

<p><strong>Coverage targets:</strong> aim for ~80% line coverage on business logic; lower OK for pure UI. Coverage isn&rsquo;t the goal &mdash; finding bugs is. Critical paths get E2E even if coverage is high. Skip testing trivial code (one-line components, glue code) &mdash; ROI is poor.</p>
'''

ANSWERS[41] = r'''
<p><strong>Situation:</strong> a multi-section form (profile + address + preferences) has 30+ fields. Naive implementation with <code>useState</code> per field is tedious and slow (every keystroke re-renders the whole form). Validation, dependent fields, and submit handling compound the complexity.</p>

<p><strong>Approach:</strong> use <strong>React Hook Form + Zod</strong> &mdash; uncontrolled inputs (no re-render per keystroke), schema-driven validation, easy server-error mapping. For very large forms, split into sections with their own state and submit independently or coordinate via parent.</p>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  // Profile
  firstName: z.string().min(1, "Required"),
  lastName:  z.string().min(1, "Required"),
  email:     z.string().email("Invalid email"),
  phone:     z.string().regex(/^\+?\d{10,15}$/, "Invalid phone"),

  // Address
  address: z.object({
    line1:   z.string().min(1, "Required"),
    line2:   z.string().optional(),
    city:    z.string().min(1, "Required"),
    state:   z.string().length(2, "Use 2-letter state code"),
    zip:     z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP")
  }),

  // Preferences
  newsletter: z.boolean(),
  notifications: z.array(z.enum(["email", "sms", "push"])),

  // Cross-field rules
  password:        z.string().min(8),
  confirmPassword: z.string()
}).refine(d =&gt; d.password === d.confirmPassword, {
  message: "Passwords don&rsquo;t match",
  path: ["confirmPassword"]
});

type FormValues = z.infer&lt;typeof schema&gt;;

function LargeForm({ initial }: { initial?: Partial&lt;FormValues&gt; }) {
  const {
    register, handleSubmit, watch, setError,
    formState: { errors, isSubmitting, isDirty }
  } = useForm&lt;FormValues&gt;({
    resolver: zodResolver(schema),
    defaultValues: initial,
    mode: "onBlur"   // validate on blur, then on every change
  });

  // Conditional field — show shipping notes only if newsletter true
  const newsletter = watch("newsletter");

  // Warn before navigating away with unsaved changes
  useEffect(() =&gt; {
    const handler = (e) =&gt; { if (isDirty) { e.preventDefault(); e.returnValue = ""; } };
    window.addEventListener("beforeunload", handler);
    return () =&gt; window.removeEventListener("beforeunload", handler);
  }, [isDirty]);

  const onSubmit = async (data: FormValues) =&gt; {
    try {
      await api.saveProfile(data);
      navigate("/profile");
    } catch (e: any) {
      // Map server validation errors back to fields
      if (e.response?.status === 422) {
        for (const [field, message] of Object.entries(e.response.data.errors)) {
          setError(field as any, { message: String(message) });
        }
      } else {
        setError("root", { message: "Save failed &mdash; please try again" });
      }
    }
  };

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)}&gt;
      &lt;fieldset&gt;
        &lt;legend&gt;Personal info&lt;/legend&gt;
        &lt;label&gt;First name &lt;input {...register("firstName")} /&gt;&lt;/label&gt;
        {errors.firstName &amp;&amp; &lt;p&gt;{errors.firstName.message}&lt;/p&gt;}
        {/* ... more fields ... */}
      &lt;/fieldset&gt;

      &lt;fieldset&gt;
        &lt;legend&gt;Address&lt;/legend&gt;
        &lt;label&gt;Street &lt;input {...register("address.line1")} /&gt;&lt;/label&gt;
        {errors.address?.line1 &amp;&amp; &lt;p&gt;{errors.address.line1.message}&lt;/p&gt;}
        {/* ... more fields ... */}
      &lt;/fieldset&gt;

      &lt;fieldset&gt;
        &lt;legend&gt;Preferences&lt;/legend&gt;
        &lt;label&gt;&lt;input type="checkbox" {...register("newsletter")} /&gt; Subscribe to newsletter&lt;/label&gt;
        {newsletter &amp;&amp; (
          &lt;label&gt;
            How often? &lt;select {...register("frequency")}&gt;
              &lt;option value="weekly"&gt;Weekly&lt;/option&gt;
              &lt;option value="monthly"&gt;Monthly&lt;/option&gt;
            &lt;/select&gt;
          &lt;/label&gt;
        )}
      &lt;/fieldset&gt;

      {errors.root &amp;&amp; &lt;p className="err"&gt;{errors.root.message}&lt;/p&gt;}

      &lt;button type="submit" disabled={isSubmitting || !isDirty}&gt;
        {isSubmitting ? "Saving..." : "Save"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Performance with 100+ fields</td><td>RHF&rsquo;s uncontrolled approach &mdash; only the field re-renders on its keystroke, not the whole form</td></tr>
  <tr><td>Cross-field validation</td><td>Zod <code>.refine()</code>; or <code>watch()</code> + manual <code>setError</code></td></tr>
  <tr><td>Conditional fields</td><td><code>watch("newsletter")</code> reactively shows/hides; or <code>useWatch</code> for finer control</td></tr>
  <tr><td>Multi-section forms</td><td>Split per <code>&lt;fieldset&gt;</code>; for huge forms, multi-step wizard pattern (Q46)</td></tr>
  <tr><td>Auto-save drafts</td><td>Debounce <code>watch()</code> output → save to localStorage or server every 5s</td></tr>
  <tr><td>Server validation errors</td><td><code>setError(field, { message })</code> displays them next to fields</td></tr>
  <tr><td>Unsaved changes warning</td><td><code>isDirty</code> + <code>beforeunload</code> prompt</td></tr>
  <tr><td>Field arrays (variable rows)</td><td><code>useFieldArray</code> &mdash; insert, remove, swap rows with stable keys</td></tr>
</table>

<p><strong>For wizards / multi-step</strong>, see Q46 &mdash; combine RHF state with step navigation. <strong>Schema-first design</strong> pays off: the same Zod schema validates client-side AND server-side (Node/Bun); types come from <code>z.infer</code>; one place to change rules.</p>
'''

ANSWERS[42] = r'''
<p><strong>Situation:</strong> the app must let users download files &mdash; reports, exports, attachments, generated PDFs. Files come from authenticated endpoints (need auth header), are sometimes large, and may need progress feedback. Browser&rsquo;s native download flow handles small files; large/authenticated downloads need extra plumbing.</p>

<p><strong>Approach:</strong> for simple authenticated downloads &mdash; fetch as blob, create object URL, trigger anchor click, revoke URL. For large files &mdash; either redirect to a signed URL or use streaming (<code>showSaveFilePicker</code> when available). Use <code>Content-Disposition: attachment</code> server-side for filename hints.</p>

<pre><code>// === Simple authenticated download ===
async function downloadFile(url: string, filename: string) {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error(`Download failed: ${res.status}`);

  const blob = await res.blob();
  const objectUrl = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(objectUrl);   // free memory
}

// Usage in component
function DownloadButton({ reportId }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState&lt;string | null&gt;(null);

  const handleClick = async () =&gt; {
    setLoading(true);
    setError(null);
    try {
      await downloadFile(`/api/reports/${reportId}/export`, `report-${reportId}.csv`);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    &lt;&gt;
      &lt;button onClick={handleClick} disabled={loading}&gt;
        {loading ? "Preparing..." : "Download CSV"}
      &lt;/button&gt;
      {error &amp;&amp; &lt;p className="err"&gt;{error}&lt;/p&gt;}
    &lt;/&gt;
  );
}</code></pre>

<pre><code>// === With progress (XMLHttpRequest or fetch + ReadableStream) ===
async function downloadWithProgress(url: string, filename: string, onProgress: (pct: number) =&gt; void) {
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("Failed");

  const total = Number(res.headers.get("Content-Length")) || 0;
  const reader = res.body!.getReader();
  const chunks: Uint8Array[] = [];
  let received = 0;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    received += value.length;
    if (total) onProgress(Math.round((received / total) * 100));
  }

  const blob = new Blob(chunks);
  const url2 = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href: url2, download: filename });
  a.click();
  URL.revokeObjectURL(url2);
}</code></pre>

<pre><code>// === Modern: showSaveFilePicker (File System Access API) — Chrome/Edge only ===
async function streamDownload(url: string, suggestedName: string) {
  const handle = await window.showSaveFilePicker({ suggestedName });
  const writable = await handle.createWritable();

  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  await res.body!.pipeTo(writable);
  // streams directly to disk — no memory footprint for huge files
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Best for</th><th>Issues</th></tr>
  <tr><td>Direct anchor link</td><td>Public files</td><td>Can&rsquo;t add auth headers</td></tr>
  <tr><td>Fetch + blob + anchor click</td><td>Authenticated, small/medium files (&lt;100MB)</td><td>Loads entire file into memory</td></tr>
  <tr><td>Signed URL redirect</td><td>Large files in S3/GCS</td><td>Server generates short-lived signed URL; browser downloads directly</td></tr>
  <tr><td>showSaveFilePicker + stream</td><td>Very large files, Chrome/Edge users</td><td>Limited browser support</td></tr>
  <tr><td>Progressive download with progress bar</td><td>UX polish for big files</td><td>More code; XHR or stream reader</td></tr>
</table>

<p><strong>Server-side considerations:</strong></p>

<table>
  <tr><th>Header / behavior</th><th>Why</th></tr>
  <tr><td><code>Content-Disposition: attachment; filename="..."</code></td><td>Forces download instead of inline render; suggests filename</td></tr>
  <tr><td><code>Content-Length</code></td><td>Enables progress bars</td></tr>
  <tr><td><code>Content-Type</code></td><td>Correct MIME type for the file (<code>application/pdf</code>, <code>text/csv</code>, etc.)</td></tr>
  <tr><td>Streaming generation</td><td>For large CSVs, stream rows from DB &mdash; don&rsquo;t buffer the whole thing</td></tr>
  <tr><td>Signed URLs (S3/GCS)</td><td>Move bandwidth off your server; expires in 5-15 min</td></tr>
</table>

<p><strong>Common pitfalls:</strong> forgetting <code>URL.revokeObjectURL</code> (memory leak); not handling errors (silent failure); using GET with sensitive data in URL (logged everywhere &mdash; use POST with body); CORS issues on cross-origin downloads (Origin must allow <code>Content-Disposition</code>).</p>
'''

ANSWERS[43] = r'''
<p><strong>Situation:</strong> the app has many tables &mdash; users, orders, products, logs &mdash; each needs sorting (any column), filtering (search, dropdowns), and pagination. Building each independently leads to inconsistent UX and duplicated code. A single reusable table component handles all of them.</p>

<p><strong>Approach:</strong> use <strong>TanStack Table</strong> (formerly React Table) &mdash; a headless library that provides the logic (sorting, filtering, pagination, virtualization) without imposing markup. You bring the JSX. Combine with <strong>shadcn/ui</strong>&rsquo;s data-table starter for production-ready styles.</p>

<pre><code>// Install: npm install @tanstack/react-table

import {
  useReactTable, getCoreRowModel, getSortedRowModel, getFilteredRowModel, getPaginationRowModel,
  flexRender, createColumnHelper
} from "@tanstack/react-table";
import { useState } from "react";

type User = { id: string; name: string; email: string; role: string; createdAt: Date };

const columnHelper = createColumnHelper&lt;User&gt;();

const columns = [
  columnHelper.accessor("name", { header: "Name", cell: (info) =&gt; info.getValue() }),
  columnHelper.accessor("email", { header: "Email" }),
  columnHelper.accessor("role", {
    header: "Role",
    cell: (info) =&gt; &lt;span className={`badge badge-${info.getValue()}`}&gt;{info.getValue()}&lt;/span&gt;
  }),
  columnHelper.accessor("createdAt", {
    header: "Joined",
    cell: (info) =&gt; new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(info.getValue())
  }),
  columnHelper.display({
    id: "actions",
    cell: ({ row }) =&gt; &lt;button onClick={() =&gt; edit(row.original.id)}&gt;Edit&lt;/button&gt;
  })
];

function DataTable&lt;T&gt;({ data, columns }: { data: T[]; columns: any[] }) {
  const [sorting, setSorting] = useState([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const table = useReactTable({
    data, columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 20 } }
  });

  return (
    &lt;&gt;
      &lt;input
        value={globalFilter}
        onChange={e =&gt; setGlobalFilter(e.target.value)}
        placeholder="Search..."
      /&gt;

      &lt;table&gt;
        &lt;thead&gt;
          {table.getHeaderGroups().map(hg =&gt; (
            &lt;tr key={hg.id}&gt;
              {hg.headers.map(h =&gt; (
                &lt;th
                  key={h.id}
                  onClick={h.column.getToggleSortingHandler()}
                  style={{ cursor: h.column.getCanSort() ? "pointer" : "default" }}
                &gt;
                  {flexRender(h.column.columnDef.header, h.getContext())}
                  {{ asc: " ▲", desc: " ▼" }[h.column.getIsSorted() as string] ?? ""}
                &lt;/th&gt;
              ))}
            &lt;/tr&gt;
          ))}
        &lt;/thead&gt;
        &lt;tbody&gt;
          {table.getRowModel().rows.map(row =&gt; (
            &lt;tr key={row.id}&gt;
              {row.getVisibleCells().map(cell =&gt; (
                &lt;td key={cell.id}&gt;{flexRender(cell.column.columnDef.cell, cell.getContext())}&lt;/td&gt;
              ))}
            &lt;/tr&gt;
          ))}
        &lt;/tbody&gt;
      &lt;/table&gt;

      &lt;div&gt;
        &lt;button onClick={() =&gt; table.previousPage()} disabled={!table.getCanPreviousPage()}&gt;Prev&lt;/button&gt;
        &lt;span&gt;
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        &lt;/span&gt;
        &lt;button onClick={() =&gt; table.nextPage()} disabled={!table.getCanNextPage()}&gt;Next&lt;/button&gt;
      &lt;/div&gt;
    &lt;/&gt;
  );
}

// Usage
&lt;DataTable data={users} columns={columns} /&gt;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Client-side vs server-side sorting/filtering</td><td>Client OK for ≤1k rows; server-side for larger (set <code>manualPagination/manualSorting/manualFiltering: true</code>)</td></tr>
  <tr><td>Many rows (&gt;1000)</td><td>Add row virtualization with TanStack Virtual &mdash; only renders visible rows</td></tr>
  <tr><td>Per-column filters (not just global search)</td><td>Add <code>columnFilters</code> state + <code>filterFn</code> per column</td></tr>
  <tr><td>Resizable / reorderable columns</td><td>TanStack Table supports both; persist to localStorage</td></tr>
  <tr><td>Row selection</td><td><code>getRowSelectionRowModel</code> + checkbox column</td></tr>
  <tr><td>Expandable rows</td><td><code>getExpandedRowModel</code> + sub-row data</td></tr>
  <tr><td>Sticky header on scroll</td><td><code>position: sticky</code> on <code>&lt;thead&gt;</code> + <code>top: 0</code></td></tr>
  <tr><td>URL-synced state</td><td>Sync sorting/filters/page to <code>useSearchParams</code> for shareable views</td></tr>
</table>

<p><strong>Why headless wins</strong>: complete styling control + framework-agnostic logic. <strong>shadcn/ui</strong>&rsquo;s data-table example combines TanStack Table + Tailwind + Radix primitives &mdash; copy that into your project for production-ready setup. <strong>For maximum scale</strong>: AG Grid (commercial), MUI X DataGrid (commercial Pro features), Glide Data Grid (canvas-based, handles millions of rows).</p>
'''

ANSWERS[44] = r'''
<p><strong>Situation:</strong> the app collects payment for orders, subscriptions, or one-time purchases. Stripe is the dominant 2026 choice. The challenge: PCI compliance &mdash; you cannot touch raw card data. Stripe Elements handles card UI; your server processes the payment via the Stripe API.</p>

<p><strong>Approach:</strong> use <strong>@stripe/react-stripe-js</strong> + <strong>Stripe Elements</strong>. The card form lives in an iframe controlled by Stripe &mdash; PCI scope stays with Stripe, not you. Server creates a PaymentIntent; client confirms payment with the Stripe SDK; webhook handles the success/failure.</p>

<pre><code>// === 1. Server creates PaymentIntent (Node/Bun) ===
import Stripe from "stripe";
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

app.post("/api/checkout", async (req, res) =&gt; {
  const { items, userId } = req.body;
  const amount = calculateTotal(items);   // SERVER-side, never trust client total

  const intent = await stripe.paymentIntents.create({
    amount,
    currency: "usd",
    automatic_payment_methods: { enabled: true },
    metadata: { userId, orderItems: JSON.stringify(items) }
  });

  res.json({ clientSecret: intent.client_secret });
});</code></pre>

<pre><code>// === 2. Client renders Stripe Elements ===
import { loadStripe } from "@stripe/stripe-js";
import { Elements, PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

function CheckoutPage({ items }) {
  const [clientSecret, setClientSecret] = useState&lt;string | null&gt;(null);

  useEffect(() =&gt; {
    fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items })
    })
      .then(r =&gt; r.json())
      .then(d =&gt; setClientSecret(d.clientSecret));
  }, [items]);

  if (!clientSecret) return &lt;p&gt;Setting up payment...&lt;/p&gt;;

  return (
    &lt;Elements stripe={stripePromise} options={{ clientSecret }}&gt;
      &lt;CheckoutForm /&gt;
    &lt;/Elements&gt;
  );
}

function CheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState&lt;string | null&gt;(null);

  const handleSubmit = async (e) =&gt; {
    e.preventDefault();
    if (!stripe || !elements) return;

    setSubmitting(true);
    setError(null);

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: `${window.location.origin}/order-success` }
    });

    if (error) {
      // immediate validation errors (card declined, expired)
      setError(error.message ?? "Payment failed");
      setSubmitting(false);
    }
    // Otherwise Stripe redirects to return_url after 3DS / approval
  };

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;PaymentElement /&gt;     {/* Stripe-hosted iframe — handles card, Apple Pay, Google Pay */}
      {error &amp;&amp; &lt;p className="err"&gt;✗ {error}&lt;/p&gt;}
      &lt;button type="submit" disabled={!stripe || submitting}&gt;
        {submitting ? "Processing..." : "Pay"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<pre><code>// === 3. Webhook handles success (server) ===
app.post("/api/stripe/webhook", express.raw({ type: "application/json" }), async (req, res) =&gt; {
  const sig = req.headers["stripe-signature"]!;
  const event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET!);

  if (event.type === "payment_intent.succeeded") {
    const intent = event.data.object;
    await fulfillOrder(intent.metadata.userId, JSON.parse(intent.metadata.orderItems));
  }

  res.json({ received: true });
});</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>PCI compliance scope</td><td>Stripe Elements iframe — your servers/code never touch raw card data</td></tr>
  <tr><td>Client computes amount</td><td>NEVER &mdash; always server-side. Client passes items, server computes total</td></tr>
  <tr><td>3D Secure / SCA in EU</td><td>Stripe&rsquo;s <code>confirmPayment</code> handles the redirect/challenge automatically</td></tr>
  <tr><td>Order fulfillment</td><td>WEBHOOK ONLY &mdash; not in client success handler. Client can be closed/lost.</td></tr>
  <tr><td>Subscriptions</td><td>Use Stripe&rsquo;s Subscriptions API + Customer Portal (hosted by Stripe)</td></tr>
  <tr><td>Apple Pay / Google Pay</td><td><code>&lt;PaymentElement /&gt;</code> shows them automatically when supported</td></tr>
  <tr><td>Refunds</td><td>Server-only via Stripe API; never trust client refund requests</td></tr>
  <tr><td>Test cards</td><td>4242 4242 4242 4242 (success), 4000 0000 0000 9995 (declined) in test mode</td></tr>
</table>

<p><strong>Stripe Checkout (hosted) vs Elements (embedded):</strong></p>

<table>
  <tr><th></th><th>Checkout (hosted page)</th><th>Elements (embedded)</th></tr>
  <tr><td>Setup time</td><td>10 minutes</td><td>1-2 days</td></tr>
  <tr><td>Customization</td><td>Limited theming</td><td>Full control</td></tr>
  <tr><td>PCI scope</td><td>Smallest (SAQ A)</td><td>Small (SAQ A)</td></tr>
  <tr><td>UX</td><td>Stripe-branded redirect page</td><td>Stays in your app</td></tr>
  <tr><td>Best for</td><td>Quick start, simple flows</td><td>Polished UX, multi-step checkout</td></tr>
</table>

<p><strong>Critical reminders:</strong> never log full card data; never trust client-computed totals; always use webhooks for fulfillment; test in test mode first; use idempotency keys on PaymentIntent creation; verify webhook signatures. <strong>Alternatives:</strong> PayPal SDK, Adyen Web, Square (similar patterns); for crypto, Coinbase Commerce. Stripe&rsquo;s docs are exemplary &mdash; follow them rather than inventing your own flow.</p>
'''

ANSWERS[45] = r'''
<p><strong>Situation:</strong> a component must perform side effects &mdash; fetching data, subscribing to an event source, setting up timers, syncing with localStorage, integrating non-React libraries. Side effects must run at the right time, clean up properly, and not race with each other when deps change.</p>

<p><strong>Approach:</strong> use <code>useEffect</code> for most cases (runs after render commit, async-friendly), <code>useLayoutEffect</code> when you need to mutate DOM before paint, and refs for values that must persist across renders without triggering re-renders. Always include cleanup; always declare dependencies honestly.</p>

<pre><code>// === Pattern 1: Fetch with cancellation ===
function UserPanel({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() =&gt; {
    const ctrl = new AbortController();

    fetch(`/api/users/${userId}`, { signal: ctrl.signal })
      .then(r =&gt; r.json())
      .then(setUser)
      .catch(e =&gt; { if (e.name !== "AbortError") console.error(e); });

    return () =&gt; ctrl.abort();   // cancel in-flight on unmount or userId change
  }, [userId]);

  return user ? &lt;h2&gt;{user.name}&lt;/h2&gt; : &lt;p&gt;Loading...&lt;/p&gt;;
}

// === Pattern 2: Subscriptions ===
function PriceTicker({ symbol }) {
  const [price, setPrice] = useState(null);

  useEffect(() =&gt; {
    const sub = priceFeed.subscribe(symbol, setPrice);
    return () =&gt; sub.unsubscribe();
  }, [symbol]);

  return &lt;p&gt;{symbol}: ${price ?? "—"}&lt;/p&gt;;
}

// === Pattern 3: Browser events ===
function useScrollDirection() {
  const [direction, setDirection] = useState&lt;"up"|"down"&gt;("up");
  const lastY = useRef(0);

  useEffect(() =&gt; {
    const handleScroll = () =&gt; {
      const y = window.scrollY;
      setDirection(y &gt; lastY.current ? "down" : "up");
      lastY.current = y;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () =&gt; window.removeEventListener("scroll", handleScroll);
  }, []);

  return direction;
}

// === Pattern 4: Timers ===
function AutoSave({ value, onSave }) {
  useEffect(() =&gt; {
    const id = setTimeout(() =&gt; onSave(value), 1000);
    return () =&gt; clearTimeout(id);   // reset timer on every value change
  }, [value, onSave]);
  return null;
}

// === Pattern 5: Sync to localStorage ===
function usePersistentState&lt;T&gt;(key: string, initial: T) {
  const [value, setValue] = useState&lt;T&gt;(() =&gt; {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initial;
  });

  useEffect(() =&gt; {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// === Pattern 6: Non-React library integration ===
function MapView({ lat, lng }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() =&gt; {
    mapRef.current = new MapLibrary(containerRef.current, { lat, lng });
    return () =&gt; mapRef.current.destroy();
  }, []);

  // Sync prop changes to imperative map without re-creating it
  useEffect(() =&gt; {
    mapRef.current?.setCenter(lat, lng);
  }, [lat, lng]);

  return &lt;div ref={containerRef} style={{ height: 400 }} /&gt;;
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pitfall</th><th>Fix</th></tr>
  <tr><td>Stale closure (effect uses old state)</td><td>Include the value in deps, OR use updater form (<code>setX(prev =&gt; ...)</code>), OR ref</td></tr>
  <tr><td>Race condition: response from old fetch arrives last</td><td>AbortController in cleanup; or <code>cancelled</code> flag</td></tr>
  <tr><td>Effect re-runs every render</td><td>Forgot deps array. <code>useEffect(() =&gt; {})</code> with no array runs always.</td></tr>
  <tr><td>Strict Mode double-runs effects</td><td>Intentional &mdash; surfaces missing cleanups. Production runs once.</td></tr>
  <tr><td>Setting state synchronously in effect</td><td>Avoid &mdash; cascading re-renders. Compute during render or use <code>useMemo</code>.</td></tr>
  <tr><td>useEffect for derived state</td><td>Don&rsquo;t. Compute during render: <code>const fullName = `${first} ${last}`</code>.</td></tr>
  <tr><td>Sync external store</td><td>Use <code>useSyncExternalStore</code> for stores outside React (Redux v4 already does this internally)</td></tr>
</table>

<p><strong>The mental model:</strong> "useEffect synchronizes my component with an external system." Setup matches deps; if deps change, clean up old setup, run new. Don&rsquo;t use it to chain state updates &mdash; that&rsquo;s a code smell pointing toward derived state or events.</p>

<p><strong>2026 reality:</strong> for data fetching specifically, prefer <strong>TanStack Query</strong> (cleaner abstractions, built-in cache/retry/deduplication). Reach for raw <code>useEffect</code> when synchronizing with subscriptions, browser APIs, third-party libraries &mdash; the cases TanStack Query doesn&rsquo;t cover. Use <strong>useEffect Event</strong> when stable in React (separates &ldquo;reactive deps&rdquo; from &ldquo;just read latest value&rdquo;).</p>
'''

ANSWERS[46] = r'''
<p><strong>Situation:</strong> the app needs a multi-step checkout/onboarding flow &mdash; address, shipping, payment, review. Each step validates before advancing; back navigation preserves data; URL syncs to the current step (refresh-safe + shareable). Final submit collects all data and sends one request.</p>

<p><strong>Approach:</strong> URL-driven steps via React Router child routes. Form state in React Hook Form + Zod, lifted to a parent context shared across steps. Each step validates its slice of the schema before advancing. Persistence to sessionStorage so refresh doesn&rsquo;t lose progress.</p>

<pre><code>// === Schema split per step + composed full schema ===
const personalSchema = z.object({
  firstName: z.string().min(1), lastName: z.string().min(1),
  email: z.string().email()
});
const addressSchema = z.object({
  street: z.string().min(1), city: z.string().min(1),
  state: z.string().length(2), zip: z.string().regex(/^\d{5}$/)
});
const paymentSchema = z.object({
  cardNumber: z.string().regex(/^\d{13,19}$/),
  expiry: z.string().regex(/^\d{2}\/\d{2}$/),
  cvv: z.string().regex(/^\d{3,4}$/)
});
const fullSchema = personalSchema.merge(addressSchema).merge(paymentSchema);
type FullData = z.infer&lt;typeof fullSchema&gt;;

// === Wizard context — owns shared state ===
const WizardContext = createContext&lt;{
  data: Partial&lt;FullData&gt;;
  update: (patch: Partial&lt;FullData&gt;) =&gt; void;
} | null&gt;(null);

function WizardProvider({ children }) {
  const [data, setData] = useState&lt;Partial&lt;FullData&gt;&gt;(() =&gt; {
    const stored = sessionStorage.getItem("wizard");
    return stored ? JSON.parse(stored) : {};
  });

  useEffect(() =&gt; {
    sessionStorage.setItem("wizard", JSON.stringify(data));
  }, [data]);

  const update = (patch) =&gt; setData(prev =&gt; ({ ...prev, ...patch }));

  return &lt;WizardContext.Provider value={{ data, update }}&gt;{children}&lt;/WizardContext.Provider&gt;;
}

const useWizard = () =&gt; useContext(WizardContext)!;</code></pre>

<pre><code>// === Each step is its own form ===
function PersonalStep() {
  const { data, update } = useWizard();
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(personalSchema),
    defaultValues: data
  });

  const onSubmit = (values) =&gt; {
    update(values);
    navigate("/checkout/address");
  };

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)}&gt;
      &lt;input {...register("firstName")} placeholder="First name" /&gt;
      &lt;input {...register("lastName")} placeholder="Last name" /&gt;
      &lt;input {...register("email")} placeholder="Email" /&gt;
      &lt;button type="submit"&gt;Next&lt;/button&gt;
    &lt;/form&gt;
  );
}

// (AddressStep, PaymentStep similar — each validates its slice and navigates)

// === Review + submit ===
function ReviewStep() {
  const { data } = useWizard();

  const handleSubmit = async () =&gt; {
    const validated = fullSchema.parse(data);   // final validation
    await api.placeOrder(validated);
    sessionStorage.removeItem("wizard");
    navigate("/order-success");
  };

  return (
    &lt;&gt;
      &lt;h2&gt;Review&lt;/h2&gt;
      &lt;dl&gt;
        &lt;dt&gt;Name&lt;/dt&gt; &lt;dd&gt;{data.firstName} {data.lastName}&lt;/dd&gt;
        &lt;dt&gt;Address&lt;/dt&gt; &lt;dd&gt;{data.street}, {data.city}&lt;/dd&gt;
        &lt;dt&gt;Card&lt;/dt&gt; &lt;dd&gt;**** {data.cardNumber?.slice(-4)}&lt;/dd&gt;
      &lt;/dl&gt;
      &lt;button onClick={handleSubmit}&gt;Place order&lt;/button&gt;
    &lt;/&gt;
  );
}

// === Layout with progress + outlet ===
function CheckoutLayout() {
  const { pathname } = useLocation();
  const stepIndex = ["personal", "address", "payment", "review"]
    .findIndex(s =&gt; pathname.endsWith(s));

  return (
    &lt;&gt;
      &lt;ProgressBar steps={["Personal", "Address", "Payment", "Review"]} current={stepIndex} /&gt;
      &lt;Outlet /&gt;
    &lt;/&gt;
  );
}

// === Routes ===
&lt;Route path="/checkout" element={&lt;WizardProvider&gt;&lt;CheckoutLayout /&gt;&lt;/WizardProvider&gt;}&gt;
  &lt;Route path="personal" element={&lt;PersonalStep /&gt;} /&gt;
  &lt;Route path="address" element={&lt;AddressStep /&gt;} /&gt;
  &lt;Route path="payment" element={&lt;PaymentStep /&gt;} /&gt;
  &lt;Route path="review" element={&lt;ReviewStep /&gt;} /&gt;
&lt;/Route&gt;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>URL per step</td><td>Refresh-safe, shareable, browser back works correctly</td></tr>
  <tr><td>Refresh loses data</td><td>sessionStorage syncs context</td></tr>
  <tr><td>Cross-step validation</td><td>Final <code>fullSchema.parse</code> on review; per-step validates slice</td></tr>
  <tr><td>Skip-ahead protection</td><td>Step guards: redirect from /payment if /personal incomplete</td></tr>
  <tr><td>Don&rsquo;t store sensitive payment data</td><td>Tokenize via Stripe Elements; store Stripe payment-method-id, not card details</td></tr>
  <tr><td>Progressive disclosure</td><td>Show error summary at top of step; inline errors per field</td></tr>
  <tr><td>Allow back nav without losing data</td><td>Context retains values; defaultValues hydrate form</td></tr>
</table>

<p><strong>Mature wizard libs:</strong> <strong>react-hook-form</strong>&rsquo;s docs include this pattern (it&rsquo;s lean and works); <strong>formik-wizard</strong> (Formik-based, slightly older); <strong>@reactgular/react-stepper</strong>. <strong>For very long signup flows</strong>, consider authoring the form server-side and submitting per-step via Server Actions (Next.js) &mdash; less client state, more progressive enhancement.</p>
'''

ANSWERS[47] = r'''
<p><strong>Situation:</strong> several components scattered across the tree need to read or update the same state &mdash; e.g., the current user, theme, language, or notification queue. Prop drilling is impractical (passing through 5 layers of intermediate components). The simplest answer that doesn&rsquo;t add a library: Context.</p>

<p><strong>Approach:</strong> Create a Context with both state and dispatch (or setter). Wrap the app with a provider. Components read via <code>useContext</code>. Split state and dispatch into separate Contexts to avoid re-rendering pure consumers. For complex global state, graduate to Zustand or a similar library.</p>

<pre><code>// === AuthContext.tsx ===
import { createContext, useContext, useState, useMemo } from "react";

type User = { id: string; name: string; email: string };

type AuthState = { user: User | null; loading: boolean };
type AuthActions = {
  signIn: (email: string, password: string) =&gt; Promise&lt;void&gt;;
  signOut: () =&gt; void;
};

// Split: state changes don&rsquo;t re-render pure dispatchers
const StateContext = createContext&lt;AuthState | null&gt;(null);
const ActionsContext = createContext&lt;AuthActions | null&gt;(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState&lt;User | null&gt;(null);
  const [loading, setLoading] = useState(false);

  // Actions are stable (useMemo with empty deps + functional updates)
  const actions = useMemo&lt;AuthActions&gt;(() =&gt; ({
    signIn: async (email, password) =&gt; {
      setLoading(true);
      try {
        const u = await api.login(email, password);
        setUser(u);
      } finally { setLoading(false); }
    },
    signOut: () =&gt; setUser(null)
  }), []);

  const state = useMemo(() =&gt; ({ user, loading }), [user, loading]);

  return (
    &lt;StateContext.Provider value={state}&gt;
      &lt;ActionsContext.Provider value={actions}&gt;
        {children}
      &lt;/ActionsContext.Provider&gt;
    &lt;/StateContext.Provider&gt;
  );
}

// Consumer hooks with safety
export function useAuthState() {
  const ctx = useContext(StateContext);
  if (!ctx) throw new Error("useAuthState must be used inside &lt;AuthProvider&gt;");
  return ctx;
}

export function useAuthActions() {
  const ctx = useContext(ActionsContext);
  if (!ctx) throw new Error("useAuthActions must be used inside &lt;AuthProvider&gt;");
  return ctx;
}</code></pre>

<pre><code>// === Components ===
function Header() {
  const { user } = useAuthState();
  const { signOut } = useAuthActions();

  return (
    &lt;header&gt;
      {user ? (
        &lt;&gt;
          &lt;span&gt;Hi, {user.name}&lt;/span&gt;
          &lt;button onClick={signOut}&gt;Sign out&lt;/button&gt;
        &lt;/&gt;
      ) : (
        &lt;Link to="/login"&gt;Sign in&lt;/Link&gt;
      )}
    &lt;/header&gt;
  );
}

// This component only triggers actions — never reads state.
// It WON&rsquo;T re-render when state changes.
function LogoutButton() {
  const { signOut } = useAuthActions();
  return &lt;button onClick={signOut}&gt;Sign out&lt;/button&gt;;
}

// Wrap app
function App() {
  return (
    &lt;AuthProvider&gt;
      &lt;ThemeProvider&gt;
        &lt;Router /&gt;
      &lt;/ThemeProvider&gt;
    &lt;/AuthProvider&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Every consumer re-renders on context change</td><td>Split state and actions into two contexts; pure dispatchers don&rsquo;t re-render</td></tr>
  <tr><td>Provider <code>value</code> must be stable</td><td>useMemo / useCallback the value object, or split fields into multiple contexts</td></tr>
  <tr><td>No selector support</td><td>Context can&rsquo;t subscribe to slices &mdash; if user shape grows, all consumers re-render. Use Zustand for selectors</td></tr>
  <tr><td>Provider hell</td><td>Compose in one wrapper component, or use a "compose providers" helper</td></tr>
  <tr><td>Default value vs guard</td><td>Use <code>null</code> default + throw in hook &mdash; catches misuse outside provider</td></tr>
  <tr><td>SSR / Next.js</td><td>Provider wraps the layout; works in Server Components for read-only contexts</td></tr>
</table>

<p><strong>When Context isn&rsquo;t enough &mdash; the boundary cases:</strong></p>

<ul>
  <li><strong>High-frequency updates</strong> (mouse position, scroll progress) &mdash; Context re-renders every consumer; use refs + imperative DOM updates instead.</li>
  <li><strong>Many consumers, partial-data subscriptions</strong> &mdash; use <strong>Zustand</strong> or <strong>Jotai</strong> for selector-based subscriptions.</li>
  <li><strong>Large complex state with middleware (logging, undo, time-travel)</strong> &mdash; <strong>Redux Toolkit</strong>.</li>
  <li><strong>Server data</strong> &mdash; never put it in Context. Use <strong>TanStack Query</strong>; it handles caching/refetch better.</li>
</ul>

<p><strong>Default for 2026:</strong> Context for low-frequency app-wide state (auth, theme, locale). Zustand for everything else. TanStack Query for server data. Never mix server data into your client state.</p>
'''

ANSWERS[48] = r'''
<p><strong>Situation:</strong> the app needs real-time push notifications &mdash; new message, friend request, payment received. Polling wastes battery and bandwidth; WebSockets require extra infrastructure. <strong>Firebase Cloud Messaging (FCM)</strong> piggybacks on Google&rsquo;s push infrastructure; the Web Push API delivers them even when the tab is closed.</p>

<p><strong>Approach:</strong> register a service worker, request notification permission, get an FCM token, store it server-side per user. When server wants to push, it calls FCM with the token; FCM delivers via Web Push. Foreground messages go through <code>onMessage</code>; background messages through the service worker.</p>

<pre><code>// === Setup: install firebase + service worker ===
// public/firebase-messaging-sw.js — must be at site root
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "...", projectId: "...", messagingSenderId: "...", appId: "..."
});

const messaging = firebase.messaging();

// Background notification handler
messaging.onBackgroundMessage((payload) =&gt; {
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body,
    icon: "/icon-192.png",
    data: payload.data    // arbitrary key/value for click handling
  });
});

self.addEventListener("notificationclick", (event) =&gt; {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url || "/"));
});</code></pre>

<pre><code>// === Client setup ===
import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

const firebaseApp = initializeApp({
  apiKey: import.meta.env.VITE_FIREBASE_KEY, /* ... */
});
const messaging = getMessaging(firebaseApp);

export async function registerForNotifications(userId: string) {
  if (!("Notification" in window)) {
    throw new Error("This browser doesn&rsquo;t support notifications");
  }

  const permission = await Notification.requestPermission();
  if (permission !== "granted") return null;

  // Get the FCM token (uniquely identifies this device + browser)
  const token = await getToken(messaging, {
    vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY
  });

  if (!token) return null;

  // Send token to server, associate with user
  await fetch("/api/notifications/register", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${authToken}` },
    body: JSON.stringify({ userId, token, platform: "web" })
  });

  // Foreground messages — show toast inside the app
  onMessage(messaging, (payload) =&gt; {
    notify.info(payload.notification?.body ?? "New message");
  });

  return token;
}

// Component
function NotificationOptIn() {
  const { user } = useAuth();
  const [status, setStatus] = useState&lt;"idle" | "asking" | "granted" | "denied"&gt;("idle");

  const enable = async () =&gt; {
    setStatus("asking");
    try {
      const token = await registerForNotifications(user.id);
      setStatus(token ? "granted" : "denied");
    } catch (e) {
      setStatus("denied");
    }
  };

  return status === "granted"
    ? &lt;p&gt;✓ Notifications enabled&lt;/p&gt;
    : &lt;button onClick={enable}&gt;Enable notifications&lt;/button&gt;;
}</code></pre>

<pre><code>// === Server sends notification (Node) ===
import admin from "firebase-admin";

await admin.messaging().send({
  token: userFcmToken,
  notification: { title: "New message", body: "Alice sent you a message" },
  webpush: { fcmOptions: { link: "/messages/1234" } },
  data: { type: "message", messageId: "1234" }
});</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>Permission UX</td><td>Don&rsquo;t prompt on page load &mdash; wait for an explicit user action (e.g., &ldquo;Enable notifications&rdquo; button)</td></tr>
  <tr><td>Token rotation</td><td>FCM tokens can change &mdash; refresh on app start, sync to server</td></tr>
  <tr><td>Multi-device users</td><td>Store multiple tokens per user; send to all on notify</td></tr>
  <tr><td>Notification preferences</td><td>Server-side per-user opt-out for each notification type (digest, mentions, etc.)</td></tr>
  <tr><td>iOS Safari</td><td>Web Push works on iOS 16.4+ but only when the app is installed as a PWA (added to home screen)</td></tr>
  <tr><td>Permission revocation</td><td>If user revokes, push fails &mdash; clean up dead tokens server-side</td></tr>
  <tr><td>Privacy / GDPR</td><td>Allow users to disable notifications; document data retention</td></tr>
  <tr><td>Don&rsquo;t spam</td><td>Bundle multiple notifications; quiet hours; rate limit</td></tr>
</table>

<p><strong>Alternatives in 2026:</strong> <strong>OneSignal</strong> (cross-platform, generous free tier, good admin UI), <strong>Pusher Beams</strong>, <strong>Knock</strong> (notification routing across email/push/in-app/SMS &mdash; great for multi-channel), <strong>Apple Push Notification Service</strong> for native iOS. <strong>For real-time in-app updates without OS notifications</strong> (someone joined the chat, new comment), use WebSockets/Pusher/Convex/Liveblocks &mdash; FCM is for OS-level push.</p>
'''

ANSWERS[49] = r'''
<p><strong>Situation:</strong> the app has a dashboard with multiple widgets &mdash; sales chart, recent orders, KPI cards, activity feed. Each widget fetches independently; users can rearrange/resize/toggle them; layout persists. Common in admin panels, BI tools, monitoring apps.</p>

<p><strong>Approach:</strong> compose dashboards from independent widget components, each owning its own data and loading state. Use <strong>react-grid-layout</strong> for resizable/draggable layout, persist to backend or localStorage. Each widget uses <strong>TanStack Query</strong> with appropriate <code>staleTime</code> and refetch interval.</p>

<pre><code>// === Widget primitive ===
function WidgetCard({ title, actions, children, isLoading, error }) {
  return (
    &lt;div className="widget"&gt;
      &lt;header className="widget-header"&gt;
        &lt;h3&gt;{title}&lt;/h3&gt;
        &lt;div&gt;{actions}&lt;/div&gt;
      &lt;/header&gt;
      &lt;div className="widget-body"&gt;
        {error ? &lt;ErrorState message={error.message} /&gt;
          : isLoading ? &lt;Skeleton /&gt;
          : children}
      &lt;/div&gt;
    &lt;/div&gt;
  );
}

// === Each widget owns its data fetching ===
function SalesChartWidget() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["sales-chart"],
    queryFn: () =&gt; api.getSalesChart(),
    refetchInterval: 60_000,
    staleTime: 30_000
  });

  return (
    &lt;WidgetCard
      title="Sales (30 days)"
      isLoading={isLoading} error={error}
      actions={&lt;button onClick={() =&gt; refetch()}&gt;↻&lt;/button&gt;}
    &gt;
      &lt;BarChart data={data} /&gt;
    &lt;/WidgetCard&gt;
  );
}

function KpiCardWidget({ kpi }) {
  const { data, isLoading } = useQuery({
    queryKey: ["kpi", kpi],
    queryFn: () =&gt; api.getKpi(kpi),
    staleTime: 60_000
  });

  return (
    &lt;WidgetCard title={data?.label ?? kpi} isLoading={isLoading}&gt;
      &lt;div className="kpi"&gt;
        &lt;span className="kpi-value"&gt;{data?.value}&lt;/span&gt;
        &lt;span className={`kpi-delta ${data?.delta &gt; 0 ? "up" : "down"}`}&gt;
          {data?.delta &gt; 0 ? "▲" : "▼"} {Math.abs(data?.delta ?? 0)}%
        &lt;/span&gt;
      &lt;/div&gt;
    &lt;/WidgetCard&gt;
  );
}

function RecentOrdersWidget() {
  const { data, isLoading } = useQuery({
    queryKey: ["recent-orders"],
    queryFn: () =&gt; api.getRecentOrders(10),
    refetchInterval: 30_000
  });

  return (
    &lt;WidgetCard title="Recent orders" isLoading={isLoading}&gt;
      &lt;ul&gt;
        {data?.map(o =&gt; (
          &lt;li key={o.id}&gt;
            #{o.id} &mdash; ${o.total} &mdash; {o.customer}
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/WidgetCard&gt;
  );
}</code></pre>

<pre><code>// === Resizable / draggable layout ===
import GridLayout from "react-grid-layout";

const DEFAULT_LAYOUT = [
  { i: "sales",   x: 0, y: 0, w: 8, h: 4 },
  { i: "kpi-rev", x: 8, y: 0, w: 4, h: 2 },
  { i: "kpi-ord", x: 8, y: 2, w: 4, h: 2 },
  { i: "orders",  x: 0, y: 4, w: 12, h: 4 }
];

function Dashboard() {
  const [layout, setLayout] = usePersistentState("dashboard-layout", DEFAULT_LAYOUT);

  return (
    &lt;GridLayout
      className="layout"
      layout={layout}
      cols={12}
      rowHeight={80}
      width={1200}
      onLayoutChange={setLayout}
      isDraggable
      isResizable
      draggableHandle=".widget-header"
    &gt;
      &lt;div key="sales"&gt;&lt;SalesChartWidget /&gt;&lt;/div&gt;
      &lt;div key="kpi-rev"&gt;&lt;KpiCardWidget kpi="revenue" /&gt;&lt;/div&gt;
      &lt;div key="kpi-ord"&gt;&lt;KpiCardWidget kpi="orders" /&gt;&lt;/div&gt;
      &lt;div key="orders"&gt;&lt;RecentOrdersWidget /&gt;&lt;/div&gt;
    &lt;/GridLayout&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Resolution</th></tr>
  <tr><td>N widgets = N parallel requests</td><td>Browser caps at 6 per origin (HTTP/1.1) &mdash; use HTTP/2 backend; or batch via GraphQL/single endpoint</td></tr>
  <tr><td>Same data needed by multiple widgets</td><td>TanStack Query dedupes by query key &mdash; one fetch shared</td></tr>
  <tr><td>Refetch frequency vs server load</td><td>Per-widget <code>staleTime</code> + <code>refetchInterval</code>; pause when tab hidden</td></tr>
  <tr><td>Widget independence</td><td>Each owns its loading/error state &mdash; one slow widget doesn&rsquo;t block others</td></tr>
  <tr><td>User customization</td><td>Layout to localStorage; sync to server for cross-device</td></tr>
  <tr><td>Mobile responsive</td><td>react-grid-layout&rsquo;s <code>ResponsiveGridLayout</code> with breakpoints</td></tr>
  <tr><td>Empty/error states per widget</td><td>Each widget renders own state &mdash; doesn&rsquo;t crash the dashboard</td></tr>
  <tr><td>Permissions</td><td>Hide widgets per role; server returns 403 for unauthorized data</td></tr>
</table>

<p><strong>Production-ready dashboard libraries:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>react-grid-layout</td><td>Custom dashboards with drag/resize</td></tr>
  <tr><td>Tremor</td><td>Tailwind-styled analytics dashboards out of the box</td></tr>
  <tr><td>Refine</td><td>Admin panels with auth/data layer integrated</td></tr>
  <tr><td>shadcn/ui blocks</td><td>Copy dashboard templates as starting point</td></tr>
  <tr><td>Recharts / Tremor Charts</td><td>Chart components for the widgets</td></tr>
</table>

<p><strong>For real-time dashboards</strong>, layer in WebSocket subscriptions or SSE for live KPIs (Q73). <strong>For huge datasets</strong>, server-side aggregation (don&rsquo;t fetch raw rows; fetch pre-aggregated stats) and virtualization. The architecture pattern stays the same; the data source changes.</p>
'''

ANSWERS[50] = r'''
<p><strong>Situation:</strong> Redux state changes need to fire async actions &mdash; fetch data, call APIs, talk to WebSockets, debounce/batch operations. Reducers must be pure, so async logic lives in middleware. The 2026 default: <strong>RTK Query</strong> for data fetching + <strong>createAsyncThunk</strong> for everything else.</p>

<p><strong>Approach:</strong> use Redux Toolkit. <strong>RTK Query</strong> auto-generates reducers, hooks, and cache for any HTTP API &mdash; handles loading/error/cache automatically. <strong>createAsyncThunk</strong> handles arbitrary async logic with auto-dispatched lifecycle actions (pending/fulfilled/rejected).</p>

<pre><code>// === RTK Query — for HTTP data ===
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: "/api",
    prepareHeaders: (headers, { getState }) =&gt; {
      const token = (getState() as RootState).auth.token;
      if (token) headers.set("Authorization", `Bearer ${token}`);
      return headers;
    }
  }),
  tagTypes: ["Post", "User"],
  endpoints: (build) =&gt; ({
    getPosts: build.query&lt;Post[], void&gt;({
      query: () =&gt; "/posts",
      providesTags: ["Post"]
    }),
    getPost: build.query&lt;Post, string&gt;({
      query: (id) =&gt; `/posts/${id}`,
      providesTags: (_, __, id) =&gt; [{ type: "Post", id }]
    }),
    createPost: build.mutation&lt;Post, Partial&lt;Post&gt;&gt;({
      query: (body) =&gt; ({ url: "/posts", method: "POST", body }),
      invalidatesTags: ["Post"]   // auto-refetches list
    }),
    deletePost: build.mutation&lt;void, string&gt;({
      query: (id) =&gt; ({ url: `/posts/${id}`, method: "DELETE" }),
      invalidatesTags: ["Post"]
    })
  })
});

export const { useGetPostsQuery, useGetPostQuery, useCreatePostMutation, useDeletePostMutation } = api;

// === In components — auto-handles loading/error/cache ===
function PostsList() {
  const { data: posts, isLoading, error } = useGetPostsQuery();
  const [createPost, { isLoading: isCreating }] = useCreatePostMutation();

  if (isLoading) return &lt;p&gt;Loading...&lt;/p&gt;;
  if (error)     return &lt;p&gt;{(error as any).data?.message ?? "Error"}&lt;/p&gt;;

  return (
    &lt;&gt;
      &lt;ul&gt;{posts?.map(p =&gt; &lt;li key={p.id}&gt;{p.title}&lt;/li&gt;)}&lt;/ul&gt;
      &lt;button
        onClick={() =&gt; createPost({ title: "New post" })}
        disabled={isCreating}
      &gt;
        New post
      &lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<pre><code>// === createAsyncThunk — for non-HTTP async (auth, complex flows) ===
import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

export const login = createAsyncThunk(
  "auth/login",
  async (credentials: { email: string; password: string }, { rejectWithValue }) =&gt; {
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();   // becomes payload of fulfilled action
    } catch (e: any) {
      return rejectWithValue(e.message);
    }
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState: { user: null, token: null, loading: false, error: null },
  reducers: {
    logout: (state) =&gt; { state.user = null; state.token = null; }
  },
  extraReducers: (builder) =&gt; {
    builder
      .addCase(login.pending, (state) =&gt; { state.loading = true; state.error = null; })
      .addCase(login.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(login.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.payload as string;
      });
  }
});

// Component dispatch
function LoginForm() {
  const dispatch = useAppDispatch();
  const { loading, error } = useAppSelector(s =&gt; s.auth);

  const handleSubmit = (e) =&gt; {
    e.preventDefault();
    dispatch(login({ email, password }));
  };

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      {/* ... inputs ... */}
      &lt;button disabled={loading}&gt;{loading ? "..." : "Sign in"}&lt;/button&gt;
      {error &amp;&amp; &lt;p className="err"&gt;{error}&lt;/p&gt;}
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Best for</th></tr>
  <tr><td>RTK Query</td><td>HTTP APIs &mdash; auto cache, refetch, invalidation; should be the default for fetching</td></tr>
  <tr><td>createAsyncThunk</td><td>Auth flows, file uploads, anything that doesn&rsquo;t cleanly fit "endpoint = data"</td></tr>
  <tr><td>Redux Saga</td><td>Complex orchestration, retry logic, rate limiting &mdash; reach for this only when thunks aren&rsquo;t enough</td></tr>
  <tr><td>Redux Observable (RxJS)</td><td>Streams, complex async pipelines &mdash; rare in 2026 React apps</td></tr>
  <tr><td>Listener middleware</td><td>React to actions with side effects (analytics, navigation, websocket connect on login)</td></tr>
</table>

<p><strong>2026 reality:</strong> for new apps, ask yourself if you need Redux at all. <strong>TanStack Query + Zustand</strong> handles 90% of state needs with less boilerplate. Redux Toolkit remains valuable for: large apps with strong action-log requirements (audit trails, undo/redo), teams already on Redux, complex middleware ecosystems. <strong>Don&rsquo;t put server data in client state</strong> &mdash; RTK Query (or TanStack Query) gives you cache, deduplication, refetch on focus, optimistic updates &mdash; manually replicating these in plain Redux is wasted effort. <strong>For optimistic updates</strong>, RTK Query has <code>onQueryStarted</code> + <code>updateQueryData</code> for the snapshot/rollback pattern.</p>
'''

ANSWERS[51] = r'''
<p><strong>Situation:</strong> a photo gallery shows hundreds of images. Loading all of them upfront wastes bandwidth and freezes the page; users may scroll only halfway. Lazy loading defers image fetches until they&rsquo;re about to enter the viewport &mdash; cutting initial weight by 70-80% on long galleries.</p>

<p><strong>Approach:</strong> use the <strong>native <code>loading="lazy"</code></strong> attribute as the foundation; layer on responsive sizing (<code>srcset</code> + <code>sizes</code>), modern formats (AVIF/WebP via <code>&lt;picture&gt;</code>), explicit dimensions to prevent CLS, and a placeholder/blur effect for perceived performance. For Next.js apps, <code>next/image</code> provides all of this in one component.</p>

<pre><code>import { useState } from "react";

function GalleryImage({ photo }) {
  const [loaded, setLoaded] = useState(false);

  return (
    &lt;div
      style={{
        position: "relative",
        aspectRatio: "1 / 1",
        background: "#f0f0f0",
        overflow: "hidden",
        borderRadius: 8
      }}
    &gt;
      {/* Tiny LQIP — loads instantly, blurs out as full image arrives */}
      &lt;img
        src={photo.thumbnailDataURL}
        alt=""
        aria-hidden
        style={{
          position: "absolute", inset: 0,
          width: "100%", height: "100%",
          filter: "blur(20px)",
          opacity: loaded ? 0 : 1,
          transition: "opacity 300ms"
        }}
      /&gt;

      &lt;picture&gt;
        &lt;source srcSet={photo.avif} type="image/avif" /&gt;
        &lt;source srcSet={photo.webp} type="image/webp" /&gt;
        &lt;img
          src={photo.jpeg}
          srcSet={photo.jpegSrcset}        // "/img-400.jpg 400w, /img-800.jpg 800w, ..."
          sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 33vw"
          alt={photo.alt}
          loading="lazy"                    // browser handles the rest
          decoding="async"
          onLoad={() =&gt; setLoaded(true)}
          width={400}
          height={400}
          style={{
            width: "100%", height: "100%",
            objectFit: "cover",
            opacity: loaded ? 1 : 0,
            transition: "opacity 300ms"
          }}
        /&gt;
      &lt;/picture&gt;
    &lt;/div&gt;
  );
}

function Gallery({ photos }) {
  return (
    &lt;div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: 8
      }}
    &gt;
      {photos.map(p =&gt; &lt;GalleryImage key={p.id} photo={p} /&gt;)}
    &lt;/div&gt;
  );
}

// === Or Next.js — much simpler ===
import Image from "next/image";

function NextGallery({ photos }) {
  return photos.map(p =&gt; (
    &lt;Image
      key={p.id}
      src={p.url}
      alt={p.alt}
      width={400}
      height={400}
      placeholder="blur"
      blurDataURL={p.blurDataURL}
      sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 33vw"
      priority={false}
    /&gt;
  ));
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Native <code>loading="lazy"</code></th><th>IntersectionObserver custom impl</th></tr>
  <tr><td>Setup cost</td><td>Zero</td><td>Custom hook + state</td></tr>
  <tr><td>Threshold control</td><td>Browser-decided</td><td>Configurable rootMargin</td></tr>
  <tr><td>Browser support</td><td>Universal since 2022</td><td>Universal</td></tr>
  <tr><td>Above-fold images</td><td>Should use <code>loading="eager"</code></td><td>Manual exclusion</td></tr>
</table>

<p><strong>Critical do&rsquo;s and don&rsquo;ts:</strong> always specify <code>width</code>/<code>height</code> (prevents CLS); use <code>fetchpriority="high"</code> on the LCP image; use <code>loading="eager"</code> for above-fold images (lazy loading them hurts LCP); serve AVIF/WebP first (30-50% smaller than JPEG); generate responsive sizes (<code>srcset</code>) so phones don&rsquo;t download desktop images. <strong>For production at scale</strong>: an image CDN (Cloudinary, imgix, Vercel Image Optimization) handles format negotiation, resizing, and caching automatically &mdash; you upload one source image and the CDN generates everything else on demand.</p>
'''

ANSWERS[52] = r'''
<p><strong>Situation:</strong> a form needs to submit data to a server, show success or error feedback, prevent double-submission, and handle network/validation failures gracefully. The pattern applies to almost every form in a real app &mdash; sign-up, contact, checkout, profile updates.</p>

<p><strong>Approach:</strong> use <strong>React Hook Form + Zod</strong> for validation; track submit state separately from form state; show specific error messages from the server; disable the form during submission to prevent duplicates. For React 19, <code>useActionState</code> + form actions is the modern alternative.</p>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState } from "react";

const schema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email"),
  message: z.string().min(10, "Message must be at least 10 characters")
});

type FormValues = z.infer&lt;typeof schema&gt;;

function ContactForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    reset
  } = useForm&lt;FormValues&gt;({ resolver: zodResolver(schema) });

  const [submitState, setSubmitState] = useState&lt;
    { type: "idle" | "success" | "error"; message?: string }
  &gt;({ type: "idle" });

  const onSubmit = async (data: FormValues) =&gt; {
    setSubmitState({ type: "idle" });

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() =&gt; ({}));

        // Map server-side field errors to specific fields
        if (errorData.fieldErrors) {
          Object.entries(errorData.fieldErrors).forEach(([field, message]) =&gt; {
            setError(field as keyof FormValues, { message: message as string });
          });
          return;
        }

        // Generic server error
        setSubmitState({
          type: "error",
          message: errorData.message || `Failed: ${res.status}`
        });
        return;
      }

      setSubmitState({ type: "success", message: "Thanks &mdash; we&rsquo;ll be in touch!" });
      reset();   // clear form
    } catch (err: any) {
      setSubmitState({
        type: "error",
        message: err.name === "TypeError" ? "Network error" : err.message
      });
    }
  };

  if (submitState.type === "success") {
    return (
      &lt;div role="status" className="success-card"&gt;
        ✓ {submitState.message}
        &lt;button onClick={() =&gt; setSubmitState({ type: "idle" })}&gt;Send another&lt;/button&gt;
      &lt;/div&gt;
    );
  }

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)} noValidate&gt;
      &lt;input
        {...register("name")}
        placeholder="Name"
        disabled={isSubmitting}
        aria-invalid={!!errors.name}
      /&gt;
      {errors.name &amp;&amp; &lt;p className="err"&gt;{errors.name.message}&lt;/p&gt;}

      &lt;input
        {...register("email")}
        type="email"
        placeholder="Email"
        disabled={isSubmitting}
        aria-invalid={!!errors.email}
      /&gt;
      {errors.email &amp;&amp; &lt;p className="err"&gt;{errors.email.message}&lt;/p&gt;}

      &lt;textarea
        {...register("message")}
        placeholder="Message"
        disabled={isSubmitting}
        aria-invalid={!!errors.message}
      /&gt;
      {errors.message &amp;&amp; &lt;p className="err"&gt;{errors.message.message}&lt;/p&gt;}

      {submitState.type === "error" &amp;&amp; (
        &lt;p role="alert" className="err-banner"&gt;✗ {submitState.message}&lt;/p&gt;
      )}

      &lt;button type="submit" disabled={isSubmitting}&gt;
        {isSubmitting ? "Sending..." : "Send"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Use when</th></tr>
  <tr><td>React Hook Form + Zod</td><td>Production default; uncontrolled inputs (fast), schema validation, server error mapping</td></tr>
  <tr><td>Manual <code>useState</code> + <code>onSubmit</code></td><td>Tiny forms (1-2 fields); good for understanding the basics</td></tr>
  <tr><td>React 19 <code>useActionState</code></td><td>Server Actions (Next.js); FormData-driven submission; minimal client code</td></tr>
  <tr><td>Formik (legacy)</td><td>Existing codebases; new projects shouldn&rsquo;t adopt &mdash; prefer RHF</td></tr>
</table>

<p><strong>Critical UX details</strong>: disable inputs <em>and</em> button during submit (prevents double-submission); distinguish field-level errors (next to input) from form-level errors (banner); reset only after a confirmed success; show loading state inline (button text); offer a clear &ldquo;send another&rdquo; path after success. <strong>Server-side errors</strong> should map to specific fields when possible (e.g., &ldquo;email already exists&rdquo; → set on email field) so users can fix without searching.</p>
'''

ANSWERS[53] = r'''
<p><strong>Situation:</strong> users need to reorder a list by dragging items. Use cases: priority queue, kanban columns, photo album, playlists, settings preferences. Modern solution: <strong>dnd-kit</strong> &mdash; accessible, touch-friendly, the de-facto standard since react-beautiful-dnd was archived in late 2023.</p>

<p><strong>Approach:</strong> wrap the list in <code>&lt;DndContext&gt;</code> + <code>&lt;SortableContext&gt;</code>; each item uses the <code>useSortable</code> hook for drag/drop affordances. On drag end, use <code>arrayMove</code> to reorder the array in state. Add keyboard sensors for accessibility &mdash; arrow keys + Enter must move items.</p>

<pre><code>import { useState } from "react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

type Task = { id: string; title: string; priority: "high" | "med" | "low" };

function SortableRow({ task }: { task: Task }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: task.id });

  return (
    &lt;li
      ref={setNodeRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.4 : 1,
        padding: 12,
        margin: "4px 0",
        background: "#f9fafb",
        border: "1px solid #e5e7eb",
        borderRadius: 6,
        cursor: "grab",
        display: "flex",
        gap: 8,
        userSelect: "none"
      }}
      {...attributes}
      {...listeners}
    &gt;
      &lt;span aria-hidden&gt;⋮⋮&lt;/span&gt;
      &lt;span&gt;{task.title}&lt;/span&gt;
      &lt;span style={{ marginLeft: "auto", opacity: 0.6 }}&gt;{task.priority}&lt;/span&gt;
    &lt;/li&gt;
  );
}

function SortableTaskList() {
  const [tasks, setTasks] = useState&lt;Task[]&gt;([
    { id: "1", title: "Review PR #42",  priority: "high" },
    { id: "2", title: "Update docs",     priority: "low"  },
    { id: "3", title: "Deploy staging",  priority: "med"  },
    { id: "4", title: "Run integration tests", priority: "med" }
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = async (event: any) =&gt; {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = tasks.findIndex(t =&gt; t.id === active.id);
    const newIndex = tasks.findIndex(t =&gt; t.id === over.id);
    const newOrder = arrayMove(tasks, oldIndex, newIndex);

    setTasks(newOrder);

    // Persist to backend
    try {
      await fetch("/api/tasks/reorder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids: newOrder.map(t =&gt; t.id) })
      });
    } catch (err) {
      // Rollback on failure
      setTasks(tasks);
      toast.error("Failed to save order");
    }
  };

  return (
    &lt;DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    &gt;
      &lt;SortableContext items={tasks} strategy={verticalListSortingStrategy}&gt;
        &lt;ul style={{ listStyle: "none", padding: 0 }}&gt;
          {tasks.map(task =&gt; (
            &lt;SortableRow key={task.id} task={task} /&gt;
          ))}
        &lt;/ul&gt;
      &lt;/SortableContext&gt;
    &lt;/DndContext&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Library</th><th>2026 status</th><th>Best for</th></tr>
  <tr><td>dnd-kit</td><td>Active, recommended</td><td>Most use cases &mdash; lists, grids, multi-container</td></tr>
  <tr><td>react-beautiful-dnd</td><td>Archived 2023; React 18 issues</td><td>Don&rsquo;t use for new code</td></tr>
  <tr><td>HTML5 drag API</td><td>Built-in, no deps</td><td>Simple cases; no mobile/touch support</td></tr>
  <tr><td>react-grid-layout</td><td>Active</td><td>Grid dashboards specifically (resize + drag)</td></tr>
</table>

<p><strong>Production concerns</strong>: persist new order via API (debounce or batch if rapid drags); rollback optimistically applied changes on failure; show subtle drag preview (dnd-kit&rsquo;s <code>DragOverlay</code> for sticky preview); distinguish drag from click (<code>activationConstraint: { distance: 5 }</code>); test keyboard flow (Tab → Space picks up → arrows move → Space drops); add <code>aria-live</code> announcements for screen readers (dnd-kit provides defaults). <strong>Multi-container drag</strong> (Trello-style) uses one <code>DndContext</code> wrapping multiple <code>SortableContext</code> &mdash; one per column.</p>
'''

ANSWERS[54] = r'''
<p><strong>Situation:</strong> a component holds local state that should reset when a key prop changes &mdash; e.g., a profile editor showing user A&rsquo;s data; user prop switches to user B; the form must reset to user B&rsquo;s data, not retain user A&rsquo;s edits. Several patterns solve this; the right choice depends on whether you control the component or it&rsquo;s third-party.</p>

<p><strong>Approach:</strong> the cleanest solution is the <strong><code>key</code> prop trick</strong> &mdash; changing the key forces React to unmount and remount, which resets all internal state. For more nuanced control, derive state from props during render (no <code>useEffect</code> needed) or use the <code>useEffect</code> + <code>useState</code> pattern as a last resort.</p>

<pre><code>// === Pattern 1: key prop (recommended) ===
function App() {
  const [selectedUserId, setSelectedUserId] = useState("user-1");

  return (
    &lt;&gt;
      &lt;UserSelector value={selectedUserId} onChange={setSelectedUserId} /&gt;
      {/* When userId changes, ProfileEditor unmounts and remounts → state resets */}
      &lt;ProfileEditor key={selectedUserId} userId={selectedUserId} /&gt;
    &lt;/&gt;
  );
}

function ProfileEditor({ userId }) {
  // All this state resets automatically when userId (and therefore key) changes
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [bio, setBio] = useState("");

  useEffect(() =&gt; {
    fetch(`/api/users/${userId}`)
      .then(r =&gt; r.json())
      .then(user =&gt; {
        setName(user.name);
        setEmail(user.email);
        setBio(user.bio);
      });
  }, [userId]);

  return (
    &lt;form&gt;
      &lt;input value={name} onChange={e =&gt; setName(e.target.value)} /&gt;
      &lt;input value={email} onChange={e =&gt; setEmail(e.target.value)} /&gt;
      &lt;textarea value={bio} onChange={e =&gt; setBio(e.target.value)} /&gt;
    &lt;/form&gt;
  );
}

// === Pattern 2: derive during render (better when possible) ===
function ProductCard({ product }) {
  // No useEffect needed — derive directly
  const formattedPrice = useMemo(
    () =&gt; new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" })
                  .format(product.price),
    [product.price]
  );
  return &lt;p&gt;{product.name}: {formattedPrice}&lt;/p&gt;;
}

// === Pattern 3: track previous prop and reset on change ===
function Counter({ initialValue }) {
  const [count, setCount] = useState(initialValue);
  const [prevInitial, setPrevInitial] = useState(initialValue);

  // This runs DURING render — that&rsquo;s OK for state setters!
  if (prevInitial !== initialValue) {
    setPrevInitial(initialValue);
    setCount(initialValue);   // reset
  }

  return &lt;button onClick={() =&gt; setCount(c =&gt; c + 1)}&gt;{count}&lt;/button&gt;;
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pattern</th><th>Pros</th><th>Cons</th></tr>
  <tr><td><code>key</code> prop</td><td>Simple; full reset; no extra code</td><td>Loses focus, scroll position; expensive if subtree is large</td></tr>
  <tr><td>Derive during render</td><td>No state at all; always in sync</td><td>Only works if value is purely derived (no user edits)</td></tr>
  <tr><td>Track previous prop + reset</td><td>Fine-grained control</td><td>Extra state; React 19 prefers this less than <code>key</code></td></tr>
  <tr><td><code>useEffect</code> reset</td><td>Familiar</td><td>Anti-pattern &mdash; double render, infinite loop risk</td></tr>
</table>

<p><strong>The <code>useEffect</code> anti-pattern to avoid</strong>:</p>

<pre><code>// ❌ Don&rsquo;t do this — extra render, harder to reason about
useEffect(() =&gt; {
  setCount(initialValue);
}, [initialValue]);</code></pre>

<p>This causes two renders (initial render with stale state → effect fires → setState → re-render). Worse, the user briefly sees stale state. <code>key</code> prop or in-render reset both avoid this.</p>

<p><strong>When to choose what</strong>: if state is fully derived from props, derive it &mdash; don&rsquo;t store it. If state involves user input that should reset on prop change, use <code>key</code> for full reset OR the in-render reset pattern for partial reset. Reach for <code>useEffect</code> only when you need a side effect (network call, subscription) &mdash; not for syncing state.</p>
'''

ANSWERS[55] = r'''
<p><strong>Situation:</strong> a login form needs a "Remember me" checkbox &mdash; checked → keep user signed in across browser restarts; unchecked → log out when the browser closes. The mechanism choice (long-lived JWT in localStorage vs httpOnly cookies vs refresh tokens) has real security implications.</p>

<p><strong>Approach:</strong> for production security, use <strong>httpOnly cookies</strong> for the auth token (immune to XSS); the &ldquo;remember me&rdquo; flag is sent to the server, which sets either a session cookie (no expiry &mdash; cleared on browser close) or a long-lived cookie (e.g., 30 days). Pair with refresh token rotation for high-security apps. For lower-security/internal apps, JWT in <code>localStorage</code> (remember me) vs <code>sessionStorage</code> (session only) works.</p>

<pre><code>import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email("Valid email required"),
  password: z.string().min(1, "Password required"),
  rememberMe: z.boolean().default(false)
});
type FormValues = z.infer&lt;typeof schema&gt;;

function LoginForm() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  const {
    register, handleSubmit, formState: { errors, isSubmitting }
  } = useForm&lt;FormValues&gt;({
    resolver: zodResolver(schema),
    // Persist email if user previously checked remember me
    defaultValues: {
      email: localStorage.getItem("rememberedEmail") || "",
      rememberMe: !!localStorage.getItem("rememberedEmail")
    }
  });

  const onSubmit = async (data: FormValues) =&gt; {
    setError("");

    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",     // include cookies in CORS requests
        body: JSON.stringify({
          email: data.email,
          password: data.password,
          rememberMe: data.rememberMe
          // Server handles cookie expiry based on rememberMe
        })
      });

      if (!res.ok) {
        const { message } = await res.json().catch(() =&gt; ({}));
        throw new Error(message || "Sign in failed");
      }

      // Save email locally if user opted to be remembered
      if (data.rememberMe) {
        localStorage.setItem("rememberedEmail", data.email);
      } else {
        localStorage.removeItem("rememberedEmail");
      }

      navigate("/dashboard", { replace: true });
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)}&gt;
      &lt;input
        type="email"
        placeholder="Email"
        autoComplete="email"
        {...register("email")}
        disabled={isSubmitting}
      /&gt;
      {errors.email &amp;&amp; &lt;p className="err"&gt;{errors.email.message}&lt;/p&gt;}

      &lt;input
        type="password"
        placeholder="Password"
        autoComplete="current-password"
        {...register("password")}
        disabled={isSubmitting}
      /&gt;
      {errors.password &amp;&amp; &lt;p className="err"&gt;{errors.password.message}&lt;/p&gt;}

      &lt;label&gt;
        &lt;input type="checkbox" {...register("rememberMe")} /&gt;
        Remember me on this device
      &lt;/label&gt;

      {error &amp;&amp; &lt;p role="alert" className="err"&gt;✗ {error}&lt;/p&gt;}

      &lt;button type="submit" disabled={isSubmitting}&gt;
        {isSubmitting ? "Signing in..." : "Sign in"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}

// === Server-side cookie setting (Express / Hono / Next.js Route Handler) ===
// app.post("/api/login", async (req, res) =&gt; {
//   const { email, password, rememberMe } = req.body;
//   const token = await authenticateUser(email, password);
//
//   res.cookie("auth", token, {
//     httpOnly: true,
//     secure: true,
//     sameSite: "lax",
//     maxAge: rememberMe ? 30 * 24 * 60 * 60 * 1000 : undefined  // session cookie if not
//   });
//   res.json({ ok: true });
// });</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Storage</th><th>"Remember me"</th><th>"Session only"</th><th>XSS safe?</th></tr>
  <tr><td>httpOnly cookie</td><td>maxAge: 30d</td><td>No maxAge</td><td>✓ Yes</td></tr>
  <tr><td>localStorage</td><td>Set token</td><td>(don&rsquo;t use for session-only)</td><td>✗ No</td></tr>
  <tr><td>sessionStorage</td><td>(doesn&rsquo;t persist)</td><td>Set token</td><td>✗ No</td></tr>
  <tr><td>Refresh token + access token</td><td>Long refresh expiry</td><td>Short refresh expiry</td><td>✓ With httpOnly</td></tr>
</table>

<p><strong>Critical security notes</strong>: <code>localStorage</code>-stored JWTs are vulnerable to any XSS &mdash; a single injected script can exfiltrate them. Cookies with <code>httpOnly</code> + <code>SameSite=Lax</code> + <code>Secure</code> are immune to XSS reads but require CSRF protection. <strong>For new apps in 2026</strong>: use a managed auth service (Clerk, Supabase Auth, Auth0, NextAuth.js) &mdash; they handle remember-me, refresh tokens, session management, and security correctly. Don&rsquo;t store the password in localStorage even if "remember me" is checked &mdash; only the email at most.</p>
'''

ANSWERS[56] = r'''
<p><strong>Situation:</strong> an app makes API calls from many components. Without centralized error handling, every component repeats try/catch logic, errors get displayed inconsistently, and unauthenticated 401s aren&rsquo;t globally redirecting to login. Need one place to intercept failures, classify them, and respond consistently.</p>

<p><strong>Approach:</strong> use a <strong>fetch wrapper</strong> or <strong>axios interceptors</strong> to centralize error handling. Combine with <strong>TanStack Query</strong>&rsquo;s built-in retry/error machinery and a global error boundary for render errors. Send all production errors to <strong>Sentry</strong> for monitoring. Show a global error toast for unrecoverable errors; let components show inline messages for expected errors.</p>

<pre><code>// === Centralized fetch wrapper ===
import * as Sentry from "@sentry/react";

class ApiError extends Error {
  constructor(public status: number, public body: any, message: string) {
    super(message);
  }
}

async function api(url: string, options: RequestInit = {}) {
  const token = getAuthToken();

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token &amp;&amp; { Authorization: `Bearer ${token}` }),
      ...options.headers
    },
    credentials: "include"
  });

  // Auth expired — redirect to login
  if (res.status === 401) {
    clearAuthToken();
    window.location.href = "/login?expired=1";
    throw new ApiError(401, null, "Session expired");
  }

  // Forbidden
  if (res.status === 403) {
    throw new ApiError(403, await res.json(), "You don&rsquo;t have access");
  }

  // Rate limit — caller can retry with backoff
  if (res.status === 429) {
    const retryAfter = res.headers.get("Retry-After");
    throw new ApiError(429, { retryAfter }, "Too many requests");
  }

  // Server error — log to Sentry
  if (res.status &gt;= 500) {
    const body = await res.json().catch(() =&gt; null);
    Sentry.captureException(new Error(`API ${res.status} on ${url}`), {
      extra: { url, status: res.status, body }
    });
    throw new ApiError(res.status, body, "Server error");
  }

  // Client error
  if (!res.ok) {
    const body = await res.json().catch(() =&gt; ({}));
    throw new ApiError(res.status, body, body.message || "Request failed");
  }

  return res.json();
}

// === TanStack Query global config ===
import { QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) =&gt; {
        // Don&rsquo;t retry 4xx errors — they won&rsquo;t change
        if (error instanceof ApiError &amp;&amp; error.status &gt;= 400 &amp;&amp; error.status &lt; 500) {
          return false;
        }
        return failureCount &lt; 3;
      },
      retryDelay: (attempt) =&gt; Math.min(1000 * 2 ** attempt, 30000),
      staleTime: 60 * 1000
    },
    mutations: {
      // Surface mutation errors as toasts globally
      onError: (error: any) =&gt; {
        if (error instanceof ApiError &amp;&amp; error.status === 429) {
          toast.error(`Rate limited. Try again in ${error.body.retryAfter}s.`);
          return;
        }
        toast.error(error.message || "Something went wrong");
      }
    }
  }
});

// === Use in components ===
function useUser(userId: string) {
  return useQuery({
    queryKey: ["users", userId],
    queryFn: () =&gt; api(`/api/users/${userId}`)
  });
}

// === Global error boundary for render errors ===
function App() {
  return (
    &lt;Sentry.ErrorBoundary
      fallback={({ error, resetError }) =&gt; (
        &lt;div role="alert"&gt;
          &lt;h1&gt;Something went wrong&lt;/h1&gt;
          &lt;button onClick={resetError}&gt;Try again&lt;/button&gt;
        &lt;/div&gt;
      )}
      showDialog
    &gt;
      &lt;Routes&gt;...&lt;/Routes&gt;
    &lt;/Sentry.ErrorBoundary&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Error type</th><th>Where to handle</th><th>UX response</th></tr>
  <tr><td>401 expired</td><td>Fetch wrapper</td><td>Redirect to login</td></tr>
  <tr><td>403 forbidden</td><td>Component</td><td>Inline message ("You don&rsquo;t have access")</td></tr>
  <tr><td>404 not found</td><td>Component</td><td>"Resource not found" page or message</td></tr>
  <tr><td>422 validation</td><td>Component</td><td>Field-level error mapping</td></tr>
  <tr><td>429 rate limit</td><td>Wrapper + caller</td><td>Toast + automatic retry with backoff</td></tr>
  <tr><td>500 server error</td><td>Wrapper</td><td>Toast + Sentry capture</td></tr>
  <tr><td>Network error</td><td>Wrapper</td><td>Toast: "Check your connection"</td></tr>
  <tr><td>Render error</td><td>Error boundary</td><td>Fallback UI + Sentry capture</td></tr>
</table>

<p><strong>Critical principle</strong>: not all errors are equal. <strong>Recoverable errors</strong> (network blip, rate limit) → retry automatically. <strong>User errors</strong> (validation) → inline feedback. <strong>System errors</strong> (500, render crash) → log to Sentry + show fallback. <strong>Auth errors</strong> → centralized redirect. Don&rsquo;t blanket every error with "Something went wrong" &mdash; specific messages let users self-correct.</p>
'''

ANSWERS[57] = r'''
<p><strong>Situation:</strong> users will visit URLs that don&rsquo;t exist, navigate to deleted resources, or hit unhandled exceptions during page load. Default browser 404s and white-screen JS crashes feel broken. Custom 404 and 500 pages give users a way out (link home, search, contact support) and let you log the failure for fixing.</p>

<p><strong>Approach:</strong> for 404, use React Router&rsquo;s catch-all route (<code>path="*"</code>) and conditional rendering when API resource is missing. For 500 (render crashes and unhandled errors), use error boundaries. In Next.js, use <code>not-found.tsx</code> and <code>error.tsx</code> conventions per route segment.</p>

<pre><code>// === React Router 404 ===
import { Routes, Route, Link, useNavigate, useLocation } from "react-router-dom";

function NotFound() {
  const location = useLocation();

  // Log unknown URLs — useful for finding broken links
  useEffect(() =&gt; {
    Sentry.addBreadcrumb({
      category: "404",
      message: `User hit unknown URL: ${location.pathname}`
    });
  }, [location.pathname]);

  return (
    &lt;div className="error-page"&gt;
      &lt;h1&gt;404 &mdash; Page not found&lt;/h1&gt;
      &lt;p&gt;The page &lt;code&gt;{location.pathname}&lt;/code&gt; doesn&rsquo;t exist.&lt;/p&gt;
      &lt;ul&gt;
        &lt;li&gt;&lt;Link to="/"&gt;Go home&lt;/Link&gt;&lt;/li&gt;
        &lt;li&gt;&lt;Link to="/search"&gt;Search the site&lt;/Link&gt;&lt;/li&gt;
        &lt;li&gt;&lt;Link to="/contact"&gt;Contact support&lt;/Link&gt;&lt;/li&gt;
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}

function App() {
  return (
    &lt;Routes&gt;
      &lt;Route path="/" element={&lt;Home /&gt;} /&gt;
      &lt;Route path="/products" element={&lt;Products /&gt;} /&gt;
      &lt;Route path="/products/:id" element={&lt;ProductDetail /&gt;} /&gt;
      &lt;Route path="*" element={&lt;NotFound /&gt;} /&gt;       {/* catch-all */}
    &lt;/Routes&gt;
  );
}

// === Resource-level 404 (existing route, missing data) ===
function ProductDetail() {
  const { id } = useParams();
  const { data, error, isLoading } = useQuery({
    queryKey: ["products", id],
    queryFn: () =&gt; api(`/api/products/${id}`)
  });

  if (isLoading) return &lt;Spinner /&gt;;

  if (error instanceof ApiError &amp;&amp; error.status === 404) {
    return (
      &lt;div className="error-page"&gt;
        &lt;h1&gt;Product not found&lt;/h1&gt;
        &lt;p&gt;This product may have been removed.&lt;/p&gt;
        &lt;Link to="/products"&gt;Browse all products&lt;/Link&gt;
      &lt;/div&gt;
    );
  }

  if (error) throw error;   // let error boundary handle 500s

  return &lt;ProductView product={data} /&gt;;
}

// === 500 / generic error boundary ===
import { ErrorBoundary } from "react-error-boundary";

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    &lt;div role="alert" className="error-page"&gt;
      &lt;h1&gt;Something went wrong&lt;/h1&gt;
      &lt;p&gt;Our team has been notified. You can try again or go home.&lt;/p&gt;

      {process.env.NODE_ENV === "development" &amp;&amp; (
        &lt;pre style={{ color: "red" }}&gt;{error.message}&lt;/pre&gt;
      )}

      &lt;button onClick={resetErrorBoundary}&gt;Try again&lt;/button&gt;
      &lt;Link to="/"&gt;Go home&lt;/Link&gt;
    &lt;/div&gt;
  );
}

function App() {
  return (
    &lt;ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, info) =&gt; Sentry.captureException(error, { extra: info })}
      onReset={() =&gt; { /* navigate, clear state, etc. */ }}
    &gt;
      &lt;Routes&gt;...&lt;/Routes&gt;
    &lt;/ErrorBoundary&gt;
  );
}

// === Next.js conventions (App Router) ===
// app/not-found.tsx — global 404
export default function NotFound() {
  return &lt;div&gt;Page not found. &lt;Link href="/"&gt;Home&lt;/Link&gt;&lt;/div&gt;;
}

// app/products/[id]/not-found.tsx — segment-specific 404
// app/error.tsx — global 500 (must be a Client Component)
"use client";
export default function Error({ error, reset }: any) {
  useEffect(() =&gt; { Sentry.captureException(error); }, [error]);
  return (
    &lt;div&gt;
      &lt;h1&gt;Something went wrong&lt;/h1&gt;
      &lt;button onClick={reset}&gt;Try again&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>What it catches</th></tr>
  <tr><td>Catch-all route (<code>path="*"</code>)</td><td>Unknown URLs (404)</td></tr>
  <tr><td>Conditional render in component</td><td>Resource missing (data 404)</td></tr>
  <tr><td>Error boundary</td><td>Render-time exceptions, render-thrown errors</td></tr>
  <tr><td>Global onerror / unhandledrejection</td><td>Async errors outside React tree</td></tr>
  <tr><td>Server-side fallback</td><td>Direct URL hits / SSR errors</td></tr>
</table>

<p><strong>Server config matters</strong>: BrowserRouter URLs need server fallback to <code>index.html</code> &mdash; without it, refreshing on <code>/products/42</code> hits the server, which returns its own 404 (not your React 404). Configure: Vercel/Netlify auto-handle this; nginx needs <code>try_files $uri $uri/ /index.html;</code>. <strong>SEO note</strong>: real 404 pages should return HTTP status 404 (not 200). With SPAs this requires server cooperation; with Next.js / Remix, frameworks set the status correctly.</p>

<p><strong>UX details that matter</strong>: don&rsquo;t blame the user (&ldquo;You went the wrong way&rdquo;); offer 2-3 escape paths (home, search, support); preserve the URL for analytics; reset error boundary state when navigating away (<code>resetKeys</code> with route changes). Production error pages also need basic styling that works without the rest of the app loading &mdash; if a chunk fails to load, the error page must still render.</p>
'''

ANSWERS[58] = r'''
<p><strong>Situation:</strong> a React app needs to manage user sessions: store the auth token securely, attach it to API requests, refresh expired tokens automatically, log users out cleanly, and survive page refreshes. The 2026 sweet spot: <strong>httpOnly cookies + refresh token rotation</strong> for security; <strong>Clerk/Supabase/Auth0</strong> for managed solutions.</p>

<p><strong>Approach:</strong> use httpOnly cookies for tokens (XSS-safe). Implement refresh token rotation: short-lived access token (15 min) + long-lived refresh token (30 days). On 401, attempt token refresh; if refresh fails, redirect to login. Store auth state in React Context for synchronous access; sync with the cookie via API calls.</p>

<pre><code>import { createContext, useContext, useState, useEffect, useCallback } from "react";

type User = { id: string; email: string; role: string };

type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) =&gt; Promise&lt;void&gt;;
  logout: () =&gt; Promise&lt;void&gt;;
  refresh: () =&gt; Promise&lt;boolean&gt;;
};

const AuthContext = createContext&lt;AuthContextType | null&gt;(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState&lt;User | null&gt;(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount, check for existing session via httpOnly cookie
  useEffect(() =&gt; {
    fetch("/api/me", { credentials: "include" })
      .then(r =&gt; r.ok ? r.json() : null)
      .then(setUser)
      .finally(() =&gt; setIsLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) =&gt; {
    const res = await fetch("/api/login", {
      method: "POST",
      credentials: "include",                // server sets httpOnly cookies
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error("Sign in failed");
    setUser(await res.json());
  }, []);

  const logout = useCallback(async () =&gt; {
    await fetch("/api/logout", { method: "POST", credentials: "include" });
    setUser(null);
    queryClient.clear();                     // wipe cached data
  }, []);

  const refresh = useCallback(async () =&gt; {
    try {
      const res = await fetch("/api/refresh", {
        method: "POST",
        credentials: "include"
      });
      if (!res.ok) throw new Error("Refresh failed");
      setUser(await res.json());
      return true;
    } catch {
      setUser(null);
      return false;
    }
  }, []);

  return (
    &lt;AuthContext.Provider value={{ user, isLoading, login, logout, refresh }}&gt;
      {children}
    &lt;/AuthContext.Provider&gt;
  );
}

export const useAuth = () =&gt; {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};

// === Auto-refresh on 401 with single-flight protection ===
let refreshPromise: Promise&lt;boolean&gt; | null = null;

async function fetchWithRefresh(url: string, options: RequestInit = {}) {
  let res = await fetch(url, { ...options, credentials: "include" });

  if (res.status === 401) {
    // Coalesce multiple simultaneous 401s into one refresh attempt
    if (!refreshPromise) {
      refreshPromise = fetch("/api/refresh", { method: "POST", credentials: "include" })
        .then(r =&gt; r.ok)
        .finally(() =&gt; { refreshPromise = null; });
    }
    const ok = await refreshPromise;

    if (ok) {
      // Retry original request with new token (set by server in cookie)
      res = await fetch(url, { ...options, credentials: "include" });
    } else {
      window.location.href = "/login?expired=1";
      throw new Error("Session expired");
    }
  }

  return res;
}

// === Cross-tab sync ===
useEffect(() =&gt; {
  const channel = new BroadcastChannel("auth");
  channel.onmessage = (e) =&gt; {
    if (e.data.type === "LOGOUT") {
      setUser(null);
      queryClient.clear();
    }
  };
  return () =&gt; channel.close();
}, []);

// In logout(): channel.postMessage({ type: "LOGOUT" });</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Security</th><th>Complexity</th><th>2026 use</th></tr>
  <tr><td>httpOnly cookie + refresh rotation</td><td>High &mdash; XSS-immune</td><td>Server-side complexity</td><td>Recommended for security-sensitive apps</td></tr>
  <tr><td>Managed auth (Clerk, Supabase, Auth0)</td><td>High &mdash; outsourced</td><td>Low</td><td>Default for new apps</td></tr>
  <tr><td>JWT in localStorage</td><td>Low &mdash; XSS-vulnerable</td><td>Low</td><td>Only for internal/low-stakes apps</td></tr>
  <tr><td>NextAuth.js / Auth.js</td><td>High &mdash; httpOnly by default</td><td>Low for Next.js</td><td>Recommended for Next.js</td></tr>
</table>

<p><strong>Critical security details</strong>: <strong>refresh token rotation</strong> &mdash; each refresh issues a new refresh token; reusing an old one is a sign of theft and revokes the family. <strong>Single-flight protection</strong> &mdash; multiple 401s should trigger one refresh, not N. <strong>Cross-tab sync</strong> &mdash; BroadcastChannel lets logout in one tab log out all others. <strong>CSRF protection</strong> &mdash; cookies need <code>SameSite=Lax</code> + CSRF tokens for sensitive operations. <strong>Don&rsquo;t implement crypto/signing yourself</strong>; use established libraries (jose, jsonwebtoken with proven config) or managed services.</p>
'''

ANSWERS[59] = r'''
<p><strong>Situation:</strong> an app needs centralized theme management &mdash; light/dark mode, accent color, font size preferences, density. Every component must respond to changes consistently; user preferences should persist across sessions and respect OS-level settings. Repeated styling logic per component is a maintenance disaster.</p>

<p><strong>Approach:</strong> single source of truth in a <strong>ThemeProvider</strong> using Context. Theme drives a <code>data-theme</code> attribute on the root; CSS variables resolve based on that attribute &mdash; all styling responds via CSS, not JS. Persist choice to localStorage; respect <code>prefers-color-scheme</code> for default; inline a script in HTML head to prevent flash of unstyled content (FOUC).</p>

<pre><code>// === ThemeProvider ===
import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

type ThemeContextType = {
  theme: Theme;
  resolvedTheme: "light" | "dark";   // what&rsquo;s actually applied
  setTheme: (theme: Theme) =&gt; void;
};

const ThemeContext = createContext&lt;ThemeContextType | null&gt;(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState&lt;Theme&gt;(() =&gt; {
    return (localStorage.getItem("theme") as Theme) || "system";
  });

  // Compute what theme is actually applied (resolve "system")
  const [resolvedTheme, setResolvedTheme] = useState&lt;"light" | "dark"&gt;(() =&gt; {
    if (theme === "dark") return "dark";
    if (theme === "light") return "light";
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  // Update DOM and resolved theme when theme changes or OS preference changes
  useEffect(() =&gt; {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");

    const apply = () =&gt; {
      const next: "light" | "dark" =
        theme === "system" ? (mq.matches ? "dark" : "light") : theme;
      setResolvedTheme(next);
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("theme", theme);
    };

    apply();

    // React to OS preference changes if user is on "system"
    if (theme === "system") {
      mq.addEventListener("change", apply);
      return () =&gt; mq.removeEventListener("change", apply);
    }
  }, [theme]);

  return (
    &lt;ThemeContext.Provider value={{ theme, resolvedTheme, setTheme: setThemeState }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

export const useTheme = () =&gt; {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme inside ThemeProvider");
  return ctx;
};

// === Theme toggle component ===
function ThemeToggle() {
  const { theme, resolvedTheme, setTheme } = useTheme();

  return (
    &lt;select value={theme} onChange={e =&gt; setTheme(e.target.value as Theme)}&gt;
      &lt;option value="light"&gt;☀ Light&lt;/option&gt;
      &lt;option value="dark"&gt;🌙 Dark&lt;/option&gt;
      &lt;option value="system"&gt;💻 System ({resolvedTheme})&lt;/option&gt;
    &lt;/select&gt;
  );
}</code></pre>

<pre><code>/* === Tokens via CSS variables === */
:root {
  --bg:           #ffffff;
  --bg-elevated:  #f9fafb;
  --text:         #111827;
  --text-muted:   #6b7280;
  --primary:      #3b82f6;
  --border:       #e5e7eb;
  --shadow:       0 1px 3px rgba(0, 0, 0, 0.08);
}

[data-theme="dark"] {
  --bg:           #0f172a;
  --bg-elevated:  #1e293b;
  --text:         #f8fafc;
  --text-muted:   #94a3b8;
  --primary:      #60a5fa;
  --border:       #334155;
  --shadow:       0 1px 3px rgba(0, 0, 0, 0.4);
}

body { background: var(--bg); color: var(--text); transition: background 200ms; }
.card { background: var(--bg-elevated); border: 1px solid var(--border); }</code></pre>

<pre><code>&lt;!-- Inline in &lt;head&gt; — prevents flash of wrong theme on initial load --&gt;
&lt;script&gt;
  (function() {
    const stored = localStorage.getItem("theme") || "system";
    const isDark = stored === "dark" ||
      (stored === "system" &amp;&amp; matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
  })();
&lt;/script&gt;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>data-theme + CSS vars</td><td>Performant; framework-agnostic; no JS per component</td><td>Need consistent CSS architecture</td></tr>
  <tr><td>Tailwind dark mode</td><td>Built-in; <code>dark:</code> prefix in classnames</td><td>Class-name explosion in JSX</td></tr>
  <tr><td>JS-in-JS theming (styled-components, Emotion)</td><td>Dynamic; type-safe</td><td>Runtime cost; CSS-in-JS is declining 2026</td></tr>
  <tr><td>next-themes (Next.js)</td><td>Battle-tested; SSR-safe; handles flash</td><td>Next.js-only</td></tr>
  <tr><td>shadcn/ui + CSS vars</td><td>2026 default for shadcn-based apps</td><td>Tailwind-coupled</td></tr>
</table>

<p><strong>The flash-of-wrong-theme bug</strong>: without the inline script, the page renders with default theme briefly before React hydrates and applies the user&rsquo;s stored preference &mdash; jarring. The synchronous script in <code>&lt;head&gt;</code> sets <code>data-theme</code> before any CSS runs &mdash; first paint shows the right colors. Tailwind&rsquo;s <code>darkMode: ["class", '[data-theme="dark"]']</code> config integrates with this approach. <strong>For Next.js</strong>, use the <code>next-themes</code> library &mdash; it handles SSR + flash prevention automatically.</p>
'''

ANSWERS[60] = r'''
<p><strong>Situation:</strong> users need to upload files via drag-and-drop &mdash; drop a file onto a target area, see preview/progress, support multiple files, optionally upload images/documents only. Use cases: profile photos, document submission, attachment upload in a chat or email composer.</p>

<p><strong>Approach:</strong> use the HTML5 drag-and-drop API for the drop zone behavior; use <strong>react-dropzone</strong> for production (handles edge cases like nested drag events, accessibility, file type filtering). Pair with axios <code>onUploadProgress</code> or fetch with streams for progress reporting; show per-file status and allow cancellation.</p>

<pre><code>// Install: npm install react-dropzone axios

import { useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";

type UploadFile = {
  id: string;
  file: File;
  progress: number;
  status: "queued" | "uploading" | "done" | "error";
  url?: string;
  error?: string;
  controller?: AbortController;
};

function FileUploader({ onUploadComplete }: { onUploadComplete?: (urls: string[]) =&gt; void }) {
  const [files, setFiles] = useState&lt;UploadFile[]&gt;([]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    accept: {
      "image/*": [".jpg", ".jpeg", ".png", ".webp"],
      "application/pdf": [".pdf"]
    },
    maxSize: 10 * 1024 * 1024,    // 10 MB
    multiple: true,
    onDrop: (accepted, rejected) =&gt; {
      const newFiles: UploadFile[] = accepted.map(file =&gt; ({
        id: crypto.randomUUID(),
        file,
        progress: 0,
        status: "queued"
      }));
      setFiles(prev =&gt; [...prev, ...newFiles]);
      newFiles.forEach(uploadFile);

      rejected.forEach(({ file, errors }) =&gt; {
        toast.error(`${file.name}: ${errors[0].message}`);
      });
    }
  });

  const uploadFile = async (uf: UploadFile) =&gt; {
    const controller = new AbortController();

    setFiles(prev =&gt; prev.map(f =&gt;
      f.id === uf.id ? { ...f, status: "uploading", controller } : f
    ));

    const formData = new FormData();
    formData.append("file", uf.file);

    try {
      const { data } = await axios.post("/api/upload", formData, {
        signal: controller.signal,
        onUploadProgress: (e) =&gt; {
          if (e.total) {
            const progress = Math.round((e.loaded / e.total) * 100);
            setFiles(prev =&gt; prev.map(f =&gt;
              f.id === uf.id ? { ...f, progress } : f
            ));
          }
        }
      });

      setFiles(prev =&gt; prev.map(f =&gt;
        f.id === uf.id ? { ...f, status: "done", url: data.url, progress: 100 } : f
      ));
    } catch (err: any) {
      if (axios.isCancel(err)) return;
      setFiles(prev =&gt; prev.map(f =&gt;
        f.id === uf.id ? { ...f, status: "error", error: err.message } : f
      ));
    }
  };

  const cancelUpload = (id: string) =&gt; {
    const f = files.find(f =&gt; f.id === id);
    f?.controller?.abort();
    setFiles(prev =&gt; prev.filter(f =&gt; f.id !== id));
  };

  return (
    &lt;div&gt;
      &lt;div
        {...getRootProps()}
        style={{
          border: `2px dashed ${
            isDragReject ? "#dc2626" : isDragActive ? "#3b82f6" : "#d1d5db"
          }`,
          borderRadius: 8,
          padding: 32,
          textAlign: "center",
          background: isDragActive ? "#eff6ff" : "#fafafa",
          cursor: "pointer",
          transition: "all 150ms"
        }}
      &gt;
        &lt;input {...getInputProps()} /&gt;
        {isDragReject
          ? "Some files aren&rsquo;t allowed (wrong type or too big)"
          : isDragActive
            ? "Drop files here..."
            : "Drag &amp; drop files here, or click to browse"}
        &lt;p style={{ fontSize: 12, color: "#6b7280" }}&gt;
          Images and PDFs up to 10 MB
        &lt;/p&gt;
      &lt;/div&gt;

      &lt;ul style={{ listStyle: "none", padding: 0, marginTop: 16 }}&gt;
        {files.map(f =&gt; (
          &lt;li
            key={f.id}
            style={{ padding: 12, background: "#f9fafb", marginBottom: 4, borderRadius: 4 }}
          &gt;
            &lt;div style={{ display: "flex", justifyContent: "space-between" }}&gt;
              &lt;span&gt;{f.file.name}&lt;/span&gt;
              &lt;span&gt;
                {f.status === "uploading" &amp;&amp; `${f.progress}%`}
                {f.status === "done"     &amp;&amp; "✓"}
                {f.status === "error"    &amp;&amp; `✗ ${f.error}`}
                {f.status !== "done" &amp;&amp; (
                  &lt;button onClick={() =&gt; cancelUpload(f.id)} style={{ marginLeft: 8 }}&gt;
                    ✕
                  &lt;/button&gt;
                )}
              &lt;/span&gt;
            &lt;/div&gt;
            {f.status === "uploading" &amp;&amp; (
              &lt;div style={{ height: 4, background: "#e5e7eb", marginTop: 4 }}&gt;
                &lt;div style={{
                  width: `${f.progress}%`, height: "100%", background: "#3b82f6",
                  transition: "width 200ms"
                }} /&gt;
              &lt;/div&gt;
            )}
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Concern</th><th>Solution</th></tr>
  <tr><td>Large files (videos, datasets)</td><td>Chunked / resumable uploads &mdash; <strong>tus-js-client</strong>, S3 multipart, Uploadcare</td></tr>
  <tr><td>Direct-to-S3 uploads (skip server)</td><td>Pre-signed URLs from server; client uploads directly to S3</td></tr>
  <tr><td>Image processing (resize, optimize)</td><td>Cloudinary / Uploadcare / S3 + Lambda for transformation</td></tr>
  <tr><td>Concurrent upload limit</td><td>Queue with worker pool (e.g., 3 uploads in parallel)</td></tr>
  <tr><td>Resumable on connection loss</td><td>tus-js-client; chunked uploads with offset tracking</td></tr>
</table>

<p><strong>Production concerns</strong>: validate file type/size <em>both</em> client and server (client-side checks improve UX but aren&rsquo;t security); generate stable IDs with <code>crypto.randomUUID</code> (not <code>Date.now()</code> &mdash; collisions on rapid drops); show progress per-file; allow cancellation via <code>AbortController</code>; for sensitive content (medical, financial), encrypt at rest and validate MIME types server-side &mdash; client-reported types are spoofable. <strong>Server uploads scale badly</strong> &mdash; for any non-trivial file size, switch to direct-to-cloud uploads with pre-signed URLs.</p>
'''

ANSWERS[61] = r'''
<p><strong>Situation:</strong> a dashboard / admin app needs a sidebar that collapses to icons on small screens or to give users more content area. Common in CMS, admin panels, IDE-like apps, project management tools.</p>

<p><strong>Approach:</strong> two collapse modes &mdash; <strong>icon-only</strong> (desktop, more screen real estate) and <strong>fully hidden</strong> (mobile, full-screen content). Use CSS transitions for smooth motion; persist user preference to localStorage; auto-collapse on narrow viewports; preserve keyboard navigation and accessibility.</p>

<pre><code>import { useState, useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard",  icon: "📊" },
  { to: "/projects",  label: "Projects",   icon: "📁" },
  { to: "/tasks",     label: "Tasks",      icon: "✓"  },
  { to: "/team",      label: "Team",       icon: "👥" },
  { to: "/settings",  label: "Settings",   icon: "⚙"  }
];

function CollapsibleSidebar() {
  const [collapsed, setCollapsed] = useState&lt;boolean&gt;(() =&gt; {
    return localStorage.getItem("sidebar:collapsed") === "true";
  });
  const [mobileOpen, setMobileOpen] = useState(false);
  const isMobile = useMediaQuery("(max-width: 768px)");

  useEffect(() =&gt; {
    localStorage.setItem("sidebar:collapsed", String(collapsed));
  }, [collapsed]);

  // Close mobile sidebar when route changes
  const location = useLocation();
  useEffect(() =&gt; { setMobileOpen(false); }, [location.pathname]);

  // Close mobile on Escape
  useEffect(() =&gt; {
    if (!mobileOpen) return;
    const handler = (e: KeyboardEvent) =&gt; e.key === "Escape" &amp;&amp; setMobileOpen(false);
    document.addEventListener("keydown", handler);
    return () =&gt; document.removeEventListener("keydown", handler);
  }, [mobileOpen]);

  // On mobile, the sidebar is in/out; on desktop, full/icon-only
  const sidebarOpen = isMobile ? mobileOpen : true;
  const showLabels = isMobile ? mobileOpen : !collapsed;

  return (
    &lt;&gt;
      {/* Mobile toggle button — outside sidebar */}
      {isMobile &amp;&amp; (
        &lt;button
          onClick={() =&gt; setMobileOpen(o =&gt; !o)}
          aria-expanded={mobileOpen}
          aria-controls="sidebar"
          aria-label="Toggle navigation"
          style={{ position: "fixed", top: 12, left: 12, zIndex: 100 }}
        &gt;
          ☰
        &lt;/button&gt;
      )}

      {/* Mobile backdrop */}
      {isMobile &amp;&amp; mobileOpen &amp;&amp; (
        &lt;div
          onClick={() =&gt; setMobileOpen(false)}
          style={{
            position: "fixed", inset: 0,
            background: "rgba(0,0,0,0.4)", zIndex: 40
          }}
        /&gt;
      )}

      &lt;aside
        id="sidebar"
        aria-label="Main navigation"
        style={{
          position: isMobile ? "fixed" : "sticky",
          top: 0,
          left: 0,
          height: "100vh",
          zIndex: 50,
          width: showLabels ? 240 : 64,
          background: "#1e293b",
          color: "#f1f5f9",
          padding: 12,
          transition: "width 200ms, transform 200ms",
          transform: isMobile &amp;&amp; !mobileOpen ? "translateX(-100%)" : "translateX(0)",
          overflow: "hidden"
        }}
      &gt;
        &lt;div style={{ display: "flex", justifyContent: showLabels ? "space-between" : "center" }}&gt;
          {showLabels &amp;&amp; &lt;strong&gt;MyApp&lt;/strong&gt;}
          {!isMobile &amp;&amp; (
            &lt;button
              onClick={() =&gt; setCollapsed(c =&gt; !c)}
              aria-expanded={!collapsed}
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              style={{ background: "transparent", color: "inherit", border: "none" }}
            &gt;
              {collapsed ? "›" : "‹"}
            &lt;/button&gt;
          )}
        &lt;/div&gt;

        &lt;nav&gt;
          &lt;ul style={{ listStyle: "none", padding: 0 }}&gt;
            {NAV_ITEMS.map(item =&gt; (
              &lt;li key={item.to}&gt;
                &lt;NavLink
                  to={item.to}
                  title={!showLabels ? item.label : undefined}   // tooltip when collapsed
                  style={({ isActive }) =&gt; ({
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    padding: "10px 12px",
                    borderRadius: 6,
                    color: "inherit",
                    background: isActive ? "#334155" : "transparent",
                    textDecoration: "none",
                    whiteSpace: "nowrap"
                  })}
                &gt;
                  &lt;span style={{ fontSize: 20, flexShrink: 0 }}&gt;{item.icon}&lt;/span&gt;
                  {showLabels &amp;&amp; &lt;span&gt;{item.label}&lt;/span&gt;}
                &lt;/NavLink&gt;
              &lt;/li&gt;
            ))}
          &lt;/ul&gt;
        &lt;/nav&gt;
      &lt;/aside&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Choice</th><th>Reasoning</th></tr>
  <tr><td>Sidebar position</td><td>Sticky on desktop, fixed on mobile</td><td>Sticky scrolls with content area; fixed overlays main content on mobile</td></tr>
  <tr><td>Width transition</td><td>CSS <code>width</code> + <code>transition</code></td><td>Smoother than show/hide; icons remain visible</td></tr>
  <tr><td>Tooltip on collapsed icons</td><td>Native <code>title</code> attribute</td><td>Free; for richer tooltips, use Radix Tooltip</td></tr>
  <tr><td>Persist preference</td><td>localStorage</td><td>Survives reloads; per-device makes sense for layout</td></tr>
  <tr><td>Auto-close on navigate (mobile)</td><td>Watch <code>location.pathname</code></td><td>Standard mobile UX</td></tr>
</table>

<p><strong>Accessibility checklist</strong>: <code>aria-expanded</code> on toggle button; <code>aria-label</code> for sidebar landmark; <code>aria-controls</code> linking toggle to sidebar; ESC closes mobile sidebar; backdrop click closes; collapsed icons have <code>title</code> for screen-reader-friendly tooltips. <strong>For complex apps</strong>, use <strong>Radix UI&rsquo;s Sheet</strong> (mobile sidebar) or <strong>shadcn/ui Sheet</strong> &mdash; they handle focus trapping, return-focus, and animations.</p>
'''

ANSWERS[62] = r'''
<p><strong>Situation:</strong> an app uses a GraphQL backend; the React frontend needs to query data, handle subscriptions, manage cache, and stay in sync. Choices: <strong>Apollo Client</strong> (full-featured, normalized cache), <strong>urql</strong> (lighter), <strong>Relay</strong> (Meta-built, very powerful), or <strong>TanStack Query + graphql-request</strong> (simple, no normalization).</p>

<p><strong>Approach:</strong> for most teams in 2026, <strong>Apollo Client</strong> remains the production default &mdash; mature, well-documented, normalized cache with automatic UI updates. Use <code>graphql-codegen</code> to generate type-safe hooks from your schema. For lighter footprint or simpler needs, urql; for Meta-scale apps with intense caching needs, Relay.</p>

<pre><code>// Install: npm install @apollo/client graphql
// Type generation: npm install -D @graphql-codegen/cli @graphql-codegen/typescript-react-apollo

// === Setup ===
import { ApolloClient, InMemoryCache, ApolloProvider, HttpLink, from } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";

const httpLink = new HttpLink({ uri: "https://api.example.com/graphql" });

const authLink = setContext((_, { headers }) =&gt; {
  const token = getAuthToken();
  return { headers: { ...headers, authorization: token ? `Bearer ${token}` : "" } };
});

const errorLink = onError(({ graphQLErrors, networkError }) =&gt; {
  if (networkError) Sentry.captureException(networkError);
  graphQLErrors?.forEach(({ message, path }) =&gt; {
    console.error(`GraphQL error at ${path}: ${message}`);
  });
});

export const client = new ApolloClient({
  link: from([errorLink, authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          posts: {
            // Pagination merge function
            keyArgs: ["filter"],
            merge(existing = [], incoming) {
              return [...existing, ...incoming];
            }
          }
        }
      }
    }
  })
});

function Root() {
  return (
    &lt;ApolloProvider client={client}&gt;
      &lt;App /&gt;
    &lt;/ApolloProvider&gt;
  );
}

// === Type-safe queries with codegen ===
// Generated by graphql-codegen — fully typed
import { useGetPostsQuery, useCreatePostMutation } from "./generated/graphql";

function PostList() {
  const { data, loading, error, fetchMore } = useGetPostsQuery({
    variables: { limit: 10, offset: 0 }
  });

  const loadMore = () =&gt; {
    fetchMore({
      variables: { offset: data?.posts.length || 0 }
    });
  };

  if (loading &amp;&amp; !data) return &lt;Spinner /&gt;;
  if (error) return &lt;p&gt;Error: {error.message}&lt;/p&gt;;

  return (
    &lt;&gt;
      &lt;ul&gt;
        {data?.posts.map(post =&gt; (
          &lt;li key={post.id}&gt;
            &lt;strong&gt;{post.title}&lt;/strong&gt; by {post.author.name}
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
      &lt;button onClick={loadMore}&gt;Load more&lt;/button&gt;
    &lt;/&gt;
  );
}

// === Mutations with cache update ===
function CreatePost() {
  const [createPost, { loading }] = useCreatePostMutation({
    update(cache, { data }) {
      // Update cache so all consumers see new post immediately
      cache.modify({
        fields: {
          posts(existing = []) {
            return [data!.createPost, ...existing];
          }
        }
      });
    },
    optimisticResponse: (variables) =&gt; ({
      createPost: {
        __typename: "Post",
        id: `temp-${Date.now()}`,
        title: variables.title,
        author: { __typename: "User", id: currentUser.id, name: currentUser.name }
      }
    })
  });

  return (
    &lt;form onSubmit={(e) =&gt; {
      e.preventDefault();
      const title = (e.target as any).title.value;
      createPost({ variables: { title } });
    }}&gt;
      &lt;input name="title" /&gt;
      &lt;button disabled={loading}&gt;Create&lt;/button&gt;
    &lt;/form&gt;
  );
}

// === Subscriptions for real-time ===
import { useSubscription } from "@apollo/client";

function LiveCommentCount({ postId }) {
  const { data } = useSubscription(NEW_COMMENT_SUBSCRIPTION, { variables: { postId } });
  return &lt;span&gt;💬 {data?.commentCount ?? 0}&lt;/span&gt;;
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Library</th><th>Bundle</th><th>Cache</th><th>Best for</th></tr>
  <tr><td>Apollo Client</td><td>~33KB</td><td>Normalized</td><td>Production default; complex caching</td></tr>
  <tr><td>urql</td><td>~7KB</td><td>Document or normalized (opt-in)</td><td>Simpler apps; smaller bundle</td></tr>
  <tr><td>Relay</td><td>Larger</td><td>Normalized + fragments</td><td>Meta-scale; declarative data needs</td></tr>
  <tr><td>TanStack Query + graphql-request</td><td>~15KB</td><td>Per-query (not normalized)</td><td>Already use TanStack Query; simple needs</td></tr>
</table>

<p><strong>Critical patterns</strong>: <strong>graphql-codegen</strong> generates fully-typed hooks from your schema &mdash; catches schema/query mismatches at compile time. <strong>Normalized cache</strong> means updating one entity reflects everywhere it&rsquo;s used (no manual cache invalidation). <strong>Optimistic responses</strong> + cache <code>update</code> functions give instant UI updates with rollback on error. <strong>Persisted queries</strong> (Apollo, urql) reduce request size and protect against arbitrary query DoS. <strong>Don&rsquo;t over-fetch</strong> &mdash; one of GraphQL&rsquo;s benefits is you only get what you query for; specify exactly the fields each component needs.</p>
'''

ANSWERS[63] = r'''
<p><strong>Situation:</strong> a search input fires an API request on every keystroke &mdash; 10 characters typed = 10 requests, most of which become irrelevant before they return. Debouncing waits until the user stops typing for N ms, then fires one request &mdash; saves bandwidth, server load, and prevents flickering results.</p>

<p><strong>Approach:</strong> for typed search, two complementary techniques: <strong>debouncing</strong> (delay the trigger) and <strong>request cancellation</strong> (abort stale in-flight requests). With <strong>TanStack Query</strong>, debounce the query key; the library auto-cancels stale requests via signal integration. For roll-your-own, a <code>useDebouncedValue</code> hook + AbortController is enough.</p>

<pre><code>// === Custom debounce hook ===
import { useState, useEffect } from "react";

function useDebouncedValue&lt;T&gt;(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() =&gt; {
    const id = setTimeout(() =&gt; setDebounced(value), delay);
    return () =&gt; clearTimeout(id);   // cancel previous timer on every change
  }, [value, delay]);

  return debounced;
}

// === Usage with TanStack Query ===
import { useQuery, keepPreviousData } from "@tanstack/react-query";

function SearchPage() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 300);

  const { data, isFetching } = useQuery({
    queryKey: ["search", debouncedQuery],
    queryFn: async ({ signal }) =&gt; {
      // signal aborts the request if a newer one starts
      const res = await fetch(
        `/api/search?q=${encodeURIComponent(debouncedQuery)}`,
        { signal }
      );
      return res.json();
    },
    enabled: debouncedQuery.length &gt;= 2,
    placeholderData: keepPreviousData,        // smooth UX while new query loads
    staleTime: 30 * 1000
  });

  return (
    &lt;&gt;
      &lt;input
        value={query}
        onChange={(e) =&gt; setQuery(e.target.value)}
        placeholder="Search..."
        autoFocus
      /&gt;
      {isFetching &amp;&amp; &lt;span&gt;Searching...&lt;/span&gt;}
      &lt;ul&gt;
        {data?.results.map((r: any) =&gt; (
          &lt;li key={r.id}&gt;{r.title}&lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/&gt;
  );
}

// === Without TanStack Query (manual cancellation) ===
function ManualSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState&lt;any[]&gt;([]);
  const [loading, setLoading] = useState(false);
  const debouncedQuery = useDebouncedValue(query, 300);

  useEffect(() =&gt; {
    if (debouncedQuery.length &lt; 2) {
      setResults([]);
      return;
    }

    const controller = new AbortController();
    setLoading(true);

    fetch(`/api/search?q=${encodeURIComponent(debouncedQuery)}`, {
      signal: controller.signal
    })
      .then(r =&gt; r.json())
      .then(data =&gt; setResults(data.results))
      .catch(err =&gt; {
        if (err.name !== "AbortError") console.error(err);
      })
      .finally(() =&gt; setLoading(false));

    return () =&gt; controller.abort();   // cancel on next debouncedQuery change
  }, [debouncedQuery]);

  return (
    &lt;&gt;
      &lt;input value={query} onChange={(e) =&gt; setQuery(e.target.value)} /&gt;
      {loading &amp;&amp; &lt;Spinner /&gt;}
      &lt;ul&gt;{results.map(r =&gt; &lt;li key={r.id}&gt;{r.title}&lt;/li&gt;)}&lt;/ul&gt;
    &lt;/&gt;
  );
}

// === useDeferredValue alternative (React 18+) ===
// Best for client-side filtering of already-loaded data, NOT API calls
import { useDeferredValue, useMemo } from "react";

function ClientFilter({ items }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);

  const filtered = useMemo(() =&gt; {
    if (!deferredQuery) return items;
    return items.filter(i =&gt; i.name.toLowerCase().includes(deferredQuery.toLowerCase()));
  }, [items, deferredQuery]);

  return (
    &lt;&gt;
      &lt;input value={query} onChange={e =&gt; setQuery(e.target.value)} /&gt;
      &lt;ul&gt;{filtered.map(i =&gt; &lt;li key={i.id}&gt;{i.name}&lt;/li&gt;)}&lt;/ul&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Technique</th><th>Best for</th><th>Delay</th></tr>
  <tr><td>Debounce</td><td>Wait for typing pause; expensive ops</td><td>250-500ms typical</td></tr>
  <tr><td>Throttle</td><td>Steady rate; scroll/resize handlers</td><td>16-100ms typical</td></tr>
  <tr><td><code>useDeferredValue</code></td><td>Client-side filtering of already-loaded data</td><td>Browser-decided</td></tr>
  <tr><td>useTransition</td><td>Mark state update as low-priority</td><td>Browser-decided</td></tr>
  <tr><td>AbortController</td><td>Cancel stale fetch requests</td><td>Immediate</td></tr>
</table>

<p><strong>Pick the right delay</strong>: 200-300ms is the sweet spot for search &mdash; long enough to catch typing pauses, short enough to feel responsive. 100ms feels instant but fires too many requests; 600ms feels laggy. <strong>Library options</strong>: <code>use-debounce</code> (popular, well-tested), <code>lodash.debounce</code>, or roll your own as above. <strong>For typeahead/autocomplete</strong>, combine debouncing + <code>placeholderData: keepPreviousData</code> (TanStack Query) so old results stay visible while new ones load &mdash; eliminates flicker. <strong>useDeferredValue is NOT a debounce replacement for API calls</strong> &mdash; it&rsquo;s for purely client-side work; for API requests, debounce.</p>
'''

ANSWERS[64] = r'''
<p><strong>Situation:</strong> state updates that depend on the previous state can race when batched or queued. <code>setCount(count + 1)</code> called twice in the same event handler increments by 1, not 2 &mdash; both reads see the same stale <code>count</code>. The fix: use the <strong>updater function form</strong> of <code>setState</code> &mdash; it receives the current state and returns the new one.</p>

<p><strong>Approach:</strong> always use the updater function when next state depends on previous: <code>setCount(prev =&gt; prev + 1)</code>. React queues these and applies them in order, each operating on the result of the previous &mdash; no stale reads. This matters in event handlers, async callbacks, intervals, and any code that runs across multiple renders.</p>

<pre><code>import { useState, useEffect } from "react";

// === The bug: stale closure ===
function BuggyCounter() {
  const [count, setCount] = useState(0);

  const handleClick = () =&gt; {
    // Both reads see the SAME stale count
    setCount(count + 1);
    setCount(count + 1);
    setCount(count + 1);
    // Only increments by 1, not 3!
  };

  return &lt;button onClick={handleClick}&gt;{count}&lt;/button&gt;;
}

// === The fix: updater function ===
function CorrectCounter() {
  const [count, setCount] = useState(0);

  const handleClick = () =&gt; {
    setCount(prev =&gt; prev + 1);
    setCount(prev =&gt; prev + 1);
    setCount(prev =&gt; prev + 1);
    // Increments by 3 — each updater receives the previous result
  };

  return &lt;button onClick={handleClick}&gt;{count}&lt;/button&gt;;
}

// === Common bug: stale state in setInterval ===
function BuggyTimer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() =&gt; {
    const id = setInterval(() =&gt; {
      // Closure captures `seconds` from when interval was created — always 0
      setSeconds(seconds + 1);
    }, 1000);
    return () =&gt; clearInterval(id);
  }, []);   // empty deps means stale closure

  return &lt;p&gt;{seconds}&lt;/p&gt;;   // stays at 1 forever
}

// === Fix with updater function ===
function CorrectTimer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() =&gt; {
    const id = setInterval(() =&gt; {
      setSeconds(prev =&gt; prev + 1);   // always operates on latest state
    }, 1000);
    return () =&gt; clearInterval(id);
  }, []);

  return &lt;p&gt;{seconds}&lt;/p&gt;;   // increments correctly
}

// === Updates to objects/arrays — same principle ===
function TodoList() {
  const [todos, setTodos] = useState&lt;Todo[]&gt;([]);

  const addTodo = (text: string) =&gt; {
    setTodos(prev =&gt; [...prev, { id: Date.now(), text, done: false }]);
  };

  const toggle = (id: number) =&gt; {
    setTodos(prev =&gt; prev.map(t =&gt;
      t.id === id ? { ...t, done: !t.done } : t
    ));
  };

  const remove = (id: number) =&gt; {
    setTodos(prev =&gt; prev.filter(t =&gt; t.id !== id));
  };

  return (/* ... */);
}

// === useReducer: built-in &ldquo;previous state&rdquo; ===
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "INCREMENT":
      return { ...state, count: state.count + 1 };  // always operates on current state
    case "ADD_TODO":
      return { ...state, todos: [...state.todos, action.todo] };
    default:
      return state;
  }
}

const [state, dispatch] = useReducer(reducer, initialState);
// Multiple dispatches batch correctly — no stale state issue</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pattern</th><th>When to use</th><th>Stale-state risk</th></tr>
  <tr><td><code>setState(value)</code></td><td>New value doesn&rsquo;t depend on previous</td><td>Safe</td></tr>
  <tr><td><code>setState(prev =&gt; ...)</code></td><td>Next state depends on previous</td><td>Always safe</td></tr>
  <tr><td><code>useReducer</code></td><td>Multiple related updates; complex transitions</td><td>Safe by design</td></tr>
  <tr><td>Refs (<code>useRef</code>)</td><td>Mutable values that don&rsquo;t trigger renders</td><td>N/A &mdash; no batching</td></tr>
</table>

<p><strong>Why this matters more in React 18+</strong>: automatic batching &mdash; React batches state updates across promises, timeouts, and native event handlers (not just synthetic events). More batching means more cases where multiple updates happen before a re-render &mdash; and more chances for stale-state bugs.</p>

<p><strong>The exhaustive-deps lint rule</strong>: ESLint&rsquo;s <code>react-hooks/exhaustive-deps</code> warns about missing dependencies in effects/callbacks &mdash; including state values used inside. The fix is often to use the updater form (which lets you remove the state from deps) or include it (which causes effect to re-run on every change). <strong>Don&rsquo;t silence the warning</strong> &mdash; missing deps are real bugs.</p>

<p><strong>For functional updates with multiple state pieces</strong>: if multiple states update together, use <code>useReducer</code> &mdash; one dispatch, atomic transition, no chance of inconsistency between pieces.</p>
'''

ANSWERS[65] = r'''
<p><strong>Situation:</strong> a tooltip needs to appear when users hover or focus on an element &mdash; explanation of an icon button, abbreviation expansion, help text. Must handle keyboard users (focus, not just hover), avoid clipping at viewport edges, and announce content to screen readers.</p>

<p><strong>Approach:</strong> for production, use <strong>Radix UI Tooltip</strong> or <strong>shadcn/ui Tooltip</strong> (Radix-based). They handle all the edge cases &mdash; positioning, collision detection, focus management, ARIA roles, escape key, hover delay. For learning purposes, build a basic version with <strong>Floating UI</strong> for positioning.</p>

<pre><code>// === Production: Radix UI ===
// Install: npm install @radix-ui/react-tooltip

import * as Tooltip from "@radix-ui/react-tooltip";

function App() {
  return (
    &lt;Tooltip.Provider delayDuration={300}&gt;
      &lt;Tooltip.Root&gt;
        &lt;Tooltip.Trigger asChild&gt;
          &lt;button aria-label="Save"&gt;💾&lt;/button&gt;
        &lt;/Tooltip.Trigger&gt;
        &lt;Tooltip.Portal&gt;
          &lt;Tooltip.Content
            side="top"
            sideOffset={6}
            className="tooltip-content"
          &gt;
            Save your work (⌘S)
            &lt;Tooltip.Arrow className="tooltip-arrow" /&gt;
          &lt;/Tooltip.Content&gt;
        &lt;/Tooltip.Portal&gt;
      &lt;/Tooltip.Root&gt;
    &lt;/Tooltip.Provider&gt;
  );
}

// === Roll-your-own with Floating UI for positioning ===
// Install: npm install @floating-ui/react

import { useState, useId } from "react";
import {
  useFloating, useHover, useFocus, useDismiss, useRole,
  useInteractions, autoUpdate, offset, flip, shift, FloatingPortal
} from "@floating-ui/react";

function CustomTooltip({ children, label }: { children: React.ReactElement; label: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();

  const { refs, floatingStyles, context } = useFloating({
    open,
    onOpenChange: setOpen,
    placement: "top",
    middleware: [
      offset(6),
      flip(),                        // flips to bottom if no room above
      shift({ padding: 8 })          // shifts to stay in viewport
    ],
    whileElementsMounted: autoUpdate
  });

  const hover = useHover(context, { delay: { open: 300, close: 0 } });
  const focus = useFocus(context);
  const dismiss = useDismiss(context);
  const role = useRole(context, { role: "tooltip" });

  const { getReferenceProps, getFloatingProps } = useInteractions([
    hover, focus, dismiss, role
  ]);

  return (
    &lt;&gt;
      {/* Spread referenceRef and props onto trigger */}
      {React.cloneElement(children, {
        ref: refs.setReference,
        "aria-describedby": open ? id : undefined,
        ...getReferenceProps()
      })}

      {open &amp;&amp; (
        &lt;FloatingPortal&gt;
          &lt;div
            ref={refs.setFloating}
            style={{
              ...floatingStyles,
              background: "#1f2937",
              color: "white",
              padding: "6px 10px",
              borderRadius: 4,
              fontSize: 13,
              maxWidth: 240,
              zIndex: 1000
            }}
            id={id}
            {...getFloatingProps()}
          &gt;
            {label}
          &lt;/div&gt;
        &lt;/FloatingPortal&gt;
      )}
    &lt;/&gt;
  );
}

// Usage
&lt;CustomTooltip label="Click to save your changes"&gt;
  &lt;button&gt;💾&lt;/button&gt;
&lt;/CustomTooltip&gt;

// === Naive version (educational only — has edge cases) ===
function NaiveTooltip({ children, text }) {
  const [show, setShow] = useState(false);
  return (
    &lt;span style={{ position: "relative" }}
          onMouseEnter={() =&gt; setShow(true)}
          onMouseLeave={() =&gt; setShow(false)}
          onFocus={() =&gt; setShow(true)}
          onBlur={() =&gt; setShow(false)}&gt;
      {children}
      {show &amp;&amp; (
        &lt;span role="tooltip" style={{
          position: "absolute", bottom: "100%",
          left: "50%", transform: "translateX(-50%)",
          background: "#333", color: "white", padding: "4px 8px",
          borderRadius: 4, whiteSpace: "nowrap", pointerEvents: "none"
        }}&gt;
          {text}
        &lt;/span&gt;
      )}
    &lt;/span&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Use when</th></tr>
  <tr><td>Radix Tooltip / shadcn/ui</td><td>Production default; handles all edge cases automatically</td></tr>
  <tr><td>Floating UI custom</td><td>Need custom interaction (e.g., click to open, multi-trigger)</td></tr>
  <tr><td>Native <code>title</code> attribute</td><td>Quick & free; but slow, ugly, inconsistent across browsers</td></tr>
  <tr><td>Roll-your-own positioning</td><td>Don&rsquo;t &mdash; positioning is genuinely hard</td></tr>
</table>

<p><strong>Edge cases proper libraries handle</strong>:</p>
<ul>
  <li><strong>Viewport collision</strong> &mdash; auto-flip from top to bottom when there&rsquo;s no room above.</li>
  <li><strong>Scroll repositioning</strong> &mdash; tooltip moves with target as page scrolls.</li>
  <li><strong>Hover delay</strong> &mdash; opens after 300-700ms (avoids accidental triggers); closes immediately.</li>
  <li><strong>Touch devices</strong> &mdash; tap-and-hold or long-press; doesn&rsquo;t interfere with click events.</li>
  <li><strong>Keyboard accessibility</strong> &mdash; focus shows tooltip; Escape dismisses; <code>aria-describedby</code> announced.</li>
  <li><strong>Focus trap awareness</strong> &mdash; doesn&rsquo;t steal focus from modals.</li>
  <li><strong>z-index stacking</strong> &mdash; portals to <code>body</code> to escape overflow/transform contexts.</li>
</ul>

<p><strong>Don&rsquo;t use tooltips for critical info</strong>: tooltips are progressive disclosure for "nice to have" info. Anything users <em>need</em> should be visible (label below an icon, helper text in a form). Tooltips also fail on touch devices &mdash; phones don&rsquo;t have hover. Pair tooltips with visible labels in mobile breakpoints.</p>
'''

ANSWERS[66] = r'''
<p><strong>Situation:</strong> a form needs dynamically added/removed fields &mdash; users can add multiple emails, phone numbers, work experiences, family members, ingredients in a recipe. Each &ldquo;row&rdquo; has its own validation; the array length is user-controlled.</p>

<p><strong>Approach:</strong> for simple cases, manage as an array in <code>useState</code> with stable IDs (<code>crypto.randomUUID()</code>, never indexes). For production, use <strong>React Hook Form&rsquo;s <code>useFieldArray</code></strong> &mdash; it handles add/remove, key management, and per-field validation natively.</p>

<pre><code>// === React Hook Form approach (recommended for production) ===
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const phoneSchema = z.object({
  type: z.enum(["mobile", "home", "work"], { errorMap: () =&gt; ({ message: "Required" }) }),
  number: z.string().regex(/^[0-9-+\s()]+$/, "Invalid phone format")
});

const formSchema = z.object({
  name: z.string().min(1, "Name required"),
  phones: z.array(phoneSchema).min(1, "At least one phone number")
});

type FormValues = z.infer&lt;typeof formSchema&gt;;

function ContactForm() {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors }
  } = useForm&lt;FormValues&gt;({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      phones: [{ type: "mobile", number: "" }]
    }
  });

  const { fields, append, remove, move } = useFieldArray({
    control,
    name: "phones"
  });

  return (
    &lt;form onSubmit={handleSubmit(data =&gt; console.log(data))}&gt;
      &lt;label&gt;
        Name:
        &lt;input {...register("name")} /&gt;
        {errors.name &amp;&amp; &lt;span className="err"&gt;{errors.name.message}&lt;/span&gt;}
      &lt;/label&gt;

      &lt;h3&gt;Phone numbers&lt;/h3&gt;
      {fields.map((field, index) =&gt; (
        &lt;div
          key={field.id}     // RHF provides stable IDs — never use index
          style={{ display: "flex", gap: 8, marginBottom: 8 }}
        &gt;
          &lt;select {...register(`phones.${index}.type`)}&gt;
            &lt;option value="mobile"&gt;Mobile&lt;/option&gt;
            &lt;option value="home"&gt;Home&lt;/option&gt;
            &lt;option value="work"&gt;Work&lt;/option&gt;
          &lt;/select&gt;

          &lt;input
            {...register(`phones.${index}.number`)}
            placeholder="555-123-4567"
            aria-invalid={!!errors.phones?.[index]?.number}
          /&gt;

          {errors.phones?.[index]?.number &amp;&amp; (
            &lt;span className="err"&gt;{errors.phones[index]!.number!.message}&lt;/span&gt;
          )}

          &lt;button
            type="button"
            onClick={() =&gt; remove(index)}
            disabled={fields.length === 1}
            aria-label={`Remove phone ${index + 1}`}
          &gt;
            ✕
          &lt;/button&gt;

          {index &gt; 0 &amp;&amp; (
            &lt;button
              type="button"
              onClick={() =&gt; move(index, index - 1)}
              aria-label="Move up"
            &gt;
              ↑
            &lt;/button&gt;
          )}
        &lt;/div&gt;
      ))}

      &lt;button
        type="button"
        onClick={() =&gt; append({ type: "mobile", number: "" })}
      &gt;
        + Add phone
      &lt;/button&gt;

      &lt;button type="submit"&gt;Save&lt;/button&gt;
    &lt;/form&gt;
  );
}

// === Manual approach (no library, for understanding) ===
import { useState } from "react";

function ManualDynamicForm() {
  const [phones, setPhones] = useState([
    { id: crypto.randomUUID(), type: "mobile", number: "" }
  ]);

  const addPhone = () =&gt; {
    setPhones(prev =&gt; [...prev, {
      id: crypto.randomUUID(),
      type: "mobile",
      number: ""
    }]);
  };

  const removePhone = (id: string) =&gt; {
    setPhones(prev =&gt; prev.filter(p =&gt; p.id !== id));
  };

  const updatePhone = (id: string, field: string, value: string) =&gt; {
    setPhones(prev =&gt; prev.map(p =&gt; p.id === id ? { ...p, [field]: value } : p));
  };

  return (
    &lt;form&gt;
      {phones.map(phone =&gt; (
        &lt;div key={phone.id}&gt;
          &lt;select
            value={phone.type}
            onChange={e =&gt; updatePhone(phone.id, "type", e.target.value)}
          &gt;
            &lt;option value="mobile"&gt;Mobile&lt;/option&gt;
            &lt;option value="home"&gt;Home&lt;/option&gt;
            &lt;option value="work"&gt;Work&lt;/option&gt;
          &lt;/select&gt;
          &lt;input
            value={phone.number}
            onChange={e =&gt; updatePhone(phone.id, "number", e.target.value)}
          /&gt;
          &lt;button type="button" onClick={() =&gt; removePhone(phone.id)}&gt;✕&lt;/button&gt;
        &lt;/div&gt;
      ))}
      &lt;button type="button" onClick={addPhone}&gt;+ Add phone&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>RHF <code>useFieldArray</code></td><td>Stable IDs, validation per row, move/swap helpers</td><td>Library dependency</td></tr>
  <tr><td>useState array</td><td>No deps; simple to understand</td><td>Manual key management; manual validation</td></tr>
  <tr><td>useReducer with array actions</td><td>Centralized logic; testable</td><td>More code</td></tr>
</table>

<p><strong>Critical: never use array index as key</strong>. If user removes the second item, React reuses the third item&rsquo;s state for what is now the second position &mdash; classic data corruption bug. Use <code>crypto.randomUUID()</code> or RHF&rsquo;s built-in IDs. <strong>Validation per row</strong> &mdash; RHF + Zod arrays validate each item independently with per-field error mapping. <strong>Min/max enforcement</strong> &mdash; disable the remove button when at minimum, hide add button at maximum (or show a message). <strong>Reordering</strong> &mdash; RHF&rsquo;s <code>move(from, to)</code> lets users drag-and-drop rows; combine with dnd-kit for the drag UI.</p>
'''

ANSWERS[67] = r'''
<p><strong>Situation:</strong> a logout button needs to clear the user&rsquo;s session, invalidate cached data, sync the logout across browser tabs, and redirect to the login page or home. Half-implemented logout creates security issues (cached data still showing) and bad UX (logged out in one tab, still &ldquo;logged in&rdquo; in another).</p>

<p><strong>Approach:</strong> a complete logout flow: call the server logout endpoint (invalidates session/refresh token); clear local auth state and cookies; wipe TanStack Query cache; broadcast logout to other tabs via BroadcastChannel; redirect with <code>replace: true</code> so back button doesn&rsquo;t return to authenticated pages.</p>

<pre><code>import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";

// === Auth context with complete logout ===
const channel = new BroadcastChannel("auth");

export function AuthProvider({ children }) {
  const [user, setUser] = useState&lt;User | null&gt;(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Listen for logout from other tabs
  useEffect(() =&gt; {
    const handler = (e: MessageEvent) =&gt; {
      if (e.data.type === "LOGGED_OUT") {
        setUser(null);
        queryClient.clear();
        // Don't navigate here — let the auth guard redirect naturally
      }
    };
    channel.addEventListener("message", handler);
    return () =&gt; channel.removeEventListener("message", handler);
  }, [queryClient]);

  const logout = useCallback(async (reason?: "user" | "expired" | "forced") =&gt; {
    try {
      // 1. Invalidate server-side session
      await fetch("/api/logout", {
        method: "POST",
        credentials: "include"
      });
    } catch {
      // Even if server call fails, proceed with local cleanup
    }

    // 2. Clear local state
    setUser(null);

    // 3. Wipe cached data so previous user&rsquo;s data isn&rsquo;t exposed
    queryClient.clear();

    // 4. Clear app-specific storage
    localStorage.removeItem("preferences");
    sessionStorage.clear();

    // 5. Notify other tabs
    channel.postMessage({ type: "LOGGED_OUT" });

    // 6. Redirect with appropriate message
    const params = reason === "expired" ? "?expired=1" : "";
    navigate(`/login${params}`, { replace: true });
  }, [navigate, queryClient]);

  // ... login, refresh, etc.

  return (
    &lt;AuthContext.Provider value={{ user, logout, /* ... */ }}&gt;
      {children}
    &lt;/AuthContext.Provider&gt;
  );
}

// === Logout button component ===
function LogoutButton() {
  const { logout } = useAuth();
  const [confirming, setConfirming] = useState(false);

  if (confirming) {
    return (
      &lt;div&gt;
        Are you sure?
        &lt;button onClick={() =&gt; logout("user")}&gt;Yes, log out&lt;/button&gt;
        &lt;button onClick={() =&gt; setConfirming(false)}&gt;Cancel&lt;/button&gt;
      &lt;/div&gt;
    );
  }

  return (
    &lt;button onClick={() =&gt; setConfirming(true)}&gt;
      Sign out
    &lt;/button&gt;
  );
}

// === Auto-logout on token expiry ===
function ApiInterceptor() {
  const { logout } = useAuth();

  // Custom fetch wrapper or axios interceptor calls logout("expired") on 401
  // (see global error handling pattern)

  return null;
}

// === Login page handles return parameters ===
function LoginPage() {
  const [searchParams] = useSearchParams();
  const expired = searchParams.get("expired") === "1";

  return (
    &lt;&gt;
      {expired &amp;&amp; (
        &lt;div role="alert" className="info-banner"&gt;
          Your session expired. Please sign in again.
        &lt;/div&gt;
      )}
      &lt;LoginForm /&gt;
    &lt;/&gt;
  );
}

// === Inactivity-based auto-logout ===
function useInactivityLogout(timeoutMinutes = 30) {
  const { logout } = useAuth();

  useEffect(() =&gt; {
    let timer: ReturnType&lt;typeof setTimeout&gt;;

    const reset = () =&gt; {
      clearTimeout(timer);
      timer = setTimeout(() =&gt; logout("expired"), timeoutMinutes * 60 * 1000);
    };

    const events = ["mousedown", "keydown", "touchstart", "scroll"];
    events.forEach(e =&gt; window.addEventListener(e, reset, { passive: true }));
    reset();

    return () =&gt; {
      clearTimeout(timer);
      events.forEach(e =&gt; window.removeEventListener(e, reset));
    };
  }, [logout, timeoutMinutes]);
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Logout trigger</th><th>Reason</th><th>UX</th></tr>
  <tr><td>User clicks &ldquo;Sign out&rdquo;</td><td>Explicit</td><td>Optionally confirm to prevent misclicks</td></tr>
  <tr><td>Token expired</td><td>Auto via API interceptor</td><td>Banner: &ldquo;Your session expired&rdquo;; preserve return URL</td></tr>
  <tr><td>Inactivity timeout</td><td>Sensitive apps (banking, healthcare)</td><td>Optional warning at 5 min; logout at 30 min</td></tr>
  <tr><td>Logout in another tab</td><td>Cross-tab sync</td><td>Background sync; redirect on next route change</td></tr>
  <tr><td>Forced (admin revokes session)</td><td>Server-pushed via WebSocket / next API call</td><td>Banner: &ldquo;You&rsquo;ve been signed out&rdquo;</td></tr>
</table>

<p><strong>Critical security details</strong>: <strong>always wipe cached data</strong> &mdash; <code>queryClient.clear()</code> prevents next user (or back-navigation) from seeing previous user&rsquo;s data. <strong>Server-side invalidation</strong> &mdash; client-only logout still leaves the token valid; the server must add it to a revocation list (or rotate refresh tokens). <strong>HttpOnly cookies</strong> are cleared by the server&rsquo;s logout response setting an expired cookie. <strong>Don&rsquo;t use <code>window.location.href</code></strong> for the redirect &mdash; use React Router&rsquo;s <code>navigate</code> for SPA behavior; <code>replace: true</code> prevents back-button reaching authenticated pages.</p>

<p><strong>Production additions</strong>: log logout events for security auditing; rate-limit logout endpoint to prevent abuse; for highly sensitive apps, consider re-authentication for sensitive actions (privilege escalation) rather than just session length.</p>
'''

ANSWERS[68] = r'''
<p><strong>Situation:</strong> need a slider control for selecting a numeric value or range &mdash; volume, price filter, image opacity, brightness, year picker. The native <code>&lt;input type="range"&gt;</code> works but has limitations: no two-thumb range selection, awkward styling across browsers, no rich tooltips during drag.</p>

<p><strong>Approach:</strong> for single-value sliders, native <code>&lt;input type="range"&gt;</code> with custom CSS is fine. For range sliders (two thumbs), or rich features (markers, tooltips, custom rendering), use <strong>Radix UI Slider</strong> or <strong>shadcn/ui Slider</strong> &mdash; accessible, keyboard-friendly, fully stylable.</p>

<pre><code>// === Native slider with controlled value ===
function VolumeSlider() {
  const [volume, setVolume] = useState(50);

  return (
    &lt;div&gt;
      &lt;label htmlFor="volume"&gt;
        Volume: {volume}%
      &lt;/label&gt;
      &lt;input
        id="volume"
        type="range"
        min={0}
        max={100}
        step={1}
        value={volume}
        onChange={(e) =&gt; setVolume(Number(e.target.value))}
      /&gt;
    &lt;/div&gt;
  );
}

// === Radix UI: range slider with two thumbs ===
import * as Slider from "@radix-ui/react-slider";

function PriceRangeSlider() {
  const [range, setRange] = useState([100, 500]);

  return (
    &lt;div&gt;
      &lt;label&gt;Price: ${range[0]} – ${range[1]}&lt;/label&gt;

      &lt;Slider.Root
        value={range}
        onValueChange={setRange}
        min={0}
        max={1000}
        step={10}
        minStepsBetweenThumbs={1}
        style={{
          position: "relative",
          width: 280,
          height: 20,
          display: "flex",
          alignItems: "center"
        }}
      &gt;
        &lt;Slider.Track style={{
          background: "#e5e7eb",
          height: 4, borderRadius: 999, flex: 1
        }}&gt;
          &lt;Slider.Range style={{
            background: "#3b82f6",
            height: "100%", borderRadius: 999, position: "absolute"
          }} /&gt;
        &lt;/Slider.Track&gt;

        &lt;Slider.Thumb
          aria-label="Min price"
          style={{
            display: "block", width: 16, height: 16,
            background: "white",
            border: "2px solid #3b82f6",
            borderRadius: "50%",
            cursor: "pointer"
          }}
        /&gt;
        &lt;Slider.Thumb
          aria-label="Max price"
          style={{
            display: "block", width: 16, height: 16,
            background: "white",
            border: "2px solid #3b82f6",
            borderRadius: "50%",
            cursor: "pointer"
          }}
        /&gt;
      &lt;/Slider.Root&gt;
    &lt;/div&gt;
  );
}

// === Slider with marks and value tooltip ===
function MarkedSlider() {
  const [value, setValue] = useState(50);
  const marks = [0, 25, 50, 75, 100];

  return (
    &lt;div style={{ width: 320, padding: 16 }}&gt;
      &lt;Slider.Root
        value={[value]}
        onValueChange={(v) =&gt; setValue(v[0])}
        min={0}
        max={100}
        step={5}
        style={{ position: "relative", display: "flex", alignItems: "center", height: 32 }}
      &gt;
        &lt;Slider.Track style={{ background: "#e5e7eb", height: 4, flex: 1, borderRadius: 999 }}&gt;
          &lt;Slider.Range style={{
            background: "#3b82f6", height: "100%", borderRadius: 999, position: "absolute"
          }} /&gt;
        &lt;/Slider.Track&gt;

        &lt;Slider.Thumb style={{
          width: 18, height: 18, background: "white",
          border: "2px solid #3b82f6", borderRadius: "50%", position: "relative"
        }}&gt;
          {/* Value tooltip on the thumb */}
          &lt;span style={{
            position: "absolute", top: -28, left: "50%", transform: "translateX(-50%)",
            background: "#1f2937", color: "white", padding: "2px 6px",
            borderRadius: 4, fontSize: 12, whiteSpace: "nowrap"
          }}&gt;
            {value}
          &lt;/span&gt;
        &lt;/Slider.Thumb&gt;
      &lt;/Slider.Root&gt;

      {/* Mark labels */}
      &lt;div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}&gt;
        {marks.map(m =&gt; (
          &lt;button
            key={m}
            onClick={() =&gt; setValue(m)}
            style={{ background: "transparent", border: "none", cursor: "pointer" }}
          &gt;
            {m}
          &lt;/button&gt;
        ))}
      &lt;/div&gt;
    &lt;/div&gt;
  );
}

// === Combine with debounce for filtering ===
function PriceFilter() {
  const [range, setRange] = useState([0, 1000]);
  const debouncedRange = useDebouncedValue(range, 300);

  // Only fires API call after user stops dragging
  const { data } = useQuery({
    queryKey: ["products", debouncedRange],
    queryFn: () =&gt; fetch(
      `/api/products?minPrice=${debouncedRange[0]}&amp;maxPrice=${debouncedRange[1]}`
    ).then(r =&gt; r.json())
  });

  return (
    &lt;&gt;
      &lt;PriceRangeSlider value={range} onChange={setRange} /&gt;
      &lt;ProductList products={data} /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Best for</th><th>Limitations</th></tr>
  <tr><td>Native <code>&lt;input type="range"&gt;</code></td><td>Simple, single-value, basic styling</td><td>No range; ugly default; cross-browser styling pain</td></tr>
  <tr><td>Radix UI Slider</td><td>Production default; range; full a11y</td><td>Add dependency; styling required</td></tr>
  <tr><td>shadcn/ui Slider</td><td>Tailwind apps; pre-styled</td><td>Tailwind-coupled</td></tr>
  <tr><td>react-slider / rc-slider</td><td>Mature; lots of features</td><td>Larger bundles</td></tr>
</table>

<p><strong>Accessibility checklist</strong>: each thumb has an <code>aria-label</code>; arrow keys move ±step; Page Up/Down move by larger increments; Home/End jump to min/max; current value announced via <code>aria-valuenow</code>. Radix handles all of this. <strong>Performance</strong> &mdash; for sliders that filter large data, debounce the change event (300ms typical) so the filter doesn&rsquo;t fire on every pixel of dragging. <strong>Touch devices</strong> &mdash; the default thumb size (16-18px) is too small; consider 24-28px for mobile breakpoints. Radix and shadcn/ui handle pointer events that work for both mouse and touch.</p>
'''

ANSWERS[69] = r'''
<p><strong>Situation:</strong> an app needs to display a map &mdash; show a location, plot multiple markers, draw routes, allow user interaction. Use cases: contact page (&ldquo;our office&rdquo;), real estate listings, ride-hailing, delivery tracking, store finder. The Google Maps JavaScript API is the industry default; alternatives include Mapbox, Leaflet, and OpenStreetMap.</p>

<p><strong>Approach:</strong> use <strong><code>@vis.gl/react-google-maps</code></strong> &mdash; the official React wrapper from Google&rsquo;s visualization team (replaces the older <code>@react-google-maps/api</code>). Provides typed hooks, declarative components, and automatic map lifecycle management.</p>

<pre><code>// Install: npm install @vis.gl/react-google-maps

import { APIProvider, Map, Marker, InfoWindow, useMap } from "@vis.gl/react-google-maps";
import { useState, useEffect } from "react";

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY;

// === Basic map ===
function StoreLocator() {
  const stores = [
    { id: 1, name: "Downtown",  position: { lat: 40.7128, lng: -74.0060 } },
    { id: 2, name: "Uptown",    position: { lat: 40.7831, lng: -73.9712 } },
    { id: 3, name: "Brooklyn",  position: { lat: 40.6782, lng: -73.9442 } }
  ];

  const [selectedId, setSelectedId] = useState&lt;number | null&gt;(null);
  const selectedStore = stores.find(s =&gt; s.id === selectedId);

  return (
    &lt;APIProvider apiKey={API_KEY} libraries={["places"]}&gt;
      &lt;div style={{ height: 500, width: "100%" }}&gt;
        &lt;Map
          defaultCenter={{ lat: 40.7128, lng: -74.0060 }}
          defaultZoom={11}
          mapId="YOUR_MAP_ID"          // for cloud-styled maps
          gestureHandling="greedy"     // single-finger pan on mobile
          disableDefaultUI={false}
        &gt;
          {stores.map(store =&gt; (
            &lt;Marker
              key={store.id}
              position={store.position}
              onClick={() =&gt; setSelectedId(store.id)}
              title={store.name}
            /&gt;
          ))}

          {selectedStore &amp;&amp; (
            &lt;InfoWindow
              position={selectedStore.position}
              onCloseClick={() =&gt; setSelectedId(null)}
            &gt;
              &lt;div&gt;
                &lt;strong&gt;{selectedStore.name}&lt;/strong&gt;
                &lt;p&gt;Click for details&lt;/p&gt;
              &lt;/div&gt;
            &lt;/InfoWindow&gt;
          )}
        &lt;/Map&gt;
      &lt;/div&gt;
    &lt;/APIProvider&gt;
  );
}

// === User&rsquo;s current location ===
function NearbyStores() {
  const [userLocation, setUserLocation] = useState&lt;
    { lat: number; lng: number } | null
  &gt;(null);

  useEffect(() =&gt; {
    if (!("geolocation" in navigator)) return;

    navigator.geolocation.getCurrentPosition(
      (pos) =&gt; setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      (err) =&gt; console.error("Geolocation:", err.message),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, []);

  if (!userLocation) return &lt;p&gt;Getting your location...&lt;/p&gt;;

  return (
    &lt;APIProvider apiKey={API_KEY}&gt;
      &lt;Map
        defaultCenter={userLocation}
        defaultZoom={14}
        style={{ height: 400, width: "100%" }}
      &gt;
        &lt;Marker position={userLocation} /&gt;
      &lt;/Map&gt;
    &lt;/APIProvider&gt;
  );
}

// === Programmatic map control ===
function MapWithControls() {
  function FlyToButton({ position }: { position: any }) {
    const map = useMap();
    return (
      &lt;button onClick={() =&gt; map?.panTo(position)}&gt;
        Center on store
      &lt;/button&gt;
    );
  }

  return (
    &lt;APIProvider apiKey={API_KEY}&gt;
      &lt;Map defaultCenter={{ lat: 0, lng: 0 }} defaultZoom={2} style={{ height: 400 }}&gt;
        &lt;Marker position={{ lat: 35.6762, lng: 139.6503 }} /&gt;
      &lt;/Map&gt;
      &lt;FlyToButton position={{ lat: 35.6762, lng: 139.6503 }} /&gt;
    &lt;/APIProvider&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Library</th><th>Pricing</th><th>Best for</th></tr>
  <tr><td>Google Maps</td><td>$200/mo free credit; pay per use</td><td>Familiar UX; rich data (places, routes, traffic)</td></tr>
  <tr><td>Mapbox</td><td>50K loads/mo free</td><td>Beautiful custom styling; vector tiles</td></tr>
  <tr><td>Leaflet + OpenStreetMap</td><td>Free</td><td>Simple use cases; no API key; lightweight</td></tr>
  <tr><td>MapLibre GL JS</td><td>Free (Mapbox fork)</td><td>Open-source alternative to Mapbox</td></tr>
</table>

<p><strong>Production considerations</strong>: <strong>API keys</strong> &mdash; restrict by HTTP referrer in Google Cloud Console; never expose unrestricted keys (you&rsquo;ll get billed for someone else&rsquo;s usage). <strong>Lazy load the map library</strong> &mdash; use dynamic <code>import()</code> for routes that don&rsquo;t always need the map (saves ~200KB on initial bundle). <strong>Geolocation requires HTTPS</strong> in modern browsers and explicit user consent. <strong>Many markers</strong> (1000+) &mdash; use marker clustering (<code>@googlemaps/markerclusterer</code>) to avoid janky rendering. <strong>SSR</strong> &mdash; map libraries are client-only; in Next.js, use dynamic import with <code>ssr: false</code> or render in a Client Component.</p>

<p><strong>For very simple needs</strong> (just show one address): an iframe with Google Maps embed URL is free and zero-JS &mdash; no API key needed. <code>&lt;iframe src="https://www.google.com/maps?q=..." /&gt;</code>.</p>
'''

ANSWERS[70] = r'''
<p><strong>Situation:</strong> a form has nested objects &mdash; e.g., a user profile with shipping address (street, city, zip), billing address, and a list of children with their own fields. Each nested entity has its own validation; the data structure mirrors the API/database shape. Flattening everything into <code>userName_streetLine1</code> field names is fragile and ugly.</p>

<p><strong>Approach:</strong> use <strong>React Hook Form&rsquo;s dot notation</strong> for nested registration (<code>{...register("address.city")}</code>) and <strong>Zod schemas</strong> for nested validation. RHF handles the nested state; Zod validates the structure. For arrays of nested objects, combine with <code>useFieldArray</code>.</p>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const addressSchema = z.object({
  street: z.string().min(1, "Street required"),
  city: z.string().min(1, "City required"),
  zip: z.string().regex(/^\d{5}(-\d{4})?$/, "Invalid ZIP")
});

const personSchema = z.object({
  name: z.string().min(1, "Name required"),
  email: z.string().email("Valid email required"),
  shipping: addressSchema,
  billing: addressSchema,
  preferences: z.object({
    newsletter: z.boolean(),
    notifications: z.object({
      email: z.boolean(),
      sms:   z.boolean()
    })
  })
});

type FormValues = z.infer&lt;typeof personSchema&gt;;

function ProfileForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue
  } = useForm&lt;FormValues&gt;({
    resolver: zodResolver(personSchema),
    defaultValues: {
      name: "",
      email: "",
      shipping: { street: "", city: "", zip: "" },
      billing:  { street: "", city: "", zip: "" },
      preferences: {
        newsletter: false,
        notifications: { email: true, sms: false }
      }
    }
  });

  // Convenience: copy shipping → billing
  const sameAsShipping = watch("billing.street") === watch("shipping.street") &amp;&amp;
                         watch("billing.city")   === watch("shipping.city")   &amp;&amp;
                         watch("billing.zip")    === watch("shipping.zip");

  const copyShippingToBilling = () =&gt; {
    setValue("billing", watch("shipping"));
  };

  return (
    &lt;form onSubmit={handleSubmit(data =&gt; console.log(data))}&gt;
      &lt;fieldset&gt;
        &lt;legend&gt;Personal info&lt;/legend&gt;
        &lt;label&gt;
          Name: &lt;input {...register("name")} /&gt;
          {errors.name &amp;&amp; &lt;span className="err"&gt;{errors.name.message}&lt;/span&gt;}
        &lt;/label&gt;
        &lt;label&gt;
          Email: &lt;input type="email" {...register("email")} /&gt;
          {errors.email &amp;&amp; &lt;span className="err"&gt;{errors.email.message}&lt;/span&gt;}
        &lt;/label&gt;
      &lt;/fieldset&gt;

      &lt;fieldset&gt;
        &lt;legend&gt;Shipping address&lt;/legend&gt;
        &lt;label&gt;
          Street: &lt;input {...register("shipping.street")} /&gt;
          {errors.shipping?.street &amp;&amp;
            &lt;span className="err"&gt;{errors.shipping.street.message}&lt;/span&gt;}
        &lt;/label&gt;
        &lt;label&gt;
          City: &lt;input {...register("shipping.city")} /&gt;
          {errors.shipping?.city &amp;&amp;
            &lt;span className="err"&gt;{errors.shipping.city.message}&lt;/span&gt;}
        &lt;/label&gt;
        &lt;label&gt;
          ZIP: &lt;input {...register("shipping.zip")} /&gt;
          {errors.shipping?.zip &amp;&amp;
            &lt;span className="err"&gt;{errors.shipping.zip.message}&lt;/span&gt;}
        &lt;/label&gt;
      &lt;/fieldset&gt;

      &lt;fieldset&gt;
        &lt;legend&gt;
          Billing address
          &lt;button type="button" onClick={copyShippingToBilling}&gt;
            Same as shipping
          &lt;/button&gt;
        &lt;/legend&gt;
        &lt;label&gt;Street: &lt;input {...register("billing.street")} /&gt;&lt;/label&gt;
        &lt;label&gt;City: &lt;input {...register("billing.city")} /&gt;&lt;/label&gt;
        &lt;label&gt;ZIP: &lt;input {...register("billing.zip")} /&gt;&lt;/label&gt;
      &lt;/fieldset&gt;

      &lt;fieldset&gt;
        &lt;legend&gt;Preferences&lt;/legend&gt;
        &lt;label&gt;
          &lt;input type="checkbox" {...register("preferences.newsletter")} /&gt;
          Newsletter
        &lt;/label&gt;
        &lt;label&gt;
          &lt;input type="checkbox" {...register("preferences.notifications.email")} /&gt;
          Email notifications
        &lt;/label&gt;
        &lt;label&gt;
          &lt;input type="checkbox" {...register("preferences.notifications.sms")} /&gt;
          SMS notifications
        &lt;/label&gt;
      &lt;/fieldset&gt;

      &lt;button type="submit"&gt;Save&lt;/button&gt;
    &lt;/form&gt;
  );
}

// === Reusable AddressFieldset to reduce duplication ===
function AddressFieldset({
  prefix,
  errors
}: {
  prefix: "shipping" | "billing";
  errors: any;
}) {
  const { register } = useFormContext();   // from FormProvider

  return (
    &lt;fieldset&gt;
      &lt;legend&gt;{prefix === "shipping" ? "Shipping" : "Billing"} address&lt;/legend&gt;
      &lt;input
        {...register(`${prefix}.street`)}
        placeholder="Street"
        aria-invalid={!!errors?.[prefix]?.street}
      /&gt;
      &lt;input {...register(`${prefix}.city`)} placeholder="City" /&gt;
      &lt;input {...register(`${prefix}.zip`)} placeholder="ZIP" /&gt;
    &lt;/fieldset&gt;
  );
}

// Use FormProvider to share form context with nested components
import { FormProvider, useFormContext } from "react-hook-form";</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>RHF dot notation + Zod</td><td>Type-safe; matches API shape; reusable subcomponents</td><td>Library setup</td></tr>
  <tr><td>Manual nested useState</td><td>No deps</td><td>Tedious updates: <code>setUser({ ...user, address: { ...user.address, city: x } })</code></td></tr>
  <tr><td>Flatten to top-level fields</td><td>Simpler form code</td><td>Mismatch with API shape; manual reshape on submit</td></tr>
  <tr><td>useReducer with nested reducers</td><td>Centralized; testable</td><td>More code than RHF</td></tr>
</table>

<p><strong>Reusable nested components</strong> &mdash; pass a <code>prefix</code> prop and use <code>useFormContext()</code> from RHF&rsquo;s <code>FormProvider</code>; the same <code>AddressFieldset</code> works for shipping AND billing. <strong>Conditional fields</strong> &mdash; use <code>watch</code> to react to other fields (e.g., show "company name" if "type === &lsquo;business&rsquo;"). <strong>Server validation errors mapped to nested paths</strong> &mdash; RHF&rsquo;s <code>setError("shipping.zip", { message: "Invalid for region" })</code> places the error on the right nested field. <strong>Performance</strong> &mdash; RHF doesn&rsquo;t re-render the whole form when one nested field changes; only the field with the error updates. <strong>Submission</strong> &mdash; the data structure passed to your handler is already nested correctly &mdash; submit it directly to your API.</p>
'''

ANSWERS[71] = r'''
<p><strong>Situation:</strong> an app needs SSR for SEO, faster first paint, and social sharing previews. Modern React SSR is dominated by <strong>Next.js</strong> &mdash; especially the App Router with React Server Components, which moves data fetching and rendering to the server by default.</p>

<p><strong>Approach:</strong> use <strong>Next.js 15+ App Router</strong>. Components are Server Components by default (rendered on server, no JS shipped); add <code>"use client"</code> only where you need interactivity. Data is fetched in components via async/await; the bundler handles streaming HTML to the client.</p>

<pre><code>// Install: npx create-next-app@latest

// === File structure (App Router) ===
// app/
// ├── layout.tsx              ← root layout, persists across navigations
// ├── page.tsx                ← home page (/)
// ├── loading.tsx             ← shown while page&rsquo;s data loads
// ├── error.tsx               ← caught render errors
// ├── not-found.tsx           ← 404 for this segment
// ├── products/
// │   ├── page.tsx            ← /products
// │   └── [id]/
// │       ├── page.tsx        ← /products/:id
// │       └── loading.tsx
// └── api/
//     └── products/route.ts   ← API endpoint

// === app/layout.tsx — root layout ===
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "My App",
  description: "..."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    &lt;html lang="en"&gt;
      &lt;body className={inter.className}&gt;
        &lt;Header /&gt;
        &lt;main&gt;{children}&lt;/main&gt;
        &lt;Footer /&gt;
      &lt;/body&gt;
    &lt;/html&gt;
  );
}

// === app/products/page.tsx — Server Component (default) ===
async function getProducts() {
  // Runs on server. Direct DB or service call OK.
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 60 }   // ISR: cache for 60s
  });
  return res.json();
}

export default async function ProductsPage() {
  const products = await getProducts();   // no useEffect needed!

  return (
    &lt;div&gt;
      &lt;h1&gt;Products&lt;/h1&gt;
      &lt;ul&gt;
        {products.map((p: any) =&gt; (
          &lt;li key={p.id}&gt;
            &lt;Link href={`/products/${p.id}`}&gt;{p.name}&lt;/Link&gt;
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}

// === app/products/[id]/page.tsx ===
type Props = { params: { id: string } };

// Per-page metadata (SEO + Open Graph)
export async function generateMetadata({ params }: Props) {
  const product = await getProduct(params.id);
  return {
    title: product.name,
    description: product.description,
    openGraph: { images: [product.image] }
  };
}

export default async function ProductPage({ params }: Props) {
  const product = await getProduct(params.id);

  if (!product) notFound();   // triggers not-found.tsx

  return (
    &lt;article&gt;
      &lt;h1&gt;{product.name}&lt;/h1&gt;
      &lt;p&gt;{product.description}&lt;/p&gt;
      {/* Client component for the interactive cart button */}
      &lt;AddToCartButton productId={product.id} /&gt;
    &lt;/article&gt;
  );
}

// === Mark interactive components with "use client" ===
// app/components/AddToCartButton.tsx
"use client";

import { useState } from "react";

export default function AddToCartButton({ productId }: { productId: string }) {
  const [adding, setAdding] = useState(false);

  const handleClick = async () =&gt; {
    setAdding(true);
    await fetch("/api/cart", {
      method: "POST",
      body: JSON.stringify({ productId })
    });
    setAdding(false);
  };

  return (
    &lt;button onClick={handleClick} disabled={adding}&gt;
      {adding ? "Adding..." : "Add to cart"}
    &lt;/button&gt;
  );
}

// === Streaming with Suspense ===
import { Suspense } from "react";

export default function DashboardPage() {
  return (
    &lt;div&gt;
      &lt;h1&gt;Dashboard&lt;/h1&gt;

      &lt;Suspense fallback={&lt;StatsSkeleton /&gt;}&gt;
        {/* @ts-expect-error Async Server Component */}
        &lt;Stats /&gt;
      &lt;/Suspense&gt;

      &lt;Suspense fallback={&lt;ChartSkeleton /&gt;}&gt;
        {/* @ts-expect-error Async Server Component */}
        &lt;RevenueChart /&gt;
      &lt;/Suspense&gt;
    &lt;/div&gt;
  );
}

async function Stats() {
  const stats = await getStats();   // slow query OK — streams independently
  return &lt;StatsView stats={stats} /&gt;;
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Rendering strategy</th><th>When data fetches</th><th>Cache directive</th></tr>
  <tr><td>Static (default)</td><td>At build time</td><td>(default)</td></tr>
  <tr><td>ISR</td><td>Cached, regenerated on schedule</td><td><code>{ next: { revalidate: 60 } }</code></td></tr>
  <tr><td>Dynamic SSR</td><td>Per-request on server</td><td><code>{ cache: "no-store" }</code></td></tr>
  <tr><td>Client-side</td><td>In browser after hydration</td><td><code>"use client"</code> + useEffect/useQuery</td></tr>
</table>

<p><strong>Critical Server Component rules</strong>: can&rsquo;t use hooks, browser APIs, or event handlers; can be async; receives props from URL params and search params; runs once per request. <strong>Critical Client Component rules</strong>: must declare <code>"use client"</code> at top of file; can use all React features; ships JS to browser; can&rsquo;t be async by default. <strong>The <code>"use client"</code> boundary</strong> &mdash; once you&rsquo;re inside a Client Component, all imported components are also client (even without their own directive).</p>

<p><strong>For non-Next.js apps</strong>: <strong>Remix / React Router v7</strong> with loaders is the closest alternative; <strong>Astro</strong> for content-heavy sites with islands of interactivity; manual SSR with <code>renderToPipeableStream</code> + Express works but you&rsquo;re re-implementing what Next.js does. <strong>Don&rsquo;t add SSR to a CSR app to "improve performance"</strong> &mdash; the migration cost is high; use it from the start when SEO/social previews matter.</p>
'''

ANSWERS[72] = r'''
<p><strong>Situation:</strong> a design system needs a single <code>&lt;Input&gt;</code> component that handles labels, validation states, error messages, helper text, and accessibility &mdash; reused across dozens of forms. Doing this per-input form-by-form leads to inconsistent UX and accessibility gaps.</p>

<p><strong>Approach:</strong> build a flexible Input component that wraps the native input, accepts label/error/hint props, generates IDs for label association and ARIA attributes, and integrates cleanly with React Hook Form via <code>forwardRef</code> (or React 19&rsquo;s ref-as-prop).</p>

<pre><code>import { forwardRef, useId } from "react";
import type { InputHTMLAttributes } from "react";

type InputProps = {
  label: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
} &amp; InputHTMLAttributes&lt;HTMLInputElement&gt;;

export const Input = forwardRef&lt;HTMLInputElement, InputProps&gt;(
  ({ label, error, hint, leftIcon, rightIcon, className, ...rest }, ref) =&gt; {
    const id = useId();
    const errorId = `${id}-err`;
    const hintId = `${id}-hint`;

    // Build aria-describedby from whichever helper text exists
    const describedBy = [
      hint &amp;&amp; hintId,
      error &amp;&amp; errorId
    ].filter(Boolean).join(" ") || undefined;

    return (
      &lt;div className={`form-field ${error ? "has-error" : ""}`}&gt;
        &lt;label htmlFor={id} className="form-label"&gt;
          {label}
          {rest.required &amp;&amp; &lt;span aria-hidden="true" className="required"&gt;*&lt;/span&gt;}
        &lt;/label&gt;

        &lt;div className="input-wrap"&gt;
          {leftIcon &amp;&amp; &lt;span className="icon icon-left" aria-hidden&gt;{leftIcon}&lt;/span&gt;}

          &lt;input
            id={id}
            ref={ref}
            aria-invalid={!!error}
            aria-describedby={describedBy}
            className={`form-input ${className || ""}`}
            {...rest}
          /&gt;

          {rightIcon &amp;&amp; &lt;span className="icon icon-right" aria-hidden&gt;{rightIcon}&lt;/span&gt;}
        &lt;/div&gt;

        {hint &amp;&amp; !error &amp;&amp; (
          &lt;p id={hintId} className="form-hint"&gt;{hint}&lt;/p&gt;
        )}

        {error &amp;&amp; (
          &lt;p id={errorId} role="alert" className="form-error"&gt;
            {error}
          &lt;/p&gt;
        )}
      &lt;/div&gt;
    );
  }
);

Input.displayName = "Input";

// === Usage with React Hook Form ===
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email("Please enter a valid email"),
  password: z.string().min(8, "At least 8 characters")
});

function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm({ resolver: zodResolver(schema) });

  return (
    &lt;form onSubmit={handleSubmit(data =&gt; console.log(data))}&gt;
      &lt;Input
        label="Email"
        type="email"
        autoComplete="email"
        leftIcon="✉"
        hint="We&rsquo;ll never share your email"
        error={errors.email?.message}
        required
        {...register("email")}
      /&gt;

      &lt;Input
        label="Password"
        type="password"
        autoComplete="new-password"
        hint="At least 8 characters"
        error={errors.password?.message}
        required
        {...register("password")}
      /&gt;

      &lt;button type="submit"&gt;Sign up&lt;/button&gt;
    &lt;/form&gt;
  );
}

// === Variants for different sizes/styles ===
type InputVariant = "default" | "filled" | "outlined";
type InputSize = "sm" | "md" | "lg";

const variantClasses: Record&lt;InputVariant, string&gt; = {
  default:  "border border-gray-300 bg-white",
  filled:   "border-0 bg-gray-100",
  outlined: "border-2 border-blue-500 bg-transparent"
};

const sizeClasses: Record&lt;InputSize, string&gt; = {
  sm: "px-2 py-1 text-sm",
  md: "px-3 py-2 text-base",
  lg: "px-4 py-3 text-lg"
};

// Add these as additional props on Input

// === React 19 simpler version (ref as prop) ===
function InputV19({
  label,
  error,
  hint,
  ref,                     // ref is now a regular prop in React 19
  ...rest
}: InputProps &amp; { ref?: React.Ref&lt;HTMLInputElement&gt; }) {
  const id = useId();
  // ... same body, no forwardRef wrapper needed
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Best for</th></tr>
  <tr><td>Custom component (above)</td><td>In-house design system; full control</td></tr>
  <tr><td>shadcn/ui Input</td><td>Tailwind apps; copy-paste components you own</td></tr>
  <tr><td>Material UI / Chakra UI</td><td>Big component libraries; less code; less customization</td></tr>
  <tr><td>Radix UI Input + custom styling</td><td>Headless: a11y solved, styling yours</td></tr>
</table>

<p><strong>Accessibility checklist that the example above covers</strong>: <code>useId</code> for unique label-input pairing; <code>aria-invalid</code> when there&rsquo;s an error; <code>aria-describedby</code> linking to hint/error text; <code>role="alert"</code> on errors so screen readers announce them; the <code>htmlFor</code> on label so clicking it focuses the input; required indicator with <code>aria-hidden</code> so screen readers don&rsquo;t announce the asterisk twice (the <code>required</code> attribute itself is announced).</p>

<p><strong>Don&rsquo;t reinvent native inputs</strong>: native <code>&lt;input&gt;</code> handles focus, keyboard, spellcheck, autofill, password managers, autocomplete. A custom &ldquo;input&rdquo; built from divs + contenteditable breaks all of these. Wrap the native input; don&rsquo;t replace it. <strong>Composable variants</strong> &mdash; <code>variant</code>, <code>size</code>, <code>density</code> as props let you build complex UI from one component. <strong>For password fields</strong>, add a show/hide toggle (right icon area); for search, add a clear button; for currency, format the value on blur. These domain-specific behaviors should live in specialized components (PasswordInput, SearchInput) that compose from the base Input.</p>
'''

ANSWERS[73] = r'''
<p><strong>Situation:</strong> an app needs URL-driven page navigation without full page reloads &mdash; users see different views, the URL updates, browser back/forward work, and direct links to inner pages work. The 2026 React choice: <strong>React Router v6.4+</strong> (the data API version with loaders/actions) or <strong>v7</strong> (which is essentially Remix as a router); for Next.js apps, the App Router replaces React Router entirely.</p>

<p><strong>Approach:</strong> declare routes via <code>createBrowserRouter</code>; add loaders for per-route data fetching; use <code>useNavigate</code>/<code>Link</code> for programmatic and declarative navigation; handle 404 with a catch-all route. Configure server fallback for direct URL hits.</p>

<pre><code>// Install: npm install react-router-dom

// === Modern data API (v6.4+) ===
import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
  Link,
  NavLink,
  useNavigate,
  useLoaderData,
  redirect
} from "react-router-dom";

// Route components
function RootLayout() {
  return (
    &lt;&gt;
      &lt;header&gt;
        &lt;nav&gt;
          &lt;NavLink to="/"&gt;Home&lt;/NavLink&gt;
          &lt;NavLink to="/products"&gt;Products&lt;/NavLink&gt;
          &lt;NavLink to="/about"&gt;About&lt;/NavLink&gt;
        &lt;/nav&gt;
      &lt;/header&gt;
      &lt;main&gt;
        &lt;Outlet /&gt;
      &lt;/main&gt;
    &lt;/&gt;
  );
}

function ProductsPage() {
  const products = useLoaderData() as Product[];
  return (
    &lt;ul&gt;
      {products.map(p =&gt; (
        &lt;li key={p.id}&gt;&lt;Link to={`/products/${p.id}`}&gt;{p.name}&lt;/Link&gt;&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}

function ProductDetail() {
  const product = useLoaderData() as Product;
  return (
    &lt;article&gt;
      &lt;h1&gt;{product.name}&lt;/h1&gt;
      &lt;p&gt;{product.description}&lt;/p&gt;
    &lt;/article&gt;
  );
}

// Loaders run before navigation completes — page renders only after data is ready
const productsLoader = async () =&gt; {
  const res = await fetch("/api/products");
  if (!res.ok) throw new Response("Failed", { status: res.status });
  return res.json();
};

const productLoader = async ({ params }: any) =&gt; {
  const res = await fetch(`/api/products/${params.id}`);
  if (res.status === 404) throw new Response("Not found", { status: 404 });
  return res.json();
};

// Auth guard via loader
const dashboardLoader = async () =&gt; {
  const user = await getCurrentUser();
  if (!user) throw redirect("/login");
  return user;
};

// === Router definition ===
const router = createBrowserRouter([
  {
    path: "/",
    element: &lt;RootLayout /&gt;,
    errorElement: &lt;ErrorPage /&gt;,
    children: [
      { index: true, element: &lt;Home /&gt; },
      {
        path: "products",
        children: [
          { index: true, element: &lt;ProductsPage /&gt;, loader: productsLoader },
          { path: ":id", element: &lt;ProductDetail /&gt;, loader: productLoader }
        ]
      },
      {
        path: "dashboard",
        element: &lt;DashboardLayout /&gt;,
        loader: dashboardLoader,
        children: [
          { index: true, element: &lt;Overview /&gt; },
          { path: "settings", element: &lt;Settings /&gt; }
        ]
      },
      { path: "about", element: &lt;About /&gt; },
      { path: "*", element: &lt;NotFound /&gt; }
    ]
  }
]);

function App() {
  return &lt;RouterProvider router={router} /&gt;;
}

// === Programmatic navigation ===
function LoginButton() {
  const navigate = useNavigate();

  const handleLogin = async () =&gt; {
    await loginUser();
    navigate("/dashboard", { replace: true });
  };

  return &lt;button onClick={handleLogin}&gt;Sign in&lt;/button&gt;;
}

// === URL search params (filters, pagination, sort) ===
import { useSearchParams } from "react-router-dom";

function ProductFilters() {
  const [searchParams, setSearchParams] = useSearchParams();
  const category = searchParams.get("category") || "all";
  const sort = searchParams.get("sort") || "popular";

  const updateFilter = (key: string, value: string) =&gt; {
    setSearchParams(prev =&gt; {
      const next = new URLSearchParams(prev);
      if (value === "" || value === "all") next.delete(key);
      else next.set(key, value);
      return next;
    });
  };

  return (
    &lt;&gt;
      &lt;select value={category} onChange={e =&gt; updateFilter("category", e.target.value)}&gt;
        &lt;option value="all"&gt;All&lt;/option&gt;
        &lt;option value="electronics"&gt;Electronics&lt;/option&gt;
      &lt;/select&gt;
      &lt;select value={sort} onChange={e =&gt; updateFilter("sort", e.target.value)}&gt;
        &lt;option value="popular"&gt;Popular&lt;/option&gt;
        &lt;option value="newest"&gt;Newest&lt;/option&gt;
      &lt;/select&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Router</th><th>Best for</th></tr>
  <tr><td>React Router v6.4+ data API</td><td>SPA with route loaders/actions; SSR-aware</td></tr>
  <tr><td>React Router v7</td><td>Latest; framework features (Remix patterns); SSR or SPA</td></tr>
  <tr><td>Next.js App Router</td><td>SSR/SSG/RSC by default; production fullstack</td></tr>
  <tr><td>TanStack Router</td><td>Type-safe routes; first-class search params; younger</td></tr>
  <tr><td>Wouter</td><td>Tiny (~2KB); good for very simple apps</td></tr>
</table>

<p><strong>Critical configuration</strong>: <strong>server fallback</strong> &mdash; BrowserRouter URLs need server to serve <code>index.html</code> for unknown paths. Vercel/Netlify auto-handle this; nginx needs <code>try_files $uri $uri/ /index.html;</code>; without this, refreshing on <code>/products/42</code> shows the server&rsquo;s 404. <strong>Catch-all route</strong> (<code>path: "*"</code>) renders your custom 404 page. <strong>URL search params</strong> for filters/pagination &mdash; users can bookmark and share filtered views; the URL is the source of truth, not React state.</p>

<p><strong>Don&rsquo;t use <code>HashRouter</code> for new apps</strong> &mdash; ugly URLs (<code>#/products</code>), bad SEO, harder to share. Only use it when you can&rsquo;t configure server fallback (e.g., static GitHub Pages without rewrite support, but even there workarounds exist).</p>

<p><strong>Migrate from old patterns</strong>: <code>useHistory</code> → <code>useNavigate</code>; <code>history.push</code> → <code>navigate(to)</code>; <code>history.replace</code> → <code>navigate(to, { replace: true })</code>. Switch to data API for any new code; the old <code>&lt;Routes&gt;</code> + <code>&lt;Route&gt;</code> with <code>useEffect</code>-based fetching still works but loses the loader benefits (parallel data fetching, no flash of loading state).</p>
'''

ANSWERS[74] = r'''
<p><strong>Situation:</strong> a UI needs to display hierarchical data &mdash; file system, organization chart, product categories, comment threads. Each node may have children, be expandable, support selection, and operations (rename, delete). For 100+ deeply-nested items, virtualization becomes essential.</p>

<p><strong>Approach:</strong> for simple cases, recursive <code>TreeNode</code> component that renders itself + children. For production with thousands of nodes, drag-drop, multi-select, and virtualization, use <strong>react-arborist</strong> &mdash; the modern recommended library that handles all of this.</p>

<pre><code>// === Custom recursive tree (educational / small datasets) ===
import { useState } from "react";

type TreeNode = {
  id: string;
  name: string;
  children?: TreeNode[];
};

function TreeNodeView({ node, level = 0 }: { node: TreeNode; level?: number }) {
  const [expanded, setExpanded] = useState(level &lt; 1);   // first level open
  const hasChildren = !!node.children?.length;

  return (
    &lt;li role="treeitem" aria-expanded={hasChildren ? expanded : undefined}&gt;
      &lt;div
        style={{
          paddingLeft: level * 20,
          padding: "4px 8px",
          cursor: hasChildren ? "pointer" : "default",
          userSelect: "none",
          fontFamily: "monospace"
        }}
        onClick={() =&gt; hasChildren &amp;&amp; setExpanded(!expanded)}
      &gt;
        {hasChildren ? (expanded ? "▼" : "▶") : " "}
        {hasChildren ? "📁" : "📄"} {node.name}
      &lt;/div&gt;

      {hasChildren &amp;&amp; expanded &amp;&amp; (
        &lt;ul role="group" style={{ listStyle: "none", padding: 0 }}&gt;
          {node.children!.map(child =&gt; (
            &lt;TreeNodeView key={child.id} node={child} level={level + 1} /&gt;
          ))}
        &lt;/ul&gt;
      )}
    &lt;/li&gt;
  );
}

function TreeView({ data }: { data: TreeNode }) {
  return (
    &lt;ul role="tree" aria-label="File explorer" style={{ listStyle: "none", padding: 0 }}&gt;
      &lt;TreeNodeView node={data} /&gt;
    &lt;/ul&gt;
  );
}

// === react-arborist for production ===
// Install: npm install react-arborist

import { Tree, NodeRendererProps } from "react-arborist";

const data = [
  {
    id: "1", name: "src",
    children: [
      { id: "2", name: "App.tsx" },
      { id: "3", name: "components", children: [
        { id: "4", name: "Button.tsx" },
        { id: "5", name: "Input.tsx" }
      ]},
    ]
  },
  { id: "6", name: "package.json" }
];

function FileNode({ node, style, dragHandle }: NodeRendererProps&lt;any&gt;) {
  return (
    &lt;div
      ref={dragHandle}
      style={{
        ...style,
        padding: "4px 8px",
        background: node.isSelected ? "#e0f2fe" : "transparent",
        cursor: "pointer",
        display: "flex",
        gap: 6
      }}
      onClick={() =&gt; node.toggle()}
    &gt;
      &lt;span&gt;
        {node.isLeaf ? "📄" : node.isOpen ? "📂" : "📁"}
      &lt;/span&gt;
      &lt;span&gt;{node.data.name}&lt;/span&gt;
    &lt;/div&gt;
  );
}

function FileExplorer() {
  return (
    &lt;Tree
      data={data}
      width={300}
      height={500}
      indent={20}
      rowHeight={28}
      openByDefault={false}
      onMove={({ dragIds, parentId, index }) =&gt; {
        // Persist reorder to backend
        console.log("Move", dragIds, "to", parentId, "at", index);
      }}
      onRename={({ id, name }) =&gt; {
        // Persist rename to backend
        console.log("Rename", id, "to", name);
      }}
    &gt;
      {FileNode}
    &lt;/Tree&gt;
  );
}

// === Selection + multi-select ===
function SelectableTree() {
  const [selected, setSelected] = useState&lt;Set&lt;string&gt;&gt;(new Set());

  return (
    &lt;Tree
      data={data}
      width={300}
      height={500}
      selectionFollowsFocus
      onSelect={(nodes) =&gt; setSelected(new Set(nodes.map(n =&gt; n.id)))}
    &gt;
      {(nodeProps) =&gt; (
        &lt;div
          ref={nodeProps.dragHandle}
          style={{
            ...nodeProps.style,
            background: selected.has(nodeProps.node.id) ? "#e0f2fe" : "transparent"
          }}
        &gt;
          {nodeProps.node.data.name}
        &lt;/div&gt;
      )}
    &lt;/Tree&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Best for</th><th>Limitations</th></tr>
  <tr><td>Custom recursive</td><td>&lt; 200 nodes; learning</td><td>No virtualization; manual a11y; perf issues at scale</td></tr>
  <tr><td>react-arborist</td><td>1000-10000+ nodes; production trees</td><td>Library dependency; styled defaults need overriding</td></tr>
  <tr><td>react-treebeard / rc-tree</td><td>Antd-compatible UIs</td><td>Older; less flexible</td></tr>
  <tr><td>Build on react-virtual</td><td>Custom needs not met by libraries</td><td>Significant code</td></tr>
</table>

<p><strong>Accessibility for tree views</strong>: <code>role="tree"</code> on the container; <code>role="treeitem"</code> on each node; <code>role="group"</code> on child lists; <code>aria-expanded</code> on expandable nodes (true/false/undefined for leaves); <code>aria-selected</code> for selectable nodes; arrow keys navigate (Up/Down between siblings/cousins, Right opens, Left closes); Home/End jump to first/last; Enter activates. react-arborist handles all of this.</p>

<p><strong>Lazy loading children</strong>: for trees backed by an API where loading all data upfront is wasteful (file system browser, S3 explorer, large org chart), fetch a node&rsquo;s children only when expanded. Show a loading state inline; cache results in TanStack Query keyed by parent ID.</p>

<p><strong>Drag-and-drop in tree views is genuinely hard</strong> &mdash; collision detection across levels, validation (can&rsquo;t drop a parent into its descendant), visual feedback for valid/invalid drop targets. react-arborist gets all this right; rolling your own with raw dnd-kit is a substantial project.</p>
'''

ANSWERS[75] = r'''
<p><strong>Situation:</strong> a multi-step form (wizard) needs to manage accumulated state across steps, validate per-step before advancing, allow backward navigation without losing data, persist across reloads, and submit a combined payload. Patterns: maintain accumulated form state, validate per step before advancing, allow back navigation without losing data, persist state for refresh resilience, show progress indicator.</p>

<p><strong>Approach:</strong> use <code>useReducer</code> for the wizard state machine (step + per-section data + errors); use <strong>React Hook Form + Zod</strong> per step for field validation; persist to <code>sessionStorage</code> for refresh resilience; URL-drive the step number for shareable progress.</p>

<pre><code>import { useReducer, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// === Schemas per step ===
const personalSchema = z.object({
  name: z.string().min(1),
  email: z.string().email()
});

const addressSchema = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  zip: z.string().regex(/^\d{5}$/)
});

const paymentSchema = z.object({
  cardNumber: z.string().regex(/^\d{16}$/),
  expiry: z.string().regex(/^\d{2}\/\d{2}$/),
  cvv: z.string().regex(/^\d{3,4}$/)
});

type WizardData = {
  personal?: z.infer&lt;typeof personalSchema&gt;;
  address?:  z.infer&lt;typeof addressSchema&gt;;
  payment?:  z.infer&lt;typeof paymentSchema&gt;;
};

type State = { step: number; data: WizardData };

type Action =
  | { type: "SET_STEP"; step: number }
  | { type: "SAVE_DATA"; section: keyof WizardData; values: any }
  | { type: "RESET" };

const STORAGE_KEY = "checkout-wizard";

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_STEP":
      return { ...state, step: action.step };
    case "SAVE_DATA":
      return {
        ...state,
        data: { ...state.data, [action.section]: action.values }
      };
    case "RESET":
      return { step: 0, data: {} };
    default:
      return state;
  }
}

function init(): State {
  try {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return { step: 0, data: {} };
}

// === Wizard root ===
function CheckoutWizard() {
  const [state, dispatch] = useReducer(reducer, undefined, init);
  const [searchParams, setSearchParams] = useSearchParams();

  // URL ↔ step sync
  useEffect(() =&gt; {
    const urlStep = parseInt(searchParams.get("step") || "0", 10);
    if (urlStep !== state.step &amp;&amp; urlStep &gt;= 0 &amp;&amp; urlStep &lt;= 2) {
      dispatch({ type: "SET_STEP", step: urlStep });
    }
  }, [searchParams]);

  useEffect(() =&gt; {
    setSearchParams({ step: String(state.step) });
  }, [state.step, setSearchParams]);

  // Persist
  useEffect(() =&gt; {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const submitFinal = async () =&gt; {
    const fullData = state.data;
    const res = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(fullData)
    });
    if (res.ok) {
      sessionStorage.removeItem(STORAGE_KEY);
      dispatch({ type: "RESET" });
      // navigate to success page
    }
  };

  return (
    &lt;div&gt;
      &lt;ProgressIndicator step={state.step} totalSteps={3} /&gt;

      {state.step === 0 &amp;&amp; (
        &lt;PersonalStep
          initial={state.data.personal}
          onNext={(values) =&gt; {
            dispatch({ type: "SAVE_DATA", section: "personal", values });
            dispatch({ type: "SET_STEP", step: 1 });
          }}
        /&gt;
      )}
      {state.step === 1 &amp;&amp; (
        &lt;AddressStep
          initial={state.data.address}
          onBack={() =&gt; dispatch({ type: "SET_STEP", step: 0 })}
          onNext={(values) =&gt; {
            dispatch({ type: "SAVE_DATA", section: "address", values });
            dispatch({ type: "SET_STEP", step: 2 });
          }}
        /&gt;
      )}
      {state.step === 2 &amp;&amp; (
        &lt;PaymentStep
          initial={state.data.payment}
          onBack={() =&gt; dispatch({ type: "SET_STEP", step: 1 })}
          onSubmit={async (values) =&gt; {
            dispatch({ type: "SAVE_DATA", section: "payment", values });
            await submitFinal();
          }}
        /&gt;
      )}
    &lt;/div&gt;
  );
}

// === Reusable step component ===
function PersonalStep({ initial, onNext }: any) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(personalSchema),
    defaultValues: initial || { name: "", email: "" }
  });

  return (
    &lt;form onSubmit={handleSubmit(onNext)}&gt;
      &lt;h2&gt;Personal info&lt;/h2&gt;
      &lt;input {...register("name")} placeholder="Name" /&gt;
      {errors.name &amp;&amp; &lt;span className="err"&gt;{errors.name.message}&lt;/span&gt;}

      &lt;input {...register("email")} type="email" placeholder="Email" /&gt;
      {errors.email &amp;&amp; &lt;span className="err"&gt;{errors.email.message}&lt;/span&gt;}

      &lt;button type="submit"&gt;Next →&lt;/button&gt;
    &lt;/form&gt;
  );
}

// AddressStep, PaymentStep follow the same pattern with their own schema

// === Progress indicator ===
function ProgressIndicator({ step, totalSteps }: { step: number; totalSteps: number }) {
  const labels = ["Personal", "Address", "Payment"];
  return (
    &lt;div role="navigation" aria-label="Checkout progress"&gt;
      &lt;ol style={{ display: "flex", listStyle: "none", padding: 0, gap: 8 }}&gt;
        {labels.map((label, i) =&gt; (
          &lt;li
            key={i}
            aria-current={i === step ? "step" : undefined}
            style={{
              flex: 1, padding: 8, textAlign: "center",
              background: i === step ? "#3b82f6" : i &lt; step ? "#10b981" : "#e5e7eb",
              color: i &lt;= step ? "white" : "#666",
              borderRadius: 4
            }}
          &gt;
            {i + 1}. {label}
          &lt;/li&gt;
        ))}
      &lt;/ol&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pattern</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>useReducer + RHF per step</td><td>Centralized state; per-step validation; testable</td><td>More setup</td></tr>
  <tr><td>Single useForm with all fields</td><td>One form state; simpler</td><td>All fields validated together; harder to navigate steps</td></tr>
  <tr><td>External state machine (XState)</td><td>Complex flows with branching</td><td>Library + learning curve</td></tr>
  <tr><td>URL-driven steps with no shared state</td><td>Refresh-safe; bookmarkable</td><td>Per-step state must persist independently</td></tr>
</table>

<p><strong>Three production-grade behaviors</strong>:</p>
<ul>
  <li><strong>Persist to <code>sessionStorage</code></strong> &mdash; user refreshes mid-checkout and continues where they left off; clear on success or 30 min timeout.</li>
  <li><strong>URL-driven step</strong> &mdash; <code>?step=2</code> in the URL; back button works correctly; users can share &ldquo;I&rsquo;m stuck on step 2&rdquo; for support.</li>
  <li><strong>Validate per step before advancing</strong> &mdash; user can&rsquo;t skip step 2 with empty fields; per-step Zod schemas keep validation logic close to the form.</li>
</ul>

<p><strong>Branching wizards</strong> (different paths based on selections) are where <strong>XState</strong> shines &mdash; visualize the state machine, prevent invalid transitions. For linear wizards, useReducer is plenty. <strong>Don&rsquo;t blindly use sessionStorage for sensitive data</strong> &mdash; payment fields shouldn&rsquo;t persist; mark them as ephemeral and only submit them at final step.</p>
'''

ANSWERS[76] = r'''
<p><strong>Situation:</strong> Multi-level navigation needs breadcrumbs &mdash; "<em>Home / Products / Electronics / Laptops / Dell XPS</em>" &mdash; that auto-derive from the current route, support clickable parent links, and stay consistent across the app without each page hand-coding them.</p>

<p><strong>Approach:</strong> Two solid patterns &mdash; <strong>(1)</strong> derive from React Router&rsquo;s <code>useMatches()</code> + per-route <code>handle</code> metadata, or <strong>(2)</strong> a <code>BreadcrumbContext</code> where pages register their crumbs imperatively. Pattern 1 is preferred because routes are the source of truth.</p>

<pre><code>// Define crumb in route handle (React Router v6.4+)
const router = createBrowserRouter([
  {
    path: "/",
    handle: { crumb: () =&gt; "Home" },
    children: [
      {
        path: "products",
        handle: { crumb: () =&gt; "Products" },
        children: [
          {
            path: ":category",
            handle: { crumb: (data) =&gt; data.category.name },
            loader: ({ params }) =&gt; getCategory(params.category),
            children: [
              {
                path: ":productId",
                handle: { crumb: (data) =&gt; data.product.name },
                loader: ({ params }) =&gt; getProduct(params.productId),
                element: &lt;ProductPage /&gt;
              }
            ]
          }
        ]
      }
    ]
  }
]);

// Breadcrumbs component reads matches
import { Link, useMatches } from "react-router-dom";

function Breadcrumbs() {
  const matches = useMatches();
  const crumbs = matches
    .filter((m) =&gt; m.handle?.crumb)
    .map((m) =&gt; ({ label: m.handle.crumb(m.data), to: m.pathname }));

  return (
    &lt;nav aria-label="Breadcrumb"&gt;
      &lt;ol className="breadcrumbs"&gt;
        {crumbs.map((c, i) =&gt; (
          &lt;li key={c.to}&gt;
            {i &lt; crumbs.length - 1 ? (
              &lt;Link to={c.to}&gt;{c.label}&lt;/Link&gt;
            ) : (
              &lt;span aria-current="page"&gt;{c.label}&lt;/span&gt;
            )}
            {i &lt; crumbs.length - 1 &amp;&amp; &lt;span aria-hidden&gt; / &lt;/span&gt;}
          &lt;/li&gt;
        ))}
      &lt;/ol&gt;
    &lt;/nav&gt;
  );
}</code></pre>

<p><strong>Library options for the production version:</strong></p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>useMatches + handle</td><td>Co-located with routes; data loaders provide labels</td><td>Tied to React Router v6.4+</td></tr>
  <tr><td>BreadcrumbContext + register hook</td><td>Pages control their own crumbs</td><td>Cleanup ordering bugs; race on remount</td></tr>
  <tr><td>Path-based parsing</td><td>No registration needed</td><td>Loses dynamic labels (IDs in URL stay as IDs)</td></tr>
  <tr><td>Static config in nav tree</td><td>Simple; works everywhere</td><td>Drifts from actual routes; manual</td></tr>
</table>

<p><strong>JSON-LD for SEO</strong>: search engines parse breadcrumb structured data and display them in results. Add a <code>&lt;script type="application/ld+json"&gt;</code> with <code>BreadcrumbList</code> schema reflecting the same crumbs.</p>

<p><strong>Trade-offs:</strong> Auto-derived breadcrumbs are correct by construction but require route metadata discipline &mdash; every route needs a crumb function. Loader-driven labels (e.g., product name from data) couple breadcrumbs to data fetching &mdash; convenient but means breadcrumbs render late if loaders are slow; render placeholder ("...") for the dynamic segment while loading. <strong>Accessibility</strong>: <code>nav aria-label="Breadcrumb"</code>, <code>aria-current="page"</code> on the last crumb, and visible separator characters that are <code>aria-hidden</code> so screen readers don&rsquo;t announce them. Don&rsquo;t make the last crumb a link &mdash; users are already there.</p>
'''

ANSWERS[77] = r'''
<p><strong>Situation:</strong> Users should rate products with stars (1-5), optionally leave written reviews, and see aggregated ratings. The system needs accessible star input, optimistic submission, edit/delete of own reviews, sort/filter, and protection against ballot stuffing.</p>

<p><strong>Approach:</strong> Build a star-rating primitive on top of accessible radio buttons (each star is a radio), back it with TanStack Query mutations for optimistic UX, and pair with a review form using React Hook Form + Zod.</p>

<pre><code>// Accessible star rating — uses native radios
function StarRating({ value, onChange, name = "rating", readOnly = false }) {
  return (
    &lt;fieldset className="star-rating" disabled={readOnly}&gt;
      &lt;legend className="sr-only"&gt;Rate this product&lt;/legend&gt;
      {[1, 2, 3, 4, 5].map((n) =&gt; (
        &lt;label key={n} className={n &lt;= value ? "filled" : ""}&gt;
          &lt;input
            type="radio"
            name={name}
            value={n}
            checked={value === n}
            onChange={() =&gt; onChange(n)}
            className="sr-only"
          /&gt;
          &lt;StarIcon /&gt;
          &lt;span className="sr-only"&gt;{n} {n === 1 ? "star" : "stars"}&lt;/span&gt;
        &lt;/label&gt;
      ))}
    &lt;/fieldset&gt;
  );
}</code></pre>

<pre><code>// Review form with optimistic submit
const reviewSchema = z.object({
  rating: z.number().int().min(1).max(5),
  comment: z.string().min(10).max(2000)
});

function ReviewForm({ productId }) {
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors }, control, reset } =
    useForm({ resolver: zodResolver(reviewSchema), defaultValues: { rating: 0, comment: "" } });

  const mutation = useMutation({
    mutationFn: (data) =&gt; api.createReview(productId, data),
    onMutate: async (data) =&gt; {
      await queryClient.cancelQueries({ queryKey: ["reviews", productId] });
      const previous = queryClient.getQueryData(["reviews", productId]);
      queryClient.setQueryData(["reviews", productId], (old = []) =&gt; [
        { id: "temp-" + Date.now(), ...data, status: "pending", user: currentUser },
        ...old
      ]);
      return { previous };
    },
    onError: (err, _, ctx) =&gt; queryClient.setQueryData(["reviews", productId], ctx.previous),
    onSettled: () =&gt; queryClient.invalidateQueries({ queryKey: ["reviews", productId] }),
    onSuccess: () =&gt; reset()
  });

  return (
    &lt;form onSubmit={handleSubmit((data) =&gt; mutation.mutate(data))}&gt;
      &lt;Controller
        name="rating" control={control}
        render={({ field }) =&gt; &lt;StarRating value={field.value} onChange={field.onChange} /&gt;}
      /&gt;
      {errors.rating &amp;&amp; &lt;p role="alert"&gt;Please select a rating&lt;/p&gt;}

      &lt;textarea {...register("comment")} placeholder="What did you think?" /&gt;
      {errors.comment &amp;&amp; &lt;p role="alert"&gt;{errors.comment.message}&lt;/p&gt;}

      &lt;button disabled={mutation.isPending}&gt;Submit review&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Aggregation displayed back to users:</strong></p>

<table>
  <tr><th>Element</th><th>What it shows</th></tr>
  <tr><td>Average score</td><td>4.3 ★ rounded to one decimal</td></tr>
  <tr><td>Count</td><td>"based on 247 reviews"</td></tr>
  <tr><td>Distribution bars</td><td>5★ ▓▓▓▓▓ 65%, 4★ ▓▓ 20%, etc.</td></tr>
  <tr><td>Filters</td><td>Show only verified purchases / by star count</td></tr>
  <tr><td>Sort</td><td>Most helpful, most recent, lowest first</td></tr>
</table>

<p><strong>Trade-offs:</strong> The radio-fieldset pattern gives keyboard navigation, screen-reader announcements, and form-submit integration for free &mdash; building stars from buttons or divs requires reimplementing all of that. <strong>Spam protection</strong>: rate-limit per user/IP server-side; require verified purchase or account; flag identical text across reviews; use hCaptcha for anonymous reviews. <strong>Editing</strong>: allow within a window (24-72 hours) then lock; show "edited" badge with timestamp. <strong>JSON-LD <code>AggregateRating</code></strong> schema for SEO &mdash; rich-result stars in Google. Don&rsquo;t expose raw counts to manipulation by treating the displayed number as authoritative client-side; always recompute server-side after writes.</p>
'''

ANSWERS[78] = r'''
<p><strong>Situation:</strong> A product grid, dashboard, or photo wall must adapt fluidly across phone (1 column), tablet (2-3), desktop (4-6), and ultra-wide (8+) without manual breakpoint maintenance. Items vary in count; layout should look balanced at every width.</p>

<p><strong>Approach:</strong> Use <strong>CSS Grid&rsquo;s <code>auto-fit</code> + <code>minmax()</code></strong> &mdash; the browser computes column count from container width. No JS, no breakpoint media queries, no resize listeners. Pair with <code>aspect-ratio</code> for consistent card heights.</p>

<pre><code>/* Responsive grid — pure CSS */
.responsive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
  gap: 1rem;
}

.grid-card {
  aspect-ratio: 4 / 5;
  border-radius: 12px;
  overflow: hidden;
}</code></pre>

<p><code>auto-fit</code> creates as many columns as fit, each ≥280px and stretching to fill. <code>min(280px, 100%)</code> prevents overflow on phones narrower than 280px. Add columns as the viewport grows; no media queries.</p>

<p><strong>React component with optional config:</strong></p>

<pre><code>function ResponsiveGrid({ minColumnWidth = 280, gap = "1rem", children }) {
  const style = {
    display: "grid",
    gridTemplateColumns: `repeat(auto-fit, minmax(min(${minColumnWidth}px, 100%), 1fr))`,
    gap
  };
  return &lt;div style={style}&gt;{children}&lt;/div&gt;;
}

&lt;ResponsiveGrid minColumnWidth={300}&gt;
  {products.map((p) =&gt; &lt;ProductCard key={p.id} product={p} /&gt;)}
&lt;/ResponsiveGrid&gt;</code></pre>

<p><strong>Pattern decisions:</strong></p>

<table>
  <tr><th>Goal</th><th>CSS</th></tr>
  <tr><td>Auto column count, items fill row</td><td><code>auto-fit, minmax(280px, 1fr)</code></td></tr>
  <tr><td>Auto column count, leave empty cells</td><td><code>auto-fill, minmax(280px, 1fr)</code></td></tr>
  <tr><td>Fixed 4 columns at desktop, 1 on mobile</td><td>Media queries with explicit columns</td></tr>
  <tr><td>Masonry layout (Pinterest-style)</td><td><code>grid-template-rows: masonry</code> (Firefox) or CSS columns / library</td></tr>
  <tr><td>Items span variable columns</td><td><code>grid-column: span N</code> per item</td></tr>
</table>

<p><strong>Container queries</strong> (2026-supported in all modern browsers) give per-component responsiveness regardless of viewport:</p>

<pre><code>.product-shelf {
  container-type: inline-size;
}

@container (min-width: 600px) {
  .product-shelf .grid-card {
    flex-direction: row;     /* horizontal card when shelf is wide */
  }
}</code></pre>

<p>Same component works in a sidebar (narrow) and a main content area (wide) without knowing where it&rsquo;s placed.</p>

<p><strong>Image discipline inside cards</strong>: always set <code>width</code>/<code>height</code> attributes (or <code>aspect-ratio</code>) to prevent CLS; use <code>srcset</code> for responsive variants; <code>loading="lazy"</code> for off-screen items. A grid that "settles" as images load destroys perceived performance even if computed metrics look fine.</p>

<p><strong>Trade-offs:</strong> CSS Grid <code>auto-fit</code> is the simplest answer for 90% of cases &mdash; no JS, no edge cases, scales to any viewport. <strong>Limit</strong>: when columns must align across multiple grids (homepage hero alignment), grid auto-sizing per container produces mismatches; explicit breakpoints serve better there. <strong>For very large lists</strong> (1000+ items), grid layouts force the browser to lay out everything; pair with virtualization (TanStack Virtual, react-virtuoso) and keep grid-by-row but virtualize rows. <strong>Don&rsquo;t reinvent</strong>: Tailwind&rsquo;s <code>grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4</code> works fine, but loses the auto-fit gracefulness; pick based on whether you want fluid (auto-fit) or stepped (breakpoints) responsiveness.</p>
'''

ANSWERS[79] = r'''
<p><strong>Situation:</strong> The app needs a notification system for transient feedback (success toasts, errors, info), persistent alerts (banner: "scheduled maintenance Sunday"), and inline status (form-level errors). Each has different UX requirements: dismissibility, urgency, screen-reader behavior, queueing.</p>

<p><strong>Approach:</strong> Use <strong>Sonner</strong> (the 2026 standard for toasts), a banner context for persistent alerts, and inline alerts for form feedback. Don&rsquo;t conflate them &mdash; toasts are ephemeral, banners are persistent until dismissed.</p>

<pre><code>// 1. Toaster mounted once at app root
import { Toaster, toast } from "sonner";

function App() {
  return (
    &lt;&gt;
      &lt;Toaster position="bottom-right" richColors closeButton /&gt;
      &lt;Routes&gt; ... &lt;/Routes&gt;
    &lt;/&gt;
  );
}

// 2. Trigger from anywhere
toast.success("Profile updated");
toast.error("Failed to save", { description: "Check your connection" });
toast.promise(api.save(data), {
  loading: "Saving...",
  success: "Saved",
  error: "Could not save"
});

// 3. Action toasts
toast("Deleted 3 items", {
  action: { label: "Undo", onClick: () =&gt; restore(items) }
});</code></pre>

<p><strong>Persistent banner system:</strong></p>

<pre><code>// Banner context
type Banner = { id: string; type: "info" | "warning" | "error"; message: string; dismissible?: boolean };

const BannerContext = createContext(null);

function BannerProvider({ children }) {
  const [banners, setBanners] = useState&lt;Banner[]&gt;([]);

  const show = useCallback((banner) =&gt; {
    setBanners((prev) =&gt; [...prev, { ...banner, id: crypto.randomUUID() }]);
  }, []);

  const dismiss = useCallback((id) =&gt; {
    setBanners((prev) =&gt; prev.filter((b) =&gt; b.id !== id));
  }, []);

  return (
    &lt;BannerContext.Provider value={{ show, dismiss }}&gt;
      &lt;div className="banner-stack" role="region" aria-label="Notifications"&gt;
        {banners.map((b) =&gt; (
          &lt;div key={b.id} role="alert" className={`banner banner-${b.type}`}&gt;
            &lt;p&gt;{b.message}&lt;/p&gt;
            {b.dismissible !== false &amp;&amp; (
              &lt;button onClick={() =&gt; dismiss(b.id)} aria-label="Dismiss"&gt;✕&lt;/button&gt;
            )}
          &lt;/div&gt;
        ))}
      &lt;/div&gt;
      {children}
    &lt;/BannerContext.Provider&gt;
  );
}</code></pre>

<p><strong>Notification type decision matrix:</strong></p>

<table>
  <tr><th>Use case</th><th>Component</th><th>ARIA</th></tr>
  <tr><td>Saved successfully</td><td>Toast (auto-dismiss 4s)</td><td><code>role="status"</code></td></tr>
  <tr><td>Critical error</td><td>Toast with <code>type: "error"</code></td><td><code>role="alert"</code></td></tr>
  <tr><td>Site-wide maintenance notice</td><td>Persistent banner at top</td><td><code>role="status"</code></td></tr>
  <tr><td>Account suspended / urgent</td><td>Persistent banner, non-dismissible</td><td><code>role="alert"</code></td></tr>
  <tr><td>Form field error</td><td>Inline below field</td><td><code>aria-describedby</code> + <code>aria-invalid</code></td></tr>
  <tr><td>Form-level summary</td><td>Inline alert above form</td><td><code>role="alert"</code> with <code>tabindex="-1"</code> for focus</td></tr>
  <tr><td>Real-time push (new message)</td><td>Toast + badge update</td><td><code>role="status"</code></td></tr>
</table>

<p><strong>Library options:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>Sonner</td><td>Modern toasts; the 2026 default</td></tr>
  <tr><td>react-hot-toast</td><td>Lightweight alternative; popular</td></tr>
  <tr><td>Radix Toast</td><td>Headless; full custom UI; great a11y</td></tr>
  <tr><td>Custom + AnimatePresence</td><td>When you need full design control</td></tr>
</table>

<p><strong>Trade-offs:</strong> Sonner ships with sensible defaults: stacking, swipe-to-dismiss, screen-reader announcements, position presets, dark mode. Reaching for it ends most toast discussions. <strong>Don&rsquo;t toast everything</strong> &mdash; success toasts on every interaction become noise; reserve them for actions where users need confirmation that something went off-screen (deleted, sent, saved). <strong>Errors should be persistent enough to read</strong> &mdash; default 4s timeout is too fast for long error messages; bump to 8s or require dismissal for severe errors. <strong>Accessibility</strong>: <code>role="alert"</code> announces immediately and rudely (use sparingly &mdash; only true alerts); <code>role="status"</code> announces politely after current speech finishes (the right default for success/info). <strong>Don&rsquo;t put crucial info only in toasts</strong> &mdash; users may miss them entirely; show form errors inline AND optionally toast for global feedback.</p>
'''

ANSWERS[80] = r'''
<p><strong>Situation:</strong> A product page or landing hero needs an image carousel with multiple slides, navigation controls, swipe gestures on touch, autoplay with pause-on-hover, and lazy-loaded images. Must be accessible (keyboard, screen readers) and not bloat the bundle.</p>

<p><strong>Approach:</strong> Reach for <strong>Embla Carousel</strong> (the 2026 standard &mdash; lightweight, accessible, momentum scrolling, no jQuery) or <strong>Swiper.js</strong> for richer feature set. Avoid building from scratch &mdash; touch handling, momentum, peek scrolling, and a11y are all subtle.</p>

<pre><code>// Embla — lightweight, modern, ~7KB
import useEmblaCarousel from "embla-carousel-react";
import Autoplay from "embla-carousel-autoplay";

function HeroCarousel({ slides }) {
  const [emblaRef, emblaApi] = useEmblaCarousel(
    { loop: true, align: "start" },
    [Autoplay({ delay: 5000, stopOnInteraction: true })]
  );

  const [selected, setSelected] = useState(0);

  useEffect(() =&gt; {
    if (!emblaApi) return;
    const onSelect = () =&gt; setSelected(emblaApi.selectedScrollSnap());
    emblaApi.on("select", onSelect);
    onSelect();
    return () =&gt; { emblaApi.off("select", onSelect); };
  }, [emblaApi]);

  return (
    &lt;section aria-roledescription="carousel" aria-label="Featured products"&gt;
      &lt;div className="embla" ref={emblaRef}&gt;
        &lt;div className="embla__container"&gt;
          {slides.map((s, i) =&gt; (
            &lt;div
              key={s.id}
              className="embla__slide"
              role="group"
              aria-roledescription="slide"
              aria-label={`${i + 1} of ${slides.length}`}
            &gt;
              &lt;img
                src={s.url}
                alt={s.alt}
                width={1200}
                height={600}
                loading={i === 0 ? "eager" : "lazy"}
                fetchpriority={i === 0 ? "high" : "auto"}
              /&gt;
              &lt;h2&gt;{s.title}&lt;/h2&gt;
            &lt;/div&gt;
          ))}
        &lt;/div&gt;
      &lt;/div&gt;

      &lt;div className="carousel-controls"&gt;
        &lt;button onClick={() =&gt; emblaApi?.scrollPrev()} aria-label="Previous"&gt;‹&lt;/button&gt;
        &lt;div role="tablist" aria-label="Slide selector"&gt;
          {slides.map((_, i) =&gt; (
            &lt;button
              key={i}
              role="tab"
              aria-selected={i === selected}
              aria-label={`Go to slide ${i + 1}`}
              onClick={() =&gt; emblaApi?.scrollTo(i)}
              className={i === selected ? "active" : ""}
            /&gt;
          ))}
        &lt;/div&gt;
        &lt;button onClick={() =&gt; emblaApi?.scrollNext()} aria-label="Next"&gt;›&lt;/button&gt;
      &lt;/div&gt;
    &lt;/section&gt;
  );
}</code></pre>

<p><strong>Library comparison:</strong></p>

<table>
  <tr><th>Library</th><th>Bundle</th><th>Best for</th></tr>
  <tr><td>Embla Carousel</td><td>~7KB</td><td>Modern, accessible, lightweight; default 2026 pick</td></tr>
  <tr><td>Swiper</td><td>~30KB+</td><td>Feature-rich (3D, parallax, virtual slides); heavier</td></tr>
  <tr><td>Keen Slider</td><td>~5KB</td><td>Tiny, customizable; less ecosystem</td></tr>
  <tr><td>Native CSS scroll-snap</td><td>0KB</td><td>Simple horizontal scroll; no programmatic API</td></tr>
  <tr><td>Splide</td><td>~15KB</td><td>Full-featured; declarative; good a11y</td></tr>
</table>

<p><strong>Native CSS scroll-snap baseline (no JS):</strong></p>

<pre><code>.scroll-carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
}
.scroll-carousel &gt; * {
  flex: 0 0 100%;
  scroll-snap-align: start;
}</code></pre>

<p>Works for content shelves where users just scroll &mdash; no autoplay, no dots needed. Free and bulletproof.</p>

<p><strong>Trade-offs:</strong> Hand-rolled carousels almost always have bugs &mdash; flicker on resize, broken keyboard nav, autoplay that won&rsquo;t pause for screen readers, performance jank during transitions. <strong>Autoplay considerations</strong>: WCAG requires pause/play controls and pausing on hover or focus; never autoplay if there&rsquo;s text content users need to read. Provide a visible pause button. <strong>For hero carousels</strong>, single-slide-per-view + manual nav often beats autoplay (autoplay is criticized by UX research &mdash; users miss content as it slides away). <strong>Mobile-first</strong>: swipe gestures require <code>touch-action: pan-y</code> on the container so vertical scroll still works; Embla/Swiper handle this. <strong>Performance</strong>: lazy-load all but the first slide; use <code>fetchpriority="high"</code> on the first hero image to win the LCP race; preload only when moving toward a slide. <strong>SEO</strong>: all slide content should be in the HTML at render time (don&rsquo;t lazy-mount slides) so crawlers see it.</p>
'''

ANSWERS[81] = r'''
<p><strong>Situation:</strong> A search input needs autocomplete &mdash; as users type, suggestions appear in a dropdown; arrow keys navigate; Enter selects. Suggestions come from an API (with debounce, cancellation, caching) or a local list. Critical use cases: cities, products, users, tags &mdash; the primary search affordance for many apps.</p>

<p><strong>Approach:</strong> Use <strong>Downshift</strong> or <strong>cmdk</strong> for behavior + state machine; pair with TanStack Query for server suggestions. Don&rsquo;t hand-roll &mdash; the keyboard nav, ARIA combobox pattern, and focus management are subtle.</p>

<pre><code>import { useCombobox } from "downshift";
import { useQuery } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";

function ProductAutocomplete({ onSelect }) {
  const [input, setInput] = useState("");
  const [debouncedInput] = useDebounce(input, 250);

  const { data: items = [], isFetching } = useQuery({
    queryKey: ["products", "search", debouncedInput],
    queryFn: ({ signal }) =&gt; fetch(`/api/products?q=${debouncedInput}`, { signal }).then(r =&gt; r.json()),
    enabled: debouncedInput.length &gt;= 2,
    placeholderData: keepPreviousData,
    staleTime: 60_000
  });

  const combobox = useCombobox({
    items,
    inputValue: input,
    onInputValueChange: ({ inputValue }) =&gt; setInput(inputValue),
    onSelectedItemChange: ({ selectedItem }) =&gt; selectedItem &amp;&amp; onSelect(selectedItem),
    itemToString: (item) =&gt; item?.name ?? ""
  });

  return (
    &lt;div className="autocomplete"&gt;
      &lt;div {...combobox.getComboboxProps()}&gt;
        &lt;input
          {...combobox.getInputProps({ placeholder: "Search products..." })}
          aria-busy={isFetching}
        /&gt;
      &lt;/div&gt;
      &lt;ul {...combobox.getMenuProps()} className={combobox.isOpen ? "open" : ""}&gt;
        {combobox.isOpen &amp;&amp; items.map((item, idx) =&gt; (
          &lt;li
            key={item.id}
            {...combobox.getItemProps({ item, index: idx })}
            className={combobox.highlightedIndex === idx ? "highlighted" : ""}
          &gt;
            &lt;Highlight text={item.name} match={input} /&gt;
            &lt;span className="meta"&gt;${item.price}&lt;/span&gt;
          &lt;/li&gt;
        ))}
        {combobox.isOpen &amp;&amp; debouncedInput.length &gt;= 2 &amp;&amp; items.length === 0 &amp;&amp; !isFetching &amp;&amp; (
          &lt;li className="empty"&gt;No results for &ldquo;{debouncedInput}&rdquo;&lt;/li&gt;
        )}
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p>Downshift wires up the <strong>WAI-ARIA combobox</strong> pattern: <code>role="combobox"</code>, <code>aria-expanded</code>, <code>aria-activedescendant</code>, arrow-key navigation, Enter to select, Escape to close. Hand-rolling all of this correctly takes 100+ lines and a week of edge-case fixes.</p>

<p><strong>Library options:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>Downshift</td><td>Behavioral primitive; bring your own UI; superb a11y</td></tr>
  <tr><td>cmdk</td><td>Command palette / autocomplete; designed for keyboard-first UX (Cmd+K)</td></tr>
  <tr><td>Radix Combobox (via shadcn/ui)</td><td>Drop-in autocomplete component with Tailwind styling</td></tr>
  <tr><td>react-select / react-aria</td><td>Heavier but full-featured (multi-select, async, virtualized)</td></tr>
  <tr><td>Algolia InstantSearch + Autocomplete</td><td>When using Algolia anyway; sub-50ms typo-tolerance</td></tr>
</table>

<p><strong>UX details that separate good from great:</strong></p>

<table>
  <tr><th>Detail</th><th>Why</th></tr>
  <tr><td>Highlight matched text</td><td>Users immediately see why a result matched</td></tr>
  <tr><td>Show recent searches when input is empty</td><td>Faster repeat queries</td></tr>
  <tr><td>Group results by category</td><td>"Products" vs "Brands" vs "Help articles"</td></tr>
  <tr><td>Show keyboard shortcut hints</td><td>"↑↓ navigate, Enter to select"</td></tr>
  <tr><td>Loading indicator inside dropdown</td><td>Don&rsquo;t leave users wondering if anything&rsquo;s happening</td></tr>
  <tr><td>Empty state with suggestions</td><td>"No matches. Try [popular term]"</td></tr>
</table>

<p><strong>Trade-offs:</strong> Debounce timing matters &mdash; 250ms is the sweet spot; less wastes API calls, more feels laggy. <strong>Cancellation</strong>: TanStack Query auto-cancels stale queries via the AbortSignal &mdash; without this, slow earlier responses can override fast newer ones (race-condition bug). <strong>Server-side filtering</strong> for &gt;1000 items; client-side for known-small datasets (forms, dropdowns). <strong>For full-text search</strong>: pair with Algolia / Meilisearch / Typesense for typo-tolerance and ranking; raw SQL <code>LIKE</code> queries don&rsquo;t scale beyond a few thousand rows. <strong>Mobile</strong>: virtual keyboards push the dropdown off-screen; use <code>position: fixed</code> for the dropdown on mobile or use a full-screen search overlay (the iOS / Android pattern).</p>
'''

ANSWERS[82] = r'''
<p><strong>Situation:</strong> User data (settings, preferences, profile, drafts) must stay synchronized across the user&rsquo;s devices, multiple browser tabs, and after coming back online from a network drop. Conflicts must be resolved sensibly, not silently lost.</p>

<p><strong>Approach:</strong> Three layers: <strong>(1)</strong> server as source of truth, <strong>(2)</strong> per-device cache with TanStack Query, <strong>(3)</strong> live sync via WebSockets/SSE for active sessions, plus cross-tab sync via BroadcastChannel. For collaborative editing, reach for <strong>Yjs</strong>/<strong>Liveblocks</strong>/<strong>Convex</strong>.</p>

<pre><code>// Layer 1+2: TanStack Query as the device cache
const { data: profile } = useQuery({
  queryKey: ["profile"],
  queryFn: api.getProfile,
  staleTime: 30_000,
  gcTime: 1000 * 60 * 60 * 24,    // keep in cache 24h offline
});

const updateProfile = useMutation({
  mutationFn: api.updateProfile,
  onMutate: async (updates) =&gt; {
    await queryClient.cancelQueries({ queryKey: ["profile"] });
    const previous = queryClient.getQueryData(["profile"]);
    queryClient.setQueryData(["profile"], { ...previous, ...updates });
    return { previous };
  },
  onError: (err, _, ctx) =&gt; queryClient.setQueryData(["profile"], ctx.previous),
  onSuccess: (server) =&gt; {
    queryClient.setQueryData(["profile"], server);   // server-authoritative
    bc.postMessage({ type: "profile-updated", data: server });
  }
});

// Layer 3: cross-tab sync
const bc = new BroadcastChannel("user-data");
useEffect(() =&gt; {
  bc.onmessage = (e) =&gt; {
    if (e.data.type === "profile-updated") {
      queryClient.setQueryData(["profile"], e.data.data);
    }
  };
  return () =&gt; bc.close();
}, []);

// Layer 4: live sync for active session
useEffect(() =&gt; {
  const ws = new WebSocket(`wss://api.example.com/ws?token=${token}`);
  ws.onmessage = (msg) =&gt; {
    const { type, data } = JSON.parse(msg.data);
    if (type === "PROFILE_UPDATED") {
      queryClient.setQueryData(["profile"], data);
    }
  };
  return () =&gt; ws.close();
}, []);</code></pre>

<p><strong>The four sync surfaces:</strong></p>

<table>
  <tr><th>Surface</th><th>Mechanism</th><th>Use for</th></tr>
  <tr><td>Server &harr; current device</td><td>TanStack Query + REST/GraphQL</td><td>All persisted data</td></tr>
  <tr><td>Tab &harr; tab (same browser)</td><td>BroadcastChannel</td><td>Auth state, draft saves, settings</td></tr>
  <tr><td>Device &harr; device (live)</td><td>WebSocket / SSE / Pusher</td><td>Real-time updates, presence</td></tr>
  <tr><td>Offline → online</td><td>Service worker + IndexedDB queue</td><td>PWAs, mobile-like apps</td></tr>
</table>

<p><strong>Conflict resolution strategies:</strong></p>

<table>
  <tr><th>Strategy</th><th>When</th></tr>
  <tr><td>Last-write-wins (server timestamp)</td><td>Default; works for non-conflicting fields</td></tr>
  <tr><td>Field-level merge</td><td>Different fields edited on different devices</td></tr>
  <tr><td>CRDTs (Yjs, Automerge)</td><td>Collaborative editing; multiple concurrent edits</td></tr>
  <tr><td>Optimistic + reject on conflict</td><td>"Sorry, this changed elsewhere &mdash; reload?"</td></tr>
  <tr><td>Manual resolution</td><td>Show diff; user picks (rare; bad UX)</td></tr>
</table>

<p><strong>For collaborative apps</strong>, hand-rolling sync is a multi-quarter project. Reach for:</p>

<table>
  <tr><th>Service</th><th>Best for</th></tr>
  <tr><td>Convex</td><td>Real-time database with reactive queries; React-first</td></tr>
  <tr><td>Liveblocks</td><td>Presence, cursors, comments; pair with Yjs for docs</td></tr>
  <tr><td>Yjs</td><td>CRDT primitive; works offline; pluggable transports</td></tr>
  <tr><td>Supabase Realtime</td><td>Postgres changes streamed to clients</td></tr>
  <tr><td>Replicache / Rocicorp</td><td>Offline-first sync engine; commercial</td></tr>
</table>

<p><strong>Trade-offs:</strong> Most apps don&rsquo;t need full CRDT collaboration &mdash; TanStack Query + WebSocket invalidation gives "near real-time" sync for 95% of use cases at a fraction of the complexity. Reach for CRDTs only when concurrent editing is core to the product (docs, whiteboards, design tools). <strong>Offline support</strong> is a major investment: service worker for asset caching, IndexedDB for data, mutation queue for offline writes, conflict resolution on reconnect, queue retry policy. PWA territory; don&rsquo;t add it casually. <strong>Single-flight refresh</strong>: when WebSocket and a manual refetch both fire, deduplicate (TanStack Query handles this via query keys). <strong>Testing</strong>: simulate offline (DevTools network), multiple tabs, slow networks, mid-flight disconnects &mdash; sync bugs only manifest under these conditions. <strong>Privacy</strong>: don&rsquo;t broadcast user data via BroadcastChannel if other browser users (shared device) might have other tabs; scope by user ID and clear on logout.</p>
'''

ANSWERS[83] = r'''
<p><strong>Situation:</strong> The app uses JWT auth with short-lived access tokens (15 min) and longer-lived refresh tokens. Need to: refresh transparently on access-token expiry, prevent multiple concurrent refreshes, rotate refresh tokens on each use (security), survive page refreshes, and handle refresh-token expiry by forcing re-login.</p>

<p><strong>Approach:</strong> Store access token in memory (or short-lived cookie); refresh token in <strong>httpOnly secure cookie</strong> (never in JS-accessible storage). Use a fetch wrapper that detects 401, refreshes once (single-flight), retries the original request.</p>

<pre><code>// auth/tokenManager.ts — single-flight refresh + queue
let accessToken: string | null = null;
let refreshPromise: Promise&lt;string&gt; | null = null;

export const setAccessToken = (token: string | null) =&gt; { accessToken = token; };
export const getAccessToken = () =&gt; accessToken;

async function refreshAccessToken(): Promise&lt;string&gt; {
  // Refresh token sent automatically via httpOnly cookie
  const res = await fetch("/auth/refresh", {
    method: "POST",
    credentials: "include"
  });
  if (!res.ok) throw new Error("Refresh failed");

  const { accessToken: newToken } = await res.json();
  setAccessToken(newToken);
  return newToken;
}

// Single-flight — concurrent calls share the same in-flight refresh
export async function ensureFreshToken(): Promise&lt;string&gt; {
  if (refreshPromise) return refreshPromise;

  refreshPromise = refreshAccessToken().finally(() =&gt; {
    refreshPromise = null;
  });
  return refreshPromise;
}</code></pre>

<pre><code>// fetch wrapper with auto-refresh
export async function authFetch(url: string, init: RequestInit = {}): Promise&lt;Response&gt; {
  const token = getAccessToken();

  const doFetch = (t: string | null) =&gt;
    fetch(url, {
      ...init,
      headers: {
        ...init.headers,
        ...(t ? { Authorization: `Bearer ${t}` } : {})
      },
      credentials: "include"
    });

  let res = await doFetch(token);

  if (res.status === 401 &amp;&amp; token) {
    try {
      const newToken = await ensureFreshToken();
      res = await doFetch(newToken);              // retry original request
    } catch {
      logoutAndRedirect("expired");
      throw new Error("Session expired");
    }
  }

  return res;
}</code></pre>

<p><strong>App startup &mdash; restore session:</strong></p>

<pre><code>// On app load, try to refresh — if cookie still valid, get fresh access token
useEffect(() =&gt; {
  ensureFreshToken()
    .then(() =&gt; setStatus("authenticated"))
    .catch(() =&gt; setStatus("unauthenticated"));
}, []);

// Periodic refresh (slightly before expiry)
useEffect(() =&gt; {
  const interval = setInterval(() =&gt; {
    ensureFreshToken().catch(() =&gt; logoutAndRedirect("expired"));
  }, 13 * 60 * 1000);   // 13 min for 15-min tokens
  return () =&gt; clearInterval(interval);
}, []);</code></pre>

<p><strong>Refresh-token rotation</strong> (security best practice): each refresh issues a new refresh token; the old one is invalidated server-side. Detection of an old refresh token being reused indicates token theft &mdash; revoke the entire family and force re-auth.</p>

<p><strong>Token storage trade-offs:</strong></p>

<table>
  <tr><th>Storage</th><th>Refresh token</th><th>Access token</th></tr>
  <tr><td>httpOnly cookie</td><td>✅ Best — JS can&rsquo;t read; CSRF mitigated by SameSite=Strict</td><td>OK if same-site only</td></tr>
  <tr><td>localStorage</td><td>✗ XSS exfiltrates it; persistent</td><td>✗ Same risk</td></tr>
  <tr><td>sessionStorage</td><td>✗ Same XSS risk; lost on close</td><td>✗ Same risk</td></tr>
  <tr><td>Memory only</td><td>Lost on refresh — bad for refresh tokens</td><td>✅ Best — XSS-resistant; lost on refresh OK</td></tr>
</table>

<p><strong>Trade-offs:</strong> The httpOnly cookie + in-memory access token combo is the modern standard for SPA auth &mdash; it&rsquo;s the only configuration that resists both XSS and CSRF. Same-site cookies and CORS configuration must be correct (frontend and API on same registrable domain or use proper CORS + credentials). <strong>Single-flight refresh is critical</strong>: without it, 5 concurrent failing requests trigger 5 refresh calls, racing each other &mdash; one succeeds, the others see 401 and chain-fail; some refresh tokens are consumed and invalidated mid-flight. The promise-cache pattern above prevents this. <strong>Don&rsquo;t pre-emptively refresh on every request</strong> &mdash; doubles API traffic; instead, react to 401 OR refresh on a timer slightly before expiry. <strong>Logout</strong> must clear access token in memory AND call <code>/auth/logout</code> to invalidate refresh token server-side AND broadcast to other tabs. <strong>Modern alternatives</strong>: services like Clerk, Auth0, Supabase Auth, NextAuth.js handle all of this correctly out of the box &mdash; reach for them rather than rolling your own JWT handling unless you have specific reasons.</p>
'''

ANSWERS[84] = r'''
<p><strong>Situation:</strong> A page needs to fire several API requests &mdash; user profile, dashboard stats, recent activity, notifications &mdash; concurrently rather than sequentially. Some depend on others; some can fail without breaking the page; total page wait should equal the slowest request, not the sum.</p>

<p><strong>Approach:</strong> TanStack Query handles this elegantly &mdash; multiple <code>useQuery</code> calls in one component fire in parallel automatically. For dependent queries, use <code>enabled</code>. For waterfalls, use <code>useQueries</code>. For "succeed if any one succeeds" patterns, use <code>Promise.allSettled</code>.</p>

<pre><code>// Pattern 1: Independent parallel queries — TanStack Query
function Dashboard() {
  const profile = useQuery({ queryKey: ["profile"], queryFn: api.getProfile });
  const stats = useQuery({ queryKey: ["stats"], queryFn: api.getStats });
  const activity = useQuery({ queryKey: ["activity"], queryFn: api.getActivity });
  const notifications = useQuery({ queryKey: ["notifications"], queryFn: api.getNotifications });

  // All four fire in parallel; each renders independently
  // Total wait = max(t_profile, t_stats, t_activity, t_notifications)

  return (
    &lt;&gt;
      {profile.isLoading ? &lt;Skeleton /&gt; : &lt;ProfileCard data={profile.data} /&gt;}
      {stats.isLoading ? &lt;Skeleton /&gt; : &lt;StatsCard data={stats.data} /&gt;}
      {activity.isLoading ? &lt;Skeleton /&gt; : &lt;ActivityFeed data={activity.data} /&gt;}
      {notifications.isLoading ? &lt;Skeleton /&gt; : &lt;NotificationBell data={notifications.data} /&gt;}
    &lt;/&gt;
  );
}</code></pre>

<pre><code>// Pattern 2: Dependent queries — wait for one before firing the next
function UserOrders() {
  const { data: user } = useQuery({ queryKey: ["user"], queryFn: api.getUser });
  const { data: orders } = useQuery({
    queryKey: ["orders", user?.id],
    queryFn: () =&gt; api.getOrders(user.id),
    enabled: !!user?.id    // only fires once user loads
  });
  return ...;
}</code></pre>

<pre><code>// Pattern 3: Dynamic list of parallel queries
function ProductGrid({ productIds }) {
  const queries = useQueries({
    queries: productIds.map((id) =&gt; ({
      queryKey: ["product", id],
      queryFn: () =&gt; api.getProduct(id),
      staleTime: 60_000
    }))
  });

  const allLoaded = queries.every((q) =&gt; q.isSuccess);
  // Or render progressively as each resolves
}</code></pre>

<pre><code>// Pattern 4: Raw promises — Promise.all vs allSettled
async function loadDashboardData() {
  // Promise.all — fails fast if any fails
  const [profile, stats] = await Promise.all([
    api.getProfile(),
    api.getStats()
  ]);

  // Promise.allSettled — succeed individually
  const results = await Promise.allSettled([
    api.getProfile(),
    api.getStats(),
    api.getActivity()
  ]);
  results.forEach((r) =&gt; {
    if (r.status === "fulfilled") use(r.value);
    else logError(r.reason);
  });
}</code></pre>

<p><strong>Decision matrix:</strong></p>

<table>
  <tr><th>Scenario</th><th>Pattern</th></tr>
  <tr><td>Multiple independent fetches</td><td>Multiple <code>useQuery</code> (parallel automatically)</td></tr>
  <tr><td>B depends on A&rsquo;s result</td><td><code>useQuery</code> with <code>enabled: !!a.data</code></td></tr>
  <tr><td>N parallel fetches (dynamic list)</td><td><code>useQueries</code></td></tr>
  <tr><td>Wait for all, fail-fast</td><td><code>Promise.all</code></td></tr>
  <tr><td>Wait for all, partial OK</td><td><code>Promise.allSettled</code></td></tr>
  <tr><td>Race for fastest</td><td><code>Promise.race</code> (rarely useful)</td></tr>
  <tr><td>SSR / preload before render</td><td>React Router loaders / Next.js Server Components</td></tr>
</table>

<p><strong>React Router data loaders &mdash; parallel by route segment:</strong></p>

<pre><code>{
  path: "/dashboard",
  loader: async () =&gt; {
    const [profile, stats, activity] = await Promise.all([
      api.getProfile(),
      api.getStats(),
      api.getActivity()
    ]);
    return { profile, stats, activity };
  }
}</code></pre>

<p>Loader runs once before page render &mdash; eliminates loading spinners for primary data; React Router waits for all and renders the full tree.</p>

<p><strong>Trade-offs:</strong> The biggest mistake is sequential awaits &mdash; <code>await api.a(); await api.b()</code> serializes them. Use <code>Promise.all</code> when fetches are independent. <strong>Concurrency limits</strong>: firing 200 parallel API calls overwhelms the server (and exhausts browser connection pool &mdash; usually 6 per origin). Use a queue with concurrency limit (libraries like <code>p-limit</code>) for batch operations. <strong>Cancellation</strong>: TanStack Query auto-cancels stale queries via AbortSignal &mdash; without this, "rapid type then click result" races can show stale data. <strong>Error UX</strong>: with parallel queries, decide upfront which failures break the whole page (must-have data) vs which are best-effort (notifications, recommendations). Best-effort failures should silently render fallback or empty state &mdash; don&rsquo;t crash the whole dashboard if recommendations API is down. <strong>Streaming SSR with Suspense</strong> (Next.js): kick off all data fetches; stream HTML as each resolves; users see the fastest sections immediately while slow ones spinner-load. The right pattern for fast-first-paint with multi-source pages.</p>
'''

ANSWERS[85] = r'''
<p><strong>Situation:</strong> Form needs a tag input &mdash; users type tags separated by Enter/comma, see them as removable chips, can navigate with arrow keys, paste comma-separated lists, and have inputs validated/de-duplicated. Examples: email recipients, post tags, skills, recipients.</p>

<p><strong>Approach:</strong> Build on top of <strong>react-tag-input-component</strong>, <strong>cmdk</strong> (for tag-with-suggestions), or hand-roll for full control. The pattern: array of tag strings + uncommitted draft input + keyboard handlers.</p>

<pre><code>function TagInput({ value = [], onChange, suggestions = [], maxTags, placeholder, validate }) {
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const addTag = (raw) =&gt; {
    const trimmed = raw.trim();
    if (!trimmed) return;
    if (value.includes(trimmed)) { setError("Duplicate tag"); return; }
    if (maxTags &amp;&amp; value.length &gt;= maxTags) { setError(`Max ${maxTags} tags`); return; }

    const validation = validate?.(trimmed);
    if (validation) { setError(validation); return; }

    onChange([...value, trimmed]);
    setDraft("");
    setError("");
  };

  const removeTag = (idx) =&gt; onChange(value.filter((_, i) =&gt; i !== idx));

  const handleKeyDown = (e) =&gt; {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(draft);
    } else if (e.key === "Backspace" &amp;&amp; !draft &amp;&amp; value.length) {
      // Backspace on empty input removes last tag
      removeTag(value.length - 1);
    }
  };

  const handlePaste = (e) =&gt; {
    const text = e.clipboardData.getData("text");
    if (text.includes(",") || text.includes("\n")) {
      e.preventDefault();
      text.split(/[,\n]/).forEach(addTag);
    }
  };

  return (
    &lt;div className="tag-input" onClick={() =&gt; inputRef.current?.focus()}&gt;
      {value.map((tag, i) =&gt; (
        &lt;span key={`${tag}-${i}`} className="tag"&gt;
          {tag}
          &lt;button
            type="button"
            onClick={() =&gt; removeTag(i)}
            aria-label={`Remove ${tag}`}
          &gt;
            ✕
          &lt;/button&gt;
        &lt;/span&gt;
      ))}
      &lt;input
        ref={inputRef}
        value={draft}
        onChange={(e) =&gt; { setDraft(e.target.value); setError(""); }}
        onKeyDown={handleKeyDown}
        onPaste={handlePaste}
        onBlur={() =&gt; addTag(draft)}
        placeholder={value.length === 0 ? placeholder : ""}
        aria-invalid={!!error}
        aria-describedby={error ? "tag-error" : undefined}
      /&gt;
      {error &amp;&amp; &lt;p id="tag-error" role="alert"&gt;{error}&lt;/p&gt;}
    &lt;/div&gt;
  );
}

// Usage
&lt;TagInput
  value={tags}
  onChange={setTags}
  maxTags={10}
  placeholder="Add tags..."
  validate={(t) =&gt; t.length &lt; 2 ? "Min 2 characters" : null}
/&gt;</code></pre>

<p><strong>With autocomplete suggestions:</strong></p>

<pre><code>// Wrap with cmdk or Downshift for typeahead
const matching = suggestions.filter(
  (s) =&gt; s.toLowerCase().includes(draft.toLowerCase()) &amp;&amp; !value.includes(s)
);

{showSuggestions &amp;&amp; matching.length &gt; 0 &amp;&amp; (
  &lt;ul role="listbox"&gt;
    {matching.map((s) =&gt; (
      &lt;li key={s} onClick={() =&gt; addTag(s)}&gt;{s}&lt;/li&gt;
    ))}
  &lt;/ul&gt;
)}</code></pre>

<p><strong>UX details that matter:</strong></p>

<table>
  <tr><th>Feature</th><th>Why</th></tr>
  <tr><td>Backspace removes last tag</td><td>Familiar from Gmail, Slack, all major apps</td></tr>
  <tr><td>Comma + Enter both commit</td><td>Different muscle memory; both are expected</td></tr>
  <tr><td>Paste with delimiters</td><td>Pasting "a, b, c" should make 3 tags, not 1</td></tr>
  <tr><td>Blur commits unfinished input</td><td>Prevents losing typed-but-not-Entered tag</td></tr>
  <tr><td>Click anywhere → focus input</td><td>Larger hit target than just the input</td></tr>
  <tr><td>Per-tag remove button</td><td>Required for mouse-only users</td></tr>
  <tr><td>Visual error feedback</td><td>Duplicate / invalid / max-reached</td></tr>
  <tr><td>Arrow-left into tags</td><td>Advanced; lets keyboard users edit/delete specific tags</td></tr>
</table>

<p><strong>Library options:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>react-tag-input-component</td><td>Simple, drop-in tag input</td></tr>
  <tr><td>react-select (with creatable)</td><td>Tags + autocomplete from large set</td></tr>
  <tr><td>cmdk + custom UI</td><td>Modern, keyboard-first, with suggestions</td></tr>
  <tr><td>react-aria TagGroup</td><td>Adobe&rsquo;s a11y-first primitives</td></tr>
</table>

<p><strong>Trade-offs:</strong> The pattern is straightforward, but a11y is easy to break: tag list should announce as a list (<code>role="list"</code> implicit on ul/li); each remove button needs an accessible label including the tag value; the live region for errors needs <code>role="alert"</code> or <code>aria-live="polite"</code>. <strong>Validation strategy</strong>: client-side for format (email regex, length); server-side for uniqueness or constraints (already-used tags in the system). <strong>Performance</strong>: tags shouldn&rsquo;t use array index as key when reorderable &mdash; if the same tag string can repeat, use a synthetic ID. <strong>Mobile</strong>: virtual keyboards behave oddly with chips; ensure tap targets are ≥44px; consider a "Done" button or full-screen tag editor on small screens. <strong>Multi-line wrap</strong>: tags should wrap to multiple lines as they fill the row; flexbox + <code>flex-wrap: wrap</code> handles this naturally.</p>
'''

ANSWERS[86] = r'''
<p><strong>Situation:</strong> Forms, modals, and wizard steps need correct focus behavior &mdash; first input focused on mount, focus trapped inside modals, focus returned to trigger on close, error fields focused on submission failure, and skip-to-content links for keyboard users. Bad focus management is the most common a11y failure.</p>

<p><strong>Approach:</strong> Use <strong>react-aria</strong>, <strong>focus-trap-react</strong>, or <strong>Radix UI</strong> primitives for production-grade focus handling. Hand-rolled focus is full of edge cases. For form errors, manage focus imperatively after submit.</p>

<pre><code>// Pattern 1: Auto-focus first input on mount
function CheckoutForm() {
  const firstInputRef = useRef(null);
  useEffect(() =&gt; { firstInputRef.current?.focus(); }, []);

  return (
    &lt;form&gt;
      &lt;input ref={firstInputRef} name="email" /&gt;
      &lt;input name="password" /&gt;
    &lt;/form&gt;
  );
}

// Pattern 2: Focus first error after failed submit
const { register, handleSubmit, formState: { errors }, setFocus } = useForm();

const onSubmit = async (data) =&gt; {
  try { await api.save(data); }
  catch (err) {
    if (err.field) setFocus(err.field);   // server-side validation field
  }
};

const onError = (errors) =&gt; {
  const firstError = Object.keys(errors)[0];
  if (firstError) setFocus(firstError);   // first client-side error
};

&lt;form onSubmit={handleSubmit(onSubmit, onError)}&gt;...&lt;/form&gt;</code></pre>

<pre><code>// Pattern 3: Focus trap in modal — Radix handles this automatically
import * as Dialog from "@radix-ui/react-dialog";

&lt;Dialog.Root&gt;
  &lt;Dialog.Trigger&gt;Open&lt;/Dialog.Trigger&gt;
  &lt;Dialog.Portal&gt;
    &lt;Dialog.Overlay /&gt;
    &lt;Dialog.Content&gt;
      {/* Focus trapped here, returned to trigger on close */}
      &lt;Dialog.Title&gt;Confirm action&lt;/Dialog.Title&gt;
      &lt;input autoFocus /&gt;
      &lt;Dialog.Close&gt;Cancel&lt;/Dialog.Close&gt;
    &lt;/Dialog.Content&gt;
  &lt;/Dialog.Portal&gt;
&lt;/Dialog.Root&gt;</code></pre>

<pre><code>// Pattern 4: Focus management in wizards — focus heading on step change
function WizardStep({ step }) {
  const headingRef = useRef(null);
  useEffect(() =&gt; {
    headingRef.current?.focus();   // announce new step to screen readers
  }, [step]);

  return (
    &lt;section&gt;
      &lt;h2 ref={headingRef} tabIndex={-1}&gt;Step {step}&lt;/h2&gt;
      ...
    &lt;/section&gt;
  );
}</code></pre>

<p><strong>Focus management checklist:</strong></p>

<table>
  <tr><th>Scenario</th><th>Required behavior</th></tr>
  <tr><td>Modal opens</td><td>Focus moves into modal; trap inside; restore to trigger on close</td></tr>
  <tr><td>Form submit fails</td><td>Focus first error field; announce to AT</td></tr>
  <tr><td>Tab change / step change</td><td>Focus the new heading or first focusable element</td></tr>
  <tr><td>Item deleted from list</td><td>Focus next item, or previous if last, or list itself</td></tr>
  <tr><td>Page navigation (SPA)</td><td>Focus main heading or skip link</td></tr>
  <tr><td>Inline error appears</td><td>Associate via <code>aria-describedby</code>; don&rsquo;t steal focus</td></tr>
  <tr><td>Async operation completes</td><td><code>aria-live</code> region announces; don&rsquo;t move focus mid-action</td></tr>
</table>

<p><strong>SPA navigation focus &mdash; commonly overlooked:</strong></p>

<pre><code>// Focus h1 of new page on route change (otherwise screen-reader users miss the navigation)
function PageContainer({ children }) {
  const headingRef = useRef(null);
  const location = useLocation();

  useEffect(() =&gt; {
    headingRef.current?.focus();
    // optional: also announce route name via aria-live region
  }, [location.pathname]);

  return (
    &lt;main&gt;
      &lt;h1 ref={headingRef} tabIndex={-1}&gt;{children.props.title}&lt;/h1&gt;
      {children}
    &lt;/main&gt;
  );
}</code></pre>

<p><strong>Common pitfalls:</strong></p>

<table>
  <tr><th>Pitfall</th><th>Fix</th></tr>
  <tr><td>Focus stuck in closed modal (focus trap not removed)</td><td>Use library; cleanup in useEffect return</td></tr>
  <tr><td>Click-only handlers (no keyboard)</td><td>Use <code>&lt;button&gt;</code> not <code>&lt;div onClick&gt;</code></td></tr>
  <tr><td>Custom widgets without keyboard support</td><td>Add <code>onKeyDown</code> for Enter/Space; tabIndex</td></tr>
  <tr><td>Hidden focusable elements</td><td><code>display: none</code> hides; <code>visibility: hidden</code> hides; <code>aria-hidden=true</code> doesn&rsquo;t prevent focus &mdash; combine with tabIndex=-1 or hide them</td></tr>
  <tr><td>Focus outline removed globally</td><td>Use <code>:focus-visible</code> for keyboard-only outlines</td></tr>
  <tr><td>Auto-focus on every render</td><td>Use empty-array deps so it runs once on mount</td></tr>
</table>

<p><strong>Trade-offs:</strong> Reach for libraries: <strong>Radix UI</strong> primitives, <strong>react-aria</strong> hooks, or <strong>focus-trap-react</strong> handle the dozen subtle cases hand-rolled implementations get wrong. <strong>Don&rsquo;t fight the browser</strong>: the browser&rsquo;s focus order is correct for most cases; intervene only when the natural order breaks UX (e.g., modal portal&rsquo;d outside the trigger). <strong>Test with keyboard only</strong>: Tab through every interactive element on every page; the worst a11y bugs are invisible until you stop using a mouse. <strong>Screen reader testing</strong>: NVDA (Windows, free) or VoiceOver (Mac built-in) reveal whether focus changes are announced or silent &mdash; many "focused but silent" failures aren&rsquo;t visible until tested with AT. <strong>Don&rsquo;t use autoFocus on every page</strong>: it can confuse users on landing pages and break browser back-button restoration of scroll position.</p>
'''

ANSWERS[87] = r'''
<p><strong>Situation:</strong> The frontend must rate-limit outbound API calls &mdash; protect against accidental loops, respect server limits (e.g., 100 req/min), space out batch operations, and queue overflow rather than firing 1000 requests at once.</p>

<p><strong>Approach:</strong> Use a client-side <strong>token bucket</strong> or <strong>p-limit</strong> for concurrency control. Combine with HTTP-level retry-after handling. Don&rsquo;t reinvent rate-limiting algorithms &mdash; battle-tested libraries handle the edge cases.</p>

<pre><code>// Approach 1: Concurrency limiting with p-limit
import pLimit from "p-limit";

const limit = pLimit(5);   // max 5 concurrent requests

async function fetchAllProducts(ids) {
  const tasks = ids.map((id) =&gt; limit(() =&gt; api.getProduct(id)));
  return Promise.all(tasks);   // total throughput capped at 5 concurrent
}</code></pre>

<pre><code>// Approach 2: Rate limiter — N requests per window
class RateLimiter {
  constructor(maxRequests, windowMs) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.timestamps = [];
    this.queue = [];
  }

  async acquire() {
    return new Promise((resolve) =&gt; {
      this.queue.push(resolve);
      this.process();
    });
  }

  process() {
    const now = Date.now();
    // Drop timestamps outside the window
    this.timestamps = this.timestamps.filter((t) =&gt; now - t &lt; this.windowMs);

    while (this.queue.length &amp;&amp; this.timestamps.length &lt; this.maxRequests) {
      this.timestamps.push(now);
      this.queue.shift()();
    }

    if (this.queue.length) {
      const oldest = this.timestamps[0];
      const wait = this.windowMs - (now - oldest);
      setTimeout(() =&gt; this.process(), wait);
    }
  }
}

const limiter = new RateLimiter(60, 60_000);   // 60/min

async function rateLimitedFetch(url, opts) {
  await limiter.acquire();
  return fetch(url, opts);
}</code></pre>

<pre><code>// Approach 3: Respect server rate-limit headers (HTTP standard)
async function smartFetch(url, opts, retries = 3) {
  const res = await fetch(url, opts);

  if (res.status === 429 &amp;&amp; retries &gt; 0) {
    const retryAfter = parseInt(res.headers.get("Retry-After") || "1", 10);
    await new Promise((r) =&gt; setTimeout(r, retryAfter * 1000));
    return smartFetch(url, opts, retries - 1);
  }

  // Track remaining quota
  const remaining = parseInt(res.headers.get("X-RateLimit-Remaining") || "999", 10);
  const reset = parseInt(res.headers.get("X-RateLimit-Reset") || "0", 10);
  if (remaining &lt; 5) {
    console.warn(`Rate limit nearly exhausted; resets at ${new Date(reset * 1000)}`);
  }

  return res;
}</code></pre>

<p><strong>Algorithm comparison:</strong></p>

<table>
  <tr><th>Algorithm</th><th>Behavior</th><th>Use when</th></tr>
  <tr><td>Concurrency limit (semaphore)</td><td>Max N in-flight; queue extras</td><td>Long-running uploads; protect connection pool</td></tr>
  <tr><td>Fixed window</td><td>N per minute; window resets at boundary</td><td>Simple, but burst at boundary</td></tr>
  <tr><td>Sliding window</td><td>N per rolling 60s</td><td>Smoother; what most APIs implement server-side</td></tr>
  <tr><td>Token bucket</td><td>Tokens refill at rate R; spend per request</td><td>Allow short bursts; smooth average</td></tr>
  <tr><td>Leaky bucket</td><td>Constant outflow rate; no bursts</td><td>Strict pacing</td></tr>
  <tr><td>Debounce / throttle</td><td>Per-event; not for arbitrary calls</td><td>UI-driven (search, scroll)</td></tr>
</table>

<p><strong>TanStack Query interplay</strong>: it dedupes identical concurrent queries (one network request even if 10 components ask) &mdash; many "rate-limit" problems are actually duplicate-fetch problems that disappear with proper caching.</p>

<p><strong>Library options:</strong></p>

<table>
  <tr><th>Library</th><th>Use</th></tr>
  <tr><td>p-limit</td><td>Concurrency cap; tiny, well-tested</td></tr>
  <tr><td>p-queue</td><td>Concurrency + rate per second + priority</td></tr>
  <tr><td>bottleneck</td><td>Full-featured: rate, concurrency, priority, reservoirs</td></tr>
  <tr><td>axios-rate-limit</td><td>Drop-in axios wrapper with rate limits</td></tr>
</table>

<p><strong>Trade-offs:</strong> Frontend rate limiting is a <em>good citizen</em> measure, not a security boundary &mdash; the server must still enforce its own limits, since a malicious client can disable rate limiting. <strong>Bursty vs smooth</strong>: token bucket allows occasional bursts (good UX for normal use); leaky bucket pre-paces requests (predictable load). <strong>Queue overflow</strong>: if 10,000 items queue up, memory pressure and stale requests become problems. Cap queue size; reject or notify when exceeded. <strong>Cancellation</strong>: when components unmount, abort in-flight requests via AbortController; otherwise rate-limited queues hold references to dead components. <strong>Server-driven backoff</strong>: respect <code>Retry-After</code> header on 429s (HTTP standard); honor <code>X-RateLimit-*</code> headers to slow proactively before hitting the limit. <strong>Don&rsquo;t over-engineer</strong>: most apps need at most concurrency limit + 429 retry; full token-bucket libraries are appropriate for batch operations and admin-tool bulk actions.</p>
'''

ANSWERS[88] = r'''
<p><strong>Situation:</strong> Components subscribe to events, set timers, open WebSockets, attach DOM listeners, fire fetches. Without proper cleanup, unmounted components leak memory, run setState on dead components ("Can&rsquo;t perform a React state update on an unmounted component"), and produce double-handlers in development with Strict Mode.</p>

<p><strong>Approach:</strong> Every <code>useEffect</code> that creates a subscription, timer, listener, or in-flight async operation MUST return a cleanup function. The cleanup runs before the next effect (or on unmount). Strict Mode in dev double-invokes effects to surface missing cleanups.</p>

<pre><code>// Timer cleanup
useEffect(() =&gt; {
  const id = setInterval(() =&gt; tick(), 1000);
  return () =&gt; clearInterval(id);
}, []);

// Event listener cleanup
useEffect(() =&gt; {
  const onResize = () =&gt; setSize(window.innerWidth);
  window.addEventListener("resize", onResize);
  return () =&gt; window.removeEventListener("resize", onResize);
}, []);

// Subscription cleanup
useEffect(() =&gt; {
  const unsubscribe = chatStore.subscribe(setMessages);
  return () =&gt; unsubscribe();
}, []);

// WebSocket cleanup
useEffect(() =&gt; {
  const ws = new WebSocket(url);
  ws.onmessage = (e) =&gt; handleMessage(e);
  return () =&gt; ws.close();
}, [url]);

// IntersectionObserver cleanup
useEffect(() =&gt; {
  const observer = new IntersectionObserver(callback, options);
  if (ref.current) observer.observe(ref.current);
  return () =&gt; observer.disconnect();
}, []);</code></pre>

<p><strong>The async fetch problem &mdash; ignore-flag pattern:</strong></p>

<pre><code>useEffect(() =&gt; {
  let cancelled = false;

  fetchData(id).then((data) =&gt; {
    if (cancelled) return;       // skip setState on unmounted component
    setData(data);
  });

  return () =&gt; { cancelled = true; };
}, [id]);

// Better: AbortController — actually cancels the request
useEffect(() =&gt; {
  const controller = new AbortController();

  fetch(`/api/items/${id}`, { signal: controller.signal })
    .then((r) =&gt; r.json())
    .then(setData)
    .catch((err) =&gt; {
      if (err.name !== "AbortError") setError(err);
    });

  return () =&gt; controller.abort();
}, [id]);</code></pre>

<p><strong>What needs cleanup:</strong></p>

<table>
  <tr><th>Side effect</th><th>Cleanup</th></tr>
  <tr><td>setTimeout / setInterval</td><td>clearTimeout / clearInterval</td></tr>
  <tr><td>addEventListener</td><td>removeEventListener (same function reference)</td></tr>
  <tr><td>WebSocket / EventSource</td><td>close()</td></tr>
  <tr><td>IntersectionObserver / MutationObserver</td><td>disconnect()</td></tr>
  <tr><td>Subscription (RxJS, store, pubsub)</td><td>Call unsubscribe</td></tr>
  <tr><td>Pending fetch</td><td>AbortController.abort()</td></tr>
  <tr><td>Animation frame</td><td>cancelAnimationFrame</td></tr>
  <tr><td>Third-party widget</td><td>Library-specific destroy()</td></tr>
  <tr><td>requestIdleCallback</td><td>cancelIdleCallback</td></tr>
  <tr><td>Geolocation watch</td><td>navigator.geolocation.clearWatch</td></tr>
</table>

<p><strong>Strict Mode double-invocation</strong>:</p>

<pre><code>// In Strict Mode (dev), this runs:
// 1. setup → cleanup → setup
// To surface missing cleanups: if you forget to clear, you get duplicates.

useEffect(() =&gt; {
  const id = setInterval(tick, 1000);   // creates timer
  return () =&gt; clearInterval(id);       // ✅ cleared on each rerun
}, []);

// Without cleanup:
useEffect(() =&gt; {
  setInterval(tick, 1000);   // ✗ Strict Mode creates 2 timers; production creates 1 leak per remount
}, []);</code></pre>

<p><strong>Common cleanup bugs:</strong></p>

<table>
  <tr><th>Bug</th><th>Fix</th></tr>
  <tr><td>removeEventListener with different fn reference</td><td>Define handler in effect; reference same fn</td></tr>
  <tr><td>Cleanup uses stale closure</td><td>Use refs for current values inside cleanup</td></tr>
  <tr><td>Async cleanup (await in cleanup fn)</td><td>Cleanup must be sync; chain with then() if needed</td></tr>
  <tr><td>Forgetting cleanup on conditional setup</td><td>Setup creates resource → cleanup must release it</td></tr>
  <tr><td>useEffect with no array → effect every render</td><td>Add deps array; cleanup runs on each rerun</td></tr>
</table>

<p><strong>Trade-offs:</strong> The mental model: <em>"every effect that opens something must close it"</em>. The cleanup function runs in two cases &mdash; before the next effect run (deps changed) AND on unmount. This unification is what makes the pattern work elegantly. <strong>useRef for cleanup-time values</strong>: cleanup closures capture values at setup time; if the cleanup needs the latest value (e.g., notifying the server with the current user ID), use a ref that&rsquo;s updated each render. <strong>Class components</strong> required <code>componentWillUnmount</code> for cleanup &mdash; with hooks, setup and cleanup co-locate, eliminating the "set up here, clean up there" desynchronization that caused most class-component leaks. <strong>TanStack Query</strong> handles cleanup automatically &mdash; it cancels in-flight queries when components unmount, and removes data from cache on a configurable schedule (gcTime). For most data fetching, you don&rsquo;t write cleanup at all. <strong>For native/RN</strong>: AppState changes (background/foreground) need explicit cleanup of timers and connections that shouldn&rsquo;t run when the app is backgrounded.</p>
'''

ANSWERS[89] = r'''
<p><strong>Situation:</strong> Multiple components fetch data with similar patterns &mdash; loading states, errors, refetching, caching, request cancellation. Without abstraction, each component duplicates 30+ lines of fetching boilerplate. Need a reusable hook that captures the pattern.</p>

<p><strong>Approach:</strong> In 2026, <strong>don&rsquo;t roll your own &mdash; use TanStack Query</strong>. It is the API hook. Hand-rolling for learning is fine; using it in production reinvents a battle-tested wheel. Build domain-specific hooks <em>on top of</em> TanStack Query.</p>

<pre><code>// Domain-specific hook layered on TanStack Query
export function useUser(userId: string | undefined) {
  return useQuery({
    queryKey: ["user", userId],
    queryFn: () =&gt; api.getUser(userId!),
    enabled: !!userId,
    staleTime: 1000 * 60 * 5,   // 5 min
    select: (data) =&gt; ({ ...data, fullName: `${data.first} ${data.last}` })
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updates: Partial&lt;User&gt;) =&gt; api.updateUser(updates),
    onSuccess: (updated) =&gt; {
      queryClient.setQueryData(["user", updated.id], updated);
      queryClient.invalidateQueries({ queryKey: ["users"] });
    }
  });
}

// Usage — clean, declarative
function ProfilePage({ userId }) {
  const { data: user, isLoading, error } = useUser(userId);
  const updateUser = useUpdateUser();

  if (isLoading) return &lt;Skeleton /&gt;;
  if (error) return &lt;ErrorState error={error} /&gt;;

  return (
    &lt;form onSubmit={(e) =&gt; updateUser.mutate({ name: e.target.name.value })}&gt;
      ...
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Hand-rolled version &mdash; for understanding the pattern:</strong></p>

<pre><code>function useFetch&lt;T&gt;(url: string | null) {
  const [data, setData] = useState&lt;T | null&gt;(null);
  const [error, setError] = useState&lt;Error | null&gt;(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() =&gt; {
    if (!url) return;

    let cancelled = false;
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);

    fetch(url, { signal: controller.signal })
      .then((r) =&gt; { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then((json) =&gt; { if (!cancelled) setData(json); })
      .catch((err) =&gt; {
        if (cancelled || err.name === "AbortError") return;
        setError(err);
      })
      .finally(() =&gt; { if (!cancelled) setIsLoading(false); });

    return () =&gt; { cancelled = true; controller.abort(); };
  }, [url]);

  return { data, error, isLoading };
}</code></pre>

<p>This works for one component but lacks: caching across components, deduplication of identical concurrent requests, background refetch on window focus, retry on failure, mutations + optimistic updates, infinite queries, prefetching, devtools. TanStack Query gives all of those.</p>

<p><strong>What TanStack Query handles automatically:</strong></p>

<table>
  <tr><th>Capability</th><th>Without it</th></tr>
  <tr><td>Cross-component cache</td><td>Each component refetches the same data</td></tr>
  <tr><td>Request deduplication</td><td>10 components asking for the same query → 10 requests</td></tr>
  <tr><td>Background refetch</td><td>Stale data shown until manual refetch</td></tr>
  <tr><td>Retry with backoff</td><td>One transient error → broken UI</td></tr>
  <tr><td>Optimistic updates</td><td>UI lags behind user action</td></tr>
  <tr><td>Cache invalidation</td><td>After mutation, manually refetch every dependent</td></tr>
  <tr><td>Cancellation on unmount</td><td>setState-on-unmounted-component warnings</td></tr>
  <tr><td>Devtools</td><td>console.log debugging only</td></tr>
  <tr><td>Persistence</td><td>Hand-roll localStorage sync</td></tr>
</table>

<p><strong>Library comparison:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>TanStack Query</td><td>2026 default; framework-agnostic; excellent DX</td></tr>
  <tr><td>SWR</td><td>Simpler API; from Vercel; good for Next.js</td></tr>
  <tr><td>RTK Query</td><td>If already using Redux Toolkit; auto-generates hooks from API endpoints</td></tr>
  <tr><td>Apollo Client</td><td>GraphQL apps; cache normalization</td></tr>
  <tr><td>urql</td><td>GraphQL alternative; lighter</td></tr>
  <tr><td>Convex / Liveblocks / Supabase</td><td>Reactive backend with auto-sync</td></tr>
</table>

<p><strong>Trade-offs:</strong> Building data-fetching hooks from <code>useEffect</code> + <code>fetch</code> seems simple but rapidly accumulates complexity: cancellation, race conditions (slow earlier requests overriding fast later ones), cache, error handling, retry, refetch on focus, dependent queries. By the time you&rsquo;ve handled all cases, you&rsquo;ve recreated a worse version of TanStack Query. <strong>The wrapper layer matters</strong>: even with TanStack Query, encapsulate domain hooks (<code>useUser</code>, <code>useProducts</code>) so query keys, fetcher functions, and select transforms are centralized &mdash; components shouldn&rsquo;t know <code>queryKey</code> conventions. <strong>Server Components in Next.js</strong> often eliminate the need for client-side fetch hooks entirely &mdash; fetch in the component itself, no <code>useQuery</code>, no loading state. Use TanStack Query for client-side interactive data; Server Components for initial render data.</p>
'''

ANSWERS[90] = r'''
<p><strong>Situation:</strong> An IDE-style or email-app-style layout has a resizable left pane (file tree) and right pane (content). Users drag the divider; positions persist; mobile collapses to single pane. Used in dashboards, file explorers, code editors, mail clients.</p>

<p><strong>Approach:</strong> Use <strong>react-resizable-panels</strong> (modern, accessible, persistence built-in) for production. CSS Grid + JS for custom needs. On mobile, switch to single-pane with toggle.</p>

<pre><code>// react-resizable-panels — the 2026 default
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

function SplitView() {
  return (
    &lt;PanelGroup direction="horizontal" autoSaveId="main-layout"&gt;
      &lt;Panel defaultSize={25} minSize={15} maxSize={40} collapsible&gt;
        &lt;FileTree /&gt;
      &lt;/Panel&gt;

      &lt;PanelResizeHandle className="resize-handle" /&gt;

      &lt;Panel defaultSize={75} minSize={30}&gt;
        &lt;PanelGroup direction="vertical"&gt;
          &lt;Panel defaultSize={70}&gt;
            &lt;Editor /&gt;
          &lt;/Panel&gt;
          &lt;PanelResizeHandle /&gt;
          &lt;Panel defaultSize={30} minSize={10}&gt;
            &lt;Terminal /&gt;
          &lt;/Panel&gt;
        &lt;/PanelGroup&gt;
      &lt;/Panel&gt;
    &lt;/PanelGroup&gt;
  );
}</code></pre>

<p>Features come for free: drag handle, sizes saved to localStorage by <code>autoSaveId</code>, keyboard accessible (left/right arrows resize), <code>collapsible</code> snaps to closed, min/max constraints, nested panel groups for IDE-style layouts.</p>

<p><strong>CSS-only baseline (no resize, just split):</strong></p>

<pre><code>.split-view {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 0;
  height: 100vh;
}

@media (max-width: 768px) {
  .split-view {
    grid-template-columns: 1fr;   /* single column on mobile */
  }
}</code></pre>

<p><strong>Hand-rolled resizable handle:</strong></p>

<pre><code>function ResizableSplit({ children, defaultSize = 280, minSize = 150, maxSize = 600 }) {
  const [size, setSize] = useState(() =&gt;
    parseInt(localStorage.getItem("split-size") || defaultSize.toString(), 10)
  );
  const dragging = useRef(false);

  useEffect(() =&gt; {
    const onMove = (e) =&gt; {
      if (!dragging.current) return;
      const newSize = Math.min(maxSize, Math.max(minSize, e.clientX));
      setSize(newSize);
    };
    const onUp = () =&gt; {
      if (dragging.current) {
        dragging.current = false;
        localStorage.setItem("split-size", size.toString());
      }
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () =&gt; {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [size, minSize, maxSize]);

  return (
    &lt;div style={{ display: "grid", gridTemplateColumns: `${size}px 4px 1fr` }}&gt;
      {children[0]}
      &lt;div
        role="separator"
        aria-orientation="vertical"
        aria-valuenow={size}
        aria-valuemin={minSize}
        aria-valuemax={maxSize}
        tabIndex={0}
        onMouseDown={() =&gt; { dragging.current = true; }}
        onKeyDown={(e) =&gt; {
          if (e.key === "ArrowLeft") setSize((s) =&gt; Math.max(minSize, s - 10));
          if (e.key === "ArrowRight") setSize((s) =&gt; Math.min(maxSize, s + 10));
        }}
        className="resize-handle"
      /&gt;
      {children[1]}
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Mobile pattern &mdash; toggle between panes:</strong></p>

<pre><code>function ResponsiveSplit() {
  const isMobile = useMediaQuery("(max-width: 768px)");
  const [activePane, setActivePane] = useState&lt;"left" | "right"&gt;("left");

  if (isMobile) {
    return (
      &lt;&gt;
        &lt;Tabs value={activePane} onValueChange={setActivePane}&gt;
          &lt;TabsList&gt;
            &lt;TabsTrigger value="left"&gt;Files&lt;/TabsTrigger&gt;
            &lt;TabsTrigger value="right"&gt;Editor&lt;/TabsTrigger&gt;
          &lt;/TabsList&gt;
          &lt;TabsContent value="left"&gt;&lt;FileTree /&gt;&lt;/TabsContent&gt;
          &lt;TabsContent value="right"&gt;&lt;Editor /&gt;&lt;/TabsContent&gt;
        &lt;/Tabs&gt;
      &lt;/&gt;
    );
  }

  return &lt;DesktopSplit /&gt;;
}</code></pre>

<p><strong>Library comparison:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>react-resizable-panels</td><td>Modern default; nesting; persistence; a11y</td></tr>
  <tr><td>react-split-pane</td><td>Older; still works; less maintained</td></tr>
  <tr><td>allotment</td><td>VSCode-style; commercial-grade</td></tr>
  <tr><td>Custom CSS Grid</td><td>Static splits; no resize needed</td></tr>
</table>

<p><strong>Trade-offs:</strong> react-resizable-panels handles every detail you&rsquo;d otherwise rebuild: nested groups, collapse/expand, persistence with versioning, keyboard navigation, ARIA separator roles, mouse + touch + pointer events, performance (throttled resize). <strong>Performance during drag</strong>: avoid re-rendering heavy children mid-drag &mdash; react-resizable-panels uses CSS variables for sizes during drag and only commits state at end. Hand-rolled implementations re-render every frame and lag with complex panes. <strong>Persistence</strong>: store per-layout, not globally; if a user has multiple workspaces, each should remember its split sizes. <strong>Touch interactions</strong>: 4px handles are too narrow for fingers; use a hit target ≥16px even if the visual handle is 4px. <strong>iframe-heavy panes</strong> (like embedded editors) capture pointer events &mdash; cover them with an overlay during drag so the resize handle doesn&rsquo;t lose tracking.</p>
'''

ANSWERS[91] = r'''
<p><strong>Situation:</strong> First-time users land in the app and need guided introduction &mdash; profile setup, feature tour, sample data. Bad onboarding loses 60-80% of signups; good onboarding shows time-to-value within minutes. Patterns: progressive disclosure, contextual tooltips, sample workspace, interactive tutorial.</p>

<p><strong>Approach:</strong> Combine: <strong>(1)</strong> a multi-step setup wizard for required info, <strong>(2)</strong> contextual product tour with libraries like <strong>Shepherd.js</strong>, <strong>react-joyride</strong>, or <strong>Intro.js</strong>, <strong>(3)</strong> empty states with calls-to-action, <strong>(4)</strong> server-side tracking of completion so users can resume, <strong>(5)</strong> dismissibility so power users can skip.</p>

<pre><code>// Onboarding state machine — XState or useReducer
type OnboardingStep =
  | "welcome"
  | "profile"
  | "team"
  | "first-project"
  | "tour"
  | "complete";

const onboardingSteps: OnboardingStep[] = ["welcome", "profile", "team", "first-project", "tour", "complete"];

function OnboardingFlow() {
  const { data: user } = useUser();
  const updateUser = useMutation({ mutationFn: api.updateOnboarding });

  const currentStep = user?.onboarding?.step ?? "welcome";

  if (currentStep === "complete") return null;   // hide flow

  const advance = (next: OnboardingStep) =&gt; updateUser.mutate({ step: next });

  return (
    &lt;Dialog open modal&gt;
      &lt;ProgressIndicator current={currentStep} steps={onboardingSteps} /&gt;
      {currentStep === "welcome" &amp;&amp; &lt;WelcomeStep onNext={() =&gt; advance("profile")} /&gt;}
      {currentStep === "profile" &amp;&amp; &lt;ProfileStep onNext={() =&gt; advance("team")} /&gt;}
      {currentStep === "team" &amp;&amp; &lt;TeamStep onNext={() =&gt; advance("first-project")} onSkip={() =&gt; advance("first-project")} /&gt;}
      {currentStep === "first-project" &amp;&amp; &lt;ProjectStep onNext={() =&gt; advance("tour")} /&gt;}
      {currentStep === "tour" &amp;&amp; &lt;ProductTour onComplete={() =&gt; advance("complete")} /&gt;}
    &lt;/Dialog&gt;
  );
}</code></pre>

<p><strong>Product tour with react-joyride:</strong></p>

<pre><code>import Joyride from "react-joyride";

const tourSteps = [
  { target: "#sidebar", content: "Navigate between sections here", placement: "right" },
  { target: "#new-project-btn", content: "Create your first project", placement: "bottom" },
  { target: "#help", content: "Get help anytime here", placement: "left" }
];

function ProductTour({ onComplete }) {
  return (
    &lt;Joyride
      steps={tourSteps}
      continuous
      showProgress
      showSkipButton
      callback={({ status }) =&gt; {
        if (["finished", "skipped"].includes(status)) onComplete();
      }}
      styles={{ options: { primaryColor: "#0066cc" } }}
    /&gt;
  );
}</code></pre>

<p><strong>Empty states with clear next-step CTAs:</strong></p>

<pre><code>function ProjectsPage() {
  const { data: projects } = useProjects();

  if (!projects?.length) {
    return (
      &lt;EmptyState
        icon={&lt;FolderIcon /&gt;}
        title="No projects yet"
        description="Create your first project to get started — most teams start with a sample template."
        actions={
          &lt;&gt;
            &lt;Button onClick={createFromTemplate}&gt;Start from template&lt;/Button&gt;
            &lt;Button variant="ghost" onClick={createBlank}&gt;Or start blank&lt;/Button&gt;
          &lt;/&gt;
        }
      /&gt;
    );
  }
  ...
}</code></pre>

<p><strong>Onboarding patterns by app type:</strong></p>

<table>
  <tr><th>App type</th><th>Best onboarding</th></tr>
  <tr><td>SaaS productivity (Notion, Asana)</td><td>Sample workspace with example data; tour</td></tr>
  <tr><td>Data tool</td><td>"Connect data" wizard; first dashboard</td></tr>
  <tr><td>Social app</td><td>Profile photo + bio + follow suggestions</td></tr>
  <tr><td>Marketplace</td><td>Browse first; signup at checkout</td></tr>
  <tr><td>Dev tool</td><td>Quickstart with copy-paste; sample project</td></tr>
  <tr><td>Mobile app</td><td>Permissions + 3-screen swipe + skippable</td></tr>
</table>

<p><strong>Library comparison:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>react-joyride</td><td>Step tours; spotlight; progress; skip</td></tr>
  <tr><td>Shepherd.js</td><td>Framework-agnostic tours; powerful</td></tr>
  <tr><td>Intro.js</td><td>Simple tours; long-established</td></tr>
  <tr><td>Driver.js</td><td>Lightweight tours; modern</td></tr>
  <tr><td>Userpilot / Appcues / Pendo</td><td>SaaS &mdash; non-engineers create flows</td></tr>
</table>

<p><strong>Trade-offs:</strong> Onboarding fights with itself: thoroughness vs friction. Every required step loses some users to abandonment. Aim for one minimum-viable goal (sign up + create first thing) inside 90 seconds; defer optional steps. <strong>Server-track completion</strong>: persist <code>onboarding_step</code> on the user; users abandoning mid-flow return to the right place. <strong>A/B test ruthlessly</strong>: onboarding is the single biggest activation lever; measure conversion per step; prune steps that lose users. <strong>Skippable always</strong>: power users (returning customers, switchers from competitors) hate forced tours; provide "skip tour" prominently; don&rsquo;t hide it. <strong>Sample data</strong> beats empty starting state &mdash; users learn the app interacting with realistic content rather than staring at "Click here to begin." <strong>Progressive onboarding</strong>: don&rsquo;t teach everything upfront; introduce features contextually as users encounter them ("First time using filters? Here&rsquo;s how..."). <strong>SaaS tools (Userpilot, Appcues)</strong>: PMs and CS teams modify flows without engineering &mdash; useful for growth experimentation; expensive at scale.</p>
'''

ANSWERS[92] = r'''
<p><strong>Situation:</strong> A page header (or section header inside a long page) should stay pinned to the top as the user scrolls past it. Variations: header that shrinks/changes style when stuck, hides on scroll-down and reveals on scroll-up, or stays sticky only within its section.</p>

<p><strong>Approach:</strong> CSS <code>position: sticky</code> handles 90% of cases natively &mdash; no JS needed. Use IntersectionObserver to detect when the header has become "stuck" for style changes. Use scroll-direction detection for hide-on-scroll-down behavior.</p>

<pre><code>/* Pure CSS sticky header */
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: white;
  border-bottom: 1px solid var(--border);
  /* sticky needs a non-static parent without overflow:hidden */
}</code></pre>

<p><code>position: sticky</code> behaves like <code>relative</code> until the scroll position would push it past <code>top: 0</code>, at which point it becomes <code>fixed</code>. Free; performant; works in all modern browsers.</p>

<p><strong>Detect "stuck" state with IntersectionObserver</strong> (sentinel pattern):</p>

<pre><code>function StickyHeader({ children }) {
  const sentinelRef = useRef(null);
  const [isStuck, setIsStuck] = useState(false);

  useEffect(() =&gt; {
    const observer = new IntersectionObserver(
      ([entry]) =&gt; setIsStuck(entry.intersectionRatio &lt; 1),
      { threshold: [1], rootMargin: "-1px 0px 0px 0px" }
    );

    if (sentinelRef.current) observer.observe(sentinelRef.current);
    return () =&gt; observer.disconnect();
  }, []);

  return (
    &lt;&gt;
      &lt;div ref={sentinelRef} style={{ height: 1 }} /&gt;
      &lt;header className={`site-header ${isStuck ? "is-stuck" : ""}`}&gt;
        {children}
      &lt;/header&gt;
    &lt;/&gt;
  );
}

/* CSS — different style when stuck */
.site-header { padding: 1.5rem 2rem; }
.site-header.is-stuck {
  padding: 0.75rem 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.85);
}</code></pre>

<p><strong>Hide-on-scroll-down, reveal-on-scroll-up</strong> (Medium-style):</p>

<pre><code>function HideOnScrollHeader({ children }) {
  const [hidden, setHidden] = useState(false);
  const lastY = useRef(0);

  useEffect(() =&gt; {
    let rafId = null;

    const onScroll = () =&gt; {
      if (rafId) return;
      rafId = requestAnimationFrame(() =&gt; {
        const y = window.scrollY;
        if (y &gt; 100 &amp;&amp; y &gt; lastY.current) setHidden(true);   // scrolling down → hide
        else setHidden(false);                                  // scrolling up → show
        lastY.current = y;
        rafId = null;
      });
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () =&gt; window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    &lt;header className={`header ${hidden ? "hidden" : ""}`}&gt;
      {children}
    &lt;/header&gt;
  );
}

/* CSS */
.header {
  position: sticky;
  top: 0;
  transform: translateY(0);
  transition: transform 0.2s ease;
}
.header.hidden { transform: translateY(-100%); }</code></pre>

<p><strong>Pattern decisions:</strong></p>

<table>
  <tr><th>Goal</th><th>Approach</th></tr>
  <tr><td>Always-visible header</td><td>CSS <code>position: sticky; top: 0</code></td></tr>
  <tr><td>Different style when stuck</td><td>IntersectionObserver sentinel + class toggle</td></tr>
  <tr><td>Hide on scroll-down, show on scroll-up</td><td>Scroll-direction detection + transform</td></tr>
  <tr><td>Hide entirely past threshold</td><td>Conditional render or <code>display: none</code></td></tr>
  <tr><td>Sticky only within its section</td><td><code>position: sticky</code> with parent containing the scroll</td></tr>
  <tr><td>Pinned but transparent over hero</td><td><code>position: fixed</code> + <code>backdrop-filter</code></td></tr>
</table>

<p><strong>Common pitfalls:</strong></p>

<table>
  <tr><th>Pitfall</th><th>Cause / fix</th></tr>
  <tr><td>Sticky doesn&rsquo;t work</td><td>Parent has <code>overflow: hidden</code> or <code>auto</code> — remove or use fixed</td></tr>
  <tr><td>Sticky covers content</td><td>Add scroll-margin-top on anchored elements: <code>scroll-margin-top: 64px</code></td></tr>
  <tr><td>Layout shift when style changes</td><td>Reserve fixed height for header; use opacity/transform, not height changes</td></tr>
  <tr><td>Z-index battles with modals</td><td>Define a z-index scale; modals always above sticky headers</td></tr>
  <tr><td>Janky scroll on mobile Safari</td><td>iOS bounces; <code>position: sticky</code> handles this; <code>position: fixed</code> can fail</td></tr>
</table>

<p><strong>Trade-offs:</strong> <code>position: sticky</code> is performant because the browser handles it on the compositor thread &mdash; no JS scroll handlers, no jank. Reach for it first. Add JS only when sticky alone can&rsquo;t express the behavior (style changes, hide-on-scroll-down). <strong>Mobile considerations</strong>: small screens have less vertical space; aggressive sticky headers cost users content. Hide-on-scroll-down is friendlier on mobile. Bottom navigation often serves better than sticky top headers on mobile (thumbs reach the bottom). <strong>Performance</strong>: scroll handlers must be passive (<code>{ passive: true }</code>) to allow the browser to keep scrolling smooth; rAF-throttled for state updates. <strong>Accessibility</strong>: sticky headers must not cover content the user just navigated to via anchor link &mdash; <code>scroll-margin-top: var(--header-height)</code> on anchored elements ensures they appear below the header. Skip-link to main content remains required even with sticky header.</p>
'''

ANSWERS[93] = r'''
<p><strong>Situation:</strong> Image gallery, product page, or article needs a lightbox &mdash; click a thumbnail and the image expands full-screen with overlay, navigation between images (next/prev), zoom, swipe gestures on mobile, and keyboard navigation (arrows, Escape).</p>

<p><strong>Approach:</strong> Use a battle-tested library &mdash; <strong>yet-another-react-lightbox</strong>, <strong>PhotoSwipe</strong>, or <strong>react-image-gallery</strong>. Don&rsquo;t hand-roll &mdash; gesture handling, focus trap, image preloading, and zoom UX have many edge cases.</p>

<pre><code>// yet-another-react-lightbox — modern 2026 default
import Lightbox from "yet-another-react-lightbox";
import Zoom from "yet-another-react-lightbox/plugins/zoom";
import Thumbnails from "yet-another-react-lightbox/plugins/thumbnails";
import Captions from "yet-another-react-lightbox/plugins/captions";
import "yet-another-react-lightbox/styles.css";

function ProductGallery({ images }) {
  const [open, setOpen] = useState(false);
  const [index, setIndex] = useState(0);

  return (
    &lt;&gt;
      &lt;div className="thumbnail-grid"&gt;
        {images.map((img, i) =&gt; (
          &lt;button
            key={img.id}
            onClick={() =&gt; { setIndex(i); setOpen(true); }}
            aria-label={`View ${img.alt} full screen`}
          &gt;
            &lt;img
              src={img.thumb}
              alt={img.alt}
              width={200}
              height={200}
              loading="lazy"
            /&gt;
          &lt;/button&gt;
        ))}
      &lt;/div&gt;

      &lt;Lightbox
        open={open}
        close={() =&gt; setOpen(false)}
        index={index}
        on={{ view: ({ index }) =&gt; setIndex(index) }}
        slides={images.map((img) =&gt; ({
          src: img.full,
          alt: img.alt,
          title: img.title,
          description: img.description,
          width: img.width,
          height: img.height,
          srcSet: [
            { src: img.full_sm,  width: 800,  height: 600 },
            { src: img.full_md,  width: 1600, height: 1200 },
            { src: img.full_lg,  width: 3200, height: 2400 }
          ]
        }))}
        plugins={[Zoom, Thumbnails, Captions]}
        zoom={{ maxZoomPixelRatio: 3, scrollToZoom: true }}
      /&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>You get for free: keyboard navigation (arrows, Escape, Home/End), swipe gestures, pinch-to-zoom on touch, image preloading of next/prev, focus trap, scroll lock on body, ARIA roles (<code>aria-modal="true"</code>), responsive srcsets, optional video/3D/PDF slides via plugins.</p>

<p><strong>Library comparison:</strong></p>

<table>
  <tr><th>Library</th><th>Bundle</th><th>Best for</th></tr>
  <tr><td>yet-another-react-lightbox</td><td>~30KB</td><td>Modern; plugin architecture; the 2026 default</td></tr>
  <tr><td>PhotoSwipe (with React wrapper)</td><td>~30KB</td><td>Highly polished; battle-tested at scale</td></tr>
  <tr><td>react-image-gallery</td><td>~25KB</td><td>Inline gallery + lightbox combo</td></tr>
  <tr><td>react-photo-view</td><td>~20KB</td><td>Lightweight; smooth animations</td></tr>
  <tr><td>headlessui Dialog + custom</td><td>Variable</td><td>Full control; build your own around primitives</td></tr>
</table>

<p><strong>Hand-rolled minimal version</strong> (when you need full control):</p>

<pre><code>function MinimalLightbox({ images, index, onClose, onNavigate }) {
  useEffect(() =&gt; {
    const onKey = (e) =&gt; {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowLeft") onNavigate(index - 1);
      if (e.key === "ArrowRight") onNavigate(index + 1);
    };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";

    return () =&gt; {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [index, onClose, onNavigate]);

  // Preload neighbors
  useEffect(() =&gt; {
    [-1, 1].forEach((delta) =&gt; {
      const next = images[index + delta];
      if (next) {
        const img = new Image();
        img.src = next.full;
      }
    });
  }, [index, images]);

  return createPortal(
    &lt;div className="lightbox-overlay" role="dialog" aria-modal="true" aria-label="Image viewer" onClick={onClose}&gt;
      &lt;img
        src={images[index].full}
        alt={images[index].alt}
        onClick={(e) =&gt; e.stopPropagation()}
      /&gt;
      &lt;button className="prev" onClick={() =&gt; onNavigate(index - 1)} disabled={index === 0}&gt;‹&lt;/button&gt;
      &lt;button className="next" onClick={() =&gt; onNavigate(index + 1)} disabled={index === images.length - 1}&gt;›&lt;/button&gt;
      &lt;button className="close" onClick={onClose} aria-label="Close"&gt;✕&lt;/button&gt;
      &lt;p className="counter"&gt;{index + 1} / {images.length}&lt;/p&gt;
    &lt;/div&gt;,
    document.body
  );
}</code></pre>

<p><strong>UX details that separate good from great:</strong></p>

<table>
  <tr><th>Feature</th><th>Why</th></tr>
  <tr><td>Preload next/prev images</td><td>Instant navigation; no flash of loading</td></tr>
  <tr><td>Body scroll lock when open</td><td>Background page shouldn&rsquo;t scroll</td></tr>
  <tr><td>Focus trap inside lightbox</td><td>Tab cycles within; doesn&rsquo;t escape to background</td></tr>
  <tr><td>Restore focus on close</td><td>Return to the thumbnail user clicked</td></tr>
  <tr><td>Pinch-to-zoom on touch</td><td>Native pattern users expect</td></tr>
  <tr><td>Swipe to navigate / dismiss</td><td>Touch-first interaction</td></tr>
  <tr><td>Counter / position indicator</td><td>Users want to know "which photo of how many"</td></tr>
  <tr><td>Caption / description</td><td>Context for the image</td></tr>
  <tr><td>Loading state for slow images</td><td>Show spinner; don&rsquo;t leave blank</td></tr>
</table>

<p><strong>Trade-offs:</strong> Hand-rolled lightboxes ship with at least 5 a11y bugs. Every gesture combination, focus trap edge case, and preloading strategy in the libraries is the result of years of bug reports &mdash; reuse that work. <strong>Performance</strong>: full-resolution images can be huge; serve appropriately-sized variants based on viewport (srcSet); lazy-load non-visible thumbnails. <strong>Animation</strong>: a smooth thumbnail-to-fullscreen transition (FLIP technique or shared-element transition) feels native; abrupt show/hide feels cheap. <strong>SEO/social sharing</strong>: thumbnails must remain in the DOM (not fetched only on lightbox open) so crawlers see them; lightbox itself doesn&rsquo;t need to be SSR&rsquo;d. <strong>Mobile</strong>: full-screen lightboxes should respect notches and dynamic viewport (use <code>100dvh</code> not <code>100vh</code>); pinch zoom requires <code>touch-action: pinch-zoom</code> on the image container.</p>
'''

ANSWERS[94] = r'''
<p><strong>Situation:</strong> Need a rich-text editor for posts, comments, descriptions, or documentation. Requirements: bold/italic/lists, headings, links, images, code blocks, paste-from-Word handling, mentions/hashtags, collaborative editing, mobile support. Not a textarea or markdown field &mdash; full WYSIWYG.</p>

<p><strong>Approach:</strong> Use <strong>TipTap</strong> (built on ProseMirror) &mdash; the 2026 default for new React WYSIWYG. Alternatives: <strong>Lexical</strong> (Meta&rsquo;s, used in Facebook), <strong>Slate</strong>, <strong>Editor.js</strong>. Avoid: Quill (legacy maintenance), Draft.js (deprecated by Meta), CKEditor (commercial, heavy).</p>

<pre><code>// TipTap setup
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import Placeholder from "@tiptap/extension-placeholder";
import Mention from "@tiptap/extension-mention";

function RichEditor({ value, onChange, placeholder = "Start writing..." }) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] }
      }),
      Link.configure({ openOnClick: false }),
      Image.configure({ inline: false }),
      Placeholder.configure({ placeholder }),
      Mention.configure({
        suggestion: {
          items: ({ query }) =&gt;
            api.searchUsers(query).then((users) =&gt; users.slice(0, 5))
        }
      })
    ],
    content: value,
    onUpdate: ({ editor }) =&gt; onChange(editor.getHTML()),
    editorProps: {
      attributes: {
        class: "prose max-w-none focus:outline-none min-h-[300px]",
        "aria-label": "Rich text editor"
      }
    }
  });

  if (!editor) return null;

  return (
    &lt;div className="editor"&gt;
      &lt;Toolbar editor={editor} /&gt;
      &lt;EditorContent editor={editor} /&gt;
    &lt;/div&gt;
  );
}

// Toolbar — bind buttons to editor commands
function Toolbar({ editor }) {
  return (
    &lt;div className="toolbar" role="toolbar"&gt;
      &lt;button
        type="button"
        onClick={() =&gt; editor.chain().focus().toggleBold().run()}
        className={editor.isActive("bold") ? "active" : ""}
        aria-pressed={editor.isActive("bold")}
        aria-label="Bold"
      &gt;
        &lt;BoldIcon /&gt;
      &lt;/button&gt;
      &lt;button
        type="button"
        onClick={() =&gt; editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={editor.isActive("heading", { level: 2 }) ? "active" : ""}
      &gt;
        H2
      &lt;/button&gt;
      &lt;button
        type="button"
        onClick={() =&gt; {
          const url = window.prompt("URL");
          if (url) editor.chain().focus().setLink({ href: url }).run();
        }}
      &gt;
        &lt;LinkIcon /&gt;
      &lt;/button&gt;
      &lt;button
        type="button"
        onClick={() =&gt; editor.chain().focus().toggleBulletList().run()}
        className={editor.isActive("bulletList") ? "active" : ""}
      &gt;
        &lt;ListIcon /&gt;
      &lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Image upload integration:</strong></p>

<pre><code>// Custom paste / drop handler — upload to S3, insert URL
const handleImageUpload = async (file) =&gt; {
  const url = await api.uploadImage(file);
  editor.chain().focus().setImage({ src: url, alt: file.name }).run();
};

// Bind to editor events
editor.setOptions({
  editorProps: {
    handlePaste: (view, event) =&gt; {
      const file = event.clipboardData?.files[0];
      if (file?.type.startsWith("image/")) {
        handleImageUpload(file);
        return true;
      }
      return false;
    }
  }
});</code></pre>

<p><strong>Library comparison:</strong></p>

<table>
  <tr><th>Library</th><th>Engine</th><th>Best for</th></tr>
  <tr><td>TipTap</td><td>ProseMirror</td><td>2026 default; great DX; large ecosystem</td></tr>
  <tr><td>Lexical</td><td>Custom (Meta)</td><td>Performance-focused; used in production at Facebook</td></tr>
  <tr><td>Slate</td><td>Custom</td><td>Highly customizable; larger learning curve</td></tr>
  <tr><td>Editor.js</td><td>Block-based</td><td>Notion-style; JSON output</td></tr>
  <tr><td>BlockNote</td><td>TipTap-based</td><td>Notion-style API on top of TipTap</td></tr>
  <tr><td>Quill</td><td>Custom</td><td>Older; legacy projects</td></tr>
</table>

<p><strong>Output format choices:</strong></p>

<table>
  <tr><th>Format</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>HTML</td><td>Render directly; SEO-friendly; common</td><td>Sanitization required (XSS); DB stores markup</td></tr>
  <tr><td>JSON (ProseMirror doc)</td><td>Structured; programmatically transformable</td><td>Render layer required; not portable</td></tr>
  <tr><td>Markdown</td><td>Portable; easy to read</td><td>Loses rich features (mentions, custom blocks)</td></tr>
</table>

<p><strong>Trade-offs:</strong> WYSIWYG editors are enormous projects when hand-rolled; ProseMirror (the engine under TipTap) represents thousands of hours solving the hard problems &mdash; collaborative editing, undo/redo with operational transforms, paste from Word, IME composition, mobile keyboards. Use the libraries. <strong>XSS prevention is critical</strong>: editor output is HTML &mdash; if rendered with <code>dangerouslySetInnerHTML</code>, sanitize first with <strong>DOMPurify</strong>. Better: use the editor&rsquo;s renderer instead of dangerouslySetInnerHTML. <strong>Collaboration</strong>: TipTap + Yjs gives real-time multi-user editing in ~50 lines. Don&rsquo;t roll your own &mdash; CRDTs are doctorate-level work. <strong>Mobile</strong>: virtual keyboards, IME composition, native paste menus all interact with rich editors in subtle ways; libraries handle this. Always test on real iOS/Android. <strong>SSR considerations</strong>: TipTap requires browser APIs; render only on client (<code>useEffect</code> + state) or use the SSR-friendly extensions. <strong>Bundle size</strong>: full WYSIWYG is 100KB+ minified; lazy-load the editor on first edit attempt to keep initial bundle small.</p>
'''

ANSWERS[95] = r'''
<p><strong>Situation:</strong> Form needs multi-select &mdash; users pick multiple options from a list. Requirements: searchable, keyboard navigable, shows selected as chips, support for large option lists (1000+), grouping, async-loaded options, accessible.</p>

<p><strong>Approach:</strong> Use <strong>react-select</strong> (the established standard), <strong>shadcn/ui combobox</strong> (multi-select variant), or <strong>react-aria&rsquo;s <code>useListBox</code></strong> for full custom control. Don&rsquo;t hand-roll &mdash; the ARIA listbox + combobox pattern is dense.</p>

<pre><code>// react-select — production multi-select
import Select from "react-select";

const options = [
  { value: "react", label: "React" },
  { value: "vue", label: "Vue" },
  { value: "angular", label: "Angular" },
  { value: "svelte", label: "Svelte" }
];

function SkillsField({ value, onChange }) {
  return (
    &lt;Select
      isMulti
      options={options}
      value={options.filter((o) =&gt; value.includes(o.value))}
      onChange={(selected) =&gt; onChange(selected.map((s) =&gt; s.value))}
      closeMenuOnSelect={false}
      isSearchable
      placeholder="Select skills..."
      noOptionsMessage={() =&gt; "No matching skills"}
      classNamePrefix="select"
      aria-label="Skills"
    /&gt;
  );
}</code></pre>

<p><strong>Async-loaded options for large datasets:</strong></p>

<pre><code>import AsyncSelect from "react-select/async";

const loadOptions = async (input) =&gt; {
  if (input.length &lt; 2) return [];
  const results = await api.searchUsers(input);
  return results.map((u) =&gt; ({ value: u.id, label: u.name, email: u.email }));
};

&lt;AsyncSelect
  isMulti
  cacheOptions
  defaultOptions
  loadOptions={loadOptions}
  value={selectedUsers}
  onChange={setSelectedUsers}
  formatOptionLabel={(option) =&gt; (
    &lt;div className="user-option"&gt;
      &lt;strong&gt;{option.label}&lt;/strong&gt;
      &lt;small&gt;{option.email}&lt;/small&gt;
    &lt;/div&gt;
  )}
/&gt;</code></pre>

<p><strong>Hand-rolled with Downshift &mdash; more control, more code:</strong></p>

<pre><code>function MultiSelect({ options, value, onChange, label }) {
  const [inputValue, setInputValue] = useState("");
  const filtered = options.filter(
    (o) =&gt; o.label.toLowerCase().includes(inputValue.toLowerCase()) &amp;&amp; !value.includes(o.value)
  );

  const combobox = useCombobox({
    items: filtered,
    inputValue,
    onInputValueChange: ({ inputValue }) =&gt; setInputValue(inputValue),
    onSelectedItemChange: ({ selectedItem }) =&gt; {
      if (selectedItem) {
        onChange([...value, selectedItem.value]);
        setInputValue("");
      }
    },
    stateReducer: (state, { type, changes }) =&gt; {
      // Keep menu open after selection
      if (type === useCombobox.stateChangeTypes.InputKeyDownEnter ||
          type === useCombobox.stateChangeTypes.ItemClick) {
        return { ...changes, isOpen: true, highlightedIndex: 0, inputValue: "" };
      }
      return changes;
    }
  });

  const removeItem = (val) =&gt; onChange(value.filter((v) =&gt; v !== val));

  return (
    &lt;div className="multi-select"&gt;
      &lt;label {...combobox.getLabelProps()}&gt;{label}&lt;/label&gt;
      &lt;div {...combobox.getComboboxProps()} className="multi-select-input"&gt;
        {value.map((v) =&gt; {
          const opt = options.find((o) =&gt; o.value === v);
          return (
            &lt;span key={v} className="chip"&gt;
              {opt?.label}
              &lt;button type="button" onClick={() =&gt; removeItem(v)} aria-label={`Remove ${opt?.label}`}&gt;✕&lt;/button&gt;
            &lt;/span&gt;
          );
        })}
        &lt;input {...combobox.getInputProps()} placeholder="Search..." /&gt;
      &lt;/div&gt;
      &lt;ul {...combobox.getMenuProps()} className={combobox.isOpen ? "open" : ""}&gt;
        {combobox.isOpen &amp;&amp; filtered.map((item, idx) =&gt; (
          &lt;li
            key={item.value}
            {...combobox.getItemProps({ item, index: idx })}
            className={combobox.highlightedIndex === idx ? "highlighted" : ""}
          &gt;
            {item.label}
          &lt;/li&gt;
        ))}
      &lt;/ul&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Library comparison:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>react-select</td><td>Production multi-select; mature; many features; ~30KB</td></tr>
  <tr><td>shadcn/ui combobox + checkboxes</td><td>Tailwind-styled; full control; integrates with cmdk</td></tr>
  <tr><td>Downshift</td><td>Behavioral primitive; bring your own UI</td></tr>
  <tr><td>react-aria useListBox</td><td>Full a11y from Adobe; verbose</td></tr>
  <tr><td>Mantine MultiSelect</td><td>Polished; works out of the box</td></tr>
  <tr><td>Headless UI Combobox</td><td>Tailwind-friendly primitive</td></tr>
</table>

<p><strong>UX details that matter:</strong></p>

<table>
  <tr><th>Detail</th><th>Why</th></tr>
  <tr><td>Keep menu open after selection</td><td>Users pick multiple in succession; closing per pick is annoying</td></tr>
  <tr><td>Keyboard remove (Backspace on empty)</td><td>Faster than mouse-clicking ✕ on each chip</td></tr>
  <tr><td>"Select all" / "Clear all"</td><td>Common operations on large lists</td></tr>
  <tr><td>Selected count badge</td><td>"3 selected" when many</td></tr>
  <tr><td>Group options</td><td>Categories visible without scrolling</td></tr>
  <tr><td>Virtualize long lists</td><td>1000+ options need react-window inside the menu</td></tr>
  <tr><td>Search highlights match</td><td>Show what matched the query</td></tr>
  <tr><td>Empty state</td><td>"No matches for X. Add as new?" for creatable selects</td></tr>
</table>

<p><strong>Trade-offs:</strong> react-select is the safe production pick &mdash; thousands of apps, mature, accessible, well-documented. ~30KB is its main cost. <strong>For Tailwind/design-system codebases</strong>, shadcn/ui combobox built on cmdk + Radix gives full styling control with accessible primitives &mdash; sometimes worth replacing react-select for visual consistency. <strong>Performance with large lists</strong>: react-select handles ~1000 options before performance degrades; beyond that, virtualize the menu (<code>react-window</code> or <code>react-virtuoso</code>) or move to async-loaded options. <strong>Mobile UX</strong>: native <code>&lt;select multiple&gt;</code> on iOS/Android is awkward; libraries provide better touch UX with full-screen modals on small viewports. <strong>Form integration</strong>: with React Hook Form, use Controller wrapper since react-select doesn&rsquo;t use standard input events; with Zod, validate the array of selected values. <strong>A11y minimum</strong>: combobox role + listbox role + aria-multiselectable + aria-selected per option + announcement of selections via live region.</p>
'''

ANSWERS[96] = r'''
<p><strong>Situation:</strong> The app makes the same API calls repeatedly &mdash; user profile fetched on every page load, lookup tables refetched constantly, dashboard widgets each refetch the same metrics. Need a caching strategy that&rsquo;s fast, fresh enough, and works offline.</p>

<p><strong>Approach:</strong> <strong>TanStack Query</strong> as the universal client-side data cache. Tune <code>staleTime</code> + <code>gcTime</code> per query type. For offline support, persist to localStorage/IndexedDB. For HTTP-level caching, set proper <code>Cache-Control</code> headers server-side and let the browser do work.</p>

<pre><code>// Configure global defaults + per-query overrides
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,                  // data fresh for 30s; no refetch
      gcTime: 5 * 60 * 1000,              // cache kept 5min after no observers
      refetchOnWindowFocus: true,         // refetch when tab regains focus
      refetchOnReconnect: true,           // refetch when network returns
      retry: (failureCount, error) =&gt; {
        if (error.status === 404) return false;
        return failureCount &lt; 3;
      }
    }
  }
});

// Per-query: override based on data volatility
const useUserProfile = () =&gt; useQuery({
  queryKey: ["profile"],
  queryFn: api.getProfile,
  staleTime: 5 * 60 * 1000     // profile changes rarely; 5min stale
});

const useDashboardStats = () =&gt; useQuery({
  queryKey: ["dashboard", "stats"],
  queryFn: api.getStats,
  staleTime: 10_000,           // refresh frequently
  refetchInterval: 30_000      // even if focused, refresh every 30s
});

const useStaticLookup = () =&gt; useQuery({
  queryKey: ["countries"],
  queryFn: api.getCountries,
  staleTime: Infinity,         // never goes stale; lookup table doesn&rsquo;t change
  gcTime: Infinity
});</code></pre>

<p><strong>Persistence across page reloads:</strong></p>

<pre><code>import { persistQueryClient } from "@tanstack/react-query-persist-client";
import { createSyncStoragePersister } from "@tanstack/query-sync-storage-persister";

const persister = createSyncStoragePersister({
  storage: window.localStorage,
  key: "QUERY_CACHE",
  serialize: JSON.stringify,
  deserialize: JSON.parse
});

persistQueryClient({
  queryClient,
  persister,
  maxAge: 1000 * 60 * 60 * 24,    // discard cached data older than 24h
  buster: import.meta.env.VITE_BUILD_ID  // bust cache on new deploys
});</code></pre>

<p>Now data persists across reloads &mdash; users see cached content instantly while background refetch updates it. Fundamental for offline-first PWAs.</p>

<p><strong>Multi-layer caching strategy:</strong></p>

<table>
  <tr><th>Layer</th><th>Mechanism</th><th>What it caches</th></tr>
  <tr><td>HTTP (browser)</td><td><code>Cache-Control</code> headers</td><td>Static assets, images, public APIs</td></tr>
  <tr><td>Service Worker</td><td>Custom fetch interception</td><td>Offline-first PWA assets/data</td></tr>
  <tr><td>TanStack Query (memory)</td><td>In-memory cache</td><td>API responses across components</td></tr>
  <tr><td>TanStack Query (persisted)</td><td>localStorage/IndexedDB</td><td>API responses across reloads</td></tr>
  <tr><td>Server-side (CDN)</td><td>Cloudflare, Vercel, Fastly</td><td>API responses; static pages</td></tr>
  <tr><td>Server-side (app)</td><td>Redis, Memcached</td><td>Database query results</td></tr>
</table>

<p><strong>Cache key design</strong> &mdash; the foundation of everything else:</p>

<pre><code>// Hierarchical keys — invalidate broadly or specifically
["users"]                              // all users
["users", "list", { page: 1 }]         // users list page 1
["users", "detail", userId]            // specific user
["users", "detail", userId, "posts"]   // user&rsquo;s posts

// Invalidate selectively after mutation
queryClient.invalidateQueries({ queryKey: ["users"] });               // ALL users
queryClient.invalidateQueries({ queryKey: ["users", "list"] });       // just lists
queryClient.invalidateQueries({ queryKey: ["users", "detail", id] }); // one user</code></pre>

<p><strong>Caching by data type:</strong></p>

<table>
  <tr><th>Data type</th><th>staleTime</th><th>refetchOnWindowFocus</th></tr>
  <tr><td>User profile</td><td>5 min</td><td>true</td></tr>
  <tr><td>Lookup tables (countries, categories)</td><td>Infinity</td><td>false</td></tr>
  <tr><td>Dashboard metrics</td><td>10s</td><td>true</td></tr>
  <tr><td>Search results</td><td>1 min</td><td>false (annoying)</td></tr>
  <tr><td>User-created content (posts, todos)</td><td>30s</td><td>true</td></tr>
  <tr><td>Real-time data (chat, prices)</td><td>0 (always stale)</td><td>true (or use WebSocket)</td></tr>
  <tr><td>Static config</td><td>Infinity</td><td>false</td></tr>
</table>

<p><strong>Cache invalidation patterns:</strong></p>

<table>
  <tr><th>Pattern</th><th>Use</th></tr>
  <tr><td><code>invalidateQueries</code> &mdash; mark stale, refetch active</td><td>After mutations; data changed</td></tr>
  <tr><td><code>setQueryData</code> &mdash; manual update</td><td>Got fresh data from another source (mutation response, WebSocket)</td></tr>
  <tr><td><code>removeQueries</code> &mdash; delete from cache</td><td>User logged out; sensitive data</td></tr>
  <tr><td><code>refetchQueries</code> &mdash; force fetch now</td><td>Refresh button; debug</td></tr>
  <tr><td>Time-based <code>staleTime</code></td><td>Predictable freshness window</td></tr>
</table>

<p><strong>Trade-offs:</strong> Cache freshness vs traffic is the central tension. Aggressive caching (long staleTime) means fewer requests but stale data risk; aggressive refetch means fresh data but server load. Tune per data type, not globally. <strong>Don&rsquo;t cache stale-sensitive data forever</strong> &mdash; pricing, inventory, balance, anything financial: keep staleTime low or use WebSockets. <strong>Cache busting on deploy</strong> &mdash; the persisted cache must include a build ID so old cached data structures don&rsquo;t break a new app version. <strong>HTTP caching often beats client caching</strong>: a properly-configured CDN with <code>Cache-Control: public, max-age=300, stale-while-revalidate=60</code> caches at the edge for all users globally; client-side caching only helps the same user. Use both. <strong>Privacy</strong>: don&rsquo;t persist personally-sensitive data to localStorage on shared devices; selectively persist (e.g., exclude queries containing PII) or scope by user ID and clear on logout.</p>
'''

ANSWERS[97] = r'''
<p><strong>Situation:</strong> Modal dialogs must work across viewports &mdash; centered overlay on desktop, full-screen sheet on phones, possibly bottom-sheet style for mobile-native UX. Content varies in length; modals must scroll within themselves; never break the underlying page; respect safe-areas on iOS notches.</p>

<p><strong>Approach:</strong> Use <strong>Radix Dialog</strong> for behavior; layer responsive CSS for sizing. For mobile bottom-sheet UX, <strong>Vaul</strong> (the 2026 React drawer/sheet library) gives native-feel drag-to-dismiss; combine with Dialog at desktop sizes via media query.</p>

<pre><code>// Responsive modal: centered on desktop, full-screen sheet on mobile
import * as Dialog from "@radix-ui/react-dialog";

function ResponsiveModal({ open, onClose, title, children }) {
  return (
    &lt;Dialog.Root open={open} onOpenChange={onClose}&gt;
      &lt;Dialog.Portal&gt;
        &lt;Dialog.Overlay className="dialog-overlay" /&gt;
        &lt;Dialog.Content className="dialog-content"&gt;
          &lt;header className="dialog-header"&gt;
            &lt;Dialog.Title&gt;{title}&lt;/Dialog.Title&gt;
            &lt;Dialog.Close aria-label="Close"&gt;✕&lt;/Dialog.Close&gt;
          &lt;/header&gt;
          &lt;div className="dialog-body"&gt;{children}&lt;/div&gt;
        &lt;/Dialog.Content&gt;
      &lt;/Dialog.Portal&gt;
    &lt;/Dialog.Root&gt;
  );
}</code></pre>

<pre><code>/* Desktop: centered modal */
.dialog-overlay {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.55);
  animation: fadeIn 150ms ease;
}

.dialog-content {
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  max-width: 500px;
  width: 95vw;
  max-height: 85vh;
  background: white;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: scaleIn 150ms ease;
}

.dialog-body {
  overflow-y: auto;     /* body scrolls; header stays */
  padding: 1rem 1.5rem;
}

/* Mobile: full-screen */
@media (max-width: 600px) {
  .dialog-content {
    top: 0; left: 0;
    transform: none;
    width: 100vw;
    max-width: 100vw;
    height: 100dvh;       /* dynamic viewport height for iOS Safari */
    max-height: 100dvh;
    border-radius: 0;
    padding-top: env(safe-area-inset-top);
    padding-bottom: env(safe-area-inset-bottom);
    animation: slideUp 200ms ease;
  }
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}</code></pre>

<p><strong>Bottom-sheet for mobile (native-feel):</strong></p>

<pre><code>// Vaul drawer for mobile, Radix Dialog for desktop
import { Drawer } from "vaul";

function MobileBottomSheet({ open, onClose, children }) {
  return (
    &lt;Drawer.Root open={open} onOpenChange={(o) =&gt; !o &amp;&amp; onClose()}&gt;
      &lt;Drawer.Portal&gt;
        &lt;Drawer.Overlay className="drawer-overlay" /&gt;
        &lt;Drawer.Content className="drawer-content"&gt;
          &lt;div className="drag-handle" /&gt;
          {children}
        &lt;/Drawer.Content&gt;
      &lt;/Drawer.Portal&gt;
    &lt;/Drawer.Root&gt;
  );
}

// Switch based on viewport
function Modal({ open, onClose, children, title }) {
  const isMobile = useMediaQuery("(max-width: 600px)");

  return isMobile ? (
    &lt;MobileBottomSheet open={open} onClose={onClose}&gt;{children}&lt;/MobileBottomSheet&gt;
  ) : (
    &lt;ResponsiveModal open={open} onClose={onClose} title={title}&gt;{children}&lt;/ResponsiveModal&gt;
  );
}</code></pre>

<p><strong>Sizing patterns:</strong></p>

<table>
  <tr><th>Modal type</th><th>Desktop</th><th>Mobile</th></tr>
  <tr><td>Confirmation</td><td>400px wide</td><td>Centered card with margin</td></tr>
  <tr><td>Form</td><td>500-600px wide</td><td>Full-screen sheet</td></tr>
  <tr><td>Detail view</td><td>800px wide</td><td>Full-screen</td></tr>
  <tr><td>Onboarding</td><td>700px x 500px</td><td>Full-screen with steps</td></tr>
  <tr><td>Picker (date, etc.)</td><td>Anchored popover</td><td>Bottom sheet</td></tr>
  <tr><td>Photo viewer</td><td>Near-full-screen</td><td>Full-screen with swipe-to-close</td></tr>
</table>

<p><strong>iOS-specific gotchas:</strong></p>

<table>
  <tr><th>Issue</th><th>Fix</th></tr>
  <tr><td><code>100vh</code> includes the address bar that hides</td><td>Use <code>100dvh</code> (dynamic viewport)</td></tr>
  <tr><td>Background page scrolls under modal</td><td>Body scroll lock (Radix does this)</td></tr>
  <tr><td>Bottom safe area cuts off content</td><td><code>padding-bottom: env(safe-area-inset-bottom)</code></td></tr>
  <tr><td>Notch covers top content</td><td><code>padding-top: env(safe-area-inset-top)</code></td></tr>
  <tr><td>Virtual keyboard shifts viewport</td><td><code>visualViewport</code> API or <code>interactive-widget=resizes-content</code></td></tr>
  <tr><td>Pinch-zoom triggers in modal</td><td><code>touch-action: pan-y</code> on scrollable areas</td></tr>
</table>

<p><strong>Trade-offs:</strong> Bottom sheets feel native on mobile (matches iOS sheet, Android Material) but require more code than scaling a desktop modal full-screen. For most apps, full-screen mobile modal is good enough; reserve bottom sheets for primary touch interactions (filters, options menus). <strong>Radix Dialog gives you</strong>: focus trap, restore focus on close, body scroll lock, Escape to close, click-outside to close, ARIA roles. Don&rsquo;t hand-roll &mdash; the a11y is dense. <strong>Animation timing</strong>: 150-200ms for desktop modals, 200-300ms for mobile sheets; faster than 100ms feels instant (jarring); slower than 300ms feels sluggish. Use ease-out for entrance, ease-in for exit. <strong>Long content</strong>: scroll within the modal body, not the page; the modal header/footer stay fixed for context. <strong>Stack management</strong>: nested modals are an antipattern &mdash; one modal at a time. If you need a "second step," replace content within the same modal.</p>
'''

ANSWERS[98] = r'''
<p><strong>Situation:</strong> State has nested structure &mdash; user with addresses with phone numbers, form with sections with fields with options, document with pages with elements. Updating deeply requires preserving immutability without spreading every level manually. Hand-spread updates become unreadable and error-prone.</p>

<p><strong>Approach:</strong> Use <strong>Immer</strong> for mutate-style updates that produce immutable results. Already built into <strong>Redux Toolkit</strong> and <strong>Zustand&rsquo;s middleware</strong>. For component-local complex state, combine <code>useReducer</code> + Immer (<code>useImmerReducer</code>).</p>

<pre><code>// Without Immer — manual spread chains, error-prone
const updateUserPhone = (state, userId, phoneIdx, newNumber) =&gt; ({
  ...state,
  users: state.users.map((u) =&gt;
    u.id !== userId ? u : {
      ...u,
      addresses: u.addresses.map((addr, ai) =&gt;
        ai !== 0 ? addr : {
          ...addr,
          phones: addr.phones.map((p, pi) =&gt;
            pi !== phoneIdx ? p : { ...p, number: newNumber }
          )
        }
      )
    }
  )
});</code></pre>

<pre><code>// With Immer — mutate-style; output is immutable
import { produce } from "immer";

const updateUserPhone = (state, userId, phoneIdx, newNumber) =&gt;
  produce(state, (draft) =&gt; {
    const user = draft.users.find((u) =&gt; u.id === userId);
    if (user) {
      user.addresses[0].phones[phoneIdx].number = newNumber;
    }
  });</code></pre>

<p>Same logic, immensely more readable. Immer wraps the draft in a Proxy that records mutations and applies them to a new immutable state.</p>

<p><strong>useImmerReducer for component state:</strong></p>

<pre><code>import { useImmerReducer } from "use-immer";

type State = {
  user: { name: string; addresses: Address[] };
  ui: { activeAddressId: string | null; isEditing: boolean };
};

const reducer = (draft: State, action: Action) =&gt; {
  switch (action.type) {
    case "ADD_ADDRESS":
      draft.user.addresses.push(action.address);
      break;
    case "UPDATE_ADDRESS":
      const addr = draft.user.addresses.find((a) =&gt; a.id === action.id);
      if (addr) Object.assign(addr, action.updates);
      break;
    case "REMOVE_ADDRESS":
      draft.user.addresses = draft.user.addresses.filter((a) =&gt; a.id !== action.id);
      break;
    case "SET_EDITING":
      draft.ui.isEditing = action.value;
      break;
  }
  // No need to return anything — Immer handles it
};

function ProfileEditor() {
  const [state, dispatch] = useImmerReducer(reducer, initialState);
  ...
}</code></pre>

<p><strong>Approach comparison:</strong></p>

<table>
  <tr><th>Approach</th><th>Best for</th></tr>
  <tr><td>Hand-spread <code>{...state}</code></td><td>Shallow updates, &lt;3 levels nesting</td></tr>
  <tr><td>Immer <code>produce</code></td><td>Any depth; mutate-style code; clear intent</td></tr>
  <tr><td>Lodash <code>_.set</code> with cloneDeep</td><td>Path-based; old-school; mutates clones</td></tr>
  <tr><td>Normalize state shape</td><td>Avoid the problem entirely &mdash; flatten</td></tr>
  <tr><td>External libs (Lens, Optics)</td><td>Functional purists; advanced</td></tr>
</table>

<p><strong>The deeper fix &mdash; normalize state shape:</strong></p>

<pre><code>// Bad — nested
state = {
  users: [{
    id: 1,
    addresses: [{
      id: 10,
      phones: [{ id: 100, number: "..." }]
    }]
  }]
}

// Good — normalized (Redux Toolkit&rsquo;s createEntityAdapter pattern)
state = {
  users:     { byId: { 1: { id: 1, addressIds: [10] } }, allIds: [1] },
  addresses: { byId: { 10: { id: 10, userId: 1, phoneIds: [100] } }, allIds: [10] },
  phones:    { byId: { 100: { id: 100, addressId: 10, number: "..." } }, allIds: [100] }
}

// Update a phone — flat, no traversal
draft.phones.byId[100].number = newNumber;</code></pre>

<p>Normalized state is what relational databases do; React state can borrow the pattern. Updates become O(1); querying needs joins (selectors), but that&rsquo;s well-supported by <code>reselect</code> or <code>createEntityAdapter</code>.</p>

<p><strong>When to normalize vs nest:</strong></p>

<table>
  <tr><th>Nest when</th><th>Normalize when</th></tr>
  <tr><td>Data is genuinely tree-shaped (UI tree, document outline)</td><td>Many places reference same entities</td></tr>
  <tr><td>Updates always touch the whole subtree</td><td>Same entity needs deep updates from many places</td></tr>
  <tr><td>State is small</td><td>State is large (1000+ entities)</td></tr>
  <tr><td>Component-local</td><td>App-wide (Redux, Zustand)</td></tr>
  <tr><td>One-shot use (form draft)</td><td>Long-lived domain data</td></tr>
</table>

<p><strong>TypeScript with Immer</strong> works seamlessly &mdash; the draft type is inferred as a writable version of the state type; the result is properly typed back. <strong>Performance</strong>: Immer&rsquo;s proxy adds a small overhead but it&rsquo;s negligible for typical state sizes (under 100ms even for very large states). For hot loops with millions of updates, manual spread can be faster &mdash; but that&rsquo;s rare.</p>

<p><strong>Trade-offs:</strong> Immer is the productivity multiplier for nested state &mdash; the readable, intuitive way to write deep updates without giving up immutability. Redux Toolkit and Zustand bake it in; using it elsewhere is one import. <strong>Don&rsquo;t reach for Immer to "fix" badly-shaped state</strong>: if you&rsquo;re writing 5-level deep updates frequently, the state shape is wrong &mdash; normalize first. Immer makes deep updates tolerable; normalization makes them disappear. <strong>Identity preservation</strong>: Immer only creates new references for branches that changed; unchanged branches keep their references &mdash; React.memo/useMemo continue to work correctly. <strong>Don&rsquo;t use Immer outside of state updates</strong>: it&rsquo;s for state transitions; using it for general data manipulation just hides the immutability semantic. <strong>Patches</strong>: Immer can produce patches and inverse patches; useful for undo/redo, server sync (send only diffs), and audit logs.</p>
'''

ANSWERS[99] = r'''
<p><strong>Situation:</strong> The frontend talks to flaky APIs &mdash; transient network errors, 5xx server hiccups, rate-limit 429s. Without retry logic, every flake becomes a user-visible error. Need automatic retry with exponential backoff, jitter, idempotency awareness, and "give up after N tries" handling.</p>

<p><strong>Approach:</strong> If using TanStack Query, configure its built-in retry &mdash; you&rsquo;re mostly done. For non-React-Query code, build a fetch wrapper using <strong>axios-retry</strong>, <strong>ky</strong> (with retry built-in), or roll your own minimal version.</p>

<pre><code>// TanStack Query — built-in retry with backoff
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) =&gt; {
        // Don&rsquo;t retry 4xx (client errors); only 5xx and network errors
        if (error?.status &gt;= 400 &amp;&amp; error?.status &lt; 500) return false;
        return failureCount &lt; 3;
      },
      retryDelay: (attempt) =&gt; Math.min(1000 * 2 ** attempt, 30_000)
    },
    mutations: {
      retry: 1   // be careful with mutation retries
    }
  }
});</code></pre>

<p><strong>Standalone API client with retry &mdash; ky (the modern fetch wrapper):</strong></p>

<pre><code>import ky from "ky";

const api = ky.create({
  prefixUrl: import.meta.env.VITE_API_URL,
  retry: {
    limit: 3,
    methods: ["get", "put", "head", "delete", "options"],   // skip POST by default — risky
    statusCodes: [408, 429, 500, 502, 503, 504],
    backoffLimit: 30_000
  },
  hooks: {
    beforeRetry: [
      ({ request, error, retryCount }) =&gt; {
        console.warn(`Retrying ${request.url} (attempt ${retryCount + 1}):`, error.message);
      }
    ]
  },
  timeout: 10_000
});

// Usage
const data = await api.get("users/123").json();</code></pre>

<p><strong>Hand-rolled fetch wrapper with backoff + jitter:</strong></p>

<pre><code>type RetryOptions = {
  retries?: number;
  baseDelay?: number;
  maxDelay?: number;
  retryOn?: number[];
  signal?: AbortSignal;
};

async function fetchWithRetry(
  url: string,
  init: RequestInit = {},
  opts: RetryOptions = {}
): Promise&lt;Response&gt; {
  const {
    retries = 3,
    baseDelay = 1000,
    maxDelay = 30_000,
    retryOn = [408, 429, 500, 502, 503, 504],
    signal
  } = opts;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt &lt;= retries; attempt++) {
    if (signal?.aborted) throw new Error("Aborted");

    try {
      const res = await fetch(url, { ...init, signal });

      if (res.ok) return res;

      if (!retryOn.includes(res.status) || attempt === retries) {
        throw new HttpError(res.status, res.statusText);
      }

      // Honor Retry-After if present
      const retryAfter = res.headers.get("Retry-After");
      const headerDelay = retryAfter ? parseInt(retryAfter, 10) * 1000 : 0;

      // Exponential backoff with full jitter
      const expDelay = Math.min(baseDelay * 2 ** attempt, maxDelay);
      const jittered = Math.random() * expDelay;
      const delay = Math.max(headerDelay, jittered);

      await new Promise((r) =&gt; setTimeout(r, delay));
    } catch (err) {
      if (err.name === "AbortError") throw err;
      lastError = err;

      if (attempt === retries) throw err;

      const expDelay = Math.min(baseDelay * 2 ** attempt, maxDelay);
      await new Promise((r) =&gt; setTimeout(r, Math.random() * expDelay));
    }
  }

  throw lastError;
}

class HttpError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}</code></pre>

<p><strong>Retry-or-not decision matrix:</strong></p>

<table>
  <tr><th>Status / Error</th><th>Retry?</th><th>Why</th></tr>
  <tr><td>Network error (offline)</td><td>Yes</td><td>Connection may recover</td></tr>
  <tr><td>408 Request Timeout</td><td>Yes</td><td>Server didn&rsquo;t complete in time</td></tr>
  <tr><td>429 Too Many Requests</td><td>Yes (with Retry-After)</td><td>Rate-limited; back off</td></tr>
  <tr><td>500 Internal Server Error</td><td>Yes</td><td>Likely transient</td></tr>
  <tr><td>502 / 503 / 504</td><td>Yes</td><td>Gateway / unavailable / timeout</td></tr>
  <tr><td>400 Bad Request</td><td>No</td><td>Client error; won&rsquo;t change</td></tr>
  <tr><td>401 Unauthorized</td><td>No (or refresh-token-then-retry)</td><td>Auth issue; need fresh token</td></tr>
  <tr><td>403 Forbidden</td><td>No</td><td>Permission won&rsquo;t change</td></tr>
  <tr><td>404 Not Found</td><td>No</td><td>Resource doesn&rsquo;t exist</td></tr>
  <tr><td>409 Conflict</td><td>No</td><td>State conflict; user must resolve</td></tr>
  <tr><td>422 Unprocessable</td><td>No</td><td>Validation failed</td></tr>
</table>

<p><strong>Mutation retry caution:</strong></p>

<table>
  <tr><th>Operation</th><th>Idempotent?</th><th>Safe to retry?</th></tr>
  <tr><td>GET</td><td>Yes</td><td>✅ Always</td></tr>
  <tr><td>PUT (full replace)</td><td>Yes</td><td>✅ Yes</td></tr>
  <tr><td>DELETE</td><td>Yes</td><td>✅ Yes (404 on second is OK)</td></tr>
  <tr><td>POST (create)</td><td>No</td><td>⚠ Risk of duplicate; need idempotency key</td></tr>
  <tr><td>POST (action: send email)</td><td>No</td><td>⚠ Side effect repeats</td></tr>
  <tr><td>PATCH</td><td>Depends</td><td>⚠ Verify per endpoint</td></tr>
</table>

<p><strong>Idempotency keys for POSTs</strong>: client generates a UUID per logical operation; sends as <code>Idempotency-Key</code> header; server stores and returns the same response on retry. Stripe&rsquo;s API uses this pattern; payment APIs must use it.</p>

<p><strong>Trade-offs:</strong> Retry logic is a minefield of subtle bugs &mdash; libraries (TanStack Query, ky, axios-retry) get it right. Don&rsquo;t hand-roll unless you have specific needs. <strong>Exponential backoff + jitter is essential</strong>: without jitter, all retrying clients hit the server simultaneously after each backoff window (thundering herd) &mdash; jitter spreads them out and breaks the cascade. <strong>Honor Retry-After</strong>: when the server tells you to wait 60s, do it; ignoring this header can get your client IP rate-limited or banned. <strong>Don&rsquo;t retry forever</strong>: cap at 3-5 attempts; surface failure to the user with retry button. <strong>User-cancellable</strong>: pass an AbortSignal through retry loops; users navigating away should cancel pending retries. <strong>Mutation retries need idempotency</strong>: never blindly retry a POST that creates payments, sends emails, or charges accounts &mdash; require server-side dedup via idempotency key. <strong>Observability</strong>: log retry attempts to Sentry/Datadog with attempt count; sustained retry rates indicate upstream issues you can alert on.</p>
'''

ANSWERS[100] = r'''
<p><strong>Situation:</strong> Forms must validate user input with custom error messages &mdash; not just "required" but contextually meaningful messages ("Password must include a number", "Email must be a work address", "Username already taken"). Validation runs client-side for instant feedback and server-side for trust. Messages must be translatable.</p>

<p><strong>Approach:</strong> Use <strong>React Hook Form</strong> + <strong>Zod</strong> &mdash; the 2026 standard. Zod schemas declare both shape and messages; types and runtime validation share one source. Custom messages for each rule; async validation for server-checked rules.</p>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const signupSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address")
    .endsWith(".com", "Sorry, only .com email addresses are allowed for now")
    .refine(
      async (val) =&gt; {
        if (!val.includes("@")) return true;   // skip if invalid format
        const taken = await api.checkEmailTaken(val);
        return !taken;
      },
      { message: "This email is already registered" }
    ),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password is too long")
    .regex(/[A-Z]/, "Password must include at least one uppercase letter")
    .regex(/[0-9]/, "Password must include at least one number")
    .regex(/[^A-Za-z0-9]/, "Password must include a special character"),
  confirmPassword: z.string(),
  age: z
    .number({ invalid_type_error: "Please enter a number" })
    .int("Age must be a whole number")
    .min(13, "You must be at least 13 to sign up")
    .max(120, "Please enter a valid age")
}).refine((data) =&gt; data.password === data.confirmPassword, {
  message: "Passwords don&rsquo;t match",
  path: ["confirmPassword"]
});

type SignupForm = z.infer&lt;typeof signupSchema&gt;;

function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError
  } = useForm&lt;SignupForm&gt;({
    resolver: zodResolver(signupSchema),
    mode: "onBlur",       // validate on blur; not on every keystroke
    reValidateMode: "onChange"   // re-validate on change after first error
  });

  const onSubmit = async (data: SignupForm) =&gt; {
    try {
      await api.signup(data);
    } catch (err) {
      if (err.field) {
        // Map server-side validation errors to fields
        setError(err.field, { type: "server", message: err.message });
      } else {
        setError("root", { type: "server", message: err.message || "Signup failed" });
      }
    }
  };

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)} noValidate&gt;
      &lt;Field
        label="Email"
        error={errors.email?.message}
        {...register("email")}
      /&gt;
      &lt;Field
        label="Password"
        type="password"
        error={errors.password?.message}
        helperText="At least 8 characters, with uppercase, number, and symbol"
        {...register("password")}
      /&gt;
      &lt;Field
        label="Confirm password"
        type="password"
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      /&gt;
      &lt;Field
        label="Age"
        type="number"
        error={errors.age?.message}
        {...register("age", { valueAsNumber: true })}
      /&gt;

      {errors.root &amp;&amp; (
        &lt;div role="alert" className="form-error"&gt;
          {errors.root.message}
        &lt;/div&gt;
      )}

      &lt;button disabled={isSubmitting}&gt;
        {isSubmitting ? "Creating account..." : "Sign up"}
      &lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Field component &mdash; reusable accessible primitive:</strong></p>

<pre><code>const Field = forwardRef&lt;HTMLInputElement, FieldProps&gt;(
  ({ label, error, helperText, ...inputProps }, ref) =&gt; {
    const id = useId();
    const errorId = `${id}-error`;
    const helperId = `${id}-helper`;

    return (
      &lt;div className="field"&gt;
        &lt;label htmlFor={id}&gt;{label}&lt;/label&gt;
        &lt;input
          {...inputProps}
          ref={ref}
          id={id}
          aria-invalid={!!error}
          aria-describedby={[error &amp;&amp; errorId, helperText &amp;&amp; helperId].filter(Boolean).join(" ") || undefined}
        /&gt;
        {helperText &amp;&amp; !error &amp;&amp; &lt;p id={helperId} className="helper"&gt;{helperText}&lt;/p&gt;}
        {error &amp;&amp; &lt;p id={errorId} role="alert" className="error"&gt;{error}&lt;/p&gt;}
      &lt;/div&gt;
    );
  }
);</code></pre>

<p><strong>Validation timing strategies:</strong></p>

<table>
  <tr><th>Mode</th><th>When validates</th><th>Best for</th></tr>
  <tr><td>onSubmit</td><td>Only on submit</td><td>Short forms; least intrusive</td></tr>
  <tr><td>onBlur</td><td>When field loses focus</td><td>Default for most forms; balanced</td></tr>
  <tr><td>onChange</td><td>Every keystroke</td><td>Annoying for unfilled fields; OK after first error</td></tr>
  <tr><td>onTouched</td><td>onBlur first, then onChange</td><td>Sweet spot; most users prefer this</td></tr>
</table>

<p><strong>Error message principles:</strong></p>

<table>
  <tr><th>Bad</th><th>Good</th></tr>
  <tr><td>"Invalid"</td><td>"Email must include @ and a domain"</td></tr>
  <tr><td>"Required"</td><td>"Please enter your email"</td></tr>
  <tr><td>"Error 422"</td><td>"This username is already taken &mdash; try another"</td></tr>
  <tr><td>"Password failed"</td><td>"Password must include at least one number"</td></tr>
  <tr><td>"Field error"</td><td>"Phone number must be 10 digits with no spaces"</td></tr>
</table>

<p><strong>i18n with Zod:</strong></p>

<pre><code>// Messages as translation keys; resolve in renderer
const schema = z.object({
  email: z.string().email("errors.invalidEmail")
});

// In Field component
{error &amp;&amp; &lt;p&gt;{t(error)}&lt;/p&gt;}

// Or use zod-i18n-map for full integration
import { zodI18nMap } from "zod-i18n-map";
import i18next from "i18next";
z.setErrorMap(zodI18nMap);   // all default errors translated</code></pre>

<p><strong>Server-side validation must mirror client</strong>: never trust client validation alone. Use the same Zod schema on the server (Node.js) for guaranteed parity, or use a different validator if backend is in another language &mdash; just keep rules in sync. Server returns field-keyed errors; client maps them to <code>setError(field, ...)</code>.</p>

<p><strong>Trade-offs:</strong> Zod + React Hook Form is the production sweet spot &mdash; declarative schemas, custom messages, async validation, full TypeScript inference, server-side reuse. Alternatives: Yup (older but mature), Valibot (lighter weight), AJV (JSON Schema standard). <strong>Don&rsquo;t over-validate</strong>: too many rules ("must contain a special character but not these specific ones, length 9-15, no consecutive identical chars") frustrate users and don&rsquo;t add security. The CISA / NIST 2024+ guidance is "longer is better than complex" &mdash; let users pick passwords they can remember; use <code>haveibeenpwned</code> API to block known-breached passwords instead. <strong>Async validation UX</strong>: show "Checking..." indicator during async checks (email-taken, username-available); debounce 500ms so it doesn&rsquo;t fire on every keystroke; cancel in-flight checks when input changes. <strong>Accessibility</strong>: <code>aria-invalid</code>, <code>aria-describedby</code> linking to error message, <code>role="alert"</code> for errors that appear, focus the first error after failed submit, never rely solely on color (red text + icon + label change). <strong>Don&rsquo;t reveal too much</strong>: "Email or password incorrect" beats "Password incorrect" (the latter confirms the email exists, useful to attackers).</p>
'''
