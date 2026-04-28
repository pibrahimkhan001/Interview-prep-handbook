"""MySQL Advanced — 100 detailed answers."""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>InnoDB</strong> is the default and the right choice for essentially all modern workloads. <strong>MyISAM</strong> is a legacy engine that survives mainly in old codebases &mdash; new tables should never use it.</p>

<table>
  <tr><th>Aspect</th><th>InnoDB</th><th>MyISAM</th></tr>
  <tr><td>Transactions</td><td>Full ACID with redo + undo logs</td><td>None &mdash; no COMMIT/ROLLBACK</td></tr>
  <tr><td>Locking</td><td>Row-level via record + gap locks</td><td>Table-level only</td></tr>
  <tr><td>Crash recovery</td><td>Automatic via redo log replay</td><td>Manual <code>REPAIR TABLE</code>; data loss possible</td></tr>
  <tr><td>Foreign keys</td><td>Enforced</td><td>Parsed and silently ignored</td></tr>
  <tr><td>Index structure</td><td>Clustered: PK <em>is</em> the row; secondary indexes hold PK</td><td>Heap-organized; all indexes hold row pointers</td></tr>
  <tr><td>Buffer pool</td><td>Caches data and indexes</td><td>Caches indexes only; data via OS file cache</td></tr>
  <tr><td>MVCC</td><td>Yes &mdash; readers don&rsquo;t block writers</td><td>No &mdash; readers block writers</td></tr>
</table>

<p><strong>Why InnoDB wins for production</strong>: row-level locking allows real concurrent writes; MVCC lets long reports run without freezing inserts; the redo log makes crashes recoverable in seconds rather than hours of <code>REPAIR</code>. The clustered-index design also makes PK lookups one I/O instead of two.</p>

<p>MyISAM&rsquo;s historical advantages (slightly faster <code>COUNT(*)</code>, smaller files, full-text search) are gone &mdash; InnoDB caches counts well, supports FULLTEXT since 5.6, and modern SSDs erase the storage gap. Convert any remaining MyISAM tables with <code>ALTER TABLE ... ENGINE=InnoDB</code>.</p>
'''

ANSWERS[2] = r'''
<p>Optimization is iterative measurement, not guesswork. Start by reproducing the slow query in a representative environment, then run <code>EXPLAIN ANALYZE</code> &mdash; this returns the actual execution plan with row counts and timing per step, exposing where time goes.</p>

<p><strong>The systematic levers</strong>:</p>
<ul>
  <li><strong>Indexes</strong> covering the <code>WHERE</code>, <code>JOIN</code>, and <code>ORDER BY</code> columns, in that priority order. A composite index on <code>(filter_col, sort_col)</code> often eliminates both a scan and a sort.</li>
  <li><strong>Avoid index-killing patterns</strong> &mdash; <code>WHERE YEAR(date_col) = 2026</code>, <code>WHERE col + 0 = 5</code>, <code>WHERE LOWER(name) = 'alice'</code>. Move functions to the constant side or use generated columns.</li>
  <li><strong>Reduce returned columns</strong> &mdash; <code>SELECT *</code> forces row lookups; explicit columns may be served from a covering index alone.</li>
  <li><strong>Rewrite correlated subqueries as joins</strong> when the optimizer doesn&rsquo;t do it itself; <code>EXISTS</code> often beats <code>IN (subquery)</code>.</li>
  <li><strong>Pagination</strong>: replace <code>LIMIT 10 OFFSET 10000</code> with keyset pagination using a <code>(sort_key, id) &lt; (?, ?)</code> predicate.</li>
</ul>

<p><strong>Beyond query rewriting</strong>: tune <code>innodb_buffer_pool_size</code> to fit hot data in memory (50-70% of RAM on dedicated servers), <code>ANALYZE TABLE</code> after large data shifts so the optimizer has fresh statistics, partition very large tables by date, and offload long reads to a replica. <strong>pt-query-digest</strong> on the slow log surfaces the queries actually worth your time &mdash; optimizing rare queries is wasted effort.</p>
'''

ANSWERS[3] = r'''
<p>A <strong>query execution plan</strong> is the optimizer&rsquo;s chosen strategy for resolving a query: which index to use, the join order, the access method (range vs ref vs ALL), whether sorting or temp tables are needed. MySQL exposes it via <code>EXPLAIN</code>, with the more detailed <code>EXPLAIN ANALYZE</code> running the query and reporting actual timings.</p>

<p><strong>Reading EXPLAIN output</strong> &mdash; the columns that matter most:</p>

<table>
  <tr><th>Column</th><th>What to look at</th></tr>
  <tr><td><code>type</code></td><td><code>const</code>, <code>eq_ref</code>, <code>ref</code> are great. <code>range</code> is fine. <code>index</code> is a full index scan. <code>ALL</code> is a table scan &mdash; usually a problem.</td></tr>
  <tr><td><code>key</code></td><td>The chosen index. NULL means none used.</td></tr>
  <tr><td><code>rows</code></td><td>Estimated rows examined. The optimizer minimizes the product across joined tables.</td></tr>
  <tr><td><code>filtered</code></td><td>Estimated % of <code>rows</code> that match the <code>WHERE</code>. Low values mean the predicate isn&rsquo;t indexable.</td></tr>
  <tr><td><code>Extra</code></td><td><code>Using filesort</code>, <code>Using temporary</code>, <code>Using where</code>; these are diagnostic flags.</td></tr>
</table>

<p><strong>EXPLAIN ANALYZE</strong> (8.0.18+) gives ground truth: actual rows, actual time per operator, loops. Use it whenever the estimate-based <code>EXPLAIN</code> looks fine but the query is still slow &mdash; statistics drift causes the planner to under-estimate. <strong>EXPLAIN FORMAT=JSON</strong> exposes the optimizer&rsquo;s cost model so you can see why one plan was chosen over another.</p>

<p><strong>Tools for visualization</strong>: MySQL Workbench&rsquo;s visual explain, the <strong>EVERSQL</strong> or <strong>pt-visual-explain</strong> tools render the plan as a tree, making nested loops and join order easier to reason about.</p>
'''

ANSWERS[4] = r'''
<p><code>EXPLAIN</code> tells you how the optimizer plans to execute a query &mdash; without actually running it. It&rsquo;s the diagnostic starting point for any optimization work because every other decision (which index to add, whether to rewrite the query) depends on understanding the plan.</p>

<pre><code>EXPLAIN SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.country = 'IN'
GROUP BY u.id;</code></pre>

<p><strong>Three EXPLAIN flavors in MySQL 8</strong>:</p>

<table>
  <tr><th>Form</th><th>Use</th></tr>
  <tr><td><code>EXPLAIN ...</code></td><td>Tabular plan, estimates only. Cheap.</td></tr>
  <tr><td><code>EXPLAIN FORMAT=JSON ...</code></td><td>Detailed cost-model output. Shows why plans were rejected.</td></tr>
  <tr><td><code>EXPLAIN ANALYZE ...</code></td><td>Runs the query, reports actual rows and times per operator. Most useful but executes side effects on writes.</td></tr>
</table>

<p><strong>Interpreting key signals</strong>:</p>
<ul>
  <li><code>type: ALL</code> on a large table = full table scan; missing or unusable index.</li>
  <li><code>Using filesort</code> = no index supports the <code>ORDER BY</code>; in-memory or on-disk sort.</li>
  <li><code>Using temporary</code> = optimizer materializes intermediate results; common for <code>GROUP BY</code> without a covering index.</li>
  <li><code>filtered: 5%</code> on millions of rows = the index doesn&rsquo;t narrow well; a more selective index may help.</li>
</ul>

<p>Run <code>EXPLAIN</code> first, identify the worst access type or biggest <code>rows</code> estimate, fix that one thing, re-run. Single-step iterative optimization beats trying to fix everything at once.</p>
'''

ANSWERS[5] = r'''
<p>Indexes are sorted lookup structures that let MySQL find rows without scanning the whole table. The default and dominant type is the <strong>B+tree</strong>, which provides O(log n) lookups, range scans, and ordered traversal.</p>

<p><strong>What a good index looks like</strong>:</p>

<ul>
  <li><strong>Selective</strong> &mdash; the indexed column distinguishes rows well. An index on <code>gender</code> (two values) helps almost nothing; one on <code>email</code> helps a lot.</li>
  <li><strong>Aligned with the WHERE</strong> &mdash; column order in a composite index must follow the leftmost-prefix rule: an index <code>(a, b, c)</code> serves queries on <code>(a)</code>, <code>(a, b)</code>, <code>(a, b, c)</code> but not <code>(b)</code> alone.</li>
  <li><strong>Covering</strong> when possible &mdash; if every column in <code>SELECT</code> is in the index, MySQL never reads the row data. Append the displayed columns to the index for read-heavy queries.</li>
  <li><strong>Index-friendly predicates</strong> &mdash; <code>WHERE date_col &gt;= '2026-01-01'</code> uses an index; <code>WHERE YEAR(date_col) = 2026</code> defeats it. Avoid wrapping indexed columns in functions.</li>
</ul>

<p><strong>Specialized index types</strong>:</p>

<table>
  <tr><th>Type</th><th>For</th></tr>
  <tr><td>B+tree (default)</td><td>Equality, range, sort</td></tr>
  <tr><td>Hash (MEMORY engine only)</td><td>Equality only, no ranges</td></tr>
  <tr><td>FULLTEXT</td><td>Text-search via tokenization</td></tr>
  <tr><td>Spatial (R-tree)</td><td>GEOMETRY columns &mdash; bounding-box queries</td></tr>
  <tr><td>Functional (8.0.13+)</td><td><code>INDEX ((LOWER(email)))</code> &mdash; index over an expression</td></tr>
</table>

<p><strong>Cost</strong>: every index slows writes (each INSERT/UPDATE/DELETE updates every index) and consumes disk plus memory. Add indexes deliberately, drop unused ones (<code>sys.schema_unused_indexes</code>), and let <code>EXPLAIN</code> verify they&rsquo;re actually picked.</p>
'''

ANSWERS[6] = r'''
<p>FULLTEXT indexes tokenize text columns into words and build an inverted word→document index, enabling natural-language and Boolean searches that B+tree indexes can&rsquo;t support. InnoDB has supported FULLTEXT since MySQL 5.6.</p>

<pre><code>ALTER TABLE articles
ADD FULLTEXT INDEX ft_body (title, body);

SELECT id, title,
       MATCH(title, body) AGAINST('+wireless +headphones -wired' IN BOOLEAN MODE) AS score
FROM articles
WHERE MATCH(title, body) AGAINST('+wireless +headphones -wired' IN BOOLEAN MODE)
ORDER BY score DESC LIMIT 20;</code></pre>

<p><strong>Search modes</strong>:</p>

<table>
  <tr><th>Mode</th><th>Behavior</th></tr>
  <tr><td>NATURAL LANGUAGE (default)</td><td>Relevance-ranked match; multi-word query treated as a phrase scoring</td></tr>
  <tr><td>BOOLEAN</td><td>Operators: <code>+required -excluded *prefix "exact phrase"</code></td></tr>
  <tr><td>WITH QUERY EXPANSION</td><td>Two-pass &mdash; second pass finds documents related to top initial matches</td></tr>
</table>

<p><strong>Configuration knobs that matter</strong>:</p>
<ul>
  <li><code>innodb_ft_min_token_size</code> (default 3) &mdash; words shorter than this are excluded. Lower it to index "AI" or "Go".</li>
  <li><code>innodb_ft_user_stopword_table</code> &mdash; replace the default stopword list ("the", "a", "and", ...) with a custom one.</li>
  <li>The <strong>50% threshold</strong> in NATURAL LANGUAGE MODE: words appearing in over half the rows score zero. Switch to BOOLEAN MODE on small datasets where common words must still match.</li>
  <li><code>WITH PARSER ngram</code> for CJK languages where whitespace tokenization fails.</li>
</ul>

<p><strong>When to step outside MySQL</strong>: at tens of millions of rows or when you need stemming, synonyms, fuzzy matching, faceted aggregation, or cross-language analyzers, move to a dedicated search engine &mdash; <strong>Elasticsearch</strong>, <strong>OpenSearch</strong>, <strong>Meilisearch</strong>, or <strong>Typesense</strong>. MySQL FULLTEXT covers internal CMS-scale content but stops being a winning answer at search-product scale.</p>
'''

ANSWERS[7] = r'''
<p>Partitioning splits a single logical table into multiple physical files based on a partitioning key. Queries that filter by the key only read relevant partitions (<em>partition pruning</em>); maintenance operations can target individual partitions without scanning the whole table.</p>

<pre><code>CREATE TABLE events (
  id BIGINT, user_id INT, created_at DATETIME, payload JSON,
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (YEAR(created_at)) (
  PARTITION p2024 VALUES LESS THAN (2025),
  PARTITION p2025 VALUES LESS THAN (2026),
  PARTITION p2026 VALUES LESS THAN (2027),
  PARTITION pmax  VALUES LESS THAN MAXVALUE
);</code></pre>

<p><strong>Partition strategies</strong>:</p>

<table>
  <tr><th>Type</th><th>Use case</th></tr>
  <tr><td><code>RANGE</code> / <code>RANGE COLUMNS</code></td><td>Time-series, ordered data &mdash; natural for date partitioning</td></tr>
  <tr><td><code>LIST</code> / <code>LIST COLUMNS</code></td><td>Discrete categories &mdash; region, tenant_id</td></tr>
  <tr><td><code>HASH</code> / <code>KEY</code></td><td>Spread load evenly when no natural range exists</td></tr>
</table>

<p><strong>Operational benefits</strong>: <code>ALTER TABLE events DROP PARTITION p2023</code> deletes a year of data in milliseconds &mdash; instant data retention enforcement. <code>ALTER TABLE events EXCHANGE PARTITION</code> atomically swaps a partition with a separate table for archival. Local indexes per partition mean rebuilding one partition&rsquo;s indexes doesn&rsquo;t touch others.</p>

<p><strong>Important constraints</strong>: every unique key (including the PK) must include the partitioning column. Foreign keys are not supported on partitioned tables. Partition pruning only kicks in when queries filter on the partition key directly &mdash; <code>WHERE YEAR(created_at) = 2026</code> defeats it; <code>WHERE created_at &gt;= '2026-01-01'</code> works.</p>

<p><strong>When it pays off</strong>: very large time-series tables (logs, events, telemetry) with predictable retention, where 90% of queries hit recent data and old data is dropped wholesale. For mid-sized OLTP tables, the operational complexity rarely beats good indexes plus periodic archive scripts.</p>
'''

ANSWERS[8] = r'''
<p>Both terms describe how to split a large table, but along different axes:</p>

<table>
  <tr><th>Aspect</th><th>Horizontal partitioning</th><th>Vertical partitioning</th></tr>
  <tr><td>Splits by</td><td>Rows</td><td>Columns</td></tr>
  <tr><td>Goal</td><td>Reduce rows per partition</td><td>Reduce row width</td></tr>
  <tr><td>Native MySQL feature</td><td>Yes &mdash; <code>PARTITION BY</code></td><td>No &mdash; achieved via separate tables</td></tr>
  <tr><td>Joins required</td><td>No (same table)</td><td>Yes (across tables)</td></tr>
</table>

<p><strong>Horizontal example</strong> &mdash; events split by date so each partition stays small:</p>

<pre><code>events
├── p2024  (Jan-Dec 2024 rows)
├── p2025  (Jan-Dec 2025 rows)
└── p2026  (Jan-Dec 2026 rows)</code></pre>

<p>Same columns in every partition; the row split is invisible to most queries.</p>

<p><strong>Vertical example</strong> &mdash; split a wide <code>users</code> table into hot (small, frequently read) and cold columns:</p>

<pre><code>users           users_profile
+----+-------+    +----+----------+----------+----------+
| id | name  |    | id | bio_text | avatar   | settings |
+----+-------+    +----+----------+----------+----------+
| 1  | Alice |    | 1  | "..."    | url://.. | { ... }  |
+----+-------+    +----+----------+----------+----------+</code></pre>

<p>Hot path queries (<code>SELECT name FROM users WHERE id = 5</code>) read fewer bytes per row, get more rows per page, and stay in the buffer pool longer. Joins to <code>users_profile</code> happen only when the rare columns are needed.</p>

<p><strong>Sharding</strong> is horizontal partitioning across multiple servers &mdash; rows of a logical "users" table are distributed across N database instances by a shard key. Adds operational complexity and constraints (no cross-shard joins) but is the path to scaling beyond one machine. <strong>Vitess</strong>, <strong>PlanetScale</strong>, and <strong>TiDB</strong> implement this transparently for MySQL-compatible workloads.</p>

<p>In practice: vertical splits live with you forever (just denormalization with extra steps); horizontal partitioning earns its place once a table outgrows what indexes alone can keep fast.</p>
'''

ANSWERS[9] = r'''
<p>MySQL&rsquo;s memory hierarchy splits between <em>global</em> buffers (shared across all sessions) and <em>per-thread</em> buffers (allocated per connection). The biggest by far is the InnoDB buffer pool.</p>

<p><strong>Key memory settings</strong>:</p>

<table>
  <tr><th>Variable</th><th>Purpose</th><th>Typical value</th></tr>
  <tr><td><code>innodb_buffer_pool_size</code></td><td>Caches data + indexes</td><td>50-70% of RAM on dedicated servers</td></tr>
  <tr><td><code>innodb_log_buffer_size</code></td><td>Buffers redo log writes</td><td>16-64 MB</td></tr>
  <tr><td><code>tmp_table_size</code> / <code>max_heap_table_size</code></td><td>In-memory tmp tables before disk spill</td><td>16-64 MB; raise if you see <code>Created_tmp_disk_tables</code> growing</td></tr>
  <tr><td><code>sort_buffer_size</code></td><td>Per-thread sort workspace</td><td>2-4 MB; multiplied by connection count</td></tr>
  <tr><td><code>join_buffer_size</code></td><td>Per-thread, per-join scratch</td><td>2-4 MB; large values × many joins blow up RAM</td></tr>
</table>

<p><strong>The buffer pool is the single biggest knob</strong> &mdash; the goal is for the working set (frequently-accessed pages) to live in RAM. Diagnose hit ratio with:</p>

<pre><code>SELECT
  100 * (1 - innodb_buffer_pool_reads / innodb_buffer_pool_read_requests) AS hit_pct
FROM (SELECT
  (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') AS innodb_buffer_pool_reads,
  (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests') AS innodb_buffer_pool_read_requests
) t;</code></pre>

<p>Hit ratio above 99% is healthy for OLTP; falling below 95% means hot data doesn&rsquo;t fit in memory.</p>

<p><strong>Per-thread caution</strong>: <code>max_connections × (sort_buffer + join_buffer + read_buffer)</code> can dwarf the buffer pool if you over-tune the per-thread values. <strong>ProxySQL</strong> or <strong>connection pools</strong> at the application layer (HikariCP for JVM, mysql2&rsquo;s pool for Node.js) keep <code>max_connections</code> manageable. Watch for OOM-killer activity: <code>journalctl -u mysql</code> showing <code>oom-kill</code> means the math has overflowed.</p>
'''

ANSWERS[10] = r'''
<p>The <strong>query cache stored full result sets keyed by exact query text</strong>, returning cached results without re-executing. <strong>It was deprecated in MySQL 5.7 and removed entirely in MySQL 8.0</strong> &mdash; if you&rsquo;re on a current MySQL, the cache no longer exists and there&rsquo;s nothing to manage.</p>

<p><strong>Why it was removed</strong>:</p>
<ul>
  <li><strong>Mutex contention</strong> &mdash; the cache used a single global mutex; on multi-core servers it became a serialization bottleneck under concurrent load.</li>
  <li><strong>Invalidation overhead</strong> &mdash; any write to a table invalidated every cached query touching that table. Write-heavy workloads spent more time invalidating than the cache saved.</li>
  <li><strong>Strict matching</strong> &mdash; queries had to match byte-for-byte. Different whitespace, comment, or capitalization missed the cache. Most ORM-generated queries never matched twice.</li>
  <li><strong>Better alternatives</strong> &mdash; the InnoDB buffer pool already caches the underlying pages, so re-running a query reads from RAM. Application-level caches (Redis, Memcached) do per-result caching with proper invalidation strategies.</li>
</ul>

<p><strong>For MySQL 5.7 and earlier</strong>, the relevant variables were <code>query_cache_type</code> (ON/OFF/DEMAND), <code>query_cache_size</code>, and <code>query_cache_limit</code>. Most operators set <code>query_cache_type = 0</code> long before 8.0 because the contention outweighed the wins on production workloads.</p>

<p><strong>Modern caching strategy</strong>:</p>
<ul>
  <li>Buffer pool sized so hot data stays resident (Q9).</li>
  <li><strong>Application-level caching</strong> &mdash; Redis or Memcached for materialized API responses, user sessions, computed aggregates. Cache key encodes input parameters; TTL or explicit invalidation on writes.</li>
  <li><strong>Read replicas</strong> for heavy SELECT workloads &mdash; offload reporting from the primary.</li>
  <li><strong>Materialized aggregates</strong> in summary tables, refreshed by triggers or scheduled jobs.</li>
</ul>

<p>The "MySQL query cache" answer is now historical context. For new deployments, ignore it.</p>
'''

ANSWERS[11] = r'''
<p>"Large" usually means the working set no longer fits in memory or maintenance operations (DDL, backups, deletes) take hours. The solutions divide between making the existing schema more efficient and structurally changing how data is stored.</p>

<p><strong>Within the existing schema</strong>:</p>
<ul>
  <li><strong>Right-size data types</strong> &mdash; <code>BIGINT</code> when <code>INT</code> suffices wastes 4 bytes per row times every index. <code>VARCHAR(255)</code> for a 20-char value still works, but smaller types pack more rows per page, raising buffer pool efficiency.</li>
  <li><strong>Drop unused indexes</strong> &mdash; check <code>sys.schema_unused_indexes</code>; every index slows writes and consumes RAM.</li>
  <li><strong>Online schema changes</strong> &mdash; <strong>pt-online-schema-change</strong> (Percona) and <strong>gh-ost</strong> (GitHub) rebuild tables in the background and atomically swap, avoiding hours of locked DDL.</li>
  <li><strong>Batched writes</strong> &mdash; deletes and updates of millions of rows should run in chunks of a few thousand with <code>LIMIT</code>, committing each batch to avoid long undo logs.</li>
</ul>

<p><strong>Structural changes</strong>:</p>
<ul>
  <li><strong>Partitioning</strong> by date for time-series tables &mdash; old partitions can be dropped instantly, queries prune to recent data.</li>
  <li><strong>Archival</strong> &mdash; move old rows to a separate cold table, S3 + Parquet, or a warehouse like ClickHouse / BigQuery for analytics.</li>
  <li><strong>Read replicas</strong> &mdash; scale reads horizontally; offload reporting and search from the primary.</li>
  <li><strong>Sharding</strong> &mdash; only when one server&rsquo;s I/O genuinely can&rsquo;t serve writes. Tools: <strong>Vitess</strong>, <strong>PlanetScale</strong>, <strong>TiDB</strong>.</li>
</ul>

<p><strong>Backups deserve special attention</strong>: <code>mysqldump</code> on multi-TB databases takes too long. Switch to <strong>Percona XtraBackup</strong> for physical backups (snapshot speed, parallelizable), or use cloud-provider snapshots (AWS RDS, Aurora, Cloud SQL) which are storage-level and near-instant. Always test restore times &mdash; a 4-hour backup window means a 4-hour outage when you need to recover.</p>
'''

ANSWERS[12] = r'''
<p>A <strong>covering index</strong> is one that contains every column the query needs, so MySQL can answer the query from the index alone without reading the row data &mdash; eliminating one I/O per row. <code>EXPLAIN</code> shows <code>Extra: Using index</code> when this happens.</p>

<pre><code>-- Schema
CREATE TABLE orders (
  id           INT PRIMARY KEY,
  user_id      INT,
  status       VARCHAR(20),
  total        DECIMAL(10,2),
  created_at   DATETIME,
  shipping_addr TEXT,
  notes        TEXT,
  INDEX idx_user_status (user_id, status, created_at, total)
);

-- Covered: every selected column is in the index
SELECT created_at, total
FROM orders
WHERE user_id = 5 AND status = 'completed';
-- EXPLAIN shows: Using where; Using index → no row fetch needed</code></pre>

<p>The same index is used but <em>not</em> as a cover here:</p>

<pre><code>SELECT created_at, total, shipping_addr   -- shipping_addr not in index
FROM orders WHERE user_id = 5 AND status = 'completed';
-- MySQL uses the index to find rows but must look up the row data for shipping_addr</code></pre>

<p><strong>Why it matters</strong>: in InnoDB, secondary indexes store the leaf-level row pointers as the primary key. A non-covering query does an index seek, then a separate primary-key lookup per row &mdash; doubling the I/O. For a query returning 10K rows, that&rsquo;s 10K extra random reads. Covering indexes turn this into a single ordered range scan over the index leaves.</p>

<p><strong>Designing covering indexes</strong>: include filter columns first (in selectivity order), then sort columns, then the small projection columns the query reads. Don&rsquo;t cover huge TEXT/BLOB columns &mdash; the index bloats. Two indexes specialized for two queries usually beat one wide index trying to cover both.</p>

<p><strong>Limit</strong>: every additional column slows writes (each insert updates the index) and increases RAM usage. Cover specifically the queries that are hot &mdash; not every query.</p>
'''

ANSWERS[13] = r'''
<p>A <strong>deadlock</strong> occurs when two transactions hold locks the other needs, forming a cycle neither can break. InnoDB detects deadlock cycles via a wait-for graph and aborts the cheaper transaction (the one with fewer rows modified) with error <code>1213 (40001)</code>; the other proceeds.</p>

<p><strong>Inspect the most recent deadlock</strong>:</p>

<pre><code>SHOW ENGINE INNODB STATUS\G
-- Look for the LATEST DETECTED DEADLOCK section:
-- shows both transactions, their queries, and the locks involved.

-- For systematic logging, enable:
SET GLOBAL innodb_print_all_deadlocks = ON;
-- Each deadlock now logs to the error log.</code></pre>

<p><strong>Common causes</strong>:</p>
<ul>
  <li><strong>Inconsistent lock ordering</strong> &mdash; transaction A updates row 1 then 2; transaction B updates row 2 then 1. Acquiring locks in a fixed global order eliminates this class.</li>
  <li><strong>Gap and next-key locks</strong> at <code>REPEATABLE READ</code> &mdash; range queries lock not just matching rows but gaps between them, increasing collision surface.</li>
  <li><strong>Foreign key cascades</strong> on heavily-updated parent tables &mdash; the child row locks ripple unpredictably.</li>
  <li><strong>Long transactions</strong> &mdash; the longer locks are held, the more chance of conflict.</li>
</ul>

<p><strong>Fixes, in order of preference</strong>:</p>
<ol>
  <li><strong>Always retry</strong> on error 1213 &mdash; deadlocks are normal and the application must handle them with bounded retries (typically 3 attempts with backoff). Treat them like any transient error, not a bug.</li>
  <li><strong>Order writes consistently</strong> &mdash; sort updates by primary key before issuing them.</li>
  <li><strong>Shorten transactions</strong> &mdash; commit small units; never wait for I/O or user input mid-transaction.</li>
  <li><strong>Reduce isolation</strong> &mdash; <code>READ COMMITTED</code> avoids most gap locks if the application can tolerate non-repeatable reads.</li>
  <li><strong>Add indexes</strong> &mdash; predicates that scan instead of seek lock more rows than needed.</li>
</ol>

<p><strong>Don&rsquo;t treat deadlocks as catastrophic</strong>. A few per hour on a busy OLTP system is normal. Spikes (hundreds per minute) point to a hot row or unordered write pattern worth investigating.</p>
'''

ANSWERS[14] = r'''
<p>A <strong>temporary table</strong> exists only for the duration of the connection that created it and is invisible to other sessions. MySQL automatically drops it when the connection closes. Useful for staging data during multi-step computations, breaking complex queries into simpler stages, and avoiding repeated subquery evaluation.</p>

<pre><code>CREATE TEMPORARY TABLE recent_high_value AS
SELECT customer_id, SUM(total) AS spend
FROM orders
WHERE created_at &gt;= CURDATE() - INTERVAL 90 DAY
GROUP BY customer_id
HAVING spend &gt; 10000;

-- Now use it in subsequent queries within the same connection:
SELECT c.id, c.name, r.spend
FROM customers c JOIN recent_high_value r ON r.customer_id = c.id
WHERE c.country = 'IN';</code></pre>

<p><strong>Storage</strong>: small temp tables stay in memory (engine controlled by <code>internal_tmp_mem_storage_engine</code>, defaults to <code>TempTable</code> in MySQL 8); when they exceed <code>tmp_table_size</code>, they spill to disk using <code>internal_tmp_disk_storage_engine</code> (InnoDB by default). Watch <code>Created_tmp_disk_tables</code> &mdash; high values indicate the in-memory limit needs raising or the query needs rewriting.</p>

<p><strong>Two MySQL-specific gotchas</strong>:</p>
<ul>
  <li>A temporary table can&rsquo;t be referenced twice in the same query &mdash; <code>SELECT ... FROM tmp t1 JOIN tmp t2 ...</code> errors with <em>Can&rsquo;t reopen table</em>. Workaround: copy to a second temp table or use a CTE.</li>
  <li>If a permanent table with the same name exists, the temp table <em>shadows</em> it &mdash; queries hit the temp table for the session. Use <code>DROP TEMPORARY TABLE</code> (not <code>DROP TABLE</code>) to safely remove only the temp.</li>
</ul>

<p><strong>CTE alternative</strong>: for one-shot intermediate results within a single query, MySQL 8&rsquo;s <code>WITH</code> clause is cleaner &mdash; no setup, no cleanup, scoped to the query. Use temp tables when the staged data must persist across multiple statements (multi-step ETL, complex reports executed via stored procedures).</p>
'''

ANSWERS[15] = r'''
<p><code>GROUP_CONCAT</code> aggregates rows from a group into a single delimited string &mdash; the SQL way to flatten one-to-many relationships into a single result column without the application having to stitch them together.</p>

<pre><code>SELECT
  u.id,
  u.name,
  GROUP_CONCAT(DISTINCT t.name ORDER BY t.name SEPARATOR ', ') AS tags
FROM users u
JOIN user_tags ut ON ut.user_id = u.id
JOIN tags t       ON t.id = ut.tag_id
GROUP BY u.id, u.name;</code></pre>

<p>Output one row per user with their tags rolled up into a comma-separated list.</p>

<p><strong>Optional clauses</strong>:</p>

<ul>
  <li><code>DISTINCT</code> &mdash; deduplicate values before concatenating.</li>
  <li><code>ORDER BY</code> &mdash; sort within the concatenation.</li>
  <li><code>SEPARATOR 'str'</code> &mdash; default is a comma. Pass an empty string for no separator.</li>
</ul>

<p><strong>The truncation pitfall</strong>: results are silently truncated at <code>group_concat_max_len</code> (default <strong>1024 bytes</strong>). On large groups the trailing values vanish without error or warning. Raise it for the session before queries that may produce long outputs:</p>

<pre><code>SET SESSION group_concat_max_len = 1000000;</code></pre>

<p>Or set the global default in <code>my.cnf</code>: <code>group_concat_max_len = 1048576</code>.</p>

<p><strong>JSON alternative</strong>: <code>JSON_ARRAYAGG</code> (8.0+) returns a proper JSON array, which is easier to parse on the application side and doesn&rsquo;t need delimiter handling:</p>

<pre><code>SELECT
  u.id,
  JSON_ARRAYAGG(t.name) AS tags
FROM users u JOIN user_tags ut ON ut.user_id = u.id
             JOIN tags t       ON t.id = ut.tag_id
GROUP BY u.id;
-- Returns ["sql", "react", "kubernetes"] as a real JSON array.</code></pre>

<p>Use <code>JSON_OBJECTAGG</code> for key→value rollups. For new code prefer the JSON aggregates &mdash; they&rsquo;re less fragile than string concatenation.</p>
'''

ANSWERS[16] = r'''
<p>Joins combine rows from multiple tables based on a matching condition. The four standard variants differ only in <em>which non-matching rows are kept</em>.</p>

<table>
  <tr><th>Join type</th><th>Keeps non-matching from</th><th>Use when</th></tr>
  <tr><td><strong>INNER JOIN</strong></td><td>Neither side</td><td>You only want rows present in both tables</td></tr>
  <tr><td><strong>LEFT [OUTER] JOIN</strong></td><td>Left side</td><td>You want all left rows plus matched right data</td></tr>
  <tr><td><strong>RIGHT [OUTER] JOIN</strong></td><td>Right side</td><td>Mirror of LEFT &mdash; rarely used; flip the order and use LEFT</td></tr>
  <tr><td><strong>FULL [OUTER] JOIN</strong></td><td>Both sides</td><td>You want everything, with NULLs where unmatched</td></tr>
</table>

<p><strong>MySQL caveat</strong>: <code>FULL OUTER JOIN</code> isn&rsquo;t supported natively. Emulate with <code>UNION</code>:</p>

<pre><code>SELECT u.id, u.name, o.id AS order_id
FROM users u LEFT JOIN orders o ON o.user_id = u.id
UNION
SELECT u.id, u.name, o.id AS order_id
FROM users u RIGHT JOIN orders o ON o.user_id = u.id;</code></pre>

<p><strong>Common pattern: find rows in A but not B</strong> &mdash; the LEFT JOIN with IS NULL idiom:</p>

<pre><code>SELECT u.id, u.name
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.user_id IS NULL;
-- Users who have never ordered</code></pre>

<p><code>NOT EXISTS</code> usually executes the same plan with cleaner semantics and better NULL handling:</p>

<pre><code>SELECT u.id, u.name FROM users u
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);</code></pre>

<p><strong>Performance considerations</strong>:</p>
<ul>
  <li>Both join columns should be indexed; for <code>JOIN orders o ON o.user_id = u.id</code>, ensure <code>orders.user_id</code> has an index (<code>users.id</code> as PK is already indexed).</li>
  <li>MySQL 8 supports <strong>hash joins</strong> for non-indexed equi-joins on large tables &mdash; previously a nested-loop disaster, now efficient.</li>
  <li>Predicates on the right table of a <code>LEFT JOIN</code> belong in the <code>ON</code> clause, not <code>WHERE</code> &mdash; otherwise the LEFT JOIN collapses to INNER.</li>
</ul>
'''

ANSWERS[17] = r'''
<p>Stored functions return a single value and can be embedded inside SQL expressions like a built-in function. They package logic that would otherwise be repeated in many queries or in application code.</p>

<pre><code>DELIMITER //

CREATE FUNCTION fmt_currency(amount DECIMAL(15,2), code CHAR(3))
RETURNS VARCHAR(32)
DETERMINISTIC
NO SQL
BEGIN
  RETURN CONCAT(code, ' ', FORMAT(amount, 2));
END //

DELIMITER ;

SELECT id, fmt_currency(total, 'USD') AS display_total FROM orders;</code></pre>

<p><strong>Required characteristic clauses</strong> &mdash; MySQL needs to know the function&rsquo;s data-access pattern for replication and optimization:</p>

<table>
  <tr><th>Clause</th><th>Meaning</th></tr>
  <tr><td><code>DETERMINISTIC</code></td><td>Same input → same output. Required for use in generated columns and some optimizations.</td></tr>
  <tr><td><code>NOT DETERMINISTIC</code></td><td>Output may vary (uses <code>NOW()</code>, <code>RAND()</code>, etc.).</td></tr>
  <tr><td><code>NO SQL</code></td><td>Pure computation; no SQL inside.</td></tr>
  <tr><td><code>READS SQL DATA</code></td><td>Reads tables but doesn&rsquo;t modify.</td></tr>
  <tr><td><code>MODIFIES SQL DATA</code></td><td>Writes data.</td></tr>
</table>

<p>Without these, MySQL refuses creation unless <code>log_bin_trust_function_creators = ON</code>, because incorrect classification can break statement-based replication.</p>

<p><strong>Performance reality</strong>: a function called in <code>SELECT fn(col) FROM big_table</code> runs once per row &mdash; effectively a correlated subquery. For large result sets, an inline expression or a join often runs faster. Functions that wrap a <code>SELECT COUNT(*)</code> turn one aggregate into N aggregates.</p>

<p><strong>When functions earn their place</strong>:</p>
<ul>
  <li>Encapsulating business logic used by many queries (currency formatting, tax computation, business-day arithmetic).</li>
  <li>Generated columns &mdash; <code>GENERATED ALWAYS AS (my_fn(col))</code> stores the precomputed value, sidestepping the per-row cost.</li>
  <li>Application portability &mdash; clients in different languages all see consistent behavior.</li>
</ul>

<p><strong>Functions vs procedures</strong>: functions return a single value usable in expressions; procedures execute via <code>CALL</code>, can return result sets, and may have OUT parameters. Procedures suit multi-statement workflows; functions suit value computation.</p>
'''

ANSWERS[18] = r'''
<p>A <strong>Common Table Expression</strong> (CTE) is a named, reusable result set defined at the start of a query with the <code>WITH</code> clause. It exists only for the duration of that query &mdash; cleaner than nested subqueries and far cheaper than creating a temporary table for one-off intermediate results. Available in MySQL 8.0+.</p>

<pre><code>WITH high_value_orders AS (
  SELECT user_id, SUM(total) AS revenue, COUNT(*) AS order_count
  FROM orders
  WHERE created_at &gt;= CURDATE() - INTERVAL 1 YEAR
  GROUP BY user_id
  HAVING revenue &gt; 10000
)
SELECT u.id, u.name, h.revenue, h.order_count
FROM users u
JOIN high_value_orders h ON h.user_id = u.id
ORDER BY h.revenue DESC;</code></pre>

<p>The CTE behaves like an inline view: the outer query treats <code>high_value_orders</code> as if it were a table.</p>

<p><strong>Multiple CTEs in one query</strong>:</p>

<pre><code>WITH
  recent_orders AS (
    SELECT user_id, total FROM orders
    WHERE created_at &gt;= CURDATE() - INTERVAL 30 DAY
  ),
  user_country AS (
    SELECT id, country FROM users WHERE active = 1
  )
SELECT uc.country, SUM(ro.total) AS revenue
FROM recent_orders ro
JOIN user_country uc ON uc.id = ro.user_id
GROUP BY uc.country;</code></pre>

<p>Each CTE is reusable within the query; later CTEs can reference earlier ones.</p>

<p><strong>CTEs vs subqueries</strong>:</p>

<table>
  <tr><th>Aspect</th><th>CTE</th><th>Subquery in FROM</th></tr>
  <tr><td>Readability</td><td>Named, top-of-query, sequential</td><td>Nested, often cryptic</td></tr>
  <tr><td>Reuse within query</td><td>Yes</td><td>Must repeat</td></tr>
  <tr><td>Recursion</td><td>Yes (with <code>WITH RECURSIVE</code>)</td><td>No</td></tr>
  <tr><td>Performance</td><td>Identical &mdash; the optimizer treats it as a derived table</td><td>Same</td></tr>
</table>

<p>In MySQL, CTEs are <strong>not materialized by default</strong> &mdash; the optimizer can merge them into the outer query or evaluate them inline. There&rsquo;s no <code>MATERIALIZED</code> hint as in PostgreSQL, but for performance-sensitive cases a temporary table can force materialization.</p>

<p><strong>Recursive CTEs</strong> open up tree/graph traversal &mdash; org charts, category hierarchies, comment threads, file systems &mdash; in pure SQL. See Q19.</p>
'''

ANSWERS[19] = r'''
<p>Recursive CTEs handle hierarchical data &mdash; org charts, category trees, comment threads, file systems &mdash; in pure SQL by chaining a query to its own previous output until no new rows are produced.</p>

<pre><code>WITH RECURSIVE org_tree AS (
  -- Anchor: top-level employees (no manager)
  SELECT id, name, manager_id, 0 AS depth
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- Recursive: people whose manager is in the previous level
  SELECT e.id, e.name, e.manager_id, t.depth + 1
  FROM employees e
  JOIN org_tree t ON e.manager_id = t.id
)
SELECT CONCAT(REPEAT('  ', depth), name) AS indented, depth FROM org_tree;</code></pre>

<p><strong>Structure</strong>:</p>
<ol>
  <li><strong>Anchor query</strong> (above the <code>UNION ALL</code>) &mdash; the seed rows, executed once.</li>
  <li><strong>Recursive query</strong> (below) &mdash; references the CTE, joining back to the source. MySQL re-evaluates this until no new rows appear.</li>
</ol>

<p>Each iteration sees only the previous iteration&rsquo;s output via the CTE name &mdash; not the cumulative set &mdash; which keeps work bounded.</p>

<p><strong>Alternate directions</strong> &mdash; "all ancestors" instead of "all descendants" by flipping the join:</p>

<pre><code>WITH RECURSIVE managers AS (
  SELECT id, name, manager_id FROM employees WHERE id = 42

  UNION ALL

  SELECT e.id, e.name, e.manager_id
  FROM employees e
  JOIN managers m ON e.id = m.manager_id
)
SELECT * FROM managers;
-- Walks upward: employee 42 → their manager → their manager&rsquo;s manager → ...</code></pre>

<p><strong>Safety knobs</strong>: <code>cte_max_recursion_depth</code> caps iterations (default 1000); set lower for queries on potentially-cyclic data to fail fast. Always include a depth column and add <code>WHERE depth &lt; 100</code> as a belt-and-suspenders limit if cycles are conceivable.</p>

<p><strong>When to materialize a closure table instead</strong>: for write-light, read-heavy hierarchies queried thousands of times per second, pre-compute a <code>(ancestor, descendant, depth)</code> table maintained by triggers. Reads become a single index lookup; the recursive CTE only needs to run when the tree changes.</p>

<p>Other useful applications: generating date ranges (<code>WITH RECURSIVE dates AS (SELECT '2026-01-01' AS d UNION ALL SELECT d + INTERVAL 1 DAY FROM dates WHERE d &lt; '2026-12-31')</code>), running cumulative calculations, traversing graph-like FK chains.</p>
'''

ANSWERS[20] = r'''
<p>A <strong>materialized view</strong> is a precomputed query result stored as a table and refreshed on a schedule or trigger &mdash; faster reads at the cost of staleness and write overhead. <strong>MySQL doesn&rsquo;t have native materialized views</strong> (PostgreSQL and Oracle do), so you simulate them with regular tables plus a refresh strategy.</p>

<p><strong>Pattern 1 &mdash; full refresh on a schedule</strong>:</p>

<pre><code>CREATE TABLE mv_revenue_by_country (
  country  CHAR(2) PRIMARY KEY,
  revenue  DECIMAL(15, 2),
  updated_at DATETIME
);

-- Refresh job (scheduled hourly via the event scheduler or external cron)
DELIMITER //
CREATE EVENT refresh_revenue_view
ON SCHEDULE EVERY 1 HOUR
DO
BEGIN
  TRUNCATE TABLE mv_revenue_by_country;

  INSERT INTO mv_revenue_by_country (country, revenue, updated_at)
  SELECT u.country, SUM(o.total), NOW()
  FROM orders o JOIN users u ON u.id = o.user_id
  WHERE o.created_at &gt;= CURDATE() - INTERVAL 1 YEAR
  GROUP BY u.country;
END //
DELIMITER ;</code></pre>

<p>Reads are now an indexed lookup against a 200-row table instead of an aggregation over millions of orders.</p>

<p><strong>Pattern 2 &mdash; incremental refresh via triggers</strong>: maintain the aggregate row by row as the source changes. More work to implement but always fresh.</p>

<pre><code>CREATE TRIGGER orders_after_insert
AFTER INSERT ON orders
FOR EACH ROW
  INSERT INTO mv_revenue_by_country (country, revenue, updated_at)
  SELECT u.country, NEW.total, NOW()
  FROM users u WHERE u.id = NEW.user_id
  ON DUPLICATE KEY UPDATE revenue = revenue + NEW.total, updated_at = NOW();</code></pre>

<p><strong>Pattern 3 &mdash; flag-and-rebuild</strong>: write to a "shadow" table while a background job rebuilds the main one, then atomically swap with <code>RENAME TABLE</code>. Avoids serving partial results during refresh.</p>

<p><strong>Modern alternatives</strong>:</p>
<ul>
  <li><strong>ProxySQL query rewrite</strong> + Redis caching &mdash; cache hot aggregates at the application layer.</li>
  <li><strong>Streaming pipelines</strong> &mdash; <strong>Debezium</strong> reads MySQL binlog into Kafka; <strong>Flink</strong> or <strong>Materialize</strong> maintain incremental aggregates with full SQL semantics.</li>
  <li><strong>Analytics warehouses</strong> &mdash; ClickHouse, BigQuery, Snowflake handle aggregate-heavy queries natively. Replicate from MySQL for reporting.</li>
</ul>

<p>For a single MySQL instance, the scheduled-event pattern covers most reporting needs; reach for streaming infrastructure once latency requirements drop below a few minutes.</p>
'''

ANSWERS[21] = r'''
<p>Window functions perform calculations across a <em>set of rows related to the current row</em> without collapsing them into one row like <code>GROUP BY</code> does. Each row keeps its identity but gains a value computed from a "window" of surrounding rows. MySQL 8+ supports the full standard set.</p>

<pre><code>SELECT
  user_id,
  order_date,
  amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_total,
  LAG(amount)  OVER (PARTITION BY user_id ORDER BY order_date) AS prev_order,
  RANK()       OVER (PARTITION BY user_id ORDER BY amount DESC) AS rank_for_user
FROM orders;</code></pre>

<p>Three windowed values per row, with all original detail preserved. <code>GROUP BY</code> would have collapsed this into one row per user.</p>

<p><strong>The OVER clause has three optional parts</strong>:</p>

<table>
  <tr><th>Part</th><th>Effect</th></tr>
  <tr><td><code>PARTITION BY col</code></td><td>Resets the window per group &mdash; like a <code>GROUP BY</code> for the window only</td></tr>
  <tr><td><code>ORDER BY col</code></td><td>Defines the row order for the window; required for ranking and offset functions</td></tr>
  <tr><td>Frame: <code>ROWS BETWEEN ... AND ...</code></td><td>Limits which rows the function sees</td></tr>
</table>

<p><strong>Function categories</strong>:</p>

<ul>
  <li><strong>Aggregate-as-window</strong>: <code>SUM</code>, <code>AVG</code>, <code>COUNT</code>, <code>MIN</code>, <code>MAX</code> &mdash; running totals, moving averages.</li>
  <li><strong>Ranking</strong>: <code>ROW_NUMBER</code>, <code>RANK</code>, <code>DENSE_RANK</code>, <code>NTILE</code>, <code>PERCENT_RANK</code> &mdash; top-N per group, percentiles, quartiles.</li>
  <li><strong>Offset</strong>: <code>LAG</code>, <code>LEAD</code>, <code>FIRST_VALUE</code>, <code>LAST_VALUE</code>, <code>NTH_VALUE</code> &mdash; comparing to neighbors.</li>
</ul>

<p><strong>Frames for moving calculations</strong> &mdash; the 7-day moving average:</p>

<pre><code>SELECT
  date,
  daily_revenue,
  AVG(daily_revenue) OVER (
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS revenue_7d_avg
FROM daily_summary;</code></pre>

<p><strong>Why they matter</strong>: window functions cleanly replace many self-joins, correlated subqueries, and procedural workarounds. Top-1-per-group, running totals, gap detection, year-over-year comparisons &mdash; one CTE-and-window combination instead of three nested queries. They&rsquo;re the single biggest reason to be on MySQL 8.</p>
'''

ANSWERS[22] = r'''
<p><code>ROW_NUMBER()</code> assigns a unique sequential integer to each row within its partition, ordered by the specified columns. Unlike <code>RANK</code> and <code>DENSE_RANK</code>, it never repeats numbers &mdash; ties are broken arbitrarily by the optimizer.</p>

<pre><code>SELECT
  category,
  product_name,
  price,
  ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rn
FROM products;

-- category    | product   | price | rn
-- ------------+-----------+-------+----
-- electronics | Laptop X  | 2400  | 1
-- electronics | Tablet Y  |  900  | 2
-- electronics | Mouse     |   30  | 3
-- books       | Atlas     |  120  | 1
-- books       | Novel     |   25  | 2</code></pre>

<p><strong>Top-N per group</strong> is the canonical use:</p>

<pre><code>-- Top 3 most expensive products per category
SELECT category, product_name, price
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rn
  FROM products
) ranked
WHERE rn &lt;= 3;</code></pre>

<p>Replaces what would otherwise be a correlated subquery or self-join.</p>

<p><strong>ROW_NUMBER vs RANK vs DENSE_RANK</strong> &mdash; the distinction is how they handle ties:</p>

<table>
  <tr><th>Values</th><th>ROW_NUMBER</th><th>RANK</th><th>DENSE_RANK</th></tr>
  <tr><td>100, 90, 90, 80</td><td>1, 2, 3, 4</td><td>1, 2, 2, 4</td><td>1, 2, 2, 3</td></tr>
</table>

<p>Choose by intent: ROW_NUMBER for "give me exactly N rows" (one winner per group, even on ties); RANK for "all rows tied at the top win" (sports leaderboards); DENSE_RANK for "no gaps" (academic grading bands).</p>

<p><strong>Pagination via ROW_NUMBER</strong> &mdash; portable across databases:</p>

<pre><code>SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (ORDER BY created_at DESC) AS rn
  FROM articles
) ranked
WHERE rn BETWEEN 21 AND 30;
-- Page 3 with 10 items per page</code></pre>

<p>For huge tables, prefer keyset pagination (<code>WHERE created_at &lt; ? ORDER BY created_at DESC LIMIT 10</code>) &mdash; constant time vs ROW_NUMBER&rsquo;s linear cost in offset.</p>

<p><strong>Other practical uses</strong>: deduplicating rows by keeping the first per group, sequencing events for time-series analysis, generating "first occurrence" flags.</p>
'''

ANSWERS[23] = r'''
<p>Schema migrations &mdash; adding columns, changing types, modifying indexes &mdash; are risky on production data because they can lock tables for hours and corrupt state if interrupted. The discipline is to <strong>version migrations as code</strong>, run them through automated tooling, and use online-DDL strategies on large tables.</p>

<p><strong>Migration tools</strong> manage forward and rollback scripts, track which migrations have been applied, and integrate with deploys:</p>

<table>
  <tr><th>Tool</th><th>Ecosystem</th></tr>
  <tr><td><strong>Flyway</strong>, <strong>Liquibase</strong></td><td>Polyglot, JVM origin; SQL or XML migrations</td></tr>
  <tr><td><strong>golang-migrate</strong></td><td>Standalone CLI; works with any stack</td></tr>
  <tr><td><strong>Alembic</strong></td><td>Python / SQLAlchemy</td></tr>
  <tr><td><strong>Prisma Migrate</strong>, <strong>Drizzle Kit</strong></td><td>TypeScript ORM-driven</td></tr>
  <tr><td><strong>Rails migrations</strong>, <strong>Knex</strong></td><td>Ruby, Node</td></tr>
</table>

<p>Each migration gets a timestamped name, a "up" script, and (ideally) a "down" script for rollback. The tool maintains a <code>schema_migrations</code> table tracking what has been applied.</p>

<p><strong>Online DDL on large tables</strong>:</p>
<ul>
  <li><strong>MySQL 8 ALGORITHM=INSTANT</strong> &mdash; metadata-only changes (adding/dropping columns, setting defaults) finish in milliseconds without rewriting data. Always specify it explicitly so MySQL fails fast if the change can&rsquo;t be instant.</li>
  <li><strong>ALGORITHM=INPLACE</strong> &mdash; modifies in place; non-blocking for many index operations.</li>
  <li><strong>pt-online-schema-change</strong> (Percona) &mdash; copies the table in the background, replays binlog changes, atomically renames at the end. Used widely on multi-TB tables.</li>
  <li><strong>gh-ost</strong> (GitHub) &mdash; same goal, no triggers, throttles based on replica lag. Preferred where pt-osc&rsquo;s triggers are problematic.</li>
</ul>

<p><strong>Production-safe patterns</strong>:</p>
<ul>
  <li><strong>Expand-contract</strong> &mdash; for renames or type changes, add the new column, dual-write to both, migrate readers, then drop the old. Each deploy is reversible.</li>
  <li><strong>Backwards-compatible deploys</strong> &mdash; the migration goes out before the code that uses it.</li>
  <li><strong>Test on a snapshot</strong> &mdash; run migrations against a recent production snapshot in staging to catch lock-time surprises.</li>
</ul>

<p><strong>Avoid</strong> ad-hoc SQL run by hand on production. Every change goes through the same automated pipeline as code &mdash; reviewed, tested, recoverable.</p>
'''

ANSWERS[24] = r'''
<p>Backup strategy is determined by two numbers: <strong>RPO</strong> (Recovery Point Objective &mdash; how much data loss is tolerable, in time) and <strong>RTO</strong> (Recovery Time Objective &mdash; how long restoration is allowed to take). Both should be requirements, not afterthoughts.</p>

<p><strong>Logical vs physical backups</strong>:</p>

<table>
  <tr><th>Type</th><th>Tool</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>Logical (SQL dump)</td><td><code>mysqldump</code>, <code>mysqlpump</code></td><td>Portable, version-flexible, selective</td><td>Slow on TB+ databases; hours to restore</td></tr>
  <tr><td>Physical (file copy)</td><td><strong>Percona XtraBackup</strong>, MySQL Enterprise Backup</td><td>Fast (parallelizable), incremental supported</td><td>Same major version + storage required</td></tr>
  <tr><td>Snapshots</td><td>AWS RDS / Aurora, GCP Cloud SQL, EBS snapshots</td><td>Instant; managed service handles complexity</td><td>Cloud lock-in</td></tr>
</table>

<p><strong>Point-in-time recovery (PITR)</strong>: a base backup plus the binary logs lets you restore to any second in time. Indispensable for "the migration script ran at 14:32 and broke production" scenarios. Configure <code>log_bin</code>, <code>binlog_expire_logs_seconds</code> (e.g., 7 days), and back up binlogs continuously.</p>

<p><strong>Operational essentials</strong>:</p>

<ul>
  <li><strong>Use <code>--single-transaction</code></strong> for InnoDB dumps &mdash; consistent snapshot without locking writers.</li>
  <li><strong>Test restores regularly</strong> &mdash; an untested backup doesn&rsquo;t exist. Run quarterly drills to a staging environment.</li>
  <li><strong>3-2-1 rule</strong> &mdash; 3 copies, on 2 different media, with 1 offsite. Cloud snapshots + offsite cold storage (S3 Glacier).</li>
  <li><strong>Encrypt at rest</strong> &mdash; backups contain the same data as the live DB; protect them the same way.</li>
  <li><strong>Monitor backup completion</strong> &mdash; alert if a scheduled backup hasn&rsquo;t finished within its window.</li>
</ul>

<p><strong>Modern managed services</strong> &mdash; AWS RDS, Aurora, Cloud SQL, PlanetScale &mdash; handle base backups, transaction logs, retention, and PITR automatically. For self-hosted MySQL, the standard production stack is XtraBackup nightly + binlog continuous backup + offsite replication. <code>mysqldump</code> remains useful for development environments, table-level extracts, and migrations between major versions.</p>
'''

ANSWERS[25] = r'''
<p>Replication copies writes from a <strong>source</strong> (primary) server to one or more <strong>replicas</strong> (secondaries). Used for read scaling, high availability, geographic distribution, and offloading backups/reports.</p>

<p><strong>How it works</strong>: every change on the source is recorded in its <em>binary log</em> (binlog). Each replica connects, streams the binlog, writes events to its <em>relay log</em>, and applies them &mdash; eventually consistent with the source.</p>

<pre><code>┌──────────┐                     ┌──────────┐
│  source  │  binlog stream      │ replica  │
│ (writes) │ ──────────────────&gt; │ (reads)  │
└──────────┘                     └──────────┘</code></pre>

<p><strong>Setup essentials</strong>:</p>

<pre><code>-- Source my.cnf
server-id = 1
log_bin = mysql-bin
binlog_format = ROW
gtid_mode = ON
enforce_gtid_consistency = ON

-- Replica my.cnf
server-id = 2
relay_log = relay-bin
read_only = ON

-- Replica
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = 'primary',
  SOURCE_USER = 'replicator',
  SOURCE_PASSWORD = '...',
  SOURCE_AUTO_POSITION = 1;
START REPLICA;</code></pre>

<p><strong>Topologies</strong>:</p>

<ul>
  <li><strong>Source &rarr; replicas</strong> &mdash; classic read-scaling. Writes go to source; reads distribute across replicas.</li>
  <li><strong>Cascade</strong> (source &rarr; replica &rarr; replica) &mdash; reduces source load when many replicas exist.</li>
  <li><strong>Group Replication</strong> (MySQL 8) &mdash; multi-primary cluster with automatic failover; foundation of <strong>InnoDB Cluster</strong>.</li>
  <li><strong>Multi-source</strong> &mdash; one replica pulls from multiple sources (data consolidation).</li>
</ul>

<p><strong>Modes</strong>:</p>

<table>
  <tr><th>Mode</th><th>Behavior</th></tr>
  <tr><td>Asynchronous (default)</td><td>Source commits immediately; replicas catch up. Fastest, allows lag.</td></tr>
  <tr><td>Semi-synchronous</td><td>Source waits for at least one replica to acknowledge before commit returns. Slightly slower; protects against losing the last few seconds of writes if source fails.</td></tr>
  <tr><td>Synchronous (Group Replication)</td><td>Quorum-based; majority must agree before commit. Highest durability.</td></tr>
</table>

<p><strong>Operational concerns</strong>: applications must tolerate replica lag (read-your-writes consistency requires routing some reads to source). Modern managed services (Aurora, PlanetScale, Cloud SQL) handle topology, failover, and lag mitigation transparently &mdash; usually the right choice over hand-rolled replication.</p>
'''

ANSWERS[26] = r'''
<p><strong>GTID</strong> (Global Transaction Identifier) tags each transaction with a unique identifier of the form <code>SOURCE_UUID:transaction_number</code>. Replicas track which GTIDs they&rsquo;ve applied; binlog positions become irrelevant. This is the modern replication mechanism &mdash; introduced in MySQL 5.6, mature in 5.7+, the default expectation in 8.x.</p>

<pre><code>-- A transaction&rsquo;s GTID looks like:
3E11FA47-71CA-11E1-9E33-C80AA9429562:23
-- ────────── server UUID ──────────  ─ tx num ─</code></pre>

<p><strong>Why GTIDs are better than the old binlog-position approach</strong>:</p>

<ul>
  <li><strong>Failover is trivial</strong> &mdash; promote any replica to source. New replicas just say <code>SOURCE_AUTO_POSITION = 1</code>; the protocol exchanges GTID sets and resumes from the right point. With binlog positions, every replica had to be carefully repointed using the new source&rsquo;s exact file/offset.</li>
  <li><strong>Idempotent application</strong> &mdash; replicas track applied GTIDs in <code>gtid_executed</code>; an event with a GTID already there is skipped, preventing double-application after failover.</li>
  <li><strong>Audit trail</strong> &mdash; every transaction is uniquely identifiable across the entire topology. <code>SHOW BINARY LOG STATUS</code> displays current GTID sets; you can grep binlogs for a specific transaction across hosts.</li>
</ul>

<p><strong>Configuration</strong>:</p>

<pre><code>[mysqld]
gtid_mode = ON
enforce_gtid_consistency = ON
log_replica_updates = ON   -- so replicas can themselves be sources for cascading</code></pre>

<p><code>enforce_gtid_consistency</code> rejects statements that can&rsquo;t be safely tracked &mdash; <code>CREATE TABLE ... AS SELECT</code>, non-transactional DML in transactions, etc. The constraints are mild and worth accepting.</p>

<p><strong>Operational queries</strong>:</p>

<pre><code>-- What has been applied?
SELECT @@global.gtid_executed;

-- What has been purged from binlogs?
SELECT @@global.gtid_purged;

-- Has a replica caught up?
SHOW REPLICA STATUS\G  -- compare Executed_Gtid_Set with source&rsquo;s</code></pre>

<p><strong>The win</strong>: GTID-based replication makes MySQL clusters operationally manageable. Failover, replica reseeding, and topology changes that used to require careful manual coordination become single commands. Combined with <strong>InnoDB Cluster</strong> or <strong>Orchestrator</strong>, GTIDs underpin the automated failover used by managed services and modern self-hosted setups.</p>
'''

ANSWERS[27] = r'''
<p><strong>Replication lag</strong> is the time gap between a write committing on the source and being applied on a replica. Some lag is normal; growing or unbounded lag means the replica can&rsquo;t keep up &mdash; replicas eventually serve stale data, and the cluster loses its HA properties.</p>

<p><strong>Measure it</strong>:</p>

<pre><code>SHOW REPLICA STATUS\G
-- Key fields:
-- Seconds_Behind_Source: 12       (the simple lag indicator)
-- Replica_IO_Running:    Yes
-- Replica_SQL_Running:   Yes
-- Last_SQL_Error:        ...

-- More accurate via heartbeat tables (pt-heartbeat or built-in)
SELECT NOW() - last_heartbeat AS true_lag_seconds FROM heartbeat.heartbeat;</code></pre>

<p><code>Seconds_Behind_Source</code> can read 0 even when the replica is very behind &mdash; it measures only the time of the currently-being-applied event, not the queue depth. <strong>pt-heartbeat</strong> writes a timestamp to a heartbeat table on the source; the replica computes lag as <code>NOW() - last_heartbeat</code>, which is robust.</p>

<p><strong>Common causes</strong>:</p>

<table>
  <tr><th>Cause</th><th>Diagnosis</th></tr>
  <tr><td>Single-threaded replica SQL apply</td><td>Replica CPU at 100% on one core. Enable <code>slave_parallel_workers</code> (default 4 in 8.0).</td></tr>
  <tr><td>Slow query on replica</td><td><code>SHOW PROCESSLIST</code> on replica shows a long-running statement. Add missing indexes.</td></tr>
  <tr><td>Heavy write burst on source</td><td>Source binlog growth rate &gt; replica apply rate. Tune buffer pool, parallel workers, or batch the writes.</td></tr>
  <tr><td>Network</td><td>IO thread paused or slow. Check bandwidth, packet loss between source and replica.</td></tr>
  <tr><td>Long transactions</td><td>One huge transaction blocks all subsequent events. Break large updates into batches.</td></tr>
</table>

<p><strong>Mitigations</strong>:</p>
<ul>
  <li><strong>Parallel replication</strong> &mdash; <code>slave_parallel_type=LOGICAL_CLOCK</code> + multiple workers applies independent transactions concurrently. Default in 8.0.</li>
  <li><strong>Larger replica</strong> &mdash; replicas often need at least the same hardware spec as the source for write-heavy workloads, contrary to the assumption they can be smaller.</li>
  <li><strong>Skip non-critical reads</strong> &mdash; some queries route to the source when freshness matters; static data goes to replicas.</li>
  <li><strong>InnoDB Cluster / Group Replication</strong> &mdash; built-in flow control throttles fast members so replicas keep up.</li>
</ul>

<p><strong>Monitoring</strong>: alert on lag &gt; threshold (e.g., 60s), and on lag growing rather than absolute value. Sustained growth indicates a structural problem; spikes during batch jobs are usually self-correcting.</p>
'''

ANSWERS[28] = r'''
<p><code>binlog_format</code> controls how changes are recorded in the binary log. Three values, each with different replication behavior:</p>

<table>
  <tr><th>Format</th><th>What gets logged</th><th>Pros</th><th>Cons</th></tr>
  <tr><td><strong>STATEMENT</strong></td><td>The original SQL text</td><td>Compact; easy to read</td><td>Non-deterministic statements (NOW(), RAND(), UUID(), reads from triggers) drift between source and replica</td></tr>
  <tr><td><strong>ROW</strong> (default since 5.7.7)</td><td>The actual before/after row images</td><td>Always deterministic; reflects exact state changes</td><td>Larger binlogs; harder to read by humans</td></tr>
  <tr><td><strong>MIXED</strong></td><td>STATEMENT by default; auto-switches to ROW for unsafe statements</td><td>Compact when safe</td><td>Behavior varies by statement; harder to reason about</td></tr>
</table>

<p><strong>Why ROW won</strong>: in modern MySQL the safety guarantees of ROW outweigh its size cost. Replicas always apply the exact same row state the source committed, eliminating an entire class of subtle drift bugs (auto-increments diverging, trigger results differing, time-dependent functions). It&rsquo;s also the format CDC tools (<strong>Debezium</strong>, <strong>Maxwell</strong>) consume to stream changes to Kafka, search engines, or data warehouses.</p>

<pre><code>-- Set format
SET GLOBAL binlog_format = 'ROW';

-- For a single transaction
SET SESSION binlog_format = 'ROW';

-- Persist in my.cnf
[mysqld]
binlog_format = ROW
binlog_row_image = MINIMAL  -- only changed columns + PK; reduces size</code></pre>

<p><strong>binlog_row_image</strong> tunes what ROW format actually records:</p>

<ul>
  <li><code>FULL</code> (default) &mdash; every column for every change, even unchanged. Largest, safest for replication clients that need full state.</li>
  <li><code>MINIMAL</code> &mdash; only PK + changed columns. Smaller binlogs. Some downstream consumers (CDC) require full image.</li>
  <li><code>NOBLOB</code> &mdash; full image but skip BLOB/TEXT columns when not modified.</li>
</ul>

<p><strong>Inspecting binlogs</strong> &mdash; even ROW format is human-readable via <code>mysqlbinlog</code>:</p>

<pre><code>mysqlbinlog --base64-output=DECODE-ROWS --verbose mysql-bin.000123
-- Shows pseudo-SQL representations of row events</code></pre>

<p><strong>Production answer</strong>: leave it at ROW. The size cost is minor compared to the operational simplicity, and many modern features (CDC pipelines, GTID-based reseeding, backwards-compatible replication) assume or work best with ROW.</p>
'''

ANSWERS[29] = r'''
<p>Multi-master means multiple servers accept writes; conflicts (two writes to the same row at the same time on different masters) must be detected and resolved. <strong>Classic asynchronous master-master replication is operationally fragile</strong> and largely obsolete in MySQL 8 &mdash; <strong>Group Replication</strong> (the foundation of InnoDB Cluster) is the supported modern answer.</p>

<p><strong>Group Replication</strong> uses a Paxos-style consensus protocol: every transaction is sent to all members, certified to detect conflicts, and applied only after a quorum agrees. Two modes:</p>

<table>
  <tr><th>Mode</th><th>Description</th></tr>
  <tr><td><strong>Single-primary</strong> (default)</td><td>One member accepts writes; others are read-only secondaries. Automatic failover on primary loss.</td></tr>
  <tr><td><strong>Multi-primary</strong></td><td>All members accept writes. Conflicts detected at certification; the first transaction wins, the conflicting one is rolled back.</td></tr>
</table>

<p><strong>Configuration</strong>:</p>

<pre><code>[mysqld]
plugin_load_add = group_replication.so
group_replication_group_name = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
group_replication_start_on_boot = OFF
group_replication_local_address = "node1:33061"
group_replication_group_seeds = "node1:33061,node2:33061,node3:33061"
group_replication_bootstrap_group = OFF
group_replication_single_primary_mode = ON</code></pre>

<p><strong>Why classic circular replication is dangerous</strong>:</p>
<ul>
  <li><strong>No conflict detection</strong> &mdash; both nodes accept conflicting updates, then the later replication event silently overwrites the other&rsquo;s. Last-write-wins is rarely the desired semantic.</li>
  <li><strong>Auto-increment collisions</strong> &mdash; without offsetting (<code>auto_increment_increment</code> + <code>auto_increment_offset</code>), both nodes generate the same IDs.</li>
  <li><strong>Failure modes</strong> are subtle &mdash; one node fails, comes back, replication breaks unpredictably depending on what was in flight.</li>
</ul>

<p><strong>Practical advice</strong>:</p>

<ul>
  <li><strong>Don&rsquo;t roll your own multi-master</strong>. Use Group Replication / InnoDB Cluster or a managed service (Aurora, PlanetScale, TiDB).</li>
  <li><strong>Most apps don&rsquo;t need multi-write</strong> &mdash; route writes to a single primary; replicas serve reads. This is simpler and avoids the entire conflict-resolution problem.</li>
  <li><strong>Geographic distribution</strong> with strong consistency is genuinely hard &mdash; consider region-local primaries with eventual consistency, CRDTs, or a database designed for it (CockroachDB, Spanner).</li>
</ul>

<p>"Multi-master" sounds like a scaling answer; in practice it&rsquo;s usually an availability answer with significant complexity costs.</p>
'''

ANSWERS[30] = r'''
<p><strong>Sharding</strong> is horizontal partitioning <em>across servers</em> &mdash; rows of one logical table are distributed across multiple physical databases. Used when a single server&rsquo;s I/O, CPU, or storage can&rsquo;t handle the workload, even after vertical scaling and read replicas.</p>

<p><strong>Sharding strategies</strong>:</p>

<table>
  <tr><th>Strategy</th><th>How it works</th><th>Trade-offs</th></tr>
  <tr><td><strong>Hash-based</strong></td><td><code>shard_id = hash(user_id) % N</code></td><td>Even distribution; resharding is painful (every key&rsquo;s shard changes when N changes)</td></tr>
  <tr><td><strong>Range-based</strong></td><td>Users 1-10M on shard 1, 10M-20M on shard 2</td><td>Simple, range queries possible; hot ranges create hotspots</td></tr>
  <tr><td><strong>Directory-based</strong></td><td>Lookup table maps each key to its shard</td><td>Most flexible; lookup table is itself a SPOF and bottleneck</td></tr>
  <tr><td><strong>Geographic</strong></td><td>By region (US shard, EU shard)</td><td>Data residency; latency wins; uneven population</td></tr>
</table>

<p><strong>What sharding costs you</strong>:</p>
<ul>
  <li><strong>No cross-shard JOINs</strong> &mdash; or you build them in application code, gathering rows from each shard and joining in memory. Slow and fragile.</li>
  <li><strong>No global aggregates</strong> trivially &mdash; <code>SELECT COUNT(*) FROM users</code> requires fan-out plus merge.</li>
  <li><strong>Distributed transactions</strong> &mdash; transferring money between two users on different shards either uses 2PC (slow, fragile) or eventual consistency with reconciliation.</li>
  <li><strong>Resharding</strong> &mdash; outgrowing the initial shard count is genuinely painful; consistent hashing eases this but doesn&rsquo;t eliminate it.</li>
</ul>

<p><strong>Modern tools that handle the complexity for you</strong>:</p>
<ul>
  <li><strong>Vitess</strong> &mdash; the YouTube-origin sharding layer; speaks MySQL protocol so applications need few changes. Powers PlanetScale and many Slack/GitHub-scale services.</li>
  <li><strong>PlanetScale</strong> &mdash; managed Vitess; resharding via online migrations.</li>
  <li><strong>TiDB</strong> &mdash; MySQL-compatible distributed SQL with automatic sharding and global ACID.</li>
  <li><strong>ProxySQL</strong> &mdash; routing layer; works for simple shard-aware routing patterns.</li>
</ul>

<p><strong>Pragmatic advice</strong>: most teams shouldn&rsquo;t shard. Hardware has gotten huge &mdash; a single MySQL instance on modern cloud hardware can serve 100K+ QPS and tens of TB. Push vertical scaling, read replicas, table partitioning, application caching, and archiving as far as possible first. Only when one shard&rsquo;s write throughput genuinely caps the system should you take on sharding&rsquo;s permanent operational tax.</p>
'''

ANSWERS[31] = r'''
<p>Complex transactions need to balance three concerns: <strong>correctness</strong> (atomic, isolated), <strong>throughput</strong> (lock contention kills concurrency), and <strong>recoverability</strong> (deadlocks happen and must be retried). The optimization rules are mostly about keeping transactions <em>short and predictable</em>.</p>

<p><strong>Core principles</strong>:</p>

<ul>
  <li><strong>Begin late, commit early</strong> &mdash; a transaction holds locks from its first write until <code>COMMIT</code>. Don&rsquo;t do user input, network calls, or computation inside one. Open the transaction immediately before the writes; commit immediately after.</li>
  <li><strong>Touch rows in a consistent order</strong> &mdash; if two transactions update rows A and B, both should lock A before B. Sort by PK before issuing updates. Eliminates a major class of deadlocks.</li>
  <li><strong>Batch large updates</strong> &mdash; updating millions of rows in one transaction creates a huge undo log, blocks other writers via metadata locks, and often deadlocks. Loop with <code>LIMIT 1000</code> chunks, committing each.</li>
  <li><strong>Use the right isolation level</strong> &mdash; default <code>REPEATABLE READ</code> takes gap locks on range queries, increasing collision surface. <code>READ COMMITTED</code> trades repeatability for fewer locks &mdash; fine for most application patterns.</li>
  <li><strong>Always retry deadlocks</strong> &mdash; error 1213 isn&rsquo;t a bug; it&rsquo;s normal. Wrap business operations in retry-with-backoff (3 attempts, exponential backoff).</li>
</ul>

<p><strong>Lock-aware patterns</strong>:</p>

<pre><code>-- SELECT ... FOR UPDATE — explicit row lock for read-then-write patterns
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 5 FOR UPDATE;  -- locks row 5
UPDATE accounts SET balance = balance - 100 WHERE id = 5;
COMMIT;

-- SELECT ... FOR SHARE — read lock; allows other reads but blocks writes
SELECT inventory FROM products WHERE id = 12 FOR SHARE;</code></pre>

<p><strong>SKIP LOCKED</strong> for queue-like patterns &mdash; multiple workers consume jobs without blocking each other:</p>

<pre><code>SELECT id FROM jobs
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;     -- skip rows another transaction has locked</code></pre>

<p><strong>Diagnostics</strong>:</p>
<ul>
  <li><code>SHOW ENGINE INNODB STATUS\G</code> &mdash; current locks, waits, recent deadlocks.</li>
  <li><code>information_schema.INNODB_TRX</code> &mdash; running transactions and what they hold.</li>
  <li><code>performance_schema.data_locks</code> / <code>data_lock_waits</code> &mdash; structured queries over current lock state.</li>
  <li>Slow log with <code>log_slow_admin_statements</code> &mdash; long transactions stand out.</li>
</ul>

<p>The biggest wins almost always come from <strong>shortening transactions</strong>, not tuning isolation or lock granularity.</p>
'''

ANSWERS[32] = r'''
<p>Isolation levels control what one transaction can see of another&rsquo;s in-flight work. The four standard levels trade strictness against concurrency:</p>

<table>
  <tr><th>Level</th><th>Dirty Read</th><th>Non-repeatable Read</th><th>Phantom Read</th><th>Lock cost</th></tr>
  <tr><td>READ UNCOMMITTED</td><td>Possible</td><td>Possible</td><td>Possible</td><td>Lowest</td></tr>
  <tr><td>READ COMMITTED</td><td>No</td><td>Possible</td><td>Possible</td><td>Low</td></tr>
  <tr><td><strong>REPEATABLE READ</strong> (MySQL default)</td><td>No</td><td>No</td><td>No (via gap locks)</td><td>Medium</td></tr>
  <tr><td>SERIALIZABLE</td><td>No</td><td>No</td><td>No</td><td>Highest</td></tr>
</table>

<p><strong>The anomalies</strong>:</p>

<ul>
  <li><strong>Dirty read</strong> &mdash; transaction A reads a row B has modified but not yet committed. If B rolls back, A acted on data that never existed.</li>
  <li><strong>Non-repeatable read</strong> &mdash; A reads row 5, B updates row 5 and commits, A reads row 5 again and gets a different value within the same transaction.</li>
  <li><strong>Phantom read</strong> &mdash; A queries <code>WHERE balance &gt; 100</code> and gets 5 rows; B inserts a matching row; A re-queries and gets 6.</li>
</ul>

<p><strong>MySQL specifics</strong>:</p>

<ul>
  <li><strong>InnoDB&rsquo;s REPEATABLE READ uses MVCC + gap locks</strong> for both reads and range scans. This eliminates phantoms in practice (more strict than the SQL standard requires).</li>
  <li><strong>Snapshot is taken at the first read</strong>, not at <code>BEGIN</code>. Subsequent reads in the transaction see that snapshot regardless of what others commit.</li>
  <li><strong>Locking reads bypass the snapshot</strong> &mdash; <code>SELECT ... FOR UPDATE</code> sees the latest committed version, not the snapshot.</li>
</ul>

<p><strong>Setting the level</strong>:</p>

<pre><code>-- Per session
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Per transaction
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
START TRANSACTION;

-- Globally in my.cnf
[mysqld]
transaction_isolation = READ-COMMITTED</code></pre>

<p><strong>Practical guidance</strong>:</p>

<ul>
  <li><strong>READ COMMITTED</strong> is a good default for most applications &mdash; lower lock contention, fewer deadlocks, and the application code rarely depends on intra-transaction repeatable reads.</li>
  <li><strong>REPEATABLE READ</strong> (MySQL default) is fine if you stay there; switching can change application behavior subtly. PostgreSQL and Oracle default to READ COMMITTED for the contention reasons.</li>
  <li><strong>SERIALIZABLE</strong> only when you have specific correctness requirements that demand it &mdash; financial transactions, certain compliance scenarios. Throughput drops noticeably.</li>
  <li><strong>READ UNCOMMITTED</strong> is essentially never the right choice in production.</li>
</ul>
'''

ANSWERS[33] = r'''
<p><code>SERIALIZABLE</code> is the strictest isolation level &mdash; transactions execute as if they ran one at a time, even though they actually run concurrently. It eliminates every read anomaly: no dirty reads, no non-repeatable reads, no phantoms, no write skew.</p>

<p><strong>How InnoDB implements it</strong>: <code>SERIALIZABLE</code> implicitly converts plain <code>SELECT</code> statements to <code>SELECT ... LOCK IN SHARE MODE</code> &mdash; every read takes a shared lock on the rows it touches, preventing other transactions from modifying them until the reading transaction completes. Combined with <code>REPEATABLE READ</code>&rsquo;s gap locks, the result is genuinely serializable execution.</p>

<pre><code>-- Within a SERIALIZABLE transaction:
SELECT balance FROM accounts WHERE id = 5;
-- Effectively becomes: SELECT balance FROM accounts WHERE id = 5 LOCK IN SHARE MODE;
-- Other transactions can still read row 5, but cannot modify it until commit.</code></pre>

<p><strong>The implications &mdash; what makes it expensive</strong>:</p>

<ul>
  <li><strong>Locking on every read</strong> &mdash; <code>SELECT</code>s that previously held no locks now block writers. Read-heavy workloads see throughput drop.</li>
  <li><strong>More deadlocks</strong> &mdash; share locks plus write locks create more conflict configurations. Every transaction must be prepared to retry.</li>
  <li><strong>Longer wait times</strong> &mdash; transactions queue more, latency rises.</li>
  <li><strong>No phantom protection beyond REPEATABLE READ in InnoDB</strong> &mdash; the practical correctness gain over RR is small in MySQL specifically.</li>
</ul>

<p><strong>When you actually need it</strong>:</p>

<ul>
  <li><strong>Write skew scenarios</strong> &mdash; two transactions read overlapping data, decide to act based on what they read, and commit non-conflicting writes whose combination violates an invariant. The classic example: two on-call doctors checking "is at least one other doctor on call?" each see "yes," each take themselves off &mdash; both transactions commit, on-call set is now empty. SERIALIZABLE prevents this; REPEATABLE READ doesn&rsquo;t.</li>
  <li><strong>Strict accounting / financial requirements</strong> where correctness must be provable.</li>
  <li><strong>Test correctness verification</strong> &mdash; running test suites under SERIALIZABLE catches concurrency bugs that lower levels mask.</li>
</ul>

<p><strong>Practical pattern</strong>: use SERIALIZABLE on the small fraction of transactions where it matters, not server-wide:</p>

<pre><code>SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
START TRANSACTION;
-- ... critical correctness-sensitive logic ...
COMMIT;
-- Subsequent transactions revert to the session/global default.</code></pre>

<p><strong>Modern alternative</strong>: explicit <code>SELECT ... FOR UPDATE</code> at lower isolation often achieves the same correctness goal with less contention &mdash; you lock only the specific rows that matter, not everything you read.</p>
'''

ANSWERS[34] = r'''
<p>Two strategies for handling concurrent updates to the same data:</p>

<table>
  <tr><th></th><th>Pessimistic locking</th><th>Optimistic locking</th></tr>
  <tr><td>Assumption</td><td>Conflicts will happen, prevent them</td><td>Conflicts are rare, detect them</td></tr>
  <tr><td>Mechanism</td><td>Acquire DB lock before reading/modifying</td><td>Read freely; verify version on write</td></tr>
  <tr><td>SQL pattern</td><td><code>SELECT ... FOR UPDATE</code></td><td>Version column or timestamp; <code>WHERE version = ?</code> on update</td></tr>
  <tr><td>Cost</td><td>Lock wait time on contention</td><td>Wasted work on retry; conflict detection adds an extra column check</td></tr>
  <tr><td>Best when</td><td>High contention; long-running updates</td><td>Low contention; short transactions</td></tr>
</table>

<p><strong>Pessimistic example</strong>:</p>

<pre><code>START TRANSACTION;
SELECT balance FROM accounts WHERE id = 5 FOR UPDATE;  -- row locked
-- ... compute new balance ...
UPDATE accounts SET balance = ? WHERE id = 5;
COMMIT;
-- Other transactions wait at the SELECT FOR UPDATE until commit.</code></pre>

<p><strong>Optimistic example</strong>:</p>

<pre><code>-- Read with version
SELECT balance, version FROM accounts WHERE id = 5;

-- Compute new balance in the application

-- Conditional update — succeeds only if no one else updated
UPDATE accounts
SET balance = ?, version = version + 1
WHERE id = 5 AND version = ?;       -- version from the read

-- ROW_COUNT() = 0 means someone else won the race; retry from the top.</code></pre>

<p>The version column is incremented on every write; concurrent writers see the version has changed and their UPDATE affects 0 rows.</p>

<p><strong>Why optimistic often wins for web applications</strong>:</p>

<ul>
  <li>Web requests are <em>stateless</em> &mdash; the application fetches data, the user thinks for 10 minutes, then submits. Holding a database lock the whole time is a non-starter; pessimistic is impossible.</li>
  <li>Conflicts on the same row by two users in the same second are genuinely rare in most workloads. The retry cost is amortized to zero in practice.</li>
  <li>No long-held locks → no replica-lag amplification, no deadlocks, no lock waits in metrics.</li>
</ul>

<p><strong>When pessimistic earns its place</strong>:</p>

<ul>
  <li>Inventory decrements, financial transfers, ticket sales &mdash; high-contention single rows where many writers race.</li>
  <li>Long-running back-office processes that need exclusive access.</li>
  <li>Patterns combining read and write where reading the latest committed value is essential (claiming jobs from a queue: <code>FOR UPDATE SKIP LOCKED</code>).</li>
</ul>

<p>ORMs (Hibernate, JPA, Django, Rails) typically build optimistic locking in via a <code>version</code> column convention. Use it as the default; reach for pessimistic locks only when measurement shows you need to.</p>
'''

ANSWERS[35] = r'''
<p>Row-level security (RLS) restricts which rows a user can see or modify based on their identity, role, or attributes. <strong>MySQL has no native RLS</strong> (PostgreSQL does); the standard implementation patterns are at the schema and application level.</p>

<p><strong>Pattern 1 &mdash; Views with predicate filters</strong>:</p>

<pre><code>CREATE VIEW v_orders_for_user AS
SELECT * FROM orders
WHERE user_id = (SELECT id FROM users WHERE username = SESSION_USER());
-- Each connecting user sees only their own orders.

-- Grant only on the view, never on the base table:
REVOKE SELECT ON shop.orders FROM 'app_users';
GRANT SELECT ON shop.v_orders_for_user TO 'app_users';</code></pre>

<p><code>SESSION_USER()</code> returns the authenticated user; the view filters automatically. Works well when users have distinct DB accounts; less useful when one app user is shared.</p>

<p><strong>Pattern 2 &mdash; Tenant ID in every query, enforced at the application layer</strong>:</p>

<pre><code>// Every query is annotated with the tenant
SELECT * FROM orders WHERE tenant_id = ? AND ...
INSERT INTO orders (tenant_id, ...) VALUES (?, ...)

// ORM middleware adds tenant_id automatically — never trust app code to remember.</code></pre>

<p>This is what most multi-tenant SaaS apps do. The risk: one missed <code>WHERE tenant_id = ?</code> leaks data across tenants. Static analysis (linting), code review, and integration tests are essential. Some ORMs (Prisma with global filters, SQLAlchemy with mixins) automate it.</p>

<p><strong>Pattern 3 &mdash; Stored procedures as the only API</strong>:</p>

<pre><code>CREATE PROCEDURE get_orders_for(IN user_id INT)
BEGIN
  -- Verifies the calling user matches user_id, then returns rows
  IF user_id != (SELECT id FROM users WHERE username = SESSION_USER()) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Access denied';
  END IF;
  SELECT * FROM orders WHERE user_id = user_id;
END;</code></pre>

<p>Application has <code>EXECUTE</code> on procedures only, never on tables. Tighter security than views; more rigid than direct SQL.</p>

<p><strong>Pattern 4 &mdash; Database-per-tenant</strong>:</p>

<p>Each tenant gets a separate database (or schema). Permissions are managed at the database level &mdash; tenant A&rsquo;s connection literally cannot see tenant B&rsquo;s data. Strongest isolation; complicates schema migrations (now apply to N databases) and backup strategy. Suits regulated industries; awkward at scale.</p>

<p><strong>Production reality</strong>: most multi-tenant MySQL apps use <strong>tenant_id everywhere with ORM enforcement</strong>, plus database-level access control limiting which app users can connect at all. True row-level security with database enforcement requires either Postgres, custom triggers, or a proxy layer (<strong>ProxySQL</strong> with query rewriting).</p>
'''

ANSWERS[36] = r'''
<p><strong>User-defined variables</strong> are session-scoped variables prefixed with <code>@</code>. They hold values across statements within a single connection &mdash; useful for stashing intermediate results, generating row numbers in pre-window-function MySQL, or passing values between successive queries.</p>

<pre><code>SET @threshold = 1000;
SELECT * FROM orders WHERE total &gt; @threshold;

-- Capture a value
SELECT @last_id := MAX(id) FROM users;
SELECT * FROM users WHERE id = @last_id;

-- Multi-statement use
SELECT @sum := 0;
SELECT id, total, @sum := @sum + total AS running_total FROM orders ORDER BY id;</code></pre>

<p><strong>Two assignment operators</strong>:</p>

<ul>
  <li><code>SET @v = 5;</code> &mdash; standalone <code>SET</code> statement.</li>
  <li><code>SELECT @v := 5;</code> or <code>SELECT @v := col FROM ...</code> &mdash; assignment inside a query (using <code>:=</code>, not <code>=</code> which would be comparison).</li>
</ul>

<p><strong>The historical pre-MySQL 8 use case &mdash; row numbering</strong>:</p>

<pre><code>SELECT @rn := @rn + 1 AS row_num, name
FROM users, (SELECT @rn := 0) init
ORDER BY name;
-- Generates 1, 2, 3, ... across results</code></pre>

<p>Window functions (<code>ROW_NUMBER() OVER (...)</code>) replaced this in MySQL 8 &mdash; cleaner, optimizer-friendly, and the order of evaluation is well-defined. <strong>The variable trick relies on undefined evaluation order in newer MySQL and may produce wrong results.</strong></p>

<p><strong>Modern uses that still make sense</strong>:</p>

<ul>
  <li>Capturing output between statements: <code>SET @new_id := LAST_INSERT_ID();</code> then using it in a subsequent query.</li>
  <li>Parameterizing values across multiple statements in scripts.</li>
  <li>Building dynamic SQL with <code>PREPARE</code> + <code>EXECUTE</code> using variables.</li>
</ul>

<pre><code>SET @table = 'orders';
SET @sql = CONCAT('SELECT COUNT(*) FROM ', @table);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;</code></pre>

<p><strong>Caveats</strong>:</p>

<ul>
  <li><strong>Session-scoped</strong> &mdash; not visible to other connections; cleared when the connection closes.</li>
  <li><strong>Loosely typed</strong> &mdash; can hold any scalar; type can change between assignments. Use with care in arithmetic.</li>
  <li><strong>Evaluation order is unsafe in expressions</strong> &mdash; using the same variable on both sides of an expression yields undefined results. Don&rsquo;t do <code>SELECT @v, @v := col + 1 FROM tbl</code>.</li>
  <li><strong>Not the same as system variables</strong> (<code>@@max_connections</code>) or stored-procedure local variables (<code>DECLARE x INT</code>).</li>
</ul>

<p>For most modern queries, window functions and CTEs replace the older user-variable hacks. The variables remain useful for parameter passing and scripting.</p>
'''

ANSWERS[37] = r'''
<p>Bulk inserts dominate import performance. The naive approach &mdash; one <code>INSERT</code> per row in a loop &mdash; is 50-100x slower than batched inserts because every statement pays full network round-trip + transaction commit overhead.</p>

<p><strong>Optimization techniques, biggest wins first</strong>:</p>

<ul>
  <li><strong>Multi-row INSERT</strong> &mdash; one statement, many rows. Each row adds ~30 bytes of overhead instead of a full statement.
<pre><code>INSERT INTO users (name, email) VALUES
  ('Alice', 'a@x.com'),
  ('Bob',   'b@x.com'),
  ('Carol', 'c@x.com'),
  ...                                  -- thousands at once
  ('Zoe',   'z@x.com');</code></pre>
A batch size of 500-5000 is the typical sweet spot. Watch out for <code>max_allowed_packet</code> (default 64MB) which caps statement size.</li>

  <li><strong>LOAD DATA INFILE</strong> &mdash; the fastest path for huge imports. 5-20x faster than even multi-row INSERTs because it bypasses SQL parsing per row.
<pre><code>LOAD DATA LOCAL INFILE '/tmp/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;</code></pre></li>

  <li><strong>Wrap in a transaction</strong> &mdash; without an explicit transaction, every <code>INSERT</code> auto-commits, fsyncing to disk. One transaction containing the whole load is dramatically faster.
<pre><code>SET autocommit = 0;
START TRANSACTION;
-- ... thousands of inserts ...
COMMIT;</code></pre></li>

  <li><strong>Disable per-row checks during the load</strong>:
<pre><code>SET unique_checks = 0;
SET foreign_key_checks = 0;
-- ... bulk insert ...
SET unique_checks = 1;
SET foreign_key_checks = 1;
-- Indexes still updated, but per-row constraint validation skipped.</code></pre>
Only do this when you trust the data; constraint violations now fail at COMMIT, not insert time.</li>

  <li><strong>Sort by primary key before inserting</strong> &mdash; InnoDB&rsquo;s clustered index works best with sequential PKs. Random or reverse order fragments the B-tree and causes page splits.</li>

  <li><strong>Drop secondary indexes, load, recreate</strong> &mdash; for one-shot huge initial loads, this is faster than maintaining indexes per row. Don&rsquo;t do it for incremental loads.</li>
</ul>

<p><strong>Tuning knobs</strong>:</p>
<ul>
  <li><code>innodb_flush_log_at_trx_commit = 2</code> &mdash; trades a tiny window of durability for big throughput gains during loads. Reset to 1 for normal operation.</li>
  <li><code>bulk_insert_buffer_size</code> &mdash; legacy MyISAM setting; ignore for InnoDB.</li>
  <li><code>innodb_buffer_pool_size</code> sized so the table&rsquo;s indexes fit during the load.</li>
</ul>

<p><strong>Application-level</strong>: connection pooling, prepared statements, parallelism (multiple workers loading disjoint key ranges). Tools: <strong>mysqlimport</strong> CLI, <strong>mysqlsh util.importTable</strong> (parallel chunked load), <strong>Apache Sqoop</strong> for warehouse imports.</p>
'''

ANSWERS[38] = r'''
<p>Both <code>UNION</code> and <code>UNION ALL</code> combine the result sets of two or more queries vertically &mdash; same columns, stacked rows. The difference is duplicate handling:</p>

<table>
  <tr><th></th><th>UNION</th><th>UNION ALL</th></tr>
  <tr><td>Duplicates</td><td>Removed</td><td>Kept</td></tr>
  <tr><td>Sort/dedupe pass</td><td>Yes &mdash; needed to find duplicates</td><td>No</td></tr>
  <tr><td>Performance</td><td>Slower</td><td>Faster</td></tr>
  <tr><td>Default to use</td><td>Only when you genuinely need deduplication</td><td>Almost always</td></tr>
</table>

<pre><code>-- UNION ALL: stacks results, keeps everything
(SELECT id, name FROM customers WHERE country = 'US')
UNION ALL
(SELECT id, name FROM customers WHERE country = 'UK');

-- UNION: stacks then dedupes
(SELECT email FROM employees)
UNION
(SELECT email FROM contractors);
-- emails appearing in both are returned once</code></pre>

<p><strong>Constraints both share</strong>:</p>
<ul>
  <li>Each <code>SELECT</code> must produce the same number of columns.</li>
  <li>Column types should be compatible (MySQL coerces as needed).</li>
  <li>Column names come from the <em>first</em> query; aliases on later queries are ignored.</li>
  <li>To sort the combined result, put <code>ORDER BY</code> at the very end &mdash; it applies to the whole UNION.</li>
</ul>

<p><strong>Performance details</strong>: <code>UNION</code> implies a full sort or hash distinct over the combined set. On a 10M+ row union, that&rsquo;s a substantial cost &mdash; multiple disk-spilling temp tables, lots of CPU. <code>UNION ALL</code> simply concatenates and is essentially free in comparison.</p>

<p><strong>Safe rule</strong>: default to <code>UNION ALL</code>. Use <code>UNION</code> only when:</p>
<ul>
  <li>You genuinely expect duplicates and need them removed.</li>
  <li>The duplicate-removal cost is acceptable for the volume.</li>
</ul>

<p>If duplicates would be unusual but possible, often it&rsquo;s cheaper to use <code>UNION ALL</code> and let the application handle them, or wrap with <code>SELECT DISTINCT (UNION ALL)</code> only on the result columns that need deduplication.</p>

<p><strong>Common patterns</strong>:</p>

<pre><code>-- Reporting: combine current and archived data
SELECT id, action, created_at FROM events_current
UNION ALL
SELECT id, action, created_at FROM events_archive
WHERE created_at &gt;= '2024-01-01'
ORDER BY created_at DESC LIMIT 100;

-- Adding a synthetic header row
SELECT 'Total' AS label, SUM(amount) AS value FROM transactions
UNION ALL
SELECT category, SUM(amount) FROM transactions GROUP BY category;</code></pre>

<p><strong>FULL OUTER JOIN emulation</strong>: MySQL doesn&rsquo;t support <code>FULL OUTER JOIN</code> directly. <code>LEFT JOIN ... UNION ... RIGHT JOIN</code> is the standard workaround.</p>
'''

ANSWERS[39] = r'''
<p>Disk I/O is usually the ultimate bottleneck for OLTP workloads. The optimization strategy is fitting the working set in memory (so most reads are RAM hits) and batching writes (so each fsync amortizes over many changes).</p>

<p><strong>Storage layer choices, biggest impact first</strong>:</p>

<ul>
  <li><strong>NVMe SSDs over SATA SSDs over HDDs</strong> &mdash; the difference between NVMe and HDD is 100-1000x random I/O throughput. For any production OLTP workload in 2026, NVMe is table stakes; HDDs only for cold archive.</li>
  <li><strong>Local instance storage vs network-attached</strong> &mdash; cloud instance-local NVMe (AWS i4i, GCP local SSD) outperforms network-attached storage for IOPS-bound workloads at lower latency. Trade-off: data is lost when the instance terminates, so it&rsquo;s for replicas or rebuildable shards.</li>
</ul>

<p><strong>InnoDB tuning</strong>:</p>

<table>
  <tr><th>Variable</th><th>Effect</th><th>Guidance</th></tr>
  <tr><td><code>innodb_buffer_pool_size</code></td><td>RAM cache for data + indexes</td><td>50-70% of system RAM on dedicated DB hosts</td></tr>
  <tr><td><code>innodb_flush_log_at_trx_commit</code></td><td>How often redo log fsyncs</td><td>1 = full ACID. 2 = log written on commit, fsync per second &mdash; small durability window, big throughput gain</td></tr>
  <tr><td><code>innodb_log_file_size</code></td><td>Redo log size</td><td>Larger = less frequent checkpoint flushes; 1-2 GB typical</td></tr>
  <tr><td><code>innodb_io_capacity</code></td><td>Hint to InnoDB about disk speed</td><td>For NVMe, 5000-20000+; throttles background I/O</td></tr>
  <tr><td><code>innodb_flush_method</code></td><td>How writes hit disk</td><td><code>O_DIRECT</code> on Linux to bypass OS file cache (avoids double-buffering)</td></tr>
</table>

<p><strong>Schema-level wins</strong>:</p>

<ul>
  <li><strong>Right-size data types</strong> &mdash; smaller rows = more rows per page = better cache density.</li>
  <li><strong>Avoid wide TEXT/BLOB columns</strong> in main tables &mdash; they&rsquo;re stored off-page; vertical partition into a sidecar table when not always needed.</li>
  <li><strong>Sequential primary keys</strong> &mdash; UUID v4 (random) PKs cause page splits across the entire B-tree on insert. Use BIGINT autoincrement, ULID, UUIDv7, or KSUID for time-ordered keys.</li>
  <li><strong>Drop unused indexes</strong> &mdash; every index doubles or triples write I/O.</li>
</ul>

<p><strong>Diagnose I/O pressure</strong>:</p>

<pre><code># OS-level
iostat -x 1            # %util, await, IOPS per device
vmstat 1               # bi/bo (block in/out)

-- MySQL
SHOW ENGINE INNODB STATUS\G    -- "Pending normal aio reads/writes"
SELECT * FROM performance_schema.file_summary_by_event_name
WHERE EVENT_NAME LIKE '%file/innodb%'
ORDER BY SUM_TIMER_WAIT DESC LIMIT 10;</code></pre>

<p>If <code>%util</code> on the data disk stays above 80%, the system is I/O bound &mdash; tune the buffer pool, add memory, or move to faster storage.</p>
'''

ANSWERS[40] = r'''
<p>Foreign keys enforce referential integrity at the database level: a row in the child table must reference an existing row in the parent table. The DB rejects orphan inserts and (depending on the action) cascades or restricts deletes/updates.</p>

<pre><code>CREATE TABLE orders (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  total       DECIMAL(10, 2) NOT NULL,

  CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  INDEX idx_customer (customer_id)
) ENGINE=InnoDB;</code></pre>

<p>InnoDB enforces FKs; MyISAM accepts the syntax and silently ignores them &mdash; another reason to use InnoDB everywhere.</p>

<p><strong>Referential actions</strong>:</p>

<table>
  <tr><th>Action</th><th>What happens when the parent row is deleted/updated</th></tr>
  <tr><td><code>RESTRICT</code> (default)</td><td>Operation fails if any child rows exist</td></tr>
  <tr><td><code>NO ACTION</code></td><td>Same as RESTRICT in InnoDB</td></tr>
  <tr><td><code>CASCADE</code></td><td>Children are deleted/updated to match</td></tr>
  <tr><td><code>SET NULL</code></td><td>Children&rsquo;s FK column is set to NULL (column must be nullable)</td></tr>
  <tr><td><code>SET DEFAULT</code></td><td>Parsed but not enforced in InnoDB</td></tr>
</table>

<p><strong>Why FKs matter</strong>:</p>

<ul>
  <li><strong>Data integrity</strong> &mdash; the database guarantees relationships are consistent, regardless of which application writes the data. Bug in app code? Bad migration script? FKs catch it.</li>
  <li><strong>Self-documentation</strong> &mdash; the schema declares the data model; tools can generate ER diagrams; new developers understand structure faster.</li>
  <li><strong>Cascading cleanup</strong> &mdash; <code>ON DELETE CASCADE</code> handles dependent-row cleanup automatically; no application code needs to remember.</li>
</ul>

<p><strong>The standard objections (and rebuttals)</strong>:</p>

<ul>
  <li><em>"They slow down writes."</em> &mdash; True, but the cost is small (one indexed lookup per insert/update). Indexes on the FK columns are essential; missing them is the actual cause of slowness people attribute to FKs.</li>
  <li><em>"They complicate sharding."</em> &mdash; Sharding breaks FKs across shards; this is real. Within a shard they remain useful.</li>
  <li><em>"The application validates this already."</em> &mdash; Until it doesn&rsquo;t, due to a bug or race condition. Defense in depth is cheaper than an emergency data-cleanup project.</li>
</ul>

<p><strong>Operational notes</strong>:</p>
<ul>
  <li>Always index the FK column &mdash; CASCADE deletes scan otherwise.</li>
  <li>Bulk loads can disable FK checks: <code>SET foreign_key_checks = 0;</code> &mdash; verify integrity manually afterward.</li>
  <li>FKs prevent dropping referenced tables: drop the FK first or use <code>SET FOREIGN_KEY_CHECKS = 0</code> for migrations.</li>
  <li>Modern frameworks (Prisma, Drizzle, ActiveRecord) generate FKs by default in migrations &mdash; keep them.</li>
</ul>
'''

ANSWERS[41] = r'''
<p><strong>Denormalization</strong> is the deliberate addition of redundant data to a normalized schema to optimize for read patterns. It&rsquo;s a tactical choice, not a starting point.</p>

<p><strong>Advantages</strong>:</p>

<ul>
  <li><strong>Faster reads</strong> &mdash; precomputed aggregates and embedded copies eliminate joins and aggregation. A dashboard that took 200ms over five JOINs becomes 5ms over a single indexed lookup.</li>
  <li><strong>Simpler queries</strong> &mdash; one table, fewer joins, easier for application developers and reporting tools.</li>
  <li><strong>Lower CPU for read paths</strong> &mdash; relevant when the same expensive query runs millions of times.</li>
  <li><strong>Independent scaling of hot data</strong> &mdash; denormalized read tables can be moved to replicas or cached layers without affecting transactional schema.</li>
</ul>

<p><strong>Disadvantages</strong>:</p>

<ul>
  <li><strong>Update complexity</strong> &mdash; every change to source data must update every denormalized copy. Easy to miss; bugs cause silent inconsistencies that compound over time.</li>
  <li><strong>Storage overhead</strong> &mdash; the same fact is stored multiple times. Sometimes 2-3x storage cost.</li>
  <li><strong>Consistency window</strong> &mdash; denormalized data is usually not updated atomically with the source; reads can see stale values until the next refresh.</li>
  <li><strong>Schema rigidity</strong> &mdash; renaming a column now means coordinated updates across many places. Migrations get more painful.</li>
</ul>

<p><strong>Common denormalization patterns</strong>:</p>

<table>
  <tr><th>Pattern</th><th>Use case</th></tr>
  <tr><td>Embedded columns</td><td>Storing <code>customer_name</code> on <code>orders</code> to avoid joining customers in the order list</td></tr>
  <tr><td>Cached counters</td><td><code>order_count</code> on <code>users</code> instead of <code>SELECT COUNT(*) FROM orders</code> on every page</td></tr>
  <tr><td>Materialized aggregates</td><td>Pre-aggregated daily/monthly summary tables for analytics</td></tr>
  <tr><td>Generated columns</td><td>InnoDB STORED generated columns &mdash; computed once, indexed normally</td></tr>
  <tr><td>Search indexes</td><td>Mirroring searchable fields to Elasticsearch / Meilisearch / Typesense</td></tr>
</table>

<p><strong>Maintenance strategies for denormalized data</strong>:</p>

<ul>
  <li><strong>Triggers</strong> &mdash; in-database, automatic. Pro: never forgotten. Con: hidden complexity, every write pays the cost.</li>
  <li><strong>Application-layer dual-write</strong> &mdash; explicit in code; testable. Risk: missed paths or out-of-sync on failure.</li>
  <li><strong>Scheduled refresh</strong> &mdash; periodic full or incremental rebuild. Suits eventual-consistency tolerant cases.</li>
  <li><strong>CDC streaming</strong> &mdash; <strong>Debezium</strong> reads binlog, projections updated downstream. Cleanest but most infrastructure.</li>
</ul>

<p><strong>The pragmatic rule</strong>: <em>normalize until it hurts; denormalize until it works</em>. Start fully normalized for clarity and integrity. Identify specific hot read paths via metrics. Denormalize those paths surgically &mdash; not the whole schema. Document each denormalization with a comment explaining the why and the maintenance strategy.</p>
'''

ANSWERS[42] = r'''
<p>Zero-or-minimal-downtime migration uses the <strong>expand-contract pattern</strong>: every change is broken into deploys that are individually reversible and coexist with both old and new application code. No single moment requires both DB and application to switch atomically.</p>

<p><strong>The general phases for any column rename, type change, or table restructure</strong>:</p>

<ol>
  <li><strong>Expand</strong> &mdash; add the new column / table alongside the old. Both schemas coexist. App still uses old schema.</li>
  <li><strong>Backfill</strong> &mdash; populate the new structure from the old, in batches, online. Triggers or application dual-write keeps them in sync going forward.</li>
  <li><strong>Migrate readers</strong> &mdash; deploy app code reading the new structure. Old structure still receives writes via dual-write.</li>
  <li><strong>Migrate writers</strong> &mdash; deploy app code writing to the new structure (and stop dual-writing).</li>
  <li><strong>Verify</strong> &mdash; validate consistency for some bake-in time.</li>
  <li><strong>Contract</strong> &mdash; drop the old structure.</li>
</ol>

<p>Each step is an independent deploy that&rsquo;s safe to roll back. No two steps must happen simultaneously.</p>

<p><strong>Online DDL for the heavy operations</strong>:</p>

<ul>
  <li><strong>ALGORITHM=INSTANT</strong> (MySQL 8) &mdash; metadata-only changes (adding a column at the end, changing a column default) finish in milliseconds. Always specify <code>ALGORITHM=INSTANT</code> explicitly to fail fast if the change can&rsquo;t be instant.</li>
  <li><strong>pt-online-schema-change</strong> (Percona) &mdash; copies the table in the background using triggers to capture concurrent changes; atomically swaps at the end. Used widely on multi-TB tables.</li>
  <li><strong>gh-ost</strong> (GitHub) &mdash; same goal without triggers; reads binlog instead. Throttles based on replica lag.</li>
  <li><strong>MySQL Workbench / SchemaHero / Atlas</strong> &mdash; GitOps-style schema management.</li>
</ul>

<p><strong>Replica-driven cutovers</strong> &mdash; for major version upgrades or hardware changes:</p>

<ol>
  <li>Build a new replica on the target version / hardware.</li>
  <li>Let it catch up to the source.</li>
  <li>Stop application writes, wait for the replica to fully apply, promote the replica, repoint the application.</li>
  <li>Total downtime: seconds, not hours.</li>
</ol>

<p>Cloud-managed databases (RDS, Cloud SQL, PlanetScale, Aurora) automate large parts of this.</p>

<p><strong>Critical practices</strong>:</p>

<ul>
  <li><strong>Test the migration on a recent production snapshot</strong>. Lock-time surprises only show up on real data volumes.</li>
  <li><strong>Have a rollback plan for every step</strong>. "Roll forward through" is not a rollback plan.</li>
  <li><strong>Monitor lag and saturation</strong> during long-running migrations. <strong>gh-ost</strong> and <strong>pt-osc</strong> have throttling controls; use them.</li>
  <li><strong>Communicate with stakeholders</strong> &mdash; even "zero-downtime" migrations often involve degraded performance windows.</li>
</ul>

<p>The goal isn&rsquo;t literally zero impact &mdash; it&rsquo;s reducing the irreversible-blast-radius window from hours to seconds.</p>
'''

ANSWERS[43] = r'''
<p><code>mysqldump</code> is the standard logical-backup utility &mdash; produces a SQL script that recreates a database when re-executed. Comes with every MySQL installation; portable across versions and platforms.</p>

<p><strong>Backup essentials</strong>:</p>

<pre><code>mysqldump -u root -p \
  --single-transaction \              # consistent snapshot for InnoDB without locking
  --routines --triggers --events \    # include stored programs (omitted by default!)
  --hex-blob \                        # safer encoding for binary columns
  --set-gtid-purged=ON \              # GTID metadata for replica reseeding
  shop &gt; shop.sql

# Compress on the fly
mysqldump ... shop | gzip &gt; shop.sql.gz

# All databases
mysqldump -u root -p --all-databases --single-transaction --routines --triggers \
    &gt; full_backup.sql

# Single table
mysqldump -u root -p shop users orders &gt; partial.sql

# WHERE filter — partial extract
mysqldump -u root -p --single-transaction \
  --where="created_at &gt;= '2026-01-01'" \
  shop orders &gt; recent_orders.sql</code></pre>

<p><strong>Critical flags</strong>:</p>

<table>
  <tr><th>Flag</th><th>Why</th></tr>
  <tr><td><code>--single-transaction</code></td><td>InnoDB consistent snapshot; <strong>required for hot backups without locking writers</strong></td></tr>
  <tr><td><code>--routines --triggers --events</code></td><td>Include stored programs; default is to skip them</td></tr>
  <tr><td><code>--hex-blob</code></td><td>Encodes BLOBs as hex; survives any text encoding</td></tr>
  <tr><td><code>--set-gtid-purged=ON</code></td><td>GTID-aware replication reseeding</td></tr>
  <tr><td><code>--master-data=2</code></td><td>Records source binlog position in the dump as a comment</td></tr>
  <tr><td><code>--no-data</code></td><td>Schema only; no rows</td></tr>
  <tr><td><code>--no-create-info</code></td><td>Data only; no DDL</td></tr>
</table>

<p><strong>Restore</strong>:</p>

<pre><code>mysql -u root -p shop &lt; shop.sql

# From compressed
gunzip &lt; shop.sql.gz | mysql -u root -p shop

# Speed up large restores
mysql -u root -p shop &lt;&lt; 'EOF'
SET autocommit = 0;
SET unique_checks = 0;
SET foreign_key_checks = 0;
SOURCE shop.sql;
COMMIT;
SET unique_checks = 1;
SET foreign_key_checks = 1;
EOF</code></pre>

<p>Disabling per-row checks drops restore time substantially &mdash; tens of millions of rows in minutes instead of hours.</p>

<p><strong>When to choose alternatives</strong>:</p>

<ul>
  <li><strong>Multi-TB databases</strong> &mdash; <code>mysqldump</code>&rsquo;s single-threaded restore takes hours. <strong>Percona XtraBackup</strong> does physical (file-level) backups that restore in minutes.</li>
  <li><strong>Parallelism</strong> &mdash; <code>mysqlpump</code> (5.7+) uses multiple threads; <code>mysqlsh util.dumpInstance / loadDump</code> in MySQL Shell is the fastest logical option.</li>
  <li><strong>Cloud-managed</strong> &mdash; AWS RDS, Cloud SQL, Aurora handle backups via storage snapshots; near-instant base, continuous binlog backup. Use the platform.</li>
</ul>

<p><strong>Best practices</strong>: encrypt at rest, store offsite (3-2-1 rule), test restore times quarterly. <strong>An untested backup doesn&rsquo;t exist.</strong></p>
'''

ANSWERS[44] = r'''
<p>MySQL security is layered &mdash; network, authentication, authorization, encryption, and auditing each cover a different attack surface. The defense-in-depth principle: assume any one layer might fail.</p>

<p><strong>Network</strong>:</p>

<ul>
  <li><strong>Bind to private interfaces only</strong> &mdash; <code>bind-address = 10.0.0.5</code> (not <code>0.0.0.0</code>). A MySQL server should never be reachable from the public internet.</li>
  <li><strong>Firewall / Security Group</strong> &mdash; allow port 3306 only from application servers. AWS Security Groups, GCP firewall rules, or iptables.</li>
  <li><strong>Require TLS for all connections</strong> &mdash; <code>require_secure_transport = ON</code> rejects unencrypted connections. Use <code>REQUIRE SSL</code> on the user account too.</li>
  <li><strong>Bastion / VPN access</strong> &mdash; humans connect via SSH bastions or VPN, never directly.</li>
</ul>

<p><strong>Authentication</strong>:</p>

<ul>
  <li><strong>Strong passwords</strong> &mdash; use <code>validate_password</code> plugin to enforce complexity. Better: use a secret manager (AWS Secrets Manager, Vault) and rotate.</li>
  <li><strong>Modern auth plugin</strong> &mdash; <code>caching_sha2_password</code> (MySQL 8 default) over the legacy <code>mysql_native_password</code>.</li>
  <li><strong>IAM authentication</strong> in cloud environments &mdash; AWS RDS IAM auth, GCP Cloud SQL IAM. No password to leak; auth via short-lived tokens.</li>
  <li><strong>Disable root remote access</strong> &mdash; <code>'root'@'localhost'</code> only. Never <code>'root'@'%'</code>.</li>
  <li><strong>Drop the anonymous user</strong> and <code>test</code> database from fresh installs (run <code>mysql_secure_installation</code>).</li>
</ul>

<p><strong>Authorization &mdash; principle of least privilege</strong>:</p>

<ul>
  <li>Application user gets <code>SELECT, INSERT, UPDATE, DELETE</code> on its specific database, nothing else.</li>
  <li>Migration user (separate) gets <code>CREATE, ALTER, INDEX, REFERENCES</code> &mdash; used only by deploy pipelines.</li>
  <li>Read-only reporting user gets <code>SELECT</code> &mdash; for analytics and dashboards.</li>
  <li>DBA / admin users are few in number, with strong auth and audit.</li>
</ul>

<p><strong>MySQL 8 roles</strong> simplify managing privileges across many users:</p>

<pre><code>CREATE ROLE 'app_read', 'app_write';
GRANT SELECT ON shop.* TO 'app_read';
GRANT INSERT, UPDATE, DELETE ON shop.* TO 'app_write';
GRANT 'app_read', 'app_write' TO 'app_user'@'%';
SET DEFAULT ROLE ALL TO 'app_user'@'%';</code></pre>

<p><strong>Encryption</strong>:</p>

<ul>
  <li><strong>At rest</strong> &mdash; InnoDB tablespace encryption (<code>encryption='Y'</code>), or storage-level (LUKS, EBS-encrypted volumes, KMS-backed cloud storage).</li>
  <li><strong>In transit</strong> &mdash; TLS 1.2+ for client/server connections and replica/source.</li>
  <li><strong>Backups encrypted</strong> &mdash; the dump file contains the same data; protect it the same way.</li>
</ul>

<p><strong>Auditing</strong>:</p>

<ul>
  <li><strong>MySQL Enterprise Audit</strong> or <strong>Percona Audit Plugin</strong> &mdash; structured logs of connections, queries, schema changes.</li>
  <li><strong>Binary logs</strong> already capture every write; combined with audit they reconstruct any incident.</li>
  <li>Forward to a SIEM (Splunk, Elastic) or cloud-native logging.</li>
</ul>

<p><strong>Application-side</strong>: parameterized queries (always &mdash; never string-concatenated SQL), input validation, ORMs that escape by default, secret management. The OWASP SQL injection cheat sheet is mandatory reading for any team writing SQL-using code.</p>
'''

ANSWERS[45] = r'''
<p>TLS protects MySQL connections from eavesdropping and tampering. In modern deployments it&rsquo;s essentially mandatory: any traffic crossing a network boundary should be encrypted, and most security baselines require it.</p>

<p><strong>Server certificate setup</strong> &mdash; MySQL 8 auto-generates self-signed certs on first start, suitable for development:</p>

<pre><code>SHOW VARIABLES LIKE '%ssl%';
-- ssl_ca:   /var/lib/mysql/ca.pem
-- ssl_cert: /var/lib/mysql/server-cert.pem
-- ssl_key:  /var/lib/mysql/server-key.pem
-- have_ssl: YES</code></pre>

<p>For production, replace these with certs signed by a real CA &mdash; either internal (HashiCorp Vault, cert-manager + Let&rsquo;s Encrypt) or your cloud provider&rsquo;s managed certificates.</p>

<p><strong>Configure in my.cnf</strong>:</p>

<pre><code>[mysqld]
ssl_ca   = /etc/mysql/certs/ca.pem
ssl_cert = /etc/mysql/certs/server-cert.pem
ssl_key  = /etc/mysql/certs/server-key.pem

require_secure_transport = ON           # reject unencrypted connections
tls_version = TLSv1.2,TLSv1.3           # force modern TLS
admin_tls_version = TLSv1.3             # for the admin port</code></pre>

<p><strong>Per-user TLS requirements</strong>:</p>

<pre><code>-- Connection must use TLS
ALTER USER 'app_user'@'%' REQUIRE SSL;

-- Stricter: must present a valid client certificate
ALTER USER 'admin'@'%' REQUIRE X509;

-- Strictest: client cert must match specific subject
ALTER USER 'admin'@'%' REQUIRE
  SUBJECT '/C=US/ST=CA/CN=admin-cert' AND
  ISSUER  '/C=US/CN=Internal CA';</code></pre>

<p><strong>Client connection</strong>:</p>

<pre><code># mysql client
mysql -u app_user -p -h db.internal \
  --ssl-mode=REQUIRED \
  --ssl-ca=/etc/ssl/ca.pem

# Application — Node.js mysql2
const conn = mysql.createConnection({
  host: 'db.internal', user: 'app', database: 'shop',
  ssl: { ca: fs.readFileSync('/etc/ssl/ca.pem') }
});

# Application — JDBC
"jdbc:mysql://db.internal:3306/shop?useSSL=true&requireSSL=true&verifyServerCertificate=true"</code></pre>

<p><strong>--ssl-mode levels</strong> for the client:</p>

<table>
  <tr><th>Mode</th><th>Behavior</th></tr>
  <tr><td>DISABLED</td><td>No TLS</td></tr>
  <tr><td>PREFERRED (default)</td><td>TLS if available, else plain &mdash; vulnerable to MITM</td></tr>
  <tr><td>REQUIRED</td><td>TLS required, but no certificate verification &mdash; still MITM-vulnerable</td></tr>
  <tr><td>VERIFY_CA</td><td>TLS + verify certificate is signed by the configured CA</td></tr>
  <tr><td>VERIFY_IDENTITY</td><td>TLS + CA + hostname matches certificate subject</td></tr>
</table>

<p><strong>Use VERIFY_IDENTITY in production</strong> &mdash; lower modes don&rsquo;t protect against MITM attacks.</p>

<p><strong>Replication channels</strong> need TLS too:</p>

<pre><code>CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = 'primary.internal',
  SOURCE_USER = 'replicator',
  SOURCE_SSL = 1,
  SOURCE_SSL_CA = '/etc/ssl/ca.pem',
  SOURCE_SSL_VERIFY_SERVER_CERT = 1;</code></pre>

<p><strong>Cloud reality</strong>: AWS RDS / Aurora / Cloud SQL provide managed TLS by default; download the provider&rsquo;s CA bundle and configure clients to verify against it. Letting platforms handle cert rotation is a major operational win.</p>
'''

ANSWERS[46] = r'''
<p>MySQL 8 introduced <strong>roles</strong> &mdash; named bundles of privileges that can be granted to users. Before 8, every user had to be granted privileges individually; managing 100 app servers each with its own user meant 100 separate <code>GRANT</code> statements.</p>

<pre><code>-- Define roles by intent
CREATE ROLE 'app_read', 'app_write', 'app_admin';

GRANT SELECT ON shop.* TO 'app_read';
GRANT INSERT, UPDATE, DELETE ON shop.* TO 'app_write';
GRANT CREATE, ALTER, DROP, INDEX ON shop.* TO 'app_admin';

-- Compose roles
GRANT 'app_read' TO 'app_write';   -- writers also read

-- Assign to users
CREATE USER 'webapp'@'%' IDENTIFIED BY '...';
GRANT 'app_write' TO 'webapp'@'%';

-- Activate roles automatically on login
SET DEFAULT ROLE ALL TO 'webapp'@'%';</code></pre>

<p>Now changing what writers can do is one statement: <code>GRANT EXECUTE ON shop.* TO 'app_write'</code> &mdash; every user with the role inherits the new privilege.</p>

<p><strong>The principle of least privilege</strong> &mdash; canonical role layout for an application:</p>

<table>
  <tr><th>Role</th><th>Used by</th><th>Privileges</th></tr>
  <tr><td><code>app_read</code></td><td>Read replicas, reporting tools</td><td><code>SELECT</code> on app schema</td></tr>
  <tr><td><code>app_write</code></td><td>Web server / API</td><td><code>SELECT, INSERT, UPDATE, DELETE</code></td></tr>
  <tr><td><code>app_admin</code></td><td>Migration runner / deploy pipeline</td><td>+ DDL on the app schema</td></tr>
  <tr><td><code>backup</code></td><td>Backup tooling</td><td><code>SELECT, LOCK TABLES, RELOAD, REPLICATION CLIENT, EVENT</code></td></tr>
  <tr><td><code>replicator</code></td><td>Replicas connecting to source</td><td><code>REPLICATION SLAVE</code></td></tr>
  <tr><td><code>monitor</code></td><td>Metrics tools (mysqld_exporter)</td><td><code>PROCESS, REPLICATION CLIENT, SELECT</code> on perf schema</td></tr>
</table>

<p><strong>Activate roles per session</strong>:</p>

<pre><code>-- Use only specific roles for the current connection
SET ROLE 'app_read';

-- Activate all granted roles
SET ROLE ALL;

-- See current active roles
SELECT CURRENT_ROLE();</code></pre>

<p>Applications usually want default-on roles (set with <code>SET DEFAULT ROLE</code>); admins and humans benefit from explicit role activation as a defense against accidental destructive operations.</p>

<p><strong>Inspecting privileges</strong>:</p>

<pre><code>SHOW GRANTS FOR 'webapp'@'%';
SHOW GRANTS FOR 'webapp'@'%' USING 'app_write';   -- expand role contents

-- Programmatic
SELECT * FROM mysql.role_edges;                    -- role hierarchy
SELECT * FROM information_schema.applicable_roles; -- what current user can SET</code></pre>

<p><strong>Cloud-native alternatives</strong>:</p>

<ul>
  <li><strong>AWS RDS IAM authentication</strong> &mdash; map IAM principals to MySQL users; no password, short-lived auth tokens.</li>
  <li><strong>GCP Cloud SQL IAM</strong> &mdash; similar.</li>
  <li><strong>Azure Active Directory</strong> &mdash; AD auth for Azure Database for MySQL.</li>
  <li><strong>HashiCorp Vault dynamic secrets</strong> &mdash; Vault generates short-lived MySQL credentials per request; no static passwords stored anywhere.</li>
</ul>

<p>For new production deployments, prefer ephemeral credentials over long-lived passwords. Roles still apply &mdash; the credential identifies who you are; the role determines what you can do.</p>
'''

ANSWERS[47] = r'''
<p>Two distinct mechanisms with overlapping use cases &mdash; both protect against SQL injection and reduce parsing overhead, but at different layers.</p>

<table>
  <tr><th>Aspect</th><th>Stored procedure</th><th>Prepared statement</th></tr>
  <tr><td>Where defined</td><td>In the database, persistent</td><td>In the connection, per-session</td></tr>
  <tr><td>Lifetime</td><td>Survives across connections</td><td>Per-connection; vanishes on disconnect</td></tr>
  <tr><td>Invocation</td><td><code>CALL my_proc(...)</code></td><td><code>EXECUTE stmt USING @v</code></td></tr>
  <tr><td>Logic</td><td>Multi-statement, control flow, loops</td><td>One parameterized SQL statement</td></tr>
  <tr><td>SQL injection</td><td>Safe if parameters are used correctly</td><td>Safe by design</td></tr>
  <tr><td>Performance</td><td>Reduces network round-trips for multi-step ops</td><td>Cached plan; reused for repeated execution</td></tr>
</table>

<p><strong>Stored procedure example</strong>:</p>

<pre><code>DELIMITER //
CREATE PROCEDURE place_order(
  IN p_user_id INT,
  IN p_amount DECIMAL(10,2),
  OUT p_order_id INT
)
BEGIN
  START TRANSACTION;
  INSERT INTO orders (user_id, amount) VALUES (p_user_id, p_amount);
  SET p_order_id = LAST_INSERT_ID();
  UPDATE users SET order_count = order_count + 1 WHERE id = p_user_id;
  COMMIT;
END //
DELIMITER ;

CALL place_order(42, 99.99, @new_order_id);
SELECT @new_order_id;</code></pre>

<p>Procedures encapsulate multi-statement business logic in the database. Useful when:</p>
<ul>
  <li>Multiple application languages need to invoke the same logic.</li>
  <li>Network latency matters &mdash; one CALL replaces 5+ round-trips.</li>
  <li>The logic involves cursors or row-by-row processing.</li>
  <li>Permissions can be tighter (grant <code>EXECUTE</code> on procedures, not on tables).</li>
</ul>

<p><strong>Prepared statement example</strong>:</p>

<pre><code>PREPARE find_user FROM 'SELECT id, name FROM users WHERE email = ? AND active = ?';
SET @email = 'alice@x.com', @active = 1;
EXECUTE find_user USING @email, @active;
DEALLOCATE PREPARE find_user;

-- Application code (mysql2 in Node.js)
const [rows] = await conn.execute(
  'SELECT id, name FROM users WHERE email = ? AND active = ?',
  ['alice@x.com', 1]
);</code></pre>

<p>Almost every database driver uses prepared statements transparently when you pass <code>?</code> placeholders. They&rsquo;re the standard way to issue parameterized SQL from application code.</p>

<p><strong>Why prepared statements are essentially mandatory</strong>:</p>

<ul>
  <li><strong>SQL injection prevention</strong> &mdash; values are sent separately from SQL text; can&rsquo;t be reinterpreted as SQL.</li>
  <li><strong>Cached query plan</strong> &mdash; the optimizer parses and plans once, executes many times. For a query running 1000/sec, this saves real CPU.</li>
  <li><strong>Type safety</strong> &mdash; parameters are typed; no quoting / escaping bugs.</li>
</ul>

<p><strong>Modern stance</strong>: use prepared statements universally for all application queries. Use stored procedures sparingly &mdash; only when business logic genuinely belongs in the database (high network cost, multi-app reuse, security boundary). Putting business logic in stored procedures often complicates testing, version control, and deployment; modern apps overwhelmingly prefer code-side logic with parameterized queries.</p>
'''

ANSWERS[48] = r'''
<p><strong>Performance Schema</strong> is MySQL&rsquo;s built-in observability subsystem &mdash; structured tables exposing what the server is doing right now and what it has done. Replaces ad-hoc SHOW commands with relational, queryable data.</p>

<p><strong>Setup</strong> &mdash; enabled by default since 5.6. Verify:</p>

<pre><code>SHOW VARIABLES LIKE 'performance_schema';   -- ON

-- See instrumented producers
SELECT * FROM performance_schema.setup_instruments LIMIT 10;
-- Enable specific instruments
UPDATE performance_schema.setup_instruments
SET ENABLED = 'YES', TIMED = 'YES'
WHERE NAME LIKE 'statement/%';</code></pre>

<p><strong>The most useful tables</strong>:</p>

<table>
  <tr><th>Table</th><th>What it shows</th></tr>
  <tr><td><code>events_statements_summary_by_digest</code></td><td>Aggregated stats per query template &mdash; the slow-query hit list</td></tr>
  <tr><td><code>events_statements_history_long</code></td><td>Recent statements with full SQL and timing</td></tr>
  <tr><td><code>table_io_waits_summary_by_table</code></td><td>I/O cost per table &mdash; what&rsquo;s hot</td></tr>
  <tr><td><code>file_summary_by_event_name</code></td><td>I/O cost per file (data, log, temp)</td></tr>
  <tr><td><code>data_locks</code> / <code>data_lock_waits</code></td><td>Current row/gap locks and waits</td></tr>
  <tr><td><code>memory_summary_global_by_event_name</code></td><td>Memory allocation by component</td></tr>
  <tr><td><code>threads</code></td><td>Per-thread state, current statement, OS thread ID</td></tr>
  <tr><td><code>replication_*</code></td><td>Replica health, applier worker status, lag</td></tr>
</table>

<p><strong>The "top 10 worst queries" go-to query</strong>:</p>

<pre><code>SELECT
  SUBSTRING(digest_text, 1, 80) AS query,
  count_star                    AS execs,
  ROUND(sum_timer_wait/1e12, 1) AS total_seconds,
  ROUND(avg_timer_wait/1e9, 2)  AS avg_ms,
  sum_rows_examined             AS rows_examined,
  sum_rows_sent                 AS rows_sent
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC
LIMIT 10;</code></pre>

<p>Identifies the queries consuming the most time across all executions &mdash; the right targets for optimization. <code>rows_examined / rows_sent</code> ratio identifies queries scanning far more rows than they return (missing indexes).</p>

<p><strong>The sys schema &mdash; Performance Schema for humans</strong>: pre-built views with friendlier names. <code>sys.statement_analysis</code>, <code>sys.schema_unused_indexes</code>, <code>sys.io_global_by_file_by_bytes</code> &mdash; ready-to-use queries that wrap raw Performance Schema data:</p>

<pre><code>SELECT * FROM sys.schema_unused_indexes;          -- candidates to drop
SELECT * FROM sys.io_global_by_file_by_bytes;     -- I/O hotspots
SELECT * FROM sys.x$schema_table_lock_waits;      -- table-level lock contention
SELECT * FROM sys.statement_analysis LIMIT 10;    -- slow query analysis</code></pre>

<p><strong>Overhead consideration</strong>: Performance Schema isn&rsquo;t free &mdash; full instrumentation costs ~5-10% on busy servers. Default settings are tuned for low overhead; enabling history-long tables (<code>events_statements_history_long</code>) for many event types raises memory use. Inspect <code>performance_schema.setup_consumers</code> and disable consumers you don&rsquo;t use.</p>

<p><strong>External tooling</strong> consumes Performance Schema data: <strong>Percona Monitoring &amp; Management (PMM)</strong>, <strong>Datadog</strong>, <strong>Prometheus + mysqld_exporter</strong>, <strong>New Relic</strong>, <strong>SolarWinds DPA</strong>. They turn raw tables into trends, alerts, and query-level analysis. For self-hosted MySQL in 2026, Prometheus + Grafana is the standard open-source stack.</p>
'''

ANSWERS[49] = r'''
<p>Audit logging captures who did what, when, and from where &mdash; essential for compliance (PCI-DSS, HIPAA, SOC 2, GDPR) and incident investigation. <strong>MySQL has no native audit log</strong>; pick from several mature plugins or external systems.</p>

<p><strong>Plugin options</strong>:</p>

<table>
  <tr><th>Plugin</th><th>Source</th><th>License</th></tr>
  <tr><td>MySQL Enterprise Audit</td><td>Oracle</td><td>Commercial only</td></tr>
  <tr><td>Percona Audit Log Plugin</td><td>Percona Server</td><td>GPL, free</td></tr>
  <tr><td>MariaDB Audit Plugin</td><td>MariaDB &mdash; works on Oracle MySQL too</td><td>GPL, free</td></tr>
  <tr><td>McAfee MySQL Audit Plugin</td><td>open source</td><td>GPL</td></tr>
</table>

<p>For self-hosted Oracle MySQL Community Edition, the MariaDB Audit Plugin is the most common free choice. Percona Server bundles its own. Cloud-managed services (RDS, Aurora) provide audit logs natively.</p>

<p><strong>Setup &mdash; MariaDB plugin example</strong>:</p>

<pre><code>INSTALL PLUGIN server_audit SONAME 'server_audit.so';

SET GLOBAL server_audit_logging         = ON;
SET GLOBAL server_audit_events          = 'CONNECT,QUERY,TABLE';
SET GLOBAL server_audit_file_path       = '/var/log/mysql/audit.log';
SET GLOBAL server_audit_file_rotate_size = 1000000000;   -- 1GB
SET GLOBAL server_audit_file_rotations  = 10;

-- Persist
SET PERSIST server_audit_logging = ON;</code></pre>

<p><strong>Output format</strong> &mdash; one line per event, structured:</p>

<pre><code>20260427 14:32:11,db1,app_user,10.0.1.5,3,42,QUERY,shop,'UPDATE orders SET status = ? WHERE id = ?',0
─time─               ─host─ ─user─    ─src ip─  ─event─ ─database─ ─query──── ─retcode</code></pre>

<p>Forward this stream to a log management system &mdash; <strong>Splunk</strong>, <strong>Elastic Stack</strong>, <strong>Datadog</strong>, <strong>Grafana Loki</strong>, or a SIEM. Run regular automated checks: privilege escalations, schema changes outside change windows, queries from unexpected source IPs, off-hours admin access.</p>

<p><strong>Application-level audit columns</strong> &mdash; complementary, not a replacement:</p>

<pre><code>ALTER TABLE orders
  ADD COLUMN created_by INT,
  ADD COLUMN updated_by INT,
  ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;</code></pre>

<p>Adds a "who-touched-this" column at the schema level. Triggers can populate <code>created_by / updated_by</code> from session variables set by the application.</p>

<p><strong>History tables for sensitive data</strong> &mdash; full row-level changelog using triggers (covered in Q69) or <strong>Debezium</strong> CDC streaming binlog events to a downstream audit store.</p>

<p><strong>What to log</strong> &mdash; balance compliance requirements with log volume:</p>

<ul>
  <li><strong>Always</strong>: connection events (success/failure), schema changes (DDL), privilege grants/revokes.</li>
  <li><strong>Often</strong>: writes to sensitive tables (PII, financial), admin queries.</li>
  <li><strong>Selectively</strong>: all queries (high volume; useful in regulated environments).</li>
  <li><strong>Avoid</strong>: logging values containing sensitive data (passwords, tokens, full credit card numbers) &mdash; redaction should happen at the audit-plugin layer.</li>
</ul>

<p><strong>Retention</strong>: defined by policy (often 1-7 years). Cold-storage compress and offload aged audit logs (S3 Glacier) rather than dropping.</p>
'''

ANSWERS[50] = r'''
<p>Hierarchical data &mdash; org charts, category trees, comment threads, file systems &mdash; doesn&rsquo;t map cleanly to flat relational tables. Several patterns trade off query simplicity, write cost, and how deep the hierarchy can go.</p>

<table>
  <tr><th>Pattern</th><th>Schema</th><th>Read cost</th><th>Write cost</th></tr>
  <tr><td>Adjacency list</td><td>each row stores parent_id</td><td>Recursive CTE per query</td><td>O(1) for any change</td></tr>
  <tr><td>Path enumeration</td><td>materialize path (e.g., '/1/4/12/')</td><td>O(1) ancestor; LIKE for descendants</td><td>Update path on subtree move</td></tr>
  <tr><td>Nested set</td><td>each row stores (left, right) tree visit numbers</td><td>O(1) descendants via range</td><td>Inserts shift many rows</td></tr>
  <tr><td>Closure table</td><td>separate (ancestor, descendant, depth) table</td><td>O(1) any relationship via index</td><td>O(d) per insert (d = depth)</td></tr>
</table>

<p><strong>Adjacency list &mdash; the default starting point</strong>:</p>

<pre><code>CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  manager_id INT,
  FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- Walk the tree with a recursive CTE (MySQL 8+)
WITH RECURSIVE tree AS (
  SELECT id, name, manager_id, 0 AS depth FROM employees WHERE id = 100
  UNION ALL
  SELECT e.id, e.name, e.manager_id, t.depth + 1
  FROM employees e JOIN tree t ON e.manager_id = t.id
)
SELECT * FROM tree;</code></pre>

<p>Simple to write to, recursive CTE handles reads. Default choice for most application data.</p>

<p><strong>Closure table &mdash; for read-heavy hierarchies queried thousands of times per second</strong>:</p>

<pre><code>CREATE TABLE category_closure (
  ancestor   INT NOT NULL,
  descendant INT NOT NULL,
  depth      INT NOT NULL,
  PRIMARY KEY (ancestor, descendant)
);

-- Every category includes itself at depth 0, plus one row per (ancestor, descendant) pair
-- "All descendants of category 5":  SELECT descendant FROM closure WHERE ancestor = 5
-- "Direct children of category 5":  SELECT descendant FROM closure WHERE ancestor = 5 AND depth = 1
-- "Path from root":                SELECT ancestor FROM closure WHERE descendant = 12 ORDER BY depth DESC</code></pre>

<p>Reads are single-index lookups regardless of tree depth; writes maintain triggers or app-side logic to keep closure rows in sync. Used by Ruby on Rails&rsquo; <code>closure_tree</code> gem and similar.</p>

<p><strong>Path enumeration &mdash; pragmatic for shallow file-like hierarchies</strong>:</p>

<pre><code>CREATE TABLE files (
  id INT PRIMARY KEY,
  name VARCHAR(255),
  path VARCHAR(1024)   -- e.g., '/1/4/12/'
);
CREATE INDEX idx_path ON files(path);

-- Descendants
SELECT * FROM files WHERE path LIKE '/1/4/%';
-- Ancestors  (parse the path string in app code or use a function)</code></pre>

<p><strong>Document/JSON for very dynamic structures</strong> &mdash; nested JSON in a single column. Easy for trees that aren&rsquo;t queried by hierarchy structure (just rendered whole), unwieldy for relational queries.</p>

<p><strong>Practical guidance</strong>: start with adjacency list. The recursive CTE handles 95% of needs. Move to closure table only when reads are demonstrably bottlenecked &mdash; the implementation overhead is real. For deep hierarchies in graph-shape (many-to-many), consider a graph database (<strong>Neo4j</strong>) or PostgreSQL with <code>ltree</code>.</p>
'''

ANSWERS[51] = r'''
<p>The native <code>JSON</code> data type (MySQL 5.7+) stores semi-structured data with validation, indexing support, and a rich query API. Internally MySQL parses and stores JSON in a compact binary format, not as raw text &mdash; lookups don&rsquo;t reparse, and individual paths can be extracted efficiently.</p>

<pre><code>CREATE TABLE products (
  id    INT PRIMARY KEY,
  name  VARCHAR(200),
  attrs JSON,
  CONSTRAINT chk_attrs CHECK (JSON_VALID(attrs))
);

INSERT INTO products VALUES
  (1, 'Laptop', '{"brand": "Acme", "ram_gb": 16, "ports": ["usb-c", "hdmi"]}'),
  (2, 'Phone',  '{"brand": "Acme", "ram_gb": 8,  "color": "black"}');</code></pre>

<p><strong>Why use JSON columns vs separate tables</strong>:</p>

<ul>
  <li><strong>Sparse, varying-shape attributes</strong> &mdash; products of different categories have different fields; a single key/value table or wide schema is awkward.</li>
  <li><strong>Document-shaped data from APIs</strong> &mdash; webhook payloads, third-party integrations &mdash; preserve the original structure.</li>
  <li><strong>Configuration / metadata</strong> &mdash; per-row settings that aren&rsquo;t queried analytically.</li>
</ul>

<p><strong>Why <em>not</em></strong>:</p>
<ul>
  <li>Fields you filter on heavily belong in real columns &mdash; index performance is better.</li>
  <li>JSON columns can&rsquo;t enforce foreign keys or per-field constraints natively.</li>
  <li>Schema validation is opt-in via <code>JSON_SCHEMA_VALID</code> (8.0.17+); without it, anything valid JSON is accepted.</li>
</ul>

<p><strong>Indexing JSON</strong> &mdash; you can&rsquo;t index a JSON column directly, but you can index expressions over it:</p>

<pre><code>-- Generated column + index for fast filter on attrs.brand
ALTER TABLE products
ADD COLUMN brand VARCHAR(50)
  GENERATED ALWAYS AS (JSON_UNQUOTE(JSON_EXTRACT(attrs, '$.brand'))) STORED,
ADD INDEX idx_brand (brand);

-- Multi-valued indexes (8.0.17+) for arrays
ALTER TABLE products
ADD INDEX idx_ports ((CAST(attrs-&gt;'$.ports' AS CHAR(20) ARRAY)));
-- Now JSON_CONTAINS can use an index:
SELECT * FROM products WHERE JSON_CONTAINS(attrs-&gt;'$.ports', '"hdmi"');</code></pre>

<p><strong>Schema validation against a schema</strong>:</p>

<pre><code>ALTER TABLE products
ADD CONSTRAINT chk_attrs_schema
CHECK (JSON_SCHEMA_VALID(
  '{"type":"object",
    "required":["brand"],
    "properties":{"brand":{"type":"string"},"ram_gb":{"type":"integer","minimum":1}}}',
  attrs
));</code></pre>

<p><strong>When to step outside MySQL</strong>: heavily document-shaped workloads with deep nesting and complex queries are often better served by a document database (MongoDB, DynamoDB, Postgres JSONB). MySQL JSON shines for hybrid: relational where it matters, JSON where it doesn&rsquo;t.</p>
'''

ANSWERS[52] = r'''
<p>MySQL provides a rich set of JSON functions for extracting, modifying, and searching JSON values. Path expressions follow the JSONPath syntax: <code>$.field</code> for object members, <code>$[i]</code> for array indices, <code>$.array[*]</code> for wildcards.</p>

<p><strong>Reading values</strong>:</p>

<pre><code>-- JSON_EXTRACT and the -&gt; operator are equivalent
SELECT attrs-&gt;'$.brand'        FROM products;   -- returns "Acme" (with quotes — JSON value)
SELECT attrs-&gt;&gt;'$.brand'       FROM products;   -- returns Acme (unquoted — string)
-- -&gt;&gt; is shorthand for JSON_UNQUOTE(JSON_EXTRACT(...))

-- Multiple paths
SELECT JSON_EXTRACT(attrs, '$.brand', '$.ram_gb') FROM products;
-- Returns ["Acme", 16]</code></pre>

<p><strong>Filtering on JSON values</strong>:</p>

<pre><code>-- Equality
SELECT * FROM products WHERE attrs-&gt;&gt;'$.brand' = 'Acme';

-- Numeric comparison (cast required)
SELECT * FROM products WHERE attrs-&gt;'$.ram_gb' &gt;= 16;

-- Existence
SELECT * FROM products WHERE JSON_CONTAINS_PATH(attrs, 'one', '$.color');

-- Array containment
SELECT * FROM products WHERE JSON_CONTAINS(attrs-&gt;'$.ports', '"usb-c"');
-- Does the ports array contain "usb-c"?

-- Array overlap (8.0.17+)
SELECT * FROM products WHERE JSON_OVERLAPS(attrs-&gt;'$.ports', '["hdmi","ethernet"]');</code></pre>

<p><strong>Modifying JSON in place</strong>:</p>

<pre><code>UPDATE products
SET attrs = JSON_SET(attrs, '$.warranty_months', 24)   -- set or replace
WHERE id = 1;

UPDATE products
SET attrs = JSON_REMOVE(attrs, '$.color')              -- delete a key
WHERE id = 2;

UPDATE products
SET attrs = JSON_ARRAY_APPEND(attrs, '$.ports', 'displayport')
WHERE id = 1;

UPDATE products
SET attrs = JSON_MERGE_PATCH(attrs, '{"ram_gb":32,"new_field":true}');
-- Standard JSON Merge Patch (RFC 7396) — null values delete keys</code></pre>

<p><strong>JSON_TABLE &mdash; relational view of nested JSON</strong> (8.0+, the most powerful JSON function):</p>

<pre><code>SELECT p.id, jt.port_name
FROM products p,
JSON_TABLE(p.attrs-&gt;'$.ports', '$[*]'
  COLUMNS (port_name VARCHAR(20) PATH '$')
) AS jt;
-- One row per (product, port) — relational shape from nested array</code></pre>

<p>Lets you join, filter, and aggregate over JSON arrays as if they were normalized tables &mdash; without actually denormalizing.</p>

<p><strong>Performance considerations</strong>:</p>

<ul>
  <li>JSON queries without indexes are full scans &mdash; design generated columns for the paths you filter on.</li>
  <li>Modifying a JSON column rewrites the whole binary representation, even for small changes &mdash; not free.</li>
  <li><code>EXPLAIN</code> shows when a JSON-derived index is being used; without it, you&rsquo;re scanning.</li>
</ul>

<p>For occasional document fields, MySQL JSON is a clean fit. For schemas where most queries are JSON-pathing, the workload may be better served by a database designed for documents.</p>
'''

ANSWERS[53] = r'''
<p>MySQL has had spatial data types and functions since 4.1 and full OpenGIS standard support in 5.6+. The data types represent geometric shapes, and the functions implement standard spatial relationships and computations.</p>

<p><strong>Geometry types</strong> (a hierarchy):</p>

<table>
  <tr><th>Type</th><th>Represents</th></tr>
  <tr><td><code>POINT</code></td><td>A single coordinate (lat/long, x/y)</td></tr>
  <tr><td><code>LINESTRING</code></td><td>A connected sequence of points (a route, a road)</td></tr>
  <tr><td><code>POLYGON</code></td><td>A closed area with optional inner holes</td></tr>
  <tr><td><code>MULTIPOINT</code>, <code>MULTILINESTRING</code>, <code>MULTIPOLYGON</code></td><td>Collections of the above</td></tr>
  <tr><td><code>GEOMETRY</code></td><td>Generic supertype</td></tr>
  <tr><td><code>GEOMETRYCOLLECTION</code></td><td>Mixed collection</td></tr>
</table>

<pre><code>CREATE TABLE locations (
  id     INT PRIMARY KEY,
  name   VARCHAR(100),
  pos    POINT NOT NULL SRID 4326,
  area   POLYGON SRID 4326,
  SPATIAL INDEX idx_pos (pos)
) ENGINE=InnoDB;

INSERT INTO locations VALUES
  (1, 'HQ',     ST_GeomFromText('POINT(-122.4194 37.7749)', 4326), NULL),
  (2, 'Office', ST_GeomFromText('POINT(-73.9857 40.7484)',  4326), NULL);</code></pre>

<p><strong>SRID</strong> &mdash; Spatial Reference System Identifier. <strong>4326 (WGS84)</strong> is the standard for lat/long; <strong>3857 (Web Mercator)</strong> for tile-map projections. Mixing SRIDs in calculations produces errors or wrong results.</p>

<p><strong>Common spatial queries</strong>:</p>

<pre><code>-- Distance between two points (great-circle, in meters)
SELECT ST_Distance_Sphere(
  ST_GeomFromText('POINT(-122.4 37.77)', 4326),
  ST_GeomFromText('POINT(-73.98 40.74)', 4326)
);
-- ≈ 4129000 (meters from SF to NYC)

-- Find all locations within 5km of a point
SELECT name, ST_Distance_Sphere(pos, @target) AS meters
FROM locations
WHERE ST_Distance_Sphere(pos, @target) &lt;= 5000
ORDER BY meters;

-- Points inside a polygon
SELECT id, name FROM locations
WHERE ST_Contains(@bay_area_polygon, pos);

-- Two shapes intersect (touch or overlap)
SELECT a.id, b.id
FROM regions a JOIN regions b ON ST_Intersects(a.boundary, b.boundary)
WHERE a.id &lt; b.id;</code></pre>

<p><strong>Spatial indexes</strong> (R-tree based) make bounding-box queries fast &mdash; the optimizer uses them for <code>ST_Contains</code>, <code>ST_Within</code>, <code>ST_Intersects</code>. Distance queries don&rsquo;t use the index directly; combine with a bounding box for performance:</p>

<pre><code>-- Distance + bounding box prefilter
SELECT name FROM locations
WHERE MBRContains(
  ST_GeomFromText('POLYGON((...))', 4326),  -- bounding box around target ± radius
  pos
)
AND ST_Distance_Sphere(pos, @target) &lt;= 5000;</code></pre>

<p><strong>Limitations</strong>: MySQL&rsquo;s spatial implementation is OK for moderate workloads but lacks features and performance of dedicated GIS databases. <strong>PostGIS</strong> on PostgreSQL is the gold standard &mdash; richer functions, faster, more accurate. For mapping at scale, consider <strong>PostGIS</strong> or specialized stores like <strong>Tile38</strong> (real-time geofencing on Redis-protocol).</p>
'''

ANSWERS[54] = r'''
<p><code>GEOMETRY</code> is the generic supertype for all spatial values in MySQL &mdash; a column declared <code>GEOMETRY</code> can hold any of the specific subtypes (POINT, LINESTRING, POLYGON, etc.). Use it when a single column should accept multiple shape kinds; otherwise prefer the specific type for type safety.</p>

<pre><code>CREATE TABLE features (
  id      INT PRIMARY KEY,
  name    VARCHAR(100),
  shape   GEOMETRY NOT NULL SRID 4326,
  SPATIAL INDEX idx_shape (shape)
);

INSERT INTO features VALUES
  (1, 'Trail head', ST_GeomFromText('POINT(-122.4 37.77)', 4326)),
  (2, 'Trail',      ST_GeomFromText('LINESTRING(-122.4 37.77, -122.41 37.78)', 4326)),
  (3, 'Park',       ST_GeomFromText('POLYGON((-122.42 37.76, -122.42 37.78, -122.40 37.78, -122.40 37.76, -122.42 37.76))', 4326));</code></pre>

<p><strong>Identifying the actual shape</strong>:</p>

<pre><code>SELECT id, ST_GeometryType(shape) AS shape_type FROM features;
-- 1 → "POINT"
-- 2 → "LINESTRING"
-- 3 → "POLYGON"</code></pre>

<p><strong>Storage</strong>: each row stores the type tag plus the binary representation. Point columns are smaller and faster than the generic GEOMETRY because the parser knows the shape upfront.</p>

<p><strong>Working with coordinates</strong>:</p>

<pre><code>-- Extract X (longitude) and Y (latitude) from a POINT
SELECT
  id,
  name,
  ST_X(shape) AS lng,
  ST_Y(shape) AS lat
FROM features
WHERE ST_GeometryType(shape) = 'POINT';

-- Construct a point from coordinates
SET @pt = ST_SRID(POINT(-122.4194, 37.7749), 4326);
SELECT ST_AsText(@pt);  -- "POINT(-122.4194 37.7749)"</code></pre>

<p><strong>SRID essentials</strong>: an SRID-bound column rejects values with mismatched SRIDs &mdash; safety net against mixing coordinate systems. Always specify <code>SRID 4326</code> for lat/long data; spatial indexes only work efficiently when the SRID matches the index.</p>

<p><strong>Format conversions</strong>:</p>

<pre><code>-- WKT (Well-Known Text) — human-readable
ST_GeomFromText('POINT(-122.4 37.77)', 4326)
ST_AsText(shape)

-- WKB (Well-Known Binary) — compact, used over the wire
ST_GeomFromWKB(unhex('0101...'), 4326)
ST_AsBinary(shape)

-- GeoJSON (RFC 7946)
ST_GeomFromGeoJSON('{"type":"Point","coordinates":[-122.4,37.77]}')
ST_AsGeoJSON(shape)</code></pre>

<p><strong>Practical advice</strong>: most geospatial applications use POINT for items with a location and POLYGON for regions/zones. The generic GEOMETRY column type is only needed when a single table holds genuinely heterogeneous shapes (CAD files, GIS imports). For simple "store and query nearby" use cases, POINT plus a spatial index handles millions of rows fine.</p>
'''

ANSWERS[55] = r'''
<p>High-concurrency workloads (thousands of concurrent connections, hot rows, high QPS) need careful tuning at multiple layers. The bottlenecks are typically lock contention, connection overhead, and CPU saturation rather than raw I/O.</p>

<p><strong>Connection management is usually the first bottleneck</strong>:</p>

<ul>
  <li><strong>Connection pooling at the application</strong> &mdash; HikariCP (JVM), <code>mysql2</code> pool (Node.js), SQLAlchemy pool (Python). Reuse connections; don&rsquo;t open one per request.</li>
  <li><strong>ProxySQL or MaxScale in front</strong> &mdash; multiplexes thousands of application connections onto a small backend pool, splits read/write traffic, caches query plans.</li>
  <li><strong>Tune <code>max_connections</code></strong> realistically &mdash; per-thread buffers (sort, join, read) consume RAM × max_connections; 500-1000 is usually plenty with proper pooling.</li>
</ul>

<p><strong>InnoDB tuning for concurrency</strong>:</p>

<table>
  <tr><th>Variable</th><th>What to set</th></tr>
  <tr><td><code>innodb_thread_concurrency</code></td><td>0 (let InnoDB schedule) on modern servers; rarely beneficial to limit</td></tr>
  <tr><td><code>innodb_buffer_pool_instances</code></td><td>8-16 (multiple smaller pools reduce mutex contention on the global LRU)</td></tr>
  <tr><td><code>innodb_io_capacity / max</code></td><td>5000-20000 for NVMe; signals available I/O for background work</td></tr>
  <tr><td><code>innodb_purge_threads</code></td><td>4+ to keep undo cleanup parallel under heavy writes</td></tr>
  <tr><td><code>innodb_adaptive_hash_index</code></td><td>OFF on extreme write workloads &mdash; the AHI mutex becomes a hotspot</td></tr>
</table>

<p><strong>Schema and query patterns</strong>:</p>

<ul>
  <li><strong>Avoid hot rows</strong> &mdash; a single counter that every transaction updates is a sequential bottleneck. Shard the counter into N rows; sum on read.</li>
  <li><strong>Short transactions</strong> &mdash; long transactions hold locks longer, blocking everyone else. Begin late, commit early.</li>
  <li><strong>Use SKIP LOCKED for queues</strong> &mdash; multiple workers consuming jobs without queueing on a lock:
<pre><code>SELECT * FROM jobs
WHERE status='pending'
ORDER BY created_at
LIMIT 10
FOR UPDATE SKIP LOCKED;</code></pre></li>
  <li><strong>InnoDB row locks, not table locks</strong> &mdash; ensure indexes exist for predicates so InnoDB locks rows, not ranges. <code>WHERE col = ?</code> on an unindexed column causes full-scan with row locks on every row examined.</li>
  <li><strong>Read replicas for read-heavy traffic</strong> &mdash; offload reporting and analytical queries; primary serves writes and read-your-writes paths.</li>
</ul>

<p><strong>Operating-system level</strong>:</p>

<ul>
  <li><strong>Linux: <code>net.core.somaxconn</code></strong> high enough to absorb connection bursts.</li>
  <li><strong>File descriptor limits</strong> &mdash; <code>ulimit -n</code> raised for the mysql user.</li>
  <li><strong>Sufficient CPU cores</strong> &mdash; modern MySQL scales well to 32-64 cores; beyond that, NUMA effects matter (pin to nodes).</li>
</ul>

<p><strong>Beyond a single instance</strong> &mdash; ProxySQL routing, read replicas, sharding via Vitess/PlanetScale/TiDB. The architecture answer often beats further single-instance tuning past a certain scale.</p>
'''

ANSWERS[56] = r'''
<p><code>innodb_buffer_pool_size</code> is the single most important MySQL configuration variable. It controls how much memory InnoDB uses to cache data and indexes; its size determines whether the working set lives in RAM (fast) or hits disk (slow).</p>

<p><strong>Sizing guidance</strong>:</p>

<table>
  <tr><th>Server role</th><th>Buffer pool size</th></tr>
  <tr><td>Dedicated MySQL server</td><td>50-70% of RAM</td></tr>
  <tr><td>Server shared with app</td><td>30-50% of RAM</td></tr>
  <tr><td>Development / small DB</td><td>Match expected DB size, capped at 1-2 GB</td></tr>
</table>

<p>Don&rsquo;t set it to 100% of RAM &mdash; the OS, replication, per-thread buffers, and other processes need memory too. On a 64 GB dedicated server, ~40 GB is a sensible starting point.</p>

<p><strong>How it works</strong>: InnoDB reads pages from disk into the pool on first access, evicts pages via an LRU algorithm when full. The pool caches both data pages and index pages; secondary indexes that fit in memory enable index-only lookups without ever touching disk.</p>

<pre><code>-- Set in my.cnf
[mysqld]
innodb_buffer_pool_size = 40G
innodb_buffer_pool_instances = 16

-- Or change at runtime (8.0+)
SET PERSIST innodb_buffer_pool_size = 42949672960;</code></pre>

<p><strong>buffer_pool_instances</strong> splits the pool into N independent partitions, each with its own LRU and mutexes &mdash; reduces contention on multi-core systems. Default is 8 in 8.0; 16 for very busy servers.</p>

<p><strong>Diagnose hit ratio</strong>:</p>

<pre><code>SELECT
  100 * (1 - innodb_buffer_pool_reads / innodb_buffer_pool_read_requests) AS hit_pct,
  innodb_buffer_pool_reads             AS disk_reads,
  innodb_buffer_pool_read_requests     AS total_reads
FROM (SELECT
  (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME='Innodb_buffer_pool_reads') AS innodb_buffer_pool_reads,
  (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME='Innodb_buffer_pool_read_requests') AS innodb_buffer_pool_read_requests
) t;</code></pre>

<ul>
  <li><strong>&gt; 99%</strong> &mdash; healthy. Working set fits comfortably.</li>
  <li><strong>95-99%</strong> &mdash; OK for OLAP, marginal for high-QPS OLTP.</li>
  <li><strong>&lt; 95%</strong> &mdash; pool is too small; disk reads are dominating. Add memory or shrink the schema.</li>
</ul>

<p><strong>Buffer pool warm-up</strong> &mdash; after a restart, the pool is empty and queries are slow. <code>innodb_buffer_pool_dump_at_shutdown / load_at_startup</code> persist the page list so a restart preloads hot pages:</p>

<pre><code>[mysqld]
innodb_buffer_pool_dump_at_shutdown = ON
innodb_buffer_pool_load_at_startup  = ON
innodb_buffer_pool_dump_pct         = 50  -- top 50% most-used pages</code></pre>

<p><strong>Monitor key counters</strong>: <code>Innodb_buffer_pool_pages_dirty</code>, <code>Innodb_buffer_pool_pages_free</code>, <code>Innodb_buffer_pool_wait_free</code>. Free pages dropping to zero or wait_free incrementing means flushing can&rsquo;t keep up with writes &mdash; raise <code>innodb_io_capacity</code> or improve the disk.</p>
'''

ANSWERS[57] = r'''
<p><code>mysqlslap</code> is a built-in load-testing tool that simulates concurrent client load against a MySQL server. Useful for quick sanity-check benchmarks: comparing config changes, validating that hardware can sustain expected QPS, or measuring relative impact of schema changes.</p>

<pre><code># Generate and run a synthetic workload — 50 concurrent clients, 1000 iterations each
mysqlslap \
  --user=root --password \
  --concurrency=50 \
  --iterations=1000 \
  --auto-generate-sql \
  --auto-generate-sql-load-type=mixed \
  --number-int-cols=2 \
  --number-char-cols=3 \
  --engine=innodb

# Output reports min/avg/max time and operations/sec.</code></pre>

<p><strong>Run a custom query</strong> &mdash; far more useful than the auto-generated workload:</p>

<pre><code>mysqlslap \
  --user=app --password \
  --host=db.internal \
  --concurrency=100 \
  --iterations=1 \
  --create-schema=shop \
  --query="SELECT * FROM orders WHERE customer_id = 5 ORDER BY created_at DESC LIMIT 20"
# Each of 100 clients runs the query in parallel; reports timings.</code></pre>

<p><strong>Pre-load and then test</strong>:</p>

<pre><code>mysqlslap \
  --create="CREATE TABLE t (id INT PRIMARY KEY, val INT, INDEX(val))" \
  --pre-query="INSERT INTO t (id, val) SELECT n, RAND()*1000 FROM seq_1_to_100000" \
  --query="SELECT COUNT(*) FROM t WHERE val &gt; 500" \
  --concurrency=50 --iterations=10</code></pre>

<p><strong>Limitations</strong>:</p>

<ul>
  <li>Doesn&rsquo;t simulate realistic mixed read/write patterns by default.</li>
  <li>No transaction modeling (commits per second, conflicting writes).</li>
  <li>No application-level concurrency patterns (connection pooling, request bursts).</li>
  <li>Single-machine; can&rsquo;t scale beyond what one client can drive.</li>
</ul>

<p><strong>Modern alternative &mdash; sysbench</strong>: more realistic, more flexible, the de facto industry benchmarking standard.</p>

<pre><code># Standard OLTP read-write benchmark
sysbench oltp_read_write \
  --mysql-host=db.internal \
  --mysql-user=root --mysql-password=... \
  --tables=10 --table-size=1000000 \
  --threads=64 --time=300 \
  --report-interval=10 \
  prepare      # populate tables

sysbench oltp_read_write [...same args] run     # actual benchmark
sysbench oltp_read_write [...same args] cleanup</code></pre>

<p><strong>Other tools</strong>:</p>

<ul>
  <li><strong>HammerDB</strong> &mdash; cross-database, TPC-C and TPC-H benchmarks.</li>
  <li><strong>Percona TPCC-mysql</strong> &mdash; classic transactional benchmark.</li>
  <li><strong>BenchmarkSQL</strong> &mdash; TPC-C style, easy to set up.</li>
  <li><strong>Locust + Python driver</strong> &mdash; realistic application-level scenarios with HTTP and DB calls intermixed.</li>
</ul>

<p><strong>Practical advice</strong>: <code>mysqlslap</code> is fine for quick comparisons (<em>"did changing this setting help?"</em>) but production capacity planning needs realistic mixed workloads driven from the application side. Run benchmarks on hardware and OS configurations identical to production &mdash; the relative numbers transfer; absolute numbers don&rsquo;t.</p>
'''

ANSWERS[58] = r'''
<p>Index design is the single biggest lever for query performance. The principles are well-established; the discipline is applying them systematically rather than reactively adding indexes when slow queries appear.</p>

<p><strong>Selectivity first</strong>: an index is useful when the indexed column distinguishes rows. <code>email</code> with millions of distinct values: excellent. <code>gender</code> with two values: useless &mdash; the optimizer scans anyway because reading the index plus row is more work than just scanning.</p>

<pre><code>-- Estimate selectivity
SELECT COUNT(DISTINCT col) / COUNT(*) AS selectivity FROM tbl;
-- &gt; 0.1: probably worth indexing
-- &lt; 0.01: probably not</code></pre>

<p><strong>Composite indexes follow the leftmost-prefix rule</strong>:</p>

<table>
  <tr><th>Index</th><th>Serves WHERE on</th><th>Doesn&rsquo;t serve</th></tr>
  <tr><td><code>(a, b, c)</code></td><td><code>a</code>, <code>(a, b)</code>, <code>(a, b, c)</code></td><td><code>b</code> alone, <code>c</code> alone, <code>(b, c)</code></td></tr>
</table>

<p>Order columns by selectivity (most selective first) <em>or</em> by query usage. Equality predicates first, then range, then sort. <code>(status, created_at)</code> serves <code>WHERE status='active' ORDER BY created_at</code> with no sort; <code>(created_at, status)</code> doesn&rsquo;t.</p>

<p><strong>Cover hot queries</strong> &mdash; include all columns the query reads to enable index-only access:</p>

<pre><code>-- Query: SELECT id, total FROM orders WHERE customer_id = ? AND status = 'paid'
CREATE INDEX idx_cust_status_total ON orders (customer_id, status, total);
-- Now EXPLAIN shows: Using where; Using index — no row fetch needed</code></pre>

<p><strong>Avoid index-killing patterns in WHERE</strong>:</p>

<ul>
  <li><code>WHERE YEAR(date_col) = 2026</code> &mdash; wraps the indexed column. Use <code>WHERE date_col &gt;= '2026-01-01' AND date_col &lt; '2027-01-01'</code> instead.</li>
  <li><code>WHERE col + 0 = 5</code> &mdash; same problem. Move the math.</li>
  <li><code>WHERE LOWER(name) = 'alice'</code> &mdash; create a functional index <code>(LOWER(name))</code> or generated column.</li>
  <li><code>WHERE col LIKE '%suffix'</code> &mdash; leading wildcard prevents index range scan; <code>'prefix%'</code> works.</li>
</ul>

<p><strong>Drop unused indexes</strong>:</p>

<pre><code>SELECT object_schema, object_name, index_name
FROM sys.schema_unused_indexes;
-- Indexes that haven't been touched since startup. Drop after observing for a couple weeks.</code></pre>

<p>Every index slows writes (each INSERT/UPDATE/DELETE updates every index) and consumes RAM. The wrong index can be worse than no index.</p>

<p><strong>Don&rsquo;t over-index</strong>:</p>

<ul>
  <li>Two specialized indexes often beat one wide index trying to cover all queries.</li>
  <li>Avoid redundant prefix indexes &mdash; <code>(a)</code> when <code>(a, b)</code> already exists.</li>
  <li>Partial / functional indexes for specific patterns (8.0.13+).</li>
</ul>

<p><strong>Verify with EXPLAIN</strong>: <code>type: ref</code> or <code>type: range</code> on the chosen index, low <code>rows</code> estimate, no <code>Using filesort</code> or <code>Using temporary</code> for the predicate&rsquo;s portion. <code>EXPLAIN ANALYZE</code> confirms with actual numbers.</p>

<p><strong>Tools</strong>: <strong>pt-index-usage</strong>, MySQL Workbench&rsquo;s visual explain, <strong>EVERSQL</strong>, <strong>sys.statement_analysis</strong> &mdash; identify queries that would benefit from new indexes or have stale ones.</p>
'''

ANSWERS[59] = r'''
<p>Slow queries are diagnosed and fixed through a tight loop: capture, identify, analyze, fix, verify. The slow query log + <code>pt-query-digest</code> is the standard pipeline.</p>

<p><strong>Step 1 &mdash; capture</strong>:</p>

<pre><code>-- Enable the slow query log
SET GLOBAL slow_query_log = ON;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
SET GLOBAL long_query_time = 0.5;       -- queries &gt; 500ms
SET GLOBAL log_queries_not_using_indexes = ON;
SET GLOBAL log_slow_admin_statements = ON;

-- Persist
SET PERSIST long_query_time = 0.5;</code></pre>

<p>Set <code>long_query_time</code> low enough to capture useful data &mdash; 0.5 to 1 second on OLTP. Capturing every query (<code>0</code>) is OK for a few minutes during diagnosis but generates massive logs.</p>

<p><strong>Step 2 &mdash; aggregate with pt-query-digest</strong>:</p>

<pre><code>pt-query-digest /var/log/mysql/slow.log | head -100

# Output groups queries by fingerprint and ranks by total time.
# Example top entry:
# Rank Response time   Calls  R/Call   Item
# 1    234.5s 38%      4521   0.052s   SELECT orders WHERE customer_id = ?
# 2     67.2s 11%       142   0.473s   UPDATE inventory ...</code></pre>

<p>Sort by <strong>total time</strong>, not average &mdash; a query running 4521 times at 50ms is a much bigger target than one running once at 5 seconds.</p>

<p><strong>Step 3 &mdash; analyze with EXPLAIN ANALYZE</strong>:</p>

<pre><code>EXPLAIN ANALYZE
SELECT orders.* FROM orders WHERE customer_id = 5 ORDER BY created_at DESC LIMIT 20;</code></pre>

<p>Look at:</p>

<ul>
  <li><strong>Access type</strong> &mdash; <code>ALL</code> (table scan), <code>index</code> (full index scan), <code>range</code> (range scan), <code>ref</code> (matching value), <code>const</code> (PK lookup).</li>
  <li><strong>Rows examined vs rows returned</strong> &mdash; large gap means the predicate isn&rsquo;t selective at the index level. Add a more specific index.</li>
  <li><strong>Extra: Using filesort</strong> &mdash; ORDER BY with no compatible index. Add an index ordered the same way.</li>
  <li><strong>Extra: Using temporary</strong> &mdash; GROUP BY or DISTINCT spilling to temp table. Often resolved with a covering index.</li>
</ul>

<p><strong>Step 4 &mdash; fix</strong>:</p>

<ul>
  <li>Add or modify indexes (Q58).</li>
  <li>Rewrite the query &mdash; correlated subqueries to joins, IN-with-large-list to JOIN with derived table, function-on-column predicates to range.</li>
  <li>Reduce returned columns to enable covering index.</li>
  <li>Replace <code>OFFSET N LIMIT M</code> on big tables with keyset pagination.</li>
</ul>

<p><strong>Step 5 &mdash; verify</strong>:</p>

<pre><code>-- Re-run pt-query-digest after the fix:
pt-query-digest /var/log/mysql/slow.log | head -20
-- The previously-bad query should drop in rank.</code></pre>

<p><strong>For systematic monitoring rather than firefighting</strong>:</p>

<ul>
  <li><code>performance_schema.events_statements_summary_by_digest</code> &mdash; queryable, no log parsing needed.</li>
  <li><strong>Percona PMM</strong>, <strong>Datadog DBM</strong>, <strong>SolarWinds DPA</strong>, <strong>New Relic</strong> &mdash; continuous query-level metrics with alerting and historical trends.</li>
  <li><strong>Prometheus + mysqld_exporter</strong> for self-hosted monitoring; pair with Grafana for dashboards.</li>
</ul>

<p>The standing principle: <strong>optimize the queries that consume the most cumulative time</strong>, not the most irritating individual ones. Heavy-tailed workloads mean a few queries dominate everything.</p>
'''

ANSWERS[60] = r'''
<p>Time-series data &mdash; metrics, events, IoT readings, log entries &mdash; has predictable shape (timestamp + dimensions + values), append-only writes, and queries that filter by time range. MySQL handles moderate-scale time series well with the right schema patterns; high-volume cases warrant a purpose-built database.</p>

<p><strong>Schema basics</strong>:</p>

<pre><code>CREATE TABLE metrics (
  ts          DATETIME(3) NOT NULL,
  metric      VARCHAR(64) NOT NULL,
  host        VARCHAR(64) NOT NULL,
  value       DOUBLE NOT NULL,

  PRIMARY KEY (ts, metric, host),
  INDEX idx_metric_ts (metric, ts)
) ENGINE=InnoDB
PARTITION BY RANGE (TO_DAYS(ts)) (
  PARTITION p2026_q1 VALUES LESS THAN (TO_DAYS('2026-04-01')),
  PARTITION p2026_q2 VALUES LESS THAN (TO_DAYS('2026-07-01')),
  PARTITION p2026_q3 VALUES LESS THAN (TO_DAYS('2026-10-01')),
  PARTITION p2026_q4 VALUES LESS THAN (TO_DAYS('2027-01-01')),
  PARTITION pmax     VALUES LESS THAN MAXVALUE
);</code></pre>

<p><strong>Why these choices</strong>:</p>

<ul>
  <li><strong>PK starts with timestamp</strong> &mdash; sequential inserts append to the end of the clustered index; no random I/O during writes.</li>
  <li><strong>Range partitioning by date</strong> &mdash; old partitions can be dropped wholesale; queries pruning by time only scan relevant partitions.</li>
  <li><strong>Secondary index <code>(metric, ts)</code></strong> &mdash; supports queries like <em>"all values of cpu.usage in the last hour"</em>.</li>
</ul>

<p><strong>Common queries</strong>:</p>

<pre><code>-- Latest value per host
SELECT host, value FROM metrics
WHERE metric = 'cpu.usage' AND ts &gt;= NOW() - INTERVAL 5 MINUTE
ORDER BY ts DESC LIMIT 1;

-- Time-bucketed aggregation
SELECT
  metric,
  DATE_FORMAT(ts, '%Y-%m-%d %H:%i:00') AS minute,
  AVG(value) AS avg_val
FROM metrics
WHERE metric = 'cpu.usage'
  AND ts &gt;= NOW() - INTERVAL 1 HOUR
GROUP BY metric, minute
ORDER BY minute;</code></pre>

<p><strong>Retention via partition drops</strong>:</p>

<pre><code>-- Drop a quarter of data instantly
ALTER TABLE metrics DROP PARTITION p2024_q4;
-- Same operation as DELETE WHERE ts &lt; X but milliseconds vs hours.</code></pre>

<p><strong>Pre-aggregation for read performance</strong>: maintain rollup tables (1-minute, 1-hour, 1-day) refreshed by scheduled events or on-write triggers. Queries pick the appropriate granularity:</p>

<pre><code>-- Hourly rollup of metrics
CREATE TABLE metrics_hourly (
  hour    DATETIME, metric VARCHAR(64), host VARCHAR(64),
  cnt INT, sum DOUBLE, min DOUBLE, max DOUBLE,
  PRIMARY KEY (hour, metric, host)
);

-- Refresh on a schedule
INSERT INTO metrics_hourly (hour, metric, host, cnt, sum, min, max)
SELECT
  DATE_FORMAT(ts, '%Y-%m-%d %H:00:00'),
  metric, host,
  COUNT(*), SUM(value), MIN(value), MAX(value)
FROM metrics
WHERE ts &gt;= NOW() - INTERVAL 2 HOUR AND ts &lt; DATE_FORMAT(NOW(), '%Y-%m-%d %H:00:00')
GROUP BY 1, 2, 3
ON DUPLICATE KEY UPDATE cnt = VALUES(cnt), sum = VALUES(sum), min = LEAST(min, VALUES(min)), max = GREATEST(max, VALUES(max));</code></pre>

<p><strong>When MySQL is the wrong tool</strong>:</p>

<ul>
  <li>Sustained ingest above ~50K writes/sec &mdash; <strong>InfluxDB</strong>, <strong>TimescaleDB</strong> (PostgreSQL extension), <strong>QuestDB</strong>, <strong>VictoriaMetrics</strong>.</li>
  <li>Multi-billion-row scans for analytics &mdash; <strong>ClickHouse</strong> (columnar, MergeTree designed for time series).</li>
  <li>Production observability &mdash; <strong>Prometheus</strong> (pull model, designed for metrics), <strong>OpenTelemetry</strong> + a backend.</li>
</ul>

<p>Use MySQL for time-series data tightly coupled to relational data (e.g., per-customer event histories where joins matter); use a purpose-built TSDB when the volume is the primary concern.</p>
'''

ANSWERS[61] = r'''
<p><code>INFORMATION_SCHEMA</code> is a set of read-only views exposing metadata about every database, table, column, index, constraint, privilege, and runtime variable on the server. Standardized across many SQL databases (it&rsquo;s an ANSI SQL feature), so the same queries work on PostgreSQL, MariaDB, etc., with minor variations.</p>

<p><strong>Practical examples</strong> &mdash; the queries you actually use:</p>

<pre><code>-- Tables in a database with row counts and storage
SELECT
  table_name,
  table_rows,
  ROUND((data_length + index_length) / 1024 / 1024, 1) AS size_mb,
  ROUND(data_length / 1024 / 1024, 1)                 AS data_mb,
  ROUND(index_length / 1024 / 1024, 1)                AS index_mb
FROM information_schema.tables
WHERE table_schema = 'shop'
ORDER BY data_length + index_length DESC;

-- All columns in a table with types
SELECT column_name, data_type, is_nullable, column_default, column_comment
FROM information_schema.columns
WHERE table_schema = 'shop' AND table_name = 'orders'
ORDER BY ordinal_position;

-- Indexes on a table (including composite definitions)
SELECT
  index_name,
  GROUP_CONCAT(column_name ORDER BY seq_in_index) AS columns,
  non_unique = 0 AS is_unique,
  index_type
FROM information_schema.statistics
WHERE table_schema = 'shop' AND table_name = 'orders'
GROUP BY index_name, non_unique, index_type;

-- Foreign key relationships
SELECT
  constraint_name,
  table_name AS child_table, column_name AS child_col,
  referenced_table_name AS parent_table, referenced_column_name AS parent_col
FROM information_schema.key_column_usage
WHERE table_schema = 'shop' AND referenced_table_name IS NOT NULL;

-- All databases on the server
SELECT schema_name FROM information_schema.schemata;

-- Privileges granted
SELECT * FROM information_schema.user_privileges
WHERE grantee LIKE '%app_user%';</code></pre>

<p><strong>Common uses</strong>:</p>

<ul>
  <li><strong>Schema introspection</strong> &mdash; ORM tools and migrations read it to discover table structure.</li>
  <li><strong>Disk-usage monitoring</strong> &mdash; tracking biggest tables; identifying growth.</li>
  <li><strong>Documentation generation</strong> &mdash; auto-generated ER diagrams, data dictionaries.</li>
  <li><strong>Audit and compliance</strong> &mdash; verifying expected privileges, tables, columns exist.</li>
  <li><strong>Migration safety checks</strong> &mdash; "does this column already exist?" before adding it.</li>
</ul>

<p><strong>Useful schema tables not always remembered</strong>:</p>

<ul>
  <li><code>processlist</code> &mdash; current connections and their queries (also via <code>SHOW PROCESSLIST</code>).</li>
  <li><code>innodb_metrics</code> &mdash; detailed InnoDB counters.</li>
  <li><code>events</code>, <code>routines</code>, <code>triggers</code> &mdash; stored programs.</li>
  <li><code>partitions</code> &mdash; partition layout, row counts per partition.</li>
  <li><code>collations</code>, <code>character_sets</code> &mdash; what&rsquo;s available for column definitions.</li>
</ul>

<p><strong>Performance note</strong>: queries against <code>INFORMATION_SCHEMA</code> can be slow on servers with many databases and tables &mdash; the views are built on the fly. For repeated metadata queries, cache results in your application or use Performance Schema variants when available.</p>

<p><strong>Related</strong>: <code>performance_schema</code> for runtime diagnostics, <code>sys</code> schema for friendlier views over Performance Schema. INFORMATION_SCHEMA is for static structure; the others for runtime behavior.</p>
'''

ANSWERS[62] = r'''
<p>Database refactoring &mdash; renaming columns, splitting tables, changing types, normalizing or denormalizing &mdash; is risky because the existing data and schema must change <em>without breaking running applications</em>. The discipline is breaking each change into reversible deploys using the <strong>expand-contract pattern</strong>.</p>

<p><strong>The rename-column pattern, end to end</strong>:</p>

<pre><code>-- Goal: rename users.fullname to users.full_name

-- Step 1: EXPAND — add the new column without removing the old
ALTER TABLE users
  ADD COLUMN full_name VARCHAR(200) GENERATED ALWAYS AS (fullname) STORED;
-- Generated column auto-syncs from old to new; no app changes needed yet.

-- Step 2: BACKFILL (already done by the generated column)
-- Verify: SELECT COUNT(*) FROM users WHERE full_name IS NULL;

-- Step 3: MIGRATE READERS — deploy app code reading full_name
-- The old column still exists; rollback is safe.

-- Step 4: MIGRATE WRITERS — drop the generated dependency, make full_name a real column
ALTER TABLE users
  DROP COLUMN full_name,
  ADD COLUMN full_name VARCHAR(200);

-- Backfill manually since generated column is gone
UPDATE users SET full_name = fullname;

-- Deploy app code writing to full_name; dual-write to fullname during transition.

-- Step 5: VERIFY — bake-in time, monitor for drift

-- Step 6: CONTRACT — drop the old column
ALTER TABLE users DROP COLUMN fullname;</code></pre>

<p>Each step is an independent deploy. At any moment, the app and DB are mutually compatible.</p>

<p><strong>Common refactoring scenarios</strong>:</p>

<table>
  <tr><th>Refactor</th><th>Approach</th></tr>
  <tr><td>Rename column</td><td>Add new + dual-write + migrate reads + drop old</td></tr>
  <tr><td>Change column type (e.g., INT → BIGINT)</td><td>Same as rename: add new typed column, backfill, switch reads/writes, drop old</td></tr>
  <tr><td>Split one table into two</td><td>Create new tables; backfill from old; dual-write; migrate reads; stop dual-write; drop old</td></tr>
  <tr><td>Merge two tables</td><td>Create combined table; populate; dual-write all sources; migrate reads; remove writes to old; drop old</td></tr>
  <tr><td>Add NOT NULL to a nullable column</td><td>Backfill all NULLs first; deploy app code that never inserts NULLs; then ALTER to NOT NULL</td></tr>
  <tr><td>Drop a column</td><td>Stop reading; stop writing; drop &mdash; one piece at a time</td></tr>
</table>

<p><strong>Online DDL tools for the heavy operations</strong>:</p>

<ul>
  <li><strong>ALGORITHM=INSTANT</strong> (MySQL 8) &mdash; metadata-only changes (Add nullable column at end, drop default) in milliseconds.</li>
  <li><strong>pt-online-schema-change</strong> (Percona) &mdash; uses triggers; widely tested on multi-TB tables.</li>
  <li><strong>gh-ost</strong> (GitHub) &mdash; trigger-free; reads binlog; throttles to replica lag.</li>
  <li><strong>SchemaHero</strong>, <strong>Atlas</strong> &mdash; declarative schema-as-code with migrations generated from a desired state.</li>
</ul>

<p><strong>Discipline that prevents disasters</strong>:</p>

<ul>
  <li><strong>Version migrations as code</strong> &mdash; Flyway, Liquibase, golang-migrate, Alembic, Prisma Migrate. Every migration reviewed and tested before production.</li>
  <li><strong>Test on a recent production snapshot</strong> &mdash; lock-time, undo-log size, and disk usage surprises only show up at real volume.</li>
  <li><strong>Always have a rollback path</strong> &mdash; "roll forward through the bug" is not a plan.</li>
  <li><strong>Coordinate with deploy schedule</strong> &mdash; the DB migration goes out before the application code that uses it.</li>
</ul>
'''

ANSWERS[63] = r'''
<p>Archiving moves old data out of the hot table to keep query and maintenance performance bounded. The right strategy depends on access patterns: how often is old data read, and what queries should still work over it.</p>

<p><strong>Pattern 1 &mdash; partition + drop</strong> (best for time-series, append-only workloads):</p>

<pre><code>-- Table is partitioned by month (or quarter, year)
ALTER TABLE events
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p2024_jan VALUES LESS THAN (TO_DAYS('2024-02-01')),
  PARTITION p2024_feb VALUES LESS THAN (TO_DAYS('2024-03-01')),
  ...
);

-- Drop old partitions wholesale (instant; no scan)
ALTER TABLE events DROP PARTITION p2024_jan;</code></pre>

<p>Drops are O(1) regardless of partition size &mdash; no DELETE pass over millions of rows. Suits logs, metrics, audit events: data over N months is simply gone.</p>

<p><strong>Pattern 2 &mdash; archive table</strong> (when old data is occasionally queried):</p>

<pre><code>CREATE TABLE orders_archive LIKE orders;

-- Periodic archive job (run nightly)
INSERT INTO orders_archive
SELECT * FROM orders WHERE created_at &lt; CURDATE() - INTERVAL 2 YEAR;

DELETE FROM orders WHERE created_at &lt; CURDATE() - INTERVAL 2 YEAR;</code></pre>

<p>Hot table stays small and fast; archive table holds historical rows for compliance or rare lookups. Queries that span both can <code>UNION ALL</code>.</p>

<p><strong>Batched delete to avoid lock pressure</strong>:</p>

<pre><code>-- Delete in chunks of 10K, sleep between batches
DELETE FROM orders
WHERE created_at &lt; CURDATE() - INTERVAL 2 YEAR
LIMIT 10000;
-- Run repeatedly until ROW_COUNT() = 0</code></pre>

<p><strong>Pattern 3 &mdash; offload to S3 / object storage</strong> (cold data, rarely or never queried):</p>

<ol>
  <li>Export old rows to <strong>Parquet</strong> files via <code>SELECT INTO OUTFILE</code> or pandas/Spark/dbt.</li>
  <li>Upload to S3 with appropriate storage class (Glacier for very cold).</li>
  <li>Drop the rows from MySQL.</li>
  <li>Query from object storage on demand via <strong>Athena</strong>, <strong>Presto/Trino</strong>, <strong>DuckDB</strong>.</li>
</ol>

<p>Storage cost per GB on S3 Glacier is 1-2% of typical RDS storage. For year-old data accessed once a quarter, the math is overwhelming.</p>

<p><strong>Pattern 4 &mdash; warehouse for analytics, MySQL for OLTP</strong>:</p>

<ul>
  <li>Stream MySQL changes via <strong>Debezium</strong> + Kafka into <strong>ClickHouse</strong>, <strong>BigQuery</strong>, or <strong>Snowflake</strong>.</li>
  <li>Operational queries hit MySQL on recent data.</li>
  <li>Analytical queries (long-range, aggregate, ad-hoc) run on the warehouse.</li>
  <li>Rows can be aggressively retained in the warehouse without slowing OLTP.</li>
</ul>

<p><strong>Operational considerations</strong>:</p>

<ul>
  <li><strong>Retention policies driven by requirements</strong> &mdash; legal (tax, GDPR), business (lifetime customer history), product (analytics needs).</li>
  <li><strong>Automate the archive job</strong> &mdash; manual archives are forgotten until disks fill.</li>
  <li><strong>Verify before deleting</strong> &mdash; row counts in archive match deletes; data is queryable in its new home.</li>
  <li><strong>Rebuild / OPTIMIZE TABLE</strong> after large deletes if not partitioned, to reclaim disk space (otherwise space is reused only by future inserts).</li>
  <li><strong>GDPR right-to-erasure</strong> &mdash; archived PII still has compliance obligations; design archives to be searchable for deletion requests.</li>
</ul>
'''

ANSWERS[64] = r'''
<p>Optimizer hints override the query planner&rsquo;s decisions. Used sparingly &mdash; the optimizer is usually right, and hints can become wrong as data shifts &mdash; but invaluable when the planner picks a clearly bad plan.</p>

<p><strong>The two hint syntaxes</strong>:</p>

<pre><code>-- Old style: index hints on the table reference
SELECT * FROM orders USE INDEX (idx_customer_status)
WHERE customer_id = 5 AND status = 'paid';

SELECT * FROM orders FORCE INDEX (idx_customer)
WHERE customer_id = 5;

SELECT * FROM orders IGNORE INDEX (idx_status)
WHERE customer_id = 5;

-- New style (5.7+): comment-based hints inside SELECT
SELECT /*+ INDEX(orders idx_customer_status) */ *
FROM orders WHERE customer_id = 5;

SELECT /*+ JOIN_ORDER(o, c) */ *
FROM orders o JOIN customers c ON c.id = o.customer_id;</code></pre>

<p><strong>USE / FORCE / IGNORE INDEX</strong>:</p>

<table>
  <tr><th>Hint</th><th>Behavior</th></tr>
  <tr><td><code>USE INDEX (a, b)</code></td><td>Suggests these indexes; optimizer may still ignore them</td></tr>
  <tr><td><code>FORCE INDEX (a)</code></td><td>Forces use of index a even if optimizer prefers table scan</td></tr>
  <tr><td><code>IGNORE INDEX (a)</code></td><td>Excludes index a from consideration</td></tr>
</table>

<p><strong>Common optimizer hints</strong>:</p>

<table>
  <tr><th>Hint</th><th>Effect</th></tr>
  <tr><td><code>JOIN_ORDER(t1, t2, t3)</code></td><td>Force the join order specified</td></tr>
  <tr><td><code>JOIN_PREFIX(t1)</code></td><td>Start the join with t1</td></tr>
  <tr><td><code>NO_BNL</code> / <code>BNL</code></td><td>Disable / enable Block Nested Loop join</td></tr>
  <tr><td><code>NO_HASH_JOIN</code> / <code>HASH_JOIN</code></td><td>Force or prevent hash join (8.0.18+)</td></tr>
  <tr><td><code>SET_VAR(...)</code></td><td>Set a system variable for this statement only</td></tr>
  <tr><td><code>MAX_EXECUTION_TIME(ms)</code></td><td>Kill the query if it runs longer than ms</td></tr>
  <tr><td><code>RESOURCE_GROUP(grp)</code></td><td>Run query in a specific resource group (priority/affinity)</td></tr>
</table>

<p><strong>When hints make sense</strong>:</p>

<ul>
  <li><strong>The optimizer is provably wrong</strong> &mdash; <code>EXPLAIN</code> shows a plan that scans 10M rows when an index covers the query. Hint to force the index; verify with <code>EXPLAIN ANALYZE</code>.</li>
  <li><strong>Skewed data confuses statistics</strong> &mdash; one customer has 80% of orders; the optimizer underestimates selectivity for that customer. <code>FORCE INDEX</code> on the predicate that&rsquo;s actually selective.</li>
  <li><strong>Long timeout protection</strong> &mdash; <code>/*+ MAX_EXECUTION_TIME(5000) */</code> kills runaway reporting queries.</li>
  <li><strong>Resource isolation</strong> &mdash; analytical queries routed to a lower-priority resource group.</li>
</ul>

<p><strong>When hints are smell</strong>:</p>

<ul>
  <li>Hint wars across many queries usually point to <strong>missing or stale statistics</strong>. Run <code>ANALYZE TABLE</code> first.</li>
  <li>Schema design issues (missing index, bad index, wrong join structure) should be fixed structurally, not papered over with hints.</li>
  <li>Hints become wrong over time as data changes &mdash; that 80%-customer might no longer dominate; the forced index may now be slower than the alternative.</li>
</ul>

<p><strong>Process</strong>: identify the bad plan with <code>EXPLAIN ANALYZE</code>, try a hint, verify it&rsquo;s actually faster, document why the hint exists in a comment. Re-evaluate after major data growth or schema changes.</p>
'''

ANSWERS[65] = r'''
<p>Read-heavy and write-heavy workloads need different optimizations. Most real systems are mixed; the question is which side dominates and what techniques apply to each.</p>

<p><strong>Read-heavy workloads (analytics, dashboards, content sites)</strong>:</p>

<ul>
  <li><strong>Read replicas</strong> &mdash; route SELECTs to async replicas; primary handles writes only. Replicas can be added horizontally for more read throughput.</li>
  <li><strong>Aggressive caching</strong> &mdash; Redis or Memcached for materialized API responses, common queries, sessions. Cache layer fronts the DB; invalidate on writes.</li>
  <li><strong>Buffer pool sized to fit hot data</strong> &mdash; the goal is &gt; 99% buffer pool hit ratio. Cold queries hit disk; hot ones never do.</li>
  <li><strong>Cover hot queries with indexes</strong> &mdash; index-only access (<code>Using index</code> in EXPLAIN) avoids row fetches.</li>
  <li><strong>Materialized aggregates / summary tables</strong> &mdash; precompute expensive joins and aggregates; refresh on schedule or via CDC.</li>
  <li><strong>Read-write split via ProxySQL or application logic</strong> &mdash; transparently send reads to replicas and writes to primary.</li>
</ul>

<p><strong>Write-heavy workloads (event ingestion, telemetry, transactional systems)</strong>:</p>

<ul>
  <li><strong>Sequential primary keys</strong> &mdash; UUID v4 (random) PKs cause page splits across the entire B-tree on insert. Use BIGINT autoincrement, ULID, UUIDv7, or KSUID for time-ordered keys.</li>
  <li><strong>Batched writes</strong> &mdash; multi-row INSERTs are 50-100x faster than single-row; queue and flush in chunks.</li>
  <li><strong>Group commit / async commit</strong> &mdash; <code>innodb_flush_log_at_trx_commit = 2</code> flushes once per second instead of per commit. Tiny durability window for big throughput gain.</li>
  <li><strong>Partitioning by date</strong> &mdash; sequential inserts append to the latest partition; old data dropped wholesale.</li>
  <li><strong>Disable secondary indexes during bulk loads</strong> &mdash; rebuild after; faster than per-row index maintenance.</li>
  <li><strong>Larger redo log</strong> &mdash; <code>innodb_log_file_size = 2G</code> reduces flush frequency.</li>
  <li><strong>NVMe storage and high <code>innodb_io_capacity</code></strong> &mdash; writes are I/O bound; faster disks matter directly.</li>
</ul>

<p><strong>Mixed workloads (the realistic case)</strong>:</p>

<ul>
  <li><strong>Routing</strong>: write to the source, read from replicas where freshness allows. Application or ProxySQL routes; some queries (read-your-writes) must hit primary.</li>
  <li><strong>Connection pooling</strong> with separate pools for reads and writes &mdash; HikariCP, PgBouncer-style ProxySQL.</li>
  <li><strong>Async replication lag awareness</strong> &mdash; user-visible read paths after writes either route to primary, or wait for replica catchup.</li>
  <li><strong>Background jobs offload</strong> &mdash; expensive computations (PDF generation, billing, ETL) run on a queue against replicas, not blocking the main app.</li>
</ul>

<p><strong>Capacity at scale</strong>: when a single primary can&rsquo;t handle write throughput &mdash; sharding becomes the answer. <strong>Vitess</strong>, <strong>PlanetScale</strong>, <strong>TiDB</strong> distribute writes across nodes while keeping the MySQL protocol. Sharding has real operational cost; push vertical scaling, replicas, partitioning, and caching first.</p>

<p><strong>Measure before optimizing</strong>: <code>performance_schema.events_statements_summary_by_digest</code> shows whether your top time-consumers are reads or writes. The right answer comes from data, not assumption.</p>
'''

ANSWERS[66] = r'''
<p>Two fundamentally different backup approaches:</p>

<table>
  <tr><th>Aspect</th><th>Logical backup</th><th>Physical backup</th></tr>
  <tr><td>What&rsquo;s captured</td><td>SQL statements (CREATE + INSERT)</td><td>Raw data files (tablespace, redo log)</td></tr>
  <tr><td>Tools</td><td><code>mysqldump</code>, <code>mysqlpump</code>, <code>mysqlsh dumpInstance</code></td><td>Percona XtraBackup, MySQL Enterprise Backup, filesystem snapshots</td></tr>
  <tr><td>Format</td><td>Text (or compressed text)</td><td>Binary, MySQL-version-specific</td></tr>
  <tr><td>Backup speed</td><td>Slow &mdash; reads every row</td><td>Fast &mdash; copies files in parallel</td></tr>
  <tr><td>Restore speed</td><td>Slow &mdash; replays statements</td><td>Fast &mdash; copies files back</td></tr>
  <tr><td>Portability</td><td>High &mdash; works across versions, platforms, even other DBs</td><td>Low &mdash; same major MySQL version, same OS family</td></tr>
  <tr><td>Selective restore</td><td>Easy &mdash; one table from a dump</td><td>Hard &mdash; whole instance or hand-extract</td></tr>
  <tr><td>Compression</td><td>Built-in via gzip pipe</td><td>Tool-specific</td></tr>
</table>

<p><strong>Logical backup &mdash; mysqldump</strong>:</p>

<pre><code>mysqldump --single-transaction --routines --triggers --events \
  --hex-blob --set-gtid-purged=ON \
  shop &gt; shop.sql
gzip shop.sql

# Restore
gunzip &lt; shop.sql.gz | mysql -u root -p shop</code></pre>

<p>Use cases: small to medium databases (under 100GB), table-level extracts, migrations between major versions, dev/staging refreshes.</p>

<p><strong>Physical backup &mdash; Percona XtraBackup</strong>:</p>

<pre><code>xtrabackup --backup --target-dir=/backup/full --user=root --password=...
# Apply log to make it consistent
xtrabackup --prepare --target-dir=/backup/full

# Incremental — only changed pages since the last backup
xtrabackup --backup --target-dir=/backup/incr1 \
  --incremental-basedir=/backup/full --user=root --password=...

# Restore
systemctl stop mysql
rm -rf /var/lib/mysql/*
xtrabackup --copy-back --target-dir=/backup/full
chown -R mysql:mysql /var/lib/mysql
systemctl start mysql</code></pre>

<p>Use cases: TB-scale databases, frequent backups (hourly + binlog), tight RTO requirements. Backups are file-level snapshots of the data directory; restore is essentially a file copy.</p>

<p><strong>Filesystem / cloud snapshots</strong> &mdash; another physical option:</p>

<ul>
  <li><strong>LVM snapshots</strong> &mdash; on Linux with logical volume management.</li>
  <li><strong>EBS / GCP / Azure disk snapshots</strong> &mdash; on cloud providers; instant copy-on-write.</li>
  <li><strong>RDS / Aurora / Cloud SQL snapshots</strong> &mdash; managed services automate this.</li>
</ul>

<p>For consistency, briefly flush + freeze the filesystem (<code>FLUSH TABLES WITH READ LOCK</code>; <code>fsfreeze</code>) before snapshotting; release immediately after.</p>

<p><strong>The pragmatic combination</strong>:</p>

<ul>
  <li><strong>Daily physical backup</strong> (XtraBackup or snapshots) for fast recovery.</li>
  <li><strong>Continuous binlog backup</strong> for point-in-time recovery between physical backups.</li>
  <li><strong>Occasional logical dumps</strong> for portability, dev refreshes, version migrations.</li>
  <li><strong>Off-site, encrypted, tested quarterly.</strong></li>
</ul>

<p><strong>For cloud-managed databases</strong>: rely on the provider&rsquo;s native backup (RDS automated backups, Aurora continuous backup, Cloud SQL backups). They handle physical-snapshot semantics, retention, and PITR transparently.</p>
'''

ANSWERS[67] = r'''
<p>FULLTEXT search in MySQL handles natural-language and Boolean queries against text columns. Suitable for moderate-scale internal search (CMS content, product catalogs, knowledge bases) when you don&rsquo;t want the operational complexity of a dedicated search engine.</p>

<p><strong>Set up the index</strong>:</p>

<pre><code>CREATE TABLE articles (
  id      INT PRIMARY KEY,
  title   VARCHAR(200),
  body    TEXT,
  tags    VARCHAR(255),
  FULLTEXT INDEX ft_search (title, body, tags)
) ENGINE=InnoDB;

-- Or add later
ALTER TABLE articles ADD FULLTEXT INDEX ft_search (title, body, tags);</code></pre>

<p>Multi-column FULLTEXT indexes serve queries that match across all listed columns; the column list inside <code>MATCH(...)</code> must exactly match the index definition.</p>

<p><strong>Query patterns</strong>:</p>

<pre><code>-- Natural language — relevance-ranked
SELECT id, title,
       MATCH(title, body, tags) AGAINST('react server components') AS rel
FROM articles
WHERE MATCH(title, body, tags) AGAINST('react server components')
ORDER BY rel DESC LIMIT 20;

-- Boolean — operators for required, excluded, prefix, phrase
SELECT id, title FROM articles
WHERE MATCH(title, body, tags)
      AGAINST('+react +(server hooks) -class' IN BOOLEAN MODE);

-- Exact phrase
... AGAINST('"server components"' IN BOOLEAN MODE);

-- Prefix match
... AGAINST('rea*' IN BOOLEAN MODE);

-- Combine with non-FULLTEXT filters
SELECT id, title FROM articles
WHERE MATCH(title, body) AGAINST('mysql performance' IN NATURAL LANGUAGE MODE)
  AND published_at &gt;= '2026-01-01'
  AND status = 'published'
ORDER BY MATCH(title, body) AGAINST('mysql performance') DESC
LIMIT 10;</code></pre>

<p><strong>Configuration that affects results</strong>:</p>

<table>
  <tr><th>Variable</th><th>Effect</th></tr>
  <tr><td><code>innodb_ft_min_token_size</code></td><td>Minimum word length (default 3); shorter words excluded</td></tr>
  <tr><td><code>innodb_ft_max_token_size</code></td><td>Maximum word length (default 84); longer words truncated</td></tr>
  <tr><td><code>innodb_ft_user_stopword_table</code></td><td>Custom stopword list (default excludes "the", "and", etc.)</td></tr>
  <tr><td>50% threshold</td><td>NATURAL LANGUAGE mode: words appearing in &gt; 50% of rows score zero. Use BOOLEAN mode on small datasets to disable.</td></tr>
</table>

<p>After changing tokenization config, drop and recreate the index for it to apply.</p>

<p><strong>Multi-language</strong>: default tokenization is whitespace-based and works for European languages. For CJK (Chinese, Japanese, Korean), use the <code>ngram</code> parser:</p>

<pre><code>FULLTEXT INDEX ft_cjk (body) WITH PARSER ngram;</code></pre>

<p><strong>Limits, and when to use a real search engine</strong>:</p>

<ul>
  <li>No <strong>stemming</strong> beyond simple word boundaries (no "running" matching "run").</li>
  <li>No <strong>synonyms</strong>, fuzzy matching, or typo tolerance.</li>
  <li>Limited <strong>relevance tuning</strong> &mdash; the BM25 scoring is fixed.</li>
  <li>Performance degrades on tens of millions of rows.</li>
  <li>No <strong>faceted aggregation</strong> &mdash; "filter by category, sort by relevance, show counts per facet."</li>
</ul>

<p><strong>Modern alternatives</strong>: <strong>Elasticsearch</strong> / <strong>OpenSearch</strong> (heavyweight, feature-complete), <strong>Meilisearch</strong> (typo-tolerant, easy ops), <strong>Typesense</strong> (real-time, good for product search), <strong>Algolia</strong> (managed). Replicate searchable fields from MySQL via <strong>Debezium</strong> or application dual-write. For internal CMS / product-detail search up to ~5M rows, MySQL FULLTEXT is good enough; beyond that, dedicated search wins.</p>
'''

ANSWERS[68] = r'''
<p>The <code>FEDERATED</code> storage engine lets one MySQL server access tables on a <em>remote</em> MySQL server as if they were local. The local table holds no data; every query is forwarded to the remote server. It&rsquo;s a niche feature &mdash; rarely the right answer in modern architectures &mdash; but useful in narrow cases.</p>

<pre><code>-- On the remote server (the data source)
CREATE TABLE remote_orders (
  id INT PRIMARY KEY,
  customer_id INT,
  total DECIMAL(10, 2)
) ENGINE=InnoDB;

-- On the local server
INSTALL PLUGIN federated SONAME 'ha_federated.so';
SET GLOBAL federated_engine_enabled = ON;

CREATE TABLE federated_orders (
  id INT PRIMARY KEY,
  customer_id INT,
  total DECIMAL(10, 2)
)
ENGINE=FEDERATED
CONNECTION='mysql://user:pass@remote.host:3306/database/remote_orders';

-- Now query the local "table" — under the hood, queries go to remote.host
SELECT * FROM federated_orders WHERE customer_id = 5;</code></pre>

<p><strong>How it works</strong>: every query against the federated table is rewritten as a query to the remote server, sent over the network, executed there, and the results streamed back. There&rsquo;s no caching; each query pays full network latency.</p>

<p><strong>Real-world limitations</strong>:</p>

<ul>
  <li><strong>No transactions across federated tables</strong> &mdash; each query is independent on the remote.</li>
  <li><strong>No foreign keys</strong> referencing federated tables.</li>
  <li><strong>No indexes</strong> on the local side &mdash; the optimizer can&rsquo;t plan effectively without remote stats.</li>
  <li><strong>No DDL forwarding</strong> &mdash; <code>ALTER TABLE federated_orders</code> doesn&rsquo;t change the remote schema.</li>
  <li><strong>Performance is poor for anything but trivial queries</strong> &mdash; joins, subqueries, aggregations all hit the network repeatedly.</li>
  <li><strong>Connection per query</strong> &mdash; FEDERATED opens a new connection for each query (FEDERATEDX in MariaDB pools them; vanilla FEDERATED doesn&rsquo;t).</li>
</ul>

<p><strong>FEDERATEDX</strong> (in MariaDB) is the maintained successor with connection pooling and bug fixes &mdash; if you must use this pattern, prefer FEDERATEDX. Oracle&rsquo;s MySQL has not significantly developed FEDERATED in years.</p>

<p><strong>When FEDERATED might still be appropriate</strong>:</p>

<ul>
  <li><strong>One-off data migration</strong> &mdash; mirror a remote table locally to facilitate INSERT INTO ... SELECT FROM federated_remote.</li>
  <li><strong>Read-only lookups</strong> on small reference tables that change rarely.</li>
  <li><strong>Test environments</strong> referencing a separate canonical data source.</li>
</ul>

<p><strong>Better alternatives for the typical use cases</strong>:</p>

<table>
  <tr><th>Goal</th><th>Modern approach</th></tr>
  <tr><td>Read remote data</td><td>Replication: replica with the data; queries hit replica</td></tr>
  <tr><td>Cross-server joins</td><td>ETL the data into one place; or use a query federation engine like Trino / Presto</td></tr>
  <tr><td>Multi-DB application data access</td><td>Application-level service calls (REST, gRPC) instead of direct DB linking</td></tr>
  <tr><td>Multi-tenant data unified view</td><td>Sharding layer (Vitess) or a single instance with tenant_id</td></tr>
</table>

<p><strong>Summary</strong>: the FEDERATED engine works but has been superseded by better patterns &mdash; replication for data access, ETL or query federation for analytics, service APIs for application coupling. Avoid in new architectures.</p>
'''

ANSWERS[69] = r'''
<p>Triggers execute SQL automatically before or after inserts, updates, or deletes on a table. They run in the same transaction as the triggering statement and have access to the old/new row values via <code>OLD</code> and <code>NEW</code> pseudo-rows.</p>

<p><strong>Validation example</strong>:</p>

<pre><code>DELIMITER //

CREATE TRIGGER trg_orders_validate_before_insert
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
  IF NEW.total &lt; 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Order total cannot be negative';
  END IF;

  IF NEW.customer_id IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'customer_id is required';
  END IF;
END //

DELIMITER ;</code></pre>

<p><code>SIGNAL SQLSTATE '45000'</code> raises a user-defined error that aborts the transaction.</p>

<p><strong>Audit example</strong> &mdash; the most common legitimate use:</p>

<pre><code>CREATE TABLE orders_audit (
  audit_id   INT AUTO_INCREMENT PRIMARY KEY,
  order_id   INT NOT NULL,
  action     ENUM('INSERT', 'UPDATE', 'DELETE'),
  old_total  DECIMAL(10, 2),
  new_total  DECIMAL(10, 2),
  changed_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  changed_by VARCHAR(100)
);

DELIMITER //

CREATE TRIGGER trg_orders_audit_insert
AFTER INSERT ON orders
FOR EACH ROW
INSERT INTO orders_audit (order_id, action, new_total, changed_by)
VALUES (NEW.id, 'INSERT', NEW.total, CURRENT_USER());

CREATE TRIGGER trg_orders_audit_update
AFTER UPDATE ON orders
FOR EACH ROW
INSERT INTO orders_audit (order_id, action, old_total, new_total, changed_by)
VALUES (NEW.id, 'UPDATE', OLD.total, NEW.total, CURRENT_USER());

CREATE TRIGGER trg_orders_audit_delete
AFTER DELETE ON orders
FOR EACH ROW
INSERT INTO orders_audit (order_id, action, old_total, changed_by)
VALUES (OLD.id, 'DELETE', OLD.total, CURRENT_USER());

DELIMITER ;</code></pre>

<p><strong>Trigger timing options</strong>:</p>

<table>
  <tr><th>Timing</th><th>Use for</th></tr>
  <tr><td><code>BEFORE INSERT/UPDATE</code></td><td>Validation, defaulting, normalization &mdash; can modify NEW</td></tr>
  <tr><td><code>AFTER INSERT/UPDATE</code></td><td>Audit, denormalized counters, side effects &mdash; NEW is committed</td></tr>
  <tr><td><code>BEFORE DELETE</code></td><td>Validation that depends on related data; rare</td></tr>
  <tr><td><code>AFTER DELETE</code></td><td>Audit, cascading cleanup not handled by FK</td></tr>
</table>

<p><strong>The arguments against triggers</strong>:</p>

<ul>
  <li><strong>Hidden behavior</strong> &mdash; an insert silently writes to multiple tables; new developers don&rsquo;t see it. Documentation and code review essential.</li>
  <li><strong>Hard to test</strong> &mdash; trigger logic in DB doesn&rsquo;t show up in application unit tests.</li>
  <li><strong>Performance cost</strong> &mdash; every write pays trigger overhead.</li>
  <li><strong>Migration complexity</strong> &mdash; pt-osc and gh-ost have constraints around triggers; some refactoring tools fight them.</li>
  <li><strong>Schema-version drift</strong> &mdash; trigger code lives in the DB and can fall out of sync with what the codebase expects.</li>
</ul>

<p><strong>Modern alternatives</strong>:</p>

<ul>
  <li><strong>Application-layer audit logs</strong> &mdash; explicit and testable; risk of forgetting paths.</li>
  <li><strong>Generated columns</strong> for derived values without the trigger overhead.</li>
  <li><strong>CHECK constraints</strong> (8.0.16+) for validation; declarative and visible in <code>SHOW CREATE TABLE</code>.</li>
  <li><strong>CDC streaming</strong> &mdash; <strong>Debezium</strong> reads binlog and produces change events; the audit "trigger" is a downstream subscriber. Cleaner separation of concerns.</li>
</ul>

<p><strong>Pragmatic stance</strong>: triggers are appropriate for <em>auditing</em> (where missing a write is unacceptable) and tight integrity validations (CHECK constraints often suffice now). For business logic, prefer application code; for change capture at scale, prefer CDC.</p>
'''

ANSWERS[70] = r'''
<p>InnoDB <strong>requires an index on every foreign key column</strong> &mdash; FK creation actually creates one automatically if no suitable index exists. The interesting questions are which index, and how to design it for the queries that use the FK.</p>

<p><strong>Why FK columns must be indexed</strong>:</p>

<ul>
  <li><strong>Cascade and set-null actions</strong> &mdash; <code>ON DELETE CASCADE</code> on the parent table requires scanning the child for matching rows. Without an index, this becomes a full table scan per parent delete &mdash; deleting one customer with 5000 orders becomes 5000 full scans.</li>
  <li><strong>Lock granularity</strong> &mdash; without an index, child-table modifications take broader locks (next-key locks across the table). With an index, locks are scoped to specific rows.</li>
  <li><strong>Reference checking</strong> &mdash; insert into child must verify the parent row exists; an index on the parent PK already does this. The child-side index helps the reverse direction (deletes from parent).</li>
</ul>

<pre><code>CREATE TABLE orders (
  id          INT PRIMARY KEY,
  customer_id INT NOT NULL,
  total       DECIMAL(10, 2),
  status      VARCHAR(20),

  CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE RESTRICT,

  -- Even without explicit INDEX, MySQL would auto-create one for the FK.
  -- But often you want a more specific composite for actual queries:
  INDEX idx_customer_status (customer_id, status)   -- supports FK + filter queries
);</code></pre>

<p>The composite index <code>(customer_id, status)</code> serves both the FK requirement <em>and</em> common queries like <em>"this customer&rsquo;s pending orders"</em> &mdash; one index doing two jobs.</p>

<p><strong>Indexing patterns for FK columns</strong>:</p>

<ul>
  <li><strong>Single-column index</strong> &mdash; default; covers FK requirement and basic <code>WHERE fk = ?</code> queries.</li>
  <li><strong>Composite leading with FK column</strong> &mdash; covers FK + a common filter or sort. Example: <code>(customer_id, created_at)</code> for "customer&rsquo;s recent orders".</li>
  <li><strong>Composite leading with selectivity column</strong> &mdash; if a different column is more selective, lead with it; FK column trails. The optimizer can still use the composite for FK enforcement.</li>
</ul>

<p><strong>Counter-intuitive cases</strong>:</p>

<ul>
  <li><strong>Auto-created index might not be the best one</strong> &mdash; create your preferred index <em>before</em> adding the FK, and MySQL won&rsquo;t auto-create a redundant one.</li>
  <li><strong>Multi-column FK</strong> &mdash; the index must lead with the same column order as the FK definition.</li>
</ul>

<p><strong>Operational hazards from missing or unhelpful FK indexes</strong>:</p>

<ul>
  <li><strong>Deleting from the parent locks the child for a long time</strong> &mdash; deletes that should be sub-millisecond take seconds, blocking other writes.</li>
  <li><strong>Deadlocks during cascades</strong> &mdash; broader locks intersect with other transactions&rsquo; locks.</li>
  <li><strong>Bulk deletes amplify the problem</strong> &mdash; even a small batch can stall the system.</li>
</ul>

<p><strong>Diagnose FK-related slowness</strong>:</p>

<pre><code>SHOW ENGINE INNODB STATUS\G
-- Look for "lock waits" pointing to FK-related operations.

EXPLAIN SELECT * FROM orders WHERE customer_id = 5;
-- type should be ref; key should be a FK index.</code></pre>

<p><strong>Cleanup of redundant FK indexes</strong>: don&rsquo;t blindly drop indexes that look duplicate &mdash; verify they&rsquo;re unused via <code>sys.schema_unused_indexes</code> first. An index that <code>EXPLAIN</code> picks may not be the one another query needs.</p>
'''

ANSWERS[71] = r'''
<p><code>mysqlbinlog</code> reads MySQL&rsquo;s binary log files (binlogs) and converts them to readable SQL or row-event output. Essential for point-in-time recovery, auditing what changed, and inspecting replication.</p>

<p><strong>Binary logs record every change</strong> &mdash; each <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code>, and DDL statement. Replication uses them; backups need them for PITR; investigations rely on them.</p>

<pre><code># Binlogs live in the data directory (or where log_bin specifies)
ls /var/lib/mysql/mysql-bin.*
# mysql-bin.000123  mysql-bin.000124  mysql-bin.index

# Read a binlog as SQL
mysqlbinlog mysql-bin.000123

# Filter by time range
mysqlbinlog \
  --start-datetime="2026-04-27 14:30:00" \
  --stop-datetime="2026-04-27 14:45:00" \
  mysql-bin.000123

# Filter by position (for very precise extraction)
mysqlbinlog \
  --start-position=4 \
  --stop-position=12345 \
  mysql-bin.000123</code></pre>

<p><strong>For ROW-format binlogs</strong> (default in 8.0), events are encoded as base64. The <code>--verbose</code> flag decodes them to readable pseudo-SQL:</p>

<pre><code>mysqlbinlog --base64-output=DECODE-ROWS --verbose mysql-bin.000123

# Output sample:
### UPDATE `shop`.`orders`
### WHERE
###   @1=42                   /* INT */
###   @2='pending'            /* VARCHAR */
###   @3=99.99                /* DECIMAL */
### SET
###   @1=42
###   @2='paid'
###   @3=99.99</code></pre>

<p><strong>Point-in-time recovery</strong> &mdash; the textbook PITR pattern:</p>

<pre><code># 1. Restore from the most recent full backup
xtrabackup --copy-back --target-dir=/backup/full

# 2. Replay binlogs from the backup&rsquo;s GTID/position to just before the bad event
mysqlbinlog \
  --start-datetime="2026-04-27 02:00:00" \
  --stop-datetime="2026-04-27 14:32:00" \
  mysql-bin.000123 mysql-bin.000124 mysql-bin.000125 \
  | mysql -u root -p

# Now the database is at exactly 14:32:00, just before "DROP TABLE oops" at 14:32:15.</code></pre>

<p><strong>Filter to specific tables or databases</strong>:</p>

<pre><code>mysqlbinlog --database=shop \
  --include-tables=shop.orders,shop.customers \
  mysql-bin.000123</code></pre>

<p><strong>GTID-based replay</strong> &mdash; the modern way:</p>

<pre><code>mysqlbinlog \
  --include-gtids='3E11FA47-71CA-11E1-9E33-C80AA9429562:23-1500' \
  mysql-bin.000123 mysql-bin.000124</code></pre>

<p><strong>Common operational uses</strong>:</p>

<ul>
  <li><strong>"Who deleted this row?"</strong> &mdash; <code>mysqlbinlog --base64-output=DECODE-ROWS --verbose</code> piped to grep for the row&rsquo;s PK shows the exact timestamp and the prior values.</li>
  <li><strong>Audit ad-hoc</strong> &mdash; production binlogs as a permanent change log; ship to S3 with retention.</li>
  <li><strong>Debugging replication breaks</strong> &mdash; inspect what the source sent vs what the replica applied.</li>
  <li><strong>Migration verification</strong> &mdash; after a refactor, count rows changed in binlog vs expected.</li>
</ul>

<p><strong>For programmatic consumption</strong>: <strong>Debezium</strong>, <strong>Maxwell</strong>, <strong>Canal</strong> read binlogs and produce streaming events to Kafka or other downstream consumers &mdash; the modern way to build CDC pipelines, search-index sync, audit warehouses.</p>

<p><strong>Configuration matters</strong>: binlogs only exist if <code>log_bin = ON</code>. Set <code>binlog_expire_logs_seconds</code> to retain enough history (e.g., 7 days = 604800) to cover backup recovery windows. Cloud-managed databases handle binlog retention via PITR settings.</p>
'''

ANSWERS[72] = r'''
<p>Cloning means producing a working copy of an existing database &mdash; for setting up a replica, refreshing a staging environment, or seeding a new instance. The right method depends on size, downtime tolerance, and whether the source can be paused.</p>

<p><strong>Method 1 &mdash; <code>mysqldump</code> + manual replica setup</strong> (small to medium databases):</p>

<pre><code># 1. Dump from the source with master-data flag
mysqldump -u root -p \
  --single-transaction \
  --routines --triggers --events \
  --master-data=2 \
  --set-gtid-purged=ON \
  --all-databases &gt; full.sql

# 2. Restore on the new instance
mysql -u root -p &lt; full.sql

# 3. The dump file contains the source binlog position as a comment:
# CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000123', MASTER_LOG_POS=1234;
# (or with GTIDs, just SOURCE_AUTO_POSITION = 1)

# 4. Configure replication on the clone
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = 'primary.host',
  SOURCE_USER = 'replicator',
  SOURCE_PASSWORD = '...',
  SOURCE_AUTO_POSITION = 1;
START REPLICA;</code></pre>

<p>Slow on TB-scale databases (hours to dump + hours to restore), and the source is read-locked during the dump unless <code>--single-transaction</code> handles it (InnoDB only).</p>

<p><strong>Method 2 &mdash; Percona XtraBackup</strong> (the standard for large databases):</p>

<pre><code># 1. Take a hot backup from the source (no locks held the whole time)
xtrabackup --backup --target-dir=/backup/clone --user=root --password=...

# 2. Apply log to make it consistent
xtrabackup --prepare --target-dir=/backup/clone

# 3. Copy to the new instance
rsync -av /backup/clone/ newhost:/var/lib/mysql/

# 4. Start the new instance
chown -R mysql:mysql /var/lib/mysql
systemctl start mysql

# 5. Set up replication using GTIDs from the backup
cat /var/lib/mysql/xtrabackup_binlog_info  # shows GTID position
CHANGE REPLICATION SOURCE TO ... SOURCE_AUTO_POSITION = 1;
START REPLICA;</code></pre>

<p>Backups are file-level &mdash; backup speed and restore speed both scale with disk throughput, not row count. Used widely for multi-TB clones.</p>

<p><strong>Method 3 &mdash; CLONE INSTANCE</strong> (MySQL 8.0.17+, the modern built-in way):</p>

<pre><code>-- On the source, install the clone plugin
INSTALL PLUGIN clone SONAME 'mysql_clone.so';

-- On the new instance (the recipient)
INSTALL PLUGIN clone SONAME 'mysql_clone.so';
SET GLOBAL clone_valid_donor_list = 'primary.host:3306';
CLONE INSTANCE FROM 'cloneuser'@'primary.host':3306
  IDENTIFIED BY 'password';
-- Restarts automatically into a clean clone state.</code></pre>

<p>Pure MySQL, no extra tools. Streams data files over the network; tracks position automatically; new instance becomes a working clone ready to be set up as a replica or run independently.</p>

<p><strong>Method 4 &mdash; Cloud snapshots</strong>:</p>

<ul>
  <li><strong>AWS RDS / Aurora snapshots</strong> &mdash; copy snapshot, restore to new instance, configure replication. The platform handles consistency.</li>
  <li><strong>Cloud SQL</strong> on GCP &mdash; same pattern.</li>
  <li><strong>EBS snapshot</strong> &mdash; for self-managed MySQL on EC2 with EBS-backed data directory.</li>
</ul>

<p>Near-instant for the snapshot creation; restore time is data transfer + warm-up.</p>

<p><strong>Setting up a cloned instance as a replica</strong>:</p>

<ol>
  <li>Ensure the source has <code>log_bin = ON</code> and <code>gtid_mode = ON</code>.</li>
  <li>Create a replication user on the source.</li>
  <li>After the clone, set <code>server_id</code> to a unique value on the new instance.</li>
  <li>Configure <code>CHANGE REPLICATION SOURCE TO ... SOURCE_AUTO_POSITION = 1</code> and <code>START REPLICA</code>.</li>
  <li>Monitor <code>SHOW REPLICA STATUS\G</code> until caught up.</li>
</ol>

<p><strong>Modern alternative for replica creation</strong>: managed services (RDS read replica, Aurora Replica, Cloud SQL replica) handle all of the above with one click. For self-managed, MySQL 8&rsquo;s CLONE INSTANCE is the cleanest built-in option; XtraBackup remains best for the largest databases.</p>
'''

ANSWERS[73] = r'''
<p>Connection pooling solves a fundamental problem: opening a TCP + TLS + auth handshake for every query is expensive, but holding one connection per concurrent request requires far more connections than MySQL can serve. The pool sits between application and DB, recycling a small set of connections across many requests.</p>

<p><strong>The math</strong>: opening a fresh MySQL connection is 10-100ms (TCP, TLS, auth, session setup). Reusing a pooled connection is microseconds. A web app handling 1000 req/sec with 5ms DB queries needs maybe 5 active connections &mdash; not 1000.</p>

<p><strong>Two pooling layers</strong>:</p>

<table>
  <tr><th>Layer</th><th>Examples</th><th>Notes</th></tr>
  <tr><td>Application-side pool</td><td>HikariCP (JVM), mysql2 pool (Node), SQLAlchemy pool (Python), Rails ActiveRecord pool</td><td>One pool per application instance; sized to expected concurrency</td></tr>
  <tr><td>Proxy-side pool</td><td>ProxySQL, MaxScale</td><td>Fronts MySQL; multiplexes thousands of app connections onto a small backend pool</td></tr>
</table>

<p>For a single-instance app, application-side is enough. For deployments with 100+ application servers each opening connections, ProxySQL prevents <code>max_connections</code> exhaustion and centralizes routing.</p>

<p><strong>Sizing the pool</strong>:</p>

<pre><code>pool_size = (cores × 2) + effective_disk_count
# A common rule of thumb (HikariCP guide). Most apps: 10-20 connections per instance.</code></pre>

<p>Larger pools mean more idle connections, more memory waste, more contention &mdash; not more throughput. The bottleneck is usually CPU and locking, not connection count.</p>

<p><strong>Application pool example &mdash; HikariCP</strong>:</p>

<pre><code>// Java / Spring Boot
HikariDataSource ds = new HikariDataSource();
ds.setJdbcUrl("jdbc:mysql://db.internal:3306/shop");
ds.setUsername("app");
ds.setPassword("...");
ds.setMaximumPoolSize(20);
ds.setMinimumIdle(5);
ds.setConnectionTimeout(30_000);   // ms to wait for a connection
ds.setIdleTimeout(600_000);        // close idle conns after 10 min
ds.setMaxLifetime(1_800_000);      // recycle conns every 30 min</code></pre>

<p><strong>Node.js mysql2 pool</strong>:</p>

<pre><code>const pool = mysql.createPool({
  host: 'db.internal', user: 'app', password: '...', database: 'shop',
  connectionLimit: 20,
  queueLimit: 0,
  idleTimeout: 600_000,
  enableKeepAlive: true,
});</code></pre>

<p><strong>ProxySQL example</strong> &mdash; sits in front of MySQL, app connects to ProxySQL:</p>

<pre><code># Configured via SQL on its admin port (6032)
INSERT INTO mysql_servers(hostgroup_id, hostname, port, max_connections)
VALUES (10, 'mysql.primary', 3306, 1000);

LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;

-- Add read-write split rules
INSERT INTO mysql_query_rules (rule_id, active, match_pattern, destination_hostgroup, apply)
VALUES (1, 1, '^SELECT.*FOR UPDATE', 10, 1),    -- to primary
       (2, 1, '^SELECT', 20, 1);                 -- to replica</code></pre>

<p>App opens 100 connections to ProxySQL; ProxySQL maintains ~20 to MySQL backend &mdash; 5x reduction in backend connection count.</p>

<p><strong>Critical settings on MySQL</strong>:</p>

<ul>
  <li><code>max_connections</code> &mdash; absolute server-side limit. Hitting it causes "Too many connections" errors. Default 151; production typical 500-2000.</li>
  <li><code>wait_timeout</code> &mdash; idle connection auto-close. Default 8 hours; some apps tune lower.</li>
  <li><code>interactive_timeout</code> &mdash; same for interactive (mysql client) sessions.</li>
  <li><code>thread_cache_size</code> &mdash; reuse threads when connections close.</li>
</ul>

<p><strong>Common pitfalls</strong>: opening a connection per request without pooling (especially in serverless contexts), not setting timeouts (idle connections accumulate), pool too large (RAM waste, contention), forgetting keep-alives across NAT or firewall boundaries (connections silently die).</p>
'''

ANSWERS[74] = r'''
<p>Distributed databases face an impossibility theorem (CAP) and a set of practical trade-offs around <strong>availability vs consistency vs latency</strong>. Single-instance MySQL gives strict ACID; distributing across nodes means choosing what to relax.</p>

<p><strong>Consistency models, from strongest to weakest</strong>:</p>

<table>
  <tr><th>Model</th><th>Guarantee</th></tr>
  <tr><td><strong>Strict serializability</strong></td><td>Transactions appear to execute in real-time order, atomically; matches single-node ACID</td></tr>
  <tr><td><strong>Linearizability</strong></td><td>Per-key reads always see the latest committed write</td></tr>
  <tr><td><strong>Snapshot isolation</strong></td><td>Each transaction sees a consistent snapshot; possible write skew</td></tr>
  <tr><td><strong>Read-your-writes</strong></td><td>A user sees their own writes, but might not see others&rsquo; latest</td></tr>
  <tr><td><strong>Eventual consistency</strong></td><td>If writes stop, all replicas converge eventually</td></tr>
</table>

<p><strong>The trade-offs</strong>:</p>

<ul>
  <li><strong>Stronger consistency = higher latency and lower availability</strong> &mdash; cross-region quorums require round-trips; partition events fail writes.</li>
  <li><strong>Weaker consistency = better latency and availability</strong> &mdash; but the application must handle stale reads, conflicts, race conditions.</li>
</ul>

<p><strong>Approaches with MySQL</strong>:</p>

<ul>
  <li><strong>Async replication (default)</strong> &mdash; eventual consistency. Replicas lag by milliseconds to seconds. Reads from replicas may be stale; writes go to primary.</li>
  <li><strong>Semi-synchronous replication</strong> &mdash; primary waits for at least one replica to acknowledge before commit returns. Protects against data loss in primary failures; doesn&rsquo;t guarantee replicas are in sync.</li>
  <li><strong>Group Replication</strong> (foundation of InnoDB Cluster) &mdash; quorum-based; majority must agree before commit. Strongly consistent within the group. Geographic distribution suffers (round-trip dominates write latency).</li>
</ul>

<p><strong>Two-phase commit (2PC)</strong> &mdash; coordinator asks all participants to prepare, then all commit. Provides atomicity across nodes. Drawbacks: slow (2x round-trips), fragile (coordinator failure mid-commit leaves participants blocked), not horizontally scalable. <em>XA transactions</em> in MySQL implement 2PC; rarely used in production for these reasons.</p>

<p><strong>Sagas &mdash; the modern pattern for cross-service transactions</strong>:</p>

<ol>
  <li>Break a logical transaction into local steps, each in its own transaction.</li>
  <li>Each step has a <em>compensating action</em> that undoes it.</li>
  <li>If a later step fails, run compensations for completed steps in reverse order.</li>
  <li>Coordinated by an orchestrator or via choreography (event-driven).</li>
</ol>

<p>Embraces eventual consistency; doesn&rsquo;t pretend to be ACID. Used for distributed business processes (order placement → payment → inventory → shipping).</p>

<p><strong>Stronger-consistency distributed databases</strong> &mdash; if your application genuinely needs ACID across geographic regions:</p>

<ul>
  <li><strong>CockroachDB</strong> &mdash; SQL-compatible (mostly Postgres dialect); strict serializability via Raft + hybrid logical clocks.</li>
  <li><strong>Google Spanner / AlloyDB</strong> &mdash; strict serializability with TrueTime hardware clocks.</li>
  <li><strong>YugabyteDB</strong> &mdash; PostgreSQL-compatible, Raft-based.</li>
  <li><strong>TiDB</strong> &mdash; MySQL-compatible distributed SQL; HTAP (transactional + analytical) workloads.</li>
</ul>

<p><strong>The pragmatic stance</strong>:</p>

<ul>
  <li>Single-region MySQL with replicas is enough for the vast majority of applications.</li>
  <li>If you genuinely need multi-region writes, consider whether your data model allows region-local primaries (per-customer region routing) rather than global ACID &mdash; usually cheaper.</li>
  <li>Distributed transactions across services should use sagas, not 2PC.</li>
  <li>Reach for a distributed SQL database only when measurement shows you need it. The operational cost is real.</li>
</ul>
'''

ANSWERS[75] = r'''
<p>Application-level sharding distributes data across multiple MySQL instances, with the application choosing which shard each row lives on. Used when a single primary can&rsquo;t serve write throughput &mdash; vertical scaling, replicas, partitioning, and caching have all been exhausted.</p>

<p><strong>The core decisions</strong>:</p>

<ol>
  <li><strong>Shard key</strong> &mdash; the column that determines placement. Should be present on every read query (otherwise you fan out to all shards).</li>
  <li><strong>Distribution function</strong> &mdash; how to map shard key values to shards.</li>
  <li><strong>Routing layer</strong> &mdash; where the shard decision happens.</li>
  <li><strong>Resharding plan</strong> &mdash; how to grow when one shard outgrows its capacity.</li>
</ol>

<p><strong>Distribution strategies</strong>:</p>

<table>
  <tr><th>Strategy</th><th>How</th><th>Trade-offs</th></tr>
  <tr><td>Hash-based</td><td><code>shard = hash(user_id) % N</code></td><td>Even distribution; resharding moves every key</td></tr>
  <tr><td>Range-based</td><td>users 1-1M on shard 1, 1M-2M on shard 2</td><td>Range queries possible; hot ranges create imbalance</td></tr>
  <tr><td>Directory / lookup</td><td>Lookup table maps each key to its shard</td><td>Most flexible; lookup table itself can become a bottleneck</td></tr>
  <tr><td>Consistent hashing</td><td>Hash to virtual nodes; resharding affects fewer keys</td><td>Better resharding properties; more complex to implement</td></tr>
</table>

<p><strong>Routing layer options</strong>:</p>

<ul>
  <li><strong>In application code</strong> &mdash; the simplest. The app picks a shard based on the shard key, opens a connection to that shard&rsquo;s database. Tightly coupled to data model; cross-shard queries done in the app.</li>
  <li><strong>ProxySQL</strong> &mdash; routes queries to shards based on regex rules over the SQL text. Works for simple shard-key patterns; struggles with complex queries.</li>
  <li><strong>Vitess</strong> &mdash; transparent sharding layer; speaks MySQL protocol so apps need few changes. Handles routing, cross-shard queries (where possible), resharding, and online schema changes. Used at YouTube, Slack, GitHub, Square.</li>
</ul>

<p><strong>Application-level shard routing example</strong>:</p>

<pre><code>// Simple hash-based router
function getShardConnection(userId) {
  const shardId = hashStr(userId.toString()) % NUM_SHARDS;
  return shardPools[shardId];
}

async function getUser(userId) {
  const conn = getShardConnection(userId);
  return conn.query('SELECT * FROM users WHERE id = ?', [userId]);
}

// Cross-shard aggregation — fan out, merge in app
async function totalActiveUsers() {
  const counts = await Promise.all(
    shardPools.map(p =&gt; p.query('SELECT COUNT(*) as c FROM users WHERE active=1'))
  );
  return counts.reduce((sum, [r]) =&gt; sum + r.c, 0);
}</code></pre>

<p><strong>What sharding costs you</strong>:</p>

<ul>
  <li><strong>No cross-shard JOINs</strong> &mdash; or build them in application code. Slow and fragile for anything non-trivial.</li>
  <li><strong>No global aggregates</strong> trivially &mdash; <code>SELECT COUNT(*)</code> over all users requires fan-out plus merge.</li>
  <li><strong>Distributed transactions</strong> &mdash; transferring data between users on different shards either uses 2PC (slow), sagas (eventual consistency), or just isn&rsquo;t allowed.</li>
  <li><strong>Resharding</strong> &mdash; outgrowing N shards is genuinely painful. Consistent hashing eases this; doesn&rsquo;t eliminate the data-movement step.</li>
  <li><strong>Operational complexity</strong> &mdash; backup, monitoring, failover, schema migrations all multiply by N.</li>
</ul>

<p><strong>Modern alternatives</strong>:</p>

<ul>
  <li><strong>Vitess</strong> + <strong>PlanetScale</strong> &mdash; managed Vitess; resharding via online migrations.</li>
  <li><strong>TiDB</strong> &mdash; MySQL-compatible distributed SQL with automatic sharding and global ACID. Skip explicit sharding entirely.</li>
  <li><strong>CockroachDB</strong>, <strong>YugabyteDB</strong> &mdash; distributed SQL (Postgres dialect, mostly).</li>
</ul>

<p><strong>The honest answer</strong>: most teams shouldn&rsquo;t shard. Hardware has gotten enormous &mdash; modern cloud instances handle 100K+ QPS and tens of TB. Push vertical scaling, read replicas, table partitioning, application caching, and archiving as far as possible. Sharding is a permanent operational tax; only take it on when measurement shows you need to.</p>
'''

ANSWERS[76] = r'''
<p>Mixed read/write workloads &mdash; typical OLTP &mdash; need a layered approach: route reads and writes differently, optimize each path, and protect them from each other. The patterns combine.</p>

<p><strong>Routing</strong> &mdash; the foundation:</p>

<table>
  <tr><th>Layer</th><th>What it does</th></tr>
  <tr><td><strong>ProxySQL / MaxScale</strong></td><td>Transparent read/write split based on query patterns; reads go to replicas, writes to the source</td></tr>
  <tr><td><strong>Application-level routing</strong></td><td>Two connection pools (writer / reader); explicit choice per query</td></tr>
  <tr><td><strong>Vitess / PlanetScale</strong></td><td>Built-in routing with shard awareness</td></tr>
  <tr><td><strong>Read-your-writes consistency</strong></td><td>Recently-written sessions stick to the source for a few seconds</td></tr>
</table>

<p><strong>Read path optimization</strong>:</p>
<ul>
  <li><strong>Buffer pool sized for reads</strong> &mdash; 50-70% RAM keeps hot data in memory, eliminating disk I/O on the common path.</li>
  <li><strong>Indexes covering hot queries</strong> &mdash; <code>EXPLAIN</code> should show <code>Using index</code> for queries that run thousands of times per second.</li>
  <li><strong>Read replicas</strong> for analytics, reports, and heavy queries.</li>
  <li><strong>Cache layer</strong> (Redis, Memcached) in front for query patterns that re-execute often with the same parameters &mdash; user profile, session, feature flags.</li>
</ul>

<p><strong>Write path optimization</strong>:</p>
<ul>
  <li><strong>Group commit</strong> &mdash; <code>innodb_flush_log_at_trx_commit = 1</code> + <code>binlog_group_commit_sync_delay = 1000</code> batches fsyncs across concurrent transactions.</li>
  <li><strong>Sequential primary keys</strong> &mdash; ULID, UUIDv7, KSUID, or auto-increment. Random PKs (UUIDv4) cause B-tree page splits on every insert.</li>
  <li><strong>Right number of indexes</strong> &mdash; each secondary index is rewritten on every insert/update. Drop unused ones.</li>
  <li><strong>Batch writes</strong> &mdash; multi-row INSERTs and bulk UPDATEs are 10-100× faster than per-row.</li>
</ul>

<p><strong>Protect them from each other</strong>:</p>
<ul>
  <li>Long analytical SELECTs on the source hold MVCC snapshots open, blocking purge and bloating undo. Send them to replicas.</li>
  <li>Write bursts cause replica lag, which makes reads stale. Throttle bulk writes (chunked migrations, background jobs) to bound the lag impact.</li>
  <li>Connection pools sized too high cause queueing under load &mdash; <strong>HikariCP</strong>&rsquo;s philosophy: a small, well-sized pool outperforms a large one. Typical: 10-20 connections per app instance.</li>
</ul>

<p><strong>Modern stack</strong>: cloud OLTP is usually <strong>Aurora MySQL</strong> or <strong>PlanetScale</strong> (auto-managed read replicas + managed proxy + storage that decouples I/O from compute). For self-hosted, <strong>InnoDB Cluster</strong> + <strong>ProxySQL</strong> is the standard mature setup; layer <strong>Redis</strong> in front for the hottest reads.</p>
'''

ANSWERS[77] = r'''
<p><strong>ENUM</strong> stores a string column whose value must be one of a fixed list, internally as a small integer index into that list. Compact and self-validating &mdash; but rigid.</p>

<pre><code>CREATE TABLE orders (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  status ENUM('pending', 'paid', 'shipped', 'delivered', 'cancelled')
         NOT NULL DEFAULT 'pending'
);
-- Stored as 1 byte (or 2 if &gt;255 values)
-- INSERT with invalid value: rejected with strict mode, silently '' otherwise</code></pre>

<table>
  <tr><th>Advantage</th><th>Disadvantage</th></tr>
  <tr><td>Compact (1-2 bytes vs. <code>VARCHAR</code>&rsquo;s string length)</td><td>Adding/removing/reordering values requires <code>ALTER TABLE</code></td></tr>
  <tr><td>Database-level validation &mdash; bad values rejected</td><td>Reordering changes underlying integer codes; corrupts comparisons</td></tr>
  <tr><td>Self-documenting &mdash; the values are visible in the schema</td><td>Each <code>ALTER</code> rewrites the table on older engines (instant in 8.0+)</td></tr>
  <tr><td>Faster than string comparison</td><td>Doesn&rsquo;t cross databases &mdash; PostgreSQL has a different ENUM model</td></tr>
  <tr><td>Sortable in declaration order &mdash; useful for status workflows</td><td>Localizing display values requires app-side mapping</td></tr>
</table>

<p><strong>The reordering trap</strong>:</p>

<pre><code>-- Original
status ENUM('pending', 'paid', 'shipped')
-- 'pending' = 1, 'paid' = 2, 'shipped' = 3

-- Reorder &mdash; data corruption!
status ENUM('paid', 'pending', 'shipped')
-- Now 1 = 'paid', 2 = 'pending'
-- All existing rows with stored value 1 (was 'pending') now read as 'paid'</code></pre>

<p>Always <em>append</em> values, never reorder. The ALTER for an append at the end is metadata-only in 8.0 and effectively free.</p>

<p><strong>When to use ENUM</strong>:</p>
<ul>
  <li>Truly fixed value sets that change rarely (yes/no, OK/error, sort directions).</li>
  <li>Status fields with a clear workflow.</li>
  <li>Performance-sensitive small-cardinality columns.</li>
</ul>

<p><strong>When to prefer a lookup table</strong>:</p>
<ul>
  <li>Set of values changes regularly &mdash; product types, regions, tags.</li>
  <li>Values have associated metadata (display name, color, sort order).</li>
  <li>You need internationalization or admin UI to manage the values.</li>
</ul>

<pre><code>-- Lookup-table alternative
CREATE TABLE order_statuses (
  code         VARCHAR(20) PRIMARY KEY,
  display_name VARCHAR(50) NOT NULL,
  is_terminal  BOOLEAN NOT NULL DEFAULT FALSE,
  sort_order   INT
);

ALTER TABLE orders
ADD COLUMN status_code VARCHAR(20) NOT NULL,
ADD CONSTRAINT fk_status FOREIGN KEY (status_code) REFERENCES order_statuses(code);</code></pre>

<p><strong>Modern stance</strong>: ENUMs are fine and underused for genuinely-fixed sets. Use them for status fields, mode flags, and similar &mdash; they prevent invalid data with zero overhead. Pick a lookup table when the set is dynamic or carries metadata.</p>
'''

ANSWERS[78] = r'''
<p><strong>BLOB</strong> (binary) and <strong>TEXT</strong> (text) types store large variable-length data:</p>

<table>
  <tr><th>Type</th><th>Max size</th><th>Storage</th></tr>
  <tr><td><code>TINYBLOB</code> / <code>TINYTEXT</code></td><td>255 bytes</td><td>1 byte length prefix</td></tr>
  <tr><td><code>BLOB</code> / <code>TEXT</code></td><td>64 KB</td><td>2 byte prefix</td></tr>
  <tr><td><code>MEDIUMBLOB</code> / <code>MEDIUMTEXT</code></td><td>16 MB</td><td>3 byte prefix</td></tr>
  <tr><td><code>LONGBLOB</code> / <code>LONGTEXT</code></td><td>4 GB</td><td>4 byte prefix</td></tr>
</table>

<p><strong>Storage behavior in InnoDB</strong>:</p>
<ul>
  <li>Small BLOBs (under ~700 bytes with default <code>innodb_page_size=16K</code>) live inline with the row.</li>
  <li>Larger BLOBs live in <strong>off-page overflow</strong> &mdash; the row holds a 20-byte pointer; the actual data is in separate pages.</li>
  <li>Off-page reads are extra I/O. Selecting a BLOB column means an extra page fetch.</li>
</ul>

<p><strong>The big practical guidance &mdash; almost always store BLOBs out of MySQL</strong>:</p>

<pre><code>-- ❌ Avoid
CREATE TABLE products (
  id    INT PRIMARY KEY,
  name  VARCHAR(100),
  image LONGBLOB    -- 5 MB image, makes every product row a multi-page fetch
);

-- ✅ Preferred
CREATE TABLE products (
  id        INT PRIMARY KEY,
  name      VARCHAR(100),
  image_url VARCHAR(500)    -- s3://bucket/products/123.jpg
);</code></pre>

<p><strong>Why</strong>:</p>
<ul>
  <li>Backup time blows up &mdash; mysqldump of a BLOB-heavy table can take hours.</li>
  <li>Buffer pool pressure &mdash; one big BLOB read evicts thousands of small rows.</li>
  <li>Replication overhead &mdash; binlog events with row images include the full BLOB.</li>
  <li>Object storage (S3, GCS, Azure Blob) is purpose-built: cheaper, scales independently, CDN-friendly.</li>
</ul>

<p><strong>When BLOB-in-MySQL is reasonable</strong>:</p>
<ul>
  <li>Small images / icons / thumbnails (&lt; 64 KB) where transactional consistency with the row matters.</li>
  <li>Generated documents (PDFs, signed reports) where audit trail is paramount.</li>
  <li>Cryptographic blobs &mdash; encrypted payloads, certificates &mdash; that need to be tied to a specific record.</li>
  <li>Embedded systems / single-tenant deployments where adding S3 is overkill.</li>
</ul>

<p><strong>If you must &mdash; isolate them</strong>:</p>

<pre><code>-- Vertical partition: BLOBs in a sidecar table
CREATE TABLE products (
  id   INT PRIMARY KEY,
  name VARCHAR(100),
  ...
);

CREATE TABLE product_images (
  product_id INT PRIMARY KEY,
  image      LONGBLOB,
  FOREIGN KEY (product_id) REFERENCES products(id)
);
-- Queries that don&rsquo;t need the image avoid the I/O cost</code></pre>

<p><strong>InnoDB row formats matter</strong>: <code>DYNAMIC</code> (default) and <code>COMPRESSED</code> store BLOBs entirely off-page; <code>COMPACT</code> and <code>REDUNDANT</code> store the first 768 bytes inline. Stick with <code>DYNAMIC</code> unless storage cost dominates.</p>
'''

ANSWERS[79] = r'''
<p><strong>Rate limiting</strong> caps how many requests a client can make per time window. Implementing it in MySQL is possible but rarely the right choice &mdash; <strong>Redis</strong> with its atomic counters is purpose-built for it. Still, a MySQL implementation is useful for small-scale apps or when Redis isn&rsquo;t available.</p>

<p><strong>Token bucket / fixed window in MySQL</strong>:</p>

<pre><code>CREATE TABLE rate_limits (
  identifier   VARCHAR(64)  NOT NULL,         -- user_id, IP, API key
  window_start DATETIME     NOT NULL,
  request_count INT          NOT NULL DEFAULT 1,
  PRIMARY KEY (identifier, window_start)
);

-- On each request:
INSERT INTO rate_limits (identifier, window_start, request_count)
VALUES (?, DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:00'), 1)
ON DUPLICATE KEY UPDATE request_count = request_count + 1;

-- Then read and check
SELECT request_count
FROM rate_limits
WHERE identifier = ?
  AND window_start = DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:00');
-- If &gt; threshold, reject the request</code></pre>

<p><code>DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:00')</code> rounds to the minute &mdash; one bucket per identifier per minute. The <code>ON DUPLICATE KEY UPDATE</code> increments atomically.</p>

<p><strong>Sliding window log</strong> &mdash; more accurate but heavier:</p>

<pre><code>CREATE TABLE request_log (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  identifier  VARCHAR(64) NOT NULL,
  timestamp   DATETIME(3) NOT NULL,
  INDEX idx_id_ts (identifier, timestamp)
);

-- On each request:
INSERT INTO request_log (identifier, timestamp) VALUES (?, NOW(3));

-- Check count in last 60 seconds:
SELECT COUNT(*) FROM request_log
WHERE identifier = ?
  AND timestamp &gt; NOW(3) - INTERVAL 60 SECOND;

-- Periodic cleanup
DELETE FROM request_log WHERE timestamp &lt; NOW() - INTERVAL 1 HOUR;</code></pre>

<p>Accurate but the table grows fast and DELETEs become hot.</p>

<p><strong>Why Redis is preferred</strong>:</p>

<table>
  <tr><th>Criterion</th><th>MySQL</th><th>Redis</th></tr>
  <tr><td>Latency per check</td><td>1-10 ms</td><td>0.1-1 ms</td></tr>
  <tr><td>QPS ceiling</td><td>10K-100K</td><td>100K-1M+ per node</td></tr>
  <tr><td>Atomic operations</td><td>Via INSERT...ON DUPLICATE KEY UPDATE</td><td>INCR, INCRBY, EVAL natively atomic</td></tr>
  <tr><td>Expiry</td><td>Manual cleanup job</td><td>Built-in TTL on keys</td></tr>
  <tr><td>Memory overhead</td><td>InnoDB overhead per row</td><td>Tens of bytes per counter</td></tr>
</table>

<p><strong>Redis equivalent</strong> is famously short:</p>

<pre><code>-- Lua for atomic check-and-increment
local current = redis.call('INCR', KEYS[1])
if current == 1 then redis.call('EXPIRE', KEYS[1], 60) end
if current &gt; tonumber(ARGV[1]) then return 0 end
return 1</code></pre>

<p><strong>When to do it in MySQL anyway</strong>:</p>
<ul>
  <li>Low-volume APIs (under 100 req/sec) where adding Redis isn&rsquo;t worth the operational cost.</li>
  <li>Per-user quotas with billing implications &mdash; you need durable, audit-friendly counters.</li>
  <li>Compliance requirements that demand the rate-limit ledger be durable and queryable.</li>
</ul>

<p>For high-traffic public APIs use Redis (or a managed limiter like <strong>Cloudflare</strong>, <strong>AWS API Gateway</strong>, <strong>Kong</strong>) and skip the database layer entirely.</p>
'''

ANSWERS[80] = r'''
<p><strong>High availability</strong> means the database tolerates failures of any single component without service interruption. The architecture combines redundancy, automated failover, and application-level resilience.</p>

<p><strong>Components of a typical HA MySQL stack</strong>:</p>

<table>
  <tr><th>Layer</th><th>Component</th><th>Purpose</th></tr>
  <tr><td>Topology</td><td>InnoDB Cluster (3+ nodes) or Group Replication</td><td>Quorum-based replication; auto-failover when source dies</td></tr>
  <tr><td>Routing</td><td>MySQL Router or ProxySQL</td><td>Routes connections to current primary; redirects after failover</td></tr>
  <tr><td>Failover orchestration</td><td>Orchestrator, MySQL Shell AdminAPI</td><td>Detects failure, promotes new primary, reconfigures replicas</td></tr>
  <tr><td>Connection retry</td><td>Application + connection pool</td><td>Retries with exponential backoff on transient failures</td></tr>
  <tr><td>Monitoring</td><td>PMM, Datadog, Prometheus</td><td>Alerts on lag, replication errors, disk space, slow queries</td></tr>
</table>

<p><strong>Self-hosted: InnoDB Cluster</strong>:</p>

<pre><code>// Set up via MySQL Shell
mysqlsh --user=admin
JS&gt; var cluster = dba.createCluster('myCluster')
JS&gt; cluster.addInstance('node2:3306')
JS&gt; cluster.addInstance('node3:3306')
JS&gt; cluster.status()
// Quorum: needs majority alive. 3 nodes tolerate 1 failure; 5 tolerate 2.</code></pre>

<p>The cluster combines Group Replication (Paxos consensus on every commit) with MySQL Router (transparent connection routing). Failover takes ~10 seconds with no manual intervention.</p>

<p><strong>Cloud-managed: simpler and stronger</strong>:</p>

<table>
  <tr><th>Service</th><th>HA mechanism</th><th>RPO / RTO</th></tr>
  <tr><td><strong>AWS Aurora MySQL</strong></td><td>Storage spread across 3 AZs (6 copies); compute can failover in seconds</td><td>RPO ~0 / RTO &lt; 30 s</td></tr>
  <tr><td><strong>RDS Multi-AZ</strong></td><td>Synchronous replication to standby in another AZ</td><td>RPO ~0 / RTO 1-2 min</td></tr>
  <tr><td><strong>Cloud SQL HA</strong></td><td>Regional persistent disks + standby</td><td>RPO ~0 / RTO &lt; 60 s</td></tr>
  <tr><td><strong>PlanetScale</strong></td><td>Vitess-managed; primary and replicas across regions</td><td>RPO ~0 / RTO &lt; 30 s</td></tr>
</table>

<p><strong>Application-level requirements</strong>:</p>
<ul>
  <li>Connection pool with per-connection timeout (5-10 sec).</li>
  <li>Retry transient errors (1213 deadlock, 2003 connection refused, 2006 server gone).</li>
  <li>Health check endpoint that runs <code>SELECT 1</code>; load balancer pulls unhealthy instances.</li>
  <li>Read-after-write consistency: route writes-followed-by-reads to the source for a few seconds (cookie-based, GTID-based with <code>WAIT_FOR_EXECUTED_GTID_SET</code>).</li>
</ul>

<p><strong>Disaster recovery</strong> &mdash; HA isn&rsquo;t the same as DR:</p>
<ul>
  <li><strong>HA</strong>: tolerate a node or AZ failure (minutes of downtime worst case).</li>
  <li><strong>DR</strong>: recover from total region failure or data corruption (hours acceptable).</li>
  <li>Cross-region replicas with delayed apply (~1 hour lag) protect against logical errors propagating immediately.</li>
  <li>Off-site backups (different cloud account, different region) test-restored quarterly.</li>
</ul>

<p><strong>Pragmatic guidance</strong>: most teams should use a managed service. The HA logic is the part where home-rolled solutions go wrong silently, often during the failure they&rsquo;re supposed to handle.</p>
'''

ANSWERS[81] = r'''
<p><strong>Optimizer trace</strong> shows exactly how MySQL evaluated alternative query plans and which it chose. Use it when <code>EXPLAIN</code> doesn&rsquo;t answer "why this plan and not the obvious one?".</p>

<pre><code>-- Enable for the session
SET optimizer_trace = 'enabled=on';
SET optimizer_trace_max_mem_size = 1000000;     -- bytes

-- Run the query
SELECT * FROM orders WHERE customer_id = 4221 AND status = 'paid';

-- Read the trace
SELECT TRACE FROM information_schema.OPTIMIZER_TRACE\G

-- Disable
SET optimizer_trace = 'enabled=off';</code></pre>

<p><strong>What the trace contains</strong>:</p>

<table>
  <tr><th>Section</th><th>Shows</th></tr>
  <tr><td><code>join_preparation</code></td><td>Initial query rewrites (subquery flattening, view expansion)</td></tr>
  <tr><td><code>join_optimization</code></td><td>Decisions: which indexes considered, ranges computed, costs estimated</td></tr>
  <tr><td><code>condition_processing</code></td><td>How <code>WHERE</code> clauses are simplified, propagated, decomposed</td></tr>
  <tr><td><code>rows_estimation</code></td><td>Cardinality estimate for each table/access path</td></tr>
  <tr><td><code>considered_execution_plans</code></td><td>Each plan with cost; the chosen one is marked</td></tr>
  <tr><td><code>join_execution</code></td><td>Sort/temp-table decisions made just before execution</td></tr>
</table>

<p>The output is JSON; pipe through <code>jq</code> or read in MySQL Workbench for a tree view.</p>

<p><strong>Common questions it answers</strong>:</p>
<ul>
  <li><em>Why isn&rsquo;t my index being used?</em> &mdash; the trace shows the alternative considered and the cost estimate the optimizer rejected. Often: the optimizer thinks a full scan is cheaper because cardinality stats are stale (<code>ANALYZE TABLE</code>).</li>
  <li><em>Why this join order?</em> &mdash; visible in <code>considered_execution_plans</code>; you can see why the alternative was costlier.</li>
  <li><em>Why a temp table or filesort?</em> &mdash; the trace shows where ordering and grouping decisions were made.</li>
</ul>

<p><strong>Combine with EXPLAIN ANALYZE</strong> &mdash; complementary tools:</p>

<table>
  <tr><th>Tool</th><th>What it tells you</th></tr>
  <tr><td><code>EXPLAIN</code></td><td>The plan as JSON</td></tr>
  <tr><td><code>EXPLAIN ANALYZE</code></td><td>Plan + actual time + actual rows per node (8.0+)</td></tr>
  <tr><td><code>OPTIMIZER_TRACE</code></td><td>Why this plan was chosen over alternatives</td></tr>
</table>

<p><strong>When you actually need it</strong>: about 5% of query-tuning sessions. For most queries, EXPLAIN reveals the issue and the fix; for the stubborn ones where the plan looks reasonable but is slow, optimizer trace is decisive.</p>

<p><strong>Limits</strong>: traces are large (often hundreds of KB). The session-scoped buffer keeps only the most recent traces. Don&rsquo;t leave it on in production &mdash; it has overhead and can flood logs.</p>
'''

ANSWERS[82] = r'''
<p>Production MySQL monitoring needs a layered metrics view: server health (CPU, RAM, disk), MySQL internals (QPS, connections, replication, buffer pool), and query-level performance (slow queries, top digests, anomalies).</p>

<p><strong>The metrics that actually matter</strong>:</p>

<table>
  <tr><th>Category</th><th>Key metrics</th></tr>
  <tr><td>Throughput</td><td>QPS, TPS, statements per second by type (SELECT/INSERT/UPDATE/DELETE)</td></tr>
  <tr><td>Latency</td><td>P50/P95/P99 query response time; events_statements_summary_by_digest</td></tr>
  <tr><td>Connections</td><td>Connections open, max used, threads_running, aborted_connects</td></tr>
  <tr><td>Buffer pool</td><td>Hit ratio (target &gt;99%), pages_dirty / pages_total, free pages</td></tr>
  <tr><td>Replication</td><td>Seconds_Behind_Source, retrieved_gtid_set vs executed_gtid_set</td></tr>
  <tr><td>Disk I/O</td><td>Read/write IOPS, latency per fs operation, free space</td></tr>
  <tr><td>Resource</td><td>CPU per core, memory used vs allocated, swap activity (should be 0)</td></tr>
  <tr><td>Errors</td><td>error log entries, deadlock count, lock wait timeouts, slow query count</td></tr>
</table>

<p><strong>Tooling stack</strong>:</p>

<ul>
  <li><strong>Percona PMM</strong> &mdash; free, MySQL-specific; deep dashboards, query analytics, the standard for self-hosted.</li>
  <li><strong>Prometheus + mysqld_exporter + Grafana</strong> &mdash; the open-source default for cloud-native deployments.</li>
  <li><strong>Datadog</strong>, <strong>New Relic</strong>, <strong>SolarWinds DPA</strong> &mdash; commercial APM with good MySQL coverage; integrate with broader app/infra monitoring.</li>
  <li>Cloud-native: <strong>RDS Performance Insights</strong>, <strong>Cloud SQL Insights</strong>, <strong>Azure Monitor</strong> &mdash; use them; managed services usually have better instrumentation than you can self-build.</li>
</ul>

<p><strong>Alerting thresholds</strong> &mdash; tuned to your SLOs, not generic defaults:</p>

<table>
  <tr><th>Condition</th><th>Action</th></tr>
  <tr><td>Replica lag &gt; 30s for 1 min</td><td>Page; investigate before alerts cascade</td></tr>
  <tr><td>Disk &gt; 85%</td><td>Notify (warning)</td></tr>
  <tr><td>Disk &gt; 95%</td><td>Page; provision more before MySQL halts</td></tr>
  <tr><td>Buffer pool hit ratio &lt; 95% sustained</td><td>Investigate working set size</td></tr>
  <tr><td>Connection count &gt; 80% of max</td><td>Investigate; possible app retry storm</td></tr>
  <tr><td>Long-running query (&gt; 5 min)</td><td>Notify; possible runaway analytics or stuck transaction</td></tr>
</table>

<p><strong>Query-level tracking</strong> &mdash; the highest leverage:</p>

<pre><code>-- Top 10 queries by total time, normalized by shape
SELECT
  ROUND(sum_timer_wait / 1e12, 2) AS total_seconds,
  count_star                       AS executions,
  ROUND(avg_timer_wait / 1e6, 2)  AS avg_ms,
  digest_text
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC
LIMIT 10;</code></pre>

<p>Tracked over time, this surfaces both new slow queries (regressions) and gradually-degrading queries (data growth outstripping indexes).</p>

<p><strong>Operational discipline</strong>: a dashboard you actually look at beats one nobody does. Keep one MySQL overview dashboard with 8-12 graphs that fit on a screen, plus drill-down dashboards by topic. Alert only on conditions that need human action; everything else goes on the dashboard.</p>
'''

ANSWERS[83] = r'''
<p><strong>User-defined functions (UDFs)</strong> are MySQL functions written in C/C++, compiled to a shared library, and loaded at runtime. They run inside the server process &mdash; very fast but with serious operational and security implications.</p>

<p><strong>UDF lifecycle</strong>:</p>

<pre><code>// 1. Write C code with the required entry points
my_bool my_func_init(UDF_INIT *initid, UDF_ARGS *args, char *message);
void   my_func_deinit(UDF_INIT *initid);
long long my_func(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error);

// 2. Compile to a shared library
gcc -shared -o my_func.so my_func.c -I/usr/include/mysql

// 3. Place in the plugin directory
sudo cp my_func.so /usr/lib/mysql/plugin/

// 4. Register in MySQL
CREATE FUNCTION my_func RETURNS INTEGER SONAME 'my_func.so';

// 5. Use it like any function
SELECT my_func(123) FROM dual;</code></pre>

<p><strong>Why anyone still uses UDFs</strong>:</p>
<ul>
  <li>Performance &mdash; native C runs orders of magnitude faster than stored functions for CPU-heavy operations (cryptographic hashes, custom math, regex).</li>
  <li>Integration with C/C++ libraries (geographic projections, machine learning inference).</li>
  <li>Aggregations not built into MySQL &mdash; e.g., percentile functions before they were native.</li>
</ul>

<p><strong>Why almost no one should</strong>:</p>

<table>
  <tr><th>Risk</th><th>Detail</th></tr>
  <tr><td>Crashes</td><td>A UDF bug crashes the entire mysqld process &mdash; downtime + recovery</td></tr>
  <tr><td>Security</td><td>Anyone with FILE + INSERT can install malicious UDFs &mdash; classic privilege escalation in 2010s breaches</td></tr>
  <tr><td>Replication</td><td>UDF must exist on every replica with same behavior; mismatch breaks consistency</td></tr>
  <tr><td>Upgrades</td><td>Recompile against new MySQL headers each upgrade</td></tr>
  <tr><td>Maintenance</td><td>Specialized C/C++ knowledge; few developers can debug</td></tr>
</table>

<p><strong>Modern alternatives that don&rsquo;t involve writing C</strong>:</p>

<ul>
  <li><strong>Move logic to the application layer</strong> &mdash; almost always the right answer. Read the data, compute in the app, write the result.</li>
  <li><strong>Use built-in functions</strong> &mdash; modern MySQL has native JSON, regex, window functions, spatial, and crypto functions that cover most historical UDF use cases.</li>
  <li><strong>Stored functions</strong> &mdash; slower than UDFs but no crash risk; written in SQL.</li>
  <li><strong>Database extensions in cloud-native systems</strong> &mdash; <strong>TiDB</strong> and <strong>SingleStore</strong> support more extensibility models that don&rsquo;t require C.</li>
  <li><strong>Sidecar service</strong> &mdash; a worker that consumes the binlog (Debezium → Kafka → consumer) does heavy compute and writes results back.</li>
</ul>

<p><strong>Production guidance</strong>: managed services (RDS, Aurora, Cloud SQL) typically don&rsquo;t allow custom UDFs precisely because of the crash and security risks. If you find yourself needing a UDF in 2026, it&rsquo;s worth questioning whether the architecture has a problem better solved elsewhere.</p>
'''

ANSWERS[84] = r'''
<p><strong>CHAR</strong> and <strong>VARCHAR</strong> both store strings; the difference is fixed vs. variable length and how each handles padding and storage overhead.</p>

<table>
  <tr><th>Aspect</th><th>CHAR(N)</th><th>VARCHAR(N)</th></tr>
  <tr><td>Storage</td><td>Always N characters (padded with spaces)</td><td>Length + actual bytes</td></tr>
  <tr><td>Length overhead</td><td>None</td><td>1 byte if N &lt; 256, 2 bytes otherwise</td></tr>
  <tr><td>Trailing space handling</td><td>Stripped on retrieval (default)</td><td>Preserved as written</td></tr>
  <tr><td>Updates</td><td>No row-size change</td><td>May change row size; can cause page splits</td></tr>
  <tr><td>Index efficiency</td><td>Slightly faster (fixed offset)</td><td>Marginally slower</td></tr>
  <tr><td>Best for</td><td>Truly fixed-length data</td><td>Variable-length text (the default)</td></tr>
</table>

<p><strong>Storage examples</strong> with utf8mb4 (worst-case 4 bytes/char):</p>

<ul>
  <li><code>CHAR(10)</code> storing <code>"abc"</code>: 40 bytes (always 10 chars × 4 bytes).</li>
  <li><code>VARCHAR(10)</code> storing <code>"abc"</code>: 13 bytes (1 length byte + 3 chars × 4 bytes).</li>
  <li><code>VARCHAR(255)</code> storing <code>"abc"</code>: 13 bytes (still 1 length byte + 3 chars).</li>
  <li><code>VARCHAR(256)</code> storing <code>"abc"</code>: 14 bytes (2 length bytes + 3 chars).</li>
</ul>

<p><strong>The trailing space gotcha</strong>:</p>

<pre><code>INSERT INTO t (c) VALUES ('hello   ');
-- CHAR column: stored, but retrieved as 'hello' (trailing spaces stripped)
-- VARCHAR column: stored as 'hello   ' and retrieved exactly

-- Comparisons ignore trailing spaces in both
SELECT 'hello' = 'hello   ';        -- 1 (true)
SELECT 'hello' = BINARY 'hello   '; -- 0 (false; binary keeps the spaces)</code></pre>

<p>To preserve trailing whitespace, use VARCHAR with a <code>BINARY</code> or <code>_bin</code> collation, or BLOB.</p>

<p><strong>When CHAR is right</strong>:</p>
<ul>
  <li>Country codes (<code>CHAR(2)</code> &mdash; 'US', 'GB', 'JP').</li>
  <li>State codes, currency codes, language codes.</li>
  <li>Hashes of fixed length (<code>CHAR(32)</code> for MD5, <code>CHAR(64)</code> for SHA-256).</li>
  <li>Yes/no flags as <code>CHAR(1)</code> (though <code>BOOLEAN</code>/<code>TINYINT</code> is usually better).</li>
</ul>

<p><strong>When VARCHAR is right</strong>: almost everything else &mdash; names, emails, URLs, descriptions. Variable-length data should use a variable-length type.</p>

<p><strong>The myth that VARCHAR(255) is special</strong>: this used to be the threshold below which length was stored in 1 byte instead of 2. The 1-byte savings is microscopic; modern advice is to size VARCHAR to the actual maximum reasonable length. <code>VARCHAR(40)</code> for emails, <code>VARCHAR(100)</code> for names, <code>VARCHAR(2000)</code> for URLs &mdash; deliberate sizing improves data quality and protects against pathological inputs.</p>

<p><strong>Storage strategy</strong>: with <code>utf8mb4_0900_ai_ci</code> (the modern default), VARCHAR length is in <em>characters</em>, not bytes. <code>VARCHAR(255)</code> can hold up to 255 characters (1020 bytes worst case). InnoDB row format <code>DYNAMIC</code> handles long values cleanly via off-page storage.</p>
'''

ANSWERS[85] = r'''
<p><strong>Versioning and history tracking</strong> means preserving previous values whenever a row changes. Useful for audit trails, "what did this look like 30 days ago?", undo functionality, and regulatory compliance. Several patterns; pick based on query needs.</p>

<table>
  <tr><th>Pattern</th><th>Storage shape</th><th>Best for</th></tr>
  <tr><td><strong>Audit table with full snapshots</strong></td><td>Separate <code>orders_history</code> table; row per change with all columns</td><td>Compliance, point-in-time queries</td></tr>
  <tr><td><strong>Audit table with JSON diffs</strong></td><td>Separate table; one column with old/new as JSON</td><td>Schemas that change shape often</td></tr>
  <tr><td><strong>Effective dating (temporal)</strong></td><td>Add <code>valid_from</code>/<code>valid_to</code> columns; one row per version</td><td>Slowly-changing dimensions; "as-of" queries</td></tr>
  <tr><td><strong>CDC-based</strong></td><td>External system (Kafka + warehouse) consumes binlog</td><td>Analytics, large-scale audit, no in-DB overhead</td></tr>
</table>

<p><strong>Pattern 1: snapshot history table via trigger</strong>:</p>

<pre><code>CREATE TABLE orders_history (
  history_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id       INT NOT NULL,
  status         VARCHAR(20),
  total          DECIMAL(10, 2),
  customer_id    INT,
  changed_at     DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  changed_by     INT,
  change_type    ENUM('insert', 'update', 'delete') NOT NULL,
  INDEX idx_order_time (order_id, changed_at)
);

DELIMITER //
CREATE TRIGGER trg_orders_audit
AFTER UPDATE ON orders FOR EACH ROW
BEGIN
  INSERT INTO orders_history (order_id, status, total, customer_id, changed_by, change_type)
  VALUES (OLD.id, OLD.status, OLD.total, OLD.customer_id, @app_user_id, 'update');
END //
DELIMITER ;</code></pre>

<p><strong>Pattern 2: JSON diffs</strong> &mdash; flexible across schema changes:</p>

<pre><code>CREATE TABLE orders_history (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  entity_id    INT NOT NULL,
  changed_at   DATETIME(3),
  changed_by   INT,
  before       JSON,
  after        JSON,
  INDEX idx_entity_time (entity_id, changed_at)
);
-- Query: "what changed about order 4221 between dates?"
SELECT changed_at,
       JSON_KEYS(JSON_OVERLAPS(before, after) - after) AS changed_fields,
       before, after
FROM orders_history
WHERE entity_id = 4221 AND changed_at BETWEEN ? AND ?;</code></pre>

<p><strong>Pattern 3: effective dating (temporal table emulation)</strong>:</p>

<pre><code>CREATE TABLE customer_address (
  customer_id  INT,
  address      VARCHAR(500),
  valid_from   DATE NOT NULL,
  valid_to     DATE,                   -- NULL = current
  PRIMARY KEY (customer_id, valid_from)
);

-- "What was the address on 2025-06-15?"
SELECT address FROM customer_address
WHERE customer_id = ?
  AND valid_from &lt;= '2025-06-15'
  AND (valid_to IS NULL OR valid_to &gt; '2025-06-15');</code></pre>

<p>Pattern useful for slowly-changing data &mdash; addresses, prices, tax rates &mdash; where queries genuinely need historical state, not just an audit log.</p>

<p><strong>Pattern 4: CDC streaming</strong> &mdash; the modern at-scale answer:</p>

<ul>
  <li><strong>Debezium</strong> consumes the MySQL binlog and emits each change to Kafka with full before/after images.</li>
  <li>Downstream consumers write to a data lake / warehouse (Snowflake, BigQuery, ClickHouse, Iceberg).</li>
  <li>Audit queries run there, not in OLTP.</li>
  <li>No trigger overhead; works for any table; supports schema evolution.</li>
</ul>

<p><strong>What to track</strong>: <code>changed_at</code>, <code>changed_by</code>, the operation, and either full snapshots or diffs. Always index by entity ID + time so "history for entity X" is a fast range scan.</p>

<p><strong>Retention</strong>: history tables grow forever. Partition by date; archive old partitions to cold storage; document retention per regulation (SOX, HIPAA, GDPR) and prune accordingly.</p>
'''

ANSWERS[86] = r'''
<p><strong>Real-time analytics</strong> means dashboards and reports that show data within seconds of changes happening in OLTP. MySQL is built for transactions, not analytics &mdash; making it serve both well requires architectural choices.</p>

<p><strong>The fundamental tension</strong>: OLTP queries are point lookups (1 row out of millions). Analytical queries scan millions of rows for aggregates. The same indexes that make point lookups fast slow down analytical scans, and vice versa.</p>

<table>
  <tr><th>Scale</th><th>Approach</th></tr>
  <tr><td>Small (&lt; 10M rows, simple aggregates)</td><td>Run analytics directly on the OLTP database; cache results</td></tr>
  <tr><td>Medium (10M-1B rows)</td><td>Read replicas dedicated to analytics; materialized aggregates refreshed via cron or events</td></tr>
  <tr><td>Large or strict latency</td><td>Stream data to a columnar store (ClickHouse, BigQuery, Snowflake); query there</td></tr>
</table>

<p><strong>Pattern 1: materialized aggregates</strong>:</p>

<pre><code>-- Hourly summary table
CREATE TABLE order_summary_hourly (
  hour_bucket DATETIME PRIMARY KEY,
  total_orders INT,
  total_revenue DECIMAL(12, 2),
  unique_customers INT,
  avg_order_value DECIMAL(10, 2)
);

-- Refresh job (event scheduler or external cron)
INSERT INTO order_summary_hourly
SELECT
  DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00') AS hour_bucket,
  COUNT(*) AS total_orders,
  SUM(total) AS total_revenue,
  COUNT(DISTINCT customer_id) AS unique_customers,
  AVG(total) AS avg_order_value
FROM orders
WHERE created_at &gt;= ? AND created_at &lt; ?
GROUP BY hour_bucket
ON DUPLICATE KEY UPDATE
  total_orders = VALUES(total_orders),
  total_revenue = VALUES(total_revenue),
  unique_customers = VALUES(unique_customers),
  avg_order_value = VALUES(avg_order_value);</code></pre>

<p>Dashboards query <code>order_summary_hourly</code> &mdash; thousands of rows instead of millions.</p>

<p><strong>Pattern 2: dedicated analytics replica</strong>:</p>

<ul>
  <li>One replica configured for analytics: more RAM, more cores, fewer indexes (or different ones), can have heavier queries.</li>
  <li>Routing layer sends OLTP traffic to source/main replicas; analytics queries to this replica.</li>
  <li>Replication lag (a few seconds) is acceptable for analytics use.</li>
</ul>

<p><strong>Pattern 3: streaming to a columnar warehouse</strong>:</p>

<pre><code>// Architecture
MySQL (OLTP) → binlog → Debezium → Kafka → consumer → ClickHouse / BigQuery
                                                       ↓
                                              Dashboards (Metabase, Looker, Grafana)</code></pre>

<p>The destination is purpose-built for analytical scans:</p>

<table>
  <tr><th>System</th><th>Strength</th></tr>
  <tr><td><strong>ClickHouse</strong></td><td>Self-hosted, columnar, blazing-fast analytical queries; replaces MySQL replicas for reporting</td></tr>
  <tr><td><strong>BigQuery</strong></td><td>Serverless, scales to PB; pay per query; tight Google Cloud integration</td></tr>
  <tr><td><strong>Snowflake</strong></td><td>Multi-cloud warehouse; separate compute/storage; widely adopted for BI</td></tr>
  <tr><td><strong>Apache Pinot</strong> / <strong>Druid</strong></td><td>Real-time OLAP &mdash; sub-second analytical queries on streaming data</td></tr>
</table>

<p><strong>Pattern 4: real-time materialized views</strong>:</p>

<ul>
  <li><strong>Materialize</strong>, <strong>RisingWave</strong>, <strong>ksqlDB</strong> consume change streams and continuously update SQL-defined views.</li>
  <li>Application reads the view; it&rsquo;s always up-to-date within milliseconds.</li>
  <li>Newer category; mature for stream processing.</li>
</ul>

<p><strong>Pragmatic guidance</strong>:</p>
<ul>
  <li>Start with materialized aggregates &mdash; covers 80% of cases with no extra infrastructure.</li>
  <li>Add a dedicated analytics replica when summary refresh becomes too expensive.</li>
  <li>Move to ClickHouse/BigQuery/Snowflake when analytical queries become the dominant workload or when answers need to span more data than MySQL can hold conveniently.</li>
  <li>Reach for stream-processing systems when "freshness within seconds" is a hard requirement.</li>
</ul>
'''

ANSWERS[87] = r'''
<p><strong>MySQL proxies</strong> sit between the application and the database, abstracting connection management, routing, and pool reuse. They&rsquo;re a key building block for HA, read/write splitting, and sharding without forcing every change into application code.</p>

<table>
  <tr><th>Proxy</th><th>Strengths</th><th>Use cases</th></tr>
  <tr><td><strong>ProxySQL</strong></td><td>Mature, configurable; query rewriting; connection pooling; query caching; firewalling</td><td>The default for self-hosted MySQL of any scale</td></tr>
  <tr><td><strong>MySQL Router</strong></td><td>Official; tight InnoDB Cluster integration; minimal config</td><td>Used as part of an InnoDB Cluster setup</td></tr>
  <tr><td><strong>MaxScale</strong> (MariaDB)</td><td>Plugin architecture; binlog routing for CDC; data masking</td><td>Mixed MariaDB/MySQL; complex routing rules</td></tr>
  <tr><td><strong>Vitess vtgate</strong></td><td>Sharding-aware; transparent resharding; cross-shard queries</td><td>Vitess deployments; massive scale</td></tr>
  <tr><td><strong>HAProxy</strong></td><td>L4 load balancing; not MySQL-aware</td><td>Simple round-robin; behind a smarter proxy</td></tr>
</table>

<p><strong>What ProxySQL does in practice</strong>:</p>

<pre><code>-- ProxySQL admin interface
mysql -h 127.0.0.1 -P 6032 -u admin -p

-- Define backend hosts
INSERT INTO mysql_servers(hostgroup_id, hostname, port) VALUES
  (10, 'mysql-primary',   3306),    -- writers
  (20, 'mysql-replica-1', 3306),    -- readers
  (20, 'mysql-replica-2', 3306);

-- Routing rules: SELECT goes to read group, everything else to write group
INSERT INTO mysql_query_rules(rule_id, match_pattern, destination_hostgroup, apply) VALUES
  (1, '^SELECT.*FOR UPDATE',  10, 1),     -- locking SELECTs to writer
  (2, '^SELECT',               20, 1),     -- other SELECTs to readers
  (3, '.*',                    10, 1);     -- everything else to writer

LOAD MYSQL SERVERS TO RUNTIME;
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
SAVE MYSQL QUERY RULES TO DISK;</code></pre>

<p>The application connects to ProxySQL on port 6033 and gets transparent routing. No code changes when topology changes.</p>

<p><strong>Connection pooling</strong> &mdash; the killer feature:</p>

<ul>
  <li>App opens 100 connections to ProxySQL; ProxySQL maintains 20 to MySQL.</li>
  <li>Connections are multiplexed &mdash; idle app connections don&rsquo;t hold backend connections.</li>
  <li>Massive savings on MySQL&rsquo;s per-connection memory (~1 MB each).</li>
</ul>

<p><strong>Other features that earn its keep</strong>:</p>

<ul>
  <li><strong>Query rewriting</strong> &mdash; fix bad queries without app deploys (kill a runaway, force an index).</li>
  <li><strong>Query firewall</strong> &mdash; block specific patterns (e.g., <code>UPDATE without WHERE</code>).</li>
  <li><strong>Query cache</strong> &mdash; cache results of expensive read-only queries with TTL.</li>
  <li><strong>Failover</strong> &mdash; reroute traffic when a backend dies; works with Orchestrator and InnoDB Cluster.</li>
  <li><strong>Per-user routing</strong> &mdash; analytics users go to dedicated replicas; admin connections to source.</li>
</ul>

<p><strong>Cloud reality</strong>: AWS RDS Proxy, Aurora&rsquo;s built-in router, and PlanetScale&rsquo;s vtgate provide most of these features as managed offerings. For self-hosted MySQL, ProxySQL is the de facto standard.</p>

<p><strong>Trade-offs</strong>: another component to monitor and patch; an extra hop in the request path (sub-millisecond, usually negligible); subtle bugs around prepared statements and connection state across multiplexing. Production deployments should HA the proxy itself &mdash; multiple ProxySQL instances behind a TCP load balancer or VIP.</p>
'''

ANSWERS[88] = r'''
<p><strong>Encrypted data</strong> in MySQL operates at three layers: at rest (on disk), in transit (network), and in application (column-level). Each protects against different threats.</p>

<table>
  <tr><th>Layer</th><th>Protects against</th><th>Mechanism</th></tr>
  <tr><td><strong>At rest</strong></td><td>Stolen disks, raw filesystem access</td><td>InnoDB tablespace encryption, filesystem encryption (LUKS), cloud volume encryption</td></tr>
  <tr><td><strong>In transit</strong></td><td>Network sniffing, MITM</td><td>TLS between client and server, between replicas</td></tr>
  <tr><td><strong>In application</strong></td><td>Compromised DBAs, leaked backups, multi-tenant data leaks</td><td>Encrypt before INSERT; only the app holds the key</td></tr>
</table>

<p><strong>InnoDB tablespace encryption (TDE)</strong> &mdash; transparent at-rest encryption:</p>

<pre><code>-- Setup (server-level keyring)
[mysqld]
early-plugin-load = keyring_file.so
keyring_file_data = /var/lib/mysql-keyring/keyring

-- Encrypt a single tablespace
ALTER TABLE customer_pii ENCRYPTION = 'Y';

-- New tables default to encrypted
SET default_table_encryption = ON;</code></pre>

<p>Production deployments use a real KMS-backed keyring (<strong>HashiCorp Vault</strong>, <strong>AWS KMS</strong>, <strong>Google Cloud KMS</strong>) instead of <code>keyring_file</code>. Cloud-managed MySQL handles this automatically.</p>

<p><strong>Column-level encryption</strong> &mdash; for fields like SSN, payment data:</p>

<pre><code>-- Built-in AES (server-side, key in mysqld memory)
SELECT AES_ENCRYPT('123-45-6789', UNHEX('A1B2C3...')) AS encrypted_ssn;

-- Decrypt
SELECT AES_DECRYPT(encrypted_ssn_column, UNHEX('A1B2C3...')) FROM customers;</code></pre>

<p>The catch: with the key in MySQL, anyone with access to MySQL can decrypt. The protection is partial &mdash; mainly against stolen backups.</p>

<p><strong>Stronger pattern: application-side encryption</strong>:</p>

<pre><code>// Application encrypts before insert; database never sees plaintext
const encrypted = aesGcmEncrypt(ssn, dataKey);  // dataKey from KMS
await db.query('INSERT INTO customers (ssn) VALUES (?)', [encrypted]);

// On read, decrypt in the application
const row = await db.query('SELECT ssn FROM customers WHERE id = ?', [id]);
const ssn = aesGcmDecrypt(row.ssn, dataKey);</code></pre>

<p>The trade-off: you can&rsquo;t SQL-search on encrypted columns. Workarounds:</p>

<ul>
  <li><strong>Deterministic encryption</strong> &mdash; same plaintext → same ciphertext, allows equality search but leaks frequency information.</li>
  <li><strong>Searchable encryption</strong> with a separate keyed-hash column for equality lookup.</li>
  <li><strong>Tokenization</strong> &mdash; replace sensitive values with non-sensitive tokens; lookup table in a separately-secured system.</li>
</ul>

<p><strong>Key management is the hard part</strong>:</p>

<ul>
  <li>Keys must be rotated regularly; old data stays accessible via key versioning.</li>
  <li>Keys never live in source code or configuration files.</li>
  <li>Use a KMS (AWS KMS, GCP KMS, HashiCorp Vault, Azure Key Vault) for envelope encryption: KMS holds the master key; data keys are wrapped by it.</li>
</ul>

<p><strong>Practical guidance for PII</strong>: encrypt sensitive columns at the application layer with envelope encryption. Use TDE as a defense-in-depth layer for the rest. Audit access to KMS keys &mdash; that audit trail is the actual defense.</p>

<p><strong>Compliance</strong>: PCI-DSS, HIPAA, GDPR all have specific encryption requirements that map to these patterns. Cloud-managed databases (Aurora, Cloud SQL) typically have compliance certifications that simplify the audit story considerably.</p>
'''

ANSWERS[89] = r'''
<p><strong>Geographic information system (GIS)</strong> queries answer questions like "stores within 10 km of this point", "which delivery zone contains this address", and "intersect this route with these regions". MySQL has native spatial support since 5.7+; full OpenGIS standard since 5.7+ with R-tree spatial indexes.</p>

<p><strong>Schema for points of interest</strong>:</p>

<pre><code>CREATE TABLE stores (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  name      VARCHAR(200),
  address   VARCHAR(500),
  location  POINT NOT NULL SRID 4326,        -- WGS-84 (lat-long)
  SPATIAL INDEX (location)
);

-- Insert with explicit SRID
INSERT INTO stores (name, address, location) VALUES (
  'Downtown Branch',
  '123 Main St',
  ST_GeomFromText('POINT(-73.9857 40.7484)', 4326)   -- (lng, lat)
);</code></pre>

<p>SRID 4326 is the WGS-84 standard for GPS lat/long. Note ordering: in MySQL, the default for GIS POINT is <code>POINT(longitude latitude)</code> &mdash; X first, Y second.</p>

<p><strong>Find stores within radius</strong>:</p>

<pre><code>-- Query: stores within 10km of a user location
SELECT
  id, name, address,
  ST_Distance_Sphere(
    location,
    ST_GeomFromText('POINT(-73.9857 40.7484)', 4326)
  ) / 1000 AS distance_km
FROM stores
WHERE ST_Distance_Sphere(
        location,
        ST_GeomFromText('POINT(-73.9857 40.7484)', 4326)
      ) &lt;= 10000
ORDER BY distance_km
LIMIT 20;</code></pre>

<p><code>ST_Distance_Sphere</code> uses great-circle distance on a sphere &mdash; fast and accurate enough for most use cases (errors &lt; 1% vs. ellipsoidal calculations).</p>

<p><strong>Bounding-box pre-filter</strong> &mdash; lets the spatial index do its job:</p>

<pre><code>-- Combine: spatial index narrows candidates; precise distance filters them
SET @user_point = ST_GeomFromText('POINT(-73.9857 40.7484)', 4326);
SET @bbox = ST_GeomFromText(
  'POLYGON((-74.1 40.6, -74.1 40.85, -73.9 40.85, -73.9 40.6, -74.1 40.6))',
  4326
);

SELECT id, name, ST_Distance_Sphere(location, @user_point) AS dist
FROM stores
WHERE MBRContains(@bbox, location)               -- spatial index hit
  AND ST_Distance_Sphere(location, @user_point) &lt;= 10000
ORDER BY dist;</code></pre>

<p>The <code>MBRContains</code> predicate uses the spatial index (R-tree); <code>ST_Distance_Sphere</code> filters precisely.</p>

<p><strong>Polygon containment &mdash; "which delivery zone contains this point?"</strong>:</p>

<pre><code>CREATE TABLE delivery_zones (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  area POLYGON NOT NULL SRID 4326,
  SPATIAL INDEX (area)
);

SELECT id, name
FROM delivery_zones
WHERE ST_Contains(area, ST_GeomFromText('POINT(-73.9857 40.7484)', 4326));</code></pre>

<p><strong>Other useful spatial functions</strong>:</p>

<table>
  <tr><th>Function</th><th>Purpose</th></tr>
  <tr><td><code>ST_Distance_Sphere(a, b)</code></td><td>Great-circle distance in meters (lat/lng)</td></tr>
  <tr><td><code>ST_Distance(a, b)</code></td><td>Cartesian distance &mdash; fine for projected coordinates</td></tr>
  <tr><td><code>ST_Contains(a, b)</code> / <code>ST_Within(b, a)</code></td><td>Polygon contains point</td></tr>
  <tr><td><code>ST_Intersects(a, b)</code></td><td>Two geometries share any space</td></tr>
  <tr><td><code>ST_Buffer(point, dist)</code></td><td>Generate a circle/polygon around a point</td></tr>
  <tr><td><code>ST_Length</code> / <code>ST_Area</code></td><td>Length of LineString / area of Polygon</td></tr>
</table>

<p><strong>When to step out of MySQL</strong>:</p>
<ul>
  <li><strong>PostGIS</strong> on PostgreSQL is the gold-standard for serious GIS work &mdash; far more functions, better optimizer, projection handling.</li>
  <li><strong>Elasticsearch</strong> with geo_point/geo_shape for high-throughput nearest-neighbor and aggregation.</li>
  <li><strong>Mapbox / Tile servers</strong> + <strong>S2</strong> / <strong>H3</strong> indexing for global-scale geo applications.</li>
</ul>

<p>For occasional "nearby" queries on hundreds of thousands of rows, MySQL spatial is plenty. For millions of polygons, complex projection math, or geographic-routing, look at PostGIS.</p>
'''

ANSWERS[90] = r'''
<p><strong>Large datasets</strong> &mdash; tables in the hundreds of millions or billions of rows &mdash; need a different mindset than the "just add an index" toolkit. The performance issues compound: query times grow, schema changes take hours, and operational tasks (backup, migration, restore) become projects.</p>

<p><strong>The four levers</strong>, in order of effort:</p>

<table>
  <tr><th>Lever</th><th>What it does</th></tr>
  <tr><td><strong>Index right</strong></td><td>Cover the hot queries; drop everything unused; minimize secondary index count</td></tr>
  <tr><td><strong>Partition</strong></td><td>Split by date; queries hit one partition; drop old partitions instantly</td></tr>
  <tr><td><strong>Archive</strong></td><td>Move cold data out of the hot table; smaller working set fits in buffer pool</td></tr>
  <tr><td><strong>Offload analytics</strong></td><td>Send to columnar warehouse (ClickHouse, BigQuery); MySQL only handles hot OLTP</td></tr>
</table>

<p><strong>Right-size the schema</strong>:</p>

<ul>
  <li><code>BIGINT</code> only if values exceed 2^31; <code>INT</code> saves 4 bytes/row × 1B rows = 4 GB.</li>
  <li><code>VARCHAR</code> sized to actual maximums &mdash; not <code>VARCHAR(255)</code> as a default.</li>
  <li>Avoid wide <code>TEXT</code>/<code>BLOB</code> columns inline; off-table or external storage.</li>
  <li>Drop unused columns with <code>ALTER TABLE ... DROP COLUMN, ALGORITHM=INSTANT</code>.</li>
</ul>

<p><strong>Partitioning strategy for time-series-like data</strong>:</p>

<pre><code>ALTER TABLE events
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p_2024_q4 VALUES LESS THAN (TO_DAYS('2025-01-01')),
  PARTITION p_2025_q1 VALUES LESS THAN (TO_DAYS('2025-04-01')),
  PARTITION p_2025_q2 VALUES LESS THAN (TO_DAYS('2025-07-01')),
  ...
  PARTITION p_max     VALUES LESS THAN MAXVALUE
);</code></pre>

<p>Queries with <code>WHERE created_at &gt; ?</code> hit only relevant partitions. Dropping a quarter is instant: <code>ALTER TABLE events DROP PARTITION p_2024_q4</code>.</p>

<p><strong>Archival pattern</strong>:</p>

<pre><code>-- Move old data to archive table, then delete from hot table
INSERT INTO orders_archive
SELECT * FROM orders
WHERE created_at &lt; '2023-01-01'
LIMIT 50000;

DELETE FROM orders
WHERE created_at &lt; '2023-01-01'
ORDER BY id LIMIT 50000;

-- Repeat in chunks to avoid long locks; commit between batches</code></pre>

<p>Better &mdash; partition + drop:</p>

<pre><code>ALTER TABLE orders DROP PARTITION p_2022_q1, p_2022_q2, ...;
-- Instant; no row-by-row delete</code></pre>

<p><strong>Operational concerns at scale</strong>:</p>

<ul>
  <li><strong>Backups</strong>: <code>mysqldump</code> doesn&rsquo;t scale past tens of GB. Use <strong>Percona XtraBackup</strong> for physical backups in minutes; cloud snapshots for managed services.</li>
  <li><strong>Schema changes</strong>: <code>ALTER TABLE ALGORITHM=INSTANT</code> for metadata-only changes (most common 8.0+); <strong>pt-online-schema-change</strong> or <strong>gh-ost</strong> for full rewrites.</li>
  <li><strong>Migrations</strong>: never <code>UPDATE table SET col = ...</code> on a billion rows in one statement &mdash; chunked batches with throttling.</li>
  <li><strong>Restore</strong>: practice restoring from backup at full size; restore time often surprises.</li>
</ul>

<p><strong>Read-heavy analytics</strong>: stop running them on the OLTP database. Stream changes to <strong>ClickHouse</strong>, <strong>BigQuery</strong>, or <strong>Snowflake</strong> via Debezium + Kafka. The analytical store is purpose-built for the scans; MySQL keeps responding to point lookups.</p>

<p><strong>When MySQL is genuinely outgrown</strong>: tens of TB working set, sustained 100K+ writes/sec, multi-region writes. Look at <strong>Vitess</strong> / <strong>PlanetScale</strong> for sharded MySQL, or <strong>TiDB</strong> / <strong>CockroachDB</strong> / <strong>Spanner</strong> for distributed alternatives. But this threshold is much higher than most teams assume &mdash; Stack Overflow famously ran for years on a single big MySQL instance.</p>
'''

ANSWERS[91] = r'''
<p><strong>Data retention policies</strong> codify how long different categories of data live in the active database vs. archive vs. deletion. They&rsquo;re a regulatory requirement (GDPR right-to-erasure, SOX retention windows, HIPAA), an operational hygiene practice (smaller working set), and a cost control (storage isn&rsquo;t free).</p>

<p><strong>Three retention dimensions</strong>:</p>

<table>
  <tr><th>Dimension</th><th>Question</th></tr>
  <tr><td>How long</td><td>Days, months, years &mdash; varies by data type and regulation</td></tr>
  <tr><td>Hot vs cold</td><td>How long in the active database vs. archive storage</td></tr>
  <tr><td>Deletion type</td><td>Hard delete vs. soft delete vs. anonymize vs. tombstone</td></tr>
</table>

<p><strong>Pattern 1: partition + drop</strong> &mdash; the most efficient for time-series data:</p>

<pre><code>-- Logs partitioned by month
CREATE TABLE access_logs (
  id BIGINT AUTO_INCREMENT,
  user_id INT,
  url VARCHAR(2000),
  ts DATETIME NOT NULL,
  PRIMARY KEY (id, ts)
)
PARTITION BY RANGE (TO_DAYS(ts)) (
  PARTITION p_2025_03 VALUES LESS THAN (TO_DAYS('2025-04-01')),
  PARTITION p_2025_04 VALUES LESS THAN (TO_DAYS('2025-05-01')),
  ...
);

-- Monthly retention job: drop the partition older than N months
ALTER TABLE access_logs DROP PARTITION p_2024_04;</code></pre>

<p>Instant &mdash; no row-by-row deletion, no long locks. The partition file is reclaimed immediately.</p>

<p><strong>Pattern 2: scheduled DELETE in batches</strong>:</p>

<pre><code>-- Event scheduler runs monthly
CREATE EVENT IF NOT EXISTS purge_old_sessions
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
  REPEAT
    DELETE FROM sessions
    WHERE last_activity &lt; NOW() - INTERVAL 30 DAY
    LIMIT 1000;
  UNTIL ROW_COUNT() = 0 END REPEAT;
END;</code></pre>

<p>Use when partitioning isn&rsquo;t feasible. Batch size keeps locks short and avoids replica lag.</p>

<p><strong>Pattern 3: soft delete + scheduled hard delete</strong>:</p>

<pre><code>-- Soft delete on user request
UPDATE customers SET deleted_at = NOW() WHERE id = ?;

-- App queries always filter:
SELECT * FROM customers WHERE deleted_at IS NULL;

-- Scheduled job hard-deletes after retention window
DELETE FROM customers
WHERE deleted_at IS NOT NULL
  AND deleted_at &lt; NOW() - INTERVAL 30 DAY;</code></pre>

<p>The soft-delete window allows recovery from accidental deletions; the hard delete enforces actual erasure.</p>

<p><strong>Pattern 4: anonymization</strong> &mdash; for data that must be retained but where personal info should be removed:</p>

<pre><code>UPDATE customers
SET email     = CONCAT('deleted-', id, '@example.invalid'),
    name      = 'Deleted User',
    phone     = NULL,
    address   = NULL,
    anonymized_at = NOW()
WHERE deleted_at &lt; NOW() - INTERVAL 30 DAY
  AND anonymized_at IS NULL;</code></pre>

<p>Order rows and analytics keep working (the customer_id stays); PII is gone. This satisfies most GDPR right-to-erasure scenarios while preserving business records.</p>

<p><strong>GDPR specifically</strong>:</p>
<ul>
  <li>Right-to-erasure (Article 17): user can request deletion; you have ~30 days.</li>
  <li>Data minimization: don&rsquo;t store what you don&rsquo;t need.</li>
  <li>Audit trail: log who requested deletion, when, what was deleted.</li>
  <li>Backups complicate things &mdash; either delete from backups too (rare) or document that backups expire on a published schedule.</li>
</ul>

<p><strong>Tools and infrastructure</strong>:</p>

<ul>
  <li><strong>MySQL Event Scheduler</strong> for simple schedules.</li>
  <li><strong>External cron / Kubernetes CronJob / Airflow</strong> for jobs needing visibility and alerts.</li>
  <li><strong>Apache Atlas</strong>, <strong>OpenLineage</strong>, <strong>Monte Carlo</strong> for data governance and lineage at scale.</li>
  <li>Cloud-native: <strong>S3 lifecycle policies</strong> + <strong>Glacier</strong> for archived data.</li>
</ul>

<p><strong>Document the policy</strong>: a retention policy that lives only in scripts and config is operationally fragile. Write it down: which table, what data, how long, what action (drop / anonymize / archive), regulatory basis. Audit annually.</p>
'''

ANSWERS[92] = r'''
<p><strong>Advanced text searching</strong> goes beyond exact match and <code>LIKE</code> patterns &mdash; relevance ranking, stemming ("running" matches "ran"), synonyms, fuzzy matching ("colour" matches "color"), and multi-language analyzers. MySQL FULLTEXT covers the basics; serious workloads usually move to a dedicated search engine.</p>

<p><strong>What MySQL FULLTEXT does well</strong>:</p>

<ul>
  <li>Natural-language search with relevance ranking (<code>MATCH ... AGAINST</code>).</li>
  <li>Boolean operators (<code>+required</code>, <code>-excluded</code>, <code>"phrase"</code>, <code>prefix*</code>).</li>
  <li>Query expansion (find related results based on initial matches).</li>
  <li>Acceptable for moderate-scale internal search (under ~1M rows).</li>
</ul>

<pre><code>-- Index multiple columns
ALTER TABLE products ADD FULLTEXT idx_search (name, description, tags);

-- Boolean search with required/excluded terms
SELECT id, name,
       MATCH(name, description, tags) AGAINST('+wireless +headphones -wired*' IN BOOLEAN MODE) AS score
FROM products
WHERE MATCH(name, description, tags) AGAINST('+wireless +headphones -wired*' IN BOOLEAN MODE)
ORDER BY score DESC
LIMIT 20;</code></pre>

<p><strong>What MySQL FULLTEXT doesn&rsquo;t do</strong>:</p>

<table>
  <tr><th>Need</th><th>Why MySQL falls short</th></tr>
  <tr><td>Stemming (run/running/ran)</td><td>Token matching only; no morphological analysis</td></tr>
  <tr><td>Synonyms (laptop/notebook)</td><td>No synonym dictionary support</td></tr>
  <tr><td>Fuzzy match / typo tolerance</td><td>Exact tokens only; "color" doesn&rsquo;t match "colour"</td></tr>
  <tr><td>Multi-language analyzers</td><td>Limited to English-style tokenization (and ngram for CJK)</td></tr>
  <tr><td>Faceted filtering</td><td>No native facet aggregations</td></tr>
  <tr><td>Highlighting matches</td><td>You compute it in the app</td></tr>
  <tr><td>Scale beyond 10M+ rows</td><td>Full-text index updates become expensive</td></tr>
</table>

<p><strong>Modern dedicated search engines</strong>:</p>

<table>
  <tr><th>Engine</th><th>Best for</th></tr>
  <tr><td><strong>Elasticsearch</strong> / <strong>OpenSearch</strong></td><td>De facto standard; rich features; complex deployment</td></tr>
  <tr><td><strong>Meilisearch</strong></td><td>Developer-friendly; typo tolerance built-in; ~5 minutes to deploy</td></tr>
  <tr><td><strong>Typesense</strong></td><td>Open-source; designed as Algolia alternative; instant search UX</td></tr>
  <tr><td><strong>Algolia</strong></td><td>Hosted; premium UX; expensive at scale</td></tr>
  <tr><td><strong>Apache Solr</strong></td><td>Older but mature; strong faceting</td></tr>
  <tr><td><strong>pgroonga</strong> (PostgreSQL extension)</td><td>If you&rsquo;re on Postgres; far better than PG&rsquo;s native FTS</td></tr>
</table>

<p><strong>Pattern: MySQL as source of truth, search engine as index</strong>:</p>

<pre><code>// Application architecture
MySQL (source of truth) → Debezium → Kafka → consumer → Elasticsearch (search index)

// On read:
1. App queries Elasticsearch for fast text search → returns IDs + score
2. App queries MySQL by IDs for current authoritative state
3. Results combined</code></pre>

<p>The search engine handles the hard text problems; MySQL stays as the durable transactional store. Updates flow one-way via change-data-capture; the systems can be operated independently.</p>

<p><strong>Vector search &mdash; the modern AI use case</strong>:</p>

<ul>
  <li>Semantic search using embedding vectors (text turned into 768-dim or 1536-dim vectors via OpenAI, Cohere, sentence-transformers).</li>
  <li>"Similar meaning" instead of "matching words" &mdash; finds related concepts even with no shared keywords.</li>
  <li>Specialized engines: <strong>Pinecone</strong>, <strong>Weaviate</strong>, <strong>Qdrant</strong>, <strong>Milvus</strong>, <strong>pgvector</strong> (Postgres).</li>
  <li>Combines well with traditional keyword search for hybrid retrieval.</li>
  <li>MySQL has no native vector index in 8.x; this is a common reason teams add a sidecar.</li>
</ul>

<p><strong>Pragmatic guidance</strong>: if requirements are <em>"users can search products by name and description"</em>, MySQL FULLTEXT is fine for under 1M rows. Once "as you type", "did you mean", or "similar to" enter the requirements, move to a dedicated search engine.</p>
'''

ANSWERS[93] = r'''
<p><strong>MySQL Event Scheduler</strong> runs SQL on a schedule inside the database &mdash; like cron, but for MySQL statements. Useful for housekeeping (purges, refreshes, summary updates) that doesn&rsquo;t need an external orchestrator.</p>

<pre><code>-- Enable the scheduler
SET GLOBAL event_scheduler = ON;

-- Or in my.cnf:
[mysqld]
event_scheduler = ON</code></pre>

<p><strong>Define an event</strong>:</p>

<pre><code>-- Run every day at 2 AM
CREATE EVENT IF NOT EXISTS purge_old_sessions
ON SCHEDULE EVERY 1 DAY
  STARTS TIMESTAMP(CURRENT_DATE, '02:00:00')
DO
  DELETE FROM sessions WHERE last_activity &lt; NOW() - INTERVAL 30 DAY;

-- Run every 15 minutes
CREATE EVENT refresh_dashboard_summary
ON SCHEDULE EVERY 15 MINUTE
DO
BEGIN
  TRUNCATE TABLE dashboard_summary;
  INSERT INTO dashboard_summary
  SELECT region, COUNT(*) AS orders, SUM(total) AS revenue
  FROM orders
  WHERE created_at &gt;= CURDATE()
  GROUP BY region;
END;

-- One-shot: run at a specific time
CREATE EVENT one_time_cleanup
ON SCHEDULE AT '2026-05-01 03:00:00'
DO
  DELETE FROM temp_imports WHERE imported_at &lt; '2026-05-01';</code></pre>

<p><strong>Inspect and manage</strong>:</p>

<pre><code>SHOW EVENTS;
SHOW EVENTS WHERE Name = 'purge_old_sessions'\G

-- Disable temporarily
ALTER EVENT purge_old_sessions DISABLE;

-- Reschedule
ALTER EVENT purge_old_sessions
ON SCHEDULE EVERY 6 HOUR;

-- Drop
DROP EVENT IF EXISTS purge_old_sessions;</code></pre>

<p><strong>Common use cases</strong>:</p>

<ul>
  <li>Purging old data (sessions, logs, soft-deleted rows past retention).</li>
  <li>Refreshing materialized aggregates (hourly/daily summary tables).</li>
  <li>Periodic maintenance: <code>OPTIMIZE TABLE</code>, <code>ANALYZE TABLE</code>.</li>
  <li>Statistics rotation: archive yesterday&rsquo;s metrics into a summary table.</li>
</ul>

<p><strong>Limitations</strong>:</p>

<table>
  <tr><th>Issue</th><th>Detail</th></tr>
  <tr><td>Replication-aware?</td><td>Events run on the source by default; replicas have them disabled. Set <code>ENABLE ON REPLICA</code> if you really want them on replicas.</td></tr>
  <tr><td>Visibility</td><td>Events run quietly; failures only show in the error log. No dashboard or notification by default.</td></tr>
  <tr><td>No retry on failure</td><td>If an event errors, it just doesn&rsquo;t run that occurrence.</td></tr>
  <tr><td>Single-threaded per event</td><td>Long events can overlap themselves; use <code>ON COMPLETION NOT PRESERVE</code> + idempotent design.</td></tr>
  <tr><td>Privileges</td><td>Need <code>EVENT</code> privilege; events run with the creator&rsquo;s privileges.</td></tr>
</table>

<p><strong>When external orchestrators are better</strong>:</p>

<ul>
  <li><strong>cron</strong> (or systemd timers) calling <code>mysql -e "..."</code> &mdash; visible logs, exit codes, easy to alert on failures.</li>
  <li><strong>Kubernetes CronJob</strong> &mdash; integrated with the cluster, retries, observability via Prometheus.</li>
  <li><strong>Airflow / Dagster / Prefect</strong> &mdash; full orchestration; dependencies between jobs; UI for runs and history.</li>
</ul>

<p><strong>Pragmatic guidance</strong>: use MySQL events for trivial maintenance (a daily DELETE, a 15-minute summary refresh) where you don&rsquo;t need observability beyond "did it work or not." For anything important &mdash; jobs whose failure matters, jobs that must run on time, jobs with dependencies &mdash; use an external orchestrator that gives you a paging-grade story when something breaks.</p>
'''

ANSWERS[94] = r'''
<p><strong>Query execution time</strong> management is the daily job of database operations: capture the slow ones, identify root causes, fix the worst offenders, prevent regressions. Performance work is iterative; the goal is a tight loop.</p>

<p><strong>Capture &mdash; the slow query log</strong>:</p>

<pre><code>SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 0.5;             -- 500 ms
SET GLOBAL log_queries_not_using_indexes = ON;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';</code></pre>

<p><strong>Aggregate with pt-query-digest</strong> (Percona Toolkit) &mdash; the standard tool:</p>

<pre><code>pt-query-digest /var/log/mysql/slow.log

# Output: top queries by total time, with normalized fingerprints,
# call count, average/max/p99 time, percent of total, sample query.</code></pre>

<p>Or query <code>events_statements_summary_by_digest</code> directly &mdash; same data, no log parsing:</p>

<pre><code>SELECT
  ROUND(sum_timer_wait / 1e12, 2) AS total_seconds,
  count_star                        AS executions,
  ROUND(avg_timer_wait / 1e6, 2)   AS avg_ms,
  ROUND(max_timer_wait / 1e6, 2)   AS max_ms,
  digest_text
FROM performance_schema.events_statements_summary_by_digest
WHERE schema_name = 'company'
ORDER BY sum_timer_wait DESC
LIMIT 20;</code></pre>

<p><strong>Identify &mdash; EXPLAIN ANALYZE</strong>:</p>

<pre><code>EXPLAIN ANALYZE
SELECT o.id, o.total, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.created_at &gt;= '2026-04-01' AND o.status = 'paid'
ORDER BY o.created_at DESC
LIMIT 100;

-- Output shows actual rows examined, time per node, total cost
-- Look for: full table scans, large rows-examined / rows-sent ratio,
-- mismatched estimates vs actuals.</code></pre>

<p><strong>The five typical fixes, in order</strong>:</p>

<table>
  <tr><th>Fix</th><th>When to apply</th></tr>
  <tr><td>1. Add an index</td><td>Most common &mdash; a hot query without index support</td></tr>
  <tr><td>2. Rewrite the query</td><td>Subquery → JOIN, OR → UNION, eliminate <code>SELECT *</code></td></tr>
  <tr><td>3. Update statistics</td><td><code>ANALYZE TABLE</code> when optimizer is choosing wrong</td></tr>
  <tr><td>4. Materialize aggregate</td><td>When the query is fundamentally expensive</td></tr>
  <tr><td>5. Move the workload</td><td>Read replicas, ClickHouse for analytics, cache for repeated reads</td></tr>
</table>

<p><strong>Common quick-wins</strong>:</p>

<ul>
  <li><code>WHERE YEAR(created_at) = 2026</code> → <code>WHERE created_at &gt;= '2026-01-01' AND created_at &lt; '2027-01-01'</code> (uses index).</li>
  <li><code>WHERE name LIKE '%foo%'</code> &mdash; can&rsquo;t use B-tree; use FULLTEXT index or external search.</li>
  <li><code>SELECT *</code> when you need 3 columns &mdash; ditch the rest, then a covering index becomes possible.</li>
  <li>Implicit type conversion: <code>WHERE phone = 1234567</code> on a VARCHAR column casts every row → forces full scan. Quote it.</li>
  <li>OR conditions across columns &mdash; rewrite as UNION ALL of indexed lookups.</li>
</ul>

<p><strong>Prevent regressions</strong>:</p>

<ul>
  <li><strong>EXPLAIN before merge</strong> &mdash; review query plans for new queries in code review.</li>
  <li><strong>CI checks</strong> &mdash; run new queries against a snapshot, verify they don&rsquo;t scan more than N rows.</li>
  <li><strong>Production sampling</strong> &mdash; send a small percentage of queries through EXPLAIN automatically; alert on full table scans.</li>
  <li><strong>Slow query alerting</strong> &mdash; trend the count of queries over <code>long_query_time</code>; alert when it spikes.</li>
</ul>

<p><strong>Tooling stack</strong>: <strong>Percona PMM Query Analytics</strong>, <strong>Datadog DBM</strong>, <strong>SolarWinds DPA</strong>, <strong>Sentry Performance</strong>, <strong>OpenTelemetry</strong> for tracing. The combination of slow query log + performance_schema + a continuous-monitoring tool covers most teams&rsquo; needs.</p>
'''

ANSWERS[95] = r'''
<p><strong>Recursive CTEs</strong> (Common Table Expressions, MySQL 8.0+) handle hierarchical and iterative computations &mdash; org charts, comment trees, file system traversal, graph walking, generating sequences. Two parts: an <em>anchor</em> query (the seed) and a <em>recursive</em> query that joins the CTE to itself.</p>

<pre><code>WITH RECURSIVE name(...) AS (
  -- Anchor: the starting rows
  SELECT ...

  UNION ALL

  -- Recursive: each iteration joins the previous level back to the source
  SELECT ...
  FROM source_table s
  JOIN name n ON ...
)
SELECT ... FROM name;</code></pre>

<p><strong>Example 1: traverse an org chart</strong>:</p>

<pre><code>WITH RECURSIVE subordinates AS (
  SELECT id, name, manager_id, 0 AS depth, CAST(name AS CHAR(500)) AS path
  FROM employees
  WHERE id = 100                               -- start: this manager

  UNION ALL

  SELECT e.id, e.name, e.manager_id, s.depth + 1,
         CONCAT(s.path, ' &gt; ', e.name)
  FROM employees e
  JOIN subordinates s ON e.manager_id = s.id   -- join previous level
  WHERE s.depth &lt; 100                          -- safety: bound depth
)
SELECT id, name, depth, path
FROM subordinates
ORDER BY path;</code></pre>

<p><strong>Example 2: generate a date series</strong>:</p>

<pre><code>WITH RECURSIVE date_series AS (
  SELECT '2026-01-01' AS d
  UNION ALL
  SELECT d + INTERVAL 1 DAY FROM date_series WHERE d &lt; '2026-12-31'
)
SELECT d FROM date_series;
-- 365 rows: every day in 2026</code></pre>

<p>Useful for filling gaps in time-series reports &mdash; LEFT JOIN against the date series so missing days show up as zeros instead of being absent.</p>

<p><strong>Example 3: graph cycle detection</strong>:</p>

<pre><code>WITH RECURSIVE traversal AS (
  SELECT from_node, to_node,
         CAST(CONCAT(from_node, '-', to_node) AS CHAR(1000)) AS path,
         0 AS cycle
  FROM edges WHERE from_node = 'A'

  UNION ALL

  SELECT t.from_node, e.to_node,
         CONCAT(t.path, ',', e.to_node),
         IF(FIND_IN_SET(e.to_node, t.path) &gt; 0, 1, 0)
  FROM traversal t
  JOIN edges e ON e.from_node = t.to_node
  WHERE t.cycle = 0 AND CHAR_LENGTH(t.path) &lt; 500
)
SELECT * FROM traversal WHERE cycle = 1;
-- Returns paths that loop back to a previously-visited node</code></pre>

<p><strong>Performance considerations</strong>:</p>

<table>
  <tr><th>Concern</th><th>Detail</th></tr>
  <tr><td>Termination</td><td>Recursive CTE must produce zero new rows eventually; otherwise infinite</td></tr>
  <tr><td><code>cte_max_recursion_depth</code></td><td>Default 1000; bumped via <code>SET cte_max_recursion_depth = 10000</code></td></tr>
  <tr><td>Materialization</td><td>Each iteration is materialized; deep / wide trees use memory</td></tr>
  <tr><td>Indexes matter</td><td>The recursive join hits the source table on every iteration; index the join column</td></tr>
  <tr><td>No optimization across iterations</td><td>The optimizer plans once; can&rsquo;t reorder iterations</td></tr>
</table>

<p><strong>When to consider alternatives</strong>:</p>

<ul>
  <li><strong>Closure tables</strong> &mdash; if you query the hierarchy thousands of times per second, materialize all (ancestor, descendant) pairs in a separate table; lookups become O(1).</li>
  <li><strong>Path enumeration</strong> &mdash; store the full path as a string column; ranges via LIKE.</li>
  <li><strong>Graph databases</strong> &mdash; <strong>Neo4j</strong>, <strong>Amazon Neptune</strong>, <strong>JanusGraph</strong> for genuinely deep / many-to-many graph workloads.</li>
  <li><strong>PostgreSQL ltree</strong> &mdash; if hierarchical queries dominate, Postgres&rsquo;s ltree extension is significantly more powerful than MySQL CTEs.</li>
</ul>

<p><strong>Idiomatic patterns</strong>:</p>

<ul>
  <li>Always include a <strong>depth</strong> column &mdash; lets you limit, sort, or visualize.</li>
  <li>Always include a <strong>safety bound</strong> (<code>WHERE depth &lt; N</code>) &mdash; protects against malformed data causing infinite recursion.</li>
  <li>Track a <strong>path</strong> column for ordering tree results, debugging, or detecting cycles.</li>
  <li>Use <code>UNION ALL</code> (not <code>UNION</code>) &mdash; deduplication is rarely needed and adds an expensive sort.</li>
</ul>
'''

ANSWERS[96] = r'''
<p><strong>Aggregation and analysis</strong> is what databases turn raw rows into summaries: sums, counts, averages, percentiles, time-bucketed metrics. MySQL&rsquo;s SQL gives you simple aggregates, GROUP BY, window functions, and JSON aggregations &mdash; enough for most operational analysis.</p>

<table>
  <tr><th>Operation</th><th>Function / clause</th></tr>
  <tr><td>Standard aggregates</td><td><code>COUNT</code>, <code>SUM</code>, <code>AVG</code>, <code>MIN</code>, <code>MAX</code>, <code>STDDEV</code>, <code>VAR</code></td></tr>
  <tr><td>Distinct counts</td><td><code>COUNT(DISTINCT col)</code> &mdash; expensive at scale</td></tr>
  <tr><td>Conditional</td><td><code>SUM(CASE WHEN ... THEN 1 ELSE 0 END)</code> or <code>SUM(condition)</code></td></tr>
  <tr><td>String aggregation</td><td><code>GROUP_CONCAT(col ORDER BY ... SEPARATOR ', ')</code></td></tr>
  <tr><td>JSON aggregation</td><td><code>JSON_ARRAYAGG</code>, <code>JSON_OBJECTAGG</code></td></tr>
  <tr><td>Window functions</td><td><code>OVER (PARTITION BY ... ORDER BY ...)</code> &mdash; running totals, ranks, lags</td></tr>
  <tr><td>Multi-level</td><td><code>WITH ROLLUP</code> &mdash; subtotals + grand total in one query</td></tr>
</table>

<p><strong>Standard aggregation</strong>:</p>

<pre><code>SELECT
  region,
  COUNT(*)                                AS orders,
  SUM(total)                              AS revenue,
  AVG(total)                              AS avg_order,
  COUNT(DISTINCT customer_id)             AS customers,
  SUM(CASE WHEN status = 'paid' THEN total ELSE 0 END) AS paid_revenue
FROM orders
WHERE created_at &gt;= CURDATE() - INTERVAL 30 DAY
GROUP BY region
ORDER BY revenue DESC;</code></pre>

<p><strong>Window functions</strong> &mdash; running totals, ranks, time series:</p>

<pre><code>-- 7-day moving average of daily revenue
SELECT
  DATE(created_at) AS day,
  SUM(total)       AS daily_revenue,
  AVG(SUM(total)) OVER (
    ORDER BY DATE(created_at)
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rev_7day_avg
FROM orders
GROUP BY DATE(created_at)
ORDER BY day;

-- Customer rank by revenue, by region
SELECT
  region, customer_id,
  SUM(total) AS revenue,
  RANK() OVER (PARTITION BY region ORDER BY SUM(total) DESC) AS region_rank
FROM orders
GROUP BY region, customer_id;</code></pre>

<p><strong>WITH ROLLUP &mdash; subtotals in one pass</strong>:</p>

<pre><code>SELECT region, status, COUNT(*) AS orders, SUM(total) AS revenue
FROM orders
GROUP BY region, status WITH ROLLUP;

-- Output:
-- ('North', 'paid', 50, 5000)
-- ('North', 'cancelled', 10, 0)
-- ('North', NULL, 60, 5000)            ← subtotal for North
-- ('South', 'paid', 30, 3000)
-- ('South', NULL, 30, 3000)            ← subtotal for South
-- (NULL, NULL, 90, 8000)                ← grand total</code></pre>

<p>Use <code>GROUPING(col)</code> to distinguish ROLLUP-generated NULLs from real NULLs.</p>

<p><strong>JSON aggregation</strong> &mdash; modern API-shaped output:</p>

<pre><code>-- Build a per-customer summary as JSON
SELECT
  c.id,
  c.name,
  JSON_OBJECT(
    'order_count', COUNT(o.id),
    'total_spent', SUM(o.total),
    'orders', JSON_ARRAYAGG(JSON_OBJECT('id', o.id, 'date', o.created_at, 'amount', o.total))
  ) AS profile
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;</code></pre>

<p>Returns one JSON document per customer &mdash; shape ready for a REST API response.</p>

<p><strong>Percentiles and median &mdash; what MySQL doesn&rsquo;t give natively</strong>:</p>

<pre><code>-- Approximate median via window functions
WITH ranked AS (
  SELECT total, ROW_NUMBER() OVER (ORDER BY total) AS rn,
                COUNT(*)    OVER ()                AS total_count
  FROM orders
  WHERE created_at &gt;= CURDATE() - INTERVAL 30 DAY
)
SELECT AVG(total) AS median
FROM ranked
WHERE rn IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2));

-- For percentiles, use PERCENT_RANK or compute manually
SELECT total
FROM (
  SELECT total, PERCENT_RANK() OVER (ORDER BY total) AS pct
  FROM orders
) r
WHERE pct &gt;= 0.95
ORDER BY total
LIMIT 1;
-- 95th percentile order total</code></pre>

<p>PostgreSQL has native <code>PERCENTILE_CONT</code> / <code>PERCENTILE_DISC</code>; MySQL doesn&rsquo;t (yet). For heavy percentile work, consider doing the math in the application or in a columnar warehouse.</p>

<p><strong>When to step out of MySQL</strong>:</p>

<ul>
  <li><strong>ClickHouse</strong>, <strong>Druid</strong>, <strong>Apache Pinot</strong> &mdash; sub-second analytics on billions of rows; built for aggregation.</li>
  <li><strong>BigQuery</strong>, <strong>Snowflake</strong>, <strong>Redshift</strong> &mdash; cloud warehouses; scale to PB; pay per query.</li>
  <li><strong>DuckDB</strong> &mdash; embedded analytical SQL; great for app-side aggregation over CSV / Parquet.</li>
  <li>For real-time analytics over streaming data, <strong>Materialize</strong> or <strong>RisingWave</strong> maintain SQL views continuously.</li>
</ul>

<p><strong>Pragmatic guidance</strong>: MySQL handles aggregation up to a couple hundred GB and tens of millions of rows comfortably. Beyond that, the right answer is to ship the data to a columnar store and query there; keep MySQL for transactions.</p>
'''

ANSWERS[97] = r'''
<p><strong>Parallel query execution</strong> &mdash; multiple CPU cores working on a single query &mdash; has historically been weak in MySQL. Most queries use one thread regardless of how many cores the server has. MySQL 8.0+ has added parallelism for some operations, but the overall story is "limited compared to dedicated analytical databases."</p>

<p><strong>What MySQL 8 does in parallel</strong>:</p>

<table>
  <tr><th>Operation</th><th>Parallelism</th></tr>
  <tr><td>Multiple concurrent queries</td><td>Each gets its own thread &mdash; this scales fine across cores</td></tr>
  <tr><td><code>SELECT COUNT(*)</code> on InnoDB</td><td>Parallel scan via <code>innodb_parallel_read_threads</code> (default 4)</td></tr>
  <tr><td><code>CHECK TABLE</code></td><td>Parallel checks of partitions</td></tr>
  <tr><td>Replication apply</td><td>Parallel via <code>replica_parallel_workers</code> (default 4)</td></tr>
  <tr><td>Most other SELECTs</td><td>Single-threaded execution</td></tr>
</table>

<p><strong>Configuration</strong>:</p>

<pre><code>SET innodb_parallel_read_threads = 8;       -- per-query parallel scan threads
SET replica_parallel_workers = 16;          -- replication apply parallelism
SET replica_parallel_type = 'LOGICAL_CLOCK';</code></pre>

<p>The <code>innodb_parallel_read_threads</code> setting helps for full-table scans on large tables &mdash; <code>SELECT COUNT(*)</code> can use 4-8× more cores. Doesn&rsquo;t affect indexed lookups, ORDER BY, GROUP BY, JOINs &mdash; those stay single-threaded.</p>

<p><strong>Patterns to extract parallelism without engine support</strong>:</p>

<p><strong>Pattern 1: chunk and scatter-gather in the application</strong>:</p>

<pre><code>// Split the work into chunks and run them in parallel
const chunks = [
  { from: 1,        to: 100000 },
  { from: 100001,   to: 200000 },
  { from: 200001,   to: 300000 },
];

const results = await Promise.all(chunks.map(c =&gt;
  db.query(
    `SELECT SUM(total) AS sum FROM orders WHERE id BETWEEN ? AND ?`,
    [c.from, c.to]
  )
));

const total = results.reduce((sum, r) =&gt; sum + r[0].sum, 0);</code></pre>

<p>Each query runs single-threaded, but the application coordinates them across separate connections &mdash; using all available cores on the database server. Works for any aggregation that&rsquo;s decomposable.</p>

<p><strong>Pattern 2: per-partition queries</strong>:</p>

<pre><code>-- Table partitioned by month
SELECT SUM(total) FROM orders PARTITION (p_2026_04);
-- Run each partition in parallel from the application; sum results</code></pre>

<p><strong>Pattern 3: read replicas as parallel workers</strong>:</p>

<pre><code>// Hash-partition the workload across replicas
worker1: SELECT ... FROM orders WHERE id % 4 = 0
worker2: SELECT ... FROM orders WHERE id % 4 = 1
worker3: SELECT ... FROM orders WHERE id % 4 = 2
worker4: SELECT ... FROM orders WHERE id % 4 = 3</code></pre>

<p>Each replica handles a slice; combine results in the application.</p>

<p><strong>When parallelism really matters &mdash; use the right tool</strong>:</p>

<table>
  <tr><th>System</th><th>Parallelism approach</th></tr>
  <tr><td><strong>ClickHouse</strong></td><td>Native MPP; scans use all cores; perfect for analytical workloads</td></tr>
  <tr><td><strong>BigQuery</strong></td><td>Massively parallel by design; thousands of slots</td></tr>
  <tr><td><strong>Snowflake</strong></td><td>Multi-cluster warehouses scale per workload</td></tr>
  <tr><td><strong>DuckDB</strong></td><td>Embedded analytical engine; great for app-side parallel queries</td></tr>
  <tr><td><strong>Apache Spark</strong></td><td>Distributed compute over MySQL via JDBC source</td></tr>
  <tr><td><strong>Vitess</strong> / <strong>TiDB</strong></td><td>Distributed MySQL-compatible; scatter-gather across shards</td></tr>
</table>

<p><strong>Pragmatic guidance</strong>: don&rsquo;t expect MySQL to magically use 32 cores for one query. Either keep query work small enough to be single-thread-bounded, parallelize at the application level for embarrassingly parallel work, or move analytical work to a columnar engine. For OLTP, single-threaded queries are actually a feature &mdash; predictable performance, no resource contention surprises across concurrent users.</p>
'''

ANSWERS[98] = r'''
<p><strong>Session management</strong> tracks logged-in users across HTTP requests. The classic approach is server-side sessions stored in a database; modern variants include Redis-backed sessions, signed cookies (JWT), and database-issued tokens. Each has trade-offs.</p>

<p><strong>Schema for database-backed sessions</strong>:</p>

<pre><code>CREATE TABLE sessions (
  id            CHAR(64) PRIMARY KEY,            -- random token (hex of 32 bytes)
  user_id       INT NOT NULL,
  created_at    DATETIME(3) NOT NULL,
  last_activity DATETIME(3) NOT NULL,
  expires_at    DATETIME(3) NOT NULL,
  ip_address    VARCHAR(45),                     -- IPv4 or IPv6
  user_agent    VARCHAR(500),
  data          JSON,                            -- arbitrary session state

  INDEX idx_user (user_id, last_activity),
  INDEX idx_expires (expires_at),
  CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;</code></pre>

<p><strong>Lifecycle operations</strong>:</p>

<pre><code>-- Create on login
INSERT INTO sessions (id, user_id, created_at, last_activity, expires_at, ip_address, user_agent)
VALUES (?, ?, NOW(3), NOW(3), NOW(3) + INTERVAL 30 DAY, ?, ?);

-- Validate on each request
SELECT user_id, expires_at FROM sessions
WHERE id = ? AND expires_at &gt; NOW(3);

-- Touch (extend) on activity
UPDATE sessions
SET last_activity = NOW(3),
    expires_at    = GREATEST(expires_at, NOW(3) + INTERVAL 30 MINUTE)
WHERE id = ?;

-- Logout
DELETE FROM sessions WHERE id = ?;

-- Logout all sessions (e.g., password reset)
DELETE FROM sessions WHERE user_id = ?;

-- Periodic cleanup
DELETE FROM sessions WHERE expires_at &lt; NOW();</code></pre>

<p><strong>Security best practices</strong>:</p>

<table>
  <tr><th>Practice</th><th>Detail</th></tr>
  <tr><td>Random session ID</td><td>32 bytes from <code>crypto.randomBytes</code> &mdash; impossible to guess</td></tr>
  <tr><td>HTTPS only</td><td>Cookie <code>Secure; HttpOnly; SameSite=Strict</code></td></tr>
  <tr><td>Rotate on auth changes</td><td>Issue new session ID after login, password change, role change</td></tr>
  <tr><td>Bind to context</td><td>Verify IP/user-agent if security-sensitive (with care &mdash; users move)</td></tr>
  <tr><td>Track active sessions</td><td>Let users see and revoke their sessions per device</td></tr>
  <tr><td>Idle timeout + absolute timeout</td><td>30 min idle, 30 day max</td></tr>
</table>

<p><strong>Why MySQL for sessions has trade-offs</strong>:</p>

<ul>
  <li><strong>Hot table</strong> &mdash; every request reads/writes it; the buffer pool fills with session pages.</li>
  <li><strong>Write amplification</strong> &mdash; each request UPDATEs <code>last_activity</code>; replicates to all replicas.</li>
  <li><strong>Cleanup overhead</strong> &mdash; periodic DELETEs of expired sessions are surprisingly heavy.</li>
</ul>

<p><strong>Redis is the standard alternative</strong>:</p>

<pre><code>// Redis: simple, fast, expires automatically
await redis.setex(`session:${sessionId}`, 3600, JSON.stringify({
  userId: 42,
  roles: ['admin'],
  csrfToken: '...'
}));
// Retrieval: O(1) memory access
// Expiry: built-in TTL; no cleanup job</code></pre>

<table>
  <tr><th>Criterion</th><th>MySQL</th><th>Redis</th></tr>
  <tr><td>Latency per check</td><td>1-10 ms</td><td>0.1-1 ms</td></tr>
  <tr><td>Throughput</td><td>Tens of thousands of req/sec</td><td>Hundreds of thousands+</td></tr>
  <tr><td>Expiry</td><td>Manual purge job</td><td>Native TTL</td></tr>
  <tr><td>Persistence</td><td>Durable; survives crash</td><td>RDB/AOF; some loss possible on restart</td></tr>
  <tr><td>Complexity</td><td>Already there</td><td>Extra component to operate</td></tr>
</table>

<p><strong>JWT alternative</strong> &mdash; stateless tokens:</p>

<pre><code>// Signed token contains user info; no server-side state
const token = jwt.sign({ userId: 42, roles: ['admin'] }, secret, { expiresIn: '1h' });

// Verify on each request &mdash; no DB hit
const payload = jwt.verify(token, secret);</code></pre>

<p>Trade-offs: can&rsquo;t easily revoke a single token without a denylist (which brings the database back); rotation requires careful key management; tokens get larger as you stuff more claims.</p>

<p><strong>Pragmatic guidance</strong>: for most web apps, Redis-backed sessions are the right choice &mdash; fast, automatic expiry, no DB hot table. Database sessions for low-traffic apps or strong-audit requirements; JWTs for stateless API tokens with a short TTL plus a refresh-token database for revocation.</p>
'''

ANSWERS[99] = r'''
<p><strong>Disk space</strong> is the boring metric that takes systems down hardest &mdash; MySQL halts when InnoDB can&rsquo;t write the redo log, replicas fall over when binlogs accumulate, backups fail mid-flight. Monitoring and forecast capacity are operational fundamentals.</p>

<p><strong>What consumes disk in MySQL</strong>:</p>

<table>
  <tr><th>Consumer</th><th>Detail</th></tr>
  <tr><td>InnoDB tablespaces</td><td>Data + indexes; the bulk of typical usage</td></tr>
  <tr><td>InnoDB redo log</td><td><code>innodb_log_file_size × innodb_log_files_in_group</code> &mdash; usually fixed</td></tr>
  <tr><td>Undo tablespaces</td><td>Grows with long transactions; can balloon if a single tx stays open</td></tr>
  <tr><td>Binary logs</td><td>Written for every change; <code>binlog_expire_logs_seconds</code> controls retention</td></tr>
  <tr><td>Relay logs (replicas)</td><td>Replicated events being applied; usually small</td></tr>
  <tr><td>Slow / general / error logs</td><td>Can grow large with verbose logging</td></tr>
  <tr><td>Temp files</td><td>Sort/spill files; hit-and-miss</td></tr>
</table>

<p><strong>Inspect from MySQL</strong>:</p>

<pre><code>-- Database sizes
SELECT
  table_schema,
  ROUND(SUM(data_length + index_length) / 1024 / 1024 / 1024, 2) AS size_gb
FROM information_schema.TABLES
GROUP BY table_schema
ORDER BY size_gb DESC;

-- Top 20 tables
SELECT
  table_schema, table_name,
  table_rows,
  ROUND(data_length / 1024 / 1024, 2)  AS data_mb,
  ROUND(index_length / 1024 / 1024, 2) AS index_mb,
  ROUND((data_length + index_length) / 1024 / 1024, 2) AS total_mb
FROM information_schema.TABLES
WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
ORDER BY data_length + index_length DESC
LIMIT 20;

-- Free space inside tablespaces (fragmentation)
SELECT
  table_schema, table_name,
  ROUND(data_free / 1024 / 1024, 2) AS free_mb,
  ROUND(data_free / NULLIF(data_length, 0) * 100, 1) AS free_pct
FROM information_schema.TABLES
WHERE data_free &gt; 100 * 1024 * 1024
ORDER BY data_free DESC;

-- Binary logs
SHOW BINARY LOGS;</code></pre>

<p><strong>Inspect from the OS</strong>:</p>

<pre><code>df -h /var/lib/mysql
du -sh /var/lib/mysql/*.ibd | sort -h | tail -20
du -sh /var/lib/mysql/binlog* | tail
du -sh /var/lib/mysql/undo*</code></pre>

<p><strong>Reclaiming space</strong>:</p>

<table>
  <tr><th>Action</th><th>Detail</th></tr>
  <tr><td><code>OPTIMIZE TABLE</code></td><td>Rebuilds the table; reclaims free space from deletes/updates. <code>ALGORITHM=INPLACE</code> 8.0+ avoids long locks.</td></tr>
  <tr><td>Drop unused indexes</td><td>Each secondary index is data; <code>sys.schema_unused_indexes</code> lists candidates</td></tr>
  <tr><td>Drop unused columns</td><td><code>ALTER TABLE ... DROP COLUMN, ALGORITHM=INSTANT</code> in 8.0</td></tr>
  <tr><td>Partition + drop</td><td>Drop old partitions instantly; better than DELETE for retention</td></tr>
  <tr><td>Shorten binlog retention</td><td><code>SET GLOBAL binlog_expire_logs_seconds = 604800</code> (7 days)</td></tr>
  <tr><td>Tune undo retention</td><td>Auto-truncate enabled by default; set <code>innodb_max_undo_log_size</code></td></tr>
  <tr><td>Move logs</td><td>Slow / general logs to a separate disk; rotate aggressively</td></tr>
</table>

<p><strong>Alerting</strong>:</p>

<ul>
  <li><strong>Warning at 80%</strong> &mdash; investigate; plan to add capacity.</li>
  <li><strong>Page at 90%</strong> &mdash; act today; days from outage.</li>
  <li><strong>Page hard at 95%</strong> &mdash; emergency; provision more capacity now.</li>
</ul>

<p>Forecast capacity by trending growth: if the database grows 10 GB/week, a 100 GB free buffer is 10 weeks. Plan capacity with that runway.</p>

<p><strong>Cloud reality</strong>: managed services usually auto-scale storage (Aurora grows automatically; RDS has GP3 expansion). Self-hosted requires explicit volume expansion &mdash; possible without downtime on most modern Linux setups (LVM, EBS resize), but procedure should be tested before you need it under pressure.</p>

<p><strong>Tooling</strong>: <strong>Prometheus + node_exporter + mysqld_exporter</strong>, <strong>PMM</strong>, <strong>Datadog</strong> all expose disk metrics out of the box. The key is having an alert before you run out, not just a dashboard you check sometimes.</p>
'''

ANSWERS[100] = r'''
<p><strong>The sys schema</strong> is a set of pre-built views, functions, and procedures over <code>performance_schema</code> &mdash; turning raw instrumentation tables into human-readable diagnostic queries. Bundled with MySQL since 5.7; the standard go-to for self-service tuning and diagnostics.</p>

<p>The raw <code>performance_schema</code> tables have terse column names and need timer-unit math; <code>sys</code> wraps them in views with friendly names, computed columns, and ordered defaults.</p>

<table>
  <tr><th>View / procedure</th><th>What it shows</th></tr>
  <tr><td><code>sys.schema_unused_indexes</code></td><td>Indexes never used since server start &mdash; safe to drop</td></tr>
  <tr><td><code>sys.statement_analysis</code></td><td>Top queries by total time, with examples and statistics</td></tr>
  <tr><td><code>sys.io_global_by_file_by_bytes</code></td><td>Files with the most I/O bytes</td></tr>
  <tr><td><code>sys.io_global_by_wait_by_latency</code></td><td>I/O operations sorted by total wait time</td></tr>
  <tr><td><code>sys.x$schema_table_lock_waits</code></td><td>Lock-wait events by table</td></tr>
  <tr><td><code>sys.host_summary</code></td><td>Per-client-host activity summary</td></tr>
  <tr><td><code>sys.user_summary</code></td><td>Per-user activity summary</td></tr>
  <tr><td><code>sys.processlist</code></td><td>Better than <code>SHOW PROCESSLIST</code>: includes wait info, blockers</td></tr>
  <tr><td><code>sys.innodb_lock_waits</code></td><td>Currently-blocked transactions and what blocks them</td></tr>
  <tr><td><code>sys.session_ssl_status</code></td><td>SSL/TLS state per session</td></tr>
  <tr><td><code>sys.metrics</code></td><td>Hundreds of named metrics, one row each</td></tr>
</table>

<p><strong>Top-10 slow queries &mdash; one query, no math</strong>:</p>

<pre><code>SELECT
  query              AS query_pattern,
  exec_count,
  total_latency,
  avg_latency,
  rows_examined_avg,
  rows_sent_avg
FROM sys.statement_analysis
ORDER BY total_latency DESC
LIMIT 10;</code></pre>

<p><strong>Find unused indexes</strong>:</p>

<pre><code>SELECT * FROM sys.schema_unused_indexes
WHERE object_schema = 'company';
-- Each index returned has had zero reads since server start
-- Confirm by waiting through a typical traffic cycle (week) before dropping</code></pre>

<p><strong>Currently-blocking lock waits</strong>:</p>

<pre><code>SELECT
  waiting_pid, waiting_query,
  blocking_pid, blocking_query,
  wait_age
FROM sys.innodb_lock_waits;
-- Identify which session is blocking which; KILL the blocker if needed</code></pre>

<p><strong>I/O hotspots</strong>:</p>

<pre><code>SELECT * FROM sys.io_global_by_file_by_bytes LIMIT 15;
-- Files generating the most read/write traffic
-- Useful for &quot;is the binlog dominating writes?&quot; or &quot;which table&rsquo;s data is hot?&quot;</code></pre>

<p><strong>Per-user resource consumption</strong>:</p>

<pre><code>SELECT * FROM sys.user_summary;
-- Statements, latency, errors, connections by user
-- Quickly identifies the &quot;heavy user&quot; or rogue script</code></pre>

<p><strong>Useful procedures</strong>:</p>

<pre><code>-- Activate / deactivate a consumer for instrumentation
CALL sys.ps_setup_enable_consumer('events_statements_history_long');
CALL sys.ps_setup_disable_consumer('statements_digest');

-- Reset all stats (for clean baselines)
CALL sys.ps_truncate_all_tables(FALSE);

-- Show current configuration
CALL sys.ps_setup_show_enabled(TRUE, TRUE);</code></pre>

<p><strong>What sys schema doesn&rsquo;t replace</strong>:</p>

<ul>
  <li><strong>Continuous monitoring</strong> &mdash; sys is point-in-time; tools like <strong>PMM</strong>, <strong>Datadog</strong>, <strong>Prometheus</strong> capture trends.</li>
  <li><strong>Slow-query log</strong> &mdash; sys tracks since restart; the slow log is durable.</li>
  <li><strong>Application-level traces</strong> &mdash; OpenTelemetry / Sentry show which user request caused the slow query.</li>
</ul>

<p><strong>Operational discipline</strong>:</p>

<ul>
  <li>Keep <code>sys</code> queries handy in a runbook; on-call should reach for them first when "MySQL is slow".</li>
  <li>Snapshot relevant <code>sys</code> views into a metrics database periodically; sys data resets on restart.</li>
  <li>Use <code>sys.statement_analysis</code> as a weekly review &mdash; the top 10-20 queries by total time deserve scrutiny.</li>
  <li><code>sys.schema_unused_indexes</code> review every quarter; dropping unused indexes typically reclaims significant write throughput and disk.</li>
</ul>

<p><strong>For external tooling</strong>: <strong>Percona PMM</strong> queries the same underlying performance_schema tables and presents them as time-series dashboards. <strong>Datadog DBM</strong>, <strong>SolarWinds DPA</strong>, and <strong>Prometheus + mysqld_exporter</strong> do similarly. <code>sys</code> is the in-MySQL self-service layer; production deployments wrap it in continuous monitoring infrastructure.</p>
'''
