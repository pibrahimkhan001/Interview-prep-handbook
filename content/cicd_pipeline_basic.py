"""Detailed answers for CI/CD Pipeline &mdash; Basic level.

Each entry maps a 1-indexed question number to an HTML fragment that the build
script wraps inside the chapter template. Style: Basic-level &mdash; concise prose
with explicit bullets/tables, brief code blocks when essential, ~1,500-2,800
chars per answer. References to 2026-current tooling (GitHub Actions, GitLab
CI, CircleCI, Argo CD, Tekton, Buildkite, modern alternatives).
"""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''<p>A <strong>CI/CD pipeline</strong> is an automated workflow that takes code from a developer&rsquo;s commit through to running production systems. CI (Continuous Integration) is the &ldquo;build &amp; test&rdquo; half: every push gets compiled, linted, unit-tested, and packaged. CD (Continuous Delivery or Deployment) is the &ldquo;ship&rdquo; half: tested artifacts get promoted through environments &mdash; staging, canary, production &mdash; with deployment, smoke tests, and rollback automation.</p>
<p>A typical pipeline runs as YAML or DSL alongside the source code. For a MERN app it might look like this on GitHub Actions:</p>
<pre><code># .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
</code></pre>
<p>Pipelines remove the &ldquo;works on my machine&rdquo; problem, catch regressions early, and let teams deploy multiple times per day with confidence. The 2026 default tools are <strong>GitHub Actions</strong> (most popular for OSS and private repos), <strong>GitLab CI/CD</strong> (integrated platform), <strong>CircleCI</strong>, and <strong>Buildkite</strong> for self-hosted agents on cloud control plane. For Kubernetes-native deployments, <strong>Argo CD</strong> and <strong>FluxCD</strong> handle the CD half via GitOps.</p>
<p>Pipelines typically have stages: source &rarr; build &rarr; test &rarr; security scan &rarr; package &rarr; deploy &rarr; verify &rarr; promote. Each stage has clear pass/fail signals and can fan out into parallel jobs (e.g., test on Node 18/20/22 simultaneously). The contract is: if the pipeline is green, the code is shippable.</p>'''

ANSWERS[2] = r'''<p><strong>Continuous Integration (CI)</strong> is the practice of merging every developer&rsquo;s changes into a shared mainline branch frequently &mdash; ideally multiple times per day &mdash; and validating each merge with an automated build and test suite. The goal is to catch integration problems within minutes instead of days, when the cost to fix is small.</p>
<p>Without CI, developers work on long-lived branches that drift apart, then face painful merge conflicts. With CI, every push triggers a pipeline that:</p>
<ul>
<li><strong>Compiles or transpiles</strong> the code (TypeScript, Babel, etc.)</li>
<li><strong>Runs linters and formatters</strong> (ESLint, Prettier, Biome) to enforce style</li>
<li><strong>Executes unit and integration tests</strong> (Vitest, Jest, Playwright)</li>
<li><strong>Performs static analysis</strong> (TypeScript type-check, SonarQube, CodeQL)</li>
<li><strong>Scans for vulnerabilities</strong> in dependencies (npm audit, Snyk, Socket.dev, Dependabot)</li>
<li><strong>Builds the artifact</strong> (Docker image, npm package, bundle)</li>
</ul>
<p>If any step fails, the merge is blocked. This contract &mdash; main is always green &mdash; is what makes CI valuable. Teams using CI well report fewer production incidents, faster feature delivery, and higher confidence when refactoring.</p>
<p>Modern CI requires <strong>fast feedback</strong>: tests should run in under 10 minutes for the typical PR, and under 30 minutes for the full suite. Achieve this via parallel jobs, test sharding, dependency caching (npm/pnpm/Docker layer cache), and incremental builds via Nx, Turborepo, or Bazel. Slow CI is worse than no CI &mdash; people start ignoring it.</p>
<p>CI is foundational; CD builds on top. You can&rsquo;t safely automate deployment without first having confidence that what&rsquo;s being deployed actually works.</p>'''

ANSWERS[3] = r'''<p><strong>Continuous Delivery</strong> and <strong>Continuous Deployment</strong> are related but distinct. The shared goal: get tested code into production safely and frequently. The difference is the trigger for the final production push.</p>
<table>
<thead><tr><th>Term</th><th>Trigger to prod</th><th>Use case</th></tr></thead>
<tbody>
<tr><td>Continuous Delivery</td><td>Manual approval (button click)</td><td>Regulated industries, business calendar control, weekly releases</td></tr>
<tr><td>Continuous Deployment</td><td>Automatic on green main</td><td>SaaS, internal tools, high-velocity teams</td></tr>
</tbody>
</table>
<p>Both require:</p>
<ul>
<li>A green CI pipeline as a prerequisite</li>
<li>Automated deployment to staging/pre-prod environments</li>
<li>Smoke tests, health checks, and synthetic monitoring after deploy</li>
<li>One-click (or zero-click) rollback if anything goes wrong</li>
<li>Feature flags (LaunchDarkly, Statsig, GrowthBook, PostHog, Unleash) so deploy and release are decoupled</li>
</ul>
<p>The benefits are huge: smaller change sets per deploy means smaller blast radius if something breaks. Teams shipping daily detect and fix issues faster than teams shipping monthly. Mean time to recovery (MTTR) drops because the diff is small.</p>
<p>Patterns that make CD safe:</p>
<ul>
<li><strong>Blue-green:</strong> two identical environments; flip traffic via load balancer or Argo Rollouts.</li>
<li><strong>Canary:</strong> route 1% &rarr; 5% &rarr; 25% &rarr; 100% of traffic to new version, automated rollback on error rate spike (Argo Rollouts, Flagger, AWS CodeDeploy).</li>
<li><strong>Feature flags:</strong> deploy code dark, then flip on for cohorts.</li>
<li><strong>Database migrations:</strong> expand-then-contract (add nullable column, backfill, switch reads, drop old column) so any version can run against any schema during the rollout.</li>
</ul>
<p>The 2026 reality: most SaaS teams do Continuous Deployment with feature flags. Compliance-heavy teams (banks, healthcare) do Continuous Delivery with audit-logged manual approval.</p>'''

ANSWERS[4] = r'''<p>The benefits of CI/CD compound over time and are well-documented in the DORA <em>Accelerate</em> research. The four DORA metrics &mdash; deployment frequency, lead time, change failure rate, MTTR &mdash; all improve with mature CI/CD.</p>
<table>
<thead><tr><th>Benefit</th><th>What it looks like</th></tr></thead>
<tbody>
<tr><td><strong>Faster feedback</strong></td><td>Bugs caught in 5 minutes after a push instead of weeks later in QA</td></tr>
<tr><td><strong>Smaller change sets</strong></td><td>Easier to review, easier to debug, easier to roll back</td></tr>
<tr><td><strong>Higher deploy frequency</strong></td><td>Multiple deploys per day vs one per quarter</td></tr>
<tr><td><strong>Lower change failure rate</strong></td><td>Automated tests + canary deploys catch most regressions</td></tr>
<tr><td><strong>Faster MTTR</strong></td><td>Small diffs are fast to roll back; auto-rollback handles many cases</td></tr>
<tr><td><strong>Reproducible builds</strong></td><td>Same Docker image runs locally, in CI, and in prod</td></tr>
<tr><td><strong>Audit trail</strong></td><td>Every deploy is tied to a Git SHA, a PR, an approval, a CI run</td></tr>
<tr><td><strong>Developer happiness</strong></td><td>No &ldquo;deploy day&rdquo; dread; ship when ready</td></tr>
<tr><td><strong>Security</strong></td><td>SAST/DAST/SCA scans run automatically on every PR</td></tr>
<tr><td><strong>Documentation</strong></td><td>Pipeline-as-code is itself runnable, version-controlled documentation</td></tr>
</tbody>
</table>
<p>CI/CD also enables <strong>trunk-based development</strong>, where everyone commits to main multiple times per day behind feature flags. This eliminates merge hell from long-lived branches and is the dominant pattern at high-velocity orgs in 2026.</p>
<p>Indirect benefits: better tests (because they run all the time, flakiness is intolerable), better infrastructure (Docker, IaC, observability are CI/CD prerequisites), better hiring story (engineers want to work somewhere they can ship). The org-level outcome is faster product iteration with fewer outages.</p>'''

ANSWERS[5] = r'''<p>GitHub supports CI/CD primarily through <strong>GitHub Actions</strong>, a native pipeline engine that runs YAML workflows triggered by repository events (push, pull request, issue, schedule, manual dispatch, webhook). Workflows live in <code>.github/workflows/*.yml</code> and are versioned with the code.</p>
<p>Beyond Actions, GitHub provides:</p>
<ul>
<li><strong>Branch protection rules</strong> &mdash; require status checks (CI green), required reviewers, signed commits, no force-push to main.</li>
<li><strong>GitHub Packages</strong> &mdash; built-in registry for npm, Docker, Maven, NuGet artifacts.</li>
<li><strong>GitHub Container Registry (ghcr.io)</strong> &mdash; free private/public Docker image hosting tied to repo permissions.</li>
<li><strong>Environments</strong> &mdash; gate deploys with required reviewers, secrets per env (staging, production), wait timers.</li>
<li><strong>Secrets and variables</strong> &mdash; org/repo/env scoped, encrypted at rest, masked in logs.</li>
<li><strong>OIDC tokens</strong> &mdash; short-lived federated tokens to AWS/GCP/Azure without storing long-lived cloud credentials.</li>
<li><strong>Dependabot</strong> &mdash; automated dependency updates with PRs.</li>
<li><strong>CodeQL</strong> &mdash; native SAST.</li>
<li><strong>Code Scanning &amp; Secret Scanning</strong> &mdash; automatic for public repos, available for private with GitHub Advanced Security.</li>
</ul>
<p>A minimal workflow:</p>
<pre><code>name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test
</code></pre>
<p>The runner ecosystem: GitHub-hosted runners (ubuntu-latest, macos-latest, windows-latest), self-hosted runners (your own infra, often K8s via Actions Runner Controller), and larger runners for heavy workloads. The Marketplace has tens of thousands of pre-built actions (Docker build, AWS deploy, Slack notify), though best practice is to pin actions to a SHA and audit before use to avoid supply-chain attacks.</p>
<p>GitHub Actions has eclipsed Jenkins for new projects in 2026. CircleCI, Buildkite, and GitLab CI remain strong alternatives.</p>'''

ANSWERS[6] = r'''<p><strong>Docker</strong> is a platform for packaging applications and their dependencies into <em>containers</em> &mdash; lightweight, isolated runtime environments built from layered images. A container bundles your code, runtime (Node.js, Python), system libraries, and config into one immutable unit that runs identically anywhere Docker is supported.</p>
<p>Why Docker is central to CI/CD pipelines:</p>
<ul>
<li><strong>Reproducibility:</strong> the same image that passes tests in CI runs in staging and production. Eliminates &ldquo;works on my machine&rdquo;.</li>
<li><strong>Isolation:</strong> each pipeline job can run in its own clean container, no shared state between builds.</li>
<li><strong>Speed:</strong> containers start in seconds, not minutes like VMs. Layer caching makes rebuilds fast.</li>
<li><strong>Portability:</strong> the artifact (image) is the deploy unit. Push to a registry, pull anywhere.</li>
<li><strong>Service dependencies:</strong> spin up MongoDB, Redis, or any service as a sidecar container during integration tests.</li>
</ul>
<p>A typical pipeline uses Docker in three ways: <strong>(1)</strong> the build environment is a container (Node 20 image with your toolchain), <strong>(2)</strong> the build produces a Docker image as the deploy artifact, <strong>(3)</strong> integration tests run against containerized service dependencies.</p>
<p>Example multi-stage Dockerfile for a Node.js API:</p>
<pre><code># syntax=docker/dockerfile:1.7
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER node
CMD [&quot;node&quot;, &quot;dist/server.js&quot;]
</code></pre>
<p>The 2026 ecosystem: Docker Engine + Docker Desktop are still dominant, but <strong>Podman</strong> (rootless, daemon-less, drop-in replacement), <strong>Buildah</strong> (image building), and <strong>BuildKit</strong> (Docker&rsquo;s newer builder with parallelism and better caching) are common. <strong>Nerdctl</strong> + <strong>containerd</strong> is what Kubernetes actually runs under the hood.</p>'''

ANSWERS[7] = r'''<p><strong>Kubernetes (K8s)</strong> is the orchestration layer where containers run in production. In a CI/CD pipeline, Kubernetes is the deployment target: the pipeline builds a Docker image, pushes it to a registry, then updates a Kubernetes manifest to roll out the new version with zero downtime.</p>
<p>Why CI/CD pipelines need Kubernetes:</p>
<ul>
<li><strong>Declarative deploys:</strong> you describe the desired state (3 replicas, image v1.2.3, 2 GB memory) and K8s reconciles. No imperative scripts.</li>
<li><strong>Rolling updates:</strong> built-in. Replace pods one at a time with health checks; if new pods fail readiness, halt the rollout.</li>
<li><strong>Self-healing:</strong> crashed pods are restarted; failed nodes have their pods rescheduled.</li>
<li><strong>Horizontal scaling:</strong> HPA scales based on CPU, memory, or custom metrics (KEDA scales on queue depth, request rate).</li>
<li><strong>Service discovery + load balancing:</strong> Services route traffic to healthy pods automatically.</li>
<li><strong>Config + secrets management:</strong> ConfigMaps and Secrets injected as env vars or files.</li>
</ul>
<p>The CD step typically looks like:</p>
<pre><code># In CI: build &amp; push image
- run: docker build -t ghcr.io/me/api:${{ github.sha }} .
- run: docker push ghcr.io/me/api:${{ github.sha }}

# CD: update Deployment
- run: kubectl set image deployment/api api=ghcr.io/me/api:${{ github.sha }}
- run: kubectl rollout status deployment/api --timeout=5m
</code></pre>
<p>The 2026 standard is <strong>GitOps</strong>: instead of <code>kubectl set image</code> from CI, the pipeline updates a YAML file in a Git repo, and <strong>Argo CD</strong> or <strong>FluxCD</strong> watches that repo and reconciles the cluster. This gives you audit trail, rollback via git revert, and clean separation between CI (build) and CD (deploy).</p>
<p>Managed K8s offerings dominate: <strong>EKS</strong> (AWS), <strong>GKE</strong> (Google &mdash; Autopilot is excellent), <strong>AKS</strong> (Azure). For multi-cluster: <strong>Rancher</strong>, <strong>Karmada</strong>, or fleet management via <strong>Cluster API</strong>. For simpler workloads, many teams skip K8s entirely and use Cloud Run, Fargate, or Fly Machines.</p>'''

ANSWERS[8] = r'''<p><strong>Jenkins</strong> is the original open-source automation server, dating to 2011 (forked from Hudson). It runs builds, tests, and deployments via plugins and scripts. For two decades it was the dominant CI/CD tool; today it&rsquo;s still widely used but losing ground to YAML-based, cloud-native alternatives.</p>
<p>Jenkins fits into CI/CD as the orchestration brain: a controller polls SCM (or receives webhooks), schedules jobs onto agent nodes, executes pipelines, and reports results. Pipelines are defined in a <code>Jenkinsfile</code> using Groovy DSL (declarative or scripted) and can be triggered by SCM changes, schedules, manual triggers, or upstream jobs.</p>
<p>Example declarative Jenkinsfile:</p>
<pre><code>pipeline {
  agent any
  stages {
    stage('Build')  { steps { sh 'npm ci &amp;&amp; npm run build' } }
    stage('Test')   { steps { sh 'npm test' } }
    stage('Deploy') {
      when { branch 'main' }
      steps { sh './deploy.sh' }
    }
  }
}
</code></pre>
<p>Jenkins strengths in 2026:</p>
<ul>
<li>Mature plugin ecosystem (1,800+ plugins): every cloud, every tool, every weird integration.</li>
<li>Self-hosted &mdash; full control, no vendor lock-in, no per-minute cost.</li>
<li>Fits enterprise on-prem, air-gapped, regulated environments.</li>
<li>Powerful Groovy DSL for complex pipeline logic.</li>
</ul>
<p>Jenkins weaknesses driving the move away:</p>
<ul>
<li>Plugin sprawl &mdash; security CVEs, version conflicts, brittle upgrades.</li>
<li>Groovy DSL has a learning curve and is hard to test locally.</li>
<li>Operations burden &mdash; you maintain the controller, agents, plugins, OS, JVM.</li>
<li>UI feels dated; Blue Ocean helped but is essentially abandoned.</li>
<li>YAML alternatives (GitHub Actions, GitLab CI, CircleCI) are simpler and cloud-native.</li>
</ul>
<p>For new projects in 2026, default to GitHub Actions or GitLab CI. Use Jenkins when you have existing investment, complex pipeline logic, or strict on-prem requirements. <strong>CloudBees</strong> sells managed/enterprise Jenkins. <strong>JenkinsX</strong> is a Kubernetes-native rewrite that didn&rsquo;t catch on; <strong>Tekton</strong> is the spiritual successor for K8s.</p>'''

ANSWERS[9] = r'''<p>A GitHub Action workflow is a YAML file in <code>.github/workflows/</code> that defines triggers, jobs, and steps. The smallest useful workflow runs tests on every push and pull request:</p>
<pre><code># .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm test
</code></pre>
<p>Key concepts:</p>
<ul>
<li><strong>on:</strong> the trigger. Common ones: <code>push</code>, <code>pull_request</code>, <code>schedule</code> (cron), <code>workflow_dispatch</code> (manual), <code>release</code>.</li>
<li><strong>jobs:</strong> independent units that run in parallel by default; use <code>needs:</code> to chain them sequentially.</li>
<li><strong>runs-on:</strong> the runner image. <code>ubuntu-latest</code>, <code>macos-latest</code>, <code>windows-latest</code>, or self-hosted labels.</li>
<li><strong>steps:</strong> sequential commands within a job. Either <code>uses:</code> (reusable action) or <code>run:</code> (shell command).</li>
<li><strong>actions/checkout@v4:</strong> clones your repo into the runner.</li>
<li><strong>cache:</strong> the setup-node action can cache <code>node_modules</code> based on <code>package-lock.json</code>.</li>
</ul>
<p>To add deployment:</p>
<pre><code>jobs:
  test: ... # as above
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.PROD_API_KEY }}
</code></pre>
<p>Best practices: pin third-party actions to a commit SHA (<code>uses: org/action@a1b2c3d</code>), not a moving tag, to prevent supply-chain attacks. Use the GitHub-managed <code>${{ secrets.* }}</code> for credentials. Set the workflow timeout (<code>timeout-minutes: 30</code>). Add concurrency groups to cancel superseded runs (<code>concurrency: { group: ${{ github.ref }}, cancel-in-progress: true }</code>). For matrix builds across Node versions, use <code>strategy.matrix</code>.</p>'''

ANSWERS[10] = r'''<p>A <strong>Dockerfile</strong> is a plain-text recipe for building a Docker image. Each line is an instruction; together they describe how to layer a runtime environment on top of a base image. Docker reads it, executes the instructions, and produces an immutable image you can ship anywhere.</p>
<p>A typical Dockerfile for a Node.js application:</p>
<pre><code># syntax=docker/dockerfile:1.7
FROM node:20-alpine AS base
WORKDIR /app

# Install deps separately for better layer caching
COPY package*.json ./
RUN npm ci --omit=dev

# Copy source last (changes more frequently than deps)
COPY . .

# Drop privileges; node user exists in the official image
USER node
EXPOSE 3000
CMD [&quot;node&quot;, &quot;server.js&quot;]
</code></pre>
<p>Key instructions:</p>
<ul>
<li><strong>FROM</strong> &mdash; base image to start from. Use specific tags (<code>node:20-alpine</code>) not <code>latest</code>.</li>
<li><strong>WORKDIR</strong> &mdash; sets and creates the working directory.</li>
<li><strong>COPY / ADD</strong> &mdash; copy files from the build context into the image. Prefer COPY; ADD has surprising URL/tar behavior.</li>
<li><strong>RUN</strong> &mdash; execute a command at build time, creating a new layer.</li>
<li><strong>ENV</strong> &mdash; set environment variables.</li>
<li><strong>EXPOSE</strong> &mdash; document which ports the container listens on (informational).</li>
<li><strong>USER</strong> &mdash; drop from root to a non-privileged user (security best practice).</li>
<li><strong>CMD / ENTRYPOINT</strong> &mdash; the default command when the container starts.</li>
</ul>
<p>Build it: <code>docker build -t myapp:1.0 .</code> Run it: <code>docker run -p 3000:3000 myapp:1.0</code>.</p>
<p>Best practices in 2026:</p>
<ul>
<li><strong>Multi-stage builds</strong> to keep final image small (build deps in one stage, copy artifacts to a slim runtime stage).</li>
<li><strong>Order instructions from least to most frequently changing</strong> for layer cache hits.</li>
<li><strong>Use distroless or alpine base images</strong> to minimize attack surface; <strong>Chainguard Images</strong> are a 2026 favorite for hardened, near-zero-CVE bases.</li>
<li><strong>Pin versions</strong> for reproducibility (<code>node:20.11.1-alpine3.19</code>).</li>
<li><strong>Run as non-root</strong>.</li>
<li><strong>Scan images</strong> with Trivy, Grype, or Snyk before pushing to a registry.</li>
</ul>'''

ANSWERS[11] = r'''<p><strong>Containerization</strong> is the practice of packaging an application together with its dependencies (libraries, runtime, config) into a self-contained unit &mdash; a <em>container</em> &mdash; that runs identically across environments. The OS kernel is shared with the host, but everything else is isolated via Linux primitives: <strong>namespaces</strong> (process, network, mount, PID, UTS, user) provide isolation, <strong>cgroups</strong> enforce resource limits (CPU, memory, I/O), and <strong>union filesystems</strong> (overlayfs) layer the image.</p>
<table>
<thead><tr><th>Aspect</th><th>VM</th><th>Container</th></tr></thead>
<tbody>
<tr><td>Boot time</td><td>30-60 seconds</td><td>&lt;1 second</td></tr>
<tr><td>Disk size</td><td>GBs (full OS)</td><td>MBs to a few hundred MB</td></tr>
<tr><td>Memory overhead</td><td>Hundreds of MB per VM</td><td>Tens of MB per container</td></tr>
<tr><td>Density per host</td><td>Tens</td><td>Hundreds to thousands</td></tr>
<tr><td>Isolation</td><td>Strong (separate kernel)</td><td>Process-level (shared kernel)</td></tr>
<tr><td>Portability</td><td>OS-image-format-specific</td><td>OCI-standard, runs anywhere</td></tr>
</tbody>
</table>
<p>Containers are immutable: you don&rsquo;t patch a running container, you build a new image and replace the container. This makes deployments and rollbacks deterministic.</p>
<p>The container ecosystem revolves around the <strong>OCI (Open Container Initiative)</strong> standards, which define image format and runtime behavior. Tools that implement OCI: <strong>Docker</strong> (most popular), <strong>Podman</strong> (daemonless, rootless by default), <strong>containerd</strong> (used by Kubernetes), <strong>CRI-O</strong>, <strong>Buildah</strong>, <strong>BuildKit</strong>.</p>
<p>Why containerization matters for CI/CD:</p>
<ul>
<li>Build once, run anywhere (dev laptop, CI runner, staging, prod).</li>
<li>Eliminates &ldquo;works on my machine&rdquo; class of bugs.</li>
<li>Enables microservices: small services in their own containers communicating over the network.</li>
<li>Pairs with orchestrators (Kubernetes, ECS, Nomad) for scheduling, scaling, healing.</li>
<li>Foundation for modern serverless platforms (Cloud Run, AWS App Runner, Fargate, Fly Machines &mdash; all run OCI containers).</li>
</ul>
<p>Containerization is the de-facto deployment unit in 2026. Even &ldquo;serverless&rdquo; functions on Cloud Run, Fly, and modern Lambda are container-based under the hood.</p>'''

ANSWERS[12] = r'''<p>A Kubernetes cluster has two layers: the <strong>control plane</strong> (the brain) and the <strong>worker nodes</strong> (where your pods run).</p>
<table>
<thead><tr><th>Component</th><th>Layer</th><th>Role</th></tr></thead>
<tbody>
<tr><td><strong>kube-apiserver</strong></td><td>Control plane</td><td>REST API for the entire cluster; everything talks to it</td></tr>
<tr><td><strong>etcd</strong></td><td>Control plane</td><td>Distributed key-value store holding all cluster state</td></tr>
<tr><td><strong>kube-scheduler</strong></td><td>Control plane</td><td>Decides which node a new pod should run on</td></tr>
<tr><td><strong>kube-controller-manager</strong></td><td>Control plane</td><td>Reconciles desired vs actual state for built-in resources (deployments, services, etc.)</td></tr>
<tr><td><strong>cloud-controller-manager</strong></td><td>Control plane</td><td>Reconciles cloud-provider resources (load balancers, volumes)</td></tr>
<tr><td><strong>kubelet</strong></td><td>Worker node</td><td>Agent that runs on each node, talks to the apiserver, manages pods</td></tr>
<tr><td><strong>kube-proxy</strong></td><td>Worker node</td><td>Network proxy for Services (iptables, IPVS, or eBPF rules)</td></tr>
<tr><td><strong>container runtime</strong></td><td>Worker node</td><td>containerd or CRI-O &mdash; actually starts containers</td></tr>
<tr><td><strong>CNI plugin</strong></td><td>Worker node</td><td>Container networking (Cilium, Calico, AWS VPC CNI)</td></tr>
</tbody>
</table>
<p>The reconciliation loop is the heart of K8s: you submit desired state to the apiserver (e.g., &ldquo;I want 3 replicas of my web pod&rdquo;), it&rsquo;s stored in etcd, controllers notice the diff and act (scheduler picks nodes, kubelet starts containers), and the loop continues forever. If you delete a pod, the controller starts a replacement.</p>
<p>Resource hierarchy from smallest to largest:</p>
<ul>
<li><strong>Container</strong> &mdash; one running process</li>
<li><strong>Pod</strong> &mdash; one or more containers sharing network and storage; the smallest schedulable unit</li>
<li><strong>ReplicaSet</strong> &mdash; ensures N copies of a pod template</li>
<li><strong>Deployment</strong> &mdash; manages ReplicaSets for rolling updates</li>
<li><strong>Service</strong> &mdash; stable network endpoint for a set of pods</li>
<li><strong>Namespace</strong> &mdash; logical grouping for multi-tenancy</li>
</ul>
<p>In managed K8s (EKS/GKE/AKS), the cloud provider runs the control plane for you; you only manage worker nodes. <strong>GKE Autopilot</strong> goes further: the cloud manages nodes too. The 2026 trend is &ldquo;managed everything&rdquo; &mdash; very few teams should be running self-hosted K8s control planes.</p>'''

ANSWERS[13] = r'''<p><strong>Jenkins pipelines</strong> are the modern way to define CI/CD jobs in Jenkins as code, replacing the older &ldquo;Freestyle Project&rdquo; UI-clicking style. Pipelines are written in Groovy and stored in a <code>Jenkinsfile</code> at the root of your repository, so the pipeline definition is versioned alongside the code it builds.</p>
<p>Two flavors:</p>
<ul>
<li><strong>Declarative</strong> &mdash; structured, opinionated, easier to read. The recommended default.</li>
<li><strong>Scripted</strong> &mdash; full Groovy, more powerful but more dangerous. Use only when you need imperative logic the declarative syntax doesn&rsquo;t support.</li>
</ul>
<p>Declarative example:</p>
<pre><code>pipeline {
  agent any
  options {
    timeout(time: 20, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }
  environment {
    NODE_ENV = 'test'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Build')    { steps { sh 'npm ci &amp;&amp; npm run build' } }
    stage('Test') {
      parallel {
        stage('Unit')        { steps { sh 'npm test' } }
        stage('Integration') { steps { sh 'npm run test:int' } }
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps { sh './deploy.sh' }
    }
  }
  post {
    always { junit 'reports/**/*.xml' }
    failure { slackSend(channel: '#alerts', message: &quot;Build failed: ${env.BUILD_URL}&quot;) }
  }
}
</code></pre>
<p>Key blocks:</p>
<ul>
<li><strong>agent</strong> &mdash; where the pipeline runs (any node, a specific label, a Docker image, a Kubernetes pod template).</li>
<li><strong>stages</strong> &mdash; logical groupings shown in the Blue Ocean UI.</li>
<li><strong>steps</strong> &mdash; the actual commands.</li>
<li><strong>parallel</strong> &mdash; run substages concurrently.</li>
<li><strong>when</strong> &mdash; conditional execution (branch, tag, expression).</li>
<li><strong>post</strong> &mdash; cleanup, notifications, reporting after success/failure/always.</li>
</ul>
<p>Pipelines support <strong>shared libraries</strong> (reusable Groovy code across many Jenkinsfiles), <strong>Multibranch Pipelines</strong> (auto-discover branches and PRs), and <strong>parameterized builds</strong>. The Kubernetes plugin lets each stage spin up an ephemeral pod as the agent, eliminating long-lived agent state.</p>
<p>Pipelines-as-code is the right way to use Jenkins in 2026 &mdash; the old Freestyle UI configurations are unmaintainable at any scale.</p>'''

ANSWERS[14] = r'''<p>Jenkins builds can be triggered in many ways. The four most common, from manual to fully automated:</p>
<ol>
<li><strong>Manual / parameterized:</strong> click <em>Build Now</em> in the UI, optionally entering parameter values. Good for ad-hoc deploys, hotfixes, debugging.</li>
<li><strong>SCM polling:</strong> Jenkins periodically pulls the repo and triggers if there&rsquo;s a new commit. Configured via cron syntax (<code>H/5 * * * *</code> = every 5 min). Inefficient at scale; prefer webhooks.</li>
<li><strong>Webhooks (push notifications):</strong> the SCM (GitHub, GitLab, Bitbucket) sends an HTTP POST to Jenkins on each push or PR. Real-time, scales to thousands of repos.</li>
<li><strong>Schedule (cron):</strong> nightly builds, weekly long-running tests, periodic security scans. Use <code>H</code> for jitter so all jobs don&rsquo;t fire at exactly midnight.</li>
</ol>
<p>Other triggers:</p>
<ul>
<li><strong>Upstream / downstream:</strong> Job B starts when Job A succeeds (<code>build job: 'B'</code> or &ldquo;Build after other projects are built&rdquo;).</li>
<li><strong>Remote API trigger:</strong> hit <code>/job/myjob/build?token=XYZ</code> from anywhere &mdash; useful for chaining external systems or triggering from chat ops.</li>
<li><strong>Generic webhook trigger plugin:</strong> accept arbitrary JSON payloads and use JSONPath to extract parameters; good for custom event sources.</li>
</ul>
<p>Webhook setup with GitHub:</p>
<ol>
<li>In Jenkins job: enable &ldquo;GitHub hook trigger for GITScm polling&rdquo;.</li>
<li>In GitHub repo settings &rarr; Webhooks: add <code>https://jenkins.example.com/github-webhook/</code>, content type <code>application/json</code>, secret token, events: just push (or push + PR).</li>
<li>Test by pushing &mdash; the build should kick off within seconds.</li>
</ol>
<p>For Multibranch Pipelines, GitHub Branch Source plugin auto-discovers branches and PRs and creates a separate job per branch &mdash; the standard pattern for trunk-based development. Pull-request builds run on a merge-commit so you test the post-merge state.</p>
<p>Real-world tip: avoid SCM polling at scale &mdash; it hammers your SCM with millions of LDAP/auth checks per day. Always use webhooks. Pair with a <strong>build queue</strong> and <strong>concurrency limits</strong> per job to prevent stampedes.</p>'''

ANSWERS[15] = r'''<p>Containers and virtual machines both isolate workloads, but at different layers of the stack. The simplest way to think about it: a VM virtualizes <em>hardware</em>, a container virtualizes the <em>process</em>.</p>
<table>
<thead><tr><th>Aspect</th><th>Virtual Machine</th><th>Container</th></tr></thead>
<tbody>
<tr><td>Virtualizes</td><td>Hardware (CPU, memory, devices)</td><td>OS process (namespaces + cgroups)</td></tr>
<tr><td>Includes</td><td>Full guest OS + kernel + userland + app</td><td>Just userland + app; shares host kernel</td></tr>
<tr><td>Boot time</td><td>30-60 seconds</td><td>&lt;1 second</td></tr>
<tr><td>Image size</td><td>Several GB</td><td>10 MB to a few hundred MB</td></tr>
<tr><td>Memory overhead</td><td>~512 MB+ per VM</td><td>Tens of MB per container</td></tr>
<tr><td>Density</td><td>Tens per host</td><td>Hundreds to thousands per host</td></tr>
<tr><td>Isolation strength</td><td>Strong (separate kernel)</td><td>Process-level (shared kernel)</td></tr>
<tr><td>OS flexibility</td><td>Any guest OS (Linux, Windows, BSD)</td><td>Tied to host kernel; Linux containers need Linux kernel</td></tr>
<tr><td>Hypervisor</td><td>KVM, VMware, Hyper-V, Xen</td><td>Container runtime: containerd, CRI-O</td></tr>
<tr><td>Security boundary</td><td>Industry-standard for multi-tenancy</td><td>Weaker; kernel exploits cross containers</td></tr>
</tbody>
</table>
<p>Practical implication: VMs are heavier but more isolated. If you&rsquo;re running untrusted code from random tenants on the same host, VMs (or VM-like sandboxes such as <strong>Firecracker</strong>, <strong>gVisor</strong>, or <strong>Kata Containers</strong>) are the safer choice. AWS Lambda and Fly Machines run on Firecracker microVMs precisely because container isolation isn&rsquo;t enough for arbitrary tenant code.</p>
<p>For trusted workloads (your own services), containers are cheaper, faster, and more portable. Hybrid approaches are common: VMs as Kubernetes nodes (cluster autoscaling spins up VMs), then many containers per node. Cloud providers offer per-second billing on both.</p>
<p>2026 trend: <strong>microVMs</strong> (Firecracker, Cloud Hypervisor) blur the line. They boot in 100ms like containers but provide VM-grade isolation. <strong>WebAssembly (Wasm)</strong> is the next abstraction layer down &mdash; even smaller, even faster, even more portable, but with a smaller ecosystem.</p>'''

ANSWERS[16] = r'''<p>Installing Docker on Linux varies by distribution. The official method uses Docker&rsquo;s apt or dnf repositories. For Ubuntu 22.04+ (the most common dev/CI runner OS):</p>
<pre><code># Remove any old Docker packages
sudo apt remove docker docker-engine docker.io containerd runc

# Install prerequisites
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository
echo &quot;deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release &amp;&amp; echo $VERSION_CODENAME) stable&quot; | \
  sudo tee /etc/apt/sources.list.d/docker.list

# Install
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Verify
sudo docker run hello-world
</code></pre>
<p>Post-install: add your user to the <code>docker</code> group so you don&rsquo;t need sudo:</p>
<pre><code>sudo usermod -aG docker $USER
newgrp docker  # or log out/in
docker run hello-world  # no sudo needed
</code></pre>
<p>For RHEL/CentOS/Fedora, use <code>dnf</code> with the equivalent Docker repo. For Amazon Linux 2023, use <code>dnf install -y docker</code>.</p>
<p>Alternatives in 2026:</p>
<ul>
<li><strong>Podman</strong> &mdash; Red Hat&rsquo;s daemonless, rootless container engine. Drop-in CLI compatible: <code>alias docker=podman</code>. Default on RHEL 9+, Fedora.</li>
<li><strong>nerdctl</strong> &mdash; CLI for containerd, Docker-CLI-compatible. What you&rsquo;d use if you&rsquo;re running containerd directly.</li>
<li><strong>Docker Desktop</strong> &mdash; for Mac/Windows dev. Now requires a paid license for orgs &gt;250 employees or &gt;$10M revenue. Alternatives: <strong>Colima</strong>, <strong>Rancher Desktop</strong>, <strong>OrbStack</strong> (macOS, very fast), <strong>Podman Desktop</strong>.</li>
</ul>
<p>For CI runners, you usually don&rsquo;t install Docker yourself &mdash; GitHub-hosted runners ship with Docker preinstalled. For self-hosted runners on K8s, use <strong>kaniko</strong> or <strong>BuildKit</strong> for rootless image builds without Docker-in-Docker risks.</p>'''

ANSWERS[17] = r'''<p>A <strong>GitHub repository</strong> (&ldquo;repo&rdquo;) is a hosted Git repository on GitHub.com plus a layer of project-management features built around it. At the core: source code, branches, tags, and history. Around it: collaboration tools (pull requests, code review, issues), CI/CD (Actions, Environments), security (Dependabot, secret scanning, CodeQL), packaging (Releases, Packages, Container Registry), documentation (README, Wiki, Pages), and access control (teams, roles, branch protection).</p>
<p>Repositories have visibility levels:</p>
<ul>
<li><strong>Public</strong> &mdash; anyone can clone and read. Free Actions minutes are larger here.</li>
<li><strong>Private</strong> &mdash; only invited collaborators can access. Most company code lives here.</li>
<li><strong>Internal</strong> &mdash; visible to all org members; useful for inner-source patterns at large companies.</li>
</ul>
<p>Each repo has:</p>
<ul>
<li><strong>Branches</strong> with optional protection rules (required reviewers, status checks, no force-push).</li>
<li><strong>Pull requests</strong> &mdash; the unit of code review and the trigger for most CI.</li>
<li><strong>Issues</strong> + <strong>Projects</strong> + <strong>Discussions</strong> for project management.</li>
<li><strong>Actions</strong> &mdash; YAML workflows in <code>.github/workflows/</code>.</li>
<li><strong>Wiki</strong> and <strong>Pages</strong> for documentation and static sites.</li>
<li><strong>Releases</strong> tied to git tags, with attached binary assets and changelogs.</li>
<li><strong>Webhooks</strong> for integrating external systems.</li>
<li><strong>Settings</strong> for branch protection, secrets, environments, deploy keys, OIDC trust, custom rulesets.</li>
</ul>
<p>Standard files at the root that GitHub recognizes:</p>
<ul>
<li><code>README.md</code> &mdash; rendered on the repo home page.</li>
<li><code>LICENSE</code> &mdash; recognized and surfaced in the sidebar.</li>
<li><code>.gitignore</code> &mdash; files Git should not track.</li>
<li><code>.github/CODEOWNERS</code> &mdash; auto-assigns reviewers for paths.</li>
<li><code>.github/PULL_REQUEST_TEMPLATE.md</code> and <code>ISSUE_TEMPLATE/*</code> &mdash; standard templates.</li>
<li><code>.github/dependabot.yml</code> &mdash; configure auto dependency updates.</li>
<li><code>SECURITY.md</code> &mdash; vulnerability reporting policy.</li>
</ul>
<p>For CI/CD, the repository is the natural unit: workflows, secrets, environments, and branch rules all scope to it. Larger orgs use a mix of repo-level and org-level settings (org secrets, org rulesets, org Actions cache).</p>'''

ANSWERS[18] = r'''<p><strong>GitHub Actions</strong> is GitHub&rsquo;s native CI/CD and automation platform, launched in 2018 and now the most popular CI tool for new projects in 2026. Workflows are YAML files in <code>.github/workflows/</code> triggered by repository events (push, PR, issue, schedule, manual dispatch, webhooks).</p>
<p>Anatomy:</p>
<ul>
<li><strong>Workflow</strong> &mdash; one YAML file. Has triggers, jobs, and global config.</li>
<li><strong>Job</strong> &mdash; a unit that runs on a single runner. Jobs run in parallel by default; chain with <code>needs:</code>.</li>
<li><strong>Step</strong> &mdash; a sequential command within a job. Either <code>uses:</code> (a reusable Action) or <code>run:</code> (shell).</li>
<li><strong>Action</strong> &mdash; a reusable piece of code published in the Marketplace or your own repo. Three types: JavaScript, Docker container, composite.</li>
<li><strong>Runner</strong> &mdash; the VM or container that executes the job. GitHub-hosted (ubuntu-latest, macos-latest, windows-latest) or self-hosted.</li>
</ul>
<p>Beyond CI/CD, Actions are used for:</p>
<ul>
<li>Issue and PR automation (auto-label, auto-assign, stale bot)</li>
<li>Scheduled tasks (nightly cleanup, weekly reports)</li>
<li>Release automation (semantic-release, changelog generation, npm publish)</li>
<li>Security scanning (CodeQL, Trivy, OSV-Scanner)</li>
<li>Documentation generation and deployment to GitHub Pages</li>
<li>Cross-repository workflows via repository_dispatch</li>
</ul>
<p>Key features:</p>
<ul>
<li><strong>Matrix builds</strong> &mdash; same job across multiple Node/Python/OS versions.</li>
<li><strong>Reusable workflows</strong> (<code>workflow_call</code>) &mdash; share workflows across repos.</li>
<li><strong>Composite actions</strong> &mdash; bundle a set of steps into a reusable Action.</li>
<li><strong>Environments</strong> &mdash; gate deployments with required reviewers, env-specific secrets, wait timers.</li>
<li><strong>OIDC</strong> &mdash; federate to AWS, GCP, Azure, HashiCorp Vault without storing long-lived credentials.</li>
<li><strong>Concurrency control</strong> &mdash; cancel in-progress runs when a newer one starts on the same branch.</li>
<li><strong>Artifacts and caches</strong> &mdash; share files between jobs; cache <code>node_modules</code> across runs.</li>
</ul>
<p>Pricing: free for public repos with high quotas; private repos get a monthly free allowance plus per-minute billing. Self-hosted runners are unlimited (you pay only for the underlying compute). The 2026 trend: most orgs run a mix of GitHub-hosted runners for general work and self-hosted on Kubernetes (via Actions Runner Controller) for heavy or specialized jobs.</p>'''

ANSWERS[19] = r'''<p>Installing Jenkins on a Linux server uses the official package repos. For Ubuntu/Debian:</p>
<pre><code># Install Java (Jenkins LTS needs Java 17 or 21 in 2026)
sudo apt update
sudo apt install -y fontconfig openjdk-17-jre

# Add Jenkins repository
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo &quot;deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/&quot; | \
  sudo tee /etc/apt/sources.list.d/jenkins.list &gt; /dev/null

# Install Jenkins
sudo apt update
sudo apt install -y jenkins

# Start &amp; enable
sudo systemctl enable --now jenkins
sudo systemctl status jenkins
</code></pre>
<p>Jenkins listens on port 8080 by default. Get the initial admin password to unlock the UI:</p>
<pre><code>sudo cat /var/lib/jenkins/secrets/initialAdminPassword
</code></pre>
<p>Open <code>http://server:8080</code>, paste the password, install suggested plugins, and create your admin user. Jenkins runs as the <code>jenkins</code> user; its home is <code>/var/lib/jenkins</code> (config, jobs, plugins, workspaces).</p>
<p>Production hardening:</p>
<ul>
<li><strong>Reverse proxy</strong> &mdash; put nginx or Caddy in front of Jenkins for TLS termination and HTTPS. Don&rsquo;t expose 8080 to the internet directly.</li>
<li><strong>Authentication</strong> &mdash; switch from local users to GitHub OAuth, LDAP, SAML, or OIDC.</li>
<li><strong>Authorization</strong> &mdash; use Role-Based Access Control plugin or Matrix Authorization.</li>
<li><strong>Backups</strong> &mdash; back up <code>/var/lib/jenkins</code> regularly (jobs, configs, credentials).</li>
<li><strong>Plugin hygiene</strong> &mdash; keep plugins updated, but pin versions in environments where stability matters.</li>
<li><strong>Agents</strong> &mdash; don&rsquo;t run jobs on the controller. Set up agent nodes (static, Docker, Kubernetes) and label them.</li>
</ul>
<p>2026 alternatives to bare-metal install:</p>
<ul>
<li><strong>Docker:</strong> <code>docker run -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk17</code> &mdash; easiest for evaluation.</li>
<li><strong>Kubernetes:</strong> install via the Jenkins Helm chart; pair with the Kubernetes plugin so each build runs in an ephemeral pod.</li>
<li><strong>CloudBees CI</strong> &mdash; commercial, managed-or-self-hosted Jenkins for enterprises with audit, security, and team management features.</li>
</ul>
<p>For new projects, ask whether you actually need Jenkins. GitHub Actions, GitLab CI, or CircleCI are simpler choices for most teams in 2026.</p>'''

ANSWERS[20] = r'''<p>A <strong>Docker registry</strong> is a server that stores and distributes Docker (OCI) images. Pipelines push images to a registry after building; deployment targets pull from it when starting containers. Registries are the source of truth for &ldquo;which version of which service is available&rdquo;.</p>
<p>The role in CI/CD:</p>
<ul>
<li><strong>Build &rarr; push:</strong> CI builds an image and pushes it tagged with the git SHA, branch, and/or semver version.</li>
<li><strong>Deploy &rarr; pull:</strong> Kubernetes, ECS, Docker, or any orchestrator pulls the image when starting containers.</li>
<li><strong>Promotion:</strong> the same image (same digest) flows from staging to prod, guaranteeing what was tested is what runs.</li>
<li><strong>Rollback:</strong> previous image tags remain available, enabling instant rollback by switching the tag.</li>
</ul>
<p>Major registries in 2026:</p>
<table>
<thead><tr><th>Registry</th><th>Notes</th></tr></thead>
<tbody>
<tr><td><strong>Docker Hub</strong></td><td>Default public registry; rate limits on anonymous pulls; paid plans for private repos</td></tr>
<tr><td><strong>GitHub Container Registry (ghcr.io)</strong></td><td>Free for public images; private images tied to repo permissions; dominant for OSS in 2026</td></tr>
<tr><td><strong>AWS Elastic Container Registry (ECR)</strong></td><td>Tightly integrated with IAM, ECS, EKS, Lambda; per-region; ECR Public for OSS</td></tr>
<tr><td><strong>Google Artifact Registry</strong></td><td>Replaces GCR; supports many formats besides Docker</td></tr>
<tr><td><strong>Azure Container Registry (ACR)</strong></td><td>Azure-native; geo-replication built-in</td></tr>
<tr><td><strong>Harbor</strong></td><td>OSS self-hosted; vulnerability scanning, signing, replication</td></tr>
<tr><td><strong>JFrog Artifactory</strong></td><td>Multi-format (Docker, npm, Maven, Helm); enterprise standard</td></tr>
<tr><td><strong>GitLab Container Registry</strong></td><td>Built into GitLab; per-project</td></tr>
</tbody>
</table>
<p>Push/pull:</p>
<pre><code>docker login ghcr.io -u me
docker tag myapp:1.0 ghcr.io/me/myapp:1.0
docker push ghcr.io/me/myapp:1.0
docker pull ghcr.io/me/myapp:1.0
</code></pre>
<p>Best practices: tag images with both <code>:sha-abc1234</code> (immutable, traceable) and <code>:1.2.3</code> (semver) and optionally <code>:latest</code> for convenience. Scan images for CVEs (Trivy, Grype, Snyk) before promoting to prod. Sign images with <strong>Sigstore Cosign</strong> and verify in Kubernetes admission control. Set up retention policies so old images don&rsquo;t bloat the registry indefinitely. Use <strong>image immutability</strong> rules &mdash; once a tag is pushed, it cannot be overwritten &mdash; to prevent supply-chain tampering.</p>'''

ANSWERS[21] = r'''<p>A <strong>Dockerfile</strong> describes how to build an image as a sequence of instructions. Each instruction creates a layer; layers are cached, so well-ordered Dockerfiles rebuild fast. Best practice in 2026 is <strong>multi-stage builds</strong> + <strong>non-root user</strong> + <strong>small base image</strong>.</p>
<p>Example for a Node.js + TypeScript API:</p>
<pre><code># syntax=docker/dockerfile:1.7
ARG NODE_VERSION=20.11-alpine

# --- Stage 1: install deps with cache ---
FROM node:${NODE_VERSION} AS deps
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev

# --- Stage 2: build TypeScript ---
FROM node:${NODE_VERSION} AS build
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

# --- Stage 3: minimal runtime image ---
FROM node:${NODE_VERSION}
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist         ./dist
COPY package.json ./

USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e &quot;require('http').get('http://localhost:3000/health', r =&gt; process.exit(r.statusCode === 200 ? 0 : 1))&quot;
CMD [&quot;node&quot;, &quot;dist/server.js&quot;]
</code></pre>
<p>Build it: <code>docker build -t myapi:1.0 .</code> You can pass <code>--build-arg NODE_VERSION=22-alpine</code> to override versions.</p>
<p>Why it&rsquo;s structured this way:</p>
<ul>
<li><strong>Separate deps stage</strong> caches <code>npm ci</code> as long as <code>package-lock.json</code> doesn&rsquo;t change &mdash; the slowest step.</li>
<li><strong>BuildKit cache mount</strong> persists the npm cache across builds for even faster rebuilds.</li>
<li><strong>Final stage copies only the runtime artifacts</strong> (<code>node_modules</code> + <code>dist</code>), not the build toolchain. Smaller image, smaller attack surface.</li>
<li><strong>USER node</strong> drops from root to a non-privileged user (<code>node</code> user is built into the official Node images).</li>
<li><strong>HEALTHCHECK</strong> lets Docker, ECS, and Kubernetes detect unhealthy containers.</li>
</ul>
<p>Add a <code>.dockerignore</code> to exclude <code>node_modules</code>, <code>.git</code>, build outputs, secrets &mdash; the build context is sent to the daemon, so excluding garbage speeds up builds and prevents leaking files. Scan with <code>docker scout</code> or <code>trivy image</code> before pushing. For ultimate slimness, switch the runtime base to <strong>distroless</strong> (<code>gcr.io/distroless/nodejs20-debian12</code>) or <strong>Chainguard</strong> images.</p>'''

ANSWERS[22] = r'''<p>A <strong>Pod</strong> is the smallest deployable unit in Kubernetes. It&rsquo;s a wrapper around one or more containers that share network namespace, IPC, and storage volumes. The containers in a pod run on the same node, share <code>localhost</code>, and can mount the same volumes &mdash; they&rsquo;re effectively co-located processes. Most pods have a single primary container, with secondary containers acting as <strong>sidecars</strong> (logging shipper, service mesh proxy, secrets fetcher) or <strong>init containers</strong> (run once before the main containers, e.g., DB migrations).</p>
<p>Example pod manifest:</p>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: api
  labels:
    app: api
spec:
  containers:
  - name: api
    image: ghcr.io/me/api:1.0
    ports:
    - containerPort: 3000
    env:
    - name: NODE_ENV
      value: production
    resources:
      requests: { cpu: 100m, memory: 256Mi }
      limits:   { cpu: 500m, memory: 512Mi }
    readinessProbe:
      httpGet: { path: /health, port: 3000 }
      periodSeconds: 5
    livenessProbe:
      httpGet: { path: /health, port: 3000 }
      periodSeconds: 30
</code></pre>
<p>Important properties:</p>
<ul>
<li><strong>Pods are ephemeral.</strong> When a pod dies, it dies forever &mdash; you don&rsquo;t restart it; a controller (Deployment, StatefulSet, DaemonSet) creates a replacement with a new IP.</li>
<li><strong>One IP per pod.</strong> All containers in the pod share that IP. They communicate over localhost.</li>
<li><strong>Shared volumes.</strong> Volumes declared in the pod spec are mounted into all containers that opt in.</li>
<li><strong>Resource requests + limits</strong> control scheduling and enforce quotas.</li>
<li><strong>Probes</strong> (readiness, liveness, startup) tell the kubelet when the pod is ready for traffic and when to restart it.</li>
</ul>
<p>You almost never create raw pods directly. Instead, use higher-level controllers:</p>
<ul>
<li><strong>Deployment</strong> &mdash; stateless replicas with rolling updates.</li>
<li><strong>StatefulSet</strong> &mdash; stable pod names + storage for databases, queues.</li>
<li><strong>DaemonSet</strong> &mdash; one pod per node (log shippers, monitoring agents, CNI).</li>
<li><strong>Job / CronJob</strong> &mdash; run-to-completion tasks.</li>
</ul>
<p>The pod is the boundary of co-location and shared lifecycle: scale up, you get more pods, each a fresh copy of the template. The 2026 trend: most teams keep pods to a single container plus a service-mesh sidecar (or use Istio Ambient / Linkerd to eliminate even that).</p>'''

ANSWERS[23] = r'''<p>A <strong>Jenkinsfile</strong> defines a Jenkins pipeline as code, stored at the root of your repository. The two syntaxes &mdash; declarative and scripted &mdash; both produce the same execution. Declarative is the modern default: structured, readable, easier to validate.</p>
<p>Minimal declarative Jenkinsfile:</p>
<pre><code>pipeline {
  agent any
  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timestamps()
  }
  triggers {
    pollSCM('H/5 * * * *')
  }
  environment {
    NODE_ENV = 'test'
    REGISTRY = 'ghcr.io/me'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Install')  { steps { sh 'npm ci' } }
    stage('Test') {
      parallel {
        stage('Lint') { steps { sh 'npm run lint' } }
        stage('Unit') { steps { sh 'npm test' } }
      }
    }
    stage('Build') {
      steps {
        sh 'npm run build'
        sh &quot;docker build -t ${REGISTRY}/api:${env.GIT_COMMIT} .&quot;
      }
    }
    stage('Push') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr',
            usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login ghcr.io -u $U --password-stdin'
          sh &quot;docker push ${REGISTRY}/api:${env.GIT_COMMIT}&quot;
        }
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps { sh &quot;kubectl set image deploy/api api=${REGISTRY}/api:${env.GIT_COMMIT}&quot; }
    }
  }
  post {
    always  { junit 'reports/**/*.xml'; archiveArtifacts 'dist/**' }
    success { slackSend(channel: '#deploys', message: &quot;${env.JOB_NAME} #${env.BUILD_NUMBER} succeeded&quot;) }
    failure { slackSend(channel: '#alerts', message: &quot;${env.JOB_NAME} #${env.BUILD_NUMBER} FAILED: ${env.BUILD_URL}&quot;) }
  }
}
</code></pre>
<p>Key sections:</p>
<ul>
<li><strong>agent</strong> &mdash; where the pipeline runs. <code>any</code>, <code>{ label 'docker' }</code>, <code>{ docker { image 'node:20' } }</code>, or a Kubernetes pod template.</li>
<li><strong>stages</strong> &mdash; logical phases shown in the UI.</li>
<li><strong>parallel</strong> &mdash; run sub-stages concurrently.</li>
<li><strong>when</strong> &mdash; conditional execution (branch, tag, expression).</li>
<li><strong>environment</strong> &mdash; env vars for the whole pipeline or per-stage.</li>
<li><strong>options</strong> &mdash; timeouts, retention, timestamps, ANSI color output.</li>
<li><strong>post</strong> &mdash; hooks: always, success, failure, unstable, changed.</li>
<li><strong>withCredentials</strong> &mdash; bind Jenkins-stored secrets to env vars without leaking them in logs.</li>
</ul>
<p>For Multibranch Pipelines, Jenkins discovers branches and PRs automatically and runs the Jenkinsfile from each branch. Combine with <strong>Shared Libraries</strong> for reusable Groovy across many repos. Validate locally with the <code>jenkins-cli declarative-linter</code> command or VS Code Jenkinsfile extensions.</p>'''

ANSWERS[24] = r'''<p>A typical CI/CD pipeline progresses through a series of <strong>stages</strong>, each with a clear pass/fail signal. The exact list varies by team, but the canonical stages in 2026:</p>
<table>
<thead><tr><th>#</th><th>Stage</th><th>What happens</th></tr></thead>
<tbody>
<tr><td>1</td><td><strong>Source</strong></td><td>Checkout the commit; resolve submodules, LFS objects, monorepo paths</td></tr>
<tr><td>2</td><td><strong>Install</strong></td><td>Restore dependency caches; <code>npm ci</code>, <code>pnpm install --frozen-lockfile</code></td></tr>
<tr><td>3</td><td><strong>Lint &amp; format check</strong></td><td>ESLint, Prettier, Biome &mdash; fast feedback on style</td></tr>
<tr><td>4</td><td><strong>Type-check</strong></td><td><code>tsc --noEmit</code>; mypy, pyright</td></tr>
<tr><td>5</td><td><strong>Unit tests</strong></td><td>Vitest, Jest, pytest &mdash; fast, isolated, run on every PR</td></tr>
<tr><td>6</td><td><strong>Integration tests</strong></td><td>Tests against a real DB / cache / queue spun up as containers</td></tr>
<tr><td>7</td><td><strong>Build</strong></td><td>Compile, transpile, bundle (Vite, Turbopack, esbuild, Rspack); produce artifact</td></tr>
<tr><td>8</td><td><strong>Security scan</strong></td><td>SAST (CodeQL, Semgrep), SCA (Snyk, Socket.dev), container scan (Trivy, Grype)</td></tr>
<tr><td>9</td><td><strong>Package</strong></td><td>Build Docker image; tag with SHA + semver; push to registry; sign with Cosign</td></tr>
<tr><td>10</td><td><strong>Deploy to staging</strong></td><td>Roll out to a pre-prod environment; run smoke tests + E2E (Playwright)</td></tr>
<tr><td>11</td><td><strong>Manual approval</strong></td><td>(CD with gate) Required reviewer clicks &ldquo;Approve&rdquo; on a GitHub Environment / Jenkins input step</td></tr>
<tr><td>12</td><td><strong>Deploy to production</strong></td><td>Canary or blue-green; auto-rollback on metric anomaly</td></tr>
<tr><td>13</td><td><strong>Verify &amp; promote</strong></td><td>Watch SLOs, error budgets, RUM signals; promote canary to 100% if healthy</td></tr>
<tr><td>14</td><td><strong>Post-deploy</strong></td><td>Tag release, generate changelog, notify Slack/Datadog, update docs</td></tr>
</tbody>
</table>
<p>Not every project needs all 14 &mdash; a small library might stop at &ldquo;publish to npm&rdquo;. A regulated bank might add several more stages (compliance attestation, audit log generation, change-advisory-board approval).</p>
<p>Stages are arranged so that <strong>fast checks fail fast</strong>. Lint and type-check before unit tests; unit tests before integration; everything before any deploy. The earlier a problem is caught, the cheaper to fix. The 2026 best practice is to also run a <strong>preview environment</strong> deploy on every PR (Vercel, Netlify, Render, Coherence, fly.io preview apps) so reviewers can click and try the change.</p>'''

ANSWERS[25] = r'''<p>Environment variables are the standard way to pass configuration into pipeline jobs &mdash; secrets, environment names, version numbers, feature flags. Every CI system supports them, with three scopes: <strong>workflow / pipeline level</strong>, <strong>job level</strong>, and <strong>step level</strong>.</p>
<p>GitHub Actions:</p>
<pre><code>env:
  GLOBAL_VAR: hello                  # workflow scope

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      JOB_VAR: world                 # job scope
    steps:
      - run: echo &quot;$GLOBAL_VAR $JOB_VAR&quot;
        env:
          STEP_VAR: '!'              # step scope
      - name: Use a secret
        run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
</code></pre>
<p>GitLab CI:</p>
<pre><code>variables:
  GLOBAL_VAR: hello

build:
  stage: build
  variables:
    JOB_VAR: world
  script:
    - echo &quot;$GLOBAL_VAR $JOB_VAR&quot;
</code></pre>
<p>Jenkins (declarative):</p>
<pre><code>environment {
  GLOBAL_VAR = 'hello'
}
stages {
  stage('Build') {
    environment { JOB_VAR = 'world' }
    steps { sh 'echo $GLOBAL_VAR $JOB_VAR' }
  }
}
</code></pre>
<p>Best practices:</p>
<ul>
<li><strong>Never put secrets in plain env declarations or YAML.</strong> Use the CI&rsquo;s secrets store: GitHub Actions <code>secrets.*</code>, GitLab CI/CD variables (masked, protected), Jenkins Credentials Plugin, Doppler, Infisical, HashiCorp Vault.</li>
<li><strong>Mark secrets as masked</strong> so they&rsquo;re redacted from logs.</li>
<li><strong>Restrict secret scope</strong> to the protected branches/environments that need them.</li>
<li><strong>Prefer OIDC over long-lived secrets</strong> when integrating with cloud providers (AWS, GCP, Azure all support GitHub OIDC). The runner exchanges a short-lived OIDC token for a temporary cloud credential &mdash; no rotating API keys.</li>
<li><strong>Use environment-scoped variables</strong> for things that differ between staging and prod (DB URL, feature flags). GitHub Environments, GitLab Environments, Jenkins Environment plugins all support this.</li>
<li><strong>Document required env vars</strong> in your README and validate at startup so missing config fails fast.</li>
</ul>
<p>For complex setups, a config-as-code library like <strong>Doppler</strong> or <strong>Infisical</strong> centralizes secrets across environments and inject them into the pipeline at runtime, eliminating per-CI duplication.</p>'''


ANSWERS[26] = r'''<p>A <strong>Docker Compose file</strong> (<code>compose.yaml</code> or the older <code>docker-compose.yml</code>) is a YAML manifest that declares a multi-container application as a single unit &mdash; services, networks, volumes, environment, ports, dependencies. <code>docker compose up</code> reads it and starts everything; <code>down</code> stops it. It&rsquo;s the standard tool for local development of multi-service apps and ships built-in with Docker Engine since v20.</p>
<p>Minimal example for a MERN dev stack:</p>
<pre><code># compose.yaml
services:
  mongo:
    image: mongo:7
    volumes: [mongo-data:/data/db]
    ports: ['27017:27017']
  api:
    build: ./server
    environment:
      MONGO_URL: mongodb://mongo:27017/app
      NODE_ENV: development
    ports: ['4000:4000']
    depends_on: [mongo]
    develop:
      watch:
        - { path: ./server, action: sync, target: /app }
  web:
    build: ./client
    ports: ['5173:5173']
volumes:
  mongo-data:
</code></pre>
<p>Key features:</p>
<ul>
<li><strong>Service discovery</strong> via service name &mdash; <code>api</code> reaches Mongo at <code>mongo:27017</code>, no IPs needed.</li>
<li><strong>Profiles</strong> let you opt into optional services: <code>docker compose --profile debug up</code>.</li>
<li><strong>Watch mode</strong> (<code>compose watch</code>) hot-reloads files into the container.</li>
<li><strong>Multiple Compose files</strong> can be layered: <code>-f compose.yaml -f compose.prod.yaml</code> for env-specific overrides.</li>
</ul>
<p>In CI, Compose is useful for spinning up integration test dependencies (Mongo, Redis, MailHog) before running tests. For production at scale, prefer Kubernetes or AWS ECS/Fargate &mdash; Compose is dev-tier orchestration. Docker Swarm reads the same format but Swarm itself is largely deprecated in 2026 in favor of K8s.</p>'''

ANSWERS[27] = r'''<p>Kubernetes scales applications along three axes: <strong>horizontal</strong> (more pod replicas), <strong>vertical</strong> (bigger pods), and <strong>cluster-level</strong> (more nodes). The default and most useful is horizontal scaling.</p>
<p><strong>Manual scaling:</strong> <code>kubectl scale deploy/api --replicas=5</code> immediately adjusts replica count.</p>
<p><strong>Horizontal Pod Autoscaler (HPA)</strong> auto-scales based on metrics:</p>
<pre><code>apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api-hpa }
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
    - type: External
      external:
        metric: { name: sqs_queue_depth }
        target: { type: AverageValue, averageValue: '50' }
</code></pre>
<p><strong>Other scaling tools (2026):</strong></p>
<ul>
<li><strong>KEDA</strong> &mdash; event-driven autoscaling on 60+ external sources (SQS depth, Kafka lag, HTTP RPS, cron). Can scale to zero, which HPA cannot.</li>
<li><strong>Vertical Pod Autoscaler (VPA)</strong> &mdash; recommends or applies CPU/memory requests based on actual usage. Use in <em>recommend</em> mode in production; <em>auto</em> mode causes restarts.</li>
<li><strong>Cluster Autoscaler / Karpenter</strong> &mdash; adds/removes nodes when pods can&rsquo;t schedule. Karpenter (AWS, now upstream) is faster and picks better instance types.</li>
</ul>
<p>Always pair HPA with <strong>readiness probes</strong>, <strong>PodDisruptionBudgets</strong> (so scale-down doesn&rsquo;t take everything down), and <strong>graceful shutdown</strong> handling SIGTERM. Scale on the metric that actually reflects load &mdash; for queue workers, queue depth beats CPU; for HTTP APIs, RPS or p95 latency beats CPU.</p>'''

ANSWERS[28] = r'''<p>GitHub Actions secrets are encrypted environment variables stored at the <strong>repository</strong>, <strong>environment</strong>, or <strong>organization</strong> level. They&rsquo;re injected into workflows at runtime, masked in logs, and never visible in the UI after creation.</p>
<p><strong>Where to store:</strong></p>
<ul>
<li><strong>Repository secrets</strong> &mdash; available to all workflows in the repo. Settings &rarr; Secrets and variables &rarr; Actions.</li>
<li><strong>Environment secrets</strong> &mdash; scoped to a deployment environment (production, staging) with optional approval gates and branch restrictions.</li>
<li><strong>Organization secrets</strong> &mdash; shared across selected repos.</li>
</ul>
<p><strong>Using secrets in a workflow:</strong></p>
<pre><code>name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production         # gates + env secrets
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: ./deploy.sh
</code></pre>
<p><strong>Best practices (2026):</strong></p>
<ul>
<li><strong>Prefer OIDC over long-lived secrets</strong> for cloud providers. Configure <code>permissions: id-token: write</code>, then use <code>aws-actions/configure-aws-credentials@v4</code> with <code>role-to-assume</code> instead of storing AWS keys.</li>
<li><strong>Never echo secrets</strong> &mdash; even masked, they can leak through error traces and side-channel logs.</li>
<li><strong>Limit secret scope</strong> &mdash; environment secrets with required reviewers + branch protections.</li>
<li><strong>Rotate regularly</strong> and use GitHub&rsquo;s push-protection + secret scanning to catch leaks.</li>
<li><strong>Centralize via Doppler / Infisical / HashiCorp Vault</strong> for cross-system secret sync, so the same secret in a hundred repos rotates from one place.</li>
</ul>
<p>Variables (non-secret config) go in the same UI under &ldquo;Variables&rdquo; tab and use <code>${{ vars.MY_VAR }}</code>.</p>'''

ANSWERS[29] = r'''<p>A <strong>Docker image</strong> is a static, read-only template &mdash; a layered tarball built from a Dockerfile, stored in a registry, identified by a name+tag (<code>node:20-alpine</code>) or digest (<code>sha256:abc&hellip;</code>). It contains the filesystem, dependencies, and metadata needed to run a process.</p>
<p>A <strong>Docker container</strong> is a running (or stopped) instance of an image &mdash; a process in an isolated namespace + cgroup with a writable layer on top of the immutable image layers. You can have many containers from the same image.</p>
<p>The class/instance analogy holds:</p>
<table>
<thead><tr><th>Image</th><th>Container</th></tr></thead>
<tbody>
<tr><td>Class / blueprint</td><td>Instance / running object</td></tr>
<tr><td>Built once via <code>docker build</code></td><td>Created per <code>docker run</code></td></tr>
<tr><td>Immutable</td><td>Has a writable filesystem layer</td></tr>
<tr><td>Stored in a registry (Docker Hub, ECR, GHCR)</td><td>Lives on a host</td></tr>
<tr><td>Versioned by tag/digest</td><td>Identified by container ID/name</td></tr>
<tr><td>No state</td><td>Has runtime state (memory, files, network)</td></tr>
</tbody>
</table>
<p>Common commands:</p>
<pre><code>docker build -t myapp:1.2.3 .       # build an image
docker images                       # list images
docker run -d --name api myapp:1.2.3 # create and run a container
docker ps                           # list running containers
docker stop api &amp;&amp; docker rm api   # stop and remove the container
docker rmi myapp:1.2.3              # remove the image
</code></pre>
<p>The writable container layer is ephemeral: when the container is removed, those changes are lost. Persistent data should live in <strong>volumes</strong> (named or bind-mount). For app state in production, never rely on the container filesystem &mdash; use external databases, S3, or volumes mounted into stateful workloads.</p>'''

ANSWERS[30] = r'''<p>Deploying a Docker container to Kubernetes requires three steps: push the image to a registry, write a manifest, and apply it.</p>
<p><strong>1. Push the image:</strong></p>
<pre><code>docker build -t ghcr.io/acme/api:1.0.0 .
docker push ghcr.io/acme/api:1.0.0
</code></pre>
<p><strong>2. Write the Deployment + Service manifest:</strong></p>
<pre><code># api.yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 3
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          ports: [{ containerPort: 4000 }]
          env:
            - name: MONGO_URL
              valueFrom: { secretKeyRef: { name: api-secrets, key: mongo-url } }
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
          readinessProbe:
            httpGet: { path: /healthz, port: 4000 }
            initialDelaySeconds: 5
---
apiVersion: v1
kind: Service
metadata: { name: api }
spec:
  selector: { app: api }
  ports: [{ port: 80, targetPort: 4000 }]
  type: ClusterIP
</code></pre>
<p><strong>3. Apply:</strong></p>
<pre><code>kubectl apply -f api.yaml
kubectl rollout status deploy/api
kubectl get pods -l app=api
</code></pre>
<p>For external access, add an Ingress (NGINX Ingress, Traefik) or a LoadBalancer Service. For multiple environments and templating, use <strong>Helm</strong> charts or <strong>Kustomize</strong>. For GitOps deployment from CI, push manifests to Git and let <strong>Argo CD</strong> or <strong>Flux</strong> reconcile &mdash; the CI never gets cluster credentials.</p>
<p>Always include resource requests/limits, readiness/liveness probes, and a graceful-shutdown handler in your container, otherwise rolling updates and autoscaling misbehave.</p>'''

ANSWERS[31] = r'''<p>Connecting Jenkins to GitHub combines authentication (so Jenkins can pull and report status) and triggering (so pushes start builds). The 2026 best path is <strong>GitHub App</strong> credentials &mdash; not personal access tokens.</p>
<p><strong>Authentication setup:</strong></p>
<ul>
<li>Install the <strong>GitHub Branch Source Plugin</strong> in Jenkins.</li>
<li>Create a GitHub App (Settings &rarr; Developer settings &rarr; GitHub Apps) with permissions: <em>Contents: Read</em>, <em>Metadata: Read</em>, <em>Pull requests: Read &amp; Write</em>, <em>Commit statuses: Read &amp; Write</em>.</li>
<li>Install the App on the target repo or org.</li>
<li>In Jenkins: Manage Jenkins &rarr; Credentials &rarr; Add &ldquo;GitHub App&rdquo; with the App ID + private key.</li>
</ul>
<p><strong>Triggering builds:</strong></p>
<ul>
<li><strong>Webhook</strong> from GitHub &rarr; <code>https://jenkins.example.com/github-webhook/</code>. Push events fire jobs immediately. Most common in 2026.</li>
<li><strong>Multibranch Pipeline job</strong> &mdash; auto-discovers branches and PRs, scans periodically, and creates one Jenkins job per branch/PR. Runs the <code>Jenkinsfile</code> at the branch tip.</li>
<li><strong>Pull request comment trigger</strong> via the GitHub PR Builder plugin (e.g. <code>retest this please</code>).</li>
</ul>
<p><strong>Reporting back:</strong></p>
<p>Jenkins posts commit statuses (<em>pending</em> &rarr; <em>success</em> / <em>failure</em>) so PRs show CI checks. Configure under &ldquo;Properties &rarr; GitHub project&rdquo; in the job, and use <code>githubNotify</code> from <code>Jenkinsfile</code> stages for granular checks.</p>
<p><strong>Honest 2026 take:</strong> Jenkins+GitHub remains common in regulated/on-prem shops, but greenfield teams overwhelmingly default to <strong>GitHub Actions</strong> (zero infra, native integration), <strong>Buildkite</strong> (self-hosted runners + cloud control), or <strong>Tekton/Argo Workflows</strong> on K8s. Pick Jenkins only when policy requires self-managed CI or when a heavy plugin ecosystem (e.g. Blue Ocean dashboards, complex Job DSL) genuinely matters.</p>'''

ANSWERS[32] = r'''<p><strong>Helm</strong> is the de facto package manager for Kubernetes. A <strong>Helm chart</strong> is a versioned bundle of YAML templates plus a values file, parameterized so the same chart deploys to dev/staging/prod with different settings. Helm renders templates with values, applies the result to the cluster, and tracks the release as a versioned history (so you can roll back).</p>
<p>Chart layout:</p>
<pre><code>mychart/
├── Chart.yaml          # name, version, appVersion
├── values.yaml         # default values
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── _helpers.tpl
└── charts/             # subchart dependencies
</code></pre>
<p>Common commands:</p>
<pre><code>helm install api ./mychart -n prod \
  --set image.tag=1.2.3 -f values.prod.yaml
helm upgrade api ./mychart -n prod --set image.tag=1.2.4
helm rollback api 1 -n prod          # rollback to revision 1
helm list -n prod
helm template ./mychart               # render to YAML without installing
</code></pre>
<p><strong>Why Helm matters:</strong></p>
<ul>
<li><strong>Reuse</strong> &mdash; popular charts (Bitnami, ingress-nginx, cert-manager, kube-prometheus-stack) make installing complex software a one-liner.</li>
<li><strong>Templating</strong> &mdash; loops, conditionals, and value injection avoid the &ldquo;copy-paste 15 YAML files per env&rdquo; trap.</li>
<li><strong>Release lifecycle</strong> &mdash; install/upgrade/rollback/uninstall with history.</li>
<li><strong>Hooks</strong> &mdash; pre-install, post-upgrade lifecycle hooks for migrations and one-time jobs.</li>
</ul>
<p><strong>Alternatives in 2026:</strong> <strong>Kustomize</strong> (overlays without templating, good for simpler stacks; built into <code>kubectl</code>), <strong>Argo CD ApplicationSets</strong> (combine Helm or Kustomize with GitOps), <strong>Cdk8s</strong> (TypeScript/Python instead of YAML), <strong>Timoni</strong> (CUE-based, fixes Helm&rsquo;s templating fragility). Most teams settle on <em>Helm for third-party software, Kustomize or raw YAML + Argo CD for their own services</em>.</p>'''

ANSWERS[33] = r'''<p>A <strong>Dockerfile</strong> describes how to build an image: a base, copies, commands, and metadata. <code>docker build</code> reads it line by line and produces a layered image you can run.</p>
<p>Minimal Node.js example:</p>
<pre><code># Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
EXPOSE 4000
CMD ["node", "server.js"]
</code></pre>
<p>Build it:</p>
<pre><code>docker build -t myapp:1.0.0 .
# Or with BuildKit cache + multi-platform:
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --cache-to type=gha --cache-from type=gha \
  -t ghcr.io/acme/myapp:1.0.0 --push .
</code></pre>
<p><strong>Better in production &mdash; multi-stage build with non-root user:</strong></p>
<pre><code>FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -S app &amp;&amp; adduser -S app -G app
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist          ./dist
USER app
EXPOSE 4000
CMD ["node", "dist/server.js"]
</code></pre>
<p><strong>Best practices (2026):</strong></p>
<ul>
<li><strong>Pin base images by digest</strong>, not just tag, for reproducibility.</li>
<li><strong>Multi-stage builds</strong> drop dev dependencies and build tools from the final image.</li>
<li><strong>Layer order</strong> &mdash; copy <code>package.json</code> before source so dependency layers cache.</li>
<li><strong>Run as non-root</strong> with <code>USER</code>.</li>
<li><strong>.dockerignore</strong> &mdash; exclude <code>node_modules</code>, <code>.git</code>, secrets.</li>
<li><strong>Distroless or Alpine</strong> bases for smaller, lower-CVE surface.</li>
<li><strong>Sign with cosign</strong> + push SBOM (<code>docker buildx --sbom=true --provenance=true</code>).</li>
</ul>
<p>Alternatives like <strong>Buildpacks</strong> (Heroku/CNB) and <strong>Nixpacks</strong> (Railway) skip the Dockerfile entirely &mdash; they detect the language and produce a hardened image automatically.</p>'''

ANSWERS[34] = r'''<p>A GitHub repository (<em>repo</em>) is a Git project hosted on GitHub with extra collaboration features: issues, pull requests, branch protections, Actions, releases, packages. Setup takes a minute via web UI or <code>gh</code> CLI.</p>
<p><strong>Via the GitHub CLI (recommended for scripting):</strong></p>
<pre><code>gh auth login
gh repo create acme/my-app --private --clone --add-readme
cd my-app
echo 'node_modules' &gt;&gt; .gitignore
git add . &amp;&amp; git commit -m 'chore: initial commit'
git push
</code></pre>
<p><strong>Via web UI:</strong> github.com/new &rarr; choose owner, name, visibility (public / private / internal), tick &ldquo;Add a README&rdquo;, &ldquo;Add .gitignore&rdquo;, license. Done.</p>
<p><strong>Wire up an existing local project:</strong></p>
<pre><code>git init
git add .
git commit -m 'feat: initial import'
gh repo create acme/my-app --private --source=. --push
</code></pre>
<p><strong>Recommended hygiene right after creation:</strong></p>
<ul>
<li><strong>Branch protection</strong> on <code>main</code> &mdash; require PR review, passing status checks, signed commits, and linear history. Settings &rarr; Branches.</li>
<li><strong>Default branch</strong> set to <code>main</code> (default since 2020).</li>
<li><strong>CODEOWNERS</strong> file for automatic review assignment.</li>
<li><strong>Dependabot</strong> + <strong>Secret scanning</strong> + <strong>CodeQL</strong> &mdash; all under Settings &rarr; Code security.</li>
<li><strong>License</strong> &mdash; MIT/Apache-2.0/AGPL/proprietary as appropriate.</li>
<li><strong>Conventional Commits</strong> + <strong>release-please</strong> or <strong>changesets</strong> for automated versioning and changelogs.</li>
</ul>
<p><strong>Repo templates and starters:</strong> create your own template repo (<code>--template</code>) so every new service starts with the same lint, test, CI, and Docker scaffolding. Tools like <strong>Backstage</strong> or <strong>Cookiecutter</strong> automate this organization-wide.</p>'''

ANSWERS[35] = r'''<p>Jenkins plugins extend the core with new build steps, integrations (Git, Docker, Slack, AWS), UI features (Blue Ocean), and pipeline syntax. Jenkins ships a slim core; almost everything useful is a plugin.</p>
<p><strong>Installing plugins:</strong></p>
<ul>
<li>Manage Jenkins &rarr; Plugins &rarr; Available plugins. Search, tick, install. Restart if needed.</li>
<li>Or via CLI/Configuration-as-Code: list plugins in <code>plugins.txt</code> and provision them at startup with <code>jenkins-plugin-cli --plugin-file plugins.txt</code>. This is the production path &mdash; reproducible installs.</li>
</ul>
<p><strong>Using a plugin:</strong> after installing, plugins typically appear in three places:</p>
<ul>
<li><strong>Job configuration</strong> &mdash; new build steps, post-build actions, triggers.</li>
<li><strong>Pipeline DSL</strong> &mdash; new Groovy steps for <code>Jenkinsfile</code>, e.g. <code>slackSend</code>, <code>withAWS</code>, <code>kubernetesDeploy</code>.</li>
<li><strong>Global configuration</strong> &mdash; credentials, server endpoints, tool installations.</li>
</ul>
<p><strong>Pipeline example using two plugins (Docker Pipeline + Slack):</strong></p>
<pre><code>pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        script {
          docker.build("acme/api:${env.BUILD_NUMBER}")
        }
      }
    }
  }
  post {
    success { slackSend channel: '#deploys', message: "&#9989; ${env.JOB_NAME} #${env.BUILD_NUMBER} succeeded" }
    failure { slackSend channel: '#deploys', message: "&#10060; ${env.JOB_NAME} #${env.BUILD_NUMBER} failed" }
  }
}
</code></pre>
<p><strong>Essential plugins to know:</strong> Pipeline, Git, GitHub Branch Source, Credentials Binding, Docker Pipeline, Kubernetes, Blue Ocean, Configuration as Code (JCasC), Job DSL, Slack Notification, AWS Steps, SonarQube Scanner, Mailer.</p>
<p><strong>Plugin hygiene:</strong> Jenkins plugins are a major CVE surface. Pin versions in <code>plugins.txt</code>, run the Plugin Health Score check, remove unused plugins, and use Configuration as Code so the entire Jenkins setup is reproducible from Git. The plugin sprawl is the #1 reason teams migrate away from Jenkins to GitHub Actions or Buildkite.</p>'''

ANSWERS[36] = r'''<p>A Kubernetes <strong>Service</strong> is a stable network endpoint for a set of pods. Pods are ephemeral &mdash; they get recreated, rescheduled, IPs change &mdash; so clients can&rsquo;t target pods directly. A Service gives you a fixed DNS name and virtual IP that load-balances to whatever pods match its selector.</p>
<p>Service types:</p>
<table>
<thead><tr><th>Type</th><th>Use case</th></tr></thead>
<tbody>
<tr><td><strong>ClusterIP</strong> (default)</td><td>Internal-only; reachable from other pods at <code>svc-name.namespace.svc.cluster.local</code></td></tr>
<tr><td><strong>NodePort</strong></td><td>Exposes a static port on every node. Mostly for dev/local clusters.</td></tr>
<tr><td><strong>LoadBalancer</strong></td><td>Provisions a cloud load balancer (AWS NLB/ALB, GCP LB). Public traffic entry point.</td></tr>
<tr><td><strong>ExternalName</strong></td><td>DNS CNAME alias to an external service.</td></tr>
<tr><td><strong>Headless</strong> (<code>clusterIP: None</code>)</td><td>No virtual IP; DNS returns pod IPs. Used by StatefulSets and clients that do their own load balancing (gRPC).</td></tr>
</tbody>
</table>
<p>Example:</p>
<pre><code>apiVersion: v1
kind: Service
metadata: { name: api, namespace: prod }
spec:
  type: ClusterIP
  selector: { app: api }
  ports:
    - name: http
      port: 80
      targetPort: 4000
</code></pre>
<p>From any pod in the cluster: <code>http://api.prod.svc.cluster.local</code> (or just <code>http://api</code> from same namespace).</p>
<p><strong>For external HTTP traffic</strong>, prefer an <strong>Ingress</strong> (one LoadBalancer fronting many services with hostname/path routing) or the newer <strong>Gateway API</strong> &mdash; the modern, more expressive successor adopted across NGINX, Istio, Cilium, and Envoy gateway implementations.</p>
<p>Services use <strong>kube-proxy</strong> (iptables, IPVS, or nftables) or <strong>eBPF</strong> (Cilium) to do load balancing. For service mesh features &mdash; mTLS, retries, traffic shifting &mdash; layer Linkerd, Istio Ambient, or Cilium Service Mesh on top.</p>'''

ANSWERS[37] = r'''<p>A CI/CD pipeline is the technical backbone of <strong>DevOps</strong>: it&rsquo;s how the cultural goals (small batches, shared ownership, fast feedback, automated quality) become daily reality. DevOps without CI/CD is aspirational; CI/CD without DevOps is busywork.</p>
<p><strong>The role it plays:</strong></p>
<ul>
<li><strong>Fast feedback</strong> &mdash; every push runs lint/tests/builds in minutes, so defects are caught while context is fresh.</li>
<li><strong>Reduced batch size</strong> &mdash; small frequent merges replace risky big-bang releases.</li>
<li><strong>Shared ownership</strong> &mdash; the pipeline is a contract: dev, ops, security, and QA all see the same gates.</li>
<li><strong>Automation as policy</strong> &mdash; security scans, license checks, performance budgets are enforced by code, not by gatekeepers.</li>
<li><strong>Repeatable production changes</strong> &mdash; same tested artifact ships to staging and prod via parameterized deploy.</li>
<li><strong>Audit + compliance</strong> &mdash; every deploy is traceable to a commit, a build, an approver. Critical for SOC 2, HIPAA, PCI.</li>
</ul>
<p><strong>Mapping to DORA metrics</strong> (the standard DevOps KPIs):</p>
<table>
<thead><tr><th>DORA metric</th><th>What CI/CD enables</th></tr></thead>
<tbody>
<tr><td>Deployment frequency</td><td>Automated tests + auto-promote &rArr; dozens of deploys/day</td></tr>
<tr><td>Lead time for changes</td><td>From commit to prod in minutes/hours, not days</td></tr>
<tr><td>Change failure rate</td><td>Pre-merge tests + canary deploys catch regressions</td></tr>
<tr><td>Mean time to recovery (MTTR)</td><td>Automated rollback + feature flags</td></tr>
</tbody>
</table>
<p>Modern DevOps adds <strong>GitOps</strong> on top: production state is declared in Git, and Argo CD/Flux reconcile the cluster. <strong>Progressive delivery</strong> (Argo Rollouts, Flagger, LaunchDarkly) replaces blue-green with metric-driven canaries. <strong>Platform engineering</strong> (Backstage, Humanitec, Port) wraps these primitives into self-service developer experiences. The pipeline is no longer just a build server &mdash; it&rsquo;s the operating model.</p>'''

ANSWERS[38] = r'''<p>Pushing a Docker image to Docker Hub takes three steps: log in, tag the image with your username, push.</p>
<pre><code># 1. Log in (uses ~/.docker/config.json)
docker login                       # interactive
# Or with a Personal Access Token (recommended over password):
echo &quot;$DOCKER_TOKEN&quot; | docker login -u myuser --password-stdin

# 2. Tag the image
docker build -t myapp:1.0.0 .
docker tag myapp:1.0.0 myuser/myapp:1.0.0
docker tag myapp:1.0.0 myuser/myapp:latest

# 3. Push
docker push myuser/myapp:1.0.0
docker push myuser/myapp:latest
</code></pre>
<p><strong>Repository naming</strong> follows <code>username/repo:tag</code>. Without a registry hostname, Docker assumes Docker Hub. For other registries it&rsquo;s explicit:</p>
<ul>
<li><strong>Docker Hub:</strong> <code>myuser/myapp:1.0.0</code></li>
<li><strong>GitHub Container Registry:</strong> <code>ghcr.io/acme/myapp:1.0.0</code></li>
<li><strong>AWS ECR:</strong> <code>123.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0.0</code></li>
<li><strong>Google Artifact Registry:</strong> <code>us-docker.pkg.dev/proj/repo/myapp:1.0.0</code></li>
</ul>
<p><strong>From CI (GitHub Actions example):</strong></p>
<pre><code>- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: |
      myuser/myapp:${{ github.sha }}
      myuser/myapp:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
    platforms: linux/amd64,linux/arm64
    sbom: true
    provenance: true
</code></pre>
<p><strong>Tagging strategy:</strong> never deploy <code>:latest</code> in production &mdash; it&rsquo;s a moving target. Use immutable tags (semver, git SHA, or build number) plus <code>:latest</code> as a convenience pointer. For supply-chain trust, sign images with <strong>cosign</strong> and verify in Kubernetes with <strong>policy-controller</strong> or <strong>Kyverno</strong>.</p>
<p><strong>Honest 2026 advice:</strong> Docker Hub is rate-limited for anonymous pulls. For production, push to <strong>GHCR</strong> (free with GitHub), <strong>ECR</strong>, or <strong>Cloudflare Container Registry</strong> &mdash; faster, no rate limits, and tighter cloud integration.</p>'''

ANSWERS[39] = r'''<p>A GitHub Action for building and pushing a Docker image is a few lines of YAML. The official <code>docker/build-push-action</code> handles BuildKit, multi-arch, caching, SBOMs, and provenance attestations.</p>
<pre><code># .github/workflows/docker.yml
name: Docker Build &amp; Push

on:
  push:
    branches: [main]
    tags: ['v*']

permissions:
  contents: read
  packages: write          # for GHCR
  id-token: write          # for cosign keyless signing

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-qemu-action@v3       # multi-arch
      - uses: docker/setup-buildx-action@v3     # BuildKit

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,format=long
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}

      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          platforms: linux/amd64,linux/arm64
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          sbom: true
          provenance: mode=max

      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.meta.outputs.digest }}
</code></pre>
<p><strong>What this does:</strong></p>
<ul>
<li>Sets up BuildKit and QEMU for multi-arch (amd64 + arm64) builds.</li>
<li>Logs into GHCR using the auto-provided <code>GITHUB_TOKEN</code> (no PAT needed).</li>
<li>Generates rich tag metadata: git SHA, branch name, semver, and <code>:latest</code> on main.</li>
<li>Builds with BuildKit, caches layers in GitHub Actions cache, pushes the image.</li>
<li>Generates an SBOM (CycloneDX) and SLSA provenance attestation.</li>
<li>Signs the image with cosign keyless (uses OIDC, no key management).</li>
</ul>
<p><strong>For AWS ECR or Docker Hub</strong>, swap the <code>login-action</code> step for those registries (and use <code>aws-actions/configure-aws-credentials</code> with OIDC for ECR &mdash; no AWS keys in secrets). The rest is identical.</p>'''

ANSWERS[40] = r'''<p>A Kubernetes <strong>Deployment</strong> manages a replicated, stateless app. You declare desired state &mdash; image, replica count, environment, resources &mdash; and the Deployment controller creates/updates a <strong>ReplicaSet</strong>, which in turn creates <strong>Pods</strong>. When you change the spec (e.g. new image), it does a <strong>rolling update</strong> with configurable surge/unavailable, and keeps revision history for rollbacks.</p>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels: { app: api }
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 25%, maxUnavailable: 0 }
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          ports: [{ containerPort: 4000 }]
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
          readinessProbe:
            httpGet: { path: /healthz, port: 4000 }
          livenessProbe:
            httpGet: { path: /healthz, port: 4000 }
            initialDelaySeconds: 30
</code></pre>
<p><strong>Useful commands:</strong></p>
<pre><code>kubectl apply -f deployment.yaml
kubectl rollout status deploy/api
kubectl set image deploy/api api=ghcr.io/acme/api:1.0.1   # update image
kubectl rollout history deploy/api
kubectl rollout undo deploy/api --to-revision=2
kubectl scale deploy/api --replicas=5
</code></pre>
<p><strong>Deployment vs other workloads:</strong></p>
<table>
<thead><tr><th>Workload</th><th>Use for</th></tr></thead>
<tbody>
<tr><td>Deployment</td><td>Stateless web/API servers</td></tr>
<tr><td>StatefulSet</td><td>Stateful with stable identity (Mongo, Postgres, Kafka)</td></tr>
<tr><td>DaemonSet</td><td>One pod per node (log shipper, CNI agent)</td></tr>
<tr><td>Job / CronJob</td><td>Run-to-completion or scheduled batch work</td></tr>
</tbody>
</table>
<p><strong>Pair Deployments with:</strong> a <strong>Service</strong> (network endpoint), <strong>HPA</strong> (autoscale), <strong>PodDisruptionBudget</strong> (don&rsquo;t evict everything at once during node drains), <strong>NetworkPolicy</strong> (default-deny + allowlist), and <strong>readiness/liveness probes</strong> (rolling updates depend on them). For progressive delivery (canary, blue-green with metric analysis), wrap the Deployment with <strong>Argo Rollouts</strong> or <strong>Flagger</strong>.</p>'''

ANSWERS[41] = r'''<p>Securing Jenkins is non-trivial because Jenkins runs arbitrary code (build scripts) by design. The 2026 hardening checklist covers identity, authorization, network, supply chain, and operations.</p>
<p><strong>Identity:</strong></p>
<ul>
<li><strong>Disable anonymous access</strong> &mdash; Manage Jenkins &rarr; Security &rarr; Authorize: <em>Logged-in users can do anything</em> at minimum.</li>
<li><strong>SSO</strong> via the OpenID Connect Provider, SAML, or LDAP plugins. Tie Jenkins users to your IdP (Okta, Entra ID, Google Workspace) so offboarding works automatically.</li>
<li><strong>Disable the local user database</strong> once SSO is wired.</li>
<li><strong>MFA</strong> at the IdP level &mdash; preferably phishing-resistant (Passkeys/WebAuthn).</li>
</ul>
<p><strong>Authorization:</strong></p>
<ul>
<li><strong>Role Strategy plugin</strong> for project- and folder-scoped roles. Avoid the global &ldquo;admin or nothing&rdquo; matrix.</li>
<li><strong>Project-based Matrix Authorization</strong> for per-job permissions.</li>
<li><strong>Folder-level isolation</strong> &mdash; one folder per team with its own credentials.</li>
</ul>
<p><strong>Build security:</strong></p>
<ul>
<li><strong>Run agents on separate hosts</strong> from the controller; never run untrusted PR builds on the controller.</li>
<li><strong>Use ephemeral agents</strong> (Kubernetes, Docker, EC2 spot) so each build gets a clean environment.</li>
<li><strong>Sandbox Groovy</strong> &mdash; keep the Script Security plugin&rsquo;s sandbox enabled.</li>
<li><strong>Approve scripts</strong> only after security review; don&rsquo;t auto-approve.</li>
</ul>
<p><strong>Network &amp; transport:</strong></p>
<ul>
<li><strong>HTTPS only</strong>, terminate TLS at a reverse proxy (nginx, Caddy, ALB).</li>
<li><strong>Bind to private network</strong> &mdash; Jenkins behind a VPN or zero-trust gateway (Cloudflare Access, Tailscale, Pomerium); never internet-facing.</li>
<li><strong>CSRF protection</strong> on (default).</li>
<li><strong>Reverse proxy enforces auth</strong> as a second layer.</li>
</ul>
<p><strong>Operations:</strong></p>
<ul>
<li><strong>Pin and update plugins</strong> &mdash; CVEs come fast. Use <strong>Configuration as Code (JCasC)</strong> + <code>plugins.txt</code> so reinstalls are reproducible.</li>
<li><strong>Backups</strong> of <code>$JENKINS_HOME</code> with off-site immutable storage; test-restore quarterly.</li>
<li><strong>Audit logging</strong> via the Audit Trail plugin shipped to a SIEM.</li>
<li><strong>Secrets in Vault/Doppler</strong> via the HashiCorp Vault plugin, not the built-in credentials store for production secrets.</li>
</ul>
<p><strong>Honest take:</strong> if your team is small, the security overhead of running Jenkins safely often exceeds the value &mdash; switch to GitHub Actions / GitLab CI / Buildkite, which inherit your IdP and SSO automatically.</p>'''

ANSWERS[42] = r'''<p>A Docker <strong>volume</strong> is persistent storage that lives outside the container&rsquo;s writable layer, so data survives container restarts and removals. There are three storage modes:</p>
<table>
<thead><tr><th>Type</th><th>Definition</th><th>When to use</th></tr></thead>
<tbody>
<tr><td><strong>Named volume</strong></td><td>Managed by Docker, stored under <code>/var/lib/docker/volumes/</code></td><td>Production data &mdash; databases, app state</td></tr>
<tr><td><strong>Bind mount</strong></td><td>A specific host path mapped into the container</td><td>Dev hot-reload, sharing source code</td></tr>
<tr><td><strong>tmpfs</strong></td><td>In-memory only, never written to disk</td><td>Sensitive secrets, scratch space</td></tr>
</tbody>
</table>
<p><strong>Examples:</strong></p>
<pre><code># Named volume
docker volume create mongo-data
docker run -d --name mongo \
  -v mongo-data:/data/db \
  mongo:7

# Bind mount for dev
docker run --rm -it \
  -v &quot;$PWD&quot;:/app -w /app \
  node:20 bash

# tmpfs for sensitive scratch space
docker run --tmpfs /run/secrets:rw,size=64m,mode=0700 myapp
</code></pre>
<p><strong>In Compose:</strong></p>
<pre><code>services:
  mongo:
    image: mongo:7
    volumes:
      - mongo-data:/data/db          # named
      - ./init:/docker-entrypoint-initdb.d:ro   # bind mount, read-only
volumes:
  mongo-data:
</code></pre>
<p><strong>Why it matters:</strong></p>
<ul>
<li><strong>Containers are ephemeral.</strong> Anything in the writable layer is lost on <code>docker rm</code>.</li>
<li><strong>Volumes survive restarts and image upgrades.</strong> Pull a new <code>mongo:7</code> image, re-create the container, data persists.</li>
<li><strong>Better performance</strong> than the writable layer or bind mounts (especially on macOS/Windows where bind mounts go through a VM).</li>
<li><strong>Volume drivers</strong> (NFS, AWS EFS, Azure Files, Cloudflare R2 via FUSE) let volumes back onto network storage.</li>
</ul>
<p><strong>Production reality:</strong> in Kubernetes you use <strong>PersistentVolumes</strong> + <strong>PersistentVolumeClaims</strong> backed by a CSI driver (EBS, GCE PD, Azure Disk, Longhorn, Ceph). For most stateful workloads at scale, prefer a managed service (Atlas for Mongo, RDS for Postgres) over self-managed volumes &mdash; backups, replication, and PITR come included.</p>'''

ANSWERS[43] = r'''<p>GitHub Actions runs CI/CD workflows defined as YAML in <code>.github/workflows/</code>. Each workflow is a graph of jobs; each job is a sequence of steps; each step is either a shell command or a reusable action. Triggers include pushes, PRs, schedules, manual dispatch, repository events, and webhooks.</p>
<p><strong>Anatomy of a typical pipeline:</strong></p>
<pre><code># .github/workflows/ci-cd.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: 20

permissions:
  contents: read
  id-token: write          # OIDC for cloud auth

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongo:
        image: mongo:7
        ports: ['27017:27017']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ env.NODE_VERSION }}, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v4

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production       # protection rules + env secrets
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gh-deploy
          aws-region: us-east-1
      - run: aws ecs update-service --cluster prod --service api \
            --force-new-deployment
</code></pre>
<p><strong>Capabilities to know (2026):</strong></p>
<ul>
<li><strong>Reusable workflows</strong> (<code>uses: org/.github/.../ci.yml</code>) and <strong>composite actions</strong> for sharing across repos.</li>
<li><strong>Matrix builds</strong> for cross-platform/cross-version testing.</li>
<li><strong>Self-hosted runners</strong> &mdash; run jobs on your own infra (or with GHE-hosted runners), often via <strong>actions-runner-controller</strong> on Kubernetes.</li>
<li><strong>OIDC</strong> for keyless cloud auth &mdash; no AWS access keys in secrets.</li>
<li><strong>Concurrency</strong> for canceling redundant runs (<code>concurrency: { group: ${{ github.ref }}, cancel-in-progress: true }</code>).</li>
<li><strong>Environments</strong> with required reviewers + deployment branch policies.</li>
<li><strong>Artifact attestations</strong> + <strong>cosign signing</strong> built-in for supply-chain integrity.</li>
</ul>
<p>For agentic workflows, <strong>Claude Code Action</strong> can run code review or auto-fix on PRs. Pair Actions with <strong>Argo CD</strong> or <strong>Flux</strong> for GitOps so the cluster is the source of truth, not the CI.</p>'''

ANSWERS[44] = r'''<p>A Jenkins <strong>agent</strong> (formerly &ldquo;slave&rdquo; &mdash; deprecated terminology) is a worker node that executes builds on behalf of the Jenkins controller. The <strong>controller</strong> handles the UI, scheduling, and metadata; agents do the actual work. Almost any production Jenkins runs the controller separately and one or more agents.</p>
<p><strong>Why agents:</strong></p>
<ul>
<li><strong>Isolation</strong> &mdash; untrusted PR builds don&rsquo;t run on the controller.</li>
<li><strong>Capacity</strong> &mdash; horizontal scale across many machines.</li>
<li><strong>Heterogeneity</strong> &mdash; different agents for Linux, Windows, macOS, ARM, GPU jobs.</li>
<li><strong>Ephemeral environments</strong> &mdash; spin up a fresh agent per build, throw it away.</li>
</ul>
<p><strong>Agent types:</strong></p>
<table>
<thead><tr><th>Type</th><th>How it&rsquo;s provisioned</th></tr></thead>
<tbody>
<tr><td>Static / permanent</td><td>VMs you maintain; connect via SSH or JNLP</td></tr>
<tr><td>Docker</td><td>Each build runs in a fresh container; uses Docker plugin</td></tr>
<tr><td>Kubernetes</td><td>Each build is a Pod; uses Kubernetes plugin (most common 2026)</td></tr>
<tr><td>EC2 / Cloud</td><td>EC2 plugin spins up spot instances on demand</td></tr>
</tbody>
</table>
<p><strong>Pipeline example pinning to a Kubernetes agent:</strong></p>
<pre><code>pipeline {
  agent {
    kubernetes {
      yaml &#39;&#39;&#39;
        spec:
          containers:
            - name: node
              image: node:20-alpine
              command: ['cat']
              tty: true
            - name: docker
              image: docker:24
              command: ['cat']
              tty: true
              volumeMounts:
                - { name: dind, mountPath: /var/run }
            - name: dind
              image: docker:24-dind
              securityContext: { privileged: true }
          volumes:
            - { name: dind, emptyDir: {} }
      &#39;&#39;&#39;
    }
  }
  stages {
    stage('Build') {
      steps {
        container('node') { sh 'npm ci &amp;&amp; npm test' }
        container('docker') { sh 'docker build -t myapp .' }
      }
    }
  }
}
</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
<li><strong>Don&rsquo;t run builds on the controller</strong> &mdash; configure 0 executors there.</li>
<li><strong>Ephemeral agents</strong> &mdash; clean state, no caching landmines, smaller blast radius for compromised builds.</li>
<li><strong>Labels</strong> &mdash; tag agents (<code>linux-arm64</code>, <code>gpu</code>, <code>signed-release</code>) and pin jobs with <code>agent { label 'linux-arm64' }</code>.</li>
<li><strong>Pre-built agent images</strong> with required toolchains baked in &mdash; reduces per-build setup time.</li>
<li><strong>Capacity-based autoscaling</strong> &mdash; the Kubernetes plugin scales Pods on demand; the EC2 plugin scales VMs.</li>
</ul>
<p>Among modern alternatives, <strong>GitHub Actions self-hosted runners</strong> via <em>actions-runner-controller</em> on Kubernetes give you the same model with a cleaner UX.</p>'''

ANSWERS[45] = r'''<p>A Kubernetes <strong>namespace</strong> is a logical partition of cluster resources &mdash; pods, services, configmaps, secrets are scoped within it. Namespaces give you isolation, quota, and RBAC boundaries without needing separate clusters.</p>
<p><strong>Create one:</strong></p>
<pre><code># Imperative
kubectl create namespace prod

# Declarative (preferred &mdash; checks into Git)
cat &lt;&lt;EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    env: production
    pod-security.kubernetes.io/enforce: restricted
EOF
</code></pre>
<p><strong>Use it:</strong></p>
<pre><code>kubectl get pods -n prod
kubectl config set-context --current --namespace=prod   # default for session
kubectl apply -f deployment.yaml -n prod
</code></pre>
<p><strong>What namespaces give you:</strong></p>
<ul>
<li><strong>Resource isolation</strong> &mdash; same names can repeat across namespaces (<code>api</code> in <code>dev</code> and <code>prod</code>).</li>
<li><strong>RBAC scope</strong> &mdash; grant a team admin in <code>team-a</code> only.</li>
<li><strong>ResourceQuota</strong> &mdash; cap CPU/memory/storage per namespace.</li>
<li><strong>LimitRange</strong> &mdash; default request/limit per pod.</li>
<li><strong>NetworkPolicy</strong> scope &mdash; deny by default within and across namespaces.</li>
<li><strong>Pod Security Standards</strong> &mdash; enforce <em>restricted</em> via the namespace label.</li>
</ul>
<p><strong>Common partitioning patterns:</strong></p>
<ul>
<li>One namespace per <strong>environment</strong>: <code>dev</code>, <code>staging</code>, <code>prod</code>.</li>
<li>One namespace per <strong>team</strong> or <strong>service</strong>: <code>checkout</code>, <code>billing</code>, <code>search</code>.</li>
<li>System workloads in <code>kube-system</code>, observability in <code>monitoring</code>, ingress in <code>ingress-nginx</code>.</li>
</ul>
<p><strong>Honest 2026 advice:</strong> namespaces are a soft boundary, not a hard one &mdash; a privileged pod or escape can still affect other namespaces. For real multi-tenancy use <strong>vCluster</strong> (virtual clusters, very popular 2026), <strong>Capsule</strong>, or separate clusters managed via Argo CD ApplicationSets / Cluster API. Don&rsquo;t mix prod and untrusted workloads in one cluster regardless of namespace.</p>'''

ANSWERS[46] = r'''<p>Docker <strong>networks</strong> connect containers to each other and to the outside world. Every container attaches to one or more networks, and Docker handles IP allocation, DNS-based service discovery, and packet forwarding behind the scenes.</p>
<p><strong>Network drivers (built-in):</strong></p>
<table>
<thead><tr><th>Driver</th><th>Use case</th></tr></thead>
<tbody>
<tr><td><strong>bridge</strong> (default)</td><td>Containers on a single host; the default bridge has limited DNS, custom bridges have full service discovery</td></tr>
<tr><td><strong>host</strong></td><td>Skip Docker&rsquo;s network stack; container shares host&rsquo;s network namespace. Fastest, least isolated.</td></tr>
<tr><td><strong>none</strong></td><td>No network. For isolated batch jobs.</td></tr>
<tr><td><strong>overlay</strong></td><td>Multi-host networking for Docker Swarm.</td></tr>
<tr><td><strong>macvlan</strong></td><td>Container gets a MAC and IP on the physical network. Used for legacy integration.</td></tr>
</tbody>
</table>
<p><strong>Practical example:</strong></p>
<pre><code># Custom bridge with auto DNS between containers
docker network create app-net

docker run -d --name mongo --network app-net mongo:7
docker run -d --name api   --network app-net \
  -e MONGO_URL=mongodb://mongo:27017/app \
  acme/api:1.0.0

# Inspect
docker network ls
docker network inspect app-net
</code></pre>
<p>The API container reaches Mongo via the hostname <code>mongo</code> &mdash; Docker&rsquo;s embedded DNS resolves container names on the same custom bridge.</p>
<p><strong>In Compose</strong> every service automatically joins a default network and is reachable by service name:</p>
<pre><code>services:
  mongo: { image: mongo:7 }
  api:   { build: ./server, environment: { MONGO_URL: mongodb://mongo:27017/app } }
</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
<li><strong>Always use a custom bridge</strong>, not the default. Custom bridges have automatic DNS; the default doesn&rsquo;t.</li>
<li><strong>Avoid <code>--network host</code></strong> in production unless you really need raw performance &mdash; you lose isolation and port mapping.</li>
<li><strong>Don&rsquo;t expose ports unnecessarily</strong> &mdash; <code>EXPOSE</code> is metadata; <code>-p</code> publishes to the host.</li>
<li><strong>For multi-host networking, prefer Kubernetes</strong> with a CNI (Cilium, Calico) over Docker Swarm overlays in 2026.</li>
</ul>
<p>In Kubernetes, networks are abstracted away &mdash; pods get IPs from the CNI and reach Services by DNS (<code>svc.namespace.svc.cluster.local</code>). For policy enforcement use <strong>NetworkPolicy</strong> + Cilium / Calico for default-deny + explicit allowlists.</p>'''

ANSWERS[47] = r'''<p>Deploying to Kubernetes from GitHub Actions has two patterns: <strong>direct push</strong> from CI (simple) and <strong>GitOps pull</strong> from the cluster (recommended in 2026).</p>
<p><strong>Pattern A &mdash; Direct push (smaller teams):</strong></p>
<pre><code>name: Deploy to K8s
on:
  push: { branches: [main] }

permissions:
  contents: read
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      # OIDC =&gt; AWS =&gt; EKS, no static creds
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gh-deploy
          aws-region: us-east-1
      - run: aws eks update-kubeconfig --name prod

      - name: Set image
        run: |
          kubectl set image deploy/api api=ghcr.io/acme/api:${{ github.sha }} -n prod
          kubectl rollout status deploy/api -n prod --timeout=5m
</code></pre>
<p>Or with Helm:</p>
<pre><code>      - uses: azure/setup-helm@v4
      - run: |
          helm upgrade --install api ./charts/api \
            -n prod -f values.prod.yaml \
            --set image.tag=${{ github.sha }} \
            --wait --timeout 5m
</code></pre>
<p><strong>Pattern B &mdash; GitOps with Argo CD / Flux (recommended):</strong></p>
<p>CI never holds cluster credentials. Instead, the workflow updates a manifest repo, and an in-cluster Argo CD or Flux controller reconciles to whatever&rsquo;s in Git.</p>
<pre><code>      - uses: actions/checkout@v4
        with:
          repository: acme/k8s-manifests
          token: ${{ secrets.MANIFESTS_PUSH_TOKEN }}
      - run: |
          yq -i '.spec.template.spec.containers[0].image=&quot;ghcr.io/acme/api:${{ github.sha }}&quot;' \
            apps/api/deployment.yaml
          git config user.email ci@acme.com &amp;&amp; git config user.name ci
          git add . &amp;&amp; git commit -m &quot;chore(api): deploy ${{ github.sha }}&quot;
          git push
</code></pre>
<p>Argo CD watches the manifest repo, detects the change, and rolls out within seconds &mdash; with an audit log, sync diff UI, and one-click rollback.</p>
<p><strong>Why GitOps wins (2026):</strong></p>
<ul>
<li>Cluster credentials never leave the cluster.</li>
<li>Git is the source of truth &mdash; rollback = revert.</li>
<li>Drift detection: Argo CD flags out-of-band changes.</li>
<li>Multi-cluster fans out via Argo CD ApplicationSets.</li>
<li>Pairs with <strong>Argo Rollouts</strong> for progressive delivery (canary, blue-green) without changing Deployments.</li>
</ul>
<p>For Kustomize-only setups, <strong>Flux</strong> is the lighter alternative. Both Argo and Flux are CNCF graduated and stable.</p>'''

ANSWERS[48] = r'''<p><strong>Blue Ocean</strong> is a redesigned UI for Jenkins focused on visualizing pipelines: a graph of stages, parallel branches, real-time logs per step, PR overview, and a guided pipeline editor. It was the &ldquo;modern face&rdquo; of Jenkins introduced around 2017.</p>
<p><strong>What it gives you:</strong></p>
<ul>
<li><strong>Pipeline visualization</strong> &mdash; the stages-and-steps graph that you see referenced in screenshots; much easier to read than the classic console log.</li>
<li><strong>Per-step logs</strong> &mdash; click a stage, see exactly what failed without scrolling 50,000 lines.</li>
<li><strong>Multibranch view</strong> &mdash; PRs and branches at a glance with build status.</li>
<li><strong>Visual pipeline editor</strong> &mdash; build a Jenkinsfile via drag-and-drop (rarely used in practice).</li>
<li><strong>Better mobile experience</strong>, dark mode.</li>
</ul>
<p><strong>How to get it:</strong> Manage Jenkins &rarr; Plugins &rarr; install <em>Blue Ocean</em>, then <code>https://jenkins/blue/</code>.</p>
<p><strong>Honest 2026 status:</strong> Blue Ocean is in <strong>maintenance mode</strong> at CloudBees. The Jenkins project itself is investing in a separate UI redesign (the &ldquo;Modern UI&rdquo; effort). New installs in 2026 should weigh:</p>
<ul>
<li>Use Blue Ocean knowing it&rsquo;s frozen in feature development but still works.</li>
<li>Track the new modern Jenkins UI initiative.</li>
<li>Or, more realistically, evaluate moving the workload to <strong>GitHub Actions</strong> (better visualization out of the box), <strong>Buildkite</strong> (best-in-class pipeline UI), <strong>GitLab CI</strong>, or <strong>CircleCI</strong> &mdash; all of which have polished visual pipelines without a separate plugin.</li>
</ul>
<p>Blue Ocean is still a quick UX win for legacy Jenkins shops, but most teams in 2026 use it as a stepping stone before migrating CI/CD to a SaaS or Argo Workflows-style platform.</p>'''

ANSWERS[49] = r'''<p>A multi-container app with Docker Compose declares each service in <code>compose.yaml</code> with build context, environment, ports, volumes, and dependencies. <code>docker compose up</code> brings the whole stack up; <code>down</code> tears it down. It&rsquo;s the universal pattern for local development of MERN/Next/microservices apps.</p>
<p><strong>Full MERN example:</strong></p>
<pre><code># compose.yaml
services:
  mongo:
    image: mongo:7
    restart: unless-stopped
    volumes: [mongo-data:/data/db]
    healthcheck:
      test: ['CMD', 'mongosh', '--eval', 'db.runCommand({ping:1})']
      interval: 10s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 10s

  api:
    build:
      context: ./server
      target: dev
    environment:
      NODE_ENV: development
      MONGO_URL: mongodb://mongo:27017/app
      REDIS_URL: redis://redis:6379
    ports: ['4000:4000']
    depends_on:
      mongo: { condition: service_healthy }
      redis: { condition: service_healthy }
    develop:
      watch:
        - { path: ./server/src,  action: sync, target: /app/src }
        - { path: ./server/package.json, action: rebuild }

  web:
    build:
      context: ./client
      target: dev
    environment:
      VITE_API_URL: http://localhost:4000
    ports: ['5173:5173']
    depends_on: [api]
    develop:
      watch:
        - { path: ./client/src, action: sync, target: /app/src }

  mailhog:               # local SMTP catcher
    image: mailhog/mailhog
    ports: ['1025:1025', '8025:8025']

volumes:
  mongo-data:
</code></pre>
<p><strong>Run it:</strong></p>
<pre><code>docker compose up -d              # start in background
docker compose watch              # hot-reload on file changes
docker compose logs -f api        # tail one service
docker compose exec api sh        # shell into a container
docker compose down -v            # stop + remove volumes (clean slate)
</code></pre>
<p><strong>Production-style patterns:</strong></p>
<ul>
<li><strong>Multi-stage Dockerfiles</strong> with <code>target: dev</code> for hot-reload and <code>target: prod</code> for slim images.</li>
<li><strong>Profiles</strong> &mdash; <code>profiles: [debug]</code> on optional services; opt in via <code>--profile debug</code>.</li>
<li><strong>Compose overrides</strong> &mdash; <code>compose.yaml</code> + <code>compose.override.yaml</code> for dev specifics; <code>-f compose.yaml -f compose.prod.yaml</code> for prod.</li>
<li><strong>Healthchecks + <code>depends_on: condition: service_healthy</code></strong> so dependent services only start once their deps are ready.</li>
<li><strong>Watch mode</strong> (Compose 2.22+) replaces nodemon-mounted volumes &mdash; faster, more reliable.</li>
</ul>
<p><strong>For production at scale</strong>, move to Kubernetes (use <code>compose-on-kubernetes</code> or rewrite as Helm charts) or AWS ECS/Fargate (which can ingest a Compose file via <code>docker compose convert</code>).</p>'''

ANSWERS[50] = r'''<p>A <strong>Jenkinsfile</strong> is a text file (Groovy) checked into a repository that defines the entire build pipeline as code. It&rsquo;s the canonical way to write Jenkins pipelines &mdash; portable, reviewable in PRs, and reproducible.</p>
<p><strong>Why it exists:</strong></p>
<ul>
<li><strong>Pipeline as code</strong> &mdash; CI lives next to the source, versioned with it.</li>
<li><strong>Code review</strong> &mdash; pipeline changes go through PR review like any other code.</li>
<li><strong>Branch-aware</strong> &mdash; each branch can have its own pipeline (Multibranch jobs auto-discover them).</li>
<li><strong>Reusable</strong> &mdash; shared libraries factor common steps across projects.</li>
<li><strong>Disaster recovery</strong> &mdash; if Jenkins dies, you reinstall and re-import; pipelines come back from Git.</li>
</ul>
<p><strong>Two syntaxes:</strong></p>
<table>
<thead><tr><th>Style</th><th>When to use</th></tr></thead>
<tbody>
<tr><td><strong>Declarative</strong></td><td>Standard. Structured, easier to read, supports validation. Default for 2026.</td></tr>
<tr><td><strong>Scripted</strong></td><td>Pure Groovy. More flexible but harder to maintain. Use for advanced cases or shared libraries.</td></tr>
</tbody>
</table>
<p><strong>Declarative example:</strong></p>
<pre><code>// Jenkinsfile
pipeline {
  agent { label 'linux' }
  options {
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }
  environment {
    REGISTRY = 'ghcr.io/acme'
  }
  stages {
    stage('Build') {
      steps {
        sh 'npm ci &amp;&amp; npm run build'
      }
    }
    stage('Test') {
      parallel {
        stage('Unit')        { steps { sh 'npm test' } }
        stage('Lint')        { steps { sh 'npm run lint' } }
        stage('Type check')  { steps { sh 'npm run typecheck' } }
      }
    }
    stage('Docker') {
      when { branch 'main' }
      steps {
        sh &quot;docker build -t $REGISTRY/api:${env.GIT_COMMIT} .&quot;
        sh &quot;docker push $REGISTRY/api:${env.GIT_COMMIT}&quot;
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        input 'Promote to production?'
        sh './deploy.sh prod ${env.GIT_COMMIT}'
      }
    }
  }
  post {
    always  { junit 'reports/*.xml' }
    failure { slackSend channel: '#deploys', message: ":x: $JOB_NAME #$BUILD_NUMBER failed" }
  }
}
</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
<li><strong>Keep <code>Jenkinsfile</code> short</strong> &mdash; push complex logic to shell scripts in the repo or to a <strong>Jenkins shared library</strong>.</li>
<li><strong>Pin tool versions</strong> with <code>tools { nodejs '20'; maven '3.9' }</code>.</li>
<li><strong>Parallelize</strong> independent stages (lint/typecheck/unit tests).</li>
<li><strong>Always set timeouts</strong>; Jenkins jobs that hang chew up agent capacity.</li>
<li><strong>Use the <code>options</code> block</strong> for build retention, concurrency control, and skip-on-empty.</li>
</ul>
<p>Equivalent in modern terms: a <code>.github/workflows/*.yml</code> file in GitHub Actions or <code>.gitlab-ci.yml</code> in GitLab. The <strong>pipeline-as-code</strong> idea is now universal &mdash; the Jenkinsfile was its archetype.</p>'''

ANSWERS[51] = r'''<p>A <strong>Docker Compose file</strong> in CI/CD usually plays one of three roles: spinning up service dependencies for tests, building multi-container artifacts, or running end-to-end test stacks. Each maps cleanly to a CI step.</p>
<p><strong>Pattern 1 &mdash; integration test dependencies:</strong></p>
<pre><code># .github/workflows/ci.yml
- run: docker compose -f compose.test.yaml up -d
- run: npm ci
- run: npm test                # tests connect to mongo:27017, redis:6379
- if: always()
  run: docker compose -f compose.test.yaml down -v
</code></pre>
<p>The <code>compose.test.yaml</code> defines just dependencies (Mongo, Redis, MailHog, LocalStack for AWS) that tests need.</p>
<p><strong>Pattern 2 &mdash; service containers (GitHub Actions native):</strong></p>
<pre><code>jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongo: { image: mongo:7, ports: ['27017:27017'] }
      redis: { image: redis:7, ports: ['6379:6379'] }
    steps:
      - uses: actions/checkout@v4
      - run: npm ci &amp;&amp; npm test
</code></pre>
<p>For CI-native service containers (GitHub Actions <code>services:</code>, GitLab <code>services:</code>) prefer this over Compose &mdash; less to manage and faster startup.</p>
<p><strong>Pattern 3 &mdash; full E2E stack:</strong></p>
<pre><code>- run: docker compose -f compose.yaml -f compose.e2e.yaml up -d --wait
- run: npx playwright test
- if: always()
  run: docker compose logs &gt; e2e-logs.txt
- if: always()
  uses: actions/upload-artifact@v4
  with: { name: e2e-logs, path: e2e-logs.txt }
</code></pre>
<p>Bring the whole MERN stack up, run Playwright/Cypress against the live web service, capture logs on failure.</p>
<p><strong>Pattern 4 &mdash; build &amp; push composed images:</strong></p>
<pre><code>- run: docker compose -f compose.yaml -f compose.prod.yaml build
- run: docker compose push           # pushes all services
</code></pre>
<p><strong>Best practices in CI:</strong></p>
<ul>
<li><strong><code>--wait</code> flag</strong> (Compose 2.x) blocks until healthchecks pass; pair with <code>healthcheck:</code> blocks per service.</li>
<li><strong>Use <code>-d</code> in CI</strong> + tail logs separately; foreground Compose hangs runners.</li>
<li><strong>Always teardown</strong> with <code>down -v</code> in an <code>if: always()</code> step so disk fills don&rsquo;t accumulate on self-hosted runners.</li>
<li><strong>Fail fast on health</strong> &mdash; if a dependency doesn&rsquo;t come up, fail before running tests.</li>
<li><strong>Pin image tags</strong> (<code>mongo:7.0.5</code>, not <code>mongo:latest</code>) for reproducibility.</li>
<li><strong>Cache build layers</strong> via BuildKit + GHA cache for fast rebuilds.</li>
</ul>
<p><strong>Honest 2026 advice:</strong> in Kubernetes-native CI (Tekton, Argo Workflows, Dagger), Compose is rare &mdash; sidecars, jobs, and ephemeral pods do the same thing. But for GitHub Actions / GitLab / Jenkins, Compose remains the easiest way to spin up multi-service test fixtures.</p>'''

ANSWERS[52] = r'''<p>Kubernetes deployments keep <strong>revision history</strong> for rolling updates, so rolling back is a one-liner.</p>
<pre><code># See history
kubectl rollout history deploy/api -n prod

# Roll back to the immediately previous revision
kubectl rollout undo deploy/api -n prod

# Roll back to a specific revision
kubectl rollout undo deploy/api -n prod --to-revision=4

# Watch the rollback progress
kubectl rollout status deploy/api -n prod
</code></pre>
<p><strong>What happens internally:</strong> the Deployment controller spins up a new ReplicaSet matching the chosen revision&rsquo;s pod template, scales it up while scaling the current ReplicaSet down (respecting <code>maxSurge</code>/<code>maxUnavailable</code>), and waits for readiness probes.</p>
<p><strong>Configure history depth:</strong></p>
<pre><code>spec:
  revisionHistoryLimit: 10   # default
</code></pre>
<p><strong>Rollback options by tooling:</strong></p>
<table>
<thead><tr><th>Tool</th><th>Rollback path</th></tr></thead>
<tbody>
<tr><td><strong>kubectl</strong></td><td><code>kubectl rollout undo</code> (above)</td></tr>
<tr><td><strong>Helm</strong></td><td><code>helm rollback api 5 -n prod</code> &mdash; rolls back to release revision 5</td></tr>
<tr><td><strong>Argo CD</strong></td><td>One-click rollback in the UI, or <code>argocd app rollback api</code></td></tr>
<tr><td><strong>Argo Rollouts</strong></td><td><code>kubectl argo rollouts undo api</code> &mdash; preserves canary state</td></tr>
<tr><td><strong>GitOps</strong> (Argo CD/Flux)</td><td><code>git revert</code> the offending commit, push; the controller reconciles</td></tr>
</tbody>
</table>
<p><strong>Limitations to know:</strong></p>
<ul>
<li><strong>Rollback only restores the pod template</strong> &mdash; not Services, ConfigMaps, Secrets, or PVCs. Those follow their own lifecycle.</li>
<li><strong>StatefulSet rollbacks are tricky</strong> when schemas change &mdash; rollback the app, not the data. Use schema versioning for forward-compatible changes (expand/migrate/contract pattern).</li>
<li><strong>Database migrations don&rsquo;t auto-revert</strong>. Always design migrations to be backward-compatible so app rollback doesn&rsquo;t leave data orphaned.</li>
</ul>
<p><strong>2026 best practice:</strong> use <strong>progressive delivery</strong> with Argo Rollouts or Flagger so a bad release auto-aborts and rolls back based on metrics (error rate, latency) before it reaches 100% of traffic. Combined with <strong>feature flags</strong> (LaunchDarkly, Statsig, GrowthBook), rollback often means flipping a flag in seconds &mdash; without redeploying anything.</p>'''

ANSWERS[53] = r'''<p>A <strong>webhook</strong> is an HTTP POST GitHub sends to a URL you provide whenever a configured event happens &mdash; pushes, PRs, releases, comments, deployments. Webhooks are how external CI servers (Jenkins, custom systems) get notified of events without polling.</p>
<p><strong>Setting one up:</strong></p>
<ul>
<li>Repository &rarr; Settings &rarr; Webhooks &rarr; Add webhook.</li>
<li><strong>Payload URL</strong> &mdash; e.g. <code>https://jenkins.example.com/github-webhook/</code>.</li>
<li><strong>Content type</strong> &mdash; <code>application/json</code>.</li>
<li><strong>Secret</strong> &mdash; a strong random token used to sign payloads (HMAC-SHA256). <em>Always set this.</em></li>
<li><strong>Events</strong> &mdash; either &ldquo;Just the push event&rdquo; or pick specific events (PRs, deployments, etc.).</li>
<li><strong>Active</strong> &mdash; tick to enable.</li>
</ul>
<p><strong>GitHub signs each payload</strong> with the secret in the <code>X-Hub-Signature-256</code> header. Always verify before trusting:</p>
<pre><code>// Express receiver
import crypto from 'node:crypto'

app.post('/webhook', express.json({
  verify: (req, _res, buf) =&gt; { req.rawBody = buf }
}), (req, res) =&gt; {
  const sig = req.header('x-hub-signature-256') || ''
  const expected = 'sha256=' + crypto
    .createHmac('sha256', process.env.GH_WEBHOOK_SECRET)
    .update(req.rawBody)
    .digest('hex')
  if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) {
    return res.status(401).send('bad signature')
  }
  const event = req.header('x-github-event')   // e.g. 'push', 'pull_request'
  // dispatch on event...
  res.sendStatus(202)
})
</code></pre>
<p><strong>What you typically do with the webhook:</strong></p>
<ul>
<li><strong>Trigger CI</strong> &mdash; Jenkins, Buildkite, custom workflow engines.</li>
<li><strong>Update an issue tracker</strong> &mdash; Linear, Jira, Asana automation.</li>
<li><strong>Notify chat</strong> &mdash; Slack, Discord, Microsoft Teams (use the dedicated apps where possible).</li>
<li><strong>Update an internal dashboard</strong> &mdash; deployment tracker, on-call escalations.</li>
<li><strong>Trigger ChatOps</strong> &mdash; auto-comment on PRs, run Claude Code review.</li>
</ul>
<p><strong>Best practices (2026):</strong></p>
<ul>
<li><strong>Always verify signatures</strong>; an unauthenticated webhook receiver is a public RCE.</li>
<li><strong>Be idempotent</strong> &mdash; GitHub retries failed deliveries; the same event may arrive twice.</li>
<li><strong>Acknowledge fast</strong> (under 10s) &mdash; queue work asynchronously (BullMQ, SQS, Inngest, Trigger.dev) and return 202 immediately.</li>
<li><strong>Replay on failure</strong> &mdash; the webhooks UI lets you redeliver any event manually.</li>
<li><strong>Use GitHub Apps over PATs</strong> for any webhook flow that involves API callbacks &mdash; better security and rate limits.</li>
<li><strong>Tunneling for local dev</strong> via <code>ngrok</code>, <code>cloudflared tunnel</code>, or <code>smee.io</code> &mdash; no need to deploy to test webhook handlers.</li>
</ul>'''

ANSWERS[54] = r'''<p>A Jenkins <strong>node</strong> is a machine that participates in the Jenkins farm. The <strong>controller</strong> is one node (sometimes called the &ldquo;master&rdquo; in older docs &mdash; deprecated terminology); <strong>agents</strong> are the worker nodes. So &ldquo;node&rdquo; is the umbrella term for both.</p>
<p><strong>Anatomy:</strong></p>
<table>
<thead><tr><th>Node type</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Controller</td><td>Hosts UI, schedules builds, stores config + history, manages plugins. Should never run builds itself in production.</td></tr>
<tr><td>Agent (static)</td><td>Persistent worker (VM, bare metal). Connects via SSH or JNLP.</td></tr>
<tr><td>Agent (cloud)</td><td>Provisioned on demand (Kubernetes pod, Docker container, EC2 spot). Lives only for the build.</td></tr>
</tbody>
</table>
<p><strong>How nodes connect:</strong></p>
<ul>
<li><strong>SSH inbound</strong> &mdash; controller SSH&rsquo;s into the agent host. Simplest for static agents.</li>
<li><strong>JNLP inbound</strong> (TCP/JNLP4) &mdash; agent runs a small JAR that calls home to the controller. Used when the controller can&rsquo;t reach the agent (e.g. behind NAT/firewall, or in Kubernetes).</li>
<li><strong>WebSocket inbound</strong> &mdash; modern variant of JNLP using HTTPS only; firewall-friendly.</li>
</ul>
<p><strong>Defining nodes:</strong></p>
<ul>
<li>Manage Jenkins &rarr; Nodes &rarr; New Node.</li>
<li>Set <strong>labels</strong> (e.g. <code>linux</code>, <code>arm64</code>, <code>gpu</code>) so jobs can target capabilities: <code>agent { label 'linux &amp;&amp; arm64' }</code>.</li>
<li>Configure <strong># of executors</strong> (parallel builds per node), <strong>remote root</strong> (working dir on the agent), and <strong>usage</strong> (Use this node as much as possible / Only build jobs with matching label expressions).</li>
</ul>
<p><strong>Cloud nodes (recommended for 2026):</strong></p>
<pre><code>// Kubernetes plugin
podTemplate(label: 'k8s', containers: [
  containerTemplate(name: 'node', image: 'node:20-alpine', ttyEnabled: true, command: 'cat'),
  containerTemplate(name: 'docker', image: 'docker:24', command: 'cat', ttyEnabled: true)
]) {
  node('k8s') {
    container('node') { sh 'npm ci &amp;&amp; npm test' }
    container('docker') { sh 'docker build -t myapp .' }
  }
}
</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
<li><strong>Zero executors on the controller</strong> &mdash; isolation and capacity.</li>
<li><strong>Ephemeral cloud agents</strong> &mdash; clean state, cost-efficient, scales to zero.</li>
<li><strong>Label strategy</strong> &mdash; capability labels (<code>docker</code>, <code>gpu</code>, <code>signed-release</code>), not arbitrary names.</li>
<li><strong>Sized for parallel</strong> &mdash; executors per node = vCPUs (or fewer for IO-bound jobs).</li>
<li><strong>Pre-built images</strong> with toolchains baked in; per-build Apt/Brew installs are slow and flaky.</li>
<li><strong>Run agents as non-root</strong> with restricted IAM/RBAC scope.</li>
</ul>
<p>Modern equivalent: GitHub Actions runners and runner groups, GitLab runners with tags, Buildkite agents with queues. The terminology differs but the model is identical.</p>'''

ANSWERS[55] = r'''<p>A <strong>ConfigMap</strong> stores non-sensitive configuration data &mdash; environment variables, config files, command-line flags &mdash; that pods consume at runtime. ConfigMaps decouple config from container images, so the same image runs in dev/staging/prod with different settings.</p>
<p><strong>Three ways to consume a ConfigMap:</strong></p>
<p><strong>1. As environment variables:</strong></p>
<pre><code>apiVersion: v1
kind: ConfigMap
metadata: { name: api-config }
data:
  LOG_LEVEL: info
  FEATURE_FLAG_X: 'true'
  CACHE_TTL_SECONDS: '300'
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  template:
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          envFrom:
            - configMapRef: { name: api-config }
          # or pick individual keys:
          # env:
          #   - name: LOG_LEVEL
          #     valueFrom: { configMapKeyRef: { name: api-config, key: LOG_LEVEL } }
</code></pre>
<p><strong>2. As mounted files:</strong></p>
<pre><code>apiVersion: v1
kind: ConfigMap
metadata: { name: nginx-config }
data:
  nginx.conf: |
    server {
      listen 80;
      location / { proxy_pass http://api:4000; }
    }
---
spec:
  template:
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          volumeMounts:
            - { name: config, mountPath: /etc/nginx/conf.d, readOnly: true }
      volumes:
        - name: config
          configMap: { name: nginx-config }
</code></pre>
<p><strong>3. Via subPath</strong> for a single file alongside other files in a directory.</p>
<p><strong>Updating ConfigMaps:</strong></p>
<ul>
<li><strong>Env-var consumers</strong> don&rsquo;t see updates without a pod restart. Trigger one with <code>kubectl rollout restart deploy/api</code> or use <code>stakater/Reloader</code> to auto-restart on change.</li>
<li><strong>Volume-mounted</strong> ConfigMaps update on disk within ~1 minute, but most apps need a SIGHUP or reload to pick up changes (nginx supports <code>nginx -s reload</code>).</li>
<li>Never reuse a ConfigMap name with mutated content silently &mdash; treat them like immutable releases (Helm + checksum annotation pattern, or generate uniquely named ConfigMaps via Kustomize&rsquo;s <code>configMapGenerator</code>).</li>
</ul>
<p><strong>ConfigMap vs Secret:</strong></p>
<ul>
<li>Both share the same API shape, but Secrets are base64-encoded (not encrypted by default!) and typically restricted via RBAC.</li>
<li>For real secrets use <strong>Secrets</strong> + <strong>External Secrets Operator</strong> (pulling from AWS Secrets Manager, Vault, Doppler, Infisical) and enable <strong>encryption at rest</strong> in etcd.</li>
<li>For non-sensitive config: ConfigMap.</li>
</ul>
<p><strong>2026 alternatives:</strong> <strong>Argo CD ApplicationSets</strong> + Helm/Kustomize for env-specific values, <strong>Cdk8s</strong> or <strong>Timoni</strong> for typed config in code.</p>'''

ANSWERS[56] = r'''<p>Building a Docker image in Jenkins uses the <strong>Docker Pipeline plugin</strong> (or just shell calls). The pattern: have Docker available on the agent, build, tag, push.</p>
<p><strong>Declarative pipeline example:</strong></p>
<pre><code>pipeline {
  agent any
  environment {
    REGISTRY = 'ghcr.io/acme'
    IMAGE    = 'api'
    TAG      = "${env.GIT_COMMIT.take(8)}"
  }
  stages {
    stage('Build') {
      steps {
        script {
          docker.withRegistry("https://${REGISTRY}", 'ghcr-credentials') {
            def img = docker.build("${REGISTRY}/${IMAGE}:${TAG}",
              "--cache-from ${REGISTRY}/${IMAGE}:cache --build-arg NODE_ENV=production .")
            img.push()
            if (env.BRANCH_NAME == 'main') img.push('latest')
          }
        }
      }
    }
  }
}
</code></pre>
<p><strong>Or pure shell (works on any agent that has Docker):</strong></p>
<pre><code>stage('Build &amp; push') {
  steps {
    withCredentials([usernamePassword(credentialsId: 'ghcr-credentials',
                                      usernameVariable: 'U', passwordVariable: 'P')]) {
      sh &#39;&#39;&#39;
        echo &quot;$P&quot; | docker login ghcr.io -u &quot;$U&quot; --password-stdin
        docker buildx build \
          --platform linux/amd64,linux/arm64 \
          --cache-from type=registry,ref=$REGISTRY/$IMAGE:cache \
          --cache-to   type=registry,ref=$REGISTRY/$IMAGE:cache,mode=max \
          -t $REGISTRY/$IMAGE:$GIT_COMMIT \
          --push .
      &#39;&#39;&#39;
    }
  }
}
</code></pre>
<p><strong>Where Docker comes from on the agent:</strong></p>
<table>
<thead><tr><th>Setup</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Docker daemon on the agent</td><td>Easiest. Add the Jenkins user to the <code>docker</code> group.</td></tr>
<tr><td>Docker-in-Docker (DinD)</td><td>Sidecar in K8s pod templates. Privileged. Common pattern.</td></tr>
<tr><td><strong>Kaniko</strong> / <strong>Buildah</strong></td><td>Daemonless image builds. Run rootless. Recommended for K8s.</td></tr>
<tr><td>BuildKit standalone</td><td>Daemonless via <code>buildctl</code>. Most efficient cache.</td></tr>
</tbody>
</table>
<p><strong>Best practices (2026):</strong></p>
<ul>
<li><strong>Multi-stage Dockerfiles</strong> + <strong>BuildKit cache</strong> (<code>cache-from</code>/<code>cache-to type=registry</code>) cut build times dramatically across CI runs.</li>
<li><strong>Non-privileged builds</strong> &mdash; prefer Kaniko or Buildah on K8s rather than DinD.</li>
<li><strong>Multi-arch</strong> via <code>buildx</code> + QEMU.</li>
<li><strong>Sign with cosign</strong>, generate SBOM and SLSA provenance.</li>
<li><strong>Pin tags by digest</strong> in production manifests; <code>:latest</code> is for convenience only.</li>
<li><strong>Scan the image</strong> (Trivy, Grype) and fail the build on critical CVEs.</li>
</ul>
<p>Note: most teams have moved this exact pipeline shape to <strong>GitHub Actions</strong> using <code>docker/build-push-action</code> &mdash; it&rsquo;s the same pattern, less setup, and OIDC for keyless registry auth.</p>'''

ANSWERS[57] = r'''<p>GitHub Actions <strong>secrets</strong> are encrypted, scoped key/value pairs that workflows reference via <code>${{ secrets.NAME }}</code>. They&rsquo;re injected at runtime, masked in logs, and never visible after creation. Three scopes:</p>
<table>
<thead><tr><th>Scope</th><th>Where</th><th>Use</th></tr></thead>
<tbody>
<tr><td>Repository</td><td>Repo &rarr; Settings &rarr; Secrets and variables &rarr; Actions</td><td>Workflow-specific keys</td></tr>
<tr><td>Environment</td><td>Repo &rarr; Settings &rarr; Environments &rarr; <em>name</em></td><td>Per-env (prod/staging) with required reviewers, branch policies, wait timers</td></tr>
<tr><td>Organization</td><td>Org &rarr; Settings &rarr; Secrets</td><td>Shared across selected repos (e.g. <code>NPM_TOKEN</code>, <code>DOCKERHUB_TOKEN</code>)</td></tr>
</tbody>
</table>
<p><strong>Reference in workflows:</strong></p>
<pre><code>jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production           # gates + env secrets
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          NPM_TOKEN:    ${{ secrets.NPM_TOKEN }}
        run: ./deploy.sh
</code></pre>
<p><strong>Variables (non-secret, visible) </strong> live alongside secrets and use <code>${{ vars.NAME }}</code>. Use them for environment names, region IDs, default branches &mdash; anything safe to display.</p>
<p><strong>Auto-provided secrets:</strong></p>
<ul>
<li><code>secrets.GITHUB_TOKEN</code> &mdash; ephemeral token scoped to the repo, valid for the workflow run. Use it for GHCR pushes, comments, releases. No setup needed.</li>
</ul>
<p><strong>Best practices (2026):</strong></p>
<ul>
<li><strong>Prefer OIDC</strong> for cloud auth (AWS, GCP, Azure, HashiCorp Vault) over long-lived access keys. <code>permissions: id-token: write</code> + provider action exchanges a short-lived JWT for cloud creds.</li>
<li><strong>Environment secrets &gt; repo secrets</strong> for production &mdash; required reviewers and branch policies are an extra control plane.</li>
<li><strong>Centralize via Doppler / Infisical / Vault</strong> when you have many repos sharing many secrets &mdash; rotate from one place, not one PR per repo.</li>
<li><strong>Don&rsquo;t echo secrets</strong> &mdash; even masking has gaps; redacted strings can sometimes leak via debug, error stacks, or third-party action output.</li>
<li><strong>Don&rsquo;t pass secrets to forked PRs</strong> &mdash; <code>pull_request_target</code> is dangerous; if you must, use a separate workflow with strict allowlist.</li>
<li><strong>Audit usage</strong> &mdash; GitHub Audit Log shows secret access events.</li>
<li><strong>Rotate</strong> &mdash; tokens and keys on a schedule. Pair with GitHub Push Protection + Secret Scanning to catch leaks.</li>
</ul>
<p>For per-job dynamic secrets, the <strong>HashiCorp Vault GitHub Action</strong> issues short-lived database credentials, AWS roles, etc. on the fly &mdash; no static secrets to rotate.</p>'''

ANSWERS[58] = r'''<p>Managing dependencies in Docker means controlling what goes into the image: language packages, system libraries, build tools. Done well, layers cache and rebuilds are fast; done poorly, every push reinstalls the world. The pattern that wins for MERN: lockfile-driven, multi-stage, ordered for cache hits.</p>
<p><strong>Node.js example:</strong></p>
<pre><code># Dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./   # &laquo; only deps files
RUN npm ci --omit=dev                    # deterministic install from lockfile
# This whole layer caches as long as package*.json is unchanged

FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci                               # full deps for build
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
RUN apk add --no-cache tini              # system dep
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist          ./dist
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/server.js"]
</code></pre>
<p><strong>Key principles:</strong></p>
<ul>
<li><strong>Copy lockfile before source.</strong> Source changes daily; lockfile changes weekly. Putting <code>npm ci</code> after <code>COPY package*.json</code> means the deps layer caches across most builds.</li>
<li><strong>Use <code>npm ci</code> (or <code>pnpm install --frozen-lockfile</code>, <code>yarn install --immutable</code>)</strong> &mdash; respects the lockfile exactly, no version drift.</li>
<li><strong>Multi-stage</strong> &mdash; install dev deps for the build stage, copy only runtime deps to the final image.</li>
<li><strong>Pin versions</strong> in <code>package.json</code> + commit lockfile.</li>
<li><strong>System packages:</strong> <code>apk add --no-cache</code> on Alpine, <code>apt-get install --no-install-recommends &amp;&amp; rm -rf /var/lib/apt/lists/*</code> on Debian; combine in one <code>RUN</code> to keep one layer.</li>
</ul>
<p><strong>Cache mounts</strong> (BuildKit):</p>
<pre><code>RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev
</code></pre>
<p>Cache mounts share the npm/pnpm cache across builds without baking it into the image.</p>
<p><strong>Multi-language stacks</strong> (e.g. Node + Python + system tools): copy each lockfile separately and run installs in cache-friendly order:</p>
<pre><code>COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
</code></pre>
<p><strong>Vulnerability hygiene:</strong> scan with <strong>Trivy</strong>, <strong>Grype</strong>, <strong>Snyk</strong>, or <strong>Socket.dev</strong> in CI; pin to digests; track CVEs via <strong>Dependabot</strong> + <strong>renovate</strong>; sign images with <strong>cosign</strong>; generate SBOM with BuildKit (<code>--sbom=true</code>).</p>
<p><strong>Honest 2026 advice:</strong> for a stable, hardened container, consider <strong>Buildpacks</strong> (Heroku/CNB), <strong>Nixpacks</strong> (Railway), or <strong>Chainguard Images</strong> (distroless, signed, low-CVE base images) instead of writing your own Dockerfile from scratch. They handle dep ordering, caching, and security baselines automatically.</p>'''

ANSWERS[59] = r'''<p>An <strong>Ingress</strong> exposes HTTP/HTTPS routes from outside the cluster to Services inside it. Without an Ingress, you&rsquo;d need one cloud LoadBalancer per Service &mdash; expensive and unmanageable. Ingress lets one entry point fan out to many Services based on hostname, path, or headers.</p>
<p><strong>Architecture:</strong></p>
<table>
<thead><tr><th>Layer</th><th>Component</th></tr></thead>
<tbody>
<tr><td>Outside</td><td>DNS &rarr; cloud LoadBalancer (one)</td></tr>
<tr><td>In cluster</td><td>Ingress controller (NGINX, Traefik, HAProxy, Envoy/Contour, Cilium)</td></tr>
<tr><td>Routing rules</td><td>Ingress resources match host/path and forward to Services</td></tr>
<tr><td>Backends</td><td>Services &rarr; Pods</td></tr>
</tbody>
</table>
<p><strong>Example:</strong></p>
<pre><code>apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
    nginx.ingress.kubernetes.io/proxy-body-size: 10m
spec:
  ingressClassName: nginx
  tls:
    - hosts: [app.example.com]
      secretName: app-tls         # cert-manager populates this
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api/
            pathType: Prefix
            backend: { service: { name: api, port: { number: 80 } } }
          - path: /
            pathType: Prefix
            backend: { service: { name: web, port: { number: 80 } } }
</code></pre>
<p><strong>Ingress controllers (2026 popular):</strong></p>
<ul>
<li><strong>NGINX Ingress</strong> &mdash; the default for most clusters. Stable, ubiquitous, well-documented.</li>
<li><strong>Traefik</strong> &mdash; great UX, built-in dashboard, dynamic config, popular in K3s.</li>
<li><strong>Envoy/Contour</strong> &mdash; programmable, high performance.</li>
<li><strong>Cilium</strong> &mdash; eBPF-based; combines CNI + Ingress + service mesh in one.</li>
<li><strong>HAProxy</strong> &mdash; very fast, advanced routing.</li>
</ul>
<p><strong>Gateway API &mdash; the modern successor:</strong></p>
<p>Ingress&rsquo;s extension model (annotations) doesn&rsquo;t scale. The <strong>Gateway API</strong> (GA in K8s 1.29+) is the official replacement: typed CRDs (<code>Gateway</code>, <code>HTTPRoute</code>, <code>TCPRoute</code>, <code>GRPCRoute</code>), role separation between cluster operators and app teams, and richer routing (header matching, traffic splits, request mirroring without annotations). NGINX, Istio, Cilium, Envoy Gateway, Traefik, and Kong all implement Gateway API in 2026. Greenfield clusters should start with Gateway API.</p>
<p><strong>TLS and DNS</strong> typically come from <strong>cert-manager</strong> (Let&rsquo;s Encrypt) + <strong>external-dns</strong> (auto-creates Route 53/Cloudflare records from Ingress hosts). For WAF, layer Cloudflare or AWS WAF in front of the cluster LoadBalancer.</p>'''

ANSWERS[60] = r'''<p>Integrating Jenkins with Docker means: agents can build images, registries are accessible, and pipelines can run/test in containers. Three integration points cover most needs.</p>
<p><strong>1. Run Jenkins itself in Docker</strong>:</p>
<pre><code>docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins-home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts-jdk21
</code></pre>
<p>Mounting <code>docker.sock</code> lets Jenkins build images using the host&rsquo;s Docker daemon. <em>This is convenient but grants the Jenkins container effective root on the host</em> &mdash; only do this in trusted single-tenant setups.</p>
<p><strong>2. Run builds inside Docker containers (Docker Pipeline plugin):</strong></p>
<pre><code>pipeline {
  agent { docker { image 'node:20-alpine' } }
  stages {
    stage('Test') {
      steps {
        sh 'npm ci &amp;&amp; npm test'
      }
    }
  }
}
</code></pre>
<p>Each stage runs in a fresh container &mdash; clean state, no toolchain installs on agents. Mix images per stage:</p>
<pre><code>stages {
  stage('Backend') {
    agent { docker { image 'node:20' } }
    steps { sh 'cd server &amp;&amp; npm test' }
  }
  stage('Python ML') {
    agent { docker { image 'python:3.12' } }
    steps { sh 'cd ml &amp;&amp; pytest' }
  }
}
</code></pre>
<p><strong>3. Build and push images from a pipeline:</strong></p>
<pre><code>pipeline {
  agent any
  stages {
    stage('Image') {
      steps {
        script {
          docker.withRegistry('https://ghcr.io', 'ghcr-credentials') {
            def img = docker.build("ghcr.io/acme/api:${env.GIT_COMMIT}")
            img.push()
            img.push('latest')
          }
        }
      }
    }
  }
}
</code></pre>
<p><strong>4. Kubernetes plugin (recommended for production):</strong></p>
<p>Each Jenkins build becomes a Pod with whatever containers it needs (Node, Docker-in-Docker, Kaniko). Agents are ephemeral, autoscale to zero, and isolation is real. The DinD pattern is the most common but you can swap it for <strong>Kaniko</strong> (rootless, no privileged container) for production-grade security:</p>
<pre><code>podTemplate(yaml: &#39;&#39;&#39;
spec:
  containers:
    - name: kaniko
      image: gcr.io/kaniko-project/executor:debug
      command: ['cat']
      tty: true
&#39;&#39;&#39;) {
  node(POD_LABEL) {
    container('kaniko') {
      sh '/kaniko/executor --dockerfile=Dockerfile \
          --context=`pwd` --destination=ghcr.io/acme/api:${env.GIT_COMMIT}'
    }
  }
}
</code></pre>
<p><strong>Best practices (2026):</strong></p>
<ul>
<li><strong>Don&rsquo;t mount <code>docker.sock</code></strong> for multi-tenant Jenkins &mdash; use Kaniko or Buildah.</li>
<li><strong>Ephemeral agents</strong> on Kubernetes &mdash; clean state per build, scale to zero between.</li>
<li><strong>Use Docker images for tools</strong>, not <code>apt-get install</code> in pipelines &mdash; faster, cacheable, reproducible.</li>
<li><strong>BuildKit cache</strong> via registry (<code>cache-to type=registry,mode=max</code>) for cross-build speed.</li>
<li><strong>cosign</strong>-sign images and verify in K8s with policy-controller.</li>
<li><strong>Scan in pipeline</strong> &mdash; Trivy/Grype, fail on critical CVEs.</li>
</ul>'''

ANSWERS[61] = r'''<p>A <strong>Docker container registry</strong> is a server that stores and distributes Docker images. When you run <code>docker push</code>, the image layers are uploaded to a registry; <code>docker pull</code> retrieves them. Registries make images portable across CI runners, K8s clusters, and developer laptops.</p>
<p>Common registries in 2026:</p>
<table>
<tr><th>Registry</th><th>Best for</th><th>Notes</th></tr>
<tr><td><strong>Docker Hub</strong></td><td>Public images</td><td>Free tier rate-limits anonymous pulls (100/6h); auth helps.</td></tr>
<tr><td><strong>GitHub Container Registry (GHCR)</strong></td><td>OSS + GitHub-native CI</td><td><code>ghcr.io/owner/image</code>; auth via <code>GITHUB_TOKEN</code>.</td></tr>
<tr><td><strong>AWS ECR</strong></td><td>EKS / ECS / Lambda</td><td>Private by default; IAM-controlled; ECR Public for OSS.</td></tr>
<tr><td><strong>Google Artifact Registry</strong></td><td>GKE / Cloud Run</td><td>Replaces deprecated GCR; multi-format (Docker, npm, Maven).</td></tr>
<tr><td><strong>Azure Container Registry (ACR)</strong></td><td>AKS</td><td>Geo-replication, Tasks for in-registry builds.</td></tr>
<tr><td><strong>Harbor</strong></td><td>Self-hosted enterprise</td><td>OSS by CNCF; vulnerability scanning, replication, RBAC.</td></tr>
<tr><td><strong>Quay.io</strong></td><td>Red Hat / OpenShift</td><td>Robot accounts, Clair scanning.</td></tr>
</table>
<p>Typical workflow:</p>
<pre><code>docker login ghcr.io -u USERNAME -p $GITHUB_TOKEN
docker build -t ghcr.io/acme/api:1.2.3 .
docker push ghcr.io/acme/api:1.2.3
</code></pre>
<p><strong>Best practices:</strong> tag with both <code>:1.2.3</code> (immutable) and <code>:latest</code> (moving), enable vulnerability scanning (Trivy, Snyk, ECR Enhanced Scanning), use OIDC tokens instead of long-lived passwords from CI, and configure retention policies to delete untagged/old images automatically. Sign images with <strong>Sigstore Cosign</strong> and verify signatures at deploy time for supply-chain security.</p>'''

ANSWERS[62] = r'''<p>GitHub Actions runs tests by checking out the code, installing the runtime + dependencies, then executing your test command on every push or pull request. Workflows live in <code>.github/workflows/test.yml</code>.</p>
<p><strong>Minimal Node.js example:</strong></p>
<pre><code>name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm test
</code></pre>
<p><strong>Key features:</strong></p>
<ul>
<li><strong>Matrix builds</strong> &mdash; test across Node 18/20/22 and ubuntu/macos/windows in parallel: <code>strategy: { matrix: { node: [18, 20, 22] } }</code>.</li>
<li><strong>Service containers</strong> &mdash; spin up Postgres, MongoDB, Redis as a sidecar service for integration tests, no setup script needed.</li>
<li><strong>Artifacts</strong> &mdash; <code>actions/upload-artifact@v4</code> to save coverage reports, screenshots from failing Playwright runs, build outputs for downstream jobs.</li>
<li><strong>Caching</strong> &mdash; <code>actions/setup-node</code>, <code>setup-python</code>, etc. handle npm/pip/cargo cache automatically; or <code>actions/cache@v4</code> for custom paths.</li>
<li><strong>Required checks</strong> &mdash; mark the job &ldquo;required&rdquo; in branch protection so PRs can&rsquo;t merge with failing tests.</li>
</ul>
<p><strong>Concurrency</strong> control prevents wasted runs on rapid pushes:</p>
<pre><code>concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
</code></pre>
<p>For monorepos, use <code>paths:</code> filters or tools like <strong>Nx Affected</strong> / <strong>Turbo</strong> to only test packages whose code changed, dramatically cutting CI time.</p>'''

ANSWERS[63] = r'''<p>A <strong>Persistent Volume (PV)</strong> is a piece of storage in a Kubernetes cluster, decoupled from any pod&rsquo;s lifecycle. A <strong>PersistentVolumeClaim (PVC)</strong> is a pod&rsquo;s request for storage, matched to a PV by size and access mode.</p>
<p>The provisioning flow:</p>
<ol>
<li>Cluster admin creates a <strong>StorageClass</strong> (e.g. <code>gp3</code> on EKS, <code>premium-rwo</code> on GKE).</li>
<li>Application defines a <strong>PVC</strong> requesting <em>X</em> GB with an access mode.</li>
<li>The <strong>CSI driver</strong> dynamically provisions a PV (an EBS volume, GCE PD, Azure Disk, etc.) and binds it to the claim.</li>
<li>The pod mounts the PVC at a path inside the container.</li>
</ol>
<p><strong>Example:</strong></p>
<pre><code>apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongo-data
spec:
  storageClassName: gp3
  accessModes: [ReadWriteOnce]
  resources:
    requests: { storage: 50Gi }
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: mongo }
spec:
  template:
    spec:
      containers:
        - name: mongo
          image: mongo:7
          volumeMounts:
            - name: data
              mountPath: /data/db
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        resources: { requests: { storage: 50Gi } }
</code></pre>
<p><strong>Access modes:</strong> <code>ReadWriteOnce</code> (RWO &mdash; one node), <code>ReadOnlyMany</code> (ROX), <code>ReadWriteMany</code> (RWX &mdash; only NFS / EFS / Azure Files / Filestore), <code>ReadWriteOncePod</code> (single pod, K8s 1.27+).</p>
<p><strong>Reclaim policies:</strong> <code>Delete</code> (default for dynamic) destroys the underlying disk when the PVC is deleted; <code>Retain</code> keeps it for manual cleanup &mdash; safer for production data.</p>
<p>For databases, prefer <strong>managed services</strong> (Atlas, RDS, Cloud SQL) over self-hosted PVs &mdash; you avoid backup/upgrade/replication operational burden. Use PVs for caches, file uploads, and stateful workloads where managed isn&rsquo;t available.</p>'''

ANSWERS[64] = r'''<p>A <strong>Jenkinsfile</strong> defines a pipeline as code, checked into the repo at the root. When Jenkins detects a Jenkinsfile (via a Multibranch Pipeline or Pipeline job), it executes its stages on each commit.</p>
<p><strong>Step 1 &mdash; create the Jenkinsfile</strong> at the repo root:</p>
<pre><code>// Jenkinsfile (declarative)
pipeline {
  agent { label 'docker' }
  options {
    timeout(time: 30, unit: 'MINUTES')
    disableConcurrentBuilds()
  }
  environment {
    REGISTRY = 'ghcr.io/acme'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Test') {
      steps {
        sh 'npm ci'
        sh 'npm test'
      }
    }
    stage('Build') {
      steps {
        sh "docker build -t $REGISTRY/api:${env.GIT_COMMIT} ."
      }
    }
    stage('Push') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr', usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login ghcr.io -u $U --password-stdin'
          sh "docker push $REGISTRY/api:${env.GIT_COMMIT}"
        }
      }
    }
  }
  post {
    always { archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true }
    failure { mail to: 'team@acme.com', subject: "Build failed: ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>Step 2 &mdash; create the Jenkins job:</strong></p>
<ol>
<li><em>New Item</em> &rarr; <em>Multibranch Pipeline</em> (recommended &mdash; auto-discovers branches and PRs).</li>
<li>Configure the Git source (GitHub/GitLab/Bitbucket plugin) with credentials.</li>
<li>Set <em>Script Path</em> to <code>Jenkinsfile</code>.</li>
<li>Configure scan triggers: webhook (best) or periodic.</li>
</ol>
<p><strong>Step 3 &mdash; trigger:</strong> push to a branch &rarr; Jenkins detects the change via webhook and runs the pipeline. Open Blue Ocean (or the modern <em>Pipeline Graph</em> view) to watch stages execute.</p>
<p><strong>Tips:</strong> Keep secrets in Jenkins Credentials (never inline). Use <code>when</code> directives to skip stages on PRs vs main. Prefer <strong>Declarative</strong> over Scripted unless you need full Groovy. For 2026 greenfield projects, evaluate GitHub Actions / GitLab CI / Buildkite first &mdash; Jenkins is typically chosen for legacy continuity or specific plugin needs.</p>'''

ANSWERS[65] = r'''<p><strong>Docker Swarm</strong> is Docker&rsquo;s built-in clustering and orchestration mode that turns a group of Docker hosts into a single virtual host. It is simpler than Kubernetes but vastly less capable; in 2026 it sees little new adoption &mdash; Kubernetes (often via managed EKS / GKE / AKS) is the default.</p>
<p><strong>When you might still meet Swarm:</strong> small teams, edge devices, legacy systems that haven&rsquo;t migrated, or the simplicity of a single <code>docker</code> binary with no separate kubectl/Helm/operators.</p>
<p><strong>Basic workflow:</strong></p>
<pre><code># 1. Initialize a swarm on the first node (becomes manager)
docker swarm init --advertise-addr 10.0.0.1

# 2. Get the join command and run it on workers
docker swarm join-token worker
# (paste the printed command on each worker)

# 3. List nodes
docker node ls

# 4. Deploy a stack from a Compose file
docker stack deploy -c docker-compose.yml myapp

# 5. Scale a service
docker service scale myapp_api=5

# 6. Roll a new image
docker service update --image ghcr.io/acme/api:2.0.0 myapp_api
</code></pre>
<p><strong>Swarm-aware Compose file:</strong></p>
<pre><code>services:
  api:
    image: ghcr.io/acme/api:1.0.0
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        order: start-first
      restart_policy:
        condition: on-failure
    ports: ["3000:3000"]
</code></pre>
<p><strong>Comparison with K8s:</strong></p>
<table>
<tr><th>Feature</th><th>Docker Swarm</th><th>Kubernetes</th></tr>
<tr><td>Setup complexity</td><td>Trivial (1 command)</td><td>High (use managed)</td></tr>
<tr><td>Ecosystem</td><td>Stagnant</td><td>Massive (Helm, Operators, mesh)</td></tr>
<tr><td>Auto-scaling</td><td>Basic</td><td>HPA + VPA + Cluster Autoscaler</td></tr>
<tr><td>Storage</td><td>Limited</td><td>CSI ecosystem</td></tr>
<tr><td>Community</td><td>Maintenance only</td><td>CNCF graduated, active</td></tr>
</table>
<p><strong>2026 advice:</strong> for new projects, skip Swarm. Use <strong>Docker Compose</strong> for local dev, then <strong>K8s</strong> (managed) or a PaaS (Fly, Railway, Render) for prod.</p>'''

ANSWERS[66] = r'''<p>The <strong>GitHub Actions Marketplace</strong> (<code>github.com/marketplace</code>) is a public catalog of reusable, community-contributed actions. Instead of writing shell scripts for common tasks, you reference an action by <code>owner/repo@version</code>.</p>
<p><strong>Example workflow using marketplace actions:</strong></p>
<pre><code>jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/deploy
          aws-region: us-east-1
      - uses: docker/build-push-action@v6
        with: { push: true, tags: acme/api:${{ github.sha }} }
      - uses: codecov/codecov-action@v4
      - uses: slackapi/slack-github-action@v1
        with: { payload: '{"text":"Deploy complete"}' }
</code></pre>
<p><strong>Categories of useful actions:</strong></p>
<ul>
<li><strong>Setup</strong> &mdash; <code>actions/setup-node</code>, <code>setup-python</code>, <code>setup-go</code>, <code>setup-java</code>; handle install + caching.</li>
<li><strong>Cloud auth</strong> &mdash; <code>aws-actions/configure-aws-credentials</code>, <code>google-github-actions/auth</code>, <code>azure/login</code>; OIDC-based, no long-lived secrets.</li>
<li><strong>Build/release</strong> &mdash; <code>docker/build-push-action</code>, <code>goreleaser/goreleaser-action</code>, <code>softprops/action-gh-release</code>.</li>
<li><strong>Quality/security</strong> &mdash; <code>codecov/codecov-action</code>, <code>aquasecurity/trivy-action</code>, <code>github/codeql-action</code>, <code>step-security/harden-runner</code>.</li>
<li><strong>Notifications</strong> &mdash; Slack, Discord, Microsoft Teams, email actions.</li>
</ul>
<p><strong>Security best practices:</strong></p>
<ul>
<li><strong>Pin to a commit SHA</strong>, not a tag, for third-party actions: <code>uses: foo/bar@a1b2c3d</code>. Tags are mutable; SHAs are not.</li>
<li>Prefer official (<code>actions/*</code>, <code>github/*</code>) and verified-creator actions where possible.</li>
<li>Review the action&rsquo;s source and required permissions before adoption &mdash; a malicious action sees your secrets.</li>
<li>Use <code>step-security/harden-runner</code> to audit/block egress and detect malicious behaviour.</li>
<li>Set least-privilege <code>permissions:</code> at the workflow or job level.</li>
</ul>
<p>You can also publish your own actions (JavaScript, Docker, or composite) to the Marketplace for reuse across repos and the community.</p>'''

ANSWERS[67] = r'''<p>Deploying Jenkins on Kubernetes lets the master run as a Pod and dynamically spawn agent Pods per build, scaling on demand. The standard approach in 2026 is the official <strong>Jenkins Helm chart</strong>.</p>
<p><strong>1. Install via Helm:</strong></p>
<pre><code>helm repo add jenkins https://charts.jenkins.io
helm repo update

# minimal values.yaml
cat &lt;&lt;EOF &gt; values.yaml
controller:
  adminUser: admin
  ingress:
    enabled: true
    hostName: jenkins.acme.com
    tls:
      - secretName: jenkins-tls
        hosts: [jenkins.acme.com]
persistence:
  size: 20Gi
  storageClass: gp3
agent:
  enabled: true       # spawn agents as pods
EOF

helm upgrade --install jenkins jenkins/jenkins -n ci --create-namespace -f values.yaml
</code></pre>
<p><strong>2. Configure dynamic agents</strong> &mdash; the Helm chart pre-installs the <em>Kubernetes plugin</em>, which is configured in <em>Manage Jenkins &rarr; Clouds &rarr; Kubernetes</em>. Each pipeline declares the agent it needs:</p>
<pre><code>pipeline {
  agent {
    kubernetes {
      yaml &apos;&apos;&apos;
        apiVersion: v1
        kind: Pod
        spec:
          containers:
            - name: node
              image: node:20
              command: [cat]
              tty: true
            - name: docker
              image: docker:25-dind
              securityContext: { privileged: true }
      &apos;&apos;&apos;
    }
  }
  stages {
    stage('Test') { steps { container('node') { sh 'npm test' } } }
    stage('Build') { steps { container('docker') { sh 'docker build .' } } }
  }
}
</code></pre>
<p>Pods are created at job start, deleted when the build finishes &mdash; no idle agent cost.</p>
<p><strong>3. Operational concerns:</strong></p>
<ul>
<li><strong>Persistence</strong> &mdash; controller stores config + plugins on a PV; back up regularly via Velero or volume snapshots.</li>
<li><strong>Configuration as Code (JCasC)</strong> &mdash; describe Jenkins config in YAML so it&rsquo;s versioned and reproducible after a disaster.</li>
<li><strong>Auth</strong> &mdash; integrate with GitHub OAuth, Okta, or Azure AD via SSO plugins.</li>
<li><strong>Backups</strong> &mdash; <code>thinBackup</code> plugin or scheduled rsync of <code>/var/jenkins_home</code> to S3.</li>
</ul>
<p><strong>2026 alternatives:</strong> for greenfield K8s-native CI, consider <strong>Tekton</strong>, <strong>Argo Workflows</strong>, or <strong>GitHub Actions self-hosted runners</strong> on K8s &mdash; all leaner than Jenkins on K8s.</p>'''

ANSWERS[68] = r'''<p>Monitoring a Kubernetes cluster needs visibility into three layers: <strong>cluster health</strong> (nodes, control plane), <strong>workloads</strong> (pods, deployments), and <strong>application metrics</strong> (latency, errors, business KPIs). The 2026 standard is <strong>Prometheus + Grafana</strong> for self-hosted, or a managed observability platform.</p>
<p><strong>The kube-prometheus-stack:</strong> the most common bundle, installed via Helm:</p>
<pre><code>helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace
</code></pre>
<p>This installs:</p>
<ul>
<li><strong>Prometheus</strong> &mdash; scrapes metrics from kubelet, node-exporter, kube-state-metrics, and your Pods.</li>
<li><strong>Grafana</strong> &mdash; pre-built dashboards for cluster, nodes, namespaces, deployments.</li>
<li><strong>Alertmanager</strong> &mdash; routes alerts to Slack/PagerDuty/Opsgenie.</li>
<li><strong>node-exporter</strong> &mdash; CPU, memory, disk, network per node.</li>
<li><strong>kube-state-metrics</strong> &mdash; counts of pods/deployments/jobs and their states.</li>
</ul>
<p><strong>Key signals to watch:</strong></p>
<table>
<tr><th>Layer</th><th>Metric</th><th>Why</th></tr>
<tr><td>Node</td><td>CPU/memory pressure, disk %</td><td>Pods evicted when full</td></tr>
<tr><td>Pod</td><td>Restart count, OOMKilled events</td><td>Memory leak, bad limits</td></tr>
<tr><td>Deployment</td><td>Available vs desired replicas</td><td>Health/scaling issues</td></tr>
<tr><td>API server</td><td>Latency p99, error rate</td><td>Control plane health</td></tr>
<tr><td>Etcd</td><td>Disk fsync, leader changes</td><td>Cluster-wide impact</td></tr>
</table>
<p><strong>Logs and traces:</strong> add <strong>Loki</strong> + <strong>Promtail</strong> (or Vector / Fluent Bit) for logs, and <strong>OpenTelemetry Collector</strong> shipping to <strong>Tempo</strong>, <strong>Jaeger</strong>, or a SaaS for distributed tracing. Together with metrics this gives full <em>three pillars</em> coverage.</p>
<p><strong>Managed alternatives in 2026</strong> (skip running this yourself):</p>
<ul>
<li><strong>Datadog</strong> &mdash; agent DaemonSet, auto-discovers everything, polished UX.</li>
<li><strong>Grafana Cloud</strong> &mdash; managed Prometheus + Loki + Tempo.</li>
<li><strong>Honeycomb</strong> &mdash; trace-first; great for high-cardinality debugging.</li>
<li><strong>Cloud-native</strong> &mdash; CloudWatch Container Insights, GKE Cloud Monitoring, Azure Monitor for Containers.</li>
</ul>
<p><strong>Alerting</strong>: start with Google&rsquo;s SRE <em>golden signals</em> (latency, traffic, errors, saturation) per service, and alert on symptoms (user-visible failure) rather than causes (CPU 90%) to avoid pager fatigue.</p>'''

ANSWERS[69] = r'''<p>A <strong>Docker network</strong> connects containers and decides who can talk to whom. Docker creates default networks at install time, but you typically create custom networks for application isolation.</p>
<p><strong>Default networks (run <code>docker network ls</code>):</strong></p>
<table>
<tr><th>Network</th><th>Driver</th><th>Use</th></tr>
<tr><td><code>bridge</code></td><td>bridge</td><td>Default for containers without <code>--network</code> &mdash; legacy</td></tr>
<tr><td><code>host</code></td><td>host</td><td>Container shares host network (no isolation)</td></tr>
<tr><td><code>none</code></td><td>null</td><td>No networking at all</td></tr>
</table>
<p><strong>Create a custom user-defined bridge network:</strong></p>
<pre><code>docker network create --driver bridge app-net
docker network create --driver bridge \
  --subnet 172.30.0.0/16 \
  --gateway 172.30.0.1 \
  app-net
</code></pre>
<p><strong>Run containers on it:</strong></p>
<pre><code>docker run -d --name mongo --network app-net mongo:7
docker run -d --name api --network app-net \
  -e MONGO_URL=mongodb://mongo:27017 \
  ghcr.io/acme/api:1.0.0
</code></pre>
<p>Containers on a user-defined bridge get <strong>automatic DNS</strong> &mdash; <code>api</code> can reach <code>mongo</code> by name without ports being published to the host. This is the main reason to prefer a custom network over the default <code>bridge</code>.</p>
<p><strong>Inspect / connect / disconnect / remove:</strong></p>
<pre><code>docker network inspect app-net
docker network connect app-net web
docker network disconnect app-net web
docker network rm app-net           # only if no containers attached
docker network prune                # remove all unused networks
</code></pre>
<p><strong>Network drivers beyond bridge:</strong></p>
<ul>
<li><strong>overlay</strong> &mdash; multi-host, used by Swarm to span containers across nodes.</li>
<li><strong>macvlan</strong> &mdash; container gets its own MAC + IP on the host LAN; useful for legacy apps that need layer-2 access.</li>
<li><strong>ipvlan</strong> &mdash; similar to macvlan but more efficient.</li>
</ul>
<p>In <strong>Docker Compose</strong>, networks are usually implicit &mdash; Compose creates a project network and all services join automatically. You can declare additional networks for segmentation:</p>
<pre><code>services:
  web: { networks: [front] }
  api: { networks: [front, back] }
  db:  { networks: [back] }
networks:
  front: {}
  back:  {}
</code></pre>
<p>This puts <code>db</code> behind <code>api</code> &mdash; <code>web</code> can&rsquo;t reach it directly.</p>'''

ANSWERS[70] = r'''<p>GitHub Actions automates testing on every push and pull request. The workflow runs in <code>.github/workflows/</code>, executes your test command on a runner, and reports status back to the PR &mdash; required checks block merges if tests fail.</p>
<p><strong>Comprehensive Node.js example with lint, type-check, unit, and e2e:</strong></p>
<pre><code>name: CI
on:
  push: { branches: [main] }
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongo:
        image: mongo:7
        ports: [27017:27017]
      redis:
        image: redis:7
        ports: [6379:6379]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage
      - run: npm run build
      - uses: codecov/codecov-action@v4
        with: { token: ${{ secrets.CODECOV_TOKEN }} }

  e2e:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
</code></pre>
<p><strong>Patterns for fast, reliable test runs:</strong></p>
<ul>
<li><strong>Matrix testing</strong> across Node 18 / 20 / 22 in parallel: <code>strategy: { matrix: { node: [18, 20, 22] } }</code>, then use <code>${{ matrix.node }}</code>.</li>
<li><strong>Service containers</strong> for stateful dependencies (DBs, queues) &mdash; faster than docker-compose-up scripts.</li>
<li><strong>Sharding</strong> long suites: <code>strategy: { matrix: { shard: [1, 2, 3, 4] } }</code> + <code>npm test -- --shard=${{ matrix.shard }}/4</code>.</li>
<li><strong>Cache</strong> &mdash; setup-node handles npm/yarn/pnpm caches automatically; for custom paths use <code>actions/cache@v4</code>.</li>
<li><strong>Required checks</strong> &mdash; mark <em>test</em> required in branch protection so PRs can&rsquo;t merge red.</li>
<li><strong>Concurrency</strong> &mdash; cancel superseded runs on rapid pushes (saves runner minutes).</li>
<li><strong>Annotations</strong> &mdash; tools like <code>jest-github-actions-reporter</code> or <code>vitest-github-actions-reporter</code> surface failures inline in the PR diff.</li>
</ul>
<p><strong>Monorepo tip:</strong> use <strong>Nx Affected</strong>, <strong>Turbo</strong>, or path filters (<code>paths: [packages/api/**]</code>) to run only the tests for changed packages &mdash; keeps CI under a few minutes even at scale.</p>'''

ANSWERS[71] = r'''<p>A <strong>Jenkins build step</strong> is a single executable unit inside a stage &mdash; it runs a shell command, invokes a plugin, or calls a function. Multiple steps form a stage; multiple stages form a pipeline.</p>
<p><strong>In a declarative pipeline:</strong></p>
<pre><code>pipeline {
  agent any
  stages {
    stage('Test') {
      steps {                          // ← block of build steps
        sh 'npm ci'                    // shell step
        sh 'npm test'                  // another shell step
        junit 'test-results/**/*.xml'  // plugin step (JUnit)
        archiveArtifacts 'coverage/**' // plugin step (artifacts)
      }
    }
  }
}
</code></pre>
<p><strong>Common built-in steps:</strong></p>
<table>
<tr><th>Step</th><th>Purpose</th></tr>
<tr><td><code>sh</code> / <code>bat</code> / <code>powershell</code></td><td>Run shell commands (Linux / Windows)</td></tr>
<tr><td><code>checkout scm</code></td><td>Pull source from the configured Git repo</td></tr>
<tr><td><code>git url: '...'</code></td><td>Clone a specific repo</td></tr>
<tr><td><code>echo</code></td><td>Print to the build log</td></tr>
<tr><td><code>archiveArtifacts</code></td><td>Save files for later download</td></tr>
<tr><td><code>junit</code></td><td>Publish test results (JUnit XML)</td></tr>
<tr><td><code>stash</code> / <code>unstash</code></td><td>Pass files between stages on different agents</td></tr>
<tr><td><code>input</code></td><td>Pause for human approval (manual gate)</td></tr>
<tr><td><code>timeout</code></td><td>Fail the step after N minutes</td></tr>
<tr><td><code>retry</code></td><td>Retry a flaky step N times</td></tr>
<tr><td><code>withCredentials</code></td><td>Inject secrets as env vars for the block</td></tr>
<tr><td><code>parallel</code></td><td>Run multiple branches at once</td></tr>
</table>
<p><strong>Plugin-provided steps:</strong> Docker (<code>docker.build</code>, <code>docker.image('...').inside { }</code>), Kubernetes (<code>kubernetesDeploy</code>), Slack (<code>slackSend</code>), AWS (<code>withAWS</code>), and thousands more on the Plugin Index.</p>
<p><strong>Freestyle vs Pipeline:</strong> in classic Freestyle jobs, &ldquo;build steps&rdquo; are configured in the UI as discrete blocks (Execute Shell, Invoke Maven, etc.). In Pipeline jobs they are code in <code>steps { }</code>, which is the modern recommendation &mdash; reproducible, reviewable, versioned with the application.</p>
<p><strong>Best practice:</strong> keep individual steps small and focused; one shell step per logical action so failures pinpoint the cause. Wrap brittle network calls in <code>retry(3) { sh '...' }</code>, and put time-bounded operations under <code>timeout</code>.</p>'''

ANSWERS[72] = r'''<p><strong>Kubernetes Secrets</strong> store sensitive data &mdash; passwords, API keys, certificates &mdash; separately from Pod definitions, so manifests can be checked into Git without exposing credentials. Secrets are mounted as files or injected as env vars at Pod start.</p>
<p><strong>Create a Secret:</strong></p>
<pre><code># From literal values
kubectl create secret generic api-secrets \
  --from-literal=DB_PASSWORD='hunter2' \
  --from-literal=JWT_SECRET='supersecret'

# From a file
kubectl create secret generic tls-cert \
  --from-file=tls.crt --from-file=tls.key

# From a YAML manifest (values must be base64-encoded)
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
type: Opaque
data:
  DB_PASSWORD: aHVudGVyMg==     # base64
  JWT_SECRET:  c3VwZXJzZWNyZXQ=
</code></pre>
<p><strong>Consume in a Pod:</strong></p>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  template:
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: DB_PASSWORD
          envFrom:
            - secretRef: { name: api-secrets }   # all keys at once
          volumeMounts:
            - name: certs
              mountPath: /etc/tls
              readOnly: true
      volumes:
        - name: certs
          secret: { secretName: tls-cert }
</code></pre>
<p><strong>Critical caveats:</strong></p>
<ul>
<li><strong>Base64 is not encryption</strong> &mdash; anyone with API access can decode it. Enable <strong>encryption at rest</strong> for etcd via <code>EncryptionConfiguration</code> (managed clusters do this for you).</li>
<li><strong>RBAC is essential</strong> &mdash; restrict <code>get/list secrets</code> to a tiny set of identities. Default service accounts often have too much access.</li>
<li><strong>Don&rsquo;t commit Secret YAML to Git</strong> with raw values. Use <strong>Sealed Secrets</strong>, <strong>SOPS</strong>, or pull from an external store.</li>
</ul>
<p><strong>2026 best practice &mdash; external secret managers:</strong></p>
<table>
<tr><th>Tool</th><th>Pattern</th></tr>
<tr><td><strong>External Secrets Operator</strong></td><td>Sync from AWS Secrets Manager / GCP Secret Manager / Azure Key Vault / Vault / Doppler / Infisical into K8s Secrets</td></tr>
<tr><td><strong>Vault Secrets Operator</strong></td><td>HashiCorp Vault &rarr; K8s Secret with auto-rotation</td></tr>
<tr><td><strong>CSI Secrets Store Driver</strong></td><td>Mount secrets directly from a manager into Pod files, no K8s Secret intermediary</td></tr>
<tr><td><strong>Sealed Secrets</strong></td><td>Encrypt Secret manifests so they can be safely Git-committed</td></tr>
</table>
<p>This keeps the source-of-truth in a hardened secret manager with audit logs and rotation, while K8s gets just-in-time copies.</p>'''

ANSWERS[73] = r'''<p>Running a Docker container starts a process from a built image. The basic command is <code>docker run [options] image [command]</code> &mdash; Docker pulls the image if missing, creates a writable layer on top, and starts the entrypoint.</p>
<p><strong>Common patterns:</strong></p>
<pre><code># Foreground, interactive, removed when done
docker run -it --rm ubuntu:24.04 bash

# Detached web service with port mapping
docker run -d --name web -p 8080:80 nginx:alpine

# Container with env vars and volume
docker run -d --name api \
  -e NODE_ENV=production \
  -e MONGO_URL=mongodb://host.docker.internal:27017/app \
  -p 3000:3000 \
  -v $(pwd)/uploads:/app/uploads \
  ghcr.io/acme/api:1.0.0

# Limit resources
docker run -d --name api \
  --cpus 1.0 --memory 512m --memory-swap 512m \
  ghcr.io/acme/api:1.0.0

# Connect to a custom network
docker run -d --network app-net --name redis redis:7

# Override the entrypoint / cmd
docker run --rm node:20 node -e 'console.log("hi")'
docker run --rm --entrypoint sh node:20 -c 'env'

# Read-only root filesystem with a writable tmpfs (security hardening)
docker run -d --read-only --tmpfs /tmp ghcr.io/acme/api:1.0.0
</code></pre>
<p><strong>Frequently used flags:</strong></p>
<table>
<tr><th>Flag</th><th>Effect</th></tr>
<tr><td><code>-d</code></td><td>Detached (background)</td></tr>
<tr><td><code>-it</code></td><td>Interactive + TTY (for shells)</td></tr>
<tr><td><code>--rm</code></td><td>Auto-remove on exit (no clutter)</td></tr>
<tr><td><code>-p HOST:CONT</code></td><td>Publish a port</td></tr>
<tr><td><code>-e KEY=VAL</code></td><td>Set an env var</td></tr>
<tr><td><code>--env-file .env</code></td><td>Load env from file</td></tr>
<tr><td><code>-v HOST:CONT</code></td><td>Bind mount (host path)</td></tr>
<tr><td><code>-v vol:CONT</code></td><td>Named volume (Docker-managed)</td></tr>
<tr><td><code>--network NAME</code></td><td>Attach to a custom network</td></tr>
<tr><td><code>--restart unless-stopped</code></td><td>Restart on crash + boot</td></tr>
<tr><td><code>--user 1000:1000</code></td><td>Run as non-root</td></tr>
<tr><td><code>--cap-drop=ALL</code></td><td>Drop Linux capabilities</td></tr>
<tr><td><code>--security-opt</code> / <code>--read-only</code></td><td>Security hardening</td></tr>
</table>
<p><strong>Lifecycle commands:</strong></p>
<pre><code>docker ps              # running containers
docker ps -a           # include stopped
docker logs -f api     # tail logs
docker exec -it api sh # shell into a running container
docker stop api && docker rm api
</code></pre>
<p><strong>For dev work,</strong> prefer <code>docker compose up</code> over many ad-hoc <code>docker run</code> commands &mdash; the Compose file is reproducible and version-controlled. For prod, prefer Kubernetes / ECS / Nomad over hand-managed <code>docker run</code> on hosts.</p>'''

ANSWERS[74] = r'''<p>Building and deploying a Node.js application via GitHub Actions typically combines: install &rarr; test &rarr; build a Docker image &rarr; push to a registry &rarr; deploy to a target (K8s / ECS / Cloud Run / SSH host).</p>
<p><strong>Full example: build &amp; deploy to a managed K8s cluster:</strong></p>
<pre><code># .github/workflows/deploy.yml
name: Build and Deploy
on:
  push: { branches: [main] }

permissions:
  contents: read
  packages: write
  id-token: write   # OIDC for cloud auth

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test
      - run: npm run build

      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest,enable={{is_default_branch}}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production    # adds approval + secret scoping
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gh-deploy
          aws-region: us-east-1
      - run: aws eks update-kubeconfig --name prod
      - run: |
          kubectl set image deployment/api \
            api=${{ needs.build.outputs.image }}
          kubectl rollout status deployment/api --timeout=5m
</code></pre>
<p><strong>Companion <code>Dockerfile</code> using multi-stage:</strong></p>
<pre><code>FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
USER node
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/server.js"]
</code></pre>
<p><strong>Key practices:</strong></p>
<ul>
<li><strong>OIDC auth</strong> &mdash; <code>aws-actions/configure-aws-credentials</code> exchanges a short-lived OIDC token for AWS credentials; no long-lived keys in secrets.</li>
<li><strong>Image immutable tag</strong> = <code>github.sha</code>; the moving <code>:latest</code> is for humans only.</li>
<li><strong>GitHub Environments</strong> with required reviewers gate prod deploys.</li>
<li><strong>Buildx cache</strong> (<code>type=gha</code>) caches Docker layers in the GitHub cache for 5&times; faster rebuilds.</li>
<li><strong>Other deploy targets</strong>: Vercel / Render / Fly use a single CLI step; ECS uses <code>aws-actions/amazon-ecs-deploy-task-definition</code>; Cloud Run uses <code>google-github-actions/deploy-cloudrun</code>.</li>
</ul>'''

ANSWERS[75] = r'''<p>The <strong>Jenkins Job DSL</strong> plugin lets you describe Jenkins jobs in Groovy code instead of clicking through the UI. A &ldquo;seed job&rdquo; runs the DSL script and creates / updates the actual jobs &mdash; classic <em>jobs as code</em>.</p>
<p><strong>Example DSL script (<code>jobs/dsl.groovy</code>):</strong></p>
<pre><code>// Generate a freestyle job
job('acme/api-build') {
  description('Builds the acme API on every push')
  scm {
    git {
      remote { url('https://github.com/acme/api.git') }
      branch('main')
    }
  }
  triggers { githubPush() }
  steps {
    shell('npm ci && npm test && docker build -t api .')
  }
  publishers {
    archiveJunit('test-results/**/*.xml')
    slackNotifier { room('#ci') }
  }
}

// Generate a multibranch pipeline pointing to a Jenkinsfile
multibranchPipelineJob('acme/api') {
  branchSources {
    github {
      id('acme-api')
      repoOwner('acme')
      repository('api')
      scanCredentialsId('github-token')
    }
  }
  factory { workflowBranchProjectFactory { scriptPath('Jenkinsfile') } }
  orphanedItemStrategy {
    discardOldItems { numToKeep(20) }
  }
}

// Loop to generate one job per service
['api', 'web', 'worker'].each { svc -&gt;
  multibranchPipelineJob("acme/${svc}") {
    branchSources { github { repoOwner('acme'); repository(svc) } }
  }
}
</code></pre>
<p><strong>How it&rsquo;s wired up:</strong></p>
<ol>
<li>Install the <em>Job DSL</em> plugin.</li>
<li>Create one <strong>seed job</strong> manually (Freestyle, &ldquo;Process Job DSLs&rdquo; build step pointing at <code>jobs/*.groovy</code>).</li>
<li>Run the seed job &rarr; it materialises every job described in the script.</li>
<li>On every commit to the DSL repo, the seed re-runs &mdash; jobs are kept in sync.</li>
</ol>
<p><strong>Job DSL vs Pipeline DSL:</strong></p>
<table>
<tr><th></th><th>Job DSL</th><th>Pipeline DSL (Jenkinsfile)</th></tr>
<tr><td>Purpose</td><td>Defines <em>which jobs exist</em></td><td>Defines <em>what one job does</em></td></tr>
<tr><td>Lives in</td><td>Seed-job repo / Jenkins admin repo</td><td>Application repo</td></tr>
<tr><td>Replaces</td><td>Manual &ldquo;New Item&rdquo; clicks</td><td>Freestyle build steps</td></tr>
</table>
<p>You typically use both: Job DSL provisions the jobs; each provisioned job runs a Pipeline / Jenkinsfile.</p>
<p><strong>2026 alternatives:</strong> for fully declarative Jenkins setup, prefer <strong>JCasC</strong> (Jenkins Configuration as Code) for the Jenkins controller config plus <strong>Jenkinsfile</strong> per repo &mdash; many teams skip Job DSL entirely. For greenfield CI, GitHub Actions / GitLab CI / Buildkite have config-as-code as the default with no seed-job ceremony.</p>'''

ANSWERS[76] = r'''<p>Real organisations rarely run a single Kubernetes cluster &mdash; they split across environments (dev / staging / prod), regions (us-east / eu-west), or business units. Managing many clusters needs tooling beyond raw <code>kubectl</code>.</p>
<p><strong>Levels of multi-cluster management:</strong></p>
<ol>
<li><strong>Context switching</strong> &mdash; <code>kubectl config use-context prod-us</code>; fine for two or three clusters.</li>
<li><strong>GitOps</strong> &mdash; one Git repo defines the desired state of every cluster; an agent reconciles continuously. <em>This is the 2026 default.</em></li>
<li><strong>Multi-cluster control planes</strong> &mdash; one tool to view, deploy, and govern fleets of clusters.</li>
</ol>
<p><strong>GitOps options:</strong></p>
<table>
<tr><th>Tool</th><th>Notes</th></tr>
<tr><td><strong>Argo CD</strong></td><td>Most popular; great UI, ApplicationSet for fan-out across clusters.</td></tr>
<tr><td><strong>Flux</strong></td><td>CNCF graduated; component-based (kustomize / helm / image-update controllers).</td></tr>
<tr><td><strong>Argo CD ApplicationSet</strong></td><td>Generate one Argo Application per cluster from a list / cluster generator.</td></tr>
</table>
<p><strong>Argo CD ApplicationSet example &mdash; deploy <code>api</code> to all clusters tagged <code>env=prod</code>:</strong></p>
<pre><code>apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: api }
spec:
  generators:
    - clusters:
        selector: { matchLabels: { env: prod } }
  template:
    metadata: { name: 'api-{{name}}' }
    spec:
      project: default
      source:
        repoURL: https://github.com/acme/manifests
        path: 'apps/api/overlays/{{name}}'
      destination:
        server: '{{server}}'
        namespace: api
      syncPolicy:
        automated: { selfHeal: true, prune: true }
</code></pre>
<p><strong>Multi-cluster control planes:</strong></p>
<ul>
<li><strong>Rancher</strong> &mdash; SUSE&rsquo;s OSS multi-cluster manager; one UI for many clusters across clouds, integrated RBAC.</li>
<li><strong>Karmada</strong> &mdash; CNCF; multi-cluster scheduling and propagation.</li>
<li><strong>Cluster API</strong> &mdash; Kubernetes-native cluster lifecycle (provision / upgrade / delete).</li>
<li><strong>Crossplane</strong> &mdash; control plane for clusters and any cloud resource as Kubernetes objects.</li>
<li><strong>Anthos / EKS Anywhere / Azure Arc</strong> &mdash; cloud-vendor solutions for hybrid + multi-cloud fleets.</li>
</ul>
<p><strong>Cross-cluster networking and traffic:</strong> <strong>Submariner</strong>, <strong>Cilium Cluster Mesh</strong>, <strong>Istio multi-cluster</strong>, or app-layer multi-cluster ingress (AWS Global Accelerator, GCP Multi-Cluster Ingress) for failover and global routing.</p>
<p><strong>Observability across clusters:</strong> ship metrics / logs / traces to a single backend &mdash; <strong>Grafana Cloud</strong>, <strong>Datadog</strong>, <strong>Honeycomb</strong>, or self-hosted <strong>Thanos</strong> / <strong>Mimir</strong> for federated Prometheus.</p>
<p><strong>Best practice:</strong> treat clusters as cattle &mdash; the Git repo, not the cluster, is the source of truth. Provision new clusters via Terraform / Crossplane, bootstrap them with Argo CD / Flux, and let GitOps fill them in. A lost cluster should be replaceable in minutes.</p>'''

ANSWERS[77] = r'''<p><strong>Docker Hub</strong> (<code>hub.docker.com</code>) is Docker&rsquo;s original and largest public image registry. It hosts <em>millions</em> of images: official base images (node, python, postgres, nginx), vendor images, and community/personal images.</p>
<p><strong>Three image categories:</strong></p>
<table>
<tr><th>Category</th><th>Example</th><th>Notes</th></tr>
<tr><td><strong>Official Images</strong></td><td><code>node</code>, <code>python</code>, <code>postgres</code></td><td>Curated by Docker; security-patched; the canonical base for most Dockerfiles.</td></tr>
<tr><td><strong>Verified Publisher</strong></td><td><code>microsoft/...</code>, <code>nvidia/...</code></td><td>Vendor-published, trustworthy.</td></tr>
<tr><td><strong>Community</strong></td><td><code>jdoe/myapp</code></td><td>Anyone can publish; review before using.</td></tr>
</table>
<p><strong>Basic usage:</strong></p>
<pre><code>docker login                              # log in (caches token in ~/.docker/config.json)
docker pull node:20-alpine                # pull an official image
docker tag myapp:1.0 acme/myapp:1.0       # tag for your account
docker push acme/myapp:1.0                # push to Hub
docker search prometheus                  # search images
</code></pre>
<p><strong>Important caveats in 2026:</strong></p>
<ul>
<li><strong>Anonymous pull rate limits</strong> &mdash; 100 pulls per 6 hours per IP. Authenticated free accounts: 200/6h. Paid: unlimited. CI runners commonly hit this; <em>always log in</em> in CI, even with a free account.</li>
<li><strong>Repository limits</strong> &mdash; free accounts: unlimited public repos, only one private repo. Paid plans for more.</li>
<li><strong>Old/abandoned images</strong> &mdash; verify the publisher and last-updated date; many community images are unmaintained and contain critical CVEs.</li>
</ul>
<p><strong>Alternatives many teams now prefer:</strong></p>
<ul>
<li><strong>GitHub Container Registry (GHCR)</strong> &mdash; free for public, integrated with GitHub auth, no Hub rate limits.</li>
<li><strong>AWS ECR Public Gallery</strong> &mdash; rate-limit-free pulls, hosted by AWS.</li>
<li><strong>Cloud-vendor private registries</strong> (ECR, Artifact Registry, ACR) &mdash; closer to where workloads run, IAM-controlled.</li>
</ul>
<p><strong>Best practices when using Hub:</strong></p>
<ul>
<li>Pin to a specific digest for reproducibility: <code>FROM node:20-alpine@sha256:abc...</code>.</li>
<li>Prefer <em>distroless</em> or <em>chainguard</em> base images for production &mdash; smaller surface, fewer CVEs.</li>
<li>Scan images on push: Hub&rsquo;s built-in scan, <strong>Trivy</strong>, <strong>Snyk</strong>, <strong>Grype</strong>.</li>
<li>Sign images with <strong>Sigstore Cosign</strong> and verify at deploy.</li>
<li>Configure registry mirroring (e.g. AWS ECR pull-through cache) to dodge rate limits and centralise scanning.</li>
</ul>'''

ANSWERS[78] = r'''<p>Continuous Deployment with GitHub Actions means: every commit to <code>main</code> that passes CI is <em>automatically</em> released to production with no human click. Continuous <em>Delivery</em> uses the same pipeline but adds a manual approval gate before prod.</p>
<p><strong>Building blocks:</strong></p>
<ol>
<li><strong>Branching strategy</strong> &mdash; trunk-based: feature branches &rarr; PR &rarr; squash merge to <code>main</code>.</li>
<li><strong>Branch protection</strong> &mdash; <code>main</code> requires green CI + reviewers, no direct pushes.</li>
<li><strong>Automated tests</strong> &mdash; lint / unit / integration / e2e all pass on PR and on <code>main</code>.</li>
<li><strong>Environments</strong> with secrets and (optionally) required reviewers.</li>
<li><strong>Promotion strategy</strong> &mdash; one workflow per environment, or one workflow with sequential jobs.</li>
</ol>
<p><strong>Sequential dev &rarr; staging &rarr; prod with approval before prod:</strong></p>
<pre><code>name: Deploy
on:
  push: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps: [ ... ]   # build, test, build image, push

  deploy-staging:
    needs: test
    environment: staging        # auto-deploy to staging
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh staging

  smoke-staging:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - run: npx playwright test --config staging.config.ts

  deploy-prod:
    needs: smoke-staging
    environment: production     # ← required reviewers gate
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh prod

  smoke-prod:
    needs: deploy-prod
    runs-on: ubuntu-latest
    steps:
      - run: npx playwright test --config prod.config.ts
</code></pre>
<p><strong>GitHub Environments give you:</strong></p>
<ul>
<li><strong>Required reviewers</strong> &mdash; only listed users / teams can approve a deploy.</li>
<li><strong>Wait timer</strong> &mdash; force a delay (e.g. 15 min) for canary observation.</li>
<li><strong>Environment secrets</strong> &mdash; <code>PROD_DB_URL</code> visible only in the prod job.</li>
<li><strong>Deployment branches</strong> &mdash; restrict deploys to <code>main</code> only.</li>
</ul>
<p><strong>Safe-deploy patterns to layer on:</strong></p>
<ul>
<li><strong>Feature flags</strong> (LaunchDarkly / Statsig / GrowthBook / PostHog / Unleash) decouple deploy from release.</li>
<li><strong>Canary / blue-green</strong> via Argo Rollouts (K8s), AWS CodeDeploy (ECS), Cloudflare/Vercel preview &rarr; promote.</li>
<li><strong>Automatic rollback</strong> on error-rate or latency SLO breach (Datadog Watchdog, custom k8s-rollout-controllers).</li>
<li><strong>Smoke tests post-deploy</strong> &mdash; fail the workflow on regression.</li>
<li><strong>Synthetic checks</strong> &mdash; Datadog Synthetics / Checkly / Grafana k6 verifying end-user paths every minute.</li>
</ul>
<p><strong>Dora-metric instrumentation</strong> (deployment frequency, lead time, MTTR, change failure rate) helps the team measure whether CD is actually making things better.</p>'''

ANSWERS[79] = r'''<p>A <strong>stage</strong> in a Jenkins pipeline groups related steps under a name &mdash; it&rsquo;s the unit shown as a coloured block in Blue Ocean / Pipeline Graph. Stages give visual structure, parallelism, and conditional execution.</p>
<p><strong>Anatomy:</strong></p>
<pre><code>pipeline {
  agent any
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Build')    { steps { sh 'npm ci && npm run build' } }

    stage('Test') {
      parallel {
        stage('Unit')        { steps { sh 'npm test' } }
        stage('Lint')        { steps { sh 'npm run lint' } }
        stage('Type-check')  { steps { sh 'npm run typecheck' } }
      }
    }

    stage('Docker Build &amp; Push') {
      when { branch 'main' }                       // only on main
      steps {
        sh 'docker build -t ghcr.io/acme/api:$BUILD_NUMBER .'
        withCredentials([usernamePassword(credentialsId:'ghcr', usernameVariable:'U', passwordVariable:'P')]) {
          sh 'echo $P | docker login ghcr.io -u $U --password-stdin'
          sh 'docker push ghcr.io/acme/api:$BUILD_NUMBER'
        }
      }
    }

    stage('Deploy to Prod') {
      when { branch 'main' }
      input {
        message 'Deploy to production?'
        ok 'Deploy'
        submitter 'release-managers'              // only this group can approve
      }
      steps {
        sh './scripts/deploy.sh prod $BUILD_NUMBER'
      }
    }
  }
  post {
    success { slackSend(channel: '#deploys', message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER}") }
    failure { slackSend(channel: '#deploys', message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER}") }
  }
}
</code></pre>
<p><strong>Common stage features:</strong></p>
<ul>
<li><strong><code>steps { }</code></strong> &mdash; the actions performed in the stage.</li>
<li><strong><code>when { }</code></strong> &mdash; conditional execution (<code>branch</code>, <code>changeset</code>, <code>environment name: ...</code>, <code>expression { }</code>).</li>
<li><strong><code>parallel { }</code></strong> &mdash; sub-stages that run concurrently.</li>
<li><strong><code>input { }</code></strong> &mdash; pause for human approval (manual gate).</li>
<li><strong><code>options { }</code></strong> &mdash; per-stage timeout, retry, skip-default-checkout.</li>
<li><strong><code>environment { }</code></strong> &mdash; per-stage env vars / credentials.</li>
<li><strong><code>agent { }</code></strong> &mdash; override the pipeline-level agent (different label / docker image / kubernetes pod per stage).</li>
<li><strong><code>post { }</code></strong> &mdash; <code>always</code> / <code>success</code> / <code>failure</code> / <code>changed</code> hooks.</li>
</ul>
<p><strong>Best-practice stage layout:</strong> <em>Checkout &rarr; Build &rarr; Test (parallel) &rarr; Package &rarr; Publish &rarr; Deploy &rarr; Smoke</em>. Keep each stage focused on one concern so the timeline shows clearly where time is spent and where failures happen. Use <code>options { timeout(time: 10, unit: 'MINUTES') }</code> on each stage to bound runaway jobs.</p>'''

ANSWERS[80] = r'''<p>A <strong>DaemonSet</strong> ensures that exactly one copy of a Pod runs on every (or every selected) node in the cluster. It&rsquo;s the right tool for <em>node-level agents</em> &mdash; things that must observe / serve / manage every host.</p>
<p><strong>Typical uses:</strong></p>
<ul>
<li><strong>Log shippers</strong> &mdash; Fluent Bit, Vector, Filebeat tailing <code>/var/log/containers</code> on each node.</li>
<li><strong>Node-level monitoring</strong> &mdash; <code>node-exporter</code>, Datadog Agent, New Relic, Falco for runtime security.</li>
<li><strong>Networking</strong> &mdash; Cilium / Calico / Flannel CNI agents, kube-proxy.</li>
<li><strong>Storage</strong> &mdash; CSI node plugins (EBS / EFS / GCE PD).</li>
<li><strong>GPU drivers</strong> &mdash; NVIDIA device plugin.</li>
</ul>
<p><strong>Example &mdash; Fluent Bit log forwarder:</strong></p>
<pre><code>apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels: { app: fluent-bit }
  template:
    metadata:
      labels: { app: fluent-bit }
    spec:
      tolerations:
        - operator: Exists                  # run on tainted nodes too (e.g. control plane)
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:3.1
          resources:
            requests: { cpu: 50m, memory: 64Mi }
            limits:   { cpu: 200m, memory: 256Mi }
          volumeMounts:
            - name: varlog
              mountPath: /var/log
              readOnly: true
            - name: containers
              mountPath: /var/lib/docker/containers
              readOnly: true
      volumes:
        - name: varlog
          hostPath: { path: /var/log }
        - name: containers
          hostPath: { path: /var/lib/docker/containers }
</code></pre>
<p><strong>Targeting a subset of nodes:</strong> use a <code>nodeSelector</code> or <code>affinity</code> rule:</p>
<pre><code>spec:
  template:
    spec:
      nodeSelector:
        gpu: 'true'           # only nodes labelled gpu=true
</code></pre>
<p><strong>How DaemonSets differ from other workloads:</strong></p>
<table>
<tr><th>Workload</th><th>Replication</th><th>Use</th></tr>
<tr><td><strong>Deployment</strong></td><td>N replicas, scheduler decides where</td><td>Stateless apps</td></tr>
<tr><td><strong>StatefulSet</strong></td><td>N replicas, stable identity / storage</td><td>Databases, queues</td></tr>
<tr><td><strong>DaemonSet</strong></td><td>One per node (filtered)</td><td>Per-node agents</td></tr>
<tr><td><strong>Job / CronJob</strong></td><td>Run-to-completion</td><td>Batch / scheduled tasks</td></tr>
</table>
<p><strong>Update strategy:</strong> DaemonSets default to <code>RollingUpdate</code>, replacing one Pod per node at a time, controlled by <code>maxUnavailable</code>. Use <code>OnDelete</code> for manual control on sensitive node agents (CSI, CNI).</p>
<p><strong>Operational tips:</strong> set tight resource <code>requests</code>/<code>limits</code> &mdash; a DaemonSet leak burns capacity on every node. Add <code>priorityClassName: system-node-critical</code> for agents that must not be evicted under pressure. Use Pod Disruption Budgets if rolling updates risk losing too many node agents at once.</p>'''

ANSWERS[81] = r'''<p>Tagging a Docker image gives it a human-friendly name (and a registry path) so it can be pushed, pulled, and referenced. The full reference is <code>registry/namespace/repo:tag</code>; if you omit pieces, Docker fills in defaults (<code>docker.io/library/...:latest</code>).</p>
<p><strong>Tagging at build time:</strong></p>
<pre><code># Build and tag in one step
docker build -t acme/api:1.2.3 .

# Multiple tags at once
docker build \
  -t ghcr.io/acme/api:1.2.3 \
  -t ghcr.io/acme/api:1.2 \
  -t ghcr.io/acme/api:latest \
  -t ghcr.io/acme/api:$(git rev-parse --short HEAD) \
  .
</code></pre>
<p><strong>Tagging an existing image:</strong></p>
<pre><code>docker tag api:1.2.3 ghcr.io/acme/api:1.2.3
docker push ghcr.io/acme/api:1.2.3
</code></pre>
<p><strong>Tag-naming strategy</strong> &mdash; choose <em>at least</em> two:</p>
<table>
<tr><th>Tag style</th><th>Example</th><th>Use</th></tr>
<tr><td>Semantic version</td><td><code>:1.2.3</code></td><td>Releases &mdash; immutable, points to a specific build</td></tr>
<tr><td>Major / minor</td><td><code>:1.2</code>, <code>:1</code></td><td>Floating &mdash; latest patch in that line</td></tr>
<tr><td>Git SHA</td><td><code>:a1b2c3d</code></td><td>Per-commit &mdash; perfect for CI builds &amp; rollback</td></tr>
<tr><td>Branch</td><td><code>:main</code>, <code>:dev</code></td><td>Floating &mdash; latest of that branch</td></tr>
<tr><td>Date</td><td><code>:2026-05-02</code></td><td>Daily nightlies</td></tr>
<tr><td><code>:latest</code></td><td>(default)</td><td>Floating &mdash; mostly for humans, never for prod manifests</td></tr>
</table>
<p><strong>Critical pitfalls:</strong></p>
<ul>
<li><strong>Tags are mutable.</strong> Anyone with push access can re-tag. Production manifests should reference an <em>immutable</em> tag (semver or SHA) <em>or</em> a digest (<code>image@sha256:...</code>).</li>
<li><strong><code>:latest</code> in production is dangerous</strong> &mdash; rolling restarts can pull a different image than what you tested. Use it for local dev only.</li>
<li><strong>Pinning by digest</strong> is the strongest guarantee: <code>FROM node:20-alpine@sha256:abc...</code> &mdash; the layer is byte-identical forever.</li>
</ul>
<p><strong>In CI</strong> use <code>docker/metadata-action@v5</code> to generate consistent tags automatically:</p>
<pre><code>- uses: docker/metadata-action@v5
  with:
    images: ghcr.io/acme/api
    tags: |
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=sha,prefix=
      type=ref,event=branch
</code></pre>
<p>This gives you semver tags on releases, SHA tags on every push, and branch tags for previews &mdash; all without hand-rolling tag logic.</p>'''

ANSWERS[82] = r'''<p>Setting up CI/CD for Python with GitHub Actions covers: install dependencies (with caching), lint, type-check, test (with coverage), build a wheel or Docker image, and deploy.</p>
<p><strong>Modern Python project (Ruff + uv + pytest + Docker):</strong></p>
<pre><code># .github/workflows/python.yml
name: Python CI/CD
on:
  push: { branches: [main] }
  pull_request:

permissions:
  contents: read
  packages: write
  id-token: write

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python: ['3.11', '3.12', '3.13']
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: pw, POSTGRES_DB: test }
        ports: [5432:5432]
        options: --health-cmd "pg_isready -U postgres"
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv python install ${{ matrix.python }}
      - run: uv sync --all-extras
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src
      - run: uv run pytest --cov=src --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:pw@localhost:5432/test
      - uses: codecov/codecov-action@v4

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  publish-to-pypi:
    if: startsWith(github.ref, 'refs/tags/v')
    needs: test
    runs-on: ubuntu-latest
    environment: pypi          # required reviewers + OIDC trust
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1
        # OIDC: no token needed, configure trusted publisher in PyPI
</code></pre>
<p><strong>Companion <code>Dockerfile</code> for a Python web app:</strong></p>
<pre><code>FROM python:3.13-slim AS base
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
RUN uv sync --frozen --no-dev
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
</code></pre>
<p><strong>Tooling notes:</strong></p>
<ul>
<li><strong>uv</strong> (Astral) replaces pip + pip-tools + virtualenv with one extremely fast binary; standard for new Python projects in 2026.</li>
<li><strong>Ruff</strong> replaces flake8 + black + isort + many plugins &mdash; one tool, &lt;1 s on most repos.</li>
<li><strong>Pytest</strong> + <strong>pytest-asyncio</strong> + <strong>coverage</strong> for tests; <strong>Hypothesis</strong> for property-based.</li>
<li><strong>mypy</strong> or <strong>pyright</strong>/<strong>ty</strong> for static typing.</li>
<li><strong>PyPI Trusted Publishing</strong> &mdash; OIDC-based, no API tokens stored in GitHub.</li>
</ul>'''

ANSWERS[83] = r'''<p><strong>Pipelines as Code (PaC)</strong> means defining your CI/CD pipeline in a file checked into the repo, instead of clicking through a UI. In Jenkins this means a <strong>Jenkinsfile</strong> at the repo root that declares the pipeline using Groovy DSL.</p>
<p><strong>Why it matters:</strong></p>
<ul>
<li><strong>Versioned</strong> &mdash; the pipeline lives next to the code; old commits build with the pipeline that was current at the time.</li>
<li><strong>Reviewable</strong> &mdash; pipeline changes go through PR review like any code change.</li>
<li><strong>Reproducible</strong> &mdash; restoring a Jenkins instance from scratch is a clone + run, not a re-click of every job.</li>
<li><strong>Multi-branch</strong> &mdash; each branch can have its own Jenkinsfile, so refactors are testable.</li>
</ul>
<p><strong>Two Jenkins flavours:</strong></p>
<table>
<tr><th></th><th>Declarative</th><th>Scripted</th></tr>
<tr><td>Style</td><td>Structured DSL with <code>pipeline { stages { stage { } } }</code></td><td>Free-form Groovy with <code>node { }</code></td></tr>
<tr><td>Validation</td><td>Lint via <code>jenkins-cli declarative-linter</code></td><td>Runtime errors only</td></tr>
<tr><td>Recommended</td><td>✅ Yes &mdash; for almost all use cases</td><td>Only when full Groovy control is needed</td></tr>
</table>
<p><strong>Declarative Jenkinsfile:</strong></p>
<pre><code>pipeline {
  agent any
  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }
  environment { CI = 'true' }
  stages {
    stage('Test')   { steps { sh 'npm ci && npm test' } }
    stage('Build')  { steps { sh 'docker build -t api .' } }
    stage('Deploy') {
      when { branch 'main' }
      steps { sh './deploy.sh' }
    }
  }
}
</code></pre>
<p><strong>Setup steps:</strong></p>
<ol>
<li>Add a <code>Jenkinsfile</code> to the repo root.</li>
<li>In Jenkins, create a <strong>Multibranch Pipeline</strong> job pointing at the repo.</li>
<li>Jenkins auto-discovers branches and PRs, runs the Jenkinsfile from each.</li>
</ol>
<p><strong>Shared libraries</strong> let teams DRY up common stages across many repos:</p>
<pre><code>// In a separate Git repo, src/com/acme/Pipeline.groovy
def call(Map config) {
  pipeline {
    agent any
    stages {
      stage('Test')  { steps { sh "npm test" } }
      stage('Build') { steps { sh "docker build -t ${config.image} ." } }
    }
  }
}

// In any service&rsquo;s Jenkinsfile
@Library('acme-pipeline') _
acmePipeline(image: 'acme/api')
</code></pre>
<p><strong>2026 reality:</strong> &ldquo;Pipelines as Code&rdquo; is now the universal default &mdash; <strong>GitHub Actions</strong> (<code>.github/workflows/*.yml</code>), <strong>GitLab CI</strong> (<code>.gitlab-ci.yml</code>), <strong>CircleCI</strong> (<code>.circleci/config.yml</code>), <strong>Buildkite</strong>, <strong>Tekton</strong> all follow the same pattern. UI-clicked pipelines are considered legacy.</p>'''

ANSWERS[84] = r'''<p>A <strong>StatefulSet</strong> manages Pods that need a stable identity, stable storage, and ordered lifecycle &mdash; databases, queues, leader-elected services. Unlike a Deployment, each replica gets a sticky name (<code>db-0</code>, <code>db-1</code>, <code>db-2</code>) and its own PersistentVolumeClaim that survives restarts.</p>
<p><strong>Three guarantees a StatefulSet provides:</strong></p>
<table>
<tr><th>Guarantee</th><th>Mechanism</th></tr>
<tr><td>Stable network identity</td><td>Each Pod gets DNS <code>db-0.db.ns.svc.cluster.local</code> via a headless Service.</td></tr>
<tr><td>Stable storage</td><td><code>volumeClaimTemplates</code> creates one PVC per Pod, kept across restarts.</td></tr>
<tr><td>Ordered ops</td><td>Pods come up and roll updates in order; <code>db-1</code> waits for <code>db-0</code> to be Ready.</td></tr>
</table>
<p><strong>Example &mdash; a 3-node MongoDB ReplicaSet:</strong></p>
<pre><code>apiVersion: v1
kind: Service
metadata: { name: mongo, namespace: db }
spec:
  clusterIP: None        # headless &mdash; required for StatefulSet
  selector: { app: mongo }
  ports: [ { port: 27017 } ]
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: mongo, namespace: db }
spec:
  serviceName: mongo
  replicas: 3
  selector: { matchLabels: { app: mongo } }
  template:
    metadata: { labels: { app: mongo } }
    spec:
      containers:
        - name: mongo
          image: mongo:7
          ports: [ { containerPort: 27017 } ]
          volumeMounts:
            - name: data
              mountPath: /data/db
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: gp3
        resources: { requests: { storage: 50Gi } }
</code></pre>
<p>Each Pod gets a stable hostname (<code>mongo-0</code>, <code>mongo-1</code>, <code>mongo-2</code>), a dedicated PVC (<code>data-mongo-0</code>, etc.), and a deterministic DNS name &mdash; the database can configure replication to its peers reliably.</p>
<p><strong>Update strategies:</strong></p>
<ul>
<li><code>RollingUpdate</code> (default) &mdash; reverse ordinal order: <code>db-2</code> first, then <code>db-1</code>, then <code>db-0</code>.</li>
<li><code>OnDelete</code> &mdash; nothing happens until you delete a Pod manually; useful for stateful systems where you want full control.</li>
<li><code>partition: N</code> &mdash; only update Pods with ordinal &ge; N; enables canary updates.</li>
</ul>
<p><strong>StatefulSet vs Deployment:</strong></p>
<table>
<tr><th></th><th>Deployment</th><th>StatefulSet</th></tr>
<tr><td>Pod name</td><td>Random suffix</td><td>Stable: name-0, name-1, ...</td></tr>
<tr><td>Storage</td><td>Shared or none</td><td>Per-Pod PVC, persists across restarts</td></tr>
<tr><td>Scaling</td><td>Parallel</td><td>Ordered</td></tr>
<tr><td>Use</td><td>Stateless apps</td><td>Databases, message queues, ZK/etcd-like quorum systems</td></tr>
</table>
<p><strong>2026 advice:</strong> for production databases, prefer <strong>managed services</strong> (Atlas, RDS, Cloud SQL, ElastiCache) over self-hosted StatefulSets &mdash; you avoid backups, upgrades, replication, and certificate rotation. Reach for StatefulSets when no managed option exists, you have specific compliance / data-sovereignty needs, or you&rsquo;re running a Kafka / Cassandra / Elasticsearch where Operators (Strimzi, K8ssandra, ECK) automate the lifecycle.</p>'''

ANSWERS[85] = r'''<p>Pulling an image from Docker Hub downloads its layers to your local Docker daemon&rsquo;s storage. <code>docker run</code> pulls implicitly if the image is missing; <code>docker pull</code> fetches without running.</p>
<p><strong>Basic syntax:</strong></p>
<pre><code>docker pull node:20-alpine            # specific tag
docker pull node                       # implicit :latest &mdash; avoid
docker pull docker.io/library/node:20  # fully-qualified
docker pull node:20-alpine@sha256:abc  # by digest (immutable)
</code></pre>
<p>For private repositories you must authenticate first:</p>
<pre><code>docker login                  # interactive (Docker Hub default)
docker login -u USER --password-stdin &lt;&lt;&lt; "$TOKEN"
docker pull acme/private-app:1.0.0
docker logout                  # remove cached creds
</code></pre>
<p>Credentials are cached in <code>~/.docker/config.json</code> by default. On servers, use a <strong>credential helper</strong> (osxkeychain, secretservice, pass, or cloud-vendor helpers like <code>docker-credential-ecr-login</code>) so tokens aren&rsquo;t stored in plaintext.</p>
<p><strong>Pull policies in Kubernetes:</strong></p>
<table>
<tr><th>Policy</th><th>Behaviour</th></tr>
<tr><td><code>Always</code></td><td>Pull on every Pod start (default for <code>:latest</code>)</td></tr>
<tr><td><code>IfNotPresent</code></td><td>Use cached if present (default for tagged versions)</td></tr>
<tr><td><code>Never</code></td><td>Use only the cached image; fail if missing</td></tr>
</table>
<p>For private registries in K8s, create an <code>imagePullSecret</code>:</p>
<pre><code>kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=USER \
  --docker-password=$GITHUB_TOKEN \
  --namespace api

# Reference it in the Pod spec
spec:
  imagePullSecrets:
    - name: ghcr-creds
  containers: [ { name: api, image: ghcr.io/acme/private:1.0.0 } ]
</code></pre>
<p><strong>Anonymous pull rate limits</strong> on Docker Hub (100/6h per IP) trip up CI runners constantly. Mitigations:</p>
<ul>
<li><strong>Authenticate in CI</strong> &mdash; even a free Docker Hub account doubles the limit.</li>
<li><strong>Pull-through cache</strong> &mdash; AWS ECR, GCP Artifact Registry, and Harbor all support proxying Docker Hub on the first miss and serving from local cache thereafter.</li>
<li><strong>Mirror official images</strong> in your internal registry.</li>
<li><strong>Cache layers in CI</strong> &mdash; <code>docker/build-push-action</code> with <code>cache-from: type=gha</code> avoids re-downloading layers across runs.</li>
</ul>
<p><strong>Verify what you pulled</strong> with <code>docker inspect IMAGE</code> or <code>docker history IMAGE</code> &mdash; useful for catching unexpected base-image changes when something pinned to <code>:latest</code> goes wrong.</p>'''

ANSWERS[86] = r'''<p>Configuring GitHub Actions for a Java project is a matter of: choose a JDK version, run Maven or Gradle, cache dependencies, run tests, optionally build a JAR / container, deploy.</p>
<p><strong>Maven example:</strong></p>
<pre><code># .github/workflows/maven.yml
name: Java CI
on:
  push: { branches: [main] }
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        java: ['17', '21']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin    # Adoptium / Eclipse Temurin (recommended)
          java-version: ${{ matrix.java }}
          cache: maven
      - run: mvn -B verify
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: surefire-reports-jdk${{ matrix.java }}
          path: '**/target/surefire-reports/'

  build-and-publish:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 21, cache: maven }
      - run: mvn -B package -DskipTests
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
</code></pre>
<p><strong>Gradle equivalent:</strong></p>
<pre><code>      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew build --no-daemon
</code></pre>
<p><strong>Companion multi-stage <code>Dockerfile</code> using a small JRE base:</strong></p>
<pre><code>FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY pom.xml .
RUN mvn -B dependency:go-offline
COPY src ./src
RUN mvn -B package -DskipTests

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /src/target/*.jar app.jar
USER 1000:1000
EXPOSE 8080
CMD ["java", "-XX:MaxRAMPercentage=75", "-jar", "/app/app.jar"]
</code></pre>
<p><strong>Useful add-ons for Java pipelines:</strong></p>
<ul>
<li><strong>Spotless / Checkstyle / PMD / SpotBugs</strong> &mdash; linting and bug-pattern detection in CI.</li>
<li><strong>JaCoCo</strong> &mdash; code coverage reports; upload to Codecov / Coveralls / SonarCloud.</li>
<li><strong>SonarCloud / SonarQube</strong> &mdash; long-term code-quality trend tracking.</li>
<li><strong>Snyk / Dependabot / OWASP Dependency-Check</strong> &mdash; supply-chain vulnerability scanning.</li>
<li><strong>Maven publish</strong> &mdash; <code>actions/setup-java</code> can pre-fill <code>~/.m2/settings.xml</code> with creds for Maven Central / GitHub Packages.</li>
<li><strong>Native image</strong> &mdash; for GraalVM / Spring AOT, use <code>graalvm/setup-graalvm</code> and build native binaries.</li>
</ul>
<p><strong>Distribution choice:</strong> <strong>Eclipse Temurin</strong> (default), <strong>Microsoft Build of OpenJDK</strong>, <strong>Amazon Corretto</strong>, <strong>Azul Zulu</strong>, or <strong>GraalVM</strong> for native &mdash; all are free and supported. Avoid Oracle JDK for production unless you have a paid Oracle subscription.</p>'''

ANSWERS[87] = r'''<p>Jenkins schedules jobs using a slightly extended cron syntax. The trigger is configured per-job, in the UI under <em>Build Triggers &rarr; Build periodically</em>, or via Pipeline DSL.</p>
<p><strong>Cron syntax</strong>: <code>MIN HOUR DAY-OF-MONTH MONTH DAY-OF-WEEK</code></p>
<table>
<tr><th>Expression</th><th>Meaning</th></tr>
<tr><td><code>H * * * *</code></td><td>Once an hour, at a random minute (Jenkins picks)</td></tr>
<tr><td><code>H 2 * * *</code></td><td>Every day around 2 AM</td></tr>
<tr><td><code>H/15 * * * *</code></td><td>Every 15 minutes</td></tr>
<tr><td><code>H 9-17 * * 1-5</code></td><td>Hourly during business hours, weekdays</td></tr>
<tr><td><code>0 0 1 * *</code></td><td>First of every month at midnight</td></tr>
<tr><td><code>@daily</code> / <code>@weekly</code> / <code>@hourly</code></td><td>Aliases</td></tr>
</table>
<p><strong>Important &mdash; the <code>H</code> &ldquo;hash&rdquo; symbol:</strong> Jenkins-only; computes a stable random value from the job name to spread load. Use <code>H</code> instead of literal <code>0</code> in shared instances so 100 jobs don&rsquo;t all hammer the system at midnight.</p>
<p><strong>Two trigger types:</strong></p>
<table>
<tr><th>Trigger</th><th>Behaviour</th><th>Use</th></tr>
<tr><td><code>cron(...)</code></td><td>Run on schedule, regardless of changes</td><td>Nightly builds, dependency updates</td></tr>
<tr><td><code>pollSCM(...)</code></td><td>Poll Git on schedule, build only if commits</td><td>Legacy &mdash; <strong>prefer webhooks</strong></td></tr>
</table>
<p><strong>Declarative pipeline triggers:</strong></p>
<pre><code>pipeline {
  agent any
  triggers {
    cron('H 2 * * *')                    // nightly
    // pollSCM('H/5 * * * *')           // every 5 min, build if changed
    upstream(upstreamProjects: 'lib-build', threshold: hudson.model.Result.SUCCESS)
  }
  stages {
    stage('Build') { steps { sh 'mvn verify' } }
  }
}
</code></pre>
<p><strong>Common scheduling patterns:</strong></p>
<ul>
<li><strong>Nightly integration tests</strong> &mdash; full e2e suite that&rsquo;s too slow for every PR.</li>
<li><strong>Dependency updates</strong> &mdash; nightly <code>npm audit</code>, <code>mvn versions:display-dependency-updates</code>, or open Dependabot/Renovate PRs.</li>
<li><strong>Cleanup jobs</strong> &mdash; prune old workspaces, old Docker images, stale K8s namespaces.</li>
<li><strong>Backup jobs</strong> &mdash; nightly database/config snapshot to S3.</li>
<li><strong>Health checks</strong> &mdash; periodic synthetic monitoring of prod endpoints.</li>
</ul>
<p><strong>Manual job triggers</strong> in addition to schedule:</p>
<ul>
<li><strong>Webhooks</strong> &mdash; GitHub/GitLab push triggers (preferred over <code>pollSCM</code>).</li>
<li><strong>Parameterized builds</strong> &mdash; <em>Build with parameters</em> button in UI.</li>
<li><strong>Remote API</strong> &mdash; <code>curl -X POST https://jenkins/job/foo/buildWithParameters?token=ABC&amp;BRANCH=main</code>.</li>
<li><strong>Upstream / downstream</strong> &mdash; chain jobs so a successful library build triggers dependent service builds.</li>
</ul>
<p><strong>2026 alternative:</strong> for new scheduling needs, GitHub Actions <code>schedule:</code> trigger or workflow_dispatch is simpler and free; cron-on-cluster patterns now use <strong>Kubernetes CronJob</strong> for batch workloads, with <strong>Argo Workflows</strong> or <strong>Temporal</strong> for richer DAGs.</p>'''

ANSWERS[88] = r'''<p>A <strong>Kubernetes Operator</strong> is a controller that extends the Kubernetes API to manage a complex application as if it were a built-in resource. The pattern is: define a <em>Custom Resource Definition</em> (CRD), then write a controller that watches custom-resource objects and reconciles real-world state to match the spec.</p>
<p><strong>Why operators exist:</strong> built-in resources (Deployment, StatefulSet) handle generic Pod orchestration but can&rsquo;t manage application-specific lifecycle &mdash; backups, upgrades, replication, failover. An operator encodes a human SRE&rsquo;s playbook as software.</p>
<p><strong>Example mental model &mdash; the PostgreSQL Operator:</strong></p>
<pre><code>apiVersion: postgres-operator.crunchydata.com/v1beta1
kind: PostgresCluster
metadata: { name: app-db }
spec:
  postgresVersion: 16
  instances:
    - name: instance1
      replicas: 3
      dataVolumeClaimSpec:
        accessModes: [ReadWriteOnce]
        resources: { requests: { storage: 100Gi } }
  backups:
    pgbackrest:
      repos:
        - name: repo1
          s3: { bucket: backups, region: us-east-1, endpoint: s3.amazonaws.com }
</code></pre>
<p>This single resource tells the operator: &ldquo;run a 3-replica Postgres 16 cluster with continuous S3 backups.&rdquo; The operator&rsquo;s controllers create the StatefulSet, configure replication, schedule backups, manage failover, run major-version upgrades &mdash; all things you&rsquo;d otherwise script manually.</p>
<p><strong>Notable operators in 2026:</strong></p>
<table>
<tr><th>Domain</th><th>Operator</th></tr>
<tr><td>Postgres</td><td>CloudNativePG, Crunchy Postgres, Zalando Postgres</td></tr>
<tr><td>MySQL/MariaDB</td><td>Oracle MySQL, Vitess, Percona</td></tr>
<tr><td>MongoDB</td><td>MongoDB Enterprise Operator, Percona Server for MongoDB</td></tr>
<tr><td>Kafka</td><td>Strimzi (CNCF graduated)</td></tr>
<tr><td>Elastic stack</td><td>ECK</td></tr>
<tr><td>Cassandra</td><td>K8ssandra, Cass Operator</td></tr>
<tr><td>Redis</td><td>Redis Enterprise, Spotahome Redis</td></tr>
<tr><td>Prometheus</td><td>Prometheus Operator (kube-prometheus-stack)</td></tr>
<tr><td>Cert mgmt</td><td>cert-manager</td></tr>
<tr><td>External secrets</td><td>External Secrets Operator</td></tr>
<tr><td>GitOps</td><td>Argo CD, Flux</td></tr>
<tr><td>Cloud resources</td><td>AWS Controllers for Kubernetes (ACK), Crossplane, GCP Config Connector</td></tr>
</table>
<p><strong>Operator capability levels</strong> (the original CoreOS maturity model):</p>
<ol>
<li>Basic install</li>
<li>Seamless upgrades</li>
<li>Full lifecycle (backup, restore, scaling)</li>
<li>Deep insights (metrics, alerts)</li>
<li>Auto-pilot (auto-scaling, auto-tuning)</li>
</ol>
<p><strong>Building one</strong> usually means using the <strong>Operator SDK</strong>, <strong>Kubebuilder</strong>, or <strong>Metacontroller</strong> to scaffold a Go controller. <strong>OperatorHub.io</strong> is the catalog. <strong>OLM (Operator Lifecycle Manager)</strong> installs/upgrades operators on OpenShift; on vanilla K8s most teams just use Helm.</p>
<p><strong>2026 advice:</strong> install operators only when the lifecycle complexity justifies them. For greenfield apps, prefer <strong>managed services</strong> (Atlas, RDS, Confluent Cloud, Elastic Cloud) over running an operator yourself &mdash; you skip the upgrade-and-backup ops burden.</p>'''

ANSWERS[89] = r'''<p>A <strong>Dockerfile</strong> is the recipe that defines how to build an image. In a CI/CD pipeline it&rsquo;s the contract between &ldquo;source code&rdquo; and &ldquo;immutable runtime artifact&rdquo; &mdash; the same Dockerfile produces identical images across dev, CI, staging, and prod.</p>
<p><strong>Pipeline integration in three steps:</strong></p>
<ol>
<li><strong>Build</strong> the image from source.</li>
<li><strong>Scan</strong> for vulnerabilities and (optionally) sign it.</li>
<li><strong>Push</strong> to a registry; downstream stages deploy by reference.</li>
</ol>
<p><strong>GitHub Actions example:</strong></p>
<pre><code>jobs:
  docker:
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write, id-token: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true        # SLSA build provenance
          sbom: true              # software bill of materials
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          severity: HIGH,CRITICAL
          exit-code: 1            # fail the build on findings
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
</code></pre>
<p><strong>Production-grade Dockerfile patterns:</strong></p>
<pre><code># Multi-stage build keeps the runtime image small
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
USER nonroot
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist         ./dist
EXPOSE 3000
CMD ["dist/server.js"]
</code></pre>
<p><strong>Best practices:</strong></p>
<ul>
<li><strong>Multi-stage</strong> &mdash; final image contains only runtime artefacts, not build tools.</li>
<li><strong>Distroless / chainguard / wolfi</strong> base images &mdash; minimal CVE surface.</li>
<li><strong>Non-root user</strong> &mdash; <code>USER 1000</code> prevents root escapes.</li>
<li><strong>Pin base image by digest</strong> &mdash; reproducible across rebuilds.</li>
<li><strong>Order layers by churn</strong> &mdash; copy <code>package.json</code> + <code>npm ci</code> <em>before</em> <code>COPY . .</code> so dependency layers cache.</li>
<li><strong>BuildKit cache mounts</strong> &mdash; <code>RUN --mount=type=cache,target=/root/.npm npm ci</code> reuses package cache between builds.</li>
<li><strong>.dockerignore</strong> &mdash; exclude <code>.git</code>, <code>node_modules</code>, <code>__pycache__</code>, build outputs &mdash; keeps the build context tiny.</li>
<li><strong>Sign &amp; verify</strong> &mdash; Sigstore Cosign in CI and admission policy at deploy.</li>
<li><strong>Generate SBOM</strong> &mdash; for supply-chain compliance (SLSA, FedRAMP, EU CRA).</li>
</ul>'''

ANSWERS[90] = r'''<p>Deploying to AWS from GitHub Actions in 2026 means using <strong>OIDC trust</strong> instead of long-lived access keys. GitHub issues a short-lived OIDC token; AWS exchanges it for IAM role credentials valid for the workflow run. No secrets to rotate, leak-proof.</p>
<p><strong>One-time AWS setup:</strong></p>
<ol>
<li>Create an IAM <strong>OIDC identity provider</strong> for <code>token.actions.githubusercontent.com</code> (one per AWS account).</li>
<li>Create an IAM <strong>role</strong> with a trust policy that allows your repo&rsquo;s OIDC subject:</li>
</ol>
<pre><code>{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::ACCT:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike":   { "token.actions.githubusercontent.com:sub": "repo:acme/api:ref:refs/heads/main" }
    }
  }]
}
</code></pre>
<p>Attach the minimum permissions needed (e.g. ECR push + ECS deploy) to the role.</p>
<p><strong>The workflow:</strong></p>
<pre><code>name: Deploy
on:
  push: { branches: [main] }

permissions:
  contents: read
  id-token: write          # required for OIDC

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gh-deploy
          aws-region: us-east-1

      # Push image to ECR
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -t $ECR/api:${{ github.sha }} .
          docker push $ECR/api:${{ github.sha }}
        env:
          ECR: 123456789012.dkr.ecr.us-east-1.amazonaws.com

      # ECS rolling deploy
      - uses: aws-actions/amazon-ecs-render-task-definition@v1
        id: task
        with:
          task-definition: ecs/task-def.json
          container-name: api
          image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/api:${{ github.sha }}
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task.outputs.task-definition }}
          cluster: prod
          service: api
          wait-for-service-stability: true
</code></pre>
<p><strong>Common AWS deploy targets and the action that handles them:</strong></p>
<table>
<tr><th>Target</th><th>Action</th></tr>
<tr><td>ECR push</td><td><code>aws-actions/amazon-ecr-login</code></td></tr>
<tr><td>ECS service</td><td><code>aws-actions/amazon-ecs-deploy-task-definition</code></td></tr>
<tr><td>EKS</td><td>OIDC + <code>kubectl</code> + <code>aws eks update-kubeconfig</code></td></tr>
<tr><td>Lambda (zip)</td><td><code>aws lambda update-function-code</code></td></tr>
<tr><td>Lambda (container)</td><td>ECR push + <code>aws lambda update-function-code</code></td></tr>
<tr><td>S3 static site</td><td><code>aws s3 sync</code> + <code>aws cloudfront create-invalidation</code></td></tr>
<tr><td>CloudFormation</td><td><code>aws-actions/aws-cloudformation-github-deploy</code></td></tr>
<tr><td>SAM / CDK</td><td><code>sam deploy</code> / <code>cdk deploy</code></td></tr>
<tr><td>App Runner / Beanstalk</td><td>vendor-specific actions</td></tr>
</table>
<p><strong>Best practices:</strong> scope the IAM role tightly per repo and per environment (separate <code>gh-deploy-prod</code> vs <code>gh-deploy-staging</code>); pin OIDC subject claims to specific branches or environments; use <strong>GitHub Environments</strong> with required reviewers for prod; emit immutable image tags (Git SHA), not <code>:latest</code>; audit role usage via CloudTrail.</p>'''

ANSWERS[91] = r'''<p><strong>Jenkins Pipeline DSL</strong> is the Groovy-based domain-specific language used inside a <code>Jenkinsfile</code> to define the steps of a pipeline. It comes in two flavours:</p>
<table>
<tr><th></th><th>Declarative</th><th>Scripted</th></tr>
<tr><td>Top-level keyword</td><td><code>pipeline { }</code></td><td><code>node { }</code></td></tr>
<tr><td>Style</td><td>Structured, opinionated</td><td>Imperative Groovy</td></tr>
<tr><td>Validation</td><td>Up-front lint check</td><td>Runtime errors only</td></tr>
<tr><td>Easy to read</td><td>✅</td><td>For Groovy programmers</td></tr>
<tr><td>Use when</td><td>Almost always (default)</td><td>Need full Groovy power</td></tr>
</table>
<p><strong>Declarative example:</strong></p>
<pre><code>pipeline {
  agent { label 'docker' }
  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timestamps()
  }
  parameters {
    choice(name: 'ENV', choices: ['dev', 'staging', 'prod'])
    booleanParam(name: 'SKIP_TESTS', defaultValue: false)
  }
  environment {
    REGISTRY = 'ghcr.io/acme'
    GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
  }
  stages {
    stage('Test') {
      when { not { expression { params.SKIP_TESTS } } }
      steps { sh 'npm ci && npm test' }
    }
    stage('Build') {
      steps { sh "docker build -t $REGISTRY/api:$GIT_SHORT ." }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps { sh "./deploy.sh ${params.ENV} $GIT_SHORT" }
    }
  }
  post {
    always  { junit 'test-results/**/*.xml' }
    success { slackSend(channel: '#deploys', message: "✅ ${env.JOB_NAME}") }
    failure { slackSend(channel: '#deploys', message: "❌ ${env.JOB_NAME}") }
  }
}
</code></pre>
<p><strong>Scripted equivalent</strong> (only when you need it):</p>
<pre><code>node('docker') {
  try {
    stage('Test') {
      checkout scm
      sh 'npm ci && npm test'
    }
    stage('Build') {
      sh 'docker build -t myapp .'
    }
    if (env.BRANCH_NAME == 'main') {
      stage('Deploy') {
        sh './deploy.sh'
      }
    }
  } finally {
    junit 'test-results/**/*.xml'
  }
}
</code></pre>
<p><strong>Key building blocks:</strong></p>
<ul>
<li><strong><code>agent</code></strong> &mdash; where it runs (any, label, docker image, kubernetes pod template).</li>
<li><strong><code>environment</code></strong> &mdash; per-pipeline or per-stage env vars / credentials.</li>
<li><strong><code>parameters</code></strong> &mdash; user-supplied build params (string, choice, boolean, password, file).</li>
<li><strong><code>options</code></strong> &mdash; cross-cutting concerns (timeout, retries, lock, ansiColor).</li>
<li><strong><code>triggers</code></strong> &mdash; cron, pollSCM, upstream.</li>
<li><strong><code>stages</code></strong> &mdash; visible blocks; each contains <code>steps</code> or nested <code>parallel</code>.</li>
<li><strong><code>when</code></strong> &mdash; conditional execution (branch, environment, tag, expression).</li>
<li><strong><code>input</code></strong> &mdash; manual approval gate.</li>
<li><strong><code>post</code></strong> &mdash; <code>always / success / failure / changed / fixed</code> handlers.</li>
</ul>
<p><strong>Reusable code:</strong> <strong>Shared Libraries</strong> let you publish helper steps to a Git repo and import them with <code>@Library('lib') _</code>. Useful for standardising deploy steps across a fleet of services.</p>
<p><strong>2026 reality:</strong> for new projects, GitHub Actions / GitLab CI / Buildkite / Tekton offer cleaner config-as-code without the Groovy learning curve. Jenkins Pipeline DSL is the right answer when you have an existing Jenkins fleet, plugin lock-in, or air-gapped on-prem requirements.</p>'''

ANSWERS[92] = r'''<p><strong>Helm</strong> is the package manager for Kubernetes. A <strong>chart</strong> bundles a set of K8s manifests as templates with values you can override per environment &mdash; the equivalent of an apt/npm package for cluster workloads.</p>
<p><strong>Chart layout:</strong></p>
<pre><code>my-chart/
├── Chart.yaml          # name, version, appVersion, dependencies
├── values.yaml         # default values
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── _helpers.tpl    # template helpers
└── charts/             # subcharts
</code></pre>
<p><strong>Templated manifest</strong> &mdash; values become placeholders:</p>
<pre><code># templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-chart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: app
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          resources: {{- toYaml .Values.resources | nindent 12 }}
</code></pre>
<p><strong>Common operations:</strong></p>
<pre><code># Add a chart repo and install
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install my-redis bitnami/redis -n cache --create-namespace

# Upgrade with overrides (file or --set)
helm upgrade --install api ./my-chart \
  -f values-prod.yaml \
  --set image.tag=1.2.3 \
  --namespace prod \
  --atomic --wait --timeout 5m

# Diff before applying
helm diff upgrade api ./my-chart -f values-prod.yaml

# List, status, history, rollback
helm list -A
helm status api -n prod
helm history api -n prod
helm rollback api 3 -n prod          # roll back to revision 3

# Render templates locally without applying
helm template api ./my-chart -f values-prod.yaml | kubectl apply --dry-run=server -f -

# Uninstall
helm uninstall api -n prod
</code></pre>
<p><strong>Why teams use Helm:</strong></p>
<ul>
<li><strong>Templating</strong> &mdash; one chart, many environments via different <code>values-*.yaml</code> files.</li>
<li><strong>Releases</strong> &mdash; Helm tracks revisions; <code>helm rollback</code> reverts to a previous version atomically.</li>
<li><strong>Hooks</strong> &mdash; pre-install / post-install / pre-upgrade jobs (DB migrations, smoke tests).</li>
<li><strong>Dependencies</strong> &mdash; chart can depend on other charts (your app pulls in postgres + redis charts).</li>
<li><strong>Hub of pre-built charts</strong> &mdash; Bitnami, Artifact Hub host thousands of community charts (Postgres, Redis, Keycloak, monitoring stacks).</li>
</ul>
<p><strong>Pitfalls:</strong></p>
<ul>
<li>Templates are string-based &mdash; whitespace and indentation bugs are common; <code>helm lint</code> + <code>helm template</code> + a chart-testing tool catch most.</li>
<li>Complex charts become hard to read; alternatives like <strong>Kustomize</strong> use overlays without templating.</li>
<li>Helm releases live in K8s Secrets in the namespace &mdash; not safe in cross-cluster scenarios without backup.</li>
</ul>
<p><strong>2026 alternatives and complements:</strong></p>
<ul>
<li><strong>Kustomize</strong> &mdash; built into <code>kubectl</code> via <code>-k</code>; overlay-based, no templates.</li>
<li><strong>Argo CD / Flux</strong> &mdash; both natively render Helm charts in GitOps workflows; you keep <code>values-*.yaml</code> in Git, the controller installs/upgrades.</li>
<li><strong>Carvel kapp / ytt</strong> &mdash; alternative composition tools.</li>
<li><strong>cdk8s</strong> / <strong>Pulumi</strong> &mdash; programmatic K8s manifests in real languages (TS, Python, Go).</li>
</ul>'''

ANSWERS[93] = r'''<p>Old Docker images and stopped containers accumulate fast on dev machines and CI runners and quietly fill the disk. Cleanup is a routine maintenance job.</p>
<p><strong>Targeted removal:</strong></p>
<pre><code># Stop and remove a single container
docker stop api
docker rm api

# Remove one image
docker rmi ghcr.io/acme/api:1.0.0

# Remove all stopped containers
docker container prune

# Remove all dangling images (untagged, no children)
docker image prune

# Remove unused images (no container is using them)
docker image prune -a

# Remove dangling volumes
docker volume prune

# Remove unused networks
docker network prune
</code></pre>
<p><strong>Nuclear option &mdash; remove everything not in use:</strong></p>
<pre><code># Containers, networks, dangling images, build cache
docker system prune

# Same plus unused images and volumes (very aggressive)
docker system prune -a --volumes

# Filtered &mdash; only prune things older than 24h
docker system prune --filter "until=24h"

# Just the build cache
docker builder prune --keep-storage 10GB
</code></pre>
<p><strong>Inspect what&rsquo;s consuming space:</strong></p>
<pre><code>docker system df              # summary by category
docker system df -v           # verbose: per-image / per-container / per-volume sizes
docker images --filter dangling=true
docker ps -a --filter status=exited
</code></pre>
<p><strong>Automation patterns:</strong></p>
<table>
<tr><th>Where</th><th>Mechanism</th></tr>
<tr><td>Local dev</td><td>Cron / launchd: <code>0 3 * * * docker system prune -af --filter "until=168h"</code></td></tr>
<tr><td>CI runners</td><td>End-of-job step: <code>docker system prune -af</code></td></tr>
<tr><td>Container hosts</td><td>systemd timer or DaemonSet running prune</td></tr>
<tr><td>Kubernetes nodes</td><td>kubelet image-gc handles unused images automatically; tune <code>--image-gc-high-threshold</code></td></tr>
<tr><td>Docker daemon</td><td><code>--config-file</code> with <code>"builder": { "gc": { "enabled": true, "defaultKeepStorage": "20GB" } }</code></td></tr>
</table>
<p><strong>Registry-side cleanup</strong> (just as important):</p>
<ul>
<li><strong>Docker Hub</strong> &mdash; tag retention rules on paid plans; manual delete via UI/API.</li>
<li><strong>GHCR</strong> &mdash; package retention via GitHub UI; <code>actions/delete-package-versions</code> in workflows.</li>
<li><strong>AWS ECR</strong> &mdash; lifecycle policies (<em>keep last 30 images, expire untagged after 7 days</em>).</li>
<li><strong>GCP Artifact Registry / ACR</strong> &mdash; comparable retention rules.</li>
</ul>
<p><strong>Best practices:</strong></p>
<ul>
<li><strong>Use <code>--rm</code></strong> on one-off <code>docker run</code> commands so containers vanish on exit.</li>
<li><strong>BuildKit cache mounts</strong> (<code>RUN --mount=type=cache,...</code>) are bounded automatically &mdash; safer than uncached layers.</li>
<li><strong>Tag immutably</strong> (semver / Git SHA) so old releases are easy to identify and prune.</li>
<li><strong>Monitor disk</strong> with Prometheus node_exporter <code>node_filesystem_avail_bytes</code> &mdash; alert at 80 % full.</li>
</ul>'''

ANSWERS[94] = r'''<p>GitHub Actions ships with a rich ecosystem of security-scanning actions covering source code (SAST), dependencies (SCA), container images, infrastructure-as-code, and secret detection. The goal is &ldquo;shift left&rdquo; &mdash; catch issues in PR before they reach <code>main</code>.</p>
<p><strong>Comprehensive security workflow:</strong></p>
<pre><code>name: Security
on:
  push: { branches: [main] }
  pull_request:
  schedule: [{ cron: '0 6 * * 1' }]   # weekly full scan

permissions:
  contents: read
  security-events: write    # to upload SARIF to GitHub Security tab
  pull-requests: write

jobs:
  codeql:                                       # SAST (source code)
    runs-on: ubuntu-latest
    strategy:
      matrix: { language: [javascript, python] }
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: ${{ matrix.language }} }
      - uses: github/codeql-action/analyze@v3

  dependency-review:                            # SCA on PR (catches CVE-introducing PRs)
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
        with: { fail-on-severity: high }

  trivy-fs:                                     # vulnerabilities + misconfigs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          format: sarif
          output: trivy.sarif
          severity: HIGH,CRITICAL
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: trivy.sarif }

  container-scan:                               # docker image
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app:${{ github.sha }} .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:${{ github.sha }}
          severity: HIGH,CRITICAL
          exit-code: 1                          # fail PR on findings
      - uses: anchore/sbom-action@v0
        with: { image: app:${{ github.sha }}, format: spdx-json }

  iac-scan:                                     # Terraform / K8s / Dockerfile config
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@master
        with: { framework: terraform,kubernetes,dockerfile }

  secrets:                                      # secret detection
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env: { GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} }
</code></pre>
<p><strong>Tool ecosystem:</strong></p>
<table>
<tr><th>Category</th><th>Free / OSS</th><th>Paid</th></tr>
<tr><td>SAST</td><td>CodeQL, Semgrep OSS, Bandit (Python)</td><td>Snyk Code, Veracode, Checkmarx</td></tr>
<tr><td>SCA</td><td>Dependabot, dependency-review, OSV Scanner, Trivy</td><td>Snyk, Socket.dev, Mend, Dependabot Security Updates</td></tr>
<tr><td>Container</td><td>Trivy, Grype, Docker Scout (free tier)</td><td>Snyk, Wiz, Sysdig Secure</td></tr>
<tr><td>IaC</td><td>Checkov, KICS, tfsec</td><td>Bridgecrew, Snyk IaC, Wiz</td></tr>
<tr><td>Secrets</td><td>Gitleaks, TruffleHog, GitHub Secret Scanning (free for public)</td><td>GitGuardian</td></tr>
<tr><td>Supply chain</td><td>Sigstore, SLSA, in-toto</td><td>Chainguard, Anchore Enterprise</td></tr>
</table>
<p><strong>Built-in GitHub Advanced Security</strong> (free for public repos, paid for private orgs) gives Code Scanning, Secret Scanning + Push Protection, and Dependency Review with native PR-blocking integration.</p>
<p><strong>Best practices:</strong> upload findings as <strong>SARIF</strong> to surface in the GitHub Security tab; mark security checks as required for merging; use OSV Scanner for transitive vulnerability accuracy; <strong>step-security/harden-runner</strong> blocks unexpected egress to detect malicious actions; sign images with <strong>Cosign</strong> and verify at deploy.</p>'''

ANSWERS[95] = r'''<p>Jenkins runs jobs on <strong>agents</strong> (also called nodes / workers). The <strong>controller</strong> (formerly &ldquo;master&rdquo;) schedules jobs and serves the UI; agents do the actual work. Modern Jenkins terminology drops &ldquo;master/slave&rdquo; in favour of &ldquo;controller/agent&rdquo;.</p>
<p><strong>Why distribute:</strong></p>
<ul>
<li>Run jobs in parallel across many machines.</li>
<li>Use OS-specific agents (Linux for backend, macOS for iOS builds, Windows for .NET).</li>
<li>Isolate the controller from build workloads &mdash; controller stays responsive even when 50 builds run.</li>
<li>Scale horizontally; add agents on demand.</li>
</ul>
<p><strong>Connection methods:</strong></p>
<table>
<tr><th>Method</th><th>How it works</th><th>Use</th></tr>
<tr><td><strong>Inbound (JNLP)</strong></td><td>Agent connects out to controller; only controller port needs to be reachable</td><td>Most common &mdash; works through NATs / firewalls</td></tr>
<tr><td><strong>SSH</strong></td><td>Controller SSHes into agent to launch the agent process</td><td>Long-lived static agents on known machines</td></tr>
<tr><td><strong>Docker / Kubernetes</strong></td><td>Agent Pod / container is created per build, deleted afterwards</td><td>Modern default &mdash; ephemeral, scales to zero</td></tr>
<tr><td><strong>Cloud plugins</strong> (EC2, Azure VM, GCE)</td><td>Agents auto-provisioned as VMs on demand</td><td>Bursty workloads on cloud</td></tr>
</table>
<p><strong>Static SSH agent setup:</strong></p>
<ol>
<li>Generate an SSH key pair on the controller; add the public key to <code>~/.ssh/authorized_keys</code> on the agent host.</li>
<li>In Jenkins UI: <em>Manage Jenkins &rarr; Nodes &rarr; New Node</em> &rarr; permanent agent.</li>
<li>Set <em>Remote root directory</em>, <em>Labels</em> (e.g. <code>linux docker</code>), <em>Launch method = SSH</em>, point at the host + credentials.</li>
<li>Save &rarr; agent connects and shows online.</li>
</ol>
<p><strong>Pin a job to specific agents using labels:</strong></p>
<pre><code>pipeline {
  agent { label 'linux && docker' }
  stages { stage('Build') { steps { sh 'docker build .' } } }
}
</code></pre>
<p><strong>Kubernetes Cloud (modern preferred pattern):</strong> the Kubernetes plugin spawns a Pod per build, runs the steps in containers inside the Pod, then deletes it.</p>
<pre><code>pipeline {
  agent {
    kubernetes {
      yaml &apos;&apos;&apos;
        apiVersion: v1
        kind: Pod
        spec:
          containers:
            - name: node
              image: node:20
              command: [cat]
              tty: true
            - name: docker
              image: docker:25-dind
              securityContext: { privileged: true }
      &apos;&apos;&apos;
    }
  }
  stages {
    stage('Test')  { steps { container('node')   { sh 'npm test' } } }
    stage('Build') { steps { container('docker') { sh 'docker build .' } } }
  }
}
</code></pre>
<p><strong>Operational concerns:</strong></p>
<ul>
<li><strong>Capacity planning</strong> &mdash; size agents for peak concurrent builds plus headroom; monitor queue length.</li>
<li><strong>Security</strong> &mdash; treat agents as untrusted; never run them with controller-level credentials. Use the <em>Authorize Project</em> plugin for least privilege.</li>
<li><strong>Persistence</strong> &mdash; build workspaces on agents are ephemeral; use <code>stash</code> / <code>unstash</code> or artifacts for files that need to cross stages.</li>
<li><strong>Auto-scaling</strong> &mdash; <code>jenkins-kubernetes-operator</code>, <code>EC2 Fleet</code>, or <code>Kubernetes Cloud</code> scales agents on demand &mdash; you only pay when builds run.</li>
</ul>
<p><strong>2026 trend:</strong> for new CI installations, GitHub Actions self-hosted runners on K8s (<strong>actions-runner-controller</strong>) or <strong>Buildkite agents</strong> are leaner alternatives to Jenkins controller/agent topology.</p>'''

ANSWERS[96] = r'''<p><strong>Minikube</strong> runs a single-node Kubernetes cluster on a developer&rsquo;s laptop, perfect for learning, local development, and CI smoke-tests. It supports multiple drivers (Docker, Podman, hyperkit, VirtualBox, KVM2) and can simulate multi-node clusters.</p>
<p><strong>Install and start:</strong></p>
<pre><code># macOS / Linux (Homebrew)
brew install minikube

# Windows (winget)
winget install Kubernetes.minikube

# Start a cluster (defaults: docker driver, 2 CPUs, 4 GB RAM)
minikube start

# Custom configuration
minikube start \
  --driver=docker \
  --cpus=4 --memory=8g \
  --kubernetes-version=v1.30.0 \
  --nodes=3 \
  --addons=ingress,metrics-server
</code></pre>
<p><strong>Verify and use:</strong></p>
<pre><code>minikube status
kubectl get nodes
kubectl create deployment hello --image=nginx
kubectl expose deployment hello --port=80 --type=NodePort
minikube service hello                # opens in browser
</code></pre>
<p><strong>Useful commands:</strong></p>
<table>
<tr><th>Command</th><th>Purpose</th></tr>
<tr><td><code>minikube dashboard</code></td><td>Launch the K8s web UI</td></tr>
<tr><td><code>minikube tunnel</code></td><td>Expose <code>LoadBalancer</code> services on localhost</td></tr>
<tr><td><code>minikube image load IMG</code></td><td>Push a local image into the cluster (skip registry)</td></tr>
<tr><td><code>eval $(minikube docker-env)</code></td><td>Build images with Minikube&rsquo;s Docker daemon directly</td></tr>
<tr><td><code>minikube addons list</code></td><td>List add-ons (ingress, registry, dashboard, gpu, ...)</td></tr>
<tr><td><code>minikube addons enable ingress</code></td><td>Install nginx-ingress</td></tr>
<tr><td><code>minikube ssh</code></td><td>Shell into the node VM</td></tr>
<tr><td><code>minikube logs</code></td><td>Show node logs</td></tr>
<tr><td><code>minikube delete</code></td><td>Tear it all down</td></tr>
<tr><td><code>minikube profile NAME</code></td><td>Switch among multiple clusters</td></tr>
</table>
<p><strong>Multi-node example:</strong></p>
<pre><code>minikube start --nodes=3 --kubernetes-version=v1.30.0
kubectl get nodes
# NAME           STATUS   ROLES           AGE
# minikube       Ready    control-plane   30s
# minikube-m02   Ready    &lt;none&gt;          15s
# minikube-m03   Ready    &lt;none&gt;          5s
</code></pre>
<p><strong>Local-cluster alternatives:</strong></p>
<table>
<tr><th>Tool</th><th>Notes</th></tr>
<tr><td><strong>Kind</strong> (Kubernetes-in-Docker)</td><td>Lightweight, fast, great for CI; the standard choice for K8s testing in 2026.</td></tr>
<tr><td><strong>k3d</strong></td><td>Wraps k3s in Docker; very fast, low memory.</td></tr>
<tr><td><strong>Docker Desktop</strong> / <strong>Rancher Desktop</strong> / <strong>Podman Desktop</strong></td><td>One-click K8s integrated with the Docker runtime.</td></tr>
<tr><td><strong>OrbStack</strong></td><td>macOS-only; very fast K8s + Docker.</td></tr>
<tr><td><strong>Colima</strong></td><td>Lima-based; lightweight macOS/Linux.</td></tr>
</table>
<p><strong>When to use what:</strong> Minikube for learning and one-off experiments; <strong>Kind</strong> for CI and reproducible testing (<code>actions/setup-k8s</code> integrates cleanly); <strong>k3d</strong> for the smallest footprint; <strong>Docker Desktop K8s</strong> for the easiest GUI experience. For serious workloads use a managed cluster (<strong>EKS / GKE / AKS</strong>).</p>'''

ANSWERS[97] = r'''<p>A <strong>multi-stage Dockerfile</strong> uses multiple <code>FROM</code> instructions, each beginning a new build stage. You compile / install in one stage with full toolchains, then copy only the produced artefacts into a slim final stage. Result: a tiny, secure runtime image with no build tools, source code, or dev dependencies.</p>
<p><strong>Why it matters:</strong></p>
<ul>
<li><strong>Smaller images</strong> &mdash; 50&ndash;90 % size reduction is typical (e.g. 1.2 GB &rarr; 80 MB).</li>
<li><strong>Smaller attack surface</strong> &mdash; no compilers / package managers / source code in prod.</li>
<li><strong>Faster pulls and rolling updates</strong> &mdash; less network I/O, fewer cold-start delays.</li>
<li><strong>Cleaner layers</strong> &mdash; build cache is stage-aware; rebuilding only re-runs affected stages.</li>
</ul>
<p><strong>Node.js example:</strong></p>
<pre><code># --- Stage 1: production dependencies only
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

# --- Stage 2: full build (TypeScript, bundler)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# --- Stage 3: minimal runtime
FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
USER nonroot
COPY --from=deps  /app/node_modules ./node_modules
COPY --from=build /app/dist         ./dist
EXPOSE 3000
CMD ["dist/server.js"]
</code></pre>
<p>The final image contains no <code>npm</code>, no source <code>.ts</code>, no test files &mdash; only the built JS, the prod <code>node_modules</code>, and a minimal Node runtime.</p>
<p><strong>Go example &mdash; the dramatic case:</strong></p>
<pre><code>FROM golang:1.23-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/app ./cmd/server

FROM gcr.io/distroless/static-debian12
COPY --from=build /out/app /app
USER nonroot
EXPOSE 8080
ENTRYPOINT ["/app"]
</code></pre>
<p>Final image: ~10&ndash;20 MB, contains nothing but the static binary.</p>
<p><strong>Advanced features:</strong></p>
<ul>
<li><strong>Targeting a specific stage:</strong> <code>docker build --target build .</code> stops at <code>build</code> &mdash; useful for running tests in CI without producing the runtime image.</li>
<li><strong>Cross-platform builds</strong> with BuildKit:
<pre><code>FROM --platform=$BUILDPLATFORM golang:1.23 AS build
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/app .
</code></pre>
</li>
<li><strong>BuildKit cache mounts</strong> persist package caches across builds:
<pre><code>RUN --mount=type=cache,target=/root/.npm npm ci
RUN --mount=type=cache,target=/root/.cache/go-build go build .
</code></pre>
</li>
<li><strong>Secret mounts</strong> avoid baking secrets into layers:
<pre><code>RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
</code></pre>
</li>
</ul>
<p><strong>Best practices:</strong></p>
<ul>
<li>Use <strong>distroless / chainguard</strong> base images for the final stage.</li>
<li>Run as <strong>non-root</strong> (<code>USER nonroot</code>).</li>
<li>Pin base images by digest for reproducibility.</li>
<li>Order copies by churn &mdash; <code>package.json</code> / <code>go.sum</code> first, source last, so dependency layers cache.</li>
<li>Use <code>.dockerignore</code> &mdash; skip <code>.git</code>, <code>node_modules</code>, <code>__pycache__</code>, build outputs.</li>
</ul>'''

ANSWERS[98] = r'''<p><strong>Code coverage</strong> measures what fraction of your code is exercised by tests. GitHub Actions integrates with coverage runners (Jest / Vitest / pytest-cov / JaCoCo / go test -cover) and uploaders (Codecov, Coveralls, SonarCloud) to track coverage per commit and PR.</p>
<p><strong>Node.js example with Vitest + Codecov:</strong></p>
<pre><code>name: Coverage
on: [push, pull_request]
permissions: { contents: read }

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run test:coverage    # produces coverage/lcov.info
      - uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: coverage/lcov.info
          fail_ci_if_error: true
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/
</code></pre>
<p><strong>Vitest config:</strong></p>
<pre><code>// vitest.config.ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'html'],
      thresholds: {
        lines: 80, functions: 80, branches: 75, statements: 80,
      },
      exclude: ['node_modules/', 'dist/', '**/*.config.ts'],
    },
  },
});
</code></pre>
<p><strong>Python example with pytest-cov:</strong></p>
<pre><code>jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv run pytest --cov=src --cov-report=xml --cov-report=term
      - uses: codecov/codecov-action@v4
        with: { files: coverage.xml }
</code></pre>
<p><strong>Java with JaCoCo:</strong></p>
<pre><code>      - run: mvn -B verify   # generates target/site/jacoco/jacoco.xml
      - uses: codecov/codecov-action@v4
        with: { files: target/site/jacoco/jacoco.xml }
</code></pre>
<p><strong>Coverage providers:</strong></p>
<table>
<tr><th>Tool</th><th>Notes</th></tr>
<tr><td><strong>Codecov</strong></td><td>PR comments with diff coverage, status checks; free for OSS, paid for private.</td></tr>
<tr><td><strong>Coveralls</strong></td><td>Similar; lighter UI; free for OSS.</td></tr>
<tr><td><strong>SonarCloud / SonarQube</strong></td><td>Coverage + code-quality + security in one report.</td></tr>
<tr><td><strong>Codacy / Code Climate</strong></td><td>Coverage + maintainability metrics.</td></tr>
<tr><td><strong>Self-hosted</strong></td><td>Upload <code>coverage/</code> as artifact + GitHub Pages or static report site.</td></tr>
</table>
<p><strong>PR comments &mdash; the killer feature:</strong> Codecov posts a comment showing how the PR changes coverage, with file-by-file diffs and which new lines lack tests. Combined with a <strong>required status check</strong> (<em>&ldquo;coverage must not decrease&rdquo;</em>), this prevents untested code from sneaking in.</p>
<p><strong>Best practices:</strong></p>
<ul>
<li><strong>Per-PR diff coverage</strong> &gt; absolute coverage &mdash; require new code to be 80 %+ covered, not the whole codebase.</li>
<li><strong>Don&rsquo;t chase 100 %</strong> &mdash; the last 10 % is usually generated code, error handlers, or framework boilerplate. Focus on critical paths.</li>
<li><strong>Differentiate test types</strong> &mdash; track unit / integration / e2e coverage separately; combine via Codecov flags.</li>
<li><strong>Mutation testing</strong> for higher confidence: <strong>Stryker</strong> (JS), <strong>mutmut</strong> (Python), <strong>PIT</strong> (Java) verify tests actually catch bugs &mdash; coverage alone can be misleading.</li>
<li><strong>Beware coverage gaming</strong> &mdash; tests that execute lines without asserting anything pass coverage but catch nothing. Code review remains essential.</li>
</ul>'''

ANSWERS[99] = r'''<p>A <strong>Declarative Pipeline</strong> is the modern, opinionated syntax for Jenkins pipelines. It uses a fixed top-level structure (<code>pipeline { agent { } stages { } post { } }</code>) and a constrained DSL designed for readability and up-front validation. It&rsquo;s the recommended style for almost all new Jenkins pipelines.</p>
<p><strong>Mandatory skeleton:</strong></p>
<pre><code>pipeline {
  agent any                  // required &mdash; where it runs
  stages {                   // required
    stage('...') {
      steps {                // required inside stage
        // build steps
      }
    }
  }
}
</code></pre>
<p><strong>Full-featured example:</strong></p>
<pre><code>pipeline {
  agent { label 'linux && docker' }

  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timestamps()
    disableConcurrentBuilds()
    ansiColor('xterm')
  }

  parameters {
    choice(name: 'ENV', choices: ['dev', 'staging', 'prod'])
    booleanParam(name: 'SKIP_TESTS', defaultValue: false)
    string(name: 'VERSION', defaultValue: '')
  }

  environment {
    REGISTRY = 'ghcr.io/acme'
    SLACK_CRED = credentials('slack-webhook')   // injects USR + PSW
  }

  triggers {
    cron('H 2 * * *')               // nightly
    pollSCM('H/5 * * * *')          // back-up if webhooks fail
  }

  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Test') {
      when { not { expression { params.SKIP_TESTS } } }
      parallel {
        stage('Unit')        { steps { sh 'npm test' } }
        stage('Lint')        { steps { sh 'npm run lint' } }
        stage('Type-check')  { steps { sh 'npm run typecheck' } }
      }
    }

    stage('Build') {
      steps {
        sh "docker build -t $REGISTRY/api:${env.GIT_COMMIT} ."
      }
    }

    stage('Push') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr', usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login ghcr.io -u $U --password-stdin'
          sh "docker push $REGISTRY/api:${env.GIT_COMMIT}"
        }
      }
    }

    stage('Deploy') {
      when { branch 'main' }
      input {
        message 'Deploy to production?'
        ok 'Deploy'
        submitter 'release-managers'
      }
      steps {
        sh "./deploy.sh ${params.ENV} ${env.GIT_COMMIT}"
      }
    }
  }

  post {
    always  { junit 'test-results/**/*.xml' }
    success { slackSend(channel: '#deploys', message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER}") }
    failure { slackSend(channel: '#deploys', message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER}") }
    cleanup { deleteDir() }
  }
}
</code></pre>
<p><strong>Top-level sections (most-used):</strong></p>
<table>
<tr><th>Section</th><th>Purpose</th></tr>
<tr><td><code>agent</code></td><td>Where the pipeline runs (any, label, docker, kubernetes pod)</td></tr>
<tr><td><code>options</code></td><td>Cross-cutting concerns (timeout, retention, locks)</td></tr>
<tr><td><code>parameters</code></td><td>User-supplied build params</td></tr>
<tr><td><code>environment</code></td><td>Pipeline / stage env vars + credentials</td></tr>
<tr><td><code>triggers</code></td><td>cron, pollSCM, upstream</td></tr>
<tr><td><code>stages</code></td><td>The actual work, with optional <code>parallel</code> and <code>when</code></td></tr>
<tr><td><code>post</code></td><td><code>always</code> / <code>success</code> / <code>failure</code> / <code>changed</code> / <code>cleanup</code></td></tr>
</table>
<p><strong>Validation</strong> &mdash; declarative pipelines are statically analysed before execution:</p>
<pre><code># From CLI
curl -X POST -F "jenkinsfile=@Jenkinsfile" \
  https://jenkins.acme.com/pipeline-model-converter/validate

# Or the linter inside Blue Ocean / Pipeline Editor in the UI
</code></pre>
<p><strong>Declarative vs Scripted:</strong> use Declarative unless you genuinely need full Groovy control flow inside the pipeline. If you do, you can drop into a <code>script { }</code> block within Declarative steps for the best of both. For repeated logic across many repos, factor it into a <strong>Shared Library</strong> rather than reaching for Scripted.</p>'''

ANSWERS[100] = r'''<p><strong>Role-Based Access Control (RBAC)</strong> in Kubernetes governs who can do what to which resources. RBAC is enabled by default in modern clusters and is the primary tool for least-privilege isolation between teams, services, and CI pipelines.</p>
<p><strong>Four core resources:</strong></p>
<table>
<tr><th>Resource</th><th>Scope</th><th>Says</th></tr>
<tr><td><code>Role</code></td><td>Namespace</td><td>What actions are allowed in this namespace</td></tr>
<tr><td><code>ClusterRole</code></td><td>Cluster-wide</td><td>What actions are allowed cluster-wide (or as a re-usable template)</td></tr>
<tr><td><code>RoleBinding</code></td><td>Namespace</td><td>Who gets the Role&rsquo;s permissions in this namespace</td></tr>
<tr><td><code>ClusterRoleBinding</code></td><td>Cluster-wide</td><td>Who gets a ClusterRole cluster-wide</td></tr>
</table>
<p><strong>Example &mdash; let a CI service account deploy in <code>prod</code>:</strong></p>
<pre><code># 1. ServiceAccount the CI pipeline assumes (via OIDC / token)
apiVersion: v1
kind: ServiceAccount
metadata: { name: ci-deployer, namespace: prod }
---
# 2. Role &mdash; minimal permissions for rolling deployments
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer
  namespace: prod
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "patch", "update"]
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["get", "list", "watch"]
---
# 3. RoleBinding &mdash; bind Role to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: deployer
  namespace: prod
subjects:
  - kind: ServiceAccount
    name: ci-deployer
    namespace: prod
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
</code></pre>
<p><strong>Subjects</strong> can be:</p>
<ul>
<li><code>ServiceAccount</code> &mdash; for pods, controllers, CI agents.</li>
<li><code>User</code> &mdash; humans (authenticated via OIDC, certificates, cloud IAM).</li>
<li><code>Group</code> &mdash; for groups defined by the auth provider (Okta groups, Azure AD groups).</li>
</ul>
<p><strong>Verbs:</strong> <code>get</code>, <code>list</code>, <code>watch</code>, <code>create</code>, <code>update</code>, <code>patch</code>, <code>delete</code>, <code>deletecollection</code>, plus <code>impersonate</code>, <code>bind</code>, <code>escalate</code> for special cases.</p>
<p><strong>Built-in ClusterRoles you usually re-use rather than re-creating:</strong></p>
<ul>
<li><code>cluster-admin</code> &mdash; god mode; never bind to humans broadly.</li>
<li><code>admin</code> &mdash; full access in a namespace except RBAC.</li>
<li><code>edit</code> &mdash; create / update / delete resources, no RBAC.</li>
<li><code>view</code> &mdash; read-only.</li>
</ul>
<p><strong>Auditing your RBAC:</strong></p>
<pre><code>kubectl auth can-i create deployments --namespace prod
kubectl auth can-i '*' '*' --as system:serviceaccount:prod:ci-deployer

# What can a SA actually do?
kubectl get rolebindings,clusterrolebindings -A \
  -o json | jq '.items[] | select(.subjects[]?.name=="ci-deployer")'

# Tools
rakkess           # show resource access for users / SAs
rbac-lookup        # who has access to what
audit2rbac        # generate minimal RBAC from audit logs
</code></pre>
<p><strong>Cloud-IAM integration</strong> (the modern path):</p>
<ul>
<li><strong>EKS</strong> &mdash; <em>EKS Pod Identity</em> or <em>IRSA</em> map K8s ServiceAccounts to AWS IAM roles; pods get short-lived AWS credentials automatically.</li>
<li><strong>GKE</strong> &mdash; <em>Workload Identity</em> federates GSA &harr; KSA.</li>
<li><strong>AKS</strong> &mdash; <em>Azure AD Workload Identity</em>.</li>
</ul>
<p><strong>Best practices:</strong> default-deny by namespace; create one ServiceAccount per workload (never share <code>default</code>); start with <code>view</code> + add what&rsquo;s needed (don&rsquo;t start with <code>admin</code> + remove); review bindings quarterly; audit <code>cluster-admin</code> bindings carefully; use <strong>OPA Gatekeeper</strong> or <strong>Kyverno</strong> to enforce policies (e.g. &ldquo;no <code>cluster-admin</code> bindings outside the <code>kube-system</code> namespace&rdquo;).</p>'''
