"""Python · Basic · Detailed answers. Each value is an HTML snippet."""

ANSWERS = {}

ANSWERS[1] = r'''
<p><strong>Python</strong> is a high-level, interpreted, general-purpose programming language. It's known for clean, readable syntax and a vast standard library that covers everything from web servers to statistics.</p>
<p>Key characteristics:</p>
<ul>
  <li><strong>Dynamically typed</strong> — variable types are resolved at runtime, not declared up front.</li>
  <li><strong>Interpreted</strong> — runs directly from source via the CPython interpreter (no separate compile step you manage yourself).</li>
  <li><strong>Multi-paradigm</strong> — supports procedural, object-oriented, and functional styles.</li>
  <li><strong>"Batteries included"</strong> — the standard library ships with modules for JSON, HTTP, sockets, testing, dates, and much more.</li>
</ul>
<pre><code>print("Hello, World!")</code></pre>
<p>It's widely used for data science, machine learning, web backends (Django, FastAPI), scripting, automation, and DevOps. The current major version is Python 3; Python 2 reached end-of-life in 2020.</p>
'''

ANSWERS[2] = r'''
<p>Installation differs by platform, but the recommended source is <a href="https://python.org/downloads">python.org</a>.</p>
<ul>
  <li><strong>Windows</strong> — download the installer from python.org. <strong>Important:</strong> check "Add Python to PATH" during setup.</li>
  <li><strong>macOS</strong> — download the installer from python.org, or use Homebrew: <code>brew install python</code>.</li>
  <li><strong>Linux</strong> — usually pre-installed. If not: <code>sudo apt install python3 python3-pip</code> (Debian/Ubuntu), <code>sudo dnf install python3 python3-pip</code> (Fedora).</li>
</ul>
<p>For managing multiple Python versions, use <strong>pyenv</strong> (Linux/macOS) or the official installer's "pylauncher" on Windows.</p>
<pre><code># Verify installation
python --version
# or on systems where python = Python 2:
python3 --version</code></pre>
<div class="callout callout-tip">
  <div class="callout-icon">i</div>
  <div>Avoid modifying your system Python. Use virtual environments (<code>python -m venv .venv</code>) for each project instead.</div>
</div>
'''

ANSWERS[3] = r'''
<p>Run <code>python --version</code> in a terminal (or <code>python3 --version</code> on systems where <code>python</code> still points to Python 2).</p>
<pre><code>$ python --version
Python 3.12.1

$ python3 --version
Python 3.12.1</code></pre>
<p>From inside Python itself:</p>
<pre><code>import sys
print(sys.version)
# 3.12.1 (main, Dec  7 2023, 20:45:44) [GCC 13.2.0]

print(sys.version_info)
# sys.version_info(major=3, minor=12, micro=1, releaselevel='final', serial=0)</code></pre>
<p>In scripts that need a minimum version, check programmatically:</p>
<pre><code>import sys
if sys.version_info &lt; (3, 10):
    raise RuntimeError("Python 3.10 or newer required")</code></pre>
'''

ANSWERS[4] = r'''
<p>Python's design emphasizes readability and programmer productivity. Core features:</p>
<ul>
  <li><strong>Readable syntax</strong> — indentation-based structure forces clean code.</li>
  <li><strong>Dynamic typing</strong> — fast prototyping; no type declarations required.</li>
  <li><strong>Automatic memory management</strong> — reference-counted garbage collection.</li>
  <li><strong>Rich standard library</strong> — covers I/O, math, networking, data formats, testing.</li>
  <li><strong>Huge ecosystem</strong> — PyPI hosts 500,000+ third-party packages.</li>
  <li><strong>Cross-platform</strong> — runs on Windows, macOS, Linux, BSD, and more with identical code.</li>
  <li><strong>Multi-paradigm</strong> — procedural, object-oriented, and functional all first-class.</li>
  <li><strong>Interoperability</strong> — easy C/C++ bindings (ctypes, CFFI, Cython), which is why NumPy and TensorFlow are fast.</li>
  <li><strong>Strong community</strong> — extensive docs, tutorials, Stack Overflow answers, mature tooling.</li>
</ul>
<p>Languages like Python trade raw execution speed for developer speed — which is why it dominates in data science and scripting, but less often in high-frequency trading or game engines.</p>
'''

ANSWERS[5] = r'''
<p><strong>PEP 8</strong> is Python's official style guide — rules for how Python code should be formatted to remain consistent and readable across projects.</p>
<p>Key conventions:</p>
<ul>
  <li><strong>Indentation</strong> — 4 spaces per level, never tabs.</li>
  <li><strong>Line length</strong> — 79 characters (99 for modern projects).</li>
  <li><strong>Naming</strong> — <code>snake_case</code> for functions/variables, <code>PascalCase</code> for classes, <code>UPPER_SNAKE_CASE</code> for constants.</li>
  <li><strong>Imports</strong> — one per line, grouped (standard lib → third-party → local), each group separated by a blank line.</li>
  <li><strong>Whitespace</strong> — spaces around operators (<code>a + b</code>, not <code>a+b</code>); no trailing whitespace.</li>
  <li><strong>Blank lines</strong> — two between top-level definitions, one between methods.</li>
</ul>
<pre><code># PEP 8-compliant
import os
import sys

from collections import Counter


def calculate_total(items: list[dict]) -&gt; float:
    return sum(item["price"] for item in items)


class ShoppingCart:
    def __init__(self):
        self.items = []</code></pre>
<p>Enforce it automatically with <strong>black</strong> (formatter) and <strong>ruff</strong> or <strong>flake8</strong> (linter). Consistent style reduces cognitive load in code review.</p>
'''

ANSWERS[6] = r'''
<p>Python's built-in data types fall into a few categories:</p>
<table>
  <thead><tr><th>Category</th><th>Types</th><th>Mutable?</th></tr></thead>
  <tbody>
    <tr><td>Numeric</td><td><code>int</code>, <code>float</code>, <code>complex</code></td><td>No</td></tr>
    <tr><td>Boolean</td><td><code>bool</code> (subclass of <code>int</code>)</td><td>No</td></tr>
    <tr><td>Sequence</td><td><code>str</code>, <code>tuple</code>, <code>range</code></td><td>No</td></tr>
    <tr><td>Sequence</td><td><code>list</code></td><td>Yes</td></tr>
    <tr><td>Mapping</td><td><code>dict</code></td><td>Yes</td></tr>
    <tr><td>Set</td><td><code>set</code></td><td>Yes</td></tr>
    <tr><td>Set</td><td><code>frozenset</code></td><td>No</td></tr>
    <tr><td>Binary</td><td><code>bytes</code>, <code>bytearray</code>, <code>memoryview</code></td><td>bytes: No; others: Yes</td></tr>
    <tr><td>None</td><td><code>NoneType</code></td><td>N/A</td></tr>
  </tbody>
</table>
<pre><code>x: int = 42
y: float = 3.14
name: str = "Ana"
items: list[int] = [1, 2, 3]
config: dict[str, int] = {"port": 8080}
tags: set[str] = {"python", "tutorial"}
coords: tuple[int, int] = (10, 20)
done: bool = True
nothing = None</code></pre>
<p>Check a type at runtime with <code>type(x)</code> or <code>isinstance(x, int)</code>. Everything in Python is an object, including numbers and functions.</p>
'''

ANSWERS[7] = r'''
<p>Python variables are declared by assignment — no keywords like <code>var</code> or <code>let</code>, no type declarations required.</p>
<pre><code>name = "Ana"          # str
age = 30              # int
price = 19.99         # float
is_active = True      # bool
tags = ["a", "b"]     # list</code></pre>
<p>The variable's type is determined by the value, and it can be reassigned to a different type:</p>
<pre><code>x = 42
x = "now a string"    # legal — Python is dynamically typed</code></pre>
<p><strong>Type hints</strong> (PEP 484) let you annotate types for readability and tooling. They don't affect runtime behavior but are checked by tools like <strong>mypy</strong> or <strong>pyright</strong>:</p>
<pre><code>name: str = "Ana"
age: int = 30
scores: list[float] = [4.5, 8.9, 3.2]</code></pre>
<p><strong>Multiple assignment</strong> and <strong>unpacking</strong> are idiomatic:</p>
<pre><code>a, b, c = 1, 2, 3
x = y = z = 0
first, *rest = [1, 2, 3, 4]    # first=1, rest=[2,3,4]</code></pre>
'''

ANSWERS[8] = r'''
<p>Python offers four common string-formatting approaches. <strong>f-strings are the modern default.</strong></p>
<pre><code>name, age = "Ana", 30

# 1. f-strings (Python 3.6+) — preferred
greeting = f"Hi {name}, you are {age}."

# 2. str.format()
greeting = "Hi {}, you are {}.".format(name, age)
greeting = "Hi {n}, you are {a}.".format(n=name, a=age)

# 3. % operator (old-style, C printf heritage)
greeting = "Hi %s, you are %d." % (name, age)

# 4. String concatenation (avoid for complex cases)
greeting = "Hi " + name + ", you are " + str(age) + "."</code></pre>
<p>f-strings support expressions, format specs, and even debugging:</p>
<pre><code>pi = 3.14159
f"Pi to 2 decimals: {pi:.2f}"        # "Pi to 2 decimals: 3.14"
f"Pad: |{name:&gt;10}|"                 # "Pad: |       Ana|"
f"Hex: {255:#x}"                     # "Hex: 0xff"
f"{name=}, {age=}"                   # "name='Ana', age=30"  (Python 3.8+ debug)</code></pre>
<div class="callout callout-tip">
  <div class="callout-icon">i</div>
  <div>f-strings are the fastest formatting option and the easiest to read. Use them unless you need dynamic format strings (stored as variables), in which case <code>.format()</code> or <code>%</code> fit better.</div>
</div>
'''

ANSWERS[9] = r'''
<p>Arithmetic in Python uses familiar operators with a few Python-specific behaviors.</p>
<pre><code>a, b = 10, 3

a + b      # 13   addition
a - b      # 7    subtraction
a * b      # 30   multiplication
a / b      # 3.333... (always float)
a // b     # 3    floor division (integer quotient)
a % b      # 1    modulo (remainder)
a ** b     # 1000 exponentiation
-a         # -10  unary negation
abs(-10)   # 10</code></pre>
<p>Key Python specifics:</p>
<ul>
  <li><code>/</code> always returns a float, even for integer operands (unlike some languages).</li>
  <li><code>//</code> floors toward negative infinity: <code>-7 // 2 == -4</code>, not <code>-3</code>.</li>
  <li>Integers have <strong>arbitrary precision</strong> — no overflow: <code>2 ** 1000</code> just works.</li>
  <li>Operator precedence follows standard math: <code>**</code> &gt; unary &gt; <code>*</code>/<code>/</code>/<code>//</code>/<code>%</code> &gt; <code>+</code>/<code>-</code>.</li>
</ul>
<p>For high-precision decimals (money) use the <code>decimal</code> module; for rationals use <code>fractions</code>:</p>
<pre><code>from decimal import Decimal
Decimal("0.1") + Decimal("0.2")    # Decimal('0.3') — no float rounding</code></pre>
'''

ANSWERS[10] = r'''
<p>Both are ordered sequences, but differ in mutability and typical use.</p>
<table>
  <thead><tr><th></th><th>list</th><th>tuple</th></tr></thead>
  <tbody>
    <tr><td>Syntax</td><td><code>[1, 2, 3]</code></td><td><code>(1, 2, 3)</code></td></tr>
    <tr><td>Mutable</td><td>Yes — add/remove/change items</td><td>No — fixed after creation</td></tr>
    <tr><td>Methods</td><td>Many (<code>append</code>, <code>sort</code>, <code>pop</code>, …)</td><td>Two (<code>count</code>, <code>index</code>)</td></tr>
    <tr><td>Memory</td><td>Slightly larger (over-allocates)</td><td>Smaller, more compact</td></tr>
    <tr><td>Hashable</td><td>No</td><td>Yes (if items are)</td></tr>
    <tr><td>Typical use</td><td>Homogeneous items you'll modify</td><td>Heterogeneous records; dict keys</td></tr>
  </tbody>
</table>
<pre><code>point = (10, 20)             # coordinates — fixed, tuple fits
users = ["Ana", "Bo", "Cy"]  # collection you'll grow — list fits

users.append("Dan")          # works
point[0] = 99                # TypeError: 'tuple' object does not support item assignment

# Tuples are hashable, so usable as dict keys:
regions = {(0, 0): "origin", (1, 0): "east"}</code></pre>
<p>Rule of thumb: if the collection won't change, a tuple communicates intent and is marginally faster. Otherwise, use a list.</p>
'''

ANSWERS[11] = r'''
<p>A <strong>dict</strong> is a mutable mapping of unique keys to values — Python's built-in hash table.</p>
<pre><code># Literal syntax
user = {"name": "Ana", "age": 30, "role": "admin"}

# Constructor with keyword args
user = dict(name="Ana", age=30, role="admin")

# From pairs
user = dict([("name", "Ana"), ("age", 30)])

# Empty then populate
user = {}
user["name"] = "Ana"</code></pre>
<p>Access, update, delete:</p>
<pre><code>user["name"]             # "Ana" — raises KeyError if missing
user.get("name")          # "Ana" — returns None if missing
user.get("email", "n/a")  # "n/a"

user["age"] = 31          # update
user["email"] = "a@b.co"  # add
del user["role"]          # remove

"name" in user            # True — membership test (keys)</code></pre>
<p>Useful methods: <code>keys()</code>, <code>values()</code>, <code>items()</code>, <code>update()</code>, <code>pop()</code>, <code>setdefault()</code>. Since Python 3.7, dicts preserve insertion order — iteration gives keys in the order they were added.</p>
<p><strong>Dict comprehensions</strong> mirror list comprehensions:</p>
<pre><code>squares = {n: n * n for n in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}</code></pre>
'''

ANSWERS[12] = r'''
<p>A <strong>set</strong> is an unordered collection of unique, hashable items — a mathematical set.</p>
<pre><code># Literal (empty set needs set() — {} is a dict)
tags = {"python", "tutorial", "beginner"}
empty = set()

# From iterable — dedupes automatically
unique = set([1, 2, 2, 3, 3, 3])    # {1, 2, 3}

# Comprehension
vowel_counts = {c for c in "mississippi" if c in "aeiou"}  # {'i'}</code></pre>
<p>Core operations run in O(1):</p>
<pre><code>tags.add("advanced")
tags.remove("beginner")       # raises KeyError if missing
tags.discard("xyz")           # silently ignores if missing
"python" in tags              # True</code></pre>
<p>Set algebra:</p>
<pre><code>a = {1, 2, 3}
b = {3, 4, 5}

a | b    # union         {1, 2, 3, 4, 5}
a &amp; b    # intersection  {3}
a - b    # difference    {1, 2}
a ^ b    # symmetric diff {1, 2, 4, 5}</code></pre>
<p>Use sets for deduplication, membership testing, and set math. For an immutable set (usable as a dict key), use <code>frozenset</code>.</p>
'''

ANSWERS[13] = r'''
<p>Use the <code>def</code> keyword; indent the body; optionally annotate types and return.</p>
<pre><code>def greet(name: str) -&gt; str:
    return f"Hello, {name}!"

greet("Ana")    # "Hello, Ana!"</code></pre>
<p>Features you'll use a lot:</p>
<pre><code># Default arguments
def connect(host: str, port: int = 8080) -&gt; None:
    print(f"Connecting to {host}:{port}")

# Keyword arguments
connect(host="localhost", port=3000)

# *args (variable positional), **kwargs (variable keyword)
def log(*values, sep: str = " ", level: str = "INFO") -&gt; None:
    print(f"[{level}] {sep.join(str(v) for v in values)}")

log("hello", "world", level="DEBUG")

# Positional-only (/) and keyword-only (*) parameters (Python 3.8+)
def divide(a, b, /, *, strict=True):
    # a, b positional only; strict keyword only
    if strict and b == 0:
        raise ValueError("div by zero")
    return a / b</code></pre>
<p>Functions are first-class: you can pass them as arguments, return them from other functions, and store them in data structures. Docstrings (the first string literal in the body) serve as inline docs and are accessible via <code>help(fn)</code>.</p>
'''

ANSWERS[14] = r'''
<p><code>return</code> exits a function and sends a value back to the caller.</p>
<pre><code>def add(a, b):
    return a + b

result = add(3, 4)    # 7</code></pre>
<p>Key behaviors:</p>
<ul>
  <li>A bare <code>return</code> (no value) returns <code>None</code>.</li>
  <li>A function with no <code>return</code> also returns <code>None</code>.</li>
  <li><code>return</code> can appear anywhere, ending execution at that point — useful for early exits (guard clauses).</li>
  <li>Return multiple values via a tuple:
    <pre><code>def divmod(a, b):
    return a // b, a % b    # packed into a tuple

quotient, remainder = divmod(17, 5)    # unpacks</code></pre>
  </li>
</ul>
<p><strong>Guard clause pattern</strong> — handle edge cases first, keep the happy path flat:</p>
<pre><code>def process(user):
    if user is None:
        return None
    if not user.is_active:
        return "inactive"
    # Happy path continues here without indentation
    return user.name.upper()</code></pre>
'''

ANSWERS[15] = r'''
<p>Wrap risky code in <code>try/except</code>. Handle specific exceptions; avoid catching everything.</p>
<pre><code>try:
    value = int(user_input)
except ValueError:
    print("Not a number")

# Catch multiple; access the exception object
try:
    result = 10 / divisor
    data = json.loads(payload)
except ZeroDivisionError:
    result = float("inf")
except json.JSONDecodeError as e:
    print(f"Bad JSON at pos {e.pos}: {e.msg}")

# Full shape: try / except / else / finally
try:
    f = open("data.txt")
except FileNotFoundError:
    log("missing")
else:
    # only if try succeeded
    content = f.read()
finally:
    # always runs — cleanup
    if "f" in locals():
        f.close()</code></pre>
<p><strong>Raise your own</strong>:</p>
<pre><code>if amount &lt; 0:
    raise ValueError(f"Amount must be non-negative, got {amount}")</code></pre>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div>Avoid bare <code>except:</code> or <code>except Exception:</code> — they swallow keyboard interrupts, bugs, and programmer errors. Catch the narrowest exception you can handle.</div>
</div>
'''

ANSWERS[16] = r'''
<p>Python has two loop constructs: <code>for</code> and <code>while</code>.</p>
<pre><code># for — iterate over a sequence or iterable
for name in ["Ana", "Bo", "Cy"]:
    print(name)

for i in range(5):
    print(i)    # 0 1 2 3 4

for i, name in enumerate(["Ana", "Bo"], start=1):
    print(i, name)    # 1 Ana, 2 Bo

for key, value in user.items():
    print(f"{key}: {value}")

# while — loop until a condition is false
count = 0
while count &lt; 5:
    print(count)
    count += 1</code></pre>
<p>Loop control:</p>
<ul>
  <li><code>break</code> exits the loop immediately.</li>
  <li><code>continue</code> skips to the next iteration.</li>
  <li><code>else</code> after the loop body runs if the loop completes <em>without</em> <code>break</code> — useful for search patterns.</li>
</ul>
<pre><code>for item in items:
    if item == target:
        print("found")
        break
else:
    print("not found")    # runs only if no break</code></pre>
<p>Pythonic idiom: iterate directly over a collection rather than indexing it (<code>for x in items</code>, not <code>for i in range(len(items))</code>).</p>
'''

ANSWERS[17] = r'''
<p><code>range()</code> generates an arithmetic progression — commonly used to drive loops a fixed number of times.</p>
<pre><code>range(5)          # 0, 1, 2, 3, 4
range(2, 7)       # 2, 3, 4, 5, 6
range(1, 10, 2)   # 1, 3, 5, 7, 9   (step = 2)
range(5, 0, -1)   # 5, 4, 3, 2, 1   (countdown)</code></pre>
<p>Common uses:</p>
<pre><code># Repeat N times
for _ in range(3):
    print("Hello")

# Index + value (prefer enumerate when you also want value)
for i in range(len(items)):
    print(i, items[i])

# Better
for i, v in enumerate(items):
    print(i, v)

# Populate a list
squares = [n * n for n in range(10)]</code></pre>
<p><code>range</code> is lazy (doesn't build a list in memory) — <code>range(10 ** 9)</code> takes constant memory. Convert to a list explicitly if needed:</p>
<pre><code>list(range(5))    # [0, 1, 2, 3, 4]</code></pre>
'''

ANSWERS[18] = r'''
<p>A <strong>module</strong> is a file containing Python definitions (functions, classes, variables) that can be imported and reused.</p>
<pre><code># math_utils.py
def add(a, b):
    return a + b

PI = 3.14159

# main.py
import math_utils
math_utils.add(2, 3)    # 5
math_utils.PI           # 3.14159</code></pre>
<p>A module is how you split code across files. Related modules can be grouped into a <strong>package</strong> — a directory with an <code>__init__.py</code> file (empty or with initialization code).</p>
<pre><code>my_app/
├── __init__.py
├── models.py
├── views.py
└── utils/
    ├── __init__.py
    └── strings.py

# Use it
from my_app.utils.strings import slugify</code></pre>
<p>Python's standard library is a collection of modules: <code>os</code>, <code>sys</code>, <code>json</code>, <code>datetime</code>, <code>collections</code>, etc. Third-party modules come from <strong>PyPI</strong> and are installed with <code>pip</code>.</p>
<p>When you import a module for the first time, its top-level code runs once — subsequent imports reuse the cached module object (<code>sys.modules</code>).</p>
'''

ANSWERS[19] = r'''
<p>Use the <code>import</code> statement in one of several forms:</p>
<pre><code># 1. Import the whole module
import math
math.sqrt(16)    # 4.0

# 2. Import with an alias
import numpy as np
np.array([1, 2, 3])

# 3. Import specific names
from datetime import datetime, timedelta
datetime.now()

# 4. Import all (avoid — pollutes namespace)
from os import *

# 5. Conditional import inside a function (for slow imports)
def process():
    import heavy_library
    heavy_library.do_stuff()</code></pre>
<p>Convention:</p>
<ul>
  <li>Group imports at the top of the file.</li>
  <li>Order: standard library → third-party → local, each group separated by a blank line.</li>
  <li>Alphabetize within each group.</li>
  <li>Avoid <code>from X import *</code> — it hides what's actually in scope.</li>
</ul>
<pre><code>import os
import sys

import requests
from fastapi import FastAPI

from .models import User
from .utils import slugify</code></pre>
<p>Tools like <strong>isort</strong> (or <strong>ruff</strong> with <code>--fix</code>) automate this ordering.</p>
'''

ANSWERS[20] = r'''
<p>Use <code>input()</code> — it blocks until the user presses Enter and returns a string.</p>
<pre><code>name = input("What's your name? ")
print(f"Hello, {name}!")

# Input is always a string — convert explicitly if you need a number
age_str = input("Age? ")
age = int(age_str)    # raises ValueError if not an integer

# Safer: validate + retry
while True:
    try:
        age = int(input("Age? "))
        break
    except ValueError:
        print("Please enter a valid integer")</code></pre>
<p>For scripts that read from standard input in bulk (piped data, multi-line input), use <code>sys.stdin</code>:</p>
<pre><code>import sys
for line in sys.stdin:
    print(line.strip().upper())</code></pre>
<p>For command-line arguments, use <code>sys.argv</code> or — for anything non-trivial — the <code>argparse</code> module:</p>
<pre><code>import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True)
args = parser.parse_args()
print(args.name)</code></pre>
<p>For hidden input (passwords), use <code>getpass.getpass()</code> so the input isn't echoed to the terminal.</p>
'''

ANSWERS[21] = r'''
<p>They test different things and catch different beginners.</p>
<table>
  <thead><tr><th></th><th><code>==</code></th><th><code>is</code></th></tr></thead>
  <tbody>
    <tr><td>Tests</td><td>Value equality</td><td>Object identity (same memory)</td></tr>
    <tr><td>Uses</td><td>Calls <code>__eq__</code></td><td>Compares <code>id(a) == id(b)</code></td></tr>
    <tr><td>Typical use</td><td>Comparing values</td><td>Comparing to <code>None</code>, singletons</td></tr>
  </tbody>
</table>
<pre><code>a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b    # True — same contents
a is b    # False — different list objects in memory
a is c    # True — same object

# Always use `is` for None, True, False
if user is None: ...
if flag is True: ...</code></pre>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div>Don't use <code>is</code> for numbers or strings — Python caches some small integers (-5 to 256) and interned strings, so <code>x is 257</code> can surprisingly be <code>False</code> while <code>x is 5</code> is <code>True</code>. Always use <code>==</code> for value comparison, reserve <code>is</code> for identity.</div>
</div>
'''

ANSWERS[22] = r'''
<p>Python uses <code>#</code> for single-line comments and triple-quoted strings for multi-line comments or docstrings.</p>
<pre><code># Single-line comment
x = 42    # Inline comment after code

# Multiple line comments — just multiple # lines
# This is line 1
# This is line 2

"""
Triple-quoted string used as a multi-line comment.
Technically it's a string literal, but if it's not
assigned to anything the interpreter discards it.
"""

def greet(name):
    """Return a greeting for the given name.

    This is a docstring — the first string literal in a
    function, class, or module. Accessible via help(greet)
    and tools like Sphinx.
    """
    return f"Hello, {name}!"</code></pre>
<p>Conventions:</p>
<ul>
  <li>Write comments to explain <em>why</em>, not <em>what</em>. Clean code rarely needs to restate mechanics.</li>
  <li>Keep them current — stale comments are worse than no comments.</li>
  <li>Use docstrings for public functions, classes, and modules. PEP 257 documents the style.</li>
  <li>TODO / FIXME / HACK tags are conventional and searchable.</li>
</ul>
<pre><code># TODO(ana): handle pagination when user list exceeds 1000
# FIXME: race condition when two requests hit this path</code></pre>
'''

ANSWERS[23] = r'''
<p>A <strong>list comprehension</strong> builds a list from an iterable with optional filtering and transformation — concise and faster than the equivalent <code>for</code> loop.</p>
<pre><code># Syntax: [expression for item in iterable if condition]

# Basic mapping
squares = [n * n for n in range(5)]
# [0, 1, 4, 9, 16]

# With a filter
evens = [n for n in range(10) if n % 2 == 0]
# [0, 2, 4, 6, 8]

# Transform + filter
names = ["Ana", "", "Bo", "  ", "Cy"]
cleaned = [n.strip().upper() for n in names if n.strip()]
# ['ANA', 'BO', 'CY']

# Nested — flatten
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [x for row in matrix for x in row]
# [1, 2, 3, 4, 5, 6]</code></pre>
<p>Sibling forms:</p>
<pre><code># Set comprehension
unique_lengths = {len(w) for w in words}

# Dict comprehension
word_lengths = {w: len(w) for w in words}

# Generator expression (lazy, no brackets)
total = sum(n * n for n in range(1_000_000))    # no list built</code></pre>
<div class="callout callout-tip">
  <div class="callout-icon">i</div>
  <div>If a comprehension spans more than two lines or nests more than two <code>for</code> clauses, use a regular loop. Readability beats cleverness.</div>
</div>
'''

ANSWERS[24] = r'''
<p>Two options, depending on whether you want to change the original list.</p>
<pre><code>items = [3, 1, 4, 1, 5, 9, 2, 6]

# 1. In-place — modifies the original
items.sort()
print(items)    # [1, 1, 2, 3, 4, 5, 6, 9]

# 2. Return a new sorted list
items = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_items = sorted(items)
# items unchanged; sorted_items is new

# Descending
items.sort(reverse=True)
sorted(items, reverse=True)

# Sort by a key function
users = [{"name": "Ana", "age": 30}, {"name": "Bo", "age": 25}]
users.sort(key=lambda u: u["age"])
# [{name: Bo, age: 25}, {name: Ana, age: 30}]

# Sort by multiple keys (use a tuple in the key)
users.sort(key=lambda u: (u["age"], u["name"]))

# Sort case-insensitively
names = ["ana", "Bo", "cy"]
names.sort(key=str.lower)</code></pre>
<p><strong>Which to pick</strong>: use <code>sorted()</code> when you want to keep the original (or sort any iterable like a tuple or dict values). Use <code>.sort()</code> when you already have a list and mutation is fine. Both are stable — items with equal keys preserve their relative order.</p>
'''

ANSWERS[25] = r'''
<p>A <strong>lambda</strong> is a small anonymous function — one expression, no name.</p>
<pre><code># Equivalent: def add(a, b): return a + b
add = lambda a, b: a + b
add(2, 3)    # 5</code></pre>
<p>Typical use is as an argument to higher-order functions:</p>
<pre><code># Sort by a computed key
users.sort(key=lambda u: u.age)

# Filter
over_18 = list(filter(lambda u: u.age &gt;= 18, users))

# Map
lengths = list(map(lambda s: len(s), words))</code></pre>
<p>Restrictions:</p>
<ul>
  <li>Only a single expression — no <code>return</code>, no <code>if/else</code> statement (ternary is fine), no loops.</li>
  <li>No docstring, no annotations.</li>
</ul>
<div class="callout callout-info">
  <div class="callout-icon">?</div>
  <div>Pythonic style prefers <code>def</code> for anything non-trivial. <code>map</code> and <code>filter</code> are often clearer as list comprehensions: <code>[len(s) for s in words]</code> beats <code>list(map(lambda s: len(s), words))</code>.</div>
</div>
<p>Lambdas shine as ad-hoc keys for sorting, as simple event handlers, and in functional-style data pipelines.</p>
'''

ANSWERS[26] = r'''
<p>Use the <code>class</code> keyword. The constructor is <code>__init__</code>; the instance is referenced as <code>self</code>.</p>
<pre><code>class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def greet(self) -&gt; str:
        return f"Hello, I'm {self.name}"

    def __repr__(self) -&gt; str:
        return f"User(name={self.name!r}, email={self.email!r})"


u = User("Ana", "ana@example.com")
u.greet()    # "Hello, I'm Ana"
print(u)     # User(name='Ana', email='ana@example.com')</code></pre>
<p>Common dunder ("double under") methods:</p>
<ul>
  <li><code>__init__</code> — initializer, runs after the object is created.</li>
  <li><code>__repr__</code> — developer-readable string (for debugging).</li>
  <li><code>__str__</code> — user-readable string (for <code>print</code>).</li>
  <li><code>__eq__</code>, <code>__hash__</code> — equality and hashing.</li>
  <li><code>__len__</code>, <code>__iter__</code>, <code>__contains__</code> — make your class behave like a collection.</li>
</ul>
<p>For simple data-holding classes, the <code>dataclass</code> decorator generates <code>__init__</code>, <code>__repr__</code>, <code>__eq__</code> automatically:</p>
<pre><code>from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str</code></pre>
'''

ANSWERS[27] = r'''
<p><code>self</code> is the reference to the current instance, passed implicitly as the first argument when you call a method on an instance.</p>
<pre><code>class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def get(self):
        return self.count


c = Counter()
c.increment()      # Python translates this to Counter.increment(c)
c.get()            # 1</code></pre>
<p>How it works:</p>
<ul>
  <li>When you call <code>c.increment()</code>, Python looks up <code>increment</code> on the class, then calls <code>Counter.increment(c)</code> — binding <code>c</code> to the first parameter.</li>
  <li>The name <code>self</code> is a convention — any name would work — but stick to <code>self</code> for readability. PEP 8 enforces this.</li>
  <li>Without <code>self</code>, a method has no way to access the instance's attributes or call other methods on it.</li>
</ul>
<p><strong>Class methods</strong> use <code>cls</code> (the class itself); <strong>static methods</strong> take neither:</p>
<pre><code>class Config:
    default_port = 8080

    @classmethod
    def create_default(cls):
        return cls()                # use cls to construct

    @staticmethod
    def is_valid_port(port):
        return 0 &lt; port &lt; 65536     # no instance or class state</code></pre>
'''

ANSWERS[28] = r'''
<p>Call the class like a function — Python invokes <code>__init__</code> on a newly created object.</p>
<pre><code>class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages


# Create an instance
b1 = Book("Dune", "Frank Herbert", 688)
b2 = Book("1984", "George Orwell", 328)

print(b1.title)         # Dune
print(b2.pages)         # 328
print(type(b1))         # &lt;class '__main__.Book'&gt;
print(isinstance(b1, Book))    # True</code></pre>
<p>Behind the scenes:</p>
<ol>
  <li><code>Book(...)</code> calls <code>Book.__call__(...)</code> (inherited from the metaclass).</li>
  <li>That calls <code>Book.__new__(Book)</code>, which allocates a new, empty object.</li>
  <li>Then <code>Book.__init__(instance, "Dune", ...)</code> initializes it.</li>
  <li>The instance is returned.</li>
</ol>
<p>Each instance has its own attributes (<code>self.title</code>, etc.) but shares methods defined on the class. You can also add attributes after creation — Python is flexible:</p>
<pre><code>b1.rating = 5    # dynamically add an attribute (not in __init__)</code></pre>
<p>This flexibility is powerful but can hide bugs; tools like <strong>pydantic</strong> and <strong>dataclass(slots=True)</strong> restrict which attributes are allowed.</p>
'''

ANSWERS[29] = r'''
<p>Class and instance variables live in different places and serve different purposes.</p>
<pre><code>class Dog:
    species = "Canis familiaris"    # class variable — shared by all instances

    def __init__(self, name, age):
        self.name = name    # instance variable — unique per instance
        self.age = age


a = Dog("Rex", 3)
b = Dog("Buddy", 5)

a.name, b.name        # "Rex", "Buddy"        — per instance
a.species, b.species  # "Canis familiaris" both — from the class</code></pre>
<p>Resolution rules:</p>
<ul>
  <li>When you read an attribute, Python looks on the instance first, then the class.</li>
  <li>When you write, Python <em>always</em> creates/updates an instance attribute — it doesn't mutate the class:
    <pre><code>a.species = "wolfdog"    # creates a new instance attribute on `a`
b.species                 # still "Canis familiaris"
Dog.species               # still "Canis familiaris"</code></pre>
  </li>
</ul>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div><strong>Gotcha:</strong> if a class variable is <em>mutable</em> (like a list), all instances share it:
<pre><code>class Bad:
    items = []    # SHARED

a = Bad()
a.items.append(1)
Bad().items    # [1] — leaked!</code></pre>
Initialize mutable state in <code>__init__</code> instead.</div>
</div>
'''

ANSWERS[30] = r'''
<p><strong>Inheritance</strong> lets a class derive from another, gaining its methods and attributes while being able to add or override behavior.</p>
<pre><code>class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Some sound"


class Dog(Animal):
    def speak(self):
        return "Woof!"        # override

    def fetch(self):
        return f"{self.name} fetches the ball"


class Puppy(Dog):
    def speak(self):
        return super().speak() + " (tiny)"    # extend parent


d = Dog("Rex")
d.speak()     # "Woof!"
d.fetch()     # "Rex fetches the ball"

p = Puppy("Bean")
p.speak()     # "Woof! (tiny)"
isinstance(p, Dog)       # True
isinstance(p, Animal)    # True — transitive</code></pre>
<p>Key features:</p>
<ul>
  <li><code>super()</code> calls the parent's version of a method — critical for <code>__init__</code> chaining.</li>
  <li><strong>Multiple inheritance</strong> is supported: <code>class Child(A, B):</code>. Resolution follows the <strong>MRO</strong> (Method Resolution Order), computable via <code>Child.__mro__</code>.</li>
  <li><strong>Composition over inheritance</strong> — for most production code, &ldquo;has-a&rdquo; (composition) scales better than &ldquo;is-a&rdquo; (inheritance). Use inheritance for genuine taxonomies.</li>
</ul>
<p>Abstract base classes (<code>abc.ABC</code>) let you declare &ldquo;subclasses must implement this method&rdquo;:</p>
<pre><code>from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...</code></pre>
'''

ANSWERS[31] = r'''
<p>Define a method with the same name in the subclass. When called on an instance, Python walks the MRO and uses the subclass's version.</p>
<pre><code>class Vehicle:
    def describe(self):
        return "A vehicle"

    def start(self):
        return "Starting engine..."


class Car(Vehicle):
    def describe(self):
        return "A car"        # overrides Vehicle.describe

    def start(self):
        # Extend rather than replace — call parent first
        parent_msg = super().start()
        return f"{parent_msg} Vroom!"


c = Car()
c.describe()    # "A car"
c.start()       # "Starting engine... Vroom!"</code></pre>
<p>Tips:</p>
<ul>
  <li>Use <code>super().method()</code> when you want to <em>extend</em> the parent's behavior, not replace it entirely.</li>
  <li>Keep the overridden method's signature compatible with the parent's — otherwise it breaks polymorphism (and Liskov substitution).</li>
  <li>Mark overrides explicitly with the <code>@override</code> decorator from <code>typing</code> (Python 3.12+) so a typo causes a type-check failure:
    <pre><code>from typing import override

class Car(Vehicle):
    @override
    def describe(self): ...</code></pre>
  </li>
</ul>
'''

ANSWERS[32] = r'''
<p>A <strong>decorator</strong> is a function that takes another function and returns a (usually modified) function. Decorators are a clean way to wrap behavior around functions or methods without changing their code.</p>
<pre><code>import time
from functools import wraps

def timer(fn):
    @wraps(fn)                           # preserves fn's name and docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{fn.__name__} took {elapsed:.3f}s")
        return result
    return wrapper


@timer
def slow_task():
    time.sleep(1)
    return "done"


slow_task()
# slow_task took 1.001s
# 'done'</code></pre>
<p>The <code>@timer</code> syntax is sugar for <code>slow_task = timer(slow_task)</code>.</p>
<p>Common built-in decorators:</p>
<ul>
  <li><code>@staticmethod</code>, <code>@classmethod</code> — change how a method is called.</li>
  <li><code>@property</code> — turns a method into a read-only attribute.</li>
  <li><code>@functools.lru_cache</code> — memoizes function results.</li>
  <li><code>@dataclasses.dataclass</code> — generates boilerplate for data classes.</li>
</ul>
<p>Decorators that accept arguments are a common pattern — wrap the real decorator in another function that captures the arguments.</p>
'''

ANSWERS[33] = r'''
<p><code>map(fn, iterable)</code> applies <code>fn</code> to each item of the iterable, returning a <strong>lazy iterator</strong>. You typically convert the result to a list or iterate it.</p>
<pre><code># Square each number
nums = [1, 2, 3, 4]
squared = list(map(lambda n: n * n, nums))
# [1, 4, 9, 16]

# Apply a named function
def celsius_to_f(c):
    return c * 9 / 5 + 32

temps_c = [0, 20, 100]
temps_f = list(map(celsius_to_f, temps_c))
# [32.0, 68.0, 212.0]

# Multiple iterables — fn receives one item from each
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
# [11, 22, 33]</code></pre>
<p><strong>Pythonic alternative:</strong> list comprehensions usually beat <code>map</code> for readability:</p>
<pre><code>squared = [n * n for n in nums]
# Equivalent; clearer; same speed</code></pre>
<p>Use <code>map</code> when you already have a named function you want to apply — <code>list(map(str.upper, words))</code> is tidier than <code>[s.upper() for s in words]</code>. Otherwise, prefer comprehensions.</p>
'''

ANSWERS[34] = r'''
<p>Both are higher-order functions on iterables, but they do different things.</p>
<table>
  <thead><tr><th></th><th><code>map(fn, items)</code></th><th><code>filter(fn, items)</code></th></tr></thead>
  <tbody>
    <tr><td>Purpose</td><td>Transform each item</td><td>Keep items where fn returns truthy</td></tr>
    <tr><td>Function signature</td><td>Any → any</td><td>Any → bool (predicate)</td></tr>
    <tr><td>Result size</td><td>Same as input</td><td>Less than or equal to input</td></tr>
    <tr><td>Each item in output is</td><td>fn(item)</td><td>Original item</td></tr>
  </tbody>
</table>
<pre><code>nums = [1, 2, 3, 4, 5]

# map — transform
list(map(lambda n: n * 2, nums))      # [2, 4, 6, 8, 10]

# filter — select
list(filter(lambda n: n % 2 == 0, nums))    # [2, 4]

# Combine — filter, then map
evens_squared = list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums)))
# [4, 16]

# Pythonic equivalents — usually clearer
doubled = [n * 2 for n in nums]
evens = [n for n in nums if n % 2 == 0]
evens_squared = [n * n for n in nums if n % 2 == 0]</code></pre>
<p>Both return lazy iterators in Python 3, so wrap with <code>list()</code> if you need a concrete list. For readability, most Pythonistas prefer list comprehensions over <code>map</code>/<code>filter</code>.</p>
'''

ANSWERS[35] = r'''
<p><code>reduce(fn, iterable, initial=...)</code> boils an iterable down to a single value by repeatedly applying a two-argument function. It's in <code>functools</code> (not a built-in in Python 3).</p>
<pre><code>from functools import reduce

# Sum — classic example
nums = [1, 2, 3, 4]
total = reduce(lambda acc, x: acc + x, nums, 0)
# Step by step:
#   acc=0, x=1 → 1
#   acc=1, x=2 → 3
#   acc=3, x=3 → 6
#   acc=6, x=4 → 10

# Max
max_val = reduce(lambda a, b: a if a &gt; b else b, nums)
# 4

# Flatten a list of lists
from operator import iconcat
flat = reduce(iconcat, [[1, 2], [3, 4], [5]], [])
# [1, 2, 3, 4, 5]

# Build a nested key path on a dict
def get_path(data, path):
    return reduce(lambda d, k: d[k], path, data)

config = {"db": {"pg": {"host": "localhost"}}}
get_path(config, ["db", "pg", "host"])    # "localhost"</code></pre>
<p><strong>Python style:</strong> Guido himself removed <code>reduce</code> from built-ins because <code>sum</code>, <code>min</code>, <code>max</code>, <code>any</code>, <code>all</code>, and explicit loops cover 99% of use cases more clearly. Reach for <code>reduce</code> when no simpler alternative fits — often in functional-style pipelines.</p>
'''

ANSWERS[36] = r'''
<p>Python's four built-in collection types:</p>
<table>
  <thead><tr><th>Type</th><th>Ordered</th><th>Mutable</th><th>Duplicates</th><th>Indexed</th></tr></thead>
  <tbody>
    <tr><td><code>list</code></td><td>Yes</td><td>Yes</td><td>Yes</td><td>By int position</td></tr>
    <tr><td><code>tuple</code></td><td>Yes</td><td>No</td><td>Yes</td><td>By int position</td></tr>
    <tr><td><code>dict</code></td><td>Yes (3.7+)</td><td>Yes</td><td>Keys unique</td><td>By key</td></tr>
    <tr><td><code>set</code></td><td>No</td><td>Yes</td><td>No</td><td>No</td></tr>
  </tbody>
</table>
<pre><code>grades = [90, 85, 88]          # ordered collection
point = (10, 20)                # fixed record
user = {"name": "Ana"}         # key → value
tags = {"py", "beginner"}       # unique collection</code></pre>
<p>The <strong><code>collections</code> module</strong> adds specialized variants used constantly in production:</p>
<ul>
  <li><code>defaultdict</code> — dict with a default value for missing keys.</li>
  <li><code>Counter</code> — dict subclass for counting hashable items (<code>Counter("mississippi")</code>).</li>
  <li><code>deque</code> — double-ended queue with O(1) append/pop at both ends.</li>
  <li><code>OrderedDict</code> — same as dict now that dicts are ordered, but has extra methods.</li>
  <li><code>namedtuple</code> — lightweight tuple with named fields.</li>
  <li><code>ChainMap</code> — layered view over multiple mappings.</li>
</ul>
<pre><code>from collections import Counter, defaultdict

Counter("mississippi").most_common(3)    # [('i', 4), ('s', 4), ('p', 2)]

by_tag = defaultdict(list)
by_tag["python"].append("tutorial")      # no KeyError first time</code></pre>
'''

ANSWERS[37] = r'''
<p>Use the <code>open()</code> built-in. Always use it in a <code>with</code> statement so the file closes automatically, even if an exception fires.</p>
<pre><code># Read the whole file as one string
with open("poem.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Iterate line by line (memory-efficient for large files)
with open("log.txt", encoding="utf-8") as f:
    for line in f:
        print(line.rstrip())

# Read all lines into a list
with open("names.txt", encoding="utf-8") as f:
    names = f.readlines()    # ['Ana\n', 'Bo\n', ...]

# Read N bytes at a time
with open("data.bin", "rb") as f:
    while chunk := f.read(4096):
        process(chunk)</code></pre>
<p>Mode strings:</p>
<ul>
  <li><code>"r"</code> — read text (default).</li>
  <li><code>"w"</code> — write, truncating the file.</li>
  <li><code>"a"</code> — append.</li>
  <li><code>"x"</code> — exclusive create, fails if the file exists.</li>
  <li>Append <code>"b"</code> for binary (<code>"rb"</code>, <code>"wb"</code>) — don't decode as text.</li>
</ul>
<div class="callout callout-tip">
  <div class="callout-icon">i</div>
  <div>Always pass <code>encoding="utf-8"</code> explicitly — the default is platform-dependent and has bitten countless programs on Windows.</div>
</div>
'''

ANSWERS[38] = r'''
<p>Open the file in write or append mode and call <code>.write()</code> or <code>.writelines()</code>.</p>
<pre><code># Overwrite (or create) the file with a single string
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")
    f.write("Second line\n")

# Append instead of overwrite
with open("log.txt", "a", encoding="utf-8") as f:
    f.write(f"{datetime.now().isoformat()} - event fired\n")

# Write a list of lines — note: no newlines are added for you
lines = ["first\n", "second\n", "third\n"]
with open("out.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)

# Binary write
with open("image.png", "wb") as f:
    f.write(image_bytes)

# JSON — use json module, not manual formatting
import json
with open("user.json", "w", encoding="utf-8") as f:
    json.dump({"name": "Ana", "age": 30}, f, indent=2)

# CSV — use csv module
import csv
with open("users.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "age"])
    w.writerows([["Ana", 30], ["Bo", 25]])</code></pre>
<p>Writes are usually buffered; the buffer flushes when the file closes (the <code>with</code> block handles this). For critical data, call <code>f.flush()</code> and <code>os.fsync(f.fileno())</code> to guarantee the OS has persisted it.</p>
'''

ANSWERS[39] = r'''
<p>Both read a text file, but they return different shapes and differ in memory behavior.</p>
<table>
  <thead><tr><th></th><th><code>read()</code></th><th><code>readlines()</code></th></tr></thead>
  <tbody>
    <tr><td>Returns</td><td>One string (whole file)</td><td>List of strings, one per line</td></tr>
    <tr><td>Newlines</td><td>Included as-is</td><td>Each line keeps its trailing <code>\n</code></td></tr>
    <tr><td>Memory</td><td>Loads entire file at once</td><td>Loads entire file at once</td></tr>
    <tr><td>Typical use</td><td>Small files, simple search</td><td>When you need line-level access</td></tr>
  </tbody>
</table>
<pre><code>with open("poem.txt") as f:
    text = f.read()
# "Roses are red\nViolets are blue\n"

with open("poem.txt") as f:
    lines = f.readlines()
# ['Roses are red\n', 'Violets are blue\n']</code></pre>
<p><strong>Neither is ideal for large files.</strong> Prefer iterating the file object, which reads one line at a time:</p>
<pre><code>with open("huge.log") as f:
    for line in f:              # memory-safe
        process(line.rstrip())</code></pre>
<p>There's also <code>readline()</code> (singular) — reads and returns one line; useful when you're parsing streaming input with variable line structure.</p>
'''

ANSWERS[40] = r'''
<p>Wrap file operations in <code>try/except</code> and catch specific I/O exceptions.</p>
<pre><code>try:
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print("config.json is missing — using defaults")
    config = DEFAULT_CONFIG
except PermissionError:
    print("No permission to read config.json")
    raise
except UnicodeDecodeError as e:
    print(f"File is not valid UTF-8: {e}")
    config = None
except json.JSONDecodeError as e:
    print(f"Invalid JSON at line {e.lineno}: {e.msg}")
    config = None</code></pre>
<p>Common file-related exceptions:</p>
<ul>
  <li><code>FileNotFoundError</code> — file doesn't exist (subclass of <code>OSError</code>).</li>
  <li><code>PermissionError</code> — insufficient permissions.</li>
  <li><code>IsADirectoryError</code> / <code>NotADirectoryError</code> — wrong kind of path.</li>
  <li><code>OSError</code> — catch-all for I/O failures (disk full, broken pipe, etc.).</li>
  <li><code>UnicodeDecodeError</code> / <code>UnicodeEncodeError</code> — encoding issues.</li>
</ul>
<p><strong>Check vs. try</strong>: the Pythonic style is "ask forgiveness, not permission" (EAFP) — try the operation and handle failure — rather than pre-checking with <code>os.path.exists</code> (LBYL), which has a race condition between the check and the open.</p>
<pre><code># Pythonic
try:
    with open(path) as f: ...
except FileNotFoundError: ...

# Less reliable — another process could delete the file between check and open
if os.path.exists(path):
    with open(path) as f: ...    # FileNotFoundError still possible!</code></pre>
'''

ANSWERS[41] = r'''
<p>The <code>with</code> statement manages a <strong>context</strong> — it guarantees setup and teardown happen as a pair, even when exceptions fire.</p>
<pre><code># Without `with` — tedious and error-prone
f = open("data.txt")
try:
    content = f.read()
finally:
    f.close()

# With `with` — Python handles close()
with open("data.txt") as f:
    content = f.read()
# File is closed here, even if read() raised</code></pre>
<p>Multiple contexts in one statement:</p>
<pre><code>with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read().upper())</code></pre>
<p>Common context managers:</p>
<ul>
  <li><code>open()</code> — files.</li>
  <li><code>threading.Lock()</code>, <code>asyncio.Lock()</code> — locks.</li>
  <li><code>tempfile.TemporaryDirectory()</code> — auto-cleaned temp dirs.</li>
  <li><code>contextlib.suppress(Exception)</code> — ignore specific exceptions.</li>
  <li><code>unittest.mock.patch</code> — test patching.</li>
  <li>DB connections, HTTP sessions, timing contexts.</li>
</ul>
<p>Create your own by implementing <code>__enter__</code> / <code>__exit__</code>, or more easily with the <code>@contextmanager</code> decorator:</p>
<pre><code>from contextlib import contextmanager
import time

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")

with timer("query"):
    run_query()</code></pre>
'''

ANSWERS[42] = r'''
<p>Use the <code>int()</code> built-in. It accepts an optional base for non-decimal input.</p>
<pre><code>int("42")            # 42
int("-17")           # -17
int("  42  ")         # 42 — whitespace is stripped
int("101", 2)         # 5     — binary
int("ff", 16)         # 255   — hex
int("0x1f", 0)        # 31    — base 0 auto-detects prefix

int("3.14")          # ValueError — doesn't parse floats
int(3.14)            # 3 — but int(float) truncates toward zero
int("abc")           # ValueError: invalid literal for int() with base 10</code></pre>
<p>If the input might not be a valid integer, wrap in <code>try/except</code>:</p>
<pre><code>def safe_int(s, default=0):
    try:
        return int(s)
    except (ValueError, TypeError):
        return default

safe_int("42")        # 42
safe_int("abc")       # 0
safe_int(None)        # 0</code></pre>
<p>For float-like strings, parse to float first, then to int:</p>
<pre><code>int(float("3.14"))    # 3</code></pre>
<p>Watch out for locale-specific formats (commas, dots) — <code>int("1,000")</code> raises. Strip those first:</p>
<pre><code>int("1,000".replace(",", ""))    # 1000</code></pre>
'''

ANSWERS[43] = r'''
<p>Use <code>str()</code>, or an f-string, or <code>format()</code>.</p>
<pre><code>n = 42

str(n)              # "42"
f"{n}"              # "42"
"{}".format(n)      # "42"

# With formatting
f"{n:05d}"          # "00042" — pad with zeros to width 5
f"{n:,}"            # "42"  (no effect here; "1,000,000" for larger)
f"{n:x}"            # "2a"  — hex
f"{n:b}"            # "101010" — binary
f"{n:.2f}"          # "42.00" — as float with 2 decimals

# Explicit base conversion
hex(n)              # "0x2a"
oct(n)              # "0o52"
bin(n)              # "0b101010"</code></pre>
<p>Concatenation note:</p>
<pre><code># Can't concatenate int to str directly
print("Age: " + 30)      # TypeError

# Convert or interpolate
print("Age: " + str(30)) # works
print(f"Age: {30}")       # preferred</code></pre>
<p>When you're formatting many values into a message, f-strings are the fastest and most readable choice.</p>
'''

ANSWERS[44] = r'''
<p>Scope is determined by where a name is assigned.</p>
<pre><code>x = 10    # global — module-level

def outer():
    y = 20    # local to outer

    def inner():
        z = 30    # local to inner
        print(x, y, z)    # all readable (LEGB rule)

    inner()
    print(y)      # readable
    # print(z)    # NameError — inner's local is gone

outer()
print(x)          # readable</code></pre>
<p><strong>LEGB scope resolution order:</strong></p>
<ol>
  <li><strong>L</strong>ocal — current function.</li>
  <li><strong>E</strong>nclosing — any enclosing function (for nested functions).</li>
  <li><strong>G</strong>lobal — the module.</li>
  <li><strong>B</strong>uilt-in — names like <code>print</code>, <code>len</code>.</li>
</ol>
<p><strong>Writing to outer scopes</strong> requires explicit keywords — otherwise a bare assignment creates a new local:</p>
<pre><code>counter = 0

def increment():
    global counter        # declare — we're modifying the module-level name
    counter += 1

def make_counter():
    count = 0
    def inner():
        nonlocal count    # declare — we're modifying the enclosing function's name
        count += 1
        return count
    return inner</code></pre>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div>Heavy use of <code>global</code> is a code smell — it creates hidden dependencies. Pass state via arguments, return values, or encapsulate in a class instead.</div>
</div>
'''

ANSWERS[45] = r'''
<p>Add <code>= value</code> to a parameter. The default is used when the caller omits that argument.</p>
<pre><code>def connect(host: str, port: int = 8080, timeout: float = 5.0) -&gt; None:
    print(f"Connecting to {host}:{port} (timeout={timeout}s)")

connect("api.example.com")                    # uses defaults
connect("api.example.com", 443)                # port=443, default timeout
connect("api.example.com", timeout=10.0)       # keyword skips port</code></pre>
<p>Rules:</p>
<ul>
  <li>Parameters with defaults must come <em>after</em> parameters without defaults.</li>
  <li>Defaults are evaluated <strong>once</strong> at function definition time — not each call.</li>
</ul>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div><strong>Mutable default argument gotcha:</strong>
<pre><code>def append_item(item, target=[]):    # target is created ONCE
    target.append(item)
    return target

append_item(1)    # [1]
append_item(2)    # [1, 2] — surprise!</code></pre>
Use <code>None</code> as the sentinel and create the mutable object inside the function:
<pre><code>def append_item(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target</code></pre>
</div>
</div>
<p>For named-only parameters (defaults accessed by keyword only), use <code>*</code>:</p>
<pre><code>def func(a, b, *, verbose=False):
    # verbose must be passed by keyword
    ...</code></pre>
'''

ANSWERS[46] = r'''
<p>Both add items to a list, but they differ in what they treat the argument as.</p>
<table>
  <thead><tr><th></th><th><code>append(x)</code></th><th><code>extend(iterable)</code></th></tr></thead>
  <tbody>
    <tr><td>Adds</td><td>x as a single element</td><td>Each item of iterable</td></tr>
    <tr><td>Length change</td><td>+1</td><td>+len(iterable)</td></tr>
    <tr><td>Typical use</td><td>One new item</td><td>Merge two sequences</td></tr>
  </tbody>
</table>
<pre><code>a = [1, 2, 3]

# append — adds argument as a single element
a.append([4, 5])
# [1, 2, 3, [4, 5]] — nested list!

b = [1, 2, 3]
b.extend([4, 5])
# [1, 2, 3, 4, 5] — flat merge

# extend works with any iterable
b.extend("ab")       # [1, 2, 3, 4, 5, 'a', 'b']
b.extend(range(3))   # [1, 2, 3, 4, 5, 'a', 'b', 0, 1, 2]</code></pre>
<p>Equivalent operators:</p>
<pre><code>a += [4, 5]      # equivalent to a.extend([4, 5])
a = a + [4, 5]   # creates a NEW list (slower for big lists)</code></pre>
<p>For building lists in a loop, <code>.append()</code> is standard and O(1) amortized. For concatenating many lists at once, <code>.extend()</code> is clearer than repeated <code>.append()</code> in a loop.</p>
'''

ANSWERS[47] = r'''
<p>Four idiomatic ways depending on what you know.</p>
<pre><code>items = ["a", "b", "c", "d", "e"]

# 1. Remove by index
del items[2]             # ['a', 'b', 'd', 'e']
popped = items.pop(0)    # popped='a'; items=['b', 'd', 'e']
items.pop()              # removes and returns the LAST item

# 2. Remove by value (first occurrence)
items = ["a", "b", "c", "b"]
items.remove("b")        # ['a', 'c', 'b'] — first 'b' gone; ValueError if missing

# 3. Clear entirely
items.clear()            # []

# 4. Remove by filter — build a new list
items = [1, 2, 3, 4, 5]
items = [x for x in items if x % 2 == 0]
# [2, 4]</code></pre>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div><strong>Don't mutate a list while iterating over it</strong>:
<pre><code>for x in items:
    if x &lt; 0:
        items.remove(x)    # skips items — iteration state gets confused</code></pre>
Build a new list with a comprehension, or iterate over a copy:
<pre><code>items = [x for x in items if x &gt;= 0]
# or: for x in items[:]: ...</code></pre>
</div>
</div>
<p>Time complexity: <code>pop()</code> (end) is O(1); <code>pop(i)</code>, <code>remove(x)</code>, <code>del items[i]</code> at arbitrary positions are O(n) because subsequent items shift left.</p>
'''

ANSWERS[48] = r'''
<p><code>pass</code> is a do-nothing statement used as a placeholder where syntax requires a statement but you have nothing to execute.</p>
<pre><code># Empty function body — you'll fill it in later
def parse_input(data):
    pass    # TODO: implement

# Empty class
class AuthError(Exception):
    pass

# Empty loop body — typically when the side effect happens in the condition
while check_connection():
    pass

# Conditional with deliberately empty branch
if debug_mode:
    log_details()
else:
    pass    # no-op — though here you'd usually just omit the else</code></pre>
<p>Alternatives in specific contexts:</p>
<ul>
  <li><strong>Ellipsis</strong> (<code>...</code>) — conventional for type-stub files and abstract methods:
    <pre><code>from typing import Protocol

class Reader(Protocol):
    def read(self) -&gt; str: ...    # method signature only</code></pre>
  </li>
  <li><strong>NotImplementedError</strong> — marks an abstract method you expect subclasses to override:
    <pre><code>def process(self):
    raise NotImplementedError</code></pre>
  </li>
</ul>
<p>Use <code>pass</code> when you need a syntactically complete block with no behavior. It's not an error or no-op marker — it's just &ldquo;nothing to see here&rdquo;.</p>
'''

ANSWERS[49] = r'''
<p><code>zip()</code> pairs up items from multiple iterables, producing tuples. Iteration stops when the shortest iterable is exhausted.</p>
<pre><code>names = ["Ana", "Bo", "Cy"]
ages = [30, 25, 35]

list(zip(names, ages))
# [('Ana', 30), ('Bo', 25), ('Cy', 35)]

# Typical use — parallel iteration
for name, age in zip(names, ages):
    print(f"{name} is {age}")

# Build a dict from two lists
dict(zip(names, ages))
# {'Ana': 30, 'Bo': 25, 'Cy': 35}</code></pre>
<p>With three or more iterables:</p>
<pre><code>cities = ["Paris", "Berlin", "Tokyo"]
for name, age, city in zip(names, ages, cities):
    print(f"{name}, {age}, lives in {city}")</code></pre>
<p>Iteration stops at the shortest. If that's a problem, use <code>zip_longest</code> which fills with a sentinel:</p>
<pre><code>from itertools import zip_longest
list(zip_longest([1, 2, 3], ["a", "b"], fillvalue="?"))
# [(1, 'a'), (2, 'b'), (3, '?')]

# Python 3.10+: strict=True raises if lengths differ
list(zip([1, 2], [3, 4, 5], strict=True))    # ValueError</code></pre>
<p><strong>Unzipping</strong> uses the <code>*</code> operator:</p>
<pre><code>pairs = [("Ana", 30), ("Bo", 25)]
names, ages = zip(*pairs)    # ('Ana', 'Bo'), (30, 25)</code></pre>
'''

ANSWERS[50] = r'''
<p>A <strong>generator</strong> is a function that produces a sequence of values lazily — one at a time, on demand — rather than building the whole sequence in memory.</p>
<pre><code>def count_up_to(n):
    i = 0
    while i &lt; n:
        yield i           # pauses here; resumes on next next() call
        i += 1

# Generators are iterators
gen = count_up_to(3)
next(gen)    # 0
next(gen)    # 1
next(gen)    # 2
next(gen)    # StopIteration

# Normally you iterate — for loop handles StopIteration
for n in count_up_to(3):
    print(n)    # 0, 1, 2</code></pre>
<p>Benefits:</p>
<ul>
  <li><strong>Memory-efficient</strong> — <code>count_up_to(10 ** 9)</code> uses constant memory; a list would use gigabytes.</li>
  <li><strong>Lazy</strong> — values are computed only when requested.</li>
  <li><strong>Infinite sequences</strong> are possible:
    <pre><code>def naturals():
    n = 0
    while True:
        yield n
        n += 1</code></pre>
  </li>
</ul>
<p><strong>Generator expression</strong> — like a list comprehension but with parentheses and lazy:</p>
<pre><code># Eager — builds the whole list
total = sum([n * n for n in range(1_000_000)])

# Lazy — one item at a time
total = sum(n * n for n in range(1_000_000))</code></pre>
<p>Use generators for: streaming large files line-by-line, processing pipelines, anywhere you don't need random access or the full list at once.</p>
'''

ANSWERS[51] = r'''
<p>Two ways: a <strong>generator function</strong> (using <code>yield</code>) or a <strong>generator expression</strong> (like a comprehension with parentheses).</p>
<pre><code># 1. Generator function
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip()

# Usage — one line in memory at a time
for line in read_large_file("huge.log"):
    if "ERROR" in line:
        print(line)

# 2. Generator expression
squares = (n * n for n in range(10))    # parens, not brackets
print(next(squares))    # 0
print(next(squares))    # 1</code></pre>
<p>Generators compose cleanly into <strong>pipelines</strong>:</p>
<pre><code>def lines(path):
    with open(path) as f:
        yield from f                  # yield each line

def non_blank(lines):
    for line in lines:
        if line.strip():
            yield line

def parse(lines):
    for line in lines:
        yield json.loads(line)


pipeline = parse(non_blank(lines("events.ndjson")))
for event in pipeline:
    handle(event)
# At any moment, only one line is in flight — perfect for streaming ETL</code></pre>
<p><code>yield from</code> is shorthand for &ldquo;yield everything from this iterable&rdquo;, useful when chaining generators. Generators can also receive values via <code>.send()</code>, but that's rare in practice — the common use is one-way production.</p>
'''

ANSWERS[52] = r'''
<p>Both exit a function-like construct, but differently and in different contexts.</p>
<table>
  <thead><tr><th></th><th><code>return</code></th><th><code>yield</code></th></tr></thead>
  <tbody>
    <tr><td>Found in</td><td>Regular functions</td><td>Generator functions</td></tr>
    <tr><td>Function ends?</td><td>Yes — done after return</td><td>No — paused, resumes on next call</td></tr>
    <tr><td>Caller receives</td><td>One value</td><td>One value per yield, as an iterator</td></tr>
    <tr><td>State</td><td>Local variables are gone</td><td>Preserved between yields</td></tr>
  </tbody>
</table>
<pre><code># Regular function — one-shot
def get_squares(n):
    return [i * i for i in range(n)]

get_squares(5)    # [0, 1, 4, 9, 16]  — whole list, immediately

# Generator — streaming
def gen_squares(n):
    for i in range(n):
        yield i * i

g = gen_squares(5)
next(g)    # 0
next(g)    # 1
# ... remembers `i` between calls

list(gen_squares(5))    # [0, 1, 4, 9, 16] — materialize if needed</code></pre>
<p>Key behaviors:</p>
<ul>
  <li>A function with even a single <code>yield</code> becomes a generator function — calling it doesn't execute the body; it returns a generator object.</li>
  <li><code>return</code> inside a generator still works — it ends iteration and can attach a value to the <code>StopIteration</code> exception (rarely used directly; useful with <code>yield from</code>).</li>
</ul>
'''

ANSWERS[53] = r'''
<p>Several idiomatic ways depending on what you want.</p>
<pre><code>s = "Hello, World!"

# 1. Character by character — list() over a string
list(s)
# ['H', 'e', 'l', 'l', 'o', ',', ' ', 'W', 'o', 'r', 'l', 'd', '!']

# 2. Split on whitespace
"one two three".split()
# ['one', 'two', 'three']

# 3. Split on a specific delimiter
"a,b,c,d".split(",")
# ['a', 'b', 'c', 'd']

"apple:banana:cherry".split(":", maxsplit=1)
# ['apple', 'banana:cherry']

# 4. Split by lines
"""line 1
line 2
line 3""".splitlines()
# ['line 1', 'line 2', 'line 3']

# 5. Words with punctuation handling — regex
import re
re.findall(r"\w+", "Hello, World! It's 2024.")
# ['Hello', 'World', 'It', 's', '2024']</code></pre>
<p>For iterating characters without materializing a list, just loop:</p>
<pre><code>for char in s:
    ...    # strings are iterable</code></pre>
<p>For the reverse (list → string), use <code>"".join(items)</code> — not <code>"" + item + item</code>, which is O(n²). <code>join</code> requires string items; convert non-strings first:</p>
<pre><code>",".join(str(n) for n in [1, 2, 3])    # "1,2,3"</code></pre>
'''

ANSWERS[54] = r'''
<p><strong>Regular expressions</strong> (regex) are patterns for matching text. Python's <code>re</code> module provides the API.</p>
<pre><code>import re

# Match — from the start
re.match(r"\d+", "123abc")           # &lt;Match '123'&gt;
re.match(r"\d+", "abc123")           # None — must match at start

# Search — anywhere in the string
re.search(r"\d+", "abc123")          # &lt;Match '123'&gt;

# Find all non-overlapping matches
re.findall(r"\d+", "a1 b22 c333")    # ['1', '22', '333']

# Iterator over matches (useful for big strings)
for m in re.finditer(r"\d+", text):
    print(m.group(), m.start())

# Substitute
re.sub(r"\d+", "N", "a1 b22 c333")   # 'aN bN cN'

# Split on a pattern
re.split(r"\s+", "one   two three")   # ['one', 'two', 'three']</code></pre>
<p>Common pattern syntax:</p>
<ul>
  <li><code>.</code> any char &nbsp;|&nbsp; <code>*</code> 0+ &nbsp;|&nbsp; <code>+</code> 1+ &nbsp;|&nbsp; <code>?</code> 0 or 1 &nbsp;|&nbsp; <code>{n,m}</code> between n and m</li>
  <li><code>\d</code> digit &nbsp;|&nbsp; <code>\w</code> word char &nbsp;|&nbsp; <code>\s</code> whitespace &nbsp;|&nbsp; <code>[abc]</code> char class</li>
  <li><code>^</code> start &nbsp;|&nbsp; <code>$</code> end &nbsp;|&nbsp; <code>\b</code> word boundary</li>
  <li><code>( )</code> capture group &nbsp;|&nbsp; <code>(?: )</code> non-capturing &nbsp;|&nbsp; <code>(?P&lt;name&gt; )</code> named</li>
</ul>
<div class="callout callout-tip">
  <div class="callout-icon">i</div>
  <div>Always use <strong>raw strings</strong> (<code>r"..."</code>) for regex patterns — otherwise <code>\b</code>, <code>\d</code>, and friends get mangled by string-literal escaping.</div>
</div>
'''

ANSWERS[55] = r'''
<p>Key API functions for pattern matching:</p>
<pre><code>import re

text = "Contact: alice@example.com or bob@company.co.uk"

# 1. Match at start of string
m = re.match(r"Contact", text)
if m:
    print(m.group())    # "Contact"

# 2. Search anywhere
m = re.search(r"\w+@\w+\.\w+", text)
if m:
    print(m.group(), m.span())    # 'alice@example.com' (9, 26)

# 3. Capture groups
pattern = r"(\w+)@(\w+)\.(\w+)"
m = re.search(pattern, text)
m.group(0)    # full match: 'alice@example.com'
m.group(1)    # 'alice'       — first group
m.group(2)    # 'example'
m.group(3)    # 'com'
m.groups()    # ('alice', 'example', 'com')

# 4. Named groups
m = re.search(r"(?P&lt;user&gt;\w+)@(?P&lt;domain&gt;[\w.]+)", text)
m.group("user"), m.group("domain")    # ('alice', 'example.com')

# 5. Find all matches
re.findall(r"\w+@[\w.]+", text)
# ['alice@example.com', 'bob@company.co.uk']

# 6. Iterate — access Match objects (spans, groups)
for m in re.finditer(r"(\w+)@([\w.]+)", text):
    print(f"{m.group(1)} at {m.group(2)}")

# 7. Compile for reuse — faster in loops
email_re = re.compile(r"\w+@[\w.]+", re.IGNORECASE)
for line in huge_text.splitlines():
    if email_re.search(line):
        ...</code></pre>
<p>Flags: <code>re.IGNORECASE</code>, <code>re.MULTILINE</code> (<code>^</code>/<code>$</code> match per line), <code>re.DOTALL</code> (<code>.</code> matches newlines), <code>re.VERBOSE</code> (lets you format the pattern with whitespace + comments).</p>
'''

ANSWERS[56] = r'''
<p>Slicing extracts a substring using <code>s[start:stop:step]</code> — half-open range, zero-indexed.</p>
<pre><code>s = "Hello, World!"

s[0]          # 'H'
s[-1]         # '!'   — negative index counts from the end
s[7]          # 'W'

s[0:5]        # 'Hello'        — indices 0, 1, 2, 3, 4
s[7:12]       # 'World'
s[:5]         # 'Hello'        — start default = 0
s[7:]         # 'World!'       — stop default = len(s)
s[:]          # full copy

s[-6:-1]      # 'World'        — negatives work too
s[::2]        # 'Hlo ol!'      — every 2nd character
s[::-1]       # '!dlroW ,olleH' — reversed</code></pre>
<p>Key behaviors:</p>
<ul>
  <li><code>stop</code> is <strong>exclusive</strong> — <code>s[0:3]</code> gives 3 characters, not 4.</li>
  <li>Out-of-range indices are clamped gracefully — no IndexError:
    <pre><code>"abc"[0:100]    # 'abc' — no error</code></pre>
  </li>
  <li>Strings are immutable, so slicing always returns a new string.</li>
  <li>The same syntax works on lists and tuples (and any sequence).</li>
</ul>
<p>Common recipes:</p>
<pre><code>last_three = s[-3:]               # last 3 chars
without_last = s[:-1]              # all but last
reversed_s = s[::-1]               # reverse
every_other = s[::2]               # every other char</code></pre>
'''

ANSWERS[57] = r'''
<p>They're complementary — <code>split</code> breaks a string into a list; <code>join</code> combines a list into a string.</p>
<pre><code>s = "a,b,c,d"

# split — string → list
parts = s.split(",")
# ['a', 'b', 'c', 'd']

# join — list → string (called on the delimiter!)
result = ",".join(parts)
# 'a,b,c,d'</code></pre>
<p>Details:</p>
<pre><code># split without an argument splits on any whitespace, collapsing runs
"  one    two   three  ".split()
# ['one', 'two', 'three']

# With a delimiter, consecutive delimiters create empty strings
"a,,b".split(",")
# ['a', '', 'b']

# maxsplit limits the splits
"a:b:c:d".split(":", maxsplit=1)
# ['a', 'b:c:d']

# rsplit splits from the right
"a/b/c/file.txt".rsplit("/", maxsplit=1)
# ['a/b/c', 'file.txt']

# join requires all items to be strings
",".join(["1", "2", "3"])         # '1,2,3'
",".join([1, 2, 3])               # TypeError

# Convert first
",".join(str(n) for n in [1, 2, 3])    # '1,2,3'</code></pre>
<div class="callout callout-tip">
  <div class="callout-icon">i</div>
  <div>Use <code>"".join(...)</code> to concatenate many strings — it's O(n). Building up with <code>+=</code> in a loop is O(n²) and noticeably slower for large inputs.</div>
</div>
'''

ANSWERS[58] = r'''
<p>Sets are unordered collections of unique, hashable items. (Same topic as Q12 — quick recap with a different angle.)</p>
<pre><code># Create
empty = set()                           # NOT {} — that's a dict
tags = {"python", "tutorial"}
unique_words = set(text.split())         # dedupe

# Membership — O(1)
"python" in tags    # True

# Add / remove
tags.add("beginner")
tags.remove("beginner")      # KeyError if absent
tags.discard("beginner")      # silent if absent
tags.pop()                    # removes an arbitrary element

# Length, iteration
len(tags)
for tag in tags:
    print(tag)

# Set algebra
a, b = {1, 2, 3}, {3, 4, 5}
a | b        # union         {1, 2, 3, 4, 5}
a &amp; b        # intersection  {3}
a - b        # difference    {1, 2}
a ^ b        # symmetric     {1, 2, 4, 5}

a &lt;= b       # subset test
a &gt;= b       # superset test</code></pre>
<p>Typical uses:</p>
<ul>
  <li><strong>Deduplication</strong> — <code>unique = list(set(items))</code> (drops order).</li>
  <li><strong>Fast membership</strong> — <code>"x" in s</code> is O(1) vs O(n) on a list.</li>
  <li><strong>Set math</strong> — intersect permissions, find common tags, compute diffs.</li>
  <li><strong>Cache of seen items</strong> — skip duplicates in a stream.</li>
</ul>
<p>For an immutable set (usable as a dict key), use <code>frozenset()</code>.</p>
'''

ANSWERS[59] = r'''
<p>Several approaches — the right one depends on whether order matters.</p>
<pre><code>items = [3, 1, 4, 1, 5, 9, 2, 6, 5]

# 1. set — fastest, loses order
unique = list(set(items))
# [1, 2, 3, 4, 5, 6, 9]  (order not guaranteed)

# 2. dict.fromkeys — preserves first-seen order (Python 3.7+)
unique = list(dict.fromkeys(items))
# [3, 1, 4, 5, 9, 2, 6]

# 3. Set + order manually (for older Python or more control)
seen = set()
unique = []
for x in items:
    if x not in seen:
        seen.add(x)
        unique.append(x)
# [3, 1, 4, 5, 9, 2, 6]

# 4. For lists of dicts (not hashable), use a key-based approach
users = [
    {"id": 1, "name": "Ana"},
    {"id": 2, "name": "Bo"},
    {"id": 1, "name": "Ana"},
]
seen_ids = set()
unique_users = [u for u in users if not (u["id"] in seen_ids or seen_ids.add(u["id"]))]

# Or using a dict keyed by id:
unique_users = list({u["id"]: u for u in users}.values())</code></pre>
<p><strong>Which to pick</strong>: for hashable items where order doesn't matter, <code>set</code> is simplest. To preserve order, <code>dict.fromkeys</code> is a one-liner. For custom dedup keys (like &ldquo;same email&rdquo;), write an explicit loop or use a dict keyed by the dedup attribute.</p>
'''

ANSWERS[60] = r'''
<p><code>None</code> is Python's singleton &ldquo;no value&rdquo; — the only instance of <code>NoneType</code>. It's used as a default return, a placeholder, and a sentinel for &ldquo;not set&rdquo;.</p>
<pre><code># Default return when a function has no return statement
def log(msg):
    print(msg)

result = log("hi")
result is None    # True

# Default argument to signal &quot;user didn't pass one&quot;
def connect(host, port=None):
    if port is None:
        port = 443 if host.startswith("https://") else 80
    ...

# Sentinel for &quot;no value yet&quot; (common in caches, lazy init)
_instance = None
def get_instance():
    global _instance
    if _instance is None:
        _instance = expensive_init()
    return _instance

# Optional type hints use None
from typing import Optional
def find_user(email: str) -&gt; Optional[User]:    # User or None
    ...
# Equivalent (Python 3.10+): -&gt; User | None</code></pre>
<p>Rules:</p>
<ul>
  <li>Always compare with <code>is</code>: <code>if x is None</code>, never <code>if x == None</code>. It's more explicit, faster, and unambiguous even if <code>x</code> overrides <code>__eq__</code>.</li>
  <li><code>None</code> is falsy in boolean contexts — but so are <code>0</code>, <code>""</code>, <code>[]</code>. Don't use <code>if not x</code> when you specifically mean &ldquo;None&rdquo;.</li>
  <li>JSON's <code>null</code> maps to <code>None</code> in Python and vice versa.</li>
</ul>
'''

ANSWERS[61] = r'''
<p><code>enumerate()</code> wraps any iterable and yields <code>(index, value)</code> pairs. It replaces the ugly <code>range(len(...))</code> pattern.</p>
<pre><code>fruits = ["apple", "banana", "cherry"]

# Without enumerate — clunky
for i in range(len(fruits)):
    print(i, fruits[i])

# With enumerate — clean
for i, fruit in enumerate(fruits):
    print(i, fruit)
# 0 apple
# 1 banana
# 2 cherry

# Start counting from a different number
for lineno, line in enumerate(open("file.txt"), start=1):
    print(f"{lineno}: {line.rstrip()}")</code></pre>
<p>Works with any iterable: lists, tuples, strings, generators, file objects. The second argument (<code>start</code>) lets you count from 1 for human-friendly output like line numbers.</p>
'''

ANSWERS[62] = r'''
<p><code>assert</code> is a debugging aid. If the condition is false, it raises <code>AssertionError</code>; if true, execution continues.</p>
<pre><code>def divide(a, b):
    assert b != 0, "Divisor must not be zero"
    return a / b

divide(10, 2)   # 5.0
divide(10, 0)   # AssertionError: Divisor must not be zero</code></pre>
<p>Use for:</p>
<ul>
  <li>Internal invariants — &ldquo;this should never happen but let me know if it does.&rdquo;</li>
  <li>Quick sanity checks during development.</li>
  <li>Preconditions in tests.</li>
</ul>
<div class="callout callout-warning">
  <div class="callout-icon">!</div>
  <div><strong>Don't use <code>assert</code> for runtime input validation.</strong> Python's <code>-O</code> optimization flag strips all asserts. Use proper <code>if ... raise ValueError</code> for checks that must always run.</div>
</div>
'''

ANSWERS[63] = r'''
<p>A <strong>shallow copy</strong> creates a new list object but keeps the same references for nested elements. Three equivalent ways:</p>
<pre><code>original = [1, 2, [3, 4]]

copy1 = original.copy()       # method (Python 3.3+)
copy2 = original[:]           # slice
copy3 = list(original)        # constructor

# All three produce independent top-level lists
copy1.append(99)
print(original)  # [1, 2, [3, 4]] — unchanged

# But nested objects are shared
copy1[2].append(5)
print(original)  # [1, 2, [3, 4, 5]] — mutated!</code></pre>
<p>Shallow copies are fine when:</p>
<ul>
  <li>The list contains only immutable items (numbers, strings, tuples).</li>
  <li>You only modify the top-level list (append, insert, remove).</li>
</ul>
<p>For anything nested and mutable, use <code>copy.deepcopy()</code> — see the next question.</p>
'''

ANSWERS[64] = r'''
<p><code>copy.deepcopy()</code> recursively copies every nested object. The result shares nothing with the original.</p>
<pre><code>import copy

original = [1, 2, [3, 4]]
deep = copy.deepcopy(original)

deep[2].append(99)
print(original)  # [1, 2, [3, 4]] — truly independent
print(deep)      # [1, 2, [3, 4, 99]]</code></pre>
<p>Works on arbitrary nested structures: dicts of lists of objects, graph-like data with cycles (it tracks already-copied objects), custom classes.</p>
<p>Trade-offs:</p>
<ul>
  <li><strong>Slow</strong> — recursive traversal + object creation for everything.</li>
  <li><strong>Memory-heavy</strong> — duplicates the entire structure.</li>
  <li><strong>Custom classes</strong> — can customize with <code>__deepcopy__(self, memo)</code> if default behavior isn't right.</li>
</ul>
<p>Don't deep-copy &ldquo;just in case&rdquo;; use it only when you genuinely need to mutate a nested copy without affecting the original.</p>
'''

ANSWERS[65] = r'''
<p><code>__init__</code> is Python's constructor — it runs automatically when you instantiate a class. Its job is to set up the object's initial state.</p>
<pre><code>class Point:
    def __init__(self, x, y):
        self.x = x      # instance attributes
        self.y = y

    def distance_from_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

p = Point(3, 4)           # __init__(3, 4) runs
p.distance_from_origin()  # 5.0</code></pre>
<p>Key points:</p>
<ul>
  <li><code>self</code> refers to the instance being constructed (Python passes it implicitly).</li>
  <li>Don't confuse with <code>__new__</code>, which actually creates the object. <code>__init__</code> just initializes it.</li>
  <li>Not strictly required — if absent, Python uses the parent's (or a no-op).</li>
  <li>To call the parent's <code>__init__</code> in a subclass, use <code>super().__init__(...)</code>.</li>
</ul>
<p><code>__init__</code> should return <code>None</code> (implicitly). Returning anything else raises <code>TypeError</code>.</p>
'''

ANSWERS[66] = r'''
<p>A <strong>static method</strong> doesn't receive <code>self</code> or <code>cls</code> — it's just a regular function that lives inside a class for namespacing. Use the <code>@staticmethod</code> decorator.</p>
<pre><code>class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def is_even(n):
        return n % 2 == 0

# Call without instantiating
MathUtils.add(2, 3)       # 5
MathUtils.is_even(4)      # True

# Works on instances too (but no instance state accessible)
m = MathUtils()
m.add(10, 20)             # 30</code></pre>
<p>Use static methods when:</p>
<ul>
  <li>A utility function conceptually belongs with the class.</li>
  <li>It doesn't need instance state (<code>self</code>) or class state (<code>cls</code>).</li>
</ul>
<p>If the method accesses neither, <code>@staticmethod</code> makes that explicit. If you find yourself writing many static methods, consider whether a module-level function would be clearer.</p>
'''

ANSWERS[67] = r'''
<p>A <strong>class method</strong> receives the class itself as the first argument (<code>cls</code>) instead of an instance. Decorated with <code>@classmethod</code>.</p>
<pre><code>class Person:
    population = 0

    def __init__(self, name):
        self.name = name
        Person.population += 1

    @classmethod
    def get_population(cls):
        return cls.population

    @classmethod
    def from_birth_year(cls, name, year):
        # Alternative constructor
        from datetime import date
        age = date.today().year - year
        return cls(name)   # cls refers to Person (or a subclass)

p = Person.from_birth_year("Ana", 1990)
Person.get_population()   # 1</code></pre>
<p>Common uses:</p>
<ul>
  <li><strong>Alternative constructors</strong> — <code>dict.fromkeys()</code>, <code>datetime.fromisoformat()</code> are real-world examples.</li>
  <li><strong>Access to class-level state</strong> — counters, registries, configuration.</li>
  <li><strong>Inheritance-aware factories</strong> — <code>cls()</code> creates an instance of the right subclass.</li>
</ul>
<p>Differences: <code>@classmethod</code> gets <code>cls</code>; <code>@staticmethod</code> gets nothing; regular methods get <code>self</code>.</p>
'''

ANSWERS[68] = r'''
<p>Python <strong>does not support method overloading</strong> in the traditional sense (multiple methods with the same name but different signatures). The last-defined method wins — the earlier one is overwritten.</p>
<pre><code>class Foo:
    def greet(self):
        return "hi"
    def greet(self, name):     # overwrites the first!
        return f"hi {name}"

Foo().greet()           # TypeError: missing argument "name"</code></pre>
<p>Approaches to simulate overloading:</p>
<pre><code># 1. Default arguments
class Greeter:
    def greet(self, name=None):
        return f"hi {name}" if name else "hi"

# 2. Variable arguments
class Calculator:
    def add(self, *args):
        return sum(args)
Calculator().add(1, 2, 3)    # 6

# 3. functools.singledispatch — dispatch by type
from functools import singledispatchmethod
class Processor:
    @singledispatchmethod
    def process(self, arg):
        raise NotImplementedError
    @process.register
    def _(self, arg: int):   return f"int {arg}"
    @process.register
    def _(self, arg: str):   return f"str {arg}"</code></pre>
<p>In practice, default arguments and <code>*args</code>/<code>**kwargs</code> cover most needs cleanly.</p>
'''

ANSWERS[69] = r'''
<p><code>super()</code> returns a proxy object for the parent class, letting subclasses call parent methods — most commonly in <code>__init__</code> to extend initialization.</p>
<pre><code>class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)      # run Animal's __init__
        self.breed = breed

    def speak(self):
        base = super().speak()       # extend parent method
        return f"{base} (a bark)"

d = Dog("Rex", "Lab")
d.speak()    # "Rex makes a sound (a bark)"</code></pre>
<p>Key points:</p>
<ul>
  <li>No need to pass <code>self</code> — <code>super()</code> handles it.</li>
  <li>Modern <code>super()</code> (Python 3) takes no arguments inside a method. Older style: <code>super(Dog, self).__init__(name)</code>.</li>
  <li>Works with multiple inheritance via the MRO (Method Resolution Order) — calling <code>super()</code> in a diamond hierarchy visits each class once.</li>
  <li>Best practice: always call <code>super().__init__()</code> when subclassing unless you deliberately want to skip parent setup.</li>
</ul>
'''

ANSWERS[70] = r'''
<p><code>__name__</code> is set to <code>"__main__"</code> when a Python file is run directly, or to the module's name when imported.</p>
<pre><code># my_script.py
def main():
    print("Running as main")

if __name__ == "__main__":
    main()

# Direct run:
# $ python my_script.py
# → __name__ == "__main__" → main() runs

# Imported:
# &gt;&gt;&gt; import my_script
# → __name__ == "my_script" → main() does NOT run</code></pre>
<p>This idiom lets a file serve two purposes:</p>
<ul>
  <li>As an <strong>importable library</strong> — other code can <code>from my_script import foo</code> without triggering the main routine.</li>
  <li>As an <strong>executable script</strong> — running it directly kicks off the main logic.</li>
</ul>
<p>Essential for any file that defines reusable functions but also wants to be runnable. Test files and CLI tools use this pattern universally.</p>
'''

ANSWERS[71] = r'''
<p>Use the <code>in</code> operator — it's the idiomatic, clear, and fast way.</p>
<pre><code>d = {"name": "Ana", "age": 30}

"name" in d           # True
"email" in d          # False
"name" not in d       # False

# Use with a conditional
if "email" in d:
    send_to(d["email"])</code></pre>
<p>Other approaches — less common:</p>
<pre><code># .get() with a default — returns None if missing
d.get("email")          # None
d.get("email", "N/A")   # "N/A"

# .keys() — works but pointless; "in" on dicts already checks keys
"name" in d.keys()      # redundant

# try/except — use when you need the value AND absence is exceptional
try:
    email = d["email"]
except KeyError:
    email = None</code></pre>
<p><strong>Avoid <code>d.has_key("name")</code></strong> — that was Python 2; removed in Python 3.</p>
'''

ANSWERS[72] = r'''
<p>Python 3.9+ introduced the <code>|</code> operator for dict merging — the cleanest approach.</p>
<pre><code>a = {"x": 1, "y": 2}
b = {"y": 20, "z": 30}

# Python 3.9+ — merge operator
merged = a | b           # {"x": 1, "y": 20, "z": 30}  (b wins on conflicts)

# In-place merge
a |= b                   # a is now merged

# Unpacking — works in older Pythons (3.5+)
merged = {**a, **b}      # same result

# .update() — mutates a in place
a.update(b)

# Multiple dicts
merged = {**a, **b, **c}
merged = a | b | c</code></pre>
<p>Conflict resolution: the <strong>right-hand dict wins</strong>. <code>a | b</code> gives b's values for overlapping keys.</p>
<p>For deep merging (nested dicts), write a small helper or use a library — none of the built-in methods merge recursively.</p>
'''

ANSWERS[73] = r'''
<table>
  <thead><tr><th></th><th><code>pop(key)</code></th><th><code>popitem()</code></th></tr></thead>
  <tbody>
    <tr><td>Removes</td><td>Specific key</td><td>Arbitrary (last-inserted) key</td></tr>
    <tr><td>Returns</td><td>The value</td><td>Tuple <code>(key, value)</code></td></tr>
    <tr><td>Missing key</td><td>Raises <code>KeyError</code> (or default if given)</td><td>Raises <code>KeyError</code> on empty dict</td></tr>
    <tr><td>Argument</td><td>Required (<code>key</code>, optional <code>default</code>)</td><td>None</td></tr>
  </tbody>
</table>
<pre><code>d = {"a": 1, "b": 2, "c": 3}

d.pop("a")              # 1, d is now {"b": 2, "c": 3}
d.pop("x", "missing")   # "missing" — default prevents KeyError

# Python 3.7+ guarantees insertion order; popitem removes last inserted
d.popitem()             # ("c", 3), d is now {"b": 2}

# Useful for processing a dict like a stack
while d:
    key, value = d.popitem()
    process(key, value)</code></pre>
<p>Before Python 3.7, <code>popitem()</code> removed an arbitrary key (not guaranteed last). Modern code can rely on LIFO order.</p>
'''

ANSWERS[74] = r'''
<p>Use <code>.items()</code> for key-value pairs, <code>.keys()</code> for just keys, <code>.values()</code> for just values.</p>
<pre><code>d = {"name": "Ana", "age": 30, "city": "NYC"}

# Both key and value
for k, v in d.items():
    print(f"{k}: {v}")
# name: Ana
# age: 30
# city: NYC

# Just keys — equivalent to iterating the dict directly
for k in d:
    print(k)
for k in d.keys():        # explicit, same result
    print(k)

# Just values
for v in d.values():
    print(v)</code></pre>
<p>These return <strong>views</strong>, not lists — they reflect live changes to the dict and don't allocate a new collection.</p>
<pre><code>keys = d.keys()
d["email"] = "a@b.c"
print(keys)  # dict_keys(['name', 'age', 'city', 'email'])  — updated!</code></pre>
<p>Don't mutate a dict while iterating its view — you'll get a <code>RuntimeError</code>. Either iterate a snapshot (<code>list(d.items())</code>) or collect changes and apply after the loop.</p>
'''

ANSWERS[75] = r'''
<p><code>any()</code> returns <code>True</code> if <strong>at least one</strong> element is truthy. <code>all()</code> returns <code>True</code> if <strong>every</strong> element is truthy (or the iterable is empty).</p>
<pre><code>numbers = [1, 2, 3, 4, 5]

any(n &gt; 3 for n in numbers)   # True — 4 and 5 are &gt; 3
all(n &gt; 0 for n in numbers)   # True — all are positive
all(n &gt; 3 for n in numbers)   # False — 1, 2, 3 aren't
any(n &gt; 100 for n in numbers) # False

# Empty iterable
any([])   # False
all([])   # True   (&quot;vacuous truth&quot;)</code></pre>
<p>Both <strong>short-circuit</strong> — they stop as soon as the answer is determined. This makes them fast and lets you use them for existence checks without scanning the whole iterable.</p>
<pre><code># Instead of:
found = False
for line in huge_file:
    if "ERROR" in line:
        found = True
        break

# Just:
found = any("ERROR" in line for line in huge_file)   # same, cleaner</code></pre>
<p>The generator-expression form is essential for large or infinite iterables — it avoids building an intermediate list.</p>
'''

ANSWERS[76] = r'''
<p>Use <code>sorted()</code> with <code>.items()</code>, then reconstruct a dict (Python 3.7+ preserves insertion order).</p>
<pre><code>d = {"banana": 3, "apple": 1, "cherry": 2}

# Ascending by key
sorted_d = dict(sorted(d.items()))
# {"apple": 1, "banana": 3, "cherry": 2}

# Descending
sorted_d = dict(sorted(d.items(), reverse=True))
# {"cherry": 2, "banana": 3, "apple": 1}

# Custom key function — sort by length of key
sorted_d = dict(sorted(d.items(), key=lambda item: len(item[0])))
# {"apple": 1, "banana": 3, "cherry": 2}  (5, 6, 6)</code></pre>
<p>Note: <code>sorted()</code> returns a new list; you can't sort a dict in place (nor would that be meaningful pre-3.7 when order wasn't preserved). The idiom is <strong>create a new sorted dict</strong>.</p>
<p>If you only need the sorted keys, skip the dict reconstruction: <code>sorted(d)</code> returns the keys in sorted order.</p>
'''

ANSWERS[77] = r'''
<p>Same pattern as sorting by key, but pass a <code>key</code> function that picks the value.</p>
<pre><code>d = {"banana": 3, "apple": 1, "cherry": 2}

# By value, ascending
sorted_d = dict(sorted(d.items(), key=lambda item: item[1]))
# {"apple": 1, "cherry": 2, "banana": 3}

# By value, descending
sorted_d = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))
# {"banana": 3, "cherry": 2, "apple": 1}

# Using operator.itemgetter — slightly faster
from operator import itemgetter
sorted_d = dict(sorted(d.items(), key=itemgetter(1)))</code></pre>
<p>For mixed-type values where you need a tiebreaker (e.g., sort by value, then alphabetically by key):</p>
<pre><code>sorted_d = dict(sorted(d.items(), key=lambda item: (item[1], item[0])))</code></pre>
<p>If your values are unhashable or unsortable among themselves, you'll get a <code>TypeError</code>. Convert them first or supply a key that produces a sortable representation.</p>
'''

ANSWERS[78] = r'''
<p>The idiomatic Python idiom is slicing with a step of <code>-1</code>.</p>
<pre><code>s = "hello"

# Slice — clearest, most common
reversed_s = s[::-1]          # "olleh"

# reversed() returns an iterator — join to get a string
reversed_s = "".join(reversed(s))   # "olleh"

# Manual loop — rarely needed
chars = list(s)
chars.reverse()               # in place
reversed_s = "".join(chars)</code></pre>
<p>The slice approach works on any sequence (string, list, tuple, bytes). The <code>[start:stop:step]</code> syntax with <code>step = -1</code> walks the sequence backward.</p>
<p>Time and space: O(n). All three approaches allocate a new string — Python strings are immutable.</p>
<p>For reversing iteration without building a new string:</p>
<pre><code>for char in reversed(s):
    print(char)</code></pre>
'''

ANSWERS[79] = r'''
<p>Use the built-in <code>len()</code> function — works on any object that defines <code>__len__</code>.</p>
<pre><code>s = "hello world"
len(s)         # 11

# Multi-byte characters count as 1 (Python measures code points, not bytes)
len("café")    # 4 — four Unicode characters
len("🎉")      # 1

# Compare with byte length
len("café".encode("utf-8"))   # 5 — UTF-8 encodes 'é' as 2 bytes</code></pre>
<p>Works on other sequences too: <code>len([1,2,3])</code>, <code>len({"a":1})</code>, <code>len((1,2))</code>.</p>
<p>Gotcha: <code>len()</code> of a generator or iterator raises <code>TypeError</code> — these don't know their size in advance. To count items from a generator, you must consume it:</p>
<pre><code>g = (x for x in range(100))
len(g)           # TypeError

count = sum(1 for _ in g)    # 100 — but now g is exhausted</code></pre>
'''

ANSWERS[80] = r'''
<p>Use the <code>.startswith()</code> method. It's clearer and faster than slicing.</p>
<pre><code>url = "https://example.com"

url.startswith("https://")         # True
url.startswith(("http://", "https://"))   # True — tuple of prefixes

# Case-sensitive — normalize if needed
"HELLO".startswith("hello")              # False
"HELLO".lower().startswith("hello")      # True

# With offsets
s = "  hello world"
s.startswith("hello", 2)             # True — starts checking at index 2
s.startswith("hello", 2, 7)          # True — within range [2, 7)</code></pre>
<p>Passing a tuple checks multiple prefixes at once — more efficient than chained <code>or</code>.</p>
<p>Common pattern: validate URL schemes.</p>
<pre><code>def is_safe_url(u):
    return u.startswith(("https://", "http://"))</code></pre>
<p>Equivalent but verbose: <code>s[:len(prefix)] == prefix</code> — avoid, it's harder to read and doesn't handle tuples.</p>
'''

ANSWERS[81] = r'''
<p>Symmetric to <code>.startswith()</code>: use <code>.endswith()</code>. Same features — single suffix, tuple of suffixes, optional range.</p>
<pre><code>file = "report.pdf"

file.endswith(".pdf")                         # True
file.endswith((".pdf", ".doc", ".docx"))      # True — any of these

# Case-insensitive
"README.md".lower().endswith(".md")           # True

# Path checking
for name in os.listdir("."):
    if name.endswith((".py", ".pyi")):
        print(name)</code></pre>
<p>Performance: <code>.endswith()</code> is O(k) where k is the suffix length — doesn't scan the whole string.</p>
<div class="callout callout-tip">
  <div class="callout-icon">💡</div>
  <div>For file extension checks specifically, <code>pathlib.Path(name).suffix</code> is often cleaner than <code>.endswith()</code> and handles edge cases like missing dots.</div>
</div>
'''

ANSWERS[82] = r'''
<p><strong>Docstrings</strong> are string literals at the top of a module, class, function, or method. Python stores them in the object's <code>__doc__</code> attribute and tools (help, Sphinx, IDEs) display them as documentation.</p>
<pre><code>def calculate_tax(amount, rate):
    """Calculate tax on a given amount.

    Args:
        amount: The taxable amount in dollars.
        rate: The tax rate as a decimal (0.08 for 8%).

    Returns:
        The tax amount, rounded to 2 decimal places.

    Raises:
        ValueError: If rate is negative or greater than 1.
    """
    if not 0 &lt;= rate &lt;= 1:
        raise ValueError("rate must be between 0 and 1")
    return round(amount * rate, 2)

help(calculate_tax)           # prints the docstring
calculate_tax.__doc__         # access directly</code></pre>
<p>Conventions:</p>
<ul>
  <li><strong>Triple quotes</strong> — <code>"""..."""</code>, even for one-liners.</li>
  <li><strong>One-liner for simple functions</strong>; multi-line with sections for anything non-trivial.</li>
  <li><strong>Formats</strong>: Google style (shown above), NumPy style (with separate sections), reStructuredText (<code>:param x:</code>, for Sphinx).</li>
  <li><strong>PEP 257</strong> is the official style guide.</li>
</ul>
<p>Classes and modules can (and should) have docstrings too — placed as the first statement in the class body or module file.</p>
'''

ANSWERS[83] = r'''
<p>Subclass <code>Exception</code> (or a more specific built-in like <code>ValueError</code>). Custom exceptions make error handling more precise.</p>
<pre><code>class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the account balance."""
    def __init__(self, balance, amount):
        super().__init__(f"Cannot withdraw ${amount}; balance is ${balance}")
        self.balance = balance
        self.amount = amount

# Raise
class Account:
    def withdraw(self, amount):
        if amount &gt; self.balance:
            raise InsufficientFundsError(self.balance, amount)
        self.balance -= amount

# Catch
try:
    account.withdraw(1000)
except InsufficientFundsError as e:
    print(f"Blocked: balance={e.balance}, attempted={e.amount}")</code></pre>
<p>Guidelines:</p>
<ul>
  <li><strong>Subclass <code>Exception</code></strong>, not <code>BaseException</code> (which is for system-level things like <code>KeyboardInterrupt</code>).</li>
  <li><strong>Build exception hierarchies</strong> for related errors — e.g., <code>DatabaseError</code> → <code>ConnectionError</code>, <code>QueryError</code>. Consumers can catch specific or general levels.</li>
  <li><strong>Attach context</strong> as instance attributes so handlers can inspect what went wrong.</li>
  <li><strong>Name with <code>Error</code> suffix</strong> by convention (<code>NetworkError</code>, not <code>NetworkException</code>).</li>
</ul>
'''

ANSWERS[84] = r'''
<p>The <code>finally</code> block runs <strong>no matter what</strong> — whether the <code>try</code> block succeeded, raised an exception (caught or not), or even executed <code>return</code>.</p>
<pre><code>def read_config(path):
    f = open(path)
    try:
        return json.load(f)
    except json.JSONDecodeError:
        return {}
    finally:
        f.close()          # always runs — even if parse fails</code></pre>
<p>Use it for <strong>cleanup</strong> that must happen regardless of success:</p>
<ul>
  <li>Closing files, sockets, database connections.</li>
  <li>Releasing locks.</li>
  <li>Logging &ldquo;request complete&rdquo;.</li>
  <li>Resetting state.</li>
</ul>
<div class="callout callout-tip">
  <div class="callout-icon">💡</div>
  <div>For resource cleanup, <strong>prefer <code>with</code> statements</strong> over <code>try/finally</code>. Context managers (<code>with open(...) as f:</code>) encapsulate the pattern and can't be forgotten.</div>
</div>
<p>Full structure: <code>try / except / else / finally</code>. The <code>else</code> runs only if no exception occurred; <code>finally</code> runs always.</p>
'''

ANSWERS[85] = r'''
<p>Use the <code>raise</code> statement followed by an exception instance (or class).</p>
<pre><code># Raise with a message
if age &lt; 0:
    raise ValueError(f"Age must be non-negative, got {age}")

# Raise a built-in
if not isinstance(x, int):
    raise TypeError("Expected int")

# Raise your own
raise InsufficientFundsError(balance, amount)

# Re-raise after logging (preserves the original traceback)
try:
    risky()
except Exception:
    logger.exception("Something went wrong")
    raise        # re-raises the same exception

# Raise from — preserves cause chain
try:
    int(user_input)
except ValueError as e:
    raise AppError("Bad input") from e</code></pre>
<p>Best practices:</p>
<ul>
  <li><strong>Raise early</strong> — fail fast when preconditions are violated.</li>
  <li><strong>Include context</strong> in the message (actual value, not just &ldquo;invalid&rdquo;).</li>
  <li><strong>Use <code>raise ... from ...</code></strong> to chain exceptions so the root cause is visible in the traceback.</li>
  <li><strong>Don't raise <code>Exception</code> directly</strong> — use a specific type so callers can catch the right thing.</li>
</ul>
'''

ANSWERS[86] = r'''
<p>The <code>os</code> module is Python's portable interface to the operating system — files, directories, processes, environment variables.</p>
<pre><code>import os

# Environment variables
os.environ["HOME"]                # "/home/user"
os.environ.get("API_KEY", "")     # safe access with default
os.environ["MY_VAR"] = "hello"    # set (for this process)

# Paths
os.path.join("data", "reports", "2024.csv")  # "data/reports/2024.csv" (or \ on Windows)
os.path.exists("config.ini")
os.path.isfile("config.ini")
os.path.isdir("data")

# Working directory
os.getcwd()                       # current directory
os.chdir("/home/user/projects")   # change directory

# Directory operations
os.makedirs("output/reports", exist_ok=True)
os.remove("old.log")
os.rename("draft.txt", "final.txt")

# Run external commands
os.system("ls -la")               # returns exit code</code></pre>
<p>Many <code>os.path</code> operations have a modern replacement in <strong><code>pathlib</code></strong>, which is more readable:</p>
<pre><code>from pathlib import Path
p = Path("data") / "reports" / "2024.csv"   # cleaner than os.path.join
p.exists()
p.read_text()</code></pre>
<p>Use <code>pathlib</code> for new code; <code>os</code> remains essential for environment variables, processes, and system-level operations.</p>
'''

ANSWERS[87] = r'''
<p>Use <code>os.getcwd()</code> — stands for &ldquo;get current working directory.&rdquo;</p>
<pre><code>import os

os.getcwd()        # "/home/user/projects/myapp"

# pathlib equivalent
from pathlib import Path
Path.cwd()         # PosixPath('/home/user/projects/myapp')</code></pre>
<p>The CWD is the directory from which Python was launched (unless changed via <code>os.chdir</code>). It matters because <strong>relative paths resolve against it</strong>.</p>
<pre><code># If CWD is /home/user/projects/myapp:
open("data.csv")                  # opens /home/user/projects/myapp/data.csv
open("../shared/config.json")     # opens /home/user/projects/shared/config.json</code></pre>
<p>To get the directory of the <em>script itself</em> (not the CWD), use <code>__file__</code>:</p>
<pre><code>import os
script_dir = os.path.dirname(os.path.abspath(__file__))

# Or with pathlib
from pathlib import Path
script_dir = Path(__file__).parent.resolve()</code></pre>
<p>Relying on CWD makes scripts fragile — prefer paths relative to <code>__file__</code> when loading data the script ships with.</p>
'''

ANSWERS[88] = r'''
<p>Three common approaches, from simplest to most powerful.</p>
<pre><code>import os

# os.listdir — flat list of names
os.listdir(".")                # ['file1.txt', 'subdir', 'file2.py']

# os.scandir — with metadata (faster for large dirs)
with os.scandir(".") as it:
    for entry in it:
        if entry.is_file():
            print(entry.name, entry.stat().st_size)

# os.walk — recursive
for root, dirs, files in os.walk("data"):
    for f in files:
        print(os.path.join(root, f))</code></pre>
<p>Modern alternative with <code>pathlib</code>:</p>
<pre><code>from pathlib import Path

# Direct children only
for p in Path(".").iterdir():
    print(p)

# With pattern matching
for p in Path(".").glob("*.py"):        # only Python files
    print(p)

# Recursive with glob
for p in Path(".").rglob("*.txt"):      # all .txt anywhere under "."
    print(p)</code></pre>
<p>Choose based on need: <code>listdir</code> for simple cases, <code>scandir</code> when metadata matters, <code>walk</code> for recursion, <code>pathlib.glob</code> for pattern matching.</p>
'''

ANSWERS[89] = r'''
<p>The <code>sys</code> module exposes information about the Python interpreter and system — command-line arguments, standard streams, the module search path, exit codes.</p>
<pre><code>import sys

# Command-line arguments
sys.argv        # ['script.py', 'arg1', 'arg2']

# Python version
sys.version          # "3.12.1 (main, ...)"
sys.version_info     # sys.version_info(major=3, minor=12, ...)

# Standard streams
sys.stdout.write("hello\n")
print("error", file=sys.stderr)

# Module search path
sys.path        # list of directories Python searches for imports
sys.path.append("/my/custom/modules")

# Exit with a code
sys.exit(0)            # success
sys.exit(1)            # failure
sys.exit("Error msg")  # prints to stderr and exits with 1

# Loaded modules
sys.modules       # dict of all currently loaded modules

# Platform info
sys.platform      # "linux", "darwin" (macOS), "win32"</code></pre>
<p>For CLI argument parsing beyond the basics, use <code>argparse</code> instead of manually slicing <code>sys.argv</code>. For environment variables, use <code>os.environ</code>.</p>
'''

ANSWERS[90] = r'''
<p><code>sys.argv</code> is a list of command-line arguments. Index 0 is the script name; real arguments start at index 1.</p>
<pre><code># greet.py
import sys

if len(sys.argv) != 2:
    print("Usage: python greet.py &lt;name&gt;")
    sys.exit(1)

name = sys.argv[1]
print(f"Hello, {name}!")

# $ python greet.py Alice
# Hello, Alice!</code></pre>
<p>For anything beyond one or two arguments, use the <code>argparse</code> module — it handles validation, help text, defaults, types, and mutually exclusive groups.</p>
<pre><code>import argparse

parser = argparse.ArgumentParser(description="Greet someone.")
parser.add_argument("name", help="Person to greet")
parser.add_argument("--count", type=int, default=1, help="Number of greetings")
parser.add_argument("--shout", action="store_true", help="Use uppercase")

args = parser.parse_args()

greeting = f"Hello, {args.name}!"
if args.shout:
    greeting = greeting.upper()
for _ in range(args.count):
    print(greeting)

# $ python greet.py Alice --count 3 --shout
# HELLO, ALICE!
# HELLO, ALICE!
# HELLO, ALICE!</code></pre>
<p>Alternatives: <code>click</code> (decorator-based, nicer for large CLIs), <code>typer</code> (type-hint-driven).</p>
'''

ANSWERS[91] = r'''
<p>The <code>json</code> module converts between Python objects and JSON — the standard format for configs, APIs, and data exchange.</p>
<pre><code>import json

# Four core functions
json.dumps(obj)     # Python → JSON string
json.dump(obj, f)   # Python → JSON written to file
json.loads(text)    # JSON string → Python
json.load(f)        # JSON read from file → Python

# Type mapping
# dict          ↔ object
# list / tuple  ↔ array
# str           ↔ string
# int / float   ↔ number
# True / False  ↔ true / false
# None          ↔ null</code></pre>
<p>Not everything serializes natively: <code>datetime</code>, <code>Decimal</code>, custom classes, sets, bytes. Pass a <code>default</code> function or subclass <code>JSONEncoder</code>.</p>
<pre><code>from datetime import datetime

data = {"now": datetime.now()}

json.dumps(data)  # TypeError — datetime not serializable

json.dumps(data, default=str)      # "{"now": "2024-11-04 15:30:00"}"
json.dumps(data, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))</code></pre>
<p>For YAML, TOML, or msgpack, use <code>pyyaml</code>, <code>tomllib</code> (stdlib in 3.11+), or <code>msgpack</code> respectively.</p>
'''

ANSWERS[92] = r'''
<p>Use <code>json.dumps()</code> for a string, <code>json.dump()</code> to write to a file.</p>
<pre><code>import json

data = {
    "name": "Ana",
    "age": 30,
    "hobbies": ["reading", "hiking"],
    "active": True,
}

# To string
text = json.dumps(data)
# '{"name": "Ana", "age": 30, "hobbies": ["reading", "hiking"], "active": true}'

# Pretty-printed
text = json.dumps(data, indent=2, sort_keys=True)
# {
#   "active": true,
#   "age": 30,
#   "hobbies": [
#     "reading",
#     "hiking"
#   ],
#   "name": "Ana"
# }

# To file
with open("user.json", "w") as f:
    json.dump(data, f, indent=2)

# Ensure non-ASCII characters render literally
json.dumps({"name": "Café"}, ensure_ascii=False)   # '{"name": "Café"}'</code></pre>
<p>Useful parameters:</p>
<ul>
  <li><code>indent</code> — pretty-print with N spaces (<code>None</code> for compact).</li>
  <li><code>sort_keys=True</code> — deterministic output (great for diffs).</li>
  <li><code>separators=(",", ":")</code> — tightest possible encoding.</li>
  <li><code>ensure_ascii=False</code> — preserve Unicode instead of <code>\u</code>-escaping.</li>
</ul>
'''

ANSWERS[93] = r'''
<p>Use <code>json.loads()</code> for a string, <code>json.load()</code> for a file.</p>
<pre><code>import json

text = '{"name": "Ana", "age": 30, "active": true, "tags": ["admin"]}'

data = json.loads(text)
# {'name': 'Ana', 'age': 30, 'active': True, 'tags': ['admin']}

data["name"]       # "Ana"
data["tags"][0]    # "admin"

# From file
with open("user.json") as f:
    data = json.load(f)

# From URL (with requests library)
import requests
data = requests.get("https://api.example.com/user").json()</code></pre>
<p>Error handling — JSON parsing can fail:</p>
<pre><code>try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    print(f"Invalid JSON at line {e.lineno}, col {e.colno}: {e.msg}")</code></pre>
<p>Security note: <code>json.loads</code> is safe on untrusted input (unlike <code>eval</code>). It only produces plain Python data types — no arbitrary code execution.</p>
'''

ANSWERS[94] = r'''
<p>The <code>datetime</code> module provides classes for dates, times, and durations. Essential for any app dealing with time.</p>
<pre><code>from datetime import datetime, date, time, timedelta, timezone

# Key classes
datetime     # Date + time + optional timezone
date         # Year/month/day
time         # Hour/minute/second
timedelta    # Duration between two datetimes
timezone     # Timezone offset (UTC-aware)

# Creating
now = datetime.now()                              # local time
utc_now = datetime.now(timezone.utc)              # UTC
specific = datetime(2024, 11, 4, 15, 30, 0)
today = date.today()

# Parsing
dt = datetime.strptime("2024-11-04", "%Y-%m-%d")
dt = datetime.fromisoformat("2024-11-04T15:30:00")

# Formatting
dt.strftime("%Y-%m-%d %H:%M:%S")   # "2024-11-04 15:30:00"
dt.isoformat()                      # "2024-11-04T15:30:00"

# Arithmetic
tomorrow = today + timedelta(days=1)
a_week_ago = now - timedelta(weeks=1)
duration = end - start              # returns timedelta</code></pre>
<p><strong>Always store UTC</strong> for anything user-facing. Convert to local zones only at display time. For robust timezone handling, use <code>zoneinfo</code> (stdlib, 3.9+):</p>
<pre><code>from zoneinfo import ZoneInfo
ny = datetime.now(ZoneInfo("America/New_York"))
tokyo = ny.astimezone(ZoneInfo("Asia/Tokyo"))</code></pre>
<p>For more ergonomic APIs, consider third-party libraries like <code>arrow</code> or <code>pendulum</code>.</p>
'''

ANSWERS[95] = r'''
<p>Several options depending on what you need.</p>
<pre><code>from datetime import datetime, date, timezone

# Current local date and time
datetime.now()
# datetime(2024, 11, 4, 15, 30, 42, 123456)

# Current UTC date and time (preferred for timestamps)
datetime.now(timezone.utc)
# datetime(2024, 11, 4, 20, 30, 42, tzinfo=timezone.utc)

# Just the date — no time component
date.today()
# date(2024, 11, 4)

# Epoch timestamp (seconds since 1970-01-01 UTC)
import time
time.time()        # 1730747442.123456

# From datetime to timestamp
datetime.now().timestamp()</code></pre>
<p><code>datetime.utcnow()</code> is deprecated in Python 3.12+ — use <code>datetime.now(timezone.utc)</code> instead. The old one returned a naive datetime (no timezone info), which led to subtle bugs.</p>
<p>For a named timezone:</p>
<pre><code>from zoneinfo import ZoneInfo
datetime.now(ZoneInfo("Europe/London"))</code></pre>
'''

ANSWERS[96] = r'''
<p>Use <code>.strftime()</code> with format codes, or <code>.isoformat()</code> for the standard ISO format.</p>
<pre><code>from datetime import datetime
now = datetime(2024, 11, 4, 15, 30, 45)

# ISO 8601 — machine-readable, sortable
now.isoformat()              # "2024-11-04T15:30:45"

# Common custom formats
now.strftime("%Y-%m-%d")              # "2024-11-04"
now.strftime("%d/%m/%Y")              # "04/11/2024"
now.strftime("%A, %B %d, %Y")         # "Monday, November 04, 2024"
now.strftime("%I:%M %p")               # "03:30 PM"
now.strftime("%H:%M:%S")               # "15:30:45"

# Parse the reverse direction
dt = datetime.strptime("2024-11-04", "%Y-%m-%d")</code></pre>
<p>Common format codes:</p>
<table>
  <thead><tr><th>Code</th><th>Meaning</th><th>Example</th></tr></thead>
  <tbody>
    <tr><td><code>%Y</code></td><td>4-digit year</td><td>2024</td></tr>
    <tr><td><code>%m</code></td><td>Month (01-12)</td><td>11</td></tr>
    <tr><td><code>%d</code></td><td>Day (01-31)</td><td>04</td></tr>
    <tr><td><code>%H</code></td><td>Hour (00-23)</td><td>15</td></tr>
    <tr><td><code>%M</code></td><td>Minute (00-59)</td><td>30</td></tr>
    <tr><td><code>%S</code></td><td>Second (00-59)</td><td>45</td></tr>
    <tr><td><code>%A</code></td><td>Weekday name</td><td>Monday</td></tr>
    <tr><td><code>%B</code></td><td>Month name</td><td>November</td></tr>
  </tbody>
</table>
<p>For locale-aware display (translated month names, local date orderings), use <code>locale.setlocale()</code> or the third-party <code>babel</code> library.</p>
'''

ANSWERS[97] = r'''
<p><code>timedelta</code> represents a duration. You can add/subtract it from a <code>datetime</code>.</p>
<pre><code>from datetime import datetime, timedelta

# Create durations
one_hour    = timedelta(hours=1)
two_weeks   = timedelta(weeks=2)
complex_d   = timedelta(days=3, hours=4, minutes=30, seconds=15)

# Use for arithmetic
now = datetime.now()
tomorrow  = now + timedelta(days=1)
next_week = now + timedelta(days=7)
hour_ago  = now - one_hour

# Duration between two datetimes
duration = datetime(2024, 12, 31) - datetime(2024, 1, 1)
# timedelta(days=365)

# Access total duration
duration.total_seconds()   # 31536000.0
duration.days              # 365</code></pre>
<p>Accepts: <code>weeks</code>, <code>days</code>, <code>hours</code>, <code>minutes</code>, <code>seconds</code>, <code>milliseconds</code>, <code>microseconds</code>. No <code>months</code> or <code>years</code> — their length is ambiguous. For calendar math, use <code>dateutil.relativedelta</code>:</p>
<pre><code>from dateutil.relativedelta import relativedelta
next_month = datetime.now() + relativedelta(months=1)
next_year  = datetime.now() + relativedelta(years=1)</code></pre>
'''

ANSWERS[98] = r'''
<p>The <code>collections</code> module provides specialized container types that go beyond the built-ins.</p>
<table>
  <thead><tr><th>Type</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>Counter</code></td><td>Count occurrences of elements</td></tr>
    <tr><td><code>defaultdict</code></td><td>Dict that auto-creates missing values</td></tr>
    <tr><td><code>OrderedDict</code></td><td>Dict with explicit ordering methods (mostly historical in Python 3.7+)</td></tr>
    <tr><td><code>deque</code></td><td>Double-ended queue with O(1) append/pop at both ends</td></tr>
    <tr><td><code>namedtuple</code></td><td>Tuple with named fields</td></tr>
    <tr><td><code>ChainMap</code></td><td>View of multiple dicts as one</td></tr>
  </tbody>
</table>
<pre><code>from collections import Counter, defaultdict, deque, namedtuple

# Count frequencies
Counter("mississippi")
# Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})

Counter(["a", "b", "a", "c", "b", "a"]).most_common(2)
# [('a', 3), ('b', 2)]

# Dict with default value type
groups = defaultdict(list)
for name, team in [("Ana", "A"), ("Bo", "B"), ("Cy", "A")]:
    groups[team].append(name)
# {"A": ["Ana", "Cy"], "B": ["Bo"]}

# Nested defaultdict
tree = defaultdict(lambda: defaultdict(int))
tree["a"]["x"] += 1

# Fast queue
queue = deque([1, 2, 3])
queue.appendleft(0)     # [0, 1, 2, 3]
queue.pop()             # 3</code></pre>
'''

ANSWERS[99] = r'''
<p><code>namedtuple</code> creates a tuple subclass with named fields — immutable, self-documenting, memory-efficient.</p>
<pre><code>from collections import namedtuple

# Define the type
Point = namedtuple("Point", ["x", "y"])
# Or: Point = namedtuple("Point", "x y")

# Instantiate
p = Point(3, 4)
p.x        # 3 — access by name
p.y        # 4
p[0]       # 3 — still a tuple, indexable
x, y = p   # unpacks like a tuple

# Immutable
p.x = 10   # AttributeError

# Create a modified copy
p2 = p._replace(x=10)   # Point(x=10, y=4)

# To/from dict
p._asdict()              # {'x': 3, 'y': 4}
Point(**{"x": 1, "y": 2})</code></pre>
<p>Use cases: return values with multiple fields, records, coordinate-like data, anything where a dict feels too loose and a class feels too heavy.</p>
<p>Modern alternatives:</p>
<ul>
  <li><strong><code>typing.NamedTuple</code></strong> — same behavior, cleaner syntax with type hints.</li>
  <li><strong><code>@dataclass(frozen=True)</code></strong> — more flexible (mutable by default, methods, inheritance).</li>
</ul>
<pre><code>from typing import NamedTuple
class Point(NamedTuple):
    x: int
    y: int</code></pre>
'''

ANSWERS[100] = r'''
<p><code>deque</code> ("double-ended queue") is a list-like container with <strong>O(1) appends and pops at both ends</strong> — unlike a list, where <code>insert(0, ...)</code> and <code>pop(0)</code> are O(n).</p>
<pre><code>from collections import deque

# Create
d = deque([1, 2, 3])
d = deque([1, 2, 3], maxlen=5)   # bounded — drops from other end when full

# Add
d.append(4)         # [1, 2, 3, 4]     — right end
d.appendleft(0)     # [0, 1, 2, 3, 4]  — left end
d.extend([5, 6])    # [0, 1, 2, 3, 4, 5, 6]

# Remove
d.pop()             # 6 — from right
d.popleft()         # 0 — from left

# Rotate (cyclic shift)
d.rotate(1)         # shift right by 1

# Fixed-size buffer — perfect for &quot;last N items&quot; tracking
recent = deque(maxlen=10)
for event in stream:
    recent.append(event)      # only the 10 most recent are kept</code></pre>
<p>Best for:</p>
<ul>
  <li><strong>Queues</strong> (FIFO) and <strong>stacks</strong> (LIFO).</li>
  <li><strong>Sliding windows</strong> over streams (with <code>maxlen</code>).</li>
  <li><strong>BFS</strong> traversals in graphs/trees.</li>
  <li><strong>Buffers</strong> of recent items (logs, undo history).</li>
</ul>
<p>For thread-safe queues across threads or processes, use <code>queue.Queue</code> instead.</p>
'''
