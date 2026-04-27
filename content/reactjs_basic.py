"""ReactJS Basic — 101 detailed answers."""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''
<p><strong>React</strong> is a JavaScript library for building user interfaces &mdash; created by Facebook (now Meta) in 2013 and now maintained by an open-source community. It powers parts of Facebook, Instagram, Netflix, Airbnb, and thousands of other apps.</p>

<p>React&rsquo;s core idea: <strong>describe what your UI should look like for any given state, and React figures out how to update the DOM efficiently when that state changes</strong>. You write components &mdash; reusable pieces that combine markup, logic, and styling &mdash; and compose them into full pages.</p>

<pre><code>// A simple React component
function Welcome() {
  return &lt;h1&gt;Hello, world!&lt;/h1&gt;;
}</code></pre>

<p><strong>Why developers use React:</strong></p>
<ul>
  <li><strong>Component-based</strong> &mdash; build UI from small reusable pieces.</li>
  <li><strong>Declarative</strong> &mdash; describe the result, not the steps to get there.</li>
  <li><strong>Virtual DOM</strong> &mdash; React updates only what changed, making rendering fast.</li>
  <li><strong>Huge ecosystem</strong> &mdash; routing, state management, UI libraries, and tooling.</li>
  <li><strong>Strong job market</strong> &mdash; one of the most-requested skills in front-end roles.</li>
</ul>

<p>React isn&rsquo;t a framework like Angular &mdash; it&rsquo;s focused on the view layer. For routing, forms, and data fetching, you compose React with other libraries (React Router, TanStack Query, etc.) or use a meta-framework like Next.js or Remix.</p>
'''

ANSWERS[2] = r'''
<p>React&rsquo;s key features make UI development faster, more predictable, and easier to scale.</p>

<table>
  <tr><th>Feature</th><th>What it does</th></tr>
  <tr><td><strong>Components</strong></td><td>Reusable, self-contained UI pieces with their own logic and styling</td></tr>
  <tr><td><strong>JSX</strong></td><td>HTML-like syntax inside JavaScript; compiles to function calls</td></tr>
  <tr><td><strong>Virtual DOM</strong></td><td>In-memory UI tree React diffs to compute minimal real DOM updates</td></tr>
  <tr><td><strong>One-way data flow</strong></td><td>Data flows down via props; predictable, easier to debug</td></tr>
  <tr><td><strong>Hooks</strong></td><td>Add state/side effects to function components</td></tr>
  <tr><td><strong>Declarative</strong></td><td>Describe what the UI looks like; React handles the how</td></tr>
  <tr><td><strong>Cross-platform</strong></td><td>Same model for web (React DOM), mobile (React Native)</td></tr>
</table>

<pre><code>function Counter() {
  const [count, setCount] = useState(0);

  return (
    &lt;button onClick={() =&gt; setCount(count + 1)}&gt;
      Clicked {count} times
    &lt;/button&gt;
  );
}</code></pre>

<p>This tiny component demonstrates several features at once: JSX (HTML-like syntax), hooks (<code>useState</code>), declarative rendering (the button always shows the current count), and event handling. React updates the DOM efficiently every time you click.</p>
'''

ANSWERS[3] = r'''
<p><strong>JSX</strong> (JavaScript XML) is a syntax extension that lets you write HTML-like markup inside JavaScript. It&rsquo;s the language of React components.</p>

<pre><code>const element = &lt;h1 className="greeting"&gt;Hello, {name}!&lt;/h1&gt;;</code></pre>

<p>JSX isn&rsquo;t valid JavaScript on its own &mdash; a build tool (Babel, Vite, esbuild) compiles it to <code>React.createElement()</code> calls before the browser runs it. The output:</p>

<pre><code>const element = React.createElement(
  "h1",
  { className: "greeting" },
  "Hello, ",
  name,
  "!"
);</code></pre>

<p><strong>Key JSX rules:</strong></p>
<ul>
  <li><strong>Use <code>className</code>, not <code>class</code></strong> &mdash; <code>class</code> is reserved in JavaScript.</li>
  <li><strong>Curly braces <code>{}</code> embed JavaScript</strong> &mdash; expressions, variables, function calls.</li>
  <li><strong>One root element</strong> &mdash; multiple top-level tags need a wrapper or fragment <code>&lt;&gt;...&lt;/&gt;</code>.</li>
  <li><strong>Self-closing tags need <code>/</code></strong> &mdash; <code>&lt;img /&gt;</code>, not <code>&lt;img&gt;</code>.</li>
  <li><strong>camelCase attributes</strong> &mdash; <code>onClick</code>, not <code>onclick</code>; <code>tabIndex</code>, not <code>tabindex</code>.</li>
</ul>

<p>JSX makes components more readable than equivalent <code>createElement</code> calls. You don&rsquo;t have to use JSX to build React apps, but virtually everyone does.</p>
'''

ANSWERS[4] = r'''
<p>You create a React component by writing a JavaScript function that returns JSX. This is the modern, recommended approach &mdash; called a <strong>functional component</strong>.</p>

<pre><code>// Greeting.jsx
function Greeting() {
  return &lt;h1&gt;Hello, world!&lt;/h1&gt;;
}

export default Greeting;</code></pre>

<p>Then use it like an HTML tag in another component:</p>

<pre><code>import Greeting from "./Greeting";

function App() {
  return (
    &lt;div&gt;
      &lt;Greeting /&gt;
      &lt;Greeting /&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Component naming rules:</strong></p>
<ul>
  <li><strong>Must start with a capital letter</strong> &mdash; <code>Greeting</code>, not <code>greeting</code>. React uses the case to distinguish your components from HTML tags.</li>
  <li><strong>One component per file</strong> is conventional &mdash; makes imports clean.</li>
  <li><strong>Match the file name</strong> &mdash; <code>Greeting</code> in <code>Greeting.jsx</code>.</li>
</ul>

<p><strong>Components can accept props</strong> (data passed in):</p>

<pre><code>function Greeting({ name }) {
  return &lt;h1&gt;Hello, {name}!&lt;/h1&gt;;
}

// Use it
&lt;Greeting name="Alice" /&gt;</code></pre>

<p>Components are the building blocks of every React app. Compose small components into pages; each one stays small and focused on one job.</p>
'''

ANSWERS[5] = r'''
<p>React has two ways to write components: <strong>functional</strong> and <strong>class</strong>. Modern React (since hooks shipped in 2019) strongly prefers functional components for everything.</p>

<table>
  <tr><th></th><th>Functional Component</th><th>Class Component</th></tr>
  <tr><td>Syntax</td><td>Plain JavaScript function</td><td>ES6 class extending <code>React.Component</code></td></tr>
  <tr><td>State</td><td><code>useState</code> hook</td><td><code>this.state</code></td></tr>
  <tr><td>Side effects</td><td><code>useEffect</code> hook</td><td>Lifecycle methods</td></tr>
  <tr><td>Code volume</td><td>Compact</td><td>More boilerplate</td></tr>
  <tr><td>Modern preference</td><td>Yes &mdash; recommended</td><td>Legacy, not deprecated but not for new code</td></tr>
</table>

<pre><code>// Functional (modern)
function Counter() {
  const [count, setCount] = useState(0);
  return &lt;button onClick={() =&gt; setCount(count + 1)}&gt;{count}&lt;/button&gt;;
}

// Class (legacy)
class Counter extends React.Component {
  state = { count: 0 };
  render() {
    return (
      &lt;button onClick={() =&gt; this.setState({ count: this.state.count + 1 })}&gt;
        {this.state.count}
      &lt;/button&gt;
    );
  }
}</code></pre>

<p><strong>Why functional won:</strong> hooks gave functional components everything classes had (state, lifecycle, refs) plus better composition (custom hooks reuse logic across components). Less code, easier to test, and they avoid <code>this</code> binding bugs.</p>

<p><strong>You&rsquo;ll still see classes in legacy codebases</strong> &mdash; they&rsquo;re fully supported &mdash; but every React tutorial, library, and team in 2026 uses functional components for new code.</p>
'''

ANSWERS[6] = r'''
<p>A functional component is a JavaScript function that takes <strong>props</strong> as an argument and returns JSX. The simplest possible component:</p>

<pre><code>function Welcome() {
  return &lt;h1&gt;Welcome!&lt;/h1&gt;;
}</code></pre>

<p><strong>Accepting props:</strong></p>
<pre><code>function Welcome(props) {
  return &lt;h1&gt;Welcome, {props.name}!&lt;/h1&gt;;
}

// Use:
&lt;Welcome name="Alice" /&gt;</code></pre>

<p><strong>Modern style with destructuring</strong> (cleaner, recommended):</p>
<pre><code>function Welcome({ name, age }) {
  return (
    &lt;div&gt;
      &lt;h1&gt;Welcome, {name}!&lt;/h1&gt;
      &lt;p&gt;You are {age} years old.&lt;/p&gt;
    &lt;/div&gt;
  );
}

&lt;Welcome name="Alice" age={30} /&gt;</code></pre>

<p><strong>Arrow function form &mdash; equally valid:</strong></p>
<pre><code>const Welcome = ({ name }) =&gt; &lt;h1&gt;Welcome, {name}!&lt;/h1&gt;;

// With multiple lines:
const Welcome = ({ name }) =&gt; {
  const greeting = `Welcome, ${name}!`;
  return &lt;h1&gt;{greeting}&lt;/h1&gt;;
};</code></pre>

<p><strong>Adding state with hooks:</strong></p>
<pre><code>import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);
  return (
    &lt;button onClick={() =&gt; setCount(count + 1)}&gt;
      Clicked {count} times
    &lt;/button&gt;
  );
}</code></pre>

<p>Functional components combined with hooks are the entire modern React API. Every new component you write should be functional.</p>
'''

ANSWERS[7] = r'''
<p>A class component is created by extending <code>React.Component</code> and implementing a <code>render()</code> method that returns JSX. While modern React prefers functional components, class components are still fully supported and you&rsquo;ll find them in legacy codebases.</p>

<pre><code>import React from "react";

class Welcome extends React.Component {
  render() {
    return &lt;h1&gt;Welcome, {this.props.name}!&lt;/h1&gt;;
  }
}

export default Welcome;</code></pre>

<p><strong>With state and methods:</strong></p>
<pre><code>class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
    this.handleClick = this.handleClick.bind(this);   // bind manually
  }

  handleClick() {
    this.setState({ count: this.state.count + 1 });
  }

  render() {
    return (
      &lt;button onClick={this.handleClick}&gt;
        Clicked {this.state.count} times
      &lt;/button&gt;
    );
  }
}</code></pre>

<p><strong>Modern class shorthand</strong> (uses class field syntax to avoid <code>bind</code>):</p>
<pre><code>class Counter extends React.Component {
  state = { count: 0 };           // class field; no constructor needed

  handleClick = () =&gt; {            // arrow auto-binds this
    this.setState({ count: this.state.count + 1 });
  };

  render() {
    return &lt;button onClick={this.handleClick}&gt;{this.state.count}&lt;/button&gt;;
  }
}</code></pre>

<p><strong>Quirks of class components:</strong></p>
<ul>
  <li><strong><code>this</code> binding</strong> &mdash; methods need explicit binding (or arrow syntax) to access <code>this</code> properly.</li>
  <li><strong>Verbose</strong> &mdash; even simple components have more boilerplate than functional equivalents.</li>
  <li><strong>Lifecycle methods</strong> &mdash; <code>componentDidMount</code>, <code>componentDidUpdate</code>, etc., for side effects.</li>
</ul>

<p>For any new code in 2026, write functional components. Use class components only when you need to maintain or extend an older codebase.</p>
'''

ANSWERS[8] = r'''
<p>The <code>render()</code> method is the only required method in a class component. It returns the JSX that React should display on the screen for the component&rsquo;s current props and state.</p>

<pre><code>class Greeting extends React.Component {
  render() {
    return &lt;h1&gt;Hello, {this.props.name}!&lt;/h1&gt;;
  }
}</code></pre>

<p><strong>Key rules of <code>render()</code>:</strong></p>
<ul>
  <li><strong>Must return JSX</strong> (or <code>null</code>, an array, a string, or a number).</li>
  <li><strong>Should be pure</strong> &mdash; given the same props and state, it should always return the same output. Don&rsquo;t modify state or perform side effects (network calls, timers, DOM mutations) inside <code>render()</code>.</li>
  <li><strong>Called on every update</strong> &mdash; React invokes it whenever state or props change to re-render the component.</li>
  <li><strong>Reads <code>this.props</code> and <code>this.state</code></strong> to decide what to display.</li>
</ul>

<pre><code>class Counter extends React.Component {
  state = { count: 0 };

  render() {
    // No side effects here — just compute the JSX
    return (
      &lt;div&gt;
        &lt;p&gt;Count: {this.state.count}&lt;/p&gt;
        &lt;button onClick={() =&gt; this.setState({ count: this.state.count + 1 })}&gt;
          Increment
        &lt;/button&gt;
      &lt;/div&gt;
    );
  }
}</code></pre>

<p><strong>Conditional rendering</strong> in <code>render()</code>:</p>
<pre><code>render() {
  if (this.props.loading) return &lt;div&gt;Loading...&lt;/div&gt;;
  if (this.props.error)   return &lt;div&gt;Error!&lt;/div&gt;;
  return &lt;div&gt;{this.props.data}&lt;/div&gt;;
}</code></pre>

<p>The functional component equivalent has no <code>render()</code> method &mdash; the function itself IS the render. The body of the function returns JSX directly. This is one reason functional components feel cleaner.</p>
'''

ANSWERS[9] = r'''
<p><strong>Props</strong> (short for "properties") are how parent components pass data down to their children. Props are read-only inputs &mdash; the child receives them and uses them to render. They flow one direction: parent &rarr; child.</p>

<pre><code>// Parent passes props
function App() {
  return &lt;Greeting name="Alice" age={30} /&gt;;
}

// Child receives props
function Greeting(props) {
  return (
    &lt;div&gt;
      &lt;h1&gt;Hello, {props.name}!&lt;/h1&gt;
      &lt;p&gt;Age: {props.age}&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Modern style: destructure props in the function signature:</strong></p>
<pre><code>function Greeting({ name, age }) {
  return (
    &lt;div&gt;
      &lt;h1&gt;Hello, {name}!&lt;/h1&gt;
      &lt;p&gt;Age: {age}&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Props can be any JavaScript value:</strong></p>
<pre><code>&lt;UserCard
  name="Alice"
  age={30}
  isActive={true}
  hobbies={["reading", "hiking"]}
  address={{ city: "Boston", state: "MA" }}
  onClick={handleClick}
/&gt;</code></pre>

<ul>
  <li><strong>Strings</strong> use double quotes: <code>name="Alice"</code></li>
  <li><strong>Other types</strong> use curly braces: <code>age={30}</code>, <code>onClick={handleClick}</code></li>
  <li><strong>Booleans default to true</strong>: <code>&lt;Button disabled /&gt;</code> = <code>&lt;Button disabled={true} /&gt;</code></li>
</ul>

<p><strong>Props are read-only.</strong> A child must NOT modify its props directly. To "change" what a child displays, the parent passes new props. To send data UP from child to parent, pass a callback function as a prop:</p>

<pre><code>// Parent
&lt;Button onClick={() =&gt; alert("clicked!")} /&gt;

// Child
function Button({ onClick }) {
  return &lt;button onClick={onClick}&gt;Click me&lt;/button&gt;;
}</code></pre>

<p>Props + state are how React apps manage all data flow.</p>
'''

ANSWERS[10] = r'''
<p><strong>State</strong> is data that a component owns and can change over time. Unlike props (which come from a parent and are read-only), state is local to a component and triggers re-renders when it changes.</p>

<pre><code>import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);   // initial state: 0

  return (
    &lt;div&gt;
      &lt;p&gt;You clicked {count} times&lt;/p&gt;
      &lt;button onClick={() =&gt; setCount(count + 1)}&gt;
        Click me
      &lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>The flow:</strong></p>
<ol>
  <li>Component renders with <code>count = 0</code> &mdash; UI shows "You clicked 0 times".</li>
  <li>User clicks the button.</li>
  <li><code>setCount(1)</code> tells React the state changed.</li>
  <li>React re-renders the component with <code>count = 1</code>.</li>
  <li>UI updates to "You clicked 1 times".</li>
</ol>

<p><strong>Common uses of state:</strong></p>
<ul>
  <li>Form input values</li>
  <li>Toggle switches (open/closed, expanded/collapsed)</li>
  <li>Loading status (loading/loaded/error)</li>
  <li>Fetched data from APIs</li>
  <li>UI selections (selected tab, active item)</li>
</ul>

<p><strong>State vs props:</strong></p>
<table>
  <tr><th></th><th>State</th><th>Props</th></tr>
  <tr><td>Owner</td><td>The component itself</td><td>The parent component</td></tr>
  <tr><td>Mutability</td><td>Can change (via setter)</td><td>Read-only</td></tr>
  <tr><td>Triggers re-render</td><td>Yes</td><td>Yes (when parent re-renders)</td></tr>
  <tr><td>Use for</td><td>Component-internal data</td><td>Configuration from outside</td></tr>
</table>

<p>State is what makes components interactive. Without it, components would always render the same thing for the same inputs.</p>
'''

ANSWERS[11] = r'''
<p>In a class component, state is initialized either inside the constructor or as a class field (modern shorthand). Both forms create the initial <code>this.state</code> object.</p>

<p><strong>Constructor form (traditional):</strong></p>
<pre><code>class Counter extends React.Component {
  constructor(props) {
    super(props);                   // always call super first
    this.state = {
      count: 0,
      isActive: false,
      items: []
    };
  }

  render() {
    return &lt;p&gt;Count: {this.state.count}&lt;/p&gt;;
  }
}</code></pre>

<p><strong>Class field form (modern shorthand)</strong> &mdash; no constructor needed:</p>
<pre><code>class Counter extends React.Component {
  state = {
    count: 0,
    isActive: false,
    items: []
  };

  render() {
    return &lt;p&gt;Count: {this.state.count}&lt;/p&gt;;
  }
}</code></pre>

<p><strong>State must be an object</strong> in class components &mdash; you can&rsquo;t use a primitive directly. If you only need one value, wrap it: <code>{ value: 0 }</code>.</p>

<p><strong>Initialize from props</strong> (common pattern):</p>
<pre><code>class UserProfile extends React.Component {
  state = {
    name: this.props.initialName || "",
    age: this.props.initialAge || 0
  };
}</code></pre>

<p><strong>Important rules:</strong></p>
<ul>
  <li><strong>Never modify <code>this.state</code> directly</strong> &mdash; only the constructor can assign to it. After that, use <code>setState()</code>.</li>
  <li><strong>Always call <code>super(props)</code></strong> first in the constructor &mdash; otherwise <code>this</code> won&rsquo;t be available.</li>
  <li><strong>State should be the minimal data needed</strong> &mdash; don&rsquo;t store derivable values; compute them in <code>render()</code>.</li>
</ul>

<p>The class field form is now standard &mdash; cleaner and more concise. The constructor form is legacy.</p>
'''

ANSWERS[12] = r'''
<p>In a functional component, you initialize state with the <code>useState</code> hook. Pass the initial value to <code>useState()</code>; it returns an array with two items: the current state and a function to update it.</p>

<pre><code>import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);     // initial: 0

  return &lt;p&gt;Count: {count}&lt;/p&gt;;
}</code></pre>

<p>The square brackets <code>[count, setCount]</code> are array destructuring. <code>useState</code> always returns <code>[currentValue, updateFunction]</code> &mdash; the names are conventional, not required. Common pattern: <code>[noun, setNoun]</code>.</p>

<p><strong>Multiple state variables</strong> &mdash; just call <code>useState</code> multiple times:</p>
<pre><code>function UserForm() {
  const [name, setName] = useState("");
  const [age, setAge] = useState(0);
  const [isActive, setIsActive] = useState(false);
  // Each value is independent
}</code></pre>

<p><strong>Initial state can be any type</strong> &mdash; no need for an object wrapper like in classes:</p>
<pre><code>const [count, setCount] = useState(0);              // number
const [name, setName] = useState("");                // string
const [items, setItems] = useState([]);              // array
const [user, setUser] = useState({ name: "", age: 0 }); // object
const [isOpen, setIsOpen] = useState(false);         // boolean
const [data, setData] = useState(null);              // null until loaded</code></pre>

<p><strong>Lazy initialization</strong> &mdash; if computing the initial value is expensive, pass a function instead. React calls it only on the first render:</p>
<pre><code>const [data, setData] = useState(() =&gt; expensiveComputation());</code></pre>

<p>This is the modern way to manage component state &mdash; far less code than class equivalents. Most components use 2-5 useState calls; for more complex state, reach for <code>useReducer</code>.</p>
'''

ANSWERS[13] = r'''
<p>The <code>useState</code> hook is React&rsquo;s most fundamental hook &mdash; it lets functional components remember values between renders. Every interactive component uses it.</p>

<pre><code>import { useState } from "react";

const [value, setValue] = useState(initialValue);</code></pre>

<p><strong>What it returns:</strong></p>
<ul>
  <li><strong><code>value</code></strong> &mdash; the current state value (matches <code>initialValue</code> on first render).</li>
  <li><strong><code>setValue</code></strong> &mdash; a function to update the state and trigger a re-render.</li>
</ul>

<p><strong>Complete example:</strong></p>
<pre><code>function Counter() {
  const [count, setCount] = useState(0);

  function increment() {
    setCount(count + 1);
  }

  function reset() {
    setCount(0);
  }

  return (
    &lt;div&gt;
      &lt;p&gt;Count: {count}&lt;/p&gt;
      &lt;button onClick={increment}&gt;+1&lt;/button&gt;
      &lt;button onClick={reset}&gt;Reset&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Key behaviors:</strong></p>
<ul>
  <li><strong>State persists between renders</strong> &mdash; React remembers the latest value automatically.</li>
  <li><strong>Calling the setter triggers a re-render</strong> with the new value.</li>
  <li><strong>State updates may be asynchronous</strong> &mdash; React batches multiple setState calls in the same event for performance.</li>
  <li><strong>Each component instance has its own state</strong> &mdash; <code>&lt;Counter /&gt;&lt;Counter /&gt;</code> renders two independent counters.</li>
</ul>

<p><strong>Functional updater form</strong> &mdash; for state that depends on the previous value:</p>
<pre><code>setCount(count + 1);            // works most of the time
setCount(prev =&gt; prev + 1);      // safer when batching is involved</code></pre>

<p>The functional form prevents stale-state bugs: in event handlers that fire rapidly or set state multiple times, the function form always gets the latest value.</p>

<p><strong>Rules of hooks</strong>: only call hooks at the top level of your component (not inside loops, conditions, or nested functions), and only inside function components or custom hooks. React relies on call order to track which state belongs to which hook.</p>
'''

ANSWERS[14] = r'''
<p>In a class component, you update state with <code>this.setState()</code>. Never modify <code>this.state</code> directly &mdash; React won&rsquo;t notice and won&rsquo;t re-render.</p>

<pre><code>class Counter extends React.Component {
  state = { count: 0 };

  increment = () =&gt; {
    this.setState({ count: this.state.count + 1 });
  };

  render() {
    return (
      &lt;button onClick={this.increment}&gt;
        Count: {this.state.count}
      &lt;/button&gt;
    );
  }
}</code></pre>

<p><strong>Key rules:</strong></p>
<ul>
  <li><strong><code>setState</code> merges</strong> the object you pass with the existing state &mdash; you don&rsquo;t need to include unchanged keys.</li>
  <li><strong>Updates are asynchronous</strong> &mdash; React batches them for performance. Don&rsquo;t read <code>this.state</code> immediately after calling <code>setState</code> expecting the new value.</li>
  <li><strong>Triggers a re-render</strong> &mdash; React calls <code>render()</code> again with the updated state.</li>
</ul>

<pre><code>// Partial state update — other keys preserved
this.setState({ count: 5 });          // count updates; isActive stays
// state was: { count: 0, isActive: true }
// becomes:   { count: 5, isActive: true }</code></pre>

<p><strong>Functional update form</strong> &mdash; use when new state depends on previous state:</p>
<pre><code>// WRONG — may use stale state
this.setState({ count: this.state.count + 1 });

// CORRECT — always uses the latest state
this.setState((prevState) =&gt; ({
  count: prevState.count + 1
}));</code></pre>

<p>This matters when multiple <code>setState</code> calls happen in the same event &mdash; React batches them, and direct reads return the OLD state.</p>

<p><strong>Callback after update</strong>:</p>
<pre><code>this.setState({ count: 5 }, () =&gt; {
  console.log("Updated:", this.state.count);   // 5
});</code></pre>

<p>The optional second argument runs after the state is committed. Rarely needed in practice; <code>componentDidUpdate</code> is usually clearer.</p>

<p>In modern functional components, <code>setState</code> is replaced by the setter returned from <code>useState</code> (e.g., <code>setCount</code>). Same idea, different syntax.</p>
'''

ANSWERS[15] = r'''
<p>In a functional component, you update state by calling the setter function returned by <code>useState</code>. Pass the new value &mdash; React stores it and re-renders the component.</p>

<pre><code>import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);

  function increment() {
    setCount(count + 1);             // pass new value directly
  }

  return (
    &lt;button onClick={increment}&gt;
      Count: {count}
    &lt;/button&gt;
  );
}</code></pre>

<p><strong>Functional updater form</strong> &mdash; preferred when new state depends on previous state:</p>
<pre><code>setCount(prev =&gt; prev + 1);</code></pre>

<p>The function receives the latest state and returns the new value. Safe even when React batches multiple updates.</p>

<p><strong>Why functional form matters</strong> &mdash; consider this:</p>
<pre><code>function handleClick() {
  setCount(count + 1);
  setCount(count + 1);
  setCount(count + 1);
}
// Result: count goes from 0 to 1, NOT 3
// Each setCount uses the SAME stale value of count (0)</code></pre>

<pre><code>function handleClick() {
  setCount(prev =&gt; prev + 1);
  setCount(prev =&gt; prev + 1);
  setCount(prev =&gt; prev + 1);
}
// Result: count goes from 0 to 3 — each receives the latest</code></pre>

<p><strong>Updating object state</strong> &mdash; unlike <code>setState</code> in classes, <code>useState</code> setters REPLACE rather than merge:</p>
<pre><code>const [user, setUser] = useState({ name: "Alice", age: 30 });

// WRONG — replaces entire state, losing 'age'
setUser({ name: "Bob" });

// CORRECT — spread to preserve other fields
setUser({ ...user, name: "Bob" });

// SAFER with functional form
setUser(prev =&gt; ({ ...prev, name: "Bob" }));</code></pre>

<p><strong>Updating array state</strong>:</p>
<pre><code>const [items, setItems] = useState([]);

// Add: spread + new item
setItems([...items, newItem]);
setItems(prev =&gt; [...prev, newItem]);   // safer

// Remove
setItems(prev =&gt; prev.filter(item =&gt; item.id !== id));

// Update one
setItems(prev =&gt; prev.map(item =&gt;
  item.id === id ? { ...item, name: "new" } : item
));</code></pre>

<p>Always create new objects/arrays &mdash; React detects state changes by reference, so mutating in place won&rsquo;t trigger a re-render.</p>
'''

ANSWERS[16] = r'''
<p>A React component&rsquo;s lifecycle is the sequence of phases it goes through from creation to removal. Understanding the lifecycle helps you decide when to fetch data, set up timers, or clean up resources.</p>

<table>
  <tr><th>Phase</th><th>What happens</th><th>Class methods</th><th>Functional equivalent</th></tr>
  <tr><td>Mounting</td><td>Component is created and inserted into DOM</td><td><code>constructor</code>, <code>render</code>, <code>componentDidMount</code></td><td><code>useState</code>, <code>useEffect</code> (empty deps)</td></tr>
  <tr><td>Updating</td><td>Component re-renders due to props/state change</td><td><code>render</code>, <code>componentDidUpdate</code></td><td><code>useEffect</code> (with deps)</td></tr>
  <tr><td>Unmounting</td><td>Component removed from DOM</td><td><code>componentWillUnmount</code></td><td><code>useEffect</code> cleanup function</td></tr>
</table>

<p><strong>Mounting flow:</strong></p>
<ol>
  <li>Constructor runs (initial state set up).</li>
  <li>First <code>render()</code> produces JSX.</li>
  <li>React inserts the result into the real DOM.</li>
  <li><code>componentDidMount()</code> fires &mdash; perfect place for API calls, subscriptions, DOM measurements.</li>
</ol>

<p><strong>Updating flow</strong> (when state or props change):</p>
<ol>
  <li><code>render()</code> runs again.</li>
  <li>React diffs the new JSX against the old, updates the DOM minimally.</li>
  <li><code>componentDidUpdate(prevProps, prevState)</code> fires &mdash; react to prop/state changes (e.g., refetch when an ID prop changes).</li>
</ol>

<p><strong>Unmounting flow:</strong></p>
<ol>
  <li><code>componentWillUnmount()</code> fires &mdash; clean up timers, subscriptions, network requests.</li>
  <li>Component is removed from the DOM.</li>
</ol>

<p><strong>Functional component equivalent</strong> &mdash; one hook handles all three:</p>
<pre><code>useEffect(() =&gt; {
  console.log("mounted or updated");

  return () =&gt; {
    console.log("about to unmount or re-run");   // cleanup
  };
}, [/* dependencies */]);</code></pre>

<p>Modern React abstracts the lifecycle into <code>useEffect</code>: empty dependency array runs once (mount); with deps runs on those changes (update); cleanup function runs on unmount and before the next effect.</p>
'''

ANSWERS[17] = r'''
<p>Class components have multiple lifecycle methods spanning mount, update, and unmount phases. The most common ones to know:</p>

<table>
  <tr><th>Method</th><th>Phase</th><th>Common use</th></tr>
  <tr><td><code>constructor(props)</code></td><td>Mount</td><td>Initialize state, bind methods</td></tr>
  <tr><td><code>render()</code></td><td>Mount + Update</td><td>Return JSX (required)</td></tr>
  <tr><td><code>componentDidMount()</code></td><td>After Mount</td><td>API calls, subscriptions, DOM access</td></tr>
  <tr><td><code>shouldComponentUpdate(nextProps, nextState)</code></td><td>Before Update</td><td>Performance: skip render if returns false</td></tr>
  <tr><td><code>componentDidUpdate(prevProps, prevState)</code></td><td>After Update</td><td>React to prop/state changes</td></tr>
  <tr><td><code>componentWillUnmount()</code></td><td>Before Unmount</td><td>Cleanup timers, subscriptions, listeners</td></tr>
  <tr><td><code>componentDidCatch(error, info)</code></td><td>Error Boundary</td><td>Catch errors from descendants</td></tr>
</table>

<pre><code>class UserProfile extends React.Component {
  state = { user: null, loading: true };

  componentDidMount() {
    fetch(`/api/users/${this.props.id}`)
      .then(res =&gt; res.json())
      .then(user =&gt; this.setState({ user, loading: false }));
  }

  componentDidUpdate(prevProps) {
    if (prevProps.id !== this.props.id) {
      // Refetch when id changes
      this.setState({ loading: true });
      fetch(`/api/users/${this.props.id}`)
        .then(res =&gt; res.json())
        .then(user =&gt; this.setState({ user, loading: false }));
    }
  }

  componentWillUnmount() {
    // Cancel any pending requests, clear timers, etc.
  }

  render() {
    if (this.state.loading) return &lt;div&gt;Loading...&lt;/div&gt;;
    return &lt;div&gt;{this.state.user.name}&lt;/div&gt;;
  }
}</code></pre>

<p><strong>Less common but worth knowing:</strong></p>
<ul>
  <li><strong><code>getDerivedStateFromProps(props, state)</code></strong> &mdash; static method to derive state from props before each render.</li>
  <li><strong><code>getSnapshotBeforeUpdate(prevProps, prevState)</code></strong> &mdash; capture DOM info (e.g., scroll position) right before an update applies.</li>
</ul>

<p><strong>Deprecated in React 17+</strong>: <code>componentWillMount</code>, <code>componentWillReceiveProps</code>, <code>componentWillUpdate</code> &mdash; replaced by safer alternatives. Don&rsquo;t use them.</p>

<p>For new code, use functional components with <code>useEffect</code> &mdash; one hook covers mount, update, and unmount cleanly.</p>
'''

ANSWERS[18] = r'''
<p><code>componentDidMount()</code> is called <strong>once, immediately after the component is inserted into the DOM</strong>. It&rsquo;s the standard place to do anything that needs the DOM to exist or that should run only once on creation.</p>

<pre><code>class WeatherWidget extends React.Component {
  state = { weather: null, loading: true };

  componentDidMount() {
    // Fetch initial data
    fetch("/api/weather")
      .then(res =&gt; res.json())
      .then(weather =&gt; this.setState({ weather, loading: false }));
  }

  render() {
    if (this.state.loading) return &lt;div&gt;Loading weather...&lt;/div&gt;;
    return &lt;div&gt;{this.state.weather.temperature}&deg;F&lt;/div&gt;;
  }
}</code></pre>

<p><strong>Common uses:</strong></p>
<ul>
  <li><strong>API calls / data fetching</strong> &mdash; load data once after the component appears.</li>
  <li><strong>Subscriptions</strong> &mdash; subscribe to a WebSocket, event bus, or store.</li>
  <li><strong>DOM measurements</strong> &mdash; the real DOM exists now; you can get sizes or positions.</li>
  <li><strong>Timer setup</strong> &mdash; <code>setInterval</code> for periodic updates.</li>
  <li><strong>Third-party library init</strong> &mdash; integrate with a chart library, map, video player.</li>
</ul>

<pre><code>class Clock extends React.Component {
  state = { time: new Date() };

  componentDidMount() {
    this.timerId = setInterval(() =&gt; {
      this.setState({ time: new Date() });
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.timerId);    // ALWAYS clean up
  }

  render() {
    return &lt;p&gt;{this.state.time.toLocaleTimeString()}&lt;/p&gt;;
  }
}</code></pre>

<p>If you set up something in <code>componentDidMount</code>, you almost always need to tear it down in <code>componentWillUnmount</code> &mdash; otherwise you leak memory or trigger updates on unmounted components.</p>

<p><strong>Functional component equivalent:</strong></p>
<pre><code>useEffect(() =&gt; {
  // Runs once after mount (empty dep array)
  fetchWeather();

  return () =&gt; {
    // Optional cleanup on unmount
  };
}, []);   // empty array means "run only once"</code></pre>

<p><code>useEffect</code> with empty <code>[]</code> dependencies replicates <code>componentDidMount</code> exactly &mdash; the cleanup function replaces <code>componentWillUnmount</code>.</p>
'''

ANSWERS[19] = r'''
<p><code>componentDidUpdate(prevProps, prevState)</code> is called <strong>after every render except the first</strong> (which uses <code>componentDidMount</code>). It receives the previous props and state, letting you compare them to current values and react to specific changes.</p>

<pre><code>class UserProfile extends React.Component {
  componentDidUpdate(prevProps) {
    // React only when the user ID changes
    if (prevProps.userId !== this.props.userId) {
      this.fetchUserData(this.props.userId);
    }
  }

  fetchUserData(id) {
    fetch(`/api/users/${id}`).then(/* ... */);
  }

  render() {
    return &lt;div&gt;{/* user details */}&lt;/div&gt;;
  }
}</code></pre>

<p><strong>Common uses:</strong></p>
<ul>
  <li><strong>Refetch data when an ID prop changes</strong> &mdash; e.g., navigating between user profiles.</li>
  <li><strong>Persist state to localStorage when it changes.</strong></li>
  <li><strong>Update third-party library state</strong> based on new props.</li>
  <li><strong>Programmatic scroll or focus</strong> after the DOM updates.</li>
</ul>

<p><strong>Critical rule: ALWAYS guard with a comparison</strong> before triggering side effects. Without a guard, you create infinite loops:</p>

<pre><code>// INFINITE LOOP — setState triggers another update, which triggers this method again
componentDidUpdate() {
  this.setState({ count: this.state.count + 1 });   // BAD
}

// FIXED — only update when something specific changed
componentDidUpdate(prevProps) {
  if (prevProps.userId !== this.props.userId) {
    this.setState({ user: null });              // OK
  }
}</code></pre>

<p><strong>The third parameter</strong> &mdash; if <code>getSnapshotBeforeUpdate</code> is defined, its return value is passed as the third argument to <code>componentDidUpdate</code>. Use case: preserve scroll position across updates.</p>

<p><strong>Functional component equivalent:</strong></p>
<pre><code>useEffect(() =&gt; {
  // Runs after every render where userId changed
  fetchUserData(userId);
}, [userId]);   // only re-runs when userId changes</code></pre>

<p>The dependency array <code>[userId]</code> is automatic guarding &mdash; React only re-runs the effect when the listed dependencies change. Much cleaner than manual comparisons in classes.</p>
'''

ANSWERS[20] = r'''
<p><code>componentWillUnmount()</code> is called <strong>once, right before a component is removed from the DOM</strong>. It&rsquo;s for cleanup &mdash; removing event listeners, canceling timers, closing subscriptions, aborting fetches.</p>

<pre><code>class Clock extends React.Component {
  state = { time: new Date() };

  componentDidMount() {
    this.timerId = setInterval(() =&gt; {
      this.setState({ time: new Date() });
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.timerId);              // stop the timer
  }

  render() {
    return &lt;p&gt;{this.state.time.toLocaleTimeString()}&lt;/p&gt;;
  }
}</code></pre>

<p><strong>What needs cleanup:</strong></p>
<ul>
  <li><strong>Timers</strong>: <code>setTimeout</code>, <code>setInterval</code> &mdash; clear them.</li>
  <li><strong>Event listeners</strong> on <code>window</code> or <code>document</code> &mdash; remove them.</li>
  <li><strong>Subscriptions</strong> &mdash; unsubscribe from stores, WebSockets, RxJS observables.</li>
  <li><strong>Pending fetches</strong> &mdash; abort with <code>AbortController</code>.</li>
  <li><strong>Third-party library instances</strong> &mdash; destroy charts, maps, video players.</li>
</ul>

<pre><code>class SearchResults extends React.Component {
  componentDidMount() {
    this.controller = new AbortController();

    fetch("/api/search?q=" + this.props.query, {
      signal: this.controller.signal
    }).then(/* ... */);

    window.addEventListener("resize", this.handleResize);
  }

  componentWillUnmount() {
    this.controller.abort();                              // cancel fetch
    window.removeEventListener("resize", this.handleResize);
  }
}</code></pre>

<p><strong>Why cleanup matters:</strong></p>
<ul>
  <li><strong>Memory leaks</strong> &mdash; uncleaned listeners and timers persist after the component is gone.</li>
  <li><strong>State update warnings</strong> &mdash; "Can&rsquo;t perform a React state update on an unmounted component" usually means you forgot to cancel an async operation.</li>
  <li><strong>Performance</strong> &mdash; orphaned timers and listeners slow the page down over time.</li>
</ul>

<p><strong>Functional component equivalent</strong> &mdash; the cleanup function returned from <code>useEffect</code>:</p>
<pre><code>useEffect(() =&gt; {
  const id = setInterval(tick, 1000);

  return () =&gt; clearInterval(id);              // cleanup function
}, []);</code></pre>

<p>The cleanup runs when the component unmounts AND before each re-run of the effect. Cleaner than splitting cleanup logic between mount and unmount methods.</p>
'''

ANSWERS[21] = r'''
<p>The <code>useEffect</code> hook lets you perform <strong>side effects</strong> in functional components &mdash; data fetching, subscriptions, timers, DOM mutations, anything that&rsquo;s not part of pure rendering. It replaces the lifecycle methods of class components.</p>

<pre><code>import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() =&gt; {
    fetch(`/api/users/${userId}`)
      .then(res =&gt; res.json())
      .then(setUser);
  }, [userId]);   // dependency array

  if (!user) return &lt;div&gt;Loading...&lt;/div&gt;;
  return &lt;h1&gt;{user.name}&lt;/h1&gt;;
}</code></pre>

<p><strong>The dependency array controls when the effect runs:</strong></p>
<table>
  <tr><th>Form</th><th>Behavior</th></tr>
  <tr><td><code>useEffect(fn)</code></td><td>Runs after EVERY render</td></tr>
  <tr><td><code>useEffect(fn, [])</code></td><td>Runs ONCE after mount</td></tr>
  <tr><td><code>useEffect(fn, [a, b])</code></td><td>Runs after mount AND when <code>a</code> or <code>b</code> changes</td></tr>
</table>

<p><strong>Cleanup function</strong> &mdash; return a function from your effect; React runs it on unmount and before the next effect:</p>
<pre><code>useEffect(() =&gt; {
  const id = setInterval(() =&gt; tick(), 1000);

  return () =&gt; clearInterval(id);     // cleanup
}, []);</code></pre>

<p><strong>Common patterns:</strong></p>
<pre><code>// Fetch on mount
useEffect(() =&gt; {
  fetchData();
}, []);

// Refetch when prop changes
useEffect(() =&gt; {
  fetchData(props.id);
}, [props.id]);

// Subscribe + unsubscribe
useEffect(() =&gt; {
  const unsubscribe = store.subscribe(handleChange);
  return unsubscribe;
}, []);

// Local storage sync
useEffect(() =&gt; {
  localStorage.setItem("user", JSON.stringify(user));
}, [user]);</code></pre>

<p><strong>Common mistakes:</strong></p>
<ul>
  <li><strong>Missing dependencies</strong> &mdash; if your effect uses a variable, it must be in the dependency array. Otherwise it gets stale.</li>
  <li><strong>Object/function dependencies</strong> &mdash; created fresh each render; effect runs every time. Use <code>useMemo</code> or <code>useCallback</code> to stabilize them.</li>
  <li><strong>Forgetting cleanup</strong> &mdash; subscriptions, timers, and fetches need to be cancelled.</li>
</ul>

<p><code>useEffect</code> is the second most common hook after <code>useState</code> &mdash; you&rsquo;ll use it in nearly every component that talks to the outside world.</p>
'''

ANSWERS[22] = r'''
<p>Conditional rendering means showing different UI based on application state &mdash; loading vs loaded, logged in vs logged out, error vs success. React supports several patterns for this.</p>

<p><strong>1. <code>if</code> statement (early return):</strong></p>
<pre><code>function UserList({ users, loading, error }) {
  if (loading) return &lt;div&gt;Loading...&lt;/div&gt;;
  if (error)   return &lt;div&gt;Error: {error.message}&lt;/div&gt;;
  if (users.length === 0) return &lt;div&gt;No users found&lt;/div&gt;;

  return (
    &lt;ul&gt;
      {users.map(u =&gt; &lt;li key={u.id}&gt;{u.name}&lt;/li&gt;)}
    &lt;/ul&gt;
  );
}</code></pre>

<p>Best for distinct, mutually-exclusive states &mdash; loading / error / empty / data.</p>

<p><strong>2. Ternary operator (inline):</strong></p>
<pre><code>function Greeting({ user }) {
  return (
    &lt;div&gt;
      {user
        ? &lt;p&gt;Welcome back, {user.name}!&lt;/p&gt;
        : &lt;p&gt;Please sign in&lt;/p&gt;
      }
    &lt;/div&gt;
  );
}</code></pre>

<p>Good for two alternatives shown in the same place.</p>

<p><strong>3. Logical AND <code>&amp;&amp;</code> (show or hide):</strong></p>
<pre><code>function Notification({ message }) {
  return (
    &lt;div&gt;
      {message &amp;&amp; &lt;p className="alert"&gt;{message}&lt;/p&gt;}
    &lt;/div&gt;
  );
}</code></pre>

<p>If <code>message</code> is truthy, the JSX renders; otherwise nothing renders.</p>

<p><strong>Watch out: <code>0 &amp;&amp; ...</code></strong> renders the literal "0" because React renders numbers. Convert to boolean:</p>
<pre><code>// BAD: renders "0" when count is 0
{count &amp;&amp; &lt;p&gt;You have {count} items&lt;/p&gt;}

// GOOD
{count &gt; 0 &amp;&amp; &lt;p&gt;You have {count} items&lt;/p&gt;}
{!!count &amp;&amp; &lt;p&gt;...&lt;/p&gt;}</code></pre>

<p><strong>4. Element variables:</strong></p>
<pre><code>function Page({ user }) {
  let header;
  if (user) {
    header = &lt;UserHeader user={user} /&gt;;
  } else {
    header = &lt;GuestHeader /&gt;;
  }

  return (
    &lt;div&gt;
      {header}
      &lt;Main /&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p>Useful when the JSX is too complex for inline ternaries.</p>

<p><strong>5. Component switch / lookup table</strong>:</p>
<pre><code>const statusComponents = {
  loading: LoadingSpinner,
  error:   ErrorMessage,
  success: SuccessIcon
};

function Status({ status }) {
  const Component = statusComponents[status];
  return &lt;Component /&gt;;
}</code></pre>

<p>Pick the pattern that reads most clearly. Early returns for distinct states; ternaries for two alternatives; <code>&amp;&amp;</code> for show-or-hide.</p>
'''

ANSWERS[23] = r'''
<p>Render lists in React by mapping an array to JSX elements. Each item in the array becomes a React element &mdash; you put them all inside a parent (often a <code>&lt;ul&gt;</code> or <code>&lt;div&gt;</code>).</p>

<pre><code>function UserList({ users }) {
  return (
    &lt;ul&gt;
      {users.map(user =&gt; (
        &lt;li key={user.id}&gt;{user.name}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}

// Use:
&lt;UserList users={[
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 3, name: "Carol" }
]} /&gt;</code></pre>

<p>The <code>{users.map(...)}</code> expression returns an array of <code>&lt;li&gt;</code> elements. React renders all of them in order.</p>

<p><strong>The <code>key</code> prop is REQUIRED</strong> &mdash; React uses it to track which items changed, were added, or were removed. Without keys, React falls back to using array index, which causes bugs when lists reorder.</p>

<p><strong>Rendering complex items:</strong></p>
<pre><code>function ProductGrid({ products }) {
  return (
    &lt;div className="grid"&gt;
      {products.map(product =&gt; (
        &lt;article key={product.id} className="card"&gt;
          &lt;img src={product.image} alt={product.name} /&gt;
          &lt;h3&gt;{product.name}&lt;/h3&gt;
          &lt;p&gt;${product.price}&lt;/p&gt;
          &lt;button&gt;Add to cart&lt;/button&gt;
        &lt;/article&gt;
      ))}
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Filtering before rendering:</strong></p>
<pre><code>function ActiveUsers({ users }) {
  return (
    &lt;ul&gt;
      {users
        .filter(user =&gt; user.isActive)
        .map(user =&gt; (
          &lt;li key={user.id}&gt;{user.name}&lt;/li&gt;
        ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p><strong>Empty list state:</strong></p>
<pre><code>function TodoList({ todos }) {
  if (todos.length === 0) {
    return &lt;p&gt;No todos yet. Add one to get started!&lt;/p&gt;;
  }

  return (
    &lt;ul&gt;
      {todos.map(todo =&gt; (
        &lt;li key={todo.id}&gt;{todo.text}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p>Always handle the empty case &mdash; an empty list with no message looks broken to users.</p>

<p><strong>Extract item components</strong> when items get complex:</p>
<pre><code>function TodoItem({ todo }) {
  return &lt;li className={todo.done ? "done" : ""}&gt;{todo.text}&lt;/li&gt;;
}

function TodoList({ todos }) {
  return (
    &lt;ul&gt;
      {todos.map(t =&gt; &lt;TodoItem key={t.id} todo={t} /&gt;)}
    &lt;/ul&gt;
  );
}</code></pre>

<p>Cleaner code, reusable item rendering, easier to test.</p>
'''

ANSWERS[24] = r'''
<p>The <code>key</code> prop is a special string attribute React uses to <strong>identify which items in a list changed, were added, or were removed</strong> between renders. Without keys, React can&rsquo;t efficiently update the DOM and may produce visual bugs.</p>

<pre><code>function UserList({ users }) {
  return (
    &lt;ul&gt;
      {users.map(user =&gt; (
        &lt;li key={user.id}&gt;{user.name}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p><strong>Why keys matter:</strong> React performs DOM diffing by comparing element trees between renders. With keys, React knows "this element with key=5 is the same one as before, just maybe with new content" &mdash; and updates it in place. Without keys, React has to assume positions correspond, which breaks when items reorder.</p>

<p><strong>The right key:</strong></p>
<table>
  <tr><th>Source</th><th>Use as key</th></tr>
  <tr><td>Database records</td><td>Primary ID (e.g., <code>user.id</code>)</td></tr>
  <tr><td>External API responses</td><td>Stable ID from the API</td></tr>
  <tr><td>Generated client-side</td><td><code>crypto.randomUUID()</code> (set when item is created, not on each render)</td></tr>
  <tr><td>Combinations</td><td><code>`${userId}-${date}`</code> if the data has natural compound uniqueness</td></tr>
</table>

<p><strong>Common bug: using array index as key</strong>:</p>
<pre><code>// WORKS until the list reorders
{items.map((item, i) =&gt; &lt;li key={i}&gt;{item.text}&lt;/li&gt;)}</code></pre>

<p>If you sort, filter, or insert items, the index shifts &mdash; React thinks items changed when they didn&rsquo;t. Form input state, focus, and animations get attached to the wrong rows.</p>

<p><strong>When index keys are OK:</strong></p>
<ul>
  <li>The list never reorders.</li>
  <li>Items can&rsquo;t be added or removed in the middle.</li>
  <li>Items have no internal state.</li>
</ul>

<p>Static lists (e.g., navigation links from a hardcoded array) meet these criteria; dynamic lists usually don&rsquo;t.</p>

<p><strong>Key requirements:</strong></p>
<ul>
  <li><strong>Unique among siblings</strong> &mdash; not globally unique. Two items in different lists can both have key="1".</li>
  <li><strong>Stable across renders</strong> &mdash; the same item should always have the same key.</li>
  <li><strong>Don&rsquo;t generate keys during render</strong> &mdash; <code>Math.random()</code> in <code>map</code> creates new keys every render, defeating the purpose.</li>
</ul>

<p><strong>Common warning: "Each child in a list should have a unique 'key' prop"</strong> &mdash; React detected a list without keys; add them to fix.</p>

<p>Keys are React&rsquo;s most important performance and correctness mechanism for lists. Always provide stable, unique keys.</p>
'''

ANSWERS[25] = r'''
<p>React handles events using a synthetic event system &mdash; you attach handlers as props with camelCase names like <code>onClick</code>, <code>onChange</code>, <code>onSubmit</code>. The handler function receives a <strong>SyntheticEvent</strong>, a wrapper around the native browser event with consistent cross-browser behavior.</p>

<pre><code>function Button() {
  function handleClick(event) {
    console.log("Clicked!", event.target);
    event.preventDefault();      // works just like native events
  }

  return &lt;button onClick={handleClick}&gt;Click me&lt;/button&gt;;
}</code></pre>

<p><strong>Common event handlers:</strong></p>
<table>
  <tr><th>Event</th><th>Element</th><th>Use</th></tr>
  <tr><td><code>onClick</code></td><td>Buttons, divs, anything clickable</td><td>Click handlers</td></tr>
  <tr><td><code>onChange</code></td><td>Inputs, selects, textareas</td><td>Value changed</td></tr>
  <tr><td><code>onSubmit</code></td><td>Forms</td><td>Form submission</td></tr>
  <tr><td><code>onFocus</code> / <code>onBlur</code></td><td>Inputs</td><td>Focus changes</td></tr>
  <tr><td><code>onKeyDown</code> / <code>onKeyUp</code></td><td>Inputs, document</td><td>Keyboard input</td></tr>
  <tr><td><code>onMouseEnter</code> / <code>onMouseLeave</code></td><td>Anything</td><td>Hover detection</td></tr>
</table>

<p><strong>Inline arrow function</strong> &mdash; convenient for short handlers:</p>
<pre><code>&lt;button onClick={() =&gt; alert("Hello!")}&gt;Greet&lt;/button&gt;</code></pre>

<p><strong>Passing arguments to a handler</strong>:</p>
<pre><code>function ItemList({ items, onDelete }) {
  return (
    &lt;ul&gt;
      {items.map(item =&gt; (
        &lt;li key={item.id}&gt;
          {item.name}
          &lt;button onClick={() =&gt; onDelete(item.id)}&gt;
            Delete
          &lt;/button&gt;
        &lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p>Wrap in an arrow function to pass the item ID. The function is created on each render, but the impact is negligible for typical UIs.</p>

<p><strong>Form events</strong>:</p>
<pre><code>function LoginForm() {
  const [email, setEmail] = useState("");

  function handleSubmit(e) {
    e.preventDefault();          // stop browser from reloading the page
    fetch("/api/login", { method: "POST", body: JSON.stringify({ email }) });
  }

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input
        type="email"
        value={email}
        onChange={e =&gt; setEmail(e.target.value)}
      /&gt;
      &lt;button type="submit"&gt;Log in&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Key differences from native events:</strong></p>
<ul>
  <li><strong>camelCase names</strong>: <code>onClick</code> not <code>onclick</code>.</li>
  <li><strong>Function references</strong>, not strings: <code>onClick={handleClick}</code> not <code>onclick="handleClick()"</code>.</li>
  <li><strong>SyntheticEvent</strong> normalizes browser quirks &mdash; the same handler works identically across browsers.</li>
  <li><strong>Event delegation</strong> &mdash; React attaches one listener at the document root and dispatches to your handlers, which is why thousands of <code>onClick</code>s don&rsquo;t hurt performance.</li>
</ul>
'''

ANSWERS[26] = r'''
<p>Form inputs in React come in two flavors based on who controls their value:</p>

<table>
  <tr><th></th><th>Controlled</th><th>Uncontrolled</th></tr>
  <tr><td>Value source</td><td>React state</td><td>The DOM itself</td></tr>
  <tr><td>How you read</td><td>State variable</td><td>via <code>ref</code></td></tr>
  <tr><td>How you set</td><td><code>setState</code> / setter</td><td>Direct DOM manipulation</td></tr>
  <tr><td>Validation</td><td>On every keystroke</td><td>On submit only (typically)</td></tr>
  <tr><td>React preference</td><td>Recommended</td><td>For specific use cases</td></tr>
</table>

<p><strong>Controlled component</strong>:</p>
<pre><code>function Form() {
  const [name, setName] = useState("");

  return (
    &lt;input
      value={name}                              // React owns the value
      onChange={e =&gt; setName(e.target.value)}    // every keystroke updates state
    /&gt;
  );
}</code></pre>

<p>Every keystroke fires <code>onChange</code>, updates state, re-renders, and the input shows the new value &mdash; from React. The DOM input is just a display.</p>

<p><strong>Uncontrolled component</strong>:</p>
<pre><code>function Form() {
  const inputRef = useRef(null);

  function handleSubmit() {
    console.log(inputRef.current.value);     // read from DOM directly
  }

  return (
    &lt;&gt;
      &lt;input ref={inputRef} defaultValue="hello" /&gt;
      &lt;button onClick={handleSubmit}&gt;Submit&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>The DOM input owns its value. React only reads it when needed (on submit). Note <code>defaultValue</code> instead of <code>value</code> for the initial value.</p>

<p><strong>When to use each:</strong></p>
<table>
  <tr><th>Scenario</th><th>Best</th></tr>
  <tr><td>Form with live validation</td><td>Controlled</td></tr>
  <tr><td>Search/filter as user types</td><td>Controlled</td></tr>
  <tr><td>Conditional fields based on input</td><td>Controlled</td></tr>
  <tr><td>Simple form, validate on submit only</td><td>Either</td></tr>
  <tr><td>File inputs (<code>&lt;input type="file"&gt;</code>)</td><td>Uncontrolled (always)</td></tr>
  <tr><td>Integration with non-React form libraries</td><td>Uncontrolled</td></tr>
  <tr><td>Performance: huge forms with hundreds of fields</td><td>Uncontrolled (less re-rendering)</td></tr>
</table>

<p><strong>Default recommendation</strong>: controlled. The benefit of having form data in React state &mdash; for validation, conditional UI, and submission &mdash; outweighs the small overhead. Reach for uncontrolled when you specifically don&rsquo;t need React to track the value.</p>

<p>Modern forms often use libraries like React Hook Form or Formik that combine the best of both: uncontrolled internally for performance, with hooks that give you controlled-like access for validation.</p>
'''

ANSWERS[27] = r'''
<p>A controlled component is a form input whose value is owned by React state. The state is the "single source of truth" &mdash; the input always shows what state says, and every keystroke updates state.</p>

<pre><code>import { useState } from "react";

function NameForm() {
  const [name, setName] = useState("");

  return (
    &lt;form&gt;
      &lt;label&gt;
        Name:
        &lt;input
          type="text"
          value={name}                              // value comes from state
          onChange={e =&gt; setName(e.target.value)}    // updates state
        /&gt;
      &lt;/label&gt;
      &lt;p&gt;You typed: {name}&lt;/p&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>The two-way binding pattern</strong> requires two pieces:</p>
<ul>
  <li><strong><code>value={name}</code></strong> &mdash; tells React: display whatever <code>name</code> says.</li>
  <li><strong><code>onChange={e =&gt; setName(e.target.value)}</code></strong> &mdash; tells React: when user types, update state with the new value.</li>
</ul>

<p>Skipping either breaks the input. <code>value</code> without <code>onChange</code> = read-only input. <code>onChange</code> without <code>value</code> = uncontrolled.</p>

<p><strong>Multiple inputs &mdash; one state object:</strong></p>
<pre><code>function SignupForm() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    age: ""
  });

  function handleChange(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value      // dynamic key from input name
    });
  }

  return (
    &lt;form&gt;
      &lt;input name="name"  value={form.name}  onChange={handleChange} /&gt;
      &lt;input name="email" value={form.email} onChange={handleChange} /&gt;
      &lt;input name="age"   value={form.age}   onChange={handleChange} /&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p>The <code>[e.target.name]: e.target.value</code> uses the input&rsquo;s <code>name</code> attribute to update the right field generically &mdash; one handler for any number of inputs.</p>

<p><strong>Different input types:</strong></p>
<pre><code>// Checkbox
&lt;input
  type="checkbox"
  checked={isAgree}                       // 'checked', not 'value'
  onChange={e =&gt; setIsAgree(e.target.checked)}
/&gt;

// Select
&lt;select value={size} onChange={e =&gt; setSize(e.target.value)}&gt;
  &lt;option value="small"&gt;Small&lt;/option&gt;
  &lt;option value="large"&gt;Large&lt;/option&gt;
&lt;/select&gt;

// Textarea
&lt;textarea value={message} onChange={e =&gt; setMessage(e.target.value)} /&gt;</code></pre>

<p><strong>Benefits of controlled inputs:</strong></p>
<ul>
  <li><strong>Live validation</strong> &mdash; check format/length on every keystroke.</li>
  <li><strong>Conditional rendering</strong> &mdash; show fields based on what&rsquo;s entered.</li>
  <li><strong>Format on input</strong> &mdash; force uppercase, mask phone numbers, restrict to digits.</li>
  <li><strong>Submission state</strong> &mdash; data is already in React, ready to send.</li>
</ul>
'''

ANSWERS[28] = r'''
<p>An uncontrolled component lets the DOM hold the input&rsquo;s value &mdash; React doesn&rsquo;t track it on every keystroke. You read the value when you need it, typically on form submission, using a ref.</p>

<pre><code>import { useRef } from "react";

function NameForm() {
  const inputRef = useRef(null);

  function handleSubmit(e) {
    e.preventDefault();
    alert("Name: " + inputRef.current.value);
  }

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input
        type="text"
        ref={inputRef}
        defaultValue="Alice"               // initial value (NOT 'value')
      /&gt;
      &lt;button type="submit"&gt;Submit&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Key differences from controlled:</strong></p>
<ul>
  <li><strong><code>defaultValue</code> instead of <code>value</code></strong> for initial value &mdash; sets the starting state but doesn&rsquo;t lock the input.</li>
  <li><strong>No <code>onChange</code> needed</strong> for tracking &mdash; the DOM tracks itself.</li>
  <li><strong>Read via <code>ref.current.value</code></strong> when needed.</li>
</ul>

<p><strong>Multiple uncontrolled inputs:</strong></p>
<pre><code>function SignupForm() {
  const formRef = useRef(null);

  function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(formRef.current);
    const data = Object.fromEntries(formData);
    console.log(data);   // { name: "...", email: "...", password: "..." }
  }

  return (
    &lt;form ref={formRef} onSubmit={handleSubmit}&gt;
      &lt;input name="name"     defaultValue="" /&gt;
      &lt;input name="email"    type="email" /&gt;
      &lt;input name="password" type="password" /&gt;
      &lt;button type="submit"&gt;Sign up&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p>Using <code>FormData</code> on the form element grabs all named inputs at once &mdash; no per-input refs needed.</p>

<p><strong>File inputs are ALWAYS uncontrolled</strong> &mdash; you can&rsquo;t set a file&rsquo;s value programmatically (browser security):</p>

<pre><code>function FileUpload() {
  const fileRef = useRef(null);

  function handleSubmit(e) {
    e.preventDefault();
    const file = fileRef.current.files[0];
    console.log("Uploading:", file.name);
  }

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input type="file" ref={fileRef} /&gt;
      &lt;button&gt;Upload&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>When uncontrolled is the right choice:</strong></p>
<ul>
  <li><strong>Simple forms</strong> with no live validation needs.</li>
  <li><strong>File inputs</strong> &mdash; required.</li>
  <li><strong>Integrating with non-React libraries</strong> that manage their own DOM.</li>
  <li><strong>Performance</strong> &mdash; huge forms (100+ fields) where re-rendering on every keystroke is wasteful.</li>
</ul>

<p>For most React forms, controlled is the better default. Uncontrolled has its place but isn&rsquo;t the modern standard.</p>
'''

ANSWERS[29] = r'''
<p>The <code>ref</code> attribute lets you access a DOM node directly from React, escaping the usual declarative model. Refs are the way to do imperative things React doesn&rsquo;t handle declaratively: focusing inputs, measuring elements, integrating with non-React libraries.</p>

<pre><code>import { useRef } from "react";

function FocusableInput() {
  const inputRef = useRef(null);

  function handleFocus() {
    inputRef.current.focus();        // imperative DOM call
  }

  return (
    &lt;&gt;
      &lt;input ref={inputRef} type="text" /&gt;
      &lt;button onClick={handleFocus}&gt;Focus the input&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Common use cases:</strong></p>
<ul>
  <li><strong>Focus, text selection, or media playback</strong> &mdash; <code>input.focus()</code>, <code>video.play()</code>.</li>
  <li><strong>Triggering animations</strong> imperatively (e.g., shake animation on validation error).</li>
  <li><strong>Integrating with third-party libraries</strong> that need a DOM node (Chart.js, mapbox, video players).</li>
  <li><strong>Scrolling to elements</strong> programmatically.</li>
  <li><strong>Measuring DOM</strong> &mdash; <code>getBoundingClientRect()</code> for size or position.</li>
  <li><strong>Storing mutable values that don&rsquo;t trigger re-renders</strong> &mdash; like timer IDs.</li>
</ul>

<pre><code>function ScrollToTop() {
  const topRef = useRef(null);

  function scrollUp() {
    topRef.current.scrollIntoView({ behavior: "smooth" });
  }

  return (
    &lt;div&gt;
      &lt;div ref={topRef}&gt;Top of page&lt;/div&gt;
      {/* ... lots of content ... */}
      &lt;button onClick={scrollUp}&gt;Back to top&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Two types of refs:</strong></p>
<table>
  <tr><th>Type</th><th>Created with</th><th>What it holds</th></tr>
  <tr><td>DOM ref</td><td><code>useRef(null)</code></td><td>Reference to a DOM element</td></tr>
  <tr><td>Mutable value ref</td><td><code>useRef(initialValue)</code></td><td>Mutable value; doesn&rsquo;t trigger re-renders when changed</td></tr>
</table>

<p><strong>Mutable value example:</strong></p>
<pre><code>function Timer() {
  const intervalIdRef = useRef(null);
  const [time, setTime] = useState(0);

  function start() {
    intervalIdRef.current = setInterval(() =&gt; setTime(t =&gt; t + 1), 1000);
  }

  function stop() {
    clearInterval(intervalIdRef.current);
  }

  return &lt;button onClick={start}&gt;Start ({time}s)&lt;/button&gt;;
}</code></pre>

<p>The interval ID is stored on the ref &mdash; mutating <code>ref.current</code> doesn&rsquo;t cause a re-render, which is exactly what we want.</p>

<p><strong>Important rules:</strong></p>
<ul>
  <li><strong>Only access <code>ref.current</code> after mounting</strong> &mdash; in event handlers, <code>useEffect</code>, etc.</li>
  <li><strong>Don&rsquo;t use refs to manage data that should be state</strong> &mdash; if a value affects what&rsquo;s rendered, it should be state.</li>
  <li><strong>Refs escape React&rsquo;s declarative model</strong> &mdash; reach for them only when nothing else fits.</li>
</ul>
'''

ANSWERS[30] = r'''
<p>You create a ref with the <code>useRef</code> hook and attach it to a JSX element via the <code>ref</code> attribute. Read or write the underlying value through <code>ref.current</code>.</p>

<pre><code>import { useRef, useEffect } from "react";

function AutoFocus() {
  const inputRef = useRef(null);     // initial value: null

  useEffect(() =&gt; {
    inputRef.current.focus();        // focus on mount
  }, []);

  return &lt;input ref={inputRef} type="text" /&gt;;
}</code></pre>

<p><strong>The pattern:</strong></p>
<ol>
  <li><strong>Create the ref</strong> with <code>useRef(initialValue)</code>.</li>
  <li><strong>Attach to a JSX element</strong> with <code>ref={refName}</code>.</li>
  <li><strong>Access via <code>refName.current</code></strong> after the component mounts.</li>
</ol>

<p><strong>Multiple refs in one component:</strong></p>
<pre><code>function MultiInputForm() {
  const nameRef = useRef(null);
  const emailRef = useRef(null);
  const submitRef = useRef(null);

  function focusNext(currentRef, nextRef) {
    return (e) =&gt; {
      if (e.key === "Enter") {
        e.preventDefault();
        nextRef.current.focus();
      }
    };
  }

  return (
    &lt;form&gt;
      &lt;input ref={nameRef}   placeholder="Name"  onKeyDown={focusNext(nameRef, emailRef)} /&gt;
      &lt;input ref={emailRef}  placeholder="Email" onKeyDown={focusNext(emailRef, submitRef)} /&gt;
      &lt;button ref={submitRef}&gt;Submit&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Refs on custom components</strong> &mdash; need <code>forwardRef</code> (pre-React 19) or just work directly (React 19+):</p>
<pre><code>// React 19+ — refs work on custom components automatically
function MyInput({ label, ref, ...props }) {
  return (
    &lt;label&gt;
      {label}
      &lt;input ref={ref} {...props} /&gt;
    &lt;/label&gt;
  );
}

function Parent() {
  const ref = useRef(null);
  return &lt;MyInput label="Name" ref={ref} /&gt;;
}</code></pre>

<p>In React 18 and earlier, you needed <code>forwardRef</code> to make refs pass through custom components &mdash; the modern API treats <code>ref</code> as a regular prop.</p>

<p><strong>Class component refs</strong> &mdash; create with <code>React.createRef()</code>:</p>
<pre><code>class TextInput extends React.Component {
  inputRef = React.createRef();

  componentDidMount() {
    this.inputRef.current.focus();
  }

  render() {
    return &lt;input ref={this.inputRef} /&gt;;
  }
}</code></pre>

<p><strong>Common gotcha &mdash; refs are <code>null</code> on first render</strong>:</p>
<pre><code>function Component() {
  const ref = useRef(null);

  // BAD: ref is null on first render!
  console.log(ref.current);   // null

  useEffect(() =&gt; {
    // GOOD: ref is set after mount
    console.log(ref.current);   // &lt;input&gt;
  }, []);

  return &lt;input ref={ref} /&gt;;
}</code></pre>

<p>The DOM doesn&rsquo;t exist until after React renders. Always access <code>ref.current</code> in event handlers or effects, not directly during render.</p>
'''

ANSWERS[31] = r'''
<p>The Context API lets you <strong>share data across components without passing props through every level</strong>. It solves "prop drilling" &mdash; the awkwardness of passing data through 5+ intermediate components that don&rsquo;t use it themselves.</p>

<pre><code>// Without Context — prop drilling
function App() {
  const user = { name: "Alice" };
  return &lt;Layout user={user} /&gt;;
}

function Layout({ user }) {
  return &lt;Header user={user} /&gt;;
}

function Header({ user }) {
  return &lt;UserMenu user={user} /&gt;;
}

function UserMenu({ user }) {
  return &lt;span&gt;Hi, {user.name}&lt;/span&gt;;       // finally uses it
}</code></pre>

<p><strong>With Context</strong> &mdash; data jumps directly from provider to consumer:</p>
<pre><code>const UserContext = createContext(null);

function App() {
  const user = { name: "Alice" };
  return (
    &lt;UserContext.Provider value={user}&gt;
      &lt;Layout /&gt;       {/* no user prop needed */}
    &lt;/UserContext.Provider&gt;
  );
}

function UserMenu() {
  const user = useContext(UserContext);     // read directly
  return &lt;span&gt;Hi, {user.name}&lt;/span&gt;;
}</code></pre>

<p>Layout and Header don&rsquo;t need to know about <code>user</code> &mdash; they just render their children.</p>

<p><strong>Common use cases:</strong></p>
<ul>
  <li><strong>Theme</strong> &mdash; light/dark mode toggle accessible everywhere.</li>
  <li><strong>Authenticated user</strong> &mdash; current user available to any component.</li>
  <li><strong>Locale / language</strong> &mdash; for translations.</li>
  <li><strong>Feature flags</strong> &mdash; enable/disable UI features.</li>
  <li><strong>Modal/toast managers</strong> &mdash; trigger UI from any component.</li>
</ul>

<p><strong>When NOT to use Context:</strong></p>
<ul>
  <li><strong>Frequently-changing values</strong> &mdash; every consumer re-renders when context value changes; can hurt performance.</li>
  <li><strong>Component-specific data</strong> &mdash; props are still better when data is only needed by direct children.</li>
  <li><strong>Complex state with many updates</strong> &mdash; reach for Redux, Zustand, or Jotai instead.</li>
</ul>

<p><strong>Context is best for "global but stable" data</strong> &mdash; values that change rarely (theme, locale) or that almost every component needs (current user).</p>

<p>For application-wide state with frequent updates, dedicated state managers (Redux, Zustand, MobX) handle performance better than vanilla Context.</p>
'''

ANSWERS[32] = r'''
<p>You create a context with <code>createContext()</code>, optionally passing a default value used when a consumer has no matching Provider above it.</p>

<pre><code>import { createContext } from "react";

// Create the context
const ThemeContext = createContext("light");

// Optional: export so other files can use it
export { ThemeContext };</code></pre>

<p><strong>The default value</strong> is used only when a consumer is rendered without any matching Provider. It&rsquo;s mostly useful for:</p>
<ul>
  <li><strong>Testing</strong> components in isolation without setting up a Provider.</li>
  <li><strong>Avoiding errors</strong> if someone forgets to add the Provider.</li>
  <li><strong>Sensible fallback</strong> behavior.</li>
</ul>

<p><strong>Setting up the Provider</strong> &mdash; usually high in the component tree:</p>

<pre><code>import { ThemeContext } from "./ThemeContext";

function App() {
  const [theme, setTheme] = useState("light");

  return (
    &lt;ThemeContext.Provider value={theme}&gt;
      &lt;Layout&gt;
        &lt;Toolbar /&gt;
        &lt;MainContent /&gt;
      &lt;/Layout&gt;
      &lt;button onClick={() =&gt; setTheme(theme === "light" ? "dark" : "light")}&gt;
        Toggle theme
      &lt;/button&gt;
    &lt;/ThemeContext.Provider&gt;
  );
}</code></pre>

<p>Everything inside <code>&lt;ThemeContext.Provider&gt;</code> can access <code>theme</code> via <code>useContext(ThemeContext)</code>.</p>

<p><strong>Sharing both value AND setter</strong> &mdash; pass an object:</p>
<pre><code>const ThemeContext = createContext({
  theme: "light",
  setTheme: () =&gt; {}      // default no-op for fallback
});

function App() {
  const [theme, setTheme] = useState("light");

  return (
    &lt;ThemeContext.Provider value={{ theme, setTheme }}&gt;
      &lt;Toolbar /&gt;
    &lt;/ThemeContext.Provider&gt;
  );
}

function Toolbar() {
  const { theme, setTheme } = useContext(ThemeContext);
  return (
    &lt;button onClick={() =&gt; setTheme(theme === "light" ? "dark" : "light")}&gt;
      Current: {theme}
    &lt;/button&gt;
  );
}</code></pre>

<p><strong>Custom Provider component pattern</strong> &mdash; encapsulates state and exposes a clean API:</p>

<pre><code>function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");

  function toggleTheme() {
    setTheme(prev =&gt; prev === "light" ? "dark" : "light");
  }

  return (
    &lt;ThemeContext.Provider value={{ theme, toggleTheme }}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

// Usage
&lt;ThemeProvider&gt;
  &lt;App /&gt;
&lt;/ThemeProvider&gt;</code></pre>

<p>This is the standard pattern in modern React &mdash; the provider component owns the state, exposes setter helpers, and wraps the app.</p>

<p><strong>Multiple contexts</strong> &mdash; nest providers as needed:</p>
<pre><code>&lt;ThemeProvider&gt;
  &lt;UserProvider&gt;
    &lt;LocaleProvider&gt;
      &lt;App /&gt;
    &lt;/LocaleProvider&gt;
  &lt;/UserProvider&gt;
&lt;/ThemeProvider&gt;</code></pre>

<p>Common in real apps. For 4-5+ providers, extract a <code>&lt;Providers&gt;</code> component to keep the tree clean.</p>
'''

ANSWERS[33] = r'''
<p>To use a context, consume it from any descendant of the matching Provider with the <code>useContext</code> hook (in functional components) or the <code>Context.Consumer</code> render prop (in class components).</p>

<p><strong>Modern: <code>useContext</code> hook</strong> &mdash; the standard way:</p>

<pre><code>import { useContext } from "react";
import { ThemeContext } from "./ThemeContext";

function ThemedButton() {
  const theme = useContext(ThemeContext);

  return (
    &lt;button className={`btn-${theme}`}&gt;
      Click me
    &lt;/button&gt;
  );
}</code></pre>

<p><code>useContext</code> reads the closest Provider above this component in the tree. If <code>theme</code> is "dark", the button gets class "btn-dark".</p>

<p><strong>If the value is an object with multiple fields</strong>, destructure:</p>
<pre><code>function Toolbar() {
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    &lt;button onClick={toggleTheme}&gt;
      Current theme: {theme}
    &lt;/button&gt;
  );
}</code></pre>

<p><strong>Custom hook pattern</strong> &mdash; wrap <code>useContext</code> for safety and ergonomics:</p>
<pre><code>// In ThemeContext.js
function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used inside ThemeProvider");
  }
  return ctx;
}

// In components
function App() {
  const { theme, toggleTheme } = useTheme();      // safer, cleaner
  // ...
}</code></pre>

<p>The custom hook adds a clear error if someone forgets to add the Provider &mdash; far better than getting a confusing <code>undefined</code> error later.</p>

<p><strong>Class components: <code>static contextType</code> or <code>Consumer</code>:</strong></p>
<pre><code>class ThemedButton extends React.Component {
  static contextType = ThemeContext;     // single context only

  render() {
    const theme = this.context;
    return &lt;button className={`btn-${theme}`}&gt;...&lt;/button&gt;;
  }
}

// Render prop pattern (works for multiple contexts)
class ThemedButton extends React.Component {
  render() {
    return (
      &lt;ThemeContext.Consumer&gt;
        {theme =&gt; &lt;button className={`btn-${theme}`}&gt;...&lt;/button&gt;}
      &lt;/ThemeContext.Consumer&gt;
    );
  }
}</code></pre>

<p>Modern apps use <code>useContext</code> exclusively &mdash; classes only show up in legacy code.</p>

<p><strong>Important behaviors:</strong></p>
<ul>
  <li><strong>Re-renders on value change</strong> &mdash; every component using <code>useContext</code> re-renders when the Provider&rsquo;s <code>value</code> changes (by reference).</li>
  <li><strong>Walks up the tree</strong> &mdash; finds the nearest matching Provider; defaults if none found.</li>
  <li><strong>One Provider value</strong> &mdash; all consumers see the same value.</li>
</ul>

<p><strong>Performance gotcha</strong>: passing <code>value={{ x, y }}</code> creates a new object every render, triggering all consumers. For frequently-changing values, memoize:</p>
<pre><code>const value = useMemo(() =&gt; ({ x, y }), [x, y]);
&lt;Context.Provider value={value}&gt;...&lt;/Context.Provider&gt;</code></pre>
'''

ANSWERS[34] = r'''
<p>The <code>useContext</code> hook is the modern way to read a context value in functional components. It replaces the older <code>Context.Consumer</code> render prop and the class-based <code>static contextType</code>.</p>

<pre><code>import { useContext } from "react";
import { ThemeContext } from "./ThemeContext";

function MyComponent() {
  const theme = useContext(ThemeContext);
  return &lt;div className={`bg-${theme}`}&gt;Hello&lt;/div&gt;;
}</code></pre>

<p><strong>What it does:</strong></p>
<ul>
  <li>Walks up the component tree.</li>
  <li>Finds the nearest <code>&lt;ThemeContext.Provider&gt;</code>.</li>
  <li>Returns its current <code>value</code> prop.</li>
  <li>Re-renders this component whenever that value changes.</li>
</ul>

<p>If no Provider is found, <code>useContext</code> returns the default value passed to <code>createContext()</code>.</p>

<p><strong>Common pattern: custom hook wrapper</strong>:</p>
<pre><code>// ThemeProvider.jsx
import { createContext, useContext, useState } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");
  const value = { theme, setTheme };

  return (
    &lt;ThemeContext.Provider value={value}&gt;
      {children}
    &lt;/ThemeContext.Provider&gt;
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used inside ThemeProvider");
  return ctx;
}</code></pre>

<p>Now consumers don&rsquo;t need to import the context object &mdash; just the hook:</p>
<pre><code>import { useTheme } from "./ThemeProvider";

function Toolbar() {
  const { theme, setTheme } = useTheme();
  return (
    &lt;button onClick={() =&gt; setTheme(theme === "light" ? "dark" : "light")}&gt;
      {theme}
    &lt;/button&gt;
  );
}</code></pre>

<p><strong>Multiple contexts in one component:</strong></p>
<pre><code>function UserProfile() {
  const { theme } = useTheme();
  const user = useContext(UserContext);
  const { locale } = useContext(LocaleContext);

  return (
    &lt;div className={`bg-${theme}`}&gt;
      {translate("greeting", locale)}, {user.name}
    &lt;/div&gt;
  );
}</code></pre>

<p>Call <code>useContext</code> as many times as needed &mdash; once per context.</p>

<p><strong>Performance note</strong>: every component using <code>useContext</code> re-renders when the Provider&rsquo;s value changes &mdash; even if it doesn&rsquo;t use the part that changed. To avoid unnecessary re-renders for frequently-changing context:</p>

<ul>
  <li><strong>Split the context</strong> &mdash; one for stable values (user info), one for changing ones (settings).</li>
  <li><strong>Memoize the value</strong> with <code>useMemo</code> so reference identity is stable.</li>
  <li><strong>Use <code>React.memo</code></strong> on consumers that should skip re-renders when their inputs don&rsquo;t change.</li>
</ul>

<p>For complex state with many updates, consider a state manager (Zustand, Redux Toolkit) instead of Context.</p>
'''

ANSWERS[35] = r'''
<p><strong>React Fragments</strong> let you group multiple elements without adding an extra DOM node. Useful when a component must return multiple siblings &mdash; React requires a single root, but you don&rsquo;t always want a wrapping <code>&lt;div&gt;</code>.</p>

<pre><code>// WITHOUT fragments — extra div in the DOM
function Header() {
  return (
    &lt;div&gt;
      &lt;h1&gt;Title&lt;/h1&gt;
      &lt;p&gt;Subtitle&lt;/p&gt;
    &lt;/div&gt;
  );
}

// WITH fragments — no extra DOM
function Header() {
  return (
    &lt;&gt;
      &lt;h1&gt;Title&lt;/h1&gt;
      &lt;p&gt;Subtitle&lt;/p&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>The output renders <code>&lt;h1&gt;</code> and <code>&lt;p&gt;</code> directly into the parent, with no wrapping element.</p>

<p><strong>Two ways to write fragments:</strong></p>

<table>
  <tr><th>Syntax</th><th>Use when</th></tr>
  <tr><td><code>&lt;&gt;...&lt;/&gt;</code> (short)</td><td>Most cases &mdash; concise, readable</td></tr>
  <tr><td><code>&lt;Fragment&gt;...&lt;/Fragment&gt;</code></td><td>You need to add a key (e.g., in a list)</td></tr>
</table>

<pre><code>import { Fragment } from "react";

function Glossary({ entries }) {
  return (
    &lt;dl&gt;
      {entries.map(entry =&gt; (
        &lt;Fragment key={entry.id}&gt;
          &lt;dt&gt;{entry.term}&lt;/dt&gt;
          &lt;dd&gt;{entry.definition}&lt;/dd&gt;
        &lt;/Fragment&gt;
      ))}
    &lt;/dl&gt;
  );
}</code></pre>

<p>Each iteration produces a <code>&lt;dt&gt;</code> + <code>&lt;dd&gt;</code> pair without a wrapping element &mdash; the <code>&lt;dl&gt;</code> contains them as direct children. The short syntax <code>&lt;&gt;...&lt;/&gt;</code> doesn&rsquo;t accept props like <code>key</code>, so use the long form for keyed fragments.</p>

<p><strong>Why fragments matter:</strong></p>

<p><strong>1. Cleaner DOM</strong> &mdash; less nesting, easier to style with CSS Grid/Flexbox:</p>
<pre><code>// Without fragments — div breaks grid layout
&lt;div className="grid"&gt;
  &lt;div&gt;            {/* unnecessary wrapper */}
    &lt;div&gt;cell 1&lt;/div&gt;
    &lt;div&gt;cell 2&lt;/div&gt;
  &lt;/div&gt;
&lt;/div&gt;

// With fragments — cells are direct grid children
&lt;div className="grid"&gt;
  &lt;CellPair /&gt;     {/* renders &lt;div&gt; cell 1, &lt;div&gt; cell 2 */}
&lt;/div&gt;</code></pre>

<p><strong>2. Table layout integrity</strong> &mdash; HTML tables are strict about structure; you can&rsquo;t put a <code>&lt;div&gt;</code> inside <code>&lt;tr&gt;</code>:</p>
<pre><code>function TableRow({ name, age }) {
  return (
    &lt;&gt;
      &lt;td&gt;{name}&lt;/td&gt;
      &lt;td&gt;{age}&lt;/td&gt;
    &lt;/&gt;
  );
}

&lt;tr&gt;&lt;TableRow name="Alice" age={30} /&gt;&lt;/tr&gt;</code></pre>

<p><strong>3. Component composition</strong> &mdash; sometimes a component logically returns multiple things at the same level:</p>
<pre><code>function Modal() {
  return (
    &lt;&gt;
      &lt;div className="overlay" /&gt;
      &lt;div className="modal-content"&gt;...&lt;/div&gt;
    &lt;/&gt;
  );
}</code></pre>

<p>Fragments don&rsquo;t render anything visible &mdash; they&rsquo;re purely a React-side mechanism. Inspect the DOM in DevTools and you&rsquo;ll see only the children, no fragment marker.</p>

<p><strong>Modern React preference</strong>: use fragments when wrapping is unnecessary. Reach for a <code>&lt;div&gt;</code> only when you actually need to style or query the wrapper itself.</p>
'''

ANSWERS[36] = r'''
<p>Forms in React use <strong>controlled components</strong> &mdash; React state holds the input value, and an <code>onChange</code> handler updates it on each keystroke. The state is the single source of truth.</p>

<pre><code>function ContactForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const handleSubmit = (e) =&gt; {
    e.preventDefault();
    console.log({ name, email });
    // submit to backend...
  };

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input
        value={name}
        onChange={e =&gt; setName(e.target.value)}
        placeholder="Name"
      /&gt;
      &lt;input
        type="email"
        value={email}
        onChange={e =&gt; setEmail(e.target.value)}
        placeholder="Email"
      /&gt;
      &lt;button type="submit"&gt;Send&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>For larger forms,</strong> a single state object is cleaner:</p>

<pre><code>const [form, setForm] = useState({ name: "", email: "" });

const handleChange = (e) =&gt;
  setForm({ ...form, [e.target.name]: e.target.value });

&lt;input name="name" value={form.name} onChange={handleChange} /&gt;</code></pre>

<p><strong>For complex forms</strong> (validation, errors, dirty tracking, arrays), libraries like <strong>React Hook Form</strong> or <strong>Formik</strong> handle the boilerplate. React 19 also introduced the new <code>useActionState</code> and <code>useFormStatus</code> hooks specifically for form handling with Server Actions &mdash; simpler patterns for forms that submit to a backend.</p>
'''

ANSWERS[37] = r'''
<p><code>useReducer</code> is an alternative to <code>useState</code> for managing <strong>complex state</strong> &mdash; especially when state has multiple sub-values, or when the next state depends on the previous one. It mirrors Redux&rsquo;s reducer pattern at the component level.</p>

<pre><code>import { useReducer } from "react";

function reducer(state, action) {
  switch (action.type) {
    case "INCREMENT": return { count: state.count + 1 };
    case "DECREMENT": return { count: state.count - 1 };
    case "RESET":     return { count: 0 };
    default: return state;
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0 });

  return (
    &lt;&gt;
      &lt;p&gt;Count: {state.count}&lt;/p&gt;
      &lt;button onClick={() =&gt; dispatch({ type: "INCREMENT" })}&gt;+&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch({ type: "DECREMENT" })}&gt;-&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch({ type: "RESET" })}&gt;Reset&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>useState vs useReducer:</strong></p>

<table>
  <tr><th>Use useState</th><th>Use useReducer</th></tr>
  <tr><td>Simple values (string, number, boolean)</td><td>Complex objects with multiple fields</td></tr>
  <tr><td>Independent updates</td><td>Updates that depend on each other</td></tr>
  <tr><td>Component-local state</td><td>State logic shared across components</td></tr>
  <tr><td>Easy to test inline</td><td>Testable as pure reducer function</td></tr>
</table>

<p><strong>Benefits</strong>: predictable updates (one reducer handles all transitions), easier to debug (log dispatched actions), and the reducer is a pure function you can unit test in isolation. For shopping carts, multi-step forms, and undo/redo, <code>useReducer</code> is usually clearer than juggling several <code>useState</code> calls.</p>
'''

ANSWERS[38] = r'''
<p>Side effects in functional components are handled by the <code>useEffect</code> hook &mdash; it runs after render and is the place for: data fetching, subscriptions, timers, DOM manipulation, and logging. Anything that touches the world outside React goes here.</p>

<pre><code>import { useState, useEffect } from "react";

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() =&gt; {
    fetch(`/api/users/${userId}`)
      .then(res =&gt; res.json())
      .then(setUser);
  }, [userId]);   // re-runs when userId changes

  if (!user) return &lt;p&gt;Loading...&lt;/p&gt;;
  return &lt;h1&gt;{user.name}&lt;/h1&gt;;
}</code></pre>

<p><strong>The dependency array</strong> controls when the effect runs:</p>

<table>
  <tr><th>Dependency array</th><th>Effect runs</th></tr>
  <tr><td><code>[]</code> empty</td><td>Once after first render (mount)</td></tr>
  <tr><td><code>[userId]</code></td><td>After mount, and whenever userId changes</td></tr>
  <tr><td>Omitted (no array)</td><td>After every single render &mdash; rarely what you want</td></tr>
</table>

<p><strong>Cleanup</strong> &mdash; return a function to clean up subscriptions or timers:</p>

<pre><code>useEffect(() =&gt; {
  const id = setInterval(() =&gt; console.log("tick"), 1000);
  return () =&gt; clearInterval(id);   // cleanup runs on unmount or before next effect
}, []);</code></pre>

<p><strong>Modern alternative for data fetching</strong>: in 2026, libraries like TanStack Query, SWR, or React Server Components handle most data-fetching better than raw <code>useEffect</code> &mdash; with built-in caching, deduplication, and revalidation. Reach for <code>useEffect</code> for non-data side effects (subscriptions, browser APIs, manual DOM access).</p>
'''

ANSWERS[39] = r'''
<p>API data fetching in React typically uses <code>useEffect</code> + <code>fetch</code> (or <code>axios</code>) for simple cases &mdash; though modern apps prefer dedicated data libraries.</p>

<p><strong>Basic pattern with useEffect:</strong></p>

<pre><code>import { useState, useEffect } from "react";

function Posts() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() =&gt; {
    let cancelled = false;

    async function load() {
      try {
        const res = await fetch("/api/posts");
        if (!res.ok) throw new Error("Failed to load");
        const data = await res.json();
        if (!cancelled) setPosts(data);
      } catch (e) {
        if (!cancelled) setError(e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () =&gt; { cancelled = true; };   // prevent state update after unmount
  }, []);

  if (loading) return &lt;p&gt;Loading...&lt;/p&gt;;
  if (error)   return &lt;p&gt;Error: {error}&lt;/p&gt;;

  return (
    &lt;ul&gt;
      {posts.map(p =&gt; &lt;li key={p.id}&gt;{p.title}&lt;/li&gt;)}
    &lt;/ul&gt;
  );
}</code></pre>

<p><strong>The pattern always has three states</strong>: loading, error, success. The <code>cancelled</code> flag prevents state updates if the component unmounts mid-fetch.</p>

<p><strong>Modern preferred approach &mdash; TanStack Query:</strong></p>

<pre><code>import { useQuery } from "@tanstack/react-query";

function Posts() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["posts"],
    queryFn: () =&gt; fetch("/api/posts").then(r =&gt; r.json())
  });

  if (isLoading) return &lt;p&gt;Loading...&lt;/p&gt;;
  if (error)     return &lt;p&gt;Error&lt;/p&gt;;

  return &lt;ul&gt;{data.map(p =&gt; &lt;li key={p.id}&gt;{p.title}&lt;/li&gt;)}&lt;/ul&gt;;
}</code></pre>

<p>TanStack Query handles caching, refetching, request deduplication, retries, and pagination &mdash; replacing 50+ lines of manual <code>useEffect</code> code. In 2026 it&rsquo;s the standard for client-side data fetching.</p>

<p><strong>React 19&rsquo;s <code>use()</code> hook</strong> reads promises directly (with Suspense), eliminating effect entirely for many cases.</p>
'''

ANSWERS[40] = r'''
<p>(Same topic as Q39 &mdash; the question split across two entries in the source. See Q39 for the full data-fetching answer.)</p>

<p><strong>Quick summary of the data-fetching landscape in React (2026):</strong></p>

<table>
  <tr><th>Approach</th><th>When to use</th></tr>
  <tr><td><code>useEffect</code> + <code>fetch</code></td><td>Simple one-off fetches; learning React</td></tr>
  <tr><td>TanStack Query / SWR</td><td>Production client apps with caching, refetch, mutations</td></tr>
  <tr><td>React Server Components</td><td>Next.js / Remix apps; fetch on server, no client state</td></tr>
  <tr><td><code>use(promise)</code> + Suspense</td><td>React 19+ pattern for streaming data without effects</td></tr>
  <tr><td>Form actions / <code>useActionState</code></td><td>Form-driven server mutations</td></tr>
</table>

<p><strong>The <code>use()</code> hook (React 19+):</strong></p>

<pre><code>import { use, Suspense } from "react";

function Posts({ postsPromise }) {
  const posts = use(postsPromise);     // suspends until promise resolves
  return &lt;ul&gt;{posts.map(p =&gt; &lt;li key={p.id}&gt;{p.title}&lt;/li&gt;)}&lt;/ul&gt;;
}

function App() {
  const promise = fetch("/api/posts").then(r =&gt; r.json());
  return (
    &lt;Suspense fallback={&lt;p&gt;Loading...&lt;/p&gt;}&gt;
      &lt;Posts postsPromise={promise} /&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p>No <code>useEffect</code>, no loading state, no error state &mdash; the Suspense boundary handles it. This pattern works best when data starts loading high in the tree (passed down as a promise prop) so it begins early, before deeper components render.</p>

<p>For interview answers that ask about data fetching: lead with the basic <code>useEffect</code> pattern, then mention TanStack Query as the production tool. Demonstrating awareness of trade-offs is what interviewers look for at this level.</p>
'''

ANSWERS[41] = r'''
<p><code>useCallback</code> memoizes a function reference so it stays the same across renders unless its dependencies change. Without it, every render creates a new function instance, which can break optimizations downstream.</p>

<pre><code>import { useState, useCallback } from "react";

function Parent() {
  const [count, setCount] = useState(0);

  // Without useCallback: a new function on every render
  // const handleClick = () =&gt; setCount(c =&gt; c + 1);

  // With useCallback: same function reference between renders
  const handleClick = useCallback(() =&gt; {
    setCount(c =&gt; c + 1);
  }, []);   // empty deps = function never changes

  return &lt;Child onClick={handleClick} /&gt;;
}

const Child = React.memo(({ onClick }) =&gt; {
  console.log("Child rendered");
  return &lt;button onClick={onClick}&gt;Click&lt;/button&gt;;
});</code></pre>

<p><strong>Why this matters</strong>: <code>React.memo</code> wraps a component to skip re-rendering when its props haven&rsquo;t changed (referentially). If the parent passes a new function instance every render (without <code>useCallback</code>), the prop "changes" each time and memoization is defeated.</p>

<p><strong>When to use <code>useCallback</code>:</strong></p>
<ul>
  <li>The function is passed as a prop to a <strong>memoized child</strong> (<code>React.memo</code>).</li>
  <li>The function is a <strong>dependency of another hook</strong> (<code>useEffect</code>, <code>useMemo</code>).</li>
  <li>The function is used in a <strong>custom hook</strong> with stable identity expectations.</li>
</ul>

<p><strong>When NOT to use it</strong>: regular event handlers that aren&rsquo;t passed deep, prop-passing to non-memoized components, simple components where re-renders are cheap. Premature memoization adds complexity without benefit.</p>

<p><strong>React 19&rsquo;s React Compiler</strong> automatically applies <code>useCallback</code> and <code>useMemo</code> where beneficial &mdash; manually wrapping is often unnecessary in modern projects.</p>
'''

ANSWERS[42] = r'''
<p>Performance optimization in React focuses on <strong>preventing unnecessary re-renders</strong> and reducing bundle size. The browser is fast; React is fast; problems usually come from doing too much work on every state update.</p>

<p><strong>Key optimization techniques:</strong></p>

<table>
  <tr><th>Technique</th><th>What it does</th></tr>
  <tr><td><code>React.memo</code></td><td>Skip re-render if props haven&rsquo;t changed (shallow compare)</td></tr>
  <tr><td><code>useMemo</code></td><td>Cache expensive computed values</td></tr>
  <tr><td><code>useCallback</code></td><td>Cache function references for memoized children</td></tr>
  <tr><td>Code splitting (<code>React.lazy</code>)</td><td>Load components only when needed; smaller initial bundle</td></tr>
  <tr><td>Virtualization (TanStack Virtual)</td><td>Only render visible items in long lists</td></tr>
  <tr><td>Avoid inline objects/arrays</td><td>New reference each render breaks memoization</td></tr>
  <tr><td>Move state down</td><td>Local state doesn&rsquo;t cause parent re-render</td></tr>
  <tr><td>Lift state up wisely</td><td>Avoid prop drilling that re-renders many components</td></tr>
</table>

<pre><code>// AVOID: new array reference every render
&lt;Component items={[1, 2, 3]} /&gt;

// BETTER: stable reference
const items = useMemo(() =&gt; [1, 2, 3], []);
&lt;Component items={items} /&gt;</code></pre>

<p><strong>Profile before optimizing</strong> &mdash; React DevTools Profiler shows which components rendered, how long they took, and why. Optimize what&rsquo;s actually slow, not what you guess might be slow.</p>

<p><strong>2026 reality:</strong> the <strong>React Compiler</strong> (production-ready in React 19) automatically applies memoization where beneficial. For new code, write naturally and let the compiler optimize. Manual <code>useMemo</code>/<code>useCallback</code> is needed mainly for older codebases or when the compiler can&rsquo;t verify safety.</p>

<p>Bundle size matters too: tree-shake imports, prefer named imports over default for small utilities, and use the bundle analyzer to spot large dependencies.</p>
'''

ANSWERS[43] = r'''
<p><code>useMemo</code> caches the result of an expensive computation between renders. The function only re-runs when one of its dependencies changes &mdash; otherwise the previous result is returned.</p>

<pre><code>import { useState, useMemo } from "react";

function ProductList({ products, query }) {
  // Expensive: filter 10,000 items on every render
  const filtered = useMemo(() =&gt; {
    return products.filter(p =&gt;
      p.name.toLowerCase().includes(query.toLowerCase())
    );
  }, [products, query]);   // only re-filter if products or query change

  return (
    &lt;ul&gt;
      {filtered.map(p =&gt; &lt;li key={p.id}&gt;{p.name}&lt;/li&gt;)}
    &lt;/ul&gt;
  );
}</code></pre>

<p><strong>useMemo vs useCallback:</strong></p>

<table>
  <tr><th></th><th>useMemo</th><th>useCallback</th></tr>
  <tr><td>What it caches</td><td>The result of calling a function</td><td>The function itself</td></tr>
  <tr><td>Returns</td><td>Whatever your function returns</td><td>The function reference</td></tr>
  <tr><td>Use for</td><td>Expensive calculations, derived state</td><td>Stable function references for memoized components</td></tr>
</table>

<pre><code>const value = useMemo(() =&gt; expensiveCalc(a, b), [a, b]);
const handler = useCallback(() =&gt; doSomething(a), [a]);

// useCallback(fn, deps) === useMemo(() =&gt; fn, deps)</code></pre>

<p><strong>When useMemo is worth it:</strong></p>
<ul>
  <li>Filtering or sorting <strong>large lists</strong> (1000+ items).</li>
  <li>Heavy computations like complex math, formatting, or transformations.</li>
  <li>Creating <strong>stable object/array references</strong> passed to memoized children.</li>
  <li>Derived data computed from props/state.</li>
</ul>

<p><strong>When NOT to use it</strong>: simple calculations, primitive values, when the dependency itself changes every render (no memoization benefit), or to "just be safe" (the bookkeeping overhead can exceed the savings).</p>

<p>As with <code>useCallback</code>, React 19&rsquo;s compiler auto-applies <code>useMemo</code> where it helps &mdash; manual usage is mostly for legacy code or compiler edge cases.</p>
'''

ANSWERS[44] = r'''
<p>React error handling has two layers: <strong>try/catch for async operations</strong> (data fetching, event handlers) and <strong>error boundaries</strong> for rendering errors that propagate up the component tree.</p>

<p><strong>Errors during render</strong> &mdash; caught by error boundaries (see Q45-46):</p>

<pre><code>function BrokenComponent() {
  throw new Error("Something went wrong");
}

function App() {
  return (
    &lt;ErrorBoundary fallback={&lt;p&gt;Oops!&lt;/p&gt;}&gt;
      &lt;BrokenComponent /&gt;
    &lt;/ErrorBoundary&gt;
  );
}</code></pre>

<p><strong>Errors in event handlers</strong> &mdash; standard try/catch (NOT caught by error boundaries):</p>

<pre><code>function SubmitButton() {
  const handleClick = async () =&gt; {
    try {
      await fetch("/api/submit", { method: "POST" });
      alert("Success!");
    } catch (error) {
      alert(`Failed: ${error.message}`);
    }
  };
  return &lt;button onClick={handleClick}&gt;Submit&lt;/button&gt;;
}</code></pre>

<p><strong>What error boundaries catch vs miss:</strong></p>

<table>
  <tr><th>Caught by error boundaries</th><th>NOT caught</th></tr>
  <tr><td>Errors during rendering</td><td>Errors in event handlers</td></tr>
  <tr><td>Errors in lifecycle methods</td><td>Asynchronous code (setTimeout, promises)</td></tr>
  <tr><td>Errors in constructors of children</td><td>Server-side rendering errors</td></tr>
  <tr><td></td><td>Errors thrown in the boundary itself</td></tr>
</table>

<p><strong>Production error reporting</strong> &mdash; integrate with services like <strong>Sentry</strong>, <strong>Bugsnag</strong>, or <strong>Datadog</strong>. Wrap your app in an error boundary that logs errors to the service, then shows a fallback UI.</p>

<p><strong>For data fetching errors</strong>, libraries like TanStack Query expose error state directly: <code>const { error } = useQuery(...)</code>. No try/catch boilerplate.</p>

<p>The right pattern: <strong>error boundaries</strong> at strategic points (page-level, key features) for unexpected render failures, plus <strong>try/catch + error UI states</strong> for predictable failures (network errors, validation, etc.).</p>
'''

ANSWERS[45] = r'''
<p>An <strong>error boundary</strong> is a React component that catches JavaScript errors in its child component tree, logs them, and displays a fallback UI instead of crashing the entire app. They&rsquo;re React&rsquo;s implementation of a "try/catch" for the rendering lifecycle.</p>

<p><strong>What error boundaries catch:</strong></p>
<ul>
  <li>Errors during rendering of children.</li>
  <li>Errors in lifecycle methods of children.</li>
  <li>Errors in constructors of children.</li>
</ul>

<p><strong>What they DON&rsquo;T catch:</strong></p>
<ul>
  <li>Event handlers (use <code>try/catch</code>).</li>
  <li>Async code (<code>setTimeout</code>, fetch promises).</li>
  <li>Server-side rendering.</li>
  <li>Errors thrown in the boundary component itself.</li>
</ul>

<pre><code>// Without error boundary: one broken component crashes the whole app

// With error boundary: only that subtree shows fallback
&lt;App&gt;
  &lt;ErrorBoundary fallback={&lt;Header /&gt;}&gt;     {/* protects header */}
    &lt;Header /&gt;
  &lt;/ErrorBoundary&gt;
  &lt;ErrorBoundary fallback={&lt;Sidebar /&gt;}&gt;    {/* protects sidebar separately */}
    &lt;Sidebar /&gt;
  &lt;/ErrorBoundary&gt;
&lt;/App&gt;</code></pre>

<p><strong>Why use them</strong>: in production, an unhandled error tears down the entire React tree &mdash; users see a blank page. Error boundaries scope failures to a section, keep the rest of the app working, and let you show a friendly "Something went wrong" with a retry button.</p>

<p><strong>Strategic placement:</strong></p>
<ul>
  <li><strong>Page level</strong> &mdash; catches everything; shows full-page error state.</li>
  <li><strong>Feature level</strong> &mdash; isolates broken features (a bad widget doesn&rsquo;t kill the page).</li>
  <li><strong>Around third-party components</strong> &mdash; protects you from external bugs.</li>
</ul>

<p><strong>2026 note</strong>: error boundaries still must be <strong>class components</strong> (no hook equivalent yet, though discussed for future React versions). Most teams use libraries like <code>react-error-boundary</code> for cleaner functional usage. See Q46 for implementation.</p>
'''

ANSWERS[46] = r'''
<p>Error boundaries are class components that implement <code>getDerivedStateFromError</code> (to render fallback UI) and/or <code>componentDidCatch</code> (to log the error).</p>

<pre><code>import { Component } from "react";

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  // Update state to render fallback on the next render
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  // Log the error to a reporting service
  componentDidCatch(error, errorInfo) {
    console.error("Error caught:", error, errorInfo);
    // sendToSentry(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        &lt;div className="error-fallback"&gt;
          &lt;h2&gt;Something went wrong&lt;/h2&gt;
          &lt;p&gt;{this.state.error?.message}&lt;/p&gt;
          &lt;button onClick={() =&gt; this.setState({ hasError: false })}&gt;
            Try again
          &lt;/button&gt;
        &lt;/div&gt;
      );
    }
    return this.props.children;
  }
}

// Usage
function App() {
  return (
    &lt;ErrorBoundary&gt;
      &lt;UserDashboard /&gt;
    &lt;/ErrorBoundary&gt;
  );
}</code></pre>

<p><strong>The two methods explained:</strong></p>

<table>
  <tr><th>Method</th><th>Purpose</th></tr>
  <tr><td><code>getDerivedStateFromError</code></td><td>Set state to trigger fallback render. Pure &mdash; no side effects.</td></tr>
  <tr><td><code>componentDidCatch</code></td><td>Log error, call analytics. Has side effects.</td></tr>
</table>

<p><strong>Modern approach &mdash; the <code>react-error-boundary</code> library</strong> wraps this in a hook-friendly component:</p>

<pre><code>import { ErrorBoundary } from "react-error-boundary";

function FallbackUI({ error, resetErrorBoundary }) {
  return (
    &lt;div&gt;
      &lt;p&gt;Error: {error.message}&lt;/p&gt;
      &lt;button onClick={resetErrorBoundary}&gt;Retry&lt;/button&gt;
    &lt;/div&gt;
  );
}

&lt;ErrorBoundary
  FallbackComponent={FallbackUI}
  onError={(error, info) =&gt; logToService(error, info)}
  onReset={() =&gt; resetState()}
&gt;
  &lt;App /&gt;
&lt;/ErrorBoundary&gt;</code></pre>

<p>Most teams use this library &mdash; less boilerplate, built-in reset capability, plays nicely with hooks. In 2026 it&rsquo;s the de-facto standard for error boundaries in React applications.</p>
'''

ANSWERS[47] = r'''
<p>Lazy loading defers loading a component&rsquo;s code until it&rsquo;s actually needed &mdash; reducing the initial bundle size and speeding up first page load. React provides <code>React.lazy()</code> for this, paired with <code>Suspense</code> for the loading fallback.</p>

<pre><code>import { lazy, Suspense } from "react";

// Component code is fetched only when first rendered
const Dashboard = lazy(() =&gt; import("./Dashboard"));
const Settings = lazy(() =&gt; import("./Settings"));

function App() {
  return (
    &lt;Suspense fallback={&lt;p&gt;Loading...&lt;/p&gt;}&gt;
      &lt;Routes&gt;
        &lt;Route path="/dashboard" element={&lt;Dashboard /&gt;} /&gt;
        &lt;Route path="/settings" element={&lt;Settings /&gt;} /&gt;
      &lt;/Routes&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p><strong>What happens behind the scenes:</strong></p>
<ol>
  <li>Webpack/Vite splits the import into a separate JS chunk during build.</li>
  <li>The main bundle stays small &mdash; doesn&rsquo;t include the lazy component.</li>
  <li>When React renders <code>&lt;Dashboard /&gt;</code>, it fetches the chunk.</li>
  <li>While loading, <code>Suspense</code> shows the fallback.</li>
  <li>Once loaded, the component renders and is cached for future use.</li>
</ol>

<p><strong>Common lazy-loading patterns:</strong></p>

<table>
  <tr><th>Pattern</th><th>What to lazy-load</th></tr>
  <tr><td>Route-based splitting</td><td>Each top-level route as a separate chunk</td></tr>
  <tr><td>Modal-based</td><td>Modals and dialogs (only loaded when opened)</td></tr>
  <tr><td>Tab-based</td><td>Each tab as a chunk</td></tr>
  <tr><td>Below-the-fold</td><td>Heavy components below the visible viewport</td></tr>
</table>

<p><strong>Critical requirement</strong>: <code>React.lazy</code> only works with <strong>default exports</strong>:</p>

<pre><code>// component.tsx
export default function Dashboard() { ... }   // ✓

// Use named export — won't work with React.lazy directly
export function Dashboard() { ... }            // ✗

// Workaround for named exports
const Dashboard = lazy(() =&gt;
  import("./components").then(m =&gt; ({ default: m.Dashboard }))
);</code></pre>

<p><strong>Don&rsquo;t over-split</strong>: too many chunks = many small network requests. Group related components into the same chunk for better performance.</p>
'''

ANSWERS[48] = r'''
<p><strong>React Suspense</strong> is a built-in component that lets parts of the tree "wait" for something before rendering &mdash; showing a fallback UI in the meantime. Originally designed for code splitting (with <code>React.lazy</code>), it&rsquo;s evolved into a general mechanism for asynchronous rendering: data fetching, code loading, and any operation that returns a promise.</p>

<pre><code>import { Suspense } from "react";

function App() {
  return (
    &lt;Suspense fallback={&lt;p&gt;Loading...&lt;/p&gt;}&gt;
      &lt;LazyDashboard /&gt;
    &lt;/Suspense&gt;
  );
}</code></pre>

<p><strong>The core idea</strong>: instead of every component managing its own loading state, a parent <code>Suspense</code> boundary handles the "I&rsquo;m not ready yet" signal from any descendant. Components throw a promise when they&rsquo;re not ready; Suspense catches it and renders the fallback until the promise resolves.</p>

<p><strong>What Suspense supports in React 19+:</strong></p>

<table>
  <tr><th>Use case</th><th>How</th></tr>
  <tr><td>Code splitting</td><td><code>React.lazy()</code></td></tr>
  <tr><td>Data fetching</td><td><code>use(promise)</code> hook (React 19+)</td></tr>
  <tr><td>Server Components</td><td>Native streaming with Next.js / Remix</td></tr>
  <tr><td>Image preloading</td><td>Future: <code>preload()</code> APIs</td></tr>
</table>

<p><strong>Nested Suspense for streaming UI:</strong></p>

<pre><code>&lt;Suspense fallback={&lt;PageSkeleton /&gt;}&gt;
  &lt;Header /&gt;

  &lt;Suspense fallback={&lt;ContentSkeleton /&gt;}&gt;
    &lt;MainContent /&gt;
  &lt;/Suspense&gt;

  &lt;Suspense fallback={&lt;SidebarSkeleton /&gt;}&gt;
    &lt;Sidebar /&gt;
  &lt;/Suspense&gt;
&lt;/Suspense&gt;</code></pre>

<p>Each section loads independently. Header shows immediately; main and sidebar load in parallel and reveal as ready &mdash; no waterfall, smooth progressive UI.</p>

<p><strong>Why it&rsquo;s powerful</strong>: instead of writing <code>{loading ? &lt;Spinner /&gt; : data}</code> dozens of times across your app, you declare loading boundaries once and let React orchestrate. Combined with React Server Components, it enables full server-rendered streaming pages.</p>
'''

ANSWERS[49] = r'''
<p>Code splitting with Suspense is the most common pattern: combine <code>React.lazy()</code> for the component and <code>&lt;Suspense&gt;</code> for the loading state. The result: smaller initial bundles, faster page loads, deferred work for sections users may never visit.</p>

<pre><code>import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

const Home      = lazy(() =&gt; import("./pages/Home"));
const About     = lazy(() =&gt; import("./pages/About"));
const Dashboard = lazy(() =&gt; import("./pages/Dashboard"));

function App() {
  return (
    &lt;BrowserRouter&gt;
      &lt;Suspense fallback={&lt;LoadingSpinner /&gt;}&gt;
        &lt;Routes&gt;
          &lt;Route path="/" element={&lt;Home /&gt;} /&gt;
          &lt;Route path="/about" element={&lt;About /&gt;} /&gt;
          &lt;Route path="/dashboard" element={&lt;Dashboard /&gt;} /&gt;
        &lt;/Routes&gt;
      &lt;/Suspense&gt;
    &lt;/BrowserRouter&gt;
  );
}</code></pre>

<p><strong>Better skeletons</strong> &mdash; show layout placeholders instead of spinners:</p>

<pre><code>function PageSkeleton() {
  return (
    &lt;div className="skeleton"&gt;
      &lt;div className="skeleton-header" /&gt;
      &lt;div className="skeleton-paragraph" /&gt;
      &lt;div className="skeleton-paragraph" /&gt;
    &lt;/div&gt;
  );
}

&lt;Suspense fallback={&lt;PageSkeleton /&gt;}&gt;
  &lt;Dashboard /&gt;
&lt;/Suspense&gt;</code></pre>

<p>Skeletons feel faster than spinners because users see the eventual layout immediately &mdash; perceived performance improves.</p>

<p><strong>Multiple Suspense boundaries for parallel loading:</strong></p>

<pre><code>function Dashboard() {
  return (
    &lt;div&gt;
      &lt;Suspense fallback={&lt;StatsSkeleton /&gt;}&gt;
        &lt;Stats /&gt;             {/* loads in parallel */}
      &lt;/Suspense&gt;

      &lt;Suspense fallback={&lt;ChartSkeleton /&gt;}&gt;
        &lt;ChartsPanel /&gt;       {/* loads in parallel */}
      &lt;/Suspense&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Split at routes</strong> first &mdash; biggest payoff for least complexity.</li>
  <li><strong>Split at modals/dialogs</strong> &mdash; only load when user opens them.</li>
  <li><strong>Don&rsquo;t over-split</strong> &mdash; too many chunks means too many requests.</li>
  <li><strong>Preload on hover</strong> &mdash; trigger the import when user hovers a link, so it&rsquo;s ready when clicked.</li>
</ul>

<p>Modern build tools (Vite, Next.js) automate most of this &mdash; they detect dynamic imports and split chunks during build. You write <code>lazy(() =&gt; import(...))</code>; the bundler handles the rest.</p>
'''

ANSWERS[50] = r'''
<p>Both hooks run side effects, but <strong>at different times in the render cycle</strong>:</p>

<table>
  <tr><th></th><th><code>useEffect</code></th><th><code>useLayoutEffect</code></th></tr>
  <tr><td>When it runs</td><td>After browser paints</td><td>Before browser paints (synchronously)</td></tr>
  <tr><td>Blocks paint?</td><td>No &mdash; non-blocking</td><td>Yes &mdash; can delay paint</td></tr>
  <tr><td>Use for</td><td>Most side effects: data fetch, subscriptions, timers</td><td>DOM measurements, synchronous layout updates</td></tr>
  <tr><td>Default choice</td><td>Yes (preferred 99% of the time)</td><td>Only when you see flicker with useEffect</td></tr>
</table>

<p><strong>The classic case for useLayoutEffect &mdash; reading DOM dimensions and updating state synchronously:</strong></p>

<pre><code>import { useState, useLayoutEffect, useRef } from "react";

function Tooltip({ children, target }) {
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef(null);

  useLayoutEffect(() =&gt; {
    if (!target || !tooltipRef.current) return;

    const targetRect = target.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();

    setPosition({
      top: targetRect.top - tooltipRect.height - 8,
      left: targetRect.left + targetRect.width / 2 - tooltipRect.width / 2
    });
  }, [target]);

  return (
    &lt;div ref={tooltipRef} style={position}&gt;
      {children}
    &lt;/div&gt;
  );
}</code></pre>

<p>If we used <code>useEffect</code> here, the tooltip would render at <code>(0, 0)</code> first, then snap to the correct position &mdash; users would see a flicker. <code>useLayoutEffect</code> updates state before paint, so the tooltip appears in its correct position immediately.</p>

<p><strong>Decision rule:</strong></p>
<ol>
  <li>Default to <code>useEffect</code>.</li>
  <li>If you see flicker (visible "jump" between renders), switch to <code>useLayoutEffect</code>.</li>
  <li>Don&rsquo;t use <code>useLayoutEffect</code> "to be safe" &mdash; blocking the paint hurts perceived performance.</li>
</ol>

<p><strong>SSR caveat</strong>: <code>useLayoutEffect</code> doesn&rsquo;t run on the server (no DOM to measure) &mdash; React warns if used in SSR contexts. For isomorphic code, use <code>useIsomorphicLayoutEffect</code> from utility libraries, or guard with <code>typeof window !== "undefined"</code>.</p>
'''

ANSWERS[51] = r'''
<p>State management in React ranges from <strong>local component state</strong> to <strong>global app-wide state</strong>. Choose the simplest tool that fits the problem &mdash; complexity escalates only as needs grow.</p>

<p><strong>The state management hierarchy (use in order):</strong></p>

<table>
  <tr><th>Tool</th><th>Use for</th></tr>
  <tr><td><code>useState</code></td><td>Local component state (input, toggle, counter)</td></tr>
  <tr><td><code>useReducer</code></td><td>Complex local state with multiple transitions</td></tr>
  <tr><td>Lifted state + props</td><td>State shared between siblings (lift to common parent)</td></tr>
  <tr><td>Context API + <code>useReducer</code></td><td>App-wide state with no library</td></tr>
  <tr><td><strong>Zustand / Jotai</strong></td><td>Lightweight global state (recommended in 2026)</td></tr>
  <tr><td>Redux Toolkit</td><td>Large apps; team prefers explicit action/reducer pattern</td></tr>
  <tr><td>TanStack Query / SWR</td><td>Server state (API data with caching)</td></tr>
</table>

<pre><code>// Local: useState
const [count, setCount] = useState(0);

// Lifted: parent owns it
function Parent() {
  const [count, setCount] = useState(0);
  return &lt;ChildA count={count} setCount={setCount} /&gt;;
}

// Global: Zustand (popular 2026 choice)
import { create } from "zustand";
const useStore = create((set) =&gt; ({
  count: 0,
  increment: () =&gt; set((s) =&gt; ({ count: s.count + 1 }))
}));

function Counter() {
  const { count, increment } = useStore();
  return &lt;button onClick={increment}&gt;{count}&lt;/button&gt;;
}</code></pre>

<p><strong>Crucial distinction &mdash; client state vs server state:</strong></p>
<ul>
  <li><strong>Client state</strong>: UI state, form values, modals open/closed, selected items. Owned by your app. Use Zustand, Context, or useState.</li>
  <li><strong>Server state</strong>: data from APIs, database. Cached. Use TanStack Query or SWR &mdash; they handle caching, refetching, deduplication automatically. Don&rsquo;t store server data in Redux.</li>
</ul>

<p><strong>2026 recommendation:</strong> for new apps, default to <strong>useState + Context</strong> for simple cases, <strong>Zustand</strong> for global client state, and <strong>TanStack Query</strong> for server state. Redux is still common in large legacy codebases but Redux Toolkit is the modern API if you choose it.</p>
'''

ANSWERS[52] = r'''
<p><strong>React hooks</strong> are functions that let you "hook into" React features &mdash; state, lifecycle, context, refs &mdash; from functional components. Introduced in React 16.8 (2019), they replaced the need for class components and unified how reusable logic is shared.</p>

<p><strong>Why hooks matter:</strong></p>
<ul>
  <li><strong>Functional components can have state</strong> &mdash; no more class boilerplate.</li>
  <li><strong>Stateful logic is reusable</strong> via custom hooks &mdash; replaces HOCs and render props.</li>
  <li><strong>Related logic is co-located</strong> instead of split across <code>componentDidMount</code>, <code>componentDidUpdate</code>, <code>componentWillUnmount</code>.</li>
  <li><strong>Cleaner component code</strong> &mdash; less indentation, fewer wrappers.</li>
</ul>

<p><strong>The core built-in hooks:</strong></p>

<table>
  <tr><th>Hook</th><th>Purpose</th></tr>
  <tr><td><code>useState</code></td><td>Local state in a functional component</td></tr>
  <tr><td><code>useEffect</code></td><td>Side effects (data fetch, subscriptions)</td></tr>
  <tr><td><code>useContext</code></td><td>Read context value</td></tr>
  <tr><td><code>useReducer</code></td><td>Complex state with reducer pattern</td></tr>
  <tr><td><code>useRef</code></td><td>Mutable reference; access DOM nodes</td></tr>
  <tr><td><code>useMemo</code></td><td>Memoize expensive computations</td></tr>
  <tr><td><code>useCallback</code></td><td>Memoize function references</td></tr>
  <tr><td><code>useLayoutEffect</code></td><td>Effect that runs before browser paint</td></tr>
  <tr><td><code>useId</code></td><td>Generate stable unique IDs</td></tr>
  <tr><td><code>useTransition</code></td><td>Mark updates as non-urgent (React 18+)</td></tr>
  <tr><td><code>useDeferredValue</code></td><td>Defer re-rendering with stale value</td></tr>
  <tr><td><code>use(promise/context)</code></td><td>Read promises or context (React 19+)</td></tr>
  <tr><td><code>useActionState</code></td><td>Handle form actions (React 19+)</td></tr>
  <tr><td><code>useOptimistic</code></td><td>Show optimistic UI updates (React 19+)</td></tr>
</table>

<p><strong>The two rules of hooks (enforced by ESLint):</strong></p>
<ol>
  <li><strong>Only call hooks at the top level</strong> &mdash; not in loops, conditions, or nested functions. React relies on call order to associate hook calls with their state.</li>
  <li><strong>Only call hooks from React functions</strong> &mdash; functional components or other custom hooks. Not from regular JavaScript functions or class components.</li>
</ol>

<pre><code>// BAD: hook inside conditional
if (loggedIn) {
  const [data, setData] = useState(null);   // ✗ violates rule 1
}

// GOOD: hook at top level; conditional inside
const [data, setData] = useState(null);
useEffect(() =&gt; {
  if (loggedIn) fetchData();
}, [loggedIn]);</code></pre>

<p>Hooks are now the primary React API in 2026. Class components still work but are rarely written for new code &mdash; they&rsquo;re reserved for error boundaries (the only use case lacking a hook equivalent).</p>
'''

ANSWERS[53] = r'''
<p>A custom hook is a JavaScript function whose name starts with <code>use</code> and that calls other hooks. It encapsulates reusable stateful logic so multiple components can share it without duplication.</p>

<pre><code>import { useState, useEffect } from "react";

// Custom hook that tracks window size
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() =&gt; {
    const handleResize = () =&gt; {
      setSize({ width: window.innerWidth, height: window.innerHeight });
    };
    window.addEventListener("resize", handleResize);
    return () =&gt; window.removeEventListener("resize", handleResize);
  }, []);

  return size;
}

// Use it like a built-in hook
function Header() {
  const { width } = useWindowSize();
  return width &lt; 768 ? &lt;MobileHeader /&gt; : &lt;DesktopHeader /&gt;;
}</code></pre>

<p><strong>Common custom hooks people build:</strong></p>

<table>
  <tr><th>Hook</th><th>Purpose</th></tr>
  <tr><td><code>useLocalStorage</code></td><td>Sync state with localStorage</td></tr>
  <tr><td><code>useDebounce</code></td><td>Debounce a fast-changing value</td></tr>
  <tr><td><code>useFetch</code></td><td>Fetch data with loading/error states</td></tr>
  <tr><td><code>usePrevious</code></td><td>Track previous value of a state/prop</td></tr>
  <tr><td><code>useMediaQuery</code></td><td>Match media queries reactively</td></tr>
  <tr><td><code>useOnClickOutside</code></td><td>Detect clicks outside an element</td></tr>
  <tr><td><code>useIntersectionObserver</code></td><td>Track element visibility</td></tr>
</table>

<p><strong>Example &mdash; useLocalStorage:</strong></p>

<pre><code>function useLocalStorage(key, initial) {
  const [value, setValue] = useState(() =&gt; {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initial;
  });

  useEffect(() =&gt; {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// Usage
const [theme, setTheme] = useLocalStorage("theme", "light");</code></pre>

<p><strong>Best practices:</strong></p>
<ul>
  <li><strong>Name starts with <code>use</code></strong> &mdash; required by linter; signals that hook rules apply.</li>
  <li><strong>Each component using the hook gets isolated state</strong> &mdash; calling <code>useWindowSize</code> in two components creates two separate state instances. Use Context or a state library for genuinely shared state.</li>
  <li><strong>Compose hooks freely</strong> &mdash; custom hooks can call other custom hooks.</li>
  <li><strong>Test as plain functions</strong> &mdash; with <code>renderHook</code> from React Testing Library.</li>
</ul>

<p>Many libraries publish ready-made custom hooks: <code>react-use</code>, <code>usehooks-ts</code>, <code>@uidotdev/usehooks</code>. Useful as references and ready-to-use solutions.</p>
'''

ANSWERS[54] = r'''
<p><strong>PropTypes</strong> is a runtime type-checking library for React component props. In development mode, it warns in the console if props don&rsquo;t match the expected types &mdash; helpful for catching bugs early.</p>

<pre><code>import PropTypes from "prop-types";

function UserCard({ name, age, isAdmin, tags, onClick }) {
  return (
    &lt;div onClick={onClick}&gt;
      &lt;h3&gt;{name} ({age})&lt;/h3&gt;
      {isAdmin &amp;&amp; &lt;span&gt;Admin&lt;/span&gt;}
      {tags.map(t =&gt; &lt;span key={t}&gt;{t}&lt;/span&gt;)}
    &lt;/div&gt;
  );
}

UserCard.propTypes = {
  name: PropTypes.string.isRequired,
  age: PropTypes.number,
  isAdmin: PropTypes.bool,
  tags: PropTypes.arrayOf(PropTypes.string),
  onClick: PropTypes.func.isRequired
};</code></pre>

<p>Now if you accidentally do <code>&lt;UserCard name={42} /&gt;</code>, the console warns: "Failed prop type: name expected string, received number."</p>

<p><strong>Common PropTypes validators:</strong></p>

<table>
  <tr><th>Validator</th><th>Use for</th></tr>
  <tr><td><code>PropTypes.string</code></td><td>Strings</td></tr>
  <tr><td><code>PropTypes.number</code></td><td>Numbers</td></tr>
  <tr><td><code>PropTypes.bool</code></td><td>Booleans</td></tr>
  <tr><td><code>PropTypes.func</code></td><td>Functions</td></tr>
  <tr><td><code>PropTypes.array</code></td><td>Arrays (any type)</td></tr>
  <tr><td><code>PropTypes.arrayOf(...)</code></td><td>Arrays of specific type</td></tr>
  <tr><td><code>PropTypes.object</code></td><td>Plain objects</td></tr>
  <tr><td><code>PropTypes.shape({...})</code></td><td>Object with specific keys/types</td></tr>
  <tr><td><code>PropTypes.oneOf([...])</code></td><td>Enum-like (one of given values)</td></tr>
  <tr><td><code>PropTypes.oneOfType([...])</code></td><td>Union type</td></tr>
  <tr><td><code>PropTypes.node</code></td><td>Anything renderable (string, element, array)</td></tr>
  <tr><td><code>PropTypes.element</code></td><td>A single React element</td></tr>
</table>

<p>Append <code>.isRequired</code> to make a prop mandatory.</p>

<p><strong>2026 reality &mdash; PropTypes is largely obsolete</strong>. Most teams use <strong>TypeScript</strong> instead, which provides static type checking at compile time:</p>

<pre><code>type UserCardProps = {
  name: string;
  age?: number;
  isAdmin?: boolean;
  tags?: string[];
  onClick: () =&gt; void;
};

function UserCard({ name, age, isAdmin, tags = [], onClick }: UserCardProps) {
  // TypeScript catches type errors before the code runs
}</code></pre>

<p>TypeScript is more powerful (catches errors at build time, integrates with editors), faster (no runtime overhead), and more thorough. PropTypes was deprecated from React itself in version 15.5 (now external package <code>prop-types</code>); <strong>for new projects, choose TypeScript over PropTypes</strong>.</p>
'''

ANSWERS[55] = r'''
<p>Default props let a component fall back to a default value when the parent doesn&rsquo;t pass that prop. The modern (and preferred) pattern uses <strong>destructuring with default values</strong>; class components and older code use <code>defaultProps</code>.</p>

<p><strong>Functional component &mdash; destructuring defaults (modern):</strong></p>

<pre><code>function Button({
  label = "Click me",
  variant = "primary",
  onClick = () =&gt; {},
  disabled = false
}) {
  return (
    &lt;button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    &gt;
      {label}
    &lt;/button&gt;
  );
}

// Usage with no props — uses all defaults
&lt;Button /&gt;

// Override some
&lt;Button label="Save" variant="success" /&gt;</code></pre>

<p><strong>Class component &mdash; <code>defaultProps</code> static:</strong></p>

<pre><code>class Button extends React.Component {
  static defaultProps = {
    label: "Click me",
    variant: "primary",
    disabled: false
  };

  render() {
    return &lt;button ... /&gt;;
  }
}</code></pre>

<p><strong>The <code>defaultProps</code> approach</strong> works for both class and functional components historically, but in React 18+ it&rsquo;s deprecated for functional components &mdash; destructuring defaults is the official recommendation. React 19 removed the <code>defaultProps</code> warning for functional components.</p>

<p><strong>Comparison:</strong></p>

<table>
  <tr><th>Approach</th><th>Pros</th><th>Cons</th></tr>
  <tr><td>Destructuring defaults</td><td>Explicit, simple, works with TypeScript</td><td>Slight verbosity for many props</td></tr>
  <tr><td><code>defaultProps</code> object</td><td>Centralized in one place</td><td>Deprecated for functional components</td></tr>
</table>

<p><strong>Defaults work for nullish, not falsy</strong> &mdash; destructuring defaults only kick in when the value is <code>undefined</code>. Passing <code>null</code> bypasses the default:</p>

<pre><code>function Button({ label = "Default" }) { return &lt;button&gt;{label}&lt;/button&gt;; }

&lt;Button /&gt;                    // label = "Default" ✓
&lt;Button label={undefined} /&gt;   // label = "Default" ✓
&lt;Button label={null} /&gt;        // label = null     ✗ (default doesn't apply)
&lt;Button label="" /&gt;            // label = ""       ✗ (empty string is intentional)</code></pre>

<p>If you want a default for null too, use <code>label ?? "Default"</code> in the body. For most cases, the standard destructuring default is exactly the right behavior.</p>
'''

ANSWERS[56] = r'''
<p>Form validation in React typically combines <strong>React state</strong> for input values, <strong>validation logic</strong> on change/submit, and <strong>error display</strong> next to fields. For non-trivial forms, libraries like <strong>React Hook Form</strong> + <strong>Zod</strong> handle most of this with much less code.</p>

<p><strong>Manual validation &mdash; small forms:</strong></p>

<pre><code>function SignupForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});

  const validate = () =&gt; {
    const newErrors = {};
    if (!email) newErrors.email = "Email is required";
    else if (!/^[^@]+@[^@]+\.[^@]+$/.test(email))
      newErrors.email = "Invalid email";
    if (password.length &lt; 8)
      newErrors.password = "Password must be 8+ characters";
    return newErrors;
  };

  const handleSubmit = (e) =&gt; {
    e.preventDefault();
    const errors = validate();
    if (Object.keys(errors).length &gt; 0) {
      setErrors(errors);
      return;
    }
    // submit form...
  };

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input
        value={email}
        onChange={e =&gt; setEmail(e.target.value)}
        placeholder="Email"
      /&gt;
      {errors.email &amp;&amp; &lt;p className="error"&gt;{errors.email}&lt;/p&gt;}

      &lt;input
        type="password"
        value={password}
        onChange={e =&gt; setPassword(e.target.value)}
        placeholder="Password"
      /&gt;
      {errors.password &amp;&amp; &lt;p className="error"&gt;{errors.password}&lt;/p&gt;}

      &lt;button type="submit"&gt;Sign up&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Modern approach &mdash; React Hook Form + Zod (recommended for production):</strong></p>

<pre><code>import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be 8+ characters")
});

function SignupForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema)
  });

  return (
    &lt;form onSubmit={handleSubmit(data =&gt; console.log(data))}&gt;
      &lt;input {...register("email")} placeholder="Email" /&gt;
      {errors.email &amp;&amp; &lt;p&gt;{errors.email.message}&lt;/p&gt;}

      &lt;input type="password" {...register("password")} /&gt;
      {errors.password &amp;&amp; &lt;p&gt;{errors.password.message}&lt;/p&gt;}

      &lt;button type="submit"&gt;Sign up&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Why React Hook Form is the 2026 standard:</strong></p>
<ul>
  <li><strong>Uncontrolled by default</strong> &mdash; faster, fewer re-renders.</li>
  <li><strong>Schema validation</strong> with Zod, Yup, or Joi.</li>
  <li><strong>Built-in async validation</strong> for server-side checks.</li>
  <li><strong>TypeScript support</strong> &mdash; types inferred from Zod schema.</li>
  <li><strong>Field arrays, nested objects, conditional fields</strong> all supported.</li>
</ul>

<p>For interview answers: lead with the manual pattern to show you understand the underlying mechanics, then mention React Hook Form + Zod as the production tool of choice.</p>
'''

ANSWERS[57] = r'''
<p><strong>React Router</strong> is the standard library for client-side routing in React applications &mdash; mapping URLs to components, handling navigation without full page reloads, and managing browser history. Current major version is React Router v7 (2024+) which combines features from earlier v6 and Remix.</p>

<pre><code>// Install: npm install react-router-dom

import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

function App() {
  return (
    &lt;BrowserRouter&gt;
      &lt;nav&gt;
        &lt;Link to="/"&gt;Home&lt;/Link&gt;
        &lt;Link to="/about"&gt;About&lt;/Link&gt;
        &lt;Link to="/products"&gt;Products&lt;/Link&gt;
      &lt;/nav&gt;

      &lt;Routes&gt;
        &lt;Route path="/" element={&lt;Home /&gt;} /&gt;
        &lt;Route path="/about" element={&lt;About /&gt;} /&gt;
        &lt;Route path="/products" element={&lt;Products /&gt;} /&gt;
        &lt;Route path="/products/:id" element={&lt;ProductDetail /&gt;} /&gt;
        &lt;Route path="*" element={&lt;NotFound /&gt;} /&gt;
      &lt;/Routes&gt;
    &lt;/BrowserRouter&gt;
  );
}</code></pre>

<p><strong>Core building blocks:</strong></p>

<table>
  <tr><th>Component</th><th>Purpose</th></tr>
  <tr><td><code>&lt;BrowserRouter&gt;</code></td><td>Wraps app; provides routing context</td></tr>
  <tr><td><code>&lt;Routes&gt;</code></td><td>Container for route definitions</td></tr>
  <tr><td><code>&lt;Route&gt;</code></td><td>Maps a URL pattern to a component</td></tr>
  <tr><td><code>&lt;Link&gt;</code></td><td>Navigate without page reload</td></tr>
  <tr><td><code>&lt;Outlet&gt;</code></td><td>Render nested route&rsquo;s component</td></tr>
  <tr><td><code>&lt;Navigate&gt;</code></td><td>Programmatic redirect</td></tr>
</table>

<p><strong>Hooks for routing data and navigation:</strong></p>

<table>
  <tr><th>Hook</th><th>Returns</th></tr>
  <tr><td><code>useParams</code></td><td>URL parameters (e.g., <code>:id</code>)</td></tr>
  <tr><td><code>useNavigate</code></td><td>Programmatic navigation function</td></tr>
  <tr><td><code>useLocation</code></td><td>Current URL info (pathname, search, hash)</td></tr>
  <tr><td><code>useSearchParams</code></td><td>Read/write query string</td></tr>
  <tr><td><code>useMatch</code></td><td>Check if current URL matches a pattern</td></tr>
</table>

<pre><code>function ProductDetail() {
  const { id } = useParams();        // /products/123 -&gt; id = "123"
  const navigate = useNavigate();

  return (
    &lt;div&gt;
      &lt;h1&gt;Product {id}&lt;/h1&gt;
      &lt;button onClick={() =&gt; navigate("/products")}&gt;
        Back to list
      &lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>2026 note &mdash; deprecated APIs to avoid</strong>: <code>useHistory</code> (use <code>useNavigate</code>), <code>&lt;Switch&gt;</code> (use <code>&lt;Routes&gt;</code>), <code>useRouteMatch</code> (use <code>useMatch</code>). Older tutorials still show these.</p>

<p>Alternatives in 2026: <strong>TanStack Router</strong> (type-safe routing, very popular for new projects), <strong>Next.js App Router</strong> (file-based routing for Next.js apps), <strong>Wouter</strong> (minimal, ~2KB).</p>
'''

ANSWERS[58] = r'''
<p>Nested routes let you compose layouts &mdash; a parent route renders shared UI (like a layout with sidebar/header), and child routes fill in the content area via <code>&lt;Outlet&gt;</code>.</p>

<pre><code>import { Routes, Route, Outlet, Link } from "react-router-dom";

// Layout with shared sidebar/header
function DashboardLayout() {
  return (
    &lt;div className="dashboard"&gt;
      &lt;aside&gt;
        &lt;Link to="/dashboard/overview"&gt;Overview&lt;/Link&gt;
        &lt;Link to="/dashboard/users"&gt;Users&lt;/Link&gt;
        &lt;Link to="/dashboard/settings"&gt;Settings&lt;/Link&gt;
      &lt;/aside&gt;
      &lt;main&gt;
        &lt;Outlet /&gt;          {/* nested route renders here */}
      &lt;/main&gt;
    &lt;/div&gt;
  );
}

function App() {
  return (
    &lt;Routes&gt;
      &lt;Route path="/" element={&lt;Home /&gt;} /&gt;

      &lt;Route path="/dashboard" element={&lt;DashboardLayout /&gt;}&gt;
        &lt;Route index element={&lt;DashboardHome /&gt;} /&gt;
        &lt;Route path="overview" element={&lt;Overview /&gt;} /&gt;
        &lt;Route path="users" element={&lt;Users /&gt;} /&gt;
        &lt;Route path="users/:id" element={&lt;UserDetail /&gt;} /&gt;
        &lt;Route path="settings" element={&lt;Settings /&gt;} /&gt;
      &lt;/Route&gt;
    &lt;/Routes&gt;
  );
}</code></pre>

<p><strong>How URL matching works:</strong></p>

<table>
  <tr><th>URL</th><th>Renders</th></tr>
  <tr><td><code>/dashboard</code></td><td>DashboardLayout + DashboardHome (index route)</td></tr>
  <tr><td><code>/dashboard/overview</code></td><td>DashboardLayout + Overview</td></tr>
  <tr><td><code>/dashboard/users</code></td><td>DashboardLayout + Users</td></tr>
  <tr><td><code>/dashboard/users/42</code></td><td>DashboardLayout + UserDetail (id="42")</td></tr>
</table>

<p><strong>Three key concepts:</strong></p>
<ul>
  <li><strong><code>&lt;Outlet /&gt;</code></strong> &mdash; placeholder where child routes render. Without it, nested routes have nowhere to display.</li>
  <li><strong>Index routes</strong> &mdash; <code>&lt;Route index .../&gt;</code> matches when you&rsquo;re at the parent path with no child segment.</li>
  <li><strong>Relative paths</strong> &mdash; child <code>path="users"</code> resolves to <code>/dashboard/users</code> (joined with parent).</li>
</ul>

<p><strong>Multi-level nesting</strong> works the same way:</p>

<pre><code>&lt;Route path="/admin" element={&lt;AdminLayout /&gt;}&gt;
  &lt;Route path="users" element={&lt;UsersLayout /&gt;}&gt;
    &lt;Route index element={&lt;UsersList /&gt;} /&gt;
    &lt;Route path=":id" element={&lt;UserDetail /&gt;} /&gt;
    &lt;Route path=":id/edit" element={&lt;EditUser /&gt;} /&gt;
  &lt;/Route&gt;
&lt;/Route&gt;</code></pre>

<p>Each level renders its layout; the deepest matching route fills the innermost <code>&lt;Outlet /&gt;</code>. Each layout can have its own header, sidebar, breadcrumbs.</p>

<p><strong>Why this pattern is powerful</strong>: layouts are co-located with their routes; users navigating between sibling routes don&rsquo;t lose layout state (sidebar scroll position, etc.); URL structure mirrors UI hierarchy.</p>
'''

ANSWERS[59] = r'''
<p>Both routers handle client-side routing in React Router; they differ in <strong>how they encode the URL</strong>.</p>

<table>
  <tr><th></th><th><code>&lt;BrowserRouter&gt;</code></th><th><code>&lt;HashRouter&gt;</code></th></tr>
  <tr><td>URL style</td><td><code>example.com/about</code></td><td><code>example.com/#/about</code></td></tr>
  <tr><td>Uses</td><td>HTML5 History API (pushState)</td><td>URL fragment (hash)</td></tr>
  <tr><td>Server config required?</td><td>Yes &mdash; server must serve index.html for all routes</td><td>No &mdash; works with any static host</td></tr>
  <tr><td>SEO friendly</td><td>Yes</td><td>No (search engines often ignore hash)</td></tr>
  <tr><td>Recommended for</td><td>Production apps, SPAs with backends</td><td>Static sites without server control</td></tr>
</table>

<p><strong>BrowserRouter &mdash; the default choice:</strong></p>

<pre><code>import { BrowserRouter } from "react-router-dom";

&lt;BrowserRouter&gt;
  &lt;App /&gt;
&lt;/BrowserRouter&gt;</code></pre>

<p>Clean URLs, full SEO support &mdash; but the server needs to send <code>index.html</code> for any path that doesn&rsquo;t match a static file. Otherwise refreshing on <code>/about</code> returns a 404.</p>

<p><strong>Server config examples:</strong></p>

<pre><code># nginx
location / {
  try_files $uri $uri/ /index.html;
}

# netlify (_redirects file)
/*    /index.html   200

# vercel.json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }</code></pre>

<p><strong>HashRouter &mdash; for restricted hosts:</strong></p>

<pre><code>import { HashRouter } from "react-router-dom";

&lt;HashRouter&gt;
  &lt;App /&gt;
&lt;/HashRouter&gt;</code></pre>

<p>The <code>#</code> fragment is purely client-side &mdash; the server only ever sees <code>example.com/</code>, so any host serving <code>index.html</code> works. Use this on GitHub Pages (without custom config), restricted CDNs, or static file shares where you can&rsquo;t configure URL rewrites.</p>

<p><strong>2026 recommendation:</strong> use <code>BrowserRouter</code> almost always. Modern hosts (Netlify, Vercel, AWS Amplify, Cloudflare Pages) support SPA fallback rewrites natively &mdash; no manual config needed. <code>HashRouter</code> is a fallback for legacy hosts where you can&rsquo;t configure the server.</p>
'''

ANSWERS[60] = r'''
<p>React Router supports two primary redirect patterns: <strong><code>&lt;Navigate&gt;</code> component</strong> for declarative redirects in JSX, and <strong><code>useNavigate</code> hook</strong> for programmatic redirects in event handlers or effects.</p>

<p><strong>Declarative &mdash; <code>&lt;Navigate&gt;</code>:</strong></p>

<pre><code>import { Navigate } from "react-router-dom";

function ProtectedRoute({ children, isAuthenticated }) {
  if (!isAuthenticated) {
    return &lt;Navigate to="/login" replace /&gt;;
  }
  return children;
}

// Use in routes
&lt;Route path="/dashboard" element={
  &lt;ProtectedRoute isAuthenticated={user !== null}&gt;
    &lt;Dashboard /&gt;
  &lt;/ProtectedRoute&gt;
} /&gt;</code></pre>

<p>Renders nothing visually &mdash; just triggers the navigation when mounted.</p>

<p><strong>Programmatic &mdash; <code>useNavigate</code>:</strong></p>

<pre><code>import { useNavigate } from "react-router-dom";

function LoginForm() {
  const navigate = useNavigate();

  const handleLogin = async (e) =&gt; {
    e.preventDefault();
    const success = await login();
    if (success) {
      navigate("/dashboard");
    }
  };

  return &lt;form onSubmit={handleLogin}&gt;...&lt;/form&gt;;
}</code></pre>

<p><strong>The <code>replace</code> prop &mdash; understanding history:</strong></p>

<table>
  <tr><th>Default (push)</th><th><code>replace: true</code></th></tr>
  <tr><td>Adds entry to history stack</td><td>Replaces current entry</td></tr>
  <tr><td>Back button returns to previous</td><td>Back button skips this redirect</td></tr>
  <tr><td>Use for normal navigation</td><td>Use for redirects (login, logout, post-submit)</td></tr>
</table>

<pre><code>navigate("/dashboard");                  // history: [...prev, /dashboard]
navigate("/dashboard", { replace: true }); // history: [...prev replaced]</code></pre>

<p><strong>Common redirect patterns:</strong></p>

<pre><code>// After login
navigate("/dashboard", { replace: true });

// Pass state along
navigate("/checkout", { state: { from: "cart" } });

// Go back
navigate(-1);

// Go forward
navigate(1);

// Replace whole URL with query string
navigate("/search?q=react", { replace: true });</code></pre>

<p><strong>Reading the redirect destination</strong> &mdash; common pattern for "redirect to login then back":</p>

<pre><code>function ProtectedRoute({ children, isAuth }) {
  const location = useLocation();
  if (!isAuth) {
    return &lt;Navigate to="/login" state={{ from: location }} replace /&gt;;
  }
  return children;
}

function LoginForm() {
  const location = useLocation();
  const navigate = useNavigate();
  const from = location.state?.from?.pathname || "/dashboard";

  const handleLogin = async () =&gt; {
    await login();
    navigate(from, { replace: true });   // back to where they came from
  };
}</code></pre>

<p><strong>Deprecated</strong>: <code>useHistory().push()</code> from React Router v5. Use <code>useNavigate()</code> in v6+.</p>
'''

ANSWERS[61] = r'''
<p>Route parameters are URL segments captured as variables &mdash; defined with a colon in the path pattern (<code>:id</code>) and read with the <code>useParams</code> hook.</p>

<pre><code>import { Routes, Route, useParams } from "react-router-dom";

function App() {
  return (
    &lt;Routes&gt;
      &lt;Route path="/products/:id" element={&lt;ProductDetail /&gt;} /&gt;
      &lt;Route path="/users/:userId/posts/:postId" element={&lt;PostDetail /&gt;} /&gt;
    &lt;/Routes&gt;
  );
}

function ProductDetail() {
  const { id } = useParams();
  // /products/42 -&gt; id = "42"
  return &lt;h1&gt;Product {id}&lt;/h1&gt;;
}

function PostDetail() {
  const { userId, postId } = useParams();
  // /users/7/posts/42 -&gt; userId = "7", postId = "42"
  return &lt;h1&gt;Post {postId} by user {userId}&lt;/h1&gt;;
}</code></pre>

<p><strong>Important: params are always strings.</strong> Convert to numbers if needed:</p>

<pre><code>const { id } = useParams();
const idNum = Number(id);   // or parseInt(id, 10)</code></pre>

<p><strong>Optional segments &mdash; question mark suffix:</strong></p>

<pre><code>&lt;Route path="/products/:id?" element={&lt;ProductDetail /&gt;} /&gt;
// matches /products AND /products/42
// when missing, useParams returns id: undefined</code></pre>

<p><strong>Splat / wildcard parameters</strong> &mdash; capture the rest of the URL:</p>

<pre><code>&lt;Route path="/files/*" element={&lt;FileViewer /&gt;} /&gt;

function FileViewer() {
  const params = useParams();
  const path = params["*"];   // /files/folder/sub/file.txt -&gt; "folder/sub/file.txt"
}</code></pre>

<p><strong>Query strings vs route params:</strong></p>

<table>
  <tr><th></th><th>Route param</th><th>Query string</th></tr>
  <tr><td>Example</td><td><code>/products/42</code></td><td><code>/products?id=42</code></td></tr>
  <tr><td>Read with</td><td><code>useParams()</code></td><td><code>useSearchParams()</code></td></tr>
  <tr><td>Use for</td><td>Required identifiers</td><td>Optional filters, sort, page</td></tr>
</table>

<pre><code>import { useSearchParams } from "react-router-dom";

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const sort = searchParams.get("sort") || "name";
  const page = Number(searchParams.get("page") || 1);

  return (
    &lt;&gt;
      &lt;button onClick={() =&gt; setSearchParams({ sort: "price", page: 1 })}&gt;
        Sort by price
      &lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Generating param URLs from data</strong>:</p>

<pre><code>{products.map(p =&gt; (
  &lt;Link key={p.id} to={`/products/${p.id}`}&gt;
    {p.name}
  &lt;/Link&gt;
))}</code></pre>

<p>Use template literals to embed values; modern code rarely needs <code>generatePath()</code> &mdash; the explicit string is clearer for most cases.</p>
'''

ANSWERS[62] = r'''
<p>The <code>&lt;Link&gt;</code> component navigates between routes <strong>without a full page reload</strong>. Behind the scenes, it&rsquo;s an <code>&lt;a&gt;</code> tag with <code>onClick</code> that intercepts the navigation and uses React Router&rsquo;s history.</p>

<pre><code>import { Link } from "react-router-dom";

function Nav() {
  return (
    &lt;nav&gt;
      &lt;Link to="/"&gt;Home&lt;/Link&gt;
      &lt;Link to="/about"&gt;About&lt;/Link&gt;
      &lt;Link to="/products"&gt;Products&lt;/Link&gt;
      &lt;Link to="/products/42"&gt;Specific product&lt;/Link&gt;
    &lt;/nav&gt;
  );
}</code></pre>

<p><strong>Why use <code>&lt;Link&gt;</code> instead of <code>&lt;a&gt;</code>:</strong></p>

<table>
  <tr><th><code>&lt;a href&gt;</code></th><th><code>&lt;Link to&gt;</code></th></tr>
  <tr><td>Triggers full page reload</td><td>Uses client-side routing &mdash; no reload</td></tr>
  <tr><td>App state lost</td><td>App state preserved</td></tr>
  <tr><td>Slow navigation</td><td>Fast (no network round-trip)</td></tr>
  <tr><td>Re-fetches all assets</td><td>Reuses already-loaded code/data</td></tr>
</table>

<p>For external URLs, <code>&lt;a&gt;</code> is correct (those need full reload anyway). For internal app routes, always use <code>&lt;Link&gt;</code>.</p>

<p><strong>Common props:</strong></p>

<pre><code>// Pass state to the destination
&lt;Link to="/details" state={{ from: "search" }}&gt;Details&lt;/Link&gt;

// Replace history instead of pushing
&lt;Link to="/login" replace&gt;Login&lt;/Link&gt;

// Open in new tab — falls back to plain &lt;a&gt; behavior
&lt;Link to="/page" target="_blank" rel="noopener"&gt;New tab&lt;/Link&gt;

// Relative navigation
&lt;Link to="settings"&gt;...&lt;/Link&gt;        // relative to current
&lt;Link to="/settings"&gt;...&lt;/Link&gt;       // absolute</code></pre>

<p><strong><code>&lt;NavLink&gt;</code> &mdash; for active styling:</strong></p>

<pre><code>import { NavLink } from "react-router-dom";

&lt;NavLink
  to="/about"
  className={({ isActive }) =&gt; isActive ? "active" : ""}
&gt;
  About
&lt;/NavLink&gt;</code></pre>

<p><code>NavLink</code> automatically applies an <code>active</code> class when the URL matches &mdash; perfect for navigation menus where you want to highlight the current page.</p>

<p><strong>Programmatic alternative</strong> &mdash; <code>useNavigate</code> for navigations from event handlers, not user clicks:</p>

<pre><code>const navigate = useNavigate();
navigate("/dashboard");          // imperative redirect</code></pre>

<p>Use <code>&lt;Link&gt;</code> for user-initiated navigation; <code>useNavigate</code> for programmatic (after form submit, login success, etc.).</p>
'''

ANSWERS[63] = r'''
<p><strong><code>useHistory</code> was the React Router v5 hook for programmatic navigation</strong> &mdash; but it&rsquo;s <strong>deprecated and removed</strong> in v6 and later. The current equivalent is <code>useNavigate</code>.</p>

<p><strong>Old (v5) &mdash; <code>useHistory</code>:</strong></p>

<pre><code>// React Router v5 — deprecated
import { useHistory } from "react-router-dom";

function LoginForm() {
  const history = useHistory();

  const handleLogin = () =&gt; {
    history.push("/dashboard");
    history.replace("/login");
    history.goBack();
    history.goForward();
  };
}</code></pre>

<p><strong>Modern (v6+) &mdash; <code>useNavigate</code>:</strong></p>

<pre><code>import { useNavigate } from "react-router-dom";

function LoginForm() {
  const navigate = useNavigate();

  const handleLogin = () =&gt; {
    navigate("/dashboard");                          // push
    navigate("/login", { replace: true });           // replace
    navigate(-1);                                    // back
    navigate(1);                                     // forward
  };
}</code></pre>

<p><strong>Migration map:</strong></p>

<table>
  <tr><th>Old (v5)</th><th>New (v6+)</th></tr>
  <tr><td><code>history.push("/path")</code></td><td><code>navigate("/path")</code></td></tr>
  <tr><td><code>history.replace("/path")</code></td><td><code>navigate("/path", { replace: true })</code></td></tr>
  <tr><td><code>history.goBack()</code></td><td><code>navigate(-1)</code></td></tr>
  <tr><td><code>history.goForward()</code></td><td><code>navigate(1)</code></td></tr>
  <tr><td><code>history.go(2)</code></td><td><code>navigate(2)</code></td></tr>
  <tr><td><code>history.location</code></td><td><code>useLocation()</code></td></tr>
</table>

<p><strong>Pass state on navigation</strong> &mdash; same pattern in both:</p>

<pre><code>// Old
history.push("/products", { from: "search" });

// New
navigate("/products", { state: { from: "search" } });

// Read it
function Products() {
  const location = useLocation();
  const from = location.state?.from;
}</code></pre>

<p><strong>If you&rsquo;re working in a v5 codebase</strong>: many old codebases still use <code>useHistory</code>; the migration to v6+ is straightforward but requires updating import paths and adjusting <code>push</code>/<code>replace</code> calls.</p>

<p><strong>For interview answers</strong>: mention that <code>useHistory</code> existed in v5, then explain it&rsquo;s replaced by <code>useNavigate</code> in v6+. Demonstrating awareness of the breaking change is valuable &mdash; many interviewers test whether candidates know this.</p>

<p><strong>2026 status</strong>: React Router v7 (current) only supports the modern hooks. <code>useHistory</code> doesn&rsquo;t exist; even older tutorials should be considered out of date.</p>
'''

ANSWERS[64] = r'''
<p>The <code>useParams</code> hook returns an <strong>object containing all route parameters</strong> defined in the current route&rsquo;s path pattern. It&rsquo;s how components read dynamic segments from the URL.</p>

<pre><code>import { Routes, Route, useParams } from "react-router-dom";

function App() {
  return (
    &lt;Routes&gt;
      &lt;Route path="/users/:userId" element={&lt;UserProfile /&gt;} /&gt;
      &lt;Route path="/blog/:year/:month/:slug" element={&lt;BlogPost /&gt;} /&gt;
    &lt;/Routes&gt;
  );
}

function UserProfile() {
  const { userId } = useParams();
  // URL /users/42 -&gt; userId = "42"

  return &lt;h1&gt;User {userId}&lt;/h1&gt;;
}

function BlogPost() {
  const { year, month, slug } = useParams();
  // URL /blog/2026/04/hello-world -&gt; year="2026", month="04", slug="hello-world"
}</code></pre>

<p><strong>Key behaviors to know:</strong></p>
<ul>
  <li><strong>All values are strings</strong> &mdash; even numeric-looking ones. Convert with <code>Number()</code> when you need a number.</li>
  <li><strong>Returns an empty object</strong> if no params in the route &mdash; never returns <code>undefined</code>.</li>
  <li><strong>Updates reactively</strong> &mdash; component re-renders when the URL changes (e.g., navigating from <code>/users/1</code> to <code>/users/2</code>).</li>
</ul>

<p><strong>Typical usage with data fetching:</strong></p>

<pre><code>function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);

  useEffect(() =&gt; {
    fetch(`/api/products/${id}`)
      .then(r =&gt; r.json())
      .then(setProduct);
  }, [id]);   // re-fetch when id changes

  if (!product) return &lt;p&gt;Loading...&lt;/p&gt;;
  return &lt;h1&gt;{product.name}&lt;/h1&gt;;
}</code></pre>

<p><strong>The id changes</strong> trigger re-fetch automatically &mdash; <code>useEffect</code> with <code>[id]</code> dep array runs the effect again on each new id.</p>

<p><strong>TypeScript usage</strong>:</p>

<pre><code>import { useParams } from "react-router-dom";

function UserProfile() {
  const { userId } = useParams&lt;{ userId: string }&gt;();
  // userId is typed as string | undefined
}</code></pre>

<p><strong>Common gotcha &mdash; missing param when route doesn&rsquo;t match:</strong></p>

<pre><code>// On route /products (no :id)
const { id } = useParams();
// id is undefined — NOT an empty string

if (!id) return &lt;Navigate to="/" /&gt;;   // guard against missing</code></pre>

<p><strong>Splat / wildcard params</strong>:</p>

<pre><code>// Route: path="/files/*"
const params = useParams();
const restPath = params["*"];   // /files/folder/sub/file.txt -&gt; "folder/sub/file.txt"</code></pre>

<p>Useful for file viewers, deeply-nested paths, or catch-all routes.</p>
'''

ANSWERS[65] = r'''
<p><strong><code>useRouteMatch</code> was the v5 hook</strong> for matching URL patterns against the current location &mdash; useful for nested-route logic and conditional rendering. It&rsquo;s <strong>deprecated and removed</strong> in v6+; the modern equivalent is <strong><code>useMatch</code></strong>.</p>

<p><strong>Old (v5) &mdash; <code>useRouteMatch</code>:</strong></p>

<pre><code>// React Router v5 — deprecated
import { useRouteMatch } from "react-router-dom";

function ProfileTabs() {
  const match = useRouteMatch();
  // match.path  -&gt; "/profile"     (the route pattern)
  // match.url   -&gt; "/profile"     (current URL)
  // match.params -&gt; {}
  // match.isExact -&gt; true

  return (
    &lt;&gt;
      &lt;Link to={`${match.url}/posts`}&gt;Posts&lt;/Link&gt;
      &lt;Link to={`${match.url}/photos`}&gt;Photos&lt;/Link&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Modern (v6+) &mdash; <code>useMatch</code>:</strong></p>

<pre><code>import { useMatch, useLocation } from "react-router-dom";

function NavItem({ to, children }) {
  const match = useMatch(to);   // returns match object or null
  return (
    &lt;Link to={to} className={match ? "active" : ""}&gt;
      {children}
    &lt;/Link&gt;
  );
}

// More common: just use NavLink for active styling
import { NavLink } from "react-router-dom";

&lt;NavLink to="/about" className={({ isActive }) =&gt; isActive ? "active" : ""}&gt;
  About
&lt;/NavLink&gt;</code></pre>

<p><strong>Comparison:</strong></p>

<table>
  <tr><th>v5 (<code>useRouteMatch</code>)</th><th>v6+ (<code>useMatch</code>)</th></tr>
  <tr><td>Returns match for current route always</td><td>Takes a pattern; returns match or <code>null</code></td></tr>
  <tr><td>Used for relative URL building</td><td>Used for boolean checks (active, etc.)</td></tr>
  <tr><td>Returns <code>{ path, url, params, isExact }</code></td><td>Returns <code>{ pathname, params, pattern }</code> or <code>null</code></td></tr>
</table>

<p><strong>Common v5 use cases and their v6+ equivalents:</strong></p>

<table>
  <tr><th>Goal</th><th>v5</th><th>v6+</th></tr>
  <tr><td>Build nested URLs</td><td><code>${match.url}/posts</code></td><td>Use relative <code>&lt;Link to="posts"&gt;</code></td></tr>
  <tr><td>Active link styling</td><td>Compare <code>match</code> manually</td><td><code>&lt;NavLink&gt;</code> with <code>isActive</code></td></tr>
  <tr><td>Conditional render</td><td><code>useRouteMatch("/admin")</code></td><td><code>useMatch("/admin")</code></td></tr>
  <tr><td>Get current pathname</td><td><code>match.url</code></td><td><code>useLocation().pathname</code></td></tr>
</table>

<p><strong>Realistic 2026 advice</strong>: most code that previously needed <code>useRouteMatch</code> doesn&rsquo;t need <code>useMatch</code> either &mdash; <code>NavLink</code>, relative <code>&lt;Link&gt;</code>, and <code>useLocation</code> handle the common cases more cleanly. Reach for <code>useMatch</code> only for explicit pattern checks (e.g., "are we currently on any admin route?").</p>

<pre><code>function AdminBanner() {
  const match = useMatch("/admin/*");
  if (!match) return null;
  return &lt;div&gt;Admin mode active&lt;/div&gt;;
}</code></pre>
'''

ANSWERS[66] = r'''
<p>Conditional navigation means redirecting based on app state &mdash; auth status, user permissions, feature flags, or completed onboarding. The cleanest pattern is a <strong>route guard component</strong> that wraps protected routes.</p>

<p><strong>Auth-protected routes:</strong></p>

<pre><code>import { Navigate, useLocation } from "react-router-dom";

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    // Save where they were trying to go, send to login
    return &lt;Navigate to="/login" state={{ from: location }} replace /&gt;;
  }
  return children;
}

// Use in route definitions
&lt;Routes&gt;
  &lt;Route path="/login" element={&lt;Login /&gt;} /&gt;
  &lt;Route path="/dashboard" element={
    &lt;ProtectedRoute&gt;
      &lt;Dashboard /&gt;
    &lt;/ProtectedRoute&gt;
  } /&gt;
&lt;/Routes&gt;</code></pre>

<p><strong>Login form &mdash; redirect back after login:</strong></p>

<pre><code>function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const handleLogin = async () =&gt; {
    await login();
    navigate(from, { replace: true });
  };
}</code></pre>

<p><strong>Role-based access:</strong></p>

<pre><code>function RoleGate({ children, requiredRole }) {
  const { user } = useAuth();
  if (!user) return &lt;Navigate to="/login" replace /&gt;;
  if (user.role !== requiredRole)
    return &lt;Navigate to="/forbidden" replace /&gt;;
  return children;
}

&lt;Route path="/admin" element={
  &lt;RoleGate requiredRole="admin"&gt;
    &lt;AdminPanel /&gt;
  &lt;/RoleGate&gt;
} /&gt;</code></pre>

<p><strong>Programmatic redirect after action:</strong></p>

<pre><code>function CheckoutForm() {
  const navigate = useNavigate();

  const handleSubmit = async () =&gt; {
    const result = await placeOrder();
    if (result.success) {
      navigate(`/orders/${result.orderId}`, { replace: true });
    } else if (result.requiresPayment) {
      navigate("/payment", { state: { order: result.order } });
    } else {
      navigate("/error", { state: { error: result.error } });
    }
  };
}</code></pre>

<p><strong>Common conditional patterns:</strong></p>

<table>
  <tr><th>Condition</th><th>Approach</th></tr>
  <tr><td>Not logged in</td><td>Redirect to login (save destination in state)</td></tr>
  <tr><td>Wrong role</td><td>Redirect to /forbidden</td></tr>
  <tr><td>Onboarding incomplete</td><td>Redirect to /onboarding</td></tr>
  <tr><td>Subscription expired</td><td>Redirect to /upgrade</td></tr>
  <tr><td>Form not yet submitted</td><td>Redirect back with error toast</td></tr>
</table>

<p><strong>Loaders (React Router v6.4+ data API)</strong> handle this even better &mdash; you can throw a redirect from a loader function before the component even renders:</p>

<pre><code>import { redirect } from "react-router-dom";

const dashboardLoader = async () =&gt; {
  const user = await getCurrentUser();
  if (!user) throw redirect("/login");
  return user;
};

&lt;Route path="/dashboard" loader={dashboardLoader} element={&lt;Dashboard /&gt;} /&gt;</code></pre>

<p>Loaders run before render &mdash; no flash of "loading then redirect" UX. They&rsquo;re the modern recommended pattern in React Router v6.4+ and v7.</p>
'''

ANSWERS[67] = r'''
<p><strong>Redux is a predictable state container</strong> for JavaScript apps &mdash; not just React, though it&rsquo;s commonly used with React via <strong>react-redux</strong>. It centralizes app state in a single store, makes updates predictable through pure reducer functions, and provides a clear data flow: action &rarr; reducer &rarr; new state &rarr; UI.</p>

<p><strong>Why Redux exists:</strong></p>
<ul>
  <li><strong>Centralized state</strong> &mdash; instead of scattering state across components and lifting it up trees, all app state lives in one store.</li>
  <li><strong>Predictable updates</strong> &mdash; the only way to change state is dispatching actions; reducers are pure functions.</li>
  <li><strong>Time-travel debugging</strong> &mdash; Redux DevTools lets you replay actions, inspect every state transition.</li>
  <li><strong>Cross-component sharing</strong> &mdash; any component can read or update state without prop drilling.</li>
</ul>

<p><strong>Core concepts:</strong></p>

<table>
  <tr><th>Concept</th><th>What it is</th></tr>
  <tr><td>Store</td><td>The single source of truth holding all app state</td></tr>
  <tr><td>Action</td><td>A plain object describing what happened: <code>{ type, payload }</code></td></tr>
  <tr><td>Reducer</td><td>Pure function: <code>(state, action) =&gt; new state</code></td></tr>
  <tr><td>Dispatch</td><td>Sends an action to the store; triggers reducers</td></tr>
  <tr><td>Selector</td><td>Function that reads a specific slice from the store</td></tr>
</table>

<p><strong>Modern usage &mdash; Redux Toolkit (RTK)</strong>, the official, recommended way to write Redux:</p>

<pre><code>import { configureStore, createSlice } from "@reduxjs/toolkit";

const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) =&gt; { state.value += 1; },
    decrement: (state) =&gt; { state.value -= 1; },
    incrementByAmount: (state, action) =&gt; {
      state.value += action.payload;
    }
  }
});

export const { increment, decrement, incrementByAmount } = counterSlice.actions;
export const store = configureStore({ reducer: { counter: counterSlice.reducer } });</code></pre>

<p><strong>Compared to classic Redux</strong>: RTK eliminates 80% of the boilerplate &mdash; no manual action types, no switch statements in reducers, mutations look mutable but are made immutable by Immer under the hood.</p>

<p><strong>2026 reality &mdash; Redux is no longer the default for new apps</strong>:</p>

<table>
  <tr><th>State type</th><th>Recommended tool</th></tr>
  <tr><td>Server data (API responses)</td><td>TanStack Query / SWR</td></tr>
  <tr><td>Lightweight global state</td><td>Zustand / Jotai</td></tr>
  <tr><td>Complex global state with team familiarity</td><td>Redux Toolkit</td></tr>
  <tr><td>Local component state</td><td><code>useState</code> / <code>useReducer</code></td></tr>
</table>

<p>Redux remains common in large existing codebases. For new projects in 2026, default to simpler tools first; reach for Redux only when its action-log + middleware ecosystem genuinely helps.</p>
'''

ANSWERS[68] = r'''
<p>Integrating Redux with a React app uses the <strong>react-redux</strong> library &mdash; it provides the <code>&lt;Provider&gt;</code> component to make the store available to all children, plus hooks (<code>useSelector</code>, <code>useDispatch</code>) for reading and updating state.</p>

<p><strong>Step 1 &mdash; install:</strong></p>

<pre><code>npm install @reduxjs/toolkit react-redux</code></pre>

<p><strong>Step 2 &mdash; create slices and store:</strong></p>

<pre><code>// store/counterSlice.js
import { createSlice } from "@reduxjs/toolkit";

const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment: (state) =&gt; { state.value += 1; },
    decrement: (state) =&gt; { state.value -= 1; }
  }
});

export const { increment, decrement } = counterSlice.actions;
export default counterSlice.reducer;</code></pre>

<pre><code>// store/index.js
import { configureStore } from "@reduxjs/toolkit";
import counterReducer from "./counterSlice";

export const store = configureStore({
  reducer: {
    counter: counterReducer
  }
});</code></pre>

<p><strong>Step 3 &mdash; provide the store to your app:</strong></p>

<pre><code>// main.jsx (Vite) or index.js (CRA)
import { Provider } from "react-redux";
import { store } from "./store";

ReactDOM.createRoot(document.getElementById("root")).render(
  &lt;Provider store={store}&gt;
    &lt;App /&gt;
  &lt;/Provider&gt;
);</code></pre>

<p><strong>Step 4 &mdash; use state and dispatch in components:</strong></p>

<pre><code>import { useSelector, useDispatch } from "react-redux";
import { increment, decrement } from "./store/counterSlice";

function Counter() {
  const count = useSelector((state) =&gt; state.counter.value);
  const dispatch = useDispatch();

  return (
    &lt;&gt;
      &lt;p&gt;Count: {count}&lt;/p&gt;
      &lt;button onClick={() =&gt; dispatch(increment())}&gt;+&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch(decrement())}&gt;-&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>That&rsquo;s the entire integration</strong>: any component anywhere in the tree can now read from the store via <code>useSelector</code> and dispatch actions via <code>useDispatch</code>. No props passed down; no lifting state up.</p>

<p><strong>Project structure (typical):</strong></p>

<pre><code>src/
├── store/
│   ├── index.js          ← configureStore + combine reducers
│   ├── counterSlice.js
│   ├── userSlice.js
│   └── productsSlice.js
├── components/
│   ├── Counter.jsx
│   └── ...
└── main.jsx              ← &lt;Provider&gt; wraps &lt;App /&gt;</code></pre>

<p><strong>Don&rsquo;t use the old <code>connect</code> HOC</strong> &mdash; it&rsquo;s legacy. The hooks API (<code>useSelector</code>, <code>useDispatch</code>) is the modern standard, cleaner, and works better with TypeScript.</p>

<p><strong>For TypeScript</strong>: define typed hooks once and import them everywhere &mdash; gives full type inference for state and actions.</p>
'''

ANSWERS[69] = r'''
<p>An <strong>action</strong> in Redux is a plain JavaScript object that describes <strong>what happened</strong>. Actions are the only way to change state in a Redux store &mdash; you dispatch an action, and reducers respond to it.</p>

<p><strong>Action shape</strong>:</p>

<pre><code>// Standard structure
{
  type: "TODO_ADDED",          // string identifier (required)
  payload: { id: 1, text: "Buy milk" }   // data (optional)
}

// Common variations
{ type: "INCREMENT" }                          // no payload
{ type: "USER_LOGGED_IN", payload: { user } }   // with data
{ type: "FETCH_FAILED", error: true,
  payload: new Error("Network error") }         // error flag</code></pre>

<p>The <code>type</code> field is required &mdash; usually a unique string. The <code>payload</code> carries the data needed to make the change. By convention (Flux Standard Action), errors set <code>error: true</code>.</p>

<p><strong>Action creators</strong> &mdash; functions that return action objects:</p>

<pre><code>// Manual action creator (classic Redux)
function todoAdded(text) {
  return {
    type: "TODO_ADDED",
    payload: { id: Date.now(), text, done: false }
  };
}

// Use it
dispatch(todoAdded("Buy milk"));</code></pre>

<p><strong>With Redux Toolkit (RTK)</strong> &mdash; <code>createSlice</code> generates action creators automatically:</p>

<pre><code>const todosSlice = createSlice({
  name: "todos",
  initialState: [],
  reducers: {
    todoAdded(state, action) {
      state.push({ id: Date.now(), text: action.payload, done: false });
    },
    todoToggled(state, action) {
      const todo = state.find(t =&gt; t.id === action.payload);
      if (todo) todo.done = !todo.done;
    },
    todoRemoved(state, action) {
      return state.filter(t =&gt; t.id !== action.payload);
    }
  }
});

// RTK auto-generates action creators
export const { todoAdded, todoToggled, todoRemoved } = todosSlice.actions;

// Use them like before
dispatch(todoAdded("Buy milk"));      // { type: "todos/todoAdded", payload: "Buy milk" }
dispatch(todoToggled(123));            // { type: "todos/todoToggled", payload: 123 }</code></pre>

<p><strong>RTK&rsquo;s naming convention</strong>: action types are auto-prefixed with the slice name (<code>todos/todoAdded</code>), avoiding collisions across slices.</p>

<p><strong>Best practices for actions:</strong></p>
<ul>
  <li><strong>Describe events, not setters</strong>: <code>USER_LOGGED_IN</code> is better than <code>SET_USER</code>. The reducer decides what state changes happen.</li>
  <li><strong>Action types are domain events</strong> &mdash; should be readable in the time-travel debugger as a story of "what happened."</li>
  <li><strong>Keep payload serializable</strong> &mdash; no functions, no class instances. Plain data only (Date is borderline; ISO strings are safer).</li>
  <li><strong>One action per business event</strong> &mdash; not multiple sequential dispatches when one would do.</li>
</ul>

<p><strong>Async actions</strong> use middleware (Thunk, Saga) &mdash; covered in Q76-78.</p>
'''

ANSWERS[70] = r'''
<p>A <strong>reducer</strong> is a pure function that takes the <strong>current state</strong> and an <strong>action</strong>, and returns the <strong>new state</strong>. The signature is always: <code>(state, action) =&gt; newState</code>. Reducers are the only place state changes happen in Redux.</p>

<p><strong>Classic Redux reducer:</strong></p>

<pre><code>const initialState = { count: 0 };

function counterReducer(state = initialState, action) {
  switch (action.type) {
    case "INCREMENT":
      return { ...state, count: state.count + 1 };
    case "DECREMENT":
      return { ...state, count: state.count - 1 };
    case "INCREMENT_BY":
      return { ...state, count: state.count + action.payload };
    default:
      return state;       // unknown action — return current state unchanged
  }
}</code></pre>

<p><strong>Three rules every reducer must follow:</strong></p>

<table>
  <tr><th>Rule</th><th>Why</th></tr>
  <tr><td>Pure function</td><td>Same inputs always produce same outputs &mdash; predictable, testable</td></tr>
  <tr><td>No mutation of state</td><td>Return new objects; don&rsquo;t modify the input state</td></tr>
  <tr><td>No side effects</td><td>No API calls, no random values, no <code>Date.now()</code> &mdash; effects belong in middleware</td></tr>
</table>

<p><strong>Why immutability matters</strong>: Redux uses reference equality (<code>===</code>) to detect changes. Mutating state means the reference doesn&rsquo;t change, so React-Redux can&rsquo;t tell what changed and components don&rsquo;t re-render.</p>

<pre><code>// WRONG — mutating state directly
function reducer(state, action) {
  state.count += 1;     // ✗ mutation
  return state;
}

// RIGHT — return new object
function reducer(state, action) {
  return { ...state, count: state.count + 1 };
}</code></pre>

<p><strong>Modern Redux Toolkit reducers</strong> &mdash; let you write "mutating" code that&rsquo;s actually immutable (Immer wraps it):</p>

<pre><code>const todosSlice = createSlice({
  name: "todos",
  initialState: [],
  reducers: {
    todoAdded(state, action) {
      state.push(action.payload);     // looks like mutation, actually immutable!
    },
    todoToggled(state, action) {
      const todo = state.find(t =&gt; t.id === action.payload);
      if (todo) todo.done = !todo.done;   // also safe
    }
  }
});</code></pre>

<p><strong>Behind the scenes</strong>, Immer creates a draft of state, lets you mutate the draft, then produces a new immutable state from your changes. The code reads naturally; the immutability is preserved.</p>

<p><strong>Combining multiple reducers</strong> &mdash; <code>combineReducers</code> for classic Redux, automatic in RTK:</p>

<pre><code>// Classic
const rootReducer = combineReducers({
  todos: todosReducer,
  user: userReducer,
  filters: filtersReducer
});

// Redux Toolkit
const store = configureStore({
  reducer: {
    todos: todosSlice.reducer,
    user: userSlice.reducer,
    filters: filtersSlice.reducer
  }
});</code></pre>

<p>State shape becomes <code>{ todos: [...], user: {...}, filters: {...} }</code> &mdash; each reducer manages its own slice independently.</p>
'''

ANSWERS[71] = r'''
<p>The <strong>Redux store</strong> holds the entire app state in a single JavaScript object. It&rsquo;s the <strong>single source of truth</strong> &mdash; the only place state lives, the only thing components read from, and the only thing reducers update.</p>

<p><strong>The store provides three core methods:</strong></p>

<table>
  <tr><th>Method</th><th>Purpose</th></tr>
  <tr><td><code>store.getState()</code></td><td>Returns the current state object</td></tr>
  <tr><td><code>store.dispatch(action)</code></td><td>Sends an action through the reducers; triggers updates</td></tr>
  <tr><td><code>store.subscribe(listener)</code></td><td>Register a callback that runs after each dispatch</td></tr>
</table>

<p><strong>Creating a store with Redux Toolkit:</strong></p>

<pre><code>import { configureStore } from "@reduxjs/toolkit";
import counterReducer from "./counterSlice";
import todosReducer from "./todosSlice";

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    todos: todosReducer
  }
});</code></pre>

<p><strong>What <code>configureStore</code> does behind the scenes:</strong></p>
<ul>
  <li>Combines your reducers automatically.</li>
  <li>Adds <code>redux-thunk</code> middleware (for async actions).</li>
  <li>Includes the Redux DevTools extension support.</li>
  <li>Adds development-only checks for state mutations and serializability.</li>
</ul>

<p><strong>Single store, many slices</strong>:</p>

<pre><code>// State shape becomes:
{
  counter: { value: 0 },
  todos: [
    { id: 1, text: "Buy milk", done: false },
    { id: 2, text: "Walk dog", done: true }
  ]
}</code></pre>

<p>Each top-level key is managed by its own slice/reducer. The store is one object, but logic is modular.</p>

<p><strong>Why a single store</strong>:</p>
<ul>
  <li><strong>Easy to debug</strong> &mdash; all state visible in one place.</li>
  <li><strong>Time-travel debugging</strong> &mdash; replay any action sequence.</li>
  <li><strong>Persistence</strong> &mdash; serialize the whole store to localStorage with one call.</li>
  <li><strong>SSR</strong> &mdash; serialize on server, hydrate on client.</li>
</ul>

<p><strong>The Provider connects store to React:</strong></p>

<pre><code>import { Provider } from "react-redux";
import { store } from "./store";

&lt;Provider store={store}&gt;
  &lt;App /&gt;
&lt;/Provider&gt;</code></pre>

<p>All components inside <code>&lt;Provider&gt;</code> can read from the store via <code>useSelector</code> and dispatch via <code>useDispatch</code> &mdash; no prop drilling.</p>

<p><strong>Direct store access (rare)</strong>:</p>

<pre><code>// Outside React (utilities, services)
import { store } from "./store";

const currentUser = store.getState().user;
store.dispatch({ type: "user/loggedOut" });</code></pre>

<p>Useful in non-React code (analytics, error reporting, web sockets) but generally components should use the hooks instead.</p>

<p><strong>Multiple stores</strong>: technically possible but discouraged &mdash; loses many of Redux&rsquo;s benefits. Almost always one store per app.</p>
'''

ANSWERS[72] = r'''
<p>Dispatching actions in a React component uses the <strong><code>useDispatch</code></strong> hook from <strong>react-redux</strong>. It returns the store&rsquo;s <code>dispatch</code> function, which you call with action objects (or action creators).</p>

<pre><code>import { useDispatch } from "react-redux";
import { increment, decrement, incrementByAmount } from "./counterSlice";

function CounterControls() {
  const dispatch = useDispatch();

  return (
    &lt;&gt;
      &lt;button onClick={() =&gt; dispatch(increment())}&gt;+&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch(decrement())}&gt;-&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch(incrementByAmount(5))}&gt;+5&lt;/button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>The flow:</strong></p>
<ol>
  <li>User clicks the <code>+</code> button.</li>
  <li><code>dispatch(increment())</code> sends the action to the store.</li>
  <li>Reducer responds, updates state.</li>
  <li>Components subscribed via <code>useSelector</code> re-render with the new state.</li>
</ol>

<p><strong>Dispatching with payload:</strong></p>

<pre><code>function TodoForm() {
  const dispatch = useDispatch();
  const [text, setText] = useState("");

  const handleSubmit = (e) =&gt; {
    e.preventDefault();
    dispatch(todoAdded(text));     // action creator generates the payload
    setText("");
  };

  return (
    &lt;form onSubmit={handleSubmit}&gt;
      &lt;input value={text} onChange={e =&gt; setText(e.target.value)} /&gt;
      &lt;button type="submit"&gt;Add&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Multiple dispatches:</strong></p>

<pre><code>function CheckoutButton() {
  const dispatch = useDispatch();

  const handleCheckout = () =&gt; {
    dispatch(cartCleared());
    dispatch(orderCreated());
    dispatch(notificationShown("Order placed"));
  };

  return &lt;button onClick={handleCheckout}&gt;Checkout&lt;/button&gt;;
}</code></pre>

<p>Each dispatch is independent &mdash; the store updates after each. Components re-render in response to changes affecting them.</p>

<p><strong>Async dispatches with Thunks (Redux Toolkit):</strong></p>

<pre><code>import { createAsyncThunk } from "@reduxjs/toolkit";

export const fetchUser = createAsyncThunk("user/fetch", async (userId) =&gt; {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
});

// Component dispatches the thunk
function UserProfile({ userId }) {
  const dispatch = useDispatch();

  useEffect(() =&gt; {
    dispatch(fetchUser(userId));
  }, [userId]);
}</code></pre>

<p><strong>Common gotchas:</strong></p>
<ul>
  <li><strong>Calling <code>dispatch</code> outside a component</strong> &mdash; use the imported <code>store.dispatch</code> directly, or pass dispatch through a parameter to the function.</li>
  <li><strong>Dispatching during render</strong> &mdash; will cause infinite re-renders. Always dispatch in event handlers, <code>useEffect</code>, or callbacks.</li>
  <li><strong>Forgetting to call the action creator</strong>: <code>dispatch(increment)</code> dispatches the function reference (wrong); <code>dispatch(increment())</code> dispatches the action object (correct).</li>
</ul>

<p><strong>TypeScript</strong>: define a typed <code>useDispatch</code> hook once that knows about thunks &mdash; gives full type checking on dispatched actions.</p>
'''

ANSWERS[73] = r'''
<p>The <strong><code>useSelector</code></strong> hook reads data from the Redux store. It takes a selector function that receives the entire state and returns the slice you care about. The component re-renders whenever the selected value changes.</p>

<pre><code>import { useSelector } from "react-redux";

function Counter() {
  const count = useSelector((state) =&gt; state.counter.value);
  return &lt;p&gt;Count: {count}&lt;/p&gt;;
}

function TodoList() {
  const todos = useSelector((state) =&gt; state.todos);
  return (
    &lt;ul&gt;
      {todos.map(todo =&gt; (
        &lt;li key={todo.id}&gt;{todo.text}&lt;/li&gt;
      ))}
    &lt;/ul&gt;
  );
}</code></pre>

<p><strong>How re-renders work</strong>: react-redux subscribes the component to the store. After each dispatch, react-redux runs the selector with the new state. If the result <strong>differs by reference equality</strong> (<code>===</code>) from the previous result, the component re-renders.</p>

<p><strong>Critical &mdash; selector return values must have stable references for unchanged data:</strong></p>

<pre><code>// BAD: creates new object every render — always re-renders
const userInfo = useSelector(state =&gt; ({
  name: state.user.name,
  email: state.user.email
}));   // ✗ new object every time, even if data same

// GOOD: select primitives or whole objects from store
const name = useSelector(state =&gt; state.user.name);
const email = useSelector(state =&gt; state.user.email);

// OR use shallowEqual for object selections
import { shallowEqual } from "react-redux";

const userInfo = useSelector(
  state =&gt; ({ name: state.user.name, email: state.user.email }),
  shallowEqual    // compare object keys, not full reference
);</code></pre>

<p><strong>Memoized selectors with reselect</strong> &mdash; for expensive derivations:</p>

<pre><code>import { createSelector } from "@reduxjs/toolkit";

const selectTodos = (state) =&gt; state.todos;
const selectFilter = (state) =&gt; state.filter;

// Memoized — only recomputes when todos or filter change
const selectVisibleTodos = createSelector(
  [selectTodos, selectFilter],
  (todos, filter) =&gt; todos.filter(t =&gt; matches(t, filter))
);

// Use in component
const visibleTodos = useSelector(selectVisibleTodos);</code></pre>

<p><strong>Selector best practices:</strong></p>

<table>
  <tr><th>Practice</th><th>Why</th></tr>
  <tr><td>Co-locate selectors with slices</td><td>Easier to maintain</td></tr>
  <tr><td>Export named selectors</td><td>Reusable across components</td></tr>
  <tr><td>Use <code>createSelector</code> for derivations</td><td>Avoid recomputing on every render</td></tr>
  <tr><td>Select primitives when possible</td><td>Built-in equality check works</td></tr>
  <tr><td>Use <code>shallowEqual</code> for object slices</td><td>Avoid unnecessary re-renders</td></tr>
</table>

<p><strong>TypeScript usage</strong>:</p>

<pre><code>import type { RootState } from "./store";

const count = useSelector((state: RootState) =&gt; state.counter.value);

// Better: typed hook (define once, import everywhere)
const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;
const count = useAppSelector(state =&gt; state.counter.value);   // fully typed</code></pre>

<p>The typed-hook pattern is the official Redux Toolkit recommendation &mdash; defines selector types once, automatic everywhere.</p>
'''

ANSWERS[74] = r'''
<p>The <strong><code>useDispatch</code></strong> hook returns the store&rsquo;s <code>dispatch</code> function, which is how components send actions to the store. It&rsquo;s the counterpart to <code>useSelector</code> &mdash; one reads, the other writes.</p>

<pre><code>import { useDispatch } from "react-redux";
import { increment, decrement, todoAdded } from "./store";

function Counter() {
  const dispatch = useDispatch();

  return (
    &lt;&gt;
      &lt;button onClick={() =&gt; dispatch(increment())}&gt;+&lt;/button&gt;
      &lt;button onClick={() =&gt; dispatch(decrement())}&gt;-&lt;/button&gt;
    &lt;/&gt;
  );
}

function AddTodo() {
  const dispatch = useDispatch();
  const [text, setText] = useState("");

  return (
    &lt;form onSubmit={(e) =&gt; {
      e.preventDefault();
      dispatch(todoAdded(text));
      setText("");
    }}&gt;
      &lt;input value={text} onChange={(e) =&gt; setText(e.target.value)} /&gt;
      &lt;button type="submit"&gt;Add&lt;/button&gt;
    &lt;/form&gt;
  );
}</code></pre>

<p><strong>Key behaviors:</strong></p>
<ul>
  <li><strong>Reference is stable</strong> &mdash; <code>dispatch</code> doesn&rsquo;t change between renders, safe to put in <code>useEffect</code> dependency arrays without causing infinite loops.</li>
  <li><strong>Returns the action object</strong> &mdash; useful for chaining, but rarely needed.</li>
  <li><strong>Synchronous</strong> &mdash; reducers run immediately. State is updated by the time <code>dispatch</code> returns.</li>
</ul>

<p><strong>Dispatching async thunks:</strong></p>

<pre><code>import { fetchUserById } from "./userSlice";

function UserProfile({ userId }) {
  const dispatch = useDispatch();

  useEffect(() =&gt; {
    dispatch(fetchUserById(userId));
  }, [userId, dispatch]);
}</code></pre>

<p><strong>Awaiting thunks &mdash; <code>.unwrap()</code> for handling success/error:</strong></p>

<pre><code>async function handleSubmit() {
  try {
    const user = await dispatch(fetchUserById(userId)).unwrap();
    // user is the resolved payload
    showToast(`Loaded ${user.name}`);
  } catch (error) {
    // error is the rejected payload
    showToast(`Error: ${error.message}`);
  }
}</code></pre>

<p><code>.unwrap()</code> on a thunk dispatch result returns a promise that resolves to the action&rsquo;s payload, or rejects with the error &mdash; cleanly handle async dispatches in event handlers.</p>

<p><strong>Common patterns:</strong></p>

<pre><code>// Multiple dispatches
const handleSave = async () =&gt; {
  dispatch(saveStarted());
  try {
    await api.save(data);
    dispatch(saveSucceeded());
  } catch (e) {
    dispatch(saveFailed(e.message));
  }
};

// Conditional dispatch
const handleSubmit = () =&gt; {
  if (isValid(form)) {
    dispatch(formSubmitted(form));
  } else {
    dispatch(validationFailed(getErrors(form)));
  }
};</code></pre>

<p><strong>TypeScript &mdash; typed dispatch hook:</strong></p>

<pre><code>import type { AppDispatch } from "./store";

const useAppDispatch = () =&gt; useDispatch&lt;AppDispatch&gt;();

// Now imports give full type inference for thunks
const dispatch = useAppDispatch();
const result = await dispatch(fetchUser(id)).unwrap();   // result is fully typed</code></pre>

<p>Same pattern as the typed selector hook &mdash; define once, use everywhere with full type safety.</p>
'''

ANSWERS[75] = r'''
<p><strong>Middleware in Redux</strong> sits between dispatching an action and the action reaching the reducer. It can intercept, transform, log, delay, or replace actions &mdash; enabling cross-cutting concerns like logging, async operations, analytics, and error reporting.</p>

<p><strong>The dispatch flow with middleware:</strong></p>

<pre><code>dispatch(action)
   ↓
[middleware 1: logging]
   ↓
[middleware 2: thunk — runs functions]
   ↓
[middleware 3: API client]
   ↓
[reducer]
   ↓
new state</code></pre>

<p>Each middleware decides whether to pass the action along, modify it, replace it with another action, or short-circuit entirely.</p>

<p><strong>Built-in middleware in Redux Toolkit:</strong></p>

<table>
  <tr><th>Middleware</th><th>What it does</th></tr>
  <tr><td>thunk</td><td>Lets you dispatch functions instead of plain objects (for async)</td></tr>
  <tr><td>serializableCheck (dev)</td><td>Warns if action/state contains non-serializable values (Date, Map, functions)</td></tr>
  <tr><td>immutableCheck (dev)</td><td>Warns if state is mutated outside reducers</td></tr>
  <tr><td>actionCreatorCheck (dev)</td><td>Warns if action creators are accidentally dispatched as functions</td></tr>
</table>

<p><strong>Adding custom middleware:</strong></p>

<pre><code>const loggerMiddleware = (storeAPI) =&gt; (next) =&gt; (action) =&gt; {
  console.log("Dispatching:", action);
  const result = next(action);   // pass to next middleware/reducer
  console.log("Next state:", storeAPI.getState());
  return result;
};

const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefault) =&gt; getDefault().concat(loggerMiddleware)
});</code></pre>

<p>The <code>(storeAPI) =&gt; (next) =&gt; (action) =&gt;</code> currying pattern is the standard middleware signature. <code>storeAPI</code> has <code>getState</code> and <code>dispatch</code>; <code>next</code> passes the action along; <code>action</code> is what was dispatched.</p>

<p><strong>Common middleware uses:</strong></p>

<pre><code>// Analytics
const analyticsMw = () =&gt; (next) =&gt; (action) =&gt; {
  if (action.type === "checkout/completed") {
    trackEvent("Purchase", action.payload);
  }
  return next(action);
};

// Error reporting
const sentryMw = () =&gt; (next) =&gt; (action) =&gt; {
  if (action.error) {
    Sentry.captureException(action.payload);
  }
  return next(action);
};

// Persistence (manual)
const persistMw = (storeAPI) =&gt; (next) =&gt; (action) =&gt; {
  const result = next(action);
  localStorage.setItem("state", JSON.stringify(storeAPI.getState()));
  return result;
};</code></pre>

<p><strong>Popular third-party middleware:</strong></p>
<ul>
  <li><strong>redux-thunk</strong> &mdash; async actions as functions (built into RTK).</li>
  <li><strong>redux-saga</strong> &mdash; complex async flows with generators.</li>
  <li><strong>redux-observable</strong> &mdash; reactive streams with RxJS.</li>
  <li><strong>redux-persist</strong> &mdash; persist store to localStorage automatically.</li>
  <li><strong>redux-logger</strong> &mdash; console-friendly action/state logger.</li>
</ul>

<p><strong>Modern alternative</strong>: RTK Query (built into Redux Toolkit) handles most async data needs without explicit middleware &mdash; it generates reducers, actions, and hooks for API endpoints automatically. For new Redux projects in 2026, RTK Query handles the use cases that previously needed Thunk or Saga.</p>
'''

ANSWERS[76] = r'''
<p>Asynchronous actions in Redux can&rsquo;t be plain action objects (which are synchronous). They need <strong>middleware</strong> &mdash; the most common is <strong>Redux Thunk</strong> (built into Redux Toolkit), which lets you dispatch functions that perform async work and dispatch other actions.</p>

<p><strong>The standard approach &mdash; <code>createAsyncThunk</code> from RTK:</strong></p>

<pre><code>import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

// Define the thunk
export const fetchUserById = createAsyncThunk(
  "user/fetchById",                          // action type prefix
  async (userId, thunkAPI) =&gt; {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      return thunkAPI.rejectWithValue("Failed to fetch user");
    }
    return response.json();
  }
);

// Handle the three states in your slice
const userSlice = createSlice({
  name: "user",
  initialState: { data: null, loading: false, error: null },
  reducers: {},
  extraReducers: (builder) =&gt; {
    builder
      .addCase(fetchUserById.pending, (state) =&gt; {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserById.fulfilled, (state, action) =&gt; {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchUserById.rejected, (state, action) =&gt; {
        state.loading = false;
        state.error = action.payload;
      });
  }
});</code></pre>

<p><strong>Three auto-generated action types per thunk:</strong></p>

<table>
  <tr><th>Action</th><th>When dispatched</th></tr>
  <tr><td><code>user/fetchById/pending</code></td><td>When the thunk starts</td></tr>
  <tr><td><code>user/fetchById/fulfilled</code></td><td>On success (with payload from your function)</td></tr>
  <tr><td><code>user/fetchById/rejected</code></td><td>On error (or <code>rejectWithValue</code>)</td></tr>
</table>

<p><strong>Using the thunk in a component:</strong></p>

<pre><code>import { useDispatch, useSelector } from "react-redux";
import { fetchUserById } from "./userSlice";

function UserProfile({ userId }) {
  const dispatch = useDispatch();
  const { data, loading, error } = useSelector(state =&gt; state.user);

  useEffect(() =&gt; {
    dispatch(fetchUserById(userId));
  }, [userId]);

  if (loading) return &lt;p&gt;Loading...&lt;/p&gt;;
  if (error)   return &lt;p&gt;Error: {error}&lt;/p&gt;;
  return &lt;h1&gt;{data.name}&lt;/h1&gt;;
}</code></pre>

<p><strong>Async patterns table:</strong></p>

<table>
  <tr><th>Pattern</th><th>Tool</th><th>When</th></tr>
  <tr><td>Simple async actions</td><td>createAsyncThunk</td><td>API calls with success/error/loading</td></tr>
  <tr><td>Complex flows</td><td>Redux-Saga</td><td>Cancellation, retries, race conditions, complex orchestration</td></tr>
  <tr><td>Streams of events</td><td>redux-observable</td><td>WebSockets, real-time updates, RxJS</td></tr>
  <tr><td>Auto-cached server data</td><td>RTK Query</td><td>Most modern apps &mdash; replaces hand-rolled async</td></tr>
</table>

<p><strong>RTK Query &mdash; the 2026 recommendation for async data:</strong></p>

<pre><code>import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  endpoints: (builder) =&gt; ({
    getUser: builder.query({
      query: (id) =&gt; `users/${id}`
    })
  })
});

export const { useGetUserQuery } = api;

// Component
function UserProfile({ userId }) {
  const { data, isLoading, error } = useGetUserQuery(userId);
  if (isLoading) return &lt;p&gt;Loading...&lt;/p&gt;;
  return &lt;h1&gt;{data.name}&lt;/h1&gt;;
}</code></pre>

<p>Auto-cached, deduplicated, refetched on focus, with normalized cache &mdash; replaces 30+ lines of thunk + slice + reducer with a single endpoint definition.</p>
'''

ANSWERS[77] = r'''
<p><strong>Redux Thunk</strong> is the most common middleware for handling async logic in Redux. A "thunk" is a function returned by another function &mdash; it lets you dispatch a function instead of a plain action object. The middleware intercepts these functions, calls them with <code>dispatch</code> and <code>getState</code>, and lets you perform async operations.</p>

<p><strong>What thunk middleware enables:</strong></p>

<pre><code>// Without thunk: only plain objects can be dispatched
dispatch({ type: "USER_FETCHED", payload: user });   // ✓
dispatch(fetchUser());                                  // ✗ throws

// With thunk: functions are also valid
function fetchUser(userId) {
  return async (dispatch, getState) =&gt; {
    dispatch({ type: "USER_FETCH_STARTED" });
    try {
      const user = await api.fetchUser(userId);
      dispatch({ type: "USER_FETCHED", payload: user });
    } catch (e) {
      dispatch({ type: "USER_FETCH_FAILED", error: e.message });
    }
  };
}

dispatch(fetchUser(123));   // ✓ works with thunk middleware</code></pre>

<p><strong>What you get inside a thunk:</strong></p>

<table>
  <tr><th>Argument</th><th>Use for</th></tr>
  <tr><td><code>dispatch</code></td><td>Dispatch other actions (start, success, fail)</td></tr>
  <tr><td><code>getState</code></td><td>Read current state to make decisions</td></tr>
  <tr><td><code>extraArgument</code> (optional)</td><td>Inject API client or services for testability</td></tr>
</table>

<p><strong>Modern usage &mdash; <code>createAsyncThunk</code> from Redux Toolkit:</strong></p>

<pre><code>import { createAsyncThunk } from "@reduxjs/toolkit";

export const fetchUser = createAsyncThunk(
  "user/fetch",
  async (userId, { rejectWithValue, getState }) =&gt; {
    try {
      const response = await fetch(`/api/users/${userId}`);
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Auto-generates: user/fetch/pending, user/fetch/fulfilled, user/fetch/rejected
// You handle these in extraReducers</code></pre>

<p><strong>Conditional dispatch with getState:</strong></p>

<pre><code>function fetchUserIfNeeded(userId) {
  return async (dispatch, getState) =&gt; {
    const cached = getState().users[userId];
    if (cached &amp;&amp; cached.timestamp &gt; Date.now() - 60000) {
      return;   // skip fetch — recent data already in store
    }
    dispatch(fetchUser(userId));
  };
}</code></pre>

<p><strong>Sequential / parallel dispatches:</strong></p>

<pre><code>// Sequential
function loginAndLoadProfile(credentials) {
  return async (dispatch) =&gt; {
    const user = await dispatch(login(credentials)).unwrap();
    dispatch(loadProfile(user.id));
    dispatch(loadPreferences(user.id));
  };
}

// Parallel
function loadDashboard() {
  return async (dispatch) =&gt; {
    await Promise.all([
      dispatch(loadStats()),
      dispatch(loadNotifications()),
      dispatch(loadActivity())
    ]);
  };
}</code></pre>

<p><strong>Pros and cons of Thunk:</strong></p>

<table>
  <tr><th>Pros</th><th>Cons</th></tr>
  <tr><td>Simple, just plain async functions</td><td>No built-in cancellation</td></tr>
  <tr><td>Easy to test (pure functions)</td><td>Complex orchestration is awkward</td></tr>
  <tr><td>Built into RTK</td><td>Race conditions need manual handling</td></tr>
  <tr><td>Works for 90% of async needs</td><td>No timeline-style debugging like Saga</td></tr>
</table>

<p><strong>2026 status</strong>: thunk via <code>createAsyncThunk</code> is the default for Redux Toolkit projects. For most apps it&rsquo;s the right choice. Reach for Saga only when you have complex flows (cancellation, retries, debouncing, race-condition logic). Reach for RTK Query when your async work is fetching server data &mdash; it handles caching automatically.</p>
'''

ANSWERS[78] = r'''
<p><strong>Redux-Saga</strong> is a middleware library that uses <strong>generator functions</strong> to manage complex async logic in Redux. It&rsquo;s designed for cases where Thunk isn&rsquo;t enough: cancellation, retries, debouncing, race conditions, and complex orchestration of multiple async operations.</p>

<p><strong>Sagas use generator functions</strong> &mdash; functions that can pause and resume, yielding "effects" that the saga middleware executes:</p>

<pre><code>import { call, put, takeEvery } from "redux-saga/effects";

function* fetchUserSaga(action) {
  try {
    const user = yield call(api.fetchUser, action.payload);
    yield put({ type: "USER_FETCH_SUCCESS", payload: user });
  } catch (error) {
    yield put({ type: "USER_FETCH_FAILURE", error: error.message });
  }
}

// Watcher: listens for actions and runs the saga
function* watchFetchUser() {
  yield takeEvery("USER_FETCH_REQUESTED", fetchUserSaga);
}

// Root saga combines all watchers
export default function* rootSaga() {
  yield all([
    watchFetchUser(),
    watchOtherActions()
  ]);
}</code></pre>

<p><strong>Common saga effects:</strong></p>

<table>
  <tr><th>Effect</th><th>Purpose</th></tr>
  <tr><td><code>call(fn, ...args)</code></td><td>Call a function (sync or async); pauses saga until it resolves</td></tr>
  <tr><td><code>put(action)</code></td><td>Dispatch an action to the store</td></tr>
  <tr><td><code>select(selector)</code></td><td>Read from store state</td></tr>
  <tr><td><code>take(actionType)</code></td><td>Wait for a specific action to be dispatched</td></tr>
  <tr><td><code>takeEvery(type, saga)</code></td><td>Run saga every time matching action is dispatched</td></tr>
  <tr><td><code>takeLatest(type, saga)</code></td><td>Cancel previous; only run latest invocation</td></tr>
  <tr><td><code>fork(saga)</code></td><td>Run saga in background (non-blocking)</td></tr>
  <tr><td><code>all([...effects])</code></td><td>Run effects in parallel; wait for all</td></tr>
  <tr><td><code>race({...effects})</code></td><td>Race multiple effects; whoever finishes first wins</td></tr>
  <tr><td><code>delay(ms)</code></td><td>Pause for specified time</td></tr>
  <tr><td><code>cancel(task)</code></td><td>Cancel a running saga</td></tr>
</table>

<p><strong>Where Sagas shine &mdash; complex orchestration:</strong></p>

<pre><code>// Debounced search — cancels previous request when user keeps typing
function* searchSaga() {
  while (true) {
    const action = yield take("SEARCH_TERM_CHANGED");
    yield delay(300);                              // wait 300ms
    const results = yield call(api.search, action.payload);
    yield put({ type: "SEARCH_RESULTS", payload: results });
  }
}

// Race — fetch with timeout
function* fetchWithTimeout(url) {
  const { response, timeout } = yield race({
    response: call(api.fetch, url),
    timeout: delay(5000)
  });
  if (timeout) {
    yield put({ type: "FETCH_TIMEOUT" });
  } else {
    yield put({ type: "FETCH_SUCCESS", payload: response });
  }
}

// Cancel on navigation
function* uploadSaga() {
  const task = yield fork(uploadFile);
  yield take("USER_NAVIGATED_AWAY");
  yield cancel(task);                             // cancel upload
}</code></pre>

<p><strong>Thunk vs Saga:</strong></p>

<table>
  <tr><th></th><th>Thunk</th><th>Saga</th></tr>
  <tr><td>Learning curve</td><td>Easy (just async functions)</td><td>Steep (generators + effects)</td></tr>
  <tr><td>Cancellation</td><td>Manual</td><td>Built-in (<code>cancel</code>, <code>takeLatest</code>)</td></tr>
  <tr><td>Testing</td><td>Mock dispatch and async</td><td>Test effect descriptions (declarative)</td></tr>
  <tr><td>Complex flows</td><td>Awkward</td><td>Natural &mdash; sagas read like business logic</td></tr>
  <tr><td>Bundle size</td><td>Small (~1KB)</td><td>Larger (~12KB)</td></tr>
  <tr><td>Use for</td><td>Most async (90% of cases)</td><td>Complex orchestration, cancellation, retries</td></tr>
</table>

<p><strong>2026 reality</strong>: Saga is mostly used in large enterprise apps with complex async flows. For typical CRUD apps, <strong>RTK Query</strong> (server state) + <strong><code>createAsyncThunk</code></strong> (other async) covers 95% of needs. Sagas remain valuable when you genuinely need their power: WebSocket message handling, complex authentication flows, multi-step wizards with cancellation, etc.</p>
'''

ANSWERS[79] = r'''
<p>Setting up a Redux store with middleware is straightforward in <strong>Redux Toolkit</strong> &mdash; <code>configureStore</code> includes default middleware (thunk, dev checks) and lets you add custom middleware via the <code>middleware</code> option.</p>

<p><strong>Default setup &mdash; just RTK&rsquo;s built-in middleware:</strong></p>

<pre><code>import { configureStore } from "@reduxjs/toolkit";
import counterReducer from "./counterSlice";
import todosReducer from "./todosSlice";

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    todos: todosReducer
  }
  // middleware: gets the defaults — thunk + dev checks
});</code></pre>

<p><strong>Adding custom middleware</strong> &mdash; concatenate to the default list:</p>

<pre><code>import logger from "redux-logger";

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =&gt;
    getDefaultMiddleware().concat(logger)
});</code></pre>

<p>The <code>getDefaultMiddleware</code> callback gives you the array of default middleware (thunk, immutability check, etc.). <code>.concat()</code> appends yours; <code>.prepend()</code> puts it first.</p>

<p><strong>Adding multiple middleware:</strong></p>

<pre><code>import logger from "redux-logger";
import { sentryMiddleware } from "./middleware/sentry";
import { analyticsMiddleware } from "./middleware/analytics";

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =&gt;
    getDefaultMiddleware().concat(logger, sentryMiddleware, analyticsMiddleware)
});</code></pre>

<p><strong>Disabling default middleware (rare but possible):</strong></p>

<pre><code>middleware: (getDefaultMiddleware) =&gt;
  getDefaultMiddleware({
    serializableCheck: false,    // disable serialization check (e.g., for Date objects)
    immutableCheck: false        // disable immutability check
  })</code></pre>

<p><strong>Adding Saga middleware:</strong></p>

<pre><code>import createSagaMiddleware from "redux-saga";
import rootSaga from "./sagas";

const sagaMiddleware = createSagaMiddleware();

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =&gt;
    getDefaultMiddleware({ thunk: false }).concat(sagaMiddleware)
  // Note: { thunk: false } if you're using Saga instead of Thunk
});

sagaMiddleware.run(rootSaga);     // start the saga</code></pre>

<p><strong>Adding RTK Query middleware:</strong></p>

<pre><code>import { setupListeners } from "@reduxjs/toolkit/query";
import { api } from "./services/api";

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    counter: counterReducer
  },
  middleware: (getDefaultMiddleware) =&gt;
    getDefaultMiddleware().concat(api.middleware)
});

setupListeners(store.dispatch);    // enables refetchOnFocus, refetchOnReconnect</code></pre>

<p><strong>Full production setup with TypeScript:</strong></p>

<pre><code>import { configureStore } from "@reduxjs/toolkit";
import { TypedUseSelectorHook, useDispatch, useSelector } from "react-redux";
import logger from "redux-logger";
import { api } from "./services/api";
import counterReducer from "./counterSlice";

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    [api.reducerPath]: api.reducer
  },
  middleware: (getDefaultMiddleware) =&gt;
    getDefaultMiDdleware()
      .concat(api.middleware)
      .concat(process.env.NODE_ENV !== "production" ? [logger] : [])
});

export type RootState = ReturnType&lt;typeof store.getState&gt;;
export type AppDispatch = typeof store.dispatch;

// Typed hooks for components
export const useAppDispatch: () =&gt; AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook&lt;RootState&gt; = useSelector;</code></pre>

<p><strong>This is the modern standard:</strong> RTK + RTK Query + typed hooks. Components import <code>useAppDispatch</code>/<code>useAppSelector</code> instead of the raw <code>useDispatch</code>/<code>useSelector</code>, getting full TypeScript inference for state and actions.</p>

<p><strong>Old <code>createStore</code> + <code>applyMiddleware</code></strong>: still works but deprecated &mdash; <code>configureStore</code> is the recommended API since 2019.</p>
'''

ANSWERS[80] = r'''
<p>Debugging React apps combines <strong>browser DevTools</strong>, <strong>React DevTools</strong> (a separate browser extension), and good old <strong><code>console.log</code></strong>. The key is using the right tool for the kind of bug you&rsquo;re hunting.</p>

<p><strong>The debugging toolkit:</strong></p>

<table>
  <tr><th>Tool</th><th>Use for</th></tr>
  <tr><td><code>console.log</code> / <code>console.table</code></td><td>Quick inspection of values, props, state</td></tr>
  <tr><td><code>debugger</code> statement</td><td>Pause execution; inspect locals in DevTools Sources tab</td></tr>
  <tr><td>React DevTools (Components)</td><td>Inspect component tree, props, state, hooks</td></tr>
  <tr><td>React DevTools (Profiler)</td><td>Find performance bottlenecks; see which components re-rendered and why</td></tr>
  <tr><td>Network tab</td><td>Inspect API requests, responses, status codes</td></tr>
  <tr><td>Sources tab + breakpoints</td><td>Step through code line by line</td></tr>
  <tr><td>Redux DevTools</td><td>Time-travel through Redux actions; inspect state diffs</td></tr>
  <tr><td>Error boundaries + Sentry</td><td>Catch and report unexpected errors in production</td></tr>
</table>

<p><strong>Common debugging patterns:</strong></p>

<pre><code>// Inspect props and state
function Component({ user }) {
  console.log("Component render", { user });   // log every render
  return &lt;p&gt;{user.name}&lt;/p&gt;;
}

// Inspect render reasons (why did this component re-render?)
useEffect(() =&gt; {
  console.log("user changed", user);
}, [user]);

// Pause execution
function handleClick() {
  debugger;     // browser stops here when DevTools is open
  doSomething();
}

// Use console.table for arrays of objects
console.table(users);   // shows nice tabular output</code></pre>

<p><strong>Common bug patterns and how to debug them:</strong></p>

<table>
  <tr><th>Symptom</th><th>How to debug</th></tr>
  <tr><td>State doesn&rsquo;t update</td><td>React DevTools → check state at each render. Look for <code>setState</code> not being called or being passed the wrong value.</td></tr>
  <tr><td>Infinite re-renders</td><td>Console error mentions "Maximum update depth." Look for <code>setState</code> in render body or missing/wrong <code>useEffect</code> deps.</td></tr>
  <tr><td>useEffect runs too often</td><td>Inspect dep array. Reference values (objects, arrays, functions) defined in render body change every render.</td></tr>
  <tr><td>Stale closure (old state in callback)</td><td>useState updater form: <code>setX(prev =&gt; prev + 1)</code>. Or include the value in deps.</td></tr>
  <tr><td>Missing key warnings</td><td>Add stable <code>key</code> prop to list items.</td></tr>
  <tr><td>Cannot read property of undefined</td><td>Optional chaining (<code>obj?.field</code>) and proper loading states.</td></tr>
</table>

<p><strong>"Why did you render?"</strong> &mdash; the <code>why-did-you-render</code> library hooks into React and logs reasons for re-renders. Useful when chasing performance issues.</p>

<p><strong>Strict Mode</strong> &mdash; in development, React runs effects and reducers twice to surface bugs. Common surprise: an effect logs twice because it&rsquo;s being intentionally double-invoked. This is a feature, not a bug.</p>

<pre><code>// Production: enabling source maps lets you debug minified code with original line numbers
// Vite/CRA enable this by default in dev; you can also enable it in production builds
&lt;StrictMode&gt;
  &lt;App /&gt;
&lt;/StrictMode&gt;</code></pre>
'''

ANSWERS[81] = r'''
<p><strong>React Developer Tools</strong> is a browser extension (Chrome, Firefox, Edge) that adds two tabs to your DevTools: <strong>Components</strong> and <strong>Profiler</strong>. It&rsquo;s essential for debugging React apps &mdash; you can inspect the component tree, see props and state, track hook values, and analyze performance.</p>

<p><strong>The two tabs:</strong></p>

<table>
  <tr><th>Tab</th><th>Purpose</th></tr>
  <tr><td>Components</td><td>Tree view of all React components; inspect/edit props, state, hooks</td></tr>
  <tr><td>Profiler</td><td>Record render performance; see which components rendered, how long they took, why</td></tr>
</table>

<p><strong>What you can do in the Components tab:</strong></p>
<ul>
  <li><strong>Browse the component tree</strong> &mdash; expand/collapse, search by component name.</li>
  <li><strong>Inspect props and state</strong> &mdash; see all props passed to a component, all state values inside it.</li>
  <li><strong>Edit values live</strong> &mdash; change a state value or prop in real time to test UI behavior.</li>
  <li><strong>See hook values</strong> &mdash; <code>useState</code>, <code>useReducer</code>, <code>useContext</code>, custom hooks all show up.</li>
  <li><strong>Jump to source</strong> &mdash; click a component to open its file in your editor (with proper config).</li>
  <li><strong>View context values</strong> &mdash; see which Context providers are above the component.</li>
</ul>

<p><strong>What you can do in the Profiler tab:</strong></p>
<ul>
  <li><strong>Record a session</strong> &mdash; click record, interact with the app, stop recording.</li>
  <li><strong>See a flamegraph</strong> &mdash; visualize render times per component for each commit.</li>
  <li><strong>Inspect "why did this render"</strong> &mdash; see if a component rendered due to props change, state change, parent re-render, or hooks.</li>
  <li><strong>Compare commits</strong> &mdash; ranked chart shows which commits were slowest.</li>
  <li><strong>Find unnecessary renders</strong> &mdash; components that render when their props/state didn&rsquo;t actually change.</li>
</ul>

<p><strong>Installation</strong>:</p>

<pre><code>// Chrome/Edge: Install from Chrome Web Store
//   "React Developer Tools" by Meta

// Firefox: Install from Firefox Add-ons
//   "React Developer Tools"

// Standalone (Electron app): for React Native or in environments without browsers
npm install -g react-devtools
react-devtools</code></pre>

<p><strong>Once installed</strong>: open browser DevTools (F12), and you&rsquo;ll see two new tabs: <strong>Components</strong> and <strong>Profiler</strong>. They only appear when the page is using React.</p>

<p><strong>Tip &mdash; the React logo in the address bar:</strong></p>

<table>
  <tr><th>Logo color</th><th>Meaning</th></tr>
  <tr><td>Blue</td><td>Production build of React</td></tr>
  <tr><td>Red (orange)</td><td>Development build &mdash; lightning fast iteration</td></tr>
  <tr><td>Greyscale</td><td>No React detected on the page</td></tr>
</table>

<p>If you see grey on a known React app, the tools haven&rsquo;t loaded &mdash; refresh the page after installing.</p>

<p><strong>2026 reality</strong>: React DevTools is essentially required for serious React work. Modern versions integrate with React 19 features (Server Components, useActionState, use()) and the React Compiler.</p>
'''

ANSWERS[82] = r'''
<p>The <strong>Components tab</strong> in React DevTools shows the full component tree of your running app. You inspect components, view their props/state/hooks, and even edit values live to test behavior.</p>

<p><strong>How to inspect the tree:</strong></p>
<ol>
  <li><strong>Open browser DevTools</strong> (F12 or right-click → Inspect).</li>
  <li><strong>Click the Components tab</strong> (it appears next to Console, Sources, etc., when React is loaded).</li>
  <li><strong>Expand the tree</strong> to navigate from <code>&lt;App /&gt;</code> down to specific components.</li>
  <li><strong>Click a component</strong> to see its details in the right pane: props, state, hooks, source location.</li>
</ol>

<p><strong>What the right pane shows:</strong></p>

<pre><code>// When you select a component, the right pane shows:

Props
  ▾ user: { id: 42, name: "Alice", email: "alice@..." }
  ▸ onSelect: ƒ()
    isActive: true

State
  ▾ count: 5

Hooks
  1. State: 5             (useState)
  2. State: ""            (useState)
  3. Effect: ƒ()          (useEffect)
  4. Memo: { ... }        (useMemo)
  5. Callback: ƒ()        (useCallback)

Context
  ThemeContext: { mode: "dark" }

rendered by App › Layout</code></pre>

<p><strong>Hooks appear in call order</strong> &mdash; matching the order they appear in your component code. This is why hooks must be called in the same order every render.</p>

<p><strong>Editing values live:</strong></p>
<ul>
  <li><strong>Click a prop or state value</strong> to edit it in place &mdash; component re-renders with the new value.</li>
  <li>Useful for: testing edge cases (empty arrays, very long strings, error states), simulating loading/error states without triggering them, exploring conditional rendering.</li>
</ul>

<p><strong>Useful navigation features:</strong></p>

<table>
  <tr><th>Feature</th><th>How</th></tr>
  <tr><td>Search by name</td><td>Type in search box at top of Components tab</td></tr>
  <tr><td>Find a DOM element&rsquo;s component</td><td>Right-click element on page → "Inspect"; in Elements tab, the highlighted DOM node maps to a component in Components tab</td></tr>
  <tr><td>"Inspect" button (target icon)</td><td>Click, then click any element on the page to jump to its component</td></tr>
  <tr><td>Jump to source code</td><td>Click <code>&lt;&gt;</code> icon next to component name; opens the file in editor (requires config)</td></tr>
  <tr><td>Filter by component name</td><td>Settings cog → "Components" filters &mdash; hide HostComponents, hide internal components, etc.</td></tr>
  <tr><td>Highlight updates when components render</td><td>Settings cog → "Highlight updates when components render"</td></tr>
</table>

<p><strong>Highlight Updates feature</strong> is invaluable: enables a colored border that flashes around any component as it re-renders. You instantly see when components render unexpectedly &mdash; useful for finding wasted renders during interactions.</p>

<p><strong>Common workflow when debugging a UI bug:</strong></p>
<ol>
  <li>Reproduce the bug.</li>
  <li>Open Components tab.</li>
  <li>Find the affected component.</li>
  <li>Inspect props and state &mdash; do they match expectations?</li>
  <li>Walk up the tree to find where bad data originated.</li>
  <li>Edit values in place to confirm the hypothesis.</li>
  <li>Fix the source.</li>
</ol>

<p><strong>For Server Components (React 19+ in Next.js)</strong>: DevTools shows them with a special icon. They have no client state &mdash; just props.</p>
'''

ANSWERS[83] = r'''
<p>Animations in React come in three flavors: <strong>CSS animations/transitions</strong> (simplest), <strong>animation libraries</strong> like Framer Motion (most flexible), and <strong>imperative APIs</strong> like the Web Animations API (advanced control). Choose based on complexity and animation requirements.</p>

<p><strong>CSS transitions &mdash; simplest, just add a class:</strong></p>

<pre><code>// Component
function Box({ active }) {
  return (
    &lt;div className={`box ${active ? "active" : ""}`}&gt;
      Content
    &lt;/div&gt;
  );
}

/* CSS */
.box {
  transition: transform 300ms ease, background 300ms ease;
  transform: translateX(0);
  background: white;
}
.box.active {
  transform: translateX(100px);
  background: lightblue;
}</code></pre>

<p>CSS transitions handle most simple animations &mdash; hover effects, sliding panels, fading elements &mdash; with no JavaScript at all.</p>

<p><strong>CSS keyframe animations &mdash; for complex motion:</strong></p>

<pre><code>@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.1); }
}
.button-pulse {
  animation: pulse 2s ease-in-out infinite;
}</code></pre>

<p><strong>For animations on mount/unmount</strong> (a component appearing or being removed), CSS alone isn&rsquo;t enough &mdash; you need a library that delays unmounting until the exit animation completes.</p>

<p><strong>Framer Motion &mdash; the modern standard for React animations:</strong></p>

<pre><code>import { motion, AnimatePresence } from "framer-motion";

function Modal({ isOpen, children }) {
  return (
    &lt;AnimatePresence&gt;
      {isOpen &amp;&amp; (
        &lt;motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.2 }}
        &gt;
          {children}
        &lt;/motion.div&gt;
      )}
    &lt;/AnimatePresence&gt;
  );
}</code></pre>

<p><strong>Why Framer Motion dominates 2026:</strong></p>
<ul>
  <li><strong>Declarative</strong> &mdash; describe states, library figures out the animation.</li>
  <li><strong>Spring physics</strong> &mdash; natural, physics-based motion (more realistic than easing curves).</li>
  <li><strong>Layout animations</strong> &mdash; auto-animate when an element&rsquo;s size or position changes (<code>layout</code> prop).</li>
  <li><strong>Gestures</strong> &mdash; built-in drag, hover, tap, focus handlers.</li>
  <li><strong>Choreography</strong> &mdash; orchestrate sequences with <code>staggerChildren</code>.</li>
</ul>

<p><strong>Animation library landscape:</strong></p>

<table>
  <tr><th>Library</th><th>Best for</th></tr>
  <tr><td>Framer Motion</td><td>Most React projects &mdash; balance of power and ease</td></tr>
  <tr><td>React Spring</td><td>Physics-based animations; data-driven motion</td></tr>
  <tr><td>GSAP</td><td>Complex timeline-based animations; not React-specific</td></tr>
  <tr><td>React Transition Group</td><td>Mount/unmount transitions; lightweight, low-level</td></tr>
  <tr><td>Auto-Animate</td><td>Drop-in for list animations; minimal config</td></tr>
  <tr><td>CSS only</td><td>Simple state transitions; no JS overhead</td></tr>
</table>

<p><strong>Performance tip</strong>: animate <code>transform</code> and <code>opacity</code> &mdash; these are GPU-accelerated and don&rsquo;t cause layout reflow. Avoid animating <code>width</code>, <code>height</code>, <code>top</code>, <code>left</code>, <code>margin</code> on frequently-rendered elements.</p>

<p><strong>Accessibility</strong>: respect <code>prefers-reduced-motion</code> &mdash; users with vestibular disorders need this. Most animation libraries support it built-in:</p>

<pre><code>@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}</code></pre>
'''

ANSWERS[84] = r'''
<p><strong>React Transition Group</strong> is a small, focused animation library that manages <strong>component mount/unmount transitions</strong>. It doesn&rsquo;t do animations itself &mdash; it just exposes lifecycle hooks (mounting, mounted, unmounting, unmounted) so you can apply CSS classes or trigger custom animations at the right times.</p>

<p>Install with <code>npm install react-transition-group</code>. Despite its age (predates Framer Motion), it&rsquo;s still used in many production codebases &mdash; lightweight, framework-agnostic, no runtime overhead.</p>

<p><strong>The four core components:</strong></p>

<table>
  <tr><th>Component</th><th>Purpose</th></tr>
  <tr><td><code>&lt;Transition&gt;</code></td><td>Low-level: gives you raw lifecycle states</td></tr>
  <tr><td><code>&lt;CSSTransition&gt;</code></td><td>Most common: applies CSS classes at each lifecycle stage</td></tr>
  <tr><td><code>&lt;TransitionGroup&gt;</code></td><td>Manages a list of transitioning items (animated lists)</td></tr>
  <tr><td><code>&lt;SwitchTransition&gt;</code></td><td>Coordinates exit + enter when swapping a single child</td></tr>
</table>

<p><strong>Why use it over CSS alone</strong>: with CSS, when you remove an element from the DOM, its exit animation can&rsquo;t play &mdash; the element is just gone. React Transition Group keeps the element mounted for a configured duration after you remove it, applying exit classes during that window.</p>

<p><strong>Quick example &mdash; CSSTransition:</strong></p>

<pre><code>import { CSSTransition } from "react-transition-group";
import "./fade.css";

function App() {
  const [show, setShow] = useState(true);

  return (
    &lt;&gt;
      &lt;button onClick={() =&gt; setShow(s =&gt; !s)}&gt;Toggle&lt;/button&gt;

      &lt;CSSTransition
        in={show}
        timeout={300}
        classNames="fade"
        unmountOnExit
      &gt;
        &lt;div className="modal"&gt;Hello&lt;/div&gt;
      &lt;/CSSTransition&gt;
    &lt;/&gt;
  );
}</code></pre>

<pre><code>/* fade.css */
.fade-enter            { opacity: 0; }
.fade-enter-active     { opacity: 1; transition: opacity 300ms; }
.fade-exit             { opacity: 1; }
.fade-exit-active      { opacity: 0; transition: opacity 300ms; }</code></pre>

<p>The classes are applied automatically as <code>show</code> toggles &mdash; CSS handles the actual animation.</p>

<p><strong>Lifecycle stages and class names:</strong></p>

<table>
  <tr><th>Stage</th><th>Class added</th><th>When</th></tr>
  <tr><td>enter</td><td><code>fade-enter</code></td><td>Just before mounting (start state)</td></tr>
  <tr><td>entering</td><td><code>fade-enter-active</code></td><td>Right after mount (transition to end state)</td></tr>
  <tr><td>entered</td><td><code>fade-enter-done</code></td><td>After transition completes</td></tr>
  <tr><td>exit</td><td><code>fade-exit</code></td><td>Just before unmounting (start state)</td></tr>
  <tr><td>exiting</td><td><code>fade-exit-active</code></td><td>During exit (transition to end)</td></tr>
  <tr><td>exited</td><td><code>fade-exit-done</code></td><td>After exit completes; ready to unmount</td></tr>
</table>

<p><strong>2026 perspective</strong>: React Transition Group is still well-maintained and useful, but most teams reach for <strong>Framer Motion</strong> first &mdash; the API is more declarative, supports gestures and physics, and handles everything Transition Group does plus much more. Use Transition Group when you want minimal bundle size and CSS-driven animations; use Framer Motion when you want polish and flexibility.</p>

<p>See Q85 for a more detailed CSSTransition example.</p>
'''

ANSWERS[85] = r'''
<p><strong><code>CSSTransition</code></strong> is the most-used component from React Transition Group. It applies CSS classes to a child element at each stage of mounting/unmounting &mdash; you write the actual animation in CSS.</p>

<p><strong>Full example &mdash; modal with fade animation:</strong></p>

<pre><code>import { CSSTransition } from "react-transition-group";
import { useState, useRef } from "react";
import "./modal.css";

function Modal({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const nodeRef = useRef(null);    // avoids findDOMNode warning in StrictMode

  return (
    &lt;&gt;
      &lt;button onClick={() =&gt; setIsOpen(true)}&gt;Open&lt;/button&gt;

      &lt;CSSTransition
        in={isOpen}
        nodeRef={nodeRef}
        timeout={250}
        classNames="modal"
        unmountOnExit
      &gt;
        &lt;div ref={nodeRef} className="modal-overlay"&gt;
          &lt;div className="modal-content"&gt;
            {children}
            &lt;button onClick={() =&gt; setIsOpen(false)}&gt;Close&lt;/button&gt;
          &lt;/div&gt;
        &lt;/div&gt;
      &lt;/CSSTransition&gt;
    &lt;/&gt;
  );
}</code></pre>

<pre><code>/* modal.css */
.modal-enter         { opacity: 0; transform: scale(0.9); }
.modal-enter-active  { opacity: 1; transform: scale(1);
                       transition: opacity 250ms, transform 250ms; }
.modal-exit          { opacity: 1; transform: scale(1); }
.modal-exit-active   { opacity: 0; transform: scale(0.9);
                       transition: opacity 250ms, transform 250ms; }</code></pre>

<p>When <code>isOpen</code> becomes <code>true</code>: <code>modal-enter</code> applied → <code>modal-enter-active</code> applied next frame → CSS transition runs from start to end state. When it becomes <code>false</code>: exit classes run, then component unmounts.</p>

<p><strong>Key props:</strong></p>

<table>
  <tr><th>Prop</th><th>Purpose</th></tr>
  <tr><td><code>in</code></td><td>Boolean: triggers enter (true) or exit (false)</td></tr>
  <tr><td><code>timeout</code></td><td>Duration in ms (must match CSS transition duration)</td></tr>
  <tr><td><code>classNames</code></td><td>Prefix for the CSS classes (e.g., "fade" → "fade-enter")</td></tr>
  <tr><td><code>unmountOnExit</code></td><td>Remove from DOM after exit (default: keep mounted)</td></tr>
  <tr><td><code>mountOnEnter</code></td><td>Don&rsquo;t mount until <code>in</code> first becomes true</td></tr>
  <tr><td><code>nodeRef</code></td><td>Ref to the DOM node (recommended for StrictMode)</td></tr>
  <tr><td><code>onEntered</code> / <code>onExited</code></td><td>Lifecycle callbacks at each stage</td></tr>
</table>

<p><strong>Animating lists with TransitionGroup:</strong></p>

<pre><code>import { TransitionGroup, CSSTransition } from "react-transition-group";

function TodoList({ todos }) {
  return (
    &lt;TransitionGroup component="ul"&gt;
      {todos.map(todo =&gt; (
        &lt;CSSTransition key={todo.id} timeout={300} classNames="todo"&gt;
          &lt;li&gt;{todo.text}&lt;/li&gt;
        &lt;/CSSTransition&gt;
      ))}
    &lt;/TransitionGroup&gt;
  );
}</code></pre>

<p>When items are added/removed from the array, each gets enter/exit animations automatically &mdash; great for animated lists.</p>

<p><strong>Common gotchas:</strong></p>

<table>
  <tr><th>Issue</th><th>Fix</th></tr>
  <tr><td>Animation doesn&rsquo;t play on first render</td><td>Add <code>appear</code> prop &amp; CSS classes <code>.modal-appear</code>, <code>.modal-appear-active</code></td></tr>
  <tr><td><code>findDOMNode</code> warning in StrictMode</td><td>Use <code>nodeRef</code> prop with a <code>useRef</code></td></tr>
  <tr><td>Element flashes before animation</td><td>Make sure <code>.modal-enter</code> sets the start state immediately</td></tr>
  <tr><td>Timeout vs CSS duration mismatch</td><td>Keep them equal &mdash; or component unmounts mid-animation</td></tr>
</table>

<p><strong>For more complex needs</strong> &mdash; spring physics, gestures, layout animations, or list reordering &mdash; reach for <strong>Framer Motion</strong>. CSSTransition is great for simple class-based animations but lacks the polish features modern UI demands.</p>
'''

ANSWERS[86] = r'''
<p>Testing a React component means verifying that it <strong>renders correctly given various props</strong> and <strong>responds to user interactions</strong>. The modern standard is <strong>Vitest</strong> (or Jest) as the test runner + <strong>React Testing Library</strong> (RTL) as the rendering and querying library.</p>

<p><strong>Why React Testing Library:</strong></p>
<ul>
  <li><strong>Tests behavior, not implementation</strong> &mdash; queries by what the user sees (text, role, label).</li>
  <li><strong>Catches accessibility bugs</strong> &mdash; using ARIA roles makes screen-reader issues visible.</li>
  <li><strong>Refactor-safe</strong> &mdash; tests don&rsquo;t break when you change internal implementation, only when behavior changes.</li>
  <li><strong>Encourages testing the way users use the app</strong>.</li>
</ul>

<p><strong>Basic test &mdash; rendering and assertions:</strong></p>

<pre><code>import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Greeting from "./Greeting";

test("renders a greeting with the user&rsquo;s name", () =&gt; {
  render(&lt;Greeting name="Alice" /&gt;);
  expect(screen.getByText("Hello, Alice!")).toBeInTheDocument();
});

test("button click increments counter", async () =&gt; {
  const user = userEvent.setup();
  render(&lt;Counter /&gt;);

  expect(screen.getByText("Count: 0")).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: /increment/i }));

  expect(screen.getByText("Count: 1")).toBeInTheDocument();
});</code></pre>

<p><strong>The query priority order &mdash; how to find elements:</strong></p>

<table>
  <tr><th>Priority</th><th>Query</th><th>Use for</th></tr>
  <tr><td>1 (best)</td><td><code>getByRole</code></td><td>Buttons, headings, inputs &mdash; matches accessibility</td></tr>
  <tr><td>2</td><td><code>getByLabelText</code></td><td>Form inputs (matches associated label)</td></tr>
  <tr><td>3</td><td><code>getByPlaceholderText</code></td><td>Inputs without labels (less ideal)</td></tr>
  <tr><td>4</td><td><code>getByText</code></td><td>Visible text content</td></tr>
  <tr><td>5</td><td><code>getByDisplayValue</code></td><td>Form elements with current values</td></tr>
  <tr><td>6 (last resort)</td><td><code>getByTestId</code></td><td>When no semantic option exists</td></tr>
</table>

<p><strong>The three query variants:</strong></p>

<table>
  <tr><th>Variant</th><th>Returns</th><th>Throws if not found?</th></tr>
  <tr><td><code>getBy</code></td><td>The element</td><td>Yes</td></tr>
  <tr><td><code>queryBy</code></td><td>The element or null</td><td>No (use for "should not exist")</td></tr>
  <tr><td><code>findBy</code></td><td>Promise of element</td><td>Yes (waits up to 1s for it to appear)</td></tr>
</table>

<pre><code>// Use getBy when element should be there
expect(screen.getByText("Loaded!")).toBeInTheDocument();

// Use queryBy when checking absence
expect(screen.queryByText("Error")).not.toBeInTheDocument();

// Use findBy for async — waits for the element
expect(await screen.findByText("Loaded!")).toBeInTheDocument();</code></pre>

<p><strong>What NOT to test</strong>: implementation details. Don&rsquo;t test that <code>useState</code> is called, that a specific function name was used, that internal helper functions returned X. Test the <strong>behavior</strong>: "when user clicks save, the form data is submitted to the API."</p>

<p><strong>Don&rsquo;t use Enzyme in 2026</strong>: it&rsquo;s effectively abandoned (last major release supported React 17), encourages testing implementation details, and the React community has moved on. <strong>React Testing Library is the standard</strong>.</p>

<p><strong>Test runner choice</strong>: <strong>Vitest</strong> (Vite-native, faster) for new projects; <strong>Jest</strong> for existing CRA/Next.js apps. Both work identically with RTL.</p>
'''

ANSWERS[87] = r'''
<p><strong>Jest</strong> is a JavaScript test runner from Meta &mdash; for years the standard for testing React apps. It provides: a test runner, an assertion library (<code>expect</code>), mocking, snapshot testing, and code coverage. Used together with React Testing Library for the actual component testing.</p>

<p><strong>Setup &mdash; Jest comes pre-configured in Create React App and Next.js</strong>:</p>

<pre><code>// CRA / Next.js: already installed
// For Vite, install manually:
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

// jest.config.js
export default {
  testEnvironment: "jsdom",     // simulates browser DOM
  setupFilesAfterEach: ["./jest.setup.js"]
};

// jest.setup.js
import "@testing-library/jest-dom";    // adds custom matchers like .toBeInTheDocument</code></pre>

<p><strong>Basic Jest test structure:</strong></p>

<pre><code>// math.test.js
describe("add()", () =&gt; {
  test("adds two numbers", () =&gt; {
    expect(add(2, 3)).toBe(5);
  });

  test("returns 0 for no arguments", () =&gt; {
    expect(add()).toBe(0);
  });

  it("accepts negative numbers", () =&gt; {   // it() is alias for test()
    expect(add(-1, 1)).toBe(0);
  });
});</code></pre>

<p><strong>Common Jest matchers:</strong></p>

<table>
  <tr><th>Matcher</th><th>Use for</th></tr>
  <tr><td><code>toBe(value)</code></td><td>Strict equality (===)</td></tr>
  <tr><td><code>toEqual(value)</code></td><td>Deep equality for objects/arrays</td></tr>
  <tr><td><code>toBeTruthy()</code> / <code>toBeFalsy()</code></td><td>Truthy/falsy values</td></tr>
  <tr><td><code>toBeNull()</code> / <code>toBeUndefined()</code></td><td>null or undefined</td></tr>
  <tr><td><code>toContain(item)</code></td><td>Array contains item; string contains substring</td></tr>
  <tr><td><code>toHaveLength(n)</code></td><td>Array/string has expected length</td></tr>
  <tr><td><code>toMatch(regex)</code></td><td>String matches pattern</td></tr>
  <tr><td><code>toThrow(message)</code></td><td>Function throws an error</td></tr>
  <tr><td><code>toHaveBeenCalled()</code></td><td>Mock function was called</td></tr>
  <tr><td><code>toHaveBeenCalledWith(args)</code></td><td>Mock function called with specific args</td></tr>
</table>

<p><strong>RTL matchers (from <code>@testing-library/jest-dom</code>):</strong></p>

<table>
  <tr><th>Matcher</th><th>Tests for</th></tr>
  <tr><td><code>toBeInTheDocument()</code></td><td>Element is in the DOM</td></tr>
  <tr><td><code>toBeVisible()</code></td><td>Element is visible to the user</td></tr>
  <tr><td><code>toHaveTextContent(text)</code></td><td>Element contains text</td></tr>
  <tr><td><code>toHaveClass(name)</code></td><td>Element has the CSS class</td></tr>
  <tr><td><code>toBeDisabled()</code> / <code>toBeEnabled()</code></td><td>Form element disabled state</td></tr>
  <tr><td><code>toHaveValue(value)</code></td><td>Input has expected value</td></tr>
</table>

<p><strong>Setup and teardown:</strong></p>

<pre><code>describe("Component", () =&gt; {
  beforeAll(() =&gt; { /* runs once before all tests */ });
  beforeEach(() =&gt; { /* runs before each test */ });
  afterEach(() =&gt; { /* runs after each test */ });
  afterAll(() =&gt; { /* runs once after all tests */ });

  test("first test", () =&gt; { /* ... */ });
  test("second test", () =&gt; { /* ... */ });
});</code></pre>

<p><strong>Common scripts in package.json:</strong></p>

<pre><code>{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}</code></pre>

<p><strong>2026 reality &mdash; Vitest is increasingly popular</strong>: Vite-native test runner, Jest-compatible API (most Jest tests run in Vitest unchanged), much faster startup, native ESM support. For new Vite projects, choose Vitest. For CRA/Next.js, Jest remains the default. The testing patterns and matchers are nearly identical.</p>

<p><strong>Snapshot testing</strong>, <strong>mocking</strong>, and <strong>async testing</strong> &mdash; covered in Q90, Q92, Q93.</p>
'''

ANSWERS[88] = r'''
<p>A unit test for a React component verifies that <strong>given some props or interactions, the component renders the expected output</strong>. With React Testing Library, you focus on what the user sees and does &mdash; not internal implementation.</p>

<p><strong>Component to test:</strong></p>

<pre><code>// Counter.jsx
import { useState } from "react";

export default function Counter({ initial = 0, label = "Count" }) {
  const [count, setCount] = useState(initial);
  return (
    &lt;div&gt;
      &lt;p&gt;{label}: {count}&lt;/p&gt;
      &lt;button onClick={() =&gt; setCount(count + 1)}&gt;Increment&lt;/button&gt;
      &lt;button onClick={() =&gt; setCount(count - 1)}&gt;Decrement&lt;/button&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p><strong>Test file:</strong></p>

<pre><code>// Counter.test.jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Counter from "./Counter";

describe("Counter", () =&gt; {
  test("renders with default initial value of 0", () =&gt; {
    render(&lt;Counter /&gt;);
    expect(screen.getByText("Count: 0")).toBeInTheDocument();
  });

  test("respects custom initial value", () =&gt; {
    render(&lt;Counter initial={10} /&gt;);
    expect(screen.getByText("Count: 10")).toBeInTheDocument();
  });

  test("respects custom label", () =&gt; {
    render(&lt;Counter label="Score" /&gt;);
    expect(screen.getByText("Score: 0")).toBeInTheDocument();
  });

  test("increments when increment button clicked", async () =&gt; {
    const user = userEvent.setup();
    render(&lt;Counter /&gt;);

    await user.click(screen.getByRole("button", { name: /increment/i }));

    expect(screen.getByText("Count: 1")).toBeInTheDocument();
  });

  test("decrements when decrement button clicked", async () =&gt; {
    const user = userEvent.setup();
    render(&lt;Counter initial={5} /&gt;);

    await user.click(screen.getByRole("button", { name: /decrement/i }));

    expect(screen.getByText("Count: 4")).toBeInTheDocument();
  });
});</code></pre>

<p><strong>Anatomy of a unit test &mdash; AAA pattern:</strong></p>

<table>
  <tr><th>Phase</th><th>What happens</th></tr>
  <tr><td>Arrange</td><td>Set up the component (render with props)</td></tr>
  <tr><td>Act</td><td>Trigger an interaction (click, type, submit)</td></tr>
  <tr><td>Assert</td><td>Verify the expected outcome (text appears, function called)</td></tr>
</table>

<pre><code>test("submits form with name", async () =&gt; {
  // Arrange
  const onSubmit = jest.fn();
  const user = userEvent.setup();
  render(&lt;Form onSubmit={onSubmit} /&gt;);

  // Act
  await user.type(screen.getByLabelText("Name"), "Alice");
  await user.click(screen.getByRole("button", { name: /submit/i }));

  // Assert
  expect(onSubmit).toHaveBeenCalledWith({ name: "Alice" });
});</code></pre>

<p><strong>Best practices for component tests:</strong></p>
<ul>
  <li><strong>One concept per test</strong> &mdash; multiple assertions OK if testing the same behavior.</li>
  <li><strong>Descriptive names</strong> &mdash; "renders error when API fails" not "test 1".</li>
  <li><strong>Test behavior, not implementation</strong> &mdash; users don&rsquo;t care if you used <code>useState</code> or <code>useReducer</code>.</li>
  <li><strong>Query by role first</strong> &mdash; matches accessibility.</li>
  <li><strong>Use <code>userEvent</code>, not <code>fireEvent</code></strong> &mdash; simulates real user interactions more accurately.</li>
  <li><strong>Don&rsquo;t test third-party libs</strong> &mdash; trust they work; test your component&rsquo;s integration with them.</li>
</ul>

<p><strong>Testing common patterns:</strong></p>

<pre><code>// Conditional rendering
expect(screen.queryByText("Error")).not.toBeInTheDocument();   // not shown

// Calling parent callback
const onSelect = jest.fn();
render(&lt;Item onSelect={onSelect} /&gt;);
await user.click(screen.getByRole("button"));
expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ id: 1 }));

// Form input
const input = screen.getByLabelText("Email");
await user.type(input, "alice@example.com");
expect(input).toHaveValue("alice@example.com");</code></pre>
'''

ANSWERS[89] = r'''
<p><strong>Enzyme</strong> was a popular React testing library from Airbnb that provided shallow rendering, mounting, and a jQuery-like API for traversing component trees. It was the standard from 2016-2020 but has been <strong>effectively abandoned</strong>: the last major release officially supports only up to React 16, with community-maintained adapters for React 17 but <strong>no official support for React 18 or 19</strong>.</p>

<p><strong>The 2026 reality</strong>: <strong>do not use Enzyme for new projects</strong>. The React community has fully migrated to <strong>React Testing Library (RTL)</strong>, which is officially recommended by the React team.</p>

<p><strong>Why Enzyme fell out of favor:</strong></p>

<table>
  <tr><th>Issue</th><th>Why it&rsquo;s a problem</th></tr>
  <tr><td>Tests implementation details</td><td>Brittle &mdash; tests break when you refactor</td></tr>
  <tr><td>Shallow rendering encourages bad tests</td><td>Tests don&rsquo;t reflect actual component behavior</td></tr>
  <tr><td>Direct state inspection</td><td>Encourages "white box" tests of internals</td></tr>
  <tr><td>No official React 18+ support</td><td>Hooks, concurrent features, Suspense not properly tested</td></tr>
  <tr><td>Maintenance status</td><td>Effectively unmaintained as of 2022; no React Compiler support</td></tr>
</table>

<p><strong>Old Enzyme code (DON&rsquo;T write this in 2026):</strong></p>

<pre><code>// Enzyme — outdated approach
import { shallow } from "enzyme";
import Counter from "./Counter";

test("increments count on click", () =&gt; {
  const wrapper = shallow(&lt;Counter /&gt;);

  expect(wrapper.find("p").text()).toBe("Count: 0");

  wrapper.find("button.increment").simulate("click");

  expect(wrapper.state("count")).toBe(1);    // direct state inspection — bad
  expect(wrapper.find("p").text()).toBe("Count: 1");
});</code></pre>

<p><strong>Modern equivalent with React Testing Library:</strong></p>

<pre><code>// React Testing Library — modern approach
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Counter from "./Counter";

test("increments count on click", async () =&gt; {
  const user = userEvent.setup();
  render(&lt;Counter /&gt;);

  expect(screen.getByText("Count: 0")).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: /increment/i }));

  expect(screen.getByText("Count: 1")).toBeInTheDocument();
  // We don't inspect state directly — we verify the visible behavior
});</code></pre>

<p><strong>Migration mapping:</strong></p>

<table>
  <tr><th>Enzyme</th><th>React Testing Library</th></tr>
  <tr><td><code>shallow(&lt;Component /&gt;)</code></td><td><code>render(&lt;Component /&gt;)</code> (always full render)</td></tr>
  <tr><td><code>mount(&lt;Component /&gt;)</code></td><td><code>render(&lt;Component /&gt;)</code></td></tr>
  <tr><td><code>wrapper.find(...)</code></td><td><code>screen.getByRole/Text/Label(...)</code></td></tr>
  <tr><td><code>wrapper.simulate("click")</code></td><td><code>await user.click(element)</code></td></tr>
  <tr><td><code>wrapper.state()</code></td><td>(don&rsquo;t test state &mdash; test rendered output)</td></tr>
  <tr><td><code>wrapper.props()</code></td><td>(don&rsquo;t test props &mdash; test what they produce)</td></tr>
  <tr><td><code>wrapper.instance()</code></td><td>(no equivalent &mdash; test behavior, not internals)</td></tr>
</table>

<p><strong>If you encounter an Enzyme test in legacy code</strong>:</p>
<ul>
  <li><strong>Don&rsquo;t add new Enzyme tests</strong> &mdash; write new tests in RTL.</li>
  <li><strong>Migrate gradually</strong> &mdash; convert Enzyme tests to RTL when you change the component anyway.</li>
  <li><strong>Don&rsquo;t mix in the same file</strong> &mdash; pick one library per test file.</li>
  <li><strong>For React 18+</strong>, the unofficial <code>@cfaester/enzyme-adapter-react-18</code> exists but isn&rsquo;t officially supported &mdash; risk increases over time.</li>
</ul>

<p><strong>Bottom line for interview answers</strong>: acknowledge Enzyme exists historically, but state clearly that <strong>React Testing Library is the modern standard</strong> and that you wouldn&rsquo;t reach for Enzyme in new code. Knowing this is what interviewers want to hear.</p>
'''

ANSWERS[90] = r'''
<p>A <strong>snapshot test</strong> renders a component and saves its output (typically the rendered HTML) to a file. On subsequent runs, the new output is compared to the saved snapshot &mdash; if they differ, the test fails. It&rsquo;s a way to detect <strong>unintended UI changes</strong>.</p>

<p><strong>Basic snapshot test with Jest:</strong></p>

<pre><code>import { render } from "@testing-library/react";
import Greeting from "./Greeting";

test("Greeting renders correctly", () =&gt; {
  const { container } = render(&lt;Greeting name="Alice" /&gt;);
  expect(container).toMatchSnapshot();
});</code></pre>

<p><strong>First run</strong>: Jest creates <code>__snapshots__/Greeting.test.js.snap</code>:</p>

<pre><code>// __snapshots__/Greeting.test.js.snap
exports[`Greeting renders correctly 1`] = `
&lt;div&gt;
  &lt;h1
    class="greeting"
  &gt;
    Hello, Alice!
  &lt;/h1&gt;
&lt;/div&gt;
`;</code></pre>

<p><strong>Subsequent runs</strong>: Jest compares the new render to the saved snapshot. If different → test fails. If you intended the change → run <code>jest --updateSnapshot</code> (or press <code>u</code> in watch mode) to update.</p>

<p><strong>Inline snapshots &mdash; preferred for small components:</strong></p>

<pre><code>test("Button renders correctly", () =&gt; {
  const { container } = render(&lt;Button label="Save" /&gt;);
  expect(container).toMatchInlineSnapshot(`
    &lt;div&gt;
      &lt;button class="btn"&gt;
        Save
      &lt;/button&gt;
    &lt;/div&gt;
  `);
});</code></pre>

<p>Inline snapshots live in the test file itself &mdash; easier to review in code reviews; no separate snapshot file to look up.</p>

<p><strong>When snapshots are useful:</strong></p>
<ul>
  <li><strong>Static UI components</strong> with little dynamic content (buttons, badges, icons).</li>
  <li><strong>Catching regressions</strong> after refactors &mdash; "did my CSS class changes affect this component?"</li>
  <li><strong>Testing complex render output</strong> with many nested elements.</li>
  <li><strong>Verifying generated content</strong> &mdash; markdown rendering, code highlighting output.</li>
</ul>

<p><strong>Common pitfalls:</strong></p>

<table>
  <tr><th>Anti-pattern</th><th>Why it&rsquo;s bad</th></tr>
  <tr><td>Huge snapshots (1000+ lines)</td><td>Nobody actually reviews changes; just blindly runs <code>--updateSnapshot</code></td></tr>
  <tr><td>Snapshots of complex components with many states</td><td>Many overlapping snapshots; hard to reason about which changes are intended</td></tr>
  <tr><td>Snapshots as the only test</td><td>Misses behavior &mdash; need behavioral tests too</td></tr>
  <tr><td>Snapshots with timestamps, IDs, random data</td><td>Always fail; need to mock the dynamic values</td></tr>
</table>

<p><strong>Better approach for non-trivial components</strong>: use <strong>specific assertions</strong> for the parts that matter:</p>

<pre><code>// Less brittle than a full snapshot
test("Button renders with correct accessibility", () =&gt; {
  render(&lt;Button label="Save" disabled /&gt;);

  const btn = screen.getByRole("button", { name: "Save" });
  expect(btn).toBeDisabled();
  expect(btn).toHaveClass("btn");
});</code></pre>

<p><strong>Snapshot with stable mock data:</strong></p>

<pre><code>// Mock Date.now for snapshot stability
jest.useFakeTimers().setSystemTime(new Date("2024-01-01"));

test("renders timestamped item", () =&gt; {
  const { container } = render(&lt;Item createdAt={new Date()} /&gt;);
  expect(container).toMatchSnapshot();
});</code></pre>

<p><strong>2026 perspective</strong>: snapshots are useful but commonly overused. Reach for them when comparing complex output is genuinely easier than writing specific assertions. For most components, <strong>behavior-focused RTL queries</strong> are clearer and more maintainable. Many teams reserve snapshots for design-system primitives where any change really should require explicit review.</p>
'''

ANSWERS[91] = r'''
<p>The <strong><code>act()</code></strong> function tells React: "I&rsquo;m about to do something that updates state &mdash; flush all the resulting renders, effects, and updates before continuing." It ensures the test sees a consistent UI state, with all React updates applied.</p>

<p><strong>The good news</strong>: with React Testing Library and modern React, <strong>you almost never need to call <code>act()</code> directly</strong>. RTL wraps its methods (<code>render</code>, <code>fireEvent</code>, <code>userEvent</code>) in <code>act()</code> automatically.</p>

<p><strong>When you DO see <code>act()</code> warnings:</strong></p>

<pre><code>Warning: An update to MyComponent inside a test was not wrapped in act(...).

When testing, code that causes React state updates should be wrapped into act(...):

act(() =&gt; {
  /* fire events that update state */
});</code></pre>

<p>This warning means your test triggered a state update that React noticed but the test didn&rsquo;t handle properly &mdash; usually an async update completed after the test "finished."</p>

<p><strong>Common causes and fixes:</strong></p>

<table>
  <tr><th>Cause</th><th>Fix</th></tr>
  <tr><td>Async update after test ends</td><td>Use <code>findBy*</code> queries to wait for the update</td></tr>
  <tr><td>setState after unmount</td><td>Cleanup async work in <code>useEffect</code> return</td></tr>
  <tr><td>Direct manipulation outside RTL helpers</td><td>Wrap in <code>await act(async () =&gt; { ... })</code></td></tr>
  <tr><td>Timer-based updates</td><td>Use <code>jest.useFakeTimers()</code> and advance them inside <code>act</code></td></tr>
</table>

<p><strong>Example &mdash; async update warning and fix:</strong></p>

<pre><code>// PROBLEM: state updates after API call but test doesn&rsquo;t wait
test("fetches and displays user", () =&gt; {
  render(&lt;UserProfile id={1} /&gt;);
  // Test ends, but the fetch is still pending → act warning
});

// FIX: use findBy* to wait for the rendered result
test("fetches and displays user", async () =&gt; {
  render(&lt;UserProfile id={1} /&gt;);
  expect(await screen.findByText("Alice")).toBeInTheDocument();
  // findBy* polls until found, wrapping internally in act()
});</code></pre>

<p><strong>Manual <code>act</code> &mdash; only when RTL helpers don&rsquo;t fit:</strong></p>

<pre><code>import { act } from "react";   // React 18.3+: from "react"
                                  // Older versions: from "react-dom/test-utils"

test("manual state update via ref", async () =&gt; {
  const ref = createRef();
  render(&lt;Counter ref={ref} /&gt;);

  // Trigger an imperative method via ref — RTL doesn't know about this
  await act(async () =&gt; {
    ref.current.increment();
  });

  expect(screen.getByText("Count: 1")).toBeInTheDocument();
});</code></pre>

<p><strong>Async <code>act</code> for promises:</strong></p>

<pre><code>await act(async () =&gt; {
  await fetchSomething();      // promise inside act
  // any state updates that result are flushed
});</code></pre>

<p><strong>Three reasons RTL handles act for you:</strong></p>
<ol>
  <li><code>render()</code> wraps initial mount in <code>act()</code>.</li>
  <li><code>userEvent.click()</code>, <code>userEvent.type()</code>, etc., are async and wrap interactions.</li>
  <li><code>findBy*</code>, <code>waitFor</code>, and <code>waitForElementToBeRemoved</code> all use <code>act</code> internally.</li>
</ol>

<p><strong>If you see <code>act</code> warnings constantly</strong>, you&rsquo;re probably:</p>
<ul>
  <li>Using <code>fireEvent</code> for things that trigger async updates &mdash; switch to <code>userEvent</code>.</li>
  <li>Not awaiting promises in tests &mdash; add <code>await</code>.</li>
  <li>Using <code>getBy</code> instead of <code>findBy</code> for elements that appear async.</li>
  <li>Running effects against real timers &mdash; consider <code>jest.useFakeTimers()</code>.</li>
</ul>

<p><strong>2026 status</strong>: <code>act</code> is now imported from <code>"react"</code> in React 18.3+ (was previously in <code>"react-dom/test-utils"</code>). For most tests, you&rsquo;ll never type <code>act</code> manually &mdash; treat <code>act</code> warnings as bug indicators that point to async issues in your tests.</p>
'''

ANSWERS[92] = r'''
<p>Mocking API calls in React tests prevents real network requests, makes tests fast and deterministic, and lets you simulate any scenario (success, error, slow response, empty data). The two main approaches: <strong>mock the fetch/axios function directly</strong>, or <strong>intercept HTTP at a higher level with MSW</strong> (Mock Service Worker).</p>

<p><strong>Approach 1 &mdash; mock <code>fetch</code> with Jest:</strong></p>

<pre><code>// Setup mock before tests
beforeEach(() =&gt; {
  global.fetch = jest.fn();
});

afterEach(() =&gt; {
  jest.restoreAllMocks();
});

test("displays user data", async () =&gt; {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () =&gt; ({ id: 1, name: "Alice" })
  });

  render(&lt;UserProfile userId={1} /&gt;);

  expect(await screen.findByText("Alice")).toBeInTheDocument();
});

test("displays error on fetch failure", async () =&gt; {
  global.fetch.mockResolvedValueOnce({ ok: false, status: 500 });

  render(&lt;UserProfile userId={1} /&gt;);

  expect(await screen.findByText(/error/i)).toBeInTheDocument();
});</code></pre>

<p><strong>Approach 2 &mdash; mock axios with Jest:</strong></p>

<pre><code>import axios from "axios";

jest.mock("axios");

test("loads posts via axios", async () =&gt; {
  axios.get.mockResolvedValueOnce({
    data: [{ id: 1, title: "Hello" }]
  });

  render(&lt;PostList /&gt;);
  expect(await screen.findByText("Hello")).toBeInTheDocument();
});</code></pre>

<p><strong>Approach 3 &mdash; MSW (Mock Service Worker), the modern recommendation:</strong></p>

<pre><code>// mocks/handlers.js
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users/:id", ({ params }) =&gt; {
    return HttpResponse.json({ id: params.id, name: "Alice" });
  }),

  http.get("/api/posts", () =&gt; {
    return HttpResponse.json([
      { id: 1, title: "First post" },
      { id: 2, title: "Second post" }
    ]);
  })
];</code></pre>

<pre><code>// mocks/server.js (for tests)
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);

// jest.setup.js
beforeAll(() =&gt; server.listen());
afterEach(() =&gt; server.resetHandlers());
afterAll(() =&gt; server.close());</code></pre>

<p><strong>Test using MSW:</strong></p>

<pre><code>import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";

test("displays user", async () =&gt; {
  // handlers from setup are active by default
  render(&lt;UserProfile userId={1} /&gt;);
  expect(await screen.findByText("Alice")).toBeInTheDocument();
});

test("handles 500 error", async () =&gt; {
  // override the default handler for this test
  server.use(
    http.get("/api/users/:id", () =&gt; HttpResponse.error())
  );

  render(&lt;UserProfile userId={1} /&gt;);
  expect(await screen.findByText(/error/i)).toBeInTheDocument();
});</code></pre>

<p><strong>Comparison:</strong></p>

<table>
  <tr><th></th><th>Mock fetch/axios</th><th>MSW</th></tr>
  <tr><td>Setup complexity</td><td>Low</td><td>Medium (one-time setup)</td></tr>
  <tr><td>Tests what they call</td><td>Tests the fetch interface</td><td>Tests the actual HTTP request &amp; response</td></tr>
  <tr><td>Reuse for development</td><td>No</td><td>Yes &mdash; same handlers in browser dev mode</td></tr>
  <tr><td>Refactor safety</td><td>Breaks if you switch fetch → axios</td><td>Survives any HTTP client change</td></tr>
  <tr><td>2026 recommendation</td><td>Quick tests, simple cases</td><td>Production apps, complex API surfaces</td></tr>
</table>

<p><strong>For TanStack Query / RTK Query tests</strong>: MSW is essentially required. Mocking the data-fetching library directly defeats the purpose of those libraries.</p>

<p><strong>Best practice</strong>: invest in MSW for any non-trivial app. The investment pays back many times over &mdash; tests stay valid through refactors, dev experience improves, and you have a single source of truth for mock API behavior across tests, Storybook, and local development.</p>
'''

ANSWERS[93] = r'''
<p>Asynchronous code in React tests &mdash; data fetching, timers, animations &mdash; requires <strong>waiting</strong> for state updates to complete before asserting. React Testing Library provides three primary tools: <strong><code>findBy*</code></strong> queries (wait until found), <strong><code>waitFor</code></strong> (wait for any condition), and <strong><code>waitForElementToBeRemoved</code></strong> (wait for unmount).</p>

<p><strong><code>findBy*</code> &mdash; wait for an element to appear:</strong></p>

<pre><code>test("loads and displays user data", async () =&gt; {
  render(&lt;UserProfile userId={1} /&gt;);

  // Component starts in loading state, then fetches user, then displays
  // findByText polls every 50ms for up to 1 second by default
  expect(await screen.findByText("Alice")).toBeInTheDocument();
});</code></pre>

<p><code>findBy*</code> is the cleanest async approach &mdash; matches the pattern of <code>getBy*</code> but waits for the element to exist. Use it whenever you&rsquo;re testing UI that updates after async work.</p>

<p><strong><code>waitFor</code> &mdash; wait for any custom condition:</strong></p>

<pre><code>import { waitFor } from "@testing-library/react";

test("submits form and shows success", async () =&gt; {
  const user = userEvent.setup();
  render(&lt;ContactForm /&gt;);

  await user.type(screen.getByLabelText("Email"), "alice@example.com");
  await user.click(screen.getByRole("button", { name: /submit/i }));

  // Wait for the API call to complete and message to appear
  await waitFor(() =&gt; {
    expect(screen.getByText("Submitted!")).toBeInTheDocument();
  });
});

// Or for absence
await waitFor(() =&gt; {
  expect(screen.queryByText("Loading")).not.toBeInTheDocument();
});</code></pre>

<p><strong><code>waitForElementToBeRemoved</code> &mdash; wait for something to disappear:</strong></p>

<pre><code>test("loading spinner is removed after data loads", async () =&gt; {
  render(&lt;Posts /&gt;);

  // Wait for the loading state to go away
  await waitForElementToBeRemoved(() =&gt; screen.getByText("Loading..."));

  expect(screen.getByText("Welcome")).toBeInTheDocument();
});</code></pre>

<p><strong>Mocking timers:</strong></p>

<pre><code>jest.useFakeTimers();

test("debounced search triggers after delay", async () =&gt; {
  const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
  const onSearch = jest.fn();

  render(&lt;SearchInput onSearch={onSearch} delay={500} /&gt;);

  await user.type(screen.getByRole("textbox"), "hello");
  expect(onSearch).not.toHaveBeenCalled();

  // Fast-forward 500ms
  jest.advanceTimersByTime(500);
  expect(onSearch).toHaveBeenCalledWith("hello");
});

afterEach(() =&gt; {
  jest.useRealTimers();
});</code></pre>

<p><strong>Common async patterns:</strong></p>

<table>
  <tr><th>Pattern</th><th>Tool</th></tr>
  <tr><td>Element appears after fetch</td><td><code>await screen.findByText(...)</code></td></tr>
  <tr><td>Loading spinner disappears</td><td><code>await waitForElementToBeRemoved(...)</code></td></tr>
  <tr><td>Multiple conditions</td><td><code>await waitFor(() =&gt; { ... })</code></td></tr>
  <tr><td>Timer-based delay</td><td><code>jest.useFakeTimers()</code> + <code>jest.advanceTimersByTime</code></td></tr>
  <tr><td>Promise.resolve in setup</td><td>Just <code>await</code> the promise</td></tr>
  <tr><td>Polling / setInterval</td><td>Fake timers + <code>act</code> for each tick</td></tr>
</table>

<p><strong>Common mistakes:</strong></p>

<pre><code>// WRONG — getBy throws immediately if not yet present
render(&lt;Posts /&gt;);
expect(screen.getByText("Loaded!")).toBeInTheDocument();   // ✗ throws

// CORRECT — findBy waits for the element
render(&lt;Posts /&gt;);
expect(await screen.findByText("Loaded!")).toBeInTheDocument();   // ✓

// WRONG — multiple assertions in waitFor (only the first matters for the wait)
await waitFor(() =&gt; {
  expect(screen.getByText("Title")).toBeInTheDocument();
  expect(api.fetch).toHaveBeenCalled();
});

// CORRECT — split or use a single condition
await waitFor(() =&gt; expect(screen.getByText("Title")).toBeInTheDocument());
expect(api.fetch).toHaveBeenCalled();</code></pre>

<p><strong>Default timeouts</strong>:</p>

<table>
  <tr><th>Function</th><th>Default timeout</th></tr>
  <tr><td><code>findBy*</code></td><td>1000ms (1 second)</td></tr>
  <tr><td><code>waitFor</code></td><td>1000ms</td></tr>
  <tr><td><code>waitForElementToBeRemoved</code></td><td>1000ms</td></tr>
</table>

<p>Override per-call: <code>findByText("foo", {}, { timeout: 5000 })</code>. Or globally in setup: <code>configure({ asyncUtilTimeout: 5000 })</code>.</p>

<p><strong>Don&rsquo;t use <code>setTimeout</code> in tests</strong> &mdash; flaky and slow. Always use proper async helpers and fake timers when needed.</p>
'''

ANSWERS[94] = r'''
<p><strong><code>fireEvent</code></strong> dispatches synthetic DOM events on elements &mdash; click, change, submit, keyboard events, etc. It&rsquo;s the lower-level event utility from React Testing Library. <strong>For most modern tests, prefer <code>userEvent</code></strong> &mdash; it more accurately simulates real user interactions.</p>

<p><strong>Basic <code>fireEvent</code> usage:</strong></p>

<pre><code>import { fireEvent, render, screen } from "@testing-library/react";

test("button click increments counter", () =&gt; {
  render(&lt;Counter /&gt;);

  const button = screen.getByRole("button", { name: /increment/i });
  fireEvent.click(button);

  expect(screen.getByText("Count: 1")).toBeInTheDocument();
});

test("input change updates value", () =&gt; {
  render(&lt;SearchBox /&gt;);

  const input = screen.getByRole("textbox");
  fireEvent.change(input, { target: { value: "react" } });

  expect(input).toHaveValue("react");
});</code></pre>

<p><strong>Common <code>fireEvent</code> methods:</strong></p>

<table>
  <tr><th>Method</th><th>Purpose</th></tr>
  <tr><td><code>fireEvent.click(element)</code></td><td>Click event</td></tr>
  <tr><td><code>fireEvent.change(input, { target: { value } })</code></td><td>Form input change</td></tr>
  <tr><td><code>fireEvent.submit(form)</code></td><td>Form submission</td></tr>
  <tr><td><code>fireEvent.keyDown(elem, { key: "Enter" })</code></td><td>Keyboard event</td></tr>
  <tr><td><code>fireEvent.focus(input)</code></td><td>Focus event</td></tr>
  <tr><td><code>fireEvent.blur(input)</code></td><td>Blur event</td></tr>
  <tr><td><code>fireEvent.mouseEnter(elem)</code></td><td>Mouse hover</td></tr>
</table>

<p><strong><code>fireEvent</code> vs <code>userEvent</code> &mdash; the critical difference:</strong></p>

<table>
  <tr><th></th><th><code>fireEvent</code></th><th><code>userEvent</code></th></tr>
  <tr><td>Speed</td><td>Synchronous</td><td>Async (more realistic)</td></tr>
  <tr><td>Simulates real interaction</td><td>Single event</td><td>Full sequence (focus, change, blur, click)</td></tr>
  <tr><td>Typing</td><td>One <code>change</code> event</td><td>Individual keypress for each character</td></tr>
  <tr><td>Click</td><td>Just dispatches click</td><td>Mousemove → mousedown → mouseup → click → focus</td></tr>
  <tr><td>Recommended</td><td>For low-level event tests</td><td>For most user-interaction tests (preferred)</td></tr>
</table>

<p><strong>The same test with both:</strong></p>

<pre><code>// fireEvent — fires one synthetic change
fireEvent.change(input, { target: { value: "hello" } });

// userEvent — types each character, fires keydown/keypress/input/keyup per char
const user = userEvent.setup();
await user.type(input, "hello");</code></pre>

<p><strong>When <code>userEvent</code> matters &mdash; debounced inputs:</strong></p>

<pre><code>// PROBLEM: fireEvent fires one event, debounce may miss it
fireEvent.change(input, { target: { value: "react" } });

// Better: userEvent simulates real typing → debounce activates correctly
await user.type(input, "react");</code></pre>

<p><strong>When <code>fireEvent</code> is still useful:</strong></p>
<ul>
  <li><strong>Custom events</strong> &mdash; <code>fireEvent(element, new CustomEvent(...))</code>.</li>
  <li><strong>Performance-critical tests</strong> &mdash; <code>fireEvent</code> is synchronous, faster.</li>
  <li><strong>Edge cases</strong> &mdash; testing event handlers in isolation.</li>
  <li><strong>Things <code>userEvent</code> doesn&rsquo;t support directly</strong> &mdash; e.g., scroll events.</li>
</ul>

<p><strong>Setup userEvent properly:</strong></p>

<pre><code>import userEvent from "@testing-library/user-event";

test("user types in search", async () =&gt; {
  const user = userEvent.setup();      // create instance per test
  render(&lt;SearchBox /&gt;);

  await user.type(screen.getByRole("textbox"), "react");
  await user.click(screen.getByRole("button", { name: /search/i }));

  // assertions...
});</code></pre>

<p><strong>2026 best practice</strong>: <strong>default to <code>userEvent</code></strong> for all interaction tests. It produces tests that are more representative of real user behavior, catches more bugs, and integrates well with async patterns. Reach for <code>fireEvent</code> only when you have a specific reason (a custom event, a synthetic-only DOM API, etc.).</p>
'''

ANSWERS[95] = r'''
<p>Simulating user interactions in React tests is best done with <strong><code>@testing-library/user-event</code></strong> &mdash; a library built on top of <code>fireEvent</code> that mimics real user behavior more faithfully. It dispatches the full sequence of events that a real interaction triggers (focus, mousedown, mouseup, click, etc.) instead of a single synthetic event.</p>

<p><strong>Setup:</strong></p>

<pre><code>import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("login form", async () =&gt; {
  // Create a userEvent instance — once per test
  const user = userEvent.setup();
  render(&lt;LoginForm /&gt;);

  // ...interactions...
});</code></pre>

<p><strong>Common interaction methods:</strong></p>

<table>
  <tr><th>Method</th><th>Simulates</th></tr>
  <tr><td><code>user.click(element)</code></td><td>Mouse click (full sequence: down, up, click, focus)</td></tr>
  <tr><td><code>user.dblClick(element)</code></td><td>Double click</td></tr>
  <tr><td><code>user.type(input, "text")</code></td><td>Typing each character with key events</td></tr>
  <tr><td><code>user.clear(input)</code></td><td>Select all + delete</td></tr>
  <tr><td><code>user.tab()</code></td><td>Tab to next focusable element</td></tr>
  <tr><td><code>user.keyboard("{Enter}")</code></td><td>Press a key (or sequence)</td></tr>
  <tr><td><code>user.hover(element)</code></td><td>Mouse hover</td></tr>
  <tr><td><code>user.unhover(element)</code></td><td>Move mouse away</td></tr>
  <tr><td><code>user.selectOptions(select, value)</code></td><td>Choose option in &lt;select&gt;</td></tr>
  <tr><td><code>user.upload(input, file)</code></td><td>File upload</td></tr>
</table>

<p><strong>Realistic interaction example:</strong></p>

<pre><code>test("user logs in", async () =&gt; {
  const user = userEvent.setup();
  const onLogin = jest.fn();

  render(&lt;LoginForm onLogin={onLogin} /&gt;);

  // Type into fields
  await user.type(screen.getByLabelText("Email"), "alice@example.com");
  await user.type(screen.getByLabelText("Password"), "secret123");

  // Submit form
  await user.click(screen.getByRole("button", { name: /sign in/i }));

  // Verify the callback received the data
  expect(onLogin).toHaveBeenCalledWith({
    email: "alice@example.com",
    password: "secret123"
  });
});</code></pre>

<p><strong>Keyboard interactions &mdash; special keys:</strong></p>

<pre><code>// Special keys are wrapped in {...}
await user.keyboard("{Enter}");        // press Enter
await user.keyboard("{Escape}");       // press Escape
await user.keyboard("{Tab}");          // tab forward
await user.keyboard("{Shift&gt;}{Tab}{/Shift}");   // Shift+Tab
await user.keyboard("a{Enter}b");      // type "a", press Enter, type "b"

// Modifier combinations
await user.keyboard("{Control&gt;}c{/Control}");    // Ctrl+C
await user.keyboard("{Meta&gt;}{Enter}{/Meta}");    // Cmd+Enter (Mac)</code></pre>

<p><strong>Form field testing:</strong></p>

<pre><code>// Text input
await user.type(input, "hello");

// Clear and replace
await user.clear(input);
await user.type(input, "new value");

// Checkbox/radio
await user.click(screen.getByLabelText("I agree"));
expect(screen.getByLabelText("I agree")).toBeChecked();

// Select dropdown
await user.selectOptions(
  screen.getByLabelText("Country"),
  "United States"
);

// File upload
const file = new File(["hello"], "hello.txt", { type: "text/plain" });
await user.upload(screen.getByLabelText("Upload"), file);</code></pre>

<p><strong>Why prefer <code>userEvent</code> over <code>fireEvent</code>:</strong></p>

<ul>
  <li><strong>Catches more bugs</strong> &mdash; tests fail when components have accessibility issues (e.g., a button that&rsquo;s not actually focusable).</li>
  <li><strong>Realistic event sequences</strong> &mdash; the order of focus/blur/change matters in real apps.</li>
  <li><strong>Better support for keyboard navigation</strong> &mdash; tab order, focus management, modifier keys.</li>
  <li><strong>Built-in async handling</strong> &mdash; awaiting interactions makes tests more reliable.</li>
</ul>

<p><strong>Watch out for:</strong></p>

<table>
  <tr><th>Gotcha</th><th>Solution</th></tr>
  <tr><td>Forgetting <code>await</code></td><td>All <code>userEvent</code> methods are async; always await them</td></tr>
  <tr><td>Calling <code>userEvent.setup()</code> only once</td><td>Use one setup per test &mdash; ensures clean state</td></tr>
  <tr><td>Trying to type in a disabled input</td><td>userEvent throws &mdash; matches real browser behavior</td></tr>
  <tr><td>Fake timers + userEvent</td><td>Pass <code>{ advanceTimers: jest.advanceTimersByTime }</code> to setup</td></tr>
</table>

<p><strong>2026 standard</strong>: <code>userEvent</code> v14+ with <code>setup()</code> pattern is the de-facto way to simulate user interactions. It works seamlessly with React 19, Vitest, and Jest.</p>
'''

ANSWERS[96] = r'''
<p><strong>Important &mdash; Create React App (CRA) is officially deprecated as of February 2025.</strong> The React team itself recommended in early 2025 that <strong>new projects should use Vite, Next.js, Remix, or other modern frameworks</strong>. CRA is no longer maintained.</p>

<p><strong>For new React projects in 2026, use Vite instead:</strong></p>

<pre><code>// Vite — modern recommended replacement for CRA
npm create vite@latest my-app -- --template react

# Or with TypeScript
npm create vite@latest my-app -- --template react-ts

cd my-app
npm install
npm run dev      # development server with HMR
npm run build    # production build
npm run preview  # preview production build locally</code></pre>

<p><strong>Why Vite replaced CRA:</strong></p>

<table>
  <tr><th></th><th>CRA (deprecated)</th><th>Vite (recommended)</th></tr>
  <tr><td>Dev server startup</td><td>10-30+ seconds</td><td>&lt;1 second</td></tr>
  <tr><td>HMR (hot module replacement)</td><td>1-5 seconds per change</td><td>&lt;100ms</td></tr>
  <tr><td>Build tool</td><td>Webpack (slow)</td><td>esbuild + Rollup (fast)</td></tr>
  <tr><td>Configuration</td><td>"Eject" or use craco</td><td>Simple <code>vite.config.js</code></td></tr>
  <tr><td>Bundle size</td><td>Larger</td><td>Smaller (better tree-shaking)</td></tr>
  <tr><td>TypeScript support</td><td>Slow type checking</td><td>Native esbuild &mdash; instant</td></tr>
  <tr><td>Status</td><td>Deprecated 2025</td><td>Active, recommended</td></tr>
</table>

<p><strong>For historical reference &mdash; old CRA setup:</strong></p>

<pre><code>// Old CRA workflow (don&rsquo;t use for new projects)
npx create-react-app my-app
cd my-app
npm start         # dev server
npm test          # run tests
npm run build     # production build

// Or with TypeScript
npx create-react-app my-app --template typescript</code></pre>

<p>CRA generated a project structure with <code>public/</code>, <code>src/</code>, and a hidden Webpack config. To customize the config, you had to "eject" (irreversible) or use libraries like <code>craco</code> &mdash; both painful.</p>

<p><strong>Modern alternatives in 2026:</strong></p>

<table>
  <tr><th>Tool</th><th>Best for</th></tr>
  <tr><td>Vite</td><td>SPAs, libraries, simple sites &mdash; closest to old CRA experience</td></tr>
  <tr><td>Next.js</td><td>Full-stack React apps, SEO-critical sites, Server Components</td></tr>
  <tr><td>Remix</td><td>Full-stack apps with strong web standards, nested layouts</td></tr>
  <tr><td>TanStack Start</td><td>New &mdash; type-safe full-stack with file-based routing</td></tr>
  <tr><td>Astro</td><td>Content-heavy sites with islands of interactivity</td></tr>
</table>

<p><strong>Migrating from CRA to Vite:</strong></p>

<ol>
  <li>Create a new Vite project alongside your CRA project.</li>
  <li>Copy <code>src/</code> into the Vite project.</li>
  <li>Move <code>public/index.html</code> to the project root (Vite expects it there).</li>
  <li>Update <code>index.html</code> to import the entry: <code>&lt;script type="module" src="/src/main.jsx"&gt;</code>.</li>
  <li>Update environment variables: <code>process.env.REACT_APP_*</code> → <code>import.meta.env.VITE_*</code>.</li>
  <li>Replace <code>react-scripts</code> with Vite scripts in <code>package.json</code>.</li>
</ol>

<p><strong>For interview answers in 2026</strong>: lead with the fact that CRA is deprecated. Show you know the modern alternatives. If asked about CRA specifically, explain how it worked historically and why it was retired (slow Webpack-based build, lack of customization without ejection, no SSR support).</p>
'''

ANSWERS[97] = r'''
<p>A custom Webpack config gives you full control over how your React app bundles &mdash; useful for specific optimizations, complex monorepos, or legacy projects. <strong>For new projects in 2026, prefer Vite</strong>; reach for custom Webpack only when you have a specific reason.</p>

<p><strong>Minimal React + Webpack setup:</strong></p>

<pre><code>npm install --save-dev webpack webpack-cli webpack-dev-server \
  babel-loader @babel/core @babel/preset-env @babel/preset-react \
  html-webpack-plugin css-loader style-loader

npm install react react-dom</code></pre>

<p><strong><code>webpack.config.js</code>:</strong></p>

<pre><code>const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  entry: "./src/index.jsx",

  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].[contenthash].js",
    clean: true   // wipe dist/ before each build
  },

  resolve: {
    extensions: [".js", ".jsx", ".ts", ".tsx"]
  },

  module: {
    rules: [
      // JS/JSX → Babel
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", ["@babel/preset-react", { runtime: "automatic" }]]
          }
        }
      },
      // CSS
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      },
      // Images
      {
        test: /\.(png|jpg|jpeg|gif|svg)$/,
        type: "asset/resource"
      }
    ]
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: "./public/index.html"
    })
  ],

  devServer: {
    static: "./dist",
    hot: true,
    port: 3000,
    historyApiFallback: true   // for React Router
  },

  mode: process.env.NODE_ENV === "production" ? "production" : "development"
};</code></pre>

<p><strong>Common configuration patterns:</strong></p>

<table>
  <tr><th>Goal</th><th>Add</th></tr>
  <tr><td>TypeScript</td><td><code>ts-loader</code> or <code>@babel/preset-typescript</code></td></tr>
  <tr><td>SCSS / SASS</td><td><code>sass-loader</code></td></tr>
  <tr><td>CSS Modules</td><td><code>css-loader</code> with <code>{ modules: true }</code></td></tr>
  <tr><td>Code splitting (lazy load)</td><td>Built-in &mdash; use dynamic <code>import()</code></td></tr>
  <tr><td>Environment variables</td><td><code>webpack.DefinePlugin</code> + <code>dotenv</code></td></tr>
  <tr><td>Bundle analysis</td><td><code>webpack-bundle-analyzer</code></td></tr>
  <tr><td>Production minification</td><td><code>terser-webpack-plugin</code> (default in mode: production)</td></tr>
</table>

<p><strong>Optimizing for production:</strong></p>

<pre><code>// webpack.config.js production additions
optimization: {
  splitChunks: {
    chunks: "all",                  // split shared code
    cacheGroups: {
      vendor: {                     // vendor bundle for node_modules
        test: /[\\/]node_modules[\\/]/,
        name: "vendors",
        chunks: "all"
      }
    }
  },
  runtimeChunk: "single"             // separate runtime
},

// Long-term caching with content hashes
output: {
  filename: "[name].[contenthash].js",
  chunkFilename: "[name].[contenthash].chunk.js"
}</code></pre>

<p><strong>Environment variables:</strong></p>

<pre><code>const webpack = require("webpack");

plugins: [
  new webpack.DefinePlugin({
    "process.env.API_URL": JSON.stringify(process.env.API_URL),
    "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV)
  })
]

// In your code
const apiUrl = process.env.API_URL;</code></pre>

<p><strong>Common scripts:</strong></p>

<pre><code>"scripts": {
  "dev": "webpack serve --mode development",
  "build": "webpack --mode production",
  "analyze": "webpack-bundle-analyzer dist/stats.json"
}</code></pre>

<p><strong>2026 perspective</strong>: writing custom Webpack configs is rarely necessary anymore. <strong>Vite uses esbuild + Rollup for 10-100x faster builds</strong> with simpler config. Webpack remains entrenched in older codebases and Next.js (which uses Webpack/Turbopack). For interview answers: know how Webpack works conceptually (entry, loaders, plugins, output), but recommend modern bundlers for new projects unless there&rsquo;s a specific Webpack-only requirement.</p>
'''

ANSWERS[98] = r'''
<p>The <strong><code>.env</code> file</strong> stores environment variables &mdash; configuration values that vary between environments (development, staging, production) without hardcoding them in source. The build tool reads these at build time and embeds them in your JavaScript bundle.</p>

<p><strong>Basic <code>.env</code> usage:</strong></p>

<pre><code># .env (in project root)
VITE_API_URL=https://api.example.com
VITE_GOOGLE_ANALYTICS_ID=G-1234567890
VITE_FEATURE_FLAGS=newUI,betaPayments</code></pre>

<p><strong>Reading variables in your React code:</strong></p>

<pre><code>// Vite syntax
const apiUrl = import.meta.env.VITE_API_URL;

// Create React App (deprecated) syntax
const apiUrl = process.env.REACT_APP_API_URL;

// Next.js syntax
const apiUrl = process.env.NEXT_PUBLIC_API_URL;        // exposed to browser
const secret = process.env.SECRET;                      // server-only</code></pre>

<p><strong>Critical &mdash; the prefix matters:</strong></p>

<table>
  <tr><th>Build tool</th><th>Required prefix for client-side</th><th>Why</th></tr>
  <tr><td>Vite</td><td><code>VITE_</code></td><td>Only prefixed vars are exposed to browser</td></tr>
  <tr><td>CRA</td><td><code>REACT_APP_</code></td><td>Same reason</td></tr>
  <tr><td>Next.js</td><td><code>NEXT_PUBLIC_</code></td><td>Same reason; non-prefixed are server-only</td></tr>
  <tr><td>Webpack (custom)</td><td>Whatever you configure with DefinePlugin</td><td>Manual setup</td></tr>
</table>

<p><strong>The prefix prevents accidental leaks</strong>: server secrets like database credentials, API tokens, etc., should never end up in the client bundle. The prefix system enforces explicit opt-in.</p>

<p><strong>Multiple environments:</strong></p>

<pre><code># .env                  ← loaded in all environments (defaults)
# .env.local             ← local overrides; gitignored
# .env.development       ← loaded in dev (npm run dev)
# .env.production        ← loaded in production builds
# .env.test              ← loaded during testing</code></pre>

<p>Typically you commit <code>.env</code> with safe defaults; <code>.env.local</code> is gitignored and contains personal/sensitive overrides.</p>

<p><strong>Example multi-environment setup:</strong></p>

<pre><code># .env (committed)
VITE_API_URL=https://api.example.com
VITE_FEATURE_NEW_UI=false

# .env.development (committed)
VITE_API_URL=http://localhost:3001
VITE_FEATURE_NEW_UI=true

# .env.local (gitignored — personal overrides)
VITE_API_URL=http://localhost:3001
VITE_DEBUG_MODE=true</code></pre>

<p><strong>The <code>.gitignore</code> rule:</strong></p>

<pre><code># .gitignore
.env.local
.env.*.local

# DO commit .env (with safe defaults), .env.development, .env.production
# DON'T commit .env.local (personal/secrets)</code></pre>

<p><strong>Important security warnings:</strong></p>

<table>
  <tr><th>Rule</th><th>Why</th></tr>
  <tr><td>Never put secrets in client-side env vars</td><td>They&rsquo;re embedded in the JS bundle &mdash; visible to anyone</td></tr>
  <tr><td>Never put database credentials, API keys, JWT secrets in any prefixed var</td><td>Same reason</td></tr>
  <tr><td>Only put public configuration in client vars</td><td>API URLs, feature flags, public keys (e.g., publishable Stripe key)</td></tr>
  <tr><td>For real secrets, use server-side env (Next.js without prefix, or backend)</td><td>These never reach the browser</td></tr>
</table>

<p><strong>Safe vs unsafe to expose:</strong></p>

<table>
  <tr><th>Safe (client-side OK)</th><th>Unsafe (server-only)</th></tr>
  <tr><td>Public API URL</td><td>Database credentials</td></tr>
  <tr><td>Google Analytics ID</td><td>JWT signing key</td></tr>
  <tr><td>Stripe publishable key (<code>pk_live_*</code>)</td><td>Stripe secret key (<code>sk_live_*</code>)</td></tr>
  <tr><td>Feature flag IDs</td><td>API keys with write access</td></tr>
  <tr><td>App version, build info</td><td>OAuth client secrets</td></tr>
</table>

<p><strong>TypeScript autocomplete &mdash; type your env vars:</strong></p>

<pre><code>// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_FEATURE_NEW_UI: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}</code></pre>

<p><strong>2026 best practice</strong>: use <code>.env.local</code> for personal dev secrets, commit <code>.env.development</code> and <code>.env.production</code> with environment-appropriate (non-secret) values, and use server-side environments (Vercel env vars, AWS Secrets Manager, etc.) for true secrets.</p>
'''

ANSWERS[99] = r'''
<p>Deploying a React app means: <strong>building a production bundle</strong> (HTML + JS + CSS + assets), then <strong>uploading it to a host</strong> that serves static files. Modern hosts make this nearly automatic via Git integration.</p>

<p><strong>Build the production bundle:</strong></p>

<pre><code># Vite (recommended for new projects)
npm run build           # outputs to dist/

# Create React App (deprecated)
npm run build           # outputs to build/

# Next.js (full-stack)
npm run build           # builds + ready to deploy</code></pre>

<p>The build folder contains optimized, minified files ready to serve.</p>

<p><strong>Most popular deployment platforms in 2026:</strong></p>

<table>
  <tr><th>Platform</th><th>Best for</th><th>Free tier?</th></tr>
  <tr><td>Vercel</td><td>Next.js apps; React SPAs; ideal for full-stack React</td><td>Yes (generous)</td></tr>
  <tr><td>Netlify</td><td>SPAs, static sites, JAMstack</td><td>Yes</td></tr>
  <tr><td>Cloudflare Pages</td><td>Static sites with edge functions; very fast CDN</td><td>Yes</td></tr>
  <tr><td>AWS Amplify</td><td>AWS-integrated apps; full-stack</td><td>Yes (limited)</td></tr>
  <tr><td>GitHub Pages</td><td>Simple static SPAs; portfolio sites</td><td>Yes (public repos)</td></tr>
  <tr><td>Render</td><td>Static + backend services</td><td>Yes</td></tr>
  <tr><td>Firebase Hosting</td><td>Google ecosystem; with Firestore/Auth</td><td>Yes</td></tr>
  <tr><td>S3 + CloudFront</td><td>AWS-native; high control; enterprise</td><td>Pay-as-you-go</td></tr>
</table>

<p><strong>Easiest deployment &mdash; Vercel/Netlify with Git integration:</strong></p>
<ol>
  <li>Push your code to GitHub.</li>
  <li>Sign in to Vercel/Netlify; click "Import project."</li>
  <li>Select your repo. The platform auto-detects Vite/CRA/Next.js.</li>
  <li>Click "Deploy." Site live in &lt;1 minute.</li>
  <li>Future commits to <code>main</code> auto-deploy. PRs get preview URLs.</li>
</ol>

<p><strong>Manual deployment via CLI:</strong></p>

<pre><code># Vercel
npm i -g vercel
vercel              # follow prompts

# Netlify
npm i -g netlify-cli
netlify deploy --prod --dir=dist

# Firebase
npm i -g firebase-tools
firebase init hosting
firebase deploy

# AWS S3 (via aws-cli)
aws s3 sync dist/ s3://my-bucket --delete</code></pre>

<p><strong>Critical: SPA routing config.</strong> SPAs use client-side routing &mdash; the server needs to send <code>index.html</code> for any path so React Router can handle the URL.</p>

<pre><code># nginx
location / {
  try_files $uri $uri/ /index.html;
}

# Apache (.htaccess)
RewriteEngine On
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Netlify (_redirects file in public/)
/*    /index.html   200

# Vercel (vercel.json)
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }</code></pre>

<p>Without this, refreshing on <code>/dashboard</code> returns a 404. Modern hosts handle this automatically when they detect Vite/CRA/Next.js.</p>

<p><strong>Environment variables for production:</strong></p>
<ul>
  <li><strong>Set them in the host&rsquo;s dashboard</strong> (Vercel, Netlify env settings).</li>
  <li>The build process reads them and embeds the values in the bundle.</li>
  <li>Never commit production secrets to <code>.env.production</code> &mdash; use the host&rsquo;s env settings.</li>
</ul>

<p><strong>Deployment checklist:</strong></p>

<table>
  <tr><th>Item</th><th>Check</th></tr>
  <tr><td>Production build runs cleanly</td><td><code>npm run build</code> with no errors</td></tr>
  <tr><td>Source maps disabled (or hidden)</td><td>Avoids exposing source in DevTools</td></tr>
  <tr><td>Environment variables set on host</td><td>API URLs, public keys</td></tr>
  <tr><td>SPA fallback configured</td><td>Reload on subroutes works</td></tr>
  <tr><td>HTTPS enforced</td><td>Most hosts default to HTTPS now</td></tr>
  <tr><td>Cache headers reasonable</td><td>Long-cache static assets, no-cache for index.html</td></tr>
  <tr><td>Bundle size reviewed</td><td>Run bundle analyzer if &gt;500KB</td></tr>
  <tr><td>Error tracking enabled</td><td>Sentry / Datadog in production</td></tr>
  <tr><td>Custom domain configured</td><td>If using one</td></tr>
</table>

<p><strong>2026 recommendation</strong>: for SPAs, <strong>Vercel or Netlify</strong> are the easiest wins. For Next.js apps, <strong>Vercel</strong> is the natural fit (made by the same company). For static portfolios and simple sites, <strong>Cloudflare Pages</strong> is fast and free. For AWS-native shops, <strong>S3 + CloudFront</strong> remains the standard.</p>
'''

ANSWERS[100] = r'''
<p>React doesn&rsquo;t prescribe a styling approach &mdash; you can choose from several options based on team preference and project needs.</p>

<p><strong>The main styling approaches:</strong></p>

<table>
  <tr><th>Approach</th><th>Style</th><th>Best for</th></tr>
  <tr><td>Plain CSS</td><td>External <code>.css</code> files</td><td>Simple projects; team prefers regular CSS</td></tr>
  <tr><td>CSS Modules</td><td>Locally-scoped <code>.module.css</code></td><td>Component-scoped styles without runtime overhead</td></tr>
  <tr><td>Tailwind CSS</td><td>Utility classes inline</td><td>Most popular in 2026; fast development; consistent design</td></tr>
  <tr><td>CSS-in-JS (styled-components, Emotion)</td><td>Component-scoped JS-defined styles</td><td>Highly dynamic styles based on props</td></tr>
  <tr><td>Inline styles</td><td>Style prop with object</td><td>Quick prototyping; truly dynamic styles</td></tr>
  <tr><td>SCSS / SASS</td><td>CSS preprocessor</td><td>Teams comfortable with SASS; nesting, mixins</td></tr>
  <tr><td>UI libraries (Material UI, Chakra, Mantine)</td><td>Pre-built components</td><td>Rapid app development; consistent design system</td></tr>
</table>

<p><strong>1. Plain CSS:</strong></p>

<pre><code>// Component.jsx
import "./Component.css";
function Component() { return &lt;div className="card"&gt;...&lt;/div&gt;; }

/* Component.css */
.card { padding: 16px; background: white; }</code></pre>

<p>Simple but global &mdash; class names can conflict across files.</p>

<p><strong>2. CSS Modules &mdash; locally scoped:</strong></p>

<pre><code>// Component.jsx
import styles from "./Component.module.css";
function Component() { return &lt;div className={styles.card}&gt;...&lt;/div&gt;; }

/* Component.module.css */
.card { padding: 16px; background: white; }</code></pre>

<p>Class names are auto-prefixed (<code>card</code> → <code>Component_card__a3b9c</code>) so no conflicts. Built into Vite, CRA, Next.js.</p>

<p><strong>3. Tailwind CSS &mdash; the 2026 dominant choice:</strong></p>

<pre><code>function Card() {
  return (
    &lt;div className="p-4 rounded-lg shadow-md bg-white hover:shadow-lg transition"&gt;
      &lt;h3 className="text-xl font-bold text-gray-900"&gt;Title&lt;/h3&gt;
      &lt;p className="text-gray-600 mt-2"&gt;Body text&lt;/p&gt;
    &lt;/div&gt;
  );
}</code></pre>

<p>Build-time tool generates only the classes you use &mdash; tiny CSS bundle. Pros: extremely fast development, consistent spacing/colors, no naming bikeshedding. Cons: HTML can look noisy; learning curve for class names.</p>

<p><strong>4. CSS-in-JS &mdash; styled-components:</strong></p>

<pre><code>import styled from "styled-components";

const Card = styled.div`
  padding: 16px;
  background: ${props =&gt; props.dark ? "#222" : "white"};
  color: ${props =&gt; props.dark ? "white" : "black"};
`;

function App() { return &lt;Card dark&gt;Hello&lt;/Card&gt;; }</code></pre>

<p>Dynamic styles based on props; no class name conflicts; co-located with components. Cons: runtime overhead, slightly larger bundles.</p>

<p><strong>5. Inline styles:</strong></p>

<pre><code>function Box({ color }) {
  return (
    &lt;div style={{
      padding: 16,
      backgroundColor: color,
      borderRadius: 8
    }}&gt;
      Content
    &lt;/div&gt;
  );
}</code></pre>

<p>Object syntax (camelCase). No pseudo-classes (<code>:hover</code>), no media queries. Use sparingly &mdash; for genuinely dynamic styles only.</p>

<p><strong>6. SCSS:</strong></p>

<pre><code>// Component.scss
.card {
  padding: 16px;
  &amp;:hover { box-shadow: 0 2px 8px rgba(0,0,0,.1); }
  .title { font-weight: bold; }
}

// Component.jsx
import "./Component.scss";</code></pre>

<p>Familiar to teams from non-React backgrounds. Combine with CSS Modules for scoping (<code>Component.module.scss</code>).</p>

<p><strong>2026 popularity rankings (informal):</strong></p>

<table>
  <tr><th>Rank</th><th>Approach</th><th>Trend</th></tr>
  <tr><td>1</td><td>Tailwind CSS</td><td>Most popular for new projects</td></tr>
  <tr><td>2</td><td>CSS Modules</td><td>Stable, widely used</td></tr>
  <tr><td>3</td><td>UI library (Material UI, shadcn/ui)</td><td>shadcn/ui surging in 2025-26</td></tr>
  <tr><td>4</td><td>styled-components / Emotion</td><td>Declining but still common</td></tr>
  <tr><td>5</td><td>Plain CSS</td><td>Simple projects, learning</td></tr>
</table>

<p><strong>shadcn/ui</strong> (a code-first UI library based on Tailwind + Radix) has become extremely popular &mdash; you copy components into your project rather than installing a package. Combine with Tailwind for the modern stack many teams converge on.</p>

<p><strong>How to choose</strong>: <strong>Tailwind</strong> for fast development with a design system, <strong>CSS Modules</strong> for component-scoped traditional CSS, <strong>styled-components</strong> for highly dynamic prop-driven styles, <strong>UI library</strong> for rapid app development without designing everything yourself. The "best" choice depends on team familiarity and project needs.</p>
'''

ANSWERS[101] = r'''
<p><strong>styled-components</strong> is a popular CSS-in-JS library for React. You define a component&rsquo;s styles using template literals containing real CSS, and the library injects scoped class names at runtime. It supports props-based styling, theming, and global styles.</p>

<p><strong>Install and basic usage:</strong></p>

<pre><code>npm install styled-components

// Button.jsx
import styled from "styled-components";

const Button = styled.button`
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &amp;:hover {
    background: #0056b3;
  }
`;

function App() {
  return &lt;Button&gt;Click me&lt;/Button&gt;;
}</code></pre>

<p>The <code>styled.button</code> tagged template returns a React component &mdash; use it like any other component. Behind the scenes, styled-components generates a unique class name and injects the CSS.</p>

<p><strong>Props-based styling &mdash; the killer feature:</strong></p>

<pre><code>const Button = styled.button`
  padding: ${props =&gt; props.size === "large" ? "12px 24px" : "8px 16px"};
  background: ${props =&gt; props.variant === "danger" ? "#dc3545" : "#007bff"};
  color: white;
  border-radius: 4px;
`;

function App() {
  return (
    &lt;&gt;
      &lt;Button&gt;Default&lt;/Button&gt;
      &lt;Button variant="danger"&gt;Delete&lt;/Button&gt;
      &lt;Button size="large"&gt;Big button&lt;/Button&gt;
    &lt;/&gt;
  );
}</code></pre>

<p><strong>Extending styled components:</strong></p>

<pre><code>const Button = styled.button`
  padding: 8px 16px;
  background: #007bff;
  color: white;
`;

const PrimaryButton = styled(Button)`
  font-weight: bold;
  text-transform: uppercase;
`;

const TomatoButton = styled(Button)`
  background: tomato;
`;</code></pre>

<p><strong>Theming with ThemeProvider:</strong></p>

<pre><code>import { ThemeProvider } from "styled-components";

const theme = {
  colors: {
    primary: "#007bff",
    danger: "#dc3545",
    success: "#28a745"
  },
  spacing: {
    sm: "8px",
    md: "16px",
    lg: "24px"
  }
};

function App() {
  return (
    &lt;ThemeProvider theme={theme}&gt;
      &lt;Layout /&gt;
    &lt;/ThemeProvider&gt;
  );
}

// Any styled component can access the theme
const Card = styled.div`
  padding: ${props =&gt; props.theme.spacing.md};
  background: ${props =&gt; props.theme.colors.primary};
`;</code></pre>

<p><strong>Global styles:</strong></p>

<pre><code>import { createGlobalStyle } from "styled-components";

const GlobalStyle = createGlobalStyle`
  * { box-sizing: border-box; }
  body {
    font-family: system-ui, sans-serif;
    margin: 0;
    background: ${props =&gt; props.theme.colors.background};
  }
`;

function App() {
  return (
    &lt;ThemeProvider theme={theme}&gt;
      &lt;GlobalStyle /&gt;
      &lt;Layout /&gt;
    &lt;/ThemeProvider&gt;
  );
}</code></pre>

<p><strong>The <code>css</code> helper for shared style snippets:</strong></p>

<pre><code>import styled, { css } from "styled-components";

const focusOutline = css`
  outline: 2px solid blue;
  outline-offset: 2px;
`;

const Input = styled.input`
  padding: 8px;
  border: 1px solid #ccc;

  &amp;:focus { ${focusOutline} }
`;

const Button = styled.button`
  &amp;:focus { ${focusOutline} }
`;</code></pre>

<p><strong>Pros and cons:</strong></p>

<table>
  <tr><th>Pros</th><th>Cons</th></tr>
  <tr><td>Co-located styles + component</td><td>Runtime overhead (parses + injects styles)</td></tr>
  <tr><td>Dynamic styles via props</td><td>Larger bundle (~12KB)</td></tr>
  <tr><td>No CSS class name conflicts</td><td>Doesn&rsquo;t work with React Server Components without workarounds</td></tr>
  <tr><td>Theming with React Context</td><td>Worse performance than build-time CSS solutions</td></tr>
  <tr><td>Type-safe with TypeScript</td><td>Increasingly out of fashion vs Tailwind</td></tr>
</table>

<p><strong>2026 reality &mdash; styled-components is in decline</strong>:</p>
<ul>
  <li><strong>Tailwind</strong> has become the dominant React styling approach.</li>
  <li><strong>Server Components</strong> in Next.js / React 19 don&rsquo;t play well with runtime CSS-in-JS.</li>
  <li><strong>Zero-runtime alternatives</strong> like <strong>Vanilla Extract</strong>, <strong>Linaria</strong>, <strong>Panda CSS</strong>, and <strong>StyleX</strong> (from Meta) offer the same DX with build-time CSS extraction.</li>
  <li><strong>shadcn/ui</strong> (Tailwind + Radix) often replaces the use cases that styled-components solved.</li>
</ul>

<p><strong>Should you still learn it?</strong> Yes &mdash; many existing codebases use it heavily, and it&rsquo;s still the most popular CSS-in-JS library by usage. But for new projects, evaluate Tailwind, CSS Modules, or zero-runtime CSS-in-JS first. styled-components remains a solid choice for projects that need highly dynamic prop-based styling, but the broader ecosystem trend is toward build-time solutions for better performance.</p>
'''
