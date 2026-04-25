"""Python · Advanced · Detailed answers. Each value is an HTML snippet."""

ANSWERS = {}

ANSWERS[1] = r'''
<p>The <strong>GIL</strong> is a mutex in CPython that ensures only one thread executes Python bytecode at a time — even on multi-core CPUs. It simplifies memory management (reference counting becomes trivially thread-safe) but limits true parallelism for CPU-bound Python code.</p>
<p>Consequences:</p>
<ul>
  <li><strong>CPU-bound threaded code</strong> runs no faster (often slower) than single-threaded — threads take turns holding the GIL.</li>
  <li><strong>I/O-bound threaded code</strong> works fine — the GIL is released during blocking I/O calls (file, network, sleep).</li>
  <li><strong>Workarounds</strong> — <code>multiprocessing</code> (each process has its own GIL), native extensions that release the GIL (NumPy, PyTorch), or <code>asyncio</code>.</li>
</ul>
<pre><code># Check if GIL is held
import sys
sys.getswitchinterval()    # 0.005 — how often threads rotate</code></pre>
<p>Python 3.13 introduced an optional <strong>free-threaded build</strong> (<code>python3.13t</code>) that removes the GIL. It's a long-term ongoing change — most C extensions still need rebuilding. Jython, IronPython, and PyPy-STM don't have a GIL.</p>
'''

ANSWERS[2] = r'''
<p>Python performance optimization is layered — measure first, attack the biggest offender.</p>
<ol>
  <li><strong>Profile</strong> with <code>cProfile</code> or <code>py-spy</code>; never guess.</li>
  <li><strong>Better algorithms</strong> beat micro-optimization every time — O(n log n) vs O(n²) dwarfs any constant-factor tweak.</li>
  <li><strong>Built-ins and stdlib are C</strong> — <code>sum()</code>, <code>map()</code>, <code>set()</code>, <code>heapq</code>, <code>bisect</code> outperform hand-written loops.</li>
  <li><strong>Use the right data structure</strong> — <code>set</code>/<code>dict</code> lookup is O(1), <code>list</code> is O(n).</li>
  <li><strong>Avoid repeated work</strong> — cache with <code>@lru_cache</code>; precompute invariants outside loops.</li>
  <li><strong>Local name binding</strong> — inside hot loops, bind <code>append = lst.append</code> once to skip attribute lookup.</li>
  <li><strong>NumPy vectorization</strong> for numeric work — replaces Python loops with C.</li>
  <li><strong>JIT or compile</strong> — PyPy (drop-in), Cython, mypyc, Numba for tight numeric code.</li>
  <li><strong>Offload</strong> — Rust/C extensions, GPU, or a different process entirely.</li>
</ol>
<p>Don't optimize prematurely: readable Python that's fast enough beats clever Python that's unmaintainable.</p>
'''

ANSWERS[3] = r'''
<p>A <strong>decorator</strong> is a callable that takes a function and returns a replacement function — a way to add behavior without modifying the original. The <code>@decorator</code> syntax is sugar for <code>func = decorator(func)</code>.</p>
<pre><code>from functools import wraps
import time

def timing(fn):
    @wraps(fn)                  # preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{fn.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@timing
def slow(n):
    time.sleep(n)
    return n

slow(0.5)    # "slow took 0.501s" → 0.5</code></pre>
<p>Always use <code>@functools.wraps</code> — without it, the decorated function loses its name, docstring, and signature, breaking introspection and documentation tools.</p>
<p>Common uses: caching, timing, logging, access control, retry, registration in a catalog. Class-based decorators are useful when you need state; decorator factories (decorators with arguments) add a level of nesting — see Q65.</p>
'''

ANSWERS[4] = r'''
<table>
  <thead><tr><th></th><th>Synchronous</th><th>Asynchronous</th></tr></thead>
  <tbody>
    <tr><td>Execution</td><td>Blocks until work completes</td><td>Yields control; resumes when work is ready</td></tr>
    <tr><td>Concurrency model</td><td>Threads or processes</td><td>Single-threaded event loop</td></tr>
    <tr><td>Scales to</td><td>Hundreds of connections</td><td>Tens of thousands</td></tr>
    <tr><td>Code complexity</td><td>Simple, linear</td><td>Requires <code>async/await</code> discipline</td></tr>
    <tr><td>CPU-bound work</td><td>Fine</td><td>Blocks the loop — offload to executor</td></tr>
  </tbody>
</table>
<pre><code># Sync — each fetch blocks
import requests
for url in urls:
    r = requests.get(url)

# Async — fetches overlap
import asyncio, aiohttp
async def fetch_all(urls):
    async with aiohttp.ClientSession() as s:
        return await asyncio.gather(*[s.get(u) for u in urls])</code></pre>
<p>Async shines for <strong>I/O-bound workloads</strong>: many connections waiting on network. It does not help CPU-bound work — the GIL still applies. Functions are "colored": async and sync can't interop freely. Mixing them requires <code>asyncio.run()</code> at the top or <code>asyncio.to_thread()</code> to bridge.</p>
'''

ANSWERS[5] = r'''
<p><code>asyncio</code> provides the event loop, coroutines, and primitives for concurrent I/O in a single thread.</p>
<pre><code>import asyncio

async def fetch(url: str) -&gt; str:
    print(f"start {url}")
    await asyncio.sleep(1)       # non-blocking — other tasks run meanwhile
    return f"data from {url}"

async def main():
    # Run concurrently
    results = await asyncio.gather(
        fetch("a"), fetch("b"), fetch("c"),
    )
    print(results)

    # Or with timeout
    try:
        await asyncio.wait_for(fetch("slow"), timeout=0.5)
    except asyncio.TimeoutError:
        print("timed out")

asyncio.run(main())</code></pre>
<p>Core concepts:</p>
<ul>
  <li><strong>Coroutine</strong> — an <code>async def</code> function; calling it returns a coroutine object, not a result. Must be awaited or run.</li>
  <li><strong>Task</strong> — a coroutine scheduled on the loop (<code>asyncio.create_task()</code>).</li>
  <li><strong>Event loop</strong> — rotates between ready tasks; <code>await</code> yields control.</li>
  <li><strong>Cancellation</strong> — tasks can be cancelled via <code>.cancel()</code>.</li>
</ul>
<p>Common pitfalls: calling a sync blocking function inside async code freezes everything; use <code>asyncio.to_thread(sync_fn)</code>. Avoid <code>asyncio.sleep()</code>'s sync cousin <code>time.sleep()</code>.</p>
'''

ANSWERS[6] = r'''
<p>A <strong>metaclass</strong> is the class of a class — it controls how classes themselves are created. Regular classes are instances of <code>type</code>; custom metaclasses subclass <code>type</code>.</p>
<pre><code>class LoggedMeta(type):
    def __new__(mcs, name, bases, namespace):
        # Wrap all methods with logging
        for key, value in namespace.items():
            if callable(value) and not key.startswith("_"):
                namespace[key] = log_calls(value)
        return super().__new__(mcs, name, bases, namespace)

class Service(metaclass=LoggedMeta):
    def process(self, x):
        return x * 2

Service().process(5)    # prints "Service.process called with (5,)"</code></pre>
<p>Real-world uses:</p>
<ul>
  <li><strong>ORMs</strong> — Django's <code>Model</code>, SQLAlchemy's declarative base build column definitions at class-creation time.</li>
  <li><strong>ABCs</strong> — <code>ABCMeta</code> enforces abstract-method implementation.</li>
  <li><strong>Registry patterns</strong> — auto-register subclasses in a catalog.</li>
</ul>
<p>Tim Peters famously said: "Metaclasses are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don't." Modern Python often uses <code>__init_subclass__</code> or decorators to achieve the same effect with less friction.</p>
'''

ANSWERS[7] = r'''
<p><code>functools</code> provides higher-order utilities for callable objects.</p>
<table>
  <thead><tr><th>Function</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>reduce</code></td><td>Fold an iterable into a single value</td></tr>
    <tr><td><code>partial</code></td><td>Pre-supply some arguments to a function</td></tr>
    <tr><td><code>lru_cache</code></td><td>Memoize recent calls</td></tr>
    <tr><td><code>cache</code></td><td>Unbounded memoization (3.9+)</td></tr>
    <tr><td><code>cached_property</code></td><td>Compute-once instance property</td></tr>
    <tr><td><code>wraps</code></td><td>Copy metadata onto a decorator's wrapper</td></tr>
    <tr><td><code>singledispatch</code></td><td>Dispatch by argument type</td></tr>
    <tr><td><code>total_ordering</code></td><td>Derive all comparison operators from __lt__ and __eq__</td></tr>
  </tbody>
</table>
<pre><code>from functools import reduce, partial, lru_cache, cached_property

reduce(lambda a, b: a + b, [1, 2, 3, 4])   # 10
add5 = partial(lambda x, y: x + y, 5)
add5(10)                                    # 15

@lru_cache(maxsize=128)
def expensive(n):
    ...

class Model:
    @cached_property
    def loaded(self):
        return load_from_disk()</code></pre>
<p>Skip <code>reduce</code> for simple sums/products — <code>sum()</code>, <code>math.prod()</code> are clearer. Use <code>partial</code> liberally — it's essential for dependency injection patterns.</p>
'''

ANSWERS[8] = r'''
<p><code>partial</code> creates a new callable with some arguments pre-filled. Useful for specializing general-purpose functions.</p>
<pre><code>from functools import partial

# Pre-fill the base
int2 = partial(int, base=2)
int2("1011")         # 11

# Create typed variants
from decimal import Decimal
to_dollars = partial(Decimal, "0.01")

# Event handlers that need extra context
def on_click(user_id, event):
    print(f"User {user_id} clicked at {event}")

button.bind(partial(on_click, current_user.id))

# Partial vs lambda
add = lambda x, y: x + y
add5_lambda = lambda y: add(5, y)
add5_partial = partial(add, 5)</code></pre>
<p><strong>Advantages over lambdas:</strong></p>
<ul>
  <li>Picklable (lambdas aren't) — works with <code>multiprocessing</code>.</li>
  <li>Preserves introspection (<code>.__name__</code>, <code>.args</code>, <code>.keywords</code>).</li>
  <li>Slightly faster — no Python frame overhead.</li>
</ul>
<p>Related: <code>functools.partialmethod</code> for pre-filling the <code>self</code>-bound version inside a class body. Use <code>partial</code> when you're genuinely fixing arguments; prefer <code>lambda</code> for trivial one-liners where readability trumps pickling.</p>
'''

ANSWERS[9] = r'''
<p><code>@lru_cache</code> memoizes function calls. It stores up to <code>maxsize</code> results, keyed by the argument tuple; new calls evict the least-recently-used entry.</p>
<pre><code>from functools import lru_cache

@lru_cache(maxsize=256)
def fib(n):
    return n if n &lt; 2 else fib(n-1) + fib(n-2)

fib(100)                    # instant
fib.cache_info()            # CacheInfo(hits=98, misses=101, maxsize=256, currsize=101)
fib.cache_clear()           # reset

# Unbounded — Python 3.9+
from functools import cache
@cache
def pure_fn(x): ...</code></pre>
<p>Requirements:</p>
<ul>
  <li><strong>Arguments must be hashable</strong> — no dicts, lists, sets as args. Use tuples instead.</li>
  <li><strong>Function should be pure</strong> — same input always produces same output. Memoizing impure functions returns stale results.</li>
  <li><strong>Instance methods</strong> — beware: <code>self</code> becomes part of the cache key, leaking memory. Use <code>@cached_property</code> or a <code>WeakValueDictionary</code> instead.</li>
</ul>
<p>Internally, it's a thread-safe dict + doubly-linked list for LRU tracking. Extremely fast — often the difference between a 10-second and 10-millisecond algorithm.</p>
'''

ANSWERS[10] = r'''
<p>Context managers handle setup and teardown through the <code>with</code> statement — guaranteeing cleanup even on exceptions.</p>
<pre><code># Built-in examples
with open("file.txt") as f:                    # file auto-closed
    content = f.read()

with threading.Lock():                          # lock auto-released
    shared_resource.modify()

with contextlib.suppress(FileNotFoundError):    # errors silently ignored
    os.remove("maybe_gone.txt")

# Multiple contexts (Python 3.1+)
with open("in.txt") as fin, open("out.txt", "w") as fout:
    fout.write(fin.read())</code></pre>
<p>The protocol: <code>__enter__()</code> runs at the top of <code>with</code>; <code>__exit__(exc_type, exc_val, exc_tb)</code> runs at the end, even if an exception occurred. Returning True from <code>__exit__</code> suppresses the exception.</p>
<p>Use context managers for:</p>
<ul>
  <li>Resources needing release: files, sockets, database connections, locks.</li>
  <li>Transactional scopes: DB transactions, undo stacks.</li>
  <li>Temporary state: changing working directory, setting logging level.</li>
  <li>Instrumentation: timing a block of code.</li>
</ul>
<p>Prefer <code>with</code> over <code>try/finally</code> — it centralizes the cleanup policy in the resource, not the caller.</p>
'''

ANSWERS[11] = r'''
<p><code>contextlib.contextmanager</code> turns a generator into a context manager — much less boilerplate than a full class.</p>
<pre><code>from contextlib import contextmanager
import time

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")

with timer("load data"):
    load_huge_file()
# "load data: 2.341s"

# With a yielded value
@contextmanager
def atomic_update(filepath):
    tmp = filepath + ".tmp"
    with open(tmp, "w") as f:
        yield f
    os.replace(tmp, filepath)       # atomic on POSIX

with atomic_update("config.json") as f:
    json.dump(new_config, f)</code></pre>
<p>Structure: code before <code>yield</code> is setup (<code>__enter__</code>); code after is teardown (<code>__exit__</code>); wrap teardown in <code>try/finally</code> to run on exceptions too. Whatever you <code>yield</code> becomes the <code>as</code> target.</p>
<p>For reusing the same context across contexts, use <code>contextlib.ContextDecorator</code> to allow both <code>with</code> usage and decorator usage with the same object.</p>
'''

ANSWERS[12] = r'''
<p><code>yield from</code> delegates iteration to a sub-generator. It's shorthand for a loop, plus it properly propagates <code>send()</code>, <code>throw()</code>, and return values from the inner generator.</p>
<pre><code># Without yield from — verbose, loses advanced semantics
def outer():
    for value in inner():
        yield value

# With yield from — cleaner AND correct for coroutines
def outer():
    yield from inner()

# Flatten nested iterables
def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3, 4]], [5]]))    # [1, 2, 3, 4, 5]

# Capture a generator's return value
def subgen():
    yield 1; yield 2
    return "done"

def main():
    result = yield from subgen()
    print(result)     # "done" — only accessible via yield from</code></pre>
<p>Introduced in PEP 380 (Python 3.3). Before <code>asyncio</code> moved to <code>async/await</code>, <code>yield from</code> was the primary way to chain coroutines. Today it's mostly used for generator composition and recursive tree traversals.</p>
'''

ANSWERS[13] = r'''
<p><code>itertools</code> provides memory-efficient iterator building blocks, all implemented in C.</p>
<pre><code>from itertools import (
    count, cycle, repeat,                   # infinite
    chain, zip_longest, product,             # combining
    combinations, permutations,              # combinatoric
    groupby, takewhile, dropwhile,           # filtering
    islice, tee, starmap, accumulate,        # transforming
)

# Infinite
list(islice(count(start=10, step=2), 5))     # [10, 12, 14, 16, 18]

# Cartesian product
list(product([1, 2], ['a', 'b']))
# [(1,'a'), (1,'b'), (2,'a'), (2,'b')]

# Accumulate — running totals / folds
list(accumulate([1, 2, 3, 4]))               # [1, 3, 6, 10]
list(accumulate([1, 2, 3, 4], max))          # [1, 2, 3, 4]

# Flatten one level
list(chain([1, 2], [3, 4], [5]))             # [1, 2, 3, 4, 5]

# Sliding window (3.10+)
from itertools import pairwise
list(pairwise([1, 2, 3, 4]))                 # [(1,2), (2,3), (3,4)]</code></pre>
<p>Everything returns an iterator — lazy evaluation lets you work with infinite streams. Always materialize to a list only when needed. The <a href="https://docs.python.org/3/library/itertools.html#itertools-recipes">itertools recipes</a> section in the docs has many more composable patterns worth reading.</p>
'''

ANSWERS[14] = r'''
<p><code>chain</code> flattens multiple iterables into one sequential iterator — like concatenation, but lazy.</p>
<pre><code>from itertools import chain

list(chain([1, 2], (3, 4), "xy"))
# [1, 2, 3, 4, 'x', 'y']

# chain.from_iterable — one argument that's an iterable-of-iterables
list(chain.from_iterable([[1, 2], [3, 4], [5]]))
# [1, 2, 3, 4, 5]

# Vs + concatenation for lists
list1 + list2          # allocates a full copy
list(chain(list1, list2))   # lazy — no copy

# Works for heterogeneous iterables
for item in chain(range(3), ["a", "b"], (True, False)):
    print(item)</code></pre>
<p>Performance: O(1) setup, O(1) per item. For just two lists, <code>a + b</code> is typically fine; for many or for streaming, <code>chain</code> wins. <code>chain.from_iterable</code> is the standard way to flatten a single level without writing <code>chain(*iter_of_iters)</code> (which unpacks everything eagerly).</p>
<p>Real use case: combining several iterators over different data sources (database pages, file chunks) without materializing them.</p>
'''

ANSWERS[15] = r'''
<p><code>groupby</code> collapses consecutive equal elements into groups. Critically, it groups <strong>consecutive</strong> items — you usually need to <code>sort</code> first.</p>
<pre><code>from itertools import groupby

data = [("A", 1), ("A", 2), ("B", 3), ("B", 4), ("A", 5)]

# WITHOUT sorting — the second "A" group is separate!
for key, group in groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# A [('A', 1), ('A', 2)]
# B [('B', 3), ('B', 4)]
# A [('A', 5)]              ← separate group because not contiguous

# With sorting first
data.sort(key=lambda x: x[0])
for key, group in groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# A [('A', 1), ('A', 2), ('A', 5)]
# B [('B', 3), ('B', 4)]</code></pre>
<p>Use <code>collections.defaultdict</code> for unordered grouping:</p>
<pre><code>from collections import defaultdict
groups = defaultdict(list)
for k, v in data:
    groups[k].append(v)</code></pre>
<p>Gotcha: the group iterator is <em>shared</em> with the outer loop — advancing <code>groupby</code> invalidates the previous group. Always materialize with <code>list()</code> if you need to store groups.</p>
'''

ANSWERS[16] = r'''
<p>A <strong>coroutine</strong> is a function that can suspend and resume execution. Modern Python has two kinds:</p>
<ul>
  <li><strong>Native coroutines</strong> (3.5+) — <code>async def</code> functions used with <code>await</code>.</li>
  <li><strong>Generator-based coroutines</strong> — historical, built on <code>yield</code>/<code>yield from</code>.</li>
</ul>
<pre><code># Native coroutine
import asyncio

async def fetch(url):
    await asyncio.sleep(1)     # yields control to the event loop
    return f"data from {url}"

async def main():
    # Run sequentially
    a = await fetch("a")
    b = await fetch("b")
    # Run concurrently — both fetches overlap
    a, b = await asyncio.gather(fetch("a"), fetch("b"))

asyncio.run(main())</code></pre>
<p>Coroutines are <strong>not functions</strong> — calling <code>fetch("a")</code> returns a coroutine object; it only runs when <code>await</code>ed or scheduled on an event loop.</p>
<p>Mental model: <code>await expr</code> means "run this to completion, yielding the event loop meanwhile, and resume when done." The event loop rotates between ready coroutines; blocked ones wait. This model is <em>cooperative</em> — a coroutine must <code>await</code> regularly or it monopolizes the loop.</p>
'''

ANSWERS[17] = r'''
<p>Python threads share memory and run in one process. Because of the GIL, threads don't give you CPU parallelism — but they <strong>do</strong> give you concurrency for I/O.</p>
<pre><code>from concurrent.futures import ThreadPoolExecutor
import requests

def fetch(url):
    return requests.get(url).status_code

# Modern idiom — ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch, urls))

# Lower-level threading module
import threading
results = {}
def worker(url):
    results[url] = requests.get(url).status_code

threads = [threading.Thread(target=worker, args=(u,)) for u in urls]
for t in threads: t.start()
for t in threads: t.join()</code></pre>
<p>Threading concerns:</p>
<ul>
  <li><strong>Race conditions</strong> — use <code>threading.Lock()</code> or <code>RLock</code> for shared mutable state.</li>
  <li><strong>Deadlocks</strong> — always acquire locks in a consistent order.</li>
  <li><strong>GIL</strong> — no CPU parallelism for pure Python. For numeric work, use NumPy (releases GIL in C code).</li>
  <li><strong>Exception handling</strong> — exceptions in threads don't propagate to the main thread unless you check <code>future.result()</code>.</li>
</ul>
<p>For CPU-bound work, use <code>multiprocessing</code> instead. For async I/O at higher scale, <code>asyncio</code> is more efficient than threads.</p>
'''

ANSWERS[18] = r'''
<p><code>multiprocessing</code> spawns separate OS processes, each with its own Python interpreter and GIL. This gives true CPU parallelism at the cost of higher overhead than threads (process startup, data serialization).</p>
<pre><code>from concurrent.futures import ProcessPoolExecutor

def compute(n):
    return sum(i * i for i in range(n))

with ProcessPoolExecutor() as executor:
    results = list(executor.map(compute, [10**6, 10**7, 10**8]))

# Lower-level — multiprocessing.Pool
from multiprocessing import Pool
with Pool(processes=4) as pool:
    results = pool.map(compute, inputs)

# Queues for IPC
from multiprocessing import Process, Queue
def worker(in_q, out_q):
    while (item := in_q.get()) is not None:
        out_q.put(process(item))</code></pre>
<p>Key caveats:</p>
<ul>
  <li><strong>Data is pickled</strong> between processes — heavy objects or unpicklable things (lambdas, local classes) fail.</li>
  <li><strong>Startup is expensive</strong> — reuse a <code>Pool</code> rather than spawning per task.</li>
  <li><strong>Memory</strong> — each process has its own copy; for huge read-only data, use <code>multiprocessing.shared_memory</code> or memory-mapped files.</li>
  <li><strong>Windows spawn method</strong> requires <code>if __name__ == "__main__":</code> guard around the entry point.</li>
</ul>
<p>Use multiprocessing for CPU-bound work where input/output is modest and work is substantial.</p>
'''

ANSWERS[19] = r'''
<table>
  <thead><tr><th></th><th>Threading</th><th>Multiprocessing</th></tr></thead>
  <tbody>
    <tr><td>Memory</td><td>Shared (one process)</td><td>Separate per process</td></tr>
    <tr><td>Communication</td><td>Shared state + locks</td><td>Pickle + IPC (Queue, Pipe)</td></tr>
    <tr><td>GIL</td><td>Held by one thread at a time</td><td>One per process — true parallelism</td></tr>
    <tr><td>Startup cost</td><td>Cheap (μs)</td><td>Expensive (ms)</td></tr>
    <tr><td>Crashes</td><td>Takes down the process</td><td>Isolated — one worker can die safely</td></tr>
    <tr><td>Best for</td><td>I/O-bound concurrency</td><td>CPU-bound parallelism</td></tr>
  </tbody>
</table>
<pre><code># Rule of thumb:
# Is the work waiting on I/O (network, disk)?   → threads or asyncio
# Is the work crunching numbers/data?           → multiprocessing
# Tens of thousands of concurrent connections?  → asyncio
# Mixed? Use ProcessPoolExecutor for CPU chunks
# called from an async main loop via run_in_executor</code></pre>
<p>A common pattern: <code>asyncio</code> + <code>ProcessPoolExecutor</code>. The event loop handles I/O; CPU-heavy tasks are dispatched to worker processes via <code>loop.run_in_executor</code>. Best of both worlds — scalable I/O and real parallelism.</p>
'''

ANSWERS[20] = r'''
<p><code>subprocess</code> spawns external processes. Modern code should use <code>subprocess.run()</code>, not the older <code>os.system()</code> or <code>os.popen()</code>.</p>
<pre><code>import subprocess

# Simple case — run and capture output
result = subprocess.run(
    ["ls", "-la", "/tmp"],
    capture_output=True,
    text=True,
    check=True,               # raises CalledProcessError on non-zero exit
)
print(result.stdout)
print(result.returncode)

# With timeout
try:
    subprocess.run(["slow-tool"], timeout=10)
except subprocess.TimeoutExpired:
    ...

# Pipe commands together
p1 = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
p2 = subprocess.run(["grep", "py"], stdin=p1.stdout, capture_output=True, text=True)

# NEVER use shell=True with user input — shell injection risk
subprocess.run(f"echo {user_input}", shell=True)   # DANGEROUS
subprocess.run(["echo", user_input])               # Safe</code></pre>
<p>Best practices:</p>
<ul>
  <li><strong>Pass args as a list</strong>, not a string — avoids shell injection.</li>
  <li><strong>Avoid <code>shell=True</code></strong> unless you genuinely need shell features (globs, redirects).</li>
  <li><strong>Always set <code>timeout=</code></strong> for external commands that might hang.</li>
  <li><strong>Use <code>check=True</code></strong> or inspect <code>returncode</code> — silent failures are bugs.</li>
</ul>
<p>For async subprocess management, <code>asyncio.create_subprocess_exec</code> integrates with the event loop.</p>
'''

ANSWERS[21] = r'''
<p><code>selectors</code> provides a portable I/O multiplexer — the backbone of many event loops. It lets a single thread monitor many file descriptors (sockets, pipes) for readiness.</p>
<pre><code>import selectors
import socket

sel = selectors.DefaultSelector()       # picks best backend: epoll/kqueue/poll/select

def accept(sock, mask):
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, handle_client)

def handle_client(conn, mask):
    data = conn.recv(1024)
    if data:
        conn.send(data)                  # echo
    else:
        sel.unregister(conn)
        conn.close()

server = socket.socket()
server.bind(("127.0.0.1", 5000))
server.listen()
server.setblocking(False)
sel.register(server, selectors.EVENT_READ, accept)

while True:
    for key, mask in sel.select():       # blocks until any fd is ready
        key.data(key.fileobj, mask)</code></pre>
<p><code>DefaultSelector</code> picks the best available: <strong>epoll</strong> (Linux), <strong>kqueue</strong> (macOS/BSD), <strong>devpoll</strong> (Solaris), <strong>poll</strong>, or <strong>select</strong> as fallback. Scales to tens of thousands of connections without per-connection threads.</p>
<p>In practice, use <code>asyncio</code> for modern async code — it uses <code>selectors</code> internally but exposes a nicer coroutine-based API. Raw <code>selectors</code> is useful when you need low-level control or integration with custom event loops.</p>
'''

ANSWERS[22] = r'''
<p><code>signal</code> lets a process handle OS signals (Ctrl+C, termination requests, user-defined).</p>
<pre><code>import signal
import time

def shutdown(signum, frame):
    print(f"Got signal {signum}; cleaning up")
    # Do cleanup, then re-raise or sys.exit
    raise SystemExit(0)

signal.signal(signal.SIGINT,  shutdown)    # Ctrl+C
signal.signal(signal.SIGTERM, shutdown)    # kill

# Custom alarm — for timeouts
def timeout_handler(signum, frame):
    raise TimeoutError

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)                  # fire SIGALRM in 5 seconds
try:
    long_running_task()
finally:
    signal.alarm(0)              # cancel</code></pre>
<p>Rules and limitations:</p>
<ul>
  <li><strong>Only the main thread can register handlers.</strong></li>
  <li><strong>Handlers are async-signal-unsafe</strong> in general — keep them minimal (set a flag, exit).</li>
  <li><strong>Windows support is limited</strong> — <code>SIGALRM</code> is not available; use a threading timer instead.</li>
  <li><strong>Python's default Ctrl+C behavior</strong> is to raise <code>KeyboardInterrupt</code>. Override with care.</li>
</ul>
<p>For graceful shutdown in servers, signals are the standard mechanism — SIGTERM to request shutdown, SIGKILL (can't be caught) as a last resort.</p>
'''

ANSWERS[23] = r'''
<p>ABCs define interfaces — classes that declare abstract methods subclasses must implement. Use <code>abc.ABC</code> as a base and <code>@abstractmethod</code> on required methods.</p>
<pre><code>from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, key: str, value: bytes) -&gt; None: ...

    @abstractmethod
    def load(self, key: str) -&gt; bytes: ...

    def save_json(self, key, obj):         # concrete method — inherited freely
        self.save(key, json.dumps(obj).encode())

class S3Storage(Storage):
    def save(self, key, value): ...         # required
    def load(self, key): ...                # required

Storage()            # TypeError — can't instantiate abstract class
S3Storage().save_json("k", {"a": 1})        # OK</code></pre>
<p>ABCs also enable <strong>virtual subclassing</strong> — marking a class as conforming to the interface without inheriting, via <code>@Storage.register(MyClass)</code> or <code>__subclasshook__</code>.</p>
<p>When to reach for ABCs:</p>
<ul>
  <li>Multiple concrete implementations of a clear interface (storage backends, serializers).</li>
  <li>Library APIs where consumers implement your protocol.</li>
  <li>Teaching/enforcing a contract at class creation time.</li>
</ul>
<p>For lighter-weight interfaces, consider <code>typing.Protocol</code> (structural typing — no inheritance needed).</p>
'''

ANSWERS[24] = r'''
<p><code>@dataclass</code> auto-generates <code>__init__</code>, <code>__repr__</code>, and optionally <code>__eq__</code>, <code>__hash__</code>, comparisons, from type-annotated class attributes.</p>
<pre><code>from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True, slots=True)
class User:
    id: int
    name: str
    email: str
    roles: List[str] = field(default_factory=list)
    joined_at: str = "unknown"

u = User(1, "Ana", "a@b.c", roles=["admin"])
u.name                      # "Ana"
print(u)                    # User(id=1, name='Ana', email='a@b.c', roles=['admin'], joined_at='unknown')
u == User(1, "Ana", "a@b.c", roles=["admin"])   # True — structural equality</code></pre>
<p>Key parameters:</p>
<ul>
  <li><code>frozen=True</code> — immutable (and hashable).</li>
  <li><code>slots=True</code> (3.10+) — uses <code>__slots__</code> for lower memory footprint.</li>
  <li><code>order=True</code> — adds <code>__lt__</code>, <code>__le__</code>, etc.</li>
  <li><code>kw_only=True</code> (3.10+) — all fields are keyword-only.</li>
</ul>
<p>Use <code>field(default_factory=...)</code> for mutable defaults to avoid the classic shared-mutable-default bug. For data transfer objects and model classes, <code>dataclass</code> has largely replaced hand-written constructors. Alternatives: <code>attrs</code> (predecessor, more features), <code>pydantic</code> (runtime validation, JSON serialization).</p>
'''

ANSWERS[25] = r'''
<p>A singleton allows only one instance. Python has several idioms.</p>
<pre><code># 1. Module-level — simplest and most Pythonic
# config.py
SETTINGS = load_config()          # module = singleton

# 2. __new__ override
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# 3. Metaclass
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DBPool(metaclass=SingletonMeta):
    pass

# 4. Decorator
def singleton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper</code></pre>
<p>Thread safety: all the patterns above have race conditions. Use a <code>threading.Lock()</code> around instance creation, or use module-level initialization (handled by Python's import system, which is thread-safe).</p>
<p><strong>Reconsider before using</strong>: singletons are global state in disguise — they hurt testability and obscure dependencies. Prefer dependency injection or module-level instances that can be swapped for tests.</p>
'''

ANSWERS[26] = r'''
<p><strong>Monkey patching</strong> replaces attributes or methods at runtime. Python's dynamic model makes it trivial — and dangerous.</p>
<pre><code>import json

# Replace a function
_original_dumps = json.dumps
def safe_dumps(obj, **kw):
    kw.setdefault("default", str)
    return _original_dumps(obj, **kw)
json.dumps = safe_dumps

# Patch a class method
class User: pass
def greet(self): return f"Hi, {self.name}"
User.greet = greet

# Mock for testing — legitimate use
from unittest.mock import patch
with patch("requests.get") as mock_get:
    mock_get.return_value.status_code = 200
    # Call code that uses requests.get</code></pre>
<p>Legitimate uses:</p>
<ul>
  <li><strong>Testing</strong> — <code>unittest.mock.patch</code> swaps attributes for the test's duration.</li>
  <li><strong>Polyfills</strong> — backporting <code>str.removeprefix</code> on older Python.</li>
  <li><strong>Hot-fixes</strong> — when you can't deploy a patched version immediately.</li>
</ul>
<p>Problems in production: collisions between multiple patches, breakage across library upgrades, invisible behavior changes that break consumer assumptions. Prefer wrappers, subclasses, or dependency injection. Document any surviving patches loudly.</p>
'''

ANSWERS[27] = r'''
<p><code>@property</code> turns a method into a read-only attribute — access triggers computation, but callers see it as a simple attribute. Use it to compute derived values or to add logic behind a public attribute later without breaking callers.</p>
<pre><code>class Celsius:
    def __init__(self, temp):
        self._temp = temp

    @property
    def fahrenheit(self):              # read
        return self._temp * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):       # write
        self._temp = (value - 32) * 5 / 9

    @fahrenheit.deleter
    def fahrenheit(self):              # del
        raise AttributeError("cannot delete")

c = Celsius(100)
c.fahrenheit       # 212.0 — no parens
c.fahrenheit = 32  # setter runs
c._temp            # 0.0</code></pre>
<p>Properties are the standard solution to Java's "private fields + getters/setters" overhead. Start with a plain public attribute; switch to a property only if you need computation or validation later — callers don't need to change.</p>
<p>For expensive computations that should be cached on the instance, use <code>functools.cached_property</code> — computed once, stored on the instance.</p>
'''

ANSWERS[28] = r'''
<p><strong>Descriptors</strong> are objects that implement <code>__get__</code>, <code>__set__</code>, or <code>__delete__</code> and are assigned to <em>class</em> attributes. They control how attribute access is handled — they're the machinery behind <code>@property</code>, methods, <code>@classmethod</code>, <code>@staticmethod</code>, and ORM fields.</p>
<pre><code>class Positive:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value &lt; 0:
            raise ValueError(f"{self.name} must be &gt;= 0")
        instance.__dict__[self.name] = value

class Product:
    price = Positive()
    quantity = Positive()

    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

p = Product(10, 5)
p.price = -1       # ValueError: price must be &gt;= 0</code></pre>
<p>Two flavors:</p>
<ul>
  <li><strong>Data descriptors</strong> (define <code>__set__</code>) — shadow instance <code>__dict__</code>.</li>
  <li><strong>Non-data descriptors</strong> (only <code>__get__</code>) — shadowed by instance <code>__dict__</code>.</li>
</ul>
<p>Real-world uses: SQLAlchemy columns, Django model fields, validation frameworks. Complex but powerful — reach for them when <code>@property</code> isn't reusable enough.</p>
'''

ANSWERS[29] = r'''
<p>A <strong>weak reference</strong> points to an object without incrementing its refcount — it lets the object be garbage collected even while the reference exists. Used for caches, observer lists, and cyclic-reference avoidance.</p>
<pre><code>import weakref

class Resource:
    pass

r = Resource()
ref = weakref.ref(r)        # weak reference
ref()                       # &lt;Resource object&gt; — dereferenced
del r
ref()                       # None — object was collected

# WeakValueDictionary — cache that doesn't keep objects alive
cache = weakref.WeakValueDictionary()
cache["a"] = Resource()
# When no strong references remain, entry disappears

# WeakKeyDictionary — metadata without retaining keys
metadata = weakref.WeakKeyDictionary()
for obj in some_objects:
    metadata[obj] = compute_metadata(obj)
# When obj is collected, its metadata entry goes too

# Callbacks on collection
def on_collected(wr): print("object gone")
ref = weakref.ref(Resource(), on_collected)</code></pre>
<p>Use cases:</p>
<ul>
  <li>Observer pattern — subscribers shouldn't prevent publisher GC.</li>
  <li>Caches that shouldn't retain objects beyond normal lifetime.</li>
  <li>Breaking reference cycles (parent ↔ child) so GC can reclaim.</li>
</ul>
<p>Not every type supports weak refs — <code>list</code>, <code>dict</code>, <code>int</code>, <code>str</code> don't. Custom classes and most stdlib objects do.</p>
'''

ANSWERS[30] = r'''
<p><code>heapq</code> implements a binary heap as a list — the smallest element is always at index 0. Operations are O(log n). It's a <strong>min-heap</strong>; for max-heap, negate keys.</p>
<pre><code>import heapq

# Build from a list in O(n)
nums = [5, 1, 8, 3, 2]
heapq.heapify(nums)
# nums is now a heap: [1, 2, 8, 3, 5]

# Push / pop — O(log n)
heapq.heappush(nums, 0)
heapq.heappop(nums)      # 0 (smallest)

# Push and pop together (slightly faster than separate calls)
heapq.heappushpop(nums, 10)
heapq.heapreplace(nums, 10)

# Get n smallest / largest without sorting whole list
heapq.nsmallest(3, [5, 1, 8, 3, 2])   # [1, 2, 3]
heapq.nlargest(3, [5, 1, 8, 3, 2])    # [8, 5, 3]

# Priority queue with (priority, item) tuples
heap = []
heapq.heappush(heap, (2, "task B"))
heapq.heappush(heap, (1, "task A"))    # higher priority
heapq.heappop(heap)[1]                  # "task A"

# Merge sorted iterables (see itertools Q14)
heapq.merge([1, 4, 7], [2, 3, 8])</code></pre>
<p>Uses: priority queue, k-smallest/largest, Dijkstra's algorithm, streaming top-N, merging k sorted lists in O(N log k). For thread-safe priority queue, use <code>queue.PriorityQueue</code> instead.</p>
'''

ANSWERS[31] = r'''
<p><code>bisect</code> maintains a sorted list with binary-search inserts — O(log n) search, O(n) insert (due to shifting). Essential when you need "insert while keeping sorted" semantics.</p>
<pre><code>import bisect

sorted_list = [1, 3, 5, 7, 9]

# Find insertion point
bisect.bisect_left(sorted_list, 4)      # 2  (where 4 would go)
bisect.bisect_right(sorted_list, 5)     # 3  (just after existing 5)
bisect.bisect(sorted_list, 5)           # same as bisect_right

# Insert while keeping sorted
bisect.insort(sorted_list, 6)
# sorted_list is now [1, 3, 5, 6, 7, 9]

# Use for grade lookup
grades = [60, 70, 80, 90]
letters = "FDCBA"
def grade(score):
    return letters[bisect.bisect(grades, score)]
grade(85)   # "B"

# Find all indices in O(log n)
def find_range(a, x):
    lo = bisect.bisect_left(a, x)
    hi = bisect.bisect_right(a, x)
    return lo, hi</code></pre>
<p>Common algorithmic uses: LIS in O(n log n), count elements in a range, merge-sort-tree queries. For very large insert-heavy workloads, a skip list or balanced BST (via the <code>sortedcontainers</code> package) gives O(log n) inserts instead of O(n).</p>
'''

ANSWERS[32] = r'''
<p>Memoization caches function results keyed by arguments. Python offers several levels of abstraction.</p>
<pre><code>from functools import lru_cache, cache

# Simplest — decorator, bounded cache
@lru_cache(maxsize=128)
def slow(n):
    return expensive_calc(n)

# Unbounded (Python 3.9+)
@cache
def pure(x):
    return calc(x)

# Manual — when arguments aren't hashable
_cache = {}
def memo(args):
    key = json.dumps(args, sort_keys=True)    # serialize to hashable
    if key not in _cache:
        _cache[key] = compute(args)
    return _cache[key]

# For methods — avoid memory leaks by using a class-level cache
class MyClass:
    @lru_cache(maxsize=None)
    def method(self, x):        # self is hashed; all instances leak!
        ...

# Better: cached_property for per-instance one-time computation
from functools import cached_property
class Model:
    @cached_property
    def embedding(self):
        return compute_embedding(self)</code></pre>
<p>Cache invalidation considerations:</p>
<ul>
  <li><strong>Pure functions only</strong> — impure = stale results.</li>
  <li><strong>Hashable arguments</strong> — lists/dicts need conversion.</li>
  <li><strong>Memory bounds</strong> — unbounded caches grow forever; use <code>maxsize</code> in long-running processes.</li>
  <li><strong>Cross-process caching</strong> — use Redis or a disk cache (<code>diskcache</code>).</li>
</ul>
'''

ANSWERS[33] = r'''
<p><code>uuid</code> generates universally unique identifiers — 128-bit values used for IDs that don't need central coordination.</p>
<pre><code>import uuid

# v4 — random (most common)
uuid.uuid4()                    # UUID('c3f4...')
str(uuid.uuid4())               # "c3f4a2b1-..."

# v1 — time + MAC (leaks hostname; rarely used now)
uuid.uuid1()

# v5 — SHA-1 namespace + name (deterministic)
uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")

# UUID v7 (Python 3.14+) — time-ordered, sortable
uuid.uuid7()                    # integrates naturally with DB indexes

# Parse back
u = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
u.hex                           # string without hyphens
u.bytes                         # 16-byte binary
u.int                           # integer form</code></pre>
<p>Pick the right version:</p>
<ul>
  <li><strong>v4</strong> — random; 122 bits of entropy. Collision odds astronomically low. Default for most APIs.</li>
  <li><strong>v5</strong> — deterministic; same name → same UUID. Use when you need reproducible IDs from external identifiers.</li>
  <li><strong>v7</strong> — time-ordered. Better for database primary keys because consecutive rows cluster on the index.</li>
</ul>
<p>For short IDs in URLs, consider nanoid (shorter, URL-safe) or Snowflake IDs (Twitter's approach).</p>
'''

ANSWERS[34] = r'''
<p><code>pickle</code> serializes arbitrary Python objects to bytes — including instances of custom classes, functions, cyclic data.</p>
<pre><code>import pickle

data = {"user": User(1, "Ana"), "tags": ["admin", "dev"], "created": datetime.now()}

# Serialize
blob = pickle.dumps(data)                 # to bytes
with open("data.pkl", "wb") as f:
    pickle.dump(data, f)                  # to file

# Deserialize
restored = pickle.loads(blob)
with open("data.pkl", "rb") as f:
    restored = pickle.load(f)

# Custom __reduce__ for fine control
class Counter:
    def __init__(self, start=0):
        self.n = start
    def __reduce__(self):
        return (Counter, (self.n,))</code></pre>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div><strong>Pickle is unsafe on untrusted input.</strong> Unpickling can execute arbitrary code (<code>__reduce__</code> can return any callable). Never unpickle data from untrusted sources. For cross-language or network data, use JSON, msgpack, or Protocol Buffers.</div>
</div>
<p>Use pickle for: local caches, multiprocessing IPC, saving ML model state, checkpointing. Alternatives for specific cases: <code>joblib</code> for NumPy-heavy data (faster for large arrays), <code>dill</code> for objects pickle can't handle (lambdas, nested classes).</p>
'''

ANSWERS[35] = r'''
<p><code>enum</code> creates named constants grouped under a type — safer and more self-documenting than bare integers or strings.</p>
<pre><code>from enum import Enum, IntEnum, StrEnum, Flag, auto

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

Color.RED           # &lt;Color.RED: 1&gt;
Color.RED.value     # 1
Color.RED.name      # 'RED'
Color(1)            # look up by value
Color["RED"]        # look up by name

# IntEnum — compares as int
class Status(IntEnum):
    OK = 200
    NOT_FOUND = 404
Status.OK == 200    # True

# StrEnum (3.11+) — compares as str
class Method(StrEnum):
    GET = "GET"
    POST = "POST"

# Flag — bitwise combinable
class Permission(Flag):
    READ = auto()     # 1
    WRITE = auto()    # 2
    EXEC = auto()     # 4
    ALL = READ | WRITE | EXEC

p = Permission.READ | Permission.WRITE
Permission.READ in p    # True</code></pre>
<p>Benefits over raw constants:</p>
<ul>
  <li><strong>Type safety</strong> — can't accidentally assign an unrelated int.</li>
  <li><strong>Iteration</strong> — <code>list(Color)</code> gives all members.</li>
  <li><strong>Nice repr</strong> — <code>Color.RED</code> in logs/debugger, not a cryptic 1.</li>
  <li><strong>IDE support</strong> — autocomplete, refactoring.</li>
</ul>
<p>Use <code>@unique</code> to forbid aliases; use <code>auto()</code> to skip numbering.</p>
'''

ANSWERS[36] = r'''
<p><code>logging</code> is Python's structured logging framework — far better than <code>print()</code> for anything beyond quick scripts. Logs go to handlers (files, stdout, syslog), formatted by formatters, filtered by level.</p>
<pre><code>import logging

# Basic — enough for scripts
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)
logger.info("Server starting on port %d", 8080)
logger.error("Connection failed", exc_info=True)      # includes traceback
logger.debug("detailed state: %r", state)</code></pre>
<p>Levels, ascending: <code>DEBUG</code>, <code>INFO</code>, <code>WARNING</code>, <code>ERROR</code>, <code>CRITICAL</code>. Set at <code>WARNING</code> by default.</p>
<p>Best practices:</p>
<ul>
  <li><strong>Use <code>getLogger(__name__)</code></strong> — gives per-module loggers following the package hierarchy.</li>
  <li><strong>Don't f-string messages</strong>: <code>logger.info("x=%s", x)</code> avoids formatting cost when the level is filtered out.</li>
  <li><strong>Structured/JSON logs</strong> for production — use <code>python-json-logger</code> or <code>structlog</code>.</li>
  <li><strong>Configure at entry point</strong>, not in libraries. Libraries just create loggers; apps configure them.</li>
  <li><strong>Always log exceptions with <code>exc_info=True</code></strong> or use <code>logger.exception</code>.</li>
</ul>
<p>For production, ship logs to a central aggregator (CloudWatch, Datadog, Loki, ELK) — don't just write to files.</p>
'''

ANSWERS[37] = r'''
<p>Custom loggers give per-module control over level and destinations. Use <code>dictConfig</code> for declarative, reproducible setup.</p>
<pre><code>import logging
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10_000_000,
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "loggers": {
        "myapp":       {"level": "DEBUG", "handlers": ["console", "file"]},
        "myapp.db":    {"level": "WARNING"},       # quieter
        "urllib3":     {"level": "WARNING"},       # silence noisy deps
    },
    "root": {"level": "WARNING", "handlers": ["console"]},
}
logging.config.dictConfig(LOGGING)</code></pre>
<p>Handlers worth knowing: <code>RotatingFileHandler</code>, <code>TimedRotatingFileHandler</code>, <code>SysLogHandler</code>, <code>SMTPHandler</code> (email alerts), <code>QueueHandler</code> (non-blocking — dispatch via a background thread to avoid slowing request handling). For structured context (user ID, request ID), use <code>LoggerAdapter</code> or <code>contextvars</code>.</p>
'''

ANSWERS[38] = r'''
<p>Type hints annotate variables, arguments, and return types. Python doesn't enforce them at runtime — they're for static analyzers (mypy, pyright), IDE autocomplete, and human readers.</p>
<pre><code>from typing import Optional, Union, Callable, Iterable

def greet(name: str, loud: bool = False) -&gt; str:
    message = f"Hello, {name}"
    return message.upper() if loud else message

# Python 3.10+ union syntax
def parse(raw: str | bytes) -&gt; int | None:
    try:
        return int(raw)
    except ValueError:
        return None

# Generic collections (3.9+) — use lowercase built-ins
items: list[int] = [1, 2, 3]
tags:  dict[str, set[str]] = {}

# Custom types
from typing import NewType, TypedDict, Literal
UserId = NewType("UserId", int)

class UserDict(TypedDict):
    id: UserId
    name: str
    role: Literal["admin", "user", "guest"]</code></pre>
<p>Why bother:</p>
<ul>
  <li>Catches bugs at analysis time, before runtime.</li>
  <li>Serves as the most up-to-date documentation.</li>
  <li>Enables smarter IDE features (rename, go-to-definition, autocomplete).</li>
  <li>Frameworks use them at runtime: FastAPI routes, Pydantic validation, attrs/dataclasses field types.</li>
</ul>
<p>For gradual adoption, type critical APIs first (public functions, data classes). Don't over-annotate trivial locals.</p>
'''

ANSWERS[39] = r'''
<p><code>typing</code> provides the vocabulary for type hints: generics, protocols, literals, aliases, overloads.</p>
<pre><code>from typing import (
    Any, Optional, Union, Callable, Iterable, Iterator,
    TypeVar, Generic, Protocol, Literal, Final,
    TypedDict, NotRequired, cast, overload,
)

# Generics
T = TypeVar("T")

def first(items: Iterable[T]) -&gt; T | None:
    return next(iter(items), None)

class Stack(Generic[T]):
    def __init__(self):
        self._items: list[T] = []
    def push(self, item: T) -&gt; None: ...
    def pop(self) -&gt; T: ...

# Protocols — structural typing
class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -&gt; bool: ...

def sort_them(items: Iterable[Comparable]) -&gt; list: ...

# Overloads — different return types by arg
@overload
def parse(x: str) -&gt; str: ...
@overload
def parse(x: int) -&gt; int: ...
def parse(x):                # actual implementation
    return x * 2

# Literal types — specific values
Mode = Literal["r", "w", "a"]
def open_file(path: str, mode: Mode) -&gt; Any: ...</code></pre>
<p><code>Protocol</code> is especially powerful — duck typing with type safety. A class conforms to a Protocol structurally without needing to inherit from it. The go-to for designing modern Python APIs with flexible typing.</p>
'''

ANSWERS[40] = r'''
<p><code>mypy</code> is the original Python type checker. It reads your code + annotations and flags inconsistencies — without running the code.</p>
<pre><code># app.py
def greet(name: str) -&gt; str:
    return f"Hello, {name}"

greet(42)                   # mypy: Argument 1 has incompatible type "int"; expected "str"
result: int = greet("Ana")  # mypy: Incompatible types in assignment

# Run
$ mypy app.py
app.py:4: error: Argument 1 to "greet" has incompatible type "int"; expected "str"
Found 1 error in 1 file (checked 1 source file)</code></pre>
<p>How it works:</p>
<ul>
  <li>Parses source code + <code>.pyi</code> type stubs + reads installed package metadata.</li>
  <li>Infers types from annotations, literal values, and control flow.</li>
  <li>Flow analysis narrows types (after <code>if isinstance(x, int)</code>, x is <code>int</code> inside the block).</li>
  <li>Supports incremental checking for speed in large codebases.</li>
</ul>
<p>Configuration via <code>pyproject.toml</code> or <code>mypy.ini</code>. Key flags: <code>--strict</code> (no <code>Any</code>, no untyped defs), <code>--warn-unused-ignores</code>. Alternatives: <strong>pyright</strong> (Microsoft, faster, used by Pylance in VS Code), <strong>pyre</strong> (Facebook), <strong>pytype</strong> (Google).</p>
<p>Add to CI for safety; run locally through your editor for rapid feedback.</p>
'''

ANSWERS[41] = r'''
<p><code>pytest</code> is the standard Python testing framework — minimal boilerplate, powerful fixtures, plugin ecosystem.</p>
<pre><code># test_math.py
def test_addition():
    assert 1 + 1 == 2

def test_division_by_zero():
    import pytest
    with pytest.raises(ZeroDivisionError):
        1 / 0

# Parametrized (see Q42)
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert a + b == expected

# Fixtures (see Q43)
@pytest.fixture
def db():
    conn = create_test_db()
    yield conn
    conn.close()

def test_user_save(db):
    db.save(User("Ana"))
    assert db.query(User).count() == 1</code></pre>
<pre><code># Run
pytest                       # auto-discovers test_*.py
pytest tests/ -v             # verbose
pytest -k "addition"         # only tests matching pattern
pytest --cov=myapp           # with coverage (pytest-cov plugin)
pytest -x                    # stop on first failure
pytest --lf                  # re-run only last failures</code></pre>
<p>Why pytest over <code>unittest</code>: plain <code>assert</code> (with rich failure messages), fixtures instead of setUp/tearDown, no class requirement, huge plugin ecosystem (<code>pytest-cov</code>, <code>pytest-xdist</code> for parallel, <code>pytest-asyncio</code>, <code>hypothesis</code> for property testing).</p>
'''

ANSWERS[42] = r'''
<p><code>@pytest.mark.parametrize</code> runs the same test with multiple input sets — each as a separate test case with its own pass/fail status.</p>
<pre><code>import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "olleh"),
    ("", ""),
    ("a", "a"),
    ("AB", "BA"),
])
def test_reverse(input, expected):
    assert reverse(input) == expected

# Multiple parameters with IDs
@pytest.mark.parametrize(
    "n,result",
    [(0, 1), (1, 1), (5, 120), (10, 3628800)],
    ids=["zero", "one", "five", "ten"],
)
def test_factorial(n, result):
    assert factorial(n) == result

# Stacked — cartesian product
@pytest.mark.parametrize("base", [2, 10, 16])
@pytest.mark.parametrize("exp", [0, 1, 5])
def test_power(base, exp):
    assert power(base, exp) == base ** exp
# Runs 3 × 3 = 9 tests

# With pytest.param — mark individual cases
@pytest.mark.parametrize("x,y", [
    (1, 2),
    pytest.param(3, 0, marks=pytest.mark.xfail),    # expected failure
    pytest.param(5, 6, marks=pytest.mark.skip),
])
def test_cases(x, y):
    ...</code></pre>
<p>Output shows each parameter combo as a distinct test. Essential for table-driven tests — much cleaner than writing separate functions or using loops (which report only one aggregated failure).</p>
'''

ANSWERS[43] = r'''
<p><strong>Fixtures</strong> supply test dependencies — databases, clients, temp directories, mock objects. pytest handles setup, teardown, and dependency wiring.</p>
<pre><code>import pytest

@pytest.fixture
def user():
    return User(id=1, name="Ana")

def test_greet(user):            # pytest injects fixture by name
    assert user.name == "Ana"

# Setup + teardown via yield
@pytest.fixture
def db_conn():
    conn = connect("sqlite://:memory:")
    setup_schema(conn)
    yield conn                    # test runs here
    conn.close()

# Scoped fixtures — share across tests
@pytest.fixture(scope="session")      # function / class / module / package / session
def expensive_resource():
    return start_selenium()

# Autouse — runs without explicit request
@pytest.fixture(autouse=True)
def reset_logging():
    yield
    logging.shutdown()

# Fixtures can depend on other fixtures
@pytest.fixture
def authenticated_client(db_conn, user):
    return make_client(user, db_conn)</code></pre>
<p>Built-in fixtures worth knowing: <code>tmp_path</code> (temp directory), <code>monkeypatch</code> (safe patching), <code>capsys</code> (capture stdout/stderr), <code>caplog</code> (capture logs), <code>request</code> (metadata about the current test).</p>
<p>Organize shared fixtures in <code>conftest.py</code> — pytest auto-loads it from any level of your test tree.</p>
'''

ANSWERS[44] = r'''
<p><code>unittest.mock</code> replaces real objects with test doubles that record calls and return canned values. Essential for isolating units and testing interactions.</p>
<pre><code>from unittest.mock import MagicMock, patch

# Direct mock
m = MagicMock(return_value=42)
m(1, 2, key="val")
m.assert_called_with(1, 2, key="val")
m.call_count                  # 1

# Patch during a test — context manager or decorator
@patch("myapp.email.send")
def test_signup(mock_send):
    mock_send.return_value = True
    signup("ana@example.com")
    mock_send.assert_called_once_with("ana@example.com", subject="Welcome")

# Patch an attribute
with patch.object(MyService, "fetch") as mock_fetch:
    mock_fetch.return_value = {"id": 1}
    service.process(1)

# Spec — fail on calls to methods that don't exist on real object
mock = MagicMock(spec=User)
mock.nonexistent()            # AttributeError

# Side effects — custom behavior or raising
mock.method.side_effect = [1, 2, ValueError("boom")]    # sequence
mock.method.side_effect = lambda x: x + 1               # function</code></pre>
<p>Rules:</p>
<ul>
  <li><strong>Patch where the name is used</strong>, not where it's defined: <code>@patch("myapp.module.requests")</code>, not <code>@patch("requests")</code>.</li>
  <li><strong>Use <code>spec=</code></strong> to catch typos at test time.</li>
  <li><strong>Don't over-mock</strong> — mocked tests can pass while real code fails. Mock external dependencies, not your own code.</li>
</ul>
<p>pytest has <code>mocker</code> fixture (<code>pytest-mock</code> plugin) for a cleaner syntax.</p>
'''

ANSWERS[45] = r'''
<p>Custom exceptions let you distinguish domain-specific errors from library errors, attach structured context, and let callers catch the right thing.</p>
<pre><code>class AppError(Exception):
    """Base class for all application errors."""
    def __init__(self, message: str, *, code: str = None, **context):
        super().__init__(message)
        self.code = code
        self.context = context

class ValidationError(AppError):
    """Input validation failed."""

class ResourceNotFound(AppError):
    """Requested resource does not exist."""

class RateLimitExceeded(AppError):
    """Too many requests."""
    def __init__(self, retry_after: int):
        super().__init__(f"Rate limited; retry in {retry_after}s",
                         code="RATE_LIMIT", retry_after=retry_after)

# Usage — consumers catch the level they care about
try:
    process(user_input)
except ValidationError as e:
    return jsonify({"error": e.code, "details": e.context}), 400
except AppError as e:
    logger.error(str(e), extra=e.context)
    return jsonify({"error": "internal"}), 500</code></pre>
<p>Design guidelines:</p>
<ul>
  <li><strong>Hierarchy</strong> — single base, specific subclasses. Lets callers catch broadly or narrowly.</li>
  <li><strong>Attach context</strong> as attributes, not just in the message — structured logging can use them.</li>
  <li><strong>Chain with <code>raise ... from ...</code></strong> — preserve root cause in tracebacks.</li>
  <li><strong>Name with <code>Error</code> suffix</strong> per Python convention.</li>
  <li><strong>Don't catch <code>Exception</code> wholesale</strong> unless at a boundary with a logging fallback.</li>
</ul>
'''

ANSWERS[46] = r'''
<p><code>__slots__</code> replaces a class's <code>__dict__</code> with a fixed array of attributes — reducing memory per instance by 30-50% and slightly speeding up attribute access.</p>
<pre><code>class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.x = 3              # OK — declared slot
p.z = 4              # AttributeError — not in __slots__

# Memory comparison
import sys
class PointDict:
    def __init__(self, x, y):
        self.x, self.y = x, y

sys.getsizeof(Point(1, 2))                   # ~48 bytes
sys.getsizeof(PointDict(1, 2))               # ~48 bytes — plus the dict itself (~200 bytes)</code></pre>
<p>Trade-offs:</p>
<ul>
  <li><strong>Smaller memory</strong>, modestly faster attribute access.</li>
  <li><strong>No dynamic attributes</strong> — can't add new fields at runtime. For most classes, that's a feature.</li>
  <li><strong>Multiple inheritance</strong> — non-empty <code>__slots__</code> on more than one parent fails. All parents must define slots or use <code>__slots__ = ()</code>.</li>
  <li><strong>No <code>__weakref__</code> by default</strong> — add <code>"__weakref__"</code> to slots if needed.</li>
  <li><strong>No pickle customization headaches</strong> — works with standard pickle.</li>
</ul>
<p>Use for data-heavy classes with millions of instances (game entities, graph nodes). <code>@dataclass(slots=True)</code> (Python 3.10+) generates slots automatically.</p>
'''

ANSWERS[47] = r'''
<p><code>inspect</code> introspects live objects — signatures, source code, class hierarchies, frame data. The backbone of debuggers, IDEs, and ORMs that need to reason about code at runtime.</p>
<pre><code>import inspect

def greet(name: str, loud: bool = False) -&gt; str:
    """Greet someone."""
    return f"Hello, {name}"

# Function signature
sig = inspect.signature(greet)
sig.parameters          # OrderedDict of Parameter objects
sig.return_annotation   # &lt;class 'str'&gt;

for name, param in sig.parameters.items():
    print(name, param.annotation, param.default)

# Source code
inspect.getsource(greet)
inspect.getfile(greet)
inspect.getmodule(greet)

# Class hierarchy
inspect.getmro(SomeClass)           # method resolution order

# Stack frames (debugging)
frame = inspect.currentframe()
frame.f_locals                       # local variables
inspect.stack()                      # all frames up to the root

# Check callable types
inspect.isfunction(x)
inspect.ismethod(x)
inspect.isgenerator(x)
inspect.iscoroutinefunction(x)</code></pre>
<p>Use cases: auto-generating CLI from function signatures (<code>click</code>, <code>typer</code>), dependency injection (FastAPI), API documentation, decorators that need to adapt to wrapped function's signature. For production code, pair with <code>functools.wraps</code> to preserve inspectability through decorators.</p>
'''

ANSWERS[48] = r'''
<p><code>traceback</code> manipulates exception tracebacks — formatting, printing, extracting frame details.</p>
<pre><code>import traceback

try:
    1 / 0
except ZeroDivisionError as e:
    # Print to stderr (like the default)
    traceback.print_exc()

    # Get as string
    tb_str = traceback.format_exc()
    log.error("Calculation failed:\n%s", tb_str)

    # Structured access
    tb_list = traceback.extract_tb(e.__traceback__)
    for frame in tb_list:
        print(f"{frame.filename}:{frame.lineno} in {frame.name}")

# Custom exception hook — catch uncaught exceptions
def global_handler(exc_type, exc_value, exc_tb):
    logger.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_tb),
    )
    sys.__excepthook__(exc_type, exc_value, exc_tb)   # also print normally
sys.excepthook = global_handler

# Python 3.11+ — better tracebacks with caret markers
# Shows exactly which sub-expression failed</code></pre>
<p>Logging gotchas:</p>
<ul>
  <li><code>logger.exception("msg")</code> — includes traceback automatically (inside an <code>except</code>).</li>
  <li><code>logger.error("msg", exc_info=True)</code> — same, from anywhere.</li>
  <li>For async code, use <code>loop.set_exception_handler</code> to catch unhandled coroutine exceptions.</li>
</ul>
<p>In production, ship tracebacks to Sentry or similar — they deduplicate and group by root cause, and are much more useful than log files for debugging.</p>
'''

ANSWERS[49] = r'''
<p><code>difflib</code> compares sequences and produces diffs — the foundation of <code>diff</code>-style tools and patch generation.</p>
<pre><code>import difflib

# Show unified diff (like git diff)
a = "the quick brown fox\njumps over\nlazy dogs".splitlines(keepends=True)
b = "the QUICK brown fox\njumps over\nthe lazy dog".splitlines(keepends=True)

print("".join(difflib.unified_diff(a, b, fromfile="a", tofile="b", lineterm="")))
# --- a
# +++ b
# @@ -1,3 +1,3 @@
# -the quick brown fox
# +the QUICK brown fox
#  jumps over
# -lazy dogs
# +the lazy dog

# Find similar strings — "did you mean?"
difflib.get_close_matches("peach", ["apple", "pineapple", "peachy", "peace"], n=2)
# ['peachy', 'peach' didn't match exactly but 'peachy' and 'peace' did]

# SequenceMatcher — more detailed
m = difflib.SequenceMatcher(None, "abcd", "abxd")
m.ratio()                     # 0.75 — similarity score
m.get_matching_blocks()       # matched subsequences

# HTML side-by-side diff (rendering-ready)
html = difflib.HtmlDiff().make_file(a, b)</code></pre>
<p>Use cases: code review tools, merge conflict UI, fuzzy matching, spell check suggestions, configuration drift detection. For large files or heavy diff workloads, libraries like <code>python-rapidfuzz</code> (faster similarity) or <code>unidiff</code> (parse diff output) may be better fits.</p>
'''

ANSWERS[50] = r'''
<p><code>codecs</code> provides the registry and interfaces for character encodings. Most text I/O hits it implicitly; you reach for it directly when dealing with uncommon encodings, stream transformations, or error handlers.</p>
<pre><code>import codecs

# Open with explicit encoding + error handling
with codecs.open("latin1_file.txt", "r", encoding="latin-1", errors="replace") as f:
    text = f.read()

# Encode/decode bytes manually
b = "café".encode("utf-8")           # b'caf\xc3\xa9'
codecs.decode(b, "utf-8")             # "café"

# BOM — byte order mark
with open("out.txt", "wb") as f:
    f.write(codecs.BOM_UTF8)          # optional UTF-8 BOM
    f.write("hello".encode("utf-8"))

# Transformations — rarely needed now
import base64
base64.b64encode(b"data")             # Use base64 module, not codecs
codecs.encode(b"data", "hex")          # Still works but dated

# Error handlers: 'strict' (default), 'ignore', 'replace', 'xmlcharrefreplace', 'backslashreplace'
"café".encode("ascii", errors="xmlcharrefreplace")    # b'caf&amp;#233;'</code></pre>
<p>In modern Python, most code just uses <code>open(path, encoding="utf-8")</code> — the codecs registry handles the rest. Reach for <code>codecs</code> directly when you need custom error handlers, stream wrappers, or support for exotic encodings (UTF-7, IBM EBCDIC variants).</p>
'''

ANSWERS[51] = r'''
<p>Python 3 strings are <strong>Unicode code points</strong>, not bytes. <code>bytes</code> objects hold raw binary data. Converting between them requires an explicit encoding.</p>
<pre><code># str ↔ bytes — always specify encoding
s = "café"
b = s.encode("utf-8")         # b'caf\xc3\xa9'
b.decode("utf-8")             # "café"

# File I/O — declare encoding
with open("f.txt", encoding="utf-8") as f:    # text mode
    text = f.read()

with open("f.bin", "rb") as f:                 # binary mode
    data = f.read()

# Detect (heuristically) — chardet/charset-normalizer
from charset_normalizer import from_bytes
result = from_bytes(unknown_bytes).best()
print(result.encoding, str(result))</code></pre>
<p>Best practices:</p>
<ul>
  <li><strong>UTF-8 everywhere</strong> — for source files, web APIs, databases, logs, filenames.</li>
  <li><strong>Always specify <code>encoding=</code></strong> on <code>open()</code> — on Windows the default is locale-dependent (often cp1252).</li>
  <li><strong>Normalize Unicode</strong> when comparing: <code>unicodedata.normalize("NFC", s)</code>. "é" (single codepoint) and "e + combining acute" compare unequal otherwise.</li>
  <li><strong>Length vs display width</strong>: <code>len("🎉")</code> is 1 (codepoint) but renders as a grapheme that may be 2 terminal columns.</li>
</ul>
<p>Python 3.15 will make UTF-8 the default on all platforms (PEP 686). Set <code>PYTHONUTF8=1</code> today to get that behavior early.</p>
'''

ANSWERS[52] = r'''
<p><code>struct</code> converts between Python values and fixed-size C binary layouts — essential for protocols, file formats, and interop with C code.</p>
<pre><code>import struct

# Format string specifies byte order + types
# Common types: b(int8), h(int16), i(int32), q(int64), f(float), d(double), s(bytes)
# Order: '&lt;' little-endian, '&gt;' big-endian, '!' network (big-endian), '=' native

# Pack — values to bytes
data = struct.pack("&lt;ihh", 1234, 42, -7)
# 4 bytes (int32) + 2 bytes (int16) + 2 bytes (int16) = 8 bytes
# b'\xd2\x04\x00\x00*\x00\xf9\xff'

# Unpack — bytes to values
struct.unpack("&lt;ihh", data)                 # (1234, 42, -7)

# Size without packing
struct.calcsize("&lt;ihh")                      # 8

# Iterate fixed-size records from a binary file
with open("records.bin", "rb") as f:
    while chunk := f.read(8):
        record = struct.unpack("&lt;ihh", chunk)
        process(record)

# Strings with fixed size
header = struct.pack("&lt;4sI", b"WAVE", 16000)    # 4-byte tag + uint32</code></pre>
<p>Use cases: reading PNG/WAV/TCP packet headers, network protocol implementations, memory-mapped files, parsing legacy formats. For variable-length or complex types, consider <code>construct</code> (declarative) or serialization formats like Protobuf.</p>
'''

ANSWERS[53] = r'''
<p><code>shutil</code> covers "shell-like" file operations — copying, moving, deleting directories, disk usage, archive handling.</p>
<pre><code>import shutil

# Copy
shutil.copy("src.txt", "dst.txt")              # file, preserves permissions
shutil.copy2("src.txt", "dst.txt")             # also preserves timestamps
shutil.copyfile("src.txt", "dst.txt")          # content only

# Directory operations
shutil.copytree("src_dir", "dst_dir")
shutil.copytree("src", "dst", dirs_exist_ok=True)    # Python 3.8+
shutil.move("old", "new")                      # works across filesystems
shutil.rmtree("obsolete_dir")                  # recursive delete

# Disk usage
total, used, free = shutil.disk_usage("/")

# Archives
shutil.make_archive("backup", "zip", "my_project")
shutil.unpack_archive("backup.zip", "restored/")

# Find executable in PATH
shutil.which("python")                          # "/usr/bin/python" or None

# High-level file-like copy with callback
shutil.copyfileobj(src_file, dst_file, length=1024 * 1024)</code></pre>
<p><strong>Cross-device moves</strong> — <code>shutil.move</code> handles them by copy+delete when <code>os.rename</code> fails. Copying doesn't preserve ownership by default; use <code>copy2</code> + <code>chown</code> if needed. For huge files, combine with <code>os.sendfile</code> on Linux for zero-copy kernel-level transfer.</p>
'''

ANSWERS[54] = r'''
<p><code>glob</code> expands shell-style wildcards to file paths. Simpler than writing recursive <code>os.walk</code> logic for pattern matching.</p>
<pre><code>import glob

glob.glob("*.py")                      # ["app.py", "test.py"]
glob.glob("src/**/*.py", recursive=True)   # recursive — with **
glob.glob("file?.txt")                 # single char wildcard
glob.glob("[abc]*.txt")                # character class

# iglob — iterator, for huge directories
for path in glob.iglob("logs/**/*.log", recursive=True):
    process(path)

# pathlib — usually more readable
from pathlib import Path
list(Path("src").glob("*.py"))
list(Path(".").rglob("*.py"))           # r = recursive

# Patterns
#   *     any sequence (no /)
#   **    any depth (with recursive=True or pathlib.rglob)
#   ?     single char
#   [seq] char in set
#   [!seq] char NOT in set</code></pre>
<p>Prefer <code>pathlib.Path.glob/rglob</code> for new code — returns <code>Path</code> objects with better ergonomics. Note that <code>glob</code> doesn't match hidden files (starting with <code>.</code>) by default — use <code>glob.glob(".*")</code> explicitly.</p>
<p>For complex filtering (file size, modification time), <code>glob</code> gives you paths; layer <code>os.stat</code> or <code>Path.stat</code> on top.</p>
'''

ANSWERS[55] = r'''
<p><code>zipfile</code> reads and writes ZIP archives, including password-protected, ZIP64 (large files), and streaming.</p>
<pre><code>import zipfile

# Create
with zipfile.ZipFile("archive.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write("file.txt")                         # add file
    z.write("path/to/file.py", arcname="file.py")   # rename on add
    z.writestr("meta.txt", "created in memory")     # from a string

# Read
with zipfile.ZipFile("archive.zip") as z:
    z.namelist()                                # list contents
    z.printdir()                                # pretty print
    z.read("file.txt")                          # bytes
    z.extractall("output_dir")

# Member info
for info in z.infolist():
    print(info.filename, info.file_size, info.compress_size)

# Stream read without full extract
with zipfile.ZipFile("big.zip") as z:
    with z.open("inner.csv") as f:
        for line in io.TextIOWrapper(f, "utf-8"):
            process(line)

# Compression levels
# ZIP_STORED   — no compression
# ZIP_DEFLATED — standard (zlib)
# ZIP_BZIP2    — better ratio, slower
# ZIP_LZMA     — best ratio, slowest</code></pre>
<p>ZIP is good for widely compatible archives. For better compression, use LZMA (<code>.xz</code>) via <code>lzma</code> module; for tar compatibility, use <code>tarfile</code> (next question). For writing directly to cloud storage, use <code>smart_open</code> or zipstream libraries.</p>
'''

ANSWERS[56] = r'''
<p><code>tarfile</code> handles tar archives, with optional gzip/bzip2/xz compression. More common than ZIP on Unix systems.</p>
<pre><code>import tarfile

# Create — mode "w:gz" means write + gzip
with tarfile.open("backup.tar.gz", "w:gz") as tar:
    tar.add("my_project", arcname="project")
    tar.add("config.yaml")

# Read and extract
with tarfile.open("backup.tar.gz", "r:*") as tar:    # "*" auto-detects compression
    tar.list()                                        # print contents
    tar.extractall(path="restored/")

# Stream member by member — memory-friendly
with tarfile.open("big.tar.gz") as tar:
    for member in tar:
        if member.name.endswith(".log"):
            f = tar.extractfile(member)
            if f:
                for line in f:
                    process(line.decode("utf-8"))

# Filter what gets extracted (Python 3.12+ recommends filter="data")
tar.extractall(path="dest/", filter="data")</code></pre>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div><strong>Tar extraction has security implications.</strong> Malicious archives can contain paths with <code>..</code> or absolute paths that write outside the target directory. Python 3.12+ added <code>filter=</code> — use <code>filter="data"</code> for untrusted archives. Before 3.12, validate member names manually or use <code>safetar</code>.</div>
</div>
<p>Compression modes: <code>w:</code> (no compression), <code>w:gz</code>, <code>w:bz2</code>, <code>w:xz</code>. Use <code>"r:*"</code> to auto-detect on read.</p>
'''

ANSWERS[57] = r'''
<p><code>tempfile</code> creates temporary files and directories that are automatically cleaned up — no manual path-generation or leftover cruft.</p>
<pre><code>import tempfile

# Named temp file — visible on disk, auto-deleted when closed
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=True) as f:
    f.write("hello")
    f.flush()
    print(f.name)       # /tmp/tmpXXXX.txt
# File gone here

# In-memory temp file — avoids disk
with tempfile.SpooledTemporaryFile(max_size=1_000_000) as f:
    f.write(b"initially in memory")
    # rolls to disk only if size exceeds max_size

# Temp directory — recursive auto-cleanup
with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "work.txt"
    path.write_text("scratch work")
    # tmpdir is gone when context exits

# Explicit lifetime — you handle cleanup
f = tempfile.NamedTemporaryFile(delete=False)
try:
    f.write(b"data"); f.close()
    subprocess.run(["tool", f.name])
finally:
    os.remove(f.name)

# Temp name without creating file (rarely what you want)
tempfile.mktemp(suffix=".ini")     # deprecated; race condition</code></pre>
<p>Use <code>tempfile</code> over hand-rolled "/tmp/myapp-XXXX" paths: it picks the right base directory per OS (<code>TMPDIR</code>, <code>TEMP</code>, <code>TMP</code>), creates securely (mode 600), guarantees unique names, and cleans up on context exit — including on exceptions.</p>
'''

ANSWERS[58] = r'''
<p><code>sched</code> provides a general-purpose event scheduler — run callables at specific delays or absolute times, within one process.</p>
<pre><code>import sched, time

scheduler = sched.scheduler(time.time, time.sleep)

def send_reminder(msg):
    print(f"[{time.ctime()}] {msg}")

# Schedule with delay (in seconds) + priority
scheduler.enter(5,  1, send_reminder, argument=("5s delay",))
scheduler.enter(10, 1, send_reminder, argument=("10s delay",))

# Absolute time
scheduler.enterabs(time.time() + 30, 1, send_reminder, ("at 30s",))

# Cancel
event = scheduler.enter(60, 1, send_reminder, ("won't run",))
scheduler.cancel(event)

scheduler.run()        # blocks until all events fire</code></pre>
<p>Limitations:</p>
<ul>
  <li><strong>Single-threaded</strong> — <code>run()</code> blocks; callbacks can't be long-running without starving other events.</li>
  <li><strong>Not persistent</strong> — scheduled events die with the process. Use a real job queue (APScheduler, Celery beat, or systemd timers) for anything that needs to survive restarts.</li>
  <li><strong>Priorities</strong> break ties for simultaneous events — lower number fires first.</li>
</ul>
<p>For simple delayed work inside an async app, use <code>asyncio.sleep</code> + <code>asyncio.create_task</code>. For cron-style recurrence, <code>APScheduler</code> is the standard choice.</p>
'''

ANSWERS[59] = r'''
<p><code>queue</code> provides thread-safe FIFO, LIFO, and priority queues for producer-consumer patterns between threads. Never use a plain <code>list</code> across threads.</p>
<pre><code>import queue
import threading

q = queue.Queue(maxsize=100)     # bounded — producer blocks when full

# Producer
def producer():
    for item in generate_items():
        q.put(item)              # blocks if full
    q.put(None)                  # sentinel to signal end

# Consumer
def consumer():
    while True:
        item = q.get()           # blocks if empty
        if item is None:
            q.task_done()
            break
        process(item)
        q.task_done()

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()

q.join()                          # wait until all tasks are task_done
t1.join(); t2.join()</code></pre>
<p>Queue types in the module:</p>
<ul>
  <li><code>Queue</code> — FIFO (default).</li>
  <li><code>LifoQueue</code> — stack.</li>
  <li><code>PriorityQueue</code> — heap-based; items are tuples <code>(priority, data)</code>.</li>
  <li><code>SimpleQueue</code> (3.7+) — faster unbounded FIFO without <code>task_done</code>/<code>join</code>.</li>
</ul>
<p>For inter-process: <code>multiprocessing.Queue</code> (similar API, pickle overhead). For async: <code>asyncio.Queue</code> (not thread-safe, but event-loop-safe).</p>
'''

ANSWERS[60] = r'''
<p>Several levels of abstraction depending on needs:</p>
<pre><code>import heapq

# 1. Raw heap — fastest, not thread-safe
heap = []
heapq.heappush(heap, (priority, task))
task = heapq.heappop(heap)[1]       # smallest priority first

# 2. queue.PriorityQueue — thread-safe
from queue import PriorityQueue
pq = PriorityQueue()
pq.put((2, "medium"))
pq.put((1, "urgent"))
pq.get()[1]       # "urgent"

# 3. Full-featured wrapper with stable ordering
import itertools
class PriorityQueueStable:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def push(self, item, priority):
        # counter breaks ties to maintain insertion order
        heapq.heappush(self._heap, (priority, next(self._counter), item))

    def pop(self):
        return heapq.heappop(self._heap)[2]

    def __len__(self):
        return len(self._heap)</code></pre>
<p>Notes:</p>
<ul>
  <li><strong>Ties and non-comparable items</strong>: raw tuples in the heap will compare item-by-item. If priorities tie and items aren't comparable (like dicts), you get <code>TypeError</code>. The counter trick prevents it.</li>
  <li><strong>Max-heap</strong>: negate priorities or use a <code>(-priority, item)</code> tuple.</li>
  <li><strong>Dynamic priorities</strong>: heaps don't support efficient update. Mark items as stale and skip them on pop, or use a Fibonacci heap library for true decrease-key.</li>
</ul>
'''

ANSWERS[61] = r'''
<p>An iterator implements <code>__iter__()</code> (returns self) and <code>__next__()</code> (returns the next item or raises <code>StopIteration</code>).</p>
<pre><code>class Countdown:
    def __init__(self, start):
        self.n = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.n &lt;= 0:
            raise StopIteration
        current = self.n
        self.n -= 1
        return current

list(Countdown(3))           # [3, 2, 1]

# Iterable that produces fresh iterators on each iter()
class FibonacciIterable:
    def __init__(self, limit):
        self.limit = limit

    def __iter__(self):
        # Return a new iterator each time — supports multiple loops
        def generate():
            a, b = 0, 1
            for _ in range(self.limit):
                yield a
                a, b = b, a + b
        return generate()

fib = FibonacciIterable(5)
list(fib)                    # [0, 1, 1, 2, 3]
list(fib)                    # [0, 1, 1, 2, 3]  — works again</code></pre>
<p>Distinction matters:</p>
<ul>
  <li><strong>Iterator</strong> — has state, single-use. List iterators, file iterators, generators.</li>
  <li><strong>Iterable</strong> — can produce iterators. Lists, sets, dicts, strings.</li>
</ul>
<p>For all but the most specialized cases, <strong>use a generator function</strong> — <code>def __iter__(self): yield ...</code>. Generators handle the protocol automatically.</p>
'''

ANSWERS[62] = r'''
<p>Covered alongside Q23. The <code>abc</code> module provides machinery for abstract base classes and virtual subclassing.</p>
<pre><code>from abc import ABC, ABCMeta, abstractmethod

# Preferred — inherit from ABC
class Shape(ABC):
    @abstractmethod
    def area(self) -&gt; float: ...

# Equivalent — use metaclass directly
class Shape(metaclass=ABCMeta):
    @abstractmethod
    def area(self) -&gt; float: ...

# Virtual subclass — already-written class retroactively declared conforming
@Shape.register
class Circle:                     # NOT inheriting from Shape
    def __init__(self, r): self.r = r
    def area(self): return 3.14 * self.r ** 2

isinstance(Circle(1), Shape)      # True
issubclass(Circle, Shape)         # True

# __subclasshook__ — automatic virtual subclass by method presence
class Greetable(ABC):
    @classmethod
    def __subclasshook__(cls, subclass):
        if any("greet" in C.__dict__ for C in subclass.__mro__):
            return True
        return NotImplemented

class Robot:
    def greet(self): print("beep")

issubclass(Robot, Greetable)      # True</code></pre>
<p>Standard ABCs in <code>collections.abc</code>: <code>Iterable</code>, <code>Container</code>, <code>Hashable</code>, <code>Sized</code>, <code>Sequence</code>, <code>Mapping</code>, <code>MutableSequence</code>, etc. Use them in type hints and <code>isinstance</code> checks for maximum flexibility.</p>
'''

ANSWERS[63] = r'''
<p><code>pdb</code> is Python's built-in debugger. Drop it into code at any point for an interactive session.</p>
<pre><code># Set a breakpoint
import pdb; pdb.set_trace()      # old way
breakpoint()                      # Python 3.7+, same effect

# Inside the debugger — common commands:
# (Pdb) l          list source around current line
# (Pdb) n          next (execute current line)
# (Pdb) s          step into function call
# (Pdb) c          continue until next breakpoint
# (Pdb) p var      print variable
# (Pdb) pp obj     pretty-print
# (Pdb) w          where — stack trace
# (Pdb) u / d      move up / down a stack frame
# (Pdb) b 42       set breakpoint at line 42
# (Pdb) !expr      execute arbitrary Python
# (Pdb) q          quit

# Post-mortem on a caught exception
import pdb, traceback, sys
try:
    buggy()
except Exception:
    traceback.print_exc()
    pdb.post_mortem()

# Run a script under pdb
$ python -m pdb app.py</code></pre>
<p>Alternatives worth knowing:</p>
<ul>
  <li><strong>ipdb</strong> — pdb with IPython's UI (tab completion, colors).</li>
  <li><strong>pudb</strong> — TUI debugger with side-by-side source/variables.</li>
  <li><strong>IDE debuggers</strong> — VS Code, PyCharm offer graphical breakpoints and watch windows; usually the productive choice.</li>
  <li><strong>Print debugging</strong> — unashamedly valid. <code>from pprint import pp; pp(obj)</code>.</li>
</ul>
'''

ANSWERS[64] = r'''
<p><code>cProfile</code> measures where time is spent — the first tool to reach for before optimizing.</p>
<pre><code># Quick profile
import cProfile
cProfile.run("expensive_function()")

# With output file
cProfile.run("expensive_function()", "profile.stats")

# Programmatic API — finer control
import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()
...
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative").print_stats(20)   # top 20 by cumulative time

# Command line
$ python -m cProfile -o profile.out -s cumulative app.py
$ python -m pstats profile.out
&gt;&gt;&gt; sort cumulative
&gt;&gt;&gt; stats 20</code></pre>
<p>Key metrics:</p>
<ul>
  <li><strong>ncalls</strong> — total calls (and recursive / primitive).</li>
  <li><strong>tottime</strong> — time spent <em>in this function only</em>.</li>
  <li><strong>cumtime</strong> — time including sub-calls. Usually what you want.</li>
</ul>
<p>Better tools for specific needs:</p>
<ul>
  <li><strong>py-spy</strong> — sampling profiler; attaches to running processes; doesn't need code changes. Great for production diagnosis.</li>
  <li><strong>snakeviz</strong> / <strong>tuna</strong> — visualize <code>cProfile</code> output as flame graphs.</li>
  <li><strong>line_profiler</strong> — per-line timing, for tight loops.</li>
  <li><strong>memory_profiler</strong> / <strong>tracemalloc</strong> — memory, not CPU.</li>
</ul>
'''

ANSWERS[65] = r'''
<p>Decorators that accept arguments add one level of nesting — the outer callable returns the actual decorator.</p>
<pre><code>from functools import wraps
import time

def retry(max_attempts=3, delay=1):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}; retrying in {delay}s")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=5, delay=2)
def fetch(url):
    return requests.get(url)

# Class-based — cleaner when you need state
class Retry:
    def __init__(self, max_attempts=3, delay=1):
        self.max_attempts = max_attempts
        self.delay = delay

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ...
        return wrapper

@Retry(max_attempts=5)
def fetch(url): ...</code></pre>
<p>The three levels: decorator-factory (takes args, returns decorator) → decorator (takes function, returns wrapper) → wrapper (replaces the function). The <code>@wraps</code> in the inner function preserves metadata.</p>
<p>Gotcha: writing <code>@retry</code> instead of <code>@retry()</code> calls <code>retry(fn)</code> with the function as argument, which fails confusingly. Require parentheses or detect both cases with a <code>default</code> fallback.</p>
'''

ANSWERS[66] = r'''
<p><code>ast</code> parses Python source into an Abstract Syntax Tree — a structured representation of code. Enables static analysis, refactoring tools, DSLs, and code generators.</p>
<pre><code>import ast

source = """
def greet(name):
    print(f"Hello, {name}")
"""

tree = ast.parse(source)
print(ast.dump(tree, indent=2))
# Module(
#   body=[
#     FunctionDef(
#       name='greet',
#       args=arguments(args=[arg(arg='name')]),
#       body=[...]

# Visitor pattern — walk the tree
class FunctionFinder(ast.NodeVisitor):
    def __init__(self):
        self.names = []
    def visit_FunctionDef(self, node):
        self.names.append(node.name)
        self.generic_visit(node)       # recurse

finder = FunctionFinder()
finder.visit(tree)
finder.names     # ["greet"]

# Transform (modify) — rewrites nodes
class RenameVisitor(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == "old_name":
            node.id = "new_name"
        return node

# Compile and execute a transformed AST
new_tree = ast.fix_missing_locations(tree)     # re-calculate line numbers
exec(compile(new_tree, "&lt;ast&gt;", "exec"))</code></pre>
<p>Uses: linters (flake8, ruff), autoformatters (black parses to AST), type checkers, security scanners (bandit), codemod tools (LibCST goes deeper). Safer than <code>exec</code> or <code>eval</code> on user input — you can validate the AST before running.</p>
'''

ANSWERS[67] = r'''
<p><code>random</code> provides pseudorandom numbers — great for simulations, games, sampling. <strong>Not cryptographically secure</strong> — use <code>secrets</code> for anything security-related.</p>
<pre><code>import random

# Basic
random.random()              # float in [0.0, 1.0)
random.uniform(1, 10)        # float in [1, 10]
random.randint(1, 6)         # int in [1, 6] — both inclusive
random.randrange(0, 100, 2)  # even int in [0, 100)

# Sequences
random.choice(["rock", "paper", "scissors"])
random.choices(["a", "b", "c"], weights=[3, 1, 1], k=5)    # with replacement
random.sample([1, 2, 3, 4, 5], k=3)                         # without replacement

# Shuffle in place
lst = [1, 2, 3, 4, 5]
random.shuffle(lst)

# Distributions
random.gauss(mu=0, sigma=1)
random.expovariate(lambd=1.5)
random.lognormvariate(mu=0, sigma=1)

# Reproducibility
random.seed(42)              # same sequence every run

# Independent generator
rng = random.Random(42)
rng.randint(1, 100)</code></pre>
<p>Uses the <strong>Mersenne Twister</strong> algorithm — fast, good statistical properties. Same seed → same sequence across platforms.</p>
<p>For NumPy arrays of random numbers: <code>numpy.random</code> with the newer Generator API (<code>np.random.default_rng()</code>).</p>
'''

ANSWERS[68] = r'''
<p><code>secrets</code> generates cryptographically strong random numbers — for passwords, tokens, API keys, anything security-sensitive. <strong>Never use <code>random</code> for these.</strong></p>
<pre><code>import secrets

# Random bytes
secrets.token_bytes(32)              # 32-byte random data

# URL-safe token (base64-ish, no +/=)
secrets.token_urlsafe(16)            # "OeqMntVoGKBa..."

# Hex
secrets.token_hex(16)                # "a3f4c8..."

# Random choice from a sequence — cryptographically uniform
secrets.choice(["admin", "user", "guest"])

# Compare without timing leaks
secrets.compare_digest("expected", user_input)    # constant-time

# Password reset token pattern
def generate_reset_token():
    return secrets.token_urlsafe(32)

# Session cookie
cookie_value = secrets.token_urlsafe(24)</code></pre>
<p>Why <code>random</code> is unsafe for security:</p>
<ul>
  <li>Mersenne Twister is deterministic — given enough output, you can predict future values.</li>
  <li>Internal state is 624 32-bit words; observing ~624 outputs compromises the entire sequence.</li>
</ul>
<p><code>secrets</code> uses the OS's cryptographic random source (<code>/dev/urandom</code> on Linux, <code>BCryptGenRandom</code> on Windows) — unpredictable even to attackers with significant knowledge. Slower but that's fine for these use cases.</p>
'''

ANSWERS[69] = r'''
<p>Python has a built-in <code>complex</code> type: real + imaginary parts. Full math support via the <code>cmath</code> module.</p>
<pre><code># Literal syntax — j for imaginary unit
z = 2 + 3j
type(z)                  # &lt;class 'complex'&gt;
z.real                   # 2.0
z.imag                   # 3.0
z.conjugate()            # (2-3j)

# Arithmetic — all operators work
(1 + 2j) * (3 + 4j)      # (-5+10j)
abs(3 + 4j)              # 5.0  (magnitude)

# cmath — math functions for complex numbers
import cmath
cmath.sqrt(-1)           # 1j
cmath.phase(1 + 1j)      # 0.7853... (π/4)
cmath.polar(1 + 1j)      # (1.414, 0.785) — (magnitude, phase)
cmath.rect(1, cmath.pi / 2)   # roughly 1j — from polar

# Real division
(1 + 2j) / (3 + 4j)      # (0.44+0.08j)</code></pre>
<p>Uses: signal processing (FFTs), control systems, electrical engineering (AC circuits), quantum computing, Mandelbrot generators. For numerical work with arrays of complex numbers, use NumPy — <code>numpy.fft</code>, element-wise operations, etc.</p>
<p>Note: regular <code>math</code> module doesn't accept complex; use <code>cmath</code>. Most math functions return complex even for real inputs (e.g., <code>cmath.sqrt(2)</code> returns <code>(1.414+0j)</code>).</p>
'''

ANSWERS[70] = r'''
<p><code>decimal</code> provides arbitrary-precision decimal arithmetic — exact representation of decimal fractions that floats can't represent. Essential for money and financial calculations.</p>
<pre><code>from decimal import Decimal, getcontext, ROUND_HALF_UP

# Float gotcha
0.1 + 0.2            # 0.30000000000000004
0.1 + 0.2 == 0.3     # False

# Decimal — exact
Decimal("0.1") + Decimal("0.2")      # Decimal('0.3')
Decimal("0.1") + Decimal("0.2") == Decimal("0.3")   # True

# Construct — ALWAYS from string for precision
Decimal(0.1)         # Decimal('0.10000000000000000555...') — float error leaks in
Decimal("0.1")       # Decimal('0.1') — exact

# Context controls precision and rounding
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

# Money computations
price = Decimal("19.99")
tax_rate = Decimal("0.0725")
total = (price * (1 + tax_rate)).quantize(Decimal("0.01"))   # round to cents</code></pre>
<p>When to use:</p>
<ul>
  <li><strong>Money</strong>, accounting, taxes — where cents matter.</li>
  <li><strong>Scientific calculations</strong> needing arbitrary precision (use <code>mpmath</code> for more).</li>
  <li>Any domain where <code>0.1 + 0.2 != 0.3</code> is unacceptable.</li>
</ul>
<p>Performance: Decimal is 10-100× slower than float. For bulk numeric work, keep using floats or scale to integer cents. Databases have DECIMAL types that map naturally — drivers convert them to Python <code>Decimal</code>.</p>
'''

ANSWERS[71] = r'''
<p>Covered from the basics in Python Basic Q94. Advanced concerns:</p>
<pre><code>from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo       # Python 3.9+

# Always use timezone-aware datetimes for anything user-facing
utc_now = datetime.now(timezone.utc)

# Arithmetic respects DST
nyc = ZoneInfo("America/New_York")
spring_forward = datetime(2024, 3, 10, 1, 30, tzinfo=nyc)   # day of spring forward
later = spring_forward + timedelta(hours=1)
# later.hour is 3, not 2 — clocks skipped 2 AM

# Difference between times
start = datetime(2024, 1, 1, tzinfo=timezone.utc)
end   = datetime(2024, 12, 31, tzinfo=timezone.utc)
diff  = end - start               # timedelta
diff.days                         # 365
diff.total_seconds()

# Cannot subtract naive and aware datetimes — TypeError
# Convert zones for display
nyc_time = utc_now.astimezone(nyc)

# ISO parsing (Python 3.7+ basic, 3.11+ more formats)
datetime.fromisoformat("2024-11-04T15:30:00+00:00")

# Arithmetic with "one month" — use dateutil.relativedelta
from dateutil.relativedelta import relativedelta
next_month = datetime.now() + relativedelta(months=1)</code></pre>
<p>Python 3.12+ has a new <code>Temporal</code>-style approach being discussed (PEP 692). Until then, <code>zoneinfo</code> is the modern recommendation over <code>pytz</code> — <code>pytz</code> has non-standard API (<code>localize()</code>) that leads to bugs.</p>
'''

ANSWERS[72] = r'''
<p><code>calendar</code> handles calendar math — day-of-week, leap years, month layouts, formatted calendar views.</p>
<pre><code>import calendar

# Day of week for a specific date
calendar.weekday(2024, 11, 4)        # 0=Monday, 6=Sunday
calendar.day_name[0]                  # "Monday"

# Leap year
calendar.isleap(2024)                 # True
calendar.leapdays(2020, 2025)         # 2 — count in range

# Number of days in a month
calendar.monthrange(2024, 2)          # (3, 29) — (first weekday, num days)

# Print-friendly views
print(calendar.month(2024, 11))
# November 2024
# Mo Tu We Th Fr Sa Su
#              1  2  3
#  4  5  6  7  8  9 10
# 11 12 13 14 15 16 17
# ...

print(calendar.calendar(2024))        # whole year

# HTMLCalendar — generate HTML tables
html = calendar.HTMLCalendar().formatmonth(2024, 11)

# Set first day of week (some cultures start Sunday)
calendar.setfirstweekday(calendar.SUNDAY)</code></pre>
<p>Common uses: date pickers, generating payroll schedules, business-day calculations (combined with holiday lists — the <code>holidays</code> package covers most countries), iCalendar generation (<code>icalendar</code> package).</p>
'''

ANSWERS[73] = r'''
<p><code>pytz</code> was the standard timezone library for years, but modern Python (3.9+) has <strong><code>zoneinfo</code></strong> built in — use it instead for new code.</p>
<pre><code># Modern — zoneinfo (3.9+)
from zoneinfo import ZoneInfo
from datetime import datetime

nyc = ZoneInfo("America/New_York")
dt = datetime(2024, 11, 4, 15, 30, tzinfo=nyc)
dt.astimezone(ZoneInfo("Asia/Tokyo"))     # convert
dt.tzname()                                # "EST" or "EDT" depending on date

# List timezones
import zoneinfo
zoneinfo.available_timezones()            # set of ~600 names

# pytz (legacy) — avoid for new code
import pytz
# Gotcha: pytz requires localize() for aware creation
nyc = pytz.timezone("America/New_York")
dt = nyc.localize(datetime(2024, 11, 4, 15, 30))   # NOT datetime(..., tzinfo=nyc)</code></pre>
<p>Why <code>zoneinfo</code> beats <code>pytz</code>:</p>
<ul>
  <li>Built into the standard library — no extra dependency.</li>
  <li>Standard <code>tzinfo</code> API — <code>datetime(..., tzinfo=nyc)</code> works correctly.</li>
  <li>Uses system tz database (IANA) by default on Linux/Mac; <code>tzdata</code> package for Windows or sandboxed environments.</li>
  <li>pytz's <code>localize()</code> / <code>normalize()</code> quirks are a documented source of bugs.</li>
</ul>
<p>Use <code>zoneinfo.ZoneInfo("Region/City")</code>. If you must target Python 3.8 or earlier, use <code>backports.zoneinfo</code> for the same API.</p>
'''

ANSWERS[74] = r'''
<p><code>http.client</code> is the low-level HTTP client in the stdlib — powers <code>urllib.request</code>. Rarely used directly; <code>requests</code> or <code>httpx</code> give a much nicer API.</p>
<pre><code>import http.client

conn = http.client.HTTPSConnection("api.example.com")
conn.request("GET", "/users/1", headers={"Authorization": "Bearer xyz"})
response = conn.getresponse()
print(response.status, response.reason)      # 200 OK
data = response.read().decode("utf-8")
conn.close()

# POST with body
import json
body = json.dumps({"name": "Ana"})
conn.request("POST", "/users", body=body, headers={
    "Content-Type": "application/json",
})

# Compared with requests — the same, much nicer
import requests
r = requests.get("https://api.example.com/users/1",
                 headers={"Authorization": "Bearer xyz"})
r.status_code; r.json()</code></pre>
<p>When to reach for <code>http.client</code>: avoiding third-party dependencies, working in restricted environments (e.g., building tooling for people with minimal Python installations). For anything real-world, use <strong><code>requests</code></strong> (synchronous) or <strong><code>httpx</code></strong> (sync + async, HTTP/2, modern).</p>
<p>Important: always set timeouts! <code>HTTPSConnection(..., timeout=10)</code> — without them, a hung server will hang your process indefinitely.</p>
'''

ANSWERS[75] = r'''
<p><code>socket</code> provides low-level network access. TCP server pattern: create a listening socket, accept connections, serve them.</p>
<pre><code>import socket

def start_tcp_server(host="127.0.0.1", port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)       # backlog of pending connections
        print(f"Listening on {host}:{port}")

        while True:
            conn, addr = server.accept()     # blocks until a client connects
            with conn:
                print(f"Connection from {addr}")
                while data := conn.recv(1024):
                    conn.sendall(data)        # echo

# For real concurrent servers, use:
# - threading: spawn a thread per connection (fine for dozens)
# - socketserver: stdlib wrapper (see Q97)
# - asyncio: asyncio.start_server (scales to tens of thousands)</code></pre>
<p>Caveats:</p>
<ul>
  <li><strong>Single-threaded by default</strong> — one connection at a time.</li>
  <li><strong><code>SO_REUSEADDR</code></strong> prevents "Address already in use" errors after a crash/restart.</li>
  <li><strong><code>conn.recv(N)</code></strong> may return fewer bytes than asked — loop until you have all expected data.</li>
  <li><strong>TCP has no message boundaries</strong> — if you send two <code>sendall</code>s they may arrive as one <code>recv</code>. Use a length prefix or delimiters.</li>
</ul>
<p>For real applications, prefer <code>asyncio</code> or higher-level frameworks (FastAPI, Flask, aiohttp).</p>
'''

ANSWERS[76] = r'''
<p>UDP is connectionless and unreliable — packets can be lost, duplicated, or reordered. Simpler than TCP; use where speed matters more than delivery guarantees (DNS, VoIP, games).</p>
<pre><code>import socket

def udp_server(host="127.0.0.1", port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        while True:
            data, addr = s.recvfrom(1024)       # read a single datagram
            print(f"From {addr}: {data!r}")
            s.sendto(b"ack", addr)               # reply

def udp_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(b"hello", (host, port))
        data, _ = s.recvfrom(1024)
        print(f"Got: {data!r}")</code></pre>
<p>Key differences vs TCP:</p>
<ul>
  <li><code>SOCK_DGRAM</code> not <code>SOCK_STREAM</code>.</li>
  <li>No <code>listen</code>/<code>accept</code> — just <code>recvfrom</code>.</li>
  <li>Each send is one packet — atomic, no stream.</li>
  <li>Typical MTU ~1500 bytes; larger packets get fragmented or dropped.</li>
</ul>
<p>Use UDP for: DNS queries, NTP, VoIP, real-time games, video streaming (some), service discovery (multicast), logging (syslog). For reliability on top of UDP, protocols like QUIC (HTTP/3) build acknowledgments and congestion control in userspace. For async UDP, use <code>asyncio.DatagramProtocol</code>.</p>
'''

ANSWERS[77] = r'''
<p>Flask is a minimal web framework — perfect for small to medium REST APIs. Modern production Python often uses FastAPI instead, but Flask remains extremely popular.</p>
<pre><code>from flask import Flask, request, jsonify

app = Flask(__name__)
users = {}

@app.get("/users")
def list_users():
    return jsonify(list(users.values()))

@app.get("/users/&lt;int:user_id&gt;")
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify(user)

@app.post("/users")
def create_user():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name required"}), 400
    uid = max(users, default=0) + 1
    users[uid] = {"id": uid, "name": data["name"]}
    return jsonify(users[uid]), 201

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)</code></pre>
<p>For production: don't run Flask's dev server — use a WSGI server like <strong>Gunicorn</strong> (<code>gunicorn -w 4 app:app</code>) behind a reverse proxy. Add <code>flask-restful</code> or <code>flask-smorest</code> for proper REST conventions, <code>flask-sqlalchemy</code> for DB, <code>flask-login</code> for sessions.</p>
<p>For modern async Python APIs, <strong>FastAPI</strong> is the better choice: built-in OpenAPI docs, Pydantic validation, async support, and similar Flask-like ergonomics.</p>
'''

ANSWERS[78] = r'''
<p>Several libraries. For async Python, <strong>websockets</strong> is the most popular; for Flask/Django-style frameworks, there are dedicated integrations.</p>
<pre><code>import asyncio
from websockets.asyncio.server import serve

connected = set()

async def handler(websocket):
    connected.add(websocket)
    try:
        async for message in websocket:
            # Broadcast to all connected clients
            for client in connected:
                await client.send(message)
    finally:
        connected.remove(websocket)

async def main():
    async with serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()       # run forever

asyncio.run(main())

# Client side
from websockets.asyncio.client import connect

async def client():
    async with connect("ws://localhost:8765") as ws:
        await ws.send("hello")
        print(await ws.recv())

asyncio.run(client())</code></pre>
<p>For non-async frameworks:</p>
<ul>
  <li><strong>Flask-SocketIO</strong> — socket.io protocol on top of Flask.</li>
  <li><strong>Channels</strong> for Django — adds ASGI + WebSockets.</li>
  <li><strong>FastAPI</strong> has built-in WebSocket support: <code>@app.websocket("/ws")</code>.</li>
</ul>
<p>Production: put WebSockets behind a reverse proxy that supports them (nginx with <code>proxy_http_version 1.1</code> and Upgrade/Connection headers). For horizontal scale, use a message broker (Redis pub/sub, NATS) so connections on different servers can communicate.</p>
'''

ANSWERS[79] = r'''
<p><code>xml.etree.ElementTree</code> (aka ET) is the stdlib XML parser — lightweight, convenient for most tasks. For very large documents, use iterative parsing; for XPath-heavy work, <code>lxml</code> is faster and more capable.</p>
<pre><code>import xml.etree.ElementTree as ET

xml_data = """
&lt;users&gt;
  &lt;user id="1"&gt;&lt;name&gt;Ana&lt;/name&gt;&lt;/user&gt;
  &lt;user id="2"&gt;&lt;name&gt;Bo&lt;/name&gt;&lt;/user&gt;
&lt;/users&gt;
"""

# Parse from string or file
root = ET.fromstring(xml_data)
tree = ET.parse("data.xml")
root = tree.getroot()

# Iterate
for user in root.findall("user"):
    uid = user.get("id")
    name = user.find("name").text
    print(uid, name)

# XPath (subset)
root.findall(".//user[@id='1']")

# Build
root = ET.Element("users")
user = ET.SubElement(root, "user", attrib={"id": "3"})
ET.SubElement(user, "name").text = "Cy"
tree = ET.ElementTree(root)
tree.write("out.xml", encoding="utf-8", xml_declaration=True)

# Streaming for huge files — don't load the whole tree
for event, elem in ET.iterparse("huge.xml", events=("end",)):
    if elem.tag == "record":
        process(elem)
        elem.clear()            # free memory</code></pre>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div><strong>XML parsing has security pitfalls.</strong> Default ElementTree is safe from common XXE attacks, but <code>xml.etree</code>, <code>xml.dom</code>, and <code>xml.sax</code> historically had vulnerabilities. For untrusted XML, use <code>defusedxml</code>.</div>
</div>
<p>For modern APIs, prefer JSON. XML persists in SOAP, RSS/Atom, SVG, Office documents, legacy enterprise systems.</p>
'''

ANSWERS[80] = r'''
<p>Covered in Python Basic Q91-93. Advanced topics for the <code>json</code> module:</p>
<pre><code>import json
from datetime import datetime, date
from decimal import Decimal

# Custom encoder for non-standard types
class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)        # or float(obj) if precision loss is OK
        if hasattr(obj, "__dict__"):
            return obj.__dict__    # for arbitrary objects
        return super().default(obj)

json.dumps(data, cls=ExtendedEncoder, indent=2)

# Custom decoder — convert fields back
def object_hook(d):
    if "created_at" in d:
        d["created_at"] = datetime.fromisoformat(d["created_at"])
    return d
json.loads(data, object_hook=object_hook)

# Parse very large files incrementally — ijson package
import ijson
with open("big.json", "rb") as f:
    for item in ijson.items(f, "items.item"):
        process(item)

# Performance — orjson is a drop-in C replacement, 5-10× faster
import orjson
orjson.dumps(data)             # returns bytes
orjson.loads(raw_bytes)</code></pre>
<p>Best practices:</p>
<ul>
  <li>Use <code>ensure_ascii=False</code> for Unicode-friendly output.</li>
  <li>Set <code>sort_keys=True</code> for deterministic output (git-friendly, easy diffs).</li>
  <li>For APIs, <code>pydantic</code> handles serialization + validation together.</li>
  <li>For huge data, stream with <code>ijson</code> or use a binary format (MessagePack, CBOR).</li>
</ul>
'''

ANSWERS[81] = r'''
<p><code>sqlite3</code> is Python's built-in SQLite driver. SQLite is a tiny embedded DB — a single file, no server, perfect for prototypes, config stores, caches, and many production apps.</p>
<pre><code>import sqlite3

# Connect — creates file if absent
conn = sqlite3.connect("app.db")
conn.row_factory = sqlite3.Row          # access columns by name
cur = conn.cursor()

# Schema
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        email  TEXT UNIQUE NOT NULL,
        name   TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert — ALWAYS use parameters, never format strings
cur.execute(
    "INSERT INTO users (email, name) VALUES (?, ?)",
    ("a@b.c", "Ana"),
)
conn.commit()

# Bulk insert
cur.executemany(
    "INSERT INTO users (email, name) VALUES (?, ?)",
    [("u@x.c", "U"), ("v@x.c", "V")],
)

# Query
for row in cur.execute("SELECT id, name FROM users WHERE name LIKE ?", ("%a%",)):
    print(row["id"], row["name"])

# Transaction context manager
with conn:
    conn.execute("UPDATE users SET name = ? WHERE id = ?", ("Ana2", 1))

conn.close()</code></pre>
<p>Security: SQL injection is the classic vuln. Use parameterized queries (<code>?</code> placeholders) — <em>never</em> f-strings or string concatenation with user input. Python 3.12+ also added <code>PRAGMA</code> support for WAL mode and other tuning.</p>
<p>For connection pooling, async, or Postgres features, move to SQLAlchemy or aiosqlite.</p>
'''

ANSWERS[82] = r'''
<p><code>psycopg2</code> (and its successor <code>psycopg3</code>) is the standard PostgreSQL driver.</p>
<pre><code># Modern psycopg3
import psycopg

with psycopg.connect("dbname=mydb user=alice password=...") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM users WHERE active = %s", (True,))
        for row in cur.fetchall():
            print(row)

# Connection pooling — use psycopg_pool for production
from psycopg_pool import ConnectionPool
pool = ConnectionPool("dbname=mydb", min_size=5, max_size=20)
with pool.connection() as conn:
    ...

# Async (psycopg3)
import asyncio
import psycopg
async def main():
    async with await psycopg.AsyncConnection.connect("...") as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            print(await cur.fetchone())

# COPY for bulk load — MUCH faster than many INSERTs
with cur.copy("COPY users (email, name) FROM STDIN") as copy:
    for email, name in records:
        copy.write_row([email, name])</code></pre>
<p>Parameter style: psycopg uses <code>%s</code>, not <code>?</code> — don't mistake for printf formatting. Always pass args as the second parameter to <code>execute</code>, not format the SQL string.</p>
<p>For higher-level access, use <code>SQLAlchemy</code> (ORM + Core). For async, <code>asyncpg</code> is faster than async psycopg for raw queries but has a different API. Most real apps pick psycopg3 (mature, sync+async, features) or SQLAlchemy (portable, abstracted).</p>
'''

ANSWERS[83] = r'''
<p><code>mysql-connector-python</code> is Oracle's official pure-Python MySQL driver. <code>PyMySQL</code> and <code>mysqlclient</code> (C) are alternatives.</p>
<pre><code>import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="alice",
    password="...",
    database="mydb",
    charset="utf8mb4",              # for full Unicode (incl. emoji)
)

cursor = conn.cursor(dictionary=True)    # rows as dicts

cursor.execute("SELECT id, name FROM users WHERE active = %s", (True,))
for row in cursor.fetchall():
    print(row["id"], row["name"])

# Parameterized insert
cursor.execute(
    "INSERT INTO users (email, name) VALUES (%s, %s)",
    ("a@b.c", "Ana"),
)
conn.commit()

# Bulk insert
cursor.executemany(
    "INSERT INTO users (email, name) VALUES (%s, %s)",
    rows,
)
conn.commit()

cursor.close()
conn.close()

# Connection pooling
from mysql.connector.pooling import MySQLConnectionPool
pool = MySQLConnectionPool(pool_size=10, pool_name="mypool", **config)
with pool.get_connection() as conn:
    ...</code></pre>
<p>Driver comparison:</p>
<ul>
  <li><strong>mysqlclient</strong> — C extension, fastest. Requires build tools for install.</li>
  <li><strong>mysql-connector-python</strong> — official, pure Python, no compile. Slightly slower.</li>
  <li><strong>PyMySQL</strong> — pure Python, widely used, simple.</li>
  <li><strong>aiomysql</strong> / <strong>asyncmy</strong> — async options.</li>
</ul>
<p>For production, prefer an ORM (SQLAlchemy) or at least a query builder. Handling MySQL's quirks directly (timezone handling, auto-reconnect, certificate pinning for SSL) is painful without one.</p>
'''

ANSWERS[84] = r'''
<p>SQLAlchemy is Python's dominant ORM and SQL toolkit. Two layers: <strong>Core</strong> (SQL expression language) and <strong>ORM</strong> (Python objects ↔ rows).</p>
<pre><code>from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id:    Mapped[int]  = mapped_column(primary_key=True)
    email: Mapped[str]  = mapped_column(String(255), unique=True)
    name:  Mapped[str]  = mapped_column(String(100))
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id:       Mapped[int] = mapped_column(primary_key=True)
    title:    Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author:   Mapped["User"] = relationship(back_populates="posts")

engine = create_engine("postgresql+psycopg://alice@localhost/mydb", echo=True)
Base.metadata.create_all(engine)

# CRUD with Session
with Session(engine) as session:
    ana = User(email="a@b.c", name="Ana")
    session.add(ana)
    session.commit()

    # Query
    stmt = select(User).where(User.name.like("A%"))
    for user in session.scalars(stmt):
        print(user.name)

    # Relationship lazy-loaded
    print(ana.posts)</code></pre>
<p>Essential features: connection pooling, schema migrations (via Alembic), eager loading (<code>selectinload</code>, <code>joinedload</code>), async support (<code>AsyncSession</code>). Core is powerful for data-heavy work where ORM overhead matters; ORM is cleaner for web-app CRUD.</p>
<p>Alternatives: <strong>Tortoise ORM</strong> (async-first), <strong>Peewee</strong> (lightweight), <strong>Django ORM</strong> (bundled with Django).</p>
'''

ANSWERS[85] = r'''
<p><code>aiomysql</code> is the asyncio wrapper around PyMySQL. For higher performance, <code>asyncmy</code> is a drop-in replacement with better speeds.</p>
<pre><code>import asyncio
import aiomysql

async def main():
    pool = await aiomysql.create_pool(
        host="localhost", user="alice", password="...", db="mydb",
        minsize=5, maxsize=20,
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name FROM users WHERE active = %s", (True,))
            async for row in cur:
                print(row)

            # Insert
            await cur.execute(
                "INSERT INTO users (email, name) VALUES (%s, %s)",
                ("a@b.c", "Ana"),
            )
            await conn.commit()
    pool.close()
    await pool.wait_closed()

asyncio.run(main())

# SQLAlchemy async for a nicer API
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine("mysql+aiomysql://alice@localhost/mydb")
async with AsyncSession(engine) as session:
    result = await session.execute(select(User))
    users = result.scalars().all()</code></pre>
<p>When to go async with databases:</p>
<ul>
  <li><strong>I/O-bound web apps</strong> with many concurrent connections — benefit is real.</li>
  <li><strong>Mixing with other async I/O</strong> (external APIs, Redis) — keeps the event loop fully utilized.</li>
</ul>
<p>When NOT to: simple scripts, CPU-bound workloads, existing sync codebases. The mental overhead and color-of-function problem make async cost real. For Postgres, <code>asyncpg</code> is significantly faster than <code>aiomysql</code> for its DB.</p>
'''

ANSWERS[86] = r'''
<p><code>requests</code> is the de-facto HTTP client — deliberately human-friendly API. <code>httpx</code> is the modern async-capable alternative with similar ergonomics.</p>
<pre><code>import requests

# Simple GET
r = requests.get("https://api.example.com/users/1",
                 params={"include": "posts"},
                 headers={"Accept": "application/json"},
                 timeout=10)           # ALWAYS set timeout
r.raise_for_status()                    # raises on 4xx/5xx
data = r.json()

# POST
r = requests.post("https://api.example.com/users",
                  json={"name": "Ana"},  # auto-sets Content-Type
                  auth=("user", "pass"))

# Session — connection pooling, persistent cookies
with requests.Session() as s:
    s.headers.update({"Authorization": "Bearer xyz"})
    s.get("https://api.example.com/a")
    s.get("https://api.example.com/b")   # reuses connection

# File upload
with open("file.pdf", "rb") as f:
    r = requests.post("https://upload", files={"file": f})

# Streaming for large downloads
with requests.get(url, stream=True) as r:
    with open("big.dat", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)</code></pre>
<p>Production concerns:</p>
<ul>
  <li><strong>Always timeout</strong> — missing timeouts hang your process on slow servers.</li>
  <li><strong>Retries</strong> — use <code>urllib3.util.Retry</code> with <code>HTTPAdapter</code> for exponential backoff.</li>
  <li><strong>Verify SSL</strong> — don't set <code>verify=False</code> outside of specific testing.</li>
  <li><strong>Rate limit respect</strong> — honor <code>Retry-After</code> and <code>X-RateLimit-*</code> headers.</li>
</ul>
<p>For async or HTTP/2, use <strong>httpx</strong>. For scraping workloads, <strong>aiohttp</strong> + concurrency.</p>
'''

ANSWERS[87] = r'''
<p><code>beautifulsoup4</code> parses HTML into a navigable tree — forgiving with malformed markup, intuitive API. Pair with <code>requests</code> for fetching.</p>
<pre><code>import requests
from bs4 import BeautifulSoup

r = requests.get("https://example.com")
soup = BeautifulSoup(r.text, "lxml")      # "lxml" is fastest parser

# Find elements
soup.title.text
soup.find("h1")
soup.find_all("a", class_="external")
soup.select("div.post &gt; h2")              # CSS selectors
soup.select_one("#header")

# Navigate
a = soup.find("a")
a["href"]
a.text.strip()
a.parent
a.find_next_sibling()

# Extract structured data
posts = []
for article in soup.select("article.post"):
    posts.append({
        "title": article.find("h2").text.strip(),
        "author": article.find("span", class_="author").text,
        "link": article.find("a")["href"],
    })

# Modify the tree
for img in soup.find_all("img"):
    img["loading"] = "lazy"
print(soup.prettify())</code></pre>
<p>Parsers:</p>
<ul>
  <li><strong>lxml</strong> — fastest, most forgiving. Recommended.</li>
  <li><strong>html.parser</strong> — stdlib, no install. Slower.</li>
  <li><strong>html5lib</strong> — HTML5-spec compliant, slowest but most forgiving.</li>
</ul>
<p>For modern sites with heavy JavaScript, <code>requests</code> + BS4 won't work — the DOM is built client-side. Use <strong>Playwright</strong> or <strong>Selenium</strong> to render first, then parse. Always check <code>robots.txt</code>, set a sensible <code>User-Agent</code>, rate-limit your requests, and honor the site's terms.</p>
'''

ANSWERS[88] = r'''
<p>Combine <code>aiohttp</code> (async HTTP) with BeautifulSoup for scraping at scale — fetch many pages concurrently without the overhead of threads.</p>
<pre><code>import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_page(session, url):
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
        return await r.text()

async def parse_page(session, url):
    html = await fetch_page(session, url)
    soup = BeautifulSoup(html, "lxml")
    return {
        "url": url,
        "title": soup.title.text.strip() if soup.title else None,
        "links": [a["href"] for a in soup.find_all("a", href=True)],
    }

async def scrape(urls, concurrency=10):
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Use a semaphore to cap concurrency inside gather
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded(url):
            async with semaphore:
                try:
                    return await parse_page(session, url)
                except Exception as e:
                    return {"url": url, "error": str(e)}

        return await asyncio.gather(*[bounded(u) for u in urls])

results = asyncio.run(scrape(urls))</code></pre>
<p>Benefits over threading: one event loop handles thousands of in-flight requests with minimal memory. BeautifulSoup itself is sync — but parsing is fast compared to network latency, so it runs in the event loop fine.</p>
<p>For CPU-heavy parsing of many pages, offload parsing to a <code>ProcessPoolExecutor</code>. For JavaScript-rendered pages, use <code>playwright-python</code> with async support. Respect <code>robots.txt</code> and set per-domain rate limits with a token bucket.</p>
'''

ANSWERS[89] = r'''
<p><code>http.server</code> provides a minimal HTTP server — useful for local development, ad-hoc file sharing, demos. <strong>Not for production.</strong></p>
<pre><code># One-liner: serve current directory
$ python -m http.server 8000
# Now http://localhost:8000 serves files from CWD

# Custom handler
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        # ... process ...
        self.send_response(201)
        self.end_headers()

    def log_message(self, format, *args):     # silence default logging
        pass

server = ThreadingHTTPServer(("0.0.0.0", 8000), MyHandler)
server.serve_forever()</code></pre>
<p><strong>Production warnings:</strong> single-threaded by default, no HTTPS without adding <code>ssl.wrap_socket</code>, no authentication, serves everything in the working directory including sensitive files if misconfigured. Use it for testing and personal projects only.</p>
<p>For real use, pick a proper framework (FastAPI, Flask, aiohttp) + a real WSGI/ASGI server (Gunicorn, uvicorn) behind a reverse proxy (nginx, Caddy).</p>
'''

ANSWERS[90] = r'''
<p><code>contextlib</code> provides utilities for creating and composing context managers — beyond just defining <code>__enter__</code>/<code>__exit__</code>.</p>
<pre><code>from contextlib import (
    contextmanager,
    closing,
    suppress,
    redirect_stdout, redirect_stderr,
    ExitStack,
    nullcontext,
)

# Generator → context manager (see Q11)
@contextmanager
def timer():
    start = time.perf_counter()
    yield
    print(f"{time.perf_counter() - start:.2f}s")

# Close things that have .close() but don't support 'with'
from urllib.request import urlopen
with closing(urlopen("https://...")) as page:
    data = page.read()

# Ignore specific exceptions
with suppress(FileNotFoundError):
    os.remove("maybe_gone")

# Redirect stdout
import io
buf = io.StringIO()
with redirect_stdout(buf):
    print("captured")
print(buf.getvalue())

# Dynamic stacking — variable number of contexts
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    # all closed at block exit

# Conditional context
def maybe_locked(use_lock):
    return lock if use_lock else nullcontext()

with maybe_locked(config.threaded):
    ...</code></pre>
<p>The standout is <strong><code>ExitStack</code></strong> — when you need to manage a variable number of contexts (a list of files of unknown count) or compose contexts dynamically based on runtime conditions. Avoids nested <code>with</code> pyramids.</p>
'''

ANSWERS[91] = r'''
<p><code>concurrent.futures</code> provides a high-level interface for thread and process pools. Simpler than raw <code>threading</code> or <code>multiprocessing</code> APIs.</p>
<pre><code>from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url):
    return requests.get(url).status_code

# submit + Future objects
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch, url): url for url in urls}
    for future in as_completed(futures):
        url = futures[future]
        try:
            status = future.result()
            print(url, status)
        except Exception as e:
            print(url, "failed:", e)

# map — parallel map, results in input order
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch, urls, timeout=30))

# Handle errors with map — they re-raise during iteration
try:
    for result in executor.map(fetch, urls):
        ...
except Exception as e:
    ...</code></pre>
<p>Sizing the pool:</p>
<ul>
  <li><strong>I/O-bound</strong> — <code>max_workers</code> can be much higher than CPU count. Tens to hundreds is reasonable.</li>
  <li><strong>CPU-bound</strong> — at most <code>os.cpu_count()</code> (but use <code>ProcessPoolExecutor</code> anyway).</li>
  <li><strong>Default</strong> — <code>min(32, os.cpu_count() + 4)</code>.</li>
</ul>
<p>Gotchas: exceptions from <code>submit</code> are hidden until you call <code>.result()</code>. Use <code>as_completed</code> when you want to process results as they arrive (instead of in input order).</p>
'''

ANSWERS[92] = r'''
<p><code>multiprocessing.Pool</code> is the classic interface — predates <code>ProcessPoolExecutor</code> and has a richer feature set for some use cases.</p>
<pre><code>from multiprocessing import Pool

def square(n):
    return n * n

with Pool(processes=4) as pool:
    # map — synchronous, in order
    results = pool.map(square, range(10))        # [0, 1, 4, 9, ...]

    # map_async — returns AsyncResult
    async_result = pool.map_async(square, range(100))
    results = async_result.get(timeout=10)

    # imap — iterator, lazy
    for result in pool.imap(square, range(1000)):
        print(result)

    # imap_unordered — as results complete, not in input order
    for result in pool.imap_unordered(square, range(1000)):
        print(result)

    # starmap — unpacks arg tuples
    pool.starmap(pow, [(2, 3), (3, 2), (10, 2)])    # [8, 9, 100]

    # apply_async — single task
    result = pool.apply_async(square, (42,))
    result.get(timeout=5)                            # 1764</code></pre>
<p>When to use <code>Pool</code> vs <code>ProcessPoolExecutor</code>: Pool is more flexible (unordered iteration, async variants, initializer function), ProcessPoolExecutor has a unified API shared with threads. Either works for most needs.</p>
<p>Pitfalls: functions passed to Pool workers must be <strong>picklable</strong> — no lambdas, no local functions. Module-level functions or callable classes only. On Windows, the entry point must be guarded by <code>if __name__ == "__main__":</code> because workers re-import the module.</p>
'''

ANSWERS[93] = r'''
<table>
  <thead><tr><th></th><th>ThreadPoolExecutor</th><th>ProcessPoolExecutor</th></tr></thead>
  <tbody>
    <tr><td>Parallelism</td><td>Concurrency via GIL rotation (I/O only)</td><td>True parallelism — one GIL per process</td></tr>
    <tr><td>Memory</td><td>Shared</td><td>Per-process; data pickled for transfer</td></tr>
    <tr><td>Startup cost</td><td>Fast (μs)</td><td>Slow (ms)</td></tr>
    <tr><td>Argument constraints</td><td>None</td><td>Must be picklable</td></tr>
    <tr><td>Best for</td><td>I/O-bound: HTTP, disk, DB</td><td>CPU-bound: numeric, image, data crunching</td></tr>
    <tr><td>Worst case</td><td>Doesn't help CPU-bound Python</td><td>Overhead dominates for tiny tasks</td></tr>
  </tbody>
</table>
<pre><code># Shared API — swap executor type, everything else stays
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def work(x):
    return x * 2

# For I/O-bound
with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(work, range(100)))

# For CPU-bound — drop-in replacement
with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(work, range(100)))

# Rule of thumb
# &gt; 50% time in Python/CPU → ProcessPool
# &gt; 50% time waiting on I/O → ThreadPool or asyncio</code></pre>
<p>For <strong>mixed workloads</strong>, combine: an async event loop handles I/O, with CPU-bound tasks dispatched to a ProcessPoolExecutor via <code>loop.run_in_executor()</code>. Measure before optimizing — thread vs process choice often matters less than choosing good algorithms.</p>
'''

ANSWERS[94] = r'''
<p>Covered in Q20 (high-level) and Q94 here focuses on advanced <code>subprocess</code> patterns — streams, pipes, async.</p>
<pre><code>import subprocess

# Pipe output between commands (equivalent of shell: ls | grep py)
ls = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
grep = subprocess.Popen(["grep", "py"], stdin=ls.stdout, stdout=subprocess.PIPE, text=True)
ls.stdout.close()         # let ls get SIGPIPE if grep exits
output, _ = grep.communicate()

# Real-time output streaming — don't buffer
with subprocess.Popen(["tail", "-f", "log.txt"], stdout=subprocess.PIPE, text=True) as p:
    for line in p.stdout:
        print(line, end="")

# Send input to stdin
result = subprocess.run(["wc", "-l"], input="a\nb\nc\n", text=True, capture_output=True)
print(result.stdout)      # "3"

# Long-running with timeout + cleanup
try:
    proc = subprocess.Popen(["long-task"])
    proc.wait(timeout=60)
except subprocess.TimeoutExpired:
    proc.terminate()       # SIGTERM
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()        # SIGKILL if SIGTERM ignored

# Async — asyncio.subprocess
import asyncio
async def run_async():
    proc = await asyncio.create_subprocess_exec(
        "ls", "-la",
        stdout=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return stdout.decode()</code></pre>
<p>Watch for deadlocks: if the child fills its stdout/stderr pipe buffer and you're only reading stdout, it blocks — use <code>communicate()</code> or read both streams concurrently. Environment isolation via <code>env={"PATH": ..., ...}</code>. Set <code>cwd=</code> to pick the working directory.</p>
'''

ANSWERS[95] = r'''
<p>Named pipes (FIFOs) are POSIX-only file-system entries for inter-process communication. Less common today than sockets or multiprocessing Queue, but still useful for shell-script interop.</p>
<pre><code>import os, errno

# Create a FIFO
path = "/tmp/my_pipe"
try:
    os.mkfifo(path, mode=0o600)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# Writer process
with open(path, "w") as fifo:
    fifo.write("hello\n")
    fifo.flush()

# Reader process (separate process)
with open(path, "r") as fifo:
    print(fifo.read())

# Cleanup
os.remove(path)

# Example: producer-consumer via FIFO
# Producer
with open(path, "w") as pipe:
    for i in range(10):
        pipe.write(f"item {i}\n")
        pipe.flush()

# Consumer
with open(path, "r") as pipe:
    for line in pipe:
        process(line.strip())</code></pre>
<p>Characteristics:</p>
<ul>
  <li><strong>POSIX-only</strong> — doesn't work on Windows (which has its own named pipes at <code>\\.\pipe\name</code>, accessible via <code>pywin32</code>).</li>
  <li><strong>Blocking</strong> — opening for read blocks until someone writes, and vice versa.</li>
  <li><strong>One-way</strong> — use two FIFOs for bidirectional communication.</li>
  <li><strong>File system persistence</strong> — the FIFO outlives processes; remove it when done.</li>
</ul>
<p>Alternatives: <code>multiprocessing.Pipe</code> (in-memory, bidirectional), Unix domain sockets (bidirectional, well-supported), or ZeroMQ for serious IPC needs.</p>
'''

ANSWERS[96] = r'''
<p>Covered extensively in Q22. Additional advanced patterns:</p>
<pre><code>import signal

# Signal flags pattern — set flag in handler, act in main loop
shutdown_flag = False
def on_shutdown(signum, frame):
    global shutdown_flag
    shutdown_flag = True
signal.signal(signal.SIGTERM, on_shutdown)
signal.signal(signal.SIGINT, on_shutdown)

while not shutdown_flag:
    do_work_step()

# Signal-aware context manager
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def handler(signum, frame):
        raise TimeoutError
    old_handler = signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

with timeout(5):
    long_running_task()

# Ignore a signal (Ctrl+C won't interrupt)
signal.signal(signal.SIGINT, signal.SIG_IGN)

# Reset to default behavior
signal.signal(signal.SIGINT, signal.SIG_DFL)

# asyncio signal handling
import asyncio
loop = asyncio.get_event_loop()
loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())</code></pre>
<p>Async signal handling is cleaner than sync: <code>add_signal_handler</code> schedules a callback on the event loop instead of interrupting arbitrary code. Essential for graceful shutdown of async servers.</p>
<p>Platform reminder: Windows lacks most signals. <code>SIGINT</code> and <code>SIGTERM</code> work; <code>SIGALRM</code> and others do not. Use threading.Timer for Windows-compatible timeouts.</p>
'''

ANSWERS[97] = r'''
<p><code>socketserver</code> is an older-style framework for writing custom network servers. Provides mixins for threading and forking.</p>
<pre><code>import socketserver

class EchoHandler(socketserver.StreamRequestHandler):
    def handle(self):
        # self.rfile and self.wfile are file-like wrappers around the socket
        for line in self.rfile:
            self.wfile.write(line)        # echo back

# Threading server — one thread per connection
class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

with ThreadedServer(("0.0.0.0", 9000), EchoHandler) as server:
    server.serve_forever()

# Handler types:
# - BaseRequestHandler: raw (socket_obj, ...)
# - StreamRequestHandler: TCP, with rfile/wfile
# - DatagramRequestHandler: UDP

# Server base classes:
# - TCPServer / UDPServer
# - UnixStreamServer / UnixDatagramServer (POSIX)

# Mixins:
# - ThreadingMixIn — one thread per request
# - ForkingMixIn — one process per request (POSIX)</code></pre>
<p>Good for: prototypes, teaching, one-off protocol servers, embedded tooling. Each connection gets its own handler instance, so state is per-connection.</p>
<p>For production, <strong>prefer <code>asyncio</code></strong>: <code>asyncio.start_server()</code> is more efficient (thousands of connections without OS threads) and integrates with modern Python async ecosystems. Full frameworks (aiohttp, FastAPI) layer HTTP-specific concerns on top.</p>
'''

ANSWERS[98] = r'''
<p><code>ssl</code> wraps sockets with TLS. Most code uses it indirectly via <code>requests</code>, <code>httpx</code>, or <code>aiohttp</code> — but direct use is sometimes needed.</p>
<pre><code>import ssl, socket

# Client — connect to HTTPS server manually
context = ssl.create_default_context()        # sane defaults (verify, modern TLS)
with socket.create_connection(("example.com", 443)) as sock:
    with context.wrap_socket(sock, server_hostname="example.com") as ssock:
        ssock.send(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        response = ssock.recv(4096)

# Server — serve TLS
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

with socket.socket() as server:
    server.bind(("0.0.0.0", 443))
    server.listen(5)
    while True:
        conn, addr = server.accept()
        with context.wrap_socket(conn, server_side=True) as tls_conn:
            handle(tls_conn)

# Mutual TLS (client certs)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(cafile="client-ca.crt")

# Custom trust (self-signed for dev — NOT production)
dev_context = ssl.create_default_context()
dev_context.check_hostname = False
dev_context.verify_mode = ssl.CERT_NONE</code></pre>
<p>Best practices:</p>
<ul>
  <li><strong>Use <code>create_default_context()</code></strong> — picks safe protocol versions and cipher suites.</li>
  <li><strong>Always verify certificates</strong> in production — <code>CERT_REQUIRED</code> + hostname check.</li>
  <li><strong>Keep <code>ssl</code> library updated</strong> — it wraps OpenSSL, which gets frequent security fixes.</li>
  <li><strong>Certificate rotation</strong> — use certbot (Let's Encrypt) or your cloud provider's managed certs.</li>
</ul>
<p>For HTTP-over-TLS, use <code>requests</code> or similar — they handle certificate verification, SNI, and session reuse correctly.</p>
'''

ANSWERS[99] = r'''
<p>Python 3.10+ discourages custom event loops — the defaults handle almost all needs. But the API exists for specialized integrations (game engines, GUI frameworks, high-performance servers).</p>
<pre><code>import asyncio

# Get the running loop (inside a coroutine)
async def main():
    loop = asyncio.get_running_loop()
    loop.call_later(1, lambda: print("delayed"))

# Use uvloop for better performance — drop-in replacement
# pip install uvloop
import asyncio
import uvloop
uvloop.install()                        # before asyncio.run
asyncio.run(main())                     # now uses uvloop under the hood

# In Python 3.11+:
asyncio.run(main(), loop_factory=uvloop.new_event_loop)

# Integrate with a GUI event loop (Tk example)
# Use libraries like asyncio-tkinter or qasync — don't write this by hand

# Custom executor for blocking code
def blocking_call():
    time.sleep(5)
    return "done"

async def use_executor():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, blocking_call)   # default ThreadPoolExecutor

# Low-level loop control (rarely needed)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(my_coroutine())
    loop.run_forever()
finally:
    loop.close()</code></pre>
<p>When you genuinely need a custom loop:</p>
<ul>
  <li><strong>uvloop</strong> — Cython-implemented loop, 2-4× faster for I/O-heavy workloads.</li>
  <li><strong>GUI integration</strong> — Qt, Tk, Gtk each have bridge libraries.</li>
  <li><strong>Game/real-time loops</strong> — integrate asyncio with a fixed-tick loop.</li>
</ul>
<p>For 99% of apps, <code>asyncio.run()</code> with its default policy is correct.</p>
'''

ANSWERS[100] = r'''
<p>Covered alongside Q24. For immutable data classes specifically, use <code>frozen=True</code>.</p>
<pre><code>from dataclasses import dataclass, field, replace
from typing import List

@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
p.x = 10       # FrozenInstanceError — attribute is read-only

# Making changes — replace produces a new instance
p2 = replace(p, x=10.0)   # Point(x=10.0, y=2.0)

# Mutable default — use default_factory
@dataclass(frozen=True)
class Config:
    name: str
    tags: tuple = ()          # tuple (immutable) for safety

# Nested frozen structures — deep immutability
@dataclass(frozen=True)
class Line:
    start: Point
    end: Point

line = Line(Point(0, 0), Point(1, 1))
# line.start.x = 5    # FrozenInstanceError

# Hashability — frozen dataclasses get __hash__ automatically
{p, Point(1.0, 2.0)}          # set with one element (they're equal + hashable)</code></pre>
<p>Benefits of immutability:</p>
<ul>
  <li><strong>Thread safety</strong> — no race conditions on attribute writes.</li>
  <li><strong>Hashable</strong> — usable as dict keys and set members.</li>
  <li><strong>Predictability</strong> — values don't mutate out from under you.</li>
  <li><strong>Value semantics</strong> — equality based on content, not identity.</li>
</ul>
<p>Caveats: attributes holding mutable objects (lists, dicts) are still mutable — use tuples, frozensets, or <code>immutables.Map</code>. For data models with validation, <code>pydantic</code> and <code>attrs</code> both support frozen modes with richer features.</p>
'''
