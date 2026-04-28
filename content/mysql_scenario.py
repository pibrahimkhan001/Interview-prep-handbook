"""
MySQL Scenario Based answers (Q1-Q100).

Style:
- Situation -> Approach (with production-grade SQL/code) -> Trade-offs (table) -> Production polish
- Modern (2026) MySQL ecosystem references throughout
- HTML uses <p>, <table>, <pre><code>, &lt; &gt; &amp; escapes, smart quotes
"""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''
<p><strong>Situation:</strong> an e-commerce platform needs to model products with categories, customers placing orders containing line items, payment state, and inventory &mdash; all while staying performant as catalog and order volume grow.</p>

<p><strong>Approach:</strong> normalize the core entities, denormalize a few hot paths (order line snapshots), use a hierarchical category model, and keep money in <code>DECIMAL</code>.</p>

<pre><code>-- Categories (adjacency list; CTE for tree queries)
CREATE TABLE categories (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  parent_id INT NULL,
  name      VARCHAR(100) NOT NULL,
  slug      VARCHAR(120) NOT NULL UNIQUE,
  FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- Products
CREATE TABLE products (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  sku           VARCHAR(64) NOT NULL UNIQUE,
  name          VARCHAR(255) NOT NULL,
  description   TEXT,
  price_cents   INT UNSIGNED NOT NULL,           -- store in smallest unit
  currency      CHAR(3) NOT NULL DEFAULT 'USD',
  category_id   INT NOT NULL,
  status        ENUM('draft','active','archived') NOT NULL DEFAULT 'draft',
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id),
  INDEX idx_products_category_status (category_id, status),
  FULLTEXT KEY ft_products_name_desc (name, description)
);

-- Inventory split out -- writes are hotter than reads of products
CREATE TABLE inventory (
  product_id  BIGINT PRIMARY KEY,
  on_hand     INT NOT NULL DEFAULT 0,
  reserved    INT NOT NULL DEFAULT 0,         -- in-cart, awaiting payment
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Customers
CREATE TABLE customers (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Orders + items (snapshot pricing -- prices change, history must not)
CREATE TABLE orders (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id   BIGINT NOT NULL,
  status        ENUM('pending','paid','shipped','delivered','cancelled','refunded')
                  NOT NULL DEFAULT 'pending',
  subtotal_cents INT UNSIGNED NOT NULL,
  tax_cents     INT UNSIGNED NOT NULL,
  total_cents   INT UNSIGNED NOT NULL,
  placed_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  INDEX idx_orders_customer_placed (customer_id, placed_at DESC),
  INDEX idx_orders_status_placed   (status, placed_at)
);

CREATE TABLE order_items (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id        BIGINT NOT NULL,
  product_id      BIGINT NOT NULL,
  product_name    VARCHAR(255) NOT NULL,        -- snapshot
  unit_price_cents INT UNSIGNED NOT NULL,        -- snapshot
  quantity        INT UNSIGNED NOT NULL,
  FOREIGN KEY (order_id)   REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id),
  INDEX idx_oi_order   (order_id),
  INDEX idx_oi_product (product_id)
);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Alternative</th></tr>
  <tr><td><code>price_cents INT</code></td><td>No floating-point errors; sortable; integer math</td><td><code>DECIMAL(10,2)</code> is also fine; never <code>FLOAT</code></td></tr>
  <tr><td>Snapshot price &amp; name on order_items</td><td>Customer must see what they paid even after price/name changes</td><td>JOIN to products &mdash; breaks when products are archived</td></tr>
  <tr><td>Adjacency-list categories</td><td>Simple; recursive CTE handles tree queries</td><td>Closure table for very read-heavy hierarchies</td></tr>
  <tr><td>Inventory in separate table</td><td>Stock changes constantly; products rarely &mdash; different write profiles</td><td>One row, one lock contention point</td></tr>
  <tr><td>Reserved + on_hand columns</td><td>Cart hold without committing the sale</td><td>Single quantity &mdash; oversells under concurrency</td></tr>
</table>

<p><strong>Production polish:</strong> use <code>SELECT ... FOR UPDATE</code> when reserving inventory inside a transaction; index hot reporting columns (<code>placed_at</code>, <code>status</code>); partition <code>orders</code> by month once you cross ~50M rows; push search to <strong>Meilisearch</strong> or <strong>Elasticsearch</strong> for fuzzy matching, faceted filters, and multilingual stemming; run analytics off a read replica or stream to <strong>ClickHouse</strong> via <strong>Debezium</strong> &mdash; reporting on the OLTP database is the #1 cause of e-commerce database fires.</p>
'''

ANSWERS[2] = r'''
<p><strong>Situation:</strong> a web app needs login with email + password, password reset, "remember me," optional MFA, and protection against brute force. The schema must store credentials safely and support session or token-based auth.</p>

<p><strong>Approach:</strong> separate <code>users</code>, <code>credentials</code>, <code>sessions</code>, and <code>auth_attempts</code> tables. Hash passwords with bcrypt or argon2id; store the algorithm + cost so you can rotate.</p>

<pre><code>CREATE TABLE users (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  email           VARCHAR(255) NOT NULL UNIQUE,
  email_verified  BOOLEAN NOT NULL DEFAULT FALSE,
  display_name    VARCHAR(100),
  status          ENUM('active','locked','disabled') NOT NULL DEFAULT 'active',
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login_at   DATETIME NULL
);

-- Credentials separate so you can rotate algorithms / add passkeys later
CREATE TABLE user_passwords (
  user_id      BIGINT PRIMARY KEY,
  password_hash VARCHAR(255) NOT NULL,            -- "$argon2id$v=19$m=65536,t=3,p=4$..."
  must_change  BOOLEAN NOT NULL DEFAULT FALSE,
  changed_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- MFA secrets (TOTP)
CREATE TABLE user_mfa (
  user_id     BIGINT PRIMARY KEY,
  totp_secret VARBINARY(64) NOT NULL,             -- encrypted at rest
  enabled     BOOLEAN NOT NULL DEFAULT FALSE,
  recovery_codes JSON,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sessions (server-side; supports revocation)
CREATE TABLE sessions (
  id           CHAR(43) PRIMARY KEY,             -- 256-bit random, base64url
  user_id      BIGINT NOT NULL,
  ip_address   VARBINARY(16),
  user_agent   VARCHAR(255),
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at   DATETIME NOT NULL,
  revoked_at   DATETIME NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_sessions_user (user_id, expires_at),
  INDEX idx_sessions_expires (expires_at)         -- for cleanup job
);

-- Brute-force tracking
CREATE TABLE auth_attempts (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  email        VARCHAR(255) NOT NULL,
  ip_address   VARBINARY(16) NOT NULL,
  succeeded    BOOLEAN NOT NULL,
  attempted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_attempts_email_time (email, attempted_at),
  INDEX idx_attempts_ip_time    (ip_address, attempted_at)
);</code></pre>

<p><strong>Login flow (Node + mysql2):</strong></p>

<pre><code>import bcrypt from 'bcrypt';
import crypto from 'crypto';

async function login(email, password, ip, userAgent) {
  // 1. Rate-limit by email + IP
  const [[{ recent_failures }]] = await db.query(
    `SELECT COUNT(*) AS recent_failures FROM auth_attempts
     WHERE email = ? AND succeeded = 0
       AND attempted_at &gt; NOW() - INTERVAL 15 MINUTE`, [email]);
  if (recent_failures &gt;= 5) throw new Error('Too many failures, try later');

  // 2. Verify
  const [[user]] = await db.query(
    `SELECT u.id, u.status, p.password_hash
       FROM users u JOIN user_passwords p ON p.user_id = u.id
      WHERE u.email = ?`, [email]);
  const ok = user &amp;&amp; user.status === 'active'
            &amp;&amp; await bcrypt.compare(password, user.password_hash);

  await db.query(
    `INSERT INTO auth_attempts (email, ip_address, succeeded) VALUES (?, ?, ?)`,
    [email, ip, ok ? 1 : 0]);

  if (!ok) throw new Error('Invalid credentials');

  // 3. Issue session
  const sid = crypto.randomBytes(32).toString('base64url');
  await db.query(
    `INSERT INTO sessions (id, user_id, ip_address, user_agent, expires_at)
     VALUES (?, ?, ?, ?, NOW() + INTERVAL 30 DAY)`,
    [sid, user.id, ip, userAgent]);

  return sid;     // set as HttpOnly Secure SameSite=Lax cookie
}</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Choice</th><th>Why</th><th>When not</th></tr>
  <tr><td>argon2id (or bcrypt cost ≥ 12)</td><td>Memory-hard; resistant to GPU cracking</td><td>Embedded systems with no memory</td></tr>
  <tr><td>Server-side sessions in MySQL</td><td>Revocable; supports "log out everywhere"</td><td>Use Redis if QPS &gt; 10k &mdash; MySQL becomes the bottleneck</td></tr>
  <tr><td>Random opaque session IDs</td><td>No info leakage; trivial to revoke</td><td>JWT for stateless multi-service auth</td></tr>
  <tr><td>Separate <code>user_passwords</code> table</td><td>Easy migration to passkeys / SSO without touching <code>users</code></td><td>Slightly more JOINs</td></tr>
</table>

<p><strong>Production polish:</strong> use cookies with <code>HttpOnly; Secure; SameSite=Lax</code>; rotate session ID on privilege changes; add <code>auth_attempts</code> cleanup job (prune &gt; 30 days); store <code>totp_secret</code> encrypted via column-level <strong>AES_ENCRYPT</strong> with key in <strong>HashiCorp Vault</strong> or <strong>AWS KMS</strong>; consider stepping up to <strong>WebAuthn / passkeys</strong> &mdash; the modern stack (Auth0, Clerk, WorkOS, Stytch) handles all of this so you can focus on application logic.</p>
'''

ANSWERS[3] = r'''
<p><strong>Situation:</strong> a blog needs posts with rich content, threaded comments, and many-to-many tags. Common queries: posts by tag, comments on a post, search by keyword, recent posts feed.</p>

<p><strong>Approach:</strong> three core tables (<code>posts</code>, <code>comments</code>, <code>tags</code>) plus a junction table for the post-tag M2M. Use <code>FULLTEXT</code> for search; index for the access patterns you actually have.</p>

<pre><code>CREATE TABLE posts (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  author_id   BIGINT NOT NULL,
  slug        VARCHAR(255) NOT NULL UNIQUE,
  title       VARCHAR(255) NOT NULL,
  body        MEDIUMTEXT NOT NULL,
  status      ENUM('draft','published','archived') NOT NULL DEFAULT 'draft',
  published_at DATETIME NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  comment_count INT UNSIGNED NOT NULL DEFAULT 0,    -- denormalized counter
  FOREIGN KEY (author_id) REFERENCES users(id),
  INDEX idx_posts_published (status, published_at DESC),
  FULLTEXT KEY ft_posts (title, body)
);

CREATE TABLE comments (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  post_id     BIGINT NOT NULL,
  parent_id   BIGINT NULL,                        -- threaded replies
  author_id   BIGINT NOT NULL,
  body        TEXT NOT NULL,
  status      ENUM('visible','hidden','spam') NOT NULL DEFAULT 'visible',
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id)   REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
  FOREIGN KEY (author_id) REFERENCES users(id),
  INDEX idx_comments_post (post_id, created_at)
);

CREATE TABLE tags (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  slug  VARCHAR(64) NOT NULL UNIQUE,
  name  VARCHAR(64) NOT NULL
);

CREATE TABLE post_tags (
  post_id BIGINT NOT NULL,
  tag_id  INT NOT NULL,
  PRIMARY KEY (post_id, tag_id),
  KEY idx_pt_tag (tag_id, post_id),               -- "posts with tag X"
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id)  REFERENCES tags(id)  ON DELETE CASCADE
);</code></pre>

<p><strong>Common queries:</strong></p>

<pre><code>-- Latest published posts (homepage feed)
SELECT id, slug, title, published_at
FROM posts
WHERE status = 'published'
ORDER BY published_at DESC
LIMIT 20;

-- Posts by tag
SELECT p.id, p.slug, p.title, p.published_at
FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
WHERE pt.tag_id = ? AND p.status = 'published'
ORDER BY p.published_at DESC
LIMIT 20;

-- Comments tree for a post
WITH RECURSIVE comment_tree AS (
  SELECT id, post_id, parent_id, body, created_at, 0 AS depth
  FROM comments
  WHERE post_id = ? AND parent_id IS NULL AND status = 'visible'
  UNION ALL
  SELECT c.id, c.post_id, c.parent_id, c.body, c.created_at, ct.depth + 1
  FROM comments c
  JOIN comment_tree ct ON c.parent_id = ct.id
  WHERE c.status = 'visible'
)
SELECT * FROM comment_tree
ORDER BY depth, created_at;

-- Full-text search
SELECT id, slug, title,
       MATCH(title, body) AGAINST(? IN NATURAL LANGUAGE MODE) AS score
FROM posts
WHERE status = 'published'
  AND MATCH(title, body) AGAINST(? IN NATURAL LANGUAGE MODE)
ORDER BY score DESC
LIMIT 20;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Cost</th></tr>
  <tr><td>Junction table for tags</td><td>Standard M2M; supports tag pages efficiently</td><td>One extra JOIN per tag query</td></tr>
  <tr><td>Composite key on post_tags</td><td>No duplicate (post,tag) pairs; covering index for both directions</td><td>None &mdash; cheaper than surrogate id</td></tr>
  <tr><td>Adjacency list for comments</td><td>Simple; recursive CTE for trees</td><td>Recursive query at O(depth)</td></tr>
  <tr><td>Denormalized <code>comment_count</code></td><td>Avoid <code>COUNT(*)</code> on every post listing</td><td>Sync on insert/delete via trigger or app code</td></tr>
  <tr><td>FULLTEXT index</td><td>Built-in; works for moderate scale</td><td>No stemming, no fuzzy &mdash; step out to Elasticsearch / Meilisearch when needed</td></tr>
</table>

<p><strong>Production polish:</strong> add a "tag cloud" view backed by <code>SELECT tag_id, COUNT(*) FROM post_tags</code> (cache 5 min); paginate comments at depth-2 (load more via API); store post bodies as Markdown, render server-side; for blogs &gt; 100k posts, replace FULLTEXT with <strong>Meilisearch</strong> or <strong>Typesense</strong> &mdash; both ship a single-binary self-hosted search engine and crush MySQL FULLTEXT for relevance and typo tolerance.</p>
'''

ANSWERS[4] = r'''
<p><strong>Situation:</strong> a school database needs to model students taking many courses, courses having many students, with the relationship carrying its own attributes &mdash; enrollment date, grade, status. The classic many-to-many problem.</p>

<p><strong>Approach:</strong> a junction table <code>enrollments</code> &mdash; not just a pair of foreign keys, but a first-class entity because the enrollment <em>itself</em> has data attached.</p>

<pre><code>CREATE TABLE students (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  student_code VARCHAR(20) NOT NULL UNIQUE,
  first_name   VARCHAR(50) NOT NULL,
  last_name    VARCHAR(50) NOT NULL,
  email        VARCHAR(255) NOT NULL UNIQUE,
  enrolled_on  DATE NOT NULL
);

CREATE TABLE courses (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  course_code  VARCHAR(20) NOT NULL UNIQUE,        -- 'CS-101'
  title        VARCHAR(150) NOT NULL,
  credits      TINYINT UNSIGNED NOT NULL,
  department   VARCHAR(50) NOT NULL,
  status       ENUM('open','closed','archived') NOT NULL DEFAULT 'open'
);

-- The junction table -- carries its own attributes
CREATE TABLE enrollments (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  student_id      INT NOT NULL,
  course_id       INT NOT NULL,
  semester        VARCHAR(10) NOT NULL,            -- '2026-Spring'
  enrolled_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status          ENUM('enrolled','dropped','completed','failed') NOT NULL DEFAULT 'enrolled',
  final_grade     CHAR(2),                         -- 'A+', 'B-', etc.
  grade_points    DECIMAL(3, 2),

  UNIQUE KEY uq_student_course_semester (student_id, course_id, semester),
  INDEX idx_enrollments_course   (course_id, semester),
  INDEX idx_enrollments_student  (student_id, semester),

  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE RESTRICT,
  FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE RESTRICT
);</code></pre>

<p><strong>Common queries:</strong></p>

<pre><code>-- All courses a student is taking this semester
SELECT c.course_code, c.title, c.credits, e.status
FROM enrollments e
JOIN courses c ON c.id = e.course_id
WHERE e.student_id = ? AND e.semester = '2026-Spring'
ORDER BY c.course_code;

-- Roster for a course
SELECT s.student_code, s.last_name, s.first_name, e.final_grade
FROM enrollments e
JOIN students s ON s.id = e.student_id
WHERE e.course_id = ? AND e.semester = '2026-Spring'
ORDER BY s.last_name, s.first_name;

-- GPA per student (4-point scale)
SELECT s.id, s.last_name,
       ROUND(SUM(e.grade_points * c.credits) / SUM(c.credits), 2) AS gpa
FROM students s
JOIN enrollments e ON e.student_id = s.id
JOIN courses c     ON c.id = e.course_id
WHERE e.status = 'completed'
GROUP BY s.id, s.last_name;

-- Course capacity check
SELECT COUNT(*) AS enrolled
FROM enrollments
WHERE course_id = ? AND semester = '2026-Spring' AND status = 'enrolled';</code></pre>

<p><strong>Atomic enrollment with capacity check:</strong></p>

<pre><code>START TRANSACTION;

-- Lock the course row to prevent over-enrollment
SELECT capacity INTO @cap FROM courses WHERE id = ? FOR UPDATE;

SELECT COUNT(*) INTO @enrolled
FROM enrollments
WHERE course_id = ? AND semester = ? AND status = 'enrolled';

IF @enrolled &lt; @cap THEN
  INSERT INTO enrollments (student_id, course_id, semester) VALUES (?, ?, ?);
  COMMIT;
ELSE
  ROLLBACK;     -- 'Course full'
END IF;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Alternative</th></tr>
  <tr><td>Junction table as a real entity</td><td>Carries grade/status/enrolled_at; queries are clean</td><td>Two-column composite is enough only for pure M2M without attributes</td></tr>
  <tr><td>UNIQUE on (student, course, semester)</td><td>Same student can retake a course in a later semester &mdash; allowed</td><td>UNIQUE on (student, course) blocks retakes</td></tr>
  <tr><td>Indexes both directions</td><td>"Student&rsquo;s courses" and "course&rsquo;s students" both fast</td><td>One index forces a full scan in the other direction</td></tr>
  <tr><td>Surrogate <code>id</code> on enrollments</td><td>Enrollment can be referenced (assignments, grades)</td><td>Composite PK works if no FKs ever target enrollments</td></tr>
  <tr><td>ON DELETE RESTRICT</td><td>Don&rsquo;t silently lose academic history</td><td>CASCADE if soft-deleting students entirely</td></tr>
</table>

<p><strong>Production polish:</strong> partition <code>enrollments</code> by <code>semester</code> once you cross ~10M rows (drop old semesters as a partition operation, instant); add <code>capacity</code> + <code>waitlist_position</code> for over-enrollment workflows; consider <code>SELECT ... FOR UPDATE SKIP LOCKED</code> for waitlist promotion processing; archive completed semesters to a <strong>ClickHouse</strong> warehouse for historical analytics, keep MySQL focused on the active term.</p>
'''

ANSWERS[5] = r'''
<p><strong>Situation:</strong> a library system tracks books (with multiple authors), members (who can borrow), loans (which book, who, when due), and returns. Common queries: what does this member have out, what books are overdue, find a book by title or author.</p>

<p><strong>Approach:</strong> separate <code>books</code> from <code>book_copies</code> (you have multiple physical copies of one title); M2M between books and authors; <code>loans</code> tracks the active and historical borrowing.</p>

<pre><code>CREATE TABLE books (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  isbn      CHAR(13) UNIQUE,                     -- nullable: not all old books have ISBN
  title     VARCHAR(255) NOT NULL,
  publisher VARCHAR(150),
  pub_year  YEAR,
  category  VARCHAR(80),
  FULLTEXT KEY ft_books_title (title)
);

CREATE TABLE authors (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  INDEX idx_authors_name (name)
);

CREATE TABLE book_authors (
  book_id   INT NOT NULL,
  author_id INT NOT NULL,
  ord       TINYINT NOT NULL DEFAULT 1,        -- author order on cover
  PRIMARY KEY (book_id, author_id),
  KEY idx_ba_author (author_id, book_id),
  FOREIGN KEY (book_id)   REFERENCES books(id)   ON DELETE CASCADE,
  FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Physical copies of each title -- a popular book has many copies
CREATE TABLE book_copies (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  book_id      INT NOT NULL,
  barcode      VARCHAR(32) NOT NULL UNIQUE,
  acquired_on  DATE NOT NULL,
  status       ENUM('available','on_loan','reserved','lost','retired')
                 NOT NULL DEFAULT 'available',
  FOREIGN KEY (book_id) REFERENCES books(id),
  INDEX idx_copies_book_status (book_id, status)
);

CREATE TABLE members (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  card_no    VARCHAR(20) NOT NULL UNIQUE,
  full_name  VARCHAR(150) NOT NULL,
  email      VARCHAR(255) UNIQUE,
  status     ENUM('active','suspended','expired') NOT NULL DEFAULT 'active',
  joined_on  DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE loans (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  copy_id       BIGINT NOT NULL,
  member_id     INT NOT NULL,
  loaned_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  due_at        DATETIME NOT NULL,
  returned_at   DATETIME NULL,
  fine_cents    INT UNSIGNED NOT NULL DEFAULT 0,
  FOREIGN KEY (copy_id)   REFERENCES book_copies(id),
  FOREIGN KEY (member_id) REFERENCES members(id),
  INDEX idx_loans_member_open (member_id, returned_at),
  INDEX idx_loans_copy        (copy_id),
  INDEX idx_loans_due_open    (due_at, returned_at)     -- overdue queries
);</code></pre>

<p><strong>Common queries:</strong></p>

<pre><code>-- What does member 42 have out right now?
SELECT b.title, l.due_at,
       DATEDIFF(NOW(), l.due_at) AS days_overdue
FROM loans l
JOIN book_copies c ON c.id = l.copy_id
JOIN books       b ON b.id = c.book_id
WHERE l.member_id = 42 AND l.returned_at IS NULL
ORDER BY l.due_at;

-- Overdue books with member contact
SELECT m.full_name, m.email, b.title, l.due_at
FROM loans l
JOIN members     m ON m.id = l.member_id
JOIN book_copies c ON c.id = l.copy_id
JOIN books       b ON b.id = c.book_id
WHERE l.returned_at IS NULL AND l.due_at &lt; NOW()
ORDER BY l.due_at;

-- Search by author
SELECT b.id, b.title
FROM books b
JOIN book_authors ba ON ba.book_id = b.id
JOIN authors      a  ON a.id = ba.author_id
WHERE a.name LIKE 'Octavia%'
ORDER BY b.title;</code></pre>

<p><strong>Loan checkout (atomic):</strong></p>

<pre><code>START TRANSACTION;

-- Find an available copy and lock it
SELECT id INTO @copy
FROM book_copies
WHERE book_id = ? AND status = 'available'
LIMIT 1
FOR UPDATE SKIP LOCKED;

IF @copy IS NULL THEN
  ROLLBACK;     -- no copies free
ELSE
  UPDATE book_copies SET status = 'on_loan' WHERE id = @copy;
  INSERT INTO loans (copy_id, member_id, due_at)
  VALUES (@copy, ?, NOW() + INTERVAL 14 DAY);
  COMMIT;
END IF;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th></tr>
  <tr><td>books / book_copies split</td><td>One title, many physical copies &mdash; loans target a copy, not a title</td></tr>
  <tr><td>SKIP LOCKED on available copy</td><td>Two librarians checking out the same book don&rsquo;t collide</td></tr>
  <tr><td>Composite (member, returned_at) index</td><td>"Active loans for member" is the hottest query</td></tr>
  <tr><td>Status enum on copies</td><td>Captures lost/retired without deleting history</td></tr>
  <tr><td>Loan history kept (returned_at NULL or set)</td><td>Compliance, statistics, member reading history</td></tr>
</table>

<p><strong>Production polish:</strong> a scheduled job promotes overdue loans to "fines" status; reservations queue uses <code>FOR UPDATE SKIP LOCKED</code>; for very large libraries, partition <code>loans</code> by year (instant drop of old data); modern systems often use <strong>Koha</strong> or <strong>FOLIO</strong> as off-the-shelf library management software &mdash; the schema above is what they look like under the hood.</p>
'''

ANSWERS[6] = r'''
<p><strong>Situation:</strong> migrating data between MySQL databases &mdash; could be a version upgrade (5.7 → 8.x), provider switch (self-hosted → RDS / Cloud SQL / PlanetScale), region move, or schema overhaul. Whether downtime is acceptable changes everything.</p>

<p><strong>Approach (zero-downtime):</strong> source + target run in parallel; replicate continuously; cut over apps when target is caught up.</p>

<pre><code>-- 1. Snapshot the source consistently
mysqldump --single-transaction --routines --triggers --events \
          --set-gtid-purged=ON --hex-blob \
          -h source-db -u admin -p \
          mydatabase | gzip &gt; snapshot.sql.gz

# Faster for big DBs: physical backup
xtrabackup --backup --target-dir=/backup/full --user=admin
xtrabackup --prepare --target-dir=/backup/full</code></pre>

<pre><code>-- 2. Restore on the target
gzcat snapshot.sql.gz | mysql -h target-db -u admin -p mydatabase

-- 3. Configure target as a replica of the source
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST     = 'source-db',
  SOURCE_USER     = 'repl_user',
  SOURCE_PASSWORD = '...',
  SOURCE_AUTO_POSITION = 1,           -- GTID-based; no binlog file/position bookkeeping
  SOURCE_SSL = 1;
START REPLICA;

-- 4. Watch lag drop to zero
SHOW REPLICA STATUS\G
-- Seconds_Behind_Source: 0
-- Replica_IO_Running:    Yes
-- Replica_SQL_Running:   Yes</code></pre>

<p><strong>5. Cut over (a few seconds of write pause):</strong></p>

<pre><code>-- On source: stop accepting writes
SET GLOBAL super_read_only = ON;

-- Wait for replica to catch up the last transactions
-- (poll Seconds_Behind_Source = 0 and Retrieved == Executed GTIDs)

-- On target: promote
STOP REPLICA;
RESET REPLICA ALL;
SET GLOBAL super_read_only = OFF;

-- Update DNS / connection strings to point apps at target
-- Apps reconnect; new writes go to target</code></pre>

<p><strong>For schema-changing migrations</strong> (column rename, table split):</p>

<pre><code>-- Use gh-ost or pt-online-schema-change to alter source first
-- pt-online-schema-change builds a copy via triggers, syncs writes, swaps atomically
pt-online-schema-change \
  --alter "ADD COLUMN email_normalized VARCHAR(255) GENERATED ALWAYS AS (LOWER(email)) STORED" \
  D=mydatabase,t=users \
  --execute

-- Or: dual-write -- expand-contract pattern
-- Step 1: Add new column; app keeps reading old, writing both
-- Step 2: Backfill old rows (chunked job)
-- Step 3: App reads new column; verifies match
-- Step 4: Drop old column</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Strategy</th><th>Downtime</th><th>Complexity</th><th>Best for</th></tr>
  <tr><td>Dump + restore + cutover</td><td>Hours (during dump)</td><td>Low</td><td>Small DBs, cold migrations</td></tr>
  <tr><td>Snapshot + binlog replication</td><td>Seconds</td><td>Medium</td><td>Most production migrations</td></tr>
  <tr><td>XtraBackup + replication</td><td>Seconds</td><td>Medium</td><td>Multi-TB databases</td></tr>
  <tr><td>Dual-write (expand-contract)</td><td>Zero</td><td>High</td><td>Schema changes; cross-cloud</td></tr>
  <tr><td>CDC (Debezium → target)</td><td>Zero</td><td>High</td><td>Heterogeneous targets (MySQL → Postgres / MongoDB)</td></tr>
</table>

<p><strong>Production polish:</strong> always do a dry-run against a snapshot in staging; data parity check post-migration via <strong>pt-table-checksum</strong> or row-count + checksum-per-table queries; keep the source running read-only for a week as a fallback; for cross-version upgrades validate <code>information_schema</code> for deprecated features; cloud migrations into <strong>Aurora</strong> or <strong>Cloud SQL</strong> have built-in <strong>DMS</strong> / <strong>Datastream</strong> services that automate the snapshot + CDC pipeline &mdash; usually the right path over hand-rolled tools.</p>
'''

ANSWERS[7] = r'''
<p><strong>Situation:</strong> tracking employee attendance &mdash; clock-in / clock-out, breaks, time off, leave types, plus reporting (hours per week, late arrivals, overtime). Schema must support audit, scale to thousands of employees, and integrate with payroll.</p>

<p><strong>Approach:</strong> separate <code>employees</code>, <code>attendance_events</code> (raw clock punches), <code>shifts</code> (planned schedule), and <code>leave_requests</code> (vacation/sick/PTO). Aggregations are computed from raw events, not stored as derived state.</p>

<pre><code>CREATE TABLE employees (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  emp_code     VARCHAR(20) NOT NULL UNIQUE,
  full_name    VARCHAR(150) NOT NULL,
  department   VARCHAR(80),
  manager_id   INT NULL,
  status       ENUM('active','on_leave','terminated') NOT NULL DEFAULT 'active',
  hired_on     DATE NOT NULL,
  FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- Raw clock events -- append-only; the source of truth
CREATE TABLE attendance_events (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  event_type  ENUM('clock_in','clock_out','break_start','break_end') NOT NULL,
  occurred_at DATETIME(3) NOT NULL,                      -- millisecond precision
  source      ENUM('biometric','rfid','web','mobile','manual') NOT NULL,
  device_id   VARCHAR(50),
  ip_address  VARBINARY(16),
  notes       VARCHAR(255),
  FOREIGN KEY (employee_id) REFERENCES employees(id),
  INDEX idx_attend_emp_time (employee_id, occurred_at),
  INDEX idx_attend_time     (occurred_at)
)
PARTITION BY RANGE (TO_DAYS(occurred_at)) (
  PARTITION p2026_q1 VALUES LESS THAN (TO_DAYS('2026-04-01')),
  PARTITION p2026_q2 VALUES LESS THAN (TO_DAYS('2026-07-01')),
  PARTITION p2026_q3 VALUES LESS THAN (TO_DAYS('2026-10-01')),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);

CREATE TABLE shifts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  shift_date  DATE NOT NULL,
  starts_at   TIME NOT NULL,
  ends_at     TIME NOT NULL,
  UNIQUE KEY uq_emp_date (employee_id, shift_date),
  FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE leave_requests (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  leave_type  ENUM('vacation','sick','personal','bereavement','jury') NOT NULL,
  starts_on   DATE NOT NULL,
  ends_on     DATE NOT NULL,
  status      ENUM('pending','approved','rejected','cancelled') NOT NULL DEFAULT 'pending',
  approved_by INT NULL,
  reason      TEXT,
  FOREIGN KEY (employee_id) REFERENCES employees(id),
  FOREIGN KEY (approved_by) REFERENCES employees(id),
  INDEX idx_leave_emp_dates (employee_id, starts_on, ends_on)
);</code></pre>

<p><strong>Daily hours per employee (the report payroll needs):</strong></p>

<pre><code>-- Pair each clock_in with its next clock_out per employee per day
WITH paired AS (
  SELECT
    employee_id,
    DATE(occurred_at) AS work_date,
    occurred_at AS in_time,
    LEAD(occurred_at) OVER (
      PARTITION BY employee_id, DATE(occurred_at)
      ORDER BY occurred_at
    ) AS out_time,
    event_type
  FROM attendance_events
  WHERE event_type IN ('clock_in', 'clock_out')
    AND occurred_at &gt;= CURDATE() - INTERVAL 7 DAY
)
SELECT
  employee_id,
  work_date,
  ROUND(SUM(TIMESTAMPDIFF(SECOND, in_time, out_time)) / 3600, 2) AS hours_worked
FROM paired
WHERE event_type = 'clock_in' AND out_time IS NOT NULL
GROUP BY employee_id, work_date
ORDER BY work_date, employee_id;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th></tr>
  <tr><td>Append-only event log</td><td>Audit-friendly; corrections add a new event; no destructive updates</td></tr>
  <tr><td>DATETIME(3) precision</td><td>Sub-second matters when biometric scanners record rapid double-punches</td></tr>
  <tr><td>RANGE partition by date</td><td>Drop old quarter as a partition operation; instant; no DELETE storms</td></tr>
  <tr><td>Pair with LEAD() window function</td><td>Compute durations without a self-join</td></tr>
  <tr><td>Separate <code>shifts</code> table</td><td>Compare actual vs planned for late/early/no-show metrics</td></tr>
</table>

<p><strong>Production polish:</strong> add a <code>corrections</code> event type for manager-edited entries (preserves the original); a nightly rollup job populates <code>daily_attendance_summary</code> for fast reports; integrate with payroll via CSV export or API webhook on shift completion; for fleets &gt; 50k employees, stream attendance events into <strong>ClickHouse</strong> via <strong>Debezium</strong> and run analytics there &mdash; MySQL handles the operational workload, ClickHouse handles "show me a year of attendance heatmaps."</p>
'''

ANSWERS[8] = r'''
<p><strong>Situation:</strong> users in an app should receive notifications &mdash; comments on their post, mentions, system alerts, marketing &mdash; with read/unread state, channels (in-app, email, push), and an unread badge count.</p>

<p><strong>Approach:</strong> a single <code>notifications</code> table with polymorphic actor/target via type + ID columns; one row per user per notification; pivot the unread count via a denormalized counter or a fast indexed query.</p>

<pre><code>CREATE TABLE notifications (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id       BIGINT NOT NULL,                    -- recipient
  type          VARCHAR(50) NOT NULL,               -- 'comment.posted', 'mention', 'order.shipped'
  actor_id      BIGINT NULL,                        -- who triggered it
  subject_type  VARCHAR(50) NULL,                   -- 'post', 'order'
  subject_id    BIGINT NULL,
  payload       JSON NOT NULL,                      -- {"post_title": "...", "comment_excerpt": "..."}
  channels      SET('in_app','email','push','sms') NOT NULL DEFAULT 'in_app',
  read_at       DATETIME NULL,
  delivered_at  DATETIME NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  -- Hot query: "user&rsquo;s unread feed, latest first"
  INDEX idx_notif_user_unread (user_id, read_at, id DESC),
  -- Hot query: "user&rsquo;s feed by type"
  INDEX idx_notif_user_type   (user_id, type, id DESC),
  INDEX idx_notif_subject     (subject_type, subject_id)
);

-- User preferences -- per-channel opt in/out per type
CREATE TABLE notification_preferences (
  user_id     BIGINT NOT NULL,
  type        VARCHAR(50) NOT NULL,
  channel     ENUM('email','push','sms') NOT NULL,
  enabled     BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (user_id, type, channel)
);</code></pre>

<p><strong>Common queries:</strong></p>

<pre><code>-- User&rsquo;s feed (unread first, then read)
SELECT id, type, payload, created_at, read_at
FROM notifications
WHERE user_id = ?
ORDER BY id DESC
LIMIT 20;

-- Unread count for the badge
SELECT COUNT(*) AS unread
FROM notifications
WHERE user_id = ? AND read_at IS NULL;

-- Mark all as read
UPDATE notifications
SET read_at = NOW()
WHERE user_id = ? AND read_at IS NULL;

-- Mark single as read
UPDATE notifications
SET read_at = NOW()
WHERE id = ? AND user_id = ? AND read_at IS NULL;</code></pre>

<p><strong>Fan-out write</strong> &mdash; one event becomes many notifications:</p>

<pre><code>-- "User X commented on post Y" notifies the post author + all watchers
INSERT INTO notifications (user_id, type, actor_id, subject_type, subject_id, payload)
SELECT DISTINCT w.user_id, 'comment.posted', ?, 'post', ?,
       JSON_OBJECT('post_id', ?, 'comment_id', ?, 'excerpt', ?)
FROM post_watchers w
WHERE w.post_id = ?
  AND w.user_id &lt;&gt; ?;     -- don&rsquo;t notify the actor</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Alternative</th></tr>
  <tr><td>One row per recipient</td><td>Per-user read state is trivial; cleanup is simple</td><td>Pub-sub model with delivery records &mdash; more complex, scales further</td></tr>
  <tr><td>JSON payload</td><td>Polymorphic content without 50-column tables</td><td>Per-type tables &mdash; cleaner schema, more JOINs</td></tr>
  <tr><td>SET column for channels</td><td>Compact storage; easy filtering</td><td>Junction table for highly variable channel sets</td></tr>
  <tr><td>Composite (user, read_at, id) index</td><td>Unread feed and badge count both fast</td><td>Per-user counter table &mdash; sync overhead</td></tr>
  <tr><td>Pull-based (no push job)</td><td>Simple architecture</td><td>Server-Sent Events / WebSockets for live unread count</td></tr>
</table>

<p><strong>Production polish:</strong> partition by month and drop notifications older than 90 days; offload email/push delivery to a queue (<strong>SQS</strong>, <strong>BullMQ</strong> on Redis, <strong>Kafka</strong>) so DB writes commit fast and worker processes handle external APIs (SES, SendGrid, FCM, Twilio); for unread badges at very high scale, denormalize a <code>users.unread_count</code> column updated on insert/read; the modern hosted alternative is <strong>Knock</strong>, <strong>Courier</strong>, or <strong>Novu</strong> &mdash; they handle template management, multi-channel delivery, and digest grouping out of the box.</p>
'''

ANSWERS[9] = r'''
<p><strong>Situation:</strong> a record needs version history &mdash; "what did this row look like last Tuesday?", "who changed it?", "revert to v3". Common in CMS articles, regulated data (medical records), and compliance audits.</p>

<p><strong>Approach:</strong> three patterns, picked based on how often you query history vs only-current. Most teams use the first.</p>

<p><strong>Pattern 1 &mdash; History table (most common):</strong> one main table for the current state, one history table that records every change. Triggered by INSERT/UPDATE/DELETE.</p>

<pre><code>CREATE TABLE articles (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(255) NOT NULL,
  body        MEDIUMTEXT NOT NULL,
  status      ENUM('draft','published','archived') NOT NULL,
  version     INT NOT NULL DEFAULT 1,
  updated_by  BIGINT NOT NULL,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE articles_history (
  history_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
  id          BIGINT NOT NULL,                 -- the original article id
  version     INT NOT NULL,
  title       VARCHAR(255) NOT NULL,
  body        MEDIUMTEXT NOT NULL,
  status      ENUM('draft','published','archived') NOT NULL,
  changed_by  BIGINT NOT NULL,
  changed_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  operation   ENUM('insert','update','delete') NOT NULL,
  INDEX idx_hist_article_version (id, version)
);

DELIMITER //
CREATE TRIGGER articles_after_update
AFTER UPDATE ON articles
FOR EACH ROW
BEGIN
  INSERT INTO articles_history
    (id, version, title, body, status, changed_by, operation)
  VALUES
    (OLD.id, OLD.version, OLD.title, OLD.body, OLD.status, OLD.updated_by, 'update');
END //
DELIMITER ;</code></pre>

<p><strong>App layer increments version</strong> on every save with optimistic concurrency:</p>

<pre><code>UPDATE articles
SET title = ?, body = ?, status = ?, version = version + 1, updated_by = ?
WHERE id = ? AND version = ?;        -- detect concurrent edit if rows_affected = 0</code></pre>

<p><strong>Pattern 2 &mdash; Effective-dated rows (temporal):</strong> every change is a new row with valid_from/valid_to ranges:</p>

<pre><code>CREATE TABLE article_versions (
  id          BIGINT NOT NULL,
  version     INT NOT NULL,
  title       VARCHAR(255) NOT NULL,
  body        MEDIUMTEXT NOT NULL,
  status      ENUM('draft','published','archived') NOT NULL,
  valid_from  DATETIME NOT NULL,
  valid_to    DATETIME NOT NULL DEFAULT '9999-12-31',  -- "open" current row
  changed_by  BIGINT NOT NULL,
  PRIMARY KEY (id, version),
  INDEX idx_av_id_validity (id, valid_from, valid_to)
);

-- "What did article 42 look like on 2026-01-15?"
SELECT * FROM article_versions
WHERE id = 42 AND '2026-01-15' BETWEEN valid_from AND valid_to;

-- Current version
SELECT * FROM article_versions
WHERE id = 42 AND valid_to = '9999-12-31';</code></pre>

<p><strong>Pattern 3 &mdash; JSON snapshots:</strong> store a JSON diff or full snapshot per change in a single audit table.</p>

<pre><code>CREATE TABLE record_changes (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  table_name   VARCHAR(64) NOT NULL,
  record_id    BIGINT NOT NULL,
  changed_by   BIGINT NOT NULL,
  changed_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  before_data  JSON,
  after_data   JSON,
  INDEX idx_rc_record (table_name, record_id, changed_at)
);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pattern</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>History table + trigger</td><td>Current queries are fast; history isolated</td><td>Trigger logic to maintain; schema drift between main and history</td></tr>
  <tr><td>Effective-dated rows</td><td>"As-of" queries are first-class; one schema</td><td>Every read must filter on validity; bulkier indexes</td></tr>
  <tr><td>JSON snapshots</td><td>Schema-flexible; one audit table for many entities</td><td>Hard to query specific old field values; no integrity</td></tr>
  <tr><td><strong>CDC streaming (Debezium)</strong></td><td>Source of truth in Kafka; durable; replayable</td><td>Operational overhead of stream infrastructure</td></tr>
</table>

<p><strong>Production polish:</strong> for compliance-grade auditing, layer history-table + CDC; ensure history tables are append-only (revoke UPDATE/DELETE); periodically archive old versions to S3 or cold storage; for very large entities, store body diffs (git-style) instead of full snapshots; consider PostgreSQL&rsquo;s native temporal tables or <strong>Snowflake</strong> Time Travel if "as-of" queries are central to your product.</p>
'''

ANSWERS[10] = r'''
<p><strong>Situation:</strong> "top-selling products this month" runs slowly on a 50M-row orders table. The current query joins orders + order_items + products and aggregates &mdash; takes 8 seconds. Need it under 200ms for the dashboard.</p>

<p><strong>Approach:</strong> diagnose with EXPLAIN, then layer fixes &mdash; index for filters, narrow the result set early, denormalize a counter, or roll up to a summary table updated incrementally.</p>

<pre><code>-- The slow query
EXPLAIN ANALYZE
SELECT p.id, p.name, SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN orders o   ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
WHERE o.placed_at &gt;= CURDATE() - INTERVAL 30 DAY
  AND o.status = 'paid'
GROUP BY p.id, p.name
ORDER BY units_sold DESC
LIMIT 10;

-- Likely problems EXPLAIN reveals:
--  - orders: full table scan or index scan on date alone (50M rows)
--  - order_items: hash join with no useful filter
--  - filesort + temporary table for the GROUP BY</code></pre>

<p><strong>Fix 1 &mdash; covering composite index on orders:</strong></p>

<pre><code>CREATE INDEX idx_orders_status_placed ON orders (status, placed_at, id);
-- Now WHERE status='paid' AND placed_at &gt;= ? uses the index
-- and the JOIN to order_items is much smaller</code></pre>

<p><strong>Fix 2 &mdash; index supporting the join + aggregation on order_items:</strong></p>

<pre><code>CREATE INDEX idx_oi_order_product_qty ON order_items (order_id, product_id, quantity);
-- Covering: the optimizer satisfies the JOIN and SUM from the index alone</code></pre>

<p><strong>Fix 3 &mdash; pre-aggregated summary table (the big win):</strong></p>

<pre><code>CREATE TABLE daily_product_sales (
  sale_date    DATE NOT NULL,
  product_id   BIGINT NOT NULL,
  units_sold   INT UNSIGNED NOT NULL,
  revenue_cents BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (sale_date, product_id)
);

-- Nightly job populates yesterday&rsquo;s row
INSERT INTO daily_product_sales (sale_date, product_id, units_sold, revenue_cents)
SELECT DATE(o.placed_at), oi.product_id,
       SUM(oi.quantity),
       SUM(oi.quantity * oi.unit_price_cents)
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.placed_at &gt;= CURDATE() - INTERVAL 1 DAY
  AND o.placed_at &lt;  CURDATE()
  AND o.status = 'paid'
GROUP BY DATE(o.placed_at), oi.product_id
ON DUPLICATE KEY UPDATE
  units_sold    = VALUES(units_sold),
  revenue_cents = VALUES(revenue_cents);

-- Now the dashboard query reads ~30 rows × ~product count = trivial
SELECT p.name, SUM(s.units_sold) AS units_sold
FROM daily_product_sales s
JOIN products p ON p.id = s.product_id
WHERE s.sale_date &gt;= CURDATE() - INTERVAL 30 DAY
GROUP BY s.product_id, p.name
ORDER BY units_sold DESC
LIMIT 10;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Fix</th><th>When</th><th>Cost</th></tr>
  <tr><td>Add filter index</td><td>One-shot relief; query was missing an obvious index</td><td>Tiny: storage + write overhead</td></tr>
  <tr><td>Covering index on join</td><td>Aggregation hot path</td><td>Wider index; more buffer pool space</td></tr>
  <tr><td>Pre-aggregation table</td><td>Dashboard queries are repetitive and predictable</td><td>Stale until next refresh; sync logic</td></tr>
  <tr><td>Real-time materialized view</td><td>Need fresh + fast</td><td>Operational complexity (Materialize / RisingWave / ClickHouse + CDC)</td></tr>
  <tr><td>Move to OLAP (ClickHouse)</td><td>"Top X by Y" is the entire workload</td><td>New system to operate</td></tr>
</table>

<p><strong>Production polish:</strong> always EXPLAIN the new query in production-like data sizes &mdash; not your 1k-row dev DB; track query digest in <code>performance_schema.events_statements_summary_by_digest</code> and alert when the top query&rsquo;s avg time regresses; for top-N type queries with very high concurrency, push to <strong>Redis</strong> sorted sets updated on order completion; for genuinely warehouse-scale analytics, stream orders to <strong>ClickHouse</strong> via <strong>Debezium</strong> and answer the same question in 50ms over years of data.</p>
'''

ANSWERS[11] = r'''
<p><strong>Situation:</strong> social platform with users posting content, others liking and commenting, a feed that&rsquo;s the home page, and follower relationships. Has to scale to millions of users and remain responsive.</p>

<p><strong>Approach:</strong> normalize entities, denormalize hot counters, design for the feed-read pattern (which dominates traffic).</p>

<pre><code>CREATE TABLE users (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(50) NOT NULL UNIQUE,
  email         VARCHAR(255) NOT NULL UNIQUE,
  display_name  VARCHAR(100),
  bio           TEXT,
  follower_count  INT UNSIGNED NOT NULL DEFAULT 0,    -- denormalized
  following_count INT UNSIGNED NOT NULL DEFAULT 0,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id       BIGINT NOT NULL,
  body          TEXT NOT NULL,
  media_urls    JSON,                                -- ['s3://...', ...]
  like_count    INT UNSIGNED NOT NULL DEFAULT 0,     -- denormalized
  comment_count INT UNSIGNED NOT NULL DEFAULT 0,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_posts_user_time (user_id, created_at DESC),
  INDEX idx_posts_time      (created_at DESC)
)
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p2026_q1 VALUES LESS THAN (TO_DAYS('2026-04-01')),
  PARTITION p2026_q2 VALUES LESS THAN (TO_DAYS('2026-07-01')),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- Many-to-many: who follows whom
CREATE TABLE follows (
  follower_id   BIGINT NOT NULL,
  followee_id   BIGINT NOT NULL,
  followed_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (follower_id, followee_id),
  KEY idx_follows_followee (followee_id, follower_id),    -- "who follows me"
  FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (followee_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Likes: one row per like
CREATE TABLE likes (
  user_id      BIGINT NOT NULL,
  post_id      BIGINT NOT NULL,
  liked_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, post_id),
  KEY idx_likes_post (post_id, liked_at),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE comments (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  post_id      BIGINT NOT NULL,
  user_id      BIGINT NOT NULL,
  body         TEXT NOT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_comments_post (post_id, created_at)
);</code></pre>

<p><strong>The feed query (pull model):</strong></p>

<pre><code>-- Posts from people I follow, latest first
SELECT p.id, p.user_id, u.username, u.display_name, p.body, p.media_urls,
       p.like_count, p.comment_count, p.created_at
FROM posts p
JOIN users u  ON u.id = p.user_id
JOIN follows f ON f.followee_id = p.user_id
WHERE f.follower_id = ?
  AND p.created_at &gt;= NOW() - INTERVAL 7 DAY
ORDER BY p.created_at DESC
LIMIT 20;</code></pre>

<p><strong>Like / unlike (atomic counter update):</strong></p>

<pre><code>-- Like
START TRANSACTION;
INSERT IGNORE INTO likes (user_id, post_id) VALUES (?, ?);
-- IGNORE prevents duplicate-like errors
IF ROW_COUNT() = 1 THEN
  UPDATE posts SET like_count = like_count + 1 WHERE id = ?;
END IF;
COMMIT;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Limit</th></tr>
  <tr><td>Pull-model feed</td><td>Simple; post once, read many; works to millions of MAU</td><td>"Celebrity" with 1M followers slow if many posters in feed</td></tr>
  <tr><td>Denormalized counters</td><td>like_count display avoids COUNT(*) per render</td><td>Must keep in sync &mdash; transaction or async correction job</td></tr>
  <tr><td>Partition posts by date</td><td>Drop old data instantly; recent-feed queries hit one partition</td><td>Query across many partitions still slow</td></tr>
  <tr><td>(post_id, liked_at) on likes</td><td>"Who liked this post" page</td><td>Two indexes per like = more write cost</td></tr>
</table>

<p><strong>Production polish:</strong> at significant scale (&gt; 10M MAU), pull-model feed bottlenecks on celebrities &mdash; switch to <strong>fan-out on write</strong> for normal users (push posts to follower inboxes via <strong>Kafka</strong> + <strong>Redis</strong> sorted sets) and pull for celebrities; cache hot post pages in <strong>Redis</strong> with TTL; offload media URLs to <strong>S3 / CloudFront</strong>; for trending/recommendation features, stream events into <strong>ClickHouse</strong> or a dedicated graph DB &mdash; MySQL stays the source of truth, specialized systems serve the queries it&rsquo;s bad at.</p>
'''

ANSWERS[12] = r'''
<p><strong>Situation:</strong> production MySQL holds the entire business; backups must restore reliably, the strategy must work without downtime, and recovery time must meet a written SLA (RPO/RTO). "We have backups" without "we tested restore" is a fairytale.</p>

<p><strong>Approach:</strong> layered backups (logical + physical + binlog), automated, encrypted, off-site, with quarterly restore drills. Different layers cover different failure modes.</p>

<table>
  <tr><th>Layer</th><th>Tool</th><th>Recovery covers</th></tr>
  <tr><td>Logical full</td><td><code>mysqldump</code> / <code>mysqlsh dumpInstance</code></td><td>Cross-version migration; selective table restore</td></tr>
  <tr><td>Physical full</td><td><strong>Percona XtraBackup</strong> / cloud snapshots</td><td>Fast multi-TB restore; same-version DR</td></tr>
  <tr><td>Continuous</td><td>Binlog shipping</td><td>Point-in-time recovery to any second</td></tr>
  <tr><td>Replica</td><td>Live read-replica</td><td>Hardware/AZ failure; ~zero RTO failover</td></tr>
</table>

<p><strong>Daily logical backup script:</strong></p>

<pre><code>#!/bin/bash
set -euo pipefail
DATE=$(date +%Y%m%d_%H%M%S)
DEST=s3://mycompany-mysql-backups/daily

mysqldump \
  --single-transaction --routines --triggers --events \
  --set-gtid-purged=ON --hex-blob \
  --default-character-set=utf8mb4 \
  -u backup_user -p$BACKUP_PASS \
  --all-databases \
  | gzip \
  | aws s3 cp - "$DEST/full_$DATE.sql.gz" \
        --sse aws:kms --sse-kms-key-id $KMS_KEY_ID

# Lifecycle policy on bucket auto-tiers to Glacier after 30 days, deletes after 1 year</code></pre>

<p><strong>Hourly XtraBackup (multi-TB databases):</strong></p>

<pre><code>xtrabackup --backup --target-dir=/backup/$DATE --user=backup_user
xtrabackup --prepare --target-dir=/backup/$DATE
tar czf - /backup/$DATE | aws s3 cp - "s3://.../xtrabackup/$DATE.tar.gz" \
  --sse aws:kms --sse-kms-key-id $KMS_KEY_ID</code></pre>

<p><strong>Continuous binlog shipping (PITR):</strong></p>

<pre><code>-- Configure source to keep binlogs &gt; 7 days
SET GLOBAL binlog_expire_logs_seconds = 604800;

-- Ship to S3 as they rotate (mysqlbinlog --read-from-remote-server)
mysqlbinlog --read-from-remote-server \
  --raw --stop-never \
  --host=primary --user=replicator \
  -- $(NEXT_BINLOG_FILE) \
  | aws s3 cp - "s3://.../binlogs/..."</code></pre>

<p><strong>Point-in-time recovery to "5 minutes before the bad DELETE":</strong></p>

<pre><code># 1. Restore most recent full backup to a fresh instance
xtrabackup --copy-back --target-dir=/backup/2026-04-27_00-00

# 2. Replay binlogs up to the target time
mysqlbinlog \
  --start-datetime="2026-04-27 00:00:00" \
  --stop-datetime="2026-04-27 14:34:55" \   # 5 minutes before bad DELETE
  binlog.000123 binlog.000124 binlog.000125 \
  | mysql -u root -p

# 3. Verify, point app at the restored instance</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Cost</th></tr>
  <tr><td>Backup from a replica, not source</td><td>Avoids load on production during backup</td><td>Need a dedicated backup replica</td></tr>
  <tr><td>Encrypt at rest (KMS)</td><td>Compliance; theft of S3 bucket isn&rsquo;t a data breach</td><td>Slightly slower; key management</td></tr>
  <tr><td>Off-site (cross-region)</td><td>Survives full-region outage</td><td>Egress cost</td></tr>
  <tr><td>Quarterly restore drills</td><td>The only thing that proves backups work</td><td>2-4 hours of engineer time per drill</td></tr>
  <tr><td>Replica + binlog + snapshot</td><td>Defense in depth: each handles different failure</td><td>Operationally complex</td></tr>
</table>

<p><strong>Cloud reality:</strong> <strong>Aurora</strong>, <strong>RDS</strong>, <strong>Cloud SQL</strong>, <strong>PlanetScale</strong> handle most of this automatically &mdash; continuous backups with PITR, automated snapshots, cross-region replication. Self-hosted requires the discipline above; managed services let you focus on application correctness. Either way: <strong>test the restore</strong>. Untested backups fail at the worst possible time.</p>

<p><strong>Production polish:</strong> document RPO (max acceptable data loss) and RTO (max acceptable downtime) per database; alert on missing backups within 1 hour of expected; encrypt backup transport in addition to at-rest; rotate backup credentials quarterly; use <strong>AWS Backup Vault Lock</strong> or <strong>S3 Object Lock</strong> for ransomware-resistant immutable backups.</p>
'''

ANSWERS[13] = r'''
<p><strong>Situation:</strong> a content platform needs tags &mdash; users tag posts with multiple keywords, queries support "posts tagged X" and "posts tagged X AND Y", "popular tags". Standard many-to-many.</p>

<p><strong>Approach:</strong> three tables &mdash; <code>posts</code>, <code>tags</code>, junction <code>post_tags</code>. Composite primary key on the junction prevents duplicates and gives free indexes both directions.</p>

<pre><code>CREATE TABLE tags (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  slug        VARCHAR(64) NOT NULL UNIQUE,        -- 'machine-learning'
  name        VARCHAR(64) NOT NULL,               -- 'Machine Learning'
  usage_count INT UNSIGNED NOT NULL DEFAULT 0,    -- denormalized for tag clouds
  INDEX idx_tags_usage (usage_count DESC)
);

CREATE TABLE posts (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(255) NOT NULL,
  body        MEDIUMTEXT NOT NULL,
  status      ENUM('draft','published') NOT NULL DEFAULT 'draft',
  published_at DATETIME NULL,
  INDEX idx_posts_published (status, published_at DESC)
);

CREATE TABLE post_tags (
  post_id     BIGINT NOT NULL,
  tag_id      INT NOT NULL,
  added_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (post_id, tag_id),
  KEY idx_pt_tag_post (tag_id, post_id),                      -- "posts with tag X"
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id)  REFERENCES tags(id)  ON DELETE CASCADE
);</code></pre>

<p><strong>Common queries:</strong></p>

<pre><code>-- Posts tagged 'mysql' (single tag)
SELECT p.id, p.title, p.published_at
FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t       ON t.id = pt.tag_id
WHERE t.slug = 'mysql' AND p.status = 'published'
ORDER BY p.published_at DESC
LIMIT 20;

-- Posts with ALL of (mysql, performance, indexing)
SELECT p.id, p.title
FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t       ON t.id = pt.tag_id
WHERE t.slug IN ('mysql', 'performance', 'indexing')
  AND p.status = 'published'
GROUP BY p.id, p.title
HAVING COUNT(DISTINCT t.id) = 3
ORDER BY p.published_at DESC;

-- Posts with ANY of (mysql, postgresql)
SELECT DISTINCT p.id, p.title
FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t       ON t.id = pt.tag_id
WHERE t.slug IN ('mysql', 'postgresql')
  AND p.status = 'published'
ORDER BY p.published_at DESC LIMIT 50;

-- Top 20 tags
SELECT slug, name, usage_count
FROM tags
ORDER BY usage_count DESC
LIMIT 20;

-- Tags for a specific post
SELECT t.slug, t.name
FROM tags t
JOIN post_tags pt ON pt.tag_id = t.id
WHERE pt.post_id = ?
ORDER BY t.name;</code></pre>

<p><strong>Atomic tag insert with usage_count maintenance:</strong></p>

<pre><code>START TRANSACTION;

-- Find or create the tag
INSERT INTO tags (slug, name) VALUES (?, ?)
  ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id);
SET @tag_id = LAST_INSERT_ID();

-- Insert junction; ignore duplicate
INSERT IGNORE INTO post_tags (post_id, tag_id) VALUES (?, @tag_id);
IF ROW_COUNT() = 1 THEN
  UPDATE tags SET usage_count = usage_count + 1 WHERE id = @tag_id;
END IF;

COMMIT;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Cost</th></tr>
  <tr><td>Junction table over comma-separated string</td><td>Indexable; supports JOINs; integrity enforced</td><td>One extra JOIN per query</td></tr>
  <tr><td>Composite PK (post_id, tag_id)</td><td>Prevents duplicate tagging; covering index for one direction</td><td>Need second key for the reverse direction</td></tr>
  <tr><td>Denormalized usage_count</td><td>Tag clouds without COUNT(*) per render</td><td>Sync logic on tag/untag</td></tr>
  <tr><td>HAVING COUNT(*) for AND query</td><td>Standard set-intersection pattern</td><td>Slow at extreme scale &mdash; consider per-tag inverted index</td></tr>
  <tr><td>Slug as URL identifier, name for display</td><td>SEO; URL stability when renaming</td><td>Slug must be unique and immutable</td></tr>
</table>

<p><strong>Production polish:</strong> tag input should suggest existing tags (typeahead from <code>tags</code> table); enforce a tag-count limit per post (e.g., 10) at the app layer; for very large platforms (&gt; 100M posts) push tag-search to <strong>Elasticsearch</strong> &mdash; faceted filtering and "more like this" become first-class; the modern alternative for content discovery is <strong>Algolia</strong> or <strong>Meilisearch</strong> indexed off MySQL via <strong>Debezium</strong>.</p>
'''

ANSWERS[14] = r'''
<p><strong>Situation:</strong> sales reporting needs aggregations &mdash; revenue by region by month, top products by quarter, year-over-year growth. Running these on the live <code>orders</code> table is slow and competes with the OLTP workload.</p>

<p><strong>Approach:</strong> roll up raw orders into a star-schema fact table refreshed nightly, with denormalized region/time dimensions. Reports read the rollup, not the raw data.</p>

<pre><code>-- Operational tables (existing)
-- orders(id, customer_id, total_cents, placed_at, status)
-- order_items(id, order_id, product_id, quantity, unit_price_cents)
-- customers(id, region_id, ...)
-- regions(id, name, country)

-- Star-schema fact table
CREATE TABLE fact_sales_daily (
  sale_date     DATE NOT NULL,
  region_id     INT NOT NULL,
  product_id    BIGINT NOT NULL,
  units_sold    INT UNSIGNED NOT NULL,
  revenue_cents BIGINT UNSIGNED NOT NULL,
  order_count   INT UNSIGNED NOT NULL,
  PRIMARY KEY (sale_date, region_id, product_id),
  INDEX idx_fact_region_date (region_id, sale_date),
  INDEX idx_fact_product_date (product_id, sale_date)
)
PARTITION BY RANGE (TO_DAYS(sale_date)) (
  PARTITION p2026_q1 VALUES LESS THAN (TO_DAYS('2026-04-01')),
  PARTITION p2026_q2 VALUES LESS THAN (TO_DAYS('2026-07-01')),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);</code></pre>

<p><strong>Nightly refresh job (idempotent):</strong></p>

<pre><code>-- Recompute yesterday&rsquo;s row
DELETE FROM fact_sales_daily WHERE sale_date = CURDATE() - INTERVAL 1 DAY;

INSERT INTO fact_sales_daily
  (sale_date, region_id, product_id, units_sold, revenue_cents, order_count)
SELECT
  DATE(o.placed_at)            AS sale_date,
  c.region_id                  AS region_id,
  oi.product_id                AS product_id,
  SUM(oi.quantity)             AS units_sold,
  SUM(oi.quantity * oi.unit_price_cents) AS revenue_cents,
  COUNT(DISTINCT o.id)         AS order_count
FROM orders o
JOIN customers c   ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
WHERE o.placed_at &gt;= CURDATE() - INTERVAL 1 DAY
  AND o.placed_at &lt;  CURDATE()
  AND o.status = 'paid'
GROUP BY DATE(o.placed_at), c.region_id, oi.product_id;</code></pre>

<p><strong>Reports run against the rollup &mdash; instant:</strong></p>

<pre><code>-- Revenue by region, this month
SELECT r.name AS region,
       SUM(f.revenue_cents) / 100 AS revenue,
       SUM(f.order_count)         AS orders
FROM fact_sales_daily f
JOIN regions r ON r.id = f.region_id
WHERE f.sale_date &gt;= DATE_FORMAT(CURDATE(), '%Y-%m-01')
GROUP BY r.id, r.name
ORDER BY revenue DESC;

-- YoY comparison: monthly revenue this year vs last
SELECT DATE_FORMAT(sale_date, '%Y-%m') AS month_key,
       SUM(revenue_cents) / 100 AS revenue
FROM fact_sales_daily
WHERE sale_date &gt;= CURDATE() - INTERVAL 24 MONTH
GROUP BY month_key
ORDER BY month_key;

-- Top 10 products this quarter, by region
SELECT region_id, product_id, SUM(revenue_cents) / 100 AS revenue
FROM fact_sales_daily
WHERE sale_date &gt;= '2026-01-01' AND sale_date &lt; '2026-04-01'
GROUP BY region_id, product_id
ORDER BY region_id, revenue DESC;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Choice</th><th>Why</th><th>Limit</th></tr>
  <tr><td>Pre-aggregated daily rows</td><td>Reports are 1000× faster; OLTP not stressed</td><td>Stale until next refresh; can&rsquo;t drill below day</td></tr>
  <tr><td>DELETE-then-INSERT for refresh</td><td>Idempotent; safe to rerun on partial failure</td><td>Brief gap during refresh</td></tr>
  <tr><td>Partition by date</td><td>Drop old partitions instantly; queries scoped to recent partitions</td><td>Partition pruning only on date filter</td></tr>
  <tr><td>Run on a replica</td><td>Reporting load doesn&rsquo;t touch primary</td><td>Replica lag affects "yesterday" cutoff</td></tr>
  <tr><td>Star schema (region, product as keys)</td><td>Standard BI shape; works with Looker, Metabase, Tableau</td><td>Multi-dimensional growth: region × product × day rows</td></tr>
</table>

<p><strong>Production polish:</strong> for sub-hour freshness, switch to <strong>Materialize</strong> or <strong>RisingWave</strong> &mdash; streaming materialized views over the binlog; for true warehouse scale (multi-billion rows, ad-hoc dimensions), stream into <strong>ClickHouse</strong>, <strong>BigQuery</strong>, or <strong>Snowflake</strong> via <strong>Debezium</strong> and run all analytics there. MySQL keeps the OLTP workload; the warehouse handles "give me revenue by region by hour by product variant for the last 3 years" in 200ms.</p>
'''

ANSWERS[15] = r'''
<p><strong>Situation:</strong> a category tree where a category has subcategories, those have sub-subcategories, with arbitrary depth. Common queries: full subtree of a category, breadcrumb path, all root categories.</p>

<p><strong>Approach:</strong> the four standard hierarchical patterns trade reads against writes. For most product catalogs, <strong>adjacency list</strong> + recursive CTE is the right starting point.</p>

<p><strong>Pattern 1 &mdash; Adjacency list (default):</strong></p>

<pre><code>CREATE TABLE categories (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  parent_id INT NULL,
  name      VARCHAR(100) NOT NULL,
  slug      VARCHAR(120) NOT NULL,
  sort_ord  INT NOT NULL DEFAULT 0,
  UNIQUE KEY uq_parent_slug (parent_id, slug),
  INDEX idx_parent (parent_id, sort_ord),
  FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- All descendants of category 5
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name, slug, 0 AS depth
  FROM categories WHERE id = 5

  UNION ALL

  SELECT c.id, c.parent_id, c.name, c.slug, t.depth + 1
  FROM categories c
  JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth, name;

-- Ancestors (breadcrumb path) for category 47
WITH RECURSIVE ancestors AS (
  SELECT id, parent_id, name, slug, 0 AS hop
  FROM categories WHERE id = 47

  UNION ALL

  SELECT c.id, c.parent_id, c.name, c.slug, a.hop + 1
  FROM categories c
  JOIN ancestors a ON c.id = a.parent_id
)
SELECT * FROM ancestors ORDER BY hop DESC;</code></pre>

<p><strong>Pattern 2 &mdash; Closure table (when descendant queries dominate):</strong></p>

<pre><code>CREATE TABLE category_tree (
  ancestor_id   INT NOT NULL,
  descendant_id INT NOT NULL,
  depth         INT NOT NULL,
  PRIMARY KEY (ancestor_id, descendant_id),
  INDEX idx_descendant (descendant_id),
  FOREIGN KEY (ancestor_id)   REFERENCES categories(id) ON DELETE CASCADE,
  FOREIGN KEY (descendant_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- All descendants of 5 -- one indexed lookup
SELECT c.* FROM categories c
JOIN category_tree t ON c.id = t.descendant_id
WHERE t.ancestor_id = 5 AND t.depth &gt; 0;

-- All ancestors of 47
SELECT c.* FROM categories c
JOIN category_tree t ON c.id = t.ancestor_id
WHERE t.descendant_id = 47 AND t.depth &gt; 0
ORDER BY t.depth DESC;</code></pre>

<p>Insert into closure table requires writing one row for self + one row for every ancestor:</p>

<pre><code>-- Inserting category X under parent P
INSERT INTO categories (parent_id, name, slug) VALUES (P, ?, ?);
SET @new_id = LAST_INSERT_ID();

-- Self-reference
INSERT INTO category_tree (ancestor_id, descendant_id, depth) VALUES (@new_id, @new_id, 0);

-- Copy parent&rsquo;s ancestors with depth + 1
INSERT INTO category_tree (ancestor_id, descendant_id, depth)
SELECT ancestor_id, @new_id, depth + 1
FROM category_tree
WHERE descendant_id = P;</code></pre>

<p><strong>Pattern 3 &mdash; Path enumeration:</strong></p>

<pre><code>ALTER TABLE categories ADD COLUMN path VARCHAR(500);
-- e.g., '/1/4/12/47' for a 4-deep chain

-- All descendants of 5
SELECT * FROM categories WHERE path LIKE '/1/4/5/%';</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Pattern</th><th>Read descendants</th><th>Read ancestors</th><th>Insert</th><th>Move subtree</th></tr>
  <tr><td>Adjacency list</td><td>Recursive CTE</td><td>Recursive CTE</td><td>O(1)</td><td>O(1) update parent_id</td></tr>
  <tr><td>Closure table</td><td>O(1) JOIN</td><td>O(1) JOIN</td><td>O(depth)</td><td>O(descendants × ancestors)</td></tr>
  <tr><td>Path enumeration</td><td>LIKE prefix</td><td>SUBSTRING parse</td><td>O(1)</td><td>O(descendants)</td></tr>
  <tr><td>Nested set</td><td>Range query</td><td>Range query</td><td>O(N)</td><td>O(N)</td></tr>
</table>

<p><strong>Production polish:</strong> store category breadcrumb in a JSON column or denormalized <code>full_path</code> string for the product page (avoid the recursive query on every render); pre-compute and cache the entire tree in the application as a tree object refreshed every 5 minutes &mdash; categories change rarely; for very deep / many-to-many graph data (org charts, social graphs), look at <strong>Neo4j</strong> or PostgreSQL&rsquo;s <code>ltree</code>; in MySQL 8 the recursive CTE is fast enough for nearly every catalog use case.</p>
'''

ANSWERS[16] = r'''
<p><strong>Situation:</strong> articles table has 200k rows; users need to search by keyword in title and body. <code>LIKE '%term%'</code> is slow (no index can be used) and lacks ranking.</p>

<p><strong>Approach:</strong> add a FULLTEXT index on the searchable columns; query with <code>MATCH(...) AGAINST(...)</code>. Works well for moderate scale and English content; for advanced search, push out to a dedicated engine.</p>

<pre><code>CREATE TABLE articles (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(255) NOT NULL,
  body        MEDIUMTEXT NOT NULL,
  author_id   BIGINT NOT NULL,
  status      ENUM('draft','published','archived') NOT NULL DEFAULT 'draft',
  published_at DATETIME NULL,
  FULLTEXT KEY ft_articles (title, body)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;</code></pre>

<p><strong>Three search modes:</strong></p>

<pre><code>-- 1. Natural language (relevance-ranked, simplest)
SELECT id, title,
       MATCH(title, body) AGAINST('mysql performance tuning' IN NATURAL LANGUAGE MODE) AS score
FROM articles
WHERE status = 'published'
  AND MATCH(title, body) AGAINST('mysql performance tuning' IN NATURAL LANGUAGE MODE)
ORDER BY score DESC
LIMIT 20;

-- 2. Boolean mode (operators: + required, - excluded, * prefix, "" phrase)
SELECT id, title,
       MATCH(title, body) AGAINST('+mysql +(performance tuning) -postgresql' IN BOOLEAN MODE) AS score
FROM articles
WHERE MATCH(title, body) AGAINST('+mysql +(performance tuning) -postgresql' IN BOOLEAN MODE);

-- 3. Query expansion (broadens with related terms from top results)
SELECT id, title
FROM articles
WHERE MATCH(title, body) AGAINST('database' WITH QUERY EXPANSION);</code></pre>

<p><strong>Combine with structured filters:</strong></p>

<pre><code>SELECT a.id, a.title, a.published_at,
       MATCH(a.title, a.body) AGAINST(? IN NATURAL LANGUAGE MODE) AS score
FROM articles a
WHERE a.status = 'published'
  AND a.author_id IN (?, ?)
  AND a.published_at &gt;= '2026-01-01'
  AND MATCH(a.title, a.body) AGAINST(? IN NATURAL LANGUAGE MODE)
ORDER BY score DESC
LIMIT 20;</code></pre>

<p><strong>Configuration knobs:</strong></p>

<pre><code>-- Minimum word length (default 3 in InnoDB; 4 in MyISAM)
SHOW VARIABLES LIKE 'innodb_ft_min_token_size';
-- Lower if you need to index 2-letter words (rebuilds index)

-- Stopwords (default has ~30: 'the', 'and', etc.)
SHOW VARIABLES LIKE 'innodb_ft_default_stopword';

-- Custom stopwords table
CREATE TABLE my_stopwords (value VARCHAR(30)) ENGINE=InnoDB;
INSERT INTO my_stopwords VALUES ('foo'),('bar');
SET GLOBAL innodb_ft_server_stopword_table = 'mydb/my_stopwords';</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Aspect</th><th>MySQL FULLTEXT</th><th>Elasticsearch / Meilisearch / Typesense</th></tr>
  <tr><td>Setup</td><td>Built-in; one DDL</td><td>Separate service to operate</td></tr>
  <tr><td>Stemming (run/running/ran)</td><td>None</td><td>Yes</td></tr>
  <tr><td>Synonyms</td><td>None</td><td>Yes</td></tr>
  <tr><td>Typo tolerance ("mysl" finds "mysql")</td><td>None</td><td>Yes</td></tr>
  <tr><td>Faceted filters</td><td>Manual</td><td>Native</td></tr>
  <tr><td>Multi-language</td><td>Limited</td><td>Per-field analyzers</td></tr>
  <tr><td>Scale ceiling</td><td>~1M-10M docs comfortably</td><td>100M+ docs</td></tr>
  <tr><td>Operational cost</td><td>None extra</td><td>Cluster to run, index sync</td></tr>
</table>

<p><strong>Production polish:</strong> use FULLTEXT for blogs, support docs, and most product catalogs &mdash; it&rsquo;s genuinely good enough; index sync is automatic (no separate process). For e-commerce search with facets, instant-search UIs, and millions of docs, push to <strong>Meilisearch</strong> (single binary, easy ops) or <strong>Typesense</strong> (similar) for self-host, or <strong>Algolia</strong> as a SaaS; sync via <strong>Debezium</strong> CDC. For semantic / "find similar" use vector search &mdash; <strong>pgvector</strong> on Postgres, <strong>Pinecone</strong>, <strong>Weaviate</strong>, <strong>Qdrant</strong>, <strong>Milvus</strong> indexed with embeddings.</p>
'''

ANSWERS[17] = r'''
<p><strong>Situation:</strong> a high-write OLTP database (orders, events, logs) grows by millions of rows daily. Old data is rarely queried but takes space, slows backups, and bloats indexes. Need to archive old rows without losing them.</p>

<p><strong>Approach:</strong> a layered strategy &mdash; partition the active table by time, drop old partitions to an archive table or S3, and serve historical reads from a read replica or warehouse.</p>

<p><strong>Step 1 &mdash; Partition the hot table by time:</strong></p>

<pre><code>CREATE TABLE events (
  id          BIGINT NOT NULL AUTO_INCREMENT,
  user_id     BIGINT NOT NULL,
  event_type  VARCHAR(50) NOT NULL,
  payload     JSON,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id, created_at),                  -- partition key must be in PK
  INDEX idx_user_time (user_id, created_at)
)
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p2025_q4 VALUES LESS THAN (TO_DAYS('2026-01-01')),
  PARTITION p2026_q1 VALUES LESS THAN (TO_DAYS('2026-04-01')),
  PARTITION p2026_q2 VALUES LESS THAN (TO_DAYS('2026-07-01')),
  PARTITION p2026_q3 VALUES LESS THAN (TO_DAYS('2026-10-01')),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);</code></pre>

<p><strong>Step 2 &mdash; Archive table for &gt; N-month-old data:</strong></p>

<pre><code>CREATE TABLE events_archive LIKE events;
ALTER TABLE events_archive REMOVE PARTITIONING;
ALTER TABLE events_archive ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;</code></pre>

<p><strong>Step 3 &mdash; Quarterly archival job:</strong></p>

<pre><code>-- Move Q4 2025 partition out (instant, no row-by-row delete)
ALTER TABLE events EXCHANGE PARTITION p2025_q4
       WITH TABLE events_archive_staging;

-- events_archive_staging now contains all Q4 2025 rows
-- events partition p2025_q4 is now empty

-- Bulk-insert into archive
INSERT INTO events_archive
SELECT * FROM events_archive_staging;

TRUNCATE events_archive_staging;

-- Drop the empty partition
ALTER TABLE events DROP PARTITION p2025_q4;

-- Add a new future partition
ALTER TABLE events
  REORGANIZE PARTITION p_future INTO (
    PARTITION p2026_q4 VALUES LESS THAN (TO_DAYS('2027-01-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
  );</code></pre>

<p><strong>Step 4 &mdash; Cold storage for very old data (&gt; 1 year):</strong></p>

<pre><code>-- Export to Parquet/CSV and ship to S3/GCS
SELECT * FROM events_archive WHERE created_at &lt; '2025-01-01'
INTO OUTFILE '/tmp/events_2024.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# aws s3 cp /tmp/events_2024.csv.gz s3://archive/events/year=2024/
# Then: DELETE FROM events_archive WHERE created_at &lt; '2025-01-01';</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Strategy</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>Partition + drop</td><td>Instant; no row-by-row cost</td><td>Partition key must be in PK; granularity = partition size</td></tr>
  <tr><td>EXCHANGE PARTITION</td><td>Move 100M rows in milliseconds</td><td>Schema must match exactly; one shot per partition</td></tr>
  <tr><td>Compressed archive table</td><td>2-4× space saving</td><td>Slower reads; CPU during compression</td></tr>
  <tr><td>S3 / Parquet</td><td>Cheap (cents/GB); virtually unlimited</td><td>No SQL on it without Athena/BigQuery</td></tr>
  <tr><td>Archive in same DB</td><td>Joinable from app code</td><td>Backup includes the archive too</td></tr>
  <tr><td>Stream to ClickHouse / Snowflake</td><td>Reportable forever; columnar storage</td><td>Operational complexity</td></tr>
</table>

<p><strong>Production polish:</strong> automate the archival job in <strong>Airflow</strong>, <strong>Dagster</strong>, or a Kubernetes CronJob; verify row count parity before dropping partitions; for compliance use cases (GDPR, HIPAA) ensure the archive supports targeted deletion of a single user&rsquo;s history; modern alternative for high-velocity event data is to bypass MySQL archival entirely &mdash; write events to <strong>ClickHouse</strong> or <strong>BigQuery</strong> from the start (via <strong>Kafka</strong> or <strong>Debezium</strong>) and keep MySQL for transactional state only.</p>
'''

ANSWERS[18] = r'''
<p><strong>Situation:</strong> a movie rental system tracks the catalog (movies, genres, multiple physical/digital copies), customers, rentals (who rented what when, when due, when returned), and late fees.</p>

<p><strong>Approach:</strong> separate <code>movies</code> from <code>movie_copies</code> (multiple copies of one title); rentals reference the copy, not the title; soft-archive customers and movies rather than deleting.</p>

<pre><code>CREATE TABLE genres (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE movies (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(255) NOT NULL,
  release_year  YEAR NOT NULL,
  rating        ENUM('G','PG','PG-13','R','NC-17') NOT NULL,
  runtime_min   SMALLINT UNSIGNED NOT NULL,
  rental_price_cents INT UNSIGNED NOT NULL,
  daily_late_fee_cents INT UNSIGNED NOT NULL,
  status        ENUM('available','retired') NOT NULL DEFAULT 'available',
  added_on      DATE NOT NULL DEFAULT (CURRENT_DATE),
  INDEX idx_movies_title (title),
  FULLTEXT KEY ft_movies (title)
);

CREATE TABLE movie_genres (
  movie_id INT NOT NULL,
  genre_id INT NOT NULL,
  PRIMARY KEY (movie_id, genre_id),
  KEY idx_mg_genre (genre_id, movie_id),
  FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
  FOREIGN KEY (genre_id) REFERENCES genres(id)
);

-- Physical/digital copies
CREATE TABLE movie_copies (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  movie_id  INT NOT NULL,
  format    ENUM('dvd','blu_ray','digital') NOT NULL,
  barcode   VARCHAR(32) UNIQUE,                      -- physical only
  status    ENUM('available','rented','reserved','lost','damaged') NOT NULL DEFAULT 'available',
  FOREIGN KEY (movie_id) REFERENCES movies(id),
  INDEX idx_copies_movie_status (movie_id, status)
);

CREATE TABLE customers (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  full_name    VARCHAR(150) NOT NULL,
  email        VARCHAR(255) NOT NULL UNIQUE,
  phone        VARCHAR(30),
  address      VARCHAR(255),
  status       ENUM('active','suspended','closed') NOT NULL DEFAULT 'active',
  joined_on    DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE rentals (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id     INT NOT NULL,
  copy_id         BIGINT NOT NULL,
  rented_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  due_at          DATETIME NOT NULL,
  returned_at     DATETIME NULL,
  rental_fee_cents INT UNSIGNED NOT NULL,
  late_fee_cents  INT UNSIGNED NOT NULL DEFAULT 0,
  payment_status  ENUM('pending','paid','refunded') NOT NULL DEFAULT 'pending',
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (copy_id)     REFERENCES movie_copies(id),
  INDEX idx_rentals_customer_active (customer_id, returned_at),
  INDEX idx_rentals_copy             (copy_id),
  INDEX idx_rentals_overdue          (returned_at, due_at)
);</code></pre>

<p><strong>Atomic rental checkout:</strong></p>

<pre><code>START TRANSACTION;

-- Pick an available copy with SKIP LOCKED (multiple clerks safe)
SELECT id INTO @copy
FROM movie_copies
WHERE movie_id = ? AND status = 'available'
LIMIT 1
FOR UPDATE SKIP LOCKED;

IF @copy IS NULL THEN
  ROLLBACK;
ELSE
  UPDATE movie_copies SET status = 'rented' WHERE id = @copy;
  INSERT INTO rentals (customer_id, copy_id, due_at, rental_fee_cents)
  SELECT ?, @copy, NOW() + INTERVAL 7 DAY, rental_price_cents
  FROM movies WHERE id = ?;
  COMMIT;
END IF;</code></pre>

<p><strong>Common reports:</strong></p>

<pre><code>-- Active rentals for a customer
SELECT m.title, r.due_at, DATEDIFF(NOW(), r.due_at) AS days_overdue
FROM rentals r
JOIN movie_copies c ON c.id = r.copy_id
JOIN movies       m ON m.id = c.movie_id
WHERE r.customer_id = ? AND r.returned_at IS NULL
ORDER BY r.due_at;

-- Most rented movies last month
SELECT m.title, COUNT(*) AS rentals
FROM rentals r
JOIN movie_copies c ON c.id = r.copy_id
JOIN movies       m ON m.id = c.movie_id
WHERE r.rented_at &gt;= CURDATE() - INTERVAL 30 DAY
GROUP BY m.id, m.title
ORDER BY rentals DESC
LIMIT 10;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th></tr>
  <tr><td>Movie / movie_copy split</td><td>Rentals reference physical copies; one DVD can&rsquo;t be in two places</td></tr>
  <tr><td>SKIP LOCKED on checkout</td><td>Multiple clerks pick distinct copies; no contention</td></tr>
  <tr><td>Status enum on copy</td><td>Tracks lost/damaged without deleting history</td></tr>
  <tr><td>Late fee separate from rental fee</td><td>Clear accounting; partial refunds easier</td></tr>
  <tr><td>Customer status enum</td><td>Suspend without losing rental history</td></tr>
</table>

<p><strong>Production polish:</strong> a scheduled job calculates and applies late fees at midnight (<code>UPDATE rentals SET late_fee_cents = ... WHERE returned_at IS NULL AND due_at &lt; NOW() - INTERVAL 1 DAY</code>); reservations queue uses <code>FOR UPDATE SKIP LOCKED</code>; for streaming-rental services the schema simplifies (no copies, just licenses + concurrent-stream limits per customer); use <strong>Stripe</strong> or <strong>Adyen</strong> for payment and webhook back to update <code>payment_status</code>; modern equivalents like Plex/Hulu/Netflix run effectively this same schema for their library/holdings, with a streaming layer (DRM, CDN) on top.</p>
'''

ANSWERS[19] = r'''
<p><strong>Situation:</strong> a warehouse needs to track stock levels for products across multiple bins/locations, support reservations (held for a pending order), record receipts and adjustments, and prevent overselling under concurrency.</p>

<p><strong>Approach:</strong> separate "current state" from "movement history." Use atomic UPDATE for adjustments; an append-only ledger gives audit + reconciliation.</p>

<pre><code>CREATE TABLE products (
  id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  sku   VARCHAR(64) NOT NULL UNIQUE,
  name  VARCHAR(255) NOT NULL,
  reorder_point INT UNSIGNED NOT NULL DEFAULT 10,
  reorder_qty   INT UNSIGNED NOT NULL DEFAULT 50
);

CREATE TABLE warehouses (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(20) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  address VARCHAR(255)
);

-- Current state: per product, per warehouse
CREATE TABLE inventory (
  product_id   BIGINT NOT NULL,
  warehouse_id INT NOT NULL,
  on_hand      INT NOT NULL DEFAULT 0,        -- physical count
  reserved     INT NOT NULL DEFAULT 0,        -- earmarked for orders
  in_transit   INT NOT NULL DEFAULT 0,        -- inbound from supplier
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id, warehouse_id),
  FOREIGN KEY (product_id)   REFERENCES products(id),
  FOREIGN KEY (warehouse_id) REFERENCES warehouses(id),
  CHECK (on_hand &gt;= 0 AND reserved &gt;= 0 AND reserved &lt;= on_hand)
);

-- Append-only movement log (audit + reconciliation)
CREATE TABLE inventory_movements (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  product_id    BIGINT NOT NULL,
  warehouse_id  INT NOT NULL,
  movement_type ENUM('receipt','sale','reservation','release','adjustment','transfer_out','transfer_in')
                  NOT NULL,
  qty_change    INT NOT NULL,                  -- can be negative
  reason_code   VARCHAR(50),
  reference_type VARCHAR(30),                   -- 'order','po','manual'
  reference_id  BIGINT,
  performed_by  BIGINT NOT NULL,
  occurred_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_movements_product (product_id, occurred_at),
  INDEX idx_movements_ref     (reference_type, reference_id)
);</code></pre>

<p><strong>Atomic reservation (no oversell):</strong></p>

<pre><code>START TRANSACTION;

-- Lock + atomically check + reserve in one statement
UPDATE inventory
SET reserved = reserved + ?
WHERE product_id   = ?
  AND warehouse_id = ?
  AND on_hand - reserved &gt;= ?;       -- only succeeds if available

IF ROW_COUNT() = 0 THEN
  ROLLBACK;     -- insufficient stock
ELSE
  INSERT INTO inventory_movements
    (product_id, warehouse_id, movement_type, qty_change, reference_type, reference_id, performed_by)
  VALUES (?, ?, 'reservation', ?, 'order', ?, ?);
  COMMIT;
END IF;</code></pre>

<p>The conditional <code>WHERE on_hand - reserved &gt;= ?</code> is the key &mdash; one statement does check and reserve atomically, no race window.</p>

<p><strong>Sale completion (release reservation, decrement on_hand):</strong></p>

<pre><code>START TRANSACTION;
UPDATE inventory
SET on_hand  = on_hand - ?,
    reserved = reserved - ?
WHERE product_id = ? AND warehouse_id = ?;

INSERT INTO inventory_movements (...) VALUES (..., 'sale', -?, 'order', ?, ?);
COMMIT;</code></pre>

<p><strong>Reorder report:</strong></p>

<pre><code>SELECT p.sku, p.name, w.code AS warehouse,
       i.on_hand, i.reserved, i.on_hand - i.reserved AS available,
       p.reorder_point, p.reorder_qty
FROM inventory i
JOIN products  p ON p.id = i.product_id
JOIN warehouses w ON w.id = i.warehouse_id
WHERE i.on_hand - i.reserved &lt; p.reorder_point;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Risk</th></tr>
  <tr><td>Conditional UPDATE for reservation</td><td>Atomic; no race window even under high concurrency</td><td>None &mdash; this is the standard pattern</td></tr>
  <tr><td>Movement log + current state</td><td>Audit; reconciliation; replay history</td><td>Disk + writes are 2× (state + log)</td></tr>
  <tr><td>Per-warehouse rows</td><td>Multi-location stock without complex JSON</td><td>Hot product × hot warehouse row contention</td></tr>
  <tr><td>CHECK on column ranges</td><td>Catches bugs that bypass app logic</td><td>None &mdash; cheap insurance</td></tr>
</table>

<p><strong>Production polish:</strong> nightly reconciliation job recomputes <code>on_hand</code> from movement log to detect drift; integrate with WMS via webhooks; for chains with thousands of stores, partition <code>inventory_movements</code> by month; for very high-throughput inventory (Amazon-scale), consider an event-sourced design with <strong>Kafka</strong> as the source of truth and MySQL/Redis as projections; the modern stack for retail uses <strong>Square</strong>, <strong>Shopify</strong>, or <strong>SAP</strong> as the system of record &mdash; each implements approximately this schema.</p>
'''

ANSWERS[20] = r'''
<p><strong>Situation:</strong> products on a marketplace need customer reviews (1-5 stars + text), with one review per customer per product, helpful/unhelpful voting, moderation, and aggregate ratings on product pages.</p>

<p><strong>Approach:</strong> reviews table with unique (product, customer); separate votes table; denormalized aggregates on the product to avoid <code>AVG</code> per page render.</p>

<pre><code>CREATE TABLE reviews (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  product_id   BIGINT NOT NULL,
  customer_id  BIGINT NOT NULL,
  order_id     BIGINT NULL,                          -- "verified buyer" link
  rating       TINYINT UNSIGNED NOT NULL,            -- 1-5
  title        VARCHAR(150),
  body         TEXT,
  helpful_count   INT UNSIGNED NOT NULL DEFAULT 0,
  unhelpful_count INT UNSIGNED NOT NULL DEFAULT 0,
  status       ENUM('pending','approved','rejected','flagged') NOT NULL DEFAULT 'pending',
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_review_product_customer (product_id, customer_id),
  CHECK (rating BETWEEN 1 AND 5),

  FOREIGN KEY (product_id)  REFERENCES products(id),
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (order_id)    REFERENCES orders(id),
  INDEX idx_reviews_product_status_created (product_id, status, created_at DESC),
  INDEX idx_reviews_status (status, created_at)        -- moderation queue
);

-- Helpful/unhelpful votes
CREATE TABLE review_votes (
  review_id   BIGINT NOT NULL,
  customer_id BIGINT NOT NULL,
  vote        ENUM('helpful','unhelpful') NOT NULL,
  voted_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (review_id, customer_id),
  FOREIGN KEY (review_id)   REFERENCES reviews(id) ON DELETE CASCADE,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Denormalized aggregates on the product
ALTER TABLE products
  ADD COLUMN review_count INT UNSIGNED NOT NULL DEFAULT 0,
  ADD COLUMN rating_sum   INT UNSIGNED NOT NULL DEFAULT 0,
  ADD COLUMN rating_avg   DECIMAL(3,2) GENERATED ALWAYS AS
                          (CASE WHEN review_count = 0 THEN 0
                                ELSE rating_sum / review_count END) VIRTUAL;</code></pre>

<p><strong>Submit a review (atomic with aggregate update):</strong></p>

<pre><code>START TRANSACTION;

INSERT INTO reviews (product_id, customer_id, order_id, rating, title, body)
VALUES (?, ?, ?, ?, ?, ?);
-- UNIQUE constraint prevents duplicate review per customer

UPDATE products
SET review_count = review_count + 1,
    rating_sum   = rating_sum   + ?
WHERE id = ?;

COMMIT;</code></pre>

<p><strong>Vote helpful (idempotent &mdash; can switch vote):</strong></p>

<pre><code>INSERT INTO review_votes (review_id, customer_id, vote)
VALUES (?, ?, 'helpful')
ON DUPLICATE KEY UPDATE vote = VALUES(vote), voted_at = NOW();

-- Then recalculate counts (or use triggers)
UPDATE reviews r
SET helpful_count = (SELECT COUNT(*) FROM review_votes WHERE review_id = r.id AND vote = 'helpful'),
    unhelpful_count = (SELECT COUNT(*) FROM review_votes WHERE review_id = r.id AND vote = 'unhelpful')
WHERE r.id = ?;</code></pre>

<p><strong>Common queries:</strong></p>

<pre><code>-- Reviews for a product (newest first, approved only)
SELECT r.id, r.rating, r.title, r.body, r.helpful_count, r.created_at,
       c.display_name
FROM reviews r
JOIN customers c ON c.id = r.customer_id
WHERE r.product_id = ? AND r.status = 'approved'
ORDER BY r.helpful_count DESC, r.created_at DESC
LIMIT 20;

-- Rating distribution for a product
SELECT rating, COUNT(*) AS n
FROM reviews
WHERE product_id = ? AND status = 'approved'
GROUP BY rating
ORDER BY rating DESC;

-- Moderation queue
SELECT r.id, r.created_at, r.rating, r.body, c.email
FROM reviews r
JOIN customers c ON c.id = r.customer_id
WHERE r.status = 'pending'
ORDER BY r.created_at;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th><th>Cost</th></tr>
  <tr><td>UNIQUE (product, customer)</td><td>Prevents review spam from one customer</td><td>None &mdash; standard practice</td></tr>
  <tr><td>Denormalized rating_avg / count</td><td>Product pages don&rsquo;t pay for AVG/COUNT per render</td><td>Sync logic on review insert/update/delete</td></tr>
  <tr><td>Generated VIRTUAL column for avg</td><td>Avg is always consistent with sum/count</td><td>Computed at read time (cheap)</td></tr>
  <tr><td>Moderation status enum</td><td>Hide spam without deleting (audit trail)</td><td>Filter required on every read</td></tr>
  <tr><td>Verified-buyer order_id link</td><td>Trust signal; "verified buyer" badge</td><td>None &mdash; nullable</td></tr>
</table>

<p><strong>Production polish:</strong> rate-limit submissions per customer (1 review per product, ~5 reviews per day across products); run new reviews through a moderation pipeline (regex + ML toxicity classifier or <strong>Perspective API</strong>); for very large catalogs, run aggregate reads off a read replica and rebuild aggregates incrementally rather than per-write; the modern stack for review-heavy commerce uses <strong>Yotpo</strong>, <strong>Bazaarvoice</strong>, or <strong>Trustpilot</strong> as a hosted layer with the schema above as the canonical store.</p>
'''

ANSWERS[21] = r'''
<p><strong>Situation:</strong> a single MySQL instance has hit its limits &mdash; storage saturating, write throughput plateaued, even hot read paths feel slow. Vertical scaling, caching, and read replicas have been pushed to their limit. Need to spread the data across multiple databases.</p>

<p><strong>Approach:</strong> shard horizontally by a chosen <strong>shard key</strong>. Most teams reach for a hosted solution (Vitess / PlanetScale / TiDB) before rolling their own &mdash; the operational burden of DIY sharding is significant.</p>

<p><strong>Pick the shard key carefully &mdash; this decision is hard to undo:</strong></p>

<table>
  <tr><th>Strategy</th><th>How shard chosen</th><th>Best for</th><th>Watch out for</th></tr>
  <tr><td>Hash sharding</td><td><code>shard = hash(user_id) % N</code></td><td>Even distribution; user-keyed workloads</td><td>Resharding moves nearly all keys</td></tr>
  <tr><td>Range sharding</td><td>Each shard owns a key range</td><td>Time-series; alphabetical</td><td>Hot ranges = hot shard</td></tr>
  <tr><td>Directory sharding</td><td>Lookup table: <code>tenant_id → shard</code></td><td>Multi-tenant SaaS</td><td>Lookup adds a hop</td></tr>
  <tr><td>Geographic</td><td>Region/country → shard</td><td>Data sovereignty (GDPR)</td><td>Uneven shard sizes</td></tr>
</table>

<p><strong>Application-level routing example:</strong></p>

<pre><code>// Shard router (Node/JS)
class ShardRouter {
  constructor(shards) { this.shards = shards; }   // [{pool: pool0, ...}, ...]

  shardFor(userId) {
    const hash = murmurhash3(String(userId));
    return this.shards[hash % this.shards.length];
  }

  async query(userId, sql, params) {
    const shard = this.shardFor(userId);
    return shard.pool.query(sql, params);
  }
}

const result = await router.query(
  user.id,
  'SELECT * FROM orders WHERE user_id = ?',
  [user.id]
);</code></pre>

<p><strong>Costs of sharding:</strong></p>
<ul>
  <li><strong>Cross-shard JOINs</strong> &mdash; impossible. Queries that need data from multiple shards fan out and merge in the app.</li>
  <li><strong>Global aggregates</strong> &mdash; <code>SELECT COUNT(*) FROM orders</code> queries every shard.</li>
  <li><strong>Distributed transactions</strong> &mdash; 2PC is slow; most teams design around it (sagas, eventually consistent).</li>
  <li><strong>Resharding</strong> &mdash; doubling shards moves 50% of keys; weeks of work.</li>
  <li><strong>Schema migrations</strong> &mdash; must run on every shard, ideally in lockstep.</li>
  <li><strong>Operational overhead</strong> &mdash; backups, monitoring, failover &times; N.</li>
</ul>

<p><strong>Modern solutions that hide most of this:</strong></p>

<table>
  <tr><th>Tool</th><th>Type</th><th>Notes</th></tr>
  <tr><td><strong>Vitess</strong></td><td>Self-hosted sharding proxy in front of MySQL</td><td>Powers YouTube, Slack; mature</td></tr>
  <tr><td><strong>PlanetScale</strong></td><td>Managed Vitess</td><td>Online schema changes; resharding without downtime</td></tr>
  <tr><td><strong>TiDB</strong></td><td>MySQL-protocol distributed DB</td><td>Transparent sharding at the storage layer; strong consistency</td></tr>
  <tr><td><strong>CockroachDB</strong></td><td>Postgres-compatible distributed DB</td><td>Geo-distributed multi-region writes</td></tr>
  <tr><td><strong>ProxySQL</strong></td><td>Query router / load balancer</td><td>DIY sharding building block</td></tr>
</table>

<p><strong>Production guidance:</strong></p>
<ul>
  <li><strong>Don&rsquo;t shard until you have to.</strong> Vertical scaling, partitioning, archiving, and caching cover years of runway. Cloud instances now go to 100k+ QPS and tens of TB.</li>
  <li>Shard by a key that <strong>most queries already filter by</strong> (user_id, tenant_id) so cross-shard queries are rare.</li>
  <li>Use <strong>UUIDv7 or KSUID</strong> for IDs &mdash; sortable, globally unique, no auto-increment coordination.</li>
  <li>Plan resharding from day 1 with <strong>logical shards</strong> (1024 logical shards on N physical, double N by remapping &mdash; not by re-hashing every key).</li>
  <li>Monitor per-shard load; rebalance or split hot shards.</li>
</ul>

<p><strong>Realistic recommendation:</strong> for nearly all teams, picking a managed sharded DB (PlanetScale, TiDB Cloud, AlloyDB) is dramatically cheaper than DIY sharding. The exception is teams with the operational maturity and scale of YouTube/Slack/Etsy, who built or adopted Vitess.</p>
'''

ANSWERS[22] = r'''
<p><strong>Situation:</strong> a game leaderboard ranks players by score. Common operations: get top 100, get my rank, get scores around me ("rank 15234 ± 5"). Updates are frequent; ranks should be fresh.</p>

<p><strong>Approach:</strong> for moderate scale, MySQL with the right index works; for high concurrency or huge player counts, <strong>Redis sorted sets</strong> are the right tool with MySQL as the durable store.</p>

<p><strong>MySQL approach (works to a few million players):</strong></p>

<pre><code>CREATE TABLE players (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  username    VARCHAR(50) NOT NULL UNIQUE,
  high_score  INT UNSIGNED NOT NULL DEFAULT 0,
  scored_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  region      VARCHAR(20) NOT NULL,
  INDEX idx_players_score (high_score DESC, scored_at, id),
  INDEX idx_players_region_score (region, high_score DESC)
);

-- Score history table (for "personal best" trends, anti-cheat)
CREATE TABLE score_events (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  player_id   BIGINT NOT NULL,
  score       INT UNSIGNED NOT NULL,
  match_id    VARCHAR(64),
  occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_se_player_time (player_id, occurred_at),
  FOREIGN KEY (player_id) REFERENCES players(id)
);</code></pre>

<p><strong>Update high score (only if higher):</strong></p>

<pre><code>-- Atomic conditional update
UPDATE players
SET high_score = ?, scored_at = NOW()
WHERE id = ? AND high_score &lt; ?;

-- Always log the event regardless
INSERT INTO score_events (player_id, score, match_id) VALUES (?, ?, ?);</code></pre>

<p><strong>Top 100 leaderboard:</strong></p>

<pre><code>SELECT id, username, high_score, scored_at,
       RANK() OVER (ORDER BY high_score DESC, scored_at, id) AS player_rank
FROM players
ORDER BY high_score DESC, scored_at, id
LIMIT 100;</code></pre>

<p><strong>"My rank" &mdash; the tricky one:</strong></p>

<pre><code>-- COUNT players with strictly higher score (+ 1 = my rank)
SELECT 1 + COUNT(*) AS my_rank
FROM players
WHERE high_score &gt; (SELECT high_score FROM players WHERE id = ?);

-- O(N) at worst; index on high_score makes it O(log N + matching rows)
-- Acceptable up to a few million players</code></pre>

<p><strong>Scores around me (15234 ± 5):</strong></p>

<pre><code>WITH me AS (SELECT high_score, id FROM players WHERE id = ?)
SELECT p.id, p.username, p.high_score,
       1 + (SELECT COUNT(*) FROM players WHERE high_score &gt; p.high_score) AS player_rank
FROM players p, me
WHERE (p.high_score, p.id) BETWEEN
        (me.high_score - 100, 0) AND (me.high_score + 100, 999999999)
ORDER BY p.high_score DESC
LIMIT 11;</code></pre>

<p><strong>Redis sorted set approach (high scale):</strong></p>

<pre><code># Update score (atomic; keeps max)
ZADD leaderboard:global GT 15234 player:42      # GT = only if greater

# Top 100
ZREVRANGE leaderboard:global 0 99 WITHSCORES   # O(log N + 100)

# My rank
ZREVRANK leaderboard:global player:42           # O(log N)

# Players around me
my_rank = ZREVRANK leaderboard:global player:42
ZREVRANGE leaderboard:global (my_rank - 5) (my_rank + 5) WITHSCORES</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Top N</th><th>My rank</th><th>Around me</th><th>Scale ceiling</th></tr>
  <tr><td>MySQL with index</td><td>Fast</td><td>O(log N + matching)</td><td>Two queries</td><td>~10M players</td></tr>
  <tr><td>Redis sorted set</td><td>O(log N + N)</td><td>O(log N)</td><td>O(log N + N)</td><td>~100M+</td></tr>
  <tr><td>Pre-computed rank column</td><td>Trivial</td><td>O(1)</td><td>BETWEEN query</td><td>Stale; expensive to refresh</td></tr>
  <tr><td>Approximate rank (HyperLogLog, sketches)</td><td>Trivial</td><td>±10% accuracy</td><td>Approximate</td><td>Unlimited</td></tr>
</table>

<p><strong>Production polish:</strong> store the source of truth in MySQL (durable, queryable, anti-cheat); cache the top 100 in Redis with TTL; use Redis sorted sets for live "my rank" if the game is high-traffic; for tournament play, build per-tournament sorted sets keyed by event; for cross-region leaderboards, use Redis Cluster or per-region sets and merge top-N at query time; modern game backends commonly use <strong>PlayFab</strong>, <strong>Firebase</strong>, or custom Redis + relational hybrid &mdash; the schema above is what they look like under the hood.</p>
'''

ANSWERS[23] = r'''
<p><strong>Situation:</strong> an event-booking platform &mdash; concerts, conferences, classes &mdash; with users reserving seats. Concurrency must prevent double-booking; cancellations free seats; admins manage events and capacity.</p>

<p><strong>Approach:</strong> separate <code>events</code> from <code>event_seats</code> (one row per seat); reservations claim seats with <code>FOR UPDATE</code> for atomicity. For general-admission events, an inventory counter pattern works.</p>

<pre><code>CREATE TABLE venues (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  name      VARCHAR(150) NOT NULL,
  address   VARCHAR(255) NOT NULL,
  city      VARCHAR(100) NOT NULL,
  capacity  INT UNSIGNED NOT NULL
);

CREATE TABLE events (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  venue_id      INT NOT NULL,
  title         VARCHAR(200) NOT NULL,
  description   TEXT,
  starts_at     DATETIME NOT NULL,
  ends_at       DATETIME NOT NULL,
  total_seats   INT UNSIGNED NOT NULL,
  price_cents   INT UNSIGNED NOT NULL,
  status        ENUM('draft','published','cancelled','completed') NOT NULL DEFAULT 'draft',
  FOREIGN KEY (venue_id) REFERENCES venues(id),
  INDEX idx_events_starts (starts_at),
  INDEX idx_events_status (status, starts_at)
);

-- Per-seat model (assigned seating)
CREATE TABLE event_seats (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  event_id    BIGINT NOT NULL,
  seat_label  VARCHAR(20) NOT NULL,                 -- 'A-12', 'Floor-Standing'
  section     VARCHAR(50),
  status      ENUM('available','held','reserved','occupied') NOT NULL DEFAULT 'available',
  held_until  DATETIME NULL,                        -- short hold during checkout
  reservation_id BIGINT NULL,
  UNIQUE KEY uq_event_seat (event_id, seat_label),
  INDEX idx_seats_event_status (event_id, status),
  FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE reservations (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  event_id      BIGINT NOT NULL,
  user_id       BIGINT NOT NULL,
  status        ENUM('pending','confirmed','cancelled','refunded') NOT NULL DEFAULT 'pending',
  seat_count    INT UNSIGNED NOT NULL,
  total_cents   INT UNSIGNED NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  payment_intent VARCHAR(100),
  FOREIGN KEY (event_id) REFERENCES events(id),
  FOREIGN KEY (user_id)  REFERENCES users(id),
  INDEX idx_res_event_status (event_id, status),
  INDEX idx_res_user (user_id, created_at DESC)
);</code></pre>

<p><strong>Atomic seat hold (15-minute hold during checkout):</strong></p>

<pre><code>START TRANSACTION;

-- Reserve N specific seats; FOR UPDATE locks them
SELECT id FROM event_seats
WHERE event_id = ? AND seat_label IN (?, ?, ?) AND status = 'available'
FOR UPDATE;
-- Verify count matches request; otherwise rollback (someone took one)

UPDATE event_seats
SET status = 'held', held_until = NOW() + INTERVAL 15 MINUTE
WHERE event_id = ? AND seat_label IN (?, ?, ?) AND status = 'available';

-- Verify ROW_COUNT() = requested seat count
INSERT INTO reservations (event_id, user_id, seat_count, total_cents)
VALUES (?, ?, ?, ?);

COMMIT;</code></pre>

<p><strong>General-admission inventory counter:</strong></p>

<pre><code>-- Conditional UPDATE prevents oversell without per-seat rows
UPDATE events
SET total_seats = total_seats - ?
WHERE id = ? AND total_seats &gt;= ?;

-- ROW_COUNT() = 1 → success; 0 → sold out</code></pre>

<p><strong>Hold-expiry job (runs every minute):</strong></p>

<pre><code>UPDATE event_seats
SET status = 'available', held_until = NULL, reservation_id = NULL
WHERE status = 'held' AND held_until &lt; NOW();

-- And cancel the corresponding reservations
UPDATE reservations r
JOIN (...) ON ...
SET r.status = 'cancelled'
WHERE r.status = 'pending' AND r.created_at &lt; NOW() - INTERVAL 15 MINUTE;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Decision</th><th>Why</th></tr>
  <tr><td>Per-seat row vs counter</td><td>Per-seat needed for assigned seating (concert hall); counter for GA (festival)</td></tr>
  <tr><td>Held state with timeout</td><td>Lets users finish checkout without losing the seat to another buyer</td></tr>
  <tr><td>FOR UPDATE on the seat read</td><td>Prevents two users grabbing the same seat in parallel</td></tr>
  <tr><td>UNIQUE (event, seat_label)</td><td>Schema-level integrity; no duplicate seat rows</td></tr>
  <tr><td>Separate reservations table</td><td>Multiple seats in one purchase; payment lifecycle isolated</td></tr>
</table>

<p><strong>Production polish:</strong> integrate with <strong>Stripe</strong> or <strong>Adyen</strong> for payment; use webhooks to confirm reservations on payment success; support waitlists with <code>FOR UPDATE SKIP LOCKED</code> when seats free up; for very large venues (&gt; 100k tickets) cache seat status in <strong>Redis</strong> for fast availability map renders, MySQL stays the durable record; modern booking platforms (Eventbrite, Ticketmaster, SeatGeek) implement variations of this; <strong>Hopin</strong>, <strong>Luma</strong>, and <strong>Sched</strong> for conferences add session-level scheduling but the core booking model is the same.</p>
'''

ANSWERS[24] = r'''
<p><strong>Situation:</strong> regulatory or compliance requirements demand a tamper-evident audit log of changes to critical tables (orders, balances, user PII). Auditors need: who, what, when, before, after &mdash; and they need it to survive even if the application is compromised.</p>

<p><strong>Approach:</strong> three layers, picked based on rigor needed:</p>

<table>
  <tr><th>Layer</th><th>Mechanism</th><th>Tamper resistance</th></tr>
  <tr><td>Application audit log</td><td>App writes audit rows on every change</td><td>Low &mdash; relies on app correctness</td></tr>
  <tr><td>Trigger-based audit</td><td>BEFORE/AFTER triggers write to history</td><td>Medium &mdash; bypassed if user has DDL</td></tr>
  <tr><td>Audit plugin</td><td>MySQL Enterprise / Percona / MariaDB plugin</td><td>High &mdash; logs every statement at server level</td></tr>
  <tr><td>Binlog / CDC</td><td>Stream binlog (Debezium → Kafka)</td><td>Highest &mdash; durable, replayable, off-database</td></tr>
</table>

<p><strong>Layer 1 &mdash; History tables with triggers:</strong></p>

<pre><code>CREATE TABLE orders_audit (
  audit_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id     BIGINT NOT NULL,
  operation    ENUM('insert','update','delete') NOT NULL,
  changed_by   BIGINT NOT NULL,
  changed_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  before_data  JSON,
  after_data   JSON,
  INDEX idx_audit_order (order_id, changed_at),
  INDEX idx_audit_user  (changed_by, changed_at)
);

DELIMITER //
CREATE TRIGGER orders_audit_insert AFTER INSERT ON orders
FOR EACH ROW
BEGIN
  INSERT INTO orders_audit (order_id, operation, changed_by, after_data)
  VALUES (NEW.id, 'insert', NEW.updated_by,
          JSON_OBJECT('status', NEW.status, 'total_cents', NEW.total_cents,
                      'customer_id', NEW.customer_id));
END //

CREATE TRIGGER orders_audit_update AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
  INSERT INTO orders_audit (order_id, operation, changed_by, before_data, after_data)
  VALUES (NEW.id, 'update', NEW.updated_by,
          JSON_OBJECT('status', OLD.status, 'total_cents', OLD.total_cents),
          JSON_OBJECT('status', NEW.status, 'total_cents', NEW.total_cents));
END //

CREATE TRIGGER orders_audit_delete AFTER DELETE ON orders
FOR EACH ROW
BEGIN
  INSERT INTO orders_audit (order_id, operation, changed_by, before_data)
  VALUES (OLD.id, 'delete', OLD.updated_by,
          JSON_OBJECT('status', OLD.status, 'total_cents', OLD.total_cents));
END //
DELIMITER ;</code></pre>

<p>Track <em>who</em> made the change by adding a session-set context column:</p>

<pre><code>-- App sets this on every connection
SET @audit_user_id = ?;     -- the human user, not the DB account

-- Trigger reads it
... INSERT INTO orders_audit (..., changed_by, ...) VALUES (..., @audit_user_id, ...);</code></pre>

<p><strong>Layer 2 &mdash; Audit plugin (MySQL-server-level statement logging):</strong></p>

<pre><code>-- MariaDB / Percona Audit Plugin
INSTALL PLUGIN server_audit SONAME 'server_audit.so';

SET GLOBAL server_audit_logging = ON;
SET GLOBAL server_audit_events  = 'CONNECT,QUERY,TABLE';
SET GLOBAL server_audit_file_path = '/var/log/mysql/audit.log';</code></pre>

<p>Output: every connection, every statement, with user + IP + statement text. Forward via <strong>Filebeat / Fluentd / Vector</strong> to <strong>Splunk / Elasticsearch / Loki / Datadog Logs</strong>.</p>

<p><strong>Layer 3 &mdash; CDC (highest assurance):</strong></p>

<pre><code>-- Configure binlog in ROW format
[mysqld]
binlog_format     = ROW
binlog_row_image  = FULL
log_bin           = mysql-bin
gtid_mode         = ON
enforce_gtid_consistency = ON

-- Debezium connector reads the binlog and streams to Kafka
-- Each row change → Kafka event with before/after image
-- Kafka topics retain weeks/months/forever; immutable
-- Audit queries hit Kafka or a derived store (ClickHouse, Snowflake)</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>App-level only</td><td>Simple; flexible logging</td><td>Bypassed by direct SQL; not compliance-grade</td></tr>
  <tr><td>Triggers</td><td>Atomic with the change; can&rsquo;t bypass via app</td><td>Triggers can be dropped by sysadmins; perf overhead</td></tr>
  <tr><td>Audit plugin</td><td>Server-level; covers all access</td><td>Volume can be huge; needs forwarding/retention</td></tr>
  <tr><td>CDC streaming</td><td>Durable; replayable; off-database storage</td><td>Operational complexity (Kafka cluster, Debezium)</td></tr>
</table>

<p><strong>Production polish:</strong> revoke UPDATE/DELETE on audit tables to prevent post-hoc tampering (audit user has INSERT only); ship audit logs off the production DB to cold storage (S3 with Object Lock for immutability); for SOX/HIPAA/PCI compliance, layer multiple approaches; build user-friendly "audit viewer" tooling so investigators don&rsquo;t need DB access; modern compliance platforms (<strong>Drata</strong>, <strong>Vanta</strong>, <strong>Sumo Logic</strong>, <strong>Datadog Cloud SIEM</strong>) consume these streams and produce auditor-ready reports.</p>
'''

ANSWERS[25] = r'''
<p><strong>Situation:</strong> a system spans multiple MySQL instances &mdash; sharded by region, or replicated across data centers, or in a multi-master setup. Reads or writes happen on different nodes; data must remain consistent enough for correctness without sacrificing too much availability or performance.</p>

<p><strong>Approach:</strong> consistency in distributed systems is a spectrum &mdash; pick the right model per workload. The CAP theorem says you can&rsquo;t have consistency, availability, and partition tolerance all at once during a network partition; modern choices land on a sliding scale.</p>

<table>
  <tr><th>Model</th><th>Guarantees</th><th>Cost</th><th>Use when</th></tr>
  <tr><td><strong>Strong / linearizable</strong></td><td>Reads see latest committed write everywhere</td><td>Latency; requires consensus (Paxos/Raft)</td><td>Money, identity, regulated data</td></tr>
  <tr><td><strong>Eventual</strong></td><td>Replicas converge; "last write wins"</td><td>Stale reads window</td><td>Catalog, analytics, social timelines</td></tr>
  <tr><td><strong>Read-your-writes</strong></td><td>You see your own changes immediately</td><td>Route reads to source post-write or sticky-session</td><td>Most user-facing apps</td></tr>
  <tr><td><strong>Monotonic reads</strong></td><td>Once you&rsquo;ve seen value V, you don&rsquo;t see older</td><td>Sticky session per user</td><td>Pagination, feeds</td></tr>
  <tr><td><strong>Bounded staleness</strong></td><td>Reads at most N seconds old</td><td>Replica lag monitoring + routing</td><td>Reporting, dashboards</td></tr>
</table>

<p><strong>Tools you have in MySQL:</strong></p>

<pre><code>-- 1. Synchronous replication via Group Replication (InnoDB Cluster)
-- Source waits for majority quorum before commit returns
plugin_load_add = 'group_replication.so'
group_replication_consistency = AFTER         -- read-after-write across cluster

-- 2. Semi-synchronous replication (compromise)
SET GLOBAL rpl_semi_sync_source_enabled = ON;
-- Source waits for at least 1 replica to ACK before commit returns
-- Loses the last few seconds of writes max if source crashes

-- 3. Read-your-writes via routing
-- App sends reads to source for N seconds after a write, then to replica</code></pre>

<p><strong>Cross-shard transactions &mdash; usually impossible cleanly:</strong></p>

<pre><code>-- 2PC works but is slow + a coordinator failure leaves locks dangling
-- Modern alternative: Saga pattern -- a sequence of local transactions
--   with compensating actions for rollback

-- Order placement spans payments DB + inventory DB
-- Step 1: Reserve inventory (commits locally)
-- Step 2: Charge payment (commits locally)
-- Step 3: Mark order shipped (commits locally)
-- If step 2 fails: emit "release inventory" event (compensation)</code></pre>

<p><strong>Conflict resolution in multi-master:</strong></p>

<pre><code>-- Group Replication detects conflicts and aborts the later transaction
-- The app gets a deadlock-like error; retries

-- Without GR: last-write-wins, version vectors, or CRDT data types
-- All require app-level discipline; brittle</code></pre>

<p><strong>Production patterns:</strong></p>

<table>
  <tr><th>Pattern</th><th>What it gives you</th></tr>
  <tr><td>Single-primary writes, replicas for reads</td><td>Strong consistency for writes; tunable read freshness</td></tr>
  <tr><td>Read-after-write routing</td><td>App reads from primary for K seconds post-write</td></tr>
  <tr><td>Sticky sessions on a replica</td><td>Monotonic reads per user</td></tr>
  <tr><td>Idempotency keys</td><td>Retries don&rsquo;t double-charge / double-create</td></tr>
  <tr><td>Outbox pattern + CDC</td><td>App writes to local DB + outbox; Debezium streams to Kafka; eventual consistency with durability</td></tr>
  <tr><td>Saga orchestration</td><td>Long-running multi-service workflows; compensations on failure</td></tr>
</table>

<p><strong>Trade-offs:</strong></p>
<ul>
  <li>Strong consistency cross-region is <strong>expensive</strong> &mdash; Paxos round-trips at the speed of light add tens to hundreds of ms.</li>
  <li>Most apps don&rsquo;t need it everywhere &mdash; users see "your post will appear shortly" patterns and accept seconds of staleness.</li>
  <li>Money/inventory/auth need strong; product catalog / social feed / analytics get away with eventual.</li>
</ul>

<p><strong>Modern stack:</strong> for multi-region strong consistency, native distributed databases like <strong>CockroachDB</strong>, <strong>Spanner</strong>, <strong>YugabyteDB</strong>, or <strong>TiDB</strong> handle the hard parts (consensus, conflict resolution) instead of bolting them onto MySQL. <strong>PlanetScale</strong> offers MySQL-compatible distributed via Vitess; <strong>Aurora Global Database</strong> gives sub-second cross-region replication. For most teams: pick a managed system that matches your consistency needs, not roll your own.</p>
'''

ANSWERS[26] = r'''
<p><strong>Situation:</strong> a system processes millions of transactions per day &mdash; an order pipeline, payment ledger, ticketing platform &mdash; and MySQL must handle the write throughput plus concurrent analytical reads without falling over.</p>

<p><strong>Approach:</strong> the optimization stack runs from schema and indexing up through hardware. Address each layer; skipping straight to bigger hardware wastes money on inefficient queries.</p>

<pre><code>-- Server tuning: critical InnoDB knobs (my.cnf)
innodb_buffer_pool_size       = 75% of RAM      -- the single biggest win
innodb_buffer_pool_instances  = 8               -- reduce internal contention
innodb_log_file_size          = 2G              -- larger redo log absorbs write spikes
innodb_flush_log_at_trx_commit = 1              -- 1 = full ACID; 2 = trade durability for speed
innodb_io_capacity            = 2000            -- match SSD/NVMe IOPS
innodb_io_capacity_max        = 4000
innodb_flush_method           = O_DIRECT        -- bypass OS page cache (avoid double-buffering)
sync_binlog                   = 1               -- 1 = durable; 100 = group commit, faster

-- Schema-level: choose the smallest type that fits
CREATE TABLE orders (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,  -- not UUID-as-CHAR(36)!
  customer_id INT UNSIGNED NOT NULL,
  amount      DECIMAL(12,2) NOT NULL,
  status      TINYINT UNSIGNED NOT NULL,                    -- enum mapped in app code
  created_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_customer_created (customer_id, created_at),       -- composite for common query
  KEY idx_status_created   (status, created_at)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- Partition hot tables by date for write locality + cheap drop
ALTER TABLE orders PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p202604 VALUES LESS THAN (TO_DAYS('2026-05-01')),
  PARTITION p202605 VALUES LESS THAN (TO_DAYS('2026-06-01')),
  PARTITION pmax    VALUES LESS THAN MAXVALUE
);

-- Batch writes; one INSERT with 1,000 rows beats 1,000 single inserts ~50x
INSERT INTO order_events (order_id, event, ts) VALUES
  (1, 'paid', NOW()), (2, 'shipped', NOW()), ... ;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Lever</th><th>Win</th><th>Cost</th></tr></thead>
  <tbody>
    <tr><td>Bigger buffer pool</td><td>Hot data in RAM &rarr; reads avoid disk</td><td>RAM cost; warm-up after restart</td></tr>
    <tr><td>Read replicas</td><td>Spread SELECT load; reports off primary</td><td>Replication lag; app must route</td></tr>
    <tr><td>Async commit (<code>flush_log_at_trx_commit=2</code>)</td><td>2-3x write throughput</td><td>Up to 1s of committed transactions lost on OS crash</td></tr>
    <tr><td>Partitioning by date</td><td>Pruning + cheap archive</td><td>All partition keys must be in PK</td></tr>
    <tr><td>Sharding</td><td>Linear write scale</td><td>Major operational complexity; cross-shard joins die</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: profile <em>before</em> tuning &mdash; <code>EXPLAIN ANALYZE</code>, <strong>Percona PMM</strong> or <strong>Datadog DBM</strong> to find the top-N expensive queries (<code>sys.statement_analysis</code>). Keep <strong>ProxySQL</strong> or <strong>RDS Proxy</strong> in front for connection pooling and read/write splitting. Push aggregations to <strong>ClickHouse</strong> via <strong>Debezium</strong> CDC instead of running them on the OLTP primary &mdash; that single move buys most platforms a year of headroom. <strong>Aurora MySQL</strong> or <strong>PlanetScale</strong> (Vitess) absorb traffic that would otherwise force sharding. The order in 2026: tune queries &rarr; add replicas &rarr; cache (<strong>Redis</strong>) &rarr; offload analytics &rarr; <em>then</em> consider sharding. Most "MySQL can&rsquo;t handle our load" stories are missing indexes.</p>
'''

ANSWERS[27] = r'''
<p><strong>Situation:</strong> the system records continuous measurements over time &mdash; sensor temperatures, app metrics, IoT telemetry, stock ticks &mdash; with high write rates, append-mostly access, and queries that aggregate over time windows.</p>

<p><strong>Approach:</strong> use a narrow append-only schema, partition by time, build only indexes the dashboards need, and downsample old data to keep the table size bounded. MySQL works for moderate volumes; for true time-series scale, pair with <strong>TimescaleDB</strong> or <strong>ClickHouse</strong>.</p>

<pre><code>-- Sensors registry (slow-changing dimension)
CREATE TABLE sensors (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  external_id VARCHAR(64) NOT NULL UNIQUE,
  location    VARCHAR(100),
  unit        VARCHAR(20)                                    -- 'celsius', 'pa', etc.
);

-- Measurements: append-only fact table, partitioned by month
CREATE TABLE sensor_readings (
  sensor_id  INT NOT NULL,
  ts         DATETIME(3) NOT NULL,
  value      DOUBLE NOT NULL,
  PRIMARY KEY (sensor_id, ts)                                -- clustered: time-sorted writes
) ENGINE=InnoDB
PARTITION BY RANGE (TO_DAYS(ts)) (
  PARTITION p202604 VALUES LESS THAN (TO_DAYS('2026-05-01')),
  PARTITION p202605 VALUES LESS THAN (TO_DAYS('2026-06-01')),
  PARTITION pmax    VALUES LESS THAN MAXVALUE
);

-- Pre-aggregated rollup for dashboards (1-minute, 1-hour buckets)
CREATE TABLE sensor_readings_1m (
  sensor_id INT NOT NULL,
  bucket    DATETIME NOT NULL,
  avg_val   DOUBLE,
  min_val   DOUBLE,
  max_val   DOUBLE,
  count     INT,
  PRIMARY KEY (sensor_id, bucket)
);

-- Hot query: last 24 hours for a sensor (uses PK; partition pruning)
SELECT ts, value
FROM   sensor_readings
WHERE  sensor_id = 42
  AND  ts &gt;= NOW() - INTERVAL 1 DAY
ORDER  BY ts;

-- Aggregation for charts (use rollup, not raw)
SELECT bucket, avg_val
FROM   sensor_readings_1m
WHERE  sensor_id = 42
  AND  bucket &gt;= NOW() - INTERVAL 7 DAY;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>PK = (sensor_id, ts)</td><td>Time-ordered writes per sensor; range scan-friendly</td><td>Cross-sensor queries scan multiple PK ranges</td></tr>
    <tr><td>Monthly partitions</td><td>Drop = instant; query-pruning</td><td>Manual partition maintenance (or scheduler)</td></tr>
    <tr><td>Pre-aggregated rollups</td><td>Sub-second dashboards</td><td>Background job complexity</td></tr>
    <tr><td>Stay in MySQL</td><td>One DB, simple ops</td><td>Caps out around ~100K writes/sec</td></tr>
    <tr><td>Move to TimescaleDB / ClickHouse</td><td>10-100x writes; native time functions</td><td>Two systems to operate</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: run a scheduled event to add next month&rsquo;s partition and drop ones past retention &mdash; <code>ALTER TABLE ... ADD PARTITION</code> / <code>DROP PARTITION</code>. The drop is metadata-only and instant, vastly better than <code>DELETE</code>. Roll up readings via a cron-driven query or <strong>Materialize</strong> / <strong>RisingWave</strong> for streaming aggregates. At meaningful scale the answer in 2026 is <strong>TimescaleDB</strong> (Postgres-based, hypertables + continuous aggregates), <strong>ClickHouse</strong> (columnar, MergeTree partitioning), or <strong>InfluxDB 3.0</strong>. Stream raw points via <strong>Kafka</strong> or <strong>Redpanda</strong>, write through <strong>Telegraf</strong> or <strong>Vector</strong>. <strong>Grafana</strong> sits on top regardless of backend. MySQL is fine up to a few thousand writes/sec; past that, the time-series specialists pay for themselves quickly.</p>
'''

ANSWERS[28] = r'''
<p><strong>Situation:</strong> a multi-user application needs role-based access control &mdash; admins, editors, viewers, plus custom team-level roles. Permissions must be auditable, easy to update, and fast to evaluate on every request.</p>

<p><strong>Approach:</strong> classic three-table RBAC: <code>users</code>, <code>roles</code>, <code>permissions</code>, joined by two M2M tables. Permissions are fine-grained verbs on resources; roles are bundles of permissions; users get one or more roles. Cache the resolved permission set per user.</p>

<pre><code>CREATE TABLE roles (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(50) NOT NULL UNIQUE,            -- 'admin', 'editor', 'viewer'
  description VARCHAR(255)
);

CREATE TABLE permissions (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  resource VARCHAR(50) NOT NULL,                       -- 'posts', 'users', 'billing'
  action   VARCHAR(20) NOT NULL,                       -- 'read', 'create', 'update', 'delete'
  UNIQUE KEY uq_resource_action (resource, action)
);

CREATE TABLE role_permissions (
  role_id       INT NOT NULL,
  permission_id INT NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  FOREIGN KEY (role_id)       REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

CREATE TABLE user_roles (
  user_id    INT NOT NULL,
  role_id    INT NOT NULL,
  granted_by INT,
  granted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, role_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Resolve all permissions for a user
SELECT DISTINCT p.resource, p.action
FROM   user_roles ur
JOIN   role_permissions rp ON rp.role_id = ur.role_id
JOIN   permissions       p ON p.id       = rp.permission_id
WHERE  ur.user_id = ?;

-- Optional: per-resource ownership for fine-grained control (ABAC layer)
CREATE TABLE post_acl (
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  role    ENUM('owner','editor','viewer') NOT NULL,
  PRIMARY KEY (post_id, user_id)
);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Model</th><th>Use when</th><th>Limitation</th></tr></thead>
  <tbody>
    <tr><td>Pure RBAC (3-table)</td><td>Roles map cleanly to job functions</td><td>Per-record permissions get awkward</td></tr>
    <tr><td>RBAC + per-resource ACL</td><td>Documents/projects need fine-grained sharing</td><td>Two systems; queries across both</td></tr>
    <tr><td>ABAC (attribute-based)</td><td>Rules like "users in dept X edit dept X docs"</td><td>Complex policy engine; hard to reason about</td></tr>
    <tr><td>ReBAC (relationship-based, Zanzibar)</td><td>Google Drive-style nested sharing</td><td>Specialized service required</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: cache the resolved permission set in <strong>Redis</strong> per user with a 5-15 minute TTL; invalidate on role changes via pub/sub. Audit every grant via a <code>role_grants_log</code> append-only table &mdash; SOC 2 auditors will ask. For the simple case, libraries like <strong>Casbin</strong> (config-as-code policies, multi-language) or <strong>CASL</strong> (JS/TS, ability-checking in UI + API) sit on top of this schema. For complex sharing graphs &mdash; folders inside teams inside orgs &mdash; the 2026 standard is <strong>Zanzibar-style ReBAC</strong>: <strong>SpiceDB</strong> (Authzed), <strong>Permify</strong>, <strong>OpenFGA</strong> (CNCF, originally Auth0), or <strong>Oso Cloud</strong>. They evaluate "can user X do Y on object Z" in single-digit ms with consistency guarantees. Don&rsquo;t reinvent &mdash; permission systems get gnarly fast and security bugs here are catastrophic.</p>
'''

ANSWERS[29] = r'''
<p><strong>Situation:</strong> data must stay synchronized across multiple MySQL databases &mdash; primary &harr; replica for HA, region &harr; region for global reads, OLTP &rarr; analytics warehouse, or microservice &harr; microservice. The choice of mechanism depends on the consistency and lag tolerances.</p>

<p><strong>Approach:</strong> three production patterns dominate &mdash; native replication, change data capture, and dual-write through an outbox. Pick by direction (one-way vs bidirectional), latency budget (sync vs async), and how strict the consistency requirement is.</p>

<pre><code>-- Pattern 1: native MySQL replication (one primary, many replicas)
-- On primary: ensure GTID + ROW format
SET GLOBAL gtid_mode               = ON;
SET GLOBAL enforce_gtid_consistency = ON;
SET GLOBAL binlog_format            = ROW;

-- On replica: point at primary using GTID auto-positioning
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST          = 'primary.db.internal',
  SOURCE_USER          = 'repl',
  SOURCE_PASSWORD      = '...',
  SOURCE_AUTO_POSITION = 1,
  SOURCE_SSL           = 1;
START REPLICA;
SHOW REPLICA STATUS\G  -- watch Seconds_Behind_Source

-- Pattern 2: CDC out to a different system (Debezium / Maxwell)
-- Debezium streams binlog events to Kafka; consumers write to ClickHouse,
-- a downstream MySQL, search index, etc.

-- Pattern 3: dual-write via transactional outbox
CREATE TABLE outbox (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  aggregate_id  VARCHAR(64) NOT NULL,
  event_type    VARCHAR(50) NOT NULL,
  payload       JSON       NOT NULL,
  created_at    DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  published_at  DATETIME   NULL,
  KEY idx_unpublished (published_at)
);

START TRANSACTION;
  UPDATE orders SET status='paid' WHERE id = 1234;
  INSERT INTO outbox (aggregate_id, event_type, payload)
  VALUES ('order:1234','order_paid', JSON_OBJECT('order_id',1234,'amount',99));
COMMIT;
-- relay process drains outbox &rarr; Kafka / SQS / HTTP webhook</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Pattern</th><th>Latency</th><th>Direction</th><th>Best for</th></tr></thead>
  <tbody>
    <tr><td>Async replication</td><td>ms-seconds lag</td><td>Primary &rarr; replicas</td><td>Read scaling, HA</td></tr>
    <tr><td>Semi-sync</td><td>+RTT per commit</td><td>Primary &rarr; replicas</td><td>Stronger durability, slight latency hit</td></tr>
    <tr><td>Group Replication</td><td>Quorum write</td><td>Multi-primary cluster</td><td>HA without manual failover</td></tr>
    <tr><td>CDC (Debezium)</td><td>Sub-second</td><td>One-way to anything</td><td>Search, warehouse, microservices</td></tr>
    <tr><td>Outbox + relay</td><td>Eventual</td><td>App-controlled</td><td>Cross-service events with no dual-write bug</td></tr>
    <tr><td>Two-phase commit</td><td>Slow + brittle</td><td>Synchronous</td><td>Avoid; sagas are better</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: for HA inside one DC, <strong>InnoDB Cluster</strong> + <strong>MySQL Router</strong> or managed services like <strong>Aurora MySQL</strong>, <strong>PlanetScale</strong>, <strong>Cloud SQL</strong>. For global, <strong>Aurora Global Database</strong> (sub-second cross-region), <strong>PlanetScale</strong> regions, <strong>Vitess</strong> with VReplication, or <strong>YugabyteDB</strong> / <strong>CockroachDB</strong> as MySQL-/Postgres-compatible distributed alternatives. For OLTP &rarr; analytics, <strong>Debezium</strong> &rarr; <strong>Kafka</strong> &rarr; <strong>ClickHouse</strong> / <strong>Snowflake</strong> / <strong>BigQuery</strong> is the default 2026 pipeline. Avoid bidirectional replication where possible &mdash; conflict resolution is genuinely painful. If you must go bidirectional, use a CRDT layer or designate one row owner per region.</p>
'''

ANSWERS[30] = r'''
<p><strong>Situation:</strong> a messaging app needs users, conversations (1:1 and group), messages, read receipts, attachments, presence, and typing state &mdash; with chronological ordering and fast unread counts.</p>

<p><strong>Approach:</strong> normalize conversations and participants; treat messages as an append-only log partitioned by time. Avoid scanning all messages to compute unread counts &mdash; track "last read" per participant.</p>

<pre><code>CREATE TABLE users (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  username     VARCHAR(50) NOT NULL UNIQUE,
  display_name VARCHAR(100),
  avatar_url   VARCHAR(500),
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  type       ENUM('direct','group') NOT NULL,
  title      VARCHAR(255),                                   -- group only
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_message_at DATETIME(3),                               -- denormalized for inbox sort
  KEY idx_last_message (last_message_at)
);

CREATE TABLE conversation_participants (
  conversation_id  BIGINT NOT NULL,
  user_id          INT    NOT NULL,
  joined_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_read_msg_id BIGINT,                                    -- O(1) unread = max_msg_id - this
  muted            BOOLEAN DEFAULT FALSE,
  role             ENUM('member','admin') DEFAULT 'member',
  PRIMARY KEY (conversation_id, user_id),
  KEY idx_user_convs (user_id, conversation_id),              -- inbox: my conversations
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)         REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE messages (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  conversation_id BIGINT  NOT NULL,
  sender_id       INT     NOT NULL,
  body            TEXT,
  attachment_url  VARCHAR(500),
  created_at      DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  edited_at       DATETIME(3) NULL,
  deleted_at      DATETIME(3) NULL,
  KEY idx_conv_created (conversation_id, created_at),
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
  FOREIGN KEY (sender_id)       REFERENCES users(id)
) PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p202604 VALUES LESS THAN (TO_DAYS('2026-05-01')),
  PARTITION pmax    VALUES LESS THAN MAXVALUE
);

-- Inbox query: my conversations sorted by recent activity, with unread count
SELECT c.id, c.title, c.last_message_at,
       (SELECT COUNT(*) FROM messages m
        WHERE  m.conversation_id = c.id
          AND  m.id &gt; COALESCE(cp.last_read_msg_id, 0)) AS unread
FROM   conversation_participants cp
JOIN   conversations c ON c.id = cp.conversation_id
WHERE  cp.user_id = ?
ORDER  BY c.last_message_at DESC
LIMIT  50;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Single <code>messages</code> table</td><td>Simple</td><td>Huge as the app grows; needs partitioning</td></tr>
    <tr><td>Per-conversation message tables</td><td>Smaller per shard</td><td>Schema explosion; cross-conv queries hard</td></tr>
    <tr><td><code>last_read_msg_id</code> per participant</td><td>O(1) unread badge</td><td>Counting unread = COUNT(*); cache it</td></tr>
    <tr><td>Denormalized <code>last_message_at</code></td><td>Fast inbox sort</td><td>Must update on every send</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: presence and typing indicators belong in <strong>Redis</strong> (sets with TTL) or <strong>Pusher</strong> / <strong>Ably</strong>, not MySQL &mdash; the write rate destroys throughput. Real-time delivery is <strong>WebSocket</strong> via <strong>Socket.IO</strong>, <strong>Phoenix Channels</strong>, or managed services like <strong>Pusher Channels</strong>, <strong>Ably</strong>, <strong>PubNub</strong>. End-to-end encryption uses <strong>libsignal</strong> (the protocol behind WhatsApp and Signal). At chat-app scale &mdash; Slack, Discord territory &mdash; messages move to <strong>Cassandra</strong> or <strong>ScyllaDB</strong> (write-optimized, partition by conversation_id). Push notifications via <strong>FCM</strong> / <strong>APNs</strong>. Search via <strong>Meilisearch</strong> / <strong>Typesense</strong> for small apps, <strong>Elasticsearch</strong> / <strong>OpenSearch</strong> for large. The MySQL schema above carries small-to-medium apps comfortably; specialized stores enter at "millions of DAU" scale.</p>
'''

ANSWERS[31] = r'''
<p><strong>Situation:</strong> a system needs to track changes to records &mdash; who changed what, when, from what to what &mdash; for compliance (SOC 2, HIPAA, GDPR), debugging, undo features, or temporal queries.</p>

<p><strong>Approach:</strong> three competing patterns &mdash; (1) shadow history table populated by triggers, (2) effective-dated rows where every change is a new row, or (3) CDC streaming change events to an external store. The right answer depends on what you query.</p>

<pre><code>-- Pattern 1: history table + triggers (simple, MySQL-native)
CREATE TABLE customers (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  name  VARCHAR(100),
  email VARCHAR(255),
  tier  VARCHAR(20),
  updated_by INT,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers_history (
  history_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  name        VARCHAR(100),
  email       VARCHAR(255),
  tier        VARCHAR(20),
  changed_by  INT,
  changed_at  DATETIME NOT NULL,
  operation   ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  KEY idx_customer_changed (customer_id, changed_at)
);

DELIMITER $$
CREATE TRIGGER customers_after_update
AFTER UPDATE ON customers FOR EACH ROW
BEGIN
  INSERT INTO customers_history (customer_id, name, email, tier, changed_by, changed_at, operation)
  VALUES (OLD.id, OLD.name, OLD.email, OLD.tier, NEW.updated_by, NEW.updated_at, 'UPDATE');
END$$
DELIMITER ;

-- Pattern 2: effective-dated rows (temporal table)
CREATE TABLE prices (
  id          INT NOT NULL,
  price       DECIMAL(10,2) NOT NULL,
  valid_from  DATETIME NOT NULL,
  valid_to    DATETIME NULL,                   -- NULL = current
  PRIMARY KEY (id, valid_from),
  KEY idx_current (id, valid_to)
);

-- Price as of any point in time
SELECT price FROM prices
WHERE  id = 42 AND valid_from &lt;= '2026-01-15'
  AND  (valid_to IS NULL OR valid_to &gt; '2026-01-15');

-- Pattern 3: change diff as JSON for compact, generic audit
CREATE TABLE audit_log (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  table_name  VARCHAR(50) NOT NULL,
  record_id   VARCHAR(64) NOT NULL,
  changed_by  INT,
  changed_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  operation   ENUM('INSERT','UPDATE','DELETE') NOT NULL,
  before_data JSON,
  after_data  JSON,
  KEY idx_record (table_name, record_id, changed_at)
);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Pattern</th><th>Strength</th><th>Weakness</th></tr></thead>
  <tbody>
    <tr><td>History tables + triggers</td><td>Per-table; trivial to query "history of X"</td><td>Schema duplication; trigger-debugging pain</td></tr>
    <tr><td>Effective-dated rows</td><td>Native temporal queries; no triggers</td><td>Every JOIN needs a date predicate</td></tr>
    <tr><td>JSON audit log</td><td>One table for every entity</td><td>Querying specific field values is slow</td></tr>
    <tr><td>CDC (Debezium)</td><td>Zero app code; replays binlog</td><td>External system to operate</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: which user made the change is the easiest thing to lose. Set <code>SET @app_user_id = ?</code> at session start so triggers can read it, or include <code>updated_by</code> in every UPDATE explicitly. For compliance-grade audit, the 2026 path is <strong>Debezium</strong> CDC streaming to <strong>S3 with Object Lock</strong> (WORM) or <strong>Snowflake</strong> &mdash; tamper-evident, append-only, queryable for years. Tools like <strong>Datadog Audit Trail</strong>, <strong>Drata</strong>, <strong>Vanta</strong>, <strong>Tugboat Logic</strong> integrate the audit table directly into evidence collection for SOC 2 / ISO 27001. <strong>MariaDB Audit Plugin</strong> or the commercial <strong>MySQL Enterprise Audit</strong> capture <em>every</em> SQL statement at the server &mdash; useful for DBA/ops audit but heavy. Keep history tables in InnoDB (not MyISAM) so they participate in transactions: an INSERT into history that survives a rolled-back UPDATE is worse than no audit at all.</p>
'''

ANSWERS[32] = r'''
<p><strong>Situation:</strong> a SaaS product serves many tenants &mdash; companies, organizations, customers &mdash; from one application. The data must be isolated, performant per tenant, and easy to operate across all tenants (backups, migrations, billing).</p>

<p><strong>Approach:</strong> three industry patterns &mdash; pooled (single schema, <code>tenant_id</code> column), schema-per-tenant, and database-per-tenant. The right one depends on tenant count, isolation requirements, and noisy-neighbor concerns. Pooled is the default until you have a strong reason otherwise.</p>

<pre><code>-- Pattern 1: pooled (recommended default; thousands of tenants)
CREATE TABLE tenants (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  slug   VARCHAR(50) NOT NULL UNIQUE,
  plan   ENUM('free','pro','enterprise'),
  status ENUM('active','suspended') DEFAULT 'active'
);

CREATE TABLE users (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT NOT NULL,                          -- mandatory on every tenant table
  email     VARCHAR(255) NOT NULL,
  KEY idx_tenant_email (tenant_id, email),
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE TABLE projects (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id INT NOT NULL,
  name      VARCHAR(100),
  KEY idx_tenant (tenant_id),
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- EVERY query MUST filter by tenant_id; framework should enforce this
SELECT * FROM projects
WHERE  tenant_id = ?       -- never optional
  AND  status = 'active';

-- Optional: row-level enforcement via views per tenant
CREATE VIEW tenant_42_projects AS
SELECT * FROM projects WHERE tenant_id = 42;

-- Pattern 2: schema-per-tenant
CREATE DATABASE tenant_acme;
CREATE TABLE tenant_acme.projects (...);
-- App connects to a different schema per request based on subdomain.

-- Pattern 3: database-per-tenant (one MySQL instance, N databases; or N instances)
-- Hardest isolation; easiest data export and per-tenant backup/restore.</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Model</th><th>Density</th><th>Isolation</th><th>Operations</th><th>Best for</th></tr></thead>
  <tbody>
    <tr><td>Pooled (shared schema)</td><td>Highest</td><td>App-enforced only</td><td>One migration</td><td>10s of thousands of small tenants</td></tr>
    <tr><td>Schema per tenant</td><td>High</td><td>Stronger; SQL-level</td><td>N migrations</td><td>Hundreds of mid-size tenants</td></tr>
    <tr><td>Database per tenant</td><td>Low</td><td>Strong</td><td>Per-tenant backup; complex</td><td>Compliance-heavy enterprise</td></tr>
    <tr><td>Hybrid (pool + dedicated)</td><td>Mixed</td><td>Tiered</td><td>Most complex</td><td>Free pool + paid dedicated tier</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the <em>biggest</em> risk in pooled multi-tenancy is leaking data across tenants &mdash; a missing <code>WHERE tenant_id = ?</code> in one query and a customer sees another customer&rsquo;s data. Mitigations: an ORM/middleware layer (<strong>Prisma</strong> middleware, <strong>SQLAlchemy</strong> session events, <strong>Hibernate</strong> filters) that injects the predicate automatically, code review checklists, and integration tests that cross-check tenant access. Postgres has true row-level security; MySQL does not, so this discipline matters more. For noisy neighbors, <strong>PlanetScale</strong> or <strong>Vitess</strong> shard by <code>tenant_id</code> using consistent hashing &mdash; large tenants get their own shard. Per-tenant backup/restore is dramatically simpler in schema/database-per-tenant. The 2026 pragmatic answer at most SaaS scales: pooled with <code>tenant_id</code> + <strong>Prisma</strong>/<strong>Drizzle</strong> middleware enforcement, with a tiny escape hatch to move whales to dedicated databases when revenue justifies it.</p>
'''

ANSWERS[33] = r'''
<p><strong>Situation:</strong> the database must remain available during instance failures, AZ outages, and ideally region-level disasters &mdash; with bounded data loss (RPO) and quick recovery time (RTO). Production-grade ops requires a documented replication and failover strategy.</p>

<p><strong>Approach:</strong> deploy a primary with multiple replicas across availability zones, set RPO/RTO targets, automate failover, and run regular DR drills. Use semi-sync or Group Replication where data loss is unacceptable.</p>

<pre><code>-- Topology examples (all use GTID + ROW binlog format)

-- A) Primary + 2 async replicas (read scaling, basic HA)
--    DC1: primary    &harr;     DC1 replica (async)
--    DC2: replica (async, also serves as DR)

-- B) Semi-synchronous (waits for at least one replica ACK before commit)
INSTALL PLUGIN rpl_semi_sync_source PLUGIN_NAME = 'semisync_source.so';
SET GLOBAL rpl_semi_sync_source_enabled = 1;
SET GLOBAL rpl_semi_sync_source_timeout = 1000;  -- ms; falls back to async if all replicas down

-- C) Group Replication / InnoDB Cluster (auto-failover, single-primary or multi-primary)
SET GLOBAL group_replication_bootstrap_group = ON;
START GROUP_REPLICATION;
SET GLOBAL group_replication_bootstrap_group = OFF;
-- Other nodes:
START GROUP_REPLICATION;

-- D) Aurora MySQL: storage-level replication; promote any of 15 replicas in &lt;30s

-- Monitor lag continuously
SHOW REPLICA STATUS\G   -- look at Seconds_Behind_Source, Replica_IO_Running, Replica_SQL_Running

-- Backups for the recovery side
mysqldump --single-transaction --all-databases | gzip &gt; backup.sql.gz   -- small DBs
xtrabackup --backup --target-dir=/backups/$(date +%F)                  -- large; physical, fast restore</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Topology</th><th>RPO</th><th>RTO</th><th>Failover</th><th>Cost</th></tr></thead>
  <tbody>
    <tr><td>Async replication</td><td>Seconds</td><td>Minutes (manual)</td><td>Manual or Orchestrator</td><td>$</td></tr>
    <tr><td>Semi-sync</td><td>~Zero</td><td>Minutes</td><td>Manual or auto</td><td>$$ (commit latency)</td></tr>
    <tr><td>Group Replication</td><td>Zero (quorum)</td><td>Sub-minute</td><td>Automatic</td><td>$$$ (3-9 nodes)</td></tr>
    <tr><td>Aurora / managed</td><td>Zero (storage replicated)</td><td>~30s</td><td>Automatic</td><td>$$$$ (cloud bill)</td></tr>
    <tr><td>Cross-region async</td><td>Seconds-minutes</td><td>Minutes-hours</td><td>Manual region failover</td><td>$$</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the standard 2026 stack is managed &mdash; <strong>Aurora MySQL</strong> (sub-minute failover, 6-way storage replication across 3 AZs, Aurora Global for &lt;1s cross-region), <strong>PlanetScale</strong> (Vitess-based, automatic failover), <strong>Cloud SQL</strong> with HA, <strong>Azure Database for MySQL Flexible Server</strong>. Self-hosted: <strong>Orchestrator</strong> by GitHub for topology management and failover, <strong>ProxySQL</strong> for routing. <strong>InnoDB Cluster</strong> bundles Group Replication + MySQL Router + MySQL Shell. Drill DR quarterly: write a runbook, simulate primary failure, time RTO, validate RPO from binlog gaps. Keep <strong>backups separate from primary</strong>: encrypted, off-region, immutable (S3 Object Lock). Point-in-time recovery via binlog replay is the difference between losing 5 minutes vs an entire day after corruption events. The number-one DR failure mode isn&rsquo;t infrastructure &mdash; it&rsquo;s never having tested the runbook.</p>
'''

ANSWERS[34] = r'''
<p><strong>Situation:</strong> a customer support platform needs tickets, agents, customers, threaded responses, attachments, SLA tracking, tags, and queue routing. Reports need ticket counts by status, response times, and CSAT.</p>

<p><strong>Approach:</strong> normalize tickets and messages; track SLAs with explicit timestamps; denormalize hot ticket fields used in queue views.</p>

<pre><code>CREATE TABLE customers (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  email  VARCHAR(255) NOT NULL UNIQUE,
  name   VARCHAR(100)
);

CREATE TABLE agents (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  email   VARCHAR(255) NOT NULL UNIQUE,
  team_id INT,
  active  BOOLEAN DEFAULT TRUE
);

CREATE TABLE tickets (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  ticket_number   VARCHAR(20) NOT NULL UNIQUE,                -- 'INC-12345' for humans
  customer_id     INT NOT NULL,
  assignee_id     INT NULL,                                    -- agent currently owning it
  subject         VARCHAR(255) NOT NULL,
  status          ENUM('new','open','pending','resolved','closed') NOT NULL DEFAULT 'new',
  priority        ENUM('low','normal','high','urgent') NOT NULL DEFAULT 'normal',
  channel         ENUM('email','web','chat','phone','api') NOT NULL,
  -- SLA tracking timestamps
  created_at      DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  first_responded_at DATETIME(3) NULL,
  resolved_at     DATETIME(3) NULL,
  due_at          DATETIME    NULL,                            -- SLA target
  -- Denormalized for queue view
  last_activity_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  message_count    INT NOT NULL DEFAULT 0,
  KEY idx_status_priority (status, priority, last_activity_at),
  KEY idx_assignee_status (assignee_id, status),
  KEY idx_customer        (customer_id, created_at),
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (assignee_id) REFERENCES agents(id)
);

CREATE TABLE ticket_messages (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  ticket_id   INT NOT NULL,
  author_type ENUM('customer','agent','system') NOT NULL,
  author_id   INT NOT NULL,
  body        TEXT,
  internal    BOOLEAN DEFAULT FALSE,                            -- internal note vs customer-visible
  created_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_ticket_created (ticket_id, created_at),
  FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

CREATE TABLE ticket_tags (
  ticket_id INT NOT NULL,
  tag       VARCHAR(50) NOT NULL,
  PRIMARY KEY (ticket_id, tag),
  KEY idx_tag (tag, ticket_id),
  FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- Queue view: open tickets for an agent, oldest first
SELECT id, ticket_number, subject, priority, last_activity_at
FROM   tickets
WHERE  assignee_id = ? AND status IN ('new','open','pending')
ORDER  BY priority DESC, last_activity_at ASC
LIMIT  50;

-- SLA breach alert: tickets past their due_at and not yet resolved
SELECT id, ticket_number, customer_id, due_at
FROM   tickets
WHERE  due_at &lt; NOW() AND resolved_at IS NULL;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Denormalized <code>message_count</code>, <code>last_activity_at</code></td><td>Cheap queue rendering</td><td>Update on every reply</td></tr>
    <tr><td>SLA timestamps as columns (vs derived)</td><td>Reports without joins</td><td>Trigger or app must populate</td></tr>
    <tr><td>One messages table</td><td>Simple thread query</td><td>Grows fast; partition or archive</td></tr>
    <tr><td>Tags as table (not JSON)</td><td>Index-friendly tag search</td><td>Extra join</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: SLA calculation should account for business hours and customer time zones &mdash; "respond within 4 business hours" is not <code>NOW() + 4 HOUR</code>. Libraries like <strong>BullHours</strong> or service-side rules in <strong>Zendesk</strong> / <strong>Intercom</strong> / <strong>Front</strong> handle this. Full-text search across messages via <strong>Meilisearch</strong>, <strong>Typesense</strong>, or <strong>Elasticsearch</strong>. AI triage and summarization in 2026 is standard: <strong>Intercom Fin</strong>, <strong>Zendesk Resolution Bot</strong>, <strong>Kustomer IQ</strong>, or <strong>Claude</strong>/<strong>GPT-4</strong> APIs invoked from the app to suggest replies and auto-tag. Stream ticket events to <strong>Snowflake</strong> / <strong>BigQuery</strong> via <strong>Debezium</strong> for analytics: response-time distributions, agent productivity, CSAT correlation. <strong>PagerDuty</strong> / <strong>Opsgenie</strong> hooks for "urgent + new + unassigned &gt; 5 min" tickets. Most teams build the schema then realize they should have started with <strong>Zendesk</strong>, <strong>Front</strong>, or <strong>Plain</strong> &mdash; build only when the integrations and AI features of off-the-shelf no longer meet the need.</p>
'''

ANSWERS[35] = r'''
<p><strong>Situation:</strong> an e-commerce or content platform wants to recommend products to users based on their purchase history &mdash; "people who bought X also bought Y", category affinities, similar-user clusters &mdash; with reasonable accuracy and sub-100ms response time.</p>

<p><strong>Approach:</strong> three layers &mdash; (1) compute item-item co-occurrence offline, (2) store recommendations precomputed per user, (3) serve from a fast lookup. MySQL handles the storage; the modeling moves to a warehouse + ML platform.</p>

<pre><code>-- Source: order_items table (the signal)
CREATE TABLE order_items (
  order_id   INT NOT NULL,
  product_id INT NOT NULL,
  PRIMARY KEY (order_id, product_id),
  KEY idx_product (product_id, order_id)
);

-- Item-item co-occurrence (precomputed offline; "X also bought Y")
CREATE TABLE product_recommendations (
  product_id     INT NOT NULL,
  recommended_id INT NOT NULL,
  score          DECIMAL(6,4) NOT NULL,                  -- co-occurrence weighted
  rank           SMALLINT NOT NULL,                      -- 1..N for fast top-K
  computed_at    DATETIME NOT NULL,
  PRIMARY KEY (product_id, rank),
  KEY idx_product_score (product_id, score DESC)
);

-- Personalized recommendations (precomputed per user)
CREATE TABLE user_recommendations (
  user_id     INT NOT NULL,
  product_id  INT NOT NULL,
  score       DECIMAL(6,4) NOT NULL,
  rank        SMALLINT NOT NULL,
  reason      VARCHAR(50),                                -- 'collaborative', 'category', 'recent'
  computed_at DATETIME NOT NULL,
  PRIMARY KEY (user_id, rank)
);

-- Compute job (run nightly): co-occurrence
INSERT INTO product_recommendations (product_id, recommended_id, score, rank, computed_at)
SELECT
  a.product_id,
  b.product_id,
  COUNT(*) / SQRT(
    (SELECT COUNT(*) FROM order_items WHERE product_id = a.product_id) *
    (SELECT COUNT(*) FROM order_items WHERE product_id = b.product_id)
  ) AS cosine_score,
  ROW_NUMBER() OVER (PARTITION BY a.product_id ORDER BY COUNT(*) DESC) AS rank,
  NOW()
FROM   order_items a
JOIN   order_items b ON a.order_id = b.order_id
                    AND a.product_id &lt;&gt; b.product_id
GROUP  BY a.product_id, b.product_id
HAVING rank &lt;= 20;

-- Serve: top-10 recommendations for user 42
SELECT p.id, p.name, p.image_url, ur.reason, ur.score
FROM   user_recommendations ur
JOIN   products p ON p.id = ur.product_id
WHERE  ur.user_id = 42
ORDER  BY ur.rank
LIMIT  10;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Approach</th><th>Win</th><th>Loss</th></tr></thead>
  <tbody>
    <tr><td>Item-item collaborative</td><td>Simple; "also bought" is intuitive</td><td>Cold start: new products have no signal</td></tr>
    <tr><td>User-user collaborative</td><td>Personal taste capture</td><td>Cold start: new users; sparse</td></tr>
    <tr><td>Content-based (categories, embeddings)</td><td>Solves cold start</td><td>No serendipity; obvious recommendations</td></tr>
    <tr><td>Hybrid + reranker</td><td>Best of both</td><td>Real complexity; needs ML infra</td></tr>
    <tr><td>Vector search (embeddings)</td><td>Semantic similarity; works on text/images</td><td>Embedding pipeline + vector store</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026 the realistic stack is &mdash; raw events stream to <strong>Snowflake</strong>, <strong>BigQuery</strong>, or <strong>Databricks</strong> via <strong>Debezium</strong> CDC; train a model with <strong>Spark MLlib</strong>, <strong>TensorFlow Recommenders</strong>, <strong>PyTorch</strong>, or hosted services like <strong>AWS Personalize</strong>, <strong>Vertex AI Recommendations</strong>, or specialized vendors <strong>Algolia Recommend</strong>, <strong>Recombee</strong>, <strong>Coveo</strong>; write back the user_recommendations table or push to <strong>Redis</strong> / <strong>DynamoDB</strong> for sub-10ms reads. Modern fashion / catalog apps use embedding-based similarity: encode products with <strong>OpenAI</strong> / <strong>Cohere</strong> / <strong>VoyageAI</strong> / <strong>Sentence-Transformers</strong>, store vectors in <strong>pgvector</strong>, <strong>Pinecone</strong>, <strong>Weaviate</strong>, <strong>Milvus</strong>, <strong>Qdrant</strong>, or <strong>Vespa</strong>, and run kNN at query time. A/B test religiously &mdash; recommendation models can look great offline and tank conversion. Always log impressions, clicks, and purchases back into the training data; the feedback loop is what makes recommenders improve over time. The MySQL piece is just the system-of-record and the lookup cache; the ML lives elsewhere.</p>
'''

ANSWERS[36] = r'''
<p><strong>Situation:</strong> a production database needs schema changes &mdash; new columns, dropped columns, type changes, index additions &mdash; without taking the application offline. A long ALTER on a billion-row table can lock the table for hours.</p>

<p><strong>Approach:</strong> MySQL 8 supports <code>ALGORITHM=INSTANT</code> for many changes; for everything else, use online schema-change tools (<strong>gh-ost</strong>, <strong>pt-online-schema-change</strong>). Always run an expand-contract migration over multiple deploys for behavior changes.</p>

<pre><code>-- Step 1: check what MySQL 8 can do natively (free)
ALTER TABLE orders ADD COLUMN refunded_at DATETIME, ALGORITHM=INSTANT;
-- INSTANT supports: ADD COLUMN at end (8.0.12+), drop default, rename column,
-- DROP COLUMN (8.0.29+), rename table.
-- INPLACE supports: most index ops, virtual column add, FK add.
-- COPY (the fallback) is the slow one to avoid.

-- For changes that aren&rsquo;t INSTANT/INPLACE, use gh-ost (GitHub) or pt-online-schema-change
-- gh-ost: reads binlog instead of triggers; safer at scale
gh-ost \
  --host=primary.db --user=admin --password=... \
  --database=shop --table=orders \
  --alter='MODIFY status VARCHAR(50)' \
  --execute

-- It creates orders_gho, copies data in chunks, applies binlog events,
-- then atomic-renames at the end.

-- Expand-contract for risky changes (rename column, type change with semantics):
-- Phase 1 (deploy 1): add new column, dual-write, app reads old
ALTER TABLE users ADD COLUMN email_addr VARCHAR(255);
UPDATE users SET email_addr = email WHERE email_addr IS NULL; -- backfill

-- Phase 2 (deploy 2): app reads new column, still writes both
-- Phase 3 (deploy 3): stop writing old column
-- Phase 4 (deploy 4): drop old column
ALTER TABLE users DROP COLUMN email, ALGORITHM=INSTANT;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Method</th><th>Lock impact</th><th>Speed</th><th>Risk</th></tr></thead>
  <tbody>
    <tr><td><code>ALGORITHM=INSTANT</code></td><td>None (metadata-only)</td><td>Sub-second</td><td>Limited operations</td></tr>
    <tr><td><code>ALGORITHM=INPLACE</code></td><td>Brief lock at start/end</td><td>Slow but online</td><td>Some block writes during phases</td></tr>
    <tr><td><code>ALGORITHM=COPY</code></td><td>Full table lock</td><td>Hours-days; blocks writes</td><td>Outage; avoid</td></tr>
    <tr><td>pt-online-schema-change</td><td>Brief; uses triggers</td><td>Hours; throttled</td><td>Triggers add write overhead</td></tr>
    <tr><td>gh-ost</td><td>Brief; binlog-based</td><td>Hours; dynamic throttling</td><td>Best of class for large tables</td></tr>
    <tr><td>Aurora / PlanetScale</td><td>Online by design</td><td>Managed</td><td>Vendor-specific tooling</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: all schema changes go through migration tooling &mdash; <strong>Flyway</strong>, <strong>Liquibase</strong>, <strong>Atlas</strong>, <strong>Sqitch</strong>, or framework-native (<strong>Prisma Migrate</strong>, <strong>Drizzle</strong>, <strong>Rails</strong>, <strong>Django</strong>) &mdash; tracked in version control, applied by CI/CD, never by hand on production. <strong>PlanetScale</strong> turns this entire problem into deploy-the-branch via Vitess + branching; <strong>Aurora</strong> handles many ALTERs online via storage-level mechanisms. <strong>Atlas</strong> by Ariga adds plan/preview/lint to detect destructive ops before merge. Always test the migration on a production-sized clone &mdash; an INSTANT operation in a 100GB test DB might be COPY in production due to row format. Coordinate with replicas: a long ALTER on the primary replicates and runs on every replica. The cardinal rule: <em>never</em> change a column&rsquo;s meaning in place &mdash; expand-contract every time. Apps and databases must be deployable in either order during the rollout.</p>
'''

ANSWERS[37] = r'''
<p><strong>Situation:</strong> a project management tool (think Asana, Linear, Jira) needs projects, tasks, subtasks, users, assignments, statuses, comments, attachments, custom fields, and activity history.</p>

<p><strong>Approach:</strong> normalize core entities; use adjacency-list for subtasks; track status changes via an activity log. Keep custom fields flexible via JSON or EAV depending on query patterns.</p>

<pre><code>CREATE TABLE workspaces (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  slug VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(100)
);

CREATE TABLE projects (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  workspace_id  INT NOT NULL,
  name          VARCHAR(100),
  status        ENUM('active','archived') DEFAULT 'active',
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_workspace (workspace_id, status),
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

CREATE TABLE tasks (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  project_id   INT NOT NULL,
  parent_id    INT NULL,                                       -- subtasks (adjacency list)
  title        VARCHAR(255) NOT NULL,
  description  TEXT,
  status       ENUM('todo','in_progress','review','done') NOT NULL DEFAULT 'todo',
  priority     ENUM('low','medium','high','urgent') DEFAULT 'medium',
  assignee_id  INT NULL,
  reporter_id  INT NOT NULL,
  due_date     DATE,
  position     DECIMAL(10,4),                                  -- for drag-reorder; sparse insert
  custom_fields JSON,                                          -- {sprint: 'Q1', estimate: 5}
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_project_status (project_id, status, position),
  KEY idx_assignee_status (assignee_id, status, due_date),
  KEY idx_parent          (parent_id),
  FOREIGN KEY (project_id)  REFERENCES projects(id),
  FOREIGN KEY (parent_id)   REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (assignee_id) REFERENCES users(id),
  FOREIGN KEY (reporter_id) REFERENCES users(id)
);

CREATE TABLE task_activity (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  task_id    INT NOT NULL,
  actor_id   INT NOT NULL,
  action     ENUM('created','status_changed','assigned','commented','attachment_added') NOT NULL,
  before_val VARCHAR(255),
  after_val  VARCHAR(255),
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_task_created (task_id, created_at),
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Kanban view: tasks for a project, grouped by status, sorted by user-defined position
SELECT id, title, assignee_id, due_date, position
FROM   tasks
WHERE  project_id = ?
ORDER  BY status, position;

-- "My tasks" view across projects
SELECT t.id, t.title, p.name AS project_name, t.due_date, t.priority
FROM   tasks t
JOIN   projects p ON p.id = t.project_id
WHERE  t.assignee_id = ? AND t.status &lt;&gt; 'done'
ORDER  BY t.due_date IS NULL, t.due_date, t.priority DESC;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Adjacency list for subtasks</td><td>Simple; one column</td><td>Deep nesting needs CTE</td></tr>
    <tr><td>JSON <code>custom_fields</code></td><td>Per-workspace flexibility</td><td>Indexing specific fields needs generated columns</td></tr>
    <tr><td><code>DECIMAL position</code> for ordering</td><td>Drag-reorder = single row update; insert between two with average</td><td>Periodic rebalancing as positions get crowded</td></tr>
    <tr><td>Activity log table</td><td>Full timeline; great for notifications</td><td>Grows fast; archive periodically</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: real-time collaboration uses CRDTs &mdash; <strong>Yjs</strong>, <strong>Automerge</strong> &mdash; with <strong>Liveblocks</strong>, <strong>Hocuspocus</strong>, <strong>Partykit</strong>, or self-hosted via <strong>WebSocket</strong>; the database stores periodic snapshots, not every keystroke. Search with <strong>Meilisearch</strong>, <strong>Typesense</strong>, or <strong>Elasticsearch</strong> across tasks/comments/projects. AI summarization, "explain what changed this week", and auto-prioritization are 2026 table-stakes &mdash; <strong>Linear</strong> and <strong>Asana</strong> both ship them via <strong>OpenAI</strong> / <strong>Anthropic</strong> APIs. Notifications via <strong>Knock</strong>, <strong>Courier</strong>, or <strong>Novu</strong> deduplicate "X assigned 5 tasks to you" into a single digest. For activity feeds at scale, <strong>Stream</strong> (getstream.io) is the off-the-shelf option. The hardest UX problem is dependencies and Gantt: model dependencies as <code>task_dependencies(blocker_id, blocked_id)</code>, compute critical path on the server, render with <strong>Frappe Gantt</strong> or <strong>DHTMLX</strong>. The schema is the easy part &mdash; the value is in the integrations and AI layer above it.</p>
'''

ANSWERS[38] = r'''
<p><strong>Situation:</strong> a query joins three or more large tables &mdash; orders, customers, products, payments &mdash; runs in 30+ seconds, and the table scans are killing the database. Need to bring it under 200 ms.</p>

<p><strong>Approach:</strong> understand the plan with <code>EXPLAIN ANALYZE</code>, then attack join order, indexes (especially covering ones), filter pushdown, and last-resort approaches like denormalization or pre-aggregated rollups.</p>

<pre><code>-- The slow query (illustrative)
SELECT o.id, c.name, p.title, pay.amount
FROM   orders o
JOIN   customers c ON c.id = o.customer_id
JOIN   order_items oi ON oi.order_id = o.id
JOIN   products p ON p.id = oi.product_id
JOIN   payments pay ON pay.order_id = o.id
WHERE  o.created_at &gt;= '2026-01-01'
  AND  o.status = 'completed'
  AND  p.category_id = 5;

-- Step 1: see what MySQL is actually doing
EXPLAIN ANALYZE SELECT ...;
-- Look for: rows examined, type=ALL (table scan), Using temporary, Using filesort

-- Step 2: ensure each join column has an index AND each filter is index-able
-- Composite index covering common access pattern:
ALTER TABLE orders ADD INDEX idx_status_created (status, created_at, customer_id, id);
-- Includes id at the end so it&rsquo;s a covering index for the join

ALTER TABLE order_items ADD INDEX idx_order_product (order_id, product_id);
ALTER TABLE products    ADD INDEX idx_category     (category_id);
ALTER TABLE payments    ADD INDEX idx_order        (order_id);

-- Step 3: rewrite to push filters into a derived table that limits rows EARLY
SELECT o.id, c.name, p.title, pay.amount
FROM   (
   SELECT id, customer_id
   FROM   orders
   WHERE  status = 'completed'
     AND  created_at &gt;= '2026-01-01'
   LIMIT  10000              -- if pagination, paginate at this layer
) o
JOIN customers c ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id AND p.category_id = 5
JOIN payments pay   ON pay.order_id = o.id;

-- Step 4: optimizer hints when the planner picks badly
SELECT /*+ JOIN_ORDER(o, c, oi, p, pay) INDEX(o idx_status_created) */
       ...
FROM   ...

-- Step 5: if still slow, materialize a daily rollup
CREATE TABLE order_summary_daily (
  day             DATE NOT NULL,
  category_id     INT NOT NULL,
  order_count     INT,
  total_amount    DECIMAL(14,2),
  PRIMARY KEY (day, category_id)
);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Technique</th><th>Win</th><th>Cost</th></tr></thead>
  <tbody>
    <tr><td>Covering composite indexes</td><td>Avoids reading the row; index-only scan</td><td>Index size; slower writes</td></tr>
    <tr><td>Filter-first derived tables</td><td>Smaller intermediate row sets</td><td>Query rewrite; less elegant</td></tr>
    <tr><td>Optimizer hints</td><td>Bypass planner mistakes</td><td>Brittle; breaks on data growth</td></tr>
    <tr><td>Denormalization (precomputed columns)</td><td>One-table query</td><td>Update on every change; staleness</td></tr>
    <tr><td>Pre-aggregated rollups</td><td>Sub-100 ms dashboards</td><td>Background job + late-arriving data</td></tr>
    <tr><td>Move to ClickHouse</td><td>Joins on billions of rows</td><td>Two systems</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the biggest wins are usually a <em>missing index</em> and a <em>filter that can&rsquo;t use the index</em> (<code>WHERE DATE(created_at) = '2026-01-01'</code> &mdash; the function call disables the index; rewrite to <code>created_at &gt;= '2026-01-01' AND created_at &lt; '2026-01-02'</code>). Use <strong>pt-query-digest</strong> on the slow log or <strong>sys.statement_analysis</strong> to find the worst queries. <strong>Percona PMM</strong> and <strong>Datadog DBM</strong> visualize plans over time. For genuinely complex analytics, push to <strong>ClickHouse</strong> (joins on billions of rows in seconds), <strong>Snowflake</strong>, <strong>BigQuery</strong>, or <strong>DuckDB</strong> via <strong>Debezium</strong> CDC; the OLTP database focuses on transactional reads. <strong>Materialize</strong> and <strong>RisingWave</strong> incrementally maintain materialized views &mdash; the join is computed once, then updated by deltas. The 2026 hierarchy: index correctly &rarr; rewrite query &rarr; cache (<strong>Redis</strong>) &rarr; rollup table &rarr; columnar store. Don&rsquo;t skip steps; an index fix is hours, a columnar migration is weeks.</p>
'''

ANSWERS[39] = r'''
<p><strong>Situation:</strong> the system stores logs, events, sessions, or user-generated content with regulatory or business retention windows &mdash; "delete logs older than 90 days", "purge inactive accounts after 3 years". GDPR, CCPA, and HIPAA add legal teeth. Manual cleanup doesn&rsquo;t scale.</p>

<p><strong>Approach:</strong> use partitioned tables for time-based data so deletion is O(1) (drop partition); use scheduled events or external cron + chunked deletes for non-partitioned data; document retention policy and audit deletions.</p>

<pre><code>-- Partition-based retention (best: deletion is metadata-only)
CREATE TABLE app_logs (
  id         BIGINT AUTO_INCREMENT,
  user_id    INT,
  level      VARCHAR(10),
  message    TEXT,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (id, created_at)                          -- partition key in PK
)
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p202601 VALUES LESS THAN (TO_DAYS('2026-02-01')),
  PARTITION p202602 VALUES LESS THAN (TO_DAYS('2026-03-01')),
  PARTITION p202603 VALUES LESS THAN (TO_DAYS('2026-04-01')),
  PARTITION pmax    VALUES LESS THAN MAXVALUE
);

-- Daily maintenance job: add next month, drop ones past retention (90 days)
ALTER TABLE app_logs ADD PARTITION (
  PARTITION p202605 VALUES LESS THAN (TO_DAYS('2026-06-01'))
);
ALTER TABLE app_logs DROP PARTITION p202601;            -- instant; no row-by-row work

-- Non-partitioned: chunked DELETE to avoid long locks
DELIMITER $$
CREATE EVENT IF NOT EXISTS purge_old_sessions
ON SCHEDULE EVERY 1 HOUR
DO BEGIN
  REPEAT
    DELETE FROM sessions
    WHERE  expires_at &lt; NOW() - INTERVAL 7 DAY
    LIMIT  1000;
  UNTIL ROW_COUNT() = 0 END REPEAT;
END$$
DELIMITER ;

-- GDPR right-to-be-forgotten: soft delete + scheduled hard delete
ALTER TABLE users ADD COLUMN deleted_at DATETIME NULL;

UPDATE users SET deleted_at = NOW(), email = CONCAT('deleted_', id, '@deleted'),
                 name = NULL, phone = NULL
WHERE  id = ?;

-- Hard delete after grace period (e.g., 30 days)
DELETE FROM users WHERE deleted_at &lt; NOW() - INTERVAL 30 DAY;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Method</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Partition drop</td><td>Instant; no replication lag</td><td>Requires partitioning by retention key from the start</td></tr>
    <tr><td>Chunked DELETE in event</td><td>Works on any table</td><td>Generates binlog volume; replica lag</td></tr>
    <tr><td>Soft delete + hard delete later</td><td>Mistake recoverable; satisfies GDPR grace</td><td>Two-phase complexity</td></tr>
    <tr><td>Archive to S3 / cold storage</td><td>Compliance + analytics later</td><td>Pipeline to maintain</td></tr>
    <tr><td>External tool (e.g., MaxScale data-archive filter)</td><td>Pluggable</td><td>Adds infra</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: write the retention policy in a document signed off by legal &mdash; "logs: 90 days; orders: 7 years; PII: erase within 30 days of account close". Implement it as code, not a manual checklist. <strong>MySQL Events</strong> are easy to forget about; consider running cron via <strong>Kubernetes CronJobs</strong>, <strong>AWS EventBridge</strong>, <strong>Airflow</strong>, or <strong>Temporal</strong> &mdash; visible to ops and observable. Archive purged data to <strong>S3</strong> in <strong>Parquet</strong> via <strong>AWS DMS</strong>, <strong>Datastream</strong>, or a custom job &mdash; queryable by <strong>Athena</strong> / <strong>Trino</strong> / <strong>DuckDB</strong> when auditors come knocking. For GDPR specifically: maintain an "erasure log" recording who was erased and when, and ensure backups don&rsquo;t resurrect them &mdash; this is harder than the live deletion. Compliance platforms (<strong>Vanta</strong>, <strong>Drata</strong>, <strong>OneTrust</strong>) check that you actually run the policy. Big lesson: the cheap part is deleting; the expensive part is proving you deleted on schedule and propagated to backups, replicas, and downstream systems (warehouse, search index, cache).</p>
'''

ANSWERS[40] = r'''
<p><strong>Situation:</strong> a SaaS or media company sells subscriptions &mdash; monthly, annual, with proration, cancellations, plan changes, failed payments, dunning &mdash; plus invoices, taxes, and receipts. The schema must reconcile with finance and survive payment-provider weirdness.</p>

<p><strong>Approach:</strong> model plans, subscriptions, invoices, and payments as separate concerns. Capture every state change as an immutable event. Most teams should use <strong>Stripe Billing</strong> / <strong>Chargebee</strong> / <strong>Recurly</strong> for the actual logic and just sync; rolling your own billing is the most regretted backend choice.</p>

<pre><code>CREATE TABLE plans (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  code       VARCHAR(50) NOT NULL UNIQUE,         -- 'pro_monthly_v3'
  name       VARCHAR(100),
  price      DECIMAL(10,2) NOT NULL,
  currency   CHAR(3) NOT NULL,
  interval_unit  ENUM('month','year') NOT NULL,
  interval_count INT NOT NULL DEFAULT 1,
  trial_days INT DEFAULT 0,
  active     BOOLEAN DEFAULT TRUE
);

CREATE TABLE subscriptions (
  id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id         INT NOT NULL,
  plan_id             INT NOT NULL,
  status              ENUM('trialing','active','past_due','canceled','paused') NOT NULL,
  current_period_start DATETIME NOT NULL,
  current_period_end   DATETIME NOT NULL,
  trial_end           DATETIME NULL,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  canceled_at         DATETIME NULL,
  external_id         VARCHAR(64),                 -- 'sub_1234' from Stripe
  created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_customer (customer_id, status),
  KEY idx_renewal  (status, current_period_end),
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (plan_id)     REFERENCES plans(id)
);

CREATE TABLE invoices (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  subscription_id BIGINT,
  customer_id     INT NOT NULL,
  number          VARCHAR(50) NOT NULL UNIQUE,     -- 'INV-2026-001234'
  status          ENUM('draft','open','paid','uncollectible','void') NOT NULL,
  subtotal        DECIMAL(12,2) NOT NULL,
  tax             DECIMAL(12,2) NOT NULL DEFAULT 0,
  total           DECIMAL(12,2) NOT NULL,
  currency        CHAR(3) NOT NULL,
  due_at          DATETIME NOT NULL,
  paid_at         DATETIME NULL,
  external_id     VARCHAR(64),
  KEY idx_customer (customer_id, status),
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE invoice_lines (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  invoice_id  BIGINT NOT NULL,
  description VARCHAR(255),
  quantity    INT NOT NULL DEFAULT 1,
  unit_amount DECIMAL(12,2) NOT NULL,
  amount      DECIMAL(12,2) NOT NULL,
  FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);

CREATE TABLE subscription_events (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  subscription_id BIGINT NOT NULL,
  event_type      VARCHAR(50) NOT NULL,           -- 'created','renewed','canceled','plan_changed'
  payload         JSON,
  created_at      DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_sub_created (subscription_id, created_at)
);

-- Renewal job: subscriptions due in next hour
SELECT id, customer_id, plan_id
FROM   subscriptions
WHERE  status = 'active'
  AND  current_period_end &lt; NOW() + INTERVAL 1 HOUR
  AND  cancel_at_period_end = FALSE;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Use Stripe Billing as source of truth</td><td>Tax, dunning, proration solved</td><td>Per-transaction fee; vendor lock</td></tr>
    <tr><td>Self-rolled with event log</td><td>Fully owned; cheap at scale</td><td>Edge cases multiply (proration, tax, refunds)</td></tr>
    <tr><td>Subscription-events table</td><td>Replay state; audit; rebuild</td><td>Dual write with subscription row</td></tr>
    <tr><td>Per-customer invoice numbering</td><td>Clean</td><td>Globally unique safer for accounting</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026 the right answer for almost everyone is <strong>Stripe Billing</strong> &mdash; or <strong>Chargebee</strong>, <strong>Recurly</strong>, <strong>Maxio</strong> (formerly Chargify), <strong>Paddle</strong> (handles VAT/MoR for digital goods), <strong>Lemon Squeezy</strong>, <strong>Orb</strong>, <strong>Metronome</strong>, <strong>m3ter</strong> for usage billing. They handle proration, dunning, tax (<strong>Stripe Tax</strong>, <strong>Avalara</strong>, <strong>TaxJar</strong>), and SCA/3DS. Mirror their state into your DB via webhooks &mdash; never reimplement the logic. Failed payments need dunning: retry with exponential backoff, send "update card" emails (<strong>Stripe Smart Retries</strong> does this automatically). For receipt PDFs, <strong>Stripe Hosted Invoices</strong> or libraries like <strong>react-pdf</strong>, <strong>Puppeteer</strong>. Keep finance happy with a daily reconciliation job comparing your <code>invoices</code>/<code>payments</code> tables to the Stripe Sigma export &mdash; mismatches indicate webhook drops or manual edits. Usage-based / metered billing is its own world: pre-aggregate events in <strong>ClickHouse</strong> or <strong>Druid</strong>, push usage records to Stripe / Orb / m3ter on a schedule. The schema above is right; the operational complexity is what kills home-grown billing systems.</p>
'''

ANSWERS[41] = r'''
<p><strong>Situation:</strong> a single MySQL table has billions of rows &mdash; orders history, events, logs &mdash; and queries scanning subsets are slow. Indexes help but the table itself is too big for efficient maintenance: ALTER takes hours, backups are huge, query planner stats lag.</p>

<p><strong>Approach:</strong> partition the table by a column that matches access patterns &mdash; almost always time. The optimizer can skip partitions that don&rsquo;t match the WHERE, and partition drops are O(1).</p>

<pre><code>-- RANGE partitioning by date (most common)
CREATE TABLE events (
  id         BIGINT AUTO_INCREMENT,
  user_id    INT NOT NULL,
  type       VARCHAR(50),
  payload    JSON,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (id, created_at)               -- partition key MUST be in every UNIQUE/PRIMARY KEY
)
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p202601 VALUES LESS THAN (TO_DAYS('2026-02-01')),
  PARTITION p202602 VALUES LESS THAN (TO_DAYS('2026-03-01')),
  PARTITION p202603 VALUES LESS THAN (TO_DAYS('2026-04-01')),
  PARTITION pmax    VALUES LESS THAN MAXVALUE
);

-- Verify partition pruning (optimizer skips irrelevant partitions)
EXPLAIN PARTITIONS
SELECT * FROM events
WHERE  created_at &gt;= '2026-03-01' AND created_at &lt; '2026-04-01';
-- partitions: p202603

-- HASH partitioning (even distribution, no time semantics)
CREATE TABLE user_logins (
  user_id    INT NOT NULL,
  login_at   DATETIME NOT NULL,
  PRIMARY KEY (user_id, login_at)
)
PARTITION BY HASH(user_id) PARTITIONS 16;

-- KEY partitioning (HASH using MySQL&rsquo;s internal function)
PARTITION BY KEY(user_id) PARTITIONS 16;

-- LIST partitioning (categorical)
CREATE TABLE orders_by_region (
  id INT, region CHAR(2), ...
  PRIMARY KEY (id, region)
)
PARTITION BY LIST COLUMNS(region) (
  PARTITION pna VALUES IN ('US','CA','MX'),
  PARTITION peu VALUES IN ('UK','DE','FR'),
  PARTITION pap VALUES IN ('JP','SG','AU')
);

-- Maintenance: monthly partition rotation
ALTER TABLE events ADD PARTITION (PARTITION p202607 VALUES LESS THAN (TO_DAYS('2026-08-01')));
ALTER TABLE events DROP PARTITION p202601;     -- instant 90-day-retention</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Strategy</th><th>Strength</th><th>Watch out for</th></tr></thead>
  <tbody>
    <tr><td>RANGE by date</td><td>Time-bounded queries prune perfectly; cheap drop</td><td>All hot data in one partition; uneven sizes</td></tr>
    <tr><td>HASH / KEY</td><td>Even row distribution</td><td>No pruning for range queries</td></tr>
    <tr><td>LIST</td><td>Categorical isolation</td><td>Manual mapping; new categories need ALTER</td></tr>
    <tr><td>Subpartitioning</td><td>Two-dimensional pruning (year + region)</td><td>Complex; few real wins</td></tr>
    <tr><td>Don&rsquo;t partition</td><td>Simplest</td><td>Maintenance pain at billions of rows</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: <em>partitioning is not sharding</em> &mdash; partitioned tables still live on one server. The cap is roughly the largest single host: tens of TB, ~500K QPS. Beyond that, sharding via <strong>Vitess</strong>, <strong>PlanetScale</strong>, or <strong>TiDB</strong> is the next step. The biggest mistake is partitioning without checking the optimizer actually prunes &mdash; <code>EXPLAIN PARTITIONS</code> in dev catches this. Constraint: every UNIQUE/PRIMARY KEY must include the partition key, which often means changing the PK design. Foreign keys are not supported on partitioned tables &mdash; enforce in app code or use triggers. Always keep a <code>pmax</code> catch-all so unexpected dates don&rsquo;t error out. Automate partition rotation via a scheduled event, <strong>pt-online-schema-change</strong>, or external cron &mdash; nothing kills a service at 3am like a missing partition. For analytics over partitioned data, consider streaming via <strong>Debezium</strong> to <strong>ClickHouse</strong> &mdash; columnar engines partition far more flexibly. <strong>Aurora MySQL</strong> and <strong>PlanetScale</strong> use storage-level mechanisms that make this less acute, but the partitioning concept still applies.</p>
'''

ANSWERS[42] = r'''
<p><strong>Situation:</strong> a job portal needs employers, jobs (with detailed requirements, location, salary), applicants (with resumes, skills, work history), applications (linking applicant to job), and search/filter that&rsquo;s fast over millions of listings.</p>

<p><strong>Approach:</strong> normalize core entities; M2M for skills; offload free-text and geo search to a search engine; track application state transitions.</p>

<pre><code>CREATE TABLE employers (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  company     VARCHAR(150) NOT NULL,
  industry    VARCHAR(80),
  website     VARCHAR(255),
  verified_at DATETIME NULL
);

CREATE TABLE applicants (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL UNIQUE,
  headline    VARCHAR(150),
  resume_url  VARCHAR(500),
  visibility  ENUM('public','recruiters','private') DEFAULT 'recruiters',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE jobs (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  employer_id   INT NOT NULL,
  title         VARCHAR(150) NOT NULL,
  description   TEXT,
  location      VARCHAR(150),
  remote        ENUM('onsite','hybrid','remote') NOT NULL DEFAULT 'onsite',
  salary_min    INT, salary_max INT, salary_currency CHAR(3),
  employment_type ENUM('full_time','part_time','contract','intern') NOT NULL,
  experience_level ENUM('entry','mid','senior','lead','exec') NOT NULL,
  status        ENUM('draft','open','closed','expired') DEFAULT 'open',
  posted_at     DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  expires_at    DATETIME NULL,
  KEY idx_status_posted (status, posted_at),
  KEY idx_employer       (employer_id, status),
  FOREIGN KEY (employer_id) REFERENCES employers(id),
  FULLTEXT idx_ft_title_desc (title, description)
);

CREATE TABLE skills (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE job_skills (
  job_id   INT NOT NULL,
  skill_id INT NOT NULL,
  required BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (job_id, skill_id),
  KEY idx_skill (skill_id, job_id),
  FOREIGN KEY (job_id)   REFERENCES jobs(id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skills(id)
);

CREATE TABLE applicant_skills (
  applicant_id INT NOT NULL,
  skill_id     INT NOT NULL,
  years        TINYINT,
  PRIMARY KEY (applicant_id, skill_id),
  FOREIGN KEY (applicant_id) REFERENCES applicants(id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skills(id)
);

CREATE TABLE applications (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  job_id       INT NOT NULL,
  applicant_id INT NOT NULL,
  status       ENUM('submitted','reviewed','interview','offer','hired','rejected','withdrawn') NOT NULL,
  cover_letter TEXT,
  applied_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_applicant_job (applicant_id, job_id),
  KEY idx_job_status   (job_id, status, applied_at),
  KEY idx_applicant    (applicant_id, applied_at),
  FOREIGN KEY (job_id) REFERENCES jobs(id),
  FOREIGN KEY (applicant_id) REFERENCES applicants(id)
);

-- "Find me Python jobs in Berlin paying &gt; 70K"
SELECT j.id, j.title, e.company, j.location, j.salary_min, j.salary_max
FROM   jobs j
JOIN   employers e ON e.id = j.employer_id
JOIN   job_skills js ON js.job_id = j.id
JOIN   skills s ON s.id = js.skill_id
WHERE  j.status = 'open'
  AND  s.name = 'Python'
  AND  j.location LIKE 'Berlin%'
  AND  j.salary_min &gt;= 70000
ORDER  BY j.posted_at DESC
LIMIT  20;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Skills as M2M (not free-text tags)</td><td>Canonical; index-friendly</td><td>Need taxonomy management</td></tr>
    <tr><td>UNIQUE(applicant_id, job_id)</td><td>Prevents duplicate applications</td><td>Must handle re-applies thoughtfully</td></tr>
    <tr><td>FULLTEXT in MySQL</td><td>Built-in, no extra infra</td><td>Limited ranking; no synonyms / typo tolerance</td></tr>
    <tr><td>Application status as ENUM</td><td>Simple state tracking</td><td>Adding states needs ALTER</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: free-text + geographic + faceted search across millions of jobs is a search-engine job, not a SQL job. <strong>Elasticsearch</strong> / <strong>OpenSearch</strong> dominate at scale; <strong>Meilisearch</strong>, <strong>Typesense</strong>, <strong>Algolia</strong> for managed/easier ops; <strong>Vespa</strong> for ranking-heavy use. Sync via <strong>Debezium</strong> CDC. Geographic search uses geohashing or vector tiles &mdash; ES native, or <strong>PostGIS</strong> on Postgres if you migrated. Resume parsing is its own market: <strong>Affinda</strong>, <strong>Sovren</strong>, <strong>HireAbility</strong>, or in-house with <strong>OpenAI</strong> / <strong>Anthropic</strong> APIs. Skill-matching has moved to embedding similarity in 2026: encode JD and resume with <strong>VoyageAI</strong> / <strong>Cohere</strong> / <strong>OpenAI</strong>, store in <strong>pgvector</strong> / <strong>Pinecone</strong> / <strong>Weaviate</strong>, score with kNN; this catches "Python developer" matching "Django engineer" without hand-curated synonyms. ATS workflows (interview scheduling, scorecards) are usually <strong>Greenhouse</strong>, <strong>Lever</strong>, <strong>Ashby</strong>, <strong>Workable</strong> &mdash; few teams build this from scratch successfully.</p>
'''

ANSWERS[43] = r'''
<p><strong>Situation:</strong> a content platform (Reddit/HN style) lets users upvote and downvote posts and comments; needs to display vote counts, "current user&rsquo;s vote", and rank by score. Vote integrity matters: one user, one vote per item.</p>

<p><strong>Approach:</strong> separate table for individual votes (with UNIQUE constraint), denormalized counter on the item for fast reads, and idempotent UPSERT for vote toggling.</p>

<pre><code>CREATE TABLE posts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(255),
  body        TEXT,
  author_id   INT NOT NULL,
  upvotes     INT NOT NULL DEFAULT 0,                -- denormalized
  downvotes   INT NOT NULL DEFAULT 0,                -- denormalized
  score       INT NOT NULL DEFAULT 0,                -- upvotes - downvotes (or hot algo)
  created_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_score_created (score DESC, created_at DESC),
  FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE TABLE post_votes (
  post_id  INT NOT NULL,
  user_id  INT NOT NULL,
  vote     TINYINT NOT NULL,                          -- +1 or -1
  voted_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (post_id, user_id),                     -- one vote per user per post
  KEY idx_user (user_id, voted_at),
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Cast / change a vote (idempotent)
START TRANSACTION;
  -- Get the current vote (NULL or +1/-1)
  SELECT vote INTO @old_vote FROM post_votes
  WHERE  post_id = ? AND user_id = ? FOR UPDATE;

  -- UPSERT new vote
  INSERT INTO post_votes (post_id, user_id, vote)
  VALUES (?, ?, ?)
  ON DUPLICATE KEY UPDATE vote = VALUES(vote), voted_at = CURRENT_TIMESTAMP(3);

  -- Update denormalized counters by delta
  UPDATE posts
  SET   upvotes   = upvotes
                  + IF(? = 1, 1, 0)
                  - IF(@old_vote = 1, 1, 0),
        downvotes = downvotes
                  + IF(? = -1, 1, 0)
                  - IF(@old_vote = -1, 1, 0),
        score     = upvotes - downvotes
  WHERE id = ?;
COMMIT;

-- Display a post with the current user&rsquo;s vote
SELECT p.id, p.title, p.score, COALESCE(pv.vote, 0) AS my_vote
FROM   posts p
LEFT   JOIN post_votes pv ON pv.post_id = p.id AND pv.user_id = ?
WHERE  p.id = ?;

-- "Hot" ranking (HN-style): score / (age + 2)^1.8
SELECT id, title, score,
       score / POW(TIMESTAMPDIFF(HOUR, created_at, NOW()) + 2, 1.8) AS hot
FROM   posts
ORDER  BY hot DESC
LIMIT  30;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Denormalized counters</td><td>Listing pages don&rsquo;t COUNT</td><td>Must update transactionally</td></tr>
    <tr><td>One row per vote</td><td>Audit; "shown my vote"; revoke</td><td>Storage at very high vote volume</td></tr>
    <tr><td>UNIQUE(post, user)</td><td>One vote per user enforced at DB</td><td>Idempotency requires UPSERT pattern</td></tr>
    <tr><td>Score = up - down</td><td>Simple</td><td>Doesn&rsquo;t reward agreement (Wilson, hot, controversial)</td></tr>
    <tr><td>Counter in Redis, sync to MySQL</td><td>Hot voting absorbed without DB pressure</td><td>Two systems consistency</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: at scale, the vote counter is a contention hotspot &mdash; many users hammering the same row. Solutions: (1) write votes to <strong>Redis</strong> (<code>HINCRBY post:1234 upvotes 1</code>), drain to MySQL every minute; (2) shard the counter into N rows summed at read; (3) use <strong>Aurora MySQL</strong> which handles single-row contention better. The ranking formula matters more than the schema &mdash; Reddit&rsquo;s "hot" weighs early votes heavily, "best" uses Wilson lower bound, "controversial" boosts items with both up and down. Compute on the fly for small feeds, materialize a <code>posts_ranked_hourly</code> table for large ones, or use <strong>ClickHouse</strong> for "top of all time" queries. Anti-fraud is essential: rate-limit votes per user, detect ring voting (graph cluster of accounts upvoting each other) via <strong>Neo4j</strong> or app logic. Show the user&rsquo;s vote without an extra query by joining or by storing in a session/cookie. Vote brigading and abuse tooling is harder than the schema.</p>
'''

ANSWERS[44] = r'''
<p><strong>Situation:</strong> the application opens a new MySQL connection per request; under load, connection establishment becomes the bottleneck (TLS handshake, auth, allocation). MySQL itself caps at <code>max_connections</code> (default 151), and exceeding it returns <code>Too many connections</code>.</p>

<p><strong>Approach:</strong> use a connection pool in the application, and put a connection multiplexer (<strong>ProxySQL</strong>, <strong>RDS Proxy</strong>) in front of MySQL when the app is multi-process or serverless.</p>

<pre><code>// Node.js: mysql2 with a pool
const mysql = require('mysql2/promise');
const pool  = mysql.createPool({
  host: 'db.internal',
  user: 'app',
  password: process.env.DB_PASS,
  database: 'shop',
  connectionLimit: 20,        // size per process
  queueLimit:      0,         // 0 = unlimited; reject above queue?
  waitForConnections: true,
  enableKeepAlive: true,
  keepAliveInitialDelay: 10000,
  idleTimeout: 60000,
});

// Use it
const [rows] = await pool.execute('SELECT * FROM products WHERE id = ?', [42]);

# Python (asyncpg-style for MySQL: aiomysql, sqlalchemy)
from sqlalchemy.ext.asyncio import create_async_engine
engine = create_async_engine(
    "mysql+aiomysql://app:secret@db/shop",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,         # recycle connections older than 30 min
    pool_pre_ping=True,        # validate before use; survives DB restarts
)

-- Server side: provision for concurrency
SET GLOBAL max_connections = 1000;
SET GLOBAL wait_timeout    = 600;     -- close idle after 10 min
SET GLOBAL interactive_timeout = 600;
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Threads_running';   -- the one that matters for load

-- ProxySQL: connection multiplexing (many app conns &harr; few backend conns)
INSERT INTO mysql_servers (hostgroup_id, hostname, port) VALUES (10, 'primary', 3306);
INSERT INTO mysql_users   (username, password, default_hostgroup) VALUES ('app','...',10);
LOAD MYSQL SERVERS TO RUNTIME;
LOAD MYSQL USERS   TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
SAVE MYSQL USERS   TO DISK;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Pool location</th><th>Strength</th><th>Weakness</th></tr></thead>
  <tbody>
    <tr><td>In-process pool (mysql2, HikariCP, SQLAlchemy)</td><td>Lowest latency; standard</td><td>One pool per process; serverless = N=cold</td></tr>
    <tr><td>External proxy (ProxySQL, MaxScale, RDS Proxy)</td><td>Pool shared across all app instances</td><td>Extra hop ~1-2 ms; another thing to operate</td></tr>
    <tr><td>Pgbouncer-style (Postgres analog)</td><td>Transaction-mode multiplexing</td><td>Limited prepared statement support</td></tr>
    <tr><td>Per-request connect (no pool)</td><td>Simple</td><td>Don&rsquo;t do this in production</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: pool sizing is empirical &mdash; total app connections (= pool size &times; instances) should not exceed <code>max_connections</code> minus headroom for admin sessions and replicas&rsquo; replication threads. Common starting point: <code>pool_size = (number_of_cores &times; 2) + spindles</code>; tune with monitoring. Connection-storm: when 1000 Lambdas each open 10 connections, the database melts &mdash; <strong>RDS Proxy</strong>, <strong>Aurora Data API</strong>, <strong>PlanetScale</strong>&rsquo;s native HTTP API, <strong>Neon</strong>&rsquo;s serverless driver, or <strong>Cloudflare Hyperdrive</strong> solve this for serverless. Always set <code>pool_recycle</code> &mdash; idle connections die from server-side <code>wait_timeout</code> or NAT/firewall idle drops; pre-ping prevents stale-conn errors. Watch <code>Threads_running</code>, not <code>Threads_connected</code> &mdash; running threads compete for CPU. <strong>ProxySQL</strong> additionally adds query routing (read &harr; write split), query caching, and rate limiting. <strong>Datadog DBM</strong>, <strong>PMM</strong>, <strong>SolarWinds DPA</strong> graph it. The 2026 default for Lambda-or-similar: managed proxy in front of managed MySQL; for VMs/k8s pods: in-process pool sized to a fraction of <code>max_connections</code>.</p>
'''

ANSWERS[45] = r'''
<p><strong>Situation:</strong> a fitness tracking app needs users, workouts (cardio, strength, classes), exercises within workouts (sets, reps, weight), goals, and progress over time. Reports show "weekly volume", "1RM trend", "consistency streak".</p>

<p><strong>Approach:</strong> normalize workouts and exercises with a junction table for the per-set records; treat workouts as time-series. Goals are a separate entity tracked via progress events.</p>

<pre><code>CREATE TABLE users (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  email        VARCHAR(255) NOT NULL UNIQUE,
  display_name VARCHAR(100),
  weight_kg    DECIMAL(5,2),
  height_cm    SMALLINT,
  birthdate    DATE,
  timezone     VARCHAR(50)
);

CREATE TABLE exercises (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL UNIQUE,            -- 'Back Squat'
  category      ENUM('strength','cardio','flexibility','sport') NOT NULL,
  primary_muscle VARCHAR(50),                              -- 'quads', 'chest'
  equipment     VARCHAR(50)                                -- 'barbell', 'bodyweight'
);

CREATE TABLE workouts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  name        VARCHAR(100),                                -- 'Push Day', 'Long Run'
  workout_type ENUM('strength','cardio','class','other') NOT NULL,
  started_at  DATETIME NOT NULL,
  ended_at    DATETIME NULL,
  notes       TEXT,
  KEY idx_user_started (user_id, started_at),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- One row per set (strength) or per interval (cardio)
CREATE TABLE workout_sets (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  workout_id   INT NOT NULL,
  exercise_id  INT NOT NULL,
  set_number   SMALLINT NOT NULL,
  reps         SMALLINT,
  weight_kg    DECIMAL(6,2),
  duration_s   INT,                                        -- cardio
  distance_m   INT,                                        -- cardio
  rpe          DECIMAL(3,1),                               -- rate of perceived exertion 1-10
  KEY idx_workout (workout_id, set_number),
  KEY idx_exercise_user (exercise_id, workout_id),         -- "all my squats"
  FOREIGN KEY (workout_id)  REFERENCES workouts(id) ON DELETE CASCADE,
  FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);

CREATE TABLE goals (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  goal_type   ENUM('weight','strength_1rm','distance_total','frequency_weekly') NOT NULL,
  target_value DECIMAL(10,2) NOT NULL,
  unit        VARCHAR(20),
  exercise_id INT NULL,                                     -- for 1RM goals
  start_date  DATE NOT NULL,
  target_date DATE NOT NULL,
  status      ENUM('active','achieved','abandoned') DEFAULT 'active',
  KEY idx_user_status (user_id, status),
  FOREIGN KEY (user_id)     REFERENCES users(id),
  FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);

-- Estimated 1RM trend for back squat (Epley formula: weight * (1 + reps/30))
SELECT DATE(w.started_at) AS day,
       MAX(ws.weight_kg * (1 + ws.reps / 30.0)) AS est_1rm
FROM   workout_sets ws
JOIN   workouts w ON w.id = ws.workout_id
JOIN   exercises e ON e.id = ws.exercise_id
WHERE  w.user_id = ? AND e.name = 'Back Squat'
  AND  w.started_at &gt;= NOW() - INTERVAL 6 MONTH
GROUP  BY DATE(w.started_at)
ORDER  BY day;

-- Workout streak: consecutive days with at least one workout
WITH days AS (
  SELECT DISTINCT DATE(started_at) AS d
  FROM workouts WHERE user_id = ?
), grp AS (
  SELECT d, DATE_SUB(d, INTERVAL ROW_NUMBER() OVER (ORDER BY d) DAY) AS g FROM days
)
SELECT MIN(d) AS streak_start, MAX(d) AS streak_end, COUNT(*) AS length
FROM grp GROUP BY g ORDER BY length DESC LIMIT 1;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Per-set rows</td><td>Granular analytics; PRs per exercise</td><td>High row count vs aggregated workouts</td></tr>
    <tr><td>Strength + cardio in one table</td><td>One workout query</td><td>Many NULL columns by type</td></tr>
    <tr><td>Goals separate from workouts</td><td>Multiple concurrent goals</td><td>Progress join</td></tr>
    <tr><td>Pre-computed weekly_summary</td><td>Fast dashboards</td><td>Background job</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: device sync &mdash; Apple Watch, Garmin, Fitbit, Whoop, Oura, Strava &mdash; goes through <strong>Apple HealthKit</strong>, <strong>Google Health Connect</strong>, <strong>Strava API</strong>, <strong>Garmin Connect</strong>, <strong>Terra API</strong>, or <strong>Vital</strong>; the schema above stores normalized output. GPS tracks for runs/rides are large &mdash; store as compressed GPX/FIT in S3, summary metrics (distance, pace, elevation) in MySQL. AI form coaching from video (<strong>Onform</strong>, <strong>HomeCourt</strong>, <strong>BurnLab</strong>) and AI-generated programs (<strong>Future</strong>, <strong>Fitbod</strong>, <strong>Centr</strong>) are 2026 differentiators &mdash; LLMs reading user history (<strong>OpenAI</strong>, <strong>Anthropic</strong>) generate next-week programs. Real-time leaderboards via <strong>Redis Sorted Sets</strong>. Wearable streams (heart rate during a workout) belong in <strong>InfluxDB</strong> / <strong>TimescaleDB</strong>; the per-set table is fine in MySQL even at billions of rows once partitioned. Subscription billing is its own layer (see Q40).</p>
'''

ANSWERS[46] = r'''
<p><strong>Situation:</strong> the application supports multiple languages &mdash; English, Spanish, Japanese, Arabic, Hindi &mdash; and content (product names, descriptions, UI strings, articles) needs translations. Translations may be partial (only popular languages get all content), and editors update them over time.</p>

<p><strong>Approach:</strong> separate the entity from its translatable fields via a translations table keyed by entity + locale. Always have a fallback locale. Translation memory and machine translation hooks accelerate coverage.</p>

<pre><code>-- Pattern 1: side-table (recommended)
CREATE TABLE products (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  sku          VARCHAR(50) NOT NULL UNIQUE,
  price        DECIMAL(10,2),
  category_id  INT,
  -- non-translatable canonical fields only
  KEY idx_category (category_id)
);

CREATE TABLE product_translations (
  product_id    INT NOT NULL,
  locale        VARCHAR(10) NOT NULL,            -- 'en', 'es-MX', 'ja', 'ar'
  name          VARCHAR(255) NOT NULL,
  description   TEXT,
  slug          VARCHAR(255),
  meta_title    VARCHAR(150),
  meta_desc     VARCHAR(300),
  translator    VARCHAR(50),                      -- 'human', 'mt:deepl', 'mt:gpt-4'
  reviewed_at   DATETIME NULL,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (product_id, locale),
  UNIQUE KEY uq_locale_slug (locale, slug),       -- locale-scoped slugs
  FULLTEXT idx_ft_name_desc (name, description),
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Display product in user&rsquo;s locale, fallback to 'en'
SELECT p.id, p.sku, p.price,
       COALESCE(pt.name, en.name) AS name,
       COALESCE(pt.description, en.description) AS description
FROM   products p
LEFT   JOIN product_translations pt ON pt.product_id = p.id AND pt.locale = ?
JOIN   product_translations en ON en.product_id = p.id AND en.locale = 'en'
WHERE  p.id = ?;

-- UI strings (gettext-style)
CREATE TABLE ui_strings (
  msg_key  VARCHAR(100) NOT NULL,                  -- 'checkout.button.pay'
  locale   VARCHAR(10)  NOT NULL,
  value    VARCHAR(500) NOT NULL,
  context  VARCHAR(100),                            -- helps translators disambiguate
  PRIMARY KEY (msg_key, locale)
);

-- Pattern 2: JSON columns (when locale count is small/stable)
ALTER TABLE products
  ADD COLUMN name_i18n JSON;
-- name_i18n: {"en":"Backpack","es":"Mochila","ja":"&#12496;&#12483;&#12463;&#12497;&#12483;&#12463;"}

SELECT JSON_EXTRACT(name_i18n, '$.es') AS name_es FROM products;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Approach</th><th>Strength</th><th>Weakness</th></tr></thead>
  <tbody>
    <tr><td>Side-table</td><td>Clean; new locale = INSERTs not ALTER; partial translations natural</td><td>JOIN on every read</td></tr>
    <tr><td>JSON column</td><td>Simple; single row</td><td>Index per-locale needs generated columns; harder to track per-locale review state</td></tr>
    <tr><td>Wide table (name_en, name_es, name_ja)</td><td>Direct access</td><td>ALTER for every new locale; sparse</td></tr>
    <tr><td>One row per locale (full duplicate)</td><td>Independent rows</td><td>Sync nightmare; non-translatable fields drift</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: a translation management system &mdash; <strong>Crowdin</strong>, <strong>Lokalise</strong>, <strong>Phrase</strong>, <strong>Tolgee</strong>, <strong>Localazy</strong>, or <strong>Smartling</strong> &mdash; handles the editor workflow, version control of strings, and integration with translators. Push canonical English &rarr; pull localized translations via API or webhooks. Machine translation as first pass: <strong>DeepL</strong> for European languages (best quality), <strong>Google Cloud Translate</strong>, <strong>Amazon Translate</strong>, or LLMs (<strong>GPT-4</strong>, <strong>Claude</strong>) for context-aware translation; mark MT&rsquo;d strings <code>reviewed_at IS NULL</code> so humans can polish. Right-to-left languages (Arabic, Hebrew) need UI direction flag and Unicode-clean fonts (<strong>Noto Sans</strong>). Locale isn&rsquo;t just language: <strong>ICU</strong>-formatted dates/numbers/currencies via <strong>Intl</strong> in JS or <strong>Babel</strong> in Python. SEO with locale subpaths (<code>/es/products/...</code>) and <code>hreflang</code> tags. The schema above is the foundation; the operational discipline is making sure every new field added to <code>products</code> gets a corresponding migration in <code>product_translations</code> &mdash; build it as a single workflow.</p>
'''

ANSWERS[47] = r'''
<p><strong>Situation:</strong> sensitive data &mdash; payment details, government IDs, health records, credentials, PII &mdash; lives in MySQL, and regulations (PCI DSS, HIPAA, GDPR) plus business risk demand encryption at rest, in transit, and ideally at the column level for the most sensitive fields.</p>

<p><strong>Approach:</strong> three layers &mdash; (1) TLS for connections (in-transit), (2) full-disk / tablespace encryption (at-rest), (3) column-level encryption for crown jewels with a separate KMS-managed key. Hash, don&rsquo;t encrypt, things like passwords.</p>

<pre><code>-- 1. Connections: require TLS
SET GLOBAL require_secure_transport = ON;
GRANT ALL ON shop.* TO 'app'@'%' REQUIRE SSL;

-- 2. At-rest: InnoDB tablespace encryption (transparent data encryption, TDE)
-- Configure keyring (e.g., keyring_file plugin or HashiCorp Vault via keyring_okv)
[mysqld]
early-plugin-load   = keyring_file.so
keyring_file_data   = /var/lib/mysql-keyring/keyring
default_table_encryption = ON

-- New encrypted table
CREATE TABLE customers (
  id        INT PRIMARY KEY AUTO_INCREMENT,
  email     VARCHAR(255),
  ssn_enc   VARBINARY(255)            -- column-level (see below)
) ENCRYPTION='Y';

-- Encrypt an existing table
ALTER TABLE orders ENCRYPTION='Y';

-- 3. Column-level (envelope encryption) for the highly sensitive
-- App encrypts before INSERT using a data key wrapped by KMS
INSERT INTO customers (email, ssn_enc)
VALUES (?, AES_ENCRYPT(?, @data_key, @iv));

-- Decrypt at read time (only when needed; show last 4 most of the time)
SELECT email, AES_DECRYPT(ssn_enc, @data_key, @iv) AS ssn FROM customers WHERE id = ?;

-- Better: app-side encryption with libsodium / AWS Encryption SDK / GCP KMS Tink
-- Server only sees ciphertext; key never enters MySQL.

-- 4. Passwords: HASH, never encrypt
INSERT INTO user_passwords (user_id, password_hash)
VALUES (?, ?);                         -- argon2id hash from app

-- 5. Searchable encryption: deterministic hash for lookup
ALTER TABLE customers ADD COLUMN email_lookup BINARY(32);
-- email_lookup = HMAC-SHA256(secret_key, lower(email))
SELECT * FROM customers WHERE email_lookup = ?;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Layer</th><th>Protects against</th><th>Doesn&rsquo;t protect against</th></tr></thead>
  <tbody>
    <tr><td>TLS in-transit</td><td>Network sniffing, MitM</td><td>Compromised app or DB</td></tr>
    <tr><td>InnoDB encryption (TDE)</td><td>Stolen disks/backups</td><td>SQL access; compromised DB user</td></tr>
    <tr><td>Column-level (DB-side)</td><td>Casual DBA browsing</td><td>App compromise (key in app)</td></tr>
    <tr><td>App-side envelope encryption</td><td>Compromised DB; rogue DBA</td><td>Compromised app</td></tr>
    <tr><td>Hash (passwords)</td><td>Database leak; rainbow tables</td><td>Weak passwords + brute force</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: managed services bake this in &mdash; <strong>Aurora</strong>, <strong>RDS</strong>, <strong>Cloud SQL</strong>, <strong>Azure DB for MySQL</strong>, <strong>PlanetScale</strong> all encrypt at-rest by default with cloud-provider-managed keys. Bring-your-own-key (BYOK) via <strong>AWS KMS</strong>, <strong>GCP KMS</strong>, <strong>Azure Key Vault</strong>, or <strong>HashiCorp Vault</strong> for compliance. The hardest column-level problem is searchability: encrypted ciphertext breaks <code>WHERE email = ?</code>. Solutions: deterministic hashing (above), <strong>blind indexing</strong>, or specialized formats like <strong>CipherStash</strong>, <strong>EvenVault</strong> that support encrypted equality and range queries. Tokenization for credit cards: <strong>Basis Theory</strong>, <strong>VGS</strong>, <strong>Skyflow</strong>, or PCI-compliant gateways (<strong>Stripe</strong>, <strong>Adyen</strong>) hold the real PAN; you store tokens. Rotate keys on a schedule (90 days for high-sensitivity), enforced by KMS. Audit access via <strong>MariaDB Audit Plugin</strong> or <strong>MySQL Enterprise Audit</strong>. The single biggest failure mode: encrypting at the database level then logging plaintext in application logs &mdash; review logging configs end-to-end, redact in <strong>Datadog</strong>, <strong>Splunk</strong>, <strong>Sentry</strong>.</p>
'''

ANSWERS[48] = r'''
<p><strong>Situation:</strong> the product team needs to run A/B tests &mdash; assigning users to variants, tracking conversion, calculating significance &mdash; plus feature flags for gradual rollouts and kill switches. Engineering wants a clean separation: which user sees which feature is decided by config, not code.</p>

<p><strong>Approach:</strong> three core entities &mdash; experiments, variant assignments, exposure events. Use a feature-flag service for gating; use the analytics warehouse for stats, not the OLTP DB.</p>

<pre><code>CREATE TABLE experiments (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  key_name     VARCHAR(80)  NOT NULL UNIQUE,        -- 'checkout_redesign_2026q2'
  hypothesis   TEXT,
  status       ENUM('draft','running','paused','completed') NOT NULL DEFAULT 'draft',
  traffic_pct  DECIMAL(5,2) NOT NULL DEFAULT 100,    -- % of users in experiment vs control
  primary_metric VARCHAR(80),                         -- 'orders_per_user'
  started_at   DATETIME NULL,
  ended_at     DATETIME NULL
);

CREATE TABLE experiment_variants (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  experiment_id INT NOT NULL,
  name          VARCHAR(50) NOT NULL,                 -- 'control', 'treatment_a'
  weight        DECIMAL(5,2) NOT NULL,                -- 50.00, 50.00 for 50/50 split
  config        JSON,                                  -- variant-specific params
  UNIQUE KEY uq_exp_variant (experiment_id, name),
  FOREIGN KEY (experiment_id) REFERENCES experiments(id)
);

-- Sticky assignment: user X always gets the same variant
CREATE TABLE experiment_assignments (
  experiment_id INT NOT NULL,
  user_id       INT NOT NULL,
  variant_id    INT NOT NULL,
  assigned_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (experiment_id, user_id),
  KEY idx_variant (experiment_id, variant_id),
  FOREIGN KEY (experiment_id) REFERENCES experiments(id),
  FOREIGN KEY (variant_id)    REFERENCES experiment_variants(id)
);

-- Exposure event: when the user actually saw the variant (vs just being assigned)
CREATE TABLE experiment_exposures (
  experiment_id INT NOT NULL,
  user_id       INT NOT NULL,
  variant_id    INT NOT NULL,
  exposed_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_exp_user (experiment_id, user_id),
  KEY idx_exp_time (experiment_id, exposed_at)
) PARTITION BY RANGE (TO_DAYS(exposed_at)) ( ... );

-- Feature flags (separate from experiments; on/off + rollout)
CREATE TABLE feature_flags (
  key_name    VARCHAR(80) PRIMARY KEY,
  enabled     BOOLEAN NOT NULL DEFAULT FALSE,
  rollout_pct DECIMAL(5,2) NOT NULL DEFAULT 0,        -- 0..100
  rules       JSON,                                    -- targeting rules
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Resolve variant for a user at request time
SELECT v.id, v.name, v.config
FROM   experiment_assignments a
JOIN   experiment_variants v ON v.id = a.variant_id
WHERE  a.experiment_id = ? AND a.user_id = ?;

-- If no assignment, hash the user_id into a bucket deterministically:
-- variant = variants_sorted[ HASH(user_id || experiment_key) % total_weight ]</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Sticky assignment in DB</td><td>Reproducible; auditable</td><td>Write per first-exposure user</td></tr>
    <tr><td>Hash-based assignment (no DB write)</td><td>Zero state; scales infinitely</td><td>Need stable user_id; no per-user override</td></tr>
    <tr><td>Exposures separate from assignments</td><td>"Intent to treat" vs actual view</td><td>Two tables to maintain</td></tr>
    <tr><td>Flags in MySQL</td><td>One source of truth</td><td>Flag eval per request hits DB; cache it</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the OLTP database stores assignments and config; the <em>statistics</em> happen in the warehouse. Stream <code>experiment_exposures</code> + conversion events to <strong>Snowflake</strong>, <strong>BigQuery</strong>, <strong>ClickHouse</strong>, or a dedicated <strong>Eppo</strong> / <strong>Statsig</strong> / <strong>GrowthBook</strong> / <strong>Optimizely</strong> / <strong>LaunchDarkly Experimentation</strong> backend that computes p-values, confidence intervals, sequential tests (CUPED variance reduction, Bayesian methods). Modern flag platforms &mdash; <strong>LaunchDarkly</strong>, <strong>Statsig</strong>, <strong>Unleash</strong>, <strong>Flagsmith</strong>, <strong>ConfigCat</strong>, <strong>PostHog</strong>, <strong>GrowthBook</strong> &mdash; cache flag state in their SDK so checks are sub-millisecond and don&rsquo;t hit the DB. They also handle targeting rules ("EU users with feature_x enabled who are in cohort Y"), gradual rollouts (5% &rarr; 25% &rarr; 100%), and kill switches. Don&rsquo;t reinvent these unless your scale or compliance demands it. Most-cited mistake: peeking at A/B results before reaching the planned sample size and calling significance &mdash; build sample-size guardrails into the workflow, or use sequential testing tools that handle this correctly.</p>
'''

ANSWERS[49] = r'''
<p><strong>Situation:</strong> a recommendation engine should suggest "products similar to this one" or "users you might like" based on user behavior &mdash; views, purchases, time spent, ratings &mdash; not just static categories.</p>

<p><strong>Approach:</strong> compute embeddings (vectors) representing each product/user from behavior data, store the embeddings, and serve nearest-neighbor lookups at query time. MySQL stores the metadata; a vector store handles the similarity.</p>

<pre><code>-- Source signals
CREATE TABLE user_events (
  user_id    INT NOT NULL,
  product_id INT NOT NULL,
  event_type ENUM('view','add_cart','purchase','rating') NOT NULL,
  rating     TINYINT NULL,                       -- 1-5 if rating event
  ts         DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_user_ts    (user_id, ts),
  KEY idx_product_ts (product_id, ts)
) PARTITION BY RANGE (TO_DAYS(ts)) ( ... );

-- Embeddings (vectors) computed by an ML pipeline; one row per product
CREATE TABLE product_embeddings (
  product_id INT PRIMARY KEY,
  embedding  BLOB,                                -- 768 floats packed; or use VECTOR (MySQL 9+)
  model      VARCHAR(50),                          -- 'item2vec_v3'
  computed_at DATETIME NOT NULL,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- For exact lookups: cached top-K precomputed
CREATE TABLE similar_products (
  product_id   INT NOT NULL,
  similar_id   INT NOT NULL,
  similarity   DECIMAL(6,4) NOT NULL,              -- cosine 0-1
  rank         SMALLINT NOT NULL,
  computed_at  DATETIME NOT NULL,
  PRIMARY KEY (product_id, rank),
  KEY idx_product_sim (product_id, similarity DESC)
);

-- Serve: top-10 similar products for product 42
SELECT p.id, p.name, p.image_url, sp.similarity
FROM   similar_products sp
JOIN   products p ON p.id = sp.similar_id
WHERE  sp.product_id = 42
ORDER  BY sp.rank
LIMIT  10;

-- Compute job (scheduled): item2vec / matrix factorization / neural retrieval
-- emits one row per (product, similar_product) pair to the table above

-- For real-time vector search (no precompute), call a vector DB
-- (Pinecone / Weaviate / Milvus / pgvector / Qdrant) from the app:
--   results = vector_db.query(embedding_of(product_42), top_k=10)
-- then JOIN MySQL for product metadata.</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Approach</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Precomputed top-K table</td><td>Sub-ms reads; simple SQL</td><td>Stale; expensive batch jobs</td></tr>
    <tr><td>Real-time vector store kNN</td><td>Always fresh; "users like you" dynamic</td><td>External system; cold start latency</td></tr>
    <tr><td>Co-occurrence "people also bought"</td><td>Easy from order_items</td><td>Sparse; doesn&rsquo;t generalize across users</td></tr>
    <tr><td>Content-based (categories, attributes)</td><td>No behavior data needed; cold start</td><td>Boring/obvious recs</td></tr>
    <tr><td>Hybrid (behavior + content embeddings)</td><td>Best quality</td><td>ML pipeline complexity</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026 the standard recipe is &mdash; encode products with a multimodal embedding (text + image) using <strong>OpenAI text-embedding-3</strong>, <strong>Cohere</strong>, <strong>VoyageAI</strong>, <strong>Sentence-Transformers</strong>, or vision-text models for images (<strong>CLIP</strong>, <strong>SigLIP</strong>); store vectors in <strong>Pinecone</strong>, <strong>Weaviate</strong>, <strong>Qdrant</strong>, <strong>Milvus</strong>, <strong>pgvector</strong>, <strong>Vespa</strong>, or <strong>MongoDB Atlas Vector Search</strong>; query with HNSW or IVF index for sub-50ms kNN over millions of items. <strong>MySQL 9</strong> introduced a VECTOR type but lacks a true ANN index &mdash; pair with a vector DB for now. Layer behavioral signals: <strong>matrix factorization</strong> (<strong>Spark ALS</strong>), <strong>two-tower neural retrieval</strong> (<strong>TensorFlow Recommenders</strong>, <strong>Vertex AI Matching Engine</strong>), or off-the-shelf <strong>AWS Personalize</strong>, <strong>Recombee</strong>, <strong>Algolia Recommend</strong>. Always rerank with a small model (LightGBM) using business signals (margin, in-stock, freshness). The hard part is feedback loops: log impressions and clicks back into training. A/B test recommender changes against revenue per session, not click-through rate alone &mdash; recommendations that get clicks but don&rsquo;t convert are anti-features.</p>
'''

ANSWERS[50] = r'''
<p><strong>Situation:</strong> a hotel reservation system needs hotels, rooms (with types), guests, bookings, availability, pricing (which varies by date), and prevention of double-booking under concurrent requests.</p>

<p><strong>Approach:</strong> separate room <em>types</em> from physical rooms; track availability via the bookings themselves (not a per-day table); use locking or atomic inserts to prevent double-booking; price comes from a date-keyed pricing table.</p>

<pre><code>CREATE TABLE hotels (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(150) NOT NULL,
  city        VARCHAR(100),
  country     CHAR(2),
  star_rating TINYINT,
  geo_lat     DECIMAL(9,6),
  geo_lng     DECIMAL(9,6),
  KEY idx_city (city),
  SPATIAL KEY idx_geo (POINT(geo_lat, geo_lng))
);

CREATE TABLE room_types (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  hotel_id    INT NOT NULL,
  name        VARCHAR(80),                          -- 'Deluxe King'
  capacity    TINYINT NOT NULL,
  amenities   JSON,
  KEY idx_hotel (hotel_id),
  FOREIGN KEY (hotel_id) REFERENCES hotels(id)
);

CREATE TABLE rooms (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  hotel_id     INT NOT NULL,
  room_type_id INT NOT NULL,
  room_number  VARCHAR(10),
  status       ENUM('available','maintenance','retired') DEFAULT 'available',
  UNIQUE KEY uq_hotel_room (hotel_id, room_number),
  FOREIGN KEY (hotel_id)     REFERENCES hotels(id),
  FOREIGN KEY (room_type_id) REFERENCES room_types(id)
);

CREATE TABLE bookings (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  hotel_id    INT NOT NULL,
  room_id     INT NULL,                             -- assigned at check-in or earlier
  room_type_id INT NOT NULL,
  guest_id    INT NOT NULL,
  check_in    DATE NOT NULL,
  check_out   DATE NOT NULL,                        -- exclusive
  status      ENUM('held','confirmed','checked_in','checked_out','cancelled','no_show') NOT NULL,
  total_price DECIMAL(10,2),
  currency    CHAR(3),
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_room_dates (room_id, check_in, check_out),
  KEY idx_hotel_dates (hotel_id, check_in, status),
  FOREIGN KEY (hotel_id)     REFERENCES hotels(id),
  FOREIGN KEY (room_id)      REFERENCES rooms(id),
  FOREIGN KEY (room_type_id) REFERENCES room_types(id),
  FOREIGN KEY (guest_id)     REFERENCES guests(id)
);

-- Pricing per date per room type
CREATE TABLE room_type_pricing (
  room_type_id INT NOT NULL,
  date         DATE NOT NULL,
  price        DECIMAL(10,2) NOT NULL,
  currency     CHAR(3) NOT NULL,
  available_count INT NOT NULL,                      -- rooms left of this type on this date
  PRIMARY KEY (room_type_id, date)
);

-- Find available rooms for a stay (room-type level)
SELECT rt.id, rt.name, SUM(rtp.price) AS total_price
FROM   room_type_pricing rtp
JOIN   room_types rt ON rt.id = rtp.room_type_id
WHERE  rt.hotel_id = ?
  AND  rtp.date &gt;= ? AND rtp.date &lt; ?            -- check_in to check_out
  AND  rtp.available_count &gt; 0
GROUP  BY rt.id
HAVING COUNT(*) = DATEDIFF(?, ?);                  -- all nights available

-- Atomic booking: reserve a specific room without double-booking
START TRANSACTION;
  -- Find a free room of the type; lock the row
  SELECT r.id INTO @room
  FROM   rooms r
  WHERE  r.hotel_id = ? AND r.room_type_id = ? AND r.status = 'available'
    AND  NOT EXISTS (
      SELECT 1 FROM bookings b
      WHERE  b.room_id = r.id
        AND  b.status IN ('held','confirmed','checked_in')
        AND  b.check_in &lt; ?      -- new check_out
        AND  b.check_out &gt; ?     -- new check_in
    )
  LIMIT 1
  FOR UPDATE SKIP LOCKED;

  INSERT INTO bookings (hotel_id, room_id, room_type_id, guest_id, check_in, check_out, status, total_price, currency)
  VALUES (?, @room, ?, ?, ?, ?, 'held', ?, ?);

  UPDATE room_type_pricing
  SET   available_count = available_count - 1
  WHERE room_type_id = ? AND date BETWEEN ? AND DATE_SUB(?, INTERVAL 1 DAY);
COMMIT;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Room types vs physical rooms</td><td>Sell at type level; assign at check-in</td><td>Two-level model</td></tr>
    <tr><td>Date-row pricing table</td><td>Yield management; easy availability</td><td>Lots of rows per room type</td></tr>
    <tr><td>SKIP LOCKED for picking a room</td><td>No deadlocks under load</td><td>MySQL 8.0+</td></tr>
    <tr><td>Range overlap check (NOT EXISTS)</td><td>Reliable double-book prevention</td><td>Index discipline required</td></tr>
    <tr><td>Held + confirmed states</td><td>Hold during checkout flow</td><td>Need timeout job to expire holds</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: real hotel ops integrate with channel managers (<strong>SiteMinder</strong>, <strong>Cloudbeds</strong>, <strong>RoomRaccoon</strong>) and OTAs (Booking.com, Expedia, Airbnb) via <strong>iCal</strong> sync or partner APIs &mdash; double-bookings across channels are the #1 risk. Yield management uses an algorithm or vendor (<strong>Duetto</strong>, <strong>IDeaS</strong>, <strong>Atomize</strong>) to set <code>price</code> dynamically based on demand, competitor pricing, day-of-week. Search at scale (geographic + filters + dates) needs <strong>Elasticsearch</strong> / <strong>OpenSearch</strong> with date availability indexed alongside hotel attributes &mdash; SQL won&rsquo;t serve "show me Paris hotels with pool, wi-fi, $150-300, July 4-7" fast across 100k+ hotels. Payment via <strong>Stripe</strong> / <strong>Adyen</strong>; PCI scope on the property side via tokenization. Cancellation policies as JSON rules tied to bookings. The toughest correctness problem isn&rsquo;t the schema &mdash; it&rsquo;s edge cases like overbooking strategy (intentional 5% over to absorb no-shows), group bookings, day-use rooms, and time-zone math when check-in is local.</p>
'''

ANSWERS[51] = r'''
<p><strong>Situation:</strong> a large dataset has both heavy reads (lists, dashboards, search) and heavy writes (logs, orders, events). Indexes that speed up reads slow down writes; getting the balance wrong kills throughput in one direction or the other.</p>

<p><strong>Approach:</strong> index for the hot read patterns, drop indexes that aren&rsquo;t actually used, prefer composite covering indexes for top queries, and isolate write-heavy paths with techniques like deferred indexing or insert buffering.</p>

<pre><code>-- Step 1: see which indexes are actually being used
SELECT index_name, count_read, count_write
FROM   performance_schema.table_io_waits_summary_by_index_usage
WHERE  object_schema = 'shop' AND object_name = 'orders'
ORDER  BY count_read DESC;

-- Step 2: composite index that COVERS the top read query
-- Query: WHERE status = ? AND customer_id = ? ORDER BY created_at DESC
ALTER TABLE orders
  ADD INDEX idx_status_customer_created (status, customer_id, created_at, id);
-- Including 'id' makes it a covering index for SELECT id, ...

-- Step 3: drop indexes that aren&rsquo;t used (reduces write cost)
ALTER TABLE orders DROP INDEX idx_unused_legacy;

-- Step 4: write-heavy table tuning
-- Insert in batches of 500-1000 rows
INSERT INTO events (user_id, type, payload, ts) VALUES
  (1,'view','...',NOW()), (2,'click','...',NOW()), ... ;

-- Reduce per-row overhead
SET autocommit = 0;
START TRANSACTION;
  -- 1000 inserts
COMMIT;

-- Defer index updates with the change buffer (InnoDB) for non-unique secondary indexes
-- Tune: innodb_change_buffer_max_size = 25 (default) for write-heavy workloads

-- Step 5: avoid filesort and temporary tables
-- Bad: ORDER BY a column not at the end of the chosen index
-- Good: index order matches the WHERE + ORDER BY of the query
EXPLAIN SELECT id FROM orders
WHERE  status = 'paid' AND customer_id = 42
ORDER  BY created_at DESC LIMIT 50;
-- Should show 'Using index' and NO 'Using filesort'

-- Step 6: for very write-heavy data (logs, events), consider partitioning + dropping
ALTER TABLE events PARTITION BY RANGE (TO_DAYS(ts)) ( ... );
-- Old partitions dropped daily &rarr; index size never grows unbounded</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Read win</th><th>Write cost</th></tr></thead>
  <tbody>
    <tr><td>Composite covering index</td><td>Index-only scan; very fast</td><td>Moderate; reasonable for hot query</td></tr>
    <tr><td>Many single-column indexes</td><td>Each one helps something</td><td>High; each INSERT/UPDATE writes all of them</td></tr>
    <tr><td>FULLTEXT index</td><td>Free-text search</td><td>Slow inserts on large tables</td></tr>
    <tr><td>Dropping unused indexes</td><td>None directly</td><td>Faster writes; smaller buffer pool</td></tr>
    <tr><td>Partitioning by date</td><td>Pruning</td><td>Constraints on UNIQUE keys</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the rule of thumb is to design indexes for the top 10-20 queries by frequency, not every possible query. Tools to identify them: <strong>pt-query-digest</strong> on the slow log, <strong>sys.statement_analysis</strong>, <strong>Datadog DBM</strong>, <strong>Percona PMM</strong>, <strong>SolarWinds DPA</strong>. <strong>EverSQL</strong>, <strong>pganalyze</strong> (Postgres) and <strong>SchemaHero</strong> can suggest index changes. <strong>MySQL 8</strong> functional indexes (<code>CREATE INDEX ... ON t ((LOWER(email)))</code>) and invisible indexes (test impact of dropping without actually dropping &mdash; <code>ALTER TABLE ... ALTER INDEX i INVISIBLE</code>) are powerful tuning aids. Hash indexes (memory storage engine) are useless for InnoDB. <strong>Aurora MySQL</strong>&rsquo;s "I/O optimized" mode and <strong>PlanetScale</strong>&rsquo;s Vitess split read/write workloads. The 2026 baseline workflow: enable slow log + Performance Schema, weekly review of top queries, EXPLAIN ANALYZE, add/remove indexes via online DDL, monitor write latency. Most apps add indexes liberally and never remove them &mdash; the audit usually finds 30-50% of indexes never read in production.</p>
'''

ANSWERS[52] = r'''
<p><strong>Situation:</strong> a crowdfunding platform (Kickstarter / Indiegogo / GoFundMe style) needs campaigns with funding goals, deadline, rewards/tiers, backers pledging amounts, payment processing, and accurate progress tracking under concurrent pledges.</p>

<p><strong>Approach:</strong> normalize campaigns, rewards, pledges; track payment status separately; use atomic counters for raised totals; trigger payouts only on successful campaigns at deadline.</p>

<pre><code>CREATE TABLE creators (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id   INT NOT NULL UNIQUE,
  verified  BOOLEAN DEFAULT FALSE,
  payout_account VARCHAR(255)                      -- Stripe Connect account ID
);

CREATE TABLE campaigns (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  creator_id  INT NOT NULL,
  title       VARCHAR(200) NOT NULL,
  description TEXT,
  goal_amount DECIMAL(12,2) NOT NULL,
  raised_amount DECIMAL(12,2) NOT NULL DEFAULT 0,    -- denormalized counter
  currency    CHAR(3) NOT NULL,
  funding_type ENUM('all_or_nothing','keep_what_you_raise') NOT NULL,
  status      ENUM('draft','active','successful','failed','cancelled') NOT NULL,
  starts_at   DATETIME NOT NULL,
  ends_at     DATETIME NOT NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_status_ends (status, ends_at),
  FOREIGN KEY (creator_id) REFERENCES creators(id)
);

CREATE TABLE rewards (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  campaign_id INT NOT NULL,
  title       VARCHAR(150) NOT NULL,
  description TEXT,
  pledge_min  DECIMAL(10,2) NOT NULL,
  quantity_limit INT NULL,                          -- NULL = unlimited
  quantity_claimed INT NOT NULL DEFAULT 0,
  ships_at    DATE NULL,
  KEY idx_campaign (campaign_id),
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE pledges (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  campaign_id     INT NOT NULL,
  reward_id       INT NULL,
  backer_id       INT NOT NULL,
  amount          DECIMAL(10,2) NOT NULL,
  currency        CHAR(3) NOT NULL,
  status          ENUM('authorized','captured','refunded','failed') NOT NULL,
  payment_method_token VARCHAR(255),                  -- e.g., Stripe pm_xxx
  charge_id       VARCHAR(255),                       -- e.g., Stripe ch_xxx
  pledged_at      DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  captured_at     DATETIME NULL,
  refunded_at     DATETIME NULL,
  KEY idx_campaign_status (campaign_id, status),
  KEY idx_backer (backer_id, pledged_at),
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
  FOREIGN KEY (reward_id)   REFERENCES rewards(id),
  FOREIGN KEY (backer_id)   REFERENCES users(id)
);

-- Place a pledge atomically (claim a reward + update campaign total)
START TRANSACTION;
  -- Lock the reward row to claim a slot
  SELECT quantity_limit, quantity_claimed
  INTO   @lim, @claimed
  FROM   rewards WHERE id = ? FOR UPDATE;

  IF @lim IS NOT NULL AND @claimed &gt;= @lim THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reward sold out';
  END IF;

  UPDATE rewards SET quantity_claimed = quantity_claimed + 1 WHERE id = ?;

  INSERT INTO pledges (campaign_id, reward_id, backer_id, amount, currency, status, payment_method_token)
  VALUES (?, ?, ?, ?, ?, 'authorized', ?);

  -- Authorized but not captured yet (charged at deadline)
  -- Don&rsquo;t increment raised_amount until campaign succeeds + payment captured
COMMIT;

-- Campaign success check (cron at deadline)
UPDATE campaigns SET status = 'successful'
WHERE  status = 'active' AND ends_at &lt; NOW()
  AND  funding_type = 'all_or_nothing' AND raised_amount &gt;= goal_amount;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Authorize at pledge, capture at deadline</td><td>All-or-nothing safe; refund if fails</td><td>Auths expire (Stripe = 7 days)</td></tr>
    <tr><td>Capture immediately</td><td>Money in escrow; simpler</td><td>Refund overhead if campaign fails</td></tr>
    <tr><td>Reward quantity in row + claimed counter</td><td>Atomic claim with lock</td><td>Hot row contention on popular rewards</td></tr>
    <tr><td>Denormalized raised_amount</td><td>Public progress bar fast</td><td>Update on every captured pledge</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the auth-then-capture flow needs a robust scheduler &mdash; <strong>Stripe</strong> auths expire after 7 days, so for long campaigns use <strong>Stripe SetupIntents</strong> + off-session charges at deadline, or charge-on-pledge with explicit refund policy. Use <strong>Stripe Connect</strong> (or <strong>Adyen for Platforms</strong>, <strong>Stripe Express accounts</strong>) to pay out to creators after success &mdash; you don&rsquo;t want to be a money services business. Compliance: KYC creators above thresholds via <strong>Stripe Identity</strong>, <strong>Persona</strong>, <strong>Onfido</strong>. Counter contention on hot campaigns: write to <strong>Redis</strong>, drain to MySQL every minute, or shard the counter row. Notifications via <strong>Customer.io</strong>, <strong>Knock</strong>, <strong>Courier</strong>. Search via <strong>Algolia</strong> / <strong>Meilisearch</strong>. Anti-fraud is significant: stolen-card pledges, friend-circle inflated funding &mdash; <strong>Stripe Radar</strong>, <strong>Sift</strong>, <strong>Persona</strong>, <strong>Sardine</strong> score risk. Customer trust comes from clear "campaign failed" refund timelines (3-5 business days) and reward fulfillment tracking after success.</p>
'''

ANSWERS[53] = r'''
<p><strong>Situation:</strong> the schema evolves over the lifetime of the application &mdash; new tables, columns, indexes, dropped columns, type changes, data backfills. Multiple developers, multiple environments (dev/staging/prod), and CI/CD all need consistent, reversible, idempotent migrations.</p>

<p><strong>Approach:</strong> migrations live in version control as numbered SQL files; a tool tracks which have been applied per environment via a metadata table; CI runs them automatically; rollbacks are documented but reverse-migration scripts are limited.</p>

<pre><code>-- Migration tooling tracks state in a metadata table
CREATE TABLE schema_migrations (
  version    VARCHAR(20) PRIMARY KEY,                 -- '20260415_120000'
  name       VARCHAR(255),
  applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  checksum   CHAR(64),                                 -- SHA-256 of file
  duration_ms INT
);

-- Convention: each migration is a numbered file
-- migrations/20260415_120000_add_orders_table.sql
CREATE TABLE orders (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_customer (customer_id)
);

-- migrations/20260420_140000_add_status_to_orders.sql
ALTER TABLE orders ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending', ALGORITHM=INSTANT;

-- Backfill migration (data, not schema) - separate from DDL
-- migrations/20260420_140100_backfill_existing_orders_to_completed.sql
UPDATE orders SET status = 'completed' WHERE created_at &lt; '2026-04-20' AND status = 'pending';

-- Migration runner pseudo-flow
function migrate():
  applied = SELECT version FROM schema_migrations
  for file in sorted(scan('migrations/')):
    if file.version not in applied:
      run(file.sql)
      INSERT INTO schema_migrations (version, name, checksum) VALUES (...)

-- Rollback (when feasible)
-- migrations/20260420_140000_DOWN.sql
ALTER TABLE orders DROP COLUMN status;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Approach</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Numbered SQL files + runner</td><td>Simple; version-controlled</td><td>No business-logic data backfills</td></tr>
    <tr><td>ORM-generated migrations (Prisma, Drizzle, Rails)</td><td>Schema-as-code; auto-diff</td><td>Generated SQL sometimes inefficient</td></tr>
    <tr><td>Atlas / Liquibase / Flyway</td><td>Cross-DB; community plugins</td><td>Extra tool to learn</td></tr>
    <tr><td>Branching DB (PlanetScale, Neon)</td><td>Schema branches like Git</td><td>Vendor-specific</td></tr>
    <tr><td>Down migrations</td><td>"Easy" rollback</td><td>Lossy in practice; data is hard to un-backfill</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the 2026 default tools are <strong>Atlas</strong> (Ariga, declarative + linter), <strong>Flyway</strong> (mature, JVM), <strong>Liquibase</strong> (XML/YAML, enterprise), <strong>Sqitch</strong> (deploy-tag-revert model). ORM-bundled: <strong>Prisma Migrate</strong>, <strong>Drizzle</strong>, <strong>TypeORM</strong>, <strong>Knex</strong> for Node; <strong>Alembic</strong> (SQLAlchemy), <strong>Django migrations</strong>, <strong>Rails</strong> for those ecosystems. <strong>PlanetScale</strong>&rsquo;s deploy-the-branch workflow is a paradigm shift &mdash; develop on a branch, request a deploy, gh-ost handles the schema change online. <strong>Atlas</strong> adds linting (catches destructive ops, missing indexes) and CI integration. The hardest principle to enforce: never make destructive changes without expand-contract (see Q36) &mdash; renaming a column in one migration breaks every running app instance during deploy. Code reviews should reject "rename column" or "drop column with reads" without expand-contract. Backfills are not migrations &mdash; they should be runnable jobs that handle large datasets in batches with progress tracking, separate from DDL. Always run migrations on a production-sized clone first. <strong>Bytebase</strong> and <strong>Schemachange</strong> add governance/approval flows for compliance environments.</p>
'''

ANSWERS[54] = r'''
<p><strong>Situation:</strong> a real-time chat app needs millions of messages per day, sub-second delivery, online presence, typing indicators, read receipts, and historical scroll-back. The DB must handle high write rates without becoming the bottleneck for delivery.</p>

<p><strong>Approach:</strong> MySQL stores the persistent message log and conversation metadata; real-time delivery, presence, and typing happen over WebSocket via a pub/sub layer (Redis, NATS) &mdash; the DB is not in the hot delivery path.</p>

<pre><code>-- Persistent storage (similar to Q30 but tuned for high-throughput chat)
CREATE TABLE conversations (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  type            ENUM('direct','group','channel') NOT NULL,
  last_message_id BIGINT NULL,                            -- denormalized
  last_message_at DATETIME(3),
  KEY idx_last (last_message_at)
);

CREATE TABLE conversation_members (
  conversation_id BIGINT NOT NULL,
  user_id         INT NOT NULL,
  joined_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_read_id    BIGINT NULL,                             -- O(1) unread = max - last_read
  PRIMARY KEY (conversation_id, user_id),
  KEY idx_user (user_id)
);

CREATE TABLE messages (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  conversation_id BIGINT NOT NULL,
  sender_id       INT NOT NULL,
  body            TEXT,
  client_id       VARCHAR(40),                              -- idempotency key from client
  created_at      DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  edited_at       DATETIME(3) NULL,
  deleted_at      DATETIME(3) NULL,
  UNIQUE KEY uq_client (sender_id, client_id),              -- de-dup retried sends
  KEY idx_conv_id (conversation_id, id)                      -- scroll-back uses id, not time
) PARTITION BY RANGE (TO_DAYS(created_at)) ( ... );

-- Reactions and read receipts as separate tables to avoid hot-row updates on messages
CREATE TABLE message_reactions (
  message_id BIGINT NOT NULL,
  user_id    INT NOT NULL,
  emoji      VARCHAR(20) NOT NULL,
  PRIMARY KEY (message_id, user_id, emoji)
);

-- Send flow:
-- 1) HTTP POST &rarr; INSERT INTO messages (atomic; UNIQUE on client_id de-dups)
-- 2) Update conversation.last_message_id
-- 3) Publish "new_message" to Redis: PUBLISH conv:{conversation_id} {payload}
-- 4) Each connected WebSocket subscribed to conv:{N} forwards to its client
START TRANSACTION;
  INSERT INTO messages (conversation_id, sender_id, body, client_id)
  VALUES (?, ?, ?, ?);
  SET @msg_id = LAST_INSERT_ID();
  UPDATE conversations SET last_message_id = @msg_id, last_message_at = NOW(3)
  WHERE id = ?;
COMMIT;
-- App: redis.publish(f"conv:{conv_id}", json)

-- Scroll-back: 50 messages older than message X
SELECT id, sender_id, body, created_at
FROM   messages
WHERE  conversation_id = ? AND id &lt; ?
ORDER  BY id DESC
LIMIT  50;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>MySQL for persistence + Redis pub/sub for delivery</td><td>DB not in hot path; real-time fan-out</td><td>Two systems to operate</td></tr>
    <tr><td>Partition by date</td><td>Old data archives cheaply</td><td>Cross-conversation queries scan all parts</td></tr>
    <tr><td>UNIQUE(sender, client_id)</td><td>Network retries don&rsquo;t double-send</td><td>Client must generate idempotency key</td></tr>
    <tr><td>Reactions in own table</td><td>No hot-row update on every reaction</td><td>JOIN on read</td></tr>
    <tr><td>Move to Cassandra at scale</td><td>10x writes; tuned for time-ordered</td><td>Operational complexity</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: the real-time layer in 2026 is one of &mdash; managed services like <strong>Pusher Channels</strong>, <strong>Ably</strong>, <strong>PubNub</strong>, <strong>Supabase Realtime</strong>; building blocks <strong>Socket.IO</strong> + Redis adapter, <strong>Phoenix Channels</strong> (Elixir), <strong>SignalR</strong> (.NET), <strong>Centrifugo</strong>; or chat-specific platforms <strong>Stream Chat</strong>, <strong>SendBird</strong>, <strong>CometChat</strong>, <strong>Twilio Conversations</strong>. Presence and typing live in <strong>Redis</strong> with TTLs (<code>SET presence:user:42 online EX 30</code>) &mdash; refreshed every 20s by the client. Push notifications via <strong>FCM</strong> / <strong>APNs</strong> for offline users. End-to-end encryption with <strong>libsignal</strong> (the protocol behind Signal/WhatsApp). At "Discord/Slack" scale, messages migrate from MySQL to <strong>Cassandra</strong>, <strong>ScyllaDB</strong>, or <strong>FoundationDB</strong> with conversation_id as partition key &mdash; write amplification stays bounded. AI moderation (toxicity, spam) via <strong>OpenAI Moderation</strong>, <strong>Perspective API</strong>, <strong>Hive</strong>. The schema above plus Redis pub/sub carries chat apps comfortably to hundreds of thousands of DAU; specialized stores enter beyond that.</p>
'''

ANSWERS[55] = r'''
<p><strong>Situation:</strong> the system uses multi-master replication &mdash; multiple writeable nodes accepting traffic in different regions or DCs &mdash; and conflicts are inevitable: two users update the same row from different masters at the same time. Without a strategy, data corrupts or rows oscillate.</p>

<p><strong>Approach:</strong> avoid multi-master where possible (single-primary with regional replicas is far simpler). When you can&rsquo;t avoid it, choose a conflict resolution strategy &mdash; last-write-wins, vector clocks, application-level reconciliation, or CRDT-style data types &mdash; and partition writes by ownership.</p>

<pre><code>-- Strategy 1: avoid multi-master (preferred)
-- Single primary with read replicas globally; writes proxy to primary
-- Aurora Global, PlanetScale, Vitess all support this with sub-second cross-region reads

-- Strategy 2: MySQL Group Replication (multi-primary mode)
-- Each commit is certified across the group; conflicts cause one transaction to abort
SET GLOBAL group_replication_single_primary_mode = OFF;     -- multi-primary
SET GLOBAL group_replication_enforce_update_everywhere_checks = ON;
START GROUP_REPLICATION;
-- Limitations: no foreign keys with cascading actions; SERIALIZABLE not supported

-- Strategy 3: partition writes by ownership (most production multi-master setups)
-- User X always writes to region X&rsquo;s primary; replicates async to other regions
-- WHERE region_id = '...' is the partition; conflicts impossible because only one writer

CREATE TABLE users (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  region_id CHAR(2) NOT NULL,                          -- 'us','eu','ap'
  email     VARCHAR(255) NOT NULL,
  -- ...
);
-- App routes: user.region_id == 'eu' &rarr; write to EU master

-- Strategy 4: last-write-wins by timestamp (lossy)
-- Add a "version" or "updated_at" column
ALTER TABLE products ADD COLUMN version BIGINT NOT NULL DEFAULT 0;
-- Replication conflict resolved by max(version) or max(updated_at)

-- Strategy 5: application-level reconciliation
-- Treat conflicts as exceptions; the application merges intelligently
-- e.g., shopping cart: union of items from both versions; counts: max</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Strategy</th><th>Strength</th><th>Weakness</th></tr></thead>
  <tbody>
    <tr><td>Single-master + global replicas</td><td>No conflicts; consistent</td><td>Cross-region write latency</td></tr>
    <tr><td>Group Replication multi-primary</td><td>Native MySQL; auto-conflict-detect</td><td>Network-sensitive; aborts under load</td></tr>
    <tr><td>Partition writes by ownership</td><td>Conflicts impossible by design</td><td>Hard cross-partition queries; data residency</td></tr>
    <tr><td>Last-write-wins</td><td>Simple; always converges</td><td>Silently overwrites concurrent edits</td></tr>
    <tr><td>App-level merge</td><td>Domain-aware; lossless</td><td>Per-table custom code</td></tr>
    <tr><td>CRDT data types</td><td>Mathematically conflict-free</td><td>Limited types; usually outside MySQL</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: 99% of teams that think they need multi-master actually need <em>multi-region with single primary plus read replicas</em>. <strong>Aurora Global Database</strong>, <strong>PlanetScale</strong>, <strong>Vitess</strong> with VReplication, <strong>YugabyteDB</strong>, <strong>CockroachDB</strong>, <strong>TiDB</strong>, <strong>Spanner</strong>-like Distributed SQL eliminate the problem with consensus protocols (Raft, Paxos). For genuine multi-master cases &mdash; offline-capable mobile apps syncing back, IoT edges &mdash; use a CRDT layer (<strong>Automerge</strong>, <strong>Yjs</strong>) or specialized DB (<strong>RethinkDB</strong>&rsquo;s former realtime, <strong>Couchbase Mobile</strong>, <strong>PouchDB</strong>+<strong>CouchDB</strong>); <strong>ElectricSQL</strong> brings CRDTs to Postgres-like SQL. Always log conflicts to a table or Sentry/Datadog &mdash; "no conflicts ever happened" usually means you&rsquo;re not detecting them. Run chaos tests: simulate cross-region partitions and verify convergence. The hardest part is auditing data accuracy after months of operation &mdash; build periodic diff jobs that compare primaries pairwise and alert on divergence. The 2026 reality: distributed SQL has matured enough that hand-rolling multi-master MySQL is a path most teams now skip.</p>
'''

ANSWERS[56] = r'''
<p><strong>Situation:</strong> an online marketplace (eBay, Etsy, Airbnb-style) needs buyers, sellers, listings, transactions, payments, escrow/holds, reviews, and dispute handling. Both sides of the marketplace need their own dashboards.</p>

<p><strong>Approach:</strong> separate user roles (buyer/seller often the same user); listings own by seller; transactions track the money flow with explicit state machine; reviews are post-transaction.</p>

<pre><code>CREATE TABLE users (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  email     VARCHAR(255) NOT NULL UNIQUE,
  is_seller BOOLEAN DEFAULT FALSE,
  is_buyer  BOOLEAN DEFAULT TRUE,
  payout_account VARCHAR(255)                        -- Stripe Connect / Adyen for Platforms
);

CREATE TABLE listings (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  seller_id   INT NOT NULL,
  title       VARCHAR(200) NOT NULL,
  description TEXT,
  price       DECIMAL(10,2) NOT NULL,
  currency    CHAR(3) NOT NULL,
  category_id INT,
  status      ENUM('draft','active','sold','removed','archived') NOT NULL DEFAULT 'draft',
  inventory   INT NOT NULL DEFAULT 1,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_seller_status (seller_id, status),
  KEY idx_status_created (status, created_at),
  FULLTEXT idx_ft (title, description),
  FOREIGN KEY (seller_id)   REFERENCES users(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE transactions (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  listing_id      INT NOT NULL,
  buyer_id        INT NOT NULL,
  seller_id       INT NOT NULL,
  quantity        INT NOT NULL DEFAULT 1,
  amount          DECIMAL(10,2) NOT NULL,
  fee_amount      DECIMAL(10,2) NOT NULL,                 -- platform commission
  currency        CHAR(3) NOT NULL,
  status          ENUM('pending','paid','shipped','delivered','disputed','refunded','released') NOT NULL,
  payment_intent_id VARCHAR(64),                          -- Stripe pi_xxx
  shipped_at      DATETIME NULL,
  delivered_at    DATETIME NULL,
  released_at     DATETIME NULL,                          -- funds released to seller
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_buyer_created  (buyer_id, created_at),
  KEY idx_seller_status  (seller_id, status, created_at),
  FOREIGN KEY (listing_id) REFERENCES listings(id),
  FOREIGN KEY (buyer_id)   REFERENCES users(id),
  FOREIGN KEY (seller_id)  REFERENCES users(id)
);

CREATE TABLE reviews (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  transaction_id INT NOT NULL UNIQUE,                     -- one review per transaction
  reviewer_id    INT NOT NULL,
  reviewee_id    INT NOT NULL,                            -- seller (buyer reviewing) or buyer (seller reviewing)
  rating         TINYINT NOT NULL,                        -- 1-5
  body           TEXT,
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_reviewee (reviewee_id, created_at),
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

CREATE TABLE disputes (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  transaction_id INT NOT NULL,
  raised_by      INT NOT NULL,
  reason         VARCHAR(50),
  description    TEXT,
  status         ENUM('open','under_review','buyer_won','seller_won','settled') NOT NULL,
  resolved_at    DATETIME NULL,
  KEY idx_transaction (transaction_id),
  FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

-- Atomic purchase
START TRANSACTION;
  -- Decrement inventory; only succeeds if available
  UPDATE listings SET inventory = inventory - 1
  WHERE  id = ? AND inventory &gt; 0;
  IF ROW_COUNT() = 0 THEN
    ROLLBACK; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Out of stock';
  END IF;

  INSERT INTO transactions (listing_id, buyer_id, seller_id, quantity, amount, fee_amount, currency, status)
  VALUES (?, ?, ?, 1, ?, ?, ?, 'pending');
COMMIT;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Combined buyer/seller in users</td><td>One profile; flexible</td><td>Authorization checks needed everywhere</td></tr>
    <tr><td>Inventory column on listing</td><td>Atomic decrement</td><td>Hot row for high-demand items</td></tr>
    <tr><td>Held funds + delayed release</td><td>Buyer protection</td><td>Capital locked; dispute window</td></tr>
    <tr><td>One review per transaction</td><td>Anti-spam</td><td>Repeat purchases? Special handling</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: marketplaces are <em>regulated</em> &mdash; you&rsquo;re a money services business in many jurisdictions. <strong>Stripe Connect</strong> (Express or Custom accounts), <strong>Adyen for Platforms</strong>, <strong>PayPal Marketplaces</strong>, <strong>Mangopay</strong> handle KYC, payouts, and split payments. Held funds + dispute window via <strong>Stripe Connect</strong> with <code>transfer_data</code> + delayed payouts. Search across millions of listings: <strong>Elasticsearch</strong> / <strong>OpenSearch</strong>, <strong>Algolia</strong>, <strong>Typesense</strong>, <strong>Meilisearch</strong>; faceted (price ranges, categories, location, rating). Recommendations via <strong>AWS Personalize</strong>, <strong>Recombee</strong>, embeddings (Q49). Trust &amp; safety is its own product: <strong>Sift</strong>, <strong>Sardine</strong>, <strong>Persona</strong>, <strong>Stripe Radar</strong> for fraud; <strong>Trustpilot</strong> integration; LLM-based listing moderation (<strong>OpenAI</strong> Moderation, <strong>Hive</strong>). Photos in S3 with <strong>imgix</strong>, <strong>Cloudinary</strong>, or <strong>Imgproxy</strong> for resizing. Analytics on user behavior (<strong>Amplitude</strong>, <strong>Mixpanel</strong>, <strong>PostHog</strong>) feeds back into recommendations. Tax handling differs by jurisdiction &mdash; <strong>Stripe Tax</strong>, <strong>TaxJar</strong>, <strong>Avalara</strong>; marketplaces in EU/India/Australia have specific marketplace tax obligations. The schema is the foundation; the value is in the trust, search, and payments operations layered on top.</p>
'''

ANSWERS[57] = r'''
<p><strong>Situation:</strong> the application generates large volumes of structured logs &mdash; HTTP requests, errors, business events, audit trail &mdash; and the team wants centralized storage, structured querying, retention, and dashboards. MySQL is being considered.</p>

<p><strong>Approach:</strong> MySQL is workable for low-volume audit-style logs but a poor fit for high-throughput application logs &mdash; use it for structured business events (orders, signups) and a purpose-built log store (Elasticsearch, ClickHouse, Loki) for everything else.</p>

<pre><code>-- Acceptable: low-volume, structured business events
CREATE TABLE app_events (
  id          BIGINT AUTO_INCREMENT,
  user_id     INT NULL,
  event_type  VARCHAR(50) NOT NULL,                   -- 'order.placed','user.signup'
  resource_id VARCHAR(64),
  level       ENUM('debug','info','warn','error') NOT NULL DEFAULT 'info',
  message     VARCHAR(500),
  metadata    JSON,                                    -- arbitrary structured data
  ip_address  VARBINARY(16),                            -- raw form (v4 or v6)
  user_agent  VARCHAR(500),
  trace_id    VARCHAR(64),
  ts          DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id, ts)
)
ENGINE=InnoDB
PARTITION BY RANGE (TO_DAYS(ts)) (
  PARTITION p202604 VALUES LESS THAN (TO_DAYS('2026-05-01')),
  PARTITION pmax    VALUES LESS THAN MAXVALUE
);

-- Indexes only for the queries you actually run
CREATE INDEX idx_user_ts        ON app_events (user_id, ts);
CREATE INDEX idx_event_type_ts  ON app_events (event_type, ts);
CREATE INDEX idx_trace_id       ON app_events (trace_id);

-- Insert: batched from app via async logger
INSERT INTO app_events (user_id, event_type, resource_id, level, message, metadata, ip_address, ts)
VALUES (?, 'order.placed', ?, 'info', 'Order placed', JSON_OBJECT('amount',99.50,'currency','USD'), INET6_ATON(?), NOW(3));

-- Drop old partitions (cheap retention)
ALTER TABLE app_events DROP PARTITION p202601;

-- For high-volume request logs, prefer ClickHouse / Loki / Elasticsearch
-- Schema example for ClickHouse table:
--   CREATE TABLE app_logs (ts DateTime, level String, msg String, ...) 
--   ENGINE = MergeTree PARTITION BY toYYYYMM(ts) ORDER BY (level, ts);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Store</th><th>Best for</th><th>Watch out for</th></tr></thead>
  <tbody>
    <tr><td>MySQL</td><td>Audit log; business events; ACID</td><td>Slow free-text; index bloat at high volume</td></tr>
    <tr><td>ClickHouse</td><td>Billions of events; aggregations</td><td>Eventual consistency; merge-aware schema</td></tr>
    <tr><td>Elasticsearch / OpenSearch</td><td>Full-text + filters; Kibana</td><td>Memory hungry; ops complexity</td></tr>
    <tr><td>Loki + Grafana</td><td>Log streams with labels; cheap</td><td>Limited query ability vs ES</td></tr>
    <tr><td>Datadog / Splunk / Honeycomb</td><td>SaaS; pre-built dashboards</td><td>$$$ at scale</td></tr>
    <tr><td>S3 + Athena</td><td>Cheap archive; SQL on demand</td><td>Slow for live troubleshooting</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026 the standard is structured JSON logs from the app via <strong>Pino</strong>, <strong>Winston</strong>, <strong>Bunyan</strong> (Node), <strong>structlog</strong> (Python), <strong>Zap</strong> (Go), <strong>Logback</strong> (JVM). Ship via <strong>Vector</strong>, <strong>Fluent Bit</strong>, <strong>Fluentd</strong>, or <strong>OpenTelemetry Collector</strong> to a backend. Backends: <strong>Datadog Logs</strong>, <strong>New Relic</strong>, <strong>Splunk</strong>, <strong>Honeycomb</strong>, <strong>Logz.io</strong>, <strong>Better Stack</strong>, <strong>Coralogix</strong>; self-hosted <strong>Elasticsearch + Kibana</strong> or <strong>Loki + Grafana</strong>; columnar option <strong>ClickHouse</strong> or <strong>Quickwit</strong>. Trace IDs from <strong>OpenTelemetry</strong> tie logs to traces (<strong>Jaeger</strong>, <strong>Tempo</strong>, <strong>Honeycomb</strong>). Audit logs (who did what, when, with what permissions) <em>do</em> belong in MySQL or a dedicated audit store with WORM (S3 Object Lock, <strong>AWS QLDB</strong>, <strong>Confluent Audit Log</strong>) for compliance. Don&rsquo;t mix high-volume request logs with business event audit; the access patterns and retention requirements are different. PII redaction is critical before logs leave the app &mdash; field-level redaction in the logger config; <strong>Datadog Sensitive Data Scanner</strong> as a backstop. Reserve MySQL for the events you&rsquo;ll actually JOIN with other business data.</p>
'''

ANSWERS[58] = r'''
<p><strong>Situation:</strong> an educational platform (Coursera/Udemy/edX style) needs courses with modules and lessons, instructors, students, enrollments, progress tracking, quizzes, certificates, and discussion threads.</p>

<p><strong>Approach:</strong> hierarchical content model (course &rarr; module &rarr; lesson), separate enrollment from progress, track per-lesson completion, quizzes as their own subsystem.</p>

<pre><code>CREATE TABLE instructors (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  bio     TEXT,
  payout_account VARCHAR(255),                        -- Stripe Connect for revenue share
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE courses (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  instructor_id INT NOT NULL,
  title         VARCHAR(200) NOT NULL,
  slug          VARCHAR(200) NOT NULL UNIQUE,
  description   TEXT,
  level         ENUM('beginner','intermediate','advanced') NOT NULL,
  language      VARCHAR(10) DEFAULT 'en',
  price         DECIMAL(10,2) NOT NULL,
  currency      CHAR(3) NOT NULL,
  status        ENUM('draft','published','archived') DEFAULT 'draft',
  published_at  DATETIME NULL,
  KEY idx_instructor_status (instructor_id, status),
  FOREIGN KEY (instructor_id) REFERENCES instructors(id)
);

CREATE TABLE modules (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  course_id INT NOT NULL,
  title     VARCHAR(200),
  position  SMALLINT NOT NULL,
  KEY idx_course_position (course_id, position),
  FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE lessons (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  module_id     INT NOT NULL,
  title         VARCHAR(200),
  content_type  ENUM('video','text','quiz','assignment') NOT NULL,
  content_url   VARCHAR(500),                           -- Mux/Vimeo/YouTube/Brightcove
  duration_s    INT,
  position      SMALLINT NOT NULL,
  KEY idx_module_position (module_id, position),
  FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
);

CREATE TABLE enrollments (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  course_id     INT NOT NULL,
  student_id    INT NOT NULL,
  enrolled_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at  DATETIME NULL,
  certificate_id VARCHAR(64) NULL,
  UNIQUE KEY uq_course_student (course_id, student_id),
  KEY idx_student (student_id, enrolled_at),
  FOREIGN KEY (course_id)  REFERENCES courses(id),
  FOREIGN KEY (student_id) REFERENCES users(id)
);

CREATE TABLE lesson_progress (
  enrollment_id  INT NOT NULL,
  lesson_id      INT NOT NULL,
  status         ENUM('not_started','in_progress','completed') NOT NULL DEFAULT 'not_started',
  position_s     INT DEFAULT 0,                          -- video resume point
  completed_at   DATETIME NULL,
  PRIMARY KEY (enrollment_id, lesson_id),
  FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
  FOREIGN KEY (lesson_id)     REFERENCES lessons(id)
);

CREATE TABLE quizzes (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  lesson_id INT NOT NULL,
  pass_pct  TINYINT NOT NULL DEFAULT 70,
  FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);

CREATE TABLE quiz_questions (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  quiz_id   INT NOT NULL,
  prompt    TEXT,
  options   JSON,                                        -- [{id:'a',text:'...'},...]
  answer_key JSON,                                       -- ['a','c'] for multi-correct
  KEY idx_quiz (quiz_id),
  FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

CREATE TABLE quiz_attempts (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  quiz_id       INT NOT NULL,
  student_id    INT NOT NULL,
  score_pct     DECIMAL(5,2),
  passed        BOOLEAN,
  responses     JSON,
  attempted_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Course progress for a student
SELECT
  COUNT(lp.lesson_id) AS started,
  SUM(lp.status = 'completed') AS completed,
  COUNT(l.id) AS total
FROM   lessons l
JOIN   modules m ON m.id = l.module_id
LEFT   JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.enrollment_id = ?
WHERE  m.course_id = ?;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Course &gt; module &gt; lesson</td><td>Mirrors UX; clear permissions</td><td>3-table walk for full structure</td></tr>
    <tr><td>Per-lesson progress row</td><td>Granular; resume video</td><td>Many rows per enrollment</td></tr>
    <tr><td>UNIQUE(course, student)</td><td>Prevents double-enroll</td><td>Reset/re-enroll = special case</td></tr>
    <tr><td>Quiz responses as JSON</td><td>Schema-flexible</td><td>Harder to aggregate stats</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: video is the costliest piece &mdash; <strong>Mux</strong>, <strong>Vimeo OTT</strong>, <strong>JW Player</strong>, <strong>Brightcove</strong>, <strong>Bunny Stream</strong>, or self-hosted <strong>HLS</strong> via <strong>FFmpeg</strong> + <strong>CloudFront</strong>; signed URLs prevent unauthorized embeds. Captions (auto via <strong>AssemblyAI</strong>, <strong>Rev.ai</strong>, <strong>OpenAI Whisper</strong>) are accessibility table stakes. Certificate generation: <strong>react-pdf</strong>, <strong>Puppeteer</strong>, <strong>Accredible</strong>, <strong>Sertifier</strong>, <strong>Credly</strong> &mdash; verify via blockchain or signed URL. Live courses: <strong>Zoom</strong> / <strong>Whereby</strong> / <strong>100ms</strong> / <strong>LiveKit</strong>. AI-generated summaries, "ask the course" Q&amp;A via <strong>RAG</strong> over course transcripts using <strong>OpenAI</strong> / <strong>Anthropic</strong> + a vector store (<strong>Pinecone</strong>, <strong>Weaviate</strong>, <strong>pgvector</strong>) is now standard on platforms like Coursera, Udacity, MasterClass. Discussion forums: <strong>Discourse</strong>, <strong>Circle</strong>, <strong>Discord</strong>, or built-in. Payments + revenue share via <strong>Stripe Connect</strong>. Anti-cheating in quizzes: shuffle questions, time-limit, proctor with <strong>Honorlock</strong>, <strong>ProctorU</strong>. The 2026 differentiator is adaptive learning: track which questions a student misses, recommend remediation lessons, generate practice questions with LLMs.</p>
'''

ANSWERS[59] = r'''
<p><strong>Situation:</strong> the database has duplicate records &mdash; same customer entered twice with slight variations, repeated event ingestion from a flaky producer, two import jobs creating the same row. Need to identify, merge, and prevent recurrence.</p>

<p><strong>Approach:</strong> add a UNIQUE constraint on the natural key going forward; deduplicate existing data with a query that ranks duplicates and keeps the canonical row; for fuzzy duplicates (typos, casing), use normalization or external matching.</p>

<pre><code>-- Step 1: prevent future duplicates with UNIQUE constraint (after cleanup!)
ALTER TABLE customers ADD UNIQUE KEY uq_email (email);  -- will fail if dupes exist

-- Step 2: find exact-match duplicates
SELECT email, COUNT(*) c
FROM   customers
GROUP  BY email
HAVING c &gt; 1;

-- Step 3: keep the oldest (or most-recent, or most-complete) and delete the rest
WITH ranked AS (
  SELECT id, email,
         ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at) AS rn
  FROM   customers
)
DELETE c FROM customers c
JOIN   ranked r ON c.id = r.id
WHERE  r.rn &gt; 1;

-- Step 4: re-attach foreign keys before deleting (the canonical merge)
-- If you delete a duplicate user, all their orders should point to the canonical user
UPDATE orders o
JOIN   ranked r ON o.customer_id = r.id
JOIN   ranked canonical ON canonical.email = r.email AND canonical.rn = 1
SET    o.customer_id = canonical.id
WHERE  r.rn &gt; 1;

-- Step 5: fuzzy duplicates &mdash; normalize first
ALTER TABLE customers ADD COLUMN email_normalized VARCHAR(255)
  GENERATED ALWAYS AS (LOWER(TRIM(email))) STORED;
ALTER TABLE customers ADD INDEX idx_email_norm (email_normalized);

-- Find near-duplicates by Levenshtein-like distance (use SOUNDEX, NGRAM, or app-level)
SELECT a.id, a.email, b.id, b.email
FROM   customers a JOIN customers b
  ON   a.id &lt; b.id
  AND  SOUNDEX(a.last_name) = SOUNDEX(b.last_name)
  AND  LEVENSHTEIN(a.email, b.email) &lt;= 2;             -- requires UDF or app code

-- Step 6: idempotency for ingest pipelines (prevent duplicates at write time)
CREATE TABLE events (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  external_id   VARCHAR(64) NOT NULL UNIQUE,            -- producer-supplied
  data          JSON,
  ts            DATETIME NOT NULL
);
INSERT INTO events (external_id, data, ts)
VALUES (?, ?, ?)
ON DUPLICATE KEY UPDATE id = id;                        -- no-op; idempotent</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Approach</th><th>Strength</th><th>Weakness</th></tr></thead>
  <tbody>
    <tr><td>UNIQUE constraint</td><td>Hard prevention; DB-enforced</td><td>Requires cleanup before adding</td></tr>
    <tr><td>Idempotency keys (external_id UNIQUE)</td><td>Producer retries safe</td><td>Requires producer cooperation</td></tr>
    <tr><td>Generated normalized column</td><td>Catches casing/whitespace</td><td>Doesn&rsquo;t catch typos</td></tr>
    <tr><td>Fuzzy matching (app)</td><td>Catches "John Smith" vs "Jon Smith"</td><td>False positives; manual review</td></tr>
    <tr><td>External MDM tool</td><td>Enterprise-grade matching</td><td>$$$; integration work</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: prevention is far cheaper than cleanup. Every ingest endpoint should require an idempotency key (<strong>Stripe</strong>-style <code>Idempotency-Key</code> header), enforced via UNIQUE constraint &mdash; this single discipline eliminates 80% of duplicate problems. Email normalization should account for plus addressing (<code>user+tag@gmail.com</code> = <code>user@gmail.com</code> in some interpretations &mdash; debatable; document the policy). For names/addresses, fuzzy matching libraries: <strong>fuzzywuzzy</strong>/<strong>RapidFuzz</strong> (Python), <strong>fuse.js</strong> (JS), <strong>libpostal</strong> (addresses), <strong>recordlinkage</strong> (Python). Specialized MDM platforms: <strong>Tilores</strong>, <strong>Dedupe.io</strong>, <strong>Talend Data Stewardship</strong>, <strong>Informatica MDM</strong>. CRM-specific: <strong>Salesforce Duplicate Management</strong>, <strong>HubSpot</strong> dedupe. For B2B: <strong>Clearbit</strong>, <strong>ZoomInfo</strong> enrich+match against canonical company records. Always log the merge action with both record IDs and a "merged_into" reference so you can unwind mistakes &mdash; deletes are forever, but a soft-delete flag plus a foreign-key remap is reversible. Audit periodically: a daily job counting (email, count(*)) groups with count &gt; 1 should always return zero on a healthy table.</p>
'''

ANSWERS[60] = r'''
<p><strong>Situation:</strong> the application supports user profiles where users (or admins) can add custom fields beyond the standard ones &mdash; preferred pronouns, third-party IDs, hobbies, employment, custom HR attributes for B2B. Schema can&rsquo;t change every time someone wants a new field.</p>

<p><strong>Approach:</strong> three patterns &mdash; (1) JSON column for arbitrary fields, (2) entity-attribute-value (EAV) tables, (3) wide table with reserved custom columns. JSON is the modern default; EAV for tenant-specific schemas; wide table almost never.</p>

<pre><code>-- Pattern 1: JSON column (recommended default)
CREATE TABLE users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  email         VARCHAR(255) NOT NULL UNIQUE,
  display_name  VARCHAR(100),
  custom        JSON,                                   -- {pronouns:'they/them', github:'octocat', ...}
  custom_norm   VARCHAR(255) AS (custom-&gt;&gt;'$.github') STORED,  -- index a hot path
  KEY idx_github (custom_norm),
  CHECK (JSON_VALID(custom))
);

INSERT INTO users (email, display_name, custom) VALUES
  ('a@b.com', 'Alex', JSON_OBJECT('pronouns','they/them','github','alexdev','timezone','Europe/Berlin'));

-- Query JSON fields
SELECT id, custom-&gt;&gt;'$.github' AS github
FROM   users
WHERE  custom-&gt;&gt;'$.timezone' = 'Europe/Berlin';

-- Index a specific JSON field for fast lookup (generated column above)
SELECT id FROM users WHERE custom_norm = 'octocat';

-- Update one field within JSON (atomic)
UPDATE users
SET    custom = JSON_SET(custom, '$.timezone', 'America/New_York')
WHERE  id = 42;

-- Pattern 2: EAV (entity-attribute-value) for tenant-defined fields
CREATE TABLE custom_field_definitions (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  tenant_id   INT NOT NULL,
  entity      VARCHAR(50) NOT NULL,                     -- 'user'
  key_name    VARCHAR(50) NOT NULL,
  data_type   ENUM('string','number','date','boolean','select') NOT NULL,
  options     JSON,                                      -- for select-type
  required    BOOLEAN DEFAULT FALSE,
  UNIQUE KEY uq_tenant_entity_key (tenant_id, entity, key_name)
);

CREATE TABLE custom_field_values (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  field_id      INT NOT NULL,
  entity_id     INT NOT NULL,                           -- user.id
  value_text    VARCHAR(500),
  value_number  DECIMAL(15,4),
  value_date    DATETIME,
  value_bool    BOOLEAN,
  KEY idx_field_entity (field_id, entity_id),
  KEY idx_entity (entity_id),
  FOREIGN KEY (field_id) REFERENCES custom_field_definitions(id)
);

-- Pattern 3: wide table with reserved columns (avoid; here for completeness)
CREATE TABLE users_wide (
  id INT,
  custom1_label VARCHAR(50), custom1_value VARCHAR(500),
  custom2_label VARCHAR(50), custom2_value VARCHAR(500),
  -- ... up to N reserved slots
);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Pattern</th><th>Strength</th><th>Weakness</th></tr></thead>
  <tbody>
    <tr><td>JSON column</td><td>Flexible; natural for app code; indexable via generated cols</td><td>Type-unsafe; harder reporting</td></tr>
    <tr><td>EAV</td><td>Per-tenant schema; queryable</td><td>Verbose; many JOINs; type sprawl</td></tr>
    <tr><td>Wide reserved columns</td><td>Trivial schema</td><td>Capped; sparse; ugly reports</td></tr>
    <tr><td>Side table per type</td><td>Type-safe per attribute</td><td>Schema explosion</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026 the JSON path is the practical winner for most apps &mdash; modern JS/TS tooling (<strong>Zod</strong>, <strong>Valibot</strong>, <strong>io-ts</strong>) and Python (<strong>Pydantic</strong>) validate schemas at the application boundary, and MySQL 8&rsquo;s JSON functions plus generated columns get you indexed reads on hot fields. Migrate to a real column when a JSON field becomes universally used, indexed, and reported on. For SaaS B2B with tenant-defined fields (HRIS, CRM), EAV is unavoidable &mdash; <strong>Salesforce</strong>, <strong>Airtable</strong>, <strong>Notion</strong> all use EAV variants &mdash; but use a serializer/validator layer to fake type safety in the app. Materialize tenant-specific reporting views nightly to avoid EAV pivots at query time. <strong>Postgres</strong> does this better with native <code>jsonb</code> + GIN indexes; consider it if profile flexibility is the core product. Document-databases (<strong>MongoDB</strong>, <strong>Couchbase</strong>) are sometimes a better fit and modern CRMs use them &mdash; but operational MySQL knowledge usually wins. Final caution: GDPR right-to-erase is harder when "I don&rsquo;t know everywhere this user&rsquo;s name lives" &mdash; map sensitive fields explicitly even when they&rsquo;re inside JSON.</p>
'''

ANSWERS[61] = r'''
<p><strong>Situation:</strong> users want to filter and search results by multiple criteria simultaneously &mdash; e.g., "shoes in size 10, under $80, brand Nike, free shipping, in stock, rated 4+". Each combination of filters needs to be fast across millions of rows.</p>

<p><strong>Approach:</strong> for combinatorial filtering across many independent fields, dedicated search engines (Elasticsearch, Meilisearch, Typesense) outperform SQL dramatically. SQL works for low-cardinality filter sets with carefully designed composite indexes.</p>

<pre><code>-- SQL approach: composite index supporting common filter combos
CREATE TABLE products (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  brand_id    INT NOT NULL,
  category_id INT NOT NULL,
  price       DECIMAL(10,2) NOT NULL,
  rating_avg  DECIMAL(3,2),
  rating_count INT,
  in_stock    BOOLEAN NOT NULL,
  free_ship   BOOLEAN NOT NULL,
  attributes  JSON,                                     -- {color:'red', size:10}
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_cat_brand_price (category_id, brand_id, price),
  KEY idx_cat_rating      (category_id, rating_avg DESC),
  KEY idx_cat_created     (category_id, created_at DESC),
  FULLTEXT idx_ft (name, description)
);

-- Filter query (works fine for moderate result sets)
SELECT id, name, price, rating_avg
FROM   products
WHERE  category_id = 5 AND brand_id IN (10, 22)
  AND  price BETWEEN 0 AND 80 AND rating_avg &gt;= 4
  AND  in_stock = TRUE AND free_ship = TRUE
ORDER  BY rating_avg DESC LIMIT 20;

-- Faceted counts: how many products per brand within current filter set
SELECT brand_id, COUNT(*) AS c
FROM   products
WHERE  category_id = 5 AND price &lt;= 80 AND rating_avg &gt;= 4
GROUP  BY brand_id;
-- ^ painful for large result sets without aggregated rollups

-- For attribute filters, normalize to a side table and INTERSECT
CREATE TABLE product_attributes (
  product_id INT NOT NULL,
  attr_key   VARCHAR(50) NOT NULL,
  attr_val   VARCHAR(100) NOT NULL,
  PRIMARY KEY (product_id, attr_key, attr_val),
  KEY idx_attr (attr_key, attr_val, product_id)
);

-- "size=10 AND color=red"
SELECT pa1.product_id
FROM   product_attributes pa1
JOIN   product_attributes pa2 ON pa1.product_id = pa2.product_id
WHERE  pa1.attr_key = 'size'  AND pa1.attr_val = '10'
  AND  pa2.attr_key = 'color' AND pa2.attr_val = 'red';

-- The right answer at scale: sync to a search engine
-- Meilisearch / Typesense / Elasticsearch handle facets natively in &lt;50ms</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Approach</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>SQL with composite indexes</td><td>One system; ACID</td><td>Only the leading-column combinations are fast; many combos =&nbsp; many indexes</td></tr>
    <tr><td>Bitmap index emulation (side table)</td><td>Arbitrary attribute combos</td><td>Many JOINs/INTERSECTs</td></tr>
    <tr><td>Pre-aggregated facet counts</td><td>Sub-second facets</td><td>Stale; rebuild on changes</td></tr>
    <tr><td>Search engine (ES/Meili/Typesense/Algolia)</td><td>Fast facets, free-text, ranking</td><td>Sync from MySQL; ops</td></tr>
    <tr><td>Columnar (ClickHouse, DuckDB)</td><td>Any-dimension filters fast</td><td>Read-only; eventual consistency</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026, faceted search is a solved problem &mdash; use the right tool. <strong>Meilisearch</strong> (typo-tolerant, fast facets, generous free tier), <strong>Typesense</strong> (similar), <strong>Algolia</strong> (managed, expensive but excellent UX), <strong>Elasticsearch</strong> / <strong>OpenSearch</strong> (most powerful, heavier ops), <strong>Vespa</strong> (rank-heavy use cases). Sync from MySQL via <strong>Debezium</strong> CDC + transform; or app-side dual-write inside outbox. <strong>Algolia InstantSearch</strong>, <strong>Typesense InstantSearch</strong>, <strong>React Instant Search</strong> ship the React/Vue UI components for facet UI. AI-enhanced search adds semantic similarity: <strong>Algolia Neural Search</strong>, <strong>Vespa</strong>, <strong>Vectara</strong>, or pair search with embedding kNN via <strong>Pinecone</strong> / <strong>Weaviate</strong>. Personalization (different users see different ranks) via <strong>Algolia AI Personalization</strong>, <strong>Coveo</strong>. The biggest mistake: trying to build faceted search in raw SQL on a million-row table &mdash; the optimizer can&rsquo;t handle 10-dimension filtering efficiently no matter the indexes. Index the search engine for filters; use SQL for the canonical store.</p>
'''

ANSWERS[62] = r'''
<p><strong>Situation:</strong> a restaurant management system needs menus (with dishes, modifiers, prices that change), tables/seating, orders, kitchen tickets, payments, staff, and inventory tied to dishes. Real-time order flow is critical &mdash; kitchen and front-of-house must stay synchronized.</p>

<p><strong>Approach:</strong> normalize menu and dishes; orders are header + line items with modifier sub-rows; price snapshots on order lines (menu price changes shouldn&rsquo;t affect open orders); kitchen state is a column on order_items.</p>

<pre><code>CREATE TABLE restaurants (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150),
  timezone VARCHAR(50)
);

CREATE TABLE tables (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT NOT NULL,
  number        VARCHAR(10),
  capacity      TINYINT,
  status        ENUM('available','occupied','reserved','cleaning') DEFAULT 'available',
  UNIQUE KEY uq_rest_num (restaurant_id, number),
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

CREATE TABLE menu_categories (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT NOT NULL,
  name          VARCHAR(100),
  position      SMALLINT,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

CREATE TABLE dishes (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT NOT NULL,
  category_id   INT NOT NULL,
  name          VARCHAR(150) NOT NULL,
  description   TEXT,
  price         DECIMAL(8,2) NOT NULL,
  available     BOOLEAN DEFAULT TRUE,
  preparation_min TINYINT,
  KEY idx_restaurant_avail (restaurant_id, available),
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
  FOREIGN KEY (category_id)   REFERENCES menu_categories(id)
);

CREATE TABLE modifiers (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  dish_id INT NOT NULL,
  name   VARCHAR(100),                                 -- 'Extra cheese'
  price  DECIMAL(6,2),
  FOREIGN KEY (dish_id) REFERENCES dishes(id) ON DELETE CASCADE
);

CREATE TABLE orders (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  restaurant_id INT NOT NULL,
  table_id      INT NULL,                              -- NULL for takeout/delivery
  type          ENUM('dine_in','takeout','delivery') NOT NULL,
  server_id     INT NULL,
  status        ENUM('open','sent','partially_paid','closed','voided') NOT NULL DEFAULT 'open',
  subtotal      DECIMAL(10,2) NOT NULL DEFAULT 0,
  tax           DECIMAL(8,2) NOT NULL DEFAULT 0,
  tip           DECIMAL(8,2) NOT NULL DEFAULT 0,
  total         DECIMAL(10,2) NOT NULL DEFAULT 0,
  opened_at     DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  closed_at     DATETIME(3) NULL,
  KEY idx_table_status (table_id, status),
  KEY idx_restaurant_opened (restaurant_id, opened_at),
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
  FOREIGN KEY (table_id)      REFERENCES tables(id)
);

CREATE TABLE order_items (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  order_id    INT NOT NULL,
  dish_id     INT NOT NULL,
  dish_name   VARCHAR(150) NOT NULL,                   -- snapshot
  unit_price  DECIMAL(8,2) NOT NULL,                   -- snapshot
  quantity    SMALLINT NOT NULL DEFAULT 1,
  modifiers   JSON,                                     -- [{name, price}]
  notes       VARCHAR(255),
  kitchen_status ENUM('queued','cooking','ready','served','voided') NOT NULL DEFAULT 'queued',
  sent_at     DATETIME(3) NULL,
  ready_at    DATETIME(3) NULL,
  KEY idx_order (order_id),
  KEY idx_kitchen_status (kitchen_status, sent_at),    -- "what&rsquo;s the kitchen working on"
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (dish_id)  REFERENCES dishes(id)
);

CREATE TABLE payments (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  order_id    INT NOT NULL,
  amount      DECIMAL(10,2) NOT NULL,
  method      ENUM('cash','card','gift_card','split') NOT NULL,
  processor_id VARCHAR(64),                            -- Square / Stripe / Toast txn id
  paid_at     DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Kitchen display: items queued or cooking
SELECT oi.id, o.table_id, oi.dish_name, oi.modifiers, oi.notes, oi.sent_at
FROM   order_items oi
JOIN   orders o ON o.id = oi.order_id
WHERE  oi.kitchen_status IN ('queued','cooking')
  AND  o.restaurant_id = ?
ORDER  BY oi.sent_at;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Snapshot price/name on order_items</td><td>Open orders not affected by menu changes</td><td>Storage; slight redundancy</td></tr>
    <tr><td>Modifiers as JSON on item</td><td>Flexible per-item</td><td>Hard to report on modifier popularity</td></tr>
    <tr><td>Kitchen status on item</td><td>Per-dish tracking</td><td>Update churn</td></tr>
    <tr><td>Split payments via N rows in payments</td><td>SUM = total</td><td>Refund accounting</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: real-time kitchen displays use <strong>WebSocket</strong> &mdash; <strong>Socket.IO</strong>, <strong>Phoenix Channels</strong>, <strong>SignalR</strong>, or managed (<strong>Pusher</strong>, <strong>Ably</strong>); when an item changes status, broadcast to the KDS (kitchen display system). Hardware integration: thermal receipt printers (<strong>Star Micronics</strong>, <strong>Epson TM-series</strong>), card readers (<strong>Square</strong>, <strong>Clover</strong>, <strong>Stripe Terminal</strong>, <strong>SumUp</strong>), KDS displays (<strong>Toast</strong>, <strong>TouchBistro</strong>, <strong>Square for Restaurants</strong>) use ESC/POS or vendor SDKs. Most independent restaurants use vertical SaaS &mdash; <strong>Toast</strong>, <strong>Square</strong>, <strong>Clover</strong>, <strong>TouchBistro</strong>, <strong>Lightspeed Restaurant</strong>; build only when you&rsquo;re a chain or have unique workflows. Online ordering integration: <strong>DoorDash Drive</strong>, <strong>Uber Eats</strong>, <strong>Deliveroo</strong>, <strong>Otter</strong> aggregate orders from multiple platforms. Inventory deduction at item level (recipes table linking dish &rarr; ingredients) so chefs see "out of avocado" before customers. Tip distribution and payroll integration with <strong>Gusto</strong>, <strong>Toast Payroll</strong>. The schema is fine; the value is in hardware integration, real-time UX, and OTA delivery integrations &mdash; that&rsquo;s usually why teams buy rather than build.</p>
'''

ANSWERS[63] = r'''
<p><strong>Situation:</strong> a microservices system has dozens of services, each owning its own database. Schema changes in one service must not break others; data shared via events, not direct DB access. Coordinated migrations across services are routine.</p>

<p><strong>Approach:</strong> each service owns its DB and publishes domain events on schema-stable contracts; consumer services build their own read models. Schema changes use expand-contract per service; cross-service migrations follow a documented playbook.</p>

<pre><code>-- Service A (Orders) publishes events; Service B (Analytics) consumes
-- Service A's DB
CREATE TABLE orders (
  id BIGINT, customer_id INT, amount DECIMAL(10,2), ...
);

-- Outbox pattern: write event in same transaction as state change
CREATE TABLE order_events_outbox (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  aggregate_id BIGINT NOT NULL,
  event_type   VARCHAR(50) NOT NULL,
  schema_version INT NOT NULL,                       -- event schema version
  payload      JSON NOT NULL,
  created_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  published_at DATETIME(3) NULL,
  KEY idx_unpublished (published_at)
);

-- Place order + emit event atomically
START TRANSACTION;
  INSERT INTO orders (...) VALUES (...);
  INSERT INTO order_events_outbox (aggregate_id, event_type, schema_version, payload)
  VALUES (LAST_INSERT_ID(), 'order_created', 2,
          JSON_OBJECT('id', LAST_INSERT_ID(), 'amount', 99.50));
COMMIT;

-- Relay process drains outbox to Kafka / SNS / RabbitMQ
-- Each consumer maintains its own DB and migrates independently

-- Schema evolution rule: events are additive
-- v1: {id, amount}
-- v2: {id, amount, currency}     <- new field; old consumers ignore it
-- BAD:  {id, total}              <- field rename breaks consumers

-- Service B (Analytics) DB
CREATE TABLE order_summary (
  order_id   BIGINT PRIMARY KEY,
  amount     DECIMAL(10,2),
  currency   CHAR(3) DEFAULT 'USD',
  created_at DATETIME
);

-- Coordinated cross-service migration playbook (example: change customer ID format)
-- 1. Service A adds new column customer_uuid alongside customer_id
-- 2. Service A populates both; events include both
-- 3. Service B reads both, prefers customer_uuid
-- 4. Service A stops populating customer_id
-- 5. Service B stops reading customer_id
-- 6. Service A drops customer_id column
-- &mdash; each step is a separate deploy; never break in-flight messages</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>DB per service</td><td>Independent schemas; team autonomy</td><td>No cross-service joins; eventual consistency</td></tr>
    <tr><td>Shared DB across services</td><td>JOINs work; single migration</td><td>Implicit coupling; one team blocks all</td></tr>
    <tr><td>Outbox + event bus</td><td>Reliable; replayable; decoupled</td><td>Latency; ordering semantics</td></tr>
    <tr><td>Schema-versioned events</td><td>Backward-compatible evolution</td><td>Code maintains old versions</td></tr>
    <tr><td>Saga pattern for multi-service writes</td><td>Distributed transactions</td><td>Compensating actions for failures</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: event schemas need governance &mdash; <strong>Confluent Schema Registry</strong>, <strong>Apicurio</strong>, <strong>AWS Glue Schema Registry</strong>, or <strong>Buf</strong> for protobuf; CI fails if a PR breaks compatibility. Common formats: <strong>Avro</strong>, <strong>Protobuf</strong>, <strong>JSON Schema</strong>; CloudEvents as the envelope. Event bus options: <strong>Kafka</strong> / <strong>Confluent</strong>, <strong>Redpanda</strong>, <strong>AWS SNS+SQS</strong>, <strong>EventBridge</strong>, <strong>Google Pub/Sub</strong>, <strong>RabbitMQ</strong>, <strong>NATS</strong>. <strong>Debezium</strong> auto-publishes from MySQL binlog &mdash; one less moving part than the outbox relay (but the outbox provides exactly-once write semantics). Saga orchestration via <strong>Temporal</strong>, <strong>Cadence</strong>, <strong>Zeebe</strong>, <strong>AWS Step Functions</strong>; or choreography via events. <strong>Backstage</strong> (Spotify) catalogs services and their schemas. The cardinal rules: never share databases between services (it&rsquo;s tempting, always wrong long-term); never break event compatibility; document the deployment ordering for dual-running phases. Most micro-services teams underestimate the operational maturity needed &mdash; in 2026, <strong>modular monoliths</strong> with clear module boundaries are increasingly preferred for teams under ~50 engineers; microservices when scale or team boundaries genuinely demand it.</p>
'''

ANSWERS[64] = r'''
<p><strong>Situation:</strong> a photo-sharing app needs users, photos (with metadata), albums, comments, likes, follows, feeds. Photos themselves live in object storage; the DB tracks references and metadata. The feed query is the hottest path.</p>

<p><strong>Approach:</strong> normalize core entities; store photo binaries in S3-style storage with the DB holding URLs and metadata; precompute follower counts and feeds for performance.</p>

<pre><code>CREATE TABLE users (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  username     VARCHAR(30) NOT NULL UNIQUE,
  display_name VARCHAR(100),
  avatar_url   VARCHAR(500),
  bio          VARCHAR(500),
  -- denormalized counters for profile pages
  followers_count INT NOT NULL DEFAULT 0,
  following_count INT NOT NULL DEFAULT 0,
  posts_count     INT NOT NULL DEFAULT 0
);

CREATE TABLE follows (
  follower_id  INT NOT NULL,
  followed_id  INT NOT NULL,
  followed_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (follower_id, followed_id),
  KEY idx_followed (followed_id, followed_at),
  FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (followed_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE photos (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  url             VARCHAR(500) NOT NULL,                -- CDN URL of the original
  thumb_url       VARCHAR(500),                          -- pre-resized thumbnail
  width           SMALLINT, height SMALLINT,
  caption         VARCHAR(2200),
  location        VARCHAR(150),
  taken_at        DATETIME NULL,                         -- EXIF
  uploaded_at     DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  -- denormalized
  like_count      INT NOT NULL DEFAULT 0,
  comment_count   INT NOT NULL DEFAULT 0,
  KEY idx_user_uploaded (user_id, uploaded_at DESC),
  KEY idx_uploaded      (uploaded_at DESC),              -- global feed
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE photo_likes (
  photo_id   BIGINT NOT NULL,
  user_id    INT NOT NULL,
  liked_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (photo_id, user_id),
  KEY idx_user_liked (user_id, liked_at)
);

CREATE TABLE photo_comments (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  photo_id   BIGINT NOT NULL,
  user_id    INT NOT NULL,
  body       VARCHAR(1000),
  parent_id  BIGINT NULL,                                -- replies
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_photo_created (photo_id, created_at),
  FOREIGN KEY (photo_id) REFERENCES photos(id) ON DELETE CASCADE
);

-- Pull feed (small follow lists; under ~5000)
SELECT p.*, u.username, u.avatar_url
FROM   photos p
JOIN   users u ON u.id = p.user_id
WHERE  p.user_id IN (SELECT followed_id FROM follows WHERE follower_id = ?)
ORDER  BY p.uploaded_at DESC
LIMIT  20;

-- Push (fan-out-on-write) for celebrities or large follow lists
CREATE TABLE feed_items (
  user_id    INT NOT NULL,                               -- recipient
  photo_id   BIGINT NOT NULL,
  uploaded_at DATETIME(3) NOT NULL,
  PRIMARY KEY (user_id, uploaded_at, photo_id),
  KEY idx_user_time (user_id, uploaded_at DESC)
);

-- On post: app fans out into feed_items for each follower (async, via queue)</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Pull feed (query at view time)</td><td>No fan-out cost; storage cheap</td><td>Slow for users following many</td></tr>
    <tr><td>Push feed (fan-out on write)</td><td>Sub-100 ms timeline read</td><td>Big write amplification for celebs</td></tr>
    <tr><td>Hybrid (push for normal, pull for celebs)</td><td>Best of both</td><td>Complex routing logic</td></tr>
    <tr><td>Photos in object storage</td><td>Cheap; CDN-friendly</td><td>Two systems to monitor</td></tr>
    <tr><td>Denormalized counters</td><td>Fast profile renders</td><td>Update on every like/follow</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: photos go to <strong>S3</strong> / <strong>Cloud Storage</strong> / <strong>R2</strong>; serve via <strong>CloudFront</strong>, <strong>Cloudflare</strong>, <strong>Bunny CDN</strong>, <strong>Fastly</strong>. Resize on demand with <strong>imgix</strong>, <strong>Cloudinary</strong>, <strong>imgproxy</strong>, <strong>Thumbor</strong>, or <strong>Cloudflare Images</strong> &mdash; pre-generating every size wastes storage. Background processing (resize, EXIF strip, virus scan, content moderation) via <strong>SQS</strong> + <strong>Lambda</strong>, <strong>BullMQ</strong>, <strong>Sidekiq</strong>, <strong>Temporal</strong>. AI moderation: <strong>AWS Rekognition</strong>, <strong>Google Vision Safe Search</strong>, <strong>Hive</strong>, <strong>Sightengine</strong> for NSFW/violence; <strong>Clarifai</strong> / <strong>Roboflow</strong> for custom labels. Auto-alt-text from <strong>OpenAI Vision</strong> / <strong>Anthropic Claude Vision</strong> for accessibility. Feed at scale moves to specialized stores: <strong>Cassandra</strong>, <strong>ScyllaDB</strong>, <strong>Stream</strong> (getstream.io), or graph databases for "people you might know". Push notifications via <strong>FCM</strong> / <strong>APNs</strong>. Search via <strong>Elasticsearch</strong> / <strong>OpenSearch</strong>; visual search ("find similar photos") via <strong>CLIP</strong> embeddings + <strong>Pinecone</strong> / <strong>Weaviate</strong>. The schema scales nicely; the costly path is media pipeline + feed delivery.</p>
'''

ANSWERS[65] = r'''
<p><strong>Situation:</strong> the database is the bottleneck &mdash; high QPS, long-tail latency, expensive aggregations. Adding cache reduces load but introduces consistency concerns: cached data can go stale, cache misses storm the DB, invalidation is tricky.</p>

<p><strong>Approach:</strong> layered caching &mdash; HTTP/CDN cache for public content, application cache (Redis/Memcached) for query results and computed values, in-process LRU for hot lookups. Each layer has its own TTL and invalidation strategy.</p>

<pre><code>// 1. Read-aside cache (most common pattern)
async function getProduct(id) {
  const key = `product:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const product = await db.query(
    'SELECT * FROM products WHERE id = ?', [id]);
  if (product) {
    await redis.set(key, JSON.stringify(product), 'EX', 300);  // 5 min TTL
  }
  return product;
}

// 2. Write-through (update cache when DB changes)
async function updateProduct(id, data) {
  await db.query('UPDATE products SET ... WHERE id = ?', [id]);
  // Invalidate (preferred over update; avoids race conditions)
  await redis.del(`product:${id}`);
}

// 3. Stampede protection: single-flight + lock
async function getProductSafe(id) {
  const key = `product:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  // Lock: only one request fetches; others wait briefly
  const lock = await redis.set(`lock:${key}`, '1', 'NX', 'EX', 5);
  if (!lock) {
    await sleep(50);
    return getProductSafe(id);          // retry; cache should be populated
  }
  try {
    const product = await db.query('SELECT * FROM products WHERE id = ?', [id]);
    await redis.set(key, JSON.stringify(product), 'EX', 300);
    return product;
  } finally {
    await redis.del(`lock:${key}`);
  }
}

// 4. Cache aggregated counts (list views)
async function getProductsByCategory(catId, page) {
  const key = `cat:${catId}:page:${page}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const rows = await db.query('SELECT id FROM products WHERE category_id = ? LIMIT ? OFFSET ?',
    [catId, 20, page * 20]);
  await redis.set(key, JSON.stringify(rows), 'EX', 60);   // shorter TTL for lists
  return rows;
}

# 5. Server-side: MySQL query cache (deprecated; use ProxySQL or app cache)
# 6. Database: tune the buffer pool so hot data is in RAM (caching IS the buffer pool)</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Strategy</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Read-aside (lazy load)</td><td>Simple; only cache what&rsquo;s asked for</td><td>First request slow; stampedes possible</td></tr>
    <tr><td>Write-through</td><td>Cache always fresh after writes</td><td>Slower writes; cache populated for unread keys</td></tr>
    <tr><td>Write-back</td><td>Fastest writes</td><td>Data loss on cache crash; rarely used in OLTP</td></tr>
    <tr><td>TTL only (no invalidation)</td><td>Simple</td><td>Stale data window</td></tr>
    <tr><td>Tag-based invalidation</td><td>Group invalidation</td><td>Tag tracking infra</td></tr>
    <tr><td>CDN cache (HTTP layer)</td><td>Free; closest to user</td><td>Public/idempotent only</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: <strong>Redis</strong> (or <strong>KeyDB</strong>, <strong>Dragonfly</strong>, <strong>Valkey</strong>) for application cache &mdash; managed via <strong>Elasticache</strong>, <strong>Upstash</strong>, <strong>Redis Cloud</strong>, <strong>Memorystore</strong>. <strong>Memcached</strong> is still a strong choice for pure key-value cache. <strong>CDN</strong> caching for HTML, images, API responses with public/private headers via <strong>CloudFront</strong>, <strong>Cloudflare</strong>, <strong>Fastly</strong>, <strong>Bunny</strong>, <strong>Akamai</strong>; cache-key includes Vary headers. Patterns to watch out for: <strong>thundering herd</strong> (cache miss + 1000 concurrent rebuilds &mdash; use single-flight as above, or <strong>refresh-ahead</strong>), <strong>cache penetration</strong> (queries for non-existent keys hit DB &mdash; cache nulls with short TTL or use a Bloom filter), <strong>cache avalanche</strong> (many keys expire at the same instant &mdash; jitter TTLs). Tag-based invalidation: <strong>Cloudflare Cache Tags</strong>, <strong>Vercel Tags</strong>, <strong>Redis</strong> with manual tag &rarr; key sets, <strong>Varnish</strong> with bans. Edge databases (<strong>Cloudflare D1</strong>, <strong>Turso</strong>, <strong>Neon</strong>, <strong>PlanetScale</strong> regions, <strong>Cloudflare Hyperdrive</strong>) act as a global query cache. Observe: cache hit rate must be tracked &mdash; below 80% the cache is rarely worth its complexity. The right answer often is "tune indexes first" &mdash; cache covers what indexing can&rsquo;t.</p>
'''

ANSWERS[66] = r'''
<p><strong>Situation:</strong> an inventory management system tracks products, suppliers, stock levels, purchase orders, sales (consuming stock), warehouse locations, and reorder points. Multiple users update stock concurrently; numbers must be exact.</p>

<p><strong>Approach:</strong> normalize products / suppliers / locations; track stock per (product, location) with atomic updates; record movements as immutable events for audit; reorder logic via scheduled job.</p>

<pre><code>CREATE TABLE suppliers (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  name    VARCHAR(150),
  contact JSON,
  active  BOOLEAN DEFAULT TRUE
);

CREATE TABLE products (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  sku          VARCHAR(50) NOT NULL UNIQUE,
  name         VARCHAR(200) NOT NULL,
  unit_cost    DECIMAL(10,2),
  unit_price   DECIMAL(10,2),
  reorder_point INT,
  reorder_qty   INT
);

CREATE TABLE locations (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),                                      -- 'Main Warehouse', 'Storefront NY'
  type ENUM('warehouse','store','transit') NOT NULL
);

CREATE TABLE stock (
  product_id    INT NOT NULL,
  location_id   INT NOT NULL,
  on_hand       INT NOT NULL DEFAULT 0,
  reserved      INT NOT NULL DEFAULT 0,                   -- committed to open orders
  available     INT GENERATED ALWAYS AS (on_hand - reserved) STORED,
  PRIMARY KEY (product_id, location_id),
  KEY idx_low_stock (location_id, available),
  FOREIGN KEY (product_id)  REFERENCES products(id),
  FOREIGN KEY (location_id) REFERENCES locations(id)
);

-- Immutable movement log (audit trail; rebuild stock from this if needed)
CREATE TABLE stock_movements (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  product_id    INT NOT NULL,
  location_id   INT NOT NULL,
  delta         INT NOT NULL,                              -- positive = inbound, negative = outbound
  reason        ENUM('purchase','sale','transfer','adjustment','return','damage') NOT NULL,
  reference_type VARCHAR(30),
  reference_id   BIGINT,                                   -- e.g., purchase_order.id
  actor_id      INT,
  occurred_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_product_location_time (product_id, location_id, occurred_at),
  FOREIGN KEY (product_id)  REFERENCES products(id),
  FOREIGN KEY (location_id) REFERENCES locations(id)
);

CREATE TABLE supplier_products (
  supplier_id INT NOT NULL,
  product_id  INT NOT NULL,
  supplier_sku VARCHAR(50),
  unit_cost   DECIMAL(10,2),
  lead_time_days SMALLINT,
  PRIMARY KEY (supplier_id, product_id)
);

CREATE TABLE purchase_orders (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  supplier_id  INT NOT NULL,
  status       ENUM('draft','sent','partially_received','received','cancelled') NOT NULL,
  ordered_at   DATETIME,
  expected_at  DATE,
  total_cost   DECIMAL(12,2),
  KEY idx_supplier_status (supplier_id, status),
  FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE purchase_order_items (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  po_id       INT NOT NULL,
  product_id  INT NOT NULL,
  qty_ordered INT NOT NULL,
  qty_received INT NOT NULL DEFAULT 0,
  unit_cost   DECIMAL(10,2),
  KEY idx_po (po_id),
  FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE
);

-- Atomic stock change (sale)
START TRANSACTION;
  -- Reserve when order placed; commit (decrement on_hand) when shipped
  UPDATE stock
  SET    on_hand = on_hand - ?
  WHERE  product_id = ? AND location_id = ? AND on_hand &gt;= ?;
  IF ROW_COUNT() = 0 THEN
    ROLLBACK; SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock';
  END IF;

  INSERT INTO stock_movements (product_id, location_id, delta, reason, reference_type, reference_id, actor_id)
  VALUES (?, ?, -1 * ?, 'sale', 'order', ?, ?);
COMMIT;

-- Items needing reorder
SELECT p.id, p.name, l.id AS location_id, s.available, p.reorder_point, p.reorder_qty
FROM   stock s
JOIN   products p  ON p.id = s.product_id
JOIN   locations l ON l.id = s.location_id
WHERE  s.available &lt;= p.reorder_point AND p.reorder_point IS NOT NULL;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Stock per (product, location)</td><td>Multi-warehouse; transfers tracked</td><td>More joins for total stock</td></tr>
    <tr><td>Movements log</td><td>Audit; can rebuild stock</td><td>Storage; queries vs current state</td></tr>
    <tr><td>Reserved + on_hand split</td><td>"Available" honors carts</td><td>Two columns to maintain</td></tr>
    <tr><td>Generated <code>available</code> column</td><td>Always consistent</td><td>Stored=disk; virtual=compute on read</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: integration is everything &mdash; <strong>Shopify</strong>, <strong>WooCommerce</strong>, <strong>BigCommerce</strong>, <strong>Amazon Seller Central</strong>, <strong>NetSuite</strong>, <strong>QuickBooks</strong>, <strong>Square POS</strong> all need real-time sync to avoid overselling. Vendor solutions: <strong>Zoho Inventory</strong>, <strong>Cin7</strong>, <strong>Katana</strong>, <strong>inFlow</strong>, <strong>Fishbowl</strong>, <strong>Linnworks</strong>, <strong>Brightpearl</strong>, <strong>Trade Gecko</strong> (now QuickBooks Commerce), <strong>Skubana</strong>, <strong>Sellbrite</strong> aggregate channels. Forecasting/demand planning is its own market: <strong>Inventory Planner</strong>, <strong>Streamline</strong>, <strong>Lokad</strong>, increasingly AI-driven (<strong>OpenAI</strong>, custom models on <strong>Databricks</strong>). Barcode/RFID scanning via mobile apps (<strong>Scandit</strong> SDK, <strong>Datalogic</strong>). For warehouse ops: <strong>Fishbowl</strong>, <strong>Manhattan</strong>, <strong>Korber</strong> WMS for big ops; <strong>ShipBob</strong> / <strong>ShipHero</strong> / <strong>Shippo</strong> for 3PL. Cycle counting / spot audits via mobile + RF scanner; track variance trends. The hardest correctness problem: phantom inventory (system says 10, shelf has 7) &mdash; reconcile via periodic counts, not just movement log. Multi-currency &amp; multi-tax via <strong>Avalara</strong> / <strong>TaxJar</strong>. EDI for big-supplier integration via <strong>SPS Commerce</strong>, <strong>TrueCommerce</strong>, or modern alternatives like <strong>Stedi</strong>.</p>
'''

ANSWERS[67] = r'''
<p><strong>Situation:</strong> a production MySQL deployment needs continuous monitoring &mdash; query performance, replication lag, error rates, disk usage, connection counts &mdash; with alerts when something is wrong before users notice.</p>

<p><strong>Approach:</strong> three layers &mdash; (1) MySQL Performance Schema and SHOW STATUS for raw metrics, (2) collector agent (Prometheus exporter, Datadog Agent, etc.) to gather and store, (3) alerting rules with sensible thresholds tied to runbooks.</p>

<pre><code>-- Performance Schema basics (enabled by default in MySQL 8)
-- Top slow queries by total elapsed time
SELECT digest_text, count_star, avg_timer_wait/1e9 AS avg_ms,
       sum_timer_wait/1e9 AS total_ms
FROM   performance_schema.events_statements_summary_by_digest
ORDER  BY sum_timer_wait DESC LIMIT 20;

-- Lock waits and contention
SELECT * FROM performance_schema.data_lock_waits;

-- Buffer pool hit ratio (target &gt; 99%)
SELECT (1 - (
  (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE variable_name = 'Innodb_buffer_pool_reads')
  /
  (SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE variable_name = 'Innodb_buffer_pool_read_requests')
)) * 100 AS hit_ratio_pct;

-- Connection usage
SHOW STATUS LIKE 'Threads_connected';        -- vs max_connections
SHOW STATUS LIKE 'Threads_running';          -- the one that matters under load
SHOW STATUS LIKE 'Aborted_clients';          -- connection drops

-- Replication health
SHOW REPLICA STATUS\G
-- Watch: Seconds_Behind_Source, Replica_IO_Running, Replica_SQL_Running

-- Disk space and table bloat
SELECT table_schema, table_name,
       data_length/1024/1024 AS data_mb,
       index_length/1024/1024 AS index_mb,
       data_free/1024/1024 AS free_mb
FROM   information_schema.tables
ORDER  BY data_length DESC LIMIT 10;

-- Long-running transactions (the silent killer)
SELECT trx_id, trx_state, trx_started, trx_query
FROM   information_schema.innodb_trx
WHERE  TIMESTAMPDIFF(SECOND, trx_started, NOW()) &gt; 60
ORDER  BY trx_started;</code></pre>

<p><strong>Trade-offs (alert thresholds and golden signals):</strong></p>

<table>
  <thead><tr><th>Metric</th><th>Warning</th><th>Critical</th><th>Why</th></tr></thead>
  <tbody>
    <tr><td>Replication lag (seconds)</td><td>&gt; 30</td><td>&gt; 300</td><td>Stale reads; failover risk</td></tr>
    <tr><td>Connection % of max</td><td>&gt; 70%</td><td>&gt; 90%</td><td>Coming connection wall</td></tr>
    <tr><td>Buffer pool hit ratio</td><td>&lt; 99%</td><td>&lt; 95%</td><td>Working set bigger than RAM</td></tr>
    <tr><td>Query latency p99</td><td>&gt; 100 ms</td><td>&gt; 500 ms</td><td>User-visible slowness</td></tr>
    <tr><td>Disk free space</td><td>&lt; 25%</td><td>&lt; 10%</td><td>Out-of-space = full outage</td></tr>
    <tr><td>Slow queries / sec</td><td>&gt; 5</td><td>&gt; 50</td><td>Indicator of regression</td></tr>
    <tr><td>Aborted connections / min</td><td>&gt; 10</td><td>&gt; 100</td><td>Network or auth issues</td></tr>
    <tr><td>Long-running transactions</td><td>&gt; 60s</td><td>&gt; 5min</td><td>Locks accumulate; replication stalls</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026 the standard observability stack is <strong>Prometheus</strong> + <strong>mysqld_exporter</strong> + <strong>Grafana</strong> + <strong>Alertmanager</strong> for self-hosted; SaaS options include <strong>Datadog DBM</strong> (database monitoring with query-level visibility), <strong>New Relic Database Monitoring</strong>, <strong>SolarWinds DPA</strong>, <strong>VividCortex</strong> (now SolarWinds), <strong>Percona PMM</strong> (open-source, MySQL-native), <strong>SkySQL</strong> for MariaDB. <strong>pt-query-digest</strong> remains the gold standard for slow log analysis. <strong>Aurora</strong>, <strong>Cloud SQL</strong>, <strong>Azure Database for MySQL</strong> bundle <strong>Performance Insights</strong> / <strong>Query Insights</strong> with their service. Alerting via <strong>PagerDuty</strong>, <strong>Opsgenie</strong>, <strong>Splunk On-Call</strong>, <strong>incident.io</strong>, <strong>Rootly</strong>, <strong>FireHydrant</strong>; route by severity and time of day. The cardinal principle: every alert should be actionable and have a linked runbook. "Buffer pool hit ratio low" without a runbook becomes ignored noise. Track MTTA (acknowledge) and MTTR (resolve) as KPIs &mdash; these reveal whether your alerts are calibrated. Synthetic monitoring (<strong>Checkly</strong>, <strong>Datadog Synthetics</strong>) catches user-visible problems before metrics do. Most outages aren&rsquo;t mysteries; they&rsquo;re the same recurring failures &mdash; the goal is alerting earlier and faster runbooks each cycle.</p>
'''

ANSWERS[68] = r'''
<p><strong>Situation:</strong> a travel booking platform aggregates flights, hotels, car rentals (and sometimes trains, activities) into a single trip. Inventory comes from external providers via APIs &mdash; GDSes (Amadeus, Sabre), Booking.com, Expedia &mdash; and bookings span multiple suppliers in one transaction.</p>

<p><strong>Approach:</strong> separate searches and bookings; cache search results briefly; track each segment of a trip as a separate booking with a parent trip; payment captures only after all segments confirm.</p>

<pre><code>CREATE TABLE travelers (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  full_name    VARCHAR(200),
  date_of_birth DATE,
  passport_no  VARCHAR(20),                          -- encrypted at rest
  passport_country CHAR(2),
  loyalty_numbers JSON,                               -- {AA: '...', UA: '...'}
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE trips (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  name        VARCHAR(200),
  status      ENUM('quoted','booked','partially_booked','completed','cancelled') NOT NULL,
  total_price DECIMAL(12,2),
  currency    CHAR(3),
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_user_status (user_id, status),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Each trip has multiple segments
CREATE TABLE flight_bookings (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  trip_id         INT NOT NULL,
  provider        VARCHAR(50),                       -- 'amadeus','sabre','duffel'
  pnr             VARCHAR(10),                        -- "Passenger Name Record"
  airline_code    CHAR(2),
  flight_number   VARCHAR(10),
  origin          CHAR(3),                            -- IATA
  destination     CHAR(3),
  depart_at       DATETIME,
  arrive_at       DATETIME,
  cabin           ENUM('economy','premium','business','first'),
  fare_amount     DECIMAL(10,2),
  currency        CHAR(3),
  status          ENUM('held','confirmed','ticketed','cancelled') NOT NULL,
  KEY idx_trip (trip_id),
  KEY idx_pnr (pnr),
  FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE TABLE hotel_bookings (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  trip_id     INT NOT NULL,
  provider    VARCHAR(50),                            -- 'booking','expedia','direct'
  confirmation VARCHAR(50),
  hotel_id    VARCHAR(64),
  hotel_name  VARCHAR(200),
  city        VARCHAR(100),
  check_in    DATE,
  check_out   DATE,
  room_type   VARCHAR(100),
  total_price DECIMAL(10,2),
  currency    CHAR(3),
  status      ENUM('held','confirmed','cancelled') NOT NULL,
  KEY idx_trip (trip_id),
  FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE TABLE car_bookings (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  trip_id       INT NOT NULL,
  provider      VARCHAR(50),                          -- 'hertz','avis','enterprise'
  confirmation  VARCHAR(50),
  pickup_at     DATETIME,
  return_at     DATETIME,
  pickup_loc    VARCHAR(100),
  return_loc    VARCHAR(100),
  vehicle_class VARCHAR(50),
  total_price   DECIMAL(10,2),
  status        ENUM('held','confirmed','cancelled') NOT NULL,
  KEY idx_trip (trip_id),
  FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE TABLE payments (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  trip_id     INT NOT NULL,
  amount      DECIMAL(12,2),
  currency    CHAR(3),
  processor   VARCHAR(30),                            -- 'stripe','adyen'
  intent_id   VARCHAR(64),
  status      ENUM('authorized','captured','refunded','failed') NOT NULL,
  paid_at     DATETIME(3),
  FOREIGN KEY (trip_id) REFERENCES trips(id)
);

-- Search caching
CREATE TABLE search_results_cache (
  cache_key VARCHAR(64) PRIMARY KEY,                  -- hash of params
  payload   JSON,                                      -- provider responses
  expires_at DATETIME NOT NULL,
  KEY idx_expires (expires_at)
);</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Separate tables per segment type</td><td>Type-specific fields</td><td>UNION for "all my bookings"</td></tr>
    <tr><td>Held + confirmed states</td><td>Payment captures atomically across providers</td><td>Hold expiration handling</td></tr>
    <tr><td>Search results cache</td><td>Provider rate limits respected</td><td>Stale prices &lt;30 min</td></tr>
    <tr><td>Per-provider PNR/confirmation</td><td>Direct lookup with supplier</td><td>Provider-coupled schema</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: provider integrations are the real product &mdash; flights via <strong>Amadeus</strong>, <strong>Sabre</strong>, <strong>Travelport</strong> (legacy GDSes), or modern APIs <strong>Duffel</strong>, <strong>Kiwi.com</strong>, <strong>Travelport NDC</strong>; hotels via <strong>Expedia Rapid</strong>, <strong>Booking.com Affiliate</strong>, <strong>Hotelbeds</strong>, <strong>HotelDo</strong>; cars via <strong>CarTrawler</strong>, supplier-direct (<strong>Hertz</strong>, <strong>Avis</strong>, <strong>Enterprise</strong>). Implement saga pattern for multi-segment booking: if hotel confirms but flight fails, automatically void the hotel hold &mdash; <strong>Temporal</strong>, <strong>AWS Step Functions</strong>, <strong>Cadence</strong> orchestrate this. Pricing fluctuation handling: re-validate prices at the moment of payment because providers price-change (this is why "price has changed" pop-ups exist). Trip planning AI &mdash; <strong>Layla</strong>, <strong>Mindtrip</strong>, <strong>Wonderplan</strong>, in-house with <strong>OpenAI</strong> / <strong>Anthropic</strong> &mdash; is the 2026 differentiator. Map APIs (<strong>Google Maps</strong>, <strong>Mapbox</strong>) for itinerary geographic visualization. Currency: store both transaction and display currency; FX via <strong>Wise</strong>, <strong>OpenExchangeRates</strong>. Loyalty integration is hard &mdash; airlines treat third-party booking points-eligibility opaquely. Disruption management (canceled flights, hotel oversells) is what users remember; auto-rebook flows or proactive alerts via <strong>Twilio</strong> SMS / push are major retention drivers. The schema is the infrastructure; the value is supplier coverage and disruption UX.</p>
'''

ANSWERS[69] = r'''
<p><strong>Situation:</strong> a content platform lets users tag posts/products/photos with arbitrary keywords; visitors filter by tag, see "related by tag" lists, and tag clouds. Tags are user-generated, so they have variable casing, typos, and synonyms.</p>

<p><strong>Approach:</strong> normalize tags to a tags table with canonical names; M2M between content and tags; track popularity for autocomplete; for fuzzy matching and suggestions, use a search engine.</p>

<pre><code>CREATE TABLE tags (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(50) NOT NULL UNIQUE,            -- canonical: lowercased, trimmed
  display    VARCHAR(50),                             -- as first entered
  usage_count INT NOT NULL DEFAULT 0,                  -- denormalized for ranking
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post_tags (
  post_id INT NOT NULL,
  tag_id  INT NOT NULL,
  added_by INT,
  added_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (post_id, tag_id),
  KEY idx_tag_post (tag_id, post_id),                 -- "all posts with tag X"
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id)  REFERENCES tags(id) ON DELETE CASCADE
);

-- Add a tag to a post (idempotent; create tag if missing)
START TRANSACTION;
  INSERT INTO tags (name, display) VALUES (LOWER(?), ?)
    ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id);
  SET @tag_id = LAST_INSERT_ID();
  INSERT IGNORE INTO post_tags (post_id, tag_id) VALUES (?, @tag_id);
  IF ROW_COUNT() &gt; 0 THEN
    UPDATE tags SET usage_count = usage_count + 1 WHERE id = @tag_id;
  END IF;
COMMIT;

-- Browse posts by tag
SELECT p.*
FROM   posts p
JOIN   post_tags pt ON pt.post_id = p.id
JOIN   tags t       ON t.id = pt.tag_id
WHERE  t.name = LOWER(?)
ORDER  BY p.created_at DESC
LIMIT  20;

-- "Top tags" (tag cloud)
SELECT name, usage_count
FROM   tags
WHERE  usage_count &gt; 10
ORDER  BY usage_count DESC
LIMIT  100;

-- Tag autocomplete (prefix search)
SELECT name FROM tags
WHERE  name LIKE CONCAT(LOWER(?), '%')
ORDER  BY usage_count DESC
LIMIT  10;

-- "Find similar posts via shared tags" (count overlap)
SELECT pt2.post_id, COUNT(*) AS shared_tags
FROM   post_tags pt1
JOIN   post_tags pt2 ON pt1.tag_id = pt2.tag_id AND pt1.post_id &lt;&gt; pt2.post_id
WHERE  pt1.post_id = ?
GROUP  BY pt2.post_id
ORDER  BY shared_tags DESC
LIMIT  10;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Normalized tags table</td><td>One row per concept; deduped</td><td>Requires resolution on add</td></tr>
    <tr><td>JSON array of tags on post</td><td>Single row read</td><td>Harder to count usage; index pain</td></tr>
    <tr><td>Denormalized usage_count</td><td>Fast tag clouds</td><td>Update on every (un)tag</td></tr>
    <tr><td>Synonym table (tag &rarr; canonical)</td><td>"NYC" &rarr; "New York"</td><td>Curation effort</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: tag canonicalization is the hardest part &mdash; "javascript" vs "js" vs "JavaScript" all describe the same thing. Strategies: (1) admin-curated synonyms in a synonym table; (2) auto-suggest existing tags during entry to avoid creating new variants; (3) clustering similar tags with embeddings (<strong>OpenAI</strong>, <strong>Cohere</strong>, <strong>VoyageAI</strong>) and merging near-duplicates. For autocomplete, an in-memory data structure (<strong>Redis</strong> sorted sets or <strong>Trie</strong>) outperforms <code>LIKE 'prefix%'</code> at scale. Search engines do this natively: <strong>Meilisearch</strong>, <strong>Typesense</strong>, <strong>Algolia</strong>, <strong>Elasticsearch</strong> with edge-ngram analyzer. For "related content" beyond tag overlap, semantic similarity via embeddings on titles/bodies plus tag features outperforms naive co-occurrence &mdash; vectors in <strong>pgvector</strong>, <strong>Pinecone</strong>, <strong>Weaviate</strong>. Anti-spam: rate-limit tag creation per user, block profanity (<strong>Sightengine</strong>, <strong>Hive</strong> moderation, profanity dictionaries). Hashtag-style social tagging on Instagram/X uses similar schemas at massively higher scale, with hot tags hitting Redis-style counters and search engines for browse. The principle: tags should be a UX feature first &mdash; hand-typed taxonomies become messy. Suggest existing tags as the default UX, allow free-form, normalize aggressively.</p>
'''

ANSWERS[70] = r'''
<p><strong>Situation:</strong> a mobile app needs to work offline &mdash; users edit data while disconnected, then sync when back online. Conflicts are inevitable: same record edited on phone and server simultaneously, deletes that race against edits.</p>

<p><strong>Approach:</strong> represent every change as an event with a timestamp and source; sync via diff or CRDT; resolve conflicts with last-write-wins per field, vector clocks, or app-specific merge logic. The DB on the server logs all changes; the device replays its log on sync.</p>

<pre><code>-- Server-side: change log per entity
CREATE TABLE notes (
  id          VARCHAR(36) PRIMARY KEY,                -- UUID; client-generated
  user_id     INT NOT NULL,
  title       VARCHAR(200),
  body        TEXT,
  updated_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  deleted_at  DATETIME(3) NULL,                       -- soft delete
  KEY idx_user_updated (user_id, updated_at)
);

-- Each change is an immutable event
CREATE TABLE note_changes (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  note_id      VARCHAR(36) NOT NULL,
  user_id      INT NOT NULL,
  device_id    VARCHAR(64),                            -- per-device unique
  client_seq   BIGINT NOT NULL,                        -- client&rsquo;s monotonic counter
  op           ENUM('create','update','delete') NOT NULL,
  field_changes JSON,                                   -- {title: 'new'} for partial updates
  applied_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_device_seq (device_id, client_seq),     -- idempotent retries
  KEY idx_note_applied (note_id, applied_at),
  FOREIGN KEY (note_id) REFERENCES notes(id)
);

-- Device sync session: pull server changes since last cursor
SELECT *
FROM   note_changes
WHERE  user_id = ? AND applied_at &gt; ?           -- last_sync_cursor
ORDER  BY applied_at, id
LIMIT  500;
-- Client applies these to local SQLite; advances cursor

-- Device push: client sends a batch of local changes; server applies idempotently
INSERT INTO note_changes (note_id, user_id, device_id, client_seq, op, field_changes)
VALUES (?, ?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE id = id;            -- idempotent on (device_id, client_seq)

-- Conflict resolution: last-write-wins per field on update
UPDATE notes
SET    title = JSON_VALUE(?, '$.title'),    -- only update fields the client changed
       body  = JSON_VALUE(?, '$.body'),
       updated_at = ?
WHERE  id = ? AND updated_at &lt;= ?;          -- only if our timestamp wins

-- Tombstones for delete: keep the row, mark deleted_at
UPDATE notes SET deleted_at = ? WHERE id = ? AND deleted_at IS NULL;
-- Garbage collect tombstones after retention (e.g., 30 days)</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Server-generated IDs</td><td>Globally unique by construction</td><td>Cannot create offline-first</td></tr>
    <tr><td>Client-generated UUIDs</td><td>Offline create works</td><td>Larger keys; PK ordering pain</td></tr>
    <tr><td>Last-write-wins per field</td><td>Simple; almost always sane</td><td>Concurrent edits to same field = silent loss</td></tr>
    <tr><td>CRDT data types</td><td>Mathematical convergence; lossless merge</td><td>Need CRDT-aware models on both sides</td></tr>
    <tr><td>Operation log + replay</td><td>Auditable; rebuildable</td><td>Storage; replay performance</td></tr>
    <tr><td>Soft delete + tombstones</td><td>Sync sees the delete</td><td>Tombstone GC over retention</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026, off-the-shelf sync engines have matured significantly &mdash; <strong>Replicache</strong> (now Reflect), <strong>RxDB</strong>, <strong>WatermelonDB</strong>, <strong>PowerSync</strong>, <strong>ElectricSQL</strong>, <strong>Triplit</strong>, <strong>Evolu</strong>, <strong>Zero</strong> (by Rocicorp) provide local-first databases with built-in sync. CRDTs via <strong>Yjs</strong>, <strong>Automerge</strong> for collaborative documents (text editors, whiteboards). On-device storage is <strong>SQLite</strong> (universal), <strong>Realm</strong>, <strong>Core Data</strong> (iOS), <strong>Room</strong> (Android), or <strong>WatermelonDB</strong> for React Native. Sync transports: <strong>WebSocket</strong> with backpressure, <strong>HTTP</strong> long-polling, or push-via-FCM/APNs. The hardest correctness problem is order: client device clocks lie, so use server-stamped <code>applied_at</code> for resolution &mdash; never trust device timestamps for conflict ordering. Watch out for retry-at-network-restore storms: exponential backoff + jitter; deduplication via <code>(device_id, client_seq)</code>. Schema migrations are also harder offline: include a schema_version on the device, and let the server migrate the operation stream. Encryption end-to-end if data is sensitive: <strong>libsignal</strong>, <strong>Tink</strong>, with per-user keys. Test offline rigorously &mdash; airplane mode, partial sync, conflicting edits, app force-quits mid-sync &mdash; these are where bugs live.</p>
'''

ANSWERS[71] = r'''
<p><strong>Situation:</strong> a content management system needs articles, authors, categories, tags, media, drafts, scheduled publishes, multiple editors with permissions, and version history. Editors expect Word-class authoring; readers expect static-fast page loads.</p>

<p><strong>Approach:</strong> normalize content + metadata; store revisions as separate rows linked to the article; use status + scheduled_at for publish workflow; render to static or cached HTML for read performance.</p>

<pre><code>CREATE TABLE authors (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL UNIQUE,
  bio     TEXT,
  avatar_url VARCHAR(500),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE categories (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  parent_id INT NULL,
  name      VARCHAR(100) NOT NULL,
  slug      VARCHAR(120) NOT NULL UNIQUE,
  FOREIGN KEY (parent_id) REFERENCES categories(id)
);

CREATE TABLE articles (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  author_id     INT NOT NULL,
  category_id   INT,
  title         VARCHAR(255) NOT NULL,
  slug          VARCHAR(255) NOT NULL UNIQUE,
  excerpt       VARCHAR(500),
  body          MEDIUMTEXT,                            -- markdown / portable text / HTML
  body_format   ENUM('markdown','html','portable_text') NOT NULL DEFAULT 'markdown',
  cover_image_id INT,
  status        ENUM('draft','review','scheduled','published','archived') NOT NULL DEFAULT 'draft',
  published_at  DATETIME NULL,
  scheduled_at  DATETIME NULL,
  -- SEO
  meta_title    VARCHAR(150),
  meta_desc     VARCHAR(300),
  -- Locking for concurrent edit prevention
  locked_by     INT NULL,
  locked_until  DATETIME NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_status_published (status, published_at DESC),
  KEY idx_category_published (category_id, published_at DESC),
  KEY idx_scheduled (status, scheduled_at),
  FULLTEXT idx_ft (title, body),
  FOREIGN KEY (author_id) REFERENCES authors(id),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Revisions: every save creates a row; revert by promoting one
CREATE TABLE article_revisions (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  article_id  INT NOT NULL,
  editor_id   INT NOT NULL,
  title       VARCHAR(255),
  body        MEDIUMTEXT,
  excerpt     VARCHAR(500),
  saved_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_article_saved (article_id, saved_at),
  FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE media (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  uploader_id INT NOT NULL,
  url         VARCHAR(500),
  mime_type   VARCHAR(50),
  width       INT, height INT,
  alt_text    VARCHAR(255),
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Articles published, paginated, by category (the read query)
SELECT a.id, a.title, a.slug, a.excerpt, a.cover_image_id, a.published_at,
       au.user_id, c.name AS category
FROM   articles a
JOIN   authors au ON au.id = a.author_id
LEFT   JOIN categories c ON c.id = a.category_id
WHERE  a.status = 'published'
  AND  a.published_at &lt;= NOW()
ORDER  BY a.published_at DESC
LIMIT  20 OFFSET ?;

-- Scheduler: publish anything whose time has come (cron)
UPDATE articles
SET    status = 'published', published_at = NOW()
WHERE  status = 'scheduled' AND scheduled_at &lt;= NOW();</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Body in MEDIUMTEXT</td><td>Long content; full-text searchable</td><td>Larger row reads</td></tr>
    <tr><td>Revisions in own table</td><td>History; revert; diffs</td><td>Storage growth</td></tr>
    <tr><td>Status + published_at + scheduled_at</td><td>Workflow + future-publish</td><td>Conditional indexes</td></tr>
    <tr><td>Lock columns for editing</td><td>Prevents concurrent overwrites</td><td>Stale locks if editor crashes</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: in 2026 the headless-CMS / API-first ecosystem is enormous &mdash; <strong>Sanity</strong> (Portable Text, real-time), <strong>Contentful</strong>, <strong>Strapi</strong> (OSS), <strong>Payload</strong> (TS-native), <strong>Directus</strong>, <strong>Prismic</strong>, <strong>Storyblok</strong>, <strong>Hygraph</strong>, <strong>Builder.io</strong>, <strong>WebStudio</strong>, <strong>Webflow CMS</strong>; <strong>WordPress</strong> remains the most popular for traditional CMS. Most teams should buy, not build. Front-end via <strong>Next.js</strong>, <strong>Astro</strong>, <strong>Nuxt</strong>, <strong>Remix</strong> for ISR/SSG &mdash; rendering at request time uses the schema above; static export uses build-time queries. Rich-text editing: <strong>Tiptap</strong>, <strong>Lexical</strong> (Meta), <strong>Slate</strong>, <strong>ProseMirror</strong> &mdash; all output structured JSON / Portable Text rather than HTML, far better for cross-channel rendering. Real-time collab via <strong>Yjs</strong> / <strong>Liveblocks</strong> / <strong>Hocuspocus</strong>. Media via <strong>Cloudinary</strong>, <strong>imgix</strong>, <strong>Mux</strong> (video); <strong>Cloudflare Images</strong>; cover image generation with <strong>OG Image API</strong>. AI integration is now table stakes &mdash; <strong>Claude</strong>, <strong>OpenAI</strong>, <strong>Anthropic</strong> for draft assistance, SEO suggestions, alt-text generation, translation; vector search over content via <strong>pgvector</strong> / <strong>Pinecone</strong>. Comments via <strong>Disqus</strong>, <strong>Hyvor Talk</strong>, <strong>Commento</strong>, or built-in. Workflow / approvals (especially in regulated industries) via custom state machines or platforms like <strong>Sanity Studio</strong>. The schema is mature; the differentiation is in editor UX and AI features.</p>
'''

ANSWERS[72] = r'''
<p><strong>Situation:</strong> users post content (text, images, videos, comments) that must be moderated &mdash; spam, abuse, copyright, illegal content. Pure pre-moderation kills engagement; pure post-moderation creates harm. A scalable mix involves automation, queues for human review, and a robust appeals process.</p>

<p><strong>Approach:</strong> three layers &mdash; (1) automated checks on submission (rate limits, ML scores, blocklists), (2) human-review queues for ambiguous cases, (3) post-publish reports + takedown. Track every moderation action for transparency and appeals.</p>

<pre><code>CREATE TABLE posts (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  author_id    INT NOT NULL,
  body         TEXT,
  media_urls   JSON,
  status       ENUM('pending','approved','rejected','removed','queued_review') NOT NULL DEFAULT 'pending',
  visibility   ENUM('public','restricted','hidden') NOT NULL DEFAULT 'public',
  -- automated scores
  toxicity_score    DECIMAL(4,3),                       -- 0-1
  spam_score        DECIMAL(4,3),
  nsfw_score        DECIMAL(4,3),
  -- moderator action
  moderated_by      INT NULL,
  moderated_at      DATETIME NULL,
  removed_reason    VARCHAR(80),
  created_at        DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_status_created (status, created_at),
  KEY idx_author        (author_id, created_at)
);

-- User-submitted reports
CREATE TABLE content_reports (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  post_id       BIGINT NOT NULL,
  reporter_id   INT NOT NULL,
  reason        ENUM('spam','harassment','illegal','copyright','nsfw','misinfo','other') NOT NULL,
  details       VARCHAR(500),
  status        ENUM('open','under_review','resolved','dismissed') NOT NULL DEFAULT 'open',
  resolved_by   INT NULL,
  resolved_at   DATETIME NULL,
  outcome       VARCHAR(80),                           -- 'removed','warned','no_action'
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_post (post_id),
  KEY idx_status_created (status, created_at),
  FOREIGN KEY (post_id)     REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (reporter_id) REFERENCES users(id)
);

-- Moderation queue (pre-publish for borderline content)
CREATE TABLE moderation_queue (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  post_id      BIGINT NOT NULL,
  reason_code  VARCHAR(50),                            -- 'high_toxicity','new_user','reported'
  priority     TINYINT NOT NULL DEFAULT 5,
  assigned_to  INT NULL,
  resolved_at  DATETIME NULL,
  created_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_unassigned (assigned_to, priority, created_at),
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Action history (audit; appeals)
CREATE TABLE moderation_actions (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  post_id     BIGINT,
  user_id     INT,
  action      ENUM('approve','remove','warn','suspend','ban','restore','appeal_granted','appeal_denied') NOT NULL,
  reason      VARCHAR(255),
  actor_id    INT NOT NULL,
  acted_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_user_acted (user_id, acted_at),
  KEY idx_post_acted (post_id, acted_at)
);

-- User trust signals
CREATE TABLE user_moderation (
  user_id    INT PRIMARY KEY,
  warnings   INT NOT NULL DEFAULT 0,
  strikes    INT NOT NULL DEFAULT 0,
  suspended_until DATETIME NULL,
  banned_at  DATETIME NULL,
  trust_score DECIMAL(4,3) DEFAULT 0.500
);

-- Pending review queue
SELECT mq.id, p.body, p.toxicity_score, p.spam_score, p.created_at
FROM   moderation_queue mq
JOIN   posts p ON p.id = mq.post_id
WHERE  mq.assigned_to IS NULL AND mq.resolved_at IS NULL
ORDER  BY mq.priority, mq.created_at
LIMIT  50;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Auto-publish + post-moderation</td><td>Friction-free UX</td><td>Harm window before takedown</td></tr>
    <tr><td>Pre-moderation queue</td><td>Catches before publish</td><td>Latency; engagement drop</td></tr>
    <tr><td>Hybrid (auto-allow + queue suspect)</td><td>Best of both</td><td>Complex routing; calibration</td></tr>
    <tr><td>Soft remove (visibility=hidden)</td><td>Reversible; appeals work</td><td>Storage; cache invalidation</td></tr>
    <tr><td>Audit trail</td><td>Transparency; legal defense</td><td>Storage; PII risk</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: automated content moderation in 2026 means <strong>OpenAI Moderation</strong> (free, decent), <strong>Hive</strong> (best NSFW + violence), <strong>Perspective API</strong> (Google, toxicity), <strong>Sightengine</strong>, <strong>WebPurify</strong>, <strong>Spectrum Labs</strong>, <strong>ActiveFence</strong>, <strong>TwoHat</strong> (Microsoft), <strong>Bodyguard</strong>; for image/video <strong>AWS Rekognition</strong>, <strong>Google Vision Safe Search</strong>, <strong>Azure Content Safety</strong>. CSAM detection is mandatory for image platforms &mdash; <strong>PhotoDNA</strong>, <strong>Thorn Safer</strong>, <strong>NCMEC</strong> integration, plus <strong>Project Lantern</strong> for cross-platform signals. LLM-based contextual moderation (catching dog-whistles, sarcasm) via <strong>Anthropic</strong> / <strong>OpenAI</strong> with custom rubrics. Human reviewer tools: <strong>Sift</strong>, <strong>Spectrum</strong>, <strong>Trusty</strong>, <strong>Cinder</strong>, <strong>Checkstep</strong>, <strong>Reckon</strong> &mdash; vendors with case management, decision logging, escalation. The hardest non-tech aspect is reviewer welfare: dealing with disturbing content has a real psychological cost &mdash; rotation, mental health support, and outsourcing partners with proper care (<strong>Teleperformance</strong>, <strong>Accenture</strong>, <strong>Concentrix</strong>) are necessary. Regulatory compliance: <strong>EU DSA</strong> (transparency reports, recommender opt-out, illegal content takedown SLAs), <strong>UK Online Safety Act</strong>, <strong>Australian Online Safety Act</strong>; <strong>Section 230</strong> in US offers protection but isn&rsquo;t universal. Appeals are mandatory in many jurisdictions. The schema covers the data; the operational maturity is what matters.</p>
'''

ANSWERS[73] = r'''
<p><strong>Situation:</strong> the production database fails &mdash; instance crash, disk corruption, accidental DROP TABLE, ransomware. The team needs to restore data with bounded loss (RPO) and bounded downtime (RTO). Without an established recovery process, this becomes an outage measured in days.</p>

<p><strong>Approach:</strong> three components &mdash; (1) regular backups (logical + physical), (2) binary log archive for point-in-time recovery, (3) tested runbook. Recovery is only as good as the last successful restore drill.</p>

<pre><code>-- Logical backup with mysqldump (small DBs, transactional consistency)
mysqldump --single-transaction \
  --triggers --routines --events \
  --master-data=2 \
  --all-databases | gzip &gt; full-$(date +%F).sql.gz

# Modern: mysqlpump (parallel)
mysqlpump --default-parallelism=4 \
  --include-databases=shop &gt; shop.sql

-- Physical backup with Percona XtraBackup (large DBs; near-zero impact)
xtrabackup --backup --target-dir=/backups/$(date +%F)
xtrabackup --prepare --target-dir=/backups/2026-04-28

-- Binary log archiving (for PITR between full backups)
[mysqld]
log_bin           = /var/log/mysql/binlog
binlog_expire_logs_seconds = 604800     # 7 days
sync_binlog       = 1                    # durability
binlog_format     = ROW

-- Continuous shipping of binlogs to S3
mysqlbinlog --read-from-remote-server --raw \
  --host=primary --user=repl \
  --to-last-log mysql-bin.000123 | aws s3 cp - s3://backups/binlogs/

-- Restore workflow (full + PITR)
# 1) Restore base backup
xtrabackup --copy-back --target-dir=/backups/2026-04-28
# 2) Replay binlogs up to a point-in-time (BEFORE the bad event)
mysqlbinlog --start-position=N --stop-datetime='2026-04-28 14:30:00' \
  binlog.000123 binlog.000124 | mysql

-- Selective table recovery (without restoring whole DB)
xtrabackup --copy-back --tables='shop.orders' --target-dir=/backups/...

-- Verify with checksums
SELECT TABLE_NAME, TABLE_ROWS, CHECKSUM TABLE shop.orders;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Strategy</th><th>RPO</th><th>RTO</th><th>Storage</th></tr></thead>
  <tbody>
    <tr><td>Daily mysqldump only</td><td>24h</td><td>Hours-days</td><td>Cheap</td></tr>
    <tr><td>Daily XtraBackup + binlog stream</td><td>Seconds</td><td>Hours</td><td>Moderate</td></tr>
    <tr><td>Snapshots (LVM, EBS, ZFS)</td><td>Snapshot interval</td><td>Minutes</td><td>Snapshot $$</td></tr>
    <tr><td>Replicas (read or DR)</td><td>Replication lag</td><td>Failover time</td><td>2x infrastructure</td></tr>
    <tr><td>Aurora / managed PITR</td><td>Seconds</td><td>Sub-minute</td><td>Built-in</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: backups must be (1) automated, (2) off-site, (3) immutable, (4) tested. Managed services solve most of this: <strong>Aurora MySQL</strong> (continuous backup, point-in-time to any second within retention), <strong>RDS</strong> (automated daily + binlog), <strong>Cloud SQL</strong>, <strong>PlanetScale</strong>, <strong>Azure Database for MySQL</strong>. Self-hosted: <strong>Percona XtraBackup</strong> (free, MySQL-aware physical), <strong>Mariabackup</strong>, <strong>MyDumper/MyLoader</strong> (parallel logical), commercial <strong>SQLBackupAndFTP</strong>. Store backups in <strong>S3 with Object Lock</strong> (WORM, ransomware-proof) or <strong>AWS Backup</strong>, <strong>Veeam</strong>, <strong>Rubrik</strong>, <strong>Druva</strong>, <strong>HYCU</strong>; cross-region replication is mandatory for DR. The often-skipped step: <em>test restores quarterly</em> &mdash; a backup that doesn&rsquo;t restore is no backup. Document recovery scenarios: full restore (instance lost), single-table restore (accidental DROP), point-in-time (logical corruption from a bad migration). Encrypt backups (envelope encryption, KMS-managed keys); rotate keys. <strong>3-2-1 rule</strong>: 3 copies, 2 different media, 1 off-site. Watch for "we have backups" &gt;&gt;&gt; "we have <em>tested</em> backups" &mdash; the gap is what causes 5-day outages on the news. Most production failures aren&rsquo;t lost disks &mdash; they&rsquo;re accidental DELETEs without WHERE, runaway migrations, or ransomware on backup targets that weren&rsquo;t actually immutable.</p>
'''

ANSWERS[74] = r'''
<p><strong>Situation:</strong> a learning management system (LMS) needs courses, lessons, quizzes, assignments, grading, certifications, prerequisites between courses, and progress tracking aligned with learning paths. Used by schools, corporations for compliance training, and online academies.</p>

<p><strong>Approach:</strong> course/module/lesson hierarchy (similar to Q58); add quiz attempts with detailed scoring; certifications issued on completion criteria; prerequisites enforced at enrollment.</p>

<pre><code>CREATE TABLE courses (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  code          VARCHAR(20) UNIQUE,                    -- 'CS101'
  title         VARCHAR(200) NOT NULL,
  passing_score TINYINT NOT NULL DEFAULT 70,           -- pct to pass
  cert_id       INT NULL,
  status        ENUM('active','archived') DEFAULT 'active'
);

CREATE TABLE prerequisites (
  course_id        INT NOT NULL,
  prerequisite_id  INT NOT NULL,
  PRIMARY KEY (course_id, prerequisite_id),
  FOREIGN KEY (course_id)        REFERENCES courses(id),
  FOREIGN KEY (prerequisite_id)  REFERENCES courses(id)
);

CREATE TABLE quizzes (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  course_id   INT NOT NULL,
  title       VARCHAR(200),
  time_limit_min SMALLINT,
  attempts_allowed SMALLINT DEFAULT 3,
  shuffle     BOOLEAN DEFAULT TRUE,
  KEY idx_course (course_id),
  FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE quiz_questions (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  quiz_id     INT NOT NULL,
  type        ENUM('single','multi','short_answer','true_false','match') NOT NULL,
  prompt      TEXT NOT NULL,
  options     JSON,                                    -- [{id:'a',text:'...'}]
  correct     JSON,                                    -- correct option ids or text
  points      DECIMAL(5,2) NOT NULL DEFAULT 1,
  position    SMALLINT,
  KEY idx_quiz_position (quiz_id, position),
  FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
);

CREATE TABLE quiz_attempts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  quiz_id     INT NOT NULL,
  student_id  INT NOT NULL,
  attempt_no  SMALLINT NOT NULL,
  score_pct   DECIMAL(5,2),
  passed      BOOLEAN,
  started_at  DATETIME(3),
  submitted_at DATETIME(3),
  responses   JSON,                                    -- [{question_id, response}]
  UNIQUE KEY uq_attempt (quiz_id, student_id, attempt_no),
  KEY idx_student (student_id, submitted_at),
  FOREIGN KEY (quiz_id)    REFERENCES quizzes(id),
  FOREIGN KEY (student_id) REFERENCES users(id)
);

CREATE TABLE certifications (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(200),
  issuer          VARCHAR(150),
  validity_months SMALLINT,                            -- NULL = lifetime
  template_url    VARCHAR(500)                          -- PDF template
);

CREATE TABLE student_certifications (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  student_id      INT NOT NULL,
  cert_id         INT NOT NULL,
  course_id       INT NOT NULL,
  certificate_uuid CHAR(36) NOT NULL UNIQUE,           -- public verification ID
  issued_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at      DATETIME NULL,
  pdf_url         VARCHAR(500),
  KEY idx_student (student_id, issued_at),
  FOREIGN KEY (student_id) REFERENCES users(id),
  FOREIGN KEY (cert_id)    REFERENCES certifications(id),
  FOREIGN KEY (course_id)  REFERENCES courses(id)
);

-- Check enrollment eligibility (all prerequisites passed)
SELECT NOT EXISTS (
  SELECT 1 FROM prerequisites p
  WHERE  p.course_id = ?
    AND  NOT EXISTS (
      SELECT 1 FROM enrollments e
      WHERE  e.student_id = ? AND e.course_id = p.prerequisite_id
        AND  e.completed_at IS NOT NULL
    )
) AS eligible;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Choice</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Question types as enum</td><td>Renderable per type</td><td>Adding types requires schema change</td></tr>
    <tr><td>Responses as JSON</td><td>Flexible by type</td><td>Reporting on specific question stats harder</td></tr>
    <tr><td>Cert UUID for public verify</td><td>Anyone can verify online</td><td>UUID format reveals issuance order if not random</td></tr>
    <tr><td>Prereq table</td><td>Multi-prereq; queryable</td><td>Recursion for chains</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: enterprise compliance LMS dominate this market &mdash; <strong>Cornerstone</strong>, <strong>Docebo</strong>, <strong>Workday Learning</strong>, <strong>SAP SuccessFactors</strong>, <strong>TalentLMS</strong>, <strong>Absorb</strong>, <strong>360Learning</strong>, <strong>iSpring Learn</strong> for businesses; <strong>Canvas</strong>, <strong>Blackboard</strong>, <strong>Moodle</strong>, <strong>Schoology</strong>, <strong>D2L Brightspace</strong> for education. SCORM/xAPI standards for content portability across LMSes &mdash; if you build one, support both. Anti-cheating: shuffle questions, timed sessions, browser lockdown (<strong>Respondus</strong>, <strong>SafeAssign</strong>), proctored exams via <strong>Honorlock</strong>, <strong>ProctorU</strong>, <strong>Examity</strong>, <strong>Proctorio</strong>; AI-based proctoring is controversial &mdash; bias and privacy issues. Adaptive assessments based on response patterns (<strong>IRT</strong> &mdash; item response theory) tune difficulty per learner. Certificate verification: blockchain-anchored on <strong>Ethereum</strong> / <strong>Polygon</strong> for tamper-proof claims (<strong>Accredible</strong>, <strong>Sertifier</strong>, <strong>Credly</strong>); QR codes for instant scan-to-verify. Open badges (<strong>IMS Global Open Badges</strong>) for granular credentialing. AI tutoring is now a major LMS feature &mdash; <strong>Khanmigo</strong> (Khan Academy), <strong>Squirrel AI</strong>, <strong>MathGPT</strong> &mdash; using <strong>OpenAI</strong>/<strong>Anthropic</strong> to explain wrong answers, generate practice. Analytics: track engagement, time-on-task, drop-off points to improve content. Compliance reporting (annual training completion) is the backbone of corporate LMS &mdash; design for "did 95% of staff complete the harassment training" queries.</p>
'''

ANSWERS[75] = r'''
<p><strong>Situation:</strong> a software product issues licenses (per-seat, per-machine, by feature) and subscriptions (monthly/annual); customers want to track usage, ensure they aren&rsquo;t over-deployed, and renew on time. The vendor wants to enforce usage and prevent piracy.</p>

<p><strong>Approach:</strong> license records track entitlements; activations track devices/users using a license; check-in periodically validates and refreshes the activation; tie to subscriptions for time-bounded license validity.</p>

<pre><code>CREATE TABLE products (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(150),
  features      JSON                                    -- {advanced_export: true, max_users: 10}
);

CREATE TABLE customers (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  org     VARCHAR(200),
  email   VARCHAR(255)
);

CREATE TABLE licenses (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  customer_id     INT NOT NULL,
  product_id      INT NOT NULL,
  license_key     VARCHAR(64) NOT NULL UNIQUE,          -- e.g. UUID v7 or signed JWT
  license_type    ENUM('per_seat','per_machine','site','floating') NOT NULL,
  seats_total     INT NOT NULL DEFAULT 1,
  features        JSON,                                  -- override of product defaults
  starts_at       DATE NOT NULL,
  expires_at      DATE NULL,                              -- NULL = perpetual
  status          ENUM('active','expired','revoked','suspended') NOT NULL DEFAULT 'active',
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_customer (customer_id),
  KEY idx_status_expires (status, expires_at),
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (product_id)  REFERENCES products(id)
);

CREATE TABLE activations (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  license_id    INT NOT NULL,
  device_id     VARCHAR(64),                              -- machine fingerprint
  user_email    VARCHAR(255),                             -- per-seat
  hostname      VARCHAR(100),
  ip_address    VARBINARY(16),
  activated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  deactivated_at DATETIME NULL,
  UNIQUE KEY uq_license_device (license_id, device_id),
  KEY idx_license_active (license_id, deactivated_at),
  FOREIGN KEY (license_id) REFERENCES licenses(id) ON DELETE CASCADE
);

-- Subscriptions tied to licenses (renewal cycle)
CREATE TABLE license_subscriptions (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  license_id      INT NOT NULL UNIQUE,
  plan            VARCHAR(50),
  amount          DECIMAL(10,2),
  currency        CHAR(3),
  interval_unit   ENUM('month','year') NOT NULL,
  current_period_end DATETIME NOT NULL,
  status          ENUM('active','past_due','cancelled') NOT NULL,
  external_id     VARCHAR(64),                            -- e.g., Stripe sub_xxx
  FOREIGN KEY (license_id) REFERENCES licenses(id)
);

-- Activation flow
START TRANSACTION;
  SELECT seats_total, expires_at, status,
         (SELECT COUNT(*) FROM activations
          WHERE  license_id = ? AND deactivated_at IS NULL) AS active_count
  INTO @seats, @expires, @status, @active
  FROM   licenses WHERE id = ? FOR UPDATE;

  IF @status &lt;&gt; 'active' OR (@expires IS NOT NULL AND @expires &lt; CURDATE()) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'License invalid';
  END IF;
  IF @active &gt;= @seats THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat limit reached';
  END IF;

  INSERT INTO activations (license_id, device_id, user_email, hostname, ip_address)
  VALUES (?, ?, ?, ?, INET6_ATON(?))
  ON DUPLICATE KEY UPDATE last_seen_at = NOW(3), deactivated_at = NULL;
COMMIT;

-- Periodic heartbeat (license still valid)
UPDATE activations SET last_seen_at = NOW(3) WHERE license_id = ? AND device_id = ?;

-- Renewal due in next 30 days
SELECT l.id, l.license_key, c.email, l.expires_at
FROM   licenses l
JOIN   customers c ON c.id = l.customer_id
WHERE  l.status = 'active' AND l.expires_at BETWEEN CURDATE() AND CURDATE() + INTERVAL 30 DAY;</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
  <thead><tr><th>Approach</th><th>Pro</th><th>Con</th></tr></thead>
  <tbody>
    <tr><td>Online activation (server validates)</td><td>Real-time enforcement; revoke easily</td><td>Requires connectivity</td></tr>
    <tr><td>Offline (signed license file)</td><td>Air-gapped works</td><td>Hard to revoke; clock-back attacks</td></tr>
    <tr><td>Hybrid (offline grace period)</td><td>Best of both</td><td>Edge-case bugs</td></tr>
    <tr><td>JWT license tokens</td><td>Self-verifying; offline OK</td><td>Need rotation strategy</td></tr>
    <tr><td>Hardware fingerprinting</td><td>Anti-piracy</td><td>Customers change machines</td></tr>
  </tbody>
</table>

<p><strong>Production polish</strong>: building licensing yourself is more work than it looks &mdash; <strong>Keygen</strong>, <strong>LicenseSpring</strong>, <strong>Cryptlex</strong>, <strong>Reprise</strong>, <strong>10Duke</strong>, <strong>SoftwareKey</strong> are dedicated licensing platforms with SDK + admin portal. <strong>Paddle Billing</strong>, <strong>FastSpring</strong>, <strong>Gumroad</strong>, <strong>Stripe Billing</strong> handle the subscription side; pair with a licensing service. Common pitfalls: clock manipulation (compare to a server timestamp on heartbeat), VM cloning (fingerprint includes hardware UUID, motherboard serial), aggressive revocation breaking customers (always allow grace period). For B2B SaaS, the trend is "no client license at all" &mdash; everything authenticates against the SaaS backend, and licenses are really seats in your billing system. For desktop apps and developer tools, JWT-style signed licenses (<strong>Ed25519</strong> signing) with online refresh are the modern default. Floating licenses (one of N concurrent users) need lease semantics: a session "checks out" a seat for 1 hour, returns automatically. Compliance reporting for license usage in BI tools is its own product feature: <strong>Snowflake</strong>, <strong>Tableau</strong>, <strong>Power BI</strong> all have license tracking dashboards. Anti-piracy: code obfuscation (<strong>JavaScript Obfuscator</strong>, <strong>Confuser .NET</strong>), but determined pirates win &mdash; the goal is friction, not perfection.</p>
'''

ANSWERS[76] = r'''<p><strong>Situation:</strong> An event management platform handles conferences, concerts, and meetups. Organizers create events, attendees register, and the system issues tickets with QR codes. Capacity must never be exceeded, ticket sales spike at launch, and check-in scanners hit the database hard at the venue door.</p>
<p><strong>Approach:</strong> Core tables are <code>events</code>, <code>ticket_types</code> (GA, VIP, early-bird with capacity and price), <code>tickets</code> (one row per issued seat with a unique code), <code>orders</code>, and <code>order_items</code>. Inventory is enforced atomically:</p>
<pre><code>CREATE TABLE ticket_types (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_id BIGINT NOT NULL,
  name VARCHAR(80),
  price_cents INT NOT NULL,
  capacity INT NOT NULL,
  sold INT NOT NULL DEFAULT 0,
  sale_starts_at DATETIME,
  sale_ends_at DATETIME,
  CONSTRAINT chk_sold CHECK (sold &lt;= capacity)
);

-- Reserve N seats atomically
UPDATE ticket_types
SET sold = sold + ?
WHERE id = ? AND sold + ? &lt;= capacity;

-- If affected_rows = 1, issue tickets
INSERT INTO tickets (event_id, ticket_type_id, order_id, code)
VALUES (?, ?, ?, ?);</code></pre>
<p>Each ticket has a unique scannable code (UUID v7 or signed token). Check-in writes a row to <code>ticket_scans</code>; a UNIQUE index on <code>ticket_id</code> prevents double entry.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Concern</th><th>Choice</th><th>Why</th></tr></thead><tbody>
<tr><td>Capacity</td><td>UPDATE with CHECK</td><td>Single round-trip, no oversell, no app-level race</td></tr>
<tr><td>Hot ticket launch</td><td>Queue + waiting room</td><td>Smooth 100k requests/sec to DB-friendly rate</td></tr>
<tr><td>QR scan latency</td><td>Index <code>tickets(code)</code> + Redis cache</td><td>Sub-50ms door scan even on flaky venue Wi-Fi</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Use <strong>Eventbrite</strong>, <strong>Universe</strong>, or <strong>Hopin</strong> if you don&rsquo;t want to build this; for ticketing infrastructure <strong>Tessitura</strong>, <strong>SeatGeek Open</strong>, or <strong>Spektrix</strong> are industry options. Implement waiting rooms with <strong>Cloudflare Waiting Room</strong> or <strong>Queue-it</strong> for high-demand drops. QR codes signed with HMAC prevent forgery. Stream check-ins through <strong>Kafka</strong> or <strong>Redpanda</strong> for live attendance dashboards. For NFT/blockchain tickets see <strong>GET Protocol</strong> or <strong>YellowHeart</strong>. Fraud detection via <strong>Sift</strong> or <strong>Stripe Radar</strong>.</p>'''

ANSWERS[77] = r'''<p><strong>Situation:</strong> A 10TB MySQL instance is straining storage budgets and backup windows. Most data is historical and rarely read but legally must be retained. The team needs compression and storage optimization without sacrificing query performance on hot data.</p>
<p><strong>Approach:</strong> Apply layered tactics. First, enable InnoDB page compression on cold tables, which uses zlib or LZ4 at the page level. Second, archive old partitions to compressed storage engines or external object storage. Third, normalize bloated columns and use appropriate types.</p>
<pre><code>-- Page compression on archive table (MySQL 8 with COMPRESSION attribute)
ALTER TABLE order_history
COMPRESSION='zlib';

-- Or transparent page compression on filesystem level
ALTER TABLE access_logs
ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;

-- Right-size types: INT(4 bytes) instead of BIGINT(8) when range fits
-- VARCHAR(255) is fine; CHAR(255) wastes space for variable data
-- Use ENUM or small lookup table instead of repeated VARCHAR strings

-- Move cold partitions to S3 via export
SELECT * FROM events_2022 INTO OUTFILE 's3://archive/2022.parquet'
FORMAT = 'PARQUET';
ALTER TABLE events DROP PARTITION p_2022;</code></pre>
<p>Schema-level wins: deduplicate repeated strings into lookup tables, store JSON as JSON type (compact binary) not TEXT, use VARBINARY for hashes instead of hex CHAR, and avoid SELECT-friendly NULL columns when DEFAULT 0 suffices.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Technique</th><th>Saves</th><th>Cost</th></tr></thead><tbody>
<tr><td>InnoDB page compression</td><td>40&ndash;70% disk</td><td>10&ndash;30% CPU on writes</td></tr>
<tr><td>Partition archive to S3 Parquet</td><td>90%+ for cold data</td><td>Slow ad-hoc queries on archived</td></tr>
<tr><td>Type tightening</td><td>10&ndash;30% rows</td><td>Schema migration risk</td></tr>
<tr><td>Move to ClickHouse/Druid</td><td>10x for analytics</td><td>Second system to operate</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Consider migrating analytical workloads to <strong>ClickHouse</strong>, <strong>StarRocks</strong>, or <strong>Apache Doris</strong> which offer 10x compression with columnar storage. For tiered storage on transactional data use <strong>TiDB</strong> with TiFlash or <strong>SingleStore</strong>. Backup tools like <strong>Percona XtraBackup</strong> or <strong>mysqldump</strong> with <code>--compress</code>. Cloud-native: <strong>Aurora</strong> auto-scales storage; <strong>PlanetScale</strong> handles compression internally. For archival, <strong>AWS S3 Glacier Deep Archive</strong> or <strong>Cloudflare R2</strong> with Parquet via <strong>Apache Iceberg</strong> or <strong>Delta Lake</strong> is cost-optimal.</p>'''

ANSWERS[78] = r'''<p><strong>Situation:</strong> A recruitment SaaS tracks job postings, candidate applications, multi-stage interviews, and feedback from interviewers. Hiring managers need a kanban pipeline view, recruiters need to schedule interviews, and the system must support thousands of concurrent companies.</p>
<p><strong>Approach:</strong> Tables: <code>companies</code>, <code>jobs</code>, <code>candidates</code>, <code>applications</code> (linking candidate to job with stage), <code>interviews</code> (scheduled events), <code>interview_feedback</code> (one per interviewer per interview), and <code>pipeline_stages</code> (configurable per company).</p>
<pre><code>CREATE TABLE applications (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  job_id BIGINT NOT NULL,
  candidate_id BIGINT NOT NULL,
  stage_id BIGINT NOT NULL,
  status ENUM('active','rejected','hired','withdrawn') DEFAULT 'active',
  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  position INT,  -- kanban order within stage
  UNIQUE KEY uniq_job_candidate (job_id, candidate_id),
  KEY idx_pipeline (job_id, stage_id, position)
);

CREATE TABLE interviews (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  application_id BIGINT NOT NULL,
  scheduled_at DATETIME NOT NULL,
  duration_min INT DEFAULT 60,
  meeting_url VARCHAR(500),
  status ENUM('scheduled','done','no_show','cancelled')
);

CREATE TABLE interview_feedback (
  interview_id BIGINT NOT NULL,
  interviewer_id BIGINT NOT NULL,
  rating TINYINT,  -- 1-4 strong no, no, yes, strong yes
  notes TEXT,
  submitted_at DATETIME,
  PRIMARY KEY (interview_id, interviewer_id)
);</code></pre>
<p>Stage transitions are logged in <code>application_history</code> for audit and analytics (time-in-stage, conversion rates).</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Configurable stages per company</td><td>Each company has unique hiring process</td></tr>
<tr><td>Position column on applications</td><td>Drag-drop kanban without renumbering</td></tr>
<tr><td>Separate interview_feedback table</td><td>Multi-interviewer panels with structured rubrics</td></tr>
<tr><td>UNIQUE(job_id, candidate_id)</td><td>One application per candidate per job</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Established ATSes are <strong>Greenhouse</strong>, <strong>Lever</strong>, <strong>Ashby</strong>, <strong>Workable</strong>, <strong>SmartRecruiters</strong>, and <strong>Recruitee</strong>. For sourcing: <strong>LinkedIn Recruiter</strong>, <strong>hireEZ</strong>, <strong>Gem</strong>. AI screening: <strong>Paradox Olivia</strong>, <strong>HireVue</strong>, <strong>Metaview</strong>, <strong>Pillar</strong>. Resume parsing: <strong>Affinda</strong>, <strong>Sovren</strong>, <strong>RChilli</strong>. Calendar integration via <strong>Google Calendar API</strong>, <strong>Microsoft Graph</strong>, or <strong>Cal.com</strong>. Video interviews via <strong>Zoom</strong>, <strong>Google Meet</strong>, <strong>CoderPad</strong>, <strong>HackerRank</strong>, or <strong>CodeSignal</strong>. Background checks: <strong>Checkr</strong>, <strong>Certn</strong>, <strong>Sterling</strong>.</p>'''

ANSWERS[79] = r'''<p><strong>Situation:</strong> Product wants to know DAU, MAU, retention curves, feature adoption, and funnel conversion. The site emits millions of events daily &mdash; clicks, page views, button presses. Storing every event in MySQL transactional tables would explode the OLTP database.</p>
<p><strong>Approach:</strong> Two-tier architecture. Capture raw events in a streaming pipeline; aggregate them into MySQL summary tables for fast dashboard reads. Avoid putting raw events in OLTP MySQL.</p>
<pre><code>-- MySQL holds aggregates, not raw events
CREATE TABLE daily_active_users (
  date DATE NOT NULL,
  user_id BIGINT NOT NULL,
  PRIMARY KEY (date, user_id)
);

CREATE TABLE feature_adoption (
  date DATE,
  feature_key VARCHAR(80),
  unique_users INT,
  total_events INT,
  PRIMARY KEY (date, feature_key)
);

CREATE TABLE funnel_step_counts (
  funnel_id BIGINT,
  date DATE,
  step INT,
  user_count INT,
  PRIMARY KEY (funnel_id, date, step)
);

-- Frontend sends events to ingestion endpoint
fetch('/track', { method: 'POST', body: JSON.stringify({
  user_id, event: 'checkout_started', properties: { plan: 'pro' }
})});</code></pre>
<p>The track endpoint writes to <strong>Kafka</strong> or <strong>Kinesis</strong>. A nightly job (or streaming via <strong>Flink</strong>/<strong>ksqlDB</strong>) computes aggregates and upserts into MySQL. Dashboards read summary tables in milliseconds.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Architecture</th><th>Pro</th><th>Con</th></tr></thead><tbody>
<tr><td>Raw events in MySQL</td><td>Simple, single system</td><td>Bloats DB, kills perf, terrible for OLAP</td></tr>
<tr><td>MySQL aggregates + warehouse</td><td>Fast dashboards, ad-hoc analysis available</td><td>Two systems</td></tr>
<tr><td>Pure SaaS (Mixpanel/Amplitude)</td><td>Zero infra</td><td>Cost scales with events, data lock-in</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> For event capture and analytics most teams use <strong>Mixpanel</strong>, <strong>Amplitude</strong>, <strong>Heap</strong>, <strong>PostHog</strong> (open source), or <strong>June</strong>. Pipeline tools: <strong>Segment</strong>, <strong>RudderStack</strong>, <strong>Snowplow</strong>, <strong>Jitsu</strong>. Warehouse the raw events in <strong>Snowflake</strong>, <strong>BigQuery</strong>, <strong>Databricks</strong>, or <strong>ClickHouse</strong>. Reverse-ETL with <strong>Hightouch</strong> or <strong>Census</strong> to push aggregates back to MySQL or Salesforce. Real-time product metrics via <strong>Statsig</strong> or <strong>GrowthBook</strong>. For session replay: <strong>FullStory</strong>, <strong>LogRocket</strong>, or <strong>Hotjar</strong>.</p>'''

ANSWERS[80] = r'''<p><strong>Situation:</strong> A real estate marketplace lists residential and commercial properties from agents and brokerages. Buyers search by location, price, beds/baths, and features. Listings expire, agents update prices, and the platform syncs MLS feeds. Map-based search must be fast.</p>
<p><strong>Approach:</strong> Tables: <code>properties</code> (the physical asset with address and coordinates), <code>listings</code> (a property may be listed multiple times over years), <code>agents</code>, <code>brokerages</code>, <code>property_features</code> (M2M to a feature dictionary), <code>media</code>, and <code>price_history</code>.</p>
<pre><code>CREATE TABLE properties (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  address_line VARCHAR(200),
  city VARCHAR(100),
  state CHAR(2),
  zip VARCHAR(10),
  lat DECIMAL(10,7),
  lng DECIMAL(10,7),
  property_type ENUM('single_family','condo','townhouse','multi','land','commercial'),
  beds TINYINT, baths DECIMAL(3,1),
  sqft INT, lot_sqft INT,
  year_built SMALLINT,
  KEY idx_geo (lat, lng),
  SPATIAL KEY idx_loc (location)  -- POINT column for spatial
);

CREATE TABLE listings (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  property_id BIGINT,
  agent_id BIGINT,
  list_price_cents BIGINT,
  status ENUM('active','pending','sold','withdrawn','expired'),
  listed_at DATETIME,
  closed_at DATETIME,
  mls_id VARCHAR(50),
  KEY idx_active (status, list_price_cents)
);

CREATE TABLE price_history (
  listing_id BIGINT,
  changed_at DATETIME,
  old_price BIGINT, new_price BIGINT,
  PRIMARY KEY (listing_id, changed_at)
);</code></pre>
<p>For map search, store a SPATIAL POINT and use <code>ST_Contains</code> or <code>MBRContains</code>. Or push search to a geo index outside MySQL.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Property vs listing split</td><td>Same home relisted years later keeps history</td></tr>
<tr><td>MySQL spatial vs Elasticsearch</td><td>ES handles map+filter+sort at scale better</td></tr>
<tr><td>price_history table</td><td>Show price drops, calculate market trends</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> For search at scale use <strong>Elasticsearch</strong>, <strong>OpenSearch</strong>, <strong>Algolia</strong>, or <strong>Typesense</strong> with geo filters and viewport queries. Map tiles from <strong>Mapbox</strong>, <strong>MapTiler</strong>, or <strong>Google Maps</strong>. MLS data sync via <strong>RESO Web API</strong>, <strong>Spark Platform</strong>, or aggregators like <strong>Bridge Interactive</strong>. AVM (automated valuation): <strong>HouseCanary</strong>, <strong>CoreLogic</strong>, <strong>Zillow Zestimate API</strong>. 3D tours: <strong>Matterport</strong>, <strong>Zillow 3D Home</strong>. Industry players: <strong>Zillow</strong>, <strong>Redfin</strong>, <strong>Compass</strong>, <strong>Realtor.com</strong>, <strong>HomeLight</strong>. CRM for agents: <strong>Follow Up Boss</strong>, <strong>kvCORE</strong>, <strong>Real Geeks</strong>.</p>'''

ANSWERS[81] = r'''<p><strong>Situation:</strong> A team deploys to production multiple times per day. Schema changes happen weekly &mdash; new columns, new tables, dropped indexes. The system must never have downtime, and rollbacks must be safe. Migrations cannot block long-running transactions.</p>
<p><strong>Approach:</strong> Use the <strong>expand-contract</strong> (parallel change) pattern with a versioned migration tool, online schema change tools for big tables, and feature flags to coordinate code with schema.</p>
<pre><code>-- Step 1 (expand): add new column nullable, deploy code that writes to BOTH
ALTER TABLE users ADD COLUMN email_lower VARCHAR(255);
-- Code writes both `email` and `email_lower` on every update.

-- Step 2: backfill in chunks (no big locks)
UPDATE users SET email_lower = LOWER(email)
WHERE email_lower IS NULL
LIMIT 1000;
-- Loop until 0 rows affected

-- Step 3: deploy code that reads from new column
-- Step 4 (contract): drop old column once safe
ALTER TABLE users DROP COLUMN email;</code></pre>
<p>For huge tables, use <strong>gh-ost</strong> or <strong>pt-online-schema-change</strong> which create a shadow copy and stream changes via binlog/triggers, then atomically swap. Migrations live in a versioned folder, with each file having an UP and DOWN script, applied by tools like <strong>Flyway</strong>, <strong>Liquibase</strong>, <strong>Atlas</strong>, <strong>Bytebase</strong>, or <strong>dbmate</strong>.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Pattern</th><th>Use when</th></tr></thead><tbody>
<tr><td>Inline ALTER (INSTANT)</td><td>Adding nullable column in MySQL 8</td></tr>
<tr><td>gh-ost / pt-osc</td><td>Big tables, can&rsquo;t afford metadata lock</td></tr>
<tr><td>Expand-contract</td><td>Renames, type changes, splitting columns</td></tr>
<tr><td>Feature flag + dual write</td><td>Coordinating multi-service rollouts</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Migration tools by stack: <strong>Flyway</strong>, <strong>Liquibase</strong>, <strong>Atlas</strong>, <strong>Bytebase</strong>, <strong>dbmate</strong>, <strong>Sqitch</strong>, <strong>Knex</strong>, <strong>TypeORM migrations</strong>, <strong>Prisma Migrate</strong>, <strong>Alembic</strong>, <strong>Goose</strong>, <strong>Diesel</strong>, <strong>Rails ActiveRecord</strong>, <strong>Django migrations</strong>. Online schema change at scale: <strong>gh-ost</strong> (GitHub), <strong>pt-online-schema-change</strong> (Percona), <strong>Spirit</strong>, <strong>OnlineDDL</strong>. Branch-per-PR schemas via <strong>PlanetScale branching</strong> or <strong>Neon branches</strong>. Schema review and CI: <strong>Skeema</strong>, <strong>Atlas Cloud</strong>, <strong>Bytebase SQL Review</strong>, <strong>Squawk</strong>. Always test rollbacks; many teams forbid destructive migrations in the same release as the code change.</p>'''

ANSWERS[82] = r'''<p><strong>Situation:</strong> A subscription news platform charges monthly or annually for premium articles. Subscribers expect uninterrupted access; failed payments need retries. Articles are metered (5 free per month) for unauthenticated readers and unlimited for subscribers.</p>
<p><strong>Approach:</strong> Tables: <code>publications</code>, <code>articles</code>, <code>subscribers</code>, <code>subscription_plans</code>, <code>subscriptions</code> (active subscription per subscriber), <code>invoices</code>, <code>article_views</code> (for metering and analytics).</p>
<pre><code>CREATE TABLE subscriptions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  subscriber_id BIGINT NOT NULL,
  plan_id BIGINT NOT NULL,
  status ENUM('trialing','active','past_due','cancelled','expired'),
  current_period_start DATE,
  current_period_end DATE,
  cancel_at_period_end BOOL DEFAULT FALSE,
  stripe_subscription_id VARCHAR(100),
  KEY idx_active (subscriber_id, status)
);

CREATE TABLE article_views (
  subscriber_id BIGINT NULL,
  visitor_token VARCHAR(64) NULL,
  article_id BIGINT NOT NULL,
  viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_visitor_month (visitor_token, viewed_at),
  KEY idx_article (article_id, viewed_at)
);

-- Paywall check: count anonymous views this month
SELECT COUNT(DISTINCT article_id) FROM article_views
WHERE visitor_token = ? AND viewed_at &gt;= DATE_FORMAT(NOW(),'%Y-%m-01');</code></pre>
<p>Subscription state changes are driven by webhooks from the payment processor. Failed charges retry on a schedule; after final failure, status moves to <code>past_due</code> then <code>cancelled</code>.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Stripe-managed billing</td><td>Don&rsquo;t reinvent dunning, taxes, prorations</td></tr>
<tr><td>Metering by visitor token</td><td>Cookie-based, GDPR-aware, no PII</td></tr>
<tr><td>Period dates on subscription</td><td>Fast access check without joining invoices</td></tr>
<tr><td>Soft paywall vs hard</td><td>SEO + sampling vs revenue protection</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Subscription billing: <strong>Stripe Billing</strong>, <strong>Chargebee</strong>, <strong>Recurly</strong>, <strong>Maxio</strong>, <strong>Paddle</strong> (Merchant of Record), <strong>Lemon Squeezy</strong>. Tax compliance via <strong>Stripe Tax</strong>, <strong>Avalara</strong>, or <strong>TaxJar</strong>. Newsletter platforms: <strong>Substack</strong>, <strong>Beehiiv</strong>, <strong>Ghost</strong>, <strong>Memberful</strong>, <strong>Pico</strong>. Paywall infra: <strong>Piano</strong>, <strong>Tinypass</strong>, <strong>Poool</strong>, <strong>LaterPay</strong>. Email delivery: <strong>SendGrid</strong>, <strong>Postmark</strong>, <strong>Resend</strong>, <strong>Customer.io</strong>. CDN with paywall edge logic via <strong>Cloudflare Workers</strong> or <strong>Fastly Compute</strong>. Reduce churn with <strong>ProsperStack</strong> or <strong>Churnkey</strong> cancellation flows.</p>'''

ANSWERS[83] = r'''<p><strong>Situation:</strong> An engineering team needs a tool to track sprints, tasks, bugs, releases, and time. Multiple projects, custom workflows, child tasks, and integrations with code (GitHub PRs link to issues). Reports show velocity, cycle time, and burndown.</p>
<p><strong>Approach:</strong> Tables: <code>projects</code>, <code>workflows</code> (per-project state machines), <code>states</code>, <code>issues</code>, <code>issue_links</code> (parent/child, blocks, duplicates), <code>sprints</code>, <code>sprint_issues</code>, <code>comments</code>, <code>worklogs</code>, <code>integrations</code>.</p>
<pre><code>CREATE TABLE issues (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_id BIGINT NOT NULL,
  issue_key VARCHAR(20) NOT NULL,  -- e.g., 'PROJ-1234'
  type ENUM('story','task','bug','epic','spike'),
  title VARCHAR(500),
  description MEDIUMTEXT,
  state_id BIGINT,
  assignee_id BIGINT,
  reporter_id BIGINT,
  priority ENUM('p0','p1','p2','p3','p4'),
  story_points TINYINT,
  parent_id BIGINT,
  created_at DATETIME, closed_at DATETIME,
  UNIQUE KEY uniq_key (project_id, issue_key),
  KEY idx_assignee_state (assignee_id, state_id)
);

CREATE TABLE state_transitions (
  issue_id BIGINT,
  from_state_id BIGINT,
  to_state_id BIGINT,
  changed_by BIGINT,
  changed_at DATETIME,
  PRIMARY KEY (issue_id, changed_at)
);

CREATE TABLE worklogs (
  issue_id BIGINT, user_id BIGINT,
  started_at DATETIME, minutes INT,
  PRIMARY KEY (issue_id, user_id, started_at)
);</code></pre>
<p><code>state_transitions</code> enables cycle time analytics (average time in &ldquo;in progress&rdquo;), velocity charts (story points completed per sprint), and bottleneck detection.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>State transitions table</td><td>Audit + cycle time + flow metrics</td></tr>
<tr><td>Custom workflow per project</td><td>Engineering vs design have different stages</td></tr>
<tr><td>issue_links table</td><td>Parent-child + blocks + duplicates without schema explosion</td></tr>
<tr><td>Search via Elasticsearch</td><td>MySQL full-text doesn&rsquo;t handle 1M issues with filters well</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Established players: <strong>Jira</strong>, <strong>Linear</strong>, <strong>Asana</strong>, <strong>ClickUp</strong>, <strong>Monday.com</strong>, <strong>Shortcut</strong>, <strong>Height</strong>, <strong>GitHub Projects</strong>, <strong>GitLab Issues</strong>, <strong>Plane</strong> (open source). Linear&rsquo;s data model is widely admired for speed. Code integration via <strong>GitHub webhooks</strong>, <strong>GitLab webhooks</strong>, <strong>Bitbucket Cloud</strong>. Roadmaps: <strong>ProductBoard</strong>, <strong>Aha!</strong>, <strong>Productlane</strong>. Engineering metrics: <strong>LinearB</strong>, <strong>Jellyfish</strong>, <strong>Swarmia</strong>, <strong>Sleuth</strong>. Real-time collaboration via <strong>Yjs</strong>, <strong>Liveblocks</strong>, or <strong>Replicache</strong> for offline-first like Linear.</p>'''

ANSWERS[84] = r'''<p><strong>Situation:</strong> A telehealth platform manages patients, doctors, appointments, prescriptions, and clinical notes. The system must comply with HIPAA, support insurance billing, and integrate with EHR systems. Doctors&rsquo; calendars must avoid double-booking.</p>
<p><strong>Approach:</strong> Tables: <code>patients</code>, <code>doctors</code> (and their <code>specialties</code>), <code>availability_slots</code>, <code>appointments</code>, <code>medical_records</code>, <code>prescriptions</code>, <code>insurance_claims</code>. PHI fields are encrypted at column level.</p>
<pre><code>CREATE TABLE doctors (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  npi CHAR(10) UNIQUE,  -- National Provider Identifier
  specialty_id BIGINT,
  license_state CHAR(2),
  user_id BIGINT
);

CREATE TABLE availability_slots (
  doctor_id BIGINT,
  starts_at DATETIME NOT NULL,
  ends_at DATETIME NOT NULL,
  PRIMARY KEY (doctor_id, starts_at)
);

CREATE TABLE appointments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  doctor_id BIGINT NOT NULL,
  patient_id BIGINT NOT NULL,
  starts_at DATETIME NOT NULL,
  ends_at DATETIME NOT NULL,
  type ENUM('in_person','video','phone'),
  status ENUM('scheduled','confirmed','completed','no_show','cancelled'),
  reason VARCHAR(500),
  UNIQUE KEY uniq_doctor_slot (doctor_id, starts_at),
  KEY idx_patient (patient_id, starts_at)
);

-- Booking with concurrency safety
INSERT INTO appointments (doctor_id, patient_id, starts_at, ends_at, ...)
VALUES (?, ?, ?, ?, ...);
-- UNIQUE KEY blocks double-booking; catch duplicate-key error to retry
</code></pre>
<p><code>medical_records</code> stores SOAP notes; sensitive fields encrypted with KMS-derived data keys. Audit log captures every access to PHI.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>UNIQUE on (doctor_id, starts_at)</td><td>Concurrent booking impossible</td></tr>
<tr><td>Column-level encryption</td><td>HIPAA defense-in-depth beyond TDE</td></tr>
<tr><td>Append-only audit log</td><td>Required for HIPAA access tracking</td></tr>
<tr><td>NPI as separate identifier</td><td>Industry-standard provider ID</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Telehealth platforms: <strong>Doximity</strong>, <strong>Doxy.me</strong>, <strong>Zoom for Healthcare</strong>, <strong>VSee</strong>. Backend services: <strong>Vital</strong>, <strong>Akute Health</strong>, <strong>Healthie</strong>, <strong>Mednet.io</strong>. EHR integration: <strong>Redox</strong>, <strong>Particle Health</strong>, <strong>Health Gorilla</strong>, <strong>1upHealth</strong>; FHIR-native: <strong>Medplum</strong>, <strong>Aidbox</strong>, <strong>Firely</strong>. ePrescribing: <strong>Surescripts</strong>, <strong>DoseSpot</strong>, <strong>Phreesia</strong>. Insurance verification: <strong>Stedi</strong>, <strong>Eligible</strong>, <strong>Change Healthcare</strong>. Payments: <strong>Stripe</strong> with <strong>Cedar</strong> or <strong>Inbox Health</strong> for patient billing. HIPAA-compliant infra: <strong>AWS BAA</strong>, <strong>Aptible</strong>, <strong>Vanta</strong> for compliance automation.</p>'''

ANSWERS[85] = r'''<p><strong>Situation:</strong> A high-traffic application sees 50k QPS, p99 latency creeping above 200ms, and CPU at 80%. Pages load slowly, especially the dashboard. The team needs a methodical approach to find and fix bottlenecks without over-engineering.</p>
<p><strong>Approach:</strong> Profile first; optimize second. Use Performance Schema, slow query log, and EXPLAIN to find the actual bottlenecks. Apply fixes layer by layer: query &rarr; index &rarr; schema &rarr; cache &rarr; replication &rarr; infrastructure.</p>
<pre><code>-- Find slowest queries
SELECT digest_text, count_star, avg_timer_wait/1e9 AS avg_ms,
       sum_rows_examined, sum_rows_sent
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC LIMIT 20;

-- Inspect a query
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) FROM users u
LEFT JOIN orders o ON u.id=o.user_id AND o.created_at &gt; NOW()-INTERVAL 30 DAY
WHERE u.region='US' GROUP BY u.id;

-- Common fixes
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);
ALTER TABLE orders DROP INDEX idx_unused;  -- unused indexes hurt writes
SET GLOBAL innodb_buffer_pool_size = 32 * 1024 * 1024 * 1024;</code></pre>
<p>Top wins typically: missing indexes, queries returning too much data (no LIMIT or wide SELECT *), N+1 in app, undersized buffer pool, lock contention from long transactions, and sending heavy reads to the primary instead of replicas.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Layer</th><th>Wins</th><th>Cost</th></tr></thead><tbody>
<tr><td>Index tuning</td><td>10&ndash;100x specific queries</td><td>Slower writes if too many</td></tr>
<tr><td>Read replicas</td><td>Linear read scaling</td><td>Replica lag, app routing</td></tr>
<tr><td>Caching (Redis)</td><td>Removes DB load entirely for hot keys</td><td>Invalidation complexity</td></tr>
<tr><td>Materialized views</td><td>Cheap dashboards</td><td>Staleness, refresh cost</td></tr>
<tr><td>Vertical scaling</td><td>Quick relief</td><td>Cost, eventually hits ceiling</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Profiling: <strong>Performance Schema</strong>, <strong>sys schema</strong>, <strong>pt-query-digest</strong>, <strong>SolarWinds DPA</strong>, <strong>Percona PMM</strong>, <strong>VividCortex</strong> (now SolarWinds). APM that connects DB to app traces: <strong>Datadog APM</strong>, <strong>New Relic</strong>, <strong>Dynatrace</strong>, <strong>Honeycomb</strong>, <strong>Sentry</strong>, <strong>Grafana Cloud</strong>. AI-driven query optimization: <strong>EverSQL</strong>, <strong>Ottertune</strong>. Caching layers: <strong>Redis</strong>, <strong>Dragonfly</strong>, <strong>KeyDB</strong>, <strong>Memcached</strong>, <strong>ElastiCache</strong>. CDN cache for read APIs: <strong>Cloudflare</strong>, <strong>Fastly</strong>. For sustained extreme load consider <strong>PlanetScale</strong>, <strong>Vitess</strong>, <strong>TiDB</strong>, or <strong>SingleStore</strong>.</p>'''

ANSWERS[86] = r'''<p><strong>Situation:</strong> A Spotify-like music streaming service stores users, songs, albums, artists, playlists, and listening history. Users build playlists, follow artists, and get personalized mixes. Royalty calculations require accurate per-stream play counts attributed to rights holders.</p>
<p><strong>Approach:</strong> Tables: <code>artists</code>, <code>albums</code>, <code>songs</code>, <code>users</code>, <code>playlists</code>, <code>playlist_songs</code>, <code>follows</code>, <code>plays</code> (every play is a row, append-only), <code>likes</code>, and <code>rights_holders</code>.</p>
<pre><code>CREATE TABLE songs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  album_id BIGINT,
  primary_artist_id BIGINT,
  isrc CHAR(12) UNIQUE,  -- International Standard Recording Code
  title VARCHAR(300),
  duration_ms INT,
  audio_url_hls VARCHAR(500),
  explicit BOOL DEFAULT FALSE,
  release_date DATE,
  KEY idx_artist (primary_artist_id)
);

CREATE TABLE song_artists (
  song_id BIGINT, artist_id BIGINT,
  role ENUM('primary','featured','producer','writer'),
  PRIMARY KEY (song_id, artist_id, role)
);

CREATE TABLE playlists (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  owner_id BIGINT,
  name VARCHAR(200),
  is_public BOOL DEFAULT TRUE,
  KEY idx_owner (owner_id)
);

CREATE TABLE playlist_songs (
  playlist_id BIGINT, position INT,
  song_id BIGINT,
  added_at DATETIME,
  PRIMARY KEY (playlist_id, position)
);

-- Plays go to a separate event store (Kafka -&gt; warehouse)
CREATE TABLE plays_daily_summary (
  date DATE, song_id BIGINT, country CHAR(2),
  play_count INT, paid_play_count INT,
  PRIMARY KEY (date, song_id, country)
);</code></pre>
<p>Raw plays should not live in MySQL OLTP &mdash; they go to Kafka and stream into a warehouse for royalty calculation. MySQL holds aggregates.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Plays in event store, not MySQL</td><td>Billions of rows would crush OLTP</td></tr>
<tr><td>ISRC as natural key</td><td>Industry-standard, deduplicates re-uploads</td></tr>
<tr><td>song_artists with role</td><td>Featured, producer, writer all rep&rsquo;d</td></tr>
<tr><td>Audio served via HLS/DASH from CDN</td><td>Adaptive bitrate, geo-edge delivery</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Streaming infrastructure: <strong>JW Player</strong>, <strong>BoomBox</strong>, <strong>Mux</strong> (video but adapts), <strong>AWS MediaConvert</strong>. Royalty/rights: <strong>SoundExchange</strong>, <strong>SourceAudio</strong>, <strong>Roex</strong>, <strong>Curve Royalty Systems</strong>, <strong>Vistex</strong>. Aggregators for indie release: <strong>DistroKid</strong>, <strong>TuneCore</strong>, <strong>CD Baby</strong>, <strong>Symphonic</strong>, <strong>Believe</strong>. Recommendations: collaborative filtering with <strong>Spotify Annoy</strong>, two-tower models on <strong>TensorFlow Recommenders</strong>, <strong>Vespa</strong> for retrieval. Audio fingerprinting: <strong>ACRCloud</strong>, <strong>Pex</strong>, <strong>AudibleMagic</strong>. Industry products: <strong>Spotify</strong>, <strong>Apple Music</strong>, <strong>YouTube Music</strong>, <strong>Tidal</strong>, <strong>Amazon Music</strong>, <strong>Deezer</strong>, <strong>SoundCloud</strong>.</p>'''

ANSWERS[87] = r'''<p><strong>Situation:</strong> A multi-tenant SaaS app needs fine-grained access control. Some users are admins of their org, some can edit specific projects, some are read-only. Permissions can be inherited (folder permissions cascade to documents). Performance must remain fast even with millions of authorization checks per minute.</p>
<p><strong>Approach:</strong> Combine RBAC for coarse roles with policy-based or relationship-based authorization for fine-grained checks. Cache decisions aggressively because authz reads dwarf writes.</p>
<pre><code>CREATE TABLE roles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(80) UNIQUE  -- 'admin','editor','viewer'
);

CREATE TABLE permissions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  action VARCHAR(80),       -- 'document.edit'
  resource_type VARCHAR(80) -- 'document','project'
);

CREATE TABLE role_permissions (
  role_id BIGINT, permission_id BIGINT,
  PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
  user_id BIGINT,
  role_id BIGINT,
  scope_type VARCHAR(40),  -- 'org','project','document'
  scope_id BIGINT,
  PRIMARY KEY (user_id, role_id, scope_type, scope_id)
);

-- Resource sharing for ReBAC (relationship-based)
CREATE TABLE acl_entries (
  resource_type VARCHAR(40),
  resource_id BIGINT,
  subject_type VARCHAR(40),  -- 'user' or 'group'
  subject_id BIGINT,
  relation VARCHAR(40),      -- 'owner','editor','viewer'
  PRIMARY KEY (resource_type, resource_id, subject_type, subject_id, relation)
);

-- Authz check (after caching layer miss)
SELECT 1 FROM acl_entries
WHERE resource_type='doc' AND resource_id=? AND subject_id=? AND relation IN ('owner','editor');</code></pre>
<p>For Google Drive&ndash;style cascading permissions or huge graphs, consider a dedicated authorization service modeled after Google Zanzibar.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Model</th><th>Best for</th><th>Limit</th></tr></thead><tbody>
<tr><td>Pure RBAC</td><td>Few roles, simple apps</td><td>Can&rsquo;t express &ldquo;Bob can edit only doc-42&rdquo;</td></tr>
<tr><td>RBAC + scope</td><td>Multi-tenant SaaS</td><td>Verbose for sharing</td></tr>
<tr><td>ABAC (policy)</td><td>Complex rules over attributes</td><td>Hard to debug</td></tr>
<tr><td>ReBAC (Zanzibar)</td><td>Doc-sharing, social graphs</td><td>Operational complexity</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Authorization-as-a-service: <strong>SpiceDB</strong> (AuthZed), <strong>OpenFGA</strong> (Auth0), <strong>Permify</strong>, <strong>Oso</strong>, <strong>Cerbos</strong>, <strong>Topaz</strong>, <strong>Aserto</strong>, <strong>Warrant</strong>, <strong>Permit.io</strong>. Library options: <strong>Casbin</strong> (multi-language), <strong>CASL</strong> (JS), <strong>Pundit</strong>/<strong>CanCanCan</strong> (Ruby), <strong>django-guardian</strong>. Identity: <strong>Auth0</strong>, <strong>Okta</strong>, <strong>WorkOS</strong>, <strong>Stytch</strong>, <strong>Clerk</strong>, <strong>Frontegg</strong>, <strong>Kinde</strong> handle SSO/SAML/SCIM. Audit logging via <strong>Tinybird</strong>, <strong>Honeycomb</strong>, or store in append-only <strong>S3 Object Lock</strong>. For session and token caching: <strong>Redis</strong> or in-process LRU.</p>'''

ANSWERS[88] = r'''<p><strong>Situation:</strong> A retail loyalty program awards points for purchases, lets customers redeem points for rewards, and tiers customers (silver/gold/platinum) based on annual spend. Points expire if unused; reward redemption must be atomic so a customer can&rsquo;t double-redeem.</p>
<p><strong>Approach:</strong> Tables: <code>customers</code>, <code>tiers</code>, <code>point_ledger</code> (every credit/debit, append-only), <code>rewards</code>, <code>redemptions</code>. Balance is always derived by SUM over the ledger; never stored as a single mutable balance.</p>
<pre><code>CREATE TABLE point_ledger (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id BIGINT NOT NULL,
  delta INT NOT NULL,            -- +earn, -redeem, -expire
  reason ENUM('purchase','redeem','expire','adjustment','bonus'),
  reference_id BIGINT,           -- order_id or redemption_id
  expires_at DATETIME NULL,      -- earn rows have an expiry
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_customer (customer_id, created_at)
);

-- Current balance
SELECT COALESCE(SUM(delta), 0) AS balance
FROM point_ledger
WHERE customer_id = ?
  AND (expires_at IS NULL OR expires_at &gt; NOW());

-- Atomic redemption: serialized via row lock on customer
START TRANSACTION;
SELECT COALESCE(SUM(delta),0) FROM point_ledger
  WHERE customer_id = ? FOR UPDATE;  -- locks customer row in customers
-- Validate balance &gt;= cost, then insert
INSERT INTO redemptions (customer_id, reward_id, points_cost) VALUES (?, ?, ?);
INSERT INTO point_ledger (customer_id, delta, reason, reference_id)
  VALUES (?, -?, 'redeem', LAST_INSERT_ID());
COMMIT;</code></pre>
<p>Points expire FIFO; a nightly job inserts <code>expire</code> entries equal to negative of expired earn rows. Tier is recomputed monthly from rolling 12-month spend.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Ledger over balance column</td><td>Audit, dispute resolution, replay</td></tr>
<tr><td>FIFO expiry</td><td>Standard accounting, customer-friendly</td></tr>
<tr><td>Cached balance with version</td><td>Fast reads, recompute on miss</td></tr>
<tr><td>Tier from rolling window</td><td>Customers don&rsquo;t lose status mid-year</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Loyalty platforms: <strong>Smile.io</strong>, <strong>Yotpo</strong>, <strong>Stamped</strong>, <strong>LoyaltyLion</strong>, <strong>Annex Cloud</strong>, <strong>Punchh</strong>, <strong>Open Loyalty</strong> (open source). Enterprise: <strong>Salesforce Loyalty Management</strong>, <strong>Cheetah Digital</strong>, <strong>Comarch</strong>. Card-linked offers: <strong>Fidel API</strong>, <strong>Triple</strong>, <strong>Augeo</strong>. For coalition/cross-merchant programs see <strong>Plenti</strong> patterns or <strong>StellarFi</strong>. Fraud prevention via <strong>Forter</strong> or <strong>Sift</strong>. For point-based payment redemption use <strong>Kard</strong>. Marketing automation tied to tier transitions: <strong>Braze</strong>, <strong>Iterable</strong>, <strong>Customer.io</strong>.</p>'''

ANSWERS[89] = r'''<p><strong>Situation:</strong> A team has been bitten by orphan rows, mismatched currencies, malformed emails, and silently corrupt data. They want to push validation into the database where possible so bad data can never land, regardless of which app or job writes it.</p>
<p><strong>Approach:</strong> Use the strongest constraints the database offers: NOT NULL, FOREIGN KEY, UNIQUE, CHECK constraints (MySQL 8.0.16+), correct data types, and ENUM/lookup tables for restricted values. Backstop with triggers for cross-row invariants and add app-layer validation for UX.</p>
<pre><code>CREATE TABLE orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id BIGINT NOT NULL,
  email VARCHAR(255) NOT NULL,
  total_cents INT NOT NULL,
  currency CHAR(3) NOT NULL,
  status ENUM('pending','paid','refunded') NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_total CHECK (total_cents &gt;= 0),
  CONSTRAINT chk_email CHECK (email LIKE '%_@_%._%'),
  CONSTRAINT chk_currency CHECK (currency IN ('USD','EUR','GBP','JPY','INR')),
  CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- For invariants spanning rows (e.g., line totals = order total)
DELIMITER $$
CREATE TRIGGER trg_validate_order BEFORE UPDATE ON orders
FOR EACH ROW
BEGIN
  IF NEW.status = 'paid' AND NEW.paid_at IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'paid status requires paid_at';
  END IF;
END$$
DELIMITER ;</code></pre>
<p>Use <code>generated columns</code> for derived data, <code>SET sql_mode='STRICT_ALL_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'</code> to refuse silent truncation, and monitor with periodic data quality checks.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Layer</th><th>Catches</th><th>Cost</th></tr></thead><tbody>
<tr><td>Type / NOT NULL / FK / UNIQUE</td><td>Most schema bugs</td><td>None &mdash; use freely</td></tr>
<tr><td>CHECK constraint</td><td>Range, format, enum-like rules</td><td>Hard to debug rejections</td></tr>
<tr><td>Trigger</td><td>Cross-row invariants</td><td>Hidden logic, harder to test</td></tr>
<tr><td>App-layer validation (Zod/Yup/Pydantic)</td><td>UX errors before DB hit</td><td>Must be duplicated across services</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> App-side schema validators: <strong>Zod</strong>, <strong>Yup</strong>, <strong>Joi</strong>, <strong>Valibot</strong>, <strong>ArkType</strong>, <strong>TypeBox</strong> (TS); <strong>Pydantic</strong>, <strong>marshmallow</strong>, <strong>attrs</strong> (Python); <strong>JSON Schema</strong> universally. ORM-level: <strong>Prisma</strong>, <strong>Drizzle</strong>, <strong>TypeORM</strong>, <strong>Sequelize</strong>, <strong>SQLAlchemy</strong>, <strong>Hibernate</strong>. Data quality monitoring: <strong>Great Expectations</strong>, <strong>Soda</strong>, <strong>Monte Carlo</strong>, <strong>Bigeye</strong>, <strong>Datafold</strong>, <strong>Elementary</strong>, <strong>Anomalo</strong>. Schema linting: <strong>Atlas</strong>, <strong>Squawk</strong>, <strong>Skeema</strong>. For generated columns and computed fields, MySQL 8 supports both VIRTUAL and STORED options.</p>'''

ANSWERS[90] = r'''<p><strong>Situation:</strong> A fitness app helps users follow workout plans, log sets and reps, track progress over time, and see graphs of strength gains. Plans have weekly programs; users substitute exercises; the app must compute one-rep max estimates and personal records.</p>
<p><strong>Approach:</strong> Tables: <code>exercises</code>, <code>workout_plans</code>, <code>plan_workouts</code>, <code>plan_workout_exercises</code>, <code>user_workouts</code> (instances of executing a planned workout), <code>logged_sets</code>, and <code>personal_records</code>.</p>
<pre><code>CREATE TABLE exercises (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(150),
  muscle_group VARCHAR(60),
  equipment VARCHAR(60),
  is_compound BOOL
);

CREATE TABLE user_workouts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  plan_workout_id BIGINT,
  performed_at DATETIME NOT NULL,
  duration_min INT,
  KEY idx_user_date (user_id, performed_at)
);

CREATE TABLE logged_sets (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_workout_id BIGINT NOT NULL,
  exercise_id BIGINT NOT NULL,
  set_number TINYINT,
  reps SMALLINT,
  weight_kg DECIMAL(6,2),
  rpe DECIMAL(3,1),  -- rate of perceived exertion 1-10
  est_1rm_kg DECIMAL(6,2) AS (weight_kg * (1 + reps/30.0)) STORED,  -- Epley
  KEY idx_workout (user_workout_id),
  KEY idx_user_ex (exercise_id, user_workout_id)
);

-- 1RM trend per exercise
SELECT DATE(uw.performed_at) AS d, MAX(ls.est_1rm_kg) AS top_1rm
FROM logged_sets ls JOIN user_workouts uw ON ls.user_workout_id=uw.id
WHERE uw.user_id=? AND ls.exercise_id=?
GROUP BY DATE(uw.performed_at) ORDER BY d;</code></pre>
<p>Estimated 1RM is a generated column using the Epley formula. Personal records are recomputed when a new set logs a higher est_1rm than the existing PR.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Generated 1RM column</td><td>Always in sync with reps/weight, indexed</td></tr>
<tr><td>Plan vs instance separation</td><td>Plans evolve; logged history is immutable</td></tr>
<tr><td>RPE captured</td><td>Modern training programs need fatigue data</td></tr>
<tr><td>Substitutions tracked</td><td>Users swap exercises; plan integrity preserved</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Established apps: <strong>Strong</strong>, <strong>Hevy</strong>, <strong>FitNotes</strong>, <strong>Jefit</strong>, <strong>Fitbod</strong>, <strong>Future</strong>, <strong>Caliber</strong>, <strong>Apple Fitness+</strong>. AI-driven coaching: <strong>Fitbod</strong>, <strong>JuggernautAI</strong>, <strong>RP Strength</strong>, <strong>Boostcamp</strong>. Wearable data: <strong>Apple HealthKit</strong>, <strong>Google Health Connect</strong>, <strong>Garmin Connect API</strong>, <strong>Whoop</strong>, <strong>Oura</strong>, <strong>Fitbit Web API</strong>; aggregators: <strong>Terra</strong>, <strong>Vital</strong>, <strong>Spike</strong>, <strong>Rook</strong>. Video form analysis: <strong>Forme</strong>, <strong>Tempo</strong>, <strong>Tonal</strong>. Supplement and macro tracking: <strong>MacroFactor</strong>, <strong>MyFitnessPal</strong>, <strong>Cronometer</strong>. Group community via <strong>Tribe</strong>, <strong>Circle</strong>, or <strong>Discourse</strong>.</p>'''

ANSWERS[91] = r'''<p><strong>Situation:</strong> A product team needs to collect customer feedback (NPS, CSAT, free-text reviews), track sentiment over time, route negative reviews to support, and publish high-quality reviews on the public site. Spam and fake reviews must be filtered.</p>
<p><strong>Approach:</strong> Tables: <code>surveys</code>, <code>survey_responses</code>, <code>reviews</code> (product/seller reviews with rating + text), <code>review_media</code>, <code>review_reactions</code> (helpful/not helpful), and <code>moderation_queue</code>.</p>
<pre><code>CREATE TABLE reviews (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  order_id BIGINT,             -- verified purchase
  rating TINYINT NOT NULL,     -- 1-5
  title VARCHAR(200),
  body TEXT,
  status ENUM('pending','approved','rejected','flagged') DEFAULT 'pending',
  is_verified BOOL DEFAULT FALSE,
  helpful_count INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),
  UNIQUE KEY uniq_user_product (user_id, product_id),
  KEY idx_product (product_id, status, created_at)
);

CREATE TABLE survey_responses (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  survey_id BIGINT, user_id BIGINT,
  nps_score TINYINT,           -- 0-10
  csat_score TINYINT,          -- 1-5
  comment TEXT,
  sentiment_score DECIMAL(4,3),-- -1 to 1 (filled by ML)
  submitted_at DATETIME,
  KEY idx_survey_date (survey_id, submitted_at)
);

-- Aggregate product rating for product page
SELECT AVG(rating), COUNT(*) FROM reviews
WHERE product_id=? AND status='approved';</code></pre>
<p>Sentiment is computed asynchronously by a worker that calls an LLM or sentiment model. Negative scores trigger a Slack alert and create a support ticket automatically.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Order-linked verified purchase</td><td>Higher trust, less spam</td></tr>
<tr><td>UNIQUE per user-product</td><td>One review per buyer; allow edit</td></tr>
<tr><td>Async sentiment</td><td>LLM calls cost too much for sync write</td></tr>
<tr><td>Moderation queue</td><td>Human review for borderline / flagged content</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Review platforms: <strong>Yotpo</strong>, <strong>Trustpilot</strong>, <strong>Bazaarvoice</strong>, <strong>PowerReviews</strong>, <strong>Stamped</strong>, <strong>Junip</strong>, <strong>Loox</strong>, <strong>Okendo</strong>, <strong>REVIEWS.io</strong>. NPS/survey: <strong>Delighted</strong>, <strong>SurveyMonkey</strong>, <strong>Typeform</strong>, <strong>Qualtrics</strong>, <strong>AskNicely</strong>, <strong>Chattermill</strong>. AI feedback analysis: <strong>Viable</strong>, <strong>Enterpret</strong>, <strong>Unwrap.ai</strong>, <strong>Thematic</strong>, <strong>Idiomatic</strong>, <strong>SuperKlear</strong>. Spam/fake review detection: <strong>Fakespot</strong> (acquired by Mozilla), <strong>The Transparency Company</strong>, in-house GPT-4/Claude classifier. Support ticket creation via <strong>Zendesk</strong>, <strong>Intercom</strong>, <strong>Freshdesk</strong>, <strong>Linear</strong>, or <strong>Plain</strong>.</p>'''

ANSWERS[92] = r'''<p><strong>Situation:</strong> An online auction platform like eBay must handle bid placement under heavy concurrency at the closing minute (sniping), prevent shill bidding, support buy-it-now and reserve prices, and end auctions atomically without leaving inconsistent state.</p>
<p><strong>Approach:</strong> Tables: <code>users</code>, <code>auctions</code>, <code>bids</code>, <code>watches</code>. Bid acceptance is atomic and uses optimistic concurrency or row-level locks; the highest bid is denormalized on the auction row for fast reads but always derived consistently.</p>
<pre><code>CREATE TABLE auctions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  seller_id BIGINT NOT NULL,
  title VARCHAR(300),
  starts_at DATETIME, ends_at DATETIME,
  start_price_cents INT NOT NULL,
  reserve_cents INT,
  buy_it_now_cents INT,
  current_bid_cents INT,
  current_bidder_id BIGINT,
  bid_count INT DEFAULT 0,
  status ENUM('scheduled','live','ended','cancelled'),
  KEY idx_live_end (status, ends_at)
);

CREATE TABLE bids (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  auction_id BIGINT NOT NULL,
  bidder_id BIGINT NOT NULL,
  amount_cents INT NOT NULL,
  proxy_max_cents INT,        -- automatic bidding cap
  placed_at DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
  KEY idx_auction_amount (auction_id, amount_cents DESC)
);

-- Place bid atomically
START TRANSACTION;
SELECT current_bid_cents, ends_at, status FROM auctions
  WHERE id=? FOR UPDATE;
-- Validate: status='live', NOW() &lt; ends_at, new_bid &gt; current+min_increment
INSERT INTO bids (auction_id, bidder_id, amount_cents, proxy_max_cents)
  VALUES (?, ?, ?, ?);
UPDATE auctions
  SET current_bid_cents=?, current_bidder_id=?,
      bid_count=bid_count+1,
      ends_at = IF(TIMESTAMPDIFF(SECOND, NOW(), ends_at) &lt; 300,
                   DATE_ADD(NOW(), INTERVAL 5 MINUTE), ends_at)
  WHERE id=?;
COMMIT;</code></pre>
<p>The <code>ends_at</code> auto-extension prevents last-second sniping. A scheduled job ends auctions whose <code>ends_at</code> has passed.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Row lock on auction</td><td>Strict ordering, no double-winner</td></tr>
<tr><td>Anti-snipe extension</td><td>Fairer outcomes, higher final prices</td></tr>
<tr><td>Proxy bidding column</td><td>System auto-bids up to user&rsquo;s max</td></tr>
<tr><td>Denorm current bid</td><td>Listing pages don&rsquo;t scan bids table</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Marketplace platforms: <strong>eBay</strong>, <strong>StockX</strong>, <strong>GOAT</strong>, <strong>Whatnot</strong>, <strong>Heritage Auctions</strong>, <strong>Sotheby&rsquo;s</strong>, <strong>Christie&rsquo;s LIVE</strong>, <strong>Catawiki</strong>, <strong>Hibid</strong>. Live-stream auction tech: <strong>Whatnot</strong>, <strong>Bambuser</strong>, <strong>NTWRK</strong>, <strong>ShopShops</strong>. Real-time bid updates via <strong>WebSockets</strong> through <strong>Pusher</strong>, <strong>Ably</strong>, <strong>PartyKit</strong>, or <strong>Soketi</strong>. Fraud and shill detection: <strong>Sift</strong>, <strong>Forter</strong>, <strong>Riskified</strong>. Payment escrow: <strong>Escrow.com</strong>, <strong>Trustap</strong>, <strong>Stripe Connect</strong>. Authentication services for collectibles: <strong>PSA</strong>, <strong>Beckett</strong>, <strong>Authentic First</strong>, <strong>Real Authentication</strong>.</p>'''

ANSWERS[93] = r'''<p><strong>Situation:</strong> A business-critical MySQL instance must survive hardware failure, AZ outage, and even region outage with minimal data loss. The team has SLAs of 99.99% uptime, RPO under 60 seconds, and RTO under 5 minutes.</p>
<p><strong>Approach:</strong> Use semi-synchronous replication or Group Replication for high availability within a region; use asynchronous cross-region replicas for DR. Pair with an automated failover orchestrator and regularly tested DR drills.</p>
<pre><code>-- Primary configuration
[mysqld]
log_bin = mysql-bin
binlog_format = ROW
gtid_mode = ON
enforce_gtid_consistency = ON
sync_binlog = 1
innodb_flush_log_at_trx_commit = 1
rpl_semi_sync_master_enabled = 1
rpl_semi_sync_master_timeout = 10000  -- ms

-- Replica
rpl_semi_sync_slave_enabled = 1
relay_log_recovery = ON
read_only = ON
super_read_only = ON

-- Failover with Orchestrator (open source by Shlomi Noach)
-- orchestrator detects primary failure, promotes most up-to-date replica,
-- repoints other replicas, and updates the application&rsquo;s VIP/DNS.</code></pre>
<p>Application connects via a connection layer (ProxySQL, RDS Proxy, PlanetScale) that knows the current primary. Backups via Percona XtraBackup are taken on a delayed replica plus point-in-time recovery from binlogs.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Topology</th><th>RPO</th><th>RTO</th><th>Notes</th></tr></thead><tbody>
<tr><td>Async replica</td><td>Seconds &ndash; minutes</td><td>Minutes</td><td>Cheap, simple, possible data loss</td></tr>
<tr><td>Semi-sync</td><td>~0 (commit acked by replica)</td><td>Minutes</td><td>Slightly higher latency</td></tr>
<tr><td>Group Replication</td><td>Strong consistency</td><td>Seconds</td><td>3+ nodes, network sensitive</td></tr>
<tr><td>Aurora multi-AZ</td><td>Near-zero</td><td>~30 seconds</td><td>Storage replicated 6x across 3 AZs</td></tr>
<tr><td>Aurora Global / Vitess</td><td>~1s cross-region</td><td>Minutes</td><td>For region-failure DR</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Failover orchestration: <strong>Orchestrator</strong>, <strong>MHA</strong>, <strong>MySQL Router</strong> + InnoDB Cluster, <strong>ProxySQL</strong>, <strong>HAProxy</strong>. Cloud-managed HA: <strong>Amazon Aurora</strong>, <strong>Google Cloud SQL</strong>, <strong>Azure Database for MySQL Flexible Server</strong>, <strong>PlanetScale</strong>, <strong>Vitess</strong>, <strong>TiDB</strong>, <strong>SingleStore</strong>. Backups: <strong>Percona XtraBackup</strong>, <strong>mydumper</strong>, <strong>mysqldump</strong>, <strong>AWS Backup</strong>. PITR + WAL/binlog archiving to S3. Regularly run game-day chaos engineering with <strong>Gremlin</strong>, <strong>ChaosMesh</strong>, or <strong>AWS FIS</strong> to validate runbooks. Status pages and alerting: <strong>Atlassian Statuspage</strong>, <strong>Better Stack</strong>, <strong>Datadog</strong>, <strong>PagerDuty</strong>, <strong>Incident.io</strong>, <strong>FireHydrant</strong>, <strong>Rootly</strong>.</p>'''

ANSWERS[94] = r'''<p><strong>Situation:</strong> A weather monitoring system collects readings from 100,000 sensors every minute &mdash; temperature, humidity, pressure, wind. Operators need real-time alerts on anomalies, historical analytics, and a public API for forecast services. The naive approach of one row per reading would be 144 million rows per day.</p>
<p><strong>Approach:</strong> This is a classic time-series workload; MySQL is not the best store for raw points but can manage with aggressive partitioning and aggregates. Better is to send readings to a time-series DB and keep MySQL for metadata and pre-computed aggregates.</p>
<pre><code>-- Metadata in MySQL
CREATE TABLE locations (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(200), country CHAR(2),
  lat DECIMAL(10,7), lng DECIMAL(10,7),
  elevation_m INT
);

CREATE TABLE sensors (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  location_id BIGINT,
  type ENUM('temperature','humidity','pressure','wind','precipitation'),
  unit VARCHAR(20),
  installed_at DATE
);

-- Aggregated readings in MySQL (raw stays in TSDB)
CREATE TABLE readings_hourly (
  sensor_id BIGINT NOT NULL,
  hour DATETIME NOT NULL,
  min_value DOUBLE, max_value DOUBLE,
  avg_value DOUBLE, sample_count INT,
  PRIMARY KEY (sensor_id, hour)
)
PARTITION BY RANGE (TO_DAYS(hour)) (
  PARTITION p_2026_04 VALUES LESS THAN (TO_DAYS('2026-05-01')),
  PARTITION p_2026_05 VALUES LESS THAN (TO_DAYS('2026-06-01')),
  PARTITION p_max VALUES LESS THAN MAXVALUE
);

-- Anomaly check: 3-sigma over last 24h
SELECT sensor_id FROM readings_hourly
WHERE hour &gt;= NOW() - INTERVAL 24 HOUR
GROUP BY sensor_id
HAVING ABS(MAX(avg_value) - AVG(avg_value)) &gt; 3*STDDEV(avg_value);</code></pre>
<p>Raw 1-minute readings are written to <strong>TimescaleDB</strong>, <strong>InfluxDB</strong>, <strong>QuestDB</strong>, <strong>VictoriaMetrics</strong>, or <strong>Prometheus</strong>. A Flink/Materialize job rolls them up into MySQL hourly summaries.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Store</th><th>Pro</th><th>Con</th></tr></thead><tbody>
<tr><td>MySQL only</td><td>Single system</td><td>Bloats, slow scans, no compression</td></tr>
<tr><td>MySQL + TSDB</td><td>Right tool per workload</td><td>Two systems, sync glue</td></tr>
<tr><td>ClickHouse for everything</td><td>Cheap, fast columnar</td><td>Weaker for OLTP-style writes</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Time-series databases: <strong>TimescaleDB</strong> (Postgres extension), <strong>InfluxDB 3.0</strong>, <strong>QuestDB</strong>, <strong>VictoriaMetrics</strong>, <strong>Prometheus</strong>, <strong>M3</strong>, <strong>Mimir</strong>. Columnar analytics: <strong>ClickHouse</strong>, <strong>StarRocks</strong>, <strong>Apache Druid</strong>, <strong>Apache Pinot</strong>. IoT ingestion: <strong>AWS IoT Core</strong>, <strong>Azure IoT Hub</strong>, <strong>Google Cloud IoT</strong>, <strong>Kafka</strong>, <strong>Redpanda</strong>, <strong>NATS</strong>. Stream processing: <strong>Apache Flink</strong>, <strong>Materialize</strong>, <strong>RisingWave</strong>, <strong>Bytewax</strong>. Visualization: <strong>Grafana</strong>, <strong>Apache Superset</strong>, <strong>Metabase</strong>. Weather APIs to compare against: <strong>OpenWeather</strong>, <strong>Tomorrow.io</strong>, <strong>Weatherbit</strong>, <strong>Visual Crossing</strong>, <strong>NOAA</strong>.</p>'''

ANSWERS[95] = r'''<p><strong>Situation:</strong> An e-commerce retailer ships from 12 warehouses across regions. Inventory must be tracked per warehouse, transfers between warehouses must be auditable, the cart must reserve stock during checkout, and order-routing logic should pick the cheapest warehouse to fulfill from.</p>
<p><strong>Approach:</strong> Tables: <code>products</code>, <code>warehouses</code>, <code>inventory</code> (qty per product per warehouse), <code>inventory_movements</code> (every change is logged), <code>reservations</code> (cart holds), and <code>transfers</code>.</p>
<pre><code>CREATE TABLE inventory (
  product_id BIGINT NOT NULL,
  warehouse_id BIGINT NOT NULL,
  on_hand INT NOT NULL DEFAULT 0,
  reserved INT NOT NULL DEFAULT 0,  -- held by carts
  available INT GENERATED ALWAYS AS (on_hand - reserved) VIRTUAL,
  PRIMARY KEY (product_id, warehouse_id),
  CONSTRAINT chk_on_hand CHECK (on_hand &gt;= 0),
  CONSTRAINT chk_reserved CHECK (reserved &gt;= 0 AND reserved &lt;= on_hand)
);

CREATE TABLE inventory_movements (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT, warehouse_id BIGINT,
  delta INT NOT NULL,
  reason ENUM('receipt','sale','return','transfer_out','transfer_in','adjustment'),
  reference_id BIGINT,  -- order_id, transfer_id
  occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_product_time (product_id, occurred_at)
);

-- Reserve stock for cart (atomic)
UPDATE inventory
SET reserved = reserved + ?
WHERE product_id=? AND warehouse_id=?
  AND on_hand - reserved &gt;= ?;
-- if affected_rows = 0, no stock; try next warehouse

-- Order routing query
SELECT i.warehouse_id, w.shipping_zone, w.distance_km
FROM inventory i JOIN warehouses w ON i.warehouse_id=w.id
WHERE i.product_id=? AND (i.on_hand - i.reserved) &gt;= ?
ORDER BY w.distance_km ASC, w.priority ASC LIMIT 1;</code></pre>
<p>All stock changes go through <code>inventory_movements</code> for audit. Periodic reconciliation jobs verify <code>SUM(delta) = on_hand</code> per product+warehouse.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>One row per (product, warehouse)</td><td>Simple, fast lookups</td></tr>
<tr><td>Movements ledger</td><td>Audit, reconciliation, replay</td></tr>
<tr><td>Conditional UPDATE for reserve</td><td>Atomic, avoids overselling</td></tr>
<tr><td>Cart reservation expiry</td><td>Job releases stale holds back to available</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Inventory and OMS platforms: <strong>NetSuite</strong>, <strong>Brightpearl</strong>, <strong>Cin7</strong>, <strong>Zoho Inventory</strong>, <strong>Linnworks</strong>, <strong>Veeqo</strong>, <strong>SkuVault</strong>, <strong>Cogsy</strong>, <strong>Inventory Planner</strong>. Warehouse management: <strong>Manhattan Active</strong>, <strong>SAP EWM</strong>, <strong>Logiwa</strong>, <strong>Nimbus</strong>, <strong>ShipBob OMS</strong>. 3PL services with APIs: <strong>ShipBob</strong>, <strong>ShipMonk</strong>, <strong>Flexport</strong>, <strong>Stord</strong>, <strong>Ware2Go</strong>. Forecasting: <strong>Inventory Planner</strong>, <strong>Cogsy</strong>, <strong>Streamline</strong>, <strong>StockTrim</strong>, in-house with <strong>Prophet</strong>/<strong>NeuralProphet</strong>. Transportation rate-shop: <strong>EasyPost</strong>, <strong>Shippo</strong>, <strong>ShipEngine</strong>. ERP integration via <strong>Codat</strong>, <strong>Rutter</strong>, or <strong>Finch</strong>.</p>'''

ANSWERS[96] = r'''<p><strong>Situation:</strong> A peer-to-peer lending platform matches borrowers requesting loans with retail or institutional lenders who fund them in fractional pieces. The system must compute amortization schedules, distribute payments to investors pro-rata, and handle delinquency.</p>
<p><strong>Approach:</strong> Tables: <code>borrowers</code>, <code>lenders</code>, <code>loan_listings</code>, <code>investments</code> (fractional commitments to a listing), <code>loans</code> (funded loan), <code>payment_schedule</code> (per-installment), <code>payments</code>, and <code>distributions</code> (lender share of each payment).</p>
<pre><code>CREATE TABLE loans (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  borrower_id BIGINT NOT NULL,
  principal_cents BIGINT NOT NULL,
  apr DECIMAL(6,4),
  term_months INT,
  funded_at DATETIME,
  status ENUM('active','paid','default','charged_off'),
  KEY idx_status (status)
);

CREATE TABLE investments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  loan_id BIGINT NOT NULL,
  lender_id BIGINT NOT NULL,
  amount_cents BIGINT NOT NULL,
  share_bps INT,  -- basis points (10000 = 100%) of loan
  funded_at DATETIME,
  UNIQUE KEY uniq_loan_lender (loan_id, lender_id),
  KEY idx_lender (lender_id)
);

CREATE TABLE payment_schedule (
  loan_id BIGINT, installment_no INT,
  due_date DATE, principal_cents BIGINT,
  interest_cents BIGINT,
  status ENUM('pending','paid','late','missed') DEFAULT 'pending',
  PRIMARY KEY (loan_id, installment_no)
);

CREATE TABLE distributions (
  payment_id BIGINT, lender_id BIGINT,
  principal_cents BIGINT, interest_cents BIGINT,
  fee_cents BIGINT,
  PRIMARY KEY (payment_id, lender_id)
);</code></pre>
<p>When a borrower payment arrives, a job allocates principal and interest to each lender pro-rata using their <code>share_bps</code>, writing one <code>distributions</code> row per lender. All money math uses integer cents to avoid floating-point drift.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Integer cents</td><td>No floating-point rounding errors</td></tr>
<tr><td>Pre-computed schedule</td><td>Simple due-date queries, dunning logic</td></tr>
<tr><td>Distributions table</td><td>1099 tax forms, lender statements, audit</td></tr>
<tr><td>Listings vs loans</td><td>Listing may not fully fund; loan starts after</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Lending infrastructure: <strong>LoanPro</strong>, <strong>Peach Finance</strong>, <strong>LendAPI</strong>, <strong>Canopy Servicing</strong>, <strong>Bond</strong> (BaaS), <strong>Unit</strong>, <strong>Treasury Prime</strong>. Banking-as-a-Service rails: <strong>Synapse</strong>, <strong>Galileo</strong>, <strong>Marqeta</strong>. Underwriting: <strong>Plaid</strong> (cash flow), <strong>Argyle</strong>, <strong>Pinwheel</strong> (income), <strong>FactorTrust</strong>, <strong>LexisNexis Risk</strong>. KYC/AML: <strong>Persona</strong>, <strong>Alloy</strong>, <strong>Sumsub</strong>, <strong>Onfido</strong>, <strong>Trulioo</strong>, <strong>Sardine</strong>. ACH/payments: <strong>Modern Treasury</strong>, <strong>Increase</strong>, <strong>Dwolla</strong>. P2P lending platforms: <strong>Prosper</strong>, <strong>LendingClub</strong>, <strong>Funding Circle</strong>, <strong>Upstart</strong>, <strong>Mintos</strong>, <strong>Bondora</strong>. Compliance and regulatory: <strong>ComplyAdvantage</strong>, <strong>Hummingbird</strong>, <strong>Unit21</strong>.</p>'''

ANSWERS[97] = r'''<p><strong>Situation:</strong> The team needs to import customer-uploaded CSV files (sometimes millions of rows), export query results to clients (CSV, Excel, JSON, Parquet), and synchronize data with external systems via batch files. Imports must validate, dedupe, and report errors clearly.</p>
<p><strong>Approach:</strong> Use the right tool for each direction: <code>LOAD DATA INFILE</code> or <code>LOAD DATA LOCAL INFILE</code> for high-speed bulk import, <code>SELECT ... INTO OUTFILE</code> for export, with a staging-table pattern that validates and dedupes before merging into production tables.</p>
<pre><code>-- Bulk import via staging table
CREATE TABLE customers_import_staging LIKE customers;
ALTER TABLE customers_import_staging
  ADD COLUMN row_num INT, ADD COLUMN errors JSON;

LOAD DATA LOCAL INFILE '/tmp/customers.csv'
INTO TABLE customers_import_staging
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '&quot;'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(email, full_name, phone, country)
SET row_num = @row := IFNULL(@row,0)+1,
    created_at = NOW();

-- Validate
UPDATE customers_import_staging
SET errors = JSON_OBJECT('email','invalid')
WHERE email NOT LIKE '%_@_%._%';

-- Merge clean rows
INSERT INTO customers (email, full_name, phone, country)
SELECT email, full_name, phone, country
FROM customers_import_staging
WHERE errors IS NULL
ON DUPLICATE KEY UPDATE
  full_name=VALUES(full_name), phone=VALUES(phone);

-- Export
SELECT id, email, total_spent FROM customers
WHERE country='US'
INTO OUTFILE '/tmp/us_customers.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '&quot;'
LINES TERMINATED BY '\n';</code></pre>
<p>For very large imports, partition the staging table by batch_id, parallelize, and disable secondary indexes during load (rebuild after).</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Approach</th><th>Pro</th><th>Con</th></tr></thead><tbody>
<tr><td>LOAD DATA INFILE</td><td>10-100x faster than INSERTs</td><td>Server-side file path; needs LOCAL flag for client-side</td></tr>
<tr><td>Staging table merge</td><td>Validate without polluting prod</td><td>Extra storage during import</td></tr>
<tr><td>Streaming via app code</td><td>Custom validation, easier errors</td><td>Slower for bulk</td></tr>
<tr><td>SELECT INTO OUTFILE</td><td>Server-side, fast</td><td>File on DB host; need to retrieve</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> CSV/Excel libraries by stack: <strong>fast-csv</strong>, <strong>papaparse</strong>, <strong>SheetJS</strong>, <strong>ExcelJS</strong> (JS); <strong>pandas</strong>, <strong>polars</strong>, <strong>openpyxl</strong>, <strong>pyarrow</strong> (Python). ETL/ingestion platforms: <strong>Airbyte</strong>, <strong>Fivetran</strong>, <strong>Stitch</strong>, <strong>Hevo</strong>, <strong>Meltano</strong>, <strong>Estuary</strong>. Reverse ETL: <strong>Hightouch</strong>, <strong>Census</strong>, <strong>Polytomic</strong>, <strong>Grouparoo</strong>. Data validation: <strong>Great Expectations</strong>, <strong>Soda</strong>, <strong>Pandera</strong>. CDC for live sync: <strong>Debezium</strong>, <strong>Maxwell</strong>. Customer-facing import builders: <strong>Flatfile</strong>, <strong>OneSchema</strong>, <strong>UploadJoy</strong>, <strong>Dromo</strong>, <strong>CSVBox</strong>. Background job runners: <strong>BullMQ</strong>, <strong>Sidekiq</strong>, <strong>Celery</strong>, <strong>Inngest</strong>, <strong>Trigger.dev</strong>, <strong>Temporal</strong>.</p>'''

ANSWERS[98] = r'''<p><strong>Situation:</strong> A freelance marketplace like Upwork connects clients posting projects with freelancers bidding on them. The platform handles proposals, contracts, milestones, escrow, work submissions, hourly tracking, reviews, and dispute resolution.</p>
<p><strong>Approach:</strong> Tables: <code>users</code> (with role flag), <code>freelancer_profiles</code>, <code>projects</code>, <code>proposals</code>, <code>contracts</code>, <code>milestones</code>, <code>time_logs</code>, <code>messages</code>, <code>reviews</code>, <code>disputes</code>.</p>
<pre><code>CREATE TABLE projects (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  client_id BIGINT NOT NULL,
  title VARCHAR(300),
  description TEXT,
  budget_type ENUM('fixed','hourly'),
  budget_min_cents BIGINT, budget_max_cents BIGINT,
  category_id BIGINT,
  status ENUM('open','in_progress','completed','cancelled'),
  posted_at DATETIME, KEY idx_open_cat (status, category_id)
);

CREATE TABLE proposals (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_id BIGINT, freelancer_id BIGINT,
  bid_cents BIGINT, hourly_rate_cents BIGINT,
  cover_letter TEXT, status ENUM('submitted','shortlisted','accepted','rejected','withdrawn'),
  submitted_at DATETIME,
  UNIQUE KEY uniq_proj_freelancer (project_id, freelancer_id)
);

CREATE TABLE contracts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_id BIGINT, freelancer_id BIGINT, client_id BIGINT,
  type ENUM('fixed','hourly'),
  total_cents BIGINT,
  started_at DATETIME, ended_at DATETIME,
  status ENUM('active','paused','completed','disputed','terminated')
);

CREATE TABLE milestones (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  contract_id BIGINT, title VARCHAR(200),
  amount_cents BIGINT, status ENUM('funded','submitted','released','disputed'),
  funded_at DATETIME, released_at DATETIME
);

CREATE TABLE time_logs (
  contract_id BIGINT, freelancer_id BIGINT,
  started_at DATETIME, minutes INT,
  description TEXT, screenshot_url VARCHAR(500),
  PRIMARY KEY (contract_id, started_at)
);</code></pre>
<p>Money sits in escrow (Stripe Connect or similar) when a milestone is funded. Release transitions trigger a payout.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Milestone-based escrow</td><td>Trust for both sides</td></tr>
<tr><td>Time logs with screenshots</td><td>Hourly billing dispute evidence</td></tr>
<tr><td>UNIQUE proposal per freelancer</td><td>One bid per project; revisions update</td></tr>
<tr><td>Two-sided reviews</td><td>Reputation system</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Existing platforms: <strong>Upwork</strong>, <strong>Fiverr</strong>, <strong>Toptal</strong>, <strong>Contra</strong>, <strong>MarketerHire</strong>, <strong>Braintrust</strong>, <strong>Arc.dev</strong>, <strong>Lemon.io</strong>, <strong>Worksome</strong>, <strong>Malt</strong>. Payments and escrow: <strong>Stripe Connect</strong>, <strong>Adyen for Marketplaces</strong>, <strong>Hyperwallet</strong>, <strong>Wise Platform</strong>, <strong>Tipalti</strong>, <strong>Trolley</strong>, <strong>Deel</strong>, <strong>Remote</strong>. Identity/KYC for freelancers: <strong>Persona</strong>, <strong>Stripe Identity</strong>. Time-tracking: <strong>Toggl</strong>, <strong>Harvest</strong>, <strong>Clockify</strong>, <strong>Hubstaff</strong> (with screenshots), <strong>Time Doctor</strong>. Search: <strong>Algolia</strong>, <strong>Typesense</strong>, <strong>Elasticsearch</strong>; AI matching with embeddings on <strong>Pinecone</strong> or <strong>pgvector</strong>. Disputes mediation flow can integrate <strong>Modria</strong> (Tyler ODR) or build in-house.</p>'''

ANSWERS[99] = r'''<p><strong>Situation:</strong> A digital asset management platform stores images, videos, and documents for marketing teams &mdash; with versioning, tagging, rights management, transformations (resize, crop, transcode), and CDN delivery. Files don&rsquo;t belong in MySQL; the database stores metadata.</p>
<p><strong>Approach:</strong> Files live in object storage (S3, R2, GCS); MySQL holds <code>assets</code>, <code>asset_versions</code>, <code>folders</code>, <code>tags</code>, <code>asset_tags</code>, <code>renditions</code> (pre-computed sizes), <code>rights</code>, and <code>asset_usage</code> (where the asset is used).</p>
<pre><code>CREATE TABLE assets (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  workspace_id BIGINT NOT NULL,
  folder_id BIGINT,
  name VARCHAR(300),
  current_version_id BIGINT,
  type ENUM('image','video','audio','document','other'),
  uploaded_by BIGINT,
  created_at DATETIME, KEY idx_workspace_folder (workspace_id, folder_id)
);

CREATE TABLE asset_versions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  asset_id BIGINT NOT NULL,
  version_no INT NOT NULL,
  storage_key VARCHAR(500),    -- S3 key
  byte_size BIGINT, mime_type VARCHAR(100),
  width INT, height INT, duration_ms INT,
  checksum_sha256 CHAR(64),
  uploaded_at DATETIME,
  UNIQUE KEY uniq_asset_ver (asset_id, version_no)
);

CREATE TABLE renditions (
  asset_version_id BIGINT, name VARCHAR(60), -- 'thumb','square_400','hd'
  storage_key VARCHAR(500),
  width INT, height INT, byte_size BIGINT,
  PRIMARY KEY (asset_version_id, name)
);

CREATE TABLE rights (
  asset_id BIGINT PRIMARY KEY,
  license VARCHAR(100), grant_starts DATE, grant_ends DATE,
  attribution_required BOOL, region_restrictions JSON
);

-- Search by tag
SELECT a.* FROM assets a
JOIN asset_tags at ON at.asset_id=a.id
WHERE at.tag_id IN (?,?,?)
GROUP BY a.id HAVING COUNT(*)=3;</code></pre>
<p>Renditions are generated asynchronously by a worker on upload (Lambda, Cloudflare Workers, or a Node/Python worker) and served via CDN with signed URLs.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Files in object store, metadata in MySQL</td><td>Cheap storage + queryable metadata</td></tr>
<tr><td>Pre-rendered renditions</td><td>Cheap delivery; or use on-the-fly via CDN</td></tr>
<tr><td>Version table</td><td>Roll back, audit, compare</td></tr>
<tr><td>Rights metadata</td><td>Compliance; auto-warn before public usage</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Off-the-shelf DAM: <strong>Bynder</strong>, <strong>Frontify</strong>, <strong>Brandfolder</strong>, <strong>Widen</strong>, <strong>Canto</strong>, <strong>MediaValet</strong>, <strong>Air</strong>, <strong>Pics.io</strong>, <strong>Filerobot</strong>, <strong>Cloudinary Media Library</strong>. Storage: <strong>AWS S3</strong>, <strong>Cloudflare R2</strong>, <strong>Backblaze B2</strong>, <strong>Wasabi</strong>, <strong>GCS</strong>. CDN with image transforms: <strong>Cloudinary</strong>, <strong>imgix</strong>, <strong>Cloudflare Images</strong>, <strong>Bunny</strong>, <strong>Fastly Image Optimizer</strong>, <strong>ImageKit</strong>, <strong>Uploadcare</strong>. Video: <strong>Mux</strong>, <strong>api.video</strong>, <strong>Cloudflare Stream</strong>, <strong>AWS MediaConvert</strong>. AI tagging/auto-metadata: <strong>AWS Rekognition</strong>, <strong>Google Vision</strong>, <strong>Imagga</strong>, <strong>Clarifai</strong>, <strong>OpenAI CLIP</strong>, <strong>SigLIP</strong>. Reverse search via <strong>pgvector</strong> or <strong>Pinecone</strong> on CLIP embeddings.</p>'''

ANSWERS[100] = r'''<p><strong>Situation:</strong> A food delivery platform like DoorDash links restaurants, customers, and delivery drivers. Customers browse menus, place orders, drivers accept and deliver, and the system handles payments, tipping, real-time tracking, and ratings. Order volume spikes at lunch and dinner.</p>
<p><strong>Approach:</strong> Tables: <code>restaurants</code>, <code>menu_items</code>, <code>menu_modifiers</code>, <code>customers</code>, <code>drivers</code>, <code>orders</code>, <code>order_items</code>, <code>order_status_history</code>, <code>delivery_offers</code>, <code>ratings</code>.</p>
<pre><code>CREATE TABLE restaurants (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(200), cuisine VARCHAR(80),
  address_line VARCHAR(200), lat DECIMAL(10,7), lng DECIMAL(10,7),
  is_open BOOL, prep_time_min INT,
  delivery_radius_km DECIMAL(5,2),
  KEY idx_geo_open (is_open, lat, lng)
);

CREATE TABLE menu_items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  restaurant_id BIGINT, name VARCHAR(200),
  price_cents INT, category VARCHAR(80), is_available BOOL DEFAULT TRUE,
  KEY idx_restaurant (restaurant_id, is_available)
);

CREATE TABLE orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id BIGINT, restaurant_id BIGINT, driver_id BIGINT,
  subtotal_cents INT, delivery_fee_cents INT, tip_cents INT, tax_cents INT, total_cents INT,
  delivery_lat DECIMAL(10,7), delivery_lng DECIMAL(10,7),
  status ENUM('placed','accepted_by_restaurant','prep','ready','picked_up','delivered','cancelled'),
  placed_at DATETIME, delivered_at DATETIME,
  KEY idx_customer (customer_id, placed_at),
  KEY idx_active_status (status, placed_at)
);

CREATE TABLE order_status_history (
  order_id BIGINT, status VARCHAR(40),
  changed_at DATETIME(3), changed_by ENUM('system','restaurant','driver','customer','support'),
  PRIMARY KEY (order_id, changed_at)
);

CREATE TABLE delivery_offers (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT, driver_id BIGINT,
  offered_at DATETIME, expires_at DATETIME,
  status ENUM('offered','accepted','rejected','timeout'),
  KEY idx_driver (driver_id, status)
);</code></pre>
<p>Driver location updates are not in MySQL OLTP &mdash; they go to Redis or a geo-store (Tile38, MongoDB geoNear) and feed a dispatch service. Real-time customer tracking uses websockets; the database just persists key state transitions.</p>
<p><strong>Trade-offs:</strong></p>
<table><thead><tr><th>Decision</th><th>Why</th></tr></thead><tbody>
<tr><td>Status history table</td><td>SLA reporting, dispute evidence, ETA accuracy</td></tr>
<tr><td>Driver location in Redis</td><td>10Hz updates would crush MySQL</td></tr>
<tr><td>Delivery offers separate</td><td>Multi-driver bid; first-accept wins</td></tr>
<tr><td>Tax/fee/tip split columns</td><td>Receipts, accounting, regulatory reporting</td></tr>
</tbody></table>
<p><strong>Production polish:</strong> Established platforms: <strong>DoorDash</strong>, <strong>Uber Eats</strong>, <strong>Grubhub</strong>, <strong>Deliveroo</strong>, <strong>Just Eat Takeaway</strong>, <strong>Swiggy</strong>, <strong>Zomato</strong>, <strong>Rappi</strong>, <strong>Wolt</strong>, <strong>iFood</strong>, <strong>Talabat</strong>. POS/menu integrations: <strong>Toast</strong>, <strong>Square for Restaurants</strong>, <strong>Olo</strong>, <strong>ItsaCheckmate</strong>, <strong>Otter</strong>, <strong>Deliverect</strong>. Routing/dispatch: <strong>Onfleet</strong>, <strong>Bringg</strong>, <strong>Routific</strong>, <strong>Onflight</strong>; mapping via <strong>Mapbox</strong>, <strong>Google Maps Platform</strong>, <strong>HERE</strong>. Delivery as a service (DaaS) APIs: <strong>DoorDash Drive</strong>, <strong>Uber Direct</strong>, <strong>Postmates</strong>, <strong>Burq</strong>, <strong>Gophr</strong>. Dynamic pricing/surge models in-house with reinforcement learning, or use <strong>Symphony RetailAI</strong>. Payment splitting (restaurant/driver/platform): <strong>Stripe Connect</strong>, <strong>Adyen for Platforms</strong>. Real-time customer notifications: <strong>OneSignal</strong>, <strong>Braze</strong>, <strong>Firebase Cloud Messaging</strong>, <strong>Knock</strong>.</p>'''
