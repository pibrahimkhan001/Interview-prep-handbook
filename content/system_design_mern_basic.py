"""Detailed answers for System Design MERN Stack Basic interview questions.

Style: ~80-150 words concise prose with one focused code snippet, ~1,400-1,500 chars.
Architectural-leaning Basic answers that weave the four MERN technologies together.
"""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''
<p>The <strong>MERN stack</strong> is a JavaScript-based set of four technologies used together to build full-stack web applications &mdash; everything from the database to the browser is written in JavaScript, which is the main reason the stack is popular.</p>

<p>The four letters stand for:</p>

<ul>
<li><strong>M &mdash; MongoDB</strong>: a document database that stores data as flexible JSON-like documents.</li>
<li><strong>E &mdash; Express.js</strong>: a minimalist web framework for Node.js that handles HTTP routing, middleware, and APIs.</li>
<li><strong>R &mdash; React</strong>: a component-based UI library for building interactive single-page applications in the browser.</li>
<li><strong>N &mdash; Node.js</strong>: a JavaScript runtime that lets you run JavaScript on the server.</li>
</ul>

<p>A typical request flows like this: the React app in the browser calls an HTTP API; Express (running on Node.js) handles the request; Node talks to MongoDB to read or write data; the response goes back to React, which updates the UI.</p>

<p>The big win is one language end-to-end &mdash; the same developer can read all four layers without switching mental contexts. Adjacent stacks include <strong>MEAN</strong> (Angular instead of React) and <strong>MEVN</strong> (Vue instead of React).</p>
'''

ANSWERS[2] = r'''
<p>Setting up a basic MERN application is two halves: a backend server and a frontend app, each in its own folder.</p>

<pre><code># Project layout
my-mern-app/
├── server/        ← Express + Node + MongoDB
│   ├── package.json
│   ├── index.js
│   └── .env
└── client/        ← React (created with Vite or CRA)
    ├── package.json
    └── src/

# 1. Backend
mkdir server &amp;&amp; cd server &amp;&amp; npm init -y
npm install express mongoose cors dotenv

# server/index.js
import express from "express"
import mongoose from "mongoose"
import cors from "cors"
const app = express()
app.use(cors())
app.use(express.json())
await mongoose.connect(process.env.MONGO_URI)
app.get("/api/health", (req, res) =&gt; res.json({ ok: true }))
app.listen(4000)

# 2. Frontend (Vite is the modern choice)
cd .. &amp;&amp; npm create vite@latest client -- --template react
cd client &amp;&amp; npm install
npm run dev    # http://localhost:5173</code></pre>

<p>In development the React app runs on port 5173 and the API on 4000; CORS or a Vite proxy connects them. In production both are deployed together &mdash; either as separate services or with the React build served as static files by Express.</p>
'''

ANSWERS[3] = r'''
<p>The MERN stack&rsquo;s big selling points come from being all-JavaScript and using mature, widely-deployed open-source pieces.</p>

<ul>
<li><strong>One language across the stack</strong>: write JavaScript (or TypeScript) from the database driver up to the browser. Smaller teams ship faster; the same engineer can read and fix any layer.</li>
<li><strong>JSON throughout</strong>: MongoDB documents, Express request bodies, and React state are all JSON-shaped &mdash; no impedance mismatch like SQL row &harr; object mapping.</li>
<li><strong>Huge ecosystem</strong>: npm has over a million packages, so almost anything you need (auth, payments, charts, validation, testing) already exists.</li>
<li><strong>Component reuse</strong>: React components are reusable building blocks; <code>express.Router</code> modules organize backend code the same way.</li>
<li><strong>Free and open source</strong>: every piece is permissively licensed; no per-seat fees.</li>
<li><strong>Cloud-friendly</strong>: managed hosts (MongoDB Atlas, Vercel, Render, Railway, Fly.io) make deploys easy.</li>
<li><strong>SPA-friendly</strong>: React is excellent for rich, interactive UIs.</li>
</ul>

<p>It&rsquo;s not perfect &mdash; SEO needs server-side rendering (Next.js), and CPU-heavy tasks fit Go/Rust better &mdash; but for typical CRUD-style web apps it&rsquo;s a great default.</p>
'''

ANSWERS[4] = r'''
<p>Most teams use a <strong>monorepo with two top-level folders</strong> &mdash; one for the API server, one for the React client &mdash; with a shared <code>package.json</code> at the root if you want one-command dev startup.</p>

<pre><code>my-app/
├── package.json              ← workspace runner
├── client/                   ← React app
│   ├── src/
│   │   ├── components/       ← reusable UI pieces
│   │   ├── pages/            ← route-level views
│   │   ├── hooks/            ← custom hooks
│   │   ├── api/              ← fetch wrappers
│   │   ├── store/            ← state (Redux/Zustand)
│   │   └── App.jsx
│   └── vite.config.js
├── server/                   ← Node + Express
│   ├── src/
│   │   ├── routes/           ← Express routers
│   │   ├── controllers/      ← request handlers
│   │   ├── models/           ← Mongoose schemas
│   │   ├── middleware/       ← auth, validation
│   │   ├── services/         ← business logic
│   │   └── index.js
│   └── .env
├── shared/                   ← types/utils used by both
└── README.md</code></pre>

<p>The key idea is <strong>separation of concerns within each side</strong>: routes only handle HTTP, controllers call services, services call models, models define the schema. On the React side, components stay presentational while hooks own data-fetching logic.</p>

<p>For larger apps, <strong>npm/pnpm/yarn workspaces</strong> turn this into a proper monorepo so client and server can share TypeScript types from <code>shared/</code>. <strong>Turborepo</strong> or <strong>Nx</strong> make builds fast.</p>
'''

ANSWERS[5] = r'''
<p>Connect Node.js to MongoDB using the official <strong>MongoDB driver</strong> for low-level work, or <strong>Mongoose</strong> (an ODM &mdash; Object Data Modeler) for schema-validated convenience. Mongoose is the default choice in MERN stacks.</p>

<pre><code>// server/src/db.js
import mongoose from "mongoose"

export async function connectDb() {
  try {
    await mongoose.connect(process.env.MONGO_URI, {
      // sensible defaults; most options are auto-applied in driver 4+
    })
    console.log("MongoDB connected")
  } catch (err) {
    console.error("Mongo connect failed:", err)
    process.exit(1)
  }
}

// .env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/myapp

// server/src/index.js
import { connectDb } from "./db.js"
await connectDb()
app.listen(4000)</code></pre>

<p>The <strong>connection string</strong> follows the format <code>mongodb+srv://&lt;user&gt;:&lt;pass&gt;@&lt;host&gt;/&lt;db&gt;</code> for managed Atlas clusters, or <code>mongodb://localhost:27017/myapp</code> for local dev. Always store it in a <code>.env</code> file (loaded with <strong>dotenv</strong>) and add <code>.env</code> to <code>.gitignore</code>.</p>

<p>For production, set up a connection pool (the driver does this automatically; default size is 100), enable <strong>retryWrites</strong>, and listen for connection events to log disconnects.</p>
'''

ANSWERS[6] = r'''
<p><strong>Express</strong> is the &ldquo;E&rdquo; in MERN &mdash; a minimalist web framework that runs on Node.js and provides three things: <strong>routing</strong>, <strong>middleware</strong>, and a clean way to build <strong>HTTP APIs</strong>.</p>

<ul>
<li><strong>Routing</strong>: maps HTTP methods + URL patterns to handler functions (<code>app.get("/users/:id", handler)</code>).</li>
<li><strong>Middleware</strong>: a pipeline of functions that run on every request &mdash; for parsing JSON bodies, logging, authenticating, handling errors, and so on.</li>
<li><strong>Response helpers</strong>: <code>res.json()</code>, <code>res.status()</code>, <code>res.redirect()</code> &mdash; small, ergonomic API on top of Node&rsquo;s raw HTTP.</li>
</ul>

<pre><code>import express from "express"
const app = express()

// global middleware
app.use(express.json())

// route
app.get("/api/users/:id", async (req, res) =&gt; {
  const user = await User.findById(req.params.id)
  if (!user) return res.status(404).json({ error: "not_found" })
  res.json(user)
})

app.listen(4000)</code></pre>

<p>Express is intentionally unopinionated &mdash; it doesn&rsquo;t pick your database or auth library, leaving those decisions to you. Modern alternatives in the Node ecosystem include <strong>Fastify</strong> (faster), <strong>NestJS</strong> (opinionated, TypeScript-first), <strong>Hono</strong>, and <strong>Elysia</strong>, but Express remains the most common in MERN apps.</p>
'''

ANSWERS[7] = r'''
<p>A RESTful API in Express follows the convention that URLs name <strong>resources</strong> (nouns) and HTTP methods name <strong>actions</strong> (verbs). Express <strong>routers</strong> group related routes into modules.</p>

<pre><code>// server/src/routes/users.js
import express from "express"
import * as ctrl from "../controllers/users.js"

const router = express.Router()

router.get("/",       ctrl.list)      // GET    /api/users
router.get("/:id",    ctrl.get)       // GET    /api/users/123
router.post("/",      ctrl.create)    // POST   /api/users
router.put("/:id",    ctrl.update)    // PUT    /api/users/123
router.delete("/:id", ctrl.remove)    // DELETE /api/users/123

export default router

// server/src/controllers/users.js
import User from "../models/User.js"

export const list   = async (req, res) =&gt; res.json(await User.find())
export const get    = async (req, res) =&gt; res.json(await User.findById(req.params.id))
export const create = async (req, res) =&gt; res.status(201).json(await User.create(req.body))

// server/src/index.js
import usersRouter from "./routes/users.js"
app.use("/api/users", usersRouter)</code></pre>

<p>Status codes matter: <strong>200</strong> OK, <strong>201</strong> Created, <strong>204</strong> No Content (for deletes), <strong>400</strong> Bad Request, <strong>401</strong> Unauthorized, <strong>404</strong> Not Found, <strong>500</strong> Server Error. Always return JSON with consistent error shapes (<code>{ error: &quot;message&quot; }</code>) so the React client can handle them generically.</p>
'''

ANSWERS[8] = r'''
<p>Routing in React turns URL paths into rendered components &mdash; what shows on the page when the user visits <code>/about</code> versus <code>/users/42</code>. The standard library is <strong>React Router</strong> (currently v6/v7); newer apps often use <strong>Next.js</strong> or <strong>TanStack Router</strong> instead, but React Router is the MERN default.</p>

<pre><code>// client/src/main.jsx
import { BrowserRouter, Routes, Route, Link } from "react-router-dom"

function App() {
  return (
    &lt;BrowserRouter&gt;
      &lt;nav&gt;
        &lt;Link to="/"&gt;Home&lt;/Link&gt;
        &lt;Link to="/users"&gt;Users&lt;/Link&gt;
      &lt;/nav&gt;
      &lt;Routes&gt;
        &lt;Route path="/"        element={&lt;Home /&gt;} /&gt;
        &lt;Route path="/users"   element={&lt;UserList /&gt;} /&gt;
        &lt;Route path="/users/:id" element={&lt;UserDetail /&gt;} /&gt;
        &lt;Route path="*"        element={&lt;NotFound /&gt;} /&gt;
      &lt;/Routes&gt;
    &lt;/BrowserRouter&gt;
  )
}

// inside UserDetail
import { useParams } from "react-router-dom"
const { id } = useParams()    // matches :id from the URL</code></pre>

<p>It&rsquo;s <strong>client-side routing</strong>: React intercepts navigation, updates the URL via <code>history.pushState</code>, and swaps components without a full page reload &mdash; that&rsquo;s what makes single-page apps feel instant. For SEO and faster first paint, <strong>Next.js</strong> adds server-side rendering on top of the same idea.</p>
'''

ANSWERS[9] = r'''
<p>State in React is data that, when it changes, causes the UI to re-render. There&rsquo;s a ladder of options &mdash; pick the simplest one that solves your problem.</p>

<ul>
<li><strong>Local state</strong> with <code>useState</code> &mdash; for a single component (form input, toggle, counter).</li>
<li><strong>Lifted state</strong> &mdash; move state up to a parent when two siblings need to share it.</li>
<li><strong>Context API</strong> &mdash; for app-wide values that rarely change (theme, current user, locale).</li>
<li><strong>Server state libraries</strong> (<strong>TanStack Query</strong>, <strong>SWR</strong>, <strong>RTK Query</strong>) &mdash; for data fetched from APIs, with caching, refetching, and loading/error handling built in.</li>
<li><strong>Global stores</strong> (<strong>Zustand</strong>, <strong>Jotai</strong>, <strong>Redux Toolkit</strong>) &mdash; for client state shared across many components (cart, modal stack, undo history).</li>
</ul>

<pre><code>// useState &mdash; the basic case
const [count, setCount] = useState(0)
&lt;button onClick={() =&gt; setCount(c =&gt; c + 1)}&gt;{count}&lt;/button&gt;

// TanStack Query &mdash; the modern default for API data
const { data, isLoading } = useQuery({
  queryKey: ["users"],
  queryFn: () =&gt; fetch("/api/users").then(r =&gt; r.json())
})</code></pre>

<p>The most common mistake is reaching for Redux or Zustand too early. Modern advice: separate <strong>server state</strong> (use TanStack Query) from <strong>client state</strong> (use Zustand or Context); most apps need very little of the latter.</p>
'''

ANSWERS[10] = r'''
<p><strong>MongoDB</strong> is the persistent storage layer of the MERN stack &mdash; a document database that stores JSON-like records called <em>documents</em> grouped into <em>collections</em>. Its role is to remember things between requests: users, posts, orders, anything the app needs to outlive a single page load.</p>

<p>It fits the MERN philosophy because documents map naturally to JavaScript objects:</p>

<pre><code>// JavaScript object
{ name: "Alice", email: "alice@example.com", hobbies: ["chess", "yoga"] }

// MongoDB document &mdash; same shape
{ _id: ObjectId("..."), name: "Alice", email: "alice@example.com", hobbies: ["chess", "yoga"] }</code></pre>

<p>Key properties that make MongoDB common in MERN apps:</p>

<ul>
<li><strong>Flexible schema</strong>: fields can vary across documents, which fits early-stage products that change shape often. Schema rules can be added later via <strong>Mongoose</strong> or <code>$jsonSchema</code> validators.</li>
<li><strong>JSON-native</strong>: no SQL-to-object translation; the data the API returns is the data the database stores.</li>
<li><strong>Horizontal scaling</strong>: built-in sharding distributes data across machines.</li>
<li><strong>Rich queries</strong>: filtering, projection, aggregation pipelines, full-text search, geospatial queries, all out of the box.</li>
</ul>

<p>For most CRUD apps it&rsquo;s a fine default; relational data with heavy joins still fits SQL better.</p>
'''

ANSWERS[11] = r'''
<p><strong>Mongoose</strong> wraps the MongoDB driver with schema validation and ergonomic methods. CRUD becomes four method families on the model: <code>create</code>, <code>find</code>, <code>updateOne</code>/<code>findOneAndUpdate</code>, and <code>deleteOne</code>.</p>

<pre><code>import mongoose from "mongoose"

const userSchema = new mongoose.Schema({
  name:  { type: String, required: true },
  email: { type: String, required: true, unique: true },
  age:   Number
}, { timestamps: true })   // adds createdAt, updatedAt

const User = mongoose.model("User", userSchema)

// CREATE
const u = await User.create({ name: "Alice", email: "a@example.com" })

// READ
const all  = await User.find({ age: { $gte: 18 } })
const one  = await User.findById("...")
const byEmail = await User.findOne({ email: "a@example.com" })

// UPDATE
await User.updateOne({ _id: id }, { $set: { name: "Alicia" } })
const updated = await User.findByIdAndUpdate(id, { name: "Alicia" }, { new: true })

// DELETE
await User.deleteOne({ _id: id })
const removed = await User.findByIdAndDelete(id)</code></pre>

<p>Notes for production: always handle errors with <code>try/catch</code> in async handlers, use <code>{ new: true }</code> on update methods to get the updated document back, and prefer <code>findByIdAndUpdate</code> over <code>findById</code>+<code>save</code> to avoid race conditions. Newer alternatives include <strong>Prisma</strong> with the MongoDB connector and <strong>Drizzle</strong>, but Mongoose is the MERN default.</p>
'''

ANSWERS[12] = r'''
<p>Heroku used to be the default but is now <strong>more expensive than the alternatives</strong>; modern equivalents include <strong>Render</strong>, <strong>Railway</strong>, <strong>Fly.io</strong>, <strong>Vercel</strong> (best for the React side), and <strong>AWS Elastic Beanstalk</strong>/<strong>App Runner</strong>. The shape of the deploy is the same everywhere.</p>

<p>Steps for a typical platform-as-a-service deploy:</p>

<ol>
<li><strong>Prepare the server</strong>: read <code>process.env.PORT</code> instead of hard-coding 4000, ensure <code>"start": "node src/index.js"</code> in <code>package.json</code>, set <code>"engines": { "node": "20.x" }</code>.</li>
<li><strong>Database</strong>: spin up a free <strong>MongoDB Atlas</strong> cluster, allow access from the platform&rsquo;s IPs, copy the connection string.</li>
<li><strong>Frontend</strong>: build with <code>npm run build</code>; deploy the static <code>dist/</code> folder to <strong>Vercel</strong>/<strong>Netlify</strong>/<strong>Cloudflare Pages</strong>, or have Express serve it via <code>app.use(express.static("client/dist"))</code>.</li>
<li><strong>Push</strong>:</li>
</ol>

<pre><code>git init &amp;&amp; git commit -am "init"
heroku create my-mern-app                    # or `render up`, `railway up`
heroku config:set MONGO_URI=...              # set environment variables
git push heroku main                          # platform builds and deploys</code></pre>

<p>Set <strong>environment variables</strong> in the platform UI (never commit them); enable <strong>auto-deploy from GitHub</strong> for continuous deployment; add a <strong>health-check endpoint</strong> at <code>/api/health</code> for the platform to monitor.</p>
'''

ANSWERS[13] = r'''
<p>Authentication in a MERN app means proving who is making each request. The two common patterns are <strong>JWT (JSON Web Tokens)</strong> for stateless APIs and <strong>session cookies</strong> for traditional apps; modern teams often outsource the whole thing to <strong>Auth0</strong>, <strong>Clerk</strong>, <strong>WorkOS</strong>, <strong>Supabase Auth</strong>, or <strong>Stack Auth</strong>.</p>

<p>The simple JWT flow:</p>

<pre><code>// Register / login: hash password with bcrypt, sign a JWT
import bcrypt from "bcrypt"
import jwt from "jsonwebtoken"

app.post("/api/login", async (req, res) =&gt; {
  const user = await User.findOne({ email: req.body.email })
  if (!user) return res.status(401).json({ error: "invalid" })
  const ok = await bcrypt.compare(req.body.password, user.passwordHash)
  if (!ok) return res.status(401).json({ error: "invalid" })

  const token = jwt.sign({ uid: user._id }, process.env.JWT_SECRET, { expiresIn: "15m" })
  res.json({ token })
})

// Protect routes with middleware
function auth(req, res, next) {
  const token = req.headers.authorization?.replace("Bearer ", "")
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET)
    next()
  } catch { res.status(401).json({ error: "invalid_token" }) }
}
app.get("/api/me", auth, (req, res) =&gt; res.json(req.user))</code></pre>

<p>Production essentials: <strong>never store passwords in plain text</strong>, use <strong>bcrypt</strong> or <strong>argon2</strong> with a cost of at least 10, keep tokens short-lived (15min) and pair them with <strong>refresh tokens</strong>, and serve the API over HTTPS only.</p>
'''

ANSWERS[14] = r'''
<p>Registration creates a user with a securely-hashed password; login verifies credentials and issues a token or session.</p>

<pre><code>// server/src/routes/auth.js
import bcrypt from "bcrypt"
import jwt from "jsonwebtoken"
import User from "../models/User.js"

router.post("/register", async (req, res) =&gt; {
  const { email, password, name } = req.body
  const exists = await User.findOne({ email })
  if (exists) return res.status(409).json({ error: "email_taken" })

  const passwordHash = await bcrypt.hash(password, 12)
  const user = await User.create({ email, name, passwordHash })

  const token = jwt.sign({ uid: user._id }, process.env.JWT_SECRET, { expiresIn: "15m" })
  res.status(201).json({ token, user: { id: user._id, email, name } })
})

router.post("/login", async (req, res) =&gt; {
  const user = await User.findOne({ email: req.body.email })
  if (!user || !await bcrypt.compare(req.body.password, user.passwordHash))
    return res.status(401).json({ error: "invalid_credentials" })
  const token = jwt.sign({ uid: user._id }, process.env.JWT_SECRET, { expiresIn: "15m" })
  res.json({ token })
})</code></pre>

<p>On the React side, store the token (in <strong>memory</strong> or an <strong>httpOnly cookie</strong> &mdash; never <code>localStorage</code>, which is XSS-vulnerable), include it on every request, and redirect to login when a 401 comes back. Validate inputs with <strong>Zod</strong> or <strong>Joi</strong>; rate-limit login attempts with <strong>express-rate-limit</strong> to deter brute-force; consider a hosted solution like <strong>Clerk</strong>/<strong>Auth0</strong> if you don&rsquo;t want to maintain this yourself.</p>
'''

ANSWERS[15] = r'''
<p>Protecting routes in React means redirecting unauthenticated users away from pages that need a login. The common pattern is a <code>&lt;ProtectedRoute&gt;</code> wrapper component that checks an auth context and either renders the child or redirects.</p>

<pre><code>// client/src/auth/ProtectedRoute.jsx
import { Navigate, useLocation } from "react-router-dom"
import { useAuth } from "./AuthContext"

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return &lt;Spinner /&gt;
  if (!user) return &lt;Navigate to="/login" state={{ from: location }} replace /&gt;
  return children
}

// Usage in router
&lt;Routes&gt;
  &lt;Route path="/login"     element={&lt;Login /&gt;} /&gt;
  &lt;Route path="/dashboard" element={
    &lt;ProtectedRoute&gt;&lt;Dashboard /&gt;&lt;/ProtectedRoute&gt;
  } /&gt;
&lt;/Routes&gt;</code></pre>

<p>For role-based protection, accept a <code>roles</code> prop and check <code>user.role</code> too. After login, use <code>navigate(location.state?.from || &quot;/&quot;)</code> to send the user back to where they tried to go.</p>

<p>Important: <strong>this is a UX guard, not a security boundary</strong>. The real check happens on the server &mdash; the <code>auth</code> middleware on Express must reject any unauthenticated request to <code>/api/*</code>. Hiding a button on the client doesn&rsquo;t stop someone from calling <code>fetch(&quot;/api/admin/delete&quot;)</code> directly.</p>
'''

ANSWERS[16] = r'''
<p>Form validation belongs <strong>on both sides</strong>: client-side for instant feedback, server-side for security. Never trust the client &mdash; anyone can <code>curl</code> your API.</p>

<p>On the React side, the modern combo is <strong>React Hook Form</strong> + <strong>Zod</strong>:</p>

<pre><code>import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"

const schema = z.object({
  email:    z.string().email(),
  password: z.string().min(8)
})

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } =
    useForm({ resolver: zodResolver(schema) })

  return (
    &lt;form onSubmit={handleSubmit(onSubmit)}&gt;
      &lt;input {...register("email")} /&gt;
      {errors.email &amp;&amp; &lt;span&gt;{errors.email.message}&lt;/span&gt;}
      &lt;input {...register("password")} type="password" /&gt;
      &lt;button&gt;Login&lt;/button&gt;
    &lt;/form&gt;
  )
}</code></pre>

<p>On the server, use the <strong>same Zod schema</strong> (share it via a workspace package) so client and server agree:</p>

<pre><code>app.post("/api/login", (req, res) =&gt; {
  const result = schema.safeParse(req.body)
  if (!result.success) return res.status(400).json({ errors: result.error.errors })
  // ... proceed with validated data
})</code></pre>

<p>Mongoose schemas add a third layer at the database level. Other popular validators include <strong>Yup</strong>, <strong>Joi</strong>, and <strong>Valibot</strong>.</p>
'''

ANSWERS[17] = r'''
<p><strong>Redux</strong> is a predictable state container &mdash; one big object holds all client state, and you change it only by dispatching <em>actions</em> through pure <em>reducer</em> functions. The modern way to use Redux is <strong>Redux Toolkit (RTK)</strong>, which removes most of the boilerplate.</p>

<pre><code>// store/cartSlice.js
import { createSlice } from "@reduxjs/toolkit"

const cartSlice = createSlice({
  name: "cart",
  initialState: { items: [] },
  reducers: {
    add:    (state, { payload }) =&gt; { state.items.push(payload) },
    remove: (state, { payload }) =&gt; {
      state.items = state.items.filter(i =&gt; i.id !== payload)
    },
    clear:  (state) =&gt; { state.items = [] }
  }
})

export const { add, remove, clear } = cartSlice.actions
export default cartSlice.reducer

// store/index.js
import { configureStore } from "@reduxjs/toolkit"
import cart from "./cartSlice"
export const store = configureStore({ reducer: { cart } })

// Use in component
import { useSelector, useDispatch } from "react-redux"
const items = useSelector(s =&gt; s.cart.items)
const dispatch = useDispatch()
dispatch(add({ id: 1, name: "Book" }))</code></pre>

<p>Redux is great for complex client state with many writers (cart, undo/redo, multi-step forms). For simpler apps, <strong>Zustand</strong> or <strong>Jotai</strong> are lighter alternatives. For server data, use <strong>RTK Query</strong> or <strong>TanStack Query</strong> &mdash; don&rsquo;t reinvent caching in Redux.</p>
'''

ANSWERS[18] = r'''
<p>Third-party APIs (Stripe, Mapbox, OpenAI, SendGrid) are best called from the <strong>server side</strong> when secrets are involved &mdash; the API key never touches the browser &mdash; and from the client when the request is purely public.</p>

<pre><code>// server/src/routes/payment.js &mdash; secret-bearing
import Stripe from "stripe"
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY)

router.post("/checkout", auth, async (req, res) =&gt; {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: req.body.priceId, quantity: 1 }],
    success_url: process.env.CLIENT_URL + "/success",
    cancel_url:  process.env.CLIENT_URL + "/cancel"
  })
  res.json({ url: session.url })
})

// client &mdash; redirect the user to Stripe
const { url } = await fetch("/api/checkout", { method: "POST", ... }).then(r =&gt; r.json())
window.location = url</code></pre>

<p>Best practices: keep secrets in environment variables, never in client code or git; <strong>cache responses</strong> when the data is shared across users (Redis, in-memory LRU); handle <strong>rate limits</strong> with retry-with-backoff via <strong>p-retry</strong>; for <strong>webhooks</strong> (Stripe events, GitHub events), verify the signature header before trusting the payload; use <strong>circuit breakers</strong> like <strong>opossum</strong> for resilience when the third-party is down.</p>
'''

ANSWERS[19] = r'''
<p>File uploads in MERN: the browser sends a <code>multipart/form-data</code> request, Express parses it with <strong>multer</strong>, and the file goes either to the local filesystem or to object storage (<strong>S3</strong>, <strong>R2</strong>, <strong>Cloudinary</strong>). For production, always use object storage &mdash; the local disk is ephemeral on most platforms.</p>

<pre><code>// server &mdash; multer + S3 (recommended)
import multer from "multer"
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3"

const s3 = new S3Client({ region: "us-east-1" })
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 10 * 1024 * 1024 } })

router.post("/upload", auth, upload.single("file"), async (req, res) =&gt; {
  const key = `uploads/${req.user.uid}/${Date.now()}-${req.file.originalname}`
  await s3.send(new PutObjectCommand({
    Bucket: "myapp-uploads",
    Key:    key,
    Body:   req.file.buffer,
    ContentType: req.file.mimetype
  }))
  await Photo.create({ owner: req.user.uid, key, mimetype: req.file.mimetype })
  res.json({ key })
})

// client &mdash; FormData
const fd = new FormData()
fd.append("file", fileInput.files[0])
fetch("/api/upload", { method: "POST", body: fd })</code></pre>

<p>For large files, use <strong>presigned URLs</strong> so the browser uploads directly to S3 (bytes never traverse your server). For images, <strong>Cloudinary</strong> and <strong>imgix</strong> handle resizing, format conversion, and CDN delivery automatically.</p>
'''

ANSWERS[20] = r'''
<p>A scalable Node/Express backend means serving more users without slowing down or falling over. The principles are stateless servers, async I/O, smart caching, and horizontal scaling.</p>

<ul>
<li><strong>Stateless servers</strong>: never store session data in memory &mdash; use <strong>Redis</strong>, JWTs, or sticky sessions. This lets you run N copies behind a load balancer.</li>
<li><strong>Async everything</strong>: Node is single-threaded; one blocking <code>fs.readFileSync</code> kills throughput. Always use async APIs.</li>
<li><strong>Process clustering</strong>: use <strong>PM2</strong> or Node&rsquo;s <code>cluster</code> module to run one process per CPU core; PaaS platforms handle this automatically.</li>
<li><strong>Caching</strong>: in-memory LRU for hot reads, <strong>Redis</strong> for cross-instance, CDN for static assets and public API responses.</li>
<li><strong>Database scaling</strong>: indexes that match your queries; read replicas for read-heavy workloads; sharding when one node isn&rsquo;t enough.</li>
<li><strong>Background jobs</strong>: long tasks belong in workers (<strong>BullMQ</strong>, <strong>Inngest</strong>, <strong>Trigger.dev</strong>), not in the request handler.</li>
<li><strong>Observability</strong>: structured logs (<strong>pino</strong>), metrics, traces (<strong>OpenTelemetry</strong>) &mdash; you can&rsquo;t fix what you can&rsquo;t see.</li>
</ul>

<pre><code>// Health check for load balancers
app.get("/health", (req, res) =&gt; res.json({ ok: true, uptime: process.uptime() }))</code></pre>

<p>Finally, prefer modern frameworks (<strong>Fastify</strong>, <strong>NestJS</strong>, <strong>Hono</strong>) for new projects &mdash; they&rsquo;re measurably faster than Express.</p>
'''

ANSWERS[21] = r'''
<p>Securing a MERN app is layered &mdash; no single setting makes you safe.</p>

<ul>
<li><strong>HTTPS everywhere</strong>: TLS termination at the load balancer or platform; <strong>HSTS</strong> headers; never accept cleartext.</li>
<li><strong>Authentication</strong>: hash passwords with <strong>bcrypt</strong>/<strong>argon2</strong>; short-lived JWTs with refresh tokens; consider <strong>Auth0</strong>/<strong>Clerk</strong>/<strong>WorkOS</strong>.</li>
<li><strong>Authorization</strong>: check permissions on every protected route; never trust the client.</li>
<li><strong>Input validation</strong>: <strong>Zod</strong>/<strong>Joi</strong> on every request body; never pass user input directly to a DB query.</li>
<li><strong>Helmet</strong>: <code>app.use(helmet())</code> sets safe HTTP headers (CSP, X-Frame-Options, etc.).</li>
<li><strong>CORS</strong>: whitelist origins; never <code>cors({ origin: &quot;*&quot; })</code> for credentialed APIs.</li>
<li><strong>Rate limiting</strong>: <strong>express-rate-limit</strong> on auth and write endpoints to deter brute-force.</li>
<li><strong>NoSQL injection</strong>: don&rsquo;t pass <code>req.body</code> directly to Mongo; sanitize with <strong>express-mongo-sanitize</strong>.</li>
<li><strong>Dependency hygiene</strong>: run <code>npm audit</code> in CI; use <strong>Snyk</strong>/<strong>Dependabot</strong>/<strong>Renovate</strong>.</li>
<li><strong>Secrets management</strong>: env vars, <strong>AWS Secrets Manager</strong>/<strong>HashiCorp Vault</strong>, never in git.</li>
<li><strong>XSS protection</strong>: React escapes JSX by default; the danger is <code>dangerouslySetInnerHTML</code> with user content.</li>
<li><strong>CSRF</strong>: if using cookies, add CSRF tokens via <strong>csurf</strong> or use <code>SameSite=Strict</code>.</li>
</ul>

<p>Run <strong>OWASP ZAP</strong> or <strong>Snyk</strong> against your app before launch; commission a pentest for anything that handles money or PII.</p>
'''

ANSWERS[22] = r'''
<p>Error handling in a MERN stack happens at four layers: client UI, server middleware, async operations, and the database.</p>

<pre><code>// server &mdash; central error middleware (last in the chain)
app.use((err, req, res, next) =&gt; {
  console.error(err)
  const status = err.status || 500
  res.status(status).json({
    error: err.code || "internal_error",
    message: status === 500 ? "Something went wrong" : err.message
  })
})

// async route handlers &mdash; wrap to forward errors automatically
const wrap = fn =&gt; (req, res, next) =&gt; Promise.resolve(fn(req, res, next)).catch(next)
app.get("/api/users/:id", wrap(async (req, res) =&gt; {
  const user = await User.findById(req.params.id)
  if (!user) { const e = new Error("User not found"); e.status = 404; throw e }
  res.json(user)
}))</code></pre>

<p>On the React side, wrap pages in <strong>Error Boundaries</strong> for render-time crashes, and use the loading/error states from <strong>TanStack Query</strong> for failed fetches:</p>

<pre><code>const { data, error, isLoading } = useQuery(...)
if (isLoading) return &lt;Spinner /&gt;
if (error)     return &lt;ErrorMessage error={error} /&gt;</code></pre>

<p>Send unexpected errors to <strong>Sentry</strong>, <strong>Datadog</strong>, or <strong>Honeybadger</strong> so you find out about production issues without waiting for users to report them. Always return JSON error shapes from the API so the client can render them generically.</p>
'''

ANSWERS[23] = r'''
<p>Pagination breaks a long list into chunks. Two flavors are common: <strong>offset pagination</strong> (page numbers, simple) and <strong>cursor pagination</strong> (scrolls and feeds, scales).</p>

<pre><code>// Offset (simple, fine for small datasets &amp; admin tables)
router.get("/posts", async (req, res) =&gt; {
  const page  = parseInt(req.query.page  || "1")
  const limit = parseInt(req.query.limit || "20")
  const skip  = (page - 1) * limit

  const [items, total] = await Promise.all([
    Post.find().sort({ createdAt: -1 }).skip(skip).limit(limit),
    Post.countDocuments()
  ])
  res.json({ items, total, page, pages: Math.ceil(total / limit) })
})

// Cursor (consistent under inserts, fast at any depth)
router.get("/posts", async (req, res) =&gt; {
  const limit = 20
  const before = req.query.before
  const filter = before ? { createdAt: { $lt: new Date(before) } } : {}
  const items = await Post.find(filter).sort({ createdAt: -1 }).limit(limit + 1)
  const nextCursor = items.length &gt; limit ? items[limit - 1].createdAt : null
  res.json({ items: items.slice(0, limit), nextCursor })
})</code></pre>

<p>Skip with a large offset (<code>skip: 50_000</code>) is slow because Mongo has to scan past every skipped doc. Cursor pagination scales because the database uses an index on <code>createdAt</code> directly.</p>

<p>On the React side, <strong>TanStack Query&rsquo;s <code>useInfiniteQuery</code></strong> handles the cursor flow elegantly &mdash; it tracks <code>nextCursor</code>, fetches the next page, and concatenates results.</p>
'''

ANSWERS[24] = r'''
<p>Environment variables keep configuration out of source code. Different environments (dev, staging, prod) get different values for the same variable name &mdash; database URLs, API keys, secret signing keys.</p>

<pre><code># .env (in project root, NEVER committed)
NODE_ENV=development
PORT=4000
MONGO_URI=mongodb+srv://localhost:27017/myapp
JWT_SECRET=replace-me-with-something-long-and-random
STRIPE_SECRET_KEY=sk_test_...

# .gitignore
.env
.env.local

# .env.example (committed; placeholder values only)
NODE_ENV=
PORT=4000
MONGO_URI=
JWT_SECRET=</code></pre>

<pre><code>// server/src/index.js &mdash; load with dotenv
import "dotenv/config"
const PORT = process.env.PORT || 4000
const MONGO_URI = process.env.MONGO_URI

if (!MONGO_URI) { console.error("MONGO_URI required"); process.exit(1) }

// React + Vite &mdash; client-side env vars
// Only variables prefixed with VITE_ are exposed
import.meta.env.VITE_API_URL    // OK
import.meta.env.SECRET           // undefined &mdash; secrets stay server-side</code></pre>

<p>Production tips: validate required env vars at startup with <strong>Zod</strong> or <strong>envalid</strong> so misconfiguration crashes immediately rather than mysteriously failing later. Use <strong>Doppler</strong>, <strong>1Password Secrets</strong>, <strong>AWS Secrets Manager</strong>, or platform-native secret managers (Vercel, Render, Fly.io) for production secrets &mdash; never put real secrets in <code>.env</code> on a server.</p>
'''

ANSWERS[25] = r'''
<p>Node.js is single-threaded, so async I/O is the only way to keep the server responsive while waiting for the database or network. Three styles exist; <strong>async/await</strong> is the modern standard.</p>

<pre><code>// 1. Callbacks (legacy)
fs.readFile("a.txt", (err, data) =&gt; {
  if (err) return console.error(err)
  console.log(data.toString())
})

// 2. Promises (then/catch)
fs.promises.readFile("a.txt")
  .then(data =&gt; console.log(data.toString()))
  .catch(console.error)

// 3. async/await &mdash; modern, reads top-to-bottom
async function load() {
  try {
    const data = await fs.promises.readFile("a.txt")
    console.log(data.toString())
  } catch (err) {
    console.error(err)
  }
}

// Parallel calls &mdash; Promise.all
const [user, posts] = await Promise.all([
  User.findById(id),
  Post.find({ author: id })
])

// Stay safe under partial failure
const results = await Promise.allSettled([fetchA(), fetchB(), fetchC()])</code></pre>

<p>Common pitfalls: forgetting <code>await</code> (the function returns a Promise that nobody handles), unhandled rejections (always have a top-level <code>process.on(&quot;unhandledRejection&quot;, ...)</code> handler), and serial loops where parallel would do (use <code>Promise.all</code> instead of <code>for...await</code>). For CPU-heavy work, offload to <strong>worker_threads</strong>, <strong>Piscina</strong>, or a job queue &mdash; async only helps with I/O.</p>
'''

ANSWERS[26] = r'''
<p><strong>WebSockets</strong> open a persistent two-way channel between browser and server &mdash; perfect for live chat, notifications, multiplayer games, dashboards, and collaborative editing. The most popular MERN library is <strong>Socket.IO</strong>; modern alternatives are <strong>ws</strong>, <strong>Pusher</strong>, <strong>Ably</strong>, <strong>Liveblocks</strong>, and <strong>PartyKit</strong>.</p>

<pre><code>// server &mdash; Socket.IO mounted on the same HTTP server
import { Server } from "socket.io"
import { createServer } from "http"

const httpServer = createServer(app)
const io = new Server(httpServer, { cors: { origin: process.env.CLIENT_URL } })

io.on("connection", (socket) =&gt; {
  console.log("client connected:", socket.id)

  socket.on("chat:send", async (msg) =&gt; {
    const saved = await Message.create({ ...msg, userId: socket.userId })
    io.to(msg.roomId).emit("chat:new", saved)   // broadcast to room
  })

  socket.on("disconnect", () =&gt; { /* cleanup */ })
})

httpServer.listen(4000)

// client &mdash; React + socket.io-client
import { io } from "socket.io-client"
const socket = io(import.meta.env.VITE_API_URL)
socket.emit("chat:send", { roomId: "general", text: "hi" })
socket.on("chat:new", msg =&gt; setMessages(prev =&gt; [...prev, msg]))</code></pre>

<p>For scale, run multiple Node processes with the <strong>Redis adapter</strong> so events fan out across instances; authenticate sockets in middleware (verify the JWT on connection); use <strong>rooms</strong> for per-channel broadcasts. Plain HTTP <strong>SSE (Server-Sent Events)</strong> works for one-way streams and is simpler if you don&rsquo;t need bidirectional.</p>
'''

ANSWERS[27] = r'''
<p><strong>Server-side rendering (SSR)</strong> means the HTML shipped to the browser already contains the rendered UI &mdash; the user sees content faster, search engines index the page properly, and JavaScript &ldquo;hydrates&rdquo; the static markup into an interactive React app once it loads.</p>

<p>You can roll your own with <code>renderToString</code> from <code>react-dom/server</code>, but in 2026 the practical choice is a meta-framework:</p>

<ul>
<li><strong>Next.js</strong> &mdash; the most popular React SSR framework; supports static generation, server components, and edge rendering.</li>
<li><strong>Remix / React Router 7</strong> &mdash; data-loader-centric SSR, great for traditional web apps.</li>
<li><strong>Astro</strong> &mdash; ships zero JS by default; excellent for content sites.</li>
<li><strong>TanStack Start</strong> &mdash; newer, file-based, integrates with TanStack Query.</li>
</ul>

<pre><code># Convert a MERN app to Next.js
npx create-next-app@latest client
# Pages live in app/ with built-in SSR
# app/users/[id]/page.jsx
export default async function UserPage({ params }) {
  const user = await fetch(`${process.env.API_URL}/users/${params.id}`).then(r =&gt; r.json())
  return &lt;h1&gt;{user.name}&lt;/h1&gt;
}</code></pre>

<p>SSR adds complexity (server runtime, hydration mismatches, longer Time-to-Interactive) so use it only if you need SEO or fast first paint &mdash; for internal dashboards, a normal SPA is fine. Some teams use <strong>SSR + CDN caching</strong> (Vercel, Cloudflare) so popular pages are served from cache.</p>
'''

ANSWERS[28] = r'''
<p>Performance optimization in MERN spans four layers; tackle each in measured order.</p>

<ul>
<li><strong>Database</strong>: add indexes that match query patterns (<code>db.collection.createIndex</code>); use the aggregation framework over multiple round-trips; lean queries (<code>.lean()</code> in Mongoose returns plain objects, not Mongoose documents); avoid N+1 with <code>$lookup</code> or batched queries.</li>
<li><strong>Backend</strong>: cache hot reads in <strong>Redis</strong>; gzip/brotli responses (<code>compression</code> middleware); stream large responses; profile with <code>--prof</code> or <strong>clinic.js</strong>.</li>
<li><strong>Frontend</strong>: code-split routes with <code>React.lazy</code>; memoize heavy components (<code>React.memo</code>, <code>useMemo</code>); virtualize long lists (<strong>TanStack Virtual</strong>); ship images via <strong>imgix</strong>/<strong>Cloudinary</strong> with <code>loading=&quot;lazy&quot;</code> and modern formats; defer non-critical JS.</li>
<li><strong>Network</strong>: serve static assets through a CDN (<strong>Cloudflare</strong>, <strong>Vercel</strong>); enable HTTP/2 or HTTP/3; preload critical fonts; use <strong>service workers</strong> for offline caching.</li>
</ul>

<pre><code>// Code-splitting in React
const Dashboard = React.lazy(() =&gt; import("./Dashboard"))
&lt;Suspense fallback={&lt;Spinner /&gt;}&gt;&lt;Dashboard /&gt;&lt;/Suspense&gt;</code></pre>

<p>Measure before optimizing &mdash; <strong>Lighthouse</strong> for the frontend, <strong>Datadog APM</strong>/<strong>New Relic</strong> for backend, <strong>MongoDB Atlas Performance Advisor</strong> for queries. Optimizing without numbers is folklore.</p>
'''

ANSWERS[29] = r'''
<p>Dependencies in a MERN app are managed with <strong>npm</strong>, <strong>pnpm</strong>, or <strong>yarn</strong>. The package manager reads <code>package.json</code> (the manifest) and writes <code>package-lock.json</code> / <code>pnpm-lock.yaml</code> / <code>yarn.lock</code> (the exact dependency graph), then downloads everything into <code>node_modules</code>.</p>

<pre><code># Add packages
npm install express mongoose          # runtime deps
npm install -D vitest eslint          # dev-only deps

# Update / audit
npm outdated                          # what&rsquo;s behind?
npm update                            # bump within semver range
npm audit                             # security advisories
npm audit fix                         # auto-fix where possible

# package.json
{
  "engines": { "node": "20.x" },
  "scripts": {
    "dev":   "nodemon src/index.js",
    "start": "node src/index.js",
    "test":  "vitest"
  },
  "dependencies":    { "express": "^4.19.2" },
  "devDependencies": { "vitest":  "^1.6.0" }
}</code></pre>

<p>Best practices: <strong>commit lock files</strong> (they pin exact versions for reproducible installs); use <strong>pnpm</strong> for monorepos &mdash; faster, disk-efficient, and works with workspaces; run <code>npm ci</code> in CI and Docker (it&rsquo;s strict about lockfiles); automate updates with <strong>Renovate</strong> or <strong>Dependabot</strong>; keep dependencies small &mdash; every package is a supply-chain risk; review <code>package-lock.json</code> diffs in PRs to spot unexpected sub-dependency changes.</p>
'''

ANSWERS[30] = r'''
<p><strong>CORS (Cross-Origin Resource Sharing)</strong> is a browser security mechanism: by default a page on <code>https://app.example.com</code> can&rsquo;t make API calls to <code>https://api.example.com</code> unless that API explicitly allows it. In a MERN stack, the React dev server runs on a different port from the Node API, so you hit CORS immediately.</p>

<pre><code>// server &mdash; cors middleware
import cors from "cors"

// Development: allow Vite dev server
app.use(cors({
  origin: "http://localhost:5173",
  credentials: true
}))

// Production: whitelist by env var, never "*" with credentials
const allowed = process.env.CLIENT_URL.split(",")
app.use(cors({
  origin: (origin, cb) =&gt; {
    if (!origin || allowed.includes(origin)) return cb(null, true)
    cb(new Error("Not allowed by CORS"))
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE"]
}))</code></pre>

<p>Two non-obvious points:</p>

<ul>
<li><code>credentials: true</code> requires a specific origin &mdash; the wildcard <code>"*"</code> is rejected by browsers when cookies are sent.</li>
<li>Browsers send a <strong>preflight</strong> <code>OPTIONS</code> request before non-simple methods (PUT, DELETE, JSON bodies); the <code>cors</code> middleware handles this automatically.</li>
</ul>

<p>An alternative: in development, set up a <strong>Vite proxy</strong> that forwards <code>/api/*</code> to the Node server &mdash; same origin, no CORS. In production, deploy both behind the same domain (or use a reverse proxy like Nginx or Caddy) for the same effect.</p>
'''

ANSWERS[31] = r'''
<p><strong>Context API</strong> lets you pass values down the component tree without prop-drilling. It&rsquo;s built into React &mdash; no library &mdash; and is the right fit for app-wide data that rarely changes: theme, current user, locale, feature flags.</p>

<pre><code>// auth/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from "react"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() =&gt; {
    fetch("/api/me", { credentials: "include" })
      .then(r =&gt; r.ok ? r.json() : null)
      .then(setUser)
      .finally(() =&gt; setLoading(false))
  }, [])

  return (
    &lt;AuthContext.Provider value={{ user, setUser, loading }}&gt;
      {children}
    &lt;/AuthContext.Provider&gt;
  )
}

export const useAuth = () =&gt; useContext(AuthContext)

// App.jsx
&lt;AuthProvider&gt;&lt;Router&gt;...&lt;/Router&gt;&lt;/AuthProvider&gt;

// Anywhere
const { user } = useAuth()</code></pre>

<p>What Context is <strong>not</strong> good for: <strong>frequently changing values</strong> shared across many components &mdash; every consumer re-renders on any change, which kills performance. For that, use <strong>Zustand</strong>, <strong>Jotai</strong>, or <strong>Redux Toolkit</strong>, which let consumers subscribe to slices selectively. Avoid putting form state, scroll positions, or animations in Context.</p>
'''

ANSWERS[32] = r'''
<p><strong>State lifting</strong> means moving state up to the closest common parent of two components that need to share it &mdash; instead of letting each component own a private copy that drifts out of sync.</p>

<pre><code>// Before lifting &mdash; inputs don&rsquo;t coordinate
function Celsius()    { const [c, setC] = useState(0); return &lt;input value={c} onChange={...} /&gt; }
function Fahrenheit() { const [f, setF] = useState(32); return &lt;input value={f} onChange={...} /&gt; }

// After lifting &mdash; parent owns the source of truth
function Converter() {
  const [tempC, setTempC] = useState(0)

  return (
    &lt;&gt;
      &lt;Celsius value={tempC} onChange={setTempC} /&gt;
      &lt;Fahrenheit value={tempC * 9/5 + 32}
                  onChange={f =&gt; setTempC((f - 32) * 5/9)} /&gt;
    &lt;/&gt;
  )
}

function Celsius({ value, onChange })    { return &lt;input value={value}    onChange={e =&gt; onChange(+e.target.value)} /&gt; }
function Fahrenheit({ value, onChange }) { return &lt;input value={value} onChange={e =&gt; onChange(+e.target.value)} /&gt; }</code></pre>

<p>The two components become <strong>controlled</strong> &mdash; they receive their value as a prop and call back when the user edits. The parent is the single source of truth.</p>

<p>When lifting goes too far &mdash; ten levels of prop drilling &mdash; switch to <strong>Context</strong> or a state library. The progression is: local state &rarr; lift to parent &rarr; Context &rarr; Zustand/Jotai. Don&rsquo;t skip steps; most apps need very little global state.</p>
'''

ANSWERS[33] = r'''
<p><strong>Hooks</strong> let function components manage state, side effects, and lifecycle without classes. They were introduced in React 16.8 and are now the default way to write React. The most-used built-in hooks:</p>

<ul>
<li><code>useState</code> &mdash; local component state.</li>
<li><code>useEffect</code> &mdash; run side effects (fetching, subscriptions, DOM work) after render.</li>
<li><code>useContext</code> &mdash; read a Context value.</li>
<li><code>useMemo</code> &mdash; cache an expensive computed value.</li>
<li><code>useCallback</code> &mdash; cache a function reference.</li>
<li><code>useRef</code> &mdash; persist a mutable value across renders without causing re-renders.</li>
<li><code>useReducer</code> &mdash; alternative to <code>useState</code> for complex state transitions.</li>
</ul>

<pre><code>function UserProfile({ userId }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() =&gt; {
    let active = true
    fetch(`/api/users/${userId}`)
      .then(r =&gt; r.json())
      .then(u =&gt; active &amp;&amp; setUser(u))
      .finally(() =&gt; active &amp;&amp; setLoading(false))
    return () =&gt; { active = false }    // cleanup on unmount
  }, [userId])

  if (loading) return &lt;Spinner /&gt;
  return &lt;div&gt;{user.name}&lt;/div&gt;
}</code></pre>

<p>Two rules: <strong>only call hooks at the top level</strong> (never inside loops or conditionals) and <strong>only from React functions</strong>. The <strong>eslint-plugin-react-hooks</strong> plugin catches violations automatically. Custom hooks (functions starting with <code>use</code>) compose existing hooks for reuse.</p>
'''

ANSWERS[34] = r'''
<p>Testing a MERN app means three layers: <strong>unit</strong> (pure functions, components in isolation), <strong>integration</strong> (a route plus its database), and <strong>end-to-end</strong> (a real browser driving the whole app). The modern stack:</p>

<ul>
<li><strong>Vitest</strong> or <strong>Jest</strong> &mdash; test runner for both client and server.</li>
<li><strong>React Testing Library</strong> &mdash; query and assert against rendered components.</li>
<li><strong>Supertest</strong> &mdash; in-process HTTP requests against an Express app.</li>
<li><strong>Playwright</strong> or <strong>Cypress</strong> &mdash; browser automation for E2E.</li>
<li><strong>MSW (Mock Service Worker)</strong> &mdash; intercept and mock API calls in component tests.</li>
</ul>

<pre><code>// Unit + component test
import { render, screen } from "@testing-library/react"
test("renders greeting", () =&gt; {
  render(&lt;Hello name="Alice" /&gt;)
  expect(screen.getByText(/hello, alice/i)).toBeInTheDocument()
})

// Integration test for an Express route
import request from "supertest"
import app from "../src/app.js"
test("GET /api/users returns 200", async () =&gt; {
  const res = await request(app).get("/api/users")
  expect(res.status).toBe(200)
  expect(Array.isArray(res.body)).toBe(true)
})

// E2E with Playwright
test("user logs in", async ({ page }) =&gt; {
  await page.goto("/login")
  await page.fill('[name="email"]', "alice@example.com")
  await page.fill('[name="password"]', "password")
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL("/dashboard")
})</code></pre>

<p>Run unit and integration tests on every commit in CI; run E2E in a deploy-preview environment. Use a separate <strong>test database</strong> &mdash; <strong>mongodb-memory-server</strong> spins up an in-memory MongoDB for fast, isolated runs.</p>
'''

ANSWERS[35] = r'''
<p>Session management is how the server remembers <em>who</em> is making each request after they log in. Two approaches dominate in MERN apps: <strong>stateless JWT tokens</strong> and <strong>stateful sessions backed by a store</strong>.</p>

<pre><code>// 1. Stateless: JWT in an httpOnly cookie or Authorization header
import jwt from "jsonwebtoken"
const token = jwt.sign({ uid: user._id }, process.env.JWT_SECRET, { expiresIn: "15m" })
res.cookie("token", token, { httpOnly: true, secure: true, sameSite: "strict" })

// 2. Stateful: express-session + Redis
import session from "express-session"
import RedisStore from "connect-redis"
import { createClient } from "redis"

const redisClient = createClient({ url: process.env.REDIS_URL })
await redisClient.connect()

app.use(session({
  store:   new RedisStore({ client: redisClient }),
  secret:  process.env.SESSION_SECRET,
  resave:  false,
  saveUninitialized: false,
  cookie:  { httpOnly: true, secure: true, sameSite: "strict", maxAge: 86400000 }
}))

// Then in routes
req.session.userId = user._id
const user = await User.findById(req.session.userId)</code></pre>

<p>Trade-offs: JWTs scale horizontally (no shared store) but are hard to revoke before expiry. Sessions revoke instantly (delete from Redis) but need a shared store across server instances. Modern apps often use a hybrid: <strong>short-lived JWT access tokens</strong> + <strong>long-lived refresh tokens</strong> stored server-side. Or outsource the whole concern to <strong>Auth0</strong>, <strong>Clerk</strong>, <strong>WorkOS</strong>, or <strong>Supabase Auth</strong>.</p>
'''

ANSWERS[36] = r'''
<p>A <strong>JSON Web Token (JWT)</strong> is a signed, base64-encoded string that carries claims about a user. The server signs it on login; the client sends it on every subsequent request; the server verifies the signature and trusts the claims without a database lookup &mdash; that&rsquo;s the &ldquo;stateless&rdquo; part.</p>

<pre><code>// server &mdash; sign and verify
import jwt from "jsonwebtoken"

// Login: sign
const token = jwt.sign(
  { uid: user._id, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: "15m" }                     // short-lived
)

// Middleware: verify on each request
function auth(req, res, next) {
  const header = req.headers.authorization
  if (!header) return res.status(401).json({ error: "no_token" })
  try {
    req.user = jwt.verify(header.replace("Bearer ", ""), process.env.JWT_SECRET)
    next()
  } catch {
    res.status(401).json({ error: "invalid_token" })
  }
}

// Protect routes
app.get("/api/me", auth, (req, res) =&gt; res.json(req.user))</code></pre>

<p>JWT structure: <code>header.payload.signature</code>. The payload is base64-encoded but <strong>not encrypted</strong> &mdash; never put secrets in there. Production essentials:</p>

<ul>
<li><strong>Short expiry</strong> (15 min) plus a refresh token for renewal &mdash; limits damage if a token leaks.</li>
<li><strong>Strong secret</strong> (32+ random bytes); rotate periodically.</li>
<li><strong>Asymmetric signing</strong> (RS256) for distributed services that verify but don&rsquo;t mint tokens.</li>
<li><strong>httpOnly cookies</strong> beat <code>localStorage</code> &mdash; XSS can&rsquo;t read them.</li>
<li><strong>Use a library</strong> &mdash; <code>jsonwebtoken</code> or hosted (<strong>Auth0</strong>, <strong>Clerk</strong>); never roll your own crypto.</li>
</ul>
'''

ANSWERS[37] = r'''
<p><strong>Role-based access control (RBAC)</strong> assigns each user a role (admin, editor, viewer), and each route checks whether the user&rsquo;s role can perform the requested action. The server is the only authoritative checkpoint &mdash; UI hiding is convenience, not security.</p>

<pre><code>// User model has a role field
const userSchema = new mongoose.Schema({
  email: String,
  passwordHash: String,
  role:  { type: String, enum: ["viewer", "editor", "admin"], default: "viewer" }
})

// Reusable middleware that takes allowed roles
function requireRole(...allowed) {
  return (req, res, next) =&gt; {
    if (!req.user) return res.status(401).json({ error: "unauthenticated" })
    if (!allowed.includes(req.user.role))
      return res.status(403).json({ error: "forbidden" })
    next()
  }
}

// Apply to specific routes
app.delete("/api/posts/:id", auth, requireRole("admin", "editor"), deletePost)
app.get("/api/admin/users",   auth, requireRole("admin"),          listUsers)

// On the React side: hide controls (UX only, not security)
const { user } = useAuth()
{user?.role === "admin" &amp;&amp; &lt;DeleteButton /&gt;}</code></pre>

<p>Beyond roles, sometimes you need <strong>resource ownership</strong> &mdash; &ldquo;can edit only their own posts&rdquo;. Add a check in the handler: <code>if (post.author !== req.user.uid &amp;&amp; req.user.role !== &quot;admin&quot;) return 403</code>. For complex policies (Google Docs-style sharing, GitHub teams), use a dedicated authz service: <strong>SpiceDB</strong>, <strong>OpenFGA</strong>, <strong>Cerbos</strong>, or <strong>AWS Verified Permissions</strong>.</p>
'''

ANSWERS[38] = r'''
<p>A complete RESTful API combines <strong>routes</strong>, <strong>controllers</strong>, and <strong>Mongoose models</strong> in a clean separation of concerns. Each resource gets one router with the five canonical operations.</p>

<pre><code>// models/Post.js
import mongoose from "mongoose"
const postSchema = new mongoose.Schema({
  title:  { type: String, required: true },
  body:   String,
  author: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  tags:   [String]
}, { timestamps: true })
export default mongoose.model("Post", postSchema)

// controllers/posts.js
import Post from "../models/Post.js"
export const list   = async (req, res) =&gt; res.json(await Post.find().sort({ createdAt: -1 }))
export const get    = async (req, res) =&gt; {
  const post = await Post.findById(req.params.id).populate("author", "name email")
  if (!post) return res.status(404).json({ error: "not_found" })
  res.json(post)
}
export const create = async (req, res) =&gt; {
  const post = await Post.create({ ...req.body, author: req.user.uid })
  res.status(201).json(post)
}
export const update = async (req, res) =&gt; {
  const post = await Post.findOneAndUpdate(
    { _id: req.params.id, author: req.user.uid },
    req.body,
    { new: true, runValidators: true }
  )
  if (!post) return res.status(404).json({ error: "not_found" })
  res.json(post)
}
export const remove = async (req, res) =&gt; {
  await Post.deleteOne({ _id: req.params.id, author: req.user.uid })
  res.status(204).end()
}

// routes/posts.js
const router = express.Router()
router.get("/",       list)
router.get("/:id",    get)
router.post("/",      auth,    create)
router.put("/:id",    auth,    update)
router.delete("/:id", auth,    remove)
app.use("/api/posts", router)</code></pre>

<p>Always validate request bodies with <strong>Zod</strong>; return consistent error JSON; paginate list endpoints; index fields you query and sort on.</p>
'''

ANSWERS[39] = r'''
<p>MongoDB is schemaless at the database level &mdash; you can add fields to new documents without ceremony. But real apps still need <strong>migrations</strong> to backfill old documents, rename fields, or change indexes safely. Two patterns work in practice.</p>

<p><strong>Pattern 1: Schema versioning + lazy migration.</strong> Tag each document with a <code>schemaVersion</code>. The application reads multiple versions; new writes always use the latest shape; a background job rewrites old documents in batches.</p>

<pre><code>// Model
const userSchema = new mongoose.Schema({
  schemaVersion: { type: Number, default: 2 },
  name:  { first: String, last: String },   // v2 nested
  email: String
})

// Lazy migration in app code
function readUser(doc) {
  if (doc.schemaVersion === 2) return doc
  return { ...doc.toObject(), name: { first: doc.firstName, last: doc.lastName }, schemaVersion: 2 }
}

// Background migrator (BullMQ job)
async function migrateBatch() {
  const batch = await User.find({ schemaVersion: 1 }).limit(1000)
  for (const u of batch) {
    await User.updateOne(
      { _id: u._id, schemaVersion: 1 },
      { $set: { name: { first: u.firstName, last: u.lastName }, schemaVersion: 2 },
        $unset: { firstName: "", lastName: "" } }
    )
  }
}</code></pre>

<p><strong>Pattern 2: Migration tools.</strong> Libraries like <strong>migrate-mongo</strong> or <strong>mongock</strong> store applied migrations in a <code>changelog</code> collection &mdash; same idea as Rails or Flyway. Each migration has an <code>up</code> and <code>down</code> function. Run them in CI before deploying the app version that depends on them.</p>

<p>For very large collections, always migrate in <strong>batches with sleep</strong> to avoid replica lag and oplog overflow.</p>
'''

ANSWERS[40] = r'''
<p><strong>Styled-components</strong> (and friends like <strong>Emotion</strong>) put your CSS inside JavaScript: every styled component is a regular React component with scoped, prop-aware styles. The styles are generated at runtime, scoped by hashed class names, and injected into a <code>&lt;style&gt;</code> tag.</p>

<pre><code>import styled, { css } from "styled-components"

const Button = styled.button`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: ${props =&gt; props.primary ? "#0070f3" : "#eee"};
  color:      ${props =&gt; props.primary ? "white"   : "#333"};
  cursor: pointer;

  &amp;:hover {
    opacity: 0.9;
  }

  ${props =&gt; props.large &amp;&amp; css`
    padding: 1rem 2rem;
    font-size: 1.25rem;
  `}
`

// Use like any React component
&lt;Button primary large onClick={save}&gt;Save&lt;/Button&gt;</code></pre>

<p>Pros: styles co-located with components, no global CSS conflicts, dynamic styling based on props, automatic vendor prefixing. Cons: runtime cost (slower than static CSS), bundle size, awkward server-side rendering, and React 19 introduced friction with the streaming SSR model.</p>

<p>2026 alternatives that are increasingly preferred:</p>

<ul>
<li><strong>Tailwind CSS</strong> &mdash; utility classes, zero runtime, the dominant choice in new MERN apps.</li>
<li><strong>CSS Modules</strong> &mdash; scoped CSS files (<code>Button.module.css</code>) with no runtime.</li>
<li><strong>Vanilla Extract</strong> / <strong>StyleX</strong> &mdash; static CSS-in-TS, type-safe, fast.</li>
<li><strong>Panda CSS</strong> &mdash; build-time CSS-in-JS with zero runtime.</li>
</ul>
'''

ANSWERS[41] = r'''
<p>Form state in React means tracking what the user has typed, validation errors, submission status, and dirty/touched flags. The most common approaches range from a few <code>useState</code> hooks to dedicated libraries.</p>

<pre><code>// Hand-rolled with useState (fine for small forms)
function LoginForm() {
  const [email, setEmail]     = useState("")
  const [password, setPwd]    = useState("")
  const [errors, setErrors]   = useState({})
  const [submitting, setSubm] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setSubm(true)
    try {
      await api.login({ email, password })
    } catch (err) {
      setErrors({ form: err.message })
    } finally {
      setSubm(false)
    }
  }

  return (
    &lt;form onSubmit={onSubmit}&gt;
      &lt;input value={email} onChange={e =&gt; setEmail(e.target.value)} /&gt;
      ...
    &lt;/form&gt;
  )
}

// React Hook Form &mdash; the modern default
import { useForm } from "react-hook-form"
const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm()

&lt;form onSubmit={handleSubmit(onSubmit)}&gt;
  &lt;input {...register("email", { required: true })} /&gt;
  &lt;input {...register("password", { minLength: 8 })} /&gt;
  &lt;button disabled={isSubmitting}&gt;Login&lt;/button&gt;
&lt;/form&gt;</code></pre>

<p><strong>React Hook Form</strong> is the dominant 2026 choice &mdash; uncontrolled inputs (no re-render on every keystroke), tiny bundle, ergonomic validation via <strong>Zod</strong>/<strong>Yup</strong> resolvers. <strong>Formik</strong> is the older alternative; <strong>TanStack Form</strong> is the newer competitor with even better TypeScript ergonomics.</p>
'''

ANSWERS[42] = r'''
<p>Conditional rendering shows different UI based on data &mdash; loading states, errors, auth status, feature flags. JSX has several idioms; pick whichever reads cleanest in context.</p>

<pre><code>// 1. Ternary (when there are exactly two cases)
{isLoggedIn ? &lt;Dashboard /&gt; : &lt;LoginPrompt /&gt;}

// 2. Logical AND (when there&rsquo;s nothing for the false case)
{user.isAdmin &amp;&amp; &lt;AdminPanel /&gt;}

// 3. Early return (when the whole component depends on it)
function Profile() {
  const { data, isLoading, error } = useQuery(...)
  if (isLoading) return &lt;Spinner /&gt;
  if (error)     return &lt;ErrorMessage error={error} /&gt;
  if (!data)     return &lt;Empty /&gt;
  return &lt;ProfileView data={data} /&gt;
}

// 4. Lookup table (when there are many cases)
const states = {
  idle:    () =&gt; &lt;Idle /&gt;,
  loading: () =&gt; &lt;Spinner /&gt;,
  error:   () =&gt; &lt;ErrorMessage /&gt;,
  ready:   () =&gt; &lt;Dashboard /&gt;
}
return states[status]()

// 5. Conditional class names (CSS modes)
&lt;div className={`alert ${kind === "error" ? "alert-red" : "alert-green"}`} /&gt;</code></pre>

<p>Watch out for two pitfalls. First, <code>{count &amp;&amp; &lt;X /&gt;}</code> renders the literal <code>0</code> when <code>count</code> is zero &mdash; use <code>{count &gt; 0 &amp;&amp; &lt;X /&gt;}</code> instead. Second, deep ternary nesting is hard to read &mdash; refactor to an early return or extract a small component.</p>
'''

ANSWERS[43] = r'''
<p>A search feature in MERN spans three pieces: a debounced React input, a server endpoint that filters MongoDB, and an index that makes the query fast. For non-trivial search, plug in <strong>Atlas Search</strong> or <strong>Meilisearch</strong>/<strong>Typesense</strong>/<strong>Algolia</strong> &mdash; regex queries don&rsquo;t scale.</p>

<pre><code>// MongoDB text index (simple)
postSchema.index({ title: "text", body: "text" })

// Express endpoint
router.get("/search", async (req, res) =&gt; {
  const q = req.query.q?.trim()
  if (!q) return res.json([])
  const results = await Post.find(
    { $text: { $search: q } },
    { score: { $meta: "textScore" } }
  ).sort({ score: { $meta: "textScore" } }).limit(20)
  res.json(results)
})

// React &mdash; debounced search input
import { useState, useEffect } from "react"
function Search() {
  const [q, setQ]           = useState("")
  const [results, setRes]   = useState([])

  useEffect(() =&gt; {
    if (!q) return setRes([])
    const t = setTimeout(async () =&gt; {
      const r = await fetch(`/api/search?q=${encodeURIComponent(q)}`).then(r =&gt; r.json())
      setRes(r)
    }, 250)                              // 250ms debounce
    return () =&gt; clearTimeout(t)
  }, [q])

  return (
    &lt;&gt;
      &lt;input value={q} onChange={e =&gt; setQ(e.target.value)} /&gt;
      {results.map(r =&gt; &lt;ResultItem key={r._id} {...r} /&gt;)}
    &lt;/&gt;
  )
}</code></pre>

<p>For real search needs &mdash; typo tolerance, faceting, ranking, autocomplete &mdash; <strong>Atlas Search</strong> (MongoDB&rsquo;s built-in Lucene) is the best fit in MERN. <strong>Algolia</strong> and <strong>Typesense</strong> are excellent hosted alternatives. <strong>TanStack Query</strong> with <code>keepPreviousData</code> makes the UI feel smoother during typing.</p>
'''

ANSWERS[44] = r'''
<p>Browsers ship with <strong><code>fetch</code></strong>, a Promise-based HTTP client. <strong>Axios</strong> is a popular library that adds interceptors, automatic JSON, and better error handling. Both are common in MERN; in 2026 most teams use either fetch + a tiny wrapper or jump straight to <strong>TanStack Query</strong>.</p>

<pre><code>// fetch &mdash; native, no dependency
async function getUser(id) {
  const res = await fetch(`/api/users/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

// Axios &mdash; quality-of-life upgrades
import axios from "axios"
const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" }
})
api.interceptors.request.use(cfg =&gt; {
  const token = localStorage.getItem("token")
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})
api.interceptors.response.use(
  r =&gt; r,
  err =&gt; { if (err.response?.status === 401) redirectToLogin(); throw err }
)
const user = (await api.get(`/users/${id}`)).data

// TanStack Query &mdash; what most teams now use
const { data, error, isLoading } = useQuery({
  queryKey: ["user", id],
  queryFn:  () =&gt; api.get(`/users/${id}`).then(r =&gt; r.data)
})</code></pre>

<p>Differences: fetch doesn&rsquo;t throw on 4xx/5xx (you check <code>res.ok</code>), needs explicit <code>res.json()</code>, and has manual interceptor logic. Axios reduces boilerplate but adds 13kB. <strong>TanStack Query</strong> is orthogonal &mdash; it wraps either, adding caching, deduplication, refetching, and loading/error states. Modern alternatives include <strong>ky</strong> (fetch wrapper) and <strong>ofetch</strong>.</p>
'''

ANSWERS[45] = r'''
<p>Nested routes render child routes inside a parent layout &mdash; perfect for dashboards where a sidebar stays put while the main panel changes. <strong>React Router v6/v7</strong> handles this with the <code>Outlet</code> component.</p>

<pre><code>// client/src/App.jsx
import { BrowserRouter, Routes, Route, Outlet, Link, NavLink } from "react-router-dom"

function DashboardLayout() {
  return (
    &lt;div style={{ display: "flex" }}&gt;
      &lt;nav&gt;
        &lt;NavLink to="/dashboard"&gt;Overview&lt;/NavLink&gt;
        &lt;NavLink to="/dashboard/users"&gt;Users&lt;/NavLink&gt;
        &lt;NavLink to="/dashboard/settings"&gt;Settings&lt;/NavLink&gt;
      &lt;/nav&gt;
      &lt;main&gt;
        &lt;Outlet /&gt;             {/* child route renders here */}
      &lt;/main&gt;
    &lt;/div&gt;
  )
}

&lt;BrowserRouter&gt;
  &lt;Routes&gt;
    &lt;Route path="/dashboard" element={&lt;DashboardLayout /&gt;}&gt;
      &lt;Route index           element={&lt;Overview /&gt;} /&gt;            {/* /dashboard      */}
      &lt;Route path="users"    element={&lt;UsersList /&gt;} /&gt;           {/* /dashboard/users */}
      &lt;Route path="users/:id" element={&lt;UserDetail /&gt;} /&gt;
      &lt;Route path="settings" element={&lt;Settings /&gt;} /&gt;
    &lt;/Route&gt;
  &lt;/Routes&gt;
&lt;/BrowserRouter&gt;</code></pre>

<p>The parent <code>DashboardLayout</code> renders once; children mount and unmount as the URL changes &mdash; no flicker, no re-fetch of shared data. <code>NavLink</code> automatically gets an <code>active</code> class when the URL matches, which is handy for highlighting the current section.</p>

<p>For deeply nested apps, this pattern composes &mdash; a layout&rsquo;s <code>Outlet</code> can host another layout, which has its own <code>Outlet</code>. Modern Next.js, Remix, and TanStack Router formalize the same idea with file-based routes.</p>
'''

ANSWERS[46] = r'''
<p>A loading spinner reassures users that something is happening when an async operation is in flight. Show one whenever a fetch, mutation, or navigation takes longer than a heartbeat &mdash; but not for the first 200&ndash;300ms (avoids spinner flash on fast networks).</p>

<pre><code>// Reusable Spinner component
function Spinner({ size = 24 }) {
  return (
    &lt;div className="spinner" style={{ width: size, height: size }} role="status" aria-label="Loading" /&gt;
  )
}

/* CSS */
.spinner {
  border: 3px solid #eee;
  border-top: 3px solid #0070f3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

// With TanStack Query &mdash; the modern data flow
function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn:  () =&gt; fetch("/api/users").then(r =&gt; r.json())
  })

  if (isLoading) return &lt;Spinner /&gt;
  if (error)     return &lt;ErrorMessage error={error} /&gt;
  return data.map(u =&gt; &lt;UserItem key={u._id} {...u} /&gt;)
}

// On submit buttons
&lt;button disabled={isSubmitting}&gt;
  {isSubmitting ? &lt;Spinner size={16} /&gt; : "Save"}
&lt;/button&gt;</code></pre>

<p>Better UX patterns when you can: <strong>skeleton screens</strong> (shaded placeholders matching the final layout) feel faster than spinners; <strong>optimistic updates</strong> show the new state instantly and roll back on failure; for navigation, React 18&rsquo;s <code>useTransition</code> keeps the old UI visible while the next page loads. Always include <code>aria-label="Loading"</code> for accessibility.</p>
'''

ANSWERS[47] = r'''
<p>Scroll handling in React is needed for infinite lists, sticky headers, scroll-restoration, and animation triggers. Always <strong>throttle</strong> scroll listeners &mdash; they fire dozens of times per second.</p>

<pre><code>// Basic scroll listener with throttling
import { useEffect, useState } from "react"

function useScrollY(throttleMs = 100) {
  const [y, setY] = useState(0)
  useEffect(() =&gt; {
    let last = 0
    function onScroll() {
      const now = Date.now()
      if (now - last &lt; throttleMs) return
      last = now
      setY(window.scrollY)
    }
    window.addEventListener("scroll", onScroll, { passive: true })
    return () =&gt; window.removeEventListener("scroll", onScroll)
  }, [throttleMs])
  return y
}

// Modern: IntersectionObserver for "load more when reaching bottom"
function InfiniteList({ items, onLoadMore }) {
  const ref = useRef()
  useEffect(() =&gt; {
    const obs = new IntersectionObserver(([entry]) =&gt; {
      if (entry.isIntersecting) onLoadMore()
    })
    if (ref.current) obs.observe(ref.current)
    return () =&gt; obs.disconnect()
  }, [onLoadMore])

  return (
    &lt;&gt;
      {items.map(i =&gt; &lt;Item key={i.id} {...i} /&gt;)}
      &lt;div ref={ref} style={{ height: 1 }} /&gt;
    &lt;/&gt;
  )
}</code></pre>

<p>Three rules: use <code>{ passive: true }</code> on scroll listeners so they don&rsquo;t block scrolling; remove the listener in the cleanup function (otherwise memory leaks on unmount); prefer <strong>IntersectionObserver</strong> over scroll events for &ldquo;is this element visible&rdquo; checks &mdash; it&rsquo;s built into the browser, fires only on threshold crossing, and doesn&rsquo;t block the main thread.</p>

<p>For long lists, virtualize with <strong>TanStack Virtual</strong> or <strong>react-window</strong> &mdash; only renders the rows currently in the viewport.</p>
'''

ANSWERS[48] = r'''
<p>The <strong>aggregation framework</strong> is MongoDB&rsquo;s pipeline-based query language for transforming data &mdash; the equivalent of SQL <code>GROUP BY</code>, joins, and CTEs. A pipeline is an array of stages; each stage takes documents in and emits documents out.</p>

<pre><code>// Top 5 authors by post count, with average reactions
const result = await Post.aggregate([
  { $match:  { status: "published" } },                 // filter
  { $group:  {
      _id:           "$authorId",
      postCount:     { $sum: 1 },
      avgReactions:  { $avg: "$reactions" }
  }},
  { $sort:   { postCount: -1 } },
  { $limit:  5 },
  { $lookup: {                                          // join with users
      from:         "users",
      localField:   "_id",
      foreignField: "_id",
      as:           "author"
  }},
  { $unwind: "$author" },
  { $project: {                                         // shape the output
      _id: 0,
      name:         "$author.name",
      postCount:    1,
      avgReactions: { $round: ["$avgReactions", 1] }
  }}
])</code></pre>

<p>Common stages:</p>

<ul>
<li><code>$match</code> &mdash; filter (use <em>before</em> heavy stages so indexes apply).</li>
<li><code>$group</code> &mdash; group by a key, run accumulators (<code>$sum</code>, <code>$avg</code>, <code>$min</code>, <code>$max</code>, <code>$push</code>, <code>$addToSet</code>).</li>
<li><code>$lookup</code> &mdash; left outer join to another collection.</li>
<li><code>$project</code>/<code>$set</code>/<code>$unset</code> &mdash; reshape documents.</li>
<li><code>$unwind</code> &mdash; flatten an array field into one doc per element.</li>
<li><code>$sort</code>, <code>$limit</code>, <code>$skip</code>, <code>$facet</code>, <code>$bucket</code>.</li>
</ul>

<p>For analytics dashboards, write to a materialized rollup with <code>$merge</code> or <code>$out</code> instead of recomputing each time. <strong>MongoDB Compass</strong> has a visual pipeline builder &mdash; great for prototyping.</p>
'''

ANSWERS[49] = r'''
<p>A <strong>custom hook</strong> is just a function whose name starts with <code>use</code> and that calls other hooks. They let you bundle stateful logic for reuse &mdash; the same way regular functions bundle pure logic.</p>

<pre><code>// useLocalStorage &mdash; sync a piece of state with localStorage
import { useState, useEffect } from "react"

function useLocalStorage(key, initial) {
  const [value, setValue] = useState(() =&gt; {
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : initial
  })

  useEffect(() =&gt; {
    localStorage.setItem(key, JSON.stringify(value))
  }, [key, value])

  return [value, setValue]
}

// Usage &mdash; identical to useState
function Settings() {
  const [theme, setTheme] = useLocalStorage("theme", "light")
  return &lt;button onClick={() =&gt; setTheme(t =&gt; t === "light" ? "dark" : "light")}&gt;{theme}&lt;/button&gt;
}

// useDebounce &mdash; delay a rapidly-changing value
function useDebounce(value, ms = 300) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() =&gt; {
    const t = setTimeout(() =&gt; setDebounced(value), ms)
    return () =&gt; clearTimeout(t)
  }, [value, ms])
  return debounced
}

// useMediaQuery &mdash; respond to viewport changes
function useMediaQuery(query) {
  const [match, setMatch] = useState(false)
  useEffect(() =&gt; {
    const m = window.matchMedia(query)
    setMatch(m.matches)
    const handler = e =&gt; setMatch(e.matches)
    m.addEventListener("change", handler)
    return () =&gt; m.removeEventListener("change", handler)
  }, [query])
  return match
}</code></pre>

<p>Custom hooks must follow the <strong>rules of hooks</strong> (only call other hooks at the top level). They&rsquo;re the canonical way to share logic between components in modern React &mdash; replacing the old patterns of HOCs and render props. Many production apps have a <code>hooks/</code> folder full of these utilities.</p>
'''

ANSWERS[50] = r'''
<p>In class components, lifecycle was three named methods: <code>componentDidMount</code>, <code>componentDidUpdate</code>, <code>componentWillUnmount</code>. With function components and hooks, lifecycle collapses into one tool: <strong><code>useEffect</code></strong>.</p>

<pre><code>import { useEffect } from "react"

// Run once on mount (empty deps array)
useEffect(() =&gt; {
  console.log("mounted")
}, [])

// Run when value changes (componentDidUpdate equivalent)
useEffect(() =&gt; {
  console.log("count is now", count)
}, [count])

// Run on every render (rare; usually you want deps)
useEffect(() =&gt; { /* every render */ })

// Cleanup &mdash; runs before next effect AND on unmount
useEffect(() =&gt; {
  const id = setInterval(tick, 1000)
  return () =&gt; clearInterval(id)
}, [])

// Subscriptions &mdash; classic example
useEffect(() =&gt; {
  const unsub = socket.on("message", handle)
  return () =&gt; unsub()
}, [socket])</code></pre>

<p>The dependency array is what catches people. <strong>Include every value the effect uses</strong> from the surrounding scope, otherwise the effect will close over stale values. The <code>react-hooks/exhaustive-deps</code> ESLint rule is mandatory in any serious project &mdash; let it auto-add what you forgot.</p>

<p>Other lifecycle-ish hooks:</p>

<ul>
<li><code>useLayoutEffect</code> &mdash; runs synchronously after DOM mutation, before browser paint (use rarely, for layout reads/writes).</li>
<li><code>useInsertionEffect</code> &mdash; for CSS-in-JS libraries, runs before everything else.</li>
</ul>

<p>For data fetching specifically, <strong>don&rsquo;t use <code>useEffect</code></strong> &mdash; use <strong>TanStack Query</strong> or <strong>SWR</strong>, which handle caching, refetching, and race conditions correctly.</p>
'''


ANSWERS[51] = r'''
<p>A dark mode toggle has three pieces: detecting preference, applying styles, and persisting the choice.</p>
<pre><code>// useTheme.ts
import { useEffect, useState } from "react";
type Theme = "light" | "dark" | "system";

export function useTheme() {
  const [theme, setTheme] = useState&lt;Theme&gt;(
    () =&gt; (localStorage.getItem("theme") as Theme) ?? "system"
  );

  useEffect(() =&gt; {
    const root = document.documentElement;
    const dark = theme === "dark" ||
      (theme === "system" &amp;&amp; matchMedia("(prefers-color-scheme: dark)").matches);
    root.classList.toggle("dark", dark);
    localStorage.setItem("theme", theme);
  }, [theme]);

  return [theme, setTheme] as const;
}</code></pre>
<p>Tailwind CSS reads the <code>.dark</code> class for <code>dark:bg-gray-900</code> styles; CSS-in-JS libraries (<strong>styled-components</strong>, <strong>Emotion</strong>, <strong>vanilla-extract</strong>) read a theme prop. To prevent a <strong>flash of wrong theme</strong> on load, add a small <em>blocking</em> script in <code>index.html</code> that sets the class before React hydrates &mdash; this is what <strong>next-themes</strong> does in Next.js. Honor <code>prefers-color-scheme</code> as the default; let users override and remember the choice. Make sure focus-visible, syntax highlighting, and chart colors all have dark variants &mdash; the &ldquo;just invert colors&rdquo; trap is a common 2026 mistake.</p>
'''

ANSWERS[52] = r'''
<p>Large data sets in MERN are handled by <strong>not loading them all at once</strong>. Strategies stack:</p>
<ul>
<li><strong>Pagination</strong> &mdash; cursor-based for feeds, offset for admin tables. Index the sort key.</li>
<li><strong>Server-side filtering and aggregation</strong> &mdash; let MongoDB do the work; never <code>find()</code> a million docs and filter in Node.</li>
<li><strong>Selective projection</strong> &mdash; <code>.select("title author")</code> returns only needed fields, lighter wire and parsing.</li>
<li><strong>Streaming</strong> &mdash; for exports, use <code>cursor.stream()</code> and pipe to the response without loading the full set.</li>
<li><strong>Indexes</strong> &mdash; the single biggest lever. Compound indexes following equality &rarr; sort &rarr; range (ESR rule).</li>
<li><strong>Aggregation pipeline</strong> &mdash; pre-compute summaries with <code>$merge</code> into rollup collections.</li>
<li><strong>Search</strong> &mdash; for text-heavy queries, <strong>Atlas Search</strong> (Lucene) outperforms <code>$regex</code>.</li>
</ul>
<p>On the React side: <strong>virtualized lists</strong> via <strong>TanStack Virtual</strong>/<strong>react-window</strong> render only the rows in view; <strong>code splitting</strong> avoids shipping unused JS; <strong>TanStack Query</strong>&rsquo;s <code>useInfiniteQuery</code> handles infinite scroll. For very large data, push computation to a warehouse (<strong>BigQuery</strong>/<strong>ClickHouse</strong>/<strong>Snowflake</strong>) and only show summaries in the app. Profile queries with <code>explain("executionStats")</code>; profile React with the React DevTools Profiler.</p>
'''

ANSWERS[53] = r'''
<p><strong>Socket.io</strong> is the most popular WebSocket library for Node. It gracefully falls back to long-polling when WebSockets are blocked and provides rooms, namespaces, and acks on top of raw WS.</p>
<pre><code>// server
import { Server } from "socket.io";
const io = new Server(httpServer, { cors: { origin: "http://localhost:5173" } });

io.on("connection", (socket) =&gt; {
  socket.on("join", (roomId) =&gt; socket.join(roomId));
  socket.on("message", ({ roomId, text }) =&gt; {
    io.to(roomId).emit("message", { user: socket.data.user, text, ts: Date.now() });
  });
});

// client
import { io } from "socket.io-client";
const socket = io(import.meta.env.VITE_API_URL, { withCredentials: true });
socket.emit("join", "room-42");
socket.on("message", (m) =&gt; addMessage(m));</code></pre>
<p>Use cases: chat, presence, live cursors, notifications. Beyond a single Node process, you need a <strong>Redis adapter</strong> (<code>@socket.io/redis-adapter</code>) so messages broadcast across instances. Authenticate the connection with the same JWT/session cookie as your REST API. Modern alternatives in 2026: <strong>Pusher</strong>/<strong>Ably</strong>/<strong>PubNub</strong> (managed); <strong>Supabase Realtime</strong>; <strong>PartyKit</strong>/<strong>Liveblocks</strong>/<strong>Convex</strong> (rooms-as-objects); <strong>Cloudflare Durable Objects</strong> (sticky-routed WS); raw <strong>ws</strong>/<strong>uWebSockets.js</strong> for performance. Pick managed unless you have a specific reason &mdash; running WebSockets at scale is operationally painful.</p>
'''

ANSWERS[54] = r'''
<p>A notification system in MERN typically has three parts: <strong>creation</strong>, <strong>delivery</strong>, and <strong>display</strong>.</p>
<pre><code>// 1. Persist (one notification per user)
db.notifications.insertOne({
  user_id: ObjectId("..."),
  type: "mention",
  title: "Alice mentioned you",
  url: "/posts/123",
  read: false,
  created_at: new Date()
});

// 2. Push live to the user via socket.io / Pusher / Ably
io.to(`user:${userId}`).emit("notification", payload);

// 3. Persistent fallback &mdash; APN/FCM push, email, SMS
await knock.notify("post.mentioned", { recipients: [userId], data: { ... } });</code></pre>
<p>UI side: a bell icon shows the unread count from <code>GET /api/notifications/unread-count</code>; a dropdown lists recent ones; clicking marks read. Use <strong>TanStack Query</strong> with optimistic updates for instant unread-count changes. For multi-channel delivery (in-app + push + email + SMS), use a notification platform: <strong>Knock</strong>, <strong>Courier</strong>, <strong>Customer.io</strong>, <strong>Novu</strong>, <strong>OneSignal</strong>. They handle preferences, quiet hours, digesting, A/B testing, and channel fallback. For just push: <strong>Firebase Cloud Messaging (FCM)</strong> for Android, <strong>APNs</strong> for iOS, <strong>Web Push</strong> for browsers via service worker. Mark notifications read in batches; rate-limit per user; respect quiet hours.</p>
'''

ANSWERS[55] = r'''
<p><strong>Optimistic UI</strong> updates the React state <em>before</em> the server confirms, then rolls back if the request fails. The result feels instant.</p>
<pre><code>// TanStack Query mutation with optimistic update
const mutation = useMutation({
  mutationFn: (input) =&gt; api.toggleLike(input),
  onMutate: async ({ postId }) =&gt; {
    await queryClient.cancelQueries({ queryKey: ["post", postId] });
    const previous = queryClient.getQueryData(["post", postId]);
    queryClient.setQueryData(["post", postId], (old) =&gt; ({
      ...old,
      liked: !old.liked,
      likes_count: old.likes_count + (old.liked ? -1 : 1)
    }));
    return { previous };  // for rollback
  },
  onError: (err, vars, ctx) =&gt; {
    queryClient.setQueryData(["post", vars.postId], ctx.previous);
    toast.error("Failed to update");
  },
  onSettled: (data, err, vars) =&gt; {
    queryClient.invalidateQueries({ queryKey: ["post", vars.postId] });
  }
});</code></pre>
<p>Best for low-risk, idempotent actions: likes, bookmarks, reorders. Avoid for actions where failure has consequences (payments, irreversible deletes) &mdash; use a clear loading state instead. The pattern: snapshot &rarr; apply &rarr; rollback on error &rarr; refetch to confirm. <strong>SWR</strong> has <code>mutate</code> with similar semantics. For multi-step optimistic flows (offline sync), <strong>Yjs</strong>/<strong>Replicache</strong>/<strong>RxDB</strong>/<strong>Automerge</strong> handle it as first-class. Show a small &ldquo;syncing&rdquo; indicator or a toast on rollback so users understand what happened.</p>
'''

ANSWERS[56] = r'''
<p>A <strong>service worker</strong> is a script the browser runs separately from your page, intercepting network requests. It enables offline mode, custom caching, and push notifications.</p>
<pre><code>// public/sw.js
self.addEventListener("install", (e) =&gt; {
  e.waitUntil(caches.open("v1").then((c) =&gt; c.addAll(["/", "/app.js", "/styles.css"])));
});
self.addEventListener("fetch", (e) =&gt; {
  e.respondWith(
    caches.match(e.request).then((r) =&gt; r ?? fetch(e.request))
  );
});

// app entry
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js");
}</code></pre>
<p>In 2026 you almost never write this by hand. Use <strong>Workbox</strong> for the strategies (cache-first, network-first, stale-while-revalidate) and <strong>vite-plugin-pwa</strong> or <strong>next-pwa</strong> for the build pipeline. Service workers also enable <strong>Web Push notifications</strong> (subscribe to push, show notification when one arrives even with the tab closed) and <strong>background sync</strong> (queue failed requests, retry when online). Important caveats: service workers run only over HTTPS (localhost exempted); they have a separate cache from the browser; updates require careful versioning to avoid users stuck on stale versions; not all features work on iOS Safari. For most apps, the value comes from making them installable PWAs and gracefully degrading offline rather than building a full offline-first experience.</p>
'''

ANSWERS[57] = r'''
<p>Caching in MERN happens at multiple layers; each adds speed and reduces load.</p>
<ul>
<li><strong>HTTP cache headers</strong> &mdash; <code>Cache-Control: public, max-age=31536000, immutable</code> on hashed assets; <code>private, no-cache</code> for API responses that mustn&rsquo;t be shared. The browser and CDN do the rest.</li>
<li><strong>CDN</strong> &mdash; <strong>Cloudflare</strong>/<strong>Vercel Edge Network</strong>/<strong>Fastly</strong>/<strong>CloudFront</strong> caches static assets and SSR HTML at the edge, microseconds from the user.</li>
<li><strong>Server-side cache (Redis)</strong> &mdash; cache hot read paths: user profile, top posts, expensive aggregations. <strong>Cache-aside</strong> pattern: read cache; on miss, hit DB and populate. TTL is a safety net; explicit invalidation on writes is the goal.</li>
<li><strong>Client-side cache</strong> &mdash; <strong>TanStack Query</strong>/<strong>SWR</strong> dedupes and caches API responses across components, with stale-while-revalidate.</li>
<li><strong>MongoDB Working Set</strong> &mdash; the database&rsquo;s own RAM cache.</li>
</ul>
<p>Cache <em>invalidation</em> is the hard part. Patterns: short TTL (60s) for &ldquo;eventually fresh&rdquo;; tag-based invalidation (<strong>Vercel Data Cache</strong>, <strong>Next.js</strong> <code>revalidateTag</code>); change-stream-driven (MongoDB change stream &rarr; Redis <code>DEL</code>); content-hashed URLs (assets never go stale). For low-write data, cache aggressively; for high-write, skip caching and rely on indexes. <strong>Dragonfly</strong>/<strong>KeyDB</strong>/<strong>Redis</strong> for the cache; <strong>Upstash</strong> for serverless-friendly Redis.</p>
'''

ANSWERS[58] = r'''
<p>Image uploads in MERN: store in object storage (S3/R2/GCS), keep only metadata in MongoDB, deliver via CDN.</p>
<pre><code>// Server &mdash; presigned URL
app.post("/api/uploads/presign", async (req, res) =&gt; {
  const key = `images/${userId}/${ulid()}.${ext}`;
  const url = await s3.getSignedUrl("putObject", {
    Bucket, Key: key, ContentType: req.body.type, Expires: 300
  });
  res.json({ upload_url: url, key });
});

// Client uploads directly to S3 (bytes never touch your server)
await fetch(upload_url, { method: "PUT", body: file, headers: { "Content-Type": file.type } });

// Save metadata
await api.post("/api/images", { key, content_type: file.type, size: file.size });</code></pre>
<p>Server-side, you don&rsquo;t want bytes flowing through Node &mdash; presigned URLs let the browser PUT directly to S3. For media-heavy apps, <strong>Cloudinary</strong>/<strong>imgix</strong>/<strong>Cloudflare Images</strong>/<strong>Imgproxy</strong> handle resize, crop, format conversion (AVIF/WebP), and responsive variants on the fly &mdash; you store the original, request <code>?w=400&amp;q=80</code> to get a derived version. For previews, <strong>blurhash</strong>/<strong>thumbhash</strong> tiny placeholders avoid layout shift. <strong>EXIF stripping</strong> is essential for privacy (GPS coords leak). Use <strong>uppy</strong> + <strong>tus.io</strong> for resumable uploads. CDN delivery via the same provider or <strong>CloudFront</strong>/<strong>Cloudflare</strong> in front of your bucket. Save SHA-256 checksums; never trust client-reported MIME types &mdash; sniff server-side.</p>
'''

ANSWERS[59] = r'''
<p>A multi-step form spreads input across screens with progress indication, validation per step, and optional state persistence.</p>
<pre><code>// React Hook Form + Zod, one schema per step
const stepSchemas = [accountSchema, profileSchema, paymentSchema];
const fullSchema = accountSchema.merge(profileSchema).merge(paymentSchema);

function Wizard() {
  const [step, setStep] = useState(0);
  const form = useForm({
    resolver: zodResolver(fullSchema),
    mode: "onChange"
  });
  const next = async () =&gt; {
    const fields = Object.keys(stepSchemas[step].shape);
    const ok = await form.trigger(fields as any);
    if (ok) setStep((s) =&gt; s + 1);
  };
  return (
    &lt;FormProvider {...form}&gt;
      {step === 0 &amp;&amp; &lt;AccountStep /&gt;}
      {step === 1 &amp;&amp; &lt;ProfileStep /&gt;}
      {step === 2 &amp;&amp; &lt;PaymentStep /&gt;}
      &lt;Buttons onNext={next} onBack={() =&gt; setStep(s =&gt; s - 1)} /&gt;
    &lt;/FormProvider&gt;
  );
}</code></pre>
<p>Patterns: <strong>one form context</strong> across steps so values persist when navigating back; <strong>validate the current step</strong> on Next, <strong>full schema</strong> on submit; show progress (1 of 3, completion bar); store partial state in <code>localStorage</code> or <code>sessionStorage</code> for refresh resilience &mdash; or save drafts to the server every N seconds. For very long forms (insurance, tax, onboarding), use a real form-builder library: <strong>react-jsonschema-form</strong>, <strong>SurveyJS</strong>, <strong>Formily</strong>, or <strong>Tally</strong>/<strong>Typeform</strong>/<strong>Fillout</strong> as embedded vendors. For conditional flows (&ldquo;if married, ask spouse name&rdquo;), keep branching logic declarative.</p>
'''

ANSWERS[60] = r'''
<p>A MERN chat app combines persistence (MongoDB), realtime delivery (WebSockets), and a React UI.</p>
<pre><code>// MongoDB
db.conversations.insertOne({ _id, members: [u1, u2], created_at });
db.messages.insertOne({
  _id, conversation_id, sender_id, text, ts: new Date()
});
db.messages.createIndex({ conversation_id: 1, ts: -1 });

// Server (socket.io)
io.on("connection", (socket) =&gt; {
  socket.on("join", (cid) =&gt; socket.join(`conv:${cid}`));
  socket.on("send", async ({ cid, text }) =&gt; {
    const msg = await Message.create({ conversation_id: cid, sender_id: socket.userId, text });
    io.to(`conv:${cid}`).emit("message", msg);
  });
});

// Client
const socket = io(API, { auth: { token } });
socket.emit("join", conversationId);
socket.on("message", (m) =&gt; setMessages((prev) =&gt; [...prev, m]));</code></pre>
<p>Beyond MVP: <strong>typing indicators</strong>, <strong>read receipts</strong> (per-user <code>last_read_ts</code> on conversation), <strong>presence</strong> (online/offline via socket connect/disconnect), <strong>delivery acks</strong>, <strong>message edits/deletes</strong>, <strong>media attachments</strong>, <strong>push notifications</strong> when offline. For multiple Node instances, use the <strong>Redis adapter</strong> for socket.io. For end-to-end encryption (Signal-style), use <strong>libsignal</strong> or <strong>Matrix</strong>; few apps actually need this. <strong>Managed alternatives in 2026</strong>: <strong>Stream Chat</strong>, <strong>Sendbird</strong>, <strong>PubNub</strong>, <strong>CometChat</strong> &mdash; ship in a day, scale automatically. Building chat from scratch is a multi-month investment in edge cases.</p>
'''

ANSWERS[61] = r'''
<p>Long-running tasks (sending email, processing video, generating reports) must <strong>not</strong> happen inside an HTTP request &mdash; the request will time out, the user will refresh, and the work will run multiple times. Push them to a background job queue.</p>
<pre><code>// BullMQ
import { Queue, Worker } from "bullmq";
const emailQueue = new Queue("emails", { connection: redis });

// In your route handler
app.post("/api/users", async (req, res) =&gt; {
  const user = await User.create(req.body);
  await emailQueue.add("welcome", { userId: user._id });
  res.status(201).json(user);
});

// Worker (runs in a separate process)
new Worker("emails", async (job) =&gt; {
  if (job.name === "welcome") await sendWelcomeEmail(job.data.userId);
}, { connection: redis });</code></pre>
<p>The handler returns in milliseconds; the worker does the slow work. Add: retries with exponential backoff; idempotent jobs (a retry must not double-send); dead-letter queues for permanent failures; scheduled jobs (cron, &ldquo;run every 5 minutes&rdquo;). Modern alternatives: <strong>Inngest</strong> (event-driven, durable, no Redis required &mdash; very popular in 2026), <strong>Trigger.dev</strong>, <strong>Temporal</strong> (workflows-as-code, enterprise), <strong>AWS SQS + Lambda</strong>, <strong>Cloudflare Queues</strong>, <strong>Hatchet</strong>, <strong>QStash</strong> from Upstash. For very heavy CPU work (video transcoding) push to a specialized service (<strong>Mux</strong>, <strong>Cloudflare Stream</strong>, <strong>AWS MediaConvert</strong>) instead of running it on your server.</p>
'''

ANSWERS[62] = r'''
<p>A rating system has three operations: submit a rating, compute the average, and display.</p>
<pre><code>// One rating per (user, product)
db.ratings.insertOne({
  _id: { user_id: uid, product_id: pid },
  score: 4,
  review: "Loved it",
  created_at: new Date()
});

// Denormalize aggregate on the product (cheap reads)
db.products.updateOne(
  { _id: pid },
  {
    $inc: { ratings_count: 1, ratings_sum: 4 },
    $set: { ratings_avg: NumberDecimal("...") }   // recompute
  }
);

// Read &mdash; one document
db.products.findOne({ _id: pid }, { projection: { ratings_avg: 1, ratings_count: 1 } });</code></pre>
<p>The compound <code>_id</code> guarantees one rating per user per product, with cheap upserts on update. Denormalize the aggregate on the product so you don&rsquo;t recompute on every read. For more sophisticated reviews, store reviews separately with moderation status, helpful-vote counts, and reply threads &mdash; show only approved ones on the product page. <strong>SEO</strong> benefits from <strong>JSON-LD <code>aggregateRating</code></strong> structured data. Anti-abuse: rate-limit submissions per IP and per user; require purchase for &ldquo;verified&rdquo;; ban brigading. Toxicity detection via <strong>Perspective API</strong>/<strong>Hive Moderation</strong>. For a hosted approach, <strong>BazaarVoice</strong>, <strong>Yotpo</strong>, <strong>Stamped.io</strong>, <strong>Okendo</strong>, <strong>Trustpilot</strong> embed reviews with managed moderation &mdash; popular for ecommerce in 2026.</p>
'''

ANSWERS[63] = r'''
<p>File downloads in MERN come in two shapes: small/dynamic and large/precomputed.</p>
<pre><code>// Small dynamic (CSV export, generated PDF)
app.get("/api/orders/export", async (req, res) =&gt; {
  res.setHeader("Content-Type", "text/csv");
  res.setHeader("Content-Disposition", "attachment; filename=orders.csv");
  const cursor = Order.find({ user_id: req.user.id }).cursor();
  res.write("id,total,placed_at\n");
  for await (const o of cursor) {
    res.write(`${o._id},${o.total_cents},${o.placed_at.toISOString()}\n`);
  }
  res.end();
});

// Large stored files (S3) &mdash; presigned URL, redirect
app.get("/api/files/:id/download", async (req, res) =&gt; {
  const file = await File.findById(req.params.id);
  // ...auth check...
  const url = await s3.getSignedUrl("getObject", {
    Bucket: file.bucket, Key: file.key,
    ResponseContentDisposition: `attachment; filename="${file.name}"`,
    Expires: 300
  });
  res.redirect(url);
});</code></pre>
<p>Stream rather than buffer &mdash; Node will OOM on a 1GB CSV. For S3-hosted files, <strong>never proxy through Node</strong>; redirect to a presigned URL so the bytes go browser&hairsp;&rarr;&hairsp;CDN&hairsp;&rarr;&hairsp;S3 directly. Presigned URLs expire (5 min is typical) so links don&rsquo;t leak. <strong>HTTP Range requests</strong> are honored automatically by S3 + browsers, so resume and partial download work for free. For large reports, generate asynchronously: a job creates the file, uploads to S3, emails the user a link &mdash; or shows it in their downloads page.</p>
'''

ANSWERS[64] = r'''
<p><strong>GraphQL</strong> exposes a single endpoint where clients ask for exactly the fields they need. In a MERN stack, GraphQL replaces (or supplements) REST.</p>
<pre><code>// server &mdash; Apollo Server / GraphQL Yoga / Pothos
import { ApolloServer } from "@apollo/server";
const typeDefs = `
  type User { id: ID!, name: String!, posts: [Post!]! }
  type Post { id: ID!, title: String!, author: User! }
  type Query { user(id: ID!): User }
`;
const resolvers = {
  Query: { user: (_, { id }) =&gt; User.findById(id) },
  User:  { posts: (u) =&gt; Post.find({ author_id: u._id }) }
};

// client &mdash; Apollo Client / urql / TanStack Query + graphql-request
const { data } = useQuery(USER_QUERY, { variables: { id } });</code></pre>
<p>Strengths: clients fetch <em>only</em> needed fields (smaller responses); single round trip for nested data; strong types from the schema; introspection-driven tooling. Weaknesses: caching is harder than REST; N+1 queries unless you use <strong>DataLoader</strong>; complex auth; over-fetching is replaced by query complexity attacks. In 2026, momentum has shifted: <strong>tRPC</strong> (typed RPC) covers the &ldquo;typed end-to-end&rdquo; need without GraphQL ceremony for internal MERN apps; <strong>REST + OpenAPI + Zod</strong> stays popular for public APIs; <strong>GraphQL</strong> still shines for federated data and mobile apps with diverse fields. Use <strong>Pothos</strong> for code-first schemas, <strong>GraphQL Yoga</strong> for the server, <strong>Hasura</strong>/<strong>PostGraphile</strong>/<strong>Apollo Federation</strong> for federation.</p>
'''

ANSWERS[65] = r'''
<p>Time zones are the source of countless bugs. The discipline:</p>
<ul>
<li><strong>Store everything in UTC</strong> in MongoDB. <code>new Date()</code> is UTC under the hood; <code>ISODate</code> is UTC. Never store local times without timezone info.</li>
<li><strong>Send ISO 8601 strings</strong> over the wire (<code>2026-04-29T13:42:18Z</code>). Don&rsquo;t send Unix timestamps (lose precision) or local strings (ambiguous).</li>
<li><strong>Convert to the user&rsquo;s zone at the edges</strong> &mdash; in the React client &mdash; for display.</li>
<li><strong>Detect the user&rsquo;s zone</strong> with <code>Intl.DateTimeFormat().resolvedOptions().timeZone</code> (returns IANA names like &ldquo;America/New_York&rdquo;); let users override in settings.</li>
</ul>
<pre><code>// Display with date-fns-tz / luxon / Day.js / Temporal API
import { format, toZonedTime } from "date-fns-tz";
const local = toZonedTime(post.created_at, userTimeZone);
&lt;time dateTime={post.created_at}&gt;{format(local, "PPp", { timeZone: userTimeZone })}&lt;/time&gt;</code></pre>
<p>For scheduled events (a meeting at 3pm Tokyo time), store both the UTC instant <em>and</em> the originating timezone &mdash; you need both to display correctly across DST changes. The new <strong>Temporal API</strong> (stage 3 TC39) finally fixes JavaScript&rsquo;s broken Date; <strong>js-temporal</strong> polyfill works today. <strong>date-fns-tz</strong>, <strong>luxon</strong>, <strong>Day.js</strong> remain popular. Server-side, log timestamps in UTC; let log aggregators (<strong>Datadog</strong>, <strong>Honeycomb</strong>) translate per viewer.</p>
'''

ANSWERS[66] = r'''
<p>A comment system has comments tied to a parent (post, video, article), with optional threading and moderation.</p>
<pre><code>// Flat comments
db.comments.insertOne({
  _id: ObjectId(),
  parent_id: postId,             // what's being commented on
  parent_type: "post",
  user_id: ObjectId("..."),
  text: "Great post!",
  status: "approved",            // pending | approved | hidden | spam
  created_at: new Date()
});
db.comments.createIndex({ parent_id: 1, created_at: -1 });

// Threaded (replies)
{
  ...,
  reply_to_comment_id: ObjectId("..."),  // null for top-level
  thread_depth: 1
}</code></pre>
<p>Render top-level chronologically; replies nested one level (deep threads ruin readability &mdash; Reddit caps at 8). For deep trees, use the <strong>materialized path</strong> pattern (<code>path: "/c1/c2/c3"</code>) to query subtrees with prefix matching. Counters: <code>comments_count</code> denormalized on the post, incremented atomically on submit. Moderation: spam filtering (<strong>Akismet</strong>, <strong>Perspective API</strong>, <strong>Hive Moderation</strong>); profanity word lists; rate limits. <strong>Markdown rendering</strong> via <strong>remark</strong>/<strong>markdown-it</strong> with sanitization (<strong>DOMPurify</strong>, <strong>rehype-sanitize</strong>) &mdash; never trust user HTML. Realtime updates: socket.io to broadcast new comments. Hosted alternatives: <strong>Disqus</strong>, <strong>Commento</strong>, <strong>Giscus</strong> (GitHub-backed), <strong>Hyvor Talk</strong> &mdash; embed in minutes if you don&rsquo;t want to maintain.</p>
'''

ANSWERS[67] = r'''
<p>A dashboard with charts has three layers: data aggregation, charting library, and dashboard layout.</p>
<pre><code>// Server &mdash; aggregate via MongoDB pipeline
db.orders.aggregate([
  { $match: { placed_at: { $gte: monthStart } } },
  { $group: {
      _id: { $dateTrunc: { date: "$placed_at", unit: "day" } },
      revenue: { $sum: "$total_cents" },
      count:   { $sum: 1 }
  }},
  { $sort: { _id: 1 } }
]);

// Client &mdash; Recharts (popular and easy)
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
&lt;LineChart data={data} width={600} height={300}&gt;
  &lt;XAxis dataKey="date" /&gt;&lt;YAxis /&gt;&lt;Tooltip /&gt;
  &lt;Line dataKey="revenue" stroke="#3b82f6" /&gt;
&lt;/LineChart&gt;</code></pre>
<p>2026 charting options: <strong>Recharts</strong> (declarative, React-friendly), <strong>Chart.js</strong> (mature, canvas-based), <strong>Visx</strong> (Airbnb, low-level), <strong>Apache ECharts</strong> (powerful, especially for complex/financial), <strong>Tremor</strong> (dashboards out of the box), <strong>Nivo</strong>, <strong>Highcharts</strong> (commercial). For interactive data exploration, <strong>D3</strong> with <strong>Observable Plot</strong>; for huge datasets, <strong>deck.gl</strong> or <strong>Plotly</strong> with WebGL. Pre-aggregate in MongoDB rather than computing in React; cache the aggregation result in Redis with short TTL. For complete dashboard solutions, <strong>MongoDB Atlas Charts</strong>, <strong>Metabase</strong>, <strong>Grafana</strong>, <strong>Apache Superset</strong>, <strong>Cube.js</strong>, <strong>Hex</strong>, <strong>Retool</strong> let you build dashboards without writing chart code. Add export-to-PNG/CSV, date range pickers, and respect time zones.</p>
'''

ANSWERS[68] = r'''
<p>Internationalization (i18n) splits user-facing text from code so it can be translated. The dominant React i18n libraries in 2026: <strong>react-i18next</strong>, <strong>next-intl</strong> (Next.js), <strong>FormatJS</strong>/<strong>react-intl</strong>, <strong>Lingui</strong>.</p>
<pre><code>// react-i18next
import { useTranslation } from "react-i18next";
function Greeting({ name }) {
  const { t } = useTranslation();
  return &lt;p&gt;{t("greeting", { name })}&lt;/p&gt;;
}

// locales/en.json
{ "greeting": "Hello, {{name}}!", "items_count": "{{count}} items" }

// locales/ja.json
{ "greeting": "こんにちは、{{name}}さん！", "items_count": "{{count}}個のアイテム" }</code></pre>
<p>What needs translation goes far beyond strings: <strong>plurals</strong> (English &ldquo;1 item / 2 items&rdquo; vs Polish&rsquo;s three forms) &mdash; use <strong>ICU MessageFormat</strong>; <strong>dates and numbers</strong> via <code>Intl.DateTimeFormat</code> / <code>Intl.NumberFormat</code> / <code>Intl.RelativeTimeFormat</code>; <strong>currencies</strong>; <strong>RTL</strong> layouts (Arabic, Hebrew) handled with CSS logical properties (<code>margin-inline-start</code>); <strong>locale-keyed slugs</strong> in URLs (<code>/en/about</code>, <code>/ja/about</code>) for SEO; <strong>hreflang</strong> tags. Translation management with <strong>Lokalise</strong>, <strong>Crowdin</strong>, <strong>Phrase</strong>, <strong>Tolgee</strong>, <strong>Localizely</strong>. AI-assisted first drafts via <strong>OpenAI</strong>/<strong>DeepL</strong> with human review. On the server, store user content in their language; consider <strong>Atlas Search</strong> with multi-language analyzers.</p>
'''

ANSWERS[69] = r'''
<p>React Context is a way to pass values down the tree without prop drilling. For theming it&rsquo;s a clean fit because the value (light/dark mode) changes rarely and many components need it.</p>
<pre><code>// ThemeContext.tsx
import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext&lt;{
  theme: "light" | "dark";
  toggle: () =&gt; void;
}&gt;(null!);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState&lt;"light" | "dark"&gt;("light");
  useEffect(() =&gt; {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);
  const toggle = () =&gt; setTheme((t) =&gt; (t === "light" ? "dark" : "light"));
  return (
    &lt;ThemeContext.Provider value={{ theme, toggle }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

export const useTheme = () =&gt; useContext(ThemeContext);

// In a component
const { theme, toggle } = useTheme();</code></pre>
<p>Wrap the app once: <code>&lt;ThemeProvider&gt;&lt;App /&gt;&lt;/ThemeProvider&gt;</code>. Any descendant calls <code>useTheme()</code> &mdash; no prop chains. <strong>Pitfall</strong>: every component using a context re-renders when the value changes. Don&rsquo;t put high-frequency state in context (mouse position, every keystroke). Split contexts &mdash; one for theme, one for auth, one for cart &mdash; so changing one doesn&rsquo;t re-render unrelated trees. For dark mode specifically, <strong>next-themes</strong> in Next.js handles SSR, <code>prefers-color-scheme</code>, and persistence with no flash. CSS variables + a <code>.dark</code> class are simpler than Context for purely visual theming.</p>
'''

ANSWERS[70] = r'''
<p>Infinite scroll loads more items as the user reaches the bottom &mdash; common in feeds, search results, and image grids. Stack:</p>
<pre><code>// 1. Cursor-paginated API
GET /api/posts?cursor=eyJ0cyI6...&amp;limit=20

// 2. TanStack Query useInfiniteQuery
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
  queryKey: ["feed"],
  queryFn: ({ pageParam }) =&gt; api.feed({ cursor: pageParam }),
  initialPageParam: null,
  getNextPageParam: (last) =&gt; last.next_cursor
});

// 3. IntersectionObserver triggers fetchNextPage
const sentinelRef = useRef(null);
useEffect(() =&gt; {
  const obs = new IntersectionObserver((entries) =&gt; {
    if (entries[0].isIntersecting &amp;&amp; hasNextPage &amp;&amp; !isFetchingNextPage)
      fetchNextPage();
  });
  if (sentinelRef.current) obs.observe(sentinelRef.current);
  return () =&gt; obs.disconnect();
}, [hasNextPage, isFetchingNextPage]);

return (
  &lt;&gt;
    {data?.pages.flatMap((p) =&gt; p.items).map(...)}
    &lt;div ref={sentinelRef} /&gt;
  &lt;/&gt;
);</code></pre>
<p>For long feeds (10k+ items), virtualize with <strong>TanStack Virtual</strong> or <strong>react-window</strong> &mdash; render only the rows in view. Use cursor-based (not offset) pagination so new items inserted as the user scrolls don&rsquo;t cause skipped or duplicated rows. <strong>Restoring scroll position</strong> on back-navigation is tricky &mdash; remember <code>data.pages</code> count and scroll offset. Always provide a manual &ldquo;Load more&rdquo; fallback for accessibility (some users can&rsquo;t scroll-trigger). Avoid for content people are expected to find again (no clear &ldquo;page X&rdquo;); offset pagination is friendlier for navigation-heavy content.</p>
'''

ANSWERS[71] = r'''
<p>Date and time handling in MERN follows a few rules:</p>
<ul>
<li><strong>Server stores UTC.</strong> MongoDB <code>Date</code>/<code>ISODate</code> is always UTC. Don&rsquo;t store strings.</li>
<li><strong>Wire format is ISO 8601</strong> (<code>2026-04-29T13:42:00Z</code>). JSON parsing on the client gets you a Date string; convert to a Date object with <code>new Date(str)</code>.</li>
<li><strong>Display is in user&rsquo;s zone</strong>, computed at render time.</li>
<li><strong>Date inputs need libraries</strong> &mdash; the native <code>&lt;input type="date"&gt;</code> works but is locale-quirky.</li>
</ul>
<pre><code>// 2026 stack
import { format, formatDistanceToNow } from "date-fns";
import { toZonedTime } from "date-fns-tz";

const tz = Intl.DateTimeFormat().resolvedOptions().timeZone; // user TZ
&lt;time dateTime={iso}&gt;{format(toZonedTime(iso, tz), "PPp")}&lt;/time&gt;

// "2 hours ago" relative
formatDistanceToNow(new Date(iso), { addSuffix: true });</code></pre>
<p>Library choices: <strong>date-fns</strong> (functional, tree-shakeable &mdash; default in 2026), <strong>Day.js</strong> (Moment-compatible, tiny), <strong>Luxon</strong> (timezone-strong), <strong>js-temporal/polyfill</strong> (the future via TC39 Temporal API). <strong>Avoid Moment.js</strong> &mdash; it&rsquo;s in maintenance mode and is huge. For date pickers, <strong>react-day-picker</strong>, <strong>react-datepicker</strong>, <strong>shadcn/ui</strong> Calendar (built on react-day-picker). For business-day math, <strong>date-fns-business-days</strong>. Always use <code>&lt;time dateTime="ISO"&gt;</code> for accessibility and SEO. Validate dates with Zod (<code>z.coerce.date()</code>); store recurrence rules as <strong>RRULE</strong> strings (RFC 5545) parsed with <strong>rrule.js</strong>.</p>
'''

ANSWERS[72] = r'''
<p>Responsive design in React = the same component renders well on phone, tablet, and desktop. The toolkit:</p>
<ul>
<li><strong>CSS-driven, mobile-first</strong> &mdash; Tailwind&rsquo;s <code>md:</code>/<code>lg:</code> prefixes or media queries. Start with the smallest screen; add complexity at breakpoints.</li>
<li><strong>Modern layout</strong> &mdash; <strong>CSS Grid</strong> for two-dimensional, <strong>Flexbox</strong> for one-dimensional. <code>grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))</code> wraps responsively without media queries.</li>
<li><strong>Container queries</strong> (<code>@container</code>) &mdash; the component&rsquo;s width drives layout, not the viewport&rsquo;s. Wide adoption in 2026.</li>
<li><strong>Logical properties</strong> &mdash; <code>margin-inline-start</code> instead of <code>margin-left</code> for RTL support.</li>
<li><strong>Fluid typography</strong> &mdash; <code>font-size: clamp(1rem, 2vw, 1.25rem)</code> scales smoothly between breakpoints.</li>
</ul>
<pre><code>&lt;div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"&gt;
  {/* one column on mobile, two on tablet, three on desktop */}
&lt;/div&gt;</code></pre>
<p>Test on real devices (or BrowserStack/LambdaTest); don&rsquo;t rely on the resize handle. <strong>Component libraries</strong>: <strong>shadcn/ui</strong>, <strong>Radix Primitives</strong>, <strong>Park UI</strong>, <strong>Mantine</strong>, <strong>Chakra UI</strong>, <strong>NextUI</strong>/<strong>HeroUI</strong>, <strong>Headless UI</strong> &mdash; ship responsive primitives (drawer / sheet that becomes a sidebar above <code>md</code>). For images, <code>srcset</code> and <code>&lt;picture&gt;</code>; in Next.js, the <code>&lt;Image&gt;</code> component handles all of this automatically. Avoid <code>useEffect</code>-based viewport detection &mdash; CSS solves layout faster and survives SSR.</p>
'''

ANSWERS[73] = r'''
<p>Secrets (API keys, DB URIs, signing keys) and configuration (feature flags, URLs) need different handling than regular code:</p>
<ul>
<li><strong>Never commit secrets.</strong> Use <code>.gitignore</code>; if a secret leaks, rotate immediately. <strong>git-secrets</strong>, <strong>Gitleaks</strong>, <strong>Trufflehog</strong>, <strong>GitHub Secret Scanning</strong> catch slips.</li>
<li><strong>Local dev</strong> &mdash; <code>.env</code> file loaded by <strong>dotenv</strong>; <code>.env.example</code> committed as documentation.</li>
<li><strong>Production</strong> &mdash; the deployment platform&rsquo;s secret store. Vercel/Netlify/Render dashboards; Kubernetes Secrets sealed with <strong>Sealed Secrets</strong>/<strong>SOPS</strong>; cloud-native: <strong>AWS Secrets Manager</strong>, <strong>GCP Secret Manager</strong>, <strong>Azure Key Vault</strong>; vendor-neutral: <strong>HashiCorp Vault</strong>.</li>
<li><strong>Team sharing</strong> &mdash; <strong>Doppler</strong>, <strong>Infisical</strong>, <strong>1Password Secrets</strong>, <strong>Akeyless</strong> sync secrets across local, CI, and production from one source of truth. The default in 2026 for serious teams.</li>
<li><strong>Validate at boot</strong> &mdash; Zod schema for env; crash with a clear error if a required var is missing. Don&rsquo;t discover at request time.</li>
</ul>
<pre><code>// env.ts
import { z } from "zod";
const env = z.object({
  MONGODB_URI: z.string().url(),
  JWT_SECRET:  z.string().min(32),
  STRIPE_KEY:  z.string().startsWith("sk_")
}).parse(process.env);
export default env;</code></pre>
<p>For feature flags, separate from secrets: <strong>LaunchDarkly</strong>, <strong>Statsig</strong>, <strong>PostHog</strong>, <strong>Unleash</strong>, <strong>ConfigCat</strong>, <strong>Flagsmith</strong>. Rotate secrets on schedule; audit who reads them; use <strong>least-privilege IAM</strong> for cloud secrets.</p>
'''

ANSWERS[74] = r'''
<p>Social login (OAuth / OpenID Connect) lets users sign in with Google, GitHub, Apple, etc. The standard flow:</p>
<ol>
<li>User clicks &ldquo;Sign in with Google&rdquo; &rarr; redirected to Google.</li>
<li>User authorizes &rarr; Google redirects back with an <code>authorization code</code>.</li>
<li>Your server exchanges the code for an <code>access_token</code> and <code>id_token</code>.</li>
<li>You verify the <code>id_token</code> JWT, read user info (email, name, sub), find or create the user, set your own session.</li>
</ol>
<pre><code>// Most teams use a library, not handwritten OAuth
// Auth.js (NextAuth) for Next.js
import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
export const { handlers, signIn, auth } = NextAuth({
  providers: [Google],
  callbacks: { async session({ session, token }) { ... } }
});</code></pre>
<p>Don&rsquo;t implement OAuth from scratch &mdash; the spec is intricate and security-critical. Use:</p>
<ul>
<li><strong>Auth.js (NextAuth)</strong> &mdash; Next.js standard.</li>
<li><strong>Lucia</strong>, <strong>Better Auth</strong> &mdash; framework-agnostic, self-hosted.</li>
<li><strong>Passport.js</strong> &mdash; Express classic; still works.</li>
<li><strong>Hosted</strong>: <strong>Clerk</strong>, <strong>Auth0</strong>, <strong>WorkOS</strong>, <strong>Stack Auth</strong>, <strong>Supabase Auth</strong>, <strong>Stytch</strong>, <strong>FusionAuth</strong>. Drop-in components, generous free tiers, handle MFA + SAML + audit. The default in 2026 production apps.</li>
</ul>
<p>Watch for: PKCE for SPAs, <code>state</code> parameter to prevent CSRF, scope minimization (request only what you need), email verification status from the provider. Store the provider <code>sub</code> (subject ID) as a stable user identity, not just email.</p>
'''

ANSWERS[75] = r'''
<p>Web accessibility (a11y) ensures users with disabilities can use the app. The basics every React app must get right:</p>
<ul>
<li><strong>Semantic HTML</strong> &mdash; <code>&lt;button&gt;</code>, not <code>&lt;div onClick&gt;</code>; <code>&lt;nav&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;article&gt;</code>; one <code>&lt;h1&gt;</code> per page; <code>&lt;label&gt;</code> for every input.</li>
<li><strong>Keyboard navigation</strong> &mdash; every interactive element is focusable, focus order is sensible, <code>:focus-visible</code> is styled clearly, modals trap focus.</li>
<li><strong>ARIA</strong> only when semantic HTML doesn&rsquo;t cover the case (custom comboboxes, tabs, accordions). The first rule of ARIA: don&rsquo;t use ARIA. Use the right element first.</li>
<li><strong>Color contrast</strong> &mdash; WCAG AA is 4.5:1 for body text, 3:1 for UI components. Don&rsquo;t encode information in color alone.</li>
<li><strong>Alt text</strong> on meaningful images; empty <code>alt=""</code> on decorative ones.</li>
<li><strong>Forms</strong> &mdash; labels, error association via <code>aria-describedby</code>, <code>aria-invalid</code>, clear error text.</li>
<li><strong>Reduced motion</strong> &mdash; respect <code>prefers-reduced-motion</code>.</li>
</ul>
<p>Use <strong>Radix UI</strong>, <strong>React Aria</strong> (Adobe), <strong>Headless UI</strong>, or <strong>Ariakit</strong> for accessible primitives &mdash; they handle keyboard and ARIA correctly. Audit with <strong>axe DevTools</strong>, <strong>Lighthouse</strong>, <strong>WAVE</strong>; lint with <strong>eslint-plugin-jsx-a11y</strong>; run automated checks in CI with <strong>axe-core</strong>. Test with a screen reader (<strong>VoiceOver</strong> on Mac, <strong>NVDA</strong> on Windows). Accessibility is a legal requirement (ADA, EAA in EU 2025+) &mdash; not optional.</p>
'''


ANSWERS[76] = r'''
<p>A tagging system lets multiple tags be applied to many documents and supports queries like &ldquo;all posts tagged X&rdquo; and &ldquo;tag autocomplete.&rdquo;</p>
<pre><code>// Simple: array of strings, multikey index
db.posts.insertOne({
  title: "MERN at Scale",
  tags: ["mern", "scaling", "mongodb"],
  created_at: new Date()
});
db.posts.createIndex({ tags: 1 });

// Queries
db.posts.find({ tags: "mern" });                    // any
db.posts.find({ tags: { $all: ["mern", "scaling"] } }); // all

// Top tags
db.posts.aggregate([
  { $unwind: "$tags" },
  { $sortByCount: "$tags" },
  { $limit: 50 }
]);

// Adding a tag (no duplicates)
db.posts.updateOne({ _id: pid }, { $addToSet: { tags: "react" } });</code></pre>
<p>For richer tag metadata (color, description, follower count) maintain a separate <code>tags</code> collection and reference by <code>tag_id</code> &mdash; that way renaming a tag doesn&rsquo;t require updating millions of posts. Autocomplete: <strong>MongoDB Atlas Search</strong>&rsquo;s <code>autocomplete</code> operator handles fuzzy + edge n-gram matching out of the box. UI side, components like <strong>react-select</strong>, <strong>downshift</strong>, <strong>cmdk</strong>, <strong>shadcn/ui</strong> Combobox handle the typeahead. Show top tags as a tag cloud (count drives size), &ldquo;related tags&rdquo; computed via co-occurrence in a periodic batch job. For SEO, generate <code>/tags/&lt;slug&gt;</code> pages with proper canonical URLs.</p>
'''

ANSWERS[77] = r'''
<p>A <strong>Progressive Web App (PWA)</strong> is a website that can be installed, run offline, receive push notifications, and behaves like a native app. Three requirements:</p>
<ul>
<li><strong>HTTPS</strong> &mdash; mandatory for PWA features.</li>
<li><strong>Web App Manifest</strong> &mdash; <code>manifest.webmanifest</code> with name, icons, theme color, start URL, display mode.</li>
<li><strong>Service worker</strong> &mdash; intercepts requests for offline support, caching, and push.</li>
</ul>
<pre><code>// Vite + vite-plugin-pwa is the easiest path
// vite.config.ts
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "My App", short_name: "App",
        theme_color: "#3b82f6",
        icons: [{ src: "/icon-192.png", sizes: "192x192", type: "image/png" }],
        display: "standalone"
      },
      workbox: { runtimeCaching: [...] }
    })
  ]
});</code></pre>
<p>Use <strong>Workbox</strong> (under <strong>vite-plugin-pwa</strong>/<strong>next-pwa</strong>) for caching strategies: cache-first for hashed assets, network-first with fallback for API calls, stale-while-revalidate for moderate-freshness content. Add <strong>Web Push notifications</strong> for re-engagement. Test with <strong>Lighthouse</strong>&rsquo;s PWA audit. Caveats in 2026: iOS Safari has improved PWA support but still trails Android/Chrome &mdash; push notifications work only on iOS 16.4+ via &ldquo;Add to Home Screen.&rdquo; For full app-store-distributed apps, use <strong>Capacitor</strong>/<strong>React Native</strong>/<strong>Expo</strong> &mdash; PWA stops at the OS shell.</p>
'''

ANSWERS[78] = r'''
<p>Encryption in MERN happens at multiple levels. &ldquo;File encryption&rdquo; usually means one of these:</p>
<ul>
<li><strong>Encryption at rest</strong> &mdash; provider-level (S3 SSE, MongoDB Atlas encryption at rest with AWS/GCP/Azure KMS). Default-on at most managed services. Protects against disk theft / cold backups.</li>
<li><strong>Encryption in transit</strong> &mdash; HTTPS / TLS for all traffic, including S3 uploads.</li>
<li><strong>Client-side encryption</strong> &mdash; the file is encrypted in the browser <em>before</em> upload; the server stores ciphertext it can&rsquo;t read. The user holds the key. True end-to-end.</li>
</ul>
<pre><code>// Client-side AES-GCM via WebCrypto
async function encryptFile(file) {
  const key = await crypto.subtle.generateKey({ name: "AES-GCM", length: 256 }, true, ["encrypt"]);
  const iv  = crypto.getRandomValues(new Uint8Array(12));
  const buf = await file.arrayBuffer();
  const ct  = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, buf);
  return { ciphertext: ct, key, iv };
}</code></pre>
<p>For ad-hoc file encryption, <strong>libsodium-wrappers</strong> (sealed boxes) or <strong>WebCrypto</strong> directly. <strong>Key management is the hard part</strong> &mdash; lose the key, lose the file. Use <strong>passphrase-derived keys</strong> (PBKDF2/Argon2) with the user&rsquo;s password, or wrap user keys with a service like <strong>Hashicorp Vault Transit</strong> / <strong>AWS KMS</strong> / <strong>Skyflow</strong> / <strong>Basis Theory</strong> / <strong>CipherStash</strong>. For specific data classes (PII, PHI, payment), use <strong>tokenization vaults</strong> rather than raw encryption. MongoDB&rsquo;s <strong>Queryable Encryption (7.0+)</strong> supports <code>$eq</code> and range queries on encrypted fields server-side without the keys.</p>
'''

ANSWERS[79] = r'''
<p>A wishlist (favorites, saved items) is a many-to-many relation between users and products. Two common shapes:</p>
<pre><code>// 1. Embed array on user (simple, capped)
db.users.updateOne(
  { _id: userId },
  { $addToSet: { wishlist: productId } }
);
db.users.findOne({ _id: userId }, { projection: { wishlist: 1 } });

// 2. Separate collection (scales, supports notes/timestamps)
db.wishlist_items.insertOne({
  _id: { user_id: userId, product_id: productId },
  added_at: new Date(),
  note: "for birthday"
});
db.wishlist_items.find({ "_id.user_id": userId }).sort({ added_at: -1 });</code></pre>
<p>Embedding works if a wishlist stays small (&lt; a few hundred items); use <code>$addToSet</code> for idempotency. The separate collection scales without limits, supports per-item metadata (note, priority, added date), and pages cleanly. The compound <code>_id</code> guarantees uniqueness and makes upserts efficient. For UI: <strong>TanStack Query</strong> with optimistic updates makes the heart-icon toggle feel instant. Show a count badge in the header. Notify on price drops via change streams + email/push. Common features: shareable wishlist URL (a slug like <code>/u/alice/wishlist</code>), default vs custom-named lists, &ldquo;move to cart&rdquo; in one click, restock alerts. For ecommerce platforms, <strong>Shopify</strong>/<strong>commercetools</strong>/<strong>Medusa</strong> ship wishlist primitives.</p>
'''

ANSWERS[80] = r'''
<p>Validation in MERN should run at <strong>three layers</strong>:</p>
<ul>
<li><strong>Client</strong> &mdash; instant feedback. <strong>React Hook Form</strong> + <strong>Zod</strong>/<strong>Valibot</strong>.</li>
<li><strong>API</strong> &mdash; security boundary. The same Zod schema validates <code>req.body</code>.</li>
<li><strong>Database</strong> &mdash; last resort. Mongoose schemas or MongoDB <code>$jsonSchema</code> validators catch developer mistakes.</li>
</ul>
<pre><code>// shared/schemas.ts &mdash; one source of truth
import { z } from "zod";
export const createUser = z.object({
  email:    z.string().email(),
  password: z.string().min(8),
  age:      z.number().int().min(13).max(120).optional()
});

// Client &mdash; React Hook Form
const form = useForm({ resolver: zodResolver(createUser) });

// Server &mdash; Express
app.post("/api/users", (req, res) =&gt; {
  const r = createUser.safeParse(req.body);
  if (!r.success) return res.status(422).json({ errors: r.error.flatten() });
  // ...
});

// MongoDB collection-level safety net
db.runCommand({
  collMod: "users",
  validator: { $jsonSchema: { ... } },
  validationLevel: "moderate"
});</code></pre>
<p>The discipline of <strong>one schema, three uses</strong> means validation rules live in one place. Server-side validation cannot be skipped &mdash; a malicious client can call your API with curl. <strong>Sanitize</strong> rich text with <strong>DOMPurify</strong>/<strong>rehype-sanitize</strong> &mdash; never trust raw HTML. For business-rule validation that crosses fields (start date before end date, total = sum of items), use <code>.refine()</code> in Zod. For complex domain rules, validate in service-layer code, not just in the schema.</p>
'''

ANSWERS[81] = r'''
<p>User profiles and settings split into two collections (or two subdocuments) by access pattern:</p>
<pre><code>// Profile &mdash; public-ish, displayed often
db.users.insertOne({
  _id, email, password_hash,
  username, display_name, bio,
  avatar_url, created_at
});

// Settings &mdash; private, large-ish, queried less often
db.user_settings.insertOne({
  _id: userId,
  notifications: {
    email: { mentions: true, weekly_digest: false },
    push:  { mentions: true }
  },
  privacy: { profile_public: true, show_email: false },
  preferences: { theme: "dark", locale: "en", timezone: "America/New_York" },
  updated_at: new Date()
});</code></pre>
<p>Why split: settings can grow large (notification preferences across many channels) and aren&rsquo;t needed when rendering a profile card. Keep the user doc small for the working set. <strong>Avatar uploads</strong> follow the standard pattern (S3 presigned URL, derived sizes via <strong>Cloudinary</strong>/<strong>imgix</strong>). <strong>Email change</strong> requires a verification step on the new address before commit. <strong>Account deletion</strong>: soft-delete first (<code>deleted_at: new Date()</code>) with grace period, then hard-delete via background job &mdash; comply with GDPR &ldquo;right to be forgotten&rdquo; (30 days is typical). <strong>Audit log</strong> sensitive changes (email, password, MFA). For settings UI use a tabbed/sectioned page: <strong>shadcn/ui</strong> patterns work well; <strong>react-hook-form</strong> with auto-save (<code>watch</code> + debounced PATCH) feels modern.</p>
'''

ANSWERS[82] = r'''
<p>SEO for a MERN app starts with <strong>rendering HTML the crawler can read</strong>. A pure SPA returns a near-empty HTML shell &mdash; modern crawlers do execute JS but rendering is slower and ranks less well.</p>
<ul>
<li><strong>Server-side rendering</strong> &mdash; <strong>Next.js</strong> (App Router with server components), <strong>Remix</strong>/<strong>React Router v7</strong> framework mode. The de facto MERN-SEO answer in 2026.</li>
<li><strong>Static generation</strong> &mdash; pre-render at build time for content that doesn&rsquo;t change per user. Fastest, cheapest, best ranked.</li>
<li><strong>Incremental Static Regeneration (ISR)</strong> &mdash; Next.js feature: regenerate static pages every N seconds.</li>
</ul>
<pre><code>// Next.js Metadata API &mdash; per-page SEO
export const metadata = {
  title: "How to scale MongoDB",
  description: "A guide to ...",
  openGraph: { title: ..., images: [...] },
  alternates: { canonical: "https://example.com/posts/scale-mongo" }
};</code></pre>
<p>Beyond rendering: <strong>semantic HTML</strong>, <strong>structured data</strong> (JSON-LD for articles, products, ratings &mdash; Google&rsquo;s <strong>Search Console</strong> validates), <strong>sitemap.xml</strong> + <strong>robots.txt</strong>, <strong>canonical URLs</strong>, fast <strong>Core Web Vitals</strong> (LCP, INP, CLS), <strong>internationalization</strong> with <code>hreflang</code>, accessible markup. Tools: <strong>Google Search Console</strong>, <strong>Bing Webmaster Tools</strong>, <strong>Ahrefs</strong>, <strong>SEMrush</strong>, <strong>Screaming Frog</strong>. For a dynamic React app stuck on SPA mode, <strong>prerender.io</strong>/<strong>Rendertron</strong> serves bot-friendly HTML to crawlers via UA detection &mdash; a workaround, not a solution. The <strong>right answer in 2026 is to use Next.js or Remix</strong> from day one if SEO matters.</p>
'''

ANSWERS[83] = r'''
<p>Large file uploads (&gt;100MB) need <strong>multipart upload</strong> and ideally <strong>direct-to-storage</strong> &mdash; bytes shouldn&rsquo;t flow through your Node server.</p>
<pre><code>// 1. Initiate multipart upload (server)
app.post("/api/uploads/init", async (req, res) =&gt; {
  const upload = await s3.createMultipartUpload({ Bucket, Key });
  res.json({ uploadId: upload.UploadId, key: upload.Key });
});

// 2. Presign each part (server)
app.post("/api/uploads/part", async (req, res) =&gt; {
  const url = await s3.getSignedUrl("uploadPart", {
    Bucket, Key, UploadId: req.body.uploadId,
    PartNumber: req.body.partNumber, Expires: 3600
  });
  res.json({ url });
});

// 3. Client uploads parts in parallel via PUT
// 4. Complete with the part ETags
app.post("/api/uploads/complete", async (req, res) =&gt; {
  await s3.completeMultipartUpload({
    Bucket, Key, UploadId: req.body.uploadId,
    MultipartUpload: { Parts: req.body.parts }
  });
});</code></pre>
<p>S3 supports parts of 5MB-5GB; max object size 5TB. Parallel parts upload faster than sequential. <strong>Resumable uploads</strong> via <strong>tus.io</strong> protocol with <strong>uppy</strong> on the client &mdash; survives wifi drops, browser crashes, and 95% laptop battery. Show a progress bar, allow pause/resume. <strong>Validate</strong> client-side first (size limit, MIME type) but <em>also</em> server-side after upload (sniff the actual bytes). Compute <strong>SHA-256</strong> for integrity. For images, <strong>Cloudinary</strong>/<strong>imgix</strong>/<strong>Cloudflare Images</strong>; for video, <strong>Mux</strong>/<strong>Cloudflare Stream</strong>; for everything else, <strong>S3</strong>/<strong>R2</strong>/<strong>GCS</strong> + your CDN.</p>
'''

ANSWERS[84] = r'''
<p>Express middleware is a function that runs on every request matching its mount path, with access to <code>req</code>, <code>res</code>, and <code>next</code>. Custom middleware lets you add cross-cutting behavior &mdash; logging, auth, rate limiting, request IDs.</p>
<pre><code>// Request ID middleware
import { randomUUID } from "node:crypto";

export function requestId(req, res, next) {
  req.id = req.headers["x-request-id"] ?? randomUUID();
  res.setHeader("x-request-id", req.id);
  next();
}

// Auth middleware
export async function requireAuth(req, res, next) {
  const token = req.cookies.session;
  if (!token) return res.status(401).json({ error: "unauthenticated" });
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!);
    req.user = await User.findById(payload.sub);
    next();
  } catch {
    res.status(401).json({ error: "invalid_token" });
  }
}

// Use them
app.use(requestId);
app.use(pino-http());
app.use("/api/admin", requireAuth, requireRole("admin"));</code></pre>
<p>Rules: call <code>next()</code> exactly once (otherwise the response hangs); call <code>next(err)</code> to skip to error middleware; <strong>order matters</strong> &mdash; body parsers before validators, auth before authorization. <strong>Async middleware</strong>: wrap with try/catch and call <code>next(err)</code> &mdash; or use <strong>express-async-errors</strong>. Common reusable middleware to know: <strong>cors</strong>, <strong>helmet</strong>, <strong>express.json</strong>, <strong>cookie-parser</strong>, <strong>compression</strong>, <strong>express-rate-limit</strong>, <strong>pino-http</strong>. For Next.js Route Handlers and Hono/Fastify, the equivalent concept is also called middleware but with slightly different signatures.</p>
'''

ANSWERS[85] = r'''
<p>Large React apps need a <strong>state ownership strategy</strong>, not just one library. The 2026 sane stack:</p>
<ul>
<li><strong>Server state</strong> &mdash; <strong>TanStack Query</strong> (React Query) or <strong>SWR</strong>. Owns everything fetched from the API. Handles caching, deduping, refetch, optimistic updates.</li>
<li><strong>Form state</strong> &mdash; <strong>React Hook Form</strong> + Zod. Don&rsquo;t use a global store for form fields.</li>
<li><strong>URL state</strong> &mdash; the URL itself. Filters, page, search query live in <code>useSearchParams</code>.</li>
<li><strong>Client UI state</strong> &mdash; <strong>Zustand</strong>/<strong>Jotai</strong>/<strong>Valtio</strong> for cross-component state (sidebar open, modal stack, multi-step wizard, theme). Tiny, no boilerplate.</li>
<li><strong>Local state</strong> &mdash; <code>useState</code>/<code>useReducer</code> for component-internal state.</li>
<li><strong>Cross-tab state</strong> &mdash; <strong>BroadcastChannel</strong> or <code>storage</code> events.</li>
</ul>
<pre><code>// Zustand (one slice per concern)
import { create } from "zustand";

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () =&gt; void;
}
export const useUIStore = create&lt;UIState&gt;((set) =&gt; ({
  sidebarOpen: true,
  toggleSidebar: () =&gt; set((s) =&gt; ({ sidebarOpen: !s.sidebarOpen }))
}));</code></pre>
<p>Avoid: putting server data in Zustand/Redux (you reinvent React Query badly); a single mega-store (slice it); putting transient UI state (modal open) in URLs unless deep-linking matters. <strong>Redux Toolkit</strong> still fits when you genuinely need its time-travel debugging or middleware patterns &mdash; but for most apps the smaller libraries win on ergonomics. <strong>XState</strong> for explicit state machines (wizards, payment flows). <strong>nuqs</strong> for typed URL state in Next.js.</p>
'''

ANSWERS[86] = r'''
<p>A custom error handler in Express centralizes how errors become responses. It&rsquo;s defined as a 4-argument middleware (<code>err, req, res, next</code>) and goes <em>last</em>.</p>
<pre><code>// Custom error classes
class HttpError extends Error {
  constructor(public status: number, message: string, public code?: string) {
    super(message);
  }
}
export class NotFound extends HttpError { constructor(m = "not_found") { super(404, m, "NOT_FOUND") } }
export class Forbidden extends HttpError { constructor(m = "forbidden") { super(403, m, "FORBIDDEN") } }

// Global handler
import { ZodError } from "zod";

export function errorHandler(err, req, res, next) {
  if (err instanceof ZodError)   return res.status(422).json({ error: "validation", issues: err.flatten() });
  if (err instanceof HttpError)  return res.status(err.status).json({ error: err.code, message: err.message });
  if (err.code === 11000)        return res.status(409).json({ error: "duplicate" });

  // Unknown &mdash; don&rsquo;t leak internals
  req.log.error({ err, reqId: req.id }, "unhandled");
  Sentry.captureException(err);
  res.status(500).json({ error: "internal", request_id: req.id });
}

app.use(errorHandler);  // last middleware</code></pre>
<p>Pair with <strong>express-async-errors</strong> (or wrap async handlers in a try/catch helper) so thrown errors in async functions reach this middleware. Best practices: <strong>typed errors</strong> (custom classes), <strong>4xx vs 5xx</strong> distinction, <strong>structured logs</strong> (<strong>pino</strong>) including request ID, <strong>error tracking</strong> (<strong>Sentry</strong>/<strong>Honeybadger</strong>/<strong>Bugsnag</strong>) with stack traces and breadcrumbs, <strong>never leak stack traces</strong> in production responses, <strong>request IDs</strong> in error responses for support correlation. For per-route handlers, prefer throwing typed errors over manually returning &mdash; the global handler shapes the response consistently.</p>
'''

ANSWERS[87] = r'''
<p>Rate limiting protects your API from brute-force attacks, scraping, and accidental thundering herds. Apply different limits per endpoint and per identity (IP / user / API key).</p>
<pre><code>// express-rate-limit + Redis store (works across instances)
import rateLimit from "express-rate-limit";
import RedisStore from "rate-limit-redis";

const loginLimit = rateLimit({
  store: new RedisStore({ sendCommand: (...args) =&gt; redis.call(...args) }),
  windowMs: 15 * 60 * 1000,
  max: 5,                         // 5 login attempts per 15 min per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "too_many_requests" }
});

app.post("/api/auth/login", loginLimit, loginHandler);

// Generic API limit
const apiLimit = rateLimit({ windowMs: 60_000, max: 120 });
app.use("/api", apiLimit);</code></pre>
<p>For serverless / edge, in-memory counters break across instances &mdash; use Redis. Modern alternative: <strong>Upstash Ratelimit</strong> (token bucket / sliding window via Upstash Redis or Cloudflare KV) or <strong>@vercel/firewall</strong>. <strong>Cloudflare</strong>/<strong>AWS WAF</strong>/<strong>Vercel WAF</strong> rate-limit at the edge before requests even reach your app. Strategies: <strong>fixed window</strong> (simple, vulnerable to bursts), <strong>sliding window</strong> (smoother), <strong>token bucket</strong> (burst-friendly), <strong>leaky bucket</strong>. Per-user limits use the user ID; for unauthenticated endpoints, IP &mdash; with care behind proxies (read <code>x-forwarded-for</code>, trust your LB only). Return <code>429 Too Many Requests</code> with <code>Retry-After</code> header. For especially sensitive endpoints (login, password reset), couple rate limit with <strong>CAPTCHA</strong> (<strong>hCaptcha</strong>/<strong>Cloudflare Turnstile</strong>) on suspicion.</p>
'''

ANSWERS[88] = r'''
<p>A custom data-fetching hook encapsulates request, loading, error, and stale states. In 2026, <strong>don&rsquo;t roll your own from scratch</strong> &mdash; build on top of <strong>TanStack Query</strong> or <strong>SWR</strong>, which already handle caching, deduping, retries, and refetch.</p>
<pre><code>// Wrapper for consistent API calls
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export function useUser(id: string) {
  return useQuery({
    queryKey: ["user", id],
    queryFn: ({ signal }) =&gt; fetch(`/api/users/${id}`, { signal }).then((r) =&gt; r.json()),
    staleTime: 60_000,             // consider fresh for 1 min
    gcTime: 5 * 60_000,            // keep in cache 5 min after unmount
    retry: 2
  });
}

// Mutation
export function useUpdateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input) =&gt; fetch(`/api/users/${input.id}`, {
      method: "PATCH", body: JSON.stringify(input),
      headers: { "Content-Type": "application/json" }
    }).then((r) =&gt; r.json()),
    onSuccess: (data) =&gt; qc.invalidateQueries({ queryKey: ["user", data.id] })
  });
}

// In a component
const { data, isLoading, error } = useUser(id);</code></pre>
<p>This pattern beats hand-rolled <code>useEffect + useState + fetch</code> on every axis: cancellation (via <code>signal</code>), automatic refetch on focus / reconnect, deduped concurrent calls for the same key, optimistic updates, integrated devtools, suspense support. For a typed end-to-end API, <strong>tRPC</strong> generates hooks like <code>trpc.user.byId.useQuery({ id })</code>. For GraphQL, <strong>Apollo Client</strong>/<strong>urql</strong>. Build the wrapper once per resource type; let the libraries do the heavy lifting.</p>
'''

ANSWERS[89] = r'''
<p>Two-factor authentication (2FA / MFA) requires a second factor beyond the password. The standard methods:</p>
<ul>
<li><strong>TOTP</strong> &mdash; time-based one-time passwords (Google Authenticator, Authy, 1Password). Most popular; offline; uses <strong>RFC 6238</strong>.</li>
<li><strong>WebAuthn / Passkeys</strong> &mdash; phishing-resistant, biometric, the future. Replaces password entirely in 2026 deployments.</li>
<li><strong>SMS</strong> &mdash; convenient but <strong>weakest</strong> (SIM swap attacks). Acceptable as fallback only.</li>
<li><strong>Email magic link</strong> &mdash; passwordless first-factor pattern, popular for low-stakes apps.</li>
</ul>
<pre><code>// TOTP setup with otplib
import { authenticator } from "otplib";

// 1. Generate secret, store on user, render QR
const secret = authenticator.generateSecret();
await User.updateOne({ _id: userId }, { $set: { totp_secret: secret, totp_enabled: false } });
const otpauth = authenticator.keyuri(user.email, "MyApp", secret);
// Render otpauth as QR with `qrcode` library

// 2. User scans QR with their authenticator app, enters a code to confirm
function verify(code: string, secret: string) {
  return authenticator.verify({ token: code, secret });
}
// On confirmation: User.updateOne({ _id }, { $set: { totp_enabled: true } });

// 3. On login &mdash; after password check, prompt for code
if (user.totp_enabled &amp;&amp; !verify(req.body.code, user.totp_secret))
  return res.status(401).json({ error: "totp_required" });</code></pre>
<p>Always provide <strong>backup codes</strong> (one-time use, hashed in DB) for lost devices. Store the TOTP secret encrypted (KMS-wrapped). Hosted auth (<strong>Clerk</strong>, <strong>Auth0</strong>, <strong>Stack Auth</strong>, <strong>Stytch</strong>, <strong>WorkOS</strong>) ships TOTP and Passkeys with one toggle. <strong>Passkeys</strong> via <strong>SimpleWebAuthn</strong> are dominant in 2026 &mdash; phishing-proof, no shared secret, biometric UX. Most apps should offer Passkeys + TOTP; SMS only on the explicit user&rsquo;s preference.</p>
'''

ANSWERS[90] = r'''
<p>Session expiration is the policy for how long a logged-in session stays valid. Two common patterns:</p>
<pre><code>// 1. Short-lived access token + long-lived refresh token (JWT)
// access_token: 15 min, in HttpOnly cookie
// refresh_token: 7 days, in HttpOnly cookie, rotated on each use
// On 401 from access expiry, client calls /auth/refresh transparently

// 2. Server-side session with sliding expiration
db.sessions.insertOne({
  _id: sessionId,
  user_id, ip, user_agent,
  created_at: new Date(),
  expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
});
db.sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });  // TTL

// On each request, slide the expiry forward
db.sessions.updateOne(
  { _id: sessionId, expires_at: { $gt: new Date() } },
  { $set: { expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) } }
);</code></pre>
<p>The client experience: on a 401, the React app should automatically attempt refresh once and retry the original request &mdash; <strong>TanStack Query</strong>&rsquo;s <code>retry</code> + an axios interceptor handles this cleanly. If refresh fails, send the user to <code>/login?next=...</code> so they return where they were. <strong>Absolute</strong> vs <strong>idle</strong> expiration: idle sliding (active users stay logged in) plus an absolute cap (force re-auth after 30 days regardless). Sensitive operations (password change, payment) should require <strong>recent re-authentication</strong> regardless of session age. <strong>Revocation</strong>: server-side sessions can be deleted instantly; JWT access tokens can&rsquo;t (until they expire) &mdash; that&rsquo;s why you keep them short. <strong>Hosted auth</strong> handles all of this automatically with sane defaults.</p>
'''

ANSWERS[91] = r'''
<p>Task scheduling in Node = running code at fixed times or intervals (cleanup jobs, daily reports, reminder emails). For a single instance, <strong>node-cron</strong> works; for production with multiple instances, you need a queue with scheduled jobs to avoid duplicate execution.</p>
<pre><code>// Single instance &mdash; node-cron
import cron from "node-cron";
cron.schedule("0 3 * * *", async () =&gt; {
  await purgeOldNotifications();
});

// Multi-instance safe &mdash; BullMQ with repeating job
import { Queue } from "bullmq";
const q = new Queue("scheduled", { connection: redis });

await q.add("daily-digest", {}, {
  repeat: { pattern: "0 9 * * *", tz: "America/New_York" }
});

// Worker (only one of N instances picks up each occurrence)
new Worker("scheduled", async (job) =&gt; {
  if (job.name === "daily-digest") await sendDailyDigests();
}, { connection: redis });</code></pre>
<p>2026 stack alternatives:</p>
<ul>
<li><strong>Inngest</strong> &mdash; cron + event triggers, durable, no Redis to run. Very popular.</li>
<li><strong>Trigger.dev</strong> &mdash; similar, with a great DX.</li>
<li><strong>Temporal</strong> &mdash; workflows-as-code; complex but powerful.</li>
<li><strong>Cloud schedulers</strong> &mdash; <strong>AWS EventBridge Scheduler</strong>, <strong>GCP Cloud Scheduler</strong>, <strong>Vercel Cron</strong>, <strong>Cloudflare Workers Cron Triggers</strong> &mdash; serverless cron, no infra. The right answer for serverless deployments.</li>
<li><strong>QStash</strong> from Upstash &mdash; HTTP-triggered scheduled requests.</li>
</ul>
<p>Always make scheduled jobs <strong>idempotent</strong> (safe to run twice). Log success/failure; alert on misses (use a dead-man&rsquo;s switch like <strong>Healthchecks.io</strong> &mdash; a pinger that yells if a job didn&rsquo;t run). Don&rsquo;t do long work inside the schedule trigger; enqueue and return.</p>
'''

ANSWERS[92] = r'''
<p>CSV/Excel export has two paths depending on size.</p>
<pre><code>// Small datasets &mdash; build and stream CSV in the request
app.get("/api/orders/export.csv", async (req, res) =&gt; {
  res.setHeader("Content-Type", "text/csv; charset=utf-8");
  res.setHeader("Content-Disposition", `attachment; filename="orders-${Date.now()}.csv"`);
  res.write("\uFEFF");                           // UTF-8 BOM (Excel-friendly)
  res.write("id,total,placed_at\n");
  const cursor = Order.find({ user_id: req.user.id }).cursor();
  for await (const o of cursor) {
    res.write(`${o._id},${o.total_cents / 100},${o.placed_at.toISOString()}\n`);
  }
  res.end();
});

// Large datasets &mdash; async job + email link
app.post("/api/orders/export", async (req, res) =&gt; {
  const job = await exportQueue.add("orders", { userId: req.user.id, filter: req.body });
  res.status(202).json({ jobId: job.id, status: "queued" });
});</code></pre>
<p>Library choices: <strong>csv-stringify</strong> for streaming CSV; <strong>fast-csv</strong> for parsing/streaming; <strong>exceljs</strong> for real <code>.xlsx</code> with formatting and formulas; <strong>SheetJS (xlsx)</strong> for compatibility (CSV/XLSX read+write). For Excel specifically, write XLSX rather than CSV when users need formulas, multiple sheets, or formatting. CSV pitfalls: BOM for UTF-8 (Excel can&rsquo;t detect otherwise), quote escaping, line endings (<code>\r\n</code> for Excel on Windows), comma vs semicolon (locale!). For huge exports (millions of rows), <strong>generate to S3 in a background job</strong> and email a download link &mdash; never block an HTTP request for minutes. <strong>Compression</strong>: gzip CSVs; XLSX is already a zip. <strong>Privacy</strong>: don&rsquo;t export fields the user shouldn&rsquo;t see; audit who exports what.</p>
'''

ANSWERS[93] = r'''
<p><code>multipart/form-data</code> is the HTTP encoding for forms with files. Browsers send it when a form has <code>enctype="multipart/form-data"</code> or you submit a <code>FormData</code> object via <code>fetch</code>.</p>
<pre><code>// Client
const fd = new FormData();
fd.append("title", "My post");
fd.append("cover", file);     // a File from &lt;input type="file"&gt;
await fetch("/api/posts", { method: "POST", body: fd });
//   Note: do NOT set Content-Type; the browser adds it with the right boundary

// Server &mdash; multer parses multipart
import multer from "multer";
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024, files: 1 }   // 10MB, 1 file
});

app.post("/api/posts", upload.single("cover"), async (req, res) =&gt; {
  // req.body.title  -&gt; "My post"
  // req.file        -&gt; { fieldname, originalname, mimetype, size, buffer }
  const key = `covers/${ulid()}.bin`;
  await s3.putObject({ Bucket, Key: key, Body: req.file.buffer, ContentType: req.file.mimetype });
  // ...save metadata, respond
});</code></pre>
<p><strong>Don&rsquo;t parse multipart by hand.</strong> Libraries: <strong>multer</strong> (Express classic), <strong>busboy</strong> (lower level, streaming), <strong>formidable</strong> (handles fields + files). For Next.js Route Handlers, use the native <code>request.formData()</code>. For large files, prefer <strong>presigned URLs</strong> direct to S3 and skip multipart through your server entirely &mdash; bytes through Node is wasteful and risky. Always set <code>limits</code> (file size, count) to prevent abuse; <strong>sniff</strong> the actual MIME type server-side (<strong>file-type</strong>) &mdash; the client-reported type is untrusted. Strip EXIF on uploaded images for privacy.</p>
'''

ANSWERS[94] = r'''
<p>A dynamic form builder lets non-developers configure forms (a survey tool, an admin form designer). Form structure is data, rendered into React.</p>
<pre><code>// Form schema in MongoDB
db.forms.insertOne({
  _id, title: "Contact",
  fields: [
    { id: "name",  type: "text",   label: "Name",  required: true },
    { id: "email", type: "email",  label: "Email", required: true },
    { id: "kind",  type: "select", label: "Topic", options: ["Sales", "Support"] },
    { id: "msg",   type: "textarea", label: "Message", required: true }
  ]
});

// React renderer
function Field({ field, register, errors }) {
  switch (field.type) {
    case "text":
    case "email":     return &lt;input type={field.type} {...register(field.id, { required: field.required })} /&gt;;
    case "textarea":  return &lt;textarea {...register(field.id)} /&gt;;
    case "select":    return (
      &lt;select {...register(field.id)}&gt;
        {field.options.map((o) =&gt; &lt;option key={o}&gt;{o}&lt;/option&gt;)}
      &lt;/select&gt;
    );
  }
}

function DynamicForm({ schema }) {
  const { register, handleSubmit, formState: { errors } } = useForm();
  return (
    &lt;form onSubmit={handleSubmit(submit)}&gt;
      {schema.fields.map((f) =&gt; &lt;Field key={f.id} field={f} register={register} errors={errors} /&gt;)}
      &lt;button&gt;Submit&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>
<p>Generate a Zod schema from the form definition for runtime validation server-side too. Libraries: <strong>react-jsonschema-form</strong> (RJSF) renders forms from JSON Schema; <strong>SurveyJS</strong> is feature-rich (skip logic, scoring, exports); <strong>Formily</strong> (Alibaba) for complex configurable forms; <strong>uniforms</strong> bridges schema to React. For visual builders, <strong>FormBricks</strong>, <strong>Tally</strong>, <strong>Typeform</strong>, <strong>Fillout</strong> are SaaS options &mdash; embed instead of build. Hard parts: <strong>conditional fields</strong> (&ldquo;show X only if Y is checked&rdquo;), <strong>repeating sections</strong> (multiple addresses), <strong>versioning</strong> (forms change; existing submissions reference the version they were created against), <strong>i18n</strong> of labels.</p>
'''

ANSWERS[95] = r'''
<p>Optimistic concurrency in MongoDB means letting writes proceed without locks but failing if the document changed since you read it. The pattern uses a <strong>version field</strong> in the filter.</p>
<pre><code>// Read
const doc = await Article.findById(id);
const currentVersion = doc.version;

// Edit in memory (UI)
doc.title = "Updated";

// Write &mdash; only succeeds if version unchanged
const result = await Article.updateOne(
  { _id: doc._id, version: currentVersion },
  { $set: { title: doc.title }, $inc: { version: 1 } }
);

if (result.matchedCount === 0) {
  // Someone else updated; refetch and let the user resolve
  throw new ConflictError("document_changed");
}</code></pre>
<p>Mongoose adds a <code>__v</code> version key automatically and uses it for the same purpose on <code>save()</code>. The pattern fits collaborative editing scenarios where two users may edit the same record concurrently &mdash; the second writer is rejected and retries. Compare to <strong>pessimistic locking</strong> (rare in MongoDB): take a session lock for the duration of an edit. Optimistic is preferred because it scales (no held locks), is non-blocking, and matches eventual UI patterns. For high-frequency counter increments, <strong>atomic operators</strong> (<code>$inc</code>, <code>$addToSet</code>) skip the read-modify-write entirely &mdash; race-free by construction. For multi-document atomicity, MongoDB <strong>transactions</strong> (4.0+) offer ACID with WriteConflict retry. <strong>Application-level conflict resolution</strong>: show the user the diff, let them choose; or auto-merge if fields don&rsquo;t overlap (CRDT territory &mdash; <strong>Yjs</strong>/<strong>Automerge</strong>).</p>
'''

ANSWERS[96] = r'''
<p>A recommendation system suggests items based on user behavior or item similarity. Approaches scale from naive to sophisticated:</p>
<ul>
<li><strong>Popularity-based</strong> &mdash; &ldquo;most-bought,&rdquo; &ldquo;trending now.&rdquo; Easy. Aggregation pipeline computes nightly.</li>
<li><strong>Content-based</strong> &mdash; recommend items whose features (tags, categories, text) resemble what the user liked. Cheap, no cross-user data needed.</li>
<li><strong>Collaborative filtering</strong> &mdash; &ldquo;users who liked X also liked Y.&rdquo; Requires interaction data; better recommendations.</li>
<li><strong>Hybrid + ML</strong> &mdash; modern recommenders combine signals; matrix factorization / two-tower models / sequence transformers.</li>
</ul>
<pre><code>// Simple: items co-purchased with X
db.orders.aggregate([
  { $match: { items: itemId } },
  { $unwind: "$items" },
  { $match: { items: { $ne: itemId } } },
  { $group: { _id: "$items", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
]);

// Modern: vector embeddings + Atlas Vector Search
db.products.aggregate([
  {
    $vectorSearch: {
      index: "embedding_index",
      path: "embedding",
      queryVector: userVector,    // user's interest vector
      numCandidates: 100,
      limit: 20
    }
  }
]);</code></pre>
<p>In 2026, the practical answer for most MERN apps is <strong>vector search</strong>: embed items (description / tags / images) with <strong>OpenAI</strong>/<strong>Cohere</strong>/<strong>Voyage AI</strong> embeddings, store in <strong>MongoDB Atlas Vector Search</strong>/<strong>Pinecone</strong>/<strong>Weaviate</strong>/<strong>Qdrant</strong>, query by user&rsquo;s history-derived vector. For pre-built recommenders, <strong>Algolia Recommend</strong>, <strong>Klevu</strong>, <strong>Recombee</strong>, <strong>Bloomreach</strong>. For YouTube-/Spotify-scale recommendations, run two-tower models in <strong>TensorFlow Recommenders</strong>/<strong>PyTorch</strong>; export top-K to <strong>Redis</strong>/<strong>MongoDB</strong>; serve in milliseconds. Always A/B test recommendation strategies (<strong>Statsig</strong>/<strong>LaunchDarkly</strong>); measure CTR, conversion, retention.</p>
'''

ANSWERS[97] = r'''
<p>API versioning lets you evolve your API without breaking existing clients. Three common styles:</p>
<ul>
<li><strong>URL path</strong> &mdash; <code>/api/v1/users</code>, <code>/api/v2/users</code>. Most explicit; easy to route. Common in MERN apps.</li>
<li><strong>Header</strong> &mdash; <code>Accept: application/vnd.myapp.v2+json</code>. Cleaner URLs; harder to test in browsers.</li>
<li><strong>Query parameter</strong> &mdash; <code>/api/users?api-version=2</code>. Easiest to ad-hoc test; weakest discipline.</li>
</ul>
<pre><code>// Path-based, Express
import v1 from "./routes/v1";
import v2 from "./routes/v2";

app.use("/api/v1", v1);
app.use("/api/v2", v2);

// Internal: share controllers, swap response shapers
v2.get("/users/:id", async (req, res) =&gt; {
  const u = await User.findById(req.params.id);
  res.json(toV2(u));   // new shape
});</code></pre>
<p>Strategy: <strong>additive changes never break</strong> (new optional fields, new endpoints) &mdash; do these without bumping the version. <strong>Bump the major version</strong> only on breaking changes (renamed fields, removed fields, changed semantics). Run two versions in parallel during the deprecation window (3-12 months). Communicate via <strong>Sunset</strong> and <strong>Deprecation</strong> HTTP headers (RFC 8594, 9745). Track who&rsquo;s still using v1 (per-API-key analytics) and reach out before turning it off. <strong>Internal APIs</strong> often skip versioning by deploying client + server together &mdash; especially with <strong>tRPC</strong> or <strong>GraphQL</strong> where the schema is shared. For public APIs, <strong>OpenAPI</strong> spec per version, generate client SDKs (<strong>openapi-typescript</strong>, <strong>orval</strong>, <strong>Speakeasy</strong>). For mobile clients you don&rsquo;t control, version-from-day-one &mdash; you can&rsquo;t force-update users.</p>
'''

ANSWERS[98] = r'''
<p>Client-side routing keeps the user&rsquo;s browser on the same page (no full reload) while the URL changes and the React tree swaps in new components. The 2026 dominant choices:</p>
<ul>
<li><strong>React Router v7</strong> &mdash; the merger of v6 + Remix. Both library mode (SPA) and framework mode (with loaders, actions, SSR). Most MERN tutorials.</li>
<li><strong>TanStack Router</strong> &mdash; type-safe params and search params, file-based routing, code-splitting, devtools. Popular and growing.</li>
<li><strong>Next.js App Router</strong> &mdash; file-based, but tied to Next.js / server components.</li>
</ul>
<pre><code>// React Router v7 library mode
import { createBrowserRouter, RouterProvider, Link, useParams, useNavigate } from "react-router";

const router = createBrowserRouter([
  { path: "/",          element: &lt;Home /&gt; },
  { path: "/posts/:id", element: &lt;Post /&gt; },
  { path: "*",          element: &lt;NotFound /&gt; }
]);

function Post() {
  const { id } = useParams();
  const navigate = useNavigate();
  return &lt;&gt;...&lt;Link to="/"&gt;Home&lt;/Link&gt;...&lt;/&gt;;
}

&lt;RouterProvider router={router} /&gt;</code></pre>
<p>Key concepts: <strong>browser history API</strong> under the hood; <strong>nested layouts</strong> (parent route persists when child changes &mdash; great for sidebars/tabs); <strong>data loaders</strong> (route-level data fetching, parallelized with route resolution); <strong>actions</strong> (form submissions tied to a route); <strong>error boundaries</strong> per route; <strong>code splitting</strong> via React.lazy + Suspense or framework-built-in. Watch out: <code>&lt;a href&gt;</code> causes a full reload &mdash; always use <code>&lt;Link&gt;</code> for internal links. <strong>Scroll restoration</strong>: React Router has <code>&lt;ScrollRestoration /&gt;</code>; otherwise you reset to top on every navigation. <strong>Auth guards</strong>: wrap protected routes (or use loaders that throw redirect responses). For server-rendered apps, framework mode handles SSR + data loading in one model.</p>
'''

ANSWERS[99] = r'''
<p>Breadcrumbs show the user&rsquo;s location in the site hierarchy and let them jump back. Three common ways to generate them in React:</p>
<pre><code>// 1. From route definitions (declarative)
const routes = [
  { path: "/",          name: "Home" },
  { path: "/products",  name: "Products" },
  { path: "/products/:id", name: (p) =&gt; p.product?.name ?? "Product" }
];

// 2. From URL path segments (cheap)
function Breadcrumbs() {
  const { pathname } = useLocation();
  const parts = pathname.split("/").filter(Boolean);
  return (
    &lt;nav aria-label="Breadcrumb"&gt;
      &lt;ol&gt;
        &lt;li&gt;&lt;Link to="/"&gt;Home&lt;/Link&gt;&lt;/li&gt;
        {parts.map((seg, i) =&gt; {
          const path = "/" + parts.slice(0, i + 1).join("/");
          const isLast = i === parts.length - 1;
          return (
            &lt;li key={path}&gt;
              {isLast ? &lt;span aria-current="page"&gt;{seg}&lt;/span&gt;
                     : &lt;Link to={path}&gt;{seg}&lt;/Link&gt;}
            &lt;/li&gt;
          );
        })}
      &lt;/ol&gt;
    &lt;/nav&gt;
  );
}

// 3. Component composition &mdash; each page declares its breadcrumb
&lt;Breadcrumbs items={[
  { label: "Home",     href: "/" },
  { label: "Products", href: "/products" },
  { label: "Widget" }
]} /&gt;</code></pre>
<p>Best practices: <strong>semantic markup</strong> &mdash; <code>&lt;nav aria-label="Breadcrumb"&gt;</code> + ordered list; the current page is not a link and carries <code>aria-current="page"</code>; <strong>structured data</strong> (<code>BreadcrumbList</code> JSON-LD) helps SEO &mdash; Google shows breadcrumbs in search results. <strong>Don&rsquo;t replicate the URL</strong> &mdash; if a breadcrumb says &ldquo;Mens / Shirts / Blue&rdquo; but the URL is <code>/products/12345</code>, derive labels from data. <strong>Truncate on mobile</strong> with ellipsis if long. Don&rsquo;t use breadcrumbs for shallow hierarchies (one or two levels); they add clutter without helping.</p>
'''

ANSWERS[100] = r'''
<p>A scalable folder structure for MERN follows two principles: <strong>colocate by feature, not by layer</strong>; and <strong>flatten until growth forces nesting</strong>.</p>
<pre><code>my-app/
├── apps/
│   ├── web/                          # React (Vite or Next.js)
│   │   ├── src/
│   │   │   ├── features/             # &lt;-- by feature, not by tech
│   │   │   │   ├── auth/
│   │   │   │   │   ├── components/
│   │   │   │   │   ├── hooks/
│   │   │   │   │   ├── api.ts
│   │   │   │   │   └── routes.tsx
│   │   │   │   ├── posts/
│   │   │   │   └── billing/
│   │   │   ├── components/ui/        # shared primitives
│   │   │   ├── lib/                  # shared utilities
│   │   │   ├── hooks/                # shared hooks
│   │   │   ├── routes/               # router config
│   │   │   └── main.tsx
│   └── api/                          # Express / Fastify / Hono
│       ├── src/
│       │   ├── modules/              # &lt;-- by feature
│       │   │   ├── users/
│       │   │   │   ├── routes.ts
│       │   │   │   ├── controller.ts
│       │   │   │   ├── service.ts
│       │   │   │   ├── model.ts
│       │   │   │   └── schema.ts
│       │   │   ├── posts/
│       │   │   └── billing/
│       │   ├── middleware/
│       │   ├── lib/db.ts
│       │   └── index.ts
├── packages/
│   ├── schemas/                      # shared Zod schemas
│   ├── ui/                           # shared React components
│   └── config/                       # eslint, tsconfig, prettier
├── package.json                       # workspaces
├── turbo.json                         # Turborepo
└── pnpm-workspace.yaml</code></pre>
<p>Why this scales: features are self-contained (delete a feature = delete a folder); shared cross-cutting code lives in <code>packages/</code>; <strong>schemas</strong> shared between client and server kill drift; <strong>monorepo tools</strong> (<strong>Turborepo</strong>/<strong>Nx</strong>/<strong>moon</strong>) cache builds and run only changed targets. Use <strong>pnpm</strong>/<strong>Bun</strong> workspaces over npm for performance. <strong>Path aliases</strong> (<code>@/features/auth</code>) keep imports clean. <strong>Avoid</strong>: a top-level <code>components/</code> folder containing 200 unrelated files; deep nesting (more than 3 folders) without reason; mixing <code>controllers/</code>+<code>models/</code>+<code>routes/</code> when feature folders read better. Refactor as the app grows; over-architecting day-one slows you down.</p>
'''
