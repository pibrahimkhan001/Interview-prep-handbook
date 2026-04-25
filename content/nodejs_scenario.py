"""Node.Js / Scenario Based — detailed answers."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>Situation:</strong> users upload files up to a few hundred MB; must be secure, memory-efficient, and survive abusive clients.</p>
<p><strong>Approach:</strong> stream the multipart body directly to object storage (S3/GCS) rather than buffering through Node, so request memory stays flat regardless of file size.</p>
<pre><code>import Busboy from "busboy";
import { Upload } from "@aws-sdk/lib-storage";
import { S3Client } from "@aws-sdk/client-s3";
import { fileTypeFromStream } from "file-type";

const s3 = new S3Client({ region: "us-east-1" });
const ALLOWED = new Set(["image/png", "image/jpeg", "application/pdf"]);

app.post("/upload", requireAuth, (req, res, next) =&gt; {
  const bb = Busboy({
    headers: req.headers,
    limits: { fileSize: 200 * 1024 * 1024, files: 5, fields: 20 },
  });
  const uploads = [];
  let rejected = false;

  bb.on("file", async (name, stream, info) =&gt; {
    // Peek first bytes to verify real MIME from magic bytes, not header
    const type = await fileTypeFromStream(stream);
    if (!type || !ALLOWED.has(type.mime)) {
      rejected = true; stream.resume(); return;   // drain but drop
    }
    const key = `u/${req.user.id}/${Date.now()}-${info.filename.replace(/[^a-z0-9.\-_]/gi, "_")}`;
    uploads.push(
      new Upload({ client: s3, params: { Bucket: "uploads", Key: key, Body: stream, ContentType: type.mime, ServerSideEncryption: "AES256" } }).done()
    );
  });
  bb.on("filesLimit", () =&gt; { rejected = true; });
  bb.on("close", async () =&gt; {
    if (rejected) return res.status(400).json({ error: "invalid file" });
    const results = await Promise.all(uploads);
    res.json({ files: results.map(r =&gt; r.Key) });
  });
  req.pipe(bb);
});</code></pre>
<p><strong>Trade-offs:</strong> streaming prevents OOM but means you can only validate <em>content</em> (magic bytes, virus scan) as bytes arrive — for very strict workflows, <strong>pre-signed S3 PUT URLs</strong> are better: client uploads directly, your server never touches the bytes. For small files (&lt;5 MB) and simple flows, <code>multer</code> with memory storage is faster to write. Always: <code>helmet</code> for headers, per-user size/count quotas, antivirus (ClamAV) for user-sourced files, scan metadata separately in DB, store originals in private bucket and serve via short-lived signed URLs.</p>
'''

ANSWERS[2] = r'''
<p><strong>Situation:</strong> a 50+ route API with auth, billing, notifications, multi-tenant data — multiple engineers committing daily.</p>
<p><strong>Approach:</strong> modular monolith with <em>feature-first</em> folders, shared core, strict import boundaries, and a thin composition root.</p>
<pre><code>src/
├── app.ts                        // wires everything; only file that imports across features
├── server.ts                     // boot + graceful shutdown
├── core/                         // cross-cutting, no feature logic
│   ├── config.ts                 // Zod-validated env
│   ├── logger.ts                 // pino instance
│   ├── errors.ts                 // AppError, typed errors
│   ├── middleware/               // auth, rate-limit, errorHandler
│   └── db/                       // pool, migrations
├── features/
│   ├── users/
│   │   ├── user.routes.ts
│   │   ├── user.controller.ts
│   │   ├── user.service.ts       // business logic
│   │   ├── user.repo.ts          // DB layer
│   │   ├── user.schema.ts        // Zod DTOs
│   │   └── user.test.ts
│   ├── billing/   ...
│   └── notifications/  ...
├── integrations/                 // 3rd-party clients (stripe, ses)
└── jobs/                         // BullMQ workers</code></pre>
<p><strong>Rules:</strong> features never import from each other — cross-feature calls go through a small <code>events</code> bus or a published service interface. <code>core/</code> imports nothing from features. Use path aliases (<code>@core/*</code>, <code>@features/*</code>) and ESLint's <code>no-restricted-imports</code> to enforce boundaries at CI time.</p>
<p><strong>Trade-offs:</strong> feature-first beats layer-first (controllers/, services/, models/) at scale — related code moves together, new hires ramp in one folder. Keep it a monolith until a feature earns extraction (independent scaling, team ownership, different lifecycle). For giant monorepos, graduate to pnpm workspaces with packages like <code>@app/users</code>, <code>@app/billing</code> — same boundaries, now enforced by the package manager. Add <code>tsconfig</code> project references, Turborepo/Nx for build caching. Don't reach for NestJS just for structure — the convention above gives you the benefits without the framework lock-in.</p>
'''

ANSWERS[3] = r'''
<p><strong>Situation:</strong> a REST API serving a web app and mobile clients needs login, role-gated endpoints, and session lifecycle.</p>
<p><strong>Approach:</strong> issue a short-lived access token (JWT, 15 min) and an opaque refresh token (random, stored server-side in Redis or DB), with refresh rotation and revocation list.</p>
<pre><code>// Login — verify password, issue tokens
app.post("/auth/login", async (req, res) =&gt; {
  const { email, password } = LoginSchema.parse(req.body);
  const user = await userRepo.findByEmail(email);
  if (!user || !(await argon2.verify(user.passwordHash, password))) {
    return res.status(401).json({ error: "invalid credentials" });
  }
  const accessToken = jwt.sign({ sub: user.id, role: user.role }, JWT_SECRET, { expiresIn: "15m", issuer: "api" });
  const refreshToken = crypto.randomBytes(32).toString("base64url");
  await redis.set(`rt:${refreshToken}`, user.id, "EX", 30 * 24 * 3600);
  res.cookie("rt", refreshToken, { httpOnly: true, secure: true, sameSite: "strict", path: "/auth/refresh" })
     .json({ accessToken, user: pub(user) });
});

// Authenticate middleware — verify JWT on every protected call
export const requireAuth = (req, res, next) =&gt; {
  const bearer = req.headers.authorization?.slice("Bearer ".length);
  try {
    req.user = jwt.verify(bearer, JWT_SECRET, { issuer: "api" });
    next();
  } catch { res.status(401).json({ error: "invalid token" }); }
};

// Authorize — coarse role check, or CASL for fine-grained
export const requireRole = (...roles) =&gt; (req, res, next) =&gt;
  roles.includes(req.user?.role) ? next() : res.status(403).json({ error: "forbidden" });

app.delete("/posts/:id", requireAuth, requireRole("admin", "editor"), postCtrl.remove);</code></pre>
<p><strong>Trade-offs:</strong> JWT for access tokens means stateless verification (any replica accepts it) but you can't revoke mid-session — keep them short. Refresh tokens in Redis give you revocation and rotation. For browsers, prefer httpOnly cookies over <code>localStorage</code> to prevent XSS token theft; protect with sameSite + CSRF tokens. For SSO / federated login, add <code>openid-client</code> (OAuth2 + OIDC). Fine-grained permissions (per-resource ACL) belong in <strong>CASL</strong> or <strong>Casbin</strong>, not in JWT claims. Always Argon2id for password hashing, never bcrypt's older defaults or SHA+salt.</p>
'''

ANSWERS[4] = r'''
<p><strong>Situation:</strong> public API exposed to bots and scrapers; need to cap per-IP, per-user, and per-endpoint traffic without hurting legitimate users.</p>
<p><strong>Approach:</strong> layered defense — edge CDN/WAF first (cheapest, blocks obvious floods), then per-tier app-level limits backed by Redis so all replicas share state.</p>
<pre><code>import { rateLimit, ipKeyGenerator } from "express-rate-limit";
import { RedisStore } from "rate-limit-redis";
import Redis from "ioredis";
const redis = new Redis(process.env.REDIS_URL);

// Strict on auth endpoints — prevent credential stuffing
const authLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...a) =&gt; redis.call(...a), prefix: "rl:auth:" }),
  windowMs: 15 * 60_000,
  limit: 10,
  keyGenerator: (req) =&gt; `${ipKeyGenerator(req)}:${req.body?.email ?? ""}`,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: { error: "too many login attempts" },
});

// General API — 600 req/min per user if logged in, per IP otherwise
const apiLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...a) =&gt; redis.call(...a), prefix: "rl:api:" }),
  windowMs: 60_000, limit: 600,
  keyGenerator: (req) =&gt; req.user?.id ?? ipKeyGenerator(req),
});

app.use("/auth", authLimiter);
app.use("/api", apiLimiter);

// For fine control (sliding window, burst + sustained), use ioredis Lua atomically
const slidingWindow = `
  local now = tonumber(ARGV[1]); local win = tonumber(ARGV[2]); local max = tonumber(ARGV[3])
  redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, now - win)
  local c = redis.call("ZCARD", KEYS[1])
  if c &lt; max then redis.call("ZADD", KEYS[1], now, now); redis.call("EXPIRE", KEYS[1], math.ceil(win/1000)); return {1, max-c-1} end
  return {0, 0}`;</code></pre>
<p><strong>Trade-offs:</strong> <em>fixed window</em> (express-rate-limit default) is cheapest but lets a burst double the limit at window edges. <em>Sliding window</em> (ZSET or token bucket) is smoother but costlier. <em>Token bucket</em> allows bursts while enforcing average — ideal for customer APIs. <strong>Fail open</strong> if Redis is down (otherwise a Redis blip takes your API offline) — but alarm on it. Return <code>429</code> with <code>Retry-After</code> and rate headers. For tiered SaaS, key by <code>tenantId:plan</code> and load plan limits. Stop abuse at the <strong>edge</strong> first (Cloudflare WAF, AWS WAF) — Node-level limiting wastes CPU on requests you could drop for free upstream.</p>
'''

ANSWERS[5] = r'''
<p><strong>Situation:</strong> API response times creeping up; most requests re-execute the same expensive queries for data that rarely changes.</p>
<p><strong>Approach:</strong> multi-tier cache — local (per-process, nanosecond) for hot config, distributed (Redis, sub-ms) for shared state, HTTP/CDN (edge) for public responses. Apply <em>cache-aside</em> with short TTLs + explicit invalidation.</p>
<pre><code>import { LRUCache } from "lru-cache";
import Redis from "ioredis";
const local = new LRUCache({ max: 1000, ttl: 60_000 });   // L1
const redis = new Redis(process.env.REDIS_URL);           // L2

const inflight = new Map();  // singleflight — prevent thundering herd
export async function getProduct(id) {
  const key = `p:${id}`;
  if (local.has(key)) return local.get(key);
  const cached = await redis.get(key);
  if (cached) { const v = JSON.parse(cached); local.set(key, v); return v; }
  if (inflight.has(key)) return inflight.get(key);
  const p = (async () =&gt; {
    const row = await db.product.findUnique({ where: { id } });
    await redis.set(key, JSON.stringify(row), "EX", 300 + Math.random() * 30); // jitter
    local.set(key, row);
    inflight.delete(key);
    return row;
  })();
  inflight.set(key, p);
  return p;
}
export async function updateProduct(id, patch) {
  const row = await db.product.update({ where: { id }, data: patch });
  await redis.del(`p:${id}`);        // explicit bust
  local.delete(`p:${id}`);
  await redis.publish("inv", `p:${id}`);  // tell other replicas
  return row;
}
redis.duplicate().subscribe("inv").then(sub =&gt; sub.on("message", (_, key) =&gt; local.delete(key)));

// HTTP layer — public responses cached by CDN
app.get("/api/products/:id", async (req, res) =&gt; {
  res.set("Cache-Control", "public, max-age=60, stale-while-revalidate=300");
  res.json(await getProduct(req.params.id));
});</code></pre>
<p><strong>Trade-offs:</strong> L1 gives speed but each replica has its own copy — use pub/sub to invalidate across nodes. Short TTL + jitter prevents synchronized expiry storms. <em>Stale-while-revalidate</em> in HTTP cache-control makes CDN serve stale content instantly while refreshing in background. Cache what's <em>read-heavy</em> and <em>bounded</em>; caching 1 ms queries adds latency without benefit. For per-user data, scope keys by <code>userId</code>; for tenant data, by <code>tenantId</code>. Measure hit rate — &lt; 80% and you're mostly adding cost. Never cache error responses by default. For write-heavy paths, use <strong>write-through</strong> or skip caching entirely.</p>
'''

ANSWERS[6] = r'''
<p><strong>Situation:</strong> multi-room chat with presence, typing indicators, history, scaling across replicas.</p>
<p><strong>Approach:</strong> Socket.IO with a Redis adapter so any replica can broadcast to any client; JWT for upgrade-time auth; Postgres for history, Redis for presence.</p>
<pre><code>import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
import Redis from "ioredis";
import jwt from "jsonwebtoken";

const pub = new Redis(process.env.REDIS_URL); const sub = pub.duplicate();
const io = new Server(httpServer, { cors: { origin: process.env.ORIGIN } });
io.adapter(createAdapter(pub, sub));

io.use((socket, next) =&gt; {  // auth at handshake
  try { socket.data.user = jwt.verify(socket.handshake.auth.token, JWT_SECRET); next(); }
  catch { next(new Error("unauthorized")); }
});

io.on("connection", async (socket) =&gt; {
  const { id: userId, name } = socket.data.user;
  socket.join(`user:${userId}`);
  await pub.sadd("online", userId); io.emit("presence", { userId, online: true });

  socket.on("room:join", async (roomId) =&gt; {
    if (!await canJoin(userId, roomId)) return socket.emit("error", "forbidden");
    socket.join(`room:${roomId}`);
    const last50 = await db.message.findMany({ where: { roomId }, take: 50, orderBy: { id: "desc" } });
    socket.emit("history", last50.reverse());
  });

  socket.on("message:send", async ({ roomId, body }) =&gt; {
    const text = sanitize(body).slice(0, 4000);
    const msg = await db.message.create({ data: { roomId, userId, body: text } });
    io.to(`room:${roomId}`).emit("message:new", msg);    // broadcast via Redis to all replicas
  });

  socket.on("typing", ({ roomId, typing }) =&gt; {
    socket.to(`room:${roomId}`).emit("typing", { userId, name, typing });
  });

  socket.on("disconnect", async () =&gt; {
    await pub.srem("online", userId);
    io.emit("presence", { userId, online: false });
  });
});</code></pre>
<p><strong>Trade-offs:</strong> Socket.IO gives rooms, reconnect, fallbacks, and a mature adapter ecosystem — worth the overhead vs raw <code>ws</code>. Redis adapter scales horizontally (messages fan out across replicas via pub/sub); for &gt; 100k concurrent connections per node, switch to <code>uWebSockets.js</code>. Persist to Postgres (or DynamoDB for write-heavy); use Redis sorted sets for recent-history cache. Typing indicators via <code>socket.to(room)</code> (excludes sender). For mobile, complement with push notifications when user is offline. Enforce per-room rate limits (Redis Lua) to stop spam. For E2E encryption, let clients encrypt; server just relays ciphertext. Handle presence <strong>races</strong> across reconnects with a debounced online counter (<code>ZADD</code> + TTL), not a bare flag.</p>
'''

ANSWERS[7] = r'''
<p><strong>Situation:</strong> production API with unknown error rate, intermittent 500s users complain about but nothing in local logs.</p>
<p><strong>Approach:</strong> structured JSON logs with correlation IDs → log aggregator; metrics (RED: Rate, Errors, Duration) → Prometheus/Grafana; traces → OpenTelemetry; error tracker (Sentry) for release-aware grouping.</p>
<pre><code>import pino from "pino";
import pinoHttp from "pino-http";
import * as Sentry from "@sentry/node";
import { AsyncLocalStorage } from "node:async_hooks";
import client from "prom-client";
import crypto from "node:crypto";

Sentry.init({ dsn: process.env.SENTRY_DSN, tracesSampleRate: 0.1, environment: process.env.NODE_ENV, release: process.env.GIT_SHA });

const als = new AsyncLocalStorage();
const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  redact: ["req.headers.authorization", "req.headers.cookie", "password", "token", "*.secret"],
  mixin: () =&gt; als.getStore() ?? {},
  formatters: { level: (l) =&gt; ({ level: l }) },
});

app.use((req, res, next) =&gt; {
  const reqId = req.headers["x-request-id"] ?? crypto.randomUUID();
  res.setHeader("x-request-id", reqId);
  als.run({ reqId, userId: req.user?.id, tenantId: req.user?.tenantId }, next);
});
app.use(pinoHttp({ logger, customLogLevel: (_, res, err) =&gt; err || res.statusCode &gt;= 500 ? "error" : res.statusCode &gt;= 400 ? "warn" : "info" }));

// Metrics
const httpDuration = new client.Histogram({
  name: "http_request_duration_seconds",
  labelNames: ["method", "route", "status"],
  buckets: [0.01, 0.05, 0.1, 0.3, 1, 3, 10],
});
app.use((req, res, next) =&gt; {
  const end = httpDuration.startTimer({ method: req.method });
  res.on("finish", () =&gt; end({ route: req.route?.path ?? "unmatched", status: res.statusCode }));
  next();
});
app.get("/metrics", async (_, res) =&gt; res.type(client.register.contentType).send(await client.register.metrics()));

// Errors → Sentry + structured log (never swallow)
app.use(Sentry.Handlers.errorHandler());
app.use((err, req, res, _) =&gt; {
  logger.error({ err, reqId: als.getStore()?.reqId }, "unhandled");
  res.status(err.status ?? 500).json({ error: err.expose ? err.message : "internal", reqId: als.getStore()?.reqId });
});</code></pre>
<p><strong>Trade-offs:</strong> stdout JSON + aggregator (CloudWatch, Loki, Datadog) beats writing to files — works in containers, centralized, searchable. Correlation IDs let you follow one request across services. Redact <strong>before</strong> logs leave the process — a single <code>console.log(req.headers)</code> in an error path leaks tokens to Datadog. Sample traces (10%) and logs (never DEBUG in prod) to control cost. Alert on SLO burn (error rate, p99 latency) — not absolute thresholds. Add <strong>health</strong> (<code>/health</code>) and <strong>readiness</strong> (<code>/ready</code>) probes for the orchestrator. <strong>uncaughtException</strong> and <strong>unhandledRejection</strong> → log and exit (let the supervisor restart); continuing in an unknown state is worse than a restart.</p>
'''

ANSWERS[8] = r'''
<p><strong>Situation:</strong> going from 100 RPS to 5,000+ RPS; current deployment is a single Node process behind an ALB, showing CPU pegged and slow DB queries.</p>
<p><strong>Approach:</strong> systematically work the bottleneck stack — profile, fix hot queries, pool connections, scale horizontally, cache, and offload async work. Don't micro-optimize JS; the wins are always at I/O and DB.</p>
<pre><code>// 1. One Node per core (K8s replicas or cluster)
//    - Stateless app: sessions in Redis/JWT, uploads to S3, WebSockets via Redis adapter
//    - Graceful shutdown on SIGTERM: stop accepting, drain in-flight, close DB pool

// 2. DB — usually #1 bottleneck
//    - Indexes for every WHERE/ORDER BY; EXPLAIN ANALYZE slow queries
//    - Connection pool: pool.max &lt;= (db.max_connections / total_replicas)
//    - Read replicas for heavy reads; write goes to primary
//    - Avoid N+1: DataLoader or batched query/IN clauses
import { Pool } from "pg";
const pool = new Pool({ connectionString, max: 20, idleTimeoutMillis: 30_000, statement_timeout: 5000 });

// 3. Cache hot reads
const redis = new Redis.Cluster([...]);  // share across replicas
// cache-aside with singleflight + TTL jitter (see strategies in Q5)

// 4. Keep-alive for outbound HTTP (huge)
import { setGlobalDispatcher, Agent } from "undici";
setGlobalDispatcher(new Agent({ connections: 128, keepAliveTimeout: 30_000 }));

// 5. Compression + HTTP/2 at the proxy (Nginx/ALB), not in Node
// 6. Offload async: BullMQ for emails, reports, webhooks — respond first
// 7. Backpressure + timeouts on every external call (AbortSignal.timeout)

// 8. Autoscale on CPU + RPS + queue depth
//    Min replicas = burst tolerance; max = DB connection budget</code></pre>
<p><strong>Trade-offs:</strong> scaling Node is almost always about scaling <em>out</em>, not up — one thread per process, one process per core. Profile first (<code>clinic doctor</code>, <code>0x</code>, <code>--inspect</code>); tuning without data wastes effort. Event loop utilization &gt; 0.8 means you're CPU-saturated — add replicas or move CPU work to <code>worker_threads</code>/<code>piscina</code>. If outbound HTTP is slow, you need <code>undici</code> pools + circuit breakers (<code>cockatiel</code>). Pre-cache at the edge (Cloudflare) — free horizontal scaling for public reads. Graceful shutdown on SIGTERM (drain inflight, close pool) prevents 502s during deploys. Measure p99 latency and error rate; set SLOs, then invest where they're at risk.</p>
'''

ANSWERS[9] = r'''
<p><strong>Situation:</strong> admin, editor, viewer roles plus resource-ownership rules ("editors can update their own posts"). RBAC alone is too coarse — reach for ABAC/CASL when rules touch attributes.</p>
<p><strong>Approach:</strong> role as a column on user, policies defined in <strong>CASL</strong> (declarative rules, conditions on resource attributes), middleware enforces ability per route.</p>
<pre><code>import { AbilityBuilder, createMongoAbility } from "@casl/ability";

// Central policy — single source of truth
export function defineAbilitiesFor(user) {
  const { can, cannot, build } = new AbilityBuilder(createMongoAbility);
  if (user.role === "admin") {
    can("manage", "all");                                   // do anything
  } else if (user.role === "editor") {
    can(["read", "create"], "Post");
    can(["update", "delete"], "Post", { authorId: user.id }); // only own
    can("read", "Comment");
  } else { // viewer
    can("read", "Post", { published: true });
    can("read", "Comment");
  }
  cannot("delete", "Post", { locked: true }).because("post is locked");
  return build();
}

// Middleware
export const authorize = (action, subject) =&gt; async (req, res, next) =&gt; {
  const ability = defineAbilitiesFor(req.user);
  let resource = subject;
  if (req.params.id &amp;&amp; typeof subject === "string") {
    resource = await db[subject.toLowerCase()].findUnique({ where: { id: req.params.id } });
    if (!resource) return res.status(404).end();
  }
  if (!ability.can(action, resource)) {
    return res.status(403).json({ error: "forbidden", reason: ability.rulesFor(action, subject)[0]?.reason });
  }
  req.resource = resource;
  next();
};

app.get("/posts", requireAuth, authorize("read", "Post"), async (req, res) =&gt; {
  const ability = defineAbilitiesFor(req.user);
  const filters = rulesToPrismaQuery(ability, "read", "Post");   // @casl/prisma
  res.json(await db.post.findMany({ where: filters }));          // DB-level filter
});
app.patch("/posts/:id", requireAuth, authorize("update", "Post"), postCtrl.update);</code></pre>
<p><strong>Trade-offs:</strong> plain role checks (<code>if (req.user.role === "admin")</code>) are fine for 3 roles and no attributes. Once you have "own resources only" or tenant scoping, spaghetti sets in — centralize in CASL. <strong>Casbin</strong> is a heavier alternative (supports ACL/RBAC/ABAC with policy files). For multi-tenant, always add a <code>tenantId</code> filter <em>in addition</em> to role checks — defense in depth. Pair with Postgres <strong>RLS</strong> for DB-enforced isolation. Never trust JWT claims alone for sensitive actions — check against the current DB row. Log every 403 with reason so you can spot over-restrictive rules and audit access denials.</p>
'''

ANSWERS[10] = r'''
<p><strong>Situation:</strong> same codebase deployed to dev/staging/prod, each with different DB URLs, API keys, feature flags, log levels.</p>
<p><strong>Approach:</strong> layered config — defaults → env-specific file → environment variables → secrets manager — validated at boot with Zod so typos fail fast.</p>
<pre><code>// config.ts — single typed config module, imported everywhere
import { z } from "zod";

const schema = z.object({
  NODE_ENV: z.enum(["development", "test", "staging", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  STRIPE_KEY: z.string().startsWith("sk_"),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  FEATURE_NEW_CHECKOUT: z.coerce.boolean().default(false),
  AWS_REGION: z.string().default("us-east-1"),
});

// In dev: Node 20.6+ has built-in dotenv, no package needed
// node --env-file=.env.local --env-file=.env server.js

// Parse + freeze — fail loudly on missing/malformed
const parsed = schema.safeParse(process.env);
if (!parsed.success) {
  console.error("[config] invalid environment:");
  for (const i of parsed.error.issues) console.error(`  ${i.path.join(".")}: ${i.message}`);
  process.exit(1);
}
export const config = Object.freeze(parsed.data);

// In production, secrets come from AWS Secrets Manager / SSM / Doppler, not .env
// Injected as env by the platform (ECS task def, K8s Secret → env, App Runner config source)</code></pre>
<p><strong>Layout:</strong></p>
<ul>
  <li><code>.env.example</code> — committed, every var listed, no real values.</li>
  <li><code>.env.local</code> — gitignored, developer's local secrets.</li>
  <li><code>.env.test</code> — test-environment overrides.</li>
  <li><strong>No</strong> <code>.env.production</code> file — prod secrets come from the secret manager at deploy time.</li>
</ul>
<p><strong>Trade-offs:</strong> storing config in env is the 12-factor default — portable, platform-native, works with every orchestrator. Secrets in env are acceptable for most apps but get rotated manually; use <strong>Secrets Manager/Vault</strong> for rotation, audit, and scoped access. Dynamic config (feature flags, timeouts you want to tune without redeploy) belongs in a <strong>config service</strong> (LaunchDarkly, AppConfig, Unleash) — not env. Never log <code>process.env</code>; pino's <code>redact</code> catches leaks. Validate at boot because a typo like <code>DATABSE_URL</code> should fail at startup, not at first query.</p>
'''

ANSWERS[11] = r'''
<p><strong>Situation:</strong> multi-developer Node service; manual deploys cause drift; bugs slip in because nobody ran tests before merging.</p>
<p><strong>Approach:</strong> GitHub Actions with OIDC (no long-lived cloud creds), caching, matrix testing, and automated promotion dev → staging → prod via canary.</p>
<pre><code># .github/workflows/ci.yml
name: CI/CD
on: { push: { branches: [main] }, pull_request: {} }
permissions: { id-token: write, contents: read, packages: write }

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: { image: postgres:16, env: { POSTGRES_PASSWORD: t }, ports: ["5432:5432"] }
      redis:    { image: redis:7, ports: ["6379:6379"] }
    strategy: { matrix: { node: [20, 22] } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '${{ matrix.node }}', cache: 'npm' }
      - run: npm ci
      - run: npm run lint &amp;&amp; npm run typecheck
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v4
      - run: npm audit --audit-level=high

  build:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE }}, aws-region: us-east-1 }   # OIDC, no secret keys
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -t $ECR_URL:$GITHUB_SHA .
          docker push $ECR_URL:$GITHUB_SHA
      - uses: aquasecurity/trivy-action@master           # image scan
        with: { image-ref: '${{ env.ECR_URL }}:${{ github.sha }}', severity: 'HIGH,CRITICAL', exit-code: '1' }

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production                              # requires manual approval via env rules
    steps:
      - run: ./scripts/canary-deploy.sh $GITHUB_SHA     # 10% traffic, auto-rollback on SLO breach</code></pre>
<p><strong>Trade-offs:</strong> OIDC (no AWS access keys in GitHub) is now standard — every team should migrate. Cache <code>~/.npm</code> by lockfile hash for sub-minute installs. Matrix on two Node versions catches LTS-specific bugs cheaply. <strong>Don't run tests <em>and</em> deploy from the same job</strong> — separate stages, each with least privilege. Automate dev deploys; gate prod with a manual approval or automatic canary (1% → 10% → 100% with SLO-based rollback). <strong>Run DB migrations before app deploy</strong>, and make them backward-compatible with both old and new app (expand-contract pattern). For monorepos, use Turborepo/Nx <code>--filter</code> + path filters so unrelated PRs don't retest the world. Keep end-to-end CI &lt; 5 min — anything slower gets ignored.</p>
'''

ANSWERS[12] = r'''
<p><strong>Situation:</strong> adding columns, backfills, renames, and constraint changes without downtime; multiple engineers committing schema changes.</p>
<p><strong>Approach:</strong> declarative migrations with a dedicated tool (Prisma Migrate / Knex / node-pg-migrate / db-migrate), SQL under version control, run in CI before app deploy. Follow <strong>expand → migrate → contract</strong> for zero downtime.</p>
<pre><code>// Prisma — declarative schema + generated SQL migrations
// prisma/schema.prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String
  createdAt DateTime @default(now())
  // ADDING a new column: must be NULLable OR have default (backward-compatible)
  phone     String?
}

// Dev: prisma migrate dev   — creates timestamped SQL migration
// CI/Prod: prisma migrate deploy   — applies pending migrations only</code></pre>
<pre><code>// Node-pg-migrate — SQL-first, more control
// migrations/20260418120000_add_user_phone.js
exports.up = (pgm) =&gt; {
  pgm.addColumn("users", { phone: { type: "text", notNull: false } });
  pgm.createIndex("users", "phone");
};
exports.down = (pgm) =&gt; pgm.dropColumn("users", "phone");

// migrations/20260418130000_backfill_and_enforce.js    — run AFTER app deploys
exports.up = async (pgm) =&gt; {
  await pgm.db.query(`UPDATE users SET phone = '' WHERE phone IS NULL`);
  pgm.alterColumn("users", "phone", { notNull: true });
};</code></pre>
<p><strong>Zero-downtime rename</strong> ("rename column X to Y"):</p>
<ol>
  <li><strong>Expand:</strong> migration adds <code>Y</code>, dual-writes in app (writes both X and Y).</li>
  <li><strong>Backfill:</strong> migration copies X → Y for existing rows.</li>
  <li><strong>Migrate reads:</strong> deploy app that reads from Y.</li>
  <li><strong>Contract:</strong> migration drops X.</li>
</ol>
<p><strong>Trade-offs:</strong> Prisma is great for TS codebases — typed client auto-regenerates on schema change. Knex/Kysely give more SQL control (good for complex Postgres features). <strong>Never edit an applied migration</strong> — add a new one. Run migrations in a separate CI step before the app rolls out, so app pods always see a newer-or-equal schema. For big backfills (millions of rows), use batched UPDATEs with sleeps — avoid locking. Use <code>CREATE INDEX CONCURRENTLY</code> on Postgres to avoid table locks. Test migration rollback in staging; in prod, roll <em>forward</em> (a fix migration) rather than rolling back — simpler to reason about. Tools like <strong>Liquibase/Atlas</strong> add DB drift detection if you have multi-service shared schemas.</p>
'''

ANSWERS[13] = r'''
<p><strong>Situation:</strong> public API receiving JSON from web clients and partner integrations — must reject malformed input, block XSS/SQL injection, and return structured errors for i18n.</p>
<p><strong>Approach:</strong> validate at the HTTP boundary with Zod; sanitize close to the sink (parameterized SQL always, <code>sanitize-html</code> on rich text); coerce/normalize before business logic sees the data.</p>
<pre><code>import { z } from "zod";
import sanitizeHtml from "sanitize-html";

// 1. Schemas define contract + types in one place
const AddressSchema = z.object({
  line1: z.string().trim().min(1).max(200),
  country: z.string().length(2).toUpperCase(),
  zip: z.string().max(20),
});
const CreateArticleSchema = z.object({
  title: z.string().trim().min(3).max(160),
  bodyHtml: z.string().max(100_000)
    .transform(v =&gt; sanitizeHtml(v, {
      allowedTags: ["p", "h2", "h3", "a", "ul", "ol", "li", "code", "pre", "strong", "em", "blockquote", "img"],
      allowedAttributes: { a: ["href", "rel"], img: ["src", "alt"] },
      allowedSchemes: ["https", "mailto"],
      transformTags: { a: (tag, attr) =&gt; ({ tagName: "a", attribs: { ...attr, rel: "noopener noreferrer" } }) },
    })),
  tags: z.array(z.string().min(1).max(30)).max(10).default([]),
  author: z.object({ id: z.string().uuid() }),
  address: AddressSchema.optional(),
}).strict();    // reject unknown keys — catches typos, blocks mass-assignment

type CreateArticle = z.infer&lt;typeof CreateArticleSchema&gt;;

// 2. Middleware — one factory, structured errors
const validate = (schema, where = "body") =&gt; (req, res, next) =&gt; {
  const r = schema.safeParse(req[where]);
  if (!r.success) return res.status(400).json({
    error: "VALIDATION_ERROR",
    issues: r.error.issues.map(i =&gt; ({ path: i.path.join("."), code: i.code, message: i.message })),
  });
  req[where] = r.data;          // typed, coerced
  next();
};

// 3. Parameterized queries — NEVER concatenate
app.post("/articles", requireAuth, validate(CreateArticleSchema), async (req, res) =&gt; {
  const { rows } = await pool.query(
    "INSERT INTO articles (title, body_html, author_id) VALUES ($1, $2, $3) RETURNING *",
    [req.body.title, req.body.bodyHtml, req.user.id],
  );
  res.status(201).json(rows[0]);
});</code></pre>
<p><strong>Trade-offs:</strong> Zod's type inference is the killer feature — one schema gives you runtime check + TS types + frontend (<code>react-hook-form</code> + <code>zodResolver</code>) + OpenAPI via <code>zod-to-openapi</code>. Joi is better if you're not on TS. <strong>Validate at every trust boundary</strong> — don't rely on "the frontend checked it." Strip unknown keys (<code>.strict()</code>) to prevent mass-assignment attacks that set admin flags. Sanitize HTML; never try to sanitize SQL by hand — use parameterized queries or an ORM (Prisma, Knex) that parameterizes for you. For Mongo, strip keys starting with <code>$</code> from user JSON (<code>express-mongo-sanitize</code>) to block operator injection. Return <strong>structured errors</strong> (path + code + message) so clients can localize. Never echo user input into error messages without escaping.</p>
'''

ANSWERS[14] = r'''
<p><strong>Situation:</strong> horizontally scaled API with login — need session persistence across replicas, logout that actually revokes, and low-latency reads on every request.</p>
<p><strong>Approach:</strong> store session data in Redis (sub-ms reads, shared across replicas), keep only the session ID in a signed httpOnly cookie, use <code>connect-redis</code> with Express session middleware.</p>
<pre><code>import session from "express-session";
import RedisStore from "connect-redis";
import { createClient } from "redis";

const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

app.set("trust proxy", 1);        // behind a proxy — cookie.secure relies on req.protocol
app.use(session({
  store: new RedisStore({ client: redisClient, prefix: "sess:", ttl: 24 * 3600 }),
  name: "sid",                    // don't leak framework with "connect.sid"
  secret: process.env.SESSION_SECRET,    // rotate periodically; support old+new with array
  resave: false,
  saveUninitialized: false,        // only create row on actual login
  rolling: true,                   // refresh TTL on every request (sliding expiry)
  cookie: { httpOnly: true, secure: true, sameSite: "lax", maxAge: 24 * 3600 * 1000 },
}));

// Login — store user info + mitigations
app.post("/login", async (req, res) =&gt; {
  const user = await authenticate(req.body);
  req.session.regenerate((err) =&gt; {       // prevent session fixation
    if (err) return res.status(500).end();
    req.session.userId = user.id;
    req.session.ip = req.ip;
    req.session.ua = req.get("user-agent");
    req.session.save(() =&gt; res.json({ user: pub(user) }));
  });
});

// Logout — destroy server-side, clear cookie
app.post("/logout", (req, res) =&gt; {
  req.session.destroy(() =&gt; res.clearCookie("sid").json({ ok: true }));
});

// List active sessions (for "sign out other devices")
// Use Redis SCAN on prefix sess:* with userId filter, or maintain sess-by-user set
app.get("/sessions", requireAuth, async (req, res) =&gt; {
  const ids = await redisClient.sMembers(`user-sessions:${req.user.id}`);
  const sessions = await Promise.all(ids.map(id =&gt; redisClient.get(`sess:${id}`).then(JSON.parse)));
  res.json(sessions.filter(Boolean));
});</code></pre>
<p><strong>Trade-offs:</strong> server-side sessions in Redis are ideal when you need <strong>revocation</strong> (logout, admin kick), <strong>device management</strong> (list/kill sessions), or session data too large for a cookie. Cookies are signed but opaque — never encode trust data in them. <strong>JWTs are the alternative</strong>: stateless, no lookup per request, but you can't revoke mid-lifetime (use short expiry + refresh token). For APIs used by mobile, JWT + refresh tokens are cleaner; for browser apps, Redis sessions keep things simple. Always <code>regenerate()</code> on privilege changes to prevent fixation. Use <code>sameSite=lax</code> for most apps, <code>strict</code> for sensitive flows (banking). <strong>Redis Cluster</strong> or Sentinel for HA — a Redis outage means all users log out. For extreme scale (&gt; 100k concurrent sessions), consider Upstash or Memorystore with replica reads.</p>
'''

ANSWERS[15] = r'''
<p><strong>Situation:</strong> storing sensitive user documents (passports, tax forms, medical records); files must be encrypted at rest and decryptable only by authorized users.</p>
<p><strong>Approach:</strong> AES-256-GCM for file encryption (authenticated — detects tampering), keys managed by KMS (AWS KMS, GCP KMS, Azure Key Vault, HashiCorp Vault) via envelope encryption. Never roll your own crypto.</p>
<pre><code>import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";
import { KMSClient, GenerateDataKeyCommand, DecryptCommand } from "@aws-sdk/client-kms";
import { pipeline } from "node:stream/promises";
import { createReadStream, createWriteStream } from "node:fs";

const kms = new KMSClient({});
const KEY_ID = process.env.KMS_KEY_ID;

// Encrypt — envelope encryption: KMS generates a data key, we encrypt file with plaintext, store ciphertext blob
export async function encryptFile(inPath, outPath) {
  const { Plaintext, CiphertextBlob } = await kms.send(new GenerateDataKeyCommand({
    KeyId: KEY_ID, KeySpec: "AES_256",
  }));
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", Plaintext, iv);
  await pipeline(createReadStream(inPath), cipher, createWriteStream(outPath));
  const tag = cipher.getAuthTag();
  // Store encryptedKey + iv + authTag alongside file (metadata in DB)
  return {
    encryptedKey: Buffer.from(CiphertextBlob).toString("base64"),
    iv: iv.toString("base64"),
    authTag: tag.toString("base64"),
  };
}

// Decrypt — ask KMS to unwrap the data key (requires IAM permission)
export async function decryptFile(inPath, outPath, meta) {
  const { Plaintext } = await kms.send(new DecryptCommand({
    CiphertextBlob: Buffer.from(meta.encryptedKey, "base64"),
  }));
  const decipher = createDecipheriv("aes-256-gcm", Plaintext, Buffer.from(meta.iv, "base64"));
  decipher.setAuthTag(Buffer.from(meta.authTag, "base64"));
  await pipeline(createReadStream(inPath), decipher, createWriteStream(outPath));
}</code></pre>
<p><strong>Trade-offs:</strong> <strong>envelope encryption</strong> (data key encrypted by master key) scales better than asking KMS to encrypt each file — KMS has a request throttle and data size limits. <strong>AES-GCM</strong> is authenticated (integrity + confidentiality); CBC requires a separate MAC and is easy to misuse. Stream with <code>pipeline</code> — don't load multi-GB files into memory. For cloud storage, prefer <strong>SSE-S3</strong> (server-side managed) or <strong>SSE-KMS</strong> unless you need client-side encryption for compliance (you can do both — client-side GCM then SSE). Track key rotation: KMS auto-rotates master keys; your data keys can be re-wrapped lazily. Audit <code>DecryptCommand</code> calls (CloudTrail) — every decrypt is logged with caller identity. <strong>Never</strong> store keys in code, env vars, or the same bucket as the data; never roll your own AES. For password-based encryption (user-supplied password), derive with Argon2id, not plain hash.</p>
'''

ANSWERS[16] = r'''
<p><strong>Situation:</strong> serving a SPA's build output (HTML/CSS/JS, images) from Express — but also behind a CDN.</p>
<p><strong>Approach:</strong> let the CDN/proxy handle static serving for production; use <code>express.static</code> with aggressive cache headers for dev and small deployments. Never hand-roll <code>fs</code>-based static serving.</p>
<pre><code>import express from "express";
import compression from "compression";
import helmet from "helmet";
import path from "node:path";

const app = express();
app.use(helmet({
  contentSecurityPolicy: { directives: { defaultSrc: ["'self'"], imgSrc: ["'self'", "data:", "https:"], scriptSrc: ["'self'"] } },
}));
app.use(compression());           // only if not at the proxy layer

// Hashed assets (main-abc123.js) — cache forever
app.use("/assets", express.static(path.join(__dirname, "public/assets"), {
  immutable: true,
  maxAge: "1y",
  etag: false,                     // redundant with immutable
  setHeaders: (res) =&gt; {
    res.setHeader("Cache-Control", "public, max-age=31536000, immutable");
    res.setHeader("Cross-Origin-Resource-Policy", "same-origin");
  },
}));

// Unhashed (robots.txt, favicon) — short cache with revalidation
app.use(express.static(path.join(__dirname, "public"), {
  maxAge: "1h",
  etag: true,
  lastModified: true,
}));

// SPA fallback — every unknown GET returns index.html so client-side router handles it
app.get("*", (req, res) =&gt; {
  res.sendFile(path.join(__dirname, "public/index.html"), {
    headers: { "Cache-Control": "public, max-age=60, must-revalidate" },   // HTML always short
  });
});</code></pre>
<p><strong>Production layering:</strong></p>
<ul>
  <li><strong>CDN</strong> (Cloudflare, CloudFront, Fastly) terminates TLS and caches by URL — sub-10ms globally. Let hashed assets cache for a year.</li>
  <li><strong>Object storage</strong> (S3, GCS) holds the built output; deploy = upload + invalidate.</li>
  <li><strong>Nginx / ALB</strong> serves from disk or forwards to Node; Nginx is 2-3× faster for static than <code>express.static</code>.</li>
  <li><strong>Node</strong> serves only dynamic routes — keeps the event loop free.</li>
</ul>
<p><strong>Trade-offs:</strong> <code>express.static</code> is fine for 100 rps of static traffic on a small box. For real production, never serve static from Node — it wastes event-loop time on files Nginx serves in kernel space. Pre-compress at build time (gzip + brotli) and serve the compressed variant (<code>send_brotli</code> module or <code>expressStaticGzip</code>). Set <strong>immutable</strong> Cache-Control on hashed files; short max-age on <code>index.html</code> (so deploys show up immediately). CSP at the proxy or via <code>helmet</code>. Don't forget SPA fallback (<code>app.get("*")</code>) — without it, deep links 404 on refresh. For Vercel / Netlify / Cloudflare Pages, this is all automatic.</p>
'''

ANSWERS[17] = r'''
<p><strong>Situation:</strong> public API with active mobile clients stuck on old versions; need to evolve the API without breaking them.</p>
<p><strong>Approach:</strong> URL-based versioning for simplicity and cacheability (<code>/v1/</code>, <code>/v2/</code>); deprecate politely with <code>Sunset</code>/<code>Deprecation</code> headers; bump version only on breaking changes — additive changes stay in the current version.</p>
<pre><code>import { Router } from "express";

// Routers per version — copy-paste or import shared handlers
const v1 = Router();
v1.get("/users/:id", v1Controller.getUser);   // returns { id, name }
v1.get("/posts", v1Controller.listPosts);

const v2 = Router();
v2.get("/users/:id", v2Controller.getUser);   // returns { id, displayName, avatar }
v2.get("/posts", v2Controller.listPosts);

app.use("/api/v1", v1);
app.use("/api/v2", v2);

// Deprecation signals on old version
app.use("/api/v1", (req, res, next) =&gt; {
  res.setHeader("Deprecation", "true");
  res.setHeader("Sunset", "Wed, 31 Dec 2026 23:59:59 GMT");
  res.setHeader("Link", '&lt;https://docs.example.com/migration-v2&gt;; rel="deprecation"');
  next();
});

// Alternative: header versioning for subtler schema evolution
// GET /users/123   Accept: application/vnd.company.v2+json
const negotiate = (req, res, next) =&gt; {
  const accept = req.get("Accept") ?? "";
  if (accept.includes("v2")) req.apiVersion = 2;
  else req.apiVersion = 1;
  next();
};</code></pre>
<p><strong>Rules that reduce version churn:</strong></p>
<ul>
  <li><strong>Additive changes never break:</strong> new optional fields, new endpoints, new query params with defaults. Don't bump versions for these.</li>
  <li><strong>Breaking changes force a bump:</strong> removing/renaming fields, changing response shape, changing auth, removing endpoints.</li>
  <li><strong>Dual-write transition:</strong> v2 writes to v1+v2 formats during migration; reads also dual-compatible. Removes after all clients migrate.</li>
</ul>
<p><strong>Trade-offs:</strong> URL versioning (<code>/v1/</code>) is the most discoverable and easiest to route/cache — ideal for public APIs. Header versioning (<code>Accept: application/vnd.X.v2+json</code>) is purer REST but harder to debug in curl and CDN caching is trickier. Query-param versioning (<code>?v=2</code>) is the worst — pollutes cache keys. Internally, <strong>GraphQL</strong> skips versioning entirely (deprecate fields with <code>@deprecated</code>) at the cost of complexity. <strong>gRPC</strong> evolves via additive proto changes within a major version. Publish OpenAPI (generated from Zod schemas) per version. Log <strong>version usage</strong> so you know when it's safe to sunset v1. Don't ship v2 until you can commit to supporting v1 for the agreed deprecation window — mobile apps live a long time.</p>
'''

ANSWERS[18] = r'''
<p><strong>Situation:</strong> a list endpoint (products, articles, users) that needs full-text search, field filters, sort, and pagination — at scale.</p>
<p><strong>Approach:</strong> for small corpora, Postgres full-text + B-tree indexes suffice; for larger scale and ranking needs, Meilisearch / Typesense / Elasticsearch. Always use cursor pagination for stable scroll; validate sort/filter keys against a whitelist.</p>
<pre><code>// Postgres-backed search — works for tens of millions of rows
// 1. DDL
//   ALTER TABLE articles ADD COLUMN search tsvector
//     GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || coalesce(body,''))) STORED;
//   CREATE INDEX articles_search_idx ON articles USING GIN (search);
//   CREATE INDEX articles_created_idx ON articles (created_at DESC, id DESC);

import { z } from "zod";
const SortFields = ["createdAt", "title", "views"] as const;
const Query = z.object({
  q: z.string().trim().max(200).optional(),
  author: z.string().uuid().optional(),
  tag: z.array(z.string()).optional(),
  sort: z.enum(SortFields).default("createdAt"),
  dir: z.enum(["asc", "desc"]).default("desc"),
  cursor: z.string().optional(),                     // base64(createdAt|id)
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

app.get("/articles", validate(Query, "query"), async (req, res) =&gt; {
  const { q, author, tag, sort, dir, cursor, limit } = req.query;
  const params = [];
  const where = [];

  if (q)      { params.push(q);      where.push(`search @@ websearch_to_tsquery('english', $${params.length})`); }
  if (author) { params.push(author); where.push(`author_id = $${params.length}`); }
  if (tag?.length) { params.push(tag); where.push(`tags &amp;&amp; $${params.length}::text[]`); }
  if (cursor) {
    const [c, id] = Buffer.from(cursor, "base64url").toString().split("|");
    params.push(c, id);
    where.push(`(${sort}, id) ${dir === "desc" ? "&lt;" : "&gt;"} ($${params.length-1}, $${params.length})`);
  }
  params.push(limit + 1);
  const sql = `
    SELECT id, title, author_id, created_at, ts_rank(search, websearch_to_tsquery('english', $1)) AS rank
    FROM articles
    ${where.length ? "WHERE " + where.join(" AND ") : ""}
    ORDER BY ${q ? "rank DESC," : ""} ${sort} ${dir}, id ${dir}
    LIMIT $${params.length}`;
  const { rows } = await pool.query(sql, params);
  const hasMore = rows.length &gt; limit; const page = rows.slice(0, limit);
  const nextCursor = hasMore ? Buffer.from(`${page.at(-1)[sort]}|${page.at(-1).id}`).toString("base64url") : null;
  res.json({ items: page, nextCursor });
});</code></pre>
<p><strong>Trade-offs:</strong> whitelist sort columns (<code>z.enum</code>) — never inject user-supplied field names into SQL. <strong>Cursor pagination</strong> (composite key on sort + id) beats OFFSET — OFFSET gets slow past page 100 and returns duplicates when data mutates. For ranked search, Postgres FTS works but plateaus; <strong>Meilisearch/Typesense</strong> give typo tolerance, facets, and instant-search UX out of the box. <strong>Elasticsearch</strong> is the choice for logs/analytics-style queries, aggregations, and complex scoring. Keep the search index <em>eventually consistent</em> with your DB via a background sync (CDC with Debezium → Kafka → indexer). Cache popular queries in Redis with short TTL; invalidate on writes. For multi-tenant, prefix keys/indexes by tenant, <em>never</em> trust a client-provided tenant filter — inject from auth context server-side.</p>
'''

ANSWERS[19] = r'''
<p><strong>Situation:</strong> app integrates with Stripe, SendGrid, Twilio; keys must be rotatable, scoped per environment, and never logged or committed.</p>
<p><strong>Approach:</strong> store in a secret manager (AWS Secrets Manager / GCP Secret Manager / HashiCorp Vault / Doppler); fetch at boot (or lazily with caching); design rotation as dual-key overlap so there's no downtime.</p>
<pre><code>import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";
import { LRUCache } from "lru-cache";

const sm = new SecretsManagerClient({});
const cache = new LRUCache({ max: 100, ttl: 5 * 60_000 });    // refresh every 5 min

async function getSecret(name) {
  if (cache.has(name)) return cache.get(name);
  const { SecretString } = await sm.send(new GetSecretValueCommand({ SecretId: name }));
  const parsed = JSON.parse(SecretString);
  cache.set(name, parsed);
  return parsed;
}

// Using a secret — fetch on demand, caller doesn't know about rotation
export async function getStripeClient() {
  const { apiKey } = await getSecret("prod/stripe");
  return new Stripe(apiKey, { apiVersion: "2024-06-20" });
}

// Rotation flow (automated via Lambda or scheduled job):
// 1. Generate NEW key at the provider (Stripe dashboard API / rolled token)
// 2. PUT new version into Secrets Manager (AWSCURRENT → AWSPENDING)
// 3. Test NEW key (call provider health endpoint)
// 4. Promote: Secrets Manager marks AWSPENDING as AWSCURRENT (atomic)
// 5. Wait 5-10 minutes — in-flight requests using OLD key drain (our cache TTL)
// 6. Revoke OLD key at the provider

// Handle rotation without restart — cache TTL + poll/subscribe
// Or listen to CloudWatch event when secret rotates; clear cache immediately</code></pre>
<p><strong>Trade-offs:</strong> <strong>never</strong> in env vars directly in production for long-lived keys — they don't rotate without redeploy. <strong>Secrets Manager / Vault</strong> give versioning, audit logs (who read what and when), KMS encryption at rest, and IAM-based access. Cache fetched secrets 5-15 min to avoid per-request API calls; accept a short window of staleness on rotation. For zero-downtime rotation, providers that support <strong>two active keys at once</strong> (Stripe restricted keys, AWS access keys) let you overlap — introduce new, wait for cache to expire, revoke old. Use <strong>per-service scoped</strong> restricted keys (Stripe Restricted Keys, SendGrid scoped keys) so a breach is limited. Monitor for unused keys (flag for rotation) and key-in-repo leaks (gitleaks in CI, GitHub secret scanning). Publicly committed keys happen — have a runbook and practice revocation.</p>
'''

ANSWERS[20] = r'''
<p><strong>Situation:</strong> stock ticker, live scores, collaborative editing — clients need instant updates, not polling.</p>
<p><strong>Approach:</strong> pick the right transport for the pattern: <strong>SSE</strong> for server-&gt;client one-way streams (simplest, works over HTTP/2), <strong>WebSocket</strong> for bidirectional, <strong>Socket.IO</strong> when you want rooms + fallbacks + reconnect baked in. Scale horizontally via Redis pub/sub.</p>
<pre><code>// SSE — elegant for pure server-&gt;client. Uses HTTP, no upgrade dance, auto-reconnect built into browsers.
app.get("/stream/:symbol", requireAuth, (req, res) =&gt; {
  res.set({
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache, no-transform",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",            // tell Nginx not to buffer
  });
  res.flushHeaders();

  const symbol = req.params.symbol;
  const sub = redisSub.duplicate();
  sub.subscribe(`ticker:${symbol}`);
  sub.on("message", (_, data) =&gt; {
    res.write(`data: ${data}\n\n`);      // each event ends with \n\n
  });
  const keepalive = setInterval(() =&gt; res.write(`: ping\n\n`), 15_000);   // comment = heartbeat

  req.on("close", () =&gt; { clearInterval(keepalive); sub.quit(); });
});

// WebSocket with Socket.IO — needed for chat, typing indicators, collaborative editing
import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
const io = new Server(httpServer, { cors: { origin: process.env.ORIGIN } });
io.adapter(createAdapter(redisPub, redisSub));

io.use((s, next) =&gt; { try { s.data.user = jwt.verify(s.handshake.auth.token, JWT_SECRET); next(); } catch { next(new Error("unauthorized")); } });

io.on("connection", (socket) =&gt; {
  socket.on("doc:join", async (docId) =&gt; {
    if (!await canAccess(socket.data.user, docId)) return socket.emit("error", "forbidden");
    socket.join(`doc:${docId}`);
    socket.emit("doc:state", await loadDocState(docId));
  });
  socket.on("doc:op", async ({ docId, op }) =&gt; {
    await applyOp(docId, op);                               // CRDT / OT
    socket.to(`doc:${docId}`).emit("doc:op", op);          // broadcast to others
  });
});</code></pre>
<p><strong>Trade-offs:</strong> <strong>SSE</strong> is simpler than WebSocket: plain HTTP, automatic reconnect with <code>Last-Event-ID</code>, works through most proxies, HTTP/2 multiplexes cleanly. Choose SSE for notifications, tickers, progress updates. <strong>WebSocket</strong> is needed only for true bidirectional (chat, games, collaborative editing). Scale both horizontally via Redis pub/sub so any replica can reach any client. Authenticate <strong>on upgrade/connect</strong>, not after — and validate the token fresh (don't cache decisions beyond the lifetime you can revoke). Heartbeat every 15-30s to detect zombie connections and keep proxies from idle-timing out. Enforce per-connection rate limits to stop spam. For mobile, pair with push notifications (APNs/FCM) when the socket is offline. <strong>Pusher/Ably</strong> if you don't want to operate WebSocket infra — pay for their scale. For millions of concurrent connections per node, <strong>uWebSockets.js</strong> beats Socket.IO.</p>
'''

ANSWERS[21] = r'''
<p><strong>Situation:</strong> An existing Express codebase is growing organically — routes, business logic, and DB calls are all tangled inside handlers, making testing and onboarding painful. MVC (adapted as Routes → Controllers → Services → Repositories) gives clear responsibilities.</p>
<pre><code>// Folder layout
src/
├── routes/               // HTTP surface: URL → controller mapping
│   ├── user.routes.ts
│   └── index.ts
├── controllers/          // HTTP concerns: parse req, call service, format res
│   └── user.controller.ts
├── services/             // Business logic: orchestrates repos, enforces rules
│   └── user.service.ts
├── repositories/         // Data access: SQL/Mongo queries, no business logic
│   └── user.repo.ts
├── models/               // Domain types / Mongoose/Prisma schemas
│   └── user.ts
├── middleware/           // auth, validation, logging, error handler
├── lib/                  // crypto, mailer, storage — no domain rules
├── config/               // Zod-validated env
├── app.ts                // Express wiring
└── server.ts             // boot

// routes/user.routes.ts
const r = Router();
r.get("/:id", asyncH(userController.get));
r.post("/",    validate(CreateUser), asyncH(userController.create));

// controllers/user.controller.ts
export const userController = {
  async get(req, res) { res.json(await userService.get(req.params.id)); },
  async create(req, res) { res.status(201).json(await userService.create(req.body)); },
};

// services/user.service.ts
export const userService = {
  async create(data) {
    if (await userRepo.findByEmail(data.email)) throw new ConflictError("email taken");
    const hashed = await argon2.hash(data.password);
    return userRepo.create({ ...data, password: hashed });
  },
  get(id) { return userRepo.findById(id); },
};</code></pre>
<p><strong>Trade-offs &amp; rules:</strong> enforce a <em>dependency direction</em>: routes → controllers → services → repos. Never call a repo from a controller, never import express types inside services (that's what makes them unit-testable). Controllers stay thin (5-10 lines); business rules live in services. Repositories hide the ORM — swapping Prisma for Drizzle shouldn't ripple outward. For larger codebases, layer <strong>feature folders</strong> over the MVC structure (<code>src/users/*</code>, <code>src/orders/*</code>) so one domain's code clusters together. NestJS formalizes all this with decorators and DI if you want an opinionated framework. Pair with <strong>central error handler</strong> + <strong>AsyncLocalStorage</strong> for request context (correlation ID, user) so services don't need req passed around.</p>
'''

ANSWERS[22] = r'''
<p><strong>Situation:</strong> Users need to download files ranging from small exports to multi-GB archives. Naive <code>res.send(await readFile(path))</code> OOMs on large files because it buffers the whole thing in memory.</p>
<pre><code>import { createReadStream, statSync } from "node:fs";
import { pipeline } from "node:stream/promises";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

// 1. Small local file — stream even so, no buffering
app.get("/files/:name", async (req, res, next) =&gt; {
  try {
    const path = safeResolve(req.params.name);   // prevent path traversal
    const { size, mtime } = statSync(path);
    res.setHeader("Content-Length", size);
    res.setHeader("Content-Type", mime.lookup(path) || "application/octet-stream");
    res.setHeader("Content-Disposition", `attachment; filename="${encodeURIComponent(basename(path))}"`);
    res.setHeader("Last-Modified", mtime.toUTCString());
    await pipeline(createReadStream(path), res);  // backpressure-safe
  } catch (e) { next(e); }
});

// 2. Large file from S3 — proxy through app (stream, no buffer)
const s3 = new S3Client({});
app.get("/reports/:key", async (req, res, next) =&gt; {
  try {
    const obj = await s3.send(new GetObjectCommand({ Bucket: "reports", Key: req.params.key }));
    res.setHeader("Content-Type", obj.ContentType);
    res.setHeader("Content-Length", obj.ContentLength);
    res.setHeader("Content-Disposition", `attachment; filename="${req.params.key}"`);
    await pipeline(obj.Body, res);
  } catch (e) { next(e); }
});

// 3. BEST for large files — pre-signed S3 URL (skip your server entirely)
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
app.get("/reports/:key/download-url", async (req, res) =&gt; {
  const url = await getSignedUrl(s3, new GetObjectCommand({ Bucket: "reports", Key: req.params.key }),
    { expiresIn: 300 });
  res.json({ url });  // client fetches directly from S3 — no Node in the path
});</code></pre>
<p><strong>Trade-offs:</strong> always <strong>stream</strong> — <code>pipeline()</code> handles backpressure and cleanup automatically. For anything over ~10 MB, <strong>pre-signed URLs</strong> beat proxying: CDN accelerates delivery, your Node replicas free up event-loop capacity, and bandwidth bills shift to S3. Implement <strong>range requests</strong> (HTTP 206) for resumable downloads — set <code>Accept-Ranges: bytes</code> and honor <code>Range</code> header. Sanitize paths (reject <code>..</code>), authorize ownership before issuing URLs, and set short expiries. For extra-large files, combine with <strong>multipart downloads</strong> (client fetches parallel ranges). Use CDN (CloudFront, Cloudflare R2) in front to cache globally and offload authentication to signed cookies/URLs.</p>
'''

ANSWERS[23] = r'''
<p><strong>Situation:</strong> Some operations (send email, generate PDF, resize image, export report) are too slow for HTTP response time. Run them async in workers decoupled from the request cycle. Use a durable queue with retry and observability — not in-memory timers.</p>
<pre><code>// BullMQ — Redis-backed job queue (the Node de-facto standard)
import { Queue, Worker, QueueEvents } from "bullmq";
const connection = { host: "redis", port: 6379 };

// Producer (in your API handler)
export const emailQ = new Queue("emails", { connection });
app.post("/signup", async (req, res) =&gt; {
  const user = await userService.create(req.body);
  await emailQ.add("welcome",
    { userId: user.id, to: user.email },
    {
      jobId: `welcome:${user.id}`,           // idempotency — duplicate enqueue = no-op
      attempts: 5,
      backoff: { type: "exponential", delay: 2000 },   // 2s, 4s, 8s, 16s, 32s
      removeOnComplete: { age: 3600, count: 1000 },
      removeOnFail: { age: 7 * 24 * 3600 },           // keep week of failures for debug
    }
  );
  res.status(201).json(user);   // respond instantly; email sends in background
});

// Worker process (deploy as separate replica set)
// worker.ts — run N of these behind K8s Deployment
new Worker("emails", async (job) =&gt; {
  const { userId, to } = job.data;
  await mailer.send({ template: "welcome", to, context: { userId } });
}, { connection, concurrency: 20, limiter: { max: 100, duration: 1000 } });

// Observability
const evts = new QueueEvents("emails", { connection });
evts.on("failed", ({ jobId, failedReason }) =&gt; log.error({ jobId, failedReason }));
evts.on("stalled", ({ jobId }) =&gt; log.warn({ jobId, msg: "stalled" }));</code></pre>
<p><strong>Trade-offs:</strong> separate <strong>API replicas from worker replicas</strong> — CPU-heavy jobs shouldn't contend with HTTP. Use <strong>idempotency keys</strong> (<code>jobId</code>) so retries and duplicate enqueues are safe. Configure <strong>backoff + DLQ</strong> (failed jobs after N attempts) for human review. For cross-service or language-agnostic fan-out, <strong>SQS/Kafka/NATS</strong> fit better than BullMQ (Redis). For durable workflows with human-in-the-loop steps (approvals, multi-day), <strong>Temporal</strong> or <strong>Inngest</strong> wins over raw queues. <strong>Monitor</strong>: queue depth (alert if growing), age-of-oldest-job, failed/stalled count, worker CPU — these catch silent backups before users notice. Use a dashboard (BullMQ has Bull Board or Taskforce.sh).</p>
'''

ANSWERS[24] = r'''
<p><strong>Situation:</strong> Any app taking user input is a target for SQL injection, XSS, CSRF, and a long tail of OWASP Top 10 issues. Defense is layered — no single control suffices.</p>
<pre><code>// 1. SQL INJECTION — parameterized queries always; never string-concat
// BAD:  `SELECT * FROM users WHERE email='${email}'`
// GOOD with pg (or Prisma/Knex — all safe by default):
await pool.query("SELECT * FROM users WHERE email = $1", [email]);
await prisma.user.findUnique({ where: { email } });

// NoSQL injection (Mongo) — strip $ / . operator keys from user JSON
function stripOps(obj) {
  for (const k of Object.keys(obj || {})) {
    if (k.startsWith("$") || k.includes(".")) delete obj[k];
    else if (typeof obj[k] === "object") stripOps(obj[k]);
  }
  return obj;
}
app.use((req, _res, next) =&gt; { stripOps(req.body); stripOps(req.query); next(); });

// 2. XSS — never trust HTML input; render text escaped, sanitize allowed HTML
import sanitizeHtml from "sanitize-html";
const cleanHtml = sanitizeHtml(input, {
  allowedTags: ["p", "b", "i", "em", "strong", "a"],
  allowedAttributes: { a: ["href", "title", "rel"] },
  allowedSchemes: ["https", "mailto"],
});

// 3. Security headers — helmet sets ~15 safe defaults in one line
import helmet from "helmet";
app.use(helmet({
  contentSecurityPolicy: { directives: { defaultSrc: ["'self'"], imgSrc: ["'self'", "data:"], scriptSrc: ["'self'"] } },
  hsts: { maxAge: 63072000, includeSubDomains: true, preload: true },
}));

// 4. CSRF — SameSite=Strict cookies + synchronizer tokens for state-changing requests
import csurf from "csurf";
app.use(csurf({ cookie: { secure: true, sameSite: "strict", httpOnly: true } }));

// 5. Validate everything at the boundary with Zod
app.post("/users", validate(CreateUser), handler);</code></pre>
<p><strong>Trade-offs &amp; rules:</strong> <strong>defense in depth</strong> — validate input (Zod), parameterize queries (ORM), escape output (template engine auto-escapes), enforce CSP (<code>script-src 'self'</code>), set Secure+HttpOnly+SameSite on cookies, rate-limit login, audit deps (<code>npm audit</code>, Snyk, Dependabot). Use <strong>bcrypt/argon2id</strong> for passwords, never MD5/SHA. Keep Node/deps <strong>up to date</strong> — most breaches exploit known CVEs. Scan Docker images (Trivy), sign (Cosign), run as <strong>non-root</strong>. Run a <strong>WAF</strong> (Cloudflare, AWS WAF) in front for OWASP rule coverage. Centralize secrets in a manager, never in env or code. Log <strong>security events</strong> (failed logins, auth errors, admin actions) to a SIEM. <strong>Threat model</strong> periodically — STRIDE or similar — and track findings to closure.</p>
'''

ANSWERS[25] = r'''
<p><strong>Situation:</strong> Need to generate branded PDF reports (invoices, statements, analytics dashboards). Two approaches: HTML → PDF via headless browser (pixel-perfect, reusable CSS/charts) or programmatic PDF via <code>pdfkit</code>/<code>pdfmake</code> (smaller footprint). Heavy rendering belongs in a queue, not request path.</p>
<pre><code>// Puppeteer — highest fidelity; shares HTML/CSS with your web UI
import puppeteer from "puppeteer";

async function generateInvoicePdf({ invoiceId }) {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox"],  // inside containers
  });
  try {
    const page = await browser.newPage();
    // Render from your own SSR route — identical branding as web
    await page.goto(`http://localhost:3000/internal/invoices/${invoiceId}/print`, { waitUntil: "networkidle0" });
    const pdf = await page.pdf({
      format: "A4",
      printBackground: true,
      margin: { top: "20mm", bottom: "20mm", left: "15mm", right: "15mm" },
      displayHeaderFooter: true,
      headerTemplate: `&lt;div style="font-size:9px;width:100%;text-align:right;padding-right:15mm;"&gt;&lt;span class="pageNumber"&gt;&lt;/span&gt; / &lt;span class="totalPages"&gt;&lt;/span&gt;&lt;/div&gt;`,
    });
    return pdf;
  } finally { await browser.close(); }
}

// Queue PDF generation (too slow for request path)
import { Queue, Worker } from "bullmq";
const pdfQ = new Queue("pdfs", { connection });

app.post("/invoices/:id/pdf", async (req, res) =&gt; {
  const jobId = `invoice:${req.params.id}`;
  await pdfQ.add("generate", { invoiceId: req.params.id, userId: req.user.id }, { jobId });
  res.status(202).json({ jobId, status: "generating" });   // client polls or subscribes
});

new Worker("pdfs", async (job) =&gt; {
  const pdf = await generateInvoicePdf(job.data);
  const key = `invoices/${job.data.invoiceId}.pdf`;
  await s3.send(new PutObjectCommand({ Bucket: "docs", Key: key, Body: pdf, ContentType: "application/pdf" }));
  await notifyUser(job.data.userId, { invoiceId: job.data.invoiceId, downloadKey: key });
}, { connection, concurrency: 2 });   // Puppeteer is RAM-heavy — low concurrency</code></pre>
<p><strong>Trade-offs:</strong> <strong>Puppeteer/Playwright</strong> give perfect fidelity but need Chromium (~300 MB image, ~400 MB RAM per page). For high volume, pool browser contexts or use a dedicated rendering service (<a>Gotenberg</a>, <a>Browserless</a>). <strong><code>pdfkit</code></strong> is tiny and pure JS but means hand-coded layout. <strong><code>@react-pdf/renderer</code></strong> is a middle ground — declarative, TSX-friendly. Always generate <strong>in a worker</strong>, not the request thread; store to S3 and email/notify the user with a signed URL when done. Watermark / digitally sign sensitive docs. Cache generated PDFs by hash of inputs so re-requests are free. Disable external resources / fonts at render time to avoid supply-chain risk.</p>
'''

ANSWERS[26] = r'''
<p><strong>Situation:</strong> Managing dependencies across a team (or many services in a monorepo) means keeping versions consistent, security patches applied, and CI deterministic — without becoming a full-time job.</p>
<pre><code>// package.json — pin the tools and runtime
{
  "engines": { "node": "&gt;=20.11", "pnpm": "&gt;=9" },
  "packageManager": "pnpm@9.12.0",   // enforced by Corepack
  "overrides": {                      // force transitive fixes
    "semver@&lt;7.5.2": "7.5.4"
  }
}

// Lockfile is source of truth — always commit it, always --frozen-lockfile in CI
# CI
pnpm install --frozen-lockfile
pnpm audit --audit-level=high
pnpm outdated</code></pre>
<pre><code># renovate.json — auto-update strategy
{
  "extends": ["config:recommended", ":semanticCommits"],
  "schedule": ["before 8am on monday"],
  "packageRules": [
    { "matchUpdateTypes": ["patch"],
      "automerge": true, "automergeType": "branch" },        // patch auto-merges if CI green
    { "matchUpdateTypes": ["minor"], "automerge": false },   // minor needs review
    { "matchDepTypes": ["devDependencies"], "groupName": "dev deps",
      "schedule": ["before 8am on the first day of the month"] },
    { "matchPackagePatterns": ["^@aws-sdk/"], "groupName": "aws-sdk" }
  ],
  "vulnerabilityAlerts": { "enabled": true, "automerge": true }
}</code></pre>
<p><strong>Trade-offs &amp; rules:</strong> pick <strong>one package manager</strong> (pnpm or npm) per repo; commit its lockfile; enforce via Corepack. Use <strong>strict versioning at tool level</strong> (<code>engines</code>, <code>packageManager</code>) so contributors don't diverge. In CI always <code>--frozen-lockfile</code> / <code>npm ci</code> — deterministic, fails on drift. Automate updates with <strong>Renovate</strong> or <strong>Dependabot</strong>: group, auto-merge patch, schedule so you don't get 50 PRs/day. Use <strong>overrides</strong>/<strong>resolutions</strong> for transitive CVE fixes before upstream. In monorepos (<strong>pnpm workspaces + Turborepo</strong>), pin shared deps at the root so all services use the same version; use <code>syncpack</code> to detect and fix drift. Disable install scripts (<code>npm ci --ignore-scripts</code>) for supply-chain hygiene, or allow-list via <code>--allow-scripts</code> (pnpm 9+). Run <code>npm audit</code> in CI; track <strong>SBOM</strong> (CycloneDX) for compliance. Budget time to keep deps current — drift gets harder the longer you wait.</p>
'''

ANSWERS[27] = r'''
<p><strong>Situation:</strong> Need to cap API request rates to prevent abuse (credential stuffing, scrapers) and protect downstream systems. Two related concepts: <strong>rate limiting</strong> (hard cap: "max 100/min per user") and <strong>throttling</strong> (smooth: slow down as load rises). In Node, both are implemented as middleware, typically Redis-backed so the limit is <em>global</em> across replicas.</p>
<pre><code>// Token bucket via Lua — atomic, works across any number of app replicas
const tokenBucketLua = `
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])   -- tokens/sec
local now = tonumber(ARGV[3])
local cost = tonumber(ARGV[4])

local data = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(data[1]) or capacity
local ts = tonumber(data[2]) or now

local elapsed = math.max(0, now - ts) / 1000
tokens = math.min(capacity, tokens + elapsed * refill_rate)

if tokens &lt; cost then
  redis.call("HMSET", key, "tokens", tokens, "ts", now)
  redis.call("EXPIRE", key, math.ceil(capacity / refill_rate) + 10)
  return {0, tokens}
end
tokens = tokens - cost
redis.call("HMSET", key, "tokens", tokens, "ts", now)
redis.call("EXPIRE", key, math.ceil(capacity / refill_rate) + 10)
return {1, tokens}
`;

const rateLimit = ({ capacity, refill, keyFn }) =&gt; async (req, res, next) =&gt; {
  const key = `rl:${keyFn(req)}`;
  const [allowed, remaining] = await redis.eval(tokenBucketLua, 1, key,
    capacity, refill, Date.now(), 1);
  res.setHeader("X-RateLimit-Limit", capacity);
  res.setHeader("X-RateLimit-Remaining", Math.floor(remaining));
  if (!allowed) {
    res.setHeader("Retry-After", Math.ceil(1 / refill));
    return res.status(429).json({ error: "rate_limited" });
  }
  next();
};

// Different tiers for different endpoints / user classes
app.post("/auth/login",
  rateLimit({ capacity: 5, refill: 0.1, keyFn: r =&gt; r.ip }),           // 5 / 50s per IP
  loginHandler);
app.use("/api/",
  rateLimit({ capacity: 1000, refill: 100/60, keyFn: r =&gt; r.user?.id ?? r.ip }),  // 1000/min
);</code></pre>
<p><strong>Trade-offs:</strong> <strong>Fixed window</strong> (counter per minute) is simplest but bursts at window boundaries. <strong>Sliding window</strong> is smoother but costlier. <strong>Token bucket</strong> (shown) allows bursts up to capacity, refills steadily — best all-rounder. <strong>Leaky bucket</strong> smooths output — good for downstream protection. Key choice matters: limit by <strong>user ID</strong> for authenticated, <strong>IP</strong> for public; for logins limit by <strong>IP + username</strong> to stop credential stuffing. Apply first layer at <strong>proxy/CDN</strong> (Nginx <code>limit_req</code>, Cloudflare) for cheap blocks; second layer in app for business rules. Libraries: <strong><code>express-rate-limit</code></strong> with <strong><code>rate-limit-redis</code></strong> store, or <strong><code>rate-limiter-flexible</code></strong> (richer algorithms). Always return <strong>429</strong> + <code>Retry-After</code> + structured error so clients back off. Instrument rejections — a spike is either abuse or a broken client.</p>
'''

ANSWERS[28] = r'''
<p><strong>Situation:</strong> Parts of the app need to react to domain events (user signed up, order placed) without tight coupling — sending email, updating analytics, firing webhooks. Node's built-in <code>EventEmitter</code> handles this <em>within one process</em>. For cross-process or durable delivery, you'll graduate to Redis pub/sub or a real queue.</p>
<pre><code>import { EventEmitter } from "node:events";

// Typed event bus — one per domain concern
type Events = {
  "user.created": { userId: string; email: string };
  "order.placed": { orderId: string; userId: string; total: number };
};

class TypedBus&lt;T extends Record&lt;string, any&gt;&gt; extends EventEmitter {
  emit&lt;K extends keyof T&gt;(event: K, payload: T[K]): boolean { return super.emit(event as string, payload); }
  on&lt;K extends keyof T&gt;(event: K, listener: (p: T[K]) =&gt; void) { return super.on(event as string, listener); }
}

export const bus = new TypedBus&lt;Events&gt;();
bus.setMaxListeners(50);   // default 10; raise if you expect more subscribers

// Subscribers — register at startup
bus.on("user.created", ({ userId, email }) =&gt; {
  emailQ.add("welcome", { userId, email }).catch(log.error);    // enqueue — don't do work synchronously
});
bus.on("order.placed", async ({ orderId, total }) =&gt; {
  await analytics.track("order", { orderId, total });
});

// Publisher — from a service after committing state
export async function createUser(data) {
  const user = await userRepo.create(data);
  bus.emit("user.created", { userId: user.id, email: user.email });
  return user;
}

// Error handling — one listener throwing shouldn't crash others
bus.on("error", (err) =&gt; log.error({ err }, "bus error"));
// Wrap listeners defensively
const safeOn = (event, fn) =&gt; bus.on(event, (p) =&gt; {
  Promise.resolve().then(() =&gt; fn(p)).catch(err =&gt; log.error({ err, event }));
});</code></pre>
<p><strong>Trade-offs:</strong> <code>EventEmitter</code> is <strong>synchronous by default</strong> — listeners run in emitter order, inline. A throwing listener interrupts the chain. Use <code>queueMicrotask</code>/<code>setImmediate</code> or <code>Promise.resolve().then()</code> to decouple. Events <strong>don't survive process restart</strong> and <strong>don't cross instances</strong> — anything critical (email sending) must enqueue into Bull/Kafka/etc. The safe pattern: <em>persist the side effect intent</em> (e.g. outbox row) in the same DB transaction as the state change, then emit; a background worker reads the outbox and dispatches — guaranteeing at-least-once delivery even if the process dies before the listener fires. For bigger systems, replace with <strong>Redis pub/sub</strong> (cross-instance, ephemeral), <strong>NATS JetStream</strong> or <strong>Kafka</strong> (durable, replay), or a managed bus (AWS EventBridge). Keep <code>EventEmitter</code> for in-process decoupling only.</p>
'''

ANSWERS[29] = r'''
<p><strong>Situation:</strong> Endpoint receives file uploads (profile images, CSVs, docs). <code>multipart/form-data</code> is the browser's encoding. Native Node gives a raw stream — use a library and validate aggressively (uploads are a top attack surface).</p>
<pre><code>// multer — Express-native, flexible storage
import multer from "multer";
import { z } from "zod";
import { fileTypeFromBuffer } from "file-type";
import { Upload } from "@aws-sdk/lib-storage";

const upload = multer({
  storage: multer.memoryStorage(),                   // small files; use diskStorage / S3 for big
  limits: {
    fileSize: 10 * 1024 * 1024,                      // 10 MB hard cap per file
    files: 5,                                        // max 5 per request
    fields: 20,
    fieldSize: 1024 * 1024,
  },
  fileFilter: (_req, file, cb) =&gt; {
    // MIME-by-header is user-controlled — accept a broad allowlist, re-verify later
    const allowed = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
    cb(allowed.includes(file.mimetype) ? null : new Error("unsupported type"), allowed.includes(file.mimetype));
  },
});

const Meta = z.object({ category: z.enum(["avatar", "doc"]) });

app.post("/upload",
  authRequired,
  upload.array("files", 5),
  async (req, res, next) =&gt; {
    try {
      const meta = Meta.parse(req.body);                // text fields sit in req.body
      const saved = await Promise.all((req.files as Express.Multer.File[]).map(async (f) =&gt; {
        // Re-verify by magic bytes — don't trust the header
        const sniff = await fileTypeFromBuffer(f.buffer);
        if (!sniff || !["jpg", "png", "webp", "pdf"].includes(sniff.ext)) {
          throw new Error("payload mismatch with declared type");
        }
        const key = `uploads/${req.user.id}/${crypto.randomUUID()}.${sniff.ext}`;
        await new Upload({
          client: s3, params: { Bucket: "files", Key: key, Body: f.buffer, ContentType: sniff.mime },
        }).done();
        return { key, size: f.size, type: sniff.mime };
      }));
      res.status(201).json({ uploaded: saved, meta });
    } catch (e) { next(e); }
  }
);

// Central error handler translates multer errors
app.use((err, _req, res, next) =&gt; {
  if (err instanceof multer.MulterError) return res.status(400).json({ error: err.code });
  next(err);
});</code></pre>
<p><strong>Trade-offs:</strong> for anything over <strong>~20 MB</strong>, skip in-memory parsing — use <strong>busboy</strong> or <strong>multer.diskStorage()</strong> + pipe straight to S3 (<code>@aws-sdk/lib-storage</code>) so Node never buffers the whole file. Even better: <strong>pre-signed S3 PUT URLs</strong> — browser uploads directly to S3, your API only records metadata. Always: (1) size limits at multiple layers (LB + app + S3 bucket policy), (2) MIME verification by magic bytes (<code>file-type</code>) not header, (3) virus scan (ClamAV, VirusTotal) for user-sourced files, (4) store under a UUID key (never user filename — path traversal), (5) scope paths per tenant, (6) serve downloads via signed URL, not public bucket. Return structured errors for 413/415 so clients can UX them. Log accepted + rejected counts — spikes often indicate abuse.</p>
'''

ANSWERS[30] = r'''
<p><strong>Situation:</strong> Every request should be logged with timing, status, correlation ID, and user — for debugging, audit, and SLO reporting. Naive <code>console.log</code> in a handler captures nothing useful under load. Build proper middleware using <code>pino-http</code> (fastest structured logger) with AsyncLocalStorage for per-request context.</p>
<pre><code>import pino from "pino";
import pinoHttp from "pino-http";
import { AsyncLocalStorage } from "node:async_hooks";
import { randomUUID } from "node:crypto";

const base = pino({
  level: process.env.LOG_LEVEL || "info",
  redact: {                                           // prevent token/secret leakage
    paths: ["req.headers.authorization", "req.headers.cookie", '*.password', '*.token'],
    censor: "[REDACTED]",
  },
  formatters: { level: (l) =&gt; ({ level: l }) },       // structured JSON, no pretty in prod
});

// Correlation context — any service layer can access req id/user without prop drilling
export const ctx = new AsyncLocalStorage&lt;{ reqId: string; userId?: string }&gt;();
export const log = {
  info: (o, m) =&gt; base.info({ ...ctx.getStore(), ...o }, m),
  warn: (o, m) =&gt; base.warn({ ...ctx.getStore(), ...o }, m),
  error: (o, m) =&gt; base.error({ ...ctx.getStore(), ...o }, m),
};

// pino-http — per-request logger with automatic start/finish lines
app.use(pinoHttp({
  logger: base,
  genReqId: (req) =&gt; req.headers["x-request-id"] || randomUUID(),
  customLogLevel: (_req, res, err) =&gt; {
    if (err || res.statusCode &gt;= 500) return "error";
    if (res.statusCode &gt;= 400) return "warn";
    return "info";
  },
  customProps: (req) =&gt; ({ userId: (req as any).user?.id }),
  serializers: {
    req: (req) =&gt; ({ id: req.id, method: req.method, url: req.url, remote: req.remoteAddress }),
    res: (res) =&gt; ({ statusCode: res.statusCode }),
  },
}));

// Wrap every request in AsyncLocalStorage so log.* inside services pick up ids
app.use((req, _res, next) =&gt; {
  ctx.run({ reqId: req.id as string, userId: (req as any).user?.id }, next);
});

// Now any service can log with full request context
async function createOrder(data) {
  log.info({ orderTotal: data.total }, "placing order");     // includes reqId, userId
  // ...
}</code></pre>
<p><strong>Trade-offs:</strong> <strong>structured JSON logs</strong> are table stakes — aggregators (Datadog, Loki, CloudWatch) parse them, enabling queries like "all 5xx for user X in last hour." Always <strong>redact</strong> <code>authorization</code>, <code>cookie</code>, passwords, tokens, card numbers — pino's <code>redact</code> does it at serialization time. Include a <strong>request ID</strong> (propagate via <code>x-request-id</code> header or W3C <code>traceparent</code>) so one user journey correlates across services. <strong>Log to stdout</strong>, never files — let the orchestrator handle rotation, shipping, retention. Keep <code>info</code> for normal flow, <code>warn</code> for recoverable, <code>error</code> for paging-worthy. Sample high-volume <code>info</code> (1 in 10) in prod to cut costs. Pair with <strong>OpenTelemetry traces</strong> for cross-service spans, <strong>metrics</strong> (Prometheus) for SLOs, and <strong>Sentry</strong> for error aggregation and deduplication.</p>
'''

ANSWERS[31] = r'''
<p><strong>Situation:</strong> Service must render text in multiple languages (error messages, emails, generated PDFs), format dates/numbers per locale, and handle pluralization correctly. The library consensus is <strong>i18next</strong> + Node's built-in <strong>Intl</strong> for formatting.</p>
<pre><code>import i18next from "i18next";
import Backend from "i18next-fs-backend";
import middleware, { LanguageDetector } from "i18next-http-middleware";

await i18next
  .use(Backend)
  .use(LanguageDetector)
  .init({
    fallbackLng: "en",
    supportedLngs: ["en", "es", "fr", "de", "ja", "hi", "ar"],
    preload: ["en", "es", "fr"],
    ns: ["common", "email"],
    defaultNS: "common",
    backend: { loadPath: "./locales/{{lng}}/{{ns}}.json" },
    detection: {
      order: ["header", "querystring", "cookie"],
      lookupHeader: "accept-language",
      caches: ["cookie"],
    },
  });
app.use(middleware.handle(i18next));

// locales/en/common.json
// { "welcome": "Welcome, {{name}}!",
//   "cart_item_one": "{{count}} item", "cart_item_other": "{{count}} items",
//   "err_notfound": "Not found" }

// Use in handlers
app.get("/", (req, res) =&gt; {
  res.json({
    greeting: req.t("welcome", { name: req.user?.name ?? "friend" }),
    cart: req.t("cart_item", { count: 3 }),       // auto plural
    when: new Intl.DateTimeFormat(req.language, { dateStyle: "long" }).format(new Date()),
    price: new Intl.NumberFormat(req.language, { style: "currency", currency: "EUR" }).format(1299.5),
  });
});

// Server-rendered email template — pass locale down
await mailer.send({
  to: user.email,
  subject: i18next.t("email:welcome.subject", { lng: user.locale }),
  html: render("welcome", { t: i18next.getFixedT(user.locale, "email"), user }),
});</code></pre>
<p><strong>Trade-offs:</strong> <strong>Always formula:</strong> store locale per user (<code>en-GB</code>, <code>pt-BR</code>) in DB; negotiate from <code>Accept-Language</code> header with fallback; send locale into every rendering path. Use <strong>ICU MessageFormat</strong> (i18next supports it) for complex cases — plural forms differ wildly (Arabic has 6, Russian 3, Japanese 1), and gender/select cases need real grammar support. Never string-concat translations — <code>"You have " + count + " items"</code> breaks in German (word order), French (plural agreement), and Arabic (right-to-left). Use <code>Intl.*</code> (built-in) for numbers, currency, dates, relative time, list formatting — don't hand-roll. Translations workflow: export to <strong>Crowdin</strong>/<strong>Lokalise</strong>/<strong>Phrase</strong>; CI fails on missing keys. For right-to-left scripts include <code>lang</code>/<code>dir</code> in emails so rendering is correct. Time zones: store UTC; format with <code>Intl.DateTimeFormat(locale, { timeZone })</code>.</p>
'''

ANSWERS[32] = r'''
<p><strong>Situation:</strong> A CPU-heavy operation (parse 50 MB CSV, compute crypto digests, image transform, PDF render) runs in a request handler and blocks the event loop, freezing every other request on that instance. Move it off the main thread.</p>
<pre><code>// Using piscina — a battle-tested thread pool wrapper around worker_threads
// npm i piscina
import Piscina from "piscina";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

// Pool, reused across requests — don't spawn per request
const pool = new Piscina({
  filename: resolve(fileURLToPath(import.meta.url), "../hash.worker.js"),
  maxThreads: Math.max(1, os.cpus().length - 1),   // leave a core for main
  idleTimeout: 30_000,
  resourceLimits: { maxOldGenerationSizeMb: 512 }, // prevent runaway
});

// Handler — non-blocking
app.post("/hash", async (req, res) =&gt; {
  const { data } = req.body;      // or a file path / buffer
  const digest = await pool.run({ data, algo: "sha256" });
  res.json({ digest });
});

// hash.worker.js — runs inside a worker thread
import crypto from "node:crypto";
export default async function ({ data, algo }) {
  const h = crypto.createHash(algo);
  h.update(data);
  return h.digest("hex");
}</code></pre>
<pre><code>// Raw worker_threads — when you need SharedArrayBuffer or persistent workers
import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";
if (isMainThread) {
  const w = new Worker(import.meta.filename, { workerData: { n: 40 } });
  w.on("message", console.log);   // { fib: ... }
} else {
  const fib = (n) =&gt; n &lt; 2 ? n : fib(n-1) + fib(n-2);
  parentPort.postMessage({ fib: fib(workerData.n) });
}</code></pre>
<p><strong>Trade-offs:</strong> workers are <strong>isolated V8 contexts</strong> — each has its own heap and module graph. Data crosses the boundary via <em>structured clone</em> (copied, slow for big objects) or <strong>transferable</strong>s like <code>ArrayBuffer</code>/<code>MessageChannel</code> (zero-copy, fast). <strong><code>piscina</code></strong> abstracts pooling, task queuing, and backpressure — usually the right choice. Use <strong><code>SharedArrayBuffer</code></strong> when multiple workers coordinate on a big dataset — shared memory with <code>Atomics</code> for coordination. Workers are for <strong>CPU-bound</strong> work only — for I/O, the event loop is already optimal and a worker adds overhead. Size the pool to <code>cores - 1</code>; don't overshoot (context switching thrashes). For truly heavy batch work (hours), prefer a <strong>separate worker process</strong> / <strong>BullMQ worker</strong> — it can scale horizontally and doesn't risk taking down the API process. Monitor pool utilization + queue depth; a full pool means requests wait.</p>
'''

ANSWERS[33] = r'''
<p><strong>Situation:</strong> Need to authenticate users via a third-party IdP (Google, GitHub, Okta, Auth0) rather than running your own password stack. The modern answer is <strong>OAuth 2.0 Authorization Code + PKCE</strong> with an OIDC-capable library; implicit and password grants are deprecated.</p>
<pre><code>// openid-client — reference-quality OIDC/OAuth2 library
import { Issuer, generators } from "openid-client";

const issuer = await Issuer.discover("https://accounts.google.com");
const client = new issuer.Client({
  client_id: process.env.GOOGLE_CLIENT_ID,
  client_secret: process.env.GOOGLE_CLIENT_SECRET,
  redirect_uris: ["https://app.example.com/auth/callback"],
  response_types: ["code"],
});

app.get("/auth/login", (req, res) =&gt; {
  const code_verifier = generators.codeVerifier();
  const code_challenge = generators.codeChallenge(code_verifier);
  const state = generators.state();
  const nonce = generators.nonce();

  // Store in a signed short-lived cookie or server session
  req.session.pkce = { code_verifier, state, nonce };

  res.redirect(client.authorizationUrl({
    scope: "openid email profile",
    code_challenge,
    code_challenge_method: "S256",
    state, nonce,
  }));
});

app.get("/auth/callback", async (req, res, next) =&gt; {
  try {
    const params = client.callbackParams(req);
    const { code_verifier, state, nonce } = req.session.pkce;
    delete req.session.pkce;

    const tokenSet = await client.callback(
      "https://app.example.com/auth/callback",
      params,
      { state, nonce, code_verifier },
    );

    const profile = await client.userinfo(tokenSet.access_token);
    const user = await findOrCreateByEmail(profile.email, profile);

    // Issue your own session/JWT — don't expose OAuth tokens to the browser
    req.session.userId = user.id;
    res.redirect("/");
  } catch (e) { next(e); }
});

// Refresh tokens (if used) stored server-side, rotated on each use
async function refreshIfNeeded(tokenSet) {
  if (!tokenSet.expired()) return tokenSet;
  return client.refresh(tokenSet.refresh_token);
}</code></pre>
<p><strong>Trade-offs &amp; rules:</strong> <strong>PKCE is mandatory</strong> now, even for confidential clients — protects against authorization code interception. Always validate <code>state</code> (CSRF) and <code>nonce</code> (ID token replay). <strong>Never expose access/refresh tokens to the browser</strong> — store them server-side and issue an app-side session cookie; if the SPA must talk to APIs, proxy through your backend. Request <strong>minimum scopes</strong>; re-consent for upgrades. On sign-out, revoke the refresh token at the IdP and invalidate your local session. For enterprise SSO (SAML), add <strong>passport-saml</strong> or use <strong>WorkOS</strong>/<strong>Auth0</strong>/<strong>Clerk</strong>/<strong>Supabase Auth</strong>, which unify OAuth + SAML + MFA behind one API — for most teams <em>buy</em> beats build. For machine-to-machine auth use <code>client_credentials</code> grant; prefer <code>private_key_jwt</code> over client secrets.</p>
'''

ANSWERS[34] = r'''
<p><strong>Situation:</strong> Team needs a dev/ops CLI (database migrations, cache invalidation, backfills, usage reports) installed via <code>npm install -g</code> or run via <code>npx</code>. The recipe: shebang, <code>bin</code> field, a parser (commander/yargs/oclif), a spinner/prompts library.</p>
<pre><code>// bin/mytool.js — shebang line makes it directly executable
#!/usr/bin/env node
import { Command } from "commander";
import chalk from "chalk";
import ora from "ora";
import { prompt } from "enquirer";

const program = new Command();
program
  .name("mytool")
  .version("1.2.0")
  .description("Ops CLI for our platform");

program
  .command("db:migrate")
  .description("Run pending DB migrations")
  .option("--dry-run", "print SQL without executing")
  .option("--to &lt;name&gt;", "target migration")
  .action(async (opts) =&gt; {
    const spinner = ora("Connecting to DB...").start();
    try {
      await connectDb();
      spinner.succeed("Connected");
      const pending = await listPending();
      if (!pending.length) return console.log(chalk.green("All migrations applied."));
      if (!opts.dryRun) {
        const { ok } = await prompt({ type: "confirm", name: "ok",
          message: `Apply ${pending.length} migrations to ${process.env.DB_URL_MASKED}?` });
        if (!ok) process.exit(1);
      }
      for (const m of pending) {
        const s = ora(`Applying ${m.name}`).start();
        await apply(m, opts.dryRun);
        s.succeed(m.name);
      }
    } catch (e) {
      spinner.fail(chalk.red(e.message));
      process.exit(1);
    }
  });

program
  .command("cache:purge &lt;pattern&gt;")
  .description("Delete Redis keys matching glob")
  .option("--json", "output machine-readable")
  .action(async (pattern, opts) =&gt; {
    const count = await redis.purge(pattern);
    if (opts.json) console.log(JSON.stringify({ purged: count }));
    else console.log(chalk.yellow(`Purged ${count} keys`));
  });

program.parseAsync();</code></pre>
<pre><code>// package.json
{
  "name": "@myorg/mytool",
  "version": "1.2.0",
  "type": "module",
  "bin": { "mytool": "bin/mytool.js" },
  "files": ["bin", "dist"],
  "engines": { "node": "&gt;=20" }
}</code></pre>
<p><strong>Trade-offs:</strong> <strong>commander</strong> is the simplest; <strong>yargs</strong> richer; <strong>oclif</strong> (Heroku/Salesforce) shines for multi-command CLIs with plugins and auto-docs; <strong>clipanion</strong> (Yarn) for TS-first class-based; <strong>ink</strong> when you need interactive UIs (tables, spinners, forms) in React. Always include <strong>structured <code>--json</code> output</strong> so it can be scripted. Exit codes matter: <code>0</code> success, <code>1</code> failure, <code>2+</code> semantic ("nothing to do", "aborted"). Use <strong>dotenv</strong> / <strong>Zod</strong> for config so the same env validation rules apply as in services. Distribute: publish to internal npm registry, or pre-build single binaries with <code>pkg</code>/<code>nexe</code>/<code>@yao-pkg/pkg</code> / Node's experimental <code>--experimental-sea-config</code>. Add <strong><code>update-notifier</code></strong> for friendly version nags. Write <strong>--help</strong> well — it's documentation.</p>
'''

ANSWERS[35] = r'''
<p><strong>Situation:</strong> You have dozens of env vars (DB URLs, API keys, Stripe secrets, JWT signing keys). Goals: validate at boot, scope per environment, keep secrets out of git, rotate without redeploy. The layered answer is dotenv/native env-file for local → platform-injected for prod → secret manager for sensitive values, all parsed through a Zod schema.</p>
<pre><code>// .env.example  — committed; documents every required variable
NODE_ENV=development
PORT=3000
DATABASE_URL=postgres://...
JWT_SECRET=change_me_min_32_chars
STRIPE_SECRET_KEY=

// .env.local  — gitignored; real local values
// Load with Node 20.6+ built-in: `node --env-file=.env.local server.js`

// src/config.ts — single source of truth, validated
import { z } from "zod";
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

const Env = z.object({
  NODE_ENV: z.enum(["development", "staging", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  STRIPE_SECRET_KEY: z.string().startsWith("sk_"),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
});

async function fetchSecrets() {
  if (process.env.NODE_ENV === "development") return {};
  const sm = new SecretsManagerClient({});
  const out = await sm.send(new GetSecretValueCommand({ SecretId: `app/${process.env.NODE_ENV}` }));
  return JSON.parse(out.SecretString);            // merge into process.env
}

export async function loadConfig() {
  const secrets = await fetchSecrets();
  return Env.parse({ ...process.env, ...secrets });
}

// Fail fast on boot — a typo in a var shouldn't surface during request handling
export const config = await loadConfig();</code></pre>
<p><strong>Trade-offs &amp; rules:</strong> <strong>Config ≠ secrets.</strong> Config (PORT, LOG_LEVEL) — plain env vars fine, committed defaults in <code>.env.example</code>. Secrets (DB passwords, API keys, JWT signing keys) — <strong>AWS Secrets Manager / GCP Secret Manager / HashiCorp Vault / Doppler</strong>; fetch at boot; never log. Use a single manager per org — don't sprinkle secrets across Git, Slack, and spreadsheets. <strong>Rotate</strong> on a schedule (secrets managers automate this); for DB and API keys, use short-lived credentials (IAM database auth, STS) over static passwords where possible. In <strong>Kubernetes</strong> mount secrets via CSI driver (External Secrets Operator syncs from Vault/SM into Secrets). In Lambda/Fargate inject via task definition's <code>secrets</code> field. Never commit <code>.env</code>; if it leaks, <strong>rotate immediately</strong> — history lives forever. Redact env from logs (<code>pino.redact</code>) and error traces (Sentry scrubbing). Keep <strong>per-env files</strong> (<code>.env.staging</code>, <code>.env.production</code>) only for non-secret config; secrets always come from the manager.</p>
'''

ANSWERS[36] = r'''
<p><strong>Situation:</strong> Browser-based frontend on <code>app.example.com</code> calls API at <code>api.example.com</code>. Browser same-origin policy blocks cross-origin requests unless the API replies with appropriate <code>Access-Control-Allow-*</code> headers. Use the <code>cors</code> package with a strict allowlist — never <code>*</code> for authenticated APIs.</p>
<pre><code>import cors from "cors";

const allowedOrigins = [
  "https://app.example.com",
  "https://admin.example.com",
  /^https:\/\/pr-\d+\.preview\.example\.com$/,     // ephemeral PR envs via regex
  ...(process.env.NODE_ENV === "development" ? ["http://localhost:5173"] : []),
];

app.use(cors({
  origin(origin, cb) {
    if (!origin) return cb(null, true);            // Same-origin / curl / server-to-server
    const ok = allowedOrigins.some(a =&gt; typeof a === "string" ? a === origin : a.test(origin));
    cb(ok ? null : new Error(`CORS: ${origin} not allowed`), ok);
  },
  credentials: true,                                // allow cookies/auth headers
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization", "X-Request-Id"],
  exposedHeaders: ["X-Request-Id", "X-RateLimit-Remaining"],
  maxAge: 86400,                                    // cache preflight 24h — reduces OPTIONS traffic
}));

// IMPORTANT: Register cors before auth/body-parser so preflight OPTIONS works without a token</code></pre>
<p><strong>Trade-offs &amp; rules:</strong> the key mental model: <strong>CORS is the browser trusting the server's say-so</strong> — the server states which origins may read its responses; the browser enforces. It's <em>not</em> a server security boundary — anyone can still call your API with curl. <strong>Never use <code>origin: "*"</code> with <code>credentials: true</code></strong> — the spec forbids it; always reflect a specific origin. Preflight (<code>OPTIONS</code>) happens when the request is "non-simple" (custom headers, methods beyond GET/POST, <code>Content-Type: application/json</code>); cache with <code>maxAge</code> to cut latency. For <strong>credentials</strong> (cookies, <code>Authorization</code> header) both server (<code>Access-Control-Allow-Credentials: true</code>) <em>and</em> frontend (<code>fetch(..., { credentials: "include" })</code>) must opt in. Prefer <strong>SameSite=Lax/Strict cookies</strong> to reduce CSRF need. <strong>Don't bypass CORS</strong> by writing a proxy — fix the headers. Apply CORS only to public-facing APIs; internal service-to-service calls don't use browsers, so CORS doesn't apply. Log blocked origins — unexpected ones hint at a misconfigured frontend or a probing attacker.</p>
'''

ANSWERS[37] = r'''
<p><strong>Situation:</strong> Need to run tasks on a schedule: nightly reports, hourly cache warmers, weekly cleanup. Bad choice: <code>setInterval</code> inside the API — drifts, stops on restart, fires N times under horizontal scaling. Good choices range from in-process <code>node-cron</code> → distributed queue with repeatable jobs → external scheduler (EventBridge, K8s CronJob).</p>
<pre><code>// BullMQ repeatable job — runs once across the fleet (distributed lock in Redis)
import { Queue, Worker } from "bullmq";
const connection = { host: "redis", port: 6379 };

const q = new Queue("schedules", { connection });

// Define schedules at app start; idempotent — safe to re-run on every deploy
await q.add(
  "daily-report",
  {},
  {
    repeat: { pattern: "0 3 * * *", tz: "Asia/Kolkata" },    // 3 AM IST every day
    attempts: 5,
    backoff: { type: "exponential", delay: 60_000 },
    removeOnComplete: 100,
    removeOnFail: 50,
    jobId: "daily-report",                                   // stable ID — no duplicates
  }
);

await q.add("hourly-cache-warmup", {}, {
  repeat: { pattern: "0 * * * *" },
  jobId: "hourly-cache-warmup",
});

// Worker — deploy as separate replicas (can be one or many)
new Worker("schedules", async (job) =&gt; {
  switch (job.name) {
    case "daily-report": return runDailyReport();
    case "hourly-cache-warmup": return warmCache();
  }
}, { connection, concurrency: 1 });</code></pre>
<pre><code># K8s CronJob — outside the app entirely, launches a one-shot container
apiVersion: batch/v1
kind: CronJob
metadata: { name: nightly-etl }
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: etl
              image: myorg/etl:v1.2.3
              args: ["node", "dist/jobs/nightly-etl.js"]</code></pre>
<p><strong>Trade-offs:</strong> <strong>In-process <code>node-cron</code></strong> — only OK for a single-instance app; breaks horizontally. <strong>BullMQ repeatable jobs</strong> — the Node sweet spot for most teams: Redis handles leader election, retries, DLQ, observability (Bull Board). <strong>Cloud-native (EventBridge Scheduler, GCP Cloud Scheduler, K8s CronJob)</strong> — schedules live outside your app; survives deploys and crashes; triggers HTTP or Lambda; best for ops-owned jobs. <strong>Temporal/Inngest</strong> for durable workflows with retries, human steps, multi-day duration. <strong>Always make jobs idempotent</strong> — they may fire twice. Always <strong>specify timezone</strong> — server UTC vs business timezone is the most common bug. <strong>Observability</strong>: emit metrics (duration, success rate); alert on "last run older than N" — silent missed runs are the dangerous mode. Keep one writer per job to avoid double-send (email, payment) surprises.</p>
'''

ANSWERS[38] = r'''
<p><strong>Situation:</strong> Users need real-time notifications — new message, order update, alert — delivered as soon as the event occurs. WebSockets keep a persistent socket so the server pushes without polling. Scale across instances with a Redis pub/sub adapter; persist delivery so offline users catch up on reconnect.</p>
<pre><code>// Server — Socket.IO with Redis adapter, per-user rooms
import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
import { createClient } from "redis";
import { verifyJwt } from "./auth.js";

const pub = createClient({ url: process.env.REDIS_URL });
const sub = pub.duplicate();
await Promise.all([pub.connect(), sub.connect()]);

const io = new Server(httpServer, { cors: { origin: /^https:\/\/.*\.example\.com$/ } });
io.adapter(createAdapter(pub, sub));                 // broadcast across replicas

// Authenticate on handshake — reject early
io.use(async (socket, next) =&gt; {
  try {
    const user = await verifyJwt(socket.handshake.auth.token);
    socket.data.user = user;
    next();
  } catch { next(new Error("unauthorized")); }
});

io.on("connection", async (socket) =&gt; {
  const userId = socket.data.user.id;
  socket.join(`user:${userId}`);                     // personal room

  // Deliver pending/missed notifications since last seen
  const backlog = await redis.zrangebyscore(`notif:${userId}`, socket.handshake.query.lastTs || 0, "+inf");
  for (const n of backlog) socket.emit("notification", JSON.parse(n));
});

// Publishing side — any service can call notifyUser
export async function notifyUser(userId, payload) {
  await redis.zadd(`notif:${userId}`, Date.now(), JSON.stringify(payload));   // persist
  await redis.expire(`notif:${userId}`, 7 * 86400);
  io.to(`user:${userId}`).emit("notification", payload);                       // push (if connected)
}</code></pre>
<p><strong>Trade-offs:</strong> <strong>Redis adapter</strong> is essential for multi-replica deploys — any server can emit to any connected client. <strong>Authenticate on handshake</strong>, never after — the token should be valid for the whole connection (or require refresh). <strong>Per-user rooms</strong> scale better than broadcast + filter. <strong>Heartbeat</strong> (default 25s/20s timeout) detects zombies; tune per proxy idle timeouts (ALB 60s default). <strong>Persist notifications</strong> (Redis sorted set, Postgres, DynamoDB) so offline users don't miss them — on reconnect, deliver backlog since <code>lastTs</code>. Layer with <strong>push notifications</strong> (APNs/FCM) so mobile users who aren't on the page still receive critical alerts. <strong>Alternatives:</strong> <strong>SSE</strong> (server-sent events) is simpler, one-way, fits most notification use cases, works over HTTP/2. <strong>Managed services</strong> (Pusher, Ably, Cloudflare Realtime, Supabase Realtime) skip the infra — pay for scale. For millions of concurrent connections per node, <strong>uWebSockets.js</strong> outperforms Socket.IO.</p>
'''

ANSWERS[39] = r'''
<p><strong>Situation:</strong> Endpoint needs to export a potentially large table as CSV — naively calling <code>res.send(rows.map(toCsv).join("\n"))</code> OOMs on a few million rows. The answer: stream-build the CSV row by row while streaming the DB result set, so constant memory regardless of row count.</p>
<pre><code>import { stringify } from "csv-stringify";
import { pipeline } from "node:stream/promises";
import pg from "pg";
import QueryStream from "pg-query-stream";

app.get("/exports/orders.csv", authRequired, async (req, res, next) =&gt; {
  const pool = req.app.locals.pool as pg.Pool;
  const client = await pool.connect();
  try {
    // Headers first — browser downloads with nice filename
    res.setHeader("Content-Type", "text/csv; charset=utf-8");
    res.setHeader("Content-Disposition",
      `attachment; filename="orders-${new Date().toISOString().slice(0,10)}.csv"`);
    res.setHeader("Cache-Control", "no-store");
    res.write("\uFEFF");   // BOM so Excel detects UTF-8

    // DB cursor stream — doesn't buffer entire result
    const query = new QueryStream(
      `SELECT id, created_at, user_id, total_cents, status
       FROM orders
       WHERE tenant_id = $1 AND created_at &gt;= $2
       ORDER BY id`,
      [req.user.tenantId, req.query.since ?? "2020-01-01"],
      { batchSize: 1000 }
    );
    const dbStream = client.query(query);

    // CSV formatter — transforms rows to lines with proper quoting/escaping
    const csv = stringify({
      header: true,
      columns: ["id", "created_at", "user_id", "total_cents", "status"],
    });

    // pipeline handles backpressure + cleanup on error
    await pipeline(dbStream, csv, res);
  } catch (e) {
    next(e);
  } finally {
    client.release();
  }
});</code></pre>
<p><strong>Trade-offs:</strong> <strong>Stream</strong> end-to-end — DB cursor → transform → HTTP response. <code>pipeline()</code> connects them, propagates backpressure (DB fetches next page only when HTTP can accept more), and cleans up on error. Without this, a single big export freezes the instance. Use <strong>batchSize 500-5000</strong> to balance DB round-trips vs memory. <strong>CSV quoting</strong>: use a library (<code>csv-stringify</code>, <code>@fast-csv/format</code>) — manual escaping drops rows with commas, newlines, or quotes. Include <strong>BOM</strong> (<code>"\uFEFF"</code>) at start for Excel UTF-8 detection. For very large exports (&gt; 100k rows) <strong>queue the job</strong> — generate to S3 in background, email a signed download link; synchronous HTTP has proxy timeouts (ALB 60s default) that will kill the connection. Always set <code>Content-Disposition: attachment</code> with a safe filename (URL-encode user-derived parts). Filter by tenant/permission before the query — never after. For Excel output use <code>exceljs</code> streaming writer; for JSON-to-CSV on arbitrary shapes, <code>json2csv</code>.</p>
'''

ANSWERS[40] = r'''
<p><strong>Situation:</strong> Single Node process uses one CPU core regardless of how powerful the machine is. The <code>cluster</code> module forks N worker processes (typically one per core) that share the same listening port via the OS, giving multi-core utilization inside one host.</p>
<pre><code>import cluster from "node:cluster";
import os from "node:os";
import process from "node:process";

if (cluster.isPrimary) {
  const n = Number(process.env.WORKERS) || os.availableParallelism();
  console.log(`Primary ${process.pid} spawning ${n} workers`);
  for (let i = 0; i &lt; n; i++) cluster.fork();

  // Zero-downtime reload — restart one worker at a time on SIGHUP
  process.on("SIGHUP", async () =&gt; {
    for (const w of Object.values(cluster.workers || {})) {
      await new Promise((resolve) =&gt; {
        w.once("exit", resolve);
        w.send("shutdown");
      });
      cluster.fork();
    }
  });

  // Auto-respawn crashed workers
  cluster.on("exit", (worker, code, signal) =&gt; {
    console.warn(`worker ${worker.process.pid} died (${signal || code}); restarting`);
    if (!worker.exitedAfterDisconnect) cluster.fork();
  });
} else {
  // Worker — regular app code; all workers listen on the same port (OS round-robin)
  const app = await import("./app.js");
  const server = app.default.listen(process.env.PORT || 3000);

  // Graceful shutdown on message from primary
  process.on("message", (msg) =&gt; {
    if (msg === "shutdown") {
      server.close(() =&gt; process.exit(0));
      setTimeout(() =&gt; process.exit(1), 30_000).unref();   // hard stop
    }
  });
}</code></pre>
<p><strong>Trade-offs &amp; rules:</strong> each worker is a separate process with its own memory — <strong>state must be external</strong> (Redis for sessions/cache, DB for data). In-memory caches aren't shared across workers. <strong>Modern alternative: let the orchestrator cluster for you</strong> — one Node process per container, N containers per host, managed by K8s/ECS. This is simpler (no cluster code), gives per-pod resource limits, easier graceful shutdown, and pod-level autoscaling. For small apps on a VM, <strong>PM2</strong> (<code>pm2 start app.js -i max</code>) wraps <code>cluster</code> with monitoring and reload — production-ready without writing the primary code above. Use <strong><code>SO_REUSEPORT</code></strong> (Node's default behavior via cluster) so the kernel load-balances, not the primary — much better under load. Sizing: <code>workers = cores</code> for CPU-heavy, or <code>cores × 2</code> if I/O-heavy. <strong>Don't</strong> run <code>cluster</code> inside a container on K8s — double-scaling wastes memory; use one process per pod. <strong>Graceful shutdown</strong> on SIGTERM: fail readiness, drain in-flight requests, close DB pool, exit — avoids 5xx during deploys.</p>
'''

ANSWERS[41] = r'''
<p><strong>Situation:</strong> one big Node codebase is slowing a growing team — deploys take an hour, a payment-service bug blocks a search-service ship. You're considering splitting into microservices.</p>
<p><strong>Approach:</strong> structure a monorepo by bounded context, one service per domain. Extract only when you <em>need</em> independent deploys, scaling, or team ownership. Start with a modular monolith; migrate piece by piece.</p>
<pre><code>monorepo/
├── packages/
│   ├── shared/                 # types, client SDKs, proto files, logger
│   ├── config/                 # Zod env schema, shared across services
│   └── testing/                # shared fixtures, testcontainers helpers
├── services/
│   ├── users/
│   │   ├── src/
│   │   │   ├── app.ts          # Express/Fastify entry
│   │   │   ├── domain/         # pure logic, no framework
│   │   │   ├── http/           # controllers
│   │   │   └── events/         # Kafka/NATS consumers + publishers
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── orders/
│   └── notifications/
├── infra/
│   ├── docker-compose.yml      # local stack: kafka, redis, postgres
│   └── k8s/
├── turbo.json                  # Turborepo task graph + caching
└── pnpm-workspace.yaml</code></pre>
<ul>
  <li><strong>Communication:</strong> sync via HTTP/gRPC for request-response; async via Kafka/NATS/SQS for events. Prefer async — decouples lifecycle.</li>
  <li><strong>Data ownership:</strong> each service owns its DB. No cross-service DB queries. Query via API; replicate read projections via events (CQRS).</li>
  <li><strong>API gateway</strong> (Envoy, Kong, AWS API Gateway) fronts the mesh — auth, rate limit, routing, observability.</li>
  <li><strong>Contracts:</strong> OpenAPI (REST), <code>.proto</code> (gRPC), Avro/JSON Schema (events). Contract tests (Pact) catch breakage pre-deploy.</li>
  <li><strong>Observability from day 1:</strong> OpenTelemetry (traces propagated across hops), correlated logs (<code>traceId</code> everywhere), RED metrics per service.</li>
  <li><strong>Resilience:</strong> timeouts, retries with jitter, circuit breakers (cockatiel), bulkheads.</li>
</ul>
<p><strong>Trade-offs:</strong> microservices multiply operational complexity — service discovery, distributed tracing, network failures become daily concerns. A "distributed monolith" (microservices that call each other synchronously for every operation) is worse than the monolith you fled. Extract only when the domain is mature enough to have stable boundaries. For teams &lt; 20, a modular monolith with clear package boundaries often beats microservices.</p>
'''

ANSWERS[42] = r'''
<p><strong>Situation:</strong> default Express 500 pages leak stack traces; each route hand-crafts error responses differently; clients can't programmatically distinguish "not found" from "validation failed."</p>
<p><strong>Approach:</strong> typed error classes with HTTP status and code; a single error-handling middleware at the end; RFC 7807 (<code>application/problem+json</code>) or a consistent envelope; never leak stack traces in prod.</p>
<pre><code>// Typed error hierarchy
export class AppError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) { super(message); this.name = this.constructor.name; }
}
export class NotFound extends AppError {
  constructor(resource: string, id?: string) {
    super(404, "NOT_FOUND", `${resource}${id ? ` ${id}` : ""} not found`);
  }
}
export class ValidationError extends AppError {
  constructor(details: unknown) { super(400, "VALIDATION_ERROR", "invalid input", details); }
}
export class Forbidden extends AppError {
  constructor() { super(403, "FORBIDDEN", "not allowed"); }
}

// Routes throw; no res.status(500) scattered about
app.get("/users/:id", async (req, res) =&gt; {
  const u = await db.user.findUnique({ where: { id: req.params.id } });
  if (!u) throw new NotFound("User", req.params.id);
  res.json(u);
});

// Central error middleware — LAST in the chain
app.use((err, req, res, _next) =&gt; {
  // Convert known framework errors
  if (err?.issues) err = new ValidationError(err.issues);          // Zod
  if (err?.code === "P2002") err = new AppError(409, "CONFLICT", "already exists");   // Prisma

  const appErr = err instanceof AppError ? err : new AppError(500, "INTERNAL", "internal error");

  (appErr.status &gt;= 500 ? log.error : log.warn).call(log, {
    err, reqId: req.id, userId: req.user?.id, url: req.url,
  }, appErr.message);

  res.status(appErr.status).json({
    error: {
      code: appErr.code,
      message: appErr.message,
      details: appErr.details,
      requestId: req.id,
    },
    ...(process.env.NODE_ENV !== "production" &amp;&amp; { stack: err.stack }),
  });
});

// Async-safe in Express 5 (rejected promises auto-forward). In Express 4:
import "express-async-errors";</code></pre>
<p><strong>Trade-offs:</strong> RFC 7807 problem details (<code>type</code>, <code>title</code>, <code>status</code>, <code>detail</code>, <code>instance</code>) is the standard for public APIs; an <code>{ error: { code, message } }</code> envelope is fine for internal. Never return 500 for validation issues (400) or auth failures (401/403) — clients make wrong decisions. Log 5xx; suppress noise from 4xx (but count them for trend alerting). Include a <code>requestId</code> in every response so support tickets find the exact log line. Never echo user input in error messages without escaping — XSS vectors hide in "unknown value 'alert(1)'" responses.</p>
'''

ANSWERS[43] = r'''
<p><strong>Situation:</strong> you want schema-driven validation in a JS-leaning codebase where Zod's TS-inference is overkill; Joi's mature feature set and cross-field conditionals fit better.</p>
<p><strong>Approach:</strong> centralize schemas per resource; wrap Joi in one middleware factory; strip unknowns; collect all errors; coerce where helpful.</p>
<pre><code>import Joi from "joi";

// Schema module — one per resource
export const createUserSchema = Joi.object({
  email: Joi.string().email().lowercase().trim().required(),
  password: Joi.string().min(12).max(128)
    .pattern(/[A-Z]/, "uppercase")
    .pattern(/[0-9]/, "digit").required(),
  age: Joi.number().integer().min(13).max(120).required(),
  role: Joi.string().valid("admin", "editor", "viewer").default("viewer"),
  profile: Joi.object({
    name: Joi.string().min(1).max(100).required(),
    phone: Joi.string().pattern(/^\+[1-9]\d{7,14}$/).optional(),
  }).required(),
}).options({ abortEarly: false, stripUnknown: true });

export const updateUserSchema = createUserSchema
  .fork(["password", "email"], (s) =&gt; s.optional());   // PATCH variant

// Reusable middleware factory
export const validate = (schema, source = "body") =&gt; (req, res, next) =&gt; {
  const { value, error } = schema.validate(req[source]);
  if (error) return res.status(400).json({
    error: "VALIDATION_ERROR",
    details: error.details.map(d =&gt; ({
      path: d.path.join("."), type: d.type, message: d.message,
    })),
  });
  req[source] = value;        // coerced + defaults filled in
  next();
};

app.post("/users", validate(createUserSchema), (req, res) =&gt; { /* req.body is safe */ });
app.patch("/users/:id", validate(updateUserSchema), handler);</code></pre>
<p><strong>Advanced Joi features:</strong></p>
<ul>
  <li><code>Joi.ref("password")</code> for cross-field rules (<code>confirmPassword: Joi.any().valid(Joi.ref("password"))</code>).</li>
  <li><code>Joi.when</code> for conditional validation (<code>zip</code> required only when <code>country === "US"</code>).</li>
  <li><code>.extend</code> to create custom types (E.164 phone, semantic version, tenant-scoped ID).</li>
  <li><code>.concat</code> to compose a shared base schema with resource-specific rules.</li>
  <li><code>celebrate</code> (Joi + Express wiring) gives a more structured integration.</li>
</ul>
<p><strong>Trade-offs:</strong> Joi is JS-first — no automatic TypeScript types. In TS codebases, Zod's <code>z.infer</code> eliminates a whole class of drift. For JS or legacy Node repos, Joi is fully mature and widely understood. <strong>Don't</strong> validate only client-side; the server is the sole trust boundary. Return structured error details (path + code, not free-text) so frontends can i18n messages. Always <code>abortEarly: false</code> in user-facing forms so you surface all mistakes at once.</p>
'''

ANSWERS[44] = r'''
<p><strong>Situation:</strong> storing plaintext passwords is negligence; MD5/SHA-256 are too fast for password hashing. You need a memory-hard, tunable KDF with salt per user.</p>
<p><strong>Approach:</strong> use <strong>Argon2id</strong> (OWASP first choice in 2026) via <code>argon2</code>; fall back to <strong>scrypt</strong> (built into <code>node:crypto</code>) if you can't add a native dep; <strong>bcrypt</strong> is still acceptable but 72-byte input cap and lower memory hardness make it second-tier.</p>
<pre><code>import argon2 from "argon2";

async function register(email, plainPassword) {
  const passwordHash = await argon2.hash(plainPassword, {
    type: argon2.argon2id,
    memoryCost: 19456,      // ~19 MiB — OWASP minimum (2026)
    timeCost: 2,
    parallelism: 1,
  });
  return db.user.create({ data: { email, passwordHash } });
}

async function login(email, plainPassword) {
  const user = await db.user.findUnique({ where: { email } });
  // Run verify even if user missing — avoids timing oracle
  const dummy = "$argon2id$v=19$m=19456,t=2,p=1$YWJj$YWJj";
  const valid = await argon2.verify(user?.passwordHash ?? dummy, plainPassword);
  if (!user || !valid) throw new AppError(401, "INVALID_CREDENTIALS", "wrong email or password");

  // Rehash if parameters have upgraded since the hash was created
  if (argon2.needsRehash(user.passwordHash, { memoryCost: 19456, timeCost: 2 })) {
    const fresh = await argon2.hash(plainPassword, { type: argon2.argon2id, memoryCost: 19456, timeCost: 2 });
    await db.user.update({ where: { id: user.id }, data: { passwordHash: fresh } });
  }
  return user;
}

// scrypt — zero-dep alternative using node:crypto
import { scrypt, randomBytes, timingSafeEqual } from "node:crypto";
import { promisify } from "node:util";
const scryptAsync = promisify(scrypt);

async function scryptHash(password) {
  const salt = randomBytes(16);
  const key = await scryptAsync(password, salt, 64, { N: 2 ** 17, r: 8, p: 1 });
  return `scrypt:${salt.toString("hex")}:${key.toString("hex")}`;
}
async function scryptVerify(stored, password) {
  const [, saltHex, keyHex] = stored.split(":");
  const key = Buffer.from(keyHex, "hex");
  const derived = await scryptAsync(password, Buffer.from(saltHex, "hex"), 64, { N: 2 ** 17, r: 8, p: 1 });
  return timingSafeEqual(key, derived);
}</code></pre>
<p><strong>Trade-offs:</strong> <strong>Never</strong> use <code>createHash("sha256")</code> for passwords — it's designed to be fast, which helps attackers. Argon2id (hybrid) resists both GPU and side-channel attacks. Tune parameters so a single verify takes ~0.5-1 s on your hardware; faster = weaker. Always pair with rate limiting, account lockout (5 failed attempts → 15 min lockout), and a breached-password check (Have I Been Pwned k-anonymity API) at registration. Rotate parameters yearly — old hashes get upgraded on next login via <code>needsRehash</code>. <strong>PBKDF2</strong> is only acceptable for legacy compatibility; avoid for new systems.</p>
'''

ANSWERS[45] = r'''
<p><strong>Situation:</strong> signups need welcome emails, orders need receipts, password resets need secure reset links. Sending from your SMTP server invites deliverability issues — use a transactional provider.</p>
<p><strong>Approach:</strong> choose a provider (Resend, Postmark, SES, SendGrid) by reliability + price + DX; enqueue email sends as background jobs (never await in the HTTP response); template with MJML/React Email; retry on transient failures; log every attempt.</p>
<pre><code>import { Resend } from "resend";
const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendEmail({ to, subject, html, text, replyTo, tags }) {
  const { data, error } = await resend.emails.send({
    from: "App &lt;no-reply@app.example.com&gt;",
    to, subject, html, text, replyTo,
    tags: Object.entries(tags ?? {}).map(([name, value]) =&gt; ({ name, value })),
  });
  if (error) throw Object.assign(new Error(error.message), { transient: error.statusCode &gt;= 500 });
  return data.id;
}

// queue.ts — BullMQ queue + worker
import { Queue, Worker } from "bullmq";
export const emailQueue = new Queue("email", { connection: redisCfg });

new Worker("email", async (job) =&gt; {
  const { to, template, data } = job.data;
  const { subject, html, text } = await renderTemplate(template, data);  // MJML → HTML + text
  return sendEmail({ to, subject, html, text, tags: { template } });
}, {
  connection: redisCfg,
  concurrency: 20,
  limiter: { max: 100, duration: 1000 },   // 100/s to stay within provider quota
});

app.post("/auth/register", async (req, res) =&gt; {
  const user = await createUser(req.body);
  await emailQueue.add("welcome", { to: user.email, template: "welcome", data: { name: user.name } }, {
    attempts: 5,
    backoff: { type: "exponential", delay: 2000 },
    jobId: `welcome:${user.id}`,         // idempotent — duplicate retries don't re-send
  });
  res.status(201).json({ id: user.id });
});</code></pre>
<p><strong>Deliverability essentials:</strong></p>
<ul>
  <li><strong>SPF, DKIM, DMARC</strong> on your sending domain — without these, mail lands in spam.</li>
  <li><strong>Dedicated sending domain</strong> (<code>mail.example.com</code>) separate from marketing — a bad campaign won't kill transactional.</li>
  <li><strong>Both HTML and plain-text</strong> parts (spam filters weight the ratio).</li>
  <li><strong>Unsubscribe link</strong> required by CAN-SPAM/GDPR even for transactional if there's any promotional content.</li>
  <li><strong>Handle bounces + complaints</strong> via webhook; auto-suppress hard-bounced addresses.</li>
</ul>
<p><strong>Trade-offs:</strong> running your own SMTP is technically possible but operationally punishing (IP warming, reputation, DMARC reporting). Providers absorb that work. React Email + MJML gives good DX without the "rendering HTML email is hard" pain. For critical mail (password reset), set the job attempt count high and alert on DLQ — losing a reset email is a security incident.</p>
'''

ANSWERS[46] = r'''
<p><strong>Situation:</strong> you need reliable, reproducible deploys across dev/staging/prod with the same image, regardless of the host OS.</p>
<p><strong>Approach:</strong> multi-stage Dockerfile (build with full toolchain, run with minimal image), non-root user, pinned base, healthcheck, proper signal handling; orchestrate with Kubernetes, ECS, Cloud Run, or Fly.io.</p>
<pre><code># syntax=docker/dockerfile:1.7
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build            # tsc, esbuild, whatever

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    NODE_OPTIONS="--enable-source-maps" \
    PORT=3000
USER node
COPY --from=deps  --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
COPY --from=build --chown=node:node /app/package.json ./
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD node -e "fetch('http://localhost:3000/health').then(r=&gt;process.exit(r.ok?0:1)).catch(()=&gt;process.exit(1))"
CMD ["node", "dist/server.js"]</code></pre>
<pre><code># docker-compose.yml — local dev stack
services:
  api:
    build: .
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app
      REDIS_URL: redis://redis:6379
    depends_on: { db: { condition: service_healthy }, redis: { condition: service_started } }
  db:
    image: postgres:16-alpine
    environment: { POSTGRES_USER: app, POSTGRES_PASSWORD: app, POSTGRES_DB: app }
    healthcheck: { test: ["CMD", "pg_isready", "-U", "app"], interval: 5s }
  redis:
    image: redis:7-alpine</code></pre>
<ul>
  <li><strong>Image size:</strong> alpine (~50 MB) or <code>gcr.io/distroless/nodejs22-debian12</code> (~80 MB, no shell — less attack surface).</li>
  <li><strong>Layer order:</strong> copy <code>package*.json</code> first so <code>npm ci</code> layer caches survive code edits.</li>
  <li><strong>Signals:</strong> exec-form <code>CMD</code> (array) so Node is PID 1 and receives SIGTERM. For many short-lived processes, use <code>tini</code> as init to reap zombies.</li>
  <li><strong>Secrets:</strong> never baked into the image. Inject at runtime (K8s Secret → env, ECS task secrets).</li>
  <li><strong>Security:</strong> scan with Trivy/Grype in CI; sign with Cosign; SBOM (CycloneDX). Pin digests, not just tags.</li>
  <li><strong>Don't run <code>npm start</code></strong> — it forks npm which may swallow signals; call Node directly.</li>
</ul>
<p><strong>Trade-offs:</strong> containers excel at reproducibility + portability but add an ops layer. For small apps on a single VM, PM2 + Node directly is simpler. On K8s, one Node process per pod and let the orchestrator cluster — don't use Node's <code>cluster</code> inside a container (double scaling wastes memory and complicates graceful shutdown).</p>
'''

ANSWERS[47] = r'''
<p><strong>Situation:</strong> users upload multi-GB video or backup files. Buffering in memory is impossible; the server needs to accept the stream, validate it in flight, and persist without ever holding the whole thing.</p>
<p><strong>Approach:</strong> parse multipart/form-data with busboy (stream-first), validate size and MIME as chunks arrive, pipe directly to S3's multipart upload — or better, issue pre-signed PUT URLs and let clients upload directly to S3, skipping your server entirely.</p>
<pre><code>// Option A — streaming through Node to S3 (when you need in-flight processing)
import Busboy from "busboy";
import { S3Client } from "@aws-sdk/client-s3";
import { Upload } from "@aws-sdk/lib-storage";
import { fileTypeStream } from "file-type";

const s3 = new S3Client({ region: process.env.AWS_REGION });

app.post("/uploads", requireAuth, (req, res) =&gt; {
  const bb = Busboy({ headers: req.headers, limits: { fileSize: 5 * 1024 * 1024 * 1024, files: 1 } });
  let aborted = false;

  bb.on("file", async (_field, stream, info) =&gt; {
    try {
      const checked = await fileTypeStream(stream);
      if (!["video/mp4", "video/webm"].includes(checked.fileType?.mime)) {
        aborted = true; stream.resume();
        return res.status(415).json({ error: "unsupported type" });
      }
      const key = `uploads/${req.user.id}/${Date.now()}-${info.filename}`;
      const upload = new Upload({
        client: s3,
        params: { Bucket: process.env.BUCKET, Key: key, Body: checked, ContentType: checked.fileType.mime },
        queueSize: 4, partSize: 5 * 1024 * 1024,    // 5 MB parts, 4 in parallel
      });
      stream.on("limit", () =&gt; { aborted = true; upload.abort(); });
      const result = await upload.done();
      if (!aborted) res.status(201).json({ key, location: result.Location });
    } catch (e) { if (!aborted) res.status(500).json({ error: "upload failed" }); }
  });
  req.pipe(bb);
});</code></pre>
<pre><code>// Option B (preferred for big files) — pre-signed multipart upload; client uploads directly to S3
import { CreateMultipartUploadCommand, UploadPartCommand, CompleteMultipartUploadCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

app.post("/uploads/init", requireAuth, async (req, res) =&gt; {
  const key = `uploads/${req.user.id}/${crypto.randomUUID()}`;
  const out = await s3.send(new CreateMultipartUploadCommand({ Bucket: BUCKET, Key: key, ContentType: req.body.mime }));
  res.json({ uploadId: out.UploadId, key });
});
app.post("/uploads/:id/part-url", async (req, res) =&gt; {
  const url = await getSignedUrl(s3, new UploadPartCommand({
    Bucket: BUCKET, Key: req.body.key, UploadId: req.params.id, PartNumber: req.body.partNumber,
  }), { expiresIn: 300 });
  res.json({ url });
});
app.post("/uploads/:id/complete", async (req, res) =&gt; {
  await s3.send(new CompleteMultipartUploadCommand({
    Bucket: BUCKET, Key: req.body.key, UploadId: req.params.id, MultipartUpload: { Parts: req.body.parts },
  }));
  res.json({ ok: true });
});</code></pre>
<p><strong>Trade-offs:</strong> streaming through Node (A) lets you auth, scan for malware (ClamAV stream), watermark, or encrypt — at the cost of bandwidth and concurrency on your server. Pre-signed multipart (B) scales infinitely and never touches your Node bytes — the pattern for any production video/file upload. Always set <code>fileSize</code> limits and validate by magic bytes (never trust <code>Content-Type</code>). For resumable uploads on flaky networks, <strong>tus protocol</strong> (tus.io) with <code>@tus/server</code> gives pause/resume/retry out of the box.</p>
'''

ANSWERS[48] = r'''
<p><strong>Situation:</strong> Node shouldn't terminate TLS, serve static files, or face the public internet directly. Nginx in front handles TLS, caching, compression, slow-client tolerance, and routing.</p>
<p><strong>Approach:</strong> Nginx terminates HTTPS on 443, serves static files directly, and proxies dynamic requests to Node on a loopback port. Node trusts the proxy's forwarded headers so <code>req.ip</code> and <code>req.protocol</code> are correct.</p>
<pre><code>upstream node_backend {
  least_conn;
  server 127.0.0.1:3000 max_fails=3 fail_timeout=10s;
  server 127.0.0.1:3001 max_fails=3 fail_timeout=10s;
  keepalive 64;
}

server { listen 80; server_name api.example.com;
  location /.well-known/acme-challenge/ { root /var/www/certbot; }
  location / { return 301 https://$host$request_uri; }
}

server {
  listen 443 ssl http2;
  server_name api.example.com;

  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
  ssl_protocols TLSv1.2 TLSv1.3;

  add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
  add_header X-Content-Type-Options "nosniff" always;

  location /static/ {
    root /var/www/app;
    expires 1y;
    add_header Cache-Control "public, immutable";
    gzip_static on;
    brotli_static on;
  }

  limit_req_zone $binary_remote_addr zone=api:10m rate=50r/s;

  location / {
    limit_req zone=api burst=100 nodelay;
    proxy_pass http://node_backend;
    proxy_http_version 1.1;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection        "";   # enable keep-alive to upstream

    # WebSocket upgrade
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_connect_timeout 5s;
    proxy_send_timeout    60s;
    proxy_read_timeout    60s;
  }
}</code></pre>
<pre><code>// In Node — trust the single upstream proxy
import express from "express";
const app = express();
app.set("trust proxy", 1);
// Now req.ip reflects X-Forwarded-For client; req.protocol = "https"</code></pre>
<p><strong>Trade-offs:</strong> without <code>trust proxy</code>, <code>req.ip</code> is 127.0.0.1 — breaking rate limits, audit logs, and geo-detection. TLS in Nginx (battle-tested C) outperforms TLS in Node for high throughput. Alternatives: <strong>Caddy</strong> (automatic Let's Encrypt), <strong>Traefik</strong> (container-native, auto-discovery), <strong>Envoy</strong> (L7 features, service mesh), managed <strong>AWS ALB</strong>/<strong>Cloudflare</strong>. On Kubernetes, same principle via an Ingress controller (ingress-nginx, Traefik, Gateway API). Certbot + cron-renew handles Let's Encrypt — or switch to Caddy for automatic ACME without thinking about it.</p>
'''

ANSWERS[49] = r'''
<p><strong>Situation:</strong> public or semi-public API needs protection from scrapers, abusive clients, and accidental loops — without penalizing legitimate bursts. Different endpoints need different limits (5/min on login, 1000/min on read).</p>
<p><strong>Approach:</strong> Redis-backed sliding window or token bucket, keyed by user+IP+route. Tier limits by endpoint sensitivity. Return proper 429 + <code>Retry-After</code>. Put a coarse layer at the reverse proxy to shed obvious attacks cheaply.</p>
<pre><code>// Atomic token bucket in Lua — consistent across all replicas
const tokenBucketLua = `
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local tokens_req = tonumber(ARGV[4])

local b = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(b[1]) or capacity
local ts = tonumber(b[2]) or now
local elapsed = math.max(0, (now - ts) / 1000)
tokens = math.min(capacity, tokens + elapsed * refill)

if tokens &lt; tokens_req then
  redis.call("HMSET", key, "tokens", tokens, "ts", now)
  redis.call("PEXPIRE", key, 3600000)
  return {0, tokens, math.ceil((tokens_req - tokens) * 1000 / refill)}
else
  tokens = tokens - tokens_req
  redis.call("HMSET", key, "tokens", tokens, "ts", now)
  redis.call("PEXPIRE", key, 3600000)
  return {1, tokens, 0}
end
`;
const sha = await redis.script("LOAD", tokenBucketLua);

function rateLimit({ capacity, refill, keyFn }) {
  return async (req, res, next) =&gt; {
    const key = `rl:${keyFn(req)}`;
    const [ok, remaining, retryMs] = await redis.evalsha(sha, 1, key, capacity, refill, Date.now(), 1);
    res.setHeader("RateLimit-Limit", capacity);
    res.setHeader("RateLimit-Remaining", Math.floor(remaining));
    if (!ok) {
      res.setHeader("Retry-After", Math.ceil(retryMs / 1000));
      return res.status(429).json({ error: "RATE_LIMITED" });
    }
    next();
  };
}

// Tiered limits — route-specific
app.post("/auth/login",
  rateLimit({ capacity: 5, refill: 5 / 900, keyFn: (r) =&gt; `login:${r.ip}:${r.body.email}` }),
  login,
);
app.use("/api",
  rateLimit({ capacity: 60, refill: 1, keyFn: (r) =&gt; `api:${r.user?.id ?? r.ip}` }),
);</code></pre>
<p><strong>Trade-offs:</strong> in-memory limiters (default <code>express-rate-limit</code>) only work for single-instance apps — Redis is required beyond one replica. <strong>Sliding window log</strong> is most accurate but most memory; <strong>token bucket</strong> allows natural bursting. <strong>Fixed window</strong> (simple counter) can allow 2× burst at window edges — avoid for strict limits. Tier limits per endpoint and per plan. Use <code>RateLimit-*</code> headers (IETF) for client-friendly responses. For credential-stuffing specifically, combine rate limit with account lockout + CAPTCHA after N failures. At internet scale, push it to Cloudflare/AWS WAF/Envoy — cheaper than burning Node cycles on attacker traffic.</p>
'''

ANSWERS[50] = r'''
<p><strong>Situation:</strong> replace scattered <code>console.log</code> with structured, levelled, redacted logs shipped to an aggregator — with correlation across requests.</p>
<p><strong>Approach:</strong> pick <strong>pino</strong> (fast — ~5× faster than Winston, JSON by default) as the baseline. Add <code>pino-http</code> for request logs and AsyncLocalStorage for propagating request IDs through the call graph.</p>
<pre><code>import pino from "pino";
import pinoHttp from "pino-http";
import { AsyncLocalStorage } from "node:async_hooks";

export const log = pino({
  level: process.env.LOG_LEVEL ?? "info",
  formatters: {
    level: (label) =&gt; ({ level: label }),
    bindings: (b) =&gt; ({ host: b.hostname, service: "api", env: process.env.NODE_ENV }),
  },
  redact: {
    paths: ["req.headers.authorization", "req.headers.cookie", "*.password", "*.token", "*.apiKey", "*.secret"],
    censor: "[REDACTED]",
  },
  serializers: pino.stdSerializers,
  timestamp: pino.stdTimeFunctions.isoTime,
});

const ctx = new AsyncLocalStorage();

export function attachContext(req, res, next) {
  const reqId = req.headers["x-request-id"] ?? crypto.randomUUID();
  res.setHeader("x-request-id", reqId);
  ctx.run({ reqId, userId: req.user?.id }, next);
}

export const httpLogger = pinoHttp({
  logger: log,
  customProps: () =&gt; ctx.getStore() ?? {},
  customLogLevel: (_req, res, err) =&gt;
    err || res.statusCode &gt;= 500 ? "error" :
    res.statusCode &gt;= 400 ? "warn" : "info",
});

// Anywhere deep in business logic — get a child logger with request context
export const logger = () =&gt; log.child(ctx.getStore() ?? {});

// Usage
app.use(attachContext);
app.use(httpLogger);

async function chargeCustomer(id, amount) {
  logger().info({ customerId: id, amount }, "charge start");
  try {
    const result = await stripe.charges.create({ amount });
    logger().info({ chargeId: result.id }, "charge ok");
    return result;
  } catch (err) { logger().error({ err, customerId: id }, "charge failed"); throw err; }
}</code></pre>
<p><strong>Winston equivalent:</strong> more configurable (multiple transports, custom formats) but slower, and stringly-typed transport APIs. For new projects, pino is the pragmatic choice. If already on Winston, migrate per-service; both ship JSON to the same aggregator.</p>
<ul>
  <li><strong>Structured JSON</strong> — queryable in Loki/ELK/Datadog; <code>console.log("user " + id)</code> is unparseable.</li>
  <li><strong>Levels</strong>: <code>trace</code> local, <code>debug</code> feature debugging, <code>info</code> business events, <code>warn</code> recoverable, <code>error</code> action needed, <code>fatal</code> process dying.</li>
  <li><strong>Correlation IDs</strong> on every log line — one request's journey reconstructable.</li>
  <li><strong>Redact sensitive fields</strong> at the logger, not in each caller.</li>
  <li><strong>stdout only</strong> — let the platform (Docker, systemd, K8s) ship logs. Don't write to files from Node in prod.</li>
  <li><strong>Sample</strong> high-volume info/debug logs in prod to control cost.</li>
</ul>
<p><strong>Trade-offs:</strong> observability costs scale with traffic; plan retention (hot 7 days, cold 90 days) and sampling early. A 10-replica app logging verbosely can generate terabytes/day.</p>
'''

ANSWERS[51] = r'''
<p><strong>Situation:</strong> your API aggregates data from third-party APIs that are slow, rate-limited, or flaky — and you're billed per call. Caching reduces latency and cost, and adds a safety net when upstream is down.</p>
<p><strong>Approach:</strong> cache-aside with Redis, singleflight to prevent stampedes on cold keys, stale-while-revalidate so users never wait for upstream if a cached answer exists, with short TTL tuned to freshness needs.</p>
<pre><code>import Redis from "ioredis";
import { request } from "undici";
const redis = new Redis(process.env.REDIS_URL);

const inflight = new Map();

async function fetchExternal(url, { fresh = 60, stale = 600, timeout = 3000 } = {}) {
  const key = `ext:${url}`;
  const cached = await redis.get(key);
  if (cached) {
    const { value, exp } = JSON.parse(cached);
    if (Date.now() &lt; exp.fresh) return value;
    if (Date.now() &lt; exp.stale &amp;&amp; !inflight.has(key)) {
      inflight.set(key, refresh(url, key, fresh, stale, timeout).finally(() =&gt; inflight.delete(key)));
    }
    return value;
  }
  if (inflight.has(key)) return inflight.get(key);
  const p = refresh(url, key, fresh, stale, timeout).finally(() =&gt; inflight.delete(key));
  inflight.set(key, p);
  return p;
}

async function refresh(url, key, fresh, staleMs, timeout) {
  try {
    const res = await request(url, { headersTimeout: timeout, bodyTimeout: timeout });
    if (res.statusCode &gt;= 500) throw new Error(`upstream ${res.statusCode}`);
    const value = await res.body.json();
    await redis.set(key, JSON.stringify({
      value,
      exp: { fresh: Date.now() + fresh * 1000, stale: Date.now() + staleMs * 1000 },
    }), "EX", staleMs + 60);
    return value;
  } catch (err) {
    const existing = await redis.get(key);
    if (existing) return JSON.parse(existing).value;      // stale fallback
    throw err;
  }
}

app.get("/weather/:city", async (req, res) =&gt; {
  const data = await fetchExternal(`https://weather.api/v1/${req.params.city}`, { fresh: 300, stale: 3600 });
  res.json(data);
});</code></pre>
<p><strong>Trade-offs:</strong> stale-while-revalidate trades a bit of staleness for dramatic p99 wins (users never see upstream latency). For strongly-consistent data (inventory, prices), use shorter TTLs and explicit invalidation on upstream webhooks. Respect upstream <code>Cache-Control</code> headers when present. Add a <strong>circuit breaker</strong> (cockatiel) so repeated upstream failures fail fast instead of queuing timeouts. Measure cache hit rate per key prefix — &lt; 60% means TTLs are too short or the cache key shape is wrong.</p>
'''

ANSWERS[52] = r'''
<p><strong>Situation:</strong> stateless authentication across services and mobile clients — a signed token clients include on every request, verifiable without hitting the auth DB.</p>
<p><strong>Approach:</strong> short-lived access JWT (15 min) + long-lived refresh token (stored hashed in DB, rotated on use). Sign with RS256/ES256 (asymmetric) so downstream services verify without the private key. Never put secrets or large payloads in the token.</p>
<pre><code>import jwt from "jsonwebtoken";
import { readFileSync } from "node:fs";
import { randomUUID, createHash } from "node:crypto";

const privateKey = readFileSync(process.env.JWT_PRIVATE_KEY_PATH);
const publicKey = readFileSync(process.env.JWT_PUBLIC_KEY_PATH);

function issueAccess(user) {
  return jwt.sign(
    { sub: user.id, roles: user.roles, tenantId: user.tenantId },
    privateKey,
    { algorithm: "RS256", expiresIn: "15m", issuer: "api", audience: "app" },
  );
}

async function issueRefresh(user) {
  const token = randomUUID() + "." + randomUUID();
  const hash = createHash("sha256").update(token).digest("hex");
  await db.refreshToken.create({
    data: { hash, userId: user.id, expiresAt: new Date(Date.now() + 30 * 24 * 3600_000) },
  });
  return token;
}

export function requireAuth(req, res, next) {
  try {
    const token = req.headers.authorization?.slice(7);
    req.user = jwt.verify(token, publicKey, { algorithms: ["RS256"], issuer: "api", audience: "app" });
    next();
  } catch (e) {
    if (e.name === "TokenExpiredError") return res.status(401).json({ error: "TOKEN_EXPIRED" });
    res.status(401).json({ error: "UNAUTHORIZED" });
  }
}

// Refresh — rotate with reuse detection
app.post("/auth/refresh", async (req, res) =&gt; {
  const { refreshToken } = req.body;
  const hash = createHash("sha256").update(refreshToken).digest("hex");
  const record = await db.refreshToken.findUnique({ where: { hash } });
  if (!record || record.revokedAt || record.expiresAt &lt; new Date())
    return res.status(401).json({ error: "INVALID_REFRESH" });
  if (record.usedAt) {
    // Reuse detected — revoke entire family (possible theft)
    await db.refreshToken.updateMany({ where: { userId: record.userId }, data: { revokedAt: new Date() } });
    return res.status(401).json({ error: "REFRESH_REUSE_DETECTED" });
  }
  await db.refreshToken.update({ where: { hash }, data: { usedAt: new Date() } });
  const user = await db.user.findUnique({ where: { id: record.userId } });
  res.json({ accessToken: issueAccess(user), refreshToken: await issueRefresh(user) });
});</code></pre>
<p><strong>Trade-offs:</strong> stateless JWT beats sessions for distributed systems (no shared DB lookup per request). But revocation is harder — short expiry (15 min) + refresh rotation is the standard workaround. Never store tokens in <code>localStorage</code> (XSS-exfiltrable); use <code>httpOnly</code> cookies for browsers or secure storage on mobile. Asymmetric algorithms (RS256/ES256) let downstream services verify without sharing secrets. <strong>Alternatives</strong>: <strong>PASETO</strong> avoids JWT's algorithm-confusion pitfalls; <strong>opaque tokens</strong> backed by Redis lookups are simpler to revoke when compliance demands it. Always pass explicit <code>algorithms</code> to <code>verify</code> — don't trust the header's <code>alg</code>.</p>
'''

ANSWERS[53] = r'''
<p><strong>Situation:</strong> mobile apps, browsers (Web Push), and sometimes email/SMS — you need to push notifications to users regardless of whether the app is open. Reaching APNs/FCM directly is fragile; route through a provider.</p>
<p><strong>Approach:</strong> abstract a channel interface; for mobile push use FCM (Android + iOS via APNs relay) or a managed service (OneSignal, Pusher Beams, Airship); for browsers use Web Push (VAPID + Service Worker). Enqueue sends as background jobs with retry.</p>
<pre><code>// Mobile push via Firebase Admin SDK
import { initializeApp, applicationDefault } from "firebase-admin/app";
import { getMessaging } from "firebase-admin/messaging";
initializeApp({ credential: applicationDefault() });
const messaging = getMessaging();

async function sendMobilePush({ deviceTokens, title, body, data }) {
  const response = await messaging.sendEachForMulticast({
    tokens: deviceTokens,
    notification: { title, body },
    data,
    android: { priority: "high", notification: { sound: "default" } },
    apns: { payload: { aps: { sound: "default", badge: 1 } } },
  });
  // Prune invalid tokens
  const invalid = response.responses
    .map((r, i) =&gt; (!r.success &amp;&amp; ["messaging/registration-token-not-registered"].includes(r.error.code)) ? deviceTokens[i] : null)
    .filter(Boolean);
  if (invalid.length) await db.deviceToken.deleteMany({ where: { token: { in: invalid } } });
  return response;
}

// Web Push via web-push library (VAPID)
import webpush from "web-push";
webpush.setVapidDetails("mailto:admin@example.com", process.env.VAPID_PUBLIC, process.env.VAPID_PRIVATE);

async function sendWebPush({ subscription, payload }) {
  try { await webpush.sendNotification(subscription, JSON.stringify(payload)); }
  catch (e) {
    if (e.statusCode === 410) {
      await db.pushSubscription.delete({ where: { endpoint: subscription.endpoint } });
    } else throw e;
  }
}

// Dispatcher — fan out via BullMQ respecting user preferences
import { Queue, Worker } from "bullmq";
const q = new Queue("push", { connection });

export async function notify(userId, event, data) {
  await q.add(event, { userId, event, data }, {
    attempts: 3, backoff: { type: "exponential", delay: 2000 },
    jobId: `${event}:${userId}:${data.id}`,
  });
}

new Worker("push", async ({ data }) =&gt; {
  const { userId, event, data: payload } = data;
  const prefs = await db.notificationPref.findUnique({ where: { userId } });
  if (!prefs.enabledFor(event)) return;
  const [mobileTokens, webSubs] = await Promise.all([
    db.deviceToken.findMany({ where: { userId } }).then(r =&gt; r.map(x =&gt; x.token)),
    db.pushSubscription.findMany({ where: { userId } }),
  ]);
  if (mobileTokens.length) await sendMobilePush({ deviceTokens: mobileTokens, ...payload });
  await Promise.allSettled(webSubs.map(sub =&gt; sendWebPush({ subscription: sub, payload })));
}, { connection, concurrency: 50 });</code></pre>
<p><strong>Trade-offs:</strong> self-hosted FCM/APNs integration gives full control; managed push (OneSignal, Airship, Pusher Beams) handles segmentation, scheduling, and delivery analytics for a per-user fee. Always respect user preferences + quiet hours; set TTL on notifications so a 3-hour-stale "new message" doesn't buzz. Prune invalid tokens eagerly (saving money on per-call cost). Deduplicate with idempotency keys — a flaky worker re-firing shouldn't trigger duplicate alerts. Include just enough data in payload to show preview; let the app fetch details on tap to avoid leaking private data to push providers.</p>
'''

ANSWERS[54] = r'''
<p><strong>Situation:</strong> database passwords, third-party API keys, JWT signing keys — can't live in the repo, can't be <code>console.log</code>ged, must rotate without downtime, and different environments need different values.</p>
<p><strong>Approach:</strong> store secrets in a dedicated manager (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, Doppler) and fetch at boot. Inject via IAM role / service account — no long-lived credentials baked into containers. Rotate on a schedule with a grace window for old values.</p>
<pre><code>// secrets.ts — loads once at boot, validates, exits on failure
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";
import { z } from "zod";

const client = new SecretsManagerClient({ region: process.env.AWS_REGION });

const SecretsSchema = z.object({
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_PRIVATE_KEY: z.string().min(100),
  JWT_PUBLIC_KEY: z.string().min(100),
  STRIPE_KEY: z.string().startsWith("sk_"),
  SENDGRID_API_KEY: z.string().min(10),
});

export async function loadSecrets() {
  const id = `${process.env.APP}/${process.env.ENV}`;
  const resp = await client.send(new GetSecretValueCommand({ SecretId: id }));
  const raw = JSON.parse(resp.SecretString);
  return SecretsSchema.parse(raw);
}

const secrets = await loadSecrets();</code></pre>
<p><strong>Rotation pattern (dual-value):</strong></p>
<pre><code>// SecretsManager value: { "current": "v2-secret", "previous": "v1-secret" }
export function verifyJwt(token) {
  try { return jwt.verify(token, secrets.JWT_PUBLIC_KEY_CURRENT); }
  catch (e) {
    if (secrets.JWT_PUBLIC_KEY_PREVIOUS)
      return jwt.verify(token, secrets.JWT_PUBLIC_KEY_PREVIOUS);
    throw e;
  }
}</code></pre>
<ul>
  <li><strong>Inject via IAM</strong> (AWS ECS task role, K8s IRSA) — no credentials in env.</li>
  <li><strong>Never log</strong> <code>process.env</code> or secret objects; pino <code>redact</code> catches common cases.</li>
  <li><strong>Rotate periodically</strong> (90 days for API keys, yearly for signing keys); immediately on suspected compromise.</li>
  <li><strong>Short-lived credentials</strong> where possible (AWS IAM roles with STS, Vault dynamic secrets) — even leaked credentials expire quickly.</li>
  <li><strong>Least privilege</strong>: each service fetches only its own secrets.</li>
  <li><strong>Audit</strong>: CloudTrail / Vault audit log on every secret access.</li>
</ul>
<p><strong>Trade-offs:</strong> env vars are simple but static — you rotate by redeploying. Secret managers add boot-time dependency and cost per secret per month but enable rotation without downtime. SOPS + KMS (encrypted files in the repo) is a reasonable middle ground. <strong>.env files</strong> have their place for dev only; never commit them (<code>.env.example</code> goes in git; the <code>.env</code> is gitignored).</p>
'''

ANSWERS[55] = r'''
<p><strong>Situation:</strong> every route should produce a consistent error response; uncaught exceptions in handlers shouldn't crash the process or leak stack traces; validation failures, auth errors, and internal bugs each need appropriate status codes.</p>
<p><strong>Approach:</strong> one central error middleware at the end of the pipeline; typed <code>AppError</code> hierarchy; Express 5's native async support (or <code>express-async-errors</code> for Express 4); map known framework errors (Zod, Prisma) to HTTP status; log 5xx with full context, never leak the stack to clients.</p>
<pre><code>// errors.ts
export class AppError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: unknown,
  ) { super(message); this.name = this.constructor.name; }
}
export class BadRequest extends AppError { constructor(m, d?) { super(400, "BAD_REQUEST", m, d); } }
export class Unauthorized extends AppError { constructor() { super(401, "UNAUTHORIZED", "auth required"); } }
export class Forbidden extends AppError { constructor() { super(403, "FORBIDDEN", "not allowed"); } }
export class NotFound extends AppError { constructor(r, id?) { super(404, "NOT_FOUND", `${r}${id ? ` ${id}` : ""} not found`); } }
export class Conflict extends AppError { constructor(m) { super(409, "CONFLICT", m); } }
export class RateLimited extends AppError { constructor() { super(429, "RATE_LIMITED", "slow down"); } }

// middleware/errorHandler.ts — central, final handler
import { ZodError } from "zod";
import { Prisma } from "@prisma/client";

export function errorHandler(err, req, res, _next) {
  if (err instanceof ZodError)
    err = new BadRequest("validation failed", err.issues);
  else if (err instanceof Prisma.PrismaClientKnownRequestError) {
    if (err.code === "P2002") err = new Conflict("resource already exists");
    else if (err.code === "P2025") err = new NotFound("resource");
  } else if (err?.type === "entity.too.large")
    err = new AppError(413, "PAYLOAD_TOO_LARGE", "request body too large");

  const appErr = err instanceof AppError ? err : new AppError(500, "INTERNAL", "internal error");

  const logFn = appErr.status &gt;= 500 ? log.error : log.warn;
  logFn.call(log, {
    err, reqId: req.id, method: req.method, url: req.url, userId: req.user?.id,
  }, appErr.message);

  res.status(appErr.status).json({
    error: {
      code: appErr.code,
      message: appErr.message,
      details: appErr.details,
      requestId: req.id,
    },
    ...(process.env.NODE_ENV !== "production" &amp;&amp; { stack: err.stack }),
  });
}

// app.ts
import "express-async-errors";
app.use(routes);
app.use((_req, res) =&gt; res.status(404).json({ error: { code: "NOT_FOUND" } }));
app.use(errorHandler);

// Routes just throw
app.get("/users/:id", async (req, res) =&gt; {
  const u = await db.user.findUnique({ where: { id: req.params.id } });
  if (!u) throw new NotFound("User", req.params.id);
  res.json(u);
});</code></pre>
<p><strong>Trade-offs:</strong> async errors in Express 4 require the <code>express-async-errors</code> shim or explicit <code>.catch(next)</code> — Express 5 handles rejected promises natively. Never return 500 for validation issues — clients can't distinguish "my bug" from "their mistake." Include a <code>requestId</code> in every response so support tickets trace directly to logs. For public APIs, RFC 7807 problem details (<code>application/problem+json</code>) is the standard envelope. Don't echo user input unescaped in error messages. Pair with process-level handlers (<code>uncaughtException</code>, <code>unhandledRejection</code>) that log and exit — let the orchestrator restart.</p>
'''

ANSWERS[56] = r'''
<p><strong>Situation:</strong> read/write files — config, reports, uploads. Avoid the synchronous and callback APIs in favor of the promise API; stream whenever the file might be large.</p>
<p><strong>Approach:</strong> <code>fs/promises</code> for one-shot reads/writes of small files; streams (<code>createReadStream</code>/<code>createWriteStream</code>) + <code>pipeline</code> for anything over a few MB; never use sync variants in request handlers.</p>
<pre><code>import { readFile, writeFile, mkdir, access, constants, rm, rename } from "node:fs/promises";
import { createReadStream, createWriteStream } from "node:fs";
import { pipeline } from "node:stream/promises";
import { createGzip } from "node:zlib";
import path from "node:path";

// Small file — buffer approach is fine
const config = JSON.parse(await readFile("config.json", "utf8"));

// Write JSON atomically — never leave a half-written file
async function atomicWriteJson(filepath, value) {
  const tmp = `${filepath}.${Date.now()}.tmp`;
  await writeFile(tmp, JSON.stringify(value, null, 2), { flag: "wx" });
  await rename(tmp, filepath);     // atomic on same filesystem
}

// Check existence without racing
async function exists(p) {
  try { await access(p, constants.F_OK); return true; } catch { return false; }
}

// Large file — streaming with backpressure (constant memory)
await pipeline(
  createReadStream("input.csv"),
  createGzip({ level: 6 }),
  createWriteStream("input.csv.gz"),
);

// Ensure directory exists (recursive; idempotent)
await mkdir(path.dirname("uploads/2026/04/file.png"), { recursive: true });

// Delete safely
await rm("temp", { recursive: true, force: true });

// ❌ Never in request handlers
import { readFileSync } from "node:fs";
const bad = readFileSync("huge.json");   // blocks the event loop</code></pre>
<p><strong>Path safety — user-supplied names are dangerous:</strong></p>
<pre><code>import path from "node:path";
const UPLOAD_ROOT = path.resolve("./uploads");

function safeUploadPath(userPath) {
  const resolved = path.resolve(UPLOAD_ROOT, userPath);
  if (!resolved.startsWith(UPLOAD_ROOT + path.sep)) throw new Error("path traversal");
  return resolved;
}</code></pre>
<p><strong>Trade-offs:</strong> <code>fs/promises</code> is the modern API; the callback-based <code>fs</code> APIs still work but clutter async code. <code>readFileSync</code> is fine at boot/config-load time but catastrophic in request handlers. Use <code>fs.watch</code> cautiously — platform behavior differs; <code>chokidar</code> smooths it out. <strong>For production storage, avoid the local filesystem entirely</strong> — use S3/GCS/Azure Blob. Containers are ephemeral; local files vanish on redeploy and don't survive horizontal scale.</p>
'''

ANSWERS[57] = r'''
<p><strong>Situation:</strong> user input appears in HTML (stored XSS), filenames (path traversal), DB queries (injection), shell commands (RCE), and regex (ReDoS). Sanitization prevents each category — but only if applied at the right layer.</p>
<p><strong>Approach:</strong> validate shape first (Zod/Joi), sanitize content where the trust changes (HTML → DOMPurify/sanitize-html before render/store), parameterize queries, whitelist filenames, avoid shell interpolation, cap regex. Different threats need different defenses.</p>
<pre><code>// 1. HTML — sanitize rich text before storage OR escape on render
import sanitizeHtml from "sanitize-html";
const clean = sanitizeHtml(req.body.bio, {
  allowedTags: ["p", "br", "strong", "em", "ul", "ol", "li", "a"],
  allowedAttributes: { a: ["href"] },
  allowedSchemes: ["http", "https", "mailto"],
  disallowedTagsMode: "discard",
  transformTags: { a: sanitizeHtml.simpleTransform("a", { rel: "noopener", target: "_blank" }) },
});

// 2. SQL injection — ALWAYS parameterize, never concat
// ❌ `WHERE id = ${req.params.id}`
// ✅ Prisma / Knex / pg with $1 placeholders
const user = await db.user.findUnique({ where: { id: req.params.id } });
const rows = await pool.query("SELECT * FROM users WHERE email = $1", [email]);

// 3. NoSQL — strip $ and . from user JSON (Mongo operator injection)
import mongoSanitize from "express-mongo-sanitize";
app.use(mongoSanitize());

// 4. Path traversal — resolve and bound
import path from "node:path";
const ROOT = path.resolve("./uploads");
function safePath(userProvided) {
  const r = path.resolve(ROOT, userProvided);
  if (!r.startsWith(ROOT + path.sep)) throw new Error("invalid path");
  return r;
}

// 5. Command injection — NEVER shell: true with user input
import { execFile } from "node:child_process";
// ❌ exec(`ffmpeg -i ${userFile} ...`)  // user supplies "; rm -rf /"
// ✅ execFile with an args array (no shell interpretation)
execFile("ffmpeg", ["-i", safePath(userFile), "-codec", "copy", outPath]);

// 6. ReDoS — avoid catastrophic backtracking
// ❌ /^(a+)+$/    vulnerable
// ✅ safe-regex2, validate input length first, or RE2 via 're2' bindings

// 7. Prototype pollution
// ❌ lodash.merge({}, req.body) where body = { "__proto__": { admin: true } }
// ✅ Zod.object().strict() rejects extra keys; Object.create(null) for maps</code></pre>
<p><strong>Trade-offs:</strong> <em>validate + sanitize + escape on output</em> is belt-and-suspenders — each layer catches what the others miss. Never write custom sanitizers for HTML (sanitize-html and DOMPurify are audited). Client-side sanitization is for UX; server is the sole trust boundary. Common sources of leaks: reflected input in error messages, <code>innerHTML</code> in templates, logging sensitive data, and <strong>deserialization</strong> of untrusted data (don't <code>eval</code>, don't use <code>vm</code> with user code). Regular dep audits catch transitive vulnerabilities — many prod breaches are via deps, not app code.</p>
'''

ANSWERS[58] = r'''
<p><strong>Situation:</strong> users need roles (admin, editor, viewer, billing-manager) with permissions that evolve over time — without refactoring every endpoint when a new role arrives.</p>
<p><strong>Approach:</strong> model users → roles → permissions in the DB; attach abilities on the request; check via a policy call at controllers. Cache the derived ability per user with versioning so role changes take effect fast.</p>
<pre><code>// Schema (Prisma)
// users, roles (id, name), permissions (id, action, subject, conditions_json),
// user_roles, role_permissions

import { AbilityBuilder, PureAbility } from "@casl/ability";
import Redis from "ioredis";
const redis = new Redis(process.env.REDIS_URL);

async function loadAbility(userId) {
  const cached = await redis.get(`ability:${userId}`);
  if (cached) return PureAbility.fromJSON(JSON.parse(cached));

  const perms = await db.$queryRaw`
    SELECT p.action, p.subject, p.conditions
    FROM users u
    JOIN user_roles ur ON ur.user_id = u.id
    JOIN role_permissions rp ON rp.role_id = ur.role_id
    JOIN permissions p ON p.id = rp.permission_id
    WHERE u.id = ${userId}
  `;
  const { can, build } = new AbilityBuilder(PureAbility);
  for (const p of perms) can(p.action, p.subject, p.conditions ?? undefined);
  const ability = build();

  await redis.set(`ability:${userId}`, JSON.stringify(ability.rules), "EX", 300);
  return ability;
}

async function changeRoles(userId, roleIds) {
  await db.userRole.deleteMany({ where: { userId } });
  await db.userRole.createMany({ data: roleIds.map(r =&gt; ({ userId, roleId: r })) });
  await redis.del(`ability:${userId}`);
}

app.use(async (req, _res, next) =&gt; {
  if (req.user) req.ability = await loadAbility(req.user.id);
  next();
});

export const authorize = (action, subject) =&gt; (req, res, next) =&gt;
  req.ability?.can(action, subject) ? next() : res.status(403).json({ error: "FORBIDDEN" });

app.get("/posts",        authorize("read", "Post"), postsController.list);
app.post("/posts",       authorize("create", "Post"), postsController.create);
app.delete("/posts/:id", authorize("delete", "Post"), async (req, res) =&gt; {
  const post = await db.post.findUnique({ where: { id: req.params.id } });
  if (!post) return res.status(404).end();
  if (!req.ability.can("delete", post)) return res.status(403).end();
  await db.post.delete({ where: { id: post.id } });
  res.status(204).end();
});</code></pre>
<p><strong>Trade-offs:</strong> role strings scattered as <code>if (user.role === "admin")</code> calcify fast. Build the role/permission tables from day one even for 3 roles. Move to <strong>ABAC</strong> (attribute-based) when "admin of this tenant but not that one" or "owns resource X" appear. In multi-tenant apps, tenant scoping wraps RBAC: the first check is always <code>where tenantId = req.user.tenantId</code>; never let roles span tenants. Audit every authorization failure for security monitoring. For service-to-service calls, use scoped API tokens with the same permission model.</p>
'''

ANSWERS[59] = r'''
<p><strong>Situation:</strong> users want data exports as Excel — multiple sheets, formatting, formulas. CSV doesn't suit non-technical users; a real .xlsx is the expected deliverable.</p>
<p><strong>Approach:</strong> for small reports, generate inline with <strong>exceljs</strong> and stream to the response. For large datasets, generate in a background job and deliver via S3-signed URL. For massive datasets, consider CSV + ZIP instead.</p>
<pre><code>import ExcelJS from "exceljs";

// Small — stream directly to HTTP response
app.get("/reports/orders.xlsx", requireAuth, async (req, res) =&gt; {
  res.setHeader("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
  res.setHeader("Content-Disposition", 'attachment; filename="orders-2026-04.xlsx"');

  const wb = new ExcelJS.stream.xlsx.WorkbookWriter({ stream: res });
  const ws = wb.addWorksheet("Orders", { properties: { defaultColWidth: 18 } });
  ws.columns = [
    { header: "Order ID", key: "id", width: 20 },
    { header: "Customer", key: "customer", width: 30 },
    { header: "Date", key: "date", width: 14, style: { numFmt: "yyyy-mm-dd" } },
    { header: "Total", key: "total", width: 12, style: { numFmt: '"$"#,##0.00' } },
    { header: "Status", key: "status", width: 14 },
  ];
  ws.getRow(1).font = { bold: true };
  ws.getRow(1).fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FFEEEEEE" } };
  ws.views = [{ state: "frozen", ySplit: 1 }];

  // Stream rows from DB with cursor — never load all into memory
  for await (const order of db.order.stream({ where: { tenantId: req.user.tenantId } })) {
    ws.addRow({
      id: order.id, customer: order.customer.name, date: order.createdAt,
      total: order.total, status: order.status,
    }).commit();          // flush row to stream (keeps memory constant)
  }

  const summary = wb.addWorksheet("Summary");
  summary.addRow(["Total orders", { formula: "COUNTA(Orders!A:A)-1" }]);
  summary.addRow(["Total revenue", { formula: "SUM(Orders!D:D)", result: 0 }]);

  await wb.commit();
});

// Large — offload to worker; deliver via signed URL
app.post("/reports/orders/export", requireAuth, async (req, res) =&gt; {
  const job = await reportQueue.add("orders-export", {
    userId: req.user.id, tenantId: req.user.tenantId, filters: req.body,
  });
  res.status(202).json({ jobId: job.id, statusUrl: `/reports/jobs/${job.id}` });
});
// Worker streams from DB → exceljs.stream → S3 PutObject; notifies user with signed URL on done</code></pre>
<p><strong>Trade-offs:</strong> <strong>exceljs</strong> supports styling, formulas, images, multiple sheets. <strong>xlsx (SheetJS)</strong> is lighter but less fluent; <strong>write-excel-file</strong> is minimal and fast. Use the <strong>streaming</strong> writer for datasets &gt; ~50k rows — the non-streaming API buffers everything in memory. Excel has a row limit (1,048,576) and gets unwieldy at hundreds of thousands of rows — for truly huge datasets, CSV + ZIP or Parquet is better. For scheduled daily reports, a cron-driven worker writing to S3 + email with link is cleaner than synchronous downloads. Never build .xlsx from templates with string interpolation — formula injection is a real attack surface.</p>
'''

ANSWERS[60] = r'''
<p><strong>Situation:</strong> protect multiple routes behind a consistent authentication check, keep the handlers clean, and support different auth types (JWT for mobile, session for web, API key for service-to-service).</p>
<p><strong>Approach:</strong> middleware per auth scheme that verifies + populates <code>req.user</code> and either calls <code>next()</code> or returns 401. Compose strategies. Layer authorization on top.</p>
<pre><code>import jwt from "jsonwebtoken";
import { createHash } from "node:crypto";

// JWT (Authorization: Bearer ...)
export const jwtAuth = (req, res, next) =&gt; {
  const token = req.headers.authorization?.startsWith("Bearer ")
    ? req.headers.authorization.slice(7) : null;
  if (!token) return res.status(401).json({ error: "MISSING_TOKEN" });
  try {
    req.user = jwt.verify(token, publicKey, { algorithms: ["RS256"], issuer: "api" });
    next();
  } catch (e) {
    if (e.name === "TokenExpiredError") return res.status(401).json({ error: "TOKEN_EXPIRED" });
    res.status(401).json({ error: "INVALID_TOKEN" });
  }
};

// Session cookie
export const sessionAuth = (req, res, next) =&gt; {
  if (!req.session?.userId) return res.status(401).json({ error: "NO_SESSION" });
  req.user = { sub: req.session.userId, roles: req.session.roles };
  next();
};

// API key (for service-to-service)
export const apiKeyAuth = async (req, res, next) =&gt; {
  const raw = req.headers["x-api-key"];
  if (!raw) return res.status(401).json({ error: "MISSING_API_KEY" });
  const hash = createHash("sha256").update(raw).digest("hex");
  const key = await db.apiKey.findUnique({ where: { hash } });
  if (!key || key.revokedAt) return res.status(401).json({ error: "INVALID_API_KEY" });
  req.user = { sub: key.userId, roles: key.scopes };
  db.apiKey.update({ where: { id: key.id }, data: { lastUsedAt: new Date() } }).catch(() =&gt; {});
  next();
};

// Compose — try JWT first, fall back to session (browser page reload scenarios)
export const authAny = (req, res, next) =&gt; {
  if (req.headers.authorization) return jwtAuth(req, res, next);
  if (req.session?.userId) return sessionAuth(req, res, next);
  res.status(401).json({ error: "UNAUTHORIZED" });
};

// Optional auth — populates req.user if present but doesn't reject
export const optionalAuth = (req, _res, next) =&gt; {
  const silentRes = { status: () =&gt; ({ json: () =&gt; {} }) };
  try {
    if (req.headers.authorization) jwtAuth(req, silentRes, () =&gt; {});
    else if (req.session?.userId) sessionAuth(req, silentRes, () =&gt; {});
  } catch {}
  next();
};

// Routes
app.get("/admin/users",     jwtAuth, requireRole("admin"), adminController.users);
app.post("/api/webhooks/x", apiKeyAuth, webhookController.handle);
app.get("/profile",         authAny,   profileController.get);
app.get("/public-feed",     optionalAuth, publicFeedController);</code></pre>
<p><strong>Trade-offs:</strong> Passport.js offers 500+ strategies and is the historical default — flexible but heavyweight. Writing small, focused middleware (as above) is usually clearer for a handful of schemes. For full-featured auth with MFA/SSO/social login, <strong>Auth0/Clerk/WorkOS/Supabase Auth</strong> beats building it yourself. Middleware should do one job — populate <code>req.user</code> — and leave authorization to a separate layer. Never combine auth + business logic in one function; test it separately with minimal fakes.</p>
'''

ANSWERS[61] = r'''
<p><strong>Situation:</strong> users want per-feature preferences (notification channels, language, timezone, theme, privacy) editable from settings — with sensible defaults, versioned schema, and fast reads on every request.</p>
<p><strong>Approach:</strong> model preferences as a JSON column keyed by category with a Zod schema; expose typed endpoints; cache the resolved prefs in Redis; provide defaults at read time so clients always get complete objects even if fields are missing.</p>
<pre><code>// Prisma: table user_preferences(user_id pk, data jsonb, version int, updated_at)
import { z } from "zod";
import Redis from "ioredis";
const redis = new Redis(process.env.REDIS_URL);

const PrefsSchema = z.object({
  notifications: z.object({
    email: z.boolean().default(true),
    push: z.boolean().default(true),
    sms: z.boolean().default(false),
    digest: z.enum(["instant", "daily", "weekly", "never"]).default("daily"),
  }).default({}),
  display: z.object({
    theme: z.enum(["light", "dark", "auto"]).default("auto"),
    locale: z.string().regex(/^[a-z]{2}(-[A-Z]{2})?$/).default("en-US"),
    timezone: z.string().default("UTC"),
    dateFormat: z.enum(["ISO", "US", "EU"]).default("ISO"),
  }).default({}),
  privacy: z.object({
    profileVisibility: z.enum(["public", "contacts", "private"]).default("contacts"),
    searchable: z.boolean().default(true),
    analytics: z.boolean().default(true),
  }).default({}),
}).default({});

const PatchSchema = PrefsSchema.deepPartial();

async function getPrefs(userId) {
  const cached = await redis.get(`prefs:${userId}`);
  if (cached) return JSON.parse(cached);
  const row = await db.userPreferences.findUnique({ where: { userId } });
  const prefs = PrefsSchema.parse(row?.data ?? {});  // fills defaults
  await redis.set(`prefs:${userId}`, JSON.stringify(prefs), "EX", 300);
  return prefs;
}

app.get("/me/preferences", requireAuth, async (req, res) =&gt; {
  res.json(await getPrefs(req.user.sub));
});

app.patch("/me/preferences", requireAuth, async (req, res) =&gt; {
  const patch = PatchSchema.parse(req.body);
  const current = await getPrefs(req.user.sub);
  const merged = PrefsSchema.parse(deepMerge(current, patch));
  await db.userPreferences.upsert({
    where: { userId: req.user.sub },
    update: { data: merged, version: { increment: 1 } },
    create: { userId: req.user.sub, data: merged, version: 1 },
  });
  await redis.del(`prefs:${req.user.sub}`);
  res.json(merged);
});

// Usage deep in services — always defaults-filled
async function shouldSendEmail(userId, kind) {
  const p = await getPrefs(userId);
  return p.notifications.email &amp;&amp; p.notifications.digest !== "never";
}</code></pre>
<p><strong>Trade-offs:</strong> JSONB keeps adding preferences cheap (no ALTER TABLE); versioning handles schema evolution (migrate old values lazily on read). For small, flat prefs, columns are fine — JSONB wins when the shape is nested or grows. Cache reads aggressively (5-min TTL + invalidation on write) because nearly every request needs prefs. Sync across devices via the cache + WebSocket "prefs updated" event. <strong>Default at read</strong>, not at write — old records always get new defaults without a backfill. For heavy personalization (targeting, A/B, segmentation), reach for a dedicated service (LaunchDarkly, Unleash) rather than growing prefs.</p>
'''

ANSWERS[62] = r'''
<p><strong>Situation:</strong> you want a drop-in rate limiter without writing Lua or managing Redis operations — <code>express-rate-limit</code> with a Redis store is the 80%-case answer.</p>
<p><strong>Approach:</strong> <code>express-rate-limit</code> + <code>rate-limit-redis</code> for shared state, key by user id (fallback to IP), tier by route, return proper 429 with <code>RateLimit-*</code> headers.</p>
<pre><code>import rateLimit, { ipKeyGenerator } from "express-rate-limit";
import RedisStore from "rate-limit-redis";
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL);

// Shared base: per-user limits across replicas
const baseStore = () =&gt; new RedisStore({
  sendCommand: (...args) =&gt; redis.call(...args),
  prefix: "rl:",
});

const globalApi = rateLimit({
  store: baseStore(),
  windowMs: 60_000,
  limit: 100,
  standardHeaders: "draft-7",   // IETF RateLimit-* headers
  legacyHeaders: false,
  keyGenerator: (req) =&gt; req.user?.sub ?? ipKeyGenerator(req.ip),
  handler: (_req, res) =&gt; {
    res.setHeader("Retry-After", "60");
    res.status(429).json({ error: "RATE_LIMITED", message: "too many requests" });
  },
  skip: (req) =&gt; req.user?.role === "admin",
});

// Strict: login — only count failures
const loginLimit = rateLimit({
  store: baseStore(),
  windowMs: 15 * 60_000,
  limit: 5,
  keyGenerator: (req) =&gt; `login:${req.ip}:${req.body?.email ?? ""}`,
  skipSuccessfulRequests: true,
});

// Burst tolerance on expensive endpoints
const reportLimit = rateLimit({
  store: baseStore(),
  windowMs: 60_000,
  limit: 10,
  keyGenerator: (req) =&gt; req.user?.sub ?? req.ip,
});

// Trust proxy so req.ip reflects the real client (behind Nginx/LB)
app.set("trust proxy", 1);

app.use(globalApi);
app.post("/auth/login", loginLimit, loginHandler);
app.post("/reports/generate", reportLimit, reportHandler);</code></pre>
<p><strong>Tiered per plan (free vs pro):</strong></p>
<pre><code>function tieredLimit() {
  return rateLimit({
    store: baseStore(),
    windowMs: 60_000,
    limit: (req) =&gt; req.user?.plan === "pro" ? 1000 : 100,
    keyGenerator: (req) =&gt; req.user?.sub ?? req.ip,
  });
}
app.use("/api", requireAuth, tieredLimit());</code></pre>
<p><strong>Trade-offs:</strong> <code>express-rate-limit</code> uses a fixed-window counter by default — simple and memory-cheap but allows 2× burst at window boundaries (user sends 100 at T+59s, 100 more at T+60s). For strict limits, use a sliding-window-log or token-bucket store (available as <code>@nestjs/throttler</code> or custom Lua). Without a shared Redis store, each replica keeps its own counts — useless beyond one instance. Always set <code>trust proxy</code> to the correct hop count; an incorrect value lets clients spoof <code>X-Forwarded-For</code>. Return 429 with <code>Retry-After</code>; never use 503 (implies server fault). For internet-scale DDoS, push to Cloudflare/WAF — rate limits in Node are for business logic, not attack mitigation.</p>
'''

ANSWERS[63] = r'''
<p><strong>Situation:</strong> users upload photos for avatars/product images/profile pictures. You need to validate, resize to multiple sizes for responsive delivery, and store in object storage — ideally without blocking HTTP responses on slow CPU work.</p>
<p><strong>Approach:</strong> accept via multer or pre-signed URL; <strong>sharp</strong> for resize/format (fastest image lib in Node, backed by libvips). Generate thumbnail/medium/large variants; store all in S3; return a CDN-backed base URL the client can build size URLs from.</p>
<pre><code>import multer from "multer";
import sharp from "sharp";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { fileTypeFromBuffer } from "file-type";
import { randomUUID } from "node:crypto";

const s3 = new S3Client({ region: process.env.AWS_REGION });
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },
});

const SIZES = [
  { suffix: "thumb",  width: 150, height: 150, fit: "cover" },
  { suffix: "medium", width: 800 },
  { suffix: "large",  width: 1920 },
];

app.post("/images", requireAuth, upload.single("image"), async (req, res) =&gt; {
  if (!req.file) return res.status(400).json({ error: "image required" });
  // Validate by magic bytes (not client-claimed Content-Type)
  const ft = await fileTypeFromBuffer(req.file.buffer);
  if (!ft || !["image/jpeg", "image/png", "image/webp", "image/heic"].includes(ft.mime)) {
    return res.status(415).json({ error: "unsupported image type" });
  }

  const id = randomUUID();
  const basePath = `images/${req.user.sub}/${id}`;

  // Parallel resizes with sharp — libvips is fast enough to do inline for &lt; 20 MB
  const variants = await Promise.all(SIZES.map(async (s) =&gt; {
    const buffer = await sharp(req.file.buffer, { failOnError: false })
      .rotate()                               // auto-orient from EXIF
      .resize({ width: s.width, height: s.height, fit: s.fit ?? "inside", withoutEnlargement: true })
      .webp({ quality: 82, effort: 4 })      // WebP is the modern default
      .toBuffer();

    const key = `${basePath}/${s.suffix}.webp`;
    await s3.send(new PutObjectCommand({
      Bucket: process.env.BUCKET, Key: key, Body: buffer, ContentType: "image/webp",
      CacheControl: "public, max-age=31536000, immutable",
    }));
    return { [s.suffix]: `${process.env.CDN_URL}/${key}` };
  }));
  res.status(201).json(Object.assign({ id }, ...variants));
});</code></pre>
<p><strong>For high volume — offload to a worker:</strong></p>
<pre><code>// HTTP handler uploads original to S3 quickly; enqueues variants job
await s3.send(new PutObjectCommand({ Bucket, Key: `${basePath}/original`, Body: req.file.buffer }));
await imageQueue.add("resize", { bucket: Bucket, key: `${basePath}/original`, basePath, sizes: SIZES });
res.status(202).json({ id, status: "processing" });
// Worker downloads from S3, resizes, uploads variants — doesn't block HTTP</code></pre>
<p><strong>Trade-offs:</strong> <strong>sharp</strong> is by far the fastest (4-5× faster than Jimp; uses libvips' streaming internals). Always set <code>withoutEnlargement</code> to avoid upscaling small originals. Strip EXIF metadata (<code>.withMetadata(false)</code>) unless you need it — privacy + bytes. WebP or AVIF deliver 25-50% smaller than JPEG at equivalent quality. For variable-size responsive delivery, consider an <strong>image CDN</strong> (Cloudinary, imgix, Cloudflare Images) that does on-the-fly resize + format negotiation — you upload once, the CDN handles variants. For simple apps, that's simpler than a sharp + worker pipeline. Validate by magic bytes, not <code>Content-Type</code> (trivial to spoof); cap file size at multer layer to prevent memory exhaustion.</p>
'''

ANSWERS[64] = r'''
<p><strong>Situation:</strong> process a 10 GB log file, a million-row CSV, or a stream of events from S3 — loading into memory is impossible. You need bounded memory and predictable backpressure.</p>
<p><strong>Approach:</strong> node streams with <code>pipeline</code>; transform streams for per-chunk work; async iterators for composable row-level pipelines; respect backpressure with <code>highWaterMark</code>. Never manually pipe — <code>pipeline</code> handles errors and cleanup.</p>
<pre><code>// Example: aggregate a huge CSV into Postgres — constant memory regardless of size
import { createReadStream } from "node:fs";
import { pipeline } from "node:stream/promises";
import { createGunzip } from "node:zlib";
import { parse } from "csv-parse";
import { Transform } from "node:stream";
import { from as copyFrom } from "pg-copy-streams";

async function importCsv(pool, path) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const dbStream = client.query(copyFrom("COPY events (ts, user_id, type, payload) FROM STDIN CSV"));

    let rows = 0;
    const enrich = new Transform({
      objectMode: true, highWaterMark: 256,
      transform(row, _enc, cb) {
        // Per-row work — validate, enrich, transform
        if (!row.user_id) return cb();  // skip invalid
        rows++;
        const out = [row.ts, row.user_id, row.type, JSON.stringify({ src: row.src })].join(",") + "\n";
        cb(null, out);
      },
    });

    await pipeline(
      createReadStream(path),      // file → gzip'd bytes
      createGunzip(),              // bytes → decompressed text
      parse({ columns: true, skip_empty_lines: true, trim: true }),  // text → row objects
      enrich,                      // rows → CSV lines
      dbStream,                    // CSV → Postgres COPY
    );
    await client.query("COMMIT");
    return rows;
  } catch (e) { await client.query("ROLLBACK"); throw e; }
  finally { client.release(); }
}

// Stream directly from S3 — no disk hop
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
const s3 = new S3Client({});
const res = await s3.send(new GetObjectCommand({ Bucket, Key }));
await pipeline(res.Body, createGunzip(), parse({ columns: true }), processingStream);

// Async iterator pattern — composable, easier to read than Transform
import { Readable } from "node:stream";

async function* batched(source, size = 1000) {
  let batch = [];
  for await (const item of source) {
    batch.push(item);
    if (batch.length &gt;= size) { yield batch; batch = []; }
  }
  if (batch.length) yield batch;
}

for await (const batch of batched(Readable.toWeb(parser).getReader(), 1000)) {
  await db.event.createMany({ data: batch });
}</code></pre>
<p><strong>Backpressure and memory:</strong></p>
<ul>
  <li><code>highWaterMark</code> controls the internal buffer; smaller = stricter memory but more syscalls.</li>
  <li><code>pipeline</code> handles error propagation + cleanup; manual <code>.pipe()</code> leaks on error.</li>
  <li>Object-mode streams have smaller practical hwm (item count, not bytes); scalar streams in bytes.</li>
  <li>Combining Node streams + web streams with <code>Readable.fromWeb/toWeb</code> unlocks <code>fetch</code>/<code>WritableStream</code> interop.</li>
</ul>
<p><strong>Trade-offs:</strong> streams are the correct answer for large data — <code>fs.readFile</code> on a 10 GB file will crash. Transform streams compose but the callback API is awkward; async iterators are cleaner and increasingly the preferred pattern. For distributed stream processing (Kafka, Kinesis), reach for kafkajs with consumer groups. For one-off huge imports, try to let the DB do the work — Postgres <code>COPY</code>, MongoDB <code>mongoimport</code>, or bulk-insert APIs on S3 data avoid moving bytes through Node at all.</p>
'''

ANSWERS[65] = r'''
<p><strong>Situation:</strong> users forget passwords. You need a secure reset flow: time-limited token, single use, doesn't leak whether an account exists, invalidates existing sessions on success.</p>
<p><strong>Approach:</strong> on request, always respond success (even for unknown email) to prevent enumeration; generate a cryptographic random token; store only its hash in DB with short expiry; email the plaintext token as a link; on reset, verify once and invalidate.</p>
<pre><code>import { randomBytes, createHash } from "node:crypto";
import argon2 from "argon2";

app.post("/auth/password/reset-request", async (req, res) =&gt; {
  const email = req.body.email?.toLowerCase().trim();
  const user = email ? await db.user.findUnique({ where: { email } }) : null;

  // Only act if user exists — but respond identically either way
  if (user) {
    // Invalidate any prior reset tokens for this user
    await db.passwordReset.updateMany({
      where: { userId: user.id, usedAt: null, expiresAt: { gt: new Date() } },
      data: { expiresAt: new Date() },
    });

    const token = randomBytes(32).toString("base64url");   // URL-safe, 256-bit
    const tokenHash = createHash("sha256").update(token).digest("hex");
    await db.passwordReset.create({
      data: {
        userId: user.id,
        tokenHash,
        expiresAt: new Date(Date.now() + 30 * 60_000),      // 30 min
        requestIp: req.ip,
      },
    });

    const link = `${process.env.APP_URL}/reset?token=${token}`;
    await emailQueue.add("password-reset", {
      to: user.email, template: "password-reset", data: { link, name: user.name },
    }, { attempts: 5, jobId: `pwreset:${user.id}:${Date.now()}` });
  }

  // Constant-ish response — don't leak existence
  return res.json({ ok: true, message: "If an account exists, a reset email was sent." });
});

app.post("/auth/password/reset", async (req, res) =&gt; {
  const { token, newPassword } = req.body;
  if (!token || !newPassword || newPassword.length &lt; 12)
    return res.status(400).json({ error: "invalid input" });

  const tokenHash = createHash("sha256").update(token).digest("hex");
  const record = await db.passwordReset.findUnique({ where: { tokenHash } });

  if (!record || record.usedAt || record.expiresAt &lt; new Date()) {
    return res.status(400).json({ error: "INVALID_OR_EXPIRED_TOKEN" });
  }

  const passwordHash = await argon2.hash(newPassword, { type: argon2.argon2id, memoryCost: 19456, timeCost: 2 });

  await db.$transaction([
    db.user.update({ where: { id: record.userId }, data: { passwordHash, passwordChangedAt: new Date() } }),
    db.passwordReset.update({ where: { id: record.id }, data: { usedAt: new Date() } }),
    // Revoke all active sessions + refresh tokens — attacker who had password can't ride old tokens
    db.session.deleteMany({ where: { userId: record.userId } }),
    db.refreshToken.updateMany({ where: { userId: record.userId, revokedAt: null }, data: { revokedAt: new Date() } }),
  ]);

  // Notify the user out-of-band (second channel if available)
  await emailQueue.add("password-changed", { to: (await db.user.findUnique({ where: { id: record.userId } })).email });

  res.json({ ok: true });
});</code></pre>
<p><strong>Trade-offs:</strong> <strong>never leak account existence</strong> — a naive "No such user" response enables email enumeration. Rate-limit the reset-request endpoint by IP + email (5/hour) to prevent mailbox flooding. <strong>Never store the token plain</strong> — hash with SHA-256 (fast because the token is already high-entropy random; full password hash like Argon2 is overkill here and slows comparison). Invalidate on first use; short expiry (15-30 min). On success, invalidate all active sessions — if attacker had stolen the password, this boots them. Send confirmation email to the old address so legitimate users notice unauthorized resets. Consider account recovery via a second factor for high-value accounts.</p>
'''

ANSWERS[66] = r'''
<p><strong>Situation:</strong> your app opens a new DB connection per request — dies under moderate load with "too many connections." You need pooling with correct sizing, graceful shutdown, and visibility when pools saturate.</p>
<p><strong>Approach:</strong> one shared pool per service; size it based on DB capacity ÷ replicas; don't leak connections across async boundaries; expose pool metrics; handle drain on shutdown.</p>
<pre><code>import { Pool } from "pg";

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: Number(process.env.DB_POOL_MAX) || 20,
  min: 2,
  idleTimeoutMillis: 30_000,       // recycle idle connections
  connectionTimeoutMillis: 5_000,  // fail fast if pool exhausted
  allowExitOnIdle: false,
  keepAlive: true,
  // Postgres-specific: application_name shows in pg_stat_activity
  application_name: process.env.SERVICE_NAME ?? "api",
});

pool.on("error", (err) =&gt; log.error({ err }, "pool-level error (idle connection died)"));

// Query helper — NEVER checkout without releasing in finally
export async function query(text, params) {
  const start = Date.now();
  const res = await pool.query(text, params);
  const ms = Date.now() - start;
  if (ms &gt; 500) log.warn({ text, ms, rows: res.rowCount }, "slow query");
  metrics.histogram("db.query.ms").observe(ms);
  return res;
}

// Transactions — client MUST be released
export async function tx(fn) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await fn(client);
    await client.query("COMMIT");
    return result;
  } catch (e) {
    await client.query("ROLLBACK");
    throw e;
  } finally {
    client.release();          // always — even on error
  }
}

// Graceful shutdown — drain before exit
process.on("SIGTERM", async () =&gt; {
  log.info("shutting down pool");
  await server.close();
  await pool.end();            // waits for in-flight queries to finish
  process.exit(0);
});

// Metrics
setInterval(() =&gt; {
  metrics.gauge("db.pool.total").set(pool.totalCount);
  metrics.gauge("db.pool.idle").set(pool.idleCount);
  metrics.gauge("db.pool.waiting").set(pool.waitingCount);
}, 5000);</code></pre>
<p><strong>Pool sizing rule of thumb:</strong></p>
<p><code>max = (DB_connection_limit × 0.8) ÷ number_of_replicas</code>. RDS db.m6g.large = 80 max; with 4 replicas → 16 each. <strong>Oversizing</strong> is worse than undersizing — the DB thrashes with more active connections than cores. PgBouncer (transaction-mode pooler) in front of Postgres allows hundreds of app connections to multiplex onto dozens of DB connections; essential for serverless Node.</p>
<ul>
  <li><strong>ORM pools</strong> (Prisma, Mongoose, TypeORM) wrap the same concept — configure <code>connection_limit</code> or equivalent.</li>
  <li><strong>Never open a pool per request</strong> — module-scope singleton.</li>
  <li><strong>Always <code>finally { client.release() }</code></strong> on manual checkouts.</li>
  <li><strong>Idle timeout</strong> (30s) recycles connections so DB-side limits (idle_in_transaction_timeout, server restarts) don't silently break.</li>
  <li><strong>Handle <code>pool.on("error")</code></strong> — a killed idle connection must not crash the process.</li>
  <li><strong>Read replicas</strong>: separate pool for read-only queries; route via code or a proxy (pgbouncer, ProxySQL).</li>
</ul>
<p><strong>Trade-offs:</strong> serverless (Lambda) needs an external pooler (RDS Proxy, PgBouncer) because each invocation is its own process — without one, you hit the DB's connection limit fast. In K8s, pool = small, replicas = many. For MongoDB, the native driver pools by default; tune <code>maxPoolSize</code>. Monitor <code>waitingCount</code> — a non-zero value under normal load means the pool is undersized or queries are too slow.</p>
'''

ANSWERS[67] = r'''
<p><strong>Situation:</strong> RESTful resources naturally nest — <code>/users/:userId/posts/:postId/comments/:commentId</code>. How do you model this without route spaghetti or ambiguity?</p>
<p><strong>Approach:</strong> nest only one level (shallow nesting) when the child can't exist without the parent; use query params for loose relationships; let sub-resources be reachable both nested and flat (<code>/comments/:id</code> for direct access) when they have identity. Use Express routers for modularity.</p>
<pre><code>import { Router } from "express";

// Top-level resources get their own routers
const usersRouter = Router();
const postsRouter = Router({ mergeParams: true });      // inherit :userId
const commentsRouter = Router({ mergeParams: true });   // inherit :postId

// Users
usersRouter.get("/", userController.list);
usersRouter.get("/:userId", userController.get);

// Posts nested under users — for "all posts by this user"
usersRouter.use("/:userId/posts", postsRouter);

postsRouter.get("/", async (req, res) =&gt; {
  const posts = await db.post.findMany({ where: { authorId: req.params.userId } });
  res.json(posts);
});
postsRouter.post("/", requireAuth, async (req, res) =&gt; {
  if (req.user.sub !== req.params.userId) throw new Forbidden();
  const post = await db.post.create({ data: { ...req.body, authorId: req.user.sub } });
  res.status(201).json(post);
});

// Comments nested under posts
postsRouter.use("/:postId/comments", commentsRouter);
commentsRouter.get("/", async (req, res) =&gt; {
  const comments = await db.comment.findMany({
    where: { postId: req.params.postId, post: { authorId: req.params.userId } },
  });
  res.json(comments);
});

// ALSO a flat route for direct access — you have the comment id, don't need the ancestors
app.get("/comments/:id", async (req, res) =&gt; {
  const c = await db.comment.findUnique({ where: { id: req.params.id }, include: { post: true } });
  if (!c) return res.status(404).end();
  res.json(c);
});

// Mount the tree
app.use("/users", usersRouter);</code></pre>
<p><strong>Design rules:</strong></p>
<ul>
  <li><strong>Shallow nest</strong> — one level deep max. <code>/users/:u/posts/:p/comments</code> is fine; <code>/users/:u/posts/:p/comments/:c/reactions</code> is not. Resource-level identity beats hierarchy.</li>
  <li><strong>Expose flat routes</strong> for direct lookup when the resource has its own ID. <code>/comments/:id</code> is faster to write and link.</li>
  <li><strong>Validate the hierarchy</strong> in handlers — a malicious client could GET <code>/users/alice/posts/bobs-post</code>; check that <code>bobs-post</code> actually belongs to alice.</li>
  <li><strong>Query params for loose filters</strong> — <code>GET /posts?authorId=X</code> is just as valid as <code>/users/X/posts</code>; sometimes cleaner.</li>
  <li><strong>Use <code>Router({ mergeParams: true })</code></strong> so child routes see parent params.</li>
  <li><strong>Naming:</strong> plural nouns, lowercase, hyphens. <code>/order-items</code>, not <code>/orderItems</code> or <code>/OrderItem</code>.</li>
</ul>
<p><strong>Trade-offs:</strong> deep nesting feels intuitive but clients hate building long URLs and middleware proliferates. Many teams adopt <strong>always-flat</strong> with filter params; RESTful style is prescriptive but the pragmatic "flat + filter" approach is often simpler. GraphQL sidesteps URL-tree design entirely — one endpoint with graph traversal. In your API docs (OpenAPI), use tags to group related routes regardless of URL tree — clients discover resources that way.</p>
'''

ANSWERS[68] = r'''
<p><strong>Situation:</strong> async code in Node — callbacks are hard to read, unhandled promise rejections crash modern Node, and concurrent ops need orchestration. <code>async/await</code> is the right primitive; master a few patterns.</p>
<p><strong>Approach:</strong> prefer <code>await</code> linearly; use <code>Promise.all</code> for independent parallel work; <code>Promise.allSettled</code> when failures shouldn't abort the batch; don't forget <code>try/catch</code> around every <code>await</code> that can throw; respect <code>AbortController</code> for cancellation.</p>
<pre><code>// 1. Sequential when each depends on the previous
async function publishPost(id) {
  const post = await db.post.findUnique({ where: { id } });
  if (!post) throw new NotFound("Post", id);
  const rendered = await render(post);
  const url = await s3Upload(rendered);
  await db.post.update({ where: { id }, data: { publishedUrl: url } });
  return url;
}

// 2. Parallel when independent — ~5× faster
async function loadDashboard(userId) {
  const [user, recent, notifications, balance] = await Promise.all([
    db.user.findUnique({ where: { id: userId } }),
    db.event.findMany({ where: { userId }, take: 20 }),
    db.notification.count({ where: { userId, readAt: null } }),
    billingApi.getBalance(userId),
  ]);
  return { user, recent, notifications, balance };
}

// 3. Tolerant of partial failure — Promise.allSettled
async function fanOutEmails(users, template) {
  const results = await Promise.allSettled(
    users.map(u =&gt; sendEmail({ to: u.email, template, data: u }))
  );
  const failed = results
    .map((r, i) =&gt; r.status === "rejected" ? users[i] : null)
    .filter(Boolean);
  if (failed.length) log.warn({ failed: failed.length }, "some emails failed");
  return { sent: results.length - failed.length, failed };
}

// 4. Concurrency cap — p-limit or p-queue
import pLimit from "p-limit";
const limit = pLimit(10);    // max 10 parallel
const uploaded = await Promise.all(
  files.map(f =&gt; limit(() =&gt; s3Upload(f)))
);

// 5. Timeouts + cancellation
async function fetchWithTimeout(url, ms = 5000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() =&gt; ctrl.abort(), ms);
  try { return await fetch(url, { signal: ctrl.signal }); }
  finally { clearTimeout(timer); }
}

// 6. Retries with jitter
async function withRetry(fn, { attempts = 3, baseMs = 200 } = {}) {
  for (let i = 0; i &lt; attempts; i++) {
    try { return await fn(); }
    catch (e) {
      if (i === attempts - 1) throw e;
      const wait = baseMs * 2 ** i + Math.random() * 100;
      await new Promise(r =&gt; setTimeout(r, wait));
    }
  }
}</code></pre>
<p><strong>Pitfalls:</strong></p>
<ul>
  <li><code>forEach</code> ignores returned promises — use <code>for...of</code> for sequential or <code>Promise.all(map(...))</code> for parallel.</li>
  <li>Rejected promises with no handler — crashes in Node 15+. Always chain <code>.catch</code> or wrap in try/catch.</li>
  <li>Over-parallelizing — 10,000 <code>Promise.all</code> network calls DoS yourself. Always cap concurrency.</li>
  <li>Forgetting <code>await</code> — <code>async function</code> still returns a Promise; the caller might see <code>[object Promise]</code> or silent errors.</li>
  <li>Top-level await is available in ESM and repl — use it for boot-time async (loading secrets, migrations).</li>
</ul>
<p><strong>Trade-offs:</strong> async/await is strictly better than raw <code>.then/.catch</code> — use it. Callback style (<code>util.promisify</code>) only when interfacing with old APIs. Understand when to reach for a concurrency lib: p-limit (simple), p-queue (priority/pause), Bottleneck (rate limiting with reservoirs). For heavy concurrent workflows, consider actor/workflow engines (BullMQ, Temporal) instead of hand-rolled orchestration.</p>
'''

ANSWERS[69] = r'''
<p><strong>Situation:</strong> compliance needs audit trails (who did what, when), product wants to analyze user journeys, and security needs abuse detection — all on the same event stream, without slowing request handlers.</p>
<p><strong>Approach:</strong> capture events with AsyncLocalStorage-propagated context (user, reqId, traceId); write to an append-only audit table for compliance; pipe a copy to an analytics sink (Kafka → warehouse, or Segment/RudderStack). Never block the HTTP response on audit writes.</p>
<pre><code>// activity.ts
import { AsyncLocalStorage } from "node:async_hooks";

const ctx = new AsyncLocalStorage&lt;{ userId?: string; reqId: string; ip: string; userAgent?: string }&gt;();

export function withActivityContext(req, _res, next) {
  const reqId = req.headers["x-request-id"] ?? crypto.randomUUID();
  ctx.run({ userId: req.user?.sub, reqId, ip: req.ip, userAgent: req.get("user-agent") }, next);
}

type ActivityKind = "user.login" | "user.logout" | "post.create" | "post.update" | "post.delete"
                  | "admin.impersonate" | "billing.charge" | "export.generated";

export async function logActivity(kind: ActivityKind, subject: { type: string; id: string }, data?: unknown) {
  const c = ctx.getStore();
  // Write-behind — don't block the caller
  auditQueue.add("event", {
    kind,
    actorId: c?.userId,
    subjectType: subject.type,
    subjectId: subject.id,
    data,
    ip: c?.ip,
    userAgent: c?.userAgent,
    requestId: c?.reqId,
    at: new Date().toISOString(),
  }, { attempts: 5, removeOnComplete: { age: 3600 } });
}

// Worker — appends to audit_log (append-only, partitioned by month)
new Worker("audit", async ({ data }) =&gt; {
  await db.auditLog.create({ data });
  // Mirror to analytics sink for BI
  analytics.track({ userId: data.actorId, event: data.kind, properties: data.data });
}, { connection, concurrency: 50 });

// Usage in business logic
async function updatePost(id, patch, user) {
  const before = await db.post.findUnique({ where: { id } });
  if (!before) throw new NotFound("Post", id);
  const after = await db.post.update({ where: { id }, data: patch });
  await logActivity("post.update", { type: "Post", id }, {
    changes: diff(before, after),
  });
  return after;
}</code></pre>
<p><strong>Schema considerations:</strong></p>
<pre><code>-- audit_log (partitioned by month for retention pruning)
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  kind TEXT NOT NULL,
  actor_id UUID,
  subject_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  data JSONB,
  ip INET,
  user_agent TEXT,
  request_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);
CREATE INDEX idx_audit_actor_time ON audit_log (actor_id, created_at DESC);
CREATE INDEX idx_audit_subject ON audit_log (subject_type, subject_id, created_at DESC);
-- Keep 2 years hot, archive to S3 Parquet after</code></pre>
<p><strong>Trade-offs:</strong> <strong>audit logs are different from observability logs</strong> — they're business facts with legal weight, not debugging output. Append-only (no updates/deletes), signed or hashed for tamper-evidence in regulated industries, stored for the retention required by policy (SOX: 7 yrs, GDPR: minimize). Write-behind via a queue avoids adding latency to the happy path; retry-with-DLQ keeps audit complete even during DB blips. For analytics, a dedicated pipeline (Segment, Snowflake pipes, ClickHouse) outperforms ad-hoc SQL on the audit table. <strong>Never</strong> log PII you don't need (consent-affected fields should be omitted or hashed) — audit logs are high-value targets.</p>
'''

ANSWERS[70] = r'''
<p><strong>Situation:</strong> collaborative features (shared documents, dashboards, task boards) need live updates across clients — edits made by one user appear on everyone else's screen within a second.</p>
<p><strong>Approach:</strong> WebSockets with room-per-document; server broadcasts change events to the room; clients apply patches. For conflict-free concurrent editing, reach for CRDTs (Yjs, Automerge) — the "what happens when two users edit the same field at once" problem needs more than plain broadcast.</p>
<pre><code>// Simple change-broadcast pattern — for dashboards, boards, lists
import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";

const io = new Server(httpServer, { path: "/rt" });
io.adapter(createAdapter(pub, sub));
io.use(authMiddleware);

io.on("connection", (socket) =&gt; {
  const user = socket.data.user;

  socket.on("doc:join", async (docId) =&gt; {
    if (!(await canAccess(user, docId))) return socket.emit("err", "forbidden");
    socket.join(`doc:${docId}`);
    const snapshot = await loadDoc(docId);
    socket.emit("doc:snapshot", { docId, data: snapshot, version: snapshot.version });
  });

  socket.on("doc:patch", async ({ docId, patch, baseVersion }) =&gt; {
    // Optimistic concurrency control — reject if patch is stale
    const doc = await db.doc.findUnique({ where: { id: docId } });
    if (doc.version !== baseVersion) {
      return socket.emit("doc:conflict", { docId, currentVersion: doc.version });
    }
    const newVersion = doc.version + 1;
    await db.doc.update({
      where: { id: docId, version: baseVersion },    // optimistic lock
      data: { data: applyPatch(doc.data, patch), version: newVersion, updatedAt: new Date() },
    });
    // Broadcast to everyone in the room EXCEPT the sender
    socket.to(`doc:${docId}`).emit("doc:patched", {
      docId, patch, version: newVersion, by: user.id,
    });
    socket.emit("doc:ack", { docId, version: newVersion });
  });
});</code></pre>
<pre><code>// CRDT approach with Yjs — handles concurrent edits automatically
import { Server } from "ws";
import { setupWSConnection } from "y-websocket-server";

const wss = new Server({ noServer: true });
httpServer.on("upgrade", async (req, socket, head) =&gt; {
  // Authenticate on upgrade
  try { await verifyToken(new URL(req.url, "http://x").searchParams.get("t")); }
  catch { return socket.destroy(); }
  wss.handleUpgrade(req, socket, head, (ws) =&gt; setupWSConnection(ws, req));
});
// Each doc is a Y.Doc; Yjs handles merges, persists to Redis/Postgres via y-redis/y-leveldb</code></pre>
<p><strong>Trade-offs:</strong> the simple broadcast pattern works for <strong>non-conflicting</strong> updates (Kanban card moves, checkbox toggles, list reordering with LWW). For concurrent text editing or tree edits where two users can modify the same region simultaneously, CRDTs (Yjs is the standard) or OT (what Google Docs uses) are required — rolling your own is brittle. <strong>Presence</strong> (who's here, who's typing, cursor position) is a small separate problem — broadcast at 10-30 Hz with debouncing. Always include a <strong>base version</strong> in patches so the server can reject stale writes. For offline editing + sync on reconnect, Yjs/Automerge are near-mandatory. Persist snapshots periodically; don't replay thousands of ops on every load.</p>
'''

ANSWERS[71] = r'''
<p><strong>Situation:</strong> login and signup forms attract bots that stuff credentials or register fake accounts. CAPTCHA in front of these endpoints deters automation without hurting legitimate users too much.</p>
<p><strong>Approach:</strong> use a hosted CAPTCHA (hCaptcha, Cloudflare Turnstile, reCAPTCHA v3) — it's a one-line frontend change and a server-side verify call. Enforce CAPTCHA only when risk signals fire (repeated failures, new IP, suspect UA) so humans don't see it constantly.</p>
<pre><code>// Frontend (brief): include widget; on submit, the widget yields a token.
// &lt;div class="cf-turnstile" data-sitekey="0x..."&gt;&lt;/div&gt;
// On submit: form sends req.body.captchaToken

// Backend: verify with provider
import { request } from "undici";

async function verifyTurnstile(token, ip) {
  const body = new URLSearchParams({
    secret: process.env.TURNSTILE_SECRET,
    response: token,
    remoteip: ip,
  });
  const res = await request("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST", body,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  const { success, "error-codes": errors, hostname } = await res.body.json();
  return { success, errors, hostname };
}

// Adaptive — only require captcha when risky
async function loginHandler(req, res) {
  const { email, password, captchaToken } = req.body;
  const risk = await assessRisk(email, req.ip);     // failed attempts, new device, proxy IP

  if (risk &gt;= 0.5) {
    if (!captchaToken) return res.status(401).json({ error: "CAPTCHA_REQUIRED" });
    const { success } = await verifyTurnstile(captchaToken, req.ip);
    if (!success) return res.status(401).json({ error: "CAPTCHA_FAILED" });
  }

  const user = await verifyPassword(email, password);
  if (!user) {
    await incrementFailure(email, req.ip);           // feeds future risk score
    return res.status(401).json({ error: "INVALID_CREDENTIALS" });
  }
  // ... issue tokens
}

// Custom math CAPTCHA — only for low-stakes use (not security)
import { randomInt } from "node:crypto";
import jwt from "jsonwebtoken";

app.get("/captcha/math", (_req, res) =&gt; {
  const a = randomInt(1, 10), b = randomInt(1, 10);
  const token = jwt.sign({ sum: a + b }, process.env.CAPTCHA_SECRET, { expiresIn: "5m" });
  res.json({ question: `${a} + ${b} = ?`, token });
});
app.post("/captcha/verify", (req, res) =&gt; {
  try {
    const { sum } = jwt.verify(req.body.token, process.env.CAPTCHA_SECRET);
    if (Number(req.body.answer) !== sum) return res.status(400).json({ ok: false });
    res.json({ ok: true });
  } catch { res.status(400).json({ ok: false }); }
});</code></pre>
<p><strong>Trade-offs:</strong> <strong>hCaptcha</strong> and <strong>Cloudflare Turnstile</strong> are privacy-respecting and free for most volumes; <strong>reCAPTCHA v3</strong> scores risk invisibly but sends data to Google. <strong>Turnstile</strong> is the 2026 default for most projects — no user interaction, free, privacy-clean. Pair with <strong>rate limiting + account lockout + breach password check</strong> — CAPTCHA alone is bypassable (farms of humans solving for fractions of cents). Custom math/image CAPTCHAs are weak — bots solve them easily; use only for low-stakes flows like comment posting. For API abuse, consider <strong>device attestation</strong> (App Attest, Play Integrity) on mobile or <strong>proof-of-work</strong> (Friendly Captcha) for silent challenges.</p>
'''

ANSWERS[72] = r'''
<p><strong>Situation:</strong> frontend team wants typed queries, selective field fetching, and a single endpoint — GraphQL fits. You need a production Apollo Server with security, performance, and tooling.</p>
<p><strong>Approach:</strong> Apollo Server 4 with Express; schema-first SDL; DataLoader for N+1; depth + cost limits; persisted queries in prod; OpenTelemetry integration; @defer/@stream for latency-sensitive fields.</p>
<pre><code>import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { ApolloServerPluginLandingPageProductionDefault } from "@apollo/server/plugin/landingPage/default";
import depthLimit from "graphql-depth-limit";
import { createComplexityRule } from "graphql-query-complexity";
import DataLoader from "dataloader";

const typeDefs = /* GraphQL */ `
  type Query {
    post(id: ID!): Post
    posts(first: Int = 20, after: String): PostConnection!
  }
  type Post { id: ID! title: String! author: User! comments: [Comment!]! }
  type User { id: ID! name: String! posts: [Post!]! }
  type Comment { id: ID! text: String! author: User! }
  type PostEdge { node: Post! cursor: String! }
  type PostConnection { edges: [PostEdge!]! pageInfo: PageInfo! }
  type PageInfo { hasNextPage: Boolean! endCursor: String }
`;

const resolvers = {
  Query: {
    post: (_, { id }, { loaders }) =&gt; loaders.post.load(id),
    posts: async (_, { first, after }) =&gt; {
      const posts = await db.post.findMany({
        take: first + 1, ...(after &amp;&amp; { cursor: { id: after }, skip: 1 }),
        orderBy: { createdAt: "desc" },
      });
      const hasNext = posts.length &gt; first;
      return {
        edges: posts.slice(0, first).map(p =&gt; ({ node: p, cursor: p.id })),
        pageInfo: { hasNextPage: hasNext, endCursor: posts[first - 1]?.id ?? null },
      };
    },
  },
  Post:    { author: (p, _, { loaders }) =&gt; loaders.user.load(p.authorId) },
  Comment: { author: (c, _, { loaders }) =&gt; loaders.user.load(c.authorId) },
};

// Per-request DataLoader — fixes N+1
function makeLoaders() {
  return {
    user: new DataLoader(async (ids: readonly string[]) =&gt; {
      const users = await db.user.findMany({ where: { id: { in: [...ids] } } });
      const byId = new Map(users.map(u =&gt; [u.id, u]));
      return ids.map(id =&gt; byId.get(id));
    }),
    post: new DataLoader(async (ids: readonly string[]) =&gt; {
      const posts = await db.post.findMany({ where: { id: { in: [...ids] } } });
      const byId = new Map(posts.map(p =&gt; [p.id, p]));
      return ids.map(id =&gt; byId.get(id));
    }),
  };
}

const server = new ApolloServer({
  typeDefs, resolvers,
  validationRules: [
    depthLimit(10),
    createComplexityRule({ maximumComplexity: 1000, variables: {}, estimators: [/* ... */] }),
  ],
  plugins: [
    ApolloServerPluginLandingPageProductionDefault({ embed: true }),
    // APQ / persisted queries for caching + query allowlisting in prod
  ],
  introspection: process.env.NODE_ENV !== "production",
});
await server.start();

app.use("/graphql", express.json({ limit: "50kb" }), expressMiddleware(server, {
  context: async ({ req }) =&gt; ({
    user: req.user,
    loaders: makeLoaders(),
  }),
}));</code></pre>
<p><strong>Trade-offs:</strong> GraphQL's per-request flexibility shifts burden to the server — <strong>N+1 is the default failure mode</strong>; DataLoader is non-optional. <strong>Security:</strong> introspection off in prod, depth limit (~10), cost limit, auth per resolver or via directives (<code>@auth(role: ADMIN)</code>). <strong>Persisted queries</strong>: clients send hashes instead of raw queries; server allowlists known ones — prevents arbitrary-query abuse and shrinks wire size. <strong>Caching:</strong> Apollo Cache Control headers + CDN; or Fastify-based Mercurius for better perf. For federation across services, <strong>Apollo Federation</strong> or <strong>GraphQL Mesh</strong>. Alternatives: <strong>tRPC</strong> (TS end-to-end, no codegen), <strong>gRPC</strong> (service-to-service), <strong>REST + OpenAPI</strong> (simplest operations). GraphQL shines when frontends are the primary consumer and data shape varies per view.</p>
'''

ANSWERS[73] = r'''
<p><strong>Situation:</strong> admins need to export data snapshots and import them into another environment (e.g., staging seed, customer offboarding). JSON is the interchange format; the file can be large.</p>
<p><strong>Approach:</strong> export via streaming JSON (NDJSON = newline-delimited JSON for huge sets, or <code>JSONStream</code> for arrays); import with bounded-memory parse; validate with Zod before applying; idempotent with upsert on stable keys.</p>
<pre><code>// EXPORT — NDJSON stream; constant memory even for 10M rows
import { pipeline } from "node:stream/promises";
import { Transform } from "node:stream";

app.get("/export/orders.ndjson", requireRole("admin"), async (req, res) =&gt; {
  res.setHeader("Content-Type", "application/x-ndjson");
  res.setHeader("Content-Disposition", 'attachment; filename="orders.ndjson"');

  const toJsonLine = new Transform({
    objectMode: true, writableHighWaterMark: 256,
    transform(row, _enc, cb) { cb(null, JSON.stringify(row) + "\n"); },
  });

  await pipeline(
    db.order.streamCursor({ where: { tenantId: req.user.tenantId } }),  // async iterable
    toJsonLine,
    res,
  );
});

// IMPORT — parse NDJSON line-by-line
import readline from "node:readline";
import { z } from "zod";

const OrderImport = z.object({
  externalId: z.string(),
  customerEmail: z.string().email(),
  total: z.number().positive(),
  items: z.array(z.object({ sku: z.string(), qty: z.number().int().positive(), price: z.number() })),
  createdAt: z.coerce.date(),
});

app.post("/import/orders", requireRole("admin"), async (req, res) =&gt; {
  const rl = readline.createInterface({ input: req, crlfDelay: Infinity });
  let n = 0, ok = 0, failed = [];

  const CHUNK = 500;
  let batch = [];

  for await (const line of rl) {
    if (!line.trim()) continue;
    n++;
    try {
      const order = OrderImport.parse(JSON.parse(line));
      batch.push(order);
      if (batch.length &gt;= CHUNK) { ok += await flush(batch); batch = []; }
    } catch (e) { failed.push({ line: n, error: e.message }); }
  }
  if (batch.length) ok += await flush(batch);

  res.json({ total: n, imported: ok, failed });
});

async function flush(batch) {
  // Idempotent — upsert on a stable natural key
  await db.$transaction(batch.map(o =&gt; db.order.upsert({
    where: { externalId: o.externalId },
    create: { ...o, items: { create: o.items } },
    update: { total: o.total, items: { deleteMany: {}, create: o.items } },
  })));
  return batch.length;
}</code></pre>
<pre><code>// For smaller datasets — array JSON with JSONStream parse
import JSONStream from "JSONStream";
import { parser } from "stream-json";
import { streamArray } from "stream-json/streamers/StreamArray.js";

await pipeline(req, parser(), streamArray(), async function*(source) {
  for await (const { value } of source) {
    yield await OrderImport.parse(value);
  }
});</code></pre>
<p><strong>Trade-offs:</strong> NDJSON &gt;&gt; one-big-JSON-array for large sets — streamable, tolerant of partial corruption (bad line = skip, keep going), no huge-array memory spike. For complete datasets with relationships (orders + items + customers), ZIP of multiple NDJSON files keeps each resource small and parallelizable. Validate every row with Zod before DB touch — bad data mid-batch poisons the transaction. Include a <strong>manifest</strong> file with schema version, exporter version, and timestamps so imports across versions know how to map fields. Idempotent imports (upsert on external key) let you re-run safely; non-idempotent imports are disasters waiting to happen. For massive migrations, consider pg_dump / mongoexport + direct DB-level restore; application-level export belongs in the 10 MB – 1 GB range.</p>
'''

ANSWERS[74] = r'''
<p><strong>Situation:</strong> uploads need size/type/content validation, meaningful errors for users, and cleanup on failure. The default failure modes are silent (413 from reverse proxy, generic 500 from multer) — not what you want.</p>
<p><strong>Approach:</strong> multer with tight limits; wrap in an error-mapping middleware; validate MIME by magic bytes; use a virus scan or content filter; respond with structured 4xx errors the UI can display.</p>
<pre><code>import multer from "multer";
import { fileTypeFromBuffer } from "file-type";

const MAX_MB = 10;
const ALLOWED = new Set(["image/jpeg", "image/png", "image/webp", "application/pdf"]);

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: MAX_MB * 1024 * 1024,
    files: 5,
    fields: 20,
    fieldSize: 1024 * 100,
  },
  fileFilter: (_req, file, cb) =&gt; {
    // First-pass cheap check by extension/claimed mime — real check after read
    const extOk = /\.(jpe?g|png|webp|pdf)$/i.test(file.originalname);
    const mimeOk = ALLOWED.has(file.mimetype);
    if (!extOk || !mimeOk) return cb(Object.assign(new Error("INVALID_TYPE"), { code: "INVALID_TYPE" }));
    cb(null, true);
  },
});

app.post("/documents", requireAuth, (req, res, next) =&gt; {
  upload.array("files", 5)(req, res, async (err) =&gt; {
    // Translate multer-specific errors to user-facing ones
    if (err) return next(translateUploadError(err));
    if (!req.files?.length) return res.status(400).json({ error: "NO_FILES" });

    // Second-pass MIME by magic bytes — NEVER trust Content-Type alone
    const results = await Promise.allSettled(req.files.map(async (f) =&gt; {
      const ft = await fileTypeFromBuffer(f.buffer);
      if (!ft || !ALLOWED.has(ft.mime)) throw Object.assign(new Error("INVALID_CONTENT"), { file: f.originalname });
      // Optional: scan with ClamAV
      // const clean = await clamav.scanBuffer(f.buffer); if (!clean) throw Error("MALWARE");
      const key = await uploadToS3(f.buffer, f.originalname, ft.mime, req.user.sub);
      return { key, originalName: f.originalname, mime: ft.mime, size: f.size };
    }));

    const ok = results.filter(r =&gt; r.status === "fulfilled").map(r =&gt; r.value);
    const failed = results
      .map((r, i) =&gt; r.status === "rejected" ? { name: req.files[i].originalname, error: r.reason.message } : null)
      .filter(Boolean);

    res.status(failed.length ? 207 : 201).json({ uploaded: ok, failed });
  });
});

function translateUploadError(err) {
  if (err.code === "LIMIT_FILE_SIZE")
    return Object.assign(new Error(`file too large (max ${MAX_MB} MB)`), { status: 413 });
  if (err.code === "LIMIT_FILE_COUNT")
    return Object.assign(new Error("too many files"), { status: 400 });
  if (err.code === "INVALID_TYPE")
    return Object.assign(new Error("unsupported type"), { status: 415 });
  return Object.assign(new Error("upload failed"), { status: 400 });
}</code></pre>
<p><strong>Trade-offs:</strong> multer's memory storage is fine for small files (&lt; 10 MB) but dangerous for larger uploads — disk storage (<code>multer.diskStorage</code>) or streaming directly to S3 (busboy + @aws-sdk/lib-storage) for big files. Always validate by magic bytes (<code>file-type</code> or <code>magic-bytes.js</code>) — <code>Content-Type</code> is client-controlled and trivial to spoof. For user-facing apps, return 207 Multi-Status with per-file results when uploading many; clients can render per-row errors. Set file size limits at <em>every</em> layer: Nginx <code>client_max_body_size</code>, Express body-parser limit, multer <code>fileSize</code>. Clean up partially-uploaded files on error — leaked bytes become leaked money. Consider ClamAV or a cloud malware scanning API for user-sourced content.</p>
'''

ANSWERS[75] = r'''
<p><strong>Situation:</strong> your app runs multiple replicas behind a load balancer. In-process session storage doesn't work (requests bounce between replicas); signed cookies can't be revoked. Redis gives you shared, fast, TTL-aware sessions.</p>
<p><strong>Approach:</strong> <code>express-session</code> + <code>connect-redis</code>; HTTP-only secure cookie holds only the session id; session data lives in Redis keyed by that id; rolling TTL for active-user UX; regenerate id on privilege change.</p>
<pre><code>import session from "express-session";
import { RedisStore } from "connect-redis";
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL);

app.use(session({
  store: new RedisStore({ client: redis, prefix: "sess:", ttl: 60 * 60 * 8 }),  // 8h
  secret: process.env.SESSION_SECRET,
  name: "sid",
  resave: false,
  saveUninitialized: false,
  rolling: true,                                 // reset TTL on each request
  cookie: {
    httpOnly: true,
    secure: true,                                // HTTPS only
    sameSite: "lax",                             // "strict" breaks OAuth flows
    maxAge: 8 * 3600 * 1000,
    domain: ".example.com",                      // subdomain sharing
  },
}));

// Login — regenerate to prevent session fixation
app.post("/auth/login", async (req, res) =&gt; {
  const user = await verifyPassword(req.body.email, req.body.password);
  if (!user) return res.status(401).json({ error: "INVALID_CREDENTIALS" });
  await new Promise((resolve, reject) =&gt; req.session.regenerate(err =&gt; err ? reject(err) : resolve()));
  req.session.userId = user.id;
  req.session.roles = user.roles;
  req.session.loggedInAt = Date.now();
  req.session.userAgent = req.get("user-agent");
  req.session.ip = req.ip;
  res.json({ ok: true });
});

// Auth guard
export const requireSession = (req, res, next) =&gt;
  req.session.userId ? next() : res.status(401).json({ error: "UNAUTHORIZED" });

// Logout — delete server-side + clear cookie
app.post("/auth/logout", (req, res) =&gt;
  req.session.destroy(() =&gt; res.clearCookie("sid").status(204).end()));

// List active sessions for a user
app.get("/me/sessions", requireSession, async (req, res) =&gt; {
  const keys = await redis.keys("sess:*");
  const sessions = [];
  for (const k of keys) {
    const raw = await redis.get(k);
    if (raw) {
      const s = JSON.parse(raw);
      if (s.userId === req.session.userId) {
        sessions.push({ id: k.slice(5), ip: s.ip, userAgent: s.userAgent, loggedInAt: s.loggedInAt });
      }
    }
  }
  res.json(sessions);
});

// Revoke — sign user out of every device
async function revokeAllSessions(userId) {
  // For precise + scalable: maintain index "sess-by-user:{userId}" SET when creating sessions
  const keys = await redis.keys(`sess:*`);
  const pipeline = redis.pipeline();
  for (const k of keys) {
    const raw = await redis.get(k);
    if (raw &amp;&amp; JSON.parse(raw).userId === userId) pipeline.del(k);
  }
  await pipeline.exec();
}</code></pre>
<p><strong>Trade-offs:</strong> sessions cost ~1 ms Redis lookup per request but give instant revocation (vs. JWT's short-expiry + deny-list workaround). <strong>For browser apps</strong> cookies are the right home — don't use <code>localStorage</code> (XSS-exfiltrable). <strong>Pair with CSRF protection</strong> (double-submit token or SameSite=Strict where flows allow) since cookies are auto-sent. <strong>Don't</strong> put heavy data in sessions (the full user object) — keep it to ids and re-fetch; bloated sessions slow every request. For multi-device management, maintain a per-user session index (<code>SADD sess-by-user:{id} {sid}</code>) so revocation is O(device-count) not O(total-sessions). If Redis goes down, the app is unusable — Redis Cluster or Sentinel for HA. JWTs remain preferable for stateless microservices or mobile APIs where the session-lookup cost compounds across service hops.</p>
'''

ANSWERS[76] = r'''
<p><strong>Situation:</strong> your app serves APIs + static assets over HTTPS. HTTP/2 multiplexes many requests on one TCP connection, eliminating head-of-line blocking — useful for frontends pulling dozens of small resources. HTTP/3 (QUIC) is even better for flaky networks.</p>
<p><strong>Approach:</strong> in 2026, terminate HTTP/2 (and increasingly HTTP/3) at the edge (Nginx, Caddy, CloudFront, Cloudflare) and speak HTTP/1.1 upstream to Node — simpler, proven, and Node's <code>http2</code> module is still awkward. For direct HTTP/2 in Node, use <code>node:http2</code>.</p>
<pre><code>// Direct HTTP/2 in Node (when edge termination isn't possible)
import { createSecureServer } from "node:http2";
import { readFileSync } from "node:fs";

const server = createSecureServer({
  key: readFileSync("key.pem"),
  cert: readFileSync("cert.pem"),
  allowHTTP1: true,   // accept old clients
});

server.on("stream", (stream, headers) =&gt; {
  const path = headers[":path"];
  const method = headers[":method"];

  if (method === "GET" &amp;&amp; path === "/api/user") {
    stream.respond({
      ":status": 200,
      "content-type": "application/json",
    });
    stream.end(JSON.stringify({ id: 1, name: "Ada" }));
  } else {
    stream.respond({ ":status": 404 });
    stream.end();
  }
});

server.listen(443);

// Server Push (deprecated in many browsers but still useful for SSE/long-poll)
// Most apps should use &lt;link rel="preload"&gt; headers instead</code></pre>
<pre><code># Much more commonly: let Nginx or Caddy terminate HTTP/2, proxy HTTP/1.1 to Node
server {
  listen 443 ssl http2;                 # HTTP/2 to clients
  server_name api.example.com;
  # ... TLS config ...
  location / {
    proxy_pass http://127.0.0.1:3000;   # HTTP/1.1 to Node
    proxy_http_version 1.1;
    proxy_set_header Connection "";
  }
}</code></pre>
<ul>
  <li><strong>Multiplexing:</strong> one TCP connection carries many concurrent requests without head-of-line blocking at the HTTP level — huge for pages that fetch many small resources.</li>
  <li><strong>Header compression (HPACK):</strong> repeated headers (cookies, auth) don't re-send in full — big savings on API-heavy pages.</li>
  <li><strong>Stream priorities:</strong> browsers hint which resources matter (CSS before images).</li>
  <li><strong>Binary framing:</strong> more efficient parsing than HTTP/1's text, and a single TCP connection means better congestion control.</li>
  <li><strong>Server Push</strong> is deprecated — use <code>Link: rel=preload</code> headers or <code>103 Early Hints</code> instead.</li>
</ul>
<p><strong>Trade-offs:</strong> Node's <code>http2</code> is functional but rarely used directly — the ecosystem (Express, Koa, Fastify) is HTTP/1.1-shaped. Running HTTP/2 at the edge gives most of the benefits (multiplexed TCP to clients, compressed headers, single keep-alive connection) with zero app changes. <strong>HTTP/3 (QUIC over UDP)</strong> removes TCP head-of-line blocking at the transport layer — big for mobile/lossy networks; supported by Cloudflare, CloudFront, Caddy. For backend-to-backend, <strong>gRPC over HTTP/2</strong> is the dominant binary protocol — use it for microservice calls where streaming or typed contracts matter.</p>
'''

ANSWERS[77] = r'''
<p><strong>Situation:</strong> some config must change at runtime — feature flags, rate limits, experiment buckets, A/B variants — without redeploying the app. Restart-requiring env vars are too slow.</p>
<p><strong>Approach:</strong> use a feature-flag/dynamic-config service (Unleash, LaunchDarkly, AWS AppConfig, ConfigCat) or build a minimal one with Redis + pub/sub. Fetch on boot + subscribe to changes; cache in memory; fail safe when config is unreachable.</p>
<pre><code>// Option A — Unleash (open source, self-hostable)
import { startUnleash, InMemStorageProvider } from "unleash-client";

const unleash = await startUnleash({
  url: "https://unleash.example.com/api/",
  appName: process.env.SERVICE_NAME,
  customHeaders: { Authorization: process.env.UNLEASH_TOKEN },
  storageProvider: new InMemStorageProvider(),
  refreshInterval: 10_000,   // poll changes every 10 s
});

// Anywhere in code — zero-latency flag check
function checkoutV2(user) {
  if (unleash.isEnabled("checkout-v2", { userId: user.id, properties: { plan: user.plan } })) {
    return newCheckoutFlow(user);
  }
  return oldCheckoutFlow(user);
}

// Option B — simple Redis-backed config with pub/sub
import Redis from "ioredis";
import { EventEmitter } from "node:events";
const redis = new Redis(process.env.REDIS_URL);
const sub = redis.duplicate();
const bus = new EventEmitter();

let cache = {};
async function loadAll() {
  const entries = await redis.hgetall("config:app");
  cache = Object.fromEntries(Object.entries(entries).map(([k, v]) =&gt; [k, JSON.parse(v)]));
}
await loadAll();
await sub.subscribe("config:invalidate");
sub.on("message", async () =&gt; { await loadAll(); bus.emit("change", cache); });

export function getConfig(key, fallback) {
  return key in cache ? cache[key] : fallback;
}

// Admin endpoint — update + broadcast
app.put("/admin/config/:key", requireRole("admin"), async (req, res) =&gt; {
  await redis.hset("config:app", req.params.key, JSON.stringify(req.body.value));
  await redis.publish("config:invalidate", "1");    // all replicas reload
  res.json({ ok: true });
});

// Usage — poll-free reads at call sites
const limit = getConfig("api.rateLimit.perMinute", 100);
const enabled = getConfig("features.newCheckout", false);</code></pre>
<p><strong>Patterns and pitfalls:</strong></p>
<ul>
  <li><strong>Fail safe</strong>: if the config service is down, use last-known-good values — don't crash.</li>
  <li><strong>Percentage rollouts</strong>: hash <code>userId + flagName</code> to a bucket so the same user consistently gets the same variant.</li>
  <li><strong>Kill switches</strong>: on-call should flip a flag to disable a new feature in seconds, not minutes.</li>
  <li><strong>Avoid config drift</strong> in code — prefer one service per flag; many flags = config debt.</li>
  <li><strong>Audit changes</strong>: who toggled what + when; rollback is a button, not an SRE incident.</li>
  <li><strong>Don't</strong> put secrets in dynamic config — they belong in a secret manager with different access patterns and audit.</li>
</ul>
<p><strong>Trade-offs:</strong> SaaS (LaunchDarkly, Statsig) gives sophisticated targeting + analytics for a per-user fee. Self-hosted (Unleash, FlagD) is cheaper at scale, more control. For simple kill switches, a Redis hash + pub/sub is 50 lines of code. Don't over-architect — if "config" means 3 flags, env vars + redeploy is fine; dynamic config becomes valuable at ~10+ flags with frequent toggling.</p>
'''

ANSWERS[78] = r'''
<p><strong>Situation:</strong> cross-cutting request/response concerns — adding correlation IDs, trimming sensitive headers, normalizing JSON envelopes, enforcing <code>Content-Security-Policy</code>, logging response times. These don't belong in handlers.</p>
<p><strong>Approach:</strong> Express middleware pipeline. Request transformers run early; response transformers monkey-patch <code>res.json</code>/<code>res.send</code> or use a <code>finish</code> event. Keep each middleware single-purpose and composable.</p>
<pre><code>// Request normalization — trim strings, normalize emails
export function normalizeRequest(req, _res, next) {
  if (req.body &amp;&amp; typeof req.body === "object") {
    for (const k of Object.keys(req.body)) {
      if (typeof req.body[k] === "string") req.body[k] = req.body[k].trim();
    }
    if (req.body.email) req.body.email = req.body.email.toLowerCase();
  }
  next();
}

// Request ID + logging
export function requestId(req, res, next) {
  req.id = req.get("x-request-id") ?? crypto.randomUUID();
  res.setHeader("x-request-id", req.id);
  next();
}

// Response envelope — wrap everything uniformly
export function envelope(req, res, next) {
  const _json = res.json.bind(res);
  res.json = function (body) {
    // Already-wrapped errors stay as-is
    if (body?.error) return _json(body);
    return _json({ data: body, meta: { requestId: req.id, timestamp: new Date().toISOString() } });
  };
  next();
}

// Response time
export function responseTime(_req, res, next) {
  const start = process.hrtime.bigint();
  res.on("finish", () =&gt; {
    const ms = Number(process.hrtime.bigint() - start) / 1e6;
    res.setHeader("X-Response-Time", `${ms.toFixed(1)}ms`);     // too late for client, but good for self-observation
    metrics.histogram("http.request.duration_ms").observe(ms);
  });
  next();
}

// Strip sensitive response headers
export function stripHeaders(_req, res, next) {
  res.removeHeader("X-Powered-By");
  res.removeHeader("Server");
  next();
}

// Compose
app.use(requestId);
app.use(express.json({ limit: "100kb" }));
app.use(normalizeRequest);
app.use(responseTime);
app.use(stripHeaders);
app.use(envelope);      // route handlers just call res.json(data); envelope wraps
app.use(routes);
app.use(errorHandler);  // last</code></pre>
<p><strong>Patterns:</strong></p>
<ul>
  <li><strong>Order matters</strong>: body parser before validation; auth before protected routes; error handler last.</li>
  <li><strong>Short-circuit</strong>: middleware that calls <code>res.send()</code> and doesn't call <code>next()</code> ends the chain — auth failures, cache hits.</li>
  <li><strong>Stateless</strong>: never stash cross-request state in middleware closure; use <code>req</code>/<code>res</code> locals or AsyncLocalStorage.</li>
  <li><strong>Monkey-patch carefully</strong> — wrap <code>res.json</code> in a way that's idempotent (envelope multiple times = bad).</li>
  <li><strong>Use <code>res.on("finish")</code></strong> for metrics/logging that need final status + size.</li>
</ul>
<p><strong>Trade-offs:</strong> Express middleware is a known, explicit contract. Koa's async middleware (with <code>await next()</code>) is cleaner for pre-and-post work — if starting fresh on a high-throughput API, <strong>Fastify</strong>'s hook system (onRequest, preValidation, onSend, onResponse) is more structured and faster. Don't over-middleware — every layer adds latency, and tangled chains make it hard to reason about order. Centralize cross-cutting concerns in one module per concern; keep business-logic middleware route-specific.</p>
'''

ANSWERS[79] = r'''
<p><strong>Situation:</strong> you sell a SaaS with monthly/yearly subscriptions, metered add-ons, trials, upgrades/downgrades, and failed-payment retries. Building billing yourself is a year-long project — use Stripe (or Paddle, Lemon Squeezy) and integrate carefully.</p>
<p><strong>Approach:</strong> Stripe Billing models customers → subscriptions → prices → invoices. Your app tracks userId↔stripeCustomerId mapping and entitlements derived from subscription state. <strong>Webhooks</strong> are the source of truth for billing state — never trust client-side callbacks.</p>
<pre><code>// 1. Create customer + checkout session
import Stripe from "stripe";
const stripe = new Stripe(process.env.STRIPE_SECRET, { apiVersion: "2025-08-20" });

app.post("/billing/checkout", requireAuth, async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.user.sub } });
  const customerId = user.stripeCustomerId ?? await (async () =&gt; {
    const c = await stripe.customers.create({ email: user.email, metadata: { userId: user.id } });
    await db.user.update({ where: { id: user.id }, data: { stripeCustomerId: c.id } });
    return c.id;
  })();

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer: customerId,
    line_items: [{ price: req.body.priceId, quantity: 1 }],
    success_url: `${process.env.APP_URL}/billing/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.APP_URL}/pricing`,
    allow_promotion_codes: true,
    billing_address_collection: "required",
    subscription_data: { trial_period_days: 14, metadata: { userId: user.id } },
  });
  res.json({ url: session.url });
});

// 2. Webhook — source of truth
app.post("/webhooks/stripe",
  express.raw({ type: "application/json" }),
  async (req, res) =&gt; {
    let event;
    try {
      event = stripe.webhooks.constructEvent(req.body, req.get("stripe-signature"), process.env.STRIPE_WH_SECRET);
    } catch { return res.status(400).send("invalid signature"); }

    // Idempotency — Stripe may deliver twice
    const seen = await db.webhookEvent.findUnique({ where: { id: event.id } });
    if (seen) return res.json({ received: true });
    await db.webhookEvent.create({ data: { id: event.id, type: event.type } });

    switch (event.type) {
      case "customer.subscription.created":
      case "customer.subscription.updated":
        await syncSubscription(event.data.object);
        break;
      case "customer.subscription.deleted":
        await markSubscriptionCanceled(event.data.object);
        break;
      case "invoice.payment_failed":
        await handlePaymentFailed(event.data.object);
        break;
      case "invoice.payment_succeeded":
        await recordPayment(event.data.object);
        break;
    }
    res.json({ received: true });
  });

async function syncSubscription(sub) {
  await db.subscription.upsert({
    where: { stripeId: sub.id },
    update: {
      status: sub.status,
      priceId: sub.items.data[0].price.id,
      currentPeriodEnd: new Date(sub.current_period_end * 1000),
      cancelAt: sub.cancel_at ? new Date(sub.cancel_at * 1000) : null,
    },
    create: {
      stripeId: sub.id,
      userId: sub.metadata.userId,
      status: sub.status,
      priceId: sub.items.data[0].price.id,
      currentPeriodEnd: new Date(sub.current_period_end * 1000),
    },
  });
}

// 3. Entitlement check — derive from subscription state
export async function hasEntitlement(userId, feature) {
  const sub = await db.subscription.findFirst({
    where: { userId, status: { in: ["active", "trialing", "past_due"] } },
  });
  return sub?.status === "active" || sub?.status === "trialing";
  // Map priceId → features for finer-grained plans
}

// Customer portal — let users self-serve (upgrade, cancel, update card)
app.post("/billing/portal", requireAuth, async (req, res) =&gt; {
  const user = await db.user.findUnique({ where: { id: req.user.sub } });
  const session = await stripe.billingPortal.sessions.create({
    customer: user.stripeCustomerId,
    return_url: `${process.env.APP_URL}/settings/billing`,
  });
  res.json({ url: session.url });
});</code></pre>
<p><strong>Trade-offs:</strong> use Stripe Checkout + Customer Portal instead of building UI — saves months and handles PCI for you. <strong>Webhooks are the source of truth</strong>; don't assume a successful checkout redirect means the subscription is active (the user may have closed the tab). Idempotency on webhook handling is non-negotiable. For <strong>usage-based billing</strong>, report metered usage with <code>subscription_item.usage_records</code> aggregated per period. For non-card markets (EU SEPA, APAC, iDEAL) use <strong>Paddle</strong> (merchant-of-record handles global tax) — similar pattern. Tax (VAT/GST/sales tax) is where self-built billing collapses; MoR providers (Paddle, Lemon Squeezy) earn their cut here.</p>
'''

ANSWERS[80] = r'''
<p><strong>Situation:</strong> responses are large (generated reports, API dumps); log files need archiving; bytes over the wire cost money and time. Compression with <code>zlib</code> shrinks text 70-90%.</p>
<p><strong>Approach:</strong> for HTTP responses, use <code>compression</code> middleware in dev or terminate compression at the reverse proxy in prod (Nginx brotli/gzip). For files/streams, <code>zlib</code> with <code>pipeline</code>. Choose algorithm: gzip (universal), Brotli (better ratio, widely supported), zstd (emerging, best speed-ratio trade-off).</p>
<pre><code>// HTTP response compression — simplest approach
import compression from "compression";
import express from "express";
const app = express();
app.use(compression({
  level: 6,                            // 1 (fast, larger) - 9 (slow, smallest)
  threshold: 1024,                     // don't compress &lt; 1 KB
  filter: (req, res) =&gt; {
    if (req.headers["x-no-compress"]) return false;
    return compression.filter(req, res);  // default: text types
  },
}));

// Compress a file — streaming, constant memory
import { createReadStream, createWriteStream } from "node:fs";
import { pipeline } from "node:stream/promises";
import { createGzip, createBrotliCompress } from "node:zlib";

await pipeline(
  createReadStream("logs.txt"),
  createGzip({ level: 6 }),
  createWriteStream("logs.txt.gz"),
);

// Brotli — ~20% better ratio than gzip for text; use for assets you pre-compress
await pipeline(
  createReadStream("app.js"),
  createBrotliCompress({ params: { [constants.BROTLI_PARAM_QUALITY]: 6 } }),
  createWriteStream("app.js.br"),
);

// Decompress in a stream pipeline
import { createGunzip } from "node:zlib";
await pipeline(
  createReadStream("input.csv.gz"),
  createGunzip(),
  csvParser,
  dbStream,
);

// Compress bytes in memory (small data only)
import { gzip, gunzip, brotliCompress } from "node:zlib";
import { promisify } from "node:util";
const gzipAsync = promisify(gzip);

const payload = Buffer.from(JSON.stringify(hugePayload));
const compressed = await gzipAsync(payload);</code></pre>
<p><strong>Production rules:</strong></p>
<ul>
  <li><strong>Terminate compression at the edge</strong> (Nginx, CloudFront, Cloudflare) — specialized code, CPU offloaded from Node. Use <code>gzip_static</code> / <code>brotli_static</code> to serve <em>pre-compressed</em> files.</li>
  <li><strong>Pre-compress at build time</strong> for static assets (<code>compression-webpack-plugin</code>). Compressing the same file on every request wastes CPU.</li>
  <li><strong>Level 6</strong> is the right default — level 9 squeezes a few % more for 10× CPU cost.</li>
  <li><strong>Brotli</strong> wins on final ratio; gzip wins on compression speed. Serve both if possible; browser picks the best via <code>Accept-Encoding</code>.</li>
  <li><strong>Don't compress tiny responses</strong> — under ~1 KB, the framing overhead outweighs the gain.</li>
  <li><strong>Don't compress already-compressed</strong> content (JPEG, PNG, MP4) — wastes CPU for zero shrinkage.</li>
  <li><strong>Always stream</strong> large files — <code>await gzipAsync(buffer)</code> for a 1 GB file is an OOM.</li>
  <li><strong>Security:</strong> avoid CRIME/BREACH — don't mix attacker-controlled data with secrets in the same compressed response.</li>
</ul>
<p><strong>Trade-offs:</strong> compression is CPU for bandwidth — usually a win at high-latency/mobile edges. For internal service-to-service calls on fast LANs, compression often isn't worth it — measure. <strong>zstd</strong> (via <code>@mongodb-js/zstd</code> or similar) is the modern choice for backend storage: faster than gzip, better ratio, growing browser support. For API responses, <strong>JSON + gzip</strong> is usually fine; if payload size truly dominates, consider <strong>Protocol Buffers</strong> or <strong>MessagePack</strong> instead of compressed JSON — binary-efficient to begin with.</p>
'''

ANSWERS[81] = r'''
<p><strong>Situation:</strong> a single user action updates several tables — place order, decrement inventory, charge wallet, write audit. Either all succeed or none do. Half-applied writes are the worst kind of bug: silent data corruption.</p>
<p><strong>Approach:</strong> wrap the unit of work in a transaction. In Postgres (<code>pg</code>/Prisma/Knex) this means <code>BEGIN</code> &rarr; do work &rarr; <code>COMMIT</code>/<code>ROLLBACK</code>. Use a single connection checked out from the pool for the whole unit &mdash; switching connections mid-transaction is a common bug. Keep transactions <em>short</em>: no HTTP calls, no waiting on user input, no long CPU work inside them. Choose isolation deliberately: the default <strong>READ COMMITTED</strong> is fine for most cases; use <strong>SERIALIZABLE</strong> for invariants like "no two bookings on the same seat" and be prepared to retry on conflict.</p>
<pre><code>// Prisma — interactive transaction
import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

async function placeOrder(userId: string, items: Item[]) {
  return prisma.$transaction(async (tx) =&gt; {
    const order = await tx.order.create({ data: { userId, status: "PENDING" } });
    for (const it of items) {
      // FOR UPDATE lock prevents oversell under concurrency
      const row = await tx.$queryRaw&lt;{ stock: number }[]&gt;`
        SELECT stock FROM product WHERE id = ${it.productId} FOR UPDATE`;
      if (row[0].stock &lt; it.qty) throw new Error("OUT_OF_STOCK");
      await tx.product.update({
        where: { id: it.productId },
        data: { stock: { decrement: it.qty } },
      });
      await tx.orderItem.create({ data: { orderId: order.id, ...it } });
    }
    await tx.order.update({ where: { id: order.id }, data: { status: "CONFIRMED" } });
    return order;
  }, { isolationLevel: "Serializable", timeout: 5000 });
}

// Raw pg — explicit control, retry on serialization failure
import { Pool } from "pg";
const pool = new Pool();

async function withTx&lt;T&gt;(fn: (c: any) =&gt; Promise&lt;T&gt;, retries = 3): Promise&lt;T&gt; {
  const client = await pool.connect();
  try {
    for (let i = 0; i &lt; retries; i++) {
      try {
        await client.query("BEGIN ISOLATION LEVEL SERIALIZABLE");
        const out = await fn(client);
        await client.query("COMMIT");
        return out;
      } catch (e: any) {
        await client.query("ROLLBACK").catch(() =&gt; {});
        if (e.code === "40001" &amp;&amp; i &lt; retries - 1) continue; // serialization failure
        throw e;
      }
    }
    throw new Error("tx retries exhausted");
  } finally {
    client.release();
  }
}
</code></pre>
<p><strong>Cross-service writes (HTTP + DB):</strong> <em>don't</em> put the HTTP call inside the DB transaction &mdash; you hold a row lock while a network request hangs. Use the <strong>outbox pattern</strong>: insert the "send email" job into an <code>outbox</code> table inside the same transaction, and a worker delivers it after commit. This turns a distributed-transaction problem into one local transaction plus at-least-once delivery.</p>
<p><strong>Trade-offs:</strong> transactions serialize work &mdash; long ones block everyone else. Never hold a transaction open across <code>await fetch()</code>, a queue push, or anything you don't fully control. Deadlocks happen; always <strong>lock rows in a consistent order</strong> (e.g., sort by primary key before updating). For across-service consistency (payment provider + your DB), use idempotency keys and reconciliation jobs &mdash; two-phase commit is not realistic. Use the DB's transaction; don't try to simulate one in application code.</p>
'''

ANSWERS[82] = r'''
<p><strong>Situation:</strong> the app needs to send SMS for 2FA codes, order alerts, or shipping updates. SMS is expensive per message, regulated (TCPA/opt-in), and providers fail &mdash; a solid integration treats it like payments, not like <code>console.log</code>.</p>
<p><strong>Approach:</strong> pick a provider (Twilio, AWS SNS, MessageBird, Vonage). Abstract it behind an interface so you can swap providers or add a secondary for failover. Push sends through a <strong>queue</strong> &mdash; never call the provider inline during an HTTP request. Store every send with status, provider message ID, and delivery callback. Respect opt-out lists (STOP keyword), rate-limit per recipient to stop runaway loops, and never log the full message body (PII).</p>
<pre><code>// Provider-agnostic interface
interface SmsProvider {
  send(to: string, body: string, opts?: { from?: string }): Promise&lt;{ id: string }&gt;;
}

class TwilioSms implements SmsProvider {
  constructor(private client: twilio.Twilio, private from: string) {}
  async send(to: string, body: string) {
    const m = await this.client.messages.create({ to, body, from: this.from,
      statusCallback: "https://api.example.com/webhooks/twilio/status" });
    return { id: m.sid };
  }
}

// Queue the send; HTTP handler returns immediately
app.post("/notify", requireAuth, async (req, res) =&gt; {
  const { userId, template, vars } = req.body;
  const user = await db.user.findUnique({ where: { id: userId } });
  if (!user?.phone || user.smsOptOut) return res.status(400).json({ error: "no SMS" });

  await smsQueue.add("send", { userId, template, vars }, {
    jobId: `sms:${userId}:${template}:${hash(vars)}`,   // idempotent
    attempts: 5,
    backoff: { type: "exponential", delay: 2000 },
  });
  res.status(202).json({ queued: true });
});

// Worker — applies rate limits, template, and persistence
new Worker("sms", async (job) =&gt; {
  const { userId, template, vars } = job.data;
  const user = await db.user.findUnique({ where: { id: userId } });
  if (!user || user.smsOptOut) return;

  // per-recipient cap: 10/hour
  const key = `sms:rate:${userId}`;
  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, 3600);
  if (count &gt; 10) throw new Error("RATE_LIMIT");  // retried or dropped

  const body = renderTemplate(template, vars);             // no PII in logs
  const { id } = await provider.send(user.phone, body);
  await db.smsLog.create({ data: { userId, providerId: id, template, status: "SENT" } });
});

// Delivery webhook — providers push final state
app.post("/webhooks/twilio/status", verifyTwilioSignature, async (req, res) =&gt; {
  await db.smsLog.update({
    where: { providerId: req.body.MessageSid },
    data: { status: req.body.MessageStatus, updatedAt: new Date() },
  });
  res.sendStatus(200);
});
</code></pre>
<p><strong>Compliance:</strong> carriers now require pre-registered sender IDs in many regions (US 10DLC, UK short codes). You must record explicit opt-in, honor STOP/UNSUBSCRIBE automatically, and include "Reply STOP to opt out" in marketing SMS. For 2FA, use a dedicated number or short code &mdash; mixing marketing and transactional on the same number gets your sender blocked.</p>
<p><strong>Trade-offs:</strong> SMS is slow (seconds), expensive (¢ per message), and unreliable across countries. For 2FA, <strong>TOTP apps</strong> or <strong>passkeys</strong> are cheaper and more secure &mdash; prefer those and fall back to SMS. For alerts, <strong>push notifications</strong> are free and richer. Keep SMS for cases where it's genuinely the best channel: low-tech users, critical delivery confirmations, account recovery. Never put the provider API key in client code &mdash; an exposed Twilio key is a direct bill-your-employer vulnerability.</p>
'''

ANSWERS[83] = r'''
<p><strong>Situation:</strong> the API exposes resources that naturally nest &mdash; <code>/users/:userId/posts/:postId/comments</code>. Done poorly, nested routes duplicate middleware, explode in depth, and force awkward URLs when clients only have the leaf ID.</p>
<p><strong>Approach:</strong> use <strong>shallow nesting</strong> (at most two levels) with Express <code>Router</code> modules and <code>mergeParams: true</code> so child routers see the parent's params. Provide <em>both</em> nested routes (for listing a parent's children) and <em>flat</em> routes (for direct access by ID). Keep auth and ownership checks in parent-specific middleware to avoid repeating them in every child handler.</p>
<pre><code>// routes/posts.ts — child router that inherits :userId
import { Router } from "express";
const router = Router({ mergeParams: true });

router.use(async (req, res, next) =&gt; {
  // ownership check — runs for every post route mounted under a user
  const post = await db.post.findFirst({
    where: { id: req.params.postId, userId: req.params.userId },
  });
  if (!post) return res.sendStatus(404);
  (req as any).post = post;
  next();
});

router.get("/:postId", (req, res) =&gt; res.json((req as any).post));
router.patch("/:postId", validate(UpdatePostDto), async (req, res) =&gt; { /* ... */ });

// comments nested under posts
import commentsRouter from "./comments.js";
router.use("/:postId/comments", commentsRouter);

export default router;

// routes/users.ts — mounts posts under users
import postsRouter from "./posts.js";
const users = Router();
users.use("/:userId/posts", postsRouter);

// app.ts — also expose a flat posts route for direct ID access
app.use("/api/users", users);                          // nested
app.use("/api/posts", flatPostsRouter);                // flat — /api/posts/:id

// routes/comments.ts — three levels deep; avoid going deeper
const comments = Router({ mergeParams: true });
comments.get("/", async (req, res) =&gt; {
  // req.params.userId and req.params.postId both available thanks to mergeParams
  const list = await db.comment.findMany({ where: { postId: req.params.postId } });
  res.json(list);
});
export default comments;
</code></pre>
<p><strong>Rules I follow:</strong></p>
<ul>
  <li><strong>Max two levels of nesting.</strong> <code>/users/:u/posts/:p/comments/:c/likes/:l</code> is a smell &mdash; collapse the tail into flat routes.</li>
  <li><strong>Use IDs clients already have.</strong> A client holding a <code>commentId</code> shouldn't need to know the post and user &mdash; offer <code>/api/comments/:id</code> too.</li>
  <li><strong>mergeParams is your friend.</strong> Without it, child routers can't read parent params.</li>
  <li><strong>Put validation of "does X belong to Y" in parent middleware,</strong> not scattered across handlers.</li>
  <li><strong>Version at the top.</strong> <code>/api/v1/...</code> &mdash; not deep inside nested paths.</li>
</ul>
<p><strong>Trade-offs:</strong> nested routes make hierarchy explicit and let you enforce ownership in one place, but they encourage clients to build URLs by stitching path segments, which couples clients to your resource tree. <strong>HATEOAS links</strong> (returning full URLs in responses) decouple this &mdash; clients follow <code>_links.comments</code> rather than constructing paths. For large APIs, framework choices matter: <strong>NestJS</strong> enforces router structure; <strong>Fastify</strong> has faster routing; plain Express works well if you stick to the two-level rule. When in doubt, flatter is better: fewer paths, less path-building in clients.</p>
'''

ANSWERS[84] = r'''
<p><strong>Situation:</strong> different parts of the app need to react to the same event &mdash; "user.signed_up" triggers a welcome email, a Slack notification, and a CRM sync. Wiring each handler into the signup function directly creates tight coupling. The <code>EventEmitter</code> pattern lets producers fire events without knowing who's listening.</p>
<p><strong>Approach:</strong> extend <code>EventEmitter</code> or use the built-in one. Emit events with a structured payload; listeners subscribe. Use it for <em>in-process</em> fan-out when you don't need persistence. Cap listeners to catch leaks. For cross-process or persistent fan-out, the emitter is <em>not</em> enough &mdash; reach for a queue (BullMQ, Kafka) instead.</p>
<pre><code>// Typed EventEmitter — compile-time safety for payloads
import { EventEmitter } from "node:events";

type Events = {
  "user.signed_up": [{ userId: string; email: string }];
  "order.placed":   [{ orderId: string; total: number }];
};

class AppBus extends EventEmitter {
  emit&lt;K extends keyof Events&gt;(event: K, ...args: Events[K]): boolean {
    return super.emit(event, ...args);
  }
  on&lt;K extends keyof Events&gt;(event: K, listener: (...args: Events[K]) =&gt; void): this {
    return super.on(event, listener);
  }
}
export const bus = new AppBus();
bus.setMaxListeners(50);   // default 10 — bump only after you think about it

// Emitter (domain code) — just fire and forget
async function signUp(input: SignupInput) {
  const user = await db.user.create({ data: input });
  bus.emit("user.signed_up", { userId: user.id, email: user.email });
  return user;
}

// Listeners — registered at boot
bus.on("user.signed_up", async ({ userId, email }) =&gt; {
  try { await emailService.sendWelcome(email); }
  catch (e) { log.error({ e, userId }, "welcome email failed"); }
});

bus.on("user.signed_up", async ({ userId }) =&gt; {
  await crmSync.enqueue(userId);
});

// once() — fires exactly one handler, auto-unsubscribes
bus.once("server.ready", () =&gt; log.info("ready to accept traffic"));

// Error events are special — an "error" event with no listener crashes the process
bus.on("error", (err) =&gt; log.error(err, "event-bus error"));

// AbortSignal — unsubscribe cleanly (Node 17+)
const ac = new AbortController();
bus.on("tick", onTick, { signal: ac.signal });
// later: ac.abort();  // listener removed
</code></pre>
<p><strong>Pitfalls:</strong></p>
<ul>
  <li><strong>Default cap of 10 listeners</strong> &mdash; exceed it and Node logs <code>MaxListenersExceededWarning</code>. Usually indicates a memory leak: you're subscribing in a hot path without unsubscribing.</li>
  <li><strong>Listeners run synchronously</strong> in registration order. A slow listener blocks the next one. If order matters, chain <code>await</code>s explicitly instead of relying on emit.</li>
  <li><strong>Unhandled <code>error</code> events crash the process</strong> &mdash; always attach at least one error listener.</li>
  <li><strong>No back-pressure, no persistence.</strong> If the process dies between <code>emit</code> and the listener running, the event is gone.</li>
  <li><strong>Async listeners' errors are swallowed</strong> unless you wrap them &mdash; a rejection inside <code>async (data) =&gt; ...</code> doesn't propagate back to the emitter.</li>
</ul>
<p><strong>Trade-offs:</strong> <code>EventEmitter</code> is perfect for <em>intra-process</em> decoupling &mdash; lifecycle hooks, cache invalidation, metrics fan-out. It's the wrong tool for anything that must survive a crash, deliver cross-process, or guarantee order: use <strong>BullMQ</strong>, <strong>Kafka</strong>, <strong>NATS</strong>, or <strong>Redis Streams</strong>. For complex domains, a typed event bus with schemas (Zod on payloads) saves hours of debugging. If you find yourself building retries, dead-letter queues, or replay on top of EventEmitter, stop &mdash; you're rebuilding a message broker, and broker-backed options are better in every way.</p>
'''

ANSWERS[85] = r'''
<p><strong>Situation:</strong> the API has grown past "I'll just read the code" &mdash; frontend, mobile, partners, and internal tools all need docs. Keeping prose docs in sync with code fails within a sprint. <strong>OpenAPI</strong> (formerly Swagger) generated from the code is the only sustainable option.</p>
<p><strong>Approach:</strong> pick one of two strategies. (1) <strong>Schema-first:</strong> write <code>openapi.yaml</code>, generate types/validators with <code>openapi-typescript</code> or <code>zodios</code>. (2) <strong>Code-first:</strong> define routes with <strong>Zod</strong> schemas and auto-generate the OpenAPI doc via <code>@asteasolutions/zod-to-openapi</code> or use a framework that does it natively (Fastify, NestJS). Serve the interactive UI from <code>/docs</code> with <code>swagger-ui-express</code> or the newer <strong>Scalar</strong> reference viewer. Treat the spec as the contract: validate requests <em>and</em> responses against it.</p>
<pre><code>// Zod + zod-to-openapi — single source of truth
import { z } from "zod";
import { extendZodWithOpenApi, OpenAPIRegistry, OpenApiGeneratorV3 }
  from "@asteasolutions/zod-to-openapi";
extendZodWithOpenApi(z);

const registry = new OpenAPIRegistry();

const User = z.object({
  id: z.string().uuid().openapi({ example: "f0e1..." }),
  email: z.string().email(),
  createdAt: z.string().datetime(),
}).openapi("User");

registry.registerPath({
  method: "get",
  path: "/users/{id}",
  summary: "Fetch a user",
  request: { params: z.object({ id: z.string().uuid() }) },
  responses: {
    200: { description: "ok", content: { "application/json": { schema: User } } },
    404: { description: "not found" },
  },
});

// Generate spec at boot
const spec = new OpenApiGeneratorV3(registry.definitions).generateDocument({
  openapi: "3.0.3",
  info: { title: "Orders API", version: "1.4.0" },
  servers: [{ url: "https://api.example.com/v1" }],
});

import swaggerUi from "swagger-ui-express";
app.get("/openapi.json", (_, res) =&gt; res.json(spec));
app.use("/docs", swaggerUi.serve, swaggerUi.setup(spec));

// Use the SAME schema in handlers — spec can't drift from code
app.get("/users/:id", async (req, res) =&gt; {
  const { id } = z.object({ id: z.string().uuid() }).parse(req.params);
  const user = await db.user.findUnique({ where: { id } });
  if (!user) return res.sendStatus(404);
  res.json(User.parse(user));      // response validation in dev catches drift
});
</code></pre>
<p><strong>Production practices:</strong></p>
<ul>
  <li><strong>Version the spec</strong> in the URL (<code>/v1</code>, <code>/v2</code>) and publish each version separately. Clients pin a version and migrate deliberately.</li>
  <li><strong>Lock docs behind auth</strong> if the API is private &mdash; <code>/docs</code> leaks schema and examples to anyone who finds it.</li>
  <li><strong>CI check:</strong> generate the spec on build, diff against committed version; fail PR if contract changes aren't reviewed.</li>
  <li><strong>Client codegen:</strong> run <code>openapi-typescript</code> (or <code>openapi-generator-cli</code> for other languages) in the client's CI so types match the live API.</li>
  <li><strong>Realistic examples</strong> matter more than exhaustive fields &mdash; consumers read examples, not schemas.</li>
</ul>
<p><strong>Trade-offs:</strong> code-first is easier to keep in sync but harder to review as a design document; schema-first enforces API design before code but creates friction when you want to iterate quickly. <strong>Swagger UI</strong> is familiar but dated &mdash; <strong>Scalar</strong>, <strong>Redoc</strong>, or <strong>Stoplight Elements</strong> are better-looking modern alternatives. For <strong>GraphQL</strong> APIs, OpenAPI doesn't apply &mdash; the SDL <em>is</em> the spec, and tools like GraphiQL/Apollo Sandbox cover this. For RPC-style internal APIs, <strong>tRPC</strong> or <strong>gRPC with buf.build</strong> beats hand-written OpenAPI. The biggest win from any of these: auto-generated typed clients that break at compile time when the API changes.</p>
'''

ANSWERS[86] = r'''
<p><strong>Situation:</strong> services depend on each other &mdash; <code>OrderService</code> needs <code>PaymentGateway</code> and <code>EmailClient</code>; handlers need services. Hardcoding <code>new PaymentGateway()</code> inside a service makes testing miserable (can't swap in a fake), makes config hard, and hides the dependency graph.</p>
<p><strong>Approach:</strong> have objects receive their dependencies as constructor arguments rather than creating them. Wire the graph once, in a <strong>composition root</strong> at app startup. Three common styles in Node: (1) <strong>manual constructor injection</strong> &mdash; simplest, no magic; (2) a light DI container like <strong>awilix</strong> or <strong>tsyringe</strong> for larger apps; (3) frameworks like <strong>NestJS</strong> that bake DI in. For most apps, manual injection plus a composition module beats adding a container.</p>
<pre><code>// services — depend only on interfaces they declare
export interface PaymentGateway { charge(amt: number): Promise&lt;{ id: string }&gt;; }
export interface EmailClient   { send(to: string, tmpl: string): Promise&lt;void&gt;; }

export class OrderService {
  constructor(
    private readonly payments: PaymentGateway,
    private readonly email: EmailClient,
    private readonly db: PrismaClient,
    private readonly log: Logger,
  ) {}

  async place(userId: string, total: number) {
    const { id } = await this.payments.charge(total);
    const order = await this.db.order.create({ data: { userId, paymentId: id, total } });
    await this.email.send(userId, "order_confirmed");
    return order;
  }
}

// composition root — the ONE place "new" is allowed
// container.ts
import { PrismaClient } from "@prisma/client";
import { StripeGateway } from "./infra/stripe.js";
import { SendgridClient } from "./infra/sendgrid.js";
import { OrderService } from "./domain/order.js";

export function buildContainer(cfg: Config) {
  const db       = new PrismaClient({ datasourceUrl: cfg.dbUrl });
  const log      = pino({ level: cfg.logLevel });
  const payments = new StripeGateway(cfg.stripeKey);
  const email    = new SendgridClient(cfg.sendgridKey);
  const orders   = new OrderService(payments, email, db, log);
  return { db, log, payments, email, orders };
}

// handlers — take what they need
// routes/orders.ts
export function ordersRouter(c: Container) {
  const router = Router();
  router.post("/", async (req, res) =&gt; {
    const order = await c.orders.place(req.user.id, req.body.total);
    res.status(201).json(order);
  });
  return router;
}

// tests — swap real deps for fakes, no mocking library needed
it("records order after successful charge", async () =&gt; {
  const payments = { charge: vi.fn().mockResolvedValue({ id: "pi_1" }) };
  const email    = { send:   vi.fn().mockResolvedValue(undefined) };
  const db       = { order: { create: vi.fn().mockResolvedValue({ id: "o_1" }) } };
  const svc = new OrderService(payments as any, email as any, db as any, silentLogger);
  await svc.place("u_1", 100);
  expect(payments.charge).toHaveBeenCalledWith(100);
});
</code></pre>
<p><strong>When a container helps:</strong> once you have 20+ services with overlapping dependencies, writing the wiring by hand becomes tedious. <code>awilix</code> uses parameter names to resolve deps; <code>tsyringe</code> uses decorators. They add a small runtime cost and some magic &mdash; worth it in large apps, not in small ones.</p>
<p><strong>Trade-offs:</strong> DI is really just "constructors take arguments" &mdash; plain TypeScript does 90% of it. Frameworks like NestJS <em>enforce</em> DI and give you scoped lifetimes (request-scoped, singleton), which shines for multi-tenant apps. Pitfalls: <strong>over-abstraction</strong> &mdash; if you have one implementation and will always have one, the interface is overhead. <strong>Circular dependencies</strong> &mdash; DI makes them visible but not fixable; refactor to a shared module. Keep handlers thin: they should call into services, not compose dozens of dependencies themselves. The biggest payoff is <em>tests</em>: clean DI lets you test business logic without spinning up Postgres, Redis, and Stripe.</p>
'''

ANSWERS[87] = r'''
<p><strong>Situation:</strong> a list endpoint returns thousands of rows &mdash; orders, events, activity. Returning them all blows memory and time. Clients need pages. The naive <code>LIMIT/OFFSET</code> breaks at scale: with a million rows, <code>OFFSET 900000</code> makes the database read and discard 900k rows per request.</p>
<p><strong>Approach:</strong> for small/medium data, offset pagination is fine &mdash; it lets clients jump to page 20. For large/infinite feeds, use <strong>keyset (cursor) pagination</strong>: the client sends the last item's sort key; the server filters <code>WHERE (created_at, id) &lt; (?, ?)</code>. Always paginate on a <strong>stable, indexed compound key</strong> (usually <code>created_at + id</code>) &mdash; sorting on <code>created_at</code> alone is non-deterministic when timestamps tie.</p>
<pre><code>// Offset — simple, good for small data
app.get("/orders", async (req, res) =&gt; {
  const page  = Math.max(1, +req.query.page || 1);
  const size  = Math.min(100, +req.query.size || 20);
  const [rows, total] = await Promise.all([
    db.order.findMany({ orderBy: { createdAt: "desc" }, skip: (page-1)*size, take: size }),
    db.order.count(),
  ]);
  res.json({ data: rows, page, size, total, totalPages: Math.ceil(total / size) });
});

// Keyset — fast at any depth, perfect for infinite scroll
app.get("/feed", async (req, res) =&gt; {
  const size   = Math.min(100, +req.query.size || 20);
  const cursor = req.query.cursor as string | undefined;
  // decode cursor: "createdAt|id" base64
  const after = cursor ? decodeCursor(cursor) : null;

  const rows = await db.$queryRaw`
    SELECT id, title, created_at FROM post
    WHERE (${after?.createdAt}::timestamptz IS NULL)
       OR (created_at, id) &lt; (${after?.createdAt}::timestamptz, ${after?.id}::uuid)
    ORDER BY created_at DESC, id DESC
    LIMIT ${size + 1}`;
  // request size+1 to know if there's a next page
  const hasMore = rows.length &gt; size;
  const page    = rows.slice(0, size);
  const last    = page[page.length - 1];
  res.json({
    data: page,
    nextCursor: hasMore ? encodeCursor(last.created_at, last.id) : null,
  });
});

// Index that makes this fast — required
// CREATE INDEX idx_post_created_id ON post (created_at DESC, id DESC);

// Count for UI — expensive on huge tables. Cache or estimate
async function approximateCount(table: string) {
  const [row] = await db.$queryRaw&lt;{ estimate: number }[]&gt;`
    SELECT reltuples::bigint AS estimate FROM pg_class WHERE relname = ${table}`;
  return Number(row.estimate);
}
</code></pre>
<p><strong>Pagination contract:</strong></p>
<ul>
  <li>Return <code>{ data, nextCursor }</code> for keyset; <code>{ data, page, total }</code> for offset. Be consistent across the API.</li>
  <li><strong>Never trust client-supplied limits unclamped</strong> &mdash; always <code>min(requested, hardMax)</code>. A missing clamp is a DoS.</li>
  <li><strong>Stable ordering.</strong> If the sort column ties, include the primary key as a tie-breaker; otherwise pages repeat or skip rows.</li>
  <li><strong>Don't include total counts</strong> on infinite feeds &mdash; counting a billion rows costs more than the page itself. Use approximate counts or drop the count entirely.</li>
  <li><strong>Opaque cursors:</strong> encode base64 so clients treat them as opaque tokens, not parsable values you can't evolve.</li>
</ul>
<p><strong>Trade-offs:</strong> offset is intuitive and supports jumping but degrades linearly with depth and is unstable under concurrent inserts (rows shift between pages). Keyset is fast forever and stable under writes but only supports sequential navigation &mdash; no "go to page 47." For search results, <strong>Elasticsearch's <code>search_after</code></strong> is the same idea. For admin dashboards where users need to jump, offset with a small hard cap (<code>OFFSET &lt; 10000</code>) is fine. For feeds/timelines, always keyset. The real cost isn't Node; it's the database &mdash; always back pagination with the right composite index.</p>
'''

ANSWERS[88] = r'''
<p><strong>Situation:</strong> the app needs to run a command-line tool &mdash; <code>ffmpeg</code> for transcoding, <code>pandoc</code> for conversion, a Python ML script. Shelling out from Node needs care: the wrong API risks OOM, command injection, or zombie processes.</p>
<p><strong>Approach:</strong> always use <code>spawn</code> with an <strong>array of arguments</strong>, never <code>exec</code> with a shell string built from user input. <code>spawn</code> streams stdout/stderr (memory-constant); <code>exec</code> buffers the full output (OOM on large outputs). Set timeouts. Kill children on parent shutdown. Capture the exit code and stderr properly &mdash; a zero exit code is the only signal of success.</p>
<pre><code>import { spawn } from "node:child_process";
import { once } from "node:events";

// SAFE: arg array — shell not involved, no injection even if args contain spaces/quotes
async function runFfmpeg(input: string, output: string, signal?: AbortSignal) {
  const child = spawn("ffmpeg", [
    "-i", input, "-vf", "scale=1280:-2", "-c:v", "libx264", "-crf", "23", output,
  ], { stdio: ["ignore", "pipe", "pipe"], signal });

  let stderr = "";
  child.stderr.on("data", (c) =&gt; { stderr += c.toString(); });

  const [code] = await once(child, "close") as [number | null, NodeJS.Signals | null];
  if (code !== 0) throw new Error(`ffmpeg exit ${code}: ${stderr.slice(-500)}`);
}

// Stream output instead of buffering — constant memory for GB outputs
import { createWriteStream } from "node:fs";
function streamTo(file: string, child: ReturnType&lt;typeof spawn&gt;) {
  child.stdout.pipe(createWriteStream(file));
}

// Timeout + graceful shutdown
async function runWithTimeout(cmd: string, args: string[], ms: number) {
  const ac = new AbortController();
  const timer = setTimeout(() =&gt; ac.abort(), ms);
  try {
    const child = spawn(cmd, args, { signal: ac.signal });
    const [code] = await once(child, "close");
    if (code !== 0) throw new Error(`exit ${code}`);
  } finally {
    clearTimeout(timer);
  }
}

// Feed stdin — e.g., pipe data into imagemagick
const convert = spawn("convert", ["-", "-resize", "800x", "jpg:-"]);
convert.stdin.end(inputBuffer);
for await (const chunk of convert.stdout) out.push(chunk);

// NEVER do this with user input
// exec(`grep ${userInput} log.txt`)  // classic RCE — user sends "; rm -rf /"
// spawn("grep", [userInput, "log.txt"]) is safe no matter what userInput contains.

// Cleanup on server shutdown
const children = new Set&lt;ReturnType&lt;typeof spawn&gt;&gt;();
process.on("SIGTERM", () =&gt; { for (const c of children) c.kill("SIGTERM"); });
</code></pre>
<p><strong>When NOT to shell out:</strong></p>
<ul>
  <li><strong>Anything user input touches as a command or arg list.</strong> If you absolutely must accept input, <strong>whitelist</strong> (only allowed values) &mdash; never escape.</li>
  <li><strong>Long-running or heavy jobs in-process.</strong> A 30-second ffmpeg blocks a container handling other requests &mdash; push the job to a <strong>worker pool</strong> (BullMQ + dedicated workers) so web nodes stay responsive.</li>
  <li><strong>When a native library exists.</strong> <code>sharp</code> for images, <code>fluent-ffmpeg</code> for video, <code>pdf-lib</code> for PDFs &mdash; usually faster and safer than shelling.</li>
</ul>
<p><strong>Trade-offs:</strong> <code>child_process</code> gives you the entire UNIX toolbelt, but each spawn has real cost (fork, exec, signals). For CPU work that doesn't need an external binary, <strong><code>worker_threads</code></strong> are lighter (shared memory, no serialization of stdio). For sandboxing untrusted user-supplied code, use <strong>Docker</strong>, <strong>gVisor</strong>, or a dedicated <strong>Firecracker</strong>/<strong>nsjail</strong> runner &mdash; spawn alone isn't a security boundary. Biggest sources of bugs: forgetting to drain stderr (child fills its pipe buffer and blocks), not setting a timeout, and building shell strings from user input. Use array args, set timeouts, stream &mdash; and reach for a native library first.</p>
'''

ANSWERS[89] = r'''
<p><strong>Situation:</strong> a ride-share or delivery app shows drivers moving on a map in real time. Phones emit GPS updates every few seconds; dispatchers, customers, and backend services need the current position. The naive "poll every second" pattern wastes bandwidth and battery &mdash; WebSockets (or a managed equivalent) are the right tool.</p>
<p><strong>Approach:</strong> use <strong>Socket.IO</strong> or raw <code>ws</code>. Driver clients push positions on a socket; the server writes the latest position to Redis (hot state) and occasionally persists a breadcrumb to Postgres/PostGIS for replay. Consumers join <strong>rooms</strong> scoped to a delivery or area. Rate-limit the upload side &mdash; one update per 3-5 seconds is plenty &mdash; and batch downstream broadcasts.</p>
<pre><code>// server — one Socket.IO node, Redis adapter for horizontal scale
import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
import { createClient } from "redis";

const pub = createClient({ url: process.env.REDIS_URL });
const sub = pub.duplicate();
await Promise.all([pub.connect(), sub.connect()]);
const io = new Server(httpServer, { cors: { origin: [/\.example\.com$/] } });
io.adapter(createAdapter(pub, sub));

// authenticate on handshake — reject anonymous sockets
io.use(async (socket, next) =&gt; {
  try { socket.data.user = await verifyJwt(socket.handshake.auth.token); next(); }
  catch { next(new Error("unauthorized")); }
});

// driver namespace
const driversNs = io.of("/drivers");
driversNs.on("connection", (socket) =&gt; {
  const driverId = socket.data.user.sub;

  // rate-limit incoming updates — max 1 per 2s per driver
  let last = 0;
  socket.on("position", async (p: { lat: number; lng: number; ts: number }) =&gt; {
    if (Date.now() - last &lt; 2000) return;
    last = Date.now();

    // validate — reject absurd jumps (&gt; 200 km/h)
    if (!isPlausible(driverId, p)) return;

    // hot state — Redis
    await pub.hSet(`driver:${driverId}`, { lat: p.lat, lng: p.lng, ts: p.ts });
    await pub.expire(`driver:${driverId}`, 60);

    // persistent breadcrumb — async, not on the hot path
    trailQueue.add("trail", { driverId, ...p });

    // fan out to the delivery's room — customer + dispatcher receive
    const deliveryId = await pub.get(`driver:delivery:${driverId}`);
    if (deliveryId) io.to(`delivery:${deliveryId}`).emit("driver_pos", { driverId, ...p });
  });
});

// customer joins the delivery room to watch
io.of("/track").on("connection", async (socket) =&gt; {
  const { deliveryId } = socket.handshake.query;
  if (!(await canViewDelivery(socket.data.user.sub, deliveryId))) return socket.disconnect();
  socket.join(`delivery:${deliveryId}`);
  // send last-known immediately so the UI renders without waiting for the next tick
  const driverId = await pub.get(`delivery:driver:${deliveryId}`);
  const pos = driverId ? await pub.hGetAll(`driver:${driverId}`) : null;
  if (pos) socket.emit("driver_pos", pos);
});
</code></pre>
<p><strong>Client (React Native / web) considerations:</strong></p>
<ul>
  <li><strong>Background mode:</strong> iOS/Android throttle JS when the app is backgrounded; use native geolocation plugins that run in a foreground service on Android and rely on significant-change updates on iOS.</li>
  <li><strong>Reconnect &amp; resume:</strong> Socket.IO auto-reconnects; on reconnect the client should request the latest position rather than assume what it has is current.</li>
  <li><strong>Battery:</strong> update frequency is a knob &mdash; every 3 s when in active delivery, every 30 s on standby.</li>
</ul>
<p><strong>Trade-offs:</strong> self-hosted WebSockets give you full control but you own connection management, sticky sessions, and scale-out (Redis adapter, L4 load balancer with WebSocket support). <strong>Pusher</strong>, <strong>Ably</strong>, and <strong>AWS API Gateway WebSocket APIs</strong> remove that pain at per-message cost. For <em>city-wide</em> real-time maps (Uber-scale), use <strong>H3/geohashes</strong> to index drivers by area and broadcast only to rooms covering the viewer's viewport &mdash; broadcasting all drivers to everyone doesn't scale. For <strong>end-to-end reliability</strong> (customer sees the driver move even after a server restart), keep the latest position in Redis with a TTL and re-emit on reconnect. Never put heavy business logic on the WebSocket path &mdash; WebSocket handlers should be thin and offload slow work to queues.</p>
'''

ANSWERS[90] = r'''
<p><strong>Situation:</strong> "profile" mixes concerns: email/password (auth), name/avatar/bio (display), addresses (commerce), preferences (product), privacy (compliance). A single <code>PATCH /me</code> that takes "any field" ends in subtle bugs &mdash; someone changing their display name accidentally hits email-verification logic.</p>
<p><strong>Approach:</strong> split the profile into <em>capability-based</em> endpoints, each with its own validation, auth rules, and side effects. Version the user's core record; keep auxiliary data (avatars, addresses) as related rows. Treat <strong>email</strong> and <strong>password</strong> changes as security-sensitive: re-authenticate, email both old and new addresses, invalidate sessions. Store avatars in object storage, not the DB.</p>
<pre><code>// Zod DTOs — one per operation, narrow fields, no "anything goes"
const UpdateDisplayDto = z.object({
  name: z.string().min(1).max(80),
  bio:  z.string().max(500).optional(),
  locale: z.enum(["en","es","fr","de"]).optional(),
});
const UpdatePreferencesDto = z.object({
  notifications: z.object({ email: z.boolean(), sms: z.boolean() }),
  marketingOptIn: z.boolean(),
});
const ChangeEmailDto    = z.object({ newEmail: z.string().email(), currentPassword: z.string() });
const ChangePasswordDto = z.object({ currentPassword: z.string(), newPassword: z.string().min(12) });

// Basic profile
app.patch("/me", requireAuth, validate(UpdateDisplayDto), async (req, res) =&gt; {
  const u = await db.user.update({ where: { id: req.user.id }, data: req.body });
  res.json(sanitize(u));                 // never leak password hash or internal flags
});

// Preferences — safe to change, no re-auth needed
app.put("/me/preferences", requireAuth, validate(UpdatePreferencesDto), async (req, res) =&gt; {
  await db.userPreferences.upsert({
    where: { userId: req.user.id },
    update: req.body,
    create: { userId: req.user.id, ...req.body },
  });
  res.sendStatus(204);
});

// Email change — requires password, verification of the NEW address
app.post("/me/change-email", requireAuth, validate(ChangeEmailDto), async (req, res) =&gt; {
  const user = await db.user.findUniqueOrThrow({ where: { id: req.user.id } });
  if (!(await bcrypt.compare(req.body.currentPassword, user.passwordHash)))
    return res.status(401).json({ error: "bad password" });
  const token = await createEmailChangeToken(user.id, req.body.newEmail);
  await email.send(req.body.newEmail, "verify_email_change", { token });
  await email.send(user.email,       "email_change_requested", { when: new Date() });
  res.status(202).json({ status: "verification_sent" });
});

// Avatar — multipart, stored in S3
app.post("/me/avatar", requireAuth, upload.single("file"), async (req, res) =&gt; {
  const key = `avatars/${req.user.id}/${crypto.randomUUID()}.jpg`;
  const buf = await sharp(req.file.buffer).resize(512, 512).jpeg({ quality: 85 }).toBuffer();
  await s3.putObject({ Bucket: B, Key: key, Body: buf, ContentType: "image/jpeg" });
  const url = `${CDN}/${key}`;
  await db.user.update({ where: { id: req.user.id }, data: { avatarUrl: url } });
  // delete old avatar afterwards via a queued job
  res.json({ url });
});

// GDPR: export + delete
app.get("/me/export",    requireAuth, async (req, res) =&gt; exportUserData(req.user.id, res));
app.delete("/me",        requireAuth, async (req, res) =&gt; scheduleAccountDeletion(req.user.id));
</code></pre>
<p><strong>Compliance &amp; security:</strong></p>
<ul>
  <li><strong>Sensitive changes (email, password, 2FA)</strong> should invalidate all sessions except the current one &mdash; redis <code>DEL user:sessions:*</code>.</li>
  <li><strong>Audit log</strong> every change with actor, old value (hashed where sensitive), new value, IP.</li>
  <li><strong>GDPR/CCPA</strong> require <em>export</em> and <em>delete</em>. Deletion should be <em>soft</em> initially (30-day grace, then hard delete via a scheduled job) and anonymize in immutable logs rather than delete rows you can't.</li>
  <li><strong>Never expose internal flags</strong> (<code>isStaff</code>, <code>planInternal</code>, <code>passwordHash</code>) in the profile response. Use an allowlist serializer.</li>
</ul>
<p><strong>Trade-offs:</strong> a single "update me" endpoint feels simple but conflates concerns &mdash; capability-based endpoints give per-field auth, per-field validation, and meaningful audit logs. The extra routes are a small price. For <strong>admin dashboards</strong> that need to edit other users, keep those on separate endpoints with their own permissions &mdash; never reuse <code>/me</code> with an "as user" query param. Biggest failure modes: not re-authenticating on email/password changes, accidentally exposing password hashes in <code>/me</code>, and leaking social-security-style fields to partners via over-eager JSON. The fix is always the same: narrow DTOs in, narrow DTOs out.</p>
'''

ANSWERS[91] = r'''
<p><strong>Situation:</strong> the app needs configuration that differs by environment &mdash; DB URL, API keys, feature flags, log level. Committing these to source is a leak waiting to happen; hardcoding them makes dev/staging/prod diverge. The standard solution is environment variables loaded from <code>.env</code> files in development, and from the platform (Kubernetes secrets, AWS Secrets Manager) in production.</p>
<p><strong>Approach:</strong> use <code>dotenv</code> (or the built-in <code>--env-file</code> flag in Node 20.6+) to load <code>.env</code> locally. Never load it in production &mdash; the platform injects env vars directly. Validate the resulting object at boot with Zod so the process crashes on startup if a required var is missing, not in production under load. Commit <code>.env.example</code> but <em>never</em> <code>.env</code> itself.</p>
<pre><code>// .gitignore
// .env
// .env.local
// .env.*.local

// .env.example — committed template with placeholder values
// DATABASE_URL=postgres://user:pass@localhost:5432/app
// REDIS_URL=redis://localhost:6379
// JWT_SECRET=change-me
// NODE_ENV=development

// config.ts — load, validate, freeze
import "dotenv/config";                 // or: node --env-file=.env server.js
import { z } from "zod";

const Env = z.object({
  NODE_ENV:       z.enum(["development", "test", "staging", "production"]),
  PORT:           z.coerce.number().default(3000),
  DATABASE_URL:   z.string().url(),
  REDIS_URL:      z.string().url(),
  JWT_SECRET:     z.string().min(32),
  LOG_LEVEL:      z.enum(["debug","info","warn","error"]).default("info"),
  STRIPE_KEY:     z.string().startsWith("sk_"),
  FEATURE_X:      z.coerce.boolean().default(false),
});

const parsed = Env.safeParse(process.env);
if (!parsed.success) {
  console.error("invalid env:", parsed.error.flatten().fieldErrors);
  process.exit(1);                     // fail fast, don't start with bad config
}
export const env = Object.freeze(parsed.data);

// use typed config everywhere — never read process.env outside this module
import { env } from "./config.js";
const redis = createClient({ url: env.REDIS_URL });
</code></pre>
<p><strong>Production rules:</strong></p>
<ul>
  <li><strong>Don't ship <code>.env</code> to production.</strong> Use Kubernetes <code>Secret</code>, AWS Parameter Store / Secrets Manager, or your platform's secret store (Vercel, Fly.io, Render all inject env vars).</li>
  <li><strong>Keep secrets out of error messages and logs.</strong> A common bug: logging <code>env</code> on boot. Redact.</li>
  <li><strong>Rotate regularly.</strong> A JWT secret that has never rotated is a JWT secret you can't revoke.</li>
  <li><strong>One source of truth per variable.</strong> Don't read the same value from <code>DATABASE_URL</code> and <code>DB_URL</code> &mdash; pick one.</li>
  <li><strong>Cast and validate.</strong> Env vars are always strings; <code>PORT=3000</code> is <code>"3000"</code> &mdash; coerce with Zod or parse manually.</li>
</ul>
<p><strong>Variants:</strong> <code>dotenv-expand</code> supports variable interpolation; <code>dotenv-vault</code> provides encrypted shared <code>.env</code>; <code>dotenvx</code> adds encryption at rest. <strong>Doppler</strong> and <strong>Infisical</strong> are team-oriented secret managers that sync to your process. For monorepos, keep one <code>.env</code> per app to avoid "who owns this var?" confusion.</p>
<p><strong>Trade-offs:</strong> <code>.env</code> files are convenient for local dev and terrible for anything shared &mdash; they drift, leak in Slack paste, and bypass access control. Teams should adopt a secrets manager early. For <strong>client-side config</strong> (React/Vite), only variables prefixed with <code>VITE_</code> or <code>NEXT_PUBLIC_</code> end up in the bundle &mdash; <em>never</em> put a secret in one of those. The Node-side pattern is straightforward: load, validate, freeze, import a typed object &mdash; and never sprinkle <code>process.env.FOO</code> through business code.</p>
'''

ANSWERS[92] = r'''
<p><strong>Situation:</strong> in production you need to answer questions like "what did customer X see at 02:17?" and "why did this endpoint return 500?" without asking the user. That means capturing request metadata (method, path, status, duration, user id), and selectively bodies &mdash; while aggressively redacting PII, secrets, and auth tokens.</p>
<p><strong>Approach:</strong> use <strong>pino</strong> (fast, JSON) or <strong>winston</strong> as the logger. Attach a <code>requestId</code> via <code>AsyncLocalStorage</code> so every log line in a request carries it. Log at two layers: an access log (every request, always) and application logs (whatever the code emits). <strong>Never log full bodies by default</strong> &mdash; bodies often contain passwords, tokens, credit cards. Opt-in to body logging per route, with redaction lists.</p>
<pre><code>import pino from "pino";
import pinoHttp from "pino-http";
import { AsyncLocalStorage } from "node:async_hooks";
import crypto from "node:crypto";

export const log = pino({
  level: process.env.LOG_LEVEL ?? "info",
  // pino redact uses fast JSON paths — this runs on every log call
  redact: {
    paths: [
      "req.headers.authorization",
      "req.headers.cookie",
      "req.body.password",
      "req.body.token",
      "req.body.creditCard",
      "res.headers['set-cookie']",
      "*.ssn", "*.dob",
    ],
    censor: "[REDACTED]",
  },
  // don't ship debug formatting to prod — use pino-pretty only in dev
});

// request-scoped context so downstream logs carry requestId without plumbing
const als = new AsyncLocalStorage&lt;{ requestId: string; userId?: string }&gt;();
export function getRequestId() { return als.getStore()?.requestId; }

// middleware — assigns a requestId and runs the rest of the request inside it
app.use((req, res, next) =&gt; {
  const requestId = (req.headers["x-request-id"] as string) ?? crypto.randomUUID();
  res.setHeader("x-request-id", requestId);
  als.run({ requestId }, () =&gt; next());
});

// pino-http — structured access log per request
app.use(pinoHttp({
  logger: log,
  genReqId: (req) =&gt; req.headers["x-request-id"] ?? crypto.randomUUID(),
  serializers: {
    req: (req) =&gt; ({ method: req.method, url: req.url, id: req.id }),
    res: (res) =&gt; ({ status: res.statusCode }),
  },
  customLogLevel: (req, res, err) =&gt;
    err || res.statusCode &gt;= 500 ? "error" :
    res.statusCode &gt;= 400        ? "warn"  : "info",
}));

// opt-in body logging for a debug route — with size cap and redaction
app.post("/debug/webhook", captureBody({ maxKb: 32 }), (req, res) =&gt; {
  log.info({ body: redact(req.body, ["token","password"]) }, "webhook received");
  res.sendStatus(200);
});

// Example child logger carrying context through business code
async function chargeCustomer(userId: string, amount: number) {
  const ctx = log.child({ userId, amount, requestId: getRequestId() });
  ctx.info("charge start");
  try { /* ... */ ctx.info("charge ok"); }
  catch (e) { ctx.error({ err: e }, "charge failed"); throw e; }
}
</code></pre>
<p><strong>What to log (and what not to):</strong></p>
<ul>
  <li><strong>Log:</strong> method, path, status, duration, requestId, userId, IP, user agent, route pattern (not the raw URL for unbounded-cardinality metrics).</li>
  <li><strong>Never log:</strong> passwords, raw tokens, full card numbers, full SSN/PII, Authorization headers, cookies. Redact at the logger layer so no code path can slip through.</li>
  <li><strong>Sample high-volume endpoints</strong> &mdash; 100% of 400s/500s, 1% of 200s is often enough.</li>
  <li><strong>Correlate across services</strong> via <strong>W3C Trace Context</strong> (<code>traceparent</code> header), not your own IDs. OpenTelemetry auto-propagates it.</li>
</ul>
<p><strong>Trade-offs:</strong> logging is cheap per line but expensive at volume &mdash; observability bills climb fast. Tier your storage: structured JSON to stdout &rarr; shipped by Vector/Fluent Bit &rarr; hot index (Loki, Elastic, Datadog) for 7-14 days, cold S3 for compliance. For <strong>full request/response capture</strong> use a <strong>tracing</strong> tool (OpenTelemetry + Tempo/Honeycomb/Lightstep) not logs &mdash; traces are denormalized for this exact need. The unforgivable sin is logging secrets; guard the logger with redaction lists <em>and</em> review them in CI.</p>
'''

ANSWERS[93] = r'''
<p><strong>Situation:</strong> the API must be served over HTTPS &mdash; not just "the frontend uses it over HTTPS," but every request, including direct backend calls, internal-to-internal, and webhooks. Plain HTTP anywhere leaks tokens, lets attackers MITM, and fails modern browser requirements (mixed content blocks, SameSite cookies).</p>
<p><strong>Approach:</strong> do not terminate TLS in Node in production &mdash; put a reverse proxy (<strong>Nginx</strong>, <strong>Caddy</strong>, <strong>Traefik</strong>, ALB/CloudFront) in front. It handles certificate renewal (Let's Encrypt), OCSP stapling, HTTP/2, and keeps TLS config in one vetted place. Node still needs to <em>enforce</em> HTTPS: trust the proxy's <code>X-Forwarded-Proto</code>, redirect plain HTTP, set HSTS, secure cookies, and reject non-TLS webhook sources.</p>
<pre><code>// Express — behind a proxy (the common, recommended setup)
import express from "express";
import helmet from "helmet";

const app = express();
app.set("trust proxy", 1);        // trust the first proxy's X-Forwarded-* headers

// Helmet sets sensible security headers, including HSTS
app.use(helmet({
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  contentSecurityPolicy: false,   // set CSP at the edge or here, deliberately
}));

// Redirect plain HTTP to HTTPS (the proxy usually does this; belt-and-braces)
app.use((req, res, next) =&gt; {
  if (req.secure || req.headers["x-forwarded-proto"] === "https") return next();
  res.redirect(301, "https://" + req.headers.host + req.url);
});

// Secure session cookies — only sent over HTTPS, not accessible to JS
app.use(session({
  secret: env.SESSION_SECRET,
  cookie: {
    secure: true,              // HTTPS-only
    httpOnly: true,            // no JS access
    sameSite: "lax",           // or "strict" for extra safety
    maxAge: 7 * 24 * 3600 * 1000,
  },
}));

// --- Direct TLS in Node (only if you can't use a proxy) ---
import { readFileSync } from "node:fs";
import https from "node:https";
import http from "node:http";

const server = https.createServer({
  key:  readFileSync("/etc/ssl/private/server.key"),
  cert: readFileSync("/etc/ssl/certs/server.crt"),
  ca:   readFileSync("/etc/ssl/certs/chain.pem"),
  // enforce strong TLS
  minVersion: "TLSv1.2",
  honorCipherOrder: true,
}, app).listen(443);

// Plain-HTTP listener that only redirects
http.createServer((req, res) =&gt; {
  res.writeHead(301, { Location: `https://${req.headers.host}${req.url}` });
  res.end();
}).listen(80);

// Outbound calls — verify peer certs (the default, but explicit is good)
import { Agent } from "node:https";
const agent = new Agent({ rejectUnauthorized: true });
fetch("https://api.partner.com/endpoint", { agent });

// mTLS — enforce client certs for service-to-service traffic
const mtlsServer = https.createServer({
  key, cert, ca,
  requestCert: true,
  rejectUnauthorized: true,    // reject if no/invalid client cert
}, app);
</code></pre>
<p><strong>Production must-haves:</strong></p>
<ul>
  <li><strong>Automated certificate renewal</strong> &mdash; Let's Encrypt via <code>certbot</code>, Caddy's automatic TLS, or ACM on AWS. Expired certs are the #1 outage.</li>
  <li><strong>HSTS with <code>preload</code></strong> so browsers refuse HTTP even on first visit (after registering on hstspreload.org).</li>
  <li><strong>Disable TLS 1.0/1.1</strong> at the proxy; TLS 1.3 preferred.</li>
  <li><strong>Never disable <code>rejectUnauthorized</code></strong> in outbound clients &mdash; it's the "off switch" for peer-cert validation and turns HTTPS into theater.</li>
  <li><strong>Secure cookies</strong> (<code>Secure</code>, <code>HttpOnly</code>, <code>SameSite</code>) are as important as TLS itself.</li>
  <li><strong>Webhook security:</strong> verify provider signatures (Stripe, GitHub) &mdash; HTTPS alone doesn't prove the caller is genuine.</li>
</ul>
<p><strong>Trade-offs:</strong> terminating TLS at the edge (CloudFront, Cloudflare, ALB) is easier, faster, and keeps Node out of certificate management. Downsides: the traffic is <em>re-encrypted or unencrypted</em> between edge and origin &mdash; for high-security workloads use <strong>mTLS</strong> or <strong>private VPC networking</strong>. mTLS internally stops rogue processes inside your cluster from calling services. For <strong>serverless / managed platforms</strong> (Lambda behind API Gateway, Vercel, Fly.io), TLS is transparent &mdash; your job is still to enforce secure cookies, HSTS, and peer-cert validation in outbound calls. Biggest misconception: installing a cert isn't a one-time task &mdash; automate renewal on day one.</p>
'''

ANSWERS[94] = r'''
<p><strong>Situation:</strong> a single Node process runs on one CPU core. On an 8-core box that's 12.5% CPU utilization at best. The <code>cluster</code> module forks N worker processes that share the listening port &mdash; requests are distributed across them. This has been the standard Node scaling pattern for a decade.</p>
<p><strong>Approach:</strong> for most modern apps, <em>don't</em> run cluster yourself &mdash; run <strong>one Node process per container</strong> and let your orchestrator (Kubernetes, ECS, Fly.io) scale horizontally. Containers give better isolation and cleaner restarts. Use <code>cluster</code> when you're on bare VMs, can't use containers, or want per-box parallelism without an orchestrator. The PM2 process manager wraps this nicely.</p>
<pre><code>// Using cluster directly
import cluster from "node:cluster";
import os from "node:os";
import process from "node:process";

if (cluster.isPrimary) {
  const workers = +process.env.WEB_CONCURRENCY || os.availableParallelism();
  console.log(`primary ${process.pid}: forking ${workers} workers`);

  for (let i = 0; i &lt; workers; i++) cluster.fork();

  // automatic restart on crash — but guard against crash loops
  const deaths = new Map&lt;number, number[]&gt;();
  cluster.on("exit", (worker, code, signal) =&gt; {
    console.warn(`worker ${worker.process.pid} died (${signal || code})`);
    const times = (deaths.get(worker.id) ?? []).concat(Date.now())
      .filter(t =&gt; Date.now() - t &lt; 60_000);
    deaths.set(worker.id, times);
    if (times.length &gt; 5) {
      console.error("crash-looping; not restarting");
      return;
    }
    cluster.fork();
  });

  // graceful shutdown — drain workers, don't SIGKILL
  process.on("SIGTERM", () =&gt; {
    for (const id in cluster.workers) cluster.workers[id]?.send("shutdown");
    setTimeout(() =&gt; process.exit(0), 30_000).unref();
  });
} else {
  // worker code — a normal Express app
  const app = await buildApp();
  const server = app.listen(process.env.PORT || 3000);
  process.on("message", (msg) =&gt; {
    if (msg === "shutdown") server.close(() =&gt; process.exit(0));
  });
}

// PM2 equivalent — no bespoke cluster code
// pm2 start server.js -i max --name api
// Handles forking, logging, restarts, zero-downtime reload (pm2 reload)
</code></pre>
<p><strong>Gotchas:</strong></p>
<ul>
  <li><strong>In-memory state isn't shared.</strong> Sessions, rate-limit counters, pub/sub &mdash; all must live in Redis. A rate limit counting in per-worker memory lets an attacker send N&times; more requests.</li>
  <li><strong>Sticky sessions</strong> matter for WebSockets &mdash; a client must land on the same worker. With the cluster module on a single box, the built-in round-robin breaks sticky; use the <strong>Redis adapter</strong> instead, or stick at the load balancer.</li>
  <li><strong>Worker memory leaks</strong> are masked by restarts &mdash; add max-memory-restart (<code>--max-memory-restart 512M</code> in PM2) so a leaky worker gets recycled.</li>
  <li><strong>Startup cost scales with workers.</strong> If boot takes 3 s, 16 workers take 3 s to all be ready. On the same box this also blows DB connection pool limits &mdash; configure pool size <em>per worker</em>.</li>
  <li><strong>Zero-downtime reload</strong> needs care: <code>pm2 reload</code> does it; raw cluster requires orchestrating the fork/kill sequence yourself.</li>
</ul>
<p><strong>Trade-offs:</strong> cluster utilizes all cores on one box, which matters for CPU-bound Node (JSON serialization, template rendering, compression). For I/O-bound workloads (most web APIs), the gain is smaller than you'd guess because the event loop spends most time idle. For heavy in-process CPU, <strong><code>worker_threads</code></strong> are a better fit &mdash; they share memory, avoid process fork overhead, and don't need a load balancer. The modern pattern is <strong>Docker + Kubernetes HPA</strong>: one Node per container, scale replicas by CPU/memory/queue depth. Cluster still has a niche &mdash; bare-metal deploys, simple VM hosting, fast per-box scale-up &mdash; but for new services, horizontal scaling wins on operational simplicity.</p>
'''

ANSWERS[95] = r'''
<p><strong>Situation:</strong> the app depends on a third-party API &mdash; currency rates, weather, shipping, enrichment. Their latency, downtime, and rate limits become yours unless you build guardrails. A naive <code>fetch()</code> with no timeout, retries, or caching is a production outage waiting for their next blip.</p>
<p><strong>Approach:</strong> wrap every external call in a layer that enforces <strong>timeout</strong>, <strong>retry with jittered backoff</strong>, <strong>circuit breaker</strong>, <strong>cache</strong>, and <strong>observability</strong>. For heavy integrations, put the call behind a queue so your web handler isn't blocked. Respect their rate limits using a token-bucket on your side; honor their <code>Retry-After</code> header on 429s. Cache responses per their <code>Cache-Control</code> or a sensible TTL &mdash; many third-party APIs are the biggest cost driver in a SaaS bill.</p>
<pre><code>import { fetch, Agent, setGlobalDispatcher } from "undici";

// Keep connections alive — avoids TCP/TLS handshake per call
setGlobalDispatcher(new Agent({ keepAliveTimeout: 30_000, connections: 50 }));

// Single hardened client for the provider
class RatesClient {
  private breaker = new CircuitBreaker({ threshold: 5, cooldownMs: 30_000 });
  constructor(private base: string, private apiKey: string, private redis: Redis) {}

  async get(symbol: string) {
    const cacheKey = `rates:${symbol}`;
    const cached = await this.redis.get(cacheKey);
    if (cached) return JSON.parse(cached);

    if (!this.breaker.allow()) throw new Error("CIRCUIT_OPEN");

    const data = await retry(async (attempt) =&gt; {
      const ac = new AbortController();
      const timer = setTimeout(() =&gt; ac.abort(), 3000);
      try {
        const res = await fetch(`${this.base}/rate/${symbol}`, {
          headers: { authorization: `Bearer ${this.apiKey}`, accept: "application/json" },
          signal: ac.signal,
        });
        if (res.status === 429) {
          const wait = +(res.headers.get("retry-after") || "1") * 1000;
          throw new RetryAfter(wait);
        }
        if (res.status &gt;= 500) throw new Error(`upstream ${res.status}`);
        if (!res.ok) throw new NonRetriable(`${res.status} ${await res.text()}`);
        return res.json();
      } finally { clearTimeout(timer); }
    }, { attempts: 3, baseMs: 200 });

    this.breaker.onSuccess();
    await this.redis.setex(cacheKey, 300, JSON.stringify(data));  // 5 min TTL
    return data;
  }
}

// Jittered exponential backoff — honors RetryAfter
async function retry&lt;T&gt;(fn: (n: number) =&gt; Promise&lt;T&gt;, opts: { attempts: number; baseMs: number }) {
  for (let i = 1; i &lt;= opts.attempts; i++) {
    try { return await fn(i); }
    catch (e: any) {
      if (e instanceof NonRetriable || i === opts.attempts) throw e;
      const wait = e instanceof RetryAfter ? e.wait
                 : Math.floor(opts.baseMs * 2 ** (i-1) * (0.5 + Math.random()));
      await new Promise(r =&gt; setTimeout(r, wait));
    }
  }
  throw new Error("unreachable");
}

class CircuitBreaker {
  private failures = 0; private openUntil = 0;
  constructor(private opts: { threshold: number; cooldownMs: number }) {}
  allow()   { return Date.now() &gt;= this.openUntil; }
  onSuccess() { this.failures = 0; }
  onFailure() { if (++this.failures &gt;= this.opts.threshold) this.openUntil = Date.now() + this.opts.cooldownMs; }
}
</code></pre>
<p><strong>Integration checklist:</strong></p>
<ul>
  <li><strong>Timeout every call</strong> &mdash; default global fetch has no timeout; use <code>AbortSignal.timeout(ms)</code>.</li>
  <li><strong>Retry only idempotent operations</strong> (GET, PUT, DELETE) or when the provider supports idempotency keys (Stripe). Retrying a non-idempotent POST double-charges users.</li>
  <li><strong>Cache aggressively</strong> for read-heavy APIs &mdash; even 60 seconds of caching demolishes per-request costs.</li>
  <li><strong>Metrics per provider:</strong> request count, p50/p99 latency, error rate, cache hit rate. Alerts when upstream degrades &mdash; you want to notice before users complain.</li>
  <li><strong>Secrets in env, rotated.</strong> Never commit API keys.</li>
</ul>
<p><strong>Trade-offs:</strong> owning the resilience layer yourself is flexible but error-prone &mdash; libraries like <strong>cockatiel</strong> or <strong>opossum</strong> implement circuit breakers and retries properly. <strong>undici</strong> is the fastest fetch in Node (the built-in <code>fetch</code> uses it under the hood). For heavy workflows, route the call through a <strong>queue</strong> (BullMQ) so web handlers return immediately and the worker handles retries and backoff safely out of the hot path. The biggest long-term cost of third-party APIs is <em>lock-in</em> &mdash; model the integration as a narrow interface in your code, so you can swap providers without rewriting features.</p>
'''

ANSWERS[96] = r'''
<p><strong>Situation:</strong> code needs to parse a query string coming from a webhook URL, build one for an outbound redirect, or round-trip form-encoded data. Node's <code>querystring</code> module handles this &mdash; though the modern WHATWG <code>URL</code> and <code>URLSearchParams</code> API is the preferred choice today.</p>
<p><strong>Approach:</strong> use <code>URLSearchParams</code> for new code &mdash; it's standards-based, handles arrays and Unicode correctly, and matches what browsers do. The legacy <code>querystring</code> module is still useful for edge cases (custom separators, non-standard encodings). Never parse query strings with regex or string splits &mdash; you'll miss URL encoding, repeated keys, and arrays.</p>
<pre><code>// Modern: URLSearchParams (preferred)
const u = new URL("https://api.example.com/search?q=node+js&amp;tag=js&amp;tag=ts&amp;page=2");
u.searchParams.get("q");          // "node js"
u.searchParams.getAll("tag");     // ["js", "ts"]
u.searchParams.has("page");       // true
u.searchParams.set("page", "3");  // preserves others
u.searchParams.delete("tag");
u.toString();                     // rebuilt URL

// Building a query string safely
const params = new URLSearchParams({ user: "a b", locale: "en-GB" });
params.append("tag", "one");
params.append("tag", "two");
params.toString();                // "user=a+b&locale=en-GB&tag=one&tag=two"

// Parse a raw form-encoded body (express.urlencoded does this for you)
const body = "name=Ada&email=ada%40example.com&skills=js&skills=ts";
const parsed = Object.fromEntries(new URLSearchParams(body));
// { name: "Ada", email: "ada@example.com", skills: "ts" }  &lt;-- last value wins
// For array keys, use getAll:
new URLSearchParams(body).getAll("skills"); // ["js","ts"]

// Legacy: node:querystring — still available, occasionally needed
import qs from "node:querystring";
qs.parse("a=1&amp;b=2&amp;b=3");        // { a: "1", b: ["2","3"] } — arrays for repeated keys
qs.stringify({ a: 1, b: [2,3] }); // "a=1&b=2&b=3"
qs.parse("k=v;x=y", ";");         // custom separator
qs.parse("k%3D1=v", "&amp;", "=",   // custom decode
        { decodeURIComponent: decodeURIComponent });

// Third-party: `qs` — for deep nested objects (common in PHP/Rails-style APIs)
import qs from "qs";
qs.parse("a[b][c]=1&amp;a[b][d]=2");  // { a: { b: { c: "1", d: "2" } } }
qs.stringify({ a: { b: { c: 1 } } });
// Express by default does NOT parse deep; opt in: app.use(express.urlencoded({ extended: true }))

// Gotchas — always validate query params
app.get("/search", (req, res) =&gt; {
  const schema = z.object({
    q:   z.string().min(1).max(100),
    page: z.coerce.number().int().min(1).max(1000).default(1),
    tag:  z.union([z.string(), z.array(z.string())]).optional(),
  });
  const parsed = schema.parse(req.query);
  // now use parsed with confidence
});
</code></pre>
<p><strong>Encoding pitfalls:</strong></p>
<ul>
  <li><strong>Spaces:</strong> in query strings they encode as <code>+</code> historically and <code>%20</code> in paths. <code>URLSearchParams</code> uses <code>+</code>; both decode correctly.</li>
  <li><strong>Repeated keys:</strong> <code>?tag=a&amp;tag=b</code> &mdash; treat as arrays via <code>getAll</code>; don't rely on <code>get</code> returning the last (that's implementation-defined across languages).</li>
  <li><strong>Prototype pollution:</strong> older <code>qs</code> versions let <code>?__proto__[x]=1</code> pollute globals. Update, or use <code>URLSearchParams</code> which is immune.</li>
  <li><strong>Size limits:</strong> a 1MB query string will slow your server; cap at the proxy (<code>large_client_header_buffers</code> in Nginx).</li>
  <li><strong>Always validate</strong> with Zod/Joi &mdash; assume <code>req.query</code> is an attacker-controlled map of strings until proven otherwise.</li>
</ul>
<p><strong>Trade-offs:</strong> <code>URLSearchParams</code> is a browser-standard API that works the same on the server, which matters for full-stack TypeScript code that shares utilities. <code>querystring</code> wins when you need unusual separators or performance &mdash; it's a hair faster but rarely materially so. The <code>qs</code> library is essential if you're consuming APIs that use bracket notation (<code>filters[status]=open&amp;filters[tier]=pro</code>) but it adds complexity; Express's <code>extended: true</code> uses it under the hood. For anything you take from a client, the parsing choice matters far less than the validation you apply afterwards.</p>
'''

ANSWERS[97] = r'''
<p><strong>Situation:</strong> Google Docs-style multi-user editing where every keystroke shows up on teammates' screens within milliseconds, and concurrent edits don't clobber each other. This is a genuinely hard distributed-systems problem; a chat-style "last write wins" breaks as soon as two people type in the same paragraph.</p>
<p><strong>Approach:</strong> don't invent the conflict-resolution algorithm. Use <strong>Yjs</strong> (CRDT, widely deployed) or <strong>Automerge</strong> (CRDT, richer types) for the data layer, and wire them up to a WebSocket transport. Yjs gives you shared types (<code>Y.Text</code>, <code>Y.Array</code>, <code>Y.Map</code>) with automatic merge and awareness (who's here, what are they selecting). Your server becomes a <em>relay</em> plus a persistence layer, not the decision-maker on what the document "really says."</p>
<pre><code>// server — y-websocket relay with Redis pub/sub for multi-node
// npm i yjs y-websocket ws @y/redis
import { WebSocketServer } from "ws";
import http from "node:http";
import { setupWSConnection } from "y-websocket/bin/utils.js";
import { setPersistence } from "y-websocket/bin/utils.js";
import * as Y from "yjs";

const server = http.createServer();
const wss = new WebSocketServer({ noServer: true });

server.on("upgrade", async (req, socket, head) =&gt; {
  try {
    const user = await verifyJwt(extractToken(req));
    const docName = req.url!.slice(1);
    if (!(await canEditDoc(user.id, docName))) return socket.destroy();
    wss.handleUpgrade(req, socket, head, (ws) =&gt;
      setupWSConnection(ws, req, { docName, gc: true }));
  } catch { socket.destroy(); }
});

// persistence — snapshot to Postgres every N seconds, restore on doc load
setPersistence({
  provider: "postgres",
  bindState: async (docName, ydoc) =&gt; {
    const row = await db.ydoc.findUnique({ where: { id: docName } });
    if (row) Y.applyUpdate(ydoc, row.state);
    // save every 10 seconds if modified
    let dirty = false;
    ydoc.on("update", () =&gt; { dirty = true; });
    setInterval(async () =&gt; {
      if (!dirty) return;
      const state = Y.encodeStateAsUpdate(ydoc);
      await db.ydoc.upsert({ where: { id: docName }, update: { state }, create: { id: docName, state } });
      dirty = false;
    }, 10_000);
  },
  writeState: async (docName, ydoc) =&gt; {
    const state = Y.encodeStateAsUpdate(ydoc);
    await db.ydoc.upsert({ where: { id: docName }, update: { state }, create: { id: docName, state } });
  },
});
server.listen(1234);

// client — React + Yjs + Monaco (pseudocode)
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import { MonacoBinding } from "y-monaco";

const ydoc = new Y.Doc();
const provider = new WebsocketProvider("wss://collab.example.com", "doc-42", ydoc, {
  params: { token: authToken },
});
const yText = ydoc.getText("content");
// bind Monaco editor's model to yText — automatic two-way sync
new MonacoBinding(yText, editor.getModel(), new Set([editor]), provider.awareness);

// awareness — show other users' cursors and selections
provider.awareness.setLocalStateField("user", {
  name: currentUser.name,
  color: currentUser.color,
});
</code></pre>
<p><strong>Design considerations:</strong></p>
<ul>
  <li><strong>CRDTs converge without a central authority.</strong> This is the core win: offline edits merge when the client reconnects. Yjs's updates are tiny and commutative.</li>
  <li><strong>Persistence &ne; broadcast.</strong> Redis pub/sub handles fan-out across nodes; Postgres (or S3 snapshots) holds durable state. <code>@y/redis</code> combines both.</li>
  <li><strong>Authorization on connect</strong> is non-negotiable &mdash; anyone who can open the WebSocket can see/modify the doc. Check on upgrade before calling <code>setupWSConnection</code>.</li>
  <li><strong>Document size:</strong> CRDTs grow with every edit. Run periodic <strong>garbage collection</strong> (Yjs does automatically) and consider snapshotting + pruning history for very old docs.</li>
  <li><strong>Awareness state</strong> (cursors, selections) uses a separate ephemeral channel &mdash; no persistence, no history.</li>
</ul>
<p><strong>Trade-offs:</strong> Yjs/Automerge handle the <em>hard</em> problem (merge) and let you focus on product features. The main cost is storage: every client carries the CRDT state; for a huge doc with a decade of history, initial load gets slow &mdash; compact and snapshot. For <strong>OT (Operational Transform)</strong> implementations (ShareDB, ProseMirror's collab module), you need a central authoritative server &mdash; simpler storage, more server coordination. For <em>structured</em> collaborative data (spreadsheets, Kanban boards), CRDTs shine &mdash; Linear, Figma, Notion all use them. Don't try to hand-roll conflict resolution with timestamps and row versions; it works for a week and breaks forever once users go offline. For managed options, <strong>Liveblocks</strong>, <strong>PartyKit</strong>, and <strong>Tiptap Cloud</strong> remove the ops burden entirely.</p>
'''

ANSWERS[98] = r'''
<p><strong>Situation:</strong> users have many events that warrant a notification &mdash; mentions, order updates, approvals, security alerts. The system needs multi-channel delivery (in-app, push, email, SMS), per-user preferences, digests (don't bombard users), and a record of what was sent so nothing is lost on reconnect.</p>
<p><strong>Approach:</strong> model notifications as first-class rows in the database, not as ad-hoc emails. A service emits a domain event &rarr; a notification worker fans it out into channels per user preferences &rarr; each channel is a separate, idempotent deliverer. Show in-app notifications via WebSocket for connected users and fall back to DB on reconnect. Provide an "unread count" endpoint for badges and a "mark read" mutation. Respect <strong>quiet hours</strong> and <strong>digest windows</strong>.</p>
<pre><code>// schema — Postgres
// notifications (id, user_id, type, payload jsonb, read_at, created_at)
// notification_preferences (user_id, type, channels text[], quiet_hours int4range)

// domain service publishes an event; a worker fans it out
bus.on("order.shipped", async ({ orderId, userId }) =&gt; {
  await notifyQueue.add("notify", { userId, type: "order_shipped", payload: { orderId } });
});

new Worker("notify", async (job) =&gt; {
  const { userId, type, payload } = job.data;
  const prefs = await db.notificationPreferences.findUnique({ where: { userId_type: { userId, type } } });
  const channels = prefs?.channels ?? defaultChannelsFor(type);    // e.g. ["in_app","push"]

  // persist the record first — the source of truth
  const n = await db.notification.create({ data: { userId, type, payload } });

  // in-app — push over WebSocket if the user is connected
  if (channels.includes("in_app")) {
    io.to(`user:${userId}`).emit("notification", { id: n.id, type, payload, createdAt: n.createdAt });
  }

  // quiet hours — hold email/push if inside the user's window
  const inQuietHours = isInQuietHours(prefs?.quietHours, new Date(), userTz(userId));

  if (channels.includes("push") &amp;&amp; !inQuietHours) await pushQueue.add("push", { userId, n });
  if (channels.includes("email")) {
    if (prefs?.emailDigest) await digestQueue.add("digest", { userId, notificationId: n.id });
    else                    await emailQueue.add("email",    { userId, notificationId: n.id });
  }
});

// digests — collect over a window, send as one email
// cron every hour: select users with pending digest items, batch them
await digestQueue.add("flush", {}, { repeat: { cron: "0 * * * *" } });

// API — list, unread count, mark read
app.get("/me/notifications", requireAuth, async (req, res) =&gt; {
  const cursor = req.query.cursor as string | undefined;
  const rows = await db.notification.findMany({
    where: { userId: req.user.id, ...(cursor &amp;&amp; { createdAt: { lt: decodeCursor(cursor) } }) },
    orderBy: { createdAt: "desc" },
    take: 21,
  });
  res.json({ data: rows.slice(0, 20),
             nextCursor: rows.length === 21 ? encodeCursor(rows[19].createdAt) : null });
});
app.get("/me/notifications/unread-count", requireAuth, async (req, res) =&gt; {
  const count = await db.notification.count({ where: { userId: req.user.id, readAt: null } });
  res.json({ count });
});
app.post("/me/notifications/read", requireAuth, async (req, res) =&gt; {
  await db.notification.updateMany({
    where: { userId: req.user.id, id: { in: req.body.ids } },
    data:  { readAt: new Date() },
  });
  res.sendStatus(204);
});

// WebSocket — per-user room, authed on upgrade
io.on("connection", (socket) =&gt; socket.join(`user:${socket.data.user.sub}`));
</code></pre>
<p><strong>Delivery guarantees &amp; UX:</strong></p>
<ul>
  <li><strong>DB first, channels second.</strong> If the email fails, the user sees it in-app on next login. If WebSocket is down, the badge still loads from DB on reconnect.</li>
  <li><strong>Idempotency.</strong> Job IDs like <code>notify:${eventId}:${userId}</code> prevent duplicates from at-least-once delivery.</li>
  <li><strong>Quiet hours &amp; digests</strong> prevent notification fatigue &mdash; a user who gets 40 Slack notifications in an hour unsubscribes.</li>
  <li><strong>Unsubscribe links</strong> on every email, per category (mentions vs. marketing) &mdash; required by CAN-SPAM/GDPR.</li>
  <li><strong>Group similar events</strong> &mdash; "Ada and 5 others commented" beats 6 separate notifications.</li>
</ul>
<p><strong>Trade-offs:</strong> building this in-house teaches you the domain deeply but eats weeks. Managed services &mdash; <strong>Knock</strong>, <strong>Courier</strong>, <strong>Novu</strong>, <strong>OneSignal</strong> &mdash; handle preferences, multi-channel routing, templates, and analytics. They're worth it if you have more than 5 notification types and more than one delivery channel. For <strong>mobile push</strong>, add <strong>FCM</strong>/<strong>APNs</strong> with per-device tokens, handle token-rotation on app restart, and respect platform throttles. Biggest failure modes: duplicated notifications (missing idempotency keys), lost-on-reconnect notifications (no DB persistence), and ignoring user preferences (eroding trust). Model notifications like emails, not like toasts.</p>
'''

ANSWERS[99] = r'''
<p><strong>Situation:</strong> health checks, diagnostics, and capacity decisions need to know the box they're running on &mdash; CPU count, memory, load, hostname, platform. Node's built-in <code>os</code> module exposes these. In containers, it's nuanced: some metrics report <em>host</em> values, not the container's cgroup limits.</p>
<p><strong>Approach:</strong> use <code>os</code> for hostname, platform, uptime, and load. For <em>container-aware</em> limits (CPU quota, memory limit), read <code>/proc</code> and cgroup files or use <code>process</code> APIs. Node 18.14+ added <code>os.availableParallelism()</code> which <em>does</em> respect cgroup CPU quotas &mdash; always prefer it over <code>os.cpus().length</code>.</p>
<pre><code>import os from "node:os";
import process from "node:process";

// static info
os.platform();                 // "linux" | "darwin" | "win32"
os.arch();                     // "x64" | "arm64"
os.release();                  // kernel version
os.hostname();                 // container or host name
os.homedir(), os.tmpdir();     // paths
os.userInfo();                 // uid, gid, username, shell

// CPU — respects container CPU quota (Node 18.14+)
os.availableParallelism();     // &lt;-- use this to size worker pools
os.cpus().length;              // &lt;-- host cores; misleading in containers
os.loadavg();                  // [1min, 5min, 15min] — Linux/macOS only; 0s on Windows

// Memory — host totals, not container limits
os.totalmem();                 // bytes visible to the OS
os.freemem();
process.memoryUsage();         // rss, heapTotal, heapUsed — the important ones
process.memoryUsage.rss();     // fast path for RSS only

// Network interfaces
os.networkInterfaces();        // map of interface -&gt; [{ address, family, mac, internal }]

// Uptime
os.uptime();                   // OS uptime seconds
process.uptime();              // this Node process uptime

// /health endpoint — the common consumer of all this
app.get("/health", (_req, res) =&gt; {
  const mem = process.memoryUsage();
  res.json({
    status: "ok",
    node: process.version,
    pid:   process.pid,
    hostname: os.hostname(),
    uptime: process.uptime(),
    cpus: os.availableParallelism(),
    load: os.loadavg(),
    memory: {
      rss: mem.rss,
      heapUsed: mem.heapUsed,
      heapTotal: mem.heapTotal,
      // container-aware memory limit (Linux cgroup v2)
      limit: await readCgroupMemoryMax().catch(() =&gt; null),
    },
  });
});

async function readCgroupMemoryMax() {
  const fs = await import("node:fs/promises");
  const v = (await fs.readFile("/sys/fs/cgroup/memory.max", "utf8")).trim();
  return v === "max" ? null : +v;
}

// V8 heap stats — important for JS memory leak detection
import v8 from "node:v8";
v8.getHeapStatistics();   // total_heap_size, heap_size_limit, used_heap_size...

// event loop lag — the single most useful "is Node healthy" signal
import { monitorEventLoopDelay } from "node:perf_hooks";
const h = monitorEventLoopDelay({ resolution: 20 }); h.enable();
setInterval(() =&gt; {
  console.log("loop p99 ms:", h.percentile(99) / 1e6);
  h.reset();
}, 60_000);
</code></pre>
<p><strong>Container gotchas:</strong></p>
<ul>
  <li><code>os.totalmem()</code> returns the <em>host's</em> RAM, not your container's limit. If you size caches by it in Kubernetes, you'll OOM. Read <code>/sys/fs/cgroup/memory.max</code> (cgroup v2) or <code>/sys/fs/cgroup/memory/memory.limit_in_bytes</code> (v1).</li>
  <li><code>os.cpus().length</code> returns host cores. <code>os.availableParallelism()</code> respects CPU quotas &mdash; use it for worker pool sizing.</li>
  <li><code>os.loadavg()</code> is host-wide and noisy in shared nodes &mdash; prefer event-loop lag as your per-process health signal.</li>
  <li>For full system metrics, <strong>systeminformation</strong> is a popular library that wraps dozens of OS calls into a tidy API.</li>
</ul>
<p><strong>Uses in practice:</strong> health endpoints for load balancers and Kubernetes probes, pre-flight boot logs ("starting on 4 cores, 8GB limit"), dynamic concurrency tuning (size BullMQ worker concurrency to available CPU), and diagnostic dumps in crash handlers. For real observability, send these into <strong>Prometheus</strong> via <code>prom-client</code> and graph them &mdash; don't rely on eyeballing <code>/health</code>.</p>
<p><strong>Trade-offs:</strong> the <code>os</code> module is lightweight and dependency-free but non-container-aware in several places. For production-grade observability, layer in OpenTelemetry metrics and a proper runtime agent (Datadog, New Relic, Elastic APM). For one-off diagnostics and auto-scaling decisions within a single process, <code>os</code> plus <code>process.memoryUsage()</code> plus <code>monitorEventLoopDelay()</code> is all you need. The mistake I see most often is sizing worker pools with <code>os.cpus().length</code> on Kubernetes &mdash; you end up with more workers than CPU quota allows, the scheduler thrashes, and latency spikes. Use <code>availableParallelism()</code>.</p>
'''

ANSWERS[100] = r'''
<p><strong>Situation:</strong> a web or mobile client holds local state that the server also owns &mdash; draft messages, form progress, tasks, offline edits. Keeping them in sync across tabs, devices, and network drops is a recurring systems problem. The right answer depends on conflict tolerance: a shopping cart "last write wins" is fine; a shared document needs CRDTs.</p>
<p><strong>Approach:</strong> pick the simplest sync model that fits.</p>
<ol>
  <li><strong>Polling</strong> &mdash; "tell me what changed since timestamp X." Simple, works everywhere, has latency.</li>
  <li><strong>Server-Sent Events (SSE)</strong> &mdash; one-way push, great for feeds and live dashboards.</li>
  <li><strong>WebSockets</strong> &mdash; bidirectional, right for chat, presence, collaborative edits.</li>
  <li><strong>CRDTs</strong> (Yjs, Automerge) &mdash; for true offline-first collaborative state.</li>
</ol>
<p>Always design around <strong>idempotent</strong> mutations (the client can retry safely), <strong>optimistic updates</strong> on the client (instant UI, reconcile on server ack), and a <strong>lastSyncedAt</strong> cursor so reconnects replay only what's new.</p>
<pre><code>// Delta-sync over polling/SSE — server exposes a cursor endpoint
// GET /sync?since=2026-04-18T08:00:00Z
app.get("/sync", requireAuth, async (req, res) =&gt; {
  const since = new Date(req.query.since as string);
  const changes = await db.change.findMany({
    where: { userId: req.user.id, updatedAt: { gt: since } },
    orderBy: { updatedAt: "asc" },
    take: 500,
  });
  res.json({
    changes,
    serverTime: new Date().toISOString(),           // client uses this as next `since`
    hasMore: changes.length === 500,
  });
});

// client — idempotent mutation + optimistic update
async function addTodo(localId: string, text: string) {
  // 1. optimistic: update local store immediately
  store.add({ id: localId, text, status: "pending" });

  // 2. server call with client-generated ID so retries are safe
  try {
    const saved = await fetch("/api/todos", {
      method: "POST",
      headers: { "content-type": "application/json", "idempotency-key": localId },
      body: JSON.stringify({ id: localId, text }),
    }).then(r =&gt; r.json());
    store.update(localId, { ...saved, status: "synced" });
  } catch (e) {
    store.update(localId, { status: "error" });
    queueRetry(localId);
  }
}

// real-time layer — WebSocket push; clients use to invalidate/prefetch, not as source of truth
io.of("/sync").on("connection", (socket) =&gt; {
  socket.join(`user:${socket.data.user.sub}`);
});

// when something changes on the server, notify subscribers
async function updateTodo(userId: string, todoId: string, patch: any) {
  const updated = await db.todo.update({ where: { id: todoId }, data: patch });
  await db.change.create({ data: { userId, entity: "todo", entityId: todoId, op: "update" } });
  io.of("/sync").to(`user:${userId}`).emit("invalidate", { entity: "todo", id: todoId });
  return updated;
}

// conflict resolution — version counters on each row
// PATCH /todos/:id  { version: 7, text: "..." }
app.patch("/todos/:id", requireAuth, async (req, res) =&gt; {
  const result = await db.todo.updateMany({
    where: { id: req.params.id, userId: req.user.id, version: req.body.version },
    data:  { text: req.body.text, version: { increment: 1 } },
  });
  if (result.count === 0) {
    // someone else changed it — return current server state for merge
    const current = await db.todo.findUnique({ where: { id: req.params.id } });
    return res.status(409).json({ error: "CONFLICT", current });
  }
  res.sendStatus(204);
});
</code></pre>
<p><strong>Design principles:</strong></p>
<ul>
  <li><strong>Server is the source of truth</strong> for anything that matters. Client state is a cache.</li>
  <li><strong>Client-generated IDs</strong> (UUID v7, ULID) make offline creates possible without waiting for server assignment.</li>
  <li><strong>Version or timestamp</strong> every mutable row; use optimistic concurrency so concurrent edits return 409, not silent overwrites.</li>
  <li><strong>Separate push from pull.</strong> WebSockets tell the client <em>something changed</em>; the client <em>pulls</em> the authoritative state via the delta-sync endpoint. This survives WS outages.</li>
  <li><strong>Idempotency keys</strong> on every mutating request &mdash; the client retries without fear.</li>
  <li><strong>Background sync queue</strong> on the client &mdash; enqueue mutations when offline, replay on reconnect.</li>
</ul>
<p><strong>Trade-offs:</strong> roll-your-own sync works for moderate complexity (todos, CRM contacts, Kanban cards) but becomes a swamp at the edge cases &mdash; offline-first, multi-device, long disconnects, partial syncs. Dedicated sync engines remove this pain: <strong>Replicache</strong> and <strong>Zero</strong> (by Rocicorp), <strong>ElectricSQL</strong>, <strong>PowerSync</strong>, <strong>Firebase Firestore</strong>, and <strong>Supabase Realtime</strong> each make different trade-offs (schema constraints, pricing, self-hosted vs. managed). For true offline-first multi-user editing, <strong>Yjs</strong> or <strong>Automerge</strong> are the proven choices. The biggest failure pattern is "push and pray" &mdash; assuming the WebSocket delivers every update; it won't, and clients that rely on it drift out of sync. Always back real-time pushes with a pull-based reconciliation endpoint, and your system will be resilient to every networking failure mode that will actually happen in production.</p>
'''
