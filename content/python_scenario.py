"""Python · Scenario Based · Detailed answers. Each value is an HTML snippet."""

ANSWERS = {}

ANSWERS[1] = r'''
<p><strong>Situation:</strong> a web app repeats expensive work — database lookups, external API calls, rendered pages. Caching trades memory for speed.</p>
<p><strong>Layer the cache by lifetime and scope:</strong></p>
<ul>
  <li><strong>Per-request</strong> — store inside the request object; avoids duplicate work in one call.</li>
  <li><strong>Per-process in-memory</strong> — <code>functools.lru_cache</code> or <code>cachetools.TTLCache</code>. Fast, no serialization. Doesn't survive restarts or scale across replicas.</li>
  <li><strong>Distributed</strong> — Redis or Memcached. Shared across workers, survives restarts, supports TTLs and invalidation patterns.</li>
  <li><strong>CDN / HTTP cache</strong> — for responses that don't need per-user personalization; cheapest layer.</li>
</ul>
<pre><code>import redis, json, hashlib
r = redis.Redis()

def cached(ttl=300):
    def deco(fn):
        def wrapped(*args, **kwargs):
            key = f"{fn.__module__}:{fn.__name__}:" + hashlib.md5(
                json.dumps([args, kwargs], sort_keys=True, default=str).encode()
            ).hexdigest()
            hit = r.get(key)
            if hit: return json.loads(hit)
            result = fn(*args, **kwargs)
            r.setex(key, ttl, json.dumps(result, default=str))
            return result
        return wrapped
    return deco</code></pre>
<p><strong>Trade-offs:</strong> stale reads vs freshness — use short TTLs, cache-busting on writes, or versioned keys. Beware the <em>thundering herd</em> on cache expiry — mitigate with lock-based "cache stampede protection" or jittered TTLs. Never cache user-specific data under a shared key.</p>
'''

ANSWERS[2] = r'''
<p><strong>Scenario:</strong> expose a resource (say, a "Projects" service) over HTTP. Decide between Flask (lightweight, assemble your own stack) and Django REST Framework (batteries-included with admin, ORM, migrations).</p>
<p><strong>Foundational choices:</strong></p>
<ol>
  <li><strong>Resource modeling</strong> — nouns as URLs: <code>/projects</code>, <code>/projects/{id}</code>, <code>/projects/{id}/tasks</code>. HTTP verbs map to CRUD.</li>
  <li><strong>Status codes</strong> — 200/201/204 success; 400 client error; 401/403 auth; 404 not found; 409 conflict; 429 rate limited; 500/503 server errors.</li>
  <li><strong>Versioning</strong> — URL prefix <code>/v1/projects</code> or <code>Accept: application/vnd.app.v1+json</code>.</li>
  <li><strong>Pagination</strong> — cursor-based for large lists; <code>?limit=50&amp;after=...</code>.</li>
  <li><strong>Filtering &amp; sorting</strong> — <code>?status=active&amp;sort=-created_at</code>.</li>
  <li><strong>Auth</strong> — JWT bearer for services, session cookies for browsers.</li>
</ol>
<pre><code># Flask + marshmallow — lightweight
from flask import Flask, jsonify, request, abort
app = Flask(__name__)

@app.get("/v1/projects")
def list_projects():
    page = int(request.args.get("page", 1))
    return jsonify(paginate(Project.query, page))

@app.post("/v1/projects")
def create_project():
    data = ProjectSchema().load(request.json)
    p = Project.create(**data)
    return jsonify(ProjectSchema().dump(p)), 201</code></pre>
<p>Use <strong>DRF</strong> for CRUD-heavy apps — its ViewSets + Serializers + Routers eliminate boilerplate. Use <strong>FastAPI</strong> (a modern alternative) when you want async + automatic OpenAPI docs out of the box. Always return machine-readable errors (<code>{"error": "code", "message": "..."}</code>) and include request IDs for correlation.</p>
'''

ANSWERS[3] = r'''
<p><strong>Scenario:</strong> users upload files up to several GB — videos, backups, datasets. Naive <code>request.files["upload"]</code> reads everything into memory, which crashes workers on large files.</p>
<p><strong>Approach — stream to storage, never to memory:</strong></p>
<ol>
  <li><strong>Accept chunked/streamed input</strong> — read from <code>request.stream</code> in fixed-size blocks.</li>
  <li><strong>Pipe directly to object storage</strong> — S3, GCS, Azure Blob. Use multipart upload for files &gt;100 MB so failures only need to retry one part.</li>
  <li><strong>Prefer presigned URLs</strong> — let clients PUT directly to S3 without hitting your app at all.</li>
  <li><strong>Resumable uploads</strong> for unreliable clients — tus.io protocol or S3 multipart.</li>
</ol>
<pre><code># Server-side streaming upload to S3 multipart
import boto3
s3 = boto3.client("s3")

@app.post("/upload")
def upload():
    mp = s3.create_multipart_upload(Bucket="data", Key=filename)
    parts, part_num = [], 1
    try:
        while chunk := request.stream.read(5 * 1024 * 1024):  # 5 MB
            etag = s3.upload_part(Bucket="data", Key=filename,
                                  PartNumber=part_num, UploadId=mp["UploadId"],
                                  Body=chunk)["ETag"]
            parts.append({"PartNumber": part_num, "ETag": etag})
            part_num += 1
        s3.complete_multipart_upload(Bucket="data", Key=filename,
                                     UploadId=mp["UploadId"],
                                     MultipartUpload={"Parts": parts})
    except Exception:
        s3.abort_multipart_upload(Bucket="data", Key=filename, UploadId=mp["UploadId"])
        raise</code></pre>
<p><strong>Trade-offs:</strong> presigned URLs are simpler and cheaper — the app only issues a short-lived signature. But you lose the ability to validate content in real-time; do it via an S3 event → Lambda/webhook to scan, thumbnail, or reject. Set max size limits (<code>MAX_CONTENT_LENGTH</code> in Flask), enforce content-type, and scan for malware (ClamAV).</p>
'''

ANSWERS[4] = r'''
<p><strong>Scenario:</strong> Django project needs sign-up, login, role-based permissions, API tokens.</p>
<p><strong>Authentication</strong> — "who are you":</p>
<ul>
  <li><strong>Session auth</strong> — Django's default for browsers. <code>django.contrib.auth</code> handles login/logout, password hashing (Argon2/PBKDF2), and CSRF.</li>
  <li><strong>Token/JWT</strong> — for SPAs and mobile. <code>djangorestframework-simplejwt</code> is the common pick.</li>
  <li><strong>Social login</strong> — <code>django-allauth</code> for Google/Microsoft/GitHub OAuth.</li>
  <li><strong>MFA</strong> — <code>django-otp</code> or <code>django-two-factor-auth</code> for TOTP.</li>
</ul>
<p><strong>Authorization</strong> — "what can you do":</p>
<pre><code># settings.py
AUTH_PASSWORD_VALIDATORS = [...]  # enforce strong passwords
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# models.py — custom user with role
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[("admin", "admin"), ("user", "user")])

# views.py — enforce
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.role == "admin")
def admin_only(request): ...

# DRF — per-view permissions
class ProjectView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]</code></pre>
<p>For <strong>RBAC</strong> use Django's built-in <code>Groups</code> + <code>Permissions</code>, or <code>django-guardian</code> for object-level perms. Never roll your own password hashing. Always use HTTPS, set SameSite cookies, log failed login attempts, and implement account lockout or rate-limiting on the login endpoint to prevent credential stuffing.</p>
'''

ANSWERS[5] = r'''
<p><strong>Scenario:</strong> a Flask app needs to serve hundreds of concurrent users. Flask's dev server is single-threaded — unsuitable for production.</p>
<p><strong>The production stack:</strong></p>
<ol>
  <li><strong>WSGI server</strong> — Gunicorn (multi-worker, pre-fork) or uWSGI. <code>gunicorn -w 4 -k gthread --threads 8 app:app</code> gives 4 processes × 8 threads = 32 concurrent requests.</li>
  <li><strong>Worker type</strong> — <code>sync</code> (CPU-friendly, one req per worker), <code>gthread</code> (threaded, good for I/O mix), <code>gevent</code>/<code>eventlet</code> (async via monkey-patching, scales to thousands).</li>
  <li><strong>Reverse proxy</strong> — nginx/Caddy in front for TLS, static files, buffering, compression.</li>
  <li><strong>Horizontal scaling</strong> — multiple Gunicorn instances behind a load balancer.</li>
</ol>
<pre><code># Gunicorn config
# gunicorn.conf.py
workers = (2 * os.cpu_count()) + 1
worker_class = "gthread"
threads = 4
worker_connections = 1000
timeout = 30

# For genuinely async workloads — use Quart or FastAPI instead of Flask
# Quart is Flask's async twin</code></pre>
<p><strong>Key constraints:</strong></p>
<ul>
  <li><strong>Process-local state breaks</strong> — caches, counters aren't shared between workers. Use Redis.</li>
  <li><strong>Database connections</strong> — pool per-worker; total = workers × pool_size. Don't exceed DB's max connections.</li>
  <li><strong>Long-running requests</strong> (&gt;5 s) tie up a worker — offload to Celery.</li>
  <li><strong>Worker timeout</strong> — set it aggressively; hung workers are killed by Gunicorn's master.</li>
</ul>
<p>Measure with <code>wrk</code> or <code>locust</code>; tune worker count based on CPU vs I/O profile. For radically higher concurrency, migrate to ASGI (FastAPI + uvicorn).</p>
'''

ANSWERS[6] = r'''
<p><strong>Scenario:</strong> a monolith has grown unwieldy — team velocity is dropping, deployments are risky, scaling one feature means scaling everything.</p>
<p><strong>Boundaries first — split by bounded context:</strong></p>
<ul>
  <li>User/Identity, Billing, Inventory, Notifications — not by technical layer.</li>
  <li>Each service owns its data; no direct DB access across boundaries.</li>
</ul>
<p><strong>Communication patterns:</strong></p>
<ul>
  <li><strong>Sync</strong> — REST or gRPC for request/response. Fast but coupled.</li>
  <li><strong>Async</strong> — message broker (RabbitMQ, Kafka, Redis Streams) for events. Decoupled and resilient.</li>
</ul>
<pre><code># FastAPI microservice skeleton
from fastapi import FastAPI
app = FastAPI()

# Synchronous inter-service call (HTTP)
import httpx
async def get_user(user_id):
    async with httpx.AsyncClient(timeout=2.0) as client:
        r = await client.get(f"http://users-svc/users/{user_id}")
        return r.json()

# Async event publishing
from aiokafka import AIOKafkaProducer
async def publish_event(event):
    await producer.send_and_wait("orders", json.dumps(event).encode())</code></pre>
<p><strong>Critical infrastructure:</strong> service discovery (Consul, Kubernetes DNS), API gateway (Kong, Envoy) for auth/rate limiting/routing, centralized logging (ELK, Loki), distributed tracing (OpenTelemetry + Jaeger), circuit breakers (<code>pybreaker</code>) to prevent cascading failures.</p>
<p><strong>Trade-offs:</strong> microservices add enormous operational complexity — network failures, eventual consistency, distributed transactions (sagas), versioning. Do them when team size and deployment velocity demand it; start as a modular monolith otherwise.</p>
'''

ANSWERS[7] = r'''
<p><strong>Scenario:</strong> a public API needs to prevent abuse and ensure fair sharing — without coordination, a single malicious client can overwhelm the service.</p>
<p><strong>Algorithms:</strong></p>
<ul>
  <li><strong>Fixed window</strong> — N requests per minute. Simplest; suffers from boundary bursts.</li>
  <li><strong>Sliding window</strong> — smoother; more memory per key.</li>
  <li><strong>Token bucket</strong> — allows bursts, then throttles. The typical choice.</li>
  <li><strong>Leaky bucket</strong> — enforces a steady output rate.</li>
</ul>
<p><strong>Implement with Redis:</strong></p>
<pre><code>import redis, time
r = redis.Redis()

def allow(key, limit=100, window=60):
    """Sliding window counter — atomic with INCR + EXPIRE"""
    bucket = f"{key}:{int(time.time()) // window}"
    count = r.incr(bucket)
    if count == 1:
        r.expire(bucket, window)
    return count &lt;= limit

# In a Flask before_request hook
@app.before_request
def rate_limit():
    key = f"rl:{request.remote_addr}"
    if not allow(key, limit=100, window=60):
        return jsonify({"error": "rate_limited"}), 429,
               {"Retry-After": "60"}</code></pre>
<p><strong>Production-ready libraries:</strong> <code>flask-limiter</code>, <code>django-ratelimit</code>, <code>slowapi</code> (FastAPI). For very high traffic, use an API gateway (Kong, Envoy, nginx <code>limit_req_zone</code>) — it stops abuse before it reaches your Python code.</p>
<p><strong>Keying strategy:</strong> rate-limit by API key for authenticated users, IP for anonymous. Include <code>X-RateLimit-*</code> headers so clients can self-regulate. Remember: IP-based limits break behind NAT and corporate proxies.</p>
'''

ANSWERS[8] = r'''
<p><strong>Scenario:</strong> a Django page that used to render in 200 ms now takes 4 seconds. Diagnose before optimizing.</p>
<p><strong>Diagnose first:</strong></p>
<ol>
  <li><strong>Django Debug Toolbar</strong> — shows query count, time, duplicate SQL.</li>
  <li><strong>Enable SQL logging</strong> — <code>LOGGING</code> with <code>django.db.backends</code> at DEBUG.</li>
  <li><strong>Run <code>EXPLAIN ANALYZE</code></strong> on the slow query in the DB console.</li>
</ol>
<p><strong>Common fixes:</strong></p>
<ul>
  <li><strong>N+1 queries</strong> — <code>select_related()</code> (FK/one-to-one, JOINs) or <code>prefetch_related()</code> (many-to-many/reverse FK, separate query + Python join).</li>
  <li><strong>Missing indexes</strong> — check <code>EXPLAIN</code>; add via <code>Meta.indexes</code> or migrations.</li>
  <li><strong>Too much data</strong> — use <code>.only()</code>/<code>.defer()</code> to limit columns; paginate.</li>
  <li><strong>Aggregations in Python</strong> — move to DB with <code>Count</code>, <code>Sum</code>, <code>F</code> expressions.</li>
  <li><strong>Unnecessary serialization</strong> — use <code>.values()</code> for read-only data instead of instantiating model objects.</li>
</ul>
<pre><code># Before — one SELECT per user + one for each user's project
for user in User.objects.all():
    for p in user.projects.all():   # N+1!
        ...

# After — 2 queries total
for user in User.objects.prefetch_related("projects").all():
    for p in user.projects.all():
        ...

# Add indexes
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    created_at = models.DateTimeField(db_index=True)
    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),  # composite
        ]</code></pre>
<p><strong>When DB tuning isn't enough:</strong> add caching (Redis), denormalize frequently-read aggregates, move read-heavy queries to a replica, use materialized views for complex reports. Profile after each change — guess-fixing wastes time.</p>
'''

ANSWERS[9] = r'''
<p><strong>Scenario:</strong> when a user receives a message, posts a comment, or an order status changes, the UI should update without polling.</p>
<p><strong>Transport options:</strong></p>
<table>
  <thead><tr><th>Mechanism</th><th>Use When</th></tr></thead>
  <tbody>
    <tr><td>Server-Sent Events</td><td>One-way server → client; simple; auto-reconnect</td></tr>
    <tr><td>WebSockets</td><td>Bi-directional, low-latency — chat, collab editing</td></tr>
    <tr><td>Long polling</td><td>Legacy fallback</td></tr>
    <tr><td>Web Push (APNs/FCM)</td><td>Mobile, offline — reaches users when app is closed</td></tr>
  </tbody>
</table>
<pre><code># Django Channels + Redis — scalable WebSockets
# settings.py
CHANNEL_LAYERS = {"default": {
    "BACKEND": "channels_redis.core.RedisChannelLayer",
    "CONFIG": {"hosts": [("redis", 6379)]},
}}

# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotifConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        self.group = f"user_{user.id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def notify(self, event):
        await self.send_json(event["payload"])

# Trigger from anywhere in the app
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
layer = get_channel_layer()
async_to_sync(layer.group_send)(f"user_{user.id}", {
    "type": "notify", "payload": {"kind": "message", "text": "hi"}
})</code></pre>
<p><strong>Architecture:</strong> app workers publish events to Redis; WebSocket workers (ASGI — Daphne, Uvicorn) subscribe and push to connected clients. This lets you scale WebSocket connections independently from HTTP workers. Authenticate WebSocket connections at the handshake (cookie or token in query). Fall back to polling for clients that can't WebSocket.</p>
'''

ANSWERS[10] = r'''
<p><strong>Scenario:</strong> email sending, image processing, report generation — these take seconds to minutes. Doing them in the request cycle blocks the user and risks timeouts.</p>
<p><strong>Celery architecture:</strong></p>
<ul>
  <li><strong>Broker</strong> — Redis or RabbitMQ; holds pending tasks.</li>
  <li><strong>Worker processes</strong> — pick up tasks, execute, write results to result backend.</li>
  <li><strong>Result backend</strong> — Redis, DB, or disabled (fire-and-forget).</li>
  <li><strong>Scheduler (beat)</strong> — periodic tasks (cron-like).</li>
</ul>
<pre><code># tasks.py
from celery import Celery
app = Celery("myapp", broker="redis://redis:6379/0", backend="redis://redis:6379/1")

@app.task(bind=True, max_retries=3, default_retry_delay=60,
          autoretry_for=(TransientError,))
def send_welcome_email(self, user_id):
    try:
        user = User.objects.get(pk=user_id)
        mailer.send(user.email, "Welcome", render("welcome.html", user))
    except TransientError as e:
        raise self.retry(exc=e)    # exponential backoff

# In a view
send_welcome_email.delay(user.id)
# Or with options
send_welcome_email.apply_async(args=[user.id], countdown=10, expires=3600)

# Periodic task (with celery beat)
app.conf.beat_schedule = {
    "nightly-cleanup": {"task": "tasks.cleanup", "schedule": crontab(hour=3)},
}</code></pre>
<p><strong>Best practices:</strong> tasks should be <em>idempotent</em> (retries can't double-charge, double-email), accept only IDs (not full objects — they must serialize), set a reasonable <code>time_limit</code> to kill hung tasks, monitor with Flower or Prometheus. Separate queues for priorities (<code>-Q critical,default</code>) so a backlog of low-priority jobs doesn't delay urgent ones.</p>
<p><strong>Alternatives:</strong> RQ (simpler, Redis-only), Dramatiq (modern, cleaner error handling), arq (async-native), AWS SQS + Lambda for serverless.</p>
'''

ANSWERS[11] = r'''
<p><strong>Scenario:</strong> scrape hundreds of thousands of URLs daily — product prices, news articles, public data — within target-site politeness limits.</p>
<p><strong>Architecture:</strong></p>
<ol>
  <li><strong>URL frontier</strong> — Redis queue or database of URLs to fetch, deduped.</li>
  <li><strong>Workers</strong> — async fetchers (aiohttp) behind a rate limiter. Scale horizontally.</li>
  <li><strong>Parser stage</strong> — separate workers parse HTML into structured data (Scrapy or custom with parsel/lxml).</li>
  <li><strong>Storage</strong> — raw HTML in S3 (replay parsing cheaply), parsed data in Postgres/ClickHouse.</li>
  <li><strong>Scheduler</strong> — per-domain politeness delays (<code>robots.txt</code>, Crawl-Delay), retry strategy.</li>
</ol>
<pre><code># Scrapy + scrapy-redis gives distributed crawling for free
# settings.py
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_URL = "redis://redis:6379/0"
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = True
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# For JS-heavy sites — Playwright integration
# pip install scrapy-playwright</code></pre>
<p><strong>Critical considerations:</strong></p>
<ul>
  <li><strong>Respect <code>robots.txt</code></strong> — and Terms of Service. Don't scrape what's prohibited.</li>
  <li><strong>Identify yourself</strong> — User-Agent with contact email. Respond to abuse@ complaints.</li>
  <li><strong>Rotate IPs</strong> only when legitimate (residential proxies for bot-sensitive sites; ethical gray zone).</li>
  <li><strong>Cache aggressively</strong> — don't re-fetch pages that haven't changed (ETag, Last-Modified).</li>
  <li><strong>Handle errors robustly</strong> — retries with exponential backoff, circuit breakers per domain.</li>
  <li><strong>Detect layout changes</strong> — unit tests on parsers + alerts when extraction failure rate spikes.</li>
</ul>
<p>For JS-rendered sites (React SPAs), use Playwright or Splash — but they're 100× more expensive than plain HTTP.</p>
'''

ANSWERS[12] = r'''
<p><strong>Scenario:</strong> "users who liked X also liked Y" for an e-commerce or media app.</p>
<p><strong>Approaches by sophistication:</strong></p>
<ul>
  <li><strong>Popularity-based</strong> — show trending items. Cheapest, useful as a baseline and for cold-start users.</li>
  <li><strong>Content-based</strong> — recommend items with similar features (TF-IDF on descriptions, embedding similarity). Works from day one; doesn't use other users' behavior.</li>
  <li><strong>Collaborative filtering</strong> — item-item or user-user matrix factorization. Powerful but needs interaction data.</li>
  <li><strong>Hybrid</strong> — content + collaborative, blended by weights or a meta-learner.</li>
  <li><strong>Deep learning</strong> — two-tower models, transformers (SASRec, BERT4Rec) for sequence-aware recs.</li>
</ul>
<pre><code># Matrix factorization with implicit feedback
from implicit.als import AlternatingLeastSquares
import scipy.sparse as sp

# Build user-item matrix from purchase/view events
matrix = sp.csr_matrix(...)   # users × items

model = AlternatingLeastSquares(factors=64, regularization=0.01, iterations=15)
model.fit(matrix)

# Serve: for user 42, top 10 items not already purchased
recommendations = model.recommend(userid=42, user_items=matrix[42], N=10)</code></pre>
<p><strong>Production pipeline:</strong> Batch-train nightly on Spark/Dask → export embeddings → load into a vector search DB (pgvector, Pinecone, FAISS). Real-time requests: look up user embedding, ANN search for top-k items, re-rank with business rules (inventory, freshness, diversity).</p>
<p><strong>Evaluation:</strong> offline — precision@k, recall@k, NDCG on held-out data. Online — A/B test for click-through / add-to-cart lift. Guard against filter bubbles by injecting diversity and serendipity. Handle cold-start with content-based fallback.</p>
'''

ANSWERS[13] = r'''
<p><strong>Scenario:</strong> users upload avatars, documents, media. Local disk doesn't scale and dies with the server.</p>
<p><strong>Use Django's storage abstraction + object storage:</strong></p>
<pre><code># settings.py
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": "my-uploads",
            "default_acl": "private",
            "querystring_auth": True,     # signed URLs
            "querystring_expire": 3600,
        },
    },
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
}

# models.py — works the same, just saves to S3 under the hood
class Document(models.Model):
    file = models.FileField(upload_to="docs/%Y/%m/")
    user = models.ForeignKey(User, on_delete=CASCADE)
    size = models.PositiveBigIntegerField(editable=False)

    def save(self, *args, **kwargs):
        self.size = self.file.size
        super().save(*args, **kwargs)

# View — generate a signed download URL instead of proxying through the app
def download(request, pk):
    doc = get_object_or_404(Document, pk=pk, user=request.user)
    return HttpResponseRedirect(doc.file.url)     # already signed</code></pre>
<p><strong>Pre-signed uploads</strong> are the scalable pattern: the server signs an S3 PUT URL, the browser uploads directly. The app never handles file bytes — lower memory, no middleware bottleneck, handles GB files trivially.</p>
<p><strong>Security:</strong></p>
<ul>
  <li>Private buckets by default; signed URLs for access.</li>
  <li>Content-type validation + virus scanning via S3 events → Lambda.</li>
  <li>Enforce max size in pre-signed policy.</li>
  <li>Separate buckets per environment; per-user prefixes.</li>
  <li>Serve user uploads from a sandbox domain to defeat cross-origin attacks.</li>
</ul>
<p>For sensitive files, use server-side encryption (SSE-KMS). For large media, add a CDN in front.</p>
'''

ANSWERS[14] = r'''
<p><strong>Scenario:</strong> build a Slack-like chat — rooms, presence, typing indicators, message history.</p>
<p><strong>Stack:</strong> Django Channels (ASGI) + Redis (pub/sub + channel layer) + Postgres (message history).</p>
<pre><code># consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close(); return
        self.room = self.scope["url_route"]["kwargs"]["room"]
        self.group = f"chat_{self.room}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        # Announce presence
        await self.channel_layer.group_send(self.group, {
            "type": "user_joined", "user": self.user.username
        })

    async def disconnect(self, code):
        await self.channel_layer.group_send(self.group, {
            "type": "user_left", "user": self.user.username
        })
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content):
        # Persist first, then broadcast
        msg = await database_sync_to_async(Message.objects.create)(
            room_id=self.room, user=self.user, body=content["text"]
        )
        await self.channel_layer.group_send(self.group, {
            "type": "chat_message",
            "id": msg.id, "user": self.user.username,
            "text": msg.body, "timestamp": msg.created_at.isoformat(),
        })

    async def chat_message(self, event): await self.send_json(event)
    async def user_joined(self, event):  await self.send_json(event)
    async def user_left(self, event):    await self.send_json(event)</code></pre>
<p><strong>Scaling:</strong> Redis channel layer lets multiple ASGI servers share rooms. Partition Redis or use Redis Cluster past ~100k concurrent connections. For message history, paginate from Postgres (indexed on <code>(room_id, created_at DESC)</code>).</p>
<p><strong>Features to add:</strong> read receipts (last_read pointer per user), typing indicators (ephemeral events, don't persist), file/image messages (upload to S3, send URL), end-to-end encryption (hard — keys stay on device), offline-to-online sync (client fetches messages since last seen).</p>
'''

ANSWERS[15] = r'''
<p><strong>Scenario:</strong> an endpoint returns 10,000+ items. Returning them all is slow, wasteful, and risks memory issues.</p>
<p><strong>Two main strategies:</strong></p>
<table>
  <thead><tr><th></th><th>Offset pagination</th><th>Cursor pagination</th></tr></thead>
  <tbody>
    <tr><td>Request</td><td><code>?page=3&amp;size=20</code></td><td><code>?limit=20&amp;after=abc</code></td></tr>
    <tr><td>Good for</td><td>Admin UIs with page numbers</td><td>Infinite scroll, APIs</td></tr>
    <tr><td>Performance</td><td>Degrades on large offsets (<code>OFFSET 10000</code> still scans rows)</td><td>Constant — uses index</td></tr>
    <tr><td>Consistency</td><td>Items can appear/skip when data changes between pages</td><td>Stable — anchor doesn't shift</td></tr>
  </tbody>
</table>
<pre><code># DRF — built-in paginators
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
    "PAGE_SIZE": 20,
}

# Custom cursor pagination
class TimestampCursor(pagination.CursorPagination):
    ordering = "-created_at"       # required
    page_size = 20
    max_page_size = 100

class ArticleList(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    pagination_class = TimestampCursor

# Response includes next/prev links
{
  "next": "https://api/articles?cursor=cD0yMDI0LTAz...",
  "previous": null,
  "results": [...]
}</code></pre>
<p><strong>Implementation tips:</strong> sort by a tuple <code>(created_at, id)</code> — using just timestamps causes stability issues with duplicates. Base64-encode cursors to discourage URL hacking. Return total counts only when cheap (small tables); large-table counts are expensive. For infinite scroll, no totals needed — just <code>has_more</code>.</p>
'''

ANSWERS[16] = r'''
<p><strong>Scenario:</strong> keep users logged in across requests. Store per-user state (cart, flash messages) securely.</p>
<p><strong>Flask session options:</strong></p>
<ul>
  <li><strong>Default (secure cookies)</strong> — signed, client-side storage. Limited to ~4 KB; exposed to user.</li>
  <li><strong>Server-side</strong> via <code>Flask-Session</code>: Redis, Memcached, SQLAlchemy, filesystem.</li>
</ul>
<pre><code>from flask import Flask, session
from flask_session import Session
import redis

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ["SECRET_KEY"],        # rotate periodically
    SESSION_TYPE="redis",
    SESSION_REDIS=redis.from_url("redis://redis:6379"),
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
    SESSION_COOKIE_SECURE=True,                  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,                # no JS access
    SESSION_COOKIE_SAMESITE="Lax",               # CSRF defense
)
Session(app)

@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["email"], request.form["password"])
    if not user:
        abort(401)
    session.clear()                              # prevent fixation
    session["user_id"] = user.id
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.before_request
def load_user():
    g.user = User.query.get(session["user_id"]) if "user_id" in session else None</code></pre>
<p><strong>Security checklist:</strong> rotate session ID on login (prevents fixation), enforce HTTPS, set SameSite, short absolute and idle timeouts, invalidate all sessions on password change, store minimal data in session (just user_id — fetch rest from DB). For API (SPAs/mobile), skip sessions entirely — use JWT or opaque tokens with short expiry + refresh tokens.</p>
'''

ANSWERS[17] = r'''
<p><strong>Scenario:</strong> a SaaS app serves multiple customer organizations. Data must be isolated but the same code deploys for everyone.</p>
<p><strong>Three patterns:</strong></p>
<ol>
  <li><strong>Shared DB, shared schema</strong> — add <code>tenant_id</code> to every tenant-scoped table. Lowest ops cost; risk of cross-tenant leakage from a missing filter.</li>
  <li><strong>Shared DB, schema-per-tenant</strong> — Postgres schemas, one per tenant. Good isolation, manageable count.</li>
  <li><strong>DB-per-tenant</strong> — strongest isolation, highest ops. Required for compliance (HIPAA, data residency).</li>
</ol>
<pre><code># Pattern 1 — row-level with django-tenants middleware or a TenantManager
class TenantScopedModel(models.Model):
    tenant = models.ForeignKey("Tenant", on_delete=CASCADE, db_index=True)
    objects = TenantManager()              # auto-filters by current tenant
    class Meta:
        abstract = True

class Project(TenantScopedModel):
    name = models.CharField(max_length=200)

# Middleware sets tenant from subdomain or JWT claim
class TenantMiddleware:
    def __call__(self, request):
        request.tenant = Tenant.objects.get(slug=subdomain(request))
        set_current_tenant(request.tenant)      # thread-local
        return self.get_response(request)</code></pre>
<p><strong>For schema-per-tenant, use <code>django-tenants</code>:</strong> each request routes to the right schema via <code>search_path</code>; shared tables in "public" schema.</p>
<p><strong>Cross-cutting concerns:</strong> enforce tenant filter in base QuerySet to prevent bugs, log any query that returns data from multiple tenants, separate analytics DB for cross-tenant reports, per-tenant Celery queues if workloads differ drastically. Plan tenant deletion carefully — it's often a soft delete + scheduled purge.</p>
'''

ANSWERS[18] = r'''
<p><strong>Scenario:</strong> users want to search across millions of records — products, articles, messages — with relevance ranking, filters, typo tolerance.</p>
<p><strong>Options by scale:</strong></p>
<ul>
  <li><strong>SQL <code>LIKE '%x%'</code></strong> — works up to a few thousand rows. Can't handle relevance, no index usage.</li>
  <li><strong>Postgres full-text search</strong> — good up to millions, built-in, supports ranking. Use <code>SearchVector</code>, <code>SearchQuery</code>, <code>SearchRank</code>.</li>
  <li><strong>Elasticsearch / OpenSearch</strong> — purpose-built. Handles typos, synonyms, faceting, aggregations, billions of docs.</li>
  <li><strong>Meilisearch / Typesense</strong> — simpler ES alternatives with excellent typo-tolerance, good for small/medium apps.</li>
</ul>
<pre><code># Postgres FTS in Django
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

Article.objects.annotate(
    rank=SearchRank(SearchVector("title", "body", config="english"),
                     SearchQuery("django rest"))
).filter(rank__gt=0.1).order_by("-rank")

# Add a GIN index on the search vector column for speed
class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    search_vector = SearchVectorField(null=True)
    class Meta:
        indexes = [GinIndex(fields=["search_vector"])]

# Elasticsearch via django-elasticsearch-dsl
from django_elasticsearch_dsl import Document, Index, fields

@Index("articles").doc_type
class ArticleDoc(Document):
    title = fields.TextField(analyzer="english")
    body = fields.TextField(analyzer="english")
    tags = fields.KeywordField()
    class Django:
        model = Article

# Query
search = ArticleDoc.search().query("multi_match", query="django", fields=["title^3", "body"])</code></pre>
<p><strong>Production essentials:</strong> index asynchronously from the DB via Celery on save (don't block writes), handle re-indexing gracefully (alias pattern: build new index, swap alias atomically), implement search analytics (what people search + what they click) to tune relevance.</p>
'''

ANSWERS[19] = r'''
<p><strong>Scenario:</strong> a DRF API accepts/returns JSON. Invalid input should be rejected with clear errors; model instances should serialize safely.</p>
<p><strong>Serializers handle both directions:</strong></p>
<pre><code>from rest_framework import serializers, viewsets

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    task_count = serializers.IntegerField(source="tasks.count", read_only=True)
    name = serializers.CharField(max_length=200, required=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "owner", "task_count", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]

    def validate_name(self, value):
        if Project.objects.filter(name=value, owner=self.context["request"].user).exists():
            raise serializers.ValidationError("You already have a project with this name")
        return value

    def validate(self, attrs):      # cross-field validation
        if attrs.get("end_date") and attrs["end_date"] &lt; attrs.get("start_date"):
            raise serializers.ValidationError({"end_date": "must be after start_date"})
        return attrs

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)</code></pre>
<p><strong>Error format</strong> — DRF returns <code>{"field": ["msg"]}</code>. Standardize for the whole API with a custom exception handler so client parsing is consistent. Include a machine-readable <code>code</code> alongside human messages.</p>
<p><strong>Alternatives:</strong> <code>pydantic</code> + FastAPI gives schema-based validation with automatic OpenAPI docs. For complex object graphs, <code>marshmallow</code> is widely used. For performance-critical serialization, <code>msgspec</code> is 10× faster than all the above.</p>
'''

ANSWERS[20] = r'''
<p><strong>Scenario:</strong> add cross-cutting concerns to every request — logging, request IDs, tenant detection, timing, security headers — without polluting view code.</p>
<p><strong>Django middleware is just a callable:</strong></p>
<pre><code>import time, uuid, logging
log = logging.getLogger("requests")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.id = request.headers.get("X-Request-Id", uuid.uuid4().hex)
        start = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception:
            log.exception("unhandled", extra={"request_id": request.id})
            raise
        elapsed = time.perf_counter() - start
        log.info("%s %s → %d in %.3fs",
                 request.method, request.path, response.status_code, elapsed,
                 extra={"request_id": request.id})
        response["X-Request-Id"] = request.id
        return response

# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "myapp.middleware.RequestLoggingMiddleware",         # add here
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

# Middleware that needs to short-circuit
class MaintenanceMiddleware:
    def __call__(self, request):
        if settings.MAINTENANCE and not request.path.startswith("/admin/"):
            return HttpResponse("down for maintenance", status=503)
        return self.get_response(request)</code></pre>
<p><strong>Order matters:</strong> middleware runs top-down on request, bottom-up on response. Auth must run before views. Security-header middleware should be early (outermost). For async views, use the async-capable middleware pattern (implements both <code>__call__</code> and async variants).</p>
<p>Use middleware for genuine cross-cutting concerns. Business logic belongs in views or services; putting it in middleware hides control flow.</p>
'''

ANSWERS[21] = r'''
<p><strong>Scenario:</strong> users need notifications — in-app feed, email digests, push, SMS — with rules for delivery channels and quiet hours.</p>
<p><strong>Core design:</strong> decouple event generation from delivery via a queue.</p>
<pre><code># 1) Domain code emits an event — doesn't care about channels
from .tasks import deliver_notification

class Comment(models.Model):
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            for recipient in self.post.subscribers.all():
                Notification.objects.create(
                    user=recipient, kind="new_comment",
                    payload={"post_id": self.post_id, "comment_id": self.id},
                )
                deliver_notification.delay(recipient.id, "new_comment")

# 2) Celery task consults user prefs + throttling, fans out to channels
@shared_task(bind=True, max_retries=5)
def deliver_notification(self, user_id, kind):
    user = User.objects.get(pk=user_id)
    prefs = user.notification_preferences.get(kind, {})
    if not prefs.get("enabled", True) or in_quiet_hours(user):
        return
    if prefs.get("email"):
        send_email.delay(user.id, kind)
    if prefs.get("push"):
        send_push.delay(user.id, kind)
    if prefs.get("websocket"):
        push_to_websocket(user.id, kind)

# 3) Daily/weekly digest task collapses noisy notifications
@shared_task
def send_daily_digest():
    for user in User.objects.filter(digest_frequency="daily"):
        unread = Notification.objects.filter(user=user, seen=False, kind__in=DIGESTIBLE)
        if unread.exists():
            send_mail(user.email, "Your daily summary", render_digest(unread))</code></pre>
<p><strong>Details that matter:</strong> idempotency keys so a retried task doesn't double-send; per-channel rate limits (don't email someone 50× in a minute); a <code>Notification</code> DB model as the source of truth — channels are delivery only; user-facing preferences UI granular to notification type × channel; unsubscribe links in every email; SMS opt-in consent logs for compliance.</p>
'''

ANSWERS[22] = r'''
<p><strong>Scenario:</strong> users upload sensitive files (contracts, medical records) and need to download them later. Storage and retrieval must be secure and auditable.</p>
<p><strong>Storage:</strong></p>
<ul>
  <li><strong>Object storage</strong> (S3/GCS) with encryption at rest (SSE-KMS with customer-managed keys).</li>
  <li><strong>Private bucket</strong> — never publicly readable. Access only via signed URLs.</li>
  <li><strong>Per-user or per-tenant prefix</strong> — enforce in IAM policy.</li>
  <li><strong>Content validation</strong> — check file size, MIME type, optionally run antivirus (ClamAV on S3 events).</li>
</ul>
<pre><code># Presigned upload — server signs a short-lived URL
@login_required
def request_upload_url(request):
    filename = request.POST["filename"]
    key = f"users/{request.user.id}/{uuid4()}/{filename}"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": "uploads", "Key": key,
                "ContentType": request.POST["content_type"]},
        ExpiresIn=600,
        HttpMethod="PUT",
    )
    UploadRecord.objects.create(user=request.user, key=key, status="pending")
    return JsonResponse({"url": url, "key": key})

# Presigned download — server checks authorization first
@login_required
def download(request, record_id):
    rec = get_object_or_404(FileRecord, pk=record_id)
    if not rec.can_access(request.user):
        raise PermissionDenied
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": "uploads", "Key": rec.key,
                "ResponseContentDisposition": f'attachment; filename="{rec.name}"'},
        ExpiresIn=300,
    )
    AccessLog.objects.create(user=request.user, record=rec, ip=request.META.get("REMOTE_ADDR"))
    return HttpResponseRedirect(url)</code></pre>
<p><strong>Defense in depth:</strong> TLS 1.2+ for every hop; virus scan before marking uploads "available"; immutable audit log of accesses (append-only, preferably on a different account); short TTLs on signed URLs; rate-limit download endpoints; CSRF protection on upload confirmations; for ultra-sensitive data, client-side encryption so the server never sees plaintext.</p>
'''

ANSWERS[23] = r'''
<p><strong>Scenario:</strong> diagnose production incidents quickly. Printf debugging doesn't scale — you need structured, searchable, centralized logs.</p>
<p><strong>Layered approach:</strong></p>
<ol>
  <li><strong>Structured JSON logs</strong> at the app level — use <code>python-json-logger</code> or <code>structlog</code>.</li>
  <li><strong>Contextual fields</strong> — request_id, user_id, tenant, latency. Add via middleware and <code>contextvars</code>.</li>
  <li><strong>Correlation</strong> — propagate request_id through Celery tasks, external HTTP calls (as header), log output.</li>
  <li><strong>Ship to a central aggregator</strong> — CloudWatch, Datadog, Loki, ELK. Never rely on files you SSH to read.</li>
  <li><strong>Alerting</strong> — error-rate spikes, specific exception classes, latency percentiles.</li>
</ol>
<pre><code># settings.py
import logging.config
logging.config.dictConfig({
    "version": 1, "disable_existing_loggers": False,
    "formatters": {"json": {
        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
    }},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {"level": "WARNING"},
        "django.db.backends": {"level": "WARNING"},  # don't log every query
    },
})

# structlog with contextvars (async-safe)
import structlog, contextvars
request_id_var = contextvars.ContextVar("request_id", default=None)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()
log.info("user signed up", user_id=42, plan="pro")</code></pre>
<p><strong>Anti-patterns to avoid:</strong> logging sensitive data (passwords, tokens, PII) — scrub before logging; logging at DEBUG in production (ships a firehose); ignoring log lag as a signal (logging shouldn't silently drop messages). Layer on <strong>error aggregation</strong> (Sentry) for exception-specific triage and <strong>distributed tracing</strong> (OpenTelemetry + Jaeger/Tempo) for request-flow visibility across services.</p>
'''

ANSWERS[24] = r'''
<p><strong>Scenario:</strong> process credit-card payments. Correctness, security, and compliance (PCI DSS) dominate every design choice.</p>
<p><strong>Never touch raw card data directly</strong> — use a PSP (Stripe, Adyen, Braintree) to stay out of PCI scope. The PSP's tokenization means card numbers never reach your servers.</p>
<pre><code># FastAPI + Stripe — charge flow
import stripe, uuid
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

@app.post("/payments")
async def charge(req: PaymentRequest, idempotency_key: str = Header()):
    # 1) Idempotency — caller sends same key on retry; we de-dup
    existing = await Payment.get_by_idem(idempotency_key)
    if existing:
        return existing

    # 2) Create intent — Stripe holds the charge state machine
    intent = stripe.PaymentIntent.create(
        amount=req.amount_cents, currency=req.currency,
        customer=req.customer_id, payment_method=req.payment_method_id,
        idempotency_key=idempotency_key,
        confirm=True, off_session=False,
    )

    # 3) Persist our record; status is DRIVEN by webhooks, not this response
    payment = await Payment.create(id=intent.id, status="pending",
                                     amount=req.amount_cents, idem=idempotency_key)
    return payment

# Webhook — Stripe notifies us of authoritative status changes
@app.post("/webhooks/stripe")
async def stripe_hook(request):
    event = stripe.Webhook.construct_event(await request.body(),
                                            request.headers["Stripe-Signature"],
                                            os.environ["STRIPE_WEBHOOK_SECRET"])
    if event.type == "payment_intent.succeeded":
        await mark_paid(event.data.object.id)
    elif event.type == "payment_intent.payment_failed":
        await mark_failed(event.data.object.id)</code></pre>
<p><strong>Critical patterns:</strong> <em>idempotency keys</em> on every mutating call (network retries must not double-charge); treat webhook events as the source of truth for async state; store amounts as integer cents with explicit currency (never floats); maintain an append-only ledger for auditing; separate "authorization" and "capture" for reservations. Reconcile daily with PSP reports to catch silent discrepancies.</p>
<p><strong>For subscriptions:</strong> Stripe Billing handles proration, dunning, tax. Rolling your own is months of work and risk.</p>
'''

ANSWERS[25] = r'''
<p><strong>Scenario:</strong> Django API needs to cap request rates per user or per IP — same goal as Q7 but specifically Django + Redis.</p>
<p><strong>Use <code>django-ratelimit</code> for decorators or roll your own with Redis:</strong></p>
<pre><code># With django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key="user_or_ip", rate="100/m", block=True)
def api_view(request):
    ...

# Custom sliding-window via Redis sorted sets — more accurate
import redis, time
r = redis.Redis()

def check_rate_limit(key: str, limit: int, window: int) -&gt; tuple[bool, int]:
    """Returns (allowed, remaining). Uses sorted set, atomic Lua script."""
    now = time.time()
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)    # drop old entries
    pipe.zcard(key)                                  # count in window
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, window)
    _, count, _, _ = pipe.execute()
    return count &lt; limit, limit - count - 1

# Django middleware applying it
class RateLimitMiddleware:
    def __call__(self, request):
        if request.path.startswith("/api/"):
            key = f"rl:{request.user.id if request.user.is_authenticated else request.META['REMOTE_ADDR']}"
            allowed, remaining = check_rate_limit(key, 100, 60)
            if not allowed:
                resp = JsonResponse({"error": "rate_limited"}, status=429)
                resp["Retry-After"] = "60"
                return resp
            response = self.get_response(request)
            response["X-RateLimit-Remaining"] = str(remaining)
            return response
        return self.get_response(request)</code></pre>
<p><strong>Advanced:</strong> tier users (free: 60/min, pro: 1000/min) via dynamic limit lookup per API key; separate buckets per endpoint class (writes much stricter than reads); use Redis Lua scripts for true atomicity. Offload to an edge rate-limiter (Cloudflare, nginx, API Gateway) to stop abusive traffic before it reaches Python — much cheaper at high volume.</p>
'''

ANSWERS[26] = r'''
<p><strong>Scenario:</strong> an ops dashboard shows live metrics — CPU, request rate, active users, alerts — updating without reloads.</p>
<p><strong>Architecture:</strong></p>
<ol>
  <li><strong>Metric producers</strong> — apps push samples to a time-series store (Prometheus, InfluxDB) or directly to a broker.</li>
  <li><strong>Aggregator</strong> — a Python service subscribes to the broker (Redis pub/sub, Kafka) and computes windowed aggregates.</li>
  <li><strong>WebSocket fan-out</strong> — connected clients receive updates via Django Channels / FastAPI WebSockets.</li>
  <li><strong>Frontend</strong> — render with a chart lib (Chart.js, Plotly, ECharts) that updates incrementally.</li>
</ol>
<pre><code># FastAPI + WebSockets + Redis Pub/Sub
import asyncio, json, redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket

app = FastAPI()
redis_client = aioredis.from_url("redis://redis:6379")

@app.websocket("/ws/dashboard")
async def dashboard(ws: WebSocket):
    await ws.accept()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("metrics")
    try:
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await ws.send_text(msg["data"].decode())
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("metrics")

# Metrics producer — async task that samples and publishes
async def sample_metrics():
    while True:
        payload = {"ts": time.time(), "cpu": cpu_pct(), "req_rate": current_rps()}
        await redis_client.publish("metrics", json.dumps(payload))
        await asyncio.sleep(1)</code></pre>
<p><strong>Scaling concerns:</strong> 1 s updates × 1000 connected dashboards = high broker load. Throttle per-client or aggregate server-side to 1 "tick" per second. For many users viewing different dashboards, use per-dashboard channels. If clients miss updates during a disconnect, send a snapshot on reconnect then stream deltas.</p>
<p><strong>Off-the-shelf alternative:</strong> Grafana with Prometheus / Loki covers 90% of these needs without custom code — only build your own when the visualization or interactivity is too specific.</p>
'''

ANSWERS[27] = r'''
<p><strong>Scenario:</strong> a JavaScript SPA at <code>app.example.com</code> calls an API at <code>api.example.com</code>. Browsers block these cross-origin requests unless the server sends proper CORS headers.</p>
<pre><code># flask-cors — the standard
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Simple — allow specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://app.example.com", "https://admin.example.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "X-Request-Id"],
        "expose_headers": ["X-RateLimit-Remaining", "X-Request-Id"],
        "supports_credentials": True,         # if cookies/auth used
        "max_age": 600,                         # cache preflight 10 min
    }
})

# Per-route control
from flask_cors import cross_origin

@app.route("/api/widgets")
@cross_origin(origins=["https://app.example.com"])
def widgets(): ...</code></pre>
<p><strong>Under the hood:</strong> two kinds of requests. <em>Simple</em> (GET/POST with basic headers) just need <code>Access-Control-Allow-Origin</code>. <em>Preflighted</em> (PUT/DELETE, custom headers, or <code>Content-Type: application/json</code>) trigger an <code>OPTIONS</code> probe that must return headers listing allowed methods/headers/origins.</p>
<p><strong>Security pitfalls:</strong></p>
<ul>
  <li>Never use <code>origins="*"</code> with <code>supports_credentials=True</code> — browsers reject it anyway, and it's dangerous. Be explicit.</li>
  <li>Don't reflect arbitrary Origin headers without validation — attackers can exfiltrate data.</li>
  <li>CORS is a browser-enforced policy; it doesn't protect against curl or server-to-server calls. Auth is still needed.</li>
  <li>SameSite cookies + proper auth are orthogonal to CORS — configure both.</li>
</ul>
<p>For microservices behind an API gateway, handle CORS at the gateway layer instead of in each service.</p>
'''

ANSWERS[28] = r'''
<p><strong>Scenario:</strong> build a bot that responds to users on Slack / Telegram / Discord / WhatsApp — FAQ, support triage, or assistant-style.</p>
<p><strong>Two delivery patterns:</strong></p>
<ul>
  <li><strong>Webhook-driven</strong> — platform posts events to your HTTPS endpoint (Slack Events API, Telegram webhooks).</li>
  <li><strong>Long-poll / WebSocket</strong> — Slack Socket Mode, Telegram getUpdates — no inbound firewall needed.</li>
</ul>
<pre><code># Slack Bolt (Python) — webhook + event-driven
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

@app.event("app_mention")
def on_mention(event, say, ack):
    ack()
    user, text = event["user"], event["text"]
    # Offload to background — reply within 3 s (Slack deadline)
    handle_mention_async.delay(user, text, event["channel"])

@app.message("hello")
def greet(message, say):
    say(f"Hey &lt;@{message['user']}&gt;!")

# Slash command
@app.command("/summarize")
def summarize_cmd(ack, command, respond):
    ack()    # respond within 3 s
    respond("Working on it…")
    result = call_llm(command["text"])
    respond(result, response_type="in_channel")

# Mount in Flask
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.post("/slack/events")
def slack_events():
    return handler.handle(request)</code></pre>
<p><strong>Integrating an LLM:</strong> classify intent (maybe keyword → regex → fallback to LLM), retrieve relevant docs (vector search over your KB), call the LLM with the grounding context, log the interaction. Always verify platform signatures (Slack's signing_secret, Telegram's secret token) to reject forged requests.</p>
<p><strong>Scaling:</strong> webhooks must respond quickly; offload to a task queue and reply later via an API call ("deferred response"). Persist conversation state if the bot needs multi-turn memory — use the thread/channel ID as the key.</p>
'''

ANSWERS[29] = r'''
<p><strong>Scenario:</strong> ingest data from many sources (APIs, databases, files) daily, transform it, and load into a warehouse for analytics.</p>
<p><strong>Pattern:</strong></p>
<ol>
  <li><strong>Extract</strong> — pull raw data, land it in object storage (S3) as-is (the "raw zone"). Immutable record.</li>
  <li><strong>Transform</strong> — clean, validate, dedupe, join. Output to a "curated zone" in columnar format (Parquet).</li>
  <li><strong>Load</strong> — copy curated data to the warehouse (Snowflake, BigQuery, Redshift, DuckDB).</li>
  <li><strong>Serve</strong> — BI tools, dashboards, ML features read from the warehouse.</li>
</ol>
<pre><code># Apache Airflow DAG — industry standard
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

with DAG("daily_etl", start_date=datetime(2024, 1, 1),
         schedule="0 3 * * *", catchup=False,
         default_args={"retries": 3, "retry_delay": timedelta(minutes=5)}) as dag:

    extract = PythonOperator(task_id="extract",
                              python_callable=pull_from_source_api)
    transform = PythonOperator(task_id="transform",
                                python_callable=clean_and_enrich)
    load = PythonOperator(task_id="load",
                           python_callable=load_to_warehouse)

    extract &gt;&gt; transform &gt;&gt; load</code></pre>
<p><strong>Choices:</strong></p>
<ul>
  <li><strong>Orchestration</strong>: Airflow (mature, Python-native), Prefect (modern, Pythonic), Dagster (data-asset-centric).</li>
  <li><strong>Processing</strong>: pandas/polars for &lt;100 GB; PySpark or Dask for bigger. DuckDB handles GB-scale analytics brilliantly on a single box.</li>
  <li><strong>Transformations in SQL</strong>: <strong>dbt</strong> — test-driven, version-controlled SQL transforms. Combined with Airflow, unbeatable for modern ELT.</li>
</ul>
<p><strong>Production essentials:</strong> idempotency (reprocessing a day's data shouldn't duplicate); data quality checks (Great Expectations, dbt tests); observability (row counts, freshness SLAs, schema drift alerts); lineage tracking so you know downstream impact of a source change.</p>
'''

ANSWERS[30] = r'''
<p><strong>Scenario:</strong> users upload CSVs, images, or PDFs. Processing takes seconds to minutes — validation, thumbnail generation, text extraction, virus scanning.</p>
<p><strong>Split request handling from processing:</strong></p>
<pre><code># 1) Accept upload quickly — just save to storage + queue a job
from django.db import transaction

class UploadView(APIView):
    def post(self, request):
        file = request.FILES["file"]
        # Minimal validation (size, type)
        if file.size &gt; 100 * 1024 * 1024:
            return Response({"error": "too_large"}, status=413)
        # Save to storage
        record = FileJob.objects.create(
            user=request.user, original_name=file.name,
            size=file.size, status="queued",
        )
        record.file.save(f"{record.id}/{file.name}", file)

        # Queue after DB commit — guarantees the worker finds the record
        transaction.on_commit(lambda: process_upload.delay(record.id))
        return Response({"job_id": record.id}, status=202)

# 2) Worker — Celery task
@shared_task(bind=True, max_retries=3, default_retry_delay=60,
             time_limit=600, soft_time_limit=540)
def process_upload(self, job_id):
    job = FileJob.objects.get(pk=job_id)
    job.status = "processing"; job.save()
    try:
        if job.original_name.endswith(".csv"):
            process_csv(job)
        elif job.mime_type.startswith("image/"):
            thumbnails_and_optimize(job)
        elif job.mime_type == "application/pdf":
            extract_text_and_thumbnail(job)
        job.status = "done"
    except SoftTimeLimitExceeded:
        job.status = "timeout"
        raise
    except Exception as e:
        job.status = "failed"; job.error = str(e)
        raise self.retry(exc=e)
    finally:
        job.finished_at = timezone.now(); job.save()

# 3) Frontend polls /jobs/{id} for status or subscribes to a WebSocket
class JobStatusView(APIView):
    def get(self, request, pk):
        job = get_object_or_404(FileJob, pk=pk, user=request.user)
        return Response({"status": job.status, "result_url": job.result_url})</code></pre>
<p><strong>Design details:</strong> idempotent tasks (same job_id processed twice must produce the same result); chunk huge files (each part a sub-task); publish progress via Redis / WebSockets for real-time UI feedback; retention policy for uploaded files (auto-delete after N days); dedicated Celery queue + worker type (CPU-bound image ops → <code>-c 4</code> concurrency, not hundreds).</p>
'''

ANSWERS[31] = r'''
<p><strong>Scenario:</strong> endpoints that process or return tens of thousands to millions of rows — exports, analytics, bulk operations.</p>
<p><strong>Rules:</strong></p>
<ul>
  <li><strong>Never load everything into memory</strong> — stream.</li>
  <li><strong>Don't serialize synchronously</strong> if it takes &gt;few seconds — offload.</li>
  <li><strong>Use generators</strong> to yield rows as they're computed.</li>
</ul>
<pre><code># Streaming CSV export — Flask's Response with a generator
from flask import Response
import csv
from io import StringIO

@app.get("/export/orders.csv")
def export_orders():
    def generate():
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "email", "amount", "created_at"])
        yield buffer.getvalue(); buffer.seek(0); buffer.truncate(0)

        # Stream from DB — never load all rows
        with db.session.connection().execution_options(
            stream_results=True, max_row_buffer=1000
        ) as conn:
            for row in conn.execute(text("SELECT id, email, amount, created_at FROM orders")):
                writer.writerow(row)
                data = buffer.getvalue()
                if data:
                    yield data
                    buffer.seek(0); buffer.truncate(0)

    return Response(generate(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=orders.csv"})

# For analytical queries — use Polars or DuckDB, much faster than pandas
import duckdb
result = duckdb.sql("SELECT region, SUM(amount) FROM 'orders.parquet' GROUP BY region").df()</code></pre>
<p><strong>Alternatives for very large exports:</strong> generate the file in a Celery task, upload to S3, email the user a signed download link. Avoids holding a request connection open for minutes.</p>
<p><strong>For data analysis:</strong> <code>pandas</code> is O(rows) in memory — fails on datasets &gt; RAM. Switch to <code>polars</code> (faster, lazy mode) or <code>dask</code> / <code>pyspark</code> for distributed. <code>DuckDB</code> is a local analytic DB that queries Parquet/CSV files in place — brilliant for mid-size workloads (up to TBs on one box).</p>
'''

ANSWERS[32] = r'''
<p><strong>Scenario:</strong> users need charts, tables, and exports of business data — revenue over time, funnel metrics, cohort retention.</p>
<p><strong>Separate concerns:</strong></p>
<ol>
  <li><strong>Data layer</strong> — aggregations served from a read replica or a dedicated analytics DB.</li>
  <li><strong>API layer</strong> — Django DRF endpoints returning structured data.</li>
  <li><strong>Presentation</strong> — React / Vue with a charting lib (Chart.js, Recharts, ECharts, Plotly).</li>
</ol>
<pre><code># views.py — aggregate with the ORM
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

class RevenueTimeseriesView(APIView):
    def get(self, request):
        start = parse_date(request.query_params.get("start"))
        end = parse_date(request.query_params.get("end"))
        data = (
            Order.objects
            .filter(created_at__gte=start, created_at__lt=end,
                    tenant=request.user.tenant)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(revenue=Sum("amount_cents"), count=Count("id"))
            .order_by("month")
        )
        return Response([
            {"month": row["month"].isoformat(),
             "revenue_cents": row["revenue"],
             "count": row["count"]}
            for row in data
        ])

# Scheduled rollup to pre-aggregated tables for faster reads
@shared_task
def nightly_rollup():
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO revenue_daily (tenant_id, day, revenue, orders)
            SELECT tenant_id, DATE(created_at), SUM(amount), COUNT(*)
            FROM orders WHERE created_at &gt;= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY tenant_id, DATE(created_at)
            ON CONFLICT (tenant_id, day) DO UPDATE
              SET revenue = EXCLUDED.revenue, orders = EXCLUDED.orders
        """)</code></pre>
<p><strong>Performance choices:</strong></p>
<ul>
  <li><strong>Live queries</strong> — fine for small datasets / simple aggregates. Index the date column.</li>
  <li><strong>Pre-aggregated tables</strong> — for dashboards hit many times per second. Refresh via scheduled task.</li>
  <li><strong>Materialized views</strong> (Postgres) — declarative; refresh on schedule.</li>
  <li><strong>Warehouse + cube</strong> — for very complex reports, move data to BigQuery/Snowflake and query with dbt or Cube.js.</li>
</ul>
<p>Export to CSV/Excel via generators (Q31); export to PDF via WeasyPrint or an HTML-to-PDF microservice.</p>
'''

ANSWERS[33] = r'''
<p><strong>Scenario:</strong> different roles (admin, manager, member, viewer) should see and do different things. Permissions must be consistent across views, templates, and APIs.</p>
<p><strong>Django's built-ins cover most cases:</strong></p>
<pre><code># Use Groups + Permissions — set during migrations/fixtures
from django.contrib.auth.models import Group, Permission

admins, _ = Group.objects.get_or_create(name="admins")
admins.permissions.set(Permission.objects.filter(
    codename__in=["change_project", "delete_project", "invite_user"]
))

# Assign users to groups
user.groups.add(admins)

# Enforce in views — built-in decorators and mixins
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin

@permission_required("myapp.delete_project", raise_exception=True)
def delete_project(request, pk): ...

class ProjectDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "myapp.delete_project"

# DRF — custom permission class
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name="admins").exists()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.owner == request.user
        return obj.owner == request.user or request.user.groups.filter(name="admins").exists()</code></pre>
<p><strong>For object-level permissions (user X can edit project Y but not project Z):</strong> use <code>django-guardian</code> — it adds per-object permission grants and helpers.</p>
<p><strong>Role definition strategies:</strong></p>
<ul>
  <li><strong>Static roles</strong> in code — simple, good for small apps.</li>
  <li><strong>Data-driven roles</strong> — Role model + Permission assignments; admins edit in the UI.</li>
  <li><strong>Policy engine</strong> (<code>django-rules</code>, OPA): expressive predicates per action.</li>
</ul>
<p>In templates: <code>{% if perms.myapp.delete_project %}</code>. For SPAs: expose the user's permissions list in the /me endpoint so the UI can hide or show features — but always re-check server-side.</p>
'''

ANSWERS[34] = r'''
<p><strong>Scenario:</strong> third-party apps should access your API on behalf of users — like "Sign in with Google" for their own users.</p>
<p><strong>Use <code>authlib</code> for the server:</strong></p>
<pre><code># Flask + Authlib OAuth2 server
from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6750 import BearerTokenValidator

server = AuthorizationServer(app, query_client=query_client, save_token=save_token)

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic", "client_secret_post"]
    def save_authorization_code(self, code, request): ...
    def query_authorization_code(self, code, client): ...
    def delete_authorization_code(self, ac): ...
    def authenticate_user(self, ac): return User.query.get(ac.user_id)

server.register_grant(AuthorizationCodeGrant)

# Endpoints
@app.route("/oauth/authorize", methods=["GET", "POST"])
@login_required
def authorize():
    if request.method == "GET":
        grant = server.get_consent_grant(end_user=current_user)
        return render_template("authorize.html", grant=grant)
    if request.form["confirm"] == "yes":
        return server.create_authorization_response(grant_user=current_user)
    return server.create_authorization_response(grant_user=None)

@app.route("/oauth/token", methods=["POST"])
def issue_token():
    return server.create_token_response()

# Protect API routes
require_oauth = ResourceProtector()
require_oauth.register_token_validator(BearerTokenValidator())

@app.route("/api/me")
@require_oauth("profile")
def me():
    return jsonify(id=current_token.user.id, email=current_token.user.email)</code></pre>
<p><strong>Flows:</strong> <em>Authorization Code with PKCE</em> for SPAs and mobile — never use implicit flow (deprecated). <em>Client Credentials</em> for server-to-server. <em>Refresh Tokens</em> to extend sessions without re-auth.</p>
<p><strong>Hard lessons:</strong> store client secrets hashed (like passwords); short access-token lifetimes (minutes), longer refresh (days); per-scope permissions; redirect_uri exact-match only; all endpoints HTTPS-only. For most teams, use <strong>Auth0 / Keycloak / AWS Cognito</strong> rather than operating an OAuth server yourself — the cryptographic and security footprint is significant.</p>
'''

ANSWERS[35] = r'''
<p><strong>Scenario:</strong> evolving models over months — adding columns, indexes, tables, without breaking production.</p>
<p><strong>Django's migrations</strong> are the standard — auto-generated from model changes.</p>
<pre><code># Typical flow
# 1) Change models.py
class Order(models.Model):
    ...
    coupon_code = models.CharField(max_length=50, null=True, blank=True)   # NEW

# 2) Generate migration
python manage.py makemigrations orders
# Creates orders/migrations/0005_order_coupon_code.py

# 3) Review it — especially for production
python manage.py sqlmigrate orders 0005

# 4) Apply
python manage.py migrate

# Data migrations — fill a new column from existing data
from django.db import migrations

def backfill_slugs(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    for a in Article.objects.all():
        a.slug = slugify(a.title)
        a.save(update_fields=["slug"])

class Migration(migrations.Migration):
    dependencies = [("blog", "0010_add_slug_field")]
    operations = [migrations.RunPython(backfill_slugs, reverse_code=migrations.RunPython.noop)]</code></pre>
<p><strong>Zero-downtime migrations — the hard part:</strong></p>
<ol>
  <li><strong>Adding a nullable column</strong> is always safe.</li>
  <li><strong>Adding a NOT NULL column with default</strong> — in Postgres 11+, this is fast. In older versions, it rewrites the table and locks.</li>
  <li><strong>Renaming a column</strong> → expand-contract: add new, backfill, dual-write, switch code to read new, drop old.</li>
  <li><strong>Creating indexes on large tables</strong> → use <code>CREATE INDEX CONCURRENTLY</code>. Django has <code>AddIndexConcurrently</code>.</li>
  <li><strong>Dropping a column</strong> → always last, after code no longer references it.</li>
</ol>
<p><strong>Safeguards:</strong> <code>django-migration-linter</code> flags dangerous migrations before deploy. Run migrations <em>before</em> deploying the new app version when schema changes are backward-compatible. Roll forward, rarely back — reversing data migrations is error-prone.</p>
'''

ANSWERS[36] = r'''
<p><strong>Scenario:</strong> authenticate users against an external source — LDAP, SSO, a legacy database, an API key table — alongside Django's default username/password.</p>
<pre><code># backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class APIKeyBackend(BaseBackend):
    def authenticate(self, request, api_key=None, **kwargs):
        if not api_key:
            return None
        try:
            key = APIKey.objects.select_related("user").get(
                key_hash=hash_key(api_key), active=True
            )
        except APIKey.DoesNotExist:
            return None
        key.last_used_at = timezone.now()
        key.save(update_fields=["last_used_at"])
        return key.user

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None

# settings.py — add alongside default
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",       # username/password
    "myapp.backends.APIKeyBackend",                    # API keys
    "social_core.backends.google.GoogleOAuth2",        # via python-social-auth
]

# Middleware to recognize API key headers
class APIKeyMiddleware:
    def __call__(self, request):
        key = request.META.get("HTTP_X_API_KEY")
        if key and not request.user.is_authenticated:
            user = authenticate(request, api_key=key)
            if user:
                request.user = user
        return self.get_response(request)

# Use in authenticate() calls
from django.contrib.auth import authenticate
user = authenticate(request, api_key="abc123")</code></pre>
<p><strong>Key principles:</strong> <code>authenticate()</code> walks the backends in order; the first that returns a user wins. Each backend handles its own credential verification. Backends must also implement <code>get_user</code> for session resumption.</p>
<p><strong>Common uses:</strong> LDAP/Active Directory (<code>django-auth-ldap</code>), SAML (<code>djangosaml2</code>), OIDC (<code>mozilla-django-oidc</code>), magic links, API keys. Always hash API keys at rest (treat like passwords), support rotation, and log authentication events for audit.</p>
'''

ANSWERS[37] = r'''
<p><strong>Scenario:</strong> search millions of documents by keywords, with filters (date, category), typo tolerance, and relevance ranking. Postgres FTS is starting to strain.</p>
<p><strong>Architecture:</strong></p>
<ol>
  <li><strong>Primary DB</strong> (Postgres) — source of truth.</li>
  <li><strong>Elasticsearch / OpenSearch</strong> — search index, denormalized for query shape.</li>
  <li><strong>Indexer</strong> — asynchronously copies changes from DB to ES (Celery task on save, or a CDC stream).</li>
</ol>
<pre><code># Using elasticsearch-py
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://es:9200")

# Index a document
es.index(index="articles", id=article.id, document={
    "title": article.title,
    "body": article.body,
    "tags": list(article.tags.values_list("name", flat=True)),
    "author": article.author.username,
    "published_at": article.published_at.isoformat(),
})

# Search with ranking, filter, highlight
result = es.search(index="articles", body={
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": "django rest framework",
                    "fields": ["title^3", "body"],     # boost title
                    "fuzziness": "AUTO",                # typo tolerance
                }
            },
            "filter": [
                {"term": {"tags": "python"}},
                {"range": {"published_at": {"gte": "2024-01-01"}}},
            ],
        }
    },
    "highlight": {"fields": {"body": {}}},
    "size": 20, "from": 0,
})

for hit in result["hits"]["hits"]:
    print(hit["_score"], hit["_source"]["title"], hit.get("highlight"))</code></pre>
<p><strong>Production patterns:</strong> <em>alias swap</em> for re-indexing (build v2 index alongside v1, atomically swap the alias to zero-downtime re-index); bulk indexing for initial load (<code>helpers.bulk</code> is much faster than document-at-a-time); tune analyzers per field (english stemming for body, keyword for tags, ngram for autocomplete); track relevance with click-through metrics and iterate.</p>
<p><strong>Lighter alternatives:</strong> Meilisearch, Typesense — simpler ops, excellent defaults, handle most needs up to tens of millions of docs.</p>
'''

ANSWERS[38] = r'''
<p><strong>Scenario:</strong> bit.ly / tinyurl — accept a long URL, return a short one, redirect on GET.</p>
<pre><code>from flask import Flask, request, jsonify, redirect, abort
import hashlib, base62  # pip install pybase62

app = Flask(__name__)

@app.post("/shorten")
def shorten():
    url = request.json["url"]
    if not url.startswith(("http://", "https://")):
        return jsonify({"error": "invalid_url"}), 400

    # Approach 1: counter-based — auto-increment ID, base62 encode
    link = Link.create(target=url, user_id=get_user_id())
    code = base62.encode(link.id)
    link.update(code=code)
    return jsonify({"short": f"https://short.ly/{code}"})

@app.get("/&lt;code&gt;")
def expand(code):
    link = Link.query.filter_by(code=code).first_or_404()
    # Async click logging — don't block the redirect
    log_click.delay(link.id, request.remote_addr, request.headers.get("User-Agent"))
    return redirect(link.target, code=301)   # permanent redirect</code></pre>
<p><strong>Key design choices:</strong></p>
<ul>
  <li><strong>ID generation</strong>: auto-increment + base62 encoding is simplest. Concerns: sequential IDs leak creation order/count. Alternatives: random strings (collision-checked), hash of URL (deduplicates identical URLs).</li>
  <li><strong>Storage</strong>: index on <code>code</code> (unique). Cache hot codes in Redis to avoid DB hit per click.</li>
  <li><strong>Redirect type</strong>: 301 (permanent, cached by browsers — great for CDN) vs 302 (temporary, clicks always reach your server — needed for analytics/expiration). Pick based on whether you need per-click tracking.</li>
  <li><strong>Analytics</strong>: async click logging (Celery, Kafka), or let CDN access logs capture it.</li>
  <li><strong>Abuse</strong>: malware check (Google Safe Browsing API), rate-limit per-user shortening, captcha for anonymous shortening, block known-bad domains.</li>
</ul>
<p><strong>Scale:</strong> redirect reads dominate. Cache heavily. CDN can serve 301s directly from edge. Writes are tiny by comparison. At enormous scale (10B+ links), partition by code prefix.</p>
'''

ANSWERS[39] = r'''
<p><strong>Scenario:</strong> welcome emails, password resets, order confirmations, digests. Reliable delivery matters.</p>
<p><strong>Django's email stack:</strong></p>
<pre><code># settings.py — point at a transactional provider (SendGrid, SES, Postmark, Mailgun)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = os.environ["SENDGRID_API_KEY"]
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "noreply@example.com"

# Send via Celery — never block the request
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@shared_task(bind=True, max_retries=5, default_retry_delay=60,
             autoretry_for=(SMTPException,))
def send_templated_email(self, to, template, ctx, subject):
    html = render_to_string(f"emails/{template}.html", ctx)
    text = render_to_string(f"emails/{template}.txt", ctx)    # plain-text fallback
    msg = EmailMultiAlternatives(subject, text, to=[to])
    msg.attach_alternative(html, "text/html")
    msg.send()

# Usage
send_templated_email.delay(
    to=user.email, template="welcome",
    ctx={"name": user.name, "verify_url": verify_url},
    subject="Welcome to Acme",
)</code></pre>
<p><strong>Production essentials:</strong></p>
<ul>
  <li><strong>SPF, DKIM, DMARC</strong> — DNS records that authenticate your domain; without them, emails land in spam.</li>
  <li><strong>Plain-text alongside HTML</strong> — accessibility + spam-score boost.</li>
  <li><strong>Unsubscribe links</strong> — legal in many jurisdictions (CAN-SPAM, GDPR).</li>
  <li><strong>Transactional vs marketing</strong> — different IPs, different domains, different consent. Don't mix.</li>
  <li><strong>Webhooks for bounces / complaints</strong> — provider calls you; mark emails invalid, stop sending to them.</li>
  <li><strong>Idempotency keys</strong> on sends so retries don't double-email.</li>
  <li><strong>Preview/test</strong> with tools like Mailhog or MailPit locally.</li>
</ul>
<p>Alternatives: <code>django-anymail</code> for provider-agnostic sending; <code>django-mailer</code> for an outgoing queue persisted in DB.</p>
'''

ANSWERS[40] = r'''
<p><strong>Scenario:</strong> posts, products, or documents should be taggable — users add freeform labels, filters by tag, popular-tag widgets.</p>
<pre><code># Use django-taggit — industry standard
# pip install django-taggit
# settings: INSTALLED_APPS += ["taggit"]

from taggit.managers import TaggableManager

class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    tags = TaggableManager()

# Usage
article.tags.add("django", "rest", "python")
article.tags.remove("python")
article.tags.all()      # QuerySet of Tag

# Filter by tag
Article.objects.filter(tags__name__in=["django"])
Article.objects.filter(tags__name="python")

# Popular tags
from taggit.models import Tag
Tag.objects.annotate(n=Count("taggit_taggeditem_items")).order_by("-n")[:20]

# Similar articles — same tags
def similar(article, n=5):
    return (Article.objects
            .filter(tags__in=article.tags.all())
            .exclude(pk=article.pk)
            .annotate(common=Count("tags"))
            .order_by("-common", "-created_at")[:n])</code></pre>
<p><strong>Rolling your own for more control:</strong></p>
<pre><code>class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

class Article(models.Model):
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

    def add_tags(self, names):
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name.lower().strip(),
                                                defaults={"slug": slugify(name)})
            self.tags.add(tag)</code></pre>
<p><strong>Concerns:</strong> normalize tags (lowercase, strip, unicode); merge duplicates (<code>javascript</code> vs <code>JavaScript</code>) via a canonicalizer or moderation UI; tag suggestions via autocomplete (indexed prefix search); per-tag RSS feeds; tag-level access control if tags reveal sensitive info. At scale, pre-aggregate tag counts nightly instead of live GROUP BY.</p>
'''

ANSWERS[41] = r'''
<p><strong>Scenario:</strong> users define multi-step workflows — "when a Stripe payment completes, send welcome email, generate invoice PDF, sync to accounting". Each step may fail and need retry.</p>
<p><strong>Use Celery's Canvas primitives</strong> to compose tasks into workflows.</p>
<pre><code>from celery import chain, group, chord

# chain — sequential, output of one feeds the next
workflow = chain(
    fetch_payment.s(payment_id),
    send_welcome_email.s(),
    generate_invoice.s(),
    sync_to_quickbooks.s(),
)
workflow.apply_async()

# group — parallel, independent tasks
group(
    resize_thumbnail.s(image_id, 100),
    resize_thumbnail.s(image_id, 400),
    resize_thumbnail.s(image_id, 1200),
).apply_async()

# chord — group + callback (fan-out + fan-in)
chord(
    (process_chunk.s(chunk) for chunk in chunks),    # parallel
    aggregate_results.s()                            # called with list of results
)()

# Error-handling link
chain(step1.s(), step2.s()).on_error(handle_failure.s()).apply_async()</code></pre>
<p><strong>Observability:</strong> give each workflow a correlation ID logged at every task boundary so you can trace execution. Record run state in a DB model (<code>WorkflowRun</code> with status, started_at, finished_at, steps JSON) so users can see progress.</p>
<p><strong>For complex, long-lived workflows</strong> (days/weeks, human-in-the-loop approvals), Celery starts to creak. Use <strong>Apache Airflow</strong> or <strong>Prefect</strong> (scheduled DAGs, retries, UIs) for ETL-style pipelines and <strong>Temporal</strong> for long-running business workflows with compensation/rollback semantics. Temporal guarantees correctness even across worker crashes — it replays event history.</p>
<p><strong>Built-in alternatives:</strong> Django Q2 (simpler than Celery), Dramatiq (modern, better error handling), AWS Step Functions if you're on AWS.</p>
'''

ANSWERS[42] = r'''
<p><strong>Scenario:</strong> real-time voting/polls for live events. Many users see results update instantly when anyone votes.</p>
<p><strong>Stack:</strong> Django Channels for WebSockets + Redis channel layer + Postgres for persistence.</p>
<pre><code># consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class PollConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope["url_route"]["kwargs"]["poll_id"]
        self.group = f"poll_{self.poll_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        # Send initial snapshot
        await self.send_json(await self.poll_snapshot())

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content):
        if content["action"] == "vote":
            new_counts = await self.register_vote(
                self.scope["user"], content["option_id"]
            )
            # Broadcast to all subscribers
            await self.channel_layer.group_send(self.group, {
                "type": "poll_update",
                "counts": new_counts,
            })

    async def poll_update(self, event):
        await self.send_json({"type": "counts", "counts": event["counts"]})

    @database_sync_to_async
    def register_vote(self, user, option_id):
        with transaction.atomic():
            # prevent duplicate vote
            _, created = Vote.objects.get_or_create(poll_id=self.poll_id, user=user,
                                                     defaults={"option_id": option_id})
            if not created:
                raise ValueError("already voted")
            # Recompute counts
            return dict(
                PollOption.objects.filter(poll_id=self.poll_id)
                .annotate(n=Count("votes")).values_list("id", "n")
            )</code></pre>
<p><strong>Concerns at scale:</strong> thousands of viewers × each vote triggers a broadcast = fan-out gets expensive. Mitigate: batch updates (send every 100 ms, not per-vote); use Redis <code>INCR</code> for live counts and only hit Postgres periodically for persistence; rate-limit voting. For truly massive events, offload to a dedicated realtime service (Ably, Pusher) that handles millions of connections for you.</p>
'''

ANSWERS[43] = r'''
<p><strong>Scenario:</strong> serve content in multiple languages (<em>i18n</em>) and adapt to region formats — currency, dates, number separators (<em>l10n</em>).</p>
<pre><code># settings.py
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
    ("fr", "Français"),
    ("ja", "日本語"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",      # detects from URL/session/browser
    ...
]

# urls.py — prefix URLs with language code
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path("articles/", include("blog.urls")),
    prefix_default_language=False,
)

# In Python code
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l   # lazy for class-level

def welcome(request):
    msg = _("Welcome, %(name)s!") % {"name": request.user.name}

# In templates
{% load i18n %}
{% trans "Hello" %}
{% blocktrans %}You have {{ count }} unread messages{% endblocktrans %}

# Generate translation files
python manage.py makemessages -l es    # creates locale/es/LC_MESSAGES/django.po
# Translators fill in msgstr in the .po files
python manage.py compilemessages        # compiles to .mo

# Format dates and currencies per locale
from django.utils import formats
formats.date_format(datetime.now(), "DATE_FORMAT")   # "Nov. 4, 2024" vs "4 nov. 2024"</code></pre>
<p><strong>Beyond the basics:</strong> translate model content (not just UI strings) with <code>django-modeltranslation</code> or <code>django-parler</code>; handle pluralization correctly (<code>ngettext</code> — some languages have 3+ plural forms); RTL languages (Arabic, Hebrew) need stylesheet support; use ICU MessageFormat for complex substitution rules. Integrate with translation management platforms (Crowdin, Lokalise, Transifex) for team workflows.</p>
'''

ANSWERS[44] = r'''
<p><strong>Scenario:</strong> recommend articles/videos/products to users — covered as an algorithmic question in Q12. This question focuses on <em>deploying</em> the model in a Django app.</p>
<pre><code># 1) Model training (offline, scheduled)
# Done in a notebook/airflow pipeline; model artifact saved to S3 or MLflow
import joblib
model = joblib.load("model.pkl")     # or load embeddings

# 2) Serving — two patterns

# Pattern A: In-process (low latency, per-worker memory cost)
# apps.py
class RecsConfig(AppConfig):
    def ready(self):
        from .recs import load_model
        load_model()                  # once per worker

# services/recs.py
_model = None
def load_model():
    global _model
    _model = joblib.load("/app/model.pkl")

def recommend(user_id, n=10):
    user_vec = fetch_user_embedding(user_id)
    return _model.predict(user_vec, top_k=n)

# Pattern B: Dedicated model-serving microservice
# - fastapi + uvicorn, ray serve, bentoml, kserve
# - Django calls it via HTTP
import httpx
def recommend(user_id):
    r = httpx.get(f"http://recs-svc:8000/recommend?user_id={user_id}")
    return r.json()["items"]

# 3) Caching — recompute nightly for active users
@shared_task
def precompute_recs():
    for user in User.objects.filter(last_seen__gte=timedelta(days=7).ago):
        cache.set(f"recs:{user.id}", recommend(user.id), timeout=86400)

# 4) Serving endpoint
class RecsView(APIView):
    def get(self, request):
        recs = cache.get(f"recs:{request.user.id}") or recommend(request.user.id)
        return Response({"items": recs})</code></pre>
<p><strong>Deployment decisions:</strong></p>
<ul>
  <li><strong>Small model, low QPS</strong> → in-process.</li>
  <li><strong>GPU-requiring / large / frequently updated</strong> → separate service.</li>
  <li><strong>Precompute vs real-time</strong> → depends on whether inputs change fast (recent behavior) or slowly (stable preferences).</li>
</ul>
<p><strong>Observability:</strong> log inputs + outputs (sampled) for offline analysis; track click-through rate and iterate. For A/B testing new models, route a percentage of requests to each and compare metrics.</p>
'''

ANSWERS[45] = r'''
<p><strong>Scenario:</strong> RESTful CRUD API for a set of resources. DRF eliminates boilerplate with ViewSets + Routers.</p>
<pre><code># serializers.py
from rest_framework import serializers

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "owner", "created_at"]
        read_only_fields = ["id", "owner", "created_at"]

# views.py
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "owner"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Custom action beyond CRUD
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        project = self.get_object()
        project.archive()
        return Response({"status": "archived"})

# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("api/v1/", include(router.urls)),
]
# Generates: GET/POST /projects/, GET/PUT/PATCH/DELETE /projects/{id}/, POST /projects/{id}/archive/</code></pre>
<p><strong>Add-ons worth knowing:</strong> <code>drf-spectacular</code> for OpenAPI 3.0 docs (auto-generated from serializers/views); <code>django-filter</code> for declarative filters; <code>djangorestframework-simplejwt</code> for JWT auth; <code>drf-nested-routers</code> for nested resources like <code>/projects/1/tasks/</code>.</p>
<p><strong>Versioning:</strong> DRF supports URL-prefix, accept-header, and namespace versioning. Pick one early — URL prefix (<code>/api/v1/</code>) is simplest and most visible. For breaking changes, deploy v2 alongside v1 and deprecate v1 over months.</p>
'''

ANSWERS[46] = r'''
<p><strong>Scenario:</strong> Django's default User model fits many apps, but most production projects want to customize — email as username, additional profile fields, soft delete.</p>
<p><strong>Set this up <em>before</em> first migration — hard to change later.</strong></p>
<pre><code># models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("email required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)     # hashes properly
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"           # login identifier
    REQUIRED_FIELDS = []               # prompted by createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

# settings.py
AUTH_USER_MODEL = "accounts.User"

# Always refer to user via the setting
# models.py
from django.conf import settings
class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)</code></pre>
<p><strong>Alternatives:</strong></p>
<ul>
  <li><strong><code>AbstractUser</code></strong> — keeps Django's username/email/etc., add your extras. Easier but stuck with username field.</li>
  <li><strong><code>AbstractBaseUser</code></strong> — total control, more boilerplate. Best for email-only login.</li>
  <li><strong>Profile model</strong> (one-to-one with User) — can add fields without swapping User. Good for existing projects that can't migrate.</li>
</ul>
<p><strong>Warnings:</strong> switching User model mid-project requires manual migration surgery. Admin forms need updating (<code>UserAdmin</code>). Tests using <code>UserFactory</code> need updating. Third-party apps assuming default User may break.</p>
'''

ANSWERS[47] = r'''
<p><strong>Scenario:</strong> Flask app accepts avatars, documents, or images. Like Q3 but focused on Flask's native mechanics.</p>
<pre><code>from flask import Flask, request, abort, url_for
from werkzeug.utils import secure_filename
import os, uuid

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,      # 16 MB cap
    UPLOAD_FOLDER="/var/uploads",
)
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "pdf"}

def is_allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.post("/upload")
def upload():
    if "file" not in request.files:
        return {"error": "no file"}, 400
    file = request.files["file"]
    if file.filename == "":
        return {"error": "empty filename"}, 400
    if not is_allowed(file.filename):
        return {"error": "invalid type"}, 400

    # Generate unique filename — don't trust user-supplied names
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    safe_name = secure_filename(unique_name)
    path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)

    file.save(path)

    # Additional validation — magic-number check, image decode test
    if ext in {"png", "jpg", "jpeg", "gif"}:
        try:
            from PIL import Image
            with Image.open(path) as img:
                img.verify()
        except Exception:
            os.remove(path)
            return {"error": "invalid image"}, 400

    return {"url": url_for("serve_upload", filename=safe_name)}, 201

@app.get("/uploads/&lt;path:filename&gt;")
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)</code></pre>
<p><strong>Security checklist:</strong></p>
<ul>
  <li><code>secure_filename</code> strips path traversal (<code>../</code>) and special chars.</li>
  <li>Rename uploads to UUIDs — don't rely on user filenames.</li>
  <li>Validate by content (MIME sniff, decode as expected format), not extension.</li>
  <li>Serve uploads from a separate subdomain to defeat cookie theft via uploaded HTML.</li>
  <li>Set <code>MAX_CONTENT_LENGTH</code> to prevent DoS.</li>
  <li>Run a virus scanner (ClamAV) for public-facing upload endpoints.</li>
  <li>For production, upload to S3 (pre-signed URLs, Q3) instead of local disk.</li>
</ul>
'''

ANSWERS[48] = r'''
<p><strong>Scenario:</strong> run tasks on a schedule — daily reports, weekly digests, hourly cleanup, minutely health checks.</p>
<p><strong>Celery Beat is the standard</strong> — a scheduler process that enqueues tasks at defined intervals.</p>
<pre><code># celery.py
from celery import Celery
from celery.schedules import crontab

app = Celery("myapp")
app.conf.beat_schedule = {
    "nightly-cleanup": {
        "task": "cleanup.purge_expired_sessions",
        "schedule": crontab(hour=3, minute=0),
    },
    "hourly-metrics": {
        "task": "metrics.compute_rollups",
        "schedule": crontab(minute=0),
    },
    "every-5-min": {
        "task": "monitoring.health_check",
        "schedule": 300.0,     # seconds
    },
    "weekly-digest": {
        "task": "email.send_weekly_digest",
        "schedule": crontab(day_of_week="mon", hour=9, minute=0),
    },
}

# Run
# celery -A myapp worker -l info        (workers)
# celery -A myapp beat -l info           (scheduler)

# Database-backed schedule — edit via Django admin
# pip install django-celery-beat
# settings: CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# Admins create/edit PeriodicTask rows without deploying code changes</code></pre>
<p><strong>Critical pitfalls:</strong></p>
<ul>
  <li><strong>Run exactly one beat process</strong> — two beats means every task fires twice. Use Kubernetes leader election, systemd, or a lock-based lease.</li>
  <li><strong>Idempotent tasks</strong> — a task queued at T:00 may run at T:05 if workers are busy; your job shouldn't care.</li>
  <li><strong>Don't embed business logic in the beat schedule</strong> — have the beat fire a tiny dispatcher task that figures out what to do.</li>
</ul>
<p><strong>For heavier needs</strong>: <strong>Airflow</strong> (DAGs, retries, UI, dependencies between scheduled tasks), <strong>Temporal</strong> (long-running workflows with state), <strong>cloud-native</strong> (AWS EventBridge + Lambda, GCP Cloud Scheduler).</p>
<p>For very simple needs — just systemd timers or cron calling a management command. Don't reach for Celery Beat if a 5-line crontab will do.</p>
'''

ANSWERS[49] = r'''
<p><strong>Scenario:</strong> third-party services (Stripe, GitHub, Twilio) notify your app of events via HTTPS POSTs. Process them reliably.</p>
<pre><code>import hmac, hashlib, json
from flask import Flask, request, abort

app = Flask(__name__)

@app.post("/webhooks/stripe")
def stripe_webhook():
    # 1) Verify signature — proves the request is from Stripe
    payload = request.get_data(as_text=False)
    sig = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except stripe.error.SignatureVerificationError:
        abort(400, "invalid signature")

    # 2) De-duplicate — providers sometimes retry
    if WebhookEvent.objects.filter(provider_event_id=event.id).exists():
        return "", 200       # already handled

    # 3) Persist BEFORE processing — crash-safe
    WebhookEvent.objects.create(
        provider="stripe",
        provider_event_id=event.id,
        event_type=event.type,
        payload=event.to_dict(),
    )

    # 4) Dispatch to a Celery worker — return 200 quickly
    handle_stripe_event.delay(event.id)
    return "", 200

@shared_task(bind=True, max_retries=5)
def handle_stripe_event(self, event_id):
    event = WebhookEvent.objects.get(provider_event_id=event_id)
    try:
        if event.event_type == "payment_intent.succeeded":
            mark_payment_paid(event.payload["data"]["object"])
        elif event.event_type == "customer.subscription.updated":
            update_subscription(event.payload["data"]["object"])
        event.processed_at = timezone.now(); event.save()
    except TransientError as e:
        raise self.retry(exc=e, countdown=60 * 2 ** self.request.retries)</code></pre>
<p><strong>Principles:</strong></p>
<ul>
  <li><strong>Verify signatures</strong> — HMAC of the raw body with a shared secret. Without this, anyone can fake events.</li>
  <li><strong>Return 200 quickly</strong> — providers retry aggressively on non-2xx. Do real work in a background task.</li>
  <li><strong>De-dupe by provider event ID</strong> — retries are routine.</li>
  <li><strong>Make processing idempotent</strong> — same event processed twice must produce the same outcome.</li>
  <li><strong>Log everything</strong> — webhooks are debug gold when something goes wrong.</li>
  <li><strong>Use <code>ngrok</code> or similar for local development</strong> so providers can reach your laptop.</li>
</ul>
<p>For complex ingestion across many webhooks, consider a dedicated ingest service that normalizes events into a common format before routing to handlers.</p>
'''

ANSWERS[50] = r'''
<p><strong>Scenario:</strong> API evolves — new fields, different formats, breaking changes. Clients can't all update at once.</p>
<p><strong>Versioning strategies:</strong></p>
<table>
  <thead><tr><th>Strategy</th><th>Example</th><th>Trade-off</th></tr></thead>
  <tbody>
    <tr><td>URL path</td><td><code>/api/v1/users</code></td><td>Most visible, cache-friendly, easy routing. DRF default.</td></tr>
    <tr><td>Accept header</td><td><code>Accept: application/vnd.app.v2+json</code></td><td>Purist REST. Less discoverable; complicates caching.</td></tr>
    <tr><td>Query param</td><td><code>?version=2</code></td><td>Easy but not semantic.</td></tr>
    <tr><td>Custom header</td><td><code>X-API-Version: 2</code></td><td>Clean URLs; clients must remember to send it.</td></tr>
  </tbody>
</table>
<pre><code># DRF — URL path versioning (most common)
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
}

# urls.py
urlpatterns = [
    path("api/v1/", include(("api.v1.urls", "v1"), namespace="v1")),
    path("api/v2/", include(("api.v2.urls", "v2"), namespace="v2")),
]

# Views detect version
class ProjectView(APIView):
    def get(self, request):
        if request.version == "v2":
            return Response(ProjectV2Serializer(qs, many=True).data)
        return Response(ProjectV1Serializer(qs, many=True).data)</code></pre>
<p><strong>Backward-compatible changes don't need a version bump:</strong> adding optional request fields, adding response fields (clients must ignore unknowns), new endpoints, more permissive validation.</p>
<p><strong>Breaking changes needing a new version:</strong> removing or renaming fields, changing types, changing status codes, changing auth requirements, removing endpoints.</p>
<p><strong>Deprecation lifecycle:</strong> announce v2 alongside v1; document migration; log usage of deprecated endpoints; email top consumers; wait 6-12 months; return <code>Sunset</code> and <code>Deprecation</code> headers; eventually retire v1. Keep a changelog with dates.</p>
'''

ANSWERS[51] = r'''
<p><strong>Scenario:</strong> process financial transactions reliably — transfers, refunds, settlements — where losing money or double-charging is unacceptable.</p>
<p><strong>Core principles:</strong></p>
<ul>
  <li><strong>Idempotency keys</strong> — every API call includes a client-generated UUID; the server dedupes. Essential for retries.</li>
  <li><strong>Database ACID transactions</strong> — debit/credit pairs wrap in <code>BEGIN...COMMIT</code>. Use row-level locks (<code>SELECT ... FOR UPDATE</code>) to prevent race conditions.</li>
  <li><strong>Double-entry bookkeeping</strong> — every transaction is a debit on one account and a credit on another; sum of balances is always zero.</li>
  <li><strong>Audit log</strong> — append-only event stream (ledger) with no updates or deletes. Current balances are derivable.</li>
  <li><strong>Outbox pattern</strong> — writes to the domain table and the "events to publish" table in one DB transaction; a separate worker reads the outbox and publishes to Kafka/SNS, marking rows as sent.</li>
</ul>
<pre><code>from django.db import transaction
from decimal import Decimal

@transaction.atomic
def transfer(from_id, to_id, amount: Decimal, idempotency_key: str):
    if Transfer.objects.filter(idempotency_key=idempotency_key).exists():
        return Transfer.objects.get(idempotency_key=idempotency_key)
    # Lock both accounts in a consistent order to avoid deadlocks
    ids = sorted([from_id, to_id])
    accounts = {a.id: a for a in Account.objects.select_for_update().filter(id__in=ids)}
    if accounts[from_id].balance &lt; amount:
        raise InsufficientFunds()
    accounts[from_id].balance -= amount
    accounts[to_id].balance += amount
    Account.objects.bulk_update([accounts[from_id], accounts[to_id]], ["balance"])
    transfer = Transfer.objects.create(from_id=from_id, to_id=to_id,
                                        amount=amount, idempotency_key=idempotency_key)
    LedgerEntry.objects.bulk_create([
        LedgerEntry(account_id=from_id, delta=-amount, transfer=transfer),
        LedgerEntry(account_id=to_id,   delta=amount,  transfer=transfer),
    ])
    Outbox.objects.create(event="transfer.completed", payload={...})
    return transfer</code></pre>
<p>Always use <code>decimal.Decimal</code> for money — never <code>float</code>. Store amounts in the smallest currency unit (cents). Compliance (PCI DSS, SOX) requires immutable audit logs, separation of duties, and retention. For production, consider specialized platforms: Stripe, Adyen, or ledger frameworks like TigerBeetle.</p>
'''

ANSWERS[52] = r'''
<p><strong>Scenario:</strong> Django app with heavy DB load. Layer caching from fast/local to slow/shared, invalidate precisely.</p>
<p><strong>Django's cache framework</strong> is pluggable: LocMem (dev), Redis (production), Memcached. Configure in <code>settings.py</code> once; use anywhere.</p>
<pre><code># settings.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/0",
    }
}

# Per-view caching
from django.views.decorators.cache import cache_page
@cache_page(60 * 15)
def homepage(request): ...

# Template fragment caching — cache expensive sub-sections
# {% load cache %}
# {% cache 300 sidebar request.user.id %} ... {% endcache %}

# Low-level cache API
from django.core.cache import cache
def get_popular_posts():
    key = "popular_posts:v2"
    posts = cache.get(key)
    if posts is None:
        posts = list(Post.objects.filter(popular=True).values()[:20])
        cache.set(key, posts, 3600)
    return posts

# Cache the QuerySet result, not the QuerySet itself
# (QuerySets are lazy — you'd re-execute every time)</code></pre>
<p><strong>Invalidation strategies:</strong></p>
<ul>
  <li><strong>TTL</strong> — simplest; accept staleness.</li>
  <li><strong>Versioned keys</strong> — bump <code>v2</code> to <code>v3</code> on schema changes; old keys expire naturally.</li>
  <li><strong>Signal-based</strong> — <code>post_save</code>/<code>post_delete</code> signals delete affected keys. Accurate but easy to miss cases.</li>
  <li><strong>Tag-based</strong> — third-party packages like <code>django-cachalot</code> track dependencies automatically.</li>
</ul>
<p>Watch for the <strong>thundering herd</strong> — when cache expires, many requests recompute simultaneously. Mitigate with <code>cache.add()</code> locks or libraries like <code>django-cacheops</code> that serialize recomputation.</p>
'''

ANSWERS[53] = r'''
<p><strong>Scenario:</strong> push server-originated updates (stock prices, chat messages, live dashboards) to browsers instantly, not on polling.</p>
<p><strong>Three main transports, choose by requirements:</strong></p>
<table>
<tr><th>Tech</th><th>Direction</th><th>Use case</th></tr>
<tr><td>WebSocket</td><td>Bi-directional</td><td>Chat, games, collaborative editing</td></tr>
<tr><td>Server-Sent Events (SSE)</td><td>Server → client only</td><td>Notifications, feeds, progress bars</td></tr>
<tr><td>HTTP long-polling</td><td>Client initiates</td><td>Legacy fallback, firewall traversal</td></tr>
</table>
<pre><code># Django Channels — WebSocket support
# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
application = ProtocolTypeRouter({
    "websocket": URLRouter([path("ws/orders/", OrderConsumer.as_asgi())]),
})

# consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer

class OrderConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        await self.channel_layer.group_add(f"user_{self.user_id}", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(f"user_{self.user_id}", self.channel_name)

    async def order_update(self, event):                 # called by group_send
        await self.send_json(event["data"])

# Publisher from anywhere (signal, view, celery task)
async_to_sync(channel_layer.group_send)(
    f"user_{user_id}",
    {"type": "order.update", "data": {"id": 123, "status": "shipped"}},
)</code></pre>
<p>Use <strong>Redis</strong> as the channel layer backend for multi-worker deployments. FastAPI with native async WebSockets is a strong alternative for greenfield services. Scale with sticky sessions at the load balancer and horizontal pod autoscaling on the WebSocket tier.</p>
'''

ANSWERS[54] = r'''
<p><strong>Scenario:</strong> add 2FA to a Django login flow — either TOTP (Google Authenticator-style) or SMS codes.</p>
<p><strong>TOTP via <code>django-otp</code> is the industry default</strong> — no SMS costs, better security than SMS (no SIM swap risk), works offline.</p>
<pre><code># pip install django-otp qrcode[pil]
INSTALLED_APPS += ["django_otp", "django_otp.plugins.otp_totp"]
MIDDLEWARE += ["django_otp.middleware.OTPMiddleware"]

# Enroll
from django_otp.plugins.otp_totp.models import TOTPDevice
def enroll(request):
    device = TOTPDevice.objects.create(user=request.user, confirmed=False)
    # Show QR code; user scans, enters first token
    url = device.config_url
    return render(request, "enroll.html", {"qr_url": url})

def confirm_enroll(request):
    device = TOTPDevice.objects.get(user=request.user, confirmed=False)
    token = request.POST["token"]
    if device.verify_token(token):
        device.confirmed = True; device.save()
        # Generate one-time backup codes for recovery
        for _ in range(10):
            StaticToken.objects.create(device=device.staticdevice, token=generate_code())

# Login flow
from django_otp import login as otp_login

def verify_2fa(request):
    device = request.user.totpdevice_set.get(confirmed=True)
    if device.verify_token(request.POST["token"]):
        otp_login(request, device)
        return redirect("home")
    return HttpResponse("Invalid code", status=401)

@otp_required                       # django_otp.decorators
def sensitive_view(request): ...</code></pre>
<p><strong>Security requirements:</strong> rate-limit verification attempts (e.g., 5 per minute); generate backup codes at enrollment; allow re-enrollment only after identity re-verification; rotate TOTP secret on device reset; log authentication events for audit. WebAuthn/FIDO2 (via <code>django-webauthn</code>) is even stronger — phishing-resistant hardware keys. Consider offering multiple factors and letting users choose.</p>
'''

ANSWERS[55] = r'''
<p><strong>Scenario:</strong> blogging platform REST API — posts, comments, tags, authors. Choose Flask for lightweight control and small app footprint.</p>
<pre><code>from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://..."
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    published_at = db.Column(db.DateTime)

class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=200))
    body = fields.Str(required=True)
    author_id = fields.Int(required=True)

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

@app.get("/v1/posts")
def list_posts():
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)
    query = Post.query.order_by(Post.published_at.desc())
    pagination = query.paginate(page=page, per_page=per_page)
    return jsonify({
        "data": posts_schema.dump(pagination.items),
        "meta": {"page": page, "total": pagination.total, "pages": pagination.pages},
    })

@app.post("/v1/posts")
@jwt_required
def create_post():
    try:
        data = post_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400
    post = Post(**data); db.session.add(post); db.session.commit()
    return jsonify(post_schema.dump(post)), 201

@app.errorhandler(404)
def not_found(e): return jsonify({"error": "not_found"}), 404</code></pre>
<p><strong>Essentials checklist:</strong> versioned URLs (<code>/v1</code>), Marshmallow/Pydantic schemas for validation, JWT auth (<code>flask-jwt-extended</code>), cursor/offset pagination, rate limiting (<code>flask-limiter</code>), OpenAPI docs (<code>apispec</code> or <code>flask-smorest</code>), structured error responses. Wrap DB access in <code>db.session.commit()</code>/<code>rollback()</code> with try/except.</p>
'''

ANSWERS[56] = r'''
<p><strong>Scenario:</strong> build your own validation library when existing ones (<code>pydantic</code>, <code>marshmallow</code>, <code>cerberus</code>) don't fit — e.g., highly custom error codes or domain-specific rules.</p>
<p><strong>Design:</strong> composable validators via decorators or descriptors; error accumulation rather than fail-fast; clear error paths for nested structures.</p>
<pre><code>from typing import Any, Callable
from dataclasses import dataclass, field

@dataclass
class ValidationError:
    path: str
    code: str
    message: str

class Validator:
    def __init__(self):
        self.errors: list[ValidationError] = []

    def check(self, path: str, value: Any, rules: list[Callable]):
        for rule in rules:
            err = rule(value)
            if err:
                code, msg = err
                self.errors.append(ValidationError(path, code, msg))

    def fail_if_errors(self):
        if self.errors:
            raise ValidationException(self.errors)

# Rule builders — curried
def required(value):
    return ("required", "is required") if value in (None, "", []) else None

def max_length(n):
    def rule(value):
        if value and len(value) &gt; n:
            return ("max_length", f"must be ≤ {n} chars")
    return rule

def pattern(regex):
    import re
    compiled = re.compile(regex)
    def rule(value):
        if value and not compiled.match(value):
            return ("pattern", f"must match {regex}")
    return rule

# Usage
def validate_user(data):
    v = Validator()
    v.check("name",  data.get("name"),  [required, max_length(100)])
    v.check("email", data.get("email"), [required, pattern(r"^[^@]+@[^@]+$")])
    v.fail_if_errors()</code></pre>
<p>Pros of custom: full control over error format, zero dependencies, domain vocabulary in error codes. Cons: reinvents a lot and is hard to match <code>pydantic</code>'s speed (Rust-backed in v2). For most projects, extending <code>pydantic.BaseModel</code> with custom <code>@field_validator</code>s is the pragmatic choice.</p>
'''

ANSWERS[57] = r'''
<p><strong>Scenario:</strong> Django app outgrew a single Postgres instance. Need horizontal scaling via sharding — partitioning data across databases by some key.</p>
<p><strong>Two main patterns:</strong></p>
<ol>
  <li><strong>Horizontal sharding by tenant/user</strong> — each shard holds a subset of users. Simple queries stay on one shard; cross-user queries get hard. Use a routing table or consistent hashing.</li>
  <li><strong>Read-replica split</strong> — not true sharding but often the first step. Writes to primary, reads to replicas via <code>DATABASE_ROUTERS</code>.</li>
</ol>
<pre><code># settings.py
DATABASES = {
    "default": {...},           # metadata / shard map
    "shard_0": {...},
    "shard_1": {...},
    "shard_2": {...},
}
SHARDS = ["shard_0", "shard_1", "shard_2"]

# Router
import hashlib

def shard_for(user_id: int) -&gt; str:
    h = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
    return SHARDS[h % len(SHARDS)]

class TenantRouter:
    tenant_models = {"blog.Post", "blog.Comment", "blog.Tag"}

    def _label(self, model):
        return f"{model._meta.app_label}.{model.__name__}"

    def db_for_read(self, model, **hints):
        if self._label(model) in self.tenant_models and "instance" in hints:
            return shard_for(hints["instance"].user_id)
        return None

    db_for_write = db_for_read

# Usage — manual .using() on a QuerySet
db = shard_for(current_user.id)
Post.objects.using(db).filter(user_id=current_user.id)

# Migrations — must run per shard
# python manage.py migrate --database=shard_0</code></pre>
<p><strong>Sharding is last-resort complexity.</strong> Exhaust easier scaling first: indexes, query tuning, caching, read replicas, partitioned tables (Postgres 11+ declarative partitioning stays single-DB). Re-sharding is painful — plan for it from day one with consistent hashing. Tools: <code>django-sharding</code>, Citus (Postgres extension), Vitess (for MySQL).</p>
'''

ANSWERS[58] = r'''
<p><strong>Scenario:</strong> image processing as a standalone microservice — resize, crop, format conversion, thumbnail generation — callable by other services, with auto-scaling for burst loads.</p>
<pre><code># FastAPI + Pillow — simple, async-friendly
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
from io import BytesIO
import boto3, uuid

app = FastAPI()
s3 = boto3.client("s3")
ALLOWED = {"image/jpeg", "image/png", "image/webp"}

@app.post("/v1/images/resize")
async def resize(file: UploadFile = File(...),
                 width: int = 800, height: int | None = None):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, "unsupported_format")
    data = await file.read()
    if len(data) &gt; 10 * 1024 * 1024:       # 10 MB cap
        raise HTTPException(413, "too_large")
    try:
        img = Image.open(BytesIO(data))
        img.verify()                         # quick sanity check
        img = Image.open(BytesIO(data))     # reopen after verify
    except Exception:
        raise HTTPException(400, "invalid_image")

    img.thumbnail((width, height or 10000))
    out = BytesIO()
    img.save(out, format="WEBP", quality=85)
    out.seek(0)

    key = f"resized/{uuid.uuid4()}.webp"
    s3.upload_fileobj(out, "my-bucket", key,
                      ExtraArgs={"ContentType": "image/webp"})
    return {"url": f"https://cdn.example.com/{key}"}</code></pre>
<p><strong>Production concerns:</strong></p>
<ul>
  <li>CPU-bound work — deploy with multiple Gunicorn/Uvicorn workers (one per core).</li>
  <li>For heavy formats (TIFF, HEIC), offload to Celery with <code>libvips</code> (faster and more memory-efficient than Pillow).</li>
  <li>Cache processed versions by (src-hash, params) in S3/CloudFront — identical requests get served from CDN.</li>
  <li>Strip EXIF metadata (privacy) on upload.</li>
  <li>Use dedicated image service like <code>imgproxy</code> or Cloudinary if you don't want to maintain this.</li>
</ul>
'''

ANSWERS[59] = r'''
<p><strong>Scenario:</strong> SaaS subscription billing — plans, upgrades, prorations, trial periods, invoicing, retries for failed payments.</p>
<p><strong>Don't build this from scratch.</strong> Use Stripe Billing, Paddle, or Chargebee; they handle PCI compliance, tax (Stripe Tax, TaxJar), dunning, and dozens of edge cases. You build the integration glue.</p>
<pre><code># Django models
class Plan(models.Model):
    stripe_price_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    amount_cents = models.IntegerField()
    interval = models.CharField(max_length=10)  # month, year

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100, unique=True)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20)    # trialing, active, past_due, canceled
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)

# Webhook handler — Stripe is the source of truth
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig = request.META["HTTP_STRIPE_SIGNATURE"]
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    handlers = {
        "customer.subscription.created":  handle_sub_created,
        "customer.subscription.updated":  handle_sub_updated,
        "customer.subscription.deleted":  handle_sub_deleted,
        "invoice.payment_failed":         handle_payment_failed,
    }
    handler = handlers.get(event["type"])
    if handler:
        handler(event["data"]["object"])
    return HttpResponse(status=200)</code></pre>
<p><strong>Design rules:</strong> webhook handlers must be <em>idempotent</em> (Stripe retries on failure); always verify the signature; record <code>stripe_event_id</code>s and skip duplicates; grant/revoke features based on webhook-driven status changes, not UI actions; test with Stripe CLI's event forwarding. Handle churn gracefully: dunning emails, grace periods, downgrade-on-cancel.</p>
'''

ANSWERS[60] = r'''
<p><strong>Scenario:</strong> protect a Flask API from abuse — per-IP or per-user request caps.</p>
<p><strong>Fastest: <code>flask-limiter</code>.</strong> Ships with decorator syntax, multiple storage backends, and sensible defaults.</p>
<pre><code>from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://redis:6379/0",
)

@app.get("/public")
def public():
    return "ok"

@app.get("/api/search")
@limiter.limit("10 per minute")
def search():
    return {"results": [...]}

@app.get("/api/expensive")
@limiter.limit("5 per hour", key_func=lambda: g.user.id if g.user else get_remote_address())
def expensive():
    return {...}

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "rate_limited",
        "retry_after_seconds": e.description,
    }), 429</code></pre>
<p><strong>Key decisions:</strong></p>
<ul>
  <li><strong>Key function</strong> — by IP (simple but NAT/proxies share), by user ID (requires auth), or combined. Use <code>X-Forwarded-For</code> carefully — trust only your load balancer's last hop.</li>
  <li><strong>Storage backend</strong> — Redis for multi-instance consistency; memory is per-process only.</li>
  <li><strong>Window algorithm</strong> — fixed window (default, simpler) vs sliding window (smoother, more accurate). Redis sorted sets implement sliding windows atomically.</li>
  <li><strong>Response headers</strong> — include <code>X-RateLimit-Limit</code>, <code>X-RateLimit-Remaining</code>, <code>X-RateLimit-Reset</code>, <code>Retry-After</code>.</li>
</ul>
<p>For DDoS-scale traffic, rate-limit at the edge (CloudFlare, AWS WAF) — reaching your app server is already expensive.</p>
'''

ANSWERS[61] = r'''
<p><strong>Scenario:</strong> implement autocomplete for a site search — "pyth" → ["python", "python programming", "pythagorean theorem"] — fast even with millions of documents.</p>
<p><strong>Elasticsearch's <code>completion</code> suggester or <code>edge_ngram</code> analyzer</strong> is purpose-built for this. Index short prefixes at write time; answer queries in milliseconds.</p>
<pre><code>from elasticsearch_dsl import Document, Text, Completion, connections
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl import Document as DjangoESDoc, fields

connections.create_connection()

class PostIndex(DjangoESDoc):
    class Index:
        name = "posts"
    title_suggest = fields.CompletionField()      # for suggester
    title_ngram = fields.TextField(                # for edge_ngram
        analyzer="edge_ngram_analyzer",
        search_analyzer="standard",
    )
    class Django:
        model = Post
        fields = ["title", "body"]

# Django view
def autocomplete(request):
    q = request.GET.get("q", "").strip()
    if len(q) &lt; 2:
        return JsonResponse({"suggestions": []})
    s = PostIndex.search().suggest(
        "title_suggestions", q,
        completion={"field": "title_suggest", "size": 10, "skip_duplicates": True},
    )
    response = s.execute()
    suggestions = [o["text"] for o in response.suggest.title_suggestions[0].options]
    return JsonResponse({"suggestions": suggestions})</code></pre>
<p><strong>Key choices:</strong></p>
<ul>
  <li><strong>Completion suggester</strong> — fastest (in-memory FST); exact prefix match; limited fuzziness.</li>
  <li><strong>Edge n-gram</strong> — more flexible; supports typos and mid-word; uses more disk.</li>
  <li><strong>Debounce</strong> — wait 200ms after last keystroke; cancel in-flight requests on new input.</li>
  <li><strong>Personalization</strong> — boost user's past queries or clicked results via a <code>function_score</code>.</li>
</ul>
<p>For smaller scale (&lt;1M rows), Postgres <code>pg_trgm</code> with a GiST index works surprisingly well without operating a separate service.</p>
'''

ANSWERS[62] = r'''
<p><strong>Scenario:</strong> Celery tasks fail intermittently — API timeouts, network blips. Must retry with backoff, not burn CPU, eventually give up and alert.</p>
<pre><code># celery_app/tasks.py
from celery import shared_task
from celery.exceptions import Retry
import requests
import logging

log = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,              # exponential — 1, 2, 4, 8, 16s...
    retry_backoff_max=600,            # cap at 10 min
    retry_jitter=True,                # randomize to avoid thundering herd
    max_retries=5,
    acks_late=True,                   # ack only after success — survives worker crash
)
def sync_to_crm(self, user_id: int):
    user = User.objects.get(id=user_id)
    try:
        r = requests.post("https://crm.example.com/api/users",
                          json={"id": user.id, "email": user.email},
                          timeout=10)
        r.raise_for_status()
    except requests.HTTPError as e:
        # Don't retry on 4xx — client errors won't fix themselves
        if e.response.status_code &lt; 500:
            log.error("CRM client error, not retrying: %s", e)
            raise            # bubbles up, goes to dead-letter handling
        raise self.retry(exc=e)

# Dead-letter queue — after max_retries
@shared_task
def handle_failed_task(task_name, task_id, args, kwargs, exc):
    FailedTaskLog.objects.create(
        task_name=task_name, task_id=task_id, args=args, kwargs=kwargs, error=str(exc),
    )
    alert_oncall(task_name, exc)

# In config — route failed tasks
from celery.signals import task_failure
@task_failure.connect
def on_task_failure(sender, task_id, exception, args, kwargs, **_):
    if sender.request.retries &gt;= sender.max_retries:
        handle_failed_task.delay(sender.name, task_id, args, kwargs, str(exception))</code></pre>
<p><strong>Design rules:</strong> tasks should be idempotent (retries may run twice); log at each retry; retry only transient errors (connection errors, 5xx, 429) and bail on permanent ones (4xx client errors); jitter prevents all clients retrying in sync; a DLQ + ops alert catches persistent failures. For critical workflows, consider Temporal or Airflow instead of raw Celery.</p>
'''

ANSWERS[63] = r'''
<p><strong>Scenario:</strong> stateless authentication in Flask — clients send a bearer token; server validates without a session lookup.</p>
<p><strong>Use <code>flask-jwt-extended</code>.</strong> Handles signing, verification, refresh tokens, CSRF for cookies.</p>
<pre><code>from flask import Flask, jsonify, request
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,
                                create_refresh_token, get_jwt_identity, get_jwt)
import datetime

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET"]         # rotate periodically
app.config["JWT_ACCESS_TOKEN_EXPIRES"]  = datetime.timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=7)
jwt = JWTManager(app)

revoked_tokens = set()                                           # Redis in production

@jwt.token_in_blocklist_loader
def check_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in revoked_tokens

@app.post("/auth/login")
def login():
    data = request.json
    user = User.authenticate(data["email"], data["password"])
    if not user:
        return jsonify({"error": "invalid_credentials"}), 401
    return jsonify({
        "access_token":  create_access_token(identity=user.id, additional_claims={"role": user.role}),
        "refresh_token": create_refresh_token(identity=user.id),
    })

@app.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    return jsonify({"access_token": create_access_token(identity=get_jwt_identity())})

@app.post("/auth/logout")
@jwt_required()
def logout():
    revoked_tokens.add(get_jwt()["jti"])
    return jsonify({"ok": True})

@app.get("/api/profile")
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    return jsonify(User.objects.get(id=user_id).as_dict())</code></pre>
<p><strong>Security essentials:</strong> HS256 or RS256 (asymmetric, better for multi-service); short-lived access tokens (~15 min) + refresh tokens; revocation list in Redis keyed by <code>jti</code>; HTTPS only; never put secrets or PII inside the JWT (it's readable, just signed). Rotate signing keys with grace periods. For SPAs, store access token in memory, refresh token in httpOnly cookie.</p>
'''

ANSWERS[64] = r'''
<p><strong>Scenario:</strong> "users who liked X also liked Y" for an e-commerce or content site.</p>
<p><strong>Three algorithmic approaches, layer them:</strong></p>
<ol>
  <li><strong>Collaborative filtering</strong> — based on user-item interactions. Matrix factorization (<code>implicit</code> library, ALS algorithm) or nearest-neighbors.</li>
  <li><strong>Content-based</strong> — features of the items themselves. Cosine similarity on TF-IDF (text) or embeddings (<code>sentence-transformers</code>).</li>
  <li><strong>Hybrid</strong> — weighted combination; handles cold-start.</li>
</ol>
<pre><code># Implicit (implicit feedback — views, purchases)
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

# Build user-item matrix: rows=users, cols=items, values=interaction strength
interactions = Interaction.objects.values_list("user_id", "item_id", "weight")
matrix = csr_matrix(...)

model = AlternatingLeastSquares(factors=64, iterations=20)
model.fit(matrix)

# Serve
def recommend_for(user_id, k=10):
    ids, scores = model.recommend(user_id, matrix[user_id], N=k, filter_already_liked_items=True)
    return Item.objects.filter(id__in=ids)

# Django view
from django.views.decorators.cache import cache_page
@cache_page(60 * 15)                # cache per-user recs for 15 min
def recommendations(request):
    recs = recommend_for(request.user.id)
    return JsonResponse({"items": [{"id": r.id, "title": r.title} for r in recs]})</code></pre>
<p><strong>Production realities:</strong></p>
<ul>
  <li>Retrain nightly or hourly on a batch job (Airflow/Celery). Model artifacts stored in S3.</li>
  <li>Serve from cached precomputed recs for active users; real-time scoring for long tail.</li>
  <li>Cold-start (new users/items) — fall back to popularity or content-based.</li>
  <li>Measure with offline metrics (NDCG, MAP) and online A/B tests (CTR, conversion).</li>
</ul>
<p>Managed services (Amazon Personalize, Google Recommendations AI) short-circuit a lot of engineering work.</p>
'''

ANSWERS[65] = r'''
<p><strong>Scenario:</strong> decouple slow work from request handling using a DIY queue before adopting Celery — useful for learning or minimal dependencies.</p>
<pre><code># Enqueue (in a Flask/Django view)
import redis, json, uuid

r = redis.Redis()

def enqueue_job(kind: str, payload: dict, *, priority: int = 5) -&gt; str:
    job_id = str(uuid.uuid4())
    job = {"id": job_id, "kind": kind, "payload": payload}
    # Priority via multiple lists (lower = more urgent)
    r.lpush(f"jobs:p{priority}", json.dumps(job))
    r.hset("job_status", job_id, "queued")
    return job_id

# Worker
import signal, time

running = True
def stop(*_): globals().update(running=False)
signal.signal(signal.SIGTERM, stop)

HANDLERS = {"email": send_email, "resize_image": resize_image}

def worker():
    while running:
        # BLPOP across priority queues, blocking up to 5s
        result = r.blpop(["jobs:p1", "jobs:p5", "jobs:p9"], timeout=5)
        if not result:
            continue
        _, raw = result
        job = json.loads(raw)
        r.hset("job_status", job["id"], "running")
        try:
            handler = HANDLERS[job["kind"]]
            handler(**job["payload"])
            r.hset("job_status", job["id"], "done")
        except Exception as e:
            r.hset("job_status", job["id"], f"failed: {e}")
            r.lpush("jobs:dead", raw)    # dead-letter
    r.close()</code></pre>
<p><strong>Limitations vs Celery:</strong> no scheduled/periodic tasks, no built-in retries, no result backend, no routing. For anything beyond a prototype, use <strong>RQ</strong> (redis-queue, simpler than Celery) or <strong>Celery</strong> with Redis broker. The DIY version is educational — know when to graduate.</p>
'''

ANSWERS[66] = r'''
<p><strong>Scenario:</strong> Django sessions should expire after inactivity (not just absolute time), force logout on password change, and invalidate on suspicious activity.</p>
<pre><code># settings.py — default Django session behavior
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"     # speed + persistence
SESSION_COOKIE_AGE = 60 * 60 * 2                                   # 2 hours absolute
SESSION_SAVE_EVERY_REQUEST = True                                  # refreshes cookie on each hit
SESSION_COOKIE_SECURE = True                                       # HTTPS only
SESSION_COOKIE_HTTPONLY = True                                     # JS cannot read
SESSION_COOKIE_SAMESITE = "Lax"

# Idle-timeout middleware — in addition to absolute SESSION_COOKIE_AGE
from django.utils import timezone
from django.contrib.auth import logout

class IdleTimeoutMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    MAX_IDLE_SECONDS = 30 * 60

    def __call__(self, request):
        if request.user.is_authenticated:
            last = request.session.get("last_activity")
            now_ts = timezone.now().timestamp()
            if last and now_ts - last &gt; self.MAX_IDLE_SECONDS:
                logout(request)
                return redirect("/login?reason=idle")
            request.session["last_activity"] = now_ts
        return self.get_response(request)

# Force-logout all sessions on password change
from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def logout_on_password_change(sender, instance, **kwargs):
    if instance.tracker.has_changed("password"):
        Session.objects.filter(...).delete()     # scan or use django-user-sessions</code></pre>
<p><strong>Use <code>django-user-sessions</code></strong> for per-user session tracking and bulk revocation. Show users a "Active sessions" page with device/IP info and a logout button per device — security best practice. For stateless JWT tokens, use short lifetimes and a revocation list (see Q63).</p>
'''

ANSWERS[67] = r'''
<p><strong>Scenario:</strong> Django FileField should save to S3 (or GCS, Azure) instead of local filesystem, with private vs public files, signed URLs, and CDN integration.</p>
<pre><code># Use django-storages
# pip install django-storages[s3] boto3
INSTALLED_APPS += ["storages"]

# For PUBLIC static assets
STORAGES = {
    "default":        {"BACKEND": "apps.storage.PrivateMediaStorage"},
    "staticfiles":    {"BACKEND": "storages.backends.s3.S3StaticStorage"},
}
AWS_S3_REGION_NAME = "us-east-1"
AWS_STORAGE_BUCKET_NAME = "my-app-media"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = "cdn.example.com"          # CloudFront distribution

# apps/storage.py — private files with signed URLs
from storages.backends.s3 import S3Storage

class PrivateMediaStorage(S3Storage):
    default_acl = "private"
    querystring_auth = True
    querystring_expire = 3600                      # 1-hour signed URLs
    file_overwrite = False
    location = "media"                             # key prefix

class PublicMediaStorage(S3Storage):
    default_acl = "public-read"
    querystring_auth = False
    custom_domain = "cdn.example.com"
    location = "public"

# Models
class Document(models.Model):
    file = models.FileField(storage=PrivateMediaStorage())

class ProductImage(models.Model):
    image = models.ImageField(storage=PublicMediaStorage())

# Usage
doc.file.url          # https://bucket.s3.../media/abc.pdf?AWSAccessKeyId=...&amp;Expires=...
product.image.url     # https://cdn.example.com/public/x.jpg  (no signature)</code></pre>
<p><strong>For very large files (>100 MB):</strong> use presigned POST URLs — the client uploads directly to S3, bypassing your app server. For custom backends, implement <code>django.core.files.storage.Storage</code> subclass with <code>_save</code>, <code>_open</code>, <code>url</code>, <code>exists</code>, <code>delete</code>. Always set a Content Security Policy and scan uploaded files for malware (ClamAV).</p>
'''

ANSWERS[68] = r'''
<p><strong>Scenario:</strong> push notifications to connected users in a Flask app — messages, alerts, live feeds.</p>
<p><strong>Use <code>flask-socketio</code>.</strong> Wraps Socket.IO protocol (WebSocket + fallbacks); integrates with Redis for multi-process fanout.</p>
<pre><code># pip install flask-socketio redis
from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_login import current_user

app = Flask(__name__)
socketio = SocketIO(app, message_queue="redis://redis:6379/0", cors_allowed_origins="*")

@socketio.on("connect")
def on_connect():
    if not current_user.is_authenticated:
        return False                                 # reject
    join_room(f"user:{current_user.id}")

@socketio.on("disconnect")
def on_disconnect():
    leave_room(f"user:{current_user.id}")

# Send to specific user from anywhere in the codebase
def notify_user(user_id: int, notification: dict):
    # Uses the same Redis message queue; works from Celery workers, other processes
    sio = SocketIO(message_queue="redis://redis:6379/0")
    sio.emit("notification", notification, room=f"user:{user_id}")

# Example: triggered from a business-logic function
def on_order_shipped(order):
    notify_user(order.user_id, {
        "type": "order_shipped",
        "message": f"Order #{order.id} has shipped!",
        "url": f"/orders/{order.id}",
    })

# Run: socketio.run(app) instead of app.run()
if __name__ == "__main__":
    socketio.run(app)</code></pre>
<p><strong>Production deployment:</strong> Eventlet or Gevent workers (Gunicorn: <code>-k eventlet</code>); Redis as pub/sub backbone; sticky sessions at the load balancer (WebSocket connections are long-lived and must stay on one worker). For browser fallback: Socket.IO handles long-polling automatically. Pair with a <strong>persistent store</strong> — users may be offline; save notifications to DB and deliver on reconnect.</p>
'''

ANSWERS[69] = r'''
<p><strong>Scenario:</strong> DRF API needs consistent error responses, field-level validation, and aggregated error arrays — both for API consumers and mobile clients.</p>
<pre><code># settings.py
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.api.exceptions.custom_exception_handler",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# apps/api/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

log = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:              # non-DRF exception = 500
        log.exception("unhandled_exception", extra={"view": context["view"].__class__.__name__})
        return Response({
            "error": {"code": "internal_error", "message": "Something went wrong"}
        }, status=500)

    # Flatten DRF's nested validation errors
    if isinstance(response.data, dict):
        errors = []
        for field, msgs in response.data.items():
            msgs = msgs if isinstance(msgs, list) else [msgs]
            for msg in msgs:
                errors.append({"field": field, "code": getattr(msg, "code", "invalid"),
                               "message": str(msg)})
        response.data = {"error": {"code": "validation_error", "errors": errors}}
    return response

# Serializers — use Django's validators + DRF validators
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "body", "tags"]

    def validate_title(self, value):
        if Post.objects.filter(title=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("title must be unique", code="duplicate")
        return value

    def validate(self, attrs):
        if attrs.get("publish_at") and attrs["publish_at"] &lt; timezone.now():
            raise serializers.ValidationError({"publish_at": "must be in the future"})
        return attrs</code></pre>
<p><strong>Response shape:</strong> consistent <code>{"error": {...}}</code> envelope with <code>code</code>, <code>message</code>, and a <code>errors</code> array for field-level issues. Document every error code. Include a correlation ID (request ID) in 5xx responses for support. Log structured data — never crash silently.</p>
'''

ANSWERS[70] = r'''
<p><strong>Scenario:</strong> capture user events — page views, clicks, form submissions — for analytics, debugging, and security audit.</p>
<p><strong>Three tiers by resolution and volume:</strong></p>
<table>
<tr><th>Tier</th><th>Tools</th><th>Use case</th></tr>
<tr><td>Web analytics</td><td>Google Analytics, Plausible, Mixpanel</td><td>Marketing, funnels</td></tr>
<tr><td>Product events</td><td>Custom event pipeline (Kafka + ClickHouse)</td><td>Feature usage, cohort analysis</td></tr>
<tr><td>Security audit</td><td>DB append-only table</td><td>Compliance, forensics</td></tr>
</table>
<pre><code># Security audit — synchronous, always written
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)            # "login", "password_change", ...
    ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["user", "action", "-created_at"])]

# Middleware
class ActivityMiddleware:
    LOGGED = {"/login", "/logout", "/profile/edit"}

    def __call__(self, request):
        response = self.get_response(request)
        if request.path in self.LOGGED and request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=request.path.strip("/").replace("/", "_"),
                ip=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                details={"method": request.method, "status": response.status_code},
            )
        return response

# Product events — async, high volume
import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda v: json.dumps(v).encode(),
)

def track_event(user_id: int, event_name: str, properties: dict):
    producer.send("events", {
        "user_id": user_id, "event": event_name,
        "properties": properties, "timestamp": time.time(),
    })</code></pre>
<p><strong>Privacy:</strong> GDPR/CCPA compliance — no PII in event names, honor deletion requests, anonymize IPs. Batch events client-side before sending. For server-side tracking, use a dedicated table partitioned by date for easy retention management.</p>
'''

ANSWERS[71] = r'''
<p><strong>Scenario:</strong> admin reporting dashboard — charts, KPIs, filters — for a Django app, served alongside the main product.</p>
<p><strong>Architecture:</strong> Django provides data APIs; a separate front-end (React/Vue) renders interactive visualizations. Or use Django templates with Chart.js for simpler needs.</p>
<pre><code># Django: DRF endpoints with aggregation
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDay
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

@api_view(["GET"])
@permission_classes([IsAdminUser])
def revenue_by_day(request):
    start = parse_date(request.GET["start"])
    end = parse_date(request.GET["end"])
    data = (Order.objects
        .filter(created_at__range=(start, end), status="completed")
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(revenue=Sum("total"), count=Count("id"), avg_order=Avg("total"))
        .order_by("day"))
    return Response(list(data))

@api_view(["GET"])
@permission_classes([IsAdminUser])
def conversion_funnel(request):
    return Response({
        "visited":    User.objects.filter(...).count(),
        "signed_up":  User.objects.filter(signup_complete=True).count(),
        "purchased":  User.objects.filter(orders__isnull=False).distinct().count(),
    })</code></pre>
<p><strong>Performance tips:</strong></p>
<ul>
  <li>Precompute daily aggregates into a <code>DailyMetrics</code> table via a nightly Celery task. Dashboard queries hit that, not raw transactions.</li>
  <li>Cache per-filter results (Redis, 5-min TTL) keyed by filter params hash.</li>
  <li>For very large datasets, materialized views (Postgres) or a separate warehouse (BigQuery, Snowflake, ClickHouse) via <code>dbt</code>.</li>
  <li>Use Metabase or Superset if your team wants SQL-driven dashboards without custom UI.</li>
</ul>
<p>On the front-end, Recharts (React) or Chart.js are lightweight choices; Plotly for scientific/interactive. Lazy-load chart components, paginate tables, debounce filter inputs.</p>
'''

ANSWERS[72] = r'''
<p><strong>Scenario:</strong> scrape multiple sites at scale (e.g., price monitoring across 50 retailers). Use Scrapy for robust framework, async I/O, and built-in retry/throttle.</p>
<pre><code># products_spider.py
import scrapy
from myproject.items import ProductItem

class ProductSpider(scrapy.Spider):
    name = "products"
    custom_settings = {
        "DOWNLOAD_DELAY": 1,                    # polite crawling
        "AUTOTHROTTLE_ENABLED": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "USER_AGENT": "PriceBot/1.0 (+https://example.com/bot)",
        "ROBOTSTXT_OBEY": True,
        "COOKIES_ENABLED": False,
        "RETRY_TIMES": 3,
    }
    start_urls = ["https://store.example.com/products?page=1"]

    def parse(self, response):
        for product in response.css("div.product"):
            yield ProductItem(
                name=product.css("h2::text").get(),
                price=product.css(".price::text").re_first(r"[\d.]+"),
                url=response.urljoin(product.css("a::attr(href)").get()),
            )
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

# pipelines.py — clean, validate, store
class PriceCleanupPipeline:
    def process_item(self, item, spider):
        item["price"] = float(item["price"].replace(",", ""))
        return item

class SaveToDatabasePipeline:
    def open_spider(self, spider):
        self.conn = psycopg2.connect(...)
    def close_spider(self, spider):
        self.conn.close()
    def process_item(self, item, spider):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO products (name, price, url) VALUES (%s, %s, %s) ON CONFLICT (url) DO UPDATE SET price = EXCLUDED.price, updated_at = NOW()",
                        (item["name"], item["price"], item["url"]))
        return item</code></pre>
<p><strong>Production concerns:</strong> respect <code>robots.txt</code>; rotate user agents and proxies (<code>scrapy-rotating-proxies</code>) for large-scale; detect bans and back off; use Splash or Playwright (<code>scrapy-playwright</code>) for JS-heavy sites; schedule with Scrapyd or Celery; store raw HTML in S3 for reprocessing. Legal: check ToS, copyright, CFAA; prefer official APIs when available.</p>
'''

ANSWERS[73] = r'''
<p><strong>Scenario:</strong> users upload files concurrently — images, documents — that are large, slow, and eat memory if held in RAM.</p>
<pre><code>from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os, uuid

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024    # 100 MB hard cap
UPLOAD_DIR = "/var/uploads"
ALLOWED = {"pdf", "jpg", "jpeg", "png", "webp"}

def allowed_file(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED

@app.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "no_file"}), 400
    file = request.files["file"]
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "invalid_type"}), 400

    # Werkzeug streams directly to a temp file — safe for large uploads
    safe_name = secure_filename(file.filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    unique = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, unique)
    file.save(path)                        # streams to disk, not RAM

    # Offload heavy processing to Celery — returns immediately
    process_upload.delay(path, file.mimetype)
    return jsonify({"id": unique, "status": "processing"}), 202</code></pre>
<p><strong>Concurrency strategies:</strong></p>
<ul>
  <li><strong>WSGI workers:</strong> <code>gunicorn -w 4 -k gthread --threads 8</code> — 4 processes × 8 threads each. Uploads are I/O-bound, so threads work.</li>
  <li><strong>Async alternative:</strong> Quart or FastAPI with async file handling — one process handles thousands of concurrent uploads.</li>
  <li><strong>Direct-to-S3:</strong> best for very large files. Client gets a presigned POST URL and uploads directly to S3, never touching your app server.</li>
  <li><strong>Resumable uploads:</strong> <code>tus.io</code> protocol with <code>flask-tus</code> for network-interrupted uploads (mobile, large files).</li>
</ul>
<p>Always validate file type by content (<code>python-magic</code>) in addition to extension — attackers can rename <code>exploit.php</code> to <code>photo.jpg</code>. Scan for malware (ClamAV) before making files publicly accessible.</p>
'''

ANSWERS[74] = r'''
<p><strong>Scenario:</strong> Django app with admins, editors, viewers — RBAC where users have roles and roles have permissions.</p>
<p><strong>Django ships with a permission system</strong> (Groups + Permissions) that works well for straightforward roles.</p>
<pre><code># Use Django's built-in Group model as roles
from django.contrib.auth.models import Group, Permission

# Define permissions on models (Django auto-creates add/change/delete/view per model)
# Create roles
editors = Group.objects.create(name="editors")
editors.permissions.add(
    Permission.objects.get(codename="add_post"),
    Permission.objects.get(codename="change_post"),
    Permission.objects.get(codename="view_post"),
)
user.groups.add(editors)

# Check permissions
@permission_required("blog.change_post", raise_exception=True)
def edit_post(request, id): ...

# Object-level permissions — "Alice can edit her OWN posts but not Bob's"
# Use django-guardian
from guardian.shortcuts import assign_perm, get_perms

post = Post.objects.create(...)
assign_perm("change_post", user, post)       # per-instance permission

if user.has_perm("change_post", post):
    ...

# Custom Role model for richer hierarchy
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField("Permission")
    parent = models.ForeignKey("self", null=True, on_delete=models.SET_NULL)
    # Inherits parent's permissions

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    scope = models.CharField(max_length=50, blank=True)      # e.g. "team:42"
    class Meta:
        unique_together = ("user", "role", "scope")</code></pre>
<p><strong>Design decisions:</strong> start with Django's built-in groups and permissions for simple cases; move to <code>django-guardian</code> for per-object; only build a custom model if you need role hierarchies, time-bounded roles, or scope-restricted roles (e.g., "editor for team X only"). Always check permissions server-side — never trust client-side role data. Log permission changes to the audit table.</p>
'''

ANSWERS[75] = r'''
<p><strong>Scenario:</strong> structured logs for a web app — JSON-formatted, centralized, searchable, with request correlation IDs.</p>
<pre><code># settings.py — structured logging config
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {"levelname": "level"},
        },
    },
    "filters": {
        "request_id": {"()": "apps.logging.filters.RequestIDFilter"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json",
                    "filters": ["request_id"]},
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {"level": "WARNING"},    # avoid SQL noise
    },
}
logging.config.dictConfig(LOGGING)

# apps/logging/middleware.py — attach correlation IDs
import logging, uuid, threading

_local = threading.local()

def get_request_id(): return getattr(_local, "request_id", None)

class RequestIDMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        _local.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = _local.request_id
        return response

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True

# Usage throughout the app
log = logging.getLogger(__name__)
log.info("order_created", extra={"order_id": order.id, "user_id": request.user.id, "amount": order.total})</code></pre>
<p><strong>Ship logs to a central system:</strong> ELK (Elasticsearch + Logstash + Kibana), Grafana Loki, Datadog, Splunk. Format as JSON so the aggregator can parse fields. Include correlation IDs across all services in a request chain (OpenTelemetry standardizes this). Never log passwords, tokens, or PII. Use log levels deliberately: <code>DEBUG</code> (verbose, off in prod), <code>INFO</code> (business events), <code>WARNING</code> (unexpected but recoverable), <code>ERROR</code> (failed operation), <code>CRITICAL</code> (system in peril).</p>
'''

ANSWERS[76] = r'''
<p><strong>Scenario:</strong> users need to export query results as CSV/Excel/JSON, and some exports are huge (millions of rows) so we can't hold them in memory.</p>
<p><strong>Approach:</strong> stream small exports synchronously with <code>StreamingHttpResponse</code>; offload large ones to Celery and email a download link when ready.</p>
<pre><code># Small, streamed CSV — memory stays flat
import csv
from django.http import StreamingHttpResponse

class Echo:
    """File-like object that the csv module can write into."""
    def write(self, value): return value

def export_csv(request):
    queryset = Order.objects.filter(user=request.user).iterator(chunk_size=2000)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    def rows():
        yield writer.writerow(["id", "created", "total"])
        for o in queryset:
            yield writer.writerow([o.id, o.created.isoformat(), o.total])

    response = StreamingHttpResponse(rows(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'
    return response

# Large export — offload to Celery, email link when done
@shared_task
def generate_export(user_id: int, filters: dict):
    path = f"/exports/{uuid.uuid4()}.csv.gz"
    with gzip.open(default_storage.path(path), "wt", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created", "total"])
        for o in Order.objects.filter(**filters).iterator(chunk_size=5000):
            writer.writerow([o.id, o.created.isoformat(), o.total])
    url = default_storage.url(path)
    send_mail("Your export is ready", f"Download: {url}",
              "no-reply@app.com", [User.objects.get(pk=user_id).email])
</code></pre>
<p><strong>Key details:</strong> <code>.iterator(chunk_size=N)</code> avoids loading the whole queryset; <code>StreamingHttpResponse</code> pushes bytes as they're generated so the user sees a download start immediately. For Excel at scale, use <code>xlsxwriter</code> in "constant memory" mode. Store completed exports with signed URLs that expire in 24–48 hours.</p>
'''

ANSWERS[77] = r'''
<p><strong>Scenario:</strong> chat app where messages must arrive instantly — no polling. Django Channels (or FastAPI's WebSockets) + Redis as a message broker scales cleanly.</p>
<pre><code># Django Channels consumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room = f"room_{self.scope['url_route']['kwargs']['room_id']}"
        # Auth check
        if self.scope["user"].is_anonymous:
            return await self.close(code=4401)
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

    async def receive_json(self, content):
        # Persist first, then broadcast
        msg = await database_sync_to_async(Message.objects.create)(
            room_id=self.room, user=self.scope["user"], text=content["text"][:2000],
        )
        await self.channel_layer.group_send(self.room, {
            "type": "chat.message",
            "id": msg.id, "user": self.scope["user"].username,
            "text": msg.text, "at": msg.created.isoformat(),
        })

    async def chat_message(self, event):
        # Sent to every client in the room
        await self.send_json(event)

# settings.py
CHANNEL_LAYERS = {"default": {
    "BACKEND": "channels_redis.core.RedisChannelLayer",
    "CONFIG": {"hosts": [("redis", 6379)]},
}}
</code></pre>
<p><strong>Design notes:</strong> Redis pub/sub makes the channel layer work across workers — any gunicorn/daphne process can send a message and all subscribers receive it. Persist before broadcasting so reconnecting clients can fetch history. Add per-user rate limits (e.g., 10 msgs/sec via Redis counter) to prevent abuse. For 10K+ concurrent connections, run daphne/uvicorn behind a reverse proxy and horizontally scale.</p>
'''

ANSWERS[78] = r'''
<p><strong>Scenario:</strong> secure password reset — email a time-limited, single-use link.</p>
<p><strong>Django ships with this out of the box</strong> via <code>django.contrib.auth.views.PasswordResetView</code>. Use it unless you have a reason not to.</p>
<pre><code># urls.py — four built-in views handle the full flow
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("password_reset/",  auth_views.PasswordResetView.as_view(
        email_template_name="email/reset.html",
        success_url="/password_reset/done/"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view()),
    path("reset/&lt;uidb64&gt;/&lt;token&gt;/", auth_views.PasswordResetConfirmView.as_view(
        success_url="/reset/done/"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view()),
]

# Custom API version (DRF)
class PasswordResetAPI(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email__iexact=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f"https://app.com/reset/{uid}/{token}/"
            send_mail("Reset your password", f"Click: {link}",
                      "no-reply@app.com", [email])
        except User.DoesNotExist:
            pass  # never reveal whether email exists
        return Response({"detail": "If that email exists, a reset link was sent."})
</code></pre>
<p><strong>Security essentials:</strong> tokens are HMAC-signed and embed a timestamp — they auto-expire (default 3 days, <code>PASSWORD_RESET_TIMEOUT</code>). Always respond with the same message whether the email exists or not (prevents user enumeration). Rate-limit by IP to stop abuse. After successful reset, invalidate all existing sessions for that user and send a "password was changed" confirmation email to the <em>old</em> address too.</p>
'''

ANSWERS[79] = r'''
<p><strong>Scenario:</strong> product catalog lives in service A, inventory in service B, analytics in service C — all must stay eventually consistent without a distributed transaction.</p>
<p><strong>Approach:</strong> event-driven sync with a broker (Kafka/RabbitMQ) + per-service idempotent consumers + the <strong>outbox pattern</strong>.</p>
<pre><code># Producer side — outbox table in same DB as the domain data
class Outbox(models.Model):
    aggregate = models.CharField(max_length=64)     # "product"
    event_type = models.CharField(max_length=64)    # "product.updated"
    payload = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True)

def update_product(product_id: int, **fields):
    with transaction.atomic():
        p = Product.objects.select_for_update().get(pk=product_id)
        for k, v in fields.items():
            setattr(p, k, v)
        p.save()
        Outbox.objects.create(aggregate="product", event_type="product.updated",
                              payload={"id": p.id, **fields})
    # Separate relay process reads outbox → publishes to Kafka → marks sent

# Consumer side — idempotent
def handle_product_updated(msg):
    event_id = msg.headers["event-id"]
    if ProcessedEvent.objects.filter(event_id=event_id).exists():
        return  # already processed
    with transaction.atomic():
        Inventory.objects.update_or_create(
            product_id=msg.value["id"], defaults={"name": msg.value["name"]})
        ProcessedEvent.objects.create(event_id=event_id)
</code></pre>
<p><strong>Why this pattern:</strong> publishing inside the same DB transaction as the write (via outbox) guarantees the event is never lost if the broker is down. A relay worker reads outbox rows and publishes asynchronously. Consumers dedupe on event ID for at-least-once semantics. For strong ordering, partition by aggregate ID. Distributed transactions (2PC) are tempting but brittle at scale — eventual consistency via events is the proven approach (LinkedIn, Uber, every major microservice shop).</p>
'''

ANSWERS[80] = r'''
<p><strong>Scenario:</strong> users want to query data with syntax like <code>price &gt; 100 AND status:active</code> without exposing raw SQL.</p>
<p><strong>Approach:</strong> parse the input to an AST, validate against an allowlist of fields/operators, then translate to a Django <code>Q</code> object.</p>
<pre><code># Use a parser generator — lark makes this simple
from lark import Lark, Transformer
from django.db.models import Q

GRAMMAR = r"""
start: expr
expr: expr "AND" expr -> and_
    | expr "OR" expr  -> or_
    | "(" expr ")"
    | comparison
comparison: CNAME OP value
value: SIGNED_NUMBER | ESCAPED_STRING | CNAME
OP: "&gt;" | "&lt;" | "=" | ":"
%import common (CNAME, SIGNED_NUMBER, ESCAPED_STRING, WS)
%ignore WS
"""

ALLOWED = {"price": "price", "status": "status", "name": "name__icontains"}

class ToQ(Transformer):
    def and_(self, args): return args[0] &amp; args[1]
    def or_(self, args):  return args[0] | args[1]
    def comparison(self, args):
        field, op, val = args[0].value, args[1].value, args[2].children[0]
        if field not in ALLOWED:
            raise ValueError(f"Unknown field: {field}")
        lookup = ALLOWED[field]
        if op == "&gt;":   return Q(**{f"{lookup}__gt": val})
        if op == "&lt;":   return Q(**{f"{lookup}__lt": val})
        return Q(**{lookup: val})

parser = Lark(GRAMMAR, parser="lalr", transformer=ToQ())
q = parser.parse('price &gt; 100 AND status = "active"')
Product.objects.filter(q)
</code></pre>
<p><strong>Safety:</strong> never interpolate raw strings into queries. A proper parser + field allowlist prevents injection and accidental access to sensitive columns. Limit query depth/length to prevent DoS. For simpler needs, <code>django-filter</code> or DRF's <code>SearchFilter</code> covers 80% of use cases — only build a custom language when users genuinely need boolean composition and comparison operators.</p>
'''

ANSWERS[81] = r'''
<p><strong>Scenario:</strong> Flask API needs rate limiting — e.g., 100 requests/hour/user — to prevent abuse.</p>
<p><strong>Approach:</strong> sliding-window counter in Redis. The <code>Flask-Limiter</code> library wraps this cleanly.</p>
<pre><code>from flask import Flask, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

def key_func():
    # Prefer authenticated user ID over IP (IP is shared behind NAT/proxies)
    return getattr(g, "user_id", None) or get_remote_address()

limiter = Limiter(app=app, key_func=key_func,
                  storage_uri="redis://redis:6379",
                  strategy="moving-window")  # more accurate than fixed-window

@app.route("/api/search")
@limiter.limit("100 per hour")
def search():
    return {"results": []}

@app.route("/api/expensive")
@limiter.limit("10 per minute; 100 per day")
def expensive(): ...

# Manual version — for custom logic
import redis, time
r = redis.Redis()

def check_rate_limit(user_id: str, limit: int = 100, window: int = 3600) -&gt; bool:
    now = time.time()
    key = f"ratelimit:{user_id}"
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)  # drop old entries
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)                              # how many in window?
    pipe.expire(key, window)
    _, _, count, _ = pipe.execute()
    return count &lt;= limit
</code></pre>
<p><strong>Trade-offs:</strong> fixed-window (simpler, resets cleanly) vs sliding-window (smoother, prevents burst at boundaries). The ZSET approach above is exact-sliding at O(log n) per request. For massive scale, token-bucket with atomic Lua scripts avoids the ZSET memory. Always return <code>429 Too Many Requests</code> with <code>Retry-After</code> and <code>X-RateLimit-Remaining</code> headers so clients can back off intelligently.</p>
'''

ANSWERS[82] = r'''
<p><strong>Scenario:</strong> deploy a trained sklearn / PyTorch model behind a REST API in a Django app with versioning, monitoring, and fast inference.</p>
<pre><code># Load the model once at startup — not per request
# apps/ml/apps.py
class MLConfig(AppConfig):
    name = "apps.ml"
    def ready(self):
        import joblib
        self.model = joblib.load(settings.MODEL_PATH)  # cached in memory
        self.model_version = os.environ.get("MODEL_VERSION", "v1")

# views.py — DRF endpoint
class PredictView(APIView):
    def post(self, request):
        try:
            features = PredictInputSerializer(data=request.data)
            features.is_valid(raise_exception=True)
            model = apps.get_app_config("ml").model
            X = np.array([[features.validated_data[k] for k in FEATURE_ORDER]])

            with timer("model.predict"):
                prediction = model.predict(X)[0]
                confidence = float(model.predict_proba(X).max())

            # Log for monitoring (drift detection, A/B tests)
            PredictionLog.objects.create(
                model_version=apps.get_app_config("ml").model_version,
                features=features.validated_data,
                prediction=prediction, confidence=confidence)

            return Response({"prediction": prediction, "confidence": confidence,
                             "model_version": apps.get_app_config("ml").model_version})
        except ValidationError:
            return Response({"error": "bad input"}, status=400)
</code></pre>
<p><strong>Production concerns:</strong> load the model once (not per request) — saves seconds on heavy models. Validate input strictly via serializers. Log every prediction with the model version for drift detection and audit. For high-throughput / GPU inference, put the model behind a dedicated service (TorchServe, BentoML, Triton) and have Django call it over gRPC. Blue-green deploy new model versions by env var so you can roll back instantly if accuracy drops.</p>
'''

ANSWERS[83] = r'''
<p><strong>Scenario:</strong> users upload CSVs with millions of rows — we need to validate, transform, and insert without OOMing or locking tables for hours.</p>
<p><strong>Approach:</strong> stream the file in chunks, validate per row, use PostgreSQL <code>COPY</code> (or <code>bulk_create</code>) for the insert.</p>
<pre><code>import pandas as pd
from django.db import transaction, connection

def import_csv(file_path: str, user_id: int) -&gt; ImportJob:
    job = ImportJob.objects.create(user_id=user_id, status="running")
    errors = []
    inserted = 0

    try:
        # Stream in chunks — never loads full file
        for chunk_num, chunk in enumerate(pd.read_csv(
                file_path, chunksize=10_000, dtype={"sku": str})):

            chunk = chunk.dropna(subset=["sku", "name"])
            chunk["price"] = pd.to_numeric(chunk["price"], errors="coerce")
            valid = chunk[chunk["price"].notna() &amp; (chunk["price"] &gt; 0)]
            invalid = chunk[~chunk.index.isin(valid.index)]
            for _, row in invalid.head(100).iterrows():
                errors.append({"row": int(row.name), "reason": "invalid price"})

            with transaction.atomic():
                Product.objects.bulk_create(
                    [Product(sku=r.sku, name=r.name, price=r.price)
                     for r in valid.itertuples()],
                    ignore_conflicts=True, batch_size=1000)
            inserted += len(valid)
            job.progress = inserted
            job.save(update_fields=["progress"])

        job.status = "success"
    except Exception as e:
        job.status = "failed"; job.error = str(e)
    job.errors = errors[:1000]  # cap
    job.save()
    return job

# Fastest possible — Postgres COPY FROM
with connection.cursor() as cur:
    with open(file_path) as f:
        cur.copy_expert("COPY products(sku,name,price) FROM STDIN WITH CSV HEADER", f)
</code></pre>
<p><strong>Key techniques:</strong> chunked reading keeps memory flat regardless of file size. <code>bulk_create</code> with <code>ignore_conflicts</code> handles duplicates gracefully. For raw speed on PostgreSQL, <code>COPY</code> is ~10× faster than <code>bulk_create</code> — but skips Django-level validation, so pre-validate separately. Run the import as a Celery task, track progress in the DB, and let users poll a status endpoint.</p>
'''

ANSWERS[84] = r'''
<p><strong>Scenario:</strong> users upload contracts/invoices; need to keep every version, show diff history, and allow rollback.</p>
<pre><code># Versioned file model
class Document(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    current_version = models.ForeignKey(
        "DocumentVersion", null=True, on_delete=models.SET_NULL, related_name="+")

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    version = models.PositiveIntegerField()
    file = models.FileField(upload_to=version_path)   # immutable after write
    sha256 = models.CharField(max_length=64, db_index=True)  # dedupe identical uploads
    size = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=500, blank=True)

    class Meta:
        unique_together = [("document", "version")]
        ordering = ["-version"]

def upload_new_version(doc: Document, f, user, note=""):
    digest = hashlib.sha256(b"".join(chunk for chunk in f.chunks())).hexdigest()
    f.seek(0)

    # Dedupe — don't store the same bytes twice
    existing = DocumentVersion.objects.filter(document=doc, sha256=digest).first()
    if existing:
        return existing

    with transaction.atomic():
        next_version = (doc.versions.aggregate(Max("version"))["version__max"] or 0) + 1
        v = DocumentVersion.objects.create(
            document=doc, version=next_version, file=f,
            sha256=digest, size=f.size, uploaded_by=user, note=note)
        doc.current_version = v
        doc.save(update_fields=["current_version"])
    return v

def rollback(doc, to_version: int):
    v = doc.versions.get(version=to_version)
    doc.current_version = v
    doc.save(update_fields=["current_version"])
</code></pre>
<p><strong>Key design choices:</strong> versions are immutable — never edited in place. SHA-256 content hash enables dedup (same file, multiple docs → one blob). Store the <em>pointer</em> to current version on the parent, making rollback atomic. For text diffs, generate and cache side-by-side diffs with <code>difflib</code>. For retention, add a cleanup task that deletes versions older than N days where <em>other</em> rows reference the same hash.</p>
'''

ANSWERS[85] = r'''
<p><strong>Scenario:</strong> let users submit feedback with ratings, screenshots, and categorized topics — routed to the right team, tracked to resolution.</p>
<pre><code># models.py
class Feedback(models.Model):
    CATEGORY = [("bug", "Bug"), ("feature", "Feature request"),
                ("ux", "UX"), ("other", "Other")]
    STATUS = [("new", "New"), ("triaged", "Triaged"),
              ("in_progress", "In Progress"), ("resolved", "Resolved")]
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=20, choices=CATEGORY)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=5000)
    page_url = models.URLField(blank=True)         # context of the feedback
    user_agent = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="new")
    assigned_to = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

class FeedbackAttachment(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="feedback/%Y/%m/",
                            validators=[FileExtensionValidator(["png","jpg","pdf"])])

# API view — DRF
class FeedbackViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnlyForCreate]
    throttle_classes = [UserRateThrottle]   # 5/min per user

    def perform_create(self, serializer):
        fb = serializer.save(user=self.request.user if self.request.user.is_authenticated else None,
                             user_agent=self.request.META.get("HTTP_USER_AGENT", "")[:500])
        # Auto-route based on category
        fb.assigned_to = ROUTING.get(fb.category)
        fb.save(update_fields=["assigned_to"])
        # Notify team
        notify_team.delay(fb.id)
</code></pre>
<p><strong>Details worth thinking through:</strong> capture context (URL, user agent, app version) automatically — users rarely include it. Rate-limit submissions (spam + user accidentally clicking twice). Let users attach screenshots (but validate file type/size server-side). Integrate with the team's existing tools — Slack webhook for instant notification, auto-create Linear/Jira tickets for bugs. Aggregate ratings weekly into a dashboard to spot degradation.</p>
'''

ANSWERS[86] = r'''
<p><strong>Scenario:</strong> Flask API authenticates requests via API key or JWT — want centralized middleware rather than decorators on every route.</p>
<pre><code># Custom middleware using Flask's before_request hook
from functools import wraps
from flask import Flask, request, g, jsonify, abort
import jwt as pyjwt

app = Flask(__name__)
PUBLIC_PATHS = {"/health", "/login", "/register"}

@app.before_request
def authenticate():
    if request.path in PUBLIC_PATHS or request.method == "OPTIONS":
        return    # skip auth

    auth = request.headers.get("Authorization", "")
    api_key = request.headers.get("X-API-Key")

    if auth.startswith("Bearer "):
        token = auth[7:]
        try:
            payload = pyjwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
            g.user_id = payload["sub"]
            g.scopes = payload.get("scopes", [])
            g.auth_method = "jwt"
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "token expired"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "invalid token"}), 401
    elif api_key:
        key = ApiKey.query.filter_by(hash=hash_key(api_key), active=True).first()
        if not key:
            return jsonify({"error": "invalid api key"}), 401
        g.user_id = key.user_id
        g.scopes = key.scopes
        g.auth_method = "api_key"
        key.last_used = datetime.utcnow()
        db.session.commit()
    else:
        return jsonify({"error": "authentication required"}), 401

# Scope check decorator — layered on top of middleware
def requires_scope(scope):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kw):
            if scope not in g.scopes:
                abort(403)
            return fn(*args, **kw)
        return decorated
    return wrapper

@app.route("/admin/users")
@requires_scope("admin:read")
def list_users(): ...
</code></pre>
<p><strong>Why middleware:</strong> centralizes auth so every route is protected by default (fail closed). <code>before_request</code> runs before the view; returning a response short-circuits to the client. Always hash API keys in storage (never store plaintext). For JWT, use short expiry (15 min) + refresh tokens, and keep a revocation list in Redis for logout. Layer scope checks on top via decorators for fine-grained permissions.</p>
'''

ANSWERS[87] = r'''
<p><strong>Scenario:</strong> product catalog with 10M+ rows — users search by text, filter by 10+ facets, sort, paginate. SQL <code>LIKE</code> won't cut it.</p>
<p><strong>Approach:</strong> PostgreSQL full-text for simple needs, Elasticsearch/Meilisearch/OpenSearch for real search.</p>
<pre><code># PostgreSQL — works up to a few million rows, no extra infra
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.indexes import GinIndex

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    search_vector = SearchVectorField(null=True)    # denormalized
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [GinIndex(fields=["search_vector"])]

# Update the vector via trigger — keeps it in sync
# CREATE TRIGGER products_search_update BEFORE INSERT OR UPDATE
# ON products FOR EACH ROW EXECUTE FUNCTION
# tsvector_update_trigger(search_vector, 'pg_catalog.english', name, description);

def search(q: str, category=None, price_min=None, price_max=None, sort="relevance"):
    qs = Product.objects.all()
    if q:
        query = SearchQuery(q, config="english")
        qs = qs.annotate(rank=SearchRank("search_vector", query)).filter(search_vector=query)
        if sort == "relevance":
            qs = qs.order_by("-rank")
    if category:   qs = qs.filter(category=category)
    if price_min:  qs = qs.filter(price__gte=price_min)
    if price_max:  qs = qs.filter(price__lte=price_max)
    if sort == "price_asc":  qs = qs.order_by("price")
    return qs

# For real scale — Elasticsearch via django-elasticsearch-dsl
# Index products; search with aggregations for facets; &lt;50ms typical</code></pre>
<p><strong>When to step up:</strong> Postgres FTS handles maybe 5M rows before feeling slow. For multi-language, typo tolerance ("iphon" → "iphone"), synonyms, and real-time facet counts, use a dedicated engine. Meilisearch is the easiest; Elasticsearch the most powerful. Keep the search index in sync via Celery tasks on model save (or Postgres logical replication).</p>
'''

ANSWERS[88] = r'''
<p><strong>Scenario:</strong> Celery workers handle jobs of varying urgency — billing (critical), email (medium), analytics (low). Don't let slow analytics block urgent work.</p>
<p><strong>Approach:</strong> separate queues per priority + dedicated workers per queue.</p>
<pre><code># celery.py — route tasks to specific queues
from kombu import Queue

app.conf.task_queues = (
    Queue("critical"),
    Queue("default"),
    Queue("low"),
)
app.conf.task_routes = {
    "apps.billing.tasks.*":    {"queue": "critical"},
    "apps.emails.tasks.*":     {"queue": "default"},
    "apps.analytics.tasks.*":  {"queue": "low"},
}
app.conf.task_default_queue = "default"

# Start workers separately per queue:
#   celery -A proj worker -Q critical -n critical@%h --concurrency=10 --prefetch-multiplier=1
#   celery -A proj worker -Q default  -n default@%h  --concurrency=20
#   celery -A proj worker -Q low      -n low@%h      --concurrency=4

# Per-task priority within RabbitMQ (0-9, higher wins)
@shared_task(queue="critical", priority=9)
def charge_customer(invoice_id): ...

@shared_task(queue="low", priority=1)
def recompute_stats(): ...

# Rate-limit expensive tasks so they don't starve others
@shared_task(rate_limit="10/m")
def send_marketing_email(user_id): ...
</code></pre>
<p><strong>Key rules:</strong> always set <code>prefetch_multiplier=1</code> for critical queues — otherwise workers hoard tasks and can't release them. Use <code>task_acks_late=True</code> so tasks are only acked after successful completion (survives worker crashes). Scale critical-queue workers independently based on load. For RabbitMQ, declare the queue with <code>x-max-priority</code> to enable intra-queue priority. Monitor queue depth per priority (Flower / Prometheus) and alert when critical backs up.</p>
'''

ANSWERS[89] = r'''
<p><strong>Scenario:</strong> browser and mobile clients need real-time notifications (new message, like, friend request) without polling.</p>
<p><strong>Approach:</strong> Django Channels + Redis pub/sub, keyed per user.</p>
<pre><code># consumer.py
class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            return await self.close(code=4401)
        self.user_group = f"notif_user_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()
        # Send any unread notifications on connect
        unread = await get_unread(self.scope["user"])
        for n in unread:
            await self.send_json({"type": "notification", **n})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def notification(self, event):
        await self.send_json(event["payload"])

# Fire a notification from anywhere (views, signals, Celery)
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id: int, kind: str, data: dict):
    # Persist first — if user is offline, they see it on next connect
    notif = Notification.objects.create(user_id=user_id, kind=kind, data=data)
    # Push to live socket(s) if connected
    async_to_sync(get_channel_layer().group_send)(
        f"notif_user_{user_id}",
        {"type": "notification", "payload": {"id": notif.id, "kind": kind, **data}},
    )

# Example trigger
@receiver(post_save, sender=Message)
def message_notify(sender, instance, created, **kwargs):
    if created and instance.recipient_id:
        notify_user(instance.recipient_id, "message.new",
                    {"from": instance.sender.username, "preview": instance.text[:80]})
</code></pre>
<p><strong>Design notes:</strong> always persist before pushing — offline users need to see missed notifications when they return. The <code>group_send</code> reaches all open sockets for that user (multiple devices). Use <code>group_name = f"notif_user_{id}"</code> — never broadcast all notifications to everyone. For push to closed apps (mobile in background), bridge to APNs/FCM from the same <code>notify_user</code> function.</p>
'''

ANSWERS[90] = r'''
<p><strong>Scenario:</strong> DRF endpoints return long lists — need pagination that stays fast on very large offsets and supports infinite-scroll.</p>
<p><strong>Approach:</strong> offset pagination for small pages, cursor pagination for endless feeds.</p>
<pre><code># Built-in offset pagination — fine up to a few thousand pages
class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

# Cursor pagination — O(1) regardless of offset; required for infinite scroll
class FeedCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"    # must have a strict ordering; add -id tiebreaker
    cursor_query_param = "cursor"

    def get_ordering(self, request, queryset, view):
        return ("-created_at", "-id")

# Custom "keyset" pagination — most control
def paginated_feed(qs, cursor: str = None, page_size: int = 20):
    if cursor:
        # cursor = base64("{timestamp}_{id}")
        ts, last_id = decode_cursor(cursor)
        qs = qs.filter(Q(created_at__lt=ts) |
                       Q(created_at=ts, id__lt=last_id))
    items = list(qs.order_by("-created_at", "-id")[:page_size + 1])
    has_next = len(items) &gt; page_size
    items = items[:page_size]
    next_cursor = encode_cursor(items[-1].created_at, items[-1].id) if has_next else None
    return {"results": items, "next_cursor": next_cursor, "has_next": has_next}
</code></pre>
<p><strong>Why cursor beats offset at scale:</strong> <code>OFFSET 1000000</code> forces the DB to scan-and-discard a million rows — O(N) per page. Cursor (keyset) uses a WHERE clause against an indexed column — constant time. The cost: users can't jump to page 500, and adding/removing items mid-browse can cause duplicates or skips. For search results and archives, offset is fine. For social feeds, always use cursor.</p>
'''

ANSWERS[91] = r'''
<p><strong>Scenario:</strong> generate PDFs (invoices, reports, certificates) at scale — offload from the main app to keep it responsive.</p>
<pre><code># FastAPI microservice for PDF generation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import boto3, uuid

app = FastAPI()
templates = Environment(loader=FileSystemLoader("templates"), autoescape=True)
s3 = boto3.client("s3")

class InvoiceRequest(BaseModel):
    invoice_id: int
    customer: dict
    line_items: list[dict]
    total: float

@app.post("/render/invoice")
async def render_invoice(req: InvoiceRequest):
    try:
        html = templates.get_template("invoice.html").render(**req.model_dump())
        pdf_bytes = HTML(string=html).write_pdf()

        key = f"invoices/{req.invoice_id}/{uuid.uuid4()}.pdf"
        s3.put_object(Bucket="docs", Key=key, Body=pdf_bytes,
                      ContentType="application/pdf")
        url = s3.generate_presigned_url("get_object",
                Params={"Bucket": "docs", "Key": key}, ExpiresIn=3600)
        return {"url": url, "key": key}
    except Exception as e:
        raise HTTPException(500, str(e))

# Async version for concurrent requests
from concurrent.futures import ProcessPoolExecutor
executor = ProcessPoolExecutor(max_workers=4)

@app.post("/render/batch")
async def render_batch(invoices: list[InvoiceRequest]):
    loop = asyncio.get_event_loop()
    results = await asyncio.gather(*[
        loop.run_in_executor(executor, render_pdf, inv.model_dump())
        for inv in invoices])
    return {"results": results}
</code></pre>
<p><strong>Design choices:</strong> <strong>WeasyPrint</strong> (HTML/CSS→PDF) is easiest for template-driven docs; <strong>ReportLab</strong> for pixel-perfect layouts; <strong>Playwright</strong> headless Chrome for complex charts. PDF rendering is CPU-bound — use a <code>ProcessPoolExecutor</code> (not threads) and scale horizontally. Store the output in S3 with signed URLs rather than returning inline bytes. Add a queue (SQS/Celery) if generation takes seconds; otherwise synchronous is fine.</p>
'''

ANSWERS[92] = r'''
<p><strong>Scenario:</strong> Flask API surfaces aggregates — daily revenue, top products, user cohorts — across millions of rows. Raw queries every request is too slow.</p>
<p><strong>Approach:</strong> pre-compute with scheduled jobs; cache computed results; use rollup tables.</p>
<pre><code># Rollup table — updated nightly by a cron/Celery Beat job
class DailySales(db.Model):
    date = db.Column(db.Date, primary_key=True)
    total_revenue = db.Column(db.Numeric(12, 2))
    order_count = db.Column(db.Integer)
    unique_customers = db.Column(db.Integer)

def roll_up_yesterday():
    y = date.today() - timedelta(days=1)
    row = db.session.execute(text("""
        SELECT COALESCE(SUM(total),0) AS rev, COUNT(*) AS orders,
               COUNT(DISTINCT user_id) AS users
        FROM orders WHERE created::date = :d
    """), {"d": y}).one()
    db.session.merge(DailySales(date=y, total_revenue=row.rev,
                                order_count=row.orders,
                                unique_customers=row.users))
    db.session.commit()

# API serves from the rollup — milliseconds
@app.route("/metrics/daily")
def daily_metrics():
    start = request.args.get("from", default=date.today() - timedelta(days=30))
    end = request.args.get("to", default=date.today())
    cache_key = f"metrics:daily:{start}:{end}"
    if cached := redis.get(cache_key):
        return jsonify(json.loads(cached))
    data = [r.to_dict() for r in DailySales.query.filter(
        DailySales.date.between(start, end)).order_by(DailySales.date)]
    redis.setex(cache_key, 300, json.dumps(data))  # 5-min cache
    return jsonify(data)

# For real-time aggregates, Redis sorted sets or ClickHouse
</code></pre>
<p><strong>Three-tier strategy:</strong> (1) raw table for transactions, (2) rollup tables for common aggregates (hourly/daily), (3) Redis cache for recent API responses. For analytical workloads at scale, move to a columnar store (ClickHouse, Snowflake, BigQuery) — OLTP databases are optimized for row-level reads/writes and struggle with 100M-row SUMs. Use incremental updates (watermark-based) rather than full recomputes to keep rollups fresh.</p>
'''

ANSWERS[93] = r'''
<p><strong>Scenario:</strong> DRF API serving web + mobile + 3rd parties; need to evolve without breaking existing clients.</p>
<p><strong>Approach:</strong> URL-prefix versioning (<code>/api/v1/</code>, <code>/api/v2/</code>) — explicit, visible in logs, easy to route.</p>
<pre><code># settings.py
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
}

# urls.py
urlpatterns = [
    path("api/&lt;str:version&gt;/", include("api.urls")),
]

# One view, branching logic for serializer choice
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.version == "v2":
            return OrderSerializerV2    # includes new fields
        return OrderSerializerV1        # legacy shape

# Alternative: separate view files per version
# api/v1/views.py and api/v2/views.py — cleaner when versions diverge a lot

# Deprecation header on old versions
class DeprecationMiddleware:
    def __call__(self, request):
        response = self.get_response(request)
        if getattr(request, "version", None) == "v1":
            response["Deprecation"] = "true"
            response["Sunset"] = "Wed, 31 Dec 2026 23:59:59 GMT"
            response["Link"] = '&lt;/api/v2/&gt;; rel="successor-version"'
        return response
</code></pre>
<p><strong>Versioning strategies compared:</strong></p>
<table>
  <thead><tr><th>Style</th><th>Example</th><th>Pros</th><th>Cons</th></tr></thead>
  <tbody>
    <tr><td>URL path</td><td><code>/api/v2/users</code></td><td>Explicit, cacheable</td><td>URLs change</td></tr>
    <tr><td>Header</td><td><code>Accept: vnd.app.v2+json</code></td><td>Clean URLs</td><td>Harder to debug</td></tr>
    <tr><td>Query param</td><td><code>?v=2</code></td><td>Easy toggle</td><td>Caching issues</td></tr>
  </tbody>
</table>
<p>Whichever you pick: publish a deprecation policy (e.g., 12 months of overlap), send Sunset headers, and monitor per-version traffic so you know when it's safe to remove.</p>
'''

ANSWERS[94] = r'''
<p><strong>Scenario:</strong> Django forms need validation rules that are reusable across forms and API serializers — email + phone, credit card, age ranges, etc.</p>
<p><strong>Approach:</strong> build reusable validator <em>callables</em>, compose them on fields.</p>
<pre><code># Reusable validators — just callables
def validate_phone_e164(value):
    if not re.match(r"^\+[1-9]\d{7,14}$", value):
        raise ValidationError("Phone must be E.164 format (e.g., +15551234567)")

def validate_strong_password(value):
    errors = []
    if len(value) &lt; 12:
        errors.append("At least 12 characters")
    if not re.search(r"[A-Z]", value): errors.append("One uppercase letter")
    if not re.search(r"\d", value):    errors.append("One digit")
    if not re.search(r"[^A-Za-z0-9]", value): errors.append("One symbol")
    if errors:
        raise ValidationError(errors)

# Parameterized validator — returns a callable
def max_file_size(megabytes):
    limit = megabytes * 1024 * 1024
    def validator(f):
        if f.size &gt; limit:
            raise ValidationError(f"File exceeds {megabytes} MB limit")
    return validator

# Reuse across forms and serializers
class SignupForm(forms.Form):
    phone = forms.CharField(validators=[validate_phone_e164])
    password = forms.CharField(validators=[validate_strong_password])
    avatar = forms.ImageField(validators=[max_file_size(2)])

class SignupSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[validate_phone_e164])
    password = serializers.CharField(validators=[validate_strong_password], write_only=True)

# Cross-field validation via clean()
class OrderForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("start_date") &gt; cleaned.get("end_date"):
            raise ValidationError({"end_date": "Must be after start date"})
        return cleaned
</code></pre>
<p><strong>Design principles:</strong> keep validators pure (input → raise or return None). Parameterize with closures/factory functions. Add <code>deconstruct</code> for migrations if used on model fields. For business-rule validation that spans multiple objects, put it in a service layer, not the form — forms should only validate the shape of user input.</p>
'''

ANSWERS[95] = r'''
<p><strong>Scenario:</strong> legal / cost reasons require moving old data (orders &gt; 3 years, closed tickets &gt; 1 year) out of hot storage while remaining retrievable.</p>
<pre><code># Archive model — same shape, different table
class ArchivedOrder(models.Model):
    # Original id preserved
    original_id = models.BigIntegerField(db_index=True, unique=True)
    data = models.JSONField()            # full serialized snapshot
    archived_at = models.DateTimeField(auto_now_add=True)
    archived_reason = models.CharField(max_length=50)

    class Meta:
        db_table = "orders_archived"     # or different DB entirely

# Celery Beat task — runs nightly
@shared_task
def archive_old_orders():
    cutoff = timezone.now() - timedelta(days=365 * 3)
    qs = Order.objects.filter(completed_at__lt=cutoff, status="closed")

    for batch in chunked(qs, 1000):
        with transaction.atomic():
            ArchivedOrder.objects.bulk_create([
                ArchivedOrder(original_id=o.id,
                              data=OrderSerializer(o).data,
                              archived_reason="age&gt;3y")
                for o in batch], ignore_conflicts=True)
            # Delete from hot table
            Order.objects.filter(id__in=[o.id for o in batch]).delete()

# Transparent lookup — check hot first, fall back to archive
def get_order(order_id: int):
    try:
        return Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        archived = ArchivedOrder.objects.get(original_id=order_id)
        return archived.data    # dict, read-only
</code></pre>
<p><strong>Trade-offs:</strong></p>
<ul>
<li><strong>Same DB, separate table</strong> — simple, same transactions. Hot table shrinks; overall storage grows.</li>
<li><strong>Separate archive DB</strong> — hot DB performance isolated from archive growth. Cross-DB joins become harder.</li>
<li><strong>S3 cold storage</strong> — cheapest. Use S3 Glacier for data accessed &lt; once a year. Retrieval takes minutes/hours.</li>
</ul>
<p>Also consider: PostgreSQL table partitioning (partition by created_at) — achieves most of the benefit without a second table. Regardless of approach, enforce retention policies (delete after N years) to comply with GDPR / CCPA.</p>
'''

ANSWERS[96] = r'''
<p><strong>Scenario:</strong> Flask API uses JWT for stateless auth. Need login, refresh, logout, and revocation.</p>
<pre><code>import jwt as pyjwt, secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g

ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=14)

def issue_tokens(user_id: int) -&gt; dict:
    now = datetime.utcnow()
    access_payload = {
        "sub": str(user_id), "type": "access",
        "iat": now, "exp": now + ACCESS_TTL,
        "jti": secrets.token_urlsafe(16),
    }
    # Refresh tokens are opaque + tracked in DB (enables revocation)
    refresh_id = secrets.token_urlsafe(32)
    RefreshToken.create(id=refresh_id, user_id=user_id,
                        expires_at=now + REFRESH_TTL)
    return {
        "access": pyjwt.encode(access_payload, SECRET, algorithm="HS256"),
        "refresh": refresh_id,
    }

@app.route("/auth/login", methods=["POST"])
def login():
    user = User.query.filter_by(email=request.json["email"]).first()
    if not user or not check_password(user.password_hash, request.json["password"]):
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify(issue_tokens(user.id))

@app.route("/auth/refresh", methods=["POST"])
def refresh():
    rt = RefreshToken.query.get(request.json["refresh"])
    if not rt or rt.revoked or rt.expires_at &lt; datetime.utcnow():
        return jsonify({"error": "invalid refresh token"}), 401
    # Rotate — issue new refresh, revoke old (prevents replay)
    rt.revoked = True
    db.session.commit()
    return jsonify(issue_tokens(rt.user_id))

@app.route("/auth/logout", methods=["POST"])
def logout():
    RefreshToken.query.filter_by(id=request.json["refresh"]).update({"revoked": True})
    # Add access token JTI to Redis blacklist until its exp
    redis.setex(f"revoked:{g.jti}", 900, "1")
    db.session.commit()
    return "", 204
</code></pre>
<p><strong>Security essentials:</strong> short-lived access tokens (15 min) + long-lived refresh tokens (days). Store refresh tokens server-side so you can revoke (logout, password change, compromised account). Always rotate refresh tokens on use (detect reuse as a stolen token). Never put secrets in JWT claims — JWTs are signed but not encrypted. Use HTTPS-only, HttpOnly cookies for browser clients; headers are fine for mobile/SPA.</p>
'''

ANSWERS[97] = r'''
<p><strong>Scenario:</strong> Django REST API needs per-endpoint rate limits — different limits for public, authenticated, premium users.</p>
<pre><code># DRF has built-in throttling — Redis as backing store via django-redis
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/minute",
        "user": "100/minute",
        "premium": "1000/minute",
        "burst": "60/minute",
        "sustained": "10000/day",
    },
}
CACHES = {"default": {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": "redis://redis:6379/1",
}}

# Per-view customization
class SearchView(APIView):
    throttle_classes = [BurstThrottle, SustainedThrottle]

class BurstThrottle(UserRateThrottle):       scope = "burst"
class SustainedThrottle(UserRateThrottle):   scope = "sustained"

# Dynamic rate — premium users get more
class TieredThrottle(UserRateThrottle):
    def get_rate(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated and user.is_premium:
            return self.THROTTLE_RATES["premium"]
        return self.THROTTLE_RATES["user"]

# Custom Redis-backed token bucket — for finer control
class TokenBucket:
    LUA = """
    local b = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
    local tokens = tonumber(b[1]) or tonumber(ARGV[2])
    local last_ts = tonumber(b[2]) or tonumber(ARGV[3])
    local elapsed = tonumber(ARGV[3]) - last_ts
    tokens = math.min(tonumber(ARGV[2]), tokens + elapsed * tonumber(ARGV[1]))
    if tokens &lt; 1 then return 0 end
    tokens = tokens - 1
    redis.call('HMSET', KEYS[1], 'tokens', tokens, 'ts', ARGV[3])
    redis.call('EXPIRE', KEYS[1], 3600)
    return 1"""
    def __init__(self, r): self.script = r.register_script(self.LUA)
    def allow(self, key, refill_per_sec, capacity):
        return bool(self.script(keys=[key],
                     args=[refill_per_sec, capacity, time.time()]))
</code></pre>
<p><strong>When to build custom:</strong> DRF's throttling covers 90% of cases; build a token bucket when you need smoother bursts or cross-endpoint pooled limits. Always return <code>429</code> with <code>Retry-After</code> headers. Monitor 429 rates — a sudden spike may indicate abuse or a client bug.</p>
'''

ANSWERS[98] = r'''
<p><strong>Scenario:</strong> handle large file uploads (photos, video, documents) reliably — validate type/size, show progress, store efficiently.</p>
<pre><code># Custom upload handler — processes chunks as they arrive
from django.core.files.uploadhandler import FileUploadHandler, StopUpload
import hashlib

class HashingUploadHandler(FileUploadHandler):
    """Computes SHA-256 while receiving — no second pass needed."""
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.sha256 = hashlib.sha256()
        self.total = 0

    def receive_data_chunk(self, raw_data, start):
        self.sha256.update(raw_data)
        self.total += len(raw_data)
        if self.total &gt; 100 * 1024 * 1024:       # 100 MB hard cap
            raise StopUpload(connection_reset=True)
        return raw_data     # pass through to next handler

    def file_complete(self, file_size):
        return None         # we don't create the file ourselves

# View
class UploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        request.upload_handlers = [
            HashingUploadHandler(),
            MemoryFileUploadHandler(),
            TemporaryFileUploadHandler(),
        ]
        f = request.FILES["file"]

        if f.content_type not in {"image/jpeg", "image/png", "application/pdf"}:
            return Response({"error": "unsupported type"}, status=400)

        # Dedupe on content hash
        hash_handler = request.upload_handlers[0]
        digest = hash_handler.sha256.hexdigest()
        if existing := Upload.objects.filter(sha256=digest).first():
            return Response({"id": existing.id, "deduped": True})

        upload = Upload.objects.create(
            user=request.user, file=f, sha256=digest, size=hash_handler.total)
        process_upload.delay(upload.id)   # async virus scan, thumbnail, OCR
        return Response({"id": upload.id})

# Settings — 2.5 MB in memory, rest to temp file
FILE_UPLOAD_MAX_MEMORY_SIZE = 2_621_440
DATA_UPLOAD_MAX_MEMORY_SIZE = 2_621_440
</code></pre>
<p><strong>For very large files (videos, GB+):</strong> use pre-signed S3 URLs — the client uploads directly to S3, bypassing your server entirely. Your API just issues the URL and receives a webhook when complete. For resumable uploads (flaky connections), use the TUS protocol (<code>django-tus</code>). Always scan uploads for malware (ClamAV) before serving them back to users.</p>
'''

ANSWERS[99] = r'''
<p><strong>Scenario:</strong> multi-channel notification system — real-time WebSocket push for in-app, fallback to email for offline users.</p>
<pre><code># Unified notification model
class Notification(models.Model):
    KINDS = [("message", "Message"), ("mention", "Mention"), ("system", "System")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    kind = models.CharField(max_length=20, choices=KINDS)
    data = models.JSONField()
    read_at = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "-created"])]

# Dispatcher — one call, multi-channel delivery
def send_notification(user_id: int, kind: str, data: dict):
    notif = Notification.objects.create(user_id=user_id, kind=kind, data=data)
    prefs = NotificationPreference.objects.get_or_create(user_id=user_id)[0]

    # 1. In-app via WebSocket — push if connected
    async_to_sync(get_channel_layer().group_send)(
        f"notif_{user_id}",
        {"type": "notify", "payload": serialize(notif)})

    # 2. Email if they allow it AND haven't been active recently
    last_seen = UserActivity.last_seen(user_id)
    if prefs.email_enabled and (not last_seen or last_seen &lt; now() - timedelta(minutes=5)):
        send_email_notification.apply_async(
            args=[notif.id], countdown=300)  # 5 min delay — dedupe bursts

    # 3. Push to mobile (FCM / APNs)
    if prefs.push_enabled:
        for token in DeviceToken.objects.filter(user_id=user_id, active=True):
            push_to_device.delay(token.id, serialize(notif))

# WebSocket consumer (Django Channels)
class NotifConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(f"notif_{self.scope['user'].id}",
                                           self.channel_name)
        await self.accept()
        # Flush unread on reconnect
        async for n in Notification.objects.filter(
                user=self.scope["user"], read_at__isnull=True).aiterator():
            await self.send_json(serialize(n))

    async def notify(self, event):
        await self.send_json(event["payload"])
</code></pre>
<p><strong>Design rules:</strong> always persist first so offline users see it on reconnect. Coalesce bursts (5 notifications in 10 seconds → 1 email "You have 5 new messages"). Respect user preferences per channel. Include unsubscribe links in emails (regulatory requirement). Use separate queues per channel so a slow email provider doesn't block WebSocket delivery.</p>
'''

ANSWERS[100] = r'''
<p><strong>Scenario:</strong> Flask API needs structured request/response logging — correlation IDs, timings, status codes — without adding a decorator on every route.</p>
<pre><code>import logging, time, uuid, json
from flask import Flask, request, g

logger = logging.getLogger("app.access")
app = Flask(__name__)

@app.before_request
def start_timer():
    g.start = time.perf_counter()
    g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

@app.after_request
def log_request(response):
    duration_ms = (time.perf_counter() - g.start) * 1000
    logger.info("request", extra={
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "query": request.query_string.decode(),
        "status": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "user_id": getattr(g, "user_id", None),
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "ua": request.headers.get("User-Agent", "")[:200],
    })
    response.headers["X-Request-ID"] = g.request_id
    # Warn on slow requests
    if duration_ms &gt; 1000:
        logger.warning("slow_request", extra={"request_id": g.request_id,
                       "path": request.path, "duration_ms": duration_ms})
    return response

@app.errorhandler(Exception)
def log_errors(e):
    logger.exception("unhandled_error", extra={"request_id": g.request_id})
    return jsonify({"error": "internal error", "request_id": g.request_id}), 500

# JSON formatter — one log = one line of JSON
class JSONFormatter(logging.Formatter):
    def format(self, record):
        base = {"time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
                "level": record.levelname, "message": record.getMessage(),
                "logger": record.name}
        # Include custom fields from extra={}
        for k, v in record.__dict__.items():
            if k not in {"args","created","exc_info","exc_text","filename",
                          "funcName","levelname","levelno","lineno","module",
                          "msecs","msg","name","pathname","process",
                          "processName","relativeCreated","stack_info",
                          "thread","threadName","message","asctime"}:
                base[k] = v
        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)
        return json.dumps(base)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler); logger.setLevel("INFO")
</code></pre>
<p><strong>Why middleware over decorators:</strong> <code>before_request</code>/<code>after_request</code> run for every route automatically — nothing slips through. The correlation ID (request_id) threads through all log lines for one request, making debugging a single trace. Echo it back in a response header so clients can include it in bug reports. Ship JSON to your log aggregator (CloudWatch, Datadog, Loki) for indexed search. Add alerts on <code>level=ERROR</code> and p99 latency regressions.</p>
'''
