"""MySQL Basic — Q1-100 detailed answers.

Style: Basic-level conventions. 80-150 word concise prose explanations.
Simple SQL examples. Comparison tables for related concepts.
Beginner-friendly tone. ~1,500-2,500 chars per answer.
"""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''
<p><strong>MySQL</strong> is an open-source <strong>relational database management system (RDBMS)</strong> &mdash; software that stores, organizes, and retrieves data in tables made of rows and columns. Originally created in 1995, it&rsquo;s now owned by Oracle and remains one of the most widely deployed databases in the world, powering apps from small blogs to large companies (Facebook, Twitter, YouTube all use or have used it).</p>

<p>You communicate with MySQL using <strong>SQL</strong> (Structured Query Language) &mdash; a standardized language for asking the database to <em>create</em>, <em>read</em>, <em>update</em>, and <em>delete</em> data.</p>

<pre><code>SELECT name, email FROM users WHERE active = 1;</code></pre>

<p>Key features that make MySQL popular:</p>
<ul>
  <li><strong>Free and open-source</strong> (Community Edition); paid Enterprise tier exists.</li>
  <li><strong>Cross-platform</strong> &mdash; Linux, Windows, macOS.</li>
  <li><strong>Fast for read-heavy workloads</strong>; mature query optimizer.</li>
  <li><strong>Reliable</strong> &mdash; transactions, replication, backup tooling.</li>
  <li><strong>Huge ecosystem</strong> &mdash; drivers for every language, tons of tutorials.</li>
</ul>

<p>MariaDB is a community-developed fork of MySQL that&rsquo;s mostly compatible &mdash; you&rsquo;ll see it as a drop-in replacement on many Linux distributions.</p>
'''

ANSWERS[2] = r'''
<p>Installation depends on your operating system &mdash; the official MySQL installers are available at <code>dev.mysql.com/downloads</code>.</p>

<p><strong>Windows</strong>: download the <em>MySQL Installer</em>, run it, and pick <em>Server only</em> or <em>Developer Default</em> (which includes Workbench, the GUI client). The wizard walks you through setting a root password and starting the service.</p>

<p><strong>macOS</strong>: easiest is Homebrew:</p>
<pre><code>brew install mysql
brew services start mysql</code></pre>

<p><strong>Linux (Ubuntu/Debian)</strong>:</p>
<pre><code>sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql_secure_installation</code></pre>

<p>The last command walks you through hardening: setting the root password, removing anonymous users, disallowing remote root login, and removing the test database.</p>

<p><strong>Docker</strong> is the modern preferred option for local development &mdash; you don&rsquo;t pollute your machine, and you can run multiple versions side by side:</p>
<pre><code>docker run --name mysql-dev -e MYSQL_ROOT_PASSWORD=secret \
  -p 3306:3306 -d mysql:8.0</code></pre>

<p>Verify the install by running <code>mysql --version</code> and connecting via <code>mysql -u root -p</code>.</p>
'''

ANSWERS[3] = r'''
<p>How you control the MySQL service depends on the operating system &mdash; MySQL runs as a background <em>service</em> (Windows) or <em>daemon</em> (Linux/macOS) called <code>mysqld</code>.</p>

<p><strong>Linux (systemd)</strong>:</p>
<pre><code>sudo systemctl start mysql
sudo systemctl stop mysql
sudo systemctl restart mysql
sudo systemctl status mysql            # check if running
sudo systemctl enable mysql            # auto-start on boot</code></pre>

<p><strong>macOS (Homebrew)</strong>:</p>
<pre><code>brew services start mysql
brew services stop mysql
brew services restart mysql
brew services list                     # show status</code></pre>

<p><strong>Windows (PowerShell as administrator)</strong>:</p>
<pre><code>net start MySQL80
net stop MySQL80</code></pre>

<p>Or open <em>Services</em> from the Start menu and find <em>MySQL80</em> to start/stop with a click.</p>

<p><strong>Docker</strong>:</p>
<pre><code>docker stop mysql-dev
docker start mysql-dev</code></pre>

<p>Always stop MySQL gracefully &mdash; abrupt termination can leave tables in an inconsistent state. The service stop commands above wait for in-progress transactions to finish before shutting down.</p>
'''

ANSWERS[4] = r'''
<p>The default MySQL port is <strong>3306</strong>. Clients connect to the server on this port using TCP/IP. When you run <code>mysql -u root -p</code> without specifying a host, it tries to connect via local socket (faster); when you connect over the network, it uses 3306 by default.</p>

<pre><code># Explicit host and port
mysql -h db.example.com -P 3306 -u admin -p

# In a connection string (Node.js, Python, etc.)
mysql://user:pass@db.example.com:3306/mydb</code></pre>

<p><strong>Changing the port</strong> &mdash; edit <code>my.cnf</code> (Linux/macOS) or <code>my.ini</code> (Windows) and set:</p>
<pre><code>[mysqld]
port=3307</code></pre>

<p>Then restart the service. You might do this when running multiple MySQL instances on the same machine, or to avoid conflicts with another database.</p>

<p><strong>Common related ports</strong>:</p>
<table>
  <tr><th>Port</th><th>Service</th></tr>
  <tr><td>3306</td><td>MySQL (default)</td></tr>
  <tr><td>33060</td><td>MySQL X Protocol (newer NoSQL-like API)</td></tr>
  <tr><td>5432</td><td>PostgreSQL (different DB)</td></tr>
  <tr><td>1433</td><td>SQL Server</td></tr>
</table>

<p>Firewall rules must allow 3306 if you connect remotely, but it&rsquo;s generally safer to keep it closed and connect through SSH tunnels or a VPN.</p>
'''

ANSWERS[5] = r'''
<p>Use the <code>CREATE DATABASE</code> statement &mdash; it sets up an empty container where you&rsquo;ll later define tables.</p>

<pre><code>CREATE DATABASE shop;</code></pre>

<p>To avoid an error if the database already exists:</p>
<pre><code>CREATE DATABASE IF NOT EXISTS shop;</code></pre>

<p>You can specify the character set and collation up front &mdash; recommended for international apps:</p>
<pre><code>CREATE DATABASE shop
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;</code></pre>

<p><strong>utf8mb4</strong> supports the full Unicode range including emoji and supplementary characters. Plain <code>utf8</code> in MySQL is a legacy 3-byte version that doesn&rsquo;t handle 4-byte characters &mdash; always prefer <code>utf8mb4</code> in modern apps.</p>

<p>After creating, switch to the new database and start defining tables:</p>
<pre><code>USE shop;
CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(100));</code></pre>

<p>To verify, list all databases:</p>
<pre><code>SHOW DATABASES;</code></pre>

<p>Note: in MySQL, the terms "<em>database</em>" and "<em>schema</em>" are synonymous (unlike PostgreSQL, where they differ). Permission to create databases requires the <code>CREATE</code> privilege, which root has by default.</p>
'''

ANSWERS[6] = r'''
<p>Use the <code>DROP DATABASE</code> statement &mdash; this <strong>permanently deletes</strong> the database <em>and all tables, data, and procedures inside it</em>. There is no recycle bin; back up first if there&rsquo;s any chance you&rsquo;ll need the data.</p>

<pre><code>DROP DATABASE shop;</code></pre>

<p>Avoid an error if the database doesn&rsquo;t exist:</p>
<pre><code>DROP DATABASE IF EXISTS shop;</code></pre>

<p><strong>Always back up before dropping</strong>:</p>
<pre><code>mysqldump -u root -p shop &gt; shop_backup.sql
DROP DATABASE shop;</code></pre>

<p>Common mistakes:</p>
<ul>
  <li>Running <code>DROP DATABASE</code> on production by accident &mdash; protect with restricted users; production accounts shouldn&rsquo;t have <code>DROP</code> privilege.</li>
  <li>Confusing <code>DROP DATABASE</code> with <code>DROP TABLE</code> &mdash; the first nukes everything; the second removes one table.</li>
  <li>Forgetting that <code>DROP</code> commits any open transaction immediately &mdash; you can&rsquo;t roll it back.</li>
</ul>

<p>Required privileges: <code>DROP</code> permission on the database. To check what databases your user can drop, look at the privilege grants:</p>
<pre><code>SHOW GRANTS FOR 'username'@'host';</code></pre>
'''

ANSWERS[7] = r'''
<p>Use <code>CREATE TABLE</code> to define a new table &mdash; specify the column names, their data types, and any constraints.</p>

<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  age INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);</code></pre>

<p>Breaking down the parts:</p>
<ul>
  <li><strong>Column name + data type</strong> &mdash; <code>email VARCHAR(255)</code> means a variable-length string up to 255 characters.</li>
  <li><strong>Constraints</strong> &mdash; rules the database enforces:
    <ul>
      <li><code>PRIMARY KEY</code> &mdash; unique row identifier.</li>
      <li><code>NOT NULL</code> &mdash; column must have a value.</li>
      <li><code>UNIQUE</code> &mdash; no two rows can share this value.</li>
      <li><code>DEFAULT</code> &mdash; value used if none provided.</li>
    </ul>
  </li>
  <li><strong><code>AUTO_INCREMENT</code></strong> &mdash; database picks the next number for you, starting from 1.</li>
</ul>

<p>To avoid errors when re-running scripts:</p>
<pre><code>CREATE TABLE IF NOT EXISTS users (...);</code></pre>

<p>You can specify the storage engine and character set on the table:</p>
<pre><code>CREATE TABLE users (...) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;</code></pre>

<p><strong>InnoDB</strong> is the default modern engine &mdash; it supports transactions and foreign keys.</p>
'''

ANSWERS[8] = r'''
<p>Use <code>DROP TABLE</code> to permanently remove a table along with all its data, indexes, and triggers. Like <code>DROP DATABASE</code>, this is irreversible &mdash; back up first if you may need the data.</p>

<pre><code>DROP TABLE users;</code></pre>

<p>To avoid an error if the table doesn&rsquo;t exist:</p>
<pre><code>DROP TABLE IF EXISTS users;</code></pre>

<p>Drop multiple tables in one statement:</p>
<pre><code>DROP TABLE IF EXISTS orders, order_items, cart;</code></pre>

<p><strong>DROP vs TRUNCATE vs DELETE</strong> &mdash; three different ways to "remove" data:</p>
<table>
  <tr><th>Command</th><th>Effect</th></tr>
  <tr><td><code>DROP TABLE</code></td><td>Removes the table itself (structure + data)</td></tr>
  <tr><td><code>TRUNCATE TABLE</code></td><td>Removes all rows; keeps structure; resets AUTO_INCREMENT</td></tr>
  <tr><td><code>DELETE FROM</code></td><td>Removes rows matching WHERE; can be rolled back in a transaction</td></tr>
</table>

<p><strong>Foreign key gotcha</strong>: if other tables reference your table via foreign keys, the DROP fails until those references are removed or the foreign-key constraints dropped. Either drop the dependent tables first or temporarily disable checks:</p>
<pre><code>SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE users;
SET FOREIGN_KEY_CHECKS = 1;</code></pre>

<p>Required privilege: <code>DROP</code> on the table.</p>
'''

ANSWERS[9] = r'''
<p>MySQL data types fall into a few main categories:</p>

<p><strong>Numeric types</strong>:</p>
<table>
  <tr><th>Type</th><th>Range / Description</th></tr>
  <tr><td><code>TINYINT</code></td><td>-128 to 127 (1 byte)</td></tr>
  <tr><td><code>INT</code></td><td>~-2 billion to 2 billion (4 bytes); standard integer</td></tr>
  <tr><td><code>BIGINT</code></td><td>Very large integers (8 bytes)</td></tr>
  <tr><td><code>DECIMAL(p, s)</code></td><td>Exact decimal &mdash; use for money</td></tr>
  <tr><td><code>FLOAT</code> / <code>DOUBLE</code></td><td>Approximate decimals; not for currency</td></tr>
</table>

<p><strong>String types</strong>:</p>
<table>
  <tr><th>Type</th><th>Description</th></tr>
  <tr><td><code>CHAR(n)</code></td><td>Fixed-length; padded with spaces</td></tr>
  <tr><td><code>VARCHAR(n)</code></td><td>Variable-length up to n; most common</td></tr>
  <tr><td><code>TEXT</code></td><td>Long text (up to 65,535 chars)</td></tr>
  <tr><td><code>JSON</code></td><td>Native JSON column with validation</td></tr>
</table>

<p><strong>Date and time types</strong>:</p>
<table>
  <tr><th>Type</th><th>Description</th></tr>
  <tr><td><code>DATE</code></td><td>Date only (YYYY-MM-DD)</td></tr>
  <tr><td><code>DATETIME</code></td><td>Date + time, no time zone</td></tr>
  <tr><td><code>TIMESTAMP</code></td><td>Date + time, stored in UTC, converted on display</td></tr>
  <tr><td><code>TIME</code></td><td>Time only (HH:MM:SS)</td></tr>
</table>

<p><strong>Other types</strong>: <code>BOOLEAN</code> (alias for TINYINT(1)), <code>ENUM</code> (predefined list), <code>BLOB</code> (binary data).</p>

<p>Pick the smallest type that fits your data &mdash; smaller types mean less storage, faster queries, and smaller indexes.</p>
'''

ANSWERS[10] = r'''
<p>Use the <code>INSERT</code> statement. The most common form lists columns explicitly and provides values:</p>

<pre><code>INSERT INTO users (email, name, age)
VALUES ('alice@example.com', 'Alice', 28);</code></pre>

<p>Insert multiple rows in one statement &mdash; faster than running 10 separate inserts:</p>
<pre><code>INSERT INTO users (email, name, age) VALUES
  ('bob@example.com', 'Bob', 35),
  ('carol@example.com', 'Carol', 42),
  ('dave@example.com', 'Dave', 19);</code></pre>

<p>If you provide values for <em>every</em> column in order, you can omit the column list (not recommended &mdash; brittle if columns change):</p>
<pre><code>INSERT INTO users VALUES (NULL, 'eve@example.com', 'Eve', 25, NOW());</code></pre>

<p><strong>Insert from another table</strong>:</p>
<pre><code>INSERT INTO archived_users (email, name)
SELECT email, name FROM users WHERE last_login &lt; '2020-01-01';</code></pre>

<p><strong>Variants</strong>:</p>
<ul>
  <li><code>INSERT IGNORE</code> &mdash; skip rows that would cause errors (e.g., duplicate keys).</li>
  <li><code>INSERT ... ON DUPLICATE KEY UPDATE</code> &mdash; insert or update if row already exists.</li>
  <li><code>REPLACE INTO</code> &mdash; deletes existing row with same primary/unique key, then inserts.</li>
</ul>

<p>From application code, always use <strong>parameterized queries</strong> (<code>?</code> placeholders) &mdash; never concatenate user input into SQL strings, or you create a SQL injection vulnerability.</p>
'''

ANSWERS[11] = r'''
<p>Use the <code>UPDATE</code> statement with a <code>WHERE</code> clause to modify existing rows. The <code>SET</code> clause lists columns to change.</p>

<pre><code>UPDATE users
SET age = 29
WHERE email = 'alice@example.com';</code></pre>

<p>Update multiple columns at once:</p>
<pre><code>UPDATE users
SET name = 'Alice Smith', age = 29
WHERE id = 1;</code></pre>

<p>Update many rows matching a condition:</p>
<pre><code>UPDATE products
SET price = price * 1.10
WHERE category = 'books';</code></pre>

<p><strong>Critical safety rule</strong>: <em>always include a <code>WHERE</code> clause</em>. Without one, every row in the table is updated:</p>
<pre><code>-- DANGER: updates ALL users to age 30!
UPDATE users SET age = 30;</code></pre>

<p>To be extra safe, use <code>SET SQL_SAFE_UPDATES = 1</code> &mdash; this prevents updates that don&rsquo;t use a key column in the WHERE clause. MySQL Workbench enables this by default.</p>

<p><strong>Test before updating</strong>: run the equivalent <code>SELECT</code> first to see which rows would be affected:</p>
<pre><code>SELECT * FROM users WHERE email = 'alice@example.com';
-- looks right? then run the UPDATE
UPDATE users SET age = 29 WHERE email = 'alice@example.com';</code></pre>

<p>Wrap risky updates in a transaction so you can roll back if it goes wrong.</p>
'''

ANSWERS[12] = r'''
<p>Use <code>DELETE FROM</code> with a <code>WHERE</code> clause to remove specific rows.</p>

<pre><code>DELETE FROM users
WHERE id = 42;</code></pre>

<p>Delete multiple rows matching a condition:</p>
<pre><code>DELETE FROM orders
WHERE created_at &lt; '2020-01-01';</code></pre>

<p><strong>Critical safety rule</strong>: <em>always include <code>WHERE</code></em>. Without it, every row in the table disappears:</p>
<pre><code>-- DANGER: deletes ALL rows!
DELETE FROM users;</code></pre>

<p>Run the <code>SELECT</code> equivalent first to verify the rows you&rsquo;re about to delete:</p>
<pre><code>SELECT * FROM orders WHERE created_at &lt; '2020-01-01';
-- right rows? proceed
DELETE FROM orders WHERE created_at &lt; '2020-01-01';</code></pre>

<p><strong>DELETE vs TRUNCATE vs DROP</strong>:</p>
<table>
  <tr><th>Command</th><th>Use when</th></tr>
  <tr><td><code>DELETE FROM ... WHERE ...</code></td><td>Removing some rows; transactional; can roll back</td></tr>
  <tr><td><code>TRUNCATE TABLE</code></td><td>Emptying a table fast; auto-resets AUTO_INCREMENT</td></tr>
  <tr><td><code>DROP TABLE</code></td><td>Removing the table entirely</td></tr>
</table>

<p>Wrap dangerous deletes in a transaction:</p>
<pre><code>START TRANSACTION;
DELETE FROM orders WHERE customer_id = 5;
-- check the result
ROLLBACK;     -- or COMMIT if happy</code></pre>

<p>Many apps use <em>soft deletes</em> instead &mdash; add a <code>deleted_at</code> column and update it rather than physically removing rows. Lets you recover and audit.</p>
'''

ANSWERS[13] = r'''
<p>Use the <code>SELECT</code> statement &mdash; the most-used SQL command. Specify which columns you want and from which table.</p>

<pre><code>SELECT name, email FROM users;</code></pre>

<p>Use <code>*</code> to select all columns (handy for exploration; avoid in production code &mdash; brittle if columns change):</p>
<pre><code>SELECT * FROM users;</code></pre>

<p>Filter with <code>WHERE</code>:</p>
<pre><code>SELECT name, email
FROM users
WHERE age &gt;= 18 AND active = 1;</code></pre>

<p>Sort results with <code>ORDER BY</code>:</p>
<pre><code>SELECT * FROM users
ORDER BY created_at DESC;</code></pre>

<p>Limit how many rows come back &mdash; essential for large tables:</p>
<pre><code>SELECT * FROM products
ORDER BY price DESC
LIMIT 10;</code></pre>

<p>Putting it all together &mdash; this is the canonical SELECT shape:</p>
<pre><code>SELECT column1, column2
FROM table_name
WHERE condition
ORDER BY column1
LIMIT 10;</code></pre>

<p><strong>Common operators in <code>WHERE</code></strong>: <code>=</code>, <code>!=</code> or <code>&lt;&gt;</code>, <code>&lt;</code>, <code>&gt;</code>, <code>BETWEEN</code>, <code>LIKE</code>, <code>IN</code>, <code>IS NULL</code>, <code>AND</code>, <code>OR</code>.</p>

<p>For app code, always use parameterized queries to prevent SQL injection:</p>
<pre><code>// Node.js with mysql2
const [rows] = await conn.execute(
  'SELECT * FROM users WHERE email = ?',
  [userEmail]
);</code></pre>
'''

ANSWERS[14] = r'''
<p>A <strong>primary key</strong> is a column (or combination of columns) that uniquely identifies each row in a table. Two rules:</p>
<ol>
  <li>Values must be <strong>unique</strong> &mdash; no two rows can share a primary key value.</li>
  <li>Values cannot be <strong>NULL</strong>.</li>
</ol>

<p>Each table can have only <em>one</em> primary key. It&rsquo;s how you reliably look up a specific row.</p>

<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255),
  name VARCHAR(100)
);

INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice');
-- id is auto-assigned: 1
SELECT * FROM users WHERE id = 1;</code></pre>

<p><strong>Why primary keys matter</strong>:</p>
<ul>
  <li><strong>Identity</strong> &mdash; one canonical ID for each row that other tables can reference.</li>
  <li><strong>Performance</strong> &mdash; MySQL automatically creates an index on the primary key, making lookups fast.</li>
  <li><strong>Foreign keys</strong> &mdash; other tables link to this row via the PK.</li>
</ul>

<p><strong>Choosing a primary key</strong>:</p>
<table>
  <tr><th>Choice</th><th>Pros / Cons</th></tr>
  <tr><td><code>INT AUTO_INCREMENT</code></td><td>Simple, fast, small &mdash; the default choice</td></tr>
  <tr><td><code>BIGINT AUTO_INCREMENT</code></td><td>For tables expected to exceed 2 billion rows</td></tr>
  <tr><td>UUID (CHAR(36))</td><td>Works across distributed systems; larger; slower index</td></tr>
  <tr><td>Natural key (e.g., email)</td><td>Avoid &mdash; emails change; PKs shouldn&rsquo;t</td></tr>
</table>

<p>Always have a primary key on every table.</p>
'''

ANSWERS[15] = r'''
<p>You can declare a primary key three ways: inline at column definition, as a separate clause, or with <code>ALTER TABLE</code> after creation.</p>

<p><strong>Inline (most common, single-column)</strong>:</p>
<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255),
  name VARCHAR(100)
);</code></pre>

<p><strong>As a separate clause (required for composite keys)</strong>:</p>
<pre><code>CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  quantity INT,
  PRIMARY KEY (order_id, product_id)   -- composite key
);</code></pre>

<p><strong>Add to existing table with <code>ALTER TABLE</code></strong>:</p>
<pre><code>ALTER TABLE users
ADD PRIMARY KEY (id);</code></pre>

<p><strong>Remove a primary key</strong>:</p>
<pre><code>ALTER TABLE users
DROP PRIMARY KEY;</code></pre>

<p>If you need to change which column is the primary key, drop the old one first, then add the new one in a single ALTER statement (or transaction) to avoid leaving the table without a key.</p>

<p><strong>Pairing with <code>AUTO_INCREMENT</code></strong>: this is the typical "id column" pattern &mdash; MySQL picks the next number automatically:</p>
<pre><code>CREATE TABLE products (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100)
);</code></pre>

<p>The PK column is automatically <code>NOT NULL</code>; no need to declare it. MySQL also auto-creates a B-tree index on the PK for fast lookups.</p>
'''

ANSWERS[16] = r'''
<p>A <strong>foreign key</strong> is a column (or set of columns) in one table that <em>references</em> the primary key of another table &mdash; this enforces a relationship between the two tables. The database refuses to insert rows whose foreign key value doesn&rsquo;t match an existing row in the referenced table.</p>

<pre><code>CREATE TABLE customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  total DECIMAL(10, 2),
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);</code></pre>

<p>If you try to insert an order with <code>customer_id = 999</code> when customer 999 doesn&rsquo;t exist, MySQL throws an error. This is called <strong>referential integrity</strong>.</p>

<p><strong>Why foreign keys matter</strong>:</p>
<ul>
  <li>Prevent <strong>orphan rows</strong> (an order pointing to a nonexistent customer).</li>
  <li>Document the table relationships in the schema itself.</li>
  <li>Enable cascading actions like "delete the customer, delete their orders too."</li>
</ul>

<p><strong>Cascade actions</strong> &mdash; what to do when the referenced row is deleted/updated:</p>
<pre><code>FOREIGN KEY (customer_id) REFERENCES customers(id)
  ON DELETE CASCADE   -- delete orders too when customer deleted
  ON UPDATE CASCADE   -- update if customer.id changes</code></pre>

<p>Other options: <code>SET NULL</code> (FK becomes NULL), <code>RESTRICT</code> (refuse the parent delete), <code>NO ACTION</code> (similar to RESTRICT).</p>

<p>Foreign keys require the InnoDB storage engine (the default).</p>
'''

ANSWERS[17] = r'''
<p>Three ways to declare a foreign key: inline in <code>CREATE TABLE</code>, as a table-level constraint, or via <code>ALTER TABLE</code> after creation.</p>

<p><strong>In CREATE TABLE (table-level constraint)</strong>:</p>
<pre><code>CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  total DECIMAL(10, 2),
  CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);</code></pre>

<p>Naming the constraint (<code>fk_orders_customer</code>) makes it easy to reference if you need to drop it later.</p>

<p><strong>Add to existing table</strong>:</p>
<pre><code>ALTER TABLE orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY (customer_id) REFERENCES customers(id);</code></pre>

<p><strong>Drop a foreign key</strong>:</p>
<pre><code>ALTER TABLE orders
DROP FOREIGN KEY fk_orders_customer;</code></pre>

<p><strong>Requirements</strong>:</p>
<ul>
  <li>Both tables must use the <strong>InnoDB</strong> storage engine.</li>
  <li>Referenced column must be a primary key or have a unique index.</li>
  <li>Both columns must be the same data type (and same charset/collation for strings).</li>
</ul>

<p><strong>Common pitfalls</strong>:</p>
<ul>
  <li>Existing data violating the constraint &mdash; the ALTER will fail. Clean up orphans first.</li>
  <li>Forgetting to index the foreign key column for performance &mdash; MySQL auto-creates an index, but verify with <code>SHOW INDEX FROM table</code>.</li>
  <li>Setting <code>ON DELETE CASCADE</code> too liberally &mdash; can wipe more rows than expected.</li>
</ul>
'''

ANSWERS[18] = r'''
<p>An <strong>index</strong> is a separate data structure (typically a B-tree) that MySQL maintains to make lookups fast &mdash; like the index at the back of a book. Without one, MySQL must scan every row of the table to find matching values; with one, it can jump directly to the right rows.</p>

<pre><code>-- Without index — full table scan
SELECT * FROM users WHERE email = 'alice@example.com';
-- Slow on a 10M-row table

-- With index on email
CREATE INDEX idx_users_email ON users(email);
-- Same query now uses the index — milliseconds</code></pre>

<p><strong>When to add indexes</strong>:</p>
<ul>
  <li>Columns frequently in <code>WHERE</code> clauses.</li>
  <li>Columns used in <code>JOIN</code> conditions.</li>
  <li>Columns in <code>ORDER BY</code> (avoids sorting).</li>
  <li>Foreign key columns (MySQL auto-creates these in InnoDB).</li>
</ul>

<p><strong>Trade-offs</strong>:</p>
<table>
  <tr><th>Pro</th><th>Con</th></tr>
  <tr><td>Fast SELECTs</td><td>Slower INSERT / UPDATE / DELETE (index must be maintained)</td></tr>
  <tr><td>Fast JOINs</td><td>Extra disk space</td></tr>
  <tr><td>Fast ORDER BY</td><td>Useless if column has very few unique values (e.g., gender)</td></tr>
</table>

<p><strong>Don&rsquo;t over-index</strong>. Each index slows writes and uses storage. Profile with <code>EXPLAIN</code> to see if your query benefits before adding one.</p>

<p>Special index types: <strong>UNIQUE</strong> (enforces uniqueness), <strong>FULLTEXT</strong> (text search), <strong>composite</strong> (multiple columns).</p>
'''

ANSWERS[19] = r'''
<p>Use <code>CREATE INDEX</code> to add an index after the table exists, or include it in <code>CREATE TABLE</code> upfront.</p>

<p><strong>Standalone CREATE INDEX</strong>:</p>
<pre><code>CREATE INDEX idx_users_email ON users(email);</code></pre>

<p><strong>In CREATE TABLE</strong>:</p>
<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255),
  name VARCHAR(100),
  INDEX idx_email (email)
);</code></pre>

<p><strong>Composite index (multiple columns)</strong>:</p>
<pre><code>CREATE INDEX idx_users_status_created
ON users(status, created_at);</code></pre>

<p>Order of columns matters &mdash; the index helps queries that filter by <code>status</code> alone, or <code>status</code> + <code>created_at</code>, but not <code>created_at</code> alone (leftmost-prefix rule).</p>

<p><strong>Unique index</strong> &mdash; like an index but also enforces uniqueness:</p>
<pre><code>CREATE UNIQUE INDEX idx_users_email ON users(email);</code></pre>

<p><strong>Full-text index</strong> &mdash; for text search:</p>
<pre><code>CREATE FULLTEXT INDEX idx_articles_body ON articles(body);
SELECT * FROM articles WHERE MATCH(body) AGAINST('mysql');</code></pre>

<p><strong>Naming convention</strong>: prefix with <code>idx_</code> or <code>uk_</code> (unique) and include table + column for clarity, e.g., <code>idx_orders_customer_id</code>. This makes it easy to identify when reading <code>SHOW INDEX</code> output.</p>

<p>Verify the index after creation:</p>
<pre><code>SHOW INDEX FROM users;</code></pre>
'''

ANSWERS[20] = r'''
<p>Use <code>DROP INDEX</code> &mdash; identify the index by name and the table it&rsquo;s on.</p>

<pre><code>DROP INDEX idx_users_email ON users;</code></pre>

<p>Or via <code>ALTER TABLE</code>:</p>
<pre><code>ALTER TABLE users
DROP INDEX idx_users_email;</code></pre>

<p>To find an index name if you don&rsquo;t remember it, list all indexes on the table:</p>
<pre><code>SHOW INDEX FROM users;</code></pre>

<p>Output includes columns like <code>Key_name</code>, <code>Column_name</code>, and <code>Non_unique</code>.</p>

<p><strong>When to drop indexes</strong>:</p>
<ul>
  <li>The query they were added for no longer runs.</li>
  <li>You see write performance issues from too many indexes.</li>
  <li>A composite index supersedes an older single-column index.</li>
  <li>The column distribution has changed (e.g., 99% of rows have the same value), making the index nearly useless.</li>
</ul>

<p><strong>Cannot be dropped</strong>: the primary key index is dropped via <code>DROP PRIMARY KEY</code>, not <code>DROP INDEX</code>:</p>
<pre><code>ALTER TABLE users DROP PRIMARY KEY;</code></pre>

<p>If the index supports a foreign key constraint, drop the FK first.</p>

<p><strong>Test before dropping in production</strong>: in a copy of the schema, profile your queries with <code>EXPLAIN</code> after dropping. The query optimizer might suddenly choose a much slower plan.</p>
'''

ANSWERS[21] = r'''
<p>A <strong>unique key</strong> is a constraint that ensures all values in a column (or combination of columns) are unique &mdash; no two rows can share the same value. It&rsquo;s similar to a primary key but with two differences:</p>
<ul>
  <li>A table can have <em>multiple</em> unique keys (only one primary key).</li>
  <li>A unique key column <em>can</em> contain <code>NULL</code> values, and (unlike most uniqueness rules) MySQL allows multiple <code>NULL</code> values in the same unique column.</li>
</ul>

<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  username VARCHAR(50) UNIQUE,
  age INT
);

INSERT INTO users (email, username) VALUES ('a@b.com', 'alice');
INSERT INTO users (email, username) VALUES ('a@b.com', 'bob');
-- ERROR: Duplicate entry 'a@b.com' for key 'email'</code></pre>

<p><strong>Use cases</strong>: emails, usernames, social-security numbers, ISBNs, phone numbers &mdash; anything that should be unique <em>but isn&rsquo;t the row identifier</em>.</p>

<p><strong>Primary key vs unique key</strong>:</p>
<table>
  <tr><th></th><th>Primary key</th><th>Unique key</th></tr>
  <tr><td>NULL allowed?</td><td>No</td><td>Yes (multiple NULLs OK)</td></tr>
  <tr><td>How many per table?</td><td>One</td><td>Many</td></tr>
  <tr><td>Auto-creates index?</td><td>Yes</td><td>Yes</td></tr>
  <tr><td>Used for relations?</td><td>Typically yes</td><td>Sometimes</td></tr>
</table>

<p>MySQL automatically creates an index on every unique key, making lookups fast.</p>
'''

ANSWERS[22] = r'''
<p>Three ways to declare a unique key: inline at column definition, as a table constraint, or via <code>ALTER TABLE</code>.</p>

<p><strong>Inline at column level</strong>:</p>
<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  username VARCHAR(50) UNIQUE
);</code></pre>

<p><strong>Table-level constraint (gives you naming control and supports composite keys)</strong>:</p>
<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255),
  username VARCHAR(50),
  CONSTRAINT uk_users_email UNIQUE (email),
  CONSTRAINT uk_users_username UNIQUE (username)
);</code></pre>

<p><strong>Composite unique key</strong> &mdash; combination must be unique, individual columns can repeat:</p>
<pre><code>CREATE TABLE enrollments (
  student_id INT,
  course_id INT,
  enrolled_at DATE,
  CONSTRAINT uk_enrollment UNIQUE (student_id, course_id)
);
-- Same student can enroll in different courses; same course
-- can have many students; but no duplicate (student, course) pair.</code></pre>

<p><strong>Add to existing table</strong>:</p>
<pre><code>ALTER TABLE users
ADD CONSTRAINT uk_users_email UNIQUE (email);

-- Or shorthand
ALTER TABLE users ADD UNIQUE (email);</code></pre>

<p><strong>Drop a unique key</strong>:</p>
<pre><code>ALTER TABLE users DROP INDEX uk_users_email;</code></pre>

<p>(Internally, MySQL implements unique keys as unique indexes, hence the <code>DROP INDEX</code>.)</p>

<p>If existing rows already violate uniqueness, the ALTER fails. Clean up duplicates first using GROUP BY or window functions.</p>
'''

ANSWERS[23] = r'''
<p>Use a <strong>JOIN</strong> clause to combine rows from two tables based on a related column. The most common is <strong>INNER JOIN</strong>, which returns only rows where the join condition matches in both tables.</p>

<pre><code>SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;</code></pre>

<p>This pairs each user with each of their orders. The <code>ON</code> clause specifies how rows match. Table aliases (<code>u</code>, <code>o</code>) keep the query readable.</p>

<p><strong>Worked example</strong> &mdash; given:</p>
<pre><code>users:                   orders:
+----+--------+         +----+---------+--------+
| id | name   |         | id | user_id | total  |
+----+--------+         +----+---------+--------+
| 1  | Alice  |         | 1  | 1       | 50.00  |
| 2  | Bob    |         | 2  | 1       | 30.00  |
| 3  | Carol  |         | 3  | 2       | 75.00  |
+----+--------+         +----+---------+--------+

Result of the INNER JOIN above:
+--------+-------+
| name   | total |
+--------+-------+
| Alice  | 50.00 |
| Alice  | 30.00 |
| Bob    | 75.00 |
+--------+-------+</code></pre>

<p>Carol has no orders, so she doesn&rsquo;t appear &mdash; that&rsquo;s the defining behavior of INNER JOIN.</p>

<p><strong>Why JOIN over multiple queries</strong>:</p>
<ul>
  <li><em>One round trip</em> &mdash; faster than fetching users then querying orders for each.</li>
  <li><em>Database does the work</em> &mdash; optimized join algorithms.</li>
  <li><em>Transactional consistency</em> &mdash; data is read atomically.</li>
</ul>

<p>Always have indexes on join columns (foreign keys typically) or join performance falls off a cliff.</p>
'''

ANSWERS[24] = r'''
<p>MySQL supports several JOIN types &mdash; they differ in which non-matching rows they include.</p>

<table>
  <tr><th>JOIN type</th><th>What it returns</th></tr>
  <tr><td><code>INNER JOIN</code></td><td>Only rows with matches in both tables</td></tr>
  <tr><td><code>LEFT JOIN</code></td><td>All rows from left + matching rows from right (NULL where none)</td></tr>
  <tr><td><code>RIGHT JOIN</code></td><td>All rows from right + matching rows from left</td></tr>
  <tr><td><code>CROSS JOIN</code></td><td>Cartesian product (every row × every row)</td></tr>
  <tr><td><code>SELF JOIN</code></td><td>Joining a table to itself (e.g., employees and managers)</td></tr>
</table>

<p>Visualizing with two sets:</p>

<pre><code>users (A)        orders (B)

  ___              ___
 / A \____________/ B \
 \   /   A∩B     \   /
  ‾‾‾             ‾‾‾

INNER:   A ∩ B          (overlap only)
LEFT:    A ∩ B + A only (everything in A)
RIGHT:   A ∩ B + B only (everything in B)
CROSS:   every A × every B</code></pre>

<p><strong>Note</strong>: MySQL doesn&rsquo;t natively support <code>FULL OUTER JOIN</code>. Simulate it by combining LEFT and RIGHT joins with <code>UNION</code>:</p>
<pre><code>SELECT * FROM a LEFT JOIN b ON a.id = b.a_id
UNION
SELECT * FROM a RIGHT JOIN b ON a.id = b.a_id;</code></pre>

<p>The plain word <code>JOIN</code> with no qualifier is treated as <code>INNER JOIN</code> in MySQL. Adding <code>OUTER</code> to <code>LEFT</code>/<code>RIGHT</code>/<code>FULL</code> is optional &mdash; <code>LEFT JOIN</code> means <code>LEFT OUTER JOIN</code>.</p>
'''

ANSWERS[25] = r'''
<p>An <strong>INNER JOIN</strong> returns only rows where the join condition is satisfied in <em>both</em> tables. Non-matching rows from either table are excluded.</p>

<pre><code>SELECT u.name, o.id, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;</code></pre>

<p>This returns user-order pairs. If a user has no orders, they don&rsquo;t appear. If an order has no matching user (data integrity issue!), it doesn&rsquo;t appear either.</p>

<p>The keyword <code>INNER</code> is optional &mdash; just <code>JOIN</code> means INNER JOIN in MySQL:</p>
<pre><code>SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id;</code></pre>

<p><strong>Multiple INNER JOINs</strong> &mdash; chain them:</p>
<pre><code>SELECT u.name, o.id, p.title
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
WHERE o.created_at &gt;= '2026-01-01';</code></pre>

<p><strong>Multi-column join condition</strong>:</p>
<pre><code>INNER JOIN sales s
  ON s.year = budget.year AND s.region = budget.region</code></pre>

<p><strong>Common gotcha</strong>: forgetting the <code>ON</code> clause produces a CROSS JOIN (every combination &mdash; potentially millions of rows). MySQL will warn but execute.</p>

<p>Always have indexes on the join columns &mdash; without them, MySQL falls back to nested-loop joins that scan the entire right table for each left row.</p>
'''

ANSWERS[26] = r'''
<p>A <strong>LEFT JOIN</strong> returns all rows from the left table, and the matching rows from the right table. Rows in the left table without matches still appear, with <code>NULL</code> values for the right-table columns.</p>

<pre><code>SELECT u.name, o.id, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;</code></pre>

<p>If Carol has no orders, she still appears in the result with <code>NULL</code> values for <code>o.id</code> and <code>o.total</code>.</p>

<p><strong>Common use cases</strong>:</p>
<ul>
  <li><strong>Show all parents and their (possibly zero) children</strong> &mdash; e.g., all users and any orders they may have placed.</li>
  <li><strong>Find rows with no matches</strong> &mdash; combine with <code>WHERE ... IS NULL</code>:
    <pre><code>-- Find users who haven&rsquo;t placed any orders
SELECT u.id, u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;</code></pre>
  </li>
  <li><strong>Reports with optional related data</strong> &mdash; e.g., dashboard listing all customers along with their last order date.</li>
</ul>

<p><strong>Aggregating with LEFT JOIN</strong> &mdash; useful for counts:</p>
<pre><code>SELECT u.id, u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
-- Users with no orders show order_count = 0</code></pre>

<p>The keyword <code>OUTER</code> is optional &mdash; <code>LEFT JOIN</code> and <code>LEFT OUTER JOIN</code> mean the same thing.</p>

<p>Make sure to index the right-table column used in the join condition, or LEFT JOIN scans degrade quickly.</p>
'''

ANSWERS[27] = r'''
<p>A <strong>RIGHT JOIN</strong> is the mirror image of LEFT JOIN &mdash; it returns all rows from the right table, plus matching rows from the left. Non-matching left-side rows produce <code>NULL</code> values.</p>

<pre><code>SELECT u.name, o.id, o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;</code></pre>

<p>This shows every order, even orphan orders whose <code>user_id</code> doesn&rsquo;t match any user (a data integrity warning sign &mdash; foreign keys should prevent this).</p>

<p><strong>RIGHT JOIN vs LEFT JOIN</strong>:</p>
<table>
  <tr><th>Goal</th><th>Use</th></tr>
  <tr><td>Show all "parents" (left), with matching "children" if any</td><td>LEFT JOIN</td></tr>
  <tr><td>Show all "children" (right), with matching "parents" if any</td><td>RIGHT JOIN</td></tr>
</table>

<p>Any RIGHT JOIN can be rewritten as a LEFT JOIN by swapping the table order:</p>

<pre><code>-- These are equivalent
SELECT * FROM users u RIGHT JOIN orders o ON u.id = o.user_id;
SELECT * FROM orders o LEFT JOIN users u ON u.id = o.user_id;</code></pre>

<p><strong>In practice, prefer LEFT JOIN</strong>. It&rsquo;s more idiomatic, more common, and easier to read &mdash; the table you&rsquo;re primarily interested in goes on the left, where readers expect it. Most production codebases use LEFT JOIN almost exclusively.</p>

<p>The <code>OUTER</code> keyword is optional &mdash; <code>RIGHT JOIN</code> means <code>RIGHT OUTER JOIN</code>.</p>
'''

ANSWERS[28] = r'''
<p>MySQL <strong>does not natively support FULL OUTER JOIN</strong> (unlike PostgreSQL or SQL Server). A FULL JOIN would return all rows from both tables, with NULLs where there&rsquo;s no match on either side.</p>

<p><strong>Simulate it with <code>UNION</code></strong>:</p>
<pre><code>SELECT u.name, o.id, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id

UNION

SELECT u.name, o.id, o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;</code></pre>

<p><code>UNION</code> automatically removes duplicates from the combined result &mdash; perfect for FULL JOIN simulation.</p>

<p><strong>What it returns</strong>:</p>
<ul>
  <li>Users with orders &mdash; appear once (matching rows).</li>
  <li>Users with no orders &mdash; appear with NULL order columns.</li>
  <li>Orders without users &mdash; appear with NULL user columns.</li>
</ul>

<p><strong>Use case</strong>: data reconciliation. Compare two related tables to find:</p>
<ul>
  <li>Records in A but not B.</li>
  <li>Records in B but not A.</li>
  <li>Records that match.</li>
</ul>

<pre><code>-- Find all employee/payroll mismatches
SELECT e.id, e.name, p.salary
FROM employees e LEFT JOIN payroll p ON e.id = p.employee_id
UNION
SELECT e.id, e.name, p.salary
FROM employees e RIGHT JOIN payroll p ON e.id = p.employee_id
WHERE e.id IS NULL OR p.employee_id IS NULL;</code></pre>

<p>FULL JOIN simulations are rare in practice &mdash; if you need them often, the schema may need foreign keys to prevent the orphans.</p>
'''

ANSWERS[29] = r'''
<p>A <strong>subquery</strong> (or "inner query") is a SELECT statement nested inside another SQL statement &mdash; SELECT, INSERT, UPDATE, or DELETE. The inner query runs first; its result feeds the outer query.</p>

<pre><code>-- Find users whose age is above the average
SELECT name, age
FROM users
WHERE age &gt; (SELECT AVG(age) FROM users);</code></pre>

<p>The inner query computes the average age (a single number); the outer query uses that number to filter.</p>

<p><strong>Categories</strong>:</p>
<table>
  <tr><th>Type</th><th>Returns</th><th>Example use</th></tr>
  <tr><td>Scalar subquery</td><td>One value</td><td><code>WHERE age &gt; (SELECT AVG(age) ...)</code></td></tr>
  <tr><td>Row subquery</td><td>One row</td><td><code>WHERE (a, b) = (SELECT ...)</code></td></tr>
  <tr><td>Column / list subquery</td><td>List of values</td><td><code>WHERE id IN (SELECT ...)</code></td></tr>
  <tr><td>Table subquery (derived table)</td><td>Multiple rows + columns</td><td>In FROM: <code>FROM (SELECT ...) t</code></td></tr>
  <tr><td>Correlated subquery</td><td>References outer query</td><td>Per-row computation</td></tr>
</table>

<p><strong>Correlated subquery example</strong> &mdash; references a column from the outer query:</p>
<pre><code>SELECT u.name,
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;</code></pre>

<p>The inner query runs once <em>per row</em> of the outer query &mdash; can be slow on large tables. Often a JOIN with GROUP BY is faster.</p>

<p><strong>Subquery vs JOIN</strong>: many subqueries can be rewritten as JOINs. The optimizer often produces the same plan, but JOINs tend to be more readable and sometimes perform better. Use <code>EXPLAIN</code> to compare.</p>
'''

ANSWERS[30] = r'''
<p>Wrap the inner query in parentheses and place it where you&rsquo;d normally put a value, list, or table.</p>

<p><strong>Subquery in WHERE (scalar)</strong>:</p>
<pre><code>SELECT name FROM users
WHERE department_id = (SELECT id FROM departments WHERE name = 'Engineering');</code></pre>

<p><strong>Subquery in WHERE with IN (list of values)</strong>:</p>
<pre><code>SELECT name FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total &gt; 100);</code></pre>

<p><strong>Subquery with EXISTS &mdash; check if any matches exist</strong>:</p>
<pre><code>-- Users who have at least one order
SELECT name FROM users u
WHERE EXISTS (SELECT 1 FROM orders WHERE user_id = u.id);</code></pre>

<p>EXISTS is often faster than <code>IN</code> with a subquery &mdash; it short-circuits as soon as one match is found.</p>

<p><strong>Subquery in FROM (derived table)</strong> &mdash; treat a query result as a temporary table:</p>
<pre><code>SELECT category, avg_price FROM (
  SELECT category, AVG(price) AS avg_price
  FROM products
  GROUP BY category
) AS category_avg
WHERE avg_price &gt; 50;</code></pre>

<p>The derived table must have an alias.</p>

<p><strong>Subquery in SELECT (computed column)</strong>:</p>
<pre><code>SELECT name,
       (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;</code></pre>

<p><strong>Common pitfalls</strong>:</p>
<ul>
  <li>Scalar subquery returning multiple rows &mdash; SQL error. Use <code>LIMIT 1</code> or aggregate.</li>
  <li>Correlated subqueries on huge tables &mdash; slow. Rewrite as JOIN with GROUP BY.</li>
  <li>Forgetting alias on derived table &mdash; syntax error.</li>
</ul>
'''

ANSWERS[31] = r'''
<p>A <strong>stored procedure</strong> is a precompiled set of SQL statements stored in the database itself, callable by name. Think of it as a function that lives in MySQL &mdash; you can pass parameters, perform multiple operations, and return results.</p>

<pre><code>DELIMITER //

CREATE PROCEDURE GetUserOrders(IN userId INT)
BEGIN
  SELECT o.id, o.total, o.created_at
  FROM orders o
  WHERE o.user_id = userId
  ORDER BY o.created_at DESC;
END //

DELIMITER ;

-- Call it
CALL GetUserOrders(1);</code></pre>

<p><strong>Why use stored procedures</strong>:</p>
<ul>
  <li><strong>Performance</strong> &mdash; the SQL is parsed and optimized once when created, not on every call.</li>
  <li><strong>Network efficiency</strong> &mdash; one round trip executes many statements.</li>
  <li><strong>Centralized logic</strong> &mdash; multiple apps share the same database logic.</li>
  <li><strong>Security</strong> &mdash; grant execute privilege without granting direct table access.</li>
</ul>

<p><strong>Drawbacks</strong>:</p>
<ul>
  <li><strong>Hard to version-control</strong> &mdash; lives in the DB, not in your Git repo (without tooling).</li>
  <li><strong>Limited debugging</strong> &mdash; SQL has no good debugger.</li>
  <li><strong>Vendor lock-in</strong> &mdash; MySQL syntax differs from PostgreSQL or SQL Server.</li>
  <li><strong>Modern apps prefer ORMs</strong> &mdash; logic in code, not the DB.</li>
</ul>

<p>The <code>DELIMITER</code> change is needed because the procedure body uses <code>;</code> for individual statements; without changing the delimiter, MySQL would think the first <code>;</code> ends the CREATE.</p>
'''

ANSWERS[32] = r'''
<p>Use the <code>CREATE PROCEDURE</code> syntax. The procedure body is wrapped in <code>BEGIN ... END</code>; if it contains semicolons, change the statement delimiter first.</p>

<pre><code>DELIMITER //

CREATE PROCEDURE TransferFunds(
  IN fromAcct INT,
  IN toAcct INT,
  IN amount DECIMAL(10,2)
)
BEGIN
  START TRANSACTION;
    UPDATE accounts SET balance = balance - amount WHERE id = fromAcct;
    UPDATE accounts SET balance = balance + amount WHERE id = toAcct;
  COMMIT;
END //

DELIMITER ;</code></pre>

<p><strong>Parameter modes</strong>:</p>
<table>
  <tr><th>Mode</th><th>Direction</th></tr>
  <tr><td><code>IN</code></td><td>Caller passes value in (default)</td></tr>
  <tr><td><code>OUT</code></td><td>Procedure passes value back to caller</td></tr>
  <tr><td><code>INOUT</code></td><td>Both directions</td></tr>
</table>

<pre><code>CREATE PROCEDURE GetUserCount(OUT total INT)
BEGIN
  SELECT COUNT(*) INTO total FROM users;
END //

-- Call and read OUT parameter
CALL GetUserCount(@total);
SELECT @total;</code></pre>

<p><strong>Variables and control flow</strong>:</p>
<pre><code>CREATE PROCEDURE GreetUser(IN userId INT)
BEGIN
  DECLARE userName VARCHAR(100);
  SELECT name INTO userName FROM users WHERE id = userId;

  IF userName IS NULL THEN
    SELECT 'User not found' AS message;
  ELSE
    SELECT CONCAT('Hello, ', userName) AS message;
  END IF;
END //</code></pre>

<p>MySQL supports <code>IF</code>, <code>CASE</code>, <code>WHILE</code>, <code>LOOP</code>, <code>REPEAT</code>, and cursors inside procedures &mdash; basically a small procedural language.</p>
'''

ANSWERS[33] = r'''
<p>Use the <code>CALL</code> statement, passing arguments matching the procedure&rsquo;s parameters.</p>

<pre><code>CALL GetUserOrders(1);

CALL TransferFunds(123, 456, 100.50);</code></pre>

<p><strong>OUT parameters</strong> &mdash; pass a session variable; read its value after:</p>
<pre><code>CALL GetUserCount(@total);
SELECT @total AS user_count;</code></pre>

<p><strong>From application code (Node.js, mysql2)</strong>:</p>
<pre><code>const [rows] = await conn.execute('CALL GetUserOrders(?)', [1]);
console.log(rows[0]);   // First result set</code></pre>

<p>Note: stored procedures can return multiple result sets. Most database drivers return them as an array of arrays.</p>

<p><strong>From Python (PyMySQL)</strong>:</p>
<pre><code>cur.callproc('GetUserOrders', [1])
for row in cur.fetchall():
    print(row)</code></pre>

<p><strong>Common errors when calling</strong>:</p>
<ul>
  <li><strong>Wrong argument count</strong> &mdash; "Incorrect number of arguments for PROCEDURE...".</li>
  <li><strong>Wrong type</strong> &mdash; passing a string where INT is expected; MySQL tries to coerce.</li>
  <li><strong>Privilege missing</strong> &mdash; need <code>EXECUTE</code> permission on the procedure.</li>
</ul>

<p>To grant execute permission to a user:</p>
<pre><code>GRANT EXECUTE ON PROCEDURE mydb.GetUserOrders TO 'appuser'@'%';</code></pre>

<p>To find what procedures exist in the current database:</p>
<pre><code>SHOW PROCEDURE STATUS WHERE Db = 'mydb';</code></pre>
'''

ANSWERS[34] = r'''
<p>Use the <code>DROP PROCEDURE</code> statement &mdash; specify the procedure name (no parentheses, no parameter list).</p>

<pre><code>DROP PROCEDURE GetUserOrders;</code></pre>

<p>Avoid an error if it doesn&rsquo;t exist:</p>
<pre><code>DROP PROCEDURE IF EXISTS GetUserOrders;</code></pre>

<p>If the procedure is in another database, qualify the name:</p>
<pre><code>DROP PROCEDURE shop.GetUserOrders;</code></pre>

<p><strong>To list existing procedures</strong>:</p>
<pre><code>SHOW PROCEDURE STATUS WHERE Db = 'shop';</code></pre>

<p><strong>To see a procedure&rsquo;s definition before dropping it</strong>:</p>
<pre><code>SHOW CREATE PROCEDURE GetUserOrders;</code></pre>

<p>This is good practice &mdash; copy the source somewhere you can recover it if you change your mind.</p>

<p><strong>Recreating a procedure with changes</strong> &mdash; MySQL doesn&rsquo;t support <code>CREATE OR REPLACE PROCEDURE</code> directly. The pattern is:</p>
<pre><code>DROP PROCEDURE IF EXISTS GetUserOrders;

DELIMITER //
CREATE PROCEDURE GetUserOrders(IN userId INT)
BEGIN
  -- new body
END //
DELIMITER ;</code></pre>

<p>Required privilege: <code>ALTER ROUTINE</code> permission. Procedures created by other users are visible to you but you may not have permission to drop them.</p>

<p>If you have apps actively calling a procedure, drop-and-recreate causes a brief window where calls fail. In production, deploy procedures during maintenance windows or use blue/green strategies.</p>
'''

ANSWERS[35] = r'''
<p>A <strong>trigger</strong> is a special stored program that automatically runs (<em>fires</em>) in response to an event on a specific table &mdash; typically an INSERT, UPDATE, or DELETE. Triggers let the database enforce rules or maintain related data without application code remembering to do it.</p>

<pre><code>DELIMITER //

CREATE TRIGGER audit_user_changes
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
  INSERT INTO user_audit (user_id, old_email, new_email, changed_at)
  VALUES (OLD.id, OLD.email, NEW.email, NOW());
END //

DELIMITER ;</code></pre>

<p>Now every UPDATE on <code>users</code> automatically writes an audit record &mdash; no app code involved.</p>

<p><strong>Trigger components</strong>:</p>
<ul>
  <li><strong>Timing</strong>: <code>BEFORE</code> or <code>AFTER</code> the event.</li>
  <li><strong>Event</strong>: <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code>.</li>
  <li><strong>Granularity</strong>: <code>FOR EACH ROW</code> &mdash; runs once per affected row.</li>
  <li><strong>OLD and NEW</strong>: pseudo-rows representing the values before and after the change. Available based on the event type:
    <ul>
      <li>INSERT &mdash; <code>NEW</code> only.</li>
      <li>UPDATE &mdash; <code>OLD</code> and <code>NEW</code>.</li>
      <li>DELETE &mdash; <code>OLD</code> only.</li>
    </ul>
  </li>
</ul>

<p><strong>Common uses</strong>: audit logs, derived columns (e.g., <code>full_name = first || ' ' || last</code>), referential integrity beyond foreign keys, automatic timestamps, validation.</p>

<p><strong>Caveats</strong>: triggers are invisible &mdash; engineers can be confused why data changes "by itself." They run inside the same transaction, so a slow trigger slows every write. Use sparingly and document them.</p>
'''

ANSWERS[36] = r'''
<p>Use the <code>CREATE TRIGGER</code> syntax. Specify the timing (BEFORE/AFTER), event (INSERT/UPDATE/DELETE), table, and body.</p>

<pre><code>DELIMITER //

CREATE TRIGGER set_created_at
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
  SET NEW.created_at = NOW();
END //

DELIMITER ;</code></pre>

<p>The <code>BEFORE INSERT</code> trigger fires before the row is inserted &mdash; you can modify <code>NEW</code> values, which then become the inserted row.</p>

<p><strong>UPDATE trigger</strong>:</p>
<pre><code>CREATE TRIGGER track_price_change
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
  IF OLD.price &lt;&gt; NEW.price THEN
    INSERT INTO price_history (product_id, old_price, new_price, changed_at)
    VALUES (NEW.id, OLD.price, NEW.price, NOW());
  END IF;
END //</code></pre>

<p>The <code>OLD</code> and <code>NEW</code> pseudo-rows let you compare before/after values.</p>

<p><strong>DELETE trigger</strong>:</p>
<pre><code>CREATE TRIGGER archive_deleted_user
BEFORE DELETE ON users
FOR EACH ROW
BEGIN
  INSERT INTO deleted_users
    SELECT *, NOW() AS deleted_at
    FROM users WHERE id = OLD.id;
END //</code></pre>

<p><strong>Restrictions</strong>:</p>
<ul>
  <li>A table can have only one trigger of each (timing, event) combination.</li>
  <li>Triggers cannot use <code>CALL</code> on a procedure that returns result sets.</li>
  <li>Triggers cannot start their own transactions &mdash; they run inside the calling transaction.</li>
  <li>Triggers cannot directly modify the same table they fire on (would loop).</li>
</ul>

<p>List triggers in a database:</p>
<pre><code>SHOW TRIGGERS FROM mydb;</code></pre>
'''

ANSWERS[37] = r'''
<p>Use the <code>DROP TRIGGER</code> statement.</p>

<pre><code>DROP TRIGGER audit_user_changes;</code></pre>

<p>Avoid an error if the trigger doesn&rsquo;t exist:</p>
<pre><code>DROP TRIGGER IF EXISTS audit_user_changes;</code></pre>

<p>If the trigger is in another database, qualify the name:</p>
<pre><code>DROP TRIGGER shop.audit_user_changes;</code></pre>

<p><strong>To list triggers</strong>:</p>
<pre><code>SHOW TRIGGERS FROM mydb;
-- Or specifically on one table
SHOW TRIGGERS WHERE `Table` = 'users';</code></pre>

<p>Output includes columns like <code>Trigger</code>, <code>Event</code>, <code>Table</code>, <code>Statement</code>, <code>Timing</code>.</p>

<p><strong>To see a trigger&rsquo;s definition before dropping</strong>:</p>
<pre><code>SHOW CREATE TRIGGER audit_user_changes;</code></pre>

<p>Save the output if you might need to recreate it.</p>

<p><strong>Triggers are dropped with the table</strong> &mdash; if you <code>DROP TABLE</code>, all triggers on that table are removed automatically.</p>

<p><strong>Required privilege</strong>: <code>TRIGGER</code> permission on the table.</p>

<p><strong>Recreating a trigger with changes</strong> &mdash; MySQL doesn&rsquo;t support <code>CREATE OR REPLACE TRIGGER</code>, so:</p>
<pre><code>DROP TRIGGER IF EXISTS audit_user_changes;

DELIMITER //
CREATE TRIGGER audit_user_changes
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
  -- new body
END //
DELIMITER ;</code></pre>

<p>Wrap drop+recreate in a transaction during low-traffic times to minimize the window where audit/derived data isn&rsquo;t recorded.</p>
'''

ANSWERS[38] = r'''
<p>A <strong>view</strong> is a saved SELECT query treated like a virtual table. It doesn&rsquo;t store data &mdash; it&rsquo;s just a stored query definition. When you SELECT from a view, MySQL runs the underlying query.</p>

<pre><code>CREATE VIEW active_users AS
SELECT id, name, email
FROM users
WHERE active = 1 AND deleted_at IS NULL;

-- Now use it like a table
SELECT * FROM active_users;
SELECT name FROM active_users WHERE id = 5;</code></pre>

<p><strong>Why use views</strong>:</p>
<ul>
  <li><strong>Simplify complex queries</strong> &mdash; hide multi-table joins behind a simple <code>SELECT * FROM view</code>.</li>
  <li><strong>Security</strong> &mdash; expose only certain columns or rows; grant SELECT on the view but not the underlying table.</li>
  <li><strong>Consistency</strong> &mdash; everyone uses the same definition of "active user," "high-value order," etc.</li>
  <li><strong>Schema abstraction</strong> &mdash; if the underlying table changes, the view can be rewritten to keep the same shape.</li>
</ul>

<p><strong>Updatable views</strong> &mdash; some views allow INSERT/UPDATE/DELETE that affect the underlying table:</p>
<pre><code>UPDATE active_users SET name = 'Alice' WHERE id = 1;
-- Updates the users table</code></pre>

<p>To be updatable, a view must be a simple one-to-one mapping with the base table &mdash; no <code>GROUP BY</code>, <code>DISTINCT</code>, joins, or aggregates.</p>

<p><strong>Performance</strong>: views are <em>not</em> automatically faster than the underlying query &mdash; they execute the query each time. For repeated heavy queries, consider materialized views (which MySQL doesn&rsquo;t natively support &mdash; emulate with cron + a real table).</p>
'''

ANSWERS[39] = r'''
<p>Use <code>CREATE VIEW</code> with a <code>SELECT</code> query that defines what the view returns.</p>

<pre><code>CREATE VIEW order_summary AS
SELECT
  o.id,
  u.name AS customer_name,
  o.total,
  o.created_at
FROM orders o
INNER JOIN users u ON u.id = o.user_id;

-- Use it like any table
SELECT * FROM order_summary WHERE total &gt; 100;</code></pre>

<p><strong>Replace an existing view</strong>:</p>
<pre><code>CREATE OR REPLACE VIEW order_summary AS
SELECT ...;</code></pre>

<p><strong>With explicit column names</strong> &mdash; useful when the SELECT has computed columns:</p>
<pre><code>CREATE VIEW user_stats (user_id, full_name, order_count) AS
SELECT
  u.id,
  CONCAT(u.first_name, ' ', u.last_name),
  COUNT(o.id)
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id;</code></pre>

<p><strong>WITH CHECK OPTION</strong> &mdash; prevents inserts/updates that would create rows the view wouldn&rsquo;t show:</p>
<pre><code>CREATE VIEW active_users AS
SELECT * FROM users WHERE active = 1
WITH CHECK OPTION;

-- This would fail (would create an inactive user not visible in the view)
INSERT INTO active_users (name, active) VALUES ('Bob', 0);</code></pre>

<p><strong>Restrictions</strong>:</p>
<ul>
  <li>Cannot reference temporary tables.</li>
  <li>Cannot reference variables.</li>
  <li>Cannot have ORDER BY in a way that conflicts with outer queries.</li>
</ul>

<p>List views with <code>SHOW FULL TABLES WHERE Table_type = 'VIEW';</code></p>
'''

ANSWERS[40] = r'''
<p>Use <code>DROP VIEW</code> to remove a view. The underlying tables and data are unaffected &mdash; only the view definition disappears.</p>

<pre><code>DROP VIEW active_users;</code></pre>

<p>Avoid an error if it doesn&rsquo;t exist:</p>
<pre><code>DROP VIEW IF EXISTS active_users;</code></pre>

<p>Drop multiple views at once:</p>
<pre><code>DROP VIEW IF EXISTS view1, view2, view3;</code></pre>

<p><strong>Find existing views</strong>:</p>
<pre><code>SHOW FULL TABLES WHERE Table_type = 'VIEW';
-- Or
SELECT TABLE_NAME FROM information_schema.VIEWS
WHERE TABLE_SCHEMA = 'mydb';</code></pre>

<p><strong>See the definition before dropping</strong>:</p>
<pre><code>SHOW CREATE VIEW active_users;</code></pre>

<p>Save the output if there&rsquo;s any chance you&rsquo;ll want to recreate it.</p>

<p><strong>Replace versus drop+recreate</strong> &mdash; if you just want to change the view&rsquo;s definition:</p>
<pre><code>CREATE OR REPLACE VIEW active_users AS
SELECT id, name FROM users WHERE active = 1;</code></pre>

<p>This is atomic &mdash; no window where the view doesn&rsquo;t exist.</p>

<p><strong>Required privilege</strong>: <code>DROP</code> on the view (typically inherited from <code>DROP</code> on the database).</p>

<p><strong>If apps query the view</strong>: dropping it breaks those queries until something replaces it. Coordinate with deployments; use <code>CREATE OR REPLACE</code> if updating, not removing.</p>

<p>Note: views are not in the <code>information_schema.TABLES</code> table&rsquo;s default Type column &mdash; they show as <code>VIEW</code>, not <code>BASE TABLE</code>.</p>
'''

ANSWERS[41] = r'''
<p>A <strong>transaction</strong> is a group of one or more SQL statements treated as a single unit of work &mdash; either all of them succeed and the changes are saved, or none of them are. This is the foundation of data consistency in databases.</p>

<p><strong>Classic example: bank transfer.</strong> You must subtract from one account and add to another. If only one of those operations succeeds, money disappears or appears out of thin air.</p>

<pre><code>START TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- Both updates apply, or neither does</code></pre>

<p>If something goes wrong &mdash; an error, a power failure, a manual decision &mdash; you <code>ROLLBACK</code> instead of committing:</p>
<pre><code>START TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  -- something looks off
ROLLBACK;
-- The first update is undone</code></pre>

<p><strong>The four ACID properties</strong> are guaranteed by transactions:</p>
<table>
  <tr><th>Property</th><th>Meaning</th></tr>
  <tr><td>Atomicity</td><td>All or none</td></tr>
  <tr><td>Consistency</td><td>DB stays valid (constraints enforced)</td></tr>
  <tr><td>Isolation</td><td>Concurrent transactions don&rsquo;t interfere</td></tr>
  <tr><td>Durability</td><td>Committed changes persist (survive crashes)</td></tr>
</table>

<p><strong>Engine matters</strong>: only <strong>InnoDB</strong> supports transactions in MySQL. The older MyISAM engine doesn&rsquo;t. InnoDB has been the default since MySQL 5.5.</p>
'''

ANSWERS[42] = r'''
<p>Three ways to start a transaction in MySQL:</p>

<p><strong>1. Explicit START TRANSACTION (most common)</strong>:</p>
<pre><code>START TRANSACTION;
  -- statements
COMMIT;</code></pre>

<p><strong>2. BEGIN (alias for START TRANSACTION)</strong>:</p>
<pre><code>BEGIN;
  -- statements
COMMIT;</code></pre>

<p>Some SQL dialects (PostgreSQL) prefer <code>BEGIN</code>; works in MySQL too.</p>

<p><strong>3. Disable autocommit</strong>:</p>
<pre><code>SET autocommit = 0;
  -- statements
COMMIT;
SET autocommit = 1;</code></pre>

<p>By default, MySQL has <code>autocommit = 1</code> &mdash; every statement is its own transaction, automatically committed. With autocommit off, you must explicitly COMMIT or ROLLBACK to end each transaction.</p>

<p><strong>Transaction options</strong>:</p>
<pre><code>START TRANSACTION READ ONLY;        -- optimization for SELECT-only
START TRANSACTION WITH CONSISTENT SNAPSHOT;</code></pre>

<p><strong>From application code</strong>:</p>
<pre><code>// Node.js mysql2
const conn = await pool.getConnection();
try {
  await conn.beginTransaction();
  await conn.execute('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
  await conn.execute('UPDATE accounts SET balance = balance + 100 WHERE id = 2');
  await conn.commit();
} catch (err) {
  await conn.rollback();
  throw err;
} finally {
  conn.release();
}</code></pre>

<p>Many ORMs (Sequelize, TypeORM, Prisma) provide a <code>transaction()</code> helper that handles begin/commit/rollback automatically based on whether the callback throws.</p>

<p><strong>Note</strong>: starting a new transaction in the middle of one auto-commits the open one. Nested transactions must use <code>SAVEPOINT</code>.</p>
'''

ANSWERS[43] = r'''
<p>Use the <code>COMMIT</code> statement to make all changes from the current transaction permanent. After commit:</p>
<ul>
  <li>The changes are written to disk and durable (the D in ACID).</li>
  <li>Other transactions can see them.</li>
  <li>The transaction ends &mdash; the next statement begins a new one (or auto-commits, if autocommit is on).</li>
</ul>

<pre><code>START TRANSACTION;
  INSERT INTO orders (user_id, total) VALUES (1, 99.99);
  UPDATE users SET total_orders = total_orders + 1 WHERE id = 1;
COMMIT;</code></pre>

<p><strong>From application code</strong>:</p>
<pre><code>// Node.js mysql2
const conn = await pool.getConnection();
try {
  await conn.beginTransaction();
  await conn.execute('INSERT INTO orders ...');
  await conn.execute('UPDATE users ...');
  await conn.commit();    // make changes permanent
} catch (err) {
  await conn.rollback();
}</code></pre>

<p><strong>Implicit commits</strong>: certain statements automatically commit the current transaction whether you wanted them to or not:</p>
<ul>
  <li>DDL statements: <code>CREATE TABLE</code>, <code>ALTER TABLE</code>, <code>DROP TABLE</code>.</li>
  <li><code>SET autocommit = 1</code>.</li>
  <li><code>START TRANSACTION</code> (commits the previous one).</li>
  <li><code>LOAD DATA INFILE</code>, <code>TRUNCATE TABLE</code>.</li>
</ul>

<p>This means you can&rsquo;t group <code>CREATE TABLE</code> with row inserts in a rollback-able transaction in MySQL.</p>

<p><strong>Once committed, a transaction cannot be rolled back</strong>. To "undo" committed changes, you must run new SQL that reverses them &mdash; or restore from a backup. Always test risky queries by running them inside an uncommitted transaction first.</p>
'''

ANSWERS[44] = r'''
<p>Use the <code>ROLLBACK</code> statement to undo all changes made in the current transaction. The database returns to the state it was in when the transaction started.</p>

<pre><code>START TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 999;
  -- account 999 doesn&rsquo;t exist, balance is now wrong
ROLLBACK;
-- Both updates undone; balances back to original</code></pre>

<p><strong>When to roll back</strong>:</p>
<ul>
  <li>An error occurred (network failure, constraint violation).</li>
  <li>Application logic decided to abort (validation failed mid-process).</li>
  <li>Testing potentially destructive changes safely.</li>
</ul>

<p><strong>Application code pattern</strong> &mdash; rollback on any error:</p>
<pre><code>const conn = await pool.getConnection();
try {
  await conn.beginTransaction();
  // multiple statements
  await conn.commit();
} catch (err) {
  await conn.rollback();
  throw err;
} finally {
  conn.release();
}</code></pre>

<p>Most ORMs do this automatically &mdash; if your transaction callback throws, they call rollback for you.</p>

<p><strong>Savepoints</strong> &mdash; partial rollback within a transaction:</p>
<pre><code>START TRANSACTION;
  INSERT INTO logs ...;
  SAVEPOINT before_risky;
  UPDATE accounts ...;
  -- something went wrong with the update
  ROLLBACK TO SAVEPOINT before_risky;
  -- only the UPDATE is undone; INSERT into logs is preserved
COMMIT;</code></pre>

<p><strong>Cannot roll back DDL</strong>: <code>CREATE TABLE</code>, <code>DROP TABLE</code>, etc. auto-commit in MySQL &mdash; you can&rsquo;t undo them with ROLLBACK. Always back up before structural changes.</p>

<p>If the connection drops mid-transaction, MySQL automatically rolls back &mdash; which is why short-lived transactions are safer than long ones.</p>
'''

ANSWERS[45] = r'''
<p><strong>ACID</strong> is a set of properties that guarantee database transactions are processed reliably. The acronym stands for:</p>

<table>
  <tr><th>Property</th><th>What it guarantees</th></tr>
  <tr><td><strong>A</strong>tomicity</td><td>All operations in a transaction succeed or none do; partial completion is impossible</td></tr>
  <tr><td><strong>C</strong>onsistency</td><td>Transactions transition the DB from one valid state to another; constraints (FKs, NOT NULL, etc.) are always satisfied</td></tr>
  <tr><td><strong>I</strong>solation</td><td>Concurrent transactions don&rsquo;t interfere &mdash; the DB behaves as if they ran one at a time</td></tr>
  <tr><td><strong>D</strong>urability</td><td>Once a transaction commits, the changes survive even crashes or power failures</td></tr>
</table>

<p><strong>Atomicity example</strong>: a bank transfer that deducts from one account and credits another. If the credit fails, the deduction is also undone &mdash; you can&rsquo;t end up with money missing.</p>

<p><strong>Consistency example</strong>: if a foreign key prevents deleting a user with orders, that constraint is enforced even mid-transaction. The database never reaches a state that violates its rules.</p>

<p><strong>Isolation example</strong>: two users buy the last ticket simultaneously. Without isolation, both could see "1 ticket left" and both succeed; with isolation, one buys and the other sees "sold out."</p>

<p><strong>Durability example</strong>: after <code>COMMIT</code> returns success, the data is on disk &mdash; even if the server crashes the next millisecond, the change is recoverable.</p>

<p><strong>MySQL provides ACID via the InnoDB engine</strong>. The older MyISAM engine doesn&rsquo;t support transactions, so it&rsquo;s not ACID-compliant. InnoDB has been the default since MySQL 5.5 (2010); always use it for any application that cares about data integrity.</p>

<p>Isolation has configurable levels: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ (MySQL default), SERIALIZABLE &mdash; trade-offs between strictness and concurrency.</p>
'''

ANSWERS[46] = r'''
<p>Add the <code>AUTO_INCREMENT</code> attribute to a column &mdash; MySQL automatically assigns the next number when you insert a row without specifying that column. Used almost universally for primary key id columns.</p>

<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100)
);

INSERT INTO users (name) VALUES ('Alice');   -- id = 1
INSERT INTO users (name) VALUES ('Bob');     -- id = 2
INSERT INTO users (name) VALUES ('Carol');   -- id = 3</code></pre>

<p><strong>Rules</strong>:</p>
<ul>
  <li>Only one column per table can be AUTO_INCREMENT.</li>
  <li>The column must be indexed (typically PRIMARY KEY or UNIQUE).</li>
  <li>The column must be a numeric integer type (TINYINT, INT, BIGINT, etc.).</li>
</ul>

<p><strong>Set the starting value</strong>:</p>
<pre><code>CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ...
) AUTO_INCREMENT = 1000;   -- start at 1000

-- Or after the fact
ALTER TABLE orders AUTO_INCREMENT = 5000;</code></pre>

<p><strong>Skip a value manually</strong> &mdash; provide an explicit id:</p>
<pre><code>INSERT INTO users (id, name) VALUES (100, 'Dave');
-- Next auto-assigned will be 101</code></pre>

<p><strong>Gotchas</strong>:</p>
<ul>
  <li><strong>Gaps are normal</strong>: failed inserts and rolled-back transactions still consume IDs &mdash; the sequence can have holes.</li>
  <li><strong>Reach the max</strong>: INT max is 2.1 billion; BIGINT max is 9 quintillion. Pick the right size up front &mdash; growing the column requires rebuilding the table on huge tables.</li>
  <li><strong>Replication</strong>: in master-master setups, set different <code>auto_increment_increment</code> values to avoid ID collisions.</li>
</ul>
'''

ANSWERS[47] = r'''
<p>Use the <code>LAST_INSERT_ID()</code> function &mdash; it returns the AUTO_INCREMENT value generated by the most recent successful INSERT in the current connection.</p>

<pre><code>INSERT INTO users (name, email) VALUES ('Alice', 'a@b.com');
SELECT LAST_INSERT_ID();
-- 42 (or whatever id was assigned)</code></pre>

<p><strong>Per connection, not per session</strong>: LAST_INSERT_ID is connection-local. If two clients insert at the same time, each sees its own ID. The value isn&rsquo;t affected by other clients&rsquo; activity.</p>

<p><strong>Multi-row insert</strong>: returns the ID of the <em>first</em> row inserted; subsequent IDs are sequential.</p>
<pre><code>INSERT INTO users (name) VALUES ('A'), ('B'), ('C');
SELECT LAST_INSERT_ID();
-- Say it returns 10; the inserted ids are 10, 11, 12</code></pre>

<p><strong>From application code</strong> &mdash; most drivers expose this via the result object:</p>
<pre><code>// Node.js mysql2
const [result] = await conn.execute(
  'INSERT INTO users (name) VALUES (?)', ['Alice']
);
console.log(result.insertId);   // 42

// Python PyMySQL
cur.execute('INSERT INTO users (name) VALUES (%s)', ('Alice',))
print(cur.lastrowid)            # 42

// PHP PDO
$pdo-&gt;exec("INSERT ...");
echo $pdo-&gt;lastInsertId();</code></pre>

<p><strong>Common use case</strong>: insert a parent row, get its ID, insert child rows that reference it.</p>
<pre><code>INSERT INTO orders (user_id, total) VALUES (1, 99.99);
SET @order_id = LAST_INSERT_ID();
INSERT INTO order_items (order_id, product_id, qty)
  VALUES (@order_id, 5, 2), (@order_id, 7, 1);</code></pre>

<p>Wrap in a transaction to ensure atomicity. If you need the ID after multiple inserts, capture it immediately after the relevant INSERT &mdash; later operations will overwrite it.</p>
'''

ANSWERS[48] = r'''
<p>A <strong>DEFAULT constraint</strong> specifies a value that MySQL assigns to a column automatically when an INSERT doesn&rsquo;t provide one. Useful for timestamps, status flags, and sensible fallbacks.</p>

<pre><code>CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  status VARCHAR(20) DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  total DECIMAL(10, 2) DEFAULT 0.00
);

INSERT INTO orders (id) VALUES (1);
-- status='pending', created_at=now, total=0.00</code></pre>

<p><strong>Common DEFAULT values</strong>:</p>
<table>
  <tr><th>Default</th><th>Use case</th></tr>
  <tr><td>Literal value: <code>'pending'</code>, <code>0</code>, <code>false</code></td><td>Status flags, counters</td></tr>
  <tr><td><code>CURRENT_TIMESTAMP</code> / <code>NOW()</code></td><td>Created timestamps</td></tr>
  <tr><td><code>NULL</code></td><td>Optional column with no value</td></tr>
  <tr><td>UUID generated function</td><td>External identifiers</td></tr>
</table>

<p><strong>Auto-update timestamps</strong> &mdash; common pattern for "updated_at" columns:</p>
<pre><code>CREATE TABLE posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                       ON UPDATE CURRENT_TIMESTAMP
);
-- updated_at automatically refreshes on every UPDATE</code></pre>

<p><strong>Restrictions</strong>:</p>
<ul>
  <li>BLOB/TEXT/JSON/GEOMETRY columns can&rsquo;t have a literal default in older MySQL versions (only NULL).</li>
  <li>Default expressions need to be in parentheses (MySQL 8.0.13+).</li>
</ul>

<p><strong>vs NOT NULL</strong>: DEFAULT and NOT NULL are different. DEFAULT supplies a value when none is given; NOT NULL forbids storing NULL. Combining them is common: a column that can&rsquo;t be null and has a fallback if you forget to provide one.</p>
'''

ANSWERS[49] = r'''
<p>Add the <code>DEFAULT</code> clause after the data type in a column definition. The value is used when an INSERT omits this column.</p>

<p><strong>In CREATE TABLE</strong>:</p>
<pre><code>CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  status VARCHAR(20) DEFAULT 'active',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  login_count INT DEFAULT 0
);

INSERT INTO users (name) VALUES ('Alice');
-- status='active', created_at=NOW, login_count=0</code></pre>

<p><strong>Add a default to an existing column</strong>:</p>
<pre><code>ALTER TABLE users
ALTER COLUMN status SET DEFAULT 'pending';

-- Or via MODIFY (also lets you change the type)
ALTER TABLE users
MODIFY COLUMN status VARCHAR(20) DEFAULT 'pending';</code></pre>

<p><strong>Remove a default</strong>:</p>
<pre><code>ALTER TABLE users
ALTER COLUMN status DROP DEFAULT;</code></pre>

<p><strong>Existing rows</strong>: setting a default doesn&rsquo;t change existing rows &mdash; only future INSERTs that omit the column. To backfill, run a separate UPDATE:</p>
<pre><code>UPDATE users SET status = 'active' WHERE status IS NULL;</code></pre>

<p><strong>Default with expressions</strong> &mdash; MySQL 8.0.13+ supports expressions if wrapped in parentheses:</p>
<pre><code>CREATE TABLE events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  uuid CHAR(36) DEFAULT (UUID()),
  expires_at DATETIME DEFAULT (DATE_ADD(NOW(), INTERVAL 30 DAY))
);</code></pre>

<p><strong>Use NULL when there&rsquo;s no sensible default</strong>:</p>
<pre><code>middle_name VARCHAR(50) DEFAULT NULL  -- explicit "no value"</code></pre>

<p>This is also the <em>implicit</em> default for nullable columns &mdash; specifying it just makes intent clear.</p>
'''

ANSWERS[50] = r'''
<p>A <strong>composite key</strong> is a primary key (or unique key) made up of two or more columns. The combination must be unique &mdash; individual columns can repeat, but the tuple of values cannot.</p>

<pre><code>CREATE TABLE enrollments (
  student_id INT,
  course_id INT,
  enrolled_at DATE,
  PRIMARY KEY (student_id, course_id)
);

-- These all succeed
INSERT INTO enrollments VALUES (1, 100, '2026-01-15');
INSERT INTO enrollments VALUES (1, 101, '2026-01-15');   -- same student, different course
INSERT INTO enrollments VALUES (2, 100, '2026-01-15');   -- same course, different student

-- This fails — duplicate (student_id, course_id) tuple
INSERT INTO enrollments VALUES (1, 100, '2026-02-01');
-- ERROR: Duplicate entry '1-100' for key 'PRIMARY'</code></pre>

<p><strong>When to use composite keys</strong>:</p>
<ul>
  <li><strong>Junction tables</strong> for many-to-many relationships &mdash; <code>enrollments</code>, <code>tags_on_posts</code>, <code>users_in_groups</code>.</li>
  <li><strong>Natural composite identifiers</strong> &mdash; e.g., (year, month) for monthly summaries.</li>
  <li><strong>Compound business keys</strong> &mdash; (warehouse_id, sku) when SKUs are only unique within a warehouse.</li>
</ul>

<p><strong>Modern alternative</strong>: many teams add a synthetic <code>id INT AUTO_INCREMENT PRIMARY KEY</code> and put the natural composite as a UNIQUE constraint:</p>
<pre><code>CREATE TABLE enrollments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  course_id INT,
  enrolled_at DATE,
  UNIQUE KEY uk_enrollment (student_id, course_id)
);</code></pre>

<p>Pros: simpler foreign-key references from other tables; uniform ID column. Cons: extra index. The right choice depends on whether other tables need to reference enrollments.</p>

<p>The order of columns in a composite key matters for index performance &mdash; queries that filter by the leftmost column(s) use the index; queries that filter only by later columns can&rsquo;t.</p>
'''

ANSWERS[51] = r'''
<p>Declare a composite key by listing multiple columns in the <code>PRIMARY KEY</code> clause when creating the table. The combination of the listed columns must be unique.</p>

<pre><code>CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  quantity INT NOT NULL,
  PRIMARY KEY (order_id, product_id)
);</code></pre>

<p>Each <code>(order_id, product_id)</code> pair must be unique, but each individual column can repeat &mdash; an order can have many products, and a product can appear in many orders.</p>

<p>To add a composite key to an existing table:</p>

<pre><code>ALTER TABLE order_items
ADD PRIMARY KEY (order_id, product_id);</code></pre>

<p>For a composite <em>unique</em> key (not the primary key):</p>

<pre><code>CREATE TABLE enrollments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  course_id INT,
  semester VARCHAR(10),
  UNIQUE KEY uk_student_course_sem (student_id, course_id, semester)
);</code></pre>

<p><strong>Column order matters</strong> for the index that backs the key. MySQL can use a composite index <code>(a, b, c)</code> to satisfy queries on <code>(a)</code>, <code>(a, b)</code>, or <code>(a, b, c)</code> &mdash; but not on <code>(b)</code> alone or <code>(b, c)</code>. Put the most-frequently-filtered column first.</p>

<p><strong>When to use a composite key</strong>: junction tables for many-to-many relationships, natural keys made of multiple business identifiers, time-series data partitioned by date + entity. When in doubt, use a single auto-increment ID and add a composite UNIQUE constraint &mdash; simpler to reference from foreign keys.</p>
'''

ANSWERS[52] = r'''
<p><strong>Normalization</strong> is the process of organizing tables to reduce data redundancy and prevent update anomalies. The idea: store each fact in exactly one place. Normalization is achieved by following a series of rules called <em>normal forms</em>.</p>

<p><strong>The problem normalization solves</strong> &mdash; consider this denormalized table:</p>

<pre><code>orders
+----+----------+--------------+----------+--------+
| id | customer | customer_email| product  | price  |
+----+----------+--------------+----------+--------+
| 1  | Alice    | a@x.com      | Keyboard | 50     |
| 2  | Alice    | a@x.com      | Mouse    | 30     |
| 3  | Alice    | a@y.com      | Pad      | 10     |  ← inconsistent!
+----+----------+--------------+----------+--------+</code></pre>

<p>Customer info is duplicated, and a typo means Alice&rsquo;s email is now inconsistent. Updating Alice&rsquo;s email requires updating every order row.</p>

<p><strong>The normalized version</strong>:</p>

<pre><code>customers           orders
+----+-------+-----+   +----+-------------+----------+--------+
| id | name  |email|   | id | customer_id | product  | price  |
+----+-------+-----+   +----+-------------+----------+--------+
| 1  | Alice |a@x  |   | 1  | 1           | Keyboard | 50     |
+----+-------+-----+   | 2  | 1           | Mouse    | 30     |
                       | 3  | 1           | Pad      | 10     |
                       +----+-------------+----------+--------+</code></pre>

<p>Now Alice&rsquo;s email lives in exactly one row. Updating it changes one row.</p>

<p><strong>Benefits</strong>: less storage, no inconsistent duplicates, easier updates, smaller indexes. <strong>Trade-off</strong>: queries often need joins. For read-heavy analytics, denormalization is sometimes preferred for speed.</p>
'''

ANSWERS[53] = r'''
<p><strong>Normal forms</strong> are a sequence of rules &mdash; each builds on the previous. The first three are the most important; higher forms address rarer issues.</p>

<table>
  <tr><th>Form</th><th>Rule</th></tr>
  <tr><td><strong>1NF</strong> &mdash; First Normal Form</td><td>Each column holds a single atomic value; no lists or repeating groups.</td></tr>
  <tr><td><strong>2NF</strong> &mdash; Second Normal Form</td><td>1NF + every non-key column depends on the <em>whole</em> primary key (only matters with composite keys).</td></tr>
  <tr><td><strong>3NF</strong> &mdash; Third Normal Form</td><td>2NF + non-key columns depend only on the primary key, not on other non-key columns.</td></tr>
  <tr><td><strong>BCNF</strong></td><td>Stricter version of 3NF; every determinant must be a candidate key.</td></tr>
  <tr><td><strong>4NF</strong></td><td>Eliminates multi-valued dependencies.</td></tr>
  <tr><td><strong>5NF</strong></td><td>Eliminates join dependencies that aren&rsquo;t implied by candidate keys.</td></tr>
</table>

<p><strong>1NF violation</strong>: a single cell holding multiple values.</p>
<pre><code>-- ❌ Bad
+----+-------+----------------------+
| id | name  | phones               |
+----+-------+----------------------+
| 1  | Alice | "555-1111, 555-2222" |
+----+-------+----------------------+

-- ✅ Good — separate phones table
phones (user_id, phone)</code></pre>

<p><strong>3NF violation</strong>: <code>customer_zip</code> depends on <code>customer_city</code>, not on the order&rsquo;s primary key.</p>
<pre><code>-- ❌ Bad: orders(id, customer_id, customer_city, customer_zip)
-- ✅ Good: customers(id, city, zip);  orders(id, customer_id)</code></pre>

<p><strong>In practice</strong>, most application schemas aim for <strong>3NF</strong> &mdash; it eliminates the common anomalies without becoming impractical. BCNF and beyond rarely add value for typical apps.</p>
'''

ANSWERS[54] = r'''
<p><strong>Denormalization</strong> is the deliberate addition of redundant data to a normalized schema to improve read performance. Instead of joining tables to compute a value, you store the value directly &mdash; faster reads at the cost of duplicated data and harder updates.</p>

<p><strong>Example</strong> &mdash; a normalized schema requires a join to display recent orders with customer names:</p>

<pre><code>SELECT o.id, o.total, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
ORDER BY o.created_at DESC LIMIT 100;</code></pre>

<p>Denormalized version stores <code>customer_name</code> directly in <code>orders</code>:</p>

<pre><code>SELECT id, total, customer_name
FROM orders
ORDER BY created_at DESC LIMIT 100;
-- No join. Much faster on huge tables.</code></pre>

<p><strong>Common denormalization patterns</strong>:</p>
<ul>
  <li><strong>Cached aggregates</strong> &mdash; store <code>order_count</code> on the customer row instead of <code>SELECT COUNT(*) FROM orders</code> on every page load.</li>
  <li><strong>Materialized views</strong> &mdash; pre-computed result tables refreshed periodically.</li>
  <li><strong>Embedded copies</strong> &mdash; duplicate frequently-accessed columns to avoid joins.</li>
  <li><strong>Redundant flags</strong> &mdash; <code>has_active_subscription</code> on the user row instead of querying the subscriptions table.</li>
</ul>

<p><strong>Trade-offs</strong>: writes get more complex (every customer name change must update many order rows), and inconsistencies can creep in if the duplication isn&rsquo;t maintained correctly. Use triggers, application-layer logic, or scheduled jobs to keep denormalized data in sync.</p>

<p>Rule of thumb: <em>normalize until it hurts; denormalize until it works</em>. Start normalized, denormalize specific hot paths only when measurements show the join is the bottleneck.</p>
'''

ANSWERS[55] = r'''
<p>In MySQL, the words <strong>schema</strong> and <strong>database</strong> are synonyms &mdash; both refer to a collection of tables, views, indexes, and procedures grouped under a single name.</p>

<pre><code>-- These are equivalent in MySQL:
CREATE DATABASE shop;
CREATE SCHEMA shop;

SHOW DATABASES;  -- same as SHOW SCHEMAS;</code></pre>

<p>This is different from PostgreSQL or SQL Server, where a database can contain multiple schemas (namespaces within a database). In MySQL, there&rsquo;s only one level &mdash; the database itself <em>is</em> the schema.</p>

<p><strong>What a schema contains</strong>:</p>
<ul>
  <li>Tables and their data.</li>
  <li>Indexes and constraints.</li>
  <li>Views &mdash; saved queries that act like virtual tables.</li>
  <li>Stored procedures and functions.</li>
  <li>Triggers attached to tables.</li>
  <li>Permissions granted to users on the schema.</li>
</ul>

<p><strong>System schemas</strong> that MySQL creates automatically:</p>
<ul>
  <li><code>information_schema</code> &mdash; metadata about all schemas: tables, columns, indexes, etc.</li>
  <li><code>mysql</code> &mdash; user accounts and privilege tables.</li>
  <li><code>performance_schema</code> &mdash; runtime metrics and diagnostics.</li>
  <li><code>sys</code> &mdash; user-friendly views over performance_schema.</li>
</ul>

<p>Don&rsquo;t store application data in these &mdash; they&rsquo;re managed by MySQL itself.</p>

<p>The terms <strong>"schema design"</strong> or <strong>"schema migration"</strong> refer to how tables are structured and how you evolve that structure over time &mdash; the deliberate organization of your data model.</p>
'''

ANSWERS[56] = r'''
<p>Use the <code>USE</code> statement to switch the current database context. Subsequent unqualified table names will resolve against the chosen database.</p>

<pre><code>USE shop;

-- Now this query targets shop.users
SELECT * FROM users;</code></pre>

<p>List available databases first if you need to know which exist:</p>

<pre><code>SHOW DATABASES;</code></pre>

<p>You can also reference a table in a different database without switching by qualifying it with the database name:</p>

<pre><code>SELECT u.name, p.title
FROM shop.users u
JOIN blog.posts p ON p.author_id = u.id;</code></pre>

<p>This is essential for cross-database joins.</p>

<p><strong>Connecting with a default database</strong> &mdash; from the command line:</p>

<pre><code>mysql -u root -p shop
-- Connects and immediately enters USE shop;</code></pre>

<p><strong>From application code</strong>, connection strings usually include the database:</p>
<pre><code>mysql://user:pass@host:3306/shop</code></pre>

<p>The connector executes <code>USE shop</code> automatically on connect.</p>

<p><strong>Check the current database</strong>:</p>
<pre><code>SELECT DATABASE();
-- Returns 'shop' or NULL if no database is selected.</code></pre>

<p>If you forget <code>USE</code> and run an unqualified query, you&rsquo;ll get an error like <code>"No database selected"</code>. Always either set a default or fully-qualify table names.</p>
'''

ANSWERS[57] = r'''
<p>Use <code>SHOW TABLES</code>. It lists all tables in the currently-selected database.</p>

<pre><code>USE shop;
SHOW TABLES;

+----------------+
| Tables_in_shop |
+----------------+
| customers      |
| order_items    |
| orders         |
| products       |
+----------------+</code></pre>

<p>To see tables in a different database without switching:</p>

<pre><code>SHOW TABLES FROM blog;</code></pre>

<p><strong>Filter by name pattern</strong>:</p>
<pre><code>SHOW TABLES LIKE 'order%';</code></pre>

<p><strong>Include views</strong> with <code>FULL</code>, which adds a <code>Table_type</code> column:</p>
<pre><code>SHOW FULL TABLES;

+----------------+------------+
| Tables_in_shop | Table_type |
+----------------+------------+
| customers      | BASE TABLE |
| recent_orders  | VIEW       |
+----------------+------------+</code></pre>

<p><strong>Programmatic access via information_schema</strong> &mdash; better for scripts because the column names are stable:</p>

<pre><code>SELECT TABLE_NAME, TABLE_TYPE, ENGINE, TABLE_ROWS
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop';</code></pre>

<p>This is the SQL-standard way; it works in many databases, not just MySQL.</p>

<p><strong>Get row counts and sizes</strong> for capacity planning:</p>

<pre><code>SELECT TABLE_NAME,
       TABLE_ROWS,
       ROUND(DATA_LENGTH / 1024 / 1024, 2) AS size_mb
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop'
ORDER BY DATA_LENGTH DESC;</code></pre>

<p>Note that <code>TABLE_ROWS</code> for InnoDB tables is an estimate, not exact. For an exact count run <code>SELECT COUNT(*) FROM users</code>.</p>
'''

ANSWERS[58] = r'''
<p>Use <code>DESCRIBE</code> (or its short form <code>DESC</code>) to see column names, types, nullability, keys, defaults, and extras.</p>

<pre><code>DESCRIBE users;
-- or
DESC users;

+------------+--------------+------+-----+-------------------+----------------+
| Field      | Type         | Null | Key | Default           | Extra          |
+------------+--------------+------+-----+-------------------+----------------+
| id         | int          | NO   | PRI | NULL              | auto_increment |
| email      | varchar(255) | NO   | UNI | NULL              |                |
| name       | varchar(100) | YES  |     | NULL              |                |
| created_at | datetime     | NO   |     | CURRENT_TIMESTAMP |                |
+------------+--------------+------+-----+-------------------+----------------+</code></pre>

<p>Equivalent SQL standard syntax:</p>
<pre><code>SHOW COLUMNS FROM users;</code></pre>

<p><strong>To see the full <code>CREATE TABLE</code> statement</strong> &mdash; useful when you want to recreate the table elsewhere or diff schemas:</p>

<pre><code>SHOW CREATE TABLE users\G

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;</code></pre>

<p>(The <code>\G</code> at the end is a mysql-client-only feature that displays results vertically &mdash; cleaner for wide rows.)</p>

<p><strong>Programmatic detail via information_schema</strong>:</p>

<pre><code>SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, CHARACTER_MAXIMUM_LENGTH
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'shop' AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;</code></pre>

<p><strong>For indexes specifically</strong> &mdash; <code>SHOW INDEX FROM users</code> lists every index on the table including the primary key.</p>
'''

ANSWERS[59] = r'''
<p>Use <code>RENAME TABLE</code>:</p>

<pre><code>RENAME TABLE old_name TO new_name;</code></pre>

<p>Concrete example:</p>

<pre><code>RENAME TABLE customers TO clients;</code></pre>

<p><strong>Rename multiple tables atomically</strong> in a single statement:</p>

<pre><code>RENAME TABLE
  users TO users_old,
  users_new TO users;</code></pre>

<p>This is the standard pattern for a <strong>zero-downtime swap</strong>: build <code>users_new</code> populated with cleaned data, then atomically swap the names. Application connections see no gap because both renames happen as one operation.</p>

<p><strong>Move a table to another database</strong> by qualifying the destination:</p>

<pre><code>RENAME TABLE shop.legacy_orders TO archive.legacy_orders;</code></pre>

<p>Both source and target schemas must be on the same MySQL server.</p>

<p><strong>Equivalent ALTER syntax</strong>:</p>
<pre><code>ALTER TABLE customers RENAME TO clients;</code></pre>

<p>Both work. <code>RENAME TABLE</code> is preferred for the multi-table atomic case.</p>

<p><strong>Caveats</strong>:</p>
<ul>
  <li>Foreign keys referencing the old name are automatically updated to point to the new name.</li>
  <li>Views and stored procedures referencing the old name are <em>not</em> updated &mdash; they break until you fix them.</li>
  <li>The renaming user needs <code>ALTER</code> and <code>DROP</code> privileges on the old table and <code>CREATE</code> and <code>INSERT</code> on the new.</li>
  <li>Application code must also be updated &mdash; rename the table in code at the same time, or use a view as a compatibility layer during a transition.</li>
</ul>
'''

ANSWERS[60] = r'''
<p>Use <code>ALTER TABLE ... ADD COLUMN</code>:</p>

<pre><code>ALTER TABLE users
ADD COLUMN phone VARCHAR(20);</code></pre>

<p><strong>Specify position</strong> &mdash; by default the new column is added at the end. Use <code>FIRST</code> or <code>AFTER</code> to control placement:</p>

<pre><code>ALTER TABLE users
ADD COLUMN phone VARCHAR(20) AFTER email;

ALTER TABLE users
ADD COLUMN id_v2 BIGINT FIRST;</code></pre>

<p><strong>Add multiple columns in one statement</strong> &mdash; faster than separate ALTERs because the table is rebuilt only once:</p>

<pre><code>ALTER TABLE users
  ADD COLUMN phone VARCHAR(20),
  ADD COLUMN country_code CHAR(2),
  ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;</code></pre>

<p><strong>With NOT NULL on a populated table</strong>, you must provide a default &mdash; otherwise existing rows would have no value:</p>

<pre><code>ALTER TABLE users
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active';</code></pre>

<p><strong>Performance considerations</strong>: on large tables, an <code>ALTER TABLE</code> can lock the table or rebuild it entirely &mdash; potentially hours of downtime. MySQL 8 supports <strong>instant ADD COLUMN</strong> for many cases (the metadata changes without touching data):</p>

<pre><code>ALTER TABLE huge_table
ADD COLUMN new_col INT,
ALGORITHM=INSTANT;</code></pre>

<p>For online schema changes on production tables, use tools like <strong>pt-online-schema-change</strong> (Percona) or <strong>gh-ost</strong> (GitHub&rsquo;s tool) which copy the table in the background and atomically swap.</p>
'''

ANSWERS[61] = r'''
<p>Use <code>ALTER TABLE ... DROP COLUMN</code>:</p>

<pre><code>ALTER TABLE users
DROP COLUMN phone;</code></pre>

<p><strong>Drop multiple columns</strong> in one statement:</p>

<pre><code>ALTER TABLE users
  DROP COLUMN phone,
  DROP COLUMN fax,
  DROP COLUMN legacy_id;</code></pre>

<p><strong>This is destructive</strong>: dropping a column permanently deletes the data in it. There&rsquo;s no <code>UNDO</code>. Take a backup first if there&rsquo;s any chance you&rsquo;ll need the data.</p>

<p><strong>Constraints to watch out for</strong>:</p>
<ul>
  <li><strong>Indexes</strong> on the column &mdash; dropped automatically when the column is dropped.</li>
  <li><strong>Foreign keys</strong> referencing the column &mdash; you must drop the FK constraint first, or MySQL will refuse:
<pre><code>ALTER TABLE orders DROP FOREIGN KEY fk_user;
ALTER TABLE users DROP COLUMN id;
-- (you wouldn&rsquo;t actually drop the user id column; this is just an example)</code></pre>
  </li>
  <li><strong>Views, triggers, stored procedures</strong> that reference the column &mdash; not dropped automatically; will break.</li>
</ul>

<p><strong>Performance</strong>: like adding columns, dropping a column on a large table can lock it for a long time. MySQL 8 supports <code>ALGORITHM=INPLACE</code> which is faster than the default copy approach:</p>

<pre><code>ALTER TABLE huge_table
DROP COLUMN unused_col,
ALGORITHM=INPLACE, LOCK=NONE;</code></pre>

<p><strong>Safer pattern in production</strong>: stop writing to the column from application code, deploy and verify, <em>then</em> drop it later. If you drop first and find the column was still being read somewhere, you&rsquo;ve broken production.</p>
'''

ANSWERS[62] = r'''
<p>Use <code>ALTER TABLE ... MODIFY COLUMN</code> to change a column&rsquo;s type, nullability, or default. Use <code>CHANGE COLUMN</code> to also rename the column.</p>

<pre><code>-- Change type / size only
ALTER TABLE users
MODIFY COLUMN name VARCHAR(200);

-- Change type AND rename
ALTER TABLE users
CHANGE COLUMN name full_name VARCHAR(200);</code></pre>

<p><strong>Common modifications</strong>:</p>

<pre><code>-- Add NOT NULL with a default for existing rows
ALTER TABLE users
MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active';

-- Increase column size (always safe)
ALTER TABLE products
MODIFY COLUMN description TEXT;

-- Change to a different type — risky if data won&rsquo;t fit
ALTER TABLE orders
MODIFY COLUMN total DECIMAL(10, 2);

-- Add a default
ALTER TABLE users
MODIFY COLUMN role VARCHAR(20) DEFAULT 'member';</code></pre>

<p><strong>Risks of type changes</strong>:</p>
<ul>
  <li><strong>Truncation</strong>: shrinking <code>VARCHAR(255)</code> to <code>VARCHAR(50)</code> on a column with longer values truncates them or fails. Run <code>SELECT MAX(LENGTH(col)) FROM tbl</code> first.</li>
  <li><strong>Conversion</strong>: changing <code>INT</code> to <code>VARCHAR</code> reformats the data. Going the other way fails if values aren&rsquo;t parseable as integers.</li>
  <li><strong>Charset / collation changes</strong> can take a long time and may need <code>CONVERT TO CHARACTER SET</code>.</li>
</ul>

<p><strong>For production safety</strong>: do the change in a staging environment first; test that constraints, foreign keys, and queries still work; for very large tables use online-schema-change tools (<code>pt-osc</code>, <code>gh-ost</code>) so the change is non-blocking.</p>

<p><strong>Note</strong>: when modifying, you must restate the full column definition each time &mdash; MySQL doesn&rsquo;t merge changes. <code>MODIFY COLUMN name VARCHAR(200)</code> drops the old <code>NOT NULL</code> if you don&rsquo;t restate it.</p>
'''

ANSWERS[63] = r'''
<p><strong>CHAR</strong> stores fixed-length strings, padded with spaces to fill the declared length. <strong>VARCHAR</strong> stores variable-length strings &mdash; only the actual content plus a 1- or 2-byte length prefix.</p>

<table>
  <tr><th>Aspect</th><th>CHAR(N)</th><th>VARCHAR(N)</th></tr>
  <tr><td>Storage</td><td>Always N bytes (padded with spaces)</td><td>Actual length + 1 or 2 bytes overhead</td></tr>
  <tr><td>Trailing spaces</td><td>Stripped on retrieval</td><td>Preserved</td></tr>
  <tr><td>Max length</td><td>255</td><td>65,535 (subject to row size limit)</td></tr>
  <tr><td>Best for</td><td>Fixed-width values: country codes, status flags</td><td>Variable-length: names, emails, descriptions</td></tr>
</table>

<pre><code>CREATE TABLE users (
  country_code CHAR(2),       -- always 2 chars: 'US', 'IN', 'GB'
  email        VARCHAR(255),  -- variable length
  status       CHAR(8)        -- 'active' / 'pending' (padded to 8)
);</code></pre>

<p><strong>Behavior example</strong>:</p>
<pre><code>INSERT INTO users (country_code, email)
VALUES ('US', 'a@x.com');

-- country_code is stored as 'US' (2 bytes used).
-- If declared CHAR(5), it would be stored as 'US   ' (5 bytes,
-- padded). On SELECT, MySQL returns 'US' (trailing spaces stripped).</code></pre>

<p><strong>When to choose which</strong>:</p>
<ul>
  <li>Use <strong>CHAR</strong> for genuinely fixed-width columns: 2-letter country codes, 5-character ZIP, MD5 hashes (32 chars), UUIDs (36 chars). Slightly faster index lookups for small fixed values.</li>
  <li>Use <strong>VARCHAR</strong> for everything else &mdash; saves storage when most values are shorter than the maximum.</li>
</ul>

<p><strong>Modern advice</strong>: prefer VARCHAR by default. CHAR&rsquo;s storage savings rarely matter today, and the trailing-space stripping behavior is a frequent source of bugs.</p>
'''

ANSWERS[64] = r'''
<p><code>CONCAT</code> joins two or more strings into one. Pass any number of arguments &mdash; they&rsquo;re concatenated in order.</p>

<pre><code>SELECT CONCAT('Hello, ', 'world!') AS greeting;
-- greeting: Hello, world!

SELECT CONCAT(first_name, ' ', last_name) AS full_name
FROM users;</code></pre>

<p><strong>Watch out for NULL</strong>: if any argument is <code>NULL</code>, <code>CONCAT</code> returns <code>NULL</code>. This commonly produces empty-looking results.</p>

<pre><code>SELECT CONCAT('Mr. ', NULL, ' Smith');  -- NULL, not 'Mr.  Smith'</code></pre>

<p><strong>Use <code>CONCAT_WS</code></strong> (concatenate with separator) when joining multiple parts with a delimiter &mdash; it skips NULLs:</p>

<pre><code>SELECT CONCAT_WS(' ', first_name, middle_name, last_name) AS full_name
FROM users;
-- For ('Alice', NULL, 'Smith') → 'Alice Smith' (no extra space)</code></pre>

<p>The first argument is the separator, applied between each non-NULL value.</p>

<p><strong>Convert non-strings</strong> &mdash; CONCAT auto-casts numbers and dates to strings:</p>

<pre><code>SELECT CONCAT('Order #', id, ' total: $', total)
FROM orders;
-- 'Order #1234 total: $59.99'</code></pre>

<p><strong>Common uses</strong>:</p>
<ul>
  <li>Build full names, addresses, identifiers from parts.</li>
  <li>Generate <code>LIKE</code> patterns dynamically: <code>WHERE email LIKE CONCAT(%, ?, %)</code>.</li>
  <li>Create user-facing labels in queries.</li>
  <li>Generate slugs or display names in views.</li>
</ul>

<p>The <code>||</code> operator is SQL-standard string concatenation, but in MySQL <code>||</code> defaults to logical OR. Use <code>CONCAT</code> for portability.</p>
'''

ANSWERS[65] = r'''
<p>The <code>LIKE</code> operator filters rows based on a string pattern. It uses two wildcards:</p>

<table>
  <tr><th>Wildcard</th><th>Matches</th></tr>
  <tr><td><code>%</code></td><td>Zero or more characters</td></tr>
  <tr><td><code>_</code></td><td>Exactly one character</td></tr>
</table>

<pre><code>-- Names starting with 'A'
SELECT * FROM users WHERE name LIKE 'A%';

-- Names containing 'son'
SELECT * FROM users WHERE name LIKE '%son%';

-- Names ending with 'er'
SELECT * FROM users WHERE name LIKE '%er';

-- 5-letter names starting with 'J'
SELECT * FROM users WHERE name LIKE 'J____';

-- Phone numbers like 555-XXXX
SELECT * FROM users WHERE phone LIKE '555-____';</code></pre>

<p><strong>Case sensitivity</strong> depends on the column&rsquo;s collation. The default <code>utf8mb4_0900_ai_ci</code> is case-insensitive (<code>ci</code>) and accent-insensitive (<code>ai</code>): <code>LIKE 'a%'</code> matches both <code>Alice</code> and <code>alice</code>. For case-sensitive matching, use a binary collation: <code>LIKE 'A%' COLLATE utf8mb4_bin</code>.</p>

<p><strong>NOT LIKE</strong> negates the match:</p>
<pre><code>SELECT * FROM users WHERE email NOT LIKE '%@example.com';</code></pre>

<p><strong>Escape literal % or _</strong> using a backslash or a custom <code>ESCAPE</code> character:</p>
<pre><code>SELECT * FROM products WHERE name LIKE '50\% off%';
SELECT * FROM products WHERE name LIKE '50!%off%' ESCAPE '!';</code></pre>

<p><strong>Performance</strong>: <code>LIKE 'pattern%'</code> (anchored at the start) can use a B-tree index. <code>LIKE '%pattern'</code> or <code>LIKE '%pattern%'</code> cannot &mdash; MySQL must scan every row. For full-text or substring search on large tables, use <code>FULLTEXT</code> indexes or a dedicated search engine like Elasticsearch / Meilisearch.</p>
'''

ANSWERS[66] = r'''
<p>The <code>IN</code> operator filters rows where a column matches any value in a given list. Cleaner than chaining many <code>OR</code> conditions.</p>

<pre><code>-- Verbose
SELECT * FROM users
WHERE country = 'US' OR country = 'UK' OR country = 'CA';

-- Equivalent with IN
SELECT * FROM users
WHERE country IN ('US', 'UK', 'CA');</code></pre>

<p><strong>NOT IN</strong> excludes the listed values:</p>

<pre><code>SELECT * FROM products WHERE status NOT IN ('archived', 'draft');</code></pre>

<p><strong>IN with a subquery</strong> &mdash; very common pattern, get rows where another query returns matching keys:</p>

<pre><code>-- Users who have placed orders in the last 30 days
SELECT * FROM users
WHERE id IN (
  SELECT DISTINCT user_id FROM orders
  WHERE created_at &gt; NOW() - INTERVAL 30 DAY
);</code></pre>

<p><strong>NULL gotcha with NOT IN</strong>: if the subquery returns any <code>NULL</code>, <code>NOT IN</code> evaluates to <code>NULL</code> for every row &mdash; so the outer query returns nothing. Always filter NULLs out:</p>

<pre><code>-- Wrong: returns nothing if any row in some_table has NULL col
SELECT * FROM users
WHERE id NOT IN (SELECT user_id FROM some_table);

-- Right: explicitly exclude NULLs
SELECT * FROM users
WHERE id NOT IN (SELECT user_id FROM some_table WHERE user_id IS NOT NULL);

-- Better: use NOT EXISTS, which handles NULLs correctly
SELECT * FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM some_table s WHERE s.user_id = u.id
);</code></pre>

<p><strong>Performance</strong>: with a small list, <code>IN</code> is fast and often uses an index. With a huge list (thousands of values), it can be slower than a join &mdash; consider loading the list into a temp table and joining instead.</p>

<p>From application code, always <strong>parameterize</strong> &mdash; never build <code>IN ('a', 'b', 'c')</code> from user input by string concatenation, as this is a SQL injection vector.</p>
'''

ANSWERS[67] = r'''
<p>Both filter rows, but they apply at different stages of query processing. <strong>WHERE</strong> filters rows <em>before</em> grouping; <strong>HAVING</strong> filters groups <em>after</em> aggregation.</p>

<pre><code>-- WHERE filters individual rows BEFORE GROUP BY
SELECT department, COUNT(*) AS staff_count
FROM employees
WHERE active = 1            -- only active employees considered
GROUP BY department;</code></pre>

<pre><code>-- HAVING filters groups AFTER GROUP BY
SELECT department, COUNT(*) AS staff_count
FROM employees
WHERE active = 1
GROUP BY department
HAVING COUNT(*) &gt; 10;       -- only departments with &gt;10 active staff</code></pre>

<p><strong>Key rules</strong>:</p>
<ul>
  <li><code>WHERE</code> cannot reference aggregate functions like <code>COUNT()</code> or <code>SUM()</code> &mdash; they don&rsquo;t exist yet at that stage.</li>
  <li><code>HAVING</code> can reference aggregates and grouped columns.</li>
  <li>For non-aggregated row filtering, prefer <code>WHERE</code> &mdash; it&rsquo;s evaluated earlier and benefits more from indexes.</li>
</ul>

<p><strong>Order in a SELECT</strong>:</p>

<pre><code>SELECT  ...
FROM    ...
WHERE   ...    -- filter rows
GROUP BY ...   -- combine into groups
HAVING  ...    -- filter groups
ORDER BY ...   -- sort results
LIMIT   ...    -- cap output</code></pre>

<p><strong>Combined example</strong>:</p>

<pre><code>SELECT category,
       SUM(amount) AS total_revenue
FROM sales
WHERE created_at &gt;= '2026-01-01'    -- pre-aggregation filter
GROUP BY category
HAVING SUM(amount) &gt; 100000          -- post-aggregation filter
ORDER BY total_revenue DESC;</code></pre>

<p>Reads as: from 2026 sales, group by category, keep only categories whose total exceeds $100K, sort highest first.</p>

<p><strong>Performance</strong>: filtering early via <code>WHERE</code> means fewer rows are aggregated &mdash; almost always faster. Use <code>HAVING</code> only for conditions that genuinely need aggregate values.</p>
'''

ANSWERS[68] = r'''
<p><code>GROUP BY</code> collapses rows that share values in the listed columns into a single row, allowing aggregate functions (<code>COUNT</code>, <code>SUM</code>, <code>AVG</code>, etc.) to compute over each group.</p>

<pre><code>-- Total sales per category
SELECT category, SUM(amount) AS total_sales
FROM orders
GROUP BY category;

-- category | total_sales
-- ---------|------------
-- Books    |  1240.00
-- Electronics| 8800.50
-- Clothing |  4310.25</code></pre>

<p><strong>Group by multiple columns</strong> &mdash; rows are combined only when <em>all</em> listed columns match:</p>

<pre><code>SELECT country, city, COUNT(*) AS users
FROM users
GROUP BY country, city
ORDER BY country, city;</code></pre>

<p><strong>Aggregate functions</strong> commonly paired with <code>GROUP BY</code>:</p>

<table>
  <tr><th>Function</th><th>Returns</th></tr>
  <tr><td><code>COUNT(*)</code></td><td>Number of rows in the group</td></tr>
  <tr><td><code>COUNT(col)</code></td><td>Non-NULL values in <code>col</code></td></tr>
  <tr><td><code>SUM(col)</code></td><td>Sum of numeric values</td></tr>
  <tr><td><code>AVG(col)</code></td><td>Average</td></tr>
  <tr><td><code>MIN(col)</code> / <code>MAX(col)</code></td><td>Smallest / largest value</td></tr>
  <tr><td><code>GROUP_CONCAT(col)</code></td><td>Concatenated list of values</td></tr>
</table>

<p><strong>Selecting non-aggregated columns</strong> not in <code>GROUP BY</code> is invalid in standard SQL. MySQL strict mode (<code>ONLY_FULL_GROUP_BY</code>, default since 5.7) enforces this. Workarounds: include them in <code>GROUP BY</code>, or use <code>MIN()</code>/<code>MAX()</code>/<code>ANY_VALUE()</code> on them.</p>

<pre><code>-- Strict-mode-safe
SELECT customer_id, COUNT(*), MAX(created_at) AS last_order
FROM orders
GROUP BY customer_id;</code></pre>

<p><strong>Filter groups with HAVING</strong>; sort with <code>ORDER BY</code>:</p>

<pre><code>SELECT category, SUM(amount) AS total
FROM orders
GROUP BY category
HAVING total &gt; 1000
ORDER BY total DESC;</code></pre>
'''

ANSWERS[69] = r'''
<p><code>ORDER BY</code> sorts the result rows by one or more columns. Default direction is ascending (<code>ASC</code>); use <code>DESC</code> for descending.</p>

<pre><code>-- Ascending by name
SELECT * FROM users ORDER BY name;

-- Descending by signup date (newest first)
SELECT * FROM users ORDER BY created_at DESC;

-- Multi-column sort: country ascending, then city ascending
SELECT * FROM users ORDER BY country ASC, city ASC;

-- Mixed directions
SELECT * FROM users ORDER BY country ASC, created_at DESC;</code></pre>

<p><strong>Sort by computed expressions or aggregates</strong>:</p>

<pre><code>-- Sort by a derived column (alias is allowed in MySQL)
SELECT name, LENGTH(name) AS len
FROM users
ORDER BY len DESC;

-- Sort by aggregate
SELECT category, SUM(amount) AS total
FROM orders
GROUP BY category
ORDER BY total DESC;</code></pre>

<p><strong>Sort by column position</strong> &mdash; allowed but discouraged:</p>

<pre><code>SELECT name, email, created_at
FROM users
ORDER BY 3 DESC;  -- 3rd column = created_at</code></pre>

<p>Position-based sorting is brittle &mdash; if you reorder columns, the meaning changes silently. Use column names.</p>

<p><strong>NULL handling</strong>: in MySQL, <code>NULL</code> values sort first in ascending order and last in descending. To force them to the bottom:</p>

<pre><code>SELECT * FROM users ORDER BY last_login IS NULL, last_login DESC;</code></pre>

<p>(<code>IS NULL</code> evaluates to 0 for non-NULL and 1 for NULL, so non-NULLs sort first.)</p>

<p><strong>Performance</strong>: sorting can be expensive on large result sets. An index that matches the <code>ORDER BY</code> can let MySQL skip a separate sort step. <code>EXPLAIN</code> output shows <code>Using filesort</code> when MySQL has to sort manually &mdash; fine for small results, slow for huge ones.</p>

<p>Always combine with <code>LIMIT</code> when paging through long results &mdash; otherwise you transmit and sort everything just to discard most of it.</p>
'''

ANSWERS[70] = r'''
<p><code>LIMIT</code> caps the number of rows returned. Often combined with <code>OFFSET</code> for pagination &mdash; skip a number of rows before returning.</p>

<pre><code>-- First 10 rows
SELECT * FROM products ORDER BY id LIMIT 10;

-- Skip 20, return next 10 (page 3 if page size is 10)
SELECT * FROM products ORDER BY id LIMIT 10 OFFSET 20;

-- Compact form: LIMIT offset, count
SELECT * FROM products ORDER BY id LIMIT 20, 10;</code></pre>

<p>Note the compact form&rsquo;s argument order: offset first, count second &mdash; opposite of the explicit <code>LIMIT count OFFSET offset</code> form.</p>

<p><strong>Always use ORDER BY with LIMIT</strong>. Without it, the row order is unspecified &mdash; "page 1" and "page 2" might overlap or skip rows on different runs.</p>

<p><strong>Pagination performance pitfall</strong>: deep offsets become slow. <code>LIMIT 10 OFFSET 100000</code> means MySQL fetches and discards 100,000 rows before returning 10 &mdash; cost grows linearly with offset.</p>

<p><strong>Solution: keyset pagination</strong> (also called "seek method"):</p>

<pre><code>-- Page 1 — fetch first 10
SELECT id, name, created_at FROM products
ORDER BY created_at DESC, id DESC
LIMIT 10;

-- Page 2 — pass the last seen values from page 1
SELECT id, name, created_at FROM products
WHERE (created_at, id) &lt; ('2026-04-15 12:34:56', 5523)
ORDER BY created_at DESC, id DESC
LIMIT 10;</code></pre>

<p>Each page directly looks up where the previous one left off &mdash; constant time regardless of how deep you page. This is how Twitter, Slack, and most modern feeds paginate.</p>

<p><strong>Common idioms</strong>:</p>

<pre><code>-- Get a single row (e.g., latest)
SELECT * FROM events ORDER BY created_at DESC LIMIT 1;

-- Sample without sort (any 5 rows; useful for spot-checking)
SELECT * FROM users LIMIT 5;</code></pre>
'''

ANSWERS[71] = r'''
<p>Use the <code>MAX()</code> aggregate function. Returns the largest value in the column &mdash; ignoring <code>NULL</code>s.</p>

<pre><code>-- Highest order total ever
SELECT MAX(total) FROM orders;

-- Most recent order date
SELECT MAX(created_at) FROM orders;</code></pre>

<p><strong>Combined with GROUP BY</strong> &mdash; max value per group:</p>

<pre><code>-- Max total per customer
SELECT customer_id, MAX(total) AS biggest_order
FROM orders
GROUP BY customer_id;</code></pre>

<p><strong>To return the row containing the maximum</strong> (not just the value), one common pattern is using a subquery:</p>

<pre><code>-- The single highest-value order
SELECT *
FROM orders
WHERE total = (SELECT MAX(total) FROM orders);</code></pre>

<p>Note this returns multiple rows if there&rsquo;s a tie. To handle ties or get one definitively:</p>

<pre><code>SELECT * FROM orders ORDER BY total DESC LIMIT 1;</code></pre>

<p><strong>Per-group maximum row</strong> &mdash; "the most expensive product in each category" &mdash; uses a window function (MySQL 8+):</p>

<pre><code>SELECT *
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rn
  FROM products
) ranked
WHERE rn = 1;</code></pre>

<p><strong>Works with non-numeric types</strong>:</p>

<pre><code>SELECT MAX(name) FROM users;        -- alphabetically last
SELECT MAX(created_at) FROM orders; -- most recent date/time</code></pre>

<p><strong>Performance</strong>: <code>MAX()</code> on an indexed column is very fast &mdash; MySQL reads the last (or first for <code>MIN</code>) entry of the index without scanning. <code>EXPLAIN</code> shows <code>Select tables optimized away</code>.</p>
'''

ANSWERS[72] = r'''
<p>Use the <code>MIN()</code> aggregate function. Returns the smallest value, ignoring <code>NULL</code>s. Mirrors <code>MAX</code> exactly.</p>

<pre><code>-- Cheapest product
SELECT MIN(price) FROM products;

-- Earliest signup date
SELECT MIN(created_at) FROM users;

-- First alphabetical name
SELECT MIN(name) FROM users;</code></pre>

<p><strong>With GROUP BY</strong> &mdash; minimum value per group:</p>

<pre><code>-- Cheapest item per category
SELECT category, MIN(price) AS cheapest
FROM products
GROUP BY category;</code></pre>

<p><strong>Filter on aggregate result with HAVING</strong>:</p>

<pre><code>-- Categories where the cheapest item is over $100
SELECT category, MIN(price) AS cheapest
FROM products
GROUP BY category
HAVING MIN(price) &gt; 100;</code></pre>

<p><strong>Get the row with the minimum value</strong> &mdash; either via subquery or <code>ORDER BY ... LIMIT 1</code>:</p>

<pre><code>-- All rows tied for the minimum
SELECT *
FROM products
WHERE price = (SELECT MIN(price) FROM products);

-- Just one row, definitively
SELECT *
FROM products
ORDER BY price ASC, id ASC
LIMIT 1;</code></pre>

<p><strong>NULL handling</strong>: <code>MIN</code> ignores <code>NULL</code>. If <em>all</em> values are NULL, <code>MIN</code> returns <code>NULL</code>. If the column is empty (no rows), <code>MIN</code> returns <code>NULL</code> as well.</p>

<pre><code>SELECT MIN(price) FROM products WHERE category = 'rare-stamps';
-- Returns NULL if no products in that category, not 0.</code></pre>

<p>Use <code>COALESCE(MIN(price), 0)</code> if you need <code>NULL</code> to display as something else.</p>

<p><strong>Performance</strong>: like <code>MAX</code>, <code>MIN</code> on an indexed column is essentially free &mdash; MySQL reads the first index entry directly.</p>
'''

ANSWERS[73] = r'''
<p>Use the <code>AVG()</code> aggregate function. Returns the arithmetic mean of the values, ignoring <code>NULL</code>.</p>

<pre><code>-- Average product price
SELECT AVG(price) FROM products;

-- Average order total in 2026
SELECT AVG(total) FROM orders
WHERE YEAR(created_at) = 2026;</code></pre>

<p><strong>With GROUP BY</strong> &mdash; average per group:</p>

<pre><code>-- Average price per category
SELECT category, AVG(price) AS avg_price
FROM products
GROUP BY category
ORDER BY avg_price DESC;</code></pre>

<p><strong>Round the result for display</strong>:</p>

<pre><code>SELECT category, ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category;</code></pre>

<p><strong>NULL handling</strong>: <code>AVG</code> ignores NULLs in both the numerator and denominator. <code>AVG(price)</code> over 5 rows where 2 prices are NULL averages over the 3 non-NULL values, not 5.</p>

<pre><code>-- If you want NULLs to count as 0 in the average:
SELECT AVG(COALESCE(price, 0)) FROM products;</code></pre>

<p><strong>AVG of conditional values</strong> &mdash; common pattern for percentages and rates:</p>

<pre><code>-- Conversion rate: fraction of users who placed an order
SELECT AVG(CASE WHEN order_count &gt; 0 THEN 1 ELSE 0 END) AS conversion_rate
FROM users;
-- Result like 0.234 (= 23.4%)</code></pre>

<p><strong>Result type</strong>: <code>AVG</code> on integer columns returns a <code>DECIMAL</code> &mdash; <code>AVG(1, 2, 4) = 2.3333</code>, not <code>2</code>. If you need integer division behavior, cast: <code>FLOOR(AVG(col))</code>.</p>

<p><strong>For median, mode, percentiles</strong>: there&rsquo;s no built-in <code>MEDIAN()</code> in MySQL. Use window functions (<code>PERCENT_RANK</code>, <code>NTILE</code>) or compute application-side. AVG is mean only.</p>
'''

ANSWERS[74] = r'''
<p>Use the <code>COUNT()</code> aggregate function. There are three common forms with subtly different behaviors.</p>

<pre><code>-- All rows in the table
SELECT COUNT(*) FROM users;

-- Non-NULL values in a specific column
SELECT COUNT(email) FROM users;

-- Distinct non-NULL values in a column
SELECT COUNT(DISTINCT country) FROM users;</code></pre>

<table>
  <tr><th>Form</th><th>Counts</th></tr>
  <tr><td><code>COUNT(*)</code></td><td>All rows, including those where every column is NULL</td></tr>
  <tr><td><code>COUNT(col)</code></td><td>Rows where <code>col IS NOT NULL</code></td></tr>
  <tr><td><code>COUNT(DISTINCT col)</code></td><td>Unique non-NULL values</td></tr>
  <tr><td><code>COUNT(1)</code></td><td>Same as <code>COUNT(*)</code> &mdash; no performance difference in modern MySQL</td></tr>
</table>

<p><strong>With WHERE clause</strong>:</p>

<pre><code>-- Active users
SELECT COUNT(*) FROM users WHERE active = 1;

-- Recent signups
SELECT COUNT(*) FROM users
WHERE created_at &gt; NOW() - INTERVAL 7 DAY;</code></pre>

<p><strong>Conditional counts</strong> &mdash; count rows matching a condition without filtering the whole query:</p>

<pre><code>SELECT
  COUNT(*) AS total_users,
  COUNT(CASE WHEN active = 1 THEN 1 END) AS active_users,
  SUM(active) AS active_users_alt    -- works because active is 0 or 1
FROM users;</code></pre>

<p><strong>Per-group counts</strong>:</p>

<pre><code>SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country
ORDER BY user_count DESC;</code></pre>

<p><strong>Performance note</strong>: on InnoDB, <code>COUNT(*)</code> without a <code>WHERE</code> clause requires scanning rows or an index &mdash; not instant on huge tables. For approximate counts, <code>information_schema.TABLES.TABLE_ROWS</code> gives a fast estimate. For exact counts of huge tables, maintain a counter column updated by triggers, or accept the scan cost.</p>
'''

ANSWERS[75] = r'''
<p>Use the <code>SUM()</code> aggregate function. Adds up numeric values, ignoring <code>NULL</code>s.</p>

<pre><code>-- Total revenue
SELECT SUM(total) FROM orders;

-- Revenue from a specific period
SELECT SUM(total) FROM orders
WHERE created_at BETWEEN '2026-01-01' AND '2026-04-01';</code></pre>

<p><strong>With GROUP BY</strong> &mdash; sum per group:</p>

<pre><code>-- Total revenue per customer
SELECT customer_id, SUM(total) AS lifetime_value
FROM orders
GROUP BY customer_id
ORDER BY lifetime_value DESC
LIMIT 10;</code></pre>

<p><strong>Conditional sum</strong> &mdash; sum only when a condition is met:</p>

<pre><code>-- Revenue from completed orders only
SELECT
  SUM(CASE WHEN status = 'completed' THEN total ELSE 0 END) AS completed_revenue,
  SUM(CASE WHEN status = 'refunded'  THEN total ELSE 0 END) AS refunded_revenue
FROM orders;</code></pre>

<p>This pattern is heavily used in dashboards &mdash; one query produces multiple aggregated values.</p>

<p><strong>Empty / NULL results</strong>: <code>SUM</code> over zero rows returns <code>NULL</code>, not 0. Wrap with <code>COALESCE</code> for display:</p>

<pre><code>SELECT COALESCE(SUM(total), 0) AS revenue
FROM orders
WHERE customer_id = 999;</code></pre>

<p><strong>Result type and precision</strong>: <code>SUM</code> on <code>INT</code> columns can overflow for very large totals. Cast to <code>DECIMAL</code> or <code>BIGINT</code>:</p>

<pre><code>SELECT SUM(CAST(amount AS DECIMAL(20, 2))) FROM transactions;</code></pre>

<p><strong>Combine multiple aggregates</strong> &mdash; one query, many metrics:</p>

<pre><code>SELECT
  COUNT(*) AS order_count,
  SUM(total) AS revenue,
  AVG(total) AS avg_order_value,
  MAX(total) AS biggest_order
FROM orders
WHERE status = 'completed';</code></pre>
'''

ANSWERS[76] = r'''
<p>The <code>DISTINCT</code> keyword removes duplicate rows from the result set. Apply it directly after <code>SELECT</code>.</p>

<pre><code>-- Unique countries from users table
SELECT DISTINCT country FROM users;</code></pre>

<p><strong>DISTINCT applies to the whole row</strong> &mdash; the combination of all selected columns must be unique. So selecting two columns gives unique <em>pairs</em>:</p>

<pre><code>SELECT DISTINCT country, city FROM users;
-- ('US', 'NYC') and ('US', 'LA') are both kept; they&rsquo;re different pairs.</code></pre>

<p><strong>With aggregates</strong>:</p>

<pre><code>-- Number of unique countries
SELECT COUNT(DISTINCT country) FROM users;

-- Distinct emails per country
SELECT country, COUNT(DISTINCT email)
FROM users
GROUP BY country;</code></pre>

<p><strong>Common alternative: GROUP BY</strong> &mdash; in many cases <code>SELECT DISTINCT col FROM tbl</code> is equivalent to <code>SELECT col FROM tbl GROUP BY col</code>. Use <code>DISTINCT</code> for clarity when you don&rsquo;t need aggregates.</p>

<p><strong>NULL handling</strong>: <code>DISTINCT</code> treats all NULLs as a single value. If a column has 50 NULLs, you get one NULL row in the distinct result.</p>

<p><strong>Performance</strong>:</p>
<ul>
  <li><code>DISTINCT</code> usually requires a sort or temp-table operation. Indexes that match the distinct columns can let MySQL skip the sort.</li>
  <li>If you find yourself reaching for <code>DISTINCT</code> often, the schema may have unwanted duplication &mdash; check whether a join is producing extra rows that shouldn&rsquo;t exist.</li>
  <li><code>SELECT DISTINCT *</code> over a wide table can be expensive; prefer listing only the columns whose uniqueness you actually need.</li>
</ul>

<p><strong>Don&rsquo;t confuse with UNIQUE</strong>: <code>UNIQUE</code> is a <em>constraint</em> at the table-definition level (preventing duplicate inserts); <code>DISTINCT</code> is a <em>query operation</em> at read time.</p>
'''

ANSWERS[77] = r'''
<p>Use the <code>mysqldump</code> command-line tool. It generates a <code>.sql</code> file containing the SQL statements needed to recreate the database &mdash; tables, schema, and data.</p>

<pre><code># Single database
mysqldump -u root -p shop &gt; shop_backup.sql

# All databases on the server
mysqldump -u root -p --all-databases &gt; full_backup.sql

# Specific tables only
mysqldump -u root -p shop users orders &gt; partial.sql</code></pre>

<p>You&rsquo;ll be prompted for the password.</p>

<p><strong>Useful options</strong>:</p>

<pre><code>mysqldump -u root -p \
  --single-transaction \           # consistent snapshot without locking
  --routines \                     # include stored procedures + functions
  --triggers \                     # include triggers
  --events \                       # include scheduled events
  --hex-blob \                     # safer encoding for binary data
  shop &gt; shop_backup.sql</code></pre>

<ul>
  <li><code>--single-transaction</code> is essential for InnoDB to get a consistent backup without table locks.</li>
  <li><code>--routines --triggers --events</code> ensure stored programs are included &mdash; they&rsquo;re excluded by default.</li>
</ul>

<p><strong>Compress on the fly</strong>:</p>

<pre><code>mysqldump -u root -p shop | gzip &gt; shop_backup.sql.gz</code></pre>

<p><strong>For large databases</strong>, mysqldump can be slow to restore. Alternatives:</p>
<ul>
  <li><strong>mysqlpump</strong> (MySQL 5.7+) &mdash; multi-threaded; faster.</li>
  <li><strong>Percona XtraBackup</strong> &mdash; physical backup; near-instant restore; recommended for production.</li>
  <li><strong>Cloud snapshots</strong> &mdash; AWS RDS, Google Cloud SQL provide point-in-time restore via storage-level snapshots.</li>
</ul>

<p><strong>Always test your backups</strong>. A backup you&rsquo;ve never restored is not a backup. Schedule regular restore drills to a staging environment.</p>
'''

ANSWERS[78] = r'''
<p>Pipe the backup file into the <code>mysql</code> command-line client. The SQL statements in the dump recreate the schema and reload the data.</p>

<pre><code># Restore to existing database
mysql -u root -p shop &lt; shop_backup.sql

# Or create the database first if needed
mysql -u root -p -e "CREATE DATABASE shop"
mysql -u root -p shop &lt; shop_backup.sql

# Restore from compressed file
gunzip &lt; shop_backup.sql.gz | mysql -u root -p shop</code></pre>

<p><strong>For all-databases dumps</strong> &mdash; the dump file already contains <code>CREATE DATABASE</code> statements:</p>

<pre><code>mysql -u root -p &lt; full_backup.sql</code></pre>

<p>No database name argument needed.</p>

<p><strong>Verify after restoring</strong>:</p>

<pre><code>mysql -u root -p shop -e "SHOW TABLES; SELECT COUNT(*) FROM users;"</code></pre>

<p><strong>Speeding up large restores</strong>:</p>

<pre><code># Disable foreign key checks during import (re-enable after)
mysql -u root -p shop &lt; backup.sql --init-command="SET FOREIGN_KEY_CHECKS=0"

# Or wrap restore SQL with these settings
SET autocommit=0;
SET foreign_key_checks=0;
SET unique_checks=0;
-- ... import data ...
COMMIT;
SET foreign_key_checks=1;</code></pre>

<p>Reduces overhead because indexes and constraints aren&rsquo;t validated row by row.</p>

<p><strong>Restoring to a different database name</strong> &mdash; the dump file has the original name embedded, so either:</p>
<ul>
  <li>Edit the dump file&rsquo;s <code>CREATE DATABASE</code> / <code>USE</code> lines, or</li>
  <li>Create the new database, then specify it on the command line: <code>mysql -u root -p new_name &lt; old_dump.sql</code> (works if the dump uses <code>USE</code>).</li>
</ul>

<p><strong>Caution</strong>: restoring overwrites the target database. Take a fresh backup of whatever&rsquo;s currently there before restoring an older one.</p>
'''

ANSWERS[79] = r'''
<p>Two main approaches: SQL&rsquo;s built-in <code>LOAD DATA INFILE</code>, or external tools like <code>mysqlimport</code> or scripts.</p>

<p><strong>LOAD DATA INFILE</strong> &mdash; the fastest for bulk loading:</p>

<pre><code>LOAD DATA LOCAL INFILE '/path/to/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES                    -- skip header row
(name, email, age, country);     -- column mapping</code></pre>

<p><strong>Key parts</strong>:</p>
<ul>
  <li><code>LOCAL</code> reads from the client machine; without it, the file must be on the server.</li>
  <li><code>FIELDS TERMINATED BY ','</code> sets the delimiter &mdash; use <code>'\t'</code> for TSV.</li>
  <li><code>OPTIONALLY ENCLOSED BY '"'</code> handles quoted values containing commas.</li>
  <li><code>IGNORE 1 LINES</code> skips a header row.</li>
  <li>The column list maps CSV columns to table columns.</li>
</ul>

<p><strong>With transformations</strong>:</p>

<pre><code>LOAD DATA LOCAL INFILE 'users.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
IGNORE 1 LINES
(name, email, @raw_age, @raw_date)
SET age = NULLIF(@raw_age, ''),                          -- empty string → NULL
    created_at = STR_TO_DATE(@raw_date, '%Y-%m-%d');    -- parse date</code></pre>

<p>Variables prefixed with <code>@</code> capture raw values for processing in <code>SET</code>.</p>

<p><strong>Configuration prerequisites</strong>:</p>
<ul>
  <li>For <code>LOCAL</code> uploads, both client and server must enable <code>local_infile</code> &mdash; disabled by default in newer MySQL for security.</li>
  <li>Without <code>LOCAL</code>, the file must be in the server&rsquo;s <code>secure_file_priv</code> directory.</li>
</ul>

<p><strong>Alternative: mysqlimport</strong> command-line wrapper:</p>

<pre><code>mysqlimport -u root -p --local --fields-terminated-by=',' \
  --ignore-lines=1 shop /path/to/users.csv
-- Table name is taken from the file name (users.csv → users)</code></pre>

<p><strong>For complex transformations</strong>, write a short application script (Python with pandas, Node.js with csv-parse) that reads the CSV, validates rows, and inserts via prepared statements. Slower than LOAD DATA, but more flexible.</p>
'''

ANSWERS[80] = r'''
<p>Use <code>SELECT ... INTO OUTFILE</code> &mdash; the SQL counterpart of <code>LOAD DATA INFILE</code>.</p>

<pre><code>SELECT id, name, email, created_at
FROM users
INTO OUTFILE '/var/lib/mysql-files/users_export.csv'
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';</code></pre>

<p><strong>The output file must not already exist</strong> &mdash; MySQL refuses to overwrite. Delete or rename first.</p>

<p><strong>Header row</strong> &mdash; <code>INTO OUTFILE</code> doesn&rsquo;t emit a header by itself. Use <code>UNION</code>:</p>

<pre><code>(SELECT 'id', 'name', 'email', 'created_at')
UNION ALL
(SELECT id, name, email, created_at FROM users)
INTO OUTFILE '/var/lib/mysql-files/users.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';</code></pre>

<p><strong>Server-side restriction</strong>: the file is written on the MySQL server&rsquo;s filesystem, not the client&rsquo;s. The destination must be in <code>secure_file_priv</code> (configurable; <code>SHOW VARIABLES LIKE 'secure_file_priv'</code> reveals the allowed path). The MySQL user must have the <code>FILE</code> privilege.</p>

<p><strong>Client-side export with mysql command</strong> &mdash; works without server-side file privileges:</p>

<pre><code>mysql -u root -p -e "SELECT id, name, email FROM users" shop \
  --batch \
  --skip-column-names \
  | tr '\t' ',' &gt; users.csv</code></pre>

<p>Or with proper CSV quoting:</p>

<pre><code>mysql -u root -p -e "SELECT * FROM users" shop \
  --batch \
  --skip-column-names \
  | python3 -c "import csv, sys; w = csv.writer(sys.stdout); \
       [w.writerow(line.split('\\t')) for line in sys.stdin]" &gt; users.csv</code></pre>

<p><strong>For production / large exports</strong>, dedicated tools handle CSV quoting correctly:</p>
<ul>
  <li><strong>mysqldump</strong> with <code>--tab</code> writes tab-delimited files plus a schema file per table.</li>
  <li><strong>Application code</strong> (Node.js with <code>csv-stringify</code>, Python with <code>pandas.to_csv</code>) handles edge cases like embedded newlines and quotes properly.</li>
</ul>
'''

ANSWERS[81] = r'''
<p>The <strong>MySQL client</strong> is the command-line program that connects to a MySQL server, sends SQL, and displays results. It&rsquo;s installed alongside the server, but can also be installed standalone.</p>

<pre><code># Connect to local server
mysql -u root -p

# Connect to remote server
mysql -h db.example.com -u app_user -p shop

# Connect via socket (Linux/Mac)
mysql -u root -p -S /var/run/mysqld/mysqld.sock</code></pre>

<p>After connecting, you get an interactive prompt where you can run SQL statements terminated by <code>;</code> or <code>\G</code>:</p>

<pre><code>mysql&gt; SHOW DATABASES;
mysql&gt; USE shop;
mysql&gt; SELECT * FROM users LIMIT 5\G</code></pre>

<p><strong>Common command-line flags</strong>:</p>

<table>
  <tr><th>Flag</th><th>Meaning</th></tr>
  <tr><td><code>-u user</code></td><td>Username</td></tr>
  <tr><td><code>-p</code></td><td>Prompt for password</td></tr>
  <tr><td><code>-h host</code></td><td>Hostname (default: localhost)</td></tr>
  <tr><td><code>-P port</code></td><td>Port (default: 3306)</td></tr>
  <tr><td><code>-D db</code></td><td>Default database</td></tr>
  <tr><td><code>-e "SQL"</code></td><td>Execute SQL and exit</td></tr>
  <tr><td><code>--batch</code></td><td>Tab-separated output for piping</td></tr>
  <tr><td><code>--ssl-mode=REQUIRED</code></td><td>Require encrypted connection</td></tr>
</table>

<p><strong>Useful interactive commands</strong> (not SQL):</p>

<pre><code>\h        -- help
\s        -- server status, version, encoding
\q        -- quit
\u shop   -- USE shop
\.  file.sql  -- run SQL from file
clear     -- clear current input
edit      -- edit current input in $EDITOR</code></pre>

<p><strong>GUI alternatives</strong> if you prefer not to use the command line:</p>
<ul>
  <li><strong>MySQL Workbench</strong> &mdash; official, full-featured.</li>
  <li><strong>DBeaver</strong> &mdash; free, multi-database.</li>
  <li><strong>TablePlus</strong> &mdash; modern, paid (free tier limited).</li>
  <li><strong>phpMyAdmin</strong> &mdash; web-based, common with shared hosting.</li>
</ul>
'''

ANSWERS[82] = r'''
<p>Use the <code>GRANT</code> statement to give privileges and <code>REVOKE</code> to take them away. Privileges can be assigned at the global, database, table, or column level.</p>

<pre><code>-- Read-only access on one database
GRANT SELECT ON shop.* TO 'reporter'@'localhost';

-- Full read/write on the shop database
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'app_user'@'localhost';

-- Permissions on a specific table only
GRANT SELECT, INSERT ON shop.audit_log TO 'logger'@'localhost';

-- Apply changes immediately (usually automatic)
FLUSH PRIVILEGES;</code></pre>

<p><strong>Privilege scope syntax</strong>:</p>
<ul>
  <li><code>*.*</code> &mdash; all databases, all tables (server-wide).</li>
  <li><code>shop.*</code> &mdash; all tables in <code>shop</code>.</li>
  <li><code>shop.users</code> &mdash; just one table.</li>
  <li><code>shop.users (email, name)</code> &mdash; specific columns.</li>
</ul>

<p><strong>Common privileges</strong>:</p>

<table>
  <tr><th>Privilege</th><th>Allows</th></tr>
  <tr><td>SELECT</td><td>Reading data</td></tr>
  <tr><td>INSERT, UPDATE, DELETE</td><td>Modifying data</td></tr>
  <tr><td>CREATE, DROP, ALTER</td><td>Creating / dropping / changing tables</td></tr>
  <tr><td>INDEX</td><td>Creating / dropping indexes</td></tr>
  <tr><td>EXECUTE</td><td>Calling stored procedures</td></tr>
  <tr><td>GRANT OPTION</td><td>Granting these same privileges to others</td></tr>
  <tr><td>ALL PRIVILEGES</td><td>Everything except GRANT OPTION</td></tr>
</table>

<p><strong>Inspect what a user can do</strong>:</p>

<pre><code>SHOW GRANTS FOR 'app_user'@'localhost';</code></pre>

<p><strong>Principle of least privilege</strong>: application connections should use a user with only the minimum privileges they need. Never have your web app connect as <code>root</code>. Read-only reporting tools get <code>SELECT</code> only. Migration scripts may need <code>CREATE</code>/<code>ALTER</code> &mdash; but use a separate, more privileged user for those, distinct from the runtime app user.</p>
'''

ANSWERS[83] = r'''
<p>Use the <code>CREATE USER</code> statement. A MySQL user is identified by both <em>username</em> and <em>host</em> &mdash; the same name can have different permissions depending on where they connect from.</p>

<pre><code>-- Local connections only
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'a-strong-password';

-- Connections from any host
CREATE USER 'app_user'@'%' IDENTIFIED BY 'a-strong-password';

-- Connections from a specific subnet
CREATE USER 'app_user'@'10.0.1.%' IDENTIFIED BY 'a-strong-password';

-- Connections from a specific host
CREATE USER 'app_user'@'web1.internal' IDENTIFIED BY 'a-strong-password';</code></pre>

<p><strong>Then grant privileges</strong> &mdash; <code>CREATE USER</code> alone gives no permissions:</p>

<pre><code>GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;</code></pre>

<p><strong>Authentication options</strong> &mdash; specify the auth plugin:</p>

<pre><code>-- Modern default in MySQL 8 (sha2 auth)
CREATE USER 'app_user'@'localhost'
IDENTIFIED WITH caching_sha2_password BY 'password';

-- Legacy (less secure; avoid)
CREATE USER 'app_user'@'localhost'
IDENTIFIED WITH mysql_native_password BY 'password';</code></pre>

<p><strong>Password policies</strong>:</p>

<pre><code>-- Force password change on next login
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'temp-pass'
PASSWORD EXPIRE;

-- Set expiration interval
CREATE USER 'app_user'@'%' IDENTIFIED BY 'pass'
PASSWORD EXPIRE INTERVAL 90 DAY;

-- Account lock state
CREATE USER 'frozen'@'%' IDENTIFIED BY 'pass'
ACCOUNT LOCK;</code></pre>

<p><strong>Best practices</strong>:</p>
<ul>
  <li>Use a separate user per application or service &mdash; not <code>root</code>.</li>
  <li>Use a strong, unique password (16+ random characters; managed in a secret store).</li>
  <li>Restrict by host &mdash; use specific IPs/subnets, not <code>%</code>, when possible.</li>
  <li>Use SSL/TLS for non-localhost connections: <code>REQUIRE SSL</code>.</li>
  <li>Rotate passwords periodically.</li>
</ul>
'''

ANSWERS[84] = r'''
<p>Use the <code>DROP USER</code> statement. The user is removed from the system and can no longer connect.</p>

<pre><code>DROP USER 'app_user'@'localhost';</code></pre>

<p>Specify both username and host &mdash; <code>'app_user'@'localhost'</code> and <code>'app_user'@'%'</code> are different users. Drop them separately if both exist:</p>

<pre><code>DROP USER 'app_user'@'localhost', 'app_user'@'%';</code></pre>

<p><strong>If the user doesn&rsquo;t exist</strong>, MySQL throws an error. Add <code>IF EXISTS</code> for idempotent scripts:</p>

<pre><code>DROP USER IF EXISTS 'app_user'@'localhost';</code></pre>

<p><strong>What happens to objects the user owned</strong>:</p>
<ul>
  <li><strong>Tables, views, procedures</strong> created by the user remain &mdash; they&rsquo;re owned by the database, not the user. Other users with appropriate privileges can still use them.</li>
  <li><strong>Active connections</strong> from that user are not killed automatically. Active sessions continue until they close. Use <code>KILL connection-id</code> to terminate them.</li>
  <li><strong>Privilege grants</strong> are removed automatically &mdash; the entry vanishes from <code>mysql.user</code>.</li>
</ul>

<p><strong>Find existing connections to kill</strong>:</p>

<pre><code>SELECT id, user, host, db, command, time
FROM information_schema.processlist
WHERE user = 'app_user';

-- Then for each id:
KILL 12345;</code></pre>

<p><strong>Best practice</strong>: instead of dropping users you might want to bring back, lock the account first. This preserves the user record and grants for easy reactivation:</p>

<pre><code>ALTER USER 'app_user'@'%' ACCOUNT LOCK;
-- ... later, if needed:
ALTER USER 'app_user'@'%' ACCOUNT UNLOCK;</code></pre>

<p>Drop only when you&rsquo;re certain the user won&rsquo;t be needed again &mdash; for instance, after decommissioning a service.</p>
'''

ANSWERS[85] = r'''
<p>Use <code>ALTER USER</code> with the <code>IDENTIFIED BY</code> clause to set a new password.</p>

<pre><code>ALTER USER 'app_user'@'localhost'
IDENTIFIED BY 'new-strong-password';</code></pre>

<p><strong>Change your own password</strong>:</p>

<pre><code>ALTER USER USER() IDENTIFIED BY 'new-pass';
-- USER() returns the current logged-in user.</code></pre>

<p><strong>Force password change on next login</strong>:</p>

<pre><code>ALTER USER 'app_user'@'localhost'
IDENTIFIED BY 'temp-pass'
PASSWORD EXPIRE;</code></pre>

<p>The user must change it before issuing any other command.</p>

<p><strong>Older syntax</strong> (still works in MySQL 8 but the <code>SET PASSWORD</code> form is being phased out):</p>

<pre><code>SET PASSWORD FOR 'app_user'@'localhost' = 'new-pass';
-- Same effect as ALTER USER.</code></pre>

<p><strong>Random password generation</strong> &mdash; MySQL 8 can generate one for you:</p>

<pre><code>ALTER USER 'app_user'@'localhost' IDENTIFIED BY RANDOM PASSWORD;
-- Returns a generated password in the result set.</code></pre>

<p><strong>Apply changes</strong> &mdash; in modern MySQL, <code>FLUSH PRIVILEGES</code> isn&rsquo;t needed for <code>ALTER USER</code>; the change takes effect immediately for new connections. Existing connections are unaffected until they reconnect.</p>

<p><strong>Best practices</strong>:</p>
<ul>
  <li>Don&rsquo;t put passwords in shell history &mdash; on the command line, prompt with <code>-p</code> or use a config file with restricted permissions (<code>~/.my.cnf</code>, mode 600).</li>
  <li>Don&rsquo;t embed passwords in scripts &mdash; use a secret manager (AWS Secrets Manager, HashiCorp Vault, .env files outside source control).</li>
  <li>Rotate periodically &mdash; especially for users with broad privileges.</li>
  <li>Use a strong password generator (<code>openssl rand -base64 32</code>).</li>
</ul>
'''

ANSWERS[86] = r'''
<p>Use <code>GRANT ALL PRIVILEGES</code>. The scope (<code>*.*</code>, <code>db.*</code>, etc.) determines whether it&rsquo;s server-wide or limited.</p>

<pre><code>-- All privileges on a single database
GRANT ALL PRIVILEGES ON shop.* TO 'admin_user'@'localhost';

-- Server-wide super-user (use sparingly!)
GRANT ALL PRIVILEGES ON *.* TO 'root_admin'@'localhost' WITH GRANT OPTION;

-- Apply (often automatic, but explicit is safer)
FLUSH PRIVILEGES;</code></pre>

<p><strong>What "ALL" includes</strong> &mdash; every privilege except <code>GRANT OPTION</code> (the ability to grant privileges to others) and <code>PROXY</code>. To include grant ability:</p>

<pre><code>GRANT ALL PRIVILEGES ON shop.* TO 'admin_user'@'localhost'
WITH GRANT OPTION;</code></pre>

<p><strong>Verify</strong>:</p>

<pre><code>SHOW GRANTS FOR 'admin_user'@'localhost';

-- Output like:
-- GRANT ALL PRIVILEGES ON `shop`.* TO `admin_user`@`localhost`</code></pre>

<p><strong>Why this is risky</strong>:</p>
<ul>
  <li><code>ALL PRIVILEGES ON *.*</code> means the user can drop any database, modify any user, read any data &mdash; effectively root.</li>
  <li>Compromised credentials with this level of access mean total database compromise.</li>
  <li>Application bugs (SQL injection) become much more dangerous.</li>
</ul>

<p><strong>Better alternative for application users</strong>:</p>

<pre><code>-- Specific privileges only — principle of least privilege
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'app_user'@'%';

-- And maybe these for migrations (often a separate user):
GRANT CREATE, DROP, ALTER, INDEX, REFERENCES ON shop.* TO 'migrator'@'localhost';</code></pre>

<p><strong>When ALL PRIVILEGES is reasonable</strong>:</p>
<ul>
  <li>Local development databases.</li>
  <li>Test environments.</li>
  <li>Genuinely admin/DBA users (kept few in number, with strong auth and audit logging).</li>
</ul>

<p>For production application users, never grant <code>ALL PRIVILEGES</code> &mdash; list the specific operations the application actually performs.</p>
'''

ANSWERS[87] = r'''
<p>Use the <code>REVOKE</code> statement &mdash; it mirrors <code>GRANT</code> in syntax but removes privileges instead.</p>

<pre><code>-- Revoke a specific privilege
REVOKE INSERT ON shop.* FROM 'app_user'@'localhost';

-- Revoke multiple
REVOKE INSERT, UPDATE, DELETE ON shop.* FROM 'app_user'@'localhost';

-- Revoke ALL — leaves the user but with no privileges
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'app_user'@'localhost';

FLUSH PRIVILEGES;</code></pre>

<p><strong>Scope must match</strong> the original GRANT. If you granted <code>SELECT ON shop.*</code>, you must revoke <code>SELECT ON shop.*</code> &mdash; not <code>SELECT ON *.*</code> or <code>SELECT ON shop.users</code>.</p>

<p><strong>To check what privileges a user has before revoking</strong>:</p>

<pre><code>SHOW GRANTS FOR 'app_user'@'localhost';

-- GRANT SELECT, INSERT ON `shop`.* TO `app_user`@`localhost`
-- GRANT EXECUTE ON `shop`.`some_proc` TO `app_user`@`localhost`</code></pre>

<p>Each line is a separate grant scope &mdash; revoke each accordingly.</p>

<p><strong>Common patterns</strong>:</p>

<pre><code>-- Demote a user to read-only
REVOKE INSERT, UPDATE, DELETE, CREATE, DROP, ALTER ON shop.*
FROM 'old_admin'@'localhost';

-- Strip all privileges (but keep the user account)
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'app_user'@'localhost';</code></pre>

<p><strong>Audit privilege changes</strong>: if your environment has compliance requirements, log all GRANT/REVOKE statements. MySQL Enterprise Audit plugin or external tools (Percona Audit Plugin) can capture these.</p>

<p><strong>Active connections aren&rsquo;t cut off</strong> when you revoke privileges &mdash; existing sessions continue with their original permissions until they reconnect. To force immediate effect, kill the user&rsquo;s sessions:</p>

<pre><code>SELECT id FROM information_schema.processlist
WHERE user = 'app_user';

KILL 12345;
KILL 12346;
-- ... etc</code></pre>
'''

ANSWERS[88] = r'''
<p>Query the <code>mysql.user</code> system table directly. There&rsquo;s no <code>SHOW USERS</code> command in MySQL.</p>

<pre><code>SELECT user, host FROM mysql.user;

-- More detail:
SELECT user, host, account_locked, password_expired,
       password_last_changed, plugin
FROM mysql.user;</code></pre>

<p>Sample output:</p>

<pre><code>+------------------+-----------+-----------------+
| user             | host      | plugin          |
+------------------+-----------+-----------------+
| app_user         | localhost | caching_sha2... |
| app_user         | %         | caching_sha2... |
| mysql.infoschema | localhost | caching_sha2... |
| mysql.session    | localhost | caching_sha2... |
| mysql.sys        | localhost | caching_sha2... |
| reporter         | 10.0.1.%  | caching_sha2... |
| root             | localhost | caching_sha2... |
+------------------+-----------+-----------------+</code></pre>

<p><strong>System users</strong> like <code>mysql.session</code>, <code>mysql.sys</code>, and <code>mysql.infoschema</code> are created and used by MySQL itself &mdash; don&rsquo;t modify or remove them. Filter them out for clarity:</p>

<pre><code>SELECT user, host FROM mysql.user
WHERE user NOT LIKE 'mysql.%';</code></pre>

<p><strong>To see what each user is allowed to do</strong>, iterate the <code>SHOW GRANTS</code> command per user:</p>

<pre><code>-- Check one user
SHOW GRANTS FOR 'app_user'@'localhost';</code></pre>

<p><strong>Permission required</strong>: only users with privileges on the <code>mysql</code> system database can read <code>mysql.user</code>. Application users typically can&rsquo;t list other users; <code>root</code> or DBA-level users can.</p>

<p><strong>Currently-connected users</strong> (active sessions) &mdash; different question; use:</p>

<pre><code>SELECT id, user, host, db, command, time
FROM information_schema.processlist
ORDER BY time DESC;</code></pre>

<p>This shows ongoing connections, including idle ones, with elapsed time and the database they&rsquo;re using.</p>
'''

ANSWERS[89] = r'''
<p>Several ways depending on whether you have a connection or just shell access.</p>

<p><strong>From inside the MySQL client</strong>:</p>

<pre><code>SELECT VERSION();
-- '8.4.0'

-- More detail:
SHOW VARIABLES LIKE 'version%';
-- version, version_comment, version_compile_machine, version_compile_os

STATUS;
-- (in interactive mode) prints client + server version, encoding, uptime, threads, etc.</code></pre>

<p><strong>From shell without connecting</strong>:</p>

<pre><code># Server binary version
mysqld --version

# Client binary version
mysql --version</code></pre>

<p><strong>From the connection banner</strong> &mdash; when you start the mysql client, the server version is printed:</p>

<pre><code>$ mysql -u root -p
Welcome to the MySQL monitor.  Commands end with ; or \g.
Server version: 8.4.0 MySQL Community Server - GPL
...</code></pre>

<p><strong>Why version matters</strong>:</p>
<ul>
  <li><strong>Feature support</strong>: window functions (<code>OVER()</code>) require 8.0+; CTEs (<code>WITH</code>) require 8.0+; <code>JSON_TABLE</code> requires 8.0; many <code>ALGORITHM=INSTANT</code> features are 8.0+.</li>
  <li><strong>Default authentication plugin</strong> changed from <code>mysql_native_password</code> to <code>caching_sha2_password</code> in 8.0 &mdash; legacy clients may need configuration.</li>
  <li><strong>Security patches</strong>: known CVEs are fixed in point releases &mdash; staying current matters.</li>
  <li><strong>End-of-life dates</strong>: 5.7 reached end-of-life in October 2023. 8.0 is current LTS through 2026; 8.4 is the next LTS.</li>
</ul>

<p><strong>MySQL vs MariaDB</strong>: they share heritage but diverged. <code>SELECT VERSION()</code> on MariaDB returns something like <code>10.11.6-MariaDB</code>. Many SQL features are compatible, but admin commands and some behaviors differ &mdash; check the documentation that matches your installation.</p>
'''

ANSWERS[90] = r'''
<p>"Optimization" in MySQL covers several distinct concerns. Here are the practical levers, roughly in order of impact.</p>

<p><strong>1. Add the right indexes.</strong> The single biggest performance lever. Find slow queries and add indexes covering their <code>WHERE</code>, <code>JOIN</code>, and <code>ORDER BY</code> columns:</p>

<pre><code>CREATE INDEX idx_orders_user_created
ON orders(user_id, created_at);</code></pre>

<p>Use <code>EXPLAIN</code> to see whether your query uses an index or scans:</p>

<pre><code>EXPLAIN SELECT * FROM orders WHERE user_id = 5;</code></pre>

<p><strong>2. Run <code>OPTIMIZE TABLE</code></strong> &mdash; rebuilds the table and indexes, reclaiming space from deleted rows and defragmenting:</p>

<pre><code>OPTIMIZE TABLE orders;</code></pre>

<p>For InnoDB this effectively does <code>ALTER TABLE ... ENGINE=InnoDB</code>. Useful after large deletes/updates.</p>

<p><strong>3. Tune server config</strong> &mdash; key parameters in <code>my.cnf</code>:</p>

<pre><code>[mysqld]
innodb_buffer_pool_size = 16G   # cache; 50-70% of RAM on dedicated servers
innodb_log_file_size    = 1G    # write throughput
max_connections         = 500
query_cache_type        = 0     # disable query cache (removed in MySQL 8 anyway)</code></pre>

<p><strong>4. Update statistics</strong>:</p>

<pre><code>ANALYZE TABLE orders;</code></pre>

<p>Refreshes the optimizer&rsquo;s row-count and index-cardinality estimates. Run after large data changes.</p>

<p><strong>5. Profile actual workload</strong> &mdash; enable the slow query log and check what&rsquo;s running:</p>

<pre><code>SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.5;
-- Then check the configured slow query log file</code></pre>

<p><strong>6. Other levers</strong>:</p>
<ul>
  <li><strong>Schema design</strong>: appropriate types (don&rsquo;t use <code>VARCHAR(255)</code> for things that fit in 20 chars; don&rsquo;t store JSON when columns would do).</li>
  <li><strong>Application-side caching</strong> (Redis) for repeated identical queries.</li>
  <li><strong>Read replicas</strong> for offloading SELECT-heavy workloads.</li>
  <li><strong>Partitioning</strong> for very large tables (rare; complexity often outweighs benefit).</li>
  <li><strong>Connection pooling</strong> (PgBouncer-equivalent for MySQL: ProxySQL, MaxScale).</li>
</ul>

<p>Always <strong>measure</strong> before and after &mdash; don&rsquo;t tune blindly.</p>
'''

ANSWERS[91] = r'''
<p>Use the <code>REPAIR TABLE</code> command. It attempts to fix corruption in MyISAM, ARCHIVE, and CSV tables. <strong>InnoDB tables (the default in modern MySQL) cannot be repaired this way</strong> &mdash; InnoDB has its own crash recovery via the redo log.</p>

<pre><code>REPAIR TABLE users;</code></pre>

<p><strong>Options</strong>:</p>

<pre><code>REPAIR TABLE users QUICK;       -- fast: rebuild only index file
REPAIR TABLE users EXTENDED;    -- thorough: row by row
REPAIR TABLE users USE_FRM;     -- recreate index from .frm definition
                                -- (last resort if .myi is missing)</code></pre>

<p><strong>For InnoDB</strong> &mdash; if a table is corrupted (rare but possible after hardware failure), the recovery process is different:</p>

<ol>
  <li>Restart MySQL with <code>innodb_force_recovery</code> set in <code>my.cnf</code>:
<pre><code>[mysqld]
innodb_force_recovery = 1   # try 1, then 2, 3... up to 6</code></pre>
  </li>
  <li>Once the server starts in this read-only-ish mode, dump the affected tables:
<pre><code>mysqldump shop &gt; rescue.sql</code></pre>
  </li>
  <li>Drop and recreate the database from the dump.</li>
  <li>Remove the <code>innodb_force_recovery</code> setting and restart normally.</li>
</ol>

<p><strong>Higher numbers</strong> are more aggressive but increase data-loss risk &mdash; only escalate if the previous level fails to start the server. Don&rsquo;t leave the server running in recovery mode &mdash; writes are restricted.</p>

<p><strong>Check before repairing</strong>:</p>

<pre><code>CHECK TABLE users;            -- reports OK / corrupted</code></pre>

<p><strong>Modern reality</strong>: InnoDB corruption in MySQL 8 is very rare. Hardware failure, OS-level disk issues, or a botched filesystem operation are typical causes. <strong>Backups are your real protection</strong> &mdash; if a table is unrecoverable, restore from the most recent backup. Test backup restoration regularly.</p>

<p>For very old MyISAM tables, <code>myisamchk</code> (a separate tool that operates on <code>.myi</code> files directly while the server is stopped) is the most powerful repair option.</p>
'''

ANSWERS[92] = r'''
<p>Use <code>SHOW STATUS</code> for runtime statistics, <code>SHOW VARIABLES</code> for configuration, and <code>SHOW PROCESSLIST</code> for active connections.</p>

<pre><code>-- Runtime metrics: uptime, queries handled, threads, traffic, etc.
SHOW STATUS;
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Bytes%';
SHOW STATUS LIKE 'Innodb%';

-- Server configuration values
SHOW VARIABLES;
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- Active sessions
SHOW PROCESSLIST;
SHOW FULL PROCESSLIST;     -- shows full SQL statements (else truncated)</code></pre>

<p><strong>Useful single-line health checks</strong>:</p>

<pre><code>SELECT VERSION();                               -- server version
SHOW STATUS LIKE 'Uptime';                      -- seconds since start
SHOW STATUS LIKE 'Threads_connected';           -- current connections
SHOW STATUS LIKE 'Threads_running';             -- actively executing
SHOW STATUS LIKE 'Aborted_connects';            -- failed login attempts
SHOW STATUS LIKE 'Slow_queries';                -- slow query count</code></pre>

<p><strong>InnoDB-specific status</strong> &mdash; detailed report on the storage engine:</p>

<pre><code>SHOW ENGINE INNODB STATUS\G</code></pre>

<p>Output includes: pending I/O, transaction list, deadlocks, buffer pool stats, log info. Essential for debugging contention.</p>

<p><strong>Performance Schema</strong> &mdash; the modern, structured way to access metrics:</p>

<pre><code>-- Top 10 most-frequent statements
SELECT digest_text, count_star, sum_timer_wait/1e12 AS total_seconds
FROM performance_schema.events_statements_summary_by_digest
ORDER BY count_star DESC
LIMIT 10;

-- Current connections by user
SELECT user, COUNT(*) FROM information_schema.processlist GROUP BY user;</code></pre>

<p><strong>OS-level checks</strong> &mdash; the database&rsquo;s health depends on the host:</p>
<ul>
  <li><code>top</code> / <code>htop</code> &mdash; CPU and memory usage of <code>mysqld</code>.</li>
  <li><code>iostat</code> &mdash; disk I/O.</li>
  <li><code>netstat -tn | grep 3306</code> &mdash; TCP connections.</li>
  <li><code>journalctl -u mysql</code> &mdash; MySQL service logs.</li>
</ul>

<p>For continuous monitoring in production, use a metrics tool: Prometheus + mysqld_exporter, Datadog, New Relic, Percona Monitoring &amp; Management.</p>
'''

ANSWERS[93] = r'''
<p>The <strong>slow query log</strong> records queries that exceed a configurable execution-time threshold &mdash; essential for finding which queries to optimize.</p>

<p><strong>Enable at runtime</strong> (no restart needed):</p>

<pre><code>SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;                     -- seconds; 1.0 is typical
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- Optional: log queries that don&rsquo;t use indexes (very noisy)
SET GLOBAL log_queries_not_using_indexes = 'ON';</code></pre>

<p><strong>Persistent across restarts</strong> &mdash; add to <code>my.cnf</code>:</p>

<pre><code>[mysqld]
slow_query_log              = 1
slow_query_log_file         = /var/log/mysql/slow.log
long_query_time             = 1
log_queries_not_using_indexes = 1
log_slow_admin_statements   = 1
log_slow_replica_statements = 1
min_examined_row_limit      = 1000   # only log if &gt;1000 rows scanned</code></pre>

<p><strong>Log format</strong>:</p>

<pre><code># Time: 2026-04-27T10:32:14.123456Z
# User@Host: app_user[app_user] @ web1.internal []  Id: 12345
# Query_time: 2.456789  Lock_time: 0.000123  Rows_sent: 100  Rows_examined: 500000
SET timestamp=1745749934;
SELECT * FROM orders WHERE total &gt; 100;</code></pre>

<p>Each entry shows execution time, lock wait, rows returned vs examined, and the SQL.</p>

<p><strong>Analyze with <code>mysqldumpslow</code></strong> &mdash; bundled tool that aggregates the log:</p>

<pre><code># Top 10 slowest queries by total time
mysqldumpslow -t 10 -s t /var/log/mysql/slow.log

# Top 10 by count
mysqldumpslow -t 10 -s c /var/log/mysql/slow.log</code></pre>

<p>Replaces literal values with placeholders so similar queries group together.</p>

<p><strong>Better tools</strong>:</p>
<ul>
  <li><strong>pt-query-digest</strong> (Percona Toolkit) &mdash; far richer slow-log analysis.</li>
  <li><strong>Performance Schema</strong> &mdash; live, structured slow-query data without log files.</li>
</ul>

<p><strong>Don&rsquo;t leave at <code>long_query_time = 0</code> in production</strong> &mdash; it logs every query, can fill disk fast, and adds I/O overhead. Start at 1-2 seconds in production; tune lower in staging when hunting specific issues.</p>
'''

ANSWERS[94] = r'''
<p>A <strong>storage engine</strong> is the underlying component that handles how data is stored, read, written, and indexed. MySQL is unusual in supporting multiple engines &mdash; you can pick a different engine per table, though most modern apps stick with one (InnoDB).</p>

<p><strong>Common engines</strong>:</p>

<table>
  <tr><th>Engine</th><th>Purpose</th><th>Transactional?</th></tr>
  <tr><td><strong>InnoDB</strong></td><td>Default since MySQL 5.5; ACID-compliant; row-level locking; foreign keys; crash recovery</td><td>Yes</td></tr>
  <tr><td><strong>MyISAM</strong></td><td>Older; faster reads on simple workloads; full-text indexing (legacy); table-level locking</td><td>No</td></tr>
  <tr><td><strong>MEMORY</strong></td><td>Tables stored entirely in RAM; data lost on server restart</td><td>No</td></tr>
  <tr><td><strong>ARCHIVE</strong></td><td>Compressed; insert-only; ideal for log/audit data</td><td>No</td></tr>
  <tr><td><strong>CSV</strong></td><td>Stores data in plain CSV files; useful for data interchange</td><td>No</td></tr>
  <tr><td><strong>BLACKHOLE</strong></td><td>Discards everything written; used for replication relays</td><td>No</td></tr>
  <tr><td><strong>NDB</strong></td><td>MySQL Cluster; distributed in-memory; high availability</td><td>Yes</td></tr>
</table>

<p><strong>Why InnoDB is the universal choice</strong>:</p>
<ul>
  <li>Full ACID transactions (commit, rollback, crash recovery via redo log).</li>
  <li>Row-level locking &mdash; multiple writers don&rsquo;t block each other.</li>
  <li>Foreign key support and enforcement.</li>
  <li>Clustered indexes &mdash; primary key data is the row, faster lookups.</li>
  <li>Online DDL for many operations.</li>
  <li>Buffer pool caching &mdash; hot data stays in memory.</li>
</ul>

<p><strong>See available engines and the default</strong>:</p>

<pre><code>SHOW ENGINES;

+--------+---------+-------------------------+--------------+------+------------+
| Engine | Support | Comment                 | Transactions | XA   | Savepoints |
+--------+---------+-------------------------+--------------+------+------------+
| InnoDB | DEFAULT | Supports transactions...| YES          | YES  | YES        |
| MyISAM | YES     | MyISAM storage engine   | NO           | NO   | NO         |
| ...                                                                          |
+--------+---------+-------------------------+--------------+------+------------+</code></pre>

<p><strong>See engine per table</strong>:</p>

<pre><code>SELECT TABLE_NAME, ENGINE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop';</code></pre>

<p>For new applications: use <strong>InnoDB everywhere</strong>. The other engines have niche uses but are not appropriate for general-purpose application data.</p>
'''

ANSWERS[95] = r'''
<p>Use <code>ALTER TABLE ... ENGINE = ...</code>. MySQL rebuilds the table using the new engine.</p>

<pre><code>-- Convert MyISAM to InnoDB (most common direction in legacy upgrades)
ALTER TABLE old_table ENGINE = InnoDB;

-- Convert to memory engine
ALTER TABLE temp_lookups ENGINE = MEMORY;</code></pre>

<p>Specify the new engine when creating a table:</p>

<pre><code>CREATE TABLE archived_logs (
  id BIGINT,
  msg TEXT,
  created_at DATETIME
) ENGINE = ARCHIVE;</code></pre>

<p><strong>Check current engine</strong>:</p>

<pre><code>SHOW CREATE TABLE old_table\G

CREATE TABLE `old_table` (
  `id` int NOT NULL,
  ...
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;</code></pre>

<p>Or via <code>information_schema</code>:</p>

<pre><code>SELECT TABLE_NAME, ENGINE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop' AND ENGINE != 'InnoDB';</code></pre>

<p><strong>Caveats when changing engine</strong>:</p>
<ul>
  <li><strong>Locking</strong>: <code>ALTER TABLE ENGINE</code> rewrites every row. On large tables this can take hours and may lock the table for writes. Use <code>pt-online-schema-change</code> or <code>gh-ost</code> for production.</li>
  <li><strong>Feature loss</strong>: converting from InnoDB to MyISAM loses transactional support and foreign key constraints. The constraints are silently dropped.</li>
  <li><strong>Storage size</strong>: InnoDB tables are typically larger than MyISAM (clustered index, undo log, etc.). Make sure you have disk space.</li>
  <li><strong>Indexes are rebuilt</strong> &mdash; if statistics matter for the optimizer, follow up with <code>ANALYZE TABLE</code>.</li>
  <li><strong>Foreign keys</strong>: only InnoDB supports them. If a table has FKs in or out, all related tables should be InnoDB.</li>
</ul>

<p><strong>Convert all MyISAM tables in a database</strong> with a generated script:</p>

<pre><code>SELECT CONCAT('ALTER TABLE ', TABLE_NAME, ' ENGINE = InnoDB;')
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'shop' AND ENGINE = 'MyISAM';
-- Run output as SQL.</code></pre>

<p>The default engine for new tables is set by <code>default_storage_engine</code> in <code>my.cnf</code> (InnoDB by default in modern MySQL).</p>
'''

ANSWERS[96] = r'''
<p><strong>Replication</strong> copies data from one MySQL server (the <strong>source</strong>, traditionally called <em>master</em>) to one or more other servers (<strong>replicas</strong>, traditionally <em>slaves</em>). Replicas continuously apply the same writes the source did, kept in sync via a stream of changes.</p>

<p><strong>Why use it</strong>:</p>
<ul>
  <li><strong>Read scaling</strong> &mdash; offload SELECT queries to replicas. The source handles writes; replicas handle reads.</li>
  <li><strong>High availability</strong> &mdash; if the source fails, promote a replica to take over.</li>
  <li><strong>Backups</strong> &mdash; run heavy backup operations on a replica without impacting production.</li>
  <li><strong>Geographic distribution</strong> &mdash; replicas in different regions reduce read latency.</li>
  <li><strong>Reporting / analytics</strong> &mdash; long analytical queries don&rsquo;t affect the source.</li>
</ul>

<p><strong>How it works</strong> &mdash; the source records every change in its <em>binary log</em> (binlog). Replicas read this stream and apply changes:</p>

<pre><code>┌──────────┐  binary log   ┌──────────┐
│  source  │ ────────────&gt; │ replica  │
│ (writes) │  (replication │ (reads)  │
└──────────┘   stream)     └──────────┘</code></pre>

<p><strong>Replication formats</strong>:</p>

<table>
  <tr><th>Format</th><th>What&rsquo;s logged</th></tr>
  <tr><td>STATEMENT</td><td>The original SQL statements (smaller, but non-deterministic queries can drift)</td></tr>
  <tr><td>ROW (default)</td><td>The actual row changes (larger but deterministic; safer)</td></tr>
  <tr><td>MIXED</td><td>Statement by default, switching to ROW when needed</td></tr>
</table>

<p><strong>Topologies</strong>:</p>

<ul>
  <li><strong>Source &rarr; replica</strong> (single replica) &mdash; the simplest setup.</li>
  <li><strong>Source &rarr; multiple replicas</strong> &mdash; common pattern for read scaling.</li>
  <li><strong>Source &rarr; replica &rarr; replica</strong> (chained) &mdash; a replica can itself be a source for downstream replicas.</li>
  <li><strong>Multi-source replication</strong> &mdash; one replica pulls from multiple sources.</li>
  <li><strong>Group Replication</strong> (MySQL 8) &mdash; multi-primary cluster with automatic failover; foundation of <strong>InnoDB Cluster</strong>.</li>
</ul>

<p><strong>Important caveat</strong>: replicas are <em>eventually consistent</em>. There&rsquo;s typically a small lag (milliseconds to seconds) between the source and replicas. Reading from a replica immediately after a write may return stale data.</p>

<p>Modern managed databases (AWS RDS, Google Cloud SQL, PlanetScale) handle replication setup and failover automatically &mdash; you typically don&rsquo;t configure binlog details manually.</p>
'''

ANSWERS[97] = r'''
<p>Setting up classic source-replica replication involves: configuring both servers, establishing a replication user, snapshotting the source, and starting the replica.</p>

<p><strong>1. Configure the source</strong> &mdash; in <code>my.cnf</code>:</p>

<pre><code>[mysqld]
server-id        = 1
log_bin          = mysql-bin
binlog_format    = ROW
gtid_mode        = ON
enforce_gtid_consistency = ON</code></pre>

<p>Restart MySQL.</p>

<p><strong>2. Configure the replica</strong> &mdash; in <code>my.cnf</code>:</p>

<pre><code>[mysqld]
server-id        = 2     # must differ from source
relay_log        = mysql-relay-bin
read_only        = ON
gtid_mode        = ON
enforce_gtid_consistency = ON</code></pre>

<p>Restart MySQL.</p>

<p><strong>3. Create a replication user on the source</strong>:</p>

<pre><code>CREATE USER 'replicator'@'%' IDENTIFIED BY 'strong-pass';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;</code></pre>

<p><strong>4. Snapshot the source</strong> &mdash; with GTID-based replication this is straightforward:</p>

<pre><code>mysqldump -u root -p \
  --all-databases \
  --single-transaction \
  --triggers --routines --events \
  --master-data=2 \
  --set-gtid-purged=ON \
  &gt; source_dump.sql</code></pre>

<p><strong>5. Restore the dump on the replica</strong>:</p>

<pre><code>mysql -u root -p &lt; source_dump.sql</code></pre>

<p><strong>6. Configure the replica to follow the source</strong>:</p>

<pre><code>CHANGE REPLICATION SOURCE TO
  SOURCE_HOST     = 'source.internal',
  SOURCE_USER     = 'replicator',
  SOURCE_PASSWORD = 'strong-pass',
  SOURCE_AUTO_POSITION = 1;       -- uses GTIDs

START REPLICA;</code></pre>

<p>(In MySQL 8.0.22+, <code>CHANGE REPLICATION SOURCE</code> replaces the old <code>CHANGE MASTER</code>; <code>START REPLICA</code> replaces <code>START SLAVE</code>.)</p>

<p><strong>7. Verify</strong>:</p>

<pre><code>SHOW REPLICA STATUS\G

-- Look for these:
-- Replica_IO_Running:  Yes
-- Replica_SQL_Running: Yes
-- Seconds_Behind_Source: 0</code></pre>

<p>If both are <code>Yes</code> and lag is small, replication is working.</p>

<p><strong>Modern alternatives</strong>: managed services (AWS RDS, GCP Cloud SQL, Azure Database for MySQL, PlanetScale) configure replication automatically. <strong>InnoDB Cluster</strong> using Group Replication provides multi-primary HA without manual replica setup. For new deployments, prefer these over hand-configured source-replica.</p>
'''

ANSWERS[98] = r'''
<p>Several layers, from quick interactive checks to full production observability.</p>

<p><strong>1. Quick interactive checks</strong>:</p>

<pre><code>SHOW PROCESSLIST;                          -- active sessions, current queries
SHOW STATUS LIKE 'Threads_%';              -- connection counts
SHOW STATUS LIKE 'Innodb_row_lock%';       -- lock contention
SHOW ENGINE INNODB STATUS\G                -- detailed InnoDB diagnostic dump</code></pre>

<p><strong>2. Performance Schema</strong> &mdash; structured data about everything the server does:</p>

<pre><code>-- Slowest statements globally
SELECT digest_text,
       count_star,
       avg_timer_wait/1e9 AS avg_ms,
       sum_timer_wait/1e12 AS total_seconds
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC
LIMIT 10;

-- Tables with the most reads
SELECT object_schema, object_name, count_read, sum_timer_read/1e12 AS read_seconds
FROM performance_schema.table_io_waits_summary_by_table
ORDER BY count_read DESC LIMIT 10;</code></pre>

<p><strong>3. Slow query log</strong> &mdash; queries exceeding a threshold (covered in slow log answer). Analyze with <code>pt-query-digest</code>.</p>

<p><strong>4. EXPLAIN for individual queries</strong>:</p>

<pre><code>EXPLAIN SELECT * FROM orders WHERE customer_id = 5;</code></pre>

<p>Shows the access method (index or scan), estimated rows, join order. <code>EXPLAIN ANALYZE</code> (8.0+) actually runs the query and reports real timings.</p>

<p><strong>5. Continuous monitoring tools</strong> &mdash; what production setups use:</p>

<table>
  <tr><th>Tool</th><th>Notes</th></tr>
  <tr><td>Prometheus + mysqld_exporter</td><td>Open-source; metrics + Grafana dashboards</td></tr>
  <tr><td>Percona Monitoring &amp; Management (PMM)</td><td>Open-source; rich MySQL-specific views</td></tr>
  <tr><td>Datadog / New Relic</td><td>SaaS; one-line agent install</td></tr>
  <tr><td>AWS RDS Performance Insights</td><td>Built-in for RDS instances</td></tr>
  <tr><td>VividCortex / SolarWinds DPA</td><td>Commercial query-level analyzers</td></tr>
</table>

<p><strong>Key metrics to watch</strong>:</p>
<ul>
  <li><strong>Queries per second</strong> (Com_select, Com_insert, ...).</li>
  <li><strong>Threads_connected</strong> &mdash; connection count vs <code>max_connections</code>.</li>
  <li><strong>Threads_running</strong> &mdash; concurrent active queries; high values mean contention.</li>
  <li><strong>Slow_queries</strong> &mdash; rate of queries exceeding the slow log threshold.</li>
  <li><strong>InnoDB buffer pool hit rate</strong> &mdash; cache effectiveness.</li>
  <li><strong>Replication lag</strong> &mdash; <code>Seconds_Behind_Source</code> on replicas.</li>
  <li><strong>Disk I/O</strong> at the OS level &mdash; the underlying constraint for any DB.</li>
</ul>

<p>Set alerts on these so you find out before users do.</p>
'''

ANSWERS[99] = r'''
<p><strong>NULL</strong> in SQL means "unknown" or "no value" &mdash; not zero, not empty string, not false. Special rules apply because comparisons with unknowns can&rsquo;t be true or false.</p>

<p><strong>Key rule: NULL is not equal to anything &mdash; even itself</strong>:</p>

<pre><code>SELECT NULL = NULL;     -- NULL (not TRUE!)
SELECT NULL &lt;&gt; 5;       -- NULL
SELECT NULL + 1;        -- NULL</code></pre>

<p>Use <code>IS NULL</code> and <code>IS NOT NULL</code> for null tests:</p>

<pre><code>SELECT * FROM users WHERE phone IS NULL;
SELECT * FROM users WHERE phone IS NOT NULL;</code></pre>

<p><strong>Aggregate functions ignore NULLs</strong>:</p>

<pre><code>-- AVG ignores NULLs in both numerator and denominator
SELECT AVG(score) FROM tests;
-- 5 rows, 2 NULL → averages over the 3 non-NULLs

-- COUNT(col) skips NULLs; COUNT(*) counts every row
SELECT COUNT(email), COUNT(*) FROM users;</code></pre>

<p><strong>NULLs in WHERE</strong> &mdash; rows with NULL in the filtered column don&rsquo;t match either equality or inequality:</p>

<pre><code>-- This DOES NOT match users with NULL country
SELECT * FROM users WHERE country &lt;&gt; 'US';

-- To include them:
SELECT * FROM users WHERE country &lt;&gt; 'US' OR country IS NULL;</code></pre>

<p><strong>NULLs in JOINs</strong> &mdash; <code>ON a.id = b.user_id</code> doesn&rsquo;t match if either is NULL. Use <code>LEFT JOIN</code> with <code>IS NULL</code> on the right side to find missing relationships.</p>

<p><strong>Convert NULL to a default value</strong> with <code>COALESCE</code> or <code>IFNULL</code>:</p>

<pre><code>SELECT COALESCE(phone, 'no phone') FROM users;
SELECT IFNULL(name, 'Anonymous') FROM users;</code></pre>

<p><code>COALESCE</code> takes any number of arguments and returns the first non-NULL:</p>

<pre><code>SELECT COALESCE(mobile, home, work, 'no contact') AS phone FROM users;</code></pre>

<p><strong>NULL-safe equality</strong>: the <code>&lt;=&gt;</code> operator treats two NULLs as equal:</p>

<pre><code>SELECT NULL &lt;=&gt; NULL;   -- 1 (TRUE)
SELECT NULL &lt;=&gt; 5;      -- 0 (FALSE)</code></pre>

<p><strong>Schema design</strong>: prefer <code>NOT NULL</code> with sensible defaults whenever possible. Nullable columns force every query to think about three-valued logic. Make NULL meaningful only when "unknown" or "not applicable" is genuinely a distinct state from any value.</p>
'''

ANSWERS[100] = r'''
<p><code>IFNULL(expr1, expr2)</code> returns <code>expr1</code> if it is not NULL; otherwise it returns <code>expr2</code>. Useful for substituting a sensible default when data may be missing.</p>

<pre><code>SELECT IFNULL(name, 'Anonymous') AS display_name FROM users;
-- 'Alice' for users with names; 'Anonymous' for those without

SELECT IFNULL(phone, 'No phone on file') FROM users;</code></pre>

<p><strong>In computations</strong>:</p>

<pre><code>-- Without IFNULL, NULL contaminates the math
SELECT price + IFNULL(tax, 0) AS total FROM items;

-- Avoid divide-by-NULL:
SELECT IFNULL(SUM(views), 0) AS total_views FROM posts WHERE id = 999;</code></pre>

<p><strong>IFNULL vs COALESCE</strong>:</p>

<table>
  <tr><th>Function</th><th>Args</th><th>Standard SQL?</th></tr>
  <tr><td><code>IFNULL(a, b)</code></td><td>Exactly 2</td><td>MySQL extension</td></tr>
  <tr><td><code>COALESCE(a, b, c, ...)</code></td><td>2 or more</td><td>SQL standard</td></tr>
</table>

<pre><code>-- IFNULL — only 2 args
IFNULL(mobile, 'unknown')

-- COALESCE — fall through several alternatives
COALESCE(mobile, home_phone, work_phone, 'no contact')</code></pre>

<p>For portability across databases, prefer <code>COALESCE</code>. For pure MySQL code, <code>IFNULL</code> is fine and slightly more concise for the two-argument case.</p>

<p><strong>Related NULL-handling functions</strong>:</p>

<table>
  <tr><th>Function</th><th>Returns</th></tr>
  <tr><td><code>IFNULL(a, b)</code></td><td><code>a</code> if not NULL, else <code>b</code></td></tr>
  <tr><td><code>COALESCE(a, b, ...)</code></td><td>First non-NULL argument</td></tr>
  <tr><td><code>NULLIF(a, b)</code></td><td>NULL if <code>a = b</code>; else <code>a</code></td></tr>
  <tr><td><code>ISNULL(a)</code></td><td>1 if <code>a</code> is NULL; 0 otherwise</td></tr>
  <tr><td><code>IS NULL</code> / <code>IS NOT NULL</code></td><td>Boolean test (used in WHERE)</td></tr>
</table>

<p><strong>Practical patterns</strong>:</p>

<pre><code>-- Treat empty string as NULL
SELECT NULLIF(TRIM(input), '') AS clean_input;

-- Default for nullable display
SELECT name, IFNULL(profile_pic, '/img/default-avatar.png') AS avatar FROM users;

-- Avoid NULL in concatenation
SELECT CONCAT(first_name, ' ', IFNULL(middle_name, ''), ' ', last_name) FROM users;
-- Or simpler with CONCAT_WS, which skips NULLs natively:
SELECT CONCAT_WS(' ', first_name, middle_name, last_name) FROM users;</code></pre>
'''
