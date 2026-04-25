"""Node.Js / Advanced — detailed answers."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p>The event loop is Node's scheduler, implemented in C by <strong>libuv</strong>. It lets a single JS thread handle thousands of concurrent connections by parking async work and running callbacks when the work completes.</p>
<p>Each iteration ("tick") runs through six ordered phases, each with its own FIFO callback queue:</p>
<ol>
  <li><strong>Timers</strong> — <code>setTimeout</code>/<code>setInterval</code> callbacks whose time has elapsed.</li>
  <li><strong>Pending callbacks</strong> — deferred I/O callbacks (e.g., certain TCP errors).</li>
  <li><strong>Idle, prepare</strong> — internal housekeeping.</li>
  <li><strong>Poll</strong> — the heart: retrieves new I/O events; runs most I/O callbacks. If no timers are pending and nothing else is scheduled, it blocks here waiting for I/O (up to a computed maximum).</li>
  <li><strong>Check</strong> — <code>setImmediate</code> callbacks.</li>
  <li><strong>Close callbacks</strong> — <code>socket.on("close", ...)</code> and similar.</li>
</ol>
<p><strong>Between every callback</strong> (not just between phases), Node drains two higher-priority queues: <code>process.nextTick</code> first, then the microtask queue (resolved Promises, <code>queueMicrotask</code>). These can starve the loop if they keep scheduling more of themselves — classic "microtask starvation."</p>
<p>Actual async I/O is delegated: network sockets use the OS's kernel polling (<code>epoll</code>/<code>kqueue</code>/IOCP) directly, while file I/O, DNS, and crypto use libuv's <strong>thread pool</strong> (default 4 threads, tunable via <code>UV_THREADPOOL_SIZE</code>). When work finishes, the completion callback is pushed to the appropriate phase queue. Your JS code itself is never preempted — it runs to completion before the loop advances.</p>
'''

ANSWERS[2] = r'''
<p>Node has <em>no</em> async magic at the language level — async behavior is a collaboration between V8, libuv, and the OS. When you call <code>fs.readFile(path, cb)</code>, Node packages the work as a <strong>libuv request</strong>, hands it off, and returns immediately. Your JS thread continues executing other code.</p>
<p>What happens next depends on the operation's nature:</p>
<ul>
  <li><strong>Network I/O</strong> (TCP, HTTP, DNS with <code>c-ares</code>) — libuv registers the socket with the OS's multiplexer (<code>epoll</code> on Linux, <code>kqueue</code> on BSD/macOS, IOCP on Windows). The OS notifies libuv when the socket is readable/writable. No thread is occupied while waiting.</li>
  <li><strong>File I/O, DNS (getaddrinfo), crypto, zlib, CPU hooks</strong> — dispatched to libuv's <strong>thread pool</strong> (4 threads by default). Each thread performs the blocking syscall in isolation.</li>
  <li><strong>Timers</strong> — tracked in a min-heap; libuv computes how long the poll phase can block.</li>
  <li><strong>Microtasks</strong> (Promises) — queued inside V8; drained between every JS callback.</li>
</ul>
<p>When work completes, libuv pushes the callback onto the appropriate event-loop phase queue. On the next matching phase, the loop runs it on the single JS thread. Because all callbacks share that thread, blocking it (a long loop, sync I/O, heavy JSON.parse) stalls everything.</p>
<p><strong>Key insight:</strong> "Non-blocking" doesn't mean no blocking happens — it means the blocking is pushed to OS kernels or libuv's thread pool, leaving your JS thread free.</p>
'''

ANSWERS[3] = r'''
<p>Both use an event loop, but the environments differ significantly.</p>
<table>
  <thead><tr><th>Aspect</th><th>Node.js</th><th>Browser</th></tr></thead>
  <tbody>
    <tr><td>Implementation</td><td>libuv (C)</td><td>HTML spec (<em>task</em> + <em>microtask</em> queues)</td></tr>
    <tr><td>Phases</td><td>6 distinct phases (timers, poll, check, ...)</td><td>Task queue + render steps + microtasks</td></tr>
    <tr><td>Unique primitives</td><td><code>setImmediate</code>, <code>process.nextTick</code></td><td><code>requestAnimationFrame</code>, <code>requestIdleCallback</code></td></tr>
    <tr><td>I/O model</td><td>Kernel multiplexing + thread pool</td><td>Web APIs (fetch, XHR, timers) provided by host</td></tr>
    <tr><td>Rendering</td><td>None</td><td>Paint/layout between tasks</td></tr>
    <tr><td>Workers</td><td><code>worker_threads</code> (shared memory via <code>SharedArrayBuffer</code>)</td><td>Web Workers (message-passing only, no shared context)</td></tr>
  </tbody>
</table>
<p><strong>Microtask scheduling differs subtly:</strong> in browsers, microtasks drain after each <em>task</em>. In Node 11+, microtasks drain after each <em>individual callback within a phase</em> — closer to browser behavior but with phase boundaries that don't exist in browsers.</p>
<p><strong><code>process.nextTick</code> has no browser equivalent</strong> — it runs even higher priority than microtasks and is a Node-specific escape hatch often used to defer work until after the current operation but before any I/O.</p>
<p><strong>Browsers must interleave rendering</strong> — timer callbacks may be throttled on background tabs, <code>setTimeout(fn, 0)</code> has a 4 ms minimum after nested calls. Node has no such constraints; timers fire as soon as the loop reaches the timers phase.</p>
'''

ANSWERS[4] = r'''
<p>Graceful shutdown means: stop accepting new work, let in-flight work finish, close resources, then exit — instead of killing the process mid-request and leaving clients with broken connections or DB transactions hanging.</p>
<pre><code>const server = app.listen(3000);
const connections = new Set();
server.on("connection", (c) =&gt; {
  connections.add(c);
  c.on("close", () =&gt; connections.delete(c));
});

let shuttingDown = false;

async function shutdown(signal) {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log(`${signal} received — shutting down`);

  // 1. Stop accepting new requests
  server.close(() =&gt; console.log("server closed"));

  // 2. Set a hard deadline — don't hang forever
  const killTimer = setTimeout(() =&gt; {
    console.error("forceful shutdown after 30s");
    process.exit(1);
  }, 30_000);
  killTimer.unref();            // don't keep the loop alive just for this

  // 3. Tell existing connections to close after current request
  for (const c of connections) c.end();

  // 4. Close DB pool, flush logs, stop consumers
  await Promise.allSettled([
    db.end(), redis.quit(), queueConsumer.close(),
  ]);
  process.exit(0);
}

process.on("SIGTERM", () =&gt; shutdown("SIGTERM"));   // sent by K8s, Docker, systemd
process.on("SIGINT",  () =&gt; shutdown("SIGINT"));    // Ctrl+C
</code></pre>
<p><strong>Production essentials:</strong> Kubernetes/Docker send <code>SIGTERM</code> then <code>SIGKILL</code> after a grace period (default 30s) — your shutdown must complete inside it. Add a <code>/health/ready</code> endpoint that returns 503 once <code>shuttingDown === true</code> so load balancers stop sending traffic. Respond to health checks with "not ready" <em>before</em> closing the server — gives the LB time to notice. For long requests (uploads, streams), set <code>keepAliveTimeout</code> lower than the grace period. Never swallow the <code>server.close()</code> callback error.</p>
'''

ANSWERS[5] = r'''
<p>Streams represent data that flows over time rather than existing all at once. Node models them as <code>EventEmitter</code> subclasses with standardized flow-control semantics, letting producers and consumers cooperate without either side knowing the full data size.</p>
<p>Four types: <strong>Readable</strong> (sources), <strong>Writable</strong> (sinks), <strong>Duplex</strong> (both, e.g., TCP socket), <strong>Transform</strong> (duplex that modifies, e.g., gzip).</p>
<p>Internally each has an <strong>internal buffer</strong> with a <code>highWaterMark</code> (default 16 KB). A writable's <code>.write()</code> returns <code>false</code> when the buffer is full — signaling the producer to pause. A readable pauses reading when its internal buffer is full and resumes when a consumer drains it. This handshake is <strong>backpressure</strong>: slow sinks throttle fast sources automatically, preventing memory blowup.</p>
<p><strong>Benefits:</strong></p>
<ul>
  <li><strong>Constant memory</strong> regardless of data size — a 5 GB file pipe uses ~KBs of RAM.</li>
  <li><strong>Time-to-first-byte</strong> — you write output as input arrives, not after everything's loaded.</li>
  <li><strong>Composable</strong> — <code>pipeline(src, gzip, dst)</code> chains transforms with correct error/cleanup propagation.</li>
  <li><strong>Universal</strong> — files, sockets, HTTP bodies, stdin/stdout, compression, crypto all implement the same interface.</li>
</ul>
<p><strong>Trade-offs:</strong> debugging streams is harder than arrays (events fire out of order, errors can be missed), backpressure bugs leak memory silently, and object-mode streams lose some of the buffering/backpressure benefits. Use <code>pipeline()</code> (not <code>.pipe()</code>) — it propagates errors and cleans up correctly; old <code>.pipe()</code> leaves streams open on error.</p>
'''

ANSWERS[6] = r'''
<p><strong>Backpressure</strong> occurs when a producer generates data faster than a consumer can process it. Without handling, the slower side's buffer grows unbounded until the process runs out of memory.</p>
<p>Node's stream API handles it via a <strong>return value contract</strong>:</p>
<pre><code>// Manual backpressure
source.on("data", (chunk) =&gt; {
  const ok = dest.write(chunk);
  if (!ok) {
    source.pause();                  // stop reading
    dest.once("drain", () =&gt; source.resume());   // resume when buffer empties
  }
});

// Preferred — pipeline handles this automatically
const { pipeline } = require("stream/promises");
await pipeline(source, transform, dest);

// Async iteration — `await` on each write pauses iteration naturally
async function copy(src, dst) {
  for await (const chunk of src) {
    if (!dst.write(chunk)) {
      await once(dst, "drain");
    }
  }
  dst.end();
}
</code></pre>
<p><strong>Key mechanics:</strong> <code>writable.write()</code> returns <code>false</code> when the internal buffer exceeds <code>highWaterMark</code>. The producer should stop until the <code>'drain'</code> event fires. <code>.pipe()</code> and <code>pipeline()</code> do this for you. If you write despite <code>false</code>, Node still accepts and buffers — but memory grows linearly with the lag.</p>
<p><strong>Backpressure across systems:</strong> HTTP streaming propagates naturally (TCP has its own flow control). Message queues (Kafka, RabbitMQ) implement it via consumer acks. WebSockets don't have built-in backpressure — check <code>ws.bufferedAmount</code> and throttle sends. When writing to cloud storage (S3 multipart) or databases (<code>COPY</code>), pass the stream directly and let the driver manage flow control.</p>
<p><strong>Symptom to watch for:</strong> steadily rising RSS memory during batch jobs with no GC reclaim — almost always unhandled backpressure.</p>
'''

ANSWERS[7] = r'''
<p>The <strong>cluster</strong> module lets a single Node process (the <em>primary</em>) fork multiple <em>workers</em> that share the same server port. The OS kernel (or a libuv-managed round-robin dispatcher) distributes incoming connections across workers — giving you multi-core utilization for a CPU-single-threaded runtime.</p>
<pre><code>const cluster = require("cluster");
const os = require("os");

if (cluster.isPrimary) {
  for (let i = 0; i &lt; os.cpus().length; i++) cluster.fork();
  cluster.on("exit", (worker) =&gt; {
    console.log(`worker ${worker.pid} died — respawning`);
    cluster.fork();
  });
} else {
  require("./server");              // each worker is its own Node process
}
</code></pre>
<p><strong>Architecture:</strong> Each worker is a separate V8 process with its own heap — memory is not shared, communication is via IPC (<code>process.send</code>). On Linux, cluster uses SO_REUSEPORT so the kernel balances connections. Workers crash independently — primary can respawn them.</p>
<p><strong>Use cases:</strong></p>
<ul>
  <li><strong>Scaling HTTP servers on multi-core machines</strong> — 4 cores → ~4× throughput for I/O-bound work.</li>
  <li><strong>Fault isolation</strong> — one worker's uncaught exception doesn't kill the others.</li>
  <li><strong>Zero-downtime reloads</strong> — kill workers one by one while forking replacements.</li>
</ul>
<p><strong>Trade-offs vs alternatives:</strong> compared to PM2 or running N processes behind a reverse proxy (nginx), cluster needs extra code and still has the sticky-session challenge. <strong>Worker threads</strong> share memory (via <code>SharedArrayBuffer</code>) — better for CPU-heavy work that needs to exchange data. Modern preference: deploy N container replicas behind a load balancer (K8s) and skip cluster entirely — the orchestrator handles crashes, scaling, and routing.</p>
'''

ANSWERS[8] = r'''
<p>Config management separates <strong>code</strong> from <strong>deployment-specific values</strong> (DB URLs, API keys, feature flags). The core principle comes from <strong>12-Factor App</strong>: store config in the environment, never commit secrets, fail fast on missing required values.</p>
<pre><code>// .env (gitignored)        .env.example (committed)
DATABASE_URL=postgres://...   DATABASE_URL=
JWT_SECRET=xyz                JWT_SECRET=
LOG_LEVEL=debug               LOG_LEVEL=info

// config/index.js — load + validate at startup
import "dotenv/config";
import { z } from "zod";

const schema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  FEATURE_NEW_CHECKOUT: z.coerce.boolean().default(false),
});

const parsed = schema.safeParse(process.env);
if (!parsed.success) {
  console.error("invalid config:", parsed.error.flatten());
  process.exit(1);                 // fail fast — don't start with bad config
}
export const config = Object.freeze(parsed.data);
</code></pre>
<p><strong>Environment strategy:</strong> <code>.env.development</code>, <code>.env.test</code>, <code>.env.production</code> loaded based on <code>NODE_ENV</code>. Only commit <code>.env.example</code> showing required keys. Use libraries like <code>dotenv-flow</code> or <code>config</code> for complex hierarchies.</p>
<p><strong>Secrets:</strong> don't put them in env files in production. Use managed stores — <strong>AWS Secrets Manager</strong>, <strong>HashiCorp Vault</strong>, <strong>Doppler</strong>, or Kubernetes Secrets — and inject them as env vars at runtime. For rotation, read secrets on startup <em>and</em> periodically refresh (e.g., DB passwords that rotate). Never log config values with secrets; mask them in error reports.</p>
<p><strong>Feature flags</strong> should be config too — dynamic ones via <strong>LaunchDarkly</strong>, <strong>Unleash</strong>, or a simple Redis-backed flag service. Exposing flags as typed config prevents scattered <code>process.env.X</code> reads across the codebase.</p>
'''

ANSWERS[9] = r'''
<p>Security is layered — no single measure is sufficient. The most important defenses for a Node API, in order of impact:</p>
<ul>
  <li><strong>Dependency hygiene</strong> — most Node breaches come through npm. Run <code>npm audit</code> in CI; use <code>npm ci</code> (not <code>install</code>) in deploys so lockfiles are respected. Tools: <strong>Snyk</strong>, <strong>Dependabot</strong>, <strong>Socket.dev</strong>.</li>
  <li><strong>Input validation</strong> — never trust request data. Validate shape, type, length, and allowed values with Zod/Yup/AJV. Strip unknown fields (<code>stripUnknown</code>).</li>
  <li><strong>Parameterized queries</strong> — use ORM or prepared statements; never concatenate SQL. Prevents SQL injection. For MongoDB, sanitize to prevent operator injection (<code>$where</code>, <code>$ne</code>).</li>
  <li><strong>Authentication &amp; authorization</strong> — bcrypt (cost ≥ 12) or argon2 for passwords; JWT with short TTL + refresh rotation; enforce authz on every route; prefer RBAC/ABAC patterns.</li>
  <li><strong>Security headers</strong> — use <code>helmet</code>: CSP, X-Frame-Options, HSTS, X-Content-Type-Options. Set <code>Strict-Transport-Security</code> with <code>preload</code>.</li>
  <li><strong>Rate limiting</strong> — <code>express-rate-limit</code> with Redis store; per-route limits on login/register/password-reset; CAPTCHA after N failures.</li>
  <li><strong>CORS</strong> — explicit allowlist, not <code>*</code>; reflect only trusted origins.</li>
  <li><strong>Secrets in env, not code</strong> — use a secrets manager; never log secrets; rotate on compromise.</li>
  <li><strong>HTTPS everywhere</strong> — TLS 1.2+; terminate at the LB; HSTS headers.</li>
  <li><strong>Body size limits</strong> — <code>express.json({ limit: "100kb" })</code>; <code>multer</code> with <code>fileSize</code> caps — prevents memory-exhaustion DoS.</li>
  <li><strong>Logging &amp; monitoring</strong> — structured logs (pino), anomaly detection (failed-login spikes), alerts. Don't log PII or tokens.</li>
  <li><strong>Principle of least privilege</strong> — run Node as non-root; DB user with only needed grants; separate read/write credentials.</li>
</ul>
<p>Also: enable <strong>OWASP ZAP</strong> or Burp scans in CI; maintain a <strong>responsible disclosure policy</strong>; keep Node itself patched — it has its own CVE stream.</p>
'''

ANSWERS[10] = r'''
<p>Map defenses to the <strong>OWASP Top 10</strong>:</p>
<table>
  <thead><tr><th>Vulnerability</th><th>Prevention</th></tr></thead>
  <tbody>
    <tr><td>Injection (SQL/NoSQL/command)</td><td>Parameterized queries (<code>$1</code>, <code>?</code>); ORMs; <code>express-mongo-sanitize</code>; avoid <code>child_process.exec</code> with user input — use <code>execFile</code> with args array</td></tr>
    <tr><td>XSS (cross-site scripting)</td><td>Output encode (templating engines escape by default); CSP header; <code>helmet</code>; never <code>v-html</code>/<code>dangerouslySetInnerHTML</code> on user content; sanitize with DOMPurify when needed</td></tr>
    <tr><td>CSRF (cross-site request forgery)</td><td><code>SameSite=Lax</code> cookies; double-submit CSRF token; <code>csurf</code> middleware; verify <code>Origin</code>/<code>Referer</code> for state-changing routes</td></tr>
    <tr><td>Broken auth</td><td>bcrypt/argon2; account lockout + exponential backoff; MFA; secure session cookies (<code>httpOnly</code>, <code>secure</code>, <code>sameSite</code>); short JWT TTL + refresh rotation</td></tr>
    <tr><td>Insecure deserialization</td><td>Never <code>eval</code>/<code>new Function</code>; don't deserialize untrusted JSON into prototype-polluting structures — use <code>JSON.parse</code> + schema validation</td></tr>
    <tr><td>Prototype pollution</td><td>Validate input shape; use <code>Object.create(null)</code> for maps; avoid merging user JSON into config; audit libs like lodash (historical CVEs)</td></tr>
    <tr><td>SSRF</td><td>Validate/allowlist outbound URL destinations; block private IP ranges (<code>10/8</code>, <code>169.254/16</code>, <code>::1</code>); use a proxy with policy</td></tr>
    <tr><td>Path traversal</td><td><code>path.resolve</code> + verify the result starts with the allowed base dir; never trust <code>req.params</code> as a file name</td></tr>
    <tr><td>Dependency vulns</td><td><code>npm audit</code>, Snyk, Dependabot; pin lockfile; remove unused deps</td></tr>
    <tr><td>Security misconfig</td><td><code>helmet</code>; disable <code>x-powered-by</code>; HSTS; CSP; no stack traces in production responses</td></tr>
  </tbody>
</table>
<p><strong>Node-specific gotchas:</strong> <code>regex</code> DoS ("ReDoS") — user-supplied regexes or vulnerable patterns can hang the event loop for seconds (libraries: <code>safe-regex2</code>, <code>re2</code> for linear-time regex). <code>JSON.parse</code> on huge input can still stall — enforce size caps. Don't log secrets or full request bodies; use redaction in pino.</p>
'''

ANSWERS[11] = r'''
<p>Scaling Node proceeds in layers — exhaust cheaper layers before reaching for expensive ones.</p>
<ol>
  <li><strong>Optimize the single process</strong> — async everything, eliminate sync I/O, cache hot data, use efficient serialization (<code>fast-json-stringify</code>), profile and fix the top CPU consumers.</li>
  <li><strong>Vertical scaling</strong> — more CPU/RAM on a single instance. Use all cores via <code>cluster</code> or multiple container replicas.</li>
  <li><strong>Horizontal scaling</strong> — run N identical instances behind a load balancer (nginx, AWS ALB, K8s Service). Requires stateless design — session state in Redis/DB, files in object storage, no local caches that must stay consistent.</li>
  <li><strong>Caching tier</strong> — <strong>CDN</strong> (CloudFront, Cloudflare) for static assets and cacheable API responses; <strong>Redis</strong> for session and application data; HTTP-level <code>Cache-Control</code> with ETags.</li>
  <li><strong>Database scaling</strong> — read replicas for SELECTs, connection pooling (PgBouncer), sharding by tenant/region when a single primary saturates, CQRS when read and write patterns diverge sharply.</li>
  <li><strong>Asynchronous work</strong> — move slow or bursty operations (email, PDF, image processing, webhooks) to a queue (BullMQ, SQS, RabbitMQ) consumed by worker processes. HTTP returns in ms; work happens on dedicated scalable fleets.</li>
  <li><strong>CPU-bound hotspots</strong> — offload to <code>worker_threads</code>, or a separate microservice in a more CPU-efficient language (Rust/Go).</li>
  <li><strong>Microservices / domain splits</strong> — scale independently sized domains (payments vs catalog). Adds operational complexity — justify with real constraints, not speculation.</li>
</ol>
<p><strong>Observability first:</strong> you can't scale what you can't measure. Add metrics (Prometheus), traces (OpenTelemetry), and RED metrics (Rate/Errors/Duration) per endpoint before scaling — it reveals which layer is actually the bottleneck. Often the DB or a single slow query, not Node.</p>
'''

ANSWERS[12] = r'''
<p>Distributed systems introduce <em>partial failure</em> — nodes, networks, and storage can fail independently. Node's async nature suits the pattern well, but you still need to design for it explicitly.</p>
<p><strong>Inter-service communication:</strong></p>
<ul>
  <li><strong>Synchronous</strong> — HTTP/REST, gRPC, GraphQL federation. Simple but couples availability (if service B is down, A's request fails). Mitigations: <strong>timeouts</strong> (hard cap on every call), <strong>retries with exponential backoff and jitter</strong>, <strong>circuit breakers</strong> (e.g., <code>opossum</code>) that fail fast after N errors.</li>
  <li><strong>Asynchronous</strong> — message brokers (<strong>Kafka</strong>, <strong>RabbitMQ</strong>, <strong>NATS</strong>, <strong>AWS SQS</strong>). Services emit events; consumers process independently. Decouples availability but adds eventual consistency.</li>
</ul>
<p><strong>Essential patterns:</strong></p>
<ul>
  <li><strong>Idempotency keys</strong> on every write endpoint — retries are safe.</li>
  <li><strong>Transactional outbox</strong> — persist the DB write and the outbound event in one transaction; a separate process publishes from the outbox. Avoids dual-write problems.</li>
  <li><strong>Saga pattern</strong> for cross-service transactions — compensating actions replace distributed 2PC.</li>
  <li><strong>Service discovery</strong> — K8s DNS, Consul, or platform-provided.</li>
  <li><strong>Distributed tracing</strong> — OpenTelemetry SDK; propagate <code>traceparent</code> headers so one request's path is visible across services.</li>
  <li><strong>Correlation IDs</strong> — every log line carries the request ID.</li>
</ul>
<p><strong>Node tooling:</strong> <strong>NestJS</strong> for structured microservice scaffolding with built-in transports (TCP, Redis, NATS, gRPC), <strong>Moleculer</strong> for microservice framework, <strong>BullMQ</strong> for job queues backed by Redis. For large fleets, use service mesh (<strong>Istio</strong>, <strong>Linkerd</strong>) for mTLS, retries, and observability without in-code changes.</p>
<p><strong>Failure discipline:</strong> plan for every downstream to be unavailable. Fail fast, degrade gracefully, return cached stale data when possible. Hope is not a strategy.</p>
'''

ANSWERS[13] = r'''
<table>
  <thead><tr><th>Aspect</th><th>Monolith</th><th>Microservices</th></tr></thead>
  <tbody>
    <tr><td>Deployment</td><td>One artifact, one deploy</td><td>N services, N pipelines</td></tr>
    <tr><td>Development velocity (small team)</td><td>Fast — everything in one repo, one DB</td><td>Slow — cross-service changes are costly</td></tr>
    <tr><td>Development velocity (large org)</td><td>Slows down — merge conflicts, coupling, scary deploys</td><td>Scales with teams — each owns a bounded context</td></tr>
    <tr><td>Scaling</td><td>Scale whole app, even for one hot endpoint</td><td>Scale services independently</td></tr>
    <tr><td>Technology choice</td><td>One stack</td><td>Mix freely (polyglot)</td></tr>
    <tr><td>Transactions</td><td>ACID across features</td><td>Eventual consistency, sagas, outbox</td></tr>
    <tr><td>Debugging</td><td>Single process, stack trace tells all</td><td>Distributed tracing mandatory</td></tr>
    <tr><td>Ops complexity</td><td>Low</td><td>High — K8s, service mesh, observability stack</td></tr>
    <tr><td>Network cost</td><td>In-process calls</td><td>Real network latency + serialization overhead</td></tr>
    <tr><td>Failure modes</td><td>All or nothing</td><td>Partial failure everywhere — design accordingly</td></tr>
  </tbody>
</table>
<p><strong>The honest recommendation in 2026:</strong> <em>start with a monolith</em>. Microservices solve a <strong>scaling-the-organization</strong> problem, not a technical one. Teams &lt; 20 engineers almost always regret premature splits — the cognitive and operational tax outweighs benefits. When you do split, start with a <strong>modular monolith</strong> (clear module boundaries, one deploy) and extract services only when a module has a compelling reason: different scaling profile, separate team ownership, different compliance boundary, or incompatible tech needs.</p>
<p>The <strong>"distributed monolith"</strong> anti-pattern (many services that must deploy together, share DBs) combines the worst of both worlds. If your services are tightly coupled, keep them together.</p>
'''

ANSWERS[14] = r'''
<p><strong>Worker threads</strong> provide real parallel execution within a single Node process. Each worker runs in its own V8 instance and isolate, with its own event loop and heap, but shares the parent process (same PID, same file descriptors inherited as needed).</p>
<table>
  <thead><tr><th>Aspect</th><th>Main event loop</th><th>Worker threads</th></tr></thead>
  <tbody>
    <tr><td>V8 isolate</td><td>Shared — all code runs in one</td><td>Separate per worker</td></tr>
    <tr><td>JS execution</td><td>Single thread</td><td>True parallel (N cores)</td></tr>
    <tr><td>Memory model</td><td>Shared heap</td><td>Separate heaps; share via <code>SharedArrayBuffer</code></td></tr>
    <tr><td>Startup cost</td><td>None</td><td>~10-40 ms per worker</td></tr>
    <tr><td>Communication</td><td>Direct references</td><td><code>postMessage</code> (structured clone) or SAB + <code>Atomics</code></td></tr>
    <tr><td>Use case</td><td>I/O-bound work</td><td>CPU-bound work (hashing, image, math)</td></tr>
  </tbody>
</table>
<p><strong>When to use workers:</strong> any CPU task that would block the event loop for more than ~50 ms — bcrypt hashing, PDF generation, image resizing (sharp actually uses libuv thread pool, not workers, but same idea), large JSON.parse on multi-MB payloads, encryption, heavy template rendering, complex data transforms.</p>
<p><strong>Critical distinction from <code>cluster</code>:</strong> cluster forks full Node processes (separate PIDs, IPC via pipes); workers are threads in the same process (shared PID, shared file handles, memory sharing option). Workers are <em>not</em> a replacement for cluster — cluster gives you horizontal scaling of a server across cores; workers offload specific CPU tasks.</p>
<p><strong>Watch out for:</strong> startup latency makes one-shot workers expensive — use <code>piscina</code> or a hand-rolled pool to reuse workers. <code>SharedArrayBuffer</code> requires careful synchronization via <code>Atomics</code> — easy to introduce race conditions. Native addons loaded in a worker require <code>context_aware</code> support.</p>
'''

ANSWERS[15] = r'''
<p>Two key patterns: a <strong>long-running worker pool</strong> for repeated tasks, and a <strong>one-shot worker</strong> for isolation.</p>
<pre><code>// === Pattern 1: One-shot worker for CPU task ===
// main.js
const { Worker } = require("worker_threads");

function runTask(data) {
  return new Promise((resolve, reject) =&gt; {
    const w = new Worker("./cpu-task.js", { workerData: data });
    w.on("message", resolve);
    w.on("error", reject);
    w.on("exit", (code) =&gt; code !== 0 &amp;&amp; reject(new Error(`exited ${code}`)));
  });
}

// cpu-task.js
const { workerData, parentPort } = require("worker_threads");
function fib(n) { return n &lt; 2 ? n : fib(n - 1) + fib(n - 2); }
parentPort.postMessage(fib(workerData.n));

// === Pattern 2: Worker pool (piscina handles this cleanly) ===
// npm install piscina
const Piscina = require("piscina");
const pool = new Piscina({
  filename: require("path").resolve(__dirname, "worker.js"),
  minThreads: 2, maxThreads: 8, idleTimeout: 30_000,
});

app.post("/hash", async (req, res) =&gt; {
  const hash = await pool.run(req.body.password);    // awaited, parallel
  res.json({ hash });
});

// worker.js
const bcrypt = require("bcrypt");
module.exports = async (password) =&gt; bcrypt.hash(password, 12);

// === Pattern 3: Shared memory with SharedArrayBuffer ===
const sab = new SharedArrayBuffer(4);
const view = new Int32Array(sab);
const worker = new Worker("./inc.js", { workerData: sab });
// inc.js: Atomics.add(new Int32Array(workerData), 0, 1);
// main:   Atomics.wait/notify for coordination
</code></pre>
<p><strong>Guidance:</strong> use <strong><code>piscina</code></strong> for almost all real use cases — it handles lifecycle, queuing, idle timeouts, graceful shutdown, and transfer-list optimization (for Buffers/ArrayBuffers to avoid copying). Size the pool at <code>min(cpus, peak concurrent CPU tasks)</code>. Measure first — spawning a worker costs 10-40 ms, so for sub-millisecond tasks, workers are net slower.</p>
<p><strong>Transfer vs clone:</strong> large Buffers copy by default (structured clone). Pass them in <code>transferList</code> to transfer ownership (zero-copy) — the sender loses access. This alone can turn a 100 ms IPC into 0.1 ms.</p>
'''

ANSWERS[16] = r'''
<p>A memory leak in Node = objects that accumulate across requests and are never GC'd because a reference keeps them reachable. Typical symptoms: RSS grows steadily, old-space heap grows between GCs, eventually <code>JavaScript heap out of memory</code>.</p>
<p><strong>Common causes:</strong></p>
<ul>
  <li><strong>Unbounded caches</strong> — <code>Map</code> that's never pruned. Use LRU (<code>lru-cache</code>) with size/TTL caps.</li>
  <li><strong>Event listener accumulation</strong> — adding <code>emitter.on(...)</code> per request without removing. Check with <code>emitter.listenerCount()</code>.</li>
  <li><strong>Closures capturing large objects</strong> — a setTimeout callback holding the whole request.</li>
  <li><strong>Global arrays/objects</strong> — "just for debugging" that stayed in.</li>
  <li><strong>Streams not ended/destroyed</strong> — especially on error paths.</li>
  <li><strong>Timers not cleared</strong> on shutdown or abort.</li>
  <li><strong>Promise chains with retained context</strong> — long-lived promises that don't settle.</li>
</ul>
<p><strong>Workflow to find one:</strong></p>
<ol>
  <li>Reproduce under load (autocannon, k6). Watch <code>process.memoryUsage()</code>.</li>
  <li>Take heap snapshots at intervals: <code>node --inspect</code>, open Chrome DevTools → Memory → "Heap snapshot", capture three over increasing load.</li>
  <li>Use <strong>"Comparison"</strong> view — objects growing unbounded between snapshots are suspects. <strong>"Retainers"</strong> shows what keeps them alive — follow the chain up to a global.</li>
  <li>For very large heaps, <code>v8.writeHeapSnapshot()</code> to disk, analyze offline.</li>
  <li>Tools: <code>clinic.js heap</code>, <code>heapdump</code>, <code>node --heap-prof</code>, <code>node-memwatch-next</code>.</li>
</ol>
<p><strong>Prevention:</strong> use <code>WeakMap</code>/<code>WeakRef</code> for associations that shouldn't prevent GC. Prefer <code>AbortController</code>/<code>AbortSignal</code> to clean up async work on cancel. Explicitly <code>removeListener</code> / <code>once</code> for one-shot events. Cap all collections. Set <code>--max-old-space-size=&lt;MB&gt;</code> explicitly so OOM is catchable and predictable.</p>
'''

ANSWERS[17] = r'''
<p>Profiling targets three dimensions: <strong>CPU</strong> (where time is spent), <strong>memory</strong> (allocations/leaks), and <strong>event-loop health</strong> (blocking, lag).</p>
<p><strong>CPU profiling:</strong></p>
<ul>
  <li><strong><code>node --prof app.js</code></strong> — V8 tick sampler. Post-process with <code>node --prof-process isolate-*.log</code> for a text report.</li>
  <li><strong><code>node --cpu-prof</code></strong> — writes <code>.cpuprofile</code> files viewable in Chrome DevTools.</li>
  <li><strong>Chrome DevTools</strong> — <code>node --inspect app.js</code>, open <code>chrome://inspect</code>, "Record CPU profile" while hitting the app.</li>
  <li><strong>Flame graphs via <code>0x</code></strong> — <code>npx 0x app.js</code>, generates an interactive SVG flame graph; fastest way to spot hot stacks.</li>
  <li><strong><code>clinic.js flame</code></strong> — similar, with automated scenarios.</li>
</ul>
<p><strong>Event loop health:</strong></p>
<ul>
  <li><strong><code>clinic.js doctor</code></strong> — runs your app under load and diagnoses: "event loop blocked" vs "GC pressure" vs "I/O bound."</li>
  <li><strong><code>perf_hooks</code> monitorEventLoopDelay</strong> — programmatically track p50/p99 event-loop delay as a metric.</li>
  <li><strong><code>eventLoopUtilization()</code></strong> — % of time the loop spent executing vs waiting; key production metric.</li>
</ul>
<p><strong>Memory:</strong></p>
<ul>
  <li><strong>Chrome DevTools heap snapshots</strong> — "Comparison" view between three snapshots finds growing retainers.</li>
  <li><strong><code>node --heap-prof</code></strong> — sampling allocation profiler; low overhead for production.</li>
  <li><strong><code>clinic.js heap</code></strong> — automated heap analysis.</li>
</ul>
<p><strong>APM in production:</strong> <strong>Datadog</strong>, <strong>New Relic</strong>, <strong>Dynatrace</strong>, <strong>Sentry</strong> Performance, or OSS: <strong>OpenTelemetry</strong> + Grafana + Tempo. These give continuous traces of every request with per-span timing — invaluable for finding slow DB queries and external calls that dev profiling won't reveal.</p>
<p><strong>General approach:</strong> profile under <em>realistic load</em> — tools like <code>autocannon</code>, <code>k6</code>, <code>artillery</code>. Synthetic microbenchmarks lie. Measure before and after each optimization — intuition is wrong about JS performance more often than not.</p>
'''

ANSWERS[18] = r'''
<p>Performance work is measurement-driven. Profile first, then fix the actual bottleneck — which is usually <em>not</em> the code you'd suspect.</p>
<p><strong>Application code:</strong></p>
<ul>
  <li>Eliminate <strong>sync I/O</strong> on request paths — <code>fs.readFileSync</code>, <code>crypto.pbkdf2Sync</code> are deadly.</li>
  <li>Avoid N+1 DB/API calls — batch with <strong>DataLoader</strong> or <code>IN (...)</code>.</li>
  <li>Replace <code>JSON.stringify</code> with <strong><code>fast-json-stringify</code></strong> on hot paths (4-10× faster with precompiled schema).</li>
  <li>Pre-compile regex, especially any user-facing patterns.</li>
  <li>Use streams for large payloads — constant memory, faster TTFB.</li>
  <li>Offload CPU work to <code>worker_threads</code> (<code>piscina</code>).</li>
</ul>
<p><strong>Framework/transport:</strong></p>
<ul>
  <li><strong>Fastify</strong> instead of Express — 2-3× throughput, schema compilation built in.</li>
  <li>Enable <strong>HTTP keep-alive</strong> everywhere, including outbound <code>undici</code>.</li>
  <li>Use <strong>undici</strong> (or global <code>fetch</code> from Node 18+) for HTTP — 3-5× faster than <code>axios</code>.</li>
  <li>Compression (<code>compression</code> middleware or at the proxy) — trades CPU for bandwidth.</li>
</ul>
<p><strong>Data layer:</strong></p>
<ul>
  <li><strong>Add indexes</strong> for every hot query — <code>EXPLAIN ANALYZE</code> reveals the need.</li>
  <li>Connection pooling (<code>pg-pool</code>, default Mongoose pool) — new connections per request is a killer.</li>
  <li>Cache hot reads in Redis (1-60s TTL suits many endpoints).</li>
  <li>Replace <code>SELECT *</code> with column-specific selects; use <code>.lean()</code> in Mongoose.</li>
</ul>
<p><strong>Infra &amp; config:</strong></p>
<ul>
  <li>Run with <code>NODE_ENV=production</code> — frameworks enable optimizations/templates caching.</li>
  <li>Use <code>cluster</code> or N container replicas — utilize all cores.</li>
  <li>Tune <code>UV_THREADPOOL_SIZE</code> if file/crypto/dns is the bottleneck (default 4).</li>
  <li>Set <code>--max-old-space-size</code> appropriately for container memory limits.</li>
  <li>CDN for static + cacheable assets; HTTP cache headers (ETag, <code>Cache-Control</code>).</li>
</ul>
<p><strong>The rule:</strong> measure, fix the biggest item, remeasure. The easiest perf wins are usually a missing DB index or an accidentally-sync operation — not clever micro-optimizations.</p>
'''

ANSWERS[19] = r'''
<p>A load balancer distributes incoming requests across N backend instances. For Node specifically, you're rarely writing the LB yourself — you're choosing <em>which</em> LB to put in front of your Node fleet.</p>
<p><strong>Deployment options:</strong></p>
<ul>
  <li><strong>nginx / HAProxy</strong> — battle-tested L7 reverse proxies. Sticky sessions, TLS termination, basic rate limiting, HTTP/2, WebSocket passthrough. Usually the right choice for self-hosted.</li>
  <li><strong>Cloud managed</strong> — AWS ALB, GCP Cloud Load Balancing, Azure Application Gateway. Auto-scaling, health checks, integrated with certificate managers. The default choice on cloud.</li>
  <li><strong>Kubernetes</strong> — Ingress controllers (nginx-ingress, Traefik) or Service (type LoadBalancer). The norm for containerized deploys.</li>
  <li><strong>Service mesh</strong> — Istio/Linkerd add L7 routing, mTLS, retries, circuit breaking as sidecars.</li>
  <li><strong>Node-level LB</strong> — rarely a good idea; if you really must, <code>http-proxy</code> or <code>fastify-http-proxy</code>.</li>
</ul>
<p><strong>Configuration essentials:</strong></p>
<pre><code># nginx.conf — reverse proxy with sticky sessions
upstream node_app {
  ip_hash;                    # session affinity
  server 10.0.1.10:3000 max_fails=3 fail_timeout=30s;
  server 10.0.1.11:3000 max_fails=3 fail_timeout=30s;
  server 10.0.1.12:3000 max_fails=3 fail_timeout=30s;
  keepalive 32;               # connection pool to backends
}

server {
  listen 443 ssl http2;
  location / {
    proxy_pass http://node_app;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 60s;
  }
  location /ws {              # WebSocket upgrade
    proxy_pass http://node_app;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
</code></pre>
<p><strong>Critical Node-side config:</strong> <code>app.set("trust proxy", true)</code> so Express reads <code>X-Forwarded-*</code> headers correctly for real client IPs. Health check endpoint (<code>/health</code>) returning 503 during graceful shutdown lets the LB stop sending traffic before pod termination. Sticky sessions only if absolutely needed — they break autoscaling; prefer stateless JWT + Redis-backed sessions.</p>
'''

ANSWERS[20] = r'''
<p>A transaction groups multiple DB operations into an atomic, isolated unit — they all commit or all roll back. Node has no special transaction story; you use your driver's API.</p>
<pre><code>// === Postgres (pg) — manual BEGIN/COMMIT ===
const client = await pool.connect();
try {
  await client.query("BEGIN");
  await client.query("UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                     [amount, fromId]);
  await client.query("UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                     [amount, toId]);
  await client.query("COMMIT");
} catch (err) {
  await client.query("ROLLBACK");
  throw err;
} finally {
  client.release();                    // CRITICAL — return to pool
}

// === Prisma — interactive transactions ===
await prisma.$transaction(async (tx) =&gt; {
  await tx.account.update({ where: { id: fromId }, data: { balance: { decrement: amount } } });
  await tx.account.update({ where: { id: toId },   data: { balance: { increment: amount } } });
}, { isolationLevel: "Serializable", timeout: 10_000 });

// === Mongoose — sessions ===
const session = await mongoose.startSession();
try {
  await session.withTransaction(async () =&gt; {
    await Account.updateOne({ _id: fromId }, { $inc: { balance: -amount } }, { session });
    await Account.updateOne({ _id: toId },   { $inc: { balance:  amount } }, { session });
  });
} finally { session.endSession(); }
</code></pre>
<p><strong>Isolation levels</strong> control what concurrent transactions can see. In Postgres: <code>READ COMMITTED</code> (default, prevents dirty reads), <code>REPEATABLE READ</code> (prevents non-repeatable reads), <code>SERIALIZABLE</code> (strongest — transactions behave as if serial). Financial operations usually want SERIALIZABLE or pessimistic locks (<code>SELECT ... FOR UPDATE</code>). Handle <code>SerializationFailure</code> errors with retry logic.</p>
<p><strong>Distributed transactions</strong> (across services/DBs) are a different beast — avoid them. Use the <strong>Saga pattern</strong>: a sequence of local transactions, each with a compensating action. <strong>Transactional outbox</strong> pattern keeps DB changes and published events atomic. Node libraries: <code>@node-ts/bus-core</code>, or hand-rolled with BullMQ.</p>
<p><strong>Common pitfalls:</strong> forgetting <code>client.release()</code> leaks connections; awaiting user input inside a transaction holds locks too long; retrying non-idempotent operations on rollback causes duplicates.</p>
'''

ANSWERS[21] = r'''
<p><code>async_hooks</code> lets you observe the lifecycle of async resources — timers, promises, TCP sockets, file handles. It's the foundation of <strong>AsyncLocalStorage</strong> (ALS), which is what you actually want in most cases.</p>
<pre><code>// --- Raw async_hooks (rarely used directly) ---
const async_hooks = require("async_hooks");
const hook = async_hooks.createHook({
  init(asyncId, type, triggerAsyncId) { /* new resource */ },
  before(asyncId) { /* resource callback about to run */ },
  after(asyncId)  { /* resource callback finished */ },
  destroy(asyncId){ /* resource destroyed */ },
});
hook.enable();

// --- AsyncLocalStorage — the practical API ---
const { AsyncLocalStorage } = require("async_hooks");
const ctx = new AsyncLocalStorage();

app.use((req, res, next) =&gt; {
  const store = {
    requestId: req.headers["x-request-id"] || crypto.randomUUID(),
    userId: req.user?.id,
    startTime: Date.now(),
  };
  ctx.run(store, () =&gt; next());        // every subsequent async op inherits `store`
});

// Anywhere downstream — no explicit passing
function logEvent(name, data) {
  const store = ctx.getStore();
  log.info({ requestId: store?.requestId, userId: store?.userId, event: name, ...data });
}

async function complexFlow() {
  const users = await db.query("...");    // no need to thread requestId through every call
  await processBackgroundJob(users);
  logEvent("flow.done", { count: users.length });
}
</code></pre>
<p><strong>What AsyncLocalStorage replaces:</strong> before it existed, correlating logs within a request meant passing a context object through every function signature ("context threading"), or using thread-local hacks. ALS propagates automatically across <code>await</code>, timers, event emitter callbacks — anywhere the async context preserves.</p>
<p><strong>Use cases:</strong></p>
<ul>
  <li><strong>Request-scoped logging</strong> — attach request ID, user ID, tenant ID to every log line automatically.</li>
  <li><strong>Distributed tracing</strong> — carry trace spans across async boundaries (OpenTelemetry uses ALS internally).</li>
  <li><strong>Per-request feature flags</strong> or DB read/write routing.</li>
</ul>
<p><strong>Trade-offs:</strong> there's measurable overhead on heavy async paths (Node itself tracks resource chains). In Node 16+ it's much cheaper than earlier. Avoid raw <code>async_hooks</code> — correctness is tricky (callbacks can throw, infinite loops possible). Prefer ALS unless you're building a tracing library.</p>
'''

ANSWERS[22] = r'''
<p><strong>Event-driven programming</strong> structures code as producers that emit events and consumers that react — instead of calling each other directly. Control flow is inverted: "when X happens, do Y" replaces "do X, then Y."</p>
<p>Node is event-driven at its core. The event loop itself dispatches I/O events. The <code>EventEmitter</code> class (and its subclasses: streams, servers, sockets, request/response) is Node's fundamental pattern.</p>
<pre><code>const { EventEmitter } = require("events");

class OrderService extends EventEmitter {
  async placeOrder(order) {
    const saved = await db.save(order);
    this.emit("order.placed", saved);    // fire-and-forget notification
    return saved;
  }
}

const svc = new OrderService();

// Each consumer subscribes independently — no coupling
svc.on("order.placed", sendEmail);
svc.on("order.placed", updateInventory);
svc.on("order.placed", pushAnalytics);
svc.on("order.placed", notifyWarehouse);
</code></pre>
<p><strong>Patterns enabled:</strong></p>
<ul>
  <li><strong>Decoupling</strong> — producer doesn't know who's listening; consumers can be added/removed without changes.</li>
  <li><strong>Extensibility</strong> — plugins hook into standard events (think webpack plugin architecture, Fastify hooks).</li>
  <li><strong>Non-blocking flow</strong> — emit and move on; slow consumers don't block the producer (unless they're sync).</li>
</ul>
<p><strong>Gotchas specific to EventEmitter:</strong></p>
<ul>
  <li>Listeners are called <strong>synchronously</strong>, in registration order. If you need async work, <code>emit</code> then let consumers do their own async.</li>
  <li>Unhandled <code>'error'</code> events <strong>crash the process</strong> — always register an error listener on streams and emitters.</li>
  <li>Memory leak warning at &gt; 10 listeners — often legitimate for broadcasters; set <code>emitter.setMaxListeners(N)</code> explicitly rather than ignoring.</li>
  <li>Errors thrown in listeners propagate synchronously — one bad listener can take down the emitter call; use try/catch or <code>once</code>.</li>
</ul>
<p><strong>Scaling across processes:</strong> in-process EventEmitter doesn't cross workers/instances. Use a message broker (Redis Pub/Sub, Kafka, NATS) for distributed event-driven architectures.</p>
'''

ANSWERS[23] = r'''
<p><strong>Structured debugging beats <code>console.log</code></strong> — but <code>console.log</code> still wins for quick local exploration.</p>
<p><strong>Tool ladder, simple to advanced:</strong></p>
<ul>
  <li><strong><code>console.log</code> / <code>console.dir</code> / <code>console.trace</code></strong> — fast, sometimes enough. Use <code>util.inspect(obj, { depth: null })</code> to expand nested objects.</li>
  <li><strong><code>debug</code> package</strong> — namespaced logs toggled via env var: <code>DEBUG=app:* node index.js</code>. Perfect for libraries.</li>
  <li><strong>Node inspector</strong> — <code>node --inspect</code> (or <code>--inspect-brk</code> to break on start). Open <code>chrome://inspect</code>; get full DevTools: breakpoints, step through, watch expressions, heap snapshots, CPU profiles.</li>
  <li><strong>VS Code debugger</strong> — the best daily driver. <code>launch.json</code> with <code>"type": "node"</code>, <code>"request": "launch"</code>. Integrated breakpoints, conditional breakpoints, logpoints (log without modifying code), variable inspection, and call stack navigation.</li>
  <li><strong>Remote / production debugging</strong> — attach to a running process via inspector over SSH tunnel. Never expose the inspector port publicly.</li>
  <li><strong>Post-mortem</strong> — <code>node --abort-on-uncaught-exception</code> + core dumps; analyze with <code>llnode</code> or <code>mdb_v8</code>.</li>
  <li><strong>Logpoints</strong> (VS Code) — log variable values without stopping execution; non-invasive alternative to console.log.</li>
</ul>
<p><strong>Techniques for tricky bugs:</strong></p>
<ul>
  <li><strong>Async stack traces</strong> — enable in DevTools ("Enable async stack traces"); modern V8 shows the full causal chain across awaits.</li>
  <li><strong>Conditional breakpoints</strong> — break only when <code>user.role === "admin"</code>.</li>
  <li><strong>Unhandled rejection traps</strong> — <code>process.on("unhandledRejection", ...)</code> to catch promises nobody awaited.</li>
  <li><strong>Bisect with git</strong> — when a bug appeared between releases, <code>git bisect</code> is faster than reading diffs.</li>
</ul>
<p><strong>Observability for production:</strong> a debugger is rarely usable in production. Invest in structured logging (pino), tracing (OpenTelemetry), and error aggregation (Sentry) — they turn "what's happening?" into a query, not a live session.</p>
'''

ANSWERS[24] = r'''
<p><strong>Native addons</strong> are shared libraries written in C/C++ (or Rust via <code>napi-rs</code>, or AssemblyScript) that Node loads via <code>require</code>. They bridge to code that can't be written efficiently in JS — or interface with native system APIs.</p>
<table>
  <thead><tr><th>Advantages</th><th>Disadvantages</th></tr></thead>
  <tbody>
    <tr><td>Direct access to OS APIs not exposed by Node</td><td>Platform-specific builds — Linux/macOS/Windows × x64/arm64 × glibc/musl = matrix of prebuilts</td></tr>
    <tr><td>Raw CPU performance for tight loops, crypto, image/audio processing</td><td>Requires a C/C++ toolchain to build from source — pain for users</td></tr>
    <tr><td>Integrate with existing C/C++ libraries (OpenSSL, libpng, sqlite3)</td><td>Memory safety — a C/C++ bug can crash the entire Node process (no sandbox)</td></tr>
    <tr><td>Shared memory / zero-copy buffers</td><td>Harder to debug — JS stack traces don't cross the boundary cleanly</td></tr>
    <tr><td>Bypass V8 overhead for hot paths</td><td>Node version coupling — historic APIs broke between majors</td></tr>
  </tbody>
</table>
<p><strong>Modern API — N-API (Node-API):</strong> the current, stable ABI layer. Code compiled against N-API v8 works on Node 18+, Node 20, Node 22, etc. — no recompilation per Node version. This solved the old nightmare. Use <strong><code>node-addon-api</code></strong> (C++ wrapper) or <strong><code>napi-rs</code></strong> (Rust bindings) — avoid raw N-API C unless you have a strong reason.</p>
<p><strong>When to use:</strong> extremely CPU-bound hot path after profiling (crypto, compression, parsing), integration with existing C library, OS feature missing from Node. Examples: <code>sharp</code> (libvips image processing), <code>bcrypt</code> (native wraps around OpenSSL), <code>sqlite3</code>, <code>node-sass</code> (historically).</p>
<p><strong>When to avoid:</strong> most cases. WebAssembly is often a better alternative — portable, sandboxed, no native toolchain. <code>worker_threads</code> handle many parallelism needs without the complexity. "I need speed" is usually better solved by algorithmic fixes or moving to Fastify/faster serialization.</p>
'''

ANSWERS[25] = r'''
<p>Modern Node addon development uses <strong>N-API</strong> for ABI stability across Node versions. Use <code>node-addon-api</code> (C++ wrapper) or <code>napi-rs</code> (Rust) — raw C N-API is verbose.</p>
<pre><code>// --- Path 1: C++ with node-addon-api ---
// addon.cc
#include &lt;napi.h&gt;

// Sync function — simple CPU task
Napi::Number Add(const Napi::CallbackInfo&amp; info) {
  Napi::Env env = info.Env();
  if (info.Length() &lt; 2 || !info[0].IsNumber() || !info[1].IsNumber()) {
    Napi::TypeError::New(env, "two numbers expected").ThrowAsJavaScriptException();
    return Napi::Number::New(env, 0);
  }
  double a = info[0].As&lt;Napi::Number&gt;();
  double b = info[1].As&lt;Napi::Number&gt;();
  return Napi::Number::New(env, a + b);
}

// Async function — runs on libuv thread pool, doesn't block JS
class HashWorker : public Napi::AsyncWorker {
  // ... Execute() runs on worker thread; OnOK() resolves the promise
};

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  exports.Set("add", Napi::Function::New(env, Add));
  return exports;
}
NODE_API_MODULE(addon, Init)

// binding.gyp — build config
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cc"],
    "cflags!": ["-fno-exceptions"],
    "cflags_cc!": ["-fno-exceptions"],
    "include_dirs": ["&lt;!@(node -p \"require('node-addon-api').include\")"],
    "defines": ["NAPI_DISABLE_CPP_EXCEPTIONS"]
  }]
}

// package.json:   "scripts": { "install": "node-gyp rebuild" }

// JS consumer
const addon = require("./build/Release/addon.node");
console.log(addon.add(1, 2));

// --- Path 2: Rust with napi-rs (far simpler DX) ---
// lib.rs
#[macro_use]
extern crate napi_derive;

#[napi]
pub fn add(a: f64, b: f64) -&gt; f64 { a + b }

#[napi]
pub async fn hash_password(password: String) -&gt; String {
  // runs on tokio threadpool; returns a JS Promise automatically
  tokio::task::spawn_blocking(move || bcrypt::hash(&amp;password, 12).unwrap()).await.unwrap()
}
// `napi build --release` produces a .node binary + TS types
</code></pre>
<p><strong>Distribution:</strong> ship prebuilt binaries via <code>prebuild</code>, <code>prebuildify</code>, or <code>@napi-rs/cli</code>. Without prebuilts, every user must have a C++ toolchain — fatal UX. The build matrix (Linux/macOS/Windows × x64/arm64 × glibc/musl) is real work; napi-rs has automation (GitHub Actions templates).</p>
<p><strong>Async work:</strong> never do blocking work in the JS-calling thread — it blocks the event loop. Use <code>AsyncWorker</code> (C++) or <code>tokio::task::spawn_blocking</code> (Rust) to offload to libuv's thread pool.</p>
<p><strong>Practical recommendation:</strong> start with Rust + napi-rs. The developer experience is much better, memory safety eliminates whole bug classes, cross-compilation is built in.</p>
'''

ANSWERS[26] = r'''
<p>Production logging is a product of three decisions: <strong>format</strong> (structured JSON, not pretty strings), <strong>levels</strong> (filter noise), and <strong>destination</strong> (stdout to collector, not files in the container).</p>
<pre><code>// pino — fastest Node logger, JSON output
// npm install pino pino-http
const pino = require("pino");
const log = pino({
  level: process.env.LOG_LEVEL || "info",
  base: { service: "api", env: process.env.NODE_ENV },
  timestamp: pino.stdTimeFunctions.isoTime,
  redact: {
    paths: ["password", "token", "*.authorization", "req.headers.cookie"],
    censor: "[REDACTED]",
  },
  // Pretty only in dev
  ...(process.env.NODE_ENV !== "production" &amp;&amp; {
    transport: { target: "pino-pretty" },
  }),
});

// Request logging middleware (auto-correlates with AsyncLocalStorage)
const httpLogger = require("pino-http")({ logger: log });
app.use(httpLogger);

// In handlers
app.get("/users/:id", (req, res) =&gt; {
  req.log.info({ userId: req.params.id }, "fetching user");
  // req.log already has requestId, method, url bound
});

// Child logger with bound context
const orderLog = log.child({ module: "orders" });
orderLog.info({ orderId: "abc" }, "order placed");
</code></pre>
<p><strong>Principles:</strong></p>
<ul>
  <li><strong>JSON, not strings</strong> — log aggregators (Datadog, CloudWatch, Loki, Splunk) index fields; queries like <code>status:500 AND user_id:42</code> need structured data.</li>
  <li><strong>Log to stdout/stderr</strong> — the container runtime handles rotation and forwarding. Writing to files in containers is an antipattern.</li>
  <li><strong>Include a <code>requestId</code></strong> on every log line (AsyncLocalStorage auto-propagates it); makes one request's story reconstructible across services.</li>
  <li><strong>Redact PII and secrets</strong> — pino's <code>redact</code> is cheap and removes common leaks; audit carefully.</li>
  <li><strong>Sample debug/info in high-throughput services</strong> — at 10K req/s, full logs overwhelm; sample with probability-based filters.</li>
  <li><strong>Correlate with traces</strong> — include <code>trace_id</code>/<code>span_id</code> (OpenTelemetry); logs and traces become one view.</li>
</ul>
<p><strong>Levels convention:</strong> <code>fatal</code> (process about to die), <code>error</code> (something failed), <code>warn</code> (unexpected but handled), <code>info</code> (state changes worth auditing), <code>debug</code> (diagnosis), <code>trace</code> (firehose). Default level in production: <code>info</code>. Never <code>console.log</code> in production code — unstructured, unredacted, uncorrelated.</p>
'''

ANSWERS[27] = r'''
<table>
  <thead><tr><th>Library</th><th>Characteristics</th><th>Best for</th></tr></thead>
  <tbody>
    <tr><td><strong>pino</strong></td><td>Fastest JSON logger; minimal overhead; low-allocation; built-in redaction; transports for shipping</td><td>Production APIs, high-throughput services — the default modern choice</td></tr>
    <tr><td><strong>winston</strong></td><td>Feature-rich, plugin-heavy (transports for files, DBs, Slack); more flexible config but noticeably slower</td><td>Apps that need rare destinations or complex routing; legacy codebases</td></tr>
    <tr><td><strong>bunyan</strong></td><td>OG JSON logger; still works but less actively developed; ships with <code>bunyan</code> CLI pretty-printer</td><td>Legacy; generally superseded by pino</td></tr>
    <tr><td><strong>debug</strong></td><td>Tiny namespaced debug tool; not a full logger; enabled via <code>DEBUG=foo:*</code> env var</td><td>Library authors; opt-in diagnostic output</td></tr>
    <tr><td><strong>log4js</strong></td><td>Category-based, file rotation, appenders modeled after Log4J</td><td>Teams coming from Java</td></tr>
    <tr><td><strong>signale</strong></td><td>Pretty CLI output with emoji; dev-focused</td><td>Build tools, CLIs — not servers</td></tr>
    <tr><td><strong>roarr</strong></td><td>JSON-only; context passing via child loggers</td><td>Niche</td></tr>
  </tbody>
</table>
<p><strong>Recommendation:</strong> use <strong>pino</strong> for backend services and APIs. It's ~5-10× faster than Winston in common scenarios because it offloads formatting to a separate process (<code>pino-pretty</code>, <code>pino-elasticsearch</code>, etc.), writes async, and avoids V8 deopts. Child loggers for bound context (<code>log.child({ userId })</code>) are near-free. <code>pino-http</code> is the de-facto Express/Fastify middleware.</p>
<p><strong>Framework-specific:</strong> <strong>Fastify</strong> ships with pino built in — <code>request.log</code> is available everywhere. <strong>NestJS</strong> uses its own logger abstraction; swap in pino via <code>nestjs-pino</code>. <strong>Hono</strong> is agnostic; pass pino to its logger middleware.</p>
<p><strong>Structured logging conventions:</strong> use ECS (Elastic Common Schema) or OpenTelemetry's semantic conventions — makes your logs searchable with the same field names across services. Ship to a centralized store (Loki, ElasticSearch, Splunk, Datadog) from stdout via sidecar collectors (Fluent Bit, Vector, OpenTelemetry Collector).</p>
'''

ANSWERS[28] = r'''
<p>Real-time = server can push to clients, ideally with &lt; 100 ms latency. Choose transport based on direction, scale, and client constraints.</p>
<table>
  <thead><tr><th>Transport</th><th>Direction</th><th>Use when</th></tr></thead>
  <tbody>
    <tr><td>WebSocket</td><td>Bidirectional</td><td>Chat, collaborative editing, multiplayer games, interactive dashboards</td></tr>
    <tr><td>Server-Sent Events (SSE)</td><td>Server → client</td><td>Notifications, live feeds, price tickers, log streams — simpler than WS</td></tr>
    <tr><td>Long polling</td><td>Fallback</td><td>Corporate networks blocking WS; legacy clients</td></tr>
    <tr><td>WebTransport / WebRTC</td><td>Low-latency, datagram</td><td>Video/audio, gaming; beyond HTTP stack</td></tr>
  </tbody>
</table>
<pre><code>// --- Socket.IO — battle-tested, auto-fallback, rooms, pub/sub ---
const { Server } = require("socket.io");
const { createAdapter } = require("@socket.io/redis-adapter");

const io = new Server(httpServer, { cors: { origin: "*" } });
io.adapter(createAdapter(redisPub, redisSub));      // cross-instance broadcast

io.use(async (socket, next) =&gt; {
  try {
    const user = await verifyToken(socket.handshake.auth.token);
    socket.data.userId = user.id;
    next();
  } catch { next(new Error("unauthorized")); }
});

io.on("connection", (socket) =&gt; {
  socket.join(`user:${socket.data.userId}`);         // per-user room
  socket.on("message", async (msg) =&gt; {
    const saved = await Message.create({ from: socket.data.userId, ...msg });
    io.to(`user:${msg.to}`).emit("message", saved);
  });
});

// Emit from REST handler or background job
io.to(`user:${userId}`).emit("notification", { text: "hello" });

// --- Native ws (smaller, no magic) ---
const WebSocket = require("ws");
const wss = new WebSocket.Server({ server: httpServer });
wss.on("connection", (ws) =&gt; {
  ws.on("message", (buf) =&gt; ws.send(`echo: ${buf}`));
});
</code></pre>
<p><strong>Scaling across multiple Node instances:</strong> the key problem is "user A is connected to instance 1; how does instance 2 push to them?" Solutions:</p>
<ul>
  <li><strong>Redis adapter</strong> (Socket.IO) — publishes broadcasts through Redis Pub/Sub so every instance sees them.</li>
  <li><strong>Sticky sessions</strong> on the load balancer — same user always lands on same instance. Required for WebSocket handshake over LBs that don't support WS natively.</li>
  <li><strong>Managed services</strong> — Pusher, Ably, AWS IoT, Azure SignalR. Handle scaling/persistence; pay per message.</li>
</ul>
<p><strong>Production concerns:</strong> implement heartbeat/ping to detect dead connections, backpressure by checking <code>bufferedAmount</code>, rate limit per-connection message emissions, validate every incoming payload (clients are untrusted), authenticate at handshake (token in cookie or <code>auth</code> handshake data).</p>
'''

ANSWERS[29] = r'''
<table>
  <thead><tr><th>Aspect</th><th>WebSocket</th><th>SSE</th></tr></thead>
  <tbody>
    <tr><td>Direction</td><td>Bidirectional (full duplex)</td><td>Server → client only</td></tr>
    <tr><td>Protocol</td><td>Upgrades HTTP to <code>ws://</code>/<code>wss://</code></td><td>Plain HTTP long-response with <code>text/event-stream</code></td></tr>
    <tr><td>Data format</td><td>Binary or text frames</td><td>UTF-8 text only (base64 for binary)</td></tr>
    <tr><td>Reconnection</td><td>Manual (client must re-open + resend auth)</td><td>Built into <code>EventSource</code> — auto-reconnect with <code>Last-Event-ID</code></td></tr>
    <tr><td>Firewall/proxy friendliness</td><td>Sometimes blocked; needs proxy support for Upgrade</td><td>Just HTTP — works through all proxies</td></tr>
    <tr><td>Browser support</td><td>Universal (since 2011)</td><td>Universal except IE (polyfill exists)</td></tr>
    <tr><td>Multiplexing</td><td>One connection per WS</td><td>One connection per stream; HTTP/2 multiplexes many SSE on one conn</td></tr>
    <tr><td>Server overhead</td><td>Keeps TCP conn + upgrade state</td><td>Keeps long-polled HTTP response open</td></tr>
    <tr><td>Complexity</td><td>Higher — manual reconnect, heartbeats, framing</td><td>Lower — HTTP endpoint + client EventSource</td></tr>
  </tbody>
</table>
<pre><code>// SSE — 10 lines of server code
app.get("/events", (req, res) =&gt; {
  res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" });
  const send = (data) =&gt; res.write(`data: ${JSON.stringify(data)}\n\n`);
  const timer = setInterval(() =&gt; send({ t: Date.now() }), 1000);
  req.on("close", () =&gt; clearInterval(timer));
});
// Client: new EventSource("/events").onmessage = (e) =&gt; console.log(e.data);
</code></pre>
<p><strong>Picking between them:</strong> use <strong>SSE</strong> for one-way server pushes — notifications, live tickers, log streams, progress updates, status updates. It's drastically simpler, auto-reconnects, and works through every proxy. Use <strong>WebSockets</strong> when you need <em>truly</em> bidirectional real-time — chat where typing indicators matter, collaborative editing, multiplayer games, VoIP signaling.</p>
<p><strong>Subtle gotchas:</strong> SSE's default browser connection limit per domain is 6 — HTTP/2 removes this. SSE blocks browser connections (no concurrent requests on HTTP/1.1 to same origin). WebSockets lose messages on disconnect unless you build replay; SSE's <code>Last-Event-ID</code> enables server-side replay from a cursor.</p>
'''

ANSWERS[30] = r'''
<p>The pattern depends on scale. Small files direct through Node are fine; large files or high volume demand architectural separation.</p>
<p><strong>Small uploads (&lt; 10 MB):</strong> <code>multer</code> with disk or memory storage is fine. Stream to disk (not memory) to keep RSS flat. Validate size, mime, and <em>actual file content</em> (magic bytes via <code>file-type</code>) — browser-supplied mime is spoofable.</p>
<p><strong>Large uploads (&gt; 100 MB) or high concurrency:</strong> don't send files through your Node server at all. Use <strong>pre-signed URLs</strong> — Node generates a short-lived upload URL, client PUTs directly to S3/GCS/Azure Blob.</p>
<pre><code>// Server issues pre-signed PUT URL
const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const { getSignedUrl } = require("@aws-sdk/s3-request-presigner");

app.post("/uploads/sign", authRequired, async (req, res) =&gt; {
  const { contentType, size } = req.body;
  if (size &gt; 500 * 1024 * 1024) return res.status(413).json({ error: "too large" });
  if (!["image/jpeg","image/png","application/pdf"].includes(contentType))
    return res.status(400).json({ error: "bad mime" });

  const key = `uploads/${req.user.id}/${crypto.randomUUID()}`;
  const url = await getSignedUrl(
    s3, new PutObjectCommand({ Bucket: BUCKET, Key: key, ContentType: contentType }),
    { expiresIn: 300 }        // 5 min
  );
  await Upload.create({ userId: req.user.id, key, status: "pending" });
  res.json({ url, key });
});

// Client uses fetch/PUT directly to S3; no bytes touch your server
</code></pre>
<p><strong>For multi-GB files, resumable uploads:</strong> use <strong>S3 multipart uploads</strong> (chunks 5 MB+), <strong>tus protocol</strong> (<code>@tus/server</code>), or platform equivalents. Clients can resume after network drops.</p>
<p><strong>Downloads:</strong></p>
<ul>
  <li><strong>Public files</strong> — serve via CDN (CloudFront, Cloudflare). Node shouldn't be in the byte path.</li>
  <li><strong>Private files</strong> — generate pre-signed GET URLs with short TTL; return the URL, not the bytes.</li>
  <li><strong>Streaming from Node</strong> (e.g., generating a ZIP): use streams with <code>pipeline</code>; set <code>Content-Disposition</code> for downloads; respect range requests for video seeking (<code>Accept-Ranges: bytes</code>).</li>
</ul>
<p><strong>Post-upload processing</strong> (resize, virus scan, transcode): trigger async via S3 event → SQS → worker or Lambda. Keep the upload path sync-fast; move work out of the request.</p>
'''

ANSWERS[31] = r'''
<p>A proper REST API follows resource-oriented URLs, HTTP semantics, and clear state representations.</p>
<pre><code>// Skeleton — resource routers, versioned base, layered architecture
const express = require("express");
const app = express();

// Global middleware
app.use(require("helmet")());
app.use(require("cors")({ origin: allowedOrigins }));
app.use(express.json({ limit: "1mb" }));
app.use(require("pino-http")({ logger }));

// API version prefix
const v1 = express.Router();
v1.use("/users", require("./users/router"));
v1.use("/posts", require("./posts/router"));
app.use("/api/v1", v1);

// --- users/router.js — resource-oriented, thin handlers ---
const router = require("express").Router();
const ctrl = require("./controller");

router.get   ("/",    ctrl.list);        // GET    /api/v1/users
router.post  ("/",    validate(CreateUser), ctrl.create);
router.get   ("/:id", ctrl.get);
router.patch ("/:id", validate(UpdateUser), ctrl.patch);   // partial
router.put   ("/:id", validate(ReplaceUser), ctrl.replace); // full
router.delete("/:id", ctrl.remove);

router.get   ("/:userId/posts", ctrl.listPosts);   // sub-resource
module.exports = router;

// --- controller.js — HTTP layer calls service layer ---
exports.get = async (req, res, next) =&gt; {
  try {
    const user = await userService.findById(req.params.id);
    if (!user) throw new NotFoundError();
    res.json(user);
  } catch (err) { next(err); }
};

// --- 404 + central error handler ---
app.use((req, res) =&gt; res.status(404).json({ error: "not_found" }));
app.use((err, req, res, _next) =&gt; {
  const status = err.statusCode || 500;
  if (status &gt;= 500) req.log.error({ err }, "unhandled");
  res.status(status).json({
    error: { code: err.code || "INTERNAL", message: err.message },
    requestId: req.id,
  });
});
</code></pre>
<p><strong>Layered architecture:</strong> <em>route</em> → <em>controller</em> (HTTP concerns only) → <em>service</em> (business logic) → <em>repository</em> (data access). This lets you test service logic without HTTP or a DB, and swap frameworks later.</p>
<p><strong>Essentials:</strong> input validation (Zod/AJV) on every write; authentication middleware (JWT/session); authorization at the controller or service layer; rate limiting on sensitive endpoints; pagination on all lists; consistent error envelope; request IDs for correlation; OpenAPI schema (auto from Zod via <code>zod-to-openapi</code>) for docs.</p>
<p><strong>Modern alternative:</strong> <strong>Fastify</strong> uses the same patterns with 2-3× throughput and first-class schema validation. For TypeScript-first stacks, <strong>NestJS</strong> provides structure (modules/controllers/providers) if you value convention; <strong>tRPC</strong> eliminates REST boilerplate when both ends are TypeScript.</p>
'''

ANSWERS[32] = r'''
<p>Best practices that compound into a maintainable, evolvable API:</p>
<ul>
  <li><strong>Resource-oriented URLs</strong> — nouns, plural, hierarchical: <code>/users/42/posts/9/comments</code>. Actions via HTTP verbs, not URLs.</li>
  <li><strong>HTTP verbs correctly</strong> — GET safe + idempotent, POST not idempotent, PUT idempotent replacement, PATCH partial update, DELETE idempotent removal.</li>
  <li><strong>Status codes matter</strong> — 200/201/204 for success, 400 (client error), 401 (unauth'd), 403 (forbidden), 404 (missing), 409 (conflict), 422 (validation), 429 (rate-limited), 500 (server), 503 (degraded). Don't return 200 with <code>{error}</code>.</li>
  <li><strong>Versioning</strong> — URL path (<code>/v1/</code>) is pragmatic; header versioning is purer but harder for tooling. Whatever you pick, support at least one old version during migrations.</li>
  <li><strong>Pagination</strong> — cursor for large/live data, offset for small. Return <code>hasNext</code>/<code>nextCursor</code>; never expose unbounded lists.</li>
  <li><strong>Filtering &amp; sorting</strong> — <code>?status=active&amp;sort=-createdAt</code>; allowlist fields to prevent DoS.</li>
  <li><strong>Consistent field naming</strong> — pick snake_case or camelCase and stick to it; include a style guide.</li>
  <li><strong>Envelope vs bare</strong> — returning objects directly (<code>{ id, name }</code>) is simpler; wrapping (<code>{ data, meta }</code>) helps for lists with pagination metadata. Be consistent.</li>
  <li><strong>Error envelope</strong> — <code>{ error: { code, message, details? }, requestId }</code>. Stable <code>code</code> is machine-readable; <code>message</code> is human-readable.</li>
  <li><strong>Idempotency keys</strong> — for POSTs that shouldn't duplicate (payments): accept <code>Idempotency-Key</code> header, store it with the response, return the stored response on replay.</li>
  <li><strong>Cache headers</strong> — <code>ETag</code>, <code>Cache-Control</code>, <code>Last-Modified</code>; honor <code>If-None-Match</code> for 304s.</li>
  <li><strong>Rate limits</strong> — per user or token; return <code>X-RateLimit-*</code> headers and 429 with <code>Retry-After</code>.</li>
  <li><strong>Input validation</strong> everywhere; reject unknown fields (<code>stripUnknown</code>/<code>additionalProperties: false</code>).</li>
  <li><strong>Authentication</strong> at the edge (bearer JWT or session cookie); <strong>authorization</strong> per-resource (RBAC/ABAC); never trust the client about their role.</li>
  <li><strong>Documentation</strong> — OpenAPI/Swagger, ideally generated from validation schemas. Treat the spec as a contract tested in CI.</li>
  <li><strong>Observability</strong> — requestId in every log/trace, latency + error metrics per endpoint (RED: rate/errors/duration).</li>
  <li><strong>HATEOAS</strong> is optional — few teams implement it fully; rarely pays off.</li>
</ul>
<p><strong>Breaking changes:</strong> never break existing API behavior. Add new versions or optional fields, deprecate old ones with a clear timeline, and emit <code>Deprecation</code>/<code>Sunset</code> headers.</p>
'''

ANSWERS[33] = r'''
<p>GraphQL gives clients a query language over your data graph — they pick exactly which fields and relationships to fetch. Node has first-class support.</p>
<pre><code>// Apollo Server 4 + Express
// npm install @apollo/server graphql dataloader
const { ApolloServer } = require("@apollo/server");
const { expressMiddleware } = require("@apollo/server/express4");
const DataLoader = require("dataloader");

// --- 1. Schema (SDL) ---
const typeDefs = `#graphql
  scalar DateTime
  type User { id: ID! name: String! posts: [Post!]! }
  type Post { id: ID! title: String! author: User! createdAt: DateTime! }

  type Query {
    me: User
    user(id: ID!): User
    posts(limit: Int = 20, cursor: String): PostConnection!
  }
  type PostConnection { nodes: [Post!]! nextCursor: String }

  type Mutation {
    createPost(title: String!, body: String!): Post!
  }

  type Subscription { postAdded: Post! }
`;

// --- 2. Resolvers ---
const resolvers = {
  Query: {
    me:    (_, __, ctx) =&gt; ctx.user,
    user:  (_, { id }, ctx) =&gt; ctx.loaders.user.load(id),
    posts: async (_, { limit, cursor }) =&gt; fetchPostsPaged(limit, cursor),
  },
  Mutation: {
    createPost: async (_, { title, body }, ctx) =&gt; {
      if (!ctx.user) throw new GraphQLError("auth required",
        { extensions: { code: "UNAUTHENTICATED" } });
      return Post.create({ title, body, authorId: ctx.user.id });
    },
  },
  // Field-level resolvers run per object — use DataLoader to batch
  Post: {
    author: (post, _, ctx) =&gt; ctx.loaders.user.load(post.authorId),
  },
};

// --- 3. Create loaders per-request (fresh cache per user) ---
function makeLoaders() {
  return {
    user: new DataLoader(async (ids) =&gt; {
      const users = await User.find({ _id: { $in: ids } }).lean();
      const map = new Map(users.map(u =&gt; [String(u._id), u]));
      return ids.map(id =&gt; map.get(String(id)) || null);
    }),
  };
}

// --- 4. Mount ---
const server = new ApolloServer({ typeDefs, resolvers });
await server.start();
app.use("/graphql", express.json(),
  expressMiddleware(server, {
    context: async ({ req }) =&gt; ({
      user: await userFromAuth(req),
      loaders: makeLoaders(),
    }),
  })
);
</code></pre>
<p><strong>N+1 problem:</strong> resolving 20 posts each with an <code>author</code> would naively trigger 20 user queries. <strong>DataLoader</strong> batches them into one <code>IN (...)</code> within the same tick — mandatory, not optional.</p>
<p><strong>Production must-haves:</strong> query depth/complexity limits (<code>graphql-depth-limit</code>, <code>graphql-query-complexity</code>) to prevent recursive DoS; disable introspection in production unless public; persisted queries for untrusted clients (only pre-registered query hashes allowed); field-level authz inside resolvers; tracing via Apollo's plugin or OpenTelemetry.</p>
<p><strong>Alternatives:</strong> <strong>Mercurius</strong> (Fastify + GraphQL), <strong>GraphQL Yoga</strong> (agnostic), <strong>Pothos</strong> (schema-first but TS-native). For TypeScript monorepos where client+server are shared, <strong>tRPC</strong> avoids GraphQL's complexity while giving type-safe RPCs.</p>
'''

ANSWERS[34] = r'''
<table>
  <thead><tr><th>Aspect</th><th>REST</th><th>GraphQL</th></tr></thead>
  <tbody>
    <tr><td>Endpoints</td><td>Many (one per resource)</td><td>One (<code>/graphql</code>)</td></tr>
    <tr><td>Data shape</td><td>Server-defined; client gets fixed shape</td><td>Client-specified in query; exactly what's needed</td></tr>
    <tr><td>Over-/under-fetching</td><td>Common — extra fields or multiple round trips</td><td>Rare — single query fetches nested relations</td></tr>
    <tr><td>Versioning</td><td>URL or header versions (<code>/v2/</code>)</td><td>Evolve schema; deprecate fields with <code>@deprecated</code></td></tr>
    <tr><td>Caching</td><td>HTTP cache works naturally (URL + method)</td><td>Harder — all queries hit one URL; need persisted queries or normalized client cache (Apollo, Relay)</td></tr>
    <tr><td>File uploads</td><td>Native (multipart/form-data)</td><td>Needs <code>graphql-upload</code> spec; awkward</td></tr>
    <tr><td>Learning curve</td><td>Shallow</td><td>Steeper — schema design, resolvers, DataLoader, subscriptions</td></tr>
    <tr><td>Tooling</td><td>OpenAPI/Swagger; Postman</td><td>Introspection → auto-generated docs; GraphiQL playground</td></tr>
    <tr><td>Type safety</td><td>Via OpenAPI code-gen or manual</td><td>Schema is the contract; many code generators</td></tr>
    <tr><td>Ops complexity</td><td>Low</td><td>Higher — query complexity limits, persisted queries, N+1 pitfalls</td></tr>
  </tbody>
</table>
<p><strong>Where REST wins:</strong> public APIs where third parties need stable, documented endpoints; CRUD services with clear resource boundaries; HTTP cacheability matters (CDN, browser cache); simple teams/small APIs where the overhead isn't justified.</p>
<p><strong>Where GraphQL wins:</strong> mobile/frontend teams fetching nested data across many resources; BFF (backend-for-frontend) pattern aggregating multiple microservices; rapidly evolving UIs where prescribed endpoints become a bottleneck; product teams want to iterate without waiting for API changes.</p>
<p><strong>Honest take:</strong> both are fine. The <em>worst</em> outcome is a REST API so ill-designed that clients must hit 15 endpoints to render a screen — GraphQL fixes that. A well-designed REST API with smart aggregation endpoints (<code>/dashboard?include=posts,comments</code>) often solves the same problem more cheaply.</p>
<p><strong>Don't forget:</strong> <strong>gRPC</strong> (binary, strongly-typed, fast, ideal for service-to-service), <strong>tRPC</strong> (TypeScript-native RPCs, zero schema definition), and <strong>JSON:API</strong>/<strong>HAL</strong> (standardized REST conventions). Choose based on who the client is and what problem you're solving.</p>
'''

ANSWERS[35] = r'''
<p>Database access in Node has several layers — pick based on control vs productivity trade-off.</p>
<table>
  <thead><tr><th>Tool</th><th>Abstraction</th><th>Best for</th></tr></thead>
  <tbody>
    <tr><td>Raw driver (<code>pg</code>, <code>mysql2</code>, <code>mongodb</code>)</td><td>None — you write queries</td><td>Maximum control, performance-critical queries</td></tr>
    <tr><td>Query builder (<code>knex</code>, <code>kysely</code>)</td><td>Programmatic SQL</td><td>Complex dynamic queries without ORM magic</td></tr>
    <tr><td>ORM (<code>prisma</code>, <code>typeorm</code>, <code>sequelize</code>, <code>mongoose</code>)</td><td>Objects ↔ rows</td><td>Domain modeling, migrations, relations</td></tr>
    <tr><td>Micro-ORM (<code>drizzle</code>, <code>mikro-orm</code>)</td><td>Types + queries</td><td>TS-first, minimal runtime overhead</td></tr>
  </tbody>
</table>
<pre><code>// Connection pooling — create once at startup, reuse across requests
const { Pool } = require("pg");
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,                       // peak concurrent connections
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 2_000,
});

app.get("/users/:id", async (req, res) =&gt; {
  const { rows } = await pool.query(
    "SELECT id, name, email FROM users WHERE id = $1",    // parameterized!
    [req.params.id],
  );
  res.json(rows[0]);
});

// With Prisma — typed queries, relations, migrations
const user = await prisma.user.findUnique({
  where: { id },
  include: { posts: { take: 10, orderBy: { createdAt: "desc" } } },
});
</code></pre>
<p><strong>Non-negotiables:</strong></p>
<ul>
  <li><strong>Parameterized queries</strong> — never concatenate user input into SQL. Prevents injection.</li>
  <li><strong>Connection pooling</strong> — a new connection per request will melt the DB. Pool size = peak concurrency; for serverless, use a pooler like PgBouncer or Neon's built-in.</li>
  <li><strong>Transactions</strong> for multi-statement operations that must be atomic.</li>
  <li><strong>Indexes</strong> — most perf issues trace to missing indexes, not the Node layer.</li>
  <li><strong>Migrations</strong> — schema changes in version control, run in CI/CD. Never manual DDL in production.</li>
</ul>
<p><strong>Observability:</strong> log slow queries (pg: <code>log_min_duration_statement</code>), instrument with OpenTelemetry (auto-instrumented for most drivers), track connection pool saturation as a metric. When the pool is exhausted, requests queue — p99 latency spikes are often pool exhaustion, not query speed.</p>
<p><strong>Special cases:</strong> <strong>Prisma</strong> is excellent for TypeScript projects with migrations and type-safe queries. <strong>Drizzle</strong> for SQL-like syntax with TS types, minimal overhead. <strong>Mongoose</strong> is the de-facto Mongo choice but schemaless flexibility comes at perf cost.</p>
'''

ANSWERS[36] = r'''
<table>
  <thead><tr><th>ORM</th><th>Style</th><th>Strengths</th><th>Caveats</th></tr></thead>
  <tbody>
    <tr><td><strong>Prisma</strong></td><td>Schema-first; generates client from <code>schema.prisma</code></td><td>Best TS types; great migrations; fast dev loop; clean query API</td><td>Engine binary (large); less query flexibility than raw SQL; historical cold-start issues (improved in 5+)</td></tr>
    <tr><td><strong>TypeORM</strong></td><td>Decorator-based entities (close to Hibernate/EF)</td><td>Feature-rich; supports many DBs; Active Record or Data Mapper patterns</td><td>Maintenance issues; many old bugs; migrations less polished; TS decorator requirement</td></tr>
    <tr><td><strong>Sequelize</strong></td><td>Class-based models; callback/promise era</td><td>Mature, widely used; supports MySQL/PG/MSSQL/SQLite</td><td>TypeScript types are weaker; dated feel; less ergonomic than Prisma</td></tr>
    <tr><td><strong>Mongoose</strong></td><td>Schema + Model abstraction for MongoDB</td><td>De-facto Mongo ODM; schema validation; middleware/hooks</td><td>Adds overhead over raw driver; schemaless philosophy partially lost</td></tr>
    <tr><td><strong>MikroORM</strong></td><td>Data Mapper + Identity Map pattern</td><td>Proper unit-of-work; TS-first</td><td>Learning curve; smaller community</td></tr>
    <tr><td><strong>Drizzle</strong></td><td>SQL-like DSL in TypeScript; ~zero runtime</td><td>Minimal overhead; great types; works in serverless/edge; migrations via kit</td><td>Newer (active dev); less mature than Prisma</td></tr>
    <tr><td><strong>Kysely</strong></td><td>Type-safe query builder (not an ORM)</td><td>Stellar TS types; write SQL-like; no magic</td><td>Not an ORM — no auto-relations/CRUD; manual migrations</td></tr>
    <tr><td><strong>Knex</strong></td><td>Query builder only (JS)</td><td>Works with any SQL DB; flexible</td><td>No types without helper; no model layer</td></tr>
  </tbody>
</table>
<p><strong>2026 recommendations:</strong></p>
<ul>
  <li><strong>Default choice for SQL TypeScript projects:</strong> <strong>Prisma</strong> — excellent type inference, strong migrations, growing community. Its only real downside is the engine binary (matters in serverless bundle size).</li>
  <li><strong>Serverless / edge / minimal bundles:</strong> <strong>Drizzle</strong> or <strong>Kysely</strong> — no runtime, tiny, work in Cloudflare Workers.</li>
  <li><strong>MongoDB:</strong> <strong>Mongoose</strong> if you want schemas + validation + hooks; otherwise use the native driver directly.</li>
  <li><strong>Complex OO domain models:</strong> <strong>MikroORM</strong> — true unit-of-work, identity map.</li>
  <li><strong>Avoid in new code:</strong> Sequelize (outdated DX), TypeORM (maintenance concerns).</li>
</ul>
<p><strong>ORM rule of thumb:</strong> great for CRUD and simple queries, mediocre for complex analytical ones. Drop to raw SQL (<code>$queryRaw</code>, <code>knex.raw</code>) for complex joins, CTEs, window functions — ORMs can generate awful queries. Always review with <code>EXPLAIN ANALYZE</code>.</p>
'''

ANSWERS[37] = r'''
<p>Migrations are version-controlled schema changes — each one is a file describing a forward (<code>up</code>) and reverse (<code>down</code>) transformation. They make DB schemas reviewable, reproducible, and deployable with code.</p>
<pre><code>// === Knex migration ===
// migrations/20260418_add_posts.js
exports.up = async function (knex) {
  await knex.schema.createTable("posts", (t) =&gt; {
    t.uuid("id").primary().defaultTo(knex.raw("gen_random_uuid()"));
    t.uuid("user_id").notNullable().references("id").inTable("users").onDelete("CASCADE");
    t.string("title", 200).notNullable();
    t.text("body").notNullable();
    t.boolean("published").notNullable().defaultTo(false);
    t.timestamps(true, true);            // created_at, updated_at
    t.index(["user_id", "created_at"]);
  });
};
exports.down = async function (knex) {
  await knex.schema.dropTable("posts");
};
// CLI:  knex migrate:latest   /   knex migrate:rollback

// === Prisma migration ===
// Edit schema.prisma, then:
//   npx prisma migrate dev --name add_posts    (generates + runs)
//   npx prisma migrate deploy                  (runs on prod)

// === TypeORM migration ===
@Entity()
export class Post { /* ... */ }
// CLI:  typeorm migration:generate src/migrations/AddPosts
//       typeorm migration:run
</code></pre>
<p><strong>Production workflow:</strong></p>
<ol>
  <li>Developer edits entity/schema locally.</li>
  <li>Generate migration; review the SQL (auto-generated ≠ correct).</li>
  <li>Commit to git; CI runs it against a staging DB; tests pass.</li>
  <li>Deploy pipeline runs migration <em>before</em> starting the new app version.</li>
  <li>If it fails, deployment halts; old version keeps running.</li>
</ol>
<p><strong>Safe migration rules (zero-downtime):</strong></p>
<ul>
  <li><strong>Never drop columns or tables in the same deploy that removes their usage</strong> — split across two releases: (1) stop writing, (2) stop reading, (3) drop.</li>
  <li><strong>Adding a NOT NULL column:</strong> add as nullable with default → backfill → add NOT NULL constraint — in steps.</li>
  <li><strong>Renames</strong>: create new column, dual-write in app, backfill, switch reads, drop old — <em>never</em> a single-step rename.</li>
  <li><strong>Big indexes on Postgres:</strong> use <code>CREATE INDEX CONCURRENTLY</code> (won't lock); not possible inside a transaction.</li>
  <li><strong>Long migrations</strong> on large tables: split into batches; time-bound each to avoid holding locks.</li>
  <li><strong>Always test migration + rollback on production-sized data</strong> before shipping.</li>
</ul>
<p><strong>Failure modes to plan for:</strong> migration takes longer than deploy timeout, migration locks a hot table, or rollback is impossible because data has changed. Use expand-contract patterns for anything risky.</p>
'''

ANSWERS[38] = r'''
<p>Sessions track a user's authenticated state across requests. Two models:</p>
<table>
  <thead><tr><th>Aspect</th><th>Server-side sessions</th><th>Token-based (JWT)</th></tr></thead>
  <tbody>
    <tr><td>State</td><td>Server stores session; client holds opaque ID</td><td>Client holds signed claims; server verifies</td></tr>
    <tr><td>Revocation</td><td>Delete server record — instant</td><td>Blacklist/version-check required — harder</td></tr>
    <tr><td>Horizontal scaling</td><td>Needs shared store (Redis)</td><td>Stateless — any instance can validate</td></tr>
    <tr><td>Size</td><td>Small cookie ID (~32 bytes)</td><td>Token can be large (~1 KB)</td></tr>
    <tr><td>Use case</td><td>Classic web apps, admin panels</td><td>SPAs, mobile, microservices</td></tr>
  </tbody>
</table>
<pre><code>// === express-session + Redis store — the pragmatic server-side option ===
const session = require("express-session");
const RedisStore = require("connect-redis").default;
const { createClient } = require("redis");
const redis = createClient({ url: process.env.REDIS_URL });
await redis.connect();

app.use(session({
  store: new RedisStore({ client: redis, prefix: "sess:" }),
  name: "sid",                     // don't leak framework
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,        // create session only on login
  rolling: true,                    // refresh expiry on every request
  cookie: {
    httpOnly: true,
    secure: true,                   // HTTPS only
    sameSite: "lax",                // CSRF defense
    maxAge: 24 * 3600 * 1000,
    path: "/",
  },
}));

app.post("/login", async (req, res) =&gt; {
  const user = await authenticate(req.body);
  req.session.userId = user.id;
  req.session.role = user.role;
  res.json({ ok: true });
});

app.post("/logout", (req, res) =&gt; {
  req.session.destroy(() =&gt; {
    res.clearCookie("sid");
    res.status(204).end();
  });
});
</code></pre>
<p><strong>Session fixation:</strong> regenerate the session ID on login (<code>req.session.regenerate()</code>) — otherwise an attacker who obtained a pre-login session ID can hijack the authenticated session.</p>
<p><strong>Storage choice:</strong> Redis is the default — fast, supports TTL natively, widely understood. Memory store is <em>never</em> for production (lost on restart, no multi-instance). DB store works but adds load. For globally distributed deployments, use Redis with replicas or regional stores.</p>
<p><strong>Hybrid (best of both):</strong> store an opaque session ID in an <code>httpOnly</code> cookie; keep session data (user, roles, tenant) in Redis. Same ergonomics as JWT for SPAs but with instant revocation. This is what most mature products actually do.</p>
'''

ANSWERS[39] = r'''
<p><strong>Authentication</strong> (who are you?) and <strong>authorization</strong> (what can you do?) are distinct — solve each explicitly.</p>
<p><strong>Auth strategies:</strong></p>
<ul>
  <li><strong>Password-based</strong> — bcrypt/argon2 for hashing (cost ≥ 12); account lockout + exponential backoff; password breach check (haveibeenpwned API); 2FA/TOTP.</li>
  <li><strong>Session cookies</strong> — server stores session; cookie contains opaque ID. Easy revocation, strong CSRF defense via <code>SameSite</code>.</li>
  <li><strong>JWT (access + refresh)</strong> — stateless access token (15 min TTL), longer refresh token for rotation. Fits SPAs/mobile.</li>
  <li><strong>OAuth 2.0 / OIDC</strong> — delegate to Google/GitHub/Apple/Microsoft. Use <code>passport</code> or <code>@node-oauth/oauth2-server</code>.</li>
  <li><strong>API keys</strong> — for service-to-service. Store hashed; rotate; scope narrowly.</li>
  <li><strong>mTLS</strong> — for very high-security service-to-service.</li>
</ul>
<pre><code>// JWT + RBAC — representative pattern
const jwt = require("jsonwebtoken");

function authRequired(req, res, next) {
  const token = req.headers.authorization?.slice(7);
  if (!token) return res.status(401).json({ error: "auth_required" });
  try {
    req.user = jwt.verify(token, process.env.JWT_PUBLIC_KEY, { algorithms: ["RS256"] });
    next();
  } catch { res.status(401).json({ error: "invalid_token" }); }
}

function requireRole(...roles) {
  return (req, res, next) =&gt;
    roles.includes(req.user?.role)
      ? next()
      : res.status(403).json({ error: "forbidden" });
}

function requireOwnership(getOwnerId) {
  return async (req, res, next) =&gt; {
    const ownerId = await getOwnerId(req);
    if (ownerId !== req.user.sub &amp;&amp; req.user.role !== "admin") {
      return res.status(403).json({ error: "forbidden" });
    }
    next();
  };
}

// Usage
app.get("/admin/users", authRequired, requireRole("admin"), listUsers);
app.patch("/posts/:id",
  authRequired,
  requireOwnership((req) =&gt; Post.findById(req.params.id).select("authorId")),
  updatePost
);
</code></pre>
<p><strong>Authorization depth:</strong> middleware-level checks (does user have role X?) are coarse. Deeper patterns — <strong>ABAC</strong> (attribute-based, e.g., "editor on their own team's docs"), <strong>policy engines</strong> (<strong>OPA</strong>, <strong>Casbin</strong>, <strong>Oso</strong>) — scale better as rules grow. Centralize authz as the logic gets complex; scattering it across controllers ensures bugs.</p>
<p><strong>Libraries:</strong> <strong>Passport</strong> (many strategies, stable), <strong>Auth.js / next-auth</strong> (for Next.js and standalone Node), <strong>Lucia Auth</strong> (new, session-focused). For OAuth servers, <strong>ory Hydra</strong> or managed (Auth0, Clerk, WorkOS) save months of work.</p>
'''

ANSWERS[40] = r'''
<table>
  <thead><tr><th>Aspect</th><th>Session-based</th><th>Token-based (JWT)</th></tr></thead>
  <tbody>
    <tr><td>Server state</td><td>Stored in Redis/DB; client has opaque ID cookie</td><td>Token carries claims; server verifies signature only</td></tr>
    <tr><td>Revocation</td><td>Instant — delete server record</td><td>Requires revocation list, short TTL, or tokenVersion bump</td></tr>
    <tr><td>Scaling out</td><td>Needs shared session store</td><td>Any server instance can validate</td></tr>
    <tr><td>Storage</td><td>Cookie (typically <code>httpOnly</code>, <code>secure</code>)</td><td>Cookie (same) or <code>Authorization: Bearer</code> header</td></tr>
    <tr><td>CSRF</td><td>Cookie-bound — <code>SameSite</code> helps; CSRF tokens for sensitive ops</td><td>Bearer header is CSRF-immune; cookie-stored JWT still needs protection</td></tr>
    <tr><td>XSS</td><td><code>httpOnly</code> cookie blocks JS access</td><td>If stored in <code>localStorage</code>, XSS = game over. <code>httpOnly</code> cookie required</td></tr>
    <tr><td>Mobile / native</td><td>Awkward (cookie jar per app)</td><td>Natural (send in header)</td></tr>
    <tr><td>Microservices</td><td>Needs shared session store</td><td>Any service can verify with public key (RS256)</td></tr>
    <tr><td>Size on wire</td><td>~32 bytes</td><td>~1 KB typical</td></tr>
  </tbody>
</table>
<p><strong>The hard truth about "stateless" JWT:</strong> unless you're fine waiting up to the token TTL to revoke compromised accounts, you need server-side state anyway — a blacklist, tokenVersion field, or refresh-token table. So "JWT is stateless" is half-true in real systems. The right mental model: JWT gives you a <strong>short-lived</strong> credential that's cheap to verify; anything longer needs revocation support.</p>
<p><strong>Modern best practice:</strong> the <strong>access + refresh split</strong>:</p>
<ul>
  <li><strong>Access token</strong> (JWT, 15 min TTL) — sent with every request; verified without DB hit.</li>
  <li><strong>Refresh token</strong> (opaque, stored server-side, 2 weeks TTL) — stored in <code>httpOnly</code> cookie; exchanged for a new access token; rotated on use (reuse detection = revoke all for that user).</li>
</ul>
<p><strong>Pick based on context:</strong> traditional web app with one origin → sessions (simpler, instant revocation). SPA + mobile + microservices → access+refresh JWT. For new projects, err toward sessions unless you have specific reasons — they're simpler and the "stateless" savings rarely matter at most scales.</p>
'''

ANSWERS[41] = r'''
<table>
  <thead><tr><th>Library</th><th>Role</th><th>Notes</th></tr></thead>
  <tbody>
    <tr><td><strong>jsonwebtoken</strong> (npm: <code>jsonwebtoken</code>)</td><td>Sign &amp; verify JWTs</td><td>Most widely used; supports HS256/RS256/ES256; has historical CVEs — keep updated and pass <code>algorithms</code> explicitly</td></tr>
    <tr><td><strong>jose</strong></td><td>Full JOSE (JWT + JWS + JWE + JWK)</td><td>Modern, zero-deps; the right choice for new code; encryption support</td></tr>
    <tr><td><strong>fast-jwt</strong></td><td>Fast JWT sign/verify</td><td>Optimized for Fastify; bigger perf win than you'd expect at high RPS</td></tr>
    <tr><td><strong>express-jwt</strong></td><td>Express middleware wrapper</td><td>Convenient but thin; most apps roll their own middleware</td></tr>
    <tr><td><strong>passport-jwt</strong></td><td>Passport strategy</td><td>If you use Passport for other strategies too</td></tr>
    <tr><td><strong>jwks-rsa</strong></td><td>Fetch &amp; cache JWKs from a JWKS endpoint</td><td>Required when verifying tokens from Auth0, Cognito, Firebase, etc.</td></tr>
    <tr><td><strong>@fastify/jwt</strong></td><td>Fastify-native plugin</td><td>Uses fast-jwt under the hood</td></tr>
  </tbody>
</table>
<pre><code>// Modern pattern — jose + RS256 + JWKS
const { SignJWT, jwtVerify, createRemoteJWKSet } = require("jose");
const crypto = require("crypto");

// Signing (issuer)
const privateKey = await importPKCS8(PRIVATE_KEY_PEM, "RS256");
const token = await new SignJWT({ sub: user.id, role: user.role })
  .setProtectedHeader({ alg: "RS256", kid: "key-1" })
  .setIssuer("https://api.example.com")
  .setAudience("https://app.example.com")
  .setIssuedAt()
  .setExpirationTime("15m")
  .setJti(crypto.randomUUID())
  .sign(privateKey);

// Verification (consumer — can be a different service)
const JWKS = createRemoteJWKSet(new URL("https://api.example.com/.well-known/jwks.json"));
const { payload } = await jwtVerify(token, JWKS, {
  issuer: "https://api.example.com",
  audience: "https://app.example.com",
  algorithms: ["RS256"],
});
</code></pre>
<p><strong>Security essentials (don't skip any):</strong></p>
<ul>
  <li><strong>Always pass <code>algorithms: [...]</code></strong> when verifying — prevents "alg: none" attacks and key confusion.</li>
  <li><strong>Use asymmetric (RS256/ES256) for microservices</strong> — signers keep private keys; verifiers only need public keys.</li>
  <li><strong>Set <code>iss</code>, <code>aud</code>, <code>exp</code></strong> — and verify them. Unbounded tokens are a liability.</li>
  <li><strong>Short TTL (15 min)</strong> for access tokens; refresh token for longer sessions.</li>
  <li><strong>Rotate keys</strong> — use <code>kid</code> header and JWKS so rotation is zero-downtime.</li>
  <li><strong>Never put secrets/PII in the payload</strong> — JWTs are signed, not encrypted. Use JWE if you need encryption.</li>
</ul>
<p><strong>Recommendation:</strong> for new code, use <code>jose</code> over <code>jsonwebtoken</code>. It has a better API, supports JWE, and avoids historical footguns.</p>
'''

ANSWERS[42] = r'''
<p>RBAC assigns permissions to <em>roles</em>, then assigns roles to users. Authorization checks become: "does this user have a role that holds the needed permission?"</p>
<pre><code>// --- Schema ---
// users         (id, email, ...)
// roles         (id, name)                    — "admin", "editor", "viewer"
// permissions   (id, name)                    — "post:create", "post:delete", "user:list"
// role_permissions (role_id, permission_id)
// user_roles       (user_id, role_id)

// --- Load roles+perms once per auth, attach to req.user ---
async function loadUserPermissions(userId) {
  const rows = await db.query(`
    SELECT DISTINCT p.name
    FROM user_roles ur
    JOIN role_permissions rp ON rp.role_id = ur.role_id
    JOIN permissions p        ON p.id = rp.permission_id
    WHERE ur.user_id = $1
  `, [userId]);
  return new Set(rows.map(r =&gt; r.name));
}

// --- Middleware ---
function can(...required) {
  return (req, res, next) =&gt; {
    if (!req.user) return res.status(401).json({ error: "auth_required" });
    for (const perm of required) {
      if (!req.user.permissions.has(perm)) {
        return res.status(403).json({ error: "forbidden", missing: perm });
      }
    }
    next();
  };
}

// --- Usage ---
app.post  ("/posts",       authRequired, can("post:create"), createPost);
app.delete("/posts/:id",   authRequired, can("post:delete"), deletePost);
app.get   ("/admin/users", authRequired, can("user:list"), listUsers);

// --- Ownership + role combo ---
app.patch("/posts/:id", authRequired, async (req, res, next) =&gt; {
  const post = await Post.findById(req.params.id);
  if (!post) return res.status(404).end();
  const owns = post.authorId === req.user.id;
  const isAdmin = req.user.permissions.has("post:edit_any");
  if (!owns &amp;&amp; !isAdmin) return res.status(403).json({ error: "forbidden" });
  req.post = post;
  next();
}, updatePost);
</code></pre>
<p><strong>Design principles:</strong></p>
<ul>
  <li><strong>Permissions are verbs on resources</strong> (<code>post:create</code>, <code>user:delete</code>) — not roles. Roles group permissions; you check permissions.</li>
  <li><strong>Cache permission lookups</strong> per request — put them on <code>req.user.permissions</code> during auth.</li>
  <li><strong>Fail closed</strong> — default deny. Missing role/permission = 403, never 200.</li>
  <li><strong>Audit log every authorization decision</strong> for sensitive actions — "user X granted role Y by user Z."</li>
</ul>
<p><strong>When RBAC isn't enough:</strong> <strong>ABAC</strong> (attribute-based) evaluates context — "editor on docs they created" or "admin during business hours in their region." For complex policies, use a <strong>policy engine</strong>: <strong>OPA</strong> (Open Policy Agent, language-agnostic), <strong>Casbin</strong> (Node-native), <strong>Oso</strong>, or <strong>Cedar</strong> (AWS). Write rules once, evaluate everywhere; avoid scattering authz logic across controllers.</p>
<p><strong>Multi-tenant apps:</strong> scope every check by tenant — "admin of <em>this</em> org", not "admin globally". A common SaaS bug is granting permissions that accidentally span tenants.</p>
'''

ANSWERS[43] = r'''
<p>Defense-in-depth — no single layer is enough.</p>
<p><strong>At rest (database, files, backups):</strong></p>
<ul>
  <li><strong>Disk encryption</strong> — enabled by default on managed cloud DBs (RDS, Cloud SQL) and storage. Doesn't protect against compromised DB credentials.</li>
  <li><strong>Column-level encryption</strong> for highly sensitive fields (SSN, payment tokens, PHI). Encrypt in app with envelope encryption: data key encrypts data, KMS key encrypts data key. Libraries: AWS Encryption SDK, GCP Tink, or hand-rolled with <code>crypto.createCipheriv</code>.</li>
  <li><strong>Tokenization</strong> — replace sensitive values with tokens, store originals in a locked vault (Stripe, AWS Payment Crypto).</li>
  <li><strong>Hash, don't encrypt, passwords</strong> — bcrypt/argon2. Encrypted passwords can be decrypted by attackers with the key; hashes can't.</li>
</ul>
<p><strong>In transit:</strong> TLS 1.2+ everywhere, HSTS with preload, certificate pinning for mobile clients, mTLS for service-to-service in zero-trust networks.</p>
<p><strong>In use / in memory:</strong> clear sensitive buffers when done (<code>buffer.fill(0)</code>), avoid logging request bodies, redact in APM traces.</p>
<pre><code>// Envelope encryption example (AES-256-GCM)
const crypto = require("crypto");

function encrypt(plaintext, dataKey) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", dataKey, iv);
  const ciphertext = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  const tag = cipher.getAuthTag();
  // Store iv + tag + ciphertext together (base64)
  return Buffer.concat([iv, tag, ciphertext]).toString("base64");
}

function decrypt(encoded, dataKey) {
  const buf = Buffer.from(encoded, "base64");
  const iv = buf.subarray(0, 12);
  const tag = buf.subarray(12, 28);
  const ciphertext = buf.subarray(28);
  const decipher = crypto.createDecipheriv("aes-256-gcm", dataKey, iv);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString("utf8");
}
</code></pre>
<p><strong>Secrets management:</strong> never commit secrets. Use <strong>AWS Secrets Manager</strong>, <strong>HashiCorp Vault</strong>, <strong>Doppler</strong>, <strong>Infisical</strong>, or cloud KMS. Inject as env vars at runtime; rotate on schedule (DB passwords, API keys) and on suspected compromise. For development, use <code>.env.local</code> (gitignored); tools like <code>dotenvx</code> can encrypt dotfiles.</p>
<p><strong>Logs:</strong> redact PII, auth headers, tokens, passwords — always. Pino's <code>redact</code> config is your friend. Review what's shipped to third-party loggers; many breaches come from leaked log data.</p>
<p><strong>Compliance:</strong> PCI (payment), HIPAA (health), GDPR/CCPA (privacy) add requirements — data location, right-to-erasure, audit logs, key management. Plan for it early; retrofitting is painful.</p>
'''

ANSWERS[44] = r'''
<p>The <code>crypto</code> module wraps OpenSSL. It provides symmetric/asymmetric ciphers, hashes, HMACs, key derivation, and secure random. Pick modern algorithms; avoid defaults from older tutorials.</p>
<pre><code>const crypto = require("crypto");

// === 1. Symmetric encryption — AES-256-GCM (authenticated) ===
function encryptSymmetric(plaintext, key) {       // key: 32-byte Buffer
  const iv = crypto.randomBytes(12);              // GCM uses 12-byte IV
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const ct = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  return { iv, ct, tag: cipher.getAuthTag() };
}
function decryptSymmetric({ iv, ct, tag }, key) {
  const d = crypto.createDecipheriv("aes-256-gcm", key, iv);
  d.setAuthTag(tag);                              // throws if tampered
  return Buffer.concat([d.update(ct), d.final()]).toString("utf8");
}

// === 2. Key derivation from a password — scrypt or argon2 (not SHA of password!) ===
const key = crypto.scryptSync(password, salt, 32);   // 32 bytes for AES-256

// === 3. Asymmetric encryption — RSA-OAEP (for small payloads or hybrid schemes) ===
const { publicKey, privateKey } = crypto.generateKeyPairSync("rsa", {
  modulusLength: 2048,
});
const encrypted = crypto.publicEncrypt(
  { key: publicKey, oaepHash: "sha256", padding: crypto.constants.RSA_PKCS1_OAEP_PADDING },
  Buffer.from("secret"),
);
const decrypted = crypto.privateDecrypt(
  { key: privateKey, oaepHash: "sha256", padding: crypto.constants.RSA_PKCS1_OAEP_PADDING },
  encrypted,
);

// === 4. Digital signatures — sign with private, verify with public ===
const sig = crypto.sign("sha256", Buffer.from("message"), privateKey);
const valid = crypto.verify("sha256", Buffer.from("message"), publicKey, sig);

// === 5. HMAC — message integrity with shared secret ===
const hmac = crypto.createHmac("sha256", sharedSecret).update(data).digest("hex");

// === 6. Secure random — tokens, session IDs ===
const token = crypto.randomBytes(32).toString("base64url");

// === 7. Timing-safe comparison — for tokens, signatures ===
const equal = crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
</code></pre>
<p><strong>Rules you must not break:</strong></p>
<ul>
  <li><strong>Use authenticated encryption</strong> (AES-GCM, ChaCha20-Poly1305) — plain CBC is broken by padding-oracle attacks in the wild.</li>
  <li><strong>Never reuse IVs/nonces</strong> with the same key — for GCM, reuse is catastrophic. Use <code>randomBytes</code> every time.</li>
  <li><strong>Don't hash passwords with SHA-256</strong> — use bcrypt/scrypt/argon2. Plain hashes are GPU-cracked at millions/sec.</li>
  <li><strong>Compare secrets with <code>timingSafeEqual</code></strong>, not <code>===</code>. Prevents timing attacks.</li>
  <li><strong>Don't roll your own crypto protocols</strong> — use TLS, libsodium (<code>@noble/*</code>, <code>tweetnacl</code>), or <code>jose</code> for higher-level work.</li>
  <li><strong>Key management is harder than encryption</strong> — use KMS/Vault for production keys.</li>
</ul>
<p><strong>Alternative:</strong> <strong>libsodium</strong> (via <code>sodium-native</code> or <code>@noble/ciphers</code>) offers safer defaults and modern primitives (XChaCha20-Poly1305, Ed25519) without footgun opportunities. Prefer it for new crypto work when you're not constrained to OpenSSL.</p>
'''

ANSWERS[45] = r'''
<p>Rate limiting caps how many requests an identity (IP, user, API key) can make per time window, protecting against abuse, brute force, and resource exhaustion. Algorithm choice matters.</p>
<table>
  <thead><tr><th>Algorithm</th><th>Pros</th><th>Cons</th></tr></thead>
  <tbody>
    <tr><td><strong>Fixed window</strong> (counter resets every N sec)</td><td>Dead simple</td><td>Boundary-burst: 100 at 12:59:59 and 100 at 13:00:00 = 200 in 1s</td></tr>
    <tr><td><strong>Sliding window counter</strong> (timestamps in a set)</td><td>Accurate; no burst issue</td><td>More memory; atomic update needs Lua script</td></tr>
    <tr><td><strong>Token bucket</strong></td><td>Smooth bursts; classic</td><td>Tune refill rate + capacity</td></tr>
    <tr><td><strong>Leaky bucket</strong></td><td>Smooth constant output</td><td>No burst tolerance</td></tr>
  </tbody>
</table>
<pre><code>// --- express-rate-limit + rate-limit-redis — production-ready out of the box ---
// npm install express-rate-limit rate-limit-redis ioredis
const rateLimit = require("express-rate-limit");
const RedisStore = require("rate-limit-redis").default;
const Redis = require("ioredis");
const redis = new Redis(process.env.REDIS_URL);

const apiLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) =&gt; redis.call(...args) }),
  windowMs: 60_000,                 // 1 min
  limit: 100,                       // per key
  keyGenerator: (req) =&gt; req.user?.id || req.ip,
  standardHeaders: "draft-7",       // RateLimit-Limit, -Remaining, -Reset
  legacyHeaders: false,
  handler: (req, res) =&gt; res.status(429).json({
    error: "rate_limit", retryAfter: res.getHeader("Retry-After"),
  }),
});

// Strict per-endpoint limits for sensitive ops
const loginLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) =&gt; redis.call(...args) }),
  windowMs: 15 * 60_000,
  limit: 5,
  keyGenerator: (req) =&gt; req.body?.email || req.ip,      // per-email, not IP
});

app.use("/api", apiLimiter);
app.post("/auth/login", loginLimiter, loginHandler);

// --- Tiered limits — premium users get more ---
const tierLimiter = (req) =&gt; {
  const limit = req.user?.plan === "enterprise" ? 10_000
              : req.user?.plan === "premium" ? 1_000 : 100;
  return rateLimit({ store, windowMs: 60_000, limit, /* ... */ });
};
</code></pre>
<p><strong>Critical design decisions:</strong></p>
<ul>
  <li><strong>Redis, not in-memory</strong> — multi-instance apps need shared counters or limits are per-process and trivially bypassable by load-balancing.</li>
  <li><strong>Key on user ID when authenticated</strong>, IP when anonymous — IP-only limits unfairly throttle NATed users (offices, mobile carriers).</li>
  <li><strong>Fail open</strong> on Redis outage — don't take down the whole API if the rate limiter dies. Log the event and let requests through.</li>
  <li><strong>Stricter limits on auth/reset/signup</strong> — these are brute-force targets.</li>
  <li><strong>Return proper headers</strong> — <code>X-RateLimit-Limit</code>, <code>X-RateLimit-Remaining</code>, <code>X-RateLimit-Reset</code>, <code>Retry-After</code> on 429.</li>
  <li><strong>Don't count cache hits</strong> or health checks — skew metrics.</li>
</ul>
<p><strong>Where to rate-limit:</strong> Node app for semantic limits (per user, per endpoint). At the <strong>edge</strong> (Cloudflare, AWS WAF, nginx) for volumetric DDoS. Both layers complement each other.</p>
'''

ANSWERS[46] = r'''
<p>Version the API when you need to change behavior without breaking existing clients — rename fields, change types, restructure resources. The goal is to buy time to migrate clients, not version forever.</p>
<table>
  <thead><tr><th>Strategy</th><th>Example</th><th>Pros</th><th>Cons</th></tr></thead>
  <tbody>
    <tr><td><strong>URL path</strong></td><td><code>/api/v1/users</code></td><td>Visible; easy to test; cacheable</td><td>Every URL changes between versions</td></tr>
    <tr><td><strong>Header</strong></td><td><code>Accept: application/vnd.api.v1+json</code></td><td>Purer REST; URL stable</td><td>Harder to test from a browser; cache keys need <code>Vary</code></td></tr>
    <tr><td><strong>Query param</strong></td><td><code>?api_version=1</code></td><td>Simple fallback</td><td>Looks like data; often conflated with params</td></tr>
    <tr><td><strong>Subdomain</strong></td><td><code>v1.api.example.com</code></td><td>Different deploys per version</td><td>DNS complexity; CORS</td></tr>
    <tr><td><strong>Date-based</strong></td><td><code>API-Version: 2026-04-18</code></td><td>Granular — Stripe model</td><td>Complex to implement server-side</td></tr>
  </tbody>
</table>
<pre><code>// === URL path versioning (most pragmatic) ===
const v1 = express.Router();
v1.use("/users", v1UserRouter);
v1.use("/posts", v1PostRouter);

const v2 = express.Router();
v2.use("/users", v2UserRouter);    // renamed "displayName" → "name"
v2.use("/posts", v2PostRouter);

app.use("/api/v1", v1);
app.use("/api/v2", v2);

// Deprecation: add Sunset + Deprecation headers on old version
v1.use((req, res, next) =&gt; {
  res.setHeader("Deprecation", "true");
  res.setHeader("Sunset", "Wed, 31 Dec 2026 23:59:59 GMT");
  res.setHeader("Link", '&lt;/api/v2/&gt;; rel="successor-version"');
  next();
});
</code></pre>
<p><strong>Version management practices:</strong></p>
<ul>
  <li><strong>Only major versions</strong> — breaking changes bump the version. Additive changes (new optional fields, new endpoints) don't need a version; all clients ignore unknown fields safely.</li>
  <li><strong>Support ≥ 2 versions concurrently</strong> — give clients time to migrate. Publish a sunset date.</li>
  <li><strong>Share as much code as possible</strong> — put business logic in services; only HTTP/serialization differs per version.</li>
  <li><strong>Monitor version usage</strong> — metrics per version reveal when it's safe to retire an old one.</li>
  <li><strong>Document breaking changes</strong> clearly in changelog; migration guides help adoption.</li>
</ul>
<p><strong>Prefer not to version at all:</strong> design APIs so they evolve additively. Make fields optional, accept extra fields, version individual fields with fallbacks. Stripe's "never break clients" philosophy uses date-based versions but with server-side transformers that translate old requests to the latest format — dramatically lower maintenance than running multiple parallel codebases.</p>
<p><strong>GraphQL:</strong> typically versionless — add new fields, deprecate old ones with <code>@deprecated(reason: "...")</code>, track usage, remove when unused.</p>
'''

ANSWERS[47] = r'''
<p>Good error handling is less about catching errors and more about shaping them into something usable.</p>
<p><strong>The principles:</strong></p>
<ol>
  <li><strong>Errors should carry intent</strong> — a bare <code>new Error("not found")</code> loses information. Use typed classes with <code>statusCode</code>, <code>code</code>, and context.</li>
  <li><strong>Operational vs programmer errors</strong> — operational (validation failed, resource missing) are expected; programmer errors (null pointer, bad state) are bugs and should crash. Don't catch-and-continue on programmer errors.</li>
  <li><strong>Centralize error handling</strong> — one middleware handles the response shape; individual handlers <code>throw</code> or <code>next(err)</code>.</li>
  <li><strong>Translate third-party errors</strong> at the boundary — wrap DB/HTTP errors into your domain errors in the infrastructure layer.</li>
  <li><strong>Never swallow errors</strong> — empty <code>catch</code> blocks hide production incidents.</li>
  <li><strong>Log with full context</strong> — request ID, user, operation, and the error chain (<code>cause</code>).</li>
  <li><strong>Don't leak internals</strong> in production responses — hide stack traces, raw SQL, internal file paths.</li>
</ol>
<pre><code>// --- Typed errors with cause chain ---
class AppError extends Error {
  constructor(message, { statusCode = 500, code = "INTERNAL", cause, isOperational = true } = {}) {
    super(message, { cause });     // ES2022 — preserves inner error
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = isOperational;
    Error.captureStackTrace(this, this.constructor);
  }
}
class NotFoundError extends AppError {
  constructor(msg = "not found") { super(msg, { statusCode: 404, code: "NOT_FOUND" }); }
}
class ValidationError extends AppError {
  constructor(issues) { super("validation failed", { statusCode: 400, code: "VALIDATION" }); this.issues = issues; }
}

// --- Wrapping lower-layer errors ---
async function fetchUser(id) {
  try {
    return await db.user.findUniqueOrThrow({ where: { id } });
  } catch (err) {
    if (err.code === "P2025") throw new NotFoundError(`user ${id}`);      // Prisma not-found
    throw new AppError("db error", { cause: err, isOperational: false });
  }
}

// --- Central Express handler ---
app.use((err, req, res, _next) =&gt; {
  const status = err.statusCode || 500;
  if (status &gt;= 500 || !err.isOperational) {
    req.log.error({ err, requestId: req.id }, "unhandled");
  }
  res.status(status).json({
    error: {
      code: err.code || "INTERNAL",
      message: err.isOperational ? err.message : "internal server error",
      ...(err.issues &amp;&amp; { issues: err.issues }),
    },
    requestId: req.id,
  });
});

// --- Top-level traps ---
process.on("uncaughtException",  (err) =&gt; { log.fatal({ err }, "uncaught"); process.exit(1); });
process.on("unhandledRejection", (err) =&gt; { log.fatal({ err }, "unhandled rejection"); process.exit(1); });
</code></pre>
<p><strong>Express 5 gotcha:</strong> Express 4 needed manual <code>try/catch</code> around every async handler and <code>next(err)</code> — forgetting this swallowed errors silently. Express 5 handles rejected promises automatically, but check your version; many tutorials still assume v4.</p>
<p><strong>Retry philosophy:</strong> retry with exponential backoff for transient errors (network, 5xx, rate limit); <em>never</em> retry non-idempotent operations without idempotency keys; circuit-break after N failures to avoid cascading.</p>
'''

ANSWERS[48] = r'''
<p>Custom error classes let you <em>throw meaningfully</em> — callers distinguish categories, middleware produces correct responses, logging has structured context. Without them, you're left inspecting <code>err.message</code> strings.</p>
<pre><code>// --- Base class — captures common shape, preserves prototype chain ---
class AppError extends Error {
  constructor(message, options = {}) {
    super(message, { cause: options.cause });    // ES2022 cause chain
    this.name = this.constructor.name;
    this.statusCode = options.statusCode ?? 500;
    this.code = options.code ?? "INTERNAL";
    this.isOperational = options.isOperational ?? true;
    this.meta = options.meta;                    // extra structured data
    Error.captureStackTrace(this, this.constructor);
  }

  // Serialize for JSON response (strip stack in production)
  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      ...(this.meta &amp;&amp; { meta: this.meta }),
      ...(process.env.NODE_ENV !== "production" &amp;&amp; { stack: this.stack }),
    };
  }
}

// --- Concrete subclasses — one per domain concept ---
class NotFoundError extends AppError {
  constructor(resource, id) {
    super(`${resource} not found`, { statusCode: 404, code: "NOT_FOUND", meta: { resource, id } });
  }
}
class ValidationError extends AppError {
  constructor(issues) {
    super("validation failed", { statusCode: 400, code: "VALIDATION", meta: { issues } });
  }
}
class UnauthorizedError extends AppError {
  constructor(msg = "authentication required") { super(msg, { statusCode: 401, code: "UNAUTH" }); }
}
class ForbiddenError extends AppError {
  constructor(msg = "forbidden") { super(msg, { statusCode: 403, code: "FORBIDDEN" }); }
}
class ConflictError extends AppError {
  constructor(msg, meta) { super(msg, { statusCode: 409, code: "CONFLICT", meta }); }
}
class RateLimitError extends AppError {
  constructor(retryAfter) { super("rate limited", { statusCode: 429, code: "RATE_LIMIT", meta: { retryAfter } }); }
}
class ExternalServiceError extends AppError {
  constructor(service, cause) {
    super(`${service} unavailable`, { statusCode: 502, code: "EXT_SVC", cause, isOperational: false });
  }
}

// --- Usage ---
async function getPost(id) {
  const post = await Post.findById(id);
  if (!post) throw new NotFoundError("post", id);
  return post;
}

async function chargeCard(token, amount) {
  try {
    return await stripe.charges.create({ source: token, amount });
  } catch (err) {
    if (err.code === "card_declined") {
      throw new AppError("card declined", { statusCode: 402, code: "CARD_DECLINED", cause: err });
    }
    throw new ExternalServiceError("stripe", err);
  }
}

// --- Type checks that work across files/packages ---
if (err instanceof NotFoundError) { /* ... */ }
if (err instanceof AppError &amp;&amp; err.statusCode === 409) { /* ... */ }
</code></pre>
<p><strong>Design guidelines:</strong></p>
<ul>
  <li><strong>Small fixed set</strong> — don't make 50 error classes. 5-10 cover 99% of cases.</li>
  <li><strong>Prefer <code>code</code> string</strong> over class-based checks in client-facing APIs — clients can't import your classes.</li>
  <li><strong>Preserve <code>cause</code></strong> — when wrapping a lower-layer error, pass it in <code>cause</code> so logs show the full chain.</li>
  <li><strong>Don't override builtins</strong> — don't subclass <code>TypeError</code>/<code>RangeError</code>/<code>SyntaxError</code>; they have special semantics.</li>
  <li><strong>Stack traces across packages</strong> — if your errors lose their prototype when crossing boundaries (rare but possible with older libraries/bundlers), add a <code>name</code> check as fallback: <code>err.name === "NotFoundError"</code>.</li>
</ul>
'''

ANSWERS[49] = r'''
<p>Async errors have three shapes in Node: <strong>rejected promises</strong>, <strong>thrown exceptions inside <code>async</code> functions</strong>, and <strong>emitted errors</strong> on streams/EventEmitters. Each requires matching handling.</p>
<pre><code>// === 1. async/await + try/catch — the modern default ===
async function loadUser(id) {
  try {
    const user = await db.user.findUnique({ where: { id } });
    if (!user) throw new NotFoundError();
    return user;
  } catch (err) {
    // Handle, rethrow, or wrap
    throw err;
  }
}

// === 2. Promise chain — .catch() ===
fetch("/api").then(handle).catch(err =&gt; log.error(err));

// === 3. Promise.allSettled — multiple independent awaits, collect all results ===
const [u, p, c] = await Promise.allSettled([
  loadUser(id), loadPosts(id), loadComments(id),
]);
const user = u.status === "fulfilled" ? u.value : fallbackUser;

// === 4. Stream errors — MUST register a listener ===
stream.on("error", (err) =&gt; log.error({ err }, "stream error"));
// Or use pipeline (propagates errors + closes streams)
await pipeline(src, transform, dst);   // rejects on any error

// === 5. EventEmitter errors — crash process if no listener ===
emitter.on("error", handle);           // always register

// === 6. AbortController — cancelable async ops ===
const ac = new AbortController();
setTimeout(() =&gt; ac.abort(), 5_000);
try {
  const res = await fetch(url, { signal: ac.signal });
} catch (err) {
  if (err.name === "AbortError") log.warn("timed out");
  else throw err;
}

// === 7. Top-level safety nets ===
process.on("uncaughtException",  (err) =&gt; { log.fatal({ err }, "uncaught"); gracefulExit(1); });
process.on("unhandledRejection", (err) =&gt; { log.fatal({ err }, "unhandled rejection"); gracefulExit(1); });

// === 8. Express 4 — wrap async handlers (needed because Express 4 doesn't auto-catch) ===
const asyncHandler = (fn) =&gt; (req, res, next) =&gt; Promise.resolve(fn(req, res, next)).catch(next);
app.get("/users/:id", asyncHandler(async (req, res) =&gt; {
  const user = await loadUser(req.params.id);   // throws propagate to next(err)
  res.json(user);
}));
// Express 5 handles this automatically — no wrapper needed.
</code></pre>
<p><strong>Key behaviors to internalize:</strong></p>
<ul>
  <li><strong>Forgotten <code>await</code></strong> — calling an async function without <code>await</code> creates a "floating promise"; if it rejects, you get an <code>unhandledRejection</code>. Enable ESLint rule <code>no-floating-promises</code> (TypeScript ESLint).</li>
  <li><strong>Stream <code>error</code> events</strong> — missing a listener <em>crashes the process</em>. Always register one, even if it's just a log.</li>
  <li><strong>Errors in <code>setTimeout</code>/<code>setInterval</code> callbacks</strong> — thrown errors become uncaught unless the callback is wrapped. Use <code>Promise</code>-based <code>setTimeout</code> from <code>timers/promises</code>.</li>
  <li><strong>Don't swallow at the bottom</strong> — "fail fast" beats "continue with bad state." An unhandled rejection should crash the process so orchestrator restarts it cleanly.</li>
  <li><strong>Preserve async stack traces</strong> — enable in DevTools; Node keeps them by default in recent versions.</li>
</ul>
<p><strong>Crash on uncaught?</strong> Node's official recommendation: yes. After an uncaught exception, process state is unreliable (open handles, half-completed DB operations). Log, gracefully close handles, then <code>process.exit(1)</code>. Let your orchestrator restart a clean process.</p>
'''

ANSWERS[50] = r'''
<p>Express middleware is a function <code>(req, res, next) =&gt; void</code> (or <code>(err, req, res, next) =&gt;</code> for errors) that participates in the request pipeline. Each can inspect/modify <code>req</code>/<code>res</code>, call <code>next()</code> to continue, call <code>next(err)</code> to jump to the error handler, or end the response to short-circuit.</p>
<pre><code>// === 1. Simple custom middleware ===
app.use((req, res, next) =&gt; {
  req.id = req.headers["x-request-id"] || crypto.randomUUID();
  res.setHeader("X-Request-Id", req.id);
  next();
});

// === 2. Middleware factory — pass options ===
function requireContentType(type) {
  return (req, res, next) =&gt; {
    if (!req.is(type)) return res.status(415).json({ error: "unsupported_media_type" });
    next();
  };
}
app.post("/upload", requireContentType("multipart/form-data"), uploader);

// === 3. Async middleware with error handling ===
//     Express 5 handles rejections; Express 4 needs a wrapper
function asyncMW(fn) {
  return (req, res, next) =&gt; Promise.resolve(fn(req, res, next)).catch(next);
}

app.use(asyncMW(async (req, res, next) =&gt; {
  const token = req.headers.authorization?.slice(7);
  if (token) req.user = await verifyJWT(token);
  next();
}));

// === 4. Timing middleware — onion-model response observation ===
app.use((req, res, next) =&gt; {
  const start = process.hrtime.bigint();
  res.on("finish", () =&gt; {
    const ms = Number(process.hrtime.bigint() - start) / 1e6;
    log.info({ method: req.method, url: req.url, status: res.statusCode, ms }, "req");
  });
  next();
});

// === 5. Error-handling middleware — MUST have 4 args ===
app.use((err, req, res, _next) =&gt; {
  const status = err.statusCode || 500;
  res.status(status).json({ error: { code: err.code, message: err.message } });
});

// === 6. Route-specific middleware composition ===
const auth = [authRequired, loadUser];
app.get("/me", ...auth, meHandler);

// === 7. Conditional middleware ===
const conditional = (cond, mw) =&gt; (req, res, next) =&gt;
  cond(req) ? mw(req, res, next) : next();

app.use(conditional(
  (req) =&gt; req.url.startsWith("/api"),
  require("express-rate-limit")({ windowMs: 60_000, limit: 100 }),
));
</code></pre>
<p><strong>Execution model:</strong></p>
<ul>
  <li>Middleware runs in registration order. <code>app.use(fn)</code> applies globally; <code>app.use(path, fn)</code> mounts at a prefix; <code>app.get(path, fn)</code> applies to specific routes.</li>
  <li>Must call <code>next()</code> or send a response. If you don't, the request hangs until the client times out.</li>
  <li><code>next(err)</code> jumps to the next error-handling middleware (4-arg). Regular middleware with <code>next()</code> skips error handlers.</li>
  <li><strong>Onion model</strong> — code before <code>next()</code> runs on the way in; code in <code>res.on("finish")</code> or after <code>await next()</code> (Koa-style) runs on the way out.</li>
</ul>
<p><strong>Common middleware to include in every API:</strong> <code>helmet</code> (security headers), <code>cors</code>, <code>express.json({ limit })</code>, <code>pino-http</code> (structured logging), <code>compression</code> (if not at proxy), rate limiter, request-ID assigner, then auth, then routes, then 404 catchall, then error handler.</p>
<p><strong>Testing middleware:</strong> call it directly with fake req/res objects (<code>supertest</code> for integration), or test in isolation with spies on <code>next</code>. Keep middleware small and single-purpose for easy testing.</p>
'''

ANSWERS[51] = r'''
<p><strong>Validation</strong> checks shape/type/range; <strong>sanitization</strong> removes or neutralizes hostile content (HTML/SQL/script). Validate <em>at the boundary</em> (every HTTP handler input) and sanitize <em>close to the sink</em> (HTML escape on render, parameterized queries on DB write).</p>
<ul>
  <li><strong>Schema libraries:</strong> <code>zod</code> (TS-first, inferred types), <code>joi</code>, <code>yup</code>, <code>ajv</code> (fastest — JSON Schema), <code>class-validator</code> (NestJS). Pick one per project.</li>
  <li><strong>Sanitizers:</strong> <code>sanitize-html</code> or <code>DOMPurify</code> (server via jsdom) for rich text; <code>validator</code> for normalizing emails/URLs; <strong>never</strong> hand-roll regex strippers.</li>
  <li><strong>SQL:</strong> parameterized queries (<code>pg</code>, Prisma, Knex) — never concatenate. <strong>NoSQL:</strong> strip <code>$</code>/<code>.</code> keys from user JSON to prevent operator injection.</li>
</ul>
<pre><code>// Zod middleware — single source of truth for types + runtime check
import { z } from "zod";
const CreateUser = z.object({
  email: z.string().email().toLowerCase().trim(),
  age: z.number().int().min(13).max(120),
  bio: z.string().max(2000).optional(),
});
const validate = (schema) =&gt; (req, res, next) =&gt; {
  const r = schema.safeParse(req.body);
  if (!r.success) return res.status(400).json({ errors: r.error.issues });
  req.body = r.data; // typed + coerced
  next();
};
app.post("/users", validate(CreateUser), (req, res) =&gt; { /* req.body is safe */ });</code></pre>
<p><strong>Don't trust anything client-side:</strong> re-validate everything server-side. Normalize (lowercase email, trim) before uniqueness checks. Return structured error codes, not free text, so clients can i18n messages.</p>
'''

ANSWERS[52] = r'''
<p><code>multipart/form-data</code> encodes file uploads as delimited chunks. Node's <code>http</code> module gives you a raw stream — you parse it with a library rather than hand-rolling.</p>
<table>
<thead><tr><th>Library</th><th>Strength</th><th>Use when</th></tr></thead>
<tbody>
  <tr><td><code>multer</code></td><td>Express-native, field rules, disk/memory</td><td>Standard Express uploads</td></tr>
  <tr><td><code>busboy</code></td><td>Low-level streaming, no buffering</td><td>Large files → stream directly to S3</td></tr>
  <tr><td><code>formidable</code></td><td>Good defaults, events-based</td><td>Framework-agnostic</td></tr>
  <tr><td><code>@fastify/multipart</code></td><td>Fastify-native</td><td>Fastify apps</td></tr>
</tbody>
</table>
<pre><code>// Streaming directly to S3 with busboy — never touches disk
import Busboy from "busboy";
import { S3Client, Upload } from "@aws-sdk/lib-storage";
const s3 = new S3Client({ region: "us-east-1" });
app.post("/upload", (req, res) =&gt; {
  const bb = Busboy({ headers: req.headers, limits: { fileSize: 100 * 1024 * 1024 } });
  const uploads = [];
  bb.on("file", (name, stream, info) =&gt; {
    const upload = new Upload({
      client: s3,
      params: { Bucket: "my-bucket", Key: `uploads/${Date.now()}-${info.filename}`, Body: stream },
    });
    uploads.push(upload.done());
  });
  bb.on("close", async () =&gt; {
    const results = await Promise.all(uploads);
    res.json({ files: results.map(r =&gt; r.Location) });
  });
  req.pipe(bb);
});</code></pre>
<p><strong>Production essentials:</strong> enforce <code>fileSize</code> and <code>files</code> limits, validate MIME by magic bytes (<code>file-type</code>) not just by header, scan for malware (ClamAV) if user-sourced, store metadata separately in DB, and <strong>prefer pre-signed S3 PUT URLs</strong> — the client uploads directly to S3, skipping your server entirely.</p>
'''

ANSWERS[53] = r'''
<p>Node's built-in <code>zlib</code> module provides gzip, deflate, and Brotli. For HTTP responses, <strong>let the reverse proxy (Nginx, Cloudflare) compress</strong> — it's faster and frees Node for application logic. Use <code>zlib</code> in Node for files, backups, API payloads, or S3 objects.</p>
<pre><code>import { createReadStream, createWriteStream } from "node:fs";
import { createGzip, createBrotliCompress, createGunzip } from "node:zlib";
import { pipeline } from "node:stream/promises";

// Gzip a file (fast, wide support)
await pipeline(
  createReadStream("report.csv"),
  createGzip({ level: 6 }),
  createWriteStream("report.csv.gz")
);

// Brotli for max compression (static assets, ~20% smaller than gzip)
await pipeline(
  createReadStream("app.js"),
  createBrotliCompress({ params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 } }),
  createWriteStream("app.js.br")
);

// Decompress
await pipeline(createReadStream("in.gz"), createGunzip(), createWriteStream("out"));</code></pre>
<ul>
  <li><strong>gzip:</strong> ubiquitous, level 1-9, default 6. Use for dynamic content.</li>
  <li><strong>Brotli:</strong> 15-25% better ratio than gzip, slower to compress, faster to decompress. Use for static assets pre-compressed at build time.</li>
  <li><strong>deflate:</strong> rarely used directly — gzip is deflate + checksum.</li>
  <li><strong>Express middleware:</strong> <code>compression</code> package for automatic response compression (but proxy-level is better).</li>
</ul>
<p><strong>Never compress already-compressed data</strong> (images, video, zip) — it wastes CPU. <strong>Avoid compressing below ~1 KB</strong> — headers eat the savings. For streaming (logs, events), set lower levels (1-3) to prioritize throughput.</p>
'''

ANSWERS[54] = r'''
<p>Both handle binary data, but fundamentally differ in <strong>eagerness</strong> and <strong>memory profile</strong>.</p>
<table>
<thead><tr><th>Aspect</th><th>Buffer</th><th>Stream</th></tr></thead>
<tbody>
  <tr><td>Memory</td><td>Entire data in RAM</td><td>Chunks flow through (highWaterMark)</td></tr>
  <tr><td>Latency</td><td>Wait for full load</td><td>Process first chunk immediately</td></tr>
  <tr><td>Scale</td><td>Limited by RAM (~2 GB max per Buffer)</td><td>Unlimited — process TB with MB of RAM</td></tr>
  <tr><td>API</td><td>Random access, slicing, encode/decode</td><td>Event-based or async iterator</td></tr>
  <tr><td>Use when</td><td>Small data (&lt; few MB), need full content (parse JSON, hash)</td><td>Large data, pipeline, network transfer</td></tr>
</tbody>
</table>
<pre><code>import { readFile, createReadStream } from "node:fs";
import { pipeline } from "node:stream/promises";
import { createGzip } from "node:zlib";

// Buffer — loads entire file into memory
const data = await readFile("small.json");
const parsed = JSON.parse(data); // need full content

// Stream — constant memory regardless of size
await pipeline(
  createReadStream("huge.log"),         // 100 GB file, no problem
  createGzip(),
  createWriteStream("huge.log.gz")
);</code></pre>
<p><strong>Convert between them:</strong> <code>stream.toArray()</code> or <code>Buffer.concat(await stream.toArray())</code> (stream → buffer, loads all); <code>Readable.from(buffer)</code> (buffer → stream). Buffer is actually a <code>Uint8Array</code> subclass since Node 4 — it's a typed array view over off-heap memory (allocated via <code>Buffer.allocUnsafe</code> uses a shared pool).</p>
<p><strong>Rule of thumb:</strong> if input size is bounded and small, Buffer is simpler. If it's user-uploaded or grows with usage, always stream — Buffer will OOM you in production.</p>
'''

ANSWERS[55] = r'''
<p>Containerize with a <strong>multi-stage Dockerfile</strong> (build with full toolchain, run with minimal image), <strong>non-root user</strong>, <strong>pinned base</strong>, and <strong>healthcheck</strong>. Orchestrate with Kubernetes, ECS, Cloud Run, or Fly.io.</p>
<pre><code># Multi-stage production Dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
# Non-root user (node user is built in)
USER node
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
COPY --from=build --chown=node:node /app/package.json ./
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD node -e "fetch('http://localhost:3000/health').then(r=&gt;process.exit(r.ok?0:1)).catch(()=&gt;process.exit(1))"
CMD ["node", "--enable-source-maps", "dist/server.js"]</code></pre>
<ul>
  <li><strong>Image size:</strong> alpine (~50 MB) or <code>distroless/nodejs</code> (no shell — safer). Avoid <code>node:latest</code>.</li>
  <li><strong>Layer caching:</strong> copy <code>package*.json</code> before source so <code>npm ci</code> cache survives code changes.</li>
  <li><strong>Signal handling:</strong> use <code>--init</code> or <code>tini</code> so SIGTERM reaches Node for graceful shutdown. In K8s, honor <code>preStop</code> hook.</li>
  <li><strong>Secrets:</strong> never bake into image — inject via env (K8s Secrets, AWS Secrets Manager CSI).</li>
  <li><strong>Don't <code>npm start</code>:</strong> exec Node directly so PID 1 is Node, not npm (which drops signals).</li>
</ul>
<p>Use <code>docker scout</code> or Trivy in CI to scan for CVEs. Sign images with Cosign for supply-chain integrity.</p>
'''

ANSWERS[56] = r'''
<p>Cloud deployment options span a managed-vs-control spectrum. Pick based on ops burden, cold-start tolerance, and connection patterns.</p>
<table>
<thead><tr><th>Platform</th><th>Model</th><th>Best for</th></tr></thead>
<tbody>
  <tr><td>AWS Lambda / Vercel Functions</td><td>FaaS</td><td>Bursty traffic, CRUD APIs, no long connections</td></tr>
  <tr><td>Cloudflare Workers / Deno Deploy</td><td>Edge runtime</td><td>Low-latency global, V8 isolates (no cold start)</td></tr>
  <tr><td>AWS App Runner / GCP Cloud Run / Fly.io</td><td>Container PaaS</td><td>Container, pay-per-request, scale to zero</td></tr>
  <tr><td>AWS ECS Fargate / GCP GKE Autopilot</td><td>Managed containers</td><td>Long-running, WebSocket, cron</td></tr>
  <tr><td>AWS EKS / self-managed K8s</td><td>Full control</td><td>Multi-service, sidecars, service mesh</td></tr>
  <tr><td>Render / Railway / Heroku</td><td>Git-push PaaS</td><td>Small teams, fast iteration</td></tr>
</tbody>
</table>
<p><strong>Typical pipeline:</strong> Git push → CI (lint, test, build image) → push to registry (ECR/GCR/GHCR) → deploy (Terraform, Pulumi, or platform CLI) → health check → traffic shift (blue-green or canary) → monitor.</p>
<pre><code># GitHub Actions → ECS Fargate (excerpt)
- name: Build and push
  run: |
    docker build -t $ECR_URL:$GITHUB_SHA .
    aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
    docker push $ECR_URL:$GITHUB_SHA
- name: Deploy
  run: |
    aws ecs update-service --cluster prod --service api \
      --force-new-deployment --task-definition api:$(new-rev)</code></pre>
<p><strong>Must-haves regardless of platform:</strong> HTTPS termination at edge (ALB, Cloud Load Balancer, CF), <code>/health</code> and <code>/ready</code> endpoints, log aggregation (CloudWatch, Datadog, Loki), metrics (Prometheus, CloudWatch), env-based config, secret rotation, autoscaling rules tied to CPU/RPS/queue depth. For Lambda specifically: use <strong>provisioned concurrency</strong> for latency-critical paths and <strong>connection pooling via RDS Proxy</strong>.</p>
'''

ANSWERS[57] = r'''
<p>CI/CD for Node.js revolves around fast, reproducible builds and safe deploys. The modern baseline uses GitHub Actions, GitLab CI, or CircleCI with OIDC (no long-lived cloud secrets) and caching.</p>
<ul>
  <li><strong>CI stages:</strong> install (cached) → lint → typecheck → unit + integration tests → build → Docker build → security scan → push artifact.</li>
  <li><strong>CD stages:</strong> deploy to dev → smoke tests → promote to staging → integration suite → canary to prod → full rollout → post-deploy checks.</li>
  <li><strong>Caching:</strong> cache <code>~/.npm</code> keyed by <code>package-lock.json</code>. Use <code>npm ci</code> (deterministic), not <code>npm install</code>.</li>
  <li><strong>Matrix:</strong> test against Node LTS + Current (22 + 24). Drop EOL versions promptly.</li>
  <li><strong>Security:</strong> <code>npm audit --audit-level=high</code>, Snyk/Dependabot, SBOM (CycloneDX), Trivy image scans, secret scanning (gitleaks), branch protection requires green CI.</li>
  <li><strong>Deploys:</strong> blue-green (two environments, flip ALB), canary (1% → 10% → 100% with automated rollback on error-rate SLO breach), feature flags (decouple deploy from release).</li>
  <li><strong>DB migrations:</strong> run <em>before</em> app deploy, must be backward-compatible with old app version. Never both-destructive-and-deployed in same release.</li>
</ul>
<pre><code># .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy: { matrix: { node: [22, 24] } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '${{ matrix.node }}', cache: 'npm' }
      - run: npm ci
      - run: npm run lint &amp;&amp; npm run typecheck
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v4</code></pre>
<p><strong>Make it fast:</strong> parallelize jobs, split large test suites (<code>jest --shard</code>), cache aggressively. A CI run &gt; 10 minutes gets ignored — aim for &lt; 5.</p>
'''

ANSWERS[58] = r'''
<p>Node exposes environment variables via <code>process.env</code>. In development, load from <code>.env</code> files; in production, inject via platform (K8s Secrets, ECS task def, App Runner config).</p>
<pre><code>// Node 20.6+ has built-in dotenv: node --env-file=.env server.js
// Or use dotenv package at startup
import "dotenv/config";

// ALWAYS validate env at boot — fail fast on typos, missing values
import { z } from "zod";
const Env = z.object({
  NODE_ENV: z.enum(["development", "staging", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
});
export const env = Env.parse(process.env); // typed, validated</code></pre>
<ul>
  <li><strong>Categories:</strong> config (PORT, LOG_LEVEL) — env vars fine. Secrets (API keys, DB passwords) — use a secret manager (AWS Secrets Manager, GCP Secret Manager, Vault, Doppler), not raw env.</li>
  <li><strong>.env hygiene:</strong> commit <code>.env.example</code> (schema), gitignore <code>.env</code>, rotate after any accidental commit.</li>
  <li><strong>Per-environment:</strong> <code>.env.local</code>, <code>.env.test</code>, <code>.env.production</code>. Don't rely on NODE_ENV alone — it's a string, not a config system.</li>
  <li><strong>Cloud-native:</strong> AWS ECS injects secrets as env at task start; K8s mounts from Secret; App Runner pulls from Secrets Manager by ARN.</li>
  <li><strong>Runtime reload:</strong> env vars are read once at boot. For dynamic config, fetch from config service (etcd, Consul, AppConfig) with a refresh interval.</li>
</ul>
<p><strong>Never</strong> log <code>process.env</code> — even a stray <code>console.log</code> in error paths can leak secrets to log aggregators. Redact in log transports.</p>
'''

ANSWERS[59] = r'''
<p>A CLI tool is a Node script with a <code>#!/usr/bin/env node</code> shebang, exposed via the <code>bin</code> field in <code>package.json</code> and installed globally (<code>npm i -g</code>) or via <code>npx</code>.</p>
<table>
<thead><tr><th>Library</th><th>Strength</th></tr></thead>
<tbody>
  <tr><td><code>commander</code></td><td>Lightweight, declarative, most popular</td></tr>
  <tr><td><code>yargs</code></td><td>Rich parsing, positional args, middleware</td></tr>
  <tr><td><code>oclif</code> (by Heroku/Salesforce)</td><td>Multi-command, plugins, auto-generated docs</td></tr>
  <tr><td><code>clipanion</code></td><td>TS-first, class-based (used by Yarn)</td></tr>
  <tr><td><code>ink</code></td><td>React-based interactive UIs (spinners, tables)</td></tr>
</tbody>
</table>
<pre><code>#!/usr/bin/env node
// bin/mytool.js
import { Command } from "commander";
import chalk from "chalk";
import ora from "ora";

const program = new Command();
program.name("mytool").version("1.0.0");

program
  .command("deploy &lt;env&gt;")
  .description("Deploy to environment")
  .option("-d, --dry-run", "simulate only")
  .action(async (environment, opts) =&gt; {
    const spinner = ora(`Deploying to ${environment}...`).start();
    try {
      if (opts.dryRun) spinner.info(chalk.yellow("Dry run — no changes"));
      else await deploy(environment);
      spinner.succeed(chalk.green("Deployed"));
    } catch (e) {
      spinner.fail(chalk.red(e.message));
      process.exit(1);
    }
  });

program.parseAsync();</code></pre>
<pre><code>// package.json
{
  "name": "mytool",
  "bin": { "mytool": "bin/mytool.js" },
  "type": "module",
  "engines": { "node": "&gt;=20" }
}</code></pre>
<p><strong>Polish:</strong> <code>chalk</code> for color, <code>ora</code> for spinners, <code>inquirer</code>/<code>prompts</code> for interactive input, <code>conf</code> for persistent user config, <code>update-notifier</code> for version nags. Set exit codes intentionally (0 success, 1 failure, 2+ semantic). Provide <code>--json</code> output for scripting. Publish to npm, or distribute as single binary with <code>pkg</code>/<code>nexe</code>/<code>node --experimental-sea-config</code>.</p>
'''

ANSWERS[60] = r'''
<p>Three strategies, ordered by scale: in-process cron → distributed job queue → managed cloud scheduler.</p>
<ul>
  <li><strong>In-process (<code>node-cron</code>):</strong> tiny apps, single instance. Breaks under horizontal scaling (every replica runs the job).</li>
  <li><strong>Distributed queue (BullMQ, Agenda, Temporal):</strong> Redis/Mongo-backed, leader election built in, retry/backoff, observability dashboards.</li>
  <li><strong>Cloud-native (EventBridge Scheduler, Cloud Scheduler, K8s CronJob):</strong> operates outside your app entirely — triggers HTTP/Lambda/Pub/Sub.</li>
</ul>
<pre><code>// BullMQ — repeatable job with retry and backoff
import { Queue, Worker } from "bullmq";
const connection = { host: "redis", port: 6379 };

const q = new Queue("reports", { connection });
await q.add(
  "daily-report",
  { tenantId: "*" },
  {
    repeat: { pattern: "0 3 * * *", tz: "Asia/Kolkata" }, // 3 AM IST daily
    attempts: 5,
    backoff: { type: "exponential", delay: 60_000 },
    removeOnComplete: 1000,
    removeOnFail: 100,
  }
);

// Worker — runs on any replica; BullMQ handles leader election via Redis locks
new Worker("reports", async (job) =&gt; {
  await generateReport(job.data);
}, { connection, concurrency: 4 });</code></pre>
<ul>
  <li><strong>Idempotency:</strong> a job may fire twice (at-least-once). Design with unique keys so duplicate runs are no-ops.</li>
  <li><strong>Timezones:</strong> always specify explicitly — server UTC vs user local is a classic bug.</li>
  <li><strong>Observability:</strong> emit metrics (duration, success/fail), alert on "job didn't run in N hours" (the silent-failure mode).</li>
  <li><strong>Don't use <code>setInterval</code></strong> for scheduling — drift, memory leaks on long uptimes, no persistence across restarts.</li>
</ul>
<p>For durable workflows with retries and human-in-the-loop steps, <strong>Temporal</strong> or <strong>Inngest</strong> beats ad-hoc cron.</p>
'''

ANSWERS[61] = r'''
<p>Pub/sub decouples <em>publishers</em> (emit events) from <em>subscribers</em> (react to events) via a broker. Compared to direct calls, it enables fan-out, async processing, and loose coupling.</p>
<table>
<thead><tr><th>Mechanism</th><th>Scope</th><th>Guarantees</th><th>Use when</th></tr></thead>
<tbody>
  <tr><td><code>EventEmitter</code></td><td>In-process, same JS VM</td><td>Synchronous, no persistence</td><td>Intra-module notifications</td></tr>
  <tr><td>Redis Pub/Sub</td><td>Cross-process, same datacenter</td><td>At-most-once, no replay</td><td>Chat broadcast, cache invalidation</td></tr>
  <tr><td>Redis Streams</td><td>Durable log</td><td>At-least-once, consumer groups, replay</td><td>Reliable event delivery</td></tr>
  <tr><td>NATS / NATS JetStream</td><td>Cloud-native messaging</td><td>Core: at-most-once; JetStream: at-least-once</td><td>Microservice events, low latency</td></tr>
  <tr><td>Kafka</td><td>Distributed log</td><td>At-least-once (exactly-once w/ txn), replay</td><td>Event sourcing, analytics pipelines</td></tr>
  <tr><td>AWS SNS + SQS</td><td>Managed fan-out</td><td>At-least-once, DLQ</td><td>Multi-service AWS-native</td></tr>
</tbody>
</table>
<pre><code>// Redis pub/sub — ephemeral broadcast
import { createClient } from "redis";
const pub = createClient(); const sub = pub.duplicate();
await Promise.all([pub.connect(), sub.connect()]);

await sub.subscribe("user:events", (msg) =&gt; {
  const event = JSON.parse(msg);
  console.log("got", event);
});

await pub.publish("user:events", JSON.stringify({ type: "signup", userId: "42" }));</code></pre>
<p><strong>Picking the right tool:</strong> Redis Pub/Sub is fire-and-forget — a disconnected subscriber misses messages. Use <strong>Redis Streams</strong> or <strong>Kafka</strong> when delivery must survive restarts. Reserve plain <code>EventEmitter</code> for intra-process decoupling — it breaks the moment you scale beyond one instance.</p>
'''

ANSWERS[62] = r'''
<p>A message queue is a durable buffer between producers and consumers that enables async processing, retries, rate-limiting, and peak smoothing. In Node, <strong>BullMQ</strong> (Redis) is the dominant choice for job queues; <strong>amqplib</strong> (RabbitMQ) and <strong>kafkajs</strong> for cross-service messaging.</p>
<pre><code>// BullMQ — typical async job
import { Queue, Worker, QueueEvents } from "bullmq";
const connection = { host: "redis", port: 6379 };

// Producer
const emails = new Queue("emails", { connection });
await emails.add(
  "welcome",
  { userId: "u123", to: "a@b.com" },
  {
    attempts: 5,
    backoff: { type: "exponential", delay: 2000 }, // 2s, 4s, 8s, 16s, 32s
    removeOnComplete: { age: 3600, count: 1000 },
    removeOnFail: { age: 24 * 3600 },
    jobId: "welcome:u123", // idempotency key — duplicate producers are no-ops
  }
);

// Consumer
new Worker("emails", async (job) =&gt; {
  await sendEmail(job.data);
}, { connection, concurrency: 20, limiter: { max: 100, duration: 1000 } });

// Observability
const ev = new QueueEvents("emails", { connection });
ev.on("failed", ({ jobId, failedReason }) =&gt; log.error({ jobId, failedReason }));</code></pre>
<ul>
  <li><strong>Idempotency:</strong> workers must handle duplicates (at-least-once delivery). Use <code>jobId</code> or a dedupe key stored in DB/Redis.</li>
  <li><strong>Retries + DLQ:</strong> exponential backoff with jitter; after N attempts, move to a dead-letter queue for human inspection.</li>
  <li><strong>Concurrency + rate limit:</strong> per-worker concurrency caps parallelism; BullMQ <code>limiter</code> throttles against external APIs.</li>
  <li><strong>Priorities:</strong> separate queues per tier (critical, normal, bulk) — beats priority fields for isolation.</li>
  <li><strong>Monitoring:</strong> queue depth (alert on growth), consumer lag, job duration p95, failed/dead jobs.</li>
</ul>
<p><strong>Don't roll your own</strong> with <code>setTimeout</code> arrays or DB polling — you'll rediscover every edge case (crashed workers, stuck jobs, duplicate runs) the hard way.</p>
'''

ANSWERS[63] = r'''
<p>RabbitMQ and Kafka solve different problems under the "messaging" umbrella. Pick based on delivery pattern, throughput, and replay needs.</p>
<table>
<thead><tr><th>Aspect</th><th>RabbitMQ</th><th>Kafka</th></tr></thead>
<tbody>
  <tr><td>Model</td><td>Broker (queues + exchanges)</td><td>Distributed log (topics + partitions)</td></tr>
  <tr><td>Consumer</td><td>Pull, broker tracks ack</td><td>Pull, consumer tracks offset</td></tr>
  <tr><td>Retention</td><td>Until consumed</td><td>Configurable (hours to forever)</td></tr>
  <tr><td>Throughput</td><td>Tens of thousands msg/s</td><td>Millions msg/s (per partition)</td></tr>
  <tr><td>Replay</td><td>No (message gone after ack)</td><td>Yes (seek to offset)</td></tr>
  <tr><td>Routing</td><td>Rich (topic, fanout, direct, headers)</td><td>Topic + partition only</td></tr>
  <tr><td>Use</td><td>Task queues, RPC, work distribution</td><td>Event streaming, analytics, CQRS</td></tr>
</tbody>
</table>
<pre><code>// RabbitMQ (amqplib) — work queue with ack
import amqp from "amqplib";
const conn = await amqp.connect("amqp://rabbit");
const ch = await conn.createConfirmChannel();
await ch.assertQueue("tasks", { durable: true });
ch.sendToQueue("tasks", Buffer.from(JSON.stringify({ id: 1 })), { persistent: true });

await ch.prefetch(10); // at most 10 in-flight per consumer
ch.consume("tasks", async (msg) =&gt; {
  try { await handle(JSON.parse(msg.content.toString())); ch.ack(msg); }
  catch (e) { ch.nack(msg, false, false); /* → DLX */ }
});</code></pre>
<pre><code>// Kafka (kafkajs) — event log with consumer groups
import { Kafka } from "kafkajs";
const kafka = new Kafka({ brokers: ["broker:9092"], clientId: "svc" });
const producer = kafka.producer();
await producer.connect();
await producer.send({ topic: "user.events", messages: [{ key: "u1", value: JSON.stringify(evt) }] });

const consumer = kafka.consumer({ groupId: "email-svc" });
await consumer.connect();
await consumer.subscribe({ topic: "user.events", fromBeginning: false });
await consumer.run({ eachMessage: async ({ message }) =&gt; handle(JSON.parse(message.value)) });</code></pre>
<p><strong>Choose RabbitMQ</strong> for distributed task queues (RPC, work distribution, complex routing). <strong>Choose Kafka</strong> when you need durable event history, multiple independent consumers replaying the same stream, or &gt; 100K msg/s. Many teams run both.</p>
'''

ANSWERS[64] = r'''
<p>Both are in-memory data stores, but differ sharply in features. Redis has largely displaced Memcached except for extreme-throughput pure-string-cache workloads.</p>
<table>
<thead><tr><th>Feature</th><th>Redis</th><th>Memcached</th></tr></thead>
<tbody>
  <tr><td>Data types</td><td>Strings, hashes, lists, sets, sorted sets, streams, HyperLogLog, geo, bitmaps, JSON (module)</td><td>Strings only</td></tr>
  <tr><td>Persistence</td><td>RDB snapshots + AOF log</td><td>None (pure cache)</td></tr>
  <tr><td>Replication</td><td>Master-replica, Sentinel, Cluster</td><td>Client-side sharding only</td></tr>
  <tr><td>Pub/Sub</td><td>Yes (Pub/Sub, Streams)</td><td>No</td></tr>
  <tr><td>Scripting</td><td>Lua (atomic)</td><td>No</td></tr>
  <tr><td>Transactions</td><td>MULTI/EXEC, WATCH (optimistic)</td><td>CAS token per-key</td></tr>
  <tr><td>Eviction</td><td>Configurable (LRU, LFU, TTL, random)</td><td>LRU only</td></tr>
  <tr><td>Memory efficiency</td><td>Good</td><td>Better for large small-string caches</td></tr>
</tbody>
</table>
<pre><code>// ioredis — Redis client (cluster-aware, pipelining)
import Redis from "ioredis";
const redis = new Redis(process.env.REDIS_URL);

// Cache-aside with TTL
const cached = await redis.get(`user:${id}`);
if (cached) return JSON.parse(cached);
const user = await db.user.findUnique({ where: { id } });
await redis.set(`user:${id}`, JSON.stringify(user), "EX", 300);
return user;

// Sorted set — leaderboard (not possible with Memcached)
await redis.zincrby("leaderboard", 1, `user:${id}`);
const top10 = await redis.zrevrange("leaderboard", 0, 9, "WITHSCORES");

// Distributed lock via Lua script (atomic)
const lock = `-- SET key val NX PX ms; atomic unlock via Lua check-and-del`;
await redis.set("lock:job", token, "NX", "PX", 30000);</code></pre>
<p><strong>Use Redis</strong> for anything beyond trivial caching — rate limits (sorted sets or Lua), sessions (hashes), queues (streams), pub/sub, locks. <strong>Pick Memcached</strong> only for massive simple-string caches where its multi-threaded model gives a throughput edge and you genuinely don't need any Redis feature.</p>
'''

ANSWERS[65] = r'''
<p>Caching strategies form a ladder from application-local to edge:</p>
<ol>
  <li><strong>Local in-process</strong> (<code>lru-cache</code>, <code>node-cache</code>) — nanosecond reads, but duplicated per instance and lost on restart. Good for config, compiled regexes, rarely-changing lookups.</li>
  <li><strong>Distributed cache</strong> (Redis, Memcached) — shared across instances, survives restarts. The workhorse.</li>
  <li><strong>Database query cache</strong> (Postgres, MySQL) — baked into DB, transparent but limited.</li>
  <li><strong>HTTP/CDN cache</strong> (Cloudflare, Fastly, Varnish) — cache at the edge via <code>Cache-Control</code> and <code>ETag</code>. Free scale for public data.</li>
</ol>
<p><strong>Patterns:</strong></p>
<ul>
  <li><strong>Cache-aside (lazy):</strong> app reads cache; on miss, fetches from DB and populates. Most common. Risk: thundering herd on cold cache → use singleflight (one fetch per key).</li>
  <li><strong>Read-through:</strong> cache layer fetches from DB itself on miss. Cleaner app code but tighter coupling.</li>
  <li><strong>Write-through:</strong> writes go to cache + DB synchronously. Keeps cache fresh but slower writes.</li>
  <li><strong>Write-behind:</strong> writes go to cache, flushed to DB async. Fast but risk of loss.</li>
  <li><strong>Refresh-ahead:</strong> background refresh before TTL expires. No user sees a cold miss.</li>
</ul>
<pre><code>// Cache-aside with singleflight (prevents thundering herd)
const inflight = new Map();
async function getUser(id) {
  const key = `user:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);
  if (inflight.has(key)) return inflight.get(key); // dedupe concurrent fetches
  const promise = (async () =&gt; {
    const user = await db.user.findUnique({ where: { id } });
    await redis.set(key, JSON.stringify(user), "EX", 300);
    inflight.delete(key);
    return user;
  })();
  inflight.set(key, promise);
  return promise;
}</code></pre>
<ul>
  <li><strong>TTL + jittered expiry</strong> prevents synchronized expiry storms (<code>ttl + random(0, ttl*0.1)</code>).</li>
  <li><strong>Invalidation:</strong> "one of the two hard problems." Prefer short TTLs + event-driven busts over perfect coherence.</li>
  <li><strong>Negative caching</strong> (cache "not found") prevents DB pounding for missing keys.</li>
  <li><strong>Key namespacing:</strong> <code>&lt;app&gt;:&lt;entity&gt;:&lt;id&gt;:&lt;ver&gt;</code> — bump version to mass-invalidate.</li>
</ul>
<p><strong>Measure cache hit rate</strong> — below 80% you're mostly adding latency.</p>
'''

ANSWERS[66] = r'''
<p><code>node:http2</code> supports HTTP/2 natively: binary framing, multiplexed streams over a single TCP connection, header compression (HPACK), and server push. In practice, <strong>terminate HTTP/2 at your reverse proxy</strong> (Nginx, Envoy, ALB) and speak HTTP/1.1 to Node — simpler ops, same user benefit.</p>
<pre><code>import http2 from "node:http2";
import fs from "node:fs";

const server = http2.createSecureServer({
  key: fs.readFileSync("key.pem"),
  cert: fs.readFileSync("cert.pem"),
  allowHTTP1: true, // fall back for older clients (ALPN)
});

server.on("stream", (stream, headers) =&gt; {
  const path = headers[":path"];
  stream.respond({
    ":status": 200,
    "content-type": "application/json",
    "cache-control": "max-age=60",
  });
  stream.end(JSON.stringify({ path }));
});

server.listen(8443);</code></pre>
<ul>
  <li><strong>Multiplexing:</strong> many requests over one TCP connection — eliminates head-of-line blocking that HTTP/1.1 had, reduces connection overhead.</li>
  <li><strong>HPACK header compression:</strong> big win for API-heavy apps with repeated headers (auth tokens, cookies).</li>
  <li><strong>Server Push</strong> is effectively dead (Chrome disabled it) — use <code>Link: rel=preload</code> hints instead.</li>
  <li><strong>Prior-knowledge h2c</strong> (plaintext) exists but is rarely worth the config complexity — most deployments use TLS-only h2.</li>
</ul>
<p><strong>When to use Node's http2 directly:</strong> edge services, gRPC (<code>@grpc/grpc-js</code> uses http2), realtime over h2 streams. Otherwise let Nginx/Envoy do ALPN, h2, and multiplexing — your Node app stays simpler on h1.1. Express 4 has no h2 support; Express 5 and Fastify work with <code>http2</code> via compat shims but expect gotchas. <strong>HTTP/3 (QUIC)</strong> is in Node as experimental <code>node:quic</code>; today still terminate at proxy.</p>
'''

ANSWERS[67] = r'''
<p>gRPC uses HTTP/2 + Protocol Buffers for typed, efficient RPC — far faster and smaller than JSON/REST, with strong schema contracts. In Node, use <strong><code>@grpc/grpc-js</code></strong> (pure JS, preferred) with <code>@grpc/proto-loader</code> (runtime) or <code>ts-proto</code>/<code>buf</code> (codegen).</p>
<pre><code>// user.proto
syntax = "proto3";
package user.v1;
service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);     // server streaming
}
message GetUserRequest { string id = 1; }
message User { string id = 1; string email = 2; }</code></pre>
<pre><code>// Server
import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
const pkg = grpc.loadPackageDefinition(protoLoader.loadSync("user.proto"));

const server = new grpc.Server({ "grpc.max_receive_message_length": 4 * 1024 * 1024 });
server.addService(pkg.user.v1.UserService.service, {
  GetUser: async (call, cb) =&gt; {
    const u = await db.user.findUnique({ where: { id: call.request.id } });
    if (!u) return cb({ code: grpc.status.NOT_FOUND, message: "user not found" });
    cb(null, u);
  },
  ListUsers: async (call) =&gt; {
    for await (const u of db.user.stream()) call.write(u);
    call.end();
  },
});
server.bindAsync("0.0.0.0:50051", grpc.ServerCredentials.createSsl(...), () =&gt; server.start());</code></pre>
<ul>
  <li><strong>Streaming modes:</strong> unary, server-stream, client-stream, bidirectional. Great for chat, telemetry, pagination.</li>
  <li><strong>Deadlines/cancellation:</strong> propagate across calls via metadata — essential for preventing cascading timeouts.</li>
  <li><strong>Interceptors</strong> (auth, logging, retry, tracing) replace middleware.</li>
  <li><strong>Reflection</strong> (<code>grpc-reflection</code>) lets tools like <code>grpcurl</code> and Postman introspect your API.</li>
  <li><strong>Browser:</strong> use gRPC-Web via Envoy proxy or <strong>Connect RPC</strong> (Buf's modern alternative that serves both gRPC and JSON).</li>
</ul>
<p><strong>Use gRPC</strong> for internal service-to-service at scale (~3× faster than JSON, strong schema evolution). <strong>Stick with REST/OpenAPI or tRPC/Connect</strong> for public/browser APIs.</p>
'''

ANSWERS[68] = r'''
<p>Serverless runs your code on-demand without managing servers — the platform handles provisioning, scaling, and billing-per-invocation. Trade control for operational simplicity.</p>
<table>
<thead><tr><th>Platform</th><th>Runtime</th><th>Cold start</th><th>Max duration</th></tr></thead>
<tbody>
  <tr><td>AWS Lambda</td><td>Full Node (Linux container)</td><td>100ms-1s (or provisioned)</td><td>15 min</td></tr>
  <tr><td>Vercel Functions</td><td>Node or Edge</td><td>~200ms / &lt;50ms</td><td>60s-5min</td></tr>
  <tr><td>Cloudflare Workers</td><td>V8 isolates (subset of Node APIs)</td><td>~0ms</td><td>30s CPU</td></tr>
  <tr><td>Deno Deploy</td><td>V8 isolates, Deno APIs</td><td>~0ms</td><td>10ms-30s</td></tr>
  <tr><td>GCP Cloud Functions / Run</td><td>Node container</td><td>Variable</td><td>60min (Run)</td></tr>
</tbody>
</table>
<pre><code>// AWS Lambda handler (Node 20.x runtime)
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
const s3 = new S3Client({}); // reuse across invocations (warm)

export const handler = async (event) =&gt; {
  const { bucket, key } = event;
  const obj = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
  return { statusCode: 200, body: await obj.Body.transformToString() };
};</code></pre>
<ul>
  <li><strong>Cold starts:</strong> minimize bundle (esbuild tree-shake), avoid heavy init, use <strong>provisioned concurrency</strong> (Lambda) for latency-critical paths, or move to edge runtimes.</li>
  <li><strong>Connections:</strong> never open a DB connection per request — either reuse across invocations (but connections can leak) or use <strong>RDS Proxy</strong> / <strong>PgBouncer</strong> / <strong>Neon serverless driver</strong>.</li>
  <li><strong>State:</strong> none — push to DynamoDB, S3, Redis. No local disk across invocations (except <code>/tmp</code>, ephemeral).</li>
  <li><strong>Limits:</strong> 15-min Lambda ceiling, 6 MB sync payload, 10 GB memory. Long jobs → Step Functions or Cloud Run jobs.</li>
  <li><strong>Frameworks:</strong> Serverless Framework, AWS SAM, AWS CDK, SST, OpenNext.</li>
</ul>
<p><strong>Good fit:</strong> HTTP APIs with bursty traffic, event-driven (S3, DynamoDB streams, SQS), cron-like tasks, glue code. <strong>Bad fit:</strong> WebSocket servers, connection pools, long-running jobs, stateful workloads — containers win there.</p>
'''

ANSWERS[69] = r'''
<p>Configuration layers from most-static to most-dynamic: defaults → env-specific files → environment variables → secret manager → remote config service. Validate at boot; fail fast on missing/malformed values.</p>
<table>
<thead><tr><th>Library</th><th>Strength</th></tr></thead>
<tbody>
  <tr><td><code>zod</code> / <code>envalid</code></td><td>TS-typed validation of <code>process.env</code></td></tr>
  <tr><td><code>node-config</code></td><td>Hierarchical (<code>default.json</code>, <code>production.json</code>, env overrides)</td></tr>
  <tr><td><code>convict</code> (Mozilla)</td><td>Schema + docs + coercion</td></tr>
  <tr><td><code>dotenv</code> / built-in <code>--env-file</code> (Node 20.6+)</td><td>Load <code>.env</code> locally</td></tr>
  <tr><td>AWS SSM / Secrets Manager, Doppler, HashiCorp Vault</td><td>Secret storage, rotation, audit</td></tr>
</tbody>
</table>
<pre><code>// Validated, typed config module — boot-time enforcement
import { z } from "zod";
import { SSMClient, GetParametersByPathCommand } from "@aws-sdk/client-ssm";

// Layer 1: env
const baseSchema = z.object({
  NODE_ENV: z.enum(["development", "staging", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  AWS_REGION: z.string(),
});

// Layer 2: fetch secrets from SSM at startup
async function loadSecrets() {
  const ssm = new SSMClient({});
  const out = await ssm.send(new GetParametersByPathCommand({
    Path: `/app/${process.env.NODE_ENV}/`, WithDecryption: true,
  }));
  return Object.fromEntries(out.Parameters.map(p =&gt; [
    p.Name.split("/").pop().toUpperCase(), p.Value,
  ]));
}

export async function loadConfig() {
  const secrets = await loadSecrets();
  return baseSchema.extend({
    JWT_SECRET: z.string().min(32),
    STRIPE_KEY: z.string(),
  }).parse({ ...process.env, ...secrets });
}</code></pre>
<ul>
  <li><strong>Never commit secrets</strong> — even to private repos. <code>.gitignore</code> <code>.env</code>; commit <code>.env.example</code>.</li>
  <li><strong>Separate config from code</strong> (12-factor). Same artifact deploys to every environment.</li>
  <li><strong>Dynamic config</strong> (feature flags, dynamic tuning) needs a dedicated service (Unleash, LaunchDarkly, AppConfig) — don't redeploy for a rate-limit bump.</li>
  <li><strong>Audit + rotation:</strong> centralize secrets; rotate on a schedule; track who accessed what.</li>
</ul>
<p><strong>Rule:</strong> config → env vars (plain text OK). Secrets → secret manager (encrypted, audited). Dynamic knobs → config service.</p>
'''

ANSWERS[70] = r'''
<p>Publishing an npm package is mostly polish: scaffolding is simple, but doing it <em>well</em> (types, exports, testing, CI) distinguishes maintained libraries.</p>
<pre><code>// package.json — modern dual-module, TS-first template
{
  "name": "@scope/my-lib",
  "version": "0.1.0",
  "description": "Short pitch",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    },
    "./package.json": "./package.json"
  },
  "files": ["dist", "README.md", "LICENSE"],
  "sideEffects": false,
  "engines": { "node": "&gt;=20" },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts --clean",
    "test": "vitest run",
    "release": "changeset publish"
  },
  "keywords": ["node", "util"],
  "repository": "github:scope/my-lib",
  "license": "MIT"
}</code></pre>
<ol>
  <li><strong>Write</strong> in TypeScript; ship both ESM + CJS with types (<code>tsup</code>, <code>unbuild</code>, or <code>tshy</code>).</li>
  <li><strong>Test</strong> on real Node versions in CI (matrix 20 + 22 + current).</li>
  <li><strong>Document</strong> (README with install, quickstart, API); include TSDoc comments for IDE tooltips.</li>
  <li><strong>Version</strong> with <code>changesets</code> (semantic commits + auto-generated changelog).</li>
  <li><strong>Publish:</strong> <code>npm login</code> → <code>npm publish --access public</code> (scoped packages are private by default). Use npm <code>provenance</code> (<code>--provenance</code>) for supply-chain attestation from GitHub Actions.</li>
  <li><strong>Maintain:</strong> respond to issues, deprecate with <code>npm deprecate</code>, never unpublish (use <code>deprecate</code> + version bump instead).</li>
</ol>
<p><strong>Anti-patterns:</strong> shipping <code>node_modules</code>, forgetting <code>files</code> (publishes everything), no types, breaking changes on patch versions, publishing from a developer machine (always from CI).</p>
'''

ANSWERS[71] = r'''
<p>Dependency management is about <strong>reproducibility</strong> (lockfile), <strong>security</strong> (audit + auto-update), and <strong>size</strong> (tree-shakeable, minimal).</p>
<table>
<thead><tr><th>Tool</th><th>Strength</th></tr></thead>
<tbody>
  <tr><td><code>npm</code></td><td>Ships with Node, fine for most</td></tr>
  <tr><td><code>pnpm</code></td><td>Fast, disk-efficient (content-addressed store), strict resolution</td></tr>
  <tr><td><code>yarn</code> (Berry)</td><td>Plug'n'Play, workspaces, good monorepo support</td></tr>
  <tr><td><code>bun</code></td><td>Fastest installer, works with npm registry</td></tr>
</tbody>
</table>
<ul>
  <li><strong>Pick one per repo</strong> — commit its lockfile (<code>package-lock.json</code>, <code>pnpm-lock.yaml</code>, <code>yarn.lock</code>). Use <code>npm ci</code> / <code>pnpm install --frozen-lockfile</code> in CI for deterministic installs.</li>
  <li><strong>Dependency types:</strong> <code>dependencies</code> (runtime), <code>devDependencies</code> (build/test), <code>peerDependencies</code> (consumer provides — e.g. React plugins), <code>optionalDependencies</code> (install failures ignored).</li>
  <li><strong>Audit:</strong> <code>npm audit --audit-level=high</code> in CI; fail on vulnerable direct deps. For transitive fixes beyond auto-update, use <code>overrides</code> (npm) / <code>resolutions</code> (yarn/pnpm) to force a safe version.</li>
  <li><strong>Auto-update:</strong> Renovate or Dependabot — weekly PRs, grouped by type, auto-merge patch-level after CI passes.</li>
  <li><strong>Minimal surface:</strong> reach for stdlib first (<code>node:crypto</code>, <code>node:fetch</code>, <code>node:test</code>); every dep is future CVE exposure. Check bundle impact with <code>bundlephobia</code> or <code>size-limit</code>.</li>
  <li><strong>Supply-chain:</strong> enable npm 2FA, prefer scoped orgs, use <code>npm ci --ignore-scripts</code> (postinstall scripts are a malware vector), review <code>package-lock.json</code> diffs on updates.</li>
</ul>
<pre><code>// Forcing a transitive fix via overrides (npm 8+)
{
  "overrides": {
    "left-pad": "1.3.0",
    "vulnerable-lib@&lt;2.0.0": "2.1.0"
  }
}</code></pre>
<p><strong>Monorepos:</strong> pnpm workspaces + Turborepo (or Nx, Moon) — share deps across packages, run only affected builds, hoist common tooling.</p>
'''

ANSWERS[72] = r'''
<p>SemVer is the <code>MAJOR.MINOR.PATCH</code> contract npm packages follow. It gives consumers a <em>prediction</em> of how safe an update is.</p>
<ul>
  <li><strong>PATCH</strong> (1.2.<strong>3</strong> → 1.2.4) — backward-compatible bugfix. Always safe.</li>
  <li><strong>MINOR</strong> (1.<strong>2</strong>.3 → 1.3.0) — backward-compatible new feature. Safe in principle.</li>
  <li><strong>MAJOR</strong> (<strong>1</strong>.2.3 → 2.0.0) — breaking change. Read the changelog.</li>
  <li><strong>Pre-release:</strong> <code>1.0.0-alpha.3</code>, <code>1.0.0-beta.1</code>, <code>1.0.0-rc.2</code> — install only with explicit tag, not auto-selected.</li>
  <li><strong>Build metadata:</strong> <code>1.0.0+build.42</code> — ignored by version comparison.</li>
</ul>
<table>
<thead><tr><th>Range</th><th>Matches</th><th>Example range → version</th></tr></thead>
<tbody>
  <tr><td><code>^1.2.3</code> (caret, npm default)</td><td>Minor + patch</td><td>1.2.3 to &lt; 2.0.0</td></tr>
  <tr><td><code>~1.2.3</code> (tilde)</td><td>Patch only</td><td>1.2.3 to &lt; 1.3.0</td></tr>
  <tr><td><code>1.2.3</code> (exact)</td><td>That version only</td><td>1.2.3</td></tr>
  <tr><td><code>&gt;=1.2.3 &lt;2.0.0</code></td><td>Explicit range</td><td>any within</td></tr>
  <tr><td><code>*</code> or <code>latest</code></td><td>Any</td><td>Avoid in production</td></tr>
</tbody>
</table>
<p><strong>Pre-1.0 caveat:</strong> versions <code>0.x.y</code> are explicitly "anything may break." Caret on <code>^0.2.3</code> only allows <code>0.2.x</code> (treats minor as breaking). Many libraries stay on 0.x forever — treat them cautiously.</p>
<p><strong>Publisher discipline:</strong> even a "minor" bump breaks users if you change defaults or type definitions. Use <code>changesets</code> or release automation tied to commit conventions to avoid human error. <strong>Lockfile always wins</strong> at install time — SemVer ranges only matter during updates.</p>
'''

ANSWERS[73] = r'''
<p>Node's single-threaded event loop handles thousands of concurrent requests naturally <em>because each request is mostly waiting on I/O</em>. True parallelism is only for CPU work.</p>
<ul>
  <li><strong>I/O-bound (the common case):</strong> each request blocks on DB/HTTP/disk. While waiting, the event loop handles other requests. A single Node process can serve 10k+ concurrent connections easily.</li>
  <li><strong>CPU-bound:</strong> a synchronous loop, crypto operation, or heavy JSON parse blocks <em>everyone</em>. Offload to <code>worker_threads</code> (shared memory) or <code>child_process.fork</code> (separate process).</li>
  <li><strong>Horizontal:</strong> run N worker processes with <code>cluster</code> or (better) the OS/orchestrator (PM2, systemd, K8s). Each process uses one core; N = core count.</li>
</ul>
<pre><code>// Parallel fan-out with concurrency cap — prevent overwhelming downstream
import pLimit from "p-limit";
const limit = pLimit(10); // at most 10 concurrent fetches

const results = await Promise.all(
  urls.map(url =&gt; limit(() =&gt; fetch(url).then(r =&gt; r.json())))
);

// Collect partial results (don't fail the whole batch)
const settled = await Promise.allSettled(
  urls.map(url =&gt; limit(() =&gt; fetch(url).then(r =&gt; r.json())))
);
const ok = settled.filter(r =&gt; r.status === "fulfilled").map(r =&gt; r.value);</code></pre>
<ul>
  <li><strong>Cap concurrency</strong> (<code>p-limit</code>, <code>p-queue</code>) — unbounded <code>Promise.all</code> on 10k items will open 10k sockets.</li>
  <li><strong>Connection pools</strong> (<code>pg</code>, <code>undici</code>) are the right layer to throttle at — set pool size to downstream capacity, not beyond.</li>
  <li><strong>Backpressure:</strong> for streams, respect <code>.write()</code> return value or use <code>pipeline</code>.</li>
  <li><strong>AbortController</strong> on every <code>fetch</code> and DB query to propagate client disconnects — prevents "zombie work."</li>
  <li><strong>Event loop utilization</strong> (<code>perf_hooks.performance.eventLoopUtilization()</code>) &gt; 0.8 means you're CPU-saturated — add more processes or move work off the main thread.</li>
</ul>
<p>"Handling concurrent requests" is mostly about <em>not accidentally blocking</em> the event loop, not about spawning threads per request.</p>
'''

ANSWERS[74] = r'''
<p>Unit tests exercise a single function or class in isolation, fast (&lt; 100ms each), deterministic, no I/O. They're the foundation of the testing pyramid.</p>
<pre><code>// Vitest — same API as Jest, faster, native ESM + TS
// src/cart.ts
export function total(items: Array&lt;{ price: number; qty: number }&gt;, discount = 0) {
  if (discount &lt; 0 || discount &gt; 1) throw new RangeError("discount must be 0..1");
  const sub = items.reduce((s, i) =&gt; s + i.price * i.qty, 0);
  return Math.round(sub * (1 - discount) * 100) / 100;
}

// cart.test.ts
import { describe, it, expect } from "vitest";
import { total } from "./cart";

describe("total", () =&gt; {
  it("sums items", () =&gt; {
    expect(total([{ price: 10, qty: 2 }, { price: 5, qty: 1 }])).toBe(25);
  });
  it("applies discount", () =&gt; {
    expect(total([{ price: 100, qty: 1 }], 0.2)).toBe(80);
  });
  it("rejects invalid discount", () =&gt; {
    expect(() =&gt; total([], 1.5)).toThrow(RangeError);
  });
  it("handles empty cart", () =&gt; {
    expect(total([])).toBe(0);
  });
});</code></pre>
<ul>
  <li><strong>AAA pattern:</strong> Arrange inputs → Act (call SUT) → Assert result.</li>
  <li><strong>One assertion per concept</strong> — if the test name has "and" in it, it's probably two tests.</li>
  <li><strong>Table-driven</strong> (<code>it.each</code>) for parametric coverage.</li>
  <li><strong>Edge cases:</strong> empty, null, boundary values, negative, very large, Unicode, timezone edges.</li>
  <li><strong>Test behavior, not implementation:</strong> don't assert on internal method calls — rewrite-proof by testing output.</li>
  <li><strong>Speed:</strong> no DB, no network, no filesystem (except tmp). Mock at the boundary (repo, HTTP client).</li>
  <li><strong>Coverage:</strong> aim for 80%+ lines + branches, but <strong>don't chase numbers</strong> — critical paths need 100%, trivial getters need nothing.</li>
</ul>
<p><strong>TDD</strong> (red → green → refactor) is a great tool for tricky algorithms. For glue code, write tests alongside — dogma helps no one.</p>
'''

ANSWERS[75] = r'''
<p>The Node testing ecosystem is mature — pick based on ecosystem compatibility and DX.</p>
<table>
<thead><tr><th>Framework</th><th>Strengths</th><th>Watchouts</th></tr></thead>
<tbody>
  <tr><td><strong>Vitest</strong></td><td>Jest-compatible API, native ESM + TS, fast (Vite-powered), great watch mode, workspace support</td><td>Newer ecosystem than Jest</td></tr>
  <tr><td><strong>Jest</strong></td><td>Most popular, massive plugin ecosystem, snapshot testing, mocking built in</td><td>Slow ESM support, heavy config, CJS-centric</td></tr>
  <tr><td><strong><code>node:test</code></strong> (built-in)</td><td>Zero deps, ships with Node 18+, TAP output, native test runner, supports <code>describe/it</code></td><td>No snapshot, fewer matchers, smaller community</td></tr>
  <tr><td><strong>Mocha + Chai + Sinon</strong></td><td>Mature, flexible, BDD style</td><td>Three packages to learn, slower to evolve</td></tr>
  <tr><td><strong>AVA</strong></td><td>Runs tests in parallel, minimal API</td><td>Less mainstream, awkward async patterns</td></tr>
  <tr><td><strong>Tap / Tape</strong></td><td>TAP output, simple</td><td>Barebones, less polished</td></tr>
</tbody>
</table>
<pre><code>// node:test — no install needed, Node 20+
import test from "node:test";
import assert from "node:assert/strict";
import { total } from "./cart.js";

test("total sums items", () =&gt; {
  assert.equal(total([{ price: 10, qty: 2 }]), 20);
});

test("total group", async (t) =&gt; {
  await t.test("applies discount", () =&gt; {
    assert.equal(total([{ price: 100, qty: 1 }], 0.2), 80);
  });
  await t.test("rejects bad discount", () =&gt; {
    assert.throws(() =&gt; total([], 1.5), RangeError);
  });
});
// Run: node --test --test-reporter=spec</code></pre>
<p><strong>Recommendations:</strong></p>
<ul>
  <li><strong>New TS/ESM project:</strong> Vitest — fastest, best DX.</li>
  <li><strong>Existing Jest codebase:</strong> stay with Jest or migrate to Vitest (API-compatible).</li>
  <li><strong>Zero-dep libraries:</strong> <code>node:test</code> — nothing to install, works everywhere.</li>
  <li><strong>Legacy Node / Mocha shops:</strong> keep Mocha — no need to thrash.</li>
</ul>
<p>Pair any of these with <strong>supertest</strong> (HTTP integration), <strong>testcontainers</strong> (real DBs), <strong>MSW</strong> (HTTP mocks), <strong>Playwright</strong> (E2E browser).</p>
'''

ANSWERS[76] = r'''
<p>Integration tests exercise multiple layers together — typically HTTP → controller → service → real database. Slower than unit tests (seconds each), but catch wiring bugs unit tests miss.</p>
<pre><code>// Integration test with supertest + testcontainers (real Postgres)
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import request from "supertest";
import { PostgreSqlContainer } from "@testcontainers/postgresql";
import { createApp } from "../src/app.js";
import { createPool, runMigrations } from "../src/db.js";

let container, app, pool;

beforeAll(async () =&gt; {
  container = await new PostgreSqlContainer("postgres:16-alpine").start();
  pool = createPool({ connectionString: container.getConnectionUri() });
  await runMigrations(pool);
  app = createApp({ pool });
}, 60_000);

afterAll(async () =&gt; {
  await pool.end();
  await container.stop();
});

describe("POST /users", () =&gt; {
  it("creates a user and returns 201", async () =&gt; {
    const res = await request(app)
      .post("/users")
      .send({ email: "a@b.com", password: "supersecret123" });
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ id: expect.any(String), email: "a@b.com" });
    expect(res.body.password).toBeUndefined(); // must not leak hash
  });

  it("rejects duplicate email with 409", async () =&gt; {
    await request(app).post("/users").send({ email: "dup@x.com", password: "x".repeat(12) });
    const res = await request(app).post("/users").send({ email: "dup@x.com", password: "x".repeat(12) });
    expect(res.status).toBe(409);
  });
});</code></pre>
<ul>
  <li><strong>Use real dependencies</strong> (Postgres, Redis) via <strong>testcontainers</strong> — Docker-spin them per suite. Catches schema drift, index issues, SQL dialect gotchas that mocks hide.</li>
  <li><strong>Isolation:</strong> each test gets a transaction it rolls back, OR each test file gets a fresh schema. Avoid shared state leakage.</li>
  <li><strong>Supertest</strong> wraps Express/Fastify apps without binding a port — fast, deterministic.</li>
  <li><strong>Seeds:</strong> fixture factories (<code>@mswjs/data</code>, <code>fishery</code>) over raw inserts — readable, composable.</li>
  <li><strong>Network mocks:</strong> <strong>MSW</strong> (Mock Service Worker) for outbound HTTP — intercepts at fetch level, matches requests declaratively.</li>
  <li><strong>Parallel:</strong> per-test-file DB schema or DB name lets you run Vitest with workers.</li>
</ul>
<p><strong>E2E</strong> (Playwright, Cypress) adds the browser layer — reserve for a handful of critical flows (login, checkout). Integration tests are the sweet spot for most API coverage.</p>
'''

ANSWERS[77] = r'''
<p>Mocking replaces real dependencies (DB, HTTP, time, randomness) with controllable stand-ins so tests stay fast, deterministic, and isolated.</p>
<table>
<thead><tr><th>Type</th><th>Behavior</th></tr></thead>
<tbody>
  <tr><td><strong>Stub</strong></td><td>Returns hardcoded values</td></tr>
  <tr><td><strong>Spy</strong></td><td>Wraps real function; records calls + args</td></tr>
  <tr><td><strong>Mock</strong></td><td>Spy + verifiable expectations</td></tr>
  <tr><td><strong>Fake</strong></td><td>Working implementation (in-memory DB)</td></tr>
</tbody>
</table>
<pre><code>// Vitest (same API for Jest: jest.*, jest.fn())
import { describe, it, expect, vi, beforeEach } from "vitest";
import { sendWelcome } from "../src/services/email";
import * as mailer from "../src/lib/mailer";

describe("sendWelcome", () =&gt; {
  beforeEach(() =&gt; vi.restoreAllMocks());

  it("calls mailer with formatted payload", async () =&gt; {
    const spy = vi.spyOn(mailer, "send").mockResolvedValue({ id: "m_1" });
    const result = await sendWelcome({ email: "a@b.com", name: "Ada" });
    expect(spy).toHaveBeenCalledOnce();
    expect(spy).toHaveBeenCalledWith(expect.objectContaining({
      to: "a@b.com", subject: expect.stringContaining("Welcome") }));
    expect(result.id).toBe("m_1");
  });

  it("retries on transient failure", async () =&gt; {
    const spy = vi.spyOn(mailer, "send")
      .mockRejectedValueOnce(new Error("ECONNRESET"))
      .mockResolvedValueOnce({ id: "m_2" });
    const result = await sendWelcome({ email: "x@y.com" });
    expect(spy).toHaveBeenCalledTimes(2);
    expect(result.id).toBe("m_2");
  });
});

// Time control — deterministic date-based logic
vi.useFakeTimers({ now: new Date("2026-01-15T10:00:00Z") });
vi.advanceTimersByTime(5 * 60_000); // jump 5 minutes
vi.useRealTimers();</code></pre>
<ul>
  <li><strong>Mock at the boundary:</strong> replace HTTP clients, DB drivers, file system — not your own domain logic.</li>
  <li><strong>Don't over-mock:</strong> if you're mocking 5 things for one test, you're testing the mocks, not behavior. Reach for integration tests.</li>
  <li><strong>MSW over nock:</strong> for HTTP, MSW intercepts at fetch level — same mocks work in tests and Storybook/dev.</li>
  <li><strong>Module mocks:</strong> <code>vi.mock("../db")</code> replaces an entire module — handy for ORMs, but brittle.</li>
  <li><strong>Verify interactions sparingly:</strong> assert on <em>outcomes</em>; verify calls only when the call itself is the outcome (like "sent an email").</li>
</ul>
<p><strong>Golden rule:</strong> mocks hide real failures. Every mock is technical debt — prefer fakes (in-memory repos) or real containers when feasible.</p>
'''

ANSWERS[78] = r'''
<p>Coverage reports which code lines/branches executed during tests — useful to <em>find gaps</em>, misleading as a quality score. Modern Node uses <strong>c8</strong> (V8-native, no instrumentation) or built-in Jest/Vitest coverage.</p>
<pre><code>// Vitest — coverage built in, uses v8 by default
// vitest.config.ts
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",              // or "istanbul" for detailed branch tracking
      reporter: ["text", "html", "lcov", "json-summary"],
      include: ["src/**/*.{ts,js}"],
      exclude: ["src/**/*.test.ts", "src/types/**", "src/main.ts"],
      thresholds: {
        lines: 85, branches: 80, functions: 85, statements: 85,
        // Per-file minimums — catches untested new modules
        perFile: true,
      },
    },
  },
});

// Run: vitest run --coverage</code></pre>
<pre><code># node:test + c8 — no config overhead
c8 --reporter=lcov --reporter=text --lines 80 --branches 75 node --test

# Jest has it built in
jest --coverage --coverageThreshold='{"global":{"lines":85,"branches":80}}'</code></pre>
<ul>
  <li><strong>Metrics:</strong> lines (did this line execute?), branches (did both sides of <code>if</code> run?), functions (was it called?), statements (fine-grained lines).</li>
  <li><strong>Report formats:</strong> <code>text</code> (CI log), <code>html</code> (local inspection), <code>lcov</code> (Codecov, Coveralls), <code>json-summary</code> (scripts).</li>
  <li><strong>Providers:</strong> <code>v8</code> (fast, no instrumentation, less precise branches), <code>istanbul</code> (more precise, slower, AST-instrumented).</li>
  <li><strong>Thresholds in CI:</strong> fail the build if coverage drops. Set <strong>per-file</strong> too, or new untested files slip through.</li>
  <li><strong>Exclusions:</strong> generated code, types, main bootstrap, migrations — put them in <code>exclude</code>.</li>
  <li><strong>Mutation testing</strong> (<code>stryker</code>) is the better quality metric — flips operators and checks if tests catch it.</li>
</ul>
<p><strong>100% coverage ≠ bug-free.</strong> Coverage tells you what you tested, not how well. A useless assertion on every line hits 100%. Use coverage diff tools (Codecov) to guard <em>trends</em>, not absolute numbers.</p>
'''

ANSWERS[79] = r'''
<p>The <code>debug</code> module is a tiny namespaced logger widely used by Node libraries (Express, Mocha, Passport). Logs are off by default and switched on via the <code>DEBUG</code> env var — zero overhead when disabled.</p>
<pre><code>// src/lib/payments.ts
import debug from "debug";
const log = debug("myapp:payments");        // namespace
const logHttp = debug("myapp:payments:http");

export async function charge(userId, amount) {
  log("charge start user=%s amount=%d", userId, amount);
  logHttp("POST /v1/charges");
  try {
    const result = await stripe.charges.create({ amount });
    log("charge ok id=%s", result.id);
    return result;
  } catch (e) {
    log("charge failed %o", e);   // %o for object dump
    throw e;
  }
}</code></pre>
<pre><code># Turn on at runtime — no code changes
DEBUG=myapp:* node server.js          # all myapp namespaces
DEBUG=myapp:payments:* node server.js # only payments
DEBUG=express:router,myapp:* node ... # mix libraries
DEBUG=-myapp:health,myapp:*  node ... # everything except health

# Useful when debugging dependencies
DEBUG=express:*      # Express internals
DEBUG=nodemon        # Nodemon actions
DEBUG=mongodb:*      # Mongo driver</code></pre>
<ul>
  <li><strong>Namespaces</strong> are colon-separated conventionally: <code>app:feature:subfeature</code>.</li>
  <li><strong>Printf-style</strong> formatters: <code>%s</code>, <code>%d</code>, <code>%j</code> (JSON), <code>%o</code> (util.inspect).</li>
  <li><strong>Per-namespace colors</strong> in terminals aid visual scanning.</li>
  <li><strong>Zero cost when disabled</strong> — the check is a single boolean lookup.</li>
</ul>
<p><strong>debug vs pino/winston:</strong></p>
<ul>
  <li><strong><code>debug</code>:</strong> developer diagnostics, library internals, turned on ad-hoc during troubleshooting.</li>
  <li><strong><code>pino</code>:</strong> structured production logging — JSON, levels (info/warn/error), shipped to aggregators. Always on.</li>
</ul>
<p>Use both: <code>debug</code> for "help me trace this locally," <code>pino</code> for "record what happened in prod."</p>
'''

ANSWERS[80] = r'''
<p>Dependency Injection (DI) means a class doesn't construct its dependencies — they're <em>given</em> to it. The benefit: swap real DB/HTTP/clock for fakes in tests, and make wiring explicit.</p>
<table>
<thead><tr><th>Approach</th><th>How it works</th></tr></thead>
<tbody>
  <tr><td><strong>Manual</strong></td><td>Pass dependencies to constructor/function. Tiny apps.</td></tr>
  <tr><td><strong>Factory functions</strong></td><td>Higher-order fn returns service with deps baked in.</td></tr>
  <tr><td><strong><code>awilix</code></strong></td><td>Container-based, TS-friendly, no decorators needed.</td></tr>
  <tr><td><strong><code>tsyringe</code> / <code>InversifyJS</code></strong></td><td>Decorator-based, reflect-metadata.</td></tr>
  <tr><td><strong>NestJS DI</strong></td><td>Opinionated framework with modules, providers, scopes.</td></tr>
</tbody>
</table>
<pre><code>// Manual DI — zero dependencies, maximum clarity
class UserService {
  constructor(
    private readonly users: UserRepo,      // interface
    private readonly mailer: Mailer,
    private readonly clock: () =&gt; Date = () =&gt; new Date(),
  ) {}

  async signup(email: string) {
    const user = await this.users.create({ email, createdAt: this.clock() });
    await this.mailer.send({ to: email, template: "welcome" });
    return user;
  }
}

// Production wiring
const svc = new UserService(new PgUserRepo(pool), new SesMailer(ses));

// Test wiring — fakes in, control time
const svc = new UserService(
  new InMemoryUserRepo(),
  { send: vi.fn() },
  () =&gt; new Date("2026-01-01"),
);</code></pre>
<pre><code>// awilix — DI container for larger apps
import { createContainer, asClass, asValue } from "awilix";
const c = createContainer();
c.register({
  pool:       asValue(pgPool),
  userRepo:   asClass(PgUserRepo).singleton(),
  mailer:     asClass(SesMailer).singleton(),
  userService: asClass(UserService).scoped(),   // new per request
});
// c.resolve("userService") — awilix auto-wires by param names
app.use((req, _res, next) =&gt; { req.scope = c.createScope(); next(); });</code></pre>
<ul>
  <li><strong>Inject interfaces, not concrete classes</strong> — enables swapping and testing.</li>
  <li><strong>Scopes:</strong> singleton (shared), request-scoped (per HTTP request, carries correlation ID), transient (new every time).</li>
  <li><strong>Avoid service locator</strong> — global <code>container.get("x")</code> inside methods hides deps; always inject at construction.</li>
</ul>
<p><strong>Don't over-engineer:</strong> for small apps, plain constructor injection is the cleanest DI. Reach for a container only when you have many services, request-scoped state, or a team that benefits from explicit structure (NestJS being the popular packaged answer).</p>
'''

ANSWERS[81] = r'''
<p>Validate data at every trust boundary: HTTP input, cross-service messages, file uploads, DB round-trips (defensive decoding). Choose one schema library per project and reuse schemas across API contract, DB serialization, and forms.</p>
<table>
<thead><tr><th>Library</th><th>Strengths</th></tr></thead>
<tbody>
  <tr><td><code>zod</code></td><td>TS-first, type inference, composable, best DX</td></tr>
  <tr><td><code>joi</code></td><td>Mature, rich validators, JS-first</td></tr>
  <tr><td><code>yup</code></td><td>Lightweight, familiar for Formik users</td></tr>
  <tr><td><code>ajv</code></td><td>Fastest (compiles JSON Schema), OpenAPI-friendly</td></tr>
  <tr><td><code>class-validator</code></td><td>Decorator-based, NestJS default</td></tr>
  <tr><td><code>valibot</code></td><td>Modular, tiny (&lt; 10% of Zod bundle)</td></tr>
</tbody>
</table>
<pre><code>// Zod — single schema, types + runtime guard + OpenAPI docs
import { z } from "zod";
const Role = z.enum(["admin", "editor", "viewer"]);

const CreateUser = z.object({
  email: z.string().email().trim().toLowerCase(),
  password: z.string().min(12).regex(/[A-Z]/).regex(/[0-9]/),
  age: z.coerce.number().int().min(13).max(120),
  role: Role.default("viewer"),
  profile: z.object({
    name: z.string().min(1).max(100),
    website: z.string().url().optional(),
  }),
}).strict(); // reject unknown keys

type CreateUser = z.infer&lt;typeof CreateUser&gt;;  // TS type for free

// Middleware
const validate = (schema) =&gt; (req, res, next) =&gt; {
  const r = schema.safeParse(req.body);
  if (!r.success) {
    return res.status(400).json({
      error: "VALIDATION_ERROR",
      issues: r.error.issues.map(i =&gt; ({
        path: i.path.join("."), code: i.code, message: i.message,
      })),
    });
  }
  req.body = r.data;
  next();
};

app.post("/users", validate(CreateUser), handler);</code></pre>
<ul>
  <li><strong>Validate at the boundary, not deep in the code:</strong> by the time data reaches your service layer, it must already be trustworthy.</li>
  <li><strong>Sanitize separately from validation:</strong> validation confirms shape; <code>sanitize-html</code>/<code>DOMPurify</code> neutralizes hostile HTML. For SQL, parameterize (Prisma/Knex) — don't "sanitize strings."</li>
  <li><strong>Coerce, don't reject:</strong> <code>z.coerce.number()</code>, <code>.trim()</code>, <code>.toLowerCase()</code> — repair input when reasonable, reject when not.</li>
  <li><strong>Reuse schemas:</strong> same Zod schema can power tRPC, OpenAPI doc gen (<code>zod-to-openapi</code>), and frontend form libraries (<code>react-hook-form</code> + <code>zodResolver</code>).</li>
  <li><strong>Return structured errors</strong> (field path, code, message) so clients can i18n.</li>
</ul>
<p><strong>Server is the only trust boundary that matters</strong> — client-side validation is UX, not security. Always re-validate server-side.</p>
'''

ANSWERS[82] = r'''
<p>Joi has a fluent chainable API with rich built-in validators. Common in Express + non-TS codebases. Pairs well with <code>celebrate</code> (Joi as Express middleware).</p>
<pre><code>import Joi from "joi";

// Full user registration schema
const registrationSchema = Joi.object({
  email: Joi.string().email({ tlds: { allow: false } }).required(),
  password: Joi.string().min(12).max(128)
    .pattern(/[A-Z]/, "uppercase letter")
    .pattern(/[0-9]/, "digit")
    .pattern(/[^A-Za-z0-9]/, "symbol")
    .required(),
  confirmPassword: Joi.any().valid(Joi.ref("password")).required()
    .messages({ "any.only": "passwords must match" }),
  age: Joi.number().integer().min(13).max(120).required(),
  phone: Joi.string().pattern(/^\+[1-9]\d{7,14}$/).optional(),
  role: Joi.string().valid("admin", "editor", "viewer").default("viewer"),
  address: Joi.object({
    line1: Joi.string().max(200).required(),
    country: Joi.string().length(2).uppercase().required(),
    zip: Joi.when("country", {
      is: "US",
      then: Joi.string().pattern(/^\d{5}(-\d{4})?$/).required(),
      otherwise: Joi.string().max(20).optional(),
    }),
  }).required(),
  tags: Joi.array().items(Joi.string().min(1).max(30)).max(10).unique(),
}).options({ abortEarly: false, stripUnknown: true });

// Express middleware
const validate = (schema) =&gt; (req, res, next) =&gt; {
  const { value, error } = schema.validate(req.body);
  if (error) {
    return res.status(400).json({
      error: "VALIDATION_ERROR",
      details: error.details.map(d =&gt; ({ path: d.path.join("."), message: d.message })),
    });
  }
  req.body = value;
  next();
};

app.post("/register", validate(registrationSchema), async (req, res) =&gt; {
  const user = await createUser(req.body);
  res.status(201).json(user);
});

// Custom validator — reusable domain rule
const phoneE164 = Joi.extend((joi) =&gt; ({
  type: "e164",
  base: joi.string(),
  validate(value, helpers) {
    if (!/^\+[1-9]\d{7,14}$/.test(value)) return { value, errors: helpers.error("e164.invalid") };
  },
  messages: { "e164.invalid": "must be E.164 format (+countrycode...)" },
}));</code></pre>
<p><strong>Key Joi features:</strong> <code>Joi.ref</code> (cross-field rules), <code>Joi.when</code> (conditional), <code>.concat</code> (schema composition), <code>.extend</code> (custom types), <code>abortEarly: false</code> (collect all errors), <code>stripUnknown</code> (drop unexpected keys). In TS codebases, prefer Zod for the free type inference; in JS or legacy codebases Joi remains excellent.</p>
'''

ANSWERS[83] = r'''
<p>Inversion of Control (IoC) is the general principle: a component <em>doesn't control</em> its own flow or dependencies — the framework/runtime does. DI is one form; event-driven callbacks and frameworks calling your code ("Hollywood principle: don't call us, we call you") are others.</p>
<ul>
  <li><strong>Traditional code:</strong> your <code>main()</code> creates objects, wires them, runs the loop.</li>
  <li><strong>IoC:</strong> a framework does the wiring, lifecycle, and invocation — you provide components. Express, NestJS, Fastify are all IoC containers to varying degrees.</li>
</ul>
<pre><code>// Express already uses IoC: you register handlers; it invokes them
app.get("/users/:id", userController.get);  // framework calls your function

// NestJS — full IoC container: decorators declare wiring
import { Injectable, Module, Controller, Get, Param } from "@nestjs/common";

@Injectable()
class UserRepo {
  find(id: string) { /* ... */ }
}

@Injectable()
class UserService {
  constructor(private readonly repo: UserRepo) {}          // injected
  get(id: string) { return this.repo.find(id); }
}

@Controller("users")
class UserController {
  constructor(private readonly service: UserService) {}    // injected
  @Get(":id") get(@Param("id") id: string) { return this.service.get(id); }
}

@Module({
  providers: [UserRepo, UserService],
  controllers: [UserController],
})
export class AppModule {}

// Bootstrapper — Nest builds the object graph and serves
const app = await NestFactory.create(AppModule);
await app.listen(3000);</code></pre>
<pre><code>// Plain TS IoC with awilix — same idea, no decorators
import { createContainer, asClass } from "awilix";
const c = createContainer();
c.register({
  userRepo: asClass(UserRepo).singleton(),
  userService: asClass(UserService).singleton(),
});
const svc = c.resolve("userService");  // auto-wires constructor params by name</code></pre>
<ul>
  <li><strong>DI is the mechanism; IoC is the principle.</strong> All DI is IoC; not all IoC is DI (event loops, reactive systems).</li>
  <li><strong>Benefits:</strong> testable (swap implementations), loosely coupled, explicit wiring.</li>
  <li><strong>Cost:</strong> a layer of indirection; debugging lifecycle/injection errors can be harder.</li>
  <li><strong>When to reach for a container:</strong> 10+ services, request-scoped state, team convention. Under that, manual constructor DI beats containers for clarity.</li>
</ul>
<p>Frameworks like NestJS, tsyringe, InversifyJS, and Awilix all implement IoC containers; pick one per repo and stay consistent.</p>
'''

ANSWERS[84] = r'''
<p>WebSockets give full-duplex, long-lived TCP connections over HTTP upgrade. Use <strong><code>ws</code></strong> for raw speed, <strong>Socket.IO</strong> for rooms/fallbacks/auto-reconnect, or <strong>uWebSockets.js</strong> for extreme throughput.</p>
<pre><code>// ws — bare-metal WebSocket server with heartbeat + auth
import { WebSocketServer } from "ws";
import http from "node:http";
import { verifyJwt } from "./auth.js";

const server = http.createServer();
const wss = new WebSocketServer({ noServer: true });  // manual upgrade handling

// Authenticate on HTTP upgrade — reject before opening the WS
server.on("upgrade", async (req, socket, head) =&gt; {
  try {
    const token = new URL(req.url, "http://x").searchParams.get("token");
    const user = await verifyJwt(token);
    wss.handleUpgrade(req, socket, head, (ws) =&gt; {
      ws.user = user;
      wss.emit("connection", ws, req);
    });
  } catch {
    socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
    socket.destroy();
  }
});

// Heartbeat — detect zombie connections (clients that vanish without FIN)
function heartbeat() { this.isAlive = true; }
wss.on("connection", (ws) =&gt; {
  ws.isAlive = true;
  ws.on("pong", heartbeat);

  ws.on("message", async (data) =&gt; {
    try {
      const msg = JSON.parse(data);
      // route by msg.type, validate with Zod, etc.
      ws.send(JSON.stringify({ type: "ack", userId: ws.user.id }));
    } catch (e) { ws.close(1007, "bad payload"); }
  });
});

const interval = setInterval(() =&gt; {
  for (const ws of wss.clients) {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  }
}, 30_000);
wss.on("close", () =&gt; clearInterval(interval));

server.listen(8080);</code></pre>
<ul>
  <li><strong>Authenticate on upgrade</strong> — never after. JWT in query param (browsers can't set WS headers from <code>new WebSocket(...)</code>) or in a short-lived ticket.</li>
  <li><strong>Heartbeat</strong> (ping/pong every 30s) — TCP can take hours to notice a dead peer; proxies may idle-timeout.</li>
  <li><strong>Scaling:</strong> multiple Node instances — use a Redis/NATS adapter (Socket.IO has <code>@socket.io/redis-adapter</code>) so messages broadcast across replicas.</li>
  <li><strong>Backpressure:</strong> check <code>ws.bufferedAmount</code>; drop or slow clients that can't keep up — avoid unbounded memory growth.</li>
  <li><strong>Reverse proxy:</strong> enable WebSocket upgrade (<code>proxy_set_header Upgrade $http_upgrade</code> in Nginx). ALB needs <code>http</code> target group + longer idle timeout.</li>
</ul>
<p><strong>Use Socket.IO</strong> when you want rooms, namespaces, auto-reconnect, and HTTP long-polling fallback. <strong>Use raw <code>ws</code></strong> when you control the client protocol and want minimal overhead. <strong>Consider SSE</strong> if the flow is server → client only — simpler stack, no upgrade, works over plain HTTP/2.</p>
'''

ANSWERS[85] = r'''
<p>A typical Express + MongoDB REST API has four layers: routes → controllers → services → data (Mongoose models). This separation keeps HTTP concerns out of business logic and makes each layer testable.</p>
<pre><code>// models/user.ts — Mongoose schema
import mongoose, { Schema } from "mongoose";

const UserSchema = new Schema({
  email: { type: String, required: true, unique: true, lowercase: true, trim: true, index: true },
  name: { type: String, required: true, maxlength: 100 },
  role: { type: String, enum: ["admin", "editor", "viewer"], default: "viewer" },
  createdAt: { type: Date, default: Date.now },
}, { timestamps: true, toJSON: { versionKey: false, transform: (_, ret) =&gt; { ret.id = ret._id; delete ret._id; return ret; } } });

UserSchema.index({ email: 1 }, { unique: true });
export const User = mongoose.model("User", UserSchema);</code></pre>
<pre><code>// services/user.ts — business logic, DB-specific
import { User } from "../models/user";
import { z } from "zod";

export const CreateUser = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

export const userService = {
  async create(input) {
    const data = CreateUser.parse(input);
    try { return await User.create(data); }
    catch (e) {
      if (e.code === 11000) throw Object.assign(new Error("email taken"), { status: 409 });
      throw e;
    }
  },
  list({ page = 1, limit = 20 } = {}) {
    return User.find().sort({ createdAt: -1 }).skip((page - 1) * limit).limit(limit).lean();
  },
  get(id) { return User.findById(id).lean(); },
  update(id, patch) { return User.findByIdAndUpdate(id, patch, { new: true, runValidators: true }).lean(); },
  remove(id) { return User.findByIdAndDelete(id); },
};</code></pre>
<pre><code>// routes/user.ts — HTTP boundary
import { Router } from "express";
import { userService } from "../services/user.js";
const r = Router();

r.get("/", async (req, res) =&gt; res.json(await userService.list(req.query)));
r.get("/:id", async (req, res) =&gt; {
  const u = await userService.get(req.params.id);
  if (!u) return res.status(404).json({ error: "not found" });
  res.json(u);
});
r.post("/", async (req, res, next) =&gt; {
  try { res.status(201).json(await userService.create(req.body)); } catch (e) { next(e); }
});
r.patch("/:id", async (req, res) =&gt; res.json(await userService.update(req.params.id, req.body)));
r.delete("/:id", async (req, res) =&gt; { await userService.remove(req.params.id); res.status(204).end(); });

export default r;</code></pre>
<pre><code>// app.ts — wiring
import express from "express";
import mongoose from "mongoose";
import helmet from "helmet";
import pinoHttp from "pino-http";
import userRoutes from "./routes/user.js";

await mongoose.connect(process.env.MONGO_URL);
const app = express();
app.use(helmet());
app.use(express.json({ limit: "1mb" }));
app.use(pinoHttp());
app.use("/api/v1/users", userRoutes);

// Central error handler
app.use((err, _req, res, _next) =&gt; {
  const status = err.status || 500;
  res.status(status).json({ error: err.message });
});

app.listen(process.env.PORT || 3000);</code></pre>
<p><strong>Production additions:</strong> validation middleware, auth/RBAC, rate limiter, pagination + cursor, indexes matching query shapes, <code>lean()</code> for read-only queries (skips Mongoose hydration), transactions (<code>session.withTransaction</code>) for multi-doc atomicity. Use <strong>Prisma</strong> with Mongo for TS-first DX, or <strong>MongoDB native driver</strong> if you want full control over queries.</p>
'''

ANSWERS[86] = r'''
<p>Multi-tenancy is how a single codebase serves multiple isolated customers. Three common models, from strongest isolation to cheapest ops:</p>
<table>
<thead><tr><th>Model</th><th>Isolation</th><th>Cost</th><th>Use when</th></tr></thead>
<tbody>
  <tr><td><strong>Database per tenant</strong></td><td>Highest</td><td>High (N DBs to manage)</td><td>Regulated industries, enterprise, noisy neighbors risk</td></tr>
  <tr><td><strong>Schema per tenant</strong> (Postgres)</td><td>Strong</td><td>Medium</td><td>Medium tenants, some queries per-tenant</td></tr>
  <tr><td><strong>Shared schema + tenant_id</strong></td><td>Logical (RLS for enforcement)</td><td>Lowest</td><td>SaaS with many small tenants</td></tr>
  <tr><td><strong>Hybrid</strong></td><td>Mixed</td><td>Medium</td><td>Small on shared, large on own DB</td></tr>
</tbody>
</table>
<pre><code>// Shared-schema approach — tenant context via AsyncLocalStorage
import { AsyncLocalStorage } from "node:async_hooks";
const tenantCtx = new AsyncLocalStorage();

// Resolve tenant from subdomain / header / JWT claim
app.use((req, res, next) =&gt; {
  const tenantId = req.user?.tenantId || req.headers["x-tenant-id"];
  if (!tenantId) return res.status(400).json({ error: "tenant required" });
  tenantCtx.run({ tenantId }, next);
});

// Repository always injects tenant filter — safe by construction
export const userRepo = {
  list() {
    const { tenantId } = tenantCtx.getStore();
    return db.query("SELECT * FROM users WHERE tenant_id = $1", [tenantId]);
  },
};</code></pre>
<pre><code>-- Postgres Row-Level Security — DB-enforced isolation
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON users
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- In Node: before each query, set tenant context
await pool.query("SET LOCAL app.tenant_id = $1", [tenantId]);</code></pre>
<ul>
  <li><strong>Tenant resolution:</strong> subdomain (<code>acme.app.com</code>), path prefix (<code>/t/acme/...</code>), JWT claim (most secure), or header (internal).</li>
  <li><strong>Enforce at multiple layers:</strong> app-layer filters + DB RLS + connection-level role — defense in depth. A missed <code>WHERE tenant_id</code> has leaked entire customer databases.</li>
  <li><strong>Noisy neighbors:</strong> rate-limit, quota, connection pools per tenant — one huge tenant shouldn't starve others.</li>
  <li><strong>Observability:</strong> tag logs, metrics, traces with <code>tenant_id</code> for per-tenant debugging.</li>
  <li><strong>Migrations:</strong> shared schema = one migration, run once. Schema-per-tenant = iterate or use <code>pg_tenancy</code>/custom migration runner. Database-per-tenant = orchestrated migration rollouts.</li>
  <li><strong>Backups + DR:</strong> easy per-DB; for shared schema, consider logical backups filtered by tenant for support restores.</li>
</ul>
<p>Start with shared-schema + RLS; graduate bigger tenants to dedicated DBs only when noisy-neighbor or compliance forces it.</p>
'''

ANSWERS[87] = r'''
<p>Both scaling axes have their place; real systems combine them.</p>
<table>
<thead><tr><th>Aspect</th><th>Vertical (scale up)</th><th>Horizontal (scale out)</th></tr></thead>
<tbody>
  <tr><td>Action</td><td>Bigger machine (more CPU, RAM)</td><td>More instances behind a load balancer</td></tr>
  <tr><td>Node fit</td><td>Limited — single thread uses one core</td><td>Excellent — cluster/replicas per core</td></tr>
  <tr><td>Ceiling</td><td>Hardware max, expensive tiers</td><td>Effectively unlimited</td></tr>
  <tr><td>Failure mode</td><td>Single point of failure</td><td>Node death survivable</td></tr>
  <tr><td>State</td><td>Local is fine</td><td>Must externalize (DB, Redis, S3)</td></tr>
  <tr><td>Cost curve</td><td>Exponential at top</td><td>Linear</td></tr>
  <tr><td>Deploy complexity</td><td>Low</td><td>Higher (LB, service discovery, config)</td></tr>
</tbody>
</table>
<p><strong>Node's single-threaded nature</strong> makes horizontal the primary scaling path:</p>
<ul>
  <li><strong>Within a host:</strong> <code>cluster</code> module or PM2 → one worker per CPU core. This is "scaling up" the Node <em>app</em>, scaling out workers.</li>
  <li><strong>Across hosts:</strong> containers + orchestrator (K8s, ECS, Fly) scale replicas based on CPU / RPS / queue depth metrics.</li>
</ul>
<p><strong>12-factor prerequisites for horizontal scaling</strong> — all state must be external:</p>
<ul>
  <li>Sessions → Redis / JWT (stateless tokens)</li>
  <li>File uploads → S3 / GCS</li>
  <li>Cache → Redis</li>
  <li>Long jobs → queue (BullMQ, SQS)</li>
  <li>WebSockets → Redis pub/sub adapter so any replica can reach any client</li>
  <li>Logs → stdout → aggregator (not local files)</li>
</ul>
<pre><code># K8s HPA — auto-scale pods on CPU + custom metric
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 3
  maxReplicas: 50
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
    - type: Pods
      pods: { metric: { name: http_requests_per_second }, target: { type: AverageValue, averageValue: "200" } }</code></pre>
<p><strong>Practical advice:</strong> scale vertically first (cheaper until a point, fewer moving parts), horizontally once state is externalized. Bottleneck is rarely Node — it's the DB. Scale reads with replicas and cache; scale writes with sharding or eventually-consistent patterns. For CPU-bound Node work, <code>worker_threads</code> is "vertical within a process" — a third axis.</p>
'''

ANSWERS[88] = r'''
<p>A distributed cache is shared in-memory storage accessible by all app instances, letting them collaborate on cache state. Without it, each instance has its own cold cache and most requests miss.</p>
<table>
<thead><tr><th>Option</th><th>Strength</th><th>Trade-off</th></tr></thead>
<tbody>
  <tr><td><strong>Redis</strong> (Elasticache, Upstash, Dragonfly)</td><td>Rich types, pub/sub, Lua scripts, persistence</td><td>Single-leader per shard; Cluster for sharding</td></tr>
  <tr><td><strong>Memcached</strong></td><td>Multi-threaded, simple, massive throughput</td><td>Strings only, no persistence</td></tr>
  <tr><td><strong>DynamoDB DAX</strong></td><td>Transparent write-through cache for DynamoDB</td><td>AWS-specific</td></tr>
  <tr><td><strong>Hazelcast / Apache Ignite</strong></td><td>Embedded + distributed, map-reduce</td><td>Heavier, JVM-centric</td></tr>
</tbody>
</table>
<pre><code>// Redis Cluster with ioredis — sharded, HA
import Redis from "ioredis";

const cluster = new Redis.Cluster([
  { host: "r1", port: 6379 },
  { host: "r2", port: 6379 },
  { host: "r3", port: 6379 },
], {
  scaleReads: "slave",       // route reads to replicas
  enableReadyCheck: true,
  maxRedirections: 16,       // follow MOVED/ASK during resharding
});

// Cache with singleflight + refresh-ahead (prevents stampede)
const inflight = new Map();
async function getUser(id) {
  const key = `user:${id}`;
  const [cached, ttl] = await cluster.pipeline().get(key).ttl(key).exec().then(rs =&gt; [rs[0][1], rs[1][1]]);
  if (cached) {
    // Refresh in background if nearing expiry — user never sees a miss
    if (ttl &lt; 30 &amp;&amp; !inflight.has(key)) {
      inflight.set(key, refresh(id, key).finally(() =&gt; inflight.delete(key)));
    }
    return JSON.parse(cached);
  }
  if (inflight.has(key)) return inflight.get(key);  // dedupe concurrent misses
  const p = refresh(id, key).finally(() =&gt; inflight.delete(key));
  inflight.set(key, p);
  return p;
}
async function refresh(id, key) {
  const user = await db.user.findUnique({ where: { id } });
  await cluster.set(key, JSON.stringify(user), "EX", 300);
  return user;
}</code></pre>
<ul>
  <li><strong>Sharding:</strong> Redis Cluster distributes keys across N shards via hash slots (16,384). Multi-key ops require <strong>hash tags</strong> (<code>{user:42}:profile</code> and <code>{user:42}:posts</code> land on same shard).</li>
  <li><strong>Replication:</strong> Redis Sentinel (single-master) or Cluster (sharded master-replica). AWS Elasticache manages both.</li>
  <li><strong>Cache stampede:</strong> singleflight (dedupe concurrent fetches), refresh-ahead (update before TTL), jittered TTL.</li>
  <li><strong>Consistency:</strong> follow <strong>cache-aside</strong> (write DB, invalidate cache) — write-through on Redis is rare in Node apps.</li>
  <li><strong>Eviction:</strong> set <code>maxmemory-policy</code> (usually <code>allkeys-lru</code> for cache, <code>volatile-ttl</code> for mixed).</li>
  <li><strong>Client library:</strong> <code>ioredis</code> (cluster + sentinel + streams) is the most capable; <code>redis</code> v4+ is simpler.</li>
</ul>
<p><strong>Don't cache what's cheap to fetch.</strong> A 1 ms indexed Postgres query usually doesn't need caching; a 500 ms aggregation does.</p>
'''

ANSWERS[89] = r'''
<p>Feature toggles (flags) decouple <em>deploy</em> from <em>release</em> — code ships dark, then flips on per-tenant, per-user, or percentage. Use them for kill switches, canaries, A/B tests, and progressive rollouts.</p>
<table>
<thead><tr><th>Type</th><th>Purpose</th><th>Lifetime</th></tr></thead>
<tbody>
  <tr><td><strong>Release</strong></td><td>Ship code behind a flag, enable gradually</td><td>Days-weeks, then delete</td></tr>
  <tr><td><strong>Kill switch</strong></td><td>Disable broken subsystem quickly</td><td>Permanent</td></tr>
  <tr><td><strong>Experiment (A/B)</strong></td><td>Measure variant impact</td><td>Weeks</td></tr>
  <tr><td><strong>Permission</strong></td><td>Gate features by plan/role</td><td>Permanent</td></tr>
  <tr><td><strong>Ops</strong></td><td>Tune runtime (sample rates, timeouts)</td><td>Permanent</td></tr>
</tbody>
</table>
<p><strong>Providers:</strong> <a>LaunchDarkly</a> (enterprise), <a>Flagsmith</a> / <a>Unleash</a> (self-hostable, OSS), <a>ConfigCat</a>, <a>PostHog</a>, AWS AppConfig, Cloudflare Workers KV for edge.</p>
<pre><code>// Unleash client (OSS) — fetches and caches flags, evaluates locally
import { initialize, isEnabled, getVariant } from "unleash-client";

const unleash = initialize({
  url: "https://unleash.mycorp.com/api",
  appName: "my-api",
  instanceId: process.env.HOSTNAME,
  refreshInterval: 15_000,          // poll for changes
});

unleash.on("ready", () =&gt; log.info("flags loaded"));

app.use((req, res, next) =&gt; {
  req.flags = {
    newCheckout: isEnabled("new-checkout", { userId: req.user?.id, tenantId: req.user?.tenantId }),
    experiment: getVariant("pricing-v2", { userId: req.user?.id }).name,  // "control" | "variantA" | "variantB"
  };
  next();
});

app.post("/checkout", (req, res) =&gt; {
  if (req.flags.newCheckout) return newCheckoutHandler(req, res);
  return legacyCheckoutHandler(req, res);
});</code></pre>
<ul>
  <li><strong>Evaluate locally</strong> (SDK caches rules) — don't call a remote service on every request.</li>
  <li><strong>Targeting rules:</strong> userId hash %, tenant allowlist, region, date window.</li>
  <li><strong>Safe defaults:</strong> if flag service is down, return <em>off</em> for release flags (fail-safe); <em>on</em> for kill switches (fail-open only when explicitly intended).</li>
  <li><strong>Instrument:</strong> emit a "flag evaluated" event with variant + outcome — essential for A/B stats and for auditing why a user got a feature.</li>
  <li><strong>Retire flags:</strong> once rolled out, delete the flag + all branches in code. Stale flags are the biggest tech debt in flag systems.</li>
  <li><strong>Don't flag business logic forever</strong> — flags are for temporary dual-path code, not permanent branching.</li>
</ul>
<p><strong>Minimum viable:</strong> a JSON column in the config DB + 15-second cached fetch gets you 80% of the benefit. Graduate to a dedicated platform when you need targeting rules, experimentation, and audit.</p>
'''

ANSWERS[90] = r'''
<p>"Real-time notification" spans several transport + destination combinations. Architect as a notification <em>service</em> with pluggable channels rather than sprinkling sends through the codebase.</p>
<table>
<thead><tr><th>Channel</th><th>Transport</th><th>Use</th></tr></thead>
<tbody>
  <tr><td>In-app (open tab)</td><td>WebSocket / Socket.IO / SSE</td><td>Live feeds, comments, status</td></tr>
  <tr><td>In-app (closed browser)</td><td>Web Push (VAPID) + Service Worker</td><td>Re-engagement</td></tr>
  <tr><td>Mobile push</td><td>FCM (Android/web) / APNs (iOS) via Firebase, OneSignal, Pushwoosh</td><td>App pings</td></tr>
  <tr><td>Email</td><td>SES, Postmark, SendGrid, Resend</td><td>Summaries, receipts, digest</td></tr>
  <tr><td>SMS/WhatsApp</td><td>Twilio, Vonage</td><td>Urgent, 2FA</td></tr>
  <tr><td>Managed realtime</td><td>Pusher, Ably, PubNub, Supabase Realtime</td><td>Skip self-hosted infra</td></tr>
</tbody>
</table>
<pre><code>// Notification dispatcher — one event, many channels
import { Queue, Worker } from "bullmq";
const q = new Queue("notifications", { connection });

export async function notify({ userId, event, payload }) {
  await q.add(event, { userId, event, payload }, {
    attempts: 5,
    backoff: { type: "exponential", delay: 2000 },
    jobId: `${event}:${userId}:${payload.id}`, // idempotent
  });
}

// Worker — load user prefs, fan out to enabled channels
new Worker("notifications", async ({ data }) =&gt; {
  const prefs = await prefRepo.get(data.userId);
  const channels = selectChannels(data.event, prefs);  // e.g. ["inApp", "email"]
  await Promise.allSettled(channels.map(ch =&gt; channel[ch].send(data)));
}, { connection, concurrency: 20 });

// In-app channel: Redis pub/sub so any Socket.IO replica can deliver
channel.inApp = {
  async send({ userId, event, payload }) {
    await redis.publish(`user:${userId}`, JSON.stringify({ event, payload }));
  },
};
// Elsewhere: Socket.IO subscribes each user socket to `user:${userId}`</code></pre>
<ul>
  <li><strong>User preferences:</strong> which events + channels per user; respect quiet hours, digests, opt-outs (and legally, unsubscribe links for email/SMS).</li>
  <li><strong>Delivery guarantees:</strong> queue + retry + DLQ. Track delivery status per channel for observability.</li>
  <li><strong>Deduplication:</strong> a user shouldn't get 5 emails because 5 replicas processed the same trigger — idempotency keys in the queue.</li>
  <li><strong>Scale WebSockets across instances:</strong> Redis adapter (Socket.IO) or NATS pub/sub.</li>
  <li><strong>Templates:</strong> MJML (email), JSON for push — generate server-side with i18n.</li>
  <li><strong>Rate limit per user:</strong> avoid notification spam that drives unsubscribes.</li>
</ul>
<p><strong>Build vs buy:</strong> small app → Firebase (push) + Resend (email) is 2 integrations and done. Scale up → self-host Socket.IO + Redis + BullMQ for in-app, keep transactional email with a provider, and layer a unified dispatcher over it.</p>
'''

ANSWERS[91] = r'''
<p>Backpressure is the mechanism by which a slow consumer tells a fast producer to <em>pause</em>, preventing unbounded memory growth. Ignoring it is how Node apps OOM at 3 AM.</p>
<p><strong>In Node streams:</strong> <code>writable.write(chunk)</code> returns <code>true</code> when the internal buffer is below <code>highWaterMark</code> (default 16 KB for byte streams, 16 objects for object-mode), <code>false</code> when full. The producer should stop and wait for <code>"drain"</code> before writing more.</p>
<pre><code>// Manual backpressure — rarely needed, but illustrates the API
const src = createReadStream("huge.log");
const dst = createWriteStream("out.log");
src.on("data", (chunk) =&gt; {
  if (!dst.write(chunk)) src.pause();
});
dst.on("drain", () =&gt; src.resume());
src.on("end", () =&gt; dst.end());
src.on("error", (e) =&gt; { dst.destroy(e); });

// The preferred way — pipeline() handles backpressure + errors + cleanup
import { pipeline } from "node:stream/promises";
import { createGzip } from "node:zlib";
await pipeline(
  createReadStream("huge.log"),
  createGzip(),
  createWriteStream("huge.log.gz")
); // awaits completion, destroys all on error

// Async iterators — idiomatic modern consumption with natural backpressure
for await (const chunk of stream) {
  await processChunk(chunk); // loop only advances when ready
}</code></pre>
<pre><code>// Custom Writable that respects backpressure (slow downstream DB)
import { Writable } from "node:stream";
class DbSink extends Writable {
  constructor(opts) { super({ ...opts, objectMode: true, highWaterMark: 50 }); }
  async _write(record, _enc, cb) {
    try { await db.insert(record); cb(); }   // cb() signals "ready for more"
    catch (e) { cb(e); }
  }
  async _writev(records, cb) {                // batch for efficiency
    try { await db.insertMany(records.map(r =&gt; r.chunk)); cb(); }
    catch (e) { cb(e); }
  }
}
await pipeline(csvSource, parseCsv(), new DbSink());</code></pre>
<ul>
  <li><strong><code>pipeline()</code> always</strong> — never manual <code>.pipe()</code>. Pipeline propagates errors, destroys all streams on failure, closes descriptors.</li>
  <li><strong>Tune <code>highWaterMark</code></strong> for your workload — larger reduces context switches; smaller reduces memory.</li>
  <li><strong>Beyond streams:</strong> HTTP requests have implicit backpressure via TCP flow control. Queues (BullMQ) have explicit concurrency limits. Redis pub/sub has <em>none</em> — slow subscribers get messages dropped (use Streams).</li>
  <li><strong>Event emitters are not streams</strong> — <code>ee.emit(...)</code> has no backpressure. If consumers can lag, use a stream or a queue.</li>
  <li><strong>AbortController</strong> integrates: if the consumer aborts, <code>pipeline</code> tears down upstream.</li>
</ul>
<p><strong>Debugging:</strong> sudden memory growth under load usually means missed backpressure. Heap snapshots often show one huge <code>Buffer</code> array inside a stream's internal buffer — that's the smoking gun.</p>
'''

ANSWERS[92] = r'''
<p>A proxy server forwards requests on behalf of clients — transforming, routing, or aggregating. Node proxies are typically thin glue in front of upstreams (API composition, token injection, legacy wrapping) — for production edge routing, prefer Nginx/Envoy/Caddy.</p>
<pre><code>// http-proxy-middleware — the standard in Express
import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";

const app = express();

// Forward /api/* to an internal service, rewriting the path
app.use("/api", createProxyMiddleware({
  target: "http://upstream.internal:4000",
  changeOrigin: true,
  pathRewrite: { "^/api": "/v1" },
  xfwd: true,                // set X-Forwarded-* headers
  timeout: 30_000,
  proxyTimeout: 25_000,
  on: {
    proxyReq: (proxyReq, req) =&gt; {
      proxyReq.setHeader("X-Request-Id", req.id);
      if (req.user) proxyReq.setHeader("X-User-Id", req.user.id);
    },
    proxyRes: (proxyRes) =&gt; {
      proxyRes.headers["X-Proxied-By"] = "api-gateway";
      delete proxyRes.headers["server"];
    },
    error: (err, req, res) =&gt; {
      res.status(502).json({ error: "upstream unavailable" });
    },
  },
}));

app.listen(8080);</code></pre>
<pre><code>// Raw proxy with node:http — full control
import http from "node:http";
http.createServer((req, res) =&gt; {
  const upstream = http.request({
    host: "upstream", port: 4000, path: req.url, method: req.method,
    headers: { ...req.headers, "x-forwarded-for": req.socket.remoteAddress },
  }, (upRes) =&gt; {
    res.writeHead(upRes.statusCode, upRes.headers);
    upRes.pipe(res);                 // streaming — no buffering
  });
  req.pipe(upstream);                // backpressure-safe
  upstream.on("error", () =&gt; res.writeHead(502).end());
}).listen(8080);</code></pre>
<ul>
  <li><strong>Streaming body</strong> — don't <code>await req.body</code>; pipe through. Preserves large uploads, WebSocket frames, SSE.</li>
  <li><strong>Preserve headers</strong> properly — don't duplicate <code>host</code>; add <code>X-Forwarded-For</code>, <code>X-Forwarded-Proto</code>, <code>X-Forwarded-Host</code>.</li>
  <li><strong>Timeouts</strong> — set both socket and upstream-response to bounded values; unbounded proxies leak sockets.</li>
  <li><strong>Headers hygiene:</strong> strip <code>Connection</code>, <code>Keep-Alive</code>, hop-by-hop headers when forwarding.</li>
  <li><strong>WebSockets:</strong> <code>http-proxy-middleware</code> supports <code>ws: true</code> + upgrade handling.</li>
  <li><strong>Circuit breaker</strong> (<code>cockatiel</code>, <code>opossum</code>) in front of upstream calls — fail fast when it's down.</li>
</ul>
<p><strong>Use Node proxies</strong> for per-request logic that needs app context (auth, token exchange, response composition). <strong>Use Envoy/Nginx</strong> at the edge for L7 load balancing, TLS termination, mTLS, and raw throughput.</p>
'''

ANSWERS[93] = r'''
<p>A reverse proxy sits <em>in front</em> of your Node app(s) — it terminates TLS, load-balances, serves static files, caches, rate-limits, and forwards dynamic requests to Node. This is the production-standard topology.</p>
<pre><code># /etc/nginx/sites-available/api.conf — Nginx in front of Node
upstream node_app {
  least_conn;
  server 127.0.0.1:3000 max_fails=3 fail_timeout=10s;
  server 127.0.0.1:3001 max_fails=3 fail_timeout=10s;
  keepalive 64;         # connection pool to upstream
}

server {
  listen 443 ssl http2;
  server_name api.example.com;

  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
  ssl_protocols TLSv1.2 TLSv1.3;

  # Security headers
  add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
  add_header X-Content-Type-Options "nosniff" always;

  # Static assets — nginx serves directly, never hits Node
  location /static/ {
    root /var/www/app;
    expires 1y;
    add_header Cache-Control "public, immutable";
  }

  # Dynamic — reverse proxy to Node
  location / {
    proxy_pass http://node_app;
    proxy_http_version 1.1;

    # Forwarding headers — Node uses these for req.ip, req.protocol
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host  $host;

    # WebSocket upgrade
    proxy_set_header Upgrade    $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;     # long SSE/WS connections

    # Connection reuse
    proxy_set_header Connection "";
  }
}

# HTTP → HTTPS redirect
server { listen 80; server_name api.example.com; return 301 https://$host$request_uri; }</code></pre>
<pre><code>// In Node — trust the proxy so req.ip / req.protocol are correct
import express from "express";
const app = express();
app.set("trust proxy", 1);   // trust first proxy (X-Forwarded-For)
// Now: req.ip = real client IP; req.protocol = "https" when proxied over TLS
// For Fastify: fastify({ trustProxy: true })</code></pre>
<ul>
  <li><strong>Why not Node direct?</strong> Reverse proxies are battle-tested for TLS, connection handling, slow-client tolerance, static file serving, and broad HTTP correctness. Node is better at application logic.</li>
  <li><strong>Trust proxy:</strong> without <code>trust proxy</code>, <code>req.ip</code> is <code>127.0.0.1</code> (the proxy), breaking rate limits, audit logs, geo-detection.</li>
  <li><strong>Choices:</strong> Nginx (classic, fast), Caddy (auto-HTTPS, easier config), Envoy (L7 features, service mesh), HAProxy (L4, TCP-heavy), Traefik (container-native, auto-discovery), Cloud: ALB / Cloudfront / CloudFlare / GCP LB.</li>
  <li><strong>TLS:</strong> Let's Encrypt via Certbot, or ACME in Caddy/Traefik (fully automated). Never TLS in Node directly in production.</li>
  <li><strong>Health checks:</strong> expose <code>/health</code> in Node; configure proxy to route only to healthy upstreams.</li>
  <li><strong>Rate limiting:</strong> first layer at proxy (Nginx <code>limit_req</code>) blocks obvious abuse cheaply; second layer per-user in Node for business rules.</li>
</ul>
<p><strong>Kubernetes:</strong> the reverse proxy is often an Ingress controller (nginx-ingress, Traefik, or Gateway API) — same principle, declarative config.</p>
'''

ANSWERS[94] = r'''
<p>OAuth 2.0 is a delegation framework: a user authorizes your app to access their data at a resource server (Google, GitHub, your own IdP) without sharing credentials. In 2026, use <strong>Authorization Code + PKCE</strong> for any flow involving a browser — implicit and password grants are deprecated.</p>
<pre><code>// openid-client — the reference-quality OIDC/OAuth2 library (replaces passport-oauth2)
import { Issuer, generators } from "openid-client";
import express from "express";

const issuer = await Issuer.discover("https://accounts.google.com");
const client = new issuer.Client({
  client_id: process.env.GOOGLE_CLIENT_ID,
  client_secret: process.env.GOOGLE_CLIENT_SECRET,
  redirect_uris: ["https://app.example.com/auth/callback"],
  response_types: ["code"],
});

const app = express();

app.get("/auth/login", (req, res) =&gt; {
  const code_verifier = generators.codeVerifier();
  const code_challenge = generators.codeChallenge(code_verifier);
  const state = generators.state();
  const nonce = generators.nonce();

  // Store in short-lived signed cookie or server session
  req.session.pkce = { code_verifier, state, nonce };

  res.redirect(client.authorizationUrl({
    scope: "openid email profile",
    code_challenge, code_challenge_method: "S256",
    state, nonce,
  }));
});

app.get("/auth/callback", async (req, res, next) =&gt; {
  try {
    const params = client.callbackParams(req);
    const { code_verifier, state, nonce } = req.session.pkce;
    const tokenSet = await client.callback(
      "https://app.example.com/auth/callback",
      params,
      { state, nonce, code_verifier },
    );
    const user = await client.userinfo(tokenSet.access_token);

    // Create your app's session — don't expose raw OAuth tokens to browser
    req.session.userId = await findOrCreateUser(user);
    res.redirect("/");
  } catch (e) { next(e); }
});</code></pre>
<ul>
  <li><strong>Authorization Code + PKCE</strong> is now the default for SPAs, mobile, <em>and</em> server apps. Treat it as mandatory.</li>
  <li><strong>OpenID Connect (OIDC)</strong> = OAuth2 + identity layer (ID token JWT). Use OIDC when you need user identity, OAuth2 when you just need API access.</li>
  <li><strong><code>state</code></strong> parameter prevents CSRF on the callback; <strong><code>nonce</code></strong> binds ID token to this flow.</li>
  <li><strong>Refresh tokens:</strong> store server-side, rotate, revoke on logout.</li>
  <li><strong>Never expose <code>access_token</code> to the browser</strong> — issue your own session cookie/JWT bound to an app-side session record.</li>
  <li><strong>Scopes:</strong> request the minimum; escalate via re-consent when you need more.</li>
  <li><strong>Machine-to-machine:</strong> client_credentials grant; rotate client secrets; prefer mTLS or private_key_jwt.</li>
</ul>
<p><strong>Managed IdP vs roll-your-own:</strong> Auth0, Clerk, Firebase Auth, Supabase Auth, WorkOS, Okta, AWS Cognito — they handle the entire flow including MFA, SSO (SAML, OIDC), user DB. For most teams, <em>buy this</em>. Build your own only if you have specific constraints (sovereignty, regulatory) or deep auth expertise.</p>
'''

ANSWERS[95] = r'''
<p>Express middleware is a function <code>(req, res, next) =&gt; {}</code>. When a request arrives, Express walks a sequential list, invoking each matching middleware; each must either call <code>next()</code> (pass to the next), <code>next(err)</code> (jump to error handlers), or terminate via <code>res.send()</code>/<code>res.end()</code>. This creates a "chain" (or <em>onion</em>) where each layer wraps the next.</p>
<pre><code>import express from "express";
const app = express();

// 1. Request ID — runs first, every request
app.use((req, _res, next) =&gt; {
  req.id = crypto.randomUUID();
  next();
});

// 2. Logger — records start + finish
app.use((req, res, next) =&gt; {
  const t = Date.now();
  res.on("finish", () =&gt; log.info({ id: req.id, method: req.method, url: req.url, status: res.statusCode, ms: Date.now() - t }));
  next();
});

// 3. Body parser
app.use(express.json({ limit: "1mb" }));

// 4. Auth (route-specific)
const authRequired = async (req, res, next) =&gt; {
  try {
    const token = req.headers.authorization?.slice("Bearer ".length);
    req.user = await verifyJwt(token);
    next();
  } catch { res.status(401).json({ error: "unauthorized" }); }
};

// 5. Validation factory — returns middleware
const validate = (schema) =&gt; (req, res, next) =&gt; {
  const r = schema.safeParse(req.body);
  if (!r.success) return res.status(400).json({ issues: r.error.issues });
  req.body = r.data;
  next();
};

// Compose into route — chain of responsibility
app.post("/posts",
  authRequired,
  validate(CreatePost),
  async (req, res) =&gt; res.status(201).json(await postService.create(req.user, req.body)),
);

// Error handler — 4-arg signature, goes LAST
app.use((err, req, res, _next) =&gt; {
  log.error({ id: req.id, err });
  const status = err.status || 500;
  res.status(status).json({ error: err.message || "internal error" });
});</code></pre>
<ul>
  <li><strong>Order matters.</strong> Put security (helmet), parsers, logging, and request-id early; auth before routes that need it; error handler absolute last.</li>
  <li><strong>Global vs route vs router:</strong> <code>app.use(fn)</code> (everything), <code>app.use("/admin", fn)</code> (prefix), <code>router.post(path, fn1, fn2, handler)</code> (per-route chain).</li>
  <li><strong>Async errors:</strong> Express 4 needs <code>try/catch + next(err)</code> or <code>express-async-errors</code>. <strong>Express 5</strong> auto-forwards rejected promises — but still install a central error handler.</li>
  <li><strong>Onion model (Koa-style):</strong> awaiting <code>next()</code> returns after downstream completes — great for wrapping (timing, compression, transactions). Express doesn't have this natively (middleware are one-way), but Koa and Fastify hooks do.</li>
  <li><strong>Short-circuit:</strong> any middleware can terminate by responding without calling <code>next()</code>.</li>
  <li><strong>Factory pattern</strong> (like <code>validate(schema)</code>) is the clean way to parameterize middleware.</li>
</ul>
<p><strong>Keep middleware small, single-purpose, and testable</strong> — call them with fake req/res/next in unit tests; use <code>supertest</code> for integration. Don't reach into <code>req.app</code> globals from middleware — inject dependencies via closure or <code>req</code> attached in earlier middleware.</p>
'''

ANSWERS[96] = r'''
<p>Internationalization (i18n) is designing for language- and culture-agnostic output; localization (l10n) is providing the specific translations. On the server, i18n covers API responses, emails, SMS, PDFs, and error messages — anything rendered text.</p>
<pre><code>// i18next — the de-facto standard for Node, with ICU support
import i18next from "i18next";
import Backend from "i18next-fs-backend";
import middleware, { LanguageDetector } from "i18next-http-middleware";

await i18next
  .use(Backend)
  .use(LanguageDetector)
  .init({
    fallbackLng: "en",
    supportedLngs: ["en", "es", "fr", "de", "ja", "hi"],
    preload: ["en", "es", "fr"],
    ns: ["common", "email"],
    defaultNS: "common",
    backend: { loadPath: "./locales/{{lng}}/{{ns}}.json" },
    detection: { order: ["header", "querystring", "cookie"], lookupHeader: "accept-language" },
  });

app.use(middleware.handle(i18next));

// locales/en/common.json
// { "welcome": "Welcome, {{name}}!",
//   "itemCount_one": "{{count}} item", "itemCount_other": "{{count}} items",
//   "price": "{{val, currency}}" }

app.get("/", (req, res) =&gt; {
  res.json({
    greeting: req.t("welcome", { name: req.user?.name ?? "friend" }),
    cart: req.t("itemCount", { count: 3 }),        // auto plural form
    total: req.t("price", { val: 1299.50, formatParams: { val: { currency: "USD" } } }),
  });
});</code></pre>
<pre><code>// Intl — built into Node, use for formatting (not translation)
new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(1299.5);
// "1.299,50 €"

new Intl.DateTimeFormat("ja-JP", { dateStyle: "long" }).format(new Date());
// "2026年4月18日"

new Intl.RelativeTimeFormat("es").format(-3, "day");
// "hace 3 días"

new Intl.PluralRules("ar").select(3);  // "few" (Arabic has 6 plural forms)

new Intl.ListFormat("fr", { type: "conjunction" }).format(["pommes", "oranges", "bananes"]);
// "pommes, oranges et bananes"</code></pre>
<ul>
  <li><strong>Locale negotiation:</strong> <code>Accept-Language</code> header (weighted list); fall back to tenant default, then app default. Let users override via a profile setting.</li>
  <li><strong>ICU MessageFormat</strong> (supported by i18next) handles plurals, gender, and nested selects properly — don't try to glue translations with string concat.</li>
  <li><strong>Pluralization</strong> is not "one or many" — Russian has 3 forms, Arabic 6, Japanese 1. Let the library pick the right form via <code>count</code>.</li>
  <li><strong>Intl (built-in)</strong> handles numbers, currency, dates, relative time, list formatting, plural rules, collation — use it instead of hand-written formatters.</li>
  <li><strong>Time zones:</strong> store UTC in DB, convert at the boundary using <code>Intl.DateTimeFormat(locale, { timeZone })</code> or <code>temporal</code> (Stage 3).</li>
  <li><strong>Right-to-left</strong> (Arabic, Hebrew, Farsi) is a rendering concern — include the <code>lang</code>/<code>dir</code> in emails and expose locale to the frontend.</li>
  <li><strong>Translation workflow:</strong> source in English, export to translators via Lokalise, Crowdin, or Phrase; CI validates no missing keys.</li>
</ul>
<p><strong>Never concat translated fragments.</strong> Each full sentence is one key; let the library substitute placeholders and handle grammar.</p>
'''

ANSWERS[97] = r'''
<p>Production optimization is a checklist across runtime, network, database, observability, and deployment. The biggest wins are usually at the database and in avoiding blocking operations — micro-optimizing hot loops rarely moves the needle.</p>
<table>
<thead><tr><th>Layer</th><th>Action</th></tr></thead>
<tbody>
  <tr><td><strong>Node runtime</strong></td><td>LTS, <code>--enable-source-maps</code>, tune <code>UV_THREADPOOL_SIZE</code> (default 4) for crypto/fs-heavy workloads; for ESM use native imports, not <code>ts-node</code> on hot path</td></tr>
  <tr><td><strong>Process model</strong></td><td>One Node process per CPU core (cluster, PM2, or K8s replicas); pin pods to cores</td></tr>
  <tr><td><strong>HTTP</strong></td><td>Keep-alive on both inbound and outbound (<code>undici</code> pool), HTTP/2 at proxy, compression at proxy, response size budgets</td></tr>
  <tr><td><strong>DB</strong></td><td>Pool size matching downstream capacity; indexes for every <code>WHERE</code>/<code>ORDER BY</code>; avoid N+1 (DataLoader, joins); paginate by cursor; read replicas for heavy reads</td></tr>
  <tr><td><strong>Caching</strong></td><td>Redis cache-aside with short TTL + invalidation; HTTP cache headers (<code>Cache-Control</code>, <code>ETag</code>) on public responses</td></tr>
  <tr><td><strong>Async boundaries</strong></td><td>Offload CPU-heavy work to workers; use queues for anything slow; respond first, process later</td></tr>
  <tr><td><strong>Memory</strong></td><td>Set <code>--max-old-space-size</code> ~75% of container memory; watch for heap growth; fix leaks (snapshots)</td></tr>
  <tr><td><strong>Observability</strong></td><td>Structured JSON logs (pino), RED/USE metrics (Prometheus), traces (OpenTelemetry), profile prod with clinic/0x</td></tr>
  <tr><td><strong>Security</strong></td><td>Helmet, CORS allowlist, input validation, rate limits, dep audit, secret rotation</td></tr>
  <tr><td><strong>Deploy</strong></td><td>Small containers, healthchecks, graceful shutdown (SIGTERM drain), canary/blue-green, autoscale on CPU + RPS</td></tr>
</tbody>
</table>
<pre><code>// Typical high-impact wins
// 1. Connection pooling + keep-alive for outbound HTTP
import { Agent, setGlobalDispatcher } from "undici";
setGlobalDispatcher(new Agent({
  connections: 128,         // pool size
  pipelining: 1,
  keepAliveTimeout: 30_000,
  keepAliveMaxTimeout: 60_000,
}));

// 2. DB pool — match app concurrency to DB max_connections
const pool = new Pool({ connectionString, max: 20, idleTimeoutMillis: 30_000 });

// 3. Response compression at proxy; gzip in Node only if proxy doesn't

// 4. Graceful shutdown — drain in-flight requests
const server = app.listen(port);
process.on("SIGTERM", async () =&gt; {
  server.close();                        // stop accepting new
  await pool.end();                      // close DB
  process.exit(0);
});</code></pre>
<p><strong>Measure first.</strong> Profile with <code>node --inspect</code> + Chrome DevTools, <code>clinic doctor</code>, <code>0x</code> flame graphs. Don't tune without evidence — "why is the 99th percentile 4 seconds?" almost always points to a specific DB query or an external API with no timeout.</p>
<p><strong>Set SLOs, then optimize to hit them</strong> — "response p95 &lt; 300 ms, error rate &lt; 0.1%." Without a target, you'll optimize forever.</p>
'''

ANSWERS[98] = r'''
<p>Load balancing distributes incoming requests across N backend instances to increase capacity, enable zero-downtime deploys, and tolerate failures. For Node (single-threaded), it's the primary scaling mechanism.</p>
<table>
<thead><tr><th>Layer</th><th>Examples</th><th>Strengths</th></tr></thead>
<tbody>
  <tr><td><strong>L4 (TCP)</strong></td><td>HAProxy, AWS NLB, Envoy L4</td><td>Extreme throughput, simple, any protocol</td></tr>
  <tr><td><strong>L7 (HTTP)</strong></td><td>Nginx, HAProxy, AWS ALB, GCP HTTPS LB, Cloudflare, Envoy</td><td>Routing by path/header/cookie, WAF, TLS, rewrites</td></tr>
  <tr><td><strong>DNS-based</strong></td><td>Route 53, Cloudflare LB</td><td>Geo/latency routing; coarse-grained, TTL-limited failover</td></tr>
  <tr><td><strong>In-Node</strong></td><td><code>cluster</code>, PM2</td><td>Per-host across cores (use OS-level SO_REUSEPORT)</td></tr>
  <tr><td><strong>Client-side</strong></td><td>gRPC, service mesh sidecars</td><td>Smart routing without single chokepoint</td></tr>
</tbody>
</table>
<p><strong>Algorithms:</strong></p>
<ul>
  <li><strong>Round-robin</strong> — simple, good default.</li>
  <li><strong>Least connections</strong> — routes to the instance with fewest in-flight requests. Better when request durations vary.</li>
  <li><strong>Least response time / EWMA</strong> — adapts to instance slowness; best for heterogeneous fleets.</li>
  <li><strong>Random with two choices (P2C)</strong> — Google's go-to for load balancers; as good as least-conn with less coordination.</li>
  <li><strong>IP hash / consistent hash</strong> — sticky sessions (avoid), cache locality (good).</li>
  <li><strong>Weighted</strong> — used during canary or when instances differ in size.</li>
</ul>
<pre><code># Nginx L7 — least-conn with health checks
upstream api {
  least_conn;
  keepalive 64;
  server 10.0.1.10:3000 max_fails=3 fail_timeout=10s;
  server 10.0.1.11:3000 max_fails=3 fail_timeout=10s;
  server 10.0.1.12:3000 max_fails=3 fail_timeout=10s;
}
server {
  listen 443 ssl http2;
  location / {
    proxy_pass http://api;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_next_upstream error timeout http_502 http_503;
  }
}</code></pre>
<ul>
  <li><strong>Health checks:</strong> expose <code>/health</code> (liveness) and <code>/ready</code> (drain-aware); LB polls and removes unhealthy targets.</li>
  <li><strong>Graceful shutdown:</strong> on SIGTERM, fail <code>/ready</code> first (so LB stops sending), drain in-flight, then exit. Prevents request loss on deploy.</li>
  <li><strong>Stateless app</strong> is the prerequisite — no in-memory sessions (Redis/JWT instead), uploads to S3, WebSockets via Redis adapter. Then any request can hit any replica.</li>
  <li><strong>Sticky sessions:</strong> avoid unless forced. They break autoscaling and uneven loads. If using WebSockets, prefer Redis adapter over stickiness.</li>
  <li><strong>Autoscaling:</strong> tie to CPU + RPS + queue depth. Set conservative min replicas for burst tolerance.</li>
  <li><strong>Canary / blue-green</strong> at the LB layer: weighted routing to shift % of traffic; automatic rollback on SLO breach.</li>
</ul>
<p><strong>Typical prod stack:</strong> cloud LB (TLS + geo) → ingress controller (path routing) → K8s services → pods (one Node process each). Managed LBs (ALB, GCP LB, Cloudflare) beat self-hosted for reliability unless you have very specific needs.</p>
'''

ANSWERS[99] = r'''
<p>Microservices split an application into independently deployable, loosely coupled services, each owning its data and one domain capability. They pay off for <em>organizational scale</em> (many teams shipping in parallel) more than for <em>technical scale</em> — a well-tuned monolith outperforms most microservice fleets.</p>
<p><strong>When to split:</strong> teams blocking each other on one codebase; different parts need different scaling/runtime; compliance boundaries; you can staff platform + observability teams. <strong>When not to split:</strong> small team, unclear domain boundaries, no operational maturity — start monolith-first.</p>
<table>
<thead><tr><th>Concern</th><th>Pattern / Tech</th></tr></thead>
<tbody>
  <tr><td><strong>Boundaries</strong></td><td>Domain-driven design (bounded contexts)</td></tr>
  <tr><td><strong>Inter-service</strong></td><td>REST for external, gRPC/Connect for internal, events (Kafka/NATS/SQS) for async</td></tr>
  <tr><td><strong>API gateway</strong></td><td>Kong, Envoy, AWS API Gateway, Tyk — single front door, auth, rate limit</td></tr>
  <tr><td><strong>Service discovery</strong></td><td>Kubernetes DNS + Service, Consul, Eureka</td></tr>
  <tr><td><strong>Data consistency</strong></td><td>One DB per service; Saga pattern for distributed txns; outbox pattern for reliable events</td></tr>
  <tr><td><strong>Observability</strong></td><td>OpenTelemetry (traces), Prometheus + Grafana (metrics), Loki/ELK/Datadog (logs), correlation IDs</td></tr>
  <tr><td><strong>Resilience</strong></td><td>Circuit breaker (<code>cockatiel</code>), retry with jitter, timeouts, bulkheads</td></tr>
  <tr><td><strong>Service mesh</strong></td><td>Istio, Linkerd — mTLS, retries, traffic splitting without app code</td></tr>
  <tr><td><strong>Config</strong></td><td>External (Consul, AppConfig, K8s ConfigMap), feature flags</td></tr>
  <tr><td><strong>CI/CD</strong></td><td>Per-service pipeline; contract testing (Pact)</td></tr>
</tbody>
</table>
<pre><code>// Node microservice with OpenTelemetry, circuit breaker, typed HTTP
import express from "express";
import { context, trace } from "@opentelemetry/api";
import { circuitBreaker, retry, handleAll, ExponentialBackoff } from "cockatiel";

const downstream = circuitBreaker(handleAll, {
  halfOpenAfter: 10_000,
  breaker: new ConsecutiveBreaker(5),
});
const retryPolicy = retry(handleAll, { maxAttempts: 3, backoff: new ExponentialBackoff() });

async function callOrderService(userId, traceparent) {
  const span = trace.getTracer("billing").startSpan("call.order");
  try {
    return await retryPolicy.execute(() =&gt;
      downstream.execute(() =&gt;
        fetch(`http://order/api/orders?userId=${userId}`, {
          headers: { traceparent },
          signal: AbortSignal.timeout(2000),
        }).then(r =&gt; r.ok ? r.json() : Promise.reject(new Error(`status ${r.status}`)))
      )
    );
  } finally { span.end(); }
}</code></pre>
<p><strong>Critical patterns:</strong></p>
<ul>
  <li><strong>Saga</strong> for multi-service business transactions (orchestrator or choreography); never distributed 2PC.</li>
  <li><strong>Outbox</strong> to publish events reliably after DB commits (skip the "dual write" problem).</li>
  <li><strong>Idempotency keys</strong> on every external API — at-least-once delivery means duplicates are normal.</li>
  <li><strong>Contract testing</strong> (Pact) catches breaking changes without full integration envs.</li>
  <li><strong>Correlation IDs</strong> propagated via <code>traceparent</code> across every hop — a single request's journey is reconstructable.</li>
  <li><strong>Platform tooling:</strong> service templates, shared logging/metrics libs, standardized healthchecks — services shouldn't reinvent these.</li>
</ul>
<p><strong>Modular monolith first.</strong> Enforce module boundaries inside one deployable; extract a service only when you've proven (a) independent scaling need, (b) different lifecycle, or (c) team ownership. The premature split is the classic microservices tax.</p>
'''

ANSWERS[100] = r'''
<p>Large-scale data processing in Node is less about raw compute (use Python, Spark, or DuckDB for analytics) and more about <strong>orchestrating I/O-heavy ETL and stream pipelines</strong> efficiently. Node's stream model and single-threaded event loop shine for pipeline coordination and don't shine for CPU-bound number-crunching.</p>
<table>
<thead><tr><th>Pattern</th><th>Tools</th><th>Use</th></tr></thead>
<tbody>
  <tr><td><strong>Streaming pipeline</strong></td><td><code>node:stream</code> + <code>pipeline</code>, <code>csv-parse</code>, <code>JSONStream</code>, <code>fast-csv</code></td><td>Transform &gt;GB files with MB RAM</td></tr>
  <tr><td><strong>Parallel work</strong></td><td><code>worker_threads</code>, <code>piscina</code>, <code>tinypool</code></td><td>CPU-bound (parse, hash, image resize)</td></tr>
  <tr><td><strong>Distributed jobs</strong></td><td>BullMQ, Temporal, AWS Step Functions</td><td>Batch jobs across replicas</td></tr>
  <tr><td><strong>Stream events</strong></td><td>Kafka + kafkajs, Redis Streams, NATS JetStream</td><td>Real-time event processing</td></tr>
  <tr><td><strong>DB batching</strong></td><td>Bulk COPY (pg), <code>insertMany</code> (mongo), chunked commits</td><td>Large writes; 100-1000x faster than per-row</td></tr>
  <tr><td><strong>External engines</strong></td><td>DuckDB (embedded OLAP), ClickHouse, Snowflake, BigQuery</td><td>Analytics; Node orchestrates</td></tr>
</tbody>
</table>
<pre><code>// Classic streaming ETL: huge CSV → transform → Postgres COPY
import { pipeline } from "node:stream/promises";
import { createReadStream } from "node:fs";
import { parse } from "csv-parse";
import { pool } from "./db.js";
import copyFrom from "pg-copy-streams";

await pool.query("CREATE TEMP TABLE stage (id bigint, email text, amount numeric)");
const client = await pool.connect();

try {
  const ingest = client.query(copyFrom.from("COPY stage (id, email, amount) FROM STDIN CSV"));
  await pipeline(
    createReadStream("events.csv"),
    parse({ columns: true, trim: true }),
    async function* (src) {                           // transform stage
      for await (const row of src) {
        if (!row.email?.includes("@")) continue;
        yield `${row.id},${row.email.toLowerCase()},${Number(row.amount).toFixed(2)}\n`;
      }
    },
    ingest,
  );
  await client.query(`INSERT INTO events SELECT * FROM stage ON CONFLICT (id) DO NOTHING`);
} finally { client.release(); }</code></pre>
<pre><code>// Parallel CPU work across worker threads (piscina pool)
import Piscina from "piscina";
const pool = new Piscina({ filename: "./hash-worker.js", maxThreads: 8 });

const results = await Promise.all(
  files.map(f =&gt; pool.run({ path: f }))   // each offloaded to a worker
);

// Stream processing with Kafka — consumer groups for horizontal scale
import { Kafka } from "kafkajs";
const kafka = new Kafka({ brokers: [...], clientId: "etl" });
const consumer = kafka.consumer({ groupId: "analytics", maxInFlightRequests: 200 });
await consumer.subscribe({ topic: "events" });
await consumer.run({
  eachBatchAutoResolve: false,
  eachBatch: async ({ batch, resolveOffset, heartbeat }) =&gt; {
    const rows = batch.messages.map(m =&gt; JSON.parse(m.value));
    await db.events.createMany({ data: rows });       // bulk insert
    for (const m of batch.messages) resolveOffset(m.offset);
    await heartbeat();
  },
});</code></pre>
<ul>
  <li><strong>Stream, don't load.</strong> Any file or result set large enough to matter should be consumed chunk-by-chunk — pipeline() handles backpressure, errors, and teardown.</li>
  <li><strong>Bulk writes.</strong> One INSERT per row is the #1 ETL killer. Batch 1k-10k rows per round trip; use <code>COPY</code> on Postgres for maximum throughput.</li>
  <li><strong>Shard + parallelize.</strong> Partition input by key, run N workers/replicas, each independent. Queue-based worker fleets (BullMQ) scale linearly.</li>
  <li><strong>Checkpoints + resumability.</strong> Track last processed offset/timestamp so restarts don't reprocess (or reprocess idempotently).</li>
  <li><strong>Backoff + DLQ.</strong> Transient errors retry; poison messages move to a dead-letter queue for inspection.</li>
  <li><strong>Know the limits.</strong> CPU-bound per-record transforms (parsing, regex, image ops) belong in <code>worker_threads</code>; true analytical queries belong in DuckDB / ClickHouse / BigQuery, with Node as the orchestrator.</li>
  <li><strong>Observability:</strong> records/sec, lag, error rate, p99 processing time — without these you're flying blind on a 12-hour batch job.</li>
</ul>
<p><strong>Orchestrate, don't compute.</strong> Node's best role in data pipelines is moving bytes fast, coordinating workers, and calling specialized engines — not as the math kernel.</p>
'''
