"""Detailed answers for MongoDB Scenario Based interview questions.

Each ANSWERS[n] is an HTML string suitable for embedding inside a chapter page.
Style: Situation / Approach / Trade-offs / Production polish, with substantial
mongosh + driver code blocks. ~4,000-5,000 chars per answer.
"""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''
<p><strong>Situation:</strong> an e-commerce platform needs <code>products</code>, <code>categories</code>, <code>users</code>, and <code>orders</code>. Reads are read-heavy on product/category browsing; writes are concentrated on cart and checkout. The schema must keep historical orders accurate even when products change.</p>

<p><strong>Approach:</strong> four collections. Categories use the <em>array of ancestors</em> pattern for cheap subtree queries. Products embed their primary category path. Orders <strong>snapshot</strong> product fields at checkout time so future product changes don&rsquo;t rewrite history.</p>

<pre><code>// categories &mdash; tree via ancestors array
db.categories.insertOne({
  _id: "electronics",
  name: "Electronics",
  ancestors: [],          // root
  parent: null,
  slug: "electronics"
});
db.categories.insertOne({
  _id: "phones",
  name: "Phones",
  ancestors: ["electronics"],
  parent: "electronics",
  slug: "electronics/phones"
});

// products &mdash; embed cheap category metadata for listings
db.products.insertOne({
  _id:        ObjectId(),
  sku:        "IPH-15-128",
  name:       "iPhone 15",
  price_cents: 79900,
  category:   { _id: "phones", path: ["electronics", "phones"] },
  attributes: { color: "blue", storage: "128GB" },
  inventory:  { on_hand: 42, reserved: 3 },
  active:     true,
  created_at: new Date()
});

// users &mdash; minimal profile + addresses subdoc array
db.users.insertOne({
  _id: ObjectId(),
  email: "alice@example.com",
  email_verified: true,
  addresses: [
    { type: "shipping", line1: "1 Main St", city: "NYC", default: true }
  ],
  created_at: new Date()
});

// orders &mdash; snapshot product fields, reference user
db.orders.insertOne({
  _id: ObjectId(),
  user_id: ObjectId("..."),
  status: "paid",          // pending | paid | shipped | delivered | refunded
  items: [{
    product_id:  ObjectId("..."),
    sku:         "IPH-15-128",
    name:        "iPhone 15",          // snapshot
    price_cents: 79900,                // snapshot
    quantity:    1
  }],
  totals: { subtotal_cents: 79900, tax_cents: 6392, total_cents: 86292 },
  shipping_address: { line1: "1 Main St", city: "NYC" },
  placed_at: new Date()
});

// Indexes
db.products.createIndex({ "category._id": 1, active: 1, price_cents: 1 });
db.products.createIndex({ sku: 1 }, { unique: true });
db.orders.createIndex({ user_id: 1, placed_at: -1 });
db.orders.createIndex({ status: 1, placed_at: -1 });
db.users.createIndex({ email: 1 }, { unique: true });</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Snapshot product fields on order</td><td>Order history must survive price/name changes and product deletion</td><td>$lookup live &mdash; breaks audits and reprints</td></tr>
<tr><td>Ancestors array on categories</td><td>One-shot subtree query: <code>{ ancestors: "electronics" }</code></td><td>Recursive <code>$graphLookup</code> &mdash; works but slower</td></tr>
<tr><td><code>price_cents</code> integer</td><td>No floating-point drift</td><td><code>Decimal128</code> if multi-currency with sub-cent precision</td></tr>
<tr><td>Inventory inside product doc</td><td>Single-document atomicity for cart reservations</td><td>Separate inventory collection for write-hotspot products</td></tr>
<tr><td>Embedded user addresses</td><td>Always read together with the user, capped at &lt;10</td><td>Separate collection if 100+ saved addresses per user</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> reserve inventory atomically with <code>{ $inc: { "inventory.on_hand": -1, "inventory.reserved": 1 } }</code> guarded by <code>{ "inventory.on_hand": { $gte: 1 } }</code>; back catalog search with <strong>MongoDB Atlas Search</strong> for fuzzy matching, faceting, and synonyms; stream order events to a warehouse (<strong>BigQuery</strong>, <strong>Snowflake</strong>) via <strong>Airbyte</strong> so analytics never hits the OLTP cluster; use <strong>change streams</strong> to fan out to <strong>Algolia</strong>/<strong>Meilisearch</strong> and email/SMS via <strong>BullMQ</strong>; tax and shipping calculations belong in services like <strong>Stripe Tax</strong>/<strong>TaxJar</strong> &mdash; never reinvent.</p>
'''

ANSWERS[2] = r'''
<p><strong>Situation:</strong> a recommendation system suggests products to users based on their purchase history. The system must be fast at request time, refresh incrementally as new orders arrive, and handle cold-start users with no history.</p>

<p><strong>Approach:</strong> precompute a per-user recommendations document refreshed nightly. Use collaborative filtering via co-purchase counts (&ldquo;customers who bought X also bought Y&rdquo;), with category-level fallbacks for cold-start users. Store recommendations in a dedicated collection that the API reads in one query.</p>

<pre><code>// 1. Build product-product co-purchase counts
db.orders.aggregate([
  { $match: { status: { $in: ["paid", "shipped", "delivered"] } } },
  { $project: { items: "$items.product_id" } },
  // For each order, generate all (a, b) pairs of items
  { $project: { pairs: {
      $reduce: {
        input: "$items",
        initialValue: { acc: [], rest: "$items" },
        in: {
          acc:  { $concatArrays: ["$$value.acc", { $map: {
            input: { $slice: ["$$value.rest", 1, 100] },
            as: "b",
            in: { a: "$$this", b: "$$b" }
          }}]},
          rest: { $slice: ["$$value.rest", 1, 100] }
        }
      }
  }}},
  { $unwind: "$pairs.acc" },
  { $group: { _id: "$pairs.acc", count: { $sum: 1 } } },
  { $merge: { into: "co_purchases", on: "_id", whenMatched: "replace" } }
]);

// 2. Build per-user recommendations: products bought by users with similar history
db.orders.aggregate([
  { $match: { status: { $in: ["paid", "delivered"] } } },
  { $group: { _id: "$user_id", purchased: { $addToSet: "$items.product_id" } } },
  { $unwind: "$purchased" },
  { $unwind: "$purchased" },
  { $lookup: {
      from: "co_purchases",
      localField: "purchased",
      foreignField: "_id.a",
      as: "co"
  }},
  { $unwind: "$co" },
  { $group: {
      _id: "$_id",
      candidates: { $push: { product_id: "$co._id.b", score: "$co.count" } }
  }},
  // Aggregate scores per candidate, take top 20
  { $project: {
      recommendations: {
        $slice: [
          { $sortArray: { input: "$candidates", sortBy: { score: -1 } } },
          20
        ]
      }
  }},
  { $merge: { into: "user_recommendations", on: "_id", whenMatched: "replace" } }
]);

// 3. Serve at request time &mdash; one indexed lookup
const recs = await db.collection("user_recommendations")
  .findOne({ _id: userId });

// 4. Cold-start fallback: top-selling products in user&rsquo;s most-viewed category
const fallback = await db.collection("products")
  .find({ "category._id": userPreferredCategory, active: true })
  .sort({ sales_count_30d: -1 })
  .limit(20)
  .toArray();</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Precomputed per-user docs</td><td>Single indexed read at request time; no live joining</td><td>Compute on the fly &mdash; latency spikes under load</td></tr>
<tr><td>Co-purchase as recall signal</td><td>Simple, interpretable, works at small scale</td><td>Matrix factorization / embeddings &mdash; better quality, more infra</td></tr>
<tr><td>Nightly refresh</td><td>Simple, sufficient for shopping; orders flow in slowly</td><td>Real-time via change streams if catalog changes hourly</td></tr>
<tr><td>Top-20 cap</td><td>Document stays under 1MB, predictable response size</td><td>Larger N + cursor pagination if UI needs it</td></tr>
<tr><td>Fallback to category bestsellers</td><td>Cold-start users still see relevant items</td><td>Generic top-N &mdash; less personal</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for higher-quality recs, switch to embedding-based retrieval &mdash; ingest products into <strong>MongoDB Atlas Vector Search</strong> or <strong>Pinecone</strong>/<strong>Weaviate</strong>, embed via <strong>OpenAI text-embedding-3-large</strong> or <strong>Cohere</strong>; combine with re-ranking via <strong>Cohere Rerank</strong> or a custom model on <strong>Modal</strong>/<strong>Replicate</strong>; production teams typically blend recall (vectors, co-purchase) with business rules (in-stock, margin, recency); cache responses in <strong>Redis</strong> keyed by user_id with 1h TTL; A/B test ranking variants via <strong>GrowthBook</strong>/<strong>LaunchDarkly</strong>; monitor click-through and conversion via <strong>Amplitude</strong>/<strong>PostHog</strong> to feed back into model training.</p>
'''

ANSWERS[3] = r'''
<p><strong>Situation:</strong> migrate an existing SQL database (typically Postgres or MySQL with 30+ tables, foreign keys, and some 1:N and N:N relationships) to MongoDB. The migration must preserve data integrity, run in a reasonable window, and ideally support a phased dual-write cutover.</p>

<p><strong>Approach:</strong> three-phase migration &mdash; (1) <strong>denormalize and embed</strong> based on access patterns, (2) <strong>stream changes</strong> with CDC during cutover, (3) <strong>verify and cut over</strong>. Don&rsquo;t replicate the SQL schema 1:1 &mdash; redesign for document orientation.</p>

<pre><code>// SQL: customers (1) -- (N) orders (1) -- (N) order_items (N) -- (1) products

// Step 1: ETL with embedding decisions
// customers + their addresses (1:N, small) &rarr; embed addresses as array
// orders + order_items (1:N, bounded) &rarr; embed items in order
// products (referenced from items) &rarr; snapshot name/price into items, reference _id

// Python pseudo-code with pymongo + psycopg2
import psycopg2, pymongo
sql  = psycopg2.connect("postgresql://...").cursor()
mdb  = pymongo.MongoClient("mongodb://...").shop

# Customers with embedded addresses
sql.execute("""
  SELECT c.id, c.email, c.created_at,
         json_agg(json_build_object('line1', a.line1, 'city', a.city)) AS addresses
  FROM customers c LEFT JOIN addresses a ON a.customer_id = c.id
  GROUP BY c.id
""")
batch = []
for row in sql:
    batch.append({
        "_id":        row[0],            # keep SQL id as _id for traceability
        "email":      row[1],
        "created_at": row[2],
        "addresses":  row[3] or []
    })
    if len(batch) == 1000:
        mdb.customers.insert_many(batch, ordered=False)
        batch.clear()

# Orders with embedded items + product snapshots
sql.execute("""
  SELECT o.id, o.customer_id, o.status, o.placed_at,
         json_agg(json_build_object(
           'product_id',  oi.product_id,
           'name',        p.name,
           'price_cents', oi.price_cents,
           'quantity',    oi.quantity
         )) AS items
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.id
  JOIN products    p  ON p.id = oi.product_id
  GROUP BY o.id
""")

// Step 2: enable CDC for live cutover (Debezium &rarr; Kafka &rarr; consumer)
// debezium connector emits row-level change events; consumer applies them to MongoDB
//   { "op": "c"|"u"|"d", "before": {...}, "after": {...} }

// Step 3: verify counts and checksums per table/collection
db.customers.countDocuments();          // compare with SELECT COUNT(*) FROM customers
db.orders.aggregate([{ $count: "n" }]); // compare with orders SQL count

// Sample row-level checksum
db.customers.aggregate([
  { $project: { hash: { $function: { body: "..." , args: ["$$ROOT"], lang: "js" } } } }
]);</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Embed where 1:N is bounded</td><td>One read instead of join; atomic update</td><td>Reference + <code>$lookup</code> &mdash; always slower for hot reads</td></tr>
<tr><td>Snapshot product into order items</td><td>History stable when products change</td><td>Reference &mdash; broken audit trail</td></tr>
<tr><td>Reuse SQL id as <code>_id</code></td><td>Idempotent re-runs; easy bidirectional verification</td><td>Generate new ObjectIds &mdash; harder to reconcile</td></tr>
<tr><td>Phased dual-write via CDC</td><td>Zero-downtime cutover; rollback possible</td><td>Big-bang migration &mdash; long outage, risky</td></tr>
<tr><td>Bulk inserts in batches of 1k</td><td>Network round-trip amortized; oplog stays manageable</td><td>One-by-one &mdash; orders of magnitude slower</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> use <strong>Debezium</strong>&rsquo;s Postgres/MySQL connector to stream changes to <strong>Kafka</strong>, with a small consumer that applies them to MongoDB; <strong>Airbyte</strong>, <strong>Fivetran</strong>, or <strong>Estuary</strong> are managed alternatives; for the bulk load, <strong>mongoimport</strong> with <code>--numInsertionWorkers</code> tuned to cluster capacity is fastest; verify with <strong>row-level hashes</strong> stored in both systems and compared in batches; keep dual-write running for a week, then cut reads over a percentage at a time via <strong>LaunchDarkly</strong> flags; monitor with <strong>Datadog</strong> dashboards on both sides &mdash; query latencies, error rates, drift counts.</p>
'''

ANSWERS[4] = r'''
<p><strong>Situation:</strong> a collection of 50M+ documents has queries running in 5+ seconds. The team needs to bring P95 latency under 100ms without a rewrite. Performance is suffering across reads (slow queries), writes (slow indexes), and aggregations (memory pressure).</p>

<p><strong>Approach:</strong> measure first with <code>explain()</code> and <strong>Atlas Performance Advisor</strong>, then attack in order: (1) right indexes, (2) right query shape, (3) right schema. Most slowness is one of three things: missing index, wrong index direction, or unbounded scan inside an aggregation.</p>

<pre><code>// 1. Find the offenders &mdash; enable profiler at level 2 (slow queries) for a window
db.setProfilingLevel(1, { slowms: 100 });

// Inspect after a few minutes
db.system.profile.find({ millis: { $gt: 100 } })
  .sort({ ts: -1 }).limit(20)
  .pretty();

// 2. Analyze a specific slow query
db.orders.find({ status: "paid", placed_at: { $gte: ISODate("2026-01-01") } })
         .sort({ placed_at: -1 })
         .explain("executionStats");
//   key fields:
//     winningPlan.stage      &mdash; want IXSCAN, not COLLSCAN
//     totalDocsExamined      &mdash; should be close to nReturned
//     totalKeysExamined      &mdash; should also be close
//     executionTimeMillis    &mdash; below 100 if hot

// 3. Build the right index per the ESR rule (Equality, Sort, Range)
db.orders.createIndex({ status: 1, placed_at: -1 });
//   serves: { status: "paid" } + sort by placed_at desc

// 4. Use covered queries when possible
db.orders.createIndex({ user_id: 1, placed_at: -1, total_cents: 1 });
db.orders.find(
  { user_id: ObjectId("...") },
  { _id: 0, placed_at: 1, total_cents: 1 }      // every field is in the index
).sort({ placed_at: -1 });
//   explain() shows totalDocsExamined: 0 &mdash; never touches the document

// 5. Aggregation hygiene
db.orders.aggregate([
  { $match: { placed_at: { $gte: ISODate("2026-01-01") } } },  // FIRST &mdash; uses index
  { $project: { user_id: 1, total_cents: 1 } },                // shrink documents
  { $group:   { _id: "$user_id", spend: { $sum: "$total_cents" } } },
  { $sort:    { spend: -1 } },
  { $limit:   100 }
], { allowDiskUse: true, hint: { placed_at: -1 } });

// 6. Drop unused indexes &mdash; they slow writes and waste RAM
db.orders.aggregate([{ $indexStats: {} }])
         .forEach(s =&gt; print(s.name, s.accesses.ops));
db.orders.dropIndex("legacy_idx");

// 7. For very large collections, shard or partition by date
sh.enableSharding("shop");
sh.shardCollection("shop.orders", { user_id: 1, placed_at: 1 });</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Lever</th><th>Wins</th><th>Costs</th></tr></thead>
<tbody>
<tr><td>Add compound index (ESR)</td><td>Range + sort served from index</td><td>Each index slows writes 5-10%, eats RAM</td></tr>
<tr><td>Covered queries</td><td><code>totalDocsExamined: 0</code> &mdash; fastest possible</td><td>Index becomes wider, write cost rises</td></tr>
<tr><td>Materialize via <code>$merge</code></td><td>Dashboards read precomputed rollups in 1ms</td><td>Lag between source and rollup; refresh job to maintain</td></tr>
<tr><td>Schema redesign (embed hot subdocs)</td><td>One read replaces N <code>$lookup</code>s</td><td>Document growth, larger working set</td></tr>
<tr><td>Sharding</td><td>Horizontal scale beyond ~500GB working set</td><td>Operational complexity; bad shard key = worse perf</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> in <strong>MongoDB Atlas</strong>, the <strong>Performance Advisor</strong> auto-suggests indexes from query patterns; the <strong>Query Profiler</strong> visualizes slow ops over time; pair with <strong>Datadog APM</strong>, <strong>New Relic</strong>, or <strong>Honeycomb</strong> for distributed tracing across services; tune <strong>WiredTiger cache</strong> via Atlas console (default = 50% RAM &minus; 1GB); long-running aggregations should set <code>maxTimeMS</code> so they can&rsquo;t take down the server; <strong>read preference</strong> <code>secondaryPreferred</code> on analytics queries offloads from primaries; unbounded result sets need cursor pagination, never <code>skip(N).limit(M)</code> at depth.</p>
'''

ANSWERS[5] = r'''
<p><strong>Situation:</strong> a chat application built on MongoDB needs real-time delivery of new messages, typing indicators, and read receipts. Multiple servers handle WebSocket connections; clients must see updates within 100ms.</p>

<p><strong>Approach:</strong> store messages persistently in MongoDB; use <strong>change streams</strong> to fan out new messages to subscribed WebSocket connections; combine with <strong>Redis pub/sub</strong> across application servers so any server can notify clients connected elsewhere.</p>

<pre><code>// Schema
db.conversations.insertOne({
  _id: ObjectId(),
  type: "direct",                       // direct | group
  participant_ids: [ObjectId(), ObjectId()],
  last_message_at: new Date(),
  last_message_preview: "..."
});

db.messages.insertOne({
  _id: ObjectId(),
  conversation_id: ObjectId(),
  sender_id:       ObjectId(),
  body:            "Hello",
  attachments:     [],
  reactions:       [],
  read_by:         [],                   // array of user_ids who&rsquo;ve seen it
  created_at:      new Date()
});

db.messages.createIndex({ conversation_id: 1, created_at: -1 });
db.conversations.createIndex({ participant_ids: 1, last_message_at: -1 });

// Send message: write + atomic conversation update
async function sendMessage(convId, senderId, body) {
  const msg = {
    _id: new ObjectId(),
    conversation_id: convId, sender_id: senderId, body,
    read_by: [senderId], created_at: new Date()
  };
  await db.collection("messages").insertOne(msg);
  await db.collection("conversations").updateOne(
    { _id: convId },
    { $set: { last_message_at: msg.created_at, last_message_preview: body.slice(0, 80) } }
  );
  return msg;
}

// Real-time fan-out: change stream + Redis pub/sub
import Redis from "ioredis";
const redis = new Redis(process.env.REDIS_URL);

const stream = db.collection("messages").watch(
  [{ $match: { operationType: "insert" } }],
  { fullDocument: "updateLookup" }
);

stream.on("change", async (change) =&gt; {
  const msg = change.fullDocument;
  // Broadcast to all app servers via Redis &mdash; each server pushes to its WebSocket clients
  await redis.publish(`conv:${msg.conversation_id}`, JSON.stringify(msg));
});

// In each WebSocket server
const sub = new Redis(process.env.REDIS_URL);
sub.psubscribe("conv:*");
sub.on("pmessage", (_pattern, channel, payload) =&gt; {
  const convId = channel.split(":")[1];
  const msg = JSON.parse(payload);
  // Find local sockets subscribed to this conversation, push the message
  for (const ws of localSubscribers.get(convId) ?? []) {
    ws.send(JSON.stringify({ type: "message", msg }));
  }
});

// Read receipts: atomic add to read_by array
db.messages.updateOne(
  { _id: messageId, read_by: { $ne: userId } },
  { $addToSet: { read_by: userId } }
);

// Typing indicator: ephemeral &mdash; goes through Redis only, no DB write
redis.publish(`conv:${convId}:typing`, JSON.stringify({ user_id: userId, ts: Date.now() }));</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Change stream + Redis pub/sub</td><td>Decouples DB-of-record from delivery; one DB watch fans to N servers</td><td>Direct change stream per server &mdash; oplog pressure scales with servers</td></tr>
<tr><td>Persist messages to MongoDB</td><td>History, search, audit; survives restarts</td><td>Pure pub/sub &mdash; messages lost when offline</td></tr>
<tr><td>Typing/presence in Redis only</td><td>Hundreds of events/sec/user, useless after delivery</td><td>Persisting them &mdash; oplog explosion</td></tr>
<tr><td><code>read_by</code> as embedded array</td><td>Atomic update; visible in single message read</td><td>Separate <code>message_reads</code> collection &mdash; an extra read per message</td></tr>
<tr><td>Compound index (conv, created_at)</td><td>Loads recent N messages per conversation in one IXSCAN</td><td>Scan-then-sort &mdash; doesn&rsquo;t scale past a few hundred messages</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for hundreds of thousands of concurrent connections, use a managed WebSocket gateway like <strong>Ably</strong>, <strong>Pusher</strong>, or <strong>PubNub</strong> &mdash; or self-host with <strong>Soketi</strong>/<strong>Centrifugo</strong>; <strong>Socket.IO</strong> with the Redis adapter is the classic Node stack; encrypt messages at rest using <strong>Queryable Encryption (7.0+)</strong> for HIPAA/GDPR scenarios; archive cold conversations (no activity 90+ days) to <strong>Atlas Online Archive</strong> &mdash; transparent reads, much cheaper storage; index <code>read_by</code> if you need &ldquo;unread count&rdquo; queries; rate-limit sends per user via Redis sliding window; for search, mirror messages to <strong>Atlas Search</strong> or <strong>Meilisearch</strong>.</p>
'''

ANSWERS[6] = r'''
<p><strong>Situation:</strong> a web app needs login with email/password, password reset, OAuth/social sign-in, optional MFA, role-based authorization, and protection against brute force and credential stuffing. The MongoDB schema must store credentials securely.</p>

<p><strong>Approach:</strong> separate <code>users</code>, <code>credentials</code>, <code>sessions</code>, <code>oauth_accounts</code>, and <code>auth_attempts</code>. Hash passwords with <strong>argon2id</strong> (or bcrypt cost 12+); store algorithm + parameters so you can rotate. Sessions are server-side (revocable) with HttpOnly cookies.</p>

<pre><code>db.users.insertOne({
  _id: ObjectId(),
  email:           "alice@example.com",
  email_verified:  false,
  display_name:    "Alice",
  status:          "active",     // active | locked | disabled
  roles:           ["user"],     // role names; map to permissions in code
  created_at:      new Date(),
  last_login_at:   null
});

db.user_passwords.insertOne({
  user_id:        userId,
  hash:           "$argon2id$v=19$m=65536,t=3,p=4$...",
  algorithm:      "argon2id",
  must_change:    false,
  changed_at:     new Date()
});

db.oauth_accounts.insertOne({
  user_id:    userId,
  provider:   "google",          // google | github | microsoft | ...
  subject:    "1234567890",      // provider&rsquo;s stable user id
  email:      "alice@example.com",
  linked_at:  new Date()
});

db.user_mfa.insertOne({
  user_id:        userId,
  totp_secret:    BinData(0, "..."),    // encrypted at app layer or via CSFLE
  enabled:        false,
  recovery_codes: [...]
});

db.sessions.insertOne({
  _id:         "abc...43chars",          // 256-bit random base64url
  user_id:     userId,
  ip_address:  BinData(...),
  user_agent:  "Chrome/...",
  created_at:  new Date(),
  expires_at:  new Date(Date.now() + 30*24*3600*1000),
  revoked_at:  null
});

// Indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.oauth_accounts.createIndex({ provider: 1, subject: 1 }, { unique: true });
db.sessions.createIndex({ user_id: 1, expires_at: 1 });
db.sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });  // TTL cleanup
db.auth_attempts.createIndex({ email: 1, attempted_at: -1 });
db.auth_attempts.createIndex(
  { attempted_at: 1 }, { expireAfterSeconds: 30*86400 }  // keep 30 days
);

// Login flow (Node)
import argon2 from "argon2";
import crypto from "crypto";

async function login(email, password, ip, ua) {
  const recent = await db.collection("auth_attempts").countDocuments({
    email, succeeded: false,
    attempted_at: { $gt: new Date(Date.now() - 15*60*1000) }
  });
  if (recent &gt;= 5) throw new Error("Too many attempts");

  const user = await db.collection("users").findOne({ email });
  const cred = user &amp;&amp; await db.collection("user_passwords").findOne({ user_id: user._id });
  const ok   = user?.status === "active"
            &amp;&amp; cred &amp;&amp; await argon2.verify(cred.hash, password);

  await db.collection("auth_attempts").insertOne({
    email, ip_address: ip, succeeded: !!ok, attempted_at: new Date()
  });
  if (!ok) throw new Error("Invalid credentials");

  const sid = crypto.randomBytes(32).toString("base64url");
  await db.collection("sessions").insertOne({
    _id: sid, user_id: user._id, ip_address: ip, user_agent: ua,
    created_at: new Date(), expires_at: new Date(Date.now() + 30*24*3600*1000)
  });
  return sid;   // set as Secure HttpOnly SameSite=Lax cookie
}</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Choice</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>argon2id</td><td>Modern, memory-hard, GPU-resistant</td><td>bcrypt (still acceptable, cost 12+)</td></tr>
<tr><td>Server-side sessions</td><td>Revocable instantly; supports &ldquo;sign out everywhere&rdquo;</td><td>JWT &mdash; can&rsquo;t revoke without a denylist</td></tr>
<tr><td>Password collection separate</td><td>Easy to re-encrypt all hashes; auditing</td><td>Hash on user doc &mdash; works but blends concerns</td></tr>
<tr><td>Roles in user doc, perms in code</td><td>Roles change rarely; perm logic is testable</td><td>Permissions in DB &mdash; flexible but slower checks</td></tr>
<tr><td>TTL on sessions and attempts</td><td>Self-cleaning, no nightly job</td><td>Manual cleanup &mdash; forget it once, table grows</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> outsource auth entirely to <strong>Auth0</strong>, <strong>Clerk</strong>, <strong>WorkOS</strong>, <strong>Stytch</strong>, or <strong>Supabase Auth</strong> unless auth is core IP &mdash; password reset email, OAuth flows, MFA TOTP/WebAuthn, and bot protection are commodity infrastructure with subtle security pitfalls; for self-hosting, <strong>Lucia</strong>, <strong>Better Auth</strong>, or <strong>NextAuth.js</strong>/<strong>Auth.js</strong> are well-maintained Node options; encrypt MFA secrets via <strong>Queryable Encryption</strong> or app-layer KMS (<strong>AWS KMS</strong>, <strong>HashiCorp Vault</strong>); add <strong>WebAuthn/passkeys</strong> &mdash; the modern bar; rate-limit per IP and per email separately to defeat distributed credential stuffing; integrate <strong>HaveIBeenPwned</strong> on signup to reject leaked passwords.</p>
'''

ANSWERS[7] = r'''
<p><strong>Situation:</strong> a blogging platform with posts, comments, tags, and authors. Reads dominate &mdash; mostly listing posts and reading individual posts with their comments. Writes are sparse (a few posts per day per author). Need search, tag filtering, and SEO-friendly URLs.</p>

<p><strong>Approach:</strong> embed comments inside posts (bounded, always read together); reference authors (one user, many posts); store tags as an array on the post for fast filtering; mirror to <strong>Atlas Search</strong> for full-text and faceted queries.</p>

<pre><code>db.users.insertOne({
  _id: ObjectId(),
  username: "alice",
  display_name: "Alice Wonder",
  bio: "...",
  created_at: new Date()
});

db.posts.insertOne({
  _id: ObjectId(),
  slug: "designing-document-schemas",   // unique; in URL
  title: "Designing Document Schemas",
  body: "...",
  excerpt: "When and what to embed...",
  author: {                              // denormalized snapshot
    _id: ObjectId(),
    username: "alice",
    display_name: "Alice Wonder"
  },
  tags: ["mongodb", "schema-design", "best-practices"],
  status: "published",                   // draft | published | archived
  view_count: 0,
  comments: [
    {
      _id: ObjectId(),
      author: { _id: ObjectId(), username: "bob", display_name: "Bob" },
      body: "Great post!",
      created_at: new Date(),
      reply_to: null,                    // for threading
      reactions: { like: 12, love: 3 }
    }
  ],
  comments_count: 1,
  published_at: new Date(),
  updated_at: new Date()
});

db.posts.createIndex({ slug: 1 }, { unique: true });
db.posts.createIndex({ status: 1, published_at: -1 });
db.posts.createIndex({ tags: 1, published_at: -1 });
db.posts.createIndex({ "author._id": 1, published_at: -1 });

// Common queries

// Homepage feed
db.posts.find({ status: "published" })
        .sort({ published_at: -1 })
        .limit(20);

// Tag page
db.posts.find({ tags: "mongodb", status: "published" })
        .sort({ published_at: -1 })
        .limit(20);

// Single post by slug (one read fetches everything)
db.posts.findOne({ slug: "designing-document-schemas" });

// Add a comment atomically
db.posts.updateOne(
  { _id: postId },
  {
    $push: { comments: newComment },
    $inc:  { comments_count: 1 },
    $set:  { updated_at: new Date() }
  }
);

// When the comment array might exceed 1000, externalize:
db.comments.insertOne({
  _id: ObjectId(), post_id: postId, author: {...}, body: "...", created_at: new Date()
});
db.comments.createIndex({ post_id: 1, created_at: 1 });</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Embed comments in post</td><td>One read per page view; fewer collections to manage</td><td>Separate collection &mdash; needed when comments grow unbounded (1k+)</td></tr>
<tr><td>Snapshot author on post</td><td>List pages render in one read; rare display-name changes are acceptable</td><td>Live <code>$lookup</code> &mdash; slower lists</td></tr>
<tr><td>Tags as array on post</td><td>Multikey index makes tag filtering instant</td><td>Separate <code>post_tags</code> &mdash; needs join</td></tr>
<tr><td><code>slug</code> in URL</td><td>SEO; shareable; stable</td><td>ObjectId &mdash; ugly URLs, gone-when-deleted ambiguity</td></tr>
<tr><td>Status field</td><td>Draft/published/archived in one collection</td><td>Separate drafts collection &mdash; more code paths</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> mirror posts into <strong>Atlas Search</strong> for full-text, fuzzy, and synonym-aware search with faceting on tags &mdash; faster and more flexible than <code>$text</code>; cache rendered HTML (markdown &rarr; HTML) at write time to skip render on hot reads; serve static-rendered pages via <strong>Next.js ISR</strong>, <strong>Astro</strong>, or <strong>Eleventy</strong> for low-cost CDN delivery; sync to a CDN (<strong>Cloudflare</strong>, <strong>Fastly</strong>) with cache-tags for instant invalidation on edit; throttle comment writes via Redis sliding window; moderate via <strong>Perspective API</strong> or <strong>OpenAI Moderation</strong>; <strong>Disqus</strong> or <strong>Giscus</strong> are off-the-shelf comment options if comments aren&rsquo;t core IP.</p>
'''

ANSWERS[8] = r'''
<p><strong>Situation:</strong> store an organizational structure &mdash; CEO at the top, departments below, employees within. Need to find an employee&rsquo;s manager chain, all reports under a VP, and depth-limited subtrees. Reads dominate.</p>

<p><strong>Approach:</strong> the <strong>array-of-ancestors</strong> pattern with a <strong>materialized path</strong>. Every node stores its full ancestor chain in an array, plus a path string for sort-friendly hierarchical display. Subtree queries become a single indexed lookup.</p>

<pre><code>db.org.insertMany([
  {
    _id: "ceo",
    name: "Alice (CEO)",
    parent: null,
    ancestors: [],
    path: "ceo",
    depth: 0
  },
  {
    _id: "cto",
    name: "Bob (CTO)",
    parent: "ceo",
    ancestors: ["ceo"],
    path: "ceo.cto",
    depth: 1
  },
  {
    _id: "vp_eng",
    name: "Carol (VP Eng)",
    parent: "cto",
    ancestors: ["ceo", "cto"],
    path: "ceo.cto.vp_eng",
    depth: 2
  },
  {
    _id: "eng_001",
    name: "Dave (Engineer)",
    parent: "vp_eng",
    ancestors: ["ceo", "cto", "vp_eng"],
    path: "ceo.cto.vp_eng.eng_001",
    depth: 3
  }
]);

db.org.createIndex({ ancestors: 1 });
db.org.createIndex({ parent: 1 });
db.org.createIndex({ path: 1 });

// Subtree: everyone under the CTO (one indexed query)
db.org.find({ ancestors: "cto" });

// Subtree limited to depth 2 below
db.org.find({ ancestors: "cto", depth: { $lte: 3 } });

// Direct reports only
db.org.find({ parent: "cto" });

// Manager chain &mdash; one read returns all ancestors as an array
const dave = db.org.findOne({ _id: "eng_001" });
const chain = db.org.find({ _id: { $in: dave.ancestors } }).toArray();

// Re-parent (move a subtree under a new manager) &mdash; multi-doc update
async function reparent(nodeId, newParentId) {
  const newParent = await db.collection("org").findOne({ _id: newParentId });
  const node      = await db.collection("org").findOne({ _id: nodeId });
  const oldPrefix = node.path;
  const newAncestors = [...newParent.ancestors, newParent._id];
  const newPath      = `${newParent.path}.${nodeId}`;

  // Update the node itself
  await db.collection("org").updateOne(
    { _id: nodeId },
    { $set: {
      parent: newParentId,
      ancestors: newAncestors,
      path: newPath,
      depth: newAncestors.length
    }}
  );

  // Update every descendant: rewrite ancestors and path prefix
  const descendants = await db.collection("org").find({ ancestors: nodeId }).toArray();
  const bulk = db.collection("org").initializeUnorderedBulkOp();
  for (const d of descendants) {
    const tail = d.ancestors.slice(d.ancestors.indexOf(nodeId));
    bulk.find({ _id: d._id }).updateOne({ $set: {
      ancestors: [...newAncestors, ...tail],
      path: d.path.replace(oldPrefix, newPath),
      depth: newAncestors.length + tail.length
    }});
  }
  await bulk.execute();
}

// Alternative: $graphLookup (no precomputed ancestors)
db.org.aggregate([
  { $match: { _id: "cto" } },
  { $graphLookup: {
      from: "org",
      startWith: "$_id",
      connectFromField: "_id",
      connectToField: "parent",
      as: "subtree",
      maxDepth: 5
  }}
]);</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Pattern</th><th>Reads</th><th>Writes</th><th>Best when</th></tr></thead>
<tbody>
<tr><td>Parent reference only</td><td>Recursive (slow)</td><td>O(1)</td><td>Tree rarely traversed</td></tr>
<tr><td>Array of ancestors (this answer)</td><td>O(1) subtree query</td><td>O(N descendants) on re-parent</td><td>Read-heavy, occasional reorg</td></tr>
<tr><td>Materialized path (string)</td><td>Prefix regex; hierarchical sort</td><td>O(N descendants) on re-parent</td><td>Sorted display, depth filtering</td></tr>
<tr><td>Nested set (left/right)</td><td>O(1) subtree</td><td>O(N) on any insert</td><td>Almost-static trees</td></tr>
<tr><td><code>$graphLookup</code> at query time</td><td>Slowest</td><td>O(1) on changes</td><td>Trees changing constantly</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for graph problems beyond strict trees (matrix orgs with multiple managers, social networks, supply chains), reach for a real graph DB &mdash; <strong>Neo4j</strong>, <strong>Amazon Neptune</strong>, <strong>ArangoDB</strong>, or <strong>TigerGraph</strong> &mdash; their query languages (Cypher, Gremlin) make traversals trivial; for org charts with security context (who can see whom), pair with a permission service like <strong>SpiceDB</strong>, <strong>OpenFGA</strong>, or <strong>Cerbos</strong>; expose the tree to UIs as a flat array sorted by <code>path</code> &mdash; it lets the client render any subtree without recursion; cache hot subtrees in Redis with cache-tags for fast invalidation when the org changes.</p>
'''

ANSWERS[9] = r'''
<p><strong>Situation:</strong> a service team adds new fields and renames old ones across releases. Bad data sneaks in via misbehaving clients. The team needs MongoDB to enforce required fields, types, and value ranges &mdash; while still allowing schema evolution.</p>

<p><strong>Approach:</strong> use <strong>JSON Schema validation</strong> at the collection level. Set <code>validationLevel: "moderate"</code> during transitions so existing bad documents don&rsquo;t break old paths. Add a <code>schema_version</code> field for explicit lazy migrations. Layer with <strong>Mongoose</strong>, <strong>Zod</strong>, or <strong>Prisma</strong> on the application side for stricter front-line validation.</p>

<pre><code>// Database-level validation
db.createCollection("books", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "author_id", "schema_version"],
      properties: {
        _id:           { bsonType: "objectId" },
        schema_version:{ bsonType: "int", minimum: 1 },
        title:         { bsonType: "string", minLength: 1, maxLength: 500 },
        author_id:     { bsonType: "objectId" },
        published_year:{ bsonType: ["int", "null"], minimum: 1450, maximum: 2100 },
        price_cents:   { bsonType: "int", minimum: 0 },
        tags:          { bsonType: "array", items: { bsonType: "string" } },
        rating: {
          bsonType: "object",
          required: ["count", "avg"],
          properties: {
            count: { bsonType: "int", minimum: 0 },
            avg:   { bsonType: "double", minimum: 0, maximum: 5 }
          }
        },
        created_at:    { bsonType: "date" }
      },
      additionalProperties: false   // reject unknown fields
    }
  },
  validationLevel:  "moderate",     // strict | moderate | off
  validationAction: "error"         // error | warn (warn logs but accepts)
});

// Modify an existing collection&rsquo;s validator
db.runCommand({
  collMod: "books",
  validator: { $jsonSchema: {...} },
  validationAction: "error"
});

// Inspect documents that would fail current validation
db.books.find({ $nor: [{ $jsonSchema: {...} }] });

// Application-side schemas with Zod (catch errors before they hit DB)
import { z } from "zod";
const Book = z.object({
  schema_version: z.literal(2),
  title:          z.string().min(1).max(500),
  author_id:      z.string().regex(/^[0-9a-f]{24}$/),
  published_year: z.number().int().min(1450).max(2100).nullable(),
  price_cents:    z.number().int().nonnegative(),
  tags:           z.array(z.string()).default([]),
  rating: z.object({
    count: z.number().int().nonnegative(),
    avg:   z.number().min(0).max(5)
  })
});

async function createBook(input) {
  const parsed = Book.parse(input);
  await db.collection("books").insertOne({ ...parsed, created_at: new Date() });
}

// Schema versioning &mdash; lazy migration on read
async function getBook(id) {
  let book = await db.collection("books").findOne({ _id: id });
  if (book.schema_version === 1) {
    book = migrateV1toV2(book);
    await db.collection("books").replaceOne({ _id: id }, book);
  }
  return book;
}</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Layer</th><th>Catches</th><th>Misses</th></tr></thead>
<tbody>
<tr><td>Application (Zod, Joi, Mongoose)</td><td>Most bad input; rich errors for clients</td><td>Direct DB writes (admin tools, scripts)</td></tr>
<tr><td>$jsonSchema (DB)</td><td>Anything that reaches the DB; bypass-proof</td><td>Generic errors; no field-level message</td></tr>
<tr><td>Both layers</td><td>Defense in depth</td><td>Two places to keep in sync &mdash; generate from one source</td></tr>
<tr><td><code>validationLevel: moderate</code></td><td>Allows fixing legacy docs gradually</td><td>Old bad data stays bad until rewritten</td></tr>
<tr><td><code>additionalProperties: false</code></td><td>Catches typos like <code>titel</code></td><td>Blocks rolling deployments where new code adds fields first</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> generate <strong>$jsonSchema</strong> automatically from your TypeScript types via <strong>zod-to-json-schema</strong> &mdash; one source of truth, no drift; <strong>Mongoose</strong>, <strong>Prisma</strong>, and <strong>Drizzle</strong> are popular ODMs that bring schema and migrations on the application side; for major schema versions, run a background <strong>$merge</strong> migration job (<strong>BullMQ</strong>, <strong>Inngest</strong>, <strong>Trigger.dev</strong>, <strong>Temporal</strong>); during deployments, use <code>validationAction: "warn"</code> for one release, watch logs, then flip to <code>"error"</code>; <strong>MongoDB Atlas</strong> exposes validation failures in its monitoring &mdash; alert on spikes; <strong>Queryable Encryption (7.0+)</strong> + JSON Schema validate field-level encrypted data without decrypting.</p>
'''

ANSWERS[10] = r'''
<p><strong>Situation:</strong> a content management system needs every change to a document to be traceable &mdash; who changed what, when, and the ability to view or restore any prior version. Compliance and editorial workflows demand it.</p>

<p><strong>Approach:</strong> the <strong>document-per-version</strong> pattern. Keep the latest revision in <code>documents</code>; on every write, copy the previous state into a <code>document_versions</code> collection with a <code>doc_id</code> + <code>version</code> compound key. Bonus: add JSON-patch deltas for compact storage and clear diffs.</p>

<pre><code>db.documents.insertOne({
  _id: ObjectId(),
  current_version: 1,
  title: "Initial Title",
  body: "...",
  status: "draft",
  updated_by: ObjectId("user_alice"),
  updated_at: new Date()
});

db.document_versions.insertOne({
  _id: ObjectId(),
  doc_id:    ObjectId("..."),
  version:   1,
  snapshot:  { title: "Initial Title", body: "...", status: "draft" },
  patch:     null,                   // first version has no patch
  changed_by: ObjectId("user_alice"),
  changed_at: new Date(),
  comment:   "created"
});

db.document_versions.createIndex(
  { doc_id: 1, version: -1 },
  { unique: true }
);

// Update flow &mdash; in a transaction for atomicity
import { applyPatch, compare } from "fast-json-patch";

async function updateDoc(docId, changes, userId, comment) {
  const session = client.startSession();
  await session.withTransaction(async () =&gt; {
    const current = await db.collection("documents")
      .findOne({ _id: docId }, { session });
    if (!current) throw new Error("not found");

    const newDoc = { ...current, ...changes };
    const patch  = compare(current, newDoc);   // RFC 6902 diff

    // Bump current
    await db.collection("documents").updateOne(
      { _id: docId, current_version: current.current_version }, // optimistic lock
      { $set: { ...changes,
                current_version: current.current_version + 1,
                updated_by: userId,
                updated_at: new Date() } },
      { session }
    );

    // Snapshot the previous version
    await db.collection("document_versions").insertOne({
      doc_id:    docId,
      version:   current.current_version,
      snapshot:  current,
      patch:     null,                    // first prev = full snapshot
      changed_by:userId,
      changed_at:new Date(),
      comment
    }, { session });
  });
  await session.endSession();
}

// Read history
db.document_versions.find({ doc_id: docId })
                    .sort({ version: -1 })
                    .limit(50);

// Restore to version N
async function restore(docId, version, userId) {
  const v = await db.collection("document_versions")
    .findOne({ doc_id: docId, version });
  await updateDoc(docId, v.snapshot, userId, `restored to v${version}`);
}

// Compact storage variant: store deltas instead of full snapshots
//   reconstruct by walking forward from the nearest snapshot, applying patches</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Pattern</th><th>Pros</th><th>Cons</th></tr></thead>
<tbody>
<tr><td>Full snapshot per version</td><td>Trivial to read any version</td><td>Storage explodes if docs are large</td></tr>
<tr><td>JSON-patch deltas</td><td>Compact; clear diff for review UI</td><td>Reconstructing version N requires walking</td></tr>
<tr><td>Hybrid (snapshot every N, deltas between)</td><td>Bounded reconstruction cost; reasonable storage</td><td>More code complexity</td></tr>
<tr><td>Embedded versions array on doc</td><td>One read for full history</td><td>Document grows without bound &mdash; 16MB cap hits</td></tr>
<tr><td>Optimistic locking via <code>current_version</code></td><td>Detects concurrent updates without explicit locks</td><td>Caller must retry on conflict</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for editorial workflows, integrate a CRDT-based approach via <strong>Yjs</strong> or <strong>Automerge</strong> &mdash; they handle concurrent edits without conflicts and produce natural version histories; storage backends like <strong>HocusPocus</strong> or <strong>Liveblocks</strong> manage server-side persistence; for binary content (images, PDFs), version metadata in MongoDB but store payloads in <strong>S3</strong>/<strong>Cloudflare R2</strong>/<strong>Backblaze B2</strong> with versioning enabled at the bucket level &mdash; cheaper and immutable; archive old versions to <strong>Atlas Online Archive</strong> after, say, 1 year &mdash; full search still works; for compliance, set bucket-level <strong>S3 Object Lock</strong> for tamper-proof retention.</p>
'''

ANSWERS[11] = r'''
<p><strong>Situation:</strong> the product wants to track user activity &mdash; logins, page views, button clicks, feature usage &mdash; and store it in MongoDB for analytics, debugging, and compliance. Volume is high (10k+ events/sec at peak); reads are mostly recent windows.</p>

<p><strong>Approach:</strong> use a <strong>time-series collection (5.0+)</strong> for raw events &mdash; auto-bucketed and compressed. Keep recent days hot; archive cold data via <strong>Atlas Online Archive</strong>. Roll up to summaries via scheduled <code>$merge</code> aggregations for dashboards.</p>

<pre><code>// 1. Create time-series collection &mdash; perfect fit for activity logs
db.createCollection("activity_events", {
  timeseries: {
    timeField:   "ts",
    metaField:   "user_id",     // every event for a user buckets together
    granularity: "seconds"      // seconds | minutes | hours; auto for large bursts
  },
  expireAfterSeconds: 90 * 24 * 3600  // auto-purge after 90 days
});

db.activity_events.insertMany([
  {
    ts:        new Date(),
    user_id:   ObjectId("..."),
    event:     "page_view",
    path:      "/dashboard",
    session_id: "abc123",
    ip:        BinData(...),
    ua_family: "Chrome",
    metadata:  { referrer: "https://google.com" }
  },
  {
    ts:        new Date(),
    user_id:   ObjectId("..."),
    event:     "feature_use",
    feature:   "export_csv",
    metadata:  { row_count: 4200 }
  }
]);

// Indexes (time-series collections support secondary indexes since 6.0)
db.activity_events.createIndex({ event: 1, ts: -1 });
db.activity_events.createIndex({ user_id: 1, ts: -1 });

// 2. Hot reads &mdash; recent activity for a user
db.activity_events.find({
  user_id: userId,
  ts: { $gte: new Date(Date.now() - 24*3600*1000) }
}).sort({ ts: -1 }).limit(100);

// 3. Daily rollups for dashboards
db.activity_events.aggregate([
  { $match: { ts: { $gte: yesterday, $lt: today } } },
  { $group: {
      _id: {
        day:   { $dateTrunc: { date: "$ts", unit: "day" } },
        event: "$event"
      },
      count: { $sum: 1 },
      unique_users: { $addToSet: "$user_id" }
  }},
  { $project: {
      _id: 1,
      count: 1,
      unique_user_count: { $size: "$unique_users" }
  }},
  { $merge: {
      into: "activity_daily",
      on: "_id",
      whenMatched: "replace"
  }}
]);

// 4. Per-user activity summary (refreshed nightly)
db.activity_events.aggregate([
  { $match: { ts: { $gte: thirtyDaysAgo } } },
  { $group: {
      _id: "$user_id",
      event_count_30d: { $sum: 1 },
      last_seen: { $max: "$ts" },
      events_by_type: { $push: "$event" }
  }},
  { $merge: { into: "user_activity_summary", on: "_id", whenMatched: "replace" } }
]);

// 5. High-throughput pattern &mdash; queue then bulk-insert
import { Queue, Worker } from "bullmq";
const q = new Queue("events");
// API server: just push to queue
await q.add("event", payload);
// Worker: drain in batches every 1s or 1000 events
const worker = new Worker("events", async batch =&gt; {
  await db.collection("activity_events").insertMany(batch);
});</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Time-series collection</td><td>5-10x storage savings; built-in bucketing</td><td>Regular collection &mdash; works but bigger and slower for time queries</td></tr>
<tr><td><code>metaField: user_id</code></td><td>One user&rsquo;s events colocate; per-user reads are sequential</td><td>No metaField &mdash; OK for global queries, slower for per-user</td></tr>
<tr><td>TTL via <code>expireAfterSeconds</code></td><td>Self-managing; no cleanup job</td><td>Manual delete &mdash; forget it once, disk fills</td></tr>
<tr><td>Materialize daily rollups</td><td>Dashboards read 30 docs, not 30M raw events</td><td>Compute on every dashboard load &mdash; expensive and slow</td></tr>
<tr><td>Async ingestion via queue</td><td>API never blocks on event write; smooths bursts</td><td>Sync writes &mdash; spikes propagate to user latency</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for analytics-grade workloads (billions of events, ad-hoc SQL), pipe to a warehouse &mdash; <strong>BigQuery</strong>, <strong>Snowflake</strong>, <strong>ClickHouse</strong>, or <strong>Databricks</strong> &mdash; via <strong>Airbyte</strong>, <strong>Fivetran</strong>, or change streams; product analytics tools like <strong>Amplitude</strong>, <strong>Mixpanel</strong>, <strong>PostHog</strong>, or <strong>Heap</strong> are typically a better fit than home-grown dashboards; use <strong>Segment</strong> or <strong>RudderStack</strong> as a single ingestion pipe to fan out to all destinations; <strong>OpenTelemetry</strong> for distributed tracing complements but doesn&rsquo;t replace event tracking; PII fields (IP, user agent) need a retention policy and may require encryption at rest under GDPR/CCPA.</p>
'''

ANSWERS[12] = r'''
<p><strong>Situation:</strong> store and query time-series data in MongoDB &mdash; sensor readings, financial ticks, application metrics, IoT telemetry. Volume is high (millions of points per day per source), queries focus on recent windows and aggregations like &ldquo;avg per minute&rdquo;.</p>

<p><strong>Approach:</strong> the <strong>time-series collection</strong> (5.0+) is purpose-built &mdash; documents are auto-bucketed, compressed (zstd), and queried via the standard query/aggregation API. Use <code>$dateTrunc</code> + <code>$group</code> for time-bucketed analytics. For very high cardinality, complement with a dedicated tool.</p>

<pre><code>// Create the time-series collection
db.createCollection("sensor_readings", {
  timeseries: {
    timeField:   "ts",
    metaField:   "sensor",        // {device_id, type, location} groups together
    granularity: "minutes"        // hint &mdash; affects bucketing efficiency
  },
  expireAfterSeconds: 365 * 24 * 3600   // auto-purge after 1 year
});

// Insert &mdash; meta + time + measurement
db.sensor_readings.insertMany([
  {
    ts: new Date("2026-04-28T10:00:00Z"),
    sensor: { device_id: "dev-001", type: "temp", location: "warehouse-a" },
    value: 21.5,
    unit: "C"
  },
  {
    ts: new Date("2026-04-28T10:00:30Z"),
    sensor: { device_id: "dev-001", type: "temp", location: "warehouse-a" },
    value: 21.6,
    unit: "C"
  }
]);

db.sensor_readings.createIndex({ "sensor.device_id": 1, ts: -1 });
db.sensor_readings.createIndex({ "sensor.type": 1, ts: -1 });

// Per-device, last 24h
db.sensor_readings.find({
  "sensor.device_id": "dev-001",
  ts: { $gte: new Date(Date.now() - 24*3600*1000) }
}).sort({ ts: -1 });

// 1-minute bucketed averages (with $dateTrunc)
db.sensor_readings.aggregate([
  { $match: {
      "sensor.device_id": "dev-001",
      ts: { $gte: new Date(Date.now() - 6*3600*1000) }
  }},
  { $group: {
      _id: { $dateTrunc: { date: "$ts", unit: "minute", binSize: 1 } },
      avg_value: { $avg: "$value" },
      min_value: { $min: "$value" },
      max_value: { $max: "$value" },
      count:     { $sum: 1 }
  }},
  { $sort: { _id: 1 } }
]);

// Window functions ($setWindowFields, 5.0+) &mdash; rolling averages
db.sensor_readings.aggregate([
  { $match: { "sensor.device_id": "dev-001" } },
  { $sort:  { ts: 1 } },
  { $setWindowFields: {
      partitionBy: "$sensor.device_id",
      sortBy: { ts: 1 },
      output: {
        rolling_avg_5min: {
          $avg: "$value",
          window: { range: [-5, 0], unit: "minute" }
        }
      }
  }}
]);

// Continuous downsampling: 5-minute rollups via $merge
db.sensor_readings.aggregate([
  { $match: { ts: { $gte: lastFiveMinutes } } },
  { $group: {
      _id: {
        device: "$sensor.device_id",
        bucket: { $dateTrunc: { date: "$ts", unit: "minute", binSize: 5 } }
      },
      avg_value: { $avg: "$value" },
      count:     { $sum: 1 }
  }},
  { $merge: { into: "sensor_readings_5m", on: "_id", whenMatched: "replace" } }
]);</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Time-series collection</td><td>Built-in bucketing &amp; compression; up to 90% storage savings</td><td>Regular collection &mdash; bigger, no time-aware optimizations</td></tr>
<tr><td><code>metaField</code> on sensor doc</td><td>Same-sensor data colocates; range scans are sequential</td><td>Time-only ordering &mdash; cross-sensor reads dominate, slower</td></tr>
<tr><td><code>$dateTrunc</code> for buckets</td><td>Calendar-aware; handles DST and month boundaries cleanly</td><td>Manual modulo math &mdash; brittle</td></tr>
<tr><td>Continuous 5m/1h rollups</td><td>Dashboards on 30-day windows query thousands, not millions</td><td>Compute on every dashboard load &mdash; slow and expensive</td></tr>
<tr><td>TTL on raw events</td><td>Self-cleaning; rollups stay forever</td><td>Manual purge cron &mdash; forget it, disk fills</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for million-points-per-second ingestion or complex anomaly detection, layer specialized tools &mdash; <strong>InfluxDB</strong>, <strong>TimescaleDB</strong>, <strong>QuestDB</strong>, or <strong>VictoriaMetrics</strong>; for application metrics specifically, <strong>Prometheus</strong> + <strong>Grafana</strong> or <strong>Datadog</strong> is the industry default; for IoT specifically, <strong>AWS IoT Core</strong> + <strong>Timestream</strong> or <strong>Azure IoT Hub</strong> + <strong>Time Series Insights</strong> handle device management plus storage; expose dashboards via <strong>Atlas Charts</strong> (built-in for MongoDB) or <strong>Grafana</strong> with the MongoDB data source plugin; alert via <strong>PagerDuty</strong>, <strong>Opsgenie</strong>, or <strong>Squadcast</strong>.</p>
'''

ANSWERS[13] = r'''
<p><strong>Situation:</strong> a product catalog with rich filtering &mdash; price range, category, brand, color, size, in-stock-only, free-shipping, average rating &mdash; combined with sort options and pagination. The UI shows facets with counts.</p>

<p><strong>Approach:</strong> for moderate scale, use compound indexes + <code>$facet</code> aggregation. For real catalog scale (10k+ products with rich faceting), mirror to <strong>Atlas Search</strong> or <strong>Elasticsearch</strong> &mdash; their faceted-search engines outclass anything you build on raw MongoDB.</p>

<pre><code>db.products.insertOne({
  _id: ObjectId(),
  name: "Running Shoes",
  category: { _id: "shoes", path: ["sports", "shoes"] },
  brand:    "Nike",
  price_cents: 9900,
  attributes: { color: "blue", size: 10, material: "mesh" },
  inventory:  { on_hand: 12 },
  rating:     { avg: 4.6, count: 230 },
  free_shipping: true,
  active: true
});

// Indexes for the most common filter combinations (ESR rule)
db.products.createIndex({ "category._id": 1, active: 1, price_cents: 1 });
db.products.createIndex({ brand: 1, active: 1 });
db.products.createIndex({ "attributes.color": 1, active: 1 });
db.products.createIndex({ "rating.avg": -1, active: 1 });

// Filter + sort + paginate query
const filter = {
  active: true,
  "category._id": "shoes",
  brand: { $in: ["Nike", "Adidas"] },
  price_cents: { $gte: 5000, $lte: 15000 },
  "attributes.color": "blue",
  "rating.avg": { $gte: 4 },
  free_shipping: true
};
const cursor = db.products.find(filter)
                          .sort({ "rating.avg": -1, _id: 1 })
                          .limit(24)
                          .skip(48);  // page 3

// Single round trip: results + facet counts
db.products.aggregate([
  { $match: { active: true, "category._id": "shoes" } },   // base filter
  { $facet: {
      results: [
        { $match: filter },
        { $sort:  { "rating.avg": -1, _id: 1 } },
        { $skip:  48 }, { $limit: 24 }
      ],
      brand_counts: [
        { $group: { _id: "$brand", count: { $sum: 1 } } },
        { $sort:  { count: -1 } }
      ],
      color_counts: [
        { $group: { _id: "$attributes.color", count: { $sum: 1 } } }
      ],
      price_buckets: [
        { $bucket: {
            groupBy: "$price_cents",
            boundaries: [0, 5000, 10000, 20000, 50000, 100000],
            default: "100000+",
            output: { count: { $sum: 1 } }
        }}
      ],
      total: [{ $count: "n" }]
  }}
]);

// Cursor pagination at depth (faster than skip beyond page 5)
db.products.find({ ...filter, _id: { $gt: lastSeenId } })
           .sort({ "rating.avg": -1, _id: 1 })
           .limit(24);

// Atlas Search variant &mdash; production-grade faceting
db.products.aggregate([
  { $search: {
      index: "products",
      compound: {
        filter: [
          { equals: { path: "active", value: true } },
          { equals: { path: "category._id", value: "shoes" } },
          { range: { path: "price_cents", gte: 5000, lte: 15000 } },
          { equals: { path: "attributes.color", value: "blue" } }
        ],
        should: [
          { text: { query: searchQuery, path: ["name", "description"] } }
        ]
      }
  }},
  { $facet: { ... } }
]);</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Approach</th><th>Best for</th><th>Limit</th></tr></thead>
<tbody>
<tr><td>Compound indexes + <code>$facet</code></td><td>Up to ~100k products, &lt;10 facets</td><td>Index combinatorics blow up; large <code>$group</code> stages slow</td></tr>
<tr><td>Atlas Search</td><td>Any catalog scale, fuzzy text + faceting</td><td>Per-search-index pricing; mirror lag</td></tr>
<tr><td>Elasticsearch / OpenSearch</td><td>Self-hosted; richest faceting</td><td>Operational complexity, separate cluster</td></tr>
<tr><td>Algolia / Meilisearch / Typesense</td><td>Hosted, blazing fast for catalog UIs</td><td>Cost scales with traffic; another moving part</td></tr>
<tr><td>Cursor pagination</td><td>Any depth without performance cliff</td><td>Doesn&rsquo;t support &ldquo;jump to page N&rdquo; UI</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for any serious catalog, mirror products to a dedicated search index &mdash; <strong>MongoDB Atlas Search</strong> is the lowest-friction choice (declared inside Atlas, no separate cluster); <strong>Algolia</strong>, <strong>Meilisearch</strong>, and <strong>Typesense</strong> are hosted alternatives; sync via <strong>change streams</strong> in near-real-time; cache hot category landing pages in <strong>Redis</strong> with cache-tags for invalidation on product update; track click-through and conversion per facet via <strong>Amplitude</strong>/<strong>PostHog</strong> to tune ordering; use <strong>cursor pagination</strong> &mdash; <code>skip</code> degrades quadratically past page 10.</p>
'''

ANSWERS[14] = r'''
<p><strong>Situation:</strong> design a social platform with users, posts, likes, and comments. Reads dominate (timeline rendering); writes are bursty (likes during viral moments). Schema must support timelines, profile pages, search, and notifications.</p>

<p><strong>Approach:</strong> separate <code>users</code>, <code>posts</code>, <code>follows</code>, and <code>comments</code>. Likes are a <code>$addToSet</code> array on the post, with denormalized counts. Timeline generation uses a hybrid <strong>fan-out-on-write</strong> for active users and <strong>fan-out-on-read</strong> for celebrities (the &ldquo;Twitter problem&rdquo;).</p>

<pre><code>db.users.insertOne({
  _id: ObjectId(),
  username: "alice",
  display_name: "Alice",
  bio: "Product designer",
  followers_count: 0,
  following_count: 0,
  created_at: new Date()
});

db.follows.insertOne({
  _id: ObjectId(),
  follower_id:  ObjectId("alice"),
  followee_id:  ObjectId("bob"),
  created_at:   new Date()
});
db.follows.createIndex({ follower_id: 1, followee_id: 1 }, { unique: true });
db.follows.createIndex({ followee_id: 1, created_at: -1 });

db.posts.insertOne({
  _id: ObjectId(),
  author: { _id: ObjectId(), username: "alice", display_name: "Alice" },  // snapshot
  body:   "Hello world",
  media:  [{ type: "image", url: "https://cdn.../img.jpg" }],
  likes_count:    0,
  comments_count: 0,
  created_at:     new Date()
});
db.posts.createIndex({ "author._id": 1, created_at: -1 });

db.likes.insertOne({   // separate collection scales better than embedded array
  _id: ObjectId(),
  post_id: ObjectId("..."),
  user_id: ObjectId("..."),
  created_at: new Date()
});
db.likes.createIndex({ post_id: 1, user_id: 1 }, { unique: true });
db.likes.createIndex({ user_id: 1, created_at: -1 });

db.comments.insertOne({
  _id: ObjectId(),
  post_id: ObjectId("..."),
  author:  { _id: ObjectId(), username: "bob", display_name: "Bob" },
  body:    "Great post!",
  reply_to: null,
  created_at: new Date()
});
db.comments.createIndex({ post_id: 1, created_at: 1 });

// Like a post atomically (prevent double-likes)
async function likePost(postId, userId) {
  try {
    await db.collection("likes").insertOne({
      post_id: postId, user_id: userId, created_at: new Date()
    });
    await db.collection("posts").updateOne(
      { _id: postId },
      { $inc: { likes_count: 1 } }
    );
  } catch (e) {
    if (e.code === 11000) return;  // duplicate &mdash; already liked
    throw e;
  }
}

// Timeline: hybrid fan-out
//   - Active users: precompute timelines on every post (push model)
//   - Celebrities (&gt;100k followers): pull at read time

db.timelines.insertOne({
  _id: ObjectId("user_alice"),         // _id = user_id
  posts: [/* recent 200 post snapshots */]
});

// On post creation by a non-celebrity
async function fanoutOnWrite(post) {
  const followers = db.collection("follows").find({ followee_id: post.author._id });
  for await (const f of followers) {
    await db.collection("timelines").updateOne(
      { _id: f.follower_id },
      { $push: { posts: { $each: [post], $sort: { created_at: -1 }, $slice: 200 } } }
    );
  }
}

// Read timeline for normal user &mdash; one indexed read
db.timelines.findOne({ _id: userId });

// For celebrity follows, mix in their posts at read time
const celebrityPosts = await db.collection("posts").find({
  "author._id": { $in: celebrityIdsUserFollows }
}).sort({ created_at: -1 }).limit(50).toArray();</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Likes in separate collection</td><td>Unbounded; needs &ldquo;has user X liked post Y?&rdquo; query</td><td>Embedded array &mdash; doc grows unbounded</td></tr>
<tr><td>Denormalized counts</td><td>Profile/timeline render in one read</td><td>Live <code>countDocuments</code> &mdash; slow at scale</td></tr>
<tr><td>Fan-out on write (push)</td><td>Reads are O(1) per user</td><td>Pull on read &mdash; slow for users following thousands</td></tr>
<tr><td>Fan-out on read for celebs</td><td>Avoids 100M timeline writes per Taylor Swift post</td><td>Pure push &mdash; collapses on celebrity events</td></tr>
<tr><td>Snapshot author on post</td><td>Timeline renders without joining users</td><td>Live $lookup &mdash; slower; user changes display name</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> at real social scale, MongoDB is the system of record but timelines move to <strong>Redis</strong> sorted sets (per-user ZSET, score=timestamp); <strong>Cassandra</strong> is the classic choice for fan-out-on-write because of its blazing write throughput; for notifications fan-out, use <strong>BullMQ</strong>/<strong>Kafka</strong> + push services like <strong>Firebase Cloud Messaging</strong>, <strong>OneSignal</strong>, or <strong>APNs</strong>; mirror posts to <strong>Atlas Search</strong> or <strong>Elasticsearch</strong> for content search and trending hashtags; recommendation feed (vs. follow graph) needs <strong>Atlas Vector Search</strong>/<strong>Pinecone</strong> with content embeddings; abuse detection via <strong>Perspective API</strong> or in-house ML on <strong>Modal</strong>/<strong>Replicate</strong>.</p>
'''

ANSWERS[15] = r'''
<p><strong>Situation:</strong> a single-collection workload has grown past what one server can hold or one node&rsquo;s RAM can cache. Reads slow down, writes contend, and replication lag creeps up. The team needs to partition data horizontally.</p>

<p><strong>Approach:</strong> <strong>sharding</strong>. Pick a shard key carefully &mdash; it determines distribution, query routing, and write-hotspot behavior. Combine with replication so each shard is a 3-node replica set. Premature sharding causes more pain than it solves &mdash; vertical scaling and indexing typically come first.</p>

<pre><code>// Enable sharding on a database
sh.enableSharding("shop");

// Shard the orders collection
// Best practice (4.4+): use a hashed prefix + secondary monotonic field
sh.shardCollection(
  "shop.orders",
  { user_id: "hashed", placed_at: 1 }   // compound shard key
);
// Reads by user_id route to ONE shard (efficient)
// Reads by placed_at scatter across shards (acceptable for analytics)

// Alternative: range sharding for time-bucketed queries
sh.shardCollection("shop.events", { tenant_id: 1, ts: 1 });

// Inspect chunks
sh.status();
db.adminCommand({ listShards: 1 });

// Reshard (5.0+) &mdash; live shard key change without downtime
db.adminCommand({
  reshardCollection: "shop.orders",
  key: { user_id: "hashed", placed_at: 1 }
});

// Pre-split for known data &mdash; avoids initial balancing storm
sh.splitAt("shop.orders", { user_id: "hashed_value_1" });
sh.splitAt("shop.orders", { user_id: "hashed_value_2" });

// Move chunk to a specific shard manually
sh.moveChunk("shop.orders", { user_id: "hashed_value_1" }, "shard02");

// Check distribution of data across shards
db.orders.getShardDistribution();

// Targeted vs scatter-gather queries
//   Targeted (fast):    queries that include the shard key
db.orders.find({ user_id: ObjectId("...") });

//   Scatter-gather (slow): queries without the shard key
db.orders.find({ status: "pending" });   // hits every shard

// Routing-aware aggregation
db.orders.aggregate([
  { $match: { user_id: ObjectId("...") } },  // targeted
  { $group: { _id: "$status", count: { $sum: 1 } } }
]);

// Tag-aware sharding for geo or compliance &mdash; route EU data to EU shards
sh.addShardTag("shard-eu", "EU");
sh.addTagRange("shop.users", { country: "DE" }, { country: "DE\uFFFF" }, "EU");</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Shard key choice</th><th>Pros</th><th>Cons</th></tr></thead>
<tbody>
<tr><td>Hashed (e.g. <code>{ user_id: "hashed" }</code>)</td><td>Even distribution; no hotspots</td><td>Range queries scatter; no locality</td></tr>
<tr><td>Range (e.g. <code>{ created_at: 1 }</code>)</td><td>Range queries targeted; locality for analytics</td><td>Monotonic key &rarr; one shard takes all writes (hotspot)</td></tr>
<tr><td>Compound hashed + range</td><td>Write distribution + reasonable locality</td><td>Range without prefix still scatters</td></tr>
<tr><td>Per-tenant <code>{ tenant_id: 1, _id: 1 }</code></td><td>Tenant data colocates &mdash; great for SaaS</td><td>Big-tenant problem &mdash; one tenant fills one shard</td></tr>
<tr><td>Tag-aware sharding</td><td>Geo-residency &amp; compliance; hot/cold tiers</td><td>Manual chunk-balancing rules</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> in <strong>MongoDB Atlas</strong>, sharded clusters are turnkey &mdash; no <code>mongos</code>/<code>config server</code> ops; for self-hosted, <strong>Percona Distribution for MongoDB</strong> or the <strong>MongoDB Kubernetes Operator</strong> manage the topology; pre-split before bulk loads (importing 100GB onto a single shard then waiting for the balancer kills performance); monitor <code>db.adminCommand({balancerStatus: 1})</code> and chunk-migration rate via <strong>Datadog</strong> or <strong>Atlas Charts</strong>; <strong>Atlas Global Clusters</strong> automate tag-aware sharding for geo-distribution; consider alternatives before sharding &mdash; vertical scaling, dropping unused indexes, fixing N+1 queries, archiving cold data via <strong>Atlas Online Archive</strong> &mdash; sharding is operationally heavy.</p>
'''

ANSWERS[16] = r'''
<p><strong>Situation:</strong> ensure a MongoDB deployment survives node failures, datacenter outages, and full regional disasters with bounded data loss (RPO) and recovery time (RTO). Compliance mandates daily backups and tested recovery.</p>

<p><strong>Approach:</strong> <strong>3-node replica set as the baseline</strong> for HA; add cross-region replication for DR; use <strong>Atlas Continuous Backup</strong> (or self-hosted equivalents) for point-in-time recovery. Test restores quarterly &mdash; backups you haven&rsquo;t restored from are wishful thinking, not insurance.</p>

<pre><code>// Replica set config &mdash; 3 voting members minimum, geographically diverse
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-a-1.example.com:27017", priority: 2 },     // primary preferred
    { _id: 1, host: "mongo-a-2.example.com:27017", priority: 1 },     // same region
    { _id: 2, host: "mongo-b-1.example.com:27017", priority: 1 }      // different region
  ]
});

// Add a hidden secondary in a 3rd region for DR (priority 0, doesn&rsquo;t take traffic)
rs.add({
  _id: 3,
  host: "mongo-c-1.example.com:27017",
  priority: 0,
  hidden: true,
  votes: 0,
  tags: { region: "us-west-2", role: "dr" }
});

// Verify
rs.status();          // health, optime, lag per member
rs.printSecondaryReplicationInfo();   // per-member lag in seconds

// Read preferences &mdash; client-side
const client = new MongoClient(uri, {
  readPreference: "secondaryPreferred",
  readConcernLevel: "majority",
  writeConcern: { w: "majority", wtimeoutMS: 5000 }
});

// Backups
//   Atlas: enable Continuous Backup &mdash; point-in-time restore to any moment
//   Self-hosted: mongodump for logical, file-system snapshot for binary
//
//   Logical backup (slow on large data, but portable)
mongodump --uri="mongodb://..." --out=/backups/$(date +%F) --gzip --oplog

//   File-system snapshot (fast; needs filesystem support)
//     1. fsync &amp; lock the secondary
//     2. snapshot the EBS/zfs volume
//     3. unlock
db.fsyncLock();
// snapshot now
db.fsyncUnlock();

//   Percona Backup for MongoDB (PBM) &mdash; open-source, distributed, point-in-time
pbm config --set storage.type=s3 --set storage.s3.bucket=my-mongo-backups
pbm backup
pbm restore 2026-04-28T12:00:00Z

// Test restores quarterly to a parallel environment
mongorestore --uri="mongodb://staging-cluster" /backups/2026-04-28/ --gzip

// Disaster recovery drills
//   1. Simulate primary loss &mdash; verify automatic election within 12s
//   2. Simulate region loss &mdash; promote DR replica, repoint apps
//   3. Validate RTO/RPO &mdash; how long until reads/writes resumed; how much data lost</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Strategy</th><th>RPO</th><th>RTO</th><th>Cost</th></tr></thead>
<tbody>
<tr><td>3-node replica set, single region</td><td>~0 (sync replication)</td><td>~12s (auto-elect)</td><td>Low</td></tr>
<tr><td>+ cross-region hidden secondary</td><td>seconds (async to DR)</td><td>minutes (manual promote)</td><td>Medium</td></tr>
<tr><td>+ Atlas continuous backup</td><td>seconds (oplog stream)</td><td>minutes (point-in-time restore)</td><td>Storage cost grows with retention</td></tr>
<tr><td>Atlas Global Cluster (multi-region active)</td><td>~0 within zone, eventual cross-region</td><td>~0 (already serving traffic everywhere)</td><td>Higher; multi-region latency on writes</td></tr>
<tr><td>Daily logical dumps to S3</td><td>up to 24h</td><td>hours (restore time scales with data)</td><td>Low; needs Object Lock for ransomware</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> <strong>Atlas Continuous Backup</strong> is the simplest production answer &mdash; oplog-tailing for second-level RPO, point-in-time restore, automatic encryption, geo-redundant storage; self-hosted, <strong>Percona Backup for MongoDB (PBM)</strong> is the open-source equivalent; back up the <strong>Ops Manager</strong> or operator state too if you self-manage; for ransomware resilience, store backups in a separate AWS account with <strong>S3 Object Lock</strong> in compliance mode &mdash; prevents deletion even by root; document the runbook &mdash; what to do, in what order, with which credentials &mdash; and rehearse it; <strong>Datadog</strong>, <strong>PagerDuty</strong>, <strong>Atlas Alerts</strong> for replication-lag and oplog-window alarms.</p>
'''

ANSWERS[17] = r'''
<p><strong>Situation:</strong> a project management tool with projects, tasks, and users. Users belong to multiple projects with roles (owner, editor, viewer); tasks have assignees, due dates, dependencies, and comments. Reads dominate (board views); writes happen on every drag-drop.</p>

<p><strong>Approach:</strong> three core collections (<code>projects</code>, <code>tasks</code>, <code>users</code>) plus a <code>project_members</code> join collection for role assignments. Embed comments on tasks; reference users with snapshots. Index for the two hot queries: tasks-in-project and tasks-assigned-to-user.</p>

<pre><code>db.users.insertOne({
  _id: ObjectId(),
  email: "alice@example.com",
  display_name: "Alice",
  avatar_url: "https://...",
  active: true
});

db.projects.insertOne({
  _id: ObjectId(),
  name: "Q2 Roadmap",
  slug: "q2-roadmap",
  description: "...",
  status: "active",          // active | archived
  visibility: "private",
  created_by: ObjectId("alice"),
  created_at: new Date()
});

db.project_members.insertOne({
  _id: ObjectId(),
  project_id: ObjectId("..."),
  user_id:    ObjectId("..."),
  role:       "editor",       // owner | editor | viewer
  added_at:   new Date()
});
db.project_members.createIndex({ project_id: 1, user_id: 1 }, { unique: true });
db.project_members.createIndex({ user_id: 1 });   // &ldquo;projects I belong to&rdquo;

db.tasks.insertOne({
  _id: ObjectId(),
  project_id: ObjectId("..."),
  title: "Wire up auth",
  description: "...",
  status: "in_progress",      // todo | in_progress | review | done
  priority: "high",           // low | medium | high
  assignee: {                 // snapshot
    _id: ObjectId("..."),
    display_name: "Alice",
    avatar_url: "..."
  },
  due_date: ISODate("2026-05-15"),
  labels: ["backend", "security"],
  dependencies: [ObjectId("..."), ObjectId("...")],   // task ids that must complete first
  comments: [
    {
      _id: ObjectId(),
      author: { _id: ObjectId("..."), display_name: "Bob" },
      body: "Started today",
      created_at: new Date()
    }
  ],
  comments_count: 1,
  position: 1024,             // for drag-drop ordering within column
  created_at: new Date(),
  updated_at: new Date()
});

// Indexes
db.tasks.createIndex({ project_id: 1, status: 1, position: 1 });   // board view
db.tasks.createIndex({ "assignee._id": 1, due_date: 1 });          // &ldquo;my tasks&rdquo;
db.tasks.createIndex({ project_id: 1, due_date: 1 });              // upcoming
db.tasks.createIndex({ labels: 1, project_id: 1 });                // tag filtering

// Board view &mdash; one indexed read per column
db.tasks.find({ project_id: pid, status: "in_progress" })
        .sort({ position: 1 });

// Drag-drop reorder &mdash; sparse position trick (avoid mass renumbering)
db.tasks.updateOne(
  { _id: taskId },
  { $set: { status: "review", position: 1500, updated_at: new Date() } }
);

// Add a comment atomically
db.tasks.updateOne(
  { _id: taskId },
  {
    $push: { comments: comment },
    $inc:  { comments_count: 1 },
    $set:  { updated_at: new Date() }
  }
);

// Permission check: is user X a member of project Y?
db.project_members.findOne({ project_id: pid, user_id: uid });</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Separate <code>project_members</code></td><td>Roles change; many-to-many; needs reverse lookup (user&rsquo;s projects)</td><td>Embed members on project &mdash; works for tiny projects; ugly for large teams</td></tr>
<tr><td>Embed comments on task</td><td>Bounded; always read with the task</td><td>Separate <code>comments</code> &mdash; needed if discussions exceed 1000</td></tr>
<tr><td>Sparse positions (1024-step)</td><td>O(1) reorder &mdash; just pick midpoint between neighbors</td><td>Sequential ints &mdash; require mass renumbering on every reorder</td></tr>
<tr><td>Snapshot assignee fields</td><td>Board renders without user joins</td><td>Live <code>$lookup</code> &mdash; slower; assignee changes are rare</td></tr>
<tr><td>Dependencies as id array on task</td><td>Trivial to read; supports DAG validation server-side</td><td>Separate edges collection &mdash; needed if DAG queries dominate</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for real-time multi-user board updates, layer <strong>change streams</strong> + <strong>WebSockets</strong> (or hosted: <strong>Pusher</strong>, <strong>Ably</strong>, <strong>Liveblocks</strong>); collaborative editing of task descriptions belongs in <strong>Yjs</strong>/<strong>Automerge</strong> via <strong>HocusPocus</strong>; permission service grows fast &mdash; consider <strong>SpiceDB</strong>, <strong>OpenFGA</strong>, or <strong>Cerbos</strong> for role-based access on tasks/projects/comments; mirror tasks to <strong>Atlas Search</strong> for &ldquo;search across all projects I&rsquo;m in&rdquo;; export to <strong>Linear</strong>/<strong>Notion</strong>/<strong>Jira</strong> via webhook fanout if integration is core; analytics on time-to-close, throughput &mdash; pipe events to <strong>Mixpanel</strong>/<strong>PostHog</strong> or <strong>Snowflake</strong>.</p>
'''

ANSWERS[18] = r'''
<p><strong>Situation:</strong> two clients update the same document at nearly the same time. Without coordination, one update silently overwrites the other (lost-update problem). Need a strategy that fits MongoDB&rsquo;s document-level atomicity.</p>

<p><strong>Approach:</strong> three options, picked based on conflict frequency: (1) <strong>atomic field updates</strong> with <code>$inc</code>/<code>$push</code>/<code>$addToSet</code> &mdash; the document is the lock unit; (2) <strong>optimistic concurrency control</strong> via a version field for update-if-unchanged semantics; (3) <strong>multi-document transactions</strong> for cross-document atomicity. Pessimistic locking is rare in MongoDB &mdash; usually a code smell.</p>

<pre><code>// 1. Atomic operators &mdash; safe by default
//    Two clients incrementing likes_count by 1 always end up at +2
db.posts.updateOne({ _id: pid }, { $inc: { likes_count: 1 } });

//    Atomic add-to-set, no duplicates even with race
db.posts.updateOne({ _id: pid }, { $addToSet: { liked_by: userId } });

//    Atomic push with cap (rolling buffer)
db.posts.updateOne(
  { _id: pid },
  { $push: { recent_likers: { $each: [userId], $slice: -100 } } }
);

// 2. Optimistic concurrency &mdash; for read-modify-write
//    Add a `version` field; bump on every update; refuse stale updates
async function updateTitle(postId, newTitle) {
  const post = await db.collection("posts").findOne({ _id: postId });
  const r = await db.collection("posts").updateOne(
    { _id: postId, version: post.version },          // expect THIS version
    { $set: { title: newTitle }, $inc: { version: 1 } }
  );
  if (r.matchedCount === 0) {
    throw new Error("Stale update; retry");
  }
}

// Auto-retry pattern
async function withOptimisticRetry(fn, maxAttempts = 3) {
  for (let i = 0; i &lt; maxAttempts; i++) {
    try { return await fn(); }
    catch (e) {
      if (e.message === "Stale update; retry" &amp;&amp; i &lt; maxAttempts - 1) continue;
      throw e;
    }
  }
}

// 3. findOneAndUpdate &mdash; atomic read+write, returns the updated (or pre-update) doc
const after = await db.collection("orders").findOneAndUpdate(
  { _id: orderId, status: "pending" },               // guard
  { $set: { status: "paid", paid_at: new Date() } },
  { returnDocument: "after" }
);
if (!after) throw new Error("Order was not pending");

// 4. Multi-document transactions &mdash; cross-doc atomicity
const session = client.startSession();
await session.withTransaction(async () =&gt; {
  await db.collection("accounts").updateOne(
    { _id: from }, { $inc: { balance: -100 } },
    { session }
  );
  await db.collection("accounts").updateOne(
    { _id: to }, { $inc: { balance: 100 } },
    { session }
  );
  // Auto-retries on TransientTransactionError
});
await session.endSession();

// 5. Distributed lock for very-rare cross-doc serialization (Redis or Mongo doc)
db.locks.updateOne(
  { _id: "rebuild_search_index" },
  { $setOnInsert: { acquired_at: new Date(), holder: hostname } },
  { upsert: true }
);</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Strategy</th><th>Best for</th><th>Cost</th></tr></thead>
<tbody>
<tr><td>Atomic field operators</td><td>Counters, set membership, capped pushes</td><td>None &mdash; always safe</td></tr>
<tr><td>Optimistic <code>version</code> field</td><td>Read-modify-write on full docs; rare conflicts</td><td>Caller retries on conflict; storage of one int</td></tr>
<tr><td><code>findOneAndUpdate</code> with guard</td><td>State transitions (pending&rarr;paid)</td><td>None when guard succeeds</td></tr>
<tr><td>Multi-document transactions</td><td>Cross-doc invariants (transfer, two-phase ops)</td><td>2-3x slower than single op; oplog growth</td></tr>
<tr><td>Distributed lock</td><td>Singleton background jobs</td><td>Outage risk if lock TTL too short or too long</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> design schemas so that a single document is the natural unit of consistency &mdash; that&rsquo;s the <strong>cardinal MongoDB rule</strong> and it makes 95% of concurrency questions disappear; for <strong>distributed locks</strong> with TTL and leader election, <strong>Redis Redlock</strong> is fast but operationally tricky; <strong>etcd</strong>, <strong>ZooKeeper</strong>, or <strong>HashiCorp Consul</strong> are stronger for serious leader election; for true serializable workflows (multi-step money movement), use a workflow engine like <strong>Temporal</strong>, <strong>AWS Step Functions</strong>, or <strong>Inngest</strong> &mdash; they handle retries, compensation, and idempotency primitives; <strong>change streams</strong> for downstream side-effects are exactly-once when you combine resume tokens with idempotent consumers.</p>
'''

ANSWERS[19] = r'''
<p><strong>Situation:</strong> a SaaS application serves many tenants &mdash; could be 100 enterprise customers or 100,000 small teams. Need data isolation, fair resource use, and reasonable per-tenant operations (export, delete-all, restore). Read/write paths must always include tenant context.</p>

<p><strong>Approach:</strong> three deployment patterns, picked by tenant count and isolation requirements. Most SaaS uses the <strong>shared-collection + tenant_id</strong> pattern with strong middleware to enforce tenant scoping. For hard isolation (regulated, very large tenants), one DB or one cluster per tenant.</p>

<pre><code>// Pattern A: Shared collection with tenant_id (most common)
db.documents.insertOne({
  _id: ObjectId(),
  tenant_id: ObjectId("tenant_acme"),     // ALWAYS first field for index efficiency
  title: "Q2 plan",
  body: "...",
  created_by: ObjectId("..."),
  created_at: new Date()
});

// Compound indexes ALWAYS have tenant_id leading
db.documents.createIndex({ tenant_id: 1, created_at: -1 });
db.documents.createIndex({ tenant_id: 1, title: 1 });
db.documents.createIndex({ tenant_id: 1, created_by: 1 });

// Middleware that injects tenant_id into every query (Express-ish pseudo)
app.use((req, _res, next) =&gt; {
  req.tenantId = decodeTenantFromJwt(req.headers.authorization);
  next();
});

function withTenant(filter, tenantId) {
  if (filter.tenant_id &amp;&amp; !filter.tenant_id.equals(tenantId)) {
    throw new Error("tenant mismatch");
  }
  return { ...filter, tenant_id: tenantId };
}

// Service code &mdash; can&rsquo;t accidentally leak across tenants
const docs = await db.collection("documents")
  .find(withTenant({ created_by: userId }, req.tenantId))
  .toArray();

// Pattern B: Database-per-tenant (medium count, harder isolation)
const tenantDb = client.db(`tenant_${tenantId}`);
await tenantDb.collection("documents").find(filter).toArray();

// Pattern C: Cluster-per-tenant (regulated industries, huge enterprise tenants)
const clientForTenant = clientPool.get(tenantId);
//   each cluster runs in its own VPC, with its own backup retention, encryption keys

// Tenant onboarding (Pattern A): nothing &mdash; just create the tenant record
db.tenants.insertOne({
  _id: ObjectId(),
  name: "Acme Corp",
  plan: "pro",
  created_at: new Date(),
  features: { sso: true, api_access: true }
});

// Tenant offboarding (Pattern A): bulk delete, or use Atlas Online Archive
db.documents.deleteMany({ tenant_id: ObjectId("tenant_acme") });
db.users.deleteMany({ tenant_id: ObjectId("tenant_acme") });

// Tenant export &mdash; one indexed scan per collection
const allDocs = await db.collection("documents")
  .find({ tenant_id: tid })
  .toArray();

// Sharded multi-tenant: shard key includes tenant_id for locality
sh.shardCollection("app.documents", { tenant_id: 1, _id: 1 });</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Pattern</th><th>Pros</th><th>Cons</th></tr></thead>
<tbody>
<tr><td>Shared collection + tenant_id</td><td>One cluster, low ops; cheap onboarding; cross-tenant analytics easy</td><td>Strong middleware needed; one bad query can leak; noisy-neighbor risk</td></tr>
<tr><td>Database per tenant</td><td>Hard isolation; per-tenant backup &amp; restore; per-tenant indexes</td><td>Connection pool fragmented; metadata explosion past 10k tenants</td></tr>
<tr><td>Cluster per tenant</td><td>Total isolation; regulatory checkbox</td><td>Operationally heavy; high fixed cost; only viable for huge tenants</td></tr>
<tr><td>Hybrid (default shared, big tenants get own cluster)</td><td>Best of both</td><td>Two code paths to maintain</td></tr>
<tr><td>Tag-aware sharding (geo)</td><td>EU data on EU shard for GDPR; data residency</td><td>Manual tag setup; balancing nuances</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> bake tenant scoping into a single <strong>data-access layer</strong> (Mongoose plugin, Prisma extension, Drizzle wrapper) so application code can&rsquo;t bypass it; add <strong>row-level security tests</strong> in CI &mdash; deliberately try to access another tenant&rsquo;s data; for noisy neighbors, use <strong>per-tenant rate limits</strong> (Redis sliding window) and consider <strong>Atlas Federated Sharding</strong> with tenant tags; <strong>Vercel Postgres</strong>, <strong>Neon</strong>, and <strong>PlanetScale</strong> popularized branching-per-tenant in SQL world &mdash; equivalent for Mongo is a per-tenant Atlas project; for SaaS auth/billing, <strong>WorkOS</strong>, <strong>Clerk Organizations</strong>, <strong>Stripe Billing</strong>, and <strong>Frigade</strong> handle the cross-cutting concerns.</p>
'''

ANSWERS[20] = r'''
<p><strong>Situation:</strong> a query is slow &mdash; 5+ seconds when it should be under 100ms. The dev wants a method to identify the bottleneck and fix it without guessing. The query pattern is: filter, sort, paginate over a 50M-document collection.</p>

<p><strong>Approach:</strong> follow the <strong>profile &rarr; explain &rarr; index &rarr; verify</strong> loop. Most slow queries are one of: missing index, wrong index direction, range-before-equality in compound index, or unbounded result set. <strong>Atlas Performance Advisor</strong> automates much of this for hosted clusters.</p>

<pre><code>// 1. Enable the profiler to collect slow queries
db.setProfilingLevel(1, { slowms: 100 });   // log queries &gt; 100ms
//   level 0: off  | 1: slow only  | 2: all queries

// Wait a few minutes, then read the profile collection
db.system.profile.find()
  .sort({ ts: -1 })
  .limit(20)
  .pretty();
// Each entry shows: command, millis, planSummary, docsExamined, keysExamined, nreturned

// 2. Run explain() on the slow query
db.orders.find({ status: "paid", placed_at: { $gte: ISODate("2026-04-01") } })
         .sort({ placed_at: -1 })
         .limit(50)
         .explain("executionStats");

//    Critical fields:
//      winningPlan.stage:        IXSCAN ✓ | COLLSCAN ✗ | SORT (in-memory) ✗
//      executionStats.totalKeysExamined:  should ≈ nReturned for tight queries
//      executionStats.totalDocsExamined:  should ≈ nReturned (covered queries: 0)
//      executionStats.executionTimeMillis
//      executionStats.executionStages.indexName

// 3. Add or fix the index per the ESR rule (Equality, Sort, Range)
db.orders.createIndex({ status: 1, placed_at: -1 });
//      Equality on status, sort on placed_at desc &mdash; matches the query pattern

// 4. Re-run explain() &mdash; verify IXSCAN, low examined, low time
db.orders.find({ status: "paid", placed_at: { $gte: ISODate("2026-04-01") } })
         .sort({ placed_at: -1 })
         .limit(50)
         .explain("executionStats");

// 5. Cover the query &mdash; project only fields in the index
db.orders.createIndex({ status: 1, placed_at: -1, total_cents: 1, user_id: 1 });
db.orders.find(
  { status: "paid", placed_at: { $gte: ISODate("2026-04-01") } },
  { _id: 0, placed_at: 1, total_cents: 1, user_id: 1 }
).sort({ placed_at: -1 }).limit(50);
//    explain() shows totalDocsExamined: 0 &mdash; index alone answers the query

// 6. Find unused indexes &mdash; they slow writes for nothing
db.orders.aggregate([{ $indexStats: {} }])
  .forEach(s =&gt; print(s.name, s.accesses.ops));
db.orders.dropIndex("legacy_idx_unused");

// 7. Aggregation-specific tuning
db.orders.explain("executionStats").aggregate([
  { $match: { status: "paid" } },     // FIRST &mdash; uses index
  { $project: { user_id: 1, total_cents: 1 } },
  { $group: { _id: "$user_id", spend: { $sum: "$total_cents" } } }
]);

// 8. Pagination &mdash; replace skip with cursor for deep pages
db.orders.find({ status: "paid", _id: { $gt: lastSeen } })
         .sort({ _id: 1 })
         .limit(50);
// vs. .skip(50000).limit(50)  &mdash; quadratic cost</code></pre>

<p><strong>Trade-offs / common bottlenecks:</strong></p>
<table>
<thead><tr><th>Symptom</th><th>Likely cause</th><th>Fix</th></tr></thead>
<tbody>
<tr><td>COLLSCAN in explain</td><td>No suitable index</td><td>Build a compound index per ESR</td></tr>
<tr><td>SORT stage above IXSCAN</td><td>Index doesn&rsquo;t match sort direction</td><td>Add or reorder fields in the index</td></tr>
<tr><td><code>docsExamined</code> &gt;&gt; <code>nReturned</code></td><td>Filter checks fields not in index</td><td>Cover the query, or extend the index</td></tr>
<tr><td>Slow at depth (skip/limit)</td><td>Skip is O(N)</td><td>Cursor pagination on indexed key</td></tr>
<tr><td>Aggregation memory error</td><td>$group/$sort exceeds 100MB</td><td>Add <code>{ allowDiskUse: true }</code>; pre-filter with <code>$match</code></td></tr>
<tr><td>Slow under load only</td><td>Working set &gt; RAM</td><td>Add RAM, prune indexes, archive cold data</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> <strong>Atlas Performance Advisor</strong> recommends indexes from real query traffic and shows index-usage stats &mdash; first stop on Atlas; <strong>Atlas Query Profiler</strong> visualizes slow ops over time; <strong>mongotop</strong>, <strong>mongostat</strong>, and <strong>db.serverStatus()</strong> reveal cluster-level pressure (cache evictions, lock contention, network); APM tools like <strong>Datadog</strong>, <strong>New Relic</strong>, <strong>Honeycomb</strong>, or <strong>Sentry Performance</strong> show the per-request flame graph; <strong>Percona PMM</strong> is the open-source equivalent for self-hosted; <strong>maxTimeMS</strong> on every query is a safety net &mdash; runaway queries kill servers.</p>
'''

ANSWERS[21] = r'''
<p><strong>Situation:</strong> users receive notifications &mdash; new follower, comment on a post, mention, payment received. Need to store, retrieve unread, mark-as-read, paginate, and avoid notification fatigue (dedupe similar events). Volume is high during viral moments.</p>

<p><strong>Approach:</strong> a <code>notifications</code> collection keyed by recipient with denormalized actor/object snapshots so reads don&rsquo;t join. <strong>Aggregate similar events</strong> (&ldquo;Alice and 4 others liked your post&rdquo;) via grouping logic on write. Push through <strong>BullMQ</strong>/<strong>Inngest</strong> queues to handle bursts.</p>

<pre><code>db.notifications.insertOne({
  _id: ObjectId(),
  recipient_id: ObjectId("user_alice"),
  type:         "comment",                         // follow | like | comment | mention | system
  actor: {                                         // who did it &mdash; snapshot
    _id: ObjectId(),
    username: "bob",
    display_name: "Bob",
    avatar_url: "..."
  },
  object: {                                        // what they did it on &mdash; snapshot
    type: "post",
    _id: ObjectId(),
    preview: "Designing schemas..."
  },
  read:        false,
  read_at:     null,
  created_at:  new Date()
});

db.notifications.createIndex({ recipient_id: 1, created_at: -1 });
db.notifications.createIndex({ recipient_id: 1, read: 1, created_at: -1 });
db.notifications.createIndex({ created_at: 1 }, { expireAfterSeconds: 90*24*3600 });

// Recent notifications (most common read)
db.notifications.find({ recipient_id: userId })
                .sort({ created_at: -1 })
                .limit(20);

// Unread count for badge
db.notifications.countDocuments({ recipient_id: userId, read: false });

// Mark all as read
db.notifications.updateMany(
  { recipient_id: userId, read: false },
  { $set: { read: true, read_at: new Date() } }
);

// Aggregation: &ldquo;Alice and 4 others liked your post&rdquo;
//   On every new like, look for an existing &ldquo;like on this post&rdquo; notification &lt; 24h old;
//   if found, append the actor; otherwise create a new one
async function notifyLike(postOwnerId, postId, actor) {
  const since = new Date(Date.now() - 24*3600*1000);
  const existing = await db.collection("notifications").findOneAndUpdate(
    {
      recipient_id: postOwnerId,
      type: "like_aggregate",
      "object._id": postId,
      created_at: { $gte: since }
    },
    {
      $addToSet: { "actors": actor },
      $set:      { last_actor: actor, updated_at: new Date(), read: false, read_at: null }
    },
    { returnDocument: "after" }
  );
  if (!existing) {
    await db.collection("notifications").insertOne({
      recipient_id: postOwnerId,
      type:        "like_aggregate",
      object:      { type: "post", _id: postId },
      actors:      [actor],
      last_actor:  actor,
      read:        false,
      created_at:  new Date(),
      updated_at:  new Date()
    });
  }
}

// Async fan-out via queue
import { Queue } from "bullmq";
const notifQueue = new Queue("notifications");
await notifQueue.add("like", { postOwnerId, postId, actor });</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>One doc per notification</td><td>Simple; per-notification read-state</td><td>Embedded array on user &mdash; doc grows, can&rsquo;t paginate efficiently</td></tr>
<tr><td>Denormalized actor/object</td><td>List render in 1 read; survives original deletion</td><td>Live <code>$lookup</code> &mdash; slower; broken when source disappears</td></tr>
<tr><td>Aggregate similar events</td><td>One notification for 50 likes, not 50</td><td>One per event &mdash; spam; overwhelming UX</td></tr>
<tr><td>TTL after 90 days</td><td>Self-managing; old data is rarely viewed</td><td>Manual purge cron &mdash; another moving part</td></tr>
<tr><td>Async via queue</td><td>Bursty viral moments don&rsquo;t back up the API</td><td>Sync writes &mdash; tail latency spikes</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> push notifications need a delivery channel &mdash; <strong>Firebase Cloud Messaging</strong>, <strong>OneSignal</strong>, <strong>Pusher Beams</strong>, <strong>APNs</strong> (iOS), or <strong>Web Push</strong> via service workers; for transactional email, <strong>Postmark</strong>, <strong>Resend</strong>, <strong>Loops</strong>, or <strong>SendGrid</strong>; SMS via <strong>Twilio</strong>; respect user preferences &mdash; per-channel, per-type opt-outs; <strong>Knock</strong>, <strong>Courier</strong>, and <strong>Novu</strong> are turnkey notification platforms that handle templating, fan-out, batching, digesting, and DND windows out of the box; rate-limit per recipient + type to defeat notification storms; track open/click via campaign IDs and feed into product analytics for tuning frequency.</p>
'''

ANSWERS[22] = r'''
<p><strong>Situation:</strong> an online education platform with courses, lessons, quizzes, students, instructors, enrollments, and progress tracking. Need to render course pages quickly, track per-student progress, and aggregate analytics for instructors.</p>

<p><strong>Approach:</strong> separate <code>courses</code>, <code>users</code>, <code>enrollments</code>, and <code>progress</code> collections. Embed lesson outline inside the course doc (bounded). Track progress per (student, lesson) row. Snapshot pricing and instructor metadata on enrollment so historical records survive course updates.</p>

<pre><code>db.users.insertOne({
  _id: ObjectId(),
  email: "alice@example.com",
  display_name: "Alice",
  roles: ["student"],          // student | instructor | admin
  created_at: new Date()
});

db.courses.insertOne({
  _id: ObjectId(),
  slug: "intro-to-mongodb",
  title: "Intro to MongoDB",
  description: "...",
  instructor: {                 // snapshot
    _id: ObjectId("instructor_bob"),
    display_name: "Bob",
    avatar_url: "..."
  },
  price_cents: 4900,
  duration_minutes: 480,
  modules: [                    // embedded outline; bounded
    {
      _id: ObjectId(),
      title: "Getting Started",
      lessons: [
        {
          _id: ObjectId(),
          title: "What is MongoDB?",
          type: "video",        // video | reading | quiz
          duration_minutes: 12,
          video_url: "..."
        },
        { _id: ObjectId(), title: "Quiz 1", type: "quiz", quiz_id: ObjectId("...") }
      ]
    }
  ],
  status: "published",
  rating: { avg: 4.6, count: 230 },
  enrollment_count: 0,
  created_at: new Date()
});
db.courses.createIndex({ slug: 1 }, { unique: true });
db.courses.createIndex({ status: 1, created_at: -1 });
db.courses.createIndex({ "instructor._id": 1 });

db.enrollments.insertOne({
  _id: ObjectId(),
  student_id: ObjectId("alice"),
  course_id:  ObjectId("..."),
  course_snapshot: {           // historical pricing/title
    title: "Intro to MongoDB",
    price_paid_cents: 4900
  },
  enrolled_at:    new Date(),
  status:         "active",     // active | completed | refunded
  completed_at:   null,
  certificate_id: null
});
db.enrollments.createIndex({ student_id: 1, course_id: 1 }, { unique: true });
db.enrollments.createIndex({ student_id: 1, enrolled_at: -1 });
db.enrollments.createIndex({ course_id: 1 });

db.progress.insertOne({
  _id: ObjectId(),
  enrollment_id: ObjectId("..."),
  student_id:    ObjectId("alice"),
  course_id:     ObjectId("..."),
  lesson_id:     ObjectId("..."),
  status:        "completed",   // not_started | in_progress | completed
  watched_seconds: 720,
  completed_at:    new Date(),
  quiz_score:      null
});
db.progress.createIndex({ enrollment_id: 1, lesson_id: 1 }, { unique: true });
db.progress.createIndex({ student_id: 1, completed_at: -1 });

// &ldquo;My courses&rdquo; with progress percentages
db.enrollments.aggregate([
  { $match: { student_id: ObjectId("alice"), status: "active" } },
  { $lookup: {
      from: "progress",
      let: { eid: "$_id" },
      pipeline: [
        { $match: { $expr: { $eq: ["$enrollment_id", "$$eid"] } } },
        { $group: { _id: null, completed: { $sum: { $cond: [{ $eq: ["$status", "completed"] }, 1, 0] } }, total: { $sum: 1 } } }
      ],
      as: "stats"
  }},
  { $unwind: { path: "$stats", preserveNullAndEmptyArrays: true } }
]);

// Mark a lesson complete
db.progress.updateOne(
  { enrollment_id: eid, lesson_id: lid },
  { $set: { status: "completed", completed_at: new Date(), watched_seconds: 720 } },
  { upsert: true }
);</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Embed module/lesson outline</td><td>Course page renders in 1 read; bounded size</td><td>Separate <code>lessons</code> collection &mdash; needed if 1000+ lessons per course</td></tr>
<tr><td>Per-(student, lesson) progress row</td><td>Granular tracking; partial completion is normal</td><td>Embed progress on enrollment &mdash; doc grows with lesson count</td></tr>
<tr><td>Snapshot price &amp; instructor</td><td>Price changes don&rsquo;t rewrite history; refund math intact</td><td>Live join &mdash; refund disputes when prices change</td></tr>
<tr><td>Compound unique on (student, lesson)</td><td>Idempotent &ldquo;mark complete&rdquo; via upsert</td><td>App-level dedupe &mdash; race condition risk</td></tr>
<tr><td>Denormalized rating + enrollment counts</td><td>Course list renders without aggregations</td><td>Live <code>countDocuments</code> &mdash; slow at scale</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for video delivery, never serve from MongoDB &mdash; use <strong>Mux</strong>, <strong>Cloudflare Stream</strong>, <strong>Bunny Stream</strong>, or <strong>AWS MediaConvert</strong> + <strong>S3 + CloudFront</strong>; for assignments and quizzes at scale, integrate <strong>LearnDash</strong>, <strong>TalentLMS</strong>, or build on top of <strong>Open edX</strong>; certificates: generate PDFs with <strong>Puppeteer</strong>/<strong>WeasyPrint</strong>, store in S3, link from enrollment doc; payments via <strong>Stripe Checkout</strong> or <strong>Lemon Squeezy</strong> (handles tax for digital goods globally); progress events feed instructor analytics dashboards via <strong>change streams</strong> &rarr; <strong>BigQuery</strong> or <strong>PostHog</strong>; for live cohort-based courses, layer in <strong>Discord</strong>/<strong>Circle</strong>/<strong>Slack</strong> for community.</p>
'''

ANSWERS[23] = r'''
<p><strong>Situation:</strong> a content site has 100K+ articles. Users search by free text &mdash; titles, body, tags &mdash; with typo tolerance, autocomplete, faceted filters (category, year, author), and relevance ranking. Built-in <code>$text</code> covers basic cases; serious search needs more.</p>

<p><strong>Approach:</strong> for prototypes, use the built-in <strong>text index</strong> with <code>$text</code>. For production-grade search (typo tolerance, autocomplete, synonyms, multi-language), use <strong>MongoDB Atlas Search</strong> (Lucene-powered) or mirror to a dedicated engine like <strong>Elasticsearch</strong>, <strong>Meilisearch</strong>, or <strong>Typesense</strong>.</p>

<pre><code>// Option 1: Built-in text index (fastest to set up; limited features)
db.articles.createIndex(
  { title: "text", body: "text", tags: "text" },
  { weights: { title: 10, tags: 5, body: 1 }, name: "articles_text" }
);

db.articles.find(
  { $text: { $search: "mongodb schema design" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });

// Phrases, exclusions, multi-term
db.articles.find({ $text: { $search: "\"schema design\" -relational" } });

// Limitations of $text:
//   - one text index per collection
//   - no fuzzy matching (typo tolerance)
//   - no autocomplete
//   - one language per index (or per-doc via `language` field)

// Option 2: Atlas Search (recommended for production on Atlas)
//   Define an Atlas Search index in the Atlas UI or via API:
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "title":     { "type": "string", "analyzer": "lucene.english" },
      "body":      { "type": "string", "analyzer": "lucene.english" },
      "tags":      { "type": "string" },
      "category":  { "type": "stringFacet" },
      "published_year": { "type": "numberFacet" },
      "author.name": { "type": "string" }
    }
  }
}

// Query via $search aggregation
db.articles.aggregate([
  { $search: {
      index: "articles",
      compound: {
        must: [
          { text: { query: "mongodb schema",
                    path: ["title", "body"],
                    fuzzy: { maxEdits: 1, prefixLength: 2 } } }
        ],
        filter: [
          { equals: { path: "category", value: "tutorial" } }
        ]
      },
      highlight: { path: ["title", "body"] }
  }},
  { $facet: {
      results: [
        { $project: { title: 1, score: { $meta: "searchScore" }, highlights: { $meta: "searchHighlights" } } },
        { $limit: 20 }
      ],
      facets: [
        { $searchMeta: {
            index: "articles",
            facet: {
              operator: { compound: { must: [...] } },
              facets: {
                category_facet:  { type: "string", path: "category" },
                year_facet:      { type: "number", path: "published_year", boundaries: [2020,2021,2022,2023,2024,2025,2026] }
              }
        }}}
      ]
  }}
]);

// Autocomplete via Atlas Search edgeGram analyzer
db.articles.aggregate([
  { $search: {
      index: "articles_autocomplete",
      autocomplete: { query: userInput, path: "title", tokenOrder: "sequential" }
  }},
  { $limit: 10 }
]);

// Option 3: Mirror to Elasticsearch / Meilisearch via change streams
const stream = db.collection("articles").watch(
  [{ $match: { operationType: { $in: ["insert", "update", "delete"] } } }],
  { fullDocument: "updateLookup" }
);
stream.on("change", change =&gt; {
  if (change.operationType === "delete") {
    elastic.delete({ index: "articles", id: change.documentKey._id });
  } else {
    elastic.index({ index: "articles", id: change.fullDocument._id, body: change.fullDocument });
  }
});</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Engine</th><th>Pros</th><th>Cons</th></tr></thead>
<tbody>
<tr><td>$text + text index</td><td>No extra infra; in the same cluster</td><td>No fuzzy/autocomplete; one per collection; weak ranking</td></tr>
<tr><td>Atlas Search (Lucene)</td><td>In Atlas; fuzzy/autocomplete/synonyms/highlights/facets; BM25 scoring</td><td>Atlas-only; per-search-index pricing</td></tr>
<tr><td>Elasticsearch / OpenSearch</td><td>Most powerful; aggregations + ML; on-prem</td><td>Operational complexity; sync lag; resource-heavy</td></tr>
<tr><td>Meilisearch / Typesense</td><td>Easy to run; fast; great for catalogs</td><td>Less feature-rich than ES; weaker analytics</td></tr>
<tr><td>Algolia</td><td>Hosted, blazing fast, polished UX widgets</td><td>Cost scales with traffic</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> mirror via <strong>change streams</strong> to keep the search index near-real-time consistent (typically &lt;1s lag); for typo tolerance + autocomplete, <strong>Atlas Search</strong>&rsquo;s <code>fuzzy</code> + <code>autocomplete</code> operators are the easiest path; for vector search (semantic, &ldquo;articles like this one&rdquo;), use <strong>Atlas Vector Search</strong> with embeddings from <strong>OpenAI</strong>, <strong>Cohere</strong>, or <strong>Voyage</strong>; combine with text relevance for hybrid search; cache hot query+facet combinations in <strong>Redis</strong>; track no-result queries to identify content gaps and synonym tuning opportunities.</p>
'''

ANSWERS[24] = r'''
<p><strong>Situation:</strong> a database with millions of historical records grows daily. Most queries hit recent data; old records are kept for compliance and rare lookups. Storage and backup costs balloon. Need an archival strategy without breaking reads on archived data.</p>

<p><strong>Approach:</strong> tier the data &mdash; <strong>hot</strong> in MongoDB, <strong>warm</strong> in <strong>Atlas Online Archive</strong> (queryable, cheaper), <strong>cold</strong> in <strong>S3</strong>/<strong>Glacier</strong> (compliance-only). Use <strong>TTL indexes</strong> for ephemeral data, scheduled <strong>$out</strong>/<strong>$merge</strong> for warm migration, and <strong>Federated Database</strong> queries to span tiers transparently.</p>

<pre><code>// Tier 1: hot &mdash; recent 90 days, fully indexed in main cluster
//   no special config, just normal collection

// Tier 2: warm &mdash; Atlas Online Archive (Atlas-only feature)
//   Configure in Atlas UI: archive documents older than 90 days
//   Documents transparently move to cheaper object storage
//   Queries via Federated Database can span hot + warm
db.orders.aggregate([
  { $match: { placed_at: { $gte: ISODate("2024-01-01") } } }   // spans hot + archive
]);

// Tier 3: cold &mdash; S3/Glacier
//   Older than 7 years, only restored on legal request

// Self-hosted equivalent: scheduled archival to a cold collection or cluster
// 1. Stream eligible documents to an archive cluster
db.orders.aggregate([
  { $match: { placed_at: { $lt: ninetyDaysAgo } } },
  { $merge: { into: { db: "archive", coll: "orders" } } }
]);

// 2. Then delete from hot cluster
db.orders.deleteMany({ placed_at: { $lt: ninetyDaysAgo } });

// TTL for ephemeral data (sessions, OTPs, audit logs after retention)
db.sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });
db.audit_log.createIndex({ created_at: 1 }, { expireAfterSeconds: 7*365*24*3600 });

// Time-series collections accept expireAfterSeconds at creation
db.createCollection("metrics", {
  timeseries: { timeField: "ts", metaField: "device" },
  expireAfterSeconds: 90 * 24 * 3600
});

// Selective archival via background job (BullMQ)
import { Queue, Worker } from "bullmq";
const archiveQueue = new Queue("archive");
new Worker("archive", async () =&gt; {
  const cutoff = new Date(Date.now() - 90*24*3600*1000);
  // Stream to S3 as compressed BSON
  const cursor = db.collection("orders").find({ placed_at: { $lt: cutoff } }).batchSize(1000);
  const stream = bsonEncoderStream();
  cursor.stream().pipe(zstdCompress()).pipe(stream).pipe(s3Upload("archive/orders.bson.zst"));
  await stream.finished;
  // Then delete from hot
  await db.collection("orders").deleteMany({ placed_at: { $lt: cutoff } });
});

// Querying cold data: rehydrate on demand
async function fetchCold(id) {
  const fileKey = "archive/orders/2023.bson.zst";
  // Stream from S3, decompress, find by id
}

// Atlas Federated Database: query S3 + MongoDB in one statement
//   set up a federated database in Atlas; configure S3 as a virtual collection
db.federated.orders.find({ user_id: uid });   // spans live + S3 transparently</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Tier</th><th>Cost</th><th>Latency</th><th>Use</th></tr></thead>
<tbody>
<tr><td>Hot (live MongoDB)</td><td>$$$ (RAM-bound)</td><td>ms</td><td>Last 90 days; daily reads</td></tr>
<tr><td>Atlas Online Archive</td><td>$ (S3-backed, queryable)</td><td>seconds</td><td>1-7 years; rare reads</td></tr>
<tr><td>S3 Standard</td><td>$ per GB-month</td><td>seconds</td><td>Backups, raw events for warehouse</td></tr>
<tr><td>S3 Glacier / Glacier Deep Archive</td><td>$$ per restore, &cent; per GB</td><td>hours</td><td>Compliance retention 7+ years</td></tr>
<tr><td>TTL indexes</td><td>Free</td><td>n/a (auto-delete)</td><td>Sessions, ephemeral, anything purely transient</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> <strong>Atlas Online Archive</strong> is the simplest path on Atlas &mdash; tag the field and rule, MongoDB does the rest; for self-hosted, write the archival job once, schedule via <strong>BullMQ</strong>/<strong>Inngest</strong>/<strong>Temporal</strong>, monitor via <strong>Datadog</strong>; verify integrity periodically (random-sample row hashes); use <strong>S3 Object Lock</strong> in compliance mode for tamper-proof archives (ransomware defense + regulatory); for warehouse-style historical analytics, ship raw events to <strong>BigQuery</strong>, <strong>Snowflake</strong>, or <strong>Databricks</strong> via <strong>Airbyte</strong>/<strong>Fivetran</strong>/<strong>Estuary</strong>; document the retention matrix per data type with legal &mdash; GDPR and HIPAA dictate floors and ceilings.</p>
'''

ANSWERS[25] = r'''
<p><strong>Situation:</strong> a hotel reservation system with hotels, rooms, and bookings. Users search availability by date range and city, view hotel details with photos and reviews, and book rooms. Concurrency matters &mdash; two users mustn&rsquo;t book the same room for overlapping dates.</p>

<p><strong>Approach:</strong> separate <code>hotels</code>, <code>rooms</code>, and <code>bookings</code>. Embed hotel-level data (photos, amenities) for read efficiency; rooms reference hotel; bookings hold the date range. Enforce no-overlap via a transactional check on insert, since MongoDB has no native range-overlap exclusion constraint.</p>

<pre><code>db.hotels.insertOne({
  _id: ObjectId(),
  slug: "grand-hotel-paris",
  name: "Grand Hotel Paris",
  address: { line1: "1 Rue de...", city: "Paris", country: "FR", postal: "75001" },
  location: { type: "Point", coordinates: [2.3522, 48.8566] },     // GeoJSON
  amenities: ["wifi", "pool", "parking", "breakfast"],
  photos: ["https://cdn.../1.jpg", "https://cdn.../2.jpg"],
  rating: { avg: 4.5, count: 1230 },
  star_rating: 4,
  active: true
});
db.hotels.createIndex({ location: "2dsphere" });
db.hotels.createIndex({ "address.city": 1, active: 1 });
db.hotels.createIndex({ slug: 1 }, { unique: true });

db.rooms.insertOne({
  _id: ObjectId(),
  hotel_id: ObjectId("..."),
  room_number: "401",
  type: "deluxe_double",      // standard | deluxe_double | suite
  capacity: 2,
  price_per_night_cents: 19900,
  active: true
});
db.rooms.createIndex({ hotel_id: 1, active: 1 });

db.bookings.insertOne({
  _id: ObjectId(),
  user_id:  ObjectId("..."),
  hotel_id: ObjectId("..."),
  room_id:  ObjectId("..."),
  check_in:  ISODate("2026-06-01"),
  check_out: ISODate("2026-06-05"),
  guests:    2,
  status:    "confirmed",      // pending | confirmed | cancelled | refunded
  total_cents: 79600,
  hotel_snapshot: { name: "Grand Hotel Paris", city: "Paris" },
  room_snapshot:  { type: "deluxe_double", price_per_night_cents: 19900 },
  created_at: new Date()
});
db.bookings.createIndex({ room_id: 1, check_in: 1 });
db.bookings.createIndex({ user_id: 1, check_in: -1 });
db.bookings.createIndex({ hotel_id: 1, check_in: 1 });

// Search: hotels in city with rooms available on dates
const requestedRange = { check_in: ISODate("2026-06-01"), check_out: ISODate("2026-06-05") };

// 1. Find rooms NOT booked in the requested range
db.bookings.aggregate([
  { $match: {
      status: { $in: ["pending", "confirmed"] },
      // overlap: existing.check_in &lt; requested.check_out AND existing.check_out &gt; requested.check_in
      check_in:  { $lt: requestedRange.check_out },
      check_out: { $gt: requestedRange.check_in }
  }},
  { $group: { _id: "$room_id" } }   // booked-room ids
]);

// 2. Available rooms = (rooms in hotels in city) MINUS (booked rooms)
//    Achievable via $lookup or two-step query

// Booking creation &mdash; transactional double-check to prevent races
async function bookRoom(userId, roomId, checkIn, checkOut) {
  const session = client.startSession();
  let booking;
  await session.withTransaction(async () =&gt; {
    // Re-check no overlap inside the transaction
    const conflict = await db.collection("bookings").findOne({
      room_id: roomId,
      status:  { $in: ["pending", "confirmed"] },
      check_in:  { $lt: checkOut },
      check_out: { $gt: checkIn }
    }, { session });
    if (conflict) throw new Error("Room no longer available");

    booking = {
      _id: new ObjectId(), user_id: userId, room_id: roomId,
      check_in: checkIn, check_out: checkOut, status: "confirmed",
      created_at: new Date()
    };
    await db.collection("bookings").insertOne(booking, { session });
  });
  return booking;
}

// Geo search: hotels within 5km of a point
db.hotels.find({
  location: {
    $nearSphere: {
      $geometry: { type: "Point", coordinates: [2.3522, 48.8566] },
      $maxDistance: 5000
    }
  },
  active: true
});</code></pre>

<p><strong>Trade-offs:</strong></p>
<table>
<thead><tr><th>Decision</th><th>Why</th><th>Alternative</th></tr></thead>
<tbody>
<tr><td>Range-overlap check in transaction</td><td>Only safe way without exclusion constraints</td><td>App-only check &mdash; race condition between read and insert</td></tr>
<tr><td>Snapshot hotel/room on booking</td><td>Pricing/name changes don&rsquo;t corrupt history</td><td>Live join &mdash; broken when room is renamed/deleted</td></tr>
<tr><td>2dsphere index on location</td><td>Native &ldquo;within X km&rdquo; queries</td><td>App-side haversine &mdash; reinventing the wheel</td></tr>
<tr><td>Compound index (room_id, check_in)</td><td>Overlap query uses index for narrow scans</td><td>Scan-then-filter &mdash; slow with many bookings</td></tr>
<tr><td>Status field</td><td>Cancellation invalidates booking without delete</td><td>Delete &mdash; loses audit trail; refund races</td></tr>
</tbody>
</table>

<p><strong>Production polish:</strong> for serious hotel inventory, integrate a global distribution system (<strong>Sabre</strong>, <strong>Amadeus</strong>, <strong>Travelport</strong>) or channel manager (<strong>SiteMinder</strong>, <strong>Cloudbeds</strong>) &mdash; never source pricing/availability from your own DB alone; payments via <strong>Stripe</strong> with manual capture (authorize at booking, capture at check-in); fraud detection via <strong>Stripe Radar</strong> or <strong>Sift</strong>; geo search beyond simple radius needs <strong>PostGIS</strong> or <strong>Tile38</strong>; reviews moderated via <strong>Perspective API</strong>; transactional emails (confirmations, reminders) via <strong>Postmark</strong>/<strong>Resend</strong>; analytics on conversion funnels via <strong>Amplitude</strong>; consider <strong>idempotency keys</strong> on booking POST to defeat double-clicks and retries.</p>
'''
