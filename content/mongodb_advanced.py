"""MongoDB Advanced — 100 detailed answers."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>Replica sets</strong> and <strong>sharding</strong> solve different scaling problems and are usually combined in production: every shard <em>is</em> a replica set.</p>

<table>
  <tr><th>Aspect</th><th>Replica set</th><th>Sharding</th></tr>
  <tr><td>Goal</td><td>High availability + read scaling</td><td>Horizontal write/storage scaling</td></tr>
  <tr><td>Topology</td><td>3+ nodes holding identical data</td><td>N shards, each holding a slice of the data</td></tr>
  <tr><td>Routing</td><td>Driver chooses primary or secondary</td><td>Clients connect through <code>mongos</code> routers</td></tr>
  <tr><td>Failover</td><td>Raft-like election promotes a new primary</td><td>Per-shard failover via the underlying replica set</td></tr>
  <tr><td>Operational cost</td><td>Low; default in Atlas</td><td>High &mdash; shard key choice is permanent and load-shaping matters</td></tr>
  <tr><td>When you need it</td><td>Always &mdash; production should never run standalone</td><td>When working set or write rate exceeds one machine</td></tr>
</table>

<p>Replica sets give you durability and zero-downtime maintenance through redundant copies and automatic primary elections. Sharding adds capacity by partitioning a collection across multiple replica sets keyed by the <em>shard key</em>; <code>mongos</code> consults the config-server metadata to route reads and writes to the right shard.</p>

<p>The progression is replica set first, shard later only when you outgrow a single machine&rsquo;s RAM or write capacity. Sharding too early adds operational complexity for no benefit &mdash; <strong>MongoDB Atlas</strong>&rsquo;s &ldquo;Cluster Tier&rdquo; UI even hides sharding until your data hits a threshold for exactly this reason.</p>
'''

ANSWERS[2] = r'''
<p>A sharded cluster has three components: <strong>config servers</strong> (a 3-node replica set holding cluster metadata), <strong>shards</strong> (each itself a replica set storing a subset of data), and <strong>mongos routers</strong> (stateless query routers that clients connect to). Set them up in that order &mdash; config servers first, then shards, then routers.</p>

<pre><code>// 1. Start the config replica set
mongod --configsvr --replSet cfg --dbpath /data/cfg --port 27019
// then rs.initiate({ _id: "cfg", configsvr: true, members: [...] })

// 2. Each shard is its own replica set
mongod --shardsvr --replSet shardA --dbpath /data/sa --port 27018
// rs.initiate inside each

// 3. Start mongos routers
mongos --configdb cfg/host1:27019,host2:27019,host3:27019 --port 27017

// 4. Add shards and shard a collection
sh.addShard("shardA/host:27018")
sh.enableSharding("shopdb")
sh.shardCollection("shopdb.orders", { customer_id: "hashed" })</code></pre>

<p><strong>Day-2 operations</strong>: monitor the <strong>balancer</strong> (auto-migrates chunks to keep shards even), keep an eye on <strong>jumbo chunks</strong> (chunks too large to migrate &mdash; usually a sign of a poor shard key), and use <strong>zones</strong> for geo-sharding or tiered storage. <code>sh.status()</code> shows chunk distribution; <code>db.currentOp()</code> shows in-flight migrations.</p>

<p>For nearly all teams, <strong>MongoDB Atlas</strong> is the right answer &mdash; sharded clusters provision in minutes, the balancer is fully managed, and <strong>online resharding</strong> (4.4+) lets you change the shard key without rebuilding from scratch. Self-managed sharding is operationally heavy and reserved for very specific compliance or cost scenarios.</p>
'''

ANSWERS[3] = r'''
<p>The <strong>shard key</strong> is the field (or compound of fields) MongoDB uses to decide which shard each document belongs to. It controls both write distribution and query routing &mdash; pick poorly and you end up with hot shards, scatter-gather queries, or unscalable inserts.</p>

<p><strong>The four properties of a good shard key</strong>:</p>
<ul>
  <li><strong>High cardinality</strong> &mdash; many possible values so chunks can divide evenly. <code>country</code> is bad (~200 values); <code>user_id</code> is great.</li>
  <li><strong>Low frequency</strong> &mdash; no single value dominates. A shard key where 90% of writes go to one user is effectively single-shard.</li>
  <li><strong>Non-monotonic</strong> &mdash; sequential keys (timestamps, auto-increment) cause every new write to hit the &ldquo;last&rdquo; chunk on one shard. Use <code>"hashed"</code> sharding to randomize, or compound with a high-cardinality field.</li>
  <li><strong>Matches your queries</strong> &mdash; queries that include the shard key are <em>targeted</em> (one shard); queries without it are <em>scatter-gather</em> (every shard). For a multi-tenant app, <code>{ tenant_id: 1, _id: 1 }</code> is often ideal.</li>
</ul>

<p><strong>Common patterns</strong>: hashed <code>user_id</code> for event/IoT streams (writes spread evenly), compound <code>{ tenant_id: 1, created_at: 1 }</code> for SaaS (per-tenant locality), or zone-sharded <code>{ region: 1, _id: 1 }</code> for geo-residency compliance.</p>

<p>Online <strong>resharding</strong> (4.4+, fully online in 5.0+) means you&rsquo;re no longer locked into the original choice, but it&rsquo;s a multi-hour operation on large collections. Atlas&rsquo;s shard key advisor uses workload data to recommend candidates &mdash; valuable signal even if you don&rsquo;t accept its suggestion.</p>
'''

ANSWERS[4] = r'''
<p>Pre-4.4, the shard key was immutable &mdash; changing it meant exporting, dropping the collection, and reimporting under a new key. Since 4.4 MongoDB supports <strong>refineCollectionShardKey</strong> (add fields to the existing key) and since 5.0 <strong>resharding</strong> (replace the key entirely while the database is online).</p>

<pre><code>// Add a suffix field to the existing shard key (4.4+)
db.adminCommand({
  refineCollectionShardKey: "shopdb.orders",
  key: { customer_id: 1, _id: 1 }   // was just { customer_id: 1 }
})

// Full resharding to a different key (5.0+)
db.adminCommand({
  reshardCollection: "shopdb.orders",
  key: { tenant_id: 1, created_at: 1 }
})

// Monitor progress
db.currentOp({ "command.reshardCollection": { $exists: true } })</code></pre>

<p><strong>How resharding works internally</strong>: MongoDB writes a parallel collection with the new shard key, replays the oplog continuously to keep it caught up with live writes, and finally swaps over atomically. The old collection is dropped at the end. CPU and disk pressure are real &mdash; expect noticeable slowdown on large collections.</p>

<p><strong>Operational checklist</strong>:</p>
<ul>
  <li>Reshard during low-traffic windows; set up alerts for replica lag during the operation.</li>
  <li>Have <strong>2x free disk space</strong> &mdash; the new collection coexists with the old until completion.</li>
  <li>Test on a staging cluster of comparable size first.</li>
  <li>For Atlas, the resharding wizard handles all of this with progress UI.</li>
</ul>

<p>Most teams end up resharding eventually because access patterns evolve. Modern MongoDB makes this a manageable operation rather than the data-migration nightmare it used to be.</p>
'''

ANSWERS[5] = r'''
<p><strong>Write concern</strong> tells MongoDB how durable a write must be before acknowledging the client. It&rsquo;s the knob between <em>fire-and-forget speed</em> and <em>guaranteed-on-replica safety</em>.</p>

<table>
  <tr><th>Level</th><th>Meaning</th><th>Use case</th></tr>
  <tr><td><code>w: 0</code></td><td>No acknowledgement</td><td>Fire-and-forget metrics ingestion (rare)</td></tr>
  <tr><td><code>w: 1</code></td><td>Primary acknowledged</td><td>Default; OK for non-critical data</td></tr>
  <tr><td><code>w: "majority"</code></td><td>Majority of replica members</td><td>Production default for important writes</td></tr>
  <tr><td><code>w: 2</code> / <code>3</code></td><td>Specific count</td><td>Specialized tier requirements</td></tr>
  <tr><td><code>j: true</code></td><td>+ Persisted to journal on disk</td><td>Banking, audit logs &mdash; survives crash</td></tr>
  <tr><td><code>wtimeout: ms</code></td><td>Cap how long to wait</td><td>Avoids hangs during partitions</td></tr>
</table>

<pre><code>// Production-grade write concern
db.orders.insertOne(
  { customer_id: 42, total: 100 },
  { writeConcern: { w: "majority", j: true, wtimeout: 5000 } }
)</code></pre>

<p><strong>Why majority matters</strong>: with <code>w: 1</code>, if the primary crashes after acknowledging but before replicating, the write is lost in the failover. <code>w: "majority"</code> ensures the write has reached enough nodes that no possible failover can lose it &mdash; the foundation of MongoDB&rsquo;s durability story.</p>

<p>Set the cluster default once via <code>setDefaultRWConcern</code> rather than per-operation; modern Atlas clusters default to <code>w: "majority"</code> already. Pair with <strong>read concern <code>"majority"</code></strong> for true read-your-writes consistency in distributed apps.</p>
'''

ANSWERS[6] = r'''
<p><strong>Read preference</strong> tells the driver which replica-set member to send reads to. The default <code>primary</code> serves the most consistent data; secondary modes scale read throughput at the cost of potentially stale data.</p>

<table>
  <tr><th>Mode</th><th>Behavior</th><th>Use case</th></tr>
  <tr><td><code>primary</code> (default)</td><td>Reads only from primary</td><td>Strict read-your-writes; default</td></tr>
  <tr><td><code>primaryPreferred</code></td><td>Primary if available, else secondary</td><td>Resilient reads during failover</td></tr>
  <tr><td><code>secondary</code></td><td>Secondaries only</td><td>Reporting, analytics &mdash; offload primary</td></tr>
  <tr><td><code>secondaryPreferred</code></td><td>Secondary if available, else primary</td><td>Read scaling with fallback</td></tr>
  <tr><td><code>nearest</code></td><td>Lowest network latency member</td><td>Geo-distributed apps</td></tr>
</table>

<pre><code>// Connection-string form
mongodb://host1,host2,host3/?replicaSet=rs0&amp;readPreference=secondaryPreferred

// Per-query (Node.js driver)
await db.collection("reports")
        .find({ year: 2026 })
        .withReadPreference("secondary")
        .toArray()

// Tag sets &mdash; route to specific members
const reports = client.db("shop", { readPreference: { mode: "secondary", tags: [{ region: "analytics" }] } })</code></pre>

<p><strong>Trade-offs</strong>: secondary reads can be <em>slightly stale</em> &mdash; replication lag is normally milliseconds but can spike during heavy writes or schema changes. For consistent reads, pair with <strong>causal consistency</strong> sessions or use <code>readConcern: "majority"</code>.</p>

<p>Common patterns: keep transactional reads on <code>primary</code>, route reporting and BI workloads to a tagged <strong>analytics node</strong> (a hidden replica member with priority 0), and use <code>nearest</code> only for global apps where latency dominates over freshness.</p>
'''

ANSWERS[7] = r'''
<p>The <strong>CAP theorem</strong> states that a distributed system can only guarantee two of three properties simultaneously during a network partition: <strong>Consistency</strong> (every read sees the latest write), <strong>Availability</strong> (every request gets a response), <strong>Partition tolerance</strong> (system continues despite network failures).</p>

<p>Since partitions are inevitable in real networks, the practical choice is between <strong>CP</strong> (consistent but may refuse requests during partition) and <strong>AP</strong> (always responsive but may serve stale data).</p>

<p><strong>MongoDB is fundamentally CP</strong>:</p>
<ul>
  <li>Writes go to the primary; if the primary is partitioned away, no writes happen on that side &mdash; availability sacrificed for consistency.</li>
  <li>Failover requires majority quorum; a minority partition cannot elect a new primary, ensuring no split-brain.</li>
  <li>With <code>w: "majority"</code> + <code>readConcern: "majority"</code>, MongoDB provides <em>linearizable</em> guarantees on a single document.</li>
</ul>

<p><strong>Tunable knobs</strong> let you shift along the CAP spectrum:</p>
<table>
  <tr><th>Configuration</th><th>Effect</th></tr>
  <tr><td><code>w: 1, readPreference: secondaryPreferred</code></td><td>More AP-leaning &mdash; faster reads, possibly stale</td></tr>
  <tr><td><code>w: majority, readConcern: majority</code></td><td>Strong CP &mdash; sacrifices write availability during partitions</td></tr>
  <tr><td><code>w: majority, readConcern: linearizable</code></td><td>Strongest guarantee; slower reads</td></tr>
</table>

<p>Modern thinking has moved toward <strong>PACELC</strong> &mdash; even without partitions, you trade <strong>L</strong>atency for <strong>C</strong>onsistency. MongoDB exposes both axes: write concern controls the C-vs-A tradeoff during partition, read concern + read preference control the C-vs-L tradeoff in steady state.</p>
'''

ANSWERS[8] = r'''
<p>MongoDB&rsquo;s flexible schema makes zero-downtime schema changes much easier than in SQL &mdash; documents in the same collection can have different shapes, so you can roll out new fields without a migration window. The pattern is <strong>expand &rarr; migrate &rarr; contract</strong>.</p>

<p><strong>Expand</strong>: deploy code that <em>writes</em> the new shape but still <em>reads</em> the old. Both shapes coexist:</p>
<pre><code>// Old: { name: "Alice Smith" }
// New: { first_name: "Alice", last_name: "Smith", name: "Alice Smith" }
// Reads handle either; writes always produce both.</code></pre>

<p><strong>Migrate</strong>: backfill existing documents in batches.</p>
<pre><code>// Pipeline-form update splits the old name field
db.users.updateMany(
  { first_name: { $exists: false } },
  [
    { $set: {
        first_name: { $arrayElemAt: [{ $split: ["$name", " "] }, 0] },
        last_name:  { $arrayElemAt: [{ $split: ["$name", " "] }, 1] }
    }}
  ]
)
// Run in chunks of 10K to avoid replica lag</code></pre>

<p><strong>Contract</strong>: once 100% of documents have the new shape, deploy code that reads only the new fields, then <code>$unset</code> the old field.</p>

<p><strong>Key tools</strong>:</p>
<ul>
  <li><strong>Schema versioning</strong> &mdash; add a <code>schema_version</code> field; readers branch on it. Lazy migration as users access documents.</li>
  <li><strong>JSON Schema validation</strong> &mdash; tighten gradually with <code>validationAction: "warn"</code> first, then <code>"error"</code> after backfill.</li>
  <li><strong>Atlas Trigger / change streams</strong> &mdash; can transform documents on-write during the transition.</li>
  <li><strong>Online indexing</strong> &mdash; add new indexes with <code>{ background: true }</code> (legacy) or rolling builds on replica sets.</li>
</ul>

<p>Tools like <strong>Mongoose migrations</strong>, <strong>migrate-mongo</strong>, or <strong>Atlas App Services</strong> orchestrate this in CI/CD pipelines.</p>
'''

ANSWERS[9] = r'''
<p>The <strong><code>$graphLookup</code></strong> stage performs <strong>recursive graph traversal</strong> within an aggregation pipeline. Given a starting document and a connection rule, it follows references to assemble a tree or graph &mdash; perfect for org charts, comment threads, category hierarchies, or social graphs.</p>

<pre><code>// Employees: { _id, name, manager_id }
// Find Alice and everyone in her reporting chain
db.employees.aggregate([
  { $match: { name: "Alice" } },
  { $graphLookup: {
      from:             "employees",
      startWith:        "$_id",
      connectFromField: "_id",
      connectToField:   "manager_id",
      as:               "reports",
      maxDepth:         5,
      depthField:       "level"
  }}
])
// Result: Alice + every direct/indirect report up to 5 levels deep
// Each report has a "level" field (0 = direct, 1 = grandchild, etc.)</code></pre>

<p><strong>Key parameters</strong>:</p>
<table>
  <tr><th>Parameter</th><th>Purpose</th></tr>
  <tr><td><code>startWith</code></td><td>Initial value(s) to start traversal from</td></tr>
  <tr><td><code>connectFromField</code></td><td>Field in the current doc to follow</td></tr>
  <tr><td><code>connectToField</code></td><td>Field on the target docs to match</td></tr>
  <tr><td><code>maxDepth</code></td><td>Recursion limit (0 means &ldquo;direct only&rdquo;)</td></tr>
  <tr><td><code>depthField</code></td><td>Optional &mdash; tracks distance from start</td></tr>
  <tr><td><code>restrictSearchWithMatch</code></td><td>Filter on the joined docs (e.g., active employees only)</td></tr>
</table>

<p><strong>Performance caveats</strong>: graph traversal can be expensive &mdash; index <code>connectToField</code>, set <code>maxDepth</code> conservatively, and avoid graphs with very high fanout. For huge social graphs (Twitter-scale), a purpose-built graph database like <strong>Neo4j</strong>, <strong>Memgraph</strong>, or <strong>Amazon Neptune</strong> outperforms <code>$graphLookup</code>; use this when graph queries are occasional and the data already lives in MongoDB.</p>
'''

ANSWERS[10] = r'''
<p><strong>Role-based access control (RBAC)</strong> in MongoDB centers on <strong>roles</strong> &mdash; named sets of privileges &mdash; granted to <strong>users</strong>. MongoDB ships with built-in roles for the common cases and supports custom roles for fine-grained needs.</p>

<table>
  <tr><th>Built-in role</th><th>Privileges</th></tr>
  <tr><td><code>read</code></td><td>Read on a database</td></tr>
  <tr><td><code>readWrite</code></td><td>Read + write on a database</td></tr>
  <tr><td><code>dbAdmin</code></td><td>Indexes, schema, statistics</td></tr>
  <tr><td><code>userAdmin</code></td><td>Manage users in a database</td></tr>
  <tr><td><code>clusterAdmin</code></td><td>Cluster-wide operations</td></tr>
  <tr><td><code>root</code></td><td>Superuser (admin DB only)</td></tr>
</table>

<pre><code>// Start mongod with --auth, then create users
use admin
db.createUser({
  user: "appUser",
  pwd:  passwordPrompt(),
  roles: [{ role: "readWrite", db: "shopdb" }]
})

// Custom role for a specific collection
db.createRole({
  role: "ordersReadOnly",
  privileges: [{
    resource: { db: "shopdb", collection: "orders" },
    actions:  ["find"]
  }],
  roles: []
})

// Grant or revoke
db.grantRolesToUser("appUser", [{ role: "ordersReadOnly", db: "shopdb" }])
db.revokeRolesFromUser("appUser", [{ role: "readWrite", db: "shopdb" }])</code></pre>

<p><strong>Production patterns</strong>:</p>
<ul>
  <li><strong>Least privilege</strong> &mdash; app users get <code>readWrite</code> on a single database, never <code>root</code>.</li>
  <li><strong>Separate roles</strong> for migrations (<code>dbAdmin</code>), runtime (<code>readWrite</code>), and analytics (<code>read</code> on secondaries).</li>
  <li><strong>Authentication mechanisms</strong>: SCRAM-SHA-256 default; LDAP/Kerberos in Enterprise; x.509 client certs for service-to-service.</li>
  <li><strong>Atlas</strong>: Database Users tab, IAM-style policies, and integration with cloud-provider SSO. Credentials rotated via Atlas API + <strong>HashiCorp Vault</strong> or <strong>AWS Secrets Manager</strong>.</li>
  <li><strong>Field-level access</strong>: combine RBAC with <strong>Client-Side Field-Level Encryption</strong> for PII columns &mdash; the user can read the document but can&rsquo;t decrypt the sensitive field without an extra key.</li>
</ul>
'''

ANSWERS[11] = r'''
<p><strong>Change streams</strong> are MongoDB&rsquo;s <strong>built-in change-data-capture mechanism</strong> &mdash; a real-time, ordered, resumable feed of every <code>insert</code>, <code>update</code>, <code>delete</code>, and <code>replace</code> on a collection, database, or entire cluster. They tap into the same oplog that powers replication and expose it to applications via a streaming cursor.</p>

<pre><code>// Watch a collection for any change
const stream = db.collection("orders").watch([
  { $match: { operationType: { $in: ["insert", "update"] } } }
])

stream.on("change", change =&gt; {
  // change.fullDocument has the new doc (insert / fullDocument: "updateLookup")
  // change.updateDescription.updatedFields lists the changed fields
  // change._id is the resume token &mdash; persist it for resilience
})

// Resume after a crash
const stream = db.collection("orders").watch([], { resumeAfter: lastSavedToken })

// Watch a database or the whole cluster
db.watch()                  // database-level
client.watch()              // cluster-level (Enterprise / Atlas)</code></pre>

<p><strong>What change streams power</strong>:</p>
<ul>
  <li><strong>Real-time UI updates</strong> &mdash; push to clients via WebSocket / SSE.</li>
  <li><strong>Cache invalidation</strong> &mdash; flip Redis keys when MongoDB changes.</li>
  <li><strong>Search index sync</strong> &mdash; mirror to <strong>Elasticsearch</strong> / <strong>Atlas Search</strong> / <strong>Meilisearch</strong> on every write.</li>
  <li><strong>Audit trails</strong> &mdash; stream every change to S3 / BigQuery for compliance.</li>
  <li><strong>Triggers</strong> &mdash; run business logic when documents change. Atlas Triggers wrap this with serverless Functions.</li>
</ul>

<p><strong>Operational notes</strong>: change streams require a replica set (the oplog is the source). Always persist the <strong>resume token</strong> after processing so you can pick up where you left off after a crash; without it, you lose anything written during the gap. The oplog window (default ~24h on Atlas) is your maximum tolerable downtime for the consumer.</p>
'''

ANSWERS[12] = r'''
<p>MongoDB handles large data volumes through three layered partitioning strategies, each addressing a different scale problem.</p>

<table>
  <tr><th>Strategy</th><th>What it partitions</th><th>When you need it</th></tr>
  <tr><td>Sharding</td><td>A collection across servers</td><td>Working set exceeds one machine&rsquo;s RAM, or write rate exceeds one machine&rsquo;s CPU</td></tr>
  <tr><td>Time-series collections</td><td>Documents into hourly buckets on disk</td><td>IoT, metrics, logs &mdash; high-volume time-stamped data</td></tr>
  <tr><td>Tiered storage / Atlas Online Archive</td><td>Hot vs cold data across storage classes</td><td>Compliance retention, infrequently accessed history</td></tr>
</table>

<p><strong>Sharding</strong> is the heavyweight option. Pick a shard key that distributes both reads and writes evenly &mdash; <code>{ tenant_id: 1, _id: 1 }</code> for SaaS, hashed <code>user_id</code> for IoT, geo-zoned keys for regional residency.</p>

<p><strong>Time-series collections</strong> (5.0+) automatically bucket measurements by time window and metadata, dramatically reducing storage and accelerating range queries:</p>
<pre><code>db.createCollection("sensor_readings", {
  timeseries: {
    timeField:    "ts",
    metaField:    "sensor_id",
    granularity:  "minutes"
  },
  expireAfterSeconds: 30 * 24 * 3600   // auto-delete after 30 days
})</code></pre>

<p><strong>Atlas Online Archive</strong> moves cold documents from your hot cluster to cheap S3-backed storage based on age or query frequency &mdash; queryable through the same federated endpoint as your live data. This is how production teams keep multi-year retention without paying for hot capacity. Self-hosted equivalent: periodic <code>$out</code> to a separate &ldquo;archive&rdquo; cluster + a <strong>Data Federation</strong> setup for unified queries.</p>

<p>For analytics over very large MongoDB data, push to a warehouse: <strong>BigQuery</strong>, <strong>Snowflake</strong>, or <strong>Databricks</strong> via <strong>Airbyte</strong>, <strong>Fivetran</strong>, or Atlas&rsquo;s built-in <strong>Stream Processing</strong>.</p>
'''

ANSWERS[13] = r'''
<p><strong>WiredTiger</strong> has been MongoDB&rsquo;s default storage engine since 3.2. It&rsquo;s a modern <strong>B+tree-based, MVCC-aware engine</strong> with document-level concurrency, prefix-compressed indexes, and snappy compression by default.</p>

<p><strong>Key internals</strong>:</p>
<ul>
  <li><strong>B+tree on disk</strong>: each collection and index is its own B+tree file. Pages default to 32KB and are compressed with Snappy (~50% reduction typical).</li>
  <li><strong>MVCC for concurrency</strong>: writes create new versions; readers see a consistent snapshot. Document-level locking means concurrent writers don&rsquo;t block each other unless they touch the same document.</li>
  <li><strong>Cache</strong>: WiredTiger maintains its own cache (default 50% of RAM minus 1GB). Hot data lives here; queries that fit in cache are blazingly fast.</li>
  <li><strong>Checkpoints</strong>: every 60 seconds, dirty pages are flushed to disk &mdash; recovery on crash replays only the journal since the last checkpoint.</li>
  <li><strong>Journal</strong>: write-ahead log for durability. With <code>j: true</code>, a write is acknowledged only after journal fsync.</li>
</ul>

<p><strong>Tuning levers that matter</strong>:</p>
<table>
  <tr><th>Setting</th><th>Effect</th></tr>
  <tr><td><code>storage.wiredTiger.engineConfig.cacheSizeGB</code></td><td>How much RAM the cache uses</td></tr>
  <tr><td><code>storage.wiredTiger.collectionConfig.blockCompressor</code></td><td><code>snappy</code> (default), <code>zstd</code> (better ratio), <code>none</code></td></tr>
  <tr><td><code>storage.wiredTiger.indexConfig.prefixCompression</code></td><td>Saves index space (default on)</td></tr>
</table>

<p>Use <strong>zstd</strong> compression on cold or archival collections &mdash; ~30% better ratio than snappy at moderate CPU cost. Monitor cache pressure via <code>db.serverStatus().wiredTiger.cache</code>; if &ldquo;tracked dirty bytes&rdquo; routinely exceeds the eviction trigger threshold, the cache is too small.</p>
'''

ANSWERS[14] = r'''
<p>High write throughput in MongoDB comes from <strong>removing bottlenecks</strong> at every layer: client batching, write concern, indexing, hardware, and topology.</p>

<p><strong>The hierarchy of write optimizations</strong>:</p>
<ol>
  <li><strong>Batch writes</strong> &mdash; <code>insertMany</code> / <code>bulkWrite</code> with <code>{ ordered: false }</code> can be 10x faster than individual <code>insertOne</code> calls. Optimal batch size is 500-1000.</li>
  <li><strong>Tune write concern</strong> &mdash; <code>w: 1</code> is faster than <code>w: "majority"</code>; <code>j: false</code> faster than <code>j: true</code>. Use stricter levels only where durability matters more than throughput.</li>
  <li><strong>Minimize indexes</strong> &mdash; every secondary index is updated on every insert. Drop unused ones (find via <code>$indexStats</code>); avoid &ldquo;just in case&rdquo; indexes.</li>
  <li><strong>Avoid document growth</strong> &mdash; <code>$push</code>-ing into unbounded arrays causes documents to relocate on disk. Cap arrays with <code>$slice</code> or use a separate collection.</li>
  <li><strong>Use <code>WriteResult</code> sparingly</strong> &mdash; if you don&rsquo;t need the return value, drivers can fire-and-forget faster.</li>
</ol>

<p><strong>Hardware and topology</strong>:</p>
<ul>
  <li><strong>NVMe SSDs</strong> &mdash; journal fsync is the dominant cost; faster disks mean faster commits.</li>
  <li><strong>RAM &gt;= working set</strong> &mdash; if writes touch documents not in cache, every write becomes a read-modify-write disk operation.</li>
  <li><strong>Sharding</strong> with a <strong>hashed shard key</strong> &mdash; spreads writes evenly across shards, avoiding the &ldquo;last chunk hot spot&rdquo; problem with monotonic keys.</li>
  <li><strong>Disable journal compression</strong> for write-heavy workloads &mdash; <code>storage.wiredTiger.engineConfig.journalCompressor: "none"</code>.</li>
</ul>

<p><strong>Time-series collections (5.0+)</strong> are purpose-built for high-volume time-stamped writes &mdash; auto-bucketing reduces document count and dramatically improves throughput vs a regular collection. For ingestion at extreme scale (millions of writes/sec), front MongoDB with <strong>Kafka</strong> or <strong>Redpanda</strong> for buffering, and consume with batched <code>insertMany</code>.</p>
'''

ANSWERS[15] = r'''
<p><strong>MMAPv1</strong> was MongoDB&rsquo;s original storage engine. It was deprecated in 4.0 and <strong>removed in 4.2</strong> &mdash; you can&rsquo;t use it anymore. The default everywhere now is <strong>WiredTiger</strong>.</p>

<table>
  <tr><th>Aspect</th><th>WiredTiger</th><th>MMAPv1 (legacy)</th></tr>
  <tr><td>Concurrency</td><td>Document-level locking</td><td>Database-level locking (terrible for concurrent writes)</td></tr>
  <tr><td>Compression</td><td>Snappy/zstd by default; ~50% reduction</td><td>None &mdash; data on disk same size as in memory</td></tr>
  <tr><td>MVCC</td><td>Yes &mdash; readers don&rsquo;t block writers</td><td>No &mdash; readers and writers contend</td></tr>
  <tr><td>Cache</td><td>Custom WiredTiger cache</td><td>Memory-mapped files via OS page cache</td></tr>
  <tr><td>Index structure</td><td>B+tree with prefix compression</td><td>B-tree, no compression</td></tr>
  <tr><td>Journal</td><td>Write-ahead log; configurable fsync</td><td>Write-ahead log</td></tr>
  <tr><td>Encrypted at rest</td><td>Yes (Enterprise / Atlas)</td><td>No</td></tr>
</table>

<p><strong>Why WiredTiger replaced MMAPv1</strong>:</p>
<ul>
  <li><strong>Concurrency</strong>: MMAPv1&rsquo;s database-level locks meant 100 writers were essentially serialized; WiredTiger lets each write proceed independently as long as it touches a different document.</li>
  <li><strong>Storage efficiency</strong>: 2-3x reduction in disk footprint for typical workloads.</li>
  <li><strong>Crash recovery</strong>: faster, more reliable.</li>
  <li><strong>Modern feature parity</strong>: encryption at rest, snapshots, resharding, and multi-document transactions all require WiredTiger.</li>
</ul>

<p>The transition was so successful that MongoDB never seriously considered other engines. <strong>InMemory</strong> is the only alternative shipped (Enterprise) &mdash; same WiredTiger codebase but RAM-only, used for caches and ephemeral high-throughput tiers. If you encounter MMAPv1 in legacy docs or training material, treat it as historical context only.</p>
'''

ANSWERS[16] = r'''
<p><strong>MongoDB Atlas</strong> is the official fully-managed cloud database service. It runs MongoDB on AWS, Azure, or GCP with the cluster operations &mdash; provisioning, replication, sharding, backup, monitoring, security &mdash; handled automatically.</p>

<p><strong>Core capabilities</strong>:</p>
<ul>
  <li><strong>One-click clusters</strong>: create a 3-node replica set or sharded cluster across multiple availability zones in any of 100+ regions.</li>
  <li><strong>Automated backups</strong>: continuous, point-in-time restore, cross-region copies, queryable snapshots without restore.</li>
  <li><strong>Atlas Search</strong>: Lucene-powered full-text search, autocomplete, faceting, embedded directly in the database &mdash; no separate Elasticsearch cluster.</li>
  <li><strong>Vector Search</strong>: ANN indexes for embeddings; native support for OpenAI/Cohere embeddings and hybrid search with text.</li>
  <li><strong>Online Archive</strong>: tiered storage &mdash; cold data automatically moved to cheap S3-backed storage, queryable via the same endpoint.</li>
  <li><strong>Data Federation</strong>: query across MongoDB clusters, S3 buckets, and Azure Blob Storage in a single aggregation.</li>
  <li><strong>Triggers + Functions</strong>: serverless event handlers fired on database changes, schedules, or HTTPS endpoints.</li>
  <li><strong>Stream Processing</strong>: Kafka-style streaming aggregations using MongoDB&rsquo;s aggregation language.</li>
  <li><strong>Charts</strong>: built-in BI dashboards on top of your data.</li>
  <li><strong>Performance Advisor</strong>: scans queries and recommends indexes; spots unused ones.</li>
</ul>

<p><strong>Operational features</strong>: VPC peering, AWS PrivateLink, x.509 / IAM / SSO authentication, encryption at rest with customer-managed keys (KMS), and detailed audit logs. The free <strong>M0</strong> tier (512MB) is good for prototyping; production clusters scale from M10 to multi-TB sharded deployments.</p>

<p>For the vast majority of teams, Atlas is the right answer &mdash; the ops cost of self-hosted MongoDB at scale (24/7 monitoring, backup verification, security patching, sharding rebalances) is real and rarely smaller than the Atlas premium.</p>
'''

ANSWERS[17] = r'''
<p>Encryption at rest protects MongoDB data files from physical theft of the underlying disk &mdash; if someone walks off with the storage device, they can&rsquo;t read the data without the key. MongoDB Enterprise and Atlas both support this natively; community edition relies on filesystem-level encryption.</p>

<p><strong>Three layers of at-rest encryption</strong>:</p>
<table>
  <tr><th>Layer</th><th>Coverage</th><th>How</th></tr>
  <tr><td>Filesystem</td><td>Entire disk volume</td><td>LUKS (Linux), BitLocker, AWS EBS encryption</td></tr>
  <tr><td>Storage engine</td><td>Database files only</td><td>WiredTiger encrypted storage (Enterprise)</td></tr>
  <tr><td>Field-level</td><td>Specific fields, even from DBAs</td><td>Client-Side Field-Level Encryption (CSFLE) / Queryable Encryption</td></tr>
</table>

<pre><code>// Enterprise: WiredTiger encrypted storage with KMIP key management
mongod --enableEncryption \
       --kmipServerName kms.example.com \
       --kmipPort 5696 \
       --kmipServerCAFile /etc/ssl/kmip-ca.pem \
       --encryptionKeyFile /etc/mongodb/master-key   # local key (dev only)</code></pre>

<p><strong>Atlas managed encryption</strong>: enabled by default with MongoDB-managed keys. Upgrade to <strong>Customer Key Management</strong> with AWS KMS, Azure Key Vault, or GCP Cloud KMS for compliance &mdash; you control the key, can revoke it instantly, and the data becomes unreadable.</p>

<p><strong>Field-level encryption (CSFLE)</strong>: encrypts specific fields client-side before they reach MongoDB. The database never sees the plaintext &mdash; even cluster admins can&rsquo;t read PII columns. <strong>Queryable Encryption</strong> (6.0+) extends this with the ability to perform equality and range queries on encrypted fields, using a custom encryption scheme.</p>

<p><strong>Layered approach for compliance</strong>: filesystem encryption (cheap, broad) + storage engine encryption (per-cluster keys, regulator-friendly) + Queryable Encryption (sensitive fields beyond admin reach). HIPAA, PCI-DSS, GDPR auditors generally want at least two of these.</p>
'''

ANSWERS[18] = r'''
<p><strong>MongoDB Ops Manager</strong> is the on-premises management platform shipped with MongoDB Enterprise &mdash; the self-hosted equivalent of MongoDB Atlas. It provides cluster lifecycle management, monitoring, backup, and automation for organizations that can&rsquo;t use cloud-managed Atlas (regulatory or air-gap requirements).</p>

<p><strong>Capabilities</strong>:</p>
<ul>
  <li><strong>Automation</strong>: deploy replica sets and sharded clusters from a UI, perform rolling upgrades, modify configs cluster-wide. Agents on each node enact the changes.</li>
  <li><strong>Monitoring</strong>: time-series metrics for every <code>mongod</code> &mdash; CPU, memory, replication lag, query latency, index hit rates, oplog window.</li>
  <li><strong>Backup</strong>: continuous block-level backup with point-in-time restore. Snapshots stored to local file system, S3, or other object storage.</li>
  <li><strong>Alerting</strong>: thresholds on any metric &mdash; replica lag, disk usage, slow queries &mdash; routed to PagerDuty, Slack, OpsGenie.</li>
  <li><strong>Performance Advisor</strong>: same query analysis and index suggestions as Atlas.</li>
  <li><strong>LDAP / Kerberos integration</strong> for enterprise SSO.</li>
</ul>

<p><strong>Architecture</strong>: Ops Manager itself runs as a HA cluster (typically 3 nodes) backed by its own MongoDB application database. Agents on each managed node communicate over HTTPS with the Ops Manager core. The database can be shared with the cluster being managed (small deployments) or separate (recommended).</p>

<p>For most teams the relevant comparison is <strong>Ops Manager vs Atlas</strong>: Atlas is fully managed by MongoDB Inc., so you pay a premium but skip all the &ldquo;running the management plane&rdquo; work. Ops Manager makes sense for highly regulated environments (banking, government, defense) or air-gapped deployments where calling out to a public cloud isn&rsquo;t an option. <strong>Cloud Manager</strong> is the SaaS variant for hybrid setups &mdash; you run the database, MongoDB Inc. runs the control plane.</p>
'''

ANSWERS[19] = r'''
<p>The <strong>aggregation pipeline</strong> is MongoDB&rsquo;s primary tool for complex data analysis &mdash; a sequence of stages, each transforming documents and passing them downstream. It replaces SQL&rsquo;s SELECT/GROUP BY/JOIN/HAVING with a composable JSON pipeline.</p>

<pre><code>db.orders.aggregate([
  { $match: { status: "paid", created_at: { $gte: ISODate("2026-01-01") } } },
  { $group: {
      _id: { customer: "$customer_id", month: { $dateTrunc: { date: "$created_at", unit: "month" } } },
      revenue: { $sum: "$amount" },
      orders:  { $sum: 1 }
  }},
  { $lookup: { from: "customers", localField: "_id.customer", foreignField: "_id", as: "customer" } },
  { $unwind: "$customer" },
  { $facet: {
      top_customers: [{ $sort: { revenue: -1 } }, { $limit: 10 }],
      monthly_summary: [
        { $group: { _id: "$_id.month", total_revenue: { $sum: "$revenue" } } },
        { $sort: { _id: 1 } }
      ]
  }},
  { $merge: { into: "monthly_dashboards", on: "_id" } }
])</code></pre>

<p><strong>Pipeline design principles for performance</strong>:</p>
<ul>
  <li><strong><code>$match</code> first</strong> &mdash; only the leading filter can use indexes. The earlier you cut volume, the cheaper everything downstream.</li>
  <li><strong><code>$project</code> to drop unused fields</strong> early &mdash; smaller documents flow faster.</li>
  <li><strong><code>$sort + $limit</code></strong> together can use the &ldquo;top-K&rdquo; optimization &mdash; MongoDB only tracks the top N during the sort.</li>
  <li><strong><code>$lookup</code></strong> requires an index on the foreign field; otherwise it does a per-document scan.</li>
  <li><strong><code>$facet</code></strong> runs sub-pipelines in parallel &mdash; one query for an entire dashboard.</li>
  <li><strong><code>$merge</code></strong> writes the result to a target collection &mdash; the basis for materialized views.</li>
</ul>

<p><strong>Modern operators</strong> like <code>$dateTrunc</code>, <code>$percentile</code>, <code>$top</code>/<code>$bottom</code>, <code>$setWindowFields</code> (5.0+/7.0+) bring the aggregation language close to SQL window functions and analytics. For multi-TB analytics, push to a warehouse (<strong>BigQuery</strong>, <strong>Snowflake</strong>, <strong>Databricks</strong>) via <strong>Atlas Stream Processing</strong> or CDC pipelines &mdash; MongoDB excels at operational analytics, not OLAP at extreme scale.</p>
'''

ANSWERS[20] = r'''
<p>MongoDB <strong>multi-document transactions</strong> (4.0+ replica sets, 4.2+ sharded clusters) provide ACID semantics across multiple documents, collections, and even databases. They behave like a SQL transaction: a sequence of operations that either all commit or all roll back.</p>

<pre><code>// Node.js driver: atomic transfer between two accounts
const session = client.startSession()
try {
  await session.withTransaction(async () =&gt; {
    const accounts = client.db("bank").collection("accounts")
    await accounts.updateOne(
      { _id: fromId, balance: { $gte: 100 } },
      { $inc: { balance: -100 } },
      { session }
    )
    await accounts.updateOne(
      { _id: toId },
      { $inc: { balance: 100 } },
      { session }
    )
    await client.db("bank").collection("transfers").insertOne(
      { from: fromId, to: toId, amount: 100, ts: new Date() },
      { session }
    )
  }, {
    readConcern:  { level: "snapshot" },
    writeConcern: { w: "majority" },
    readPreference: "primary"
  })
} finally {
  await session.endSession()
}</code></pre>

<p><strong>Key semantics</strong>:</p>
<ul>
  <li><strong>Snapshot isolation</strong> &mdash; the transaction sees a consistent view as of the start time; nothing leaks from concurrent transactions.</li>
  <li><strong>Atomic commit</strong> &mdash; all writes appear at once or not at all.</li>
  <li><strong>60-second default timeout</strong> &mdash; long transactions abort automatically. Tunable with <code>transactionLifetimeLimitSeconds</code>.</li>
  <li><strong>Cross-shard transactions</strong> use a 2-phase commit protocol &mdash; significantly slower than single-shard.</li>
  <li><strong><code>withTransaction</code></strong> auto-retries on transient errors (write conflicts, primary failover) &mdash; the recommended API.</li>
</ul>

<p><strong>When to use them &mdash; and when not to</strong>: transactions reduce throughput substantially. Document-level atomicity (a single <code>updateOne</code>) is enough for most cases &mdash; a well-designed schema embeds related data so transactions become unnecessary. Reach for transactions when invariants span documents (banking transfers, inventory + order, append-only audit + state change). For event-driven cross-service consistency, prefer <strong>outbox pattern</strong> with Debezium CDC or <strong>sagas</strong> over distributed MongoDB transactions.</p>
'''

ANSWERS[21] = r'''
<p>The <strong><code>$lookup</code></strong> stage performs a <strong>left outer join</strong> between two collections inside an aggregation pipeline. The result of each match is added to the source document as an array field.</p>

<pre><code>// Simple form &mdash; equality on one field each side
db.orders.aggregate([
  { $lookup: {
      from:         "customers",
      localField:   "customer_id",
      foreignField: "_id",
      as:           "customer"
  }},
  { $unwind: "$customer" }       // flatten 1-element array for 1:1 joins
])

// Pipeline form &mdash; filter / project on the joined side, multi-condition joins
db.orders.aggregate([
  { $lookup: {
      from:     "products",
      let:      { skus: "$line_items.sku", region: "$ship_to" },
      pipeline: [
        { $match: { $expr: {
            $and: [
              { $in: ["$sku", "$$skus"] },
              { $eq: ["$available_in", "$$region"] }
            ]
        }}},
        { $project: { sku: 1, name: 1, price: 1 } }
      ],
      as: "line_items_meta"
  }}
])</code></pre>

<p><strong>Performance reality</strong>:</p>
<ul>
  <li><strong>Index the foreign field</strong> &mdash; otherwise <code>$lookup</code> scans the joined collection for every input document.</li>
  <li><strong>Filter the source first</strong> with <code>$match</code> &mdash; fewer source rows means fewer per-row joins.</li>
  <li><strong>Project away unused source fields</strong> &mdash; smaller documents are cheaper to carry.</li>
  <li><strong>Across shards</strong>: <code>$lookup</code> against an unsharded foreign collection runs on each shard; against a sharded foreign collection it runs through <code>mongos</code>. The latter can be slow.</li>
</ul>

<p><strong>When to embed instead</strong>: if you constantly join the same way, embedding the looked-up data into the source document removes the join entirely &mdash; a denormalization win. The classic e-commerce pattern is to copy the <em>relevant fields</em> from <code>products</code> into each <code>order</code> line item at write time, accepting that historical orders show the price as it was at order time. This is faster <em>and</em> more correct for finance.</p>

<p>Heavy multi-table relational analytics deserves a relational database or warehouse &mdash; MongoDB&rsquo;s <code>$lookup</code> is fine for occasional joins, not the foundation of a star schema.</p>
'''

ANSWERS[22] = r'''
<p>MongoDB&rsquo;s concurrency model centers on <strong>document-level locking with MVCC</strong> on the WiredTiger storage engine. Multiple writers can update <em>different</em> documents in the same collection simultaneously without blocking each other; only writers touching the <em>same</em> document serialize.</p>

<p><strong>Isolation levels in MongoDB</strong>:</p>
<table>
  <tr><th>Level</th><th>Where used</th><th>Guarantees</th></tr>
  <tr><td>Default (read &ldquo;local&rdquo;)</td><td>Standard reads</td><td>Reads see committed local data; may differ between members</td></tr>
  <tr><td><code>readConcern: "majority"</code></td><td>Strongly-consistent reads</td><td>Sees only data acknowledged by a majority of replicas</td></tr>
  <tr><td><code>readConcern: "snapshot"</code></td><td>Inside transactions</td><td>Snapshot isolation &mdash; consistent point-in-time view</td></tr>
  <tr><td><code>readConcern: "linearizable"</code></td><td>Single-document, primary only</td><td>Strongest &mdash; sees all writes that ended before this read started</td></tr>
</table>

<p><strong>Single-document atomicity is the foundation</strong>: every operation on a single document &mdash; even one that updates many fields with <code>$set</code>, <code>$push</code>, and <code>$inc</code> together &mdash; is fully atomic. This is why MongoDB&rsquo;s embedded-document modeling is powerful: by colocating related data into one document, you get transactional semantics without paying the multi-document transaction cost.</p>

<p><strong>Conflict resolution</strong>: when two transactions try to modify the same document, one of them aborts with a <strong>WriteConflict</strong> error and is retried (drivers handle this automatically inside <code>withTransaction</code>). For hot-document contention &mdash; a viral post&rsquo;s like counter, a global rate limiter &mdash; spread the value across multiple shards (<em>sharded counters</em>), batch updates, or use Redis for the hot path and persist asynchronously.</p>

<p><strong>Read-your-writes consistency</strong>: clients within a <strong>causally consistent session</strong> always see their own writes, even when reads route to secondaries. <code>client.startSession({ causalConsistency: true })</code> &mdash; on by default in modern drivers.</p>
'''

ANSWERS[23] = r'''
<p><strong><code>mongodump</code></strong> produces a BSON-encoded backup of a database; <strong><code>mongorestore</code></strong> replays it. They&rsquo;re schema-aware, scriptable, and the standard tool for logical backups outside Atlas.</p>

<pre><code>// Full cluster dump
mongodump --uri="mongodb://localhost:27017" --out=/backup/$(date +%F)

// Specific database
mongodump --uri="mongodb://localhost:27017" --db=shopdb --out=/backup

// With auth + TLS + gzip
mongodump --uri="mongodb+srv://user:pass@cluster0.mongodb.net" \
          --gzip \
          --archive=/backup/snapshot-$(date +%F).gz

// Restore the entire archive
mongorestore --uri="mongodb://localhost:27017" --gzip --archive=/backup/snapshot.gz

// Selective restore: rename DB on the way in
mongorestore --uri=... \
             --nsFrom='shopdb.*' --nsTo='shopdb_restore.*' \
             --gzip --archive=/backup/snapshot.gz</code></pre>

<p><strong>Important characteristics</strong>:</p>
<ul>
  <li><strong>Logical backups</strong> &mdash; not snapshots. They iterate the collection at read time, so very large databases take hours.</li>
  <li><strong>Point-in-time consistency</strong> &mdash; only when run with <code>--oplog</code> against a replica set. Without it, the dump can span minutes of writes and be inconsistent.</li>
  <li><strong>Restore is not atomic</strong>: indexes are rebuilt at the end (<code>--noIndexRestore</code> + manual <code>createIndex</code> for very large collections).</li>
</ul>

<p><strong>Production-grade strategies</strong>:</p>
<table>
  <tr><th>Approach</th><th>Use case</th></tr>
  <tr><td><strong>Atlas continuous backup</strong></td><td>Default for cloud &mdash; PIT restore, queryable snapshots</td></tr>
  <tr><td><strong>EBS / disk snapshots</strong></td><td>Self-hosted, high-volume &mdash; minutes vs hours of mongodump</td></tr>
  <tr><td><strong>Filesystem snapshots</strong> (LVM, ZFS)</td><td>Same idea on bare metal</td></tr>
  <tr><td><strong>mongodump</strong></td><td>Migrations, small DBs, partial extracts, CI fixtures</td></tr>
  <tr><td><strong>Percona Backup for MongoDB</strong> (PBM)</td><td>Open-source PIT for self-hosted</td></tr>
</table>

<p>Whatever the method, <strong>test restores quarterly</strong> &mdash; a backup that was never restored is a hope, not a backup. Atlas does this automatically; for self-hosted, automate a restore-into-test-cluster + smoke test.</p>
'''

ANSWERS[24] = r'''
<p>The <strong>embed vs reference</strong> decision is the most consequential modeling choice in MongoDB. The right answer depends on how the data is accessed, how it changes, and how big it can grow.</p>

<table>
  <tr><th>Aspect</th><th>Embedded</th><th>Referenced</th></tr>
  <tr><td>Read pattern</td><td>One query, one I/O</td><td>Two queries (or <code>$lookup</code>)</td></tr>
  <tr><td>Write pattern</td><td>One atomic update</td><td>Multi-doc; needs transaction for atomicity</td></tr>
  <tr><td>Document size</td><td>Limited to 16 MB BSON</td><td>Unlimited &mdash; data lives elsewhere</td></tr>
  <tr><td>Update frequency</td><td>Best when sub-data rarely changes</td><td>Best when sub-data changes often</td></tr>
  <tr><td>Consistency</td><td>Always consistent (single doc)</td><td>Possible drift between source and copies</td></tr>
  <tr><td>Querying sub-data alone</td><td>Awkward &mdash; need <code>$unwind</code></td><td>Natural &mdash; sub-data is its own collection</td></tr>
</table>

<p><strong>Embed when</strong>:</p>
<ul>
  <li>The sub-data is read together with the parent every time (post + comments-on-display, order + line items).</li>
  <li>The sub-data is bounded in size (under ~100 KB; arrays under a few hundred elements).</li>
  <li>Atomicity matters &mdash; both must change together.</li>
</ul>

<p><strong>Reference when</strong>:</p>
<ul>
  <li>The sub-data is large or unbounded (user&rsquo;s lifetime activity, sensor readings).</li>
  <li>Sub-data is shared across many parents (a single tag attached to thousands of posts).</li>
  <li>Sub-data is queried in its own right (find all comments by user X across all posts).</li>
  <li>Sub-data has its own access control or lifecycle.</li>
</ul>

<p><strong>Hybrid pattern</strong> (most common in production): embed the <em>recent N</em> or <em>summary</em> while keeping the full history in a separate collection. <em>Last 10 comments embedded for fast display, full thread in <code>comments</code> collection.</em> This combines fast reads with unbounded storage. Maintain the embed atomically with <code>$push</code> + <code>$slice: -10</code> on every comment insertion.</p>
'''

ANSWERS[25] = r'''
<p><strong>GridFS</strong> is MongoDB&rsquo;s convention for storing files larger than the 16 MB BSON document limit. It splits a file into 255 KB chunks, stores them as documents in a <code>fs.chunks</code> collection, and keeps file metadata in <code>fs.files</code>.</p>

<pre><code>// Node.js driver
const { GridFSBucket } = require("mongodb")
const bucket = new GridFSBucket(client.db("media"))

// Upload
fs.createReadStream("/path/to/video.mp4")
  .pipe(bucket.openUploadStream("video.mp4", {
    metadata: { user_id: 42, mimeType: "video/mp4" }
  }))

// Download
bucket.openDownloadStreamByName("video.mp4")
  .pipe(fs.createWriteStream("/tmp/restored.mp4"))

// Find file metadata
db.fs.files.find({ "metadata.user_id": 42 })

// Delete
bucket.delete(fileId)</code></pre>

<p><strong>How it works internally</strong>: each upload creates one <code>fs.files</code> document (filename, length, chunkSize, uploadDate, metadata) plus N <code>fs.chunks</code> documents (each ~255 KB of binary data linked back by <code>files_id</code>). Reads stream chunks back in order. The default <code>fs.chunks</code> index on <code>{ files_id: 1, n: 1 }</code> makes ordered reads efficient.</p>

<p><strong>Honest assessment</strong>: GridFS is rarely the right choice in 2026. For media files (images, video, PDFs):</p>
<ul>
  <li><strong>Object storage</strong> &mdash; <strong>S3</strong>, <strong>Cloudflare R2</strong>, <strong>Backblaze B2</strong>, <strong>GCS</strong>, <strong>Azure Blob</strong> &mdash; is purpose-built and dramatically cheaper.</li>
  <li><strong>CDN-backed providers</strong> &mdash; <strong>Cloudinary</strong>, <strong>imgix</strong>, <strong>Cloudflare Images</strong>, <strong>Bunny</strong>, <strong>ImageKit</strong>, <strong>Uploadcare</strong> &mdash; add transformations, optimization, and global delivery.</li>
  <li><strong>Mux</strong>, <strong>api.video</strong>, <strong>Cloudflare Stream</strong> for video specifically.</li>
</ul>

<p><strong>When GridFS does fit</strong>: when files must live in the same backup/replication boundary as their metadata for compliance, when you can&rsquo;t use external storage (air-gap), or for small (single-digit GB) bundles where adding S3 isn&rsquo;t worth the operational cost. Otherwise, store binary content externally and keep a reference (<code>{ s3_url: "..." }</code>) in MongoDB.</p>
'''

ANSWERS[26] = r'''
<p>The <strong>oplog</strong> (operations log) is a special <strong>capped collection</strong> in the <code>local</code> database that records every write operation that modifies user data on the primary. Secondaries replicate by tailing the primary&rsquo;s oplog and replaying its entries in order &mdash; this is the foundation of MongoDB replication, change streams, and resumable backups.</p>

<pre><code>// Inspect the oplog (on a replica set member)
use local
db.oplog.rs.find().sort({ ts: -1 }).limit(5)
// {
//   ts:  Timestamp(1714233456, 1),     // operation time
//   t:   42,                            // primary&rsquo;s term number
//   h:   NumberLong("..."),             // hash for chain integrity
//   v:   2,                             // oplog format version
//   op:  "u",                           // i / u / d / c / n
//   ns:  "shopdb.orders",               // namespace
//   o2:  { _id: ObjectId("...") },      // pre-image (for u/d)
//   o:   { $set: { status: "shipped" } } // the operation
// }</code></pre>

<p><strong>Operation types</strong>: <code>i</code> (insert), <code>u</code> (update), <code>d</code> (delete), <code>c</code> (command e.g., create/drop), <code>n</code> (no-op heartbeat). Each entry is <strong>idempotent</strong> &mdash; replaying the same entry twice produces the same result, which is what makes recovery and resync safe.</p>

<p><strong>Sizing matters &mdash; the oplog window</strong>:</p>
<ul>
  <li>Default size: 5% of free disk, capped at 50 GB.</li>
  <li>The <strong>oplog window</strong> is the time span the oplog covers &mdash; if a secondary is offline longer than this, it can&rsquo;t catch up by replay and needs a full <strong>initial sync</strong>.</li>
  <li>Aim for at least 24-48 hours of window. Resize with <code>db.adminCommand({ replSetResizeOplog: 1, size: 16384 })</code> (in MB).</li>
</ul>

<p><strong>What the oplog enables beyond replication</strong>: <strong>change streams</strong> tail the oplog with a friendly API; <strong>point-in-time backups</strong> apply oplog entries onto a base snapshot to reach an exact target time; <strong>Debezium for MongoDB</strong> uses the oplog for CDC into Kafka. The oplog is essentially MongoDB&rsquo;s WAL, exposed as a queryable collection.</p>
'''

ANSWERS[27] = r'''
<p>A <strong>network partition</strong> (split-brain risk) is when replica-set members can&rsquo;t communicate with each other. MongoDB&rsquo;s elect-by-majority algorithm guarantees <em>at most one primary at a time</em>, which makes split-brain effectively impossible &mdash; but the &ldquo;wrong side&rdquo; of a partition becomes read-only.</p>

<p><strong>How elections handle partitions</strong>: a candidate must receive votes from a <strong>majority of voting members</strong> to be elected primary. With 3 nodes and a 2-1 split, only the side with 2 nodes can elect a primary; the lone node steps down to secondary and refuses writes. The minority side is effectively read-only with stale data until the partition heals.</p>

<table>
  <tr><th>Topology</th><th>Survives N failures</th><th>Notes</th></tr>
  <tr><td>3 voting members</td><td>1</td><td>Cheapest HA setup</td></tr>
  <tr><td>5 voting members</td><td>2</td><td>Recommended for production</td></tr>
  <tr><td>3 + arbiter</td><td>1 (avoid &mdash; risky)</td><td>Arbiter votes but holds no data &mdash; data loss risk</td></tr>
  <tr><td>Multi-region 3-node</td><td>1 region</td><td>Spread across AZs/regions for true resilience</td></tr>
</table>

<p><strong>Mitigations and resolution</strong>:</p>
<ul>
  <li><strong>Spread members across availability zones</strong> &mdash; a single AZ outage shouldn&rsquo;t take down the majority. Atlas does this by default.</li>
  <li><strong>Use <code>writeConcern: "majority"</code></strong> &mdash; writes that aren&rsquo;t replicated to a majority can be rolled back during failover. Majority commits guarantee no rollback.</li>
  <li><strong>Avoid arbiters</strong> in modern designs &mdash; they add a vote but no data, so two data nodes plus an arbiter can&rsquo;t safely use majority writes if one data node fails.</li>
  <li><strong>When the partition heals</strong>, the formerly-primary side discovers a higher-term primary and rolls back its uncommitted writes via the <strong>rollback file</strong> (saved to disk for inspection). With <code>w: "majority"</code>, this rollback is empty.</li>
</ul>

<p>The architectural lesson: MongoDB chooses <strong>consistency over availability</strong> during partitions (CP). Acknowledge this in your application &mdash; design for occasional &ldquo;primary unavailable&rdquo; errors during failover (typically 5-15 seconds) and retry idempotent operations.</p>
'''

ANSWERS[28] = r'''
<p>Time-series data (sensors, metrics, financial ticks, app logs) has predictable characteristics: high write rates, monotonic timestamps, queries by time range and metadata. MongoDB 5.0 added native <strong>time-series collections</strong> purpose-built for this.</p>

<pre><code>db.createCollection("sensor_readings", {
  timeseries: {
    timeField:    "ts",          // required &mdash; the timestamp field
    metaField:    "sensor_id",   // optional &mdash; logical series identifier
    granularity:  "minutes"      // seconds | minutes | hours
  },
  expireAfterSeconds: 90 * 24 * 3600   // optional TTL
})

// Insert as if it were a regular collection
db.sensor_readings.insertMany([
  { ts: ISODate("2026-04-28T10:00:00Z"), sensor_id: "S1", temp: 22.5, humidity: 60 },
  { ts: ISODate("2026-04-28T10:01:00Z"), sensor_id: "S1", temp: 22.7, humidity: 61 }
])

// Range queries with $dateTrunc for bucketed analytics
db.sensor_readings.aggregate([
  { $match: { sensor_id: "S1", ts: { $gte: ISODate("2026-04-28") } } },
  { $group: {
      _id: { $dateTrunc: { date: "$ts", unit: "hour" } },
      avg_temp: { $avg: "$temp" },
      max_temp: { $max: "$temp" }
  }},
  { $sort: { _id: 1 } }
])</code></pre>

<p><strong>How time-series collections optimize</strong>: documents with the same <code>metaField</code> are <em>auto-bucketed</em> into hourly compound documents on disk &mdash; one bucket holds many measurements. This delivers 3-5x storage compression, 5-10x faster range scans, and much smaller indexes. Internally it&rsquo;s a regular collection with a clever bucketing layer; from the application&rsquo;s perspective, you insert and query as usual.</p>

<p><strong>When to use what</strong>:</p>
<table>
  <tr><th>Use case</th><th>Best fit</th></tr>
  <tr><td>Operational metrics, IoT, app logs</td><td>MongoDB time-series collection</td></tr>
  <tr><td>High-cardinality observability</td><td><strong>InfluxDB 3.0</strong>, <strong>QuestDB</strong>, <strong>VictoriaMetrics</strong></td></tr>
  <tr><td>SQL-friendly time-series analytics</td><td><strong>TimescaleDB</strong></td></tr>
  <tr><td>Massive analytical scan</td><td><strong>ClickHouse</strong>, <strong>StarRocks</strong>, <strong>Druid</strong>, <strong>Pinot</strong></td></tr>
</table>

<p>For most operational workloads where the time-series data lives alongside other transactional data, the native MongoDB option keeps the stack simpler.</p>
'''

ANSWERS[29] = r'''
<p>Index optimization in MongoDB is the highest-leverage performance work. The goal is for every important query to hit an index that returns exactly the documents needed (<code>nReturned == totalDocsExamined</code>) and ideally projects only fields the index already covers.</p>

<p><strong>The systematic process</strong>:</p>
<ol>
  <li><strong>Identify slow queries</strong> &mdash; <strong>Atlas Performance Advisor</strong> automates this; self-hosted, enable the profiler with <code>db.setProfilingLevel(1, { slowms: 100 })</code> and tail <code>system.profile</code>. <strong>mongotop</strong>, <strong>mongostat</strong>, and Datadog/New Relic also flag offenders.</li>
  <li><strong>Run <code>.explain("executionStats")</code></strong> on each &mdash; look for <code>COLLSCAN</code> stages, large <code>totalDocsExamined</code>, or <code>SORT</code> in memory.</li>
  <li><strong>Apply the ESR rule</strong> &mdash; <em>E</em>quality fields, <em>S</em>ort fields, <em>R</em>ange fields, in that order.</li>
  <li><strong>Build the index</strong> &mdash; rolling builds on replica sets avoid downtime.</li>
  <li><strong>Re-explain and verify</strong>.</li>
</ol>

<p><strong>The high-impact index types</strong>:</p>
<table>
  <tr><th>Type</th><th>When to use</th></tr>
  <tr><td>Single-field</td><td>Simple equality / range queries</td></tr>
  <tr><td>Compound</td><td>Multi-field filters, follow ESR rule</td></tr>
  <tr><td>Multikey</td><td>Fields that contain arrays</td></tr>
  <tr><td>Partial</td><td>Index only docs matching a filter (e.g., active users)</td></tr>
  <tr><td>Sparse</td><td>Skip documents missing the field</td></tr>
  <tr><td>TTL</td><td>Auto-delete after N seconds</td></tr>
  <tr><td>Hashed</td><td>Even shard distribution</td></tr>
  <tr><td>Wildcard</td><td>Catch-all on dynamic schemas (use carefully)</td></tr>
</table>

<p><strong>The other half &mdash; pruning</strong>: every index costs RAM, write throughput, and disk space. Run <code>$indexStats</code> aggregation periodically to find indexes that are never accessed:</p>
<pre><code>db.collection.aggregate([{ $indexStats: {} }, { $sort: { "accesses.ops": 1 } }])</code></pre>
<p>Drop the unused ones. <strong>Atlas Performance Advisor</strong> flags both missing and unused indexes automatically.</p>

<p>Modern alternative for query optimization: <strong>OtterTune</strong> and <strong>EverSQL</strong> use ML to recommend indexes from production query logs. Useful for huge schemas where manual analysis is impractical.</p>
'''

ANSWERS[30] = r'''
<p>Both <strong>compound indexes</strong> and <strong>multikey indexes</strong> involve multiple values per document, but they solve different problems and behave differently.</p>

<table>
  <tr><th>Aspect</th><th>Compound</th><th>Multikey</th></tr>
  <tr><td>Definition</td><td>Index over multiple <em>fields</em></td><td>Index where a <em>field is an array</em></td></tr>
  <tr><td>Example</td><td><code>{ author: 1, year: -1 }</code></td><td><code>{ tags: 1 }</code> on <code>{ tags: ["a","b","c"] }</code></td></tr>
  <tr><td>Entries per document</td><td>One</td><td>One per array element</td></tr>
  <tr><td>Index size</td><td>Linear in document count</td><td>Linear in <em>total array elements</em> &mdash; can be much larger</td></tr>
  <tr><td>Query support</td><td>Leftmost-prefix queries</td><td>Equality, <code>$in</code>, <code>$all</code>, <code>$elemMatch</code></td></tr>
  <tr><td>Sort support</td><td>Yes, on indexed prefix</td><td>Limited &mdash; can&rsquo;t sort by multikey field</td></tr>
</table>

<p><strong>Compound indexes</strong> follow the leftmost-prefix rule and the ESR rule (Equality, Sort, Range). <code>{ tenant: 1, created_at: -1 }</code> serves <code>find({ tenant: X }).sort({ created_at: -1 })</code> efficiently.</p>

<p><strong>Multikey indexes</strong> are created automatically when MongoDB encounters a document with an array value for an indexed field. They power tag-based search, friend-of-friend queries, and reverse lookups efficiently:</p>

<pre><code>// Multikey index lets these be index-backed
db.posts.find({ tags: "mongodb" })                          // any element matches
db.posts.find({ tags: { $all: ["mongodb", "tutorial"] } })  // all elements present
db.posts.find({ tags: { $in: ["mongodb", "redis"] } })      // any of these</code></pre>

<p><strong>Compound + multikey</strong>: you can combine them, but only <em>one</em> field in the compound can be an array. <code>{ tags: 1, year: 1 }</code> works; <code>{ tags: 1, categories: 1 }</code> (both arrays) is rejected.</p>

<p><strong>Watch the size explosion</strong>: a collection of 1M documents with arrays averaging 50 elements creates 50M index entries &mdash; 50x the entries of a normal index. For very large arrays, model with a separate join collection instead. Index <code>$indexStats</code> shows access counts so you can drop unused multikey indexes that are silently consuming storage.</p>
'''

ANSWERS[31] = r'''
<p>MongoDB performance monitoring stacks combine <strong>built-in introspection</strong> (the database tells you what it&rsquo;s doing) with <strong>external observability</strong> (long-term retention, dashboards, alerting).</p>

<p><strong>The built-in commands every engineer should know</strong>:</p>
<table>
  <tr><th>Command</th><th>What it shows</th></tr>
  <tr><td><code>db.serverStatus()</code></td><td>Connection counts, memory, opcounts, WiredTiger cache stats</td></tr>
  <tr><td><code>db.currentOp()</code></td><td>In-flight operations &mdash; query, lock state, runtime</td></tr>
  <tr><td><code>db.collection.stats()</code></td><td>Per-collection storage, index sizes</td></tr>
  <tr><td><code>$indexStats</code></td><td>Per-index access counts</td></tr>
  <tr><td><code>db.getProfilingStatus()</code></td><td>Slow-query profiler config</td></tr>
  <tr><td><code>rs.status()</code></td><td>Replica set health, replication lag</td></tr>
  <tr><td><code>sh.status()</code></td><td>Sharded cluster topology, balancer state</td></tr>
</table>

<p><strong>The slow-query profiler</strong>:</p>
<pre><code>// Capture all queries slower than 100 ms
db.setProfilingLevel(1, { slowms: 100, sampleRate: 1.0 })

// Inspect captured operations
db.system.profile.find().sort({ ts: -1 }).limit(10).pretty()</code></pre>

<p><strong>Production observability stack</strong>:</p>
<ul>
  <li><strong>MongoDB Atlas</strong> &mdash; built-in metrics, query insights, performance advisor, real-time dashboards. Always-on for cloud users.</li>
  <li><strong>Ops Manager / Cloud Manager</strong> &mdash; same UX for self-hosted Enterprise.</li>
  <li><strong>Percona Monitoring and Management (PMM)</strong> &mdash; open-source, Grafana-based, supports MongoDB community.</li>
  <li><strong>Datadog</strong> / <strong>New Relic</strong> / <strong>Dynatrace</strong> / <strong>SigNoz</strong> &mdash; APM with MongoDB integrations; correlate database metrics with application traces.</li>
  <li><strong>Honeycomb</strong> / <strong>OpenTelemetry</strong> &mdash; distributed tracing including MongoDB span data.</li>
  <li><strong>Prometheus + <code>mongodb_exporter</code></strong> &mdash; cheap, flexible, alert via Grafana.</li>
</ul>

<p><strong>The metrics that actually matter</strong>: replication lag (target &lt; 1s), p99 query latency, WiredTiger cache hit rate (&gt; 95%), index miss ratio, oplog window (target &gt; 24h), connection count vs limit, disk I/O saturation. Set alerts on percentile latencies, not averages &mdash; averages hide tail-latency problems.</p>
'''

ANSWERS[32] = r'''
<p>Schema design in MongoDB is fundamentally about <strong>matching the document shape to the access pattern</strong>. The mantra: <em>data that&rsquo;s read together should live together; data that grows together unbounded should be split apart</em>.</p>

<p><strong>The ten rules of MongoDB schema design</strong>:</p>
<ol>
  <li><strong>Embed for one-to-few relationships</strong> &mdash; bounded, read-together (order + line items, user + addresses).</li>
  <li><strong>Reference for one-to-many that grows unbounded</strong> &mdash; user&rsquo;s lifetime activity, sensor readings.</li>
  <li><strong>Embed summary, reference detail</strong> for hybrid &mdash; recent 10 comments embedded, full archive in a separate collection.</li>
  <li><strong>Avoid the 16 MB document limit</strong> &mdash; design so no document ever approaches it.</li>
  <li><strong>Cap arrays</strong> with <code>$slice</code> on writes for unbounded-but-mostly-recent data.</li>
  <li><strong>Pre-compute frequently read aggregates</strong> &mdash; denormalize counts, averages, last-seen timestamps.</li>
  <li><strong>Avoid massive arrays</strong> (1000+ elements) &mdash; updates rewrite the whole document and indexes balloon.</li>
  <li><strong>Use schema validation</strong> via <code>$jsonSchema</code> from day one to prevent shape drift.</li>
  <li><strong>Add a <code>schema_version</code> field</strong> for graceful evolution.</li>
  <li><strong>Index for the read path, accept write cost</strong> &mdash; the right indexes are the difference between sub-millisecond and seconds.</li>
</ol>

<p><strong>Anti-patterns to avoid</strong>:</p>
<ul>
  <li><strong>SQL-style normalization everywhere</strong> &mdash; constant <code>$lookup</code> joins are a smell that you embedded too little.</li>
  <li><strong>Massive embedded arrays</strong> that grow forever &mdash; comments on a viral post, all events for a user.</li>
  <li><strong>Schema-less freedom abuse</strong> &mdash; without validation, every document drifts and queries break.</li>
  <li><strong>Polymorphic collections</strong> with totally different shapes &mdash; users + products + orders all in one collection because &ldquo;MongoDB is flexible.&rdquo; Don&rsquo;t.</li>
</ul>

<p><strong>Tools and references</strong>: the <strong>MongoDB Schema Design</strong> patterns guide documents 12 named patterns (Bucket, Computed, Outlier, Subset, Tree, etc.) &mdash; recognizing them shortcuts good design. <strong>Hackolade</strong>, <strong>Studio 3T Schema Explorer</strong>, and Atlas&rsquo;s <strong>Schema Anti-Pattern</strong> tab automatically detect common problems.</p>
'''

ANSWERS[33] = r'''
<p>The <strong><code>$geoNear</code></strong> aggregation stage finds documents <strong>nearest to a given point</strong> and adds a <em>computed distance</em> field to each result. It must be the <strong>first stage</strong> of the pipeline and requires a <strong>2dsphere geospatial index</strong>.</p>

<pre><code>// Documents store GeoJSON points
// { name: "Cafe", location: { type: "Point", coordinates: [77.5946, 12.9716] } }

// Required index
db.places.createIndex({ location: "2dsphere" })

// Find nearest 10 places, with distance in meters
db.places.aggregate([
  { $geoNear: {
      near: { type: "Point", coordinates: [77.5946, 12.9716] },
      distanceField: "distance_m",
      maxDistance: 5000,         // meters
      spherical: true,
      query: { category: "cafe" }   // pre-filter on other fields
  }},
  { $limit: 10 }
])

// Output adds distance_m to each result
// [
//   { name: "Indiranagar Cafe", location: {...}, distance_m: 124.3 },
//   { name: "Coffee Day", location: {...}, distance_m: 287.5 },
//   ...
// ]</code></pre>

<p><strong>Key parameters</strong>:</p>
<table>
  <tr><th>Parameter</th><th>Purpose</th></tr>
  <tr><td><code>near</code></td><td>The reference point (GeoJSON or legacy coords)</td></tr>
  <tr><td><code>distanceField</code></td><td>Required &mdash; output field name for the computed distance</td></tr>
  <tr><td><code>maxDistance</code> / <code>minDistance</code></td><td>Range bounds in meters (spherical) or units (planar)</td></tr>
  <tr><td><code>spherical</code></td><td>Use Earth&rsquo;s curvature (always <code>true</code> for 2dsphere)</td></tr>
  <tr><td><code>query</code></td><td>Pre-filter &mdash; equivalent to a <code>$match</code> stage but more efficient</td></tr>
  <tr><td><code>distanceMultiplier</code></td><td>Convert meters to other units (e.g., <code>0.001</code> for km)</td></tr>
</table>

<p><strong><code>$geoNear</code> vs <code>$near</code></strong>: <code>$near</code> is a query operator usable in <code>find()</code>; it sorts by distance but doesn&rsquo;t expose the distance value. <code>$geoNear</code> is the pipeline equivalent and exposes the distance, enabling tiered displays (&ldquo;within 1km / 5km / 10km&rdquo; categories).</p>

<p>Coordinates are always <code>[longitude, latitude]</code> &mdash; the most common gotcha. For huge geo workloads (millions of points, complex queries, isochrones), <strong>PostGIS</strong>, <strong>Tile38</strong>, or <strong>H3</strong> hex-indexing typically outperform MongoDB. For occasional &ldquo;find nearby&rdquo;, the native operators are excellent.</p>
'''

ANSWERS[34] = r'''
<p>The <strong>journal</strong> is MongoDB&rsquo;s write-ahead log. Every write is appended to the journal on disk before it&rsquo;s applied to the data files; on crash, MongoDB replays the journal at startup to recover any writes that hadn&rsquo;t made it to the data files yet. This is what makes MongoDB durable across power loss and process crashes.</p>

<p><strong>The mechanics</strong>:</p>
<ol>
  <li>Write arrives at the primary.</li>
  <li>Write is applied to the in-memory copy.</li>
  <li>Journal entry is appended to the journal buffer.</li>
  <li>By default, the journal is fsynced to disk every <strong>100ms</strong> (or every commit if <code>j: true</code>).</li>
  <li>Periodically (every 60 seconds), a checkpoint flushes dirty data pages to disk and truncates the journal up to that point.</li>
  <li>On crash recovery, MongoDB replays journal entries since the last checkpoint &mdash; bringing the data files back to a consistent state.</li>
</ol>

<p><strong>The <code>j: true</code> write concern</strong> changes step 4: instead of waiting for the next 100ms tick, the write blocks until its journal entry has been fsynced. This is the strongest single-node durability guarantee.</p>

<table>
  <tr><th>Setting</th><th>Default</th><th>Purpose</th></tr>
  <tr><td><code>storage.journal.commitIntervalMs</code></td><td>100</td><td>How often the journal is fsynced</td></tr>
  <tr><td>Checkpoint interval</td><td>60 sec</td><td>How often dirty pages flush to disk</td></tr>
  <tr><td><code>writeConcern: { j: true }</code></td><td>Off</td><td>Force fsync per-write</td></tr>
</table>

<p><strong>Performance implications</strong>:</p>
<ul>
  <li><strong>Journal fsync is a hot path</strong> &mdash; faster disks (NVMe) directly improve write latency.</li>
  <li><strong><code>j: true</code> trades throughput for durability</strong> &mdash; expect 5-10x latency increase on the affected writes.</li>
  <li><strong>Atlas defaults are fine</strong> &mdash; tuned for production durability without manual intervention.</li>
  <li><strong>Compression options</strong> for the journal: <code>none</code> (fastest, default in modern versions), <code>snappy</code>, <code>zstd</code>.</li>
</ul>

<p>Compared to MySQL&rsquo;s redo log or PostgreSQL&rsquo;s WAL, MongoDB&rsquo;s journal serves the same role: durability without paying for disk fsync on every write. Together with replication&rsquo;s <code>w: "majority"</code>, you get full ACID-like guarantees against both single-node and cluster-level failures.</p>
'''

ANSWERS[35] = r'''
<p><strong>Replication lag</strong> &mdash; the gap between when a primary acknowledges a write and when secondaries apply it &mdash; is the most common operational issue in busy MongoDB deployments. Healthy lag is sub-second; persistent lag of seconds or minutes signals a real problem.</p>

<p><strong>Diagnose the cause</strong>:</p>
<pre><code>// Replication state of every member
rs.printSecondaryReplicationInfo()
// Or detail
rs.status().members.forEach(m =&gt; print(m.name, m.stateStr, m.optimeDate))
// Look at "replicationLag" metric in Atlas / Ops Manager dashboards</code></pre>

<table>
  <tr><th>Cause</th><th>Symptom</th><th>Fix</th></tr>
  <tr><td>Slow secondary disks</td><td>Steady lag growing under write load</td><td>Match secondary hardware to primary</td></tr>
  <tr><td>Network bottleneck</td><td>Lag correlates with WAN saturation</td><td>Same-region replicas, increase bandwidth</td></tr>
  <tr><td>Long-running ops on secondary</td><td>Spikes during analytics queries</td><td>Use a dedicated analytics node</td></tr>
  <tr><td>Index builds</td><td>Lag during DDL operations</td><td>Rolling builds, off-peak windows</td></tr>
  <tr><td>Massive single-doc writes</td><td>Bulk inserts, large array <code>$push</code></td><td>Batch in chunks, cap arrays</td></tr>
  <tr><td>Replica too far behind oplog</td><td>State <code>RECOVERING</code> or <code>STARTUP2</code></td><td>Initial sync from scratch</td></tr>
</table>

<p><strong>Mitigation strategies</strong>:</p>
<ul>
  <li><strong>Use <code>w: "majority"</code></strong> for important writes &mdash; the primary won&rsquo;t outrun replicas because it waits for them.</li>
  <li><strong>Identical hardware</strong> for all data-bearing replica members.</li>
  <li><strong>Same AZ/region</strong> for replicas where compliance allows &mdash; cross-region adds 50-200ms baseline lag.</li>
  <li><strong>Hidden secondary for heavy reads</strong> &mdash; <code>{ priority: 0, hidden: true }</code> keeps it off the rotation while still receiving oplog.</li>
  <li><strong>Increase oplog size</strong> &mdash; if a secondary falls behind the oplog window, it needs initial sync. <code>db.adminCommand({ replSetResizeOplog: 1, size: 32768 })</code>.</li>
  <li><strong>Throttle writes</strong> at the application layer when lag exceeds a threshold &mdash; backpressure on bulk imports.</li>
</ul>

<p><strong>Atlas</strong> alerts on replication lag automatically and surfaces it in dashboards. For self-hosted, set Prometheus alerts on the <code>mongodb_mongod_replset_member_replication_lag_seconds</code> metric.</p>
'''

ANSWERS[36] = r'''
<p>An aggregation pipeline is a sequence of <strong>stages</strong>, each transforming the document stream and feeding the next. Performance is a function of <em>stage selection</em>, <em>stage order</em>, and <em>which stages can use indexes</em>.</p>

<p><strong>Stage categories and their impact</strong>:</p>
<table>
  <tr><th>Category</th><th>Stages</th><th>Performance characteristic</th></tr>
  <tr><td>Filter</td><td><code>$match</code></td><td>Uses indexes when first; fastest stage to apply</td></tr>
  <tr><td>Reshape</td><td><code>$project</code>, <code>$addFields</code>, <code>$set</code>, <code>$unset</code></td><td>Cheap; reduces document size for downstream</td></tr>
  <tr><td>Order</td><td><code>$sort</code>, <code>$limit</code>, <code>$skip</code></td><td>Index-backed when after only <code>$match</code>; otherwise in-memory (100MB cap)</td></tr>
  <tr><td>Group</td><td><code>$group</code>, <code>$bucket</code>, <code>$bucketAuto</code>, <code>$sortByCount</code></td><td>Memory-bound; spills to disk with <code>allowDiskUse</code></td></tr>
  <tr><td>Join</td><td><code>$lookup</code>, <code>$graphLookup</code>, <code>$unionWith</code></td><td>Index foreign field; can be very expensive</td></tr>
  <tr><td>Restructure</td><td><code>$unwind</code>, <code>$replaceRoot</code>, <code>$facet</code></td><td><code>$unwind</code> can multiply document count</td></tr>
  <tr><td>Window</td><td><code>$setWindowFields</code></td><td>SQL window functions; in-memory per partition</td></tr>
  <tr><td>Output</td><td><code>$out</code>, <code>$merge</code></td><td>Always last; writes to a target collection</td></tr>
</table>

<p><strong>The optimization rules that matter</strong>:</p>
<ol>
  <li><strong><code>$match</code> first</strong> &mdash; only the leading filter can use indexes. Multiple <code>$match</code>es are merged automatically.</li>
  <li><strong><code>$project</code> early</strong> &mdash; drop fields you won&rsquo;t need; smaller documents flow faster.</li>
  <li><strong><code>$sort + $limit</code></strong> together get the &ldquo;top-K&rdquo; optimization &mdash; MongoDB only tracks N candidates during the sort.</li>
  <li><strong><code>$lookup</code> needs an index</strong> on the foreign field, or it scans for every input.</li>
  <li><strong><code>$unwind</code> last when possible</strong> &mdash; it multiplies documents.</li>
  <li><strong>Use <code>{ allowDiskUse: true }</code></strong> when memory limits are hit; better than failing.</li>
</ol>

<p><strong>Verify with <code>.explain("executionStats")</code></strong> on the aggregate &mdash; <code>queryPlanner.winningPlan</code> shows whether the <code>$match</code> hit an index, <code>executionStats.executionTimeMillis</code> shows the actual cost. The <strong>Atlas Performance Advisor</strong> automatically flags pipelines that scan more documents than they return.</p>
'''

ANSWERS[37] = r'''
<p>MongoDB authentication is layered: a <strong>mechanism</strong> defines how credentials are exchanged; a <strong>user store</strong> holds the credentials. Modern deployments use SCRAM by default and add x.509 or LDAP/Kerberos on top for enterprise needs.</p>

<table>
  <tr><th>Mechanism</th><th>Description</th><th>Typical use</th></tr>
  <tr><td><strong>SCRAM-SHA-256</strong></td><td>Password-based, salted, default since 4.0</td><td>Standard application users</td></tr>
  <tr><td><strong>x.509</strong></td><td>Mutual TLS with client certificates</td><td>Service-to-service, microservices</td></tr>
  <tr><td><strong>LDAP</strong> (Enterprise / Atlas)</td><td>Delegate to corporate directory</td><td>Centralized employee access</td></tr>
  <tr><td><strong>Kerberos</strong> (Enterprise)</td><td>SPNEGO/GSSAPI</td><td>Windows AD environments</td></tr>
  <tr><td><strong>AWS IAM</strong> (Atlas)</td><td>Federated AWS identity</td><td>EC2/ECS/EKS workloads</td></tr>
  <tr><td><strong>OIDC</strong> (Atlas, 7.0+)</td><td>OpenID Connect</td><td>Modern SSO &mdash; Okta, Auth0, WorkOS</td></tr>
</table>

<pre><code>// Enable auth on self-hosted
mongod --auth --bind_ip 0.0.0.0

// Create the bootstrap admin user (first thing on a fresh deployment)
use admin
db.createUser({
  user: "admin",
  pwd:  passwordPrompt(),
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})

// Connect with creds + TLS
mongosh "mongodb://admin:pass@host:27017/admin?tls=true&amp;tlsCAFile=/etc/ssl/ca.pem"

// x.509 certificate auth
mongosh --tls \
        --tlsCertificateKeyFile /etc/ssl/client.pem \
        --tlsCAFile /etc/ssl/ca.pem \
        --authenticationMechanism MONGODB-X509 \
        --authenticationDatabase '$external'</code></pre>

<p><strong>Operational best practices</strong>:</p>
<ul>
  <li><strong>Always enable auth in production</strong> &mdash; <code>--auth</code> is not the default on bare <code>mongod</code>.</li>
  <li><strong>Pair with TLS</strong> &mdash; SCRAM over plaintext network is exposed to MITM.</li>
  <li><strong>Rotate credentials</strong> via <strong>HashiCorp Vault</strong>, <strong>AWS Secrets Manager</strong>, or <strong>Doppler</strong> &mdash; never check passwords into source control.</li>
  <li><strong>Use IAM/OIDC where supported</strong> &mdash; eliminates static secrets entirely. Atlas Database Users API enables fully programmatic credential lifecycle.</li>
  <li><strong>Audit login events</strong> &mdash; Enterprise/Atlas provides audit logs streamed to S3, Splunk, or SIEM tools.</li>
</ul>

<p>For modern apps, the <strong>OIDC + Atlas</strong> combination is the gold standard &mdash; users log into the app via Okta/Auth0/WorkOS, and the same identity carries through to MongoDB without any password exchange.</p>
'''

ANSWERS[38] = r'''
<p>The <strong><code>$sample</code></strong> aggregation stage <strong>randomly selects N documents</strong> from the input. It&rsquo;s the &ldquo;random sample&rdquo; primitive &mdash; useful for testing pipelines on representative data, randomly picking winners from a contest, or generating training data subsets.</p>

<pre><code>// Random 100 documents from the entire collection
db.users.aggregate([{ $sample: { size: 100 } }])

// Sample within a filter
db.users.aggregate([
  { $match: { country: "IN", active: true } },
  { $sample: { size: 50 } }
])

// Stratified sampling: N per group
db.users.aggregate([
  { $group: { _id: "$country", users: { $push: "$$ROOT" } } },
  { $project: {
      sample: { $slice: [{ $shuffle: "$users" }, 10] }
  }},
  { $unwind: "$sample" },
  { $replaceRoot: { newRoot: "$sample" } }
])</code></pre>

<p><strong>How it works internally</strong>:</p>
<ul>
  <li><strong>If <code>size &lt; 5%</code> of the collection</strong> AND <code>$sample</code> is the <em>first stage</em>, MongoDB uses a fast random-cursor strategy reading directly from storage.</li>
  <li><strong>Otherwise</strong>, it scans all candidates upstream of <code>$sample</code> and uses a reservoir-sampling algorithm in memory.</li>
  <li><strong>Sampling is uniformly random</strong> &mdash; each document has equal probability of selection.</li>
</ul>

<p><strong>Comparison vs alternatives</strong>:</p>
<table>
  <tr><th>Need</th><th>Best tool</th></tr>
  <tr><td>Truly random N from a collection</td><td><code>$sample</code></td></tr>
  <tr><td>Deterministic 1% sample (reproducible)</td><td><code>$expr</code> with <code>$mod</code> on a hash of <code>_id</code></td></tr>
  <tr><td>First N for &ldquo;preview&rdquo;</td><td><code>find().limit(N)</code> &mdash; not random but fast</td></tr>
  <tr><td>Sampled streaming reads</td><td>Reservoir sampling client-side over a cursor</td></tr>
</table>

<p><strong>Production uses</strong>: A/B test cohort assignment (when paired with deterministic hashing), generating training/test splits for ML pipelines, exporting representative datasets for staging environments, and randomized monitoring (sample 0.1% of requests for deep tracing). For huge collections, <code>$sample</code> with a small size is much faster than alternatives that scan everything.</p>
'''

ANSWERS[39] = r'''
<p>A <strong>hybrid SQL + MongoDB architecture</strong> is the modern norm &mdash; not a fallback. Each database does what it&rsquo;s best at: SQL for highly relational, integrity-critical, transactional data; MongoDB for flexible, hierarchical, evolving, or high-volume data.</p>

<p><strong>Where the line typically falls</strong>:</p>
<table>
  <tr><th>Use case</th><th>SQL (Postgres/MySQL)</th><th>MongoDB</th></tr>
  <tr><td>Financial transactions, billing</td><td>✓</td><td></td></tr>
  <tr><td>User identity, auth</td><td>✓</td><td></td></tr>
  <tr><td>Order management with strict integrity</td><td>✓</td><td></td></tr>
  <tr><td>Product catalog (varying attributes)</td><td></td><td>✓</td></tr>
  <tr><td>User-generated content (posts, comments)</td><td></td><td>✓</td></tr>
  <tr><td>Event/analytics streams</td><td></td><td>✓ (or warehouse)</td></tr>
  <tr><td>Search index</td><td></td><td>✓ (Atlas Search) or <strong>Elasticsearch</strong></td></tr>
  <tr><td>Time-series, IoT</td><td></td><td>✓ (time-series collections)</td></tr>
</table>

<p><strong>Architectural patterns</strong>:</p>
<ul>
  <li><strong>Polyglot persistence</strong> &mdash; each microservice owns its database choice. Avoid cross-service joins.</li>
  <li><strong>CDC pipelines</strong> &mdash; <strong>Debezium</strong> streams changes from one database into another. Postgres &rarr; Kafka &rarr; MongoDB for materialized read views, or vice versa.</li>
  <li><strong>Outbox pattern</strong> &mdash; transactional outbox in SQL, async event consumer writes to MongoDB, ensuring eventual consistency without distributed transactions.</li>
  <li><strong>Event sourcing</strong> &mdash; events in MongoDB or Kafka; projections to either SQL (for transactional reads) or MongoDB (for flexible read views).</li>
</ul>

<p><strong>Modern toolchain</strong>: <strong>Airbyte</strong>, <strong>Fivetran</strong>, <strong>Estuary</strong>, <strong>Stitch</strong> for batch ETL between systems; <strong>Debezium</strong>, <strong>Striim</strong>, <strong>Materialize</strong>, <strong>RisingWave</strong> for real-time CDC; <strong>Hightouch</strong>, <strong>Census</strong>, <strong>Polytomic</strong> for reverse-ETL pushing data <em>back</em> to operational systems. ORMs like <strong>Prisma</strong> support both SQL and MongoDB with the same API, easing developer experience across the boundary.</p>

<p>The pragmatic rule: pick the database that matches the dominant access pattern of each domain, then plan the synchronization layer between them deliberately.</p>
'''

ANSWERS[40] = r'''
<p>MongoDB&rsquo;s <strong><code>$jsonSchema</code></strong> validator brings <strong>JSON Schema-style validation</strong> to documents at insert and update time. It&rsquo;s the modern way to enforce shape constraints in a flexible-schema database without giving up the flexibility entirely.</p>

<pre><code>db.createCollection("orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["customer_id", "total", "status", "created_at"],
      properties: {
        customer_id:   { bsonType: "objectId" },
        total: {
          bsonType: "double",
          minimum:  0,
          description: "must be a non-negative number"
        },
        status: {
          enum: ["pending", "paid", "shipped", "cancelled"],
          description: "must be one of the allowed values"
        },
        created_at: { bsonType: "date" },
        line_items: {
          bsonType: "array",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["sku", "qty", "price"],
            properties: {
              sku:   { bsonType: "string" },
              qty:   { bsonType: "int", minimum: 1 },
              price: { bsonType: "double", minimum: 0 }
            }
          }
        }
      }
    }
  },
  validationAction: "error",     // reject invalid (use "warn" for soft rollout)
  validationLevel:  "strict"     // apply to inserts AND updates
})

// Add validation to an existing collection
db.runCommand({
  collMod: "orders",
  validator: { $jsonSchema: { /* ... */ } },
  validationAction: "error"
})</code></pre>

<p><strong>Modes and rollout</strong>:</p>
<table>
  <tr><th>Setting</th><th>Effect</th></tr>
  <tr><td><code>validationAction: "error"</code></td><td>Reject violating writes (default)</td></tr>
  <tr><td><code>validationAction: "warn"</code></td><td>Log to mongod log, allow the write &mdash; rollout safety net</td></tr>
  <tr><td><code>validationLevel: "strict"</code></td><td>All writes validated</td></tr>
  <tr><td><code>validationLevel: "moderate"</code></td><td>Only updates to docs that already match the schema validate</td></tr>
</table>

<p><strong>Production rollout pattern</strong>:</p>
<ol>
  <li>Deploy with <code>validationAction: "warn"</code>. Monitor logs for violations.</li>
  <li>Backfill non-conforming documents through a migration.</li>
  <li>Switch to <code>validationAction: "error"</code>.</li>
</ol>

<p>For application-side validation, libraries like <strong>Zod</strong>, <strong>Yup</strong>, <strong>Joi</strong>, <strong>Valibot</strong>, <strong>Pydantic</strong>, <strong>Mongoose schemas</strong>, or <strong>Prisma</strong>&rsquo;s schema can validate before the request even hits MongoDB &mdash; provides better error messages and earlier feedback. Use both layers: app-side for UX, database-side as the absolute backstop.</p>
'''

ANSWERS[41] = r'''
<p><strong>Atlas Data Lake</strong> (now part of <strong>Atlas Data Federation</strong>) lets you query data stored in <strong>Amazon S3</strong>, <strong>Azure Blob Storage</strong>, or <strong>HTTPS endpoints</strong> using the standard MongoDB Query Language and aggregation pipelines &mdash; without loading it into a cluster first.</p>

<p><strong>How it works</strong>: you create a <strong>Federated Database Instance</strong> mapping S3 prefixes to virtual collections. Queries from any MongoDB driver hit the federation endpoint, which translates them into S3 reads with predicate pushdown, file-format awareness (BSON, JSON, Parquet, CSV, Avro, ORC), and partitioned scans.</p>

<pre><code>// Configuration (Atlas UI or admin API): map an S3 prefix to a collection
{
  "stores": [{
    "name":       "myDataStore",
    "provider":   "s3",
    "region":     "us-east-1",
    "bucket":     "my-archived-data"
  }],
  "databases": [{
    "name": "archive",
    "collections": [{
      "name": "events_2024",
      "dataSources": [{
        "storeName": "myDataStore",
        "path":      "events/2024/{year:int}-{month:int}/*.parquet"
      }]
    }]
  }]
}

// Query like any MongoDB collection
db.events_2024.aggregate([
  { $match: { event_type: "purchase" } },
  { $group: { _id: "$product_id", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } },
  { $limit: 10 }
])</code></pre>

<p><strong>Use cases</strong>:</p>
<ul>
  <li><strong>Cold-data archive</strong> &mdash; old documents pushed from a hot cluster to S3 via <strong>Online Archive</strong>; queryable transparently.</li>
  <li><strong>Cross-cluster analytics</strong> &mdash; combine data from multiple Atlas clusters with S3 in a single aggregation.</li>
  <li><strong>Data lake on a budget</strong> &mdash; query Parquet files in S3 without ETL into a warehouse.</li>
  <li><strong>Federated read API</strong> &mdash; expose S3-backed datasets through a familiar MongoDB interface.</li>
</ul>

<p><strong>Limits</strong>: read-only (no writes back to S3 except via <code>$out</code>); query latency higher than native cluster reads; complex pipelines may be slower than dedicated warehouse engines (<strong>BigQuery</strong>, <strong>Snowflake</strong>, <strong>Athena</strong>, <strong>Trino</strong>, <strong>Databricks</strong>, <strong>ClickHouse</strong>) on huge datasets. The right fit is when most of your queries are operational and you have a long tail of cold history that&rsquo;s occasionally accessed.</p>
'''

ANSWERS[42] = r'''
<p>MongoDB triggers are typically implemented with <strong>change streams</strong> + a <strong>serverless function runtime</strong>. The change stream provides the event source; the function runs custom logic on each event. <strong>Atlas Triggers</strong> packages this as a managed service.</p>

<p><strong>Atlas Triggers (managed)</strong>:</p>
<pre><code>// Atlas UI / admin API: define a trigger
{
  "name":          "OnOrderPaid",
  "type":          "DATABASE",
  "config": {
    "operation_types": ["UPDATE"],
    "match": { "fullDocument.status": "paid" },
    "database":   "shop",
    "collection": "orders",
    "service_name": "mongodb-atlas",
    "full_document": true
  },
  "function_name": "handleOrderPaid"   // Atlas Function (TypeScript / JS)
}

// Function code
exports = async function(changeEvent) {
  const order = changeEvent.fullDocument
  // Send confirmation email, update analytics, fire webhooks
  await context.functions.execute("sendEmail", order.customer_id, order)
  await context.services.get("analytics").addToSet({ event: "purchase", order })
}</code></pre>

<p><strong>Self-hosted equivalent</strong>:</p>
<pre><code>// Worker process tailing change stream, dispatching to handlers
const stream = db.collection("orders").watch([
  { $match: { operationType: "update", "fullDocument.status": "paid" } }
], { fullDocument: "updateLookup" })

for await (const change of stream) {
  await sendToQueue("order-paid", change.fullDocument)
  // Persist resume token after successful enqueue
  await db.collection("_consumer_state").updateOne(
    { _id: "order-paid-worker" },
    { $set: { resume_token: change._id, ts: new Date() } }
  )
}

// Recover after crash with resumeAfter
const stream = db.collection("orders").watch([], { resumeAfter: lastToken })</code></pre>

<p><strong>Architectural patterns</strong>:</p>
<ul>
  <li><strong>Trigger &rarr; queue</strong> &mdash; change stream worker pushes to <strong>Kafka</strong>, <strong>SQS</strong>, <strong>BullMQ</strong>, <strong>Inngest</strong>, <strong>Trigger.dev</strong>, <strong>Temporal</strong>, or <strong>Hatchet</strong> for retries and visibility.</li>
  <li><strong>Trigger &rarr; serverless</strong> &mdash; Atlas Functions, AWS Lambda via EventBridge Pipes, Cloudflare Workers Queues.</li>
  <li><strong>Cache invalidation</strong> &mdash; flip Redis keys on every relevant change.</li>
  <li><strong>Search index sync</strong> &mdash; mirror writes into <strong>Elasticsearch</strong>, <strong>Meilisearch</strong>, <strong>Typesense</strong>, or <strong>Atlas Search</strong>.</li>
  <li><strong>Outbox pattern</strong> &mdash; for reliable cross-service events, write to an outbox collection in the same transaction as the business write; trigger ships outbox entries to Kafka.</li>
</ul>

<p><strong>Critical operational concerns</strong>: persist the resume token after each successful processing; handle exactly-once semantics at the consumer (idempotent handlers, deduplication keys); monitor consumer lag against the oplog window. <strong>Debezium for MongoDB</strong> is the production-grade alternative for high-volume CDC into Kafka.</p>
'''

ANSWERS[43] = r'''
<p>The <strong><code>$facet</code></strong> stage runs <strong>multiple sub-pipelines in parallel</strong> on the same input documents, returning their results as named arrays in a single output document. It&rsquo;s the cleanest way to compute &ldquo;everything for a dashboard&rdquo; in one round trip.</p>

<pre><code>// E-commerce category page: products + filter facets + price stats, one query
db.products.aggregate([
  { $match: { category: "electronics", in_stock: true } },
  { $facet: {
      products: [
        { $sort: { popularity: -1 } },
        { $skip: 0 },
        { $limit: 24 },
        { $project: { name: 1, price: 1, image: 1, rating: 1 } }
      ],
      facets_brand: [
        { $group: { _id: "$brand", count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 10 }
      ],
      facets_price: [
        { $bucket: {
            groupBy: "$price",
            boundaries: [0, 100, 500, 1000, 5000],
            default: "5000+",
            output: { count: { $sum: 1 } }
        }}
      ],
      stats: [
        { $group: { _id: null, total: { $sum: 1 }, avg_price: { $avg: "$price" } } }
      ]
  }}
])

// Result document:
// {
//   products:        [...24 products],
//   facets_brand:    [{_id:"Sony", count:42}, ...],
//   facets_price:    [{_id:0, count:120}, {_id:100, count:88}, ...],
//   stats:           [{_id:null, total:1245, avg_price:328.50}]
// }</code></pre>

<p><strong>Why <code>$facet</code> matters</strong>:</p>
<ul>
  <li><strong>One round trip</strong> instead of 4-5 separate queries &mdash; latency win on any UI that surfaces multiple summaries.</li>
  <li><strong>Same input</strong> &mdash; every sub-pipeline starts from the same filtered set, ensuring consistency between counts and listings.</li>
  <li><strong>Composable</strong> &mdash; each sub-pipeline is just an aggregation pipeline of its own.</li>
</ul>

<p><strong>Performance considerations</strong>:</p>
<ul>
  <li>Pre-filter with <code>$match</code> <em>before</em> <code>$facet</code> &mdash; the filter applies once, all sub-pipelines benefit.</li>
  <li>Each sub-pipeline counts against the in-memory limit (100MB) independently &mdash; use <code>{ allowDiskUse: true }</code> for big aggregations.</li>
  <li>Don&rsquo;t use <code>$facet</code> as a write side-channel; the output is a single document.</li>
  <li>For <strong>massive faceted search at scale</strong>, <strong>MongoDB Atlas Search</strong>&rsquo;s <code>facet</code> operator (Lucene-backed) is faster and more powerful than aggregation <code>$facet</code>.</li>
</ul>

<p>For e-commerce category pages, search results, or dashboards, <code>$facet</code> reduces both database load and API complexity dramatically.</p>
'''

ANSWERS[44] = r'''
<p>Migrating from a relational database to MongoDB is a <strong>schema-design exercise first</strong>, a data-movement exercise second. Lifting a normalized SQL schema into MongoDB unchanged is the most common failure mode &mdash; you end up with the worst of both worlds (rigid, JOIN-heavy MongoDB).</p>

<p><strong>The phases</strong>:</p>
<ol>
  <li><strong>Analyze access patterns</strong> &mdash; what queries does the app run? What gets read together? What changes together? This determines the document shape, not the original SQL schema.</li>
  <li><strong>Redesign for MongoDB</strong> &mdash; embed one-to-few relationships, denormalize for read efficiency, choose IDs carefully (UUIDv7 / ULID for time-ordered global uniqueness; ObjectId for MongoDB-native).</li>
  <li><strong>Build the migration pipeline</strong> &mdash; ETL or CDC, depending on whether you need a one-time cutover or live dual-writes.</li>
  <li><strong>Run dual-write phase</strong> &mdash; new code writes to both databases; reads gradually shift to MongoDB once it&rsquo;s caught up.</li>
  <li><strong>Cut over</strong> &mdash; feature-flag the switch; keep SQL writeable for a rollback window.</li>
  <li><strong>Decommission SQL</strong>.</li>
</ol>

<p><strong>Tooling for the data movement</strong>:</p>
<table>
  <tr><th>Approach</th><th>Use case</th></tr>
  <tr><td><strong>Relational Migrator</strong> (MongoDB-official)</td><td>Schema mapping + sync, Postgres/MySQL/Oracle/SQL Server</td></tr>
  <tr><td><strong>Airbyte</strong> / <strong>Fivetran</strong> / <strong>Estuary</strong></td><td>Generic data integration with SQL-to-MongoDB connectors</td></tr>
  <tr><td><strong>Debezium</strong> + Kafka + Mongo sink</td><td>Real-time CDC for live cutover</td></tr>
  <tr><td><strong>Custom ETL</strong> (Python / Node)</td><td>One-off migrations with complex transformations</td></tr>
</table>

<p><strong>Common modeling translations</strong>:</p>
<ul>
  <li>SQL <code>users</code> + <code>addresses</code> (one-to-few) &rarr; <code>users.addresses</code> embedded array.</li>
  <li>SQL <code>orders</code> + <code>order_items</code> (bounded) &rarr; <code>orders.line_items</code> embedded.</li>
  <li>SQL <code>orders</code> + <code>customers</code> (many-to-one) &rarr; reference, optionally with cached <code>customer_name</code> denormalized into the order at write time.</li>
  <li>SQL <code>posts</code> + <code>comments</code> (unbounded) &rarr; separate <code>comments</code> collection with <code>post_id</code>; embed only the recent 5 in the post for the listing view.</li>
  <li>SQL many-to-many through join tables &rarr; arrays of references (<code>{ user_id, group_ids: [...] }</code>) plus a multikey index.</li>
</ul>

<p><strong>Validation step</strong>: run the same business queries against both systems during dual-write and compare counts/sums. Discrepancies usually mean schema mismatches; fix in the MongoDB shape before cutover.</p>
'''

ANSWERS[45] = r'''
<p>MongoDB <strong>zones</strong> (formerly &ldquo;tag-aware sharding&rdquo;) let you control <em>which shard holds which data</em> based on the shard-key value &mdash; the foundation for geo-distributed deployments, tiered storage, and data residency compliance.</p>

<pre><code>// Tag shards with logical zones
sh.addShardTag("shardA", "EU")
sh.addShardTag("shardB", "EU")
sh.addShardTag("shardC", "US")
sh.addShardTag("shardD", "US")

// Map shard-key ranges to zones
// EU users (region prefix "eu_") go to EU shards
sh.addTagRange(
  "shopdb.users",
  { region: "eu_", _id: MinKey },
  { region: "eu_~", _id: MaxKey },   // ~ sorts after letters
  "EU"
)

// US users go to US shards
sh.addTagRange(
  "shopdb.users",
  { region: "us_", _id: MinKey },
  { region: "us_~", _id: MaxKey },
  "US"
)

// Cluster balancer enforces these ranges automatically</code></pre>

<p><strong>Real-world uses</strong>:</p>
<table>
  <tr><th>Use case</th><th>Zone configuration</th></tr>
  <tr><td><strong>Geo-residency</strong> (GDPR, data sovereignty)</td><td>Each region&rsquo;s shards in its own zone; shard key prefixed by region</td></tr>
  <tr><td><strong>Latency optimization</strong></td><td>User data lives near the user; reads route to local zone</td></tr>
  <tr><td><strong>Hot/cold storage tiering</strong></td><td>Recent data in &ldquo;hot&rdquo; zone (NVMe), old in &ldquo;cold&rdquo; zone (cheap disk)</td></tr>
  <tr><td><strong>Customer isolation</strong></td><td>Premium tenants on dedicated shards; isolation guarantees</td></tr>
</table>

<p><strong>Atlas Global Clusters</strong> wraps zones in a UI: pick the regions you want, pick a shard key with a region prefix, and Atlas configures the zones, shard tags, and cross-region replication automatically. Read preferences with <code>readPreference: nearest</code> route reads to the local replica, achieving sub-100ms latency globally.</p>

<p><strong>Operational considerations</strong>:</p>
<ul>
  <li>Shard key must include the zoning field (the <code>region</code> in the example) &mdash; can&rsquo;t add zones to an existing collection without resharding.</li>
  <li>Migrations to comply with zones happen via the balancer in the background &mdash; can take hours on large collections.</li>
  <li>Zones are advisory in non-Atlas deployments &mdash; they don&rsquo;t prevent writes to wrong shards if the application bypasses <code>mongos</code>.</li>
</ul>

<p>For multi-region apps with strict residency requirements, zones + Atlas Global Clusters are the canonical solution &mdash; replacing far more complex DIY architectures.</p>
'''

ANSWERS[46] = r'''
<p>Index builds on a busy collection can take hours and historically blocked writes. Modern MongoDB makes most index builds <strong>online by default</strong>, but the cost is real and there are still rules to follow on production systems.</p>

<p><strong>How modern index builds work (4.4+)</strong>:</p>
<ol>
  <li>Build runs as a foreground operation, but <strong>doesn&rsquo;t block writes</strong> on the primary. New writes are tracked in a side buffer and applied at the end.</li>
  <li>On replica sets, the build replicates as an oplog entry; secondaries build their own copies in parallel.</li>
  <li>The collection&rsquo;s data files are not locked except during a brief commit phase at the end.</li>
  <li>The index is added to the collection metadata atomically when complete.</li>
</ol>

<pre><code>// Standard index build &mdash; non-blocking by default
db.orders.createIndex({ customer_id: 1, created_at: -1 })

// Monitor progress
db.currentOp({ "command.createIndexes": { $exists: true } })

// Or use db.serverStatus() metrics
db.serverStatus().metrics.commands.createIndexes

// Old commitQuorum control (5.0+)
db.runCommand({
  createIndexes: "orders",
  indexes: [{ key: { customer_id: 1 }, name: "cust_idx" }],
  commitQuorum: "majority"   // wait for majority before commit
})</code></pre>

<p><strong>Best practices for production builds</strong>:</p>
<table>
  <tr><th>Strategy</th><th>When to use</th></tr>
  <tr><td><strong>Off-peak windows</strong></td><td>Always &mdash; build cost still impacts CPU and disk</td></tr>
  <tr><td><strong>Rolling builds</strong> (build on hidden secondary, fail over, repeat)</td><td>Self-hosted, want zero impact on primary</td></tr>
  <tr><td><strong>Atlas online indexing</strong></td><td>UI-managed, automatic rolling on secondaries first</td></tr>
  <tr><td><strong><code>commitQuorum</code></strong></td><td>Ensure majority confirms before commit</td></tr>
  <tr><td><strong>Pre-warm new indexes</strong></td><td>Run targeted queries to load index into cache before traffic</td></tr>
</table>

<p><strong>Watch the side effects</strong>:</p>
<ul>
  <li><strong>Replica lag</strong> spikes during the build &mdash; monitor and have a rollback plan.</li>
  <li><strong>WiredTiger cache pressure</strong> &mdash; the build reads the entire collection. Cold data gets pulled into cache, evicting hot data.</li>
  <li><strong>Disk usage</strong> doubles temporarily &mdash; both the index and its build buffer occupy space.</li>
  <li><strong>Index build limit</strong> &mdash; only one foreground build per collection at a time.</li>
</ul>

<p><strong>Atlas Performance Advisor</strong> recommends indexes based on actual workload; combine with the <strong>Index Suggestions</strong> view for safe, prioritized rollouts. Always test on staging or a hidden secondary first.</p>
'''

ANSWERS[47] = r'''
<p>The <strong><code>$merge</code></strong> stage writes pipeline output to a target collection &mdash; with smart upsert semantics. Unlike <code>$out</code> (which fully replaces the target), <code>$merge</code> can <strong>insert, update, replace, or skip</strong> matching documents based on a key. It&rsquo;s the proper ETL primitive in modern MongoDB.</p>

<pre><code>// Daily revenue rollup, merged into a summary collection
db.orders.aggregate([
  { $match: { created_at: { $gte: ISODate("2026-04-28") } } },
  { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      revenue: { $sum: "$amount" },
      orders:  { $sum: 1 }
  }},
  { $merge: {
      into: "daily_revenue",
      on: "_id",
      whenMatched: "replace",
      whenNotMatched: "insert"
  }}
])

// Custom update pipeline on match (preserve fields, refresh others)
{ $merge: {
    into: "daily_revenue",
    on: "_id",
    whenMatched: [
      { $set: {
          revenue:        "$$new.revenue",
          orders:         "$$new.orders",
          last_refreshed: "$$NOW"
      }}
    ],
    whenNotMatched: "insert"
}}

// Across databases
{ $merge: { into: { db: "analytics", coll: "daily_revenue" } } }</code></pre>

<p><strong><code>whenMatched</code> options</strong>:</p>
<table>
  <tr><th>Mode</th><th>Behavior</th></tr>
  <tr><td><code>"merge"</code> (default)</td><td>Shallow-merge fields; new wins on overlap</td></tr>
  <tr><td><code>"replace"</code></td><td>Full document replacement</td></tr>
  <tr><td><code>"keepExisting"</code></td><td>Skip update entirely (insert-only effect)</td></tr>
  <tr><td><code>"fail"</code></td><td>Error on any match &mdash; useful for data validation</td></tr>
  <tr><td><code>[pipeline]</code></td><td>Custom update logic with access to <code>$$new</code></td></tr>
</table>

<p><strong>Production patterns enabled by <code>$merge</code></strong>:</p>
<ul>
  <li><strong>Materialized views</strong> &mdash; refresh nightly or on schedule; queries read pre-computed results.</li>
  <li><strong>Incremental ETL</strong> &mdash; process only new data, upsert into target.</li>
  <li><strong>Event-sourced projections</strong> &mdash; reduce events into per-entity state.</li>
  <li><strong>Cross-cluster aggregation</strong> &mdash; analytics cluster materializes from operational cluster.</li>
  <li><strong>Atlas Charts pre-aggregation</strong> &mdash; dashboards read from <code>$merge</code>-built summary collections, not raw data.</li>
</ul>

<p><strong>Constraints</strong>: <code>$merge</code> must be the last stage; the <code>on</code> field must have a unique index in the target (or be <code>_id</code>); cross-cluster <code>$merge</code> requires both clusters in the same Atlas project. Pair with <strong>Atlas Triggers</strong> on a schedule to make refreshes hands-off.</p>
'''

ANSWERS[48] = r'''
<p>MongoDB&rsquo;s <strong>automatic failover</strong> is the centerpiece of replica-set high availability. When the primary becomes unreachable, the remaining members elect a new primary using a Raft-derived consensus protocol &mdash; clients reconnect transparently via the driver.</p>

<p><strong>The election process</strong>:</p>
<ol>
  <li>A secondary detects the primary is unreachable (heartbeat failures over <code>electionTimeoutMillis</code>, default 10 seconds).</li>
  <li>That secondary transitions to candidate state and requests votes.</li>
  <li>To be elected, the candidate must:
    <ul>
      <li>Have an oplog at least as up-to-date as the candidate that requested votes.</li>
      <li>Receive a majority of votes (Raft quorum).</li>
      <li>Have priority &gt; 0 (priority-0 members never become primary).</li>
    </ul>
  </li>
  <li>Winner declares itself primary, broadcasts the new term, starts accepting writes.</li>
  <li>Loser candidates step down to secondary.</li>
</ol>

<pre><code>// Replica set config controlling elections
rs.conf()
// {
//   _id: "rs0",
//   members: [
//     { _id: 0, host: "h1:27017", priority: 2 },     // preferred primary
//     { _id: 1, host: "h2:27017", priority: 1 },
//     { _id: 2, host: "h3:27017", priority: 0, hidden: true }   // backup, never primary
//   ],
//   settings: {
//     electionTimeoutMillis: 10000,
//     heartbeatIntervalMillis: 2000
//   }
// }

// Manually step down (planned maintenance)
rs.stepDown(60)   // current primary steps down for at least 60s

// Force a specific member to be primary
cfg = rs.conf()
cfg.members[0].priority = 10
rs.reconfig(cfg)</code></pre>

<p><strong>Failover characteristics</strong>:</p>
<table>
  <tr><th>Metric</th><th>Typical value</th></tr>
  <tr><td>Failure detection</td><td>~10 seconds (electionTimeout)</td></tr>
  <tr><td>Election round</td><td>1-3 seconds</td></tr>
  <tr><td>Total client-visible downtime</td><td>~12-15 seconds</td></tr>
  <tr><td>Data loss with <code>w: "majority"</code></td><td>Zero</td></tr>
  <tr><td>Data loss with <code>w: 1</code></td><td>Possible &mdash; rolled back into a rollback file</td></tr>
</table>

<p><strong>Driver-side resilience</strong>: modern drivers retry idempotent operations once on failover. Set <code>retryWrites=true</code> in the connection string (the default in modern drivers) so writes survive a single primary change.</p>

<p><strong>Atlas does the rest</strong>: alerts on member health, auto-replaces failed nodes, handles AZ/region-level outages, and offers <strong>multi-region active-active</strong> for the highest tier of availability. Self-hosted requires the same level of monitoring (PagerDuty + Prometheus alerts on member state changes).</p>
'''

ANSWERS[49] = r'''
<p>MongoDB ships in two editions plus a fully-managed cloud service. The split is between core database (free) and operational/security/compliance features (paid).</p>

<table>
  <tr><th>Capability</th><th>Community</th><th>Enterprise</th><th>Atlas</th></tr>
  <tr><td>Core database, replica sets, sharding</td><td>✓</td><td>✓</td><td>✓</td></tr>
  <tr><td>Aggregation, transactions, change streams</td><td>✓</td><td>✓</td><td>✓</td></tr>
  <tr><td>Atlas Search (Lucene full-text)</td><td>&minus;</td><td>&minus;</td><td>✓</td></tr>
  <tr><td>Atlas Vector Search</td><td>&minus;</td><td>&minus;</td><td>✓</td></tr>
  <tr><td>Encryption at rest</td><td>OS-level only</td><td>Native (KMIP)</td><td>Native + customer-managed keys</td></tr>
  <tr><td>LDAP / Kerberos auth</td><td>&minus;</td><td>✓</td><td>LDAP via Atlas</td></tr>
  <tr><td>Auditing</td><td>&minus;</td><td>✓</td><td>✓</td></tr>
  <tr><td>In-Memory storage engine</td><td>&minus;</td><td>✓</td><td>&minus;</td></tr>
  <tr><td>Ops Manager / Cloud Manager</td><td>&minus;</td><td>Ops Manager</td><td>Built-in</td></tr>
  <tr><td>BI Connector (SQL access)</td><td>&minus;</td><td>✓</td><td>✓</td></tr>
  <tr><td>Online Archive (S3 tiering)</td><td>&minus;</td><td>&minus;</td><td>✓</td></tr>
  <tr><td>Triggers / Functions / App Services</td><td>&minus;</td><td>&minus;</td><td>✓</td></tr>
  <tr><td>Continuous backup with PIT restore</td><td>DIY</td><td>Ops Manager</td><td>✓ Built-in</td></tr>
  <tr><td>License</td><td>SSPL</td><td>Commercial</td><td>SaaS subscription</td></tr>
</table>

<p><strong>The practical decision</strong>:</p>
<ul>
  <li><strong>Community</strong> &mdash; small projects, internal tools, OSS development, dev environments. Free, fully open-source under SSPL (note: SSPL is restrictive for SaaS resellers; check legal advice if building a managed service).</li>
  <li><strong>Enterprise</strong> &mdash; on-premises requirements with security/audit needs (banking, government, defense), air-gapped deployments. Includes Ops Manager for self-managed control plane.</li>
  <li><strong>Atlas</strong> &mdash; the modern default for the vast majority of teams. Pay-as-you-go, scales from M0 free tier to multi-shard global clusters. Includes Atlas Search, Vector Search, Triggers, and managed backups out of the box.</li>
</ul>

<p>Most companies move from Community to Atlas (skipping self-managed Enterprise) because the operational cost of running production MongoDB at scale rarely beats Atlas pricing once you factor in 24/7 on-call, backups, monitoring, security patching, and rebalancing.</p>
'''

ANSWERS[50] = r'''
<p>A <strong>rolling upgrade</strong> updates a replica set or sharded cluster <strong>one node at a time</strong>, keeping the system available throughout. MongoDB&rsquo;s replication protocol is designed for it &mdash; nodes running adjacent versions stay compatible, so the cluster never sees a moment where it&rsquo;s entirely on the old or new version.</p>

<p><strong>Replica set rolling upgrade</strong>:</p>
<ol>
  <li><strong>Read the release notes</strong> &mdash; look for breaking changes and check the upgrade path. MongoDB requires upgrading <em>major versions one step at a time</em> (4.4 &rarr; 5.0 &rarr; 6.0 &rarr; 7.0 &rarr; 8.0).</li>
  <li><strong>Set <code>featureCompatibilityVersion</code></strong> to the current version (ensures rollback is safe):
    <pre><code>db.adminCommand({ setFeatureCompatibilityVersion: "7.0" })</code></pre>
  </li>
  <li><strong>Upgrade secondaries first</strong>, one at a time:
    <ul>
      <li>Stop the <code>mongod</code>.</li>
      <li>Replace the binaries with the new version.</li>
      <li>Start <code>mongod</code> with the same data files.</li>
      <li>Wait until <code>rs.status()</code> shows <code>SECONDARY</code> and is fully caught up.</li>
    </ul>
  </li>
  <li><strong>Step down the primary</strong> (<code>rs.stepDown()</code>) and upgrade it.</li>
  <li><strong>Once all members are on the new version</strong>, set <code>featureCompatibilityVersion</code> to the new version to enable new features.</li>
</ol>

<p><strong>Sharded cluster rolling upgrade order</strong>:</p>
<ol>
  <li>Disable the balancer: <code>sh.stopBalancer()</code>.</li>
  <li>Upgrade <strong>config server</strong> replica set (rolling within it).</li>
  <li>Upgrade <strong>each shard</strong> replica set (rolling within each).</li>
  <li>Upgrade <strong>mongos routers</strong>.</li>
  <li>Re-enable the balancer.</li>
  <li>Bump <code>featureCompatibilityVersion</code>.</li>
</ol>

<p><strong>Operational checklist</strong>:</p>
<ul>
  <li>Test the upgrade on staging with a copy of production data first.</li>
  <li>Have a rollback plan: keep the old binaries available; FCV must remain at the lower version until 100% upgraded so you can downgrade without data corruption.</li>
  <li>Watch replication lag during each step &mdash; pause if a secondary falls behind.</li>
  <li>Schedule during low-traffic windows; expect brief failover blips when the primary steps down.</li>
</ul>

<p><strong>Atlas does this for you</strong> via the &ldquo;Cluster Tier &amp; Region&rdquo; UI &mdash; pick the new version, click Upgrade, Atlas handles the rolling upgrade with progress tracking. Self-hosted users on Ops Manager / Cloud Manager get the same automation. For teams running raw <code>mongod</code>, Ansible / Terraform playbooks are the standard way to script the sequence.</p>
'''


ANSWERS[51] = r'''
<p><strong><code>$redact</code></strong> is an aggregation stage that <strong>walks every level of a document and decides &mdash; per subdocument &mdash; whether to keep, drop, or descend further</strong>. It&rsquo;s the field-level access-control primitive in the pipeline language: instead of stripping fields after the fact, you embed permission tags in the data and let <code>$redact</code> filter the tree based on the caller&rsquo;s role.</p>

<pre><code>// Documents tag sections with required clearance levels
{
  _id: 1,
  title: "Q4 Plan",
  visibleTo: ["public", "internal"],
  details: { visibleTo: ["internal"], notes: "&hellip;" },
  payroll: { visibleTo: ["finance"], totals: 12345 }
}

// Pipeline: emit only what overlaps with userTags
db.docs.aggregate([
  { $redact: {
      $cond: {
        if:   { $gt: [{ $size: { $setIntersection: ["$visibleTo", ["public", "internal"]] } }, 0] },
        then: "$$DESCEND",     // keep this level, recurse into subdocs
        else: "$$PRUNE"         // drop this whole subtree
      }
  }}
])</code></pre>

<p>The expression returns one of three system variables &mdash; <strong><code>$$KEEP</code></strong> (include this level and don&rsquo;t descend), <strong><code>$$PRUNE</code></strong> (exclude entirely), or <strong><code>$$DESCEND</code></strong> (include this level and apply the same rule to each child). The recursion is what makes <code>$redact</code> distinct from <code>$project</code>: arbitrary depth, evaluated at each subtree.</p>

<p><strong>Practical caveats:</strong></p>
<ul>
  <li>Hard to debug &mdash; a single misplaced <code>$$DESCEND</code> can leak data. Always test with adversarial inputs.</li>
  <li>It can&rsquo;t look <em>up</em> the tree &mdash; the decision uses only the current subtree&rsquo;s fields.</li>
  <li>Modern projects usually prefer <strong>field-level access at the application or proxy layer</strong> &mdash; via <strong>SpiceDB</strong>, <strong>OpenFGA</strong>, <strong>Cerbos</strong>, or <strong>MongoDB Atlas&rsquo;s Field-Level Redaction</strong> (Enterprise) &mdash; because policy lives outside the documents and is auditable.</li>
</ul>
'''

ANSWERS[52] = r'''
<p>MongoDB transactions follow <strong>snapshot isolation</strong>: each transaction sees a consistent view as of its start time, and the storage engine (<strong>WiredTiger</strong>) detects <strong>write-write conflicts</strong> when two transactions try to modify the same document. The losing transaction aborts with a <code>WriteConflict</code> (transient error), and the recommended response is to <em>retry</em>.</p>

<pre><code>// Drivers do this for you with withTransaction()
const session = client.startSession()
try {
  await session.withTransaction(async () =&gt; {
    await accounts.updateOne(
      { _id: from },
      { $inc: { balance: -100 } },
      { session }
    )
    await accounts.updateOne(
      { _id: to },
      { $inc: { balance: 100 } },
      { session }
    )
  }, {
    readConcern:    { level: "snapshot" },
    writeConcern:   { w: "majority" },
    readPreference: "primary"
  })
} finally {
  await session.endSession()
}</code></pre>

<table><tr><th>Conflict type</th><th>Cause</th><th>Resolution</th></tr>
<tr><td>WriteConflict</td><td>Two transactions modifying the same document</td><td>Driver retry &mdash; <code>withTransaction()</code> wraps the body in a retry loop</td></tr>
<tr><td>TransactionExceededLifetimeLimitSeconds</td><td>Transaction ran longer than the 60s default</td><td>Shorten the transaction or raise <code>transactionLifetimeLimitSeconds</code></td></tr>
<tr><td>NoSuchTransaction</td><td>Stale session after primary stepdown</td><td>Restart the transaction with a fresh session</td></tr>
</table>

<p><strong>Best practices:</strong> keep transactions short (sub-second), touch as few documents as possible, never call external services inside the body, and prefer single-document atomic operators (<code>$inc</code>, <code>findOneAndUpdate</code>) when one document is enough &mdash; they don&rsquo;t need transaction overhead. For high-throughput workflows, the <strong>outbox pattern</strong> with <strong>Debezium</strong> change streams scales better than chained transactions.</p>
'''

ANSWERS[53] = r'''
<p>An <strong>arbiter</strong> is a special replica-set member that <strong>participates in elections but holds no data</strong>. Its only job is to provide a tie-breaking vote so a 2-node cluster can elect a primary. It&rsquo;s lightweight (no storage, no oplog) but creates real correctness problems &mdash; modern best practice is to <em>not use one</em>.</p>

<pre><code>// Add an arbiter to an existing replica set
rs.addArb("arbiter-host:27017")

// Or include it in the initial config
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "data1:27017" },
    { _id: 1, host: "data2:27017" },
    { _id: 2, host: "arbiter:27017", arbiterOnly: true }
  ]
})</code></pre>

<table><tr><th>Concern</th><th>Why arbiters cause issues</th></tr>
<tr><td>Write durability</td><td>Only 2 data nodes &mdash; lose one and majority writes can&rsquo;t commit</td></tr>
<tr><td>Read availability</td><td>Lose either data node and you can&rsquo;t serve writes</td></tr>
<tr><td>Rollback risk</td><td>The remaining secondary may be missing recent writes; replays cause rollback</td></tr>
<tr><td>P-CAP behavior</td><td>Arbiters increase the chance of stale reads and lost writes during partitions</td></tr>
</table>

<p>The fix: run <strong>three full data members</strong> instead. Arbiters were popular when storage was expensive; today, with cloud-managed databases (<strong>MongoDB Atlas</strong> defaults to 3 data nodes), the cost difference is negligible and you avoid the corner cases.</p>

<p>The official MongoDB documentation now explicitly recommends against arbiters in production. If you inherit a 2+arbiter cluster, the migration path is to add a third data-bearing member with <code>rs.add()</code>, wait for it to fully sync, then <code>rs.remove()</code> the arbiter.</p>
'''

ANSWERS[54] = r'''
<p><strong>MongoDB Atlas Search</strong> is the managed full-text search service built into Atlas. It&rsquo;s a <strong>Lucene-powered search index</strong> running alongside your MongoDB cluster, automatically synchronized via change streams. You query it with the <code>$search</code> aggregation stage, and results integrate with the rest of your pipeline.</p>

<pre><code>// Define a search index in the Atlas UI or via the Admin API
{
  mappings: {
    dynamic: false,
    fields: {
      title:   { type: "string", analyzer: "lucene.standard" },
      tags:    { type: "string", analyzer: "lucene.keyword" },
      content: { type: "string" }
    }
  }
}

// Query with $search
db.articles.aggregate([
  { $search: {
      compound: {
        must:   [{ text: { query: "mongodb", path: "title", score: { boost: { value: 2 } } } }],
        should: [{ text: { query: "indexes",  path: ["title", "content"] } }],
        filter: [{ equals: { path: "published", value: true } }]
      }
  }},
  { $limit: 20 }
])</code></pre>

<table><tr><th>Capability</th><th>Built-in <code>$text</code></th><th>Atlas Search</th></tr>
<tr><td>Relevance scoring</td><td>Basic TF-IDF</td><td>BM25 (modern), tunable</td></tr>
<tr><td>Fuzzy matching</td><td>None</td><td><code>fuzzy: { maxEdits: 2 }</code></td></tr>
<tr><td>Autocomplete</td><td>Manual prefix regex</td><td><code>autocomplete</code> operator with edge-n-grams</td></tr>
<tr><td>Faceting</td><td>Multi-step pipeline</td><td><code>facet</code> operator with counts</td></tr>
<tr><td>Multi-language</td><td>Per-collection</td><td>Per-field analyzers</td></tr>
<tr><td>Synonyms</td><td>None</td><td>Synonym mappings</td></tr>
</table>

<p>Atlas Search is the default choice for new projects on Atlas. Self-hosted deployments use <strong>Elasticsearch</strong>, <strong>OpenSearch</strong>, <strong>Meilisearch</strong>, or <strong>Typesense</strong> &mdash; all wire-compatible with similar feature sets. The newer <strong>Atlas Vector Search</strong> extends the same infrastructure to dense-embedding queries for AI/RAG use cases.</p>
'''

ANSWERS[55] = r'''
<p><strong>Capped collections</strong> are fixed-size, append-only ring buffers. Once they hit their byte or document cap, the oldest documents are evicted to make room for new ones. They&rsquo;re fast for high-volume writes but come with sharp restrictions that make them niche today.</p>

<pre><code>db.createCollection("logs", {
  capped: true,
  size: 100 * 1024 * 1024,   // 100 MB cap
  max:  1_000_000            // optional document-count cap
})

// Convert an existing collection (if it fits)
db.runCommand({ convertToCapped: "logs", size: 100*1024*1024 })</code></pre>

<table><tr><th>Property</th><th>Capped</th><th>Regular</th></tr>
<tr><td>Insertion order</td><td>Guaranteed; preserved on replication</td><td>Not guaranteed</td></tr>
<tr><td>Auto-eviction</td><td>Oldest documents</td><td>None &mdash; manual or TTL</td></tr>
<tr><td>Updates</td><td>Allowed only if size doesn&rsquo;t change</td><td>Free-form</td></tr>
<tr><td>Deletes</td><td>Forbidden (drop the collection instead)</td><td>Allowed</td></tr>
<tr><td>Sharding</td><td>Not supported</td><td>Yes</td></tr>
<tr><td>Indexing</td><td>Allowed (added in 3.2)</td><td>Yes</td></tr>
</table>

<p><strong>Modern alternatives are usually better:</strong></p>
<ul>
  <li><strong>Time-series collections (5.0+)</strong> &mdash; auto-bucketed, compressed, shardable; the right answer for IoT and metrics.</li>
  <li><strong>TTL indexes</strong> on a regular collection &mdash; <code>{ expireAfterSeconds: 86400 }</code>. More flexible eviction policy and supports updates and deletes.</li>
  <li><strong>Change streams + a Kafka/Redpanda topic</strong> &mdash; for genuine event-stream semantics, treat MongoDB as the system of record and stream out.</li>
</ul>

<p>Capped collections still have a niche: <strong>tailable cursors</strong> (the only place they&rsquo;re used in modern code is the oplog itself) and <strong>strict insertion-order replication</strong>. For everything else, prefer time-series or TTL.</p>
'''

ANSWERS[56] = r'''
<p>Three patterns dominate MongoDB <strong>multi-tenancy</strong>, each trading isolation for cost. The right choice depends on tenant size variance, compliance requirements, and operational complexity you can absorb.</p>

<table><tr><th>Pattern</th><th>Isolation</th><th>Operational cost</th><th>When to choose</th></tr>
<tr><td><strong>Database-per-tenant</strong></td><td>Strongest &mdash; separate auth, backups, indexes</td><td>High &mdash; per-tenant migrations, hard to query across</td><td>Regulated industries; few large tenants</td></tr>
<tr><td><strong>Collection-per-tenant</strong></td><td>Medium &mdash; shared DB, distinct collections</td><td>Medium &mdash; collection count grows linearly</td><td>SaaS with hundreds of mid-size tenants</td></tr>
<tr><td><strong>Shared collection + <code>tenantId</code></strong></td><td>Logical only &mdash; row-level filtering</td><td>Low &mdash; one schema, one index set</td><td>Many small tenants; cost-sensitive</td></tr>
</table>

<pre><code>// Shared-collection pattern (most common)
db.documents.createIndex({ tenantId: 1, _id: 1 }, { unique: true })
db.documents.createIndex({ tenantId: 1, createdAt: -1 })

// Every query MUST filter by tenantId &mdash; enforced via app-side middleware or views
db.createView(
  "tenant_42_documents", "documents",
  [{ $match: { tenantId: 42 } }]
)
db.tenant_42_documents.find()   // can&rsquo;t escape the filter

// Sharded variant: tenantId as the shard key (or compound: { tenantId: "hashed", _id: 1 })
sh.shardCollection("app.documents", { tenantId: 1, _id: 1 })</code></pre>

<p><strong>Operational notes:</strong></p>
<ul>
  <li>Make <code>tenantId</code> the leading field of <em>every</em> compound index &mdash; otherwise tenant-scoped queries can&rsquo;t use indexes efficiently.</li>
  <li>For very uneven tenants (a few whales among many minnows), use <strong>MongoDB zones</strong> to pin big tenants to dedicated shards.</li>
  <li>Driver-level approaches: <strong>Mongoose with discriminators</strong>, <strong>Prisma multi-schema</strong>, or middleware that injects <code>tenantId</code> on every query.</li>
  <li>Companies like <strong>Auth0</strong> and <strong>Vercel</strong> publish solid case studies on shared-collection multi-tenancy at scale.</li>
</ul>
'''

ANSWERS[57] = r'''
<p><strong><code>$reduce</code></strong> folds an array into a single value &mdash; equivalent to JavaScript&rsquo;s <code>Array.reduce()</code>. It iterates each element, threading an accumulator through each step, and returns the final accumulator. Useful when no built-in accumulator (<code>$sum</code>, <code>$avg</code>) covers the logic.</p>

<pre><code>// Sum the squares of an array
db.products.aggregate([
  { $project: {
      sumOfSquares: {
        $reduce: {
          input: "$prices",
          initialValue: 0,
          in: { $add: ["$$value", { $multiply: ["$$this", "$$this"] }] }
      }
    }
  }}
])

// Build a CSV string with a separator
db.users.aggregate([
  { $project: {
      tagsCsv: {
        $reduce: {
          input: "$tags",
          initialValue: "",
          in: {
            $cond: [
              { $eq: ["$$value", ""] },
              "$$this",
              { $concat: ["$$value", ", ", "$$this"] }
            ]
          }
      }
    }
  }}
])

// Stateful processing &mdash; running totals
db.transactions.aggregate([
  { $project: {
      runningTotal: {
        $reduce: {
          input: "$amounts",
          initialValue: { total: 0, history: [] },
          in: {
            total:   { $add: ["$$value.total", "$$this"] },
            history: { $concatArrays: ["$$value.history", [{ $add: ["$$value.total", "$$this"] }]] }
          }
      }
    }
  }}
])</code></pre>

<p><strong><code>$$value</code></strong> is the running accumulator (starts as <code>initialValue</code>); <strong><code>$$this</code></strong> is the current array element. The expression in <code>in</code> returns the new accumulator value &mdash; which becomes <code>$$value</code> for the next iteration.</p>

<p><strong>When to reach for <code>$reduce</code>:</strong></p>
<ul>
  <li>Custom accumulator logic that <code>$sum</code>/<code>$avg</code>/<code>$min</code> can&rsquo;t express.</li>
  <li>Building strings, deduped lists, or running totals from arrays inside a single document.</li>
  <li>Avoiding <code>$unwind</code>+<code>$group</code>, which explodes documents and breaks expression scope.</li>
</ul>

<p>For sliding-window calculations across documents (running averages over time), prefer <strong><code>$setWindowFields</code></strong> (5.0+) &mdash; purpose-built and cleaner than reducing.</p>
'''

ANSWERS[58] = r'''
<p>MongoDB&rsquo;s flexible schema makes evolution easy in theory but fragile in practice without discipline. The standard pattern is <strong>schema versioning per document</strong> &mdash; every document carries a <code>schemaVersion</code> field, and readers know how to migrate older versions on the fly or in a backfill.</p>

<pre><code>// Documents tag their version
{ _id: 1, schemaVersion: 1, name: "Alice", emails: ["a@x.com"] }
{ _id: 2, schemaVersion: 2, name: "Bob",   email: "b@x.com" }   // moved from array to scalar

// Reader handles both shapes
function normalize(doc) {
  if (doc.schemaVersion === 1) {
    return { ...doc, email: doc.emails[0], emails: undefined, schemaVersion: 2 }
  }
  return doc
}

// Lazy migration: upgrade on read
const doc = await users.findOne({ _id: 1 })
const upgraded = normalize(doc)
if (upgraded.schemaVersion !== doc.schemaVersion) {
  await users.replaceOne({ _id: doc._id }, upgraded)   // optional: persist the upgrade
}

// Eager migration: backfill in batches
db.users.aggregate([
  { $match: { schemaVersion: { $lt: 2 } } },
  { $set: {
      email:         { $arrayElemAt: ["$emails", 0] },
      schemaVersion: 2
  }},
  { $unset: "emails" },
  { $merge: { into: "users", on: "_id", whenMatched: "replace" } }
])</code></pre>

<table><tr><th>Strategy</th><th>Pros</th><th>Cons</th></tr>
<tr><td>Lazy (on read)</td><td>No long-running migration; cheap</td><td>Old data lingers; readers always handle multiple versions</td></tr>
<tr><td>Eager (batched backfill)</td><td>Single canonical shape; readers stay simple</td><td>Operational cost; replica lag risk on huge collections</td></tr>
<tr><td>Hybrid</td><td>Lazy upgrade on read +&nbsp;background backfill</td><td>Most code; usually the right answer</td></tr>
</table>

<p><strong>Tooling:</strong> <strong>Mongoose</strong>&rsquo;s discriminator/middleware support automates per-document version checks; <strong>Prisma</strong> and <strong>Drizzle</strong> manage versioning at the application schema layer. For schema-validation guarantees, set <code>$jsonSchema</code> validators on the collection &mdash; new writes must match, with the option to allow legacy documents to remain.</p>
'''

ANSWERS[59] = r'''
<p><strong><code>$function</code></strong> lets you embed a <strong>JavaScript function</strong> inside an aggregation pipeline &mdash; an escape hatch for logic that can&rsquo;t be expressed with built-in operators. It&rsquo;s powerful but slow and disabled by default; use it only as a last resort.</p>

<pre><code>// Custom field calculation
db.orders.aggregate([
  { $project: {
      _id: 1,
      tier: {
        $function: {
          body: function (total, isMember) {
            if (isMember) return total &gt; 1000 ? "platinum" : "gold"
            return total &gt; 500 ? "silver" : "bronze"
          },
          args: ["$total", "$isMember"],
          lang: "js"
      }
    }
  }}
])

// More complex: parsing a custom string format
db.docs.aggregate([
  { $project: {
      parsed: {
        $function: {
          body: `function (raw) {
            const parts = raw.split('|')
            return { type: parts[0], id: parts[1], date: new Date(parts[2]) }
          }`,
          args: ["$raw"],
          lang: "js"
      }
    }
  }}
])</code></pre>

<p><strong>Why it&rsquo;s a last resort:</strong></p>
<table><tr><th>Concern</th><th>Detail</th></tr>
<tr><td>Performance</td><td>Each invocation crosses into a JS engine; orders of magnitude slower than native operators</td></tr>
<tr><td>Security</td><td>Disabled by default &mdash; requires <code>--enableJavaScript</code> on <code>mongod</code> startup</td></tr>
<tr><td>Optimization</td><td>The query optimizer can&rsquo;t inspect the function body; can&rsquo;t reorder or use indexes through it</td></tr>
<tr><td>Sharded clusters</td><td>Function ships to each shard; debugging is awful</td></tr>
</table>

<p>Almost every <code>$function</code> can be rewritten with the standard expression language &mdash; <code>$cond</code>, <code>$switch</code>, <code>$let</code>, <code>$reduce</code>, <code>$regexFind</code>, <code>$dateFromString</code>, <code>$toString</code>. Try those first. If the logic is genuinely too complex, run a stage-out (<code>$out</code>/<code>$merge</code>) and process in <strong>application code</strong> instead &mdash; safer and easier to test.</p>

<p>Companion: <strong><code>$accumulator</code></strong> embeds JS functions for custom group accumulators (init/accumulate/merge/finalize). Same caveats apply.</p>
'''

ANSWERS[60] = r'''
<p><strong>LDAP authentication</strong> integrates MongoDB with corporate identity providers (Active Directory, OpenLDAP) so user accounts and roles are managed centrally. It&rsquo;s an Enterprise-edition feature; community edition supports SCRAM and x.509 only.</p>

<pre><code>// mongod startup flags or /etc/mongod.conf
security:
  authorization: enabled
  ldap:
    servers: "ldap.example.com"
    transportSecurity: tls
    bind:
      method: simple
      queryUser: "cn=mongo,ou=services,dc=example,dc=com"
      queryPassword: "secret"
    userToDNMapping:
      - match:    "(.+)"
        substitution: "uid={0},ou=users,dc=example,dc=com"
    authz:
      queryTemplate: "ou=groups,dc=example,dc=com??sub?(member={USER})"

setParameter:
  authenticationMechanisms: PLAIN

// MongoDB roles map to LDAP groups via $external
use admin
db.createRole({
  role: "cn=mongo-readers,ou=groups,dc=example,dc=com",
  roles: [{ role: "read", db: "appdb" }],
  privileges: []
})

// Connect with LDAP credentials
mongosh \
  --host mongo.example.com \
  --authenticationMechanism PLAIN \
  --authenticationDatabase '$external' \
  -u alice -p</code></pre>

<table><tr><th>Mechanism</th><th>Use case</th><th>Available in</th></tr>
<tr><td><strong>SCRAM-SHA-256</strong></td><td>Default; users in MongoDB itself</td><td>Community + Enterprise</td></tr>
<tr><td><strong>x.509 certificates</strong></td><td>Service-to-service; mTLS</td><td>Community + Enterprise</td></tr>
<tr><td><strong>LDAP / AD</strong></td><td>Corporate SSO</td><td>Enterprise only</td></tr>
<tr><td><strong>Kerberos / GSSAPI</strong></td><td>Windows AD environments</td><td>Enterprise only</td></tr>
<tr><td><strong>OIDC (8.0+)</strong></td><td>Modern federated SSO via Auth0/Okta/Azure AD</td><td>Enterprise; Atlas as managed</td></tr>
</table>

<p><strong>Modern path:</strong> on <strong>MongoDB Atlas</strong>, federated authentication via <strong>OIDC</strong> with <strong>Auth0</strong>, <strong>Okta</strong>, <strong>Azure AD</strong>, or <strong>WorkOS</strong> is easier to set up than raw LDAP and integrates with your existing IdP. For self-hosted Enterprise, LDAP is still the path of least resistance into AD.</p>
'''

ANSWERS[61] = r'''
<p><strong>Data archival</strong> moves cold (rarely-accessed) data out of the working set so it doesn&rsquo;t cost RAM, while keeping it available for compliance and analytics. The right strategy depends on access frequency and recovery time objectives.</p>

<table><tr><th>Tier</th><th>Storage</th><th>Access pattern</th><th>Tooling</th></tr>
<tr><td>Hot</td><td>Cluster RAM/SSD</td><td>Sub-second reads, all writes</td><td>Primary collections</td></tr>
<tr><td>Warm</td><td>Separate cheaper cluster</td><td>Occasional reads</td><td>Atlas Online Archive, separate replica set</td></tr>
<tr><td>Cold</td><td>S3, GCS, Azure Blob</td><td>Rare; analytics</td><td><code>mongodump</code> + Glacier; Atlas Data Federation; Iceberg/Delta on R2</td></tr>
<tr><td>Compliance</td><td>WORM storage</td><td>Read-only, audited</td><td>S3 Object Lock, Cloudflare R2 + lock policies</td></tr>
</table>

<pre><code>// MongoDB Atlas Online Archive &mdash; click to configure
// Defines a rule: documents older than 90 days move to S3-backed cold storage,
// still queryable via the same connection string but slower

// Self-managed: archive then delete
db.events.aggregate([
  { $match: { createdAt: { $lt: ISODate("2025-01-01") } } },
  { $merge: { into: { db: "archive", coll: "events_2024" } } }
])
db.events.deleteMany({ createdAt: { $lt: ISODate("2025-01-01") } })

// Or stream to S3 with mongoexport / Airbyte / Fivetran
mongoexport --uri "..." --collection events \
  --query '{ "createdAt": { "$lt": { "$date": "2025-01-01" } } }' \
  --out /tmp/events_2024.json
aws s3 cp /tmp/events_2024.json s3://archive-bucket/events/2024.json</code></pre>

<p><strong>Key practices:</strong></p>
<ul>
  <li>Archive on a <strong>predictable schedule</strong> (nightly, weekly) so capacity stays steady.</li>
  <li>Index the archive cutoff field (<code>createdAt</code>, <code>updatedAt</code>) &mdash; without it, archival queries scan everything.</li>
  <li>Run archival in <strong>chunks</strong> (10k docs/iteration) to avoid replica lag and long write locks.</li>
  <li>For GDPR-style erasure, archives must respect deletion requests &mdash; track erasure events in a separate immutable log.</li>
  <li><strong>Atlas Online Archive</strong> is the easiest path on Atlas; for self-hosted, build with TTL+<code>$out</code> or stream via <strong>Airbyte</strong>/<strong>Fivetran</strong> to <strong>BigQuery</strong>/<strong>Snowflake</strong>/<strong>Iceberg</strong>.</li>
</ul>
'''

ANSWERS[62] = r'''
<p><strong><code>$bucket</code></strong> and <strong><code>$bucketAuto</code></strong> partition documents into ranges &mdash; the difference is who picks the boundaries.</p>

<table><tr><th>Stage</th><th>You provide</th><th>MongoDB picks</th><th>Use when</th></tr>
<tr><td><code>$bucket</code></td><td>Boundary values</td><td>Document distribution</td><td>You know meaningful cut points (price tiers, age groups)</td></tr>
<tr><td><code>$bucketAuto</code></td><td>Number of buckets</td><td>Boundaries (balanced)</td><td>You want equal-population groups (quartiles, deciles)</td></tr>
</table>

<pre><code>// $bucket &mdash; explicit boundaries
db.products.aggregate([
  { $bucket: {
      groupBy: "$price",
      boundaries: [0, 50, 100, 500, 1000, 5000],
      default: "5000+",
      output: { count: { $sum: 1 }, avgRating: { $avg: "$rating" } }
  }}
])
// Each bucket covers [lower, upper); default catches anything outside

// $bucketAuto &mdash; equal-distribution, MongoDB chooses cut points
db.users.aggregate([
  { $bucketAuto: {
      groupBy: "$age",
      buckets: 4,                      // produce 4 quartiles
      output: { count: { $sum: 1 }, avgIncome: { $avg: "$income" } }
  }}
])

// $bucketAuto with granularity for round-number boundaries
db.products.aggregate([
  { $bucketAuto: {
      groupBy: "$price",
      buckets: 5,
      granularity: "R20",              // Renard series &mdash; nice round numbers
      output: { count: { $sum: 1 } }
  }}
])
// Granularities: POWERSOF2, 1-2-5, E6/E12/E24/E48/E96/E192, R5/R10/R20/R40/R80</code></pre>

<p><strong>Practical notes:</strong></p>
<ul>
  <li><code>$bucket</code> requires the <code>default</code> field if any document might fall outside boundaries &mdash; otherwise the stage throws.</li>
  <li>Boundaries must be sorted ascending and the same BSON type as <code>groupBy</code>.</li>
  <li>For dashboards, <code>$bucketAuto</code> + <code>granularity</code> produces histograms with friendly labels (10, 20, 50, 100&hellip;) without manual tuning.</li>
  <li>For very large datasets, push aggregation into a warehouse (<strong>BigQuery</strong>, <strong>Snowflake</strong>, <strong>ClickHouse</strong>) &mdash; native histogram support is faster.</li>
  <li>Time-bucketing is special: prefer <strong><code>$dateTrunc</code></strong> (5.0+) which handles calendar quirks correctly.</li>
</ul>
'''

ANSWERS[63] = r'''
<p>An <strong>in-place upgrade</strong> replaces the MongoDB binaries on existing data files without copying or rebuilding. It&rsquo;s fast and safe <em>if</em> you follow the rules: same major-version increments, replica-set rolling pattern, full backup beforehand.</p>

<pre><code>// Always one major version at a time:
//   6.0 &rarr; 7.0 &rarr; 8.0   (allowed)
//   6.0 &rarr; 8.0           (NOT allowed; must stop at 7.0 first)

// 1. Set feature compatibility version (FCV) to the current major
db.adminCommand({ setFeatureCompatibilityVersion: "6.0" })

// 2. Stop and upgrade ONE secondary at a time
sudo systemctl stop mongod
sudo apt install mongodb-org=7.0.x   // or yum / official tarball
sudo systemctl start mongod
rs.status()   // wait until SECONDARY catches up

// 3. Repeat for each secondary

// 4. Step down the primary, upgrade it last
rs.stepDown()
sudo systemctl stop mongod
sudo apt install mongodb-org=7.0.x
sudo systemctl start mongod

// 5. Once all members are on 7.0, bump FCV
db.adminCommand({ setFeatureCompatibilityVersion: "7.0" })</code></pre>

<table><tr><th>Step</th><th>Why</th></tr>
<tr><td>Backup first</td><td><code>mongodump</code> or filesystem snapshot &mdash; recovery if something goes wrong</td></tr>
<tr><td>Update drivers</td><td>Server features may require driver versions; check the compatibility matrix</td></tr>
<tr><td>Set FCV before upgrading</td><td>Lets you downgrade if you discover an issue mid-upgrade</td></tr>
<tr><td>Upgrade secondaries first</td><td>Primary serves writes the whole time; outages limited to step-down</td></tr>
<tr><td>Bump FCV last</td><td>Once new features are in use, downgrade is no longer possible</td></tr>
</table>

<p><strong>Sharded clusters</strong> add complexity: upgrade config servers first, then each shard&rsquo;s replica set, then mongos routers. Run with the <strong>balancer disabled</strong> during the upgrade.</p>

<p><strong>MongoDB Atlas</strong> automates the entire process &mdash; click an upgrade in the UI and Atlas does rolling upgrades, FCV management, and rollback for you. Self-hosted clusters benefit from <strong>Ops Manager</strong> or <strong>Cloud Manager</strong> for the same automation.</p>
'''

ANSWERS[64] = r'''
<p>MongoDB <strong>change streams</strong> emit a real-time feed of every modification &mdash; insert, update, delete, replace &mdash; using the replica-set oplog as the source of truth. They&rsquo;re the foundation for real-time analytics, cache invalidation, search-index sync, and event-driven architectures.</p>

<pre><code>// Watch a collection
const stream = db.collection("orders").watch([
  { $match: { operationType: { $in: ["insert", "update"] } } }
])

for await (const change of stream) {
  console.log(change.operationType, change.fullDocument)

  // Stream to Kafka for downstream consumers
  await kafka.produce({ topic: "orders.cdc", messages: [{ value: JSON.stringify(change) }] })

  // Or update a search index
  await typesense.collections("orders").documents().upsert(change.fullDocument)

  // Update aggregate counters
  await redis.hincrby(`store:${change.fullDocument.storeId}`, "order_count", 1)
}

// Resume after disconnects (essential for production)
const stream = db.collection("orders").watch([], {
  resumeAfter: lastResumeToken,           // saved checkpoint
  fullDocument: "updateLookup"            // include the post-image
})

// Pre/post images (6.0+) require collection-level config
db.runCommand({ collMod: "orders", changeStreamPreAndPostImages: { enabled: true } })</code></pre>

<table><tr><th>Use case</th><th>Pattern</th></tr>
<tr><td>Real-time dashboards</td><td>Watch &rarr; aggregate in memory &rarr; push to WebSocket clients</td></tr>
<tr><td>Search-index sync</td><td>Watch &rarr; project relevant fields &rarr; upsert to Atlas Search / Elasticsearch / Typesense</td></tr>
<tr><td>Cache invalidation</td><td>Watch &rarr; delete corresponding Redis keys</td></tr>
<tr><td>Event sourcing / outbox</td><td>Watch &rarr; emit to Kafka / Redpanda / NATS</td></tr>
<tr><td>Audit trail</td><td>Watch &rarr; append to immutable log (S3 Object Lock, ClickHouse)</td></tr>
</table>

<p><strong>Production checklist:</strong> persist <strong>resume tokens</strong> after each batch (so reconnects don&rsquo;t lose events), enable <strong>pre/post-image capture</strong> for full update context, run consumers in <strong>idempotent</strong> mode (the same event may be replayed), and consider <strong>Debezium MongoDB connector</strong> if you already use Kafka Connect.</p>
'''

ANSWERS[65] = r'''
<p><strong><code>$mergeObjects</code></strong> shallow-merges multiple objects into one &mdash; fields from later objects overwrite earlier ones on conflict. It&rsquo;s the spread-operator equivalent for the aggregation language.</p>

<pre><code>// Layer defaults with per-user overrides
db.users.aggregate([
  { $project: {
      settings: {
        $mergeObjects: [
          { theme: "light", lang: "en", notifications: true },   // defaults
          "$preferences"                                          // user-supplied
      ]
    }
  }}
])
// User settings win; missing keys fall back to defaults

// Combine fields from multiple subdocuments
db.profiles.aggregate([
  { $project: {
      combined: {
        $mergeObjects: ["$basic", "$contact", "$preferences"]
      }
  }}
])

// Promote nested object to top-level while preserving _id
db.users.aggregate([
  { $replaceRoot: {
      newRoot: { $mergeObjects: [{ _id: "$_id" }, "$profile"] }
  }}
])

// Group accumulator: progressive merge of per-user settings
db.userPrefs.aggregate([
  { $sort: { userId: 1, ts: 1 } },
  { $group: {
      _id: "$userId",
      latest: { $mergeObjects: "$settings" }   // each new doc layers on top
  }}
])</code></pre>

<table><tr><th>Behavior</th><th>Detail</th></tr>
<tr><td>Right-to-left precedence</td><td>Later operands win on key conflict</td></tr>
<tr><td>Null/missing tolerance</td><td>Missing fields treated as empty objects &mdash; safe to include conditionally</td></tr>
<tr><td>Shallow merge only</td><td>Nested objects replace, not deep-merge: <code>{a:{x:1}}</code> + <code>{a:{y:2}}</code> = <code>{a:{y:2}}</code></td></tr>
<tr><td>Group accumulator</td><td>Iteratively merges across documents in current sort order</td></tr>
</table>

<p>For deep merging, <strong>recurse with <code>$objectToArray</code> + <code>$arrayToObject</code></strong> in a custom expression, or merge in application code &mdash; deep merging is rarely the right answer in a database query (it hides surprises). <code>$mergeObjects</code> is widely used in <strong>$lookup</strong> result-shaping, <strong>defaults+overrides</strong>, and <strong>group-by-key</strong> roll-ups.</p>
'''

ANSWERS[66] = r'''
<p>MongoDB&rsquo;s memory model is dominated by the <strong>WiredTiger cache</strong> (default 50% of RAM minus 1GB), which holds frequently-accessed data and indexes. Tuning memory means keeping the working set in cache, sizing the cache appropriately, and watching eviction.</p>

<pre><code>// Inspect the WiredTiger cache
db.serverStatus().wiredTiger.cache
//   "bytes currently in the cache",
//   "tracked dirty bytes",
//   "pages evicted by application threads",   &lt;-- bad: under cache pressure
//   "eviction worker thread evicting pages"

// Tune cache size in mongod.conf
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 32         // explicit; defaults to (RAM-1GB)/2

// Working-set check: aim for cache &gt;= active data + indexes
db.runCommand({ dbStats: 1, scale: 1024*1024*1024 })   // size in GB
//   indexSize + relevant data &lt;= cacheSizeGB</code></pre>

<table><tr><th>Symptom</th><th>Cause</th><th>Fix</th></tr>
<tr><td>High <code>pages evicted by application threads</code></td><td>Working set exceeds cache</td><td>Add RAM, scale up, or shard</td></tr>
<tr><td>High disk reads + low cache hit rate</td><td>Frequent eviction; queries scan cold data</td><td>Add indexes; project less; scale up</td></tr>
<tr><td>OOM kills on the host</td><td>Cache + connection memory + OS &gt; available RAM</td><td>Lower <code>cacheSizeGB</code>; bound connections</td></tr>
<tr><td>Slow secondaries</td><td>Background eviction can&rsquo;t keep up with oplog replay</td><td>Larger oplog; faster disk; larger RAM</td></tr>
</table>

<p><strong>Other knobs:</strong></p>
<ul>
  <li><strong>Connection pooling</strong> &mdash; each connection costs ~1MB. Use a connection pool in the driver and a server-side pooler (<strong>ProxySQL</strong>-equivalent for Mongo: <strong>mongos routers</strong> for sharded; for replica sets, the driver pool is enough).</li>
  <li><strong>Index size</strong> &mdash; total index size should fit in cache; drop unused indexes via <code>$indexStats</code> or <strong>Atlas Performance Advisor</strong>.</li>
  <li><strong>Aggregation memory</strong> &mdash; per-stage 100MB limit; set <code>{ allowDiskUse: true }</code> for large group-by/sort.</li>
  <li><strong>OS-level</strong> &mdash; disable transparent huge pages (THP), use <code>noatime</code> mount, and on Linux <code>vm.swappiness=1</code>.</li>
</ul>
'''

ANSWERS[67] = r'''
<p>The <strong><code>$indexStats</code></strong> aggregation stage reports <strong>per-index access counters</strong> &mdash; how many times each index has been used since the server started. It&rsquo;s the canonical tool for spotting unused indexes that waste RAM and slow writes.</p>

<pre><code>db.orders.aggregate([{ $indexStats: {} }])
// Output (one document per index):
// {
//   name: "customer_id_1",
//   key: { customer_id: 1 },
//   accesses: { ops: 142_589, since: ISODate("2025-12-01T00:00:00Z") },
//   host: "shard0-primary:27017"
// }

// Find indexes with few or zero accesses
db.orders.aggregate([
  { $indexStats: {} },
  { $project: { name: 1, ops: "$accesses.ops", since: "$accesses.since" } },
  { $match: { ops: { $lt: 100 } } },
  { $sort:  { ops: 1 } }
])

// Across all collections
db.getCollectionNames().forEach(function (c) {
  db[c].aggregate([
    { $indexStats: {} },
    { $match: { "accesses.ops": 0 } },
    { $project: { _id: 0, collection: { $literal: c }, name: 1 } }
  ]).forEach(printjson)
})</code></pre>

<table><tr><th>Index state</th><th>Action</th></tr>
<tr><td>Zero accesses since server start</td><td>Likely safe to drop &mdash; verify across all replica members and over a full business cycle</td></tr>
<tr><td>Few accesses, large size</td><td>Drop unless required for compliance or rare reports</td></tr>
<tr><td>Heavy accesses, never updated</td><td>Working as intended; leave alone</td></tr>
<tr><td>Heavy accesses + many writes</td><td>Healthy hot index; ensure sized in cache</td></tr>
</table>

<p><strong>Caveats:</strong></p>
<ul>
  <li><code>$indexStats</code> resets on restart &mdash; check long enough after restart, or correlate with monitoring history (Atlas, Datadog, Percona PMM).</li>
  <li>Run on <strong>every replica member</strong> &mdash; secondaries see different traffic if you route reads there.</li>
  <li>An index with zero ops may still be needed for a <strong>uniqueness constraint</strong> or <strong>TTL behavior</strong> &mdash; check intent before dropping.</li>
  <li><strong>MongoDB Atlas Performance Advisor</strong> automates this analysis with an interactive UI showing redundant and unused indexes.</li>
</ul>
'''

ANSWERS[68] = r'''
<p>MongoDB <strong>auditing</strong> records authentication, authorization, schema changes, and data-access events for compliance with regulations like HIPAA, PCI-DSS, GDPR, and SOX. It&rsquo;s an Enterprise-edition feature; community edition needs application-side or proxy-based auditing.</p>

<pre><code>// /etc/mongod.conf &mdash; configure audit log
auditLog:
  destination: file
  format:      JSON
  path:        /var/log/mongodb/audit.json
  filter: '{
    atype: { $in: [
      "authenticate", "authCheck", "createUser", "dropUser",
      "grantRolesToUser", "revokeRolesFromUser",
      "createCollection", "dropCollection", "dropDatabase",
      "createIndex", "dropIndex"
    ]}
  }'

// Audit record format
{
  atype:      "createUser",
  ts:         ISODate("2026-04-28T10:00:00Z"),
  uuid:       BinData(...),
  local:      { ip: "127.0.0.1", port: 27017 },
  remote:     { ip: "10.0.1.5",   port: 54231 },
  users:      [{ user: "admin", db: "admin" }],
  roles:      [{ role: "userAdminAnyDatabase", db: "admin" }],
  param:      { user: "newuser", db: "appdb", roles: [...] },
  result:     0
}</code></pre>

<table><tr><th>Compliance regime</th><th>Required audit events</th><th>Retention</th></tr>
<tr><td>HIPAA</td><td>All PHI access; user creates/changes</td><td>6 years</td></tr>
<tr><td>PCI-DSS</td><td>Auth events; admin actions; CHD access</td><td>1 year online + 1 year offline</td></tr>
<tr><td>GDPR</td><td>PII access; deletion requests</td><td>Per data-controller policy</td></tr>
<tr><td>SOX</td><td>All financial data changes</td><td>7 years</td></tr>
</table>

<p><strong>Production hardening:</strong></p>
<ul>
  <li>Stream audit logs to <strong>SIEM</strong> &mdash; <strong>Splunk</strong>, <strong>Datadog</strong>, <strong>Elastic SIEM</strong>, <strong>Sumo Logic</strong>, <strong>Wazuh</strong>.</li>
  <li>Use <strong>WORM storage</strong> for retained audit logs &mdash; <strong>S3 Object Lock</strong>, <strong>Cloudflare R2 + lock policies</strong>.</li>
  <li>Encrypt audit logs at rest and in transit; rotate daily.</li>
  <li><strong>MongoDB Atlas</strong> includes audit logs in Enterprise tier with one-click streaming to AWS CloudWatch / GCP Logging / Azure Monitor.</li>
  <li>Compliance automation: <strong>Drata</strong>, <strong>Vanta</strong>, <strong>Secureframe</strong> hook into Atlas APIs to verify audit configuration as evidence.</li>
</ul>
'''

ANSWERS[69] = r'''
<p><strong><code>$dateToParts</code></strong> deconstructs a Date into its components (year, month, day, hour, etc.) as fields of an object. <strong><code>$dateFromParts</code></strong> does the inverse &mdash; constructs a Date from individual fields. Together they&rsquo;re the bridge between &ldquo;date as a single timestamp&rdquo; and &ldquo;date as queryable parts&rdquo;.</p>

<pre><code>// Decompose a Date for analytics
db.orders.aggregate([
  { $project: {
      _id: 1,
      parts: { $dateToParts: { date: "$createdAt", timezone: "Asia/Kolkata" } }
      // {
      //   year: 2026, month: 4, day: 28,
      //   hour: 15, minute: 30, second: 45,
      //   millisecond: 0
      // }
  }}
])

// ISO calendar variant (good for week-of-year analytics)
db.orders.aggregate([
  { $project: {
      iso: { $dateToParts: { date: "$createdAt", iso8601: true } }
      // { isoWeekYear, isoWeek, isoDayOfWeek, hour, ... }
  }}
])

// Construct a Date from integer fields
db.events.aggregate([
  { $project: {
      ts: { $dateFromParts: {
        year:  "$year",
        month: "$month",
        day:   "$day",
        hour:  "$hour",
        timezone: "America/New_York"
      }}
  }}
])

// Common pattern: bucket by ISO week
db.orders.aggregate([
  { $group: {
      _id: { $dateTrunc: { date: "$createdAt", unit: "week" } },
      count: { $sum: 1 }
  }}
])</code></pre>

<table><tr><th>Operator</th><th>Use when</th></tr>
<tr><td><code>$dateToParts</code></td><td>You need separate fields for projection, grouping, or filtering</td></tr>
<tr><td><code>$dateFromParts</code></td><td>You have year/month/day fields and need a Date for range queries</td></tr>
<tr><td><code>$dateTrunc</code> (5.0+)</td><td>Bucket Date by unit (day/week/month/quarter); cleaner than parts-and-rebuild</td></tr>
<tr><td><code>$dateAdd</code> / <code>$dateSubtract</code></td><td>Calendar-correct date arithmetic (handles leap years, varying month lengths)</td></tr>
<tr><td><code>$dateDiff</code></td><td>Difference in calendar units between two Dates</td></tr>
</table>

<p><strong>Always specify <code>timezone</code></strong> for user-facing analytics &mdash; UTC defaults silently shift &ldquo;midnight&rdquo; for non-UTC users. <code>$dateTrunc</code> + <code>timezone</code> is the modern way to bucket dates correctly.</p>
'''

ANSWERS[70] = r'''
<p><strong>Data anonymization</strong> permanently transforms PII so it can&rsquo;t be linked back to an individual; <strong>data obfuscation</strong> hides PII from non-privileged users while keeping it recoverable. The right approach depends on whether you ever need to recover the original.</p>

<table><tr><th>Technique</th><th>Reversible?</th><th>Use case</th></tr>
<tr><td><strong>Pseudonymization</strong></td><td>Yes (with key)</td><td>Tokenized IDs while preserving joins; GDPR-friendly</td></tr>
<tr><td><strong>Hashing</strong></td><td>No</td><td>Email/phone matching without storing raw value</td></tr>
<tr><td><strong>Generalization</strong></td><td>No</td><td>Replace exact age with range (30-39); ZIP+4 to ZIP-3</td></tr>
<tr><td><strong>Masking</strong></td><td>No</td><td>Show last 4 digits only (cards, SSNs)</td></tr>
<tr><td><strong>k-anonymity</strong></td><td>No (mathematically)</td><td>Each record indistinguishable among k others</td></tr>
<tr><td><strong>Differential privacy</strong></td><td>No</td><td>Statistical analysis without exposing individuals</td></tr>
</table>

<pre><code>// Pseudonymize emails for an analytics export
db.users.aggregate([
  { $project: {
      _id:   1,
      email: { $function: {
        body: function (e) {
          const crypto = require("crypto")
          return crypto.createHmac("sha256", "rotation-key-2026").update(e).digest("hex")
        },
        args: ["$email"],
        lang: "js"
      }},
      ageRange: { $switch: {
        branches: [
          { case: { $lt: ["$age", 18] }, then: "&lt;18" },
          { case: { $lt: ["$age", 30] }, then: "18-29" },
          { case: { $lt: ["$age", 50] }, then: "30-49" }
        ],
        default: "50+"
      }},
      zip3: { $substr: ["$zip", 0, 3] }
  }},
  { $merge: { into: { db: "analytics", coll: "users_anon" } } }
])</code></pre>

<p><strong>Modern tooling:</strong></p>
<ul>
  <li><strong>Tonic.ai</strong>, <strong>Gretel</strong>, <strong>Mostly AI</strong> &mdash; synthetic-data and de-identification platforms with MongoDB connectors.</li>
  <li><strong>CipherStash</strong>, <strong>EvenVault</strong>, <strong>Skyflow</strong>, <strong>VGS</strong>, <strong>Basis Theory</strong> &mdash; vault-based tokenization (PII never touches your DB; you store tokens).</li>
  <li><strong>MongoDB Atlas Field-Level Encryption</strong> &mdash; client-side encryption with deterministic and randomized algorithms; queryable encrypted fields (Queryable Encryption, GA in 7.0+).</li>
  <li>For machine learning, <strong>differential privacy libraries</strong> (Google&rsquo;s <code>diffprivlib</code>, OpenDP) add calibrated noise to aggregates.</li>
</ul>
'''

ANSWERS[71] = r'''
<p><code>$match</code> filters documents through; <code>$facet</code> processes the same input through <strong>multiple sub-pipelines in parallel</strong> and returns each result as a named field of a single output document. They solve very different problems.</p>

<table><tr><th>Aspect</th><th><code>$match</code></th><th><code>$facet</code></th></tr>
<tr><td>Purpose</td><td>Filter documents</td><td>Run multiple aggregations on the same data</td></tr>
<tr><td>Input/output</td><td>N docs in, &le;N out</td><td>N docs in, exactly 1 out</td></tr>
<tr><td>Index use</td><td>Yes (when first in pipeline)</td><td>Sub-pipelines start from <code>$facet</code>&rsquo;s input; no index access</td></tr>
<tr><td>Common usage</td><td>Every aggregation pipeline</td><td>Dashboards needing multiple summaries in one round trip</td></tr>
</table>

<pre><code>// $match &mdash; filter by status
db.orders.aggregate([
  { $match: { status: "paid", country: "IN" } }
])

// $facet &mdash; dashboard with multiple summaries
db.orders.aggregate([
  { $match: { status: "paid" } },     // shared filter (uses index!)
  { $facet: {
      totals:        [{ $group: { _id: null, total: { $sum: "$amount" }, count: { $sum: 1 } } }],
      topCustomers:  [
        { $group: { _id: "$customerId", total: { $sum: "$amount" } } },
        { $sort:  { total: -1 } },
        { $limit: 10 }
      ],
      ordersPerDay:  [
        { $group: { _id: { $dateTrunc: { date: "$createdAt", unit: "day" } }, n: { $sum: 1 } } },
        { $sort:  { _id: -1 } },
        { $limit: 30 }
      ],
      categoryBreakdown: [
        { $group: { _id: "$category", count: { $sum: 1 } } },
        { $sort:  { count: -1 } }
      ]
  }}
])
// One output document with four arrays &mdash; perfect for a dashboard endpoint</code></pre>

<p><strong>Critical pattern:</strong> always place a shared <code>$match</code> <em>before</em> <code>$facet</code> so the input is filtered once using indexes. Inside <code>$facet</code>, sub-pipelines start from the same in-memory document set &mdash; no further index access. Putting <code>$match</code> inside each sub-pipeline duplicates the filter and runs it without index help.</p>

<p>For e-commerce-style faceted search (counts per category, price band, brand), <strong>MongoDB Atlas Search</strong>&rsquo;s <code>facet</code> operator is far faster than aggregation <code>$facet</code> &mdash; it&rsquo;s purpose-built for this pattern.</p>
'''

ANSWERS[72] = r'''
<p>A robust MongoDB <strong>backup and disaster recovery</strong> strategy combines <strong>multiple methods</strong> at different recovery points: snapshots for fast full restore, incremental backups for point-in-time recovery, and geographically-replicated copies for site failures.</p>

<table><tr><th>Method</th><th>RPO</th><th>RTO</th><th>Tooling</th></tr>
<tr><td>Continuous oplog backup</td><td>seconds</td><td>minutes-hours</td><td>Atlas Backup, Ops Manager, <code>mongodump --oplog</code></td></tr>
<tr><td>Volume snapshots</td><td>minutes</td><td>minutes</td><td>EBS, GCP PD, Azure Disk &mdash; coordinated with <code>fsyncLock</code></td></tr>
<tr><td>Logical dumps</td><td>hours</td><td>hours-days</td><td><code>mongodump</code> + S3</td></tr>
<tr><td>Replica in another region</td><td>seconds</td><td>seconds (failover)</td><td>Atlas Multi-Region; cross-AZ replica members</td></tr>
</table>

<pre><code>// Atlas: enable continuous backup + point-in-time restore
//   Cluster Settings &rarr; Backup &rarr; PITR enabled

// Self-hosted: cron a nightly mongodump with oplog
mongodump \
  --uri "mongodb://backup-user:pwd@host:27017/?replicaSet=rs0&amp;authSource=admin" \
  --oplog \
  --gzip \
  --archive=/backups/$(date +%Y%m%d).gz

aws s3 cp /backups/$(date +%Y%m%d).gz \
  s3://prod-backups/$(date +%Y%m%d).gz \
  --storage-class STANDARD_IA

// Lifecycle: 7 days STANDARD &rarr; 30 days IA &rarr; 1 year Glacier &rarr; delete

// Restore for point-in-time recovery
mongorestore --uri "..." --oplogReplay \
  --oplogLimit "1714291200:0" \   // unix timestamp:opIndex
  --archive=20260428.gz --gzip</code></pre>

<p><strong>The 3-2-1 rule</strong>: <strong>3</strong> copies, on <strong>2</strong> different media, <strong>1</strong> off-site. For MongoDB: cluster + Atlas Backup + cross-region S3 archive.</p>

<p><strong>Production checklist:</strong></p>
<ul>
  <li><strong>Test restores monthly</strong> &mdash; an untested backup is a gamble. Automate with a recovery runbook.</li>
  <li><strong>Encrypt backups at rest</strong> with AES-256 + customer-managed keys (KMS).</li>
  <li><strong>Document recovery procedures</strong> in a runbook everyone can find at 3 AM.</li>
  <li><strong>Monitor backup completion</strong> &mdash; alerting on missed runs.</li>
  <li>For compliance, use <strong>WORM storage</strong> with retention locks (S3 Object Lock).</li>
  <li><strong>Atlas Live Migration</strong> and <strong>Cluster-to-Cluster Sync</strong> handle the cross-region/cross-cluster case officially.</li>
</ul>
'''

ANSWERS[73] = r'''
<p><strong><code>$replaceRoot</code></strong> and <strong><code>$replaceWith</code></strong> are aliases &mdash; both replace the entire document with the value of an embedded sub-expression. <code>$replaceWith</code> is the newer, cleaner syntax (5.0+); they&rsquo;re otherwise identical.</p>

<pre><code>// Document: { _id: 1, profile: { name: "Alice", age: 30 }, meta: {...} }

// Promote `profile` to the top level
db.users.aggregate([
  { $replaceRoot: { newRoot: "$profile" } }
])
// { name: "Alice", age: 30 }   _id, meta dropped

// Cleaner with $replaceWith
db.users.aggregate([
  { $replaceWith: "$profile" }
])

// Combine with $mergeObjects to preserve _id
db.users.aggregate([
  { $replaceWith: { $mergeObjects: [{ _id: "$_id" }, "$profile"] } }
])

// Pattern: dedupe-by-newest
db.events.aggregate([
  { $sort:  { userId: 1, ts: -1 } },
  { $group: { _id: "$userId", latest: { $first: "$$ROOT" } } },
  { $replaceWith: "$latest" }
])

// $replaceWith with computed object
db.orders.aggregate([
  { $replaceWith: {
      orderId: "$_id",
      total:   { $sum: "$lineItems.price" },
      country: "$shipping.country"
  }}
])</code></pre>

<table><tr><th>When to use</th><th>Stage</th></tr>
<tr><td>Promote a nested object to top-level</td><td><code>$replaceWith: "$nested"</code></td></tr>
<tr><td>Reshape entirely (new structure, computed fields)</td><td><code>$replaceWith: { newField: ... }</code></td></tr>
<tr><td>Just hide/show specific fields</td><td><code>$project</code> &mdash; keeps existing structure</td></tr>
<tr><td>Add fields without dropping any</td><td><code>$addFields</code> / <code>$set</code></td></tr>
</table>

<p><strong>Key differences from <code>$project</code>:</strong> <code>$project</code> reshapes within the existing document boundaries (you list which fields to keep). <code>$replaceWith</code> replaces the document entirely &mdash; you start from a sub-expression that becomes the whole document. The resulting document inherits no fields from the input unless you explicitly include them via <code>$mergeObjects</code>.</p>

<p>Common use case: after a <code>$lookup</code> + <code>$unwind</code>, the joined data sits inside a sub-field. <code>$replaceWith: "$joinedDoc"</code> flattens it cleanly.</p>
'''

ANSWERS[74] = r'''
<p>Long-running queries are the most common cause of MongoDB performance crises &mdash; they hold resources, slow other operations, and can trigger replica lag. The toolkit is <code>currentOp</code>, the <strong>profiler</strong>, the <strong>slow query log</strong>, and modern APM.</p>

<pre><code>// See running operations
db.currentOp({ "secs_running": { $gte: 5 } })
//   ns:        "appdb.orders"
//   op:        "command"
//   secs_running: 12,
//   command:   { aggregate: "orders", pipeline: [...] }

// Kill an operation
db.killOp(12345)   // opid from currentOp

// Enable the profiler (level 1 = slow ops only, level 2 = all ops)
db.setProfilingLevel(1, { slowms: 100 })   // log queries &gt; 100ms

// Inspect the profiler collection
db.system.profile.find({ millis: { $gte: 500 } })
                .sort({ ts: -1 })
                .limit(10)
                .pretty()

// Slow query log via mongod settings
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100
systemLog:
  verbosity: 0
  component:
    query:
      verbosity: 1   // include execution stats</code></pre>

<table><tr><th>Tool</th><th>Granularity</th><th>Cost</th></tr>
<tr><td><code>$currentOp</code></td><td>Live snapshot</td><td>Free; aggregation-based filtering</td></tr>
<tr><td>Profiler (level 1)</td><td>Per-op records in <code>system.profile</code></td><td>Low; capped collection</td></tr>
<tr><td>Profiler (level 2)</td><td>Every op</td><td>High &mdash; only for short investigations</td></tr>
<tr><td>Slow query log</td><td>Per-op log lines</td><td>Low; default in production</td></tr>
<tr><td>Atlas Performance Advisor</td><td>Live + historical, with index suggestions</td><td>Included on Atlas</td></tr>
<tr><td>APM (Datadog/New Relic/Honeycomb)</td><td>Application-side traces</td><td>External; correlates DB time with request latency</td></tr>
</table>

<p><strong>Modern observability stack:</strong> <strong>MongoDB Atlas Query Insights</strong> + <strong>Performance Advisor</strong> identify slow queries and suggest indexes; <strong>Percona PMM</strong> does the same for self-hosted; <strong>Datadog Database Monitoring</strong> or <strong>New Relic</strong> integrate query traces with full request flow. <strong>Honeycomb</strong> excels for high-cardinality query exploration.</p>

<p>Set <strong>maxTimeMS</strong> on every query at the application layer &mdash; bounds query lifetime and prevents single bad queries from running forever.</p>
'''

ANSWERS[75] = r'''
<p><strong>Read concern</strong> and <strong>write concern</strong> control the consistency-vs-latency trade-offs of every operation. They&rsquo;re the knobs that let you choose &ldquo;fast and possibly stale&rdquo; or &ldquo;strict and slow&rdquo; per query.</p>

<table><tr><th>Read concern</th><th>Returns</th><th>Latency</th></tr>
<tr><td><code>"local"</code> (default)</td><td>Most recent local data &mdash; may not be majority-committed</td><td>Lowest</td></tr>
<tr><td><code>"available"</code></td><td>Same as local on standalone/replica; no causal consistency on sharded</td><td>Lowest</td></tr>
<tr><td><code>"majority"</code></td><td>Majority-committed data only &mdash; durable</td><td>Higher</td></tr>
<tr><td><code>"linearizable"</code></td><td>Reflects all majority-acked writes; full linearizability</td><td>Highest</td></tr>
<tr><td><code>"snapshot"</code> (in transactions)</td><td>Consistent point-in-time view</td><td>Higher</td></tr>
</table>

<table><tr><th>Write concern</th><th>Acknowledged when</th><th>Latency</th></tr>
<tr><td><code>w: 0</code></td><td>Driver buffers; no server ack</td><td>Lowest (fire-and-forget)</td></tr>
<tr><td><code>w: 1</code> (default)</td><td>Primary writes</td><td>Low</td></tr>
<tr><td><code>w: "majority"</code></td><td>Majority of voting members confirmed</td><td>Higher; durable</td></tr>
<tr><td><code>w: N</code></td><td>N members confirmed</td><td>Tunable</td></tr>
<tr><td><code>j: true</code></td><td>+ flushed to journal on disk</td><td>Higher</td></tr>
</table>

<pre><code>// Per-operation
db.orders.insertOne(doc, {
  writeConcern: { w: "majority", j: true, wtimeout: 5000 }
})

db.orders.find({...}).readConcern("majority")

// Connection-string defaults
mongodb://host:27017/?w=majority&amp;readConcernLevel=majority

// In a session/transaction
const session = client.startSession({
  defaultTransactionOptions: {
    readConcern:    { level: "snapshot" },
    writeConcern:   { w: "majority" },
    readPreference: "primary"
  }
})</code></pre>

<p><strong>Production defaults:</strong></p>
<ul>
  <li>Reads: <code>"majority"</code> for anything user-visible; <code>"local"</code> for caches/internal counters where stale is fine.</li>
  <li>Writes: <code>w: "majority", j: true</code> for anything you can&rsquo;t lose. <code>w: 1</code> for high-volume telemetry where some loss is acceptable.</li>
  <li>Always set <code>wtimeout</code> &mdash; without it, a partition-stuck write hangs forever.</li>
  <li>For financial data, transactions with <code>"snapshot"</code> + <code>w: "majority"</code> is the baseline.</li>
</ul>
'''


ANSWERS[76] = r'''
<p><strong><code>$setWindowFields</code></strong> (5.0+) is MongoDB&rsquo;s answer to SQL window functions &mdash; running totals, moving averages, rank, lead/lag, percentiles &mdash; computed across a sliding window of documents without breaking out into <code>$unwind</code>+<code>$group</code>+<code>$lookup</code> gymnastics.</p>

<pre><code>// Running total + 7-day moving average per customer
db.orders.aggregate([
  { $setWindowFields: {
      partitionBy: "$customerId",
      sortBy:      { date: 1 },
      output: {
        runningTotal: {
          $sum:    "$amount",
          window:  { documents: ["unbounded", "current"] }
        },
        movingAvg7d: {
          $avg:    "$amount",
          window:  { range: [-7, 0], unit: "day" }
        },
        rankByAmount: { $rank: {} },
        prevAmount:   { $shift: { output: "$amount", by: -1 } }
      }
  }},
  { $sort: { customerId: 1, date: 1 } }
])

// Top 3 orders per customer (dense_rank style)
db.orders.aggregate([
  { $setWindowFields: {
      partitionBy: "$customerId",
      sortBy:      { amount: -1 },
      output:      { rankInGroup: { $denseRank: {} } }
  }},
  { $match: { rankInGroup: { $lte: 3 } } }
])</code></pre>

<table><tr><th>Window operator</th><th>Purpose</th></tr>
<tr><td><code>$sum</code>, <code>$avg</code>, <code>$min</code>, <code>$max</code>, <code>$stdDev*</code></td><td>Aggregate over the window</td></tr>
<tr><td><code>$rank</code>, <code>$denseRank</code>, <code>$documentNumber</code></td><td>Position within the partition</td></tr>
<tr><td><code>$shift</code></td><td>Lead/lag &mdash; access prior or next document</td></tr>
<tr><td><code>$first</code>, <code>$last</code></td><td>First / last value in window</td></tr>
<tr><td><code>$linearFill</code>, <code>$locf</code></td><td>Time-series gap filling (carry forward, linear interp)</td></tr>
</table>

<p><strong>Window definitions:</strong></p>
<ul>
  <li><code>documents: [-3, 0]</code> &mdash; previous 3 docs + current.</li>
  <li><code>documents: ["unbounded", "current"]</code> &mdash; everything from start of partition.</li>
  <li><code>range: [-7, 0], unit: "day"</code> &mdash; documents within 7 days behind <code>sortBy</code> field (must be Date).</li>
</ul>

<p>Before <code>$setWindowFields</code>, these patterns required either complex self-joins via <code>$lookup</code> or post-processing in application code. The native window stage is dramatically faster and clearer &mdash; the standard tool for time-series and per-group ranking analytics in modern MongoDB.</p>
'''

ANSWERS[77] = r'''
<p>Sharding an existing large collection is a multi-step process: pick a shard key, pre-split chunks, enable sharding, and let the balancer migrate data. Done wrong, it locks the cluster for hours; done right, it&rsquo;s an online operation.</p>

<pre><code>// 1. Choose the shard key &mdash; permanent decision (until 5.0+ allowed reshardCollection)
//    Goals: high cardinality, even distribution, matches query pattern

// 2. Index the shard key first
db.orders.createIndex({ tenantId: 1, _id: 1 })

// 3. Enable sharding on the database
sh.enableSharding("appdb")

// 4. Pre-split &mdash; create empty chunks before migration to avoid hot spots
//    For hashed shard keys, this is automatic
sh.shardCollection(
  "appdb.orders",
  { tenantId: 1, _id: 1 },             // compound shard key
  false,                                // unique
  { presplitHashedZones: true }
)

// 5. Monitor balancer
sh.status()                             // chunk distribution per shard
db.collection.getShardDistribution()    // live data per shard

// 6. After balancing, watch for hot chunks via mongos logs
db.adminCommand({ getShardMap: 1 })

// 7. Resharding (5.0+) lets you change the key online
db.adminCommand({
  reshardCollection: "appdb.orders",
  key: { customerId: 1, _id: 1 }        // new shard key
})</code></pre>

<table><tr><th>Shard-key trap</th><th>Symptom</th><th>Fix</th></tr>
<tr><td>Monotonic key (<code>{_id: 1}</code>, timestamps)</td><td>All writes hit one shard (hot shard)</td><td>Use hashed: <code>{ _id: "hashed" }</code> or compound</td></tr>
<tr><td>Low cardinality (<code>{country: 1}</code>)</td><td>Jumbo chunks; can&rsquo;t split</td><td>Use compound key: <code>{ country: 1, _id: 1 }</code></td></tr>
<tr><td>Unevenly distributed key</td><td>Skewed shards; one fills first</td><td>Hashed key or pre-split based on data analysis</td></tr>
<tr><td>Wrong key for queries</td><td>Scatter-gather queries hit every shard</td><td>Reshape queries or reshard (5.0+)</td></tr>
</table>

<p><strong>Production approach:</strong> on <strong>MongoDB Atlas</strong>, use the Cluster Tier UI to add shards and configure shard keys; Atlas handles pre-splitting and balancing. Self-hosted setups benefit from <strong>Ops Manager</strong>. For very large collections (TB+), do shard migrations during off-peak hours and monitor replica lag closely &mdash; chunk migrations write through the oplog.</p>
'''

ANSWERS[78] = r'''
<p>The &ldquo;<strong>too many open files</strong>&rdquo; error means MongoDB has hit the OS limit on file descriptors. The culprit is usually a fast-growing connection count or a collection-and-index count that exceeded what the OS allows.</p>

<pre><code>// Check current limits
ulimit -n                                # process limit
cat /proc/$(pgrep mongod)/limits         # actual mongod limits
ss -tan | wc -l                          # active connections
ls /proc/$(pgrep mongod)/fd | wc -l      # open file descriptors

// Recommended settings (MongoDB official guidance)
// /etc/security/limits.d/99-mongodb.conf
mongodb soft nofile 64000
mongodb hard nofile 64000
mongodb soft nproc  64000
mongodb hard nproc  64000

// systemd unit override: /etc/systemd/system/mongod.service.d/limits.conf
[Service]
LimitNOFILE=64000
LimitNPROC=64000

// Apply
sudo systemctl daemon-reload
sudo systemctl restart mongod</code></pre>

<table><tr><th>Cause</th><th>Diagnostic</th><th>Fix</th></tr>
<tr><td>Connection storm from app</td><td><code>db.serverStatus().connections</code></td><td>Connection pooling; increase <code>maxPoolSize</code> ceiling and add app-side queue</td></tr>
<tr><td>Many collections + indexes</td><td><code>db.runCommand({ dbStats: 1 })</code></td><td>Consolidate collections; drop unused indexes</td></tr>
<tr><td>WiredTiger&rsquo;s file count</td><td>Each collection/index = file</td><td>Built-in &mdash; one reason to avoid pattern of &ldquo;collection per tenant&rdquo;</td></tr>
<tr><td>Apps not closing cursors</td><td>Cursor leaks from missing <code>finally</code></td><td>Use <code>for await</code> + try/finally; modern drivers auto-close</td></tr>
</table>

<p><strong>Modern path:</strong></p>
<ul>
  <li>Set <code>nofile</code> to 64,000 (or even 1,000,000) on every MongoDB host. Not negotiable on production servers.</li>
  <li>For containers (Docker, Kubernetes), set <code>ulimits</code> in the pod spec: <code>securityContext.sysctls</code> or <code>resources.limits</code>.</li>
  <li>Use <strong>connection pooling</strong> at the driver layer &mdash; never open a new connection per request. Default pool size in modern drivers (Node.js, Go, Java) is 100; tune up for high-concurrency apps.</li>
  <li>For thousands of microservices hitting one cluster, consider <strong>connection multiplexing</strong> via <strong>mongos routers</strong> in sharded mode or a <strong>Cloud SQL Auth proxy</strong>-style sidecar.</li>
  <li><strong>MongoDB Atlas</strong> sets these limits automatically.</li>
</ul>
'''

ANSWERS[79] = r'''
<p>Both <strong><code>$out</code></strong> and <strong><code>$merge</code></strong> write pipeline output to a target collection &mdash; but they have very different semantics. <code>$out</code> replaces the entire target; <code>$merge</code> upserts based on a key. Choose by whether you&rsquo;re rebuilding from scratch or incrementally maintaining.</p>

<table><tr><th>Aspect</th><th><code>$out</code></th><th><code>$merge</code></th></tr>
<tr><td>Operation</td><td>Replace entire target collection</td><td>Insert / update / replace per matching key</td></tr>
<tr><td>Pre-existing target docs not in pipeline</td><td>Removed</td><td>Kept</td></tr>
<tr><td>Target indexes</td><td>Recreated from source if specified</td><td>Preserved</td></tr>
<tr><td>Cross-database</td><td>Same DB only (5.0+ allows cross-DB)</td><td>Cross-DB and cross-cluster (with Atlas)</td></tr>
<tr><td>Atomicity</td><td>Atomic swap at end of pipeline</td><td>Per-document upserts; not atomic across docs</td></tr>
<tr><td>Use case</td><td>Nightly full rebuild</td><td>Incremental ETL, materialized views</td></tr>
</table>

<pre><code>// $out &mdash; full rebuild every run
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: { _id: "$customerId", total: { $sum: "$amount" } } },
  { $out: "customer_totals_full" }      // wipes and rebuilds
])

// $merge &mdash; incremental update; keep records not in this run
db.orders.aggregate([
  { $match: { createdAt: { $gte: lastRunTime } } },   // only new orders
  { $group: { _id: "$customerId", added: { $sum: "$amount" } } },
  { $merge: {
      into: "customer_totals_incremental",
      on: "_id",
      whenMatched: [
        { $set: { total: { $add: ["$total", "$$new.added"] } } }
      ],
      whenNotMatched: "insert"
  }}
])

// $merge to a different cluster (Atlas)
{ $merge: { into: { db: "warehouse", coll: "summary" }, ... } }</code></pre>

<p><strong>Decision rule:</strong></p>
<ul>
  <li>Use <strong><code>$out</code></strong> when the source contains every document you&rsquo;d want in the target &mdash; daily snapshot of a denormalized view.</li>
  <li>Use <strong><code>$merge</code></strong> when adding to an existing target &mdash; running totals, deltas since last run, periodic refreshes.</li>
  <li>For very large materialized views, <code>$merge</code> with <code>whenMatched: "replace"</code> is the safe default &mdash; idempotent and incremental.</li>
</ul>
'''

ANSWERS[80] = r'''
<p><strong><code>$function</code></strong> embeds a JavaScript expression for use in any aggregation context; <strong><code>$accumulator</code></strong> defines a custom group accumulator with init/accumulate/merge/finalize stages. Both are escape hatches for logic you can&rsquo;t express with built-in operators &mdash; both come with serious performance and operational caveats.</p>

<pre><code>// $function &mdash; per-document custom logic
db.orders.aggregate([
  { $project: {
      severity: { $function: {
        body: function (total, hasIssue) {
          if (hasIssue &amp;&amp; total &gt; 1000) return "critical"
          if (hasIssue) return "warning"
          return "ok"
        },
        args: ["$total", "$hasIssue"],
        lang: "js"
      }}
  }}
])

// $accumulator &mdash; custom group accumulator
db.transactions.aggregate([
  { $group: {
      _id: "$accountId",
      stats: { $accumulator: {
        init:       function () { return { total: 0, count: 0, max: -Infinity } },
        initArgs:   [],
        accumulate: function (state, amount) {
          return {
            total: state.total + amount,
            count: state.count + 1,
            max:   Math.max(state.max, amount)
          }
        },
        accumulateArgs: ["$amount"],
        merge:    function (a, b) {     // for sharded clusters
          return {
            total: a.total + b.total,
            count: a.count + b.count,
            max:   Math.max(a.max, b.max)
          }
        },
        finalize: function (state) {     // optional shaping
          return { ...state, avg: state.count ? state.total / state.count : 0 }
        },
        lang: "js"
      }}
  }}
])</code></pre>

<table><tr><th>Concern</th><th>Detail</th></tr>
<tr><td>Performance</td><td>10-100x slower than native operators &mdash; each call into a JS engine</td></tr>
<tr><td>Security</td><td>Disabled by default; needs <code>--enableJavaScript</code></td></tr>
<tr><td>Optimization</td><td>Optimizer can&rsquo;t see inside; can&rsquo;t use indexes through them</td></tr>
<tr><td>Sharded clusters</td><td><code>$accumulator.merge</code> is mandatory; testing is painful</td></tr>
</table>

<p><strong>Better paths:</strong> express the logic with built-in operators (<code>$cond</code>, <code>$switch</code>, <code>$let</code>, <code>$reduce</code>, <code>$regexFind</code>, <code>$dateFromString</code>) wherever possible. If the logic is genuinely too complex, run an <code>$out</code>/<code>$merge</code> and process in <strong>application code</strong> instead &mdash; safer, testable, and orders of magnitude faster on hot paths.</p>
'''

ANSWERS[81] = r'''
<p>Large-scale MongoDB deployments succeed on <strong>operational discipline</strong> more than any single feature. Patterns that compound: thoughtful schema design, aggressive index hygiene, observability, automated capacity, and battle-tested DR.</p>

<table><tr><th>Pillar</th><th>Practices</th></tr>
<tr><td><strong>Schema</strong></td><td>Design for access patterns; embed where read together; reference where written separately; version every document; validate with <code>$jsonSchema</code></td></tr>
<tr><td><strong>Indexes</strong></td><td>ESR rule (Equality, Sort, Range); audit with <code>$indexStats</code> monthly; keep total index size in cache; use partial/sparse indexes for selective fields</td></tr>
<tr><td><strong>Sharding</strong></td><td>Pick a shard key for both even distribution and query targeting; reshape collections (5.0+) when patterns change; pre-split big imports</td></tr>
<tr><td><strong>Observability</strong></td><td>Atlas Performance Advisor or Percona PMM; APM (Datadog, New Relic, Honeycomb); correlate slow queries with request traces; alert on replication lag</td></tr>
<tr><td><strong>Capacity</strong></td><td>Auto-scale on Atlas; cap connections per service; size cache for working set + indexes; monitor cache eviction</td></tr>
<tr><td><strong>DR</strong></td><td>Cross-region replicas; PITR backups tested monthly; runbooks for every failure mode; chaos drills</td></tr>
<tr><td><strong>Schema migrations</strong></td><td>Expand-contract pattern; never block writes; use <code>$jsonSchema</code> validators in <code>warn</code> first then <code>error</code>; tools: Atlas Schema Suggestions, Mongoose</td></tr>
<tr><td><strong>Security</strong></td><td>Authentication, TLS, Field-Level Encryption (or Queryable Encryption 7.0+), audit logs streamed to SIEM; least-privilege roles; rotation</td></tr>
</table>

<pre><code>// Health-check dashboard signals to track
//   - replicationLag (secondaries)
//   - cacheEvictions (WiredTiger)
//   - lockTime / queueLength
//   - slowOps count and patterns
//   - connections in/out
//   - ops/sec by op type
//   - oplog window (must be &gt;&gt; replication lag)
//   - storage growth rate vs. capacity</code></pre>

<p><strong>Modern stack:</strong> <strong>MongoDB Atlas</strong> covers most of this out of the box &mdash; auto-scaling, backups, performance advisor, multi-region, federated auth via OIDC, and integrated APM. Self-hosted teams use <strong>Ops Manager</strong>, <strong>Percona PMM</strong>, or build from <strong>Prometheus</strong> + <strong>Grafana</strong> + <strong>mongodb_exporter</strong>. For organization-wide governance, <strong>HashiCorp Vault</strong> manages secrets and <strong>Atlas API</strong> + <strong>Terraform</strong> codifies deployments.</p>
'''

ANSWERS[82] = r'''
<p>MongoDB models hierarchical data with several patterns; the right one depends on tree depth, mutation rate, and query patterns. The classic options are parent reference, child references, array of ancestors, materialized path, and nested set &mdash; with <strong><code>$graphLookup</code></strong> as the modern query primitive.</p>

<table><tr><th>Pattern</th><th>Document shape</th><th>Best for</th></tr>
<tr><td><strong>Parent reference</strong></td><td><code>{ _id, name, parent_id }</code></td><td>Frequent updates; shallow trees; ancestor traversal via <code>$graphLookup</code></td></tr>
<tr><td><strong>Child references</strong></td><td><code>{ _id, name, children: [ids] }</code></td><td>Read children fast; small fan-out</td></tr>
<tr><td><strong>Array of ancestors</strong></td><td><code>{ _id, name, ancestors: [a1, a2, a3] }</code></td><td>O(1) ancestor queries; subtree counts; deep trees</td></tr>
<tr><td><strong>Materialized path</strong></td><td><code>{ _id, name, path: ",a,b,c," }</code></td><td>Prefix queries via <code>$regex</code>; readable; deep trees</td></tr>
<tr><td><strong>Nested set</strong></td><td><code>{ _id, name, lft, rgt }</code></td><td>Subtree queries fast; mutations very expensive (every insert rewrites siblings)</td></tr>
</table>

<pre><code>// Parent reference + $graphLookup for transitive queries
db.categories.aggregate([
  { $match: { _id: "shoes" } },
  { $graphLookup: {
      from: "categories",
      startWith: "$_id",
      connectFromField: "_id",
      connectToField:  "parent_id",
      as: "descendants",
      maxDepth: 10                     // safety bound
  }}
])

// Array-of-ancestors (Mongo&rsquo;s recommended hybrid)
{ _id: "running-shoes", parent_id: "shoes", ancestors: ["sports", "footwear", "shoes"] }
db.categories.find({ ancestors: "footwear" })   // all descendants of footwear, indexed!

// Update an ancestors array on move (transactional)
session.withTransaction(async () =&gt; {
  await categories.updateOne({ _id: nodeId }, { $set: { parent_id: newParent } }, { session })
  // recursive update of ancestors arrays for the moved subtree
})</code></pre>

<p>The <strong>array of ancestors</strong> pattern is the most popular for trees that fit in memory: subtree membership queries are O(1) with an index, and you only rewrite the array on moves (rare). Combine it with parent reference for the &ldquo;walk up one level&rdquo; case.</p>

<p>For very large hierarchies (org charts, taxonomy trees), specialized graph databases (<strong>Neo4j</strong>, <strong>Amazon Neptune</strong>) outperform MongoDB. For social-network-style graphs (followers, friends), modeling reads-vs-writes asymmetrically and using <strong>Redis</strong> for hot lookups is common.</p>
'''

ANSWERS[83] = r'''
<p>A <strong>hot backup</strong> takes a consistent copy of MongoDB data <em>without stopping the server</em>. The mechanisms differ by deployment: filesystem snapshots, <code>mongodump --oplog</code>, or managed services like <strong>Atlas Backup</strong> and <strong>Ops Manager Backup</strong>.</p>

<table><tr><th>Method</th><th>Consistency mechanism</th><th>RPO</th></tr>
<tr><td>Atlas Continuous Backup</td><td>Oplog-based PITR</td><td>seconds</td></tr>
<tr><td>EBS / GCP PD snapshot</td><td>WiredTiger checkpoint + journaling</td><td>minutes</td></tr>
<tr><td><code>mongodump --oplog</code></td><td>Captures oplog window during dump</td><td>varies</td></tr>
<tr><td>Filesystem snapshot (LVM, ZFS)</td><td>Atomic via copy-on-write</td><td>minutes</td></tr>
<tr><td>Percona Backup for MongoDB</td><td>Logical + oplog (open source)</td><td>seconds</td></tr>
</table>

<pre><code>// Cloud volume snapshot (most common for self-hosted)
//   1. Snapshot the volume holding /data/db while mongod runs
//   2. WiredTiger&rsquo;s journal+checkpoint scheme guarantees crash-recovery from the snapshot
//
// AWS:
aws ec2 create-snapshot --volume-id vol-abc123 \
  --description "mongo-shard0-secondary $(date +%Y%m%d)"

// mongodump --oplog &mdash; tail the oplog during the dump for consistency
mongodump --uri "mongodb://host:27017/?replicaSet=rs0" \
  --oplog --gzip --archive=/backups/$(date +%Y%m%d).gz

// Restore with oplog replay
mongorestore --uri "..." --oplogReplay \
  --archive=/backups/20260428.gz --gzip

// Percona Backup for MongoDB (PBM) &mdash; open source PITR
pbm backup --type=physical
pbm restore "$BACKUP_NAME" --time "2026-04-28T14:30:00"</code></pre>

<p><strong>Best practice:</strong></p>
<ul>
  <li><strong>Take backups from a dedicated secondary</strong> &mdash; isolates the backup load from query traffic. Configure with <code>priority: 0, hidden: true, votes: 0</code>.</li>
  <li><strong>Pair physical snapshots with oplog backups</strong> for point-in-time recovery between snapshot intervals.</li>
  <li><strong>Encrypt backups at rest</strong> with KMS-managed keys.</li>
  <li><strong>Test restores monthly</strong> &mdash; an untested backup is a bet.</li>
  <li><strong>Atlas Backup</strong> is the easiest path on Atlas: continuous oplog capture + per-second PITR + cross-region snapshots, all click-to-configure.</li>
</ul>
'''

ANSWERS[84] = r'''
<p>MongoDB performance is bounded by <strong>random I/O</strong> on the data and index files. Optimization is mostly about keeping the working set in memory; when that&rsquo;s impossible, fast disks and smart layout become the next levers.</p>

<table><tr><th>Action</th><th>Effect</th></tr>
<tr><td>Use NVMe SSDs (or io1/io2 on AWS)</td><td>10-100x random IOPS over HDDs/SATA SSDs</td></tr>
<tr><td>Sufficient cache (<code>cacheSizeGB</code>)</td><td>Working set in cache eliminates disk I/O entirely for hot reads</td></tr>
<tr><td>Tune <code>readahead</code></td><td>Default 256K is too high for MongoDB; set 8-32 sectors</td></tr>
<tr><td>Disable Transparent Huge Pages</td><td>THP causes erratic latency &mdash; mandatory disable</td></tr>
<tr><td>Mount with <code>noatime</code></td><td>Skip read-time inode updates</td></tr>
<tr><td>Separate journal disk</td><td>Sequential journal writes don&rsquo;t compete with random data I/O</td></tr>
<tr><td>RAID-10 over RAID-5/6</td><td>RAID-5 parity recalculation kills random write latency</td></tr>
<tr><td>WiredTiger compression</td><td>Default <code>snappy</code>; <code>zstd</code> for higher ratio at small CPU cost</td></tr>
</table>

<pre><code>// Disable Transparent Huge Pages (Linux)
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

// Set readahead (8KB or 16KB)
sudo blockdev --setra 32 /dev/nvme0n1

// /etc/fstab
/dev/nvme0n1   /data   xfs   noatime,nodiratime   0   0

// Verify mongod sees the right disk
db.serverStatus().wiredTiger.cache
db.serverStatus().wiredTiger["block-manager"]
//   "bytes read", "bytes written", "blocks read"</code></pre>

<p><strong>Diagnostics:</strong></p>
<ul>
  <li><code>iostat -xz 1</code> &mdash; watch <code>%util</code>, <code>await</code>, <code>r/s + w/s</code>. <code>%util</code> near 100% with high <code>await</code> = saturated disk.</li>
  <li><code>mongostat</code> &mdash; <code>dirty %</code> and <code>used %</code> from cache; rising dirty% means writes outpace eviction.</li>
  <li><strong>Atlas Performance Advisor</strong> surfaces &ldquo;working set exceeds memory&rdquo; warnings directly.</li>
  <li>For <strong>cloud deployments</strong>, instance-store NVMe (i3, i4i on AWS) gives the lowest latency; gp3 EBS with provisioned IOPS is the cost-effective baseline.</li>
</ul>
'''

ANSWERS[85] = r'''
<p><strong>MongoDB Ops Manager</strong> is the on-prem management plane for self-hosted MongoDB &mdash; the Enterprise-edition equivalent of Atlas. It automates deployment, monitoring, backup/restore, and rolling upgrades for clusters running in your own data centers.</p>

<table><tr><th>Capability</th><th>Detail</th></tr>
<tr><td>Automation</td><td>Define cluster topology declaratively; agents on each host execute changes</td></tr>
<tr><td>Monitoring</td><td>Time-series metrics for every replica member, charts, alerts</td></tr>
<tr><td>Backup</td><td>Continuous oplog capture; PITR restore to any timestamp; cross-cluster restores</td></tr>
<tr><td>Rolling upgrades</td><td>Coordinated stepDowns and member upgrades with zero downtime</td></tr>
<tr><td>Index management</td><td>Suggest, build, and audit indexes from the UI</td></tr>
<tr><td>Encryption</td><td>Manages key rotation for storage and field-level encryption</td></tr>
</table>

<pre><code>// High-level setup
//   1. Provision Ops Manager: 3+ application servers + a backing MongoDB replica set ("App DB")
//   2. Provision a separate replica set for backup data ("Blockstore" or "S3 + Oplog Store")
//   3. Install MongoDB Agents on each managed host
//   4. From the UI, declaratively define managed clusters

// Agent installation (one per managed host)
curl -OL https://opsmanager.example.com/download/agent/automation/mongodb-mms-automation-agent.tar.gz
tar zxf mongodb-mms-automation-agent.tar.gz
./agent --opsManagerUrl https://opsmanager.example.com \
        --apiKey "$AGENT_API_KEY" \
        --groupId "$PROJECT_ID"

// Declare a cluster topology in the UI &mdash; agents converge to it
{
  name: "prod-shard0",
  members: [
    { host: "shard0a:27017", priority: 1 },
    { host: "shard0b:27017", priority: 1 },
    { host: "shard0c:27017", priority: 0, hidden: true }   // backup secondary
  ],
  mongoVersion: "7.0.5",
  authentication: { mechanisms: ["SCRAM-SHA-256"] },
  tls: { mode: "requireTLS", certificateKeyFile: "/etc/ssl/mongo.pem" }
}</code></pre>

<p><strong>When to use Ops Manager:</strong></p>
<ul>
  <li><strong>Self-hosted production</strong> with hundreds of nodes &mdash; the manual operational cost is otherwise prohibitive.</li>
  <li><strong>Air-gapped environments</strong> (defense, finance) where Atlas isn&rsquo;t allowed.</li>
  <li>Teams that have grown past <strong>Cloud Manager</strong> (the lighter SaaS version that doesn&rsquo;t require self-hosting Ops Manager itself).</li>
</ul>

<p><strong>Modern alternative:</strong> on cloud, <strong>MongoDB Atlas</strong> covers the same scope with no operational burden. Most new deployments choose Atlas; Ops Manager remains the path for regulated industries and on-prem-only constraints. <strong>Kubernetes operators</strong> (<strong>MongoDB Kubernetes Operator</strong>, <strong>Percona Operator</strong>) are an emerging alternative for cloud-native self-hosted environments.</p>
'''

ANSWERS[86] = r'''
<p><strong>ISO 8601 date operators</strong> in MongoDB compute date components according to the ISO standard rather than the Gregorian calendar &mdash; week numbers and the year that &ldquo;owns&rdquo; them differ between the two for week 1 and week 52/53. Critical for analytics that must align with corporate or financial calendars.</p>

<pre><code>// Document field: orderDate (a Date)
db.orders.aggregate([
  { $project: {
      _id: 1,
      // Standard (Gregorian)
      year:        { $year:        "$orderDate" },
      month:       { $month:       "$orderDate" },
      day:         { $dayOfMonth:  "$orderDate" },
      // ISO 8601 variants
      isoYear:     { $isoWeekYear: "$orderDate" },     // Year that owns the ISO week
      isoWeek:     { $isoWeek:     "$orderDate" },     // 1-53
      isoDayOfWeek: { $isoDayOfWeek: "$orderDate" }    // 1=Mon, 7=Sun
  }}
])

// Group orders by ISO week (W01 starts on Monday containing Jan 4th)
db.orders.aggregate([
  { $group: {
      _id: {
        year: { $isoWeekYear: "$orderDate" },
        week: { $isoWeek:     "$orderDate" }
      },
      revenue: { $sum: "$amount" }
  }},
  { $sort: { "_id.year": 1, "_id.week": 1 } }
])

// Modern alternative: $dateTrunc (5.0+) handles week math directly
db.orders.aggregate([
  { $group: {
      _id: { $dateTrunc: { date: "$orderDate", unit: "week", startOfWeek: "monday" } },
      revenue: { $sum: "$amount" }
  }}
])</code></pre>

<table><tr><th>Operator</th><th>Returns</th></tr>
<tr><td><code>$year</code></td><td>Calendar year (1970-9999)</td></tr>
<tr><td><code>$isoWeekYear</code></td><td>ISO 8601 year that owns the week (Jan 1 might belong to previous year)</td></tr>
<tr><td><code>$week</code></td><td>US week (Sunday-start, 0-53)</td></tr>
<tr><td><code>$isoWeek</code></td><td>ISO 8601 week (Monday-start, 1-53)</td></tr>
<tr><td><code>$dayOfWeek</code></td><td>1=Sunday through 7=Saturday</td></tr>
<tr><td><code>$isoDayOfWeek</code></td><td>1=Monday through 7=Sunday</td></tr>
</table>

<p><code>$isoDate</code> isn&rsquo;t a query operator &mdash; <code>ISODate("2026-04-28")</code> in mongosh is just the constructor for a Date type. Use <code>$dateFromString</code> in pipelines to parse ISO 8601 strings into Dates with explicit format and timezone handling.</p>
'''

ANSWERS[87] = r'''
<p>Index builds on large collections used to lock the database; modern MongoDB (4.4+) defaults to <strong>online index builds</strong> that allow concurrent reads and writes. The trade-off is build time vs. impact &mdash; tuning means controlling memory, parallelism, and timing.</p>

<pre><code>// Default in 4.4+: hybrid build (online, replicates as it builds)
db.orders.createIndex(
  { customerId: 1, createdAt: -1 },
  { name: "orders_cust_date" }
)

// Explicit options for control
db.orders.createIndex(
  { tenantId: 1, status: 1, createdAt: -1 },
  {
    name:                 "orders_tenant_status_date",
    background:           true,        // legacy flag, ignored in modern versions
    commitQuorum:         "majority",  // wait for majority before commit
    expireAfterSeconds:   null         // not a TTL
  }
)

// Track progress
db.currentOp({ "command.createIndexes": { $exists: true } })
//   "msg":           "Index Build: scanning collection",
//   "progress":      { done: 1234567, total: 9876543 },
//   "remainingTime": 6543

// Replica set: the rolling pattern (zero-downtime, controlled impact)
//   1. Stop replication on a secondary, set member hidden
//   2. Build the index foreground (faster) on the standalone
//   3. Resume replication; let it catch up
//   4. Repeat for each secondary
//   5. Step down primary; build on it last</code></pre>

<table><tr><th>Concern</th><th>Mitigation</th></tr>
<tr><td>RAM pressure during build</td><td>Set <code>maxIndexBuildMemoryUsageMegabytes</code>; smaller = slower but safer</td></tr>
<tr><td>Replica lag during build</td><td>Hybrid builds replicate; large collections still cause lag &mdash; use rolling builds</td></tr>
<tr><td>Build interruption</td><td>4.4+ resumes after restart; older versions had to start over</td></tr>
<tr><td>Schedule conflict</td><td>Run during low-traffic windows; use <code>commitQuorum: "majority"</code> for safety</td></tr>
<tr><td>Disk space spike</td><td>Index build needs free space ≈ index size; monitor; abort if low</td></tr>
</table>

<p><strong>Modern best practices:</strong></p>
<ul>
  <li><strong>MongoDB Atlas</strong> handles all of this in the UI &mdash; rolling builds with progress tracking and automatic abort if cluster is unhealthy.</li>
  <li>For very large collections (TB+), build via the <strong>rolling pattern</strong> on each replica member &mdash; foreground build is much faster than online builds.</li>
  <li>Use <strong>partial indexes</strong> (<code>partialFilterExpression</code>) to limit scope and reduce build time.</li>
  <li>Always verify with <code>db.collection.getIndexes()</code> and <code>$indexStats</code> after the build.</li>
</ul>
'''

ANSWERS[88] = r'''
<p><strong><code>$toString</code></strong> coerces values to strings; <strong><code>$toObjectId</code></strong> coerces 24-character hex strings to <code>ObjectId</code>. Both are part of MongoDB&rsquo;s type-conversion family alongside <code>$toInt</code>, <code>$toLong</code>, <code>$toDate</code>, <code>$toBool</code>, <code>$toDecimal</code>, and the more verbose <code>$convert</code>.</p>

<pre><code>// Convert ObjectId to string for client output
db.orders.aggregate([
  { $project: {
      orderId: { $toString: "$_id" },
      customerIdStr: { $toString: "$customerId" },
      createdAtStr:  { $toString: "$createdAt" },
      amountStr:     { $toString: "$amount" }
  }}
])

// Convert hex string to ObjectId for $lookup compatibility
db.events.aggregate([
  { $addFields: { _id: { $toObjectId: "$rawId" } } },
  { $lookup: { from: "users", localField: "_id", foreignField: "_id", as: "user" } }
])

// $convert with explicit error handling
db.records.aggregate([
  { $project: {
      asInt: { $convert: {
        input:   "$rawValue",
        to:      "int",
        onError: -1,
        onNull:  0
      }}
  }}
])

// Migration: legacy string IDs to ObjectId
db.events.updateMany(
  { _id: { $type: "string" } },
  [ { $set: { _id: { $toObjectId: "$_id" } } } ]
)
// Note: _id can&rsquo;t be modified in-place &mdash; need replaceOne or insert+delete</code></pre>

<table><tr><th>Operator</th><th>Source &rarr; target</th></tr>
<tr><td><code>$toString</code></td><td>Any &rarr; string (with type-aware formatting)</td></tr>
<tr><td><code>$toObjectId</code></td><td>24-char hex string &rarr; ObjectId</td></tr>
<tr><td><code>$toInt</code> / <code>$toLong</code></td><td>String / number / decimal &rarr; int</td></tr>
<tr><td><code>$toDate</code></td><td>String (ISO) / number (epoch) / objectId &rarr; Date</td></tr>
<tr><td><code>$toDecimal</code></td><td>For financial precision (Decimal128)</td></tr>
<tr><td><code>$convert</code></td><td>Generic with <code>onError</code>/<code>onNull</code> control</td></tr>
</table>

<p><strong>Production tips:</strong></p>
<ul>
  <li>Use <code>$convert</code> when input might be invalid &mdash; raw conversion operators throw on bad input, which aborts the whole pipeline.</li>
  <li>Always pair migrations with <code>$jsonSchema</code> validators so future inserts maintain types.</li>
  <li>For consistent JSON output to clients, project <code>_id</code> as <code>$toString</code> &mdash; many JSON parsers (older PHP, JS without BSON support) mangle ObjectId.</li>
  <li>Use <strong>MongoDB Extended JSON (EJSON)</strong> for full type-fidelity exports between systems.</li>
</ul>
'''

ANSWERS[89] = r'''
<p><strong><code>$literal</code></strong> wraps a value to prevent it from being interpreted as an aggregation expression &mdash; necessary when a value happens to look like an operator (anything starting with <code>$</code>). <strong><code>$mergeArrays</code></strong> isn&rsquo;t actually a MongoDB operator (a common name confusion); the real one is <strong><code>$concatArrays</code></strong>, with set-family alternatives for deduplication.</p>

<pre><code>// $literal &mdash; prevent expression evaluation
db.users.aggregate([
  { $project: {
      label: { $literal: "$name" }   // returns the literal string "$name"
                                       // (without $literal, this would dereference the field)
  }}
])

// Use case: array of expression-like strings as data
db.metadata.aggregate([
  { $project: {
      operators: { $literal: ["$gt", "$lt", "$eq"] }   // a real array of strings
  }}
])

// $concatArrays &mdash; concatenate arrays (the real "merge")
db.products.aggregate([
  { $project: {
      allTags: { $concatArrays: ["$tagsA", "$tagsB", ["common"]] }
  }}
])

// $setUnion &mdash; concatenate + dedupe
db.products.aggregate([
  { $project: {
      uniqueTags: { $setUnion: ["$tagsA", "$tagsB"] }
  }}
])

// Deep example: combine with $cond for conditional concat
db.users.aggregate([
  { $project: {
      perms: {
        $concatArrays: [
          "$basePermissions",
          { $cond: ["$isAdmin", ["admin", "audit"], []] }
      ]
    }
  }}
])</code></pre>

<table><tr><th>Need</th><th>Operator</th></tr>
<tr><td>Concatenate arrays, allow duplicates</td><td><code>$concatArrays</code></td></tr>
<tr><td>Concatenate + dedupe</td><td><code>$setUnion</code></td></tr>
<tr><td>Common elements only</td><td><code>$setIntersection</code></td></tr>
<tr><td>Difference (A &minus; B)</td><td><code>$setDifference</code></td></tr>
<tr><td>Boolean: same elements?</td><td><code>$setEquals</code></td></tr>
</table>

<p><code>$literal</code> is rarely needed in everyday pipelines &mdash; reach for it when handling user-provided values that might begin with <code>$</code>, or when programmatically constructing pipelines where literal values risk being misinterpreted. For document merging (vs array merging), the right operator is <strong><code>$mergeObjects</code></strong>.</p>
'''

ANSWERS[90] = r'''
<p>The <strong>WiredTiger cache</strong> is MongoDB&rsquo;s primary memory consumer &mdash; it holds compressed data and indexes for fast random access. Tuning means watching cache pressure, sizing it for the working set, and detecting when secondaries fall behind.</p>

<pre><code>// Inspect cache state
db.serverStatus().wiredTiger.cache
//   "bytes currently in the cache":   42_000_000_000
//   "tracked dirty bytes in the cache": 800_000_000
//   "maximum bytes configured":         48_000_000_000
//   "pages requested from the cache":   125_678_900
//   "pages read into cache":            234_567        // disk reads (bad if high)
//   "pages evicted by application threads": 45         // bad: cache pressure
//   "modified pages evicted":           12_345

// Tune cache size in mongod.conf
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 32                # default = (RAM - 1GB) / 2

// Monitor with mongostat
mongostat 5
//   dirty %    used %    qrw    ar|aw
//   2.3        88.5      0|0    1|0
//   - dirty &lt; 5%       &lt;-- healthy
//   - used   &lt; 95%     &lt;-- below high-water mark
//   - qrw    = 0        &lt;-- no queue</code></pre>

<table><tr><th>Symptom</th><th>Cause</th><th>Fix</th></tr>
<tr><td><code>used %</code> at 95%, <code>dirty %</code> climbing</td><td>Eviction can&rsquo;t keep up with writes</td><td>Faster disk; more RAM; throttle writes</td></tr>
<tr><td>High <code>application threads evicting</code></td><td>Cache too small for working set</td><td>Add RAM or scale up; secondary read offload</td></tr>
<tr><td>Many <code>pages read into cache</code></td><td>Working set doesn&rsquo;t fit; cold queries</td><td>Add indexes; project less; cache warming</td></tr>
<tr><td>Cache hit ratio &lt; 95%</td><td>Often missing indexes or under-sized cache</td><td>Atlas Performance Advisor; <code>$indexStats</code></td></tr>
</table>

<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Total index size + active data should fit in cache</strong> &mdash; the working-set rule. Use <code>db.stats()</code> + <code>db.collection.totalIndexSize()</code> to size.</li>
  <li><strong>Don&rsquo;t over-allocate</strong> &mdash; leaving room for OS file cache helps with cold reads.</li>
  <li><strong>Connection memory</strong> isn&rsquo;t in the cache budget &mdash; each connection costs ~1MB; bound the pool.</li>
  <li><strong>Atlas dashboards</strong> show cache utilization, eviction, and hit rates directly &mdash; enable alerts on cache pressure.</li>
  <li>Self-hosted: <strong>Percona PMM</strong> or <strong>Datadog</strong> with the MongoDB integration provide the same visibility.</li>
</ul>
'''

ANSWERS[91] = r'''
<p><strong><code>$switch</code></strong> is the multi-way conditional &mdash; like a chained if/else &mdash; and <strong><code>$let</code></strong> defines local variables for use in a sub-expression. They&rsquo;re the workhorses for keeping complex pipeline expressions readable.</p>

<pre><code>// $switch &mdash; multi-branch classification
db.users.aggregate([
  { $project: {
      tier: {
        $switch: {
          branches: [
            { case: { $gte: ["$totalSpent", 10000] }, then: "platinum" },
            { case: { $gte: ["$totalSpent", 5000]  }, then: "gold"     },
            { case: { $gte: ["$totalSpent", 1000]  }, then: "silver"   }
          ],
          default: "bronze"            // required &mdash; otherwise no-match throws
        }
      }
  }}
])

// $let &mdash; reuse intermediate values
db.orders.aggregate([
  { $project: {
      finalPrice: {
        $let: {
          vars: {
            subtotal:    { $sum: "$lineItems.price" },
            taxRate:     { $cond: ["$isExempt", 0, 0.18] }
          },
          in: {
            $multiply: [
              "$$subtotal",
              { $add: [1, "$$taxRate"] }
            ]
          }
        }
      }
  }}
])

// Combine: $let + $switch for layered logic
db.orders.aggregate([
  { $project: {
      shippingPrice: {
        $let: {
          vars: { weight: "$totalWeight", expedite: "$expedite" },
          in: {
            $switch: {
              branches: [
                { case: { $and: ["$$expedite", { $gt: ["$$weight", 10] }] }, then: 50 },
                { case: "$$expedite", then: 25 },
                { case: { $gt: ["$$weight", 10] }, then: 15 }
              ],
              default: 5
            }
          }
        }
      }
  }}
])</code></pre>

<table><tr><th>Operator</th><th>Use when</th></tr>
<tr><td><code>$cond</code></td><td>Two branches (if/then/else)</td></tr>
<tr><td><code>$switch</code></td><td>Three or more branches</td></tr>
<tr><td><code>$let</code></td><td>Computed value used 2+ times in a sub-expression</td></tr>
<tr><td><code>$ifNull</code></td><td>Default for missing/null fields</td></tr>
</table>

<p><strong>Why <code>$switch</code> matters:</strong> nested <code>$cond</code> becomes unreadable after two levels. <code>$switch</code> is flatter and easier to maintain. <strong>Why <code>$let</code> matters:</strong> without it, you&rsquo;d recompute the same expression in every branch &mdash; both slower and harder to keep in sync.</p>

<p>Variables in <code>$let</code> are referenced as <code>$$varName</code> (double-dollar). System variables share the same syntax: <code>$$ROOT</code>, <code>$$NOW</code>, <code>$$REMOVE</code>.</p>
'''

ANSWERS[92] = r'''
<p>Multi-region MongoDB deployments balance <strong>latency</strong>, <strong>availability</strong>, and <strong>data sovereignty</strong>. The patterns: replicas across regions for DR, geo-zoned shards for sovereignty, or active-active via change streams for true multi-region writes.</p>

<table><tr><th>Pattern</th><th>Latency</th><th>Use case</th></tr>
<tr><td><strong>Single primary + cross-region secondaries</strong></td><td>Local reads fast; writes incur cross-region RTT</td><td>DR; majority of users in one region</td></tr>
<tr><td><strong>Geo-zoned sharding</strong></td><td>Local reads + writes for regional data</td><td>Data sovereignty (GDPR per-EU, CCPA per-CA)</td></tr>
<tr><td><strong>Atlas Global Clusters</strong></td><td>Local reads/writes per zone with automatic routing</td><td>Global SaaS with regional users</td></tr>
<tr><td><strong>Active-active via change streams</strong></td><td>Local writes everywhere; eventual consistency</td><td>Read-heavy workloads with low conflict</td></tr>
</table>

<pre><code>// Atlas Global Cluster &mdash; configure zones in the UI
//   - Zone "us-east": primary in us-east-1, secondaries in us-east-2, us-west-2
//   - Zone "eu-central": primary in eu-central-1, secondaries in eu-west-1
//   - Documents tagged with `country` route to the right zone

sh.shardCollection("appdb.users", { country: 1, _id: 1 })

sh.addShardToZone("shard-us-east-1", "US")
sh.addShardToZone("shard-eu-central-1", "EU")

sh.updateZoneKeyRange("appdb.users",
  { country: "US", _id: MinKey }, { country: "US", _id: MaxKey }, "US")
sh.updateZoneKeyRange("appdb.users",
  { country: "DE", _id: MinKey }, { country: "DE", _id: MaxKey }, "EU")

// Application-side routing
const collection = client.db("appdb").collection("users")
collection.findOne({ _id: userId, country: "DE" })   // routed to EU shard

// Read preference for cross-region reads
collection.find({ ... }).readPreference(
  "nearest",   // or "secondary"
  { tags: [{ region: "us-east" }] }
)</code></pre>

<p><strong>Trade-offs to manage:</strong></p>
<ul>
  <li><strong>Write concern</strong>: <code>w: "majority"</code> across regions = high-latency writes. Use region-local majorities (<code>tagSets</code>) when possible.</li>
  <li><strong>Failover scope</strong>: regional outage shouldn&rsquo;t require cross-region reconfiguration &mdash; design for it.</li>
  <li><strong>Cost</strong>: cross-region traffic is expensive. Atlas Global Clusters keep most reads regional.</li>
  <li><strong>Compliance</strong>: pinning data to a region (data residency) requires shard zones + careful query patterns &mdash; verify with auditing.</li>
</ul>

<p><strong>Modern stack:</strong> <strong>MongoDB Atlas Global Clusters</strong> on AWS, GCP, or Azure handle most of the operational complexity. Self-hosted multi-region needs careful network setup (VPC peering, low-latency links) and is rarely worth the effort outside specific sovereignty cases.</p>
'''

ANSWERS[93] = r'''
<p>A <strong>TTL index</strong> auto-deletes documents whose date field is older than a configured threshold. It&rsquo;s the standard pattern for sessions, tokens, ephemeral logs, and cache-like data &mdash; MongoDB runs a background TTL monitor every 60 seconds.</p>

<pre><code>// Auto-delete documents 24 hours after createdAt
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 86400 }   // 24 hours
)

// Pin to a calculated future expiry per-document
//   set the field to the expiration moment, expireAfterSeconds: 0
db.invitations.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 })
db.invitations.insertOne({
  email: "alice@example.com",
  expiresAt: new Date(Date.now() + 7 * 24 * 3600 * 1000)   // 7 days
})

// Drop &amp; recreate to change the duration
db.sessions.dropIndex("createdAt_1")
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })

// Combine with partial filter for selective TTL
db.events.createIndex(
  { processedAt: 1 },
  { expireAfterSeconds: 86400, partialFilterExpression: { archive: false } }
)</code></pre>

<table><tr><th>Behavior</th><th>Detail</th></tr>
<tr><td>Eviction granularity</td><td>Background process runs every 60 seconds &mdash; not real-time</td></tr>
<tr><td>Timezone</td><td>UTC always &mdash; the document field must be a Date</td></tr>
<tr><td>Single TTL index per field</td><td>One per field; <code>expireAfterSeconds</code> applies to that field</td></tr>
<tr><td>Compound TTL</td><td>Not supported &mdash; only the leading field can be TTL-controlled</td></tr>
<tr><td>Sharded</td><td>Works on sharded collections; deletion happens on each shard&rsquo;s primary</td></tr>
<tr><td>Replica behavior</td><td>Primary deletes; secondaries replicate the deletes</td></tr>
</table>

<p><strong>Common patterns:</strong></p>
<ul>
  <li><strong>Sessions / refresh tokens</strong>: TTL of 24h-7d.</li>
  <li><strong>Verification codes</strong>: TTL of 5-15 minutes.</li>
  <li><strong>Audit logs (short-term)</strong>: TTL of 30-90 days; archive older to cold storage.</li>
  <li><strong>Cache-like collections</strong>: TTL of seconds to minutes &mdash; though Redis is usually better.</li>
  <li><strong>GDPR retention</strong>: TTL aligned with retention policy (auto-erasure after N years).</li>
</ul>

<p><strong>Modern alternatives:</strong> for high-volume ephemeral data, <strong>Redis</strong> with native TTL is faster and cheaper. For time-series with retention windows, <strong>time-series collections</strong> (5.0+) have built-in expiry. TTL indexes are right for &ldquo;data that should disappear&rdquo; in normal collections.</p>
'''

ANSWERS[94] = r'''
<p><strong>Initial sync</strong> is the process by which a new replica-set member copies the entire dataset from a peer. It&rsquo;s safe but slow on large data &mdash; the bottleneck is usually network bandwidth or sustained disk write throughput on the new member.</p>

<pre><code>// New member joins; mongod starts initial sync automatically
//   1. Clone all collections from a sync source
//   2. Apply oplog entries that arrived during step 1
//   3. Build indexes
//   4. Apply any further oplog entries
//   5. Transition to SECONDARY

// Monitor progress
rs.status()
//   "members": [
//     {
//       "_id": 2,
//       "stateStr": "STARTUP2",
//       "infoMessage": "could not find member to sync from",
//       "initialSyncStatus": {
//         "totalInitialSyncElapsedMillis": 84000,
//         "remainingInitialSyncEstimatedMillis": 720000,
//         "approxTotalDataSize": 524288000000,    // 500 GB
//         "appliedOps": 1234,
//         "fetchedMissingDocs": 0
//       }
//     }
//   ]</code></pre>

<table><tr><th>Bottleneck</th><th>Mitigation</th></tr>
<tr><td>Network bandwidth</td><td>Use same-AZ peers; faster instance class; reduce concurrent traffic</td></tr>
<tr><td>Disk write speed</td><td>NVMe SSDs; faster EBS class (io2 vs gp2); avoid HDDs</td></tr>
<tr><td>Oplog overflow during sync</td><td>Increase oplog size <em>before</em> starting sync</td></tr>
<tr><td>Failure mid-sync</td><td>Re-starts from scratch by default; use file-system seed instead</td></tr>
<tr><td>Index build time</td><td>Indexes built sequentially after data clone; long collections delay completion</td></tr>
</table>

<p><strong>Faster alternatives for large data:</strong></p>
<ul>
  <li><strong>Filesystem seed</strong>: snapshot a healthy member&rsquo;s data directory, restore onto the new host, start mongod &mdash; it catches up via oplog only. Far faster than full initial sync; the recommended pattern for TB-scale data.</li>
  <li><strong>Logical initial sync (4.4+)</strong>: streams data from source via oplog tailable cursor; faster than the older block-based approach.</li>
  <li><strong>Atlas Live Migration</strong> and <strong>Cluster-to-Cluster Sync</strong>: managed tools for cross-cluster data moves with continuous updates until cutover.</li>
</ul>

<p><strong>Capacity planning:</strong> ensure the <strong>oplog window</strong> on the source is at least 2-3x the expected sync duration. If the oplog rolls over before sync completes, the new member errors out and starts over. Atlas auto-sizes oplog; self-hosted should set <code>storage.oplogSizeMB</code> generously (e.g., 100 GB on busy clusters).</p>
'''

ANSWERS[95] = r'''
<p><strong><code>db.currentOp()</code></strong> returns information about <strong>operations currently running</strong> on the server &mdash; queries, commands, index builds, replication, internal tasks. It&rsquo;s the first place to look when investigating slow performance, hung queries, or runaway operations.</p>

<pre><code>// Show all running operations
db.currentOp()

// Filter to operations running for 5+ seconds
db.currentOp({ "secs_running": { $gte: 5 } })

// Aggregation form (more flexible filtering, supports $match)
db.currentOp().inprog.filter(op =&gt; op.secs_running &gt; 5)

// Or via $currentOp aggregation stage
db.aggregate([
  { $currentOp: { allUsers: true, idleConnections: false } },
  { $match: {
      secs_running: { $gte: 5 },
      "command.aggregate": { $exists: true }
  }}
])

// Each operation document includes:
{
  opid:           29345,                  // pass to killOp()
  client:         "10.0.1.5:54321",
  secs_running:   12,
  microsecs_running: 12_345_678,
  op:             "command",              // query, insert, update, getmore, command
  ns:             "appdb.orders",
  command:        { aggregate: "orders", pipeline: [...] },
  planSummary:    "IXSCAN { customerId: 1 }",
  numYields:      123,
  locks:          { Global: "r", Database: "r", Collection: "r" }
}

// Kill a runaway operation
db.killOp(29345)

// Kill all aggregations running &gt; 60 seconds (use carefully)
db.currentOp({ "secs_running": { $gt: 60 }, "op": "command" })
  .inprog.forEach(op =&gt; db.killOp(op.opid))</code></pre>

<table><tr><th>Field</th><th>Use it for</th></tr>
<tr><td><code>secs_running</code></td><td>Long-running queries</td></tr>
<tr><td><code>planSummary</code></td><td>Detect missing-index COLLSCAN</td></tr>
<tr><td><code>numYields</code></td><td>High = giving up the lock often (probably blocked on I/O)</td></tr>
<tr><td><code>waitingForLatch</code></td><td>Identify lock contention</td></tr>
<tr><td><code>command</code></td><td>Reproduce and tune the query</td></tr>
</table>

<p><strong>Production usage:</strong></p>
<ul>
  <li><strong>Always set <code>maxTimeMS</code></strong> on application queries &mdash; bounds query lifetime and avoids needing manual <code>killOp</code>.</li>
  <li><strong>Schedule periodic checks</strong> for queries running &gt; threshold; auto-kill or alert.</li>
  <li><strong>Atlas Real-Time Performance Panel</strong> shows the same data graphically.</li>
  <li><strong>Datadog</strong>, <strong>New Relic</strong>, <strong>Honeycomb</strong> integrate <code>$currentOp</code> data into APM dashboards.</li>
  <li>For replica members, check operations on each one &mdash; secondaries serve reads if you&rsquo;ve set <code>readPreference</code>.</li>
</ul>
'''

ANSWERS[96] = r'''
<p><strong><code>$year</code></strong>, <strong><code>$month</code></strong>, and <strong><code>$dayOfMonth</code></strong> extract Gregorian calendar components from a Date. They&rsquo;re aggregation expressions, usable in any stage that accepts expressions: <code>$project</code>, <code>$group</code>, <code>$match</code> (via <code>$expr</code>).</p>

<pre><code>// Decompose a Date for grouping or display
db.orders.aggregate([
  { $project: {
      year:  { $year:        "$createdAt" },
      month: { $month:       "$createdAt" },
      day:   { $dayOfMonth:  "$createdAt" },
      hour:  { $hour:        "$createdAt" },
      dow:   { $dayOfWeek:   "$createdAt" },     // 1=Sunday, 7=Saturday
      doy:   { $dayOfYear:   "$createdAt" }      // 1-366
  }}
])

// Group revenue by month
db.orders.aggregate([
  { $group: {
      _id: {
        year:  { $year:  "$createdAt" },
        month: { $month: "$createdAt" }
      },
      revenue: { $sum: "$amount" }
  }},
  { $sort: { "_id.year": 1, "_id.month": 1 } }
])

// Filter by year (cleaner than range query when storing whole-day timestamps)
db.orders.find({
  $expr: { $eq: [{ $year: "$createdAt" }, 2026] }
})

// Timezone-aware extraction (essential for user-facing analytics)
db.orders.aggregate([
  { $project: {
      year:  { $year:  { date: "$createdAt", timezone: "Asia/Kolkata" } },
      month: { $month: { date: "$createdAt", timezone: "Asia/Kolkata" } }
  }}
])</code></pre>

<table><tr><th>Operator</th><th>Returns</th></tr>
<tr><td><code>$year</code></td><td>4-digit calendar year</td></tr>
<tr><td><code>$month</code></td><td>1-12</td></tr>
<tr><td><code>$dayOfMonth</code></td><td>1-31</td></tr>
<tr><td><code>$dayOfWeek</code></td><td>1=Sun, 7=Sat (US)</td></tr>
<tr><td><code>$isoDayOfWeek</code></td><td>1=Mon, 7=Sun (ISO)</td></tr>
<tr><td><code>$dayOfYear</code></td><td>1-366</td></tr>
<tr><td><code>$hour</code>, <code>$minute</code>, <code>$second</code>, <code>$millisecond</code></td><td>Time components</td></tr>
</table>

<p><strong>Modern preference (5.0+):</strong> for time-bucketing, use <strong><code>$dateTrunc</code></strong> instead of decomposing-and-rebuilding. <code>$dateTrunc</code> handles calendar quirks (varying month lengths, leap years, DST) and timezone correctly:</p>

<pre><code>// Better: truncate to month directly
db.orders.aggregate([
  { $group: {
      _id: { $dateTrunc: { date: "$createdAt", unit: "month", timezone: "Asia/Kolkata" } },
      revenue: { $sum: "$amount" }
  }}
])</code></pre>

<p>Performance: filter expressions using these operators (<code>{ $expr: { $eq: [{ $year: "$createdAt" }, 2026] } }</code>) usually <em>can&rsquo;t use indexes</em> &mdash; MongoDB has to evaluate the expression for every document. For range filters, prefer literal Date comparisons against an indexed field.</p>
'''

ANSWERS[97] = r'''
<p>The <strong>oplog</strong> is a capped collection (<code>local.oplog.rs</code>) that records every write operation on the primary; secondaries tail it to replicate. Sizing and monitoring the oplog is critical: too small and replicas can&rsquo;t catch up after a brief disconnection; too large and storage fills up.</p>

<pre><code>// Inspect current oplog stats
rs.printReplicationInfo()
//   configured oplog size:  102400MB
//   log length start to end: 86400secs (24hrs)        &lt;-- the "oplog window"
//   oplog first event time: ...
//   oplog last event time:  ...

// Or programmatically
db.getReplicationInfo()
db.printSecondaryReplicationInfo()    // syncedTo + lag per secondary

// Resize the oplog (4.0+, online operation)
db.adminCommand({ replSetResizeOplog: 1, size: 16384 })   // 16 GB

// Larger oplog allows wider window &mdash; secondary can be down longer without re-sync
storage:
  oplogSizeMB: 102400         # 100 GB</code></pre>

<table><tr><th>Symptom</th><th>Cause</th><th>Fix</th></tr>
<tr><td>Secondary stuck at <code>RECOVERING</code></td><td>Oplog window smaller than secondary&rsquo;s downtime</td><td>Initial sync from another peer; resize oplog larger</td></tr>
<tr><td>Window shrinking under load</td><td>Write rate increased</td><td>Resize oplog; consider sharding</td></tr>
<tr><td>Disk filling fast</td><td>Oversized oplog or runaway writes</td><td>Resize down (reads window will shrink); investigate write source</td></tr>
<tr><td>Replication lag &gt; 5s consistently</td><td>Secondary disk/CPU bottleneck or net latency</td><td>Faster hardware; tune RAID; check network</td></tr>
</table>

<p><strong>Sizing guidance:</strong></p>
<ul>
  <li><strong>Default</strong>: 5% of free disk space, capped at 50GB. Often too small.</li>
  <li><strong>High-volume clusters</strong>: 24-72 hour window so a downed member can rejoin without resync. Calculate as <code>peak write rate &times; oplog overhead &times; window</code>.</li>
  <li><strong>Atlas auto-sizes</strong> based on cluster tier &mdash; you don&rsquo;t need to manage it manually.</li>
  <li>Monitor <strong>oplog window</strong> as a key SRE metric; alert when it drops below 1.5x the longest expected downtime.</li>
</ul>

<p><strong>Operational notes:</strong></p>
<ul>
  <li>The oplog also serves <strong>change streams</strong> &mdash; an empty oplog window breaks change-stream consumers, who must restart from a full snapshot.</li>
  <li>For <strong>point-in-time recovery</strong>, oplog backups (Atlas Backup, mongodump --oplog) capture the rolling window so you can restore to any second.</li>
  <li>Tools: <strong>mongostat</strong> shows oplog throughput; <strong>Atlas</strong> + <strong>Percona PMM</strong> graph oplog window over time.</li>
</ul>
'''

ANSWERS[98] = r'''
<p><strong>Field-Level Encryption (FLE)</strong> encrypts specific fields client-side <em>before</em> writes hit the database, so the server never sees plaintext. <strong>Queryable Encryption (QE)</strong> (GA in 7.0+) extends FLE so you can run equality and range queries on encrypted fields without decrypting them server-side.</p>

<pre><code>// Configure CSFLE (Client-Side Field-Level Encryption) in driver
const { MongoClient, ClientEncryption } = require("mongodb")

const kmsProviders = {
  aws: {
    accessKeyId:     process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  }
  // Or: azure, gcp, kmip, local
}

const schemaMap = {
  "appdb.users": {
    bsonType: "object",
    encryptMetadata: { keyId: [keyId] },
    properties: {
      ssn:        { encrypt: { bsonType: "string", algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic" } },
      medicalNote:{ encrypt: { bsonType: "string", algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Random" } }
    }
  }
}

const client = new MongoClient(uri, {
  autoEncryption: { keyVaultNamespace: "encryption.__keyVault", kmsProviders, schemaMap }
})

// Now writes encrypt automatically
await users.insertOne({ name: "Alice", ssn: "123-45-6789" })
// Server stores ssn as binary ciphertext; queries on ssn (deterministic) still work

// Queryable Encryption (7.0+) &mdash; range queries on encrypted fields
const encryptedFieldsMap = {
  "appdb.users": {
    fields: [
      { path: "ssn",      bsonType: "string", queries: { queryType: "equality" } },
      { path: "salary",   bsonType: "int",    queries: { queryType: "range", min: 0, max: 1_000_000 } }
    ]
  }
}
// Now you can do: users.find({ salary: { $gte: 100000, $lte: 200000 } })
//   The driver runs the query against encrypted indexes server-side</code></pre>

<table><tr><th>Encryption type</th><th>Algorithm</th><th>Capability</th></tr>
<tr><td>Deterministic</td><td>AES-256-CBC + HMAC</td><td>Equality queries; same plaintext &rarr; same ciphertext</td></tr>
<tr><td>Randomized</td><td>AES-256-CBC + HMAC + IV</td><td>No queries; max security</td></tr>
<tr><td>Queryable Equality (7.0+)</td><td>Encrypted indexes</td><td>$eq, $in queries server-side</td></tr>
<tr><td>Queryable Range (7.0+)</td><td>Order-revealing encryption</td><td>$gt, $lt, $gte, $lte queries</td></tr>
</table>

<p><strong>Key management:</strong> the encryption key never reaches the MongoDB server. Use <strong>AWS KMS</strong>, <strong>GCP KMS</strong>, <strong>Azure Key Vault</strong>, <strong>HashiCorp Vault</strong>, or <strong>KMIP</strong>-compatible HSMs. For development, a local key file works but is unsuitable for production.</p>

<p><strong>Use cases:</strong> PCI-DSS compliance (card data), HIPAA (PHI), GDPR (PII for EU users), zero-trust architectures where the DBA shouldn&rsquo;t see sensitive data. <strong>Atlas</strong> integrates with cloud KMS providers in a few clicks. Alternatives include <strong>Vault Transit</strong>, <strong>CipherStash</strong>, <strong>Skyflow</strong>, <strong>Basis Theory</strong>, and <strong>VGS</strong> for tokenization at the application layer.</p>
'''

ANSWERS[99] = r'''
<p>Both operate on geospatial indexes (<code>2dsphere</code>), but they answer different questions: <strong><code>$geoNear</code></strong> ranks documents by distance from a point and adds a distance field; <strong><code>$geoWithin</code></strong> filters documents whose geometry lies inside a given shape, with no distance calculation.</p>

<table><tr><th>Operator</th><th>Returns</th><th>Sorts by distance?</th><th>Use case</th></tr>
<tr><td><code>$geoNear</code></td><td>Documents + distance field</td><td>Yes (always)</td><td>&ldquo;Find the closest 10 stores&rdquo;</td></tr>
<tr><td><code>$geoWithin</code></td><td>Documents inside polygon/circle/box</td><td>No</td><td>&ldquo;All hospitals in Bangalore&rdquo;</td></tr>
<tr><td><code>$geoIntersects</code></td><td>Documents whose geometry intersects target</td><td>No</td><td>&ldquo;Roads crossing this district&rdquo;</td></tr>
<tr><td><code>$near</code> / <code>$nearSphere</code></td><td>Like <code>$geoNear</code> in find queries</td><td>Yes</td><td>Simpler nearest queries outside aggregation</td></tr>
</table>

<pre><code>// Setup: 2dsphere index
db.places.createIndex({ location: "2dsphere" })

// $geoNear &mdash; must be the FIRST aggregation stage; computes distance
db.places.aggregate([
  { $geoNear: {
      near: { type: "Point", coordinates: [77.5946, 12.9716] },     // [lng, lat]
      distanceField: "distance_meters",
      maxDistance: 5000,
      query: { category: "cafe" },                                    // optional pre-filter
      spherical: true
  }},
  { $limit: 10 }
])
// Result includes distance_meters; documents already sorted by it

// $geoWithin &mdash; no distance, just inside-the-shape
db.places.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [[ [77.5,12.9], [77.7,12.9], [77.7,13.0], [77.5,13.0], [77.5,12.9] ]]
      }
    }
  }
})

// $geoWithin with circle (center + radius in radians)
db.places.find({
  location: {
    $geoWithin: { $centerSphere: [[77.5946, 12.9716], 5 / 6378.1] }   // 5 km
  }
})</code></pre>

<p><strong>Performance and scale:</strong></p>
<ul>
  <li>Both require a <code>2dsphere</code> index on the geo field. Always store coordinates as <code>[longitude, latitude]</code> (a common bug source).</li>
  <li><code>$geoNear</code> is more expensive: it computes distance for every candidate; bound with <code>maxDistance</code> and a <code>query</code> filter.</li>
  <li>For very large datasets (millions of points), specialized geo databases scale better: <strong>PostGIS</strong>, <strong>Tile38</strong>, <strong>H3</strong> (Uber&rsquo;s hexagonal grid), <strong>Elasticsearch geo queries</strong>.</li>
  <li>For maps, <strong>Mapbox</strong>, <strong>MapTiler</strong>, <strong>Google Maps Platform</strong>, and <strong>HERE</strong> handle rendering and routing on top of MongoDB-stored data.</li>
</ul>
'''

ANSWERS[100] = r'''
<p>An aggregation finishing with <strong><code>$merge</code></strong> persists pipeline output incrementally; <strong><code>$setUnion</code></strong> deduplicates and combines arrays inside an expression. They&rsquo;re commonly paired in ETL pipelines: <code>$setUnion</code> consolidates per-document arrays during projection, then <code>$merge</code> persists the result.</p>

<pre><code>// Example: maintain a per-author "all genres ever published" list
//   Refresh nightly into an "author_summary" collection

db.books.aggregate([
  // Aggregate per author
  { $group: {
      _id: "$author",
      // Collect every genres array from every book
      allGenresNested: { $push: "$genres" }
  }},
  // Flatten + dedupe with $setUnion + $reduce
  { $project: {
      genres: {
        $reduce: {
          input:        "$allGenresNested",
          initialValue: [],
          in:           { $setUnion: ["$$value", "$$this"] }
      }
    },
      lastUpdated: "$$NOW"
  }},
  // Persist incrementally
  { $merge: {
      into:           "author_summary",
      on:             "_id",
      whenMatched:    "replace",
      whenNotMatched: "insert"
  }}
])

// Other set-family expressions used alongside $merge ETL
//   $setIntersection &mdash; common elements across input arrays
//   $setDifference   &mdash; A &minus; B
//   $setEquals       &mdash; boolean: same elements?
//   $setIsSubset     &mdash; boolean: A subset of B?

// Combine $setUnion with $facet for incremental analytics
db.events.aggregate([
  { $match: { ts: { $gte: lastRunTime } } },           // delta only
  { $facet: {
      uniqueUsersByDay: [
        { $group: {
            _id: { day: { $dateTrunc: { date: "$ts", unit: "day" } } },
            users: { $addToSet: "$userId" }
        }},
        { $project: { day: "$_id.day", uniqueCount: { $size: "$users" } } }
      ],
      topPaths: [
        { $group: { _id: "$path", count: { $sum: 1 } } },
        { $sort:  { count: -1 } },
        { $limit: 100 }
      ]
  }},
  { $merge: {
      into: "daily_metrics",
      on:   "day",
      whenMatched: [
        { $set: {
            uniqueCount: { $add: ["$uniqueCount", "$$new.uniqueCount"] }
        }}
      ],
      whenNotMatched: "insert"
  }}
])</code></pre>

<table><tr><th>Stage / operator</th><th>Role in ETL</th></tr>
<tr><td><code>$match</code></td><td>Delta filter (only new documents since last run)</td></tr>
<tr><td><code>$group</code> + <code>$addToSet</code> / <code>$setUnion</code></td><td>Aggregate without duplicates</td></tr>
<tr><td><code>$reduce</code></td><td>Fold per-document arrays into a single deduped collection</td></tr>
<tr><td><code>$merge</code></td><td>Incremental upsert into the materialized view</td></tr>
<tr><td><code>whenMatched: [...]</code></td><td>Custom merge logic referencing <code>$$new</code></td></tr>
</table>

<p><strong>Production pattern:</strong> schedule pipelines via cron / <strong>BullMQ</strong> / <strong>Inngest</strong> / <strong>Trigger.dev</strong> / <strong>Temporal</strong>; checkpoint <code>lastRunTime</code> in a metadata collection; use <code>$merge</code> with idempotent semantics so re-running covers gaps. For very large or cross-system pipelines, push to <strong>Airbyte</strong>, <strong>Fivetran</strong>, or <strong>Estuary</strong> &mdash; they handle change-data-capture and warehouse loads (<strong>BigQuery</strong>, <strong>Snowflake</strong>, <strong>Databricks</strong>, <strong>ClickHouse</strong>) with managed reliability.</p>
'''
