"""MongoDB Basic — Q1-100 detailed answers.

Style: Basic-level conventions. 80-150 word concise prose explanations.
Simple JS shell / Mongo driver examples. Comparison tables for related concepts.
Beginner-friendly tone. ~1,500-2,500 chars per answer.
"""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''
<p><strong>MongoDB</strong> is an open-source <strong>document database</strong> &mdash; instead of storing data in rows and columns like a relational database, it stores it in flexible JSON-like documents grouped into <em>collections</em>. It was first released in 2009 by 10gen (now MongoDB, Inc.) and is the most popular NoSQL database in the world, used by everyone from small startups to huge companies like Adobe, eBay, Cisco, and EA.</p>

<p>A document looks like a JavaScript object:</p>

<pre><code>{
  _id: ObjectId("..."),
  name: "Aisha",
  email: "aisha@example.com",
  hobbies: ["chess", "hiking"]
}</code></pre>

<p>Key features that make MongoDB popular:</p>
<ul>
  <li><strong>Flexible schema</strong> &mdash; documents in the same collection can have different fields.</li>
  <li><strong>Rich query language</strong> &mdash; filter, project, sort, aggregate.</li>
  <li><strong>Horizontal scaling</strong> via built-in sharding.</li>
  <li><strong>High availability</strong> via replica sets.</li>
  <li><strong>Huge ecosystem</strong> &mdash; drivers for every language, MongoDB Atlas managed cloud, Compass GUI.</li>
</ul>

<p>MongoDB stores documents as BSON (binary JSON) on disk, which adds extra types like <code>ObjectId</code>, <code>Date</code>, and <code>Decimal128</code> beyond plain JSON.</p>
'''

ANSWERS[2] = r'''
<p>MongoDB and traditional relational databases like MySQL or PostgreSQL solve the same problem &mdash; storing and querying application data &mdash; but with very different models.</p>

<table><thead><tr><th>Aspect</th><th>Relational (SQL)</th><th>MongoDB</th></tr></thead><tbody>
<tr><td>Data unit</td><td>Row in a table</td><td>Document in a collection</td></tr>
<tr><td>Schema</td><td>Strict, defined upfront</td><td>Flexible per document</td></tr>
<tr><td>Query language</td><td>SQL</td><td>MongoDB Query Language (JS-like)</td></tr>
<tr><td>Joins</td><td>Native, fast</td><td>Embed or use <code>$lookup</code></td></tr>
<tr><td>Transactions</td><td>Strong ACID across rows</td><td>ACID, multi-document since 4.0</td></tr>
<tr><td>Scaling</td><td>Mostly vertical; sharding bolted on</td><td>Native horizontal sharding</td></tr>
<tr><td>Best for</td><td>Highly structured, relational data</td><td>Hierarchical, evolving, varied data</td></tr>
</tbody></table>

<p>The big practical difference is the embed-vs-join tradeoff. In SQL you usually normalize (one table per entity, joined at query time). In MongoDB you often <em>embed</em> related data inside the same document, so reading is one fast operation but writes touching that data may be more complex.</p>

<p>Choose MongoDB when your data is naturally hierarchical, schema evolves often, or you need easy horizontal scaling. Choose SQL when relationships are rich and integrity matters above all.</p>
'''

ANSWERS[3] = r'''
<p>A <strong>document</strong> is the basic unit of data in MongoDB &mdash; a single record, equivalent to a row in a relational table but far more flexible. Documents are stored as <strong>BSON</strong> (Binary JSON), which extends JSON with types like <code>ObjectId</code>, <code>Date</code>, <code>Binary</code>, and <code>Decimal128</code>.</p>

<pre><code>{
  _id: ObjectId("65f1a2b3c4d5e6f7a8b9c0d1"),
  username: "ibrahim",
  age: 28,
  email: "ibrahim@example.com",
  address: {
    city: "Hyderabad",
    pin: "500001"
  },
  tags: ["admin", "founder"],
  created_at: ISODate("2026-04-28T10:00:00Z")
}</code></pre>

<p>Important properties:</p>
<ul>
  <li>Every document has a unique <code>_id</code> field. If you don&rsquo;t provide one, MongoDB generates an <code>ObjectId</code> automatically.</li>
  <li>Field values can be primitives, arrays, or nested documents (objects).</li>
  <li>Maximum size is <strong>16MB</strong> per document &mdash; large blobs go into GridFS.</li>
  <li>Field names are strings; field order is preserved in BSON.</li>
</ul>

<p>Documents in the same collection can have different fields, but in practice you should keep similar shapes across a collection for sane querying and indexing.</p>
'''

ANSWERS[4] = r'''
<p>A <strong>collection</strong> is a group of MongoDB documents &mdash; conceptually similar to a table in a relational database, but without an enforced schema. Collections live inside a database, and each document inside a collection has its own <code>_id</code>.</p>

<pre><code>// Switch to (or create) a database
use shopdb

// "users" is a collection
db.users.insertOne({ name: "Sara", age: 30 })

// View collections in the current database
show collections</code></pre>

<p>Collections are created automatically the first time you insert into them &mdash; you don&rsquo;t have to <code>CREATE TABLE</code> first. You can also create them explicitly when you need options like capped collections or validators:</p>

<pre><code>db.createCollection("logs", { capped: true, size: 100000 })</code></pre>

<p>Although MongoDB doesn&rsquo;t enforce a schema by default, you can attach a <strong>JSON Schema validator</strong> to a collection to enforce structure on inserts and updates &mdash; a useful safety net once your data model is stable.</p>

<p>Naming convention: lowercase, plural names like <code>users</code>, <code>orders</code>, <code>products</code> are common. Avoid spaces and special characters.</p>
'''

ANSWERS[5] = r'''
<p>In MongoDB you don&rsquo;t explicitly &ldquo;create&rdquo; a database &mdash; you simply <code>use</code> the name you want, and the database springs into existence the first time you insert data into a collection inside it.</p>

<pre><code>// Switch to (or auto-create) the database
use bookstore

// At this point, "bookstore" doesn't actually exist yet
show dbs   // it won't appear

// Insert a document &mdash; now the DB and collection are created
db.books.insertOne({ title: "Sapiens", author: "Harari" })

show dbs   // bookstore now appears</code></pre>

<p>This lazy-creation behavior is intentional: it lets you experiment freely without polluting the server with empty databases. There are no &ldquo;CREATE DATABASE&rdquo;-style permissions to worry about either, beyond your overall connection privileges.</p>

<p>If you need to do this from an application, your driver does the same thing implicitly. For example, in Node.js with the official driver, <code>client.db("bookstore")</code> just returns a database handle &mdash; the actual database is created on first write.</p>

<p>To delete a database, switch to it and run <code>db.dropDatabase()</code>.</p>
'''

ANSWERS[6] = r'''
<p>You usually don&rsquo;t need to create collections explicitly &mdash; MongoDB creates one the first time you insert into it. But you <em>can</em> create one explicitly when you need extra options.</p>

<pre><code>// Implicit creation &mdash; happens automatically
db.products.insertOne({ name: "Laptop", price: 1200 })

// Explicit creation
db.createCollection("products")

// With options &mdash; capped collection (fixed size, FIFO eviction)
db.createCollection("logs", {
  capped: true,
  size: 1048576,   // bytes
  max: 10000       // max number of documents
})

// With a JSON Schema validator
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name"],
      properties: {
        email: { bsonType: "string", pattern: "^.+@.+$" },
        name:  { bsonType: "string" }
      }
    }
  }
})</code></pre>

<p>Use <code>createCollection</code> explicitly when you need:</p>
<ul>
  <li><strong>Capped collections</strong> &mdash; high-throughput logs that auto-evict.</li>
  <li><strong>Validators</strong> &mdash; enforce a schema on writes.</li>
  <li><strong>Time-series collections</strong> (MongoDB 5.0+) for IoT/metrics workloads.</li>
  <li>Custom collation or storage engine options.</li>
</ul>
'''

ANSWERS[7] = r'''
<p>You insert documents using <code>insertOne()</code> for a single document or <code>insertMany()</code> for a batch.</p>

<pre><code>// Single document
db.users.insertOne({
  name: "Priya",
  email: "priya@example.com",
  age: 27
})
// Returns { acknowledged: true, insertedId: ObjectId("...") }

// Multiple documents
db.users.insertMany([
  { name: "Arjun", age: 31 },
  { name: "Maya",  age: 24 }
])
// Returns { acknowledged: true, insertedIds: { "0": ObjectId(...), "1": ObjectId(...) } }</code></pre>

<p>If you don&rsquo;t supply an <code>_id</code>, MongoDB generates one for you (an <code>ObjectId</code>). If you provide one yourself, it must be unique within the collection.</p>

<p>Two useful options for <code>insertMany</code>:</p>
<ul>
  <li><code>{ ordered: true }</code> (default) &mdash; stops on the first error.</li>
  <li><code>{ ordered: false }</code> &mdash; tries every document and reports errors at the end. Faster for bulk loads.</li>
</ul>

<p>Drivers (Node.js, Python, Java, etc.) expose the same methods via idiomatic APIs, e.g. <code>await users.insertOne({...})</code>. The legacy <code>insert()</code> method still works but is deprecated &mdash; prefer <code>insertOne</code>/<code>insertMany</code>.</p>
'''

ANSWERS[8] = r'''
<p>You update documents using <code>updateOne()</code>, <code>updateMany()</code>, or <code>replaceOne()</code>. The first argument is a filter (which documents to match), and the second is what to change.</p>

<pre><code>// Update one matching document
db.users.updateOne(
  { email: "priya@example.com" },          // filter
  { $set: { age: 28, city: "Pune" } }      // update
)

// Update all matching documents
db.users.updateMany(
  { active: false },
  { $set: { archived: true } }
)

// Replace the entire document (keeps _id)
db.users.replaceOne(
  { _id: ObjectId("...") },
  { name: "New User", email: "new@example.com" }
)

// Upsert &mdash; insert if not found
db.users.updateOne(
  { email: "x@y.com" },
  { $set: { name: "X" } },
  { upsert: true }
)</code></pre>

<p>The most common <strong>update operators</strong>:</p>
<ul>
  <li><code>$set</code> &mdash; set a field&rsquo;s value.</li>
  <li><code>$unset</code> &mdash; remove a field.</li>
  <li><code>$inc</code> &mdash; increment a number.</li>
  <li><code>$push</code> / <code>$pull</code> &mdash; add to / remove from an array.</li>
  <li><code>$rename</code> &mdash; rename a field.</li>
</ul>

<p>The result includes <code>matchedCount</code> and <code>modifiedCount</code> so you can confirm how many documents the operation affected.</p>
'''

ANSWERS[9] = r'''
<p>You remove documents using <code>deleteOne()</code> for a single match or <code>deleteMany()</code> for all matches. Both take a filter.</p>

<pre><code>// Delete the first match
db.users.deleteOne({ email: "stale@example.com" })

// Delete all matches
db.users.deleteMany({ active: false })

// Delete every document in a collection (but keep the collection)
db.users.deleteMany({})

// Drop the entire collection (faster than deleteMany({}))
db.users.drop()</code></pre>

<p>The result includes <code>deletedCount</code>:</p>

<pre><code>{ acknowledged: true, deletedCount: 7 }</code></pre>

<p>Important things to remember:</p>
<ul>
  <li>Deleting many documents is <strong>not atomic across documents</strong> &mdash; concurrent reads may see partial state.</li>
  <li><code>deleteMany({})</code> still scans every document; for wiping a whole collection, <code>drop()</code> is much faster because it removes the storage files directly.</li>
  <li>For audit-friendly designs, prefer <em>soft deletes</em> (set <code>deleted_at</code>) over hard deletes.</li>
  <li>The legacy <code>remove()</code> is deprecated &mdash; always use the explicit <code>deleteOne</code>/<code>deleteMany</code>.</li>
</ul>

<p>If you need both delete and return the deleted document, use <code>findOneAndDelete()</code>.</p>
'''

ANSWERS[10] = r'''
<p>You retrieve documents with the <code>find()</code> method. With no filter, it returns every document in the collection.</p>

<pre><code>// All documents
db.users.find()

// Pretty-print in the shell
db.users.find().pretty()

// Just the first
db.users.findOne()

// As an array (in application code)
const all = await db.collection("users").find().toArray();</code></pre>

<p>In the shell, <code>find()</code> returns a <strong>cursor</strong> &mdash; an iterator over the result set. The shell auto-displays the first 20 documents and lets you type <code>it</code> to fetch the next batch.</p>

<p>Useful chained methods on the cursor:</p>
<ul>
  <li><code>.limit(n)</code> &mdash; cap the number of results.</li>
  <li><code>.skip(n)</code> &mdash; skip the first <em>n</em> results (avoid large skips for performance).</li>
  <li><code>.sort({ field: 1 })</code> &mdash; sort ascending; <code>-1</code> for descending.</li>
  <li><code>.project({ name: 1, _id: 0 })</code> &mdash; choose fields to include or exclude.</li>
  <li><code>.count()</code> / <code>.toArray()</code> / <code>.forEach()</code>.</li>
</ul>

<p>For large collections, never iterate everything in one go &mdash; use pagination via sort + range filter, or use the aggregation pipeline.</p>
'''

ANSWERS[11] = r'''
<p>The <code>_id</code> field is the unique <strong>primary key</strong> for every document. If you don&rsquo;t provide one on insert, MongoDB generates an <code>ObjectId</code> &mdash; a 12-byte value that&rsquo;s unique across the cluster and roughly time-ordered.</p>

<pre><code>ObjectId("65f1a2b3c4d5e6f7a8b9c0d1")
//        |---|---|---|--------------|
//          ts   machine pid     counter</code></pre>

<p>An <code>ObjectId</code> consists of:</p>
<ul>
  <li><strong>4 bytes</strong> &mdash; Unix timestamp (seconds since epoch).</li>
  <li><strong>5 bytes</strong> &mdash; random per-process value.</li>
  <li><strong>3 bytes</strong> &mdash; incrementing counter.</li>
</ul>

<p>Useful properties:</p>
<ul>
  <li><strong>Globally unique</strong> without coordination &mdash; safe for distributed inserts.</li>
  <li><strong>Roughly sortable by time</strong> &mdash; you can sort by <code>_id</code> to get newest-first.</li>
  <li>Extract the embedded timestamp via <code>id.getTimestamp()</code>.</li>
</ul>

<p>You can also use your own values for <code>_id</code> &mdash; an integer, a UUID, an email, anything &mdash; as long as each value is unique. For modern apps, <strong>UUIDv7</strong> is becoming popular as an alternative because it&rsquo;s standardized, time-ordered, and 16 bytes.</p>

<p>Indexed automatically &mdash; you never need to create an index on <code>_id</code>.</p>
'''

ANSWERS[12] = r'''
<p>Indexes speed up queries by avoiding full collection scans. You create one with <code>createIndex()</code>, supplying the fields and a sort direction (1 ascending, -1 descending).</p>

<pre><code>// Single-field index
db.users.createIndex({ email: 1 })

// Compound index &mdash; supports queries on email, or email+age
db.users.createIndex({ email: 1, age: -1 })

// Unique index &mdash; rejects duplicates
db.users.createIndex({ email: 1 }, { unique: true })

// Partial index &mdash; only index docs that match a filter
db.users.createIndex(
  { lastLogin: 1 },
  { partialFilterExpression: { active: true } }
)

// TTL index &mdash; auto-delete documents after N seconds
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })

// Text index &mdash; for full-text search
db.articles.createIndex({ title: "text", body: "text" })</code></pre>

<p>Best practices:</p>
<ul>
  <li>Index every field you regularly filter or sort on.</li>
  <li>For compound indexes, follow the <strong>ESR rule</strong> &mdash; Equality fields first, then Sort, then Range.</li>
  <li>Don&rsquo;t over-index &mdash; each index slows writes and uses RAM.</li>
  <li>Inspect with <code>db.users.getIndexes()</code> and <code>explain()</code> to verify indexes are actually used.</li>
</ul>

<p>The <code>_id</code> index exists automatically &mdash; you never need to create it.</p>
'''

ANSWERS[13] = r'''
<p>You drop indexes with <code>dropIndex()</code> by name or by spec, or all non-<code>_id</code> indexes at once with <code>dropIndexes()</code>.</p>

<pre><code>// List indexes
db.users.getIndexes()
// [
//   { v: 2, key: { _id: 1 }, name: "_id_" },
//   { v: 2, key: { email: 1 }, name: "email_1" },
//   { v: 2, key: { city: 1, age: -1 }, name: "city_1_age_-1" }
// ]

// Drop by name
db.users.dropIndex("email_1")

// Drop by spec (must match exactly)
db.users.dropIndex({ city: 1, age: -1 })

// Drop everything except _id
db.users.dropIndexes()</code></pre>

<p>The <code>_id</code> index cannot be dropped &mdash; MongoDB always maintains it.</p>

<p>Things to watch out for:</p>
<ul>
  <li>Dropping an index in production briefly takes a write lock &mdash; safe but worth scheduling.</li>
  <li>Use <code>db.users.aggregate([{ $indexStats: {} }])</code> first to check if an index is actually being used before dropping. If <code>accesses.ops</code> is zero over a long period, it&rsquo;s a good candidate.</li>
  <li>Background <code>hidden</code> indexes (set <code>hidden: true</code>) let you simulate dropping without losing the index, then restore quickly if performance regresses.</li>
</ul>

<p>Removing unused indexes is one of the easiest performance wins on a busy MongoDB cluster.</p>
'''

ANSWERS[14] = r'''
<p>The <code>find()</code> method retrieves documents from a collection. Its first argument is a <em>query filter</em>; its second is an optional <em>projection</em> that controls which fields come back.</p>

<pre><code>db.collection.find(filter, projection)</code></pre>

<p>Examples:</p>

<pre><code>// All documents
db.users.find()

// All active users
db.users.find({ active: true })

// Active users in Mumbai, only show name and email
db.users.find(
  { active: true, city: "Mumbai" },
  { name: 1, email: 1, _id: 0 }
)

// Cursor methods
db.users.find({ active: true })
        .sort({ createdAt: -1 })
        .limit(20)
        .skip(40)</code></pre>

<p>Key points to remember:</p>
<ul>
  <li><code>find()</code> returns a <strong>cursor</strong> &mdash; iterate it with <code>toArray()</code>, <code>forEach()</code>, or via the shell&rsquo;s automatic batching.</li>
  <li>An empty filter <code>{}</code> matches every document.</li>
  <li>In the projection, <code>1</code> includes a field and <code>0</code> excludes it &mdash; you can&rsquo;t mix the two except to suppress <code>_id</code>.</li>
  <li>Always pair filtered queries with appropriate indexes; verify with <code>.explain("executionStats")</code>.</li>
</ul>

<p>Use <code>findOne()</code> when you only need one document &mdash; it returns the document directly, not a cursor.</p>
'''

ANSWERS[15] = r'''
<p>You build query filters using field names mapped to values or to query operators. MongoDB expressions are JSON-shaped.</p>

<pre><code>// Equality
db.users.find({ city: "Hyderabad" })

// Multiple conditions are AND-ed
db.users.find({ city: "Hyderabad", age: 25 })

// Comparison operators
db.users.find({ age: { $gt: 18, $lt: 65 } })   // 18 &lt; age &lt; 65
db.users.find({ score: { $gte: 90 } })          // &gt;=
db.users.find({ status: { $ne: "banned" } })    // not equal

// Set membership
db.users.find({ role: { $in: ["admin", "editor"] } })

// Array element match
db.products.find({ tags: "sale" })   // tags array contains "sale"

// Nested fields
db.users.find({ "address.city": "Pune" })

// Existence
db.users.find({ phone: { $exists: true } })

// Regex
db.users.find({ email: { $regex: /@gmail\.com$/i } })</code></pre>

<p>The most common operators by category:</p>
<ul>
  <li><strong>Comparison:</strong> <code>$eq, $ne, $gt, $gte, $lt, $lte, $in, $nin</code>.</li>
  <li><strong>Logical:</strong> <code>$and, $or, $not, $nor</code>.</li>
  <li><strong>Element:</strong> <code>$exists, $type</code>.</li>
  <li><strong>Array:</strong> <code>$all, $elemMatch, $size</code>.</li>
</ul>

<p>For best performance, ensure the fields you filter on are indexed.</p>
'''

ANSWERS[16] = r'''
<p>You count documents with <code>countDocuments()</code> or, when you want a fast approximation of the whole collection, <code>estimatedDocumentCount()</code>.</p>

<pre><code>// Exact count, respects filter
db.users.countDocuments({ active: true })

// Whole-collection count, fast (uses metadata)
db.users.estimatedDocumentCount()

// Legacy &mdash; deprecated
db.users.count({ active: true })   // avoid in new code</code></pre>

<p>The two methods differ in important ways:</p>

<table><thead><tr><th>Method</th><th>Speed</th><th>Accuracy</th><th>Filter?</th></tr></thead><tbody>
<tr><td><code>countDocuments(filter)</code></td><td>Slower &mdash; scans/uses index</td><td>Always exact</td><td>Yes</td></tr>
<tr><td><code>estimatedDocumentCount()</code></td><td>Instant</td><td>From cached metadata; can be off after crashes</td><td>No</td></tr>
</tbody></table>

<p>Tips:</p>
<ul>
  <li>For a dashboard tile showing total docs, use <code>estimatedDocumentCount()</code>.</li>
  <li>For a paginated UI showing &ldquo;X results,&rdquo; use <code>countDocuments(filter)</code>.</li>
  <li>For really large collections, even <code>countDocuments</code> can be expensive &mdash; consider counting via a maintained aggregate document, or use approximate cardinality (HyperLogLog) outside MongoDB.</li>
</ul>

<p>Always use the modern methods &mdash; the old <code>count()</code> behaves differently across drivers and is deprecated.</p>
'''

ANSWERS[17] = r'''
<p>The <code>updateOne()</code> method updates the <em>first</em> document that matches a filter. If no document matches, nothing changes (unless you also pass <code>{ upsert: true }</code>).</p>

<pre><code>db.users.updateOne(
  { email: "ana@example.com" },                  // filter
  { $set: { lastLogin: new Date(), age: 30 } }   // update
)
// { acknowledged: true, matchedCount: 1, modifiedCount: 1 }</code></pre>

<p>The update document uses <strong>update operators</strong> (with leading <code>$</code>); a plain object would be treated as a full replacement.</p>

<pre><code>// Common operators
{ $set:    { name: "Alex" } }       // set or add field
{ $unset:  { temp: "" } }            // remove field
{ $inc:    { views: 1 } }            // increment number
{ $push:   { tags: "new" } }         // append to array
{ $pull:   { tags: "old" } }         // remove from array
{ $rename: { fname: "firstName" } }  // rename field</code></pre>

<p>Useful options:</p>
<ul>
  <li><code>{ upsert: true }</code> &mdash; insert if no match; useful for idempotent writes.</li>
  <li><code>{ arrayFilters: [...] }</code> &mdash; pinpoint specific array elements when used with <code>$[<i></i>]</code>.</li>
</ul>

<p>For atomic read-then-update workflows, use <code>findOneAndUpdate()</code> &mdash; it returns either the original or the modified document, useful for counters and queues.</p>

<p>Use <code>updateMany</code> when you need to update every match instead of just the first.</p>
'''

ANSWERS[18] = r'''
<p>To update multiple documents at once, use <code>updateMany()</code>. It applies the same update to every document that matches the filter.</p>

<pre><code>// Mark all inactive users as archived
db.users.updateMany(
  { active: false },
  { $set: { archived: true, archivedAt: new Date() } }
)
// { acknowledged: true, matchedCount: 12, modifiedCount: 12 }

// Increment a counter on every product in a category
db.products.updateMany(
  { category: "books" },
  { $inc: { views: 1 } }
)

// Add a tag to every document missing it
db.products.updateMany(
  { tags: { $nin: ["v2"] } },
  { $push: { tags: "v2" } }
)</code></pre>

<p>Things to know:</p>
<ul>
  <li>Each individual document update is atomic, but the operation as a whole is <em>not</em> atomic across documents &mdash; concurrent readers may see a mix of updated and not-yet-updated docs.</li>
  <li>If you need cross-document atomicity, wrap the call in a multi-document <strong>transaction</strong> (MongoDB 4.0+ for replica sets, 4.2+ for sharded clusters).</li>
  <li>For very large updates, consider chunking by <code>_id</code> ranges to avoid long-running operations.</li>
</ul>

<p>Use <code>{ upsert: true }</code> with caution on <code>updateMany</code> &mdash; it inserts <em>at most one</em> document if no matches, not one per filter combination.</p>
'''

ANSWERS[19] = r'''
<p>You delete a single document with <code>deleteOne()</code>, which removes the first match for a filter.</p>

<pre><code>// Delete one matching document
db.users.deleteOne({ email: "spam@example.com" })
// { acknowledged: true, deletedCount: 1 }

// Delete by _id (most precise)
db.users.deleteOne({ _id: ObjectId("65f1a2b3c4d5e6f7a8b9c0d1") })

// Atomic find-and-delete &mdash; returns the deleted doc
const removed = db.users.findOneAndDelete({ email: "x@y.com" })</code></pre>

<p>If no document matches, <code>deletedCount</code> is 0 and nothing happens &mdash; this is intentional and idempotent.</p>

<p>When to use which:</p>
<ul>
  <li><code>deleteOne</code> &mdash; you don&rsquo;t need the deleted document back.</li>
  <li><code>findOneAndDelete</code> &mdash; you want to log or process the removed document atomically.</li>
</ul>

<p>Production tips:</p>
<ul>
  <li>Always filter by <code>_id</code> when you can &mdash; it&rsquo;s indexed and unambiguous.</li>
  <li>For audit-heavy systems, prefer <em>soft delete</em> (<code>{ $set: { deleted_at: new Date() } }</code>) so data can be restored or analyzed.</li>
  <li>Pair deletes with backups; <code>deleteOne</code> is irreversible without one.</li>
</ul>

<p>The legacy <code>remove({}, { justOne: true })</code> still works but is deprecated &mdash; always use the explicit method.</p>
'''

ANSWERS[20] = r'''
<p>To delete multiple documents at once, use <code>deleteMany()</code>. It removes every document that matches the filter.</p>

<pre><code>// Delete all soft-archived rows
db.users.deleteMany({ archived: true })
// { acknowledged: true, deletedCount: 247 }

// Delete documents older than a threshold
db.logs.deleteMany({
  createdAt: { $lt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
})

// Delete everything &mdash; rarely what you want
db.events.deleteMany({})</code></pre>

<p>Important behaviors:</p>
<ul>
  <li>The operation is <strong>not atomic across documents</strong> &mdash; readers can observe partial state during a long delete.</li>
  <li>For huge deletes, MongoDB doesn&rsquo;t reclaim disk space immediately; the storage layer reuses freed space for new writes. To reclaim space, run <code>compact</code> or restore from a fresh dump.</li>
  <li>If you want to wipe a whole collection, <code>db.collection.drop()</code> is much faster than <code>deleteMany({})</code> because it removes the storage files directly. The collection re-creates on next insert.</li>
  <li>Use a <strong>TTL index</strong> for time-based auto-deletion (sessions, logs) so you don&rsquo;t need a cron at all:</li>
</ul>

<pre><code>db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })</code></pre>

<p>For very large purges, batch by <code>_id</code> range to keep operations short and avoid long-running write locks.</p>
'''

ANSWERS[21] = r'''
<p>A <strong>unique index</strong> ensures no two documents share the same value for the indexed field(s). It&rsquo;s how MongoDB enforces uniqueness on fields like email or username.</p>

<pre><code>// Single-field unique index
db.users.createIndex({ email: 1 }, { unique: true })

// Compound unique index &mdash; combination must be unique
db.orders.createIndex(
  { customerId: 1, orderNumber: 1 },
  { unique: true }
)

// Allow nulls but reject duplicates among present values
db.users.createIndex(
  { phone: 1 },
  { unique: true, partialFilterExpression: { phone: { $exists: true } } }
)</code></pre>

<p>If a duplicate insert is attempted, MongoDB throws a <code>DuplicateKey</code> error (code 11000) and rejects the operation:</p>

<pre><code>{ ok: 0, code: 11000, errmsg: "E11000 duplicate key error..." }</code></pre>

<p>Important behaviors:</p>
<ul>
  <li><strong>Build before data exists</strong> when possible &mdash; building on a collection with existing duplicates fails.</li>
  <li>By default, missing fields are treated as <code>null</code>. Two documents with no <code>email</code> field would conflict on a unique-email index. Use a <strong>partial index</strong> (above) to skip those.</li>
  <li>Unique indexes are also valid for queries &mdash; you don&rsquo;t need a separate non-unique index.</li>
  <li>The <code>_id</code> index is implicitly unique.</li>
</ul>

<p>For idempotent writes, combine unique indexes with <code>upsert: true</code> on update.</p>
'''

ANSWERS[22] = r'''
<p>The <code>aggregate()</code> method runs documents through a multi-stage <strong>pipeline</strong>. Each stage transforms the input and passes its output to the next stage, like a Unix pipe.</p>

<pre><code>db.orders.aggregate([
  { $match:   { status: "paid" } },                    // filter
  { $group:   { _id: "$customerId", total: { $sum: "$amount" } } },  // group
  { $sort:    { total: -1 } },                          // sort
  { $limit:   10 },                                     // top 10
  { $project: { customerId: "$_id", total: 1, _id: 0 } } // shape output
])</code></pre>

<p>Aggregation is far more powerful than <code>find()</code> &mdash; it can compute averages, group by, join collections (<code>$lookup</code>), unwind arrays, run window functions, and more. The most common stages:</p>

<table><thead><tr><th>Stage</th><th>Does</th></tr></thead><tbody>
<tr><td><code>$match</code></td><td>Filter docs (like <code>find</code>)</td></tr>
<tr><td><code>$group</code></td><td>Group and aggregate</td></tr>
<tr><td><code>$project</code></td><td>Reshape fields</td></tr>
<tr><td><code>$sort</code> / <code>$limit</code> / <code>$skip</code></td><td>Order and paginate</td></tr>
<tr><td><code>$lookup</code></td><td>Left-outer join with another collection</td></tr>
<tr><td><code>$unwind</code></td><td>Explode an array field into multiple docs</td></tr>
<tr><td><code>$out</code> / <code>$merge</code></td><td>Write results back to a collection</td></tr>
</tbody></table>

<p>Aggregation pipelines run on the server, use indexes when possible, and can stream large datasets. They&rsquo;re the standard way to do reporting and analytics inside MongoDB.</p>
'''

ANSWERS[23] = r'''
<p>The <code>$match</code> stage filters documents in an aggregation pipeline &mdash; it&rsquo;s functionally identical to the filter in <code>find()</code>, written using the same query operators.</p>

<pre><code>db.orders.aggregate([
  { $match: {
      status: "paid",
      total:  { $gte: 100 },
      createdAt: { $gte: ISODate("2026-01-01") }
  }}
])</code></pre>

<p>Best practice: <strong>put <code>$match</code> as early as possible</strong>. The optimizer can then use indexes and reduce the number of documents flowing through later stages.</p>

<pre><code>// Good &mdash; filter first, then heavy work
[
  { $match: { country: "IN" } },
  { $group: { _id: "$city", count: { $sum: 1 } } }
]

// Bad &mdash; group everything, then filter
[
  { $group: { _id: "$city", count: { $sum: 1 } } },
  { $match: { count: { $gte: 100 } } }   // OK, but post-group filter still needed
]</code></pre>

<p>Notes:</p>
<ul>
  <li>An early <code>$match</code> on indexed fields can entirely skip a collection scan.</li>
  <li>Use <code>$expr</code> inside <code>$match</code> if you need to compare two fields of the same document.</li>
  <li>If you also need to filter <em>after</em> a group/lookup, that&rsquo;s a separate <code>$match</code> stage &mdash; it&rsquo;s perfectly valid.</li>
</ul>

<p>Always run <code>.explain()</code> on the pipeline to verify <code>$match</code> uses an index.</p>
'''

ANSWERS[24] = r'''
<p>The <code>$group</code> stage groups documents by a key and computes aggregate values for each group &mdash; the heart of analytical queries.</p>

<pre><code>// Total revenue per customer
db.orders.aggregate([
  { $group: {
      _id: "$customerId",                  // group key
      revenue: { $sum: "$amount" },        // sum
      orders:  { $sum: 1 },                // count
      avg:     { $avg: "$amount" },        // average
      first:   { $min: "$createdAt" },     // earliest
      last:    { $max: "$createdAt" },     // latest
      items:   { $push: "$itemName" }      // collect into array
  }}
])</code></pre>

<p>The <code>_id</code> field defines the grouping key. It can be:</p>
<ul>
  <li>A single field reference: <code>"$customerId"</code>.</li>
  <li>A document for multi-field groups: <code>{ city: "$city", year: { $year: "$createdAt" } }</code>.</li>
  <li><code>null</code> &mdash; groups everything into one bucket (good for overall totals).</li>
</ul>

<p>Common accumulators:</p>

<table><thead><tr><th>Operator</th><th>Meaning</th></tr></thead><tbody>
<tr><td><code>$sum</code></td><td>Total (use <code>$sum: 1</code> for count)</td></tr>
<tr><td><code>$avg</code></td><td>Average</td></tr>
<tr><td><code>$min</code> / <code>$max</code></td><td>Extremes</td></tr>
<tr><td><code>$first</code> / <code>$last</code></td><td>First/last in input order &mdash; useful with <code>$sort</code> beforehand</td></tr>
<tr><td><code>$push</code> / <code>$addToSet</code></td><td>Collect into an array (with or without duplicates)</td></tr>
</tbody></table>

<p>Pair <code>$group</code> with an upstream <code>$match</code> to keep group sizes small and tap into indexes.</p>
'''

ANSWERS[25] = r'''
<p>The <code>$project</code> stage <strong>reshapes documents</strong> &mdash; it includes, excludes, renames, or computes new fields, similar to a <code>SELECT</code> in SQL.</p>

<pre><code>// Choose specific fields
db.users.aggregate([
  { $project: { _id: 0, name: 1, email: 1 } }
])

// Compute new fields
db.orders.aggregate([
  { $project: {
      orderId:    "$_id",
      customer:   "$customerName",
      total:      { $multiply: ["$qty", "$price"] },
      year:       { $year: "$createdAt" },
      isExpensive:{ $gt: ["$total", 1000] }
  }}
])

// Hide a sensitive field
db.users.aggregate([
  { $project: { passwordHash: 0 } }
])</code></pre>

<p>Rules to remember:</p>
<ul>
  <li>Use <code>1</code> to include a field, <code>0</code> to exclude it. You can&rsquo;t mix them, except to suppress <code>_id</code>.</li>
  <li>To rename a field, set the new name to the old field reference: <code>{ author: "$writerName" }</code>.</li>
  <li>To compute, use any aggregation expression on the right-hand side.</li>
</ul>

<p>If you only need to <em>add</em> fields without listing all the others, use <code>$addFields</code> (or its alias <code>$set</code>) &mdash; it keeps existing fields automatically:</p>

<pre><code>{ $addFields: { fullName: { $concat: ["$first", " ", "$last"] } } }</code></pre>

<p>Place <code>$project</code> late in the pipeline so earlier stages can still use the dropped fields if needed.</p>
'''

ANSWERS[26] = r'''
<p>A <strong>replica set</strong> is a group of <strong>mongod</strong> servers that maintain the same data, providing <strong>high availability</strong> and automatic failover. One member is the <strong>primary</strong> (handles all writes); the others are <strong>secondaries</strong> that replicate the primary&rsquo;s oplog and can serve reads.</p>

<pre><code>// Typical 3-node setup
//
//   Primary  --writes--&gt;  Secondary 1
//                         Secondary 2
//
// If primary fails, the remaining members elect a new primary
// (Raft-like protocol). Apps reconnect transparently via the driver.</code></pre>

<p>Why use one:</p>
<ul>
  <li><strong>Automatic failover</strong> &mdash; if the primary crashes, a secondary is elected within seconds.</li>
  <li><strong>Data redundancy</strong> &mdash; multiple copies guard against hardware failure.</li>
  <li><strong>Read scaling</strong> &mdash; secondary reads via <code>readPreference: "secondaryPreferred"</code>.</li>
  <li><strong>Zero-downtime maintenance</strong> &mdash; rolling upgrades, index builds.</li>
</ul>

<p>Production-grade clusters always run a replica set (3 or 5 members, odd numbers for elections). MongoDB Atlas creates one for you automatically. A standalone mongod is fine for local dev only.</p>
'''

ANSWERS[27] = r'''
<p>You create a replica set by starting each <code>mongod</code> with a shared <code>replSetName</code> and then running <code>rs.initiate()</code> from the shell on one member. The other members join via configuration.</p>

<pre><code>// Start 3 mongod processes on different ports
mongod --replSet rs0 --port 27017 --dbpath /data/r0 --bind_ip localhost
mongod --replSet rs0 --port 27018 --dbpath /data/r1 --bind_ip localhost
mongod --replSet rs0 --port 27019 --dbpath /data/r2 --bind_ip localhost

// Connect to one and initiate
mongosh --port 27017
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" },
    { _id: 1, host: "localhost:27018" },
    { _id: 2, host: "localhost:27019" }
  ]
});

rs.status();   // verify members PRIMARY/SECONDARY</code></pre>

<p>For production, use <strong>MongoDB Atlas</strong> &mdash; it provisions multi-AZ replica sets, handles failover, and includes monitoring. Self-hosted setups should use TLS, keyfile or x.509 authentication, and place members in different availability zones for true HA. Always use 3 or 5 members so elections always have a majority.</p>
'''

ANSWERS[28] = r'''
<p><strong>Sharding</strong> is MongoDB&rsquo;s strategy for <strong>horizontal scaling</strong> &mdash; splitting a large collection across multiple servers (called <em>shards</em>) so each one stores only a portion of the data. It&rsquo;s how you scale beyond what a single machine can hold.</p>

<pre><code>// Conceptually:
//
//   Shard A  --&gt;  documents where customer_id % 3 == 0
//   Shard B  --&gt;  documents where customer_id % 3 == 1
//   Shard C  --&gt;  documents where customer_id % 3 == 2
//
// Apps connect via mongos (router); it knows which shard
// holds which data based on the &ldquo;shard key&rdquo;.</code></pre>

<p>Key concepts:</p>
<ul>
  <li><strong>Shard key</strong> &mdash; the field(s) that determine which shard a document lives on. Choose carefully (high cardinality, even distribution, matches access pattern).</li>
  <li><strong>mongos</strong> &mdash; the query router; clients connect to it, not the shards directly.</li>
  <li><strong>Config servers</strong> &mdash; store cluster metadata (which range of shard keys lives on which shard).</li>
  <li><strong>Chunks &amp; balancer</strong> &mdash; data is split into chunks; the balancer auto-migrates them to keep shards even.</li>
</ul>

<p>Sharding is powerful but operationally complex. Use replica sets first; only shard once a single replica set can&rsquo;t hold your data or handle the write rate.</p>
'''

ANSWERS[29] = r'''
<p>Setting up sharding involves three components: <strong>config servers</strong> (a replica set storing metadata), <strong>shards</strong> (each one a replica set holding data), and <strong>mongos</strong> routers (clients connect here).</p>

<pre><code>// 1. Start a config server replica set
mongod --configsvr --replSet cfg --port 27019 --dbpath /data/cfg
// then rs.initiate() with name "cfg"

// 2. Start each shard as its own replica set
mongod --shardsvr --replSet shardA --port 27018 ...
// rs.initiate() inside each

// 3. Start mongos router pointing at the config servers
mongos --configdb cfg/host1:27019,host2:27019,host3:27019 --port 27017

// 4. From mongos: add shards and shard a collection
sh.addShard("shardA/host:27018");
sh.addShard("shardB/host:27018");

sh.enableSharding("shopdb");
db.products.createIndex({ category: 1, _id: 1 });
sh.shardCollection("shopdb.products", { category: 1, _id: 1 });</code></pre>

<p>Pick a shard key that <strong>distributes evenly</strong> (avoid monotonically increasing keys like timestamps unless hashed) and <strong>matches your queries</strong> (so they target one shard). Most teams use <strong>MongoDB Atlas</strong> instead of running this themselves &mdash; Atlas handles all of the above and lets you reshard collections online with a click.</p>
'''

ANSWERS[30] = r'''
<p><strong><code>mongod</code></strong> is the <strong>core MongoDB server process</strong> &mdash; it&rsquo;s the daemon that actually stores data, handles queries, manages indexes, and replicates with other members. Every replica set node, every shard server, runs a <code>mongod</code> process.</p>

<pre><code>// Start a basic standalone server
mongod --dbpath /data/db --port 27017

// Common production flags
mongod \
  --dbpath /data/db \
  --port 27017 \
  --bind_ip 0.0.0.0 \
  --replSet rs0 \
  --auth \
  --tlsMode requireTLS \
  --tlsCertificateKeyFile /etc/ssl/mongo.pem \
  --logpath /var/log/mongod.log \
  --fork

// Or via config file (preferred for production)
mongod --config /etc/mongod.conf</code></pre>

<p>Default port is <code>27017</code>. The data directory must exist before starting (and shouldn&rsquo;t be shared between processes). Production deployments use a config file with <code>storage.wiredTiger.engineConfig.cacheSizeGB</code>, <code>net.tls</code>, <code>security.authorization</code>, and replication settings.</p>

<p>For local development, just run <code>mongod --dbpath /tmp/db</code>. For anything serious, use systemd, MongoDB Atlas, or a Docker image &mdash; never run untuned <code>mongod</code> on a production box.</p>
'''

ANSWERS[31] = r'''
<p>The <strong><code>mongo shell</code></strong> &mdash; properly called <strong><code>mongosh</code></strong> in modern versions &mdash; is the interactive command-line client for MongoDB. It connects to a server and lets you run JavaScript-style commands against databases and collections.</p>

<pre><code>// Connect to local server (default port 27017)
mongosh

// Connect to a specific URI
mongosh "mongodb+srv://user:pass@cluster0.mongodb.net/myapp"

// Run shell commands
use shopdb              // switch database
show collections        // list collections in the current DB
db.products.find()      // run a query
db.products.countDocuments()
db.products.insertOne({ name: "Pen", price: 10 })

// Run a script
mongosh script.js</code></pre>

<p>The shell is full JavaScript &mdash; you can write loops, define functions, store variables (<code>let users = db.users.find().toArray()</code>), and import packages. <code>mongosh</code> replaced the legacy <code>mongo</code> shell starting MongoDB 5.0 and adds modern JavaScript support, syntax highlighting, and better autocomplete.</p>

<p>For GUIs, use <strong>MongoDB Compass</strong> (official) or <strong>Studio 3T</strong> &mdash; both let you query, edit, and visualize data without typing commands.</p>
'''

ANSWERS[32] = r'''
<p>You create a user with <code>db.createUser()</code>, specifying a username, password, and the roles (permissions) the user should have. Users are tied to a specific database &mdash; the one you&rsquo;re connected to when you create them.</p>

<pre><code>// Create an admin user (one-time on a fresh server)
use admin
db.createUser({
  user: "rootAdmin",
  pwd: passwordPrompt(),    // prompts securely
  roles: [{ role: "root", db: "admin" }]
});

// Create an app user with read-write access to one database
use shopdb
db.createUser({
  user: "shopApp",
  pwd: passwordPrompt(),
  roles: [{ role: "readWrite", db: "shopdb" }]
});

// Read-only analytics user across multiple databases
db.createUser({
  user: "analyst",
  pwd: passwordPrompt(),
  roles: [
    { role: "read", db: "shopdb" },
    { role: "read", db: "ordersdb" }
  ]
});</code></pre>

<p>Use <code>passwordPrompt()</code> in <code>mongosh</code> instead of a literal password &mdash; it avoids leaking the password to your shell history. Always start <code>mongod</code> with <code>--auth</code> in production. For automated rotation use <strong>HashiCorp Vault</strong>, <strong>AWS Secrets Manager</strong>, or Atlas Database Users with API-managed credentials.</p>
'''

ANSWERS[33] = r'''
<p>You grant additional roles to an existing user with <code>db.grantRolesToUser()</code>, and revoke them with <code>db.revokeRolesFromUser()</code>. Roles can be built-in (like <code>read</code>, <code>readWrite</code>, <code>dbAdmin</code>) or custom.</p>

<pre><code>// Grant additional read on the analytics DB to an existing user
use admin
db.grantRolesToUser("shopApp", [
  { role: "read", db: "analyticsdb" }
]);

// Revoke a role
db.revokeRolesFromUser("shopApp", [
  { role: "read", db: "analyticsdb" }
]);

// View the user&rsquo;s current roles
db.getUser("shopApp");

// Create a custom role with specific privileges
db.createRole({
  role: "ordersWriter",
  privileges: [{
    resource: { db: "shopdb", collection: "orders" },
    actions: [ "insert", "update", "find" ]
  }],
  roles: []
});</code></pre>

<table><thead><tr><th>Built-in role</th><th>What it grants</th></tr></thead><tbody>
<tr><td><code>read</code></td><td>Read-only on a database</td></tr>
<tr><td><code>readWrite</code></td><td>Read + write on a database</td></tr>
<tr><td><code>dbAdmin</code></td><td>Indexes, schema info, stats</td></tr>
<tr><td><code>userAdmin</code></td><td>Manage users in a database</td></tr>
<tr><td><code>root</code></td><td>Superuser; admin DB only</td></tr>
</tbody></table>

<p>Follow least-privilege: app users get <code>readWrite</code> on their database only.</p>
'''

ANSWERS[34] = r'''
<p>The <strong><code>$in</code></strong> operator matches documents where a field&rsquo;s value is in the given <strong>array of values</strong>. It&rsquo;s the equivalent of SQL&rsquo;s <code>IN (...)</code> &mdash; clean and index-friendly.</p>

<pre><code>// Find users in any of these countries
db.users.find({ country: { $in: ["IN", "US", "GB"] } });

// Equivalent to (but cleaner than)
db.users.find({
  $or: [
    { country: "IN" }, { country: "US" }, { country: "GB" }
  ]
});

// $in works on array fields too &mdash; matches if any element matches
// (a doc with tags: ["mongodb", "atlas"] matches the next query)
db.posts.find({ tags: { $in: ["mongodb", "redis"] } });

// Inverse: $nin (not in)
db.users.find({ status: { $nin: ["banned", "deleted"] } });</code></pre>

<p>Performance notes:</p>
<ul>
  <li><strong>Index-friendly</strong> &mdash; if the field is indexed, MongoDB does multiple index seeks (one per value).</li>
  <li><strong>Keep the array small</strong> &mdash; very large <code>$in</code> arrays (thousands of values) can perform worse than alternatives like a join via <code>$lookup</code>.</li>
  <li><strong>Type-sensitive</strong> &mdash; <code>{ $in: ["1"] }</code> won&rsquo;t match <code>1</code> (number). Make sure types match.</li>
</ul>
'''

ANSWERS[35] = r'''
<p>The <strong><code>$or</code></strong> operator matches documents that satisfy <strong>at least one</strong> of the conditions in its array. Each element of the array is a complete query expression.</p>

<pre><code>// Match users who are either admins or have premium plans
db.users.find({
  $or: [
    { role: "admin" },
    { plan: "premium" }
  ]
});

// Combine $or with other filters (AND-ed at the top level)
db.products.find({
  category: "electronics",
  $or: [
    { price: { $lt: 100 } },
    { on_sale: true }
  ]
});

// Nested OR / AND
db.orders.find({
  $or: [
    { $and: [{ status: "pending" }, { total: { $gt: 1000 } }] },
    { is_priority: true }
  ]
});</code></pre>

<p>Performance tips:</p>
<ul>
  <li>Each clause inside <code>$or</code> is evaluated independently &mdash; for best performance, <strong>each branch should be index-supported</strong>. If two of three branches use indexes and one does a collection scan, the whole query falls back to scan.</li>
  <li>If all branches involve the same field, <code>$in</code> is simpler and more efficient: <code>{ status: { $in: ["pending","priority"] } }</code>.</li>
  <li>Use <code>explain("executionStats")</code> to check that each branch picks the right index.</li>
</ul>
'''

ANSWERS[36] = r'''
<p>The <strong><code>$and</code></strong> operator matches documents that satisfy <strong>all</strong> the conditions in its array. In MongoDB, AND is the <em>default</em> when you list multiple fields in a query &mdash; so explicit <code>$and</code> is only needed when conditions on the <em>same field</em> would otherwise collide.</p>

<pre><code>// Implicit AND (most common form)
db.users.find({ active: true, country: "IN" });

// Explicit $and &mdash; required when you have two conditions on the same field
db.products.find({
  $and: [
    { price: { $gte: 100 } },
    { price: { $lte: 500 } }
  ]
});
// Without $and, the second `price` would just overwrite the first

// $and with $or
db.orders.find({
  $and: [
    { customer_id: ObjectId("...") },
    { $or: [{ status: "pending" }, { status: "paid" }] }
  ]
});</code></pre>

<p>Common cases requiring explicit <code>$and</code>:</p>
<ul>
  <li>Two range conditions on one field (between X and Y).</li>
  <li>Multiple <code>$or</code> blocks that must both hold.</li>
  <li>Multiple <code>$elemMatch</code> conditions on the same array field.</li>
</ul>

<p>For the everyday case, just list fields side by side &mdash; <code>$and</code> is implicit and the syntax is cleaner.</p>
'''

ANSWERS[37] = r'''
<p>The <strong><code>$set</code></strong> operator <strong>updates fields</strong> in a document &mdash; either changing existing values or adding new ones. It&rsquo;s the workhorse update operator for partial updates.</p>

<pre><code>// Update an existing field
db.users.updateOne(
  { _id: ObjectId("...") },
  { $set: { email: "new@example.com" } }
);

// Add a new field if it doesn&rsquo;t exist
db.users.updateOne(
  { _id: ObjectId("...") },
  { $set: { last_login: new Date(), login_count: 1 } }
);

// Update nested fields with dot notation
db.users.updateOne(
  { _id: ObjectId("...") },
  { $set: { "address.city": "Mumbai", "address.zip": "400001" } }
);

// Update an element in an array (positional)
db.orders.updateOne(
  { _id: ObjectId("..."), "items.sku": "ABC123" },
  { $set: { "items.$.quantity": 5 } }
);</code></pre>

<p>Why <code>$set</code> matters:</p>
<ul>
  <li><strong>Partial updates</strong> &mdash; without it, the update would replace the entire document, dropping fields you didn&rsquo;t mention.</li>
  <li><strong>Adds missing fields</strong> &mdash; if the field doesn&rsquo;t exist, <code>$set</code> creates it.</li>
  <li><strong>Works inside upserts</strong> &mdash; the <code>$set</code> values populate the new document on insert.</li>
</ul>

<p>Companion: <code>$setOnInsert</code> applies values only on the insert path of an upsert (e.g., <code>created_at</code>).</p>
'''

ANSWERS[38] = r'''
<p>The <strong><code>$unset</code></strong> operator <strong>removes a field</strong> from a document. The value you pass is ignored &mdash; conventionally use <code>""</code> or <code>1</code>. The field is gone after the update; it&rsquo;s not just set to <code>null</code>.</p>

<pre><code>// Remove a single field
db.users.updateOne(
  { _id: ObjectId("...") },
  { $unset: { temp_token: "" } }
);

// Remove multiple fields
db.users.updateOne(
  { _id: ObjectId("...") },
  { $unset: { temp_token: "", reset_code: "", legacy_field: "" } }
);

// Remove a nested field via dot notation
db.users.updateOne(
  { _id: ObjectId("...") },
  { $unset: { "address.zip": "" } }
);

// Remove a field across many documents
db.users.updateMany(
  {},
  { $unset: { deprecated_flag: "" } }
);</code></pre>

<p>Difference between <code>$unset</code> and setting to <code>null</code>:</p>
<ul>
  <li><code>$unset</code> <strong>removes</strong> the field. Queries with <code>{ field: { $exists: false } }</code> match.</li>
  <li><code>{ $set: { field: null } }</code> keeps the field but with a null value. Queries with <code>{ field: null }</code> match either case &mdash; that&rsquo;s often a source of bugs.</li>
</ul>

<p><code>$unset</code> is great for schema migrations &mdash; clean up obsolete fields across millions of documents in one <code>updateMany</code>.</p>
'''

ANSWERS[39] = r'''
<p>The <strong><code>$push</code></strong> operator <strong>appends an element to an array field</strong>. If the field doesn&rsquo;t exist, MongoDB creates it as a new array.</p>

<pre><code>// Append a single element
db.posts.updateOne(
  { _id: ObjectId("...") },
  { $push: { tags: "trending" } }
);

// Append multiple elements at once with $each
db.posts.updateOne(
  { _id: ObjectId("...") },
  { $push: { tags: { $each: ["mongo", "atlas", "guide"] } } }
);

// Limit array size with $slice (keep last 10 entries only)
db.users.updateOne(
  { _id: ObjectId("...") },
  { $push: {
      recent_views: {
        $each: [{ product_id: 42, at: new Date() }],
        $slice: -10                         // keep the last 10
      }
  }}
);

// Insert at a specific position with $position
db.posts.updateOne(
  { _id: ObjectId("...") },
  { $push: { tags: { $each: ["new"], $position: 0 } } }
);</code></pre>

<p>Companion array operators:</p>
<ul>
  <li><strong><code>$addToSet</code></strong> &mdash; append only if the value isn&rsquo;t already in the array (set semantics).</li>
  <li><strong><code>$pull</code></strong> &mdash; remove matching elements.</li>
  <li><strong><code>$pop</code></strong> &mdash; remove first or last (<code>{ $pop: { arr: 1 } }</code> for last, <code>-1</code> for first).</li>
</ul>

<p>Watch unbounded array growth &mdash; large arrays slow queries and can hit the 16 MB document limit. Use <code>$slice</code> to cap or model as separate documents.</p>
'''

ANSWERS[40] = r'''
<p>The <strong><code>$pull</code></strong> operator <strong>removes all elements from an array</strong> that match a given condition. It&rsquo;s the cleanest way to remove items by value or by an embedded query.</p>

<pre><code>// Remove a specific value
db.posts.updateOne(
  { _id: ObjectId("...") },
  { $pull: { tags: "deprecated" } }
);

// Remove multiple values with $in
db.posts.updateOne(
  { _id: ObjectId("...") },
  { $pull: { tags: { $in: ["old", "obsolete"] } } }
);

// Remove array elements matching a query (for arrays of subdocuments)
db.users.updateOne(
  { _id: ObjectId("...") },
  { $pull: { sessions: { device: "ios", expired: true } } }
);

// Remove many elements across many documents
db.users.updateMany(
  {},
  { $pull: { permissions: "deprecated_perm" } }
);</code></pre>

<p>Differences from related operators:</p>
<ul>
  <li><code>$pull</code> removes by value/condition; multiple matches all go.</li>
  <li><code>$pop</code> removes from the start (<code>-1</code>) or end (<code>1</code>); just one element.</li>
  <li><code>$pullAll</code> takes a list and removes all elements matching <em>any</em> exact value (no operators allowed).</li>
</ul>

<p>For arrays of objects, <code>$pull</code> matches on the conditions you specify &mdash; perfect for &ldquo;remove the cart item with productId X&rdquo; or &ldquo;clear all expired sessions.&rdquo;</p>
'''

ANSWERS[41] = r'''
<p>The <strong><code>$elemMatch</code></strong> operator matches documents where <strong>at least one element of an array satisfies all the given conditions <em>simultaneously</em></strong>. It&rsquo;s essential when querying arrays of subdocuments.</p>

<pre><code>// Documents:
// { name: "Alice", scores: [{ subject: "math", grade: 90 }, { subject: "english", grade: 60 }] }
// { name: "Bob",   scores: [{ subject: "math", grade: 60 }, { subject: "english", grade: 90 }] }

// Wrong: matches BOTH because each condition matches some element
db.students.find({
  "scores.subject": "math",
  "scores.grade": { $gte: 80 }
});

// Right: $elemMatch &mdash; one element must satisfy ALL conditions
db.students.find({
  scores: { $elemMatch: { subject: "math", grade: { $gte: 80 } } }
});
// matches only Alice</code></pre>

<p>Use cases:</p>
<ul>
  <li><strong>Arrays of objects</strong> where you need a single element to meet multiple criteria.</li>
  <li><strong>Multiple range conditions on a numeric array</strong>: <code>{ scores: { $elemMatch: { $gte: 80, $lt: 95 } } }</code>.</li>
  <li><strong>Projection</strong>: <code>$elemMatch</code> can also be used in projections to return only the first matching array element &mdash; perfect for paginating activity logs or comments.</li>
</ul>

<p>Without <code>$elemMatch</code>, separate conditions on the same array field are checked independently &mdash; almost always not what you want for arrays of subdocuments.</p>
'''

ANSWERS[42] = r'''
<p>The <strong><code>$exists</code></strong> operator matches documents based on whether a field is <strong>present or absent</strong>, regardless of its value. Useful when documents in a collection have varying schemas.</p>

<pre><code>// Documents that have a phone field (any value, even null)
db.users.find({ phone: { $exists: true } });

// Documents missing a phone field
db.users.find({ phone: { $exists: false } });

// Combine with a value check (must exist AND be non-null)
db.users.find({
  phone: { $exists: true, $ne: null }
});

// Useful for migrations: find docs missing a new field
db.users.find({ schema_version: { $exists: false } });</code></pre>

<table><thead><tr><th>Query</th><th>Matches</th></tr></thead><tbody>
<tr><td><code>{ x: { $exists: true } }</code></td><td>field present (even <code>null</code> or empty)</td></tr>
<tr><td><code>{ x: { $exists: false } }</code></td><td>field absent</td></tr>
<tr><td><code>{ x: null }</code></td><td>field absent OR explicitly <code>null</code></td></tr>
<tr><td><code>{ x: { $ne: null } }</code></td><td>field present AND not <code>null</code></td></tr>
</tbody></table>

<p>Performance note: <code>$exists: true</code> can usually use an index on the field; <code>$exists: false</code> typically can&rsquo;t (it&rsquo;s the absence of an index entry). For schema-version migrations, prefer adding the field with a default and querying by value.</p>
'''

ANSWERS[43] = r'''
<p>The <strong><code>$regex</code></strong> operator matches string fields against a <strong>regular expression</strong>. It supports the full PCRE-like regex syntax.</p>

<pre><code>// Names starting with "Ali" (case-insensitive)
db.users.find({ name: { $regex: "^Ali", $options: "i" } });

// Equivalent shorthand using a JavaScript regex literal
db.users.find({ name: /^Ali/i });

// Match emails ending with @example.com
db.users.find({ email: /@example\.com$/i });

// Find products with codes containing 4-digit numbers
db.products.find({ code: /\d{4}/ });

// $options: i (case-insensitive), m (multiline), x (extended), s (dotall)</code></pre>

<p>Performance and gotchas:</p>
<ul>
  <li><strong>Anchored regex (<code>^</code>) on indexed fields uses the index</strong> &mdash; e.g., <code>/^Ali/</code> is fast.</li>
  <li><strong>Unanchored or case-insensitive regex usually does not use the index</strong> &mdash; can be slow on large collections.</li>
  <li><strong>For full-text search, use <code>$text</code> + a text index</strong> instead &mdash; far faster and supports stemming.</li>
  <li><strong>For complex matching at scale</strong>, integrate with <strong>Atlas Search</strong> (Lucene-based) or a dedicated engine like <strong>Elasticsearch</strong> or <strong>Meilisearch</strong>.</li>
</ul>
'''

ANSWERS[44] = r'''
<p>The <strong><code>$text</code></strong> operator runs a <strong>full-text search</strong> on a collection that has a <strong>text index</strong>. It tokenizes the query string, applies stemming, removes stop words, and scores results by relevance.</p>

<pre><code>// First, create a text index (one per collection)
db.articles.createIndex({ title: "text", body: "text" });

// Search for documents containing "mongodb" or "atlas"
db.articles.find({ $text: { $search: "mongodb atlas" } });

// Phrase search (exact match)
db.articles.find({ $text: { $search: "\"replica set\"" } });

// Exclude a term with -
db.articles.find({ $text: { $search: "mongodb -mysql" } });

// Get the relevance score and sort by it
db.articles.find(
  { $text: { $search: "mongodb tutorial" } },
  { title: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });

// Language-specific stemming
db.articles.find({ $text: { $search: "ejecutivos", $language: "spanish" } });</code></pre>

<p>Limits and alternatives:</p>
<ul>
  <li>Each collection can have <strong>only one text index</strong>, but it can span multiple fields.</li>
  <li>Built-in text search is good for simple cases; for fuzzy matching, autocomplete, faceting, and multi-language relevance, use <strong>MongoDB Atlas Search</strong> (Lucene-powered) or external engines (<strong>Elasticsearch</strong>, <strong>Meilisearch</strong>, <strong>Typesense</strong>).</li>
</ul>
'''

ANSWERS[45] = r'''
<p>You create a <strong>text index</strong> with <code>createIndex()</code>, specifying <code>"text"</code> as the index type for one or more string fields. Text indexes support the <code>$text</code> query operator with full-text search semantics: tokenization, stemming, stop-word removal, and relevance scoring.</p>

<pre><code>// Index a single field
db.articles.createIndex({ title: "text" });

// Index multiple fields (combined into one searchable index)
db.articles.createIndex({ title: "text", body: "text", tags: "text" });

// Weight fields differently &mdash; matches in the title score higher
db.articles.createIndex(
  { title: "text", body: "text" },
  { weights: { title: 10, body: 1 }, name: "article_search" }
);

// Wildcard text index &mdash; index every string field
db.articles.createIndex({ "$**": "text" });

// Specify a default language for stemming
db.articles.createIndex(
  { body: "text" },
  { default_language: "english" }
);</code></pre>

<p>Important constraints:</p>
<ul>
  <li><strong>Only one text index per collection</strong> (it can span multiple fields, though).</li>
  <li><strong>Heavy on RAM and disk</strong> &mdash; text indexes can be 5-10x larger than the source data.</li>
  <li>For modern search needs (fuzzy, autocomplete, facets, ML relevance), <strong>MongoDB Atlas Search</strong> uses Lucene under the hood and is far more capable. For self-hosted, integrate <strong>Elasticsearch</strong>, <strong>OpenSearch</strong>, <strong>Meilisearch</strong>, or <strong>Typesense</strong>.</li>
</ul>
'''

ANSWERS[46] = r'''
<p>The <strong><code>$near</code></strong> operator finds documents whose stored geometry is <strong>nearest to a given point</strong>, sorted by distance. It requires a geospatial index (<code>2dsphere</code> for Earth-like coordinates) and is perfect for &ldquo;find the closest stores&rdquo; queries.</p>

<pre><code>// Each document has a GeoJSON point field
// { name: "Cafe", location: { type: "Point", coordinates: [77.5946, 12.9716] } }

// Create a 2dsphere index
db.places.createIndex({ location: "2dsphere" });

// Find the 10 nearest places to a point, within 5 km
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [77.5946, 12.9716] },  // [lng, lat]
      $minDistance: 0,
      $maxDistance: 5000      // meters
    }
  }
}).limit(10);

// Inside an aggregation pipeline use $geoNear (must be the first stage)
db.places.aggregate([
  { $geoNear: {
      near: { type: "Point", coordinates: [77.5946, 12.9716] },
      distanceField: "distance_meters",
      maxDistance: 5000,
      spherical: true
  }}
]);</code></pre>

<p>Important: <strong>coordinates are <code>[longitude, latitude]</code></strong>, not lat-lng &mdash; a common bug source. Use <code>$geoNear</code> in aggregation pipelines because it adds a computed distance field; <code>$near</code> only sorts results. For huge geo datasets, look at <strong>PostGIS</strong>, <strong>Tile38</strong>, or <strong>H3</strong> hex-indexing for advanced workloads.</p>
'''

ANSWERS[47] = r'''
<p>You create a <strong>geospatial index</strong> with <code>createIndex()</code>, specifying <code>"2dsphere"</code> for Earth-like coordinates (the modern default) or <code>"2d"</code> for legacy planar coordinates. The field stores GeoJSON geometry objects.</p>

<pre><code>// Create a 2dsphere index on the location field
db.places.createIndex({ location: "2dsphere" });

// Documents must store GeoJSON
db.places.insertOne({
  name: "Indiranagar Cafe",
  location: { type: "Point", coordinates: [77.6408, 12.9784] }   // [lng, lat]
});

// Polygons are also valid (city boundaries, delivery zones)
db.zones.insertOne({
  name: "Downtown",
  area: {
    type: "Polygon",
    coordinates: [[ [77.59, 12.96], [77.61, 12.96], [77.61, 12.98], [77.59, 12.98], [77.59, 12.96] ]]
  }
});

// Query: find points within a polygon
db.places.find({
  location: { $geoWithin: { $geometry: zonePolygon } }
});

// Compound geo + filter index for ranking
db.places.createIndex({ location: "2dsphere", category: 1 });</code></pre>

<p>Operators that need a 2dsphere index: <code>$near</code>, <code>$geoNear</code>, <code>$geoWithin</code>, <code>$geoIntersects</code>. Always store coordinates as <code>[longitude, latitude]</code>. For huge geo datasets or advanced queries (isochrones, routing), step out to <strong>PostGIS</strong>, <strong>Tile38</strong>, or libraries like <strong>H3</strong> by Uber.</p>
'''

ANSWERS[48] = r'''
<p>The <strong><code>$inc</code></strong> operator <strong>increments a number field</strong> atomically by the given amount. It&rsquo;s the right tool for counters: page views, like counts, score changes, balance updates.</p>

<pre><code>// Increment by 1
db.posts.updateOne(
  { _id: ObjectId("...") },
  { $inc: { views: 1 } }
);

// Decrement (negative value)
db.users.updateOne(
  { _id: ObjectId("...") },
  { $inc: { credits: -10 } }
);

// Multiple counters at once
db.posts.updateOne(
  { _id: ObjectId("...") },
  { $inc: { views: 1, share_count: 1, score: 5 } }
);

// $inc creates the field if it doesn&rsquo;t exist (starts at 0)
db.posts.updateOne(
  { _id: ObjectId("..."), views: { $exists: false } },
  { $inc: { views: 1 } }
);
// Now views = 1</code></pre>

<p>Why <code>$inc</code> matters:</p>
<ul>
  <li><strong>Atomic on a single document</strong> &mdash; safe for concurrent increments without read-modify-write race conditions.</li>
  <li><strong>Handles negative values</strong> &mdash; pass <code>-1</code> to decrement.</li>
  <li><strong>Companion: <code>$mul</code></strong> &mdash; multiplies a field by a number (10% discount: <code>{ $mul: { price: 0.9 } }</code>).</li>
</ul>

<p>For very high write rates on a single counter (a viral post), spread the count across multiple shards (sharded counters) or use Redis for the hot path and persist periodically.</p>
'''

ANSWERS[49] = r'''
<p>The <strong><code>$max</code></strong> update operator updates a field <strong>only if the new value is greater than the existing one</strong>. If the field doesn&rsquo;t exist, it&rsquo;s set to the new value. Useful for &ldquo;keep the highest seen&rdquo; semantics: high scores, latest timestamps, max prices.</p>

<pre><code>// Update high score only if greater
db.players.updateOne(
  { _id: ObjectId("...") },
  { $max: { high_score: 500 } }
);
// If high_score is 600 -&gt; no change. If 400 or missing -&gt; becomes 500.

// Track the latest activity timestamp
db.users.updateOne(
  { _id: ObjectId("...") },
  { $max: { last_active: new Date() } }
);

// Ensure a max price ceiling is recorded
db.products.updateMany(
  { category: "premium" },
  { $max: { observed_max_price: 9999 } }
);</code></pre>

<p>Compared to a naive read-modify-write:</p>
<ul>
  <li><strong>Atomic</strong> &mdash; no race conditions; safe under concurrency.</li>
  <li><strong>One round trip</strong> &mdash; no need to read first.</li>
  <li><strong>Works with dates and strings</strong> &mdash; uses BSON ordering for comparison.</li>
</ul>

<p>Companion: <strong><code>$min</code></strong> does the opposite &mdash; only updates if the new value is smaller. Both are great for monotonic counters where you only ever want the extreme value to win.</p>
'''

ANSWERS[50] = r'''
<p>The <strong><code>$min</code></strong> update operator updates a field <strong>only if the new value is less than the existing one</strong>. It&rsquo;s the mirror of <code>$max</code> &mdash; perfect for &ldquo;keep the lowest seen&rdquo; semantics like personal-best lap times, lowest observed prices, or earliest dates.</p>

<pre><code>// Track lowest price ever offered
db.products.updateOne(
  { _id: ObjectId("...") },
  { $min: { lowest_price: 99 } }
);
// If lowest_price is 80 -&gt; unchanged. If 120 or missing -&gt; becomes 99.

// Earliest signup date wins
db.users.updateOne(
  { _id: ObjectId("...") },
  { $min: { earliest_seen: new Date("2023-01-01") } }
);

// Best (lowest) lap time
db.racers.updateOne(
  { _id: ObjectId("...") },
  { $min: { best_lap_seconds: 87.42 } }
);</code></pre>

<p>Behavior summary:</p>
<table><thead><tr><th>State</th><th>Result</th></tr></thead><tbody>
<tr><td>Field absent</td><td>Set to the new value</td></tr>
<tr><td>New value smaller</td><td>Updated</td></tr>
<tr><td>New value equal/larger</td><td>Unchanged</td></tr>
</tbody></table>

<p><code>$min</code> and <code>$max</code> together cover monotonic-extreme update needs cleanly and atomically &mdash; no transaction or extra round-trip required. Don&rsquo;t confuse them with the <em>aggregation</em> accumulators of the same names, which compute group-level extremes inside pipelines.</p>
'''

ANSWERS[51] = r'''
<p>The <strong><code>$sum</code></strong> aggregation accumulator <strong>sums numeric values</strong> within a group, or counts documents when given <code>1</code>. It&rsquo;s SQL&rsquo;s SUM and COUNT rolled into one operator and is by far the most-used accumulator in pipelines.</p>

<pre><code>// Total revenue and order count per customer
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: {
      _id: "$customer_id",
      total_revenue: { $sum: "$amount" },
      order_count:   { $sum: 1 }              // count documents
  }}
]);

// Sum across all documents (one row result)
db.orders.aggregate([
  { $group: { _id: null, grand_total: { $sum: "$amount" } } }
]);

// Conditional sum (count only paid orders per customer)
db.orders.aggregate([
  { $group: {
      _id: "$customer_id",
      paid_count: { $sum: { $cond: [{ $eq: ["$status", "paid"] }, 1, 0] } }
  }}
]);

// Sum across an array element (line items)
db.orders.aggregate([
  { $project: {
      total: { $sum: "$line_items.price" }    // works on array values
  }}
]);</code></pre>

<p>Tips:</p>
<ul>
  <li>Non-numeric values are ignored (treated as 0). Make sure data is clean.</li>
  <li>Use <code>$sum: 1</code> for COUNT &mdash; cleaner than counting field presence.</li>
  <li>Combine with <code>$cond</code> for conditional aggregates (filtered counts/sums).</li>
</ul>
'''

ANSWERS[52] = r'''
<p>The <strong><code>$avg</code></strong> aggregation accumulator computes the <strong>average of numeric values</strong> within a group. Non-numeric values are ignored. It&rsquo;s the equivalent of SQL&rsquo;s AVG().</p>

<pre><code>// Average product rating per category
db.products.aggregate([
  { $group: {
      _id: "$category",
      avg_rating: { $avg: "$rating" },
      product_count: { $sum: 1 }
  }}
]);

// Average order amount &mdash; one row, no grouping
db.orders.aggregate([
  { $group: { _id: null, avg_amount: { $avg: "$amount" } } }
]);

// Average price excluding outliers
db.products.aggregate([
  { $match: { price: { $gte: 10, $lte: 1000 } } },
  { $group: { _id: "$category", avg_price: { $avg: "$price" } } }
]);

// Average across an array (per-document)
db.surveys.aggregate([
  { $project: {
      user_id: 1,
      avg_score: { $avg: "$scores" }       // works on numeric array
  }}
]);</code></pre>

<p>Practical notes:</p>
<ul>
  <li><strong>Empty groups return null</strong> for the average &mdash; not zero. Handle in your application or use <code>$ifNull</code>.</li>
  <li><strong>For median/percentiles</strong>, MongoDB doesn&rsquo;t have a direct accumulator &mdash; use <code>$percentile</code> (added in 7.0+) or compute from sorted arrays.</li>
  <li><strong>Pre-filter</strong> with <code>$match</code> before <code>$group</code> &mdash; both for index use and to avoid skewing averages with bad data.</li>
</ul>
'''

ANSWERS[53] = r'''
<p>The <strong><code>$first</code></strong> aggregation accumulator returns the <strong>first value of a field</strong> within each group, based on the current document order in the pipeline. Pair it with <code>$sort</code> upstream to make the order deterministic &mdash; otherwise &ldquo;first&rdquo; is whatever order the docs flowed in, which is unspecified.</p>

<pre><code>// First (most recent) order per customer
db.orders.aggregate([
  { $sort:  { customer_id: 1, created_at: -1 } },
  { $group: {
      _id: "$customer_id",
      most_recent_order: { $first: "$_id" },
      most_recent_amount: { $first: "$amount" }
  }}
]);

// Without $sort, "first" is undefined order &mdash; almost always a bug
db.orders.aggregate([
  { $group: { _id: "$customer_id", first_order: { $first: "$_id" } } }
]);

// Common pattern: dedupe by keeping the newest record per key
db.events.aggregate([
  { $sort: { user_id: 1, timestamp: -1 } },
  { $group: { _id: "$user_id", latest: { $first: "$$ROOT" } } },
  { $replaceRoot: { newRoot: "$latest" } }
]);</code></pre>

<p>Companions:</p>
<ul>
  <li><strong><code>$last</code></strong> &mdash; same idea, but the last document in the sorted order.</li>
  <li><strong><code>$top</code> / <code>$bottom</code></strong> (7.0+) &mdash; sorted picks without needing <code>$sort</code> upstream.</li>
  <li><strong><code>$arrayElemAt</code></strong> with <code>$push + $sort</code> &mdash; older but more flexible.</li>
</ul>

<p><code>$first</code> is the cleanest way to express &ldquo;the most recent X per Y&rdquo; queries.</p>
'''

ANSWERS[54] = r'''
<p>The <strong><code>$last</code></strong> aggregation accumulator returns the <strong>last value of a field</strong> within each group, based on document order in the pipeline. Like <code>$first</code>, you should pair it with <code>$sort</code> upstream so &ldquo;last&rdquo; is well-defined.</p>

<pre><code>// First and last login per user
db.logins.aggregate([
  { $sort:  { user_id: 1, login_at: 1 } },
  { $group: {
      _id: "$user_id",
      first_login: { $first: "$login_at" },
      last_login:  { $last:  "$login_at" }
  }}
]);

// Latest balance from a transaction log
db.tx_log.aggregate([
  { $sort:  { account_id: 1, posted_at: 1 } },
  { $group: { _id: "$account_id", current_balance: { $last: "$balance" } } }
]);

// Without $sort, the order is undefined &mdash; usually a bug
db.events.aggregate([
  { $group: { _id: "$user_id", last_event: { $last: "$type" } } }
]);</code></pre>

<table><thead><tr><th>Accumulator</th><th>Returns</th></tr></thead><tbody>
<tr><td><code>$first</code></td><td>First doc&rsquo;s value in current order</td></tr>
<tr><td><code>$last</code></td><td>Last doc&rsquo;s value in current order</td></tr>
<tr><td><code>$min</code> / <code>$max</code></td><td>Smallest / largest by BSON value</td></tr>
<tr><td><code>$top</code> / <code>$bottom</code></td><td>Top/bottom N by sortBy (7.0+)</td></tr>
</tbody></table>

<p>Use <code>$first/$last</code> with explicit upstream <code>$sort</code>; use <code>$min/$max</code> when you want extremes by value, regardless of insertion order.</p>
'''

ANSWERS[55] = r'''
<p>The <strong><code>$limit</code></strong> aggregation stage <strong>caps the number of documents</strong> passing through the pipeline. It&rsquo;s the equivalent of SQL&rsquo;s LIMIT and is essential for top-N queries and pagination.</p>

<pre><code>// Top 10 customers by total revenue
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: { _id: "$customer_id", total: { $sum: "$amount" } } },
  { $sort:  { total: -1 } },
  { $limit: 10 }
]);

// Pagination: page 3 with 20 results per page
db.products.aggregate([
  { $match: { category: "books" } },
  { $sort:  { created_at: -1 } },
  { $skip:  40 },        // skip first 2 pages
  { $limit: 20 }
]);

// Limit early to bound work for downstream stages
db.events.aggregate([
  { $match: { type: "purchase" } },
  { $limit: 100 },                   // cap before heavier stages
  { $lookup: { from: "users", localField: "user_id", foreignField: "_id", as: "user" } }
]);</code></pre>

<p>Performance tips:</p>
<ul>
  <li><strong>Place <code>$limit</code> as early as possible</strong> &mdash; reduces work for every later stage.</li>
  <li><strong>Sort + Limit can use indexes</strong> if the sort field is indexed; the optimizer applies a top-K shortcut.</li>
  <li><strong>For deep pagination</strong> (page 1000+), prefer range-based pagination using the last seen <code>_id</code> instead of <code>$skip</code> &mdash; <code>$skip</code> still scans skipped documents.</li>
</ul>
'''

ANSWERS[56] = r'''
<p>The <strong><code>$skip</code></strong> aggregation stage <strong>skips the first N documents</strong> from the pipeline before passing the rest forward. It&rsquo;s typically paired with <code>$sort</code> + <code>$limit</code> to implement classic offset-based pagination.</p>

<pre><code>// Page 4 of products, 25 per page
db.products.aggregate([
  { $match: { active: true } },
  { $sort:  { created_at: -1 } },
  { $skip:  75 },          // pages 1-3 skipped
  { $limit: 25 }
]);

// Skip the first match in a sort
db.scores.aggregate([
  { $sort:  { value: -1 } },
  { $skip:  1 },           // skip the leader
  { $limit: 1 }            // get the runner-up
]);</code></pre>

<p>Why offset pagination has problems:</p>
<ul>
  <li><strong>Linear cost</strong> &mdash; <code>$skip 10000</code> still walks 10,000 documents internally before returning the next page. On large collections this gets slow fast.</li>
  <li><strong>Inconsistent results</strong> &mdash; if data changes between page requests (new inserts), entries can shift and you may see duplicates or skip rows.</li>
</ul>

<p>Better alternative: <strong>cursor-based pagination</strong> using the last seen <code>_id</code> or sort key:</p>

<pre><code>// First page
db.products.find({ active: true }).sort({ _id: -1 }).limit(25);

// Next page: pass the last _id from the previous result
db.products.find({ active: true, _id: { $lt: lastSeenId } })
           .sort({ _id: -1 }).limit(25);</code></pre>

<p>This scales to any depth without performance loss.</p>
'''

ANSWERS[57] = r'''
<p>The <strong><code>$sort</code></strong> aggregation stage <strong>orders documents</strong> by one or more fields. Use <code>1</code> for ascending and <code>-1</code> for descending. It&rsquo;s the equivalent of SQL&rsquo;s ORDER BY and is essential for ranking, top-N queries, and pagination.</p>

<pre><code>// Sort by single field
db.products.aggregate([
  { $match: { category: "books" } },
  { $sort:  { price: 1 } }            // ascending
]);

// Sort by multiple fields
db.users.aggregate([
  { $sort: { country: 1, signup_at: -1 } }   // country A-Z, then newest first
]);

// Sort by a computed value
db.orders.aggregate([
  { $project: { customer_id: 1, total: 1, vip: { $gt: ["$total", 1000] } } },
  { $sort: { vip: -1, total: -1 } }
]);

// Sort by relevance score (with $text)
db.articles.aggregate([
  { $match: { $text: { $search: "mongodb" } } },
  { $sort: { score: { $meta: "textScore" } } }
]);</code></pre>

<p>Performance tips:</p>
<ul>
  <li><strong>Index-backed sorts are fast</strong> &mdash; if the sort matches an existing index (or its inverse), MongoDB skips the in-memory sort step entirely.</li>
  <li><strong>In-memory sort has a limit</strong> &mdash; 100 MB by default. Larger sorts need <code>{ allowDiskUse: true }</code> on the aggregation.</li>
  <li><strong>Place <code>$match</code> before <code>$sort</code></strong> to filter as much as possible first.</li>
</ul>
'''

ANSWERS[58] = r'''
<p>The <strong><code>$lookup</code></strong> aggregation stage performs a <strong>left outer join</strong> with another collection. It&rsquo;s MongoDB&rsquo;s answer to SQL&rsquo;s LEFT JOIN &mdash; useful when you can&rsquo;t (or shouldn&rsquo;t) embed related data into a single document.</p>

<pre><code>// Join orders with their customer document
db.orders.aggregate([
  { $lookup: {
      from: "customers",
      localField: "customer_id",        // field in orders
      foreignField: "_id",              // field in customers
      as: "customer"                    // populated array
  }},
  { $unwind: "$customer" }              // flatten the 1-element array
]);

// More flexible variant with a sub-pipeline (filter or project on the joined side)
db.orders.aggregate([
  { $lookup: {
      from: "customers",
      let: { custId: "$customer_id" },
      pipeline: [
        { $match: { $expr: { $and: [
            { $eq: ["$_id", "$$custId"] },
            { $eq: ["$active", true] }
        ]}}},
        { $project: { name: 1, email: 1 } }
      ],
      as: "customer"
  }}
]);</code></pre>

<p>Performance tips:</p>
<ul>
  <li><strong>Always index the foreign field</strong> &mdash; without it, every match runs a full scan.</li>
  <li><strong>Limit data first with <code>$match</code></strong> &mdash; do as little work as possible before joining.</li>
  <li><strong>Avoid heavy <code>$lookup</code> on hot paths</strong> &mdash; if you need joins constantly, embed or denormalize. MongoDB rewards thinking about access patterns first.</li>
</ul>

<p>For complex many-table joins, a relational database is simply a better fit.</p>
'''

ANSWERS[59] = r'''
<p>The <strong><code>$unwind</code></strong> aggregation stage <strong>flattens an array field</strong>, producing one output document per array element. It&rsquo;s essential when you need to operate on individual items inside an array &mdash; grouping, joining, or projecting them separately.</p>

<pre><code>// Document:
// { _id: 1, customer: "Alice", items: ["pen", "book", "lamp"] }

db.orders.aggregate([
  { $unwind: "$items" }
]);
// Yields three documents:
// { _id: 1, customer: "Alice", items: "pen" }
// { _id: 1, customer: "Alice", items: "book" }
// { _id: 1, customer: "Alice", items: "lamp" }

// Common: count individual items sold across all orders
db.orders.aggregate([
  { $unwind: "$items" },
  { $group: { _id: "$items", times_sold: { $sum: 1 } } },
  { $sort:  { times_sold: -1 } }
]);

// Preserve documents whose array is empty or missing
db.orders.aggregate([
  { $unwind: { path: "$items", preserveNullAndEmptyArrays: true } }
]);

// Get the array index too
db.orders.aggregate([
  { $unwind: { path: "$items", includeArrayIndex: "item_position" } }
]);</code></pre>

<p>Watch for the <strong>document-explosion</strong> trap &mdash; an order with a 1,000-item array becomes 1,000 documents in the pipeline. <code>$unwind</code> is powerful but can blow up memory; filter aggressively before unwinding when possible.</p>
'''

ANSWERS[60] = r'''
<p>The <strong><code>$out</code></strong> aggregation stage writes the <strong>entire pipeline result to a collection</strong>, replacing it. It must be the <strong>last</strong> stage. It&rsquo;s how you materialize the output of an aggregation as a new (or refreshed) collection.</p>

<pre><code>// Daily revenue rollup written to a new collection
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      revenue: { $sum: "$amount" },
      order_count: { $sum: 1 }
  }},
  { $out: "daily_revenue" }       // creates or replaces daily_revenue
]);

// Output to a different database
db.orders.aggregate([
  // ... pipeline stages
  { $out: { db: "analytics", coll: "daily_revenue" } }
]);</code></pre>

<p>Important behaviors:</p>
<ul>
  <li><strong>Replaces the entire collection</strong> &mdash; good for full rebuilds, dangerous for incremental updates.</li>
  <li><strong>Must be last stage</strong> in the pipeline.</li>
  <li><strong>Atomic swap</strong> in modern versions &mdash; readers see the old collection until the new one is fully written.</li>
</ul>

<p>For incremental rollups, use <strong><code>$merge</code></strong> instead &mdash; it inserts/updates/replaces matching documents based on a key, leaving non-matching documents untouched. <code>$out</code> is for &ldquo;rebuild from scratch&rdquo; jobs; <code>$merge</code> is for &ldquo;keep this collection in sync&rdquo; pipelines.</p>
'''

ANSWERS[61] = r'''
<p>The <strong><code>$addFields</code></strong> aggregation stage <strong>adds new fields</strong> (or overwrites existing ones) to documents flowing through the pipeline, while keeping all other fields intact. It&rsquo;s like <code>$project</code> but <em>additive</em> &mdash; you don&rsquo;t have to list every field you want to keep.</p>

<pre><code>// Add a computed total field with tax
db.orders.aggregate([
  { $addFields: {
      total_with_tax: { $multiply: ["$amount", 1.18] }
  }}
]);

// Add multiple fields and reshape
db.users.aggregate([
  { $addFields: {
      full_name: { $concat: ["$first_name", " ", "$last_name"] },
      year_born: { $subtract: [{ $year: new Date() }, "$age"] },
      is_premium: { $eq: ["$plan", "premium"] }
  }}
]);

// Add a field based on conditional logic
db.products.aggregate([
  { $addFields: {
      tier: {
        $switch: {
          branches: [
            { case: { $gte: ["$price", 1000] }, then: "premium" },
            { case: { $gte: ["$price", 100]  }, then: "standard" }
          ],
          default: "budget"
        }
      }
  }}
]);

// Update nested fields with dot notation
db.orders.aggregate([
  { $addFields: { "shipping.priority": "high" } }
]);</code></pre>

<p>Use <code>$addFields</code> when you want to enrich documents without dropping anything. Use <code>$project</code> when you want fine-grained control (include/exclude specific fields). Use <code>$set</code> &mdash; an alias for <code>$addFields</code> &mdash; in update aggregations.</p>
'''

ANSWERS[62] = r'''
<p>The <strong><code>$replaceRoot</code></strong> aggregation stage <strong>replaces the entire document with another sub-document</strong> from the current pipeline. It&rsquo;s the cleanest way to promote a nested object to the top level or restructure deeply nested results.</p>

<pre><code>// Document: { _id: 1, name: "Alice", profile: { age: 30, city: "Pune" } }
db.users.aggregate([
  { $replaceRoot: { newRoot: "$profile" } }
]);
// Result: { age: 30, city: "Pune" }     // _id and name are gone

// Combine current doc with embedded object
db.users.aggregate([
  { $replaceRoot: {
      newRoot: { $mergeObjects: [{ _id: "$_id" }, "$profile"] }
  }}
]);
// Result: { _id: 1, age: 30, city: "Pune" }

// Pattern: dedupe-by-newest with $first + $replaceRoot
db.events.aggregate([
  { $sort:  { user_id: 1, timestamp: -1 } },
  { $group: { _id: "$user_id", latest: { $first: "$$ROOT" } } },
  { $replaceRoot: { newRoot: "$latest" } }
]);</code></pre>

<p>Modern alternative: <strong><code>$replaceWith</code></strong> &mdash; an alias for <code>$replaceRoot</code> with cleaner syntax (<code>{ $replaceWith: "$profile" }</code>). Use whichever you prefer.</p>

<p>Use <code>$replaceRoot</code> when you need a different document shape entirely (e.g., promote a nested doc up). Use <code>$project</code> when you just want to keep/drop specific fields without rearranging the whole structure.</p>
'''

ANSWERS[63] = r'''
<p>The <strong><code>$merge</code></strong> aggregation stage <strong>writes pipeline results to a collection</strong>, but unlike <code>$out</code>, it can <strong>insert, update, or replace</strong> matching documents based on a key, leaving non-matching documents untouched. It must be the last stage.</p>

<pre><code>// Daily revenue rollup, merged into existing analytics collection
db.orders.aggregate([
  { $match: { created_at: { $gte: ISODate("2026-04-01") } } },
  { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      revenue: { $sum: "$amount" },
      order_count: { $sum: 1 }
  }},
  { $merge: {
      into: "daily_revenue",
      on: "_id",                                       // match key
      whenMatched: "replace",                          // replace if exists
      whenNotMatched: "insert"                         // insert if missing
  }}
]);

// Modes for whenMatched: "merge" (default), "replace", "keepExisting", "fail", "[pipeline]"
// Modes for whenNotMatched: "insert" (default), "discard", "fail"

// Cross-database merge
db.orders.aggregate([
  // ...
  { $merge: { into: { db: "analytics", coll: "rollup" }, on: "_id" } }
]);</code></pre>

<table><thead><tr><th>Use case</th><th>Stage</th></tr></thead><tbody>
<tr><td>Rebuild whole collection</td><td><code>$out</code> (replace all)</td></tr>
<tr><td>Incremental upserts</td><td><code>$merge</code> with <code>"replace"</code> or <code>"merge"</code></td></tr>
<tr><td>Insert-only (skip duplicates)</td><td><code>$merge</code> with <code>"keepExisting"</code></td></tr>
</tbody></table>

<p><code>$merge</code> turns aggregation pipelines into proper ETL jobs &mdash; ideal for nightly rollups, materialized views, and event-sourced projections.</p>
'''

ANSWERS[64] = r'''
<p>A <strong>compound index</strong> covers <strong>multiple fields</strong> in a single index, with a defined order. It speeds up queries that filter, sort, or group on any leading prefix of those fields &mdash; a rule called the <strong>leftmost-prefix rule</strong>.</p>

<pre><code>// Compound index on customer_id + created_at
db.orders.createIndex({ customer_id: 1, created_at: -1 });

// Queries that USE this index efficiently:
db.orders.find({ customer_id: 42 });
db.orders.find({ customer_id: 42, created_at: { $gte: lastWeek } });
db.orders.find({ customer_id: 42 }).sort({ created_at: -1 });

// Queries that DO NOT use this index efficiently:
db.orders.find({ created_at: { $gte: lastWeek } });   // missing leftmost field
db.orders.find().sort({ created_at: -1 });            // no customer filter

// Equality, then sort, then range &mdash; the ESR rule
db.orders.createIndex({ customer_id: 1, status: 1, created_at: -1 });</code></pre>

<p>Best practices:</p>
<ul>
  <li><strong>Order matters</strong> &mdash; put the most selective and most-filtered field first.</li>
  <li><strong>ESR rule</strong> &mdash; <em>E</em>quality fields, then <em>S</em>ort fields, then <em>R</em>ange fields, in that order, to maximize index use.</li>
  <li><strong>Direction matters for sort</strong> &mdash; <code>{ a: 1, b: -1 }</code> can serve <code>sort: { a: 1, b: -1 }</code> or <code>{ a: -1, b: 1 }</code> (the inverse), but not <code>{ a: 1, b: 1 }</code>.</li>
  <li><strong>Verify with <code>explain()</code></strong> &mdash; look for <code>IXSCAN</code> stage and zero-or-low <code>nReturned/totalDocsExamined</code> ratio.</li>
</ul>
'''

ANSWERS[65] = r'''
<p>You delete a database with <code>db.dropDatabase()</code>. It permanently removes the database, all its collections, and all their indexes &mdash; there&rsquo;s no recycle bin.</p>

<pre><code>// Switch to the database you want to drop
use scratch_db

// Drop it
db.dropDatabase();
// Returns: { dropped: "scratch_db", ok: 1 }

// Verify it&rsquo;s gone
show dbs

// Drop from any context (cleaner)
db.getSiblingDB("scratch_db").dropDatabase();</code></pre>

<p>Behaviors and warnings:</p>
<ul>
  <li><strong>Permanent</strong> &mdash; no undo. Have backups for production.</li>
  <li><strong>Affects all replica members</strong> &mdash; replicates immediately to secondaries.</li>
  <li><strong>Faster than deleting documents</strong> &mdash; it&rsquo;s a metadata operation, not a per-row delete.</li>
  <li><strong>Doesn&rsquo;t free system DBs</strong> &mdash; <code>admin</code>, <code>local</code>, and <code>config</code> can&rsquo;t be dropped this way (they hold cluster state).</li>
</ul>

<p>Permission requirement: the user must have the <code>dropDatabase</code> privilege (typically a <code>dbAdmin</code> or above on that database). For production cleanups, prefer scripted deletes with logging or use Atlas&rsquo;s GUI which records the action in audit logs.</p>
'''

ANSWERS[66] = r'''
<p>The <strong><code>db.collection.stats()</code></strong> method returns <strong>storage statistics</strong> about a collection &mdash; size on disk, document count, average document size, index sizes, and storage engine details. It&rsquo;s the go-to command for understanding how much space a collection uses.</p>

<pre><code>db.orders.stats();

// Selected output fields:
{
  ns: "shopdb.orders",
  count: 1500000,                  // document count
  size: 482000000,                 // logical size in bytes
  avgObjSize: 321,                 // average document size
  storageSize: 220000000,          // compressed disk usage
  totalIndexSize: 180000000,
  indexSizes: {
    _id_: 75000000,
    "customer_id_1": 50000000,
    "created_at_-1": 55000000
  },
  capped: false,
  wiredTiger: { /* engine details */ }
}

// Just the size in MB
db.orders.stats({ scale: 1024*1024 });</code></pre>

<p>Use <code>stats()</code> to:</p>
<ul>
  <li><strong>Spot bloated collections</strong> &mdash; large size + small count = wasted space; consider <code>compact</code>.</li>
  <li><strong>Audit indexes</strong> &mdash; oversized indexes can dominate RAM; drop unused ones (find with <code>$indexStats</code>).</li>
  <li><strong>Plan capacity</strong> &mdash; combined with <code>db.stats()</code> at the database level for total footprint.</li>
</ul>

<p>For deeper analytics, the <strong>MongoDB Atlas</strong> UI surfaces all of this visually plus growth trends.</p>
'''

ANSWERS[67] = r'''
<p>You retrieve the list of collections in the current database with <code>show collections</code> in the shell, or <code>db.getCollectionNames()</code> in scripts/drivers.</p>

<pre><code>use shopdb

// Shell command (mongosh)
show collections

// Programmatic (returns an array)
db.getCollectionNames();
// [ "users", "orders", "products" ]

// More detail with listCollections command
db.runCommand({ listCollections: 1 });
// Includes name, type (collection/view), options, info, idIndex

// Filter by name pattern
db.getCollectionNames().filter(n =&gt; n.startsWith("user_"));

// In Node.js driver
const db = client.db("shopdb");
const cols = await db.listCollections().toArray();
console.log(cols.map(c =&gt; c.name));</code></pre>

<p>Notes:</p>
<ul>
  <li><strong>System collections are usually hidden</strong> from <code>show collections</code> &mdash; e.g., <code>system.views</code>, <code>system.indexes</code>. Use <code>listCollections</code> to see them.</li>
  <li><strong>Views appear too</strong> &mdash; views are virtual collections defined by an aggregation; the <code>type</code> field distinguishes them.</li>
  <li><strong>Permissions</strong> &mdash; the user must have read access to the database to list collections.</li>
</ul>

<p>For migrations or admin scripts, <code>listCollections</code> is the canonical command and includes capped/sharded/option metadata in addition to names.</p>
'''

ANSWERS[68] = r'''
<p>You retrieve the list of databases with <code>show dbs</code> (or <code>show databases</code>) in the shell, or <code>db.adminCommand({ listDatabases: 1 })</code> programmatically.</p>

<pre><code>// Shell shortcut
show dbs
//  admin     200 KB
//  config     72 KB
//  local      1.2 MB
//  shopdb     482 MB

// Programmatic
db.adminCommand({ listDatabases: 1 });

// Filter empty databases
db.adminCommand({ listDatabases: 1, nameOnly: true });

// In Node.js driver
const result = await client.db().admin().listDatabases();
console.log(result.databases.map(d =&gt; d.name));</code></pre>

<p>Behaviors and notes:</p>
<ul>
  <li><strong>Lazily created databases don&rsquo;t appear</strong> until you actually write a document into them.</li>
  <li><strong>System databases</strong>: <code>admin</code> (users, system commands), <code>config</code> (sharded cluster metadata), <code>local</code> (per-server data including the oplog) are always present.</li>
  <li><strong>Permissions</strong> &mdash; the user typically needs the <code>listDatabases</code> privilege on the cluster (built into <code>readAnyDatabase</code> and <code>clusterMonitor</code> roles).</li>
</ul>

<p>For scripting and dashboards, prefer <code>listDatabases</code> with <code>nameOnly: true</code> &mdash; it&rsquo;s lightweight and skips the per-DB stats lookup.</p>
'''

ANSWERS[69] = r'''
<p>The <strong><code>db.collection.drop()</code></strong> method <strong>permanently removes a collection</strong> and all of its indexes. It&rsquo;s a metadata operation &mdash; far faster than deleting every document one by one.</p>

<pre><code>// Drop a collection
db.test_data.drop();
// Returns true if dropped, false if it didn&rsquo;t exist

// Empty a collection: use drop instead of deleteMany({})
db.test_data.drop();             // O(1) metadata op
db.test_data.deleteMany({});     // O(N) document scan

// Drop with options
db.runCommand({ drop: "test_data", writeConcern: { w: "majority" } });</code></pre>

<table><thead><tr><th>Operation</th><th>Speed</th><th>Behavior</th></tr></thead><tbody>
<tr><td><code>drop()</code></td><td>Near-instant</td><td>Removes collection + indexes</td></tr>
<tr><td><code>deleteMany({})</code></td><td>Linear in document count</td><td>Removes documents, keeps indexes</td></tr>
<tr><td>TTL index</td><td>Background</td><td>Auto-removes documents past expiry</td></tr>
</tbody></table>

<p>Important caveats:</p>
<ul>
  <li><strong>Permanent and immediate</strong> &mdash; no recycle bin.</li>
  <li><strong>Indexes are gone</strong> &mdash; you&rsquo;ll need to recreate them if you re-add data.</li>
  <li><strong>Active queries against the collection will error</strong> &mdash; coordinate with running services.</li>
  <li><strong>For temporary cleanup of test/dev data</strong>, <code>drop()</code> is the right tool. For ongoing production data lifecycle, use TTL indexes.</li>
</ul>
'''

ANSWERS[70] = r'''
<p>You perform a <strong>bulk insert</strong> with <code>insertMany()</code> for a batch of documents, or <code>bulkWrite()</code> for a mix of inserts, updates, and deletes in a single round trip. Both are far faster than individual <code>insertOne()</code> calls.</p>

<pre><code>// Batch insert
db.users.insertMany([
  { name: "Alice", email: "alice@example.com" },
  { name: "Bob",   email: "bob@example.com"   },
  { name: "Carol", email: "carol@example.com" }
]);

// Unordered: continues past errors (faster, parallel-safe)
db.users.insertMany(docs, { ordered: false });

// Mixed bulk operations
db.products.bulkWrite([
  { insertOne:  { document: { name: "Pen", price: 10 } } },
  { updateOne:  { filter: { sku: "ABC" }, update: { $inc: { stock: 100 } } } },
  { deleteMany: { filter: { discontinued: true } } }
], { ordered: false });

// Returns counts: insertedCount, modifiedCount, deletedCount, etc.</code></pre>

<p>Performance tips:</p>
<ul>
  <li><strong>Batch size 500-1,000</strong> documents per call is a healthy sweet spot. The hard limit is 100,000 ops per <code>bulkWrite</code> in modern versions, but smaller batches mean more frequent feedback and lower memory.</li>
  <li><strong>Use <code>ordered: false</code></strong> for parallel writes and to skip past individual errors (e.g., duplicate keys).</li>
  <li><strong>For very large imports</strong>, the <strong><code>mongoimport</code></strong> CLI tool or <strong>MongoDB Atlas Data API</strong> can be faster.</li>
  <li><strong>Drop and rebuild secondary indexes</strong> for one-shot huge loads to skip per-document index updates.</li>
</ul>
'''

ANSWERS[71] = r'''
<p>The <strong><code>$type</code></strong> operator matches documents where a field has a specific <strong>BSON type</strong> &mdash; useful when collections have inconsistent data and you need to find or fix mismatched types.</p>

<pre><code>// Find documents where age is stored as a string (data quality issue)
db.users.find({ age: { $type: "string" } });

// Find numeric fields stored as numbers
db.products.find({ price: { $type: "number" } });   // matches int, long, double, decimal

// Multiple types
db.users.find({ phone: { $type: ["string", "long"] } });

// By BSON type number
db.users.find({ created_at: { $type: 9 } });        // 9 = date

// Common type aliases:
// "string", "number", "double", "int", "long", "decimal",
// "object", "array", "binData", "objectId", "bool", "date",
// "null", "regex", "javascript", "timestamp"</code></pre>

<table><thead><tr><th>Use case</th><th>Query</th></tr></thead><tbody>
<tr><td>Find string-typed numbers (bug)</td><td><code>{ price: { $type: "string" } }</code></td></tr>
<tr><td>Documents with array field</td><td><code>{ tags: { $type: "array" } }</code></td></tr>
<tr><td>Identify nulls (vs missing)</td><td><code>{ field: { $type: "null" } }</code></td></tr>
</tbody></table>

<p>Use <code>$type</code> for data validation and migrations &mdash; combined with an <code>updateMany</code> using <code>$convert</code> or <code>$toInt</code>, you can fix typed-incorrectly fields in one pass. For new collections, set up <strong>schema validation</strong> at create time to prevent the problem.</p>
'''

ANSWERS[72] = r'''
<p>The <strong><code>$all</code></strong> operator matches arrays that contain <strong>every value in a given list</strong> (in any order). It&rsquo;s the &ldquo;contains all of these tags&rdquo; query and is essential for tag/label filters.</p>

<pre><code>// Posts tagged with BOTH "mongodb" AND "tutorial"
db.posts.find({ tags: { $all: ["mongodb", "tutorial"] } });

// Compare with $in (which matches ANY of the values)
db.posts.find({ tags: { $in: ["mongodb", "tutorial"] } });   // either one

// $all with $elemMatch for arrays of subdocuments
db.products.find({
  reviews: {
    $all: [
      { $elemMatch: { rating: 5, verified: true } },
      { $elemMatch: { rating: { $lte: 2 } } }      // both a 5-star verified AND a low review
    ]
  }
});

// Single element shortcut
db.posts.find({ tags: { $all: ["mongodb"] } });   // same as { tags: "mongodb" }</code></pre>

<table><thead><tr><th>Operator</th><th>Matches</th></tr></thead><tbody>
<tr><td><code>$all</code></td><td>Array contains <strong>every</strong> listed value</td></tr>
<tr><td><code>$in</code></td><td>Array contains <strong>at least one</strong> listed value</td></tr>
<tr><td><code>$nin</code></td><td>Array contains <strong>none</strong> of the listed values</td></tr>
<tr><td><code>$size</code></td><td>Array has an <strong>exact length</strong></td></tr>
</tbody></table>

<p>For tag-based search at scale, an array index plus <code>$all</code> works well; for fuzzy matching or relevance scoring, prefer <strong>Atlas Search</strong> or an external engine.</p>
'''

ANSWERS[73] = r'''
<p>The <strong><code>$size</code></strong> operator matches documents where an <strong>array has an exact length</strong>. It can&rsquo;t express ranges &mdash; only exact matches.</p>

<pre><code>// Posts with exactly 3 tags
db.posts.find({ tags: { $size: 3 } });

// Empty array
db.users.find({ permissions: { $size: 0 } });

// $size cannot do ranges directly &mdash; this DOES NOT WORK:
db.posts.find({ tags: { $size: { $gt: 2 } } });   // ❌ error

// For range checks, use aggregation with $size as an expression
db.posts.aggregate([
  { $match: { $expr: { $gt: [{ $size: "$tags" }, 2] } } }
]);

// Or pre-compute with $addFields
db.posts.aggregate([
  { $addFields: { tag_count: { $size: "$tags" } } },
  { $match:     { tag_count: { $gt: 2, $lte: 10 } } }
]);

// Maintain a denormalized counter on writes for fast queries
db.posts.updateOne(
  { _id: postId },
  { $push: { tags: "new" }, $inc: { tag_count: 1 } }
);</code></pre>

<p>Performance: <code>$size</code> can&rsquo;t use a regular array index because the index entries point at individual elements, not array length. For frequent length-based queries, denormalize a <code>tag_count</code> field and index <em>that</em> &mdash; then range queries are fast.</p>
'''

ANSWERS[74] = r'''
<p>The <strong><code>$slice</code></strong> projection operator returns a <strong>subset of an array</strong> &mdash; the first N elements, the last N elements, or a range. It&rsquo;s a projection-time tool to avoid pulling huge arrays back.</p>

<pre><code>// Document: { _id: 1, comments: [c1, c2, c3, c4, c5] }

// First 3 comments
db.posts.find({ _id: 1 }, { comments: { $slice: 3 } });
// returns comments: [c1, c2, c3]

// Last 2 comments
db.posts.find({ _id: 1 }, { comments: { $slice: -2 } });
// returns comments: [c4, c5]

// Skip 1, return next 2 (offset, count)
db.posts.find({ _id: 1 }, { comments: { $slice: [1, 2] } });
// returns comments: [c2, c3]

// In aggregation as an array operator
db.posts.aggregate([
  { $project: {
      latest_three: { $slice: ["$comments", -3] }
  }}
]);

// $slice as an UPDATE operator (cap array length)
db.users.updateOne(
  { _id: ObjectId("...") },
  { $push: {
      recent_views: { $each: [{ id: 42 }], $slice: -10 }   // keep last 10
  }}
);</code></pre>

<p>Common pattern: store a small &ldquo;recent N&rdquo; array on the user document for fast display, while a separate collection holds the full activity log. Use <code>$slice</code> on update to cap the size and on projection to return only what the UI needs.</p>
'''

ANSWERS[75] = r'''
<p>The <strong><code>$mod</code></strong> operator matches documents where a numeric field, when divided by a divisor, gives a specified remainder. It&rsquo;s niche but useful for sampling or shard-key bucketing.</p>

<pre><code>// Find users whose id % 10 == 0 (every 10th user, deterministic sample)
db.users.find({ user_number: { $mod: [10, 0] } });

// Even-numbered orders
db.orders.find({ order_no: { $mod: [2, 0] } });

// Match: field % divisor === remainder
// Syntax: { field: { $mod: [divisor, remainder] } }

// Sampling 1% deterministically by hashing first
db.events.aggregate([
  { $match: { $expr: { $eq: [{ $mod: [{ $abs: { $hash: "$user_id" } }, 100] }, 0] } } }
]);</code></pre>

<p>Practical uses:</p>
<ul>
  <li><strong>Deterministic sampling</strong> &mdash; same input always picks same output, repeatable.</li>
  <li><strong>Shard simulation</strong> &mdash; partition a dataset across N consumers manually.</li>
  <li><strong>Round-robin assignment</strong> &mdash; assign records to workers based on <code>id % worker_count</code>.</li>
</ul>

<p>For random sampling, prefer <code>$sample</code> in aggregation: <code>{ $sample: { size: 1000 } }</code> &mdash; it&rsquo;s built for the job and uses an efficient algorithm. <code>$mod</code> can&rsquo;t use indexes for this kind of query, so test on a representative dataset before deploying.</p>
'''

ANSWERS[76] = r'''
<p>The <strong><code>$ifNull</code></strong> aggregation operator returns the <strong>first non-null/non-missing value</strong> from its arguments &mdash; like SQL&rsquo;s COALESCE. Use it to provide defaults for missing fields.</p>

<pre><code>// If display_name is missing or null, fall back to email
db.users.aggregate([
  { $project: {
      handle: { $ifNull: ["$display_name", "$email"] }
  }}
]);

// Default to a literal value
db.products.aggregate([
  { $project: {
      name: 1,
      stock: { $ifNull: ["$stock", 0] }
  }}
]);

// Chain multiple fallbacks (modern MongoDB 4.4+ supports multiple args)
db.users.aggregate([
  { $project: {
      label: { $ifNull: ["$nickname", "$display_name", "$email", "Anonymous"] }
  }}
]);

// Use inside accumulators to handle missing data
db.orders.aggregate([
  { $group: {
      _id: "$customer_id",
      total: { $sum: { $ifNull: ["$amount", 0] } }
  }}
]);</code></pre>

<p>Practical tips:</p>
<ul>
  <li>Treats both <strong>null</strong> and <strong>missing fields</strong> the same way &mdash; both fall through to the next argument.</li>
  <li>Cleaner than <code>$cond</code> with a manual null check.</li>
  <li>Useful in projections to ensure consistent output shape.</li>
</ul>
'''

ANSWERS[77] = r'''
<p>The <strong><code>$dateToString</code></strong> aggregation operator <strong>formats a date</strong> as a string using a format spec like <code>%Y-%m-%d</code>. It&rsquo;s essential for grouping by day/week/month or for clean output.</p>

<pre><code>// Group orders by day
db.orders.aggregate([
  { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
      revenue: { $sum: "$amount" }
  }}
]);

// Format with timezone
db.orders.aggregate([
  { $project: {
      day: {
        $dateToString: {
          format: "%Y-%m-%d %H:%M",
          date: "$created_at",
          timezone: "Asia/Kolkata"
        }
      }
  }}
]);

// Custom labels
db.orders.aggregate([
  { $project: {
      label: {
        $dateToString: { format: "Order on %A, %d %B %Y", date: "$created_at" }
      }
  }}
]);

// Common format codes:
// %Y year, %m month, %d day, %H hour, %M minute, %S second
// %A weekday name, %B month name, %j day of year, %V ISO week</code></pre>

<p>Modern alternatives in MongoDB 5.0+:</p>
<ul>
  <li><strong><code>$dateTrunc</code></strong> &mdash; truncate a date to a unit (day, week, month, quarter, year). Cleaner for time-bucketing.</li>
  <li><strong><code>$dateAdd</code> / <code>$dateSubtract</code> / <code>$dateDiff</code></strong> &mdash; arithmetic on dates with timezone awareness.</li>
</ul>

<p>For pure analytics workloads, push date math into <strong>Atlas Charts</strong> or your warehouse &mdash; MongoDB&rsquo;s date operators are fine for transactional pipelines but limited compared to BigQuery, Snowflake, or ClickHouse.</p>
'''

ANSWERS[78] = r'''
<p>The <strong><code>$cond</code></strong> aggregation operator is the <strong>ternary if-then-else</strong>. It evaluates a condition and returns one of two values based on the result. It&rsquo;s the bread-and-butter conditional for projections and computed fields.</p>

<pre><code>// Tag VIP customers based on total spend
db.customers.aggregate([
  { $project: {
      name: 1,
      tier: {
        $cond: {
          if:   { $gte: ["$total_spent", 10000] },
          then: "VIP",
          else: "Regular"
        }
      }
  }}
]);

// Shorthand array syntax: [condition, then, else]
db.products.aggregate([
  { $project: {
      sale_price: { $cond: ["$on_sale", { $multiply: ["$price", 0.8] }, "$price"] }
  }}
]);

// Conditional aggregation (count VIPs)
db.customers.aggregate([
  { $group: {
      _id: null,
      vip_count: {
        $sum: { $cond: [{ $gte: ["$total_spent", 10000] }, 1, 0] }
      }
  }}
]);</code></pre>

<p>For <strong>more than two branches</strong>, use <strong><code>$switch</code></strong> &mdash; it expresses multi-way choices cleanly without nested <code>$cond</code> calls. <code>$cond</code> nests work but become unreadable past two levels:</p>

<pre><code>// Nested $cond: hard to read
{ $cond: [c1, t1, { $cond: [c2, t2, { $cond: [c3, t3, default] }] }] }

// $switch: clear
{ $switch: {
    branches: [
      { case: c1, then: t1 },
      { case: c2, then: t2 },
      { case: c3, then: t3 }
    ],
    default: default_value
}}</code></pre>
'''

ANSWERS[79] = r'''
<p>The <strong><code>$switch</code></strong> aggregation operator evaluates a series of <strong>case/branch conditions</strong> and returns the value for the first one that&rsquo;s true. It&rsquo;s the multi-way conditional &mdash; cleaner than nested <code>$cond</code>.</p>

<pre><code>// Categorize products by price band
db.products.aggregate([
  { $project: {
      name: 1,
      price: 1,
      tier: {
        $switch: {
          branches: [
            { case: { $gte: ["$price", 1000] }, then: "premium" },
            { case: { $gte: ["$price", 100]  }, then: "standard" },
            { case: { $gte: ["$price", 10]   }, then: "budget" }
          ],
          default: "discount"
        }
      }
  }}
]);

// Map status codes to human labels
db.orders.aggregate([
  { $project: {
      status_text: {
        $switch: {
          branches: [
            { case: { $eq: ["$status", "P"] }, then: "Pending" },
            { case: { $eq: ["$status", "S"] }, then: "Shipped" },
            { case: { $eq: ["$status", "D"] }, then: "Delivered" },
            { case: { $eq: ["$status", "C"] }, then: "Cancelled" }
          ],
          default: "Unknown"
        }
      }
  }}
]);</code></pre>

<p>Important behaviors:</p>
<ul>
  <li><strong>First match wins</strong> &mdash; subsequent branches aren&rsquo;t checked. Order matters.</li>
  <li><strong><code>default</code> is required</strong> &mdash; without it, no match raises an error at runtime. Always include one even if it&rsquo;s <code>null</code>.</li>
  <li><strong>Each branch&rsquo;s <code>case</code></strong> can be any expression that evaluates to a boolean.</li>
</ul>

<p>Use <code>$switch</code> for any 3+ branch conditional &mdash; the readability gain over nested <code>$cond</code> is substantial.</p>
'''

ANSWERS[80] = r'''
<p>The <strong><code>$map</code></strong> aggregation operator <strong>transforms each element of an array</strong>, returning a new array of the same length. It&rsquo;s like JavaScript&rsquo;s <code>Array.map()</code>.</p>

<pre><code>// Document: { _id: 1, prices: [10, 20, 30] }

// Add 18% tax to each price
db.products.aggregate([
  { $project: {
      prices_with_tax: {
        $map: {
          input: "$prices",
          as: "p",
          in: { $multiply: ["$$p", 1.18] }
      }
    }
  }}
]);
// Output: prices_with_tax: [11.8, 23.6, 35.4]

// Transform array of subdocuments
db.orders.aggregate([
  { $project: {
      summary_items: {
        $map: {
          input: "$items",
          as: "item",
          in: {
            sku: "$$item.sku",
            total: { $multiply: ["$$item.price", "$$item.qty"] }
          }
      }
    }
  }}
]);

// Use with $filter to map only some elements
db.products.aggregate([
  { $project: {
      premium_items: {
        $map: {
          input: { $filter: { input: "$items", as: "i", cond: { $gte: ["$$i.price", 100] } } },
          as: "p",
          in: "$$p.name"
      }
    }
  }}
]);</code></pre>

<p>Note the <code>$$variable</code> syntax for the loop variable &mdash; it&rsquo;s how aggregation expressions reference user-defined variables. Companion operators include <strong><code>$reduce</code></strong> (fold to a single value), <strong><code>$filter</code></strong> (subset), and <strong><code>$arrayElemAt</code></strong> (positional access).</p>
'''

ANSWERS[81] = r'''
<p>The <strong><code>$reduce</code></strong> aggregation operator <strong>folds an array into a single value</strong> by applying an expression repeatedly. It&rsquo;s like JavaScript&rsquo;s <code>Array.reduce()</code> &mdash; useful for sums, concatenations, or building aggregate state.</p>

<pre><code>// Sum an array of numbers (verbose, $sum is simpler &mdash; this is for illustration)
db.products.aggregate([
  { $project: {
      total: {
        $reduce: {
          input: "$prices",
          initialValue: 0,
          in: { $add: ["$$value", "$$this"] }
      }
    }
  }}
]);

// Concatenate strings with a separator
db.users.aggregate([
  { $project: {
      tags_csv: {
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
]);

// Count truthy elements
db.surveys.aggregate([
  { $project: {
      yes_count: {
        $reduce: {
          input: "$answers",
          initialValue: 0,
          in: { $add: ["$$value", { $cond: ["$$this", 1, 0] }] }
      }
    }
  }}
]);</code></pre>

<p>Variables: <code>$$value</code> is the running accumulator (starts as <code>initialValue</code>); <code>$$this</code> is the current array element. After the loop, the operator returns the final <code>$$value</code>. Most simple aggregations have built-in operators (<code>$sum</code>, <code>$avg</code>); <code>$reduce</code> shines when you need custom logic that none of those cover.</p>
'''

ANSWERS[82] = r'''
<p>The <strong><code>$filter</code></strong> aggregation operator <strong>returns a subset of an array</strong> &mdash; only the elements for which a condition is true. It&rsquo;s like JavaScript&rsquo;s <code>Array.filter()</code>.</p>

<pre><code>// Return only items priced &gt; 50
db.orders.aggregate([
  { $project: {
      expensive_items: {
        $filter: {
          input: "$items",
          as: "item",
          cond: { $gt: ["$$item.price", 50] }
      }
    }
  }}
]);

// Filter active sessions only
db.users.aggregate([
  { $project: {
      active_sessions: {
        $filter: {
          input: "$sessions",
          as: "s",
          cond: { $eq: ["$$s.expired", false] }
      }
    }
  }}
]);

// Combine with $size to count matches
db.products.aggregate([
  { $project: {
      reviews_count_5_star: {
        $size: {
          $filter: {
            input: "$reviews",
            as: "r",
            cond: { $eq: ["$$r.rating", 5] }
        }
      }
    }
  }}
]);

// MongoDB 5.0+: optional limit for early stop
db.products.aggregate([
  { $project: {
      first_three_in_stock: {
        $filter: {
          input: "$variants",
          as: "v",
          cond: { $gt: ["$$v.stock", 0] },
          limit: 3
      }
    }
  }}
]);</code></pre>

<p><code>$filter</code> + <code>$map</code> + <code>$reduce</code> is the Lisp-of-MongoDB &mdash; together they handle most array-transformation needs without unwinding (which can multiply documents and balloon memory). Prefer this trio over <code>$unwind + $group</code> when working with arrays inside a single document.</p>
'''

ANSWERS[83] = r'''
<p>The <strong><code>$arrayElemAt</code></strong> aggregation operator returns the <strong>element at a specific index</strong> in an array. Negative indices count from the end, just like Python.</p>

<pre><code>// Document: { _id: 1, scores: [80, 92, 75, 88, 95] }

// Get the first score
db.students.aggregate([
  { $project: { first: { $arrayElemAt: ["$scores", 0] } } }
]);

// Get the last score (negative index)
db.students.aggregate([
  { $project: { last: { $arrayElemAt: ["$scores", -1] } } }
]);

// Common pattern: get first element after sorting
db.users.aggregate([
  { $project: {
      newest_session: {
        $arrayElemAt: [
          { $sortArray: { input: "$sessions", sortBy: { ts: -1 } } },
          0
      ]
    }
  }}
]);

// Companion: $first and $last shorthands (MongoDB 4.4+)
db.students.aggregate([
  { $project: {
      first: { $first: "$scores" },     // same as $arrayElemAt: 0
      last:  { $last:  "$scores" }      // same as $arrayElemAt: -1
  }}
]);</code></pre>

<p>Watch for out-of-bounds indices: an index past the array length returns <code>null</code>, not an error. Guard with <code>$ifNull</code> if you need a default. For accessing the <em>nth from end</em> programmatically, use a negative index or compute it with <code>$subtract</code>.</p>
'''

ANSWERS[84] = r'''
<p>The <strong><code>$range</code></strong> aggregation operator generates an <strong>array of integers</strong> from a start value to (but not including) an end value, with an optional step. It&rsquo;s like Python&rsquo;s <code>range()</code>.</p>

<pre><code>// Generate [0, 1, 2, 3, 4]
db.dummy.aggregate([{ $project: { nums: { $range: [0, 5] } } }]);

// With a step: [0, 2, 4, 6, 8]
db.dummy.aggregate([{ $project: { nums: { $range: [0, 10, 2] } } }]);

// Reverse range: [10, 8, 6, 4, 2]
db.dummy.aggregate([{ $project: { nums: { $range: [10, 0, -2] } } }]);

// Practical use: enumerate documents 1..N for batch processing
db.dummy.aggregate([
  { $project: {
      pages: { $range: [1, { $add: [{ $size: "$items" }, 1] }] }
  }}
]);

// Combine with $map to generate per-element data
db.events.aggregate([
  { $project: {
      hours: {
        $map: {
          input: { $range: [0, 24] },
          as: "h",
          in: { hour: "$$h", count: 0 }
      }
    }
  }}
]);</code></pre>

<p>Common pairings: <code>$range</code> + <code>$map</code> for generating placeholder structures (e.g., 24 hour-buckets, 7 day-of-week slots, calendar grids). <code>$range</code> + <code>$reduce</code> for iterative computations. For dynamic-length sequences, compute the end value from a field with <code>$size</code> or arithmetic operators.</p>
'''

ANSWERS[85] = r'''
<p>The <strong><code>$zip</code></strong> aggregation operator <strong>combines multiple arrays element-wise</strong>, producing an array of tuples. The Nth element of each input becomes part of the Nth output tuple.</p>

<pre><code>// Pair products with their prices
db.dummy.aggregate([
  { $project: {
      pairs: {
        $zip: { inputs: [["pen", "book", "lamp"], [10, 50, 100]] }
      }
  }}
]);
// Output: [["pen", 10], ["book", 50], ["lamp", 100]]

// Zip three arrays
db.dummy.aggregate([
  { $project: {
      tuples: {
        $zip: {
          inputs: [["a", "b", "c"], [1, 2, 3], [true, false, true]]
      }
    }
  }}
]);

// Behavior with arrays of unequal length
// useLongestLength: true pads with defaults
db.dummy.aggregate([
  { $project: {
      pairs: {
        $zip: {
          inputs: [["a", "b", "c"], [1, 2]],
          useLongestLength: true,
          defaults: ["?", 0]
      }
    }
  }}
]);
// Output: [["a", 1], ["b", 2], ["c", 0]]</code></pre>

<p>Practical uses:</p>
<ul>
  <li><strong>Joining parallel arrays</strong> &mdash; common pattern when you store labels and values separately for column-oriented compactness.</li>
  <li><strong>Schema migrations</strong> &mdash; convert paired arrays into proper subdocuments using <code>$zip</code> + <code>$map</code>.</li>
</ul>

<p>Default behavior (no <code>useLongestLength</code>) truncates to the shortest array length &mdash; like Python&rsquo;s <code>zip()</code>. <code>$zip</code> is rarely needed in modern apps where data is usually structured as arrays of subdocuments instead.</p>
'''

ANSWERS[86] = r'''
<p>The <strong><code>$literal</code></strong> aggregation operator returns its argument <strong>without parsing it as an expression</strong>. It&rsquo;s the way to include a literal value (like a string starting with <code>$</code>) that would otherwise be interpreted as a field reference.</p>

<pre><code>// Without $literal, "$name" is treated as a field reference
db.users.aggregate([
  { $project: {
      label: "$name"               // returns the value of the name field
  }}
]);

// $literal forces the literal string
db.users.aggregate([
  { $project: {
      label: { $literal: "$name" }   // returns the literal string "$name"
  }}
]);

// Useful when the value happens to start with $
db.products.aggregate([
  { $project: {
      currency_marker: { $literal: "$ USD" }
  }}
]);

// Or when you need an array as data, not as an expression
db.things.aggregate([
  { $project: {
      tags: { $literal: ["$old", "$new"] }   // an array of two strings
  }}
]);

// Otherwise the array would be evaluated as { $old: "$new" }-like
// expressions and likely fail.</code></pre>

<p>Edge case: <code>$literal</code> is the escape hatch for &ldquo;I really mean this string, even though it looks like an expression.&rdquo; Most pipelines never need it &mdash; field references, numbers, and plain strings work as-is. Reach for it when handling user-provided strings that may begin with <code>$</code> or when constructing aggregation expressions programmatically.</p>
'''

ANSWERS[87] = r'''
<p>The <strong><code>$mergeObjects</code></strong> aggregation operator <strong>merges multiple documents</strong> into one, with later documents&rsquo; fields overwriting earlier ones. It&rsquo;s the spread-operator equivalent for documents.</p>

<pre><code>// Merge defaults with overrides
db.users.aggregate([
  { $project: {
      settings: {
        $mergeObjects: [
          { theme: "light", notifications: true, lang: "en" },   // defaults
          "$user_settings"                                          // overrides
        ]
      }
  }}
]);

// Merge data from multiple fields
db.profiles.aggregate([
  { $project: {
      combined: {
        $mergeObjects: ["$basic_info", "$contact_info", "$preferences"]
      }
  }}
]);

// Pattern: promote nested object + keep _id at the top level
db.users.aggregate([
  { $replaceRoot: {
      newRoot: { $mergeObjects: [{ _id: "$_id" }, "$profile"] }
  }}
]);

// Group accumulator: build per-user merged settings from multiple records
db.user_prefs.aggregate([
  { $group: {
      _id: "$user_id",
      merged: { $mergeObjects: "$settings" }
  }}
]);</code></pre>

<p>Behavior:</p>
<ul>
  <li><strong>Right-to-left precedence</strong> &mdash; later fields win when keys conflict.</li>
  <li><strong>Null and missing</strong> &mdash; treated as empty objects; safe to merge.</li>
  <li><strong>Shallow merge only</strong> &mdash; nested objects aren&rsquo;t recursively merged. For deep merging, write your own pipeline using <code>$objectToArray</code> + <code>$mergeObjects</code> recursively.</li>
</ul>

<p>Excellent for layering defaults, computed enrichments, or combining lookup results into a single shape.</p>
'''

ANSWERS[88] = r'''
<p>MongoDB doesn&rsquo;t have a <code>$mergeArrays</code> operator. The closest tool is <strong><code>$concatArrays</code></strong>, which <strong>concatenates two or more arrays</strong> into one. (You may have seen <code>$mergeArrays</code> referenced in some tutorials by mistake &mdash; the correct operator is <code>$concatArrays</code>.)</p>

<pre><code>// Concatenate arrays
db.users.aggregate([
  { $project: {
      all_tags: { $concatArrays: ["$personal_tags", "$work_tags", ["common"]] }
  }}
]);

// Document: { personal: ["a", "b"], work: ["c"] }
// Result:   all_tags: ["a", "b", "c", "common"]

// Combine with $setUnion to dedupe
db.users.aggregate([
  { $project: {
      unique_tags: { $setUnion: ["$personal_tags", "$work_tags"] }
  }}
]);

// Set operations on arrays
// $setUnion        - union (deduped)
// $setIntersection - elements in all input arrays
// $setDifference   - in first but not second
// $setEquals       - boolean, true if same elements</code></pre>

<table><thead><tr><th>Operator</th><th>Purpose</th></tr></thead><tbody>
<tr><td><code>$concatArrays</code></td><td>Concatenate, keeping duplicates and order</td></tr>
<tr><td><code>$setUnion</code></td><td>Union, deduplicated</td></tr>
<tr><td><code>$setIntersection</code></td><td>Common elements only</td></tr>
<tr><td><code>$setDifference</code></td><td>Difference (A &minus; B)</td></tr>
</tbody></table>

<p>Use <code>$concatArrays</code> when order matters and duplicates are expected. Use the set-family operators when arrays represent unordered sets and uniqueness matters.</p>
'''

ANSWERS[89] = r'''
<p>The <strong><code>$let</code></strong> aggregation operator <strong>defines local variables</strong> for use in a sub-expression. It&rsquo;s how you avoid repeating a complex computation or improve pipeline readability when intermediate values are needed.</p>

<pre><code>// Compute discounted total with named intermediates
db.orders.aggregate([
  { $project: {
      discounted_total: {
        $let: {
          vars: {
            subtotal: { $sum: "$line_items.price" },
            discount_rate: { $cond: ["$is_member", 0.1, 0.05] }
          },
          in: {
            $multiply: [
              "$$subtotal",
              { $subtract: [1, "$$discount_rate"] }
            ]
          }
        }
      }
  }}
]);

// Reuse a value computed once
db.products.aggregate([
  { $project: {
      summary: {
        $let: {
          vars: { tax: { $multiply: ["$price", 0.18] } },
          in: {
            price: "$price",
            tax: "$$tax",
            total: { $add: ["$price", "$$tax"] }
          }
        }
      }
  }}
]);</code></pre>

<p>Important details:</p>
<ul>
  <li><strong>Variables are referenced as <code>$$varName</code></strong> &mdash; the double-dollar denotes a user-defined variable.</li>
  <li><strong>Scope is the <code>in</code> expression only</strong> &mdash; variables don&rsquo;t leak to sibling stages.</li>
  <li><strong>System variables</strong> use the same syntax: <code>$$ROOT</code> (the current document), <code>$$NOW</code> (current time), <code>$$REMOVE</code> (drop a field).</li>
</ul>

<p><code>$let</code> is essential when a value would otherwise have to be recomputed three or four times in a single expression &mdash; both faster and more readable.</p>
'''

ANSWERS[90] = r'''
<p>A <strong>capped collection</strong> is a <strong>fixed-size, FIFO collection</strong> &mdash; once it reaches its size limit, the oldest documents are automatically overwritten. They&rsquo;re fast for high-volume writes and useful for circular buffers like recent logs, last-N events, or chat history.</p>

<pre><code>// Create a capped collection (10 MB max, optionally 10,000 doc limit)
db.createCollection("recent_logs", {
  capped: true,
  size: 10 * 1024 * 1024,         // 10 MB in bytes
  max: 10000                        // optional max doc count
});

// Convert an existing collection to capped (must use convertToCapped)
db.runCommand({ convertToCapped: "logs", size: 100*1024*1024 });

// Properties
// - documents are stored in insertion order (no _id sort needed)
// - inserts are very fast (no relocation, no fragmentation)
// - cannot delete or update in a way that grows the document
// - cannot shard a capped collection</code></pre>

<table><thead><tr><th>Property</th><th>Capped</th><th>Regular</th></tr></thead><tbody>
<tr><td>Insertion order</td><td>Guaranteed</td><td>Not guaranteed</td></tr>
<tr><td>Auto-eviction</td><td>Oldest documents</td><td>None &mdash; manual delete</td></tr>
<tr><td>Update grows doc?</td><td>Forbidden</td><td>Allowed</td></tr>
<tr><td>Sharding</td><td>Not supported</td><td>Yes</td></tr>
</tbody></table>

<p>Modern alternatives: for time-series data like IoT readings, MongoDB <strong>time-series collections</strong> (5.0+) are usually a better fit &mdash; auto-bucketed, compressed, and shardable. For ephemeral data like sessions, a <strong>TTL index</strong> on a regular collection is more flexible.</p>
'''

ANSWERS[91] = r'''
<p>The <strong><code>renameCollection</code></strong> command renames a collection within the same database (and optionally moves it across databases). It&rsquo;s useful for refactoring, atomic swaps during migrations, or aligning naming conventions.</p>

<pre><code>// Simple rename within the same database
db.users.renameCollection("members");

// Drop the target if it exists
db.users.renameCollection("members", true);   // dropTarget: true

// Move across databases (admin command)
db.adminCommand({
  renameCollection: "shopdb.users",
  to: "archivedb.users_2024"
});

// Common atomic-swap pattern for blue/green migrations
db.users.renameCollection("users_old", true);
db.users_new.renameCollection("users", true);
// Now "users" points to the new data; old data sits at "users_old"
// for safety. Drop later once confirmed.</code></pre>

<p>Important constraints:</p>
<ul>
  <li><strong>Within a database</strong> &mdash; fast, metadata-only operation.</li>
  <li><strong>Across databases</strong> &mdash; requires admin privileges and physically copies the data; not atomic.</li>
  <li><strong>Sharded collections</strong> &mdash; can&rsquo;t be renamed across databases; renames within the same DB are supported in modern versions.</li>
  <li><strong>Indexes are preserved</strong> &mdash; you don&rsquo;t need to recreate them.</li>
</ul>

<p>Use cases: blue/green migration cutover, normalizing names after acquisition or refactor, archiving (rename old to <code>orders_archive_2024</code> and create a fresh <code>orders</code>).</p>
'''

ANSWERS[92] = r'''
<p>The <strong><code>$expr</code></strong> operator allows <strong>aggregation expressions inside a query filter</strong>. It&rsquo;s how you compare two fields against each other or use complex computed conditions in <code>find()</code>, <code>updateMany()</code>, or pipeline <code>$match</code>.</p>

<pre><code>// Compare two fields in the same document
db.budgets.find({
  $expr: { $gt: ["$spent", "$allocated"] }
});

// Use an aggregation function in a query
db.orders.find({
  $expr: { $eq: [{ $year: "$created_at" }, 2026] }
});

// Conditional logic
db.products.find({
  $expr: {
    $cond: {
      if:   { $eq: ["$on_sale", true] },
      then: { $lt: ["$price", "$compare_price"] },
      else: true
    }
  }
});

// Inside a $lookup&rsquo;s pipeline (custom join condition)
db.orders.aggregate([
  { $lookup: {
      from: "customers",
      let: { custId: "$customer_id", region: "$region" },
      pipeline: [
        { $match: { $expr: { $and: [
          { $eq: ["$_id", "$$custId"] },
          { $eq: ["$region", "$$region"] }
        ]}}}
      ],
      as: "matched"
  }}
]);</code></pre>

<p>Performance notes:</p>
<ul>
  <li><strong><code>$expr</code> often can&rsquo;t use indexes</strong> for the comparison itself &mdash; it&rsquo;s computing values dynamically. Filter with regular operators first when possible.</li>
  <li><strong>Use sparingly in <code>find()</code></strong>; in aggregation pipelines it&rsquo;s the standard way to express complex conditions.</li>
</ul>

<p>Without <code>$expr</code>, regular query operators can&rsquo;t reference other fields &mdash; they only compare to literal values.</p>
'''

ANSWERS[93] = r'''
<p>You perform a case-insensitive search by using <strong>case-insensitive collation</strong> (best, fast) or a <strong>case-insensitive regex</strong> (flexible, slower). Each has trade-offs.</p>

<pre><code>// Case-insensitive regex (anchored regex still uses an index)
db.users.find({ name: { $regex: "^alice$", $options: "i" } });

// Better for equality: collation with strength: 2 (case-insensitive)
db.users.find({ name: "alice" }).collation({ locale: "en", strength: 2 });
// Matches Alice, ALICE, aLiCe

// Case-insensitive index (queries with matching collation use it)
db.users.createIndex(
  { name: 1 },
  { collation: { locale: "en", strength: 2 }, name: "name_ci" }
);

// Once that index exists, queries with the same collation are index-backed
db.users.find({ name: "alice" }).collation({ locale: "en", strength: 2 });

// Unicode-aware comparison (e.g., "café" matches "cafe")
db.users.find({ city: "munchen" }).collation({ locale: "de", strength: 1 });</code></pre>

<table><thead><tr><th>Approach</th><th>Speed</th><th>Best for</th></tr></thead><tbody>
<tr><td>Collation index</td><td>Fast (index-backed)</td><td>Equality and prefix searches</td></tr>
<tr><td>Anchored regex (<code>/^x/i</code>)</td><td>Index-backed in some cases</td><td>Prefix matches</td></tr>
<tr><td>Unanchored regex</td><td>Slow (collection scan)</td><td>Substring search at small scale</td></tr>
<tr><td>Atlas Search</td><td>Very fast at scale</td><td>Full-text, fuzzy, autocomplete</td></tr>
</tbody></table>

<p>For production user-facing search, <strong>MongoDB Atlas Search</strong> (Lucene-powered) is the right answer &mdash; it gives you fuzzy matching, ranking, autocomplete, and language-aware tokenization out of the box.</p>
'''

ANSWERS[94] = r'''
<p>The <strong><code>$out</code></strong> aggregation stage <strong>writes the pipeline result to a target collection</strong> (replacing it). It&rsquo;s how you export aggregation output as a new dataset for analytics or backups. (See also <code>$merge</code> for incremental writes.)</p>

<pre><code>// Export filtered users to another collection
db.users.aggregate([
  { $match: { country: "IN", active: true } },
  { $project: { name: 1, email: 1, signup_at: 1 } },
  { $out: "users_active_in_india" }
]);

// To another database
db.users.aggregate([
  // ... pipeline
  { $out: { db: "exports", coll: "snapshot_2026_04_28" } }
]);

// Export as JSON file via the CLI
mongoexport --uri="mongodb://localhost:27017/shopdb" \
  --collection=users_active_in_india \
  --out=users.json

// As CSV (specify fields)
mongoexport --uri="..." --collection=users_active_in_india \
  --type=csv --fields=name,email,signup_at \
  --out=users.csv</code></pre>

<p>Workflow tips:</p>
<ul>
  <li><strong><code>$out</code> replaces the entire target collection</strong>. For incremental updates, use <code>$merge</code> instead.</li>
  <li><strong>Use <code>mongoexport</code></strong> for getting data <em>out</em> of MongoDB into JSON/CSV files. Pair with <code>mongoimport</code> for the reverse.</li>
  <li><strong>For data warehouses</strong>, push to <strong>BigQuery</strong>, <strong>Snowflake</strong>, or <strong>Databricks</strong> via <strong>Airbyte</strong>, <strong>Fivetran</strong>, or the MongoDB Atlas Data Federation.</li>
  <li><strong>For backups</strong>, prefer <code>mongodump</code> &mdash; faster, schema-aware, and reusable with <code>mongorestore</code>.</li>
</ul>
'''

ANSWERS[95] = r'''
<p>The <strong><code>$bucket</code></strong> aggregation stage groups documents into <strong>predefined buckets based on a numeric field</strong>. Think of it as a histogram with custom bin boundaries. It&rsquo;s perfect for distributions like price ranges, age groups, or time slots.</p>

<pre><code>// Distribute users across age buckets
db.users.aggregate([
  { $bucket: {
      groupBy: "$age",
      boundaries: [0, 18, 30, 45, 60, 100],
      default: "Other",
      output: {
        count: { $sum: 1 },
        names: { $push: "$name" }
      }
  }}
]);

// Output:
// { _id: 0,   count: 5, names: [...] }     // ages 0-17
// { _id: 18,  count: 32, names: [...] }    // ages 18-29
// { _id: 30,  count: 47, names: [...] }    // ages 30-44
// { _id: 45,  count: 18, names: [...] }    // ages 45-59
// { _id: 60,  count: 8,  names: [...] }    // ages 60-99
// { _id: "Other", count: 2, names: [...] } // outside boundaries

// Price ranges
db.products.aggregate([
  { $bucket: {
      groupBy: "$price",
      boundaries: [0, 50, 100, 500, 1000, 5000],
      default: "5000+",
      output: { count: { $sum: 1 }, avg_rating: { $avg: "$rating" } }
  }}
]);</code></pre>

<p>Important details:</p>
<ul>
  <li><strong>Boundaries must be sorted ascending</strong> &mdash; each bucket covers <code>[lower, upper)</code>.</li>
  <li><strong><code>default</code> is required if values can fall outside boundaries</strong> &mdash; without it, those documents cause an error.</li>
  <li><strong>Pre-defined boundaries</strong> &mdash; if you don&rsquo;t know your data&rsquo;s range, use <strong><code>$bucketAuto</code></strong> instead, which picks boundaries for you.</li>
</ul>
'''

ANSWERS[96] = r'''
<p>The <strong><code>$bucketAuto</code></strong> aggregation stage groups documents into a specified <strong>number of equally-distributed buckets</strong> &mdash; you say how many buckets you want, MongoDB figures out the boundaries to balance them. It&rsquo;s the auto-histogram counterpart to <code>$bucket</code>.</p>

<pre><code>// 4 quartiles of users by age
db.users.aggregate([
  { $bucketAuto: {
      groupBy: "$age",
      buckets: 4,
      output: { count: { $sum: 1 } }
  }}
]);

// Output (boundaries chosen automatically):
// { _id: { min: 18, max: 28 }, count: 25 }
// { _id: { min: 28, max: 36 }, count: 25 }
// { _id: { min: 36, max: 50 }, count: 25 }
// { _id: { min: 50, max: 80 }, count: 25 }

// With granularity for round-number boundaries
db.products.aggregate([
  { $bucketAuto: {
      groupBy: "$price",
      buckets: 5,
      granularity: "R20",        // Renard series &mdash; nice round boundaries
      output: { count: { $sum: 1 }, avg_rating: { $avg: "$rating" } }
  }}
]);

// Granularities: "POWERSOF2", "1-2-5", "E6", "E12", "E24", "E48", "E96", "E192", "R5", "R10", "R20", "R40", "R80"</code></pre>

<table><thead><tr><th>Stage</th><th>You decide</th><th>MongoDB decides</th></tr></thead><tbody>
<tr><td><code>$bucket</code></td><td>Boundaries</td><td>Document distribution</td></tr>
<tr><td><code>$bucketAuto</code></td><td>Number of buckets</td><td>Boundaries (balanced)</td></tr>
</tbody></table>

<p>Use <code>$bucket</code> when you have known meaningful boundaries (e.g., age groups for marketing). Use <code>$bucketAuto</code> for ad-hoc analysis where balanced buckets matter more than specific cut points.</p>
'''

ANSWERS[97] = r'''
<p>The <strong><code>$facet</code></strong> aggregation stage runs <strong>multiple sub-pipelines in parallel</strong> on the same input documents, returning their results as named arrays in a single output document. It&rsquo;s the cleanest way to compute multiple summaries in one round trip.</p>

<pre><code>// Dashboard: get count, top categories, and price stats in one query
db.products.aggregate([
  { $match: { active: true } },
  { $facet: {
      total_count: [
        { $count: "count" }
      ],
      by_category: [
        { $group: { _id: "$category", count: { $sum: 1 } } },
        { $sort:  { count: -1 } },
        { $limit: 5 }
      ],
      price_stats: [
        { $group: {
            _id: null,
            avg: { $avg: "$price" },
            max: { $max: "$price" },
            min: { $min: "$price" }
        }}
      ]
  }}
]);

// Output:
// {
//   total_count: [{ count: 1500 }],
//   by_category:  [{ _id: "books", count: 320 }, ...],
//   price_stats:  [{ avg: 245.3, max: 1999, min: 5 }]
// }</code></pre>

<p>Real-world uses:</p>
<ul>
  <li><strong>Dashboards</strong> &mdash; one query for all charts on a page.</li>
  <li><strong>Faceted search</strong> &mdash; show product list + counts per category + price ranges in one shot (e.g., e-commerce filters).</li>
  <li><strong>Funnels</strong> &mdash; compute several conversion-rate metrics with different filter conditions.</li>
</ul>

<p>Performance: <code>$facet</code> processes the same input documents through each sub-pipeline. Place <code>$match</code> <em>before</em> <code>$facet</code> to filter once and let every facet share the reduced set. For very heavy faceting, consider <strong>Atlas Search</strong>&rsquo;s built-in facets, which are far faster.</p>
'''

ANSWERS[98] = r'''
<p>A <strong>hashed index</strong> stores the <strong>hash of a field&rsquo;s value</strong> instead of the value itself. It&rsquo;s primarily used as a <strong>shard key</strong> to distribute documents evenly across shards &mdash; especially when the original field is monotonically increasing (like timestamps or auto-incrementing IDs).</p>

<pre><code>// Create a hashed index
db.users.createIndex({ user_id: "hashed" });

// Use as a shard key for even distribution
sh.shardCollection("shopdb.events", { user_id: "hashed" });

// Compound hashed index (5.0+)
db.events.createIndex({ user_id: "hashed", created_at: 1 });</code></pre>

<table><thead><tr><th>Sharding strategy</th><th>Best for</th><th>Watch out for</th></tr></thead><tbody>
<tr><td>Range sharding (<code>{ field: 1 }</code>)</td><td>Range queries on the shard key</td><td>Hot shards if field is sequential</td></tr>
<tr><td>Hashed sharding (<code>{ field: "hashed" }</code>)</td><td>Even distribution under high write load</td><td>No range queries; all shards hit for ranges</td></tr>
<tr><td>Compound (5.0+)</td><td>Mix &mdash; even distribution + targeted reads</td><td>Slightly more complex query routing</td></tr>
</tbody></table>

<p>Trade-offs:</p>
<ul>
  <li><strong>Even write distribution</strong> &mdash; great for IoT, event streams, click logs.</li>
  <li><strong>Range queries scatter</strong> &mdash; <code>{ user_id: { $gt: X } }</code> hits every shard.</li>
  <li><strong>No sort by hashed field</strong> &mdash; the order is random.</li>
  <li><strong>Equality queries are still targeted</strong> &mdash; <code>{ user_id: 42 }</code> goes to one shard.</li>
</ul>

<p>For most modern apps, MongoDB Atlas&rsquo;s automatic shard-key suggestions are a good place to start.</p>
'''

ANSWERS[99] = r'''
<p>The <strong><code>mapReduce</code></strong> command runs a JavaScript map-reduce job over a collection &mdash; a custom function emits key-value pairs (map), and another reduces values per key. It&rsquo;s a legacy feature; modern MongoDB strongly prefers the <strong>aggregation framework</strong>, which is faster and more expressive.</p>

<pre><code>// Legacy mapReduce: total revenue per customer
db.orders.mapReduce(
  function() { emit(this.customer_id, this.amount); },     // map
  function(key, values) { return Array.sum(values); },     // reduce
  { out: "revenue_per_customer" }
);

// Same thing in aggregation (preferred &mdash; orders of magnitude faster)
db.orders.aggregate([
  { $group: { _id: "$customer_id", total: { $sum: "$amount" } } },
  { $out: "revenue_per_customer" }
]);

// Word count in mapReduce (a classic example)
db.posts.mapReduce(
  function() {
    this.content.split(/\s+/).forEach(w =&gt; emit(w.toLowerCase(), 1));
  },
  function(word, counts) { return Array.sum(counts); },
  { out: "word_counts" }
);</code></pre>

<p>Why aggregation is preferred today:</p>
<ul>
  <li><strong>10-100x faster</strong> &mdash; aggregation runs in C++; mapReduce runs JavaScript per document.</li>
  <li><strong>Index-aware</strong> &mdash; pipelines use indexes; mapReduce typically scans.</li>
  <li><strong>Pipeline operators are richer</strong> &mdash; <code>$lookup</code>, <code>$facet</code>, <code>$bucket</code>, <code>$graphLookup</code> have no mapReduce equivalent.</li>
  <li><strong>Better tooling</strong> &mdash; <code>explain()</code>, profiling, and Atlas insights focus on aggregation.</li>
</ul>

<p>MongoDB has officially deprecated <code>mapReduce</code> in favor of aggregation. Migrate any existing jobs &mdash; the rewrite is usually clearer too.</p>
'''

ANSWERS[100] = r'''
<p>MongoDB <strong>transactions</strong> let you execute <strong>multiple operations atomically</strong> &mdash; either all of them commit or all are rolled back. Available since v4.0 (replica sets) and v4.2 (sharded clusters), they bring familiar ACID semantics for cases that genuinely need cross-document consistency.</p>

<pre><code>// Node.js driver: atomic transfer between two accounts
const session = client.startSession();
try {
  await session.withTransaction(async () =&gt; {
    const accounts = client.db("bank").collection("accounts");
    await accounts.updateOne(
      { _id: fromId },
      { $inc: { balance: -100 } },
      { session }
    );
    await accounts.updateOne(
      { _id: toId },
      { $inc: { balance:  100 } },
      { session }
    );
  });
} finally {
  await session.endSession();
}

// Mongo shell
session = db.getMongo().startSession();
session.startTransaction();
try {
  session.getDatabase("bank").accounts.updateOne({ _id: 1 }, { $inc: { balance: -100 } });
  session.getDatabase("bank").accounts.updateOne({ _id: 2 }, { $inc: { balance:  100 } });
  session.commitTransaction();
} catch (err) {
  session.abortTransaction();
}</code></pre>

<p>Key details:</p>
<ul>
  <li><strong>Default time limit: 60 seconds</strong>. Long transactions abort automatically.</li>
  <li><strong>Must be on a replica set or sharded cluster</strong> &mdash; not on standalone <code>mongod</code>.</li>
  <li><strong>Use sparingly</strong> &mdash; transactions reduce throughput. Document-level atomicity (a single <code>updateOne</code>) is usually enough.</li>
  <li><strong><code>withTransaction()</code></strong> in modern drivers handles retries on transient errors automatically &mdash; the recommended way.</li>
  <li><strong>Avoid for high-write paths</strong> &mdash; for counters, queues, and event streams, prefer document-level operations.</li>
</ul>

<p>Modern alternatives for distributed consistency: the <strong>outbox pattern</strong> with CDC (Debezium), event-sourcing, or sagas for cross-service workflows.</p>
'''
