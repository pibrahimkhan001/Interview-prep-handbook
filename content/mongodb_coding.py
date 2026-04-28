"""Detailed answers for MongoDB Coding interview questions.

Each ANSWERS[n] is an HTML string suitable for embedding inside a chapter page.
Style: runnable mongosh/Node.js snippet, brief lead-in, notes & variants.
"""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''
<pre><code>// MongoDB shell (mongosh) &mdash; databases are created lazily
use library          // switches to the &ldquo;library&rdquo; database

// At this point, the database is NOT yet on disk
show dbs             // library will not appear

// Inserting any document creates the database physically
db.books.insertOne({ title: "MongoDB Basics" })

show dbs             // library now appears

// Node.js driver
const { MongoClient } = require("mongodb");
const client = new MongoClient("mongodb://localhost:27017");
await client.connect();
const db = client.db("library");          // implicitly created on first write
await db.collection("books").insertOne({ title: "MongoDB Basics" });</code></pre>

<p>Unlike SQL, MongoDB has <strong>no <code>CREATE DATABASE</code> statement</strong> &mdash; databases are created on demand when the first document is written. The <code>use</code> command in the shell only switches the &ldquo;current database&rdquo; pointer; it doesn&rsquo;t persist anything until you write data.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>Database names are <strong>case-sensitive on Linux/macOS</strong> but not on Windows. Stick to lowercase to avoid cross-platform bugs.</li>
  <li>Reserved system DBs (<code>admin</code>, <code>local</code>, <code>config</code>) cannot be used as application database names.</li>
  <li>To delete the database later: <code>db.dropDatabase()</code> while connected to it.</li>
  <li>In MongoDB Atlas, databases are visible in the cluster UI as soon as the first write lands.</li>
  <li>Naming rules: max 64 characters, no spaces, no <code>/ \ . " * &lt; &gt; : | ? $</code>, and not the empty string.</li>
</ul>
'''

ANSWERS[2] = r'''
<pre><code>use library

// Implicit creation (most common): the collection is created on first write
db.books.insertOne({ title: "MongoDB Basics" })

// Explicit creation with options
db.createCollection("books")

// Explicit with validation, capped, or collation options
db.createCollection("books", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "author"],
      properties: {
        title:          { bsonType: "string", minLength: 1 },
        author:         { bsonType: "string", minLength: 1 },
        published_year: { bsonType: "int", minimum: 1500, maximum: 2100 }
      }
    }
  },
  validationLevel: "moderate",      // moderate validates updates only on docs that already passed
  validationAction: "error"         // reject inserts/updates that fail
})</code></pre>

<p>Most code paths use <strong>implicit creation</strong> &mdash; just insert into the collection and MongoDB creates it automatically with default settings. Use <strong>explicit creation</strong> when you need options at create time: schema validation, capped/time-series collections, custom collation, or pre-existing indexes.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>Collection names share a database&rsquo;s namespace and must be unique within it.</li>
  <li>Avoid names starting with <code>system.</code> &mdash; that prefix is reserved.</li>
  <li>For high-volume log/event data, consider <code>{ timeseries: { timeField: "ts" } }</code> (5.0+) for automatic bucketing.</li>
  <li>Schema validation is enforced by the server, not the driver &mdash; bad data is rejected even from <code>mongosh</code>.</li>
  <li>To rename a collection later: <code>db.books.renameCollection("library_books")</code>.</li>
</ul>
'''

ANSWERS[3] = r'''
<pre><code>// Single document
db.books.insertOne({
  title: "MongoDB Basics",
  author: "John Doe",
  published_year: 2023
})

// Multiple documents at once (batch is far faster)
db.books.insertMany([
  { title: "MongoDB Basics",      author: "John Doe",  published_year: 2023 },
  { title: "Advanced MongoDB",    author: "Jane Doe",  published_year: 2024 },
  { title: "Aggregation Pipeline", author: "John Doe", published_year: 2025 }
])

// Inspect the result
const r = db.books.insertOne({ title: "X", author: "Y", published_year: 2025 });
print(r.insertedId);       // ObjectId of the new document

// Node.js driver, identical API
await db.collection("books").insertOne({
  title: "MongoDB Basics", author: "John Doe", published_year: 2023
});</code></pre>

<p>The <code>insertOne</code> and <code>insertMany</code> methods accept plain JavaScript objects. MongoDB auto-generates an <code>_id</code> field of type <code>ObjectId</code> if you don&rsquo;t supply one.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>The result includes <code>insertedId</code> (or <code>insertedIds</code>) so the client can chain follow-up operations.</li>
  <li>For batches, <code>{ ordered: false }</code> continues past per-document errors and runs faster: <code>insertMany(docs, { ordered: false })</code>.</li>
  <li><strong>Type matters</strong> &mdash; <code>published_year: 2023</code> stored as a JS Number ends up as a BSON Double in older drivers; use <code>NumberInt(2023)</code> in <code>mongosh</code> if you specifically want a 32-bit int (matters for some validators and aggregations).</li>
  <li>Insert duplicates of <code>_id</code> raise a <code>DuplicateKey</code> error (code <code>11000</code>) &mdash; catch it explicitly in app code.</li>
  <li>For 100k+ rows at once, split into batches of ~1000 to keep individual operations under the 16 MB BSON limit and to allow checkpointing.</li>
</ul>
'''

ANSWERS[4] = r'''
<pre><code>// Update one specific book by title
db.books.updateOne(
  { title: "MongoDB Basics" },
  { $set: { published_year: 2025 } }
)

// More precise: by ObjectId (avoids accidentally matching the wrong book)
db.books.updateOne(
  { _id: ObjectId("66243abf2c1f8e1234567890") },
  { $set: { published_year: 2025 } }
)

// Multiple fields at once
db.books.updateOne(
  { title: "MongoDB Basics" },
  { $set: { published_year: 2025, edition: 2, last_revised: new Date() } }
)

// Upsert &mdash; insert if no match, update if found
db.books.updateOne(
  { title: "MongoDB Basics" },
  { $set: { published_year: 2025 } },
  { upsert: true }
)</code></pre>

<p>The <code>$set</code> operator is the workhorse: it changes the named fields and leaves the rest of the document intact. Without <code>$set</code> the supplied object would <em>replace</em> the entire document &mdash; a frequent beginner trap.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Filter on a unique field</strong> (<code>_id</code> or a unique-indexed field) for &ldquo;update one&rdquo; semantics. Title alone may match multiple books.</li>
  <li>The result returns <code>matchedCount</code> and <code>modifiedCount</code>. If the new value equals the old, <code>modifiedCount</code> is 0 even though <code>matchedCount</code> is 1 &mdash; this is normal.</li>
  <li>To set a field only on insert (during upsert), use <code>$setOnInsert</code> alongside <code>$set</code>: <code>{ $set: { published_year: 2025 }, $setOnInsert: { created_at: new Date() } }</code>.</li>
  <li>For complex updates, use the <strong>aggregation-pipeline form</strong>: <code>updateOne(filter, [{ $set: {...} }, { $unset: [...] }])</code>.</li>
  <li><code>findOneAndUpdate()</code> is the variant that returns the updated document (or the original) &mdash; useful for read-modify patterns.</li>
</ul>
'''

ANSWERS[5] = r'''
<pre><code>// Delete one matching book
db.books.deleteOne({ title: "MongoDB Basics" })

// Returns: { acknowledged: true, deletedCount: 1 } or deletedCount: 0

// More precise &mdash; delete by ObjectId
db.books.deleteOne({ _id: ObjectId("66243abf2c1f8e1234567890") })

// Delete every book with that title (if titles aren&rsquo;t unique)
db.books.deleteMany({ title: "MongoDB Basics" })

// Soft-delete pattern (preferred for production)
db.books.updateOne(
  { title: "MongoDB Basics" },
  { $set: { deleted: true, deleted_at: new Date() } }
)
// Then exclude soft-deleted in normal queries:
db.books.find({ deleted: { $ne: true } })</code></pre>

<p><code>deleteOne</code> removes the <strong>first</strong> document matching the filter. Use <code>deleteMany</code> when you intend to remove every match. Both return a result with <code>deletedCount</code>.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Permanent &mdash; no undo</strong>. For production data, prefer soft delete (the <code>deleted: true</code> flag pattern) so you can audit, restore, or comply with retention policies.</li>
  <li>If <code>deletedCount</code> is 0, the filter didn&rsquo;t match anything &mdash; either the title is misspelled, already deleted, or there&rsquo;s a type mismatch.</li>
  <li><strong>To empty a collection</strong>, prefer <code>db.books.drop()</code> (instant, removes indexes too) over <code>deleteMany({})</code> which scans every document.</li>
  <li>For time-based cleanup (e.g. delete logs older than 30 days), use a <strong>TTL index</strong>: <code>db.logs.createIndex({ created_at: 1 }, { expireAfterSeconds: 30*24*3600 })</code>. Background thread auto-deletes &mdash; no app code required.</li>
  <li><code>findOneAndDelete()</code> deletes and returns the deleted document atomically &mdash; useful for queue/work-stealing patterns.</li>
</ul>
'''

ANSWERS[6] = r'''
<pre><code>// All documents
db.books.find()

// Pretty-print in mongosh
db.books.find().pretty()

// As an array (drivers and scripts)
const all = db.books.find().toArray()

// Iterate row by row (memory-friendly for large collections)
db.books.find().forEach(doc =&gt; print(doc.title))

// Limit + project the most useful fields
db.books.find({}, { title: 1, author: 1, published_year: 1, _id: 0 })
        .limit(20)

// Node.js driver
const cursor = db.collection("books").find()
for await (const doc of cursor) {
  console.log(doc.title)
}</code></pre>

<p>Calling <code>find()</code> with no filter returns a <strong>cursor</strong> over every document in the collection. The shell shows the first 20 by default; press <code>it</code> to fetch the next batch.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Don&rsquo;t fetch unbounded result sets in production code.</strong> Always pair with <code>limit()</code> for safety on collections of unknown size.</li>
  <li><strong>Project only the fields you need</strong> &mdash; reduces network traffic and lets <em>covering indexes</em> serve the entire query without touching documents.</li>
  <li>For deep pagination, use <strong>cursor-based pagination</strong> (last seen <code>_id</code>) rather than <code>skip()</code> &mdash; <code>skip</code> walks every skipped document.</li>
  <li>Cursors time out server-side after 10 minutes of inactivity. For long iterations, set <code>{ noCursorTimeout: true }</code> (and remember to close the cursor).</li>
  <li>To count without fetching: <code>db.books.countDocuments({})</code> for an exact count; <code>db.books.estimatedDocumentCount()</code> for the fast metadata-based count.</li>
</ul>
'''

ANSWERS[7] = r'''
<pre><code>// Books published after 2000
db.books.find({ published_year: { $gt: 2000 } })

// Strictly greater (not including 2000): use $gt
// Greater than or equal (including 2000): use $gte

// Combined range &mdash; published 2000-2010 inclusive
db.books.find({ published_year: { $gte: 2000, $lte: 2010 } })

// Sort by year ascending after filtering
db.books.find({ published_year: { $gt: 2000 } })
        .sort({ published_year: 1 })

// Project only relevant fields
db.books.find(
  { published_year: { $gt: 2000 } },
  { title: 1, author: 1, published_year: 1, _id: 0 }
)</code></pre>

<p>The <strong>comparison operators</strong> <code>$gt</code>, <code>$gte</code>, <code>$lt</code>, <code>$lte</code>, <code>$eq</code>, <code>$ne</code> work on numbers, strings, and dates &mdash; following BSON ordering rules.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>Comparison is <strong>type-strict</strong>: <code>{ published_year: { $gt: "2000" } }</code> matches strings, not numbers. Make sure your data type matches your filter type.</li>
  <li>For best performance, <strong>create an index on <code>published_year</code></strong> &mdash; <code>db.books.createIndex({ published_year: 1 })</code>. Range queries become index-range scans.</li>
  <li>If you also sort by the field, the index serves both the filter and the sort (no extra in-memory sort).</li>
  <li>Watch for null/missing fields: <code>{ published_year: { $gt: 2000 } }</code> won&rsquo;t match documents missing the field. Add <code>{ published_year: { $exists: true, $gt: 2000 } }</code> to be explicit.</li>
  <li>For date comparisons: <code>{ created_at: { $gt: ISODate("2025-01-01") } }</code>. JS <code>new Date("2025-01-01")</code> works too.</li>
</ul>
'''

ANSWERS[8] = r'''
<pre><code>// Include only title and author (and the default _id)
db.books.find({}, { title: 1, author: 1 })

// Suppress _id as well
db.books.find({}, { title: 1, author: 1, _id: 0 })

// Exclusion-style projection &mdash; everything except these fields
db.books.find({}, { synopsis: 0, reviews: 0 })

// Combined with a filter
db.books.find(
  { published_year: { $gt: 2020 } },
  { title: 1, author: 1, _id: 0 }
)

// In aggregation pipelines, use $project
db.books.aggregate([
  { $project: { title: 1, author: 1, _id: 0 } }
])</code></pre>

<p>The second argument to <code>find()</code> is a <strong>projection</strong>: <code>1</code> includes a field, <code>0</code> excludes it. Within the same projection you can&rsquo;t mix inclusion and exclusion <em>except</em> for the special <code>_id</code> field, which can be excluded alongside includes.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Always project</strong> on production reads &mdash; reduces network bandwidth and CPU on both sides, and enables <em>covering indexes</em>.</li>
  <li>A <strong>covered query</strong> reads only from the index without touching documents on disk &mdash; orders of magnitude faster. Achieved when the projected fields are all in the index and <code>_id</code> is excluded.</li>
  <li>For nested fields, use dot notation: <code>{ "address.city": 1 }</code>.</li>
  <li>For arrays, <code>{ tags: { $slice: 5 } }</code> returns only the first 5 elements; <code>{ tags: { $slice: [10, 5] } }</code> skips 10 and returns 5.</li>
  <li><code>$elemMatch</code> in projections returns the first array element matching a sub-condition &mdash; handy for &ldquo;the comment by user X.&rdquo;</li>
</ul>
'''

ANSWERS[9] = r'''
<pre><code>// Exact count matching a filter (default to {} for total)
db.books.countDocuments()
db.books.countDocuments({})
db.books.countDocuments({ author: "John Doe" })

// Fast approximate count of the entire collection
db.books.estimatedDocumentCount()

// Inside an aggregation pipeline
db.books.aggregate([
  { $match: { published_year: { $gt: 2020 } } },
  { $count: "recent_books" }
])
// Output: { recent_books: 42 }

// Legacy &mdash; deprecated in modern drivers
db.books.count()         // avoid; behavior differs across drivers</code></pre>

<p><strong><code>countDocuments()</code></strong> walks the matching index/collection range to give an exact count. <strong><code>estimatedDocumentCount()</code></strong> reads collection metadata for an instant approximate &mdash; perfect for total-row dashboards but not for filtered counts.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>For huge collections with no filter, prefer <code>estimatedDocumentCount()</code> &mdash; it&rsquo;s O(1) but can be slightly stale during heavy writes.</li>
  <li><code>countDocuments({})</code> on a collection of millions can take seconds &mdash; it walks the <code>_id</code> index. Cache or denormalize counts that you query frequently.</li>
  <li>The legacy <code>count()</code> method is <strong>deprecated</strong> &mdash; behavior on sharded collections during chunk migrations was inconsistent. Always use <code>countDocuments()</code> in new code.</li>
  <li>For dashboards that show counts per category, use a single aggregation with <code>$group</code> rather than many separate <code>countDocuments</code> calls &mdash; one pipeline, one round trip.</li>
  <li>If you need real-time counts at scale (Twitter-like engagement counters), maintain a denormalized counter field updated with <code>$inc</code> instead of recounting.</li>
</ul>
'''

ANSWERS[10] = r'''
<pre><code>// Sort by published_year descending (newest first)
db.books.find().sort({ published_year: -1 })

// Multi-field sort: year desc, then title asc as tiebreaker
db.books.find().sort({ published_year: -1, title: 1 })

// Combined: filter, sort, paginate
db.books.find({ author: "John Doe" })
        .sort({ published_year: -1 })
        .limit(10)

// In an aggregation pipeline
db.books.aggregate([
  { $sort: { published_year: -1 } }
])

// Sort direction values:
//   1  = ascending  (1, 2, 3...)
//  -1  = descending (newest, biggest first)</code></pre>

<p>Use <code>1</code> for ascending and <code>-1</code> for descending. MongoDB sorts using BSON comparison order &mdash; numbers before strings, with consistent ordering across all BSON types.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Index the sort field</strong> &mdash; a sort served by an index runs in O(N) cursor time. Without an index, MongoDB must materialize and sort in memory.</li>
  <li><strong>In-memory sort has a 100 MB limit</strong> by default. Larger sorts return an error unless you allow disk use: <code>db.books.aggregate([{ $sort: ... }], { allowDiskUse: true })</code>.</li>
  <li>For a compound index <code>{ author: 1, published_year: -1 }</code>, a query that filters by <code>author</code> and sorts by <code>published_year DESC</code> is fully index-served &mdash; no in-memory sort needed.</li>
  <li><strong>Sort direction must match the index direction</strong> for the optimizer to use it. The inverse direction (entire reversed compound) also works.</li>
  <li>Use <code>explain("executionStats")</code> and check for <code>SORT</code> stage in the plan &mdash; if present, the sort is in memory.</li>
</ul>
'''

ANSWERS[11] = r'''
<pre><code>// Single-field index on title
db.books.createIndex({ title: 1 })

// Unique index &mdash; rejects duplicate titles
db.books.createIndex({ title: 1 }, { unique: true })

// Case-insensitive index using collation
db.books.createIndex(
  { title: 1 },
  { collation: { locale: "en", strength: 2 } }
)

// List existing indexes to verify
db.books.getIndexes()

// Drop later if needed
db.books.dropIndex("title_1")

// Build in the background (older versions); 4.2+ all builds are non-blocking
db.books.createIndex({ title: 1 }, { background: true })</code></pre>

<p>Indexes dramatically speed up reads on the indexed field at the cost of slower writes (each write must update the index) and extra disk/RAM. The <code>1</code> means ascending order; for single-field indexes, the direction doesn&rsquo;t affect lookup speed but does affect <em>sort</em> efficiency.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Index name</strong> defaults to <code>title_1</code> (field name + direction). Override with <code>{ name: "idx_title" }</code>.</li>
  <li>From MongoDB 4.2+, all index builds are <strong>non-blocking</strong> &mdash; the <code>background: true</code> flag is no-op but still accepted.</li>
  <li>For text/full-text queries, use a text index instead: <code>db.books.createIndex({ title: "text" })</code>.</li>
  <li>For prefix matches like <code>/^Mongo/</code>, an ascending index works; for unanchored regex (<code>/Mongo/</code>), the index can&rsquo;t help.</li>
  <li>Before adding an index in production, check the working set size &mdash; indexes need to fit in RAM for best performance. Use <code>db.books.stats().indexSizes</code> to monitor.</li>
  <li>Use <strong>MongoDB Atlas Performance Advisor</strong> to find missing indexes from real query patterns.</li>
</ul>
'''

ANSWERS[12] = r'''
<pre><code>// Exact match on author
db.books.find({ author: "John Doe" })

// Equivalent verbose form
db.books.find({ author: { $eq: "John Doe" } })

// Case-insensitive equality (without regex):
db.books.find({ author: "John Doe" })
        .collation({ locale: "en", strength: 2 })

// Multiple authors (any of)
db.books.find({ author: { $in: ["John Doe", "Jane Doe"] } })

// Negation: not John Doe
db.books.find({ author: { $ne: "John Doe" } })

// Exists and not empty
db.books.find({ author: { $exists: true, $ne: "" } })</code></pre>

<p>Equality on a top-level field is the simplest and fastest query. If <code>author</code> is indexed, it&rsquo;s an O(log N) lookup; otherwise it&rsquo;s a full collection scan.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Type-strict</strong>: <code>{ author: 42 }</code> won&rsquo;t match the string <code>"42"</code>. MongoDB respects BSON types.</li>
  <li>For multiple values on the same field, <code>$in</code> is far cleaner than chained <code>$or</code>.</li>
  <li><strong>Indexing</strong>: <code>db.books.createIndex({ author: 1 })</code> is essential if author filters appear frequently.</li>
  <li>For <strong>case-insensitive</strong> equality at scale, build a case-insensitive index with <code>collation</code>; queries with the same collation use it. Regex (<code>/^John Doe$/i</code>) works but typically can&rsquo;t use a regular index.</li>
  <li>If <code>author</code> is an array field, <code>{ author: "John Doe" }</code> matches documents where the array <em>contains</em> that value &mdash; powerful for tag-style filtering.</li>
  <li>Use <code>explain("executionStats")</code> to verify the right index is picked. Look for <code>IXSCAN</code> stage and a low <code>totalDocsExamined</code>.</li>
</ul>
'''

ANSWERS[13] = r'''
<pre><code>// Set genre on every book that doesn&rsquo;t have one
db.books.updateMany(
  { genre: { $exists: false } },
  { $set: { genre: "General" } }
)

// Set genre on every book matching a filter
db.books.updateMany(
  { author: "John Doe" },
  { $set: { genre: "Tech" } }
)

// Set genre to a default for ALL books (use {} carefully)
db.books.updateMany(
  {},
  { $set: { genre: "Uncategorized" } }
)

// Set multiple new fields at once
db.books.updateMany(
  { published_year: { $gte: 2020 } },
  { $set: { genre: "Modern", is_recent: true, last_modified: new Date() } }
)

// The result tells you what happened
const r = db.books.updateMany({}, { $set: { genre: "X" } })
print(r.matchedCount, r.modifiedCount)</code></pre>

<p><code>updateMany</code> applies the same update to every matching document. With <code>$set</code> it adds the new field if missing or changes the value if present.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>The result returns <code>matchedCount</code> (how many docs matched the filter) and <code>modifiedCount</code> (how many actually changed). They differ when the new value equals the old one.</li>
  <li><strong>Test the filter with <code>find()</code> first</strong> &mdash; an empty filter <code>{}</code> matches every document and is a one-line accident waiting to happen.</li>
  <li>For very large collections, run the update in batches (use a date or <code>_id</code> range filter) to avoid long replication lag.</li>
  <li>For incremental updates that compute new values from existing ones, use the <strong>aggregation-pipeline form</strong>: <code>updateMany(filter, [{ $set: { full_title: { $concat: ["$title", " - ", "$author"] } } }])</code>.</li>
  <li>Each individual document update is atomic, but <code>updateMany</code> is <strong>not atomic across documents</strong> &mdash; other clients can see partial progress unless you wrap it in a transaction.</li>
</ul>
'''

ANSWERS[14] = r'''
<pre><code>// Delete every book published before 1990
db.books.deleteMany({ published_year: { $lt: 1990 } })

// Returns: { acknowledged: true, deletedCount: 47 }

// Add a guard against missing fields
db.books.deleteMany({
  published_year: { $exists: true, $lt: 1990 }
})

// Soft-delete instead (recommended for production data)
db.books.updateMany(
  { published_year: { $lt: 1990 } },
  { $set: { archived: true, archived_at: new Date() } }
)

// Use a transaction if related collections must update too
const session = db.getMongo().startSession()
session.startTransaction()
try {
  const ids = session.getDatabase("library").books
                     .find({ published_year: { $lt: 1990 } }, { _id: 1 })
                     .toArray().map(d =&gt; d._id)
  session.getDatabase("library").books.deleteMany({ _id: { $in: ids } })
  session.getDatabase("library").reviews.deleteMany({ book_id: { $in: ids } })
  session.commitTransaction()
} catch (e) { session.abortTransaction(); throw e } finally { session.endSession() }</code></pre>

<p><code>deleteMany</code> with a range filter is the standard cleanup. Always use <code>$lt</code> (strict less than) or <code>$lte</code> (less than or equal) and confirm which you need &mdash; off-by-one errors here are silent.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Run a <code>countDocuments()</code> first</strong> with the same filter so you know how many will be deleted before pulling the trigger.</li>
  <li>For huge bulk deletions, chunk them: select 1,000 <code>_id</code>s at a time, delete, repeat. Avoids long oplog entries and replica lag.</li>
  <li>If <code>published_year</code> is sometimes missing, the query won&rsquo;t match those docs &mdash; <code>$lt</code> requires the field to exist.</li>
  <li>For systematic time-based cleanup, set up a <strong>TTL index</strong>: <code>db.books.createIndex({ archived_at: 1 }, { expireAfterSeconds: 90*24*3600 })</code>. Runs in the background, no app code needed.</li>
  <li>To preserve referential integrity with related collections (reviews, ratings), wrap the delete in a transaction.</li>
</ul>
'''

ANSWERS[15] = r'''
<pre><code>// Anchored regex (uses index if title is indexed)
db.books.find({ title: /MongoDB/ })

// Equivalent $regex form, with case-insensitive option
db.books.find({ title: { $regex: "MongoDB", $options: "i" } })

// Substring match anywhere in the title
db.books.find({ title: /MongoDB/i })

// Starts with &ldquo;MongoDB&rdquo; (anchored, faster on indexed fields)
db.books.find({ title: /^MongoDB/ })

// Word boundary &mdash; whole word
db.books.find({ title: /\bMongoDB\b/i })

// Better for full-text matching: text index + $text
db.books.createIndex({ title: "text" })
db.books.find({ $text: { $search: "MongoDB" } })</code></pre>

<p>Use a regular-expression literal (<code>/MongoDB/</code>) or the <code>$regex</code> operator. The two forms are equivalent; literal form is cleaner in shell scripts.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Anchored regex (<code>^</code>) on indexed fields uses the index</strong> &mdash; substring/contains queries (<code>/MongoDB/</code>) usually do a collection scan.</li>
  <li><strong>Case-insensitive (<code>i</code> flag) typically can&rsquo;t use a regular index</strong> unless you build a collation index that matches.</li>
  <li>For real full-text needs (multiple words, stemming, relevance ranking), use a <strong>text index</strong> with <code>$text</code>, or <strong>MongoDB Atlas Search</strong> (Lucene-powered &mdash; far better for fuzzy/autocomplete/synonyms).</li>
  <li>Escape special regex characters in user input. Prefer building the regex programmatically: <code>new RegExp(escaped, "i")</code>.</li>
  <li>For very large datasets with frequent text searches, consider <strong>Elasticsearch</strong>, <strong>Meilisearch</strong>, or <strong>Typesense</strong> &mdash; purpose-built engines outperform regex queries by orders of magnitude.</li>
</ul>
'''

ANSWERS[16] = r'''
<pre><code>// Combined text index across two fields
db.books.createIndex({ title: "text", author: "text" })

// Weighted &mdash; matches in title score higher than matches in author
db.books.createIndex(
  { title: "text", author: "text" },
  { weights: { title: 10, author: 1 }, name: "books_text_idx" }
)

// Wildcard text index across all string fields
db.books.createIndex({ "$**": "text" })

// Default language for stemming (affects stop-word removal)
db.books.createIndex(
  { title: "text", author: "text" },
  { default_language: "english" }
)

// List indexes to confirm
db.books.getIndexes()

// Use it
db.books.find({ $text: { $search: "MongoDB" } })</code></pre>

<p>A <strong>text index</strong> tokenizes string fields, removes stop words, and applies stemming &mdash; powering the <code>$text</code> operator. A single collection can have <strong>only one text index</strong>, but it can span as many fields as needed.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Only one text index per collection</strong> &mdash; trying to create a second raises an error. Drop the existing one first if you need to change fields.</li>
  <li><strong>Weights</strong> let you boost specific fields (title matches matter more than synopsis matches).</li>
  <li>Text indexes are <strong>large</strong> &mdash; often 5-10x the size of the source data. Monitor disk and RAM usage.</li>
  <li>For multilingual content, <strong>specify language per document</strong>: <code>{ title: "...", language: "es" }</code> overrides the index default for that document.</li>
  <li>For modern, production search needs &mdash; fuzzy matching, autocomplete, faceting, synonyms &mdash; <strong>MongoDB Atlas Search</strong> (Lucene-backed) is the better choice. Self-hosted alternatives: <strong>Elasticsearch</strong>, <strong>OpenSearch</strong>, <strong>Meilisearch</strong>, <strong>Typesense</strong>.</li>
</ul>
'''

ANSWERS[17] = r'''
<pre><code>// Basic text search
db.books.find({ $text: { $search: "Database" } })

// Phrase search (exact match) &mdash; double-quoted inside the string
db.books.find({ $text: { $search: "\"NoSQL Database\"" } })

// Multiple words &mdash; OR semantics by default
db.books.find({ $text: { $search: "Database NoSQL" } })

// Exclude a word with -
db.books.find({ $text: { $search: "Database -SQL" } })

// Get the relevance score and sort by it
db.books.find(
  { $text: { $search: "Database" } },
  { title: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })

// Filter by score (only highly relevant)
db.books.aggregate([
  { $match: { $text: { $search: "Database" } } },
  { $addFields: { score: { $meta: "textScore" } } },
  { $match: { score: { $gt: 1.0 } } }
])</code></pre>

<p>The <code>$text</code> operator queries the collection&rsquo;s text index. Multi-word searches default to OR (matches any word). Use <code>"\"...\""</code> (escaped quotes) for exact phrase matches and <code>-word</code> to exclude.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>The <strong>relevance score</strong> is metadata accessed via <code>{ $meta: "textScore" }</code>. Always project and sort by it for &ldquo;most relevant first&rdquo; results.</li>
  <li>Stop words (<em>the</em>, <em>and</em>, <em>of</em>) are ignored.</li>
  <li>Stemming is automatic per the index&rsquo;s language &mdash; <em>databases</em> matches <em>database</em>.</li>
  <li>Only <strong>one <code>$text</code> per query</strong>; combine with other filters as needed: <code>{ $text: { $search: "..." }, author: "John Doe" }</code>.</li>
  <li>For better-than-stemming relevance (BM25, fuzzy, autocomplete, faceting), use <strong>Atlas Search</strong> &mdash; same MongoDB query API but a Lucene engine underneath.</li>
</ul>
'''

ANSWERS[18] = r'''
<pre><code>// Books per author
db.books.aggregate([
  { $group: {
      _id: "$author",
      total_books: { $sum: 1 }
  }}
])

// With sort by count descending
db.books.aggregate([
  { $group: { _id: "$author", total_books: { $sum: 1 } } },
  { $sort:  { total_books: -1 } }
])

// Top 10 most prolific authors
db.books.aggregate([
  { $group: { _id: "$author", total_books: { $sum: 1 } } },
  { $sort:  { total_books: -1 } },
  { $limit: 10 }
])

// Pre-filter (e.g. only books published after 2000)
db.books.aggregate([
  { $match: { published_year: { $gt: 2000 } } },
  { $group: { _id: "$author", total_books: { $sum: 1 } } },
  { $sort:  { total_books: -1 } }
])</code></pre>

<p>The <code>$group</code> stage takes a key (here <code>$author</code>) and accumulators that compute per-group values. <code>$sum: 1</code> is the standard count idiom &mdash; equivalent to SQL&rsquo;s <code>COUNT(*)</code>.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Always pre-filter with <code>$match</code></strong> when possible &mdash; it reduces the data volume entering the (potentially memory-heavy) <code>$group</code> stage and lets MongoDB use indexes.</li>
  <li>For very large groups, <code>$group</code> can spill to disk if needed &mdash; ensure <code>{ allowDiskUse: true }</code> is set or use Atlas (it&rsquo;s on by default).</li>
  <li>The <code>_id</code> field of <code>$group</code> can be a single field, an object of multiple fields (compound key), or <code>null</code> for &ldquo;all docs in one group.&rdquo;</li>
  <li>For accurate counts of unique authors only, use <code>$group: { _id: "$author" }</code> followed by <code>{ $count: "n" }</code>.</li>
  <li>To rename the output: project after grouping &mdash; <code>{ $project: { author: "$_id", total_books: 1, _id: 0 } }</code>.</li>
</ul>
'''

ANSWERS[19] = r'''
<pre><code>// Distinct authors using the dedicated method
db.books.distinct("author")
// Returns: [ "John Doe", "Jane Doe", "..." ]

// With a filter
db.books.distinct("author", { published_year: { $gt: 2000 } })

// In aggregation form (more flexible &mdash; can include other operations)
db.books.aggregate([
  { $group: { _id: "$author" } }
])

// Distinct with a count
db.books.aggregate([
  { $group: { _id: "$author", count: { $sum: 1 } } },
  { $sort:  { count: -1 } }
])

// Distinct values in nested arrays (e.g. genres array)
db.books.distinct("genres")     // automatic flattening</code></pre>

<p>The <code>distinct()</code> command is a fast specialized API that returns the unique values of a field. Pass a filter as the second argument to scope the search.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Output is capped at 16 MB</strong> &mdash; the BSON document limit. For high-cardinality fields (millions of distinct values), use the aggregation form which streams results.</li>
  <li>For array fields, <code>distinct</code> automatically flattens &mdash; <code>distinct("genres")</code> returns each unique tag across all books.</li>
  <li>An index on the field makes <code>distinct</code> O(unique values) instead of O(documents) &mdash; create one if you call <code>distinct</code> often.</li>
  <li>For a <strong>distinct count</strong> only: <code>db.books.distinct("author").length</code> in the shell, or <code>$group + $count</code> in aggregation for unbounded results.</li>
  <li>The aggregation form is preferred in production code because it&rsquo;s sortable, paginate-able, and handles huge result sets without the 16 MB ceiling.</li>
</ul>
'''

ANSWERS[20] = r'''
<pre><code>// Filter to books published in 2020
db.books.aggregate([
  { $match: { published_year: 2020 } }
])

// Combined with later stages
db.books.aggregate([
  { $match: { published_year: 2020 } },
  { $group: { _id: "$author", count: { $sum: 1 } } }
])

// Multiple conditions
db.books.aggregate([
  { $match: {
      published_year: 2020,
      author: { $in: ["John Doe", "Jane Doe"] }
  }}
])

// Match a date range (when stored as Date)
db.books.aggregate([
  { $match: {
      published_at: {
        $gte: ISODate("2020-01-01"),
        $lt:  ISODate("2021-01-01")
      }
  }}
])</code></pre>

<p>Place <code>$match</code> as <strong>early in the pipeline as possible</strong> &mdash; ideally first &mdash; so MongoDB can use an index to fetch only matching documents instead of scanning everything and filtering in memory.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><code>$match</code> uses the same query syntax as <code>find()</code> &mdash; all comparison/logical operators apply.</li>
  <li>If <code>published_year</code> is indexed, an early <code>$match</code> uses that index for an O(log N) seek to the matching range.</li>
  <li>Multiple <code>$match</code> stages are valid &mdash; the optimizer often merges adjacent ones.</li>
  <li>Avoid expressions that prevent index use (e.g. <code>$where</code>, complex <code>$expr</code> over multiple fields) in the first stage when possible.</li>
  <li>To verify the optimizer used your index, run <code>db.books.aggregate([...]).explain("executionStats")</code> and look for <code>IXSCAN</code>.</li>
</ul>
'''

ANSWERS[21] = r'''
<pre><code>// Average published_year per author
db.books.aggregate([
  { $group: {
      _id: "$author",
      avg_year: { $avg: "$published_year" }
  }}
])

// With count and sort
db.books.aggregate([
  { $group: {
      _id: "$author",
      avg_year:    { $avg: "$published_year" },
      total_books: { $sum: 1 },
      first_year:  { $min: "$published_year" },
      last_year:   { $max: "$published_year" }
  }},
  { $sort: { avg_year: -1 } }
])

// Round the average to 1 decimal
db.books.aggregate([
  { $group: { _id: "$author", avg_year: { $avg: "$published_year" } } },
  { $project: { _id: 1, avg_year: { $round: ["$avg_year", 1] } } }
])

// Pre-filter to make the average meaningful
db.books.aggregate([
  { $match: { published_year: { $exists: true, $type: "int" } } },
  { $group: { _id: "$author", avg_year: { $avg: "$published_year" } } }
])</code></pre>

<p>The <code>$avg</code> accumulator computes the arithmetic mean of numeric values within each group. Non-numeric values are silently ignored &mdash; treat that as a hint to validate types upstream.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Empty groups return null</strong> for the average (not zero). Handle in app code or use <code>$ifNull</code>: <code>{ $ifNull: ["$avg_year", 0] }</code>.</li>
  <li>For <strong>weighted average</strong> (e.g. weighted by number of pages), compute it manually: <code>$sum: { $multiply: ["$page_count", "$rating"] }</code> divided by total pages.</li>
  <li>For <strong>median or percentiles</strong>, MongoDB 7.0+ has <code>$percentile</code> and <code>$median</code> accumulators &mdash; far better than building it manually.</li>
  <li>Combine <code>$avg</code> with <code>$min</code>, <code>$max</code>, <code>$count</code> in a single <code>$group</code> &mdash; a single pass through the data.</li>
  <li>For very large datasets where exact accuracy isn&rsquo;t critical, MongoDB doesn&rsquo;t have a streaming mean estimator &mdash; consider an external system like <strong>Druid</strong>, <strong>ClickHouse</strong>, or <strong>StarRocks</strong>.</li>
</ul>
'''

ANSWERS[22] = r'''
<pre><code>// Project only title and published_year (drops _id by default? NO &mdash; _id stays unless excluded)
db.books.aggregate([
  { $project: { title: 1, published_year: 1 } }
])
// Output includes: _id, title, published_year

// Drop _id explicitly
db.books.aggregate([
  { $project: { title: 1, published_year: 1, _id: 0 } }
])

// Combined with rename and computed fields
db.books.aggregate([
  { $project: {
      _id: 0,
      book_title: "$title",
      year:       "$published_year",
      decade:     { $multiply: [{ $floor: { $divide: ["$published_year", 10] } }, 10] }
  }}
])

// Modern alternative: $addFields adds fields without dropping others
db.books.aggregate([
  { $addFields: { is_recent: { $gt: ["$published_year", 2020] } } }
])</code></pre>

<p>The <code>$project</code> stage controls which fields appear in the output &mdash; like SQL&rsquo;s <code>SELECT</code>. Use <code>1</code> to include and <code>0</code> to exclude. Within the same <code>$project</code> you can&rsquo;t mix inclusion and exclusion <em>except</em> for <code>_id</code>, which is excludable alongside includes.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><code>_id</code> is included by default &mdash; explicitly drop it (<code>_id: 0</code>) when you don&rsquo;t need it.</li>
  <li>Project early in the pipeline to reduce in-flight document size for downstream stages &mdash; saves memory and CPU.</li>
  <li>You can compute new fields using <strong>aggregation expressions</strong>: <code>$concat</code>, <code>$multiply</code>, <code>$add</code>, <code>$cond</code>, <code>$dateToString</code>, etc.</li>
  <li>For renaming or restructuring without losing other fields, prefer <strong><code>$addFields</code></strong> (alias <code>$set</code>) and <strong><code>$unset</code></strong>.</li>
  <li>For deeply nested transformations, use <strong><code>$replaceRoot</code></strong> to promote a sub-document to the top level.</li>
</ul>
'''

ANSWERS[23] = r'''
<pre><code>// Compound index on author (asc) and published_year (desc &mdash; newest first)
db.books.createIndex({ author: 1, published_year: -1 })

// Use cases that benefit:
//   - Filter by author, sort by year:
db.books.find({ author: "John Doe" }).sort({ published_year: -1 })

//   - Filter by author + year range:
db.books.find({ author: "John Doe", published_year: { $gte: 2020 } })

//   - Aggregation: group by author, sort within group by year
db.books.aggregate([
  { $match: { author: "John Doe" } },
  { $sort:  { published_year: -1 } }
])

// Verify the index is used
db.books.find({ author: "John Doe" })
        .sort({ published_year: -1 })
        .explain("executionStats")
// Look for "IXSCAN" stage and indexName: "author_1_published_year_-1"</code></pre>

<p>A <strong>compound index</strong> covers multiple fields with a defined order. Queries that filter or sort on the <strong>leftmost prefix</strong> can use it &mdash; this is the <em>leftmost-prefix rule</em>.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>Order matters! The index above serves <code>{ author: 1 }</code> alone or <code>{ author: 1, published_year: ... }</code> queries, but <strong>not</strong> queries on <code>published_year</code> alone.</li>
  <li>Follow the <strong>ESR rule</strong>: <em>E</em>quality fields first, <em>S</em>ort fields next, <em>R</em>ange fields last. This rule maximizes index utility for hybrid filter-sort-range queries.</li>
  <li>A query that filters on author and sorts ascending by year would <strong>not</strong> use this index efficiently &mdash; the sort directions don&rsquo;t match. Either flip the query or build a second index.</li>
  <li>For inverse direction sorts, MongoDB can read the same index backwards &mdash; <code>sort({ author: -1, published_year: 1 })</code> still works.</li>
  <li>Watch for <strong>over-indexing</strong> &mdash; each compound index slows writes and uses RAM. Use Atlas Performance Advisor or the <code>$indexStats</code> collection to find unused ones.</li>
</ul>
'''

ANSWERS[24] = r'''
<pre><code>// Most idiomatic: use $in
db.books.find({ author: { $in: ["John Doe", "Jane Doe"] } })

// Equivalent with $or (verbose but more flexible if conditions differ)
db.books.find({
  $or: [
    { author: "John Doe" },
    { author: "Jane Doe" }
  ]
})

// Combine with another filter (AND across, OR within $in)
db.books.find({
  author: { $in: ["John Doe", "Jane Doe"] },
  published_year: { $gte: 2020 }
})

// Negation &mdash; not these authors
db.books.find({ author: { $nin: ["John Doe", "Jane Doe"] } })

// $or with different conditions per branch
db.books.find({
  $or: [
    { author: "John Doe", published_year: { $gte: 2020 } },
    { author: "Jane Doe", published_year: { $gte: 2015 } }
  ]
})</code></pre>

<p>Prefer <code>$in</code> when all conditions are on the same field with the same operator &mdash; cleaner syntax and the optimizer treats it as multiple index seeks. Use <code>$or</code> when each branch has different conditions.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$in</code> on an indexed field</strong> = multiple targeted index seeks. Very fast even with hundreds of values.</li>
  <li><strong>Avoid huge <code>$in</code> arrays</strong> (thousands of values) &mdash; performance degrades. Move to a <code>$lookup</code>-style join or a temporary collection.</li>
  <li><strong>For <code>$or</code> to be index-friendly, every branch should be index-supported.</strong> If even one branch falls back to a collection scan, the entire query does too.</li>
  <li>The shorthand: <code>{ author: { $in: [...] } }</code> is preferred over manual <code>$or</code> for this case &mdash; less verbose, easier to maintain.</li>
  <li>For <strong>regex matches</strong> on multiple values: <code>{ author: { $in: [/^John/i, /^Jane/i] } }</code> works &mdash; but each regex is independently matched.</li>
</ul>
'''

ANSWERS[25] = r'''
<pre><code>// Anchored regex (uses an index on title if it exists)
db.books.find({ title: /^M/ })

// Equivalent $regex form
db.books.find({ title: { $regex: "^M" } })

// Case-insensitive (typically does NOT use an index)
db.books.find({ title: /^M/i })

// Index-friendly case-insensitive: use a collation index
db.books.createIndex(
  { title: 1 },
  { collation: { locale: "en", strength: 2 }, name: "title_ci" }
)
db.books.find({ title: /^M/ }).collation({ locale: "en", strength: 2 })

// Multiple letters &mdash; titles starting with M, A, or Z
db.books.find({ title: { $regex: "^[MAZ]" } })

// In aggregation
db.books.aggregate([
  { $match: { title: { $regex: "^M" } } }
])</code></pre>

<p>An <strong>anchored regex</strong> (<code>^</code> at the start) lets MongoDB use a regular index if one exists. Without the anchor, the engine must read every value &mdash; effectively a collection scan.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Anchored regex on indexed fields = fast.</strong> Anywhere-in-string matches are slow at scale.</li>
  <li>The <code>i</code> case-insensitive flag <strong>typically prevents index use</strong> on a regular index. Use a <strong>collation index</strong> with <code>strength: 2</code> for fast case-insensitive prefix lookups.</li>
  <li>For starts-with on numbers or dates, use range filters instead: <code>{ year: { $gte: 2020, $lt: 2030 } }</code> to find years starting with &ldquo;202&rdquo;.</li>
  <li>For autocomplete or typeahead UIs at scale, use <strong>MongoDB Atlas Search</strong>&rsquo;s autocomplete operator &mdash; far more efficient than regex.</li>
  <li>For multi-language case-insensitive search (e.g. Turkish &ldquo;İ&rdquo; vs &ldquo;i&rdquo;), specify the appropriate locale (<code>locale: "tr"</code>) in the collation.</li>
</ul>
'''

ANSWERS[26] = r'''
<pre><code>// Add a default rating to all books
db.books.updateMany(
  {},
  { $set: { rating: 5 } }
)

// Only set if missing (preserve existing values) &mdash; aggregation pipeline form
db.books.updateMany(
  {},
  [{ $set: { rating: { $ifNull: ["$rating", 5] } } }]
)

// Or with a filter that targets only docs missing the field
db.books.updateMany(
  { rating: { $exists: false } },
  { $set: { rating: 5 } }
)

// Add multiple defaults at once
db.books.updateMany(
  { rating: { $exists: false } },
  { $set: { rating: 5, review_count: 0, last_modified: new Date() } }
)

// Verify
db.books.countDocuments({ rating: 5 })</code></pre>

<p>The <strong>aggregation-pipeline update</strong> form (the array as the second argument) is the cleanest way to add a field <em>only</em> when missing &mdash; preserving existing values. Without it, plain <code>$set</code> overwrites every document.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>The <code>{ rating: { $exists: false } }</code> filter is a simpler alternative if you don&rsquo;t need a single atomic operation across both new and existing values.</li>
  <li><strong>For very large collections</strong>, run the update in batches (filter by a date or <code>_id</code> range) to avoid long replication lag and large oplog entries.</li>
  <li>To enforce the default at the schema level going forward, use <strong>schema validation</strong> on the collection &mdash; new inserts without <code>rating</code> get rejected, encouraging app-side defaults.</li>
  <li>For application-defined defaults, set them in the driver&rsquo;s ORM/ODM layer (Mongoose <code>default: 5</code>, Prisma defaults, etc.) so newly inserted documents automatically include them.</li>
  <li>Consider the data type: <code>5</code> stores as a Double; for an integer use <code>NumberInt(5)</code> in <code>mongosh</code>.</li>
</ul>
'''

ANSWERS[27] = r'''
<pre><code>// Remove the rating field from every document
db.books.updateMany(
  {},
  { $unset: { rating: "" } }
)

// The value of $unset is ignored &mdash; conventionally use "" or 1
db.books.updateMany({}, { $unset: { rating: 1 } })   // identical effect

// Remove from a subset (only books with rating 0)
db.books.updateMany(
  { rating: 0 },
  { $unset: { rating: "" } }
)

// Remove multiple fields at once
db.books.updateMany(
  {},
  { $unset: { rating: "", legacy_id: "", temp_flag: "" } }
)

// Verify the field is gone
db.books.find({ rating: { $exists: true } }).count()    // should be 0</code></pre>

<p>The <code>$unset</code> operator <strong>removes a field entirely</strong> &mdash; it&rsquo;s gone from the document, not just set to <code>null</code>. This matters because queries with <code>{ rating: null }</code> match both null values and missing fields, but <code>{ rating: { $exists: false } }</code> matches only the missing case.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>The <code>$unset</code> value is ignored</strong> &mdash; <code>""</code>, <code>1</code>, <code>true</code> all work identically. Convention is empty string or <code>1</code>.</li>
  <li>Use this for <strong>schema migrations</strong> &mdash; remove obsolete fields after refactoring.</li>
  <li>For nested fields, use dot notation: <code>{ $unset: { "metadata.legacy": "" } }</code>.</li>
  <li>For arrays, <code>$unset</code> deletes the entire array. To remove specific elements, use <code>$pull</code> or <code>$pop</code> instead.</li>
  <li>After unsetting on huge collections, run a compaction (<code>db.runCommand({ compact: "books" })</code>) if you need to reclaim disk space immediately &mdash; otherwise WiredTiger reclaims it lazily over time.</li>
</ul>
'''

ANSWERS[28] = r'''
<pre><code>// Title is not null and not missing
db.books.find({ title: { $ne: null } })

// More explicit (also exclude documents missing the field)
db.books.find({
  title: { $exists: true, $ne: null }
})

// And not an empty string either
db.books.find({
  title: { $exists: true, $ne: null, $ne: "" }
})

// Cleaner with $type &mdash; only string-typed titles
db.books.find({ title: { $type: "string", $ne: "" } })

// Aggregation form
db.books.aggregate([
  { $match: { title: { $exists: true, $ne: null } } }
])</code></pre>

<p>In MongoDB, <code>{ field: null }</code> matches both documents where the field is <em>explicitly null</em> and documents where the field is <em>missing entirely</em>. The simplest way to find &ldquo;has a non-null title&rdquo; is <code>{ title: { $ne: null } }</code> &mdash; it excludes both cases.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>This is a common interview gotcha &mdash; null and missing are conflated by default in equality checks. <code>$exists</code> separates them.</li>
  <li>To find <strong>only explicit nulls</strong> (rare): <code>{ title: { $type: "null" } }</code>.</li>
  <li>For migrations, find docs missing a required field with <code>{ title: { $exists: false } }</code> and update them with sensible defaults.</li>
  <li>Production validation: use <strong>schema validation</strong> on the collection to reject inserts without required fields. Pair with TypeScript types in the application.</li>
  <li>For data quality dashboards, query for type mismatches: <code>{ title: { $exists: true, $not: { $type: "string" } } }</code>.</li>
</ul>
'''

ANSWERS[29] = r'''
<pre><code>// Update by ObjectId (most precise)
db.books.updateOne(
  { _id: ObjectId("66243abf2c1f8e1234567890") },
  { $set: { title: "MongoDB Mastery" } }
)

// In Node.js driver, convert string to ObjectId
const { ObjectId } = require("mongodb");
await db.collection("books").updateOne(
  { _id: new ObjectId("66243abf2c1f8e1234567890") },
  { $set: { title: "MongoDB Mastery" } }
)

// Get the updated document back atomically
const updated = db.books.findOneAndUpdate(
  { _id: ObjectId("66243abf2c1f8e1234567890") },
  { $set: { title: "MongoDB Mastery" } },
  { returnDocument: "after" }   // or "before"
)

// Confirm
db.books.findOne({ _id: ObjectId("66243abf2c1f8e1234567890") })</code></pre>

<p>The <code>_id</code> field is the natural primary key &mdash; queries on it use the always-present <code>_id</code> index for instant O(log N) lookup. Always prefer <code>_id</code> over title-based filters when updating a single specific document.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Always wrap the hex string in <code>ObjectId(...)</code></strong> &mdash; passing a raw string won&rsquo;t match. This is a frequent bug source in beginner code.</li>
  <li>For <strong>read-modify-write atomicity</strong>, use <code>findOneAndUpdate()</code> &mdash; it returns the document (before or after the change) in a single round trip.</li>
  <li>The result of <code>updateOne</code> includes <code>matchedCount</code> and <code>modifiedCount</code>. Check <code>matchedCount === 0</code> to detect a missing or already-deleted document.</li>
  <li>For <strong>optimistic concurrency control</strong>, include a version field in the filter: <code>{ _id: id, version: 5 }</code> with <code>{ $set: { ...fields }, $inc: { version: 1 } }</code>. If the version has moved on, the update silently misses &mdash; you can detect and retry.</li>
  <li>For frameworks like Mongoose, <code>findByIdAndUpdate(id, { ... })</code> wraps this pattern.</li>
</ul>
'''

ANSWERS[30] = r'''
<pre><code>// Books that have an author field (any value, including null)
db.books.find({ author: { $exists: true } })

// More common: has an author and it&rsquo;s not null
db.books.find({
  author: { $exists: true, $ne: null }
})

// Has a non-empty string author
db.books.find({
  author: { $exists: true, $ne: null, $ne: "" }
})

// Inverse: missing author
db.books.find({ author: { $exists: false } })

// Both forms accepted: $exists: 1 / $exists: true and $exists: 0 / $exists: false</code></pre>

<p>The <code>$exists</code> operator checks for field presence in the document &mdash; regardless of value. It&rsquo;s the cleanest way to find documents that have or lack a particular field.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><code>$exists: true</code> matches documents where the field is present, <strong>even if the value is null</strong>. To require a non-null value, combine: <code>{ $exists: true, $ne: null }</code>.</li>
  <li><code>$exists: false</code> on a non-indexed field requires a collection scan &mdash; potentially slow on large collections.</li>
  <li>For <strong>consistency at scale</strong>, enforce field presence through schema validation rather than relying on application code to never drop fields.</li>
  <li>To find documents with all required fields populated: chain multiple <code>$exists</code> checks, or use <code>$jsonSchema</code> in <code>$match</code>: <code>{ $match: { $jsonSchema: { required: ["title", "author"] } } }</code>.</li>
  <li>For data quality reports, run an aggregation that counts missing fields per document: useful for migration planning.</li>
</ul>
'''

ANSWERS[31] = r'''
<pre><code>// Append a single genre to the array
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $push: { genres: "Fiction" } }
)

// Append multiple genres at once
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $push: { genres: { $each: ["Fiction", "Adventure", "Classic"] } } }
)

// Append unique only (no duplicates) &mdash; use $addToSet
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $addToSet: { genres: "Fiction" } }
)

// Cap the array length &mdash; keep only the latest 10
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $push: {
      recent_views: { $each: [{ user: "u1", at: new Date() }], $slice: -10 }
  }}
)

// Insert at a specific position
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $push: { genres: { $each: ["Bestseller"], $position: 0 } } }
)</code></pre>

<p>The <code>$push</code> operator appends an element to an array. If the field doesn&rsquo;t exist yet, MongoDB creates it as a new array.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$push</code> allows duplicates</strong> &mdash; use <code>$addToSet</code> if you want set semantics (no duplicates).</li>
  <li><strong>Use <code>$each</code></strong> to append multiple values in a single update; without it, an array argument is pushed as a single nested array element.</li>
  <li><strong>Use <code>$slice</code></strong> with negative N to keep only the most recent N elements &mdash; perfect for &ldquo;recent activity&rdquo; arrays.</li>
  <li><strong>Use <code>$position</code></strong> to insert at a specific index instead of appending. <code>0</code> for the start.</li>
  <li>Watch <strong>unbounded array growth</strong> &mdash; arrays become slower to query and update as they grow, and a single document can&rsquo;t exceed the 16 MB BSON limit. Use <code>$slice</code> to cap or model the data as separate documents.</li>
</ul>
'''

ANSWERS[32] = r'''
<pre><code>// Remove a single value
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $pull: { genres: "Fiction" } }
)

// Remove multiple values
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $pull: { genres: { $in: ["Fiction", "Mystery"] } } }
)

// Remove subdocuments matching a condition
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $pull: { reviews: { rating: { $lt: 3 } } } }
)

// Remove from many documents at once
db.books.updateMany(
  {},
  { $pull: { genres: "Deprecated" } }
)

// $pullAll &mdash; remove every value matching exactly any in the list (no operators)
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $pullAll: { genres: ["Fiction", "Mystery"] } }
)</code></pre>

<p>The <code>$pull</code> operator removes <strong>all elements that match a given condition</strong>. It&rsquo;s the standard way to delete items from arrays &mdash; whether by exact value or by an embedded query for arrays of subdocuments.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$pull</code> removes all matches</strong>, not just the first. This is opposite to <code>$pop</code> (which removes one element from the start or end).</li>
  <li>For <strong>arrays of subdocuments</strong>, <code>$pull</code> matches on the conditions you specify &mdash; e.g. remove cart items by SKU.</li>
  <li><code>$pullAll</code> is a related operator that takes a literal list and removes every exact match &mdash; faster for simple value-list removal but doesn&rsquo;t accept query operators.</li>
  <li>For <strong>positional removal</strong>, <code>$pop: { genres: 1 }</code> removes the last element, <code>-1</code> removes the first.</li>
  <li>To combine pull and add atomically: use a transaction or do two updates &mdash; MongoDB doesn&rsquo;t have a single &ldquo;replace element&rdquo; operator. Or use a different shape: store as a map keyed by id.</li>
</ul>
'''

ANSWERS[33] = r'''
<pre><code>// Books with at least one genre (non-empty array)
db.books.find({ genres: { $exists: true, $ne: [] } })

// Equivalent &mdash; use $not with $size 0
db.books.find({ genres: { $not: { $size: 0 } } })

// Has at least one specific genre
db.books.find({ genres: "Fiction" })           // implicit "contains"

// At least one genre from a list
db.books.find({ genres: { $in: ["Fiction", "Mystery"] } })

// At least one element matching multiple conditions (subdocs)
db.books.find({
  reviews: { $elemMatch: { rating: { $gte: 4 }, verified: true } }
})

// Aggregation form
db.books.aggregate([
  { $match: { genres: { $exists: true, $not: { $size: 0 } } } }
])</code></pre>

<p>For arrays of primitives, <code>{ field: value }</code> matches if the array <em>contains</em> that value &mdash; no special operator needed. For &ldquo;has at least one&rdquo; combined with other conditions on the same element, use <code>$elemMatch</code>.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>The query <code>{ genres: { $size: 0 } }</code> matches empty arrays (length 0). The negation finds non-empty.</li>
  <li><strong><code>$elemMatch</code> is mandatory</strong> when you have multiple conditions that must hold for the <em>same</em> element of an array of subdocuments. Otherwise MongoDB checks each condition independently across the whole array.</li>
  <li>An ascending index on the array field works for <code>{ genres: "Fiction" }</code> &mdash; MongoDB indexes each array element separately (multikey index).</li>
  <li><strong>Multikey index gotcha</strong>: a multikey index can&rsquo;t cover queries that need both field values from the index alone &mdash; the document must be fetched.</li>
  <li>For complex tag/category queries with relevance ranking (matching N out of M tags), consider <strong>Atlas Search</strong> or an external search engine.</li>
</ul>
'''

ANSWERS[34] = r'''
<pre><code>// Books with both Fiction AND Mystery in genres
db.books.find({ genres: { $all: ["Fiction", "Mystery"] } })

// Compare with $in (matches any one)
db.books.find({ genres: { $in: ["Fiction", "Mystery"] } })

// $all combined with other conditions
db.books.find({
  genres:        { $all: ["Fiction", "Adventure"] },
  published_year: { $gte: 2020 }
})

// $all on subdocuments using $elemMatch &mdash; both conditions must hold simultaneously
db.books.find({
  reviews: {
    $all: [
      { $elemMatch: { rating: 5, verified: true } },
      { $elemMatch: { rating: { $lte: 2 } } }
    ]
  }
})

// Aggregation form
db.books.aggregate([
  { $match: { genres: { $all: ["Fiction", "Mystery"] } } }
])</code></pre>

<p>The <code>$all</code> operator matches arrays that contain <strong>every value in the given list</strong>, in any order. Use it when documents have multiple tags/categories and you need to filter by the intersection.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$all</code> = AND across array values</strong>; <strong><code>$in</code> = OR.</strong> The two are commonly confused.</li>
  <li>A <strong>multikey index</strong> on <code>genres</code> accelerates <code>$all</code> &mdash; MongoDB intersects results from individual term lookups.</li>
  <li>For very large tag lists (10+ tags), <code>$all</code> can be slow even with an index. Consider full-text search engines (<strong>Atlas Search</strong>, <strong>Elasticsearch</strong>) for tag-based search at scale.</li>
  <li>For arrays of subdocuments needing complex matching, the <code>$all</code> + <code>$elemMatch</code> combo expresses &ldquo;there exists an element matching A AND an element matching B&rdquo;.</li>
  <li>For e-commerce faceting (matching multiple filters at once), <code>$all</code> is fine for small filter counts but consider purpose-built faceting systems for production.</li>
</ul>
'''

ANSWERS[35] = r'''
<pre><code>// Rename a single field across all documents
db.books.updateMany(
  {},
  { $rename: { "published_year": "year" } }
)

// Rename multiple fields at once
db.books.updateMany(
  {},
  { $rename: { "published_year": "year", "auth": "author" } }
)

// Conditional rename (only if old field exists, new doesn&rsquo;t)
db.books.updateMany(
  { published_year: { $exists: true }, year: { $exists: false } },
  { $rename: { "published_year": "year" } }
)

// Rename inside a nested document with dot notation
db.books.updateMany(
  {},
  { $rename: { "metadata.published_year": "metadata.year" } }
)

// In an aggregation pipeline (alternative)
db.books.aggregate([
  { $set: { year: "$published_year" } },
  { $unset: "published_year" },
  { $merge: { into: "books", whenMatched: "replace", whenNotMatched: "discard" } }
])</code></pre>

<p>The <code>$rename</code> operator atomically renames a field per document. If the new field name already exists, <code>$rename</code> overwrites it &mdash; be careful or use a conditional filter.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>If the source field is missing</strong> in a document, <code>$rename</code> is a no-op for that doc &mdash; safe.</li>
  <li><strong>If the target field exists</strong>, it&rsquo;s overwritten without warning. Always check the new field doesn&rsquo;t exist if that matters.</li>
  <li><strong>Doesn&rsquo;t work across documents in different shards</strong> &mdash; <code>$rename</code> requires the new path to live in the same shard as the old (rarely an issue unless your shard key includes that field).</li>
  <li>For huge collections, run the rename in batches by <code>_id</code> ranges to avoid replication lag.</li>
  <li>For schema migrations, prefer the <strong>expand-and-contract</strong> pattern: write to both fields, deploy, migrate readers, then drop the old field. Tools like <strong>Atlas Schema</strong>, <strong>Bytebase</strong>, or <strong>Liquibase</strong> formalize this.</li>
</ul>
'''

ANSWERS[36] = r'''
<pre><code>// Drop the genres field from every document
db.books.updateMany(
  {},
  { $unset: { genres: "" } }
)

// Result: { acknowledged: true, matchedCount: 1500, modifiedCount: 1500 }

// Drop only from documents that currently have the field
db.books.updateMany(
  { genres: { $exists: true } },
  { $unset: { genres: "" } }
)

// Drop multiple fields in one update
db.books.updateMany(
  {},
  { $unset: { genres: "", deprecated_tags: "", legacy_id: "" } }
)

// Verify
db.books.countDocuments({ genres: { $exists: true } })   // expect 0

// Reclaim disk space (optional, runs offline-style)
db.runCommand({ compact: "books" })</code></pre>

<p>This is the standard schema-cleanup operation when retiring a field. <code>$unset</code> removes the field entirely &mdash; it&rsquo;s gone, not set to null.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li>The value passed to <code>$unset</code> is ignored &mdash; <code>""</code>, <code>1</code>, <code>true</code> all work.</li>
  <li><strong>Run on a snapshot or backup first</strong> when removing fields from production &mdash; once dropped, the only recovery is from backup.</li>
  <li>For massive collections, batch by <code>_id</code> ranges (<code>{ _id: { $gte: lastSeen, $lt: nextChunk } }</code>) to avoid long-running operations.</li>
  <li>The <code>compact</code> command reclaims the freed disk space immediately. Without it, WiredTiger reclaims it lazily as new writes happen.</li>
  <li>Before dropping in production: verify no code references the field. Use <code>$indexStats</code> + grep across your codebase, or feature-flag the field-using code first to prove safety.</li>
</ul>
'''

ANSWERS[37] = r'''
<pre><code>// Create a capped collection with a 1 MB size limit
db.createCollection("logs", {
  capped: true,
  size: 1024 * 1024     // 1 MB in bytes
})

// Add a max document count too (whichever limit hits first wins)
db.createCollection("logs", {
  capped: true,
  size: 1024 * 1024,
  max:  10000
})

// Verify the capped status
db.logs.isCapped()       // true
db.logs.stats().capped   // true

// Convert an existing collection to capped (different command)
db.runCommand({
  convertToCapped: "logs",
  size: 10 * 1024 * 1024
})

// Drop the collection if you need to recreate with different options
db.logs.drop()</code></pre>

<p>A <strong>capped collection</strong> is a fixed-size, FIFO collection &mdash; once it reaches its limit, the oldest documents are automatically overwritten. They&rsquo;re fast for high-volume writes and useful for circular buffers like recent logs or chat history.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Size is in bytes</strong>, not documents. <code>size: 1024 * 1024</code> = 1 MB.</li>
  <li>The <code>max</code> option caps document count too &mdash; whichever limit is reached first triggers eviction.</li>
  <li><strong>Capped collections preserve insertion order</strong> &mdash; useful for tail-style consumption: <code>db.logs.find().sort({ $natural: -1 })</code>.</li>
  <li><strong>Cannot delete documents manually</strong> from a capped collection &mdash; eviction is automatic. Updates that grow a document also fail.</li>
  <li><strong>Cannot be sharded.</strong> If you outgrow a single replica set, switch to a regular collection with a TTL index for eviction or move to a <strong>time-series collection</strong> (5.0+) for IoT-style data.</li>
  <li>For modern log ingestion, prefer dedicated systems: <strong>Loki</strong>, <strong>OpenSearch</strong>, <strong>ClickHouse</strong>, <strong>Datadog Logs</strong>, or AWS CloudWatch.</li>
</ul>
'''

ANSWERS[38] = r'''
<pre><code>// Insert a log entry &mdash; same syntax as a regular collection
db.logs.insertOne({
  level:   "info",
  message: "User logged in",
  user_id: ObjectId("66243abf..."),
  ts:      new Date()
})

// Bulk insert is fine too
db.logs.insertMany([
  { level: "info",  message: "Page viewed",     ts: new Date() },
  { level: "warn",  message: "Slow query",      ts: new Date() },
  { level: "error", message: "Payment failed",  ts: new Date() }
])

// Tail the latest entries (newest first via natural reverse order)
db.logs.find().sort({ $natural: -1 }).limit(10)

// Tailable cursor (Node.js) &mdash; subscribe to new entries as they&rsquo;re inserted
const cursor = db.collection("logs").find({}, {
  tailable: true,
  awaitData: true,
  noCursorTimeout: true
})
for await (const doc of cursor) {
  console.log(doc)        // emits in real time
}</code></pre>

<p>Inserts into a capped collection use the standard <code>insertOne</code>/<code>insertMany</code> &mdash; no special API. The collection auto-evicts the oldest documents to stay under the size cap.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Inserts are very fast</strong> &mdash; documents go into pre-allocated space, no fragmentation.</li>
  <li><strong>No <code>_id</code> uniqueness check</strong> needed for in-collection uniqueness because order is guaranteed and there&rsquo;s an automatic <code>_id</code> index.</li>
  <li><strong>Use <code>$natural: -1</code></strong> for newest-first iteration; <code>1</code> for oldest-first. This matches insertion order, which capped collections preserve.</li>
  <li><strong>Tailable cursors</strong> let consumers subscribe to new inserts in real time &mdash; the basis of MongoDB&rsquo;s replication oplog.</li>
  <li>If updates that grow a document are needed, capped collections aren&rsquo;t the right fit &mdash; they reject those.</li>
  <li>For modern log workflows, also consider <strong>change streams</strong> on a regular collection &mdash; same real-time capability with full update/delete semantics.</li>
</ul>
'''

ANSWERS[39] = r'''
<pre><code>// Inclusive range: 1990 through 2000
db.books.find({
  published_year: { $gte: 1990, $lte: 2000 }
})

// Exclusive range: strictly between
db.books.find({
  published_year: { $gt: 1990, $lt: 2000 }
})

// Mixed: between 1990 (inclusive) and 2000 (exclusive)
db.books.find({
  published_year: { $gte: 1990, $lt: 2000 }
})

// For dates, use Date objects (or ISODate in mongosh)
db.books.find({
  published_at: {
    $gte: ISODate("1990-01-01"),
    $lt:  ISODate("2001-01-01")
  }
})

// Combine with other filters
db.books.find({
  published_year: { $gte: 1990, $lte: 2000 },
  author: "John Doe"
})</code></pre>

<p>Range queries combine <code>$gte</code>/<code>$gt</code> with <code>$lte</code>/<code>$lt</code>. Be deliberate about inclusive vs exclusive endpoints &mdash; off-by-one errors here are silent.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Index <code>published_year</code></strong> for fast range queries: <code>db.books.createIndex({ published_year: 1 })</code>. The index serves the range scan efficiently.</li>
  <li>Combine with a <strong>compound index</strong> if you also filter by another field: <code>{ author: 1, published_year: 1 }</code> &mdash; equality fields first, then range.</li>
  <li><strong>For dates, prefer half-open intervals</strong>: <code>$gte: startOfMonth, $lt: startOfNextMonth</code> avoids ambiguity around the end of the period and works cleanly across timezones.</li>
  <li>If <code>published_year</code> is sometimes stored as a string (data quality issue), the range filter won&rsquo;t match string values &mdash; check with <code>{ $type: "string" }</code> and migrate.</li>
  <li>For very wide ranges over a billion-row collection, consider <strong>partitioning by year</strong> in a separate analytical store (<strong>ClickHouse</strong>, <strong>StarRocks</strong>, <strong>Druid</strong>, or <strong>BigQuery</strong>).</li>
</ul>
'''

ANSWERS[40] = r'''
<pre><code>// Author starting with &ldquo;John&rdquo; (case-sensitive, anchored)
db.books.find({ author: /^John/ })

// Case-insensitive
db.books.find({ author: /^John/i })

// Equivalent $regex form
db.books.find({ author: { $regex: "^John", $options: "i" } })

// Anywhere in the string
db.books.find({ author: { $regex: "Doe", $options: "i" } })

// Whole word match (word boundaries)
db.books.find({ author: /\bDoe\b/i })

// Build dynamically from user input (escape special chars first)
const escape = s =&gt; s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const query = escape("John?");
db.books.find({ author: { $regex: `^${query}`, $options: "i" } })</code></pre>

<p>The two regex forms (<code>/.../</code> literal and <code>{ $regex: "..." }</code> object) are equivalent. The literal form is cleaner; the object form is necessary when building queries dynamically (the regex string itself is dynamic).</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Anchored regex (<code>^</code>) on indexed fields uses the index</strong>; unanchored regex typically does a collection scan.</li>
  <li><strong>Case-insensitive (<code>i</code>) typically prevents index use</strong> on a regular index. Build a collation index for index-friendly case-insensitive matching.</li>
  <li><strong>Always escape user input</strong> in regex queries to prevent ReDoS (regex denial-of-service) and mismatches from special chars.</li>
  <li>For autocomplete/typeahead at scale, <strong>MongoDB Atlas Search</strong>&rsquo;s <code>autocomplete</code> operator outperforms regex by 10-100x.</li>
  <li>For complex multi-field text matching, build a text index or use <strong>Atlas Search</strong>.</li>
</ul>
'''

ANSWERS[41] = r'''
<pre><code>// Increment copies_sold by 10
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $inc: { copies_sold: 10 } }
)

// Decrement (negative value)
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $inc: { copies_sold: -1 } }
)

// Multiple counters at once
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $inc: { copies_sold: 10, view_count: 1, revenue: 250 } }
)

// $inc creates the field if missing (starts at 0)
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $inc: { copies_sold: 10 } }
)
// If copies_sold didn&rsquo;t exist, it&rsquo;s now 10

// Atomic counter with read-back
const r = db.books.findOneAndUpdate(
  { _id: ObjectId("66243abf...") },
  { $inc: { copies_sold: 10 } },
  { returnDocument: "after" }
)
print(r.copies_sold)</code></pre>

<p>The <code>$inc</code> operator atomically adjusts a numeric field. It&rsquo;s the right tool for counters: views, likes, balances, scores. Atomic means safe under concurrent updates &mdash; no read-modify-write race.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Single-document atomic</strong> &mdash; safe for high-concurrency counter updates without locking.</li>
  <li><strong>Negative values decrement</strong>; <code>$mul</code> multiplies (e.g. <code>$mul: { price: 0.9 }</code> for 10% off).</li>
  <li><strong>Field must be numeric</strong> &mdash; trying to <code>$inc</code> a string raises an error. Use schema validation to prevent this.</li>
  <li>For <strong>extremely hot counters</strong> (viral content getting millions of inc/sec), MongoDB can become a bottleneck. Use a sharded counter pattern (multiple sub-counters per document) or front it with <strong>Redis</strong> and persist asynchronously.</li>
  <li>For aggregate stats (revenue per day, etc.), use <code>$inc</code> with an upsert: <code>updateOne({ date: today, type: "sale" }, { $inc: { total: 1 } }, { upsert: true })</code>.</li>
</ul>
'''

ANSWERS[42] = r'''
<pre><code>// Books missing the published_year field
db.books.find({ published_year: { $exists: false } })

// More expressive
db.books.find({
  $or: [
    { published_year: { $exists: false } },
    { published_year: null }
  ]
})

// Cleaner shorthand &mdash; matches null OR missing
db.books.find({ published_year: null })

// Aggregation form
db.books.aggregate([
  { $match: { published_year: { $exists: false } } }
])

// Count them
db.books.countDocuments({ published_year: { $exists: false } })</code></pre>

<p>Use <code>$exists: false</code> when you specifically want documents where the field is absent. Use <code>{ field: null }</code> when you want documents where the field is either explicitly null or absent.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$exists: false</code> queries can&rsquo;t use a regular index</strong> &mdash; the index entries point to documents that <em>have</em> the field, not those that don&rsquo;t. Expect a collection scan.</li>
  <li>For better performance, maintain a <strong>partial index</strong> on documents that have the field, and rely on a non-indexed scan for the absence query (which is usually a one-off migration query).</li>
  <li>This is the standard query for <strong>data migration audits</strong>: count documents missing a required field before adding a default.</li>
  <li>Once you&rsquo;ve added the field everywhere, use <strong>schema validation</strong> with <code>required: ["published_year"]</code> to prevent future inserts from missing it.</li>
  <li>For data quality dashboards, run periodic counts of missing fields and emit metrics &mdash; alerts on regression.</li>
</ul>
'''

ANSWERS[43] = r'''
<pre><code>// Sort by author asc, then by title asc within each author
db.books.aggregate([
  { $sort: { author: 1, title: 1 } }
])

// Mixed directions: author asc, then title desc
db.books.aggregate([
  { $sort: { author: 1, title: -1 } }
])

// With a filter and projection
db.books.aggregate([
  { $match: { published_year: { $gte: 2020 } } },
  { $sort:  { author: 1, title: 1 } },
  { $project: { author: 1, title: 1, published_year: 1, _id: 0 } }
])

// Equivalent in find() form
db.books.find({ published_year: { $gte: 2020 } })
        .sort({ author: 1, title: 1 })

// To allow large in-memory sorts (over 100 MB)
db.books.aggregate(
  [{ $sort: { author: 1, title: 1 } }],
  { allowDiskUse: true }
)</code></pre>

<p>Multi-field sort orders documents lexicographically: first by the first field, ties broken by the next, and so on. The fields can have independent sort directions.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Index for fast sorts</strong>: <code>db.books.createIndex({ author: 1, title: 1 })</code>. The index direction must match the sort direction (or be its exact inverse) for index-served sorts.</li>
  <li><strong>In-memory sorts have a 100 MB limit</strong>. Larger sorts return an error unless <code>{ allowDiskUse: true }</code> is set on the aggregation.</li>
  <li>For large sorts that always run, prefer index-served sorts &mdash; they don&rsquo;t hit the memory limit at all.</li>
  <li>Sort order is BSON ordering &mdash; numbers before strings, deterministic across types.</li>
  <li>For <strong>collation-aware sorts</strong> (e.g. locale-specific alphabet), specify <code>collation</code> on the query: <code>.sort({ title: 1 }).collation({ locale: "fr" })</code>.</li>
</ul>
'''

ANSWERS[44] = r'''
<pre><code>// Total copies_sold per author
db.books.aggregate([
  { $group: {
      _id: "$author",
      total_copies: { $sum: "$copies_sold" }
  }}
])

// Sort to find the top sellers
db.books.aggregate([
  { $group: { _id: "$author", total_copies: { $sum: "$copies_sold" } } },
  { $sort:  { total_copies: -1 } },
  { $limit: 10 }
])

// Combine multiple stats per author
db.books.aggregate([
  { $group: {
      _id: "$author",
      total_copies:  { $sum: "$copies_sold" },
      avg_per_book:  { $avg: "$copies_sold" },
      best_seller:   { $max: "$copies_sold" },
      book_count:    { $sum: 1 }
  }},
  { $sort: { total_copies: -1 } }
])

// Pre-filter for only published books
db.books.aggregate([
  { $match: { copies_sold: { $exists: true, $type: "number" } } },
  { $group: { _id: "$author", total_copies: { $sum: "$copies_sold" } } }
])</code></pre>

<p>The <code>$sum</code> accumulator in <code>$group</code> totals numeric values &mdash; equivalent to SQL&rsquo;s <code>SUM()</code>. Pass <code>$sum: 1</code> to count documents per group instead.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Non-numeric values are skipped silently.</strong> Validate your data with schema validation or <code>$type</code> filters.</li>
  <li><strong>Combine multiple accumulators</strong> in a single <code>$group</code> stage &mdash; one pass through the data computes everything: total, count, average, min, max.</li>
  <li><strong>Pre-filter with <code>$match</code></strong> early to reduce the data <code>$group</code> processes &mdash; massive perf wins on large collections.</li>
  <li>For grand-total (one row), use <code>_id: null</code>: <code>{ $group: { _id: null, total: { $sum: "$copies_sold" } } }</code>.</li>
  <li>For <strong>real-time dashboards</strong> that need the same aggregation often, materialize the result with <code>$merge</code> into a summary collection and refresh periodically.</li>
</ul>
'''

ANSWERS[45] = r'''
<pre><code>// Average rating across all books
db.books.aggregate([
  { $group: { _id: null, avg_rating: { $avg: "$rating" } } }
])

// Average rating per author
db.books.aggregate([
  { $group: { _id: "$author", avg_rating: { $avg: "$rating" } } }
])

// Round to 2 decimals
db.books.aggregate([
  { $group: { _id: null, avg_rating: { $avg: "$rating" } } },
  { $project: { avg_rating: { $round: ["$avg_rating", 2] } } }
])

// Filter out books with no rating before averaging
db.books.aggregate([
  { $match: { rating: { $exists: true, $type: "number" } } },
  { $group: { _id: null, avg_rating: { $avg: "$rating" }, sample_size: { $sum: 1 } } }
])

// Average rating per genre (after unwinding genres array)
db.books.aggregate([
  { $unwind: "$genres" },
  { $group:  { _id: "$genres", avg_rating: { $avg: "$rating" } } },
  { $sort:   { avg_rating: -1 } }
])</code></pre>

<p>The <code>$avg</code> accumulator computes the arithmetic mean. Combine with <code>$count</code> or <code>$sum: 1</code> to also report sample size &mdash; an average over 5 books is far less reliable than one over 5,000.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Non-numeric values are silently ignored</strong> &mdash; this can hide data quality issues. Filter explicitly: <code>{ rating: { $type: "number" } }</code>.</li>
  <li>For <strong>weighted averages</strong> (e.g. weighted by review count): <code>$divide: [{ $sum: { $multiply: ["$rating", "$reviews_count"] } }, { $sum: "$reviews_count" }]</code>.</li>
  <li>For <strong>median or percentiles</strong>, MongoDB 7.0+ has <code>$percentile</code>: <code>{ $percentile: { input: "$rating", p: [0.5, 0.95], method: "approximate" } }</code>.</li>
  <li><strong>Always include sample size</strong> in product analytics &mdash; an average without N is misleading.</li>
  <li>For <strong>Bayesian-style smoothing</strong> (down-weighting averages with few samples), apply post-aggregation: <code>(rating_sum + prior_sum) / (n + prior_n)</code>.</li>
</ul>
'''

ANSWERS[46] = r'''
<pre><code>// Title length &gt; 10 characters &mdash; use $expr with $strLenCP
db.books.find({
  $expr: { $gt: [{ $strLenCP: "$title" }, 10] }
})

// Aggregation form (more efficient if combined with other stages)
db.books.aggregate([
  { $match: { $expr: { $gt: [{ $strLenCP: "$title" }, 10] } } }
])

// Add a computed length field for downstream use
db.books.aggregate([
  { $addFields: { title_length: { $strLenCP: "$title" } } },
  { $match:     { title_length: { $gt: 10 } } }
])

// $strLenCP counts code points (proper Unicode counting)
// $strLenBytes counts UTF-8 bytes &mdash; differs for non-ASCII characters
db.books.find({
  $expr: { $gt: [{ $strLenBytes: "$title" }, 20] }
})

// Range filter: titles between 5 and 15 characters
db.books.find({
  $expr: {
    $and: [
      { $gte: [{ $strLenCP: "$title" }, 5] },
      { $lte: [{ $strLenCP: "$title" }, 15] }
    ]
  }
})</code></pre>

<p>String length checks require <code>$expr</code> because regular query operators can&rsquo;t call functions on field values. <code>$strLenCP</code> counts Unicode code points (the right answer for displayed characters); <code>$strLenBytes</code> counts UTF-8 bytes.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$expr</code> queries can&rsquo;t use indexes</strong> for the computed condition &mdash; expect a collection scan. For frequent length-based queries, <strong>denormalize</strong> a <code>title_length</code> field on insert/update and index that.</li>
  <li><strong>Use <code>$strLenCP</code> by default</strong> &mdash; it matches what users see in their text editor. Use <code>$strLenBytes</code> when you care about storage/network size.</li>
  <li>For <strong>graphemes</strong> (combining characters, emoji), even <code>$strLenCP</code> is an approximation &mdash; emoji modifiers count as multiple code points. For true grapheme counts, do it in app code with a Unicode library.</li>
  <li>For <strong>truncation in projection</strong>, use <code>$substrCP</code>: <code>{ short_title: { $substrCP: ["$title", 0, 10] } }</code>.</li>
  <li>To validate title length on insert/update, use <strong>schema validation</strong> with <code>{ minLength: 5, maxLength: 100 }</code>.</li>
</ul>
'''

ANSWERS[47] = r'''
<pre><code>// Phrase search &mdash; double-quoted within the search string
db.books.find({ $text: { $search: "\"NoSQL databases\"" } })

// Combine phrase with extra words (must contain phrase + any of the extras)
db.books.find({ $text: { $search: "\"NoSQL databases\" performance" } })

// Sort by relevance score
db.books.find(
  { $text: { $search: "\"NoSQL databases\"" } },
  { title: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } }).limit(10)

// Aggregation: combine phrase search with other filters and ranking
db.books.aggregate([
  { $match: {
      $text: { $search: "\"NoSQL databases\"" },
      published_year: { $gte: 2020 }
  }},
  { $addFields: { score: { $meta: "textScore" } } },
  { $sort:  { score: -1 } },
  { $limit: 20 }
])

// Modern alternative &mdash; Atlas Search phrase operator
// (run from Atlas Search compound operators)
db.books.aggregate([
  { $search: { phrase: { query: "NoSQL databases", path: ["title", "body"] } } }
])</code></pre>

<p>For an <strong>exact phrase</strong>, wrap it in <strong>escaped double quotes</strong> inside the <code>$search</code> string. Without quotes, the words are matched independently (OR semantics).</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Requires a text index</strong> on the searched fields &mdash; without it, <code>$text</code> errors out.</li>
  <li><strong>Phrase matching is exact</strong>: the words must appear consecutively in that order. Stemming still applies to individual words within the phrase.</li>
  <li>The escape sequence (<code>\"</code>) is essential in JS strings; in mongosh you can also use a JS template literal: <code>{ $search: 'phrase: "NoSQL databases"' }</code>.</li>
  <li>For <strong>better phrase relevance</strong> (proximity scoring, fuzzy matching), <strong>MongoDB Atlas Search</strong> has dedicated <code>phrase</code> and <code>span</code> operators with the <code>slop</code> parameter for fuzziness.</li>
  <li>For self-hosted environments needing top-tier search, integrate with <strong>Elasticsearch</strong>, <strong>OpenSearch</strong>, <strong>Meilisearch</strong>, or <strong>Typesense</strong>.</li>
</ul>
'''

ANSWERS[48] = r'''
<pre><code>// Books with at least one review of rating 5
db.books.find({
  reviews: { $elemMatch: { rating: 5 } }
})

// Combined conditions on the same review element (must hold simultaneously)
db.books.find({
  reviews: { $elemMatch: { rating: 5, verified: true } }
})

// Without $elemMatch, conditions are checked independently across the array
db.books.find({
  "reviews.rating":   5,
  "reviews.verified": true
})
// This matches if SOME review has rating 5 AND SOME review is verified &mdash;
// not necessarily the same review!

// $elemMatch in a projection &mdash; return only matching elements
db.books.find(
  { "reviews.rating": 5 },
  { reviews: { $elemMatch: { rating: 5 } } }
)

// Aggregation form
db.books.aggregate([
  { $match: { reviews: { $elemMatch: { rating: 5 } } } }
])</code></pre>

<p><code>$elemMatch</code> is essential when querying arrays of subdocuments and you need <strong>multiple conditions to match the same element</strong>. The dot-notation form treats each condition independently across the entire array.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Without <code>$elemMatch</code></strong>, MongoDB matches conditions independently &mdash; one review can satisfy <code>rating: 5</code> while a different review satisfies <code>verified: true</code>. Often a bug.</li>
  <li><strong>In projection</strong>, <code>$elemMatch</code> returns only the first matching element &mdash; useful for &ldquo;the comment by user X&rdquo; or pagination.</li>
  <li>For nested array indexes (multikey on <code>reviews.rating</code>), <code>$elemMatch</code> is required for the optimizer to use the index for compound conditions.</li>
  <li>For complex array filters in aggregations, also see <code>$filter</code> &mdash; it returns a filtered array (not just a match).</li>
  <li>For modeling reviews at scale, consider a separate <code>reviews</code> collection with a <code>book_id</code> reference &mdash; arrays in documents have a 16 MB hard limit and grow expensive over time.</li>
</ul>
'''

ANSWERS[49] = r'''
<pre><code>// Author not equal to "Unknown" (and present)
db.books.find({ author: { $ne: "Unknown" } })

// Returns documents with author OTHER than "Unknown"
// AND documents missing the author field (since missing != "Unknown")

// Strict: author is present AND not "Unknown"
db.books.find({
  author: { $exists: true, $ne: "Unknown" }
})

// Multiple negations
db.books.find({
  author: { $nin: ["Unknown", "Anonymous", ""] }
})

// Equivalent with $not
db.books.find({
  author: { $not: { $eq: "Unknown" } }
})

// Aggregation form
db.books.aggregate([
  { $match: { author: { $ne: "Unknown" } } }
])</code></pre>

<p>The <code>$ne</code> (not equal) operator matches documents where the field is anything other than the given value &mdash; <strong>including documents where the field is missing or null</strong>. This is sometimes surprising.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$ne</code> matches missing fields</strong>. To exclude both &ldquo;Unknown&rdquo; and missing, add <code>$exists: true</code>.</li>
  <li><strong>For multiple values</strong>, prefer <code>$nin</code>: <code>{ author: { $nin: ["Unknown", "Anonymous"] } }</code> &mdash; cleaner than chained <code>$ne</code>.</li>
  <li><strong>Negation queries can&rsquo;t use indexes effectively</strong> &mdash; <code>$ne</code> typically results in a collection scan because it&rsquo;s the entire range minus a point. Filter on the positive condition when possible.</li>
  <li>If you have a small set of known &ldquo;valid&rdquo; values, prefer the positive query: <code>{ author: { $in: ["John Doe", "Jane Doe"] } }</code> &mdash; index-friendly.</li>
  <li>For data quality monitoring, queries with <code>$nin: ["Unknown", null, ""]</code> identify the &ldquo;clean&rdquo; subset.</li>
</ul>
'''

ANSWERS[50] = r'''
<pre><code>// Books with more than 5 genres
db.books.find({
  $expr: { $gt: [{ $size: "$genres" }, 5] }
})

// $size operator (exact match only) &mdash; doesn&rsquo;t support ranges
db.books.find({ genres: { $size: 5 } })       // exactly 5 genres

// For ranges, use $expr with $size
db.books.find({
  $expr: {
    $and: [
      { $gt: [{ $size: "$genres" }, 5] },
      { $lt: [{ $size: "$genres" }, 20] }
    ]
  }
})

// More efficient: maintain a denormalized count field
db.books.updateMany({}, [
  { $set: { genres_count: { $size: { $ifNull: ["$genres", []] } } } }
])
db.books.createIndex({ genres_count: 1 })

// Now this query uses the index
db.books.find({ genres_count: { $gt: 5 } })

// Aggregation form
db.books.aggregate([
  { $addFields: { genres_count: { $size: { $ifNull: ["$genres", []] } } } },
  { $match: { genres_count: { $gt: 5 } } }
])</code></pre>

<p>The <code>$size</code> array operator only supports exact-match queries. For ranges, you need <code>$expr</code> with <code>$size</code> as a function call &mdash; but neither uses an index. The performant production approach is to <strong>denormalize a count field</strong> and index it.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$size: 5</code></strong> matches exactly 5; can&rsquo;t do <code>$gt: 5</code> or ranges directly.</li>
  <li><strong><code>$expr</code> with <code>$size</code> works for ranges</strong> but does a collection scan unless the array is small or you can pre-filter.</li>
  <li><strong>Denormalizing the count</strong> (<code>genres_count</code>) is the standard trick &mdash; index it, query it directly. Update the count atomically with each <code>$push</code>/<code>$pull</code> using a transaction or manual cooperation.</li>
  <li>For <strong>average size analytics</strong>: <code>db.books.aggregate([{ $project: { n: { $size: "$genres" } } }, { $group: { _id: null, avg: { $avg: "$n" } } }])</code>.</li>
  <li>If <code>genres</code> may be missing, use <code>{ $size: { $ifNull: ["$genres", []] } }</code> to default to an empty array (size 0) instead of erroring.</li>
</ul>
'''

ANSWERS[51] = r'''
<pre><code>// Remove books with empty or missing genres array
db.books.deleteMany({
  $or: [
    { genres: { $exists: false } },
    { genres: { $size: 0 } },
    { genres: null }
  ]
})

// Cleaner using $expr to check effective length is 0
db.books.deleteMany({
  $expr: { $eq: [{ $size: { $ifNull: ["$genres", []] } }, 0] }
})

// Soft-delete instead (preferred in production)
db.books.updateMany(
  { $or: [
      { genres: { $exists: false } },
      { genres: { $size: 0 } }
  ]},
  { $set: { archived: true, archived_at: new Date(), archived_reason: "no_genres" } }
)

// First, count to confirm
db.books.countDocuments({
  $or: [
    { genres: { $exists: false } },
    { genres: { $size: 0 } }
  ]
})</code></pre>

<p>The combination of <code>$exists: false</code>, <code>$size: 0</code>, and <code>null</code> covers all three ways a field can be &ldquo;empty.&rdquo; Always count first before deleting in production.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$size: 0</code> matches empty arrays only</strong> &mdash; not missing fields. Combine with <code>$exists: false</code> for full coverage.</li>
  <li>Run <code>countDocuments</code> with the same filter first &mdash; never blind-delete in production.</li>
  <li>For massive deletes, batch by <code>_id</code> ranges: <code>{ _id: { $gte: lastSeen, $lt: nextChunk } }</code> with <code>$or</code> conditions inside.</li>
  <li>Prefer <strong>soft delete</strong> for any user-visible content &mdash; allows undelete, audit, and compliance with retention policies.</li>
  <li>For routine cleanup of empty-array documents, schedule a job that runs daily during low-traffic hours.</li>
</ul>
'''

ANSWERS[52] = r'''
<pre><code>// Update highest_rating if 10 is greater than current value
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $max: { highest_rating: 10 } }
)

// If highest_rating is 8 -&gt; becomes 10
// If highest_rating is 12 -&gt; unchanged
// If highest_rating is missing -&gt; set to 10

// Across many books at once
db.books.updateMany(
  { genres: "Premium" },
  { $max: { highest_rating: 10 } }
)

// Track the latest activity timestamp
db.books.updateOne(
  { _id: ObjectId("66243abf...") },
  { $max: { last_viewed: new Date() } }
)

// Compare with a dynamic value (use aggregation form)
db.books.updateMany(
  {},
  [{ $set: { highest_rating: { $max: ["$highest_rating", "$current_rating", 5] } } }]
)</code></pre>

<p>The <code>$max</code> update operator sets the field <strong>only if the new value is greater than the existing one</strong> &mdash; or if the field is missing. It&rsquo;s atomic and avoids read-modify-write races.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Atomic</strong> &mdash; safe under concurrent updates without explicit locking.</li>
  <li><strong>Works with any BSON-comparable type</strong> &mdash; numbers, dates, strings (lexicographic).</li>
  <li><strong>Companion: <code>$min</code></strong> &mdash; opposite semantics; only updates if the new value is smaller.</li>
  <li>For comparing to a computed value (e.g. max of two fields), use the <strong>aggregation-pipeline update</strong> form with the <code>$max</code> aggregation operator (different from the update operator).</li>
  <li>Use cases: high-water-mark timestamps (<code>last_seen</code>), monotonic counters that should never decrease, &ldquo;best score so far&rdquo; tracking. <code>$min</code> is the dual for &ldquo;earliest seen&rdquo; or &ldquo;lowest price.&rdquo;</li>
</ul>
'''

ANSWERS[53] = r'''
<pre><code>// Multiples of 5 using $mod &mdash; year % 5 == 0
db.books.find({
  published_year: { $mod: [5, 0] }
})

// Equivalent with $expr (more readable for some)
db.books.find({
  $expr: { $eq: [{ $mod: ["$published_year", 5] }, 0] }
})

// Multiples of 10 (decades)
db.books.find({ published_year: { $mod: [10, 0] } })

// Combined with a range
db.books.find({
  published_year: { $mod: [5, 0], $gte: 2000, $lte: 2025 }
})

// Aggregation form with computed field
db.books.aggregate([
  { $addFields: { year_mod_5: { $mod: ["$published_year", 5] } } },
  { $match:     { year_mod_5: 0 } }
])</code></pre>

<p>The <code>$mod</code> operator takes <code>[divisor, remainder]</code>. <code>{ $mod: [5, 0] }</code> matches when the field divided by 5 has remainder 0 &mdash; i.e., a multiple of 5.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Doesn&rsquo;t use indexes effectively</strong> &mdash; <code>$mod</code> requires computing the modulus per document. Expect a collection scan.</li>
  <li>For frequent &ldquo;every 5 years&rdquo; queries, consider <strong>denormalizing</strong> a <code>decade</code> field on insert and indexing that.</li>
  <li>Practical use cases: <strong>deterministic sampling</strong> (every Nth document), <strong>shard simulation</strong> (partition by id mod N), <strong>round-robin scheduling</strong>.</li>
  <li>For random sampling, prefer <code>$sample</code> in aggregation: <code>{ $sample: { size: 1000 } }</code> &mdash; built for the job and uses a different algorithm.</li>
  <li>For deterministic hashed sampling: <code>{ $expr: { $eq: [{ $mod: [{ $abs: { $hash: "$_id" } }, 100] }, 0] } }</code> &mdash; 1% sample.</li>
</ul>
'''

ANSWERS[54] = r'''
<pre><code>// Total books per published year
db.books.aggregate([
  { $group: { _id: "$published_year", total: { $sum: 1 } } },
  { $sort:  { _id: 1 } }
])

// Output: [{ _id: 2020, total: 12 }, { _id: 2021, total: 18 }, ...]

// With pre-filter and a cleaner output
db.books.aggregate([
  { $match: { published_year: { $exists: true, $type: "int" } } },
  { $group: { _id: "$published_year", total: { $sum: 1 } } },
  { $sort:  { _id: 1 } },
  { $project: { _id: 0, year: "$_id", total: 1 } }
])

// Bucketed by decade instead of year
db.books.aggregate([
  { $group: {
      _id: { $multiply: [{ $floor: { $divide: ["$published_year", 10] } }, 10] },
      total: { $sum: 1 }
  }},
  { $sort: { _id: 1 } }
])

// Materialize the result as a summary collection
db.books.aggregate([
  { $group: { _id: "$published_year", total: { $sum: 1 } } },
  { $merge: { into: "books_per_year", on: "_id", whenMatched: "replace" } }
])</code></pre>

<p>The classic <code>$group</code> + <code>$sum: 1</code> idiom is the &ldquo;count by bucket&rdquo; pattern. Sort by <code>_id</code> for chronological output.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Sort by <code>_id</code></strong> after grouping for chronological order &mdash; group output is otherwise unordered.</li>
  <li>For <strong>large-scale analytical queries</strong>, materialize the result with <code>$merge</code> and refresh on a schedule. Then dashboards read pre-computed rows in O(1).</li>
  <li>For finer time bucketing (per month, week), use <code>$dateTrunc</code> (5.0+) or <code>$dateToString</code> with format <code>%Y-%m</code>.</li>
  <li>For real-time analytics on millions of new events per minute, MongoDB&rsquo;s aggregation framework can struggle &mdash; consider <strong>ClickHouse</strong>, <strong>StarRocks</strong>, <strong>Druid</strong>, or <strong>BigQuery</strong> for that scale.</li>
  <li>Use <strong>MongoDB Atlas Charts</strong> to visualize this aggregation directly without writing UI code.</li>
</ul>
'''

ANSWERS[55] = r'''
<pre><code>// Title contains a numeric digit (regex: any character that is a digit)
db.books.find({ title: /\d/ })

// Equivalent
db.books.find({ title: { $regex: "[0-9]" } })

// Title contains specifically the digit 7
db.books.find({ title: /7/ })

// Title contains a 4-digit year-like number
db.books.find({ title: /\d{4}/ })

// Starts with a digit
db.books.find({ title: /^\d/ })

// Aggregation form
db.books.aggregate([
  { $match: { title: { $regex: "[0-9]" } } }
])</code></pre>

<p>Use <code>\d</code> (or the equivalent character class <code>[0-9]</code>) to match any digit. Without anchors, the engine searches anywhere in the string.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Unanchored regex doesn&rsquo;t use a regular index</strong> &mdash; this is a collection scan. Slow on large collections.</li>
  <li>If you frequently query for digits in titles, <strong>denormalize a flag</strong>: <code>has_digit: true</code>, indexed.</li>
  <li>For more sophisticated content classification (find titles with prices, dates, ISBNs), use <strong>Atlas Search</strong> with regex queries (Lucene&rsquo;s engine handles them faster).</li>
  <li>For titles that need <strong>structured number extraction</strong>, parse on insert/update and store the number in a separate field.</li>
  <li>Watch for false positives: <code>/\d/</code> matches Unicode digits in some locales. Use <code>[0-9]</code> for strict ASCII.</li>
</ul>
'''

ANSWERS[56] = r'''
<pre><code>// Count books per genre after unwinding
db.books.aggregate([
  { $unwind: "$genres" },
  { $sortByCount: "$genres" }
])

// Output: [{ _id: "Fiction", count: 320 }, { _id: "Mystery", count: 87 }, ...]
//         already sorted by count desc

// Same idea manually with $group + $sort
db.books.aggregate([
  { $unwind: "$genres" },
  { $group:  { _id: "$genres", count: { $sum: 1 } } },
  { $sort:   { count: -1 } }
])

// Top 10 genres
db.books.aggregate([
  { $unwind: "$genres" },
  { $sortByCount: "$genres" },
  { $limit: 10 }
])

// $sortByCount on a flat field (e.g., author)
db.books.aggregate([
  { $sortByCount: "$author" }
])</code></pre>

<p><code>$sortByCount</code> is a convenience stage that combines <code>$group</code> by a key, <code>$sum: 1</code> for the count, and <code>$sort: { count: -1 }</code> in one step. It&rsquo;s the cleanest way to express &ldquo;top values by count.&rdquo;</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$unwind</code> first</strong> when the field is an array &mdash; otherwise the entire array becomes a single group key.</li>
  <li><strong>Output is sorted descending by count</strong> automatically &mdash; no extra <code>$sort</code> needed for &ldquo;top N&rdquo; queries.</li>
  <li><strong>Pre-filter with <code>$match</code></strong> when possible &mdash; restricts the data flowing into <code>$unwind</code>, which can otherwise multiply documents.</li>
  <li>For <strong>very large collections</strong>, <code>$unwind</code> can blow up memory. Consider precomputing tag counts via <code>$merge</code> into a summary collection refreshed nightly.</li>
  <li><code>$sortByCount</code> is a single-stage shorthand &mdash; for more complex aggregations (multiple computed fields), use <code>$group</code> + <code>$sort</code> directly.</li>
</ul>
'''

ANSWERS[57] = r'''
<pre><code>// Sort by copies_sold desc and take the top 1
db.books.find().sort({ copies_sold: -1 }).limit(1)

// Get a single document directly
db.books.find().sort({ copies_sold: -1 })[0]

// Or via findOne with sort (driver syntax)
db.books.findOne({}, { sort: { copies_sold: -1 } })

// Aggregation: max value (just the number, no full document)
db.books.aggregate([
  { $group: { _id: null, max_sold: { $max: "$copies_sold" } } }
])

// Highest seller per author
db.books.aggregate([
  { $sort: { author: 1, copies_sold: -1 } },
  { $group: { _id: "$author", top_book: { $first: "$$ROOT" } } },
  { $replaceRoot: { newRoot: "$top_book" } }
])

// Top 3 sellers overall
db.books.find().sort({ copies_sold: -1 }).limit(3)</code></pre>

<p>For &ldquo;the document with the highest X,&rdquo; the simplest form is <code>find().sort().limit(1)</code>. Pair with an index on the sort field for instant retrieval &mdash; otherwise it&rsquo;s a full sort.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Index <code>copies_sold</code></strong>: <code>db.books.createIndex({ copies_sold: -1 })</code>. The first document of a descending index is the max &mdash; instant lookup.</li>
  <li>For just the <strong>max value</strong> (not the document), <code>$group</code> with <code>$max</code> is more efficient.</li>
  <li>For <strong>top per group</strong> (top book per author), use <code>$sort + $group + $first</code> or <code>$top</code> (7.0+) accumulator.</li>
  <li><strong><code>$top</code> accumulator</strong> (7.0+) does this in one stage: <code>{ $group: { _id: "$author", top_book: { $top: { sortBy: { copies_sold: -1 }, output: "$$ROOT" } } } }</code>.</li>
  <li>For ties (multiple books with the same max), add a tiebreaker field to the sort: <code>.sort({ copies_sold: -1, _id: 1 })</code>.</li>
</ul>
'''

ANSWERS[58] = r'''
<pre><code>// Sort by rating ascending (ignoring nulls)
db.books.find({ rating: { $exists: true, $type: "number" } })
        .sort({ rating: 1 })
        .limit(1)

// findOne version
db.books.findOne(
  { rating: { $exists: true, $type: "number" } },
  { sort: { rating: 1 } }
)

// Just the minimum value, not the full document
db.books.aggregate([
  { $match: { rating: { $exists: true, $type: "number" } } },
  { $group: { _id: null, min_rating: { $min: "$rating" } } }
])

// Lowest-rated book per genre
db.books.aggregate([
  { $unwind: "$genres" },
  { $sort:   { genres: 1, rating: 1 } },
  { $group:  { _id: "$genres", worst: { $first: "$$ROOT" } } }
])

// Watch out for nulls
db.books.find().sort({ rating: 1 }).limit(1)
// May return a document with rating: null since null sorts before numbers</code></pre>

<p>The mirror of Q57 &mdash; sort ascending and limit to 1. Be careful with null/missing values: in BSON ordering, <strong>null sorts before numbers</strong>, so the &ldquo;lowest rating&rdquo; might just be a null.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Always filter out null/missing</strong> when computing min over partial data: <code>{ rating: { $type: "number" } }</code>.</li>
  <li><strong>Index <code>rating</code> ascending</strong>: <code>db.books.createIndex({ rating: 1 })</code>. The index supports both min and max lookups.</li>
  <li>For computing min as a single value, <code>$group + $min</code> is idiomatic.</li>
  <li><strong><code>$bottom</code> accumulator</strong> (7.0+) finds the bottom-ranked document per group cleanly: <code>{ $group: { _id: "$genres", worst: { $bottom: { sortBy: { rating: 1 }, output: "$$ROOT" } } } }</code>.</li>
  <li>For dashboards that show &ldquo;weakest performers,&rdquo; combine with sample-size threshold &mdash; a 1-rating book with 1 review isn&rsquo;t the same as one with 1,000.</li>
</ul>
'''

ANSWERS[59] = r'''
<pre><code>// First 5 books by published_year ascending (oldest first)
db.books.find().sort({ published_year: 1 }).limit(5)

// With projection
db.books.find({}, { title: 1, published_year: 1, _id: 0 })
        .sort({ published_year: 1 })
        .limit(5)

// Aggregation form
db.books.aggregate([
  { $sort:  { published_year: 1 } },
  { $limit: 5 }
])

// Within a filtered set
db.books.find({ author: "John Doe" })
        .sort({ published_year: 1 })
        .limit(5)

// As an array (drivers and scripts)
const oldest5 = db.books.find().sort({ published_year: 1 }).limit(5).toArray()</code></pre>

<p>Sort ascending by <code>published_year</code> (oldest first) and take the top 5. With a matching index, this is an instant top-K read &mdash; no in-memory sort.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Index <code>published_year</code></strong> for fast top-K: <code>db.books.createIndex({ published_year: 1 })</code>.</li>
  <li>The <code>limit(5)</code> tells the optimizer it can stop after 5 matches &mdash; combined with the index, it&rsquo;s O(log N + 5) work.</li>
  <li>For <strong>top-K per group</strong> (oldest 5 books per author), use <code>$sort + $group + $push + $slice</code> or the newer <code>$topN</code> accumulator (7.0+).</li>
  <li>For ties (multiple books from the same year), add a tiebreaker: <code>.sort({ published_year: 1, _id: 1 })</code> &mdash; deterministic ordering.</li>
  <li>For <strong>cursor-based pagination</strong>: track the last <code>(year, _id)</code> pair seen and use it as the next page&rsquo;s starting point.</li>
</ul>
'''

ANSWERS[60] = r'''
<pre><code>// Last 5 books (newest by published_year, descending)
db.books.find().sort({ published_year: -1 }).limit(5)

// Aggregation form
db.books.aggregate([
  { $sort:  { published_year: -1 } },
  { $limit: 5 }
])

// To get them in chronological order (oldest of the last 5 first), sort the result
db.books.aggregate([
  { $sort:  { published_year: -1 } },
  { $limit: 5 },
  { $sort:  { published_year: 1 } }
])

// Within a filtered set
db.books.find({ author: "John Doe" })
        .sort({ published_year: -1 })
        .limit(5)

// Last 5 with timestamp tiebreaker (when years tie)
db.books.find().sort({ published_year: -1, _id: -1 }).limit(5)</code></pre>

<p>The dual of the &ldquo;first 5&rdquo; query &mdash; sort descending (newest first) and limit. With an index, this is just as fast as ascending.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Index direction matters</strong> &mdash; an ascending index can be read in reverse for descending queries, so <code>db.books.createIndex({ published_year: 1 })</code> serves both cases.</li>
  <li><strong>For deep pagination</strong> on &ldquo;newest first&rdquo; lists, prefer <strong>cursor-based pagination</strong>: track the last <code>(year, _id)</code> pair and use it as the next page&rsquo;s anchor. Skip-based pagination performs poorly past page 100.</li>
  <li>If the result needs to be in chronological order within a &ldquo;last 5&rdquo; window, re-sort after limiting (as in the third query above).</li>
  <li>For real-time &ldquo;newest&rdquo; feeds, a <strong>change stream</strong> is more efficient than polling &mdash; the app subscribes to inserts and pushes them to clients live.</li>
  <li>Watch the index efficiency: <code>{ published_year: -1, _id: -1 }</code> is a separate index from <code>{ published_year: 1, _id: 1 }</code> &mdash; only build the second if you need direction-specific compound sorts.</li>
</ul>
'''

ANSWERS[61] = r'''
<pre><code>// Books with exactly 3 genres
db.books.find({ genres: { $size: 3 } })

// Aggregation form
db.books.aggregate([
  { $match: { genres: { $size: 3 } } }
])

// $size only matches an exact count &mdash; for ranges use $expr
db.books.find({
  $expr: { $eq: [{ $size: "$genres" }, 3] }
})

// Combined with other filters
db.books.find({
  genres: { $size: 3 },
  published_year: { $gte: 2020 }
})

// Index-friendly alternative: maintain a denormalized count
db.books.updateMany({}, [
  { $set: { genres_count: { $size: { $ifNull: ["$genres", []] } } } }
])
db.books.createIndex({ genres_count: 1 })

db.books.find({ genres_count: 3 })   // uses the index</code></pre>

<p>The <code>$size</code> operator matches arrays of an <strong>exact</strong> length. For ranges, you need <code>$expr</code>; for index-friendly queries, denormalize a count field.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$size</code> can&rsquo;t use a regular array index</strong> &mdash; the multikey index entries point to elements, not array length. Expect a collection scan unless filters narrow the dataset first.</li>
  <li><strong>For frequent queries on array length</strong>, denormalize a count field and index it. Keep the count in sync with <code>$push</code>/<code>$pull</code> updates.</li>
  <li>If <code>genres</code> is sometimes missing, <code>{ genres: { $size: 0 } }</code> won&rsquo;t match &mdash; missing fields don&rsquo;t have a size.</li>
  <li>For analytics on array sizes, use <code>{ $project: { n: { $size: "$genres" } } }</code> + <code>$bucket</code> to histogram the distribution.</li>
  <li>Watch the schema: an empty array (<code>[]</code>) and a missing field have different semantics in MongoDB. Standardize on one in your application.</li>
</ul>
'''

ANSWERS[62] = r'''
<pre><code>// First genre in the array
db.books.aggregate([
  { $project: {
      title: 1,
      first_genre: { $arrayElemAt: ["$genres", 0] }
  }}
])

// Last genre (negative index)
db.books.aggregate([
  { $project: {
      title: 1,
      last_genre: { $arrayElemAt: ["$genres", -1] }
  }}
])

// Modern shorthand &mdash; $first / $last (4.4+)
db.books.aggregate([
  { $project: {
      title: 1,
      first_genre: { $first: "$genres" },
      last_genre:  { $last:  "$genres" }
  }}
])

// Get the first non-null genre
db.books.aggregate([
  { $project: {
      title: 1,
      first_genre: { $ifNull: [{ $arrayElemAt: ["$genres", 0] }, "Uncategorized"] }
  }}
])

// Find the index of a specific genre
db.books.aggregate([
  { $project: {
      title: 1,
      fiction_position: { $indexOfArray: ["$genres", "Fiction"] }
  }}
])</code></pre>

<p>The <code>$arrayElemAt</code> operator returns the array element at a given index. Negative indices count from the end (<code>-1</code> is the last element). Out-of-bounds returns null, not an error.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Modern shorthands</strong> (4.4+): <code>$first: "$genres"</code> for index 0, <code>$last: "$genres"</code> for index -1. Cleaner than <code>$arrayElemAt</code> for those cases.</li>
  <li><strong>Out-of-bounds returns null</strong> &mdash; safe but check with <code>$ifNull</code> if you need a default.</li>
  <li>For <strong>finding by value</strong> within an array, use <code>$indexOfArray</code> &mdash; returns the position or -1 if not found.</li>
  <li>For accessing a deeply nested array element, chain <code>$arrayElemAt</code> &mdash; or use dot notation in projection: <code>{ "genres.0": 1 }</code>.</li>
  <li>For aggregations that need the &ldquo;first matching element&rdquo; based on a condition, use <code>$filter</code> + <code>$arrayElemAt</code>.</li>
</ul>
'''

ANSWERS[63] = r'''
<pre><code>// Case-insensitive equality with collation (preferred &mdash; uses index if available)
db.books.find({ title: "MongoDB Basics" })
        .collation({ locale: "en", strength: 2 })

// strength: 2 = case-insensitive
// strength: 1 = case + accent insensitive ("café" matches "cafe")

// Case-insensitive index for fast index-served queries
db.books.createIndex(
  { title: 1 },
  { collation: { locale: "en", strength: 2 }, name: "title_ci" }
)

// Now this query is index-served
db.books.find({ title: "mongodb basics" }).collation({ locale: "en", strength: 2 })

// Regex alternative (no index unless title_ci is built differently)
db.books.find({ title: { $regex: /^MongoDB Basics$/i } })

// Aggregation form
db.books.aggregate(
  [{ $match: { title: "MongoDB Basics" } }],
  { collation: { locale: "en", strength: 2 } }
)</code></pre>

<p>The cleanest case-insensitive equality uses <strong>collation</strong> &mdash; configure once on the index, query with the matching collation, and the optimizer uses the index. Regex with <code>/i</code> works but typically can&rsquo;t use the index.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Collation strength</strong>: <code>1</code> = base letters only (case + accent insensitive), <code>2</code> = case-insensitive but accent-sensitive, <code>3</code> = full case + accent (default), <code>4</code> = punctuation-aware, <code>5</code> = code-point identity.</li>
  <li><strong>Query collation must match the index collation</strong> for the index to be used. Mismatched collation = collection scan.</li>
  <li>For multilingual fields, pick the appropriate locale (<code>tr</code> for Turkish, <code>de</code> for German, etc.). Default Unicode collation may not handle all language quirks.</li>
  <li>For fuzzy matching (typo tolerance), <strong>collation alone isn&rsquo;t enough</strong> &mdash; use <strong>Atlas Search</strong> with the <code>fuzzy</code> operator.</li>
  <li>For systems with mixed case-sensitive and case-insensitive queries on the same field, build two indexes &mdash; one with collation, one without.</li>
</ul>
'''

ANSWERS[64] = r'''
<pre><code>// Books with at least one review having rating &gt; 4 &mdash; use $elemMatch
db.books.find({
  reviews: { $elemMatch: { rating: { $gt: 4 } } }
})

// Without $elemMatch &mdash; works for single-condition queries
db.books.find({ "reviews.rating": { $gt: 4 } })

// $elemMatch is REQUIRED when you have multiple conditions on the same review
db.books.find({
  reviews: { $elemMatch: { rating: { $gt: 4 }, verified: true } }
})

// Project only matching reviews
db.books.find(
  { "reviews.rating": { $gt: 4 } },
  { title: 1, "reviews.$": 1 }   // returns first matching review only
)

// Aggregation: filter reviews to only those with rating &gt; 4
db.books.aggregate([
  { $project: {
      title: 1,
      good_reviews: {
        $filter: {
          input: "$reviews",
          as:    "r",
          cond:  { $gt: ["$$r.rating", 4] }
      }}
  }}
])</code></pre>

<p>For queries on arrays of subdocuments, <code>$elemMatch</code> is essential when multiple conditions must hold for the <em>same</em> array element. For a single condition, the dot-notation form (<code>"reviews.rating": { $gt: 4 }</code>) is cleaner and equivalent.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Without <code>$elemMatch</code></strong>, multi-condition checks match if separate elements satisfy each condition &mdash; usually a bug.</li>
  <li><strong>Multikey index on <code>reviews.rating</code></strong> speeds these queries: <code>db.books.createIndex({ "reviews.rating": 1 })</code>.</li>
  <li><strong>Positional projection (<code>reviews.$</code>)</strong> returns only the first matching subdocument &mdash; useful for paginating reviews.</li>
  <li>For <strong>filtering arrays in pipelines</strong> (return all matching elements, not just the first), use <code>$filter</code> in <code>$project</code>.</li>
  <li>For high-volume reviews (thousands per book), modeling as a separate <code>reviews</code> collection with <code>book_id</code> reference scales better than embedding.</li>
</ul>
'''

ANSWERS[65] = r'''
<pre><code>// Books with more than 10 reviews (using $expr)
db.books.find({
  $expr: { $gt: [{ $size: { $ifNull: ["$reviews", []] } }, 10] }
})

// More efficient: maintain a denormalized count
db.books.updateMany({}, [
  { $set: { reviews_count: { $size: { $ifNull: ["$reviews", []] } } } }
])
db.books.createIndex({ reviews_count: 1 })

// Now use the index
db.books.find({ reviews_count: { $gt: 10 } })

// Aggregation form (computes on the fly)
db.books.aggregate([
  { $addFields: { reviews_count: { $size: { $ifNull: ["$reviews", []] } } } },
  { $match: { reviews_count: { $gt: 10 } } }
])

// Keep the count in sync on push/pull (atomic update)
db.books.updateOne(
  { _id: bookId },
  {
    $push: { reviews: newReview },
    $inc:  { reviews_count: 1 }
  }
)</code></pre>

<p>For range queries on array length, the index-friendly approach is to <strong>denormalize</strong> a counter field and keep it in sync with each array mutation. Pure <code>$size</code> + <code>$expr</code> always does a collection scan.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Denormalized counts are the standard pattern</strong> for any frequent &ldquo;array length&rdquo; query &mdash; same approach for <code>likes_count</code>, <code>comments_count</code>, <code>followers_count</code>.</li>
  <li>Update count atomically with the array mutation: <code>{ $push: { reviews: r }, $inc: { reviews_count: 1 } }</code>.</li>
  <li>For drift correction, run periodic reconciliation: <code>$set: { reviews_count: { $size: "$reviews" } }</code> in a maintenance window.</li>
  <li>For <strong>extreme array sizes</strong> (10K+ elements per document), embedding becomes inefficient &mdash; documents become large, every update rewrites the array, indexes balloon. Move to a separate collection with foreign-key style linking.</li>
  <li>For real-time popularity ranking by review count, use a <strong>Redis sorted set</strong> for the hot path and persist counts to MongoDB asynchronously.</li>
</ul>
'''

ANSWERS[66] = r'''
<pre><code>// Text search with results sorted by relevance score
db.books.find(
  { $text: { $search: "MongoDB Database" } },
  { title: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })

// Limit to top 10 most relevant
db.books.find(
  { $text: { $search: "MongoDB Database" } },
  { title: 1, author: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } }).limit(10)

// Aggregation form &mdash; more flexible
db.books.aggregate([
  { $match:    { $text: { $search: "MongoDB Database" } } },
  { $addFields:{ score: { $meta: "textScore" } } },
  { $sort:     { score: -1 } },
  { $limit:    10 },
  { $project:  { title: 1, author: 1, score: 1 } }
])

// Filter by minimum relevance
db.books.aggregate([
  { $match:    { $text: { $search: "MongoDB" } } },
  { $addFields:{ score: { $meta: "textScore" } } },
  { $match:    { score: { $gt: 1.0 } } },
  { $sort:     { score: -1 } }
])</code></pre>

<p>The text score is metadata, accessed via <code>{ $meta: "textScore" }</code>. <strong>Project</strong> it to expose it to clients, <strong>sort</strong> by it for relevance ranking. Both project and sort use the same <code>$meta</code> expression.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>The score is a <em>computed</em> field</strong> &mdash; not stored. You must explicitly project it.</li>
  <li><strong>Higher score = more relevant</strong> &mdash; sort descending for top results.</li>
  <li>The score combines: term frequency in the document, inverse document frequency, and field weights (if configured on the index).</li>
  <li>For <strong>BM25-style scoring</strong> (more modern, better calibrated), use <strong>MongoDB Atlas Search</strong> &mdash; same <code>$meta</code> mechanism but powered by Lucene&rsquo;s scoring.</li>
  <li>For <strong>hybrid retrieval</strong> (combine text relevance with other signals like recency, popularity), compute a final score in <code>$addFields</code>: <code>{ final_score: { $add: [{ $multiply: ["$score", 0.7] }, { $multiply: ["$popularity", 0.3] }] } }</code>.</li>
</ul>
'''


ANSWERS[67] = r'''
<pre><code>// $bucket: predefined boundaries
db.books.aggregate([
  { $bucket: {
      groupBy: "$published_year",
      boundaries: [1900, 1950, 1980, 2000, 2010, 2020, 2030],
      default: "other",
      output: { count: { $sum: 1 }, titles: { $push: "$title" } }
  }}
])

// Output:
// { _id: 1900, count: 12, titles: [...] }   // 1900-1949
// { _id: 1950, count: 35, titles: [...] }   // 1950-1979
// { _id: 1980, count: 88, titles: [...] }   // ...
// { _id: "other", count: 4, titles: [...] } // outside boundaries

// $bucket WITHOUT default raises an error if any doc falls outside.
// Always include `default` for production data.

// Decade buckets via $floor (more flexible than fixed boundaries)
db.books.aggregate([
  { $group: {
      _id: { $multiply: [{ $floor: { $divide: ["$published_year", 10] } }, 10] },
      count: { $sum: 1 }
  }},
  { $sort: { _id: 1 } }
])</code></pre>

<p><code>$bucket</code> partitions documents into ranges you define. Each bucket covers <code>[boundary[i], boundary[i+1])</code> &mdash; inclusive lower, exclusive upper. The <code>output</code> object names accumulators just like <code>$group</code>.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Boundaries must be sorted ascending</strong> and the same BSON type as the <code>groupBy</code> value.</li>
  <li><strong><code>default</code> is mandatory</strong> if any document might fall outside the boundaries &mdash; otherwise the stage throws.</li>
  <li>For <strong>auto-balanced buckets</strong> when you don&rsquo;t know the data distribution, use <strong><code>$bucketAuto</code></strong> instead &mdash; specify number of buckets, MongoDB picks the boundaries.</li>
  <li>Use <code>$bucket</code> for histograms in dashboards (price ranges, age groups, time slots) &mdash; pre-computed buckets render in a single round trip.</li>
</ul>
'''

ANSWERS[68] = r'''
<pre><code>// Author stored as an array (multi-author books)
db.books.find({ author: { $type: "array" } })

// By BSON type number (4 = array)
db.books.find({ author: { $type: 4 } })

// Aggregation form (uses $isArray)
db.books.aggregate([
  { $match: { $expr: { $isArray: "$author" } } }
])

// Find both array and string-typed authors (mixed schema)
db.books.find({ author: { $type: ["array", "string"] } })

// Migrate string authors to array form
db.books.updateMany(
  { author: { $type: "string" } },
  [ { $set: { author: ["$author"] } } ]
)</code></pre>

<p>The <code>$type</code> operator filters by BSON type &mdash; useful when a collection has mixed shapes (some books with a single author string, some with an array of co-authors).</p>

<p><strong>Common BSON type aliases</strong>:</p>
<table><thead><tr><th>Alias</th><th>Numeric code</th></tr></thead><tbody>
<tr><td><code>"string"</code></td><td>2</td></tr>
<tr><td><code>"array"</code></td><td>4</td></tr>
<tr><td><code>"object"</code></td><td>3</td></tr>
<tr><td><code>"int"</code> / <code>"long"</code> / <code>"double"</code></td><td>16 / 18 / 1</td></tr>
<tr><td><code>"date"</code></td><td>9</td></tr>
<tr><td><code>"objectId"</code></td><td>7</td></tr>
<tr><td><code>"null"</code></td><td>10</td></tr>
</tbody></table>

<p><strong>Notes</strong>:</p>
<ul>
  <li><code>$type: "number"</code> is a shortcut for any numeric type (int/long/double/decimal).</li>
  <li>For data quality, set <strong>JSON Schema validation</strong> at the collection level so future inserts conform to a single shape.</li>
  <li>Once migrated, normalize on a single shape (always-array is friendlier &mdash; queries handle 1 or N authors uniformly).</li>
</ul>
'''

ANSWERS[69] = r'''
<pre><code>// Output aggregation result to a new collection
db.books.aggregate([
  { $group: {
      _id: "$author",
      total_books: { $sum: 1 },
      avg_year:    { $avg: "$published_year" }
  }},
  { $merge: {
      into: "books_summary",
      on: "_id",
      whenMatched: "replace",
      whenNotMatched: "insert"
  }}
])

// To a different database
db.books.aggregate([
  { $group: { _id: "$author", count: { $sum: 1 } } },
  { $merge: { into: { db: "analytics", coll: "author_counts" }, on: "_id" } }
])

// Pipeline-based merge for partial updates
db.books.aggregate([
  { $group: { _id: "$author", count: { $sum: 1 } } },
  { $merge: {
      into: "books_summary",
      on: "_id",
      whenMatched: [
        { $set: { count: "$$new.count", refreshed_at: new Date() } }
      ],
      whenNotMatched: "insert"
  }}
])</code></pre>

<p><code>$merge</code> writes pipeline output to a target collection &mdash; with smart upsert semantics. Unlike <code>$out</code> (which replaces the whole target), <code>$merge</code> updates matching documents based on a key and leaves others alone.</p>

<p><strong><code>whenMatched</code> options</strong>:</p>
<table><thead><tr><th>Mode</th><th>Behavior</th></tr></thead><tbody>
<tr><td><code>"merge"</code> (default)</td><td>Shallow-merge fields</td></tr>
<tr><td><code>"replace"</code></td><td>Replace the entire matching doc</td></tr>
<tr><td><code>"keepExisting"</code></td><td>Skip update; keep current doc</td></tr>
<tr><td><code>"fail"</code></td><td>Error if a match exists</td></tr>
<tr><td><code>[pipeline]</code></td><td>Run a custom update pipeline</td></tr>
</tbody></table>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Must be the last stage</strong> in the pipeline.</li>
  <li>The <code>on</code> field must be unique-indexed in the target collection (or <code>_id</code>, which is unique by default).</li>
  <li>Use for incremental ETL: nightly rollups, materialized views, event-sourced projections.</li>
</ul>
'''

ANSWERS[70] = r'''
<pre><code>// Reviewed by a specific user (subdocs in reviews array)
db.books.find({ "reviews.user_id": ObjectId("66...") })

// With projection to also return only that review
db.books.find(
  { "reviews.user_id": userId },
  { title: 1, "reviews.$": 1 }
)

// Multiple conditions on the SAME review (use $elemMatch)
db.books.find({
  reviews: { $elemMatch: { user_id: userId, rating: { $gte: 4 } } }
})

// Aggregation: extract the user&rsquo;s reviews across many books
db.books.aggregate([
  { $match: { "reviews.user_id": userId } },
  { $unwind: "$reviews" },
  { $match:  { "reviews.user_id": userId } },
  { $project: { title: 1, review: "$reviews" } }
])

// Index for efficient lookup
db.books.createIndex({ "reviews.user_id": 1 })</code></pre>

<p>Dot notation queries inside arrays of subdocuments. <code>{ "reviews.user_id": userId }</code> matches if <em>any</em> review in the array has the matching <code>user_id</code>.</p>

<p><strong>Watch out for the multi-condition trap</strong>:</p>
<pre><code>// WRONG &mdash; matches if SOME review has the user_id AND ANOTHER has rating &gt;= 4
db.books.find({
  "reviews.user_id": userId,
  "reviews.rating":  { $gte: 4 }
})

// RIGHT &mdash; both conditions must be on the SAME review
db.books.find({
  reviews: { $elemMatch: { user_id: userId, rating: { $gte: 4 } } }
})</code></pre>

<p><strong>Modeling note</strong>: for high review volumes (thousands per book), a separate <code>reviews</code> collection with a <code>book_id</code> reference scales better &mdash; embedded arrays slow down once they get large because every update rewrites the whole document.</p>
'''

ANSWERS[71] = r'''
<pre><code>// Exactly 5 reviews
db.books.find({ reviews: { $size: 5 } })

// Range queries on size: $size doesn&rsquo;t support &gt;/&lt; &mdash; use $expr
db.books.find({ $expr: { $gt: [{ $size: "$reviews" }, 5] } })

// Better: maintain a denormalized count
db.books.updateMany({}, [
  { $set: { reviews_count: { $size: { $ifNull: ["$reviews", []] } } } }
])
db.books.createIndex({ reviews_count: 1 })

// Now exact match is index-backed
db.books.find({ reviews_count: 5 })

// Atomic increment when adding a review
db.books.updateOne(
  { _id: bookId },
  {
    $push: { reviews: newReview },
    $inc:  { reviews_count: 1 }
  }
)</code></pre>

<p><code>$size</code> matches an exact array length only &mdash; it can&rsquo;t express ranges. For <code>&gt;</code>, <code>&lt;</code>, or <code>between</code>, use <code>$expr</code> with <code>$size</code> in an aggregation expression, or maintain a denormalized count.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$size</code> can&rsquo;t use a regular array index</strong> &mdash; the index entries point to individual elements, not the array itself.</li>
  <li><strong>For frequent length-based queries, denormalize</strong> the count into a regular field and index that. Update both atomically (<code>$push</code> + <code>$inc</code>).</li>
  <li>For drift correction, run periodic reconciliation in a maintenance window: <code>$set: { reviews_count: { $size: "$reviews" } }</code>.</li>
  <li><code>$size</code> on a missing field errors out &mdash; wrap with <code>$ifNull</code>: <code>{ $size: { $ifNull: ["$reviews", []] } }</code>.</li>
</ul>
'''

ANSWERS[72] = r'''
<pre><code>// Unwind genres array, then group by genre
db.books.aggregate([
  { $unwind: "$genres" },
  { $group:  { _id: "$genres", count: { $sum: 1 } } },
  { $sort:   { count: -1 } }
])

// Preserve documents whose array is empty or missing
db.books.aggregate([
  { $unwind: { path: "$genres", preserveNullAndEmptyArrays: true } },
  { $group:  { _id: "$genres", count: { $sum: 1 } } }
])

// Include the array index too
db.books.aggregate([
  { $unwind: { path: "$genres", includeArrayIndex: "genre_position" } }
])

// Pre-filter for performance, then unwind
db.books.aggregate([
  { $match:  { published_year: { $gte: 2000 } } },
  { $unwind: "$genres" },
  { $group:  { _id: "$genres", count: { $sum: 1 } } },
  { $sort:   { count: -1 } },
  { $limit:  10 }
])</code></pre>

<p><code>$unwind</code> creates one output document per array element. A book with three genres becomes three pipeline documents &mdash; the rest of the document is duplicated for each.</p>

<p><strong>Watch the explosion cost</strong>: if your collection has 100K books with 5 genres each, <code>$unwind</code> produces 500K pipeline documents. Always:</p>
<ul>
  <li><strong>Filter (<code>$match</code>) before unwinding</strong> to shrink the input.</li>
  <li><strong>Project away unused fields</strong> before unwinding &mdash; smaller docs duplicate more cheaply.</li>
  <li>For frequent group-by-array-element queries, materialize the result with <code>$merge</code> into a summary collection and refresh periodically.</li>
</ul>

<p><strong>Modern alternative</strong>: for one-doc array stats (total count, distinct values), use <code>$size</code> + <code>$reduce</code> + <code>$filter</code> &mdash; no document explosion, much faster.</p>
'''

ANSWERS[73] = r'''
<pre><code>// Books published in the last 5 years
const fiveYearsAgo = new Date().getFullYear() - 5
db.books.find({ published_year: { $gte: fiveYearsAgo } })

// If published_year is an integer
db.books.find({
  published_year: { $gte: new Date().getFullYear() - 5 }
})

// If published_at is a Date type
const cutoff = new Date()
cutoff.setFullYear(cutoff.getFullYear() - 5)
db.books.find({ published_at: { $gte: cutoff } })

// Aggregation with $$NOW (current timestamp at pipeline runtime)
db.books.aggregate([
  { $match: {
      $expr: {
        $gte: [
          "$published_year",
          { $subtract: [{ $year: "$$NOW" }, 5] }
        ]
      }
  }}
])

// With Date-typed field via $dateSubtract (5.0+)
db.books.aggregate([
  { $match: {
      $expr: {
        $gte: [
          "$published_at",
          { $dateSubtract: { startDate: "$$NOW", unit: "year", amount: 5 } }
        ]
      }
  }}
])</code></pre>

<p>Two approaches: compute the cutoff in your application code (simplest), or use <code>$$NOW</code> inside the pipeline (always current, no clock drift between client and server).</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Application-side computation</strong> is fine for one-off queries; ensure your app server&rsquo;s clock is correct (NTP).</li>
  <li><strong>Server-side <code>$$NOW</code></strong> is preferable for stored views, scheduled jobs, or when consistency across clients matters.</li>
  <li><strong>Index <code>published_year</code></strong> for fast range scans: <code>db.books.createIndex({ published_year: -1 })</code>.</li>
  <li><strong>Modern date math (5.0+)</strong>: <code>$dateAdd</code>, <code>$dateSubtract</code>, <code>$dateDiff</code>, <code>$dateTrunc</code> handle calendar quirks (months of varying lengths, leap years, DST) correctly.</li>
</ul>
'''

ANSWERS[74] = r'''
<pre><code>// Find docs where published_year is NOT a number
db.books.find({ published_year: { $not: { $type: "number" } } })

// Or: any specific non-numeric type
db.books.find({ published_year: { $type: "string" } })

// Multiple non-numeric types
db.books.find({ published_year: { $type: ["string", "null", "object"] } })

// Aggregation form
db.books.aggregate([
  { $match: { $expr: { $not: { $isNumber: "$published_year" } } } }
])

// Find docs missing the field entirely
db.books.find({ published_year: { $exists: false } })

// Migration: convert string years to numbers
db.books.updateMany(
  { published_year: { $type: "string" } },
  [ { $set: { published_year: { $toInt: "$published_year" } } } ]
)</code></pre>

<p><code>$type</code> with <code>$not</code> finds documents whose <code>published_year</code> is anything other than a number &mdash; the typical &ldquo;data quality audit&rdquo; query for messy schemas.</p>

<p><strong>BSON numeric types</strong>:</p>
<table><thead><tr><th>Type</th><th>Alias</th><th>Range</th></tr></thead><tbody>
<tr><td>32-bit int</td><td><code>"int"</code></td><td>&plusmn;2.1B</td></tr>
<tr><td>64-bit int</td><td><code>"long"</code></td><td>&plusmn;9.2 quintillion</td></tr>
<tr><td>64-bit float</td><td><code>"double"</code></td><td>IEEE 754</td></tr>
<tr><td>128-bit decimal</td><td><code>"decimal"</code></td><td>34 significant digits</td></tr>
</tbody></table>

<p><code>$type: "number"</code> is a convenience that matches any of int/long/double/decimal &mdash; preferred over listing all four.</p>

<p><strong>Best practice</strong>: enable JSON Schema validation on the collection so new inserts must have <code>published_year</code> as <code>"int"</code>. Combined with a one-time migration of legacy data, you eliminate type drift permanently.</p>
'''

ANSWERS[75] = r'''
<pre><code>// Push a review subdocument
db.books.updateOne(
  { _id: bookId },
  { $push: {
      reviews: {
        user_id:    userId,
        rating:     5,
        comment:    "Excellent",
        created_at: new Date()
      }
  }}
)

// Push and keep array bounded to last 100 reviews
db.books.updateOne(
  { _id: bookId },
  { $push: {
      reviews: {
        $each: [{ user_id: userId, rating: 5, created_at: new Date() }],
        $slice: -100
      }
  }}
)

// Push + atomically maintain count
db.books.updateOne(
  { _id: bookId },
  {
    $push: { reviews: newReview },
    $inc:  { reviews_count: 1 }
  }
)

// Push only if user hasn&rsquo;t reviewed yet (prevent duplicates)
db.books.updateOne(
  { _id: bookId, "reviews.user_id": { $ne: userId } },
  { $push: { reviews: { user_id: userId, rating: 5 } } }
)
// matchedCount = 0 means the user already reviewed</code></pre>

<p><code>$push</code> appends to an array. If the field doesn&rsquo;t exist, MongoDB creates it as a new array of one element. Use <code>$each</code> to append multiple items in one operation.</p>

<p><strong>Important variants</strong>:</p>
<ul>
  <li><strong><code>$slice</code></strong> caps the array length: <code>$slice: -100</code> keeps the last 100 entries &mdash; perfect for rolling buffers.</li>
  <li><strong><code>$position</code></strong> inserts at a specific index instead of appending.</li>
  <li><strong><code>$sort</code></strong> on the embedded subdocuments after pushing: <code>{ $each: [...], $sort: { created_at: -1 } }</code>.</li>
  <li><strong><code>$addToSet</code></strong> instead of <code>$push</code> avoids duplicates &mdash; useful for tags or genres.</li>
  <li><strong>Atomic uniqueness</strong>: combine the push with a filter that checks the array doesn&rsquo;t already contain the value (<code>"reviews.user_id": { $ne: userId }</code>).</li>
</ul>
'''

ANSWERS[76] = r'''
<pre><code>// Remove all reviews with rating &lt; 3
db.books.updateOne(
  { _id: bookId },
  { $pull: { reviews: { rating: { $lt: 3 } } } }
)

// Across all books
db.books.updateMany(
  {},
  { $pull: { reviews: { rating: { $lt: 3 } } } }
)

// Pull and update count atomically (need pipeline-form update)
db.books.updateMany({}, [
  { $set: {
      reviews:       { $filter: { input: "$reviews", cond: { $gte: ["$$this.rating", 3] } } }
  }},
  { $set: {
      reviews_count: { $size: "$reviews" }
  }}
])

// Multi-condition pull
db.books.updateMany(
  {},
  { $pull: {
      reviews: {
        $or: [
          { rating: { $lt: 3 } },
          { is_spam: true }
        ]
      }
  }}
)</code></pre>

<p><code>$pull</code> removes <em>every</em> array element that matches the given condition. The condition syntax is the same as a regular query &mdash; you can combine fields, use comparison operators, or use <code>$or</code>/<code>$and</code>.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Operates on every matching document at once</strong> &mdash; safe and efficient for cleanup operations.</li>
  <li><strong>Counter drift</strong>: if you maintain a denormalized <code>reviews_count</code>, the pipeline-form update above keeps it in sync. The classic <code>$pull</code> form doesn&rsquo;t know how many were removed.</li>
  <li><strong><code>$pullAll</code></strong> takes a list of literal values to remove (no operators allowed): <code>$pullAll: { tags: ["old", "deprecated"] }</code>.</li>
  <li><strong><code>$pop</code></strong> removes one element from the start (<code>-1</code>) or end (<code>1</code>) &mdash; not condition-based.</li>
  <li>For <strong>auditing what was removed</strong>, do a <code>find</code> first, log the matching subdocs, then <code>$pull</code>.</li>
</ul>
'''

ANSWERS[77] = r'''
<pre><code>// Compare two fields of the same document &mdash; spent &gt; budget
db.books.find({ $expr: { $gt: ["$spent", "$budget"] } })

// Boolean expression with multiple comparisons
db.books.find({
  $expr: {
    $and: [
      { $gt: ["$published_year", 2000] },
      { $eq: ["$author", "$editor"] }
    ]
  }
})

// Use aggregation operators in a query
db.books.find({
  $expr: { $eq: [{ $year: "$created_at" }, 2026] }
})

// Inside $lookup with a custom join condition
db.orders.aggregate([
  { $lookup: {
      from: "books",
      let: { bookId: "$book_id" },
      pipeline: [
        { $match: { $expr: { $eq: ["$_id", "$$bookId"] } } },
        { $project: { title: 1, author: 1 } }
      ],
      as: "book"
  }}
])

// In aggregation $match (often clearer than $expr)
db.books.aggregate([
  { $match: { $expr: { $gt: [{ $size: "$reviews" }, 5] } } }
])</code></pre>

<p><code>$expr</code> evaluates an aggregation expression inside a query filter. It&rsquo;s the bridge between query-language filters (which can&rsquo;t reference other fields) and the rich aggregation expression language (which can).</p>

<p><strong>Common uses</strong>:</p>
<ul>
  <li><strong>Field-to-field comparison</strong> &mdash; <code>spent &gt; budget</code> within the same document.</li>
  <li><strong>Computed conditions</strong> &mdash; year-extracted comparisons, length checks, math.</li>
  <li><strong>Custom <code>$lookup</code> joins</strong> &mdash; multi-condition matches that <code>localField</code>/<code>foreignField</code> can&rsquo;t express.</li>
</ul>

<p><strong>Performance caveat</strong>: <code>$expr</code>-based comparisons usually <em>can&rsquo;t use indexes</em> &mdash; MongoDB has to evaluate the expression for every document. Wrap with a regular indexed filter when possible: <code>{ year: { $gte: 2000 }, $expr: { $gt: ["$spent", "$budget"] } }</code>.</p>
'''

ANSWERS[78] = r'''
<pre><code>// Match either of two titles &mdash; $in is the cleanest
db.books.find({ title: { $in: ["MongoDB Basics", "Advanced MongoDB"] } })

// $or form (equivalent for same-field equality, more verbose)
db.books.find({
  $or: [
    { title: "MongoDB Basics" },
    { title: "Advanced MongoDB" }
  ]
})

// Add other filters &mdash; AND-ed at the top level
db.books.find({
  title:  { $in: ["MongoDB Basics", "Advanced MongoDB"] },
  author: "Alice"
})

// Aggregation form
db.books.aggregate([
  { $match: { title: { $in: ["MongoDB Basics", "Advanced MongoDB"] } } },
  { $sort:  { published_year: -1 } }
])

// Case-insensitive any-of (collation index)
db.books.find({ title: { $in: ["MongoDB Basics", "Advanced MongoDB"] } })
        .collation({ locale: "en", strength: 2 })</code></pre>

<p>Use <code>$in</code> for &ldquo;is the value any of these?&rdquo; on a single field &mdash; it&rsquo;s cleaner than <code>$or</code> and the optimizer can do multiple index seeks (one per value) when the field is indexed.</p>

<p><strong>$in vs $or quick reference</strong>:</p>
<table><thead><tr><th>Need</th><th>Use</th></tr></thead><tbody>
<tr><td>Same-field equality, multiple values</td><td><code>$in</code></td></tr>
<tr><td>Different fields per clause</td><td><code>$or</code></td></tr>
<tr><td>Mixed range/equality on same field</td><td><code>$or</code> with internal <code>$in</code></td></tr>
</tbody></table>

<p><strong>Notes</strong>:</p>
<ul>
  <li>Type-sensitive &mdash; <code>{ $in: ["1"] }</code> won&rsquo;t match the number <code>1</code>.</li>
  <li>Inverse <code>$nin</code> matches values <em>not</em> in the list &mdash; but typically can&rsquo;t use an index efficiently.</li>
  <li>For very large <code>$in</code> arrays (10K+ values), consider <code>$lookup</code> against a temporary collection &mdash; faster and avoids query-size limits.</li>
</ul>
'''

ANSWERS[79] = r'''
<pre><code>// Title length between 5 and 15 characters
db.books.find({
  $expr: {
    $and: [
      { $gte: [{ $strLenCP: "$title" }, 5] },
      { $lte: [{ $strLenCP: "$title" }, 15] }
    ]
  }
})

// Aggregation form, often clearer
db.books.aggregate([
  { $match: {
      $expr: {
        $and: [
          { $gte: [{ $strLenCP: "$title" }, 5] },
          { $lte: [{ $strLenCP: "$title" }, 15] }
        ]
      }
  }}
])

// $strLenBytes (byte length, differs for multi-byte chars)
db.books.aggregate([
  { $match: { $expr: { $eq: [{ $strLenBytes: "$title" }, 10] } } }
])

// Maintain denormalized title_len for indexed range queries
db.books.updateMany({}, [
  { $set: { title_len: { $strLenCP: "$title" } } }
])
db.books.createIndex({ title_len: 1 })

// Now indexed range queries work
db.books.find({ title_len: { $gte: 5, $lte: 15 } })</code></pre>

<p>Two string-length operators:</p>
<ul>
  <li><strong><code>$strLenCP</code></strong> &mdash; counts <em>code points</em> (visible characters). What you usually want.</li>
  <li><strong><code>$strLenBytes</code></strong> &mdash; counts UTF-8 bytes. Differs for non-ASCII (each emoji is 4 bytes).</li>
</ul>

<p><strong>Performance note</strong>: <code>$expr</code> with <code>$strLenCP</code> can&rsquo;t use a regular text index &mdash; every document is scanned. For frequent length-based queries, <strong>denormalize a length field</strong> (<code>title_len</code>) and index it. Update both atomically:</p>

<pre><code>db.books.updateOne(
  { _id: bookId },
  [ { $set: { title: "New Title", title_len: { $strLenCP: "New Title" } } } ]
)</code></pre>

<p>Or simpler: compute it client-side (<code>"new title".length</code>) before sending the update.</p>
'''

ANSWERS[80] = r'''
<pre><code>// Add year_difference field (2021 - published_year)
db.books.aggregate([
  { $addFields: {
      year_difference: { $subtract: [2021, "$published_year"] }
  }}
])

// Year difference relative to current year
db.books.aggregate([
  { $addFields: {
      year_difference: { $subtract: [{ $year: "$$NOW" }, "$published_year"] }
  }}
])

// $set is an alias for $addFields (5.0+)
db.books.aggregate([
  { $set: { year_difference: { $subtract: [2021, "$published_year"] } } }
])

// Combine with downstream filtering
db.books.aggregate([
  { $addFields: { years_old: { $subtract: [2026, "$published_year"] } } },
  { $match:     { years_old: { $gte: 10 } } },
  { $sort:      { years_old: -1 } }
])

// Nested calculations
db.books.aggregate([
  { $addFields: {
      year_difference: { $subtract: [2026, "$published_year"] },
      decade:          { $multiply: [{ $floor: { $divide: ["$published_year", 10] } }, 10] }
  }}
])</code></pre>

<p><code>$addFields</code> adds new fields to documents flowing through the pipeline, keeping all existing fields intact. It&rsquo;s the additive cousin of <code>$project</code> &mdash; you don&rsquo;t have to enumerate every field you want to keep.</p>

<p><strong>$addFields vs $project vs $set</strong>:</p>
<table><thead><tr><th>Stage</th><th>Behavior</th></tr></thead><tbody>
<tr><td><code>$addFields</code></td><td>Add or overwrite fields, keep all others</td></tr>
<tr><td><code>$set</code></td><td>Alias for <code>$addFields</code> (clearer intent)</td></tr>
<tr><td><code>$project</code></td><td>Explicit include/exclude list; computed fields too</td></tr>
<tr><td><code>$unset</code></td><td>Remove specific fields</td></tr>
</tbody></table>

<p>Pair <code>$addFields</code> with <code>$match</code> to filter on the computed value &mdash; perfect when the filter condition isn&rsquo;t a literal field but a derivation. For permanent storage of the derived field, use <code>updateMany</code> with a pipeline (or <code>$merge</code> to write to a summary collection).</p>
'''

ANSWERS[81] = r'''
<pre><code>// Books having ANY genre from a given list
db.books.find({ genres: { $in: ["Mystery", "Thriller", "Crime"] } })

// Books having ALL the listed genres
db.books.find({ genres: { $all: ["Mystery", "Thriller"] } })

// Books having NONE of the listed genres
db.books.find({ genres: { $nin: ["Romance", "Fantasy"] } })

// Aggregation form with sort by relevance count
db.books.aggregate([
  { $addFields: {
      matched_genres: {
        $size: {
          $setIntersection: [
            "$genres",
            ["Mystery", "Thriller", "Crime"]
          ]
        }
      }
  }},
  { $match: { matched_genres: { $gt: 0 } } },
  { $sort:  { matched_genres: -1 } }
])

// Index for performance
db.books.createIndex({ genres: 1 })   // multikey index</code></pre>

<p>For arrays, <code>{ field: value }</code> matches if any element equals <code>value</code>. <code>$in</code> generalizes this to multiple values.</p>

<p><strong>Operator quick reference for arrays</strong>:</p>
<table><thead><tr><th>Operator</th><th>Matches when array</th></tr></thead><tbody>
<tr><td><code>$in: [a, b, c]</code></td><td>contains <em>at least one</em> of a, b, or c</td></tr>
<tr><td><code>$all: [a, b]</code></td><td>contains <em>every</em> listed value (in any order)</td></tr>
<tr><td><code>$nin: [a, b]</code></td><td>contains <em>none</em> of the listed values</td></tr>
<tr><td><code>$size: n</code></td><td>has <em>exactly n</em> elements</td></tr>
<tr><td><code>$elemMatch: {...}</code></td><td>has at least one element matching all subconditions</td></tr>
</tbody></table>

<p><strong>Notes</strong>:</p>
<ul>
  <li>A regular index on the array field is automatically a <strong>multikey index</strong> &mdash; one entry per array element. Speeds up <code>$in</code>/<code>$all</code> matching.</li>
  <li>For tag-cloud or faceted search at scale, <strong>Atlas Search</strong>&rsquo;s <code>compound</code> + <code>facet</code> operators are far more powerful than raw <code>$in</code>.</li>
  <li>For ranking by overlap count, the <code>$setIntersection</code> + <code>$size</code> trick above scales well with multikey indexes filtering first.</li>
</ul>
'''

ANSWERS[82] = r'''
<pre><code>// Document: { _id: 1, defaults: { theme: "light", lang: "en" }, custom: { theme: "dark" } }
db.users.aggregate([
  { $project: {
      settings: { $mergeObjects: ["$defaults", "$custom"] }
  }}
])
// Result: settings: { theme: "dark", lang: "en" }

// Combine three subdocuments
db.users.aggregate([
  { $project: {
      profile: {
        $mergeObjects: ["$basic", "$contact", "$preferences"]
      }
  }}
])

// Promote nested object to top level while keeping _id
db.users.aggregate([
  { $replaceRoot: {
      newRoot: { $mergeObjects: [{ _id: "$_id" }, "$profile"] }
  }}
])

// Group accumulator: merge per-user settings from multiple records
db.user_prefs.aggregate([
  { $group: {
      _id: "$user_id",
      merged: { $mergeObjects: "$settings" }
  }}
])</code></pre>

<p><code>$mergeObjects</code> shallow-merges multiple documents. Right-most arguments win when keys conflict &mdash; the typical &ldquo;defaults + overrides&rdquo; pattern.</p>

<p><strong>Behaviors</strong>:</p>
<ul>
  <li><strong>Right-to-left precedence</strong> &mdash; later objects overwrite earlier ones.</li>
  <li><strong>Null/missing</strong> arguments are treated as empty objects &mdash; safe to combine optional fields without null checks.</li>
  <li><strong>Shallow merge only</strong> &mdash; nested objects aren&rsquo;t recursively merged. <code>{ a: { x: 1 } }</code> and <code>{ a: { y: 2 } }</code> merge to <code>{ a: { y: 2 } }</code>, not <code>{ a: { x: 1, y: 2 } }</code>.</li>
  <li><strong>For deep merge</strong>, write a recursive function in application code or use <code>$objectToArray</code> / <code>$arrayToObject</code> creatively.</li>
</ul>

<p>Excellent for layering settings, computed enrichments, or shaping <code>$lookup</code> results into a flat structure.</p>
'''

ANSWERS[83] = r'''
<pre><code>// Case-insensitive regex match on author
db.books.find({ author: /^john/i })

// Object-form (programmatic)
db.books.find({ author: { $regex: "^john", $options: "i" } })

// Better: collation-based equality (uses an index)
db.books.find({ author: "John Doe" })
        .collation({ locale: "en", strength: 2 })

// Build a case-insensitive index for speed
db.books.createIndex(
  { author: 1 },
  { collation: { locale: "en", strength: 2 }, name: "author_ci" }
)

// Now case-insensitive equality is index-backed
db.books.find({ author: "JOHN DOE" })
        .collation({ locale: "en", strength: 2 })

// Anchored, case-insensitive prefix &mdash; uses collation index
db.books.find({ author: /^john/ })
        .collation({ locale: "en", strength: 2 })

// Aggregation form
db.books.aggregate([
  { $match: { author: { $regex: /john/i } } }
])</code></pre>

<p>Three approaches in increasing order of efficiency:</p>
<ol>
  <li><strong>Regex with <code>i</code> option</strong> &mdash; works anywhere, but typically scans the collection.</li>
  <li><strong>Anchored regex (<code>/^name/i</code>) + collation</strong> &mdash; can use a collation index for prefix matching.</li>
  <li><strong>Equality with collation</strong> &mdash; the fastest case-insensitive match; uses a collation index for direct lookup.</li>
</ol>

<p><strong>Collation strength reference</strong>:</p>
<table><thead><tr><th>Strength</th><th>Behavior</th></tr></thead><tbody>
<tr><td>1</td><td>Base characters only (a = A, &agrave; = a)</td></tr>
<tr><td>2</td><td>+ accents (a = A but &agrave; ≠ a)</td></tr>
<tr><td>3 (default)</td><td>+ case-sensitive</td></tr>
<tr><td>5</td><td>Full Unicode-aware comparison</td></tr>
</tbody></table>

<p>For full-text user search (typo tolerance, autocomplete, ranking), use <strong>MongoDB Atlas Search</strong> &mdash; it&rsquo;s purpose-built and faster than any regex.</p>
'''

ANSWERS[84] = r'''
<pre><code>// Project title in uppercase
db.books.aggregate([
  { $project: {
      _id:           0,
      title_upper:   { $toUpper: "$title" },
      author_upper:  { $toUpper: "$author" }
  }}
])

// Combine: uppercase + filter
db.books.aggregate([
  { $project: { title: { $toUpper: "$title" } } },
  { $match:   { title: { $regex: "^MONGO" } } }
])

// $toLower for the inverse
db.books.aggregate([
  { $project: { title_lower: { $toLower: "$title" } } }
])

// Update form &mdash; persist uppercase to disk
db.books.updateMany({}, [
  { $set: { title_upper: { $toUpper: "$title" } } }
])

// Modern alternative: $convert with explicit type/onError
db.books.aggregate([
  { $project: {
      title_upper: {
        $convert: { input: { $toUpper: "$title" }, to: "string", onNull: "" }
      }
  }}
])</code></pre>

<p><code>$toUpper</code> uppercases a string; <code>$toLower</code> lowercases. Both are simple aggregation expressions usable in any stage that accepts expressions: <code>$project</code>, <code>$addFields</code>, <code>$group</code>, etc.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>ASCII-only</strong> case rules &mdash; for full Unicode case folding (Turkish dotless i, German &szlig;), case operations on the application side with a Unicode-aware library are safer.</li>
  <li><strong>Null handling</strong>: <code>$toUpper: null</code> returns <code>""</code>; missing fields also become empty strings. Use <code>$ifNull</code> for explicit fallback values.</li>
  <li><strong>For case-insensitive comparison</strong>, prefer collation indexes over uppercasing both sides &mdash; collation can use indexes; <code>$toUpper</code> in queries cannot.</li>
  <li><strong>Storing both cases</strong> (a <code>title</code> and <code>title_lower</code> field) is a common pattern for fast prefix/equality matching on a case-insensitive lookup &mdash; index <code>title_lower</code>.</li>
</ul>
'''

ANSWERS[85] = r'''
<pre><code>// Add genre only if it&rsquo;s not already in the array
db.books.updateOne(
  { _id: bookId },
  { $addToSet: { genres: "Mystery" } }
)

// Add multiple at once with $each
db.books.updateOne(
  { _id: bookId },
  { $addToSet: { genres: { $each: ["Mystery", "Thriller", "Crime"] } } }
)

// $push with $each (allows duplicates) vs $addToSet (deduplicates)
db.books.updateOne(
  { _id: bookId },
  { $push: { genres: { $each: ["Mystery", "Mystery"] } } }
)
// Array now has TWO "Mystery" entries

db.books.updateOne(
  { _id: bookId },
  { $addToSet: { genres: { $each: ["Mystery", "Mystery"] } } }
)
// Array gets at most ONE "Mystery" added

// Across all books
db.books.updateMany(
  { author: "Alice" },
  { $addToSet: { genres: "Featured" } }
)</code></pre>

<p><code>$addToSet</code> appends values to an array <em>only if they&rsquo;re not already present</em> &mdash; it implements set semantics. <code>$each</code> wraps multiple values for a single update operation.</p>

<p><strong>Equality rules</strong>:</p>
<ul>
  <li>For primitives (strings, numbers), exact equality applies.</li>
  <li>For subdocuments, the <em>entire subdocument</em> must match field-by-field. <code>{ a: 1, b: 2 }</code> ≠ <code>{ b: 2, a: 1 }</code> in some BSON contexts &mdash; canonicalize before adding.</li>
  <li>For arrays, the entire array contents and order must match.</li>
</ul>

<p><strong>Performance note</strong>: <code>$addToSet</code> walks the array each call to check uniqueness. For very large arrays (10K+ elements), consider modeling differently:</p>
<ul>
  <li>Move &ldquo;tags per book&rdquo; into a join collection with a unique compound index.</li>
  <li>Or maintain a separate Redis set for hot-path uniqueness checks.</li>
</ul>
'''

ANSWERS[86] = r'''
<pre><code>// Inclusive range
db.books.find({ published_year: { $gte: 2000, $lte: 2020 } })

// Exclusive bounds
db.books.find({ published_year: { $gt: 2000, $lt: 2020 } })

// Open-ended (year &gt;= 2000)
db.books.find({ published_year: { $gte: 2000 } })

// With sort
db.books.find({ published_year: { $gte: 2000, $lte: 2020 } })
        .sort({ published_year: -1 })

// Aggregation form
db.books.aggregate([
  { $match: { published_year: { $gte: 2000, $lte: 2020 } } }
])

// Date-typed field
db.books.find({
  published_at: {
    $gte: ISODate("2000-01-01"),
    $lt:  ISODate("2021-01-01")
  }
})</code></pre>

<p>Range queries combine multiple comparison operators on the same field inside a single object. The four operators are <code>$gt</code>, <code>$gte</code>, <code>$lt</code>, <code>$lte</code>.</p>

<p><strong>Performance</strong>:</p>
<ul>
  <li>Always index the range field: <code>db.books.createIndex({ published_year: 1 })</code>.</li>
  <li>For range + sort, a compound index matching the sort direction avoids the SORT stage: <code>{ published_year: -1 }</code>.</li>
  <li>The <strong>ESR rule</strong>: equality fields first, sort fields next, range fields <em>last</em> in compound indexes. <code>{ author: 1, published_year: 1 }</code> serves <code>{ author: "Alice", published_year: { $gte: 2000 } }</code> efficiently.</li>
</ul>

<p><strong>Date ranges</strong>: prefer <code>Date</code> over integer year if you ever need finer granularity. <code>$gte: ISODate("2020-01-01")</code> + <code>$lt: ISODate("2021-01-01")</code> covers all of 2020 inclusively. Modern (5.0+): <code>$dateTrunc</code> simplifies week/month/quarter range generation in pipelines.</p>
'''

ANSWERS[87] = r'''
<pre><code>// Project the count of genres
db.books.aggregate([
  { $project: {
      title:        1,
      genres_count: { $size: { $ifNull: ["$genres", []] } }
  }}
])

// $size errors on missing field &mdash; always wrap with $ifNull
db.books.aggregate([
  { $project: { count: { $size: "$genres" } } }
])
// Throws if any document lacks `genres`

// Safer pattern
db.books.aggregate([
  { $project: { count: { $size: { $ifNull: ["$genres", []] } } } }
])

// Combine: count + filter
db.books.aggregate([
  { $project: {
      title:  1,
      count:  { $size: { $ifNull: ["$genres", []] } }
  }},
  { $match: { count: { $gte: 3 } } },
  { $sort:  { count: -1 } }
])

// As a permanent denormalized field
db.books.updateMany({}, [
  { $set: { genres_count: { $size: { $ifNull: ["$genres", []] } } } }
])
db.books.createIndex({ genres_count: 1 })</code></pre>

<p>The <code>$size</code> aggregation expression returns the array length. It&rsquo;s usable anywhere an aggregation expression is accepted &mdash; <code>$project</code>, <code>$addFields</code>, <code>$match</code> (via <code>$expr</code>), <code>$group</code>.</p>

<p><strong>Critical idiom</strong>: always wrap with <code>$ifNull</code>. Without it, any document missing the array field causes the stage to throw &mdash; the entire query fails. <code>{ $size: { $ifNull: ["$genres", []] } }</code> safely returns <code>0</code> for missing fields.</p>

<p><strong>Note</strong>: the <em>query operator</em> <code>$size</code> (used in <code>find()</code>) takes an exact integer and matches arrays of that length. The <em>aggregation operator</em> <code>$size</code> (used in pipelines) returns the length as a value. Same name, different roles.</p>

<p>For frequent length-based queries, denormalize a counter field and update it atomically with array mutations &mdash; far faster than computing on every read.</p>
'''

ANSWERS[88] = r'''
<pre><code>// Find books with duplicate user_id in reviews array
db.books.aggregate([
  { $match: { reviews: { $exists: true, $ne: [] } } },
  { $project: {
      title: 1,
      user_ids:        { $map: { input: "$reviews", as: "r", in: "$$r.user_id" } },
      unique_user_ids: { $setUnion: [{ $map: { input: "$reviews", as: "r", in: "$$r.user_id" } }, []] }
  }},
  { $match: {
      $expr: { $ne: [{ $size: "$user_ids" }, { $size: "$unique_user_ids" }] }
  }}
])

// Cleaner with $let
db.books.aggregate([
  { $match: {
      $expr: {
        $let: {
          vars: { ids: { $map: { input: "$reviews", as: "r", in: "$$r.user_id" } } },
          in:   { $ne: [{ $size: "$$ids" }, { $size: { $setUnion: ["$$ids", []] } }] }
        }
      }
  }}
])

// Find which user_ids are duplicated
db.books.aggregate([
  { $match: { _id: bookId } },
  { $unwind: "$reviews" },
  { $group: {
      _id: "$reviews.user_id",
      count: { $sum: 1 }
  }},
  { $match: { count: { $gt: 1 } } }
])

// Prevent duplicates with $addToSet semantics
db.books.updateOne(
  { _id: bookId, "reviews.user_id": { $ne: userId } },
  { $push: { reviews: { user_id: userId, rating: 5 } } }
)</code></pre>

<p>The trick: extract the field with <code>$map</code>, then compare <code>$size</code> against <code>$size</code> of <code>$setUnion</code>. If the array has duplicates, the de-duplicated version will be shorter.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Prevention &gt; detection</strong>: enforce uniqueness at write time using a query precondition (the <code>$ne</code> filter pattern above). This avoids needing to scan for duplicates later.</li>
  <li>For high-cardinality data, model reviews in a separate collection with a unique compound index <code>{ book_id: 1, user_id: 1 }</code> &mdash; the database enforces uniqueness for free.</li>
  <li>Periodic data-quality audits using the aggregation above can identify drift; fix with a one-time deduplication update.</li>
</ul>
'''

ANSWERS[89] = r'''
<pre><code>// Project is_recent based on published_year
db.books.aggregate([
  { $project: {
      title: 1,
      published_year: 1,
      is_recent: {
        $cond: { if: { $gte: ["$published_year", 2020] }, then: true, else: false }
      }
  }}
])

// Shorthand array form: [condition, then, else]
db.books.aggregate([
  { $project: {
      title: 1,
      is_recent: { $cond: [{ $gte: ["$published_year", 2020] }, true, false] }
  }}
])

// Even shorter: comparison directly returns a boolean
db.books.aggregate([
  { $project: {
      title: 1,
      is_recent: { $gte: ["$published_year", 2020] }
  }}
])

// Tiered classification (better with $switch)
db.books.aggregate([
  { $project: {
      era: {
        $switch: {
          branches: [
            { case: { $gte: ["$published_year", 2020] }, then: "recent" },
            { case: { $gte: ["$published_year", 2000] }, then: "modern" },
            { case: { $gte: ["$published_year", 1980] }, then: "older" }
          ],
          default: "classic"
        }
      }
  }}
])

// Conditional field value (with NULL fallback)
db.books.aggregate([
  { $project: {
      title: 1,
      effective_year: { $cond: [{ $gt: ["$published_year", 0] }, "$published_year", null] }
  }}
])</code></pre>

<p><code>$cond</code> is the ternary if-then-else of aggregation. Two syntaxes work identically: the object form (<code>{ if, then, else }</code>) and the shorthand array (<code>[cond, then, else]</code>).</p>

<p><strong>For multi-way conditionals (3+ branches), prefer <code>$switch</code></strong> &mdash; nested <code>$cond</code> becomes unreadable past two levels. <code>$switch</code> evaluates branches in order and returns the first match&rsquo;s value; the <code>default</code> branch is required.</p>

<p>Both work in any stage that accepts expressions &mdash; <code>$project</code>, <code>$addFields</code>, <code>$group</code>, <code>$match</code> (via <code>$expr</code>).</p>
'''

ANSWERS[90] = r'''
<pre><code>// Books missing the rating field
db.books.find({ rating: { $exists: false } })

// Add an index of missing-field documents (sparse alternative)
db.books.find({ rating: null })
// CAUTION: $eq null matches docs where rating is explicitly null OR missing entirely

// To distinguish: use $exists
db.books.find({ rating: { $exists: false } })           // truly missing
db.books.find({ rating: { $type: "null" } })            // explicitly null
db.books.find({ rating: null, $expr: { $eq: ["$rating", null] } })  // either

// Aggregation form
db.books.aggregate([
  { $match: { rating: { $exists: false } } }
])

// Backfill missing rating with default
db.books.updateMany(
  { rating: { $exists: false } },
  { $set: { rating: 0 } }
)</code></pre>

<p>The <code>$exists</code> operator is the only reliable way to distinguish between &ldquo;missing&rdquo; and &ldquo;explicitly null&rdquo; &mdash; an important distinction for schema migrations and audits.</p>

<p><strong>Field state matrix</strong>:</p>
<table><thead><tr><th>Document</th><th><code>{ rating: null }</code> matches?</th><th><code>{ rating: { $exists: false } }</code> matches?</th></tr></thead><tbody>
<tr><td>Missing field</td><td>Yes</td><td>Yes</td></tr>
<tr><td>Explicitly null</td><td>Yes</td><td>No</td></tr>
<tr><td>Has any other value</td><td>No</td><td>No</td></tr>
</tbody></table>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong><code>$exists: true</code> can use an index</strong>; <code>$exists: false</code> typically can&rsquo;t (it&rsquo;s the absence of an index entry).</li>
  <li>For migrations adding a new field with a default, run a one-time <code>updateMany</code> filtered by <code>{ field: { $exists: false } }</code> to backfill.</li>
  <li><strong>Sparse indexes</strong> (<code>{ sparse: true }</code>) only index documents where the field exists &mdash; useful when most documents lack the field but you still want fast queries on the few that do.</li>
</ul>
'''

ANSWERS[91] = r'''
<pre><code>// Update existing summary docs (or insert if new)
db.books.aggregate([
  { $group: {
      _id: "$author",
      total_books: { $sum: 1 },
      avg_year:    { $avg: "$published_year" }
  }},
  { $merge: {
      into: "books_summary",
      on: "_id",
      whenMatched: "merge",          // shallow-merge fields
      whenNotMatched: "insert"       // create if missing
  }}
])

// Replace entire matching doc
{ $merge: {
    into: "books_summary",
    on: "_id",
    whenMatched: "replace",
    whenNotMatched: "insert"
}}

// Custom update pipeline on match (preserve some fields, refresh others)
{ $merge: {
    into: "books_summary",
    on: "_id",
    whenMatched: [
      { $set: {
          total_books: "$$new.total_books",
          avg_year:    "$$new.avg_year",
          last_refreshed: "$$NOW"
      }}
    ],
    whenNotMatched: "insert"
}}

// Skip update if exists (insert-only)
{ $merge: { into: "books_summary", on: "_id", whenMatched: "keepExisting", whenNotMatched: "insert" } }

// Different DB target
{ $merge: { into: { db: "analytics", coll: "books_summary" } } }</code></pre>

<p><code>$merge</code> is the proper ETL primitive in MongoDB. Unlike <code>$out</code> (which replaces the entire collection), <code>$merge</code> upserts based on a key, leaving non-matching documents untouched.</p>

<p><strong><code>whenMatched</code> options</strong>:</p>
<table><thead><tr><th>Mode</th><th>Use case</th></tr></thead><tbody>
<tr><td><code>"merge"</code> (default)</td><td>Shallow-merge fields &mdash; new wins on overlap</td></tr>
<tr><td><code>"replace"</code></td><td>Full document replacement</td></tr>
<tr><td><code>"keepExisting"</code></td><td>Skip; useful for &ldquo;insert only if new&rdquo;</td></tr>
<tr><td><code>"fail"</code></td><td>Error on any match (data validation)</td></tr>
<tr><td><code>[pipeline]</code></td><td>Custom update logic with access to <code>$$new</code></td></tr>
</tbody></table>

<p>Use this for nightly rollups, materialized views, or event-sourced projections &mdash; refresh incrementally without rebuilding from scratch.</p>
'''

ANSWERS[92] = r'''
<pre><code>// Object-form $regex with explicit options
db.books.find({ title: { $regex: "Mongo.*Guide", $options: "i" } })

// Equivalent JS regex literal
db.books.find({ title: /Mongo.*Guide/i })

// Programmatic regex from user input (sanitize first!)
const userInput = "MongoDB"
const escaped = userInput.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
db.books.find({ title: { $regex: escaped, $options: "i" } })

// Common pattern flags
db.books.find({ title: { $regex: "^MongoDB",          $options: "i" } })  // prefix
db.books.find({ title: { $regex: "Database$",         $options: "i" } })  // suffix
db.books.find({ title: { $regex: "\\bMongoDB\\b",     $options: "i" } })  // word boundary
db.books.find({ title: { $regex: "[A-Z]",             $options: ""  } })  // contains uppercase
db.books.find({ title: { $regex: "^MongoDB|^Mongoose" } })                // alternation

// Multi-line / dotall
db.books.find({ description: { $regex: "Mongo.*$", $options: "ms" } })</code></pre>

<p>Two equivalent forms: JavaScript regex literal (<code>/pattern/flags</code>) and the explicit object (<code>{ $regex: "pattern", $options: "flags" }</code>). The object form is required when constructing the pattern from variables &mdash; you can&rsquo;t interpolate into a literal.</p>

<p><strong>Regex flags</strong>:</p>
<table><thead><tr><th>Flag</th><th>Meaning</th></tr></thead><tbody>
<tr><td><code>i</code></td><td>Case-insensitive</td></tr>
<tr><td><code>m</code></td><td>Multiline (^ / $ match line boundaries)</td></tr>
<tr><td><code>s</code></td><td>Dotall (<code>.</code> matches newlines)</td></tr>
<tr><td><code>x</code></td><td>Extended (allow whitespace and comments)</td></tr>
</tbody></table>

<p><strong>Critical security note</strong>: never pass raw user input into <code>$regex</code> &mdash; sanitize special characters first or you&rsquo;re vulnerable to <strong>ReDoS</strong> (catastrophic backtracking can lock up the server). For production user search, use <strong>Atlas Search</strong>; it&rsquo;s far more efficient and safer.</p>
'''

ANSWERS[93] = r'''
<pre><code>// Project only reviews with rating &gt; 4
db.books.aggregate([
  { $project: {
      title: 1,
      top_reviews: {
        $filter: {
          input: "$reviews",
          as:    "review",
          cond:  { $gt: ["$$review.rating", 4] }
      }
    }
  }}
])

// With limit (5.0+) &mdash; stops after N matches
db.books.aggregate([
  { $project: {
      title: 1,
      first_three_top_reviews: {
        $filter: {
          input: "$reviews",
          as:    "r",
          cond:  { $gt: ["$$r.rating", 4] },
          limit: 3
      }
    }
  }}
])

// Multi-condition filter with $and
db.books.aggregate([
  { $project: {
      verified_top_reviews: {
        $filter: {
          input: "$reviews",
          cond:  { $and: [
            { $gt: ["$$this.rating", 4] },
            { $eq: ["$$this.verified", true] }
          ]}
      }
    }
  }}
])

// Combine $filter + $size for &ldquo;count of matching elements&rdquo;
db.books.aggregate([
  { $project: {
      top_review_count: {
        $size: { $filter: { input: "$reviews", as: "r", cond: { $gt: ["$$r.rating", 4] } } }
      }
  }}
])</code></pre>

<p><code>$filter</code> returns a subset of an array based on a condition &mdash; the equivalent of JavaScript&rsquo;s <code>Array.filter()</code>. Inside <code>cond</code>, the loop variable defaults to <code>$$this</code> (or you name it via <code>as</code> and use <code>$$varname</code>).</p>

<p><strong>Why <code>$filter</code> over <code>$unwind + $match + $group</code></strong>:</p>
<ul>
  <li><strong>No document explosion</strong> &mdash; the array stays inside the original document.</li>
  <li><strong>Faster</strong> &mdash; fewer pipeline stages, less memory pressure.</li>
  <li><strong>Cleaner output</strong> &mdash; you keep the original document shape.</li>
</ul>

<p>Pair <code>$filter</code> with <code>$map</code> (transform each element), <code>$reduce</code> (fold to single value), and <code>$arrayElemAt</code> (positional access) to handle most array operations without leaving the document.</p>
'''

ANSWERS[94] = r'''
<pre><code>// Add last_modified to all documents (current time)
db.books.updateMany(
  {},
  { $set: { last_modified: new Date() } }
)

// $currentDate &mdash; uses server time at write
db.books.updateMany(
  {},
  { $currentDate: { last_modified: true } }
)

// Difference: $set captures the value once (when the query is sent);
// $currentDate evaluates per-document on the server.
// For batch updates these are essentially identical, but $currentDate is
// the right choice for sharded clusters where clock skew might matter.

// Add last_modified only if missing (one-time backfill)
db.books.updateMany(
  { last_modified: { $exists: false } },
  { $currentDate: { last_modified: true } }
)

// Use a Timestamp instead of Date (BSON Timestamp is special &mdash; for oplog ordering)
db.books.updateMany(
  {},
  { $currentDate: { last_modified: { $type: "timestamp" } } }
)

// Production pattern: keep last_modified updated automatically on every change
db.books.updateOne(
  { _id: bookId },
  {
    $set:        { title: "New Title" },
    $currentDate: { last_modified: true }
  }
)</code></pre>

<p>Two operators write the current time: <code>$set: { field: new Date() }</code> uses the application&rsquo;s clock, <code>$currentDate: { field: true }</code> uses the MongoDB server&rsquo;s clock at write time. The latter avoids application clock skew issues.</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><strong>Application pattern</strong>: every write should bump <code>last_modified</code> &mdash; pair every <code>$set</code> with <code>$currentDate</code>. Drivers like <strong>Mongoose</strong> automate this via <code>{ timestamps: true }</code> in the schema.</li>
  <li><strong>For audit trails</strong>, store <code>created_at</code> (set once via <code>$setOnInsert</code> in upserts) and <code>last_modified</code> (every write).</li>
  <li><strong>For change-data-capture</strong>, MongoDB&rsquo;s <strong>change streams</strong> are the proper tool &mdash; they emit a stream of every change without needing to read from the documents.</li>
</ul>
'''

ANSWERS[95] = r'''
<pre><code>// Books whose genres array has only unique values
db.books.find({
  $expr: {
    $eq: [
      { $size: "$genres" },
      { $size: { $setUnion: ["$genres", []] } }
    ]
  }
})

// Aggregation form (clearer)
db.books.aggregate([
  { $match: {
      $expr: {
        $eq: [
          { $size: { $ifNull: ["$genres", []] } },
          { $size: { $setUnion: [{ $ifNull: ["$genres", []] }, []] } }
        ]
      }
  }}
])

// Conversely &mdash; find books with duplicate genres (data quality)
db.books.aggregate([
  { $match: {
      $expr: {
        $ne: [
          { $size: "$genres" },
          { $size: { $setUnion: ["$genres", []] } }
        ]
      }
  }}
])

// Migrate: deduplicate genres in place
db.books.updateMany({}, [
  { $set: { genres: { $setUnion: ["$genres", []] } } }
])

// Prevention: use $addToSet on writes (never $push)
db.books.updateOne(
  { _id: bookId },
  { $addToSet: { genres: { $each: ["Mystery", "Thriller"] } } }
)</code></pre>

<p>The technique: compare <code>$size</code> of the original array to <code>$size</code> of its de-duplicated form. If they match, the array contains only unique values. <code>$setUnion</code> with an empty array is the canonical way to deduplicate an array.</p>

<p><strong>Set-family operators on arrays</strong>:</p>
<table><thead><tr><th>Operator</th><th>Returns</th></tr></thead><tbody>
<tr><td><code>$setUnion</code></td><td>Combined unique elements</td></tr>
<tr><td><code>$setIntersection</code></td><td>Elements in all input arrays</td></tr>
<tr><td><code>$setDifference</code></td><td>Elements in first array only</td></tr>
<tr><td><code>$setEquals</code></td><td>Boolean &mdash; sets are equal</td></tr>
<tr><td><code>$setIsSubset</code></td><td>Boolean &mdash; first is subset of second</td></tr>
</tbody></table>

<p><strong>Best practice</strong>: prevent duplicates at write time using <code>$addToSet</code> instead of <code>$push</code>. The detection query above is for migrations and audits; new code should never produce duplicates.</p>
'''

ANSWERS[96] = r'''
<pre><code>// published_year is an integer &mdash; build a date first, then format
db.books.aggregate([
  { $project: {
      title: 1,
      year_str: {
        $dateToString: {
          format: "%Y",
          date:   { $dateFromParts: { year: "$published_year" } }
        }
      }
  }}
])

// Or simpler &mdash; just convert int to string
db.books.aggregate([
  { $project: {
      title: 1,
      year_str: { $toString: "$published_year" }
  }}
])

// If the field is already a Date
db.books.aggregate([
  { $project: {
      title: 1,
      iso_date:    { $dateToString: { format: "%Y-%m-%d", date: "$published_at" } },
      with_tz:     { $dateToString: { format: "%Y-%m-%d %H:%M", date: "$published_at", timezone: "Asia/Kolkata" } },
      readable:    { $dateToString: { format: "%d %B %Y", date: "$published_at" } }
  }}
])

// Common format codes
// %Y year, %m month (01-12), %d day (01-31)
// %H hour (24h), %M minute, %S second
// %A weekday name, %B month name
// %j day of year, %V ISO week number</code></pre>

<p><code>$dateToString</code> formats a Date as a string. If your <code>published_year</code> is just an integer (not a Date), use <code>$toString</code> instead, or wrap with <code>$dateFromParts</code> to construct a Date first.</p>

<p><strong>Modern alternatives (5.0+)</strong>:</p>
<ul>
  <li><strong><code>$dateTrunc</code></strong> &mdash; truncate to a unit (day, week, month, quarter, year). Cleaner for time-bucketing than format-and-group.</li>
  <li><strong><code>$dateAdd</code> / <code>$dateSubtract</code> / <code>$dateDiff</code></strong> &mdash; arithmetic on dates with timezone awareness, handle DST and varying month lengths correctly.</li>
  <li><strong><code>$dateFromString</code></strong> &mdash; parse strings back to Dates with format/timezone hints.</li>
</ul>

<p>For analytics dashboards, push date arithmetic to <strong>Atlas Charts</strong> or your warehouse (BigQuery, Snowflake) &mdash; far richer functions and faster on large data.</p>
'''

ANSWERS[97] = r'''
<pre><code>// Titles containing any non-alphanumeric character (besides space)
db.books.find({ title: /[^a-zA-Z0-9 ]/ })

// More targeted: specific special chars
db.books.find({ title: /[!@#$%^&amp;*(){}\[\]&lt;&gt;?\/]/ })

// Regex with $options
db.books.find({ title: { $regex: "[^a-zA-Z0-9 ]", $options: "" } })

// Find titles with non-ASCII characters
db.books.find({ title: /[^\x00-\x7F]/ })

// Aggregation form
db.books.aggregate([
  { $match: { title: { $regex: /[^\w\s]/ } } }
])

// Specific punctuation
db.books.find({ title: /[:;,.!?]/ })

// Emojis (BMP and Astral planes)
db.books.find({ title: /[\u{1F300}-\u{1FFFF}]/u })</code></pre>

<p>Build a regex character class describing what you consider &ldquo;special&rdquo;. <code>[^a-zA-Z0-9 ]</code> matches anything that&rsquo;s not a letter, digit, or space &mdash; everything else (punctuation, symbols, emoji, accented characters) is &ldquo;special&rdquo;.</p>

<p><strong>Common patterns</strong>:</p>
<table><thead><tr><th>Pattern</th><th>Matches</th></tr></thead><tbody>
<tr><td><code>/[^\w\s]/</code></td><td>Any character that isn&rsquo;t word (letter/digit/_) or whitespace</td></tr>
<tr><td><code>/[!@#$%^&amp;*]/</code></td><td>Specific punctuation</td></tr>
<tr><td><code>/[^\x00-\x7F]/</code></td><td>Non-ASCII (any character above 127)</td></tr>
<tr><td><code>/[\p{P}]/u</code></td><td>Unicode punctuation property (works in modern JS but check MongoDB version)</td></tr>
</tbody></table>

<p><strong>Performance note</strong>: unanchored regex queries do a collection scan &mdash; slow on large collections. For frequent &ldquo;contains special chars&rdquo; queries, denormalize a flag at write time:</p>

<pre><code>db.books.updateMany({}, [
  { $set: { has_special_chars: { $regexMatch: { input: "$title", regex: /[^\w\s]/ } } } }
])
db.books.createIndex({ has_special_chars: 1 })</code></pre>
'''

ANSWERS[98] = r'''
<pre><code>// Join books with authors collection
db.books.aggregate([
  { $lookup: {
      from:         "authors",
      localField:   "author_id",
      foreignField: "_id",
      as:           "author_info"
  }},
  { $unwind: "$author_info" }   // flatten the 1-element array
])

// Project useful fields
db.books.aggregate([
  { $lookup: {
      from:         "authors",
      localField:   "author_id",
      foreignField: "_id",
      as:           "author_info"
  }},
  { $unwind: "$author_info" },
  { $project: {
      title:       1,
      author_name: "$author_info.name",
      bio:         "$author_info.bio"
  }}
])

// Pipeline-form $lookup &mdash; filter / project on the joined side
db.books.aggregate([
  { $lookup: {
      from:     "authors",
      let:      { aid: "$author_id" },
      pipeline: [
        { $match:   { $expr: { $and: [{ $eq: ["$_id", "$$aid"] }, { $eq: ["$active", true] }] } } },
        { $project: { name: 1, bio: 1, country: 1 } }
      ],
      as: "author_info"
  }},
  { $unwind: { path: "$author_info", preserveNullAndEmptyArrays: true } }
])

// Index the foreign field for performance
db.authors.createIndex({ _id: 1 })   // already there by default</code></pre>

<p><code>$lookup</code> is MongoDB&rsquo;s LEFT OUTER JOIN. <code>localField</code> in the source matches <code>foreignField</code> in the target; results land in the <code>as</code> array (always an array, even if there&rsquo;s only one match).</p>

<p><strong>Always <code>$unwind</code> the result</strong> if you expect a one-to-one relationship &mdash; the array form is awkward to use downstream.</p>

<p><strong>Pipeline-form <code>$lookup</code></strong> is more flexible than the simple form &mdash; you can filter, project, or even chain more lookups on the joined side. Use <code>let</code> to expose source-side fields as <code>$$variables</code>.</p>

<p><strong>Performance tips</strong>:</p>
<ul>
  <li>Always index the <code>foreignField</code> on the joined collection.</li>
  <li><code>$match</code> upstream to reduce input volume before joining.</li>
  <li>For frequent joins, consider embedding the looked-up data into the source document &mdash; MongoDB rewards designing for access patterns.</li>
</ul>
'''

ANSWERS[99] = r'''
<pre><code>// Push a review and ensure reviews array exists (using $push)
db.books.updateOne(
  { _id: bookId },
  { $push: { reviews: { user_id: userId, rating: 5, comment: "Great" } } }
)
// $push creates the array if missing &mdash; same operation either way

// More explicit: pipeline-form ensures the array is initialized
db.books.updateOne(
  { _id: bookId },
  [
    { $set: {
        reviews: { $ifNull: ["$reviews", []] }
    }},
    { $set: {
        reviews: { $concatArrays: [
          "$reviews",
          [{ user_id: userId, rating: 5, comment: "Great" }]
        ]}
    }}
  ]
)

// $addToSet variant (no duplicates by user_id requires extra logic)
db.books.updateOne(
  { _id: bookId, "reviews.user_id": { $ne: userId } },
  { $push: { reviews: { user_id: userId, rating: 5 } } }
)

// Atomic: push + maintain count + update last_modified
db.books.updateOne(
  { _id: bookId },
  {
    $push:        { reviews: newReview },
    $inc:         { reviews_count: 1 },
    $currentDate: { last_modified: true }
  }
)

// Upsert pattern: create the book with reviews if it doesn&rsquo;t exist
db.books.updateOne(
  { _id: bookId },
  {
    $setOnInsert: { _id: bookId, title: "Unknown", reviews: [] },
    $push:        { reviews: newReview }
  },
  { upsert: true }
)</code></pre>

<p><code>$push</code> already handles the &ldquo;array doesn&rsquo;t exist&rdquo; case &mdash; it creates the field as a one-element array if missing. The trickier requirements (no duplicate per user, atomic count, fresh document on first insert) need the patterns above.</p>

<p><strong>Patterns by need</strong>:</p>
<ul>
  <li><strong>Just append</strong>: <code>$push</code>.</li>
  <li><strong>Append unique</strong>: filter precondition (<code>"reviews.user_id": { $ne: userId }</code>) + <code>$push</code>.</li>
  <li><strong>Append with sibling state</strong> (count, timestamp): combine <code>$push</code> + <code>$inc</code> + <code>$currentDate</code> in one update &mdash; atomic at the document level.</li>
  <li><strong>Append or create document</strong>: <code>upsert: true</code> + <code>$setOnInsert</code> for initial fields.</li>
</ul>

<p>For high-volume reviews, model in a separate collection &mdash; embedded arrays with thousands of elements degrade write performance because every update rewrites the whole document.</p>
'''

ANSWERS[100] = r'''
<pre><code>// Average rating per book + sort by it
db.books.aggregate([
  { $project: {
      title:      1,
      author:     1,
      avg_rating: { $avg: "$reviews.rating" }
  }},
  { $sort: { avg_rating: -1 } }
])

// Filter out books with no reviews
db.books.aggregate([
  { $match: { reviews: { $exists: true, $ne: [] } } },
  { $project: {
      title: 1,
      avg_rating:     { $avg: "$reviews.rating" },
      reviews_count:  { $size: "$reviews" }
  }},
  { $sort: { avg_rating: -1 } }
])

// Top 10 highest-rated with at least 5 reviews (Bayesian-style filter)
db.books.aggregate([
  { $project: {
      title: 1,
      avg_rating:    { $avg: "$reviews.rating" },
      reviews_count: { $size: { $ifNull: ["$reviews", []] } }
  }},
  { $match: { reviews_count: { $gte: 5 } } },
  { $sort:  { avg_rating: -1 } },
  { $limit: 10 }
])

// Round to 2 decimals for cleaner output
db.books.aggregate([
  { $project: {
      title: 1,
      avg_rating: { $round: [{ $avg: "$reviews.rating" }, 2] }
  }},
  { $sort: { avg_rating: -1 } }
])

// Materialize for fast reads (refresh nightly)
db.books.aggregate([
  { $project: {
      title:         1,
      avg_rating:    { $round: [{ $avg: "$reviews.rating" }, 2] },
      reviews_count: { $size: { $ifNull: ["$reviews", []] } }
  }},
  { $merge: { into: "book_ratings", on: "_id", whenMatched: "replace", whenNotMatched: "insert" } }
])</code></pre>

<p>The trick: <code>$avg</code> works directly on an array of values via dot notation. <code>{ $avg: "$reviews.rating" }</code> averages every <code>rating</code> across the embedded reviews array &mdash; no <code>$unwind</code> needed.</p>

<p><strong>Production tips</strong>:</p>
<ul>
  <li><strong>Filter low-review books</strong> &mdash; a single 5-star review shouldn&rsquo;t outrank a book with 1000 reviews averaging 4.8. Apply a <code>reviews_count &gt;= N</code> cutoff or use a <strong>Bayesian average</strong> formula that pulls towards a global mean for books with few reviews.</li>
  <li><strong>Materialize via <code>$merge</code></strong> into a <code>book_ratings</code> collection refreshed periodically &mdash; far cheaper than recomputing on every page load.</li>
  <li><strong>For real-time leaderboards</strong>, maintain Redis sorted sets keyed by book ID, with the average rating as the score. MongoDB stores ground truth; Redis serves hot reads.</li>
  <li><strong>Modern alternative</strong>: <strong>MongoDB Atlas Search</strong>&rsquo;s <code>function</code> scoring lets you blend relevance, recency, and rating into a single search ranking signal.</li>
</ul>
'''
