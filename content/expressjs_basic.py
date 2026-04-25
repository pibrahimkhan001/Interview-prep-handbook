# ExpressJS - Basic
# Detailed answers for the 100 ExpressJS Basic questions.
# Style: Basic - definition first, key characteristics (bullets/table), one code example,
# optional gotcha callout. ~100-250 words each.

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>Express.js</strong> (commonly just "Express") is a minimal, unopinionated web framework for Node.js &mdash; a thin layer over the built-in <code>http</code> module that adds routing, middleware, request/response helpers, and a pluggable ecosystem. It was released in 2010 and for over a decade has been the default Node HTTP framework.</p>
<pre><code>const express = require("express");
const app = express();

app.get("/hello", (req, res) =&gt; {
  res.json({ message: "Hello, world!" });
});

app.listen(3000, () =&gt; console.log("http://localhost:3000"));</code></pre>
<p><strong>Key characteristics:</strong></p>
<ul>
  <li><strong>Minimal core:</strong> routing + middleware + a handful of helpers. Everything else (validation, auth, sessions, templates) comes from middleware packages.</li>
  <li><strong>Middleware pipeline:</strong> requests flow through an ordered chain of functions that can inspect, modify, or short-circuit the response.</li>
  <li><strong>Unopinionated:</strong> no enforced project layout, no built-in ORM, no CLI. You choose every piece.</li>
  <li><strong>Massive ecosystem:</strong> thousands of middleware packages on npm (<code>helmet</code>, <code>morgan</code>, <code>cors</code>, <code>express-session</code>, &hellip;).</li>
</ul>
<p><strong>Context in 2026:</strong> Express 5.x is now stable (after a long beta), with native async error handling and modernized internals. Alternatives like <strong>Fastify</strong> (faster, schema-first), <strong>Hono</strong> (edge-first), and <strong>NestJS</strong> (opinionated, DI-first) have grown, but Express remains the most widely deployed &mdash; and the knowledge transfers to nearly every Node framework.</p>
'''

ANSWERS[2] = r'''
<p>Install Express with <strong>npm</strong> (or pnpm/yarn/bun) inside a Node project. You need Node 18 or newer for Express 5.</p>
<pre><code># 1. Create a project (if you don't have one yet)
mkdir my-app &amp;&amp; cd my-app
npm init -y                 # creates package.json

# 2. Install Express as a runtime dependency
npm install express         # or: pnpm add express, yarn add, bun add

# 3. (Optional) dev tools
npm install -D nodemon      # auto-restart on file change
npm install -D typescript @types/express @types/node   # for TypeScript

# Verify
node -e "console.log(require('express/package.json').version)"</code></pre>
<p><strong>What this does:</strong></p>
<ul>
  <li>Adds <code>"express": "^5.x.x"</code> to <code>dependencies</code> in <code>package.json</code>.</li>
  <li>Downloads Express and its transitive dependencies into <code>node_modules/</code>.</li>
  <li>Records exact versions in <code>package-lock.json</code> for reproducible installs.</li>
</ul>
<p><strong>Tips:</strong></p>
<ul>
  <li>Commit <code>package.json</code> <em>and</em> <code>package-lock.json</code>; add <code>node_modules/</code> to <code>.gitignore</code>.</li>
  <li>Use <code>npm ci</code> in CI/production &mdash; it installs exactly what the lockfile says, failing if they disagree.</li>
  <li>Pin the Node version with <code>"engines": { "node": "&gt;=20" }</code> in <code>package.json</code> so teammates and CI use a compatible runtime.</li>
</ul>
'''

ANSWERS[3] = r'''
<p>Express gives you a focused set of HTTP primitives and leaves the rest to the ecosystem. Its main features all center on making an HTTP server quick to write and easy to extend.</p>
<ul>
  <li><strong>Routing</strong> &mdash; map HTTP methods + URL patterns to handler functions: <code>app.get("/users/:id", handler)</code>.</li>
  <li><strong>Middleware pipeline</strong> &mdash; compose cross-cutting concerns (logging, auth, parsing, errors) as functions that run in order.</li>
  <li><strong>Request/response helpers</strong> &mdash; <code>req.params</code>, <code>req.query</code>, <code>res.json()</code>, <code>res.status()</code>, <code>res.redirect()</code>.</li>
  <li><strong>Routers</strong> &mdash; mini-apps you can mount at a path (<code>app.use("/api", apiRouter)</code>) for modular code.</li>
  <li><strong>Static file serving</strong> &mdash; one-liner: <code>app.use(express.static("public"))</code>.</li>
  <li><strong>Template engine support</strong> &mdash; built-in integration for EJS, Pug, Handlebars, etc., via <code>res.render()</code>.</li>
  <li><strong>Content negotiation</strong> &mdash; <code>res.format()</code> for different response types, <code>req.accepts()</code> to inspect.</li>
</ul>
<pre><code>const express = require("express");
const app = express();

app.use(express.json());                         // middleware
app.get("/", (req, res) =&gt; res.send("ok"));      // route
app.use((err, req, res, next) =&gt; {               // error handler
  res.status(500).json({ error: err.message });
});
app.listen(3000);</code></pre>
<p><strong>What Express deliberately <em>doesn't</em> do:</strong> validation, ORM, authentication, config management, CLI scaffolding, built-in testing. You pick your own &mdash; that flexibility is both Express's strength and its learning curve.</p>
'''

ANSWERS[4] = r'''
<p>A "hello world" Express server is four lines of real code: import Express, create an app, declare a route, start listening.</p>
<pre><code>// server.js
const express = require("express");
const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) =&gt; {
  res.send("Hello from Express!");
});

app.get("/health", (req, res) =&gt; {
  res.json({ status: "ok", uptime: process.uptime() });
});

app.listen(PORT, () =&gt; {
  console.log(`Server listening on http://localhost:${PORT}`);
});</code></pre>
<p>Run it with <code>node server.js</code>, then open <code>http://localhost:3000</code>.</p>
<p><strong>What's happening:</strong></p>
<ul>
  <li><code>express()</code> returns an <em>app</em> object &mdash; really a function that acts as an HTTP request handler <em>and</em> carries methods like <code>get</code>, <code>use</code>, <code>listen</code>.</li>
  <li><code>app.get(path, handler)</code> registers a route for GET requests matching <code>path</code>.</li>
  <li><code>app.listen(port)</code> creates a raw <code>http.Server</code> under the hood and starts accepting connections.</li>
</ul>
<p><strong>Modern ESM version</strong> (if <code>"type": "module"</code> in <code>package.json</code>):</p>
<pre><code>import express from "express";
const app = express();
app.get("/", (req, res) =&gt; res.send("Hello!"));
app.listen(3000);</code></pre>
<p><strong>Dev tip:</strong> use <code>nodemon</code> or Node 22's built-in <code>node --watch server.js</code> to auto-restart on file changes.</p>
'''

ANSWERS[5] = r'''
<p><strong>Middleware</strong> is a function that sits in the request pipeline. Each middleware receives the request and response objects plus a <code>next</code> callback; it can inspect or modify them, send a response, or call <code>next()</code> to pass control to the next middleware in line. Express's entire design &mdash; routing, parsing, error handling &mdash; is built on this pattern.</p>
<pre><code>// Signature: (req, res, next) =&gt; void
function logger(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next();                              // pass control onward
}

function requireAuth(req, res, next) {
  if (!req.headers.authorization) return res.status(401).send("Unauthorized");
  next();
}

app.use(logger);                       // runs for every request
app.use("/admin", requireAuth);        // runs only under /admin
app.get("/admin/panel", (req, res) =&gt; res.send("welcome"));</code></pre>
<p><strong>What middleware is used for:</strong></p>
<ul>
  <li><strong>Parsing:</strong> <code>express.json()</code>, <code>express.urlencoded()</code> &mdash; turn request bodies into <code>req.body</code>.</li>
  <li><strong>Logging:</strong> <code>morgan</code>, <code>pino-http</code>.</li>
  <li><strong>Security:</strong> <code>helmet</code>, <code>cors</code>, <code>express-rate-limit</code>.</li>
  <li><strong>Authentication:</strong> Passport strategies, custom JWT verifiers.</li>
  <li><strong>Error handling:</strong> a special 4-argument middleware <code>(err, req, res, next)</code>.</li>
</ul>
<p><strong>Order matters.</strong> Middleware runs top-to-bottom in registration order. Body parsers must come before routes that read <code>req.body</code>; the error handler comes <em>last</em>. Forgetting to call <code>next()</code> (or not sending a response) leaves requests hanging forever.</p>
'''

ANSWERS[6] = r'''
<p>A <strong>route</strong> is a pairing of an HTTP method, a URL pattern, and one or more handler functions. Express provides one method per HTTP verb &mdash; <code>app.get</code>, <code>app.post</code>, <code>app.put</code>, <code>app.patch</code>, <code>app.delete</code>, <code>app.options</code>, <code>app.head</code> &mdash; plus <code>app.all</code> for any method.</p>
<pre><code>// Basic routes
app.get("/", (req, res) =&gt; res.send("home"));
app.post("/users", (req, res) =&gt; res.status(201).json({ created: true }));
app.delete("/users/:id", (req, res) =&gt; res.sendStatus(204));

// URL parameters — captured into req.params
app.get("/users/:id", (req, res) =&gt; {
  res.json({ id: req.params.id });
});

// Multiple parameters
app.get("/posts/:year/:slug", (req, res) =&gt; {
  const { year, slug } = req.params;
  res.send(`post ${slug} from ${year}`);
});

// Optional parameter (Express 5 syntax)
app.get("/products/:id{/:variant}", (req, res) =&gt; { /* variant may be undefined */ });

// Any method at this path
app.all("/status", (req, res) =&gt; res.send(`${req.method} status`));</code></pre>
<p><strong>Path patterns</strong> Express understands:</p>
<ul>
  <li><code>:param</code> &mdash; named URL parameter, available on <code>req.params</code>.</li>
  <li><code>*</code> or <code>{*any}</code> (Express 5) &mdash; wildcard.</li>
  <li>Regex &mdash; pass a <code>RegExp</code> instead of a string: <code>app.get(/^\/\d+$/, handler)</code>.</li>
</ul>
<p><strong>Express 5 note:</strong> path-to-regexp was updated; the old optional-parameter <code>:name?</code> syntax changed to <code>{/:name}</code>, and bare <code>*</code> requires a name like <code>{*splat}</code>. If you're migrating from v4, most routes still work, but optional params need updating.</p>
'''

ANSWERS[7] = r'''
<p>Both register a route, but for different <strong>HTTP methods</strong> &mdash; <code>app.get()</code> for <code>GET</code> requests (safe, idempotent reads) and <code>app.post()</code> for <code>POST</code> requests (create operations or actions that change state).</p>
<table>
  <thead><tr><th>Aspect</th><th><code>app.get()</code></th><th><code>app.post()</code></th></tr></thead>
  <tbody>
    <tr><td>HTTP method</td><td>GET</td><td>POST</td></tr>
    <tr><td>Purpose</td><td>Read data</td><td>Create / trigger action</td></tr>
    <tr><td>Body allowed?</td><td>Technically yes, but not used</td><td>Yes &mdash; payload in <code>req.body</code></td></tr>
    <tr><td>Idempotent?</td><td>Yes (same effect if repeated)</td><td>No (creates a new resource each time)</td></tr>
    <tr><td>Cacheable?</td><td>Yes</td><td>No by default</td></tr>
    <tr><td>Visible in URL?</td><td>Yes (query string)</td><td>No (body not logged by default)</td></tr>
  </tbody>
</table>
<pre><code>app.use(express.json());

// GET — read the list, no body
app.get("/users", async (req, res) =&gt; {
  const users = await db.user.findMany();
  res.json(users);
});

// POST — create a new user, data comes in req.body
app.post("/users", async (req, res) =&gt; {
  const user = await db.user.create({ data: req.body });
  res.status(201).json(user);
});</code></pre>
<p><strong>Practical rule:</strong> if the request changes server state, use POST (or PUT/PATCH/DELETE). If it only reads, use GET. Putting mutations behind GET is a common mistake &mdash; browsers prefetch GET URLs, proxies cache them, and search bots can trigger them unintentionally.</p>
'''

ANSWERS[8] = r'''
<p>Register a handler with <code>app.get(path, handler)</code>. The handler receives <code>(req, res, next)</code>. Read inputs from <code>req.params</code>, <code>req.query</code>, and headers; send the response with <code>res.json()</code>, <code>res.send()</code>, or <code>res.render()</code>.</p>
<pre><code>// Read a single user by ID (path parameter)
app.get("/users/:id", async (req, res, next) =&gt; {
  try {
    const user = await db.user.findUnique({ where: { id: req.params.id } });
    if (!user) return res.status(404).json({ error: "not found" });
    res.json(user);
  } catch (err) {
    next(err);                         // forward to error handler
  }
});

// List users with query-string filters: /users?role=admin&amp;limit=10
app.get("/users", async (req, res) =&gt; {
  const role  = req.query.role;               // string | undefined
  const limit = Math.min(100, +req.query.limit || 20);
  const users = await db.user.findMany({
    where: role ? { role } : undefined,
    take:  limit,
  });
  res.json(users);
});

// Serve HTML rendered from a template
app.get("/", (req, res) =&gt; res.render("home", { title: "Welcome" }));</code></pre>
<p><strong>Common response helpers:</strong></p>
<ul>
  <li><code>res.json(obj)</code> &mdash; stringify and send with <code>Content-Type: application/json</code>.</li>
  <li><code>res.send(str|buf|obj)</code> &mdash; auto-detects content type.</li>
  <li><code>res.sendStatus(204)</code> &mdash; status + text body.</li>
  <li><code>res.redirect("/login")</code> &mdash; 302 redirect (pass 301 for permanent).</li>
</ul>
<p><strong>Tip:</strong> never trust <code>req.query</code> or <code>req.params</code> &mdash; they're user input. Validate and coerce with Zod, Joi, or express-validator before using them in DB queries.</p>
'''

ANSWERS[9] = r'''
<p>Register the route with <code>app.post()</code> and install a body-parsing middleware (<code>express.json()</code> or <code>express.urlencoded()</code>) so Express populates <code>req.body</code>. Without the parser, <code>req.body</code> is <code>undefined</code>.</p>
<pre><code>const express = require("express");
const app = express();

// Body parsers — install BEFORE routes that read req.body
app.use(express.json({ limit: "100kb" }));                    // JSON bodies
app.use(express.urlencoded({ extended: true, limit: "100kb" })); // form bodies

// POST — create a user
app.post("/users", async (req, res, next) =&gt; {
  try {
    const { name, email } = req.body;
    if (!name || !email) {
      return res.status(400).json({ error: "name and email required" });
    }
    const user = await db.user.create({ data: { name, email } });
    res.status(201).location(`/users/${user.id}`).json(user);
  } catch (err) {
    if (err.code === "P2002") {                               // unique violation
      return res.status(409).json({ error: "email already exists" });
    }
    next(err);
  }
});</code></pre>
<p><strong>Conventions:</strong></p>
<ul>
  <li>Return <strong>201 Created</strong> on success (not 200). Add a <code>Location</code> header pointing at the new resource.</li>
  <li>Return <strong>400</strong> for bad input, <strong>409</strong> for conflicts (duplicate email), <strong>422</strong> for validation errors.</li>
  <li>Cap body size with <code>limit</code> &mdash; the default 100kb protects you from memory-bomb attacks. For uploads, use <code>multer</code> instead of <code>express.json</code>.</li>
</ul>
<p><strong>Testing quickly:</strong></p>
<pre><code>curl -X POST http://localhost:3000/users \
  -H "content-type: application/json" \
  -d '{"name":"Ada","email":"ada@example.com"}'</code></pre>
'''

ANSWERS[10] = r'''
<p><code>next()</code> is the callback every middleware receives as its third argument. Calling it passes control to the <strong>next middleware in the chain</strong>. If you neither send a response nor call <code>next()</code>, the request hangs until the client times out.</p>
<pre><code>app.use((req, res, next) =&gt; {
  req.startedAt = Date.now();
  next();                            // hand off to the next middleware
});

app.use((req, res, next) =&gt; {
  res.on("finish", () =&gt; {
    console.log(`${req.method} ${req.url} — ${Date.now() - req.startedAt}ms`);
  });
  next();
});

app.get("/", (req, res) =&gt; res.send("ok"));    // route handler — ends the chain</code></pre>
<p><strong>Three useful variants:</strong></p>
<ul>
  <li><code>next()</code> &mdash; proceed to the next middleware or route handler.</li>
  <li><code>next(err)</code> &mdash; skip ahead to the <em>next error-handling middleware</em> (the 4-argument kind). Used to signal failure.</li>
  <li><code>next("route")</code> &mdash; skip the remaining handlers in the current route and try the next matching route. Rarely used.</li>
</ul>
<pre><code>// Signal an error — Express jumps to the nearest error middleware
app.get("/protected", (req, res, next) =&gt; {
  if (!req.user) return next(new Error("unauthorized"));
  res.send("secret data");
});

// Error handler — note the 4 parameters
app.use((err, req, res, next) =&gt; {
  console.error(err);
  res.status(500).json({ error: err.message });
});</code></pre>
<p><strong>Common mistakes:</strong> (1) calling <code>next()</code> <em>and</em> sending a response &mdash; causes "headers already sent" errors. (2) forgetting <code>next()</code> in an async middleware when no response is sent &mdash; request hangs. Express 5 auto-forwards rejected promises, so <code>async (req, res) =&gt; { throw err }</code> now works without manual <code>next(err)</code>.</p>
'''

ANSWERS[11] = r'''
<p>Use the built-in <code>express.static</code> middleware. Point it at a directory and every file in that directory becomes accessible by URL path &mdash; images, CSS, JS, PDFs, favicons, anything. No route code required.</p>
<pre><code>const path = require("node:path");
const express = require("express");
const app = express();

// Serve everything in ./public at the URL root
app.use(express.static(path.join(__dirname, "public")));
// public/logo.png  →  GET /logo.png
// public/css/app.css →  GET /css/app.css

// Mount at a URL prefix
app.use("/assets", express.static(path.join(__dirname, "public")));
// public/logo.png  →  GET /assets/logo.png

// Multiple directories — first match wins
app.use(express.static("dist"));
app.use(express.static("public"));

// With options
app.use(express.static("public", {
  maxAge: "7d",          // Cache-Control: max-age=604800
  etag: true,            // enabled by default
  index: "index.html",   // default file when the URL is a directory
  dotfiles: "ignore",    // don't serve .env, .git etc.
  fallthrough: true,     // if not found, move to next middleware
}));</code></pre>
<p><strong>Practical rules:</strong></p>
<ul>
  <li><strong>Put the static middleware <em>before</em> your routes.</strong> You want <code>GET /logo.png</code> to short-circuit to the file, not hit a catch-all route.</li>
  <li>Use an absolute path (<code>path.join(__dirname, "public")</code>). Relative paths depend on where you launch the process.</li>
  <li>Set <code>maxAge</code> for versioned assets (<code>app.abc123.js</code>) &mdash; browsers cache aggressively.</li>
  <li>Never serve the project root (<code>express.static(".")</code>) &mdash; you'll expose <code>.env</code>, source code, and anything else.</li>
</ul>
<p><strong>In production</strong>, serve static files from a CDN (CloudFront, Cloudflare) or a reverse proxy (Nginx) &mdash; they're faster and free Node to handle dynamic requests.</p>
'''

ANSWERS[12] = r'''
<p><code>express.json()</code> is a built-in middleware that reads the request body stream, parses JSON, and assigns the result to <code>req.body</code>. It does nothing if the request's <code>Content-Type</code> isn't <code>application/json</code>. Without it, <code>req.body</code> is <code>undefined</code> on POST/PUT/PATCH.</p>
<pre><code>const express = require("express");
const app = express();

app.use(express.json({
  limit:    "100kb",       // reject bodies larger than this
  strict:   true,          // only accept objects/arrays at the top level
  type:     "application/json", // or a function / list of content types
  inflate:  true,          // automatically gunzip gzipped bodies
  verify:   (req, res, buf) =&gt; {   // for raw-body access, e.g. webhook signature
    req.rawBody = buf;
  },
}));

app.post("/echo", (req, res) =&gt; {
  res.json({ received: req.body });
});</code></pre>
<p><strong>Why it's needed:</strong> raw Node HTTP exposes the body as a readable stream &mdash; you'd have to collect chunks, concatenate, and <code>JSON.parse</code> yourself. <code>express.json()</code> does all of that with sensible defaults and error handling.</p>
<p><strong>Gotchas:</strong></p>
<ul>
  <li><strong>Install before routes.</strong> Middleware is ordered; parsers must run before handlers that read <code>req.body</code>.</li>
  <li><strong>Stripe/GitHub webhooks need the raw body</strong> to verify signatures. Capture it with the <code>verify</code> hook or use <code>express.raw()</code> on the specific route.</li>
  <li><strong>Invalid JSON</strong> rejects with a 400 and the error ends up in your error handler &mdash; handle it cleanly.</li>
  <li><strong>The default 100kb limit</strong> is deliberately small. Raise only if you truly need to and pair with rate limiting.</li>
</ul>
<p><strong>Note:</strong> historically you used the <code>body-parser</code> package; since Express 4.16 (2016) <code>express.json()</code> ships built-in. You almost never need the separate <code>body-parser</code> package today.</p>
'''

ANSWERS[13] = r'''
<p><strong>URL parameters</strong> (sometimes called "route parameters") are named segments of the path &mdash; declared with <code>:name</code> in the route pattern and available on <code>req.params</code> as strings.</p>
<pre><code>// Single parameter
app.get("/users/:id", (req, res) =&gt; {
  res.json({ id: req.params.id });               // GET /users/42 → "42"
});

// Multiple parameters
app.get("/orgs/:orgId/users/:userId", (req, res) =&gt; {
  const { orgId, userId } = req.params;
  res.send(`org ${orgId}, user ${userId}`);
});

// Express 5 — optional parameter (use curly braces)
app.get("/products/:id{/:variant}", (req, res) =&gt; {
  // req.params.variant is undefined when omitted
});

// Constrain with a regex (only digits for the id)
app.get("/users/:id(\\d+)", (req, res) =&gt; {
  // "/users/abc" returns 404 before the handler runs
  res.json({ id: +req.params.id });
});

// Wildcard capture (Express 5 syntax)
app.get("/files/{*path}", (req, res) =&gt; {
  res.send(req.params.path);                     // "/files/a/b/c" → "a/b/c"
});</code></pre>
<p><strong>Key behaviours:</strong></p>
<ul>
  <li><strong>Always strings.</strong> Even <code>/users/42</code> gives <code>req.params.id === "42"</code> &mdash; convert with <code>Number()</code> or <code>+</code>.</li>
  <li><strong>URL-decoded automatically</strong> &mdash; <code>%20</code> becomes a space.</li>
  <li><strong>Required by default.</strong> A pattern <code>/users/:id</code> won't match <code>/users</code>.</li>
  <li><strong>No type validation</strong> &mdash; always validate with Zod/express-validator before hitting the database.</li>
</ul>
<p><strong>Don't confuse</strong> URL parameters (<code>/users/:id</code>) with <em>query</em> parameters (<code>/users?id=42</code>). Params are part of the path; query is after the <code>?</code>. Use params for identifying a resource, query for filtering or pagination.</p>
'''

ANSWERS[14] = r'''
<p><strong>Query parameters</strong> are the key/value pairs after the <code>?</code> in a URL. Express parses them for you and exposes the result on <code>req.query</code>.</p>
<pre><code>// GET /search?q=node&amp;page=2&amp;tag=js&amp;tag=ts
app.get("/search", (req, res) =&gt; {
  const q    = req.query.q;          // "node"
  const page = +req.query.page || 1; // 2 (coerce to number)
  const tags = [].concat(req.query.tag || []); // always an array: ["js","ts"]
  res.json({ q, page, tags });
});

// With extended parsing (Express uses `qs` by default; turn off for simpler parsing)
// app.set("query parser", "simple");  // disables nested / array syntax

// Nested query (qs syntax):  /filter?sort[field]=name&amp;sort[dir]=asc
app.get("/filter", (req, res) =&gt; {
  // req.query.sort === { field: "name", dir: "asc" }
  res.json(req.query.sort);
});</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Everything is a string</strong> by default &mdash; coerce: <code>+req.query.limit || 20</code>.</li>
  <li><strong>Repeated keys become arrays.</strong> <code>?tag=a&amp;tag=b</code> → <code>req.query.tag === ["a","b"]</code>. Normalize: <code>[].concat(req.query.tag ?? [])</code>.</li>
  <li><strong>Always cap limits.</strong> <code>Math.min(100, +req.query.limit || 20)</code> prevents an attacker from asking for 10 million rows.</li>
  <li><strong>Validate and sanitize.</strong> Never drop raw query values into a SQL or shell command. Use parameterized queries and a validator (Zod).</li>
  <li><strong>Don't log full URLs with sensitive query params</strong> &mdash; access tokens in query strings end up in proxy logs.</li>
</ul>
<pre><code>// With Zod — typed, validated, default-safe
import { z } from "zod";
const Q = z.object({
  q:     z.string().min(1).max(100),
  page:  z.coerce.number().int().min(1).max(1000).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});
app.get("/search", (req, res) =&gt; {
  const { q, page, limit } = Q.parse(req.query);
  // safe to use
});</code></pre>
'''

ANSWERS[15] = r'''
<p><code>express.urlencoded()</code> parses <strong>HTML form submissions</strong> &mdash; requests with <code>Content-Type: application/x-www-form-urlencoded</code>, the default encoding a browser uses when you submit a <code>&lt;form&gt;</code>. It fills <code>req.body</code> with the parsed fields.</p>
<pre><code>app.use(express.urlencoded({
  extended: true,      // true → qs (nested/array support); false → querystring (flat)
  limit:    "100kb",
  type:     "application/x-www-form-urlencoded",
}));

// HTML form:
// &lt;form method="POST" action="/signup"&gt;
//   &lt;input name="email"&gt;
//   &lt;input name="password" type="password"&gt;
//   &lt;button&gt;Sign up&lt;/button&gt;
// &lt;/form&gt;
app.post("/signup", (req, res) =&gt; {
  const { email, password } = req.body;
  // ... create user
  res.redirect("/welcome");
});

// Extended: true → nested objects supported
// Form: user[name]=Ada&amp;user[email]=ada@x.com
// req.body = { user: { name: "Ada", email: "ada@x.com" } }</code></pre>
<p><strong>Two body parsers, two content types:</strong></p>
<table>
  <thead><tr><th>Middleware</th><th>Parses</th><th>Typical source</th></tr></thead>
  <tbody>
    <tr><td><code>express.json()</code></td><td><code>application/json</code></td><td>fetch/axios from JS, API clients</td></tr>
    <tr><td><code>express.urlencoded()</code></td><td><code>application/x-www-form-urlencoded</code></td><td>HTML form POSTs</td></tr>
    <tr><td><code>express.raw()</code></td><td>any &mdash; Buffer</td><td>webhooks needing raw body for signatures</td></tr>
    <tr><td><code>express.text()</code></td><td><code>text/plain</code></td><td>rare</td></tr>
    <tr><td><code>multer</code> (external)</td><td><code>multipart/form-data</code></td><td>file uploads</td></tr>
  </tbody>
</table>
<p><strong>In practice:</strong> if you have any HTML form in your app, install both <code>express.json()</code> and <code>express.urlencoded()</code> &mdash; they don't conflict and cover both browser forms and JS-driven API calls.</p>
'''

ANSWERS[16] = r'''
<p><code>express.Router</code> creates a <strong>mini-application</strong> &mdash; a self-contained chunk of routes and middleware you can mount anywhere on your app with <code>app.use()</code>. It's the standard way to split a growing Express app into modules.</p>
<pre><code>// routes/users.js
const express = require("express");
const router = express.Router();

// middleware scoped to this router only
router.use((req, res, next) =&gt; {
  req.routerStartTime = Date.now();
  next();
});

router.get("/",       (req, res) =&gt; res.json([/* list */]));
router.post("/",      (req, res) =&gt; res.status(201).json({ /* created */ }));
router.get("/:id",    (req, res) =&gt; res.json({ id: req.params.id }));
router.patch("/:id",  (req, res) =&gt; res.json({ updated: true }));
router.delete("/:id", (req, res) =&gt; res.sendStatus(204));

module.exports = router;

// app.js — mount the router
const express = require("express");
const usersRouter = require("./routes/users");
const app = express();
app.use(express.json());
app.use("/users", usersRouter);   // all router routes are prefixed with /users
// GET /users, POST /users, GET /users/:id, etc.
app.listen(3000);</code></pre>
<p><strong>Why routers matter:</strong></p>
<ul>
  <li><strong>Modularity.</strong> Each router lives in its own file; <code>app.js</code> stays tiny.</li>
  <li><strong>Scoped middleware.</strong> Auth, validation, or logging can run for one router only.</li>
  <li><strong>Reusable sub-apps.</strong> Mount the same router at multiple prefixes or plug into a completely different app.</li>
  <li><strong>Version prefixes.</strong> <code>app.use("/api/v1", v1Router)</code> and <code>app.use("/api/v2", v2Router)</code> run side by side.</li>
</ul>
<p><strong>Useful router options:</strong></p>
<ul>
  <li><code>{ mergeParams: true }</code> &mdash; child router can see the parent's URL params (e.g., <code>/users/:userId/posts</code>).</li>
  <li><code>{ caseSensitive: true }</code>, <code>{ strict: true }</code> &mdash; exact path matching.</li>
</ul>
'''

ANSWERS[17] = r'''
<p>Create each router in its own file and mount them at distinct URL prefixes with <code>app.use()</code>. This is how Express apps are kept tidy &mdash; one router per resource or feature.</p>
<pre><code>// routes/users.js
const r = require("express").Router();
r.get("/",  (req, res) =&gt; res.json({ list: "users" }));
r.get("/:id", (req, res) =&gt; res.json({ user: req.params.id }));
module.exports = r;

// routes/posts.js
const r = require("express").Router();
r.get("/",  (req, res) =&gt; res.json({ list: "posts" }));
module.exports = r;

// routes/admin.js — a router with its own middleware
const r = require("express").Router();
r.use((req, res, next) =&gt; {
  if (!req.user?.isAdmin) return res.sendStatus(403);
  next();
});
r.get("/stats", (req, res) =&gt; res.json({ users: 100, posts: 200 }));
module.exports = r;

// app.js — wire them up
const express = require("express");
const app = express();
app.use(express.json());

app.use("/api/users", require("./routes/users"));
app.use("/api/posts", require("./routes/posts"));
app.use("/api/admin", require("./routes/admin"));   // only admins reach here

app.listen(3000);</code></pre>
<p><strong>Nested routers</strong> &mdash; a router can mount another router, yielding natural hierarchy:</p>
<pre><code>// routes/users.js
const users  = require("express").Router();
const posts  = require("./user-posts");             // nested
users.use("/:userId/posts", posts);                 // /users/:userId/posts/...

// user-posts.js — use mergeParams to see :userId from parent
const r = require("express").Router({ mergeParams: true });
r.get("/", (req, res) =&gt; res.json({ user: req.params.userId, posts: [] }));</code></pre>
<p><strong>Rules of thumb:</strong> one router per resource (users, posts, orders), one router for each API version, and a separate router for admin routes so you can gate them with a single middleware. Keep <code>app.js</code> as a boot file &mdash; app setup and router mounts only.</p>
'''

ANSWERS[18] = r'''
<p><code>res.send()</code> sends a response body and automatically sets the correct <code>Content-Type</code> header based on what you pass. It's Express's one-size-fits-all response helper.</p>
<pre><code>// String → text/html (or text/plain if no markup)
app.get("/text", (req, res) =&gt; res.send("&lt;h1&gt;Hello&lt;/h1&gt;"));

// Object/Array → application/json (same as res.json)
app.get("/data", (req, res) =&gt; res.send({ ok: true, items: [1, 2, 3] }));

// Buffer → application/octet-stream
app.get("/binary", (req, res) =&gt; res.send(Buffer.from([0xde, 0xad, 0xbe, 0xef])));

// Chain with status
app.post("/users", (req, res) =&gt; res.status(201).send({ id: "u_1" }));

// Chain with headers
app.get("/", (req, res) =&gt; {
  res.set("Cache-Control", "no-store").send("dynamic");
});</code></pre>
<p><strong>What <code>res.send()</code> does behind the scenes:</strong></p>
<ul>
  <li>Computes <code>Content-Length</code> (or switches to chunked for streams).</li>
  <li>Generates an <code>ETag</code> so clients can do conditional requests.</li>
  <li>Handles <code>HEAD</code> automatically (sends headers, omits body).</li>
  <li>Terminates the response &mdash; calling <code>res.send()</code> twice throws.</li>
</ul>
<p><strong>When to reach for a different helper:</strong></p>
<ul>
  <li><code>res.json(obj)</code> &mdash; clearer intent when you know it's JSON; always sets <code>application/json</code>.</li>
  <li><code>res.sendFile(path)</code> &mdash; stream a file with proper headers.</li>
  <li><code>res.sendStatus(code)</code> &mdash; send just a status (sends the status text as the body).</li>
  <li><code>res.render("view", data)</code> &mdash; render a template engine view.</li>
  <li><code>res.redirect(url)</code> &mdash; send a 3xx location header.</li>
</ul>
<p><strong>Tip:</strong> for consistent APIs, prefer <code>res.json()</code> over <code>res.send(obj)</code>. It's explicit and avoids surprises if a colleague later passes a string.</p>
'''

ANSWERS[19] = r'''
<p>Use <code>res.redirect()</code> &mdash; it sets the <code>Location</code> header and a 3xx status code, telling the browser (or API client) to make a new request to another URL.</p>
<pre><code>// Default — 302 Found (temporary redirect)
app.get("/old", (req, res) =&gt; res.redirect("/new"));

// Permanent redirect — SEO, moved content
app.get("/old-url", (req, res) =&gt; res.redirect(301, "/new-url"));

// External URL
app.get("/docs", (req, res) =&gt; res.redirect("https://docs.example.com"));

// After POST — redirect to GET (post/redirect/get pattern)
app.post("/login", async (req, res) =&gt; {
  const ok = await verifyCredentials(req.body);
  if (!ok) return res.redirect("/login?error=1");
  res.redirect(303, "/dashboard");          // 303 = see other, force GET
});

// Referer-based "go back"
app.post("/items/:id/delete", (req, res) =&gt; {
  res.redirect("back");                      // uses Referer header, falls back to /
});

// Relative redirect (within the current app)
app.get("/", (req, res) =&gt; res.redirect("./dashboard"));</code></pre>
<p><strong>Pick the right status code:</strong></p>
<ul>
  <li><strong>301 Moved Permanently</strong> &mdash; SEO and long-term URL changes. Browsers cache this; once sent, you can't undo easily.</li>
  <li><strong>302 Found</strong> &mdash; Express's default; temporary redirect.</li>
  <li><strong>303 See Other</strong> &mdash; force a GET on the new URL regardless of the original method. Use after POSTs to prevent double submits.</li>
  <li><strong>307 Temporary Redirect</strong> &mdash; preserves the original method and body.</li>
  <li><strong>308 Permanent Redirect</strong> &mdash; like 307 but permanent.</li>
</ul>
<p><strong>Security note:</strong> never redirect to a URL read directly from user input (<code>res.redirect(req.query.next)</code>) without validating it against an allowlist &mdash; open redirects are a classic phishing vector.</p>
'''

ANSWERS[20] = r'''
<p>Both send data back to the client, but <code>res.json()</code> is <strong>specialized for JSON</strong>, while <code>res.send()</code> adapts to whatever you pass. Internally, <code>res.json()</code> calls <code>JSON.stringify()</code> and sets <code>Content-Type: application/json</code>; <code>res.send()</code> tries to figure out the type from the argument.</p>
<table>
  <thead><tr><th>Aspect</th><th><code>res.send()</code></th><th><code>res.json()</code></th></tr></thead>
  <tbody>
    <tr><td>Content-Type</td><td>Inferred (HTML, JSON, octet-stream)</td><td>Always <code>application/json</code></td></tr>
    <tr><td>Accepts</td><td>string, Buffer, object, array</td><td>any JSON-serializable value</td></tr>
    <tr><td>Serialization</td><td><code>JSON.stringify</code> only for objects</td><td>Always <code>JSON.stringify</code></td></tr>
    <tr><td>Pretty-print</td><td>No</td><td>Respects <code>"json spaces"</code> app setting</td></tr>
    <tr><td>Reviver/replacer</td><td>No</td><td>Respects <code>"json replacer"</code> setting</td></tr>
  </tbody>
</table>
<pre><code>// Functionally similar for objects
res.send({ ok: true });   // sends "application/json" because the arg is an object
res.json({ ok: true });   // same, explicit intent

// Different for strings
res.send("hello");         // text/html
res.json("hello");         // application/json, body: "hello" (note the quotes)

// res.json handles null/undefined — res.send("") can surprise
res.json(null);            // body: null
res.json(undefined);       // Express sends "undefined" literally — avoid</code></pre>
<p><strong>Rule of thumb:</strong> in an API, <strong>always use <code>res.json()</code></strong>. It's explicit, ensures the correct content type, and protects against a colleague accidentally passing a string that would be served as HTML. Reserve <code>res.send()</code> for rare cases where you deliberately send HTML or binary data.</p>
<p><strong>Bonus:</strong> <code>res.jsonp(obj)</code> wraps the response in a callback for JSONP &mdash; obsolete; modern apps use CORS instead.</p>
'''

ANSWERS[21] = r'''
<p>Express handles errors through <strong>error-handling middleware</strong> &mdash; a function with <em>four</em> parameters: <code>(err, req, res, next)</code>. Express recognizes the 4-arg signature and routes any error you pass to <code>next()</code> (or any promise rejection, in Express 5) through these handlers.</p>
<pre><code>const express = require("express");
const app = express();

app.get("/users/:id", async (req, res, next) =&gt; {
  try {
    const user = await db.user.findUnique({ where: { id: req.params.id } });
    if (!user) throw new NotFoundError("user not found");
    res.json(user);
  } catch (err) {
    next(err);                           // forward to error middleware
  }
});

// Express 5 — no try/catch needed; rejected promises go to error handlers automatically
app.get("/users/:id", async (req, res) =&gt; {
  const user = await db.user.findUniqueOrThrow({ where: { id: req.params.id } });
  res.json(user);
});

// ---- error middleware (must be LAST and have 4 args) ----
class NotFoundError extends Error { statusCode = 404; }
class ValidationError extends Error { statusCode = 400; }

app.use((err, req, res, next) =&gt; {
  const status = err.statusCode || 500;
  req.log?.error({ err, requestId: req.id }, "request failed");
  res.status(status).json({
    error: status &gt;= 500 ? "internal error" : err.message,
    ...(process.env.NODE_ENV !== "production" &amp;&amp; { stack: err.stack }),
  });
});</code></pre>
<p><strong>Rules of thumb:</strong></p>
<ul>
  <li><strong>Exactly 4 args</strong> for an error handler &mdash; 3 args is a regular middleware.</li>
  <li><strong>Put it last</strong>, after all routes. Otherwise it's never reached.</li>
  <li><strong>Use custom error classes</strong> (<code>NotFoundError</code>, <code>ValidationError</code>) with a <code>statusCode</code> &mdash; the handler maps them to HTTP responses.</li>
  <li><strong>Hide stack traces in production.</strong> Never leak internals to clients.</li>
  <li><strong>Log structured errors</strong> with a request ID so you can trace a user's failure in your logs.</li>
</ul>
<p>In Express 4, async handlers needed <code>try/catch</code> or a helper like <code>express-async-handler</code>. Express 5 forwards rejections automatically, simplifying async code significantly.</p>
'''

ANSWERS[22] = r'''
<p>Add a <strong>catch-all middleware</strong> after every other route. If no earlier route sent a response, this one fires and returns 404. Express tries routes top-to-bottom, so anything that reaches the bottom never matched.</p>
<pre><code>const express = require("express");
const app = express();

// ---- your routes ----
app.get("/", (req, res) =&gt; res.send("home"));
app.use("/api/users", require("./routes/users"));
app.use("/api/posts", require("./routes/posts"));

// ---- 404 handler (after all routes) ----
app.use((req, res, next) =&gt; {
  res.status(404).json({
    error: "Not Found",
    method: req.method,
    path:   req.originalUrl,
  });
});

// ---- error handler (LAST) ----
app.use((err, req, res, next) =&gt; {
  res.status(err.statusCode || 500).json({ error: err.message });
});

app.listen(3000);</code></pre>
<p><strong>Different content types based on the request:</strong></p>
<pre><code>app.use((req, res) =&gt; {
  res.status(404);
  res.format({
    "application/json": () =&gt; res.json({ error: "not found", path: req.originalUrl }),
    "text/html":        () =&gt; res.render("404", { url: req.originalUrl }),
    "text/plain":       () =&gt; res.send("not found"),
  });
});</code></pre>
<p><strong>Express 5 catch-all syntax:</strong></p>
<pre><code>// Use a named wildcard
app.all("/{*path}", (req, res) =&gt; {
  res.status(404).json({ error: "not found" });
});</code></pre>
<p><strong>Tips:</strong></p>
<ul>
  <li><strong>Place after all real routes</strong> &mdash; if the 404 middleware is before a route, the route is unreachable.</li>
  <li><strong>Return consistent JSON</strong> for API clients so error handling is uniform.</li>
  <li><strong>Log 404s</strong> &mdash; a sudden spike often means a broken link, a missing redirect, or an attacker scanning paths.</li>
  <li>For SPAs, instead of 404, return <code>index.html</code> on unmatched paths so client-side routing takes over &mdash; but keep the 404 for <code>/api/*</code>.</li>
</ul>
'''

ANSWERS[23] = r'''
<p>Custom middleware is just a function with the signature <code>(req, res, next)</code> (or <code>(err, req, res, next)</code> for error handling). Register it with <code>app.use()</code>, scope it to a route or router, or attach it per-endpoint.</p>
<pre><code>// 1. Simple middleware — run on every request
function logger(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next();
}
app.use(logger);

// 2. Middleware factory — parameterize the behaviour
function requireRole(role) {
  return function (req, res, next) {
    if (req.user?.role !== role) return res.status(403).json({ error: "forbidden" });
    next();
  };
}
app.get("/admin", requireRole("admin"), (req, res) =&gt; res.send("welcome"));

// 3. Async middleware (Express 5 handles rejections for you)
async function attachUser(req, res, next) {
  const token = req.headers.authorization?.slice("Bearer ".length);
  if (token) req.user = await verifyJwt(token);    // throws on invalid token
  next();
}
app.use(attachUser);

// 4. Scope to a path or router
app.use("/api", require("./middleware/requireAuth"));
app.use("/admin", requireRole("admin"), require("./routes/admin"));

// 5. Per-route chain — pass middleware as arguments
app.post("/users",
  validate(UserCreateSchema),
  requireRole("admin"),
  async (req, res) =&gt; { /* handler */ }
);</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Return <code>next()</code></strong> to avoid accidentally continuing after sending a response.</li>
  <li><strong>Never mutate headers after sending.</strong> Errors like "headers already sent" usually mean a middleware and a handler both tried to respond.</li>
  <li><strong>Keep middleware single-purpose</strong> &mdash; logging, auth, validation, rate-limit. Don't mix concerns.</li>
  <li><strong>Use factories</strong> (<code>requireRole(role)</code>) for configurable middleware; returns a closure over the args.</li>
  <li><strong>Attach data to <code>req</code></strong> (not <code>res</code>) for downstream handlers: <code>req.user</code>, <code>req.tenant</code>.</li>
</ul>
'''

ANSWERS[24] = r'''
<p><code>app.use()</code> mounts a <strong>middleware or router</strong> on the app &mdash; either globally (runs for every request) or scoped to a URL prefix. It's the most common method you'll call when wiring up an Express app.</p>
<pre><code>// 1. Global middleware — runs on every request, in order
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(require("cors")());
app.use(require("helmet")());
app.use(require("morgan")("combined"));

// 2. Path-scoped — only runs when the URL starts with /api
app.use("/api", require("./middleware/rateLimit"));

// 3. Mount a router at a prefix — the most common case
app.use("/api/users", require("./routes/users"));
// Inside users router: router.get("/") handles GET /api/users

// 4. Multiple middleware at once
app.use("/admin", requireAuth, requireAdmin, adminRouter);

// 5. Error-handling middleware — registered with app.use but with 4 args
app.use((err, req, res, next) =&gt; {
  res.status(500).json({ error: err.message });
});</code></pre>
<p><strong>What <code>app.use()</code> does NOT do:</strong></p>
<ul>
  <li><strong>It doesn't match an exact URL</strong> &mdash; it matches any URL that <em>starts with</em> the given prefix. <code>app.use("/admin", mw)</code> runs for <code>/admin</code>, <code>/admin/users</code>, <code>/admin/anything</code>.</li>
  <li><strong>It doesn't restrict by method.</strong> Use <code>app.get</code>, <code>app.post</code>, etc., to register method-specific routes.</li>
</ul>
<p><strong>Order matters</strong> &mdash; middleware runs in registration order. A common pattern:</p>
<pre><code>app.use(helmet());                           // security headers
app.use(cors());                             // CORS
app.use(express.json());                     // body parsing
app.use(morgan("combined"));                 // request logging
app.use("/api", apiRouter);                  // routes
app.use((req, res) =&gt; res.sendStatus(404));  // 404
app.use(errorHandler);                       // errors (4-arg, always last)</code></pre>
'''

ANSWERS[25] = r'''
<p><strong>Third-party middleware</strong> is any npm package exporting a function (or factory) compatible with Express's <code>(req, res, next)</code> signature. Install, import, register with <code>app.use()</code>. The ecosystem is massive; a few are effectively standard in every production Express app.</p>
<pre><code>// Install the essentials
// npm i helmet cors morgan express-rate-limit compression cookie-parser

const express = require("express");
const helmet  = require("helmet");
const cors    = require("cors");
const morgan  = require("morgan");
const rateLimit   = require("express-rate-limit");
const compression = require("compression");
const cookieParser = require("cookie-parser");

const app = express();

// --- standard middleware stack ---
app.use(helmet());                                         // security headers
app.use(cors({ origin: ["https://app.example.com"] }));    // CORS policy
app.use(compression());                                    // gzip/brotli responses
app.use(morgan("combined"));                               // request log
app.use(express.json());                                   // JSON body parser
app.use(express.urlencoded({ extended: true }));           // form body parser
app.use(cookieParser());                                   // req.cookies

// --- scoped middleware ---
app.use("/api", rateLimit({
  windowMs: 60_000,
  max:      100,
  standardHeaders: true,   // RateLimit-* headers
}));

// --- factories accept options ---
app.use(morgan("combined", {
  skip: (req, res) =&gt; res.statusCode &lt; 400,   // only log errors
}));</code></pre>
<p><strong>The "default" Express middleware stack</strong> for a production API in 2026:</p>
<ul>
  <li><code>helmet</code> &mdash; sensible security headers (CSP, HSTS, X-Frame-Options).</li>
  <li><code>cors</code> &mdash; Cross-Origin Resource Sharing configuration.</li>
  <li><code>compression</code> &mdash; gzip/brotli response compression.</li>
  <li><code>morgan</code> or <code>pino-http</code> &mdash; structured request logging.</li>
  <li><code>express-rate-limit</code> &mdash; block brute-force and runaway clients.</li>
  <li><code>cookie-parser</code> &mdash; populate <code>req.cookies</code>.</li>
  <li><code>express-session</code> + store (Redis) &mdash; stateful sessions (if needed).</li>
</ul>
<p><strong>Evaluating a package:</strong> check weekly downloads, last publish date (&lt; 12 months is a good sign), open issues, and security advisories (<code>npm audit</code>). Prefer packages from the <code>expressjs</code> GitHub org &mdash; they're officially maintained.</p>
'''

ANSWERS[26] = r'''
<p>Sessions store per-user state on the <strong>server</strong>, identified by a session ID kept in a cookie. Use the <code>express-session</code> middleware &mdash; don't roll your own. It generates the ID, sets the cookie, and loads/saves session data on every request.</p>
<pre><code>// npm i express-session connect-redis redis
const session = require("express-session");
const { RedisStore } = require("connect-redis");
const { createClient } = require("redis");

const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

app.use(session({
  store: new RedisStore({ client: redisClient }),    // production-grade store
  secret: process.env.SESSION_SECRET,                // signs the session cookie
  name:  "sid",                                      // don't use the default "connect.sid"
  resave: false,                                     // don't re-save unchanged sessions
  saveUninitialized: false,                          // don't create session until needed
  cookie: {
    httpOnly: true,                                  // no JS access
    secure:   process.env.NODE_ENV === "production", // HTTPS only
    sameSite: "lax",                                 // CSRF protection
    maxAge:   7 * 24 * 3600 * 1000,                  // 1 week
  },
}));

// Read/write on req.session
app.post("/login", async (req, res) =&gt; {
  const user = await authenticate(req.body.email, req.body.password);
  if (!user) return res.status(401).send("invalid");
  req.session.regenerate((err) =&gt; {                  // new ID to prevent fixation
    req.session.userId = user.id;
    res.redirect("/dashboard");
  });
});

app.post("/logout", (req, res) =&gt; {
  req.session.destroy(() =&gt; {
    res.clearCookie("sid");
    res.redirect("/");
  });
});</code></pre>
<p><strong>Critical pitfalls:</strong></p>
<ul>
  <li><strong>Never use the default <code>MemoryStore</code> in production.</strong> It leaks memory and dies with the process. Use Redis, Postgres, or DynamoDB.</li>
  <li><strong>Regenerate the session on login</strong> to prevent session fixation.</li>
  <li><strong>Set a strong, long <code>secret</code></strong> (32+ chars) and rotate periodically.</li>
  <li><strong>Prefer JWT + short-lived tokens</strong> for stateless APIs and mobile clients; sessions shine for server-rendered web apps.</li>
</ul>
'''

ANSWERS[27] = r'''
<p>Cookies are small key/value strings the browser stores and sends on every matching request. Express reads them from the <code>Cookie</code> header (with the <code>cookie-parser</code> middleware) and sets them via <code>res.cookie()</code>/<code>res.clearCookie()</code>.</p>
<pre><code>// npm i cookie-parser
const cookieParser = require("cookie-parser");

app.use(cookieParser(process.env.COOKIE_SECRET));   // secret enables signed cookies

// READ — plain and signed cookies
app.get("/whoami", (req, res) =&gt; {
  const theme   = req.cookies.theme;               // plain
  const session = req.signedCookies.sid;           // verified signature
  res.json({ theme, session });
});

// SET — with secure defaults
app.get("/prefs", (req, res) =&gt; {
  res.cookie("theme", "dark", {
    httpOnly: true,                                // not visible to JS
    secure:   true,                                // HTTPS only
    sameSite: "lax",                               // CSRF protection
    maxAge:   30 * 24 * 3600 * 1000,               // 30 days
    path:     "/",
  });
  res.send("ok");
});

// SIGNED cookie — value is tamper-proof (HMAC) but NOT encrypted
res.cookie("sid", userId, { signed: true, httpOnly: true, secure: true });

// CLEAR — options MUST match how it was set (path, domain, sameSite)
res.clearCookie("theme", { path: "/" });</code></pre>
<p><strong>Cookie attributes that matter:</strong></p>
<table>
  <thead><tr><th>Attribute</th><th>Effect</th></tr></thead>
  <tbody>
    <tr><td><code>httpOnly</code></td><td>JS can't read the cookie &mdash; defense against XSS stealing it</td></tr>
    <tr><td><code>secure</code></td><td>Only sent over HTTPS &mdash; prevents network sniffing</td></tr>
    <tr><td><code>sameSite</code></td><td><code>strict</code> / <code>lax</code> / <code>none</code> &mdash; primary CSRF defense today</td></tr>
    <tr><td><code>maxAge</code> or <code>expires</code></td><td>Lifetime &mdash; omit for session cookies (cleared on browser close)</td></tr>
    <tr><td><code>domain</code></td><td>Subdomain sharing &mdash; leave unset unless you know you need it</td></tr>
  </tbody>
</table>
<p><strong>Rules:</strong> anything sensitive (session IDs, auth tokens) must be <code>httpOnly + secure + sameSite</code>. Signed cookies prevent tampering but don't hide the value &mdash; never put secrets in a cookie.</p>
'''

ANSWERS[28] = r'''
<p><code>express-session</code> is the official Express middleware for <strong>server-side sessions</strong>. It generates a session ID, stores it in a cookie, keeps the session data in a pluggable store, and hydrates <code>req.session</code> on every request.</p>
<pre><code>const session = require("express-session");

app.use(session({
  secret: process.env.SESSION_SECRET,    // signs the sid cookie
  resave: false,                         // don't write session on every request
  saveUninitialized: false,              // don't save empty sessions (no cookie until touched)
  name: "sid",                           // custom cookie name (safer than default)
  cookie: {
    httpOnly: true,
    secure:   true,
    sameSite: "lax",
    maxAge:   3600_000,                  // 1 hour
  },
  store: new RedisStore({ client: redis }),  // required for production
}));

// Use req.session anywhere in your routes
app.get("/visits", (req, res) =&gt; {
  req.session.count = (req.session.count ?? 0) + 1;
  res.send(`visit #${req.session.count}`);
});</code></pre>
<p><strong>Key responsibilities it handles for you:</strong></p>
<ul>
  <li><strong>Session ID generation</strong> &mdash; cryptographically random; signed with your secret.</li>
  <li><strong>Cookie management</strong> &mdash; sets the cookie on first write, respects expiration.</li>
  <li><strong>Store integration</strong> &mdash; load session data on request, save on response end.</li>
  <li><strong>API on <code>req.session</code></strong> &mdash; <code>regenerate()</code> (new ID), <code>destroy()</code> (logout), <code>touch()</code> (refresh expiry), <code>save()</code> (force flush).</li>
</ul>
<p><strong>Production store options:</strong></p>
<ul>
  <li><strong><code>connect-redis</code></strong> &mdash; industry standard; fast, supports TTL, works across multiple Node instances.</li>
  <li><strong><code>connect-pg-simple</code></strong> &mdash; Postgres-backed; useful if you already have Postgres and want one less service.</li>
  <li><strong><code>connect-mongo</code></strong> &mdash; MongoDB-backed.</li>
  <li><strong><code>connect-dynamodb</code></strong> &mdash; serverless-friendly.</li>
</ul>
<p><strong>Never</strong> use the default <code>MemoryStore</code> outside of dev &mdash; it leaks, doesn't survive restarts, and breaks across horizontally-scaled nodes.</p>
'''

ANSWERS[29] = r'''
<p>Express doesn't parse <code>multipart/form-data</code> (the encoding for file uploads) natively. Use <code>multer</code> &mdash; the de-facto standard multipart parser for Express. It streams bytes to disk or memory, exposes file metadata on <code>req.file</code> / <code>req.files</code>, and handles multiple fields.</p>
<pre><code>// npm i multer
const multer = require("multer");
const path = require("node:path");

// Disk storage — writes files directly to a folder
const upload = multer({
  dest: "uploads/",                             // temp directory
  limits: {
    fileSize: 5 * 1024 * 1024,                  // 5 MB per file
    files:    10,                               // max number of files
  },
  fileFilter: (req, file, cb) =&gt; {
    const ok = /^image\/(jpeg|png|webp|gif)$/.test(file.mimetype);
    cb(ok ? null : new Error("unsupported file type"), ok);
  },
});

// Single file
app.post("/avatar", upload.single("avatar"), (req, res) =&gt; {
  // req.file = { fieldname, originalname, mimetype, size, path, ... }
  // req.body has other text fields
  res.json({ file: req.file, fields: req.body });
});

// Multiple files under the same field
app.post("/gallery", upload.array("photos", 10), (req, res) =&gt; {
  res.json({ files: req.files });
});

// Multiple fields with different limits
app.post("/profile", upload.fields([
  { name: "avatar", maxCount: 1 },
  { name: "cover",  maxCount: 1 },
]), (req, res) =&gt; {
  res.json({ avatar: req.files.avatar, cover: req.files.cover });
});</code></pre>
<p><strong>Memory vs disk vs direct-to-S3:</strong></p>
<ul>
  <li><code>multer.diskStorage(...)</code> &mdash; good for files you'll process locally; control filename and path.</li>
  <li><code>multer.memoryStorage()</code> &mdash; file arrives as a Buffer; fine for small uploads you'll forward to S3 or a processor like <code>sharp</code>.</li>
  <li><strong>Pre-signed S3 URLs</strong> &mdash; for production: client PUTs directly to S3/R2, your API just issues a signed URL. Saves bandwidth, avoids buffering huge files in Node.</li>
</ul>
<p><strong>Security essentials:</strong> always set <code>fileSize</code> and <code>files</code> limits, validate both <code>mimetype</code> and magic bytes (<code>file-type</code> package), rename uploads (never trust <code>originalname</code>), and scan for malware if users share files with each other.</p>
'''

ANSWERS[30] = r'''
<p><code>multer</code> is the Express middleware for <code>multipart/form-data</code> &mdash; the encoding browsers use when a form contains <code>&lt;input type="file"&gt;</code>. You configure a storage engine and limits, create an upload instance, and attach it to routes as middleware.</p>
<pre><code>const multer = require("multer");
const path = require("node:path");
const crypto = require("node:crypto");

// ---- configured storage ----
const storage = multer.diskStorage({
  destination: (req, file, cb) =&gt; cb(null, "uploads/"),
  filename:    (req, file, cb) =&gt; {
    // Always generate your own name — never trust originalname
    const ext  = path.extname(file.originalname).toLowerCase();
    const name = crypto.randomBytes(16).toString("hex") + ext;
    cb(null, name);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },    // 10 MB
  fileFilter: (req, file, cb) =&gt; {
    const allowed = ["image/jpeg", "image/png", "image/webp"];
    cb(allowed.includes(file.mimetype) ? null : new Error("bad type"));
  },
});

// ---- routes ----
app.post("/upload", upload.single("file"), (req, res) =&gt; {
  res.json({ url: `/uploads/${req.file.filename}`, size: req.file.size });
});

// ---- error handling for limit errors ----
app.use((err, req, res, next) =&gt; {
  if (err instanceof multer.MulterError) {
    return res.status(413).json({ error: err.code });   // e.g. LIMIT_FILE_SIZE
  }
  next(err);
});</code></pre>
<p><strong>multer's middleware variants:</strong></p>
<ul>
  <li><code>upload.single(name)</code> &mdash; one file at <code>req.file</code>.</li>
  <li><code>upload.array(name, max)</code> &mdash; multiple files in one field at <code>req.files</code>.</li>
  <li><code>upload.fields([{name,maxCount}, ...])</code> &mdash; different file fields with their own limits.</li>
  <li><code>upload.any()</code> &mdash; accept all files (avoid in production &mdash; too permissive).</li>
  <li><code>upload.none()</code> &mdash; text-only multipart (files rejected).</li>
</ul>
<p><strong>Production pattern:</strong> accept the file with <code>multer.memoryStorage()</code>, validate magic bytes (<code>file-type</code> package), run <code>sharp</code> for images, and stream to S3 via <code>@aws-sdk/client-s3</code>. Better still, bypass Node entirely with <strong>pre-signed S3 URLs</strong> so the file never touches your server.</p>
'''

ANSWERS[31] = r'''
<p><code>res.status(code)</code> sets the HTTP status code for the response. It <em>returns <code>res</code></em> so it chains with any send method &mdash; <code>.json()</code>, <code>.send()</code>, <code>.end()</code>, <code>.render()</code>.</p>
<pre><code>// Set and send in one line
app.post("/users", (req, res) =&gt; {
  res.status(201).json({ id: "u_1", name: "Ada" });
});

app.get("/missing", (req, res) =&gt; {
  res.status(404).json({ error: "not found" });
});

// Client errors
app.get("/forbidden", (req, res) =&gt; res.status(403).send("forbidden"));

// Status-only response (use sendStatus for convenience)
res.sendStatus(204);                    // "No Content"
res.sendStatus(401);                    // body: "Unauthorized"

// NOT what res.status(200) does:
//   - doesn't send the response
//   - doesn't end the request
//   - just sets the code on the outgoing headers</code></pre>
<p><strong>Common status codes to know:</strong></p>
<table>
  <thead><tr><th>Range</th><th>Meaning</th><th>Examples</th></tr></thead>
  <tbody>
    <tr><td>2xx</td><td>Success</td><td>200 OK, 201 Created, 204 No Content</td></tr>
    <tr><td>3xx</td><td>Redirect</td><td>301 Moved Permanently, 302 Found, 304 Not Modified</td></tr>
    <tr><td>4xx</td><td>Client error</td><td>400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable, 429 Too Many Requests</td></tr>
    <tr><td>5xx</td><td>Server error</td><td>500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout</td></tr>
  </tbody>
</table>
<p><strong>Tips:</strong> use meaningful codes &mdash; <code>201</code> after creates, <code>204</code> after deletes (no body), <code>401</code> for unauthenticated, <code>403</code> for authorized-but-not-allowed. Don't blanket every error as <code>500</code>; that hides real problems. <code>res.sendStatus(code)</code> is a shortcut for status + a plain-text body matching that status.</p>
'''

ANSWERS[32] = r'''
<p>Set response headers with <code>res.set()</code> (or the alias <code>res.header()</code>) or <code>res.setHeader()</code> from the underlying Node API. Express returns <code>res</code> so it chains. Headers must be set <em>before</em> the response body starts streaming.</p>
<pre><code>// Set one header
res.set("Content-Type", "application/json; charset=utf-8");

// Set many at once
res.set({
  "X-Api-Version":     "v1",
  "Cache-Control":     "no-store",
  "X-Request-Id":      req.id,
});

// Chain
app.get("/api/me", (req, res) =&gt; {
  res
    .status(200)
    .set("Cache-Control", "private, max-age=60")
    .set("X-Served-By", process.env.HOSTNAME)
    .json({ id: req.user.id });
});

// Append (for headers like Set-Cookie, Vary that allow multiple)
res.append("Vary", "Accept-Encoding");
res.append("Vary", "Authorization");

// Remove a header
res.removeHeader("X-Powered-By");</code></pre>
<p><strong>Response-helper shortcuts:</strong></p>
<ul>
  <li><code>res.type("application/json")</code> or <code>res.type("json")</code> &mdash; Content-Type shorthand.</li>
  <li><code>res.location("/dashboard")</code> &mdash; Location header (used by redirects).</li>
  <li><code>res.links({ next: "/page/2", prev: "/page/1" })</code> &mdash; RFC 5988 link header.</li>
  <li><code>res.attachment("report.pdf")</code> &mdash; Content-Disposition: attachment.</li>
  <li><code>res.cookie(name, val, opts)</code> &mdash; Set-Cookie.</li>
  <li><code>res.vary("Accept-Encoding")</code> &mdash; shortcut for the Vary header.</li>
</ul>
<p><strong>Security headers</strong> (letter <code>helmet</code> handle most of these for you):</p>
<pre><code>res.set({
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "X-Content-Type-Options":    "nosniff",
  "X-Frame-Options":           "DENY",
  "Content-Security-Policy":   "default-src 'self'",
  "Referrer-Policy":           "strict-origin-when-cross-origin",
});</code></pre>
<p><strong>Common pitfall:</strong> "Cannot set headers after they are sent to the client" &mdash; you called <code>res.send()</code> earlier, or your code has two paths that both try to respond. Return after sending: <code>return res.json(data)</code>.</p>
'''

ANSWERS[33] = r'''
<p>Use <code>res.sendFile()</code> to stream a file with the right headers, or <code>res.download()</code> to force a "Save As" prompt. Both take an <em>absolute</em> file path and handle <code>Content-Type</code>, <code>Content-Length</code>, and <code>ETag</code> automatically.</p>
<pre><code>const path = require("node:path");

// Serve a PDF inline (viewer opens in the browser)
app.get("/invoice", (req, res) =&gt; {
  const file = path.join(__dirname, "files", "invoice.pdf");
  res.sendFile(file, (err) =&gt; {
    if (err) next(err);
  });
});

// Force a download dialog with a specific filename
app.get("/report", (req, res) =&gt; {
  res.download(
    path.join(__dirname, "files", "q4.pdf"),
    "report-q4.pdf",                    // name the browser suggests
    (err) =&gt; { if (err) next(err); }
  );
});

// Custom options (range requests, caching, dotfiles)
res.sendFile(file, {
  root:     path.join(__dirname, "files"),       // safer than absolute paths
  maxAge:   "1h",                                // Cache-Control
  acceptRanges: true,                            // supports byte-range requests (video/audio seek)
  dotfiles: "deny",                              // refuse .env, .git files
  headers:  { "X-From": "node" },
});

// Streaming manually — needed for generated files, S3, or large data
const { createReadStream, statSync } = require("node:fs");
app.get("/log", (req, res) =&gt; {
  const file = "/var/log/app.log";
  res.set({
    "Content-Type":   "text/plain",
    "Content-Length": statSync(file).size,
  });
  createReadStream(file).pipe(res);              // backpressure-safe
});</code></pre>
<p><strong>Picking the right method:</strong></p>
<ul>
  <li><code>res.sendFile()</code> &mdash; show inline (PDFs, images).</li>
  <li><code>res.download()</code> &mdash; force download with a nice filename.</li>
  <li><code>res.attachment(name)</code> + manual pipe &mdash; full control over streaming/generation.</li>
  <li><code>express.static()</code> &mdash; whole directories of files; the most efficient for static assets.</li>
</ul>
<p><strong>Security:</strong> NEVER build the path by concatenating user input (<code>req.query.file</code>) &mdash; that's a path-traversal vulnerability (<code>../../../etc/passwd</code>). Use the <code>root</code> option, validate against an allowlist, or look up the real path in a database.</p>
'''

ANSWERS[34] = r'''
<p><code>app.listen()</code> starts the HTTP server on a given port. Under the hood it creates a Node <code>http.Server</code>, passes the Express app as its request handler, and calls <code>server.listen(...)</code>. It returns that server &mdash; useful if you need to close it, attach WebSockets, or do graceful shutdown.</p>
<pre><code>const app = require("express")();
const PORT = process.env.PORT || 3000;

// Simplest form
app.listen(PORT, () =&gt; console.log(`http://localhost:${PORT}`));

// Bind to a specific interface (important in containers)
app.listen(PORT, "0.0.0.0", () =&gt; { /* ... */ });
// Default is "::" which listens on all interfaces; "localhost" binds to loopback only

// Capture the server for later control
const server = app.listen(PORT);

// Graceful shutdown — critical in production
function shutdown(signal) {
  console.log(`${signal} received, closing server...`);
  server.close((err) =&gt; {                    // stop accepting new connections
    if (err) { console.error(err); process.exit(1); }
    console.log("all connections drained");
    process.exit(0);
  });
  setTimeout(() =&gt; process.exit(1), 30_000).unref();   // force-exit after 30s
}
process.on("SIGTERM", () =&gt; shutdown("SIGTERM"));
process.on("SIGINT",  () =&gt; shutdown("SIGINT"));</code></pre>
<p><strong>What <code>app.listen()</code> is actually equivalent to:</strong></p>
<pre><code>const http = require("node:http");
const server = http.createServer(app);     // app is just an HTTP request handler
server.listen(3000);</code></pre>
<p>Write it the verbose way when you need to:</p>
<ul>
  <li>Attach a <strong>WebSocket server</strong> (<code>new WebSocketServer({ server })</code>) or Socket.IO.</li>
  <li>Create an <strong>HTTPS server</strong> (<code>https.createServer({ key, cert }, app)</code>).</li>
  <li>Run <strong>multiple apps</strong> on the same port with different hostnames.</li>
</ul>
<p><strong>Port conventions:</strong> read from <code>process.env.PORT</code> (required on Heroku, Railway, Render, Cloud Run). Don't bind below 1024 without privileges. Bind to <code>0.0.0.0</code> in Docker &mdash; <code>localhost</code> won't be reachable from outside the container.</p>
'''

ANSWERS[35] = r'''
<p><strong>CORS</strong> (Cross-Origin Resource Sharing) is the browser rule that blocks requests from one origin to another unless the target server says the origin is allowed. Use the <code>cors</code> middleware &mdash; it reads the request, evaluates your policy, and writes the right <code>Access-Control-*</code> headers.</p>
<pre><code>// npm i cors
const cors = require("cors");

// Allow everyone — only OK for fully public APIs (no cookies, no auth)
app.use(cors());

// Allow a specific origin
app.use(cors({
  origin: "https://app.example.com",
  credentials: true,                          // allow cookies / Authorization
}));

// Allowlist — multiple origins with validation
const allowed = new Set([
  "https://app.example.com",
  "https://admin.example.com",
  "http://localhost:5173",                    // dev
]);
app.use(cors({
  origin: (origin, cb) =&gt; {
    if (!origin || allowed.has(origin)) return cb(null, true);
    cb(new Error(`CORS: origin ${origin} not allowed`));
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"],
  exposedHeaders: ["X-Request-Id", "RateLimit-Remaining"],
  maxAge: 600,                                // cache the preflight for 10 minutes
}));

// Per-route — restrict CORS to one endpoint
app.get("/public", cors({ origin: "*" }), (req, res) =&gt; res.json({ ok: true }));</code></pre>
<p><strong>Important details:</strong></p>
<ul>
  <li><strong>Preflight:</strong> for non-simple requests (custom headers, non-GET methods), the browser first sends an <code>OPTIONS</code> request. The <code>cors</code> middleware handles it automatically &mdash; install it <em>before</em> your routes.</li>
  <li><strong>Wildcard + credentials don't mix.</strong> <code>origin: "*"</code> with <code>credentials: true</code> is invalid; the browser will reject. Echo the specific origin instead.</li>
  <li><strong><code>sameSite=none</code> cookies</strong> must also be <code>secure=true</code> (HTTPS-only).</li>
  <li><strong>CORS is a browser thing.</strong> Server-to-server calls ignore CORS entirely &mdash; it's not a server-side security control.</li>
  <li><strong>Don't use CORS as your auth layer.</strong> Always require tokens/sessions regardless of origin.</li>
</ul>
<p><strong>Common error:</strong> "No 'Access-Control-Allow-Origin' header is present" &mdash; usually the <code>cors</code> middleware isn't installed, is installed after the failing route, or your origin isn't on the allowlist.</p>
'''

ANSWERS[36] = r'''
<p>Wildcards match any URL segments that aren't otherwise routed. In Express 5, the syntax tightened up &mdash; you use <code>{*name}</code> for a named wildcard. Wildcards are useful for catch-all 404 handlers, SPA fallbacks, and proxying.</p>
<pre><code>// Express 5 — named wildcard (required)
app.get("/files/{*path}", (req, res) =&gt; {
  // req.params.path = "a/b/c" for GET /files/a/b/c
  res.send(req.params.path);
});

// Catch-all at the end — 404 handler
app.all("/{*any}", (req, res) =&gt; {
  res.status(404).json({ error: "not found", path: req.originalUrl });
});

// SPA fallback — serve index.html for any unmatched path
app.get("/{*path}", (req, res) =&gt; {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

// Regex routes — when you need validation beyond a simple pattern
app.get(/^\/user\/\d+$/, (req, res) =&gt; {
  // Only matches /user/123, not /user/abc
  res.send("valid user id");
});</code></pre>
<p><strong>Express 4 vs 5 syntax:</strong></p>
<table>
  <thead><tr><th>Pattern</th><th>Express 4</th><th>Express 5</th></tr></thead>
  <tbody>
    <tr><td>Optional param</td><td><code>/users/:id?</code></td><td><code>/users{/:id}</code></td></tr>
    <tr><td>Unnamed wildcard</td><td><code>*</code></td><td><code>{*splat}</code> (must be named)</td></tr>
    <tr><td>Catch rest of path</td><td><code>/files/*</code></td><td><code>/files/{*path}</code></td></tr>
  </tbody>
</table>
<p><strong>Where to put catch-all routes:</strong></p>
<ul>
  <li><strong>Last.</strong> A wildcard that matches everything, registered first, swallows all traffic.</li>
  <li><strong>After your API routes</strong> but before the error handler, if you want a 404 JSON response.</li>
  <li><strong>Behind an API path prefix</strong> for SPAs: <code>/api</code> routes return JSON errors, <code>/*</code> returns the SPA shell.</li>
</ul>
<p><strong>Migration note:</strong> if you're porting from Express 4, <code>app.get("*", handler)</code> works in v4 but needs to be <code>app.get("/{*any}", handler)</code> or <code>app.use(handler)</code> in v5. Running <code>npm audit</code> against your routes during upgrade catches most of these.</p>
'''

ANSWERS[37] = r'''
<p>Express supports <strong>template engines</strong> that render HTML from templates + data via <code>res.render()</code>. Configure the engine with <code>app.set("view engine", ...)</code> and Express will auto-look up template files in the <code>views/</code> directory.</p>
<pre><code>// npm i ejs   (or: pug, handlebars, express-handlebars, etc.)
const express = require("express");
const path = require("node:path");

const app = express();

// 1. Tell Express where templates live and which engine to use
app.set("views", path.join(__dirname, "views"));   // directory
app.set("view engine", "ejs");                     // extension

// 2. Render a view and pass locals (data)
app.get("/", (req, res) =&gt; {
  res.render("home", {
    title:  "Welcome",
    user:   req.user,
    items:  ["apples", "oranges", "pears"],
  });
});

// views/home.ejs
// &lt;!doctype html&gt;
// &lt;html&gt;&lt;head&gt;&lt;title&gt;&lt;%= title %&gt;&lt;/title&gt;&lt;/head&gt;
// &lt;body&gt;
//   &lt;h1&gt;Hello, &lt;%= user?.name ?? "guest" %&gt;&lt;/h1&gt;
//   &lt;ul&gt;&lt;% items.forEach(i =&gt; { %&gt;&lt;li&gt;&lt;%= i %&gt;&lt;/li&gt;&lt;% }); %&gt;&lt;/ul&gt;
// &lt;/body&gt;&lt;/html&gt;</code></pre>
<p><strong>Shared data across all views:</strong></p>
<pre><code>// res.locals persists for the lifetime of one request
app.use((req, res, next) =&gt; {
  res.locals.currentYear = new Date().getFullYear();
  res.locals.user        = req.user;
  next();
});

// app.locals is the same for every request (e.g. site title)
app.locals.siteName = "Acme";</code></pre>
<p><strong>Popular engines (2026):</strong></p>
<table>
  <thead><tr><th>Engine</th><th>Syntax</th><th>Use case</th></tr></thead>
  <tbody>
    <tr><td><strong>EJS</strong></td><td><code>&lt;%= %&gt;</code> (HTML-like)</td><td>Fast to learn, HTML-native</td></tr>
    <tr><td><strong>Pug</strong></td><td>Indentation-based</td><td>Concise, Jade-heritage</td></tr>
    <tr><td><strong>Handlebars</strong></td><td><code>{{name}}</code>, logic-less</td><td>Shared client/server templates</td></tr>
    <tr><td><strong>Eta</strong></td><td>EJS-like, modern</td><td>Lightweight replacement for EJS</td></tr>
    <tr><td><strong>Nunjucks</strong></td><td>Jinja2-like</td><td>Rich inheritance, filters</td></tr>
  </tbody>
</table>
<p><strong>Note:</strong> for anything interactive, a SPA framework (React, Vue, Svelte) served by a meta-framework (Next.js, Remix, Nuxt, SvelteKit) is more common today. Template engines still shine for server-rendered pages with minimal JS &mdash; marketing pages, admin tools, transactional emails.</p>
'''

ANSWERS[38] = r'''
<p><code>res.render(view, locals)</code> compiles and renders a template file into HTML, then sends it as the response. It uses the view engine you set with <code>app.set("view engine", ...)</code> and looks inside <code>app.get("views")</code>.</p>
<pre><code>app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Basic render
app.get("/about", (req, res) =&gt; {
  res.render("about", { title: "About Us", company: "Acme" });
});

// With a shared layout (via express-ejs-layouts or partials)
app.get("/dashboard", async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.session.userId } });
  res.render("dashboard", {
    title: "Dashboard",
    user,
    stats: await getStats(user.id),
  });
});

// Explicit callback — catch render errors without letting them hang
app.get("/profile", (req, res, next) =&gt; {
  res.render("profile", { user: req.user }, (err, html) =&gt; {
    if (err) return next(err);
    res.send(html);
  });
});

// With an absolute path
res.render(path.resolve("views/email/welcome.ejs"), { name: req.user.name });</code></pre>
<p><strong>How it resolves the view file:</strong></p>
<ol>
  <li>Starts from the configured <code>views</code> directory.</li>
  <li>Appends the <code>view engine</code> extension if missing.</li>
  <li>Delegates to the engine (EJS, Pug, Handlebars&hellip;) to compile and render.</li>
</ol>
<p><strong>Locals precedence</strong> (later wins):</p>
<ul>
  <li><code>app.locals</code> &mdash; app-wide (site name, nav items).</li>
  <li><code>res.locals</code> &mdash; per-request (current user, request ID).</li>
  <li>The object passed to <code>res.render(view, locals)</code> &mdash; per-call.</li>
</ul>
<p><strong>Use cases:</strong> server-rendered admin dashboards, transactional emails (render once, send via <code>res.locals</code> helpers), marketing pages with good SEO. For data-heavy apps, template engines usually give way to a meta-framework &mdash; but for a simple dashboard, <code>res.render()</code> is a two-line win.</p>
'''

ANSWERS[39] = r'''
<p><strong>EJS</strong> ("Embedded JavaScript") is a simple templating engine where you embed <code>&lt;% JS %&gt;</code> inside plain HTML. It's the easiest engine to adopt because the template is essentially the HTML you already write.</p>
<pre><code>// npm i ejs
const express = require("express");
const path = require("node:path");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.get("/", (req, res) =&gt; {
  res.render("index", {
    title: "Home",
    user:  { name: "Ada", admin: true },
    items: ["apples", "oranges", "pears"],
  });
});

// views/index.ejs
// &lt;!doctype html&gt;
// &lt;html&gt;
//   &lt;head&gt;&lt;title&gt;&lt;%= title %&gt;&lt;/title&gt;&lt;/head&gt;
//   &lt;body&gt;
//     &lt;h1&gt;Hi, &lt;%= user.name %&gt;&lt;/h1&gt;
//     &lt;% if (user.admin) { %&gt;
//       &lt;a href="/admin"&gt;Admin panel&lt;/a&gt;
//     &lt;% } %&gt;
//     &lt;ul&gt;
//       &lt;% items.forEach(function(i) { %&gt;
//         &lt;li&gt;&lt;%= i %&gt;&lt;/li&gt;
//       &lt;% }); %&gt;
//     &lt;/ul&gt;
//     &lt;%- include("partials/footer") %&gt;
//   &lt;/body&gt;
// &lt;/html&gt;</code></pre>
<p><strong>EJS tag reference:</strong></p>
<table>
  <thead><tr><th>Tag</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>&lt;% code %&gt;</code></td><td>Plain JS (no output)</td></tr>
    <tr><td><code>&lt;%= value %&gt;</code></td><td>Output, <strong>HTML-escaped</strong> (safe)</td></tr>
    <tr><td><code>&lt;%- value %&gt;</code></td><td>Output, <strong>unescaped</strong> (raw HTML &mdash; XSS risk!)</td></tr>
    <tr><td><code>&lt;%# comment %&gt;</code></td><td>Comment (stripped from output)</td></tr>
    <tr><td><code>&lt;%- include("partial") %&gt;</code></td><td>Include another template file</td></tr>
  </tbody>
</table>
<p><strong>For layouts</strong> (shared header/footer), install <code>express-ejs-layouts</code> or use partials with <code>include()</code>. EJS doesn't have built-in inheritance.</p>
<p><strong>Security:</strong> <code>&lt;%= %&gt;</code> auto-escapes user input; only use <code>&lt;%- %&gt;</code> for content you fully control (pre-rendered Markdown from your own DB after sanitization). Leaking user input through <code>&lt;%- %&gt;</code> is the classic XSS mistake.</p>
'''

ANSWERS[40] = r'''
<p><strong>Pug</strong> (originally "Jade") is an indentation-based template language &mdash; no closing tags, no angle brackets. Concise and expressive once you learn it, but the strict whitespace rules are a gotcha for newcomers.</p>
<pre><code>// npm i pug
const express = require("express");
const path = require("node:path");

const app = express();
app.set("view engine", "pug");
app.set("views", path.join(__dirname, "views"));

app.get("/", (req, res) =&gt; {
  res.render("index", {
    title: "Home",
    user:  { name: "Ada", admin: true },
    items: ["apples", "oranges", "pears"],
  });
});

// views/index.pug
// doctype html
// html
//   head
//     title= title
//   body
//     h1 Hi, #{user.name}
//     if user.admin
//       a(href="/admin") Admin panel
//     ul
//       each item in items
//         li= item
//     include partials/footer.pug</code></pre>
<p><strong>Pug syntax essentials:</strong></p>
<ul>
  <li><code>tag content</code> &mdash; element with text.</li>
  <li><code>tag(attr="value", attr2="value2")</code> &mdash; attributes.</li>
  <li><code>#id</code>, <code>.class</code> &mdash; <code>div</code> if no tag: <code>.card.featured</code> is <code>&lt;div class="card featured"&gt;</code>.</li>
  <li><code>= expression</code> &mdash; output, HTML-escaped.</li>
  <li><code>!= expression</code> &mdash; output, unescaped (dangerous).</li>
  <li><code>#{value}</code> &mdash; interpolation inside text.</li>
  <li><code>// comment</code> &mdash; HTML comment; <code>//-</code> &mdash; suppressed comment.</li>
</ul>
<p><strong>Template inheritance (Pug's best feature):</strong></p>
<pre><code>// layout.pug
doctype html
html
  head
    title= title
  body
    block content

// page.pug
extends layout
block content
  h1 Page title
  p Some content</code></pre>
<p><strong>Pros:</strong> concise, powerful inheritance, mixins for reusable components, no closing-tag typos. <strong>Cons:</strong> indentation-sensitive (a stray tab breaks rendering), steeper learning curve than EJS, designers unfamiliar with it. For new projects in 2026, <strong>EJS</strong> (similarity to HTML) or a SPA framework are more common &mdash; Pug is mainly seen in legacy apps or when brevity really matters.</p>
'''

ANSWERS[41] = r'''
<p><strong>Handlebars</strong> is a "logic-less" templating engine &mdash; strict separation of structure from logic. You can't write arbitrary JavaScript inside templates; you call helpers instead. In Express, install the <code>express-handlebars</code> package for layout/partial support.</p>
<pre><code>// npm i express-handlebars
const express = require("express");
const { engine } = require("express-handlebars");
const path = require("node:path");

const app = express();

app.engine("hbs", engine({
  extname: ".hbs",
  defaultLayout: "main",                              // views/layouts/main.hbs
  partialsDir:   path.join(__dirname, "views/partials"),
  helpers: {
    uppercase: (s) =&gt; String(s).toUpperCase(),
    eq: (a, b) =&gt; a === b,
    year: () =&gt; new Date().getFullYear(),
  },
}));
app.set("view engine", "hbs");
app.set("views", path.join(__dirname, "views"));

app.get("/", (req, res) =&gt; {
  res.render("home", {
    title:   "Home",
    user:    { name: "Ada" },
    items:   ["a", "b", "c"],
    isAdmin: req.user?.role === "admin",
  });
});

// views/layouts/main.hbs
// &lt;!doctype html&gt;&lt;html&gt;&lt;head&gt;&lt;title&gt;{{title}}&lt;/title&gt;&lt;/head&gt;&lt;body&gt;{{{body}}}&lt;/body&gt;&lt;/html&gt;

// views/home.hbs
// &lt;h1&gt;Hi, {{user.name}}&lt;/h1&gt;
// {{#if isAdmin}}
//   &lt;a href="/admin"&gt;Admin&lt;/a&gt;
// {{/if}}
// &lt;ul&gt;
//   {{#each items}}
//     &lt;li&gt;{{uppercase this}}&lt;/li&gt;
//   {{/each}}
// &lt;/ul&gt;
// &lt;p&gt;&copy; {{year}}&lt;/p&gt;</code></pre>
<p><strong>Handlebars syntax:</strong></p>
<table>
  <thead><tr><th>Syntax</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>{{name}}</code></td><td>Escaped output (safe by default)</td></tr>
    <tr><td><code>{{{name}}}</code></td><td>Raw HTML output (unsafe)</td></tr>
    <tr><td><code>{{#if}} / {{else}} / {{/if}}</code></td><td>Conditional block</td></tr>
    <tr><td><code>{{#each items}}</code></td><td>Iteration; <code>this</code> is the current item</td></tr>
    <tr><td><code>{{#with}}</code></td><td>Change context scope</td></tr>
    <tr><td><code>{{&gt; partial}}</code></td><td>Include a partial</td></tr>
    <tr><td><code>{{helperName arg}}</code></td><td>Call a registered helper</td></tr>
  </tbody>
</table>
<p><strong>Why logic-less:</strong> forces you to prepare data in the controller, keeping templates readable for designers. <strong>Trade-off:</strong> complex logic requires custom helpers, which can spread over time. A pragmatic choice for content-heavy apps and emails; EJS is a simpler default for small projects.</p>
'''

ANSWERS[42] = r'''
<p>Pass multiple handler functions to a single route &mdash; Express calls them in order, like a mini pipeline. Each must either call <code>next()</code> to continue or send a response. This is the primary way to compose authentication, validation, and the handler itself.</p>
<pre><code>// Inline — three functions chained on one route
app.post("/users",
  requireAuth,                       // 1. authenticate
  validate(CreateUserSchema),        // 2. validate body
  async (req, res) =&gt; {              // 3. handler
    const user = await db.user.create({ data: req.body });
    res.status(201).json(user);
  },
);

// As an array — equivalent
app.post("/users", [requireAuth, validate(CreateUserSchema), createUserHandler]);

// Short-circuit — any handler can send a response and stop
function requireRole(role) {
  return (req, res, next) =&gt; {
    if (req.user?.role !== role) return res.status(403).send("forbidden");
    next();
  };
}

app.delete("/posts/:id",
  requireAuth,
  requireRole("admin"),              // stops here if not admin
  async (req, res) =&gt; {
    await db.post.delete({ where: { id: req.params.id } });
    res.sendStatus(204);
  },
);

// Skip the rest with next("route")
app.get("/items/:id",
  (req, res, next) =&gt; {
    if (req.params.id === "special") return next("route");   // skip below handlers
    next();
  },
  (req, res) =&gt; res.send("normal"),
);
app.get("/items/:id", (req, res) =&gt; res.send("special"));</code></pre>
<p><strong>Conventions for chaining:</strong></p>
<ul>
  <li><strong>Order matters:</strong> auth first, parse/validate next, handler last.</li>
  <li><strong>Keep each handler single-purpose.</strong> A chain of small functions is easier to test and reuse than one monster handler.</li>
  <li><strong>Return <code>next()</code></strong> to prevent accidental fallthrough after a response.</li>
  <li><strong>Reuse middleware</strong> via factories (<code>requireRole("admin")</code>) rather than duplicating logic per route.</li>
</ul>
<p><strong>Router-level:</strong> <code>router.use(requireAuth)</code> applies to every route in the router &mdash; handy when every endpoint in the file needs auth. Per-route chains are the right choice when only <em>some</em> routes need an extra check.</p>
'''

ANSWERS[43] = r'''
<p>Form data reaches your server in one of three encodings. Pick the right parser for each:</p>
<table>
  <thead><tr><th>Encoding</th><th>Comes from</th><th>Parse with</th></tr></thead>
  <tbody>
    <tr><td><code>application/x-www-form-urlencoded</code></td><td>Standard HTML <code>&lt;form&gt;</code></td><td><code>express.urlencoded()</code></td></tr>
    <tr><td><code>multipart/form-data</code></td><td>HTML forms with <code>&lt;input type="file"&gt;</code></td><td><code>multer</code></td></tr>
    <tr><td><code>application/json</code></td><td>fetch / axios from JS</td><td><code>express.json()</code></td></tr>
  </tbody>
</table>
<pre><code>const express = require("express");
const multer = require("multer");

const app = express();

// Install both body parsers so the app handles all three forms
app.use(express.urlencoded({ extended: true, limit: "100kb" }));
app.use(express.json({ limit: "100kb" }));

// ---- 1. HTML form POST (no file upload) ----
// &lt;form method="POST" action="/signup"&gt;
//   &lt;input name="email"&gt;
//   &lt;input name="password" type="password"&gt;
//   &lt;button&gt;Sign up&lt;/button&gt;
// &lt;/form&gt;
app.post("/signup", (req, res) =&gt; {
  const { email, password } = req.body;
  // ... validate &amp; create user
  res.redirect("/welcome");
});

// ---- 2. Form with file upload ----
const upload = multer({ dest: "uploads/", limits: { fileSize: 5e6 } });
// &lt;form method="POST" action="/profile" enctype="multipart/form-data"&gt;
//   &lt;input name="name"&gt;
//   &lt;input name="avatar" type="file"&gt;
// &lt;/form&gt;
app.post("/profile", upload.single("avatar"), (req, res) =&gt; {
  const { name } = req.body;      // text fields
  const avatar = req.file;        // file metadata
  res.redirect("/me");
});

// ---- 3. API request (JSON) ----
app.post("/api/users", (req, res) =&gt; {
  const { email, password } = req.body;
  res.status(201).json({ id: "u_1" });
});</code></pre>
<p><strong>Always validate</strong> incoming form data &mdash; Zod, Joi, or express-validator &mdash; before hitting the database. Trust nothing from <code>req.body</code>. For browser forms, also return <strong>useful validation error HTML</strong> rather than throwing a 500; a per-field error map in the re-rendered form is the gold standard.</p>
<p><strong>Security:</strong> cap body sizes, apply rate limits on auth-critical endpoints, and add CSRF protection (<code>csurf</code> or double-submit cookie pattern) for session-backed apps.</p>
'''

ANSWERS[44] = r'''
<p><code>body-parser</code> was the original standalone middleware for parsing request bodies &mdash; JSON, URL-encoded, text, raw. Since <strong>Express 4.16 (2016)</strong>, its parsers were merged into Express as <code>express.json()</code>, <code>express.urlencoded()</code>, <code>express.text()</code>, and <code>express.raw()</code>. For new code, use the built-ins; you rarely need the standalone package anymore.</p>
<pre><code>// ---- Modern (Express 4.16+ and all of Express 5) ----
const express = require("express");
const app = express();

app.use(express.json({ limit: "100kb" }));
app.use(express.urlencoded({ extended: true, limit: "100kb" }));

// ---- Legacy — the standalone body-parser package ----
// npm i body-parser
const bodyParser = require("body-parser");
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.raw({ type: "application/octet-stream" }));
app.use(bodyParser.text({ type: "text/*" }));</code></pre>
<p><strong>The four parser flavours</strong> (identical API in both packages):</p>
<table>
  <thead><tr><th>Parser</th><th>Content-Type it handles</th><th>Result on <code>req.body</code></th></tr></thead>
  <tbody>
    <tr><td><code>.json()</code></td><td><code>application/json</code></td><td>Parsed object/array</td></tr>
    <tr><td><code>.urlencoded()</code></td><td><code>application/x-www-form-urlencoded</code></td><td>Plain object (nested if <code>extended: true</code>)</td></tr>
    <tr><td><code>.raw()</code></td><td>anything (configurable)</td><td><code>Buffer</code></td></tr>
    <tr><td><code>.text()</code></td><td><code>text/*</code></td><td>String</td></tr>
  </tbody>
</table>
<p><strong>When you <em>might</em> still install <code>body-parser</code>:</strong></p>
<ul>
  <li>Legacy codebase where adding a second parser path is simpler than upgrading everything.</li>
  <li>A third-party middleware hard-depends on it (rare these days).</li>
</ul>
<p><strong>Don't forget:</strong></p>
<ul>
  <li>Install body parsers <em>before</em> routes that read <code>req.body</code>.</li>
  <li>Set a <code>limit</code> (default 100kb) &mdash; protects against large-body DoS.</li>
  <li><code>multipart/form-data</code> is <strong>not</strong> handled by either package &mdash; use <code>multer</code> or <code>busboy</code>.</li>
</ul>
'''

ANSWERS[45] = r'''
<p>Install the built-in <code>express.json()</code> middleware. It reads the request body stream, parses it as JSON, and sets <code>req.body</code> to the resulting object (or array, or primitive).</p>
<pre><code>const express = require("express");
const app = express();

app.use(express.json({
  limit: "100kb",               // reject larger bodies (413 Payload Too Large)
  strict: true,                 // top-level value must be an object or array
}));

app.post("/api/users", (req, res) =&gt; {
  const { name, email } = req.body;
  res.status(201).json({ id: "u_1", name, email });
});

// Per-route JSON parser (useful when most routes don't need it)
app.post("/webhooks/stripe",
  express.raw({ type: "application/json" }),    // raw needed for signature
  (req, res) =&gt; {
    const event = verifyAndParseStripe(req.body);
    // ...
  }
);</code></pre>
<p><strong>Handling parse errors:</strong></p>
<pre><code>// Malformed JSON raises an error forwarded to error-handling middleware
app.use((err, req, res, next) =&gt; {
  if (err.type === "entity.parse.failed") {
    return res.status(400).json({ error: "invalid JSON" });
  }
  if (err.type === "entity.too.large") {
    return res.status(413).json({ error: "body too large" });
  }
  next(err);
});</code></pre>
<p><strong>What <code>express.json()</code> is NOT:</strong></p>
<ul>
  <li>It isn't a validator. Parse &ne; validate. Use Zod/Joi/express-validator after parsing.</li>
  <li>It doesn't transform types. <code>{ age: "30" }</code> stays a string; coerce explicitly.</li>
  <li>It ignores requests whose <code>Content-Type</code> isn't <code>application/json</code> &mdash; no magic type detection.</li>
</ul>
<p><strong>Tip:</strong> pair with validation right at the route boundary &mdash; <code>req.body</code> is user input, nothing more.</p>
<pre><code>import { z } from "zod";
const CreateUser = z.object({ name: z.string().min(1), email: z.string().email() });
app.post("/users", (req, res) =&gt; {
  const data = CreateUser.parse(req.body);        // throws ZodError on bad input
  // ...
});</code></pre>
'''

ANSWERS[46] = r'''
<p>Call <code>res.cookie(name, value, options)</code>. Express writes a proper <code>Set-Cookie</code> response header &mdash; the browser stores it and sends it back on future requests that match the cookie's path/domain.</p>
<pre><code>// Simple session cookie — cleared when the browser closes
res.cookie("theme", "dark");

// Persistent cookie with secure defaults
res.cookie("pref-lang", "en", {
  httpOnly: true,                      // not accessible to JS (prevents XSS theft)
  secure:   true,                      // sent only over HTTPS
  sameSite: "lax",                     // CSRF protection
  maxAge:   30 * 24 * 3600 * 1000,     // 30 days in ms
  path:     "/",                       // sent for all URLs on this host
});

// Signed cookie — value is tamper-proof (HMAC) but visible
// Requires cookieParser(secret)
res.cookie("uid", "u_1", { signed: true, httpOnly: true, secure: true });

// Set multiple cookies in one response
res
  .cookie("a", "1", { httpOnly: true })
  .cookie("b", "2", { httpOnly: true, sameSite: "strict" })
  .send("ok");

// Expires vs maxAge — maxAge is easier
res.cookie("c", "1", { maxAge: 60_000 });           // 1 minute
res.cookie("d", "1", { expires: new Date(Date.now() + 60_000) }); // equivalent

// Objects serialize as JSON
res.cookie("state", { theme: "dark", lang: "en" }); // Set-Cookie: state=j%3A%7B%22theme%22%3A%22dark%22%7D</code></pre>
<p><strong>Cookie options you'll actually use:</strong></p>
<table>
  <thead><tr><th>Option</th><th>Effect</th></tr></thead>
  <tbody>
    <tr><td><code>httpOnly</code></td><td>Hides cookie from JavaScript (defends against XSS theft)</td></tr>
    <tr><td><code>secure</code></td><td>Only sent over HTTPS</td></tr>
    <tr><td><code>sameSite</code></td><td><code>strict</code> / <code>lax</code> / <code>none</code> &mdash; CSRF mitigation</td></tr>
    <tr><td><code>maxAge</code> / <code>expires</code></td><td>Lifetime; omit for session cookie</td></tr>
    <tr><td><code>domain</code></td><td>Share across subdomains; omit unless needed</td></tr>
    <tr><td><code>path</code></td><td>Limit to a URL prefix</td></tr>
    <tr><td><code>signed</code></td><td>HMAC-sign with your cookieParser secret</td></tr>
  </tbody>
</table>
<p><strong>Secure defaults in 2026:</strong> <code>httpOnly + secure + sameSite: "lax"</code> for session cookies. <code>sameSite: "none"</code> only when you need cross-site cookies, and it requires <code>secure: true</code>.</p>
'''

ANSWERS[47] = r'''
<p>Call <code>res.clearCookie(name, options)</code>. Express responds with a <code>Set-Cookie</code> header that has an expired date &mdash; the browser then removes it. The options you pass must <strong>match how the cookie was originally set</strong> (<code>path</code>, <code>domain</code>, and in modern browsers <code>sameSite</code>), or the browser won't clear it.</p>
<pre><code>// Clear a simple cookie
res.clearCookie("theme");

// Must match the original set options
res.cookie("sid", "...", { path: "/", domain: ".example.com", secure: true });
res.clearCookie("sid", { path: "/", domain: ".example.com", secure: true });

// Logout example — clear session cookies on the way out
app.post("/logout", (req, res) =&gt; {
  req.session.destroy((err) =&gt; {
    res.clearCookie("sid", { path: "/", httpOnly: true, secure: true, sameSite: "lax" });
    res.redirect("/");
  });
});

// Clear multiple cookies at once
["sid", "csrf", "pref"].forEach(n =&gt; res.clearCookie(n, { path: "/" }));</code></pre>
<p><strong>Under the hood</strong>, <code>clearCookie</code> sends:</p>
<pre><code>Set-Cookie: sid=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT</code></pre>
<p><strong>Common pitfalls:</strong></p>
<ul>
  <li><strong>Wrong path/domain.</strong> If you set the cookie with <code>path: "/admin"</code>, <code>res.clearCookie("sid")</code> with no options won't remove it &mdash; you must pass the same <code>path</code>.</li>
  <li><strong>Session cookies from <code>express-session</code></strong> need <code>req.session.destroy()</code> (to remove the row from the store) <em>and</em> <code>res.clearCookie(name)</code>. Destroying the session alone doesn't clear the cookie from the browser.</li>
  <li><strong>Secure + HTTPS mismatch:</strong> in development over HTTP with <code>secure: true</code>, the browser silently ignores the <code>Set-Cookie</code> &mdash; for both setting and clearing.</li>
  <li><strong>Stale cookies across domains</strong> are a support nightmare; set <code>domain</code> explicitly and clear it explicitly.</li>
</ul>
<p><strong>Pro tip:</strong> for "log out of all devices," rotate a server-side value (session version, refresh-token generation) so every cookie issued before the rotation becomes invalid server-side &mdash; don't rely only on client-side clearing.</p>
'''

ANSWERS[48] = r'''
<p><code>helmet</code> is a collection of smaller middleware packages that set a bundle of <strong>HTTP security response headers</strong>. It's the single most common middleware in production Express apps &mdash; turns on secure-by-default headers with one line.</p>
<pre><code>// npm i helmet
const helmet = require("helmet");
app.use(helmet());                       // good defaults; apply early in the chain</code></pre>
<p><strong>What <code>helmet()</code> sets by default (abridged):</strong></p>
<table>
  <thead><tr><th>Header</th><th>Protects against</th></tr></thead>
  <tbody>
    <tr><td><code>Content-Security-Policy</code></td><td>XSS &mdash; restrict which scripts/styles can load</td></tr>
    <tr><td><code>Strict-Transport-Security</code></td><td>Protocol downgrade &mdash; force HTTPS</td></tr>
    <tr><td><code>X-Content-Type-Options: nosniff</code></td><td>MIME sniffing attacks</td></tr>
    <tr><td><code>X-Frame-Options: SAMEORIGIN</code></td><td>Clickjacking (iframes)</td></tr>
    <tr><td><code>Referrer-Policy: no-referrer</code></td><td>Information leakage</td></tr>
    <tr><td><code>Cross-Origin-Opener-Policy</code>, <code>-Resource-Policy</code>, <code>-Embedder-Policy</code></td><td>Spectre-class cross-origin attacks</td></tr>
    <tr><td><code>Origin-Agent-Cluster</code>, <code>X-DNS-Prefetch-Control</code>, etc.</td><td>Various</td></tr>
  </tbody>
</table>
<p><strong>Customising:</strong></p>
<pre><code>app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc:  ["'self'", "https://cdn.example.com"],
      imgSrc:     ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.example.com"],
      styleSrc:   ["'self'", "'unsafe-inline'"],
    },
  },
  strictTransportSecurity: { maxAge: 31536000, includeSubDomains: true, preload: true },
  crossOriginEmbedderPolicy: false,       // disable if your site embeds third-party iframes
}));

// Turn off individual headers if they break your app
app.use(helmet({ contentSecurityPolicy: false }));</code></pre>
<p><strong>Where to place it:</strong> at the very top of your middleware stack, before routes. It must run on every response for the headers to be added.</p>
<p><strong>Notes:</strong></p>
<ul>
  <li>Helmet doesn't protect against all attacks &mdash; it's one layer alongside input validation, auth, and CORS.</li>
  <li>CSP is the big win and the most work. Start with a restrictive policy in <code>Content-Security-Policy-Report-Only</code> mode, fix violations, then enforce.</li>
  <li>In reverse-proxy setups (Nginx, CloudFront), you can also set these at the edge &mdash; pick one layer to avoid duplicates.</li>
</ul>
'''

ANSWERS[49] = r'''
<p>In production, logging every request is non-negotiable &mdash; for debugging, auditing, and performance tracking. Use a dedicated middleware rather than <code>console.log</code>. Two dominant choices: <strong><code>morgan</code></strong> (simple, text-based) and <strong><code>pino-http</code></strong> (structured JSON, fast).</p>
<pre><code>// ---- morgan — quick setup, readable output ----
// npm i morgan
const morgan = require("morgan");

app.use(morgan("combined"));     // Apache-style: IP, user, method, path, status, size, UA

// Custom tokens
morgan.token("id", (req) =&gt; req.id);
morgan.token("user", (req) =&gt; req.user?.id ?? "anon");
app.use(morgan(":id :user :method :url :status :response-time ms"));

// Skip noisy routes / only errors
app.use(morgan("combined", {
  skip: (req, res) =&gt; res.statusCode &lt; 400,
}));

// ---- pino-http — structured JSON, production-friendly ----
// npm i pino pino-http
const pino = require("pino");
const pinoHttp = require("pino-http");

const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  redact: { paths: ["req.headers.authorization", "req.headers.cookie"], censor: "[REDACTED]" },
});
app.use(pinoHttp({
  logger,
  genReqId: (req) =&gt; req.headers["x-request-id"] ?? crypto.randomUUID(),
  customLogLevel: (req, res, err) =&gt;
    err || res.statusCode &gt;= 500 ? "error" :
    res.statusCode &gt;= 400        ? "warn"  : "info",
}));</code></pre>
<p><strong>What to log (and what not to):</strong></p>
<table>
  <thead><tr><th>Log</th><th>Never log</th></tr></thead>
  <tbody>
    <tr><td>method, path, status, duration</td><td>Full request/response bodies by default</td></tr>
    <tr><td>requestId, userId, IP, user agent</td><td>Passwords, tokens, Authorization header</td></tr>
    <tr><td>error stack in non-production</td><td>Cookies with sensitive values</td></tr>
    <tr><td>sampled high-volume 2xx + all 4xx/5xx</td><td>PII like SSN, full card numbers</td></tr>
  </tbody>
</table>
<p><strong>Rules for production logging:</strong></p>
<ul>
  <li>Use <strong>structured JSON</strong> (pino) &mdash; machine-readable, one log line per request.</li>
  <li>Attach a <strong>request ID</strong> to every log line; return it as <code>X-Request-Id</code> so support can trace issues.</li>
  <li>Ship logs to <strong>stdout</strong> and let the platform (Kubernetes, Cloud Run, Fly) handle collection.</li>
  <li>Redact PII and auth at the logger level &mdash; don't rely on handlers to remember.</li>
</ul>
'''

ANSWERS[50] = r'''
<p><strong>morgan</strong> is Express's classic HTTP request logger. Drop it in, pick a format, and every request gets a log line. It's perfect for development and acceptable in small production apps; for large-scale production, prefer <code>pino-http</code> (structured JSON, faster).</p>
<pre><code>// npm i morgan
const morgan = require("morgan");

// 1. Pre-defined formats
app.use(morgan("combined"));   // Apache Combined Log Format — good for prod
app.use(morgan("common"));     // Apache Common Log Format
app.use(morgan("dev"));        // colourful, concise — good for dev
app.use(morgan("short"));
app.use(morgan("tiny"));

// 2. Custom format string using tokens
app.use(morgan(":method :url :status :res[content-length] - :response-time ms"));

// 3. Custom tokens
morgan.token("user-id", (req) =&gt; req.user?.id ?? "anon");
morgan.token("req-id",  (req) =&gt; req.id);
app.use(morgan(":req-id :user-id :method :url :status :response-time ms"));

// 4. Filter which requests get logged
app.use(morgan("combined", {
  skip: (req, res) =&gt; res.statusCode &lt; 400,         // only errors
}));

// 5. Stream to a file (or rotated logs via rotating-file-stream)
// npm i rotating-file-stream
const rfs = require("rotating-file-stream");
const accessStream = rfs.createStream("access.log", {
  interval: "1d", path: "logs", maxFiles: 14, compress: "gzip",
});
app.use(morgan("combined", { stream: accessStream }));</code></pre>
<p><strong>Format tokens</strong> (most commonly used):</p>
<table>
  <thead><tr><th>Token</th><th>Meaning</th></tr></thead>
  <tbody>
    <tr><td><code>:method</code></td><td>HTTP method</td></tr>
    <tr><td><code>:url</code></td><td>Request URL (path + query)</td></tr>
    <tr><td><code>:status</code></td><td>Response status code</td></tr>
    <tr><td><code>:response-time</code></td><td>ms to respond</td></tr>
    <tr><td><code>:res[header]</code></td><td>Response header value</td></tr>
    <tr><td><code>:req[header]</code></td><td>Request header value</td></tr>
    <tr><td><code>:remote-addr</code></td><td>Client IP (respects <code>trust proxy</code>)</td></tr>
    <tr><td><code>:user-agent</code></td><td><code>User-Agent</code> header</td></tr>
  </tbody>
</table>
<p><strong>Placement:</strong> right after security middleware, before routes &mdash; this way even short-circuited requests (rejected by auth/rate-limit) are logged.</p>
<p><strong>Caveats:</strong> morgan uses simple string output &mdash; harder to query in log aggregators compared to <code>pino</code>'s JSON. For serious production logging, pair with log shipping (Vector, Fluent Bit) into a service like Loki, Elastic, or Datadog.</p>
'''

ANSWERS[51] = r'''
<p><strong>File downloads</strong> mean sending a file to the client with headers that prompt a "Save As" dialog or trigger an automatic download, rather than rendering in the browser. Express gives you <code>res.download()</code> &mdash; a one-liner that sets the right headers and streams the file.</p>
<pre><code>const path = require("node:path");

// 1. Simple download — prompts client with the file's basename
app.get("/reports/q1", (req, res) =&gt; {
  res.download(path.join(__dirname, "files", "q1-report.pdf"));
  // sends: Content-Disposition: attachment; filename="q1-report.pdf"
});

// 2. Override the suggested filename
app.get("/reports/:id/download", (req, res) =&gt; {
  const file = path.join(__dirname, "reports", `${req.params.id}.pdf`);
  res.download(file, `Report-${req.params.id}.pdf`);
});

// 3. Handle errors — file missing, permissions, etc.
app.get("/invoice/:id", (req, res) =&gt; {
  const file = `/var/invoices/${req.params.id}.pdf`;
  res.download(file, `invoice-${req.params.id}.pdf`, (err) =&gt; {
    if (err &amp;&amp; !res.headersSent) {
      res.status(404).send("file not available");
    }
  });
});

// 4. Stream a generated or remote file (not from local disk)
const { pipeline } = require("node:stream/promises");
app.get("/export.csv", async (req, res) =&gt; {
  res.setHeader("Content-Type",        "text/csv");
  res.setHeader("Content-Disposition", 'attachment; filename="export.csv"');
  await pipeline(generateCsvStream(), res);
});</code></pre>
<p><strong>What's happening under the hood:</strong> <code>res.download()</code> sets <code>Content-Disposition: attachment; filename="..."</code>. That single header is what tells the browser to download rather than display. Otherwise it's essentially <code>res.sendFile()</code>.</p>
<p><strong>Security:</strong> never pass user-controlled paths straight to <code>res.download()</code> &mdash; a request for <code>../../etc/passwd</code> would succeed. Validate/whitelist filenames, use <code>path.basename()</code>, and confine to a fixed base directory.</p>
<p><strong>Large files:</strong> for files over ~50 MB, prefer serving via a CDN or pre-signed S3 URL rather than proxying through Node &mdash; your event loop shouldn't be babysitting multi-GB transfers.</p>
'''

ANSWERS[52] = r'''
<p><strong>Environment variables</strong> are how you keep configuration (DB URLs, API keys, ports, log levels) out of source code. Node exposes them on <code>process.env</code>; each value is always a <em>string</em> or <code>undefined</code>. In development, load them from a <code>.env</code> file via <code>dotenv</code>; in production, the platform (Kubernetes, Docker, Vercel, Heroku) injects them directly.</p>
<pre><code>// 1. .env file (never commit this; add to .gitignore)
// PORT=3000
// DATABASE_URL=postgres://localhost:5432/app
// JWT_SECRET=change-me-32-chars-minimum

// 2. Load it at the top of your entry file
require("dotenv").config();   // node 20.6+ alt: node --env-file=.env server.js

// 3. Read values with sensible defaults + type coercion
const PORT        = Number(process.env.PORT ?? 3000);
const NODE_ENV    = process.env.NODE_ENV ?? "development";
const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) throw new Error("DATABASE_URL is required");

// 4. Validate at boot — fail fast on bad config (recommended)
const { z } = require("zod");
const env = z.object({
  NODE_ENV:      z.enum(["development","test","production"]).default("development"),
  PORT:          z.coerce.number().default(3000),
  DATABASE_URL:  z.string().url(),
  JWT_SECRET:    z.string().min(32),
  LOG_LEVEL:     z.enum(["debug","info","warn","error"]).default("info"),
}).parse(process.env);

// 5. Use validated config throughout the app
const express = require("express");
const app = express();
app.listen(env.PORT, () =&gt; console.log(`listening on ${env.PORT}`));</code></pre>
<p><strong>Rules that save pain:</strong></p>
<ul>
  <li><strong>Never commit <code>.env</code></strong> &mdash; it contains secrets. Commit <code>.env.example</code> instead as a template.</li>
  <li><strong>Validate at startup</strong> with Zod/envalid so the process fails at boot instead of halfway through serving traffic.</li>
  <li><strong>All values are strings</strong> &mdash; <code>PORT=3000</code> is <code>"3000"</code>. Coerce.</li>
  <li><strong>Don't log <code>process.env</code></strong> &mdash; secrets end up in logs.</li>
  <li><strong>Production secrets:</strong> use a secrets manager (AWS Secrets Manager, Vault, Doppler) rather than a plain <code>.env</code> file shared over Slack.</li>
</ul>
'''

ANSWERS[53] = r'''
<p><strong><code>dotenv</code></strong> is a tiny package that reads a <code>.env</code> file from disk, parses key=value pairs, and adds them to <code>process.env</code>. That's literally it &mdash; a loader with zero dependencies. It exists because it's useful in development to have env vars <em>in a file</em> that's easy to share across a team (minus secrets) and auto-loaded when you run <code>node server.js</code>.</p>
<pre><code>// npm install dotenv

// .env  (project root — add to .gitignore)
// PORT=3000
// DATABASE_URL=postgres://localhost:5432/app
// FEATURE_NEW_UI=true

// Load at the TOP of your entry file — before any module reads process.env
require("dotenv").config();

// Now these are available anywhere in the process
const port = process.env.PORT;           // "3000" (always a string)
const flag = process.env.FEATURE_NEW_UI === "true";

// Specify a non-default file
require("dotenv").config({ path: ".env.local" });

// Multiple files, later ones override
require("dotenv").config({ path: [".env.local", ".env"] });

// Debug mode — shows what dotenv loaded (don't leave on in production)
require("dotenv").config({ debug: true });</code></pre>
<p><strong>Node 20.6+ built-in alternative</strong> &mdash; no library needed:</p>
<pre><code>// package.json
// { "scripts": { "dev": "node --env-file=.env server.js" } }

// Now process.env is populated at launch — no require("dotenv") call</code></pre>
<p><strong>Nuances:</strong></p>
<ul>
  <li><strong>Production:</strong> don't ship <code>.env</code> files with containers. The platform (K8s, Vercel, ECS) injects env vars directly &mdash; <code>dotenv.config()</code> becomes a no-op if the file isn't there, which is fine.</li>
  <li><strong>Quoting:</strong> <code>SECRET="a b c"</code> keeps the spaces; <code>SECRET=a b c</code> gives you <code>"a b c"</code> without quotes. Multiline values use <code>\n</code> or quoted strings.</li>
  <li><strong>Interpolation:</strong> base <code>dotenv</code> doesn't interpolate. <code>dotenv-expand</code> adds <code>${VAR}</code> support.</li>
  <li><strong>Encryption at rest:</strong> <code>dotenvx</code> and <code>dotenv-vault</code> encrypt the file so it can be committed (decryption key is the secret you keep out).</li>
</ul>
'''

ANSWERS[54] = r'''
<p><strong>express-validator</strong> is a middleware wrapper around the <code>validator.js</code> library. You declare validation rules as middleware, run them, then check for errors in your handler. It predates newer schema-based libraries (Zod, Joi) and is still widely used in legacy Express codebases.</p>
<pre><code>// npm install express-validator
const express = require("express");
const { body, param, query, validationResult } = require("express-validator");
const app = express();
app.use(express.json());

// Attach validation rules as middleware, then your handler
app.post("/users",
  // each body() is a separate middleware
  body("email").isEmail().normalizeEmail(),
  body("password").isLength({ min: 8 }).withMessage("at least 8 chars"),
  body("age").optional().isInt({ min: 13, max: 120 }).toInt(),
  body("role").isIn(["user", "admin"]).default("user"),

  (req, res) =&gt; {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // req.body is now sanitized (email normalized, age coerced to int)
    res.status(201).json({ ok: true, user: req.body });
  }
);

// Validate URL and query params
app.get("/users/:id",
  param("id").isUUID(),
  query("tab").optional().isIn(["profile", "settings"]),
  (req, res) =&gt; {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).json(errors);
    res.json({ id: req.params.id, tab: req.query.tab });
  }
);

// Group reusable rules
const userCreateRules = [
  body("email").isEmail(),
  body("password").isLength({ min: 8 }),
];
app.post("/users", userCreateRules, (req, res) =&gt; { /* ... */ });</code></pre>
<p><strong>Handy validators &amp; sanitizers:</strong></p>
<ul>
  <li><code>isEmail()</code>, <code>isURL()</code>, <code>isUUID()</code>, <code>isInt()</code>, <code>isLength({ min, max })</code>, <code>matches(regex)</code>, <code>isIn([...])</code>.</li>
  <li><code>normalizeEmail()</code>, <code>trim()</code>, <code>escape()</code> (HTML entity), <code>toInt()</code>, <code>toBoolean()</code>.</li>
  <li><code>.withMessage("...")</code> for a custom error; <code>.optional()</code> to allow missing; <code>.custom(fn)</code> for arbitrary checks (including async DB lookups).</li>
</ul>
<p><strong>When to pick what:</strong> for new projects in 2026, <strong>Zod</strong> is generally the better choice &mdash; single schema for validation + types + parsing, no fragmented middleware. <code>express-validator</code> is still fine in existing codebases and has excellent sanitization utilities out of the box.</p>
'''

ANSWERS[55] = r'''
<p>Redirects in Express come down to <code>res.redirect()</code>. You saw its basics in Q19 &mdash; this answer focuses on real-world redirect patterns: login returns, trailing-slash normalization, legacy URL mapping, and safe handling of user-supplied URLs.</p>
<pre><code>// 1. Post-login: send user back where they came from
app.get("/login", (req, res) =&gt; {
  // capture the URL they were trying to reach
  req.session.returnTo = req.query.next || "/dashboard";
  res.render("login");
});
app.post("/login", async (req, res) =&gt; {
  const user = await authenticate(req.body);
  if (!user) return res.redirect("/login?error=1");
  req.session.userId = user.id;
  const target = req.session.returnTo || "/dashboard";
  delete req.session.returnTo;
  res.redirect(target);
});

// 2. Normalize trailing slashes — send /about/ -&gt; /about
app.use((req, res, next) =&gt; {
  if (req.path !== "/" &amp;&amp; req.path.endsWith("/")) {
    const q = req.url.slice(req.path.length);
    return res.redirect(301, req.path.slice(0, -1) + q);
  }
  next();
});

// 3. Legacy URL mapping — keep old links working
const legacyMap = {
  "/home": "/",
  "/products.html": "/products",
};
app.use((req, res, next) =&gt; {
  const target = legacyMap[req.path];
  if (target) return res.redirect(301, target);
  next();
});

// 4. SAFELY redirect to a user-supplied URL — prevent open redirects
function safeRedirect(res, target, fallback = "/") {
  // Only allow relative URLs that don't start with //
  if (typeof target === "string" &amp;&amp; /^\/(?!\/)/.test(target)) {
    return res.redirect(target);
  }
  res.redirect(fallback);
}
app.get("/go", (req, res) =&gt; safeRedirect(res, req.query.next));</code></pre>
<p><strong>The open-redirect trap:</strong> <code>res.redirect(req.query.next)</code> without validation lets an attacker send a phishing link like <code>https://yoursite.com/go?next=https://evil.example</code>. Users trust the domain in the link, click it, and land on the attacker's clone of your login page. Always validate redirect targets:</p>
<ul>
  <li><strong>Only relative URLs</strong> starting with a single <code>/</code>.</li>
  <li><strong>Or allowlist</strong> known external targets.</li>
  <li><strong>Or require same-origin</strong> by parsing with <code>new URL(target, siteOrigin)</code>.</li>
</ul>
'''

ANSWERS[56] = r'''
<p>A <strong>conditional request</strong> uses caching headers (<code>If-Modified-Since</code>, <code>If-None-Match</code>) so the client can ask "only send me the resource if it changed." The server answers <strong>304 Not Modified</strong> with an empty body when the cached copy is still good, saving bandwidth and time.</p>
<pre><code>// Express handles this automatically for static files and res.send responses
// via ETag generation — just enable it:
app.set("etag", "strong");   // or "weak" (default)

// Example: manual ETag for a dynamic resource
const crypto = require("node:crypto");

app.get("/profile", async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.user.id } });
  const body = JSON.stringify(user);
  const etag = `"${crypto.createHash("sha1").update(body).digest("base64")}"`;

  res.setHeader("ETag", etag);
  res.setHeader("Cache-Control", "private, max-age=0, must-revalidate");

  // If the client sent If-None-Match and it matches, respond 304 — no body
  if (req.headers["if-none-match"] === etag) {
    return res.status(304).end();
  }
  res.type("json").send(body);
});

// Last-Modified-based conditional (coarser; timestamp precision)
app.get("/articles/:slug", async (req, res) =&gt; {
  const article = await db.article.findUnique({ where: { slug: req.params.slug } });
  const lastMod = article.updatedAt.toUTCString();
  res.setHeader("Last-Modified", lastMod);

  const ims = req.headers["if-modified-since"];
  if (ims &amp;&amp; new Date(ims) &gt;= article.updatedAt) {
    return res.status(304).end();
  }
  res.json(article);
});

// res.fresh — Express helper that consults both ETag and Last-Modified
app.get("/auto", (req, res) =&gt; {
  res.setHeader("Last-Modified", someDate.toUTCString());
  if (req.fresh) return res.status(304).end();
  res.send(bigBody);
});</code></pre>
<p><strong>How it works end to end:</strong></p>
<ol>
  <li>Server responds with an <code>ETag</code> (or <code>Last-Modified</code>) and the body.</li>
  <li>Client caches both. On its next request, it sends <code>If-None-Match: &lt;etag&gt;</code> (or <code>If-Modified-Since</code>).</li>
  <li>Server computes the current ETag. If it matches the client's &mdash; <code>304 Not Modified</code>, empty body. Otherwise, fresh response with a new ETag.</li>
</ol>
<p><strong>Gotchas:</strong> Express's default ETag is a <em>weak</em> hash of the response body. That's fine for read-heavy APIs; for write-heavy or large responses, compute ETags from DB versions (cheap) rather than body hashes (expensive). Disable ETag generation (<code>app.set("etag", false)</code>) on endpoints that should always re-fetch.</p>
'''

ANSWERS[57] = r'''
<p><strong>HTTP Basic Authentication</strong> is the simplest auth scheme: the client sends an <code>Authorization: Basic base64(user:password)</code> header on every request. It's fine for internal tools and Grafana-style admin panels behind HTTPS &mdash; not for user-facing apps.</p>
<pre><code>// Option 1: a dedicated middleware package
// npm install express-basic-auth
const basicAuth = require("express-basic-auth");

app.use("/admin", basicAuth({
  users: { admin: process.env.ADMIN_PASSWORD },
  challenge: true,                 // prompt the browser with a login dialog
  realm: "Admin Area",
  unauthorizedResponse: "unauthorized",
}));

app.get("/admin/stats", (req, res) =&gt; {
  res.json({ user: req.auth.user });
});

// Option 2: write it yourself (understanding the protocol)
function basicAuthMiddleware(validate) {
  return (req, res, next) =&gt; {
    const header = req.headers.authorization ?? "";
    if (!header.startsWith("Basic ")) return askForAuth();

    const [user, pass] = Buffer.from(header.slice(6), "base64")
                               .toString("utf8")
                               .split(":");

    if (validate(user, pass)) {
      req.user = { name: user };
      return next();
    }
    askForAuth();

    function askForAuth() {
      res.setHeader("WWW-Authenticate", 'Basic realm="Protected", charset="UTF-8"');
      res.status(401).send("Authentication required");
    }
  };
}

// Compare with timing-safe compare to avoid timing leaks
const { timingSafeEqual } = require("node:crypto");
function eq(a, b) {
  const ba = Buffer.from(a), bb = Buffer.from(b);
  return ba.length === bb.length &amp;&amp; timingSafeEqual(ba, bb);
}
app.use("/admin", basicAuthMiddleware((u, p) =&gt;
  eq(u, "admin") &amp;&amp; eq(p, process.env.ADMIN_PASSWORD)));</code></pre>
<p><strong>Characteristics to understand:</strong></p>
<ul>
  <li><strong>The credentials travel on every request</strong> in base64. <em>Base64 is encoding, not encryption.</em> HTTPS is mandatory &mdash; over plain HTTP they might as well be in the clear.</li>
  <li><strong>No logout.</strong> Browsers cache the header until they're closed.</li>
  <li><strong>No rate limiting, no lockout, no 2FA.</strong> Use only for low-risk endpoints.</li>
  <li><strong>Timing-safe comparison</strong> (above) prevents attackers from guessing the password one character at a time via response-time differences.</li>
</ul>
<p><strong>When not to use it:</strong> end-user login. Use sessions+cookies, JWT, or OAuth via <strong>Passport</strong> instead.</p>
'''

ANSWERS[58] = r'''
<p><strong>Passport.js</strong> is the classic Express authentication library. It's a small core plus ~500 <em>strategies</em> (plugins) for different auth methods: <code>passport-local</code> for username+password, <code>passport-jwt</code> for JWTs, <code>passport-google-oauth20</code> for OAuth, <code>passport-saml</code> for SSO, etc. You configure strategies, call <code>passport.authenticate()</code> as middleware, and Passport populates <code>req.user</code>.</p>
<pre><code>// npm install passport passport-local express-session
const passport = require("passport");
const LocalStrategy = require("passport-local");
const session = require("express-session");
const bcrypt = require("bcrypt");

// 1. Sessions (Passport needs them for most flows)
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, secure: true, sameSite: "lax" },
}));

// 2. Configure the local strategy — how to validate credentials
passport.use(new LocalStrategy(async (username, password, done) =&gt; {
  const user = await db.user.findUnique({ where: { username } });
  if (!user) return done(null, false, { message: "unknown user" });
  const ok = await bcrypt.compare(password, user.passwordHash);
  if (!ok)   return done(null, false, { message: "bad password" });
  return done(null, user);
}));

// 3. How to serialize/deserialize the user for the session
passport.serializeUser  ((user, done) =&gt; done(null, user.id));
passport.deserializeUser(async (id, done) =&gt; {
  const user = await db.user.findUnique({ where: { id } });
  done(null, user);
});

// 4. Wire Passport into the Express pipeline
app.use(passport.initialize());
app.use(passport.session());

// 5. Login route
app.post("/login", passport.authenticate("local", {
  successRedirect: "/dashboard",
  failureRedirect: "/login",
}));

// 6. Guard protected routes
function requireLogin(req, res, next) {
  if (req.isAuthenticated()) return next();
  res.redirect("/login");
}
app.get("/dashboard", requireLogin, (req, res) =&gt; {
  res.send(`Welcome ${req.user.username}`);
});

// 7. Logout (Passport 0.6+ — logOut is async)
app.post("/logout", (req, res, next) =&gt; {
  req.logout((err) =&gt; err ? next(err) : res.redirect("/"));
});</code></pre>
<p><strong>Strategies you'll see:</strong> <code>passport-local</code> (DB users), <code>passport-jwt</code> (stateless tokens), <code>passport-google-oauth20</code> / <code>passport-github2</code> (OAuth social login), <code>passport-saml</code> (enterprise SSO), <code>passport-oauth2</code> (generic OAuth).</p>
<p><strong>Is it still the right choice in 2026?</strong> Yes for legacy apps and for OAuth breadth. For greenfield projects, many teams reach for managed auth (<strong>Auth0</strong>, <strong>Clerk</strong>, <strong>Supabase Auth</strong>, <strong>Better Auth</strong>) or <code>openid-client</code> directly &mdash; they ship faster and stay patched. Passport's maintenance has slowed; evaluate strategy freshness before adopting a new one.</p>
'''

ANSWERS[59] = r'''
<p><strong>Role-based access control (RBAC)</strong> means allowing users to do things based on their assigned role(s): "admins can delete, editors can update, viewers can read." In Express this is just middleware that checks <code>req.user.role</code> (or roles) and passes or rejects.</p>
<pre><code>// 1. Roll-your-own — minimal RBAC middleware
function requireRole(...allowed) {
  return (req, res, next) =&gt; {
    if (!req.user) return res.status(401).json({ error: "unauthorized" });
    if (!allowed.includes(req.user.role)) {
      return res.status(403).json({ error: "forbidden" });
    }
    next();
  };
}

app.get("/users",               requireLogin, requireRole("admin", "manager"), listUsers);
app.delete("/users/:id",        requireLogin, requireRole("admin"),            deleteUser);
app.get("/profile",             requireLogin,                                   myProfile);
app.patch("/articles/:id",      requireLogin, requireRole("editor", "admin"),  updateArticle);

// 2. Multiple roles per user — check overlap
function requireAnyRole(...allowed) {
  return (req, res, next) =&gt; {
    const userRoles = req.user?.roles ?? [];
    if (allowed.some(r =&gt; userRoles.includes(r))) return next();
    res.sendStatus(403);
  };
}

// 3. Resource ownership — "admin OR the owner"
function requireOwnerOr(...roles) {
  return async (req, res, next) =&gt; {
    if (roles.includes(req.user.role)) return next();
    const article = await db.article.findUnique({ where: { id: req.params.id } });
    if (article?.authorId === req.user.id) return next();
    res.sendStatus(403);
  };
}
app.patch("/articles/:id", requireLogin, requireOwnerOr("admin"), updateArticle);

// 4. Use a battle-tested library for non-trivial rules — CASL
// npm install @casl/ability
const { AbilityBuilder, Ability } = require("@casl/ability");

function abilitiesFor(user) {
  const { can, cannot, build } = new AbilityBuilder(Ability);
  if (user.role === "admin") can("manage", "all");
  else {
    can("read", "Article");
    can(["update", "delete"], "Article", { authorId: user.id });
  }
  return build();
}

app.patch("/articles/:id", requireLogin, async (req, res, next) =&gt; {
  const ability = abilitiesFor(req.user);
  const article = await db.article.findUnique({ where: { id: req.params.id } });
  if (!ability.can("update", subject("Article", article))) return res.sendStatus(403);
  next();
});</code></pre>
<p><strong>Design notes:</strong></p>
<ul>
  <li><strong>Always two steps:</strong> "who are you?" (authentication) then "can you do this?" (authorization). Never skip the first.</li>
  <li><strong>RBAC handles roles; ABAC (attribute-based)</strong> handles rules like "can update only their own articles." For those, use a policy library like <strong>CASL</strong> or <strong>Oso</strong>.</li>
  <li><strong>Deny by default.</strong> Guard every protected route explicitly &mdash; no "shared middleware is probably there somewhere."</li>
  <li><strong>Audit</strong> sensitive actions (role changes, deletes) to an append-only log &mdash; privilege escalation is much easier to detect after the fact than to prevent.</li>
</ul>
'''

ANSWERS[60] = r'''
<p>A <strong>RESTful API</strong> maps HTTP methods (GET/POST/PUT/PATCH/DELETE) onto nouns (resources). Each resource gets its own URL path and a predictable set of operations. Express is a natural fit because routing on method+path is its core API.</p>
<pre><code>// Typical resource layout — articles
// GET    /articles             list (paginated)
// POST   /articles             create
// GET    /articles/:id         read one
// PATCH  /articles/:id         partial update
// PUT    /articles/:id         full replace
// DELETE /articles/:id         delete

const express = require("express");
const { z } = require("zod");
const app = express();
app.use(express.json());

const CreateArticle = z.object({
  title: z.string().min(1).max(200),
  body:  z.string().min(1),
  tags:  z.array(z.string()).default([]),
});
const UpdateArticle = CreateArticle.partial();

// --- routes ---
app.get("/articles", async (req, res) =&gt; {
  const page = Math.max(1, Number(req.query.page ?? 1));
  const size = Math.min(100, Number(req.query.size ?? 20));
  const [items, total] = await Promise.all([
    db.article.findMany({ skip: (page-1)*size, take: size, orderBy: { createdAt: "desc" } }),
    db.article.count(),
  ]);
  res.json({ data: items, page, size, total });
});

app.post("/articles", requireLogin, async (req, res) =&gt; {
  const parsed = CreateArticle.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.flatten());
  const article = await db.article.create({ data: { ...parsed.data, authorId: req.user.id } });
  res.status(201).location(`/articles/${article.id}`).json(article);
});

app.get("/articles/:id", async (req, res) =&gt; {
  const article = await db.article.findUnique({ where: { id: req.params.id } });
  if (!article) return res.status(404).json({ error: "not found" });
  res.json(article);
});

app.patch("/articles/:id", requireLogin, async (req, res) =&gt; {
  const parsed = UpdateArticle.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.flatten());
  const article = await db.article.update({
    where: { id: req.params.id, authorId: req.user.id },
    data:  parsed.data,
  });
  res.json(article);
});

app.delete("/articles/:id", requireLogin, async (req, res) =&gt; {
  await db.article.delete({ where: { id: req.params.id, authorId: req.user.id } });
  res.sendStatus(204);                 // no content
});

// Centralized error handler
app.use((err, req, res, next) =&gt; {
  const status = err.status ?? 500;
  res.status(status).json({ error: err.message });
});

app.listen(3000);</code></pre>
<p><strong>REST conventions worth following:</strong></p>
<ul>
  <li><strong>Status codes:</strong> 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 422 Unprocessable Entity, 500 Internal Error.</li>
  <li><strong>Plural nouns</strong> for collections: <code>/articles</code>, not <code>/article</code>.</li>
  <li><strong>Version the API</strong> at the prefix: <code>/api/v1/articles</code>.</li>
  <li><strong>Document it</strong> with OpenAPI (see API Advanced for patterns).</li>
</ul>
'''

ANSWERS[61] = r'''
<p>Express handlers are called with <code>(req, res, next)</code> and Node is single-threaded &mdash; you cannot block the event loop, so every non-trivial handler involves async code (DB queries, HTTP calls, file I/O). The modern pattern: <strong>async/await</strong> for readability, <code>Promise.all</code> for parallel, and in Express 5 errors from rejected promises propagate automatically.</p>
<pre><code>// 1. The baseline pattern — async/await
app.get("/users/:id", async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.params.id } });
  if (!user) return res.status(404).json({ error: "not found" });
  res.json(user);
});

// 2. Parallel calls — don't await sequentially when you don't need to
app.get("/dashboard", async (req, res) =&gt; {
  const [user, orders, notifications] = await Promise.all([
    db.user.findUnique({ where: { id: req.user.id } }),
    db.order.findMany({ where: { userId: req.user.id } }),
    db.notification.findMany({ where: { userId: req.user.id, readAt: null } }),
  ]);
  res.json({ user, orders, notifications });
});

// 3. Express 5 — rejections propagate to error middleware automatically
app.get("/boom", async (req, res) =&gt; {
  const data = await somethingThatRejects();   // if rejected, next(err) is called
  res.json(data);
});

// 4. Express 4 — wrap async handlers to avoid unhandled rejections
//    npm install express-async-errors   // installs a global patch
require("express-async-errors");
// OR wrap manually:
const asyncHandler = fn =&gt; (req, res, next) =&gt;
  Promise.resolve(fn(req, res, next)).catch(next);

app.get("/safe", asyncHandler(async (req, res) =&gt; {
  const x = await thingThatMightReject();
  res.json(x);
}));

// 5. Concurrency limit — don't fire 10,000 requests to a third-party at once
const pLimit = require("p-limit");
const limit = pLimit(10);
const results = await Promise.all(ids.map(id =&gt; limit(() =&gt; fetchUser(id))));</code></pre>
<p><strong>Rules of thumb:</strong></p>
<ul>
  <li><strong>Never use callbacks in new code.</strong> Wrap legacy callback APIs with <code>util.promisify</code>.</li>
  <li><strong>Parallelize independent calls</strong> with <code>Promise.all</code>; if any one can fail without killing the whole request, use <code>Promise.allSettled</code>.</li>
  <li><strong>Don't forget to <code>await</code></strong> &mdash; forgetting it silently drops the promise and the error goes to unhandled-rejection.</li>
  <li><strong>Add timeouts</strong> to outbound HTTP calls &mdash; a hung dependency shouldn't hang your handler forever.</li>
  <li><strong>Upgrade to Express 5</strong> if you can &mdash; the automatic async error forwarding removes an entire class of bugs.</li>
</ul>
'''

ANSWERS[62] = r'''
<p>A <strong>Promise</strong> represents a future value &mdash; the outcome of an async operation that's running now and will eventually resolve or reject. Most Node libraries in 2026 return promises natively (MongoDB driver, Prisma, <code>fs/promises</code>, <code>undici</code>/fetch). You rarely create promises manually; you <em>consume</em> them.</p>
<pre><code>// 1. Use async/await — promises feel synchronous
app.get("/articles/:id", async (req, res, next) =&gt; {
  try {
    const article = await db.article.findUnique({ where: { id: req.params.id } });
    if (!article) return res.status(404).json({ error: "not found" });
    res.json(article);
  } catch (err) {
    next(err);
  }
});

// 2. Classic .then()/.catch() chain — still valid, just less readable
app.get("/articles/:id", (req, res, next) =&gt; {
  db.article.findUnique({ where: { id: req.params.id } })
    .then(article =&gt; article
      ? res.json(article)
      : res.status(404).json({ error: "not found" }))
    .catch(next);
});

// 3. Promise.all — wait for many in parallel; fails fast if any rejects
const [user, posts] = await Promise.all([
  db.user.findUnique({ where: { id } }),
  db.post.findMany({ where: { authorId: id } }),
]);

// 4. Promise.allSettled — wait for all, get successes AND failures
const results = await Promise.allSettled([
  fetchWeather(),
  fetchNews(),
  fetchStocks(),
]);
const successes = results
  .filter(r =&gt; r.status === "fulfilled")
  .map(r =&gt; r.value);

// 5. Promise.race — whoever finishes first wins (great for timeouts)
const withTimeout = (p, ms) =&gt; Promise.race([
  p,
  new Promise((_, reject) =&gt; setTimeout(() =&gt; reject(new Error("timeout")), ms)),
]);

// 6. Promisify a legacy callback API
const fs = require("node:fs");
const { promisify } = require("node:util");
const readFileAsync = promisify(fs.readFile);
// or just: const fs = require("node:fs/promises");</code></pre>
<p><strong>Patterns to remember:</strong></p>
<ul>
  <li><strong>Always <code>await</code> promises</strong> (or chain <code>.then/.catch</code>) &mdash; dropping a promise means losing errors.</li>
  <li><strong>Unhandled rejections crash the process</strong> in modern Node (they used to just warn). Always catch somewhere up the chain.</li>
  <li><strong>Combinators matter:</strong> <code>Promise.all</code> (fail-fast), <code>allSettled</code> (tolerant), <code>race</code> (first wins), <code>any</code> (first success).</li>
  <li><strong>Don't wrap an existing promise</strong> in <code>new Promise</code> &mdash; common antipattern: <code>new Promise((res) =&gt; somethingThatReturnsPromise().then(res))</code>. Just use the promise you have.</li>
</ul>
'''

ANSWERS[63] = r'''
<p><strong>async/await</strong> is syntactic sugar over promises &mdash; same machinery, but code reads top-to-bottom like synchronous code. A function marked <code>async</code> always returns a promise; <code>await</code> inside it pauses until the awaited promise resolves (yielding to the event loop meanwhile).</p>
<pre><code>// Basic — almost identical to synchronous code
app.get("/users/:id", async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.params.id } });
  if (!user) return res.status(404).json({ error: "not found" });
  res.json(user);
});

// Try/catch works normally for async errors
app.post("/charges", async (req, res, next) =&gt; {
  try {
    const charge = await stripe.charges.create({ amount: 100 });
    await db.charge.create({ data: charge });
    res.status(201).json(charge);
  } catch (err) {
    next(err);       // forward to error middleware
  }
});

// In Express 5, try/catch is optional — rejections auto-forward to next(err)
app.post("/charges", async (req, res) =&gt; {
  const charge = await stripe.charges.create({ amount: 100 });
  await db.charge.create({ data: charge });
  res.status(201).json(charge);
});

// Parallel: await Promise.all instead of sequential awaits
// SLOW — sequential (3s total if each takes 1s)
const a = await fetchA();
const b = await fetchB();
const c = await fetchC();

// FAST — parallel (1s total)
const [a, b, c] = await Promise.all([fetchA(), fetchB(), fetchC()]);

// Async iteration — for-await-of for streams/generators
for await (const chunk of response.body) {
  processChunk(chunk);
}

// Loops — careful: forEach does NOT await
for (const id of ids) {
  await processOne(id);    // sequential (fine if order matters)
}
// ids.forEach(async id =&gt; await processOne(id));   // BUG — fire-and-forget</code></pre>
<p><strong>Things that trip people up:</strong></p>
<ul>
  <li><strong><code>forEach</code> ignores async.</strong> Use <code>for...of</code> with <code>await</code> for sequential, or <code>Promise.all</code> over <code>.map</code> for parallel.</li>
  <li><strong>Top-level <code>await</code></strong> works in ESM modules (Node 14+ with <code>"type": "module"</code>). Not in CommonJS.</li>
  <li><strong>Every <code>await</code> yields the event loop</strong> &mdash; your server keeps handling other requests while you wait.</li>
  <li><strong>An async function always returns a promise</strong> &mdash; even if the code inside is synchronous.</li>
  <li><strong>Error handling via try/catch</strong> &mdash; but in Express 5 you can often skip try/catch at the route level and rely on automatic forwarding.</li>
</ul>
'''

ANSWERS[64] = r'''
<p><code>multipart/form-data</code> is the content-type used when a form contains files &mdash; the body is split into parts, each with its own headers and binary payload. The built-in <code>express.json()</code> and <code>express.urlencoded()</code> do <em>not</em> parse it; you need a dedicated parser: <strong>multer</strong> (most common), <strong>busboy</strong> (lower-level), or <strong>formidable</strong>.</p>
<pre><code>// npm install multer
const multer = require("multer");
const path = require("node:path");

// 1. Store uploads on disk with a generated filename
const upload = multer({
  dest: "uploads/",                                 // or use storage: ... below
  limits: { fileSize: 5 * 1024 * 1024 },            // 5 MB cap
  fileFilter: (req, file, cb) =&gt; {
    const ok = ["image/jpeg", "image/png", "image/webp"].includes(file.mimetype);
    cb(ok ? null : new Error("invalid file type"), ok);
  },
});

// Single file field named "avatar"
app.post("/avatar", upload.single("avatar"), (req, res) =&gt; {
  // req.file = { fieldname, originalname, mimetype, size, path, filename, ... }
  // req.body = form text fields (also available)
  res.json({ stored: req.file.filename });
});

// Multiple files under one field
app.post("/photos", upload.array("photos", 10), (req, res) =&gt; {
  res.json({ count: req.files.length });
});

// Multiple fields
app.post("/profile", upload.fields([
  { name: "avatar", maxCount: 1 },
  { name: "banner", maxCount: 1 },
]), (req, res) =&gt; {
  res.json({ files: req.files });
});

// 2. Store in memory (small files only) — useful for processing + uploading to S3
const memUpload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 2 * 1024 * 1024 } });

app.post("/logo", memUpload.single("logo"), async (req, res) =&gt; {
  // req.file.buffer is the raw bytes
  const resized = await sharp(req.file.buffer).resize(512, 512).jpeg().toBuffer();
  await s3.putObject({ Bucket: "logos", Key: `${req.user.id}.jpg`, Body: resized });
  res.sendStatus(204);
});</code></pre>
<p><strong>Practices that prevent pain:</strong></p>
<ul>
  <li><strong>Always set <code>limits</code></strong> &mdash; a missing <code>fileSize</code> is an easy OOM vector.</li>
  <li><strong>Validate MIME <em>and</em> magic bytes.</strong> <code>mimetype</code> comes from the client and can lie. For real validation read the first bytes (<code>file-type</code> package).</li>
  <li><strong>Generate filenames server-side</strong> &mdash; never trust <code>originalname</code> as a path component (path traversal).</li>
  <li><strong>For production, stream to object storage</strong> (S3) rather than local disk &mdash; containers are ephemeral.</li>
  <li><strong>Very large uploads:</strong> prefer pre-signed S3 URLs (client uploads directly) over proxying through Node.</li>
</ul>
'''

ANSWERS[65] = r'''
<p><strong>connect-flash</strong> stores short-lived, one-time messages in the session &mdash; "Login successful!", "Invalid email." The message is set on one request, read on the next (usually after a redirect), then automatically cleared. It's the classic companion to server-rendered Express apps with template engines.</p>
<pre><code>// npm install connect-flash express-session
const session = require("express-session");
const flash   = require("connect-flash");

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
}));
app.use(flash());

// Make flash messages available to every rendered template
app.use((req, res, next) =&gt; {
  res.locals.success = req.flash("success");
  res.locals.error   = req.flash("error");
  next();
});

// Set a flash before redirecting
app.post("/login", async (req, res) =&gt; {
  const user = await authenticate(req.body);
  if (!user) {
    req.flash("error", "Incorrect email or password");
    return res.redirect("/login");
  }
  req.session.userId = user.id;
  req.flash("success", "Welcome back!");
  res.redirect("/dashboard");
});

// In your EJS/Pug/Handlebars template:
// &lt;% if (error.length) { %&gt;&lt;div class="alert"&gt;&lt;%= error %&gt;&lt;/div&gt;&lt;% } %&gt;
// &lt;% if (success.length) { %&gt;&lt;div class="ok"&gt;&lt;%= success %&gt;&lt;/div&gt;&lt;% } %&gt;</code></pre>
<p><strong>How it works:</strong> flash messages are stored under <code>req.session.flash</code>. Calling <code>req.flash(type, msg)</code> pushes a message; calling <code>req.flash(type)</code> reads <em>and clears</em> it. Because sessions persist across requests, the message survives a redirect and then vanishes.</p>
<p><strong>When to use it and when not:</strong></p>
<ul>
  <li><strong>Good for:</strong> traditional server-rendered apps &mdash; a form submits, redirects to the same or next page, and shows a status.</li>
  <li><strong>Not for SPAs / JSON APIs.</strong> Clients there already get success/error info in response bodies; flash just adds state on the server for no benefit.</li>
  <li><strong>Requires sessions</strong> (<code>express-session</code>). Without a session, there's no place to stash the message.</li>
</ul>
<p><strong>Passport users:</strong> when you use <code>passport.authenticate("local", { failureFlash: true })</code>, the strategy's error message is automatically flashed &mdash; no manual <code>req.flash()</code> call needed.</p>
'''

ANSWERS[66] = r'''
<p><strong>Input sanitization</strong> is cleaning or rejecting user input before it reaches your code or storage. It's related to but distinct from <em>validation</em>: validation says "is this input shaped correctly?" sanitization says "strip anything dangerous." Real apps need both.</p>
<pre><code>// 1. Validate THEN sanitize — Zod + sanitize-html
// npm install zod sanitize-html
const { z } = require("zod");
const sanitizeHtml = require("sanitize-html");

const CommentSchema = z.object({
  body: z.string().min(1).max(10_000).transform(v =&gt; sanitizeHtml(v, {
    allowedTags: ["b","i","em","strong","a","p","br","ul","ol","li"],
    allowedAttributes: { a: ["href", "title"] },
    allowedSchemes: ["http", "https", "mailto"],
  })),
  email: z.string().email().toLowerCase().trim(),
  displayName: z.string().max(80).trim(),
});

app.post("/comments", (req, res) =&gt; {
  const parsed = CommentSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.flatten());
  const comment = parsed.data;   // already sanitized
  // safe to persist — the body has no &lt;script&gt; tags left
});

// 2. Parameterized queries — the ONLY way to prevent SQL injection
// BAD:
// db.$queryRaw`SELECT * FROM user WHERE email = '${req.body.email}'`;
// GOOD — Prisma / pg both support parameters natively
await db.user.findUnique({ where: { email: req.body.email } });
await pool.query("SELECT * FROM user WHERE email = $1", [req.body.email]);

// 3. Against NoSQL injection — disallow operators in user input
// Mongoose / Mongo injection: { email: { $gt: "" } } matches anything
// Solution: never pass req.body directly as a query; extract scalar fields
const email = String(req.body.email ?? "");
await db.user.findOne({ email });                   // safe

// 4. Command injection — never pass user input to a shell
// BAD:  exec(`convert ${userInput} out.jpg`)
// GOOD: spawn("convert", [userInputPath, "out.jpg"])   // array args, no shell

// 5. XSS when rendering HTML — escape by default
// Template engines (EJS with &lt;%= ... %&gt;, Pug with #{...}) escape by default.
// If you bypass that (&lt;%- ... %&gt; in EJS), you're rendering raw HTML — only sanitized input.</code></pre>
<p><strong>Threats to sanitize against:</strong></p>
<ul>
  <li><strong>XSS</strong> &mdash; malicious HTML/JS rendered in a victim's browser. <code>sanitize-html</code>, <code>DOMPurify</code>, or escape at render time.</li>
  <li><strong>SQL / NoSQL injection</strong> &mdash; always use parameterized queries or an ORM; never interpolate user input into query strings.</li>
  <li><strong>Path traversal</strong> &mdash; <code>../</code> in filenames. Always <code>path.basename(userInput)</code> and confine to a base dir.</li>
  <li><strong>Command injection</strong> &mdash; never build shell strings from user input; use <code>spawn</code> with array args.</li>
  <li><strong>Prototype pollution</strong> &mdash; untrusted <code>__proto__</code> keys in JSON. Modern <code>express.json()</code> rejects these by default.</li>
</ul>
'''

ANSWERS[67] = r'''
<p>The <strong>compression</strong> middleware applies gzip or Brotli to response bodies before they go over the wire. Text content (HTML, JSON, CSS, JS) typically shrinks 70-90%. It's a one-liner that can be a massive perf win on high-latency or metered connections.</p>
<pre><code>// npm install compression
const compression = require("compression");

// Enable globally
app.use(compression());

// Common options
app.use(compression({
  level:     6,                     // 1 (fast) - 9 (best ratio); 6 is the sweet spot
  threshold: 1024,                  // don't bother compressing &lt; 1 KB responses
  filter:    (req, res) =&gt; {
    // custom opt-out: client sends this header to skip compression
    if (req.headers["x-no-compression"]) return false;
    return compression.filter(req, res);  // default: compress text-ish content types
  },
}));

// Place compression AFTER security/logging middleware but BEFORE routes
app.use(helmet());
app.use(morgan("combined"));
app.use(compression());             // &lt;-- here
app.use(express.json());
app.use("/api", apiRouter);</code></pre>
<p><strong>What gets compressed:</strong> the default filter compresses responses with a compressible content type (<code>text/*</code>, <code>application/json</code>, <code>application/javascript</code>). It skips already-compressed formats (JPEG, PNG, MP4, WebP, gzipped files) &mdash; those produce no gain and waste CPU.</p>
<p><strong>Trade-offs:</strong></p>
<ul>
  <li><strong>CPU cost:</strong> compression takes a small amount of CPU per response. Level 6 is the standard default; 9 is &sim;10&times; more CPU for a few percent better ratio.</li>
  <li><strong>Streaming:</strong> <code>compression</code> handles streams correctly &mdash; chunks are compressed as they're written.</li>
  <li><strong>At scale, terminate compression at the edge</strong> (Nginx, CloudFront, Cloudflare) &mdash; they do it faster and offload CPU from Node. The middleware is then redundant.</li>
  <li><strong>Static assets:</strong> pre-compress at build time (<code>app.js</code> &rarr; <code>app.js.gz</code> / <code>app.js.br</code>) instead of doing it on every request.</li>
  <li><strong>Brotli</strong> compresses 10-20% better than gzip for text. <code>compression</code> supports Brotli only via a patched fork or newer Node; edge termination is a safer path.</li>
  <li><strong>Security:</strong> avoid CRIME/BREACH attacks &mdash; don't mix attacker-controlled data with secrets in the same compressed response.</li>
</ul>
<p>If you're deploying behind CloudFront/Cloudflare/Nginx, disable this middleware. If not, keep it on &mdash; it's one of the easiest perf wins.</p>
'''

ANSWERS[68] = r'''
<p>A <strong>conditional GET</strong> is a GET with <code>If-None-Match</code> (ETag-based) or <code>If-Modified-Since</code> (timestamp-based) headers. If the server-side resource hasn't changed, the server replies <strong>304 Not Modified</strong> with no body. The client uses its cached copy. Q56 covered the concept; this answer focuses on conditional GET specifically.</p>
<pre><code>// Express sets ETags automatically on responses from res.send() / res.json()
app.set("etag", "strong");           // default is "weak"

app.get("/users/:id", async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.params.id } });
  if (!user) return res.sendStatus(404);
  res.json(user);                    // ETag is auto-computed, 304 is auto-returned
});

// The dance (behind the scenes):
// Request 1: GET /users/42
//   Response: 200 OK, ETag: "abc123", body: {...}
// Request 2: GET /users/42, If-None-Match: "abc123"
//   Response: 304 Not Modified, empty body   &lt;-- no DB call avoided by default!

// ⚠️ Express auto-304 works AFTER the handler runs. Use res.fresh to skip expensive work.
app.get("/big", async (req, res) =&gt; {
  const lastMod = await db.report.getLastModified();    // cheap
  res.setHeader("Last-Modified", lastMod.toUTCString());
  if (req.fresh) return res.status(304).end();          // &lt;-- skip the expensive query

  const report = await db.report.build();               // expensive
  res.json(report);
});

// Manual ETag based on a cheap-to-compute version (row version, updated_at)
app.get("/articles/:id", async (req, res) =&gt; {
  const meta = await db.article.findUnique({
    where: { id: req.params.id },
    select: { updatedAt: true },
  });
  if (!meta) return res.sendStatus(404);
  const etag = `"${meta.updatedAt.getTime()}"`;
  res.setHeader("ETag", etag);
  res.setHeader("Cache-Control", "max-age=60, must-revalidate");
  if (req.headers["if-none-match"] === etag) return res.status(304).end();

  const article = await db.article.findUnique({ where: { id: req.params.id } });
  res.json(article);
});</code></pre>
<p><strong>Where conditional GET shines:</strong></p>
<ul>
  <li><strong>Large JSON responses</strong> that rarely change &mdash; the 304 trip saves bandwidth and latency.</li>
  <li><strong>RSS / feed endpoints</strong> &mdash; feed readers poll; they benefit hugely.</li>
  <li><strong>Mobile clients</strong> on flaky connections &mdash; 304 is a near-free "still valid" signal.</li>
</ul>
<p><strong>Gotcha:</strong> Express's default ETag hashes the response body &mdash; the server has still computed the body to hash it. For expensive computations, compute a cheap version token (<code>updated_at</code>, row version) and return 304 <em>before</em> doing the work.</p>
'''

ANSWERS[69] = r'''
<p><strong><code>res.locals</code></strong> is a per-request object for passing data from middleware to the template engine (when using <code>res.render()</code>). Anything you put on <code>res.locals</code> is automatically available in the rendered view &mdash; you don't have to pass it explicitly every time.</p>
<pre><code>app.set("view engine", "ejs");
app.set("views", "./views");

// 1. Common pattern — inject the current user into every rendered page
app.use(async (req, res, next) =&gt; {
  if (req.session.userId) {
    res.locals.currentUser = await db.user.findUnique({
      where: { id: req.session.userId },
    });
  }
  res.locals.flash = req.flash();
  res.locals.env   = process.env.NODE_ENV;
  next();
});

// 2. Route handler — no need to pass currentUser again
app.get("/dashboard", (req, res) =&gt; {
  res.render("dashboard", { stats: { orders: 42 } });
  // Template sees: currentUser, flash, env (from locals) + stats (from render arg)
});

// views/dashboard.ejs — uses res.locals values directly
// &lt;% if (currentUser) { %&gt;
//   &lt;p&gt;Hi, &lt;%= currentUser.name %&gt;&lt;/p&gt;
// &lt;% } %&gt;
// &lt;% if (flash.success) { %&gt;
//   &lt;div class="ok"&gt;&lt;%= flash.success %&gt;&lt;/div&gt;
// &lt;% } %&gt;

// 3. res.locals is per-request — don't confuse with app.locals
app.locals.siteName   = "Acme";       // application-wide, set once at boot
app.locals.formatDate = (d) =&gt; d.toISOString().slice(0, 10);
// Templates also see app.locals values — but these are shared across all requests</code></pre>
<p><strong><code>res.locals</code> vs <code>app.locals</code>:</strong></p>
<table>
  <thead><tr><th>Aspect</th><th><code>res.locals</code></th><th><code>app.locals</code></th></tr></thead>
  <tbody>
    <tr><td>Scope</td><td>One request</td><td>App lifetime</td></tr>
    <tr><td>Used for</td><td>Current user, flash messages, request ID, CSRF token</td><td>Site name, helpers, config constants</td></tr>
    <tr><td>Set in</td><td>Middleware</td><td>Boot (before <code>listen</code>)</td></tr>
  </tbody>
</table>
<p><strong>Gotchas:</strong></p>
<ul>
  <li><strong>Don't store large/unbounded data on <code>res.locals</code></strong> &mdash; it's fine, but it's just a convenience; sometimes it hides dependencies.</li>
  <li><strong>Order matters:</strong> middleware that sets <code>res.locals</code> must run <em>before</em> routes that call <code>res.render</code>.</li>
  <li><strong>APIs (JSON endpoints) don't use this</strong> &mdash; it's a template-rendering helper. For APIs, build responses explicitly.</li>
</ul>
'''

ANSWERS[70] = r'''
<p>Chaining handlers means registering multiple functions for the same route so they run in order. Express supports this at the route level (multiple handler args) and via <code>app.route()</code> (fluent API for grouping same-path routes).</p>
<pre><code>// 1. Multiple handlers in one route — just pass them as varargs
const validate = (schema) =&gt; (req, res, next) =&gt; { /* ... */ next(); };
const authorize = (req, res, next) =&gt; { /* ... */ next(); };
const logAction = (req, res, next) =&gt; { /* ... */ next(); };

app.post("/articles",
  authenticate,
  authorize,
  validate(CreateArticle),
  logAction,
  async (req, res) =&gt; {
    const article = await db.article.create({ data: req.body });
    res.status(201).json(article);
  }
);

// Each handler MUST call next() to advance; otherwise the chain stops.

// 2. Pass as an array — useful when you want to name the pipeline
const articleCreatePipeline = [authenticate, authorize, validate(CreateArticle)];
app.post("/articles", articleCreatePipeline, async (req, res) =&gt; {
  const article = await db.article.create({ data: req.body });
  res.status(201).json(article);
});

// 3. app.route() — fluent chaining for the same path across methods
app.route("/articles/:id")
  .all(authenticate)                        // runs for GET, PATCH, DELETE
  .get(async (req, res) =&gt; res.json(await db.article.findUnique({ where: { id: req.params.id } })))
  .patch(authorize, validate(UpdateArticle), async (req, res) =&gt; {
    const article = await db.article.update({ where: { id: req.params.id }, data: req.body });
    res.json(article);
  })
  .delete(authorize, async (req, res) =&gt; {
    await db.article.delete({ where: { id: req.params.id } });
    res.sendStatus(204);
  });

// 4. Short-circuit with return — stop the chain by responding
app.get("/premium", requireSubscription, (req, res) =&gt; {
  if (!req.user.active) return res.status(402).send("payment required");
  res.send("welcome");
});</code></pre>
<p><strong>Why chain handlers:</strong></p>
<ul>
  <li><strong>Separation of concerns</strong> &mdash; auth, validation, audit, business logic are each their own function.</li>
  <li><strong>Reuse</strong> &mdash; <code>authenticate</code> goes in front of every protected route; validators are per-schema.</li>
  <li><strong>Readable route table</strong> &mdash; you can see the pipeline for each route at a glance.</li>
</ul>
<p><strong>Rules:</strong> each handler must call <code>next()</code> to continue, or send a response and <code>return</code>. The last handler is the actual route logic; it doesn't need to call <code>next()</code>. Error middleware (4-arg) sits at the end of the app.</p>
'''

ANSWERS[71] = r'''
<p><strong>Subdomains</strong> are handled at two layers: your DNS (maps <code>api.example.com</code>, <code>admin.example.com</code> to the server) and your Express app (routes requests based on the <code>Host</code> header). Express doesn't parse subdomains into its router by default &mdash; you use middleware or the <code>vhost</code> package.</p>
<pre><code>// 1. Set subdomain offset — tells Express where the "domain" ends
// For example.com, offset=2 means req.subdomains is everything beyond the last 2 labels.
app.set("subdomain offset", 2);

app.get("/", (req, res) =&gt; {
  // api.example.com -&gt; req.subdomains = ["api"]
  // admin.v2.example.com -&gt; req.subdomains = ["v2", "admin"]
  res.json({ subdomains: req.subdomains, host: req.hostname });
});

// 2. Route based on subdomain with custom middleware
app.use((req, res, next) =&gt; {
  const sub = req.subdomains[0];
  if (sub === "api")   return apiRouter(req, res, next);
  if (sub === "admin") return adminRouter(req, res, next);
  mainRouter(req, res, next);
});

// 3. vhost middleware — cleaner for distinct sub-apps
// npm install vhost
const vhost = require("vhost");

const apiApp   = express(); /* ... */
const adminApp = express(); /* ... */
const mainApp  = express(); /* ... */

const top = express();
top.use(vhost("api.example.com",   apiApp));
top.use(vhost("admin.example.com", adminApp));
top.use(vhost("example.com",       mainApp));
top.use(vhost("*.example.com",     mainApp));   // wildcard fallback
top.listen(3000);

// 4. HTTPS/cert notes — each subdomain needs a cert (or wildcard)
// Let's Encrypt: *.example.com wildcard cert covers all subs; a few DNS hops to set up.</code></pre>
<p><strong>Design choices:</strong></p>
<ul>
  <li><strong>Different apps per subdomain</strong> &mdash; <code>vhost</code> is ideal. Each sub-app has its own middleware stack, routers, and views.</li>
  <li><strong>Same app with subdomain-aware routes</strong> &mdash; a single middleware branch on <code>req.subdomains</code> is enough.</li>
  <li><strong>Cookies and CORS</strong> become tricky across subdomains. Set cookie <code>domain: ".example.com"</code> if you want sharing; use CORS headers that match the sub.</li>
  <li><strong>Proxy trust:</strong> behind a load balancer, enable <code>app.set("trust proxy", 1)</code> so <code>req.hostname</code> reads from <code>X-Forwarded-Host</code> correctly.</li>
  <li><strong>Tenant-per-subdomain</strong> (<code>acme.yourapp.com</code>): common SaaS pattern; use the subdomain to look up the tenant and attach to <code>req.tenant</code>.</li>
</ul>
'''

ANSWERS[72] = r'''
<p><code>express.static()</code> is the built-in middleware that serves files from a directory. Behind the scenes it uses the <code>serve-static</code> package &mdash; it sets MIME types, <code>Last-Modified</code>, ETag, handles range requests, and supports cache headers. Q11 covered the basics; this answer digs into the configuration.</p>
<pre><code>// Minimum — serve files from ./public at the root
app.use(express.static("public"));

// Under a prefix — /static/app.css -&gt; public/app.css
app.use("/static", express.static("public"));

// With options
app.use("/assets", express.static("dist", {
  maxAge:      "30d",         // Cache-Control: max-age=2592000
  immutable:   true,          // "this never changes" — works with hashed filenames
  etag:        true,          // default on
  lastModified:true,          // default on
  index:       false,         // don't auto-serve index.html for directory requests
  dotfiles:    "ignore",      // "allow" | "deny" | "ignore" — how to handle .env, .git
  fallthrough: true,          // if file not found, pass to next middleware (default)
  extensions:  ["html"],      // try /about.html when /about is requested
  setHeaders:  (res, path, stat) =&gt; {
    if (path.endsWith(".wasm")) res.setHeader("Content-Type", "application/wasm");
  },
}));

// Multiple static dirs — tried in registration order
app.use(express.static("public"));
app.use(express.static("uploads"));       // fallback

// Serve a single-page app — fallback to index.html for unknown routes
app.use(express.static("dist"));
app.get(/^\/(?!api).*/, (req, res) =&gt; {   // everything not starting with /api
  res.sendFile(path.resolve("dist/index.html"));
});</code></pre>
<p><strong>Production best practices:</strong></p>
<ul>
  <li><strong>Offload static files to a CDN</strong> (CloudFront, Cloudflare, Fastly). Your Node event loop should not be babysitting bytes &mdash; CDNs cache at the edge, closer to users.</li>
  <li><strong>Hashed filenames + <code>immutable</code></strong> &mdash; <code>app.a4f9b.js</code> paired with <code>maxAge: "365d"</code> means browsers cache forever; deploys invalidate via filename change.</li>
  <li><strong>Never serve the repo root.</strong> A misconfigured <code>express.static(".")</code> exposes <code>.env</code>, source code, <code>.git</code>.</li>
  <li><strong>Place early in the middleware chain</strong> &mdash; static hits skip your auth, body parsers, and loggers.</li>
  <li><strong>Security headers</strong> (Helmet's CSP, X-Content-Type-Options) matter for static content too.</li>
</ul>
'''

ANSWERS[73] = r'''
<p><strong>HTTP method override</strong> lets clients that can only send GET or POST (traditional HTML forms, some legacy proxies) simulate PUT, PATCH, DELETE. The client sends a POST with a special field or header; the <code>method-override</code> middleware rewrites <code>req.method</code> before routing runs.</p>
<pre><code>// npm install method-override
const methodOverride = require("method-override");

// Must run BEFORE your routes
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// 1. Override via body field — common with HTML forms
app.use(methodOverride("_method"));
// Now a POST with _method=DELETE in body is routed as DELETE
//
// &lt;form method="POST" action="/articles/42?_method=DELETE"&gt;
//   &lt;button&gt;Delete&lt;/button&gt;
// &lt;/form&gt;

// 2. Override via custom header (useful for APIs)
app.use(methodOverride("X-HTTP-Method-Override"));
//   fetch("/articles/42", { method: "POST", headers: { "X-HTTP-Method-Override": "DELETE" } })

// 3. Custom function — multiple signals
app.use(methodOverride((req, res) =&gt; {
  if (req.body &amp;&amp; req.body._method) {
    const method = req.body._method;
    delete req.body._method;
    return method;
  }
  if (req.headers["x-http-method-override"]) return req.headers["x-http-method-override"];
}));

// Your routes don't change — they still register on the "real" method
app.delete("/articles/:id", (req, res) =&gt; { /* ... */ });
app.patch("/articles/:id",  (req, res) =&gt; { /* ... */ });</code></pre>
<p><strong>When you'd use this:</strong></p>
<ul>
  <li><strong>Server-rendered apps with HTML forms.</strong> Browsers' <code>&lt;form method="..."&gt;</code> supports only GET and POST. To do RESTful CRUD from a form, override is the workaround.</li>
  <li><strong>Rails-style MVC apps</strong> &mdash; the pattern comes from that world.</li>
  <li><strong>Legacy clients</strong> that pass through proxies blocking non-standard HTTP methods.</li>
</ul>
<p><strong>When you don't need it:</strong></p>
<ul>
  <li><strong>SPAs / JSON APIs.</strong> <code>fetch()</code> and every HTTP client send any method directly &mdash; no override needed.</li>
  <li><strong>Mobile apps.</strong> Same story.</li>
</ul>
<p><strong>Security:</strong> <code>method-override</code> changes the semantics of a request. If you use it, make sure your CSRF protection validates the <em>overridden</em> method (not just POST), and that you don't accidentally expose destructive operations to GET-only clients.</p>
'''

ANSWERS[74] = r'''
<p><strong>Internationalization (i18n)</strong> means serving content in the user's language. In Express, this is usually the <strong>i18next</strong> ecosystem with Express middleware: it detects the language, loads translation files, and exposes a <code>t()</code> function to your templates and handlers.</p>
<pre><code>// npm install i18next i18next-fs-backend i18next-http-middleware
const i18next    = require("i18next");
const Backend    = require("i18next-fs-backend");
const middleware = require("i18next-http-middleware");

await i18next
  .use(Backend)
  .use(middleware.LanguageDetector)
  .init({
    fallbackLng: "en",
    preload: ["en", "es", "fr"],
    backend: { loadPath: "./locales/{{lng}}/{{ns}}.json" },
    detection: {
      order: ["querystring", "cookie", "header"],
      lookupQuerystring: "lng",
      lookupCookie: "lang",
      caches: ["cookie"],
    },
  });

app.use(middleware.handle(i18next));

// locales/en/translation.json
// { "welcome": "Welcome, {{name}}!", "errors": { "notFound": "Not found" } }
// locales/es/translation.json
// { "welcome": "¡Bienvenido, {{name}}!", "errors": { "notFound": "No encontrado" } }

// In a route — req.t() is the translation function for this request's language
app.get("/hello", (req, res) =&gt; {
  res.json({ message: req.t("welcome", { name: req.user?.name ?? "friend" }) });
});

// In a template — t is available via res.locals (i18next-http-middleware sets it)
// &lt;h1&gt;&lt;%= t('welcome', { name: user.name }) %&gt;&lt;/h1&gt;

// Errors localized
app.get("/users/:id", async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.params.id } });
  if (!user) return res.status(404).json({ error: req.t("errors.notFound") });
  res.json(user);
});</code></pre>
<p><strong>Without a library, using <code>Intl</code> directly</strong> (pure Node):</p>
<pre><code>// Numbers, currencies, dates — Intl is built in
new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(1234.5);
// "1.234,50 €"
new Intl.DateTimeFormat("ja-JP", { dateStyle: "long" }).format(new Date());
// "2026年4月18日"</code></pre>
<p><strong>What a good i18n setup covers:</strong></p>
<ul>
  <li><strong>Language detection</strong> &mdash; URL param &gt; cookie &gt; <code>Accept-Language</code> &gt; fallback.</li>
  <li><strong>ICU message format</strong> for plurals and gender: <code>{count, plural, one {# item} other {# items}}</code>.</li>
  <li><strong>Namespaces</strong> &mdash; split translations by area (<code>auth.json</code>, <code>checkout.json</code>) to keep files manageable.</li>
  <li><strong>Translation management</strong> &mdash; hosted services like Lokalise, Crowdin, or Tolgee plug into i18next and sync strings with translators.</li>
  <li><strong>Date/number formatting</strong> via <code>Intl</code> &mdash; don't hand-format dates.</li>
</ul>
'''

ANSWERS[75] = r'''
<p><strong>Range requests</strong> let a client fetch a specific byte range from a resource: "give me bytes 1,000,000-2,000,000 of this video." They enable seek-in-video, resume-on-download, and parallel chunk fetching. Express's <code>res.sendFile</code> and <code>express.static</code> handle ranges automatically for files on disk.</p>
<pre><code>// For files on disk, Express / serve-static handle ranges out of the box
app.get("/videos/:name", (req, res) =&gt; {
  res.sendFile(path.join(videoDir, req.params.name), { acceptRanges: true });
});

// For custom streams (e.g., S3, generated data), implement ranges manually
const fs = require("node:fs");

app.get("/stream/:id", async (req, res) =&gt; {
  const filePath = pathForId(req.params.id);
  const stat = await fs.promises.stat(filePath);
  const total = stat.size;
  const range = req.headers.range;

  if (!range) {
    // No range — send the whole file
    res.writeHead(200, {
      "Content-Length": total,
      "Content-Type":   "video/mp4",
      "Accept-Ranges":  "bytes",
    });
    return fs.createReadStream(filePath).pipe(res);
  }

  // Parse: "bytes=1000-1999" or "bytes=1000-"
  const match = /^bytes=(\d+)-(\d+)?$/.exec(range);
  if (!match) {
    res.writeHead(416, { "Content-Range": `bytes */${total}` });  // not satisfiable
    return res.end();
  }
  const start = Number(match[1]);
  const end   = match[2] ? Number(match[2]) : total - 1;
  if (start &gt;= total || end &gt;= total) {
    res.writeHead(416, { "Content-Range": `bytes */${total}` });
    return res.end();
  }

  res.writeHead(206, {                        // 206 Partial Content
    "Content-Range":  `bytes ${start}-${end}/${total}`,
    "Accept-Ranges":  "bytes",
    "Content-Length": end - start + 1,
    "Content-Type":   "video/mp4",
  });
  fs.createReadStream(filePath, { start, end }).pipe(res);
});</code></pre>
<p><strong>How the dance works:</strong></p>
<ol>
  <li>Client sends <code>Range: bytes=0-</code> (or <code>bytes=10000-20000</code>).</li>
  <li>Server responds with <strong>206 Partial Content</strong>, <code>Content-Range: bytes start-end/total</code>, and the byte slice.</li>
  <li>If the range is invalid: <strong>416 Range Not Satisfiable</strong>.</li>
  <li>If the server doesn't support ranges: ignores the header, returns <code>200</code>.</li>
</ol>
<p><strong>When you need manual handling:</strong> streaming from S3, database blobs, on-the-fly generated data. <strong>When you don't:</strong> regular files via <code>res.sendFile</code> or <code>express.static</code> &mdash; it's already built in. For serious video delivery, use a CDN with origin range support (CloudFront, Bunny) &mdash; they cache ranges at edge locations.</p>
'''

ANSWERS[76] = r'''
<p><code>cookie-parser</code> is middleware that parses the <code>Cookie</code> header into <code>req.cookies</code>, and optionally validates signed cookies into <code>req.signedCookies</code>. Without it, you'd have to parse the cookie header manually every request.</p>
<pre><code>// npm install cookie-parser
import express from "express";
import cookieParser from "cookie-parser";

const app = express();

// secret → enables signed cookies (tamper detection)
app.use(cookieParser(process.env.COOKIE_SECRET));

app.get("/set", (req, res) =&gt; {
  res.cookie("theme", "dark", {
    maxAge: 7 * 24 * 3600 * 1000,       // 7 days
    httpOnly: true,                     // not accessible via JS → mitigates XSS cookie theft
    secure: true,                       // HTTPS only
    sameSite: "lax",                    // CSRF mitigation
  });
  // signed cookie — value + HMAC
  res.cookie("uid", "42", { signed: true, httpOnly: true });
  res.send("cookies set");
});

app.get("/read", (req, res) =&gt; {
  console.log(req.cookies);             // { theme: "dark" } — unsigned
  console.log(req.signedCookies);       // { uid: "42" } — signed &amp; verified
  res.json({ ok: true });
});

app.get("/clear", (req, res) =&gt; {
  res.clearCookie("theme");
  res.send("cleared");
});

app.listen(3000);</code></pre>
<p><strong>Signed vs unsigned:</strong></p>
<ul>
  <li><strong>Unsigned</strong> &mdash; appear in <code>req.cookies</code>. The client can edit them in browser devtools; treat them as user input.</li>
  <li><strong>Signed</strong> &mdash; prefixed with an HMAC. <code>cookie-parser</code> verifies; tampered cookies become <code>false</code> in <code>req.signedCookies</code>. Use for low-risk identifiers you want to trust &mdash; <em>not</em> for session state (use <code>express-session</code> or JWT instead).</li>
</ul>
<p><strong>Security flags you should always set:</strong></p>
<ul>
  <li><code>httpOnly: true</code> &mdash; hides the cookie from <code>document.cookie</code>, preventing XSS theft.</li>
  <li><code>secure: true</code> &mdash; only transmitted over HTTPS.</li>
  <li><code>sameSite: "lax"</code> or <code>"strict"</code> &mdash; prevents cross-site request forgery (CSRF) on top-level navigations.</li>
</ul>
<p>For session cookies specifically, <code>express-session</code> and <code>cookie-session</code> both use <code>cookie-parser</code> conventions. <strong>Note:</strong> Express 5 no longer requires <code>cookie-parser</code> if you only need to <em>set</em> cookies &mdash; <code>res.cookie()</code> works without it. It's still needed to <em>read</em> them from <code>req.cookies</code>.</p>
'''

ANSWERS[77] = r'''
<p>Rate limiting caps how many requests a client can make in a time window &mdash; protects against brute-force logins, scraping, and accidental runaway clients. The standard Express middleware is <strong><code>express-rate-limit</code></strong>.</p>
<pre><code>// npm install express-rate-limit
import express from "express";
import rateLimit from "express-rate-limit";

const app = express();

// general API limiter — 100 req / 15 min / IP
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,              // RateLimit-* headers (RFC 9331)
  legacyHeaders:   false,             // drop X-RateLimit-* old headers
  message: { error: "Too many requests, try again later." },
});
app.use("/api", apiLimiter);

// tighter limit on auth endpoints — 5 attempts / 15 min / IP
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,       // only count failed logins
});
app.post("/api/login",  authLimiter, loginHandler);
app.post("/api/signup", authLimiter, signupHandler);

// per-user (not per-IP) — needs auth to run first
const perUserLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 30,
  keyGenerator: (req) =&gt; req.user?.id ?? req.ip,
});

app.listen(3000);</code></pre>
<p><strong>Critical behind a proxy:</strong> your Node app sees the proxy's IP, not the client's. Enable the trust-proxy setting so Express reads <code>X-Forwarded-For</code>:</p>
<pre><code>app.set("trust proxy", 1);            // trust the first proxy — adjust to match your infra</code></pre>
<p>Without this, every client looks like the load balancer and the limit triggers immediately.</p>
<p><strong>For production, use a shared store:</strong></p>
<ul>
  <li>The default in-memory store is <em>per-process</em> &mdash; with multiple Node instances, each tracks its own count and the global limit is effectively <code>instances &times; max</code>.</li>
  <li>Install <code>rate-limit-redis</code> to back the limiter with Redis and share the count across all instances.</li>
</ul>
<p><strong>Alternatives and advanced needs:</strong> <code>rate-limiter-flexible</code> offers token bucket, sliding window, and per-key strategies; Nginx and Cloudflare do rate limiting at the edge for cheaper DoS protection. Never rely on Express as your only rate-limit layer if you're exposed to the public internet &mdash; put a CDN or WAF in front too.</p>
'''

ANSWERS[78] = r'''
<p>Express itself doesn't speak WebSocket &mdash; the protocol starts with an HTTP <em>upgrade</em> handshake that Express routes don't handle. You attach a WebSocket library to the same HTTP server that Express is using, so both share a port. The two common choices are <strong><code>ws</code></strong> (minimal) and <strong>Socket.IO</strong> (higher-level with reconnect, rooms, fallbacks).</p>
<pre><code>// Option A — raw ws with shared HTTP server
// npm install ws
import express from "express";
import http from "node:http";
import { WebSocketServer } from "ws";

const app = express();
app.get("/", (req, res) =&gt; res.send("HTTP ok"));

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: "/ws" });

wss.on("connection", (ws, req) =&gt; {
  console.log("client connected from", req.socket.remoteAddress);
  ws.send(JSON.stringify({ type: "welcome" }));
  ws.on("message", (buf) =&gt; {
    const msg = JSON.parse(buf.toString());
    ws.send(JSON.stringify({ echo: msg }));
  });
  ws.on("close", () =&gt; console.log("disconnected"));
});

server.listen(3000);                  // both Express and WS on :3000</code></pre>
<pre><code>// Option B — Socket.IO (rooms, auto-reconnect, fallbacks)
// npm install socket.io
import { Server } from "socket.io";
const io = new Server(server, { cors: { origin: "*" } });

io.on("connection", (socket) =&gt; {
  socket.join(`user:${socket.handshake.auth.userId}`);
  socket.on("chat:send", (msg) =&gt; {
    io.to(`room:${msg.room}`).emit("chat:new", msg);
  });
});</code></pre>
<p><strong>Key design considerations:</strong></p>
<ul>
  <li><strong>Authenticate on the upgrade.</strong> Pass a token via <code>Sec-WebSocket-Protocol</code> or a query param; verify before accepting the connection. Anyone who reaches the socket has full access until you disconnect them.</li>
  <li><strong>Scale out with a Redis adapter.</strong> With multiple Node instances, <code>@socket.io/redis-adapter</code> broadcasts across processes; <code>ws</code> alone needs you to build this yourself.</li>
  <li><strong>Reverse proxies.</strong> Nginx and ALBs need WebSocket support enabled (<code>proxy_set_header Upgrade</code> / ALB target group with WS enabled).</li>
  <li><strong>Keep connections short-lived.</strong> Heartbeats detect dead peers; idle timeouts at the proxy kill stale connections you don't track.</li>
</ul>
<p>For most modern apps, Socket.IO saves enough wiring to be worth the extra bytes. For high-throughput, low-overhead use cases (IoT, financial data), <code>ws</code> or <strong>uWebSockets.js</strong> win on performance.</p>
'''

ANSWERS[79] = r'''
<p><strong>CSRF</strong> (Cross-Site Request Forgery) is an attack where a malicious site makes a logged-in user's browser perform actions on another site, using the user's cookies. <code>csurf</code> was the historical Express middleware &mdash; it was <strong>deprecated in 2022</strong>. The modern replacement is <a href="https://github.com/Psifi-Solutions/csrf-csrf"><code>csrf-csrf</code></a> (double-submit cookie pattern).</p>
<pre><code>// Modern replacement: csrf-csrf (npm install csrf-csrf)
import express from "express";
import cookieParser from "cookie-parser";
import { doubleCsrf } from "csrf-csrf";

const app = express();
app.use(cookieParser(process.env.COOKIE_SECRET));
app.use(express.json());

const { doubleCsrfProtection, generateToken } = doubleCsrf({
  getSecret: () =&gt; process.env.CSRF_SECRET,
  cookieName: "__Host-psifi.x-csrf-token",
  cookieOptions: { sameSite: "lax", secure: true, httpOnly: true },
});

// expose a token to the client (usually via /csrf-token endpoint or embedded in the page)
app.get("/csrf-token", (req, res) =&gt; {
  res.json({ csrfToken: generateToken(req, res) });
});

app.use(doubleCsrfProtection);        // protects all following routes

// client must send the token in a header (default: x-csrf-token) on POST/PUT/PATCH/DELETE
app.post("/transfer", (req, res) =&gt; {
  res.json({ ok: true });
});

app.listen(3000);</code></pre>
<p><strong>How CSRF protection works:</strong></p>
<ol>
  <li>Server generates a random token, sends it to the browser (in a cookie <em>and</em> exposed to JS/templates).</li>
  <li>On state-changing requests, the client sends the token in a header or form field.</li>
  <li>Server checks the header/form token matches the one bound to the session/cookie.</li>
  <li>A malicious site can read neither the header value (same-origin policy) nor trigger custom headers, so the check fails.</li>
</ol>
<p><strong>When you still need CSRF protection:</strong></p>
<ul>
  <li><strong>Cookie-based auth</strong> with form submissions. If the browser automatically sends your session cookie, CSRF applies.</li>
  <li><strong>Not needed</strong> for <code>Authorization: Bearer</code> APIs (the browser doesn't auto-send that header from a foreign origin) or with strict <code>SameSite=strict</code> cookies (but strict breaks legit cross-tab flows, so lax + CSRF tokens is the safer combo).</li>
</ul>
<p><strong>Historical note:</strong> <code>csurf</code> is archived and has known vulnerabilities. If an old codebase still uses it, migrate to <code>csrf-csrf</code>, switch to token-based auth, or delegate to a framework like NestJS or Next.js that handles CSRF natively.</p>
'''

ANSWERS[80] = r'''
<p><strong>JSONP</strong> (JSON with Padding) is a legacy technique for calling cross-origin APIs before CORS existed. The client adds a <code>&lt;script src="api.com/data?callback=foo"&gt;</code> tag; the server responds with <code>foo({...})</code>, which executes as JS. Express has built-in <code>res.jsonp()</code> to wrap JSON in a callback name.</p>
<pre><code>import express from "express";
const app = express();

// default callback query parameter is "callback"
app.get("/api/data", (req, res) =&gt; {
  res.jsonp({ users: [{ id: 1, name: "Ada" }] });
});
// GET /api/data?callback=handleData
// → handleData({ "users": [{ "id": 1, "name": "Ada" }] })

// change the callback param name
app.set("jsonp callback name", "cb");
// GET /api/data?cb=handleData

app.listen(3000);</code></pre>
<p>Client side:</p>
<pre><code>function handleData(data) { console.log(data); }

const s = document.createElement("script");
s.src = "http://api.example.com/api/data?callback=handleData";
document.body.appendChild(s);</code></pre>
<p><strong>Important: don't use JSONP for new work.</strong></p>
<ul>
  <li><strong>Security risk.</strong> You're executing arbitrary JavaScript from a remote origin with no CSP protection. A compromised API serves malicious script to every consumer.</li>
  <li><strong>GET-only.</strong> <code>&lt;script&gt;</code> tags only make GET requests; no POST/PUT/DELETE.</li>
  <li><strong>No error handling.</strong> A 500 response doesn't trigger <code>onerror</code> predictably.</li>
  <li><strong>No headers access.</strong> You can't read the response's headers or status.</li>
  <li><strong>Superseded by CORS.</strong> Every browser supports CORS; it's safer and more capable.</li>
</ul>
<p><strong>Where you might still encounter it:</strong> very old APIs, legacy integrations with clients you can't update, and a few ad/analytics SDKs. If you're writing a new public API, use CORS:</p>
<pre><code>import cors from "cors";
app.use("/api", cors({ origin: ["https://consumer.example.com"] }));</code></pre>
<p>Then clients fetch normally: <code>fetch("https://api.example.com/api/data").then(r =&gt; r.json())</code>. The only reason <code>res.jsonp()</code> still exists is backwards compatibility &mdash; treat it as documentation of a historical era, not a tool to reach for.</p>
'''

ANSWERS[81] = r'''
<p><strong>Graceful shutdown</strong> means: stop accepting new connections, let in-flight requests finish, close DB/Redis connections, then exit. A hard <code>process.exit(0)</code> mid-request cuts responses off and can corrupt state. In containers (Kubernetes, ECS) the runtime sends SIGTERM and gives you a grace period before SIGKILL; your job is to use it properly.</p>
<pre><code>import express from "express";
import http from "node:http";

const app = express();
app.get("/health", (_req, res) =&gt; res.send("ok"));
app.get("/slow",   async (_req, res) =&gt; {
  await new Promise(r =&gt; setTimeout(r, 5000));
  res.send("done");
});

const server = http.createServer(app);
server.listen(3000);

let isShuttingDown = false;

// readiness probe fails once shutting down → load balancer stops sending new traffic
app.get("/ready", (_req, res) =&gt;
  res.status(isShuttingDown ? 503 : 200).send(isShuttingDown ? "shutting down" : "ready"));

async function shutdown(signal) {
  if (isShuttingDown) return;
  isShuttingDown = true;
  console.log(`${signal} received — starting graceful shutdown`);

  // 1. stop taking new connections
  server.close((err) =&gt; {
    if (err) console.error("server.close error:", err);
    else    console.log("HTTP server closed");
  });

  // 2. close DB / Redis / queues
  try {
    await db.$disconnect();             // Prisma
    await redis.quit();                 // ioredis
    console.log("resources closed");
  } catch (err) {
    console.error("shutdown resource error:", err);
  }

  // 3. force-exit if anything is still hanging after the grace period
  setTimeout(() =&gt; {
    console.error("forcing exit after timeout");
    process.exit(1);
  }, 25_000).unref();                   // shorter than Kubernetes' 30s terminationGracePeriodSeconds
}

process.on("SIGTERM", () =&gt; shutdown("SIGTERM"));
process.on("SIGINT",  () =&gt; shutdown("SIGINT"));</code></pre>
<p><strong>Rules that matter:</strong></p>
<ul>
  <li><strong>Fail readiness checks immediately.</strong> This signals the load balancer to route away <em>before</em> you close the server.</li>
  <li><strong>Don't do work in process handlers.</strong> Keep <code>SIGTERM</code> handler fast &mdash; delegate to an async <code>shutdown()</code>.</li>
  <li><strong>Respect the grace period.</strong> Kubernetes default is 30s; finish cleanup inside that window or get SIGKILLed.</li>
  <li><strong>Close WebSocket and keep-alive connections.</strong> <code>server.close()</code> waits for active sockets; in Node 18.2+, <code>server.closeAllConnections()</code> force-terminates them if they stay open too long.</li>
  <li><strong>Packages help:</strong> <code>http-terminator</code> or <code>stoppable</code> handle the keep-alive edge cases for you.</li>
</ul>
'''

ANSWERS[82] = r'''
<p><code>serve-favicon</code> serves the site's <code>favicon.ico</code> efficiently: it caches the file in memory and returns 304 Not Modified when browsers ask again. Without it, every favicon request hits your logs and handlers &mdash; and browsers request it constantly.</p>
<pre><code>// npm install serve-favicon
import express from "express";
import favicon from "serve-favicon";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

// register BEFORE your logger / routes
app.use(favicon(path.join(__dirname, "public", "favicon.ico")));

app.get("/", (req, res) =&gt; res.send("home"));
app.listen(3000);</code></pre>
<p><strong>Why use it:</strong></p>
<ul>
  <li><strong>In-memory cache.</strong> The icon is read once on startup; subsequent requests never hit disk.</li>
  <li><strong>Proper caching headers.</strong> Sets <code>Cache-Control: public, max-age=...</code> so browsers stop asking.</li>
  <li><strong>Filtered out of logs.</strong> Placed before <code>morgan</code>, favicon requests never pollute your access log.</li>
</ul>
<p><strong>Do you actually need it?</strong></p>
<ul>
  <li><strong>If you're already using <code>express.static("public")</code></strong> and your favicon lives in <code>public/favicon.ico</code>, browsers will find it automatically &mdash; <code>serve-favicon</code> is not strictly necessary. It just adds caching and log-filtering.</li>
  <li><strong>If you serve static files via a CDN</strong> (Cloudflare, CloudFront), the CDN caches the favicon at the edge; the middleware's benefits disappear.</li>
  <li><strong>For production SPAs</strong> on Vercel/Netlify, the platform serves the favicon from its CDN &mdash; no Node code involved.</li>
</ul>
<p><strong>Modern favicons</strong> are more than one <code>.ico</code> file &mdash; you also want <code>apple-touch-icon.png</code>, various PNG sizes, and a <code>manifest.webmanifest</code>. Generate a full set with <strong>RealFaviconGenerator</strong> or the <strong>favicons</strong> npm package, then serve the whole directory via <code>express.static</code>. <code>serve-favicon</code> only handles the single <code>.ico</code>; the rest go through the static middleware (or a CDN).</p>
'''

ANSWERS[83] = r'''
<p>File streams are how you send large files to clients without loading the whole thing into memory. Node's <code>fs.createReadStream()</code> emits chunks as they're read; piping it into <code>res</code> lets Express push bytes to the client continuously. The built-in <code>res.sendFile()</code> wraps this pattern with MIME detection and range support.</p>
<pre><code>import express from "express";
import fs from "node:fs";
import path from "node:path";

const app = express();

// 1. simplest — res.sendFile handles stream, MIME, ranges, caching
app.get("/files/:name", (req, res, next) =&gt; {
  const abs = path.resolve("./uploads", req.params.name);
  res.sendFile(abs, (err) =&gt; {
    if (err) next(err);                    // pass to error handler instead of crashing
  });
});

// 2. manual streaming — useful when transforming or sourcing from non-disk
app.get("/report.csv", (req, res) =&gt; {
  res.setHeader("Content-Type",        "text/csv");
  res.setHeader("Content-Disposition", "attachment; filename=\"report.csv\"");

  const stream = fs.createReadStream("./big-report.csv");
  stream.on("error", (err) =&gt; {
    if (!res.headersSent) res.sendStatus(500);
    else res.destroy(err);                 // can't un-send headers; tear down
  });
  stream.pipe(res);                        // res is a Writable; pipe handles backpressure
});

// 3. modern: pipeline() — cleaner error handling
import { pipeline } from "node:stream/promises";
app.get("/pdf/:id", async (req, res, next) =&gt; {
  try {
    res.setHeader("Content-Type", "application/pdf");
    await pipeline(fs.createReadStream(`./pdfs/${req.params.id}.pdf`), res);
  } catch (err) { next(err); }
});

app.listen(3000);</code></pre>
<p><strong>Why streams matter:</strong></p>
<ul>
  <li><strong>Constant memory.</strong> Sending a 2 GB video uses &lt; 100 KB of buffer regardless of file size.</li>
  <li><strong>Progressive delivery.</strong> The client starts receiving bytes before the whole file is read &mdash; faster time-to-first-byte.</li>
  <li><strong>Backpressure.</strong> <code>pipe</code>/<code>pipeline</code> automatically pause the read when the socket buffer fills, resume when it drains.</li>
</ul>
<p><strong>Common mistakes:</strong></p>
<ul>
  <li><strong>Reading the file into memory first</strong> (<code>fs.readFile</code> + <code>res.send</code>) &mdash; OOMs on big files.</li>
  <li><strong>Not handling stream errors.</strong> A read error with no <code>on("error")</code> crashes the process. Always attach an error handler or use <code>pipeline</code>.</li>
  <li><strong>Forgetting headers before piping.</strong> Once the stream starts, you can't set <code>Content-Type</code> or <code>Content-Length</code>.</li>
</ul>
<p>For huge files or many concurrent downloads, offload to S3 + pre-signed URLs or a CDN &mdash; don't serve them from your Node process.</p>
'''

ANSWERS[84] = r'''
<p><code>vhost</code> ("virtual host") routes requests to different Express apps based on the <code>Host</code> header. A single Node process can serve <code>api.example.com</code>, <code>admin.example.com</code>, and <code>www.example.com</code> from three isolated apps.</p>
<pre><code>// npm install vhost
import express from "express";
import vhost from "vhost";

// app 1 — marketing site
const site = express();
site.get("/", (req, res) =&gt; res.send("Welcome to example.com"));

// app 2 — JSON API
const api = express();
api.use(express.json());
api.get("/status", (req, res) =&gt; res.json({ ok: true }));

// app 3 — admin dashboard
const admin = express();
admin.use((req, res, next) =&gt; {
  if (!isAdmin(req)) return res.sendStatus(403);
  next();
});
admin.get("/", (req, res) =&gt; res.send("admin panel"));

// main app — dispatches by Host header
const main = express();
main.use(vhost("www.example.com",   site));
main.use(vhost("api.example.com",   api));
main.use(vhost("admin.example.com", admin));
main.use(vhost("*.example.com",     site));   // wildcard fallback

main.listen(3000);</code></pre>
<p><strong>When is this useful?</strong></p>
<ul>
  <li>A side project or internal tool where spinning up three separate services feels excessive.</li>
  <li>Multi-tenancy by subdomain, e.g. <code>customer1.myapp.com</code>, <code>customer2.myapp.com</code>:
<pre><code>main.use(vhost("*.myapp.com", (req, res, next) =&gt; {
  req.tenantId = req.vhost[0];           // "customer1"
  tenantApp(req, res, next);
}));</code></pre>
  </li>
  <li>Local development where you want <code>localhost</code> and <code>api.localhost</code> on the same port.</li>
</ul>
<p><strong>Why you probably shouldn't use it in production:</strong></p>
<ul>
  <li><strong>Coupled deploys.</strong> One bug brings all subdomains down.</li>
  <li><strong>Shared resource limits.</strong> Slow queries in the admin app block the API's event loop.</li>
  <li><strong>Routing is a proxy's job.</strong> Nginx, Caddy, Traefik, ALB, and CloudFront all do host-based routing natively with better performance and observability.</li>
  <li><strong>Deployments are easier when services are separate.</strong> Deploy the admin panel without redeploying the public API.</li>
</ul>
<p>Reach for <code>vhost</code> for prototypes, monolith refactors, and small-scale multi-tenant apps. For anything production-grade, let a reverse proxy handle host-based routing.</p>
'''

ANSWERS[85] = r'''
<p><strong>Content negotiation</strong> is the HTTP mechanism where the client says "I prefer JSON" (via <code>Accept</code>) or "I prefer German" (<code>Accept-Language</code>), and the server picks the best match. Express exposes it via <code>res.format()</code> and the lower-level <code>req.accepts()</code>.</p>
<pre><code>import express from "express";
const app = express();

// same URL, different representations — chosen from the Accept header
app.get("/users/:id", (req, res) =&gt; {
  const user = { id: req.params.id, name: "Ada Lovelace" };

  res.format({
    "application/json": () =&gt; res.json(user),
    "text/html":        () =&gt; res.send(`&lt;h1&gt;${user.name}&lt;/h1&gt;`),
    "text/csv":         () =&gt; {
      res.type("text/csv");
      res.send(`id,name\n${user.id},${user.name}`);
    },
    default:            () =&gt; res.status(406).send("Not Acceptable"),
  });
});

// language negotiation
app.get("/greeting", (req, res) =&gt; {
  const lang = req.acceptsLanguages(["en", "de", "es"]) || "en";
  const msgs = { en: "Hello", de: "Hallo", es: "Hola" };
  res.json({ message: msgs[lang], language: lang });
});

// manual inspection
app.get("/check", (req, res) =&gt; {
  console.log(req.accepts("html"));         // "html" | false
  console.log(req.accepts(["json","xml"])); // first match or false
  console.log(req.acceptsCharsets("utf-8"));
  console.log(req.acceptsEncodings("gzip")); // gzip/br handled by compression middleware
  res.json({ ok: true });
});

app.listen(3000);</code></pre>
<p><strong>Other dimensions you can negotiate:</strong></p>
<table>
  <tr><th>Header</th><th>Helper</th><th>Picks</th></tr>
  <tr><td><code>Accept</code></td><td><code>req.accepts()</code></td><td>MIME type (JSON, HTML, CSV, XML)</td></tr>
  <tr><td><code>Accept-Language</code></td><td><code>req.acceptsLanguages()</code></td><td>Locale (en, de, es)</td></tr>
  <tr><td><code>Accept-Encoding</code></td><td><code>req.acceptsEncodings()</code></td><td>Compression (gzip, br, deflate)</td></tr>
  <tr><td><code>Accept-Charset</code></td><td><code>req.acceptsCharsets()</code></td><td>utf-8, iso-8859-1</td></tr>
</table>
<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Set <code>Vary</code>.</strong> When you vary by <code>Accept</code>, add <code>Vary: Accept</code> so caches store separate entries per format. Express sets this automatically for <code>res.format()</code>.</li>
  <li><strong>Return 406</strong> when no representation fits rather than silently picking a format the client didn't ask for.</li>
  <li><strong>URL-based negotiation is often clearer.</strong> Exposing <code>/users/42.json</code> and <code>/users/42.html</code> makes the choice explicit and cache-friendly.</li>
  <li><strong>For language</strong>, pair <code>Accept-Language</code> with an explicit <code>?lang=</code> or subdomain &mdash; let users override browser defaults.</li>
</ul>
'''

ANSWERS[86] = r'''
<p><strong>OPTIONS</strong> is the "can I do this?" HTTP method. Browsers send it as a <strong>CORS preflight</strong> before cross-origin non-simple requests (anything with custom headers, <code>Content-Type: application/json</code>, or methods beyond GET/HEAD/POST). The server's OPTIONS response tells the browser whether to proceed.</p>
<pre><code>import express from "express";
import cors from "cors";

const app = express();

// 1. easy path — use the cors middleware (handles OPTIONS automatically)
app.use(cors({
  origin: ["https://app.example.com"],
  methods: ["GET","POST","PUT","DELETE"],
  allowedHeaders: ["Content-Type","Authorization"],
  credentials: true,
}));
// Browsers preflighting POST /api/users get a valid 204 back automatically.

// 2. manual — explicit OPTIONS handler
app.options("/custom", (req, res) =&gt; {
  res
    .setHeader("Access-Control-Allow-Origin",  "https://app.example.com")
    .setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    .setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization")
    .setHeader("Access-Control-Max-Age",       "86400")              // cache preflight 24h
    .sendStatus(204);
});

// 3. catch-all — handle OPTIONS for every route
app.options("*", cors());

// 4. reply with the methods you support
app.use((req, res, next) =&gt; {
  if (req.method === "OPTIONS") {
    res.setHeader("Allow", "GET,POST,DELETE,OPTIONS");
    return res.sendStatus(204);
  }
  next();
});

app.listen(3000);</code></pre>
<p><strong>Why preflight exists:</strong> it protects servers that predate CORS &mdash; they see a harmless OPTIONS with no body and don't mutate state; only if they advertise permission (via the response headers) does the browser send the real request.</p>
<p><strong>Common issues:</strong></p>
<ul>
  <li><strong>Auth middleware runs before CORS.</strong> If you <code>requireAuth</code> before <code>cors()</code>, the preflight (no Authorization header) returns 401 and the browser aborts. Register <code>cors()</code> before auth, or skip auth for OPTIONS explicitly.</li>
  <li><strong>Wildcard + credentials.</strong> <code>Access-Control-Allow-Origin: *</code> is illegal with <code>credentials: true</code>; echo the request origin from an allowlist instead.</li>
  <li><strong>Preflight on every request.</strong> Set <code>Access-Control-Max-Age</code> (up to 86400 / 24 hours in most browsers) so browsers cache preflights.</li>
  <li><strong>Internal services.</strong> Same-origin APIs never receive CORS preflights; the browser only sends OPTIONS for cross-origin requests.</li>
</ul>
<p>For 99% of Express apps, installing <code>cors</code> and configuring an origin allowlist is the right move &mdash; manual OPTIONS handling is reserved for niche cases like custom CORS logic per route.</p>
'''

ANSWERS[87] = r'''
<p><code>method-override</code> lets clients that can only send GET/POST (classic HTML forms, some older proxies) simulate PUT/PATCH/DELETE. The middleware reads a form field, query param, or custom header and rewrites <code>req.method</code>.</p>
<pre><code>// npm install method-override
import express from "express";
import methodOverride from "method-override";

const app = express();
app.use(express.urlencoded({ extended: true }));

// override from a hidden form field
app.use(methodOverride("_method"));

// or from an HTTP header
app.use(methodOverride("X-HTTP-Method-Override"));

// or by query param
app.use(methodOverride((req) =&gt; req.query._method));

app.delete("/users/:id", (req, res) =&gt; {
  res.send(`Deleted user ${req.params.id}`);
});

app.listen(3000);</code></pre>
<p>HTML form using the override:</p>
<pre><code>&lt;!-- browsers only send GET or POST from forms; method-override fakes DELETE --&gt;
&lt;form method="POST" action="/users/42?_method=DELETE"&gt;
  &lt;button type="submit"&gt;Delete&lt;/button&gt;
&lt;/form&gt;

&lt;!-- or with a hidden field --&gt;
&lt;form method="POST" action="/users/42"&gt;
  &lt;input type="hidden" name="_method" value="DELETE" /&gt;
  &lt;button&gt;Delete&lt;/button&gt;
&lt;/form&gt;</code></pre>
<p><strong>When you need it:</strong></p>
<ul>
  <li><strong>Server-rendered apps</strong> that rely on HTML forms for RESTful actions (Rails-style). Browsers still don't natively send DELETE from forms in 2026.</li>
  <li><strong>Legacy environments</strong> where proxies or firewalls strip non-GET/POST methods.</li>
</ul>
<p><strong>When you don't need it:</strong></p>
<ul>
  <li><strong>Modern SPAs and mobile apps.</strong> JavaScript's <code>fetch()</code> and XHR send any HTTP method directly.</li>
  <li><strong>Pure JSON APIs.</strong> Clients should use the real verb; accepting a fake <code>_method=DELETE</code> widens your attack surface and muddles the contract.</li>
</ul>
<p><strong>Security note:</strong> some middleware (CSRF checks, rate limiters) reads <code>req.method</code> early &mdash; register <code>method-override</code> first so they see the overridden method. Don't accept overrides for methods that weren't in the original request in a way that bypasses auth or rate limits. If you don't need this middleware, don't install it &mdash; it's one fewer thing that can surprise you.</p>
'''

ANSWERS[88] = r'''
<p>Express doesn't have a built-in per-request timeout. You add one with a small middleware that uses <code>req.setTimeout()</code> on the underlying socket, or use the <code>connect-timeout</code> package. Either way, always have a fallback &mdash; a request that hangs indefinitely ties up a connection slot forever.</p>
<pre><code>// Option A — plain Node, no dependency
import express from "express";
const app = express();

function timeoutMiddleware(ms) {
  return (req, res, next) =&gt; {
    req.setTimeout(ms, () =&gt; {
      if (!res.headersSent) {
        res.status(503).json({ error: "Request timed out" });
      } else {
        res.destroy();                        // can't reply cleanly; drop the socket
      }
    });
    next();
  };
}

app.use(timeoutMiddleware(10_000));           // 10s for all routes
app.post("/upload", timeoutMiddleware(120_000), uploadHandler);   // longer for specific routes

// Option B — connect-timeout package
import timeout from "connect-timeout";

app.use(timeout("30s"));
app.use((req, res, next) =&gt; {                 // skip following middleware if timed out
  if (!req.timedout) next();
});

// Option C — AbortController for cancelling async work
app.get("/search", async (req, res) =&gt; {
  const ac = new AbortController();
  const timer = setTimeout(() =&gt; ac.abort(), 5000);
  req.on("close", () =&gt; ac.abort());          // client disconnected
  try {
    const results = await externalSearch({ signal: ac.signal });
    res.json(results);
  } catch (err) {
    if (err.name === "AbortError") res.status(504).json({ error: "Upstream timeout" });
    else                            res.status(500).json({ error: err.message });
  } finally {
    clearTimeout(timer);
  }
});

app.listen(3000);</code></pre>
<p><strong>Key points:</strong></p>
<ul>
  <li><strong>Set timeouts per route class.</strong> A default of 10-30s for JSON APIs; much longer (minutes) for uploads or report generation.</li>
  <li><strong>Client-disconnect detection.</strong> Listen for <code>req.on("close")</code> to cancel downstream work (DB queries, HTTP calls) when the client gives up. Otherwise you burn resources on responses no one will receive.</li>
  <li><strong>Propagate cancellation.</strong> Pass an <code>AbortSignal</code> to <code>fetch()</code> / Prisma / ioredis &mdash; stopping Express from sending the response doesn't stop the DB query finishing expensively.</li>
  <li><strong>Upstream timeouts too.</strong> Nginx (<code>proxy_read_timeout</code>) and ALB have their own timeouts &mdash; the most aggressive wins. Align Express's timeout with theirs.</li>
  <li><strong>Avoid <code>server.setTimeout</code> at the server level</strong> without thought; it resets on <em>any</em> activity and doesn't cover slow handlers. Per-request timeouts are more reliable.</li>
</ul>
'''

ANSWERS[89] = r'''
<p>Regex route parameters constrain what a URL can match. Instead of accepting any value in a named parameter, you can restrict to digits, UUIDs, slugs, etc. Express uses <strong>path-to-regexp</strong> under the hood; the syntax differs a bit between Express 4 and Express 5.</p>
<pre><code>import express from "express";
const app = express();

// --- Express 4 — parameter with parenthesized regex ---
app.get("/orders/:id([0-9]+)", (req, res) =&gt; {
  res.json({ orderId: Number(req.params.id) });   // only matches /orders/123
});

// UUID v4 — very common
const UUID = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
app.get(`/users/:id(${UUID})`, (req, res) =&gt; {
  res.json({ userId: req.params.id });
});

// slug — lowercase, hyphens, digits
app.get("/blog/:slug([a-z0-9-]+)", (req, res) =&gt; {
  res.send(`post: ${req.params.slug}`);
});

// plain RegExp as the path
app.get(/^\/api\/v[12]\/ping$/, (req, res) =&gt; res.send("pong"));
//   matches /api/v1/ping and /api/v2/ping

// --- Express 5 — parenthesized regex is removed from param syntax ---
// Use an explicit RegExp for the whole path, or a param() validator:
app.param("id", (req, res, next, id) =&gt; {
  if (!/^[0-9]+$/.test(id)) return res.sendStatus(404);
  req.params.id = Number(id);
  next();
});
app.get("/orders/:id", (req, res) =&gt; res.json({ id: req.params.id }));

app.listen(3000);</code></pre>
<p><strong>Why not just validate inside the handler?</strong> Both approaches work. Advantages of matching at the route level:</p>
<ul>
  <li><strong>404 vs 400 semantics.</strong> A non-numeric ID returning <em>no matching route</em> (404) is often more accurate than "bad request."</li>
  <li><strong>Routing precedence.</strong> You can have <code>/users/:id([0-9]+)</code> and <code>/users/:username([a-z]+)</code> on the same path and let the regex dispatch to the right handler.</li>
  <li><strong>Central declaration.</strong> The contract "IDs are UUIDs" is visible in the route path.</li>
</ul>
<p><strong>Caveats:</strong></p>
<ul>
  <li><strong>Regex denial-of-service.</strong> A badly-designed pattern with backtracking (<code>(a+)+</code>) can hang the event loop on adversarial input. Keep patterns simple and anchored.</li>
  <li><strong>Express 5 migration.</strong> The inline regex syntax is gone; rely on <code>app.param()</code> or Zod validation in a middleware instead.</li>
  <li><strong>Readability.</strong> Long regexes in URLs hurt readability; keep the complex ones in a validation middleware rather than in the route string.</li>
</ul>
'''

ANSWERS[90] = r'''
<p>A <strong>health check endpoint</strong> is a simple URL the infrastructure hits to ask "is this instance healthy?". Load balancers, Kubernetes, and monitoring systems expect one. The classic pattern is two endpoints: <code>/health</code> (liveness) and <code>/ready</code> (readiness).</p>
<pre><code>import express from "express";
const app = express();

// Liveness — are we alive? Any response means "don't restart me."
app.get("/health", (req, res) =&gt; {
  res.json({ status: "ok", uptime: process.uptime(), pid: process.pid });
});

// Readiness — are we ready to serve traffic? Check dependencies.
app.get("/ready", async (req, res) =&gt; {
  const checks = {};
  try {
    await db.$queryRaw`SELECT 1`;             checks.db    = "ok";
    await redis.ping();                       checks.redis = "ok";
    checks.memory = process.memoryUsage().rss &lt; 1.5e9 ? "ok" : "warn";
  } catch (err) {
    return res.status(503).json({ status: "not ready", error: err.message, checks });
  }
  res.json({ status: "ready", checks });
});

// Graceful shutdown signal — flip readiness off so the LB drains connections
let isShuttingDown = false;
process.on("SIGTERM", () =&gt; { isShuttingDown = true; });
app.get("/ready", (req, res, next) =&gt; {
  if (isShuttingDown) return res.status(503).json({ status: "shutting down" });
  next();
});

app.listen(3000);</code></pre>
<p><strong>Liveness vs Readiness &mdash; the crucial distinction:</strong></p>
<table>
  <tr><th>Liveness</th><th>Readiness</th></tr>
  <tr><td>"Am I alive?"</td><td>"Should traffic come to me?"</td></tr>
  <tr><td>Failing &rarr; Kubernetes restarts the pod</td><td>Failing &rarr; Kubernetes routes traffic elsewhere</td></tr>
  <tr><td>Cheap, no dependencies</td><td>Checks DB, Redis, migrations, warm cache</td></tr>
  <tr><td>Should almost always return 200</td><td>503 is expected during startup and shutdown</td></tr>
</table>
<p><strong>Common mistakes:</strong></p>
<ul>
  <li><strong>Mixing liveness and readiness.</strong> If your liveness check pings the DB and the DB goes down, Kubernetes restarts every pod simultaneously &mdash; amplifying the outage. Keep liveness simple.</li>
  <li><strong>Expensive checks.</strong> A health endpoint called every 5 seconds that runs 10 DB queries <em>is</em> the problem.</li>
  <li><strong>Not failing readiness during deploys.</strong> Let the instance finish warming caches / migrations before receiving traffic.</li>
  <li><strong>Exposing internals publicly.</strong> <code>/health</code> should not reveal version numbers, queue depths, or user counts to the internet. Expose detailed diagnostics on a separate port bound to the internal network.</li>
</ul>
<p>Include a <code>GET /version</code> endpoint with the build SHA and release name &mdash; critical for diagnosing "which version is in prod?" incidents.</p>
'''

ANSWERS[91] = r'''
<p><code>res.append()</code> adds a value to a response header without replacing existing values. It's different from <code>res.setHeader()</code> (which overwrites) &mdash; <code>append()</code> is the right choice for headers that legitimately have multiple values, like <code>Set-Cookie</code>, <code>Link</code>, or <code>Vary</code>.</p>
<pre><code>import express from "express";
const app = express();

// setting multiple Set-Cookie headers (most common use)
app.get("/login", (req, res) =&gt; {
  res.append("Set-Cookie", "session=abc123; HttpOnly; Secure");
  res.append("Set-Cookie", "csrf=def456;   HttpOnly; Secure");
  res.append("Set-Cookie", "lang=en;       Max-Age=31536000");
  res.send("logged in");
});

// multiple Link headers for HTTP/2 Server Push / preload hints
app.get("/page", (req, res) =&gt; {
  res.append("Link", "&lt;/css/app.css&gt;;  rel=preload; as=style");
  res.append("Link", "&lt;/js/app.js&gt;;    rel=preload; as=script");
  res.append("Link", "&lt;/fonts/a.woff2&gt;; rel=preload; as=font; crossorigin");
  res.render("page");
});

// Vary — tell caches which request headers affect the response
app.get("/content", (req, res) =&gt; {
  res.append("Vary", "Accept-Language");
  res.append("Vary", "Accept-Encoding");
  res.json({ message: "Hallo" });
});

// passing an array works too
res.append("X-Debug-Stage", ["validated", "authorized", "rendered"]);

app.listen(3000);</code></pre>
<p><strong><code>append</code> vs <code>set</code> vs <code>header</code>:</strong></p>
<table>
  <tr><th>Method</th><th>Behavior</th><th>When to use</th></tr>
  <tr><td><code>res.setHeader(name, val)</code></td><td>Overwrites any existing value</td><td>Single-value headers: <code>Content-Type</code>, <code>Location</code></td></tr>
  <tr><td><code>res.set(name, val)</code></td><td>Express alias for <code>setHeader</code>; also accepts an object</td><td>Same as <code>setHeader</code></td></tr>
  <tr><td><code>res.header(...)</code></td><td>Alias for <code>res.set()</code></td><td>Same as <code>set</code></td></tr>
  <tr><td><code>res.append(name, val)</code></td><td>Adds to existing values (creates array)</td><td>Multi-value: <code>Set-Cookie</code>, <code>Link</code>, <code>Vary</code>, <code>Cache-Control</code></td></tr>
</table>
<p><strong>Common mistake:</strong> calling <code>res.setHeader("Set-Cookie", "a=1")</code> then <code>res.setHeader("Set-Cookie", "b=2")</code> &mdash; the second call overwrites the first and only one cookie is sent. Use <code>res.append()</code> (or better, <code>res.cookie()</code>) for each cookie. As with all header methods, <code>res.append()</code> must be called <em>before</em> the response body starts streaming or you'll get "Cannot set headers after they are sent."</p>
'''

ANSWERS[92] = r'''
<p>To force a file to download with a specific filename, you send a <code>Content-Disposition: attachment; filename="..."</code> header. Express wraps this in the <code>res.download()</code> method &mdash; the easiest and safest way. You can also call <code>res.attachment()</code> + stream manually for more control.</p>
<pre><code>import express from "express";
import path from "node:path";

const app = express();

// 1. simplest — res.download(path, filename)
app.get("/export/:id", (req, res) =&gt; {
  const filePath = path.resolve("./storage", `report-${req.params.id}.pdf`);
  res.download(filePath, `Report_${req.params.id}.pdf`, (err) =&gt; {
    if (err &amp;&amp; !res.headersSent) res.status(404).send("File not found");
  });
});

// 2. res.attachment() + stream — when data comes from DB/S3/generated
app.get("/invoices/:id.pdf", async (req, res, next) =&gt; {
  try {
    const pdfStream = await renderInvoicePdf(req.params.id);
    res.attachment(`Invoice_${req.params.id}.pdf`);   // sets Content-Disposition + type
    res.setHeader("Content-Type", "application/pdf");
    pdfStream.pipe(res);
  } catch (err) { next(err); }
});

// 3. filename with special characters — use RFC 5987 encoding
app.get("/multi-lang-download", (req, res) =&gt; {
  const filename = "résumé — 2026.pdf";
  res.setHeader(
    "Content-Disposition",
    `attachment; filename="resume_2026.pdf"; ` +
    `filename*=UTF-8''${encodeURIComponent(filename)}`
  );
  res.setHeader("Content-Type", "application/pdf");
  res.sendFile(path.resolve("./files/resume.pdf"));
});

app.listen(3000);</code></pre>
<p><strong>How the client decides the filename:</strong></p>
<ul>
  <li><strong><code>Content-Disposition: attachment; filename="..."</code></strong> &rarr; browsers prompt Save-As with that filename.</li>
  <li><strong>Just <code>attachment</code></strong> without a filename &rarr; browsers invent one based on the URL.</li>
  <li><strong><code>inline</code></strong> (the default) &rarr; the browser renders the file if it can (PDF, images, text) or downloads it with its URL-based name.</li>
</ul>
<p><strong>Security pitfalls:</strong></p>
<ul>
  <li><strong>Never splice user input into <code>filename=</code>.</strong> A filename like <code>"; filename="evil.exe</code> breaks out of quotes and can trick some browsers. Strip quotes, semicolons, and newlines before interpolating.</li>
  <li><strong>Path traversal.</strong> If the filename comes from <code>req.params</code>, resolve it relative to a base directory and verify the result stays inside: <code>path.resolve(base, name).startsWith(base + path.sep)</code>.</li>
  <li><strong>Unicode filenames.</strong> Older browsers need the RFC 5987 <code>filename*=UTF-8''...</code> form; always provide an ASCII-safe fallback too.</li>
</ul>
'''

ANSWERS[93] = r'''
<p><code>res.format()</code> implements <strong>content negotiation</strong>: the same endpoint can return JSON, HTML, CSV, XML &mdash; whichever the client's <code>Accept</code> header asks for. Express picks the best match from the object you supply and calls that handler.</p>
<pre><code>import express from "express";
const app = express();

app.get("/users/:id", (req, res) =&gt; {
  const user = { id: req.params.id, name: "Ada Lovelace", year: 1815 };

  res.format({
    // browsers sending "Accept: text/html, ..."
    "text/html": () =&gt; {
      res.send(`&lt;!doctype html&gt;&lt;h1&gt;${user.name}&lt;/h1&gt;&lt;p&gt;born ${user.year}&lt;/p&gt;`);
    },

    // typical API clients
    "application/json": () =&gt; res.json(user),

    // old-school clients that still want XML
    "application/xml": () =&gt; {
      res.type("application/xml");
      res.send(`&lt;user id="${user.id}"&gt;&lt;name&gt;${user.name}&lt;/name&gt;&lt;/user&gt;`);
    },

    // spreadsheet exports
    "text/csv": () =&gt; {
      res.type("text/csv");
      res.send(`id,name,year\n${user.id},${user.name},${user.year}`);
    },

    // nothing matched — fall through
    default: () =&gt; res.status(406).send("Not Acceptable"),
  });
});

// shortcut syntax — strings instead of full MIME
app.get("/ping", (req, res) =&gt; {
  res.format({
    text: () =&gt; res.send("pong"),
    html: () =&gt; res.send("&lt;strong&gt;pong&lt;/strong&gt;"),
    json: () =&gt; res.json({ message: "pong" }),
  });
});

app.listen(3000);</code></pre>
<p><strong>What Express does for you:</strong></p>
<ul>
  <li><strong>Parses the <code>Accept</code> header</strong>, respecting <code>q</code> quality factors. Given <code>Accept: text/html; q=0.9, application/json</code>, the JSON handler wins (no <code>q</code> defaults to 1.0).</li>
  <li><strong>Adds <code>Vary: Accept</code></strong> automatically &mdash; critical for caches (CDN, reverse proxy) to store separate responses per format.</li>
  <li><strong>Calls <code>default</code>, or sends 406 Not Acceptable</strong>, if no handler matches.</li>
</ul>
<p><strong>When it's useful:</strong></p>
<ul>
  <li><strong>Hybrid apps</strong> &mdash; one endpoint serves both a browser (HTML page) and a mobile app (JSON).</li>
  <li><strong>Error middleware</strong> &mdash; render an HTML error page for browsers but JSON for fetch clients.</li>
  <li><strong>Data export</strong> &mdash; the same URL returns CSV or JSON based on the request.</li>
</ul>
<p><strong>When to skip it:</strong> pure JSON APIs (just call <code>res.json()</code>) and URL-based versioning (<code>/data.json</code> vs <code>/data.csv</code> is clearer and cache-friendlier than header negotiation).</p>
'''

ANSWERS[94] = r'''
<p>A custom logger is a middleware that captures interesting request/response data &mdash; method, URL, status, duration, user id, request id &mdash; and writes it to a destination (stdout, a file, an aggregator like Datadog). Use a library like <strong>pino</strong> or <strong>morgan</strong> unless you have very specific needs; rolling your own is rarely worth it.</p>
<pre><code>// Option A — minimal, hand-rolled
import express from "express";
import crypto from "node:crypto";

const app = express();

app.use((req, res, next) =&gt; {
  const requestId = req.headers["x-request-id"] || crypto.randomUUID();
  const start = process.hrtime.bigint();

  res.setHeader("X-Request-Id", requestId);

  res.on("finish", () =&gt; {
    const durMs = Number(process.hrtime.bigint() - start) / 1e6;
    console.log(JSON.stringify({
      time:   new Date().toISOString(),
      level:  res.statusCode &gt;= 500 ? "error" : res.statusCode &gt;= 400 ? "warn" : "info",
      reqId:  requestId,
      method: req.method,
      url:    req.originalUrl,
      status: res.statusCode,
      durMs:  Number(durMs.toFixed(1)),
      ua:     req.headers["user-agent"],
      ip:     req.ip,
      userId: req.user?.id,
    }));
  });

  next();
});</code></pre>
<pre><code>// Option B — pino-http (recommended: fast, structured, battle-tested)
// npm install pino pino-http
import pinoHttp from "pino-http";
import pino from "pino";

const logger = pino({
  level:     process.env.LOG_LEVEL || "info",
  redact:    ["req.headers.authorization", "req.headers.cookie"],
  timestamp: pino.stdTimeFunctions.isoTime,
});

app.use(pinoHttp({
  logger,
  customLogLevel: (req, res, err) =&gt; {
    if (err || res.statusCode &gt;= 500) return "error";
    if (res.statusCode &gt;= 400)        return "warn";
    return "info";
  },
  customProps: (req) =&gt; ({ userId: req.user?.id }),
}));

app.get("/work", (req, res) =&gt; {
  req.log.info({ step: "work-started" }, "processing");
  res.json({ ok: true });
});</code></pre>
<p><strong>Essentials of good request logging:</strong></p>
<ul>
  <li><strong>Structured (JSON).</strong> Log shippers parse JSON; they choke on prose. One event per request = one line.</li>
  <li><strong>Request id on every log.</strong> Accept <code>X-Request-Id</code> from upstream or generate a UUID; thread it through handlers (<code>AsyncLocalStorage</code>) so downstream logs inherit it.</li>
  <li><strong>Redact secrets.</strong> Authorization headers, cookies, request bodies with passwords &mdash; pino's <code>redact</code> handles this declaratively.</li>
  <li><strong>Don't log PII</strong> (emails, IPs in full) unless you need it &mdash; GDPR implications.</li>
  <li><strong>Log timing.</strong> <code>hrtime</code> is monotonic; <code>Date.now()</code> can go backwards on NTP sync.</li>
  <li><strong>Don't console.log in hot paths.</strong> It's synchronous and slow; pino is async and fast.</li>
</ul>
'''

ANSWERS[95] = r'''
<p><strong>Dynamic routes</strong> use named URL parameters (or wildcards) so one handler serves many resources. Express parses <code>:name</code> segments and populates <code>req.params</code>.</p>
<pre><code>import express from "express";
const app = express();

// single parameter
app.get("/users/:id", (req, res) =&gt; {
  res.json({ userId: req.params.id });            // /users/42 → "42"
});

// multiple parameters
app.get("/users/:userId/posts/:postId", (req, res) =&gt; {
  const { userId, postId } = req.params;
  res.json({ userId, postId });
});

// parameter with constraint — digits only
app.get("/orders/:id([0-9]+)", (req, res) =&gt; {
  res.json({ orderId: Number(req.params.id) });   // /orders/abc doesn't match
});

// optional parameter — Express 5 syntax
app.get("/posts/:id{/edit}?", (req, res) =&gt; {     // matches /posts/5 and /posts/5/edit
  res.json(req.params);
});

// wildcard — catch-all trailing segment
app.get("/files/*", (req, res) =&gt; {               // Express 4 syntax
  res.send(`path: ${req.params[0]}`);
});
app.get("/files/*path", (req, res) =&gt; {           // Express 5 syntax — named wildcard
  res.send(`path: ${req.params.path}`);
});

// centralize a param — runs once for every route that uses :id
app.param("id", async (req, res, next, id) =&gt; {
  try {
    req.resource = await db.resource.findUnique({ where: { id } });
    if (!req.resource) return res.sendStatus(404);
    next();
  } catch (err) { next(err); }
});
app.get("/widgets/:id", (req, res) =&gt; res.json(req.resource));

app.listen(3000);</code></pre>
<p><strong>Practical tips:</strong></p>
<ul>
  <li><strong>Always strings.</strong> <code>req.params.id</code> is always a string &mdash; coerce to number/UUID/date explicitly.</li>
  <li><strong>Validate as input.</strong> URL params come from the client; pipe them through Zod or a regex constraint on the route.</li>
  <li><strong>Route ordering matters.</strong> Specific routes before generic: <code>/users/me</code> registered <em>before</em> <code>/users/:id</code>, or the generic route matches <code>me</code> as an id.</li>
  <li><strong>Don't put verbs in the URL.</strong> <code>/users/:id</code> + HTTP methods is RESTful; <code>/getUser/:id</code> is RPC-in-disguise.</li>
  <li><strong>Catch-all routes</strong> should come last in the router (for SPA fallback: <code>app.get("*", serveIndexHtml)</code>).</li>
  <li><strong>Nested routers.</strong> For resources-within-resources, use <code>Router({ mergeParams: true })</code> so the child sees the parent's <code>:userId</code>.</li>
</ul>
'''

ANSWERS[96] = r'''
<p><code>res.set()</code> sets one or more response headers. It's a convenience alias for the Node <code>res.setHeader()</code>, but it can also accept an object to set many headers in one call. Alongside <code>res.header()</code> (same thing, different name), it's the standard way to configure outgoing headers in Express.</p>
<pre><code>import express from "express";
const app = express();

app.get("/api/users", (req, res) =&gt; {
  // single header, two forms — identical
  res.set("Cache-Control", "public, max-age=60");
  res.setHeader("X-API-Version", "2026.04");

  // multiple headers via object — handy for common patterns
  res.set({
    "Content-Type":  "application/json",
    "X-Powered-By":  "MyAPI",
    "X-RateLimit-Remaining": "99",
  });

  res.json([{ id: 1 }]);
});

// CORS response — a burst of related headers
app.get("/api/cors-example", (req, res) =&gt; {
  res.set({
    "Access-Control-Allow-Origin":  "https://app.example.com",
    "Access-Control-Allow-Methods": "GET,POST",
    "Access-Control-Max-Age":       "86400",
    "Vary":                         "Origin",
  });
  res.json({ ok: true });
});

// security headers without helmet
app.use((req, res, next) =&gt; {
  res.set({
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options":    "nosniff",
    "X-Frame-Options":           "DENY",
    "Referrer-Policy":           "strict-origin-when-cross-origin",
  });
  next();
});

app.listen(3000);</code></pre>
<p><strong>Related methods you'll use often:</strong></p>
<table>
  <tr><th>Method</th><th>Behavior</th></tr>
  <tr><td><code>res.set(name, value)</code></td><td>Overwrite a header (or set many via object)</td></tr>
  <tr><td><code>res.get(name)</code></td><td>Read a header you've already set</td></tr>
  <tr><td><code>res.append(name, value)</code></td><td>Add to existing value &mdash; for multi-value headers like <code>Set-Cookie</code></td></tr>
  <tr><td><code>res.removeHeader(name)</code></td><td>Remove a header before the response is sent</td></tr>
  <tr><td><code>res.type(mime)</code></td><td>Sugar for setting <code>Content-Type</code></td></tr>
  <tr><td><code>res.links({...})</code></td><td>Build a <code>Link</code> header from an object of rels &rarr; URLs</td></tr>
  <tr><td><code>res.location(url)</code></td><td>Set the <code>Location</code> header (used with <code>res.redirect</code> too)</td></tr>
</table>
<p><strong>Pitfalls:</strong></p>
<ul>
  <li><strong>After the response starts, headers are frozen.</strong> Set headers before calling <code>res.send()</code>/<code>res.json()</code>/<code>res.end()</code> &mdash; afterward you'll see "Cannot set headers after they are sent."</li>
  <li><strong>Use <code>append</code>, not <code>set</code>, for multi-value headers</strong> (<code>Set-Cookie</code>, <code>Link</code>). Repeated <code>set</code>s overwrite.</li>
  <li><strong>Don't leak framework headers.</strong> Disable <code>X-Powered-By</code> with <code>app.disable("x-powered-by")</code> &mdash; fingerprinting is a small but free info disclosure.</li>
</ul>
'''

ANSWERS[97] = r'''
<p>Async errors are Express's classic footgun. In <strong>Express 4</strong>, an unhandled rejection inside an async handler <em>doesn't</em> reach your error middleware &mdash; the request just hangs. <strong>Express 5</strong> fixed this by auto-forwarding rejected promises. The key skill is writing code that works safely in both.</p>
<pre><code>import express from "express";
const app = express();

// ❌ Express 4 — this HANGS if the DB query rejects
app.get("/bad", async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: "x" } });  // throws?
  res.json(user);
});

// ✅ Option 1: try/catch + next(err) — works in both Express 4 and 5
app.get("/users/:id", async (req, res, next) =&gt; {
  try {
    const user = await db.user.findUnique({ where: { id: req.params.id } });
    if (!user) return res.sendStatus(404);
    res.json(user);
  } catch (err) {
    next(err);
  }
});

// ✅ Option 2: an "asyncHandler" wrapper — removes try/catch boilerplate
const asyncHandler = (fn) =&gt; (req, res, next) =&gt;
  Promise.resolve(fn(req, res, next)).catch(next);

app.get("/products/:id", asyncHandler(async (req, res) =&gt; {
  const p = await db.product.findUnique({ where: { id: req.params.id } });
  if (!p) throw new HttpError("Not found", 404);
  res.json(p);
}));

// ✅ Option 3: Express 5 — native async support, just throw
app.get("/orders/:id", async (req, res) =&gt; {
  const order = await db.order.findUnique({ where: { id: req.params.id } });
  if (!order) throw new HttpError("Not found", 404);     // Express 5 forwards to error mw
  res.json(order);
});

// central error handler
class HttpError extends Error {
  constructor(message, status = 500) { super(message); this.status = status; }
}
app.use((err, req, res, _next) =&gt; {
  console.error(err);
  res.status(err.status || 500).json({ error: err.message });
});

app.listen(3000);</code></pre>
<p><strong>Useful packages:</strong></p>
<ul>
  <li><a href="https://www.npmjs.com/package/express-async-errors"><strong>express-async-errors</strong></a> &mdash; monkey-patches Express 4 so <code>throw</code> in async handlers forwards to error middleware. Import once, never worry again.</li>
  <li><a href="https://www.npmjs.com/package/express-async-handler"><strong>express-async-handler</strong></a> &mdash; the explicit wrapper version of Option 2 above.</li>
</ul>
<p><strong>What this does NOT cover:</strong></p>
<ul>
  <li><strong>Errors <em>after</em> <code>res.send()</code>.</strong> A throw in a <code>res.on("finish")</code> handler won't be caught; log it and move on.</li>
  <li><strong>Unhandled promise rejections outside handlers.</strong> Background jobs, event emitters, timers &mdash; add <code>process.on("unhandledRejection", ...)</code> and <code>process.on("uncaughtException", ...)</code> as last-resort loggers, then crash and let the supervisor restart you.</li>
  <li><strong>Fire-and-forget promises inside handlers.</strong> If you start a promise but don't await it, rejections escape Express entirely. Always <code>await</code> or chain <code>.catch()</code>.</li>
</ul>
'''

ANSWERS[98] = r'''
<p>A <strong>catch-all error handler</strong> is a 4-argument middleware (<code>(err, req, res, next)</code>) registered <em>after</em> all routes. Express recognizes error middleware by the four-parameter signature and routes errors to it via <code>next(err)</code> or (in Express 5) thrown exceptions inside async handlers.</p>
<pre><code>import express from "express";
const app = express();
app.use(express.json());

// a typed error class carries an HTTP status
class HttpError extends Error {
  constructor(message, status = 500, code) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

// ---- routes ----
app.get("/users/:id", async (req, res, next) =&gt; {
  try {
    const user = await db.user.findUnique({ where: { id: req.params.id } });
    if (!user) throw new HttpError("User not found", 404, "USER_NOT_FOUND");
    res.json(user);
  } catch (err) { next(err); }
});

// ---- 404 for unmatched routes (not an "error" — just a missing route) ----
app.use((req, res, next) =&gt; {
  next(new HttpError(`Route ${req.method} ${req.originalUrl} not found`, 404, "NOT_FOUND"));
});

// ---- catch-all error middleware — MUST be last, MUST have 4 args ----
app.use((err, req, res, _next) =&gt; {
  // 1. log with context
  req.log?.error({ err, reqId: req.id }, err.message) ?? console.error(err);

  // 2. normalize errors from known libraries into HttpErrors
  if (err.name === "ZodError")
    err = new HttpError("Invalid input", 400, "VALIDATION_FAILED");
  if (err.code === "P2002")                // Prisma unique-constraint
    err = new HttpError("Already exists", 409, "CONFLICT");

  // 3. don't leak internals in production
  const status  = err.status || 500;
  const payload = {
    error: status &gt;= 500 ? "Internal Server Error" : err.message,
    code:  err.code,
    reqId: req.id,
    ...(process.env.NODE_ENV !== "production" &amp;&amp; { stack: err.stack }),
  };

  if (!res.headersSent) res.status(status).json(payload);
});

app.listen(3000);</code></pre>
<p><strong>Principles of a good central error handler:</strong></p>
<ul>
  <li><strong>Log everything with context.</strong> Request id, user id, URL &mdash; so logs are searchable during an incident.</li>
  <li><strong>Normalize errors.</strong> Map library-specific errors (Zod, Prisma, jsonwebtoken) to your own <code>HttpError</code> class in one place; route handlers stay simple.</li>
  <li><strong>Hide stack traces in production.</strong> Return generic messages for 5xx; keep 4xx messages safe to show users.</li>
  <li><strong>Respect content type.</strong> If the client asked for HTML, render an error page; for JSON, return JSON. Use <code>res.format()</code>.</li>
  <li><strong>Check <code>headersSent</code>.</strong> If the response has already started streaming, you can't change the status &mdash; just close the socket (<code>res.destroy()</code>) and log.</li>
  <li><strong>Include a request id</strong> in the response &mdash; users copy-paste it into support tickets, making incidents easy to trace.</li>
</ul>
<p>Some codebases extract all this into a separate module (<code>middleware/errorHandler.ts</code>), import it at the bottom of <code>app.js</code>, and test it in isolation. That's the right organization once your app grows past a single file.</p>
'''

ANSWERS[99] = r'''
<p><code>app.route(path)</code> returns a route object you can chain methods on &mdash; it's a cleaner way to define several HTTP verbs for the same URL without repeating the path string. Purely a readability win; the underlying behavior is identical to registering each method separately.</p>
<pre><code>import express from "express";
const app = express();
app.use(express.json());

// chained definition — one path, many verbs
app.route("/users/:id")
  .get(async (req, res, next) =&gt; {
    try {
      const user = await db.user.findUnique({ where: { id: req.params.id } });
      if (!user) return res.sendStatus(404);
      res.json(user);
    } catch (err) { next(err); }
  })
  .put(async (req, res, next) =&gt; {
    try {
      const user = await db.user.update({
        where: { id: req.params.id },
        data:  req.body,
      });
      res.json(user);
    } catch (err) { next(err); }
  })
  .patch(async (req, res, next) =&gt; {
    try {
      const user = await db.user.update({
        where: { id: req.params.id },
        data:  req.body,
      });
      res.json(user);
    } catch (err) { next(err); }
  })
  .delete(async (req, res, next) =&gt; {
    try {
      await db.user.delete({ where: { id: req.params.id } });
      res.sendStatus(204);
    } catch (err) { next(err); }
  });

// equivalent without app.route()
// app.get   ("/users/:id", getHandler);
// app.put   ("/users/:id", putHandler);
// app.patch ("/users/:id", patchHandler);
// app.delete("/users/:id", deleteHandler);

app.listen(3000);</code></pre>
<p><strong>Why use <code>app.route()</code>:</strong></p>
<ul>
  <li><strong>Less repetition.</strong> The path string appears once. Typos and refactors affect one place.</li>
  <li><strong>Grouped by resource.</strong> Related verbs live together visually &mdash; easy to see all operations on <code>/users/:id</code>.</li>
  <li><strong>Works with middleware too:</strong>
<pre><code>app.route("/admin/:id")
  .all(requireAdmin)                    // runs before every verb on this route
  .get(adminGet)
  .post(adminCreate);</code></pre>
  </li>
</ul>
<p><strong>Same thing exists on routers:</strong></p>
<pre><code>import { Router } from "express";
const router = Router();

router.route("/")
  .get(listUsers)
  .post(createUser);

router.route("/:id")
  .get(getUser)
  .put(updateUser)
  .delete(deleteUser);

app.use("/api/users", router);</code></pre>
<p><strong>When NOT to use it:</strong> routes with very different concerns (different middleware, different auth per method) often read better as separate <code>app.get</code>/<code>app.post</code> calls. Consistency within a file matters more than the chaining style itself.</p>
'''

ANSWERS[100] = r'''
<p><strong>Content-Type negotiation</strong> has two sides:</p>
<ul>
  <li><strong>Request side</strong> &mdash; what the client is <em>sending</em>. Express uses <code>req.is()</code> and <code>req.get("Content-Type")</code>; the right body parser is picked by <code>Content-Type</code>.</li>
  <li><strong>Response side</strong> &mdash; what the client wants <em>back</em>. Express uses <code>res.format()</code>, <code>req.accepts()</code>, and <code>res.type()</code> to choose and signal the representation you're sending.</li>
</ul>
<pre><code>import express from "express";
const app = express();

// body parsers matched by Content-Type
app.use(express.json());                              // application/json
app.use(express.urlencoded({ extended: false }));     // application/x-www-form-urlencoded
// multer handles multipart/form-data (not shown)

app.post("/ingest", (req, res) =&gt; {
  // what did the client send?
  if (req.is("application/json")) {
    console.log("JSON payload:", req.body);
  } else if (req.is("urlencoded")) {                   // shorthand for x-www-form-urlencoded
    console.log("Form payload:", req.body);
  } else if (req.is("text/*")) {
    console.log("Text:", req.body);                    // requires express.text()
  } else {
    return res.status(415).send("Unsupported Media Type");
  }
  res.json({ received: true });
});

// choose the response format based on what the client accepts
app.get("/stats", (req, res) =&gt; {
  const data = { users: 42, uptime: process.uptime() };

  res.format({
    "application/json": () =&gt; res.json(data),
    "text/html":        () =&gt; res.send(`&lt;pre&gt;${JSON.stringify(data, null, 2)}&lt;/pre&gt;`),
    "text/csv":         () =&gt; {
      res.type("text/csv");
      res.send("metric,value\n" + Object.entries(data).map(([k,v]) =&gt; `${k},${v}`).join("\n"));
    },
    default:            () =&gt; res.status(406).send("Not Acceptable"),
  });
});

// explicit response type without negotiation
app.get("/robots.txt", (req, res) =&gt; {
  res.type("text/plain").send("User-agent: *\nDisallow: /admin");
});

app.listen(3000);</code></pre>
<p><strong>Key helpers:</strong></p>
<table>
  <tr><th>Method</th><th>Purpose</th></tr>
  <tr><td><code>req.is(type)</code></td><td>Does the request's <code>Content-Type</code> match? Returns the type or <code>false</code>.</td></tr>
  <tr><td><code>req.accepts(types)</code></td><td>What representation does the client want? Returns the best match or <code>false</code>.</td></tr>
  <tr><td><code>res.type(mime)</code></td><td>Set response <code>Content-Type</code>. Accepts extensions (<code>"json"</code>, <code>"html"</code>) or full MIME.</td></tr>
  <tr><td><code>res.format({...})</code></td><td>Dispatch on <code>Accept</code>; Express adds <code>Vary: Accept</code>.</td></tr>
</table>
<p><strong>Rules to live by:</strong></p>
<ul>
  <li><strong>Return 415 Unsupported Media Type</strong> when the request's <code>Content-Type</code> isn't one you support.</li>
  <li><strong>Return 406 Not Acceptable</strong> when <code>res.format()</code> has no matching handler.</li>
  <li><strong>Always set charset for text.</strong> <code>res.type("text/html; charset=utf-8")</code> &mdash; browsers misinterpret UTF-8 otherwise.</li>
  <li><strong>Include <code>Vary: Accept</code></strong> on negotiated responses so shared caches don't serve the wrong format. <code>res.format()</code> does this automatically.</li>
</ul>
'''
