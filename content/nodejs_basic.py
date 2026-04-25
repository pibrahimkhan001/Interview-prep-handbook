"""Node.Js · Basic · Detailed answers. Each value is an HTML snippet."""

ANSWERS = {}

ANSWERS[1] = r'''
<p><strong>Node.js</strong> is a JavaScript runtime built on Chrome's V8 engine that lets you run JavaScript outside the browser — most commonly on servers. Created by Ryan Dahl in 2009, it broke JavaScript out of the browser and reshaped how servers get built.</p>
<p>Key characteristics:</p>
<ul>
  <li><strong>Single-threaded, event-driven</strong> — one main thread processes callbacks from an event loop rather than spawning a thread per request.</li>
  <li><strong>Non-blocking I/O</strong> — file reads, DB queries, network calls return immediately; a callback fires when they complete.</li>
  <li><strong>npm ecosystem</strong> — the largest package registry on the planet, 2M+ packages.</li>
  <li><strong>Same language on client and server</strong> — share code, types, and mental models across the stack.</li>
</ul>
<pre><code>// server.js
const http = require("node:http");
const server = http.createServer((req, res) =&gt; {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("Hello from Node!");
});
server.listen(3000, () =&gt; console.log("http://localhost:3000"));</code></pre>
<p><strong>What Node is good at:</strong> I/O-heavy workloads — APIs, real-time systems (chat, gaming), streaming. <strong>What it's bad at:</strong> CPU-heavy workloads (image processing, ML inference) — those block the single thread. Use <code>worker_threads</code> or a different runtime for heavy computation.</p>
'''

ANSWERS[2] = r'''
<p>Node.js's defining features all flow from its event-driven, non-blocking design:</p>
<ul>
  <li><strong>Asynchronous, non-blocking I/O</strong> — the runtime issues I/O requests and moves on; callbacks fire when results arrive. One thread handles thousands of concurrent connections.</li>
  <li><strong>Single-threaded event loop</strong> — no thread-per-request overhead; no lock contention in your code (though V8 uses worker threads internally for I/O).</li>
  <li><strong>V8 JavaScript engine</strong> — the same JIT-compiled engine powering Chrome. Fast, actively maintained by Google.</li>
  <li><strong>Built-in core modules</strong> — <code>fs</code>, <code>http</code>, <code>crypto</code>, <code>stream</code>, <code>os</code>, <code>path</code> — everything you need to build a server out of the box.</li>
  <li><strong>npm</strong> — package manager + registry with millions of open-source modules and a tight install/publish flow.</li>
  <li><strong>Cross-platform</strong> — runs on Linux, macOS, Windows, BSDs, IBM mainframes, even ARM SBCs.</li>
  <li><strong>Streams</strong> — first-class abstraction for processing data without buffering it all in memory.</li>
</ul>
<pre><code>// Example of all features at once — HTTP + async + streams + core modules
const http = require("node:http"), fs = require("node:fs");
http.createServer((req, res) =&gt; {
  fs.createReadStream("big.mp4").pipe(res);   // streamed, non-blocking
}).listen(3000);</code></pre>
<p>These features together are why companies like Netflix, PayPal, Uber, and LinkedIn built core systems on Node.</p>
'''

ANSWERS[3] = r'''
<p>Traditional server frameworks (Apache + PHP, Java Servlets, Ruby on Rails with Unicorn, .NET IIS) are built around a <strong>thread-per-request</strong> or process-per-request model. Each incoming connection gets its own OS thread, which blocks on I/O. Handling 10,000 concurrent users means 10,000 threads — heavy memory, context-switching, and often a hard ceiling at a few thousand connections per box.</p>
<p>Node flips this:</p>
<table>
  <thead><tr><th>Aspect</th><th>Traditional (Apache / Java)</th><th>Node.js</th></tr></thead>
  <tbody>
    <tr><td>Concurrency model</td><td>Thread/process per request</td><td>Single thread + event loop</td></tr>
    <tr><td>I/O</td><td>Blocking (thread sleeps)</td><td>Non-blocking (callback)</td></tr>
    <tr><td>Memory per connection</td><td>~2 MB (thread stack)</td><td>Few KB (event listener)</td></tr>
    <tr><td>Max concurrent connections</td><td>Thousands</td><td>Tens of thousands+</td></tr>
    <tr><td>Language</td><td>PHP/Java/Ruby/C#</td><td>JavaScript (same as frontend)</td></tr>
    <tr><td>CPU-heavy work</td><td>Fine — threads parallelize</td><td>Blocks event loop — bad</td></tr>
  </tbody>
</table>
<p><strong>Practical difference:</strong> Node shines for I/O-heavy, many-connection workloads (chat, APIs, proxies). Java/Go shine for CPU-heavy parallel workloads. Modern Node can also use <code>cluster</code> or <code>worker_threads</code> to exploit multiple cores — but mental model stays event-driven.</p>
'''

ANSWERS[4] = r'''
<p><strong>npm</strong> (Node Package Manager) is both a command-line tool and an online registry of packages. It's how you install libraries, manage dependencies, and publish your own code.</p>
<p>Common commands:</p>
<pre><code>npm init -y                     # create a package.json
npm install express             # install &amp; save as dependency
npm install --save-dev jest     # save as devDependency (test/build only)
npm install -g nodemon          # install globally (available as a CLI)
npm uninstall express           # remove
npm update                      # update all to latest compatible
npm outdated                    # list packages with newer versions
npm run dev                     # run a script from package.json
npm ci                          # clean install from lockfile (CI/CD)
npm publish                     # publish to the registry</code></pre>
<p>Every installed package is tracked in <code>package.json</code> (declarative: what you want) and <code>package-lock.json</code> (exact: what you got, with sub-dependency versions and integrity hashes).</p>
<ul>
  <li><strong><code>dependencies</code></strong> — needed at runtime.</li>
  <li><strong><code>devDependencies</code></strong> — only needed during development/build (testing frameworks, bundlers, linters).</li>
  <li><strong><code>peerDependencies</code></strong> — expected to be provided by the host app (common for plugins).</li>
</ul>
<p>Alternatives like <strong>yarn</strong> and <strong>pnpm</strong> read the same <code>package.json</code> and offer faster installs and better disk usage (pnpm uses hard links to share packages across projects).</p>
'''

ANSWERS[5] = r'''
<p>Pass the <code>-g</code> (or <code>--global</code>) flag to <code>npm install</code>. Global packages install to a system-wide location (not your project's <code>node_modules</code>) and their executables are added to your <code>PATH</code>.</p>
<pre><code>npm install -g nodemon          # install
nodemon server.js               # now available as a shell command

npm list -g --depth=0           # list globally installed packages
npm uninstall -g nodemon        # uninstall

# See where global packages live
npm config get prefix
# Usually /usr/local on macOS/Linux, or %APPDATA%\npm on Windows</code></pre>
<p><strong>When to install globally:</strong></p>
<ul>
  <li>Standalone CLI tools you run from the terminal — <code>nodemon</code>, <code>pm2</code>, <code>typescript</code>, <code>vercel</code>.</li>
  <li>Tools you use across many projects independently.</li>
</ul>
<p><strong>When NOT to install globally:</strong></p>
<ul>
  <li>Project dependencies (Express, React, lodash) — these belong in <code>package.json</code> so everyone on the team gets the same version.</li>
  <li>Anything your code <code>require()</code>s — global modules aren't resolvable by default.</li>
</ul>
<p><strong>Modern alternative:</strong> <code>npx</code> runs a package without installing globally — <code>npx create-react-app my-app</code> fetches, runs once, and cleans up. Less pollution, always the latest version.</p>
'''

ANSWERS[6] = r'''
<p><strong><code>package.json</code></strong> is the manifest file at the root of every Node project. It describes what the project is and what it needs to run.</p>
<pre><code>{
  "name": "my-app",
  "version": "1.0.0",
  "description": "A sample Node app",
  "main": "index.js",
  "type": "module",              // use ES modules ("commonjs" is default)
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  },
  "engines": { "node": "&gt;=18" },  // required Node version
  "license": "MIT"
}</code></pre>
<p><strong>Key fields:</strong></p>
<ul>
  <li><strong><code>name</code>, <code>version</code></strong> — identity; version follows semver.</li>
  <li><strong><code>main</code></strong> — entry file that <code>require("my-app")</code> resolves to.</li>
  <li><strong><code>scripts</code></strong> — custom commands run via <code>npm run &lt;name&gt;</code>.</li>
  <li><strong><code>dependencies</code> / <code>devDependencies</code></strong> — runtime vs dev-only packages with version ranges (<code>^</code> = same major, <code>~</code> = same minor).</li>
  <li><strong><code>engines</code></strong> — Node version requirements (advisory by default; strict with <code>engine-strict=true</code>).</li>
</ul>
<p>The companion <strong><code>package-lock.json</code></strong> locks exact resolved versions of every transitive dependency — commit it so teammates and CI get byte-identical installs.</p>
'''

ANSWERS[7] = r'''
<p>Node's built-in <code>http</code> module lets you spin up a server in a handful of lines — no framework needed.</p>
<pre><code>const http = require("node:http");

const server = http.createServer((req, res) =&gt; {
  console.log(`${req.method} ${req.url}`);

  if (req.url === "/") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end("&lt;h1&gt;Hello World&lt;/h1&gt;");
  } else if (req.url === "/api") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, time: Date.now() }));
  } else {
    res.writeHead(404).end("Not found");
  }
});

server.listen(3000, () =&gt; {
  console.log("Server running at http://localhost:3000");
});</code></pre>
<p><strong>What happens:</strong> <code>createServer</code> returns an EventEmitter; the callback fires on every request. The <code>req</code> object is a readable stream with headers, URL, and body data. The <code>res</code> object is a writable stream — you set status + headers, then write the body and call <code>end()</code>.</p>
<p><strong>In practice:</strong> for anything beyond toy servers, you'll reach for <strong>Express</strong>, <strong>Fastify</strong>, or <strong>Hono</strong> — frameworks that add routing, middleware, body parsing, and error handling on top of this same <code>http</code> module. But knowing the raw layer is valuable for debugging, writing proxies, and understanding how frameworks work underneath.</p>
'''

ANSWERS[8] = r'''
<p>A <strong>module</strong> in Node.js is a reusable piece of code — usually a single file — that exports values (functions, classes, objects) for other files to import. Modules provide encapsulation: each file has its own scope, and nothing leaks to the global namespace unless explicitly exported.</p>
<p>Three kinds of modules:</p>
<ul>
  <li><strong>Core modules</strong> — bundled with Node (<code>fs</code>, <code>http</code>, <code>path</code>, <code>crypto</code>). Loaded via <code>require("node:fs")</code> or <code>import</code> — instant, no install needed.</li>
  <li><strong>Local modules</strong> — your own files. Referenced by relative path: <code>require("./utils.js")</code>.</li>
  <li><strong>Third-party modules</strong> — installed via npm, live in <code>node_modules</code>: <code>require("express")</code>.</li>
</ul>
<pre><code>// math.js — a local module
function add(a, b) { return a + b; }
function subtract(a, b) { return a - b; }
module.exports = { add, subtract };

// app.js — consume it
const math = require("./math.js");
console.log(math.add(2, 3));    // 5

// ESM equivalent (requires "type": "module" in package.json)
// math.mjs
export function add(a, b) { return a + b; }
// app.mjs
import { add } from "./math.mjs";</code></pre>
<p>Node supports two module systems: <strong>CommonJS</strong> (the original: <code>require</code>/<code>module.exports</code>) and <strong>ES Modules</strong> (<code>import</code>/<code>export</code>, the newer standard). You can mix them carefully, but it's cleaner to pick one per project.</p>
'''

ANSWERS[9] = r'''
<p>Node supports both CommonJS (CJS) and ES Modules (ESM). Syntax differs, but the concept is the same: files export values, other files import them.</p>
<p><strong>CommonJS — the classic Node style:</strong></p>
<pre><code>// utils.js — exporting
function greet(name) { return `Hello, ${name}`; }
const PI = 3.14;
class Logger { log(msg) { console.log(msg); } }

module.exports = { greet, PI, Logger };   // export object
// Or single default:  module.exports = greet;

// app.js — importing
const { greet, PI } = require("./utils.js");
const utils = require("./utils.js");          // import the whole object
greet("Ada");</code></pre>
<p><strong>ES Modules — the modern standard:</strong></p>
<pre><code>// utils.mjs — (or set "type": "module" in package.json for .js)
export function greet(name) { return `Hello, ${name}`; }
export const PI = 3.14;
export default class Logger { log(msg) { console.log(msg); } }

// app.mjs — importing
import Logger, { greet, PI } from "./utils.mjs";
import * as utils from "./utils.mjs";
</code></pre>
<p><strong>Key differences:</strong> CJS is synchronous (you can <code>require()</code> anywhere); ESM is async and has <code>import</code> hoisted to the top of the file. ESM supports tree-shaking and is the spec standard shared with browsers. For new projects, prefer ESM. Most npm packages now ship both.</p>
'''

ANSWERS[10] = r'''
<p>The <strong>event loop</strong> is the runtime mechanism that makes Node's single thread feel concurrent. It continuously checks a queue of pending callbacks and invokes them in phases when their associated I/O or timer completes.</p>
<p>The loop runs in <strong>phases</strong>, each with its own queue:</p>
<ol>
  <li><strong>Timers</strong> — callbacks scheduled by <code>setTimeout</code> / <code>setInterval</code> whose timers expired.</li>
  <li><strong>Pending callbacks</strong> — certain system callbacks (e.g., TCP errors).</li>
  <li><strong>Poll</strong> — retrieve new I/O events; execute I/O-related callbacks (most of your code runs here).</li>
  <li><strong>Check</strong> — <code>setImmediate</code> callbacks.</li>
  <li><strong>Close</strong> — <code>close</code> events (<code>socket.on("close", ...)</code>).</li>
</ol>
<p>Between every phase, Node also drains the <strong>microtask queue</strong>: resolved Promises (<code>.then</code>) and <code>process.nextTick</code> callbacks. Microtasks always run before the next phase.</p>
<pre><code>console.log("1");
setTimeout(() =&gt; console.log("2 timeout"), 0);
setImmediate(() =&gt; console.log("3 immediate"));
Promise.resolve().then(() =&gt; console.log("4 promise"));
process.nextTick(() =&gt; console.log("5 nextTick"));
console.log("6");

// Output: 1, 6, 5, 4, 2 timeout, 3 immediate
</code></pre>
<p><strong>The takeaway:</strong> long synchronous work blocks the entire loop — every connection waits. Keep handlers small and async; offload CPU-heavy work to <code>worker_threads</code>.</p>
'''

ANSWERS[11] = r'''
<p><strong>Synchronous</strong> code runs top to bottom, each line completing before the next begins. <strong>Asynchronous</strong> code starts work, returns immediately, and delivers the result later via callback / Promise / await.</p>
<pre><code>// Synchronous — blocks the event loop
const fs = require("node:fs");
const data = fs.readFileSync("big.log", "utf-8");   // ← nothing else can run until done
console.log(data);

// Asynchronous callback — non-blocking
fs.readFile("big.log", "utf-8", (err, data) =&gt; {
  if (err) return console.error(err);
  console.log(data);
});
console.log("this runs first");  // prints before the file contents

// Asynchronous Promise — modern style
fs.promises.readFile("big.log", "utf-8")
  .then(data =&gt; console.log(data))
  .catch(err =&gt; console.error(err));

// async/await — Promises with cleaner syntax
async function load() {
  try {
    const data = await fs.promises.readFile("big.log", "utf-8");
    console.log(data);
  } catch (err) { console.error(err); }
}</code></pre>
<p><strong>Why it matters in Node:</strong> Node has <em>one thread</em>. Sync I/O freezes the whole server — every pending request, every timer, every incoming connection. Use sync APIs only at startup (reading config files) or in CLI scripts. Everywhere else, default to async. The <code>Sync</code> suffix on fs methods is a warning flag: "this blocks."</p>
'''

ANSWERS[12] = r'''
<p>A <strong>callback</strong> is a function passed to another function, to be called later when something completes. It's how Node originally expressed async results before Promises arrived.</p>
<pre><code>// setTimeout takes a callback to run after 1 second
setTimeout(() =&gt; console.log("tick"), 1000);

// Reading a file with a callback
const fs = require("node:fs");
fs.readFile("data.txt", "utf-8", (err, data) =&gt; {
  if (err) return console.error("failed:", err);
  console.log("contents:", data);
});</code></pre>
<p>Node adopted the <strong>error-first callback convention</strong>: the first argument is always an error (or <code>null</code>), and subsequent arguments are the results. Always check <code>err</code> first before using data — skipping this is the #1 source of production bugs in older Node code.</p>
<p><strong>Callback hell:</strong> when callbacks nest into callbacks, indentation grows sideways and error handling gets repeated at every level:</p>
<pre><code>fs.readFile("a.txt", (err, a) =&gt; {
  if (err) return done(err);
  fs.readFile("b.txt", (err, b) =&gt; {
    if (err) return done(err);
    fs.writeFile("c.txt", a + b, (err) =&gt; {
      if (err) return done(err);
      done(null, "done!");
    });
  });
});</code></pre>
<p>Modern Node code prefers <strong>Promises</strong> and <strong>async/await</strong>, which flatten this structure and centralize error handling in <code>try/catch</code>. Callbacks are still used in libraries and EventEmitter APIs (<code>emitter.on("data", cb)</code>).</p>
'''

ANSWERS[13] = r'''
<p>Error handling in Node takes different forms depending on whether the code is synchronous, callback-based, Promise-based, or using an EventEmitter.</p>
<pre><code>// 1. Synchronous — try/catch
try {
  JSON.parse("not json");
} catch (err) {
  console.error("parse failed:", err.message);
}

// 2. Error-first callback
fs.readFile("x.txt", (err, data) =&gt; {
  if (err) return handleError(err);
  useData(data);
});

// 3. Promises — .catch()
fetch("/api").then(r =&gt; r.json()).catch(err =&gt; console.error(err));

// 4. async/await — try/catch around await
async function load() {
  try {
    const res = await fetch("/api");
    return await res.json();
  } catch (err) {
    console.error("load failed:", err);
    throw err;   // re-throw or handle
  }
}

// 5. EventEmitter — listen for "error" event (unhandled ones crash!)
server.on("error", err =&gt; console.error("server error:", err));

// 6. Last-resort global handlers — log then exit
process.on("uncaughtException", (err) =&gt; {
  console.error("FATAL:", err);
  process.exit(1);                  // state may be corrupted — don't continue
});
process.on("unhandledRejection", (reason) =&gt; {
  console.error("unhandled rejection:", reason);
});</code></pre>
<p><strong>Rules of thumb:</strong> never swallow errors silently. Let operational errors (network failure, bad input) bubble up to a central handler. Crash on programmer errors (bugs, invalid state) and restart via a process manager like PM2 or systemd — it's safer than continuing with corrupted state.</p>
'''

ANSWERS[14] = r'''
<p><strong>Streams</strong> process data in chunks instead of loading it all into memory. They're how Node handles gigabyte files, video transcoding, and long HTTP responses without crashing.</p>
<p>Four types of streams, all EventEmitters:</p>
<ul>
  <li><strong>Readable</strong> — data flows <em>out</em> (file reads, HTTP request body, <code>process.stdin</code>).</li>
  <li><strong>Writable</strong> — data flows <em>in</em> (file writes, HTTP response, <code>process.stdout</code>).</li>
  <li><strong>Duplex</strong> — both (TCP sockets, WebSockets).</li>
  <li><strong>Transform</strong> — Duplex that modifies on the way through (gzip, crypto ciphers).</li>
</ul>
<pre><code>// Copy a 10 GB file without loading it — constant memory
const fs = require("node:fs");
fs.createReadStream("huge.mp4")
  .pipe(fs.createWriteStream("copy.mp4"))
  .on("finish", () =&gt; console.log("done"));

// Stream + transform — compress on the fly
const zlib = require("node:zlib");
fs.createReadStream("big.log")
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream("big.log.gz"));

// Events on a stream
const stream = fs.createReadStream("x.txt");
stream.on("data", chunk =&gt; console.log("got", chunk.length));
stream.on("end",  ()    =&gt; console.log("done"));
stream.on("error", err  =&gt; console.error(err));</code></pre>
<p><strong>Why they matter:</strong> a naive <code>fs.readFile</code> of a 5 GB file allocates 5 GB — likely crashing your process. <code>createReadStream</code> keeps memory flat at ~64 KB per pipe regardless of file size. Modern Node also supports <strong>async iteration</strong>: <code>for await (const chunk of stream)</code> — cleaner than the event API.</p>
'''

ANSWERS[15] = r'''
<p>A <strong>Buffer</strong> is Node's representation of raw binary data — a fixed-length chunk of bytes sitting outside the V8 heap. You'll work with Buffers any time you're not dealing with UTF-8 strings: files, network packets, images, encryption.</p>
<pre><code>// Create buffers
const a = Buffer.from("hello");                    // from string (UTF-8)
const b = Buffer.from([72, 101, 108, 108, 111]);   // from byte array
const c = Buffer.alloc(10);                        // zeroed, length 10
const d = Buffer.allocUnsafe(10);                  // faster but contains garbage

// Convert back
a.toString();               // "hello"
a.toString("hex");          // "68656c6c6f"
a.toString("base64");       // "aGVsbG8="
a.length;                   // 5 (bytes, not characters!)

// Concatenate and slice
const combined = Buffer.concat([a, b]);
const slice = a.subarray(0, 3);    // "hel"

// Binary protocols — read/write typed values at offsets
const buf = Buffer.alloc(4);
buf.writeUInt32BE(1234567890, 0);  // big-endian 32-bit unsigned int</code></pre>
<p><strong>Key points:</strong></p>
<ul>
  <li><strong>Length is in bytes, not characters</strong> — <code>Buffer.from("€").length === 3</code> (UTF-8 multibyte).</li>
  <li>Stream chunks are Buffers by default unless you set an encoding.</li>
  <li>Pre-Node-10, <code>new Buffer()</code> was unsafe (could leak memory) — always use <code>Buffer.alloc()</code> / <code>Buffer.from()</code>.</li>
  <li>Modern alternative: the standard <code>Uint8Array</code> / <code>ArrayBuffer</code> work in Node and browsers; most Node APIs accept either.</li>
</ul>
'''

ANSWERS[16] = r'''
<p>Node's <code>fs</code> module offers three flavors of every file operation: synchronous, callback, and Promise. Modern code should prefer Promises.</p>
<pre><code>const fs = require("node:fs");
const fsp = require("node:fs/promises");

// READ — whole file
const data = await fsp.readFile("notes.txt", "utf-8");
console.log(data);

// READ — without encoding returns a Buffer
const buf = await fsp.readFile("image.png");

// WRITE — replaces existing content
await fsp.writeFile("out.txt", "Hello\n");

// APPEND — add without overwriting
await fsp.appendFile("log.txt", "new line\n");

// Delete
await fsp.unlink("tmp.txt");

// Large files — STREAMING instead of readFile
fs.createReadStream("huge.log")
  .pipe(fs.createWriteStream("copy.log"));

// Check existence (prefer stat over the deprecated exists)
try { await fsp.access("config.json"); /* exists */ }
catch { /* missing */ }

// Read a directory
const files = await fsp.readdir("./src");

// File metadata
const stats = await fsp.stat("report.pdf");
console.log(stats.size, stats.mtime, stats.isDirectory());</code></pre>
<p><strong>Gotchas:</strong></p>
<ul>
  <li>Always specify an encoding (<code>"utf-8"</code>) for text files — otherwise you get a Buffer.</li>
  <li>Never use <code>readFileSync</code> or <code>writeFileSync</code> inside request handlers — they freeze the event loop for the entire server.</li>
  <li>For multi-gigabyte files, use streams. <code>readFile</code> allocates the full size in memory.</li>
  <li>Handle errors — files get deleted, permissions change, disks fill up.</li>
</ul>
'''

ANSWERS[17] = r'''
<p>The <strong><code>fs</code></strong> module (file system) is Node's standard interface to the host's filesystem. It wraps POSIX-style system calls (<code>open</code>, <code>read</code>, <code>write</code>, <code>stat</code>, <code>unlink</code>) in JavaScript APIs.</p>
<p>Core capabilities:</p>
<ul>
  <li><strong>File I/O</strong> — read, write, append, delete, copy, rename.</li>
  <li><strong>Directory operations</strong> — list, create, remove, recursively traverse.</li>
  <li><strong>Metadata</strong> — file size, permissions, timestamps, owner.</li>
  <li><strong>Watching</strong> — observe file/directory changes in real time.</li>
  <li><strong>Streams</strong> — process huge files with constant memory.</li>
  <li><strong>Links &amp; paths</strong> — symbolic/hard links, resolving real paths.</li>
</ul>
<pre><code>const fs = require("node:fs");
const fsp = require("node:fs/promises");

// Metadata
const stats = await fsp.stat("app.log");
stats.size;           // bytes
stats.isFile();       // true/false
stats.isDirectory();
stats.birthtime;      // creation date

// Create a directory (recursive = like mkdir -p)
await fsp.mkdir("logs/2026/04", { recursive: true });

// Watch for changes (useful for dev tooling)
fs.watch("./src", { recursive: true }, (event, filename) =&gt; {
  console.log(`${event}: ${filename}`);
});

// Copy &amp; rename
await fsp.copyFile("a.txt", "b.txt");
await fsp.rename("old.txt", "new.txt");</code></pre>
<p><strong>API variants:</strong> <code>fs</code> (callbacks), <code>fs.promises</code> or <code>node:fs/promises</code> (Promise-based — preferred for new code), and <code>fs</code> sync methods (<code>readFileSync</code>, etc.) for startup code only. Large files deserve streams (<code>createReadStream</code>) rather than <code>readFile</code>.</p>
'''

ANSWERS[18] = r'''
<p>Node's <code>http</code> module exposes both the server side (receiving requests) and the client side (making requests). Most production apps use a framework like Express on top, but understanding the raw API is valuable.</p>
<pre><code>const http = require("node:http");

// SERVER — handling requests &amp; responses
const server = http.createServer((req, res) =&gt; {
  // Read request metadata
  console.log(req.method, req.url, req.headers);

  // For POST/PUT — body arrives as stream chunks
  if (req.method === "POST") {
    let body = "";
    req.on("data", chunk =&gt; body += chunk);
    req.on("end", () =&gt; {
      const data = JSON.parse(body);
      res.writeHead(201, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ received: data }));
    });
    return;
  }

  // Simple GET response
  res.writeHead(200, {
    "Content-Type": "text/html",
    "Cache-Control": "no-cache",
  });
  res.end("&lt;h1&gt;Hello&lt;/h1&gt;");
});

server.listen(3000);

// CLIENT — making outbound requests (consider fetch() instead)
http.get("http://api.example.com/users", (res) =&gt; {
  let data = "";
  res.on("data", chunk =&gt; data += chunk);
  res.on("end", () =&gt; console.log(JSON.parse(data)));
});</code></pre>
<p><strong>Modern alternative for outbound:</strong> Node 18+ has a built-in <code>fetch()</code> matching the browser API — strongly preferred over the raw <code>http.get</code>.</p>
<p><strong>For servers</strong>, reach for <strong>Express</strong>, <strong>Fastify</strong>, or <strong>Hono</strong> — they wrap this module with routing, middleware, JSON parsing, and error handling you'd otherwise write yourself.</p>
'''

ANSWERS[19] = r'''
<p><strong>Express.js</strong> is the most popular Node web framework — minimalist, unopinionated, and battle-tested since 2010. It builds on the core <code>http</code> module, adding routing, middleware, and helpers for building REST APIs and web apps.</p>
<pre><code>npm install express

// app.js
const express = require("express");
const app = express();

app.use(express.json());                   // parse JSON bodies

app.get("/", (req, res) =&gt; {
  res.send("&lt;h1&gt;Home&lt;/h1&gt;");
});

app.get("/users/:id", (req, res) =&gt; {
  res.json({ id: req.params.id, name: "Ada" });
});

app.post("/users", (req, res) =&gt; {
  const user = req.body;
  // ... save ...
  res.status(201).json(user);
});

app.use((err, req, res, next) =&gt; {         // error handler (4 args)
  console.error(err);
  res.status(500).json({ error: "internal" });
});

app.listen(3000);</code></pre>
<p><strong>Why Express:</strong></p>
<ul>
  <li><strong>Huge ecosystem</strong> — middleware for auth, CORS, rate limiting, logging, sessions.</li>
  <li><strong>Stable &amp; familiar</strong> — the de-facto standard; most tutorials and SO answers use it.</li>
  <li><strong>Lightweight</strong> — doesn't lock you into ORMs, templating, or folder structure.</li>
</ul>
<p><strong>Alternatives worth knowing:</strong> <strong>Fastify</strong> (faster, schema-first), <strong>Koa</strong> (from the Express team; async/await-native), <strong>NestJS</strong> (opinionated, Angular-style DI), <strong>Hono</strong> (edge-runtime friendly). For new projects in 2026, Fastify and Hono are gaining ground on raw performance.</p>
'''

ANSWERS[20] = r'''
<p>A <strong>route</strong> in Express maps an HTTP method + URL pattern to a handler function. The API is <code>app.METHOD(path, handler)</code>.</p>
<pre><code>const express = require("express");
const app = express();

// GET — fetch something
app.get("/", (req, res) =&gt; {
  res.send("Welcome!");
});

// Route parameter — :id is captured in req.params
app.get("/users/:id", (req, res) =&gt; {
  res.json({ userId: req.params.id });
});

// Multiple parameters
app.get("/posts/:postId/comments/:commentId", (req, res) =&gt; {
  const { postId, commentId } = req.params;
  res.json({ postId, commentId });
});

// Query string — /search?q=node&amp;page=2
app.get("/search", (req, res) =&gt; {
  const { q, page } = req.query;
  res.json({ q, page });
});

// POST / PUT / DELETE — typical REST pattern
app.post("/users", (req, res) =&gt; res.status(201).json(req.body));
app.put("/users/:id", (req, res) =&gt; res.json({ updated: req.params.id }));
app.delete("/users/:id", (req, res) =&gt; res.status(204).end());

// Regex / wildcard routes
app.get(/^\/articles\/(\d+)$/, (req, res) =&gt; {
  res.json({ articleId: req.params[0] });
});

app.listen(3000);</code></pre>
<p><strong>Route organization:</strong> for anything beyond a small app, split routes into <code>Router</code> files: <code>const router = express.Router()</code>, then <code>app.use("/api/users", usersRouter)</code>. This keeps <code>app.js</code> short and groups related endpoints. Always define routes from most specific to least specific — Express matches in declaration order.</p>
'''

ANSWERS[21] = r'''
<p><strong>Middleware</strong> are functions that sit in the request/response pipeline. Each middleware can inspect/modify <code>req</code> and <code>res</code>, then call <code>next()</code> to pass control to the next function, or end the response to stop the chain.</p>
<pre><code>const app = express();

// Application-level middleware — runs for EVERY request
app.use((req, res, next) =&gt; {
  console.log(`${req.method} ${req.url}`);
  next();                              // continue to next middleware/route
});

// Built-in middleware
app.use(express.json());               // parse JSON request bodies
app.use(express.static("public"));     // serve static files

// Third-party middleware
app.use(require("cors")());
app.use(require("helmet")());          // security headers

// Path-scoped middleware
app.use("/api", (req, res, next) =&gt; {
  if (!req.headers.authorization) return res.status(401).end();
  next();
});

// Route-level middleware — auth guard for a specific route
function requireAdmin(req, res, next) {
  if (req.user?.role !== "admin") return res.status(403).end();
  next();
}
app.delete("/users/:id", requireAdmin, (req, res) =&gt; res.status(204).end());

// Error-handling middleware — 4 arguments (Express knows by the signature)
app.use((err, req, res, next) =&gt; {
  console.error(err);
  res.status(500).json({ error: err.message });
});</code></pre>
<p><strong>Common middleware uses:</strong> logging, authentication, body parsing, CORS, compression, rate limiting, request validation. Ordering matters — <code>express.json()</code> must run before any route that reads <code>req.body</code>. Error handlers (4-arg signature) must be registered <em>last</em>.</p>
'''

ANSWERS[22] = r'''
<p>Form data arrives in two main shapes, depending on the HTML form's <code>enctype</code>. Express needs different middleware for each.</p>
<pre><code>// 1. application/x-www-form-urlencoded (default for &lt;form&gt;)
// Key-value pairs like: name=Ada&amp;age=36
app.use(express.urlencoded({ extended: true }));

app.post("/signup", (req, res) =&gt; {
  console.log(req.body);    // { name: "Ada", age: "36" }
  res.send("OK");
});

// 2. multipart/form-data — for file uploads
// Use the "multer" middleware
const multer = require("multer");
const upload = multer({ dest: "uploads/" });

app.post("/upload", upload.single("avatar"), (req, res) =&gt; {
  console.log(req.file);    // { filename, path, size, mimetype }
  console.log(req.body);    // other non-file fields
  res.json({ ok: true });
});

// Multiple files
app.post("/gallery", upload.array("photos", 10), (req, res) =&gt; {
  res.json({ count: req.files.length });
});

// 3. application/json (typical for SPAs/APIs, not HTML forms)
app.use(express.json({ limit: "1mb" }));

app.post("/api/user", (req, res) =&gt; {
  res.json(req.body);
});</code></pre>
<p><strong>Security essentials:</strong></p>
<ul>
  <li>Always set size limits — <code>express.json({ limit: "100kb" })</code> — to prevent memory exhaustion attacks.</li>
  <li>Validate every field before using it. Libraries like <strong>zod</strong>, <strong>joi</strong>, or <strong>express-validator</strong> handle this cleanly.</li>
  <li>For file uploads, whitelist extensions/mime types, scan for malware, store outside the webroot.</li>
  <li>Use CSRF protection for session-based forms (e.g., <code>csurf</code> or same-origin + SameSite cookies).</li>
</ul>
'''

ANSWERS[23] = r'''
<p><strong><code>body-parser</code></strong> is middleware that parses incoming request bodies and populates <code>req.body</code> with the result. Before Express 4.16 it was a separate package; now it's <strong>built into Express</strong> itself as <code>express.json()</code> and <code>express.urlencoded()</code>.</p>
<pre><code>// OLD WAY (Express &lt; 4.16 or the standalone package)
const bodyParser = require("body-parser");
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// MODERN WAY (Express 4.16+)
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Usage — after the middleware runs, req.body is populated
app.post("/submit", (req, res) =&gt; {
  console.log(req.body);      // { name: "Ada" }
  res.json(req.body);
});</code></pre>
<p><strong>What it actually does:</strong> HTTP requests deliver the body as a raw stream of bytes. Without a parser, <code>req.body</code> is <code>undefined</code>. Body-parser:</p>
<ol>
  <li>Inspects the <code>Content-Type</code> header.</li>
  <li>Reads the body stream to completion (up to a configurable size limit).</li>
  <li>Parses the bytes according to the content type (JSON → object, URL-encoded → key/value pairs).</li>
  <li>Attaches the result to <code>req.body</code>.</li>
</ol>
<p><strong>Options worth knowing:</strong> <code>limit</code> caps body size (default 100 KB — prevents DoS); <code>extended: true</code> for URL-encoded uses the <code>qs</code> library to allow nested objects (<code>a[b]=c</code> → <code>{a:{b:"c"}}</code>). <strong>Don't double-register</strong> both <code>body-parser</code> and Express's built-ins — you'll parse the body twice and break things.</p>
'''

ANSWERS[24] = r'''
<p>Cookies are small key-value strings the server sends with responses and the browser echoes back on every subsequent request to the same domain. They're the classic way to maintain session state.</p>
<pre><code>// Set cookies manually via res.setHeader
app.get("/login", (req, res) =&gt; {
  res.setHeader("Set-Cookie", "sessionId=abc123; HttpOnly; Secure; SameSite=Strict");
  res.send("Logged in");
});

// With cookie-parser middleware (for reading)
const cookieParser = require("cookie-parser");
app.use(cookieParser("signing-secret"));

app.get("/dashboard", (req, res) =&gt; {
  console.log(req.cookies);          // { sessionId: "abc123" }
  console.log(req.signedCookies);    // only signed ones
  res.send("dashboard");
});

// Express's built-in res.cookie() — cleanest setting API
app.get("/settheme", (req, res) =&gt; {
  res.cookie("theme", "dark", {
    httpOnly: true,                  // not readable by JS — prevents XSS theft
    secure: true,                    // HTTPS only
    sameSite: "strict",              // CSRF protection
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    signed: true,                    // tamper-proof (needs cookieParser secret)
  });
  res.send("theme saved");
});

// Remove a cookie
res.clearCookie("sessionId");</code></pre>
<p><strong>Security flags you should always consider:</strong></p>
<ul>
  <li><strong><code>HttpOnly</code></strong> — blocks JavaScript access; essential for session cookies.</li>
  <li><strong><code>Secure</code></strong> — only sent over HTTPS.</li>
  <li><strong><code>SameSite=Strict</code> or <code>Lax</code></strong> — mitigates CSRF.</li>
  <li><strong>Sign</strong> sensitive cookies to detect tampering.</li>
  <li>Never store sensitive data directly in a cookie — store a session ID and keep data server-side.</li>
</ul>
'''

ANSWERS[25] = r'''
<p><strong>POST</strong> creates a new resource; <strong>PUT</strong> replaces an existing one at a known URL. The formal difference is about <strong>idempotency</strong>.</p>
<table>
  <thead><tr><th>Aspect</th><th>POST</th><th>PUT</th></tr></thead>
  <tbody>
    <tr><td>Intent</td><td>Create a new resource</td><td>Create or replace at a specific URL</td></tr>
    <tr><td>Idempotent?</td><td>No — same POST twice creates two resources</td><td>Yes — same PUT any number of times has same effect</td></tr>
    <tr><td>URL</td><td><code>POST /users</code> (server picks ID)</td><td><code>PUT /users/42</code> (client knows ID)</td></tr>
    <tr><td>Partial update?</td><td>Acceptable</td><td>No — must send the full representation (use PATCH for partial)</td></tr>
    <tr><td>Response</td><td><code>201 Created</code> + Location header</td><td><code>200 OK</code> or <code>204 No Content</code></td></tr>
  </tbody>
</table>
<pre><code>// POST — create
app.post("/users", (req, res) =&gt; {
  const id = generateId();
  users[id] = req.body;
  res.status(201).location(`/users/${id}`).json({ id, ...req.body });
});

// PUT — replace (idempotent)
app.put("/users/:id", (req, res) =&gt; {
  users[req.params.id] = req.body;   // entire record replaced
  res.json(users[req.params.id]);
});

// PATCH — partial update (the third option most people forget)
app.patch("/users/:id", (req, res) =&gt; {
  users[req.params.id] = { ...users[req.params.id], ...req.body };
  res.json(users[req.params.id]);
});</code></pre>
<p><strong>Idempotency matters</strong> because networks are unreliable — clients retry failed requests. A retried POST might create duplicates; a retried PUT is safe. Well-designed APIs respect this difference.</p>
'''

ANSWERS[26] = r'''
<p>A static file server delivers unchanging assets (HTML, CSS, images, JavaScript bundles) directly from disk. Express has built-in middleware; the raw http module is only a few more lines.</p>
<pre><code>// Express — one-liner
const express = require("express");
const app = express();

app.use(express.static("public"));     // serves ./public/* at /*

// Now /public/style.css is available at http://localhost:3000/style.css
// and /public/index.html at http://localhost:3000/

// Mount at a prefix
app.use("/assets", express.static("public"));
// Now /public/style.css → http://localhost:3000/assets/style.css

// With options
app.use(express.static("public", {
  maxAge: "1d",                         // Cache-Control: max-age=86400
  etag: true,                           // ETag for conditional GET
  extensions: ["html", "htm"],          // /about → /about.html
}));

app.listen(3000);</code></pre>
<p><strong>Raw http version</strong> (educational — prefer Express in practice):</p>
<pre><code>const http = require("node:http"), fs = require("node:fs"), path = require("node:path");

http.createServer((req, res) =&gt; {
  const filePath = path.join(__dirname, "public", req.url === "/" ? "index.html" : req.url);
  const ext = path.extname(filePath);
  const mime = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript",
                 ".png": "image/png", ".jpg": "image/jpeg" }[ext] || "text/plain";

  fs.createReadStream(filePath)
    .on("open", () =&gt; res.writeHead(200, { "Content-Type": mime }))
    .on("error", () =&gt; res.writeHead(404).end())
    .pipe(res);
}).listen(3000);</code></pre>
<p><strong>Production caveat:</strong> in real deployments, you'd serve static files via a CDN (CloudFront, Cloudflare) or reverse proxy (Nginx, Caddy) — they're dramatically faster than Node and offload the work. Node's static server is perfect for development and small deployments.</p>
'''

ANSWERS[27] = r'''
<p>The <strong><code>path</code></strong> module provides utilities for working with file and directory paths — joining segments, resolving absolute paths, extracting extensions, all handling platform differences (slash vs backslash) correctly.</p>
<pre><code>const path = require("node:path");

// Joining — handles separators cross-platform
path.join("/users", "ada", "notes.txt");
// POSIX:   "/users/ada/notes.txt"
// Windows: "\\users\\ada\\notes.txt"

// Resolve — like cd — returns absolute path
path.resolve("src", "app.js");
// → "/current/working/dir/src/app.js"

// Extract parts
path.basename("/users/ada/notes.txt");          // "notes.txt"
path.basename("/users/ada/notes.txt", ".txt");  // "notes"
path.dirname("/users/ada/notes.txt");           // "/users/ada"
path.extname("notes.txt");                      // ".txt"

// parse / format — break into / rebuild from parts
path.parse("/users/ada/notes.txt");
// { root: "/", dir: "/users/ada", base: "notes.txt",
//   ext: ".txt", name: "notes" }

// Check if absolute
path.isAbsolute("/tmp");        // true on POSIX
path.isAbsolute("./src");       // false

// Special values
__dirname;                      // directory of current file (CommonJS)
__filename;                     // full path of current file
path.sep;                       // "/" on POSIX, "\\" on Windows</code></pre>
<p><strong>Always use <code>path.join</code> instead of string concatenation.</strong> Hard-coding <code>"src/" + filename</code> breaks on Windows and ignores edge cases like trailing slashes. In ESM, <code>__dirname</code> isn't available — use <code>import.meta.url</code>:</p>
<pre><code>import { fileURLToPath } from "node:url";
import { dirname } from "node:path";
const __dirname = dirname(fileURLToPath(import.meta.url));</code></pre>
'''

ANSWERS[28] = r'''
<p>Environment variables let you configure a Node app without editing code — different values in development, staging, and production. Access them via <code>process.env</code>.</p>
<pre><code>// Accessing env vars
const PORT = process.env.PORT || 3000;
const DB_URL = process.env.DATABASE_URL;
const NODE_ENV = process.env.NODE_ENV || "development";

if (!DB_URL) {
  console.error("DATABASE_URL is required");
  process.exit(1);
}

// Setting them when starting the app
// Linux/macOS:
//   PORT=8080 DATABASE_URL=postgres://... node app.js
// Windows PowerShell:
//   $env:PORT=8080; node app.js

// Using a .env file in development with dotenv
// npm install dotenv
require("dotenv").config();       // reads .env and populates process.env
// .env file:
//   PORT=3000
//   DATABASE_URL=postgres://localhost/mydb
//   JWT_SECRET=supersecret

// Node 20+ has native .env support — no dotenv needed!
// node --env-file=.env app.js</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Never commit <code>.env</code> to git.</strong> Add it to <code>.gitignore</code>. Commit a <code>.env.example</code> with placeholder values instead.</li>
  <li>Validate required vars on startup — fail fast with a clear error rather than crashing mysteriously later.</li>
  <li>All env-var values are strings. Convert: <code>parseInt(process.env.PORT, 10)</code>, <code>process.env.DEBUG === "true"</code>.</li>
  <li>For secrets in production, use a secret manager (AWS Secrets Manager, Vault, Doppler) rather than plain env vars in your deployment config.</li>
  <li>Library like <strong>envalid</strong> or <strong>zod</strong> can validate and type-convert env vars cleanly.</li>
</ul>
'''

ANSWERS[29] = r'''
<p><strong><code>process.env</code></strong> is a Node global that holds all environment variables as a plain object of string → string pairs. It's the standard way Node apps receive configuration from their runtime environment.</p>
<pre><code>// Read — every value is a string (or undefined)
console.log(process.env.PATH);          // the system PATH
console.log(process.env.HOME);          // user home directory
console.log(process.env.USER);          // current username

// Your own vars
const port = process.env.PORT || 3000;
const env = process.env.NODE_ENV;        // "production", "development", "test"

// Write — propagates to child processes spawned after the write
process.env.MY_VAR = "hello";
require("child_process").exec("echo $MY_VAR", (e, stdout) =&gt; {
  console.log(stdout);   // "hello"
});

// Inspect all
console.log(Object.keys(process.env));
console.log(process.env);</code></pre>
<p><strong>Important nuances:</strong></p>
<ul>
  <li><strong>All values are strings</strong> — even <code>process.env.PORT = 8080</code> stores <code>"8080"</code>. Always parse when you need numbers or booleans.</li>
  <li>Undefined variables return <code>undefined</code> (not an error).</li>
  <li>Values are set when the process starts; later shell changes don't affect a running process.</li>
  <li>On Windows, variable names are case-insensitive; on POSIX they're case-sensitive. Use uppercase by convention.</li>
  <li><code>NODE_ENV</code> is a <strong>convention</strong>, not a built-in Node feature — you decide what values mean what. Express and many libraries check it to enable production optimizations (e.g., view caching).</li>
</ul>
<pre><code>// Common pattern — validate required vars at startup
["DATABASE_URL", "JWT_SECRET", "STRIPE_KEY"].forEach(k =&gt; {
  if (!process.env[k]) throw new Error(`Missing env var: ${k}`);
});</code></pre>
'''

ANSWERS[30] = r'''
<p>JSON is the lingua franca of Node APIs and configs. The built-in <code>JSON</code> object handles parsing and serializing; Node adds conveniences for files and HTTP.</p>
<pre><code>// Parsing / stringifying
const obj = { name: "Ada", skills: ["js", "py"] };
const json = JSON.stringify(obj);                 // '{"name":"Ada","skills":["js","py"]}'
const parsed = JSON.parse(json);                  // back to object

// Pretty-print with indentation
JSON.stringify(obj, null, 2);
// {
//   "name": "Ada",
//   "skills": ["js", "py"]
// }

// Reading a JSON file
const fsp = require("node:fs/promises");
const config = JSON.parse(await fsp.readFile("config.json", "utf-8"));

// require() can load JSON files directly (CommonJS)
const pkg = require("./package.json");

// Writing JSON
await fsp.writeFile("out.json", JSON.stringify(data, null, 2));

// Sending JSON in HTTP responses — Express
app.get("/api/users", (req, res) =&gt; {
  res.json({ users: [...] });                     // sets Content-Type automatically
});

// Parsing JSON request bodies
app.use(express.json());
app.post("/api/user", (req, res) =&gt; {
  console.log(req.body);                          // already an object
});</code></pre>
<p><strong>Gotchas:</strong></p>
<ul>
  <li><strong>Always wrap <code>JSON.parse</code> in try/catch</strong> — invalid JSON throws synchronously. User input or network responses can be malformed.</li>
  <li><code>JSON.stringify</code> drops <code>undefined</code>, functions, symbols, and throws on circular references (<code>a.self = a</code>). Use a replacer function or <code>util.inspect</code> for logs.</li>
  <li><code>Date</code> objects serialize to ISO strings but don't auto-revive on parse — you need a reviver function or a schema library.</li>
  <li>For huge JSON files, use a streaming parser like <strong>stream-json</strong> or <strong>JSONStream</strong> — <code>JSON.parse</code> loads everything into memory.</li>
</ul>
'''

ANSWERS[31] = r'''
<p><code>require</code> belongs to <strong>CommonJS (CJS)</strong> — Node's original module system. <code>import</code> belongs to <strong>ES Modules (ESM)</strong> — the JavaScript standard shared with browsers.</p>
<table>
  <thead><tr><th>Aspect</th><th><code>require</code> (CJS)</th><th><code>import</code> (ESM)</th></tr></thead>
  <tbody>
    <tr><td>Syntax</td><td><code>const x = require("m")</code></td><td><code>import x from "m"</code></td></tr>
    <tr><td>Loading</td><td>Synchronous</td><td>Asynchronous / static</td></tr>
    <tr><td>When resolved</td><td>At call-site (runtime)</td><td>Hoisted — before any code runs</td></tr>
    <tr><td>Can be conditional?</td><td>Yes — inside <code>if</code> blocks</td><td>Static only (use dynamic <code>import()</code> for conditions)</td></tr>
    <tr><td>Enable by</td><td>Default</td><td>Set <code>"type": "module"</code> or use <code>.mjs</code></td></tr>
    <tr><td>Tree-shaking</td><td>No — whole module loads</td><td>Yes — bundlers drop unused exports</td></tr>
    <tr><td>Browser support</td><td>Node-only</td><td>Native in browsers + Node</td></tr>
    <tr><td>Top-level await</td><td>No</td><td>Yes</td></tr>
  </tbody>
</table>
<pre><code>// CommonJS (require)
const fs = require("node:fs");
const { readFile } = require("node:fs/promises");
module.exports = { add, subtract };

// ES Modules (import)
import fs from "node:fs";
import { readFile } from "node:fs/promises";
export { add, subtract };
export default class User {};

// Dynamic import — works in BOTH CJS and ESM
const { something } = await import("./module.js");</code></pre>
<p><strong>Which to use?</strong> New projects should use ESM — it's the standard, allows tree-shaking, and matches browser code. Older Node codebases are often stuck on CJS. The two interoperate: ESM can import CJS modules; CJS needs dynamic <code>import()</code> to load ESM.</p>
'''

ANSWERS[32] = r'''
<p>Node runs on a single thread — one process uses one CPU core. The <strong><code>cluster</code></strong> module forks multiple worker processes that share a port, letting you take advantage of all cores on a multi-core machine.</p>
<pre><code>const cluster = require("node:cluster");
const os = require("node:os");
const http = require("node:http");

if (cluster.isPrimary) {
  // Master process — fork one worker per CPU core
  const numCPUs = os.cpus().length;
  console.log(`Starting ${numCPUs} workers (pid ${process.pid})`);

  for (let i = 0; i &lt; numCPUs; i++) {
    cluster.fork();
  }

  // Restart workers that crash — keep cluster at full strength
  cluster.on("exit", (worker, code) =&gt; {
    console.log(`Worker ${worker.process.pid} died; restarting`);
    cluster.fork();
  });
} else {
  // Worker process — each runs the actual server
  http.createServer((req, res) =&gt; {
    res.end(`Handled by worker ${process.pid}`);
  }).listen(3000);
}</code></pre>
<p><strong>How it works:</strong> workers share a single listening port — the OS (or Node's round-robin scheduler on non-Windows) balances incoming connections among them. Each worker is a full Node process with its own memory and event loop; they don't share state.</p>
<p><strong>When to use cluster:</strong></p>
<ul>
  <li>CPU-bound workloads (multiple cores help).</li>
  <li>Taking advantage of a beefy multi-core server.</li>
  <li>Isolating crashes — one worker dying doesn't take down the others.</li>
</ul>
<p><strong>Modern alternative:</strong> most deployments now use a process manager like <strong>PM2</strong> (<code>pm2 start app.js -i max</code>) which handles clustering + restarts + logging + zero-downtime reloads — saves you writing the <code>cluster.fork()</code> scaffolding yourself. For CPU-heavy work within one request, prefer <code>worker_threads</code>.</p>
'''

ANSWERS[33] = r'''
<p>The <strong><code>child_process</code></strong> module lets your Node app spawn and communicate with other programs — anything from running <code>ls</code> to invoking a Python script to calling <code>ffmpeg</code> for video transcoding.</p>
<p>Four main APIs, each suited to different jobs:</p>
<ul>
  <li><strong><code>exec(cmd, cb)</code></strong> — run a shell command; buffers output in memory. Simple but unsafe with user input.</li>
  <li><strong><code>execFile(file, args, cb)</code></strong> — like exec, but runs a binary directly (no shell). Safer.</li>
  <li><strong><code>spawn(cmd, args)</code></strong> — streams stdout/stderr; good for long-running or output-heavy processes.</li>
  <li><strong><code>fork(modulePath)</code></strong> — spawn a new Node process with IPC; lets parent and child exchange messages.</li>
</ul>
<pre><code>const { exec, spawn, fork } = require("node:child_process");

// exec — simple commands; captures entire output
exec("ls -la", (err, stdout, stderr) =&gt; {
  if (err) return console.error(err);
  console.log(stdout);
});

// spawn — stream output (use for long/large output)
const ffmpeg = spawn("ffmpeg", ["-i", "input.mp4", "output.webm"]);
ffmpeg.stdout.on("data", data =&gt; console.log(`out: ${data}`));
ffmpeg.stderr.on("data", data =&gt; console.log(`err: ${data}`));
ffmpeg.on("close", code =&gt; console.log(`exited with ${code}`));

// fork — Node child with bidirectional messages
const child = fork("./worker.js");
child.send({ task: "process", payload: data });
child.on("message", result =&gt; console.log(result));</code></pre>
<p><strong>Security warning:</strong> never pass unsanitized user input to <code>exec</code> — it interprets shell metacharacters (<code>;</code>, <code>|</code>, <code>&amp;&amp;</code>) and enables command injection. Prefer <code>execFile</code> or <code>spawn</code> with an args array. Use cases: invoking CLI tools, transcoding media, running scripts in other languages, isolating risky work in a subprocess.</p>
'''

ANSWERS[34] = r'''
<p>Choose the API that matches what you need: quick output → <code>exec</code>; streaming → <code>spawn</code>; Node-to-Node with IPC → <code>fork</code>.</p>
<pre><code>const { spawn } = require("node:child_process");

// Basic spawn — run a command, stream its output
const ls = spawn("ls", ["-la", "/tmp"]);

ls.stdout.on("data", (chunk) =&gt; {
  process.stdout.write(chunk);             // chunk is a Buffer
});

ls.stderr.on("data", (chunk) =&gt; {
  process.stderr.write(chunk);
});

ls.on("close", (code) =&gt; {
  console.log(`child exited with code ${code}`);
});

ls.on("error", (err) =&gt; {
  console.error("failed to start:", err);
});

// Write to the child's stdin
const grep = spawn("grep", ["node"]);
grep.stdin.write("hello\nnode is fun\ngoodbye\n");
grep.stdin.end();
grep.stdout.on("data", d =&gt; console.log(d.toString()));

// Pipe one child's output to another (like a shell pipeline)
const cat = spawn("cat", ["big.log"]);
const gzip = spawn("gzip");
cat.stdout.pipe(gzip.stdin);
gzip.stdout.pipe(require("node:fs").createWriteStream("big.log.gz"));

// Promise-based — easier with util.promisify
const { promisify } = require("node:util");
const exec = promisify(require("node:child_process").exec);
const { stdout } = await exec("node --version");
console.log(stdout.trim());</code></pre>
<p><strong>Options worth knowing:</strong> <code>{ cwd: "/tmp" }</code> sets the working directory; <code>{ env: {...} }</code> provides environment variables; <code>{ shell: true }</code> runs through a shell (enables wildcards but risks injection); <code>{ timeout: 5000 }</code> kills after N ms. Always listen for the <code>"error"</code> event too — failure to spawn is separate from a non-zero exit code.</p>
'''

ANSWERS[35] = r'''
<p>Both run external commands, but they differ in how they handle output and shell interpretation — pick based on the size and nature of the command.</p>
<table>
  <thead><tr><th>Aspect</th><th><code>exec</code></th><th><code>spawn</code></th></tr></thead>
  <tbody>
    <tr><td>Shell?</td><td>Runs in a shell (<code>/bin/sh</code> or cmd.exe)</td><td>No shell — runs binary directly</td></tr>
    <tr><td>Output delivery</td><td>Buffered — full output at once</td><td>Streamed — data events as it arrives</td></tr>
    <tr><td>Max output</td><td>Limited (default 1 MB, <code>maxBuffer</code> option)</td><td>Unlimited</td></tr>
    <tr><td>API style</td><td>Callback — <code>(err, stdout, stderr)</code></td><td>Event emitter + streams</td></tr>
    <tr><td>Supports shell features?</td><td>Yes — pipes, redirects, globbing</td><td>No (unless <code>shell: true</code>)</td></tr>
    <tr><td>Security</td><td>Vulnerable to shell injection with user input</td><td>Safer — args are passed literally</td></tr>
    <tr><td>Best for</td><td>Short commands with small output</td><td>Long-running or output-heavy commands</td></tr>
  </tbody>
</table>
<pre><code>// exec — quick &amp; easy, but watch the buffer limit
const { exec } = require("node:child_process");
exec("git log --oneline -10", (err, stdout, stderr) =&gt; {
  console.log(stdout);      // all at once
});

// spawn — better for long output or when you need streaming
const { spawn } = require("node:child_process");
const find = spawn("find", ["/", "-name", "*.log"]);
find.stdout.on("data", chunk =&gt; {
  // process each chunk as it arrives — memory stays flat
});

// Good rule of thumb:
//   Output &lt; 1 MB, one-shot → exec
//   Output &gt; 1 MB, progressive → spawn
//   User input in args        → spawn (or execFile)</code></pre>
<p><strong>Safe middle ground:</strong> <code>execFile</code> — buffered like <code>exec</code> but without shell interpretation. Great for CLIs with trusted binary + user-supplied args.</p>
'''

ANSWERS[36] = r'''
<p>Node offers several ways to make HTTP requests. For new code, the built-in <code>fetch()</code> (added in Node 18) is the cleanest option.</p>
<pre><code>// Built-in fetch() — Node 18+, matches the browser API
const res = await fetch("https://api.example.com/users/1");
if (!res.ok) throw new Error(`HTTP ${res.status}`);
const user = await res.json();

// POST with JSON
const created = await fetch("https://api.example.com/users", {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
  body: JSON.stringify({ name: "Ada" }),
});

// Timeout via AbortSignal
const res2 = await fetch(url, { signal: AbortSignal.timeout(5000) });

// Raw http/https modules — verbose but no dependencies
const https = require("node:https");
https.get("https://api.example.com/data", (res) =&gt; {
  let body = "";
  res.on("data", chunk =&gt; body += chunk);
  res.on("end", () =&gt; console.log(JSON.parse(body)));
}).on("error", console.error);

// Popular third-party libraries
// axios — feature-rich, interceptors, automatic JSON
const axios = require("axios");
const { data } = await axios.get("https://api.example.com/users");
await axios.post("https://api.example.com/users", { name: "Ada" });

// undici — the modern HTTP client that powers Node's fetch
const { request } = require("undici");
const { statusCode, body } = await request("https://api.example.com");

// got — also popular
const got = (await import("got")).default;
const data2 = await got("https://api.example.com/users").json();</code></pre>
<p><strong>Which to use?</strong> Greenfield projects in 2026: use the built-in <code>fetch()</code>. For bigger codebases: <strong>axios</strong> (mature, great DX) or <strong>undici</strong> (fastest). Always set timeouts — requests without timeouts can hang forever if the server goes dark. For retries, use <code>got</code> or add an interceptor.</p>
'''

ANSWERS[37] = r'''
<p>The <strong><code>http</code></strong> module is Node's low-level HTTP implementation, covering both server and client sides. Every web framework (Express, Fastify, Koa) is built on top of it.</p>
<p><strong>Server-side primitives:</strong></p>
<ul>
  <li><code>http.createServer(callback)</code> — creates a server; callback receives <code>(req, res)</code>.</li>
  <li>The <code>req</code> is an <code>IncomingMessage</code> — a readable stream with headers, method, URL.</li>
  <li>The <code>res</code> is a <code>ServerResponse</code> — a writable stream where you set status/headers and write body.</li>
</ul>
<p><strong>Client-side primitives:</strong></p>
<ul>
  <li><code>http.request(options, callback)</code> — make an outbound request; flexible but verbose.</li>
  <li><code>http.get(url, callback)</code> — shortcut for GET.</li>
</ul>
<pre><code>const http = require("node:http");

// SERVER
const server = http.createServer((req, res) =&gt; {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("hello\n");
});
server.listen(3000);

// Lower-level events
server.on("request",    (req, res) =&gt; { /* same as callback above */ });
server.on("connection", (socket) =&gt; { /* new TCP connection */ });
server.on("close",      () =&gt; { /* server shutting down */ });

// CLIENT — modern code should prefer fetch() instead
const req = http.request({
  hostname: "example.com",
  port: 80,
  path: "/api/users",
  method: "POST",
  headers: { "Content-Type": "application/json" },
}, (res) =&gt; {
  console.log("status:", res.statusCode);
  res.on("data", chunk =&gt; console.log(chunk.toString()));
});
req.on("error", console.error);
req.write(JSON.stringify({ name: "Ada" }));
req.end();</code></pre>
<p><strong>Companion module:</strong> <code>https</code> — identical API but over TLS. For HTTPS client calls you must use <code>https.request</code>, not <code>http.request</code>. The <code>http2</code> module supports HTTP/2 (multiplexing, header compression, server push).</p>
'''

ANSWERS[38] = r'''
<p>The <strong><code>https</code></strong> module is the TLS-secured counterpart to <code>http</code>. Same API, encrypted transport. Use it any time you're transmitting credentials, tokens, or any data that shouldn't be readable on the wire.</p>
<pre><code>const https = require("node:https");
const fs = require("node:fs");

// HTTPS SERVER — needs a certificate + private key
const options = {
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.cert"),
};

https.createServer(options, (req, res) =&gt; {
  res.writeHead(200);
  res.end("Secure hello!");
}).listen(443);

// Development self-signed cert (only for local testing)
// openssl req -x509 -newkey rsa:2048 -nodes \
//   -keyout server.key -out server.cert -days 365 -subj "/CN=localhost"

// HTTPS CLIENT — same as http.request, different module
https.get("https://api.example.com/users", (res) =&gt; {
  let data = "";
  res.on("data", chunk =&gt; data += chunk);
  res.on("end", () =&gt; console.log(JSON.parse(data)));
});

// Modern alternative — fetch() handles http and https transparently
const res = await fetch("https://api.example.com/users");
const users = await res.json();</code></pre>
<p><strong>Production reality:</strong> you almost never run <code>https.createServer</code> directly in production. Instead:</p>
<ul>
  <li>Use <strong>Let's Encrypt</strong> (via <strong>certbot</strong> or <strong>greenlock</strong>) for free certificates.</li>
  <li>Terminate TLS at a <strong>reverse proxy</strong> — Nginx, Caddy, HAProxy, or a managed service like AWS ALB / Cloudflare. Node serves plain HTTP internally; the proxy handles certificates, renewal, and HTTP/2.</li>
  <li>This separation means Node doesn't need certificate files, reloading on renewal, or OCSP management.</li>
</ul>
<p><strong>Certificate pinning / mutual TLS:</strong> pass <code>ca</code> (trusted root) or <code>cert</code> + <code>key</code> options on the client side for mTLS — common in service-to-service auth.</p>
'''

ANSWERS[39] = r'''
<p>The <strong><code>crypto</code></strong> module exposes cryptographic primitives — hashing, HMAC, symmetric/asymmetric encryption, key derivation, random bytes, and certificate handling. It wraps OpenSSL, so it's battle-tested.</p>
<pre><code>const crypto = require("node:crypto");

// Secure random bytes — for tokens, IVs, salts
const token = crypto.randomBytes(32).toString("hex");
const uuid = crypto.randomUUID();         // RFC 4122 v4 UUID

// Hash — one-way digest (SHA-256, SHA-512)
const hash = crypto.createHash("sha256").update("hello world").digest("hex");

// HMAC — hash with a shared secret (for signing cookies, webhooks)
const mac = crypto.createHmac("sha256", "secret-key").update("payload").digest("hex");

// Constant-time comparison — prevents timing attacks
crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));

// Symmetric encryption — AES-256-GCM (authenticated)
const key = crypto.randomBytes(32);
const iv = crypto.randomBytes(12);
const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
const encrypted = Buffer.concat([cipher.update("secret"), cipher.final()]);
const authTag = cipher.getAuthTag();     // keep this too — verifies integrity

// Asymmetric — generate an RSA keypair
const { publicKey, privateKey } = crypto.generateKeyPairSync("rsa", {
  modulusLength: 2048,
});

// Password hashing — use scrypt (slow by design)
const salt = crypto.randomBytes(16);
const derivedKey = crypto.scryptSync("user-password", salt, 64);

// For cleaner password hashing, prefer bcrypt or argon2 libraries</code></pre>
<p><strong>When to use <code>crypto</code> directly:</strong> low-level primitives, signing tokens, HMAC validation of webhooks (Stripe, GitHub), encrypting data at rest. For passwords, prefer <strong>bcrypt</strong> or <strong>argon2</strong> libraries — they're easier to use safely and include sensible defaults. Never roll your own crypto protocols; stick to established ones (TLS, JWT, libsodium bindings).</p>
'''

ANSWERS[40] = r'''
<p><strong>Never store passwords in plaintext.</strong> Never use fast hashes like MD5, SHA-1, or plain SHA-256 for passwords — they're designed for speed, which makes brute-force attacks cheap. Use a slow, memory-hard hash: <strong>bcrypt</strong>, <strong>argon2</strong>, or Node's built-in <strong>scrypt</strong>.</p>
<pre><code>// OPTION 1 — bcrypt (the most common choice)
const bcrypt = require("bcrypt");
const SALT_ROUNDS = 12;                  // higher = slower = more secure

// Hash on registration
const hashed = await bcrypt.hash("user-password", SALT_ROUNDS);
// hashed = "$2b$12$abc...xyz"   — includes algorithm, rounds, salt, hash

// Verify on login
const ok = await bcrypt.compare("user-password", hashed);    // true
// Note: compare() handles timing-safe comparison for you

// OPTION 2 — argon2 (winner of the Password Hashing Competition)
const argon2 = require("argon2");
const hash = await argon2.hash("user-password", { type: argon2.argon2id });
const valid = await argon2.verify(hash, "user-password");

// OPTION 3 — built-in scrypt (no dependencies)
const crypto = require("node:crypto");
const { promisify } = require("node:util");
const scrypt = promisify(crypto.scrypt);

async function hashPassword(password) {
  const salt = crypto.randomBytes(16);
  const derivedKey = await scrypt(password, salt, 64);
  return `${salt.toString("hex")}:${derivedKey.toString("hex")}`;
}

async function verify(password, stored) {
  const [saltHex, keyHex] = stored.split(":");
  const salt = Buffer.from(saltHex, "hex");
  const derivedKey = await scrypt(password, salt, 64);
  return crypto.timingSafeEqual(Buffer.from(keyHex, "hex"), derivedKey);
}</code></pre>
<p><strong>Key rules:</strong></p>
<ul>
  <li>Use a <strong>unique random salt per password</strong> — bcrypt/argon2/scrypt handle this for you.</li>
  <li>Tune the work factor so hashing takes ~100 ms — fast enough for UX, slow enough to make brute-force painful. Re-tune every few years as hardware improves.</li>
  <li>Never log passwords, even hashed ones.</li>
  <li>Migrate old hashes when a user next logs in — gives you a path to upgrade algorithms.</li>
</ul>
'''

ANSWERS[41] = r'''
<p>The <strong><code>util</code></strong> module is a grab bag of utility functions — type checking, debugging, formatting, and Promise/callback interop — that Node ships internally for its own code and exposes for yours.</p>
<pre><code>const util = require("node:util");

// promisify — turn a callback-style function into a Promise-returning one
const fs = require("node:fs");
const readFile = util.promisify(fs.readFile);
const data = await readFile("x.txt", "utf-8");

// callbackify — the reverse (rarely needed)
const asyncFn = async () =&gt; "hello";
const cbFn = util.callbackify(asyncFn);
cbFn((err, result) =&gt; console.log(result));

// format — like printf
util.format("Hello %s, you are %d years old", "Ada", 36);
// "Hello Ada, you are 36 years old"

// inspect — stringify objects for logging (deeper than JSON.stringify)
const obj = { a: 1, b: { c: 2 } };
console.log(util.inspect(obj, { depth: null, colors: true }));

// types — runtime type checking
util.types.isDate(new Date());          // true
util.types.isRegExp(/abc/);             // true
util.types.isPromise(Promise.resolve()); // true
util.types.isAsyncFunction(async () =&gt; {}); // true

// deprecate — mark a function as deprecated
const old = util.deprecate(
  function() { /* ... */ },
  "oldFn() is deprecated — use newFn() instead"
);

// debuglog — conditional debug output (set NODE_DEBUG=myapp to enable)
const debug = util.debuglog("myapp");
debug("computed result: %o", result);</code></pre>
<p><strong>Most-used utilities:</strong> <code>promisify</code> (invaluable when dealing with legacy callback APIs), <code>inspect</code> (essential for debugging complex objects), and <code>types.*</code> (the only reliable way to check some types — e.g., <code>instanceof Date</code> fails across realms, but <code>util.types.isDate</code> works).</p>
'''

ANSWERS[42] = r'''
<p><code>util.format()</code> is Node's <code>printf</code>-style string formatter. It takes a format string and arguments, returning a formatted string — useful for log messages, error templates, and anywhere you want cleaner concatenation than <code>+</code> or template literals (for log-style repetition).</p>
<pre><code>const util = require("node:util");

// Format specifiers
util.format("Hello %s", "Ada");                          // "Hello Ada"
util.format("Count: %d", 42);                            // "Count: 42"
util.format("Value: %i", 3.9);                           // "Value: 3" (integer)
util.format("Value: %f", 3.14159);                       // "Value: 3.14159"
util.format("Object: %o", { a: 1 });                     // with showHidden etc.
util.format("Object: %O", { a: 1 });                     // without hidden
util.format("JSON: %j", { name: "Ada" });                // "JSON: {"name":"Ada"}"
util.format("Literal: %%");                              // "Literal: %"

// Specifiers in order
util.format("%s is %d years old", "Ada", 36);
// "Ada is 36 years old"

// Extra arguments get appended with a space
util.format("Hello", "Ada", 36);
// "Hello Ada 36"

// Objects without a specifier get inspected
util.format("User:", { name: "Ada" });
// "User: { name: 'Ada' }"</code></pre>
<p><strong>Where it shows up:</strong> internally, <code>console.log</code> uses <code>util.format</code> — that's why <code>console.log("name: %s", name)</code> works. Most logging libraries (<code>winston</code>, <code>pino</code>, <code>debug</code>) also use it under the hood.</p>
<p><strong>Format specifiers cheat sheet:</strong> <code>%s</code> string, <code>%d</code>/<code>%i</code> number/integer, <code>%f</code> float, <code>%j</code> JSON, <code>%o</code>/<code>%O</code> inspect object, <code>%c</code> CSS (browsers only), <code>%%</code> literal <code>%</code>.</p>
<p>For most modern code, template literals (<code>`Hello ${name}`</code>) are cleaner. Use <code>util.format</code> when you already have a format string separately from the values (config-driven messages) or inside logging pipelines where format-string support is a common feature.</p>
'''

ANSWERS[43] = r'''
<p>The <strong><code>dns</code></strong> module provides Domain Name System lookups — converting hostnames to IP addresses and querying various DNS record types (A, AAAA, MX, TXT, CNAME, SRV).</p>
<pre><code>const dns = require("node:dns");
const dnsp = require("node:dns/promises");

// Basic hostname resolution (uses OS resolver — usually what you want)
const address = await dnsp.lookup("example.com");
// { address: "93.184.216.34", family: 4 }

const addresses = await dnsp.lookup("example.com", { all: true });
// [{ address: "93.184.216.34", family: 4 }, ...]

// Direct DNS queries (bypasses OS resolver, uses DNS servers directly)
const a = await dnsp.resolve4("example.com");        // IPv4 addresses
const aaaa = await dnsp.resolve6("example.com");     // IPv6 addresses
const mx = await dnsp.resolveMx("example.com");      // mail exchange records
const txt = await dnsp.resolveTxt("example.com");    // TXT records (SPF, verification)
const ns = await dnsp.resolveNs("example.com");      // name servers
const srv = await dnsp.resolveSrv("_http._tcp.example.com"); // SRV records

// Reverse lookup — IP to hostname
const names = await dnsp.reverse("8.8.8.8");
// ["dns.google"]

// Set custom DNS servers
dns.setServers(["8.8.8.8", "1.1.1.1"]);</code></pre>
<p><strong>When you'd use it:</strong></p>
<ul>
  <li><strong>Email validation</strong> — look up MX records to verify a domain can receive mail.</li>
  <li><strong>Domain verification</strong> — check a TXT record for a token you provided (like <code>_acme-challenge</code> for Let's Encrypt, or SaaS domain-ownership checks).</li>
  <li><strong>Service discovery</strong> — SRV records for Kubernetes service lookup.</li>
  <li><strong>Debugging</strong> — troubleshoot connectivity issues programmatically.</li>
</ul>
<p><strong><code>lookup</code> vs <code>resolve*</code>:</strong> <code>lookup</code> uses <code>getaddrinfo(3)</code> (same as browsers, respects /etc/hosts); <code>resolve*</code> makes direct DNS queries. For most application code, use <code>lookup</code> — it's consistent with what the OS does.</p>
'''

ANSWERS[44] = r'''
<p>Two APIs for DNS lookups: <code>dns.lookup</code> (goes through the OS resolver, like the browser does) and <code>dns.resolve*</code> (direct DNS queries, bypassing <code>/etc/hosts</code>). Both have callback and Promise variants.</p>
<pre><code>const dns = require("node:dns");
const { promises: dnsp } = require("node:dns");

// lookup — OS resolver; consistent with how other apps resolve
dns.lookup("example.com", (err, address, family) =&gt; {
  console.log(address, family);          // "93.184.216.34", 4
});

// Promise + all addresses
const hits = await dnsp.lookup("google.com", { all: true });
for (const h of hits) console.log(h.address, h.family);

// IPv4 only / IPv6 only
await dnsp.lookup("example.com", { family: 4 });
await dnsp.lookup("example.com", { family: 6 });

// resolve — direct DNS query
dns.resolve4("example.com", (err, ips) =&gt; {
  console.log(ips);                       // ["93.184.216.34"]
});

// Multiple record types
const mxRecords = await dnsp.resolveMx("gmail.com");
// [{ exchange: "alt1.gmail-smtp-in.l.google.com", priority: 10 }, ...]

const spf = await dnsp.resolveTxt("gmail.com");
// [["v=spf1 redirect=_spf.google.com"]]

// Reverse lookup — PTR records
const hostnames = await dnsp.reverse("8.8.8.8");     // ["dns.google"]

// Advanced — use a specific resolver
const resolver = new dns.promises.Resolver();
resolver.setServers(["1.1.1.1"]);           // Cloudflare DNS
const ips = await resolver.resolve4("example.com");</code></pre>
<p><strong>Practical notes:</strong> DNS lookups can fail intermittently — wrap them in retries with backoff. Results are cached by the OS (or by <code>dns.resolve</code> with manual caching), so a stale record may persist briefly after a change. For HTTP requests, you don't usually call <code>dns</code> yourself — <code>http.request</code>/<code>fetch</code> handle resolution internally.</p>
'''

ANSWERS[45] = r'''
<p>The <strong><code>os</code></strong> module exposes operating system metadata — CPU info, memory, uptime, network interfaces, temp directory. Handy for diagnostics, monitoring, and writing cross-platform code.</p>
<pre><code>const os = require("node:os");

// System identity
os.platform();           // "linux", "darwin", "win32"
os.type();               // "Linux", "Darwin", "Windows_NT"
os.release();            // OS version string
os.arch();               // "x64", "arm64"
os.hostname();           // machine name
os.version();            // kernel version (OS-specific)

// Users
os.userInfo();           // { username, homedir, shell, uid, gid }
os.homedir();            // /home/ada
os.tmpdir();             // /tmp  (or OS-specific temp dir)

// CPU info
os.cpus();
// [{ model, speed, times: { user, nice, sys, idle, irq } }, ...]
os.cpus().length;        // number of logical cores

// Memory (bytes)
os.totalmem();           // total RAM
os.freemem();            // currently free

// Load average (Unix — 1/5/15 minute averages; returns [0,0,0] on Windows)
os.loadavg();

// Uptime (seconds)
os.uptime();

// Network interfaces
os.networkInterfaces();
// { eth0: [{ address, netmask, family, mac, internal }], lo: [...] }

// Constants
os.EOL;                  // "\n" on POSIX, "\r\n" on Windows
os.constants.signals.SIGKILL;   // 9</code></pre>
<p><strong>Common uses:</strong></p>
<ul>
  <li><strong>Cross-platform code</strong> — check <code>os.platform()</code> to branch on OS-specific behavior.</li>
  <li><strong>Scaling decisions</strong> — <code>os.cpus().length</code> for cluster worker count.</li>
  <li><strong>Health endpoints</strong> — exposing <code>os.freemem()</code> / <code>os.loadavg()</code> for dashboards.</li>
  <li><strong>Temp files</strong> — use <code>os.tmpdir()</code> instead of hardcoding <code>/tmp</code>.</li>
</ul>
<p>For more detailed system monitoring (disk, per-process CPU), look at <code>node-os-utils</code> or <code>systeminformation</code> packages.</p>
'''

ANSWERS[46] = r'''
<p>The <code>os</code> module covers most of what you'd want about the host system. Here's how to read typical bits of system info:</p>
<pre><code>const os = require("node:os");

// One-shot system snapshot
console.log({
  platform: os.platform(),                          // "linux"
  arch:     os.arch(),                              // "x64"
  host:     os.hostname(),
  uptime:   `${Math.floor(os.uptime() / 3600)} hours`,
  cores:    os.cpus().length,
  memory:   `${(os.totalmem() / 1e9).toFixed(1)} GB`,
  freeMem:  `${(os.freemem()  / 1e9).toFixed(1)} GB`,
  user:     os.userInfo().username,
  tempDir:  os.tmpdir(),
});

// Memory usage as percentage
const memUsed = (os.totalmem() - os.freemem()) / os.totalmem();
console.log(`Memory: ${(memUsed * 100).toFixed(1)}% used`);

// CPU usage requires sampling over time (single call is useless)
function cpuSnapshot() {
  return os.cpus().map(c =&gt; {
    const total = Object.values(c.times).reduce((a, b) =&gt; a + b);
    return { idle: c.times.idle, total };
  });
}

async function cpuUsage() {
  const a = cpuSnapshot();
  await new Promise(r =&gt; setTimeout(r, 1000));
  const b = cpuSnapshot();
  return a.map((snap, i) =&gt; {
    const idleDiff  = b[i].idle  - snap.idle;
    const totalDiff = b[i].total - snap.total;
    return 1 - idleDiff / totalDiff;
  });
}
console.log(await cpuUsage());    // [0.15, 0.23, ...] per core

// Find the external IPv4 address
const ifaces = os.networkInterfaces();
for (const [name, addrs] of Object.entries(ifaces)) {
  for (const a of addrs) {
    if (a.family === "IPv4" &amp;&amp; !a.internal) console.log(name, a.address);
  }
}

// Process-specific (not os, but related)
process.memoryUsage();    // { rss, heapTotal, heapUsed, external, arrayBuffers }
process.cpuUsage();       // { user, system } in microseconds
process.uptime();         // Node process uptime (not OS)</code></pre>
<p><strong>Caveats:</strong> <code>os.loadavg()</code> returns <code>[0, 0, 0]</code> on Windows (Windows has no equivalent metric). For accurate per-process metrics inside containers, <code>os.*</code> reports the host — use <code>/sys/fs/cgroup</code> or <code>process.*</code> methods instead.</p>
'''

ANSWERS[47] = r'''
<p>The <strong><code>v8</code></strong> module exposes APIs specific to V8, the JavaScript engine that powers Node. Mostly used for diagnostics (heap snapshots, GC statistics) and low-level tuning — not everyday code.</p>
<pre><code>const v8 = require("node:v8");

// Heap statistics — what V8's memory looks like right now
const stats = v8.getHeapStatistics();
/*
{
  total_heap_size: 10485760,
  total_heap_size_executable: 524288,
  total_physical_size: 8912896,
  total_available_size: 2195222016,
  used_heap_size: 5328984,
  heap_size_limit: 2197815296,           // max heap (≈ --max-old-space-size)
  malloced_memory: 8192,
  peak_malloced_memory: 1196592,
  does_zap_garbage: 0,
  number_of_native_contexts: 1,
  number_of_detached_contexts: 0,
}
*/

// Per-space breakdown (new space, old space, code space, etc.)
v8.getHeapSpaceStatistics();

// Write a heap snapshot — load in Chrome DevTools to analyze leaks
v8.writeHeapSnapshot("/tmp/heap.heapsnapshot");

// Version info
v8.getHeapCodeStatistics();     // { code_and_metadata_size, bytecode_and_metadata_size, ... }

// Serialize/deserialize arbitrary JS values (including Maps, Sets, typed arrays)
// — much richer than JSON, same algorithm as structuredClone()
const buf = v8.serialize({ date: new Date(), set: new Set([1, 2]) });
const restored = v8.deserialize(buf);

// Set flags programmatically (rarely used — prefer command line)
v8.setFlagsFromString("--max-old-space-size=4096");
// Reset cached flag state — not for production</code></pre>
<p><strong>When you'd reach for this module:</strong></p>
<ul>
  <li><strong>Memory leak debugging</strong> — writeHeapSnapshot + Chrome DevTools reveals which objects are retaining memory.</li>
  <li><strong>Monitoring dashboards</strong> — expose <code>getHeapStatistics()</code> via a health endpoint to see memory pressure in real time.</li>
  <li><strong>Custom serialization</strong> — <code>v8.serialize</code> handles types JSON can't (Dates, Maps, Sets, typed arrays, circular refs).</li>
</ul>
<p>You don't typically use this module in business logic — it's a diagnostic / infrastructure tool.</p>
'''

ANSWERS[48] = r'''
<p>Heap statistics tell you how much memory V8 is using and how close you are to the limit. Essential for detecting memory leaks and right-sizing the <code>--max-old-space-size</code> flag.</p>
<pre><code>const v8 = require("node:v8");

// Overall heap stats
const s = v8.getHeapStatistics();
const MB = (n) =&gt; (n / 1024 / 1024).toFixed(1);

console.log(`Heap used:  ${MB(s.used_heap_size)} MB`);
console.log(`Heap total: ${MB(s.total_heap_size)} MB`);
console.log(`Heap limit: ${MB(s.heap_size_limit)} MB`);
console.log(`Usage:      ${((s.used_heap_size / s.heap_size_limit) * 100).toFixed(1)}%`);

// Per-space breakdown (V8 divides heap into regions)
for (const space of v8.getHeapSpaceStatistics()) {
  console.log(`${space.space_name}: used ${MB(space.space_used_size)} MB `
            + `/ ${MB(space.space_size)} MB`);
}

// Process-level metrics (always available, not V8-specific)
const m = process.memoryUsage();
console.log({
  rss:         MB(m.rss) + " MB",          // resident set size (all OS memory)
  heapTotal:   MB(m.heapTotal) + " MB",    // V8's heap allocated
  heapUsed:    MB(m.heapUsed) + " MB",     // V8's heap used
  external:    MB(m.external) + " MB",     // C++ memory outside V8 heap
  arrayBuffers: MB(m.arrayBuffers) + " MB",
});

// Force a GC for testing — run node --expose-gc
if (global.gc) global.gc();

// Monitor over time in a server
setInterval(() =&gt; {
  const used = process.memoryUsage().heapUsed / 1024 / 1024;
  if (used &gt; 500) console.warn(`High memory: ${used.toFixed(0)} MB`);
}, 60_000);</code></pre>
<p><strong>What to watch for:</strong></p>
<ul>
  <li><strong>Steady upward trend</strong> in <code>heapUsed</code> over time with no plateau = probable memory leak. Take heap snapshots and compare.</li>
  <li><strong>Hit <code>heap_size_limit</code></strong> = you'll get "JavaScript heap out of memory" and crash. Raise with <code>--max-old-space-size=4096</code> (value in MB) or find the leak.</li>
  <li><strong>High <code>external</code> memory</strong> = Buffers, native bindings, ArrayBuffers. Not in the V8 heap, but still in RSS.</li>
  <li>RSS is what the OS sees. If your container has a 512 MB memory limit, that's the number that matters.</li>
</ul>
'''

ANSWERS[49] = r'''
<p>The <strong><code>zlib</code></strong> module provides data compression — gzip, deflate, brotli — both as one-shot functions and as streams. Used internally by Node's HTTP layer to handle <code>Content-Encoding: gzip</code> and <code>br</code>.</p>
<p>Three main algorithms:</p>
<ul>
  <li><strong>gzip</strong> — ubiquitous, moderate compression, fast. Default for HTTP.</li>
  <li><strong>deflate</strong> — same algorithm as gzip but different wrapper. Less common.</li>
  <li><strong>brotli</strong> — better compression ratio than gzip (20-30% smaller), well-supported in modern browsers.</li>
</ul>
<pre><code>const zlib = require("node:zlib");
const fs = require("node:fs");

// One-shot compress (in memory — good for small data)
const compressed = zlib.gzipSync(Buffer.from("hello world"));
const restored = zlib.gunzipSync(compressed).toString();

// Async versions
zlib.gzip(data, (err, result) =&gt; { /* ... */ });

// Streaming — essential for big files (memory stays flat)
fs.createReadStream("big.log")
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream("big.log.gz"));

// Decompress
fs.createReadStream("big.log.gz")
  .pipe(zlib.createGunzip())
  .pipe(fs.createWriteStream("big.log"));

// Brotli for modern HTTP responses
fs.createReadStream("index.html")
  .pipe(zlib.createBrotliCompress())
  .pipe(fs.createWriteStream("index.html.br"));

// Compress an HTTP response manually
app.get("/large", (req, res) =&gt; {
  if (req.headers["accept-encoding"]?.includes("br")) {
    res.setHeader("Content-Encoding", "br");
    getDataStream().pipe(zlib.createBrotliCompress()).pipe(res);
  } else {
    res.setHeader("Content-Encoding", "gzip");
    getDataStream().pipe(zlib.createGzip()).pipe(res);
  }
});</code></pre>
<p><strong>In practice:</strong> for HTTP compression, use the <strong>compression</strong> middleware in Express — it negotiates encoding based on the <code>Accept-Encoding</code> header. Better: terminate compression at a reverse proxy (Nginx, Cloudflare) which handles it more efficiently and lets Node focus on business logic. Use <code>zlib</code> directly for file compression, archive formats, or custom protocols.</p>
'''

ANSWERS[50] = r'''
<p>Compression shrinks data for storage or transmission. Node's <code>zlib</code> supports gzip, deflate, and brotli via both callback and stream APIs.</p>
<pre><code>const zlib = require("node:zlib");
const fs = require("node:fs");
const { promisify } = require("node:util");

// ONE-SHOT (buffers the whole input — use for small data)
const gzip = promisify(zlib.gzip);
const gunzip = promisify(zlib.gunzip);

const compressed = await gzip("hello world, this is some text");
console.log(compressed.length, "bytes");          // compressed Buffer

const original = await gunzip(compressed);
console.log(original.toString());                  // "hello world, ..."

// STREAMING — use for files, network data, anything large
fs.createReadStream("large.log")
  .pipe(zlib.createGzip({ level: 9 }))             // 1=fastest, 9=smallest
  .pipe(fs.createWriteStream("large.log.gz"))
  .on("finish", () =&gt; console.log("done"));

// Decompression
fs.createReadStream("large.log.gz")
  .pipe(zlib.createGunzip())
  .pipe(fs.createWriteStream("restored.log"));

// BROTLI — better ratio, especially for text
fs.createReadStream("index.html")
  .pipe(zlib.createBrotliCompress({
    params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 },  // max quality
  }))
  .pipe(fs.createWriteStream("index.html.br"));

// Compress an HTTP response — express + middleware
const compression = require("compression");
app.use(compression());           // handles gzip/deflate/br transparently

// Data too small to benefit? Skip it — compression has overhead
// Typical threshold: don't compress responses &lt; ~1 KB

// Useful utility — pipe-then-await with error handling
const { pipeline } = require("node:stream/promises");
await pipeline(
  fs.createReadStream("big.log"),
  zlib.createGzip(),
  fs.createWriteStream("big.log.gz"),
);</code></pre>
<p><strong>Choosing compression level:</strong> level 6 (default) is the sweet spot — 95% of max compression at much higher speed than level 9. For real-time work (HTTP), level 3-6. For archives / long-term storage where CPU isn't a concern, level 9 or brotli quality 11.</p>
'''

ANSWERS[51] = r'''
<p><strong>Global objects</strong> in Node are available everywhere without requiring/importing them. Most are JavaScript-standard globals; a handful are Node-specific.</p>
<p><strong>Node-specific globals:</strong></p>
<ul>
  <li><strong><code>global</code></strong> — the global scope itself (like <code>window</code> in browsers).</li>
  <li><strong><code>globalThis</code></strong> — standard, works identically in browser/Node/workers.</li>
  <li><strong><code>process</code></strong> — info about the current Node process (env vars, pid, stdin/stdout, exit).</li>
  <li><strong><code>Buffer</code></strong> — binary data class.</li>
  <li><strong><code>__dirname</code></strong> / <strong><code>__filename</code></strong> — current file's directory / path (CJS only).</li>
  <li><strong><code>require</code></strong>, <strong><code>module</code></strong>, <strong><code>exports</code></strong> — module system (CJS only).</li>
  <li><strong><code>setImmediate</code></strong> / <strong><code>clearImmediate</code></strong> — schedule for next event loop iteration.</li>
  <li><strong><code>setInterval</code></strong> / <strong><code>setTimeout</code></strong> / <strong><code>clearInterval</code></strong> / <strong><code>clearTimeout</code></strong> — timers.</li>
  <li><strong><code>queueMicrotask</code></strong> — queue a microtask.</li>
  <li><strong><code>fetch</code></strong> (Node 18+) — browser-compatible HTTP client.</li>
  <li><strong><code>console</code></strong> — logging.</li>
  <li><strong><code>URL</code></strong>, <strong><code>URLSearchParams</code></strong>, <strong><code>AbortController</code></strong>, <strong><code>TextEncoder</code></strong>, <strong><code>structuredClone</code></strong> — standard web APIs available globally.</li>
</ul>
<pre><code>console.log(process.pid);          // process ID
console.log(process.cwd());        // current working directory
console.log(__dirname);            // directory of this file
setTimeout(() =&gt; console.log("later"), 1000);

// Add to global (avoid! makes code harder to reason about)
global.myApp = { version: "1.0" };
// Better — use modules</code></pre>
<p><strong>Best practice:</strong> don't pollute <code>global</code> with your own variables. It works, but it breaks encapsulation and makes testing painful. Use modules for sharing. One exception: monkey-patching <code>console</code> or installing process-wide crash handlers from a single bootstrap file.</p>
'''

ANSWERS[52] = r'''
<p>The global <code>console</code> object is Node's equivalent of the browser's <code>console</code> — <code>log</code>, <code>error</code>, <code>warn</code>, <code>info</code>, <code>debug</code>, and more. Output goes to <code>stdout</code> or <code>stderr</code>.</p>
<pre><code>// Basic logging
console.log("plain message");                   // stdout
console.info("informational");                  // stdout
console.warn("warning");                        // stderr
console.error("something broke");               // stderr
console.debug("debug info");                    // stderr (by default filtered out)

// Format specifiers (same as util.format)
console.log("User %s is %d years old", "Ada", 36);
console.log("Object: %o", { a: 1, b: 2 });
console.log("JSON: %j", { a: 1 });

// Interpolate objects directly
const user = { name: "Ada", role: "admin" };
console.log("user:", user);                     // nicely formatted

// Group related output
console.group("Request");
console.log("method:", "GET");
console.log("url:", "/users");
console.groupEnd();

// Tables — for arrays of objects
console.table([
  { id: 1, name: "Ada" },
  { id: 2, name: "Lin" },
]);

// Timing
console.time("query");
await db.query("...");
console.timeEnd("query");                       // "query: 123ms"

// Assertions — logs if condition is false
console.assert(1 === 2, "math broke");          // "Assertion failed: math broke"

// Trace — print stack
console.trace("where am I?");

// Count how many times something happens
console.count("hit");                           // "hit: 1", then "hit: 2", ...

// Custom Console instance (write to a file, with custom options)
const { Console } = require("node:console");
const fs = require("node:fs");
const fileLogger = new Console({
  stdout: fs.createWriteStream("app.log"),
  stderr: fs.createWriteStream("error.log"),
});
fileLogger.log("written to app.log");</code></pre>
<p><strong>Production note:</strong> <code>console.log</code> is synchronous to a TTY and asynchronous to pipes — which causes subtle differences in tests and scripts. Real production apps use structured loggers like <strong>pino</strong> (JSON, blazing fast) or <strong>winston</strong> (flexible) so logs are machine-parsable by CloudWatch, Datadog, Loki, etc.</p>
'''

ANSWERS[53] = r'''
<p><code>setTimeout(fn, delay, ...args)</code> schedules a callback to run after at least <code>delay</code> milliseconds. It's a global in Node (no import needed) and returns a Timeout object you can use to cancel.</p>
<pre><code>// Basic — run once after 2 seconds
setTimeout(() =&gt; console.log("2 seconds later"), 2000);

// Pass arguments to the callback
setTimeout((name, age) =&gt; {
  console.log(`Hi ${name}, age ${age}`);
}, 1000, "Ada", 36);

// Cancel with clearTimeout
const timer = setTimeout(doWork, 5000);
clearTimeout(timer);                            // doWork never runs

// Zero delay — runs after current stack + microtasks
setTimeout(() =&gt; console.log("next tick"), 0);

// Promise-based delay (async/await friendly)
const { setTimeout: delay } = require("node:timers/promises");
await delay(1000);          // pauses for 1 second
await delay(5000, "done");  // resolves to "done" after 5s

// With AbortController for cancellation
const ac = new AbortController();
setTimeout(() =&gt; ac.abort(), 3000);      // cancel after 3s

try {
  await delay(10_000, undefined, { signal: ac.signal });
} catch {
  console.log("cancelled");
}

// unref() — don't keep the process alive just for this timer
const t = setTimeout(cleanup, 60_000);
t.unref();   // if nothing else is running, process exits normally

// ref() — the opposite
t.ref();</code></pre>
<p><strong>Key behaviors:</strong></p>
<ul>
  <li>Delay is a <strong>minimum</strong>, not a guarantee. A long synchronous task will push timer callbacks later.</li>
  <li>Minimum delay is 1 ms in Node (1-4 ms in browsers after nesting).</li>
  <li>Node keeps the process alive while timers are pending — use <code>.unref()</code> for background timers you don't want to block shutdown.</li>
  <li>For intervals, use <code>setInterval</code>. For "run after I/O completes, but before next timer tick," use <code>setImmediate</code>.</li>
</ul>
'''

ANSWERS[54] = r'''
<p><code>setInterval(fn, delay)</code> runs a callback repeatedly every <code>delay</code> ms. Returns a handle you pass to <code>clearInterval</code> to stop it. The first invocation happens <em>after</em> the initial delay, not immediately.</p>
<pre><code>// Basic — print every 2 seconds
const timer = setInterval(() =&gt; {
  console.log("tick", new Date().toISOString());
}, 2000);

// Stop after 10 seconds
setTimeout(() =&gt; clearInterval(timer), 10_000);

// Pass arguments
setInterval((msg) =&gt; console.log(msg), 1000, "hello");

// Keep the process alive only if needed
const heartbeat = setInterval(sendHeartbeat, 30_000);
heartbeat.unref();    // exit cleanly even if this is pending

// Better pattern for async work — avoid setInterval when the work might
// take longer than the interval (overlapping executions)

// BAD: if task takes &gt; 5s, next call starts while previous still running
setInterval(async () =&gt; await longTask(), 5000);

// GOOD: recursive setTimeout — wait for previous to finish
async function tick() {
  try { await longTask(); }
  catch (err) { console.error(err); }
  setTimeout(tick, 5000);
}
tick();

// Using the Promise-based timer (Node 16+)
const { setInterval: asyncInterval } = require("node:timers/promises");
const ac = new AbortController();

for await (const _ of asyncInterval(1000, null, { signal: ac.signal })) {
  console.log("async tick");
  if (shouldStop) ac.abort();
}</code></pre>
<p><strong>Common pitfalls:</strong></p>
<ul>
  <li><strong>Overlapping callbacks</strong> — if your work takes longer than the interval, calls queue up. Use recursive <code>setTimeout</code> for async work.</li>
  <li><strong>Forgetting to <code>clearInterval</code></strong> — intervals on long-lived objects cause memory leaks. Always pair setup with teardown in a <code>close()</code> method.</li>
  <li><strong>Drift</strong> — intervals aren't precise; for scheduled jobs use a library like <strong>node-cron</strong> or <strong>agenda</strong> tied to wall-clock time.</li>
</ul>
'''

ANSWERS[55] = r'''
<p><code>clearInterval(timer)</code> stops a timer created by <code>setInterval</code>. After calling it, the callback never fires again. Always safe to call — passing an already-cleared or invalid handle is a no-op.</p>
<pre><code>// Basic — start / stop
const timer = setInterval(() =&gt; {
  console.log("running");
}, 1000);

setTimeout(() =&gt; {
  clearInterval(timer);
  console.log("stopped");
}, 5000);

// Pattern — self-stopping interval after N ticks
let count = 0;
const t = setInterval(() =&gt; {
  count++;
  console.log(`tick ${count}`);
  if (count &gt;= 5) clearInterval(t);
}, 1000);

// Keep track of intervals in a class so you can clean up
class Monitor {
  constructor() {
    this.intervals = [];
  }

  start() {
    this.intervals.push(setInterval(this.checkHealth, 10_000));
    this.intervals.push(setInterval(this.reportMetrics, 60_000));
  }

  stop() {
    this.intervals.forEach(clearInterval);
    this.intervals = [];
  }

  checkHealth() { /* ... */ }
  reportMetrics() { /* ... */ }
}

// Graceful shutdown — clean up timers on SIGTERM
process.on("SIGTERM", () =&gt; {
  clearInterval(timer);
  server.close();
});</code></pre>
<p><strong>Related:</strong> <code>clearTimeout(handle)</code> cancels a <code>setTimeout</code>, and <code>clearImmediate(handle)</code> cancels a <code>setImmediate</code>. All three are safe to call with <code>undefined</code>/<code>null</code> — they just do nothing, so you don't need to check before clearing.</p>
<p><strong>Memory leak warning:</strong> a running <code>setInterval</code> holds references to any variables its callback captures. If the callback references a large object (DOM elements, database connections, huge arrays), forgetting to <code>clearInterval</code> prevents garbage collection of everything in the closure. Always clean up in shutdown handlers and disposal methods.</p>
'''

ANSWERS[56] = r'''
<p>Several ways to schedule "run as soon as possible" in Node, each at a different point in the event loop. Most specific to least specific:</p>
<table>
  <thead><tr><th>Function</th><th>When it runs</th><th>Use case</th></tr></thead>
  <tbody>
    <tr><td><code>process.nextTick(fn)</code></td><td>Before next phase of event loop (highest priority)</td><td>Yielding inside a callback while keeping user code atomic</td></tr>
    <tr><td><code>queueMicrotask(fn)</code></td><td>After current stack, before I/O</td><td>Microtask semantics matching Promises</td></tr>
    <tr><td><code>Promise.resolve().then(fn)</code></td><td>Same as queueMicrotask</td><td>Cleaner than wrapping in a Promise manually</td></tr>
    <tr><td><code>setImmediate(fn)</code></td><td>Check phase (after I/O, before next timers)</td><td>"Run after all pending I/O events complete"</td></tr>
    <tr><td><code>setTimeout(fn, 0)</code></td><td>Timers phase (≥ 1 ms delay)</td><td>Legacy; prefer setImmediate in Node</td></tr>
  </tbody>
</table>
<pre><code>// All five schedule "later" — different "later"s
console.log("1");
setImmediate(() =&gt; console.log("2 immediate"));
setTimeout(() =&gt; console.log("3 timeout"), 0);
process.nextTick(() =&gt; console.log("4 nextTick"));
queueMicrotask(() =&gt; console.log("5 microtask"));
Promise.resolve().then(() =&gt; console.log("6 then"));
console.log("7");

// Output: 1, 7, 4 nextTick, 5 microtask, 6 then, 3 timeout, 2 immediate
// (timeout vs immediate order is not guaranteed with delay=0 at top level)</code></pre>
<p><strong>When to use which:</strong></p>
<ul>
  <li><strong><code>process.nextTick</code></strong> — emit an event after the current function returns but before any I/O. Common in EventEmitter patterns.</li>
  <li><strong><code>setImmediate</code></strong> — yield to pending I/O before running more work. Good for breaking up CPU work.</li>
  <li><strong><code>queueMicrotask</code></strong> — when you want Promise-like ordering without wrapping in a Promise.</li>
  <li>Avoid <code>setTimeout(fn, 0)</code> — semantic is "at least 1 ms," which isn't what you usually want.</li>
</ul>
'''

ANSWERS[57] = r'''
<p><strong><code>process.nextTick(fn)</code></strong> schedules <code>fn</code> to run immediately after the current operation completes, before the event loop continues to its next phase. It's the <strong>highest priority</strong> async scheduling primitive in Node.</p>
<pre><code>console.log("start");

process.nextTick(() =&gt; console.log("nextTick"));
setImmediate(() =&gt; console.log("immediate"));
setTimeout(() =&gt; console.log("timeout"), 0);
Promise.resolve().then(() =&gt; console.log("promise"));

console.log("end");

// Output:
//   start
//   end
//   nextTick           ← ran first (before even microtasks in older versions)
//   promise            ← microtask
//   timeout            ← timers phase
//   immediate          ← check phase</code></pre>
<p><strong>Why it exists:</strong> before the current operation fully returns, Node drains the nextTick queue. This lets you preserve "user-code-runs-atomically" semantics while still scheduling follow-up work.</p>
<p><strong>Canonical use case — emit events asynchronously from a constructor:</strong></p>
<pre><code>class MyEmitter extends EventEmitter {
  constructor() {
    super();
    // BAD — listeners can't attach yet because constructor hasn't returned
    this.emit("start");

    // GOOD — defer to next tick
    process.nextTick(() =&gt; this.emit("start"));
  }
}

const e = new MyEmitter();
e.on("start", () =&gt; console.log("got start"));   // now this works</code></pre>
<p><strong>Warning — can starve I/O:</strong> <code>process.nextTick</code> runs before I/O events. If you recursively call <code>process.nextTick</code>, the event loop never progresses and incoming connections are never handled. For breaking up CPU work, use <code>setImmediate</code> instead — it yields to I/O first.</p>
<p>In modern Node, <strong>microtasks from Promises</strong> are usually a cleaner tool. Reach for <code>process.nextTick</code> specifically when you want the very-highest priority async slot.</p>
'''

ANSWERS[58] = r'''
<p>An <strong>uncaught exception</strong> is a synchronous error that escapes every <code>try/catch</code> — e.g., throwing in a timer callback. Node emits it on <code>process</code>; if you don't listen, the process crashes.</p>
<pre><code>// Listen for uncaught exceptions
process.on("uncaughtException", (err, origin) =&gt; {
  console.error("UNCAUGHT:", err, "origin:", origin);
  // The app is now in an undefined state — LOG and EXIT.
  // DO NOT try to keep running, since state may be corrupted.
  process.exit(1);
});

// For Promises — unhandled rejections are separate
process.on("unhandledRejection", (reason, promise) =&gt; {
  console.error("UNHANDLED REJECTION:", reason);
  // Node 15+ terminates on this by default (--unhandled-rejections=throw)
});

// Exit hooks — cleanup before process dies
process.on("beforeExit", (code) =&gt; {
  // Fired when event loop is empty. Can still schedule more work.
  console.log("beforeExit", code);
});

process.on("exit", (code) =&gt; {
  // Synchronous only — event loop is done
  console.log("exit", code);
});</code></pre>
<p><strong>The hard truth about uncaughtException:</strong></p>
<ul>
  <li>Once caught, <strong>your process state is unsafe</strong>. Half-written files, dangling transactions, inconsistent memory — anything is possible.</li>
  <li>The right move is: log the error with full context, flush the logger, and exit. Let a process manager (PM2, systemd, Kubernetes) restart you cleanly.</li>
  <li>Never use <code>uncaughtException</code> as a blanket "try/catch" for the whole app. Catch errors where they originate — inside async functions with <code>try/catch</code>, or in Promise <code>.catch()</code>.</li>
</ul>
<p><strong>Best practices:</strong></p>
<ul>
  <li>Always <code>await</code> or <code>.catch()</code> every Promise.</li>
  <li>Wrap event handlers in try/catch since thrown errors there become uncaught.</li>
  <li>Use <code>--unhandled-rejections=strict</code> or Node 15+ default (which throws).</li>
  <li>Run under a supervisor that auto-restarts crashed processes.</li>
</ul>
'''

ANSWERS[59] = r'''
<p>The <strong><code>domain</code></strong> module was an early Node attempt (2011) to group related async operations into an "error domain" — any uncaught error would bubble to the domain's handler. It's been <strong>deprecated since Node 4</strong> and should not be used in new code.</p>
<pre><code>// Legacy — DO NOT USE in new code
const domain = require("node:domain");

const d = domain.create();

d.on("error", (err) =&gt; {
  console.error("caught in domain:", err);
});

d.run(() =&gt; {
  setTimeout(() =&gt; {
    throw new Error("boom!");           // normally uncaught
    // but domain catches it
  }, 100);
});</code></pre>
<p><strong>Why it was deprecated:</strong></p>
<ul>
  <li>Domains couldn't reliably catch errors across async boundaries (Promises, worker_threads).</li>
  <li>The model conflicted with modern error-handling (Promises, async/await, AbortController).</li>
  <li>Fixing the issues would require fundamental changes incompatible with the JS async model.</li>
</ul>
<p><strong>Modern replacements:</strong></p>
<table>
  <thead><tr><th>Need</th><th>Modern tool</th></tr></thead>
  <tbody>
    <tr><td>Group async operations + cancellation</td><td><code>AbortController</code> + <code>AbortSignal</code></td></tr>
    <tr><td>Track async context</td><td><code>AsyncLocalStorage</code> (from <code>async_hooks</code>)</td></tr>
    <tr><td>Catch errors from async work</td><td>async/await + try/catch, or Promise <code>.catch()</code></td></tr>
    <tr><td>Last-resort safety net</td><td><code>process.on("uncaughtException")</code> + exit + supervisor</td></tr>
  </tbody>
</table>
<pre><code>// Modern equivalent — AsyncLocalStorage for request-scoped context
const { AsyncLocalStorage } = require("node:async_hooks");
const store = new AsyncLocalStorage();

app.use((req, res, next) =&gt; {
  store.run({ requestId: crypto.randomUUID() }, next);
});

// Anywhere downstream — even inside timers/Promises
function log(msg) {
  const ctx = store.getStore();
  console.log(`[${ctx?.requestId}] ${msg}`);
}</code></pre>
<p>If you encounter <code>domain</code> in legacy code, migrate to proper error propagation with Promises and AsyncLocalStorage for context.</p>
'''

ANSWERS[60] = r'''
<p>The <code>domain</code> module is <strong>deprecated</strong> — use async/await + try/catch and AsyncLocalStorage in new code. It's shown here only because legacy codebases may still contain it.</p>
<pre><code>// LEGACY DOMAIN PATTERN — for reading old code only
const domain = require("node:domain");
const http = require("node:http");

const server = http.createServer((req, res) =&gt; {
  const d = domain.create();
  d.add(req);
  d.add(res);

  d.on("error", (err) =&gt; {
    console.error("request failed:", err);
    try {
      res.writeHead(500);
      res.end("internal error");
    } catch {
      // response may be already sent
    }
    // Force a graceful shutdown of the worker
    d.exit();
  });

  d.run(() =&gt; {
    // any async error here is caught by d.on("error")
    riskyOperation(req, res);
  });
});</code></pre>
<p><strong>Modern equivalent — use try/catch in async functions:</strong></p>
<pre><code>// Express middleware wrapping async handlers
const wrap = fn =&gt; (req, res, next) =&gt; {
  Promise.resolve(fn(req, res, next)).catch(next);
};

app.get("/users/:id", wrap(async (req, res) =&gt; {
  const user = await db.findUser(req.params.id);    // any throw is caught
  res.json(user);
}));

// Central error handler
app.use((err, req, res, next) =&gt; {
  console.error(err);
  res.status(500).json({ error: "internal" });
});

// For request-scoped context (correlation IDs, user info)
const { AsyncLocalStorage } = require("node:async_hooks");
const als = new AsyncLocalStorage();

app.use((req, res, next) =&gt; {
  als.run({ requestId: crypto.randomUUID(), userId: req.user?.id }, next);
});

// Anywhere in the call tree — even deep inside async ops — retrieve context
function auditLog(action) {
  const ctx = als.getStore();
  db.logEvent({ ...ctx, action, timestamp: Date.now() });
}</code></pre>
<p><strong>Bottom line:</strong> if you're reading old Node code, <code>domain</code> is a relic. Don't add it to anything new. Use structured error propagation via Promises, and <code>AsyncLocalStorage</code> for context that needs to travel across async boundaries.</p>
'''

ANSWERS[61] = r'''
<p>The <strong><code>readline</code></strong> module reads input line by line from a readable stream — typically <code>process.stdin</code>. Perfect for CLIs, interactive prompts, and parsing large text files one line at a time.</p>
<pre><code>const readline = require("node:readline");

// INTERACTIVE CLI — read user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question("What is your name? ", (answer) =&gt; {
  console.log(`Hello, ${answer}!`);
  rl.close();
});

// Promise-based variant (Node 17+)
const rlp = require("node:readline/promises");
const rl2 = rlp.createInterface({ input: process.stdin, output: process.stdout });
const name = await rl2.question("Name? ");
const age = await rl2.question("Age? ");
console.log(name, age);
rl2.close();

// READING A FILE line by line — constant memory regardless of file size
const fs = require("node:fs");
const rl3 = readline.createInterface({
  input: fs.createReadStream("large.log"),
  crlfDelay: Infinity,               // handle both \r\n and \n
});

let lineCount = 0;
for await (const line of rl3) {
  if (line.includes("ERROR")) console.log(line);
  lineCount++;
}
console.log(`processed ${lineCount} lines`);

// Event-based reading
rl3.on("line", (line) =&gt; { /* ... */ });
rl3.on("close", () =&gt; { /* done */ });

// Multi-line CLI with history + arrow keys
const history = [];
const rl4 = readline.createInterface({
  input: process.stdin, output: process.stdout,
  prompt: "&gt; ",
  historySize: 100,
});
rl4.prompt();
rl4.on("line", (line) =&gt; {
  console.log("you said:", line);
  rl4.prompt();
});</code></pre>
<p><strong>Why readline instead of reading the whole stream?</strong> Line-oriented input is common (log parsing, CSV headers, interactive commands). Reading line-by-line avoids loading gigabyte files into memory. For richer CLIs (colors, menus, autocomplete), layer on libraries like <strong>inquirer</strong>, <strong>prompts</strong>, or <strong>enquirer</strong>.</p>
'''

ANSWERS[62] = r'''
<p>Reading from the command line in Node means reading from <code>process.stdin</code>. Use <code>readline</code> for line-at-a-time input; use <code>process.argv</code> for arguments passed at launch.</p>
<pre><code>// 1. COMMAND-LINE ARGUMENTS — available at startup (no reading needed)
// Run: node app.js --port 3000 --host localhost
console.log(process.argv);
// [ "/usr/bin/node", "/path/to/app.js", "--port", "3000", "--host", "localhost" ]

// Slice off the first two to get just the user-provided args
const args = process.argv.slice(2);
// [ "--port", "3000", "--host", "localhost" ]

// Real argument parsing — use built-in util.parseArgs (Node 18.3+)
const { parseArgs } = require("node:util");
const { values } = parseArgs({
  options: {
    port: { type: "string", default: "3000" },
    host: { type: "string", default: "localhost" },
    verbose: { type: "boolean", short: "v" },
  },
});
console.log(values);   // { port: "3000", host: "localhost", verbose: true }

// For richer CLIs — use commander, yargs, or citty

// 2. INTERACTIVE INPUT with readline
const readline = require("node:readline/promises");
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

const name = await rl.question("What's your name? ");
console.log(`Hello, ${name}!`);

// Validation loop
let age;
while (true) {
  const input = await rl.question("Enter your age: ");
  age = parseInt(input, 10);
  if (!isNaN(age) &amp;&amp; age &gt; 0) break;
  console.log("Please enter a valid age.");
}
rl.close();

// 3. PIPED INPUT — treat stdin as a stream
// Run: cat data.txt | node app.js
let data = "";
process.stdin.setEncoding("utf-8");
process.stdin.on("data", (chunk) =&gt; data += chunk);
process.stdin.on("end", () =&gt; {
  console.log("got input:", data);
});

// For line-by-line piped input
const rl2 = require("node:readline").createInterface({ input: process.stdin });
for await (const line of rl2) {
  console.log("line:", line);
}</code></pre>
<p><strong>Argument parsing recommendation:</strong> for anything beyond trivial CLIs, use <strong>commander</strong> or <strong>yargs</strong> — they handle subcommands, help text, type coercion, and environment-variable fallbacks. For modern, lightweight needs, <strong>citty</strong> is excellent.</p>
'''

ANSWERS[63] = r'''
<p>The <strong><code>events</code></strong> module exposes <code>EventEmitter</code> — the base class underlying much of Node's async API. HTTP servers, streams, sockets, and child processes all inherit from it.</p>
<p><strong>Why events matter in Node:</strong> Node's concurrency is event-driven. Instead of polling or blocking, you register listeners and let the runtime notify you when things happen — a request arrives, data is ready, a connection closes.</p>
<pre><code>const EventEmitter = require("node:events");

class OrderService extends EventEmitter {
  place(order) {
    // business logic...
    this.emit("order.placed", order);

    // Async side effects — notifications, webhooks, metrics — all listen
  }
}

const svc = new OrderService();

// Multiple listeners — all fire when emit happens
svc.on("order.placed", sendConfirmationEmail);
svc.on("order.placed", updateInventory);
svc.on("order.placed", recordMetric);

svc.place({ id: 1, total: 99 });    // all three fire, in registration order

// Rich event API
svc.once("ready", () =&gt; console.log("ready"));   // fires only once
svc.off("order.placed", sendConfirmationEmail);  // remove listener
svc.removeAllListeners("order.placed");          // remove all
svc.listenerCount("order.placed");               // how many registered
svc.eventNames();                                 // array of event names</code></pre>
<p><strong>EventEmitter is used everywhere:</strong></p>
<ul>
  <li><strong>HTTP server</strong> — <code>server.on("request", ...)</code>, <code>server.on("close", ...)</code>.</li>
  <li><strong>Streams</strong> — <code>stream.on("data", ...)</code>, <code>stream.on("end", ...)</code>, <code>stream.on("error", ...)</code>.</li>
  <li><strong>Process</strong> — <code>process.on("SIGTERM", ...)</code>, <code>process.on("exit", ...)</code>.</li>
  <li><strong>Sockets</strong> — <code>socket.on("connect", ...)</code>, <code>socket.on("close", ...)</code>.</li>
</ul>
<p>You can extend EventEmitter in your own classes to build pub/sub patterns, domain events, or any push-based API — a classic design pattern that Node made first-class.</p>
'''

ANSWERS[64] = r'''
<p>Two ways to create an EventEmitter: instantiate directly, or subclass for a custom emitter with domain-specific methods.</p>
<pre><code>const EventEmitter = require("node:events");

// 1. DIRECT INSTANTIATION — quick and simple
const emitter = new EventEmitter();

emitter.on("greet", (name) =&gt; console.log(`Hello ${name}`));
emitter.emit("greet", "Ada");          // "Hello Ada"

// 2. SUBCLASSING — when the emitter has its own methods/state
class Clock extends EventEmitter {
  constructor() {
    super();
    this.interval = setInterval(() =&gt; {
      this.emit("tick", new Date());
    }, 1000);
  }

  stop() {
    clearInterval(this.interval);
    this.emit("stopped");
  }
}

const clock = new Clock();
clock.on("tick", (date) =&gt; console.log("tick:", date));
clock.once("stopped", () =&gt; console.log("all done"));
setTimeout(() =&gt; clock.stop(), 5000);

// 3. ASYNC ITERATION — treat events as a stream
const { on, once } = require("node:events");

(async () =&gt; {
  // once() resolves to the next emission
  const [name] = await once(emitter, "greet");

  // on() is an async iterator — loop until listener is removed
  for await (const [date] of on(clock, "tick")) {
    console.log("iter:", date);
    if (shouldStop) break;
  }
})();

// 4. LISTENER LIMIT — default is 10 per event; raise for legitimate need
emitter.setMaxListeners(50);
// Exceeding the limit prints a warning — it's a leak indicator, not an error</code></pre>
<p><strong>Important rules:</strong></p>
<ul>
  <li>Always handle the <strong><code>"error"</code></strong> event. An unhandled <code>error</code> event crashes the process.</li>
  <li><strong>Events are synchronous by default</strong> — listeners fire inline during <code>emit()</code>. Wrap async work in Promises.</li>
  <li>Remove listeners when done to avoid memory leaks — especially on long-lived emitters.</li>
  <li>The <code>"newListener"</code> and <code>"removeListener"</code> meta-events let you track registration changes.</li>
</ul>
'''

ANSWERS[65] = r'''
<p><code>EventEmitter</code> is Node's implementation of the <strong>observer pattern</strong> (a.k.a. pub/sub within a single process). An object can emit named events; any number of listeners can subscribe. It's the foundation of Node's async API.</p>
<p><strong>Key methods:</strong></p>
<ul>
  <li><strong><code>on(event, listener)</code></strong> — subscribe. Alias: <code>addListener</code>.</li>
  <li><strong><code>once(event, listener)</code></strong> — subscribe but auto-unsubscribe after first fire.</li>
  <li><strong><code>off(event, listener)</code></strong> — unsubscribe. Alias: <code>removeListener</code>.</li>
  <li><strong><code>emit(event, ...args)</code></strong> — fire the event, calling every listener synchronously with <code>args</code>.</li>
  <li><strong><code>removeAllListeners(event?)</code></strong> — clear one or all events.</li>
  <li><strong><code>listenerCount(event)</code></strong> — how many subscribed.</li>
  <li><strong><code>listeners(event)</code></strong> — array of subscribed listeners.</li>
  <li><strong><code>prependListener(event, fn)</code></strong> — add to the front, not the end.</li>
</ul>
<pre><code>const EventEmitter = require("node:events");
const emitter = new EventEmitter();

// Listeners fire in registration order (unless prepended)
emitter.on("data", (x) =&gt; console.log("first:",  x));
emitter.on("data", (x) =&gt; console.log("second:", x));
emitter.prependListener("data", (x) =&gt; console.log("zero:", x));

emitter.emit("data", 42);
// zero: 42, first: 42, second: 42

// Special behavior — the "error" event
emitter.on("error", (err) =&gt; console.error("caught:", err.message));
emitter.emit("error", new Error("something bad"));
// WITHOUT a listener, emit("error", ...) throws and crashes the process</code></pre>
<p><strong>Why it's powerful:</strong></p>
<ul>
  <li><strong>Decouples producer from consumer</strong> — the code emitting doesn't need to know who listens.</li>
  <li><strong>Multiple subscribers</strong> — easy fan-out of a single event to many handlers.</li>
  <li><strong>Lifecycle hooks</strong> — perfect for before/after patterns (middleware, plugins, audit logging).</li>
  <li><strong>Testable</strong> — tests attach their own listeners to observe behavior.</li>
</ul>
<p>Nearly every I/O object in Node extends EventEmitter: <code>http.Server</code>, <code>net.Socket</code>, <code>stream.Readable</code>, <code>ChildProcess</code>, <code>process</code>.</p>
'''

ANSWERS[66] = r'''
<p><code>emit(eventName, ...args)</code> synchronously invokes every registered listener for <code>eventName</code>, passing <code>args</code>. It returns <code>true</code> if there were listeners, <code>false</code> if none.</p>
<pre><code>const EventEmitter = require("node:events");
const bus = new EventEmitter();

// Subscribe
bus.on("message", (from, text) =&gt; {
  console.log(`${from}: ${text}`);
});

// Emit — passes any number of arguments to listeners
bus.emit("message", "Ada", "hello world");
// "Ada: hello world"

// Return value — useful to check if anyone is listening
if (!bus.emit("unused")) {
  console.log("no listeners for 'unused'");
}

// Emit works with any arguments — listener signature should match
bus.on("userCreated", (user, meta) =&gt; {
  // user and meta are passed through
});
bus.emit("userCreated", { id: 1, name: "Ada" }, { source: "api" });

// Conventions:
// 1. Emit the event name as past-tense verb: "created", "updated", "deleted"
//    (emit what HAPPENED, not a command)
// 2. Pass one "payload" object rather than many positional args — easier to evolve

// Good
bus.emit("user.created", { id, name, email });

// Less good — adding fields requires changing every listener signature
bus.emit("user.created", id, name, email);</code></pre>
<p><strong>Async listeners:</strong> emit is synchronous, but listeners can be async. Node doesn't wait for their Promises — fire-and-forget. If you need sequential async listeners, implement it yourself:</p>
<pre><code>// Serial async listeners with error aggregation
async function emitAsync(emitter, event, ...args) {
  const listeners = emitter.listeners(event);
  const results = [];
  for (const fn of listeners) {
    results.push(await fn(...args));
  }
  return results;
}

// Or parallel — fire all at once
async function emitParallel(emitter, event, ...args) {
  return Promise.all(emitter.listeners(event).map(fn =&gt; fn(...args)));
}</code></pre>
<p><strong>Error handling:</strong> if a listener throws synchronously, the error propagates up through <code>emit</code> to the caller. Unhandled errors in async listeners become unhandled rejections — always use try/catch or <code>.catch()</code>.</p>
'''

ANSWERS[67] = r'''
<p><strong><code>worker_threads</code></strong> lets Node run JavaScript on <strong>multiple threads</strong> within the same process. Unlike <code>cluster</code> (which forks separate processes), worker threads share the same process but have isolated memory — making them ideal for CPU-intensive work that would otherwise block the event loop.</p>
<pre><code>// main.js
const { Worker } = require("node:worker_threads");

// Run a script in a worker thread
const worker = new Worker("./heavy.js", {
  workerData: { numbers: [1, 2, 3, 4, 5] },
});

worker.on("message", (result) =&gt; {
  console.log("result:", result);
});

worker.on("error", (err) =&gt; {
  console.error("worker error:", err);
});

worker.on("exit", (code) =&gt; {
  if (code !== 0) console.error(`Worker stopped with code ${code}`);
});

// heavy.js — the worker's code
const { workerData, parentPort } = require("node:worker_threads");

// CPU-heavy work — prime factorization, image processing, hashing, etc.
function expensiveCompute(arr) {
  let result = 0;
  for (const n of arr) {
    for (let i = 0; i &lt; 1e7; i++) result += Math.sqrt(n * i);
  }
  return result;
}

parentPort.postMessage(expensiveCompute(workerData.numbers));

// SHARED MEMORY — SharedArrayBuffer crosses the boundary without copying
const shared = new SharedArrayBuffer(1024);
const view = new Int32Array(shared);
worker.postMessage({ shared });    // both threads see the same memory
// Use Atomics.* for safe concurrent access</code></pre>
<p><strong>When to use worker_threads:</strong></p>
<ul>
  <li><strong>CPU-bound tasks</strong> — image manipulation, cryptographic operations, ML inference, data crunching.</li>
  <li><strong>Work that would block the event loop</strong> for &gt; 50 ms or so.</li>
  <li><strong>Not for I/O</strong> — Node's async I/O is already non-blocking; workers won't make it faster.</li>
</ul>
<p><strong>worker_threads vs cluster vs child_process:</strong></p>
<table>
  <thead><tr><th>Feature</th><th>worker_threads</th><th>cluster</th><th>child_process</th></tr></thead>
  <tbody>
    <tr><td>Shared memory</td><td>Yes (SharedArrayBuffer)</td><td>No</td><td>No</td></tr>
    <tr><td>Startup cost</td><td>Low</td><td>High (fork process)</td><td>High</td></tr>
    <tr><td>Use case</td><td>CPU work</td><td>Scale servers across cores</td><td>Run external programs</td></tr>
  </tbody>
</table>
<p>For pooled workers with a clean API, use the <strong>piscina</strong> library.</p>
'''

ANSWERS[68] = r'''
<p>Create a worker thread with <code>new Worker()</code>, pointing at a script file or providing inline code. Workers communicate with the main thread via message passing.</p>
<pre><code>// METHOD 1 — Separate file
// main.js
const { Worker } = require("node:worker_threads");

const worker = new Worker("./worker.js", {
  workerData: { file: "huge.csv" },
});

worker.on("message", (msg) =&gt; console.log("got:", msg));
worker.on("error", console.error);
worker.on("exit", (code) =&gt; console.log("exited:", code));

// Send messages to the worker
worker.postMessage({ action: "process" });

// worker.js
const { parentPort, workerData } = require("node:worker_threads");
console.log("processing:", workerData.file);

parentPort.on("message", (msg) =&gt; {
  const result = expensiveWork(msg);
  parentPort.postMessage(result);
});

// METHOD 2 — Inline code (useful for small workers, no extra files)
const worker2 = new Worker(`
  const { parentPort, workerData } = require("node:worker_threads");
  parentPort.postMessage(workerData.n * 2);
`, {
  eval: true,
  workerData: { n: 21 },
});
worker2.on("message", console.log);    // 42

// METHOD 3 — Worker pool for reusable workers
const { Worker } = require("node:worker_threads");
class WorkerPool {
  constructor(file, size) {
    this.workers = Array.from({ length: size }, () =&gt; new Worker(file));
    this.queue = [];
    this.workers.forEach((w) =&gt; {
      w.on("message", (result) =&gt; {
        const { resolve } = w.current;
        w.current = null;
        resolve(result);
        this.next(w);
      });
    });
  }

  run(data) {
    return new Promise((resolve) =&gt; {
      this.queue.push({ data, resolve });
      this.next();
    });
  }

  next(worker) {
    const free = worker || this.workers.find((w) =&gt; !w.current);
    if (!free || this.queue.length === 0) return;
    const task = this.queue.shift();
    free.current = task;
    free.postMessage(task.data);
  }
}

// Production alternative — the "piscina" package handles all of this cleanly
// npm install piscina</code></pre>
<p><strong>Best practices:</strong> create workers once and reuse them (startup cost is ~40ms). For many short-lived tasks, a pool beats creating a worker per task. Always handle the <code>"error"</code> and <code>"exit"</code> events. Use <code>SharedArrayBuffer</code> for big data you'd otherwise copy.</p>
'''

ANSWERS[69] = r'''
<p><strong><code>async_hooks</code></strong> is a low-level API that lets you observe the lifecycle of async resources — when they're created, when they run their callbacks, when they're destroyed. It powers context propagation libraries and async-aware instrumentation (APM tools like Datadog, New Relic).</p>
<pre><code>const async_hooks = require("node:async_hooks");

// Create a tracker
const hook = async_hooks.createHook({
  init(asyncId, type, triggerAsyncId, resource) {
    // Called when any async resource is created
    // type: "HTTPPARSER", "TCPWRAP", "Timeout", "PROMISE", "TickObject", ...
  },
  before(asyncId) {
    // Before a callback runs
  },
  after(asyncId) {
    // After a callback completes
  },
  destroy(asyncId) {
    // When the resource is destroyed
  },
  promiseResolve(asyncId) {
    // When a Promise resolves
  },
});

hook.enable();      // start tracking
// hook.disable() to stop

// Inspect the currently-executing async context
async_hooks.executionAsyncId();     // current asyncId
async_hooks.triggerAsyncId();       // what triggered us</code></pre>
<p><strong>The raw API is rarely used directly.</strong> Instead, use <code>AsyncLocalStorage</code> — a higher-level abstraction built on async_hooks that solves the most common need: <strong>request-scoped context</strong>.</p>
<pre><code>// AsyncLocalStorage — the killer use case
const { AsyncLocalStorage } = require("node:async_hooks");
const store = new AsyncLocalStorage();

// Wrap each request in its own context
app.use((req, res, next) =&gt; {
  store.run({ requestId: crypto.randomUUID(), userId: req.user?.id }, next);
});

// Read context ANYWHERE in the call tree — even deep inside Promises/timers
function log(message) {
  const ctx = store.getStore();
  console.log(`[req=${ctx?.requestId}] ${message}`);
}

// Example: log inside a DB call 5 levels deep
async function getUser(id) {
  log("fetching user");      // includes requestId!
  return db.users.findById(id);
}</code></pre>
<p><strong>What it's for:</strong> correlation IDs in logs, tenant isolation in multi-tenant apps, per-request caching, distributed tracing. Performance cost is real but usually small (~5-10% for async_hooks; less for AsyncLocalStorage alone).</p>
'''

ANSWERS[70] = r'''
<p>Tracking async resources has two levels: the low-level <code>async_hooks</code> API (for observability tools) and the higher-level <code>AsyncLocalStorage</code> (for app code that needs context).</p>
<pre><code>// HIGH-LEVEL — AsyncLocalStorage (what you actually want 95% of the time)
const { AsyncLocalStorage } = require("node:async_hooks");
const als = new AsyncLocalStorage();

// In an Express/Koa/Fastify middleware
app.use((req, res, next) =&gt; {
  const context = {
    requestId: req.headers["x-request-id"] || crypto.randomUUID(),
    userId:    req.user?.id,
    startTime: Date.now(),
  };
  als.run(context, next);
});

// Later, deep in the call stack — context is automatically preserved
function audit(action) {
  const { requestId, userId } = als.getStore() ?? {};
  console.log(JSON.stringify({ requestId, userId, action, ts: Date.now() }));
}

// Works across promises, timeouts, I/O, any async boundary
async function doThing() {
  await new Promise((r) =&gt; setTimeout(r, 100));
  audit("did-thing");         // still has the requestId!
}

// LOW-LEVEL — async_hooks (for building tools like APMs)
const asyncHooks = require("node:async_hooks");

const resourceTypes = new Map();

const hook = asyncHooks.createHook({
  init(asyncId, type, triggerAsyncId) {
    resourceTypes.set(asyncId, { type, triggerAsyncId, createdAt: Date.now() });
  },
  destroy(asyncId) {
    const info = resourceTypes.get(asyncId);
    if (info) {
      const lifetime = Date.now() - info.createdAt;
      // e.g. log if lifetime &gt; 60s — may indicate a leak
      resourceTypes.delete(asyncId);
    }
  },
});

hook.enable();

// Inspect what async work is currently live
setInterval(() =&gt; {
  console.log(`Tracking ${resourceTypes.size} async resources`);
}, 30_000);</code></pre>
<p><strong>Performance caveat:</strong> enabling async_hooks has overhead — every async operation runs hook code. In hot-path servers, weigh the cost. <code>AsyncLocalStorage</code> alone is more optimized and usually fine for production.</p>
<p><strong>Common usage:</strong></p>
<ul>
  <li>Request correlation in logs across microservices.</li>
  <li>User/tenant context in multi-tenant apps without passing it through every function.</li>
  <li>Distributed tracing (OpenTelemetry uses this internally).</li>
</ul>
'''

ANSWERS[71] = r'''
<p>The <strong><code>inspector</code></strong> module exposes Node's built-in debugger protocol — the same Chrome DevTools Protocol used by browser debuggers. Lets your code connect to its own debugger or any tool that speaks the protocol.</p>
<p><strong>Two ways to use it:</strong></p>
<ol>
  <li><strong>Start Node with inspection enabled</strong> — no code changes needed.</li>
  <li><strong>Programmatic API</strong> — enable/disable inspector from within your code.</li>
</ol>
<pre><code>// METHOD 1 — command line
// node --inspect app.js               // opens port 9229, waits for client
// node --inspect-brk app.js           // breaks on the first line
// node --inspect=0.0.0.0:9229 app.js  // listen on all interfaces

// Then open chrome://inspect in Chrome, or connect with VS Code's debugger

// METHOD 2 — programmatic
const inspector = require("node:inspector");

// Start listening for a debugger client
inspector.open(9229, "0.0.0.0", true);
// third arg: whether to block until client connects

// Use the underlying protocol directly
const session = new inspector.Session();
session.connect();

// Enable profilers
session.post("Profiler.enable", () =&gt; {
  session.post("Profiler.start", () =&gt; {
    // run code to profile
    setTimeout(() =&gt; {
      session.post("Profiler.stop", (err, { profile }) =&gt; {
        // save as .cpuprofile, load in DevTools → Performance tab
        require("node:fs").writeFileSync(
          "app.cpuprofile",
          JSON.stringify(profile));
      });
    }, 5000);
  });
});

// Take a heap snapshot — load in DevTools → Memory tab
session.post("HeapProfiler.takeHeapSnapshot", null, (err) =&gt; {
  /* snapshot arrives via session.on("HeapProfiler.addHeapSnapshotChunk") */
});

// Close when done
inspector.close();</code></pre>
<p><strong>Common uses:</strong></p>
<ul>
  <li><strong>Interactive debugging</strong> — step through code, inspect variables, set breakpoints.</li>
  <li><strong>CPU profiling</strong> — find hot functions eating CPU.</li>
  <li><strong>Memory profiling / heap snapshots</strong> — diagnose memory leaks.</li>
  <li><strong>Attaching to production</strong> — <code>SIGUSR1</code> (or <code>process.kill(pid, "SIGUSR1")</code>) opens an inspector port on a running process.</li>
</ul>
<p>Most developers interact with this indirectly via IDE debuggers (VS Code, WebStorm) or Chrome DevTools; the programmatic API is for building custom tooling.</p>
'''

ANSWERS[72] = r'''
<p>The usual flow: start Node with <code>--inspect</code>, then attach a debugger client. VS Code's built-in Node debugger is the most popular; Chrome DevTools is the built-in fallback.</p>
<pre><code>// Start Node with inspection
//   node --inspect app.js             // debug mode, doesn't pause
//   node --inspect-brk app.js         // pauses before first line so you can set breakpoints

// Default port: 9229 — accessible at ws://127.0.0.1:9229/&lt;uuid&gt;

// After starting, you'll see output like:
//   Debugger listening on ws://127.0.0.1:9229/abc-123-...
//   For help, see: https://nodejs.org/en/docs/inspector

// CONNECT FROM CHROME
// 1. Open chrome://inspect
// 2. Click "Inspect" next to your Node process
// 3. Use the DevTools Sources panel — breakpoints, step, watch vars

// CONNECT FROM VS CODE — .vscode/launch.json
//   {
//     "type": "node",
//     "request": "attach",
//     "name": "Attach to Node",
//     "port": 9229
//   }

// OR let VS Code start Node itself — simpler
//   {
//     "type": "node",
//     "request": "launch",
//     "name": "Launch app",
//     "program": "${workspaceFolder}/app.js"
//   }

// PROGRAMMATIC — trigger inspector from within your code
const inspector = require("node:inspector");

// Open inspector port when a specific signal arrives
process.on("SIGUSR2", () =&gt; {
  if (inspector.url()) inspector.close();
  else inspector.open(9229, "127.0.0.1");
});

// INSIDE CODE — drop a breakpoint via the "debugger" statement
function processOrder(order) {
  debugger;                        // pauses when debugger is attached
  return order.total * 1.1;
}

// COMMAND-LINE DEBUGGER (no GUI)
// node inspect app.js
// Then: n (next), s (step), c (continue), list, repl, watch('x'), etc.

// Attach to a running Node process
// kill -SIGUSR1 &lt;pid&gt;          # opens inspector on default port</code></pre>
<p><strong>Pro tips:</strong></p>
<ul>
  <li><strong>Conditional breakpoints</strong> — right-click a breakpoint in DevTools to only break when a condition is true.</li>
  <li><strong>Logpoints</strong> — "breakpoints" that log a message without pausing. Add observability without <code>console.log</code>s scattered in code.</li>
  <li><strong>Never expose port 9229 in production</strong> — it allows arbitrary code execution. Bind to <code>127.0.0.1</code> and use SSH tunneling if needed.</li>
  <li>For a pure-CLI debugger, run <code>node inspect app.js</code>.</li>
</ul>
'''

ANSWERS[73] = r'''
<p>The <strong><code>perf_hooks</code></strong> module (Performance Hooks) provides high-resolution timing APIs — microsecond-precision timers, performance marks/measures, and observers. Based on the W3C Performance Timeline spec used in browsers.</p>
<pre><code>const { performance, PerformanceObserver } = require("node:perf_hooks");

// High-resolution "now" in milliseconds (with fractional μs precision)
const start = performance.now();
doWork();
const duration = performance.now() - start;
console.log(`took ${duration.toFixed(3)} ms`);

// Marks and measures — named points in time
performance.mark("task-start");
doExpensiveWork();
performance.mark("task-end");
performance.measure("task", "task-start", "task-end");

// Observe measures — fires when measurements are recorded
const observer = new PerformanceObserver((items) =&gt; {
  for (const entry of items.getEntries()) {
    console.log(`${entry.name}: ${entry.duration.toFixed(2)} ms`);
  }
});
observer.observe({ entryTypes: ["measure"] });

// Node-specific observers
const httpObserver = new PerformanceObserver((items) =&gt; {
  items.getEntries().forEach(e =&gt; console.log(e.name, e.duration));
});
httpObserver.observe({ entryTypes: ["http"] });   // HTTP request timings

// Event loop utilization — detect when the loop is under stress
const elu = performance.eventLoopUtilization();
// { idle, active, utilization }  — utilization &gt; 0.8 = stressed

setInterval(() =&gt; {
  const current = performance.eventLoopUtilization(elu);
  console.log(`loop utilization: ${(current.utilization * 100).toFixed(1)}%`);
}, 1000);

// Node startup timings
const { nodeTiming } = performance;
console.log("startup took:", nodeTiming.bootstrapComplete, "ms");

// Histograms — track distributions, not just averages
const { createHistogram } = require("node:perf_hooks");
const hist = createHistogram();
hist.record(123);
hist.record(456);
console.log(hist.min, hist.max, hist.mean, hist.percentile(99));</code></pre>
<p><strong>Why it matters:</strong> <code>Date.now()</code> only has millisecond precision. <code>performance.now()</code> has sub-millisecond precision and is monotonic (isn't affected by clock adjustments). Essential for accurate profiling.</p>
<p><strong>Use cases:</strong> benchmarking functions, measuring request handling latency, detecting event-loop stalls, exposing custom metrics to monitoring systems (Prometheus, Datadog).</p>
'''

ANSWERS[74] = r'''
<p>Basic timing is simple — wrap code in <code>performance.now()</code> calls. For reusable measurements, use marks and measures. For continuous monitoring, use observers.</p>
<pre><code>const { performance, PerformanceObserver } = require("node:perf_hooks");

// 1. SIMPLE TIMING
const start = performance.now();
expensiveOperation();
console.log(`took ${(performance.now() - start).toFixed(2)} ms`);

// 2. TIMING AN ASYNC FUNCTION — measure() auto-computes duration
async function timed(fn, label) {
  performance.mark(`${label}-start`);
  const result = await fn();
  performance.mark(`${label}-end`);
  performance.measure(label, `${label}-start`, `${label}-end`);
  return result;
}

await timed(() =&gt; db.query("SELECT ..."), "db-query");

// 3. CONTINUOUS OBSERVATION — get notified as measures happen
const observer = new PerformanceObserver((items) =&gt; {
  for (const entry of items.getEntries()) {
    metrics.histogram(`${entry.name}.duration`, entry.duration);
  }
});
observer.observe({ entryTypes: ["measure"] });

// 4. TIMING FUNCTIONS — wrap a function once, measure every call
const { performance: perf } = require("node:perf_hooks");

function timeFunction(fn, name = fn.name) {
  const wrapped = perf.timerify(fn);
  return wrapped;
}

const slowFn = () =&gt; { for (let i = 0; i &lt; 1e7; i++) Math.sqrt(i); };
const slowTimed = timeFunction(slowFn, "slowFn");

new PerformanceObserver((items) =&gt; {
  items.getEntries().forEach(e =&gt; console.log(e.name, e.duration));
}).observe({ entryTypes: ["function"] });

slowTimed();   // logs: slowFn &lt;ms&gt;

// 5. HTTP TIMING — Node automatically records these
const httpObs = new PerformanceObserver((items) =&gt; {
  items.getEntries().forEach(e =&gt; {
    console.log(`HTTP ${e.name}: ${e.duration} ms`);
  });
});
httpObs.observe({ entryTypes: ["http"] });

// 6. DETECT SLOW EVENT LOOP
const monitorEventLoop = () =&gt; {
  const last = performance.eventLoopUtilization();
  return setInterval(() =&gt; {
    const current = performance.eventLoopUtilization(last);
    if (current.utilization &gt; 0.9) {
      console.warn("event loop is under stress");
    }
  }, 5000);
};</code></pre>
<p><strong>Practical tips:</strong> for monitoring services, push <code>performance.measure</code> durations to Prometheus or Datadog rather than logging. Histograms (<code>perf_hooks.createHistogram</code>) let you report percentiles (p50, p95, p99) instead of just averages.</p>
'''

ANSWERS[75] = r'''
<p>The <strong><code>trace_events</code></strong> module records detailed internal events for performance analysis and deep debugging. It produces <strong>Trace Event Format</strong> files viewable in Chrome DevTools' Performance or about:tracing.</p>
<p>Unlike <code>perf_hooks</code> (which you use to instrument your own code), <code>trace_events</code> captures what <strong>Node itself</strong> is doing — I/O, GC, V8 internals — at a very granular level.</p>
<pre><code>// Enable tracing via command line (easiest)
// node --trace-event-categories v8,node,node.async_hooks app.js
// Creates node_trace.&lt;pid&gt;.&lt;seq&gt;.log in cwd

// View in Chrome — open chrome://tracing, load the log file

// Available categories:
//   node                  — core Node events
//   node.async_hooks      — async resource creation/destruction
//   node.bootstrap        — startup timings
//   node.fs.sync          — sync fs operations
//   node.http             — HTTP server/client events
//   node.net.native       — native networking
//   node.perf             — performance hooks events
//   node.promises.rejections — unhandled rejections
//   v8                    — V8 engine events (GC, compilation)
//   v8.gc                 — just GC

// PROGRAMMATIC — enable/disable from code
const trace_events = require("node:trace_events");

const tracing = trace_events.createTracing({
  categories: ["node.http", "node.fs.sync"],
});

tracing.enable();
// ...run code you want traced...
tracing.disable();

// Check which categories are currently enabled
console.log(trace_events.getEnabledCategories());</code></pre>
<p><strong>When it's useful:</strong></p>
<ul>
  <li><strong>Diagnosing unexplained latency</strong> — see exactly what Node was doing during a slow request.</li>
  <li><strong>Profiling startup</strong> — trace what happens during bootstrap.</li>
  <li><strong>GC pressure analysis</strong> — see when and how long GC pauses occur.</li>
  <li><strong>Debugging production issues</strong> — enable briefly in production to capture a problem you can't reproduce locally.</li>
</ul>
<p><strong>Caveats:</strong> tracing is <strong>expensive</strong> — enabling broad categories in production can noticeably slow the app. Use targeted categories and enable only for short periods. The output files get large fast (hundreds of MB for busy apps over minutes).</p>
<p>Most day-to-day performance work is better served by <code>perf_hooks</code>, CPU profiles, and flame graphs. Reach for <code>trace_events</code> when other tools don't give you enough depth.</p>
'''

ANSWERS[76] = r'''
<p>Tracing captures detailed internal events — I/O calls, GC pauses, HTTP lifecycle, promise rejections — so you can analyze them in Chrome's tracing viewer. Two main approaches: command-line flags (simplest) or programmatic control (targeted).</p>
<pre><code>// METHOD 1 — command-line flags
// node --trace-events-enabled --trace-event-categories v8,node.http app.js

// Categories worth knowing:
//   v8                      — JavaScript execution and compilation
//   v8.gc                   — just garbage collection
//   node                    — general Node events
//   node.http               — HTTP server/client
//   node.async_hooks        — async resource tracking
//   node.promises.rejections — unhandled Promise rejections
//   node.perf               — performance observer events
//   node.fs.sync            — synchronous fs calls (useful for finding blockers!)

// Produces node_trace.&lt;pid&gt;.&lt;seq&gt;.log files

// METHOD 2 — programmatic, enable only for a specific window
const trace_events = require("node:trace_events");

function traceWindow(categories, fn) {
  const tracing = trace_events.createTracing({ categories });
  tracing.enable();
  try { return fn(); }
  finally { tracing.disable(); }
}

// Trace a suspected slow endpoint
app.get("/slow", async (req, res) =&gt; {
  await traceWindow(["node.http", "v8.gc"], async () =&gt; {
    const data = await heavyWork();
    res.json(data);
  });
});

// METHOD 3 — viewing traces
// 1. Open Chrome / Edge
// 2. Navigate to chrome://tracing  (or edge://tracing)
// 3. Click "Load" and pick node_trace.*.log
// 4. You'll see a flame chart — zoom / pan to investigate

// ALTERNATIVE — convert to other formats
// The trace file is Chromium Trace Event JSON, which also loads in:
// - Perfetto (https://ui.perfetto.dev) — modern alternative to about:tracing
// - speedscope.app — flame graph viewer

// EXAMPLE — inspecting synchronous fs calls that are blocking
// node --trace-event-categories node.fs.sync app.js
// Load the output and you'll see every readFileSync, writeFileSync, statSync call
// with exact timestamps</code></pre>
<p><strong>Practical workflow:</strong></p>
<ol>
  <li>Identify a suspected problem area (slow endpoint, memory spike, GC pauses).</li>
  <li>Enable tracing for just the relevant categories, ideally for a short window.</li>
  <li>Load the trace in Perfetto or Chrome for visual analysis.</li>
  <li>Look for long spans, frequent GC, or unexpected sync I/O.</li>
</ol>
<p>For simpler needs, <code>perf_hooks</code> + an APM (Datadog, New Relic) gives you 90% of the insight with far less overhead.</p>
'''

ANSWERS[77] = r'''
<p>The <strong><code>vm</code></strong> module runs JavaScript code in a <strong>separate V8 context</strong> — isolated from the calling code's globals, with its own global object. It's the engine behind Node's REPL, and useful when you need to evaluate user-provided code, build a template engine, or sandbox untrusted scripts.</p>
<pre><code>const vm = require("node:vm");

// Simple evaluation — runs code in a new context
const result = vm.runInNewContext("2 + 3 * 4");
console.log(result);       // 14

// Create a context with specific globals available
const sandbox = { x: 10, log: console.log };
vm.createContext(sandbox);
vm.runInContext("log('x squared is', x * x)", sandbox);
// x squared is 100

// Values go IN via the context object, come OUT the same way
vm.runInContext("result = x * 2", sandbox);
console.log(sandbox.result);    // 20

// Compile once, run many times — faster for repeated execution
const script = new vm.Script("Math.sqrt(n)");
for (let n = 1; n &lt;= 5; n++) {
  console.log(script.runInNewContext({ Math, n }));
}

// Timeouts — prevent runaway scripts
try {
  vm.runInNewContext("while (true) {}", {}, { timeout: 100 });
} catch (err) {
  console.error("script timed out");
}

// IMPORTANT: vm is NOT a real sandbox against malicious code.
// A determined attacker can break out using prototype tricks:
//   const AsyncFunction = (async function(){}).constructor;
//   AsyncFunction("return this.constructor.constructor('return process')()")()
// For untrusted code, use worker_threads with a hardened context,
// or run in a subprocess with OS-level isolation.</code></pre>
<p><strong>Common uses:</strong></p>
<ul>
  <li><strong>Template engines</strong> — compile <code>&lt;%= expr %&gt;</code> expressions once, run per render.</li>
  <li><strong>Custom REPLs</strong> — build your own interactive shell.</li>
  <li><strong>Plugin systems</strong> — load user plugins with a restricted set of globals.</li>
  <li><strong>Testing</strong> — run code with mocked globals.</li>
</ul>
<p>For real sandboxing against hostile code, use <strong>isolated-vm</strong> (npm), a subprocess with <code>ulimit</code>, or a proper sandbox like <strong>Deno</strong>'s permissions model. <code>vm</code> alone is <em>not</em> a security boundary.</p>
'''

ANSWERS[78] = r'''
<p>"Virtual machine context" here means a fresh V8 execution environment — a new global object, isolated from the calling code. The <code>vm</code> module provides three flavors: new context every time, a persistent context, or the current context.</p>
<pre><code>const vm = require("node:vm");

// 1. runInNewContext — cheap, one-shot evaluation
const answer = vm.runInNewContext("40 + 2");   // 42

// 2. runInContext — runs in a PRE-EXISTING context, preserving state
const context = vm.createContext({ counter: 0 });
vm.runInContext("counter++", context);
vm.runInContext("counter++", context);
console.log(context.counter);    // 2

// 3. runInThisContext — runs in the CURRENT context (like eval, but no scope access)
const x = 100;
vm.runInThisContext("console.log(typeof x)");   // "undefined" — no scope access!

// COMPILING ONCE, RUNNING MANY TIMES
const script = new vm.Script(`
  function fib(n) { return n &lt; 2 ? n : fib(n - 1) + fib(n - 2); }
  result = fib(n);
`);

const results = [];
for (let n = 10; n &lt; 20; n++) {
  const ctx = { n };
  vm.createContext(ctx);
  script.runInContext(ctx);
  results.push(ctx.result);
}

// PROVIDE SPECIFIC GLOBALS — build a safe-ish execution environment
function runUserScript(source, allowedGlobals) {
  const ctx = {
    // Explicitly allowlisted APIs
    console: { log: (...args) =&gt; console.log("[user]", ...args) },
    Math,
    Array,
    Object,
    JSON,
    ...allowedGlobals,
  };
  vm.createContext(ctx);

  const script = new vm.Script(source, {
    filename: "user-script.js",    // shows in stack traces
    lineOffset: 0,
  });

  return script.runInContext(ctx, {
    timeout: 1000,                  // max 1 second
    displayErrors: true,
  });
}

// SOURCE MAPS — useful when transpiling before running
new vm.Script("const x = 1;", { cachedData: Buffer.from(/*...*/) });</code></pre>
<p><strong>Real-world example — a calculator that supports user formulas:</strong></p>
<pre><code>function evaluateFormula(expr, variables) {
  try {
    return vm.runInNewContext(expr, { ...variables, Math }, {
      timeout: 100,
      displayErrors: false,
    });
  } catch (err) {
    throw new Error(`Invalid formula: ${err.message}`);
  }
}

evaluateFormula("price * quantity * (1 - discount)", {
  price: 9.99, quantity: 3, discount: 0.1,
});   // 26.973</code></pre>
<p><strong>Remember:</strong> contexts isolate globals, not security. For truly untrusted code, use <strong>isolated-vm</strong> or process isolation.</p>
'''

ANSWERS[79] = r'''
<p>The <strong><code>repl</code></strong> module powers Node's interactive shell — the <code>&gt;</code> prompt you see when you type <code>node</code> with no arguments. It stands for <strong>Read-Eval-Print Loop</strong>: read a line of input, evaluate it, print the result, loop.</p>
<p>Beyond the default shell, you can embed a REPL in your own apps for debugging, admin consoles, or plugin sandboxes.</p>
<pre><code>const repl = require("node:repl");

// BASIC — start a REPL in the current process
const r = repl.start({
  prompt: "myapp&gt; ",
  input: process.stdin,
  output: process.stdout,
  useColors: true,
  useGlobal: false,           // true = share globals with host process
});

// Inject variables / helpers the user can access
r.context.db = require("./database");
r.context.app = require("./app");
r.context.help = () =&gt; console.log("Available: db, app, user(id)");
r.context.user = (id) =&gt; db.users.findById(id);

// Save history to a file (like bash)
r.setupHistory(".myapp_repl_history", (err) =&gt; {
  if (err) console.error("history load failed:", err);
});

// Listen for exit
r.on("exit", () =&gt; {
  console.log("goodbye!");
  process.exit(0);
});

// CUSTOM EVALUATOR — REPL that interprets custom syntax
const customRepl = repl.start({
  prompt: "sql&gt; ",
  eval: async (cmd, context, filename, callback) =&gt; {
    try {
      const result = await db.query(cmd.trim());
      callback(null, result);
    } catch (err) {
      callback(err);
    }
  },
});

// NETWORK REPL — connect via TCP for remote debugging
const net = require("node:net");
net.createServer((socket) =&gt; {
  repl.start({
    prompt: "remote&gt; ",
    input: socket,
    output: socket,
  }).on("exit", () =&gt; socket.end());
}).listen(5001);
// Connect with: telnet localhost 5001</code></pre>
<p><strong>Uses:</strong></p>
<ul>
  <li><strong>Development REPL</strong> — quick experimentation without writing a file.</li>
  <li><strong>Admin console</strong> — add a REPL in your server so you can interact with live objects (inspect caches, trigger jobs).</li>
  <li><strong>Learning / tutorials</strong> — embedded sandboxes in docs.</li>
  <li><strong>Framework CLI</strong> — Rails has <code>rails console</code>; Laravel has <code>artisan tinker</code> — Node apps can offer the same.</li>
</ul>
<p><strong>Security:</strong> a REPL executes arbitrary code. Never expose one on a public network without strong authentication. The network REPL example above is fine on localhost / dev; wrap it in auth + TLS for anything public.</p>
'''

ANSWERS[80] = r'''
<p>The simplest REPL session is just running <code>node</code> with no arguments. For richer setups — custom prompts, globals, history, remote access — use the programmatic API.</p>
<pre><code>// SIMPLEST — command line
// $ node
// &gt; 1 + 1
// 2
// &gt; .help      // lists commands: .break .clear .editor .exit .help .load .save
// &gt; .exit

// With a preload script — nice for experimenting with libraries
// $ node -r ./setup.js

// PROGRAMMATIC — start a REPL inside your app
const repl = require("node:repl");

const server = repl.start({
  prompt: "app&gt; ",
});

// Make utilities available
server.context.greet = (name) =&gt; `Hello, ${name}!`;
server.context.env = process.env;

// User experience:
//   app&gt; greet("Ada")
//   'Hello, Ada!'
//   app&gt; env.NODE_ENV
//   'development'

// WITH HISTORY — survives restarts
server.setupHistory("/tmp/myapp.repl.history", (err) =&gt; {
  if (err) console.error(err);
});

// CUSTOM COMMANDS (starts with . like built-in ones)
server.defineCommand("restart", {
  help: "Restart the app",
  action() {
    this.clearBufferedCommand();
    console.log("restarting...");
    process.exit(0);
  },
});

// Access to last printed value is stored in "_"
// app&gt; 1 + 1
// 2
// app&gt; _ * 3
// 6

// ON-DEMAND REPL via signal — production debugging technique
process.on("SIGUSR2", () =&gt; {
  console.log("starting REPL on port 5001");
  const net = require("node:net");
  net.createServer((socket) =&gt; {
    const r = repl.start({ prompt: "&gt; ", input: socket, output: socket });
    r.context.server = httpServer;    // expose live objects
    r.context.db = db;
  }).listen(5001, "127.0.0.1");       // localhost ONLY
});

// Then: kill -SIGUSR2 &lt;pid&gt;
// Then: telnet localhost 5001</code></pre>
<p><strong>Built-in REPL commands</strong> (start with <code>.</code>):</p>
<ul>
  <li><strong><code>.help</code></strong> — list all commands.</li>
  <li><strong><code>.editor</code></strong> — multi-line editor mode (Ctrl-D to evaluate).</li>
  <li><strong><code>.load &lt;file&gt;</code></strong> — load a JS file into the session.</li>
  <li><strong><code>.save &lt;file&gt;</code></strong> — save the session to a file.</li>
  <li><strong><code>.clear</code></strong> — reset the context.</li>
  <li><strong><code>.exit</code></strong> — quit (Ctrl-D also works).</li>
</ul>
<p><strong>Pro tip:</strong> <code>node --experimental-repl-await</code> (or newer Node versions by default) let you <code>await</code> directly at the REPL prompt — no wrapping in <code>async</code> IIFE needed.</p>
'''

ANSWERS[81] = r'''
<p>The <strong><code>inspector</code></strong> module embeds the Chrome DevTools Protocol (CDP) — the same protocol that powers Chrome's DevTools — directly into your Node process. Beyond the usual "attach a debugger" use case, it opens up programmatic access to CPU profiling, heap snapshots, coverage collection, and runtime evaluation.</p>
<pre><code>const inspector = require("node:inspector");

// Quick check — is an inspector currently open?
console.log(inspector.url());        // "ws://..." or undefined

// Open programmatically on demand (useful for production diagnostics)
inspector.open(9229, "127.0.0.1", false);
//   port, host, wait-for-debugger?

// Close when done
inspector.close();

// THE POWERFUL PART — open a SESSION and speak CDP directly
const session = new inspector.Session();
session.connect();

// Example 1 — CPU profile programmatically
async function captureCpuProfile(durationMs) {
  await new Promise((r) =&gt; session.post("Profiler.enable", r));
  await new Promise((r) =&gt; session.post("Profiler.start", r));

  await new Promise((r) =&gt; setTimeout(r, durationMs));

  const { profile } = await new Promise((resolve) =&gt; {
    session.post("Profiler.stop", (err, res) =&gt; resolve(res));
  });

  return profile;   // save as .cpuprofile, open in DevTools Performance tab
}

// Trigger via a signal to capture in production
process.on("SIGUSR2", async () =&gt; {
  const profile = await captureCpuProfile(10_000);
  require("node:fs").writeFileSync(
    `/tmp/cpu-${Date.now()}.cpuprofile`,
    JSON.stringify(profile),
  );
  console.log("profile saved");
});

// Example 2 — heap snapshot
function takeHeapSnapshot(path) {
  return new Promise((resolve, reject) =&gt; {
    const fd = require("node:fs").openSync(path, "w");
    session.on("HeapProfiler.addHeapSnapshotChunk", (msg) =&gt; {
      require("node:fs").writeSync(fd, msg.params.chunk);
    });
    session.post("HeapProfiler.takeHeapSnapshot", null, (err) =&gt; {
      require("node:fs").closeSync(fd);
      err ? reject(err) : resolve();
    });
  });
}</code></pre>
<p><strong>Power users</strong> use the programmatic API to build custom tools: APM agents that take automatic profiles, diagnostic endpoints for on-demand memory dumps, integration with coverage tools, debugger frontends.</p>
<p><strong>Day-to-day developers</strong> rarely touch the raw API — they use <code>node --inspect</code> with VS Code or Chrome DevTools. But knowing it exists is useful for production diagnostics when SSH-ing into a box is impractical or attaching a debugger would violate SLAs.</p>
'''

ANSWERS[82] = r'''
<p>Several practical workflows for debugging with the inspector:</p>
<pre><code>// WORKFLOW 1 — Local development with VS Code
// Just add .vscode/launch.json:
//
// {
//   "version": "0.2.0",
//   "configurations": [
//     {
//       "type": "node",
//       "request": "launch",
//       "name": "Debug app",
//       "program": "${workspaceFolder}/index.js",
//       "skipFiles": ["&lt;node_internals&gt;/**"]
//     }
//   ]
// }
//
// Hit F5 to run — set breakpoints by clicking in the gutter.

// WORKFLOW 2 — Chrome DevTools
// Start:   node --inspect app.js
// Open:    chrome://inspect in Chrome
// Click "inspect" under your target. Use Sources panel for breakpoints,
// Performance for CPU profiles, Memory for heap snapshots.

// WORKFLOW 3 — Break before the first line
// node --inspect-brk app.js
// App pauses on line 1; you can set breakpoints and step through startup.

// WORKFLOW 4 — Attaching to a RUNNING production process
// On the server:
//   node app.js                     # running normally
//
// Then trigger inspector:
//   kill -SIGUSR1 &lt;pid&gt;             # opens port 9229 on localhost
//
// From your local machine — forward the port over SSH:
//   ssh -L 9229:localhost:9229 user@server
//
// In Chrome — chrome://inspect → Configure → add "localhost:9229"
// Now you can profile or debug the production process without restarting it.

// WORKFLOW 5 — debugger; statement
// Add `debugger;` in your code. When debugger is attached, execution
// pauses there. No need to set breakpoints by file/line.
function problematicFunction(data) {
  debugger;
  return data.map(/*...*/);
}

// WORKFLOW 6 — Conditional breakpoints (VS Code / DevTools)
// Right-click the breakpoint → "Edit Breakpoint" → enter condition
// Example condition: user.id === 42
// Only pauses when the condition is true.

// WORKFLOW 7 — Logpoints — observability without code changes
// Right-click gutter → "Add Logpoint" → type a message
// Example: "processing user {user.id}, balance {user.balance}"
// Logs without pausing. Use for temporary instrumentation.

// WORKFLOW 8 — Async debugging
// The debugger shows you an "Async" call stack — the chain of awaits
// leading to the current point. Invaluable for tracking down bugs
// deep in async code.</code></pre>
<p><strong>Security reminders for production:</strong></p>
<ul>
  <li><strong>Never</strong> bind the inspector to <code>0.0.0.0</code>. Always localhost + SSH tunnel.</li>
  <li>A debugger can run arbitrary code in your process. Treat inspector access like SSH access.</li>
  <li>Remove <code>debugger;</code> statements before shipping. Use a linter rule (ESLint's <code>no-debugger</code>).</li>
</ul>
<p><strong>For async-heavy apps,</strong> the built-in Node debugger (<code>node inspect</code>) is cumbersome. Use VS Code or Chrome DevTools — they provide much better support for Promises, async/await, and source maps.</p>
'''

ANSWERS[83] = r'''
<p>The <strong><code>buffer</code></strong> module provides the <strong><code>Buffer</code></strong> class, a representation of raw binary data outside the V8 heap. It's global (you don't need to require it) but the module itself has additional utilities.</p>
<p><strong>Why it exists:</strong> before TypedArrays were standard in JavaScript, Node needed to handle binary data efficiently — network packets, files, crypto operations, image bytes. Buffers filled that gap, and remain the idiomatic way to handle binary in Node.</p>
<pre><code>// Buffer is GLOBAL — no require needed for the class
const buf = Buffer.from("hello");

// The module adds extra utilities
const { Blob, constants, kMaxLength, transcode } = require("node:buffer");

// constants — limits imposed by the runtime
constants.MAX_LENGTH;           // largest allowable Buffer
constants.MAX_STRING_LENGTH;    // largest allowable string

// transcode — convert between character encodings
const buf2 = transcode(Buffer.from("€"), "utf8", "latin1");
// If the target encoding can't represent a character, it's replaced with ?

// Blob — matches the web Blob API (Node 18+)
const blob = new Blob(["hello"], { type: "text/plain" });
console.log(blob.size, blob.type);

// Also includes file-like behavior
const text = await blob.text();
const bytes = await blob.arrayBuffer();

// atob / btoa — base64 helpers
Buffer.from("hello").toString("base64");   // "aGVsbG8="
Buffer.from("aGVsbG8=", "base64").toString();  // "hello"

// Or globally:
btoa("hello");                  // "aGVsbG8="
atob("aGVsbG8=");               // "hello"</code></pre>
<p><strong>When you'll encounter Buffers:</strong></p>
<ul>
  <li><strong>Reading files</strong> without an encoding — <code>fs.readFile("x.png")</code> returns a Buffer.</li>
  <li><strong>Stream chunks</strong> — network data arrives as Buffers by default.</li>
  <li><strong>Crypto</strong> — hashes, keys, ciphertexts.</li>
  <li><strong>Binary protocols</strong> — TCP, WebSocket frames, protobuf.</li>
  <li><strong>Image processing</strong> — raw pixel data.</li>
</ul>
<p><strong>Modern alternative:</strong> the standard <strong><code>Uint8Array</code></strong> / <strong><code>ArrayBuffer</code></strong> work in both Node and browsers. Most Node APIs accept either. <code>Buffer</code> is a subclass of <code>Uint8Array</code> with extra methods (encoding, base64, etc.). For new code that targets both environments, prefer <code>Uint8Array</code>; for Node-only code, <code>Buffer</code> is fine and often ergonomically nicer.</p>
'''

ANSWERS[84] = r'''
<p>Several ways to create a Buffer depending on your source data. Know the difference between <code>alloc</code> and <code>allocUnsafe</code> — it matters for security.</p>
<pre><code>// FROM A STRING
Buffer.from("hello");                    // UTF-8 by default
Buffer.from("hello", "utf-8");
Buffer.from("68656c6c6f", "hex");        // from hex
Buffer.from("aGVsbG8=", "base64");       // from base64
Buffer.from("hello", "latin1");          // from latin1 / binary

// FROM AN ARRAY OF BYTES
Buffer.from([72, 101, 108, 108, 111]);   // "Hello"

// FROM ANOTHER BUFFER / TYPED ARRAY
const a = Buffer.from("hello");
const b = Buffer.from(a);                // COPY

const arr = new Uint8Array([1, 2, 3]);
Buffer.from(arr.buffer);                 // share underlying memory
Buffer.from(arr);                        // copy

// ALLOCATE A NEW BUFFER
Buffer.alloc(10);                        // 10 bytes, all zeroed — SAFE
Buffer.alloc(10, "a");                   // 10 bytes filled with "a"
Buffer.allocUnsafe(10);                  // 10 bytes, UNINITIALIZED — FASTER but may leak memory
Buffer.allocUnsafeSlow(10);              // bypass the pool (for long-lived buffers)

// DO NOT USE — deprecated/unsafe constructor
// new Buffer(10);           ← deprecated; returns uninitialized bytes, can leak secrets
// new Buffer("hello");      ← deprecated

// INSPECTING A BUFFER
const buf = Buffer.from("Hello, world!");
buf.length;                              // 13 (bytes, not characters)
buf[0];                                  // 72 (the "H" byte)
buf.toString();                          // "Hello, world!"
buf.toString("hex");                     // "48656c6c6f2c20776f726c6421"
buf.toString("base64");                  // "SGVsbG8sIHdvcmxkIQ=="
buf.toString("utf-8", 0, 5);             // "Hello"  (slice before decode)

// WRITING TO A BUFFER
const b2 = Buffer.alloc(16);
b2.write("Node.js", 0, "utf-8");         // write at offset 0
b2.writeUInt32BE(12345, 8);              // write 32-bit unsigned int at offset 8

// READING TYPED VALUES
const b3 = Buffer.from([0x00, 0x00, 0x00, 0x2a]);
b3.readUInt32BE(0);                      // 42

// CONCAT — join multiple buffers
Buffer.concat([Buffer.from("Hello "), Buffer.from("world")]);

// COMPARE
Buffer.compare(Buffer.from("a"), Buffer.from("b"));   // -1
Buffer.from("abc").equals(Buffer.from("abc"));        // true</code></pre>
<p><strong>Safe vs unsafe allocation:</strong> <code>Buffer.allocUnsafe(n)</code> is faster because it doesn't zero the memory, but the bytes may contain data from previously-freed buffers (including secrets). Only use it when you'll immediately overwrite every byte. For anything you'll expose or log, use <code>Buffer.alloc(n)</code>.</p>
'''

ANSWERS[85] = r'''
<p>The <strong><code>stream</code></strong> module provides the base classes and utilities for Node's streaming I/O — the abstraction behind file reads, HTTP request/response, sockets, compression, and encryption. Streams let you process data in chunks instead of loading it all into memory.</p>
<p><strong>Four stream types:</strong></p>
<ul>
  <li><strong>Readable</strong> — source of data (<code>fs.createReadStream</code>, <code>http.IncomingMessage</code>).</li>
  <li><strong>Writable</strong> — destination for data (<code>fs.createWriteStream</code>, <code>http.ServerResponse</code>).</li>
  <li><strong>Duplex</strong> — both (TCP sockets, WebSocket frames).</li>
  <li><strong>Transform</strong> — duplex that modifies data on the way through (gzip, encryption, hashing).</li>
</ul>
<pre><code>const stream = require("node:stream");
const fs = require("node:fs");
const zlib = require("node:zlib");
const { pipeline } = require("node:stream/promises");

// BASIC PIPING — the simplest, most common use
// Read → transform → write, with backpressure handled automatically
fs.createReadStream("input.txt")
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream("input.txt.gz"));

// PIPELINE — modern, Promise-based, handles errors properly
await pipeline(
  fs.createReadStream("input.txt"),
  zlib.createGzip(),
  fs.createWriteStream("input.txt.gz"),
);
// Any stream's error propagates; all streams are cleaned up on failure

// CUSTOM TRANSFORM — uppercase every chunk
const upper = new stream.Transform({
  transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  },
});

await pipeline(
  fs.createReadStream("hello.txt"),
  upper,
  fs.createWriteStream("HELLO.txt"),
);

// CUSTOM READABLE — generate data on demand
class Counter extends stream.Readable {
  constructor(max) { super(); this.n = 0; this.max = max; }
  _read() {
    if (this.n &gt;= this.max) this.push(null);      // end of stream
    else this.push(`${++this.n}\n`);
  }
}
new Counter(5).pipe(process.stdout);   // prints 1..5

// CUSTOM WRITABLE
class Logger extends stream.Writable {
  _write(chunk, encoding, callback) {
    console.log("got:", chunk.toString());
    callback();
  }
}

// ASYNC ITERATION — the modern ergonomic way to read streams
for await (const chunk of fs.createReadStream("big.log")) {
  processChunk(chunk);
}</code></pre>
<p><strong>Backpressure:</strong> streams automatically pause when the consumer is slower than the producer. That's why piping a 100 GB file to a slow disk doesn't explode memory — the reader throttles to match the writer. Custom streams should respect <code>.write()</code> return values and the <code>"drain"</code> event.</p>
<p>Most production code uses <code>pipeline()</code> — it handles errors and cleanup correctly, which is tricky to get right manually.</p>
'''

ANSWERS[86] = r'''
<p>Two approaches: create a readable stream from an existing source (a file, a generator), or subclass <code>Readable</code> for custom data.</p>
<pre><code>const { Readable } = require("node:stream");
const fs = require("node:fs");

// 1. FROM A FILE — most common case
const fileStream = fs.createReadStream("big.log", {
  encoding: "utf-8",         // strings instead of Buffers
  highWaterMark: 64 * 1024,  // 64 KB chunks (default)
});

fileStream.on("data", (chunk) =&gt; console.log(chunk.length));
fileStream.on("end",  ()      =&gt; console.log("done"));

// 2. FROM AN ARRAY OR ITERABLE — Readable.from()
const arrStream = Readable.from(["one\n", "two\n", "three\n"]);
arrStream.pipe(process.stdout);

// Works with any iterable — arrays, sets, generators
function* numbers() {
  for (let i = 0; i &lt; 5; i++) yield `${i}\n`;
}
Readable.from(numbers()).pipe(process.stdout);

// Works with async iterables
async function* fetchPages() {
  for (let page = 1; page &lt;= 10; page++) {
    const res = await fetch(`https://api.example.com/?page=${page}`);
    yield JSON.stringify(await res.json()) + "\n";
  }
}
Readable.from(fetchPages()).pipe(fs.createWriteStream("all.json"));

// 3. SUBCLASS Readable — full control
class CounterStream extends Readable {
  constructor(max, opts) {
    super(opts);
    this.n = 0;
    this.max = max;
  }

  // _read is called when the consumer wants more data
  _read() {
    if (this.n &gt;= this.max) {
      this.push(null);          // null = end of stream
    } else {
      this.push(`Number ${++this.n}\n`);
    }
  }
}

new CounterStream(5).pipe(process.stdout);
// Number 1
// Number 2
// Number 3
// Number 4
// Number 5

// 4. OBJECT MODE — stream arbitrary objects instead of Buffers/strings
const objStream = new Readable({
  objectMode: true,
  read() { this.push({ id: Math.random() }); },
});
// Each chunk is a whole object — useful for database cursors, message queues

// 5. ASYNC ITERATION — the modern way to CONSUME readables
for await (const chunk of fs.createReadStream("log.txt")) {
  // chunk is a Buffer (or string if encoding set)
  if (chunk.toString().includes("ERROR")) {
    console.log("found error!");
  }
}</code></pre>
<p><strong>Key concepts:</strong></p>
<ul>
  <li><strong><code>highWaterMark</code></strong> — internal buffer size. Larger = fewer <code>_read()</code> calls + more memory.</li>
  <li><strong>Object mode</strong> — yield objects instead of binary. Great for streams of records.</li>
  <li><strong>Paused vs flowing</strong> — streams start paused. <code>.pipe()</code> or <code>on("data")</code> starts them flowing. <code>.pause()</code> / <code>.resume()</code> toggles.</li>
  <li><strong>Always handle <code>"error"</code></strong> — a readable with no error handler crashes the process.</li>
</ul>
'''

ANSWERS[87] = r'''
<p>The <strong><code>net</code></strong> module provides raw TCP networking — both client and server. It's the layer beneath HTTP: when you call <code>http.createServer</code>, it's using a <code>net.Server</code> under the hood. Reach for <code>net</code> directly when you're implementing a custom protocol (not HTTP).</p>
<pre><code>const net = require("node:net");

// TCP SERVER
const server = net.createServer((socket) =&gt; {
  // socket is a Duplex stream — read and write
  console.log("client connected from", socket.remoteAddress, socket.remotePort);

  socket.write("Welcome!\n");

  socket.on("data", (data) =&gt; {
    console.log("received:", data.toString().trim());
    socket.write(`Echo: ${data}`);
  });

  socket.on("end", () =&gt; console.log("client disconnected"));
  socket.on("error", (err) =&gt; console.error("socket error:", err));
});

server.listen(3000, "127.0.0.1", () =&gt; {
  console.log("TCP server on port 3000");
});

// TCP CLIENT
const client = net.createConnection({ port: 3000 }, () =&gt; {
  console.log("connected!");
  client.write("Hello, server!");
});

client.on("data", (data) =&gt; {
  console.log("from server:", data.toString());
});

client.on("end", () =&gt; console.log("disconnected"));

// UNIX DOMAIN SOCKETS — for inter-process communication on the same machine
net.createServer(handler).listen("/tmp/my-sock");
net.createConnection({ path: "/tmp/my-sock" });

// BINDING TO AN AVAILABLE PORT (0 = assign one)
server.listen(0, () =&gt; {
  console.log("listening on port", server.address().port);
});</code></pre>
<p><strong>When to use <code>net</code> directly:</strong></p>
<ul>
  <li><strong>Custom binary protocols</strong> — MQTT, Redis RESP, your own game protocol.</li>
  <li><strong>Proxies</strong> — a <code>net.Server</code> can accept connections and forward them to another host.</li>
  <li><strong>Low-level diagnostics</strong> — port scanners, connectivity testers.</li>
  <li><strong>Simple IPC</strong> — Unix domain sockets for services on the same machine.</li>
</ul>
<p><strong>Companion modules:</strong></p>
<ul>
  <li><code>tls</code> — like <code>net</code> but over TLS (encrypted TCP).</li>
  <li><code>dgram</code> — UDP (connectionless, packet-based).</li>
  <li><code>http</code> / <code>http2</code> — higher-level, built on <code>net</code>.</li>
</ul>
<p>For the vast majority of applications, you'll use <code>http</code> or a WebSocket library — not raw TCP. But understanding <code>net</code> is valuable for debugging network issues and building protocol implementations.</p>
'''

ANSWERS[88] = r'''
<p>A TCP server accepts connections, reads incoming data as a byte stream, and writes responses. Each connection is a <code>net.Socket</code> — a duplex stream (readable + writable).</p>
<pre><code>const net = require("node:net");

// ECHO SERVER — sends back whatever it receives
const server = net.createServer((socket) =&gt; {
  console.log(`client: ${socket.remoteAddress}:${socket.remotePort}`);

  socket.on("data", (data) =&gt; socket.write(data));    // echo back
  socket.on("end",  () =&gt; console.log("client disconnected"));
  socket.on("error", (err) =&gt; console.error(err));
});

server.listen(3000, () =&gt; console.log("listening on 3000"));

// LINE-BASED PROTOCOL — collect bytes until newline, then process
const lineServer = net.createServer((socket) =&gt; {
  let buffer = "";

  socket.on("data", (chunk) =&gt; {
    buffer += chunk.toString();
    let lineBreak;
    while ((lineBreak = buffer.indexOf("\n")) !== -1) {
      const line = buffer.slice(0, lineBreak);
      buffer = buffer.slice(lineBreak + 1);
      handleLine(socket, line);
    }
  });
});

function handleLine(socket, line) {
  if (line === "PING") socket.write("PONG\n");
  else if (line === "QUIT") socket.end("BYE\n");
  else socket.write(`UNKNOWN: ${line}\n`);
}

// TEST IT — from another terminal
// $ telnet localhost 3000
// &gt; PING
// &lt; PONG

// CONNECTION LIMITS &amp; ROBUSTNESS
server.maxConnections = 1000;           // hard cap
server.on("connection", (socket) =&gt; {
  socket.setTimeout(30_000);            // drop idle connections after 30s
  socket.on("timeout", () =&gt; socket.destroy());

  socket.setKeepAlive(true, 60_000);    // TCP keepalive probes
});

// GRACEFUL SHUTDOWN
let activeSockets = new Set();
server.on("connection", (s) =&gt; {
  activeSockets.add(s);
  s.on("close", () =&gt; activeSockets.delete(s));
});

process.on("SIGTERM", () =&gt; {
  server.close(() =&gt; console.log("server closed"));
  for (const s of activeSockets) s.end();   // let in-flight work finish
  setTimeout(() =&gt; {
    for (const s of activeSockets) s.destroy();   // force close stragglers
    process.exit(0);
  }, 30_000);
});</code></pre>
<p><strong>Important behaviors:</strong></p>
<ul>
  <li><strong>No message boundaries</strong> — TCP is a stream, not packets. A <code>socket.write("foo")</code> + <code>socket.write("bar")</code> may arrive on the other side as one <code>data</code> event with <code>"foobar"</code>, or two events — or split differently. Protocols layer frame delimiters (length prefix, newlines, null bytes).</li>
  <li><strong>Backpressure</strong> — <code>socket.write()</code> returns <code>false</code> if internal buffer is full. Wait for <code>"drain"</code> before writing more.</li>
  <li><strong>Always handle errors</strong> — unhandled socket errors crash the process.</li>
</ul>
'''

ANSWERS[89] = r'''
<p>The <strong><code>tls</code></strong> module is the TLS/SSL counterpart to <code>net</code> — provides the same TCP primitives but over an encrypted connection. It's what <code>https</code> uses under the hood and is the foundation for any custom secure protocol.</p>
<pre><code>const tls = require("node:tls");
const fs = require("node:fs");

// Server options — need certificate + private key
const serverOptions = {
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),

  // Optional — require clients to authenticate with their own cert (mTLS)
  ca: [fs.readFileSync("client-ca.crt")],
  requestCert: true,
  rejectUnauthorized: true,

  // Optional — restrict to modern TLS
  minVersion: "TLSv1.2",
  ciphers: "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256",
};

// TLS SERVER
const server = tls.createServer(serverOptions, (socket) =&gt; {
  console.log("secure client connected");
  console.log("cipher:", socket.getCipher());
  console.log("authorized:", socket.authorized);   // for mTLS

  if (socket.authorized) {
    const cert = socket.getPeerCertificate();
    console.log("client common name:", cert.subject.CN);
  }

  socket.write("Hello over TLS!\n");
  socket.pipe(socket);            // echo (encrypted round-trip)
});

server.listen(8443);

// TLS CLIENT
const client = tls.connect({
  port: 8443,
  host: "example.com",
  // For a self-signed cert (dev only):
  // rejectUnauthorized: false,

  // For mTLS — present a client certificate
  key:  fs.readFileSync("client.key"),
  cert: fs.readFileSync("client.crt"),
  ca:   [fs.readFileSync("server-ca.crt")],
}, () =&gt; {
  if (client.authorized) {
    console.log("server cert is valid");
    client.write("secret message\n");
  } else {
    console.error("server cert NOT trusted:", client.authorizationError);
    client.end();
  }
});

client.on("data", (data) =&gt; console.log(data.toString()));

// CHECK TLS CONFIG OF A REMOTE SERVER
const socket = tls.connect(443, "example.com", () =&gt; {
  console.log("protocol:", socket.getProtocol());
  console.log("cipher:", socket.getCipher());
  console.log("cert:", socket.getPeerCertificate());
});</code></pre>
<p><strong>When you'd use <code>tls</code> directly:</strong></p>
<ul>
  <li><strong>Custom secure protocols</strong> — MQTT over TLS, a proprietary binary protocol, encrypted chat.</li>
  <li><strong>Mutual TLS (mTLS)</strong> — service-to-service auth with certificates instead of API keys.</li>
  <li><strong>Certificate inspection / validation</strong> — tools that check cert chains, expiries, ciphers.</li>
</ul>
<p><strong>In practice:</strong> for HTTPS, use <code>https</code> (a thin wrapper over <code>tls</code>). For production TLS termination, use a reverse proxy or managed load balancer — it's rare to run <code>tls.createServer</code> directly in prod.</p>
'''

ANSWERS[90] = r'''
<p>A secure TCP server is just a TLS server — same shape as <code>net.createServer</code>, but with certificate options.</p>
<pre><code>const tls = require("node:tls");
const fs = require("node:fs");

// DEV CERTIFICATES — self-signed for local testing (browser will warn)
//
// openssl req -x509 -newkey rsa:2048 -nodes \
//   -keyout server.key -out server.crt -days 365 \
//   -subj "/CN=localhost"
//
// PRODUCTION CERTIFICATES — use Let's Encrypt / your cert authority

const options = {
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),

  // Support modern TLS only
  minVersion: "TLSv1.2",

  // Load intermediate certs if your cert chain has them
  // ca: fs.readFileSync("intermediate.crt"),
};

const server = tls.createServer(options, (socket) =&gt; {
  console.log(`connection: ${socket.remoteAddress}:${socket.remotePort}`);
  console.log(`  cipher: ${socket.getCipher().name}`);
  console.log(`  protocol: ${socket.getProtocol()}`);

  socket.write("Welcome to the secure server!\n");

  socket.on("data", (chunk) =&gt; {
    socket.write(`Echoing: ${chunk}`);
  });

  socket.on("end", () =&gt; console.log("client disconnected"));
  socket.on("error", (err) =&gt; console.error("socket error:", err.message));
});

server.listen(8443, () =&gt; {
  console.log("TLS server listening on :8443");
});

// TEST IT from the command line
// $ openssl s_client -connect localhost:8443
// (or)
// $ curl -k https://localhost:8443      # -k skips cert verification (dev only)

// MUTUAL TLS (mTLS) — require clients to present certificates
const mtlsServer = tls.createServer({
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),
  ca:   fs.readFileSync("client-ca.crt"),  // trust this CA for client certs
  requestCert: true,                        // ask the client for its cert
  rejectUnauthorized: true,                 // reject if the cert isn't trusted
}, (socket) =&gt; {
  const clientCert = socket.getPeerCertificate();
  console.log("authenticated as:", clientCert.subject.CN);

  socket.write(`Hello, ${clientCert.subject.CN}!\n`);
});

// SNI — serve different certs for different hostnames (like nginx virtual hosts)
const sniServer = tls.createServer({
  SNICallback: (servername, callback) =&gt; {
    if (servername === "a.example.com") {
      callback(null, tls.createSecureContext(certsForA));
    } else {
      callback(null, tls.createSecureContext(certsForDefault));
    }
  },
}, handler);</code></pre>
<p><strong>Production checklist:</strong></p>
<ul>
  <li>Use real certificates (Let's Encrypt is free and automated with <strong>certbot</strong> or <strong>acme.sh</strong>).</li>
  <li>Set <code>minVersion: "TLSv1.2"</code> — older versions have known vulnerabilities.</li>
  <li>Handle certificate renewal — certs expire, typically every 90 days. Reload without restart using <code>server.setSecureContext()</code>.</li>
  <li>For most web apps, terminate TLS at a reverse proxy (Nginx / Caddy) or managed load balancer. They handle cert rotation, OCSP, modern cipher suites.</li>
</ul>
'''

ANSWERS[91] = r'''
<p>The <strong><code>dgram</code></strong> module provides UDP networking. UDP (User Datagram Protocol) is connectionless, packet-based, and unreliable — messages can arrive out of order, multiple times, or not at all. What you give up in reliability, you gain in latency and simplicity.</p>
<p><strong>When UDP is the right choice:</strong></p>
<ul>
  <li><strong>Real-time telemetry / metrics</strong> — StatsD, Syslog, SNMP, DNS. Losing a packet is acceptable.</li>
  <li><strong>Gaming / VoIP</strong> — stale data is worse than no data; keep latency minimal.</li>
  <li><strong>Video streaming</strong> — small packet loss is imperceptible; retransmission would stall the stream.</li>
  <li><strong>Service discovery on local networks</strong> — multicast UDP (mDNS, Bonjour).</li>
  <li><strong>Broadcast</strong> — one message to many recipients on a LAN.</li>
</ul>
<pre><code>const dgram = require("node:dgram");

// UDP SERVER — a.k.a. "listener" (UDP has no connection setup)
const server = dgram.createSocket("udp4");

server.on("message", (msg, rinfo) =&gt; {
  console.log(`got ${msg.length} bytes from ${rinfo.address}:${rinfo.port}`);
  console.log("payload:", msg.toString());

  // Send a reply back
  const reply = Buffer.from("ACK");
  server.send(reply, rinfo.port, rinfo.address);
});

server.on("error", (err) =&gt; {
  console.error("server error:", err);
  server.close();
});

server.on("listening", () =&gt; {
  const addr = server.address();
  console.log(`UDP server on ${addr.address}:${addr.port}`);
});

server.bind(41234);

// UDP CLIENT — no "connection," just send to an address
const client = dgram.createSocket("udp4");
const message = Buffer.from("Hello, UDP!");

client.send(message, 41234, "localhost", (err) =&gt; {
  if (err) console.error(err);
  else console.log("sent");
});

// MULTICAST — one message to all subscribers
server.addMembership("224.0.0.114");           // multicast group
server.setMulticastTTL(128);
client.send(msg, 41234, "224.0.0.114");        // sends to all group members

// BROADCAST — one message to all hosts on the LAN
client.setBroadcast(true);
client.send(msg, 41234, "255.255.255.255");</code></pre>
<p><strong>Key differences from TCP:</strong></p>
<table>
  <thead><tr><th>Aspect</th><th>UDP (<code>dgram</code>)</th><th>TCP (<code>net</code>)</th></tr></thead>
  <tbody>
    <tr><td>Connection</td><td>None</td><td>Established</td></tr>
    <tr><td>Reliability</td><td>None — packets may be lost</td><td>Guaranteed delivery</td></tr>
    <tr><td>Ordering</td><td>None</td><td>In-order</td></tr>
    <tr><td>Message boundaries</td><td>Preserved (each send = one packet)</td><td>Stream — no boundaries</td></tr>
    <tr><td>Latency</td><td>Lower</td><td>Higher (handshake, retransmission)</td></tr>
    <tr><td>Multicast / broadcast</td><td>Yes</td><td>No</td></tr>
  </tbody>
</table>
<p>For most application code you want TCP. Reach for UDP when the specific properties above matter.</p>
'''

ANSWERS[92] = r'''
<p>UDP servers are simpler than TCP ones — no connection state, no streams, just messages. You bind a socket to a port and receive datagrams with their sender address.</p>
<pre><code>const dgram = require("node:dgram");

// BASIC UDP SERVER
const server = dgram.createSocket("udp4");      // or "udp6" for IPv6

server.on("listening", () =&gt; {
  const a = server.address();
  console.log(`UDP listening on ${a.address}:${a.port}`);
});

server.on("message", (msg, rinfo) =&gt; {
  // msg is a Buffer; rinfo has { address, port, family, size }
  console.log(`${rinfo.address}:${rinfo.port} sent: ${msg}`);

  // Respond to the sender
  server.send(`echo: ${msg}`, rinfo.port, rinfo.address);
});

server.on("error", (err) =&gt; {
  console.error("socket error:", err);
  server.close();
});

server.bind(41234);             // listen on port 41234 on all interfaces

// TEST IT from another terminal with netcat
// $ echo -n "hello" | nc -u -w1 localhost 41234

// PARSING A CUSTOM BINARY PROTOCOL (e.g., StatsD-like)
server.on("message", (msg, rinfo) =&gt; {
  // Example: "metric.name:value|type"
  const text = msg.toString("utf-8");
  const match = text.match(/^([\w.]+):(-?\d+\.?\d*)\|([a-z]+)$/);
  if (match) {
    const [, metric, value, type] = match;
    recordMetric(metric, parseFloat(value), type);
  }
});

// MULTICAST — receive messages sent to a group
const multicast = dgram.createSocket({ type: "udp4", reuseAddr: true });
multicast.bind(41234, () =&gt; {
  multicast.addMembership("224.0.0.114");
  console.log("joined multicast group");
});
multicast.on("message", (msg, rinfo) =&gt; {
  console.log(`multicast from ${rinfo.address}: ${msg}`);
});

// BROADCAST — receive LAN broadcasts
const bcast = dgram.createSocket("udp4");
bcast.bind(41234);
bcast.on("listening", () =&gt; bcast.setBroadcast(true));

// GRACEFUL SHUTDOWN
process.on("SIGTERM", () =&gt; {
  server.close(() =&gt; {
    console.log("server closed");
    process.exit(0);
  });
});</code></pre>
<p><strong>Design considerations for UDP servers:</strong></p>
<ul>
  <li><strong>Expect packet loss</strong> — don't build protocols that assume delivery.</li>
  <li><strong>Size limits</strong> — practical limit is ~1400 bytes per packet (MTU minus headers). Larger packets fragment and are more likely to be lost.</li>
  <li><strong>No backpressure</strong> — you can be flooded. Implement rate limiting or queuing in your app.</li>
  <li><strong>No authentication</strong> — UDP has no handshake. IP spoofing is easy. For anything sensitive, use DTLS (UDP + TLS) via <code>dtls</code> libraries.</li>
</ul>
'''

ANSWERS[93] = r'''
<p>The <strong><code>http2</code></strong> module implements <strong>HTTP/2</strong> — a major revision of the HTTP protocol that brings multiplexing, header compression, server push, and binary framing. It coexists with the <code>http</code> module; choose based on your needs.</p>
<p><strong>Key HTTP/2 improvements over HTTP/1.1:</strong></p>
<ul>
  <li><strong>Multiplexing</strong> — many concurrent requests over one TCP connection. Kills the 6-connection-per-host browser limit.</li>
  <li><strong>Header compression (HPACK)</strong> — reduces overhead for repeated headers (cookies, user-agent).</li>
  <li><strong>Binary framing</strong> — more efficient parsing than text-based HTTP/1.</li>
  <li><strong>Server push</strong> — server can proactively send resources (now largely deprecated by browsers, superseded by 103 Early Hints).</li>
  <li><strong>Stream priority</strong> — client can hint which streams are more important.</li>
</ul>
<pre><code>const http2 = require("node:http2");
const fs = require("node:fs");

// HTTP/2 SERVER — requires TLS in browsers (HTTP/2 over cleartext is rare)
const server = http2.createSecureServer({
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),
});

server.on("stream", (stream, headers) =&gt; {
  const method = headers[":method"];
  const path = headers[":path"];

  stream.respond({
    "content-type": "application/json",
    ":status": 200,
  });

  stream.end(JSON.stringify({ method, path, ok: true }));
});

server.listen(8443);

// HTTP/2 CLIENT — make requests from Node
const client = http2.connect("https://example.com");
const req = client.request({ ":path": "/api/users" });

req.on("response", (headers) =&gt; console.log(headers[":status"]));

let data = "";
req.on("data", (chunk) =&gt; data += chunk);
req.on("end", () =&gt; {
  console.log(JSON.parse(data));
  client.close();
});
req.end();

// COMPATIBILITY — same API shape as http, but some differences
const compatServer = http2.createSecureServer({
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),
  allowHTTP1: true,                     // also accept HTTP/1 clients
}, (req, res) =&gt; {
  // Looks like an Express handler — works for both HTTP/1 and HTTP/2
  res.writeHead(200, { "content-type": "text/plain" });
  res.end("Hello from HTTP/2");
});</code></pre>
<p><strong>When to use HTTP/2:</strong></p>
<ul>
  <li><strong>Public-facing web servers</strong> — most production sites benefit, especially those with many assets.</li>
  <li><strong>APIs with frequent small requests</strong> — multiplexing eliminates connection overhead.</li>
  <li><strong>gRPC backends</strong> — gRPC uses HTTP/2 as its transport.</li>
</ul>
<p><strong>Reality:</strong> most Node apps don't use <code>http2</code> directly. A reverse proxy (Nginx, Caddy, Cloudflare, AWS ALB) terminates HTTP/2 from clients and speaks plain HTTP/1 to your Node app. This is simpler, works with any framework, and handles certificate management for you.</p>
<p><strong>HTTP/3 is next</strong> (QUIC over UDP, no head-of-line blocking) — Node has experimental support but isn't production-ready yet.</p>
'''

ANSWERS[94] = r'''
<p>Creating an HTTP/2 server is similar to HTTP/1, but with a stream-oriented event model. Browsers require TLS for HTTP/2, so you'll typically use <code>createSecureServer</code>.</p>
<pre><code>const http2 = require("node:http2");
const fs = require("node:fs");

// STREAM-BASED API (native HTTP/2)
const server = http2.createSecureServer({
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),
});

server.on("stream", (stream, headers) =&gt; {
  console.log(headers[":method"], headers[":path"]);

  stream.respond({
    "content-type": "text/html; charset=utf-8",
    ":status": 200,
  });

  stream.end("&lt;h1&gt;Hello, HTTP/2!&lt;/h1&gt;");
});

server.on("error", (err) =&gt; console.error(err));
server.listen(8443);

// COMPATIBILITY API — looks like http.createServer
// This is what most apps/frameworks use — Express works with this!
const compatServer = http2.createSecureServer({
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),
}, (req, res) =&gt; {
  // Same API as http — req/res are stream-backed
  if (req.url === "/") {
    res.writeHead(200, { "content-type": "text/html" });
    res.end("&lt;h1&gt;Compat HTTP/2&lt;/h1&gt;");
  } else {
    res.writeHead(404).end();
  }
});

// ALSO ACCEPT HTTP/1 — allows clients that don't support HTTP/2
const dualServer = http2.createSecureServer({
  key:  fs.readFileSync("server.key"),
  cert: fs.readFileSync("server.crt"),
  allowHTTP1: true,
}, requestHandler);

// SERVER PUSH — push resources before the client asks
// Note: browsers have mostly dropped support; use 103 Early Hints instead
server.on("stream", (stream, headers) =&gt; {
  if (headers[":path"] === "/") {
    // Push the CSS along with the HTML
    stream.pushStream({ ":path": "/style.css" }, (err, pushStream) =&gt; {
      if (err) return;
      pushStream.respond({ "content-type": "text/css", ":status": 200 });
      pushStream.end("body { font: 16px sans-serif; }");
    });

    stream.respond({ "content-type": "text/html", ":status": 200 });
    stream.end(`&lt;link rel="stylesheet" href="/style.css"&gt;Hello&lt;/a&gt;`);
  }
});

// 103 EARLY HINTS — the modern replacement for push
app.get("/", (req, res) =&gt; {
  res.writeEarlyHints({
    link: [
      "&lt;/style.css&gt;; rel=preload; as=style",
      "&lt;/app.js&gt;; rel=preload; as=script",
    ],
  });
  // Browser starts fetching those while the server prepares the HTML
  res.end(renderHtml());
});

// HTTP/2 CLEARTEXT (h2c) — rarely used in practice; browsers reject it
http2.createServer((req, res) =&gt; {
  res.end("Hello from cleartext HTTP/2");
}).listen(8080);</code></pre>
<p><strong>Practical advice:</strong></p>
<ul>
  <li>For typical web apps, enable HTTP/2 at your reverse proxy (Nginx / Caddy / Cloudflare) and keep your Node app on plain HTTP/1. Simpler and works with any framework.</li>
  <li>Use <code>createSecureServer</code> with <code>allowHTTP1: true</code> if you must terminate HTTP/2 directly — maximizes compatibility.</li>
  <li>Express &lt; 5 doesn't fully support native HTTP/2 stream API — use the compat mode.</li>
  <li>Fastify has excellent HTTP/2 support if you need it end-to-end in Node.</li>
</ul>
'''

ANSWERS[95] = r'''
<p>The <strong><code>timers</code></strong> module exposes Node's scheduling primitives — <code>setTimeout</code>, <code>setInterval</code>, <code>setImmediate</code>, and their clear counterparts. These are actually <strong>global</strong> (you don't need to import them), but the module offers a Promise-based alternative that's much nicer with async/await.</p>
<pre><code>// The globals you already know (no import needed)
const timer = setTimeout(() =&gt; {}, 1000);
clearTimeout(timer);

const interval = setInterval(() =&gt; {}, 1000);
clearInterval(interval);

const immediate = setImmediate(() =&gt; {});
clearImmediate(immediate);

// PROMISE-BASED API — cleaner with async/await
const timers = require("node:timers/promises");

// setTimeout — pause an async function
await timers.setTimeout(1000);                       // wait 1 second
const value = await timers.setTimeout(1000, "done"); // resolves to "done"

// setImmediate — yield control for one turn of the event loop
await timers.setImmediate();

// setInterval — async iterable of ticks
for await (const _ of timers.setInterval(1000)) {
  console.log("tick");
  if (shouldStop) break;
}

// CANCELLATION with AbortController
const ac = new AbortController();
setTimeout(() =&gt; ac.abort(), 5000);

try {
  await timers.setTimeout(60_000, undefined, { signal: ac.signal });
} catch (err) {
  // AbortError when the signal fires
  console.log("timer was cancelled");
}

// KEEPING THE PROCESS ALIVE — the .ref() / .unref() distinction
const t = setTimeout(cleanup, 60_000);
t.unref();     // don't block process exit just for this timer
t.ref();       // do block exit until it fires

// In the Promise API, pass ref: false
await timers.setTimeout(60_000, null, { ref: false });</code></pre>
<p><strong>Why Promise-based timers matter:</strong></p>
<pre><code>// OLD WAY — awkward inside async functions
await new Promise(r =&gt; setTimeout(r, 1000));

// NEW WAY — natural
await timers.setTimeout(1000);

// OLD polling pattern
setInterval(async () =&gt; {
  try {
    await checkSomething();
  } catch (e) { console.error(e); }
}, 5000);
// Problem: overlapping calls if checkSomething takes &gt; 5s

// NEW async iteration pattern
(async () =&gt; {
  for await (const _ of timers.setInterval(5000)) {
    try {
      await checkSomething();     // always completes before next tick
    } catch (e) { console.error(e); }
  }
})();</code></pre>
<p>The promise-based timers module was added in Node 15 and is the preferred API for modern async code. They handle cancellation via <code>AbortSignal</code>, which integrates well with <code>fetch()</code>, streams, and any other cancellation-aware Node API.</p>
'''

ANSWERS[96] = r'''
<p>Many ways to delay execution in Node — choose based on whether you need a single delay, a Promise for async code, or cancellation support.</p>
<pre><code>// 1. CLASSIC setTimeout — global, callback-based
setTimeout(() =&gt; {
  console.log("1 second later");
}, 1000);

// Pass arguments to the callback
setTimeout((name) =&gt; console.log(`Hi ${name}`), 500, "Ada");

// Cancel
const timer = setTimeout(doWork, 5000);
clearTimeout(timer);

// 2. PROMISE-BASED — async/await friendly (Node 15+)
const { setTimeout: delay } = require("node:timers/promises");

async function example() {
  console.log("start");
  await delay(1000);            // pauses for 1 second
  console.log("1 second later");

  // Return a value when resolved
  const result = await delay(500, "done");
  console.log(result);          // "done"
}

// 3. INLINE PROMISE — works on older Node versions
await new Promise((resolve) =&gt; setTimeout(resolve, 1000));

// Reusable helper
const sleep = (ms) =&gt; new Promise((r) =&gt; setTimeout(r, ms));
await sleep(1000);

// 4. WITH CANCELLATION — AbortController
const ac = new AbortController();
setTimeout(() =&gt; ac.abort(), 3000);     // cancel after 3s

try {
  // This delay would be 10 seconds — but the abort cancels it at 3s
  await delay(10_000, undefined, { signal: ac.signal });
  console.log("completed normally");
} catch (err) {
  if (err.name === "AbortError") console.log("was cancelled");
  else throw err;
}

// 5. EXPONENTIAL BACKOFF — common retry pattern
async function withRetry(fn, maxAttempts = 5) {
  for (let i = 0; i &lt; maxAttempts; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === maxAttempts - 1) throw err;
      const wait = Math.min(1000 * 2 ** i, 30_000);    // cap at 30s
      console.log(`attempt ${i + 1} failed; retrying in ${wait}ms`);
      await sleep(wait + Math.random() * 1000);        // jitter
    }
  }
}

// 6. PROCESS EXIT BEHAVIOR
// A pending timer keeps the process alive. Use unref() to change that.
const t = setTimeout(doSomething, 60_000);
t.unref();              // process can exit even if this timer is pending
// So if nothing else is scheduled, process exits immediately</code></pre>
<p><strong>Gotchas:</strong></p>
<ul>
  <li>The delay is a <strong>minimum</strong>, not a guarantee. A blocking synchronous operation will push the callback back.</li>
  <li>Minimum delay is 1 ms. <code>setTimeout(fn, 0)</code> doesn't mean "immediately" — it means "after at least 1 ms, probably more."</li>
  <li>For "run on the next tick of the event loop," use <code>setImmediate(fn)</code> instead of <code>setTimeout(fn, 0)</code>.</li>
  <li>Forgetting to cancel long-running timers in cleanup paths is a common memory leak source.</li>
</ul>
'''

ANSWERS[97] = r'''
<p>The <strong><code>console</code></strong> is a global object — you never need to require it — but the <strong><code>console</code></strong> module lets you create custom <code>Console</code> instances that write to streams other than stdout/stderr (e.g., log files, network sockets).</p>
<pre><code>// DEFAULT — the global console writes to process.stdout / process.stderr
console.log("info");       // → stdout
console.error("oops");     // → stderr

// CUSTOM CONSOLE — write to files
const { Console } = require("node:console");
const fs = require("node:fs");

const logger = new Console({
  stdout: fs.createWriteStream("app.log", { flags: "a" }),
  stderr: fs.createWriteStream("error.log", { flags: "a" }),
  colorMode: false,
});

logger.log("normal log entry");              // → app.log
logger.error("something broke");             // → error.log

// To both the file AND the console — use a Tee stream or write twice
function teeLogger(path) {
  const file = fs.createWriteStream(path, { flags: "a" });
  const both = new class extends require("node:stream").Writable {
    _write(chunk, enc, cb) {
      process.stdout.write(chunk);
      file.write(chunk);
      cb();
    }
  };
  return new Console({ stdout: both, stderr: both });
}

// Console methods beyond log/error/warn
console.info("info level");
console.debug("debug level");       // filtered unless NODE_DEBUG is set
console.trace("where am I?");       // logs + prints stack

// STRUCTURED OUTPUT — console.table
console.table([
  { id: 1, name: "Ada",   role: "admin" },
  { id: 2, name: "Lin",   role: "user"  },
  { id: 3, name: "Grace", role: "admin" },
]);

// GROUPING
console.group("Request processing");
console.log("parsing body");
console.log("validating");
console.groupEnd();

// TIMING
console.time("db-query");
await db.query("SELECT ...");
console.timeEnd("db-query");        // "db-query: 42.123ms"

// ASSERTIONS
console.assert(user.age &gt;= 0, "negative age!");  // only logs if condition is false

// COUNTING (useful for occurrence tracking)
console.count("hit");                // "hit: 1"
console.count("hit");                // "hit: 2"
console.countReset("hit");</code></pre>
<p><strong>Production vs development:</strong></p>
<ul>
  <li><strong>Development:</strong> <code>console.log</code> is fine. It's fast, simple, human-readable.</li>
  <li><strong>Production:</strong> use a structured logger (<strong>pino</strong>, <strong>winston</strong>, <strong>bunyan</strong>). They emit JSON, support log levels, include timestamps and PIDs, and play nicely with log aggregators (CloudWatch, Datadog, Loki).</li>
</ul>
<p><strong>Interesting fact:</strong> <code>console.log</code> is <strong>synchronous when output is a terminal</strong> but <strong>asynchronous when piped</strong>. This causes subtle differences between running a script interactively vs through a log collector.</p>
'''

ANSWERS[98] = r'''
<p>The basic logging methods all follow the same shape — accept format string + arguments (like <code>util.format</code>) and write to the appropriate stream. Different methods map to different severity levels.</p>
<pre><code>// SEVERITY LEVELS — output destination varies
console.log("info");          // stdout
console.info("info");         // stdout (same as log)
console.debug("debug");       // stdout (but filtered when NODE_DEBUG unset)
console.warn("warning");      // stderr
console.error("error");       // stderr

// FORMAT STRING SPECIFIERS (same as util.format)
console.log("User %s is %d years old", "Ada", 36);
console.log("Object: %o", { a: 1, b: { c: 2 } });     // full inspect
console.log("JSON: %j", { a: 1 });                     // JSON.stringify
console.log("Literal %%");                             // "Literal %"

// OBJECTS ARE INSPECTED
console.log("user:", { name: "Ada", age: 36 });
// user: { name: 'Ada', age: 36 }

// Control the depth of object inspection
console.dir({ a: { b: { c: { d: "deep!" } } } }, { depth: null });

// TABLE — great for arrays of objects
console.table([
  { id: 1, name: "Ada" },
  { id: 2, name: "Lin" },
]);
// ┌─────────┬────┬───────┐
// │ (index) │ id │ name  │
// ├─────────┼────┼───────┤
// │    0    │ 1  │ 'Ada' │
// │    1    │ 2  │ 'Lin' │
// └─────────┴────┴───────┘

// Restrict to specific columns
console.table(users, ["name", "role"]);

// GROUPS — visually indent related log lines
console.group("Request");
console.log("method: GET");
console.log("path: /users");
console.groupCollapsed("headers");     // collapsed in browser-like consoles
console.log("user-agent: curl/8.4");
console.groupEnd();
console.groupEnd();

// TIMING
console.time("fetch");
await fetch("https://example.com");
console.timeEnd("fetch");              // "fetch: 145.3ms"

// Multiple concurrent timers (use unique labels)
console.time("db");
console.time("render");
await Promise.all([db.query(), render()]);
console.timeEnd("db");
console.timeEnd("render");

// Continue timing across many log points
console.time("total");
console.timeLog("total", "starting phase 2");
console.timeLog("total", "finishing phase 2");
console.timeEnd("total");

// STACK TRACES
console.trace("breadcrumb");           // prints "Trace: breadcrumb" + stack

// ASSERTIONS
console.assert(Array.isArray(data), "expected array, got", typeof data);
// Only prints if condition is false — not a replacement for throwing

// COUNT — track how many times something happens
for (const item of items) {
  console.count(item.type);            // prints "user: 1", "user: 2", ...
}</code></pre>
<p><strong>Log level convention</strong> (informal but widely followed):</p>
<ul>
  <li><strong>debug</strong> — verbose, developer-only.</li>
  <li><strong>info/log</strong> — normal informational messages.</li>
  <li><strong>warn</strong> — recoverable issues, deprecation warnings.</li>
  <li><strong>error</strong> — something went wrong; needs attention.</li>
</ul>
<p>For production, use a real logger like <strong>pino</strong> (fastest) or <strong>winston</strong> (most flexible). They give you structured JSON output, log levels, rotation, and transport pluggability.</p>
'''

ANSWERS[99] = r'''
<p>The <strong><code>assert</code></strong> module is Node's built-in assertion library — small, dependency-free, and the foundation for many test frameworks. Assertions throw an <code>AssertionError</code> when they fail, which test runners (mocha, node:test, jest via adapter) catch and report.</p>
<pre><code>const assert = require("node:assert");
const strict = require("node:assert/strict");     // modern, preferred

// EQUALITY
assert.strictEqual(2 + 2, 4);          // === (strict equality)
assert.equal(2 + "2", "22");           // == (loose; avoid in new code)
assert.notStrictEqual(1, 2);

// DEEP EQUALITY for objects/arrays
assert.deepStrictEqual({ a: 1 }, { a: 1 });         // structural comparison
assert.deepStrictEqual([1, [2, 3]], [1, [2, 3]]);   // works recursively
assert.notDeepStrictEqual([1, 2], [1, 3]);

// TRUTHY / FALSY
assert(user);                          // throws if falsy
assert.ok(user);                       // same thing

// PATTERN MATCHING
assert.match("hello world", /hello/);
assert.doesNotMatch("hello", /world/);

// EXCEPTIONS
assert.throws(() =&gt; { throw new Error("boom"); });
assert.throws(() =&gt; JSON.parse("not json"), SyntaxError);
assert.throws(() =&gt; fn(), /specific error/);

// Async exceptions
await assert.rejects(
  async () =&gt; { throw new Error("async boom"); },
  /async boom/,
);

// Async NOT throwing
await assert.doesNotReject(async () =&gt; "fine");

// FAIL EXPLICITLY
if (!somethingExpected) {
  assert.fail("somethingExpected should be true");
}

// STRICT MODE — prefer this in new code (stricter, better messages)
const { strictEqual, deepStrictEqual } = require("node:assert/strict");
strictEqual("5", 5);           // throws (strict mode doesn't coerce)
// Vs:
// assert.equal("5", 5);       // passes (loose comparison)</code></pre>
<p><strong>assert vs test frameworks:</strong></p>
<ul>
  <li><strong><code>assert</code> alone</strong> — fine for basic checks inside scripts or as sanity checks in production code.</li>
  <li><strong>Test frameworks</strong> — add test organization, parallel running, reporters, mocking, fixtures. Use them for real test suites.</li>
  <li><strong>Node's built-in test runner</strong> (<code>node:test</code>, stable since Node 20) is excellent and uses <code>assert</code> under the hood.</li>
</ul>
<pre><code>// Common pattern — production sanity checks
function calculateTotal(items) {
  const total = items.reduce((s, i) =&gt; s + i.price, 0);
  assert(total &gt;= 0, "total should not be negative");
  return total;
}

// In Node 20+, assertions can be stripped in production with --disable-assertions
// This makes them free in hot paths but still catches bugs in dev/test.</code></pre>
<p>Modern test setups: <strong>node:test</strong> (built-in, zero-dep) + <strong>node:assert/strict</strong> for idiomatic JS testing; <strong>vitest</strong> for projects using Vite; <strong>jest</strong> for big existing codebases.</p>
'''

ANSWERS[100] = r'''
<p>Node ships with a built-in test runner (<strong><code>node:test</code></strong>, stable since Node 20) that pairs naturally with <code>node:assert</code>. No framework installation required.</p>
<pre><code>// math.js — code under test
function add(a, b) { return a + b; }
function divide(a, b) {
  if (b === 0) throw new Error("divide by zero");
  return a / b;
}
module.exports = { add, divide };

// math.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const { add, divide } = require("./math");

test("add — basic cases", () =&gt; {
  assert.strictEqual(add(2, 3), 5);
  assert.strictEqual(add(-1, 1), 0);
  assert.strictEqual(add(0, 0), 0);
});

test("divide — returns quotient", () =&gt; {
  assert.strictEqual(divide(10, 2), 5);
  assert.strictEqual(divide(7, 2), 3.5);
});

test("divide — throws on zero", () =&gt; {
  assert.throws(() =&gt; divide(1, 0), /divide by zero/);
});

// NESTED TESTS with describe-style
test("user service", async (t) =&gt; {
  await t.test("creates a user", () =&gt; {
    const u = createUser("Ada");
    assert.equal(u.name, "Ada");
    assert.ok(u.id);
  });

  await t.test("rejects empty name", () =&gt; {
    assert.throws(() =&gt; createUser(""));
  });
});

// SETUP / TEARDOWN
test("with hooks", async (t) =&gt; {
  let db;

  t.before(async () =&gt; { db = await connectDB(); });
  t.after(async  () =&gt; { await db.close(); });
  t.beforeEach(async () =&gt; { await db.clear(); });

  await t.test("insert", async () =&gt; {
    await db.insert({ name: "Ada" });
    const user = await db.findOne({ name: "Ada" });
    assert.equal(user.name, "Ada");
  });
});

// ASYNC TESTS
test("fetches user", async () =&gt; {
  const user = await fetchUser(1);
  assert.deepEqual(user, { id: 1, name: "Ada" });
});

// PARAMETERIZED TESTS — data-driven
for (const { a, b, expected } of [
  { a: 1, b: 2, expected: 3 },
  { a: 5, b: 5, expected: 10 },
  { a: -1, b: 1, expected: 0 },
]) {
  test(`add(${a}, ${b}) === ${expected}`, () =&gt; {
    assert.strictEqual(add(a, b), expected);
  });
}

// SKIP &amp; TODO
test("slow test", { skip: true }, () =&gt; { /* ... */ });
test("not yet implemented", { todo: true }, () =&gt; { /* ... */ });

// RUN THE TESTS
// $ node --test
// $ node --test math.test.js
// $ node --test --test-reporter=spec    # pretty output
// $ node --test --experimental-test-coverage   # coverage report</code></pre>
<p><strong>Built-in runner features:</strong></p>
<ul>
  <li><strong>Zero dependencies</strong> — ships with Node.</li>
  <li><strong>Parallel</strong> — runs test files in parallel by default.</li>
  <li><strong>TAP output</strong> — standard protocol; integrates with most CI systems.</li>
  <li><strong>Built-in coverage</strong> (Node 20+) — <code>--experimental-test-coverage</code>.</li>
  <li><strong>Mocking</strong> — <code>mock</code> module lets you stub functions and timers.</li>
</ul>
<p><strong>When to use external frameworks instead:</strong> Jest (big codebases with lots of existing Jest tests), Vitest (Vite projects, ESM-first, snapshot testing), mocha + chai (if team prefers BDD style). For greenfield Node, <code>node:test</code> is genuinely a first-class choice now.</p>
'''
