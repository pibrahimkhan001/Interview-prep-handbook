"""Detailed answers for Infrastructure MERN Stack Basic interview questions.

Style: ~80-150 words concise prose with one focused code snippet, ~1,400-1,800 chars.
Operations and tooling angle &mdash; how MERN apps are built, deployed, and run.
2026-current ecosystem: Vite, pnpm/Bun, Vercel/Fly.io/Railway/Render, Atlas, Docker, K8s.
"""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''<p>The <strong>MERN stack</strong> is a JavaScript&ndash;everywhere full&ndash;stack &mdash; one language from database access through server logic to the browser UI. The four components:</p>

<ul>
<li><strong>M &mdash; MongoDB</strong>: a document database storing flexible JSON&ndash;like records (BSON under the hood). Almost always run as managed MongoDB Atlas in production.</li>
<li><strong>E &mdash; Express.js</strong>: a small, unopinionated HTTP framework for Node.js. Modern alternatives like <strong>Hono</strong> and <strong>Fastify</strong> are gaining ground but Express still dominates legacy.</li>
<li><strong>R &mdash; React</strong>: the component&ndash;based UI library. In 2026 most new projects pair React with <strong>Next.js 15</strong> (or Remix / TanStack Start) rather than a bare SPA.</li>
<li><strong>N &mdash; Node.js</strong>: the JavaScript runtime on the server. <strong>Bun</strong> and <strong>Deno</strong> are credible alternatives but Node remains the default for MERN.</li>
</ul>

<p>From an infrastructure angle, MERN is appealing because every layer ships as plain text (JS/JSON), all four pieces have first&ndash;class managed offerings (Atlas, Vercel, Fly.io, Railway, Render), and a single team can own the full request path without context&ndash;switching between languages.</p>'''


ANSWERS[2] = r'''<p>A modern MERN local setup needs four moving pieces installed once, then a project repo on top.</p>

<pre><code># 1. Node.js (LTS) via the official installer or a version manager
nvm install --lts            # or: fnm install --lts
node --version               # v22.x or newer in 2026

# 2. A package manager &mdash; pnpm or Bun is the 2026 default
npm install -g pnpm          # or: curl -fsSL https://bun.sh/install | bash

# 3. MongoDB &mdash; either local or Atlas free tier
brew install mongodb-community     # macOS
# or sign up at mongodb.com/atlas and grab a free M0 cluster

# 4. Editor + extensions
# VS Code or Cursor with: ESLint, Prettier, MongoDB for VS Code, Tailwind</code></pre>

<p>Then scaffold the repo: a <strong>monorepo</strong> with <code>apps/web</code> (Vite + React or Next.js) and <code>apps/api</code> (Express/Hono) is the 2026 norm. Tools like <strong>Turborepo</strong> or <strong>pnpm workspaces</strong> handle the orchestration. Add <code>.env</code> for local secrets, a <code>docker-compose.yml</code> if you want Mongo + Redis containerized, and you&rsquo;re running with <code>pnpm dev</code> end&ndash;to&ndash;end.</p>

<p>Avoid Create React App &mdash; it&rsquo;s officially deprecated. Use <strong>Vite</strong> for SPAs or <strong>Next.js</strong> for SSR.</p>'''


ANSWERS[3] = r'''<p>In 2026 don&rsquo;t install Node from the OS package manager &mdash; use a version manager so you can switch between Node versions per project.</p>

<pre><code># macOS / Linux &mdash; nvm or fnm (fnm is faster, written in Rust)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install --lts            # currently Node 22 LTS
nvm use --lts
nvm alias default lts/*

# Windows &mdash; nvm-windows or fnm
fnm install --lts
fnm use lts-latest

# Verify
node --version               # v22.x.x
npm --version                # 10.x.x (ships with Node)</code></pre>

<p><strong>npm</strong> ships with Node, so installing Node automatically gives you npm. Many teams then upgrade to <strong>pnpm</strong> (faster, disk&ndash;efficient via content&ndash;addressed store) or <strong>Bun</strong> (extremely fast, includes a runtime + bundler + test runner).</p>

<p>Pin the Node version in your repo with a <code>.nvmrc</code> or <code>.node-version</code> file containing just <code>22</code> &mdash; CI tools and version managers read this and switch automatically. For Windows, install via <strong>winget</strong> (<code>winget install OpenJS.NodeJS.LTS</code>) or <strong>fnm</strong>; avoid the bundled Chocolatey package which lags releases.</p>'''


ANSWERS[4] = r'''<p>A new Node project starts with <code>npm init</code> (or <code>pnpm init</code> / <code>bun init</code>), which creates the <code>package.json</code> manifest.</p>

<pre><code>mkdir my-api &amp;&amp; cd my-api
pnpm init                   # interactive: name, version, license, etc.
                            # or: pnpm init -y for defaults

# Install runtime deps
pnpm add express mongoose zod dotenv

# Install dev deps (testing, types, linting)
pnpm add -D typescript tsx vitest @types/node @types/express
pnpm add -D eslint prettier

# Initialize TS
pnpm tsc --init</code></pre>

<p>This produces <code>package.json</code> (manifest), <code>node_modules/</code> (installed packages), and a <strong>lockfile</strong> &mdash; <code>pnpm-lock.yaml</code>, <code>package-lock.json</code>, or <code>bun.lockb</code> &mdash; which pins exact versions so every machine + CI installs the same tree. Always commit the lockfile.</p>

<p>Add useful scripts to <code>package.json</code>:</p>

<pre><code>&quot;scripts&quot;: {
  &quot;dev&quot;: &quot;tsx watch src/index.ts&quot;,
  &quot;build&quot;: &quot;tsc&quot;,
  &quot;start&quot;: &quot;node dist/index.js&quot;,
  &quot;test&quot;: &quot;vitest&quot;,
  &quot;lint&quot;: &quot;eslint .&quot;
}</code></pre>

<p>Use <code>&quot;type&quot;: &quot;module&quot;</code> in <code>package.json</code> to write modern ESM <code>import</code>/<code>export</code> syntax instead of CommonJS <code>require</code>.</p>'''


ANSWERS[5] = r'''<p>Express installs from npm like any other package and is wired up in three lines.</p>

<pre><code>pnpm add express
pnpm add -D @types/express   # if using TypeScript</code></pre>

<pre><code>// src/index.ts
import express from &quot;express&quot;;

const app = express();
app.use(express.json());                    // parse JSON request bodies

app.get(&quot;/health&quot;, (req, res) =&gt; {
  res.json({ ok: true, ts: new Date() });
});

const PORT = process.env.PORT ?? 4000;
app.listen(PORT, () =&gt; console.log(`API on :${PORT}`));</code></pre>

<p>Run with <code>pnpm dev</code> (using <strong>tsx watch</strong> or <strong>nodemon</strong> for hot reload) and hit <code>http://localhost:4000/health</code> to confirm.</p>

<p>In 2026 many teams ship new APIs with <strong>Hono</strong> instead &mdash; faster, smaller, and works on any runtime (Node, Bun, Deno, Cloudflare Workers, Vercel Edge). The Express API is largely unchanged from 2014 and is missing modern features like async error handling without middleware, Web Standard Request/Response, and edge deployment. Both Express and Hono are valid; Express remains the default in MERN tutorials and legacy code, Hono is what greenfield 2026 projects pick.</p>'''


ANSWERS[6] = r'''<p><strong>MongoDB</strong> is a document database that stores data as JSON&ndash;like documents (BSON: Binary JSON) inside collections, which sit inside databases. There&rsquo;s no rigid table schema &mdash; documents in the same collection can have different shapes, though Mongoose enforces a schema in your application code.</p>

<p>You almost never run MongoDB on a developer laptop in 2026 &mdash; just use the free <strong>Atlas</strong> M0 cluster. But if you really need it locally:</p>

<pre><code># macOS &mdash; Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Linux &mdash; official .deb / .rpm
# https://www.mongodb.com/docs/manual/installation/

# Windows &mdash; .msi installer from mongodb.com/try/download/community
# or run the official Docker image
docker run -d --name mongo -p 27017:27017 mongo:7</code></pre>

<p>Verify with <code>mongosh</code>: <code>mongosh &quot;mongodb://localhost:27017&quot;</code> opens an interactive shell where you can run <code>show dbs</code>, <code>use myapp</code>, <code>db.users.insertOne({ name: &quot;Ada&quot; })</code>, etc.</p>

<p>For GUI inspection use <strong>MongoDB Compass</strong> (official) or the <strong>MongoDB for VS Code</strong> extension &mdash; both connect to local Mongo or Atlas with a connection string.</p>'''


ANSWERS[7] = r'''<p>How you start and stop Mongo depends on how you installed it.</p>

<pre><code># macOS Homebrew &mdash; managed as a brew service
brew services start mongodb-community@7.0
brew services stop mongodb-community@7.0
brew services list                       # shows status

# Linux (systemd)
sudo systemctl start mongod
sudo systemctl stop mongod
sudo systemctl status mongod
sudo systemctl enable mongod             # auto-start at boot

# Windows
# MongoDB ships as a Windows service named &quot;MongoDB&quot;
net start MongoDB
net stop MongoDB
# or use services.msc

# Docker (recommended for dev)
docker start mongo
docker stop mongo
docker logs -f mongo                     # follow logs</code></pre>

<p>Once started, <code>mongod</code> listens on <code>localhost:27017</code> by default. Connect from another terminal with <code>mongosh</code> to verify.</p>

<p>If <code>mongod</code> won&rsquo;t start, the most common causes are: stale lock file (<code>/usr/local/var/mongodb/mongod.lock</code> on macOS), permission errors on the data directory, or the port being in use (kill the offender with <code>lsof -i :27017</code>). Logs live at <code>/usr/local/var/log/mongodb/mongo.log</code> on macOS, <code>/var/log/mongodb/mongod.log</code> on Linux. For 95% of MERN dev work you should skip all this and use Atlas.</p>'''


ANSWERS[8] = r'''<p><strong>Mongoose</strong> is an <em>Object Data Modeler</em> (ODM) for MongoDB &mdash; the conceptual cousin of an ORM but for documents instead of tables. It sits between your Node code and the raw MongoDB driver and adds:</p>

<ul>
<li><strong>Schemas + validation</strong> &mdash; you declare what a document looks like, and Mongoose rejects writes that don&rsquo;t match (required fields, types, custom validators, enums).</li>
<li><strong>Type casting</strong> &mdash; coerces strings to ObjectIds, dates, numbers automatically.</li>
<li><strong>Middleware (hooks)</strong> &mdash; <code>pre</code>/<code>post</code> save, find, update, delete hooks for cross&ndash;cutting logic.</li>
<li><strong>Population</strong> &mdash; the document version of joins; pulls related documents by ObjectId reference.</li>
<li><strong>Virtuals</strong> &mdash; computed properties that don&rsquo;t live in MongoDB.</li>
<li><strong>Query helpers + chainable APIs</strong> &mdash; nicer than the raw driver for most app code.</li>
</ul>

<p>The trade&ndash;off is overhead and an extra layer of magic. Many teams skip Mongoose for new code in 2026 and use the official driver directly, paired with <strong>Zod</strong> for validation, because Zod gives end&ndash;to&ndash;end TypeScript inference. Either choice is valid; Mongoose remains the default in MERN tutorials and is fine for most projects. <strong>Prisma</strong> also supports MongoDB now and is the typed&ndash;ORM option if you want strict generated types.</p>'''


ANSWERS[9] = r'''<p>Connecting Mongoose to MongoDB takes one async call at app startup.</p>

<pre><code>// src/db.ts
import mongoose from &quot;mongoose&quot;;

export async function connectDb() {
  const uri = process.env.MONGO_URI;
  if (!uri) throw new Error(&quot;MONGO_URI not set&quot;);

  mongoose.set(&quot;strictQuery&quot;, true);
  await mongoose.connect(uri, {
    serverSelectionTimeoutMS: 5000
  });

  mongoose.connection.on(&quot;error&quot;, (e) =&gt; console.error(&quot;Mongo error&quot;, e));
  mongoose.connection.on(&quot;disconnected&quot;, () =&gt; console.warn(&quot;Mongo disconnected&quot;));
  console.log(&quot;Mongo connected&quot;);
}

// src/index.ts
import { connectDb } from &quot;./db.js&quot;;
import app from &quot;./app.js&quot;;

await connectDb();
app.listen(4000);</code></pre>

<p>The connection string format is <code>mongodb+srv://&lt;user&gt;:&lt;pass&gt;@cluster0.xxxxx.mongodb.net/myapp?retryWrites=true&amp;w=majority</code> for Atlas, or <code>mongodb://localhost:27017/myapp</code> for local. Always store it in <code>.env</code> and load via <code>dotenv</code> (or the built&ndash;in <code>node --env-file=.env</code>).</p>

<p>Mongoose maintains a connection pool internally (default size 100) and reuses connections across requests &mdash; you connect <em>once</em> at startup, never per request. Listen for <code>disconnected</code>/<code>reconnected</code> events to log lifecycle and feed your monitoring (Datadog, Sentry).</p>'''


ANSWERS[10] = r'''<p>A minimal Express server is about ten lines plus a couple of imports.</p>

<pre><code>// src/app.ts
import express from &quot;express&quot;;
import cors from &quot;cors&quot;;
import helmet from &quot;helmet&quot;;
import morgan from &quot;morgan&quot;;

const app = express();

// Middleware (order matters)
app.use(helmet());                              // basic security headers
app.use(cors({ origin: process.env.WEB_ORIGIN }));
app.use(express.json({ limit: &quot;1mb&quot; }));
app.use(morgan(&quot;dev&quot;));                          // request logging

// Routes
app.get(&quot;/health&quot;, (req, res) =&gt; res.json({ ok: true }));
app.use(&quot;/users&quot;, usersRouter);

// 404 + error handler must be last
app.use((req, res) =&gt; res.status(404).json({ error: &quot;Not found&quot; }));
app.use((err, req, res, next) =&gt; {
  console.error(err);
  res.status(500).json({ error: &quot;Server error&quot; });
});

export default app;</code></pre>

<p>The four building blocks are <strong>middleware</strong> (functions running on every request), <strong>routes</strong> (handlers for specific URLs), the <strong>request</strong>/<strong>response</strong> objects, and the global <strong>error handler</strong> (a middleware with four parameters &mdash; Express recognizes the signature). Mount routers with <code>app.use(&quot;/prefix&quot;, router)</code> to keep the file structure clean.</p>

<p>Run with <code>tsx watch src/index.ts</code> (or <code>nodemon</code>) for hot reload during development.</p>'''


ANSWERS[11] = r'''<p>A 2026 MERN project usually lives as a <strong>monorepo</strong> with separate frontend and backend workspaces, managed by pnpm or Bun.</p>

<pre><code>my-app/
├── apps/
│   ├── web/                    # React (Vite or Next.js)
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── routes/         # or app/ for Next.js App Router
│   │   │   ├── lib/
│   │   │   └── main.tsx
│   │   ├── public/
│   │   ├── index.html
│   │   ├── vite.config.ts
│   │   └── package.json
│   └── api/                    # Express/Hono on Node.js
│       ├── src/
│       │   ├── routes/
│       │   ├── models/         # Mongoose schemas
│       │   ├── middleware/
│       │   ├── lib/
│       │   ├── app.ts
│       │   └── index.ts
│       └── package.json
├── packages/                   # shared code
│   ├── types/                  # shared TS types / Zod schemas
│   └── ui/                     # optional shared component library
├── docker-compose.yml          # local Mongo + Redis
├── turbo.json                  # Turborepo orchestration
├── pnpm-workspace.yaml
├── package.json                # root workspace
└── README.md</code></pre>

<p>The win of this layout is sharing types end&ndash;to&ndash;end &mdash; the API exports a Zod schema or tRPC router that the React app consumes with full TypeScript inference. Older MERN tutorials separate <code>client/</code> and <code>server/</code> as siblings without a workspace; functionally similar but you lose easy code sharing.</p>'''


ANSWERS[12] = r'''<p><strong>Don&rsquo;t use Create React App in 2026</strong> &mdash; it was officially deprecated by the React team. Use <strong>Vite</strong> for SPAs or <strong>Next.js</strong> for SSR/full&ndash;stack React.</p>

<pre><code># Vite (recommended for SPAs)
pnpm create vite@latest my-app
# pick: React, then TypeScript

cd my-app
pnpm install
pnpm dev                       # starts on http://localhost:5173

# Next.js (recommended if you need SSR/SEO)
pnpm create next-app@latest my-app
# answers: TypeScript yes, ESLint yes, Tailwind yes, App Router yes

# Alternatives
pnpm create vite@latest my-app -- --template react-ts
pnpm create remix@latest         # Remix
pnpm create -- @tanstack/start@latest   # TanStack Start</code></pre>

<p>Vite gives you near&ndash;instant dev server startup, hot module replacement, and a Rollup&ndash;based production build &mdash; CRA was Webpack&ndash;based and noticeably slower on cold starts. Next.js adds server&ndash;side rendering, static generation, file&ndash;system routing, image optimization, and edge runtime support. <strong>Remix</strong> and <strong>TanStack Start</strong> are valid full&ndash;stack alternatives if Next feels too opinionated.</p>

<p>If you genuinely need to support a legacy CRA project, you can run it but plan a migration to Vite (<code>npx @vitejs/cra-to-vite</code> automates most of it).</p>'''


ANSWERS[13] = r'''<p><code>package.json</code> is the manifest at the root of every Node project. It declares metadata, dependencies, and scripts, and is what npm/pnpm/Bun read to install + run things.</p>

<pre><code>{
  &quot;name&quot;: &quot;my-api&quot;,
  &quot;version&quot;: &quot;1.0.0&quot;,
  &quot;type&quot;: &quot;module&quot;,
  &quot;main&quot;: &quot;dist/index.js&quot;,
  &quot;scripts&quot;: {
    &quot;dev&quot;: &quot;tsx watch src/index.ts&quot;,
    &quot;build&quot;: &quot;tsc&quot;,
    &quot;start&quot;: &quot;node dist/index.js&quot;,
    &quot;test&quot;: &quot;vitest&quot;,
    &quot;lint&quot;: &quot;eslint .&quot;
  },
  &quot;dependencies&quot;: {
    &quot;express&quot;: &quot;^4.21.0&quot;,
    &quot;mongoose&quot;: &quot;^8.5.0&quot;,
    &quot;zod&quot;: &quot;^3.23.0&quot;
  },
  &quot;devDependencies&quot;: {
    &quot;typescript&quot;: &quot;^5.5.0&quot;,
    &quot;tsx&quot;: &quot;^4.19.0&quot;,
    &quot;vitest&quot;: &quot;^2.0.0&quot;
  },
  &quot;engines&quot;: { &quot;node&quot;: &quot;&gt;=22&quot; },
  &quot;packageManager&quot;: &quot;pnpm@9.0.0&quot;
}</code></pre>

<p>Key fields: <strong>name</strong>/<strong>version</strong> identify the package, <strong>type</strong> picks ESM (<code>module</code>) vs CommonJS, <strong>scripts</strong> are runnable via <code>pnpm &lt;name&gt;</code>, <strong>dependencies</strong> ship with your app (production), <strong>devDependencies</strong> are for tooling (build, test, lint), <strong>engines</strong> documents the required Node version, and <strong>packageManager</strong> pins the package manager (Corepack reads this to use the right version automatically).</p>

<p>Always commit the lockfile (<code>pnpm-lock.yaml</code>) so installs are reproducible across machines and CI.</p>'''


ANSWERS[14] = r'''<p>Environment variables let you change config (database URLs, API keys, feature flags) without changing code. The convention is a <code>.env</code> file in development and platform&ndash;managed env vars in production.</p>

<pre><code># .env (gitignored)
PORT=4000
MONGO_URI=mongodb+srv://user:pass@cluster0.mongodb.net/myapp
JWT_SECRET=dev-only-do-not-ship
WEB_ORIGIN=http://localhost:5173

# .env.example (committed) &mdash; documents the schema
PORT=
MONGO_URI=
JWT_SECRET=
WEB_ORIGIN=</code></pre>

<pre><code>// In Node 20+ no library needed:
node --env-file=.env src/index.js

// or with the classic dotenv package
import &quot;dotenv/config&quot;;
const port = process.env.PORT ?? 4000;</code></pre>

<p>Always validate env vars at startup with <strong>Zod</strong> so the app fails fast with a clear error instead of silently misbehaving:</p>

<pre><code>const env = z.object({
  MONGO_URI: z.string().url(),
  JWT_SECRET: z.string().min(32),
  PORT: z.coerce.number().default(4000)
}).parse(process.env);</code></pre>

<p>For React (Vite), env vars must be prefixed with <code>VITE_</code> to be exposed to the browser; for Next.js use <code>NEXT_PUBLIC_</code>. Anything not prefixed stays server&ndash;only. <strong>Never</strong> put secrets in client&ndash;side env vars &mdash; they ship in the bundle.</p>'''


ANSWERS[15] = r'''<p>Configuration in a MERN app spans three concerns: <strong>environment</strong> (URLs, secrets &mdash; always env vars), <strong>feature flags</strong> (toggles you change at runtime), and <strong>static config</strong> (constants compiled in).</p>

<pre><code>// config.ts &mdash; one validated source of truth
import { z } from &quot;zod&quot;;

const Env = z.object({
  NODE_ENV: z.enum([&quot;development&quot;, &quot;production&quot;, &quot;test&quot;])
              .default(&quot;development&quot;),
  PORT: z.coerce.number().default(4000),
  MONGO_URI: z.string().url(),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
  WEB_ORIGIN: z.string().url()
});

export const config = Env.parse(process.env);
export const isProd = config.NODE_ENV === &quot;production&quot;;</code></pre>

<p>Best practices:</p>

<ul>
<li><strong>Twelve&ndash;Factor App</strong> &mdash; configuration is in the environment, not in code.</li>
<li><strong>Validate at startup</strong> &mdash; refuse to boot if required env is missing or malformed.</li>
<li><strong>Secrets in a manager</strong> &mdash; for production, store in <strong>Doppler</strong>, <strong>Infisical</strong>, <strong>AWS Secrets Manager</strong>, <strong>HashiCorp Vault</strong>, or platform secret stores (Vercel/Fly env, GitHub Actions secrets). Never commit <code>.env</code> files.</li>
<li><strong>Feature flags</strong> &mdash; use <strong>Statsig</strong>, <strong>GrowthBook</strong>, <strong>LaunchDarkly</strong>, or <strong>PostHog</strong> for runtime toggles you can flip without redeploying.</li>
<li><strong>Per&ndash;environment files</strong> &mdash; <code>.env.development</code>, <code>.env.test</code>, <code>.env.production</code> as needed, but production values come from the secret manager.</li>
</ul>'''


ANSWERS[16] = r'''<p>The <code>.env</code> file is a plain text file with <code>KEY=VALUE</code> pairs that holds local configuration &mdash; database URLs, API keys, feature flags &mdash; outside your source code. Each line becomes <code>process.env.KEY</code> at runtime.</p>

<pre><code># .env (NEVER commit this)
MONGO_URI=mongodb+srv://user:pass@cluster0.mongodb.net/myapp
JWT_SECRET=8f4a23bcb5e9c4...long-random-string
STRIPE_SECRET_KEY=sk_test_...

# .env.example (DO commit this &mdash; documents required vars)
MONGO_URI=
JWT_SECRET=
STRIPE_SECRET_KEY=

# .gitignore
.env
.env.local
.env.*.local</code></pre>

<p>Loading in Node:</p>

<pre><code>// Modern Node 20+ &mdash; built-in, no library
node --env-file=.env src/index.js

// Or via the classic dotenv package
import &quot;dotenv/config&quot;;
console.log(process.env.MONGO_URI);</code></pre>

<p>Critical rules:</p>

<ul>
<li><strong>Never commit</strong> <code>.env</code> &mdash; add it to <code>.gitignore</code> from day one. Secrets in git are extremely common breaches; tools like <strong>gitleaks</strong> and <strong>GitGuardian</strong> exist precisely because of this.</li>
<li><strong>Commit a <code>.env.example</code></strong> with empty values so teammates know what they need to set.</li>
<li><strong>Validate at boot</strong> with Zod (see prior answer).</li>
<li><strong>Production reads from the platform</strong> &mdash; Vercel/Fly/Render/Railway dashboards, AWS Secrets Manager, etc., not from a <code>.env</code> file on disk.</li>
</ul>'''


ANSWERS[17] = r'''<p>Express routing maps HTTP methods + paths to handler functions. The two patterns are inline routes on the app object and a separate <strong>Router</strong> module for grouping.</p>

<pre><code>// src/routes/users.ts
import { Router } from &quot;express&quot;;
import { User } from &quot;../models/User.js&quot;;

const router = Router();

router.get(&quot;/&quot;, async (req, res) =&gt; {
  const users = await User.find().limit(50);
  res.json(users);
});

router.get(&quot;/:id&quot;, async (req, res) =&gt; {
  const user = await User.findById(req.params.id);
  if (!user) return res.status(404).json({ error: &quot;Not found&quot; });
  res.json(user);
});

router.post(&quot;/&quot;, async (req, res) =&gt; {
  const user = await User.create(req.body);
  res.status(201).json(user);
});

export default router;

// src/app.ts
import users from &quot;./routes/users.js&quot;;
app.use(&quot;/users&quot;, users);            // mount at /users</code></pre>

<p>Routes match in registration order &mdash; the first matching route wins. Use route parameters (<code>:id</code>) for dynamic segments and access them via <code>req.params</code>. Query string lives at <code>req.query</code>, JSON body at <code>req.body</code> (after <code>express.json()</code> middleware).</p>

<p>For nested routes mount routers within routers. For really large APIs, consider migrating to <strong>Hono</strong> or <strong>Fastify</strong> &mdash; both have cleaner async error handling and better TypeScript inference than Express, which still requires a <code>next(err)</code> dance for thrown errors in older versions.</p>'''


ANSWERS[18] = r'''<p>A typical REST endpoint is one route handler that validates input, talks to the database, and returns JSON.</p>

<pre><code>// src/routes/posts.ts
import { Router } from &quot;express&quot;;
import { z } from &quot;zod&quot;;
import { Post } from &quot;../models/Post.js&quot;;

const router = Router();

const CreatePost = z.object({
  title: z.string().min(1).max(200),
  body:  z.string().min(1).max(50_000),
  tags:  z.array(z.string()).max(10).default([])
});

router.post(&quot;/&quot;, async (req, res, next) =&gt; {
  try {
    const data = CreatePost.parse(req.body);    // 400 if invalid
    const post = await Post.create({
      ...data,
      authorId: req.userId                       // from auth middleware
    });
    res.status(201).json(post);
  } catch (err) {
    if (err instanceof z.ZodError) {
      return res.status(400).json({ errors: err.flatten() });
    }
    next(err);                                   // global error handler
  }
});

export default router;</code></pre>

<p>Anatomy of a good endpoint:</p>

<ul>
<li><strong>Validate input</strong> with Zod (or Joi/Valibot/ArkType) &mdash; never trust <code>req.body</code>.</li>
<li><strong>Async handler with try/catch</strong> &mdash; in Express 4 thrown errors don&rsquo;t auto&ndash;forward; pass them to <code>next(err)</code>. Express 5 fixes this.</li>
<li><strong>Return correct status codes</strong> &mdash; 201 Created on POST success, 400 for bad input, 401/403 for auth, 404 for not found, 500 for server errors.</li>
<li><strong>Don&rsquo;t leak internals</strong> &mdash; never return raw stack traces to clients.</li>
</ul>'''


ANSWERS[19] = r'''<p>Express models the request/response lifecycle as plain Node HTTP objects with extra helpers. <code>req</code> is what came in; <code>res</code> is what you send back; both pass through middleware in registration order until a handler ends the cycle by calling <code>res.send</code>/<code>res.json</code>/<code>res.end</code>.</p>

<pre><code>app.post(&quot;/orders&quot;, async (req, res) =&gt; {
  // Read input
  const userId = req.userId;                      // set by auth middleware
  const { sku, qty } = req.body;                  // JSON body
  const ip = req.ip;                              // client IP
  const ua = req.get(&quot;user-agent&quot;);                // request header

  // Do work
  const order = await Order.create({ userId, sku, qty });

  // Send response
  res
    .status(201)
    .set(&quot;Location&quot;, `/orders/${order._id}`)
    .json({ id: order._id, total: order.total });
});</code></pre>

<p>Common <code>req</code> fields: <code>req.params</code> (URL params), <code>req.query</code> (query string), <code>req.body</code> (JSON/form data after middleware), <code>req.headers</code> (raw), <code>req.get(&quot;X&quot;)</code> (case&ndash;insensitive header), <code>req.cookies</code> (after cookie&ndash;parser).</p>

<p>Common <code>res</code> methods: <code>res.status(n)</code> (chainable), <code>res.json(obj)</code> (sets <code>Content-Type</code>), <code>res.send(text)</code>, <code>res.redirect(url)</code>, <code>res.cookie(name, value, opts)</code>. Each request must call exactly one terminal method &mdash; calling two throws &ldquo;Cannot set headers after they are sent&rdquo;, the most classic Express bug.</p>'''


ANSWERS[20] = r'''<p><strong>CORS</strong> (Cross&ndash;Origin Resource Sharing) is the browser security model that blocks JavaScript on <code>https://app.example.com</code> from calling <code>https://api.example.com</code> unless the API explicitly opts in via response headers. Same&ndash;origin requests are unrestricted; cross&ndash;origin require the server to send <code>Access-Control-Allow-Origin</code> and friends.</p>

<pre><code>pnpm add cors @types/cors</code></pre>

<pre><code>import express from &quot;express&quot;;
import cors from &quot;cors&quot;;

const app = express();

// Single origin, allow credentials (cookies/auth headers)
app.use(cors({
  origin: process.env.WEB_ORIGIN ?? &quot;http://localhost:5173&quot;,
  credentials: true,
  methods: [&quot;GET&quot;, &quot;POST&quot;, &quot;PUT&quot;, &quot;PATCH&quot;, &quot;DELETE&quot;]
}));

// Multiple origins (e.g. staging + prod)
const allowed = [&quot;https://app.example.com&quot;, &quot;https://staging.example.com&quot;];
app.use(cors({
  origin: (origin, cb) =&gt; cb(null, !origin || allowed.includes(origin)),
  credentials: true
}));</code></pre>

<p>Key rules:</p>

<ul>
<li><strong>Never use <code>origin: &quot;*&quot;</code> with <code>credentials: true</code></strong> &mdash; the browser refuses; you must list explicit origins.</li>
<li><strong>Preflight requests</strong> (<code>OPTIONS</code>) happen automatically for &ldquo;non&ndash;simple&rdquo; methods like <code>PUT</code>/<code>DELETE</code> or custom headers. The <code>cors</code> package handles them.</li>
<li><strong>If you serve frontend + API from the same domain</strong> (e.g. via Next.js API routes or a reverse proxy at <code>/api</code>), CORS doesn&rsquo;t apply at all &mdash; same origin.</li>
<li><strong>Cookies need <code>credentials: &quot;include&quot;</code> on the fetch</strong> + <code>credentials: true</code> on the server + <code>SameSite=None; Secure</code> on the cookie.</li>
</ul>'''


ANSWERS[21] = r'''<p>Express error handling has one trick: any middleware with <strong>four parameters</strong> <code>(err, req, res, next)</code> is recognized as the global error handler. Errors flow to it via thrown async errors in Express 5, or via <code>next(err)</code> in Express 4.</p>

<pre><code>// src/middleware/errors.ts
export class HttpError extends Error {
  constructor(public status: number, message: string, public meta?: any) {
    super(message);
  }
}

export function notFound(req, res) {
  res.status(404).json({ error: &quot;Not found&quot; });
}

export function errorHandler(err, req, res, next) {
  // log full error server-side, never leak to client
  req.log?.error(err);

  if (err instanceof HttpError) {
    return res.status(err.status).json({ error: err.message, ...err.meta });
  }
  if (err.name === &quot;ZodError&quot;) {
    return res.status(400).json({ errors: err.flatten() });
  }
  if (err.name === &quot;ValidationError&quot;) {  // Mongoose
    return res.status(400).json({ error: err.message });
  }
  res.status(500).json({ error: &quot;Server error&quot; });
}

// app.ts &mdash; mount LAST, after all routes
app.use(notFound);
app.use(errorHandler);</code></pre>

<p>Best practices: define a <strong>typed <code>HttpError</code></strong> class so handlers throw <code>throw new HttpError(404, &quot;User not found&quot;)</code> rather than building the response inline; in Express 4 wrap async handlers with <code>express-async-handler</code> or upgrade to Express 5 which awaits async handlers automatically; <strong>never leak stack traces</strong> in production responses; pipe errors to <strong>Sentry</strong>, <strong>Honeybadger</strong>, or <strong>Datadog APM</strong> for tracking + alerting.</p>'''


ANSWERS[22] = r'''<p>The official <strong>MongoDB Node.js driver</strong> is the lower&ndash;level alternative to Mongoose &mdash; you skip the ODM and talk directly to MongoDB using its native API. It returns plain JS objects, which gives you full control + slightly better performance, with no schema enforcement.</p>

<pre><code>pnpm add mongodb</code></pre>

<pre><code>// src/db.ts
import { MongoClient } from &quot;mongodb&quot;;

const client = new MongoClient(process.env.MONGO_URI!, {
  serverSelectionTimeoutMS: 5000,
  retryWrites: true
});

let _connected = false;
export async function connectDb() {
  if (_connected) return client;
  await client.connect();
  _connected = true;
  console.log(&quot;Mongo connected&quot;);
  return client;
}

export const db = client.db(&quot;myapp&quot;);
export const users = db.collection(&quot;users&quot;);

// usage in a handler
const newUser = await users.insertOne({ email, name, createdAt: new Date() });
const user = await users.findOne({ _id: newUser.insertedId });
const all = await users.find({ active: true }).limit(50).toArray();</code></pre>

<p>The driver maintains a pool internally; you connect <em>once</em> at boot and reuse the client across requests. The 2026 modern setup pairs the raw driver with <strong>Zod</strong> for application&ndash;level validation and TypeScript types &mdash; same end&ndash;result as Mongoose schemas but typed end&ndash;to&ndash;end without runtime overhead.</p>

<p>If you want a typed ORM&ndash;ish layer with code generation, <strong>Prisma</strong> now supports MongoDB and gives you generated TS types from a schema file. Otherwise the raw driver + Zod is the leanest, fastest combo.</p>'''


ANSWERS[23] = r'''<p>A Mongoose <strong>schema</strong> describes the shape of documents in a collection, and a <strong>model</strong> is the runtime object you actually call (<code>find</code>, <code>create</code>, etc.) &mdash; one model per collection.</p>

<pre><code>// src/models/User.ts
import mongoose, { Schema, model, InferSchemaType } from &quot;mongoose&quot;;

const userSchema = new Schema(
  {
    email: { type: String, required: true, unique: true, lowercase: true,
             trim: true, index: true },
    name:  { type: String, required: true, trim: true },
    role:  { type: String, enum: [&quot;user&quot;, &quot;admin&quot;], default: &quot;user&quot; },
    age:   { type: Number, min: 13, max: 120 },
    tags:  [{ type: String }],
    profile: {
      bio:    String,
      avatar: String
    }
  },
  { timestamps: true }            // createdAt, updatedAt
);

// instance method
userSchema.methods.greet = function () { return `Hi, ${this.name}`; };

// derive a TS type from the schema
export type IUser = InferSchemaType&lt;typeof userSchema&gt;;
export const User = model&lt;IUser&gt;(&quot;User&quot;, userSchema);</code></pre>

<p>Schema features worth knowing: required + default + enum validators, <code>unique</code> creates a unique index in Mongo, <code>timestamps: true</code> auto&ndash;populates <code>createdAt</code>/<code>updatedAt</code>, nested objects + arrays of subdocuments are first&ndash;class, instance methods + static methods + virtuals + middleware (<code>pre</code>/<code>post</code> hooks) hang off the schema.</p>

<p>The model name (<code>&quot;User&quot;</code>) becomes the lowercase plural collection name (<code>users</code>) automatically. Use <code>InferSchemaType</code> to derive TypeScript types so your handlers get autocomplete without duplicating the schema.</p>'''


ANSWERS[24] = r'''<p>CRUD operations &mdash; <strong>C</strong>reate, <strong>R</strong>ead, <strong>U</strong>pdate, <strong>D</strong>elete &mdash; are one&ndash;line method calls on the Mongoose model.</p>

<pre><code>import { User } from &quot;../models/User.js&quot;;

// CREATE
const u = await User.create({ email: &quot;ada@example.com&quot;, name: &quot;Ada&quot; });
const many = await User.insertMany([{ email: &quot;a@b&quot; }, { email: &quot;c@d&quot; }]);

// READ
const byId = await User.findById(id);
const one  = await User.findOne({ email: &quot;ada@example.com&quot; });
const list = await User
  .find({ role: &quot;user&quot; })
  .select(&quot;email name createdAt&quot;)        // projection
  .sort({ createdAt: -1 })
  .skip(0).limit(50)
  .lean();                                // plain JS object, faster

// UPDATE
await User.updateOne({ _id: id }, { $set: { name: &quot;Ada L&quot; } });
const updated = await User.findByIdAndUpdate(
  id,
  { $set: { name: &quot;Ada L&quot; } },
  { new: true, runValidators: true }      // returns updated doc
);
await User.updateMany({ role: &quot;user&quot; }, { $set: { active: true } });

// DELETE
await User.deleteOne({ _id: id });
await User.findByIdAndDelete(id);
await User.deleteMany({ active: false });</code></pre>

<p>Tips: use <strong><code>.lean()</code></strong> for read&ndash;heavy queries to skip Mongoose hydration (faster, returns plain objects, no methods); <strong>always pass <code>{ runValidators: true }</code></strong> on updates or schema validators silently skip; <strong>use update operators</strong> (<code>$set</code>, <code>$inc</code>, <code>$push</code>, <code>$pull</code>) instead of replacing the whole document; <strong>avoid <code>findOneAndUpdate</code> race conditions</strong> by relying on atomic operators rather than read&ndash;modify&ndash;write loops.</p>'''


ANSWERS[25] = r'''<p>Authentication in MERN is &ldquo;who is the user?&rdquo;; authorization is &ldquo;what can they do?&rdquo;. The 2026 default is to <strong>not roll your own</strong> &mdash; use a managed provider unless you have a specific reason.</p>

<p><strong>Hosted (recommended for new apps):</strong></p>
<ul>
<li><strong>Clerk</strong> &mdash; drop&ndash;in React components, Passkeys, MFA, organizations, SCIM. Best DX.</li>
<li><strong>Auth0</strong> &mdash; enterprise standard, OIDC, social logins, B2B.</li>
<li><strong>WorkOS</strong> &mdash; B2B SSO/SAML/SCIM, AuthKit for end&ndash;user auth.</li>
<li><strong>Stytch</strong> / <strong>Stack Auth</strong> / <strong>Better Auth</strong> &mdash; modern alternatives.</li>
<li><strong>Supabase Auth</strong> / <strong>Firebase Auth</strong> &mdash; bundled with their backends.</li>
</ul>

<p><strong>Self&ndash;hosted (build your own):</strong></p>

<pre><code>// Sign up
import argon2 from &quot;argon2&quot;;          // not bcrypt &mdash; argon2id is the OWASP pick
const hash = await argon2.hash(plaintext, { type: argon2.argon2id });
await User.create({ email, hash });

// Sign in
const user = await User.findOne({ email });
if (!user || !await argon2.verify(user.hash, plaintext)) {
  return res.status(401).json({ error: &quot;Invalid creds&quot; });
}
const token = jwt.sign({ sub: user._id }, JWT_SECRET, { expiresIn: &quot;15m&quot; });
res.cookie(&quot;token&quot;, token, { httpOnly: true, secure: true, sameSite: &quot;lax&quot; });</code></pre>

<p>Critical rules: hash with <strong>argon2id</strong> (or bcrypt with cost ≥12 if argon2 isn&rsquo;t available); short&ndash;lived access tokens + refresh token rotation with reuse detection; store tokens in <strong>httpOnly cookies</strong> (not localStorage &mdash; XSS&ndash;readable); add MFA + Passkeys via <strong>SimpleWebAuthn</strong>; rate&ndash;limit auth endpoints aggressively. Most teams should pick a hosted provider.</p>'''


ANSWERS[26] = r'''<p><strong>JWT</strong> (JSON Web Token) is a compact signed token format &mdash; three base64url chunks (<code>header.payload.signature</code>) separated by dots. The signature lets the server verify the token wasn&rsquo;t tampered with, without storing session state in a database. The payload is <em>encoded</em>, not encrypted &mdash; anyone can decode it &mdash; so never put secrets in there.</p>

<pre><code>pnpm add jsonwebtoken @types/jsonwebtoken</code></pre>

<pre><code>import jwt from &quot;jsonwebtoken&quot;;

// Sign on login
const token = jwt.sign(
  { sub: user._id.toString(), role: user.role },
  process.env.JWT_SECRET!,
  { expiresIn: &quot;15m&quot;, issuer: &quot;myapp&quot; }
);

// Verify on each protected request
try {
  const claims = jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload;
  req.userId = claims.sub;
  req.role   = claims.role;
} catch {
  return res.status(401).json({ error: &quot;Invalid token&quot; });
}</code></pre>

<p>Best practices in 2026:</p>

<ul>
<li><strong>Short&ndash;lived access tokens</strong> (5&ndash;15 min) + <strong>long&ndash;lived refresh tokens</strong> (7&ndash;30 days) with rotation and reuse detection.</li>
<li><strong>Store in httpOnly cookies</strong>, not localStorage &mdash; localStorage is readable by any XSS.</li>
<li><strong>Use a strong secret</strong> (32+ random bytes from <code>crypto.randomBytes(32).toString(&quot;base64url&quot;)</code>); rotate periodically.</li>
<li><strong>Prefer hosted auth</strong> &mdash; Clerk, Auth0, WorkOS, Better Auth do all of this correctly with a few lines of code. Rolling your own JWT auth is a famous footgun.</li>
<li><strong>For revocation</strong> you need a denylist or short TTL &mdash; pure JWT can&rsquo;t be invalidated server&ndash;side.</li>
</ul>'''


ANSWERS[27] = r'''<p>Protect routes with <strong>middleware</strong> &mdash; a function that runs before the route handler, sets <code>req.userId</code> from the token, and calls <code>next()</code> if valid or returns 401 if not.</p>

<pre><code>// src/middleware/auth.ts
import { Request, Response, NextFunction } from &quot;express&quot;;
import jwt, { JwtPayload } from &quot;jsonwebtoken&quot;;

declare module &quot;express-serve-static-core&quot; {
  interface Request { userId?: string; role?: string; }
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const token = req.cookies?.token
             ?? req.get(&quot;authorization&quot;)?.replace(/^Bearer /, &quot;&quot;);
  if (!token) return res.status(401).json({ error: &quot;Unauthenticated&quot; });

  try {
    const claims = jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload;
    req.userId = String(claims.sub);
    req.role   = claims.role;
    next();
  } catch {
    res.status(401).json({ error: &quot;Invalid token&quot; });
  }
}

export function requireRole(...allowed: string[]) {
  return (req: Request, res: Response, next: NextFunction) =&gt; {
    if (!req.role || !allowed.includes(req.role)) {
      return res.status(403).json({ error: &quot;Forbidden&quot; });
    }
    next();
  };
}

// usage in routes
router.get(&quot;/me&quot;,    requireAuth,                async (req, res) =&gt; { ... });
router.delete(&quot;/users/:id&quot;, requireAuth, requireRole(&quot;admin&quot;), handler);</code></pre>

<p>Apply middleware at three granularities: <strong>per app</strong> (<code>app.use(requireAuth)</code> for fully&ndash;authenticated APIs), <strong>per router</strong> (<code>router.use(requireAuth)</code>), or <strong>per route</strong> (third arg to <code>router.get</code>). For complex authorization (per&ndash;resource ownership, roles + relations), pair this with a policy engine like <strong>Cerbos</strong>, <strong>SpiceDB</strong>, or <strong>OpenFGA</strong> rather than scattering <code>if</code>s.</p>'''


ANSWERS[28] = r'''<p><strong>Heroku</strong> was the original PaaS for MERN apps, but it became paid&ndash;only in 2022 and is much less popular in 2026. Modern equivalents are <strong>Render</strong>, <strong>Railway</strong>, <strong>Fly.io</strong>, <strong>Vercel</strong> (frontend + serverless), <strong>Cloud Run</strong>, and <strong>Northflank</strong>. The deploy story is similar across all of them: connect a Git repo, set env vars, push.</p>

<pre><code># If you genuinely must use Heroku:
heroku login
heroku create my-api
heroku addons:create mongolab           # or use Atlas instead
heroku config:set JWT_SECRET=&quot;...&quot;
git push heroku main
heroku logs --tail

# Modern alternatives &mdash; all roughly:
# 1. Sign up &amp; connect GitHub
# 2. Pick the repo &amp; branch
# 3. Set env vars in dashboard
# 4. Push &mdash; auto deploys

# Render: render.com
# Railway: railway.app
# Fly.io: fly.io (CLI: fly launch)
# Northflank: northflank.com</code></pre>

<p>Heroku&ndash;specific concepts that still appear in tutorials:</p>

<ul>
<li><strong>Procfile</strong> &mdash; tells the platform how to start your process: <code>web: node dist/index.js</code>.</li>
<li><strong>Dyno</strong> &mdash; Heroku&rsquo;s name for a container/process.</li>
<li><strong>Buildpacks</strong> &mdash; auto&ndash;detect Node and run <code>npm install</code> + <code>npm run build</code>.</li>
<li><strong>Config vars</strong> &mdash; the env var dashboard.</li>
</ul>

<p>For React: deploy the static build to <strong>Vercel</strong>, <strong>Netlify</strong>, or <strong>Cloudflare Pages</strong> (free tiers + global CDN). Deploy the API to <strong>Render</strong>/<strong>Railway</strong>/<strong>Fly.io</strong> with managed Mongo via <strong>Atlas</strong>. This split is the modern MERN deployment pattern.</p>'''


ANSWERS[29] = r'''<p>The <strong>Procfile</strong> is a Heroku&ndash;invented text file at the root of a project that declares process types and the command to start each. Render, Fly.io, and Northflank also recognize it.</p>

<pre><code># Procfile
web: node dist/index.js
worker: node dist/worker.js
release: node dist/migrate.js</code></pre>

<p>Process type meanings:</p>

<ul>
<li><strong><code>web</code></strong> &mdash; the HTTP server. The platform binds it to <code>$PORT</code> and routes external traffic to it.</li>
<li><strong><code>worker</code></strong> &mdash; background processes (queue consumers, scheduled jobs). Multiple workers can run.</li>
<li><strong><code>release</code></strong> &mdash; runs once before each deploy goes live; perfect place for database migrations.</li>
</ul>

<p>For a typical MERN API:</p>

<pre><code># Procfile
web: node dist/index.js
release: node dist/scripts/migrate.js</code></pre>

<p>If you don&rsquo;t supply a Procfile, Heroku looks at <code>package.json</code> &ldquo;start&rdquo; script and runs <code>npm start</code> as the web process &mdash; usually fine for simple apps. Modern alternatives have moved past Procfile syntax: <strong>Render</strong> uses a dashboard or <code>render.yaml</code>; <strong>Fly.io</strong> uses <code>fly.toml</code> + a Dockerfile; <strong>Vercel</strong> auto&ndash;detects framework. The same conceptual pieces (start command, release hooks, worker processes) exist everywhere; the syntax differs.</p>'''


ANSWERS[30] = r'''<p>Environment variables on Heroku (and equivalent platforms) are configured in the dashboard or via CLI &mdash; never committed to git.</p>

<pre><code># Heroku CLI
heroku config:set MONGO_URI=&quot;mongodb+srv://...&quot; -a my-api
heroku config:set JWT_SECRET=&quot;...&quot; NODE_ENV=production
heroku config                              # list all
heroku config:unset SOME_VAR

# Render &mdash; render.com dashboard, or render.yaml
# Railway &mdash; railway.app dashboard, or `railway variables set`
# Fly.io
fly secrets set MONGO_URI=&quot;...&quot; JWT_SECRET=&quot;...&quot;
fly secrets list

# Vercel
vercel env add MONGO_URI production
# or in the dashboard: Settings &rarr; Environment Variables</code></pre>

<p>Cross&ndash;platform best practices:</p>

<ul>
<li><strong>Validate at boot</strong> with Zod &mdash; refuse to start if a required var is missing.</li>
<li><strong>Use platform&ndash;native secret stores</strong> &mdash; Heroku Config Vars, Render Environment Groups, Fly Secrets, Vercel Encrypted Env. They&rsquo;re encrypted at rest and only available to your running app.</li>
<li><strong>For shared secrets across many services</strong> use <strong>Doppler</strong>, <strong>Infisical</strong>, <strong>AWS Secrets Manager</strong>, or <strong>HashiCorp Vault</strong> &mdash; central source of truth synced to each platform.</li>
<li><strong>Separate environments</strong> &mdash; staging and production must not share databases or API keys.</li>
<li><strong>Rotate periodically</strong> and immediately when a developer leaves the team.</li>
</ul>

<p>Heroku will restart your dynos automatically when config vars change &mdash; same for Render, Railway, and Fly.io with secrets.</p>'''


ANSWERS[31] = r'''<p><strong>MongoDB Atlas</strong> is MongoDB&rsquo;s managed cloud service &mdash; click&ndash;to&ndash;deploy clusters across AWS, GCP, and Azure with backup, monitoring, scaling, and security baked in. It&rsquo;s how essentially every MERN team in 2026 runs production MongoDB.</p>

<p>Step&ndash;by&ndash;step deployment:</p>

<ol>
<li>Sign up at <code>mongodb.com/atlas</code> (free).</li>
<li><strong>Create a project</strong> (organizational namespace).</li>
<li><strong>Create a cluster</strong> &mdash; pick the free <strong>M0</strong> for dev (512 MB), or a paid M10+ tier for production. Choose AWS/GCP/Azure region closest to your API.</li>
<li><strong>Add a database user</strong> &mdash; Database Access &rarr; Add New User &mdash; with a strong password.</li>
<li><strong>Configure network access</strong> &mdash; Network Access &rarr; Add IP. For dev, allow your IP; for production, allow only your hosting provider&rsquo;s outbound IPs (or use VPC peering / PrivateLink for AWS).</li>
<li><strong>Get the connection string</strong> &mdash; Clusters &rarr; Connect &rarr; &ldquo;Drivers&rdquo; &rarr; copy the <code>mongodb+srv://&lt;user&gt;:&lt;pass&gt;@cluster0.xxxxx.mongodb.net/&lt;db&gt;</code> URI.</li>
</ol>

<pre><code># .env (local) &mdash; never commit
MONGO_URI=mongodb+srv://api-user:S3cret@cluster0.abcde.mongodb.net/myapp?retryWrites=true&amp;w=majority

# Production &mdash; set in Vercel/Render/Fly secret store</code></pre>

<p>Atlas runs continuous backups (point&ndash;in&ndash;time restore on M10+), exposes Performance Advisor (suggests indexes), Query Profiler, and Atlas Search (full&ndash;text + vector). For most MERN teams, Atlas removes the need to ever run <code>mongod</code> yourself.</p>'''


ANSWERS[32] = r'''<p>Atlas is the path of least resistance for production MongoDB. Concrete advantages over self&ndash;hosting:</p>

<ul>
<li><strong>Zero ops</strong> &mdash; MongoDB handles upgrades, patches, OS hardening, and storage scaling. No DBA needed for typical MERN scale.</li>
<li><strong>Backups + PITR</strong> &mdash; continuous backup with point&ndash;in&ndash;time restore (sub&ndash;minute RPO) on M10+ tiers.</li>
<li><strong>Built&ndash;in monitoring</strong> &mdash; Performance Advisor automatically suggests missing indexes; Query Profiler shows slow queries; Real Time Performance Panel shows ops/sec, locks, network. Datadog and New Relic integrations one&ndash;click.</li>
<li><strong>High availability</strong> &mdash; clusters are 3&ndash;node replica sets across AZs by default. Automatic failover in seconds.</li>
<li><strong>Atlas Search</strong> &mdash; Lucene&ndash;backed full&ndash;text search and faceted queries without a separate Elasticsearch cluster.</li>
<li><strong>Atlas Vector Search</strong> &mdash; native ANN vector index for RAG / recommendations / semantic search alongside operational data.</li>
<li><strong>Atlas Stream Processing</strong> &mdash; transform change streams into materialized views or external sinks (Kafka, S3) without separate infra.</li>
<li><strong>Atlas Triggers + Functions</strong> &mdash; scheduled or change&ndash;driven serverless functions in JavaScript.</li>
<li><strong>Atlas Online Archive</strong> &mdash; tier old data automatically to cheap S3&ndash;backed storage while keeping it queryable.</li>
<li><strong>Global Clusters</strong> &mdash; zone&ndash;sharded multi&ndash;region for data residency (GDPR, India DPDP) and latency.</li>
<li><strong>Free tier</strong> &mdash; M0 covers most dev + small projects without cost.</li>
</ul>

<p>The trade&ndash;off is cost at scale and lock&ndash;in to Atlas&rsquo;s feature set. For most MERN apps both are easy to absorb; the alternative is hiring an SRE.</p>'''


ANSWERS[33] = r'''<p>Connecting Node.js to Atlas is identical to local Mongo &mdash; just swap the connection string. Mongoose or the native driver both work unchanged.</p>

<pre><code># 1. Get the connection string from Atlas:
#    Clusters &rarr; Connect &rarr; Drivers &rarr; copy URI

# 2. Put it in .env (don&apos;t commit)
MONGO_URI=mongodb+srv://api-user:S3cret@cluster0.abcde.mongodb.net/myapp?retryWrites=true&amp;w=majority&amp;appName=myapi</code></pre>

<pre><code>// src/db.ts &mdash; Mongoose
import mongoose from &quot;mongoose&quot;;

export async function connectDb() {
  await mongoose.connect(process.env.MONGO_URI!, {
    serverSelectionTimeoutMS: 5000,
    maxPoolSize: 50               // pool size; default 100
  });
  console.log(&quot;Atlas connected&quot;);
}

// or with the native driver
import { MongoClient } from &quot;mongodb&quot;;
const client = new MongoClient(process.env.MONGO_URI!, {
  serverSelectionTimeoutMS: 5000,
  retryWrites: true,
  w: &quot;majority&quot;
});
await client.connect();
const db = client.db();           // db name comes from URI</code></pre>

<p>Network access checklist:</p>

<ul>
<li><strong>Atlas Network Access</strong> must include the outbound IP of your API host. Vercel, Fly, Render publish their egress IP ranges.</li>
<li><strong>Production:</strong> use <strong>VPC Peering</strong> (AWS/GCP) or <strong>AWS PrivateLink</strong> for private connectivity instead of public IP allowlists.</li>
<li><strong>TLS is on by default</strong> with Atlas (<code>mongodb+srv://</code> implies SRV + TLS); no extra config needed.</li>
<li><strong>Connection pooling</strong> is automatic; one client/Mongoose connection at process boot, reused across requests.</li>
<li><strong>For serverless</strong> (Vercel Functions, AWS Lambda) cache the connection across invocations so cold starts are rare. Use Atlas <strong>Data API</strong> or <strong>MongoDB Driver with cached client</strong>.</li>
</ul>'''


ANSWERS[34] = r'''<p>Sensitive config &mdash; database credentials, API keys, signing secrets &mdash; never lives in code or in committed config files. The hierarchy of safety:</p>

<ol>
<li><strong>Local dev:</strong> <code>.env</code> file (gitignored), <code>.env.example</code> committed for documentation.</li>
<li><strong>CI:</strong> platform&ndash;native secrets &mdash; GitHub Actions <strong>Secrets</strong> + <strong>Environments</strong>, GitLab CI Variables, CircleCI Contexts. Reference via <code>${{ secrets.MONGO_URI }}</code>.</li>
<li><strong>Production:</strong> platform secret stores &mdash; Vercel / Fly / Render / Railway / Heroku Config Vars; AWS Secrets Manager / Parameter Store; GCP Secret Manager; Azure Key Vault.</li>
<li><strong>Centralized for many services:</strong> <strong>Doppler</strong>, <strong>Infisical</strong>, or <strong>HashiCorp Vault</strong> &mdash; single source of truth synced to every platform via integrations.</li>
</ol>

<pre><code># NEVER do this
const MONGO_URI = &quot;mongodb+srv://user:password@cluster.mongodb.net&quot;;

# DO this
const MONGO_URI = process.env.MONGO_URI;
if (!MONGO_URI) throw new Error(&quot;MONGO_URI not set&quot;);

# .gitignore
.env
.env.local
.env.*.local</code></pre>

<p>Defensive practices:</p>

<ul>
<li><strong>Pre&ndash;commit hooks</strong> with <strong>gitleaks</strong> or <strong>trufflehog</strong> to scan for accidentally staged secrets.</li>
<li><strong>GitHub Secret Scanning</strong> + <strong>Dependabot</strong> + <strong>GitGuardian</strong> watch your repo and alert on leaks.</li>
<li><strong>Use prefixed key formats</strong> (e.g., <code>sk_live_</code>) so leaked keys are recognizable + scannable by GitHub automatically.</li>
<li><strong>Rotate secrets</strong> periodically, immediately on any breach, and when a developer leaves.</li>
<li><strong>Short&ndash;lived OIDC credentials</strong> for CI &rarr; cloud (<strong>GitHub OIDC</strong> &rarr; AWS) eliminate long&ndash;lived AWS keys entirely.</li>
</ul>'''


ANSWERS[35] = r'''<p>HTTPS is non&ndash;negotiable in 2026 &mdash; browsers warn aggressively on plain HTTP, and many web APIs (geolocation, service workers, WebAuthn/Passkeys) require it. The good news: you almost never configure TLS yourself.</p>

<p><strong>Recommended approach &mdash; let the platform handle it:</strong></p>

<ul>
<li><strong>Vercel</strong>, <strong>Netlify</strong>, <strong>Cloudflare Pages</strong>, <strong>Render</strong>, <strong>Fly.io</strong>, <strong>Railway</strong>, <strong>Heroku</strong>: HTTPS auto&ndash;provisioned via Let&rsquo;s Encrypt. Add your domain, point DNS, certificates renew automatically.</li>
<li><strong>Cloudflare in front of anything</strong> gives you free TLS termination, HTTP/3, and a global CDN.</li>
</ul>

<p><strong>Self&ndash;hosting (e.g., on a VM):</strong></p>

<pre><code># Get a cert via certbot (Let&apos;s Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com
# auto-renews via cron / systemd timer</code></pre>

<pre><code># Nginx terminates TLS, proxies to Node on :4000
server {
  listen 443 ssl http2;
  server_name api.example.com;
  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

  location / {
    proxy_pass http://127.0.0.1:4000;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-For $remote_addr;
  }
}
server {           # redirect HTTP &rarr; HTTPS
  listen 80;
  server_name api.example.com;
  return 301 https://$host$request_uri;
}</code></pre>

<p>Always set the <strong>HSTS header</strong> (<code>Strict-Transport-Security: max-age=63072000; includeSubDomains; preload</code>) so browsers refuse to downgrade. Use <strong>helmet</strong> middleware in Express to add HSTS + a sensible CSP automatically.</p>'''


ANSWERS[36] = r'''<p><strong>SSL/TLS</strong> &mdash; Transport Layer Security; SSL is the deprecated predecessor name still in casual use &mdash; is the protocol that wraps HTTP into HTTPS. It does three things:</p>

<ul>
<li><strong>Encryption</strong> &mdash; nobody on the wire (coffee shop wifi, ISPs, intermediate routers) can read the request body, headers, cookies, or response.</li>
<li><strong>Integrity</strong> &mdash; tampering with bytes in transit is detected; the connection breaks rather than delivering modified data.</li>
<li><strong>Authentication</strong> &mdash; a valid certificate chain proves you&rsquo;re actually talking to <code>example.com</code> and not a man&ndash;in&ndash;the&ndash;middle.</li>
</ul>

<p>Why it&rsquo;s mandatory:</p>

<ul>
<li><strong>Cookies, tokens, passwords</strong> &mdash; without TLS, anyone on the network can snoop sessions and steal credentials.</li>
<li><strong>Browser features</strong> &mdash; service workers, geolocation, microphone/camera, WebAuthn/Passkeys, Push API, payment APIs all <em>require</em> HTTPS.</li>
<li><strong>SEO + UX</strong> &mdash; Chrome marks plain HTTP as &ldquo;Not secure&rdquo;; Google ranks HTTPS sites higher.</li>
<li><strong>HTTP/2 + HTTP/3</strong> &mdash; major performance wins (multiplexing, header compression, 0&ndash;RTT) require TLS in browsers.</li>
<li><strong>Compliance</strong> &mdash; PCI&ndash;DSS, HIPAA, SOC 2, GDPR all require encryption in transit.</li>
</ul>

<p>In 2026 the modern protocol is <strong>TLS 1.3</strong> (faster handshake, smaller cipher list, forward secrecy by default). Older TLS 1.0/1.1 are deprecated and disabled in modern browsers and platforms. Pair TLS with <strong>HSTS preload</strong> (<code>Strict-Transport-Security: max-age=63072000; includeSubDomains; preload</code> + submit to <code>hstspreload.org</code>) so browsers refuse plain&ndash;HTTP downgrade attacks even on the very first visit.</p>'''


ANSWERS[37] = r'''<p><strong>Let&rsquo;s Encrypt</strong> is a free, automated, browser&ndash;trusted Certificate Authority. It issues 90&ndash;day TLS certificates via the <strong>ACME</strong> protocol &mdash; you prove you control a domain, you get a cert, repeat every &lt;90 days. Most platforms automate the entire loop.</p>

<p><strong>Easiest path &mdash; use a platform that handles it for you:</strong></p>

<ul>
<li>Vercel, Netlify, Render, Fly.io, Cloudflare, Railway, Heroku, Cloud Run all auto&ndash;provision Let&rsquo;s Encrypt certs when you add a domain. Zero config.</li>
</ul>

<p><strong>Self&ndash;hosted &mdash; <code>certbot</code> with Nginx:</strong></p>

<pre><code># Install certbot &amp; nginx plugin
sudo apt install certbot python3-certbot-nginx

# Get cert + auto-configure nginx
sudo certbot --nginx -d api.example.com -d www.example.com

# Test renewal
sudo certbot renew --dry-run

# certbot installs a systemd timer that renews automatically
systemctl list-timers | grep certbot</code></pre>

<p><strong>Caddy</strong> is even simpler &mdash; HTTPS is automatic with no flags:</p>

<pre><code># /etc/caddy/Caddyfile
api.example.com {
  reverse_proxy localhost:4000
}
# That&apos;s it. Caddy obtains + renews certs in the background.</code></pre>

<p><strong>Traefik</strong> handles ACME similarly for Docker/Kubernetes setups. For Kubernetes specifically, <strong>cert&ndash;manager</strong> is the standard operator that requests + renews Let&rsquo;s Encrypt certs into Secrets that Ingress controllers consume.</p>

<p>Renewal failures are the #1 production TLS outage cause &mdash; monitor cert expiry with <strong>Better Uptime</strong>, <strong>Checkly</strong>, or a self&ndash;hosted check; alert &gt;2 weeks before expiry.</p>'''


ANSWERS[38] = r'''<p>A <strong>reverse proxy</strong> sits between the internet and your Node app, terminating TLS, serving static files, load&ndash;balancing across multiple Node processes, and adding security headers. Nginx is the classic choice; <strong>Caddy</strong> and <strong>Traefik</strong> are simpler 2026 alternatives that handle Let&rsquo;s Encrypt automatically.</p>

<pre><code># /etc/nginx/sites-available/api.example.com
server {
  listen 80;
  server_name api.example.com;
  return 301 https://$host$request_uri;
}

server {
  listen 443 ssl http2;
  server_name api.example.com;

  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
  add_header Strict-Transport-Security &quot;max-age=63072000; includeSubDomains&quot; always;

  # Rate limit (basic)
  limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
  limit_req zone=api burst=40 nodelay;

  # Static frontend
  location / {
    root /var/www/web/dist;
    try_files $uri /index.html;
  }

  # Proxy /api &rarr; Node on :4000
  location /api/ {
    proxy_pass http://127.0.0.1:4000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection &quot;upgrade&quot;;       # WebSocket support
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 60s;
  }
}</code></pre>

<p>Set <code>app.set(&quot;trust proxy&quot;, 1)</code> in Express so <code>req.ip</code> reads <code>X-Forwarded-For</code> correctly. For 2026 self&ndash;hosting, prefer <strong>Caddy</strong> (config below is one&ndash;tenth the lines + auto&ndash;TLS):</p>

<pre><code>api.example.com {
  reverse_proxy /api/* localhost:4000
  root * /var/www/web/dist
  file_server
}</code></pre>'''


ANSWERS[39] = r'''<p><strong>PM2</strong> is a process manager for Node.js that keeps your app running in production &mdash; it restarts on crash, runs multiple instances behind a load balancer, log&ndash;rotates, and offers zero&ndash;downtime reloads. Most managed platforms (Render, Fly.io, Vercel) make PM2 unnecessary, but it&rsquo;s standard on bare VMs or VPS deployments.</p>

<pre><code>pnpm add -g pm2

# Start a Node app
pm2 start dist/index.js --name api

# Cluster mode &mdash; spawn N instances across CPU cores
pm2 start dist/index.js --name api -i max
# or fixed count:
pm2 start dist/index.js --name api -i 4

# View &amp; manage
pm2 list
pm2 logs api --lines 200
pm2 monit                      # real-time CPU + memory
pm2 restart api
pm2 reload api                 # zero-downtime restart in cluster mode
pm2 stop api &amp;&amp; pm2 delete api

# Persist across reboots
pm2 startup                    # generates systemd unit
pm2 save                       # snapshot current process list</code></pre>

<p>For repeatable deployments use an <strong>ecosystem file</strong>:</p>

<pre><code>// ecosystem.config.js
module.exports = {
  apps: [{
    name: &quot;api&quot;,
    script: &quot;dist/index.js&quot;,
    instances: &quot;max&quot;,
    exec_mode: &quot;cluster&quot;,
    max_memory_restart: &quot;500M&quot;,
    env_production: { NODE_ENV: &quot;production&quot;, PORT: 4000 }
  }]
};
// pm2 start ecosystem.config.js --env production</code></pre>

<p>2026 alternatives: in containers + Kubernetes you typically run <em>one</em> Node process per container and let the orchestrator handle restarts and scaling &mdash; no PM2 needed. <strong>systemd</strong> directly is also valid for simple VPS deployments. PM2 shines on traditional VMs where you want clustering + log mgmt without containers.</p>'''


ANSWERS[40] = r'''<p><strong>Load balancing</strong> spreads incoming requests across multiple instances of your app so no single server is overwhelmed and a single failure doesn&rsquo;t take down the service. Three layers exist:</p>

<ul>
<li><strong>DNS / global</strong> &mdash; Cloudflare, Route 53, NS1 route users to the nearest healthy region.</li>
<li><strong>Layer 7 (HTTP) load balancer</strong> &mdash; Nginx, HAProxy, AWS ALB, GCP Cloud Load Balancing route by path/host/header.</li>
<li><strong>Process&ndash;level</strong> &mdash; PM2 cluster mode or Node&rsquo;s <code>cluster</code> module spawns N processes per CPU core to use all cores (Node is single&ndash;threaded by default).</li>
</ul>

<p>For most MERN apps in 2026 the answer is &ldquo;your platform does it&rdquo;:</p>

<ul>
<li><strong>Vercel / Netlify / Cloudflare Pages</strong> &mdash; auto&ndash;scaled global edge.</li>
<li><strong>Fly.io</strong> &mdash; runs N instances per region; built&ndash;in load balancer routes to nearest healthy. Add machines with <code>fly scale count 4</code>.</li>
<li><strong>Render / Railway</strong> &mdash; horizontal scale via dashboard slider; load balancer included.</li>
<li><strong>Kubernetes</strong> &mdash; Service object + Ingress controller (Nginx/Traefik/Istio).</li>
</ul>

<pre><code># Nginx upstream &mdash; round robin between Node instances
upstream api {
  server 10.0.0.1:4000;
  server 10.0.0.2:4000;
  server 10.0.0.3:4000 backup;
  keepalive 32;
}
server {
  location /api/ {
    proxy_pass http://api/;
  }
}</code></pre>

<p>Critical for stateful concerns: WebSocket connections must use <strong>sticky sessions</strong> or a Redis pub/sub adapter (Socket.IO Redis adapter) so messages reach all servers. Use <strong>health check endpoints</strong> (<code>/healthz</code>) so the LB removes failing nodes automatically. Make Node apps <strong>stateless</strong> &mdash; sessions in Redis, files in S3 &mdash; so any instance can serve any request.</p>'''


ANSWERS[41] = r'''<p>Performance monitoring for MERN means watching three layers: <strong>frontend Real User Metrics</strong> (what real users experience), <strong>backend APM</strong> (request latency, error rate, traces), and <strong>database</strong> (slow queries, index health, replication lag).</p>

<p><strong>Frontend RUM &mdash; Core Web Vitals + custom events:</strong></p>
<ul>
<li><strong>Vercel Speed Insights</strong>, <strong>Sentry Performance</strong>, <strong>Datadog RUM</strong>, <strong>SpeedCurve</strong>, <strong>Cloudflare Web Analytics</strong> &mdash; track LCP, INP, CLS per route.</li>
<li>Lab tools: <strong>Lighthouse CI</strong> in GitHub Actions to fail PRs that regress.</li>
</ul>

<p><strong>Backend APM &mdash; OpenTelemetry is the 2026 standard:</strong></p>

<pre><code>pnpm add @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node \
         @opentelemetry/exporter-trace-otlp-http</code></pre>

<pre><code>// src/otel.ts &mdash; require this BEFORE express
import { NodeSDK } from &quot;@opentelemetry/sdk-node&quot;;
import { getNodeAutoInstrumentations } from &quot;@opentelemetry/auto-instrumentations-node&quot;;

new NodeSDK({
  serviceName: &quot;api&quot;,
  instrumentations: [getNodeAutoInstrumentations()]
}).start();</code></pre>

<p>OTel ships traces to <strong>Datadog</strong>, <strong>Honeycomb</strong>, <strong>New Relic</strong>, <strong>Sentry</strong>, <strong>Axiom</strong>, <strong>Grafana Tempo</strong> &mdash; pick one. Auto&ndash;instrumentation captures Express, Mongo, HTTP, Redis spans automatically.</p>

<p><strong>Database &mdash; Atlas Performance Advisor + Query Insights:</strong></p>
<ul>
<li>Atlas dashboard shows ops/sec, slow query log, suggests missing indexes.</li>
<li>Set up alerts for replication lag, oplog window, connection saturation.</li>
</ul>

<p>Track the four <strong>RED</strong> metrics (Rate, Errors, Duration) per service. Define <strong>SLOs</strong> (e.g., 99.9% of requests &lt;500ms) and use burn&ndash;rate alerts via Datadog or Grafana.</p>'''


ANSWERS[42] = r'''<p>MERN apps emit logs at every layer; pick a structured logger and ship to a central platform.</p>

<p><strong>Logger &mdash; pino is the 2026 default for Node.js:</strong> fast, JSON output, ecosystem of plugins. Winston is the older alternative, still common.</p>

<pre><code>pnpm add pino pino-http</code></pre>

<pre><code>import pino from &quot;pino&quot;;
import pinoHttp from &quot;pino-http&quot;;

export const log = pino({
  level: process.env.LOG_LEVEL ?? &quot;info&quot;,
  redact: [&quot;req.headers.authorization&quot;, &quot;*.password&quot;]
});

app.use(pinoHttp({ logger: log }));     // structured per-request logs
log.info({ userId, sku }, &quot;order created&quot;);</code></pre>

<p><strong>Centralized log platforms (pick one):</strong></p>

<ul>
<li><strong>Datadog Logs</strong> &mdash; pairs with Datadog APM, expensive at scale.</li>
<li><strong>Better Stack (formerly Logtail)</strong> &mdash; great DX, fair pricing.</li>
<li><strong>Axiom</strong> &mdash; cheap log aggregation with SQL queries.</li>
<li><strong>Grafana Loki</strong> &mdash; open source; pairs with Grafana Cloud or self&ndash;hosted.</li>
<li><strong>New Relic Logs</strong>, <strong>Splunk</strong>, <strong>Sumo Logic</strong> &mdash; enterprise.</li>
<li><strong>AWS CloudWatch</strong>, <strong>GCP Cloud Logging</strong>, <strong>Azure Monitor</strong> &mdash; native cloud.</li>
<li><strong>Sentry</strong> &mdash; specifically for errors and exceptions, not general logs.</li>
<li><strong>Loggly</strong> / <strong>Papertrail</strong> &mdash; older but still used.</li>
</ul>

<p>Best practices: <strong>structured JSON</strong> always (no string concat); <strong>request IDs</strong> propagated across services for tracing; <strong>redact secrets and PII</strong> at the logger level (<code>redact</code> option above); <strong>log levels</strong> &mdash; <code>error</code> always, <code>warn</code> for unusual but recoverable, <code>info</code> for major events, <code>debug</code> off in production. Pair logs with <strong>OpenTelemetry traces</strong> via the same request ID for full visibility.</p>'''


ANSWERS[43] = r'''<p><strong>Loggly</strong> (now part of SolarWinds) is a hosted log management service &mdash; you ship logs to it, search and alert on them via a web UI. It&rsquo;s an older option in 2026; modern teams usually pick <strong>Better Stack</strong>, <strong>Axiom</strong>, <strong>Datadog Logs</strong>, or <strong>Grafana Cloud Logs</strong>. The setup pattern is similar across all of them.</p>

<pre><code>pnpm add winston winston-loggly-bulk
# or with pino + a transport</code></pre>

<pre><code>// src/log.ts &mdash; Winston + Loggly
import winston from &quot;winston&quot;;
import { Loggly } from &quot;winston-loggly-bulk&quot;;

const log = winston.createLogger({
  level: &quot;info&quot;,
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new Loggly({
      token: process.env.LOGGLY_TOKEN,
      subdomain: process.env.LOGGLY_SUBDOMAIN,
      tags: [&quot;node&quot;, &quot;api&quot;, process.env.NODE_ENV],
      json: true
    })
  ]
});

log.info(&quot;User signed up&quot;, { userId, email });
log.error(&quot;Payment failed&quot;, { orderId, error });</code></pre>

<p>The 2026 alternative pattern uses <strong>pino</strong> + <strong>OpenTelemetry log exporter</strong> + a modern aggregator:</p>

<pre><code># Better Stack (Logtail-style HTTP source)
pnpm add @logtail/pino
# pino transport ships JSON to Better Stack&apos;s ingest URL

# Or just pipe stdout to your platform
# Most platforms (Vercel, Fly, Render) capture stdout/stderr automatically
# and forward to their integrated log viewer or to Datadog/Axiom/etc.</code></pre>

<p>Whatever you pick, the rules are the same: <strong>structured JSON</strong>, <strong>redact secrets</strong>, <strong>request IDs</strong> for cross&ndash;service tracing, <strong>retention &gt;14 days</strong> for incident investigation, <strong>alerts</strong> on error rates rather than individual log lines. Loggly itself is fine but feels dated; for a new project pick a 2026&ndash;native tool.</p>'''


ANSWERS[44] = r'''<p>CI/CD = <strong>Continuous Integration</strong> (run tests on every commit) + <strong>Continuous Deployment</strong> (auto&ndash;deploy passing builds). The 2026 default is <strong>GitHub Actions</strong> for both; <strong>GitLab CI</strong>, <strong>CircleCI</strong>, and <strong>Buildkite</strong> are alternatives.</p>

<pre><code># .github/workflows/ci.yml
name: CI
on:
  push: { branches: [main] }
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck
      - run: pnpm test
      - run: pnpm build

  deploy:
    needs: test
    if: github.ref == &apos;refs/heads/main&apos;
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env: { FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }} }</code></pre>

<p>Deployment targets:</p>

<ul>
<li><strong>Frontend (React/Next.js)</strong> &rarr; <strong>Vercel</strong>, <strong>Netlify</strong>, <strong>Cloudflare Pages</strong> &mdash; all auto&ndash;deploy on push, give you preview URLs per PR.</li>
<li><strong>API (Node/Express)</strong> &rarr; <strong>Fly.io</strong>, <strong>Render</strong>, <strong>Railway</strong>, <strong>Cloud Run</strong>, <strong>AWS App Runner</strong> &mdash; deploy via CLI, Docker image, or git push.</li>
<li><strong>Database</strong> &rarr; <strong>MongoDB Atlas</strong> &mdash; usually unchanged across deploys; migrations run as a CI step.</li>
</ul>

<p>Modern best practices: <strong>preview deploys</strong> per PR (Vercel does this automatically), <strong>trunk&ndash;based development</strong> with feature flags via <strong>Statsig</strong>/<strong>GrowthBook</strong>/<strong>LaunchDarkly</strong>, <strong>required status checks</strong> on the main branch, <strong>signed builds</strong> via <strong>Sigstore</strong>/<strong>cosign</strong>, and tracking <strong>DORA metrics</strong> (deploy frequency, lead time, MTTR, change failure rate).</p>'''


ANSWERS[45] = r'''<p><strong>Docker</strong> packages your app + its dependencies + a slice of OS into an immutable image, then runs that image as a container. The big wins: identical artifact across dev/staging/prod, easy horizontal scale, no &ldquo;works on my machine&rdquo;, and a single deployable unit each platform (Kubernetes, Cloud Run, ECS) consumes.</p>

<p>For a MERN app you usually have three containers in dev (Mongo, API, Web) and two deployed (API; the React build is static + on a CDN).</p>

<pre><code># Dockerfile &mdash; multi-stage Node API
FROM node:22-alpine AS base
WORKDIR /app
RUN corepack enable

FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM deps AS build
COPY . .
RUN pnpm build

FROM base AS runtime
ENV NODE_ENV=production
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist          ./dist
COPY package.json ./
USER node                          # don&apos;t run as root
EXPOSE 4000
CMD [&quot;node&quot;, &quot;dist/index.js&quot;]</code></pre>

<pre><code># Build &amp; run
docker build -t my-api:latest .
docker run --rm -p 4000:4000 --env-file .env my-api:latest</code></pre>

<p>Why containerize a MERN app:</p>

<ul>
<li><strong>Reproducible</strong> &mdash; same image runs locally, in CI, and on any cloud.</li>
<li><strong>Platform agnostic</strong> &mdash; Cloud Run, ECS, Kubernetes, Fly.io, Railway all take a Docker image as input.</li>
<li><strong>Smaller blast radius</strong> &mdash; container isolation, capability dropping, read&ndash;only filesystems harden the deployment.</li>
<li><strong>Tooling alignment</strong> &mdash; OpenTelemetry collectors, Prometheus, log shippers all standardize on container metadata.</li>
</ul>

<p>2026 alternatives: many teams skip Docker for greenfield projects and use <strong>Buildpacks</strong> (Cloud Native Buildpacks, Paketo), <strong>Nixpacks</strong> (Railway), or platform&ndash;native builders (Render, Fly.io detect Node automatically). For most simple MERN APIs you don&rsquo;t need to write a Dockerfile yourself.</p>'''


ANSWERS[46] = r'''<p>A good Dockerfile for a Node API is a <strong>multi&ndash;stage build</strong>: separate stages for installing deps, building TS, and the slim runtime. This keeps the production image small (typically &lt;200MB) and excludes dev dependencies + source maps + build tools.</p>

<pre><code># syntax=docker/dockerfile:1.7
FROM node:22-alpine AS base
WORKDIR /app
RUN corepack enable

# 1. Install dependencies (cached layer when lockfile unchanged)
FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod=false

# 2. Build (TS compile / Next build)
FROM deps AS build
COPY . .
RUN pnpm build

# 3. Slim runtime
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod
COPY --from=build /app/dist ./dist
USER node
EXPOSE 4000
HEALTHCHECK CMD node -e &quot;fetch(&apos;http://127.0.0.1:4000/health&apos;).then(r=&gt;process.exit(r.ok?0:1))&quot;
CMD [&quot;node&quot;, &quot;dist/index.js&quot;]</code></pre>

<p>Companion <code>.dockerignore</code> (mandatory):</p>

<pre><code>node_modules
dist
.git
.env*
**/*.test.ts
coverage
.DS_Store</code></pre>

<p>Best practices: <strong>specific base image tag</strong> (<code>node:22-alpine</code>, never <code>node:latest</code>); <strong>distroless or alpine</strong> for small attack surface (<strong>chainguard images</strong> for serious security); <strong>non&ndash;root user</strong> (<code>USER node</code>); <strong>BuildKit cache mounts</strong> for fast rebuilds; <strong>layer order</strong> &mdash; copy lockfile and run install <em>before</em> copying app code so dep changes don&rsquo;t bust the cache; <strong>multi&ndash;arch builds</strong> via <code>docker buildx build --platform linux/amd64,linux/arm64</code> for Apple Silicon + Linux servers.</p>'''


ANSWERS[47] = r'''<p><strong>Docker Compose</strong> orchestrates multi&ndash;container stacks for local development &mdash; one YAML file describes your whole MERN environment (Mongo + API + Web + Redis), and <code>docker compose up</code> brings it all up with a shared network.</p>

<pre><code># docker-compose.yml
services:
  mongo:
    image: mongo:7
    restart: unless-stopped
    ports: [&quot;27017:27017&quot;]
    volumes: [mongo-data:/data/db]
    environment:
      MONGO_INITDB_ROOT_USERNAME: dev
      MONGO_INITDB_ROOT_PASSWORD: dev

  redis:
    image: redis:7-alpine
    ports: [&quot;6379:6379&quot;]

  api:
    build: ./apps/api
    ports: [&quot;4000:4000&quot;]
    depends_on: [mongo, redis]
    environment:
      MONGO_URI: mongodb://dev:dev@mongo:27017/myapp?authSource=admin
      REDIS_URL: redis://redis:6379
      JWT_SECRET: dev-only
    volumes:
      - ./apps/api/src:/app/src     # hot reload in dev
    command: pnpm dev

  web:
    build: ./apps/web
    ports: [&quot;5173:5173&quot;]
    depends_on: [api]
    environment:
      VITE_API_URL: http://localhost:4000
    volumes:
      - ./apps/web/src:/app/src

volumes:
  mongo-data:</code></pre>

<pre><code>docker compose up -d              # start all services in background
docker compose logs -f api        # follow API logs
docker compose exec api sh        # shell into API container
docker compose down               # stop &amp; remove containers
docker compose down -v            # also wipe volumes (Mongo data!)</code></pre>

<p>Why it&rsquo;s great for MERN dev: a new teammate clones the repo, runs <code>docker compose up</code>, and has the entire stack running in minutes &mdash; no need to install Mongo or Redis natively. The shared Docker network lets containers talk via service name (<code>mongo:27017</code>, <code>redis:6379</code>).</p>

<p>For production, Compose can run on a single VM via <strong>Docker Swarm</strong> or <strong>Compose v2</strong> on a Linux host, but most teams move to <strong>Kubernetes</strong>, <strong>Cloud Run</strong>, <strong>ECS</strong>, or <strong>Fly.io</strong> at scale &mdash; Compose is primarily a local&ndash;dev tool.</p>'''


ANSWERS[48] = r'''<p><strong>Kubernetes</strong> (K8s) is the open&ndash;source orchestrator for containerized applications &mdash; it runs containers across a cluster of machines, schedules them, restarts failed ones, scales horizontally, rolls out new versions safely, and exposes them to the network. Originally from Google, now CNCF&ndash;governed and the de&ndash;facto standard for large&ndash;scale container deployment.</p>

<p>For MERN apps, <strong>most teams should not start with Kubernetes</strong> &mdash; it&rsquo;s a lot of operational complexity. Use <strong>Cloud Run</strong>, <strong>Fly.io</strong>, <strong>Render</strong>, <strong>Railway</strong>, <strong>App Runner</strong>, or <strong>Heroku</strong> first; reach for K8s when you genuinely need its features (multi&ndash;region multi&ndash;cloud, complex traffic routing, GPU pools, multi&ndash;tenant platform).</p>

<p>When you do need K8s, the building blocks:</p>

<ul>
<li><strong>Pod</strong> &mdash; one or more containers running together (sharing network + storage). The atom of K8s.</li>
<li><strong>Deployment</strong> &mdash; declares N replicas of a Pod with rolling update strategy.</li>
<li><strong>Service</strong> &mdash; stable internal DNS name + load&ndash;balanced virtual IP for a set of Pods.</li>
<li><strong>Ingress</strong> &mdash; HTTP routing (host/path) to Services, terminating TLS. Implemented by Nginx, Traefik, Istio.</li>
<li><strong>ConfigMap / Secret</strong> &mdash; configuration + sensitive values mounted into Pods.</li>
<li><strong>StatefulSet</strong> &mdash; Pods with stable identity + persistent storage (Mongo, Postgres).</li>
<li><strong>Namespace</strong> &mdash; logical isolation (dev/staging/prod, per&ndash;team).</li>
</ul>

<p>Managed control planes: <strong>EKS</strong> (AWS), <strong>GKE</strong> (Google), <strong>AKS</strong> (Azure), <strong>DigitalOcean Kubernetes</strong>, <strong>Linode LKE</strong>, <strong>Civo</strong>. They handle the masters; you manage the worker nodes (or use Fargate / GKE Autopilot for serverless nodes too).</p>

<p>Deploy via <strong>kubectl apply</strong>, <strong>Helm</strong> charts, <strong>Kustomize</strong>, or GitOps with <strong>ArgoCD</strong>/<strong>Flux</strong>. Pair with <strong>Prometheus</strong> + <strong>Grafana</strong> for metrics, <strong>Loki</strong>/<strong>Datadog</strong> for logs, <strong>Istio</strong>/<strong>Linkerd</strong> for service mesh.</p>'''


ANSWERS[49] = r'''<p>A Kubernetes <strong>Deployment</strong> manifest declares a desired state (image, replicas, env, resources). The control plane converges actual state to match.</p>

<pre><code># k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels: { app: api }
spec:
  replicas: 3
  selector: { matchLabels: { app: api } }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: ghcr.io/me/api:1.4.2
          ports: [{ containerPort: 4000 }]
          env:
            - name: MONGO_URI
              valueFrom: { secretKeyRef: { name: api-secrets, key: mongo-uri } }
            - name: NODE_ENV
              value: production
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
          livenessProbe:
            httpGet: { path: /health, port: 4000 }
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet: { path: /ready, port: 4000 }
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata: { name: api }
spec:
  selector: { app: api }
  ports: [{ port: 80, targetPort: 4000 }]
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls: [{ hosts: [api.example.com], secretName: api-tls }]
  rules:
    - host: api.example.com
      http:
        paths:
          - { path: /, pathType: Prefix, backend: { service: { name: api, port: { number: 80 } } } }</code></pre>

<pre><code>kubectl apply -f k8s/
kubectl get pods,svc,ingress
kubectl logs -f deploy/api
kubectl rollout status deploy/api</code></pre>

<p>Always set <strong>resource requests/limits</strong>, <strong>liveness + readiness probes</strong>, and pair with a <strong>HorizontalPodAutoscaler</strong> for auto&ndash;scaling. Manage the YAML with <strong>Helm</strong>, <strong>Kustomize</strong>, or <strong>ArgoCD</strong> for real projects.</p>'''


ANSWERS[50] = r'''<p><strong>Helm</strong> is the package manager for Kubernetes &mdash; the equivalent of <code>npm</code> but for K8s manifests. A <strong>chart</strong> is a templated bundle of YAML; you install it with values overrides for your environment.</p>

<pre><code># Install the Helm CLI
brew install helm                # macOS
curl -fsSL https://get.helm.sh/... # Linux

# Add a public repo &amp; install something
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install my-mongo bitnami/mongodb --set auth.rootPassword=secret

# Manage releases
helm list
helm upgrade my-mongo bitnami/mongodb --set replicaCount=3
helm uninstall my-mongo</code></pre>

<p>For your own MERN app, generate a chart skeleton:</p>

<pre><code>helm create my-api
# creates my-api/
#   Chart.yaml         &mdash; metadata
#   values.yaml        &mdash; default values
#   templates/         &mdash; templated K8s manifests (Deployment, Service, Ingress)
#   templates/_helpers.tpl

# Install it
helm install api ./my-api -f values.production.yaml

# Per-environment values files
helm install api ./my-api -f values.staging.yaml --namespace staging
helm install api ./my-api -f values.production.yaml --namespace prod

# Upgrade with new image tag
helm upgrade api ./my-api --set image.tag=1.4.2 -f values.production.yaml</code></pre>

<p>Why Helm pays off:</p>

<ul>
<li><strong>Templating</strong> &mdash; one chart, many environments via values overrides.</li>
<li><strong>Versioning + rollback</strong> &mdash; <code>helm rollback api 4</code> reverts to a previous revision instantly.</li>
<li><strong>Dependencies</strong> &mdash; depend on community charts (Redis, Postgres, ingress&ndash;nginx, cert&ndash;manager) and pull them in via <code>requirements.yaml</code>.</li>
<li><strong>Distribution</strong> &mdash; ship your app as a chart for users to install on their own clusters.</li>
</ul>

<p>2026 alternatives: <strong>Kustomize</strong> (no templating &mdash; pure YAML overlays, simpler) is built into kubectl; <strong>cdk8s</strong> generates K8s manifests from TypeScript/Python; <strong>Pulumi</strong> manages K8s + clouds with real code. Most teams use Helm for community charts and Kustomize for in&ndash;house apps.</p>'''

ANSWERS[51] = r'''<p>A <strong>CDN (Content Delivery Network)</strong> is a globally distributed network of edge servers that cache your static assets &mdash; HTML, JS bundles, CSS, images, fonts, video &mdash; close to users so requests don&rsquo;t round&ndash;trip to your origin. The result: faster loads, lower bandwidth bills, and origin protection against traffic spikes.</p>

<p>For a MERN app the typical split:</p>

<ul>
<li><strong>Static frontend</strong> (Next.js build output, Vite dist) &mdash; served from the CDN&rsquo;s edge.</li>
<li><strong>API requests</strong> &mdash; hit the origin directly, or CDN passes them through with caching headers.</li>
<li><strong>User uploads</strong> &mdash; stored in S3/R2/GCS, served via a CDN distribution.</li>
</ul>

<p>The dominant 2026 choices: <strong>Cloudflare</strong> (free tier, vast network, Workers + R2 + Pages), <strong>Fastly</strong> (developer&ndash;friendly, instant purge, Compute@Edge), <strong>Vercel</strong> (Next.js&ndash;native), <strong>Netlify</strong>, <strong>AWS CloudFront</strong>, <strong>Bunny.net</strong> (cheapest), <strong>Akamai</strong> (enterprise).</p>

<pre><code>// Caching headers your origin sends &mdash; CDN respects these
res.setHeader(&quot;Cache-Control&quot;, &quot;public, max-age=31536000, immutable&quot;);
// hashed assets like /assets/app.a1b2c3.js can be cached forever

res.setHeader(&quot;Cache-Control&quot;, &quot;public, max-age=0, s-maxage=60, stale-while-revalidate=300&quot;);
// HTML &mdash; revalidate on every request, but CDN serves stale for 5 min while refreshing</code></pre>

<p>Key features to use: <strong>cache tags</strong> for surgical invalidation, <strong>image optimization</strong> at the edge (Cloudflare Images, Vercel/Next Image), <strong>edge functions</strong> (Cloudflare Workers, Vercel Edge) for personalization without losing cacheability, <strong>HTTP/3 + Brotli/Zstd compression</strong>, <strong>WAF + DDoS protection</strong>. Done well, a CDN turns a global app from 800ms TTFB into 50ms TTFB &mdash; the single biggest perf win you can ship.</p>'''


ANSWERS[52] = r'''<p>To deploy React static assets to a CDN, build the production bundle then upload the output directory to a CDN&ndash;backed origin. Modern hosts (<strong>Vercel, Netlify, Cloudflare Pages</strong>) automate this end&ndash;to&ndash;end &mdash; you push to git, they build, they fan out to their global edge.</p>

<pre><code># Vite / Create React App / Next.js static export
npm run build       # outputs to dist/ or build/ or out/

# Vercel: zero config &mdash; auto&ndash;detects the framework
vercel --prod

# Cloudflare Pages: same idea
wrangler pages deploy ./dist --project-name=my-app

# Netlify
netlify deploy --prod --dir=dist

# Manual S3 + CloudFront route
aws s3 sync ./dist s3://my-app-prod --delete
aws cloudfront create-invalidation --distribution-id E123 --paths &quot;/*&quot;</code></pre>

<p>The bundler should already <strong>fingerprint</strong> filenames (<code>app.a1b2c3.js</code>). Hashed assets get aggressive caching, while <code>index.html</code> stays short&ndash;cached so deploys propagate fast:</p>

<pre><code># Vercel / Netlify _headers / Cloudflare Pages _headers
/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*.html
  Cache-Control: public, max-age=0, must-revalidate</code></pre>

<p>Things to verify after first deploy: HTTPS via Let&rsquo;s Encrypt or the host&rsquo;s cert, automatic Brotli/Zstd compression, HTTP/3, image optimization (Vercel Image, Cloudflare Images, Netlify Image CDN), preview deploys per pull request, custom domain DNS via CNAME or Cloudflare proxy.</p>

<p>For Next.js specifically, <strong>Vercel</strong> handles SSR/RSC/ISR + static at the edge transparently; <strong>Cloudflare Pages + @cloudflare/next-on-pages</strong> or <strong>OpenNext</strong> achieve similar on Cloudflare; <strong>Netlify</strong> ships an official Next.js runtime. Pick whichever your team already uses for git &mdash; the friction matters more than the marginal feature differences.</p>'''


ANSWERS[53] = r'''<p><strong>Redis</strong> is an in&ndash;memory key/value store you put in front of your database for caching, sessions, rate&ndash;limit counters, and pub/sub. Setting it up for a MERN app in 2026:</p>

<pre><code># Local development &mdash; Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Production &mdash; managed service
# Upstash (serverless, per-request pricing, free tier)
# Redis Cloud (official, by Redis Labs)
# AWS ElastiCache, Google Memorystore, Azure Cache for Redis
# Railway, Render, Fly.io for simple managed</code></pre>

<p>Connect from Node with <strong>ioredis</strong> (richer features) or <strong>node-redis</strong> (official):</p>

<pre><code>import Redis from &quot;ioredis&quot;;
export const redis = new Redis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: 3,
  enableReadyCheck: true
});

// Cache&ndash;aside pattern
async function getUser(id: string) {
  const key = `user:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const user = await User.findById(id).lean();
  if (user) await redis.setex(key, 300, JSON.stringify(user));  // 5 min TTL
  return user;
}

// Invalidate on update
async function updateUser(id: string, patch: any) {
  const u = await User.findByIdAndUpdate(id, patch, { new: true });
  await redis.del(`user:${id}`);
  return u;
}</code></pre>

<p>Use Redis for: query result caching, sessions, rate&ndash;limit counters (with Lua scripts or <strong>Upstash Ratelimit</strong>), real&ndash;time presence, BullMQ job queues, Socket.io adapter (multi&ndash;pod fanout), pub/sub for cache invalidation across nodes. Avoid putting hot, sharded, or sensitive&ndash;at&ndash;rest data in Redis without <code>requirepass</code> + TLS.</p>

<p>For 2026 serverless apps <strong>Upstash Redis</strong> is the default &mdash; HTTP&ndash;based REST API works from edge functions (Cloudflare Workers, Vercel Edge) where TCP connections aren&rsquo;t allowed.</p>'''


ANSWERS[54] = r'''<p><strong>Caching</strong> stores the result of an expensive computation or fetch so subsequent requests return instantly. The performance win comes from skipping the slow path: a Mongo query that takes 80ms drops to 1ms when served from Redis; an API response cached at the CDN drops from 200ms to 30ms; a React component memoized doesn&rsquo;t re&ndash;render on every parent change.</p>

<p>Caches exist at <strong>multiple layers</strong> in a typical MERN stack &mdash; each one cuts work for the layer below it:</p>

<table>
<tr><th>Layer</th><th>Tool</th><th>Use case</th></tr>
<tr><td>Browser</td><td>HTTP cache, IndexedDB, localStorage</td><td>Static assets, recent API responses</td></tr>
<tr><td>CDN / edge</td><td>Cloudflare, Fastly, Vercel</td><td>Static files, public API responses</td></tr>
<tr><td>Application</td><td>In&ndash;process LRU (lru&ndash;cache)</td><td>Per&ndash;process hot data, low TTL</td></tr>
<tr><td>Distributed</td><td>Redis, Memcached, Dragonfly</td><td>Shared across pods, sessions, rate limits</td></tr>
<tr><td>Database</td><td>Mongo working set in RAM</td><td>Hot pages already in memory</td></tr>
<tr><td>Client state</td><td>TanStack Query, SWR, Apollo</td><td>API responses with dedupe + revalidation</td></tr>
</table>

<p>The hard part isn&rsquo;t adding caches &mdash; it&rsquo;s <strong>invalidation</strong>. Three strategies:</p>

<ul>
<li><strong>Time&ndash;based (TTL)</strong> &mdash; simplest, accept staleness for a window. Default for most data.</li>
<li><strong>Event&ndash;based</strong> &mdash; on write, delete or update affected keys. Risk: missed keys.</li>
<li><strong>Tag&ndash;based</strong> &mdash; group keys under tags (Cloudflare Cache Tags, Next.js <code>revalidateTag</code>) and purge by tag.</li>
</ul>

<p>Cache the slow stuff first: aggregate dashboards, list endpoints with sorting, fan&ndash;out queries. Don&rsquo;t cache user&ndash;specific writes, real&ndash;time prices, anything legally sensitive without thought. Always measure: a cache that returns stale or wrong data is worse than no cache.</p>'''


ANSWERS[55] = r'''<p><strong>Server&ndash;side rendering (SSR)</strong> generates HTML on the server for each request, then hydrates with JavaScript on the client. The trade against client&ndash;side rendering: faster first paint, real SEO content for crawlers (including AI agents like OAI&ndash;SearchBot, PerplexityBot, ClaudeBot), better social link previews, and a usable page even before JS loads.</p>

<p>The dominant 2026 choice for SSR React is <strong>Next.js 15 with the App Router and React Server Components</strong>:</p>

<pre><code>// app/products/[id]/page.tsx &mdash; rendered on the server
export default async function ProductPage({ params }: { params: Promise&lt;{ id: string }&gt; }) {
  const { id } = await params;
  const product = await getProduct(id);   // runs on server, no JS shipped
  return (
    &lt;article&gt;
      &lt;h1&gt;{product.name}&lt;/h1&gt;
      &lt;p&gt;{product.description}&lt;/p&gt;
      &lt;AddToCart productId={id} /&gt;        {/* client component island */}
    &lt;/article&gt;
  );
}

// app/products/[id]/loading.tsx &mdash; streaming Suspense fallback
export default function Loading() { return &lt;Skeleton /&gt;; }</code></pre>

<p>Other SSR options: <strong>Remix</strong> (now React Router 7) with nested routes + loaders, <strong>Astro</strong> for content&ndash;heavy sites with island hydration, <strong>TanStack Start</strong> (newer, framework&ndash;agnostic), <strong>Nuxt</strong> for Vue. For pure React without a framework, <code>renderToPipeableStream</code> wires up streaming SSR but you&rsquo;ll rebuild routing + data fetching yourself &mdash; rarely worth it.</p>

<p>Watch out for: <strong>hydration mismatches</strong> (server HTML must match what the client first renders), <strong>environment leaks</strong> (don&rsquo;t reference <code>window</code> in server code), <strong>cache headers</strong> (cache the HTML at the CDN with stale&ndash;while&ndash;revalidate), and <strong>data fetching</strong> (use <code>fetch</code> on the server, not a client library that assumes a browser). For mostly&ndash;static content, prefer <strong>SSG/ISR</strong> (build once, revalidate periodically) over per&ndash;request SSR &mdash; it&rsquo;s strictly cheaper and faster.</p>'''


ANSWERS[56] = r'''<p><strong>Next.js 15</strong> is the de&ndash;facto SSR framework for React. The App Router (default since v13) supports a mix of static, dynamic, and streaming routes side by side, with <strong>React Server Components</strong> as the foundation.</p>

<pre><code># Create + run
npx create-next-app@latest my-app --ts --tailwind --app --eslint
cd my-app
npm run dev    # http://localhost:3000</code></pre>

<pre><code>// app/page.tsx &mdash; server component by default
import { getProducts } from &quot;@/lib/db&quot;;
export const revalidate = 60;          // ISR: re-render every 60s

export default async function Home() {
  const products = await getProducts();  // server-side, zero JS shipped
  return (
    &lt;ul&gt;
      {products.map(p =&gt; &lt;li key={p._id}&gt;{p.name}&lt;/li&gt;)}
    &lt;/ul&gt;
  );
}

// app/api/products/route.ts &mdash; route handler (replaces /pages/api/*)
export async function GET() {
  return Response.json(await getProducts());
}

// app/products/[id]/page.tsx &mdash; dynamic route
export default async function P({ params }) {
  const { id } = await params;          // Next 15 params are async
  const p = await getProduct(id);
  return &lt;Detail product={p} /&gt;;
}</code></pre>

<p>Three rendering modes you pick per route:</p>

<ul>
<li><strong>Static</strong> (default) &mdash; rendered at build time, served from CDN.</li>
<li><strong>ISR</strong> &mdash; <code>export const revalidate = N</code> rebuilds in the background after N seconds, or <code>revalidatePath</code>/<code>revalidateTag</code> for on&ndash;demand.</li>
<li><strong>Dynamic SSR</strong> &mdash; whenever you read cookies, headers, or call a non&ndash;cached <code>fetch</code>, the route renders per request.</li>
</ul>

<p>Deploy to <strong>Vercel</strong> (zero config, native), <strong>Cloudflare Pages</strong> via <code>@cloudflare/next-on-pages</code> or <strong>OpenNext</strong>, <strong>Netlify</strong>, <strong>AWS Amplify</strong>, or self&ndash;host as a Node server (<code>next start</code>) behind nginx/Caddy. AI&ndash;crawler SEO and the &ldquo;works without JS&rdquo; guarantee come for free with the App Router &mdash; that&rsquo;s the main reason most new MERN projects start with Next.js in 2026.</p>'''


ANSWERS[57] = r'''<p><strong>GraphQL</strong> is a query language + runtime for APIs where the client describes exactly which fields it wants and the server returns just that. Instead of multiple REST endpoints (<code>/users/:id</code>, <code>/users/:id/posts</code>, <code>/posts/:id/comments</code>), you expose a single typed schema and the client composes requests:</p>

<pre><code># Schema (server defines what&apos;s available)
type User { id: ID!  name: String!  posts: [Post!]! }
type Post { id: ID!  title: String!  comments: [Comment!]! }
type Comment { id: ID!  text: String!  author: User! }
type Query { user(id: ID!): User }

# Client query (asks for exactly what it needs)
query {
  user(id: &quot;123&quot;) {
    name
    posts(limit: 5) { title  comments { text } }
  }
}</code></pre>

<p>Why teams reach for GraphQL in a MERN stack:</p>

<ul>
<li><strong>No over&ndash;/under&ndash;fetching</strong> &mdash; mobile clients on weak networks request only the fields they render.</li>
<li><strong>Single round&ndash;trip composition</strong> &mdash; one query for a screen instead of 4&ndash;5 REST calls.</li>
<li><strong>Strong typing</strong> &mdash; the schema is a contract; tools generate TypeScript types and React hooks automatically.</li>
<li><strong>Federation</strong> &mdash; multiple services compose into one schema (Apollo Federation, Hive Gateway, Cosmo).</li>
</ul>

<p>Trade&ndash;offs: caching is harder than REST (no URL identity), N+1 query problems are real (mitigate with <strong>DataLoader</strong>), arbitrary queries can be expensive (use <strong>persisted queries</strong> + complexity limits), and small teams often find REST/tRPC simpler.</p>

<p>2026 servers: <strong>Apollo Server</strong>, <strong>GraphQL Yoga</strong> (lightweight), <strong>Pothos</strong> (code&ndash;first TS schema). Clients: <strong>Apollo Client</strong>, <strong>urql</strong>, <strong>GraphQL Request</strong>, <strong>Relay</strong>. For purely TS&ndash;to&ndash;TS APIs <strong>tRPC</strong> often beats GraphQL with less ceremony.</p>'''


ANSWERS[58] = r'''<p><strong>Apollo Server</strong> wraps your resolvers and schema, exposes them at an HTTP endpoint, and integrates cleanly with Express. Setup in a MERN app:</p>

<pre><code>npm i @apollo/server @apollo/server/express4 graphql graphql-tag
        @as-integrations/express5 cors body-parser</code></pre>

<pre><code>// server.ts
import express from &quot;express&quot;;
import http from &quot;http&quot;;
import cors from &quot;cors&quot;;
import bodyParser from &quot;body-parser&quot;;
import { ApolloServer } from &quot;@apollo/server&quot;;
import { expressMiddleware } from &quot;@as-integrations/express5&quot;;
import { ApolloServerPluginDrainHttpServer } from &quot;@apollo/server/plugin/drainHttpServer&quot;;

const typeDefs = `#graphql
  type User { id: ID!  name: String!  email: String! }
  type Query { user(id: ID!): User  users: [User!]! }
  type Mutation { createUser(name: String!, email: String!): User! }
`;

const resolvers = {
  Query: {
    user: async (_, { id }) =&gt; await User.findById(id),
    users: async () =&gt; await User.find()
  },
  Mutation: {
    createUser: async (_, { name, email }) =&gt; await User.create({ name, email })
  }
};

const app = express();
const httpServer = http.createServer(app);
const server = new ApolloServer({
  typeDefs, resolvers,
  plugins: [ApolloServerPluginDrainHttpServer({ httpServer })]
});
await server.start();

app.use(&quot;/graphql&quot;,
  cors&lt;cors.CorsRequest&gt;(),
  bodyParser.json(),
  expressMiddleware(server, {
    context: async ({ req }) =&gt; ({ user: await authFromHeader(req) })
  })
);

await new Promise(r =&gt; httpServer.listen({ port: 4000 }, r));</code></pre>

<p>The <strong>context</strong> function runs per request &mdash; that&rsquo;s where you authenticate, attach the current user, and instantiate per&ndash;request DataLoaders to avoid N+1 queries. Apollo Sandbox at <code>http://localhost:4000/graphql</code> gives you a built&ndash;in IDE during development.</p>

<p>For production wire <strong>Apollo Studio</strong> or self&ndash;host with <strong>GraphQL Hive</strong> for schema registry, query analytics, and breaking&ndash;change detection. Add <strong>persisted queries</strong> + complexity/depth limits to prevent abusive clients. Standalone Yoga is a lighter alternative when you don&rsquo;t need Apollo&rsquo;s ecosystem.</p>'''


ANSWERS[59] = r'''<p><strong>Apollo Client</strong> manages GraphQL queries in React: cache, request dedup, optimistic updates, subscriptions, and SSR. Setup in a Vite or Next.js app:</p>

<pre><code>npm i @apollo/client graphql</code></pre>

<pre><code>// lib/apollo.ts
import { ApolloClient, InMemoryCache, HttpLink, from } from &quot;@apollo/client&quot;;
import { setContext } from &quot;@apollo/client/link/context&quot;;

const httpLink = new HttpLink({ uri: &quot;https://api.example.com/graphql&quot; });

const authLink = setContext((_, { headers }) =&gt; {
  const token = localStorage.getItem(&quot;token&quot;);
  return { headers: { ...headers, authorization: token ? `Bearer ${token}` : &quot;&quot; } };
});

export const client = new ApolloClient({
  link: from([authLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      User: { keyFields: [&quot;id&quot;] },                       // normalize by id
      Query: { fields: { posts: { merge: false } } }     // replace, don&apos;t merge
    }
  })
});

// main.tsx
&lt;ApolloProvider client={client}&gt;
  &lt;App /&gt;
&lt;/ApolloProvider&gt;</code></pre>

<pre><code>// Component using useQuery
import { gql, useQuery, useMutation } from &quot;@apollo/client&quot;;

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) { id  name  email }
  }
`;

function Profile({ id }: { id: string }) {
  const { data, loading, error } = useQuery(GET_USER, { variables: { id } });
  if (loading) return &lt;Spinner /&gt;;
  if (error)   return &lt;Err msg={error.message} /&gt;;
  return &lt;h1&gt;{data.user.name}&lt;/h1&gt;;
}</code></pre>

<p>Powerful features to use: <strong>optimistic responses</strong> for instant UI on mutations, <strong>cache redirects</strong> to avoid extra fetches, <strong>fragments</strong> for component&ndash;level field requirements, <strong>subscriptions</strong> over WebSocket for live data. For type safety run <strong>GraphQL Code Generator</strong> to produce <code>useQuery</code>/<code>useMutation</code> hooks typed from your schema.</p>

<p>Lighter 2026 alternatives: <strong>urql</strong> (smaller, GraphCache), <strong>graphql&ndash;request</strong> (just fetch + types) paired with TanStack Query, or <strong>Relay</strong> (Meta&rsquo;s heavy&ndash;duty client with compile&ndash;time guarantees).</p>'''


ANSWERS[60] = r'''<p><strong>Redux</strong> is a predictable state container. State lives in a single store, components read it via selectors, and updates happen only through dispatched <strong>actions</strong> handled by pure <strong>reducer</strong> functions. The shape is intentional: every state change is traceable, debuggable in time&ndash;travel devtools, and serializable for tests.</p>

<p>The modern (2026) way is <strong>Redux Toolkit (RTK)</strong> &mdash; it removes boilerplate and is the official recommendation:</p>

<pre><code>npm i @reduxjs/toolkit react-redux</code></pre>

<pre><code>// store/cartSlice.ts
import { createSlice, PayloadAction } from &quot;@reduxjs/toolkit&quot;;

interface CartState { items: { id: string; qty: number }[] }
const initialState: CartState = { items: [] };

const cartSlice = createSlice({
  name: &quot;cart&quot;,
  initialState,
  reducers: {
    add: (state, action: PayloadAction&lt;string&gt;) =&gt; {
      const item = state.items.find(i =&gt; i.id === action.payload);
      item ? item.qty++ : state.items.push({ id: action.payload, qty: 1 });
    },                                                       // Immer makes this safe
    remove: (state, action: PayloadAction&lt;string&gt;) =&gt; {
      state.items = state.items.filter(i =&gt; i.id !== action.payload);
    }
  }
});

export const { add, remove } = cartSlice.actions;
export default cartSlice.reducer;</code></pre>

<p>RTK gives you: <strong>createSlice</strong> for reducer + actions, <strong>configureStore</strong> with sensible defaults, <strong>RTK Query</strong> for server state (replaces hand&ndash;written thunks for most apps), and <strong>Immer</strong> baked in so you can &ldquo;mutate&rdquo; state in reducers safely.</p>

<p>When to actually use Redux in 2026: complex client&ndash;state interactions, undo/redo, cross&ndash;component coordination that doesn&rsquo;t map to URL or server state. For most apps the better default split is <strong>TanStack Query</strong> for server state + <strong>Zustand</strong>/<strong>Jotai</strong> for client state &mdash; less ceremony, smaller bundles. Redux still wins on tooling, time&ndash;travel debugging, and large&ndash;team predictability, especially with RTK Query for caching APIs.</p>'''


ANSWERS[61] = r'''<p>Setup with <strong>Redux Toolkit</strong> + <strong>React-Redux</strong> takes about five minutes:</p>

<pre><code>npm i @reduxjs/toolkit react-redux</code></pre>

<pre><code>// store/index.ts &mdash; configure the store
import { configureStore } from &quot;@reduxjs/toolkit&quot;;
import cartReducer from &quot;./cartSlice&quot;;
import userReducer from &quot;./userSlice&quot;;

export const store = configureStore({
  reducer: { cart: cartReducer, user: userReducer }
});
export type RootState = ReturnType&lt;typeof store.getState&gt;;
export type AppDispatch = typeof store.dispatch;

// hooks.ts &mdash; typed hooks (always re-export these instead of useDispatch/useSelector)
import { useDispatch, useSelector, type TypedUseSelectorHook } from &quot;react-redux&quot;;
export const useAppDispatch = () =&gt; useDispatch&lt;AppDispatch&gt;();
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;

// main.tsx &mdash; wrap the app
import { Provider } from &quot;react-redux&quot;;
import { store } from &quot;./store&quot;;
&lt;Provider store={store}&gt;&lt;App /&gt;&lt;/Provider&gt;</code></pre>

<pre><code>// In a component
import { useAppSelector, useAppDispatch } from &quot;./hooks&quot;;
import { add, remove } from &quot;./store/cartSlice&quot;;

function CartButton({ id }: { id: string }) {
  const items = useAppSelector(s =&gt; s.cart.items);
  const dispatch = useAppDispatch();
  const inCart = items.some(i =&gt; i.id === id);
  return (
    &lt;button onClick={() =&gt; dispatch(inCart ? remove(id) : add(id))}&gt;
      {inCart ? &quot;Remove&quot; : &quot;Add to cart&quot;}
    &lt;/button&gt;
  );
}</code></pre>

<p>Patterns to follow: keep <strong>selectors small and memoized</strong> (use <code>createSelector</code> from RTK for derived data), <strong>colocate slices with features</strong> (<code>features/cart/cartSlice.ts</code>), use <strong>RTK Query</strong> for server data instead of hand&ndash;writing fetch thunks, and avoid storing derived/computable state in Redux. Add <strong>Redux DevTools Extension</strong> in the browser for time&ndash;travel debugging &mdash; it works automatically with RTK&rsquo;s configureStore.</p>'''


ANSWERS[62] = r'''<p><strong>Middleware</strong> in Redux sits between dispatching an action and the reducer running. It can log, transform, delay, or short&ndash;circuit actions &mdash; the same chain&ndash;of&ndash;responsibility pattern Express uses for HTTP.</p>

<pre><code>// Custom middleware: log every action
const logger = store =&gt; next =&gt; action =&gt; {
  console.log(&quot;dispatching:&quot;, action);
  const result = next(action);     // pass to next middleware / reducer
  console.log(&quot;new state:&quot;, store.getState());
  return result;
};

// Custom middleware: throttle a noisy action
const throttle = store =&gt; next =&gt; {
  const last = new Map&lt;string, number&gt;();
  return action =&gt; {
    if (action.type === &quot;analytics/track&quot;) {
      const t = last.get(action.payload.event) ?? 0;
      if (Date.now() - t &lt; 1000) return;     // drop
      last.set(action.payload.event, Date.now());
    }
    return next(action);
  };
};</code></pre>

<pre><code>// Wire into the store (RTK)
import { configureStore } from &quot;@reduxjs/toolkit&quot;;

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefault) =&gt; getDefault().concat(logger, throttle)
});</code></pre>

<p>RTK already includes useful middleware out of the box:</p>

<ul>
<li><strong>redux&ndash;thunk</strong> &mdash; lets action creators return functions for async work.</li>
<li><strong>serializable&ndash;state checker</strong> &mdash; warns if you put non&ndash;serializable values in state.</li>
<li><strong>immutable&ndash;state checker</strong> &mdash; warns if you mutate state outside Immer.</li>
</ul>

<p>Common third&ndash;party middlewares: <strong>redux&ndash;saga</strong> (generator&ndash;based async, complex but powerful), <strong>redux&ndash;observable</strong> (RxJS), <strong>RTK Query</strong> (built&ndash;in API caching layer that&rsquo;s really middleware + reducer + hooks). For most apps in 2026, <strong>thunk + RTK Query</strong> covers async needs without dragging in saga or observable. Reach for sagas only when you have complex cancellation/race&ndash;condition workflows that benefit from generator semantics.</p>'''


ANSWERS[63] = r'''<p><strong>Redux Thunk</strong> lets action creators return a <em>function</em> instead of a plain action. The function gets <code>dispatch</code> + <code>getState</code> as args, so you can do async work (fetch, delays, conditional dispatch) before dispatching the actual action. RTK includes thunk by default; you don&rsquo;t need to install it.</p>

<pre><code>// Plain thunk
export const fetchUser = (id: string) =&gt; async (dispatch, getState) =&gt; {
  if (getState().user.byId[id]) return;       // already in cache
  dispatch({ type: &quot;user/loading&quot;, payload: id });
  try {
    const res = await fetch(`/api/users/${id}`);
    dispatch({ type: &quot;user/loaded&quot;, payload: await res.json() });
  } catch (e) {
    dispatch({ type: &quot;user/failed&quot;, payload: { id, error: e.message } });
  }
};</code></pre>

<p>The <strong>RTK</strong> way is much cleaner with <code>createAsyncThunk</code> &mdash; it generates pending/fulfilled/rejected actions for you and integrates with <code>extraReducers</code>:</p>

<pre><code>import { createAsyncThunk, createSlice } from &quot;@reduxjs/toolkit&quot;;

export const fetchUser = createAsyncThunk(
  &quot;user/fetch&quot;,
  async (id: string, { rejectWithValue }) =&gt; {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) return rejectWithValue(await res.text());
    return res.json();
  }
);

const userSlice = createSlice({
  name: &quot;user&quot;,
  initialState: { byId: {}, status: &quot;idle&quot; },
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchUser.pending,   (s) =&gt; { s.status = &quot;loading&quot;; })
      .addCase(fetchUser.fulfilled, (s, a) =&gt; { s.byId[a.payload.id] = a.payload; s.status = &quot;idle&quot;; })
      .addCase(fetchUser.rejected,  (s, a) =&gt; { s.status = &quot;error&quot;; s.error = a.payload as string; });
  }
});

// Component
const dispatch = useAppDispatch();
useEffect(() =&gt; { dispatch(fetchUser(id)); }, [id]);</code></pre>

<p>For most 2026 apps you should reach for <strong>RTK Query</strong> instead of writing thunks for API calls &mdash; it gives you caching, dedup, refetch&ndash;on&ndash;focus, and auto&ndash;generated React hooks for free. Thunks remain useful for non&ndash;HTTP async work: timers, IndexedDB, multi&ndash;step orchestration that doesn&rsquo;t map onto a single endpoint.</p>'''


ANSWERS[64] = r'''<p><strong>React Router</strong> is the standard client&ndash;side routing library. The 2026 version is <strong>React Router 7</strong> (the merged successor of Remix), and you can use it as a library (SPA) or as a framework (with SSR/loaders). Basic SPA setup:</p>

<pre><code>npm i react-router-dom</code></pre>

<pre><code>// App.tsx
import { BrowserRouter, Routes, Route, Link, Outlet, useParams } from &quot;react-router-dom&quot;;

function Layout() {
  return (
    &lt;&gt;
      &lt;nav&gt;&lt;Link to=&quot;/&quot;&gt;Home&lt;/Link&gt; &lt;Link to=&quot;/products&quot;&gt;Products&lt;/Link&gt;&lt;/nav&gt;
      &lt;Outlet /&gt;          {/* nested route renders here */}
    &lt;/&gt;
  );
}
function Home()       { return &lt;h1&gt;Home&lt;/h1&gt;; }
function Products()   { return &lt;h1&gt;Products&lt;/h1&gt;; }
function Product()    { const { id } = useParams(); return &lt;h1&gt;Product {id}&lt;/h1&gt;; }
function NotFound()   { return &lt;h1&gt;404&lt;/h1&gt;; }

export default function App() {
  return (
    &lt;BrowserRouter&gt;
      &lt;Routes&gt;
        &lt;Route element={&lt;Layout /&gt;}&gt;
          &lt;Route path=&quot;/&quot;             element={&lt;Home /&gt;} /&gt;
          &lt;Route path=&quot;/products&quot;     element={&lt;Products /&gt;} /&gt;
          &lt;Route path=&quot;/products/:id&quot; element={&lt;Product /&gt;} /&gt;
          &lt;Route path=&quot;*&quot;             element={&lt;NotFound /&gt;} /&gt;
        &lt;/Route&gt;
      &lt;/Routes&gt;
    &lt;/BrowserRouter&gt;
  );
}</code></pre>

<p>Useful APIs:</p>

<ul>
<li><code>&lt;Link&gt;</code> / <code>&lt;NavLink&gt;</code> &mdash; client&ndash;side navigation, no full reload.</li>
<li><code>useParams</code>, <code>useSearchParams</code>, <code>useLocation</code> &mdash; read URL state.</li>
<li><code>useNavigate</code> &mdash; programmatic navigation: <code>nav(&quot;/login&quot;)</code>.</li>
<li><strong>Nested routes + <code>&lt;Outlet&gt;</code></strong> &mdash; layouts compose without prop drilling.</li>
<li><strong>Lazy routes</strong> &mdash; <code>lazy: () =&gt; import(&quot;./pages/Heavy&quot;)</code> code&ndash;splits per route.</li>
</ul>

<p>For SSR/SEO needs, switch to React Router 7&rsquo;s <strong>framework mode</strong> with loaders/actions, or use <strong>Next.js App Router</strong>, <strong>TanStack Router</strong> (best&ndash;in&ndash;class type safety), or <strong>Astro</strong> for content&ndash;heavy sites. Pure SPAs with React Router still work great for internal dashboards and admin panels where SEO doesn&rsquo;t matter.</p>'''


ANSWERS[65] = r'''<p>To <strong>protect routes</strong> in React Router, wrap them with a guard component that reads auth state and either renders the route or redirects to <code>/login</code>:</p>

<pre><code>// auth/RequireAuth.tsx
import { Navigate, useLocation, Outlet } from &quot;react-router-dom&quot;;
import { useAuth } from &quot;@/hooks/useAuth&quot;;

export function RequireAuth({ roles }: { roles?: string[] }) {
  const { user, isLoading } = useAuth();
  const loc = useLocation();

  if (isLoading) return &lt;Spinner /&gt;;
  if (!user) {
    return &lt;Navigate to=&quot;/login&quot; state={{ from: loc }} replace /&gt;;
  }
  if (roles &amp;&amp; !roles.some(r =&gt; user.roles.includes(r))) {
    return &lt;Navigate to=&quot;/forbidden&quot; replace /&gt;;
  }
  return &lt;Outlet /&gt;;
}</code></pre>

<pre><code>// App.tsx &mdash; wrap private routes
&lt;Routes&gt;
  &lt;Route path=&quot;/&quot;       element={&lt;Home /&gt;} /&gt;
  &lt;Route path=&quot;/login&quot;  element={&lt;Login /&gt;} /&gt;

  &lt;Route element={&lt;RequireAuth /&gt;}&gt;                    {/* logged-in only */}
    &lt;Route path=&quot;/dashboard&quot; element={&lt;Dashboard /&gt;} /&gt;
    &lt;Route path=&quot;/profile&quot;   element={&lt;Profile /&gt;} /&gt;
  &lt;/Route&gt;

  &lt;Route element={&lt;RequireAuth roles={[&quot;admin&quot;]} /&gt;}&gt;   {/* admin only */}
    &lt;Route path=&quot;/admin&quot; element={&lt;AdminPanel /&gt;} /&gt;
  &lt;/Route&gt;
&lt;/Routes&gt;</code></pre>

<p>After login, send the user back to where they were trying to go:</p>

<pre><code>// Login.tsx
const nav = useNavigate();
const { state } = useLocation() as { state?: { from?: Location } };
async function onSubmit(creds) {
  await login(creds);
  nav(state?.from?.pathname ?? &quot;/dashboard&quot;, { replace: true });
}</code></pre>

<p>Critical reminder: <strong>client&ndash;side route guards are UX, not security</strong>. The user can edit JS in devtools to render any component. Real authorization happens on the server &mdash; every API endpoint must verify the JWT/session and check permissions independently. Use <strong>Clerk</strong>, <strong>Auth0</strong>, <strong>WorkOS</strong>, or <strong>Better Auth</strong> hooks for the auth state in 2026; they expose ready&ndash;made <code>SignedIn</code>/<code>SignedOut</code> components and protect API routes server&ndash;side too.</p>'''

ANSWERS[66] = r'''<p>Form validation in React means showing errors when input is wrong &mdash; before sending to the server &mdash; and preventing invalid submissions. The 2026 default approach is <strong>React Hook Form (RHF)</strong> + <strong>Zod</strong> (or Valibot/Yup) for schema, plugged together via <code>@hookform/resolvers/zod</code>:</p>

<pre><code>npm i react-hook-form zod @hookform/resolvers</code></pre>

<pre><code>import { useForm } from &quot;react-hook-form&quot;;
import { zodResolver } from &quot;@hookform/resolvers/zod&quot;;
import { z } from &quot;zod&quot;;

const schema = z.object({
  email:    z.string().email(&quot;Enter a valid email&quot;),
  password: z.string().min(8, &quot;At least 8 characters&quot;),
  age:      z.coerce.number().int().min(13, &quot;Must be 13+&quot;)
});
type FormData = z.infer&lt;typeof schema&gt;;

export function SignupForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm&lt;FormData&gt;({ resolver: zodResolver(schema), mode: &quot;onBlur&quot; });

  return (
    &lt;form onSubmit={handleSubmit(async (data) =&gt; { await api.signup(data); })}&gt;
      &lt;input {...register(&quot;email&quot;)} placeholder=&quot;Email&quot; /&gt;
      {errors.email &amp;&amp; &lt;span&gt;{errors.email.message}&lt;/span&gt;}

      &lt;input {...register(&quot;password&quot;)} type=&quot;password&quot; /&gt;
      {errors.password &amp;&amp; &lt;span&gt;{errors.password.message}&lt;/span&gt;}

      &lt;input {...register(&quot;age&quot;)} type=&quot;number&quot; /&gt;
      {errors.age &amp;&amp; &lt;span&gt;{errors.age.message}&lt;/span&gt;}

      &lt;button disabled={isSubmitting}&gt;Sign up&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p>Why this stack: <strong>uncontrolled inputs</strong> mean fewer re&ndash;renders (RHF only re&ndash;renders fields with errors), <strong>schema&ndash;driven</strong> means the same Zod schema validates on the API too, and <strong>resolver pattern</strong> lets you swap libraries without rewriting forms.</p>

<p>Useful bits: <code>mode: &quot;onBlur&quot;</code> validates when fields lose focus (good UX), <code>watch</code> for cross&ndash;field rules, <code>Controller</code> for non&ndash;native inputs (Radix, headless UI components), <code>setError</code> to surface API&ndash;side errors back into form state.</p>

<p>Alternatives: <strong>TanStack Form</strong> (rising star with framework agnostic + first&ndash;class TS), <strong>Conform</strong> (server&ndash;first for Remix/Next), <strong>Valibot</strong> (smaller bundle than Zod). Avoid Formik for new projects in 2026 &mdash; RHF is faster, better typed, and more actively developed.</p>'''


ANSWERS[67] = r'''<p><strong>Formik</strong> + <strong>Yup</strong> is the older but still common combo for React form validation. Formik manages form state and lifecycle; Yup provides the schema. Setup:</p>

<pre><code>npm i formik yup</code></pre>

<pre><code>import { Formik, Form, Field, ErrorMessage } from &quot;formik&quot;;
import * as Yup from &quot;yup&quot;;

const schema = Yup.object({
  email: Yup.string().email(&quot;Invalid email&quot;).required(&quot;Required&quot;),
  password: Yup.string().min(8, &quot;Min 8 chars&quot;).required(&quot;Required&quot;),
  age: Yup.number().min(13, &quot;Must be 13+&quot;).required(&quot;Required&quot;)
});

export function Signup() {
  return (
    &lt;Formik
      initialValues={{ email: &quot;&quot;, password: &quot;&quot;, age: &quot;&quot; }}
      validationSchema={schema}
      onSubmit={async (values, { setSubmitting, setErrors }) =&gt; {
        try { await api.signup(values); }
        catch (e) { setErrors({ email: &quot;Already registered&quot; }); }
        finally   { setSubmitting(false); }
      }}
    &gt;
      {({ isSubmitting }) =&gt; (
        &lt;Form&gt;
          &lt;Field name=&quot;email&quot; placeholder=&quot;Email&quot; /&gt;
          &lt;ErrorMessage name=&quot;email&quot; component=&quot;span&quot; /&gt;

          &lt;Field name=&quot;password&quot; type=&quot;password&quot; /&gt;
          &lt;ErrorMessage name=&quot;password&quot; component=&quot;span&quot; /&gt;

          &lt;Field name=&quot;age&quot; type=&quot;number&quot; /&gt;
          &lt;ErrorMessage name=&quot;age&quot; component=&quot;span&quot; /&gt;

          &lt;button type=&quot;submit&quot; disabled={isSubmitting}&gt;Sign up&lt;/button&gt;
        &lt;/Form&gt;
      )}
    &lt;/Formik&gt;
  );
}</code></pre>

<p>What Formik does well: built&ndash;in <code>&lt;Field&gt;</code>/<code>&lt;ErrorMessage&gt;</code>/<code>&lt;Form&gt;</code> components reduce wiring, <code>setErrors</code> from <code>onSubmit</code> integrates server&ndash;side errors, validation runs declaratively from the Yup schema. Yup itself has a clean fluent API for nested schemas and conditional rules (<code>Yup.when</code>).</p>

<p><strong>Honest 2026 advice:</strong> for new projects pick <strong>React Hook Form + Zod</strong> instead. Formik renders the entire form on every keystroke (slow on big forms), the maintainership has slowed, and Zod&rsquo;s TypeScript inference beats Yup&rsquo;s. RHF + Zod is also smaller (~25KB vs ~50KB), works the same with Radix/Headless UI, and shares the same Zod schema with your API for end&ndash;to&ndash;end type safety. Formik remains fine for legacy codebases &mdash; don&rsquo;t rewrite working forms just to switch.</p>'''


ANSWERS[68] = r'''<p>For new React apps in 2026 you should reach for <strong>Vite</strong>, not raw Webpack/Babel &mdash; it&rsquo;s 10&ndash;100x faster on dev startup and HMR. But understanding the underlying setup is still useful.</p>

<pre><code># The modern Vite path (recommended)
npm create vite@latest my-app -- --template react-ts
cd my-app &amp;&amp; npm i &amp;&amp; npm run dev    # dev server in &lt;1s</code></pre>

<p>For a manual Webpack + Babel setup:</p>

<pre><code>npm i -D webpack webpack-cli webpack-dev-server
        @babel/core @babel/preset-env @babel/preset-react @babel/preset-typescript
        babel-loader html-webpack-plugin css-loader style-loader</code></pre>

<pre><code>// webpack.config.js
const HtmlWebpackPlugin = require(&quot;html-webpack-plugin&quot;);
module.exports = {
  mode: process.env.NODE_ENV ?? &quot;development&quot;,
  entry: &quot;./src/index.tsx&quot;,
  output: { filename: &quot;[name].[contenthash].js&quot;, clean: true },
  resolve: { extensions: [&quot;.tsx&quot;, &quot;.ts&quot;, &quot;.js&quot;] },
  module: {
    rules: [
      { test: /\.tsx?$/, exclude: /node_modules/, use: &quot;babel-loader&quot; },
      { test: /\.css$/, use: [&quot;style-loader&quot;, &quot;css-loader&quot;] }
    ]
  },
  plugins: [new HtmlWebpackPlugin({ template: &quot;./public/index.html&quot; })],
  devServer: {
    static: &quot;./dist&quot;, hot: true, port: 3000, historyApiFallback: true
  }
};

// babel.config.json
{
  &quot;presets&quot;: [
    [&quot;@babel/preset-env&quot;, { &quot;targets&quot;: &quot;&gt;0.2%, not dead&quot; }],
    [&quot;@babel/preset-react&quot;, { &quot;runtime&quot;: &quot;automatic&quot; }],
    &quot;@babel/preset-typescript&quot;
  ]
}</code></pre>

<pre><code>// package.json
&quot;scripts&quot;: {
  &quot;dev&quot;:   &quot;webpack serve&quot;,
  &quot;build&quot;: &quot;NODE_ENV=production webpack&quot;
}</code></pre>

<p>2026 reality check: <strong>Vite</strong> uses esbuild for transforms (Go&ndash;based, parallelized) and native ES modules for dev. Webpack 5 + SWC is faster than Babel but still slow vs Vite. Other modern bundlers: <strong>Turbopack</strong> (Vercel, Next.js default), <strong>Rspack</strong> (ByteDance, Webpack&ndash;compatible Rust port), <strong>Bun</strong>. Pick Webpack only when you need its plugin ecosystem (custom builds, micro&ndash;frontends with Module Federation).</p>'''


ANSWERS[69] = r'''<p><strong>Hot Module Replacement (HMR)</strong> swaps changed modules into a running app without losing state. You edit <code>Counter.tsx</code>, save, and the new component renders instantly while the count it was holding stays at 7. Compared to a full page reload, HMR keeps your scroll position, form input, modal state, and Redux store intact &mdash; saving hundreds of micro&ndash;reloads per day.</p>

<p>In <strong>Vite</strong> (default for new React projects in 2026), HMR is on out of the box:</p>

<pre><code># Just run the dev server &mdash; HMR is automatic
npm create vite@latest my-app -- --template react-ts
cd my-app &amp;&amp; npm i &amp;&amp; npm run dev</code></pre>

<p>For React, Vite uses the official <strong>@vitejs/plugin-react</strong> which integrates <strong>React Refresh</strong> &mdash; the technology behind component&ndash;level HMR. Component state survives edits as long as the export shape stays the same; major structural changes fall back to a full reload.</p>

<p>For <strong>Webpack</strong>:</p>

<pre><code>// webpack.config.js
module.exports = {
  devServer: { hot: true, port: 3000, historyApiFallback: true }
};

// And the React Fast Refresh plugin
npm i -D @pmmmwh/react-refresh-webpack-plugin react-refresh

// webpack.config.js plugins:
const ReactRefreshWebpackPlugin = require(&quot;@pmmmwh/react-refresh-webpack-plugin&quot;);
plugins: [new ReactRefreshWebpackPlugin()]

// babel.config.json plugins:
&quot;plugins&quot;: [&quot;react-refresh/babel&quot;]</code></pre>

<p>For <strong>Next.js 15</strong>, HMR works automatically &mdash; no config required &mdash; via Turbopack/SWC + React Refresh.</p>

<p>HMR limits: side effects in module top&ndash;level code don&rsquo;t re&ndash;run cleanly (you&rsquo;ll see warnings), state in non&ndash;React stores survives but components reading it might not, and very large dependency graphs can fall back to full reload. Use <code>// @refresh reset</code> at the top of a file to force&ndash;reset state on save when needed.</p>'''


ANSWERS[70] = r'''<p><strong>ESLint</strong> finds bugs, enforces consistent code patterns, and catches subtle issues (unused imports, accidental globals, unsafe comparisons). For a MERN stack with TypeScript:</p>

<pre><code>npm i -D eslint typescript-eslint eslint-plugin-react-hooks eslint-plugin-react-refresh

# 2026: ESLint 9 uses flat config (eslint.config.js)
npx eslint --init</code></pre>

<pre><code>// eslint.config.js (flat config &mdash; the 2026 default)
import js from &quot;@eslint/js&quot;;
import tseslint from &quot;typescript-eslint&quot;;
import reactHooks from &quot;eslint-plugin-react-hooks&quot;;
import reactRefresh from &quot;eslint-plugin-react-refresh&quot;;

export default tseslint.config(
  { ignores: [&quot;dist&quot;, &quot;build&quot;, &quot;node_modules&quot;] },
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  {
    files: [&quot;**/*.{ts,tsx}&quot;],
    plugins: { &quot;react-hooks&quot;: reactHooks, &quot;react-refresh&quot;: reactRefresh },
    languageOptions: { parserOptions: { project: &quot;./tsconfig.json&quot; } },
    rules: {
      ...reactHooks.configs.recommended.rules,
      &quot;react-refresh/only-export-components&quot;: [&quot;warn&quot;, { allowConstantExport: true }],
      &quot;@typescript-eslint/no-unused-vars&quot;: [&quot;warn&quot;, { argsIgnorePattern: &quot;^_&quot; }]
    }
  }
);</code></pre>

<pre><code>// package.json scripts
&quot;scripts&quot;: {
  &quot;lint&quot;:     &quot;eslint .&quot;,
  &quot;lint:fix&quot;: &quot;eslint . --fix&quot;
}</code></pre>

<p>Wire ESLint into:</p>

<ul>
<li><strong>Editor</strong> &mdash; the ESLint VS Code extension shows red squigglies inline.</li>
<li><strong>Pre&ndash;commit</strong> &mdash; via Husky + lint&ndash;staged so bad code never lands.</li>
<li><strong>CI</strong> &mdash; <code>eslint .</code> in GitHub Actions; PRs that fail can&rsquo;t merge.</li>
</ul>

<p>Useful additional configs/plugins: <strong>eslint&ndash;config&ndash;prettier</strong> (turns off rules that conflict with Prettier), <strong>eslint&ndash;plugin&ndash;import</strong> (import order), <strong>eslint&ndash;plugin&ndash;jsx&ndash;a11y</strong> (accessibility checks), <strong>eslint&ndash;plugin&ndash;security</strong> (Node.js security rules).</p>

<p>Faster alternative emerging in 2026: <strong>Biome</strong> (Rust&ndash;based, ~25x faster than ESLint, includes formatter). Drop in if you want a single tool for lint + format and don&rsquo;t need ESLint&rsquo;s plugin ecosystem yet.</p>'''


ANSWERS[71] = r'''<p><strong>Prettier</strong> is an opinionated code formatter &mdash; it rewrites your code in a single canonical style so debates about commas, indentation, and line length end. Unlike ESLint (which checks logic + style), Prettier <em>only</em> formats. The two work together.</p>

<pre><code>npm i -D prettier eslint-config-prettier</code></pre>

<pre><code>// .prettierrc
{
  &quot;semi&quot;: true,
  &quot;singleQuote&quot;: false,
  &quot;trailingComma&quot;: &quot;es5&quot;,
  &quot;printWidth&quot;: 100,
  &quot;tabWidth&quot;: 2,
  &quot;arrowParens&quot;: &quot;always&quot;
}

// .prettierignore
dist/
build/
coverage/
node_modules/</code></pre>

<pre><code>// package.json
&quot;scripts&quot;: {
  &quot;format&quot;:       &quot;prettier --write .&quot;,
  &quot;format:check&quot;: &quot;prettier --check .&quot;
}</code></pre>

<p>Wire it in three places:</p>

<ul>
<li><strong>Editor format&ndash;on&ndash;save</strong> &mdash; install the Prettier VS Code extension and add to <code>.vscode/settings.json</code>:
<pre><code>{
  &quot;editor.formatOnSave&quot;: true,
  &quot;editor.defaultFormatter&quot;: &quot;esbenp.prettier-vscode&quot;
}</code></pre></li>
<li><strong>Pre&ndash;commit hook</strong> via Husky + lint&ndash;staged so unformatted code can&rsquo;t be committed.</li>
<li><strong>CI</strong> &mdash; <code>prettier --check .</code> in GitHub Actions to catch anyone bypassing local hooks.</li>
</ul>

<p>Pair Prettier with ESLint by extending <code>eslint-config-prettier</code> to disable any ESLint rules that would conflict with Prettier&rsquo;s formatting:</p>

<pre><code>// eslint.config.js
import prettierConfig from &quot;eslint-config-prettier&quot;;
export default [
  // ...other configs
  prettierConfig            // must come last to override style rules
];</code></pre>

<p>Prettier handles JS/TS/JSX/TSX, JSON, CSS/SCSS, HTML, Markdown, YAML, and GraphQL out of the box. Plugins extend it to PHP, Java, Solidity, etc.</p>

<p>2026 alternative: <strong>Biome</strong> ships its own formatter (Prettier&ndash;compatible style) plus linter in a single Rust binary &mdash; ~35x faster on large repos. Worth evaluating for new projects, though Prettier&rsquo;s plugin ecosystem and community recognition still make it the default.</p>'''


ANSWERS[72] = r'''<p><strong>Husky</strong> manages git hooks &mdash; scripts that run automatically on commit, push, etc. The most common use: run <code>lint + format + tests</code> on staged files before each commit, blocking bad code from entering the repo.</p>

<pre><code>npm i -D husky lint-staged
npx husky init    # creates .husky/ with a pre-commit script</code></pre>

<pre><code>// package.json &mdash; tell lint-staged what to run on which files
&quot;lint-staged&quot;: {
  &quot;*.{ts,tsx,js,jsx}&quot;: [&quot;eslint --fix&quot;, &quot;prettier --write&quot;],
  &quot;*.{md,json,yml,yaml,css}&quot;: [&quot;prettier --write&quot;]
}</code></pre>

<pre><code># .husky/pre-commit (created by husky init, then edited)
npx lint-staged</code></pre>

<p>That&rsquo;s it &mdash; on the next <code>git commit</code> Husky runs <code>lint-staged</code>, which runs ESLint + Prettier on only staged files, auto&ndash;fixes what it can, and aborts the commit if anything still fails.</p>

<p>Common other hooks worth adding:</p>

<pre><code># .husky/commit-msg &mdash; enforce conventional commits
npx --no -- commitlint --edit $1

# .husky/pre-push &mdash; run the test suite before push
npm test</code></pre>

<p>For commit message linting install <strong>commitlint</strong> + <strong>@commitlint/config-conventional</strong>:</p>

<pre><code>npm i -D @commitlint/cli @commitlint/config-conventional
echo &quot;export default { extends: [&apos;@commitlint/config-conventional&apos;] };&quot; &gt; commitlint.config.js</code></pre>

<p>Why bother: pre&ndash;commit is the cheapest place to catch bugs. Style + lint problems caught locally never reach CI, never trigger code review nits, and never end up in PR comments. Commit message format makes <strong>changesets</strong> + automatic changelog generation easy.</p>

<p>2026 alternatives: <strong>simple-git-hooks</strong> (zero deps, much smaller than Husky), <strong>lefthook</strong> (Go binary, parallel hook execution &mdash; faster on big repos), or git&rsquo;s native hooks if you don&rsquo;t need cross&ndash;platform install. Husky is still the most common and easiest to onboard new contributors to.</p>'''


ANSWERS[73] = r'''<p><strong>Jest</strong> is the most common Node.js testing framework &mdash; it bundles a test runner, assertions, mocking, and coverage reporting. Setup for a Node API:</p>

<pre><code>npm i -D jest @types/jest ts-jest

# Initialize a config
npx ts-jest config:init</code></pre>

<pre><code>// jest.config.js
module.exports = {
  preset: &quot;ts-jest&quot;,
  testEnvironment: &quot;node&quot;,
  testMatch: [&quot;**/*.test.ts&quot;],
  collectCoverageFrom: [&quot;src/**/*.ts&quot;, &quot;!**/*.d.ts&quot;]
};</code></pre>

<pre><code>// src/utils/cents.ts
export function toCents(dollars: number): number {
  if (dollars &lt; 0) throw new Error(&quot;negative&quot;);
  return Math.round(dollars * 100);
}

// src/utils/cents.test.ts
import { toCents } from &quot;./cents&quot;;
describe(&quot;toCents&quot;, () =&gt; {
  test(&quot;rounds correctly&quot;, () =&gt; {
    expect(toCents(1.005)).toBe(101);
    expect(toCents(0)).toBe(0);
  });
  test(&quot;rejects negatives&quot;, () =&gt; {
    expect(() =&gt; toCents(-1)).toThrow(&quot;negative&quot;);
  });
});</code></pre>

<pre><code># Run
npx jest                    # all tests
npx jest --watch            # re-run on file change
npx jest --coverage         # coverage report</code></pre>

<p>Useful patterns:</p>

<ul>
<li><strong>Mocking modules</strong> &mdash; <code>jest.mock(&quot;./db&quot;)</code> to swap in fakes.</li>
<li><strong>Async tests</strong> &mdash; <code>await</code> works directly; use <code>resolves</code>/<code>rejects</code> for matchers.</li>
<li><strong>Setup/teardown</strong> &mdash; <code>beforeEach</code>/<code>afterAll</code> for fixtures.</li>
<li><strong>Snapshots</strong> &mdash; <code>expect(obj).toMatchSnapshot()</code> for stable structural assertions.</li>
</ul>

<p>For database tests use <strong>mongodb-memory-server</strong> to spin up a real MongoDB in&ndash;memory per test run; for HTTP, use <strong>Supertest</strong> against your Express app instance.</p>

<p>2026 reality: <strong>Vitest</strong> is now the more popular choice &mdash; same API as Jest, faster, native ESM support, much better TypeScript story, integrates with Vite. New projects should default to Vitest unless they&rsquo;re already in a Jest ecosystem. <strong>Bun test</strong> is another fast option if your runtime is Bun.</p>'''


ANSWERS[74] = r'''<p><strong>Supertest</strong> wraps an Express app instance to let you assert against real HTTP responses without binding to a port. It pairs naturally with Jest or Vitest for integration tests.</p>

<pre><code>npm i -D supertest @types/supertest
npm i -D mongodb-memory-server   # spin up MongoDB in-memory for the test run</code></pre>

<pre><code>// src/app.ts &mdash; export the Express app *without* calling .listen()
import express from &quot;express&quot;;
export const app = express();
app.use(express.json());
app.post(&quot;/users&quot;, async (req, res) =&gt; {
  const user = await User.create(req.body);
  res.status(201).json(user);
});

// src/app.test.ts
import request from &quot;supertest&quot;;
import { MongoMemoryServer } from &quot;mongodb-memory-server&quot;;
import mongoose from &quot;mongoose&quot;;
import { app } from &quot;./app&quot;;

let mongo: MongoMemoryServer;
beforeAll(async () =&gt; {
  mongo = await MongoMemoryServer.create();
  await mongoose.connect(mongo.getUri());
});
afterAll(async () =&gt; { await mongoose.disconnect(); await mongo.stop(); });
beforeEach(async () =&gt; { await mongoose.connection.dropDatabase(); });

describe(&quot;POST /users&quot;, () =&gt; {
  test(&quot;creates a user&quot;, async () =&gt; {
    const res = await request(app)
      .post(&quot;/users&quot;)
      .send({ name: &quot;Ada&quot;, email: &quot;ada@example.com&quot; });
    expect(res.status).toBe(201);
    expect(res.body.email).toBe(&quot;ada@example.com&quot;);
  });

  test(&quot;rejects bad email&quot;, async () =&gt; {
    const res = await request(app)
      .post(&quot;/users&quot;)
      .send({ name: &quot;Bob&quot;, email: &quot;not-an-email&quot; });
    expect(res.status).toBe(400);
  });
});</code></pre>

<p>What&rsquo;s happening: <strong>Supertest</strong> creates an in&ndash;memory HTTP transport against the Express app, <strong>mongodb-memory-server</strong> downloads a real Mongo binary the first time and runs it on a random port for the test run. Each test gets a clean DB via <code>beforeEach</code> + <code>dropDatabase</code>.</p>

<p>For authenticated routes attach a header: <code>request(app).get(&quot;/me&quot;).set(&quot;Authorization&quot;, &quot;Bearer test-token&quot;)</code> and either issue a real test token or stub the auth middleware in test mode.</p>

<p>For 2026 stacks using <strong>Hono</strong> or <strong>Fastify</strong>, both ship their own injection helpers (<code>app.request()</code>, <code>fastify.inject()</code>) that work the same way without Supertest. The pattern of &ldquo;in&ndash;memory HTTP + in&ndash;memory DB + reset between tests&rdquo; is universal &mdash; it&rsquo;s the right unit of testing for backend logic above unit tests but below E2E.</p>'''


ANSWERS[75] = r'''<p><strong>React Testing Library (RTL)</strong> tests components from the user&rsquo;s perspective &mdash; query by accessible roles and visible text, not by implementation details like class names. Pair it with <strong>Vitest</strong> (or Jest) and <strong>jsdom</strong>:</p>

<pre><code>npm i -D vitest @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom</code></pre>

<pre><code>// vitest.config.ts
import { defineConfig } from &quot;vitest/config&quot;;
import react from &quot;@vitejs/plugin-react&quot;;
export default defineConfig({
  plugins: [react()],
  test: {
    environment: &quot;jsdom&quot;,
    globals: true,
    setupFiles: [&quot;./src/test/setup.ts&quot;]
  }
});

// src/test/setup.ts
import &quot;@testing-library/jest-dom/vitest&quot;;</code></pre>

<pre><code>// src/Counter.tsx
import { useState } from &quot;react&quot;;
export function Counter() {
  const [n, setN] = useState(0);
  return (
    &lt;&gt;
      &lt;p&gt;Count: {n}&lt;/p&gt;
      &lt;button onClick={() =&gt; setN(n + 1)}&gt;Increment&lt;/button&gt;
    &lt;/&gt;
  );
}

// src/Counter.test.tsx
import { render, screen } from &quot;@testing-library/react&quot;;
import userEvent from &quot;@testing-library/user-event&quot;;
import { Counter } from &quot;./Counter&quot;;

test(&quot;increments on click&quot;, async () =&gt; {
  const user = userEvent.setup();
  render(&lt;Counter /&gt;);
  expect(screen.getByText(&quot;Count: 0&quot;)).toBeInTheDocument();
  await user.click(screen.getByRole(&quot;button&quot;, { name: /increment/i }));
  expect(screen.getByText(&quot;Count: 1&quot;)).toBeInTheDocument();
});</code></pre>

<p>RTL principles to internalize:</p>

<ul>
<li>Query by <strong>accessible role</strong> (<code>getByRole</code>), label, or visible text &mdash; the way real users + screen readers find things.</li>
<li>Avoid <code>getByTestId</code> unless nothing else fits &mdash; brittle and a smell.</li>
<li>Use <strong>userEvent</strong> over <code>fireEvent</code> &mdash; simulates real user interactions including focus, hover, key sequences.</li>
<li>Wait for async UI with <strong>findBy*</strong> queries (returns a Promise that retries until the element appears).</li>
</ul>

<p>For API mocking inside component tests use <strong>MSW (Mock Service Worker)</strong> &mdash; intercepts fetch/XHR at the network layer so your component code stays unchanged. Pair RTL with <strong>Storybook</strong> + <strong>Chromatic</strong> for visual regression and you cover unit + visual + interaction testing without Cypress/Playwright (those still belong in true E2E).</p>'''


ANSWERS[76] = r'''<p><strong>Cypress</strong> drives a real browser against your running MERN app to test full user journeys end to end &mdash; signing up, adding to cart, checking out. Setup:</p>

<pre><code>npm i -D cypress
npx cypress open    # interactive runner
npx cypress run     # headless for CI</code></pre>

<pre><code>// cypress.config.ts
import { defineConfig } from &quot;cypress&quot;;
export default defineConfig({
  e2e: {
    baseUrl: &quot;http://localhost:3000&quot;,
    setupNodeEvents(on, config) { /* hooks */ }
  }
});</code></pre>

<pre><code>// cypress/e2e/checkout.cy.ts
describe(&quot;Checkout flow&quot;, () =&gt; {
  beforeEach(() =&gt; {
    // Reset DB through a test-only API endpoint
    cy.request(&quot;POST&quot;, &quot;/test/reset&quot;);
    cy.request(&quot;POST&quot;, &quot;/test/seed&quot;, { products: 3 });
  });

  it(&quot;lets a logged-in user complete a purchase&quot;, () =&gt; {
    cy.visit(&quot;/&quot;);
    cy.contains(&quot;Sign in&quot;).click();
    cy.get(&quot;input[name=email]&quot;).type(&quot;ada@example.com&quot;);
    cy.get(&quot;input[name=password]&quot;).type(&quot;hunter2{enter}&quot;);

    cy.get(&quot;[data-cy=product]&quot;).first().within(() =&gt; {
      cy.contains(&quot;Add to cart&quot;).click();
    });
    cy.contains(&quot;Cart (1)&quot;).click();
    cy.contains(&quot;Checkout&quot;).click();
    cy.contains(&quot;Order confirmed&quot;).should(&quot;be.visible&quot;);
  });
});</code></pre>

<p>Critical practices:</p>

<ul>
<li><strong>Run against a real backend</strong> with a fresh DB per test (test&ndash;only reset/seed endpoints, or <code>mongodb-memory-server</code> in dev).</li>
<li><strong>Use stable selectors</strong> &mdash; <code>data-cy</code> attributes the dev team owns, not CSS classes that designers reshuffle.</li>
<li><strong>Avoid <code>cy.wait(ms)</code></strong> &mdash; use <code>cy.intercept()</code> + <code>cy.wait(&quot;@alias&quot;)</code> on real network calls, or assertions that auto&ndash;retry.</li>
<li><strong>Run E2E in CI</strong> &mdash; spin up the app, run Cypress in headless mode, upload videos/screenshots on failure.</li>
</ul>

<p>2026 alternative gaining ground: <strong>Playwright</strong> &mdash; faster, multi&ndash;browser (Chromium/Firefox/WebKit), better trace viewer, stronger TS support. Most new MERN projects pick Playwright over Cypress; existing teams stay with Cypress for stability and tooling familiarity. Either way, keep E2E tests few but meaningful (5&ndash;20 critical journeys), not exhaustive &mdash; unit + integration cover detail, E2E covers shape.</p>'''


ANSWERS[77] = r'''<p><strong>Git</strong> is a distributed version control system; it&rsquo;s table stakes for any MERN project. Setup the first time:</p>

<pre><code># Identity (one time, globally)
git config --global user.name &quot;Ada Lovelace&quot;
git config --global user.email &quot;ada@example.com&quot;
git config --global init.defaultBranch main
git config --global pull.rebase true        # cleaner history

# Initialize a project
cd my-app
git init
echo &quot;node_modules/\ndist/\n.env&quot; &gt; .gitignore
git add .
git commit -m &quot;Initial commit&quot;</code></pre>

<pre><code># Push to GitHub
gh repo create my-app --public --source=. --remote=origin --push

# Or manually
git remote add origin git@github.com:user/my-app.git
git push -u origin main</code></pre>

<p>Day&ndash;to&ndash;day workflow:</p>

<pre><code>git checkout -b feature/cart-quantities       # branch off main
# ...edit, run tests, commit in small pieces...
git add src/cart/ &amp;&amp; git commit -m &quot;feat(cart): support quantity changes&quot;
git push -u origin feature/cart-quantities
gh pr create --fill                            # open PR via GitHub CLI</code></pre>

<p>Useful additions:</p>

<ul>
<li><strong>Conventional Commits</strong> (<code>feat:</code>, <code>fix:</code>, <code>docs:</code>) so changelogs and semver bumps auto&ndash;generate via <strong>changesets</strong> or <strong>semantic-release</strong>.</li>
<li><strong>Husky + lint&ndash;staged + commitlint</strong> to enforce format + commit conventions before each commit.</li>
<li><strong>.gitignore</strong> templates for Node/React from <a href="https://github.com/github/gitignore">github/gitignore</a> &mdash; never commit <code>node_modules/</code>, <code>.env</code>, <code>dist/</code>, IDE settings.</li>
<li><strong>Branch protection rules</strong> on GitHub: require passing CI + code review before merging into <code>main</code>.</li>
<li><strong>Trunk&ndash;based development</strong> &mdash; short&ndash;lived feature branches (1&ndash;3 days), squash&ndash;merge to main, deploy from main. Avoid long&ndash;lived develop/release branches.</li>
</ul>

<p>For 2026 teams using AI coding agents (Claude Code, Cursor, GitHub Copilot Workspace), git becomes even more critical &mdash; small commits with clear messages let agents reconstruct intent and catch regressions. Treat the commit log as documentation: each commit should be reviewable on its own.</p>'''


ANSWERS[78] = r'''<p><strong>GitHub Actions</strong> is GitHub&rsquo;s built&ndash;in CI/CD &mdash; YAML workflows that run on push, PR, schedule, or manual trigger. For a MERN project a baseline pipeline runs lint + tests + build, and on the main branch deploys to production.</p>

<pre><code># .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:7
        ports: [&quot;27017:27017&quot;]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test
        env: { MONGODB_URI: mongodb://localhost:27017/test }
      - run: pnpm build

  deploy:
    needs: test
    if: github.ref == &apos;refs/heads/main&apos;
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: vercel/action@v3
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: --prod</code></pre>

<p>Patterns to use:</p>

<ul>
<li><strong>Caching</strong> &mdash; <code>actions/setup-node</code> with <code>cache: pnpm</code> caches the lockfile&ndash;keyed install (10x faster).</li>
<li><strong>Matrix builds</strong> &mdash; test on multiple Node versions or OSes:
<pre><code>strategy:
  matrix: { node: [20, 22] }
runs-on: ubuntu-latest
steps:
  - uses: actions/setup-node@v4
    with: { node-version: ${{ matrix.node }} }</code></pre></li>
<li><strong>Secrets</strong> &mdash; store API keys in repo settings &rarr; Secrets, reference as <code>${{ secrets.NAME }}</code>.</li>
<li><strong>Concurrency</strong> &mdash; cancel previous runs on the same PR:
<pre><code>concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true</code></pre></li>
<li><strong>OIDC for cloud auth</strong> &mdash; instead of long&ndash;lived AWS/GCP keys, use OIDC short&ndash;lived tokens via <code>aws-actions/configure-aws-credentials</code> / <code>google-github-actions/auth</code>.</li>
</ul>

<p>For services like Vercel/Netlify/Render, GitHub Actions is rarely needed &mdash; they auto&ndash;deploy on push. Use Actions when you need: container image builds, custom test matrices, multiple deploy targets, supply&ndash;chain attestations (Sigstore + cosign), or scheduled jobs. Free for public repos and 2,000 min/month on private; cheap to scale beyond that.</p>'''


ANSWERS[79] = r'''<p>The <strong>MongoDB aggregation framework</strong> processes documents through a pipeline of stages &mdash; <code>$match</code>, <code>$group</code>, <code>$lookup</code>, <code>$project</code>, etc. &mdash; each transforming the docs flowing through. It&rsquo;s how you compute analytics, joins, and complex transformations without pulling everything to the application layer.</p>

<pre><code>// Find the top 5 customers by total spend in 2026
db.orders.aggregate([
  { $match: {
      status: &quot;paid&quot;,
      createdAt: { $gte: ISODate(&quot;2026-01-01&quot;) }
  } },
  { $group: {
      _id: &quot;$customerId&quot;,
      totalSpend: { $sum: &quot;$amount&quot; },
      orderCount: { $sum: 1 }
  } },
  { $sort: { totalSpend: -1 } },
  { $limit: 5 },
  { $lookup: {
      from: &quot;users&quot;,
      localField: &quot;_id&quot;,
      foreignField: &quot;_id&quot;,
      as: &quot;customer&quot;
  } },
  { $project: {
      _id: 0,
      name: { $first: &quot;$customer.name&quot; },
      email: { $first: &quot;$customer.email&quot; },
      totalSpend: 1,
      orderCount: 1
  } }
]);</code></pre>

<p>Common stages and what they do:</p>

<table>
<tr><th>Stage</th><th>Purpose</th></tr>
<tr><td><code>$match</code></td><td>Filter docs (place early, use indexes)</td></tr>
<tr><td><code>$project</code></td><td>Reshape: include/exclude/compute fields</td></tr>
<tr><td><code>$group</code></td><td>SQL <code>GROUP BY</code> + aggregations like <code>$sum</code>, <code>$avg</code>, <code>$first</code></td></tr>
<tr><td><code>$sort</code></td><td>Order results (uses index if before <code>$group</code>)</td></tr>
<tr><td><code>$limit</code> / <code>$skip</code></td><td>Pagination</td></tr>
<tr><td><code>$lookup</code></td><td>Join from another collection</td></tr>
<tr><td><code>$unwind</code></td><td>Flatten an array field into one doc per element</td></tr>
<tr><td><code>$facet</code></td><td>Run multiple sub&ndash;pipelines on the same input</td></tr>
<tr><td><code>$merge</code> / <code>$out</code></td><td>Write results to another collection (materialized views)</td></tr>
</table>

<p>Performance rules: put <code>$match</code> + <code>$sort</code> first so the planner can use indexes; <code>$lookup</code> needs an index on the foreign field; check with <code>.explain(&quot;executionStats&quot;)</code>; use Atlas <strong>Performance Advisor</strong> to spot slow pipelines. For repeated heavy queries, materialize via <code>$merge</code> on a schedule (Atlas Triggers) so dashboards read pre&ndash;computed rollups in milliseconds.</p>

<p>For full&ndash;text use <strong>Atlas Search</strong> (<code>$search</code> stage); for vector similarity use <strong>Atlas Vector Search</strong> (<code>$vectorSearch</code>). Both compose into the same pipeline syntax.</p>'''


ANSWERS[80] = r'''<p><strong>Indexes</strong> in MongoDB are B&ndash;tree (or specialized) data structures that let queries skip full collection scans. Without an index, finding a user by email scans every doc; with an index, it&rsquo;s an <em>O(log n)</em> tree walk &mdash; milliseconds vs seconds at scale.</p>

<pre><code>// Create indexes via the shell or driver (idempotent)
db.users.createIndex({ email: 1 }, { unique: true });
db.orders.createIndex({ customerId: 1, createdAt: -1 });    // compound
db.products.createIndex({ name: &quot;text&quot;, description: &quot;text&quot; });  // text
db.events.createIndex({ ts: 1 }, { expireAfterSeconds: 2592000 });  // TTL: 30 days

// In Mongoose schema
const userSchema = new mongoose.Schema({
  email: { type: String, unique: true },         // creates unique index
  tenantId: { type: String, index: true }
});
userSchema.index({ tenantId: 1, createdAt: -1 }); // compound</code></pre>

<p>Compound index field order matters &mdash; the <strong>ESR rule</strong> (Equality, Sort, Range) is the canonical guidance:</p>

<ol>
<li>Equality fields first (<code>tenantId</code>, <code>status</code>).</li>
<li>Sort fields next (<code>createdAt</code>).</li>
<li>Range fields last (<code>amount: { $gt: 100 }</code>).</li>
</ol>

<p>An index on <code>{ tenantId: 1, createdAt: -1 }</code> serves queries that filter on <code>tenantId</code> and sort by <code>createdAt</code>, but not queries that filter only on <code>createdAt</code>.</p>

<p>Check what an index does for a query:</p>

<pre><code>db.orders.find({ tenantId: &quot;t1&quot; }).sort({ createdAt: -1 })
  .explain(&quot;executionStats&quot;);
// Look for stage: IXSCAN (good) vs COLLSCAN (bad)
// Look for totalDocsExamined ≈ nReturned (good)</code></pre>

<p>Index types beyond the basic single&ndash;field/compound:</p>

<ul>
<li><strong>Unique</strong> &mdash; rejects duplicate values.</li>
<li><strong>TTL</strong> &mdash; auto&ndash;deletes docs after N seconds (sessions, logs).</li>
<li><strong>Partial</strong> &mdash; index only docs matching a filter (smaller, faster).</li>
<li><strong>Multikey</strong> &mdash; on array fields, indexes each element.</li>
<li><strong>Text</strong> / <strong>Atlas Search</strong> &mdash; full&ndash;text relevance scoring.</li>
<li><strong>Geospatial</strong> &mdash; <code>2dsphere</code> for &ldquo;within radius&rdquo; queries.</li>
<li><strong>Atlas Vector Search</strong> &mdash; ANN search on embedding vectors.</li>
</ul>

<p>Cost: indexes consume RAM + slow writes (every insert/update updates every relevant index). Atlas <strong>Performance Advisor</strong> recommends missing indexes; <strong>Query Insights</strong> shows slow ops. Drop indexes that <code>db.collection.aggregate([{ $indexStats: {} }])</code> shows are unused.</p>'''

ANSWERS[81] = r'''<p><strong>MongoDB migrations</strong> change document shape across deploys &mdash; rename a field, split a column into two, backfill missing data. Mongo&rsquo;s flexible schema means you can deploy code that handles both shapes and migrate lazily, but you still need a tool to track which migrations have run.</p>

<p>The 2026 standard is <strong>migrate-mongo</strong> &mdash; simple, schema&ndash;less, runs JS files in order:</p>

<pre><code>npm i -D migrate-mongo
npx migrate-mongo init       # creates migrate-mongo-config.js + migrations/ dir</code></pre>

<pre><code>// migrate-mongo-config.js
module.exports = {
  mongodb: {
    url: process.env.MONGODB_URI,
    databaseName: process.env.MONGODB_DB
  },
  migrationsDir: &quot;migrations&quot;,
  changelogCollectionName: &quot;_migrations&quot;
};</code></pre>

<pre><code># Create a migration
npx migrate-mongo create rename-displayName-to-fullName
# &rarr; migrations/20260501-rename-displayName-to-fullName.js

# migrations/20260501-rename-displayName-to-fullName.js
module.exports = {
  async up(db) {
    await db.collection(&quot;users&quot;).updateMany(
      { displayName: { $exists: true } },
      [{ $set: { fullName: &quot;$displayName&quot; } }, { $unset: &quot;displayName&quot; }]
    );
  },
  async down(db) {
    await db.collection(&quot;users&quot;).updateMany(
      { fullName: { $exists: true } },
      [{ $set: { displayName: &quot;$fullName&quot; } }, { $unset: &quot;fullName&quot; }]
    );
  }
};

# Run + status + rollback
npx migrate-mongo up           # apply pending
npx migrate-mongo status       # see what&apos;s applied
npx migrate-mongo down          # rollback the last one</code></pre>

<p>Best practices for production:</p>

<ul>
<li><strong>Expand&ndash;and&ndash;contract</strong> &mdash; deploy code that reads both old and new shape; backfill; remove old shape later. Avoids downtime.</li>
<li><strong>Run from CI</strong> &mdash; trigger <code>migrate-mongo up</code> in the deploy pipeline, after tests pass and before the new app version is live.</li>
<li><strong>Always include <code>down</code></strong> &mdash; even if you never run it, writing it forces you to think about reversibility.</li>
<li><strong>Test migrations</strong> against a recent prod snapshot in staging before running live.</li>
<li><strong>Long backfills</strong> on big collections should chunk + add indexes first; otherwise they hold cluster CPU and stall traffic.</li>
</ul>

<p>Alternatives: <strong>mongoose-migrate-2</strong> (Mongoose&ndash;native), <strong>typegoose-migrate</strong> for TS&ndash;heavy stacks, hand&ndash;rolled scripts via Atlas Triggers for scheduled work. The principle &mdash; &ldquo;every shape change is recorded, ordered, and reversible&rdquo; &mdash; matters more than the tool.</p>'''


ANSWERS[82] = r'''<p><strong>Database seeds</strong> are scripts that populate a database with realistic starter data: dev fixtures, test data, demo accounts, default config rows. They make onboarding new developers a one&ndash;command experience and let CI tests start from a known baseline.</p>

<p>Common patterns:</p>

<ul>
<li><strong>Static seeds</strong> &mdash; fixtures in JSON or JS files (default roles, plan tiers, country list).</li>
<li><strong>Generated seeds</strong> &mdash; use <a href="https://fakerjs.dev"><strong>Faker</strong></a> or <strong>@mswjs/data</strong> to create N realistic users/orders/products.</li>
<li><strong>Snapshot seeds</strong> &mdash; an anonymized dump from prod (Atlas Backup &rarr; restore + scrub PII).</li>
</ul>

<pre><code>npm i -D @faker-js/faker

// scripts/seed.ts
import mongoose from &quot;mongoose&quot;;
import { faker } from &quot;@faker-js/faker&quot;;
import { User } from &quot;../src/models/User&quot;;
import { Product } from &quot;../src/models/Product&quot;;

async function seed() {
  await mongoose.connect(process.env.MONGODB_URI!);

  // Wipe collections first &mdash; only safe in dev / test!
  if (process.env.NODE_ENV === &quot;production&quot;) throw new Error(&quot;NO!&quot;);
  await User.deleteMany({});
  await Product.deleteMany({});

  // Static fixtures
  await User.create({ email: &quot;admin@example.com&quot;, role: &quot;admin&quot; });

  // Generated bulk data
  const users = Array.from({ length: 100 }, () =&gt; ({
    email: faker.internet.email().toLowerCase(),
    name: faker.person.fullName(),
    createdAt: faker.date.past({ years: 2 })
  }));
  await User.insertMany(users);

  const products = Array.from({ length: 50 }, () =&gt; ({
    name: faker.commerce.productName(),
    price: parseFloat(faker.commerce.price()),
    description: faker.commerce.productDescription()
  }));
  await Product.insertMany(products);

  console.log(&quot;Seeded:&quot;, await User.countDocuments(), &quot;users,&quot;,
                          await Product.countDocuments(), &quot;products&quot;);
  await mongoose.disconnect();
}

seed().catch((e) =&gt; { console.error(e); process.exit(1); });</code></pre>

<pre><code># package.json
&quot;scripts&quot;: {
  &quot;seed&quot;: &quot;tsx scripts/seed.ts&quot;,
  &quot;db:reset&quot;: &quot;tsx scripts/wipe.ts &amp;&amp; npm run seed&quot;
}</code></pre>

<p>Critical safety rule: <strong>seeds must never run against production</strong>. Gate on <code>NODE_ENV !== &quot;production&quot;</code>, use a different connection string, ideally use a local Mongo instance entirely. For test isolation, prefer <code>mongodb-memory-server</code> + reset between tests over a shared seeded DB.</p>

<p>For more structured seeding consider <strong>fishery</strong> (factory&ndash;style builders), <strong>fixtures-for-mongoose</strong>, or your own factory functions. Idempotent seed scripts (<code>upsert</code> instead of <code>insert</code>) are useful for environments where you want to top up data without wiping.</p>'''


ANSWERS[83] = r'''<p><strong>MongoDB transactions</strong> let multiple document writes succeed or fail atomically across collections. Available since 4.0 on replica sets, 4.2 on sharded clusters &mdash; in practice always available on Atlas. Use them when business logic spans multiple documents (transfer money: debit one account, credit another, write a log entry).</p>

<pre><code>import mongoose from &quot;mongoose&quot;;

async function transferFunds(fromId: string, toId: string, amount: number) {
  const session = await mongoose.startSession();
  try {
    session.startTransaction();

    const from = await Account.findById(fromId).session(session);
    if (!from || from.balance &lt; amount) {
      throw new Error(&quot;Insufficient funds&quot;);
    }
    await Account.updateOne(
      { _id: fromId },
      { $inc: { balance: -amount } },
      { session }
    );
    await Account.updateOne(
      { _id: toId },
      { $inc: { balance:  amount } },
      { session }
    );
    await Transfer.create([{ fromId, toId, amount }], { session });

    await session.commitTransaction();
  } catch (e) {
    await session.abortTransaction();
    throw e;
  } finally {
    session.endSession();
  }
}</code></pre>

<p>Or with the helper which auto&ndash;retries on transient errors:</p>

<pre><code>const session = await mongoose.startSession();
await session.withTransaction(async () =&gt; {
  await Account.updateOne({ _id: fromId }, { $inc: { balance: -amount } }, { session });
  await Account.updateOne({ _id: toId },   { $inc: { balance:  amount } }, { session });
  await Transfer.create([{ fromId, toId, amount }], { session });
});
session.endSession();</code></pre>

<p>Important rules:</p>

<ul>
<li>Every operation in the transaction must pass the <code>session</code>. Without it the write happens outside the transaction.</li>
<li>Transactions must complete in &lt; 60 seconds (default <code>transactionLifetimeLimitSeconds</code>).</li>
<li>They cause <strong>write conflicts</strong> &mdash; concurrent transactions that touch the same docs may abort and retry. Driver retry logic handles transient errors automatically.</li>
<li>Performance cost is real &mdash; transactions take longer than single&ndash;document writes. Don&rsquo;t use them where atomic single&ndash;doc updates (<code>$inc</code>, <code>findOneAndUpdate</code>) suffice.</li>
</ul>

<p>For long&ndash;running, multi&ndash;service workflows, transactions don&rsquo;t fit &mdash; reach for the <strong>outbox pattern</strong> (write the change + an event in one transaction, then publish the event reliably) or a <strong>saga</strong> orchestrated via <strong>Temporal</strong>, <strong>Inngest</strong>, <strong>Trigger.dev</strong>, <strong>Restate</strong>, or <strong>Hatchet</strong>. Cross&ndash;service consistency is hard; transactions only solve the within&ndash;single&ndash;DB part.</p>'''


ANSWERS[84] = r'''<p><strong>Mongoose virtuals</strong> are computed properties that aren&rsquo;t stored in MongoDB but appear on documents in your application code &mdash; useful for derived values like <code>fullName</code> from <code>firstName + lastName</code>, or computed URLs.</p>

<pre><code>import mongoose from &quot;mongoose&quot;;

const userSchema = new mongoose.Schema({
  firstName: String,
  lastName: String,
  birthDate: Date
}, {
  // Include virtuals when serializing
  toJSON:   { virtuals: true },
  toObject: { virtuals: true }
});

// Define a virtual
userSchema.virtual(&quot;fullName&quot;).get(function() {
  return `${this.firstName} ${this.lastName}`;
});

userSchema.virtual(&quot;age&quot;).get(function() {
  if (!this.birthDate) return null;
  const ms = Date.now() - this.birthDate.getTime();
  return Math.floor(ms / (1000 * 60 * 60 * 24 * 365.25));
});

// Setter virtual &mdash; split a string back into fields
userSchema.virtual(&quot;fullName&quot;).set(function(name: string) {
  const [first, ...rest] = name.split(&quot; &quot;);
  this.firstName = first;
  this.lastName = rest.join(&quot; &quot;);
});

const User = mongoose.model(&quot;User&quot;, userSchema);

const u = await User.findOne();
console.log(u.fullName);    // &quot;Ada Lovelace&quot; &mdash; computed
console.log(u.age);         // 30
JSON.stringify(u);          // includes fullName + age</code></pre>

<p>Virtuals also support populated relationships &mdash; the <strong>virtual populate</strong> pattern lets you join collections without storing foreign IDs in arrays:</p>

<pre><code>const postSchema = new mongoose.Schema({ title: String, authorId: mongoose.Types.ObjectId });
const userSchema = new mongoose.Schema({ name: String });

userSchema.virtual(&quot;posts&quot;, {
  ref: &quot;Post&quot;,
  localField: &quot;_id&quot;,
  foreignField: &quot;authorId&quot;
});

const user = await User.findById(id).populate(&quot;posts&quot;);
console.log(user.posts);    // array of joined Post documents</code></pre>

<p>Caveats: virtuals <strong>can&rsquo;t be queried</strong> (<code>User.find({ fullName: &quot;Ada Lovelace&quot; })</code> returns nothing &mdash; the field doesn&rsquo;t exist in Mongo). For queryable derived data, store it as a real field maintained via a <code>pre(&quot;save&quot;)</code> hook, or compute it server&ndash;side at write time. Virtuals are fine for view&ndash;layer convenience, the wrong tool for filterable indexed fields.</p>'''


ANSWERS[85] = r'''<p><strong>WebSockets</strong> open a persistent two&ndash;way TCP connection between client and server, letting either side push messages instantly &mdash; ideal for chat, presence, live dashboards, collaborative editing, and order updates. Compare to HTTP polling: WebSockets cut latency from seconds to milliseconds with much less server load.</p>

<p>Browser API is built in:</p>

<pre><code>// Client
const ws = new WebSocket(&quot;wss://api.example.com/ws&quot;);
ws.onopen    = () =&gt; ws.send(JSON.stringify({ type: &quot;hello&quot; }));
ws.onmessage = (e) =&gt; console.log(JSON.parse(e.data));
ws.onclose   = () =&gt; console.log(&quot;closed&quot;);

// Server (Node) using ws library
import { WebSocketServer } from &quot;ws&quot;;
const wss = new WebSocketServer({ port: 8080 });
wss.on(&quot;connection&quot;, (socket) =&gt; {
  socket.on(&quot;message&quot;, (data) =&gt; {
    const msg = JSON.parse(data.toString());
    socket.send(JSON.stringify({ echo: msg }));
  });
});</code></pre>

<p>For real apps you almost always want a higher&ndash;level library:</p>

<ul>
<li><strong>Socket.IO</strong> &mdash; rooms, namespaces, auto&ndash;reconnect, fallback to polling, Redis adapter for multi&ndash;pod fanout.</li>
<li><strong>SSE (Server-Sent Events)</strong> &mdash; one&ndash;way push (server &rarr; client) over plain HTTP. Simpler if you don&rsquo;t need bidirectional.</li>
<li><strong>Hosted real-time</strong> &mdash; <strong>Ably</strong>, <strong>Pusher</strong>, <strong>PartyKit</strong>, <strong>Soketi</strong>, <strong>PieSocket</strong>, <strong>Cloudflare Durable Objects</strong>. Skip the &ldquo;which pod owns this room&rdquo; problem entirely.</li>
</ul>

<p>Things that bite production WebSocket apps:</p>

<ul>
<li><strong>Authentication</strong> &mdash; verify a short&ndash;lived JWT on connect; never trust client&ndash;sent identity.</li>
<li><strong>Connection drops on deploy</strong> &mdash; clients must auto&ndash;reconnect with backoff; server should drain gracefully.</li>
<li><strong>Multiple instances</strong> &mdash; if user A connects to pod 1 and user B to pod 2, you need a pub/sub layer (Redis adapter for Socket.IO, NATS, or a hosted service) so messages reach both.</li>
<li><strong>Backpressure</strong> &mdash; slow clients blocking your buffers; drop or queue.</li>
<li><strong>Resume after disconnect</strong> &mdash; track a last&ndash;event&ndash;ID so reconnects fetch what they missed; pair WebSocket with a REST resync endpoint.</li>
</ul>

<p>Default 2026 picks: <strong>Socket.IO + Redis adapter</strong> for self&ndash;host MERN; <strong>Ably/Pusher/PartyKit/Cloudflare Durable Objects</strong> when you want zero ops. For doc collab, layer <strong>Yjs</strong> on top of any WebSocket transport.</p>'''


ANSWERS[86] = r'''<p><strong>Socket.IO</strong> is a library on top of WebSockets adding rooms, namespaces, automatic reconnection, fallback transports, and a friendly event&ndash;based API. It&rsquo;s the most common way to add real&ndash;time to an Express app.</p>

<pre><code>npm i socket.io           # server
npm i socket.io-client    # client (or @reduxjs/toolkit&apos;s socket helpers)</code></pre>

<pre><code>// server.ts
import express from &quot;express&quot;;
import { createServer } from &quot;http&quot;;
import { Server } from &quot;socket.io&quot;;

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: { origin: &quot;https://app.example.com&quot;, credentials: true }
});

// Auth middleware &mdash; runs once per connection
io.use(async (socket, next) =&gt; {
  const token = socket.handshake.auth.token;
  try { socket.data.user = await verifyJwt(token); next(); }
  catch (e) { next(new Error(&quot;Unauthorized&quot;)); }
});

io.on(&quot;connection&quot;, (socket) =&gt; {
  console.log(&quot;connected:&quot;, socket.data.user.id);

  socket.on(&quot;join-room&quot;, (roomId) =&gt; socket.join(roomId));

  socket.on(&quot;send-message&quot;, async ({ roomId, text }) =&gt; {
    const msg = await Message.create({
      roomId, text, authorId: socket.data.user.id
    });
    io.to(roomId).emit(&quot;new-message&quot;, msg);
  });

  socket.on(&quot;disconnect&quot;, () =&gt; console.log(&quot;disconnected&quot;));
});

httpServer.listen(3000);</code></pre>

<pre><code>// React client
import { io as ioClient } from &quot;socket.io-client&quot;;
import { useEffect, useState } from &quot;react&quot;;

export function Chat({ roomId }: { roomId: string }) {
  const [messages, setMessages] = useState&lt;any[]&gt;([]);

  useEffect(() =&gt; {
    const socket = ioClient(import.meta.env.VITE_API_URL, {
      auth: { token: localStorage.getItem(&quot;token&quot;) }
    });
    socket.emit(&quot;join-room&quot;, roomId);
    socket.on(&quot;new-message&quot;, (msg) =&gt; setMessages((prev) =&gt; [...prev, msg]));
    return () =&gt; { socket.disconnect(); };
  }, [roomId]);

  return &lt;ul&gt;{messages.map(m =&gt; &lt;li key={m._id}&gt;{m.text}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<p>For multi&ndash;pod deployments you must add the <strong>Redis adapter</strong> (or Postgres adapter, or NATS) so emits reach clients connected to other pods:</p>

<pre><code>npm i @socket.io/redis-adapter ioredis

import { createAdapter } from &quot;@socket.io/redis-adapter&quot;;
import { createClient } from &quot;redis&quot;;
const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await Promise.all([pubClient.connect(), subClient.connect()]);
io.adapter(createAdapter(pubClient, subClient));</code></pre>

<p>2026 alternatives gaining traction: <strong>PartyKit</strong>, <strong>Ably</strong>, <strong>Pusher</strong>, <strong>Cloudflare Durable Objects</strong> &mdash; managed real&ndash;time so you skip Redis adapter setup and global fanout. Socket.IO remains the right pick when you want to self&ndash;host with familiar tooling.</p>'''


ANSWERS[87] = r'''<p><strong>Passport.js</strong> is an authentication middleware for Express &mdash; pluggable &ldquo;strategies&rdquo; for local username/password, OAuth (Google, GitHub, Facebook), JWT, and dozens more. You configure strategies once, then call <code>passport.authenticate(&quot;name&quot;)</code> on routes that need auth.</p>

<pre><code>npm i passport passport-local passport-jwt express-session bcryptjs</code></pre>

<pre><code>// auth.ts
import passport from &quot;passport&quot;;
import { Strategy as LocalStrategy } from &quot;passport-local&quot;;
import { Strategy as JwtStrategy, ExtractJwt } from &quot;passport-jwt&quot;;
import bcrypt from &quot;bcryptjs&quot;;
import { User } from &quot;./models/User&quot;;

passport.use(new LocalStrategy(
  { usernameField: &quot;email&quot; },
  async (email, password, done) =&gt; {
    const user = await User.findOne({ email });
    if (!user) return done(null, false, { message: &quot;Wrong credentials&quot; });
    const ok = await bcrypt.compare(password, user.passwordHash);
    if (!ok)   return done(null, false, { message: &quot;Wrong credentials&quot; });
    return done(null, user);
  }
));

passport.use(new JwtStrategy(
  {
    jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
    secretOrKey: process.env.JWT_SECRET!
  },
  async (payload, done) =&gt; {
    const user = await User.findById(payload.sub);
    return done(null, user || false);
  }
));</code></pre>

<pre><code>// app.ts
import express from &quot;express&quot;;
import passport from &quot;passport&quot;;
import jwt from &quot;jsonwebtoken&quot;;
import &quot;./auth&quot;;

const app = express();
app.use(express.json());
app.use(passport.initialize());

// Login: validate password, return JWT
app.post(&quot;/auth/login&quot;,
  passport.authenticate(&quot;local&quot;, { session: false }),
  (req, res) =&gt; {
    const token = jwt.sign({ sub: req.user._id }, process.env.JWT_SECRET!, {
      expiresIn: &quot;15m&quot;
    });
    res.json({ token });
  }
);

// Protected route &mdash; requires valid JWT
app.get(&quot;/me&quot;,
  passport.authenticate(&quot;jwt&quot;, { session: false }),
  (req, res) =&gt; res.json(req.user)
);</code></pre>

<p>Patterns and pitfalls: hash passwords with <strong>argon2id</strong> (or bcrypt with cost 12+) &mdash; never plain SHA. Issue <strong>short&ndash;lived access tokens</strong> (15 min) + <strong>refresh tokens</strong> with rotation; never put raw JWTs in localStorage long&ndash;term. Track failed login attempts and rate&ndash;limit per IP/email.</p>

<p>Honest 2026 advice: most teams skip Passport entirely and use a managed auth service &mdash; <strong>Clerk</strong>, <strong>Auth0</strong>, <strong>WorkOS</strong>, <strong>Stytch</strong>, <strong>Supabase Auth</strong>, or <strong>Better Auth</strong> (open source). They handle MFA, Passkeys, SSO, anomaly detection, and SCIM provisioning out of the box. Roll&ndash;your&ndash;own with Passport only if compliance forces it or you have a very specific niche.</p>'''


ANSWERS[88] = r'''<p>OAuth via Passport adds a strategy per provider and a callback URL. Example with Google &mdash; same pattern works for GitHub, Facebook, Microsoft, Apple, Twitter, LinkedIn:</p>

<pre><code>npm i passport-google-oauth20</code></pre>

<pre><code>// auth.ts
import passport from &quot;passport&quot;;
import { Strategy as GoogleStrategy } from &quot;passport-google-oauth20&quot;;

passport.use(new GoogleStrategy(
  {
    clientID:     process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    callbackURL:  &quot;/auth/google/callback&quot;
  },
  async (accessToken, refreshToken, profile, done) =&gt; {
    // Find or create the user in your DB
    const user = await User.findOneAndUpdate(
      { providerId: profile.id, provider: &quot;google&quot; },
      {
        $setOnInsert: { provider: &quot;google&quot;, providerId: profile.id },
        $set: {
          email: profile.emails?.[0].value,
          name:  profile.displayName,
          avatarUrl: profile.photos?.[0].value
        }
      },
      { upsert: true, new: true }
    );
    return done(null, user);
  }
));</code></pre>

<pre><code>// app.ts
import jwt from &quot;jsonwebtoken&quot;;

// Step 1: redirect the user to Google to grant consent
app.get(&quot;/auth/google&quot;,
  passport.authenticate(&quot;google&quot;, { scope: [&quot;profile&quot;, &quot;email&quot;] })
);

// Step 2: Google redirects back here with ?code=...
app.get(&quot;/auth/google/callback&quot;,
  passport.authenticate(&quot;google&quot;, { session: false, failureRedirect: &quot;/login&quot; }),
  (req, res) =&gt; {
    const token = jwt.sign({ sub: req.user._id }, process.env.JWT_SECRET!, { expiresIn: &quot;15m&quot; });
    res.redirect(`https://app.example.com/oauth-success#token=${token}`);
  }
);</code></pre>

<p>Critical configuration steps:</p>

<ul>
<li>Register the app in the Google Cloud Console, GitHub OAuth Apps, etc. Get a <strong>client ID + client secret</strong>.</li>
<li>Set <strong>authorized redirect URIs</strong> exactly &mdash; including dev (<code>http://localhost:3000/auth/google/callback</code>), staging, and prod.</li>
<li>Store secrets in a vault (Doppler, Infisical, Vault) &mdash; never commit to git.</li>
<li>Use <strong>OAuth 2.1 + PKCE</strong> for SPAs; even confidential&ndash;client flows benefit from PKCE.</li>
<li>On account linking, use <strong>email&ndash;based identity</strong> so a user signing in via Google reaches the same account as their previous email/password login.</li>
</ul>

<p>2026 reality: managed auth services (<strong>Clerk</strong>, <strong>Auth0</strong>, <strong>WorkOS</strong>, <strong>Stytch</strong>, <strong>Supabase Auth</strong>, <strong>Better Auth</strong>) implement OAuth + Passkeys + MFA + SCIM with a fraction of the code. Passport OAuth is fine for hobby projects or when you have unusual requirements (e.g. on&ndash;prem only); for production SaaS, the managed services are usually the better engineering trade.</p>'''


ANSWERS[89] = r'''<p>Express handles file uploads via <strong>multipart/form-data</strong>. The body parser doesn&rsquo;t handle this format &mdash; you need a streaming multipart parser. The standard choice is <strong>Multer</strong>:</p>

<pre><code>npm i multer</code></pre>

<pre><code>import express from &quot;express&quot;;
import multer from &quot;multer&quot;;
import path from &quot;node:path&quot;;
import { fileTypeFromFile } from &quot;file-type&quot;;

// Configure storage &mdash; disk for simple cases, memory for streaming to S3
const upload = multer({
  storage: multer.diskStorage({
    destination: &quot;/tmp/uploads&quot;,
    filename: (req, file, cb) =&gt; {
      const ext = path.extname(file.originalname);
      cb(null, `${crypto.randomUUID()}${ext}`);
    }
  }),
  limits: { fileSize: 10 * 1024 * 1024 },     // 10 MB cap
  fileFilter: (req, file, cb) =&gt; {
    const allowed = [&quot;image/png&quot;, &quot;image/jpeg&quot;, &quot;image/webp&quot;, &quot;application/pdf&quot;];
    if (allowed.includes(file.mimetype)) cb(null, true);
    else cb(new Error(&quot;Bad file type&quot;));
  }
});

const app = express();

// Single file
app.post(&quot;/upload&quot;, upload.single(&quot;file&quot;), async (req, res) =&gt; {
  // Defense&ndash;in&ndash;depth: sniff actual content, don&apos;t trust client MIME
  const real = await fileTypeFromFile(req.file!.path);
  if (!real) return res.status(400).json({ error: &quot;Unknown file type&quot; });

  res.json({ filename: req.file!.filename, size: req.file!.size });
});

// Multiple files
app.post(&quot;/upload-many&quot;, upload.array(&quot;files&quot;, 5), (req, res) =&gt; {
  res.json({ count: req.files!.length });
});</code></pre>

<p>For production you almost never want files on the API server&rsquo;s disk:</p>

<ul>
<li><strong>Direct&ndash;to&ndash;cloud uploads</strong> &mdash; the API issues a presigned S3/R2/GCS URL, the browser PUTs straight to it. Saves bandwidth and keeps your servers stateless. AWS SDK <code>getSignedUrl</code>, Cloudflare R2 + S3 SDK, GCS signed URLs.</li>
<li><strong>Resumable / chunked uploads</strong> &mdash; <a href="https://tus.io">tus.io</a> protocol via <strong>tusd</strong> or <strong>uppy/companion</strong> for big files (videos) that can&rsquo;t survive a single network blip.</li>
<li><strong>Image / video transforms</strong> &mdash; <strong>Cloudflare Images</strong>, <strong>imgix</strong>, <strong>Cloudinary</strong>, <strong>Mux</strong> handle on&ndash;the&ndash;fly resize/format conversion.</li>
</ul>

<p>Always: validate file size + MIME + actual content; strip EXIF from images; run uploads through a virus scanner (<strong>ClamAV</strong>); serve with signed download URLs that expire; never put user&ndash;controlled filenames into a path without sanitizing.</p>'''


ANSWERS[90] = r'''<p><strong>Multer</strong> is the standard middleware for parsing <code>multipart/form-data</code> in Express &mdash; the format browsers use for <code>&lt;input type=&quot;file&quot;&gt;</code> uploads. It streams the request body, writes files to disk or memory, and exposes parsed fields on <code>req.body</code> + uploaded files on <code>req.file</code>/<code>req.files</code>.</p>

<pre><code>npm i multer @types/multer

import multer from &quot;multer&quot;;

// Disk storage &mdash; saves to a directory
const diskUpload = multer({
  storage: multer.diskStorage({
    destination: &quot;./uploads&quot;,
    filename: (req, file, cb) =&gt; cb(null, `${Date.now()}-${file.originalname}`)
  }),
  limits: { fileSize: 5 * 1024 * 1024 }       // 5MB
});

// Memory storage &mdash; keeps file as Buffer (good for piping to S3)
const memUpload = multer({ storage: multer.memoryStorage() });</code></pre>

<pre><code>// Different upload patterns
import express from &quot;express&quot;;
const app = express();

// Single file under field name &quot;avatar&quot;
app.post(&quot;/profile/avatar&quot;, diskUpload.single(&quot;avatar&quot;), (req, res) =&gt; {
  console.log(req.file);  // { fieldname, originalname, mimetype, size, path, filename }
  console.log(req.body);  // other text fields submitted with the form
  res.json({ url: `/uploads/${req.file!.filename}` });
});

// Multiple files under one field
app.post(&quot;/photos&quot;, diskUpload.array(&quot;photos&quot;, 10), (req, res) =&gt; {
  res.json({ count: (req.files as Express.Multer.File[]).length });
});

// Multiple fields, each with files
app.post(&quot;/listing&quot;,
  diskUpload.fields([
    { name: &quot;cover&quot;, maxCount: 1 },
    { name: &quot;gallery&quot;, maxCount: 8 }
  ]),
  (req, res) =&gt; res.json({ files: req.files })
);

// Form fields without files (use .none() or leave Multer off entirely)
app.post(&quot;/text-only&quot;, diskUpload.none(), (req, res) =&gt; res.json(req.body));</code></pre>

<p>Pipe to S3/R2 from memory storage:</p>

<pre><code>import { S3Client, PutObjectCommand } from &quot;@aws-sdk/client-s3&quot;;
const s3 = new S3Client({ region: &quot;us-east-1&quot; });

app.post(&quot;/upload&quot;, memUpload.single(&quot;file&quot;), async (req, res) =&gt; {
  const key = `uploads/${crypto.randomUUID()}`;
  await s3.send(new PutObjectCommand({
    Bucket: &quot;my-bucket&quot;,
    Key: key,
    Body: req.file!.buffer,
    ContentType: req.file!.mimetype
  }));
  res.json({ key });
});</code></pre>

<p>Limits + safety: always set <code>limits.fileSize</code> (Multer rejects oversized uploads early), validate <code>fileFilter</code> on MIME, sniff actual content with <code>file-type</code> after upload, scan with ClamAV, and never trust filenames. For big files (&gt;100MB) prefer <strong>presigned direct&ndash;to&ndash;S3 uploads</strong> or <strong>tus.io resumable</strong> &mdash; Multer is best for small/medium files where a single HTTP POST suffices.</p>'''


ANSWERS[91] = r'''<p><strong>Netlify</strong> deploys static + Jamstack apps with a git&ndash;driven workflow: push to a branch, Netlify builds, deploys, and gives you a preview URL per PR. Setup takes minutes for a React app:</p>

<pre><code># Option A: CLI (interactive setup)
npm i -g netlify-cli
netlify login
netlify init       # links the local repo to a Netlify site
netlify deploy --prod

# Option B: dashboard
# 1. Push your repo to GitHub
# 2. netlify.com -&gt; &quot;Add new site&quot; -&gt; &quot;Import from Git&quot;
# 3. Pick the repo, framework auto-detected (Vite/CRA/Next.js)
# 4. Build command: npm run build  /  Publish dir: dist (or build)</code></pre>

<pre><code># netlify.toml &mdash; check this file in to control build + redirects
[build]
  command = &quot;npm run build&quot;
  publish = &quot;dist&quot;

# SPA fallback &mdash; serve index.html for any unknown route
[[redirects]]
  from = &quot;/*&quot;
  to   = &quot;/index.html&quot;
  status = 200

# Cache headers
[[headers]]
  for = &quot;/assets/*&quot;
  [headers.values]
    Cache-Control = &quot;public, max-age=31536000, immutable&quot;</code></pre>

<p>What Netlify gives you out of the box:</p>

<ul>
<li><strong>Continuous deployment</strong> &mdash; push to <code>main</code> redeploys automatically.</li>
<li><strong>Preview deploys per PR</strong> &mdash; every PR gets a unique URL for review.</li>
<li><strong>Free HTTPS</strong> + custom domains via Let&rsquo;s Encrypt.</li>
<li><strong>Edge CDN</strong> &mdash; Netlify Edge globally distributes static assets.</li>
<li><strong>Functions</strong> &mdash; <code>netlify/functions/*.ts</code> become serverless API endpoints; <strong>Edge Functions</strong> run on Deno at the CDN edge.</li>
<li><strong>Forms</strong>, <strong>Identity</strong> (managed auth), <strong>Image CDN</strong>, <strong>A/B testing</strong> &mdash; all built in.</li>
</ul>

<p>Environment variables: dashboard &rarr; Site &rarr; Environment, or via <code>netlify env:set KEY value</code>. They&rsquo;re injected at build time (<code>VITE_</code>/<code>REACT_APP_</code> prefix for browser exposure) and at function runtime.</p>

<p>For a MERN app, Netlify hosts the React frontend; the Express API runs elsewhere (Render, Fly.io, Railway, AWS) and the React app calls it via CORS. Or convert the API to <strong>Netlify Functions</strong> for a single&ndash;platform deploy &mdash; works for low&ndash;traffic apps, but watch cold starts and the 10s execution limit.</p>

<p>Direct competitors in 2026: <strong>Vercel</strong> (Next.js&ndash;native), <strong>Cloudflare Pages</strong> (cheapest at scale, integrated Workers), <strong>AWS Amplify Hosting</strong>. Netlify remains the simplest for non&ndash;Next stacks (Vite, Astro, Hugo, Eleventy).</p>'''


ANSWERS[92] = r'''<p><strong>Vercel</strong> is the company behind Next.js and the most polished platform for deploying React/Next apps. Setup takes literally one command:</p>

<pre><code># CLI
npm i -g vercel
vercel login
vercel              # first run: imports the project, asks framework
vercel --prod       # deploy to production

# Or via the dashboard
# 1. Push to GitHub/GitLab/Bitbucket
# 2. vercel.com -&gt; &quot;Import Project&quot;
# 3. Framework auto-detected (Next.js, Vite, CRA, Astro, Remix, Nuxt, SvelteKit, etc.)
# 4. Click Deploy</code></pre>

<p>Out of the box you get:</p>

<ul>
<li><strong>Preview deploys per pull request</strong> &mdash; every commit gets a unique URL.</li>
<li><strong>Production deploys on merge to main</strong> &mdash; with optional manual promotion.</li>
<li><strong>Edge CDN</strong> globally distributing static assets and HTML.</li>
<li><strong>Serverless / Edge Functions</strong> for Next.js API routes &mdash; auto&ndash;generated from <code>app/api/*</code>.</li>
<li><strong>Image Optimization</strong> via <code>next/image</code> &mdash; resize, WebP/AVIF, lazy load.</li>
<li><strong>Analytics</strong> &mdash; Web Vitals + Speed Insights without third&ndash;party scripts.</li>
<li><strong>Vercel KV</strong> (Redis), <strong>Postgres</strong>, <strong>Blob</strong> &mdash; integrated managed storage.</li>
<li><strong>v0</strong> &mdash; AI&ndash;assisted UI generation (separate product, integrates with Vercel).</li>
</ul>

<pre><code># vercel.json (optional, for fine control)
{
  &quot;buildCommand&quot;: &quot;npm run build&quot;,
  &quot;outputDirectory&quot;: &quot;dist&quot;,
  &quot;rewrites&quot;: [
    { &quot;source&quot;: &quot;/api/(.*)&quot;, &quot;destination&quot;: &quot;https://api.example.com/$1&quot; }
  ],
  &quot;headers&quot;: [
    {
      &quot;source&quot;: &quot;/assets/(.*)&quot;,
      &quot;headers&quot;: [{ &quot;key&quot;: &quot;Cache-Control&quot;, &quot;value&quot;: &quot;public, max-age=31536000, immutable&quot; }]
    }
  ]
}</code></pre>

<p>For Next.js apps Vercel is the path of least resistance &mdash; it understands SSR, ISR, RSC, streaming, middleware, and edge functions natively. For other React stacks (Vite, CRA, Astro) it works just as well as a static host.</p>

<p>2026 alternatives worth knowing: <strong>Cloudflare Pages</strong> (similar feature set, cheaper at scale, integrated Workers + R2 + D1), <strong>Netlify</strong>, <strong>AWS Amplify</strong>, <strong>Render</strong>, self&ndash;hosted via <strong>Coolify</strong>/<strong>Dokploy</strong>/<strong>Sliplane</strong>. Vercel pricing scales with bandwidth and function invocations &mdash; great until you&rsquo;re very large.</p>'''


ANSWERS[93] = r'''<p><strong>Vercel environment variables</strong> are configured per&ndash;environment (Production, Preview, Development) and exposed to your build + runtime. Set them in three ways:</p>

<pre><code># 1) Vercel CLI
vercel env add DATABASE_URL production
# (paste the value when prompted, available in next deploy)

vercel env add API_KEY preview     # for PR preview deploys
vercel env add LOG_LEVEL development  # only for `vercel dev`

# Pull production env down to a local .env.local for testing
vercel env pull .env.local

# 2) Dashboard
# Project -&gt; Settings -&gt; Environment Variables
# Add each var, choose which environments it applies to

# 3) vercel.json (only for non-secret values)
{
  &quot;env&quot;: { &quot;NEXT_PUBLIC_APP_NAME&quot;: &quot;MyApp&quot; }
}</code></pre>

<p>How they&rsquo;re consumed:</p>

<ul>
<li><strong>Server&ndash;side</strong> (Next.js Server Components, API routes, Edge Functions): just <code>process.env.DATABASE_URL</code>. Never exposed to the browser.</li>
<li><strong>Client&ndash;side</strong>: variables prefixed with <code>NEXT_PUBLIC_</code> (Next.js) or <code>VITE_</code> (Vite) get inlined at build time and shipped to the browser. Don&rsquo;t put secrets in these.</li>
<li><strong>Build&ndash;time</strong>: any var available during <code>vercel build</code> &mdash; useful for static generation that needs an API key to fetch.</li>
</ul>

<pre><code>// Server-only: safe for secrets
export async function GET() {
  const data = await fetch(&quot;https://api.example.com&quot;, {
    headers: { Authorization: `Bearer ${process.env.SECRET_API_KEY}` }
  }).then(r =&gt; r.json());
  return Response.json(data);
}

// Client-side: prefix with NEXT_PUBLIC_, never put secrets here
console.log(process.env.NEXT_PUBLIC_ANALYTICS_ID);</code></pre>

<p>Best practices:</p>

<ul>
<li>Use <strong>different values per environment</strong> &mdash; production hits the prod DB, preview hits a staging DB, dev hits localhost.</li>
<li>Scope <strong>preview&ndash;only secrets</strong> separately so PR previews don&rsquo;t accidentally write to production data.</li>
<li>Mark sensitive variables as <strong>Sensitive</strong> in the dashboard &mdash; the value becomes write&ndash;only and won&rsquo;t be shown in logs or to teammates.</li>
<li>For long&ndash;lived secrets (API keys, DB URLs), pull from a secrets manager (<strong>Doppler</strong>, <strong>Infisical</strong>, <strong>Vault</strong>, <strong>AWS Secrets Manager</strong>) via Vercel&rsquo;s native integrations &mdash; rotation happens centrally.</li>
<li>For OIDC&ndash;based cloud auth, use Vercel&rsquo;s <strong>OIDC tokens</strong> &mdash; short&ndash;lived credentials to AWS/GCP without storing static keys.</li>
</ul>

<p>Common gotcha: the same variable name with different values in Production vs Preview means a PR preview can behave differently than expected. Add visible indicators (banner, console log) showing the environment so reviewers know where they are.</p>'''


ANSWERS[94] = r'''<p><strong>Cloudflare</strong> is a global edge network providing DNS, CDN, WAF, DDoS protection, and a developer platform (Workers, Pages, R2, D1, KV, Durable Objects). For DNS + CDN setup:</p>

<pre><code># 1. Sign up at cloudflare.com, add your domain
# 2. Cloudflare scans your existing DNS records, imports them
# 3. Switch your registrar&apos;s nameservers to Cloudflare&apos;s (e.g. ada.ns.cloudflare.com)
#    Propagation typically 5 minutes to 24 hours
# 4. DNS becomes manageable from the Cloudflare dashboard or API</code></pre>

<p>DNS records you&rsquo;ll typically configure for a MERN app:</p>

<table>
<tr><th>Type</th><th>Name</th><th>Value</th><th>Proxy?</th></tr>
<tr><td>A or CNAME</td><td>@ or app</td><td>Vercel/Netlify alias or origin IP</td><td>✅ Proxy on</td></tr>
<tr><td>CNAME</td><td>www</td><td>example.com</td><td>✅</td></tr>
<tr><td>CNAME</td><td>api</td><td>your-api.fly.dev / render.com</td><td>✅</td></tr>
<tr><td>MX</td><td>@</td><td>Google/Fastmail/Zoho mail servers</td><td>❌ DNS only</td></tr>
<tr><td>TXT</td><td>@</td><td>SPF, DMARC, domain verification</td><td>❌</td></tr>
</table>

<p>The <strong>orange cloud</strong> (proxy) means traffic flows through Cloudflare&rsquo;s edge &mdash; that&rsquo;s where you get free CDN, DDoS protection, WAF, bot fight mode, automatic HTTPS, HTTP/3, and Brotli/Zstd compression. Mail records and direct&ndash;DB CNAMEs stay grey&ndash;cloud (DNS only).</p>

<p>Configure caching via <strong>Page Rules</strong> or the newer <strong>Cache Rules</strong>:</p>

<pre><code># Cache Rule: cache /assets/* aggressively
When incoming requests match: URI Path matches /assets/*
Then: Cache eligibility = Eligible for cache
       Edge TTL = 1 year
       Browser TTL = 1 year

# Cache Rule: bypass /api/*
When: URI Path matches /api/*
Then: Cache eligibility = Bypass cache</code></pre>

<p>Other features you&rsquo;ll likely turn on:</p>

<ul>
<li><strong>SSL/TLS &rarr; Full (strict)</strong> &mdash; HTTPS end&ndash;to&ndash;end with cert validation.</li>
<li><strong>HSTS</strong> with preload (after testing).</li>
<li><strong>Bot Fight Mode</strong> + <strong>WAF managed rules</strong> for free tier protection.</li>
<li><strong>Always Online</strong> serves cached pages if your origin is down.</li>
<li><strong>Workers</strong> for edge logic; <strong>Pages</strong> for static hosting; <strong>R2</strong> for object storage with no egress fees.</li>
</ul>

<p>For a MERN app the typical setup: Cloudflare DNS + proxy in front of <strong>Vercel/Netlify</strong> for the React app, and a separate subdomain (<code>api.example.com</code>) routing to the Express API on <strong>Fly.io/Render/Railway</strong> &mdash; all behind Cloudflare&rsquo;s edge.</p>'''


ANSWERS[95] = r'''<p><strong>AWS S3</strong> stores objects (files) in buckets &mdash; durable, cheap, infinitely scalable. For a MERN app, S3 is the standard place to keep user uploads, generated reports, and static assets that aren&rsquo;t in your bundle.</p>

<pre><code>npm i @aws-sdk/client-s3 @aws-sdk/s3-request-presigner</code></pre>

<pre><code># Create a bucket
aws s3 mb s3://my-app-uploads --region us-east-1

# Configure CORS so browser uploads work (cors.json + apply)
aws s3api put-bucket-cors --bucket my-app-uploads --cors-configuration file://cors.json
# cors.json:
# { &quot;CORSRules&quot;: [{
#     &quot;AllowedHeaders&quot;: [&quot;*&quot;],
#     &quot;AllowedMethods&quot;: [&quot;GET&quot;, &quot;PUT&quot;, &quot;POST&quot;, &quot;HEAD&quot;],
#     &quot;AllowedOrigins&quot;: [&quot;https://app.example.com&quot;],
#     &quot;ExposeHeaders&quot;: [&quot;ETag&quot;]
# }] }</code></pre>

<pre><code>// Server: issue a presigned URL so the browser uploads directly
import { S3Client, PutObjectCommand, GetObjectCommand } from &quot;@aws-sdk/client-s3&quot;;
import { getSignedUrl } from &quot;@aws-sdk/s3-request-presigner&quot;;

const s3 = new S3Client({ region: &quot;us-east-1&quot; });

app.post(&quot;/uploads/presign&quot;, requireAuth, async (req, res) =&gt; {
  const key = `users/${req.user.id}/${crypto.randomUUID()}-${req.body.filename}`;
  const url = await getSignedUrl(
    s3,
    new PutObjectCommand({
      Bucket: &quot;my-app-uploads&quot;, Key: key,
      ContentType: req.body.contentType,
      ContentLength: req.body.size,
      Metadata: { uploadedBy: req.user.id }
    }),
    { expiresIn: 60 * 5 }   // 5-minute window
  );
  res.json({ url, key });
});

// React: upload directly to S3
const { url, key } = await fetch(&quot;/uploads/presign&quot;, { method: &quot;POST&quot;, body: ... }).then(r =&gt; r.json());
await fetch(url, { method: &quot;PUT&quot;, body: file });
// Save key + metadata to MongoDB so you can recall the file later</code></pre>

<p>Serve files via <strong>CloudFront</strong> in front of S3:</p>

<ul>
<li>Block direct S3 public access; allow only CloudFront via Origin Access Control (OAC).</li>
<li>Use signed CloudFront URLs for private files.</li>
<li>Set long cache TTLs and rely on object key changes for invalidation.</li>
</ul>

<p>2026 alternatives worth knowing:</p>

<ul>
<li><strong>Cloudflare R2</strong> &mdash; S3&ndash;compatible API, <strong>zero egress fees</strong>, much cheaper for read&ndash;heavy apps. Drop&ndash;in via the same AWS SDK.</li>
<li><strong>Backblaze B2</strong> &mdash; cheapest storage, S3&ndash;compatible.</li>
<li><strong>Tigris</strong> &mdash; globally distributed S3&ndash;compatible storage.</li>
<li><strong>Vercel Blob</strong>, <strong>Supabase Storage</strong>, <strong>Cloudinary</strong> &mdash; managed convenience layers on top of object storage.</li>
</ul>

<p>Whichever you pick, the patterns are the same: presigned upload URLs, direct&ndash;to&ndash;cloud uploads, signed download URLs with expiration, content&ndash;type sniffing on receipt, virus scan via ClamAV worker, EXIF strip on images.</p>'''


ANSWERS[96] = r'''<p><strong>AWS Lambda</strong> runs your code without provisioning servers &mdash; you upload a function, AWS spins up containers on demand, scales to thousands of concurrent invocations, and bills per request + execution duration. Common uses in a MERN app: image processing, scheduled jobs, webhook receivers, and entire APIs via API Gateway or Lambda Function URLs.</p>

<pre><code># Easiest path: Serverless Framework or AWS SAM CLI
npm i -D serverless serverless-offline
npx serverless create --template aws-nodejs-typescript --path my-api</code></pre>

<pre><code># serverless.yml
service: my-api
provider:
  name: aws
  runtime: nodejs22.x
  region: us-east-1
  environment:
    MONGODB_URI: ${env:MONGODB_URI}

functions:
  hello:
    handler: src/handlers/hello.main
    events:
      - httpApi: { path: /hello, method: get }
  resize:
    handler: src/handlers/resize.main
    events:
      - s3: { bucket: my-app-uploads, event: s3:ObjectCreated:* }
  cron:
    handler: src/handlers/digest.main
    events:
      - schedule: rate(1 hour)</code></pre>

<pre><code>// src/handlers/hello.ts
import type { APIGatewayProxyHandlerV2 } from &quot;aws-lambda&quot;;

export const main: APIGatewayProxyHandlerV2 = async (event) =&gt; {
  return {
    statusCode: 200,
    headers: { &quot;content-type&quot;: &quot;application/json&quot; },
    body: JSON.stringify({ name: event.queryStringParameters?.name ?? &quot;world&quot; })
  };
};

// Deploy: npx serverless deploy</code></pre>

<p>Patterns to know:</p>

<ul>
<li><strong>Cold starts</strong> &mdash; the first invocation of a cold container takes 100&ndash;1500ms; warm invocations are &lt;10ms. Use <strong>provisioned concurrency</strong> for latency&ndash;sensitive APIs.</li>
<li><strong>Connection pooling</strong> &mdash; don&rsquo;t open a new MongoDB connection per invocation; cache the client outside the handler so it&rsquo;s reused across warm invocations. Atlas supports up to ~10K connections; pair with <strong>Atlas Data API</strong> or <strong>MongoDB driver with maxPoolSize: 1</strong>.</li>
<li><strong>Limits</strong> &mdash; 15&ndash;minute max execution, 10GB memory, 250MB deployment package (or use container images up to 10GB).</li>
<li><strong>Local dev</strong> &mdash; <code>serverless-offline</code> or <code>sam local</code> emulate Lambda locally.</li>
</ul>

<p>2026 alternatives often easier than Lambda:</p>

<ul>
<li><strong>Cloudflare Workers</strong> &mdash; ~5ms cold start, runs at the edge, V8 isolates not containers. Free tier is generous.</li>
<li><strong>Vercel Edge Functions</strong> &mdash; same idea, integrated with Next.js.</li>
<li><strong>AWS Lambda + SnapStart</strong> &mdash; near&ndash;zero cold starts on supported runtimes (Java first, others rolling out).</li>
<li><strong>Fly Machines</strong>, <strong>Cloud Run</strong>, <strong>Railway</strong> &mdash; container&ndash;per&ndash;request with autoscale to zero.</li>
</ul>

<p>For a typical MERN backend, prefer a long&ndash;running container (Render/Fly/Railway) over Lambda &mdash; persistent Mongo connections are simpler and cold starts disappear. Reserve Lambda for image/video pipelines, S3 triggers, scheduled cron, and webhook receivers where its scale&ndash;to&ndash;zero economics shine.</p>'''


ANSWERS[97] = r'''<p><strong>AWS API Gateway</strong> sits in front of your backend (Lambda, ECS, EC2) providing routing, authentication, throttling, request validation, and HTTP-to-event translation. There are two flavors: <strong>HTTP API</strong> (newer, ~70% cheaper, simpler) and <strong>REST API</strong> (older, more features). For most MERN apps you want HTTP API.</p>

<pre><code># Serverless Framework example tying API Gateway HTTP API to Lambdas
service: my-api
provider:
  name: aws
  runtime: nodejs22.x
  httpApi:
    cors: true
    authorizers:
      jwt:
        type: jwt
        identitySource: $request.header.Authorization
        issuerUrl: https://auth.example.com
        audience:
          - my-api

functions:
  listProducts:
    handler: src/products.list
    events:
      - httpApi: { path: /products, method: get }

  createProduct:
    handler: src/products.create
    events:
      - httpApi:
          path: /products
          method: post
          authorizer: { name: jwt }

  webhook:
    handler: src/webhooks.stripe
    events:
      - httpApi: { path: /webhooks/stripe, method: post }</code></pre>

<p>Features that earn API Gateway its keep:</p>

<ul>
<li><strong>JWT/Cognito authorizers</strong> &mdash; validate tokens at the gateway before invoking your function. Free request rejections.</li>
<li><strong>Throttling</strong> &mdash; per&ndash;route + per&ndash;API key rate limits.</li>
<li><strong>Custom domain + ACM cert</strong> &mdash; <code>api.example.com</code> with HTTPS managed for you.</li>
<li><strong>Stages</strong> &mdash; dev / staging / prod with separate variables and rate limits.</li>
<li><strong>WebSockets API</strong> (REST flavor) &mdash; managed WebSocket fan&ndash;out without running your own.</li>
<li><strong>Request validation</strong> &mdash; reject malformed bodies before hitting the function.</li>
<li><strong>WAF integration</strong> &mdash; AWS WAF rules in front of all routes.</li>
</ul>

<pre><code>// Lambda handler invoked by API Gateway HTTP API
import type { APIGatewayProxyHandlerV2 } from &quot;aws-lambda&quot;;

export const list: APIGatewayProxyHandlerV2 = async (event) =&gt; {
  const products = await Product.find().lean();
  return { statusCode: 200, body: JSON.stringify(products) };
};</code></pre>

<p>2026 alternatives that often beat API Gateway:</p>

<ul>
<li><strong>Cloudflare Workers + Hono</strong> &mdash; cheaper, ~5ms cold start, integrated routing.</li>
<li><strong>Vercel Edge Functions / Next.js Route Handlers</strong> &mdash; if you&rsquo;re on Vercel, no separate gateway needed.</li>
<li><strong>Hono</strong> or <strong>Fastify</strong> on a long&ndash;running container (Render, Fly, Cloud Run) with <strong>nginx/Caddy/Traefik</strong> for routing &mdash; simpler operationally for medium scale.</li>
<li><strong>Lambda Function URLs</strong> &mdash; direct HTTPS endpoint per Lambda; no API Gateway needed for simple cases.</li>
</ul>

<p>API Gateway shines when you want a managed front door across many backend services, fine&ndash;grained throttling per consumer, or AWS&ndash;native auth (Cognito). For pure simplicity in a MERN stack you can usually skip it.</p>'''


ANSWERS[98] = r'''<p><strong>MongoDB Atlas</strong> includes built&ndash;in performance tooling that turns &ldquo;why is this query slow&rdquo; from guesswork into a checklist:</p>

<ul>
<li><strong>Performance Advisor</strong> &mdash; recommends missing indexes by analyzing real query patterns. Gives you the exact <code>createIndex</code> command and an estimate of impact. Free on M10+.</li>
<li><strong>Query Profiler / Query Insights</strong> &mdash; lists the slowest queries, their shape, frequency, and which indexes they use. Find the heavy hitters.</li>
<li><strong>Real-Time Performance Panel</strong> &mdash; current ops in flight: ops/sec, latency, network throughput, queue depths.</li>
<li><strong>Metrics</strong> &mdash; CPU, memory, working set, page faults, cache hit ratio, replication lag, oplog window.</li>
<li><strong>Alerts</strong> &mdash; thresholds on the above, delivered to PagerDuty/Slack/email.</li>
</ul>

<pre><code>// Profile a specific query yourself
db.orders.find({ tenantId: &quot;t1&quot; })
  .sort({ createdAt: -1 })
  .limit(20)
  .explain(&quot;executionStats&quot;);

// Look for:
//   stage: IXSCAN  (good)  vs COLLSCAN (bad)
//   totalDocsExamined ≈ nReturned (good ratio)
//   executionTimeMillis (low)
//   totalKeysExamined &mdash; bigger than nReturned means index over-scan</code></pre>

<p>Optimization checklist when something is slow:</p>

<ol>
<li><strong>Add the right index</strong> &mdash; ESR rule: equality fields, then sort, then range. Use Performance Advisor recommendations.</li>
<li><strong>Project only fields you need</strong> &mdash; <code>.find({}, { _id: 1, name: 1 })</code>. Smaller docs over the wire, less RAM pressure.</li>
<li><strong>Limit result sets</strong> &mdash; cursor pagination beats <code>skip</code> at scale.</li>
<li><strong>Reshape pipelines</strong> &mdash; put <code>$match</code>/<code>$sort</code> first so they use indexes; use <code>$merge</code> to materialize repeated aggregations.</li>
<li><strong>Working set in RAM</strong> &mdash; if pages are constantly being loaded from disk, scale up the cluster tier or shard.</li>
<li><strong>Drop unused indexes</strong> &mdash; <code>db.collection.aggregate([{ $indexStats: {} }])</code> shows which haven&rsquo;t been used. Indexes cost RAM + write speed.</li>
<li><strong>Connection pooling</strong> &mdash; if you see &ldquo;connection refused&rdquo; or saturation, raise <code>maxPoolSize</code> or use Atlas&rsquo;s connection limits view.</li>
</ol>

<p>Capacity planning: target <strong>cache hit ratio &gt;95%</strong>, <strong>working set size &lt;~80% of RAM</strong>, <strong>oplog window &gt;24h</strong>, <strong>replication lag &lt;10s</strong>. If any of these slip, scale up before users notice. Atlas Auto&ndash;Tier scales storage automatically; Atlas Auto&ndash;Scaling can adjust compute on a schedule.</p>

<p>For workloads that have outgrown OLTP Mongo &mdash; high&ndash;concurrency analytics, full&ndash;table scans, joins across many collections &mdash; replicate to a columnar warehouse (<strong>ClickHouse</strong>, <strong>Tinybird</strong>, <strong>BigQuery</strong>, <strong>Snowflake</strong>) via Atlas Stream Processing or Debezium CDC. Mongo is excellent for operational queries; the wrong tool for ad&ndash;hoc OLAP at scale.</p>'''


ANSWERS[99] = r'''<p><strong>Datadog</strong> is a unified observability platform &mdash; metrics, logs, traces, RUM (real user monitoring), profiles, security &mdash; in one UI. It&rsquo;s powerful, expensive, and the most&ndash;deployed APM in production today.</p>

<p>Setup for a Node + Express MERN app:</p>

<pre><code>npm i dd-trace pino pino-datadog-transport</code></pre>

<pre><code>// server.ts &mdash; first import, before everything else
import &quot;./tracer&quot;;
import express from &quot;express&quot;;
// ... rest of your app

// tracer.ts
import tracer from &quot;dd-trace&quot;;
tracer.init({
  service: &quot;my-api&quot;,
  env: process.env.NODE_ENV ?? &quot;dev&quot;,
  version: process.env.GIT_SHA,
  logInjection: true,                  // adds trace IDs to logs automatically
  profiling: true,                     // continuous profiler
  runtimeMetrics: true                 // Node event loop, GC, heap
});</code></pre>

<pre><code># Run with the Datadog Agent (sidecar)
# Local dev: docker run agent
# Production: install on the VM/ECS task, or use Datadog&apos;s K8s helm chart

# Environment vars the agent reads
DD_API_KEY=xxx                         # from Datadog dashboard
DD_SITE=datadoghq.com
DD_ENV=production
DD_SERVICE=my-api
DD_VERSION=1.4.2</code></pre>

<p>Out of the box you get:</p>

<ul>
<li><strong>APM traces</strong> &mdash; every HTTP request, with auto&ndash;instrumented Express, Mongoose, Redis, fetch.</li>
<li><strong>Service map</strong> &mdash; visual graph of which services call which.</li>
<li><strong>Logs</strong> &mdash; ship via the agent or an HTTP endpoint; trace IDs auto&ndash;link logs to traces.</li>
<li><strong>Metrics</strong> &mdash; Node runtime, custom business counters via <code>tracer.dogstatsd.increment(&quot;orders.created&quot;)</code>.</li>
<li><strong>Profiles</strong> &mdash; CPU + heap profiling continuously, find slow functions in production.</li>
<li><strong>RUM</strong> &mdash; real user monitoring on the React side via <code>@datadog/browser-rum</code>; LCP, INP, CLS, errors, sessions.</li>
<li><strong>Synthetics</strong> &mdash; uptime + browser tests from global locations.</li>
<li><strong>Watchdog</strong> &mdash; ML&ndash;based anomaly detection that flags incidents you didn&rsquo;t set alerts for.</li>
</ul>

<p>For React RUM:</p>

<pre><code>import { datadogRum } from &quot;@datadog/browser-rum&quot;;
datadogRum.init({
  applicationId: &quot;...&quot;, clientToken: &quot;...&quot;, site: &quot;datadoghq.com&quot;,
  service: &quot;my-app-web&quot;, env: import.meta.env.MODE,
  version: import.meta.env.VITE_GIT_SHA,
  sessionSampleRate: 100, sessionReplaySampleRate: 20,
  trackUserInteractions: true, trackResources: true, trackLongTasks: true
});</code></pre>

<p>2026 alternatives at meaningful cost savings: <strong>Grafana Cloud / Tempo / Loki / Mimir</strong>, <strong>Honeycomb</strong> (best traces), <strong>New Relic</strong>, <strong>Sentry</strong> (errors + tracing), <strong>Axiom</strong> (logs + analytics, cheap), <strong>Better Stack</strong> (uptime + logs), <strong>SigNoz</strong> / <strong>HyperDX</strong> (open source). All build on <strong>OpenTelemetry</strong> &mdash; instrumenting with the OTel SDK keeps you portable across vendors. Datadog wins on completeness; Honeycomb on trace UX; the OSS options on cost.</p>'''


ANSWERS[100] = r'''<p>Security best practices for a MERN stack are layered defense &mdash; no single mitigation suffices. The 2026 baseline:</p>

<table>
<tr><th>Layer</th><th>What to do</th><th>Tools</th></tr>
<tr><td>Identity</td><td>Passkeys + MFA, short&ndash;lived tokens, refresh rotation with reuse detection, SSO + SCIM for B2B</td><td>Clerk, Auth0, WorkOS, Stytch, Better Auth</td></tr>
<tr><td>Transport</td><td>TLS 1.3 + HSTS preload, mTLS east&ndash;west, no public DB</td><td>Cloudflare, Caddy, ACM, Istio</td></tr>
<tr><td>Application</td><td>Helmet, strict CSP, Zod input validation, tenant scoping, never trust client IDs</td><td>helmet, Zod, Valibot</td></tr>
<tr><td>AuthZ</td><td>RBAC + ReBAC, centralized authz</td><td>SpiceDB, OpenFGA, Cerbos, Permify, Oso</td></tr>
<tr><td>Secrets</td><td>Vault &mdash; never commit .env, rotate regularly, OIDC for cloud access</td><td>Doppler, Infisical, AWS Secrets Manager, Vault</td></tr>
<tr><td>Data</td><td>Atlas at&ndash;rest encryption, CSFLE/Queryable Encryption for PII, tokenization for cards</td><td>MongoDB CSFLE, Skyflow, Basis Theory</td></tr>
<tr><td>Supply chain</td><td>Lockfile, Sigstore + cosign, GitHub Trusted Publishers, dep scanning</td><td>Socket.dev, Snyk, Dependabot, GitGuardian</td></tr>
<tr><td>Runtime</td><td>WAF + bot mgmt, DDoS protection, rate limiting per tier</td><td>Cloudflare WAF, Datadog ASM, Akamai</td></tr>
<tr><td>Observability</td><td>Audit log every privileged action, immutable storage, alerts on anomalies</td><td>Datadog, Honeycomb, AWS QLDB</td></tr>
<tr><td>Compliance</td><td>SOC 2 / HIPAA / ISO 27001 evidence automation, trust center for buyers</td><td>Vanta, Drata, SecureFrame, Sprinto</td></tr>
</table>

<pre><code>// Critical Express snippets
import helmet from &quot;helmet&quot;;
import rateLimit from &quot;express-rate-limit&quot;;
import mongoSanitize from &quot;express-mongo-sanitize&quot;;
import cors from &quot;cors&quot;;

app.use(helmet({
  contentSecurityPolicy: { directives: { /* nonce-based, no &apos;unsafe-inline&apos; */ } },
  hsts: { maxAge: 63072000, includeSubDomains: true, preload: true }
}));
app.use(cors({ origin: [&quot;https://app.example.com&quot;], credentials: true }));
app.use(express.json({ limit: &quot;1mb&quot; }));
app.use(mongoSanitize());                                  // strip $ and . from inputs
app.use(rateLimit({ windowMs: 60_000, max: 100 }));         // basic per-IP

// Always validate at the boundary, never trust client IDs
app.get(&quot;/orders/:id&quot;, requireAuth, async (req, res) =&gt; {
  const order = await Order.findOne({
    _id: req.params.id, tenantId: req.auth.tenantId    // tenant scope ALWAYS
  });
  if (!order) return res.status(404).end();
  res.json(order);
});</code></pre>

<p>Operational rituals that catch what code review misses:</p>

<ul>
<li><strong>Threat model</strong> each major feature (STRIDE).</li>
<li><strong>SAST/DAST in CI</strong> &mdash; Semgrep, CodeQL, Snyk Code, OWASP ZAP.</li>
<li><strong>Pen test + bug bounty</strong> annually &mdash; HackerOne, Intigriti.</li>
<li><strong>Quarterly access reviews</strong> &mdash; remove dormant users, audit role grants.</li>
<li><strong>Incident response runbooks</strong> &mdash; rehearse via tabletop exercises; document RTO/RPO.</li>
<li><strong>24h CVE patch SLA</strong> for high&ndash;severity dependency advisories.</li>
<li><strong>Regular dependency audits</strong> &mdash; <code>pnpm audit</code> + Renovate/Dependabot keep things current.</li>
</ul>

<p>Security is not a checkbox &mdash; it&rsquo;s a continuous program. The single biggest leverage point in 2026 is <strong>never run your own auth or payments</strong>: managed services (Clerk/Auth0/Stripe) handle 95% of compliance work and have far better security teams than yours. Spend your effort on tenant scoping, audit logging, and threat modeling the parts of your app that are uniquely yours.</p>'''
