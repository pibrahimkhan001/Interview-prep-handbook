"""Detailed answers for MySQL Coding interview questions.

Each ANSWERS[n] is an HTML string suitable for embedding inside a chapter page.
Style: brief lead-in (1-2 sentences), runnable SQL snippet, brief notes.
"""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<pre><code>CREATE DATABASE company;

-- With explicit charset (recommended for new databases)
CREATE DATABASE company
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

-- Idempotent variant — safe to run twice
CREATE DATABASE IF NOT EXISTS company
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;</code></pre>

<p>The bare <code>CREATE DATABASE company</code> works, but always specify the charset and collation in production. The default may differ across MySQL versions and OS installations &mdash; explicit settings prevent surprises with non-ASCII characters (emoji require <code>utf8mb4</code>; older <code>utf8</code> only stores 3-byte characters and silently truncates).</p>

<p><strong>Notes</strong>:</p>
<ul>
  <li><code>SCHEMA</code> is a synonym for <code>DATABASE</code> in MySQL &mdash; <code>CREATE SCHEMA company</code> is identical.</li>
  <li>The <code>IF NOT EXISTS</code> clause is essential for migration scripts that may run multiple times.</li>
  <li><code>utf8mb4_0900_ai_ci</code> is the modern collation: case-insensitive, accent-insensitive, supports the full Unicode 9.0 spec.</li>
  <li>To switch to the new database after creating: <code>USE company;</code></li>
  <li>Requires <code>CREATE</code> privilege globally.</li>
</ul>
'''

ANSWERS[2] = r'''
<pre><code>USE company;

CREATE TABLE employees (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  age        INT,
  department VARCHAR(50),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_department (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;</code></pre>

<p>The minimum viable answer is just the four columns the question names. The version above adds a few production touches that are standard practice: a surrogate <code>id</code> primary key with auto-increment, <code>NOT NULL</code> on <code>name</code> (a required field), an automatic <code>created_at</code> timestamp, and an index on <code>department</code> (commonly filtered).</p>

<p><strong>Type choices</strong>:</p>
<ul>
  <li><code>INT AUTO_INCREMENT PRIMARY KEY</code> &mdash; standard surrogate key. For very large tables (more than ~2 billion rows) use <code>BIGINT</code>.</li>
  <li><code>VARCHAR(100)</code> for <code>name</code> &mdash; variable-length, only consumes what&rsquo;s used.</li>
  <li><code>INT</code> for <code>age</code> &mdash; nullable here, since age might be unknown. <code>TINYINT UNSIGNED</code> (0&ndash;255) would be tighter.</li>
  <li><code>VARCHAR(50)</code> for <code>department</code> &mdash; fine here, but a normalized schema would put departments in their own table and reference by FK (see Q29).</li>
  <li><code>ENGINE=InnoDB</code> &mdash; the default in modern MySQL, but worth being explicit.</li>
  <li><code>CHARSET=utf8mb4</code> &mdash; supports emoji and the full Unicode range.</li>
</ul>

<p>The <code>USE company;</code> first line ensures the table is created in the right database; alternatively, qualify the table name as <code>company.employees</code>.</p>
'''

ANSWERS[3] = r'''
<pre><code>INSERT INTO employees (name, age, department)
VALUES ('Alice Johnson', 28, 'Engineering');</code></pre>

<p>The <code>id</code> column is omitted because it&rsquo;s <code>AUTO_INCREMENT</code> &mdash; MySQL assigns the next value automatically. <code>created_at</code> is omitted because it has a <code>DEFAULT CURRENT_TIMESTAMP</code>.</p>

<p><strong>Useful variants</strong>:</p>

<pre><code>-- Bulk insert (faster than 5 separate statements)
INSERT INTO employees (name, age, department) VALUES
  ('Bob Lee',     35, 'HR'),
  ('Carol Park',  42, 'Engineering'),
  ('Dave Smith',  29, 'Sales'),
  ('Eve Brown',   31, 'Engineering'),
  ('Frank Iyer',  45, 'HR');

-- Insert and skip duplicates (where a UNIQUE key would conflict)
INSERT IGNORE INTO employees (name, age, department)
VALUES ('Alice Johnson', 28, 'Engineering');

-- Insert or update if the primary/unique key already exists
INSERT INTO employees (id, name, age, department)
VALUES (1, 'Alice Johnson', 29, 'Engineering')
ON DUPLICATE KEY UPDATE age = VALUES(age);

-- Insert from another table
INSERT INTO archived_employees (name, age, department)
SELECT name, age, department FROM employees WHERE created_at &lt; '2023-01-01';</code></pre>

<p><strong>From application code</strong>: always use parameterized queries to prevent SQL injection &mdash; never concatenate user-supplied values into the SQL string.</p>

<pre><code>// Node.js with mysql2/promise
await conn.execute(
  'INSERT INTO employees (name, age, department) VALUES (?, ?, ?)',
  [name, age, department]
);</code></pre>
'''

ANSWERS[4] = r'''
<pre><code>UPDATE employees
SET age = 29
WHERE id = 5;</code></pre>

<p>The <code>WHERE</code> clause is critical &mdash; without it, every row in the table gets its <code>age</code> set to 29. MySQL by default refuses such mass-updates only when running with <code>safe-updates</code> mode enabled in the client; otherwise it executes silently. Always test the WHERE first with <code>SELECT</code>:</p>

<pre><code>-- Step 1: see which rows would be affected
SELECT id, name, age FROM employees WHERE id = 5;

-- Step 2: do the update
UPDATE employees SET age = 29 WHERE id = 5;</code></pre>

<p><strong>Update multiple columns at once</strong>:</p>

<pre><code>UPDATE employees
SET age = 29,
    department = 'Engineering',
    updated_at = NOW()
WHERE id = 5;</code></pre>

<p><strong>Update based on a join</strong> (sync from another table):</p>

<pre><code>UPDATE employees e
JOIN salary_changes s ON s.employee_id = e.id
SET e.salary = s.new_salary
WHERE s.effective_date = CURDATE();</code></pre>

<p><strong>Limit the affected rows</strong> &mdash; useful as a safety net during one-off fixes:</p>

<pre><code>UPDATE employees SET age = 29 WHERE id = 5 LIMIT 1;</code></pre>

<p>Always wrap risky updates in a transaction so you can roll back if something goes wrong:</p>

<pre><code>START TRANSACTION;
UPDATE employees SET age = 29 WHERE id = 5;
-- check the result, then:
COMMIT;       -- or ROLLBACK; if the change is wrong</code></pre>

<p>From application code: parameterize every value &mdash; <code>UPDATE employees SET age = ? WHERE id = ?</code>.</p>
'''

ANSWERS[5] = r'''
<pre><code>DELETE FROM employees
WHERE id = 5;</code></pre>

<p>Like <code>UPDATE</code>, omitting the <code>WHERE</code> deletes <em>every</em> row. There&rsquo;s no built-in undo &mdash; once committed, the data is gone. Always preview first:</p>

<pre><code>SELECT * FROM employees WHERE id = 5;
DELETE FROM employees WHERE id = 5;</code></pre>

<p><strong>Soft delete</strong> &mdash; in many applications, you don&rsquo;t actually delete; you mark the row as deleted. This preserves audit history and supports undo:</p>

<pre><code>UPDATE employees
SET deleted_at = NOW()
WHERE id = 5;

-- Application queries then exclude soft-deleted rows:
SELECT * FROM employees WHERE deleted_at IS NULL;</code></pre>

<p><strong>Foreign key cascades</strong>: if other tables reference <code>employees</code> via foreign keys, the constraint may block or cascade. Configure with <code>ON DELETE</code> when defining the FK:</p>

<pre><code>FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL,
FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE</code></pre>

<p><code>SET NULL</code> sets the referencing column to NULL; <code>CASCADE</code> deletes the dependent rows; the default <code>RESTRICT</code> blocks the delete entirely.</p>

<p><strong>Use a transaction for safety</strong>:</p>

<pre><code>START TRANSACTION;
DELETE FROM employees WHERE id = 5;
-- run sanity-check SELECTs
COMMIT;       -- or ROLLBACK</code></pre>

<p><strong>To delete the entire table&rsquo;s data quickly</strong> (without dropping the table), use <code>TRUNCATE</code> &mdash; it&rsquo;s faster than <code>DELETE</code> on a large table because it doesn&rsquo;t log each row, but it can&rsquo;t use <code>WHERE</code>: <code>TRUNCATE TABLE employees;</code>.</p>
'''

ANSWERS[6] = r'''
<pre><code>SELECT * FROM employees;</code></pre>

<p>This returns every row and every column. Fine for ad-hoc inspection, but in production code <strong>list the columns you actually need</strong> &mdash; smaller transfer, more readable, and resilient to schema changes:</p>

<pre><code>SELECT id, name, age, department, created_at
FROM employees;</code></pre>

<p><strong>With ordering</strong> &mdash; without <code>ORDER BY</code>, the row order is unspecified:</p>

<pre><code>SELECT id, name, age, department FROM employees
ORDER BY name ASC;</code></pre>

<p><strong>With pagination</strong> &mdash; for tables with many rows, fetch one page at a time:</p>

<pre><code>SELECT id, name FROM employees
ORDER BY id
LIMIT 50 OFFSET 0;        -- page 1

SELECT id, name FROM employees
ORDER BY id
LIMIT 50 OFFSET 50;       -- page 2</code></pre>

<p><strong>Watch out for huge tables</strong>: <code>SELECT * FROM huge_table</code> can return millions of rows and saturate memory or the network. Always combine with <code>WHERE</code> and <code>LIMIT</code> when exploring unfamiliar data:</p>

<pre><code>-- Safer
SELECT * FROM employees WHERE created_at &gt;= '2026-01-01' LIMIT 100;</code></pre>

<p><strong>Application code</strong>: returning all columns also includes any future columns added later, which may contain sensitive data. Listing columns explicitly is safer.</p>

<pre><code>// Node.js
const [rows] = await conn.query('SELECT id, name, department FROM employees');</code></pre>

<p>For exploratory work in a SQL console, <code>SELECT *</code> is fine. For application code, name your columns.</p>
'''

ANSWERS[7] = r'''
<pre><code>SELECT id, name, age, department
FROM employees
WHERE age &gt; 30;</code></pre>

<p>The condition <code>age &gt; 30</code> excludes employees aged exactly 30. Use <code>&gt;=</code> for inclusive:</p>

<pre><code>SELECT * FROM employees WHERE age &gt;= 30;</code></pre>

<p><strong>NULL handling</strong>: rows where <code>age IS NULL</code> are excluded by both <code>&gt; 30</code> and <code>&lt;= 30</code> &mdash; comparisons with NULL evaluate to NULL, which is treated as false in WHERE. To include unknowns:</p>

<pre><code>SELECT * FROM employees WHERE age &gt; 30 OR age IS NULL;</code></pre>

<p><strong>Combine with sorting and limiting</strong> for typical UI lists:</p>

<pre><code>SELECT id, name, age
FROM employees
WHERE age &gt; 30
ORDER BY age DESC, name ASC
LIMIT 50;</code></pre>

<p><strong>With multiple conditions</strong>:</p>

<pre><code>-- Engineering staff older than 30
SELECT * FROM employees
WHERE age &gt; 30 AND department = 'Engineering';

-- Outside the 25&ndash;35 age range
SELECT * FROM employees WHERE age &lt; 25 OR age &gt; 35;</code></pre>

<p><strong>Performance</strong>: an index on <code>age</code> helps when the filtered subset is a small fraction of the table:</p>

<pre><code>CREATE INDEX idx_employees_age ON employees(age);</code></pre>

<p>Use <code>EXPLAIN</code> to confirm the query uses it:</p>

<pre><code>EXPLAIN SELECT * FROM employees WHERE age &gt; 30;
-- Look for type=range and key=idx_employees_age in the output</code></pre>
'''

ANSWERS[8] = r'''
<pre><code>SELECT name FROM employees;</code></pre>

<p>Returns one row per employee with just the name column. Add <code>DISTINCT</code> if duplicates should collapse:</p>

<pre><code>SELECT DISTINCT name FROM employees;</code></pre>

<p>Note the <em>row</em> is unique with DISTINCT &mdash; not the values. <code>SELECT DISTINCT name, department</code> returns unique <em>pairs</em>; an employee in two departments shows twice.</p>

<p><strong>Sorted alphabetically</strong>:</p>

<pre><code>SELECT name FROM employees ORDER BY name ASC;</code></pre>

<p><strong>With NULL filtering</strong> if names might be missing:</p>

<pre><code>SELECT name FROM employees
WHERE name IS NOT NULL AND name &lt;&gt; ''
ORDER BY name;</code></pre>

<p><strong>Concatenate full names</strong> if names are split into first/last columns:</p>

<pre><code>SELECT CONCAT(first_name, ' ', last_name) AS full_name
FROM employees
ORDER BY last_name, first_name;

-- Or use CONCAT_WS to handle NULL middle names cleanly:
SELECT CONCAT_WS(' ', first_name, middle_name, last_name) AS full_name
FROM employees;</code></pre>

<p><strong>Format names for display</strong>:</p>

<pre><code>SELECT
  UPPER(LEFT(name, 1)) AS initial,
  name,
  CHAR_LENGTH(name) AS name_length
FROM employees
ORDER BY initial, name;</code></pre>

<p><strong>For very large result sets</strong>, paginate (LIMIT/OFFSET) and stream the data &mdash; don&rsquo;t fetch every name into application memory at once.</p>
'''

ANSWERS[9] = r'''
<pre><code>SELECT COUNT(*) AS total_employees FROM employees;</code></pre>

<p><code>COUNT(*)</code> counts every row, including those where every column is NULL. Other variants:</p>

<table>
  <tr><th>Form</th><th>Counts</th></tr>
  <tr><td><code>COUNT(*)</code></td><td>All rows in the table</td></tr>
  <tr><td><code>COUNT(name)</code></td><td>Rows where <code>name IS NOT NULL</code></td></tr>
  <tr><td><code>COUNT(DISTINCT department)</code></td><td>Unique non-NULL department values</td></tr>
</table>

<p><strong>With a WHERE filter</strong>:</p>

<pre><code>-- How many engineers
SELECT COUNT(*) FROM employees WHERE department = 'Engineering';

-- Active employees only
SELECT COUNT(*) FROM employees WHERE deleted_at IS NULL;</code></pre>

<p><strong>Multiple conditional counts in one query</strong> &mdash; useful for dashboards:</p>

<pre><code>SELECT
  COUNT(*) AS total,
  COUNT(CASE WHEN department = 'Engineering' THEN 1 END) AS engineering,
  COUNT(CASE WHEN department = 'HR' THEN 1 END) AS hr,
  COUNT(CASE WHEN age &gt;= 30 THEN 1 END) AS over_30
FROM employees;</code></pre>

<p><strong>Per-group counts</strong>:</p>

<pre><code>SELECT department, COUNT(*) AS staff_count
FROM employees
GROUP BY department
ORDER BY staff_count DESC;</code></pre>

<p><strong>Performance note</strong>: on large InnoDB tables, <code>COUNT(*)</code> without a <code>WHERE</code> requires scanning rows or an index &mdash; not instant on millions of rows. For approximate counts, <code>information_schema.TABLES.TABLE_ROWS</code> gives an estimate:</p>

<pre><code>SELECT TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'company' AND TABLE_NAME = 'employees';
-- Estimate only — can be off by &plusmn;10% for InnoDB</code></pre>
'''

ANSWERS[10] = r'''
<pre><code>SELECT AVG(age) AS average_age FROM employees;</code></pre>

<p><code>AVG()</code> ignores NULL values entirely &mdash; both in the sum and in the count of values being averaged. So <code>AVG(age)</code> over 5 rows where 2 ages are NULL averages over the 3 non-NULL values, not 5.</p>

<p><strong>Round for display</strong>:</p>

<pre><code>SELECT ROUND(AVG(age), 1) AS average_age FROM employees;
-- e.g., 33.7
</code></pre>

<p><strong>Treat NULL as zero</strong> if you need NULLs counted in the denominator:</p>

<pre><code>SELECT AVG(COALESCE(age, 0)) AS avg_with_zeros FROM employees;</code></pre>

<p>This is rarely the right semantic for "average age" &mdash; better to either filter out NULLs or report them separately.</p>

<p><strong>Per-group averages</strong>:</p>

<pre><code>-- Average age per department
SELECT department,
       ROUND(AVG(age), 1) AS avg_age,
       COUNT(*) AS staff_count
FROM employees
GROUP BY department
ORDER BY avg_age DESC;</code></pre>

<p><strong>Filter on the aggregate</strong> using <code>HAVING</code>:</p>

<pre><code>-- Departments where the average age is over 35
SELECT department, AVG(age) AS avg_age
FROM employees
GROUP BY department
HAVING AVG(age) &gt; 35;</code></pre>

<p><strong>Combined statistics in one query</strong>:</p>

<pre><code>SELECT
  COUNT(*) AS total,
  ROUND(AVG(age), 1) AS avg_age,
  MIN(age) AS youngest,
  MAX(age) AS oldest,
  ROUND(STDDEV(age), 1) AS std_dev
FROM employees;</code></pre>

<p>For <strong>median</strong>, MySQL has no built-in function &mdash; use window functions (<code>PERCENT_RANK</code>, <code>ROW_NUMBER</code>) or compute application-side.</p>
'''

ANSWERS[11] = r'''
<pre><code>SELECT name, age
FROM employees
WHERE age IS NOT NULL
ORDER BY age ASC
LIMIT 1;</code></pre>

<p>Sorting ascending and limiting to 1 returns the youngest. The <code>WHERE age IS NOT NULL</code> guards against the edge case where some rows have unknown age &mdash; without it, the result might be a NULL-age row depending on collation.</p>

<p><strong>Alternative with subquery</strong> &mdash; returns ALL employees tied for youngest, not just one:</p>

<pre><code>SELECT name, age FROM employees
WHERE age = (SELECT MIN(age) FROM employees);</code></pre>

<p>If two employees are 22 (the minimum), this returns both rows; the <code>ORDER BY ... LIMIT 1</code> form returns just one (deterministic only if you add a tiebreaker like <code>ORDER BY age ASC, id ASC</code>).</p>

<p><strong>Per-department youngest</strong> &mdash; a common variant. With window functions (MySQL 8+):</p>

<pre><code>SELECT department, name, age
FROM (
  SELECT department, name, age,
         ROW_NUMBER() OVER (PARTITION BY department ORDER BY age ASC, id ASC) AS rn
  FROM employees
  WHERE age IS NOT NULL
) ranked
WHERE rn = 1;</code></pre>

<p><strong>Or with a correlated subquery</strong> &mdash; works on older MySQL too:</p>

<pre><code>SELECT department, name, age
FROM employees e
WHERE age = (
  SELECT MIN(age) FROM employees
  WHERE department = e.department
);</code></pre>

<p>For <code>NULL</code> handling: <code>MIN()</code> ignores NULL values, so the subquery returns the minimum non-NULL age. Both employees explicitly with NULL ages are simply excluded from the result.</p>
'''

ANSWERS[12] = r'''
<pre><code>SELECT name, age
FROM employees
WHERE age IS NOT NULL
ORDER BY age DESC
LIMIT 1;</code></pre>

<p>Mirror of the youngest query &mdash; sort descending and limit to 1. The same caveats apply: tiebreaker if multiple employees share the maximum age, and explicit <code>IS NOT NULL</code> filter so unknowns don&rsquo;t sneak in (depending on collation, NULLs sort first in ascending order and last in descending; behavior is consistent but the explicit filter is clearer intent).</p>

<p><strong>To get all employees tied for oldest</strong>:</p>

<pre><code>SELECT name, age FROM employees
WHERE age = (SELECT MAX(age) FROM employees);</code></pre>

<p><strong>Top N oldest</strong> &mdash; just bump the LIMIT:</p>

<pre><code>SELECT name, age FROM employees
WHERE age IS NOT NULL
ORDER BY age DESC, id ASC
LIMIT 5;</code></pre>

<p>The secondary sort by <code>id ASC</code> makes ties deterministic &mdash; without it, two employees with the same age might appear in different orders on different runs.</p>

<p><strong>Oldest per department</strong> &mdash; window function approach (MySQL 8+):</p>

<pre><code>SELECT department, name, age
FROM (
  SELECT department, name, age,
         RANK() OVER (PARTITION BY department ORDER BY age DESC) AS rk
  FROM employees
  WHERE age IS NOT NULL
) ranked
WHERE rk = 1;</code></pre>

<p>Using <code>RANK()</code> instead of <code>ROW_NUMBER()</code> includes ties &mdash; if two employees are both the oldest in HR, both are returned with rank 1.</p>

<p><strong>Performance</strong>: an index on <code>age</code> makes both <code>MAX(age)</code> and the <code>ORDER BY age DESC LIMIT 1</code> form essentially instant &mdash; MySQL reads the last entry of the index without scanning rows.</p>
'''

ANSWERS[13] = r'''
<pre><code>SELECT id, name, age
FROM employees
WHERE name LIKE 'J%';</code></pre>

<p>The <code>%</code> is the wildcard for "zero or more characters". <code>'J%'</code> matches any name starting with J: <code>James</code>, <code>Janet</code>, <code>J.</code>, even just <code>J</code>.</p>

<p><strong>Case sensitivity</strong> depends on the column&rsquo;s collation. The default <code>utf8mb4_0900_ai_ci</code> is case-insensitive, so <code>'J%'</code> matches both <code>James</code> and <code>jane</code>. For case-sensitive matching, force a binary collation:</p>

<pre><code>SELECT name FROM employees
WHERE name LIKE 'J%' COLLATE utf8mb4_bin;
-- Matches 'James' but not 'jane'</code></pre>

<p><strong>Other LIKE patterns</strong>:</p>

<pre><code>-- Names ending with 'son'
SELECT name FROM employees WHERE name LIKE '%son';

-- Names containing 'an' anywhere
SELECT name FROM employees WHERE name LIKE '%an%';

-- 5-letter names starting with J (_ matches one character)
SELECT name FROM employees WHERE name LIKE 'J____';

-- Starts with J or K
SELECT name FROM employees
WHERE name LIKE 'J%' OR name LIKE 'K%';

-- Or use REGEXP for more power:
SELECT name FROM employees WHERE name REGEXP '^[JK]';</code></pre>

<p><strong>Performance</strong>: <code>LIKE 'J%'</code> (anchored at the start) can use a B-tree index on <code>name</code>:</p>

<pre><code>CREATE INDEX idx_employees_name ON employees(name);</code></pre>

<p>This makes the lookup fast even on millions of rows. By contrast, <code>LIKE '%j%'</code> or <code>LIKE '%n'</code> cannot use a normal index &mdash; MySQL must scan every row. For substring-anywhere search on large tables, use a <code>FULLTEXT</code> index or a dedicated search engine (Elasticsearch, Meilisearch, Typesense).</p>
'''

ANSWERS[14] = r'''
<pre><code>SELECT id, name, age, department
FROM employees
ORDER BY age DESC;</code></pre>

<p>Default sort direction is ascending; <code>DESC</code> reverses it &mdash; oldest first.</p>

<p><strong>Stable ordering with a tiebreaker</strong> &mdash; without one, two employees of the same age may appear in different orders on different runs:</p>

<pre><code>SELECT id, name, age, department
FROM employees
ORDER BY age DESC, id ASC;</code></pre>

<p><strong>NULL handling</strong>: in MySQL, <code>NULL</code> sorts first in ascending order and last in descending. To control NULL placement explicitly:</p>

<pre><code>-- NULLs first (default with DESC)
SELECT * FROM employees ORDER BY age DESC;

-- Force NULLs last in DESC
SELECT * FROM employees
ORDER BY age IS NULL ASC, age DESC;
-- IS NULL evaluates to 0/1; non-NULLs (0) sort first.</code></pre>

<p><strong>With pagination</strong> for large result sets:</p>

<pre><code>SELECT id, name, age FROM employees
ORDER BY age DESC, id ASC
LIMIT 50 OFFSET 100;
-- Page 3 if pages are 50 rows each</code></pre>

<p><strong>Performance</strong>: an index on <code>age</code> can let MySQL skip the sort entirely &mdash; the index already stores values in order:</p>

<pre><code>CREATE INDEX idx_employees_age ON employees(age);

EXPLAIN SELECT * FROM employees ORDER BY age DESC;
-- If 'Using filesort' appears, no index is being used.
-- If 'Using index' appears, the sort is free.</code></pre>

<p>For large tables, a manual sort (<em>filesort</em>) of millions of rows is expensive. Always pair <code>ORDER BY</code> with <code>LIMIT</code> for paginated UI &mdash; otherwise you transmit and sort everything just to discard most of it.</p>
'''

ANSWERS[15] = r'''
<pre><code>SELECT id, name, age, department
FROM employees
WHERE department = 'HR';</code></pre>

<p>Equality match on a string column. Case sensitivity again depends on collation &mdash; default <code>utf8mb4_0900_ai_ci</code> matches <code>'HR'</code>, <code>'hr'</code>, and <code>'Hr'</code> all equally. To force exact match:</p>

<pre><code>SELECT * FROM employees
WHERE department = 'HR' COLLATE utf8mb4_bin;
-- Now 'hr' would not match.</code></pre>

<p><strong>With trimming</strong> &mdash; if data ingestion left leading/trailing spaces in some rows:</p>

<pre><code>SELECT * FROM employees WHERE TRIM(department) = 'HR';</code></pre>

<p>(But applying a function to the column prevents index use &mdash; better to clean the data once: <code>UPDATE employees SET department = TRIM(department);</code>.)</p>

<p><strong>Multiple departments</strong> &mdash; use <code>IN</code> instead of chained <code>OR</code>s:</p>

<pre><code>SELECT * FROM employees
WHERE department IN ('HR', 'Sales', 'Marketing');</code></pre>

<p><strong>Combined with other filters and sorting</strong>:</p>

<pre><code>SELECT id, name, age FROM employees
WHERE department = 'HR'
  AND age &gt;= 30
ORDER BY age DESC;</code></pre>

<p><strong>Performance</strong>: a B-tree index on <code>department</code> makes the lookup fast &mdash; especially when HR is a small fraction of the table:</p>

<pre><code>CREATE INDEX idx_employees_department ON employees(department);</code></pre>

<p><strong>Better schema</strong>: storing <code>department</code> as a string repeats the value on every row. A normalized schema with a <code>departments</code> table and <code>department_id</code> foreign key is smaller, faster to update (rename a department in one place), and prevents typos. See Q29 for the join.</p>
'''

ANSWERS[16] = r'''
<pre><code>SELECT id, name, age
FROM employees
WHERE age BETWEEN 25 AND 35;</code></pre>

<p><code>BETWEEN</code> is <strong>inclusive on both ends</strong> &mdash; ages 25 and 35 are both included. Equivalent to:</p>

<pre><code>SELECT id, name, age FROM employees
WHERE age &gt;= 25 AND age &lt;= 35;</code></pre>

<p><strong>NOT BETWEEN</strong> for the opposite range:</p>

<pre><code>SELECT * FROM employees WHERE age NOT BETWEEN 25 AND 35;
-- Equivalent to: WHERE age &lt; 25 OR age &gt; 35</code></pre>

<p><strong>Watch the order</strong>: <code>BETWEEN 35 AND 25</code> (high then low) returns no rows &mdash; MySQL doesn&rsquo;t auto-swap. The first value must be the lower bound.</p>

<p><strong>Works on dates and strings too</strong>:</p>

<pre><code>-- Hires in Q1 2026
SELECT * FROM employees
WHERE hire_date BETWEEN '2026-01-01' AND '2026-03-31';

-- Names starting from L through R
SELECT * FROM employees
WHERE name BETWEEN 'L' AND 'R';</code></pre>

<p><strong>Date BETWEEN gotcha</strong>: <code>BETWEEN '2026-01-01' AND '2026-03-31'</code> on a <code>DATETIME</code> column excludes anything after midnight on March 31. Use an explicit half-open range:</p>

<pre><code>SELECT * FROM events
WHERE created_at &gt;= '2026-01-01'
  AND created_at &lt; '2026-04-01';
-- Includes all of March 31, regardless of time portion</code></pre>

<p><strong>NULL handling</strong>: rows where <code>age IS NULL</code> are excluded by both <code>BETWEEN</code> and <code>NOT BETWEEN</code> &mdash; comparisons with NULL return NULL, which doesn&rsquo;t match in WHERE. To include unknowns: <code>... OR age IS NULL</code>.</p>

<p><strong>Performance</strong>: a B-tree index on <code>age</code> supports range queries efficiently &mdash; the index stores values in sorted order so MySQL reads only the matching range.</p>
'''

ANSWERS[17] = r'''
<pre><code>SELECT id, name, age
FROM employees
WHERE name LIKE '%an%';</code></pre>

<p>The <code>%an%</code> pattern matches any string with <code>an</code> anywhere &mdash; <code>Anna</code>, <code>Brian</code>, <code>Stefan</code>, <code>Hannah</code>. Default collation is case-insensitive, so <code>'%an%'</code> matches <code>Anna</code> too.</p>

<p><strong>Word-boundary matches with REGEXP</strong> &mdash; if you want <code>an</code> as a whole word or syllable rather than embedded:</p>

<pre><code>-- Names where 'an' appears as a syllable boundary
SELECT name FROM employees
WHERE name REGEXP '\\ban|an\\b';

-- Names matching either of two substrings
SELECT name FROM employees
WHERE name REGEXP 'an|en';</code></pre>

<p><strong>Performance pitfall</strong>: <code>LIKE '%an%'</code> can&rsquo;t use a normal B-tree index &mdash; the leading <code>%</code> means MySQL must scan every row. On a 10-million-row <code>employees</code> table this could take many seconds.</p>

<p><strong>For substring search at scale</strong>, use a <code>FULLTEXT</code> index:</p>

<pre><code>-- Add a fulltext index
ALTER TABLE employees
ADD FULLTEXT KEY ft_name (name);

-- Search using MATCH ... AGAINST
SELECT name, MATCH(name) AGAINST('Anna') AS score
FROM employees
WHERE MATCH(name) AGAINST('Anna' IN NATURAL LANGUAGE MODE);

-- Or boolean mode for prefix/required terms
SELECT name FROM employees
WHERE MATCH(name) AGAINST('+brian* -bryan' IN BOOLEAN MODE);</code></pre>

<p>Fulltext indexes use a different data structure (inverted index of words) and support relevance scoring, stemming, and stopword handling.</p>

<p><strong>Better still for production search</strong>: dedicated engines like Elasticsearch, OpenSearch, Meilisearch, or Typesense &mdash; they handle typos, synonyms, multi-language, faceted search, and high traffic that pure SQL can&rsquo;t match.</p>
'''

ANSWERS[18] = r'''
<pre><code>SELECT DISTINCT department
FROM employees
ORDER BY department;</code></pre>

<p>Returns each department name once. <code>DISTINCT</code> works on the entire selected row &mdash; with multiple columns, the unique combination is returned:</p>

<pre><code>-- Unique (department, role) pairs
SELECT DISTINCT department, role FROM employees;</code></pre>

<p><strong>Filter out NULLs and empty strings</strong> if data quality varies:</p>

<pre><code>SELECT DISTINCT department
FROM employees
WHERE department IS NOT NULL AND department &lt;&gt; ''
ORDER BY department;</code></pre>

<p><strong>Equivalent with GROUP BY</strong> &mdash; same result, different style:</p>

<pre><code>SELECT department FROM employees GROUP BY department ORDER BY department;</code></pre>

<p>Use <code>DISTINCT</code> when you just want unique values; use <code>GROUP BY</code> when combining with aggregates:</p>

<pre><code>-- Departments with their headcount
SELECT department, COUNT(*) AS staff_count
FROM employees
GROUP BY department
ORDER BY staff_count DESC;</code></pre>

<p><strong>Count distinct values</strong>:</p>

<pre><code>SELECT COUNT(DISTINCT department) AS unique_departments
FROM employees;</code></pre>

<p><strong>Performance</strong>: <code>DISTINCT</code> often requires a sort or temporary table. An index on <code>department</code> can make it fast &mdash; MySQL reads unique values directly from the index without scanning the full table:</p>

<pre><code>CREATE INDEX idx_employees_department ON employees(department);

EXPLAIN SELECT DISTINCT department FROM employees;
-- Look for type=index and Extra=Using index in the output</code></pre>

<p><strong>Better schema</strong>: if departments are first-class entities (with their own attributes like budget, location, manager), put them in a separate <code>departments</code> table. Then <code>SELECT name FROM departments</code> &mdash; no DISTINCT needed.</p>
'''

ANSWERS[19] = r'''
<pre><code>-- During table creation
CREATE TABLE employees (
  id   INT AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  ...
  PRIMARY KEY (id)
);

-- Or as part of the column definition
CREATE TABLE employees (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  ...
);

-- Add a primary key to an existing table
ALTER TABLE employees
ADD PRIMARY KEY (id);</code></pre>

<p>A table can have <strong>only one primary key</strong>. The PK column(s) are NOT NULL automatically &mdash; if not declared so, MySQL silently adds the constraint. Adding a PK creates a clustered index (in InnoDB) which determines the physical row order.</p>

<p><strong>Composite primary key</strong> &mdash; multiple columns whose <em>combination</em> is unique:</p>

<pre><code>CREATE TABLE order_items (
  order_id   INT,
  product_id INT,
  quantity   INT NOT NULL,
  PRIMARY KEY (order_id, product_id)
);</code></pre>

<p><strong>Drop and replace a primary key</strong>:</p>

<pre><code>-- Drop the existing PK first
ALTER TABLE employees DROP PRIMARY KEY;

-- Then add a new one
ALTER TABLE employees ADD PRIMARY KEY (employee_uuid);</code></pre>

<p>If foreign keys reference the column being modified, drop those constraints first.</p>

<p><strong>Auto-increment requirement</strong>: MySQL requires the auto-increment column to be (or be part of) a key. The simplest pattern is making it the PK:</p>

<pre><code>CREATE TABLE logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  message TEXT
);</code></pre>

<p><strong>Common PK choices</strong>:</p>
<ul>
  <li><code>INT AUTO_INCREMENT</code> &mdash; simple, fast, ~2 billion limit (4 bytes).</li>
  <li><code>BIGINT AUTO_INCREMENT</code> &mdash; for very large tables (8 bytes).</li>
  <li><code>BINARY(16)</code> with UUID v4 &mdash; for distributed systems where IDs must be globally unique without coordination.</li>
  <li><code>UUID v7 / ULID</code> stored as <code>BINARY(16)</code> &mdash; globally unique <em>and</em> sortable; good modern choice.</li>
</ul>
'''

ANSWERS[20] = r'''
<pre><code>ALTER TABLE employees
ADD COLUMN salary DECIMAL(12, 2);</code></pre>

<p><code>DECIMAL(12, 2)</code> stores up to 10 digits before and 2 after the decimal point &mdash; correct for money. <strong>Never store money as <code>FLOAT</code> or <code>DOUBLE</code></strong>; binary floating-point causes rounding errors that compound across additions.</p>

<p><strong>With NOT NULL and a default</strong>:</p>

<pre><code>ALTER TABLE employees
ADD COLUMN salary DECIMAL(12, 2) NOT NULL DEFAULT 0.00;</code></pre>

<p>Existing rows get the default value. Without the default, NOT NULL would fail because existing rows have no value for the new column.</p>

<p><strong>Position the column</strong> &mdash; default is to add at the end. Use <code>FIRST</code> or <code>AFTER</code>:</p>

<pre><code>ALTER TABLE employees
ADD COLUMN salary DECIMAL(12, 2) AFTER department;

ALTER TABLE employees
ADD COLUMN priority INT FIRST;</code></pre>

<p><strong>Add multiple columns in one statement</strong> &mdash; faster than separate ALTERs because the table is rebuilt only once:</p>

<pre><code>ALTER TABLE employees
  ADD COLUMN salary       DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
  ADD COLUMN bonus_target DECIMAL(12, 2),
  ADD COLUMN currency     CHAR(3) NOT NULL DEFAULT 'USD';</code></pre>

<p><strong>Performance on large tables</strong>: an <code>ALTER TABLE</code> can lock the table or rebuild it entirely. MySQL 8 supports <strong>instant ADD COLUMN</strong> for many cases &mdash; the metadata changes without touching data:</p>

<pre><code>ALTER TABLE huge_table
ADD COLUMN new_col INT,
ALGORITHM=INSTANT;</code></pre>

<p>Not all column types qualify (e.g., adding a generated stored column requires a rebuild). The MySQL docs list the supported cases.</p>

<p><strong>For production tables of significant size</strong>, use online-schema-change tools that copy the table in the background and atomically swap:</p>
<ul>
  <li><strong>pt-online-schema-change</strong> (Percona Toolkit).</li>
  <li><strong>gh-ost</strong> (GitHub&rsquo;s tool, uses binlog instead of triggers).</li>
</ul>
'''

ANSWERS[21] = r'''
<pre><code>ALTER TABLE employees
DROP COLUMN salary;</code></pre>

<p>This is destructive &mdash; the salary data is permanently deleted. There&rsquo;s no <code>UNDO</code>. Take a backup first if there&rsquo;s any chance you&rsquo;ll need the data:</p>

<pre><code>-- Quick backup of just the column data + key
CREATE TABLE _salary_backup AS
SELECT id, salary FROM employees;</code></pre>

<p><strong>Drop multiple columns</strong> in one statement &mdash; faster than separate ALTERs:</p>

<pre><code>ALTER TABLE employees
  DROP COLUMN salary,
  DROP COLUMN bonus_target,
  DROP COLUMN legacy_field;</code></pre>

<p><strong>Constraints to watch out for</strong>:</p>
<ul>
  <li><strong>Indexes on the column</strong> &mdash; dropped automatically with the column.</li>
  <li><strong>Foreign keys referencing the column</strong> &mdash; you must drop the FK constraint first, or the ALTER fails with <code>"Cannot drop column"</code>:
<pre><code>ALTER TABLE child DROP FOREIGN KEY fk_employee_salary;
ALTER TABLE employees DROP COLUMN salary;</code></pre>
  </li>
  <li><strong>Views, triggers, and stored procedures</strong> referencing the column &mdash; not dropped automatically; will break at runtime.</li>
  <li><strong>Generated columns</strong> that depend on the dropped column &mdash; must be dropped or modified first.</li>
</ul>

<p><strong>Performance on large tables</strong>: dropping a column may rebuild the entire table. Use <code>ALGORITHM=INPLACE</code> when possible:</p>

<pre><code>ALTER TABLE huge_table
DROP COLUMN unused_col,
ALGORITHM=INPLACE, LOCK=NONE;</code></pre>

<p>If MySQL refuses (<em>"this algorithm cannot be used for this operation"</em>), the change requires a full rebuild &mdash; use <code>pt-online-schema-change</code> or <code>gh-ost</code> on production tables.</p>

<p><strong>Safer pattern for production</strong>:</p>
<ol>
  <li>Stop writing to the column from application code (deploy a release that no longer references it).</li>
  <li>Verify in monitoring that no SELECT queries reference it either.</li>
  <li>Wait through one full release cycle as a buffer.</li>
  <li><em>Then</em> drop the column.</li>
</ol>

<p>If you drop first and find the column was still in use somewhere, you&rsquo;ve broken production with no quick recovery.</p>
'''

ANSWERS[22] = r'''
<pre><code>RENAME TABLE employees TO staff;

-- Equivalent ALTER syntax
ALTER TABLE employees RENAME TO staff;</code></pre>

<p>Both work; <code>RENAME TABLE</code> is preferred when renaming multiple tables atomically.</p>

<p><strong>Atomic multi-rename for zero-downtime swap</strong> &mdash; rebuild a table with cleaned data, then swap names in one operation:</p>

<pre><code>-- Setup: build staff_new with the desired changes
CREATE TABLE staff_new LIKE staff;
INSERT INTO staff_new SELECT * FROM staff WHERE deleted_at IS NULL;
-- ... apply transformations ...

-- Atomic swap — application sees no gap
RENAME TABLE
  staff TO staff_old,
  staff_new TO staff;

-- After verifying, drop the old version
DROP TABLE staff_old;</code></pre>

<p>This is the standard pattern for major schema migrations: build a new version of the table, dual-write to both during a transition window, then atomically swap.</p>

<p><strong>Move a table to another database</strong> &mdash; fully qualify the destination:</p>

<pre><code>RENAME TABLE company.legacy_employees TO archive.legacy_employees;</code></pre>

<p>Both source and destination must be on the same MySQL server.</p>

<p><strong>Caveats</strong>:</p>
<ul>
  <li><strong>Foreign keys</strong> referencing the renamed table are automatically updated.</li>
  <li><strong>Views, stored procedures, triggers</strong> that reference the old name are <em>not</em> updated &mdash; they break until you fix them.</li>
  <li><strong>Permissions</strong>: the user needs <code>ALTER</code> and <code>DROP</code> on the old table and <code>CREATE</code>/<code>INSERT</code> on the new.</li>
  <li><strong>Application code</strong> must be updated too &mdash; rename in the codebase at the same time, or use a view as a compatibility layer:
<pre><code>-- During transition, keep the old name working as a view
CREATE VIEW employees AS SELECT * FROM staff;</code></pre>
  </li>
</ul>

<p><strong>Conditional rename</strong> &mdash; <code>RENAME TABLE</code> doesn&rsquo;t support <code>IF EXISTS</code> directly; check first or use a stored procedure if you need idempotency.</p>
'''

ANSWERS[23] = r'''
<pre><code>SELECT department, COUNT(*) AS staff_count
FROM employees
GROUP BY department
ORDER BY staff_count DESC
LIMIT 1;</code></pre>

<p>Group by department, count rows per group, sort descending, take the top one. Returns one row even when multiple departments tie for the highest count.</p>

<p><strong>Get all tied winners</strong> &mdash; departments with the maximum count, including ties:</p>

<pre><code>SELECT department, staff_count
FROM (
  SELECT department, COUNT(*) AS staff_count
  FROM employees
  GROUP BY department
) counts
WHERE staff_count = (
  SELECT MAX(c) FROM (
    SELECT COUNT(*) AS c FROM employees GROUP BY department
  ) max_counts
);</code></pre>

<p>Cleaner with a CTE (MySQL 8+):</p>

<pre><code>WITH dept_counts AS (
  SELECT department, COUNT(*) AS staff_count
  FROM employees
  GROUP BY department
)
SELECT department, staff_count
FROM dept_counts
WHERE staff_count = (SELECT MAX(staff_count) FROM dept_counts);</code></pre>

<p><strong>With ranking via window functions</strong> (MySQL 8+) &mdash; flexible for "top N" variations:</p>

<pre><code>SELECT department, staff_count
FROM (
  SELECT department,
         COUNT(*) AS staff_count,
         RANK() OVER (ORDER BY COUNT(*) DESC) AS rk
  FROM employees
  GROUP BY department
) ranked
WHERE rk = 1;</code></pre>

<p><code>RANK()</code> gives the same rank to ties &mdash; if HR and Engineering both have 50 staff (the maximum), both get rank 1 and both are returned.</p>

<p><strong>Filter out NULL departments</strong> if data quality varies:</p>

<pre><code>SELECT department, COUNT(*) AS staff_count
FROM employees
WHERE department IS NOT NULL
GROUP BY department
ORDER BY staff_count DESC
LIMIT 1;</code></pre>

<p><strong>Performance</strong>: an index on <code>department</code> helps the GROUP BY by letting MySQL avoid a separate sort step.</p>
'''

ANSWERS[24] = r'''
<pre><code>SELECT id, name, salary
FROM employees
WHERE salary IS NOT NULL
ORDER BY salary DESC, id ASC
LIMIT 3;</code></pre>

<p>Sort by salary descending and limit to 3. The secondary sort by <code>id ASC</code> makes ties deterministic &mdash; without it, two employees with the same salary might appear in different orders on different runs.</p>

<p><strong>Top 3 with ties included</strong> &mdash; if 5 employees are tied for the 3rd-highest salary, this returns all of them:</p>

<pre><code>SELECT id, name, salary FROM (
  SELECT id, name, salary,
         DENSE_RANK() OVER (ORDER BY salary DESC) AS rk
  FROM employees
  WHERE salary IS NOT NULL
) ranked
WHERE rk &lt;= 3
ORDER BY salary DESC, id ASC;</code></pre>

<p><code>DENSE_RANK()</code> assigns the same rank to ties without gaps &mdash; if two employees tie for #1, the next is #2, not #3.</p>

<p><strong>RANK() vs DENSE_RANK() vs ROW_NUMBER()</strong>:</p>

<table>
  <tr><th>Function</th><th>If two tie for #1, the next is...</th></tr>
  <tr><td><code>ROW_NUMBER()</code></td><td>#3 (each row gets a unique number)</td></tr>
  <tr><td><code>RANK()</code></td><td>#3 (gap after the tie)</td></tr>
  <tr><td><code>DENSE_RANK()</code></td><td>#2 (no gap)</td></tr>
</table>

<p><strong>Top 3 by department</strong> &mdash; per-group "top N" with window functions:</p>

<pre><code>SELECT department, name, salary
FROM (
  SELECT department, name, salary,
         ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
  FROM employees
  WHERE salary IS NOT NULL
) ranked
WHERE rn &lt;= 3
ORDER BY department, salary DESC;</code></pre>

<p><strong>Performance</strong>: an index on <code>salary</code> makes the basic query fast (the index already stores values sorted, so MySQL reads the last 3 entries directly):</p>

<pre><code>CREATE INDEX idx_employees_salary ON employees(salary);</code></pre>
'''

ANSWERS[25] = r'''
<pre><code>CREATE TABLE departments (
  department_id   INT AUTO_INCREMENT PRIMARY KEY,
  department_name VARCHAR(100) NOT NULL UNIQUE,
  budget          DECIMAL(15, 2),
  manager_id      INT,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;</code></pre>

<p>The minimum the question asks for is just the two named columns &mdash; <code>department_id</code> and <code>department_name</code>. The version above adds production essentials:</p>

<ul>
  <li><strong><code>UNIQUE</code> on department_name</strong> &mdash; prevents duplicate department records.</li>
  <li><strong><code>NOT NULL</code> on department_name</strong> &mdash; a department must have a name.</li>
  <li><strong><code>budget</code> as DECIMAL</strong> &mdash; correct type for money.</li>
  <li><strong><code>manager_id</code> with FK</strong> &mdash; references the employees table; <code>ON DELETE SET NULL</code> means deleting a manager doesn&rsquo;t orphan the department.</li>
  <li><strong><code>created_at</code> with default</strong> &mdash; automatic timestamp.</li>
</ul>

<p><strong>Bare minimum for the question</strong>:</p>

<pre><code>CREATE TABLE departments (
  department_id   INT AUTO_INCREMENT PRIMARY KEY,
  department_name VARCHAR(100) NOT NULL
);</code></pre>

<p><strong>Schema design considerations</strong>:</p>
<ul>
  <li>Consider whether <code>department_id</code> should be the PK in the <code>employees</code> table&rsquo;s FK reference (typically yes &mdash; surrogate keys are stable; the name might change).</li>
  <li>Reference from <code>employees</code>:
<pre><code>ALTER TABLE employees
ADD COLUMN department_id INT,
ADD CONSTRAINT fk_emp_department
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
  ON DELETE SET NULL;</code></pre>
  </li>
  <li>If keeping the existing <code>department</code> string column on employees, migrate the data:
<pre><code>UPDATE employees e
JOIN departments d ON d.department_name = e.department
SET e.department_id = d.department_id;</code></pre>
  </li>
</ul>

<p><strong>Naming conventions</strong>: some teams prefer <code>id</code> consistently as the PK column name; others prefer <code>department_id</code> for clarity in joins. Pick one and use it consistently.</p>
'''

ANSWERS[26] = r'''
<pre><code>INSERT INTO departments (department_name, budget)
VALUES ('Engineering', 1500000.00);</code></pre>

<p><code>department_id</code> is omitted because it&rsquo;s <code>AUTO_INCREMENT</code>. <code>created_at</code> uses its default.</p>

<p><strong>Bulk insert</strong> for seeding:</p>

<pre><code>INSERT INTO departments (department_name, budget) VALUES
  ('Engineering',  1500000.00),
  ('HR',            450000.00),
  ('Sales',        2200000.00),
  ('Marketing',     800000.00),
  ('Finance',       650000.00),
  ('Operations',    900000.00);</code></pre>

<p><strong>Get the auto-generated ID</strong> after inserting &mdash; useful when you need to immediately use the new row:</p>

<pre><code>INSERT INTO departments (department_name, budget)
VALUES ('R&amp;D', 1100000.00);

SELECT LAST_INSERT_ID();
-- Returns the auto-increment value just generated.

-- Or, with named binding:
INSERT INTO departments (department_name) VALUES ('R&amp;D');
SET @new_dept_id = LAST_INSERT_ID();
INSERT INTO employees (name, department_id) VALUES ('Alice', @new_dept_id);</code></pre>

<p><strong>Skip duplicates</strong> &mdash; if <code>department_name</code> has a UNIQUE constraint, you can use <code>INSERT IGNORE</code> for idempotent seed scripts:</p>

<pre><code>INSERT IGNORE INTO departments (department_name, budget)
VALUES ('Engineering', 1500000.00);
-- If 'Engineering' already exists, this row is silently skipped.</code></pre>

<p><strong>Insert or update</strong> &mdash; useful for upsert workflows:</p>

<pre><code>INSERT INTO departments (department_name, budget)
VALUES ('Engineering', 1500000.00)
ON DUPLICATE KEY UPDATE budget = VALUES(budget);
-- If a row with this name exists, update its budget.</code></pre>

<p><strong>From application code</strong>, parameterize all values:</p>

<pre><code>// Node.js with mysql2
const [result] = await conn.execute(
  'INSERT INTO departments (department_name, budget) VALUES (?, ?)',
  ['Engineering', 1500000]
);
console.log('New department_id:', result.insertId);</code></pre>
'''

ANSWERS[27] = r'''
<pre><code>UPDATE departments
SET department_name = 'People Operations'
WHERE department_id = 5;</code></pre>

<p>Identify by the primary key, then set the new value. Always test the WHERE first with a SELECT to ensure you&rsquo;re changing exactly the right row:</p>

<pre><code>SELECT department_id, department_name FROM departments WHERE department_id = 5;
-- Confirm this is the row you want to change, then:
UPDATE departments SET department_name = 'People Operations' WHERE department_id = 5;</code></pre>

<p><strong>Update multiple columns</strong>:</p>

<pre><code>UPDATE departments
SET department_name = 'People Operations',
    budget          = 600000.00,
    updated_at      = NOW()
WHERE department_id = 5;</code></pre>

<p><strong>Wrap in a transaction</strong> for safety &mdash; especially if related changes need to happen together:</p>

<pre><code>START TRANSACTION;

UPDATE departments
SET department_name = 'People Operations'
WHERE department_id = 5;

-- If renaming requires an audit log:
INSERT INTO departments_history (department_id, old_name, new_name, changed_at)
VALUES (5, 'HR', 'People Operations', NOW());

COMMIT;
-- Or ROLLBACK; if anything went wrong</code></pre>

<p><strong>Watch out for foreign keys</strong>: if other tables reference this department&rsquo;s name (poor practice, but happens), they won&rsquo;t auto-update. Better to reference by <code>department_id</code> &mdash; the surrogate key &mdash; so renaming has no ripple effect:</p>

<pre><code>-- Good: employees references by ID, not name
ALTER TABLE employees
ADD CONSTRAINT fk_dept FOREIGN KEY (department_id)
  REFERENCES departments(department_id);

-- Now updating department_name affects only the departments table.</code></pre>

<p><strong>Bulk rename</strong>:</p>

<pre><code>-- Rename based on a mapping table
UPDATE departments d
JOIN dept_renames r ON r.old_name = d.department_name
SET d.department_name = r.new_name;</code></pre>

<p><strong>From application code</strong>, parameterize all values to avoid SQL injection:</p>

<pre><code>await conn.execute(
  'UPDATE departments SET department_name = ? WHERE department_id = ?',
  [newName, deptId]
);</code></pre>
'''

ANSWERS[28] = r'''
<pre><code>DELETE FROM departments
WHERE department_id = 5;</code></pre>

<p>The risk: if employees reference this <code>department_id</code> via foreign key, MySQL behavior depends on how the FK was defined.</p>

<p><strong>Foreign key behaviors</strong>:</p>

<table>
  <tr><th>FK action</th><th>What happens to dependent rows</th></tr>
  <tr><td><code>ON DELETE RESTRICT</code> (default)</td><td>Delete is blocked; error returned</td></tr>
  <tr><td><code>ON DELETE SET NULL</code></td><td>Dependent rows&rsquo; FK column is set to NULL</td></tr>
  <tr><td><code>ON DELETE CASCADE</code></td><td>Dependent rows are deleted too</td></tr>
  <tr><td><code>ON DELETE NO ACTION</code></td><td>Same as RESTRICT in InnoDB</td></tr>
</table>

<p>If FKs default to RESTRICT and employees still reference this department, the delete fails:</p>

<pre><code>ERROR 1451 (23000): Cannot delete or update a parent row:
a foreign key constraint fails (`company`.`employees`,
CONSTRAINT `fk_dept` FOREIGN KEY (`department_id`)
REFERENCES `departments` (`department_id`))</code></pre>

<p><strong>Resolution options</strong>:</p>

<pre><code>-- Option A: reassign employees first
UPDATE employees
SET department_id = (SELECT department_id FROM departments WHERE department_name = 'Unassigned')
WHERE department_id = 5;
DELETE FROM departments WHERE department_id = 5;

-- Option B: NULL out the FK
UPDATE employees SET department_id = NULL WHERE department_id = 5;
DELETE FROM departments WHERE department_id = 5;

-- Option C: cascade delete (deletes employees too — usually not what you want!)
ALTER TABLE employees
DROP FOREIGN KEY fk_dept,
ADD CONSTRAINT fk_dept FOREIGN KEY (department_id)
  REFERENCES departments(department_id) ON DELETE CASCADE;
DELETE FROM departments WHERE department_id = 5;</code></pre>

<p><strong>Soft delete pattern</strong> &mdash; instead of physically deleting, mark as deleted. Preserves history and supports undo:</p>

<pre><code>UPDATE departments
SET deleted_at = NOW()
WHERE department_id = 5;

-- Application queries exclude soft-deleted:
SELECT * FROM departments WHERE deleted_at IS NULL;</code></pre>

<p><strong>Transaction-wrapped deletion</strong>:</p>

<pre><code>START TRANSACTION;
UPDATE employees SET department_id = NULL WHERE department_id = 5;
DELETE FROM departments WHERE department_id = 5;
COMMIT;</code></pre>

<p>Always use a transaction when a delete has multiple steps &mdash; if anything fails partway, <code>ROLLBACK</code> restores the original state.</p>
'''

ANSWERS[29] = r'''
<pre><code>-- 1. Make sure the column exists with a matching type
ALTER TABLE employees
ADD COLUMN department_id INT;

-- 2. Add the foreign key constraint
ALTER TABLE employees
ADD CONSTRAINT fk_emp_department
  FOREIGN KEY (department_id)
  REFERENCES departments(department_id)
  ON DELETE SET NULL
  ON UPDATE CASCADE;</code></pre>

<p>The <code>fk_emp_department</code> name lets you reference the constraint later (to drop or modify it). Without naming, MySQL auto-generates one.</p>

<p><strong>The FK column type must match the referenced primary key type exactly</strong> &mdash; <code>INT</code> matches <code>INT</code>, <code>BIGINT</code> matches <code>BIGINT</code>; <code>INT</code> referring to <code>BIGINT</code> fails.</p>

<p><strong>Inline at table creation</strong>:</p>

<pre><code>CREATE TABLE employees (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  department_id INT,

  FOREIGN KEY (department_id) REFERENCES departments(department_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);</code></pre>

<p><strong>Referential actions</strong> &mdash; what happens to rows in <code>employees</code> when the referenced department is deleted or its ID changes:</p>

<table>
  <tr><th>Action</th><th>On parent change/delete</th></tr>
  <tr><td><code>RESTRICT</code> / <code>NO ACTION</code></td><td>Block parent change/delete (default)</td></tr>
  <tr><td><code>CASCADE</code></td><td>Apply same change to children (e.g., delete dependent rows)</td></tr>
  <tr><td><code>SET NULL</code></td><td>Set FK to NULL (column must be nullable)</td></tr>
  <tr><td><code>SET DEFAULT</code></td><td>Not enforced in InnoDB; behaves like NO ACTION</td></tr>
</table>

<p><strong>Common patterns</strong>:</p>
<ul>
  <li><code>ON DELETE SET NULL</code> + <code>ON UPDATE CASCADE</code> &mdash; sensible for optional relationships.</li>
  <li><code>ON DELETE RESTRICT</code> &mdash; refuses deletion if dependents exist (force the application to clean up first).</li>
  <li><code>ON DELETE CASCADE</code> &mdash; for "owned" relationships (e.g., order items belong to an order).</li>
</ul>

<p><strong>Storage engine matters</strong>: foreign keys are only enforced by <strong>InnoDB</strong> (the default in modern MySQL). MyISAM tables silently accept FK syntax but don&rsquo;t enforce it.</p>

<p><strong>Drop the FK</strong> if needed:</p>

<pre><code>ALTER TABLE employees DROP FOREIGN KEY fk_emp_department;</code></pre>
'''

ANSWERS[30] = r'''
<pre><code>SELECT
  e.id,
  e.name AS employee_name,
  d.department_name,
  e.salary
FROM employees e
JOIN departments d ON d.department_id = e.department_id
ORDER BY d.department_name, e.name;</code></pre>

<p>This is an <code>INNER JOIN</code> (the keyword <code>INNER</code> is optional). It returns only rows where the join condition matches in both tables &mdash; employees without a department and departments with no employees are <em>excluded</em>.</p>

<p><strong>Include employees without a department</strong> &mdash; use a <code>LEFT JOIN</code>:</p>

<pre><code>SELECT
  e.id,
  e.name AS employee_name,
  COALESCE(d.department_name, 'Unassigned') AS department_name
FROM employees e
LEFT JOIN departments d ON d.department_id = e.department_id
ORDER BY d.department_name, e.name;</code></pre>

<p><code>LEFT JOIN</code> keeps every row from the left (employees) table; for non-matching rows, columns from the right table are <code>NULL</code>. <code>COALESCE</code> displays a friendly placeholder.</p>

<p><strong>Aliases</strong> (<code>e</code> for employees, <code>d</code> for departments) make the query much shorter when columns from multiple tables are mixed.</p>

<p><strong>Multiple joins</strong> &mdash; chain them:</p>

<pre><code>SELECT
  e.name AS employee_name,
  d.department_name,
  m.name AS manager_name
FROM employees e
LEFT JOIN departments d ON d.department_id = e.department_id
LEFT JOIN employees m ON m.id = e.manager_id;
-- The same employees table is joined to itself for managers</code></pre>

<p><strong>Performance</strong>: indexes on the join columns make this fast. Both <code>employees.department_id</code> and <code>departments.department_id</code> should be indexed (the PK on departments already is; ensure FK in employees is too):</p>

<pre><code>CREATE INDEX idx_employees_department_id
ON employees(department_id);

EXPLAIN SELECT e.name, d.department_name
FROM employees e
JOIN departments d ON d.department_id = e.department_id;
-- Look for type=ref or type=eq_ref on the joined tables</code></pre>

<p>For a small <code>departments</code> table joined to a large <code>employees</code> table, MySQL typically does a hash join in 8.0+ &mdash; very efficient.</p>
'''

ANSWERS[31] = r'''
<pre><code>SELECT id, name, department_id
FROM employees
WHERE department_id IS NULL;</code></pre>

<p>The <code>IS NULL</code> operator is the only way to test for NULL &mdash; <code>= NULL</code> always evaluates to NULL (which is falsy in WHERE), so <code>WHERE department_id = NULL</code> returns nothing even if many rows have NULL.</p>

<p><strong>If "no department" is represented by a sentinel value</strong> instead of NULL (e.g., <code>0</code> or <code>-1</code>):</p>

<pre><code>SELECT id, name FROM employees
WHERE department_id IS NULL OR department_id = 0;</code></pre>

<p><strong>Find employees with a department_id that doesn&rsquo;t actually exist</strong> in the departments table &mdash; a data integrity check:</p>

<pre><code>SELECT e.id, e.name, e.department_id
FROM employees e
LEFT JOIN departments d ON d.department_id = e.department_id
WHERE e.department_id IS NOT NULL
  AND d.department_id IS NULL;
-- Has a department_id, but no matching department row.</code></pre>

<p>This pattern detects orphaned references &mdash; rows that should have been cleaned up when their parent was deleted. With proper foreign key constraints (RESTRICT, CASCADE, or SET NULL), these shouldn&rsquo;t exist; without FKs, they&rsquo;re common.</p>

<p><strong>NOT IN with subquery</strong> &mdash; another way to find unmatched rows, but it has a NULL trap:</p>

<pre><code>-- ❌ Bad: returns nothing if any dept row has NULL
SELECT * FROM employees
WHERE department_id NOT IN (SELECT department_id FROM departments);

-- ✅ Better: NOT EXISTS handles NULL correctly
SELECT e.* FROM employees e
WHERE NOT EXISTS (
  SELECT 1 FROM departments d
  WHERE d.department_id = e.department_id
);</code></pre>

<p>The <code>NOT IN</code> form fails because <code>x NOT IN (1, 2, NULL)</code> evaluates to NULL (not TRUE), so no rows are returned. <code>NOT EXISTS</code> uses correlated logic that handles NULL correctly.</p>

<p><strong>Performance</strong>: an index on <code>department_id</code> makes this fast. <code>IS NULL</code> can use the index in modern MySQL.</p>
'''

ANSWERS[32] = r'''
<pre><code>-- Assumes a junction table for many-to-many
SELECT e.id, e.name, COUNT(*) AS department_count
FROM employees e
JOIN employee_departments ed ON ed.employee_id = e.id
GROUP BY e.id, e.name
HAVING COUNT(*) &gt; 1
ORDER BY department_count DESC;</code></pre>

<p>The original schema (with <code>department_id</code> directly on <code>employees</code>) only supports one department per employee. To allow many departments per employee, you need a junction table:</p>

<pre><code>CREATE TABLE employee_departments (
  employee_id   INT NOT NULL,
  department_id INT NOT NULL,
  is_primary    BOOLEAN DEFAULT FALSE,
  assigned_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (employee_id, department_id),
  FOREIGN KEY (employee_id)   REFERENCES employees(id)              ON DELETE CASCADE,
  FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Indexes for both directions of the join
CREATE INDEX idx_ed_dept ON employee_departments(department_id);</code></pre>

<p>The composite primary key (<code>employee_id</code>, <code>department_id</code>) prevents adding the same employee to the same department twice.</p>

<p><strong>To find their department names too</strong>:</p>

<pre><code>SELECT e.id, e.name,
       GROUP_CONCAT(d.department_name ORDER BY d.department_name SEPARATOR ', ') AS departments,
       COUNT(*) AS department_count
FROM employees e
JOIN employee_departments ed ON ed.employee_id = e.id
JOIN departments d           ON d.department_id = ed.department_id
GROUP BY e.id, e.name
HAVING department_count &gt; 1
ORDER BY department_count DESC, e.name;</code></pre>

<p><code>GROUP_CONCAT</code> aggregates the department names into a comma-separated list per employee.</p>

<p><strong>If the question assumes the original single-department schema</strong>, "more than one department" doesn&rsquo;t apply &mdash; clarify in the interview. A common interpretation: find employees whose <em>name</em> appears in multiple departments (likely duplicate employees with different IDs):</p>

<pre><code>SELECT name, COUNT(DISTINCT department) AS dept_count
FROM employees
WHERE department IS NOT NULL
GROUP BY name
HAVING dept_count &gt; 1;</code></pre>

<p>This pattern signals data quality issues &mdash; either truly duplicate names, or one person mistakenly entered twice with different IDs.</p>
'''

ANSWERS[33] = r'''
<pre><code>CREATE INDEX idx_employees_name ON employees(name);

-- Equivalent ALTER syntax
ALTER TABLE employees
ADD INDEX idx_employees_name (name);</code></pre>

<p>An index on <code>name</code> speeds up queries that filter, join, or sort on the name column. Without it, <code>WHERE name = 'Alice'</code> requires a full table scan.</p>

<p><strong>Indexes don&rsquo;t help all queries</strong>:</p>
<ul>
  <li><code>WHERE name = 'Alice'</code> &mdash; fast (uses index).</li>
  <li><code>WHERE name LIKE 'A%'</code> &mdash; fast (anchored prefix).</li>
  <li><code>WHERE name LIKE '%lice'</code> &mdash; <em>slow</em> (leading wildcard prevents index use).</li>
  <li><code>WHERE LOWER(name) = 'alice'</code> &mdash; <em>slow</em> (function on column prevents index use; create a generated column or use a case-insensitive collation instead).</li>
</ul>

<p><strong>Composite index for multi-column queries</strong>:</p>

<pre><code>-- Helps queries filtering on department AND sorting/filtering by name
CREATE INDEX idx_employees_dept_name
ON employees(department, name);</code></pre>

<p>A composite index on <code>(department, name)</code> can satisfy queries on <code>(department)</code>, <code>(department, name)</code>, but not <code>(name)</code> alone or <code>(name, department)</code>. Column order matters &mdash; put the most selective filter first.</p>

<p><strong>Unique index</strong> &mdash; if names should be unique:</p>

<pre><code>CREATE UNIQUE INDEX uk_employees_name ON employees(name);</code></pre>

<p>Inserting a duplicate name now fails. (Usually you index something like <code>email</code> uniquely, not <code>name</code>.)</p>

<p><strong>Trade-offs</strong>:</p>
<ul>
  <li>Indexes make reads faster but writes slower (every INSERT/UPDATE/DELETE must update the index).</li>
  <li>Indexes consume disk space and memory (the index pages live in the InnoDB buffer pool).</li>
  <li>Too many indexes = no benefit + significant write overhead.</li>
</ul>

<p><strong>Verify the index is being used</strong>:</p>

<pre><code>EXPLAIN SELECT * FROM employees WHERE name = 'Alice';
-- Look for type=ref and key=idx_employees_name in the output</code></pre>

<p>If <code>type=ALL</code>, the query is doing a full scan &mdash; the index isn&rsquo;t helping.</p>
'''

ANSWERS[34] = r'''
<pre><code>DROP INDEX idx_employees_name ON employees;

-- Equivalent ALTER syntax
ALTER TABLE employees
DROP INDEX idx_employees_name;</code></pre>

<p>You need the index <em>name</em>, not the column name. To find it:</p>

<pre><code>SHOW INDEX FROM employees;

-- Output columns of interest:
-- Key_name | Column_name | Non_unique | Index_type</code></pre>

<p><strong>Or via information_schema</strong>:</p>

<pre><code>SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'company'
  AND TABLE_NAME   = 'employees';</code></pre>

<p><strong>Cannot drop directly</strong>:</p>
<ul>
  <li>The <strong>primary key index</strong> &mdash; use <code>ALTER TABLE ... DROP PRIMARY KEY</code>.</li>
  <li>An <strong>index that supports a foreign key</strong> &mdash; drop the FK first, or MySQL will refuse:
<pre><code>ALTER TABLE employees DROP FOREIGN KEY fk_emp_dept;
ALTER TABLE employees DROP INDEX idx_dept;</code></pre>
  </li>
</ul>

<p><strong>When to drop indexes</strong>:</p>
<ul>
  <li>The query they were added for no longer runs.</li>
  <li>A composite index supersedes an older single-column index (e.g., index on <code>(a, b)</code> can serve queries that previously used the index on <code>(a)</code>).</li>
  <li>Write performance is suffering from too many indexes.</li>
  <li>The column distribution changed and the index is no longer selective (e.g., 99% of rows now have the same value).</li>
</ul>

<p><strong>Find unused indexes</strong> &mdash; query the Performance Schema:</p>

<pre><code>SELECT object_schema, object_name, index_name
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL
  AND count_star = 0
  AND object_schema = 'company';
-- Indexes that have never been used since the server started.</code></pre>

<p><strong>Test before dropping in production</strong>: profile your queries with <code>EXPLAIN</code> in a copy of the schema after dropping. The query optimizer may suddenly choose a much slower plan, even for queries you didn&rsquo;t expect.</p>

<p><strong>Performance impact of dropping</strong>: typically fast on small tables; can take time on huge tables (the data file is rewritten in some cases). For online drops on production, MySQL 8 supports <code>ALGORITHM=INPLACE</code>:</p>

<pre><code>ALTER TABLE huge_table DROP INDEX idx_old, ALGORITHM=INPLACE, LOCK=NONE;</code></pre>
'''

ANSWERS[35] = r'''
<pre><code>CREATE VIEW employee_details AS
SELECT
  e.id,
  e.name AS employee_name,
  e.age,
  d.department_name,
  e.created_at
FROM employees e
LEFT JOIN departments d ON d.department_id = e.department_id;</code></pre>

<p>A view is a saved query that behaves like a virtual table. Querying <code>employee_details</code> internally executes the SELECT each time:</p>

<pre><code>SELECT * FROM employee_details
WHERE department_name = 'Engineering';

-- Equivalent to running the underlying SELECT with the WHERE pushed down.</code></pre>

<p><strong>Why use views</strong>:</p>
<ul>
  <li><strong>Encapsulation</strong> &mdash; hide a complex join behind a simple name; queries become readable.</li>
  <li><strong>Access control</strong> &mdash; grant a user SELECT on the view without granting access to the underlying tables. They see only the columns/rows the view exposes.</li>
  <li><strong>Stable interface</strong> &mdash; the underlying schema can change (rename columns, restructure tables) while the view&rsquo;s shape stays the same; application code doesn&rsquo;t break.</li>
  <li><strong>Reusability</strong> &mdash; the same complex query reused across many places.</li>
</ul>

<p><strong>Updatable views</strong> &mdash; some views allow <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code> through them, with restrictions:</p>

<pre><code>-- Updatable: simple, no joins, no aggregations
CREATE VIEW active_employees AS
SELECT id, name, age FROM employees WHERE deleted_at IS NULL;

UPDATE active_employees SET age = 30 WHERE id = 5;
-- Translates to: UPDATE employees SET age = 30 WHERE id = 5 AND deleted_at IS NULL;</code></pre>

<p>Views with joins or aggregates are typically read-only.</p>

<p><strong>Materialized views</strong>: MySQL has no built-in materialized views. To cache a view&rsquo;s result for performance, manually maintain a real table:</p>

<pre><code>CREATE TABLE employee_details_cache AS SELECT * FROM employee_details;

-- Refresh on a schedule (cron job or trigger)
TRUNCATE TABLE employee_details_cache;
INSERT INTO employee_details_cache SELECT * FROM employee_details;</code></pre>

<p><strong>Modify a view</strong>:</p>

<pre><code>CREATE OR REPLACE VIEW employee_details AS
SELECT ... -- new definition
;</code></pre>
'''

ANSWERS[36] = r'''
<pre><code>SELECT * FROM employee_details;

-- Or with filtering, just like a normal table
SELECT id, employee_name, department_name
FROM employee_details
WHERE department_name = 'Engineering'
ORDER BY employee_name;</code></pre>

<p>From the application&rsquo;s perspective, a view is identical to a table &mdash; it accepts <code>WHERE</code>, <code>ORDER BY</code>, <code>LIMIT</code>, and joins.</p>

<p><strong>Behind the scenes</strong>, MySQL has two strategies for executing a query against a view:</p>

<table>
  <tr><th>Algorithm</th><th>Behavior</th></tr>
  <tr><td><code>MERGE</code></td><td>The view&rsquo;s SELECT is merged into the outer query, so MySQL runs one combined query against the base tables. Best for performance.</td></tr>
  <tr><td><code>TEMPTABLE</code></td><td>The view&rsquo;s SELECT runs first, results stored in a temporary table; outer query runs against that. Necessary when MERGE isn&rsquo;t possible (aggregations, DISTINCT, certain subqueries).</td></tr>
</table>

<p>You can hint the desired algorithm:</p>

<pre><code>CREATE ALGORITHM = MERGE VIEW employee_details AS ...;
CREATE ALGORITHM = TEMPTABLE VIEW employee_details AS ...;</code></pre>

<p><strong>Inspect a view&rsquo;s definition</strong>:</p>

<pre><code>SHOW CREATE VIEW employee_details\G</code></pre>

<p><strong>Drop a view</strong>:</p>

<pre><code>DROP VIEW IF EXISTS employee_details;</code></pre>

<p><strong>Useful joins on views</strong>:</p>

<pre><code>-- Join a view with another table
SELECT ed.employee_name, p.project_name
FROM employee_details ed
JOIN employee_projects ep ON ep.employee_id = ed.id
JOIN projects p           ON p.id = ep.project_id
WHERE ed.department_name = 'Engineering';</code></pre>

<p><strong>Performance considerations</strong>:</p>
<ul>
  <li>Views don&rsquo;t store data &mdash; each query re-executes the underlying SELECT. They&rsquo;re no faster than the equivalent direct query.</li>
  <li>Indexes are on the underlying tables; the view inherits whatever performance those indexes provide.</li>
  <li>Stacked views (a view that queries another view) can confuse the optimizer in older MySQL versions; check <code>EXPLAIN</code> output if performance is bad.</li>
</ul>

<p><strong>Permissions</strong>: granting <code>SELECT</code> on the view doesn&rsquo;t require granting <code>SELECT</code> on the base tables &mdash; useful for restricting which columns/rows a user can see.</p>
'''

ANSWERS[37] = r'''
<pre><code>DELIMITER //

CREATE PROCEDURE insert_employee(
  IN p_name       VARCHAR(100),
  IN p_age        INT,
  IN p_department VARCHAR(50)
)
BEGIN
  INSERT INTO employees (name, age, department)
  VALUES (p_name, p_age, p_department);

  SELECT LAST_INSERT_ID() AS new_employee_id;
END //

DELIMITER ;</code></pre>

<p>The <code>DELIMITER //</code> at the start changes the statement terminator from <code>;</code> to <code>//</code> &mdash; necessary because the procedure body itself contains semicolons. After the procedure is defined, <code>DELIMITER ;</code> restores the default.</p>

<p><strong>Parameter modes</strong>:</p>
<ul>
  <li><strong><code>IN</code></strong> &mdash; input only (default). Caller passes a value in.</li>
  <li><strong><code>OUT</code></strong> &mdash; output only. Caller passes a variable; procedure writes into it.</li>
  <li><strong><code>INOUT</code></strong> &mdash; both directions.</li>
</ul>

<p><strong>Procedure with output parameter</strong>:</p>

<pre><code>DELIMITER //

CREATE PROCEDURE insert_employee_v2(
  IN  p_name       VARCHAR(100),
  IN  p_age        INT,
  IN  p_department VARCHAR(50),
  OUT p_new_id     INT
)
BEGIN
  INSERT INTO employees (name, age, department)
  VALUES (p_name, p_age, p_department);

  SET p_new_id = LAST_INSERT_ID();
END //

DELIMITER ;

-- Call it
CALL insert_employee_v2('Alice', 28, 'Engineering', @new_id);
SELECT @new_id;</code></pre>

<p><strong>With validation and error handling</strong>:</p>

<pre><code>DELIMITER //

CREATE PROCEDURE insert_employee_safe(
  IN p_name       VARCHAR(100),
  IN p_age        INT,
  IN p_department VARCHAR(50)
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  IF p_age IS NOT NULL AND p_age &lt; 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid age';
  END IF;

  START TRANSACTION;
  INSERT INTO employees (name, age, department)
  VALUES (p_name, p_age, p_department);
  COMMIT;
END //

DELIMITER ;</code></pre>

<p><strong>When to use stored procedures</strong>:</p>
<ul>
  <li>Encapsulating multi-statement business logic that always runs together (transactions).</li>
  <li>Reducing network round-trips for batch operations.</li>
  <li>Granting EXECUTE access without granting direct table privileges.</li>
</ul>

<p><strong>Modern alternative</strong>: most teams now keep business logic in application code (more testable, version-controlled, easier to debug) and use stored procedures sparingly. ORMs (Prisma, Drizzle, TypeORM) and query builders typically don&rsquo;t use them.</p>
'''

ANSWERS[38] = r'''
<pre><code>CALL insert_employee('Alice Johnson', 28, 'Engineering');</code></pre>

<p><code>CALL</code> is the standard way to invoke a stored procedure. Procedures with no parameters use empty parentheses: <code>CALL my_proc()</code>.</p>

<p><strong>With output parameters</strong> &mdash; declare user variables (prefixed with <code>@</code>) for the procedure to populate:</p>

<pre><code>CALL insert_employee_v2('Alice', 28, 'Engineering', @new_id);
SELECT @new_id;
-- Returns the auto-incremented ID generated by the procedure.</code></pre>

<p><strong>Inspect the result rows</strong>: if the procedure executes a <code>SELECT</code> internally, the rows are returned to the client as if you&rsquo;d run the SELECT directly. Multiple result sets are possible:</p>

<pre><code>DELIMITER //
CREATE PROCEDURE department_summary(IN p_dept VARCHAR(50))
BEGIN
  SELECT COUNT(*) AS staff_count FROM employees WHERE department = p_dept;
  SELECT AVG(age) AS avg_age FROM employees WHERE department = p_dept;
END //
DELIMITER ;

CALL department_summary('Engineering');
-- Client gets two result sets back.</code></pre>

<p><strong>From application code</strong>:</p>

<pre><code>// Node.js with mysql2
const [rows, fields] = await conn.query(
  'CALL insert_employee(?, ?, ?)',
  ['Alice', 28, 'Engineering']
);

// For procedures with multiple result sets, mysql2 returns an array of arrays.
console.log(rows);  // either an array of result rows, or an array of result sets</code></pre>

<pre><code># Python with PyMySQL or aiomysql
async with conn.cursor() as cur:
    await cur.callproc('insert_employee', ('Alice', 28, 'Engineering'))
    rows = await cur.fetchall()</code></pre>

<p><strong>Permissions</strong>: the calling user needs the <code>EXECUTE</code> privilege on the procedure. The procedure itself runs with the privileges of its <em>definer</em> (the user who created it) by default &mdash; this is the <code>SQL SECURITY DEFINER</code> behavior. To use the caller&rsquo;s privileges instead:</p>

<pre><code>CREATE PROCEDURE my_proc(...)
SQL SECURITY INVOKER
BEGIN
  ...
END;</code></pre>

<p><strong>Inspect existing procedures</strong>:</p>

<pre><code>SHOW PROCEDURE STATUS WHERE Db = 'company';
SHOW CREATE PROCEDURE insert_employee\G</code></pre>
'''

ANSWERS[39] = r'''
<pre><code>-- First, the audit table
CREATE TABLE employee_audit (
  audit_id    INT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  action      VARCHAR(20),
  changed_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_by  VARCHAR(100),
  old_data    JSON,
  new_data    JSON
);

-- The trigger
DELIMITER //

CREATE TRIGGER trg_employees_after_insert
AFTER INSERT ON employees
FOR EACH ROW
BEGIN
  INSERT INTO employee_audit (employee_id, action, changed_by, new_data)
  VALUES (
    NEW.id,
    'INSERT',
    CURRENT_USER(),
    JSON_OBJECT(
      'name',       NEW.name,
      'age',        NEW.age,
      'department', NEW.department
    )
  );
END //

DELIMITER ;</code></pre>

<p>The trigger fires automatically after every <code>INSERT</code> on <code>employees</code>. The <code>NEW</code> pseudo-row gives access to the values being inserted.</p>

<p><strong>Trigger syntax breakdown</strong>:</p>
<ul>
  <li><strong>Timing</strong>: <code>BEFORE</code> or <code>AFTER</code> the event.</li>
  <li><strong>Event</strong>: <code>INSERT</code>, <code>UPDATE</code>, or <code>DELETE</code>.</li>
  <li><strong>Granularity</strong>: <code>FOR EACH ROW</code> &mdash; runs once per affected row (the only option in MySQL).</li>
  <li><strong><code>OLD</code> / <code>NEW</code></strong> &mdash; pseudo-rows; available based on the event:
    <ul>
      <li>INSERT &mdash; <code>NEW</code> only.</li>
      <li>UPDATE &mdash; both <code>OLD</code> and <code>NEW</code>.</li>
      <li>DELETE &mdash; <code>OLD</code> only.</li>
    </ul>
  </li>
</ul>

<p><strong>For UPDATE auditing</strong> &mdash; capture both old and new values:</p>

<pre><code>DELIMITER //
CREATE TRIGGER trg_employees_after_update
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
  INSERT INTO employee_audit (employee_id, action, changed_by, old_data, new_data)
  VALUES (
    NEW.id,
    'UPDATE',
    CURRENT_USER(),
    JSON_OBJECT('name', OLD.name, 'department', OLD.department),
    JSON_OBJECT('name', NEW.name, 'department', NEW.department)
  );
END //
DELIMITER ;</code></pre>

<p><strong>Caveats</strong>:</p>
<ul>
  <li>Triggers run within the same transaction as the triggering statement &mdash; if the trigger fails, the original INSERT/UPDATE/DELETE rolls back too.</li>
  <li>Triggers can&rsquo;t modify the table they fire on (no recursive triggers in MySQL).</li>
  <li>Heavy trigger logic slows down every write &mdash; keep the body small.</li>
  <li>Triggers can be invisible &mdash; document them, or developers will be confused why data changes "by itself."</li>
</ul>

<p><strong>Modern alternatives</strong>: many teams use application-layer audit (Hibernate/Sequelize hooks), CDC tools (Debezium reading the binlog), or temporal tables to track history. Triggers are still useful for hard requirements that the audit can&rsquo;t be bypassed.</p>
'''

ANSWERS[40] = r'''
<pre><code>-- MySQL has no DISABLE TRIGGER syntax.
-- The standard approach is to drop and recreate when needed.
DROP TRIGGER IF EXISTS trg_employees_after_insert;</code></pre>

<p>MySQL doesn&rsquo;t support disabling triggers like SQL Server (<code>DISABLE TRIGGER</code>) or PostgreSQL (<code>ALTER TABLE DISABLE TRIGGER</code>). Workarounds:</p>

<p><strong>Option 1: Drop and recreate</strong> &mdash; clean but you lose the trigger definition unless you save it:</p>

<pre><code>-- Capture the definition first so you can recreate it
SHOW CREATE TRIGGER trg_employees_after_insert\G

-- Drop it
DROP TRIGGER trg_employees_after_insert;

-- Do whatever needed to be done without the trigger firing.

-- Recreate it
DELIMITER //
CREATE TRIGGER trg_employees_after_insert
AFTER INSERT ON employees
FOR EACH ROW
BEGIN
  ... -- original body
END //
DELIMITER ;</code></pre>

<p><strong>Option 2: Conditional logic in the trigger body</strong> &mdash; gate execution on a config value:</p>

<pre><code>CREATE TABLE trigger_config (
  trigger_name VARCHAR(64) PRIMARY KEY,
  enabled      BOOLEAN NOT NULL DEFAULT TRUE
);

DELIMITER //
CREATE TRIGGER trg_employees_after_insert
AFTER INSERT ON employees
FOR EACH ROW
BEGIN
  DECLARE v_enabled BOOLEAN;
  SELECT enabled INTO v_enabled
  FROM trigger_config
  WHERE trigger_name = 'trg_employees_after_insert';

  IF v_enabled THEN
    INSERT INTO employee_audit (...) VALUES (...);
  END IF;
END //
DELIMITER ;

-- "Disable" by flipping the flag:
UPDATE trigger_config SET enabled = FALSE
WHERE trigger_name = 'trg_employees_after_insert';</code></pre>

<p>This adds a query overhead per row but lets you toggle without DDL.</p>

<p><strong>Option 3: Session variable</strong> &mdash; useful for one-off bulk loads:</p>

<pre><code>-- In the trigger body
IF @disable_audit IS NULL OR @disable_audit = 0 THEN
  INSERT INTO employee_audit (...) VALUES (...);
END IF;

-- Caller sets the flag for their session only:
SET @disable_audit = 1;
LOAD DATA INFILE '...' INTO TABLE employees ...;
SET @disable_audit = 0;</code></pre>

<p><strong>List existing triggers</strong>:</p>

<pre><code>SHOW TRIGGERS;
SHOW TRIGGERS FROM company;
SHOW TRIGGERS LIKE 'employees%';

SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE, ACTION_TIMING
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'company';</code></pre>

<p>For complex environments, MariaDB has a <code>DISABLE TRIGGER</code> extension, but it&rsquo;s not in standard MySQL.</p>
'''

ANSWERS[41] = r'''
<pre><code>SELECT name, COUNT(*) AS occurrences
FROM employees
WHERE name IS NOT NULL
GROUP BY name
HAVING COUNT(*) &gt; 1
ORDER BY occurrences DESC, name;</code></pre>

<p>Group by name and keep groups with more than one row. <code>HAVING</code> filters after grouping (<code>WHERE</code> filters before, so it can&rsquo;t reference aggregates).</p>

<p><strong>Get the actual employees too</strong> &mdash; useful for resolving the duplicates:</p>

<pre><code>SELECT id, name, age, department, created_at
FROM employees
WHERE name IN (
  SELECT name FROM employees
  WHERE name IS NOT NULL
  GROUP BY name
  HAVING COUNT(*) &gt; 1
)
ORDER BY name, created_at;</code></pre>

<p>This returns all rows participating in a duplicate.</p>

<p><strong>Or with a self-join</strong>:</p>

<pre><code>SELECT e1.id, e1.name, e1.department, e2.id AS dup_id, e2.department AS dup_department
FROM employees e1
JOIN employees e2 ON e2.name = e1.name AND e2.id &lt;&gt; e1.id
WHERE e1.name IS NOT NULL
ORDER BY e1.name, e1.id;</code></pre>

<p>The <code>e2.id &lt;&gt; e1.id</code> avoids matching rows to themselves.</p>

<p><strong>Case- and whitespace-insensitive matching</strong> &mdash; "John Smith" and "john smith" might be the same person:</p>

<pre><code>SELECT LOWER(TRIM(name)) AS normalized_name, COUNT(*) AS occurrences
FROM employees
WHERE name IS NOT NULL
GROUP BY normalized_name
HAVING COUNT(*) &gt; 1;</code></pre>

<p>(Be aware: applying functions to the column prevents index use; for production use a generated column or store normalized values.)</p>

<p><strong>Find duplicates by composite criteria</strong> &mdash; same name <em>and</em> same department, suggesting truly duplicate records:</p>

<pre><code>SELECT name, department, COUNT(*) AS dup_count, MIN(id) AS keep_id, MAX(id) AS dup_id
FROM employees
GROUP BY name, department
HAVING dup_count &gt; 1;</code></pre>

<p>Useful for a "deduplication" pass: keep the lowest <code>id</code>, delete the rest, after merging any related foreign-key references.</p>

<p><strong>Performance</strong>: an index on <code>name</code> makes the GROUP BY faster &mdash; MySQL can read pre-sorted values from the index.</p>
'''

ANSWERS[42] = r'''
<pre><code>SELECT id, name, hire_date
FROM employees
WHERE hire_date &gt;= DATE_SUB(CURDATE(), INTERVAL 6 MONTH);</code></pre>

<p><code>DATE_SUB(CURDATE(), INTERVAL 6 MONTH)</code> returns the date six calendar months before today.</p>

<p><strong>Equivalent forms</strong>:</p>

<pre><code>-- Using arithmetic
WHERE hire_date &gt;= CURDATE() - INTERVAL 6 MONTH

-- Excluding people hired in the future (data entry errors)
WHERE hire_date BETWEEN CURDATE() - INTERVAL 6 MONTH AND CURDATE()</code></pre>

<p><strong>For DATETIME columns</strong> &mdash; be careful about time-of-day boundaries:</p>

<pre><code>-- Captures everything from 6 months ago at any time
WHERE hire_date &gt;= CURDATE() - INTERVAL 6 MONTH;

-- If you want exactly 6 months ago to right now:
WHERE hire_date &gt;= NOW() - INTERVAL 6 MONTH;</code></pre>

<p><strong>Different time interval units</strong>:</p>

<pre><code>WHERE hire_date &gt;= NOW() - INTERVAL 6 MONTH;
WHERE hire_date &gt;= NOW() - INTERVAL 30 DAY;
WHERE hire_date &gt;= NOW() - INTERVAL 1 YEAR;
WHERE hire_date &gt;= NOW() - INTERVAL 2 WEEK;
WHERE hire_date &gt;= NOW() - INTERVAL 90 MINUTE;</code></pre>

<p><strong>Always use parameterized "now" in date comparisons rather than hard-coded dates</strong> &mdash; the query stays correct as time passes.</p>

<p><strong>Performance</strong>: an index on <code>hire_date</code> supports range queries efficiently:</p>

<pre><code>CREATE INDEX idx_employees_hire_date ON employees(hire_date);

EXPLAIN SELECT * FROM employees
WHERE hire_date &gt;= CURDATE() - INTERVAL 6 MONTH;
-- Look for type=range and key=idx_employees_hire_date</code></pre>

<p><strong>Common pitfall</strong>: applying a function to the column prevents index use:</p>

<pre><code>-- ❌ Slow (function on the column)
WHERE YEAR(hire_date) = 2026 AND MONTH(hire_date) &gt;= MONTH(CURDATE()) - 6;

-- ✅ Fast (function on the constant)
WHERE hire_date &gt;= CURDATE() - INTERVAL 6 MONTH;</code></pre>

<p>Apply functions to the constants on the right side, never to the indexed column on the left side.</p>
'''

ANSWERS[43] = r'''
<pre><code>SELECT
  d.department_name,
  COUNT(e.id)             AS staff_count,
  COALESCE(SUM(e.salary), 0) AS total_salary
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY total_salary DESC;</code></pre>

<p>The <code>LEFT JOIN</code> ensures departments with zero employees still appear in the result (with a total of 0). <code>COALESCE</code> turns the <code>NULL</code> from <code>SUM</code> over zero rows into a clean 0.</p>

<p><strong>If the schema has department as a string on employees</strong> (no separate departments table):</p>

<pre><code>SELECT
  department,
  COUNT(*)               AS staff_count,
  COALESCE(SUM(salary), 0) AS total_salary,
  ROUND(AVG(salary), 2)  AS avg_salary,
  MIN(salary)            AS min_salary,
  MAX(salary)            AS max_salary
FROM employees
WHERE department IS NOT NULL
GROUP BY department
ORDER BY total_salary DESC;</code></pre>

<p><strong>Multiple aggregates in one pass</strong> are far more efficient than running separate queries.</p>

<p><strong>Add a percentage column</strong> &mdash; what fraction of total payroll each department represents:</p>

<pre><code>SELECT
  department,
  COUNT(*) AS staff_count,
  SUM(salary) AS total_salary,
  ROUND(SUM(salary) * 100.0 / SUM(SUM(salary)) OVER (), 2) AS pct_of_payroll
FROM employees
WHERE salary IS NOT NULL
GROUP BY department
ORDER BY total_salary DESC;</code></pre>

<p>The <code>SUM(SUM(...)) OVER ()</code> is a window function over the grouped result &mdash; the inner SUM aggregates per department; the outer SUM totals across all departments.</p>

<p><strong>Filter to active employees only</strong>:</p>

<pre><code>SELECT department, SUM(salary) AS total_salary
FROM employees
WHERE deleted_at IS NULL
  AND active = 1
GROUP BY department;</code></pre>

<p><strong>Performance</strong>: indexes on <code>(department, salary)</code> make this fast &mdash; the optimizer can read pre-sorted values:</p>

<pre><code>CREATE INDEX idx_emp_dept_salary ON employees(department, salary);</code></pre>

<p>For very large tables, consider a materialized summary table refreshed nightly &mdash; payroll totals rarely need real-time accuracy.</p>
'''

ANSWERS[44] = r'''
<pre><code>SELECT id, name, department
FROM employees
WHERE salary IS NULL;</code></pre>

<p>The <code>IS NULL</code> operator is the only correct way to test for NULL &mdash; <code>= NULL</code> always returns NULL itself, which is treated as false in WHERE.</p>

<p><strong>If "no salary" is represented by 0 or a sentinel</strong>:</p>

<pre><code>SELECT id, name FROM employees
WHERE salary IS NULL OR salary = 0;</code></pre>

<p><strong>Find them via a LEFT JOIN to the salaries table</strong> &mdash; in normalized schemas, salary lives in its own table:</p>

<pre><code>SELECT e.id, e.name
FROM employees e
LEFT JOIN salaries s ON s.employee_id = e.id
WHERE s.employee_id IS NULL;
-- Employees with no row in salaries.</code></pre>

<p><strong>Or with NOT EXISTS</strong> &mdash; semantically clearer for "doesn&rsquo;t have an X":</p>

<pre><code>SELECT id, name
FROM employees e
WHERE NOT EXISTS (
  SELECT 1 FROM salaries s WHERE s.employee_id = e.id
);</code></pre>

<p><strong>If salaries change over time</strong> and the question means "no <em>current</em> salary":</p>

<pre><code>-- Active salary record = effective_date &lt;= today and (no end_date or end_date in future)
SELECT e.id, e.name
FROM employees e
WHERE NOT EXISTS (
  SELECT 1 FROM salaries s
  WHERE s.employee_id = e.id
    AND s.effective_date &lt;= CURDATE()
    AND (s.end_date IS NULL OR s.end_date &gt; CURDATE())
);</code></pre>

<p><strong>Update them with a default</strong> &mdash; if you want to remediate:</p>

<pre><code>UPDATE employees
SET salary = 0
WHERE salary IS NULL;</code></pre>

<p>(But in practice you&rsquo;d want to know <em>why</em> they&rsquo;re missing a salary, not just hide the problem.)</p>

<p><strong>Performance</strong>: <code>IS NULL</code> can use an index on the column in modern MySQL. For very large tables where most rows have a salary, the index is highly selective and the lookup is fast.</p>
'''

ANSWERS[45] = r'''
<pre><code>UPDATE employees
SET department_id = 5
WHERE id = 42;</code></pre>

<p>Identify the employee by primary key, set the new department reference. If the schema uses a string column instead of FK:</p>

<pre><code>UPDATE employees
SET department = 'Engineering'
WHERE id = 42;</code></pre>

<p><strong>With audit trail</strong> &mdash; record the change for compliance:</p>

<pre><code>START TRANSACTION;

-- Capture the old value
INSERT INTO employee_dept_history (employee_id, old_dept_id, new_dept_id, changed_at, changed_by)
SELECT id, department_id, 5, NOW(), CURRENT_USER()
FROM employees WHERE id = 42;

-- Apply the change
UPDATE employees
SET department_id = 5,
    updated_at    = NOW()
WHERE id = 42;

COMMIT;</code></pre>

<p>Wrapping in a transaction ensures the audit insert and the update succeed together &mdash; or both roll back if anything fails.</p>

<p><strong>Lookup the new department by name</strong> &mdash; let the caller specify a department name and resolve it:</p>

<pre><code>UPDATE employees
SET department_id = (SELECT department_id FROM departments WHERE department_name = 'Engineering')
WHERE id = 42;</code></pre>

<p>This errors if no department matches; for safety:</p>

<pre><code>UPDATE employees e
JOIN departments d ON d.department_name = 'Engineering'
SET e.department_id = d.department_id
WHERE e.id = 42;</code></pre>

<p>The JOIN form does nothing if the target department doesn&rsquo;t exist, rather than setting <code>department_id</code> to NULL.</p>

<p><strong>Bulk reassignment</strong> &mdash; move all employees from one department to another (e.g., during a reorg):</p>

<pre><code>UPDATE employees
SET department_id = 8     -- new department
WHERE department_id = 5;  -- old department being absorbed</code></pre>

<p><strong>Foreign key check</strong>: if there&rsquo;s an FK constraint, the new <code>department_id</code> must exist in <code>departments</code> &mdash; otherwise MySQL refuses with a constraint violation. Make sure the target department exists first.</p>

<p><strong>From application code</strong>:</p>

<pre><code>await conn.execute(
  'UPDATE employees SET department_id = ? WHERE id = ?',
  [newDeptId, employeeId]
);</code></pre>
'''

ANSWERS[46] = r'''
<pre><code>SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department
ORDER BY employee_count DESC;</code></pre>

<p><code>GROUP BY</code> collapses rows that share the same <code>department</code> value into a single row; <code>COUNT(*)</code> returns the size of each group.</p>

<p><strong>If the schema is normalized</strong> (departments table + FK):</p>

<pre><code>SELECT
  d.department_name,
  COUNT(e.id) AS employee_count
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY employee_count DESC, d.department_name;</code></pre>

<p>The <code>LEFT JOIN</code> includes departments with zero employees (their count is 0). An <code>INNER JOIN</code> would exclude empty departments.</p>

<p><strong>Filter out departments with too few people</strong> &mdash; <code>HAVING</code> applies after the GROUP BY:</p>

<pre><code>SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) &gt;= 5
ORDER BY employee_count DESC;</code></pre>

<p><strong>Multiple aggregates per group</strong>:</p>

<pre><code>SELECT
  department,
  COUNT(*)                 AS employee_count,
  ROUND(AVG(age), 1)       AS avg_age,
  ROUND(AVG(salary), 2)    AS avg_salary,
  MIN(age)                 AS youngest,
  MAX(age)                 AS oldest
FROM employees
WHERE department IS NOT NULL
GROUP BY department
ORDER BY employee_count DESC;</code></pre>

<p><strong>With percentage of total</strong>:</p>

<pre><code>SELECT
  department,
  COUNT(*) AS employee_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
FROM employees
WHERE department IS NOT NULL
GROUP BY department
ORDER BY employee_count DESC;</code></pre>

<p>The window function <code>SUM(COUNT(*)) OVER ()</code> totals all departments&rsquo; counts; the row&rsquo;s count divided by that gives a percentage.</p>

<p><strong>Performance</strong>: an index on <code>department</code> dramatically speeds up the GROUP BY:</p>

<pre><code>CREATE INDEX idx_emp_department ON employees(department);

EXPLAIN SELECT department, COUNT(*) FROM employees GROUP BY department;
-- Look for &quot;Using index&quot; in the Extra column</code></pre>
'''

ANSWERS[47] = r'''
<pre><code>SELECT
  department,
  COUNT(*)                                                         AS employee_count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM employees), 2)    AS percentage
FROM employees
WHERE department IS NOT NULL
GROUP BY department
ORDER BY percentage DESC;</code></pre>

<p>The subquery <code>(SELECT COUNT(*) FROM employees)</code> runs once and is reused for every group. Multiplying by 100.0 (not 100) ensures floating-point division &mdash; <code>5 / 30 = 0</code> in integer math, but <code>5 * 100.0 / 30 = 16.67</code>.</p>

<p><strong>With a window function</strong> &mdash; cleaner and avoids the subquery:</p>

<pre><code>SELECT
  department,
  COUNT(*) AS employee_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM employees
WHERE department IS NOT NULL
GROUP BY department
ORDER BY percentage DESC;</code></pre>

<p><code>SUM(COUNT(*)) OVER ()</code> is a "grand total" computed across all groups in a single pass. This pattern requires MySQL 8+.</p>

<p><strong>Including departments with zero employees</strong> &mdash; LEFT JOIN to the departments table:</p>

<pre><code>SELECT
  d.department_name,
  COUNT(e.id) AS employee_count,
  ROUND(COUNT(e.id) * 100.0 / SUM(COUNT(e.id)) OVER (), 2) AS percentage
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY percentage DESC;</code></pre>

<p><strong>Add a cumulative percentage</strong> &mdash; useful for Pareto / 80/20 analysis:</p>

<pre><code>SELECT
  department,
  COUNT(*) AS employee_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct,
  ROUND(SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS cumulative_pct
FROM employees
WHERE department IS NOT NULL
GROUP BY department
ORDER BY employee_count DESC;</code></pre>

<p>The cumulative running total shows what percentage of all employees the top N departments represent.</p>

<p><strong>Format for display</strong> &mdash; concatenate with a percent sign:</p>

<pre><code>SELECT department,
       CONCAT(ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1), '%') AS pct
FROM employees
WHERE department IS NOT NULL
GROUP BY department;</code></pre>
'''

ANSWERS[48] = r'''
<pre><code>SELECT d.department_id, d.department_name
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id
WHERE e.id IS NULL;</code></pre>

<p>The <code>LEFT JOIN</code> + <code>IS NULL</code> pattern is the canonical "find rows in A with no match in B" approach. For each department, the LEFT JOIN attempts to find matching employees; non-matching departments get NULLs in the right-side columns. Filtering for <code>e.id IS NULL</code> keeps only the unmatched ones.</p>

<p><strong>With NOT EXISTS</strong> &mdash; semantically clearer; often the same performance:</p>

<pre><code>SELECT d.department_id, d.department_name
FROM departments d
WHERE NOT EXISTS (
  SELECT 1 FROM employees e
  WHERE e.department_id = d.department_id
);</code></pre>

<p><strong>With NOT IN</strong> &mdash; works but watch the NULL trap:</p>

<pre><code>-- ❌ Bad: returns nothing if any employee has NULL department_id
SELECT * FROM departments
WHERE department_id NOT IN (
  SELECT department_id FROM employees
);

-- ✅ Filter NULLs explicitly
SELECT * FROM departments
WHERE department_id NOT IN (
  SELECT department_id FROM employees WHERE department_id IS NOT NULL
);</code></pre>

<p>The <code>NOT IN</code> form fails when the inner query returns any NULL because <code>x NOT IN (1, 2, NULL)</code> evaluates to NULL, not TRUE &mdash; so no rows pass the filter. <code>NOT EXISTS</code> doesn&rsquo;t have this issue.</p>

<p><strong>Including the count column</strong> &mdash; departments by employee count, including zeros:</p>

<pre><code>SELECT
  d.department_name,
  COUNT(e.id) AS employee_count
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(e.id) = 0;</code></pre>

<p><strong>Performance comparison</strong>:</p>

<table>
  <tr><th>Pattern</th><th>Best for</th></tr>
  <tr><td><code>LEFT JOIN ... IS NULL</code></td><td>Standard, predictable performance</td></tr>
  <tr><td><code>NOT EXISTS</code></td><td>Equally fast in modern MySQL; clearest intent</td></tr>
  <tr><td><code>NOT IN</code></td><td>Works but has the NULL pitfall; can be slower</td></tr>
</table>

<p>The MySQL optimizer often translates these into the same execution plan, but <code>NOT EXISTS</code> is the most defensible choice in code review.</p>
'''

ANSWERS[49] = r'''
<pre><code>-- Approach 1: Define at table creation
CREATE TABLE employees (
  id         INT,
  department VARCHAR(50),
  name       VARCHAR(100) NOT NULL,
  age        INT,
  PRIMARY KEY (id, department)
);

-- Approach 2: Add to existing table (if no PK exists)
ALTER TABLE employees
ADD PRIMARY KEY (id, department);</code></pre>

<p>A composite primary key&rsquo;s columns must <em>all</em> be NOT NULL (MySQL adds the constraint silently if not declared). The combination is unique &mdash; an employee with id=1 in department='HR' can coexist with id=1 in department='Engineering', but not two id=1 in department='HR'.</p>

<p><strong>Replace an existing primary key</strong>:</p>

<pre><code>-- 1. Drop the existing PK
ALTER TABLE employees DROP PRIMARY KEY;

-- 2. Add the composite PK
ALTER TABLE employees ADD PRIMARY KEY (id, department);</code></pre>

<p>If foreign keys reference the old PK, drop them first or the change fails.</p>

<p><strong>Caveats with this design</strong> &mdash; using <code>(id, department)</code> as the PK is unusual and questionable:</p>

<ul>
  <li><strong>Surrogate <code>id</code> alone</strong> is typically the better PK &mdash; stable, narrow, easy to reference from foreign keys.</li>
  <li><strong>Composite PKs</strong> shine when the natural identifier genuinely requires multiple columns &mdash; e.g., a junction table for many-to-many relationships:
<pre><code>CREATE TABLE order_items (
  order_id   INT,
  product_id INT,
  quantity   INT,
  PRIMARY KEY (order_id, product_id)
);</code></pre>
  </li>
  <li><strong>If the goal is "an employee can be in multiple departments"</strong>, the right model is a junction table, not changing the PK:
<pre><code>CREATE TABLE employee_departments (
  employee_id   INT NOT NULL,
  department_id INT NOT NULL,
  PRIMARY KEY (employee_id, department_id),
  FOREIGN KEY (employee_id)   REFERENCES employees(id),
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
);</code></pre>
  </li>
</ul>

<p><strong>Composite UNIQUE alternative</strong> &mdash; if you want to enforce that combinations are unique without using them as the PK:</p>

<pre><code>ALTER TABLE employees
ADD CONSTRAINT uk_employee_dept UNIQUE (id, department);</code></pre>

<p>Keep the simple <code>id</code> as the PK; add a UNIQUE constraint for the business rule. Easier to evolve.</p>

<p><strong>Index implications</strong>: in InnoDB, the PK is also the clustered index &mdash; physical row order follows it. Composite PKs make secondary indexes larger (they include the entire PK in each entry).</p>
'''

ANSWERS[50] = r'''
<pre><code>-- Assumes a salaries history table:
-- salaries (employee_id, salary, effective_date, end_date)
SELECT DISTINCT e.id, e.name
FROM employees e
JOIN salaries s_old ON s_old.employee_id = e.id
JOIN salaries s_new ON s_new.employee_id = e.id
WHERE s_new.effective_date &gt; s_old.effective_date
  AND s_new.salary       &gt; s_old.salary
  AND s_new.effective_date &gt;= CURDATE() - INTERVAL 1 YEAR;</code></pre>

<p>Self-join the salaries table to compare two records for the same employee &mdash; the older one (<code>s_old</code>) and the newer one (<code>s_new</code>). The conditions ensure: the second record is more recent, the salary is higher, and the increase happened within the past year.</p>

<p><strong>With window functions</strong> &mdash; cleaner for "previous salary":</p>

<pre><code>WITH salary_changes AS (
  SELECT
    employee_id,
    salary,
    effective_date,
    LAG(salary)         OVER (PARTITION BY employee_id ORDER BY effective_date) AS prev_salary,
    LAG(effective_date) OVER (PARTITION BY employee_id ORDER BY effective_date) AS prev_date
  FROM salaries
)
SELECT DISTINCT e.id, e.name,
       sc.salary - sc.prev_salary AS increase_amount,
       sc.effective_date          AS raise_date
FROM salary_changes sc
JOIN employees e ON e.id = sc.employee_id
WHERE sc.prev_salary IS NOT NULL
  AND sc.salary &gt; sc.prev_salary
  AND sc.effective_date &gt;= CURDATE() - INTERVAL 1 YEAR
ORDER BY raise_date DESC;</code></pre>

<p><code>LAG()</code> retrieves the previous row&rsquo;s value within the partition. The CTE produces one row per salary record with both current and prior values; the outer query filters for actual increases.</p>

<p><strong>Just the most recent raise per employee</strong>:</p>

<pre><code>SELECT e.id, e.name, latest_raise.raise_date, latest_raise.increase
FROM employees e
JOIN (
  SELECT
    employee_id,
    MAX(effective_date) AS raise_date,
    salary - LAG(salary) OVER (PARTITION BY employee_id ORDER BY effective_date) AS increase
  FROM salaries
  WHERE effective_date &gt;= CURDATE() - INTERVAL 1 YEAR
  GROUP BY employee_id
  HAVING increase &gt; 0
) latest_raise ON latest_raise.employee_id = e.id;</code></pre>

<p><strong>If the schema only has current salary</strong> (no history):</p>

<pre><code>-- Need the salary at some prior point — typically tracked in an audit table
SELECT e.id, e.name, e.salary AS current_salary, a.salary AS prior_salary
FROM employees e
JOIN employees_audit a ON a.employee_id = e.id
WHERE a.changed_at &gt;= CURDATE() - INTERVAL 1 YEAR
  AND a.column_name = 'salary'
  AND e.salary &gt; a.salary;</code></pre>

<p>Without history tracking, "raises" can&rsquo;t be detected from current state alone &mdash; your schema needs to record changes (audit trail or temporal tables) for this kind of query to work.</p>

<p><strong>Performance</strong>: index <code>salaries(employee_id, effective_date)</code> for the self-join and window function partitioning.</p>
'''

ANSWERS[51] = r'''
<pre><code>CREATE TABLE salaries (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  employee_id     INT NOT NULL,
  salary          DECIMAL(10, 2) NOT NULL,
  effective_date  DATE NOT NULL,
  end_date        DATE NULL,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_salaries_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id)
    ON DELETE CASCADE,

  INDEX idx_salaries_emp_date (employee_id, effective_date)
) ENGINE=InnoDB;</code></pre>

<p>Models a salary <em>history</em> &mdash; each row is one salary period for one employee. <code>effective_date</code> is when the salary started; <code>end_date</code> is when it stopped (NULL for the current salary).</p>

<p><strong>Type choices</strong>:</p>
<ul>
  <li><code>DECIMAL(10, 2)</code> &mdash; exact arithmetic for money. Never use <code>FLOAT</code> or <code>DOUBLE</code> for currency &mdash; binary floating-point introduces rounding errors.</li>
  <li><code>DATE</code> &mdash; date only, no time component. Use <code>DATETIME</code> if you need timestamps.</li>
  <li>The composite index <code>(employee_id, effective_date)</code> makes salary-history queries fast.</li>
</ul>

<p><strong>Add an upper salary bound check</strong> (MySQL 8.0.16+):</p>

<pre><code>ALTER TABLE salaries
ADD CONSTRAINT chk_salary_positive
CHECK (salary &gt; 0);</code></pre>

<p><strong>Variant with no end_date</strong> &mdash; some designs derive the period from the next row&rsquo;s <code>effective_date</code>:</p>

<pre><code>-- Only effective_date stored; current salary is the most recent row
CREATE TABLE salaries (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  employee_id  INT NOT NULL,
  salary       DECIMAL(10, 2) NOT NULL,
  effective_date DATE NOT NULL,
  UNIQUE KEY uk_emp_date (employee_id, effective_date)
);</code></pre>

<p>Simpler to write to (just INSERT new rows), but queries that need "salary as of date X" require a window function or correlated subquery.</p>

<p>For audit/compliance use cases, prefer the explicit <code>end_date</code> form &mdash; queries are simpler and the data is self-describing.</p>
'''

ANSWERS[52] = r'''
<pre><code>INSERT INTO salaries (employee_id, salary, effective_date)
VALUES (101, 75000.00, '2026-04-01');</code></pre>

<p>For a brand-new salary record, just supply the three required columns. Auto-increment handles <code>id</code>; <code>end_date</code> defaults to <code>NULL</code> (current); <code>created_at</code> defaults to now.</p>

<p><strong>Realistic pattern: closing the previous record and opening a new one</strong>. When an employee gets a raise, the existing salary row should get an <code>end_date</code> and a new row should be inserted &mdash; in one transaction:</p>

<pre><code>START TRANSACTION;

-- Close out the prior open salary
UPDATE salaries
SET end_date = '2026-03-31'
WHERE employee_id = 101 AND end_date IS NULL;

-- Insert the new one
INSERT INTO salaries (employee_id, salary, effective_date)
VALUES (101, 80000.00, '2026-04-01');

COMMIT;</code></pre>

<p>Both happen atomically &mdash; no chance of having two open salary rows or zero rows mid-update.</p>

<p><strong>Bulk insert</strong> &mdash; one INSERT statement is far faster than many for large initial loads:</p>

<pre><code>INSERT INTO salaries (employee_id, salary, effective_date) VALUES
  (101, 75000.00, '2026-04-01'),
  (102, 68000.00, '2026-04-01'),
  (103, 92000.00, '2026-04-01'),
  (104, 55000.00, '2026-04-01');</code></pre>

<p><strong>From application code</strong> use parameterized queries:</p>

<pre><code>// Node.js with mysql2/promise
await conn.execute(
  'INSERT INTO salaries (employee_id, salary, effective_date) VALUES (?, ?, ?)',
  [employeeId, salary, effectiveDate]
);</code></pre>

<p>Never build SQL by string concatenation &mdash; SQL injection. The <code>?</code> placeholders escape values correctly.</p>

<p><strong>Get the new ID</strong>:</p>

<pre><code>SELECT LAST_INSERT_ID();
-- Or, in mysql2: result.insertId
</code></pre>
'''

ANSWERS[53] = r'''
<pre><code>UPDATE salaries
SET salary = 82000.00
WHERE employee_id = 101 AND end_date IS NULL;</code></pre>

<p>This updates the employee&rsquo;s <em>current</em> salary record (the one with <code>end_date IS NULL</code>). Updating in place is appropriate when correcting a typo or applying a backdated change &mdash; not when recording a new salary period.</p>

<p><strong>For a real raise, prefer an audit-friendly approach</strong>: close the existing row, insert a new one (see Q52). Updating the existing row destroys history.</p>

<p><strong>Update by record ID</strong> &mdash; safer when the row is uniquely identified:</p>

<pre><code>UPDATE salaries
SET salary = 82000.00
WHERE id = 5567;</code></pre>

<p><strong>Conditional update with bounds check</strong>:</p>

<pre><code>UPDATE salaries
SET salary = salary * 1.05      -- 5% raise
WHERE employee_id = 101
  AND end_date IS NULL
  AND salary &lt; 100000;          -- only if currently under 100K</code></pre>

<p>The <code>WHERE</code> clause acts as a guard &mdash; if no rows match, nothing changes (no error).</p>

<p><strong>Update with a join</strong> &mdash; raise everyone in a department by 10%:</p>

<pre><code>UPDATE salaries s
JOIN employees e ON e.id = s.employee_id
SET s.salary = s.salary * 1.10
WHERE e.department_id = 5
  AND s.end_date IS NULL;</code></pre>

<p><strong>Safety in production</strong>:</p>
<ul>
  <li>Always test with a <code>SELECT</code> first using the same <code>WHERE</code> &mdash; verify which rows will change.</li>
  <li>Run inside a transaction so you can <code>ROLLBACK</code> if the result is wrong:
<pre><code>START TRANSACTION;
UPDATE salaries SET salary = ... WHERE ...;
SELECT * FROM salaries WHERE ...;   -- verify
-- If correct: COMMIT;  If not: ROLLBACK;</code></pre>
  </li>
  <li>Some teams enable <code>sql_safe_updates</code> to refuse UPDATE without a key or LIMIT.</li>
</ul>
'''

ANSWERS[54] = r'''
<pre><code>SELECT
  s.salary,
  s.effective_date,
  COALESCE(s.end_date, 'current') AS end_date,
  DATEDIFF(COALESCE(s.end_date, CURDATE()), s.effective_date) AS days_at_salary
FROM salaries s
WHERE s.employee_id = 101
ORDER BY s.effective_date DESC;</code></pre>

<p>Returns one row per salary period for the employee, ordered most recent first. <code>COALESCE(end_date, CURDATE())</code> treats the open-ended current row as ending today for duration calculations.</p>

<p><strong>With employee details</strong>:</p>

<pre><code>SELECT
  e.name,
  s.salary,
  s.effective_date,
  s.end_date,
  s.salary - LAG(s.salary) OVER w AS change_amount
FROM salaries s
JOIN employees e ON e.id = s.employee_id
WHERE s.employee_id = 101
WINDOW w AS (ORDER BY s.effective_date)
ORDER BY s.effective_date DESC;</code></pre>

<p><code>LAG()</code> shows the change from the previous record &mdash; useful for displaying raise/cut amounts.</p>

<p><strong>For all employees, latest salary only</strong>:</p>

<pre><code>SELECT e.id, e.name, s.salary, s.effective_date
FROM employees e
JOIN salaries s ON s.employee_id = e.id
WHERE s.end_date IS NULL
ORDER BY e.name;</code></pre>

<p><strong>Salary at a specific historical date</strong>:</p>

<pre><code>SELECT salary
FROM salaries
WHERE employee_id = 101
  AND effective_date &lt;= '2024-01-01'
  AND (end_date &gt; '2024-01-01' OR end_date IS NULL)
LIMIT 1;</code></pre>

<p>The condition picks the salary period that contains the target date &mdash; <code>started before</code> AND <code>ended after (or still open)</code>.</p>

<p><strong>Visualize the trajectory</strong> &mdash; minimal version useful for chart data:</p>

<pre><code>SELECT effective_date AS x, salary AS y
FROM salaries
WHERE employee_id = 101
ORDER BY effective_date;</code></pre>

<p><strong>Performance</strong>: the index <code>salaries(employee_id, effective_date)</code> makes both single-employee history queries and as-of-date lookups fast.</p>
'''

ANSWERS[55] = r'''
<pre><code>SELECT id, name, salary
FROM employees
WHERE salary &gt; (SELECT AVG(salary) FROM employees);</code></pre>

<p>The subquery computes the global average; the outer query keeps rows where the salary exceeds it. The subquery runs once because it doesn&rsquo;t reference the outer query.</p>

<p><strong>Show how much each is over the average</strong>:</p>

<pre><code>WITH avg_data AS (
  SELECT AVG(salary) AS avg_salary FROM employees
)
SELECT
  e.id,
  e.name,
  e.salary,
  ROUND(e.salary - a.avg_salary, 2) AS amount_above_avg,
  ROUND((e.salary - a.avg_salary) / a.avg_salary * 100, 1) AS percent_above
FROM employees e
CROSS JOIN avg_data a
WHERE e.salary &gt; a.avg_salary
ORDER BY e.salary DESC;</code></pre>

<p>The CTE makes the average available everywhere without recomputing.</p>

<p><strong>Above the department average</strong> &mdash; uses a correlated subquery or window function:</p>

<pre><code>-- Window function approach (preferred in MySQL 8+)
SELECT id, name, department_id, salary, dept_avg
FROM (
  SELECT
    id, name, department_id, salary,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg
  FROM employees
) ranked
WHERE salary &gt; dept_avg
ORDER BY department_id, salary DESC;</code></pre>

<p><code>AVG() OVER (PARTITION BY department_id)</code> computes a separate average for each department, and adds it as a column on every row in that department.</p>

<p><strong>Top earners as percentile</strong>:</p>

<pre><code>SELECT id, name, salary
FROM (
  SELECT
    id, name, salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS pct_rank
  FROM employees
) ranked
WHERE pct_rank &gt;= 0.90       -- top 10%
ORDER BY salary DESC;</code></pre>

<p><strong>If salaries are stored in a separate history table</strong>, join to it first:</p>

<pre><code>SELECT e.id, e.name, s.salary
FROM employees e
JOIN salaries s ON s.employee_id = e.id AND s.end_date IS NULL
WHERE s.salary &gt; (SELECT AVG(salary) FROM salaries WHERE end_date IS NULL);</code></pre>

<p>Always filter the history table to current rows before averaging.</p>
'''

ANSWERS[56] = r'''
<pre><code>ALTER TABLE employees
ADD CONSTRAINT uk_employees_email UNIQUE (email);</code></pre>

<p>Adds a unique constraint with an explicit name. MySQL automatically creates a unique index to enforce it &mdash; no separate <code>CREATE INDEX</code> needed.</p>

<p><strong>Define when creating the table</strong>:</p>

<pre><code>CREATE TABLE employees (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  email  VARCHAR(255) NOT NULL UNIQUE,
  name   VARCHAR(100) NOT NULL
);

-- Or with an explicit constraint name:
CREATE TABLE employees (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  email  VARCHAR(255) NOT NULL,
  name   VARCHAR(100) NOT NULL,
  CONSTRAINT uk_employees_email UNIQUE (email)
);</code></pre>

<p><strong>If duplicates already exist</strong>, the ALTER fails. Find them first:</p>

<pre><code>SELECT email, COUNT(*) AS cnt
FROM employees
GROUP BY email
HAVING cnt &gt; 1;

-- Resolve before adding the constraint:
-- - merge the duplicate user records, or
-- - update one of them with a new email, or
-- - delete one if it&rsquo;s a true duplicate</code></pre>

<p><strong>Composite unique constraint</strong> &mdash; uniqueness on the combination, not on each column:</p>

<pre><code>ALTER TABLE employees
ADD CONSTRAINT uk_employees_email_company
UNIQUE (email, company_id);
-- Same email allowed in different companies, but unique within one</code></pre>

<p><strong>NULL handling</strong>: in MySQL, <code>UNIQUE</code> allows multiple <code>NULL</code> values &mdash; so <code>email VARCHAR(255) UNIQUE</code> permits any number of rows with NULL email. Combine with <code>NOT NULL</code> for true uniqueness:</p>

<pre><code>ALTER TABLE employees
MODIFY COLUMN email VARCHAR(255) NOT NULL,
ADD CONSTRAINT uk_employees_email UNIQUE (email);</code></pre>

<p><strong>Drop the constraint if needed</strong>:</p>

<pre><code>ALTER TABLE employees
DROP INDEX uk_employees_email;
-- (UNIQUE constraints are stored as indexes; drop by name)</code></pre>

<p><strong>Case sensitivity</strong>: with the default <code>utf8mb4_0900_ai_ci</code> collation, <code>Alice@x.com</code> and <code>alice@x.com</code> are considered duplicates. Use a <code>_bin</code> collation if you need case-sensitive uniqueness.</p>
'''

ANSWERS[57] = r'''
<pre><code>SELECT salary, GROUP_CONCAT(name ORDER BY name) AS employees, COUNT(*) AS shared_by
FROM employees
GROUP BY salary
HAVING COUNT(*) &gt; 1
ORDER BY salary DESC;</code></pre>

<p>Groups employees by salary, keeps only groups with more than one member. <code>GROUP_CONCAT</code> produces a comma-separated list of the names.</p>

<p>Sample output:</p>

<pre><code>+--------+-----------------------+-----------+
| salary | employees             | shared_by |
+--------+-----------------------+-----------+
| 75000  | Alice, Bob, Carol     |   3       |
| 60000  | Dave, Eve             |   2       |
+--------+-----------------------+-----------+</code></pre>

<p><strong>Just the rows, no grouping</strong> &mdash; use a subquery to find the shared salary values, then re-query for full rows:</p>

<pre><code>SELECT id, name, salary
FROM employees
WHERE salary IN (
  SELECT salary
  FROM employees
  GROUP BY salary
  HAVING COUNT(*) &gt; 1
)
ORDER BY salary DESC, name;</code></pre>

<p>Lets you see all per-employee details (full row), not just the group.</p>

<p><strong>With a self-join</strong> &mdash; pair employees with their salary peers:</p>

<pre><code>SELECT
  e1.id   AS id_1,    e1.name AS name_1,
  e2.id   AS id_2,    e2.name AS name_2,
  e1.salary
FROM employees e1
JOIN employees e2
  ON e1.salary = e2.salary
 AND e1.id &lt; e2.id;          -- avoid duplicate (A,B)/(B,A) pairs</code></pre>

<p>The <code>e1.id &lt; e2.id</code> trick keeps each pair only once. Useful when displaying "who else makes this salary."</p>

<p><strong>Most common salary value</strong> &mdash; the modal salary:</p>

<pre><code>SELECT salary, COUNT(*) AS frequency
FROM employees
GROUP BY salary
ORDER BY frequency DESC, salary DESC
LIMIT 1;</code></pre>

<p><strong>Performance note</strong>: an index on <code>salary</code> makes the GROUP BY fast. For very large tables, the GROUP BY may use a temp table &mdash; check with <code>EXPLAIN</code>.</p>
'''

ANSWERS[58] = r'''
<pre><code>SELECT id, name, hire_date,
       TIMESTAMPDIFF(YEAR, hire_date, CURDATE()) AS years_with_company
FROM employees
WHERE hire_date &lt;= CURDATE() - INTERVAL 5 YEAR
ORDER BY hire_date;</code></pre>

<p><code>TIMESTAMPDIFF(YEAR, ...)</code> counts complete years between two dates. The <code>WHERE</code> clause filters to anyone hired at least 5 years ago today.</p>

<p><strong>Why <code>TIMESTAMPDIFF</code> over <code>DATEDIFF / 365</code></strong>: <code>DATEDIFF</code> returns days; dividing by 365 introduces leap-year errors. <code>TIMESTAMPDIFF(YEAR, ...)</code> handles them correctly.</p>

<pre><code>-- ❌ Slightly inaccurate (no leap-year handling)
SELECT name, DATEDIFF(CURDATE(), hire_date) / 365 AS years FROM employees;

-- ✅ Accurate to the calendar
SELECT name, TIMESTAMPDIFF(YEAR, hire_date, CURDATE()) AS years FROM employees;</code></pre>

<p><strong>With detailed tenure breakdown</strong>:</p>

<pre><code>SELECT
  id, name, hire_date,
  TIMESTAMPDIFF(YEAR,  hire_date, CURDATE()) AS years,
  TIMESTAMPDIFF(MONTH, hire_date, CURDATE()) % 12 AS months,
  TIMESTAMPDIFF(DAY,   hire_date, CURDATE()) AS total_days
FROM employees
WHERE TIMESTAMPDIFF(YEAR, hire_date, CURDATE()) &gt;= 5;</code></pre>

<p>The output shows tenure as "5 years 7 months" style.</p>

<p><strong>Tenure tiers</strong> &mdash; categorize all employees:</p>

<pre><code>SELECT
  CASE
    WHEN TIMESTAMPDIFF(YEAR, hire_date, CURDATE()) &lt; 1 THEN 'Less than 1 year'
    WHEN TIMESTAMPDIFF(YEAR, hire_date, CURDATE()) &lt; 5 THEN '1-4 years'
    WHEN TIMESTAMPDIFF(YEAR, hire_date, CURDATE()) &lt; 10 THEN '5-9 years'
    ELSE '10+ years'
  END AS tenure_band,
  COUNT(*) AS employee_count
FROM employees
GROUP BY tenure_band
ORDER BY MIN(hire_date);</code></pre>

<p><strong>Performance</strong>: the predicate <code>hire_date &lt;= CURDATE() - INTERVAL 5 YEAR</code> can use an index on <code>hire_date</code>. Avoid wrapping the indexed column in functions (<code>YEAR(hire_date)</code> would defeat the index); always operate on the constant side instead.</p>

<p><strong>Departed employees</strong>: if there&rsquo;s a <code>termination_date</code>, exclude them: <code>AND termination_date IS NULL</code>.</p>
'''

ANSWERS[59] = r'''
<pre><code>SELECT id, name, hire_date,
       DATEDIFF(CURDATE(), hire_date) AS days_employed
FROM employees
ORDER BY days_employed DESC;</code></pre>

<p><code>DATEDIFF(end, start)</code> returns the integer number of days between two dates. Argument order matters: it&rsquo;s <em>end minus start</em>.</p>

<p><strong>For more granular intervals</strong>, use <code>TIMESTAMPDIFF</code> with the desired unit:</p>

<pre><code>SELECT
  name,
  TIMESTAMPDIFF(DAY,    hire_date, CURDATE()) AS days,
  TIMESTAMPDIFF(WEEK,   hire_date, CURDATE()) AS weeks,
  TIMESTAMPDIFF(MONTH,  hire_date, CURDATE()) AS months,
  TIMESTAMPDIFF(YEAR,   hire_date, CURDATE()) AS years
FROM employees;</code></pre>

<p>Each unit returns the number of complete units between the dates.</p>

<p><strong>For a precise duration including hours/minutes</strong> &mdash; if columns are <code>DATETIME</code>:</p>

<pre><code>SELECT
  name,
  TIMESTAMPDIFF(SECOND, last_login, NOW()) AS seconds_since_login,
  SEC_TO_TIME(TIMESTAMPDIFF(SECOND, last_login, NOW())) AS time_since_login
FROM employees;
-- e.g., 3700 seconds → '01:01:40'</code></pre>

<p><strong>Days until a future date</strong> &mdash; useful for "days until contract expires":</p>

<pre><code>SELECT
  name,
  contract_end,
  DATEDIFF(contract_end, CURDATE()) AS days_remaining
FROM employees
WHERE contract_end IS NOT NULL
ORDER BY days_remaining;
-- Negative numbers indicate already-expired contracts</code></pre>

<p><strong>Date arithmetic</strong> &mdash; an alternative way to express the same logic:</p>

<pre><code>SELECT name, hire_date
FROM employees
WHERE CURDATE() - INTERVAL 30 DAY &gt; hire_date;     -- hired more than 30 days ago

-- Adding intervals
SELECT
  hire_date,
  DATE_ADD(hire_date, INTERVAL 6 MONTH) AS probation_ends,
  DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AS one_year_ago
FROM employees;</code></pre>

<p><strong>Time zone</strong>: <code>CURDATE()</code> returns the server&rsquo;s current date. If your application stores dates in UTC and the server runs in a different zone, use <code>UTC_DATE()</code> or set <code>SET time_zone = '+00:00'</code> at the connection level.</p>
'''

ANSWERS[60] = r'''
<pre><code>SELECT id, name, hire_date
FROM employees
WHERE YEAR(hire_date) = 2023;</code></pre>

<p>Simple but problematic in production: wrapping the indexed <code>hire_date</code> column in <code>YEAR()</code> prevents MySQL from using an index on it &mdash; the query scans every row.</p>

<p><strong>Index-friendly version</strong>:</p>

<pre><code>SELECT id, name, hire_date
FROM employees
WHERE hire_date &gt;= '2023-01-01'
  AND hire_date &lt;  '2024-01-01';</code></pre>

<p>The bounds are constants; MySQL can use a B-tree range scan on the <code>hire_date</code> index. This is roughly 10-100x faster on large tables.</p>

<p><strong>Equivalent with BETWEEN</strong> &mdash; clearer for some readers but inclusive on both ends, which is fine for whole-day boundaries:</p>

<pre><code>SELECT id, name, hire_date
FROM employees
WHERE hire_date BETWEEN '2023-01-01' AND '2023-12-31';</code></pre>

<p><strong>Caveat</strong>: <code>BETWEEN</code> with a <code>DATETIME</code> column is wrong if you want the whole year &mdash; <code>'2023-12-31'</code> is interpreted as <code>'2023-12-31 00:00:00'</code>, missing rows from later that day. Stick with the half-open <code>&gt;=</code> / <code>&lt;</code> form for datetimes.</p>

<p><strong>Multiple years</strong>:</p>

<pre><code>SELECT id, name, hire_date
FROM employees
WHERE hire_date &gt;= '2020-01-01'
  AND hire_date &lt;  '2023-01-01';      -- 2020, 2021, 2022 hires</code></pre>

<p><strong>Group by hire year</strong>:</p>

<pre><code>SELECT YEAR(hire_date) AS hire_year, COUNT(*) AS hires
FROM employees
GROUP BY YEAR(hire_date)
ORDER BY hire_year;</code></pre>

<p>Wrapping in <code>YEAR()</code> is fine in <code>SELECT</code> and <code>GROUP BY</code> &mdash; it&rsquo;s the <code>WHERE</code> clause where it kills index usage.</p>

<p><strong>Pass year as a parameter</strong> from app code:</p>

<pre><code>SELECT id, name, hire_date
FROM employees
WHERE hire_date &gt;= CONCAT(?, '-01-01')
  AND hire_date &lt;  CONCAT(? + 1, '-01-01');</code></pre>

<p>Or compute the date range in the app and pass complete date strings.</p>
'''

ANSWERS[61] = r'''
<pre><code>CREATE TEMPORARY TABLE temp_employees (
  id          INT,
  name        VARCHAR(100),
  age         INT,
  department  VARCHAR(50)
);</code></pre>

<p>Temporary tables exist only for the lifetime of the connection that created them and are visible only to that session. They&rsquo;re automatically dropped when the connection closes.</p>

<p><strong>Create and populate from a query</strong> &mdash; one of the most common patterns:</p>

<pre><code>CREATE TEMPORARY TABLE temp_employees AS
SELECT id, name, age, department
FROM employees
WHERE department = 'Engineering';</code></pre>

<p>The new table inherits column types from the SELECT, but loses the original primary key and indexes &mdash; add them if you need them.</p>

<pre><code>CREATE TEMPORARY TABLE temp_employees (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  age INT,
  department VARCHAR(50),
  INDEX idx_dept (department)
)
SELECT id, name, age, department
FROM employees
WHERE department = 'Engineering';</code></pre>

<p><strong>Use cases</strong>:</p>
<ul>
  <li><strong>Multi-step computations</strong>: stage intermediate results that multiple queries need.</li>
  <li><strong>Avoiding repeated subqueries</strong>: compute once, reuse.</li>
  <li><strong>Complex reporting</strong>: build up a result set in steps that&rsquo;s clearer than one massive SQL.</li>
  <li><strong>Workarounds</strong> for cases where MySQL would otherwise re-evaluate a subquery many times.</li>
</ul>

<p><strong>Modern alternative: CTEs</strong> (Common Table Expressions, MySQL 8+) often replace the need for temp tables for one-shot queries:</p>

<pre><code>WITH eng AS (
  SELECT id, name, age FROM employees WHERE department = 'Engineering'
)
SELECT * FROM eng WHERE age &gt; 30;
-- No temp table needed; the CTE exists only for this query.</code></pre>

<p>Use temp tables when you need to <em>persist</em> intermediate results across multiple statements; use CTEs for clarity within a single query.</p>

<p><strong>Drop explicitly</strong> &mdash; usually unnecessary, but you can:</p>

<pre><code>DROP TEMPORARY TABLE IF EXISTS temp_employees;</code></pre>

<p>The <code>TEMPORARY</code> keyword in DROP prevents accidentally dropping a same-named permanent table.</p>
'''

ANSWERS[62] = r'''
<pre><code>INSERT INTO temp_employees (id, name, age, department) VALUES
  (1, 'Alice',   28, 'Engineering'),
  (2, 'Bob',     35, 'Sales'),
  (3, 'Carol',   42, 'Engineering'),
  (4, 'Dave',    19, 'Marketing'),
  (5, 'Eve',     31, 'Engineering');</code></pre>

<p>Multi-row INSERT is the same syntax as for a regular table &mdash; the <code>TEMPORARY</code> nature only affects lifetime and visibility, not how you write to it.</p>

<p><strong>Insert from a SELECT</strong> &mdash; very common when the temp table is staging data from elsewhere:</p>

<pre><code>INSERT INTO temp_employees (id, name, age, department)
SELECT id, name, age, department
FROM employees
WHERE active = 1
  AND hire_date &gt;= '2023-01-01';</code></pre>

<p>This is much faster than reading rows into the application and inserting one at a time.</p>

<p><strong>Combined create + populate</strong> &mdash; one statement (also shown in Q61):</p>

<pre><code>CREATE TEMPORARY TABLE temp_employees AS
SELECT id, name, age, department
FROM employees
WHERE department IN ('Engineering', 'Marketing');</code></pre>

<p><strong>Bulk insert from a CSV file</strong> &mdash; into a temp table for staging before the real load:</p>

<pre><code>LOAD DATA LOCAL INFILE '/tmp/employees.csv'
INTO TABLE temp_employees
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(id, name, age, department);</code></pre>

<p><strong>Why use a temp table for staging</strong>:</p>
<ul>
  <li>Validate the data with SELECTs before merging into the production table.</li>
  <li>Catch problems (duplicates, bad values) without touching the real data.</li>
  <li>Run transformations or joins to enrich rows before the final insert.</li>
</ul>

<p>After validating, merge into the live table:</p>

<pre><code>INSERT INTO employees (id, name, age, department)
SELECT id, name, age, department
FROM temp_employees
WHERE id NOT IN (SELECT id FROM employees);
-- Or use INSERT ... ON DUPLICATE KEY UPDATE for upserts.</code></pre>
'''

ANSWERS[63] = r'''
<pre><code>SELECT * FROM temp_employees;</code></pre>

<p>Querying a temporary table is identical to querying a regular table &mdash; same SELECT, JOIN, WHERE, GROUP BY syntax. The only differences are scope (current connection only) and lifetime (gone when the connection closes).</p>

<p><strong>With filtering and aggregation</strong>:</p>

<pre><code>SELECT department, COUNT(*) AS staff, AVG(age) AS avg_age
FROM temp_employees
WHERE age &gt;= 25
GROUP BY department
ORDER BY staff DESC;</code></pre>

<p><strong>Joining a temp table to a permanent table</strong> &mdash; the most useful case:</p>

<pre><code>-- Compare staged data to live data
SELECT t.id, t.name AS new_name, e.name AS current_name
FROM temp_employees t
LEFT JOIN employees e ON e.id = t.id
WHERE t.name &lt;&gt; e.name OR e.id IS NULL;
-- Find rows that would be UPDATEd or INSERTed</code></pre>

<p><strong>Visibility scope</strong> &mdash; key gotchas:</p>

<ul>
  <li>A temp table is invisible to other connections, even with the same name &mdash; no contention.</li>
  <li>If a permanent table with the same name exists, the temporary table <em>shadows</em> it &mdash; queries hit the temp table for the duration of the session.</li>
  <li>Temp tables can&rsquo;t be referenced multiple times in the same query in MySQL (a known limitation):
<pre><code>-- ERROR: Can't reopen table 'temp_t'
SELECT a.id FROM temp_t a JOIN temp_t b ON a.id = b.id;</code></pre>
  Workaround: copy to another temp table or use a CTE.</li>
</ul>

<p><strong>Inspect or describe</strong>:</p>

<pre><code>DESCRIBE temp_employees;
SHOW CREATE TABLE temp_employees\G</code></pre>

<p>The <code>information_schema.TABLES</code> doesn&rsquo;t list temporary tables &mdash; they&rsquo;re session-private. To list temps in a session in MySQL 5.7+, query <code>information_schema.INNODB_TEMP_TABLE_INFO</code>.</p>

<p><strong>Storage</strong>: temp tables use the engine specified by <code>internal_tmp_disk_storage_engine</code> (defaults to InnoDB). Small temp tables stay in memory; large ones spill to disk.</p>
'''

ANSWERS[64] = r'''
<pre><code>SELECT department_id, name, salary
FROM (
  SELECT
    department_id,
    name,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
  FROM employees
) ranked
WHERE rn = 1
ORDER BY department_id;</code></pre>

<p>The window function <code>ROW_NUMBER()</code> assigns 1 to the highest salary in each department; <code>WHERE rn = 1</code> keeps only those rows. This is the canonical "top-1 per group" pattern in MySQL 8+.</p>

<p><strong>Handle ties</strong> &mdash; what if two employees share the highest salary in a department?</p>

<table>
  <tr><th>Function</th><th>Behavior on ties</th></tr>
  <tr><td><code>ROW_NUMBER()</code></td><td>Arbitrary: assigns 1, 2, 3 (one winner)</td></tr>
  <tr><td><code>RANK()</code></td><td>Both get rank 1, next row is 3 (one winner per tier)</td></tr>
  <tr><td><code>DENSE_RANK()</code></td><td>Both get rank 1, next row is 2 (no gaps)</td></tr>
</table>

<pre><code>-- Include all employees tied for highest in each department
SELECT department_id, name, salary
FROM (
  SELECT
    department_id, name, salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rk
  FROM employees
) ranked
WHERE rk = 1
ORDER BY department_id, name;</code></pre>

<p><strong>Pre-MySQL 8 alternative</strong> &mdash; correlated subquery:</p>

<pre><code>SELECT e.department_id, e.name, e.salary
FROM employees e
WHERE e.salary = (
  SELECT MAX(salary) FROM employees
  WHERE department_id = e.department_id
)
ORDER BY e.department_id;</code></pre>

<p>The inner query is re-evaluated for each row (correlated). Slower on large tables; window functions are preferred when available.</p>

<p><strong>With department names from a related table</strong>:</p>

<pre><code>SELECT d.department_name, e.name, e.salary
FROM (
  SELECT department_id, name, salary,
         ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
  FROM employees
) e
JOIN departments d ON d.department_id = e.department_id
WHERE e.rn = 1
ORDER BY d.department_name;</code></pre>

<p><strong>Top N per group</strong> &mdash; change the predicate:</p>

<pre><code>WHERE rn &lt;= 3       -- top 3 per department</code></pre>

<p><strong>Performance</strong>: index <code>(department_id, salary DESC)</code> helps the optimizer order rows for the window function efficiently.</p>
'''

ANSWERS[65] = r'''
<pre><code>DELIMITER //

CREATE FUNCTION count_employees_in(dept_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
  DECLARE n INT;

  SELECT COUNT(*) INTO n
  FROM employees
  WHERE department_id = dept_id;

  RETURN n;
END //

DELIMITER ;</code></pre>

<p>Stored functions return a value and can be used inside SQL expressions like a built-in. Call them in <code>SELECT</code>, <code>WHERE</code>, etc.</p>

<p><strong>Use it</strong>:</p>

<pre><code>SELECT count_employees_in(5);                       -- 12

SELECT name, count_employees_in(department_id) AS dept_size
FROM employees;</code></pre>

<p><strong>Function characteristics</strong> &mdash; clauses MySQL requires you to declare:</p>

<table>
  <tr><th>Clause</th><th>Meaning</th></tr>
  <tr><td><code>DETERMINISTIC</code></td><td>Same input → same output. Required for some optimizations and replication.</td></tr>
  <tr><td><code>NOT DETERMINISTIC</code></td><td>Output may vary (e.g., uses NOW()). Default if you don&rsquo;t specify.</td></tr>
  <tr><td><code>READS SQL DATA</code></td><td>Reads but doesn&rsquo;t modify data.</td></tr>
  <tr><td><code>MODIFIES SQL DATA</code></td><td>Writes data.</td></tr>
  <tr><td><code>NO SQL</code></td><td>Pure computation, no data access.</td></tr>
  <tr><td><code>CONTAINS SQL</code></td><td>Default; runs SQL but doesn&rsquo;t access tables.</td></tr>
</table>

<p>Without these declarations, MySQL refuses to create the function unless <code>log_bin_trust_function_creators</code> is on (binlog uses these to decide replication safety).</p>

<p><strong>Why the DELIMITER dance</strong>: function bodies contain semicolons. Switching the statement delimiter to <code>//</code> lets MySQL know that the inner <code>;</code> are part of the function, not statement endings. Switch back to <code>;</code> after.</p>

<p><strong>Function vs procedure</strong>: functions return a value and can be used inline in queries. Procedures don&rsquo;t return values directly &mdash; they&rsquo;re called via <code>CALL</code> and can return multiple result sets.</p>

<p><strong>Drop and replace</strong>:</p>

<pre><code>DROP FUNCTION IF EXISTS count_employees_in;
-- then re-CREATE with new logic</code></pre>

<p>MySQL has no <code>CREATE OR REPLACE FUNCTION</code> &mdash; you must drop and recreate.</p>
'''

ANSWERS[66] = r'''
<pre><code>SELECT count_employees_in(5);
-- e.g., 12</code></pre>

<p>Functions are called in any SQL expression position &mdash; <code>SELECT</code>, <code>WHERE</code>, <code>HAVING</code>, <code>ORDER BY</code>, even in <code>UPDATE</code> SET clauses.</p>

<p><strong>Use the function value in a query</strong>:</p>

<pre><code>-- Show each department&rsquo;s name with its current employee count
SELECT d.department_id,
       d.department_name,
       count_employees_in(d.department_id) AS staff_count
FROM departments d
ORDER BY staff_count DESC;</code></pre>

<p>Note that the function is invoked once per row of the outer query &mdash; effectively a correlated subquery. For large result sets a single GROUP BY is faster:</p>

<pre><code>-- Equivalent and more efficient for many departments
SELECT d.department_id, d.department_name, COUNT(e.id) AS staff_count
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY staff_count DESC;</code></pre>

<p>Functions are still valuable for encapsulating business logic that&rsquo;s used many places &mdash; just be aware of per-row invocation cost.</p>

<p><strong>In a WHERE clause</strong>:</p>

<pre><code>SELECT department_id, department_name
FROM departments
WHERE count_employees_in(department_id) &gt; 10;</code></pre>

<p>Same caveat: row-by-row evaluation. Index-friendly only if the function&rsquo;s logic could itself use indexes (which it does here &mdash; the inner COUNT can use an index on <code>employees.department_id</code>).</p>

<p><strong>Inside an UPDATE</strong>:</p>

<pre><code>UPDATE departments
SET cached_employee_count = count_employees_in(department_id);</code></pre>

<p>Useful when materializing a denormalized counter column &mdash; one statement updates every row.</p>

<p><strong>Test from the application</strong>:</p>

<pre><code>// Node.js with mysql2
const [[row]] = await conn.execute('SELECT count_employees_in(?) AS n', [deptId]);
console.log(row.n);</code></pre>

<p><strong>List existing functions</strong>:</p>

<pre><code>SHOW FUNCTION STATUS WHERE Db = 'company';

-- Or via information_schema:
SELECT ROUTINE_NAME, ROUTINE_TYPE
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = 'company';</code></pre>
'''

ANSWERS[67] = r'''
<pre><code>SELECT DISTINCT e.id, e.name
FROM employees e
JOIN bonuses b ON b.employee_id = e.id
ORDER BY e.name;</code></pre>

<p>An <code>INNER JOIN</code> against the <code>bonuses</code> table returns only employees who have at least one matching bonus row. <code>DISTINCT</code> deduplicates employees who received multiple bonuses.</p>

<p><strong>Equivalent with EXISTS</strong> &mdash; often clearer and lets the optimizer stop on first match:</p>

<pre><code>SELECT id, name
FROM employees e
WHERE EXISTS (
  SELECT 1 FROM bonuses b WHERE b.employee_id = e.id
)
ORDER BY name;</code></pre>

<p>No need for <code>DISTINCT</code> &mdash; <code>EXISTS</code> stops at the first match per outer row.</p>

<p><strong>With bonus details</strong>:</p>

<pre><code>SELECT
  e.id, e.name,
  b.bonus_amount,
  b.awarded_date,
  b.reason
FROM employees e
JOIN bonuses b ON b.employee_id = e.id
ORDER BY b.awarded_date DESC, e.name;</code></pre>

<p>Multiple rows per employee for those with multiple bonuses.</p>

<p><strong>Aggregate per employee</strong> &mdash; total bonus and count:</p>

<pre><code>SELECT
  e.id,
  e.name,
  COUNT(b.id) AS bonus_count,
  SUM(b.bonus_amount) AS total_bonus,
  MAX(b.awarded_date) AS most_recent_bonus
FROM employees e
JOIN bonuses b ON b.employee_id = e.id
GROUP BY e.id, e.name
HAVING bonus_count &gt;= 1
ORDER BY total_bonus DESC;</code></pre>

<p><strong>Filter to recent bonuses only</strong>:</p>

<pre><code>SELECT DISTINCT e.id, e.name
FROM employees e
JOIN bonuses b ON b.employee_id = e.id
WHERE b.awarded_date &gt;= CURDATE() - INTERVAL 1 YEAR;</code></pre>

<p><strong>Find employees who&rsquo;ve received bonuses above a threshold</strong>:</p>

<pre><code>SELECT DISTINCT e.id, e.name
FROM employees e
JOIN bonuses b ON b.employee_id = e.id
WHERE b.bonus_amount &gt; 5000;</code></pre>

<p><strong>If "bonus" is a column on employees</strong> instead of a separate table:</p>

<pre><code>SELECT id, name, bonus
FROM employees
WHERE bonus IS NOT NULL AND bonus &gt; 0;</code></pre>

<p>Indexes on <code>bonuses.employee_id</code> make the join efficient.</p>
'''

ANSWERS[68] = r'''
<pre><code>SELECT SUM(bonus_amount) AS total_bonuses
FROM bonuses;</code></pre>

<p>Single number: the sum of every bonus ever paid. <code>SUM</code> ignores NULLs.</p>

<p><strong>Total per year</strong>:</p>

<pre><code>SELECT
  YEAR(awarded_date) AS year,
  SUM(bonus_amount)  AS total,
  COUNT(*)           AS bonus_count
FROM bonuses
GROUP BY YEAR(awarded_date)
ORDER BY year DESC;</code></pre>

<p><strong>Total per employee</strong>:</p>

<pre><code>SELECT
  e.id,
  e.name,
  COALESCE(SUM(b.bonus_amount), 0) AS total_bonus,
  COUNT(b.id)                       AS bonus_count
FROM employees e
LEFT JOIN bonuses b ON b.employee_id = e.id
GROUP BY e.id, e.name
ORDER BY total_bonus DESC;</code></pre>

<p><code>LEFT JOIN</code> keeps all employees, even those with zero bonuses; <code>COALESCE(SUM(...), 0)</code> shows their total as 0 instead of NULL.</p>

<p><strong>Total per department</strong>:</p>

<pre><code>SELECT
  d.department_name,
  COALESCE(SUM(b.bonus_amount), 0) AS dept_total_bonus,
  COUNT(DISTINCT b.employee_id)    AS unique_recipients
FROM departments d
JOIN employees e   ON e.department_id = d.department_id
LEFT JOIN bonuses b ON b.employee_id  = e.id
GROUP BY d.department_id, d.department_name
ORDER BY dept_total_bonus DESC;</code></pre>

<p><strong>Time-windowed totals</strong>:</p>

<pre><code>-- Last 12 months
SELECT SUM(bonus_amount) AS last_year_total
FROM bonuses
WHERE awarded_date &gt;= CURDATE() - INTERVAL 1 YEAR;

-- Quarter-by-quarter
SELECT
  YEAR(awarded_date)    AS year,
  QUARTER(awarded_date) AS quarter,
  SUM(bonus_amount)     AS qtr_total
FROM bonuses
GROUP BY YEAR(awarded_date), QUARTER(awarded_date)
ORDER BY year DESC, quarter DESC;</code></pre>

<p><strong>Multiple aggregates in one query</strong> &mdash; a complete payout summary:</p>

<pre><code>SELECT
  COUNT(*)              AS total_payouts,
  COUNT(DISTINCT employee_id) AS recipients,
  SUM(bonus_amount)     AS total_amount,
  ROUND(AVG(bonus_amount), 2) AS avg_amount,
  MIN(bonus_amount)     AS smallest,
  MAX(bonus_amount)     AS largest
FROM bonuses
WHERE awarded_date &gt;= '2026-01-01';</code></pre>

<p><strong>Type considerations</strong>: store bonus amounts in <code>DECIMAL(10, 2)</code>, not <code>FLOAT</code>. <code>SUM</code> on <code>DECIMAL</code> returns a <code>DECIMAL</code> with extended precision &mdash; no rounding errors.</p>
'''

ANSWERS[69] = r'''
<pre><code>SELECT id, name
FROM employees
WHERE BINARY name = UPPER(name);</code></pre>

<p>The <code>BINARY</code> operator forces a byte-by-byte case-sensitive comparison &mdash; otherwise the default case-insensitive collation makes <code>'Alice' = 'ALICE'</code> evaluate to TRUE, which would match every name.</p>

<p><strong>Alternative without BINARY</strong> &mdash; explicit collation:</p>

<pre><code>SELECT id, name
FROM employees
WHERE name COLLATE utf8mb4_bin = UPPER(name);</code></pre>

<p>Same effect: case-sensitive comparison via a binary collation.</p>

<p><strong>Using a regex</strong> &mdash; matches names that contain only uppercase letters and spaces:</p>

<pre><code>SELECT id, name
FROM employees
WHERE name REGEXP '^[A-Z ]+$';</code></pre>

<p><strong>Why "uppercase" can be ambiguous</strong>:</p>
<ul>
  <li><code>'JOHN SMITH'</code> &mdash; clearly uppercase.</li>
  <li><code>'JOHN'</code> &mdash; uppercase, but a single word.</li>
  <li><code>'JOHN-SMITH'</code> &mdash; uppercase with hyphen; depends on whether hyphen counts as "letter."</li>
  <li><code>'JOHN 3RD'</code> &mdash; mixed letters and digits.</li>
</ul>

<p>Choose the regex to match your intent. The <code>BINARY name = UPPER(name)</code> form treats any character that&rsquo;s already its own uppercase (digits, punctuation, spaces) as "uppercase" &mdash; which is usually what you want.</p>

<p><strong>Find names with at least one uppercase letter</strong> (different question):</p>

<pre><code>SELECT id, name
FROM employees
WHERE name REGEXP '[A-Z]';</code></pre>

<p><strong>Find lowercase names</strong> (the inverse):</p>

<pre><code>SELECT id, name
FROM employees
WHERE BINARY name = LOWER(name);</code></pre>

<p><strong>Performance</strong>: <code>WHERE BINARY col = ...</code> can&rsquo;t use a normal index because the comparison is using a different collation. For occasional admin/data-quality queries this is fine; for production filters consider storing a normalized form alongside the original.</p>

<p>Real-world use: detecting data entry where users typed in all caps. Often paired with a fix:</p>

<pre><code>UPDATE employees
SET name = CONCAT(UPPER(LEFT(name, 1)), LOWER(SUBSTRING(name, 2)))
WHERE BINARY name = UPPER(name);
-- Title-cases names that are all uppercase</code></pre>
'''

ANSWERS[70] = r'''
<pre><code>UPDATE employees
SET name = LOWER(name);</code></pre>

<p>Updates every row, replacing each <code>name</code> with its lowercase version. <code>LOWER()</code> handles ASCII; for full Unicode case folding it works correctly with <code>utf8mb4</code> collations.</p>

<p><strong>Always preview first</strong>:</p>

<pre><code>SELECT id, name AS current_name, LOWER(name) AS new_name
FROM employees
WHERE name &lt;&gt; LOWER(name);</code></pre>

<p>Shows only the rows that would actually change. Run the UPDATE only after confirming the diff looks right.</p>

<p><strong>In a transaction for safety</strong>:</p>

<pre><code>START TRANSACTION;
UPDATE employees SET name = LOWER(name);
SELECT COUNT(*) FROM employees WHERE name &lt;&gt; LOWER(name);  -- should be 0
-- if good: COMMIT;  if not: ROLLBACK;</code></pre>

<p><strong>Just for SELECT (without modifying the data)</strong>:</p>

<pre><code>SELECT id, LOWER(name) AS name FROM employees;</code></pre>

<p>Lower-cases on the way out without touching stored data &mdash; usually preferable. Only modify stored data when you genuinely need a normalized canonical form.</p>

<p><strong>Why you might NOT want to lowercase stored names</strong>:</p>
<ul>
  <li>Loss of the user&rsquo;s preferred capitalization (Alice → alice).</li>
  <li>Names like "McDonald", "DiCaprio", or "ben-Yair" lose meaningful capitalization.</li>
  <li>Display becomes uglier; you&rsquo;d need to re-capitalize when rendering.</li>
</ul>

<p>A common compromise: store original-case names AND lowercase versions for searching:</p>

<pre><code>ALTER TABLE employees
ADD COLUMN name_lower VARCHAR(100)
GENERATED ALWAYS AS (LOWER(name)) STORED;

CREATE INDEX idx_name_lower ON employees(name_lower);</code></pre>

<p>The generated column stays in sync automatically. Searches use <code>WHERE name_lower = ?</code> for case-insensitive lookups while preserving display formatting.</p>

<p><strong>Case-insensitive comparison without modifying data</strong> &mdash; the default <code>utf8mb4_0900_ai_ci</code> collation already does this:</p>

<pre><code>SELECT * FROM employees WHERE name = 'alice';
-- matches 'Alice', 'ALICE', 'alice'</code></pre>
'''

ANSWERS[71] = r'''
<pre><code>SELECT first_name, GROUP_CONCAT(name ORDER BY name) AS people, COUNT(*) AS shared_by
FROM (
  SELECT id, name, SUBSTRING_INDEX(name, ' ', 1) AS first_name
  FROM employees
) e
GROUP BY first_name
HAVING COUNT(*) &gt; 1
ORDER BY shared_by DESC, first_name;</code></pre>

<p>The inner subquery extracts the first word from <code>name</code> using <code>SUBSTRING_INDEX(name, ' ', 1)</code> &mdash; everything up to the first space. The outer query groups by that and keeps groups with two or more members.</p>

<p>Sample output:</p>

<pre><code>+------------+----------------------------+-----------+
| first_name | people                     | shared_by |
+------------+----------------------------+-----------+
| Alice      | Alice Smith, Alice Wong    |     2     |
| Bob        | Bob Jones, Bob Lee, Bob Yi |     3     |
+------------+----------------------------+-----------+</code></pre>

<p><strong>If the schema has separate <code>first_name</code> and <code>last_name</code> columns</strong> &mdash; preferred design:</p>

<pre><code>SELECT first_name, GROUP_CONCAT(CONCAT(first_name, ' ', last_name)) AS people, COUNT(*) AS shared_by
FROM employees
GROUP BY first_name
HAVING COUNT(*) &gt; 1
ORDER BY shared_by DESC;</code></pre>

<p>Much cleaner &mdash; no parsing of a combined <code>name</code> string. Always prefer separate name columns when possible: parsing names is fragile because of compound surnames, multi-word given names, prefixes/suffixes.</p>

<p><strong>Alternative: self-join</strong> &mdash; pair employees with same first name:</p>

<pre><code>SELECT
  e1.id   AS id_1,    e1.name AS name_1,
  e2.id   AS id_2,    e2.name AS name_2
FROM employees e1
JOIN employees e2
  ON SUBSTRING_INDEX(e1.name, ' ', 1) = SUBSTRING_INDEX(e2.name, ' ', 1)
 AND e1.id &lt; e2.id;
-- e1.id &lt; e2.id avoids duplicate (A,B)/(B,A) pairs</code></pre>

<p><strong>Most common first names</strong>:</p>

<pre><code>SELECT
  SUBSTRING_INDEX(name, ' ', 1) AS first_name,
  COUNT(*) AS frequency
FROM employees
GROUP BY first_name
ORDER BY frequency DESC
LIMIT 10;</code></pre>

<p><strong>Performance</strong>: parsing <code>name</code> on the fly is row-by-row work. For repeated lookups, store first/last name in separate columns or as generated columns:</p>

<pre><code>ALTER TABLE employees
ADD COLUMN first_name VARCHAR(50)
GENERATED ALWAYS AS (SUBSTRING_INDEX(name, ' ', 1)) STORED;
CREATE INDEX idx_first_name ON employees(first_name);</code></pre>
'''

ANSWERS[72] = r'''
<pre><code>SELECT
  id,
  name AS full_name,
  SUBSTRING_INDEX(name, ' ', 1)          AS first_name,
  SUBSTRING_INDEX(name, ' ', -1)         AS last_name
FROM employees;</code></pre>

<p><code>SUBSTRING_INDEX(str, delim, n)</code>:</p>
<ul>
  <li>Positive <code>n</code>: take everything <em>before</em> the n-th occurrence of <code>delim</code>.</li>
  <li>Negative <code>n</code>: take everything <em>after</em> the n-th-from-the-end.</li>
</ul>

<p>So <code>(name, ' ', 1)</code> = first word; <code>(name, ' ', -1)</code> = last word.</p>

<p><strong>Edge cases</strong> the simple version doesn&rsquo;t handle:</p>

<table>
  <tr><th>Input</th><th>first_name</th><th>last_name</th></tr>
  <tr><td>'Alice Smith'</td><td>Alice</td><td>Smith</td></tr>
  <tr><td>'Mary Anne Brown'</td><td>Mary</td><td>Brown (lost "Anne")</td></tr>
  <tr><td>'Cher'</td><td>Cher</td><td>Cher (same as first)</td></tr>
  <tr><td>'Pedro de la Cruz'</td><td>Pedro</td><td>Cruz (loses "de la")</td></tr>
</table>

<p><strong>Improved: middle parts go with first name</strong>:</p>

<pre><code>SELECT
  id,
  name AS full_name,
  TRIM(SUBSTRING_INDEX(name, ' ', LENGTH(name) - LENGTH(REPLACE(name, ' ', '')))) AS first_part,
  CASE
    WHEN INSTR(name, ' ') = 0 THEN NULL                -- single word
    ELSE SUBSTRING_INDEX(name, ' ', -1)
  END AS last_name
FROM employees;</code></pre>

<p><strong>Handle no-space-name correctly</strong>:</p>

<pre><code>SELECT
  id,
  name AS full_name,
  CASE
    WHEN INSTR(name, ' ') &gt; 0 THEN SUBSTRING_INDEX(name, ' ', 1)
    ELSE name
  END AS first_name,
  CASE
    WHEN INSTR(name, ' ') &gt; 0 THEN SUBSTRING_INDEX(name, ' ', -1)
    ELSE NULL
  END AS last_name
FROM employees;</code></pre>

<p><strong>Permanent split via UPDATE</strong> &mdash; if the goal is migrating to separate columns:</p>

<pre><code>ALTER TABLE employees
  ADD COLUMN first_name VARCHAR(50),
  ADD COLUMN last_name  VARCHAR(50);

UPDATE employees
SET first_name = TRIM(SUBSTRING_INDEX(name, ' ', 1)),
    last_name  = CASE
                   WHEN INSTR(name, ' ') &gt; 0 THEN TRIM(SUBSTRING_INDEX(name, ' ', -1))
                   ELSE NULL
                 END;

-- Optionally drop the combined column once verified
-- ALTER TABLE employees DROP COLUMN name;</code></pre>

<p><strong>Real-world advice</strong>: name parsing is genuinely hard &mdash; cultural conventions vary widely (some cultures put surname first; some have no concept of "first/last"). Whenever possible, capture name parts at input rather than parsing them out later.</p>
'''

ANSWERS[73] = r'''
<pre><code>SELECT id, name, email
FROM employees
WHERE email LIKE '%@example.com';</code></pre>

<p>Finds employees whose email ends with <code>@example.com</code>. <code>LIKE</code> with <code>%</code> wildcards is the simplest pattern match.</p>

<p><strong>Anchored at start vs middle vs end</strong>:</p>

<pre><code>-- Starts with 'admin'
WHERE email LIKE 'admin%'

-- Contains 'support'
WHERE email LIKE '%support%'

-- Ends with '@example.com'
WHERE email LIKE '%@example.com'</code></pre>

<p><strong>Index usage</strong>:</p>
<ul>
  <li><code>LIKE 'admin%'</code> &mdash; can use a B-tree index on <code>email</code> (anchored at start).</li>
  <li><code>LIKE '%support%'</code> or <code>LIKE '%@example.com'</code> &mdash; cannot use a regular B-tree index. MySQL scans every row.</li>
</ul>

<p><strong>For domain searches specifically</strong>, store the domain as a separate (or generated) column:</p>

<pre><code>ALTER TABLE employees
ADD COLUMN email_domain VARCHAR(100)
GENERATED ALWAYS AS (SUBSTRING_INDEX(email, '@', -1)) STORED;

CREATE INDEX idx_email_domain ON employees(email_domain);

-- Now this is fast:
SELECT * FROM employees WHERE email_domain = 'example.com';</code></pre>

<p>The generated column stays in sync automatically; the index makes lookups O(log n).</p>

<p><strong>Regex matching</strong> &mdash; more powerful but no index help:</p>

<pre><code>SELECT id, email
FROM employees
WHERE email REGEXP '^[a-z0-9.]+@example\\.com$';   -- strict format
SELECT id, email
FROM employees
WHERE email REGEXP '\\+';                            -- contains '+'
SELECT id, email
FROM employees
WHERE email REGEXP '\\.(co|org|net)$';               -- specific TLDs</code></pre>

<p><strong>Case sensitivity</strong>: with the default <code>utf8mb4_0900_ai_ci</code> collation, <code>'Bob@X.com'</code> and <code>'bob@x.com'</code> match the same patterns. For case-sensitive matching: <code>WHERE email LIKE BINARY 'Admin%'</code>.</p>

<p><strong>Common patterns</strong>:</p>

<pre><code>-- Find emails with plus aliasing
WHERE email LIKE '%+%@%';

-- Find emails missing a TLD (data quality)
WHERE email NOT REGEXP '\\.[a-z]{2,}$';

-- Find emails with multiple @ signs (definitely invalid)
WHERE LENGTH(email) - LENGTH(REPLACE(email, '@', '')) &gt; 1;</code></pre>

<p>For real email validation, use a regex that matches the relevant standard, or perform validation in application code (libraries handle edge cases better than SQL regex).</p>
'''

ANSWERS[74] = r'''
<pre><code>CREATE TABLE projects (
  project_id     INT AUTO_INCREMENT PRIMARY KEY,
  project_name   VARCHAR(200) NOT NULL,
  start_date     DATE NOT NULL,
  end_date       DATE NULL,
  status         ENUM('planned', 'active', 'on_hold', 'completed', 'cancelled')
                 NOT NULL DEFAULT 'planned',
  budget         DECIMAL(12, 2) NULL,
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_status (status),
  INDEX idx_dates  (start_date, end_date)
) ENGINE=InnoDB;</code></pre>

<p>The table extends the basic three columns with practical additions:</p>

<ul>
  <li><strong>end_date NULL</strong> &mdash; until the project ends.</li>
  <li><strong>status ENUM</strong> &mdash; constrained to a defined list of values; database rejects invalid values.</li>
  <li><strong>budget DECIMAL(12, 2)</strong> &mdash; exact decimal arithmetic for money.</li>
  <li><strong>created_at / updated_at</strong> &mdash; audit columns, automatically maintained.</li>
  <li><strong>Indexes</strong> on commonly-filtered columns (status, dates).</li>
</ul>

<p><strong>Minimal version exactly matching the question</strong>:</p>

<pre><code>CREATE TABLE projects (
  project_id   INT AUTO_INCREMENT PRIMARY KEY,
  project_name VARCHAR(200) NOT NULL,
  start_date   DATE NOT NULL
);</code></pre>

<p><strong>Add a CHECK constraint for date sanity</strong> (MySQL 8.0.16+):</p>

<pre><code>ALTER TABLE projects
ADD CONSTRAINT chk_project_dates
CHECK (end_date IS NULL OR end_date &gt;= start_date);</code></pre>

<p><strong>Common variations</strong>:</p>

<pre><code>-- Soft delete pattern
ALTER TABLE projects ADD COLUMN deleted_at DATETIME NULL;
-- Then queries filter: WHERE deleted_at IS NULL

-- Project owner
ALTER TABLE projects
ADD COLUMN owner_id INT,
ADD CONSTRAINT fk_project_owner
  FOREIGN KEY (owner_id) REFERENCES employees(id);

-- Tagging / categorization
ALTER TABLE projects
ADD COLUMN tags JSON;
-- Stored as ['frontend', 'urgent', 'q4']</code></pre>

<p><strong>Why ENUM works for status</strong>: small fixed set of values, very compact storage (1-2 bytes), and MySQL rejects invalid inserts. Trade-off: changing the set requires <code>ALTER TABLE</code>. For larger or more dynamic value sets, prefer a separate <code>statuses</code> lookup table with a foreign key.</p>
'''

ANSWERS[75] = r'''
<pre><code>INSERT INTO projects (project_name, start_date)
VALUES ('Mobile App Redesign', '2026-05-01');</code></pre>

<p>The minimum required columns are <code>project_name</code> and <code>start_date</code> &mdash; both are <code>NOT NULL</code> with no defaults. Other columns get their defaults: <code>project_id</code> auto-increments, <code>status</code> = 'planned', <code>created_at</code> = now.</p>

<p><strong>Insert with all columns specified</strong>:</p>

<pre><code>INSERT INTO projects
  (project_name, start_date, end_date, status, budget)
VALUES
  ('Q3 Migration', '2026-07-01', '2026-09-30', 'planned', 250000.00);</code></pre>

<p><strong>Bulk insert</strong> &mdash; multiple projects in one statement:</p>

<pre><code>INSERT INTO projects (project_name, start_date, status, budget) VALUES
  ('Mobile App',          '2026-05-01', 'active',  500000.00),
  ('Data Pipeline',       '2026-04-15', 'planned', 120000.00),
  ('Marketing Campaign',  '2026-06-01', 'planned',  80000.00);</code></pre>

<p><strong>Get the new project_id</strong>:</p>

<pre><code>INSERT INTO projects (project_name, start_date)
VALUES ('Cloud Migration', '2026-08-01');

SELECT LAST_INSERT_ID();      -- e.g., 124</code></pre>

<p>From application code, the inserted ID is usually exposed directly:</p>

<pre><code>// Node.js mysql2
const [result] = await conn.execute(
  'INSERT INTO projects (project_name, start_date) VALUES (?, ?)',
  ['Cloud Migration', '2026-08-01']
);
console.log(result.insertId);     // 124</code></pre>

<p><strong>Insert from another table</strong> &mdash; e.g., copy projects from a staging table:</p>

<pre><code>INSERT INTO projects (project_name, start_date, status)
SELECT name, planned_start, 'planned'
FROM staging_projects
WHERE approved = 1;</code></pre>

<p><strong>Upsert pattern</strong> &mdash; insert if new, update if exists. Requires a unique key:</p>

<pre><code>INSERT INTO projects (project_id, project_name, start_date, status)
VALUES (123, 'Mobile App', '2026-05-01', 'active')
ON DUPLICATE KEY UPDATE
  project_name = VALUES(project_name),
  start_date   = VALUES(start_date),
  status       = VALUES(status);</code></pre>

<p>Useful for sync jobs that re-run with the same input data.</p>

<p><strong>From the application side, always parameterize</strong> &mdash; never build the SQL string from user input.</p>
'''

ANSWERS[76] = r'''
<pre><code>UPDATE projects
SET start_date = '2026-06-15'
WHERE project_id = 42;</code></pre>

<p>Always update by primary key when you know it &mdash; precise and fast.</p>

<p><strong>Track the change</strong> &mdash; <code>updated_at</code> updates automatically thanks to <code>ON UPDATE CURRENT_TIMESTAMP</code> in the schema (Q74). No manual handling needed.</p>

<p><strong>Conditional update with sanity check</strong>:</p>

<pre><code>UPDATE projects
SET start_date = '2026-06-15'
WHERE project_id = 42
  AND status IN ('planned', 'on_hold')      -- only if not yet active
  AND end_date IS NULL OR end_date &gt; '2026-06-15';   -- not after end</code></pre>

<p>The <code>WHERE</code> guards mean the UPDATE silently does nothing if the conditions don&rsquo;t hold &mdash; no error.</p>

<p><strong>Update with verification in a transaction</strong>:</p>

<pre><code>START TRANSACTION;

UPDATE projects
SET start_date = '2026-06-15'
WHERE project_id = 42;

SELECT ROW_COUNT();   -- should be 1; if 0, the project doesn&rsquo;t exist

-- If correct
COMMIT;
-- Else
-- ROLLBACK;</code></pre>

<p><code>ROW_COUNT()</code> reports how many rows the previous statement affected.</p>

<p><strong>Recompute end_date too</strong> &mdash; if the project keeps the same duration:</p>

<pre><code>UPDATE projects
SET end_date = DATE_ADD('2026-06-15', INTERVAL DATEDIFF(end_date, start_date) DAY),
    start_date = '2026-06-15'
WHERE project_id = 42;</code></pre>

<p>This shifts both dates by the same amount, preserving project length.</p>

<p><strong>Bulk shift</strong> &mdash; postpone all planned projects by 2 weeks:</p>

<pre><code>UPDATE projects
SET start_date = DATE_ADD(start_date, INTERVAL 2 WEEK),
    end_date   = CASE
                   WHEN end_date IS NULL THEN NULL
                   ELSE DATE_ADD(end_date, INTERVAL 2 WEEK)
                 END
WHERE status = 'planned';</code></pre>

<p><strong>Prevent typo-style updates</strong>: enable <code>sql_safe_updates</code> for sessions where developers run ad-hoc UPDATEs &mdash; refuses any UPDATE without a key in the WHERE clause:</p>

<pre><code>SET sql_safe_updates = 1;
UPDATE projects SET start_date = '2026-06-15';
-- ERROR 1175 (HY000): You are using safe update mode...</code></pre>
'''

ANSWERS[77] = r'''
<pre><code>DELETE FROM projects
WHERE project_id = 42;</code></pre>

<p>Removes the project row permanently &mdash; foreign-key cascades may also remove related rows in other tables (e.g., assignments referencing this project).</p>

<p><strong>Verify what would be deleted first</strong>:</p>

<pre><code>SELECT * FROM projects WHERE project_id = 42;
-- Confirm this is the right project before deleting.</code></pre>

<p><strong>Soft-delete pattern</strong> &mdash; preferred in production for projects where audit/recovery matters:</p>

<pre><code>-- One-time schema change
ALTER TABLE projects ADD COLUMN deleted_at DATETIME NULL;

-- "Delete" by marking
UPDATE projects
SET deleted_at = NOW(), status = 'cancelled'
WHERE project_id = 42;

-- Application queries always include:
WHERE deleted_at IS NULL</code></pre>

<p>Soft delete preserves history, enables recovery, and avoids cascade pain. The trade-off is that every query must remember the filter &mdash; consider a view that hides the deleted rows.</p>

<p><strong>Hard delete with FK cascade</strong> &mdash; if foreign keys are <code>ON DELETE CASCADE</code>, deleting the project deletes its assignments too:</p>

<pre><code>-- Schema (defined once)
CREATE TABLE employee_projects (
  employee_id INT,
  project_id  INT,
  FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- Now this propagates the delete:
DELETE FROM projects WHERE project_id = 42;</code></pre>

<p><strong>Delete in a transaction</strong>:</p>

<pre><code>START TRANSACTION;
DELETE FROM projects WHERE project_id = 42;
SELECT ROW_COUNT();   -- expect 1
-- COMMIT or ROLLBACK based on what you see</code></pre>

<p><strong>Delete by criteria</strong> &mdash; e.g., remove all cancelled projects older than 2 years:</p>

<pre><code>DELETE FROM projects
WHERE status = 'cancelled'
  AND end_date &lt; CURDATE() - INTERVAL 2 YEAR;</code></pre>

<p><strong>Limit the blast radius</strong> &mdash; on huge tables, delete in batches to avoid long transactions and lock contention:</p>

<pre><code>-- Repeat until ROW_COUNT() = 0
DELETE FROM projects
WHERE status = 'cancelled'
  AND end_date &lt; CURDATE() - INTERVAL 2 YEAR
LIMIT 1000;</code></pre>

<p><strong>Truncate vs delete</strong>: <code>TRUNCATE TABLE projects</code> empties the table much faster but cannot be filtered by WHERE, can&rsquo;t be rolled back as cleanly, and resets <code>AUTO_INCREMENT</code>. Use only when you genuinely want to wipe everything.</p>
'''

ANSWERS[78] = r'''
<pre><code>CREATE TABLE employee_projects (
  employee_id  INT NOT NULL,
  project_id   INT NOT NULL,
  role         VARCHAR(50)    NOT NULL DEFAULT 'contributor',
  assigned_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  end_date     DATE NULL,

  PRIMARY KEY (employee_id, project_id),

  CONSTRAINT fk_ep_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id)
    ON DELETE CASCADE,

  CONSTRAINT fk_ep_project
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
    ON DELETE CASCADE,

  INDEX idx_ep_project (project_id)
) ENGINE=InnoDB;</code></pre>

<p>This is a <strong>junction table</strong> (also called a "join table" or "bridge table") that resolves the many-to-many relationship: one employee can be on many projects; one project can have many employees.</p>

<p><strong>The composite primary key</strong> <code>(employee_id, project_id)</code> means each employee can only be assigned to a given project once &mdash; if you need multiple roles per (employee, project) pair, use a surrogate key instead:</p>

<pre><code>CREATE TABLE employee_projects (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  employee_id  INT NOT NULL,
  project_id   INT NOT NULL,
  role         VARCHAR(50) NOT NULL,
  ...
  UNIQUE KEY uk_emp_proj_role (employee_id, project_id, role)
);</code></pre>

<p><strong>Why two indexes</strong>: the PK on <code>(employee_id, project_id)</code> makes lookups by employee fast (or by employee+project). The separate index on <code>(project_id)</code> makes lookups by project fast &mdash; otherwise queries like "who&rsquo;s on this project" would scan.</p>

<p><strong>Add an assignment</strong>:</p>

<pre><code>INSERT INTO employee_projects (employee_id, project_id, role)
VALUES (101, 42, 'lead');</code></pre>

<p><strong>Remove an assignment</strong>:</p>

<pre><code>DELETE FROM employee_projects
WHERE employee_id = 101 AND project_id = 42;</code></pre>

<p><strong>The ON DELETE CASCADE</strong> on the FKs means: deleting an employee or project removes their assignments automatically. Without cascade, MySQL refuses to delete the parent row if assignments exist &mdash; you&rsquo;d have to delete the assignments first.</p>

<p><strong>Common extensions</strong>:</p>
<ul>
  <li><code>hours_per_week</code> &mdash; capacity allocation.</li>
  <li><code>hourly_rate</code> &mdash; for billable projects.</li>
  <li><code>started_at</code> / <code>ended_at</code> &mdash; for tracking project tenure.</li>
</ul>

<p>Junction tables can carry their own attributes &mdash; the relationship itself can have meaningful data, not just IDs.</p>
'''

ANSWERS[79] = r'''
<pre><code>SELECT
  e.id   AS employee_id,
  e.name AS employee_name,
  p.project_id,
  p.project_name,
  ep.role,
  ep.assigned_at
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
JOIN projects p           ON p.project_id   = ep.project_id
ORDER BY e.name, p.project_name;</code></pre>

<p>Two joins through the junction table connect employees to projects. <code>INNER JOIN</code> returns only employees who are on projects and projects that have employees.</p>

<p><strong>Include unassigned employees</strong> &mdash; <code>LEFT JOIN</code> on the junction:</p>

<pre><code>SELECT
  e.id, e.name,
  p.project_name,
  ep.role
FROM employees e
LEFT JOIN employee_projects ep ON ep.employee_id = e.id
LEFT JOIN projects p           ON p.project_id   = ep.project_id
ORDER BY e.name, p.project_name;
-- Employees without assignments show NULL for project columns</code></pre>

<p>Employees on multiple projects appear in multiple rows. To collapse them:</p>

<pre><code>SELECT
  e.id,
  e.name,
  GROUP_CONCAT(p.project_name ORDER BY p.project_name SEPARATOR ', ') AS projects,
  COUNT(p.project_id) AS project_count
FROM employees e
LEFT JOIN employee_projects ep ON ep.employee_id = e.id
LEFT JOIN projects p           ON p.project_id   = ep.project_id
GROUP BY e.id, e.name
ORDER BY e.name;</code></pre>

<p>One row per employee, with their projects in a comma-separated list.</p>

<p><strong>Filter by project status</strong> &mdash; only active assignments:</p>

<pre><code>SELECT e.name, p.project_name, ep.role
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
JOIN projects p           ON p.project_id   = ep.project_id
WHERE p.status = 'active'
  AND ep.end_date IS NULL              -- still on the project
ORDER BY e.name;</code></pre>

<p><strong>Find employees on a specific project</strong>:</p>

<pre><code>SELECT e.id, e.name, ep.role, ep.assigned_at
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
WHERE ep.project_id = 42
ORDER BY ep.role, e.name;</code></pre>

<p><strong>Performance</strong>: indexes on the junction table&rsquo;s columns (PK <code>(employee_id, project_id)</code> + secondary on <code>project_id</code>) make both directions fast. <code>EXPLAIN</code> should show <code>type=ref</code> or <code>type=eq_ref</code> for each join.</p>
'''

ANSWERS[80] = r'''
<pre><code>SELECT id, name
FROM employees
WHERE id NOT IN (
  SELECT DISTINCT employee_id FROM employee_projects
  WHERE employee_id IS NOT NULL
)
ORDER BY name;</code></pre>

<p>The subquery returns every employee who has an assignment; the outer query keeps employees whose ID isn&rsquo;t in that list. The <code>WHERE employee_id IS NOT NULL</code> in the subquery prevents NULL values from breaking the <code>NOT IN</code> (NULL in the list makes the entire expression NULL, returning nothing).</p>

<p><strong>NOT EXISTS &mdash; safer with NULLs</strong>:</p>

<pre><code>SELECT id, name
FROM employees e
WHERE NOT EXISTS (
  SELECT 1 FROM employee_projects ep
  WHERE ep.employee_id = e.id
)
ORDER BY name;</code></pre>

<p><code>NOT EXISTS</code> short-circuits as soon as it finds a match (or doesn&rsquo;t) and isn&rsquo;t affected by NULLs in the data. Generally preferred over <code>NOT IN</code> for subqueries.</p>

<p><strong>LEFT JOIN with IS NULL</strong> &mdash; another common idiom:</p>

<pre><code>SELECT e.id, e.name
FROM employees e
LEFT JOIN employee_projects ep ON ep.employee_id = e.id
WHERE ep.employee_id IS NULL
ORDER BY e.name;</code></pre>

<p>The <code>LEFT JOIN</code> matches employees to assignments; <code>WHERE ep.employee_id IS NULL</code> keeps only employees with no match.</p>

<p>All three approaches return the same rows. <strong>NOT EXISTS is generally the fastest and clearest</strong> in modern MySQL.</p>

<p><strong>Filter to active-status only</strong> &mdash; "no current assignment":</p>

<pre><code>SELECT e.id, e.name
FROM employees e
WHERE NOT EXISTS (
  SELECT 1 FROM employee_projects ep
  JOIN projects p ON p.project_id = ep.project_id
  WHERE ep.employee_id = e.id
    AND p.status = 'active'
    AND (ep.end_date IS NULL OR ep.end_date &gt; CURDATE())
);</code></pre>

<p>"Currently unassigned" employees may still have past or planned assignments &mdash; this version excludes those.</p>

<p><strong>Count of unassigned</strong>:</p>

<pre><code>SELECT COUNT(*) AS unassigned_count
FROM employees e
WHERE NOT EXISTS (
  SELECT 1 FROM employee_projects ep
  WHERE ep.employee_id = e.id
);</code></pre>

<p><strong>Performance</strong>: an index on <code>employee_projects.employee_id</code> (which the PK already provides if it&rsquo;s the leading column) makes the lookups fast.</p>
'''

ANSWERS[81] = r'''
<pre><code>SELECT p.project_id, p.project_name, p.status
FROM projects p
WHERE NOT EXISTS (
  SELECT 1 FROM employee_projects ep
  WHERE ep.project_id = p.project_id
)
ORDER BY p.project_name;</code></pre>

<p>Mirror image of Q80, swapping the side of the relationship. <code>NOT EXISTS</code> is the cleanest form.</p>

<p><strong>Equivalent with LEFT JOIN</strong>:</p>

<pre><code>SELECT p.project_id, p.project_name
FROM projects p
LEFT JOIN employee_projects ep ON ep.project_id = p.project_id
WHERE ep.project_id IS NULL
ORDER BY p.project_name;</code></pre>

<p><strong>With NOT IN</strong>:</p>

<pre><code>SELECT project_id, project_name
FROM projects
WHERE project_id NOT IN (
  SELECT DISTINCT project_id FROM employee_projects
  WHERE project_id IS NOT NULL
);</code></pre>

<p><strong>Filter by project status</strong> &mdash; "unassigned active projects need staffing":</p>

<pre><code>SELECT p.project_id, p.project_name, p.start_date
FROM projects p
WHERE p.status IN ('planned', 'active')
  AND NOT EXISTS (
    SELECT 1 FROM employee_projects ep
    WHERE ep.project_id = p.project_id
      AND (ep.end_date IS NULL OR ep.end_date &gt; CURDATE())
  )
ORDER BY p.start_date;</code></pre>

<p>This matters for project management dashboards &mdash; you want to surface projects that need staffing soon.</p>

<p><strong>Projects with no active assignments</strong> &mdash; might have had people in the past:</p>

<pre><code>SELECT p.project_id, p.project_name
FROM projects p
WHERE NOT EXISTS (
  SELECT 1 FROM employee_projects ep
  WHERE ep.project_id = p.project_id
    AND (ep.end_date IS NULL OR ep.end_date &gt; CURDATE())
);
-- Includes projects that were once staffed but everyone has rolled off</code></pre>

<p><strong>Combined dashboard query</strong> &mdash; a snapshot of project staffing health:</p>

<pre><code>SELECT
  p.project_id,
  p.project_name,
  p.status,
  COUNT(ep.employee_id) AS current_team_size
FROM projects p
LEFT JOIN employee_projects ep
       ON ep.project_id = p.project_id
      AND (ep.end_date IS NULL OR ep.end_date &gt; CURDATE())
GROUP BY p.project_id, p.project_name, p.status
ORDER BY current_team_size, p.start_date;
-- Projects with 0 team members at the top — these need attention</code></pre>

<p>Aggregates and filters in one trip; useful as the basis for a "staffing report" dashboard.</p>
'''

ANSWERS[82] = r'''
<pre><code>SELECT e.id, e.name, COUNT(ep.project_id) AS project_count
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
GROUP BY e.id, e.name
HAVING project_count &gt; 1
ORDER BY project_count DESC, e.name;</code></pre>

<p><code>GROUP BY</code> collapses an employee&rsquo;s assignments into one row; <code>HAVING</code> filters to those with more than one. <code>HAVING</code> (not <code>WHERE</code>) is needed because the condition references an aggregate.</p>

<p><strong>Show the project names too</strong>:</p>

<pre><code>SELECT
  e.id,
  e.name,
  COUNT(p.project_id) AS project_count,
  GROUP_CONCAT(p.project_name ORDER BY p.project_name SEPARATOR ', ') AS projects
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
JOIN projects p           ON p.project_id   = ep.project_id
GROUP BY e.id, e.name
HAVING COUNT(p.project_id) &gt; 1
ORDER BY project_count DESC, e.name;</code></pre>

<p>Sample output:</p>

<pre><code>+----+--------+---------------+----------------------------------+
| id | name   | project_count | projects                         |
+----+--------+---------------+----------------------------------+
| 12 | Carol  |       4       | Mobile, Pipeline, Q3 Plan, Dash. |
| 18 | Dave   |       3       | Mobile, Pipeline, Migration      |
| 7  | Alice  |       2       | Pipeline, Q3 Plan                |
+----+--------+---------------+----------------------------------+</code></pre>

<p><strong>Only currently-active assignments</strong>:</p>

<pre><code>SELECT e.id, e.name, COUNT(*) AS active_projects
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
WHERE ep.end_date IS NULL OR ep.end_date &gt; CURDATE()
GROUP BY e.id, e.name
HAVING active_projects &gt; 1
ORDER BY active_projects DESC;</code></pre>

<p><strong>Top N most-assigned employees</strong>:</p>

<pre><code>SELECT e.id, e.name, COUNT(ep.project_id) AS project_count
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
GROUP BY e.id, e.name
ORDER BY project_count DESC
LIMIT 10;</code></pre>

<p><strong>Average projects per employee</strong>:</p>

<pre><code>SELECT
  COUNT(DISTINCT ep.employee_id) AS staff_with_projects,
  COUNT(*)                       AS total_assignments,
  ROUND(COUNT(*) / COUNT(DISTINCT ep.employee_id), 2) AS avg_per_person
FROM employee_projects ep;</code></pre>

<p>Useful to detect over-allocation: if average is 3+, capacity is probably stretched thin.</p>
'''

ANSWERS[83] = r'''
<pre><code>SELECT
  e.id,
  e.name,
  COUNT(ep.project_id) AS project_count
FROM employees e
LEFT JOIN employee_projects ep ON ep.employee_id = e.id
GROUP BY e.id, e.name
ORDER BY project_count DESC, e.name;</code></pre>

<p><code>LEFT JOIN</code> includes employees who have no assignments &mdash; their <code>project_count</code> shows as 0. With <code>INNER JOIN</code>, those employees would be excluded entirely.</p>

<p><strong>Active-only count</strong>:</p>

<pre><code>SELECT
  e.id,
  e.name,
  COUNT(ep.project_id) AS active_count
FROM employees e
LEFT JOIN employee_projects ep
       ON ep.employee_id = e.id
      AND (ep.end_date IS NULL OR ep.end_date &gt; CURDATE())
GROUP BY e.id, e.name
ORDER BY active_count DESC;</code></pre>

<p>The <code>AND</code> condition is in the <code>ON</code> clause, not <code>WHERE</code> &mdash; this matters for <code>LEFT JOIN</code>. <code>WHERE</code> would convert it back into an inner-join behavior, dropping employees with no active projects.</p>

<p><strong>Combined: total and active counts</strong>:</p>

<pre><code>SELECT
  e.id,
  e.name,
  COUNT(*) AS total,
  SUM(CASE
        WHEN ep.end_date IS NULL OR ep.end_date &gt; CURDATE() THEN 1
        ELSE 0
      END) AS active,
  SUM(CASE
        WHEN ep.end_date &lt;= CURDATE() THEN 1
        ELSE 0
      END) AS finished
FROM employees e
LEFT JOIN employee_projects ep ON ep.employee_id = e.id
GROUP BY e.id, e.name
ORDER BY active DESC, e.name;</code></pre>

<p>Conditional <code>SUM(CASE ...)</code> counts only matching rows &mdash; a flexible aggregation pattern.</p>

<p><strong>Department totals</strong> &mdash; rolled up by department:</p>

<pre><code>SELECT
  d.department_name,
  COUNT(DISTINCT e.id) AS employees,
  COUNT(ep.project_id) AS total_assignments,
  ROUND(COUNT(ep.project_id) / NULLIF(COUNT(DISTINCT e.id), 0), 2)
                       AS avg_assignments_per_person
FROM departments d
LEFT JOIN employees e          ON e.department_id = d.department_id
LEFT JOIN employee_projects ep ON ep.employee_id  = e.id
GROUP BY d.department_id, d.department_name
ORDER BY avg_assignments_per_person DESC;</code></pre>

<p><code>NULLIF(x, 0)</code> avoids divide-by-zero for departments with no employees &mdash; division by NULL produces NULL instead of an error.</p>

<p><strong>Use for capacity planning</strong>: an "average assignments" much higher than 2-3 may indicate over-commitment; an average near 0 may indicate under-utilization.</p>
'''

ANSWERS[84] = r'''
<pre><code># From a shell, not from inside the MySQL client
mysqldump -u root -p \
  --single-transaction \
  --routines --triggers \
  company employees &gt; employees_backup.sql</code></pre>

<p><code>mysqldump</code> is the standard tool for SQL-level backups. The arguments specify database (<code>company</code>) and table (<code>employees</code>); output is a <code>.sql</code> script that recreates the table and reloads its data.</p>

<p><strong>Pure SQL alternatives</strong> &mdash; for occasional one-off snapshots within MySQL:</p>

<pre><code>-- Copy structure and data into a backup table
CREATE TABLE employees_backup LIKE employees;
INSERT INTO employees_backup SELECT * FROM employees;

-- Or in one statement (loses primary key, indexes, FKs!):
CREATE TABLE employees_backup AS SELECT * FROM employees;</code></pre>

<p>The <code>LIKE</code> form copies the schema (indexes, constraints, defaults). The <code>AS SELECT</code> form only copies columns and data &mdash; you lose the PK and indexes.</p>

<p><strong>Timestamped backup table</strong> &mdash; useful before risky operations:</p>

<pre><code>SET @backup_name = CONCAT('employees_backup_', DATE_FORMAT(NOW(), '%Y%m%d_%H%i'));
SET @sql = CONCAT('CREATE TABLE ', @backup_name, ' AS SELECT * FROM employees');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
-- Creates employees_backup_20260427_1430</code></pre>

<p>Dynamic SQL via <code>PREPARE</code>/<code>EXECUTE</code> is needed because table names can&rsquo;t be parameterized in plain SQL.</p>

<p><strong>Compressed backup</strong>:</p>

<pre><code>mysqldump -u root -p --single-transaction company employees | gzip &gt; employees.sql.gz</code></pre>

<p><strong>Backup with WHERE filter</strong> &mdash; only certain rows:</p>

<pre><code>mysqldump -u root -p --single-transaction \
  --where="hire_date &gt;= '2025-01-01'" \
  company employees &gt; recent_employees.sql</code></pre>

<p><strong>Verify the backup</strong> &mdash; restore to a test database and check row counts:</p>

<pre><code>mysql -u root -p test_restore &lt; employees_backup.sql
mysql -u root -p test_restore -e "SELECT COUNT(*) FROM employees;"</code></pre>

<p><strong>Production note</strong>: ad-hoc table-level backups via SQL are fine for one-off use. For systematic backup, use <code>mysqldump</code> at the database level, <strong>Percona XtraBackup</strong> for full-server physical backups, or your cloud provider&rsquo;s snapshot feature (RDS, Cloud SQL).</p>
'''

ANSWERS[85] = r'''
<pre><code># Restore from a mysqldump output
mysql -u root -p company &lt; employees_backup.sql</code></pre>

<p>Pipes the dumped SQL into the <code>mysql</code> client. The dump file contains <code>DROP TABLE IF EXISTS</code> + <code>CREATE TABLE</code> + <code>INSERT</code> statements that recreate the table from scratch.</p>

<p><strong>Restore a SQL-level backup table</strong> &mdash; if you used <code>CREATE TABLE backup_x AS SELECT ...</code>:</p>

<pre><code>-- Restore the data only
TRUNCATE TABLE employees;
INSERT INTO employees SELECT * FROM employees_backup;

-- Or, replacing the live table with the backup:
RENAME TABLE
  employees           TO employees_old,
  employees_backup    TO employees;
DROP TABLE employees_old;
-- Atomic: no gap where the table doesn&rsquo;t exist</code></pre>

<p>The <code>RENAME TABLE</code> trick is a zero-downtime way to swap a table.</p>

<p><strong>Faster restore for large dumps</strong> &mdash; disable index/constraint checks during the load:</p>

<pre><code>mysql -u root -p company &lt;&lt; 'EOF'
SET autocommit = 0;
SET unique_checks = 0;
SET foreign_key_checks = 0;
SOURCE employees_backup.sql;
COMMIT;
SET unique_checks = 1;
SET foreign_key_checks = 1;
EOF</code></pre>

<p>Indexes are still updated row by row; turning off the per-row checks reduces overhead substantially. Tens-of-millions-of-rows imports go from hours to minutes.</p>

<p><strong>Restore from compressed file</strong>:</p>

<pre><code>gunzip &lt; employees.sql.gz | mysql -u root -p company</code></pre>

<p><strong>Selective restore</strong> &mdash; restore from a full database dump but only the <code>employees</code> table:</p>

<pre><code># Extract just the employees section
sed -n '/^-- Table structure for table `employees`/,/^-- Table structure for table `[^e]/p' \
    full_backup.sql &gt; employees_only.sql
# Then load it
mysql -u root -p company &lt; employees_only.sql</code></pre>

<p>Crude but works for simple cases. Better tool: <code>mysqldump</code> the full database, then re-extract specific tables with <code>mysqlbinlog</code> or filter via grep/sed.</p>

<p><strong>Verify after restore</strong>:</p>

<pre><code>SELECT COUNT(*) FROM employees;
SELECT MAX(id) FROM employees;
CHECK TABLE employees;            -- structural integrity check
SHOW INDEX FROM employees;        -- expected indexes present?</code></pre>

<p><strong>Caution</strong>: <code>RESTORE</code> overwrites the target. Always take a fresh backup of whatever&rsquo;s currently live before restoring.</p>
'''

ANSWERS[86] = r'''
<pre><code>SELECT
  e.id,
  e.name,
  p.project_name,
  ep.assigned_at,
  TIMESTAMPDIFF(MONTH, ep.assigned_at, CURDATE()) AS months_on_project
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
JOIN projects p           ON p.project_id   = ep.project_id
WHERE ep.assigned_at &lt;= CURDATE() - INTERVAL 6 MONTH
  AND (ep.end_date IS NULL OR ep.end_date &gt; CURDATE())
ORDER BY ep.assigned_at;</code></pre>

<p>The <code>WHERE</code> clause filters to assignments older than 6 months that are still active. <code>TIMESTAMPDIFF(MONTH, ...)</code> shows how long they&rsquo;ve been on it for display.</p>

<p><strong>Note on <code>WHERE</code> placement for LEFT JOIN cases</strong>:</p>

<pre><code>-- This is INNER JOIN behavior (assignment exists), so WHERE is fine
WHERE ep.assigned_at &lt;= CURDATE() - INTERVAL 6 MONTH

-- For LEFT JOIN keeping all employees, conditions on ep.* must go in the ON
LEFT JOIN employee_projects ep
       ON ep.employee_id = e.id
      AND ep.assigned_at &lt;= CURDATE() - INTERVAL 6 MONTH</code></pre>

<p><strong>Rather than "since assignment date," use cumulative time</strong> &mdash; for someone who&rsquo;s been on a project, off it briefly, and on again:</p>

<pre><code>SELECT
  e.id,
  e.name,
  ep.project_id,
  SUM(DATEDIFF(
    LEAST(COALESCE(ep.end_date, CURDATE()), CURDATE()),
    ep.assigned_at
  )) AS total_days_on_project
FROM employees e
JOIN employee_projects ep ON ep.employee_id = e.id
GROUP BY e.id, e.name, ep.project_id
HAVING total_days_on_project &gt; 180
ORDER BY total_days_on_project DESC;</code></pre>

<p>This sums the duration of every assignment span (works if the same employee can have multiple rows for the same project &mdash; requires the surrogate-key form of the junction table from Q78).</p>

<p><strong>By project</strong> &mdash; long-running team members per project:</p>

<pre><code>SELECT
  p.project_name,
  e.name,
  TIMESTAMPDIFF(MONTH, ep.assigned_at, CURDATE()) AS months
FROM projects p
JOIN employee_projects ep ON ep.project_id = p.project_id
JOIN employees e          ON e.id          = ep.employee_id
WHERE ep.assigned_at &lt;= CURDATE() - INTERVAL 6 MONTH
  AND (ep.end_date IS NULL OR ep.end_date &gt; CURDATE())
ORDER BY p.project_name, months DESC;</code></pre>

<p><strong>Distribution of assignment lengths</strong> &mdash; how long do people typically stay on projects:</p>

<pre><code>SELECT
  CASE
    WHEN months &lt;  3 THEN '0-3 months'
    WHEN months &lt;  6 THEN '3-6 months'
    WHEN months &lt; 12 THEN '6-12 months'
    ELSE '12+ months'
  END AS bucket,
  COUNT(*) AS n
FROM (
  SELECT TIMESTAMPDIFF(MONTH, assigned_at, COALESCE(end_date, CURDATE())) AS months
  FROM employee_projects
) t
GROUP BY bucket
ORDER BY MIN(months);</code></pre>
'''

ANSWERS[87] = r'''
<pre><code>SELECT id, name, phone
FROM employees
WHERE phone REGEXP '^555-';</code></pre>

<p>Matches employees whose phone starts with the area code 555. <code>REGEXP</code> is more flexible than <code>LIKE</code> when you need anchors, alternation, or character classes.</p>

<p><strong>Common phone-pattern queries</strong>:</p>

<pre><code>-- Specific area code
WHERE phone REGEXP '^\\(212\\)';

-- Numbers in the format XXX-XXX-XXXX exactly
WHERE phone REGEXP '^[0-9]{3}-[0-9]{3}-[0-9]{4}$';

-- International numbers (start with +)
WHERE phone REGEXP '^\\+';

-- Numbers with extensions ('x' or 'ext')
WHERE phone REGEXP '(x|ext\\.?)\\s*[0-9]+';

-- Numbers containing '0000' (suspect placeholder)
WHERE phone LIKE '%0000%';</code></pre>

<p><strong>LIKE alternative for simple patterns</strong>:</p>

<pre><code>-- Anchored at start (uses index)
WHERE phone LIKE '555-%'

-- Contains substring (no index)
WHERE phone LIKE '%555%'</code></pre>

<p><strong>LIKE vs REGEXP</strong>:</p>

<table>
  <tr><th>Operator</th><th>Use when</th></tr>
  <tr><td><code>LIKE</code></td><td>Simple wildcards (% and _); anchored patterns can use indexes</td></tr>
  <tr><td><code>REGEXP</code></td><td>Anchors, alternation, character classes, quantifiers; never uses indexes</td></tr>
</table>

<p><strong>Validate well-formed phone numbers</strong> &mdash; data-quality check:</p>

<pre><code>SELECT id, name, phone
FROM employees
WHERE phone IS NOT NULL
  AND phone NOT REGEXP '^[+0-9 ()-]+$';
-- Find phones with characters that don&rsquo;t belong</code></pre>

<p><strong>Normalize phone numbers</strong> &mdash; strip non-digits for storage or comparison:</p>

<pre><code>-- Just digits
SELECT REGEXP_REPLACE(phone, '[^0-9]', '') AS digits_only
FROM employees;

-- Find duplicate phones ignoring formatting
SELECT digits_only, COUNT(*) AS shared
FROM (
  SELECT REGEXP_REPLACE(phone, '[^0-9]', '') AS digits_only
  FROM employees
  WHERE phone IS NOT NULL
) t
GROUP BY digits_only
HAVING shared &gt; 1;</code></pre>

<p><strong>Real-world advice</strong>: store phones in a normalized E.164 format (<code>+12125551234</code>) at insertion time. Validation and lookup queries become trivial &mdash; the database doesn&rsquo;t need to deal with formatting variation.</p>

<p>For complex phone parsing/validation, use a library like <strong>libphonenumber</strong> in your application code &mdash; SQL is not the right tool for full phone-number validation.</p>
'''

ANSWERS[88] = r'''
<pre><code>CREATE TABLE departments_history (
  history_id      INT AUTO_INCREMENT PRIMARY KEY,
  department_id   INT NOT NULL,
  old_name        VARCHAR(100),
  new_name        VARCHAR(100),
  changed_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  changed_by      INT,
  change_type     ENUM('insert', 'rename', 'delete') NOT NULL,

  INDEX idx_dept    (department_id, changed_at),
  INDEX idx_changed (changed_at),

  CONSTRAINT fk_dh_changed_by
    FOREIGN KEY (changed_by) REFERENCES employees(id)
) ENGINE=InnoDB;</code></pre>

<p>Audit table that records every change to <code>departments</code>. Each row captures both old and new values for renames, plus metadata about who made the change and when.</p>

<p><strong>Populate via a trigger on <code>departments</code></strong> &mdash; the standard automated pattern:</p>

<pre><code>DELIMITER //

CREATE TRIGGER trg_departments_after_update
AFTER UPDATE ON departments
FOR EACH ROW
BEGIN
  IF OLD.department_name &lt;&gt; NEW.department_name THEN
    INSERT INTO departments_history
      (department_id, old_name, new_name, changed_at, change_type)
    VALUES
      (NEW.department_id, OLD.department_name, NEW.department_name, NOW(), 'rename');
  END IF;
END //

CREATE TRIGGER trg_departments_after_insert
AFTER INSERT ON departments
FOR EACH ROW
BEGIN
  INSERT INTO departments_history
    (department_id, old_name, new_name, changed_at, change_type)
  VALUES
    (NEW.department_id, NULL, NEW.department_name, NOW(), 'insert');
END //

CREATE TRIGGER trg_departments_after_delete
AFTER DELETE ON departments
FOR EACH ROW
BEGIN
  INSERT INTO departments_history
    (department_id, old_name, new_name, changed_at, change_type)
  VALUES
    (OLD.department_id, OLD.department_name, NULL, NOW(), 'delete');
END //

DELIMITER ;</code></pre>

<p>Triggers fire automatically on every change &mdash; application code doesn&rsquo;t need to remember to insert audit rows.</p>

<p><strong>Common variations</strong>:</p>

<ul>
  <li><strong>Capture all columns</strong> &mdash; replicate the entire row in history. Useful but expands history table size:
<pre><code>history columns: id, department_name, manager_id, budget, status, ...</code></pre>
  </li>
  <li><strong>JSON snapshot</strong> &mdash; store full old/new state as JSON columns:
<pre><code>old_data JSON, new_data JSON</code></pre>
  Cleaner for tables that change schema over time.</li>
  <li><strong>Soft-delete pattern</strong> &mdash; add <code>deleted_at</code> to <code>departments</code> instead of using DELETE; history captures the state changes only.</li>
</ul>

<p><strong>Modern alternative</strong>: rather than a hand-rolled trigger system, use a CDC (change-data-capture) tool like <strong>Debezium</strong> that streams MySQL binlog changes to Kafka or another store &mdash; cleaner separation, no in-database triggers to maintain.</p>
'''

ANSWERS[89] = r'''
<pre><code>INSERT INTO departments_history
  (department_id, old_name, new_name, changed_at, change_type)
VALUES
  (5, 'Engineering', 'Software Engineering', NOW(), 'rename');</code></pre>

<p>If triggers are set up (Q88), changes happen automatically. This shows the manual form for cases without triggers, or for backfilling history.</p>

<p><strong>Insert from an actual change</strong> &mdash; rename a department in one transaction, capturing the old/new in history:</p>

<pre><code>START TRANSACTION;

-- Capture old name
SET @old_name = (SELECT department_name FROM departments WHERE department_id = 5);

-- Apply the rename
UPDATE departments
SET department_name = 'Software Engineering'
WHERE department_id = 5;

-- Record the history
INSERT INTO departments_history
  (department_id, old_name, new_name, changed_at, change_type, changed_by)
VALUES
  (5, @old_name, 'Software Engineering', NOW(), 'rename', @current_user_id);

COMMIT;</code></pre>

<p>The user variable <code>@old_name</code> captures the prior value before the UPDATE so it can be recorded.</p>

<p><strong>Wrap as a stored procedure</strong> &mdash; reusable rename operation:</p>

<pre><code>DELIMITER //

CREATE PROCEDURE rename_department(
  IN p_department_id INT,
  IN p_new_name      VARCHAR(100),
  IN p_changed_by    INT
)
BEGIN
  DECLARE v_old_name VARCHAR(100);

  -- Capture old name
  SELECT department_name INTO v_old_name
  FROM departments
  WHERE department_id = p_department_id;

  -- Apply the rename
  UPDATE departments
  SET department_name = p_new_name
  WHERE department_id = p_department_id;

  -- Record the history
  INSERT INTO departments_history
    (department_id, old_name, new_name, changed_at, change_type, changed_by)
  VALUES
    (p_department_id, v_old_name, p_new_name, NOW(), 'rename', p_changed_by);
END //

DELIMITER ;

-- Use it
CALL rename_department(5, 'Software Engineering', 101);</code></pre>

<p>Centralizes the logic. The application calls one procedure; can&rsquo;t forget to log the change.</p>

<p><strong>Bulk historical backfill</strong> &mdash; generate insert rows from existing data:</p>

<pre><code>-- One-time backfill: every existing department gets an "insert" history row
INSERT INTO departments_history (department_id, new_name, changed_at, change_type)
SELECT department_id, department_name, NOW(), 'insert'
FROM departments
WHERE NOT EXISTS (
  SELECT 1 FROM departments_history h
  WHERE h.department_id = departments.department_id
);</code></pre>

<p>Useful when retrofitting history tracking onto an existing system &mdash; gives every current row at least one history entry.</p>
'''

ANSWERS[90] = r'''
<pre><code>SELECT
  history_id,
  changed_at,
  change_type,
  old_name,
  new_name,
  changed_by
FROM departments_history
WHERE department_id = 5
ORDER BY changed_at DESC;</code></pre>

<p>Reverse-chronological for "most recent first" timeline display.</p>

<p><strong>Show with the changing user&rsquo;s name</strong>:</p>

<pre><code>SELECT
  h.history_id,
  h.changed_at,
  h.change_type,
  h.old_name,
  h.new_name,
  e.name AS changed_by_name
FROM departments_history h
LEFT JOIN employees e ON e.id = h.changed_by
WHERE h.department_id = 5
ORDER BY h.changed_at DESC;</code></pre>

<p><code>LEFT JOIN</code> in case the user has been deleted (FK with no <code>ON DELETE</code> action would prevent the deletion, but if it&rsquo;s <code>SET NULL</code> the join needs to handle the NULL).</p>

<p><strong>Time-windowed history</strong>:</p>

<pre><code>SELECT * FROM departments_history
WHERE department_id = 5
  AND changed_at &gt;= CURDATE() - INTERVAL 1 YEAR
ORDER BY changed_at DESC;</code></pre>

<p><strong>What was the department called as of date X?</strong></p>

<pre><code>SELECT new_name AS name_at_2024_01_01
FROM departments_history
WHERE department_id = 5
  AND changed_at &lt;= '2024-01-01'
  AND change_type IN ('insert', 'rename')
ORDER BY changed_at DESC
LIMIT 1;</code></pre>

<p>Picks the most recent name that took effect on or before the target date.</p>

<p><strong>Show all changes across all departments</strong> &mdash; an org-wide timeline:</p>

<pre><code>SELECT
  h.changed_at,
  h.change_type,
  COALESCE(h.new_name, h.old_name) AS dept,
  h.old_name AS was,
  h.new_name AS became,
  e.name     AS by_user
FROM departments_history h
LEFT JOIN employees e ON e.id = h.changed_by
ORDER BY h.changed_at DESC
LIMIT 100;</code></pre>

<p><strong>Number of changes per department</strong> &mdash; "most volatile" report:</p>

<pre><code>SELECT
  d.department_name AS current_name,
  COUNT(h.history_id) AS change_count,
  MIN(h.changed_at) AS first_change,
  MAX(h.changed_at) AS last_change
FROM departments d
LEFT JOIN departments_history h ON h.department_id = d.department_id
GROUP BY d.department_id, d.department_name
ORDER BY change_count DESC;</code></pre>

<p><strong>Performance</strong>: the index on <code>(department_id, changed_at)</code> from Q88 makes single-department history queries very fast &mdash; index range scan with no sort needed.</p>
'''

ANSWERS[91] = r'''
<pre><code>ALTER TABLE products
ADD FULLTEXT INDEX ft_description (description);</code></pre>

<p>A <strong>FULLTEXT</strong> index is a special index for text-search queries. It tokenizes the column into words and builds an inverted index, enabling fast substring/phrase searches that a regular B-tree index can&rsquo;t support.</p>

<p><strong>Multi-column FULLTEXT index</strong>:</p>

<pre><code>ALTER TABLE products
ADD FULLTEXT INDEX ft_search (name, description, tags);</code></pre>

<p>Searches that span multiple columns can use this single index.</p>

<p><strong>Define at table creation</strong>:</p>

<pre><code>CREATE TABLE products (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(200) NOT NULL,
  description TEXT,
  price       DECIMAL(10, 2) NOT NULL,

  FULLTEXT INDEX ft_description (description)
) ENGINE=InnoDB;</code></pre>

<p>InnoDB has supported FULLTEXT since MySQL 5.6 (previously MyISAM-only). Modern MySQL handles it well for medium-scale text search.</p>

<p><strong>Configuration knobs</strong>:</p>

<pre><code>-- Minimum word length (default 3 in InnoDB; words like 'AI' or 'go' are excluded by default)
SHOW VARIABLES LIKE 'innodb_ft_min_token_size';
-- Set in my.cnf and rebuild the index:
[mysqld]
innodb_ft_min_token_size = 2

-- Stopwords (words ignored: 'the', 'and', 'a', etc.)
SELECT * FROM information_schema.INNODB_FT_DEFAULT_STOPWORD;
-- Custom stopword list configurable via innodb_ft_user_stopword_table</code></pre>

<p>After changing token-size or stopword config, drop and recreate the index for it to take effect.</p>

<p><strong>Inspect tokens</strong> &mdash; MySQL exposes the index contents:</p>

<pre><code>SET GLOBAL innodb_ft_aux_table = 'company/products';
SELECT * FROM information_schema.INNODB_FT_INDEX_TABLE LIMIT 20;
-- Shows tokens, document counts, positions</code></pre>

<p><strong>When FULLTEXT is the right choice</strong>:</p>

<ul>
  <li>Searching descriptions, articles, or comments by keywords.</li>
  <li>Phrase matching ("exact phrase here").</li>
  <li>Boolean queries (+required -excluded *prefix).</li>
  <li>Relevance ranking (top results first).</li>
</ul>

<p><strong>When to look elsewhere</strong>:</p>

<ul>
  <li><strong>Tens of millions of rows or higher</strong>: FULLTEXT scales but degrades; consider a dedicated search engine.</li>
  <li><strong>Multilingual / typo-tolerant search</strong>: <strong>Elasticsearch</strong>, <strong>Meilisearch</strong>, <strong>Typesense</strong>, or <strong>OpenSearch</strong> handle stemming, synonyms, fuzzy matching, and analyzers per language.</li>
  <li><strong>Faceted filtering at scale</strong>: same.</li>
</ul>

<p>For most internal product catalogs and CMS-style content under 1M rows, MySQL FULLTEXT is good enough and saves operational complexity.</p>
'''

ANSWERS[92] = r'''
<pre><code>SELECT id, name, description,
       MATCH(description) AGAINST('wireless headphones' IN NATURAL LANGUAGE MODE) AS relevance
FROM products
WHERE MATCH(description) AGAINST('wireless headphones' IN NATURAL LANGUAGE MODE)
ORDER BY relevance DESC
LIMIT 20;</code></pre>

<p><code>MATCH ... AGAINST</code> is the FULLTEXT search syntax. The expression returns a relevance score (higher = better match); use it both as the filter and as the sort key.</p>

<p><strong>Three search modes</strong>:</p>

<table>
  <tr><th>Mode</th><th>Behavior</th></tr>
  <tr><td><code>NATURAL LANGUAGE MODE</code> (default)</td><td>Treats query as a phrase; returns relevance-ranked matches</td></tr>
  <tr><td><code>BOOLEAN MODE</code></td><td>Supports operators: + - * " ()</td></tr>
  <tr><td><code>WITH QUERY EXPANSION</code></td><td>Two-pass search: finds related results based on initial matches</td></tr>
</table>

<p><strong>BOOLEAN MODE for advanced queries</strong>:</p>

<pre><code>-- "wireless" required, "wired" excluded, "head*" matches headphones, headset, etc.
SELECT id, name FROM products
WHERE MATCH(description)
      AGAINST('+wireless -wired head*' IN BOOLEAN MODE);

-- Exact phrase
SELECT id, name FROM products
WHERE MATCH(description)
      AGAINST('"noise cancelling"' IN BOOLEAN MODE);

-- "headphones" required AND ("wireless" OR "bluetooth")
SELECT id, name FROM products
WHERE MATCH(description)
      AGAINST('+headphones +(wireless bluetooth)' IN BOOLEAN MODE);</code></pre>

<p><strong>Boolean operators</strong>:</p>

<table>
  <tr><th>Op</th><th>Effect</th></tr>
  <tr><td><code>+</code></td><td>Word must appear</td></tr>
  <tr><td><code>-</code></td><td>Word must NOT appear</td></tr>
  <tr><td><code>*</code></td><td>Wildcard (suffix)</td></tr>
  <tr><td><code>"..."</code></td><td>Exact phrase</td></tr>
  <tr><td><code>(...)</code></td><td>Group</td></tr>
  <tr><td><code>&gt;</code> / <code>&lt;</code></td><td>Increase / decrease relevance contribution</td></tr>
</table>

<p><strong>Multi-column search</strong> &mdash; column list inside MATCH must match the index:</p>

<pre><code>-- Requires: FULLTEXT INDEX (name, description, tags)
SELECT id, name
FROM products
WHERE MATCH(name, description, tags)
      AGAINST('+gaming +laptop' IN BOOLEAN MODE);</code></pre>

<p><strong>Combine with other filters</strong>:</p>

<pre><code>SELECT id, name, price
FROM products
WHERE MATCH(description) AGAINST('wireless headphones' IN NATURAL LANGUAGE MODE)
  AND price BETWEEN 50 AND 200
  AND in_stock = 1
ORDER BY MATCH(description) AGAINST('wireless headphones' IN NATURAL LANGUAGE MODE) DESC
LIMIT 20;</code></pre>

<p><strong>Caveats</strong>:</p>
<ul>
  <li>By default, words present in more than 50% of rows are treated as stopwords (this is the famous "50% threshold" &mdash; can be the source of confusing zero-result queries on small tables). Disable with <code>BOOLEAN MODE</code> or by tuning <code>innodb_ft_*</code> settings.</li>
  <li>Words shorter than <code>innodb_ft_min_token_size</code> (default 3) are ignored.</li>
  <li>Default tokenization is whitespace + ASCII; for CJK languages use the <code>ngram</code> parser.</li>
</ul>
'''

ANSWERS[93] = r'''
<pre><code>SELECT hire_date, COUNT(*) AS hires, GROUP_CONCAT(name ORDER BY name) AS people
FROM employees
GROUP BY hire_date
HAVING COUNT(*) &gt; 1
ORDER BY hire_date DESC;</code></pre>

<p>Groups employees by their exact <code>hire_date</code> and keeps groups with more than one member &mdash; common for batches like onboarding cohorts or class-of-2024 hires.</p>

<p><strong>Just the rows, with peer info</strong>:</p>

<pre><code>SELECT id, name, hire_date
FROM employees
WHERE hire_date IN (
  SELECT hire_date FROM employees
  GROUP BY hire_date
  HAVING COUNT(*) &gt; 1
)
ORDER BY hire_date DESC, name;</code></pre>

<p>Returns full employee rows for everyone whose hire_date is shared.</p>

<p><strong>Self-join to pair them up</strong>:</p>

<pre><code>SELECT
  e1.name AS person_1,
  e2.name AS person_2,
  e1.hire_date
FROM employees e1
JOIN employees e2
  ON e1.hire_date = e2.hire_date
 AND e1.id &lt; e2.id
ORDER BY e1.hire_date DESC, e1.name;</code></pre>

<p>The <code>e1.id &lt; e2.id</code> avoids duplicate (A,B)/(B,A) pairs.</p>

<p><strong>Same hire <em>month</em></strong> &mdash; if exact-date matches are too narrow:</p>

<pre><code>SELECT DATE_FORMAT(hire_date, '%Y-%m') AS hire_month,
       COUNT(*) AS hires,
       GROUP_CONCAT(name) AS people
FROM employees
GROUP BY DATE_FORMAT(hire_date, '%Y-%m')
HAVING COUNT(*) &gt; 1
ORDER BY hire_month DESC;</code></pre>

<p><strong>Anniversary detection</strong> &mdash; same hire date in different years:</p>

<pre><code>SELECT
  MONTH(hire_date) AS m,
  DAY(hire_date)   AS d,
  COUNT(*)         AS shared_anniversary,
  GROUP_CONCAT(CONCAT(name, ' (', YEAR(hire_date), ')') ORDER BY hire_date) AS people
FROM employees
GROUP BY MONTH(hire_date), DAY(hire_date)
HAVING shared_anniversary &gt; 1
ORDER BY m, d;</code></pre>

<p>People who share a hire month-and-day, regardless of year &mdash; useful for "anniversary celebration" features.</p>

<p><strong>Hire cohorts within a date window</strong> &mdash; "joined within 7 days of each other":</p>

<pre><code>SELECT e1.name AS person_1, e2.name AS person_2,
       ABS(DATEDIFF(e1.hire_date, e2.hire_date)) AS days_apart
FROM employees e1
JOIN employees e2 ON e1.id &lt; e2.id
WHERE ABS(DATEDIFF(e1.hire_date, e2.hire_date)) &lt;= 7
ORDER BY days_apart;</code></pre>

<p>Quadratic in the number of employees &mdash; only run on filtered subsets for large tables.</p>
'''

ANSWERS[94] = r'''
<pre><code>SELECT
  id,
  name,
  salary AS monthly_salary,
  salary * 12 AS annual_salary
FROM employees;</code></pre>

<p>If <code>salary</code> stores the monthly salary, multiplying by 12 gives the annualized figure. Adjust the multiplier if salary is stored differently:</p>

<table>
  <tr><th>If salary represents</th><th>Multiplier</th></tr>
  <tr><td>Hourly rate</td><td><code>* 40 * 52</code> (40-hr week, 52 weeks)</td></tr>
  <tr><td>Daily rate</td><td><code>* 5 * 52</code> (5 days/week, 52 weeks)</td></tr>
  <tr><td>Weekly</td><td><code>* 52</code></td></tr>
  <tr><td>Bi-weekly</td><td><code>* 26</code></td></tr>
  <tr><td>Semi-monthly</td><td><code>* 24</code></td></tr>
  <tr><td>Monthly</td><td><code>* 12</code></td></tr>
  <tr><td>Already annual</td><td>(no change)</td></tr>
</table>

<p><strong>Include benefits and bonuses</strong> &mdash; total annual compensation:</p>

<pre><code>SELECT
  e.id,
  e.name,
  e.salary * 12 AS base_annual,
  COALESCE(SUM(b.bonus_amount), 0) AS annual_bonus,
  e.salary * 12 + COALESCE(SUM(b.bonus_amount), 0) AS total_annual_comp
FROM employees e
LEFT JOIN bonuses b
       ON b.employee_id = e.id
      AND b.awarded_date &gt;= CURDATE() - INTERVAL 1 YEAR
GROUP BY e.id, e.name, e.salary
ORDER BY total_annual_comp DESC;</code></pre>

<p><strong>Format for display</strong>:</p>

<pre><code>SELECT
  name,
  CONCAT('$', FORMAT(salary * 12, 2)) AS annual_salary
FROM employees;
-- Returns '$72,000.00'</code></pre>

<p><code>FORMAT(value, decimals)</code> adds thousand separators and rounds to a fixed number of decimals.</p>

<p><strong>Pro-rate for partial years</strong>:</p>

<pre><code>SELECT
  e.id,
  e.name,
  e.salary * 12 AS full_year_salary,
  ROUND(e.salary * 12 *
        DATEDIFF(LEAST(CURDATE(), '2026-12-31'), GREATEST(e.hire_date, '2026-01-01'))
        / 365, 2) AS prorated_2026_salary
FROM employees e;</code></pre>

<p>Useful for HR reports where new hires don&rsquo;t earn a full year&rsquo;s salary in their first calendar year.</p>

<p><strong>Convert from annual to monthly</strong> (the other direction):</p>

<pre><code>SELECT
  name,
  annual_salary,
  ROUND(annual_salary / 12, 2)  AS monthly,
  ROUND(annual_salary / 26, 2)  AS bi_weekly,
  ROUND(annual_salary / 52 / 40, 2) AS hourly_equivalent
FROM employees;</code></pre>

<p><strong>Tax brackets</strong> &mdash; if you need taxable income calculations, use a CASE expression to apply progressive rates. Generally, doing tax math in SQL is fragile &mdash; do it in application code with proper tax libraries.</p>
'''

ANSWERS[95] = r'''
<pre><code>SELECT DISTINCT e.id, e.name, ph.old_role, ph.new_role, ph.changed_at
FROM employees e
JOIN promotions_history ph ON ph.employee_id = e.id
WHERE ph.change_type = 'promotion'
ORDER BY ph.changed_at DESC;</code></pre>

<p>This assumes a <code>promotions_history</code> audit table tracking role/title changes. Without history, "promoted" can&rsquo;t be detected from current data alone &mdash; you need the prior state.</p>

<p><strong>Schema for promotion tracking</strong>:</p>

<pre><code>CREATE TABLE role_history (
  history_id     INT AUTO_INCREMENT PRIMARY KEY,
  employee_id    INT NOT NULL,
  old_role       VARCHAR(100),
  new_role       VARCHAR(100),
  old_salary     DECIMAL(10, 2),
  new_salary     DECIMAL(10, 2),
  change_type    ENUM('hire', 'promotion', 'demotion', 'lateral', 'departure'),
  changed_at     DATETIME NOT NULL,
  approved_by    INT,
  INDEX idx_emp_date (employee_id, changed_at)
);</code></pre>

<p><strong>Promoted in last year</strong>:</p>

<pre><code>SELECT
  e.id, e.name,
  rh.old_role, rh.new_role,
  rh.old_salary, rh.new_salary,
  rh.changed_at
FROM employees e
JOIN role_history rh ON rh.employee_id = e.id
WHERE rh.change_type = 'promotion'
  AND rh.changed_at &gt;= CURDATE() - INTERVAL 1 YEAR
ORDER BY rh.changed_at DESC;</code></pre>

<p><strong>Detect promotions from salary jumps</strong> &mdash; if no explicit "promotion" tracking exists but a salary history does:</p>

<pre><code>WITH salary_changes AS (
  SELECT
    employee_id,
    salary,
    LAG(salary) OVER (PARTITION BY employee_id ORDER BY effective_date) AS prev_salary,
    effective_date
  FROM salaries
)
SELECT
  e.id, e.name,
  sc.prev_salary, sc.salary AS new_salary,
  ROUND((sc.salary - sc.prev_salary) / sc.prev_salary * 100, 1) AS pct_increase,
  sc.effective_date
FROM salary_changes sc
JOIN employees e ON e.id = sc.employee_id
WHERE sc.prev_salary IS NOT NULL
  AND (sc.salary - sc.prev_salary) / sc.prev_salary &gt; 0.10   -- &gt; 10% raise
ORDER BY sc.effective_date DESC;</code></pre>

<p>This is a heuristic &mdash; not every &gt;10% raise is a promotion (cost-of-living adjustments for everyone, market-rate corrections), and not every promotion is &gt;10%. But it&rsquo;s a useful approximation when explicit tracking is missing.</p>

<p><strong>Multiple promotions per employee</strong>:</p>

<pre><code>SELECT
  e.id,
  e.name,
  COUNT(*) AS promotion_count,
  MIN(rh.changed_at) AS first_promotion,
  MAX(rh.changed_at) AS most_recent_promotion
FROM employees e
JOIN role_history rh ON rh.employee_id = e.id
WHERE rh.change_type = 'promotion'
GROUP BY e.id, e.name
ORDER BY promotion_count DESC;</code></pre>

<p>Identifies fast-tracked employees &mdash; useful for retention analytics.</p>

<p><strong>Time between promotions</strong>:</p>

<pre><code>WITH promo AS (
  SELECT
    employee_id, changed_at,
    LAG(changed_at) OVER (PARTITION BY employee_id ORDER BY changed_at) AS prev_promo
  FROM role_history
  WHERE change_type = 'promotion'
)
SELECT
  e.name,
  TIMESTAMPDIFF(MONTH, prev_promo, changed_at) AS months_between
FROM promo p
JOIN employees e ON e.id = p.employee_id
WHERE prev_promo IS NOT NULL;</code></pre>
'''

ANSWERS[96] = r'''
<pre><code>SELECT
  d.department_name,
  ROUND(AVG(DATEDIFF(COALESCE(ah.left_at, CURDATE()), ah.joined_at)), 1) AS avg_days_in_dept
FROM department_assignments_history ah
JOIN departments d ON d.department_id = ah.department_id
GROUP BY d.department_id, d.department_name
ORDER BY avg_days_in_dept DESC;</code></pre>

<p>Assumes a history table with one row per employee-department tenure (joined_at and left_at). Each row&rsquo;s duration is the difference between the dates; <code>AVG</code> computes the mean across all completed and ongoing tenures.</p>

<p><strong>Schema for department history</strong>:</p>

<pre><code>CREATE TABLE department_assignments_history (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  employee_id     INT NOT NULL,
  department_id   INT NOT NULL,
  joined_at       DATE NOT NULL,
  left_at         DATE NULL,
  INDEX idx_dept_dates (department_id, joined_at)
);</code></pre>

<p>Each row represents a tenure span. When an employee changes departments, close the current row (set <code>left_at</code>) and insert a new one.</p>

<p><strong>Without a history table</strong> &mdash; if employees just have a <code>department_id</code> column, you can compute time since last department change only if a single audit table tracks all changes:</p>

<pre><code>SELECT
  d.department_name,
  AVG(DATEDIFF(CURDATE(), e.last_dept_change_at)) AS avg_days_in_current_dept
FROM employees e
JOIN departments d ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;</code></pre>

<p>Less accurate &mdash; doesn&rsquo;t capture historical tenures.</p>

<p><strong>In months</strong> &mdash; usually more readable than days:</p>

<pre><code>SELECT
  d.department_name,
  ROUND(AVG(TIMESTAMPDIFF(MONTH, ah.joined_at, COALESCE(ah.left_at, CURDATE()))), 1)
                                                  AS avg_months,
  COUNT(*)                                        AS tenure_records
FROM department_assignments_history ah
JOIN departments d ON d.department_id = ah.department_id
GROUP BY d.department_id, d.department_name
ORDER BY avg_months DESC;</code></pre>

<p><strong>Distinguish completed from ongoing</strong> &mdash; ongoing tenures bias the average downward (they haven&rsquo;t finished yet):</p>

<pre><code>SELECT
  d.department_name,
  ROUND(AVG(CASE WHEN ah.left_at IS NOT NULL
                 THEN TIMESTAMPDIFF(MONTH, ah.joined_at, ah.left_at) END), 1)
    AS avg_months_completed,
  ROUND(AVG(TIMESTAMPDIFF(MONTH, ah.joined_at, CURDATE())), 1)
    AS avg_months_so_far_ongoing,
  COUNT(CASE WHEN ah.left_at IS NULL THEN 1 END)
    AS currently_in_dept,
  COUNT(CASE WHEN ah.left_at IS NOT NULL THEN 1 END)
    AS departed
FROM department_assignments_history ah
JOIN departments d ON d.department_id = ah.department_id
GROUP BY d.department_id, d.department_name;</code></pre>

<p>Two distinct averages give a clearer picture: how long completed tenures lasted, and how long current people have been there.</p>

<p><strong>Per-employee tenure summary</strong>:</p>

<pre><code>SELECT
  e.id,
  e.name,
  COUNT(ah.id) AS departments_held,
  ROUND(AVG(TIMESTAMPDIFF(MONTH, ah.joined_at, COALESCE(ah.left_at, CURDATE()))), 1)
    AS avg_months_per_dept
FROM employees e
JOIN department_assignments_history ah ON ah.employee_id = e.id
GROUP BY e.id, e.name
ORDER BY departments_held DESC;</code></pre>

<p>Identifies internal mobility patterns.</p>
'''

ANSWERS[97] = r'''
<pre><code>WITH RECURSIVE subordinates AS (
  -- Anchor: the manager
  SELECT id, name, manager_id, 0 AS depth
  FROM employees
  WHERE id = 100               -- starting manager

  UNION ALL

  -- Recursive: people whose manager is in the previous level
  SELECT e.id, e.name, e.manager_id, s.depth + 1
  FROM employees e
  JOIN subordinates s ON e.manager_id = s.id
)
SELECT id, name, depth
FROM subordinates
WHERE id != 100               -- exclude the manager themselves
ORDER BY depth, name;</code></pre>

<p>Recursive CTEs (Common Table Expressions, MySQL 8+) let you walk hierarchical data &mdash; org charts, category trees, comment threads, file systems. Two parts:</p>

<ol>
  <li><strong>Anchor query</strong> (above the <code>UNION ALL</code>) &mdash; the starting rows.</li>
  <li><strong>Recursive query</strong> (below) &mdash; references the CTE itself, joining each previous level&rsquo;s output back to the source table.</li>
</ol>

<p>MySQL repeats the recursive query until it returns zero new rows.</p>

<p><strong>Sample output</strong>:</p>

<pre><code>+-----+----------+-------+
| id  | name     | depth |
+-----+----------+-------+
| 101 | Alice    |   1   |   ← reports to manager 100
| 102 | Bob      |   1   |
| 103 | Carol    |   1   |
| 201 | Dave     |   2   |   ← reports to Alice
| 202 | Eve      |   2   |
| 203 | Frank    |   2   |
| 301 | Grace    |   3   |   ← reports to Eve
+-----+----------+-------+</code></pre>

<p><strong>Display indented hierarchy</strong> &mdash; visualize the tree:</p>

<pre><code>WITH RECURSIVE org_chart AS (
  SELECT id, name, manager_id, 0 AS depth, CAST(name AS CHAR(1000)) AS path
  FROM employees WHERE manager_id IS NULL    -- top of tree

  UNION ALL

  SELECT e.id, e.name, e.manager_id, oc.depth + 1,
         CONCAT(oc.path, ' &gt; ', e.name)
  FROM employees e
  JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT
  CONCAT(REPEAT('  ', depth), name) AS indented_name,
  path
FROM org_chart
ORDER BY path;</code></pre>

<p><code>REPEAT('  ', depth)</code> creates leading spaces; the result reads as a tree:</p>

<pre><code>CEO
  CTO
    Engineering Lead
      Alice
      Bob
  CFO
    Accounting Lead
      Carol</code></pre>

<p><strong>Find ancestors instead</strong> &mdash; reverse the join direction:</p>

<pre><code>WITH RECURSIVE managers AS (
  SELECT id, name, manager_id, 0 AS depth
  FROM employees WHERE id = 301

  UNION ALL

  SELECT e.id, e.name, e.manager_id, m.depth + 1
  FROM employees e
  JOIN managers m ON e.id = m.manager_id    -- climb up
)
SELECT id, name, depth FROM managers ORDER BY depth;</code></pre>

<p>Now it&rsquo;s "everyone above this employee" &mdash; their chain of management.</p>

<p><strong>Recursion limits</strong>:</p>

<ul>
  <li><strong>cte_max_recursion_depth</strong> &mdash; default 1000. If a malformed CTE causes infinite recursion, this caps it.</li>
  <li>Set the depth column and check <code>WHERE depth &lt; 100</code> as a safety belt for unbounded data.</li>
</ul>

<p><strong>Performance</strong>: index on <code>manager_id</code> makes the recursive join efficient. For very deep or wide trees, consider materializing the closure (a separate table holding all ancestor-descendant pairs).</p>
'''

ANSWERS[98] = r'''
<pre><code>CREATE TABLE attendance (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  employee_id  INT NOT NULL,
  date         DATE NOT NULL,
  status       ENUM('present', 'absent', 'late', 'half_day', 'leave', 'wfh', 'holiday')
               NOT NULL DEFAULT 'present',
  check_in     TIME NULL,
  check_out    TIME NULL,
  notes        VARCHAR(255),
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uk_emp_date (employee_id, date),
  INDEX idx_date_status (date, status),

  CONSTRAINT fk_att_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id)
    ON DELETE CASCADE
) ENGINE=InnoDB;</code></pre>

<p>Practical attendance schema with several common extensions:</p>

<ul>
  <li><strong>UNIQUE (employee_id, date)</strong> &mdash; one record per employee per day. Prevents accidental duplicates.</li>
  <li><strong>ENUM status</strong> &mdash; constrained to known values; rejects typos like 'preset' instead of 'present'.</li>
  <li><strong>check_in / check_out</strong> &mdash; specific time-of-day for the day&rsquo;s shift. NULL if not tracked.</li>
  <li><strong>notes</strong> &mdash; free-text for "doctor&rsquo;s appointment" or "client meeting" annotations.</li>
  <li><strong>FK with ON DELETE CASCADE</strong> &mdash; deleting an employee removes their attendance records.</li>
</ul>

<p><strong>Minimal version exactly matching the question</strong>:</p>

<pre><code>CREATE TABLE attendance (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  employee_id  INT NOT NULL,
  date         DATE NOT NULL,
  status       VARCHAR(20) NOT NULL,
  UNIQUE KEY (employee_id, date)
);</code></pre>

<p><strong>Indexes for common queries</strong>:</p>

<ul>
  <li><strong>(employee_id, date)</strong> via the unique key &mdash; fast "this employee&rsquo;s attendance" queries.</li>
  <li><strong>(date, status)</strong> &mdash; fast "who was absent today?" queries.</li>
</ul>

<p><strong>Add a CHECK constraint for time logic</strong> (8.0.16+):</p>

<pre><code>ALTER TABLE attendance
ADD CONSTRAINT chk_check_times
CHECK (check_out IS NULL OR check_in IS NULL OR check_out &gt; check_in);</code></pre>

<p><strong>Storage considerations</strong>: with 1000 employees × 220 working days/year × ~50 bytes per row, you&rsquo;re at ~11M rows/year. Indexes triple that. Plan partitioning for very long retention:</p>

<pre><code>-- Optional: partition by year for easy archival
ALTER TABLE attendance
PARTITION BY RANGE (YEAR(date)) (
  PARTITION p2024 VALUES LESS THAN (2025),
  PARTITION p2025 VALUES LESS THAN (2026),
  PARTITION p2026 VALUES LESS THAN (2027),
  PARTITION pmax  VALUES LESS THAN MAXVALUE
);</code></pre>

<p>Useful for dropping old years quickly with <code>ALTER TABLE ... DROP PARTITION</code>.</p>

<p><strong>Computed columns for common derivations</strong>:</p>

<pre><code>ALTER TABLE attendance
ADD COLUMN hours_worked DECIMAL(4, 2)
  GENERATED ALWAYS AS (
    CASE
      WHEN check_in IS NOT NULL AND check_out IS NOT NULL
      THEN TIME_TO_SEC(TIMEDIFF(check_out, check_in)) / 3600
      ELSE 0
    END
  ) STORED;</code></pre>

<p>Daily hours worked computed from check-in/check-out automatically.</p>
'''

ANSWERS[99] = r'''
<pre><code>INSERT INTO attendance (employee_id, date, status, check_in, check_out)
VALUES (101, CURDATE(), 'present', '09:05:00', '17:30:00');</code></pre>

<p>Records today&rsquo;s attendance for employee 101. <code>CURDATE()</code> returns today&rsquo;s date; literal times can be passed as <code>'HH:MM:SS'</code> strings.</p>

<p><strong>From a check-in event</strong> &mdash; just the start of the day, check_out fills in later:</p>

<pre><code>INSERT INTO attendance (employee_id, date, status, check_in)
VALUES (101, CURDATE(), 'present', CURRENT_TIME);</code></pre>

<p>Then update on check-out:</p>

<pre><code>UPDATE attendance
SET check_out = CURRENT_TIME
WHERE employee_id = 101 AND date = CURDATE();</code></pre>

<p><strong>Upsert pattern</strong> &mdash; insert or update if a row already exists for today (relies on the unique key on <code>(employee_id, date)</code>):</p>

<pre><code>INSERT INTO attendance (employee_id, date, status, check_in)
VALUES (101, CURDATE(), 'present', CURRENT_TIME)
ON DUPLICATE KEY UPDATE
  check_in = VALUES(check_in),
  status   = VALUES(status);</code></pre>

<p>Useful for retry-safe check-ins that don&rsquo;t error out if the record already exists.</p>

<p><strong>Bulk daily insert</strong> &mdash; populate today&rsquo;s default attendance for everyone (e.g., a scheduled job that creates "absent" rows that get overwritten on check-in):</p>

<pre><code>INSERT INTO attendance (employee_id, date, status)
SELECT id, CURDATE(), 'absent'
FROM employees
WHERE active = 1
ON DUPLICATE KEY UPDATE id = id;
-- ON DUPLICATE KEY UPDATE id=id is a no-op trick: skip rows that already exist</code></pre>

<p><strong>Insert leave records</strong>:</p>

<pre><code>INSERT INTO attendance (employee_id, date, status, notes)
VALUES (101, '2026-05-10', 'leave', 'Personal day - approved')
ON DUPLICATE KEY UPDATE status = 'leave', notes = VALUES(notes);</code></pre>

<p><strong>Insert future planned leave for a date range</strong> &mdash; one row per day:</p>

<pre><code>INSERT INTO attendance (employee_id, date, status, notes)
SELECT 101, dt, 'leave', 'Vacation'
FROM (
  SELECT DATE_ADD('2026-06-01', INTERVAL n DAY) AS dt
  FROM (
    SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
  ) days
) range_dates;
-- Inserts 5 rows: June 1-5</code></pre>

<p><strong>Application-side approach</strong>:</p>

<pre><code>// Node.js with mysql2
await conn.execute(
  `INSERT INTO attendance (employee_id, date, status, check_in)
   VALUES (?, CURDATE(), ?, CURRENT_TIME)
   ON DUPLICATE KEY UPDATE check_in = VALUES(check_in)`,
  [employeeId, status]
);</code></pre>

<p>Always use prepared statements to prevent SQL injection.</p>
'''

ANSWERS[100] = r'''
<pre><code>SELECT date, status, check_in, check_out, notes
FROM attendance
WHERE employee_id = 101
  AND date &gt;= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND date &lt;  DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
ORDER BY date;</code></pre>

<p><code>DATE_FORMAT(CURDATE(), '%Y-%m-01')</code> returns the first of the current month; the upper bound is the first of next month (exclusive). The half-open range matches the whole month and uses an index on <code>date</code>.</p>

<p><strong>Equivalent with explicit functions</strong>:</p>

<pre><code>SELECT date, status, check_in, check_out
FROM attendance
WHERE employee_id = 101
  AND YEAR(date)  = YEAR(CURDATE())
  AND MONTH(date) = MONTH(CURDATE())
ORDER BY date;</code></pre>

<p>Equivalent results, but the <code>YEAR()</code> / <code>MONTH()</code> wrapping prevents index usage on <code>date</code> &mdash; slower on big tables.</p>

<p><strong>With derived columns</strong>:</p>

<pre><code>SELECT
  date,
  status,
  check_in,
  check_out,
  CASE
    WHEN check_in &lt;= '09:00:00' THEN 'on time'
    WHEN check_in &lt;= '09:30:00' THEN 'slightly late'
    ELSE 'late'
  END AS punctuality,
  TIME_TO_SEC(TIMEDIFF(check_out, check_in)) / 3600 AS hours_worked
FROM attendance
WHERE employee_id = 101
  AND date &gt;= DATE_FORMAT(CURDATE(), '%Y-%m-01')
ORDER BY date;</code></pre>

<p><strong>Monthly summary</strong>:</p>

<pre><code>SELECT
  COUNT(*)                                   AS total_days_recorded,
  SUM(status = 'present')                    AS days_present,
  SUM(status = 'absent')                     AS days_absent,
  SUM(status = 'late')                       AS days_late,
  SUM(status = 'leave')                      AS days_leave,
  SUM(status = 'wfh')                        AS days_wfh,
  ROUND(AVG(TIME_TO_SEC(TIMEDIFF(check_out, check_in)) / 3600), 2) AS avg_hours
FROM attendance
WHERE employee_id = 101
  AND date &gt;= DATE_FORMAT(CURDATE(), '%Y-%m-01');</code></pre>

<p>The <code>SUM(condition)</code> idiom counts rows where the boolean is true (boolean evaluates to 1).</p>

<p><strong>For a different month</strong> &mdash; pass year/month as parameters:</p>

<pre><code>-- April 2026
SELECT date, status, check_in, check_out
FROM attendance
WHERE employee_id = 101
  AND date &gt;= '2026-04-01'
  AND date &lt;  '2026-05-01'
ORDER BY date;</code></pre>

<p><strong>Department-wide attendance for the month</strong>:</p>

<pre><code>SELECT
  d.department_name,
  COUNT(DISTINCT a.employee_id)                  AS employees_with_records,
  SUM(a.status = 'present')                      AS total_present_days,
  SUM(a.status = 'absent')                       AS total_absent_days,
  ROUND(SUM(a.status = 'present') /
        COUNT(*) * 100, 1)                       AS attendance_rate_pct
FROM attendance a
JOIN employees e   ON e.id = a.employee_id
JOIN departments d ON d.department_id = e.department_id
WHERE a.date &gt;= DATE_FORMAT(CURDATE(), '%Y-%m-01')
  AND a.date &lt;  DATE_FORMAT(CURDATE() + INTERVAL 1 MONTH, '%Y-%m-01')
GROUP BY d.department_id, d.department_name
ORDER BY attendance_rate_pct DESC;</code></pre>

<p><strong>Calendar-style display</strong> &mdash; one row per day with empty rows for missing dates: typically generated in application code by joining a calendar dimension table.</p>
'''
