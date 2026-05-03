"""Detailed answers for CI/CD Pipeline — Coding (100 Q)

Style: code-first + brief explanation + variants/alternatives + perf notes,
~1,800-2,200 chars per answer with 2026-current ecosystem references.
"""

ANSWERS: dict[int, str] = {}

ANSWERS[1] = r'''<pre><code># .github/workflows/ci.yml
name: CI
on:
  push: { branches: [main] }
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node: ['20', '22']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
      - run: npm run build
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-node${{ matrix.node }}
          path: coverage/
</code></pre>
<p><strong>What it does:</strong> on every push to <code>main</code> and every pull request, GitHub spins up an Ubuntu runner per Node version, restores the npm cache (managed by <code>setup-node</code>), installs deps with <code>npm ci</code> for a deterministic lockfile-based install, lints, runs tests with coverage, and builds. Coverage artefacts are uploaded for inspection.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Service containers</strong> for integration tests &mdash; add <code>services: { mongo: { image: mongo:7, ports: [27017:27017] } }</code> at the job level.</li>
<li><strong>Sharded tests</strong>: <code>matrix: { shard: [1, 2, 3, 4] }</code> + <code>npm test -- --shard=${{ matrix.shard }}/4</code>.</li>
<li><strong>pnpm / yarn</strong>: switch <code>cache: pnpm</code> + add <code>pnpm/action-setup@v4</code>.</li>
<li><strong>Codecov upload</strong>: <code>uses: codecov/codecov-action@v4</code> with <code>files: coverage/lcov.info</code>.</li>
</ul>
<p><strong>Performance notes:</strong> <code>concurrency.cancel-in-progress</code> stops superseded runs on rapid pushes &mdash; saves runner minutes. <code>setup-node</code>&rsquo;s built-in cache is faster than a manual <code>actions/cache</code>. Mark <em>test</em> as a required check in branch protection so red PRs can&rsquo;t merge.</p>'''

ANSWERS[2] = r'''<pre><code>// Jenkinsfile
pipeline {
  agent { label 'docker' }
  options {
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }
  environment {
    REGISTRY = 'ghcr.io/acme'
    IMAGE    = "${REGISTRY}/api:${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Build image') {
      steps {
        sh "docker build -t $IMAGE -t $REGISTRY/api:latest ."
      }
    }

    stage('Test image') {
      steps {
        sh "docker run --rm $IMAGE npm test"
      }
    }

    stage('Push') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'ghcr',
          usernameVariable: 'U',
          passwordVariable: 'P')]) {
          sh 'echo $P | docker login ghcr.io -u $U --password-stdin'
          sh "docker push $IMAGE"
          sh "docker push $REGISTRY/api:latest"
        }
      }
    }

    stage('Deploy') {
      when { branch 'main' }
      steps {
        sh "kubectl set image deployment/api api=$IMAGE -n prod"
        sh "kubectl rollout status deployment/api -n prod --timeout=5m"
      }
    }
  }
  post {
    always  { sh 'docker logout ghcr.io || true' }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
  }
}
</code></pre>
<p><strong>Flow:</strong> tags the image with the short Git SHA (immutable) and <code>:latest</code> (moving), runs tests inside the built image so the prod artefact is what was tested, pushes to GHCR only on <code>main</code>, then rolls the deployment forward and waits for readiness.</p>
<p><strong>Variants:</strong> for ECR use <code>aws ecr get-login-password | docker login</code>; for Buildx multi-arch builds prepend a <code>docker buildx create --use</code> stage; replace <code>kubectl set image</code> with <code>helm upgrade --install</code> for Helm-managed apps.</p>
<p><strong>Performance:</strong> add a buildkit cache mount (<code>RUN --mount=type=cache,...</code>) in the Dockerfile and enable <code>DOCKER_BUILDKIT=1</code> on the agent for layer-level caching across builds.</p>'''

ANSWERS[3] = r'''<pre><code># Dockerfile
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# --- builder: install deps in an isolated layer
FROM base AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock* requirements.txt* ./
RUN uv pip install --system -r requirements.txt

# --- runtime: minimal final image
FROM base
WORKDIR /app
RUN useradd -r -u 1000 app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=app:app . .
USER app
EXPOSE 8000

# Production: gunicorn with gevent workers; for async use uvicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
</code></pre>
<p><strong>Companion <code>app.py</code>:</strong></p>
<pre><code>from flask import Flask
app = Flask(__name__)

@app.get("/")
def home():
    return {"status": "ok"}
</code></pre>
<p><strong>Why this shape:</strong></p>
<ul>
<li><strong>Multi-stage</strong> &mdash; builder has uv + build tools; runtime image carries only the installed packages, shrinking the image and attack surface.</li>
<li><strong><code>python:3.13-slim</code></strong> base &mdash; ~50 MB vs ~1 GB for full <code>python</code>; for the smallest footprint use <code>gcr.io/distroless/python3-debian12</code> as the runtime stage.</li>
<li><strong>Non-root user</strong> &mdash; defence-in-depth against container escapes.</li>
<li><strong>uv</strong> (Astral) installs deps 10&ndash;100&times; faster than pip; standard for new Python projects in 2026.</li>
<li><strong>Bytecode + buffering env vars</strong> &mdash; better logging, no <code>.pyc</code> clutter.</li>
</ul>
<p><strong>Variants:</strong> for FastAPI / async use <code>uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4</code>; for trad pip add <code>RUN pip install -r requirements.txt</code> in the builder.</p>
<p><strong>Build &amp; run:</strong></p>
<pre><code>docker build -t flask-app .
docker run -p 8000:8000 flask-app
</code></pre>
<p><strong>Don&rsquo;t forget</strong> a <code>.dockerignore</code> with <code>__pycache__/ .venv/ .git/ .pytest_cache/</code> &mdash; cuts build context size dramatically and avoids leaking local state into the image.</p>'''

ANSWERS[4] = r'''<pre><code># deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: prod
  labels: { app: api }
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  selector:
    matchLabels: { app: api }
  template:
    metadata:
      labels: { app: api }
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.2.3
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 3000
              name: http
          env:
            - name: NODE_ENV
              value: production
            - name: MONGO_URL
              valueFrom:
                secretKeyRef: { name: api-secrets, key: MONGO_URL }
          envFrom:
            - configMapRef: { name: api-config }
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
          livenessProbe:
            httpGet: { path: /healthz, port: http }
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet: { path: /ready, port: http }
            initialDelaySeconds: 5
            periodSeconds: 5
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: [ALL] }
      automountServiceAccountToken: false
</code></pre>
<p><strong>Apply &amp; observe:</strong></p>
<pre><code>kubectl apply -f deployment.yaml
kubectl rollout status deployment/api -n prod
kubectl get pods -n prod -l app=api
</code></pre>
<p><strong>Why each block matters:</strong></p>
<ul>
<li><strong><code>maxUnavailable: 0</code></strong> &mdash; zero-downtime rollouts; one extra Pod during update.</li>
<li><strong>Distinct liveness vs readiness</strong> &mdash; readiness gates traffic; liveness restarts a wedged Pod. Different paths so a slow DB doesn&rsquo;t cause restarts.</li>
<li><strong>Resource <code>requests</code></strong> &mdash; what the scheduler reserves; <strong><code>limits</code></strong> cap runaway usage. Memory limits trigger OOMKill if hit.</li>
<li><strong>Hardened <code>securityContext</code></strong> &mdash; non-root, read-only FS, no caps &mdash; passes most Pod Security Standards (restricted) checks.</li>
<li><strong>Secrets via <code>secretKeyRef</code></strong> &mdash; never hard-code; pair with External Secrets Operator for managed-vault sync.</li>
</ul>
<p><strong>Pair with</strong>: a <code>Service</code> (ClusterIP for internal), an <code>HPA</code> for auto-scaling, and a <code>PodDisruptionBudget</code> with <code>minAvailable: 2</code> so node drains don&rsquo;t take you below 2 replicas.</p>'''

ANSWERS[5] = r'''<pre><code># .github/workflows/deploy-pages.yml
name: Deploy to GitHub Pages
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write       # required for OIDC token

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build           # Vite/CRA produces ./dist or ./build
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }         # change to "build" for CRA

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
</code></pre>
<p><strong>Setup steps in GitHub:</strong></p>
<ol>
<li>Repo &rarr; <em>Settings &rarr; Pages</em> &rarr; <em>Source: GitHub Actions</em>.</li>
<li>If using a project page (<code>https://USER.github.io/REPO</code>), set <code>base: '/REPO/'</code> in <code>vite.config.js</code> (or <code>"homepage": "https://USER.github.io/REPO"</code> for CRA) &mdash; otherwise asset paths break.</li>
<li>Push to <code>main</code> &rarr; the workflow builds and publishes; first deploy provisions the Pages site.</li>
</ol>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Custom domain</strong> &mdash; add a <code>public/CNAME</code> file containing the domain; configure DNS to <code>USER.github.io</code>.</li>
<li><strong>Single-page-app routing</strong> &mdash; add a <code>404.html</code> redirect or use HashRouter; Pages doesn&rsquo;t rewrite paths server-side.</li>
<li><strong>Next.js</strong> &mdash; <code>next build && next export</code> (or use <code>output: 'export'</code> in <code>next.config.js</code>); upload <code>./out</code>.</li>
<li><strong>Vue / Svelte / Astro</strong> &mdash; same pattern, different output dir (<code>dist</code> for Vite-based).</li>
</ul>
<p><strong>Performance:</strong> the <code>actions/deploy-pages</code> action uses OIDC and atomic deploys &mdash; no API tokens, instant rollback to previous artefact in Pages UI. Concurrency group ensures only one deploy runs at a time, avoiding races.</p>'''

ANSWERS[6] = r'''<pre><code>// Jenkinsfile
pipeline {
  agent any
  tools { jdk 'jdk-21'; maven 'maven-3.9' }
  options { timeout(time: 30, unit: 'MINUTES') }
  environment {
    APP_NAME = 'api'
    EC2_HOST = 'deploy@ec2-1-2-3-4.compute-1.amazonaws.com'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Build & Test') {
      steps {
        sh 'mvn -B clean verify'
      }
      post {
        always { junit '**/target/surefire-reports/*.xml' }
      }
    }

    stage('Package') {
      steps {
        sh 'mvn -B package -DskipTests'
        archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
      }
    }

    stage('Deploy to EC2') {
      when { branch 'main' }
      steps {
        sshagent(['ec2-deploy-key']) {
          sh &apos;&apos;&apos;
            JAR=$(ls target/*.jar | head -1)
            scp -o StrictHostKeyChecking=no $JAR $EC2_HOST:/opt/$APP_NAME/app.jar
            ssh -o StrictHostKeyChecking=no $EC2_HOST &apos;
              sudo systemctl restart api &amp;&amp;
              sleep 5 &amp;&amp;
              curl -fsS http://localhost:8080/actuator/health
            &apos;
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
  }
}
</code></pre>
<p><strong>EC2 prerequisites:</strong></p>
<ul>
<li>SSH key uploaded to Jenkins as a credential <code>ec2-deploy-key</code>; the public key is in <code>~/.ssh/authorized_keys</code> on the box.</li>
<li>A systemd unit <code>/etc/systemd/system/api.service</code> running <code>java -jar /opt/api/app.jar</code> as a non-root user.</li>
<li>Security group permits inbound 22 only from the Jenkins agent and 8080 (or 443 via nginx/ALB) from clients.</li>
</ul>
<p><strong>Variants &amp; better options for 2026:</strong></p>
<ul>
<li><strong>S3 + CodeDeploy</strong> &mdash; upload jar to S3, trigger CodeDeploy for blue/green or in-place; safer than raw scp.</li>
<li><strong>Containerise &rarr; ECS / EKS</strong> &mdash; build a Docker image, push to ECR, update task def. Dramatically simpler at scale.</li>
<li><strong>AWS SSM Run Command</strong> &mdash; deploy without opening SSH; better audit trail.</li>
<li><strong>Auto Scaling Group + AMI</strong> &mdash; bake a new AMI with Packer, update the launch template, instance refresh.</li>
</ul>
<p><strong>Performance:</strong> add <code>options { skipDefaultCheckout() }</code> + <code>parallel</code> stages for unit / integration tests on multi-module Maven projects; cache <code>~/.m2/repository</code> on the agent or use a <em>Maven repository manager</em> (Nexus, Artifactory) to avoid re-downloading on every build.</p>'''

ANSWERS[7] = r'''<pre><code># docker-compose.yml
services:
  web:
    build: ./web
    image: acme/web:dev
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://app:secret@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db:    { condition: service_healthy }
      cache: { condition: service_started }
    develop:
      watch:                 # Compose watch (Compose v2.22+)
        - { action: sync,    path: ./web/src,         target: /app/src }
        - { action: rebuild, path: ./web/package.json }

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 10

  cache:
    image: redis:7-alpine
    command: ["redis-server", "--save", "60", "1", "--loglevel", "warning"]
    volumes: [cache-data:/data]

volumes:
  db-data: {}
  cache-data: {}
</code></pre>
<p><strong>Run it:</strong></p>
<pre><code>docker compose up -d           # start in background
docker compose logs -f web      # tail logs
docker compose watch            # live-reload on file changes (v2.22+)
docker compose down -v          # stop + remove volumes
</code></pre>
<p><strong>Why these patterns:</strong></p>
<ul>
<li><strong>Service DNS</strong> &mdash; the <code>web</code> container reaches Postgres at hostname <code>db</code> automatically; no port publishing needed for inter-service calls.</li>
<li><strong>Health-checked startup</strong> &mdash; <code>depends_on.condition: service_healthy</code> waits for Postgres to actually be ready, not just running.</li>
<li><strong>Init scripts</strong> &mdash; <code>/docker-entrypoint-initdb.d/*.sql</code> runs on first start to seed schema/data.</li>
<li><strong>Named volumes</strong> &mdash; <code>db-data</code> survives <code>compose down</code>; only <code>down -v</code> wipes it.</li>
<li><strong>Compose Watch</strong> &mdash; sync source files into the container without rebuilding; rebuild only when <code>package.json</code> changes.</li>
</ul>
<p><strong>Variants:</strong> add a <code>networks:</code> section for segmentation (front/back); add <code>restart: unless-stopped</code> for prod-like behaviour; use <code>profiles:</code> to opt-in extra services (mailhog, adminer, monitoring).</p>
<p><strong>Performance:</strong> for tests, use <code>tmpfs</code> for the Postgres data dir &mdash; massively faster: <code>tmpfs: /var/lib/postgresql/data</code>. For prod, do <em>not</em> use Compose at scale &mdash; reach for Kubernetes or a PaaS.</p>'''

ANSWERS[8] = r'''<pre><code># service.yaml — three common ways to expose a Deployment
---
apiVersion: v1
kind: Service                  # 1) ClusterIP — internal only (default)
metadata:
  name: api
  namespace: prod
spec:
  type: ClusterIP
  selector: { app: api }
  ports:
    - name: http
      port: 80
      targetPort: 3000
---
apiVersion: v1
kind: Service                  # 2) NodePort — :3xxxx on every node
metadata: { name: api-nodeport, namespace: prod }
spec:
  type: NodePort
  selector: { app: api }
  ports:
    - port: 80
      targetPort: 3000
      nodePort: 30080
---
apiVersion: v1
kind: Service                  # 3) LoadBalancer — cloud LB with public IP
metadata:
  name: api-lb
  namespace: prod
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
spec:
  type: LoadBalancer
  selector: { app: api }
  ports:
    - port: 443
      targetPort: 3000
---
apiVersion: networking.k8s.io/v1   # 4) Ingress — recommended for HTTP(S)
kind: Ingress
metadata:
  name: api
  namespace: prod
  annotations: { cert-manager.io/cluster-issuer: letsencrypt-prod }
spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.acme.com]
      secretName: api-tls
  rules:
    - host: api.acme.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: { name: api, port: { number: 80 } }
</code></pre>
<p><strong>When to use which:</strong></p>
<ul>
<li><strong>ClusterIP</strong> &mdash; default; for service-to-service calls inside the cluster.</li>
<li><strong>NodePort</strong> &mdash; quick &amp; dirty; one port per service across all nodes; rarely correct in prod.</li>
<li><strong>LoadBalancer</strong> &mdash; cloud LB per service. Costs add up: 50 services = 50 ELBs. Right for a small number of L4 endpoints.</li>
<li><strong>Ingress</strong> &mdash; one LB shared across many HTTP(S) services with hostname/path routing. The standard for L7 in 2026.</li>
<li><strong>Gateway API</strong> &mdash; the next-generation successor to Ingress (richer routing, shared by many controllers); GA in many controllers (Cilium, Istio, NGINX) &mdash; prefer for greenfield.</li>
</ul>
<p><strong>Apply and verify:</strong></p>
<pre><code>kubectl apply -f service.yaml
kubectl get svc -n prod
kubectl describe ingress api -n prod
kubectl port-forward svc/api 8080:80 -n prod   # quick local test
</code></pre>
<p><strong>Performance / ops tips:</strong> for LoadBalancer, choose <strong>NLB</strong> (TCP) for low latency, <strong>ALB</strong> (HTTP) for L7 features; on GKE/AKS the equivalents are Network LB and Application LB. With Ingress, set <code>externalTrafficPolicy: Local</code> on the LB to preserve client IPs and skip extra hops.</p>'''

ANSWERS[9] = r'''<pre><code># .github/workflows/coverage.yml
name: Tests + Coverage
on: [push, pull_request]

permissions: { contents: read }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run test -- --coverage --coverageReporters=lcov --coverageReporters=text
      - name: Coverage summary in PR
        if: github.event_name == 'pull_request'
        uses: davelosert/vitest-coverage-report-action@v2
        with: { json-summary-path: coverage/coverage-summary.json }
      - uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: coverage/lcov.info
          fail_ci_if_error: true
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: coverage-html, path: coverage/lcov-report }
</code></pre>
<p><strong>Vitest config with thresholds (<code>vitest.config.ts</code>):</strong></p>
<pre><code>import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'json-summary', 'html'],
      thresholds: { lines: 80, functions: 80, branches: 75, statements: 80 },
      exclude: ['node_modules/', 'dist/', '**/*.config.*', '**/*.d.ts'],
    },
  },
});
</code></pre>
<p><strong>How it&rsquo;s used:</strong></p>
<ul>
<li><strong>lcov</strong> &mdash; the universal format Codecov / Coveralls / SonarCloud all consume.</li>
<li><strong>html</strong> &mdash; uploaded as an artifact so reviewers can drill into uncovered lines.</li>
<li><strong>json-summary</strong> &mdash; the action posts a Markdown comment on the PR with file-level coverage diffs.</li>
<li><strong>thresholds</strong> &mdash; vitest fails the run if coverage drops below; combine with <em>Required status checks</em> to block merges.</li>
</ul>
<p><strong>Variants by language/runner:</strong></p>
<ul>
<li><strong>Jest</strong> &mdash; same flags; reporter <code>jest-junit</code> for test counts in PR.</li>
<li><strong>Python</strong> &mdash; <code>pytest --cov=src --cov-report=xml --cov-report=term-missing</code>; upload <code>coverage.xml</code>.</li>
<li><strong>Java + JaCoCo</strong> &mdash; <code>mvn verify</code> generates <code>target/site/jacoco/jacoco.xml</code>.</li>
<li><strong>Go</strong> &mdash; <code>go test -coverprofile=coverage.out ./... && go tool cover -func=coverage.out</code>.</li>
</ul>
<p><strong>Performance:</strong> per-PR <em>diff coverage</em> matters more than absolute coverage. Codecov&rsquo;s <code>codecov.yml</code> can require new code to be 80%+ covered without forcing 100% on the whole codebase. For the highest-confidence tests, layer mutation testing with <strong>Stryker</strong> on critical modules.</p>'''

ANSWERS[10] = r'''<pre><code>#!/usr/bin/env bash
# setup-jenkins.sh — provision a Jenkins controller with persistent state
set -euo pipefail

JENKINS_HOME=${JENKINS_HOME:-$PWD/jenkins-home}
IMAGE=jenkins/jenkins:lts-jdk21
CONTAINER=jenkins
PORT=${PORT:-8080}
AGENT_PORT=${AGENT_PORT:-50000}

mkdir -p "$JENKINS_HOME"
sudo chown -R 1000:1000 "$JENKINS_HOME"   # Jenkins UID inside the image

# Pull image and start
docker pull "$IMAGE"
docker rm -f "$CONTAINER" 2&gt;/dev/null || true
docker run -d --restart unless-stopped \
  --name "$CONTAINER" \
  -p "$PORT:8080" -p "$AGENT_PORT:50000" \
  -v "$JENKINS_HOME:/var/jenkins_home" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
  "$IMAGE"

# Wait for it to come up
echo "Waiting for Jenkins on http://localhost:$PORT ..."
until curl -fsS "http://localhost:$PORT/login" &gt;/dev/null 2&gt;&amp;1; do sleep 2; done

# Print initial admin password
echo "Initial admin password:"
docker exec "$CONTAINER" cat /var/jenkins_home/secrets/initialAdminPassword
</code></pre>
<p><strong>Companion <code>docker-compose.yml</code> (preferred for repeatable setup):</strong></p>
<pre><code>services:
  jenkins:
    image: jenkins/jenkins:lts-jdk21
    user: "1000:1000"
    ports: ["8080:8080", "50000:50000"]
    volumes:
      - jenkins-home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      JAVA_OPTS: -Djenkins.install.runSetupWizard=false
      CASC_JENKINS_CONFIG: /var/jenkins_home/casc.yaml
    restart: unless-stopped
volumes:
  jenkins-home:
</code></pre>
<p><strong>What this does:</strong></p>
<ul>
<li><strong>LTS image with JDK 21</strong> &mdash; supported &amp; modern.</li>
<li><strong>Bind-mounted <code>jenkins_home</code></strong> &mdash; survives container restarts; back this directory up regularly.</li>
<li><strong>Mounted Docker socket</strong> &mdash; lets Jenkins build images using the host&rsquo;s Docker daemon. Convenient but grants root-equivalent access; for hardened setups use rootless Buildkit, Kaniko, or the <strong>docker-in-docker</strong> sidecar pattern instead.</li>
<li><strong>Skip setup wizard</strong> &mdash; combine with <strong>Configuration as Code (JCasC)</strong> for fully reproducible config; declare admin user, plugins, security in YAML.</li>
</ul>
<p><strong>Variants &amp; production-grade options:</strong></p>
<ul>
<li><strong>JCasC</strong> + a plugin manifest checked into Git &mdash; restore an entire Jenkins from scratch in minutes.</li>
<li><strong>Helm chart on Kubernetes</strong> &mdash; <code>helm install jenkins jenkins/jenkins</code>; dynamic agents as Pods.</li>
<li><strong>For new projects in 2026</strong>, evaluate GitHub Actions / GitLab CI / Buildkite first &mdash; less infra to operate.</li>
</ul>
<p><strong>Backup:</strong> <code>tar -C $JENKINS_HOME -czf jenkins-$(date +%F).tgz .</code> nightly; or use the <em>thinBackup</em> plugin / Velero for K8s-resident installations.</p>'''

ANSWERS[11] = r'''<pre><code># configmap.yaml — non-secret config for an app
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: prod
data:
  NODE_ENV: production
  LOG_LEVEL: info
  PORT: "3000"
  FEATURE_FLAGS: "newCheckout=true,oldUI=false"
  app.json: |
    {
      "cacheTtlSeconds": 60,
      "rateLimit": { "windowMs": 60000, "max": 100 }
    }
---
# deployment-snippet.yaml — consume the ConfigMap two ways
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  template:
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          # 1) inject all keys as env vars
          envFrom:
            - configMapRef: { name: api-config }
          # 2) or pick specific keys
          env:
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef: { name: api-config, key: LOG_LEVEL }
          # 3) mount file-style keys as files
          volumeMounts:
            - name: app-config
              mountPath: /etc/app
              readOnly: true
      volumes:
        - name: app-config
          configMap:
            name: api-config
            items:
              - { key: app.json, path: app.json }
</code></pre>
<p><strong>Apply &amp; inspect:</strong></p>
<pre><code>kubectl apply -f configmap.yaml
kubectl get cm api-config -n prod -o yaml
kubectl create cm api-config --from-env-file=.env --dry-run=client -o yaml
</code></pre>
<p><strong>Three consumption patterns:</strong></p>
<ul>
<li><strong><code>envFrom</code></strong> &mdash; all keys become env vars at once; great for dump-and-go.</li>
<li><strong><code>env.valueFrom.configMapKeyRef</code></strong> &mdash; cherry-pick keys; useful for renaming.</li>
<li><strong>Volume mount</strong> &mdash; whole-file content (<code>app.json</code>) becomes a real file the app reads at boot.</li>
</ul>
<p><strong>Important caveats:</strong></p>
<ul>
<li><strong>Env-var ConfigMaps don&rsquo;t auto-reload</strong> &mdash; you must <code>kubectl rollout restart deployment/api</code> after changes. <strong>Mounted ConfigMaps</strong> <em>do</em> update on disk (~60s lag); the app must re-read the file.</li>
<li><strong>1 MB size limit</strong> per ConfigMap &mdash; chunk large config or use a real config service.</li>
<li><strong>Never put secrets here</strong> &mdash; use <code>Secret</code> or External Secrets Operator.</li>
</ul>
<p><strong>Variants:</strong> use <strong>Kustomize <code>configMapGenerator</code></strong> to auto-hash configmap names so a config change forces a rolling restart automatically; or <strong>Reloader</strong> (stakater/Reloader) to watch ConfigMaps and trigger restarts.</p>'''

ANSWERS[12] = r'''<pre><code># .github/workflows/docker.yml
name: Build & Push Docker
on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:

permissions:
  contents: read

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-qemu-action@v3   # for cross-platform builds
      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}     # access token, NOT password

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: acme/api
          tags: |
            type=ref,event=branch
            type=sha,prefix=
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable={{is_default_branch}}

      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true
</code></pre>
<p><strong>Setup &mdash; one-time:</strong></p>
<ol>
<li><em>Docker Hub &rarr; Account Settings &rarr; Security &rarr; New Access Token</em>; scope = <em>Read &amp; Write</em>.</li>
<li>GitHub repo &rarr; <em>Settings &rarr; Secrets and variables &rarr; Actions</em> &rarr; add <code>DOCKERHUB_USERNAME</code> and <code>DOCKERHUB_TOKEN</code>.</li>
</ol>
<p><strong>Why each piece:</strong></p>
<ul>
<li><strong><code>metadata-action</code></strong> &mdash; auto-generates a clean tag matrix: branch tag, short SHA, semver, <code>:latest</code> only on default branch &mdash; avoids hand-rolled tag scripts.</li>
<li><strong><code>buildx</code> + <code>qemu</code></strong> &mdash; build for amd64 and arm64 from a single workflow; M-series Macs and Graviton instances pull native arm64.</li>
<li><strong><code>cache-from/to: gha</code></strong> &mdash; layer cache stored in the GitHub cache; rebuilds 5&ndash;10&times; faster.</li>
<li><strong><code>provenance: true</code></strong> + <strong><code>sbom: true</code></strong> &mdash; SLSA build provenance and Software Bill of Materials attached as image manifests; required for many supply-chain compliance regimes.</li>
</ul>
<p><strong>Variants:</strong> swap to <strong>GHCR</strong> for ecosystem alignment (use <code>${{ secrets.GITHUB_TOKEN }}</code>, no extra creds). Add <code>aquasecurity/trivy-action</code> after build to fail on HIGH/CRITICAL CVEs. Sign the digest with <strong>Sigstore Cosign</strong> for verifiable images.</p>
<p><strong>Performance:</strong> avoid Docker Hub anonymous pull rate limits in <code>FROM</code> by switching to <code>FROM public.ecr.aws/docker/library/...</code> or pre-pulling via a registry mirror.</p>'''

ANSWERS[13] = r'''<pre><code>// Jenkinsfile — deploy a Python app to AWS Lambda (zip package)
pipeline {
  agent any
  options { timeout(time: 20, unit: 'MINUTES') }
  environment {
    AWS_REGION = 'us-east-1'
    FUNC       = 'api-handler'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Install &amp; test') {
      steps {
        sh &apos;&apos;&apos;
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pytest -q
        &apos;&apos;&apos;
      }
    }

    stage('Package') {
      steps {
        sh &apos;&apos;&apos;
          rm -rf build dist && mkdir build
          pip install --target build -r requirements.txt
          cp -r src/* build/
          (cd build && zip -qr ../dist/lambda.zip .)
          ls -lh dist/lambda.zip
        &apos;&apos;&apos;
        archiveArtifacts 'dist/lambda.zip'
      }
    }

    stage('Deploy to Lambda') {
      when { branch 'main' }
      steps {
        withCredentials([[
          $class: 'AmazonWebServicesCredentialsBinding',
          credentialsId: 'aws-deploy'
        ]]) {
          sh &apos;&apos;&apos;
            aws lambda update-function-code \
              --region $AWS_REGION \
              --function-name $FUNC \
              --zip-file fileb://dist/lambda.zip \
              --publish
            aws lambda wait function-updated --function-name $FUNC
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { echo "Deployed $FUNC" }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
  }
}
</code></pre>
<p><strong>Lambda handler (<code>src/handler.py</code>):</strong></p>
<pre><code>import json
def handler(event, context):
    return {"statusCode": 200, "body": json.dumps({"ok": True})}
</code></pre>
<p><strong>Variants &amp; better options for 2026:</strong></p>
<ul>
<li><strong>Container Lambda</strong> &mdash; build a Docker image (up to 10 GB, vs 250 MB zip), push to ECR, point Lambda at the image. Better for ML / big binaries / native deps.</li>
<li><strong>AWS SAM</strong> or <strong>AWS CDK</strong> &mdash; <code>sam deploy</code> / <code>cdk deploy</code> handle packaging, IaC, and rollouts in one step; recommended for greenfield Lambda.</li>
<li><strong>Lambda Layers</strong> &mdash; share libraries across functions instead of bundling per-function.</li>
<li><strong>Function URLs</strong> or API Gateway &mdash; for HTTP-triggered functions.</li>
</ul>
<p><strong>Performance:</strong> use <strong>provisioned concurrency</strong> for cold-start-sensitive endpoints; pin Python to <strong>3.13</strong> for newer runtime perf; tune memory upward for CPU (Lambda CPU scales linearly with memory).</p>'''

ANSWERS[14] = r'''<pre><code># ingress.yaml — host- and path-based routing to multiple services
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
  namespace: prod
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: 10m
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts: [acme.com, www.acme.com, api.acme.com]
      secretName: acme-tls
  rules:
    - host: acme.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: web, port: { number: 80 } } }
    - host: www.acme.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: web, port: { number: 80 } } }
    - host: api.acme.com
      http:
        paths:
          - path: /v1
            pathType: Prefix
            backend: { service: { name: api-v1, port: { number: 80 } } }
          - path: /v2
            pathType: Prefix
            backend: { service: { name: api-v2, port: { number: 80 } } }
          - path: /admin
            pathType: Prefix
            backend: { service: { name: admin, port: { number: 80 } } }
</code></pre>
<p><strong>Apply &amp; verify:</strong></p>
<pre><code>kubectl apply -f ingress.yaml
kubectl get ingress -n prod
kubectl describe ingress app -n prod
curl -I https://api.acme.com/v1/health
</code></pre>
<p><strong>Prerequisites:</strong></p>
<ul>
<li>An <strong>ingress controller</strong> installed in the cluster: <strong>NGINX Ingress</strong>, <strong>Traefik</strong>, <strong>HAProxy</strong>, or cloud-native (<strong>AWS Load Balancer Controller</strong> on EKS, <strong>GKE Gateway</strong>, <strong>AGIC</strong> on AKS).</li>
<li><strong>cert-manager</strong> for automated Let&rsquo;s Encrypt TLS &mdash; the annotation tells it to provision and renew certs.</li>
<li>DNS pointing the listed hostnames at the controller&rsquo;s LB IP.</li>
</ul>
<p><strong><code>pathType</code> options:</strong></p>
<ul>
<li><code>Prefix</code> &mdash; <code>/api</code> matches <code>/api/foo</code> (most common).</li>
<li><code>Exact</code> &mdash; matches only the literal path.</li>
<li><code>ImplementationSpecific</code> &mdash; controller-specific (regex on NGINX).</li>
</ul>
<p><strong>2026 alternative &mdash; Gateway API:</strong> the next-generation successor to Ingress with cleaner separation of roles, multi-protocol support (HTTP, gRPC, TCP), and better split traffic / canary primitives. Major implementations (Cilium, Istio, NGINX, Envoy Gateway) all ship Gateway API; prefer it for greenfield. Ingress remains supported but is no longer evolving.</p>
<p><strong>Performance / ops:</strong> set <code>proxy-body-size</code>, <code>proxy-read-timeout</code> via annotations; enable HTTP/2; for blue/green or canary use Argo Rollouts or NGINX&rsquo;s <code>canary-weight</code> annotation.</p>'''

ANSWERS[15] = r'''<pre><code># .github/workflows/ecs-deploy.yml
name: Deploy to ECS
on:
  push: { branches: [main] }

permissions:
  contents: read
  id-token: write          # OIDC for AWS

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    env:
      AWS_REGION:   us-east-1
      ECR_REPO:    123456789012.dkr.ecr.us-east-1.amazonaws.com/api
      ECS_CLUSTER: prod
      ECS_SERVICE: api
      CONTAINER:   api
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gh-deploy
          aws-region: ${{ env.AWS_REGION }}

      - uses: aws-actions/amazon-ecr-login@v2
        id: ecr

      - name: Build &amp; push image
        env: { TAG: ${{ github.sha }} }
        run: |
          docker build -t $ECR_REPO:$TAG -t $ECR_REPO:latest .
          docker push $ECR_REPO:$TAG
          docker push $ECR_REPO:latest

      - id: render
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ecs/task-def.json
          container-name: ${{ env.CONTAINER }}
          image: ${{ env.ECR_REPO }}:${{ github.sha }}

      - uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.render.outputs.task-definition }}
          cluster: ${{ env.ECS_CLUSTER }}
          service: ${{ env.ECS_SERVICE }}
          wait-for-service-stability: true
</code></pre>
<p><strong>One-time IAM setup (OIDC trust):</strong></p>
<ol>
<li>Create an IAM OIDC provider for <code>token.actions.githubusercontent.com</code>.</li>
<li>Create role <code>gh-deploy</code> trusted by the OIDC provider, scoped to your repo + branch via the <code>sub</code> claim (<code>repo:acme/api:ref:refs/heads/main</code>).</li>
<li>Attach minimal IAM permissions: ECR push, <code>ecs:UpdateService</code>, <code>ecs:RegisterTaskDefinition</code>, <code>iam:PassRole</code> for the task execution role.</li>
</ol>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Blue/green via CodeDeploy</strong> &mdash; set <code>deployment_controller</code> on the ECS service; use <code>aws-actions/amazon-ecs-deploy-task-definition</code> with <code>codedeploy-appspec</code>.</li>
<li><strong>Fargate</strong> &mdash; same workflow; just <code>launchType: FARGATE</code> in the task definition.</li>
<li><strong>EKS instead</strong> &mdash; add <code>aws eks update-kubeconfig</code> + <code>kubectl set image</code> + <code>kubectl rollout status</code>.</li>
<li><strong>App Runner / Copilot</strong> &mdash; for dev teams who want zero infra: <code>copilot deploy</code>.</li>
</ul>
<p><strong>Performance:</strong> use <code>cache-from/to: type=gha</code> on Buildx steps; pin task definition revision for instant rollback (<code>aws ecs update-service --task-definition api:42</code>); enable ECS Container Insights for built-in metrics.</p>'''

ANSWERS[16] = r'''<pre><code># Dockerfile — multi-stage build for a Spring Boot / Maven app
# --- Stage 1: build the jar
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src

# Cache deps before sources
COPY pom.xml .
RUN mvn -B dependency:go-offline

COPY src ./src
RUN mvn -B package -DskipTests &amp;&amp; \
    mv target/*.jar target/app.jar

# --- Stage 2: minimal runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Non-root user
RUN addgroup -S app &amp;&amp; adduser -S app -G app
USER app

COPY --from=build /src/target/app.jar app.jar

EXPOSE 8080
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75 -XX:+ExitOnOutOfMemoryError"
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
</code></pre>
<p><strong>Build &amp; run:</strong></p>
<pre><code>docker build -t acme/api:1.0.0 .
docker run -p 8080:8080 acme/api:1.0.0
docker images acme/api          # ~180 MB, vs ~600 MB single-stage
</code></pre>
<p><strong>Why this shape:</strong></p>
<ul>
<li><strong>Two stages</strong> &mdash; Maven + JDK in builder; only the small JRE in final image. Smaller image = faster pulls + smaller attack surface.</li>
<li><strong>Layer ordering</strong> &mdash; <code>pom.xml</code> + <code>dependency:go-offline</code> first so dependency layers cache; rebuilds after pure code changes are dramatically faster.</li>
<li><strong>Eclipse Temurin</strong> &mdash; the standard free OpenJDK distribution; alternatives are Amazon Corretto, Microsoft Build of OpenJDK, Azul Zulu, GraalVM (for native images).</li>
<li><strong>Non-root user</strong> + <strong>MaxRAMPercentage</strong> &mdash; defence-in-depth + container-aware heap sizing.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Distroless</strong> for production: <code>FROM gcr.io/distroless/java21-debian12</code> &mdash; even smaller, no shell.</li>
<li><strong>Gradle</strong>: replace builder stage with <code>FROM gradle:8-jdk21 AS build</code> + <code>RUN gradle bootJar --no-daemon</code>.</li>
<li><strong>Layered jar</strong> (Spring Boot): use <code>RUN java -Djarmode=layertools -jar app.jar extract</code> to split deps into separate layers, so app code rebuilds don&rsquo;t bust the deps layer.</li>
<li><strong>GraalVM native image</strong>: massive cold-start improvement (50ms vs 5s) at cost of slower builds; <code>FROM ghcr.io/graalvm/native-image-community:21</code> + <code>native-image</code>.</li>
</ul>
<p><strong>Performance:</strong> add a <code>.dockerignore</code> with <code>target/ .git/ .idea/ *.log</code> &mdash; cuts context size dramatically. Use BuildKit cache mount for Maven: <code>RUN --mount=type=cache,target=/root/.m2 mvn package</code>.</p>'''

ANSWERS[17] = r'''<pre><code>// Jenkinsfile — security scan a Docker image
pipeline {
  agent any
  options { timeout(time: 30, unit: 'MINUTES') }
  environment {
    IMAGE = "ghcr.io/acme/api:${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Build') {
      steps { sh "docker build -t $IMAGE ." }
    }

    stage('SCA + CVE scan (Trivy)') {
      steps {
        sh &apos;&apos;&apos;
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v $WORKSPACE:/work -w /work \
            aquasec/trivy:latest image \
              --severity HIGH,CRITICAL \
              --exit-code 1 \
              --format sarif \
              --output trivy.sarif \
              $IMAGE
        &apos;&apos;&apos;
      }
      post { always { archiveArtifacts 'trivy.sarif' } }
    }

    stage('Misconfig scan (Trivy config)') {
      steps {
        sh &apos;&apos;&apos;
          docker run --rm -v $WORKSPACE:/work -w /work \
            aquasec/trivy:latest config \
              --severity HIGH,CRITICAL --exit-code 1 .
        &apos;&apos;&apos;
      }
    }

    stage('Secret scan (Gitleaks)') {
      steps {
        sh &apos;&apos;&apos;
          docker run --rm -v $WORKSPACE:/scan zricethezav/gitleaks:latest \
            detect --source /scan --no-banner --redact
        &apos;&apos;&apos;
      }
    }

    stage('SBOM (Syft)') {
      steps {
        sh &apos;&apos;&apos;
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            -v $WORKSPACE:/work -w /work anchore/syft:latest \
            $IMAGE -o spdx-json=sbom.spdx.json
        &apos;&apos;&apos;
        archiveArtifacts 'sbom.spdx.json'
      }
    }

    stage('Sign (Cosign + keyless)') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          docker run --rm -v $HOME/.sigstore:/root/.sigstore \
            gcr.io/projectsigstore/cosign:v2 sign --yes $IMAGE
        &apos;&apos;&apos;
      }
    }
  }
  post {
    failure { slackSend channel: '#security', message: "❌ Scan failed: ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>What each step catches:</strong></p>
<ul>
<li><strong>Trivy image</strong> &mdash; OS package CVEs (apk/apt) + language-level deps (npm/pip/maven). <em>SCA + vuln scan in one tool.</em></li>
<li><strong>Trivy config</strong> &mdash; misconfigurations in Dockerfile (root user, latest tag, missing healthcheck) + Kubernetes manifests + Terraform.</li>
<li><strong>Gitleaks</strong> &mdash; secrets leaked in source / git history (AWS keys, API tokens, RSA keys).</li>
<li><strong>Syft</strong> &mdash; SPDX/CycloneDX SBOM listing every package in the image; required for SLSA / FedRAMP / EU CRA compliance.</li>
<li><strong>Cosign keyless signing</strong> &mdash; via Sigstore Fulcio; verifiable provenance without managing keys.</li>
</ul>
<p><strong>Variants:</strong> swap Trivy for <strong>Grype</strong> + <strong>Anchore</strong>; commercial: <strong>Snyk</strong>, <strong>Wiz</strong>, <strong>Sysdig Secure</strong>, <strong>Chainguard Enforce</strong>. For regulated workloads, integrate <strong>OPA Gatekeeper</strong> or <strong>Kyverno</strong> at the cluster admission layer to enforce &ldquo;only signed images allowed&rdquo;.</p>
<p><strong>Performance:</strong> cache the Trivy DB on the agent (<code>--cache-dir</code>) to avoid re-downloading vulnerability data each run; run scans in parallel <code>parallel { }</code> stages to overlap CPU and I/O.</p>'''

ANSWERS[18] = r'''<pre><code># mysql-statefulset.yaml — single primary, simple StatefulSet
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: db
spec:
  clusterIP: None        # headless &mdash; required for StatefulSet
  selector: { app: mysql }
  ports: [ { port: 3306, name: mysql } ]
---
apiVersion: v1
kind: Secret
metadata: { name: mysql-creds, namespace: db }
type: Opaque
stringData:
  MYSQL_ROOT_PASSWORD: rootSecret
  MYSQL_USER: app
  MYSQL_PASSWORD: appSecret
  MYSQL_DATABASE: app
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: mysql, namespace: db }
spec:
  serviceName: mysql
  replicas: 1
  selector: { matchLabels: { app: mysql } }
  template:
    metadata: { labels: { app: mysql } }
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: mysql
          image: mysql:8.4
          envFrom: [ { secretRef: { name: mysql-creds } } ]
          ports: [ { containerPort: 3306, name: mysql } ]
          args:
            - "--default-authentication-plugin=caching_sha2_password"
            - "--max-connections=500"
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
          readinessProbe:
            exec: { command: ["mysqladmin", "ping", "-h127.0.0.1", "-u$MYSQL_USER", "-p$MYSQL_PASSWORD"] }
            periodSeconds: 5
          resources:
            requests: { cpu: 250m, memory: 1Gi }
            limits:   { cpu: 1,    memory: 2Gi }
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: gp3
        resources: { requests: { storage: 50Gi } }
</code></pre>
<p><strong>Apply &amp; access:</strong></p>
<pre><code>kubectl apply -f mysql-statefulset.yaml
kubectl get pvc -n db                    # data-mysql-0 should be Bound
kubectl exec -it mysql-0 -n db -- mysql -uapp -p
# DNS: mysql-0.mysql.db.svc.cluster.local
</code></pre>
<p><strong>Why these patterns:</strong></p>
<ul>
<li><strong>StatefulSet</strong> &mdash; gives the Pod a stable name (<code>mysql-0</code>), stable DNS, and a stable PVC that survives restarts &mdash; critical for databases.</li>
<li><strong>Headless Service</strong> &mdash; required so Pods get individual DNS names; not used for load balancing here.</li>
<li><strong><code>volumeClaimTemplates</code></strong> &mdash; one PVC per Pod, named <code>data-mysql-0</code>; deleted only manually, even if you delete the StatefulSet.</li>
<li><strong>Reclaim policy</strong> &mdash; ensure your StorageClass uses <code>Retain</code> for production so a misclick doesn&rsquo;t lose data.</li>
</ul>
<p><strong>Variants for HA:</strong></p>
<ul>
<li><strong>InnoDB Cluster / Group Replication</strong> &mdash; multi-replica MySQL via the official <strong>MySQL Operator</strong>.</li>
<li><strong>Vitess</strong> &mdash; horizontal sharding for very large MySQL workloads.</li>
<li><strong>Percona Operator</strong> &mdash; battle-tested HA + backup automation.</li>
<li><strong>MariaDB Operator</strong> &mdash; alternative engine.</li>
</ul>
<p><strong>2026 advice:</strong> for production prefer a <strong>managed service</strong> (Amazon RDS, Aurora, Cloud SQL, Azure Database for MySQL) over self-hosting &mdash; you skip backup, point-in-time recovery, replication, version upgrades, and security patching. Self-host StatefulSets only when compliance / cost / data sovereignty demands.</p>'''

ANSWERS[19] = r'''<pre><code># .github/workflows/integration.yml
name: Integration Tests
on: [push, pull_request]

jobs:
  it:
    runs-on: ubuntu-latest
    services:
      mongo:
        image: mongo:7
        ports: [27017:27017]
        options: >-
          --health-cmd "mongosh --eval 'db.runCommand({ ping: 1 })'"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
      redis:
        image: redis:7
        ports: [6379:6379]
        options: --health-cmd "redis-cli ping" --health-interval 3s --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci

      - name: Build app image
        run: docker build -t app:test .

      - name: Run app container against services
        run: |
          docker run -d --name app \
            --network host \
            -e MONGO_URL=mongodb://localhost:27017/test \
            -e REDIS_URL=redis://localhost:6379 \
            app:test

          # Wait for app readiness
          for i in {1..30}; do
            if curl -fsS http://localhost:3000/healthz; then break; fi
            sleep 2
          done

      - name: Run integration tests against the container
        run: npm run test:integration
        env:
          API_URL: http://localhost:3000

      - name: Capture container logs on failure
        if: failure()
        run: docker logs app
</code></pre>
<p><strong>Why <code>services:</code> + <code>--network host</code>:</strong> GitHub&rsquo;s <code>services</code> block runs sidecar containers (Mongo, Redis) reachable from the runner on <code>localhost</code>; <code>--network host</code> lets the app container join the same network namespace so it too can reach them at <code>localhost</code>. Simpler than wiring a custom Docker network.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Docker Compose</strong> &mdash; if your test rig is complex, replace <code>services</code> + manual <code>docker run</code> with <code>docker compose up -d</code>; tests just call <code>http://localhost:3000</code>.</li>
<li><strong>Testcontainers</strong> &mdash; let test code itself spin up Docker dependencies (Postgres, Kafka, Selenium); supported in Java, Node, Python, Go. Most ergonomic option for IT in 2026.</li>
<li><strong>Ephemeral environments</strong> &mdash; for full e2e on real cloud, use <strong>Vercel Preview</strong>, <strong>Render PR Previews</strong>, or <strong>Argo CD ApplicationSet</strong> + ephemeral namespaces, then run e2e against the URL.</li>
</ul>
<p><strong>Performance:</strong> health-check options on services prevent flaky &ldquo;DB not ready&rdquo; failures. Use <code>npm ci --prefer-offline</code> with the <code>setup-node</code> cache. For long suites, shard with <code>matrix: { shard: [1, 2, 3, 4] }</code> + <code>--shard=${{ matrix.shard }}/4</code>.</p>'''

ANSWERS[20] = r'''<pre><code>#!/usr/bin/env bash
# jenkins-backup.sh — backup or restore Jenkins config + jobs
set -euo pipefail

ACTION=${1:-backup}                                       # backup | restore
JENKINS_HOME=${JENKINS_HOME:-/var/jenkins_home}
BACKUP_DIR=${BACKUP_DIR:-/backups/jenkins}
S3_BUCKET=${S3_BUCKET:-acme-jenkins-backups}
DATE=$(date +%F-%H%M)

backup() {
  mkdir -p "$BACKUP_DIR"
  ARCHIVE="$BACKUP_DIR/jenkins-$DATE.tar.gz"

  # Stop accepting new builds (optional but safer)
  curl -fsS -X POST "http://localhost:8080/quietDown" -u "$JENKINS_USER:$JENKINS_API_TOKEN" || true

  # Tar config + jobs + plugins; SKIP large or volatile state
  tar --exclude='workspace' \
      --exclude='caches' \
      --exclude='war' \
      --exclude='.cache' \
      --exclude='*/builds/*/archive' \
      -czf "$ARCHIVE" -C "$JENKINS_HOME" .

  curl -fsS -X POST "http://localhost:8080/cancelQuietDown" \
       -u "$JENKINS_USER:$JENKINS_API_TOKEN" || true

  # Off-site copy
  aws s3 cp "$ARCHIVE" "s3://$S3_BUCKET/$(basename "$ARCHIVE")"

  # Local retention &mdash; keep last 14 days
  find "$BACKUP_DIR" -name 'jenkins-*.tar.gz' -mtime +14 -delete

  echo "Backup complete: $ARCHIVE"
}

restore() {
  ARCHIVE=${2:-}
  [[ -z "$ARCHIVE" ]] &amp;&amp; { echo "Usage: $0 restore /path/to/jenkins-DATE.tar.gz"; exit 1; }

  systemctl stop jenkins   # or: docker stop jenkins
  rm -rf "$JENKINS_HOME"/*
  tar -xzf "$ARCHIVE" -C "$JENKINS_HOME"
  chown -R 1000:1000 "$JENKINS_HOME"
  systemctl start jenkins

  echo "Restore complete from $ARCHIVE"
}

case "$ACTION" in
  backup)  backup ;;
  restore) restore "$@" ;;
  *) echo "Unknown action: $ACTION"; exit 2 ;;
esac
</code></pre>
<p><strong>Schedule with cron:</strong></p>
<pre><code>0 2 * * * /usr/local/bin/jenkins-backup.sh backup &gt;&gt; /var/log/jenkins-backup.log 2&gt;&amp;1
</code></pre>
<p><strong>Why these flags:</strong></p>
<ul>
<li><strong>Quiet mode</strong> &mdash; <code>/quietDown</code> tells Jenkins to finish in-flight builds and stop scheduling new ones, avoiding mid-build snapshots.</li>
<li><strong>Excludes</strong> &mdash; <code>workspace</code>, <code>caches</code>, build archives are reproducible; including them blows up archive size needlessly. Backup focuses on configs, jobs, plugins, credentials, secrets.</li>
<li><strong>Off-site copy to S3</strong> &mdash; survives host loss; enable bucket versioning + Object Lock for ransomware protection.</li>
<li><strong>Retention</strong> &mdash; local 14 days, S3 longer (lifecycle rule).</li>
</ul>
<p><strong>Variants &amp; better options for 2026:</strong></p>
<ul>
<li><strong>thinBackup plugin</strong> &mdash; classic Jenkins plugin for scheduled backups; UI-driven; less control than scripts.</li>
<li><strong>Configuration as Code (JCasC)</strong> &mdash; declare Jenkins config in YAML checked into Git. Restore is &ldquo;reinstall + apply YAML&rdquo;. Best modern pattern.</li>
<li><strong>Velero</strong> &mdash; for Helm-installed Jenkins on Kubernetes, snapshot the PVC + manifests in one command.</li>
<li><strong>Job DSL</strong> &mdash; declare jobs as code; restore = re-run seed job.</li>
</ul>
<p><strong>Critical:</strong> <em>test restore quarterly</em>. Untested backups are guesses. Encrypt archives at rest (S3 SSE-KMS) since they contain credentials.</p>'''

ANSWERS[21] = r'''<pre><code># Dockerfile — Django app with gunicorn + multi-stage
# --- builder
FROM python:3.13-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends \
      build-essential libpq-dev &amp;&amp; rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# --- runtime
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PATH=/home/app/.local/bin:$PATH \
    DJANGO_SETTINGS_MODULE=app.settings.production
WORKDIR /app

# Runtime libs only (no compilers)
RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends \
      libpq5 curl &amp;&amp; rm -rf /var/lib/apt/lists/* &amp;&amp; \
    useradd -r -u 1000 app

COPY --from=builder /root/.local /home/app/.local
COPY --chown=app:app . .

USER app
EXPOSE 8000

# Run migrations + collectstatic at startup, then gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput &amp;&amp; \
     python manage.py collectstatic --noinput &amp;&amp; \
     gunicorn -w 4 -k gthread --threads 4 -b 0.0.0.0:8000 \
       --access-logfile - --error-logfile - app.wsgi"]
</code></pre>
<p><strong>Build &amp; run:</strong></p>
<pre><code>docker build -t myorg/django-app:1.0.0 .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgres://user:pw@db:5432/app \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  myorg/django-app:1.0.0
</code></pre>
<p><strong>Critical Django-in-Docker patterns:</strong></p>
<ul>
<li><strong>Migrations + collectstatic at startup</strong> &mdash; safe for single-replica; for multi-replica, run migrations once via a Kubernetes <strong>Job</strong> or initContainer, not in every Pod&rsquo;s CMD.</li>
<li><strong>Static files</strong> &mdash; in production, serve via WhiteNoise (in-process) or push to S3/CloudFront with <code>django-storages</code>; the Docker image just hosts the app.</li>
<li><strong>Settings split</strong> &mdash; <code>app.settings.production</code> with <code>DEBUG=False</code> + <code>ALLOWED_HOSTS</code> from env; never <code>DEBUG=True</code> in containers.</li>
<li><strong>Secret key from env</strong> &mdash; never bake into the image.</li>
<li><strong>Gunicorn worker model</strong> &mdash; <code>gthread</code> for IO-bound; <code>gevent</code>/<code>uvicorn.workers.UvicornWorker</code> for ASGI; <code>sync</code> for CPU-bound.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Async Django</strong> &mdash; switch to <code>uvicorn app.asgi:application --workers 4</code>.</li>
<li><strong>Distroless final stage</strong> &mdash; <code>FROM gcr.io/distroless/python3-debian12</code> for smallest image.</li>
<li><strong>uv</strong> instead of pip &mdash; 10&times; faster installs.</li>
<li><strong>Add Celery worker</strong> as a sibling service in Compose / K8s for background tasks; share the same image.</li>
</ul>
<p><strong>Performance:</strong> use <code>--mount=type=cache,target=/root/.cache/pip</code> in the builder stage for cached pip downloads. <code>collectstatic --noinput</code> can be slow with huge static dirs &mdash; bake static files into a separate image at build time and serve via nginx.</p>'''

ANSWERS[22] = r'''<pre><code># job.yaml — one-time data migration job
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate-2026-05-02
  namespace: prod
spec:
  backoffLimit: 3                # retry up to 3 times on failure
  ttlSecondsAfterFinished: 86400 # auto-clean Pod 24h after finish
  activeDeadlineSeconds: 1800    # kill if it runs &gt; 30 min
  template:
    spec:
      restartPolicy: Never       # required for Jobs (or OnFailure)
      containers:
        - name: migrate
          image: ghcr.io/acme/api:1.2.3
          command: ["npm", "run", "migrate"]
          envFrom:
            - secretRef: { name: api-secrets }
            - configMapRef: { name: api-config }
          resources:
            requests: { cpu: 100m, memory: 256Mi }
            limits:   { cpu: 500m, memory: 512Mi }
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
---
# parallel-job.yaml — fan out N parallel workers
apiVersion: batch/v1
kind: Job
metadata: { name: bulk-import, namespace: prod }
spec:
  parallelism: 5         # run 5 Pods at once
  completions: 20        # need 20 successful Pods total
  completionMode: Indexed   # each Pod gets JOB_COMPLETION_INDEX 0..19
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: worker
          image: ghcr.io/acme/importer:1.0.0
          env:
            - { name: SHARD, valueFrom: { fieldRef: { fieldPath: metadata.annotations['batch.kubernetes.io/job-completion-index'] } } }
</code></pre>
<p><strong>Run, watch, inspect:</strong></p>
<pre><code>kubectl apply -f job.yaml
kubectl get jobs -n prod
kubectl describe job db-migrate-2026-05-02 -n prod
kubectl logs -f -l job-name=db-migrate-2026-05-02 -n prod
kubectl wait --for=condition=complete job/db-migrate-2026-05-02 -n prod --timeout=10m
</code></pre>
<p><strong>Key fields:</strong></p>
<ul>
<li><strong><code>backoffLimit</code></strong> &mdash; how many failures before the Job is marked failed.</li>
<li><strong><code>ttlSecondsAfterFinished</code></strong> &mdash; auto-cleanup; otherwise old Job Pods linger forever.</li>
<li><strong><code>activeDeadlineSeconds</code></strong> &mdash; hard timeout, kills runaway jobs.</li>
<li><strong><code>parallelism</code> + <code>completions</code></strong> &mdash; fan-out for embarrassingly parallel work.</li>
<li><strong><code>completionMode: Indexed</code></strong> &mdash; gives each Pod a stable index (0..N-1) so workers can shard work deterministically.</li>
</ul>
<p><strong>Job vs CronJob vs Argo Workflows:</strong></p>
<ul>
<li><strong>Job</strong> &mdash; one-shot.</li>
<li><strong>CronJob</strong> &mdash; scheduled Job (nightly backups, daily cleanup).</li>
<li><strong>Argo Workflows</strong> / <strong>Tekton</strong> / <strong>Volcano</strong> &mdash; for DAGs of jobs (data pipelines, ML training); built on top of Pods with rich features (parameters, artifacts, retries, parallel branches).</li>
<li><strong>Temporal</strong> &mdash; durable workflow orchestration if you need long-running stateful business processes.</li>
</ul>
<p><strong>Performance:</strong> set <code>resources.requests</code> &mdash; the scheduler reserves capacity. For huge fan-outs, set <code>parallelism</code> based on cluster capacity / external rate limits to avoid thundering herds.</p>'''

ANSWERS[23] = r'''<pre><code># .github/workflows/heroku-deploy.yml
name: Deploy to Heroku
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions: { contents: read }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # full history; Heroku rejects shallow

      # Container approach (recommended) &mdash; modern, language-agnostic
      - name: Login to Heroku Container Registry
        run: echo "${{ secrets.HEROKU_API_KEY }}" | \
             docker login --username=_ --password-stdin registry.heroku.com

      - name: Build &amp; push web image
        env: { APP: ${{ secrets.HEROKU_APP_NAME }} }
        run: |
          docker build -t registry.heroku.com/$APP/web .
          docker push registry.heroku.com/$APP/web

      - name: Release container
        env:
          APP: ${{ secrets.HEROKU_APP_NAME }}
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
        run: |
          heroku container:release web -a $APP

      - name: Run migrations
        env: { HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }} }
        run: heroku run -a ${{ secrets.HEROKU_APP_NAME }} -- npm run migrate
</code></pre>
<p><strong>Companion <code>Dockerfile</code> for Heroku container:</strong></p>
<pre><code>FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
# Heroku injects PORT &mdash; respect it
CMD ["sh", "-c", "node server.js"]
</code></pre>
<p><strong>Two deployment models:</strong></p>
<table>
<tr><th></th><th>Container</th><th>Buildpacks (git push)</th></tr>
<tr><td>Mechanism</td><td>Push Docker image to <code>registry.heroku.com</code>, release</td><td><code>git push heroku main</code> + auto-detect</td></tr>
<tr><td>Control</td><td>Full Dockerfile control</td><td>Heroku decides build steps</td></tr>
<tr><td>Best for</td><td>Custom runtimes, native deps</td><td>Standard Node/Ruby/Python apps</td></tr>
</table>
<p><strong>Buildpack alternative</strong> via the popular community action:</p>
<pre><code>- uses: akhileshns/heroku-deploy@v3.13.15
  with:
    heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
    heroku_app_name: my-app
    heroku_email: ${{ secrets.HEROKU_EMAIL }}
</code></pre>
<p><strong>2026 reality:</strong> Heroku still works but is no longer the obvious default. Strong alternatives have emerged: <strong>Render</strong>, <strong>Fly.io</strong>, <strong>Railway</strong>, <strong>Vercel</strong>, <strong>Cloud Run</strong>, <strong>App Runner</strong>, <strong>DigitalOcean App Platform</strong> &mdash; all offer container-or-buildpack deploys with similar UX, often at lower cost. For new projects, evaluate before committing.</p>
<p><strong>Performance / ops:</strong> use a <strong>Heroku Pipeline</strong> (review apps + staging + production) for safer deploys; combine with <strong>Heroku Postgres</strong> for managed DB; enable <strong>Preboot</strong> for zero-downtime restarts.</p>'''

ANSWERS[24] = r'''<pre><code>// Jenkinsfile &mdash; .NET Core build &amp; deploy to Azure App Service
pipeline {
  agent any
  options { timeout(time: 30, unit: 'MINUTES') }
  environment {
    DOTNET_VERSION = '8.0.x'
    AZURE_APP      = 'acme-api'
    AZURE_RG       = 'prod-rg'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Setup .NET SDK') {
      steps {
        sh &apos;&apos;&apos;
          curl -sSL https://dot.net/v1/dotnet-install.sh -o install.sh
          chmod +x install.sh
          ./install.sh --channel $DOTNET_VERSION --install-dir $HOME/dotnet
          export PATH=$HOME/dotnet:$PATH
          dotnet --info
        &apos;&apos;&apos;
      }
    }

    stage('Restore &amp; build') {
      steps {
        sh &apos;&apos;&apos;
          export PATH=$HOME/dotnet:$PATH
          dotnet restore
          dotnet build --configuration Release --no-restore
        &apos;&apos;&apos;
      }
    }

    stage('Test') {
      steps {
        sh &apos;&apos;&apos;
          export PATH=$HOME/dotnet:$PATH
          dotnet test --configuration Release --no-build \
            --logger "trx;LogFileName=results.trx" \
            --collect:"XPlat Code Coverage"
        &apos;&apos;&apos;
      }
      post { always { mstest testResultsFile: '**/*.trx' } }
    }

    stage('Publish') {
      steps {
        sh &apos;&apos;&apos;
          export PATH=$HOME/dotnet:$PATH
          dotnet publish src/Api/Api.csproj \
            -c Release -o publish --no-build
          (cd publish &amp;&amp; zip -qr ../app.zip .)
        &apos;&apos;&apos;
        archiveArtifacts 'app.zip'
      }
    }

    stage('Deploy to Azure App Service') {
      when { branch 'main' }
      steps {
        withCredentials([azureServicePrincipal('azure-sp')]) {
          sh &apos;&apos;&apos;
            az login --service-principal \
              -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET \
              --tenant $AZURE_TENANT_ID
            az webapp deploy \
              --resource-group $AZURE_RG \
              --name $AZURE_APP \
              --src-path app.zip --type zip
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { slackSend channel: '#deploys', message: "✅ ${env.JOB_NAME}" }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>Setup &mdash; one-time on Azure:</strong></p>
<ol>
<li><code>az ad sp create-for-rbac --name jenkins-deploy --role contributor --scopes /subscriptions/SUBID/resourceGroups/prod-rg</code> &mdash; produces a service principal.</li>
<li>In Jenkins, install the <strong>Azure Credentials</strong> plugin and add the SP details as credential <code>azure-sp</code>.</li>
<li>Pre-create the App Service: <code>az webapp create --runtime "DOTNETCORE:8.0" ...</code>.</li>
</ol>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Containerised</strong> &mdash; build a Docker image, push to ACR, then <code>az webapp config container set ...</code>; cleaner for non-Windows runtimes.</li>
<li><strong>Azure Container Apps / AKS</strong> &mdash; for richer scaling, prefer these over Web App.</li>
<li><strong>GitHub Actions</strong> equivalent uses <code>azure/login</code> + <code>azure/webapps-deploy</code> &mdash; usually less friction than Jenkins for greenfield.</li>
<li><strong>OIDC federation</strong> &mdash; on GitHub Actions you can drop the SP secret entirely; on Jenkins, still need stored creds.</li>
</ul>
<p><strong>Performance:</strong> cache <code>~/.nuget/packages</code> on the agent; build with <code>--no-restore --no-build</code> in later stages to avoid duplicate work; use <code>dotnet publish -p:PublishReadyToRun=true</code> for faster cold starts.</p>'''

ANSWERS[25] = r'''<pre><code># secret.yaml &mdash; three creation methods + consumption pattern
---
# Method 1: declarative YAML with stringData (auto-encoded)
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: prod
type: Opaque
stringData:
  DB_PASSWORD: hunter2_strong_pw
  JWT_SECRET: 'a1b2c3d4e5f6...'
  STRIPE_KEY: sk_live_xxxx
---
# Method 2: TLS secret for ingress
apiVersion: v1
kind: Secret
metadata: { name: acme-tls, namespace: prod }
type: kubernetes.io/tls
data:
  tls.crt: LS0tLS1CRUdJTi...   # base64
  tls.key: LS0tLS1CRUdJTi...
---
# Method 3: docker registry secret
apiVersion: v1
kind: Secret
metadata: { name: ghcr-pull, namespace: prod }
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: eyJhdXRocyI6...
---
# Consume in a Deployment
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  template:
    spec:
      imagePullSecrets:
        - { name: ghcr-pull }
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          envFrom:
            - secretRef: { name: api-secrets }
          env:
            - name: STRIPE_KEY
              valueFrom:
                secretKeyRef: { name: api-secrets, key: STRIPE_KEY }
          volumeMounts:
            - { name: tls, mountPath: /etc/tls, readOnly: true }
      volumes:
        - name: tls
          secret: { secretName: acme-tls }
</code></pre>
<p><strong>Imperative creation:</strong></p>
<pre><code>kubectl create secret generic api-secrets \
  --from-literal=DB_PASSWORD=hunter2 \
  --from-literal=JWT_SECRET=$(openssl rand -hex 32) \
  -n prod

kubectl create secret tls acme-tls --cert=tls.crt --key=tls.key -n prod

kubectl create secret docker-registry ghcr-pull \
  --docker-server=ghcr.io \
  --docker-username=USER --docker-password=$GITHUB_TOKEN -n prod
</code></pre>
<p><strong>Critical caveats:</strong></p>
<ul>
<li><strong>Base64 is not encryption.</strong> Anyone with API access can <code>kubectl get secret -o yaml | base64 -d</code>. Enable etcd encryption-at-rest (managed clusters do this).</li>
<li><strong>RBAC matters most</strong> &mdash; restrict <code>get/list secrets</code> to a tiny set of identities.</li>
<li><strong>Never commit raw Secret YAML to Git</strong> &mdash; use Sealed Secrets or SOPS-encrypted manifests if you must.</li>
</ul>
<p><strong>2026 best practice &mdash; external secret stores:</strong></p>
<table>
<tr><th>Tool</th><th>Pattern</th></tr>
<tr><td><strong>External Secrets Operator</strong></td><td>Sync from AWS Secrets Manager / GCP Secret Manager / Vault / Doppler / Infisical &rarr; native K8s Secret</td></tr>
<tr><td><strong>CSI Secrets Store Driver</strong></td><td>Mount secrets directly from a vault into Pod files; no K8s Secret object</td></tr>
<tr><td><strong>Sealed Secrets</strong></td><td>Encrypt Secret manifests so they&rsquo;re safe to Git-commit; controller decrypts</td></tr>
<tr><td><strong>Vault Agent Injector</strong></td><td>Sidecar fetches and writes secrets into a shared volume</td></tr>
</table>
<p>Source-of-truth lives in a hardened secret manager with audit + rotation; Kubernetes gets just-in-time copies. This pattern eliminates the &ldquo;don&rsquo;t commit secrets&rdquo; problem entirely.</p>'''

ANSWERS[26] = r'''<pre><code># .github/workflows/branch-build.yml
name: Branch CI
on:
  push:
    branches:
      - main
      - 'release/**'        # release branches
      - 'feature/**'        # feature branches
    paths:
      - 'src/**'
      - 'package*.json'
      - '.github/workflows/**'
    paths-ignore:
      - '**.md'
      - 'docs/**'
  workflow_dispatch:        # manual run with a button

concurrency:
  group: branch-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test
      - run: npm run build
        env:
          BRANCH: ${{ github.ref_name }}
          IS_MAIN: ${{ github.ref == 'refs/heads/main' }}
</code></pre>
<p><strong>Trigger filters explained:</strong></p>
<ul>
<li><strong><code>branches</code></strong> &mdash; supports glob patterns: <code>main</code>, <code>release/**</code>, <code>feature/**</code>; use <code>branches-ignore</code> for the inverse.</li>
<li><strong><code>paths</code> / <code>paths-ignore</code></strong> &mdash; only fire when files in those globs change. <em>Critical for monorepos</em> &mdash; avoids running 50 service builds when one README changes.</li>
<li><strong><code>tags</code></strong> &mdash; trigger on tag push, e.g. <code>tags: ['v*']</code> for release pipelines.</li>
<li><strong><code>workflow_dispatch</code></strong> &mdash; manual button in the Actions UI; supports inputs.</li>
</ul>
<p><strong>Other useful triggers:</strong></p>
<pre><code>on:
  pull_request: { types: [opened, synchronize, reopened] }
  schedule: [{ cron: '0 6 * * 1' }]                 # Mondays 06:00 UTC
  release: { types: [published] }
  issue_comment: { types: [created] }                # /deploy bot
  repository_dispatch: { types: [external-trigger] } # API-triggered
  workflow_run:                                       # chain workflows
    workflows: ['Test']
    types: [completed]
    branches: [main]
</code></pre>
<p><strong>Conditional jobs/steps:</strong></p>
<pre><code>jobs:
  release:
    if: github.ref == 'refs/heads/main' &amp;&amp; github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - if: contains(github.event.head_commit.message, '[skip release]') == false
        run: ./release.sh
</code></pre>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>PR-targeted</strong>: <code>pull_request: { branches: [main] }</code> only fires for PRs into <code>main</code>.</li>
<li><strong>Draft-aware</strong>: <code>if: github.event.pull_request.draft == false</code> skips draft PRs to save runners.</li>
<li><strong>Fork-safe</strong>: use <code>pull_request_target</code> only when needed (it gets repo secrets &mdash; potentially dangerous with untrusted PRs).</li>
</ul>
<p><strong>Performance:</strong> <code>concurrency.cancel-in-progress: true</code> kills superseded runs on rapid pushes; <code>paths</code> filters cut spurious runs in monorepos by 50&ndash;90%; for very large monorepos use <strong>Nx Affected</strong> or <strong>Turbo</strong> change-detection inside the job.</p>'''

ANSWERS[27] = r'''<pre><code># docker-compose.yml &mdash; full local dev stack
name: acme-dev

services:
  api:
    build: ./api
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgresql://app:secret@db:5432/app
      REDIS_URL: redis://cache:6379
      QUEUE_URL: amqp://guest:guest@queue:5672
      LOG_LEVEL: debug
    depends_on:
      db:    { condition: service_healthy }
      cache: { condition: service_started }
      queue: { condition: service_healthy }
    develop:
      watch:
        - { action: sync,    path: ./api/src,         target: /app/src }
        - { action: rebuild, path: ./api/package.json }

  web:
    build: ./web
    ports: ["5173:5173"]
    environment:
      VITE_API_URL: http://localhost:3000
    develop:
      watch:
        - { action: sync, path: ./web/src, target: /app/src }

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    ports: ["5432:5432"]
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 10

  cache:
    image: redis:7-alpine
    ports: ["6379:6379"]

  queue:
    image: rabbitmq:3-management-alpine
    ports: ["5672:5672", "15672:15672"]
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      retries: 5

  mail:
    image: mailhog/mailhog
    ports: ["1025:1025", "8025:8025"]    # SMTP + UI
    profiles: [tools]                     # opt-in only

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: dev@local
      PGADMIN_DEFAULT_PASSWORD: dev
    ports: ["5050:80"]
    profiles: [tools]

volumes:
  db-data: {}
</code></pre>
<p><strong>Run it:</strong></p>
<pre><code>docker compose up -d                  # core services
docker compose --profile tools up -d  # core + tools (mailhog, pgadmin)
docker compose watch                  # live-reload on file save (v2.22+)
docker compose logs -f api            # tail one service
docker compose down -v                # stop and remove volumes (full reset)
</code></pre>
<p><strong>Patterns that pay off:</strong></p>
<ul>
<li><strong>Service DNS</strong> &mdash; containers reach each other by service name (<code>db</code>, <code>cache</code>) automatically; no port publishing required for inter-service calls.</li>
<li><strong>Health-checked startup</strong> &mdash; <code>depends_on.condition: service_healthy</code> blocks dependent services until DB is actually ready, eliminating boot-race flakes.</li>
<li><strong>Init scripts</strong> &mdash; mount SQL into <code>/docker-entrypoint-initdb.d</code> for first-run schema seeding.</li>
<li><strong>Compose Watch</strong> &mdash; sync source changes into running containers; rebuild only when manifests change. Eliminates Dockerfile-thrashing in dev.</li>
<li><strong>Profiles</strong> &mdash; <code>profiles: [tools]</code> means MailHog and pgAdmin only start when explicitly requested, keeping the default boot fast.</li>
</ul>
<p><strong>Variants:</strong> for offline-friendly dev, mount node_modules as a named volume so it persists across rebuilds. For team-wide consistency, commit a <code>.env.example</code>; use <code>docker compose --env-file .env.local</code>.</p>
<p><strong>Don&rsquo;t use Compose for prod at scale</strong> &mdash; reach for Kubernetes / ECS / a PaaS. Compose excels at local dev and CI integration testing.</p>'''

ANSWERS[28] = r'''<pre><code># hpa.yaml &mdash; autoscaler driven by CPU + memory + custom metric
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
  namespace: prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 30
  metrics:
    # 1) Built-in resource metrics (requires metrics-server)
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
    - type: Resource
      resource:
        name: memory
        target: { type: Utilization, averageUtilization: 80 }

    # 2) Custom metric from Prometheus Adapter (requests/sec/pod)
    - type: Pods
      pods:
        metric: { name: http_requests_per_second }
        target: { type: AverageValue, averageValue: "100" }

  # Scale-up fast, scale-down slow &mdash; avoid flapping
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100        # double pods
          periodSeconds: 30
        - type: Pods
          value: 4          # OR add 4 pods
          periodSeconds: 30
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300   # wait 5 min before scaling down
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
</code></pre>
<p><strong>Apply &amp; observe:</strong></p>
<pre><code>kubectl apply -f hpa.yaml
kubectl get hpa -n prod -w
kubectl describe hpa api -n prod
kubectl top pods -n prod -l app=api
</code></pre>
<p><strong>Prerequisites:</strong></p>
<ul>
<li><strong>metrics-server</strong> installed (most managed K8s clusters have it).</li>
<li>The target Deployment&rsquo;s containers <strong>must declare <code>resources.requests</code></strong> (CPU/memory) &mdash; HPA computes utilisation as <em>actual / requested</em>.</li>
<li>For custom metrics: <strong>prometheus-adapter</strong> or <strong>KEDA</strong> exposing your metric to the metrics API.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>KEDA</strong> &mdash; event-driven autoscaling: scale on Kafka lag, SQS depth, Redis queue length, cron, HTTP RPS, and 60+ scalers. Includes <em>scale to zero</em>, which native HPA doesn&rsquo;t support. The 2026 default for non-CPU triggers.</li>
<li><strong>VerticalPodAutoscaler (VPA)</strong> &mdash; adjusts <em>requests</em> rather than replica count; useful for right-sizing batch workloads.</li>
<li><strong>Cluster Autoscaler / Karpenter</strong> &mdash; complementary; HPA adds Pods, these add nodes when the cluster runs out of capacity. Karpenter is the modern AWS choice (faster, smarter bin-packing).</li>
</ul>
<p><strong>Performance / ops:</strong> for traffic-driven services, drive HPA off latency or RPS-per-pod, not CPU; CPU lags behind real load. The <code>behavior</code> block is the antidote to <em>flapping</em>: scale up aggressively (avoid SLO breach), scale down slowly (avoid yo-yo). Always combine HPA with a <strong>PodDisruptionBudget</strong> so cluster operations don&rsquo;t take you below <code>minReplicas</code>.</p>'''

ANSWERS[29] = r'''<pre><code># .github/workflows/lambda-flask.yml
name: Deploy Flask to Lambda
on:
  push: { branches: [main] }

permissions:
  contents: read
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    env:
      AWS_REGION: us-east-1
      FUNC: flask-api
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv pip install --system -r requirements.txt --target package
      - run: cp -r src/* package/ &amp;&amp; cd package &amp;&amp; zip -qr ../lambda.zip .

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gh-deploy
          aws-region: ${{ env.AWS_REGION }}

      - run: |
          aws lambda update-function-code \
            --function-name $FUNC \
            --zip-file fileb://lambda.zip \
            --publish
          aws lambda wait function-updated --function-name $FUNC
</code></pre>
<p><strong>Lambda handler with Flask via Mangum-style wrapper (<code>src/app.py</code>):</strong></p>
<pre><code>from flask import Flask
from awslambdaric.lambda_runtime_client import LambdaRuntimeClient   # included
import serverless_wsgi   # `pip install serverless-wsgi`

app = Flask(__name__)

@app.get("/")
def home():
    return {"status": "ok"}

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
</code></pre>
<p><strong>Why the Lambda Web Adapter is often better:</strong></p>
<pre><code># Dockerfile using AWS Lambda Web Adapter
FROM public.ecr.aws/docker/library/python:3.13-slim
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 \
     /lambda-adapter /opt/extensions/lambda-adapter
WORKDIR /var/task
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PORT=8000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "app:app"]
</code></pre>
<p>The <strong>Lambda Web Adapter</strong> lets you deploy <em>any</em> HTTP server (Flask, FastAPI, Express) to Lambda unchanged &mdash; no wrappers, no per-framework adapters. Often the cleanest option in 2026.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Container Lambda</strong> &mdash; up to 10 GB image (vs 250 MB zip); right for ML or large native deps.</li>
<li><strong>SAM</strong> &mdash; <code>sam deploy</code> handles packaging + IaC + API Gateway in one step.</li>
<li><strong>SST / Serverless Framework</strong> &mdash; higher-level frameworks for serverless deployments.</li>
<li><strong>Function URL</strong> &mdash; built-in HTTPS endpoint without API Gateway; fastest cold path.</li>
</ul>
<p><strong>Performance:</strong> use <strong>provisioned concurrency</strong> for cold-start-sensitive endpoints; <strong>Lambda SnapStart</strong> for Java; bump memory for CPU (it scales linearly). For sustained traffic, evaluate <strong>App Runner</strong> or <strong>Cloud Run</strong> &mdash; they&rsquo;re often cheaper and simpler than Lambda at high RPS.</p>'''

ANSWERS[30] = r'''<pre><code>// Jenkinsfile &mdash; Ruby on Rails: build, test, deploy
pipeline {
  agent any
  tools {
    // requires the &lsquo;rbenv&rsquo; or &lsquo;asdf&rsquo; tool plugin, or use a Docker agent
  }
  options { timeout(time: 30, unit: 'MINUTES') }
  environment {
    RAILS_ENV = 'production'
    BUNDLE_PATH = 'vendor/bundle'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Build') {
      steps {
        sh &apos;&apos;&apos;
          gem install bundler --no-document
          bundle config set --local path "$BUNDLE_PATH"
          bundle install --jobs=4 --retry=3
          yarn install --frozen-lockfile
          bundle exec rails assets:precompile
        &apos;&apos;&apos;
      }
    }

    stage('Test') {
      parallel {
        stage('RSpec') {
          steps {
            sh &apos;&apos;&apos;
              bundle exec rails db:create db:schema:load
              bundle exec rspec --format documentation \
                --format RspecJunitFormatter --out tmp/rspec.xml
            &apos;&apos;&apos;
          }
          post { always { junit 'tmp/rspec.xml' } }
        }
        stage('Lint') {
          steps {
            sh 'bundle exec rubocop'
            sh 'bundle exec brakeman --no-pager'   # security scan
          }
        }
        stage('System tests') {
          steps {
            sh 'bundle exec rails test:system'
          }
        }
      }
    }

    stage('Build container') {
      steps {
        sh &apos;&apos;&apos;
          docker build -t ghcr.io/acme/rails:${GIT_COMMIT::7} \
            --build-arg RAILS_ENV=production .
        &apos;&apos;&apos;
      }
    }

    stage('Push &amp; deploy') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr',
            usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login ghcr.io -u $U --password-stdin'
          sh 'docker push ghcr.io/acme/rails:${GIT_COMMIT::7}'
        }
        sh &apos;&apos;&apos;
          kubectl set image deployment/rails \
            rails=ghcr.io/acme/rails:${GIT_COMMIT::7} -n prod
          kubectl rollout status deployment/rails -n prod --timeout=10m

          # Run migrations as a Job so they don&rsquo;t run on every Pod
          kubectl create job --from=cronjob/rails-migrate \
            rails-migrate-${GIT_COMMIT::7} -n prod || true
        &apos;&apos;&apos;
      }
    }
  }
  post {
    always { sh 'docker logout ghcr.io || true' }
    success { slackSend channel: '#deploys', message: "✅ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>Companion <code>Dockerfile</code> (multi-stage, jemalloc + bootsnap):</strong></p>
<pre><code>FROM ruby:3.3-slim AS build
WORKDIR /app
RUN apt-get update &amp;&amp; apt-get install -y build-essential libpq-dev nodejs yarn git
COPY Gemfile* ./
RUN bundle config set --local without 'development test' &amp;&amp; bundle install
COPY package*.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN bundle exec rails assets:precompile

FROM ruby:3.3-slim
RUN apt-get update &amp;&amp; apt-get install -y libpq5 libjemalloc2 &amp;&amp; rm -rf /var/lib/apt/lists/*
ENV LD_PRELOAD=libjemalloc.so.2 RAILS_LOG_TO_STDOUT=1 RAILS_SERVE_STATIC_FILES=1
WORKDIR /app
COPY --from=build /app /app
USER 1000
EXPOSE 3000
CMD ["bundle", "exec", "puma", "-C", "config/puma.rb"]
</code></pre>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Kamal</strong> (formerly MRSK) &mdash; the Rails-team-recommended deploy tool for non-K8s servers in 2026; SSH-based, very simple.</li>
<li><strong>Heroku / Render / Fly.io</strong> &mdash; PaaS options if you want to skip K8s.</li>
<li><strong>Sidekiq workers</strong> as a sibling Deployment; share the image, override the entrypoint.</li>
</ul>
<p><strong>Performance:</strong> <strong>Bootsnap</strong> + <strong>jemalloc</strong> shave 30&ndash;50% off boot/memory. For database migrations, run them <em>once</em> via a Job, not on every Pod start.</p>'''

ANSWERS[31] = r'''<pre><code># pv-pvc.yaml
---
# Static PV (NFS-backed; pre-provisioned by an admin)
apiVersion: v1
kind: PersistentVolume
metadata: { name: nfs-archive }
spec:
  capacity: { storage: 500Gi }
  accessModes: [ReadWriteMany]
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs-archive
  nfs:
    server: nfs.acme.local
    path: /export/archive

---
# StorageClass for dynamic provisioning (cloud-typical)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: gp3 }
provisioner: ebs.csi.aws.com         # GKE: pd.csi.storage.gke.io / AKS: disk.csi.azure.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
reclaimPolicy: Retain                # Retain &mdash; keep disk after PVC delete
volumeBindingMode: WaitForFirstConsumer  # bind only when a Pod is scheduled
allowVolumeExpansion: true

---
# PVC consuming the StorageClass &mdash; PV is dynamically provisioned
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: prod
spec:
  storageClassName: gp3
  accessModes: [ReadWriteOnce]
  resources:
    requests: { storage: 100Gi }

---
# PVC for the static NFS PV (selector matches by storageClassName)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: archive
  namespace: backup
spec:
  storageClassName: nfs-archive
  accessModes: [ReadWriteMany]
  resources:
    requests: { storage: 500Gi }

---
# Mount the PVC into a Pod
apiVersion: apps/v1
kind: Deployment
metadata: { name: postgres, namespace: prod }
spec:
  template:
    spec:
      containers:
        - name: postgres
          image: postgres:16
          volumeMounts:
            - { name: data, mountPath: /var/lib/postgresql/data }
      volumes:
        - name: data
          persistentVolumeClaim: { claimName: postgres-data }
</code></pre>
<p><strong>Apply &amp; verify:</strong></p>
<pre><code>kubectl apply -f pv-pvc.yaml
kubectl get sc,pv,pvc -A
kubectl describe pvc postgres-data -n prod
</code></pre>
<p><strong>Key concepts:</strong></p>
<ul>
<li><strong>StorageClass</strong> = template for dynamic provisioning (cloud-typical).</li>
<li><strong>PV</strong> = the cluster-level resource representing a real disk.</li>
<li><strong>PVC</strong> = a Pod&rsquo;s request; gets bound to a matching PV.</li>
<li><strong>Access modes</strong>: RWO (one node), RWX (many &mdash; NFS / EFS / Azure Files), ROX (read-only many), RWOP (single Pod, K8s 1.27+).</li>
<li><strong>Reclaim policy</strong>: <code>Delete</code> (default for dynamic) destroys the disk on PVC delete; <code>Retain</code> keeps it for manual recovery &mdash; use for production data.</li>
<li><strong><code>volumeBindingMode: WaitForFirstConsumer</code></strong> &mdash; defers PV provisioning until a Pod is scheduled, so the disk is created in the same zone as the Pod.</li>
<li><strong><code>allowVolumeExpansion: true</code></strong> &mdash; let users grow PVCs (<code>kubectl edit pvc</code> + bigger storage value).</li>
</ul>
<p><strong>Variants for shared storage:</strong></p>
<ul>
<li><strong>EFS</strong> on EKS, <strong>Filestore</strong> on GKE, <strong>Azure Files</strong> on AKS &mdash; RWX without NFS-server ops.</li>
<li><strong>Longhorn</strong> / <strong>Rook-Ceph</strong> / <strong>OpenEBS</strong> &mdash; OSS distributed storage on-prem.</li>
</ul>
<p><strong>2026 advice:</strong> for databases, prefer <strong>managed services</strong> (RDS, Cloud SQL, Atlas) &mdash; you skip backup, snapshots, and cross-AZ replication operationally. PVs are right for caches, file uploads, ML datasets, and stateful workloads where managed isn&rsquo;t available.</p>'''

ANSWERS[32] = r'''<pre><code># Dockerfile &mdash; Go app, multi-stage, distroless final
# --- builder
FROM golang:1.23-alpine AS build
WORKDIR /src

# Cache modules independently of source
COPY go.mod go.sum ./
RUN go mod download

COPY . .
# Static binary, stripped, no CGO &mdash; portable across libc versions
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w -X main.version=$(git describe --tags --always 2&gt;/dev/null || echo dev)" \
    -trimpath -o /out/app ./cmd/server

# --- runtime: distroless static (~5 MB)
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/app /app
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/app"]
</code></pre>
<p><strong>Build &amp; run:</strong></p>
<pre><code>docker build -t myorg/api:1.0.0 .
docker images myorg/api          # ~10-20 MB total
docker run -p 8080:8080 myorg/api:1.0.0
</code></pre>
<p><strong>Why each line matters:</strong></p>
<ul>
<li><strong>Mod cache layer</strong> &mdash; <code>go mod download</code> before <code>COPY . .</code> means dependency layers are cached; rebuilds after pure code changes are seconds.</li>
<li><strong><code>CGO_ENABLED=0</code></strong> &mdash; produces a static binary; works in any base image, including distroless and <code>scratch</code>.</li>
<li><strong><code>-ldflags="-s -w"</code></strong> &mdash; strips debug info, halves binary size.</li>
<li><strong><code>-trimpath</code></strong> &mdash; reproducible builds; no host paths embedded.</li>
<li><strong>Version flag injection</strong> &mdash; <code>-X main.version=...</code> sets a build-time string variable, queried at runtime via <code>/version</code>.</li>
<li><strong>Distroless static</strong> &mdash; ~5 MB image, no shell, no package manager, non-root user; minimal CVE surface.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Even smaller</strong> &mdash; <code>FROM scratch</code> works for static Go binaries (no TLS root certs unless you copy them in: <code>COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/</code>).</li>
<li><strong>Cross-platform</strong> &mdash; with BuildKit:
<pre><code>FROM --platform=$BUILDPLATFORM golang:1.23-alpine AS build
ARG TARGETOS TARGETARCH
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/app .
</code></pre>
Then build with <code>docker buildx build --platform linux/amd64,linux/arm64 .</code></li>
<li><strong>Cache mount</strong> for module cache between builds:
<pre><code>RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    go build -o /out/app ./...
</code></pre>
</li>
<li><strong>Chainguard / Wolfi</strong> as final stage for compliance-friendly daily-rebuilt base images.</li>
</ul>
<p><strong>Performance:</strong> use <code>GOMAXPROCS</code> and <code>GOMEMLIMIT</code> env vars to make Go honour container CPU/memory limits (Go 1.19+ for memlimit). For massive projects, build with <code>-trimpath -buildvcs=false</code> in CI to keep builds reproducible.</p>'''

ANSWERS[33] = r'''<pre><code># .github/workflows/lint.yml
name: Lint &amp; Format
on: [push, pull_request]

permissions:
  contents: read
  pull-requests: write       # for inline annotations / reviewdog

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # JS/TS &mdash; ESLint + Prettier (or Biome)
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx eslint . --max-warnings 0
      - run: npx prettier --check .
      # alternative: one tool that does both
      # - run: npx @biomejs/biome ci .

      # Python &mdash; Ruff + mypy
      - uses: astral-sh/setup-uv@v5
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src

      # Shell scripts
      - uses: ludeeus/action-shellcheck@master

      # GitHub Actions YAML
      - uses: rhysd/actionlint@v1

      # Generic
      - uses: editorconfig-checker/action-editorconfig-checker@main
</code></pre>
<p><strong>Auto-fix instead of fail (push back to the PR):</strong></p>
<pre><code>jobs:
  fix:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    permissions: { contents: write, pull-requests: write }
    steps:
      - uses: actions/checkout@v4
        with: { ref: ${{ github.head_ref }} }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx eslint . --fix
      - run: npx prettier --write .
      - uses: stefanzweifel/git-auto-commit-action@v5
        with: { commit_message: 'style: lint auto-fix' }
</code></pre>
<p><strong>Tool pairings (the 2026 stack):</strong></p>
<table>
<tr><th>Language</th><th>Lint</th><th>Format</th><th>Type-check</th></tr>
<tr><td>JS / TS</td><td>ESLint or <strong>Biome</strong></td><td>Prettier or Biome</td><td>tsc / vue-tsc</td></tr>
<tr><td>Python</td><td><strong>Ruff</strong> (replaces flake8 + isort + pylint)</td><td>Ruff format (Black-compat)</td><td>mypy / <strong>pyright</strong> / ty</td></tr>
<tr><td>Go</td><td>golangci-lint</td><td>gofmt / gofumpt</td><td>built-in</td></tr>
<tr><td>Rust</td><td>clippy</td><td>rustfmt</td><td>built-in</td></tr>
<tr><td>Java</td><td>Checkstyle / SpotBugs</td><td>Spotless / google-java-format</td><td>javac</td></tr>
<tr><td>Shell</td><td>ShellCheck</td><td>shfmt</td><td>&mdash;</td></tr>
</table>
<p><strong>Required checks:</strong> in branch protection, mark the lint job <em>required</em> &mdash; PRs can&rsquo;t merge with style violations. <strong>pre-commit hooks</strong> (Husky / lint-staged for JS, pre-commit for Python) catch issues client-side so CI is the safety net, not the first line of defence.</p>
<p><strong>Performance:</strong> Ruff and Biome are typically 10&ndash;100&times; faster than the legacy tools they replace; CI lint stages drop from minutes to seconds. <strong>reviewdog</strong> turns linter output into inline PR review comments &mdash; far more useful than a red X.</p>'''

ANSWERS[34] = r'''<pre><code>#!/usr/bin/env bash
# setup-jenkins-agent.sh &mdash; provision a Jenkins agent (Docker-based)
set -euo pipefail

JENKINS_URL=${JENKINS_URL:-https://jenkins.acme.com}
AGENT_NAME=${AGENT_NAME:-docker-agent-1}
AGENT_SECRET=${AGENT_SECRET:?AGENT_SECRET env var is required (from Jenkins UI)}
WORK_DIR=${WORK_DIR:-/var/jenkins/agent}
LABELS=${LABELS:-linux docker}
EXECUTORS=${EXECUTORS:-2}

mkdir -p "$WORK_DIR"

# Use the official inbound-agent image; mounts Docker socket so the agent
# can build images on the host&rsquo;s Docker daemon.
docker rm -f "$AGENT_NAME" 2&gt;/dev/null || true
docker run -d --restart unless-stopped \
  --name "$AGENT_NAME" \
  -v "$WORK_DIR:/home/jenkins/agent" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e JENKINS_URL="$JENKINS_URL" \
  -e JENKINS_AGENT_NAME="$AGENT_NAME" \
  -e JENKINS_SECRET="$AGENT_SECRET" \
  -e JENKINS_AGENT_WORKDIR=/home/jenkins/agent \
  jenkins/inbound-agent:latest-jdk21

echo "Agent $AGENT_NAME started; check Jenkins UI &rarr; Manage Nodes."
</code></pre>
<p><strong>Step-by-step on the controller:</strong></p>
<ol>
<li><em>Manage Jenkins &rarr; Nodes &rarr; New Node</em>.</li>
<li>Type: <em>Permanent Agent</em>; name = <code>docker-agent-1</code>; remote root = <code>/home/jenkins/agent</code>; labels = <code>linux docker</code>; <em>Launch method</em> = <em>Launch agent by connecting it to the controller</em>.</li>
<li>Save &rarr; Jenkins shows the agent secret on the node page.</li>
<li>On the agent host, run the script with that secret.</li>
</ol>
<p><strong>Use it in a pipeline:</strong></p>
<pre><code>pipeline {
  agent { label 'docker' }
  stages {
    stage('Build') {
      steps { sh 'docker build -t myapp .' }
    }
  }
}
</code></pre>
<p><strong>Variants &amp; better options for 2026:</strong></p>
<ul>
<li><strong>Kubernetes Cloud (preferred)</strong> &mdash; install the Kubernetes plugin; agents are spawned as Pods <em>per build</em> and deleted afterwards. Zero idle cost, perfect isolation.</li>
<li><strong>EC2 Fleet plugin</strong> &mdash; auto-scale agents on EC2 spot instances based on queue length.</li>
<li><strong>Docker plugin</strong> on the controller &mdash; spawns one container per build automatically; no static agent host needed.</li>
<li><strong>SSH-based agents</strong> &mdash; controller SSHes into a known host and launches the agent; suitable for static specialised hardware (macOS for iOS, Windows for .NET).</li>
</ul>
<p><strong>Security caveats:</strong> mounting <code>/var/run/docker.sock</code> grants root-equivalent host access. For hardened setups, use <strong>Docker-in-Docker (DinD)</strong> sidecar, <strong>Buildkit rootless</strong>, or <strong>Kaniko</strong>. Run agents with the <em>Authorize Project</em> plugin so untrusted jobs can&rsquo;t escalate privileges.</p>
<p><strong>Performance:</strong> for bursty workloads, prefer K8s-spawned ephemeral agents over static fleets &mdash; you only pay when builds run, and starting a fresh Pod is cleaner than reusing a workspace. For monorepos, static agents with persistent caches can be faster than ephemeral ones.</p>'''

ANSWERS[35] = r'''<pre><code># daemonset-fluent-bit.yaml &mdash; one log forwarder per node
apiVersion: v1
kind: ConfigMap
metadata: { name: fluent-bit-config, namespace: logging }
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush 1
        Log_Level info
    [INPUT]
        Name tail
        Path /var/log/containers/*.log
        Parser cri
        Tag kube.*
        Refresh_Interval 5
    [FILTER]
        Name kubernetes
        Match kube.*
        Merge_Log On
        Keep_Log Off
    [OUTPUT]
        Name loki
        Match *
        Host loki.logging.svc
        Port 3100
        Labels job=fluent-bit
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
  labels: { app: fluent-bit }
spec:
  selector:
    matchLabels: { app: fluent-bit }
  updateStrategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 1 }
  template:
    metadata:
      labels: { app: fluent-bit }
    spec:
      serviceAccountName: fluent-bit
      priorityClassName: system-node-critical   # don&rsquo;t evict under pressure
      hostNetwork: false
      tolerations:
        - operator: Exists                       # run on all nodes including tainted
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:3.1
          resources:
            requests: { cpu: 50m, memory: 64Mi }
            limits:   { cpu: 200m, memory: 256Mi }
          volumeMounts:
            - { name: varlog, mountPath: /var/log, readOnly: true }
            - { name: containers, mountPath: /var/lib/docker/containers, readOnly: true }
            - { name: config, mountPath: /fluent-bit/etc, readOnly: true }
      volumes:
        - name: varlog
          hostPath: { path: /var/log }
        - name: containers
          hostPath: { path: /var/lib/docker/containers }
        - name: config
          configMap: { name: fluent-bit-config }
</code></pre>
<p><strong>RBAC the agent needs (read pods/namespaces for the kubernetes filter):</strong></p>
<pre><code>apiVersion: v1
kind: ServiceAccount
metadata: { name: fluent-bit, namespace: logging }
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata: { name: fluent-bit }
rules:
  - apiGroups: [""]
    resources: [namespaces, pods]
    verbs: [get, list, watch]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata: { name: fluent-bit }
subjects:
  - kind: ServiceAccount
    name: fluent-bit
    namespace: logging
roleRef:
  kind: ClusterRole
  name: fluent-bit
  apiGroup: rbac.authorization.k8s.io
</code></pre>
<p><strong>Apply &amp; verify:</strong></p>
<pre><code>kubectl apply -f daemonset-fluent-bit.yaml
kubectl get ds -n logging
kubectl logs -l app=fluent-bit -n logging
</code></pre>
<p><strong>Why a DaemonSet for log shipping:</strong></p>
<ul>
<li>Each node gets exactly one shipper &mdash; tails files on the node directly via <code>hostPath</code>; far more efficient than per-Pod sidecars.</li>
<li><strong>Kubernetes filter</strong> enriches logs with pod/namespace/labels metadata.</li>
<li><strong>Tolerations</strong> ensure shippers run on tainted control-plane nodes too.</li>
<li><strong><code>system-node-critical</code></strong> priority class keeps shippers running when nodes are under pressure.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Vector</strong> &mdash; faster, more flexible alternative to Fluent Bit; same DaemonSet shape.</li>
<li><strong>Loki / Grafana Cloud</strong> backend &mdash; cheap, label-based.</li>
<li><strong>Datadog Agent</strong>, <strong>New Relic Infra</strong>, <strong>Elastic Filebeat</strong> &mdash; managed observability stacks.</li>
<li><strong>OpenTelemetry Collector</strong> &mdash; unified logs + metrics + traces in one DaemonSet; the converging 2026 standard.</li>
</ul>
<p><strong>Performance:</strong> tune <code>Mem_Buf_Limit</code> in Fluent Bit to bound memory; use <code>refresh_interval</code> over file polling for high-churn nodes; ship to a regional aggregator (Vector / OTel Collector StatefulSet) before egress to reduce per-node CPU.</p>'''

ANSWERS[36] = r'''<pre><code># .github/workflows/netlify.yml
name: Deploy to Netlify
on:
  push: { branches: [main] }
  pull_request:                    # deploy previews for PRs

permissions:
  contents: read
  pull-requests: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test --if-present
      - run: npm run build         # outputs to ./dist (Vite) or ./build (CRA)

      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: ./dist
          production-branch: main
          production-deploy: ${{ github.ref == 'refs/heads/main' }}
          deploy-message: ${{ github.event.head_commit.message || 'Manual run' }}
          enable-pull-request-comment: true
          enable-commit-comment: true
          alias: deploy-preview-${{ github.event.number }}
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID:    ${{ secrets.NETLIFY_SITE_ID }}
        timeout-minutes: 5
</code></pre>
<p><strong>Setup &mdash; one-time:</strong></p>
<ol>
<li><em>Netlify &rarr; User settings &rarr; Applications &rarr; Personal access tokens</em> &rarr; create token &rarr; save as <code>NETLIFY_AUTH_TOKEN</code> in GitHub secrets.</li>
<li>Get the site ID: <em>Site settings &rarr; Site information &rarr; Site ID</em>; save as <code>NETLIFY_SITE_ID</code>.</li>
<li>Disable Netlify&rsquo;s native git auto-build (Site settings &rarr; Build &amp; deploy &rarr; Build settings &rarr; <em>Stop builds</em>) so GitHub Actions is the single source of truth.</li>
</ol>
<p><strong>What you get:</strong></p>
<ul>
<li><strong>Production deploys</strong> on push to <code>main</code>.</li>
<li><strong>Deploy Previews</strong> on PRs &mdash; each PR gets a unique URL like <code>deploy-preview-42--site.netlify.app</code>; the action posts the URL as a PR comment.</li>
<li><strong>Custom aliases</strong> for branch deploys.</li>
<li><strong>Atomic deploys</strong> &mdash; rolling back is one click in the Netlify UI.</li>
</ul>
<p><strong><code>netlify.toml</code> for build config (commit alongside source):</strong></p>
<pre><code>[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"      # SPA fallback
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "no-referrer-when-downgrade"
    Permissions-Policy = "geolocation=(), microphone=()"
</code></pre>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Direct Netlify CLI</strong> &mdash; <code>npx netlify deploy --prod --dir=dist --site=$NETLIFY_SITE_ID --auth=$NETLIFY_AUTH_TOKEN</code>; one less dependency.</li>
<li><strong>Functions / Edge Functions</strong> &mdash; ship serverless functions alongside; build them in the same workflow.</li>
<li><strong>Form handling, identity, A/B split</strong> &mdash; Netlify-managed, no extra infra.</li>
</ul>
<p><strong>2026 alternatives:</strong> <strong>Vercel</strong>, <strong>Cloudflare Pages</strong>, <strong>GitHub Pages</strong>, <strong>AWS Amplify</strong>, <strong>Fly.io</strong> &mdash; all offer similar DX with different trade-offs (Vercel for Next.js best-in-class, Cloudflare Pages for cheap edge, AWS for tight cloud integration).</p>
<p><strong>Performance:</strong> Netlify caches build outputs across runs &mdash; no extra config needed. For very large sites, use <code>incremental: true</code> to only rebuild changed pages.</p>'''

ANSWERS[37] = r'''<pre><code>// Jenkinsfile &mdash; Spring Boot &rarr; Cloud Run
pipeline {
  agent any
  options { timeout(time: 25, unit: 'MINUTES') }
  environment {
    GCP_PROJECT = 'acme-prod'
    GCP_REGION  = 'us-central1'
    SERVICE     = 'spring-api'
    REPO        = 'us-central1-docker.pkg.dev/acme-prod/api/spring-api'
    IMAGE       = "${REPO}:${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Build &amp; test (Maven)') {
      steps {
        sh 'mvn -B verify'
      }
      post { always { junit '**/target/surefire-reports/*.xml' } }
    }

    stage('Build &amp; push container') {
      steps {
        // Use Spring Boot&rsquo;s own buildpacks integration &mdash; no Dockerfile needed
        sh "mvn -B spring-boot:build-image -Dspring-boot.build-image.imageName=$IMAGE"
        withCredentials([file(credentialsId: 'gcp-deploy-sa', variable: 'GCP_KEY')]) {
          sh &apos;&apos;&apos;
            gcloud auth activate-service-account --key-file=$GCP_KEY
            gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
            docker push $IMAGE
          &apos;&apos;&apos;
        }
      }
    }

    stage('Deploy to Cloud Run') {
      when { branch 'main' }
      steps {
        withCredentials([file(credentialsId: 'gcp-deploy-sa', variable: 'GCP_KEY')]) {
          sh &apos;&apos;&apos;
            gcloud auth activate-service-account --key-file=$GCP_KEY
            gcloud run deploy $SERVICE \
              --image=$IMAGE \
              --region=$GCP_REGION \
              --project=$GCP_PROJECT \
              --platform=managed \
              --port=8080 \
              --memory=1Gi \
              --cpu=1 \
              --min-instances=1 \
              --max-instances=20 \
              --concurrency=80 \
              --service-account=spring-api@$GCP_PROJECT.iam.gserviceaccount.com \
              --set-env-vars="SPRING_PROFILES_ACTIVE=production" \
              --set-secrets="DATABASE_URL=db-url:latest" \
              --allow-unauthenticated
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { slackSend channel: '#deploys', message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} &rarr; ${env.SERVICE}" }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>One-time GCP setup:</strong></p>
<ol>
<li>Enable APIs: <code>gcloud services enable run.googleapis.com artifactregistry.googleapis.com</code>.</li>
<li>Create the Artifact Registry repo: <code>gcloud artifacts repositories create api --repository-format=docker --location=us-central1</code>.</li>
<li>Create a deploy service account with roles: <code>roles/run.admin</code>, <code>roles/iam.serviceAccountUser</code>, <code>roles/artifactregistry.writer</code>.</li>
<li>Download the SA key and store as Jenkins credential <code>gcp-deploy-sa</code>.</li>
</ol>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Workload Identity Federation (preferred over keys)</strong> &mdash; on GitHub Actions, use OIDC and skip stored creds entirely. On Jenkins, you&rsquo;re typically still on stored SA keys.</li>
<li><strong>Cloud Build</strong> as the build engine &mdash; Jenkins triggers Cloud Build, which builds + pushes + deploys; offloads CI compute.</li>
<li><strong>Cloud Run Jobs</strong> &mdash; for batch tasks (migrations, ETL); same image, different deploy target.</li>
<li><strong>Multi-region</strong> &mdash; deploy to several regions and front with Cloud Load Balancer + traffic split.</li>
</ul>
<p><strong>Performance:</strong> set <code>--min-instances=1</code> for sub-second responses (no cold starts); tune <code>--concurrency</code> based on per-request memory; use <strong>second-generation Cloud Run</strong> execution environment for better startup + filesystem perf.</p>'''

ANSWERS[38] = r'''<pre><code># networkpolicy.yaml &mdash; default-deny + explicit allow rules
---
# 1) Default-deny ALL ingress + egress in the namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: prod
spec:
  podSelector: {}            # all pods
  policyTypes: [Ingress, Egress]

---
# 2) Allow ingress to the API only from the front-end namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-from-frontend
  namespace: prod
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { name: frontend } }
        - podSelector: { matchLabels: { app: web } }
      ports:
        - { protocol: TCP, port: 3000 }

---
# 3) API can reach DB and external HTTPS only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-egress
  namespace: prod
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Egress]
  egress:
    # to MongoDB
    - to:
        - namespaceSelector: { matchLabels: { name: db } }
          podSelector: { matchLabels: { app: mongo } }
      ports: [ { protocol: TCP, port: 27017 } ]
    # DNS
    - to:
        - namespaceSelector: { matchLabels: { name: kube-system } }
          podSelector: { matchLabels: { k8s-app: kube-dns } }
      ports: [ { protocol: UDP, port: 53 }, { protocol: TCP, port: 53 } ]
    # outbound HTTPS (e.g. third-party APIs)
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except: [10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16]
      ports: [ { protocol: TCP, port: 443 } ]
</code></pre>
<p><strong>Apply &amp; verify:</strong></p>
<pre><code>kubectl apply -f networkpolicy.yaml
kubectl get netpol -n prod
kubectl describe netpol default-deny -n prod

# Test connectivity from a debug Pod
kubectl run debug --image=curlimages/curl -n prod --rm -it -- \
  curl -v http://api.prod.svc.cluster.local:3000/health
</code></pre>
<p><strong>Mental model:</strong></p>
<ul>
<li><strong>Whitelist model</strong> &mdash; once a NetworkPolicy selects a Pod, only explicitly-allowed traffic flows; default is deny.</li>
<li><strong>Pod-level firewall</strong> &mdash; rules apply to Pods matched by <code>podSelector</code>, not Services.</li>
<li><strong>Namespace + Pod selector union</strong> &mdash; as written above, the policy admits traffic from Pods in the <code>frontend</code> namespace AND with label <code>app: web</code>.</li>
<li><strong>DNS is required egress</strong> &mdash; without an egress allow for kube-dns, your Pods can&rsquo;t resolve names &mdash; classic gotcha.</li>
</ul>
<p><strong>Important:</strong> NetworkPolicy is a <em>spec</em>; it requires a <strong>CNI plugin</strong> that enforces it. Calico, Cilium, Antrea all do. <strong>Flannel</strong> alone doesn&rsquo;t. Verify with <code>kubectl get pods -n kube-system</code>.</p>
<p><strong>2026 advances &mdash; Cilium / eBPF:</strong></p>
<ul>
<li><strong>CiliumNetworkPolicy</strong> adds L7 rules: &ldquo;allow only <code>GET /api/v1/*</code>&rdquo;.</li>
<li><strong>Cluster Mesh</strong> &mdash; cross-cluster identity-based policies.</li>
<li><strong>Hubble</strong> &mdash; visualise flows in real time; identify what&rsquo;s being denied.</li>
<li><strong>Service Mesh</strong> (Istio, Linkerd) layers mTLS + L7 authz on top.</li>
</ul>
<p><strong>Performance:</strong> rule evaluation happens in-kernel (iptables / eBPF) &mdash; effectively free at runtime. Start with default-deny per namespace, add minimum allow rules; keep policies close to workloads (one per app, not one giant policy).</p>'''

ANSWERS[39] = r'''<pre><code># docker-compose.yml &mdash; local Jenkins + DinD agent + reverse proxy
name: jenkins-local

services:
  jenkins:
    image: jenkins/jenkins:lts-jdk21
    user: "1000:1000"
    ports:
      - "8080:8080"
      - "50000:50000"
    environment:
      JAVA_OPTS: -Djenkins.install.runSetupWizard=false
      JENKINS_OPTS: --argumentsRealm.passwd.admin=admin --argumentsRealm.roles.admin=admin
      DOCKER_HOST: tcp://docker:2376
      DOCKER_CERT_PATH: /certs/client
      DOCKER_TLS_VERIFY: "1"
    volumes:
      - jenkins-home:/var/jenkins_home
      - jenkins-docker-certs:/certs/client:ro
    depends_on: [docker]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/login"]
      interval: 10s
      retries: 12

  # Docker-in-Docker sidecar &mdash; secure alternative to mounting host socket
  docker:
    image: docker:25-dind
    privileged: true
    environment:
      DOCKER_TLS_CERTDIR: /certs
    volumes:
      - jenkins-docker-certs:/certs/client
      - jenkins-docker-data:/var/lib/docker
    command: ["--storage-driver=overlay2"]

  # Optional: nginx with TLS for browser access at https://jenkins.local
  nginx:
    image: nginx:alpine
    depends_on: [jenkins]
    ports: ["443:443", "80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./certs:/etc/nginx/certs:ro

volumes:
  jenkins-home: {}
  jenkins-docker-certs: {}
  jenkins-docker-data: {}
</code></pre>
<p><strong>Companion <code>nginx.conf</code> (optional TLS termination):</strong></p>
<pre><code>server {
  listen 443 ssl;
  server_name jenkins.local;
  ssl_certificate     /etc/nginx/certs/jenkins.crt;
  ssl_certificate_key /etc/nginx/certs/jenkins.key;
  client_max_body_size 100M;
  location / {
    proxy_pass http://jenkins:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
</code></pre>
<p><strong>Run &amp; first-time login:</strong></p>
<pre><code>docker compose up -d
docker compose logs -f jenkins | grep -A 3 'initialAdminPassword'
# or:
docker exec jenkins-local-jenkins-1 cat /var/jenkins_home/secrets/initialAdminPassword

# Open http://localhost:8080 (or https://jenkins.local with /etc/hosts entry)
</code></pre>
<p><strong>Why this shape:</strong></p>
<ul>
<li><strong>DinD sidecar</strong> &mdash; Jenkins talks to a dedicated Docker daemon over TLS; far safer than mounting the host&rsquo;s <code>/var/run/docker.sock</code>.</li>
<li><strong>Persistent volumes</strong> &mdash; <code>jenkins-home</code> survives <code>compose down</code>; only <code>down -v</code> wipes everything.</li>
<li><strong>Health check</strong> &mdash; lets Compose / orchestrators wait for readiness instead of <code>sleep</code>.</li>
<li><strong>Skip setup wizard</strong> &mdash; combine with JCasC for fully reproducible config.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Add JCasC</strong> &mdash; mount <code>casc.yaml</code> with admin user, plugins, security; restore from scratch in seconds.</li>
<li><strong>Helm chart on Kind / k3d</strong> &mdash; for local dev that mirrors prod K8s setup.</li>
<li><strong>Use Jenkins LTS</strong>, not <code>latest</code> &mdash; LTS is patched without breaking changes.</li>
</ul>
<p><strong>2026 alternative:</strong> for CI experiments, <strong>act</strong> runs GitHub Actions workflows locally in containers &mdash; often a faster feedback loop than spinning up Jenkins. <strong>Tekton</strong> on Kind is the cloud-native equivalent if you&rsquo;re evaluating beyond Jenkins.</p>'''

ANSWERS[40] = r'''<pre><code>#!/usr/bin/env bash
# install-k8s-kubeadm.sh &mdash; bootstrap a basic K8s cluster on Ubuntu 24.04
set -euxo pipefail

K8S_VERSION=${K8S_VERSION:-1.30}
POD_CIDR=${POD_CIDR:-10.244.0.0/16}

# 1) Disable swap (required by kubelet)
swapoff -a
sed -i '/ swap / s/^/#/' /etc/fstab

# 2) Kernel modules + sysctl
cat &lt;&lt;EOF | tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
modprobe overlay
modprobe br_netfilter

cat &lt;&lt;EOF | tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sysctl --system

# 3) Install containerd (the recommended CRI)
apt-get update
apt-get install -y containerd
mkdir -p /etc/containerd
containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
systemctl restart containerd

# 4) Install kubeadm, kubelet, kubectl
apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v$K8S_VERSION/deb/Release.key | \
  gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v$K8S_VERSION/deb/ /" | \
  tee /etc/apt/sources.list.d/kubernetes.list
apt-get update
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

# 5) On the CONTROL PLANE node only:
if [[ "${ROLE:-}" == "control-plane" ]]; then
  kubeadm init --pod-network-cidr=$POD_CIDR --upload-certs

  mkdir -p $HOME/.kube
  cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  chown $(id -u):$(id -g) $HOME/.kube/config

  # Install a CNI &mdash; Cilium recommended for 2026
  cilium install --version 1.16.0

  # Print join command for workers
  kubeadm token create --print-join-command &gt; /tmp/join-cmd.sh
  echo "Run this on each worker node:"
  cat /tmp/join-cmd.sh
fi

# 6) On WORKERS: paste the join command (sudo kubeadm join ...)
</code></pre>
<p><strong>Cluster verification:</strong></p>
<pre><code>kubectl get nodes -o wide
kubectl get pods -A
kubectl wait --for=condition=Ready node --all --timeout=5m
</code></pre>
<p><strong>What kubeadm does:</strong></p>
<ul>
<li>Installs control-plane components (apiserver, controller-manager, scheduler, etcd) as static Pods on the control-plane node.</li>
<li>Generates TLS certs for the API server and inter-component mTLS.</li>
<li>Configures kubelet to register with the control plane.</li>
<li>Provides a join token for workers.</li>
</ul>
<p><strong>Critical: kubeadm gives you the cluster but not the network.</strong> You must install a <strong>CNI plugin</strong> before Pods can communicate:</p>
<ul>
<li><strong>Cilium</strong> &mdash; eBPF-based, fastest, with built-in NetworkPolicy + L7 + service mesh capabilities; recommended for 2026.</li>
<li><strong>Calico</strong> &mdash; mature, BGP-routed, strong NetworkPolicy.</li>
<li><strong>Flannel</strong> &mdash; simplest; no NetworkPolicy.</li>
</ul>
<p><strong>2026 reality check:</strong></p>
<ul>
<li>For new on-prem clusters, prefer <strong>kubeadm + Cluster API + Crossplane</strong> for declarative cluster lifecycle, or <strong>k3s</strong> / <strong>RKE2</strong> for simpler single-binary clusters.</li>
<li>For cloud, use <strong>EKS / GKE / AKS</strong>; the operational burden of self-managed K8s rarely pays off below a 100-node fleet.</li>
<li><strong>Kind</strong> / <strong>k3d</strong> for laptop dev; <strong>Talos Linux</strong> for hardened immutable clusters; <strong>OpenShift</strong> for enterprise platform-as-a-service.</li>
</ul>
<p><strong>Don&rsquo;t forget:</strong> upgrade plan, etcd backups (<code>etcdctl snapshot save</code>), monitoring stack, and a CNI choice <em>before</em> putting workloads on it.</p>'''

ANSWERS[41] = r'''<pre><code># .github/workflows/vue-deploy.yml
name: Build &amp; Deploy Vue.js
on:
  push: { branches: [main] }
  pull_request:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: vue-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run test:unit
      - run: npm run build
        env:
          VITE_API_URL: ${{ vars.API_URL }}
          VITE_SENTRY_DSN: ${{ secrets.SENTRY_DSN }}
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
</code></pre>
<p><strong>Vite config note for project Pages</strong> &mdash; in <code>vite.config.js</code> set <code>base: '/repo-name/'</code> when deploying to <code>username.github.io/repo-name</code>; otherwise asset paths break.</p>
<p><strong>Deploy to a different host (S3 + CloudFront):</strong></p>
<pre><code>- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123:role/gh-deploy
    aws-region: us-east-1
- run: aws s3 sync dist/ s3://my-vue-bucket --delete
- run: aws cloudfront create-invalidation --distribution-id $CF_ID --paths "/*"
</code></pre>
<p><strong>Deploy to Vercel / Netlify / Cloudflare Pages:</strong> they auto-detect Vue/Vite; commonly you skip GitHub Actions entirely and use their native git integration. The action stays useful for tests + build artefacts though.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Nuxt</strong> &mdash; same workflow shape; <code>npm run build</code> +<code>npm run generate</code> for static, or use <code>nuxi build</code> for SSR + Node hosting.</li>
<li><strong>SSR</strong> &mdash; deploy <code>node .output/server</code> to Cloud Run / App Runner / Render; set up health checks.</li>
<li><strong>Component library</strong> &mdash; build to <code>dist/</code> and <code>npm publish</code> on release tag.</li>
</ul>
<p><strong>Performance:</strong> caching <code>node_modules</code> via <code>cache: npm</code> in <code>setup-node</code> typically halves install time. <code>concurrency.cancel-in-progress</code> kills outdated runs on rapid pushes. For large monorepos, gate jobs by <code>paths: [apps/web/**, packages/ui/**]</code>.</p>'''

ANSWERS[42] = r'''<pre><code>// Jenkinsfile &mdash; PHP app to Azure Web App
pipeline {
  agent any
  options { timeout(time: 25, unit: 'MINUTES') }
  environment {
    AZURE_APP = 'acme-php-api'
    AZURE_RG  = 'prod-rg'
    PHP_VER   = '8.3'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Install &amp; test') {
      steps {
        sh &apos;&apos;&apos;
          composer install --no-dev --prefer-dist --no-interaction --optimize-autoloader
          composer dump-autoload --classmap-authoritative --no-dev
          vendor/bin/phpunit --testdox || true   # tests against dev deps; use a separate stage if desired
        &apos;&apos;&apos;
      }
    }

    stage('Static analysis') {
      steps {
        sh &apos;&apos;&apos;
          vendor/bin/phpstan analyse --level=8 src
          vendor/bin/php-cs-fixer fix --dry-run --diff
        &apos;&apos;&apos;
      }
    }

    stage('Package') {
      steps {
        sh &apos;&apos;&apos;
          rm -f app.zip
          zip -qr app.zip . \
            -x '.git/*' '.github/*' 'tests/*' '*.md' '.env*'
        &apos;&apos;&apos;
        archiveArtifacts 'app.zip'
      }
    }

    stage('Deploy to Azure Web App') {
      when { branch 'main' }
      steps {
        withCredentials([azureServicePrincipal('azure-sp')]) {
          sh &apos;&apos;&apos;
            az login --service-principal \
              -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET \
              --tenant $AZURE_TENANT_ID
            az webapp deploy \
              --resource-group $AZURE_RG \
              --name $AZURE_APP \
              --src-path app.zip --type zip
            az webapp config appsettings set \
              --resource-group $AZURE_RG --name $AZURE_APP \
              --settings APP_ENV=production \
                         APP_DEBUG=false \
                         WEBSITE_RUN_FROM_PACKAGE=1
            az webapp restart -g $AZURE_RG -n $AZURE_APP
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { slackSend channel: '#deploys', message: "✅ ${env.JOB_NAME}" }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>One-time Azure setup:</strong></p>
<ol>
<li>Create the Web App with the PHP runtime: <code>az webapp create -g prod-rg -p plan -n acme-php-api --runtime "PHP|8.3"</code>.</li>
<li>Create a Service Principal: <code>az ad sp create-for-rbac --name jenkins-deploy --role contributor --scopes /subscriptions/SUBID/resourceGroups/prod-rg</code>.</li>
<li>Install the Jenkins <strong>Azure Credentials</strong> plugin and add the SP as <code>azure-sp</code>.</li>
</ol>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Containerised</strong> &mdash; build a PHP-FPM + nginx image, push to ACR, configure the Web App to pull it. Better for non-standard PHP extensions.</li>
<li><strong>Azure Container Apps / AKS</strong> &mdash; for richer scaling and Kubernetes-native ops.</li>
<li><strong>Laravel/Symfony specific</strong> &mdash; add stages for <code>php artisan migrate --force</code>, <code>php artisan config:cache</code>, <code>php artisan route:cache</code>, <code>php artisan view:cache</code>; ensure <code>storage/</code> is writable on the App Service plan.</li>
<li><strong>Deployment slots</strong> &mdash; deploy to <em>staging</em>, smoke-test, then <code>az webapp deployment slot swap</code> for zero-downtime cutover.</li>
</ul>
<p><strong>Performance:</strong> <strong><code>WEBSITES_ENABLE_APP_SERVICE_STORAGE=false</code></strong> + <code>WEBSITE_RUN_FROM_PACKAGE=1</code> serves files directly from the deployed zip &mdash; faster cold starts, immutable deployments. Enable OPcache via app settings (<code>PHP_OPCACHE_ENABLE=1</code>) for production-grade PHP performance.</p>'''

ANSWERS[43] = r'''<pre><code># crd.yaml &mdash; define a custom resource type
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backups.platform.acme.com
spec:
  group: platform.acme.com
  scope: Namespaced
  names:
    plural: backups
    singular: backup
    kind: Backup
    shortNames: [bk]
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          required: [spec]
          properties:
            spec:
              type: object
              required: [source, schedule]
              properties:
                source:
                  type: string
                  description: PVC name to back up
                schedule:
                  type: string
                  pattern: '^(@(annually|yearly|monthly|weekly|daily|hourly)|((\*|[0-9]+)( |\/[0-9]+)?){5})$'
                retentionDays:
                  type: integer
                  minimum: 1
                  maximum: 365
                  default: 14
                destination:
                  type: object
                  properties:
                    type: { type: string, enum: [s3, gcs, azure-blob] }
                    bucket: { type: string }
            status:
              type: object
              properties:
                lastBackupTime: { type: string, format: date-time }
                phase: { type: string, enum: [Pending, Running, Succeeded, Failed] }
                message: { type: string }
      subresources:
        status: {}
      additionalPrinterColumns:
        - name: Schedule
          jsonPath: .spec.schedule
          type: string
        - name: Source
          jsonPath: .spec.source
          type: string
        - name: Phase
          jsonPath: .status.phase
          type: string
        - name: Age
          jsonPath: .metadata.creationTimestamp
          type: date
</code></pre>
<p><strong>Use it (after applying the CRD):</strong></p>
<pre><code>apiVersion: platform.acme.com/v1
kind: Backup
metadata: { name: db-nightly, namespace: prod }
spec:
  source: postgres-data
  schedule: '0 2 * * *'
  retentionDays: 30
  destination: { type: s3, bucket: acme-backups }
</code></pre>
<pre><code>kubectl apply -f crd.yaml
kubectl get crd backups.platform.acme.com
kubectl apply -f backup-instance.yaml
kubectl get backup -n prod                # uses additionalPrinterColumns
kubectl get bk -n prod                    # shortName works too
</code></pre>
<p><strong>What you just got:</strong></p>
<ul>
<li>A new resource type the API server now understands &mdash; appears in <code>kubectl api-resources</code>.</li>
<li><strong>OpenAPI schema validation</strong> &mdash; bad manifests are rejected at apply time (<code>schedule</code> regex enforced; <code>retentionDays</code> bounded).</li>
<li><strong><code>status</code> subresource</strong> &mdash; controllers update <code>.status</code> independently of <code>.spec</code>; <code>kubectl edit</code> users only touch <code>.spec</code>.</li>
<li><strong>Custom columns</strong> in <code>kubectl get</code> output.</li>
</ul>
<p><strong>This is half of the Operator pattern.</strong> A CRD <em>defines</em> the type; an <strong>Operator</strong> (controller) <em>watches</em> CRs and reconciles real state to match. Build operators with:</p>
<ul>
<li><strong>kubebuilder</strong> / <strong>Operator SDK</strong> &mdash; Go scaffolding; the standard.</li>
<li><strong>KOPF</strong> &mdash; Python operators; great for ops teams.</li>
<li><strong>Metacontroller</strong> &mdash; declarative composition for simple cases.</li>
<li><strong>Crossplane</strong> &mdash; CRDs + composition for cloud resources (the &ldquo;K8s API for everything&rdquo;).</li>
</ul>
<p><strong>Performance / ops:</strong> set <code>preserveUnknownFields: false</code> (default in v1) so unknown fields error early. Use <code>conversion</code> + multiple <code>versions</code> for backwards-compatible schema migrations. Bump the version (<code>v1beta1 &rarr; v1</code>) when making breaking changes.</p>'''

ANSWERS[44] = r'''<pre><code># Dockerfile &mdash; React app served via nginx (multi-stage)
# --- builder
FROM node:20-alpine AS build
WORKDIR /app

# Cache deps
COPY package*.json ./
RUN npm ci

# Build
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build      # outputs to ./dist (Vite) or ./build (CRA)

# --- runtime: tiny nginx
FROM nginx:1.27-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Run as non-root (nginx-unprivileged would be even better)
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /var/run \
 &amp;&amp; sed -i 's/listen *80;/listen 8080;/' /etc/nginx/conf.d/default.conf
USER nginx
EXPOSE 8080

# Container-friendly health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -q --spider http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
</code></pre>
<p><strong>Companion <code>nginx.conf</code> with SPA-friendly routing + caching:</strong></p>
<pre><code>server {
    listen       80;
    server_name  _;
    root         /usr/share/nginx/html;
    index        index.html;

    # SPA fallback &mdash; route all unmatched paths to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Long-cache content-hashed assets
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff2?|ico)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Don&rsquo;t cache index.html itself
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
}
</code></pre>
<p><strong>Build &amp; run:</strong></p>
<pre><code>docker build --build-arg VITE_API_URL=https://api.acme.com -t acme/web:1.0.0 .
docker run -p 8080:8080 acme/web:1.0.0
</code></pre>
<p><strong>Why this shape:</strong></p>
<ul>
<li><strong>Two stages</strong> &mdash; Node toolchain in the builder; only the static bundle + nginx in the runtime image (~25 MB).</li>
<li><strong><code>npm ci</code></strong> &mdash; deterministic from <code>package-lock.json</code>; faster than <code>npm install</code>.</li>
<li><strong>Build args for env</strong> &mdash; Vite/CRA bake <code>VITE_*</code>/<code>REACT_APP_*</code> into the bundle at build time, not runtime.</li>
<li><strong>SPA fallback</strong> &mdash; the React Router needs all non-asset paths routed to <code>index.html</code>.</li>
<li><strong>Long-cache hashed assets, never cache <code>index.html</code></strong> &mdash; standard SPA caching contract.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Distroless / static-only host</strong> &mdash; <strong>Caddy</strong> auto-handles HTTPS + try-files, often simpler than nginx; or use <strong>BusyBox httpd</strong> for absolute minimal.</li>
<li><strong>SSR</strong> (Next.js / Remix) &mdash; final stage is <code>FROM node:20-alpine</code> running <code>node server.js</code>; not nginx.</li>
<li><strong>Runtime env injection</strong> &mdash; for env vars after build, replace placeholders via <code>envsubst</code> in the entrypoint, or read from a <code>/config.js</code> served by nginx.</li>
</ul>
<p><strong>Performance:</strong> <code>.dockerignore</code> with <code>node_modules .git build dist coverage</code> dramatically cuts context size. For multi-platform builds, use Buildx + GHA cache. Static sites are usually better hosted on <strong>Vercel / Netlify / CloudFront / Pages</strong> than from a self-managed container &mdash; better edge caching, free TLS, no infra.</p>'''

ANSWERS[45] = r'''<pre><code># .github/workflows/e2e-selenium.yml
name: Selenium E2E
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chrome, firefox]

    services:
      selenium:
        image: selenium/standalone-${{ matrix.browser }}:latest
        ports: ["4444:4444"]
        options: --shm-size=2g

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build

      - name: Start app
        run: |
          npm start &amp; echo $! &gt; app.pid
          for i in {1..30}; do curl -fsS http://localhost:3000 &amp;&amp; break; sleep 2; done

      - name: Wait for Selenium
        run: |
          for i in {1..30}; do
            curl -fsS http://localhost:4444/status | grep '"ready":true' &amp;&amp; break
            sleep 2
          done

      - name: Run E2E tests
        run: npm run test:e2e
        env:
          SELENIUM_URL: http://localhost:4444/wd/hub
          BROWSER: ${{ matrix.browser }}
          BASE_URL: http://localhost:3000

      - name: Upload screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with: { name: screenshots-${{ matrix.browser }}, path: screenshots/ }

      - name: Upload videos
        if: always()
        uses: actions/upload-artifact@v4
        with: { name: videos-${{ matrix.browser }}, path: videos/ }

      - name: Stop app
        if: always()
        run: kill $(cat app.pid) || true
</code></pre>
<p><strong>Sample test (<code>tests/e2e/login.test.js</code>):</strong></p>
<pre><code>const { Builder, By, until } = require('selenium-webdriver');

describe('Login flow', () =&gt; {
  let driver;
  beforeAll(async () =&gt; {
    driver = await new Builder()
      .forBrowser(process.env.BROWSER || 'chrome')
      .usingServer(process.env.SELENIUM_URL)
      .build();
  });
  afterAll(() =&gt; driver.quit());

  test('user can log in', async () =&gt; {
    await driver.get(process.env.BASE_URL + '/login');
    await driver.findElement(By.name('email')).sendKeys('user@acme.com');
    await driver.findElement(By.name('password')).sendKeys('Secret123!');
    await driver.findElement(By.css('button[type="submit"]')).click();
    await driver.wait(until.urlContains('/dashboard'), 10000);
  });
});
</code></pre>
<p><strong>Patterns that matter:</strong></p>
<ul>
<li><strong>Selenium service container</strong> &mdash; one per matrix browser; runner reaches it on <code>localhost:4444</code> via <code>--network host</code>-style implicit binding.</li>
<li><strong><code>--shm-size=2g</code></strong> &mdash; Chrome crashes with default <code>/dev/shm</code>; this is the canonical fix.</li>
<li><strong>App boot wait</strong> &mdash; poll <code>/</code> until ready; eliminates &ldquo;app not up&rdquo; flakes.</li>
<li><strong>Failure artifacts</strong> &mdash; screenshots + videos on failure are gold for debugging flaky tests.</li>
</ul>
<p><strong>2026 alternatives (often better than raw Selenium):</strong></p>
<ul>
<li><strong>Playwright</strong> &mdash; faster, built-in waiting, multi-browser, screenshots/videos/traces by default. The default for new projects.</li>
<li><strong>Cypress</strong> &mdash; same-process; great DX; trade-off is single-tab, JS-only test code.</li>
<li><strong>WebdriverIO</strong> &mdash; modern wrapper around Selenium with sync-style API.</li>
<li><strong>BrowserStack / Sauce Labs / LambdaTest</strong> &mdash; managed grid; matrix on real iOS / Safari / IE if you must.</li>
</ul>
<p><strong>Performance:</strong> shard tests across runners (<code>matrix: { shard: [1,2,3,4] }</code> + <code>--shard=$SHARD/4</code>); use <strong>headless</strong> mode for speed; tag tests <code>@smoke</code> and run only those on PRs, full suite on nightly.</p>'''

ANSWERS[46] = r'''<pre><code>#!/usr/bin/env bash
# backup-docker-volumes.sh &mdash; safely back up named Docker volumes to S3
set -euo pipefail

BACKUP_DIR=${BACKUP_DIR:-/tmp/docker-backups}
S3_BUCKET=${S3_BUCKET:-acme-docker-backups}
RETAIN_DAYS=${RETAIN_DAYS:-30}
DATE=$(date +%F-%H%M)

mkdir -p "$BACKUP_DIR"

# Discover named volumes (skip anonymous ones)
VOLUMES=$(docker volume ls --format '{{.Name}}' | grep -v '^[a-f0-9]\{64\}$')

if [[ -z "$VOLUMES" ]]; then
  echo "No named volumes to back up."
  exit 0
fi

for VOL in $VOLUMES; do
  ARCHIVE="$BACKUP_DIR/${VOL}-${DATE}.tar.gz"
  echo "==&gt; Backing up volume: $VOL"

  # Pause writers if you can &mdash; for stateful DBs use a proper logical backup instead
  CONTAINERS=$(docker ps --filter "volume=$VOL" --format '{{.Names}}')
  for C in $CONTAINERS; do docker pause "$C" || true; done

  # Tar the volume by mounting it into a throwaway alpine
  docker run --rm \
    -v "$VOL:/volume:ro" \
    -v "$BACKUP_DIR:/backup" \
    alpine:3 \
    tar czf "/backup/$(basename "$ARCHIVE")" -C /volume .

  for C in $CONTAINERS; do docker unpause "$C" || true; done

  # Off-site copy
  if command -v aws &gt;/dev/null; then
    aws s3 cp "$ARCHIVE" "s3://$S3_BUCKET/$(date +%Y/%m/%d)/$(basename "$ARCHIVE")"
  fi
done

# Local retention
find "$BACKUP_DIR" -name '*.tar.gz' -mtime +"$RETAIN_DAYS" -delete
echo "Backup complete: $BACKUP_DIR"
</code></pre>
<p><strong>Restore one volume:</strong></p>
<pre><code>VOL=postgres-data
ARCHIVE=/tmp/docker-backups/postgres-data-2026-05-01-0200.tar.gz

docker volume create "$VOL"
docker run --rm \
  -v "$VOL:/volume" \
  -v "$(dirname "$ARCHIVE"):/backup" \
  alpine:3 \
  sh -c "cd /volume &amp;&amp; tar xzf /backup/$(basename "$ARCHIVE")"
</code></pre>
<p><strong>Schedule via cron / systemd timer:</strong></p>
<pre><code># /etc/cron.d/docker-volume-backup
0 2 * * * root /usr/local/bin/backup-docker-volumes.sh &gt;&gt; /var/log/dvb.log 2&gt;&amp;1
</code></pre>
<p><strong>Why these patterns:</strong></p>
<ul>
<li><strong>Read-only mount</strong> (<code>:ro</code>) &mdash; safety; tar can&rsquo;t accidentally write back.</li>
<li><strong>Pause writers</strong> &mdash; gives a consistent snapshot for filesystem-based backups. <em>For databases, prefer logical dumps</em> (<code>pg_dumpall</code>, <code>mongodump</code>, <code>mysqldump</code>) over raw volume tar &mdash; volume backups can produce a torn / inconsistent state if the engine isn&rsquo;t flushed.</li>
<li><strong>Throwaway alpine</strong> &mdash; no need to install tar on the host; no dependency on the volume&rsquo;s consumer image.</li>
<li><strong>S3 with date-partitioned prefix</strong> &mdash; lifecycle rules can transition old objects to Glacier.</li>
<li><strong>Local retention</strong> &mdash; recent ones close, older ones offsite only.</li>
</ul>
<p><strong>Better options for production:</strong></p>
<ul>
<li><strong>Logical DB dumps</strong> always preferred for databases: <code>docker exec postgres pg_dumpall -U postgres | gzip &gt; pg.sql.gz</code>.</li>
<li><strong>Restic</strong> / <strong>BorgBackup</strong> &mdash; deduplicating, encrypted, incremental backups; far better than full tar gzips for daily runs.</li>
<li><strong>Docker volume drivers</strong> &mdash; some (Portworx, REX-Ray) have built-in snapshot APIs.</li>
<li><strong>Migrate to K8s + Velero</strong> &mdash; volume snapshots + backup of K8s manifests in one tool.</li>
<li><strong>Use managed services</strong> &mdash; RDS / Atlas / Cloud SQL handle PITR automatically.</li>
</ul>
<p><strong>Test restores quarterly.</strong> An untested backup is a guess. Encrypt archives at rest (S3 SSE-KMS) since they may contain credentials.</p>'''

ANSWERS[47] = r'''<pre><code># pdb.yaml &mdash; protect availability during voluntary disruptions
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api
  namespace: prod
spec:
  selector:
    matchLabels: { app: api }
  # EITHER minAvailable OR maxUnavailable, not both
  minAvailable: 2          # always keep at least 2 Pods running
  # maxUnavailable: 1     # alternative: at most 1 Pod down at any moment
  unhealthyPodEvictionPolicy: AlwaysAllow   # K8s 1.27+; allow evicting CrashLoopBackOff pods
---
# Example: percentage-based for autoscaled deployments
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: web, namespace: prod }
spec:
  selector: { matchLabels: { app: web } }
  maxUnavailable: 25%      # tolerate 25% disruption (rounded down)
</code></pre>
<p><strong>Apply &amp; observe:</strong></p>
<pre><code>kubectl apply -f pdb.yaml
kubectl get pdb -n prod
kubectl describe pdb api -n prod

# What happens during a node drain:
kubectl drain node-3 --ignore-daemonsets --delete-emptydir-data
# &rarr; the API server respects the PDB and won&rsquo;t evict if it would breach minAvailable
</code></pre>
<p><strong>What a PDB does (and doesn&rsquo;t):</strong></p>
<ul>
<li><strong>Protects against <em>voluntary</em> disruptions</strong> &mdash; <code>kubectl drain</code>, cluster autoscaler scale-down, node upgrades, evictions by the API. The control plane consults PDBs before evicting Pods.</li>
<li><strong>Does NOT protect against involuntary disruptions</strong> &mdash; node hardware failure, kernel panics, power loss, network partitions. For those, run multiple replicas across zones with anti-affinity.</li>
<li><strong>Does NOT block the kubelet</strong> &mdash; if a node dies, its Pods die regardless of PDB.</li>
<li><strong>Does NOT prevent rolling updates</strong> &mdash; those are governed by the Deployment&rsquo;s <code>maxUnavailable</code>.</li>
</ul>
<p><strong>Common pairings:</strong></p>
<pre><code># Deployment topology spread for true HA
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  replicas: 6
  template:
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: api } }
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector: { matchLabels: { app: api } }
                topologyKey: kubernetes.io/hostname
</code></pre>
<p><strong>Sizing the PDB:</strong></p>
<table>
<tr><th>Replicas</th><th>Recommended PDB</th></tr>
<tr><td>1</td><td>None &mdash; PDB blocks all drains; instead, accept downtime or scale up</td></tr>
<tr><td>2</td><td><code>maxUnavailable: 1</code> (one can drain at a time)</td></tr>
<tr><td>3+</td><td><code>minAvailable: N-1</code> or <code>maxUnavailable: 25%</code></td></tr>
<tr><td>HPA-scaled</td><td>Percentage form so it adapts</td></tr>
</table>
<p><strong>Ops gotcha:</strong> a PDB set to <code>minAvailable: replicas</code> blocks drains entirely. Cluster operators need wiggle room. Aim for &ldquo;minimum acceptable&rdquo; rather than &ldquo;always all replicas&rdquo;.</p>
<p><strong><code>unhealthyPodEvictionPolicy: AlwaysAllow</code></strong> (K8s 1.27+) lets the cluster evict crash-looping Pods even if it would breach the PDB &mdash; otherwise stuck nodes can&rsquo;t drain, blocking the upgrade entirely. Critical for unblocking node maintenance.</p>'''

ANSWERS[48] = r'''<pre><code># .github/workflows/digitalocean.yml
name: Deploy to DigitalOcean
on:
  push: { branches: [main] }

permissions: { contents: read }

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    env:
      REGISTRY: registry.digitalocean.com/acme
      IMAGE:    api
      DROPLET:  prod-1
      USER:     deploy
    steps:
      - uses: actions/checkout@v4

      # 1) Auth to DOCR
      - uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
      - run: doctl registry login --expiry-seconds 1200

      # 2) Build &amp; push image (with cache)
      - uses: docker/setup-buildx-action@v3
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE }}
          tags: |
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # 3a) Deploy via SSH to a Droplet (script approach)
      - name: Deploy to Droplet
        env:
          SSH_KEY: ${{ secrets.DROPLET_SSH_KEY }}
          IMAGE_TAG: ${{ env.REGISTRY }}/${{ env.IMAGE }}:sha-${{ github.sha }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_KEY" &gt; ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          ssh -o StrictHostKeyChecking=no $USER@$DROPLET &lt;&lt;EOF
            doctl registry login --expiry-seconds 1200
            docker pull $IMAGE_TAG
            docker stop api 2&gt;/dev/null || true
            docker rm   api 2&gt;/dev/null || true
            docker run -d --name api --restart unless-stopped \
              -p 80:3000 \
              -e DATABASE_URL='${{ secrets.DATABASE_URL }}' \
              $IMAGE_TAG
            docker image prune -f
          EOF
</code></pre>
<p><strong>Two DigitalOcean deployment paths:</strong></p>
<table>
<tr><th></th><th>Droplet (this script)</th><th>App Platform</th></tr>
<tr><td>Mechanism</td><td>SSH + <code>docker run</code></td><td>Push to git or DOCR &rarr; auto-build</td></tr>
<tr><td>Control</td><td>Full</td><td>Higher-level abstraction</td></tr>
<tr><td>Best for</td><td>Custom infra, sticky workloads</td><td>Greenfield apps, simple CI</td></tr>
<tr><td>Action</td><td>script above</td><td><code>digitalocean/app_action/deploy@v2</code></td></tr>
</table>
<p><strong>App Platform deploy (often simpler):</strong></p>
<pre><code>- name: Deploy to App Platform
  uses: digitalocean/app_action/deploy@v2
  with:
    app_name: acme-api
    deploy_pr_preview: ${{ github.event_name == 'pull_request' }}
  env:
    DIGITALOCEAN_ACCESS_TOKEN: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
</code></pre>
<p><strong>For DOKS (DigitalOcean Kubernetes):</strong></p>
<pre><code>- run: doctl kubernetes cluster kubeconfig save my-cluster
- run: kubectl set image deployment/api api=${{ steps.meta.outputs.tags }} -n prod
- run: kubectl rollout status deployment/api -n prod --timeout=5m
</code></pre>
<p><strong>One-time setup:</strong></p>
<ol>
<li><em>DigitalOcean Control Panel &rarr; API &rarr; Tokens</em> &rarr; create a token &rarr; save as <code>DIGITALOCEAN_ACCESS_TOKEN</code> secret in GitHub.</li>
<li>For Droplets: generate an SSH keypair, add the public key to the Droplet&rsquo;s authorized_keys, save the private key as <code>DROPLET_SSH_KEY</code> secret.</li>
<li>Create a DOCR registry: <code>doctl registry create acme</code>.</li>
</ol>
<p><strong>Performance:</strong> Buildx GHA cache makes incremental builds 5-10&times; faster. For multi-region or high-availability, prefer DOKS over single Droplet. Use App Platform&rsquo;s built-in zero-downtime deploys instead of <code>docker stop / run</code> swaps.</p>'''

ANSWERS[49] = r'''<pre><code>// Jenkinsfile &mdash; Laravel app to a Kubernetes cluster
pipeline {
  agent any
  options { timeout(time: 30, unit: 'MINUTES') }
  environment {
    REGISTRY = 'ghcr.io/acme'
    APP      = 'laravel-api'
    NS       = 'prod'
    IMAGE    = "${REGISTRY}/${APP}:${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('PHP install &amp; tests') {
      steps {
        sh &apos;&apos;&apos;
          composer install --no-dev --prefer-dist --no-interaction --optimize-autoloader
          cp .env.testing .env
          php artisan key:generate
          php artisan config:clear
          vendor/bin/phpunit --testdox
          vendor/bin/phpstan analyse --level=6 app
        &apos;&apos;&apos;
      }
    }

    stage('Frontend assets') {
      steps {
        sh &apos;&apos;&apos;
          npm ci
          npm run build       # Vite/Mix produces public/build
        &apos;&apos;&apos;
      }
    }

    stage('Build &amp; push image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr',
            usernameVariable: 'U', passwordVariable: 'P')]) {
          sh &apos;&apos;&apos;
            echo $P | docker login ghcr.io -u $U --password-stdin
            docker build -t $IMAGE -t $REGISTRY/$APP:latest .
            docker push $IMAGE
            docker push $REGISTRY/$APP:latest
          &apos;&apos;&apos;
        }
      }
    }

    stage('Deploy to K8s') {
      when { branch 'main' }
      steps {
        withKubeConfig([credentialsId: 'kube-prod']) {
          sh &apos;&apos;&apos;
            # Run migrations as a one-shot Job (not in every Pod)
            kubectl create job --from=cronjob/laravel-migrate \
              migrate-$(date +%s) -n $NS --dry-run=client -o yaml \
              | sed "s|image: .*|image: $IMAGE|" | kubectl apply -f -

            kubectl wait --for=condition=complete --timeout=5m \
              -n $NS job -l app=migrate

            # Roll forward web + queue deployments
            kubectl set image deployment/laravel-web    web=$IMAGE -n $NS
            kubectl set image deployment/laravel-queue  queue=$IMAGE -n $NS
            kubectl rollout status deployment/laravel-web   -n $NS --timeout=5m
            kubectl rollout status deployment/laravel-queue -n $NS --timeout=5m

            # Cache warmup
            kubectl exec deployment/laravel-web -n $NS -- \
              php artisan config:cache route:cache view:cache
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { slackSend channel: '#deploys', message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>Companion <code>Dockerfile</code> (PHP-FPM + nginx in one image):</strong></p>
<pre><code>FROM php:8.3-fpm-alpine AS build
RUN apk add --no-cache nginx supervisor &amp;&amp; \
    docker-php-ext-install pdo_mysql opcache bcmath
WORKDIR /var/www/html
COPY composer.json composer.lock ./
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer &amp;&amp; \
    composer install --no-dev --no-scripts --prefer-dist
COPY . .
COPY public/build ./public/build
RUN composer dump-autoload --classmap-authoritative &amp;&amp; \
    php artisan config:cache &amp;&amp; \
    chown -R www-data:www-data storage bootstrap/cache
EXPOSE 8080
CMD ["/usr/bin/supervisord", "-n"]
</code></pre>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Helm chart</strong> &mdash; replace <code>kubectl set image</code> with <code>helm upgrade --install laravel ./chart -f values.prod.yaml --set image.tag=$IMAGE</code> for templated, versioned deploys.</li>
<li><strong>GitOps via Argo CD</strong> &mdash; CI only builds + pushes; a <code>kustomization.yaml</code> in a separate repo is bumped by a PR; Argo CD reconciles. Cleaner audit trail.</li>
<li><strong>Octane</strong> &mdash; for high RPS, swap PHP-FPM for Laravel Octane (Swoole/RoadRunner); 5-10&times; throughput.</li>
<li><strong>Sidecar architecture</strong> &mdash; nginx + PHP-FPM in <em>two</em> containers in one Pod sharing an <code>emptyDir</code> volume; cleaner separation than supervisord.</li>
</ul>
<p><strong>Performance:</strong> opcache + JIT (<code>php.ini: opcache.jit=tracing</code>) noticeably accelerates Laravel; preload via <code>opcache.preload</code>. Use <strong>Redis</strong> for session/cache/queue. Run migrations once via Job &mdash; never put <code>php artisan migrate</code> in container CMD.</p>'''

ANSWERS[50] = r'''<pre><code># db-secret.yaml &mdash; database credentials for an app
---
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: prod
type: Opaque
stringData:
  POSTGRES_HOST: postgres.db.svc.cluster.local
  POSTGRES_PORT: "5432"
  POSTGRES_DB: appdb
  POSTGRES_USER: app
  POSTGRES_PASSWORD: 'changeMeStrong!23'
  # Often easier: a single connection-string env var
  DATABASE_URL: postgresql://app:changeMeStrong!23@postgres.db.svc.cluster.local:5432/appdb
---
# Use it in a Deployment
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  replicas: 3
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          # Inject only what you need
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: db-credentials, key: DATABASE_URL }
          # Or all keys at once
          envFrom:
            - secretRef: { name: db-credentials }
</code></pre>
<p><strong>Imperative create (often safer than committing secret YAML):</strong></p>
<pre><code>kubectl create secret generic db-credentials \
  --from-literal=DATABASE_URL="postgresql://app:$(vault read -field=password secret/db)@postgres:5432/appdb" \
  -n prod \
  --dry-run=client -o yaml | kubectl apply -f -
</code></pre>
<p><strong>Critical caveats:</strong></p>
<ul>
<li><strong>Base64 is not encryption.</strong> Anyone with API access can <code>kubectl get secret db-credentials -o yaml | yq '.data.DATABASE_URL' | base64 -d</code>.</li>
<li><strong>Never commit raw Secret YAML to git.</strong> Use one of the patterns below.</li>
<li><strong>RBAC is your real defence</strong> &mdash; restrict <code>get/list secrets</code> to a tiny set of identities (deploy SA, app SA, on-call humans).</li>
<li><strong>Enable etcd encryption-at-rest.</strong> Most managed clusters have this on by default; verify before relying on it.</li>
</ul>
<p><strong>2026 best practice &mdash; pull from an external secret manager:</strong></p>
<pre><code># external-secret.yaml &mdash; via External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: db-credentials              # creates a native K8s Secret
    creationPolicy: Owner
  data:
    - secretKey: DATABASE_URL
      remoteRef: { key: prod/db, property: connection_url }
    - secretKey: POSTGRES_PASSWORD
      remoteRef: { key: prod/db, property: password }
</code></pre>
<p><strong>Pattern comparison:</strong></p>
<table>
<tr><th>Pattern</th><th>Where secrets live</th><th>Trade-off</th></tr>
<tr><td>Raw Secret YAML</td><td>etcd (base64)</td><td>Simple, but git-unsafe</td></tr>
<tr><td><strong>Sealed Secrets</strong></td><td>Encrypted in git</td><td>Git-safe; controller decrypts in-cluster</td></tr>
<tr><td><strong>SOPS-encrypted</strong></td><td>Encrypted in git, KMS-backed</td><td>Versioned, audited, GitOps-friendly</td></tr>
<tr><td><strong>External Secrets Operator</strong></td><td>AWS SM / Vault / GCP SM</td><td>Source-of-truth in vault; auto-rotation</td></tr>
<tr><td><strong>CSI Secrets Store</strong></td><td>Vault, mounted at runtime</td><td>No K8s Secret object at all</td></tr>
<tr><td><strong>Vault Agent Injector</strong></td><td>Sidecar fetches; writes to volume</td><td>Per-Pod credentials, dynamic DB creds</td></tr>
</table>
<p><strong>Best of all:</strong> use <strong>dynamic database credentials</strong> via Vault &mdash; each Pod gets a unique short-lived username/password; no static secret to leak.</p>'''

ANSWERS[51] = r'''<pre><code># docker-compose.yml &mdash; PostgreSQL for local dev
name: postgres-local

services:
  db:
    image: postgres:16-alpine
    container_name: pg
    restart: unless-stopped
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
      # Useful for stricter local replication of prod behaviour
      POSTGRES_INITDB_ARGS: "--data-checksums"
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - pg-data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d:ro      # *.sql + *.sh run on first boot
      - ./db/postgresql.conf:/etc/postgresql/postgresql.conf:ro
    command: ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 10
    shm_size: 256mb           # avoid &ldquo;could not resize shared memory segment&rdquo; on busy DBs

  pgadmin:
    image: dpage/pgadmin4
    profiles: [tools]
    environment:
      PGADMIN_DEFAULT_EMAIL: dev@local
      PGADMIN_DEFAULT_PASSWORD: dev
    ports: ["5050:80"]
    depends_on: [db]

volumes:
  pg-data: {}
</code></pre>
<p><strong>Run it:</strong></p>
<pre><code>docker compose up -d
docker compose --profile tools up -d   # also starts pgadmin
docker compose logs -f db
psql postgresql://app:secret@localhost:5432/app -c '\dt'
docker compose down -v                 # FULL reset (drops the volume)
</code></pre>
<p><strong>Init scripts pattern (<code>db/init/</code>):</strong></p>
<pre><code># 01-extensions.sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS &quot;uuid-ossp&quot;;

# 02-schema.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

# 03-seed.sh
psql -U app -d app -c "INSERT INTO users (email) VALUES ('alice@local');"
</code></pre>
<p><strong>Why these flags:</strong></p>
<ul>
<li><strong><code>postgres:16-alpine</code></strong> &mdash; small image with Postgres 16 (matches modern managed-service versions).</li>
<li><strong><code>PGDATA</code> in a subdirectory</strong> &mdash; lets the named volume contain other files (backups, logs) alongside the data dir without confusing init scripts.</li>
<li><strong>Health check</strong> &mdash; <code>pg_isready</code> reports actually-ready status; pair with <code>depends_on.condition: service_healthy</code> to gate dependent containers.</li>
<li><strong>Init scripts in <code>/docker-entrypoint-initdb.d</code></strong> &mdash; run once on first boot when the data dir is empty; ordering by filename prefix.</li>
<li><strong><code>shm_size</code></strong> &mdash; avoids common errors with parallel queries / large temp tables.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>tmpfs for tests</strong> &mdash; replace the volume with <code>tmpfs: { target: /var/lib/postgresql/data, tmpfs: { size: 1g } }</code>; massively faster, data ephemeral.</li>
<li><strong>postgres + extensions</strong> &mdash; use <code>pgvector/pgvector:pg16</code> for vector search, <code>postgis/postgis:16-3.4</code> for geospatial, <code>timescale/timescaledb:latest-pg16</code> for time-series.</li>
<li><strong>Replicas</strong> &mdash; add a <code>db-replica</code> service with <code>command: standby_mode</code>; not perfect mirror of managed services, OK for local replication testing.</li>
</ul>
<p><strong>2026 advice for production:</strong> <em>do not</em> ship Postgres-in-Compose to prod. Use <strong>RDS / Cloud SQL / Atlas / Neon / Supabase</strong> &mdash; they handle backup, PITR, replication, version upgrades, and patching far better than self-hosting. Compose is for laptop dev and CI integration tests.</p>'''

ANSWERS[52] = r'''<pre><code># .github/workflows/cloud-functions.yml
name: Deploy to Cloud Functions
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions:
  contents: read
  id-token: write           # OIDC for Workload Identity Federation

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    env:
      GCP_PROJECT: acme-prod
      GCP_REGION:  us-central1
      FUNC:        api-handler
      ENTRY:       handler            # Python function name
      RUNTIME:     python312          # Python 3.12 runtime
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5
      - run: uv pip install --system -r requirements.txt
      - run: uv run pytest -q

      # Workload Identity Federation &mdash; no service-account key needed
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh
          service_account: cf-deployer@acme-prod.iam.gserviceaccount.com

      - uses: google-github-actions/setup-gcloud@v2

      - name: Deploy (2nd-gen Cloud Functions)
        run: |
          gcloud functions deploy $FUNC \
            --gen2 \
            --runtime=$RUNTIME \
            --region=$GCP_REGION \
            --source=./src \
            --entry-point=$ENTRY \
            --trigger-http \
            --allow-unauthenticated \
            --memory=512Mi \
            --cpu=1 \
            --max-instances=20 \
            --min-instances=0 \
            --timeout=60s \
            --set-env-vars="ENV=production,LOG_LEVEL=info" \
            --set-secrets="DATABASE_URL=db-url:latest"
</code></pre>
<p><strong>Function source (<code>src/main.py</code>):</strong></p>
<pre><code>import functions_framework
import json, os
from flask import Request

@functions_framework.http
def handler(request: Request):
    return {
        "ok": True,
        "env": os.getenv("ENV"),
        "method": request.method,
        "path": request.path,
    }, 200, {"Content-Type": "application/json"}
</code></pre>
<p><strong>Workload Identity Federation setup &mdash; one-time:</strong></p>
<pre><code># Create a workload identity pool and provider trusting GitHub
gcloud iam workload-identity-pools create gh --location=global
gcloud iam workload-identity-pools providers create-oidc gh \
  --location=global --workload-identity-pool=gh \
  --issuer-uri=https://token.actions.githubusercontent.com \
  --attribute-mapping=google.subject=assertion.sub,attribute.repository=assertion.repository

# Allow the SA to be impersonated by your repo
gcloud iam service-accounts add-iam-policy-binding \
  cf-deployer@acme-prod.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/123/locations/global/workloadIdentityPools/gh/attribute.repository/acme/api"
</code></pre>
<p><strong>Why 2nd-gen Cloud Functions:</strong></p>
<ul>
<li><strong>Built on Cloud Run</strong> &mdash; longer requests (up to 60 min for HTTP, 9 min for events), bigger memory/CPU, concurrent execution per instance.</li>
<li><strong>Better cold start</strong> than 1st-gen.</li>
<li><strong>Eventarc triggers</strong> &mdash; broad ecosystem (Pub/Sub, Cloud Storage, Audit Logs, Cloud Build, Firestore, etc.).</li>
<li><strong>Same runtimes &amp; frameworks</strong> &mdash; Python, Node, Go, Java, .NET, Ruby, PHP.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Cloud Run directly</strong> &mdash; for richer container control; almost no functional difference at this point.</li>
<li><strong>Pub/Sub trigger</strong>: <code>--trigger-topic=my-topic</code>.</li>
<li><strong>Cloud Storage trigger</strong>: <code>--trigger-event-filters="type=google.cloud.storage.object.v1.finalized"</code>.</li>
<li><strong>Scheduled</strong>: pair with Cloud Scheduler hitting the function URL.</li>
</ul>
<p><strong>Performance:</strong> set <code>--min-instances=1</code> for sub-second responses; tune <code>--cpu</code> + <code>--memory</code> together (CPU scales with memory). For heavy Python startup, consider Lambda-style packaging in a container image instead.</p>'''

ANSWERS[53] = r'''<pre><code>// Jenkinsfile &mdash; load test a web app via k6
pipeline {
  agent any
  options { timeout(time: 30, unit: 'MINUTES') }
  parameters {
    string(name: 'TARGET', defaultValue: 'https://staging.api.acme.com', description: 'URL to test')
    choice(name: 'PROFILE', choices: ['smoke', 'load', 'stress', 'soak'], description: 'Test profile')
    string(name: 'VUS',       defaultValue: '50',  description: 'Virtual users')
    string(name: 'DURATION',  defaultValue: '5m',  description: 'Test duration')
  }
  environment {
    K6_PROMETHEUS_RW_SERVER_URL = 'http://prometheus.observability:9090/api/v1/write'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Pre-flight smoke') {
      steps {
        sh """
          docker run --rm \
            -e BASE_URL=${TARGET} \
            -v \$PWD:/scripts -w /scripts \
            grafana/k6:latest run --vus 1 --duration 30s tests/smoke.js
        """
      }
    }

    stage('Run load test') {
      steps {
        sh """
          docker run --rm \
            -e BASE_URL=${TARGET} \
            -e K6_PROMETHEUS_RW_SERVER_URL=${K6_PROMETHEUS_RW_SERVER_URL} \
            -v \$PWD:/scripts -w /scripts \
            grafana/k6:latest run \
              --vus ${VUS} \
              --duration ${DURATION} \
              --out experimental-prometheus-rw \
              --summary-export=results/${PROFILE}.json \
              tests/${PROFILE}.js
        """
      }
    }

    stage('Evaluate thresholds') {
      steps {
        sh &apos;&apos;&apos;
          # k6 returns non-zero exit code on threshold breach &rarr; pipeline fails
          # Optional: parse summary.json for richer reporting
          jq -r '
            "p95: " + (.metrics.http_req_duration.values["p(95)"] | tostring) +
            "ms  failed: " + (.metrics.http_req_failed.values.rate * 100 | tostring) + "%"
          ' results/${PROFILE}.json
        &apos;&apos;&apos;
        archiveArtifacts 'results/*.json'
      }
    }
  }
  post {
    always { junit allowEmptyResults: true, testResults: 'results/*.xml' }
    failure { slackSend channel: '#perf', message: "❌ Load test failed: ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>Sample k6 script (<code>tests/load.js</code>):</strong></p>
<pre><code>import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50  },   // ramp-up
    { duration: '4m',  target: 50  },   // hold
    { duration: '30s', target: 0   },   // ramp-down
  ],
  thresholds: {
    http_req_failed:   ['rate&lt;0.01'],         // &lt; 1% errors
    http_req_duration: ['p(95)&lt;500'],         // 95% under 500ms
    http_req_duration: ['p(99)&lt;1500'],
  },
};

export default function () {
  const r = http.get(`${__ENV.BASE_URL}/api/products`);
  check(r, { 'status 200': (res) =&gt; res.status === 200 });
  sleep(Math.random() * 2);
}
</code></pre>
<p><strong>Profile patterns:</strong></p>
<ul>
<li><strong>Smoke</strong> &mdash; 1 VU, 30s; sanity check after deploy.</li>
<li><strong>Load</strong> &mdash; expected production rate; verify SLOs.</li>
<li><strong>Stress</strong> &mdash; ramp until errors, find the breaking point.</li>
<li><strong>Soak</strong> &mdash; 1&ndash;24 hours at moderate load; surface memory leaks.</li>
<li><strong>Spike</strong> &mdash; sudden 10&times; jump; verify autoscaler responsiveness.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>JMeter</strong> &mdash; XML test plans, GUI tooling, longer history.</li>
<li><strong>Locust</strong> &mdash; Python-based, distributed master/worker.</li>
<li><strong>Gatling</strong> &mdash; Scala/Java, recordable HAR; great reports.</li>
<li><strong>Artillery</strong> &mdash; Node-based, simple YAML scenarios.</li>
<li><strong>k6 Cloud / Grafana k6</strong> &mdash; managed at scale; multi-region load.</li>
</ul>
<p><strong>Performance gotchas:</strong> never load-test against production. Run from <em>multiple regions</em> for realism. Watch <em>both ends</em> &mdash; client metrics (RPS, latency, errors) plus server-side observability (CPU, memory, DB connections, GC pauses). Set <code>thresholds</code> in the script so failures fail the pipeline automatically.</p>'''

ANSWERS[54] = r'''<pre><code># env-configmap.yaml &mdash; non-secret env config
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-env
  namespace: prod
data:
  NODE_ENV: production
  LOG_LEVEL: info
  PORT: "3000"
  ALLOWED_ORIGINS: "https://acme.com,https://www.acme.com"
  FEATURE_NEW_CHECKOUT: "true"
  CACHE_TTL_SECONDS: "60"
---
# deployment.yaml &mdash; consume env from the ConfigMap
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: prod
spec:
  replicas: 3
  selector: { matchLabels: { app: api } }
  template:
    metadata:
      labels: { app: api }
      annotations:
        # Force a rolling restart whenever the ConfigMap content hashes change
        config-hash: REPLACE_WITH_HASH_AT_DEPLOY_TIME
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0.0
          ports: [ { containerPort: 3000 } ]
          # 1) Inject all keys at once
          envFrom:
            - configMapRef: { name: api-env }
          # 2) Pick &amp; rename selected keys
          env:
            - name: APP_LOG_LEVEL
              valueFrom:
                configMapKeyRef: { name: api-env, key: LOG_LEVEL }
</code></pre>
<p><strong>Apply &amp; consume:</strong></p>
<pre><code>kubectl apply -f env-configmap.yaml
kubectl get cm api-env -n prod -o yaml
kubectl exec deployment/api -n prod -- printenv | grep -E '^(NODE_ENV|LOG_LEVEL|PORT)'
</code></pre>
<p><strong>The auto-restart-on-change problem:</strong></p>
<p>ConfigMaps consumed via <code>envFrom</code>/<code>env</code> are read <em>only at Pod start</em>. Editing the ConfigMap does <em>not</em> restart Pods automatically. Three solutions:</p>
<ol>
<li><strong>Manual rollout</strong>: <code>kubectl rollout restart deployment/api -n prod</code> after the ConfigMap change.</li>
<li><strong>Kustomize <code>configMapGenerator</code></strong> &mdash; auto-hashes the name (<code>api-env-7g4f8c</code>) so any change creates a new ConfigMap and the Deployment&rsquo;s reference changes, triggering a rollout:
<pre><code># kustomization.yaml
configMapGenerator:
  - name: api-env
    literals:
      - NODE_ENV=production
      - LOG_LEVEL=info
</code></pre>
</li>
<li><strong>Reloader</strong> (stakater/Reloader) &mdash; install once; annotate the Deployment with <code>reloader.stakater.com/auto: "true"</code>; ConfigMap/Secret edits trigger restarts automatically.</li>
</ol>
<p><strong>Volume-mounted ConfigMaps DO update</strong> &mdash; files in <code>/etc/config</code> reflect changes within ~60s. The app must re-read the file.</p>
<p><strong>Patterns by config size:</strong></p>
<table>
<tr><th>Size</th><th>Pattern</th></tr>
<tr><td>5-20 env vars</td><td>ConfigMap + <code>envFrom</code></td></tr>
<tr><td>Whole YAML/JSON file</td><td>ConfigMap volume mount; app reads file</td></tr>
<tr><td>Per-environment</td><td>Kustomize overlays or Helm values per env</td></tr>
<tr><td>Feature flags / live</td><td><strong>LaunchDarkly / Unleash / OpenFeature</strong> &mdash; not ConfigMaps</td></tr>
<tr><td>1+ MB</td><td>Object store; ConfigMaps capped at 1 MiB</td></tr>
</table>
<p><strong>Critical:</strong> <em>never put secrets in ConfigMaps</em>. Use <code>Secret</code> + External Secrets Operator. ConfigMaps are world-readable to anyone with namespace get rights; Secrets at least require explicit <code>get secrets</code> RBAC.</p>'''

ANSWERS[55] = r'''<pre><code># Dockerfile &mdash; Angular app, multi-stage, served by nginx
# --- builder
FROM node:20-alpine AS build
WORKDIR /app

# Cache deps
COPY package*.json ./
RUN npm ci

# Build with prod config
COPY . .
ARG CONFIG=production
RUN npx ng build --configuration=$CONFIG

# --- runtime
FROM nginx:1.27-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Angular outputs to dist/&lt;app-name&gt;/browser (Angular 17+) or dist/&lt;app-name&gt; (older)
COPY --from=build /app/dist/acme-web/browser /usr/share/nginx/html

# Run as non-root
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /var/run \
 &amp;&amp; sed -i 's/listen *80;/listen 8080;/' /etc/nginx/conf.d/default.conf
USER nginx
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -q --spider http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
</code></pre>
<p><strong>Companion <code>nginx.conf</code> with SPA-friendly routing + caching:</strong></p>
<pre><code>server {
    listen       80;
    server_name  _;
    root         /usr/share/nginx/html;
    index        index.html;

    # SPA fallback &mdash; Angular Router needs all unmatched routes to land on index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Long-cache content-hashed assets
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff2?|ico)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Don&rsquo;t cache index.html
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
}
</code></pre>
<p><strong>Build &amp; run:</strong></p>
<pre><code>docker build -t acme/angular-web:1.0.0 .
docker run -p 8080:8080 acme/angular-web:1.0.0
</code></pre>
<p><strong>Why each piece:</strong></p>
<ul>
<li><strong>Two stages</strong> &mdash; full Node toolchain in the builder, only static files + nginx in runtime (~30 MB image).</li>
<li><strong>Cached deps layer</strong> &mdash; <code>npm ci</code> from <code>package-lock.json</code> is deterministic and fast; runs only when lockfile changes.</li>
<li><strong>Build configuration arg</strong> &mdash; <code>CONFIG=production</code> activates AOT, minification, source-map removal.</li>
<li><strong>Angular 17+ output path</strong> &mdash; pay attention: it&rsquo;s now <code>dist/&lt;app&gt;/browser</code>; older versions used <code>dist/&lt;app&gt;</code>.</li>
<li><strong>Cache-immutable for hashed assets, no-cache for <code>index.html</code></strong> &mdash; the standard SPA caching contract.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Angular Universal SSR</strong> &mdash; final stage runs <code>node server.mjs</code> instead of nginx; deploy to Cloud Run / App Runner / Render.</li>
<li><strong>Distroless</strong> alternative for runtime &mdash; or use <strong>Caddy</strong> (auto-HTTPS, simpler config).</li>
<li><strong>Runtime env</strong> &mdash; Angular bakes env at build time; for runtime injection, replace placeholders in a <code>config.js</code> via <code>envsubst</code> in the entrypoint.</li>
<li><strong>Multi-arch</strong> &mdash; build with Buildx for amd64 + arm64 to support Graviton + Apple Silicon.</li>
</ul>
<p><strong>Performance:</strong> <code>.dockerignore</code> with <code>node_modules .git dist .angular coverage e2e</code> dramatically cuts context size. For very large apps, consider <strong>Nx</strong> with affected-only builds in CI. Static SPAs are usually best hosted on <strong>Vercel / Netlify / CloudFront / Cloudflare Pages</strong> &mdash; better edge caching, automatic HTTPS, no infra.</p>'''

ANSWERS[56] = r'''<pre><code># .github/workflows/rust.yml
name: Rust CI &amp; Deploy
on:
  push: { branches: [main] }
  pull_request:

permissions: { contents: read }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with: { components: rustfmt, clippy }
      - uses: Swatinem/rust-cache@v2

      - run: cargo fmt --all -- --check
      - run: cargo clippy --all-targets --all-features -- -D warnings
      - run: cargo test --all-features --workspace

  build:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        target: [x86_64-unknown-linux-musl, aarch64-unknown-linux-musl]
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with: { targets: ${{ matrix.target }} }
      - uses: Swatinem/rust-cache@v2
      - uses: taiki-e/install-action@v2
        with: { tool: cross }

      - run: cross build --release --target ${{ matrix.target }}

      - uses: actions/upload-artifact@v4
        with:
          name: api-${{ matrix.target }}
          path: target/${{ matrix.target }}/release/api

  release:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
</code></pre>
<p><strong>Companion <code>Dockerfile</code> (multi-stage, distroless final):</strong></p>
<pre><code>FROM rust:1.81-slim AS build
WORKDIR /src
RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends \
      pkg-config libssl-dev musl-tools &amp;&amp; rm -rf /var/lib/apt/lists/*
RUN rustup target add x86_64-unknown-linux-musl
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release --target x86_64-unknown-linux-musl

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /src/target/x86_64-unknown-linux-musl/release/api /api
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/api"]
</code></pre>
<p><strong>Why these patterns:</strong></p>
<ul>
<li><strong><code>Swatinem/rust-cache</code></strong> &mdash; caches <code>~/.cargo</code> + <code>target/</code> by lockfile hash; Rust builds without cache are notoriously slow.</li>
<li><strong>fmt + clippy + test in one job</strong> &mdash; fail fast on style/lint before running expensive builds.</li>
<li><strong><code>cross</code></strong> &mdash; cross-compile to musl for static binaries that run anywhere; arm64 too for Graviton/Apple Silicon.</li>
<li><strong>Distroless static</strong> &mdash; ~5 MB final image; no shell, no glibc, runs as nonroot.</li>
<li><strong>Multi-arch via Buildx</strong> &mdash; pulls native arch automatically.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Cargo workspaces</strong> &mdash; <code>cargo test --workspace</code> for monorepos; consider <code>cargo nextest</code> for 2&ndash;3&times; faster test runs.</li>
<li><strong>Coverage</strong> &mdash; <code>cargo llvm-cov --lcov --output-path lcov.info</code> + Codecov upload.</li>
<li><strong>Audit</strong> &mdash; <code>cargo audit</code> (RustSec advisories) and <code>cargo deny check</code> (license + duplicate-version + bans).</li>
<li><strong>Release with cargo-dist</strong> &mdash; opinionated GitHub Release pipeline with checksums + installers.</li>
</ul>
<p><strong>Performance:</strong> use <strong>sccache</strong> with the GHA backend for incremental compile cache across runs &mdash; cuts cold-cache times further. For very large workspaces, <code>--profile dev</code> tests first then <code>--release</code> only on main. Consider <code>RUSTFLAGS=-C strip=symbols</code> to shrink the final binary.</p>'''

ANSWERS[57] = r'''<pre><code>#!/usr/bin/env bash
# scale-deployment.sh &mdash; safely scale a Kubernetes Deployment up or down
set -euo pipefail

NAMESPACE=${NAMESPACE:-prod}
DEPLOY=${1:?Usage: $0 &lt;deployment&gt; &lt;replicas|auto&gt;}
REPLICAS=${2:?missing replica count or 'auto'}
TIMEOUT=${TIMEOUT:-5m}

if [[ "$REPLICAS" == "auto" ]]; then
  echo "==&gt; Setting up HPA for $DEPLOY"
  kubectl autoscale deployment "$DEPLOY" -n "$NAMESPACE" \
    --cpu-percent=70 --min=3 --max=20
else
  echo "==&gt; Scaling $DEPLOY to $REPLICAS replicas"
  CURRENT=$(kubectl get deployment "$DEPLOY" -n "$NAMESPACE" \
    -o jsonpath='{.spec.replicas}')
  echo "Current: $CURRENT, target: $REPLICAS"

  # Safety: block large scale-downs without confirmation
  if (( REPLICAS &lt; CURRENT / 2 )) &amp;&amp; [[ "${FORCE:-}" != "1" ]]; then
    echo "Refusing to scale down by &gt; 50% without FORCE=1"
    exit 1
  fi

  kubectl scale deployment "$DEPLOY" -n "$NAMESPACE" \
    --replicas="$REPLICAS"
  kubectl rollout status deployment/"$DEPLOY" -n "$NAMESPACE" \
    --timeout="$TIMEOUT"
fi

# Verification
kubectl get deployment "$DEPLOY" -n "$NAMESPACE"
kubectl get pods -n "$NAMESPACE" -l app="$DEPLOY"
</code></pre>
<p><strong>Examples:</strong></p>
<pre><code>./scale-deployment.sh api 5
./scale-deployment.sh api 0          # scale down to zero
./scale-deployment.sh api auto       # convert to HPA
FORCE=1 ./scale-deployment.sh api 1  # force aggressive scale-down
</code></pre>
<p><strong>Capacity-based scaling for traffic spikes (event-driven via cron):</strong></p>
<pre><code>#!/usr/bin/env bash
# scale-by-time.sh &mdash; warm up before predictable traffic
HOUR=$(date +%H)
case "$HOUR" in
  06|07|08) kubectl scale deploy/api -n prod --replicas=15 ;;  # morning peak
  18|19|20) kubectl scale deploy/api -n prod --replicas=20 ;;  # evening peak
  *)        kubectl scale deploy/api -n prod --replicas=5  ;;  # off-peak
esac
</code></pre>
<p><strong>Set up via CronJob inside the cluster (no external cron needed):</strong></p>
<pre><code>apiVersion: batch/v1
kind: CronJob
metadata: { name: scale-up-morning, namespace: prod }
spec:
  schedule: "0 6 * * 1-5"        # weekdays 06:00 UTC
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: scaler
          restartPolicy: OnFailure
          containers:
            - name: kubectl
              image: bitnami/kubectl:1.30
              command: ["kubectl", "scale", "deploy/api", "-n", "prod", "--replicas=15"]
</code></pre>
<p><strong>2026 best-practice scaling stack:</strong></p>
<table>
<tr><th>Scale dimension</th><th>Tool</th></tr>
<tr><td>Pod count by CPU/RAM</td><td><strong>HorizontalPodAutoscaler</strong> (built-in)</td></tr>
<tr><td>Pod count by event source (queue depth, RPS)</td><td><strong>KEDA</strong> &mdash; 60+ scalers, supports scale-to-zero</td></tr>
<tr><td>Pod request/limit right-sizing</td><td><strong>VerticalPodAutoscaler</strong></td></tr>
<tr><td>Node count to fit pending Pods</td><td><strong>Cluster Autoscaler</strong> or <strong>Karpenter</strong></td></tr>
<tr><td>Cost-aware bin-packing</td><td><strong>Karpenter</strong> (AWS), <strong>GKE Autopilot</strong></td></tr>
</table>
<p><strong>Critical:</strong> always pair scaling with a <strong>PodDisruptionBudget</strong> so the autoscaler can&rsquo;t drain you below your safety floor; set <code>resources.requests</code> on every container so the scheduler can place new Pods accurately.</p>
<p><strong>Gotchas:</strong> manual <code>kubectl scale</code> is <em>overridden</em> by HPA &mdash; if both exist, HPA wins. Use <code>kubectl autoscale</code>, not both. To pause HPA without deleting it: <code>kubectl scale hpa api --replicas=0</code> doesn&rsquo;t work; instead patch <code>spec.maxReplicas</code> down or remove the HPA temporarily.</p>'''

ANSWERS[58] = r'''<pre><code>// Jenkinsfile &mdash; .NET to AWS Elastic Beanstalk
pipeline {
  agent any
  options { timeout(time: 30, unit: 'MINUTES') }
  environment {
    AWS_REGION = 'us-east-1'
    EB_APP     = 'acme-api'
    EB_ENV     = 'acme-api-prod'
    S3_BUCKET  = 'acme-eb-bundles'
    DOTNET_VER = '8.0.x'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Setup .NET') {
      steps {
        sh &apos;&apos;&apos;
          curl -sSL https://dot.net/v1/dotnet-install.sh -o install.sh
          chmod +x install.sh
          ./install.sh --channel $DOTNET_VER --install-dir $HOME/dotnet
          export PATH=$HOME/dotnet:$PATH
          dotnet --info
        &apos;&apos;&apos;
      }
    }

    stage('Restore, build, test') {
      steps {
        sh &apos;&apos;&apos;
          export PATH=$HOME/dotnet:$PATH
          dotnet restore
          dotnet build -c Release --no-restore
          dotnet test -c Release --no-build \
            --logger "trx;LogFileName=results.trx"
        &apos;&apos;&apos;
      }
      post { always { mstest testResultsFile: '**/*.trx' } }
    }

    stage('Publish &amp; package') {
      steps {
        sh &apos;&apos;&apos;
          export PATH=$HOME/dotnet:$PATH
          dotnet publish src/Api/Api.csproj \
            -c Release -r linux-x64 --self-contained false \
            -o publish --no-build

          # Beanstalk Linux platforms expect &lt;app&gt;-&lt;ver&gt;.zip with Procfile or aws-windows-deployment-manifest.json
          cp Procfile publish/Procfile
          (cd publish &amp;&amp; zip -qr ../deploy.zip .)
        &apos;&apos;&apos;
        archiveArtifacts 'deploy.zip'
      }
    }

    stage('Deploy to Beanstalk') {
      when { branch 'main' }
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                          credentialsId: 'aws-deploy']]) {
          sh &apos;&apos;&apos;
            VERSION="${BUILD_NUMBER}-${GIT_COMMIT::7}"
            S3_KEY="${EB_APP}/${VERSION}.zip"

            aws s3 cp deploy.zip s3://${S3_BUCKET}/${S3_KEY} --region $AWS_REGION

            aws elasticbeanstalk create-application-version \
              --application-name $EB_APP \
              --version-label $VERSION \
              --source-bundle S3Bucket=$S3_BUCKET,S3Key=$S3_KEY \
              --region $AWS_REGION

            aws elasticbeanstalk update-environment \
              --application-name $EB_APP \
              --environment-name $EB_ENV \
              --version-label $VERSION \
              --region $AWS_REGION

            # Wait for the environment to stabilise
            aws elasticbeanstalk wait environment-updated \
              --application-name $EB_APP \
              --environment-names $EB_ENV \
              --region $AWS_REGION

            # Final health check
            aws elasticbeanstalk describe-environments \
              --application-name $EB_APP --environment-names $EB_ENV \
              --region $AWS_REGION \
              --query 'Environments[0].[Status,Health,VersionLabel]' --output table
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { slackSend channel: '#deploys', message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong><code>Procfile</code> (the Beanstalk Linux entrypoint):</strong></p>
<pre><code>web: dotnet Api.dll --urls=http://0.0.0.0:5000
</code></pre>
<p><strong>One-time setup:</strong></p>
<ol>
<li>Create an EB application + environment on a .NET on Linux platform: <code>eb init</code> + <code>eb create</code>.</li>
<li>Create an S3 bucket for app version bundles (the <code>$S3_BUCKET</code> variable).</li>
<li>Create an IAM role for Jenkins with permissions: <code>elasticbeanstalk:*</code>, <code>s3:PutObject</code> on the bundle bucket.</li>
</ol>
<p><strong>Variants &amp; alternatives for 2026:</strong></p>
<ul>
<li><strong>ECS / Fargate</strong> &mdash; build a container image, push to ECR, update task def. More flexible, smaller cold-start, easier scaling than Beanstalk for new apps.</li>
<li><strong>App Runner</strong> &mdash; managed container with built-in CI/CD; the closest spiritual successor to Beanstalk for containerised apps.</li>
<li><strong>EKS</strong> &mdash; if you&rsquo;re standardising on Kubernetes.</li>
<li><strong>Beanstalk</strong> remains a solid choice for legacy .NET Framework on Windows, but for .NET Core/8+ on Linux, ECS Fargate is usually the better path now.</li>
<li><strong>OIDC federation</strong> on GitHub Actions removes the stored AWS credentials entirely; on Jenkins you&rsquo;re still on stored creds.</li>
</ul>
<p><strong>Performance / safety:</strong> use <em>Rolling with additional batch</em> deployment policy to avoid downtime; <em>Immutable</em> deploys for safer rollback (new instances, then switch); set <code>HealthCheckURL</code> to <code>/health</code> in the EB config so failed deploys auto-rollback.</p>'''

ANSWERS[59] = r'''<pre><code># sa-rbac.yaml &mdash; ServiceAccount with namespace-scoped permissions
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api-deployer
  namespace: prod
  # Disable token auto-mount on SA &mdash; explicitly opt in per Pod
automountServiceAccountToken: false
---
# Namespace-scoped Role &mdash; just what the SA needs
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: api-deployer
  namespace: prod
rules:
  - apiGroups: ["apps"]
    resources: [deployments]
    verbs: [get, list, watch, patch, update]
    resourceNames: [api]                  # only this specific Deployment
  - apiGroups: [""]
    resources: [pods, pods/log, events]
    verbs: [get, list, watch]
  - apiGroups: [""]
    resources: [configmaps]
    verbs: [get, list, watch, update]
    resourceNames: [api-config, api-env]
---
# RoleBinding &mdash; attach the Role to the ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: api-deployer
  namespace: prod
subjects:
  - kind: ServiceAccount
    name: api-deployer
    namespace: prod
roleRef:
  kind: Role
  name: api-deployer
  apiGroup: rbac.authorization.k8s.io
---
# Cluster-wide read access &mdash; ClusterRole + ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata: { name: read-only-viewer }
rules:
  - apiGroups: [""]
    resources: [pods, services, endpoints, namespaces]
    verbs: [get, list, watch]
  - apiGroups: ["apps"]
    resources: [deployments, statefulsets, daemonsets, replicasets]
    verbs: [get, list, watch]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata: { name: read-only-viewer }
subjects:
  - kind: ServiceAccount
    name: api-deployer
    namespace: prod
roleRef:
  kind: ClusterRole
  name: read-only-viewer
  apiGroup: rbac.authorization.k8s.io
</code></pre>
<p><strong>Use the SA in a Pod / Deployment:</strong></p>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata: { name: deployer-sidecar, namespace: prod }
spec:
  template:
    spec:
      serviceAccountName: api-deployer       # NOT &ldquo;default&rdquo;
      automountServiceAccountToken: true     # explicitly opt in
      containers:
        - name: kubectl
          image: bitnami/kubectl:1.30
          command: ["sleep", "infinity"]
</code></pre>
<p><strong>Apply &amp; verify:</strong></p>
<pre><code>kubectl apply -f sa-rbac.yaml
kubectl get sa,role,rolebinding -n prod

# Test what the SA can/cannot do
kubectl auth can-i list deployments \
  --as=system:serviceaccount:prod:api-deployer -n prod
kubectl auth can-i delete deployments \
  --as=system:serviceaccount:prod:api-deployer -n prod   # &rarr; no
</code></pre>
<p><strong>Mental model:</strong></p>
<ul>
<li><strong>ServiceAccount</strong> &mdash; a workload identity. Pods authenticate to the API server using the SA&rsquo;s token.</li>
<li><strong>Role</strong> / <strong>ClusterRole</strong> &mdash; lists of permissions; namespaced vs cluster-wide.</li>
<li><strong>RoleBinding</strong> / <strong>ClusterRoleBinding</strong> &mdash; the wire that connects subjects (SA, user, group) to roles.</li>
<li><strong>Subject types</strong> &mdash; <code>ServiceAccount</code>, <code>User</code>, <code>Group</code>; users and groups are external (OIDC, x509).</li>
</ul>
<p><strong>Least-privilege patterns:</strong></p>
<ul>
<li><strong><code>resourceNames</code></strong> restricts the Role to specific objects, not all of a kind &mdash; powerful for &ldquo;this SA can patch only the api Deployment&rdquo;.</li>
<li><strong>Verb hygiene</strong> &mdash; prefer <code>get/list/watch</code> + <code>patch</code> over the catch-all <code>*</code>; never grant <code>create</code> on Secrets unless required.</li>
<li><strong>Audit</strong> &mdash; <code>kubectl auth can-i --list --as=system:serviceaccount:NS:NAME</code> shows everything an SA can do.</li>
<li><strong>Workload Identity / IRSA</strong> &mdash; map K8s SAs to cloud IAM roles via OIDC instead of mounting cloud creds; on EKS use IRSA, on GKE use Workload Identity, on AKS use Workload Identity Federation.</li>
</ul>
<p><strong>Tools:</strong> <strong>RBAC Manager</strong> (FairwindsOps), <strong>kubectl-who-can</strong>, <strong>krane</strong> for visualisation/audit. <strong>OPA Gatekeeper</strong> / <strong>Kyverno</strong> enforce policy on top of RBAC (e.g. &ldquo;no Pod may use the default SA&rdquo;).</p>'''

ANSWERS[60] = r'''<pre><code># job-cleanup.yaml &mdash; one-time cleanup task as a K8s Job
apiVersion: batch/v1
kind: Job
metadata:
  name: cleanup-old-uploads
  namespace: prod
spec:
  ttlSecondsAfterFinished: 86400      # auto-delete Pod 24h later
  backoffLimit: 2                     # retry twice on failure
  activeDeadlineSeconds: 3600         # kill if runs &gt; 1h
  template:
    spec:
      restartPolicy: Never
      serviceAccountName: cleanup-sa
      containers:
        - name: cleaner
          image: amazon/aws-cli:2
          command: ["sh", "-c"]
          args:
            - |
              set -e
              CUTOFF=$(date -d '30 days ago' --iso-8601=seconds)
              echo "Deleting uploads older than $CUTOFF"
              aws s3api list-objects-v2 --bucket acme-uploads \
                --query "Contents[?LastModified&lt;\`$CUTOFF\`].Key" --output text \
                | xargs -n 100 -P 4 aws s3 rm "s3://acme-uploads/" --recursive
          envFrom:
            - secretRef: { name: aws-creds }
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits:   { cpu: 500m, memory: 256Mi }
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
---
# CronJob &mdash; same Pod template, scheduled
apiVersion: batch/v1
kind: CronJob
metadata: { name: cleanup-uploads-nightly, namespace: prod }
spec:
  schedule: "0 3 * * *"                # 03:00 UTC daily
  concurrencyPolicy: Forbid            # don&rsquo;t start a new run if last is still running
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  startingDeadlineSeconds: 600         # tolerance for missed schedules
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: cleaner
              image: amazon/aws-cli:2
              command: ["./cleanup.sh"]
</code></pre>
<p><strong>Run, watch, inspect:</strong></p>
<pre><code>kubectl apply -f job-cleanup.yaml
kubectl get jobs -n prod
kubectl logs -f -l job-name=cleanup-old-uploads -n prod
kubectl wait --for=condition=complete job/cleanup-old-uploads \
  -n prod --timeout=1h

# Trigger CronJob manually
kubectl create job --from=cronjob/cleanup-uploads-nightly \
  manual-cleanup-$(date +%s) -n prod
</code></pre>
<p><strong>Key fields:</strong></p>
<ul>
<li><strong><code>restartPolicy: Never</code> or <code>OnFailure</code></strong> &mdash; required for Jobs (vs <code>Always</code> for Deployments).</li>
<li><strong><code>backoffLimit</code></strong> &mdash; how many failures tolerated before the Job is marked failed.</li>
<li><strong><code>ttlSecondsAfterFinished</code></strong> &mdash; auto-cleanup; otherwise old Pods linger forever.</li>
<li><strong><code>activeDeadlineSeconds</code></strong> &mdash; hard wall-clock timeout, kills runaway jobs.</li>
<li><strong><code>concurrencyPolicy</code></strong> on CronJobs: <code>Allow</code> (default), <code>Forbid</code> (skip if previous still running &mdash; usually right), <code>Replace</code> (kill the old one).</li>
<li><strong><code>startingDeadlineSeconds</code></strong> &mdash; tolerance for missed schedules; without it, missed schedules due to controller restarts may never fire.</li>
</ul>
<p><strong>Job vs CronJob vs orchestrator:</strong></p>
<table>
<tr><th>Need</th><th>Tool</th></tr>
<tr><td>One-time task</td><td>Job</td></tr>
<tr><td>Scheduled task</td><td>CronJob</td></tr>
<tr><td>Embarrassingly parallel</td><td>Job with <code>parallelism</code> + <code>completions</code> + <code>completionMode: Indexed</code></td></tr>
<tr><td>DAG of tasks</td><td><strong>Argo Workflows</strong>, <strong>Tekton</strong>, <strong>Volcano</strong></td></tr>
<tr><td>Long-running stateful workflow</td><td><strong>Temporal</strong></td></tr>
<tr><td>Event-driven</td><td><strong>KEDA ScaledJob</strong> &mdash; Job per event</td></tr>
</table>
<p><strong>Performance / ops:</strong> set <code>resources.requests</code> so the scheduler can place the Pod accurately; for huge fan-outs, throttle <code>parallelism</code> based on cluster capacity / external rate limits to avoid thundering herds. Capture logs by uploading to S3 / Loki at the end of the job &mdash; Pod logs disappear with TTL.</p>'''

ANSWERS[61] = r'''<pre><code># docker-compose.yml &mdash; MongoDB for local dev (with admin UI)
name: mongo-local

services:
  mongo:
    image: mongo:7
    container_name: mongo
    restart: unless-stopped
    ports: ["27017:27017"]
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: secret
      MONGO_INITDB_DATABASE: app
    volumes:
      - mongo-data:/data/db
      - mongo-cfg:/data/configdb
      - ./mongo/init:/docker-entrypoint-initdb.d:ro
    command: ["--wiredTigerCacheSizeGB", "1"]
    healthcheck:
      test: ["CMD", "mongosh", "-u", "root", "-p", "secret", "--authenticationDatabase", "admin",
             "--eval", "db.runCommand({ ping: 1 }).ok"]
      interval: 5s
      retries: 10

  # Initialise a replica set on first boot &mdash; required for transactions / change streams
  mongo-init-rs:
    image: mongo:7
    profiles: [replica]
    depends_on: [mongo]
    entrypoint: ["bash", "-c"]
    command:
      - |
          sleep 5
          mongosh "mongodb://root:secret@mongo:27017/?authSource=admin" --eval '
            try { rs.status() } catch (_) {
              rs.initiate({ _id: "rs0", members: [{ _id: 0, host: "mongo:27017" }] })
            }
          '

  mongo-express:
    image: mongo-express:1
    profiles: [tools]
    depends_on: [mongo]
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: root
      ME_CONFIG_MONGODB_ADMINPASSWORD: secret
      ME_CONFIG_MONGODB_URL: mongodb://root:secret@mongo:27017/
      ME_CONFIG_BASICAUTH_USERNAME: dev
      ME_CONFIG_BASICAUTH_PASSWORD: dev
    ports: ["8081:8081"]

volumes:
  mongo-data: {}
  mongo-cfg:  {}
</code></pre>
<p><strong>Run it:</strong></p>
<pre><code>docker compose up -d                       # core mongo only
docker compose --profile tools up -d       # + mongo-express UI on :8081
docker compose --profile replica up -d     # also init replica set
mongosh "mongodb://root:secret@localhost:27017/?authSource=admin"
docker compose down -v                     # FULL reset
</code></pre>
<p><strong>Init scripts (<code>mongo/init/</code>):</strong></p>
<pre><code># 01-create-app-user.js  &mdash; runs only on first boot
db = db.getSiblingDB('app');
db.createUser({
  user: 'app',
  pwd: 'app-secret',
  roles: [{ role: 'readWrite', db: 'app' }],
});

# 02-seed.js
db.users.insertMany([
  { email: 'alice@local', createdAt: new Date() },
  { email: 'bob@local',   createdAt: new Date() },
]);
db.users.createIndex({ email: 1 }, { unique: true });
</code></pre>
<p><strong>Why these flags:</strong></p>
<ul>
<li><strong>Root user envs</strong> &mdash; created on first boot only; persistent volume preserves them across restarts.</li>
<li><strong><code>wiredTigerCacheSizeGB</code></strong> &mdash; explicit cache cap; Mongo defaults to half of (RAM &minus; 1 GB) which can crash the host on a laptop.</li>
<li><strong>Health check</strong> &mdash; <code>mongosh ping</code> reports actually-ready; pair with <code>depends_on.condition: service_healthy</code> in dependent services.</li>
<li><strong>Replica set profile</strong> &mdash; transactions and change streams require a replica set, even single-node. The <code>mongo-init-rs</code> service idempotently calls <code>rs.initiate()</code>.</li>
<li><strong>Init scripts</strong> &mdash; only run on first boot when <code>/data/db</code> is empty; safe to re-deploy.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>tmpfs for tests</strong> &mdash; ephemeral data, much faster: <code>tmpfs: { target: /data/db, tmpfs: { size: 1g } }</code>.</li>
<li><strong>Multi-node replica set</strong> &mdash; three <code>mongo</code> services with <code>--replSet rs0</code>; cleaner mirror of prod cluster behaviour.</li>
<li><strong>Vector / search</strong> &mdash; use <code>mongo:7-enterprise</code> for Atlas Search-compatible features locally.</li>
</ul>
<p><strong>2026 advice for production:</strong> run on <strong>MongoDB Atlas</strong>, <strong>DocumentDB</strong>, or <strong>Cosmos DB Mongo API</strong>; you skip backup, replica-set ops, version upgrades, and TLS cert management. Compose-Mongo is for laptop dev and CI integration tests &mdash; never production.</p>'''

ANSWERS[62] = r'''<pre><code># .github/workflows/ruby-heroku.yml
name: Deploy Ruby to Heroku
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions: { contents: read }

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: postgres }
        ports: [5432:5432]
        options: --health-cmd "pg_isready -U postgres" --health-interval 5s --health-retries 10
      redis:
        image: redis:7
        ports: [6379:6379]
    env:
      DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
      REDIS_URL:    redis://localhost:6379
      RAILS_ENV:    test
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.3', bundler-cache: true }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: yarn }
      - run: yarn install --frozen-lockfile
      - run: bundle exec rails db:create db:schema:load
      - run: bundle exec rspec
      - run: bundle exec rubocop
      - run: bundle exec brakeman --no-pager

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # Heroku rejects shallow clones

      # Container deploy &mdash; recommended in 2026
      - name: Login to Heroku Container Registry
        run: echo "${{ secrets.HEROKU_API_KEY }}" \
          | docker login --username=_ --password-stdin registry.heroku.com

      - name: Build &amp; push web image
        env: { APP: ${{ secrets.HEROKU_APP_NAME }} }
        run: |
          docker build -t registry.heroku.com/$APP/web .
          docker push registry.heroku.com/$APP/web

      - name: Release &amp; migrate
        env:
          APP: ${{ secrets.HEROKU_APP_NAME }}
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
        run: |
          heroku container:release web -a $APP
          heroku run -a $APP -- rails db:migrate
</code></pre>
<p><strong>Companion <code>Dockerfile</code> for Rails on Heroku:</strong></p>
<pre><code>FROM ruby:3.3-slim AS build
WORKDIR /app
RUN apt-get update &amp;&amp; apt-get install -y build-essential libpq-dev nodejs yarn git
COPY Gemfile* ./
RUN bundle config set --local without 'development test' &amp;&amp; bundle install
COPY package*.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN bundle exec rails assets:precompile

FROM ruby:3.3-slim
RUN apt-get update &amp;&amp; apt-get install -y libpq5 libjemalloc2 &amp;&amp; rm -rf /var/lib/apt/lists/*
ENV LD_PRELOAD=libjemalloc.so.2 RAILS_LOG_TO_STDOUT=1 RAILS_SERVE_STATIC_FILES=1
WORKDIR /app
COPY --from=build /app /app
USER 1000
# Heroku injects $PORT &mdash; respect it
CMD ["sh", "-c", "bundle exec puma -p $PORT -C config/puma.rb"]
</code></pre>
<p><strong>Buildpack alternative (no Dockerfile):</strong></p>
<pre><code>- uses: akhileshns/heroku-deploy@v3.13.15
  with:
    heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
    heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
    heroku_email: ${{ secrets.HEROKU_EMAIL }}
    procfile: 'web: bundle exec puma -p $PORT'
</code></pre>
<p><strong>Setup &mdash; one-time:</strong></p>
<ol>
<li><em>Heroku &rarr; Account Settings &rarr; API Key</em>; save as <code>HEROKU_API_KEY</code> in GitHub secrets.</li>
<li>Create the app + add Heroku Postgres + Redis: <code>heroku addons:create heroku-postgresql:essential-0 -a my-app</code>.</li>
<li>Set runtime env: <code>heroku config:set RAILS_MASTER_KEY=$(cat config/master.key) -a my-app</code>.</li>
</ol>
<p><strong>2026 reality:</strong> Heroku still works but is no longer the obvious default. Strong alternatives: <strong>Render</strong>, <strong>Fly.io</strong>, <strong>Railway</strong>, <strong>Cloud Run</strong>, <strong>App Runner</strong>, <strong>DigitalOcean App Platform</strong>. For Rails specifically, the Rails team itself now ships <strong>Kamal</strong> for SSH-based container deploys to your own VMs &mdash; significantly cheaper at scale than Heroku, with comparable ergonomics.</p>
<p><strong>Performance:</strong> use <strong>Heroku Pipelines</strong> (review apps + staging + production) for safer flows; enable <strong>Preboot</strong> for zero-downtime restarts on Performance dynos; jemalloc + bootsnap shave 30&ndash;50% memory + boot time.</p>'''

ANSWERS[63] = r'''<pre><code># NOTE: PodPreset was REMOVED in Kubernetes 1.20.
# This question reflects an older API. The 2026 alternatives are below.

# &mdash;&mdash; Method 1: ConfigMap envFrom + Pod patcher (Kustomize)
apiVersion: v1
kind: ConfigMap
metadata:
  name: shared-env
  namespace: prod
data:
  CLUSTER_NAME: prod-us-east
  REGION: us-east-1
  TRACING_ENDPOINT: http://otel-collector:4318
  LOG_FORMAT: json
---
# kustomization.yaml &mdash; patches every Deployment in this namespace
patches:
  - patch: |
      - op: add
        path: /spec/template/spec/containers/0/envFrom/-
        value:
          configMapRef:
            name: shared-env
    target:
      kind: Deployment
      labelSelector: "needs-shared-env=true"
</code></pre>
<p><strong>Method 2: MutatingWebhook for cluster-wide injection</strong> (the K8s-native PodPreset replacement):</p>
<pre><code># mutatingwebhook.yaml &mdash; admission controller injects env into every Pod
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata: { name: shared-env-injector }
webhooks:
  - name: env-injector.acme.com
    sideEffects: None
    admissionReviewVersions: ["v1"]
    rules:
      - operations: [CREATE]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: [pods]
    namespaceSelector:
      matchLabels: { env-injection: enabled }
    clientConfig:
      service:
        name: env-injector-webhook
        namespace: kube-system
        path: /mutate
      caBundle: LS0tLS1CRUdJTi...
</code></pre>
<p>The webhook receives every Pod creation, patches in env vars from a config source, returns the modified Pod spec.</p>
<p><strong>Method 3: Kyverno policy (the easiest in 2026)</strong></p>
<pre><code>apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: inject-shared-env }
spec:
  rules:
    - name: add-cluster-env
      match: { any: [ { resources: { kinds: [Pod] } } ] }
      mutate:
        patchStrategicMerge:
          spec:
            containers:
              - (name): "*"
                env:
                  - { name: CLUSTER_NAME, value: "prod-us-east" }
                  - { name: REGION,       value: "us-east-1"    }
</code></pre>
<p><strong>Method 4: Operator-managed sidecar injection</strong> (e.g. Istio, Linkerd, OpenTelemetry Operator) &mdash; opt-in via annotation:</p>
<pre><code>metadata:
  annotations:
    sidecar.opentelemetry.io/inject: "true"
    instrumentation.opentelemetry.io/inject-python: "true"
</code></pre>
<p><strong>Why PodPreset went away:</strong> the API was alpha for years and never matured. Mutating webhooks are the supported, more flexible pattern; they let you implement <em>any</em> mutation logic, not just env-var injection.</p>
<p><strong>Comparison:</strong></p>
<table>
<tr><th>Approach</th><th>When to use</th></tr>
<tr><td>ConfigMap + manifest patches</td><td>Small teams, GitOps-only flows; explicit per-Deployment</td></tr>
<tr><td>Kustomize patches</td><td>Cross-cutting concerns within a controlled set of manifests</td></tr>
<tr><td><strong>Kyverno</strong> ClusterPolicy</td><td><em>Recommended default for 2026</em> &mdash; declarative, no Go code</td></tr>
<tr><td><strong>OPA Gatekeeper</strong> mutation</td><td>Same league as Kyverno; Rego-based</td></tr>
<tr><td>Custom mutating webhook</td><td>Complex injection logic; service mesh / observability vendors</td></tr>
</table>
<p><strong>2026 advice:</strong> reach for <strong>Kyverno</strong> or <strong>Gatekeeper</strong> first. They&rsquo;re mature, audited, and don&rsquo;t require building/operating a webhook service. Reserve custom webhooks for vendor-style platforms (Istio, Datadog, OTel) where the injection logic is genuinely complex.</p>'''

ANSWERS[64] = r'''<pre><code>// Jenkinsfile &mdash; Scala (sbt) deploy to Google App Engine
pipeline {
  agent any
  tools { jdk 'jdk-21' }
  options { timeout(time: 25, unit: 'MINUTES') }
  environment {
    GCP_PROJECT = 'acme-prod'
    SBT_VERSION = '1.10'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Install sbt') {
      steps {
        sh &apos;&apos;&apos;
          curl -L https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}.0/sbt-${SBT_VERSION}.0.tgz \
            | tar xz -C $HOME
          export PATH=$HOME/sbt/bin:$PATH
          sbt --version
        &apos;&apos;&apos;
      }
    }

    stage('Test') {
      steps {
        sh &apos;&apos;&apos;
          export PATH=$HOME/sbt/bin:$PATH
          sbt -batch clean test
          sbt -batch scalafmtCheckAll
          sbt -batch scalafixAll --check
        &apos;&apos;&apos;
      }
      post { always { junit '**/target/test-reports/*.xml' } }
    }

    stage('Build &amp; assemble jar') {
      steps {
        sh &apos;&apos;&apos;
          export PATH=$HOME/sbt/bin:$PATH
          sbt -batch clean assembly
          mkdir -p deploy
          cp target/scala-2.13/*-assembly-*.jar deploy/app.jar
          cp app.yaml Dockerfile deploy/
        &apos;&apos;&apos;
        archiveArtifacts 'deploy/*'
      }
    }

    stage('Deploy to App Engine (Flex)') {
      when { branch 'main' }
      steps {
        withCredentials([file(credentialsId: 'gcp-deploy-sa', variable: 'GCP_KEY')]) {
          sh &apos;&apos;&apos;
            gcloud auth activate-service-account --key-file=$GCP_KEY
            gcloud config set project $GCP_PROJECT

            # Promote new version, keep one rollback target
            gcloud app deploy deploy/app.yaml \
              --project=$GCP_PROJECT \
              --quiet --promote --stop-previous-version=false

            # Smoke check
            URL=$(gcloud app browse --no-launch-browser 2&gt;&amp;1 | grep -oE 'https://[^ ]+')
            curl -fsS "$URL/health"
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { slackSend channel: '#deploys', message: "✅ ${env.JOB_NAME}" }
    failure { slackSend channel: '#deploys', message: "❌ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong><code>app.yaml</code> for App Engine Flex (custom runtime via Docker):</strong></p>
<pre><code>runtime: custom
env: flex
service: scala-api

resources:
  cpu: 2
  memory_gb: 2

automatic_scaling:
  min_num_instances: 1
  max_num_instances: 10
  cpu_utilization:
    target_utilization: 0.6

env_variables:
  ENV: production
  JAVA_OPTS: "-XX:MaxRAMPercentage=75 -XX:+ExitOnOutOfMemoryError"

readiness_check:
  path: "/health"
  check_interval_sec: 5
  timeout_sec: 4
</code></pre>
<p><strong>Companion <code>Dockerfile</code>:</strong></p>
<pre><code>FROM eclipse-temurin:21-jre-alpine
COPY app.jar /app.jar
EXPOSE 8080
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75"
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app.jar"]
</code></pre>
<p><strong>One-time GCP setup:</strong></p>
<ol>
<li><code>gcloud app create --project=$GCP_PROJECT --region=us-central</code> (App Engine is region-locked per project, forever).</li>
<li>Create a deploy SA: <code>gcloud iam service-accounts create gae-deployer</code> with roles <code>roles/appengine.deployer</code>, <code>roles/cloudbuild.builds.editor</code>, <code>roles/iam.serviceAccountUser</code>.</li>
<li>Save the SA key as Jenkins credential <code>gcp-deploy-sa</code>.</li>
</ol>
<p><strong>Variants &amp; better options for 2026:</strong></p>
<ul>
<li><strong>Cloud Run</strong> &mdash; the modern successor to App Engine Flex; same container model, faster cold starts, scale-to-zero, finer pricing. Strongly preferred for new services.</li>
<li><strong>App Engine Standard</strong> &mdash; managed JVM runtime (Java 21), no Docker; cheaper at low scale, but locked to GAE&rsquo;s sandbox.</li>
<li><strong>GKE</strong> &mdash; if you want full Kubernetes ops.</li>
<li><strong>OIDC / Workload Identity Federation</strong> on GitHub Actions removes the SA key entirely. On Jenkins you&rsquo;re typically still on stored credentials.</li>
</ul>
<p><strong>Performance:</strong> <code>min_num_instances: 1</code> avoids cold starts; <code>--stop-previous-version=false</code> keeps a rollback target around. For Scala specifically, set <code>JAVA_OPTS</code> for container-aware heap sizing; consider <strong>GraalVM native-image</strong> for &lt; 100 ms cold starts (sbt-native-packager + native-image).</p>'''

ANSWERS[65] = r'''<pre><code># Dockerfile &mdash; Next.js multi-stage with standalone output
# --- 1) Install deps separately for caching
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# --- 2) Build
FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# --- 3) Run with the standalone output (much smaller than full node_modules)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000

RUN addgroup -g 1001 -S nodejs &amp;&amp; adduser -S nextjs -u 1001
USER nextjs

# Copy ONLY what&rsquo;s needed at runtime
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/.next/static    ./.next/static
COPY --from=build --chown=nextjs:nodejs /app/public          ./public

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
</code></pre>
<p><strong>One-time prerequisite &mdash; <code>next.config.js</code>:</strong></p>
<pre><code>/** @type {import('next').NextConfig} */
module.exports = {
  output: 'standalone',          // critical &mdash; produces .next/standalone with minimal deps
  poweredByHeader: false,
  reactStrictMode: true,
  // For static export: output: 'export',  &rarr; then serve via nginx (no Node)
};
</code></pre>
<p><strong>Build &amp; run:</strong></p>
<pre><code>docker build --build-arg NEXT_PUBLIC_API_URL=https://api.acme.com \
  -t acme/web:1.0.0 .
docker run -p 3000:3000 acme/web:1.0.0
docker images acme/web   # ~150-200 MB (vs ~1 GB without standalone)
</code></pre>
<p><strong>Why this shape:</strong></p>
<ul>
<li><strong>Three stages</strong> &mdash; deps cached separately; build tools discarded; runtime is pure Node + minimal artefacts.</li>
<li><strong><code>output: 'standalone'</code></strong> &mdash; Next.js bundles only the deps the app actually imports; cuts image size by 70-80%.</li>
<li><strong>Build args for <code>NEXT_PUBLIC_*</code></strong> &mdash; these are baked into the client bundle at build time; non-public env vars stay server-side.</li>
<li><strong>Non-root user</strong> &mdash; defence-in-depth.</li>
<li><strong>Health check</strong> &mdash; orchestrators (K8s, ECS) use this for readiness; serve a lightweight <code>/api/health</code> route.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Static export</strong> &mdash; <code>output: 'export'</code> + serve <code>./out</code> from nginx/Caddy/CDN. No Node at runtime; cheapest hosting.</li>
<li><strong>App Router with RSC</strong> &mdash; same Dockerfile; just ensure the build emits server components alongside client.</li>
<li><strong>Multi-arch</strong> &mdash; <code>docker buildx build --platform linux/amd64,linux/arm64 -t acme/web:1.0.0 --push .</code>.</li>
<li><strong>Distroless runtime</strong> &mdash; <code>FROM gcr.io/distroless/nodejs20-debian12</code>; smaller, no shell.</li>
<li><strong>Yarn / pnpm</strong> &mdash; swap <code>npm ci</code> for <code>pnpm install --frozen-lockfile</code> + <code>corepack enable</code>; pnpm with hoist-friendly mode is the fastest in 2026.</li>
</ul>
<p><strong>Where to host (2026 ranking):</strong></p>
<table>
<tr><th>Host</th><th>Best for</th></tr>
<tr><td><strong>Vercel</strong></td><td>The native, zero-config home for Next.js</td></tr>
<tr><td><strong>Cloud Run</strong> / <strong>App Runner</strong></td><td>Self-hosted, auto-scales, pay-per-request</td></tr>
<tr><td><strong>Fly.io</strong> / <strong>Render</strong></td><td>Easy persistent regions</td></tr>
<tr><td><strong>K8s</strong></td><td>If you already operate K8s</td></tr>
<tr><td><strong>Cloudflare Pages</strong> + <strong>OpenNext</strong></td><td>Global edge, cheap</td></tr>
</table>
<p><strong>Performance:</strong> a <code>.dockerignore</code> with <code>node_modules .next .git .vscode .DS_Store coverage</code> dramatically cuts context size. Use Buildx GHA cache for incremental CI builds.</p>'''

ANSWERS[66] = r'''<pre><code># .github/workflows/sast.yml
name: Static Analysis
on:
  push: { branches: [main] }
  pull_request:
  schedule: [{ cron: '0 6 * * 1' }]   # Mondays 06:00 UTC for full sweep

permissions:
  contents: read
  security-events: write           # required to upload SARIF
  actions: read

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }    # Sonar / CodeQL want full history

      # 1) GitHub CodeQL &mdash; semantic analysis for many languages
      - uses: github/codeql-action/init@v3
        with: { languages: 'javascript,python' }
      - uses: github/codeql-action/analyze@v3

      # 2) Semgrep &mdash; rule-based, customisable; uploads SARIF to Code Scanning
      - uses: returntocorp/semgrep-action@v1
        with: { config: 'p/ci p/security-audit p/owasp-top-ten' }

      # 3) Trivy &mdash; filesystem + dependencies + IaC misconfig
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          format: sarif
          output: trivy.sarif
          severity: HIGH,CRITICAL
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with: { sarif_file: trivy.sarif }

      # 4) Gitleaks &mdash; secrets in code/history
      - uses: gitleaks/gitleaks-action@v2
        env: { GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} }

      # 5) SonarCloud (optional)
      - uses: SonarSource/sonarcloud-github-action@v3
        env: { SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }} }
</code></pre>
<p><strong>What each tool catches:</strong></p>
<table>
<tr><th>Tool</th><th>Specialty</th></tr>
<tr><td><strong>CodeQL</strong></td><td>Data-flow / taint analysis; finds SQLi, XSS, path traversal across function boundaries</td></tr>
<tr><td><strong>Semgrep</strong></td><td>Rule-based; very fast; custom rules for org-specific patterns</td></tr>
<tr><td><strong>Trivy fs</strong></td><td>SCA (vulnerable deps) + IaC misconfig (Dockerfiles, Terraform, K8s)</td></tr>
<tr><td><strong>Gitleaks / TruffleHog</strong></td><td>Secrets in source &amp; git history</td></tr>
<tr><td><strong>SonarCloud / SonarQube</strong></td><td>Code quality + security hotspots; nice dashboards</td></tr>
<tr><td><strong>Snyk Code</strong></td><td>Commercial SAST; broader rule set</td></tr>
<tr><td><strong>Bandit</strong> (Python), <strong>Brakeman</strong> (Rails), <strong>SpotBugs+FindSecBugs</strong> (Java), <strong>gosec</strong> (Go)</td><td>Language-specific, often catch rule violations CodeQL misses</td></tr>
</table>
<p><strong>SARIF integration &mdash; the critical bit:</strong></p>
<ul>
<li>SARIF is the standard output format for static analysis tools.</li>
<li>GitHub renders SARIF as <strong>Code Scanning alerts</strong> in the Security tab.</li>
<li>Findings appear as inline annotations on PR diffs.</li>
<li>Most major tools support SARIF output natively.</li>
</ul>
<p><strong>Performance &amp; hygiene:</strong></p>
<pre><code># Run light scans on every PR; full sweep weekly
on:
  pull_request:
    paths-ignore: ['**.md', 'docs/**']
  schedule: [{ cron: '0 6 * * 1' }]

jobs:
  light:
    if: github.event_name == 'pull_request'
    # only Trivy + Gitleaks (fast)
  full:
    if: github.event_name == 'schedule'
    # CodeQL + SonarCloud + Semgrep (slow)
</code></pre>
<p><strong>Required vs informational:</strong> mark only the <em>fastest, lowest-false-positive</em> jobs as <em>required</em> in branch protection (Trivy, Gitleaks). Treat CodeQL findings as informational at first &mdash; a noisy required check is worse than no check, because teams start ignoring them.</p>
<p><strong>Auto-remediation:</strong> use <strong>Dependabot</strong> for dependency CVEs (it opens PRs); <strong>OSSF Scorecard</strong> for repo health; <strong>OpenSSF Allstar</strong> for org-wide policy enforcement. <strong>reviewdog</strong> can convert any tool&rsquo;s output into inline PR review comments.</p>'''

ANSWERS[67] = r'''<pre><code>#!/usr/bin/env bash
# docker-cleanup.sh &mdash; reclaim disk used by Docker artefacts
set -euo pipefail

DRY_RUN=${DRY_RUN:-0}
KEEP_DAYS=${KEEP_DAYS:-7}
KEEP_TAGS=${KEEP_TAGS:-"latest stable"}

run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY-RUN: $*"
  else
    eval "$@"
  fi
}

echo "==&gt; Disk usage BEFORE"
docker system df

# 1) Stopped containers older than KEEP_DAYS
echo "==&gt; Removing stopped containers older than $KEEP_DAYS days"
STOPPED=$(docker ps -a --filter "status=exited" --filter "status=dead" --filter "status=created" \
  --format '{{.ID}} {{.CreatedAt}}' | \
  awk -v cutoff="$(date -d "$KEEP_DAYS days ago" +%s)" '
    {
      cmd = "date -d \"" $2 " " $3 " " $4 "\" +%s"
      cmd | getline created; close(cmd)
      if (created &lt; cutoff) print $1
    }')
[[ -n "$STOPPED" ]] &amp;&amp; run docker rm -f $STOPPED

# 2) Dangling (untagged) images
echo "==&gt; Removing dangling images"
run docker image prune -f

# 3) Old tagged images, keeping a few protected tags
echo "==&gt; Removing old tagged images (keeping: $KEEP_TAGS)"
PROTECT=$(echo "$KEEP_TAGS" | tr ' ' '|')
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedAt}}' | \
  grep -vE ":($PROTECT)\b" | \
  awk -v cutoff="$(date -d "$KEEP_DAYS days ago" +%s)" '
    {
      cmd = "date -d \"" $3 " " $4 " " $5 "\" +%s"
      cmd | getline created; close(cmd)
      if (created &lt; cutoff) print $2
    }' | sort -u | while read -r ID; do
  run docker rmi "$ID" || true
done

# 4) Unused volumes (anonymous volumes from removed containers)
echo "==&gt; Removing dangling volumes"
run docker volume prune -f

# 5) Unused networks (anything not referenced by a container)
echo "==&gt; Removing unused networks"
run docker network prune -f

# 6) Build cache
echo "==&gt; Pruning build cache"
run docker builder prune -af --keep-storage 5GB

# Or, the nuclear option (uncomment to use):
# echo "==&gt; Full system prune"
# run docker system prune -af --volumes

echo "==&gt; Disk usage AFTER"
docker system df
</code></pre>
<p><strong>Schedule via cron:</strong></p>
<pre><code># /etc/cron.d/docker-cleanup
0 4 * * * root /usr/local/bin/docker-cleanup.sh &gt;&gt; /var/log/docker-cleanup.log 2&gt;&amp;1
</code></pre>
<p><strong>What each prune touches:</strong></p>
<table>
<tr><th>Command</th><th>Removes</th></tr>
<tr><td><code>docker container prune</code></td><td>Stopped containers</td></tr>
<tr><td><code>docker image prune</code></td><td>Dangling images (no tag, not referenced)</td></tr>
<tr><td><code>docker image prune -a</code></td><td>All images not used by any container</td></tr>
<tr><td><code>docker volume prune</code></td><td>Volumes not mounted by any container</td></tr>
<tr><td><code>docker network prune</code></td><td>Networks not used by any container</td></tr>
<tr><td><code>docker builder prune</code></td><td>BuildKit cache</td></tr>
<tr><td><code>docker system prune --volumes -af</code></td><td>Everything not in use (nuclear)</td></tr>
</table>
<p><strong>Critical safety rules:</strong></p>
<ul>
<li><strong>Never run <code>docker volume prune</code> on hosts running databases</strong> &mdash; if the DB container isn&rsquo;t up at the moment, its volume looks unused and gets deleted.</li>
<li><strong>Use <code>--filter "until=72h"</code> instead of by-age awk</strong> for safer cutoffs:
<pre><code>docker container prune -f --filter "until=72h"
docker image prune -af --filter "until=168h"
</code></pre>
</li>
<li><strong>Tag protection</strong> &mdash; keep the production tags (<code>latest</code>, <code>stable</code>, last 5 SHAs) so a buggy deploy can roll back instantly.</li>
</ul>
<p><strong>Better options for 2026:</strong></p>
<ul>
<li><strong>Built-in disk reclamation</strong> &mdash; configure <code>daemon.json</code> with <code>"builder": { "gc": { "enabled": true, "defaultKeepStorage": "20GB" } }</code> so BuildKit garbage-collects automatically.</li>
<li><strong>K8s</strong>: kubelet&rsquo;s built-in GC handles images automatically (<code>--image-gc-high-threshold</code>); rarely need a manual script.</li>
<li><strong>Container registry retention policies</strong> &mdash; ECR / GHCR / GCR all support &ldquo;keep N most recent + tagged + young&rdquo; rules; clean up registry-side, not just locally.</li>
<li><strong>Buildx with <code>--cache-to=type=registry</code></strong> moves cache into the registry, not local disk.</li>
</ul>'''

ANSWERS[68] = r'''<pre><code># custom-resource.yaml &mdash; instance of a CRD-defined type
# Assumes the &ldquo;Backup&rdquo; CRD from the previous answer is already applied.

apiVersion: platform.acme.com/v1
kind: Backup
metadata:
  name: postgres-nightly
  namespace: prod
  labels: { app: postgres, schedule: nightly }
spec:
  source: postgres-data            # PVC name to back up
  schedule: '0 2 * * *'            # cron expression
  retentionDays: 30
  destination:
    type: s3
    bucket: acme-prod-backups
status:                            # populated by the controller; user shouldn&rsquo;t set this
  phase: Pending
  lastBackupTime: null
---
# Define multiple instances cleanly
apiVersion: platform.acme.com/v1
kind: Backup
metadata: { name: redis-hourly, namespace: prod }
spec:
  source: redis-data
  schedule: '0 * * * *'
  retentionDays: 7
  destination: { type: gcs, bucket: acme-prod-redis }
---
apiVersion: platform.acme.com/v1
kind: Backup
metadata: { name: mongo-weekly, namespace: prod }
spec:
  source: mongo-data
  schedule: '0 1 * * 0'           # Sunday 01:00
  retentionDays: 90
  destination: { type: azure-blob, bucket: acme-prod-mongo }
</code></pre>
<p><strong>Apply &amp; query:</strong></p>
<pre><code>kubectl apply -f custom-resource.yaml
kubectl get backup -n prod                # uses additionalPrinterColumns from the CRD
kubectl get bk -n prod -o wide            # short name from the CRD
kubectl describe backup postgres-nightly -n prod
kubectl get backup postgres-nightly -n prod -o yaml | yq .status
</code></pre>
<p><strong>The full picture &mdash; CRD + controller working together:</strong></p>
<ol>
<li>Cluster admin applies the <strong>CustomResourceDefinition</strong> (CRD) defining the <code>Backup</code> kind.</li>
<li>Cluster admin deploys the <strong>controller (Operator)</strong> that watches <code>Backup</code> resources.</li>
<li>Users create <code>Backup</code> resources (this YAML).</li>
<li>The controller&rsquo;s reconcile loop:
<ul>
<li>Watches the API for <code>Backup</code> events.</li>
<li>Reads <code>.spec</code> and figures out the desired state.</li>
<li>Acts on the world &mdash; for example, creates a <code>CronJob</code> running <code>pg_dump</code> + S3 upload, monitors past runs, prunes by retention.</li>
<li>Updates <code>.status</code> with progress and outcomes.</li>
</ul>
</li>
</ol>
<p><strong>Schema validation in action:</strong></p>
<pre><code># This will be REJECTED by the API server thanks to OpenAPI validation in the CRD:
spec:
  schedule: 'every 5 minutes'   # not a cron expression &mdash; regex match fails
  retentionDays: 999            # outside max=365 &mdash; rejected
  destination:
    type: ftp                   # not in enum [s3, gcs, azure-blob] &mdash; rejected
</code></pre>
<p><strong>Building the controller &mdash; tooling for 2026:</strong></p>
<table>
<tr><th>Toolkit</th><th>Language / Style</th></tr>
<tr><td><strong>Operator SDK</strong> + <strong>kubebuilder</strong></td><td>Go; controller-runtime; the de-facto standard</td></tr>
<tr><td><strong>KOPF</strong></td><td>Python; very low boilerplate; great for ops scripts</td></tr>
<tr><td><strong>Operator Framework</strong> with <strong>Helm</strong> or <strong>Ansible</strong></td><td>No-code controllers wrapping existing automations</td></tr>
<tr><td><strong>Metacontroller</strong></td><td>Compose simple webhook-driven controllers</td></tr>
<tr><td><strong>Crossplane</strong></td><td>Compose <strong>cloud resources</strong> as CRDs (the &ldquo;K8s API for everything&rdquo;)</td></tr>
</table>
<p><strong>GitOps integration:</strong> commit Custom Resources to git and let <strong>Argo CD</strong> or <strong>Flux</strong> reconcile them onto the cluster &mdash; same pattern as for native K8s resources. Operators + GitOps is the modern platform-engineering pattern.</p>
<p><strong>Performance:</strong> CRDs add a small API-server overhead per kind; design for cardinality (don&rsquo;t create one CR per ephemeral request &mdash; use a Job for that). Set <code>preserveUnknownFields: false</code> (default in <code>v1</code>) so unknown fields error early.</p>'''

ANSWERS[69] = r'''<pre><code># .github/workflows/azure-functions-go.yml
name: Deploy Go to Azure Functions
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions:
  id-token: write     # OIDC for federated auth
  contents: read

env:
  AZURE_FUNCTIONAPP_NAME: acme-go-fn
  GO_VERSION: '1.23'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '${{ env.GO_VERSION }}' }
      - run: go test -race ./...
      - run: go vet ./...

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '${{ env.GO_VERSION }}' }

      - name: Build custom handler binary
        run: |
          GOOS=linux GOARCH=amd64 CGO_ENABLED=0 \
            go build -ldflags="-s -w" -trimpath -o handler ./cmd/handler

      - name: Package artefact
        run: |
          mkdir release
          cp -r handler host.json HelloHTTP/ release/
          (cd release &amp;&amp; zip -qr ../release.zip .)

      - uses: azure/login@v2
        with:
          client-id:       ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id:       ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - uses: Azure/functions-action@v1
        with:
          app-name: ${{ env.AZURE_FUNCTIONAPP_NAME }}
          package: ./release.zip
</code></pre>
<p><strong>Function project layout (Go custom handler):</strong></p>
<pre><code># host.json &mdash; tells Functions runtime to use a custom handler
{
  "version": "2.0",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "handler",
      "workingDirectory": "",
      "arguments": []
    },
    "enableForwardingHttpRequest": true
  }
}

# HelloHTTP/function.json &mdash; the trigger binding
{
  "bindings": [
    { "type": "httpTrigger", "direction": "in",  "name": "req",
      "authLevel": "anonymous", "methods": ["get", "post"] },
    { "type": "http",        "direction": "out", "name": "res" }
  ]
}

# cmd/handler/main.go
package main
import (
  "fmt"; "log"; "net/http"; "os"
)
func main() {
  port := os.Getenv("FUNCTIONS_CUSTOMHANDLER_PORT")
  if port == "" { port = "8080" }
  http.HandleFunc("/api/HelloHTTP", func(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, `{"ok":true,"method":%q,"path":%q}`, r.Method, r.URL.Path)
  })
  log.Fatal(http.ListenAndServe(":"+port, nil))
}
</code></pre>
<p><strong>OIDC federation setup (one-time, no secrets stored):</strong></p>
<pre><code># Create an Azure App Registration + service principal
APP_ID=$(az ad app create --display-name gh-deploy-go --query appId -o tsv)
az ad sp create --id $APP_ID

# Federated credential trusting your GitHub repo &amp; branch
az ad app federated-credential create --id $APP_ID --parameters '{
  "name":"main",
  "issuer":"https://token.actions.githubusercontent.com",
  "subject":"repo:acme/api:ref:refs/heads/main",
  "audiences":["api://AzureADTokenExchange"]
}'

# Grant the SP contributor on the function&rsquo;s resource group
az role assignment create --role contributor \
  --assignee $APP_ID --scope /subscriptions/SUB/resourceGroups/prod-rg
</code></pre>
<p>In GitHub: store <code>AZURE_CLIENT_ID</code>, <code>AZURE_TENANT_ID</code>, <code>AZURE_SUBSCRIPTION_ID</code> as <em>variables</em> (not secrets &mdash; OIDC means no client secret).</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Container deploy</strong> &mdash; build a Docker image and configure the Function App to pull it; cleaner for non-trivial Go binaries.</li>
<li><strong>Premium / Dedicated plan</strong> &mdash; for warm starts &amp; VNet integration; Consumption plan has cold starts.</li>
<li><strong>Azure Container Apps</strong> &mdash; for non-bursty Go services, often a better fit than Functions.</li>
<li><strong>Function URL via Cloud Run / Lambda Function URL</strong> &mdash; if you&rsquo;re multi-cloud, evaluate before locking in.</li>
</ul>
<p><strong>Performance:</strong> static Go binaries cold-start in &lt; 200 ms even on Consumption; <code>-ldflags="-s -w" -trimpath</code> shrinks the binary; pre-load runtime via <strong>Always Ready Instances</strong> on Premium for sub-50ms responses. For event-heavy workloads, prefer Azure Container Apps + KEDA over Functions in 2026.</p>'''

ANSWERS[70] = r'''<pre><code>// Jenkinsfile &mdash; React Native: build &amp; ship to App Store + Play
pipeline {
  agent { label 'macos' }                 // iOS builds REQUIRE a Mac
  options { timeout(time: 60, unit: 'MINUTES') }
  parameters {
    choice(name: 'TRACK', choices: ['internal', 'beta', 'production'],
           description: 'Play Store track / TestFlight or App Store')
  }
  environment {
    LANG = 'en_US.UTF-8'
    FASTLANE_SKIP_UPDATE_CHECK = '1'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('JS deps') {
      steps {
        sh &apos;&apos;&apos;
          corepack enable
          yarn install --frozen-lockfile
          yarn lint
          yarn test --ci --coverage
        &apos;&apos;&apos;
      }
    }

    stage('iOS pod install') {
      steps {
        sh 'cd ios &amp;&amp; pod install --repo-update'
      }
    }

    stage('Build &amp; ship') {
      parallel {
        stage('iOS &rarr; TestFlight / App Store') {
          when { branch 'main' }
          steps {
            withCredentials([
              file(credentialsId: 'app-store-key',     variable: 'APP_STORE_KEY'),
              string(credentialsId: 'fastlane-keychain-pw', variable: 'KP'),
            ]) {
              sh &apos;&apos;&apos;
                cd ios
                bundle install --quiet
                bundle exec fastlane match appstore --readonly
                bundle exec fastlane build_release
                if [ "$TRACK" = "production" ]; then
                  bundle exec fastlane release
                else
                  bundle exec fastlane beta
                fi
              &apos;&apos;&apos;
            }
          }
        }

        stage('Android &rarr; Play Store') {
          when { branch 'main' }
          agent { label 'linux &amp;&amp; jdk21' }    // Android can build on any node
          steps {
            withCredentials([
              file(credentialsId: 'play-service-account', variable: 'PLAY_JSON'),
              file(credentialsId: 'android-keystore',     variable: 'KEYSTORE'),
              string(credentialsId: 'keystore-pw',        variable: 'KS_PW'),
            ]) {
              sh &apos;&apos;&apos;
                cd android
                cp $KEYSTORE app/release.keystore
                ./gradlew bundleRelease \
                  -Pandroid.injected.signing.store.file=app/release.keystore \
                  -Pandroid.injected.signing.store.password=$KS_PW \
                  -Pandroid.injected.signing.key.alias=upload \
                  -Pandroid.injected.signing.key.password=$KS_PW

                bundle install --quiet
                bundle exec fastlane supply --aab app/build/outputs/bundle/release/app-release.aab \
                  --track $TRACK --json-key $PLAY_JSON
              &apos;&apos;&apos;
            }
          }
        }
      }
    }
  }
  post {
    success { slackSend channel: '#mobile', message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} (${params.TRACK})" }
    failure { slackSend channel: '#mobile', message: "❌ ${env.JOB_NAME}" }
  }
}
</code></pre>
<p><strong>Fastlane lanes (<code>ios/fastlane/Fastfile</code>):</strong></p>
<pre><code>default_platform(:ios)
platform :ios do
  desc 'Build a signed release IPA'
  lane :build_release do
    setup_ci
    match(type: 'appstore', readonly: true)
    increment_build_number(xcodeproj: 'AcmeApp.xcodeproj')
    build_app(scheme: 'AcmeApp', export_method: 'app-store')
  end

  desc 'Upload to TestFlight'
  lane :beta do
    upload_to_testflight(skip_waiting_for_build_processing: true)
  end

  desc 'Submit to App Store'
  lane :release do
    upload_to_app_store(submit_for_review: true,
                        automatic_release: true,
                        force: true)
  end
end
</code></pre>
<p><strong>Why this complexity is unavoidable:</strong></p>
<ul>
<li><strong>iOS builds need macOS</strong> &mdash; Apple licensing; can&rsquo;t legally use Hackintosh; cloud Mac runners (GitHub macOS, MacStadium, AWS EC2 Mac) are the way.</li>
<li><strong>Code signing</strong> &mdash; <strong>fastlane match</strong> stores certs/profiles encrypted in a private git repo; eliminates &ldquo;works on my Mac&rdquo;.</li>
<li><strong>Two distinct build chains</strong> &mdash; iOS (Xcode + CocoaPods + fastlane) and Android (Gradle + AAB + Play Console API); parallel them.</li>
<li><strong>Tracks</strong> &mdash; iOS: TestFlight (internal/external) &rarr; App Store; Android: internal &rarr; alpha &rarr; beta &rarr; production.</li>
</ul>
<p><strong>2026 best practices:</strong></p>
<ul>
<li><strong>EAS Build</strong> (Expo) &mdash; managed cloud builds for both platforms; eliminates the macOS runner problem entirely.</li>
<li><strong>Codemagic</strong>, <strong>Bitrise</strong>, <strong>App Center</strong> &mdash; mobile-specialised CI; pre-baked Mac runners and signing flows.</li>
<li><strong>GitHub Actions <code>macos-15</code></strong> &mdash; works for moderate-volume teams; expensive for heavy use.</li>
<li><strong>Detox</strong> / <strong>Maestro</strong> &mdash; E2E testing on real devices.</li>
<li><strong>Sentry / Crashlytics</strong> &mdash; auto-upload dSYMs on every build for symbolicated stack traces.</li>
</ul>
<p><strong>Performance:</strong> cache <code>~/.gradle</code>, <code>node_modules</code>, and Pods between builds; iOS build time goes from 12&rarr;3 minutes. Use <strong>Hermes</strong> for the Android JS engine and <strong>R8</strong> with <code>shrinkResources</code> for smaller APKs.</p>'''

ANSWERS[71] = r'''<pre><code># docker-compose.yml &mdash; Redis 7 with persistence + RedisInsight UI
services:
  redis:
    image: redis:7.4-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "127.0.0.1:6379:6379"   # bind to localhost only
    command:
      - redis-server
      - --appendonly
      - "yes"
      - --requirepass
      - "${REDIS_PASSWORD:-devpass}"
      - --maxmemory
      - "256mb"
      - --maxmemory-policy
      - "allkeys-lru"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-devpass}", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  insight:
    image: redis/redisinsight:latest   # web UI on http://localhost:5540
    container_name: redisinsight
    ports: ["127.0.0.1:5540:5540"]
    depends_on: { redis: { condition: service_healthy } }

volumes:
  redis_data:
</code></pre>
<p><strong>Run:</strong> <code>docker compose up -d</code>, connect with <code>redis-cli -h 127.0.0.1 -a devpass</code> or visit RedisInsight at <code>http://localhost:5540</code>. <code>--appendonly yes</code> turns on AOF persistence so data survives restarts; <code>maxmemory + allkeys-lru</code> caps memory and evicts LRU keys, mirroring how managed Redis (ElastiCache, Upstash, Redis Cloud) behaves under pressure.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Redis Stack</strong> (<code>redis/redis-stack:latest</code>) bundles RedisJSON, RediSearch, TimeSeries, Bloom &mdash; one image for full feature set with the Insight UI on <code>:8001</code>.</li>
<li><strong>Cluster mode</strong> &mdash; use <code>grokzen/redis-cluster</code> or compose 6 nodes with <code>cluster-enabled yes</code> for testing sharded clients.</li>
<li><strong>Sentinel HA</strong> &mdash; <code>bitnami/redis-sentinel</code> chart for failover testing.</li>
<li><strong>TLS</strong> &mdash; mount certs and add <code>--tls-port 6380 --port 0 --tls-cert-file ... --tls-key-file ... --tls-ca-cert-file ...</code> to match production setups.</li>
</ul>
<p><strong>2026 ops notes:</strong> for production, prefer managed (Upstash for serverless / per-request billing, ElastiCache + MemoryDB for AWS-native, Redis Cloud for multi-AZ). Compose Redis is for local dev and integration tests &mdash; pair it with <strong>Testcontainers</strong> (<code>GenericContainer("redis:7.4-alpine")</code>) so each test run gets an isolated instance without polluting the shared dev container.</p>
'''

ANSWERS[72] = r'''<pre><code># .github/workflows/amplify-deploy.yml
# Deploys a TypeScript (Vite/Next/CRA) app to AWS Amplify Hosting via the Amplify CLI / API.
name: Deploy to AWS Amplify
on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  id-token: write   # OIDC to AWS &mdash; no long-lived keys
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      APP_ID: ${{ secrets.AMPLIFY_APP_ID }}
      BRANCH: main
      AWS_REGION: us-east-1
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }

      - name: Install + typecheck + build
        run: |
          npm ci
          npm run typecheck
          npm test -- --run
          npm run build           # produces ./dist (Vite) or ./.next (Next)

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Zip artefact &amp; upload to Amplify
        run: |
          cd dist &amp;&amp; zip -rq ../build.zip . &amp;&amp; cd ..
          UPLOAD=$(aws amplify create-deployment \
            --app-id "$APP_ID" --branch-name "$BRANCH" --query 'zipUploadUrl' --output text)
          JOB_ID=$(aws amplify create-deployment \
            --app-id "$APP_ID" --branch-name "$BRANCH" --query 'jobId' --output text)
          curl -s -H "Content-Type: application/zip" --upload-file build.zip "$UPLOAD"
          aws amplify start-deployment \
            --app-id "$APP_ID" --branch-name "$BRANCH" --job-id "$JOB_ID"
</code></pre>
<p><strong>How it works:</strong> Amplify Hosting accepts pre-built artefacts via a signed S3 URL. <code>create-deployment</code> returns an upload URL + job ID; you PUT the zip and call <code>start-deployment</code>. AWS handles CDN invalidation, TLS, and atomic switch-over.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Amplify Git-connected app</strong> &mdash; let Amplify watch the repo directly (no Action needed); <code>amplify.yml</code> in repo root defines build steps. Less control but simpler. Most teams pick this for monorepos with multiple branches/PR previews.</li>
<li><strong>Amplify Gen 2 (TypeScript-first backend)</strong> &mdash; replaces the legacy CLI; define <code>amplify/backend.ts</code>, deploy with <code>npx ampx pipeline-deploy --branch main --app-id $APP_ID</code>.</li>
<li><strong>S3 + CloudFront</strong> &mdash; <code>aws s3 sync dist/ s3://bucket --delete &amp;&amp; aws cloudfront create-invalidation --distribution-id $CF --paths '/*'</code>. Cheaper and simpler if you don&rsquo;t need Amplify&rsquo;s auth/data features.</li>
<li><strong>SST / OpenNext</strong> &mdash; for Next.js with full SSR/ISR on Lambda+CloudFront, more control than Amplify.</li>
</ul>
<p><strong>2026 advice:</strong> if the app is purely static, S3+CloudFront beats Amplify on price/control. If you want preview URLs per PR, Amplify Gen 2 / Vercel / Cloudflare Pages / Netlify are all easier than rolling it yourself.</p>
'''

ANSWERS[73] = r'''<pre><code>// Jenkinsfile &mdash; Haskell (Stack) build &amp; deploy
pipeline {
  agent { docker { image 'haskell:9.8'; args '-v /root/.stack:/root/.stack' } }
  options { timestamps(); timeout(time: 30, unit: 'MINUTES') }
  environment {
    APP   = 'my-haskell-app'
    IMAGE = "ghcr.io/acme/${APP}"
  }
  stages {
    stage('Resolve deps') {
      steps { sh 'stack setup &amp;&amp; stack build --only-dependencies' }
    }
    stage('Test') {
      steps { sh 'stack test --coverage --ta "--xml=test-results.xml"' }
      post  { always { junit allowEmptyResults: true, testResults: 'test-results.xml' } }
    }
    stage('Lint') {
      steps {
        sh 'stack install hlint &amp;&amp; hlint src --report=hlint.html || true'
        sh 'fourmolu --mode check src app'
      }
    }
    stage('Build static binary') {
      steps {
        // Static linking with musl &mdash; tiny, distroless-friendly
        sh &apos;&apos;&apos;
          stack build --copy-bins --local-bin-path ./bin \\
            --ghc-options="-static -optl-static -optl-pthread"
        &apos;&apos;&apos;
      }
    }
    stage('Docker image') {
      steps {
        sh """
          cat &gt; Dockerfile.deploy &lt;&lt;'EOF'
FROM gcr.io/distroless/static-debian12:nonroot
COPY bin/${APP} /app
EXPOSE 8080
ENTRYPOINT ["/app"]
EOF
          docker build -t ${IMAGE}:${GIT_COMMIT.take(7)} -f Dockerfile.deploy .
          docker tag  ${IMAGE}:${GIT_COMMIT.take(7)} ${IMAGE}:latest
        """
      }
    }
    stage('Push &amp; deploy') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr',
                          usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo "$P" | docker login ghcr.io -u "$U" --password-stdin'
        }
        sh "docker push ${IMAGE}:${GIT_COMMIT.take(7)} &amp;&amp; docker push ${IMAGE}:latest"
        sh "kubectl set image deploy/${APP} app=${IMAGE}:${GIT_COMMIT.take(7)} -n prod"
        sh "kubectl rollout status deploy/${APP} -n prod --timeout=5m"
      }
    }
  }
  post { always { archiveArtifacts artifacts: 'bin/**, hlint.html', allowEmptyArchive: true } }
}
</code></pre>
<p><strong>Why these choices:</strong> Haskell&rsquo;s GHC compiles to a fat native binary, so a multi-stage build (Stack image &rarr; distroless) yields ~20-30 MB images instead of 3 GB. <code>-static -optl-static</code> produces a fully static binary that runs in <code>distroless/static</code> with no glibc dependency. <code>hlint</code> + <code>fourmolu</code> cover style/lint; <code>--coverage</code> + <code>--ta</code> emit JUnit XML for Jenkins.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Cabal + Nix</strong> &mdash; <code>cabal build</code> inside a <code>nixpkgs.haskellPackages</code> shell for fully reproducible builds (preferred at large Haskell shops like Mercury, Tweag).</li>
<li><strong>GitHub Actions</strong> &mdash; <code>haskell-actions/setup@v2</code> + <code>cache: stack-work</code>. Faster start than spinning up Jenkins agents.</li>
<li><strong>Lambda</strong> &mdash; build with the Lambda Runtime Interface; ship as a container image since Haskell is not a native runtime.</li>
</ul>
<p><strong>2026 notes:</strong> use <strong>GHC 9.8+</strong> (modern record dot syntax, OrPatterns), <strong>Stackage LTS-22+</strong>, and prefer GitHub Actions over Jenkins unless you already run Jenkins for the rest of the org. Cache <code>~/.stack</code> aggressively &mdash; cold Stack builds can take 30+ minutes.</p>
'''

ANSWERS[74] = r'''<pre><code># priorityclass.yaml &mdash; tier hierarchy for a multi-tenant cluster
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: tier-critical
value: 1000000           # higher = more important; range 0..1e9 for user classes
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "Tier-1 services that must never be evicted (auth, payments, control plane)"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: tier-standard
value: 100000
globalDefault: true      # any pod without priorityClassName gets this
preemptionPolicy: PreemptLowerPriority
description: "Default tier for production workloads"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: tier-batch
value: 1000
preemptionPolicy: Never  # batch never preempts &mdash; just waits
description: "Best-effort jobs (analytics, reindex). May be evicted any time."
---
# Usage on a Pod / Deployment template:
apiVersion: v1
kind: Pod
metadata: { name: payments }
spec:
  priorityClassName: tier-critical
  containers: [{ name: app, image: ghcr.io/acme/payments:1.4.0 }]
</code></pre>
<p><strong>How it works:</strong> the scheduler computes pod priority by name lookup. When the cluster is full, a <em>higher-priority pending pod</em> can preempt running pods of lower priority on a node it would otherwise fit on &mdash; the lower pod is gracefully terminated and rescheduled. <code>preemptionPolicy: Never</code> opts out of that behaviour for batch (waits in the queue instead of bumping others).</p>
<p><strong>Reserved system classes:</strong> <code>system-cluster-critical</code> (2,000,000,000) and <code>system-node-critical</code> (2,000,001,000) are pre-installed for kube-system components &mdash; do <em>not</em> use them for user workloads.</p>
<p><strong>Pairs well with:</strong></p>
<ul>
<li><strong>PodDisruptionBudgets</strong> &mdash; preemption respects PDBs, so a tier-1 pod can&rsquo;t be evicted past your minimum-available threshold.</li>
<li><strong>ResourceQuota with <code>scopeSelector</code></strong> &mdash; cap how much CPU/memory each priority tier can consume per namespace.</li>
<li><strong>Karpenter / Cluster Autoscaler</strong> &mdash; both honour priority when deciding which pending pods to provision capacity for.</li>
</ul>
<p><strong>2026 advice:</strong> keep the number of priority classes small (3-5 max). Many teams over-engineer this with 10+ tiers and then nothing ever gets preempted because the math doesn&rsquo;t favour it. A simple <em>critical / standard / batch</em> split covers 90% of real needs. For GPU/spot workloads, look at <strong>Kueue</strong> for queue-based scheduling rather than relying on raw priority.</p>
'''

ANSWERS[75] = r'''<pre><code># Dockerfile &mdash; SvelteKit (Node adapter) production image
# ---------- Stage 1: build ----------
FROM node:20-alpine AS build
WORKDIR /app

# Better caching: copy manifests first
COPY package.json package-lock.json* pnpm-lock.yaml* ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --no-audit --no-fund

COPY . .
RUN npm run build              # produces ./build (with @sveltejs/adapter-node)
RUN npm prune --omit=dev       # drop devDependencies for the runtime stage

# ---------- Stage 2: runtime ----------
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000 \
    BODY_SIZE_LIMIT=2M

# Non-root + tini for proper signal handling
RUN apk add --no-cache tini &amp;&amp; \
    addgroup -S app &amp;&amp; adduser -S -G app app
USER app

COPY --chown=app:app --from=build /app/build      ./build
COPY --chown=app:app --from=build /app/node_modules ./node_modules
COPY --chown=app:app --from=build /app/package.json ./

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD wget -qO- http://127.0.0.1:3000/healthz || exit 1
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "build/index.js"]
</code></pre>
<p><strong>Why these choices:</strong> SvelteKit&rsquo;s <code>adapter-node</code> outputs a self-contained Node server; the multi-stage build leaves only <code>build/</code> + production <code>node_modules</code> in the final image (~80 MB). <code>npm prune --omit=dev</code> drops dev deps. <code>tini</code> reaps zombies and forwards <code>SIGTERM</code> so K8s rolling restarts are clean. The healthcheck hits a <code>/healthz</code> endpoint you add as a hook.</p>
<p><strong>Variants by adapter:</strong></p>
<ul>
<li><strong>adapter-static</strong> (pre-rendered SPA) &mdash; final stage is just <code>nginx:alpine</code> serving <code>build/</code>; ~25 MB.</li>
<li><strong>adapter-vercel / adapter-cloudflare / adapter-netlify</strong> &mdash; deploy directly to those platforms, no Dockerfile needed.</li>
<li><strong>adapter-bun</strong> &mdash; swap final stage to <code>oven/bun:1-alpine</code>, faster cold start.</li>
</ul>
<p><strong>build.sh:</strong> <code>docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/acme/svelte-app:1.0.0 --push .</code></p>
<p><strong>2026 polish:</strong> add <code>--mount=type=cache,target=/app/.svelte-kit</code> to cache the build output between runs in CI; pin Node to a digest for supply-chain hardening (<code>FROM node:20-alpine@sha256:&hellip;</code>); generate an SBOM with <code>syft</code> and sign with <code>cosign sign --yes</code>. For SSR-heavy apps consider <strong>distroless/nodejs20-debian12:nonroot</strong> for the runtime &mdash; ~50 MB and no shell, smaller attack surface.</p>
'''

ANSWERS[76] = r'''<pre><code># .github/workflows/cloud-run-kotlin.yml
name: Deploy Kotlin to Cloud Run
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions: { id-token: write, contents: read }   # OIDC =&gt; Workload Identity

env:
  PROJECT: acme-prod
  REGION:  us-central1
  SERVICE: kotlin-api
  REPO:    acme-images          # Artifact Registry repo
  IMAGE:   us-central1-docker.pkg.dev/acme-prod/acme-images/kotlin-api

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '21', cache: gradle }

      - name: Test &amp; build native image with Spring Boot
        run: |
          ./gradlew --no-daemon test
          ./gradlew --no-daemon bootBuildImage \
            --imageName=${{ env.IMAGE }}:${{ github.sha }} \
            -Pversion=${{ github.sha }}

      # OIDC -&gt; GCP via Workload Identity Federation (no JSON keys!)
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: deployer@acme-prod.iam.gserviceaccount.com

      - uses: google-github-actions/setup-gcloud@v2

      - name: Push image
        run: |
          gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
          docker push ${{ env.IMAGE }}:${{ github.sha }}

      - name: Deploy
        run: |
          gcloud run deploy ${{ env.SERVICE }} \
            --image=${{ env.IMAGE }}:${{ github.sha }} \
            --region=${{ env.REGION }} \
            --project=${{ env.PROJECT }} \
            --execution-environment=gen2 \
            --cpu=2 --memory=1Gi --min-instances=0 --max-instances=20 \
            --concurrency=80 --timeout=60s \
            --set-secrets=DB_PASSWORD=db-pass:latest \
            --set-env-vars=ENV=prod \
            --allow-unauthenticated --quiet
</code></pre>
<p><strong>How it works:</strong> Spring Boot&rsquo;s <code>bootBuildImage</code> uses Cloud Native Buildpacks to produce an OCI image with no Dockerfile. WIF lets the workflow assume a GCP service account through OIDC, no JSON key in secrets. Cloud Run gen2 gives full Linux compat + faster cold starts; <code>--min-instances=0</code> means scale-to-zero (pay only for active requests).</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Native image (GraalVM)</strong> &mdash; <code>./gradlew nativeCompile</code>, then <code>docker build</code> with a tiny base. Cold start drops from ~2 s to ~50 ms but build time goes from 1 min to 10+ min. Worth it for sporadic traffic.</li>
<li><strong>Ktor</strong> instead of Spring &mdash; smaller, faster, no <code>bootBuildImage</code>; write a manual multi-stage Dockerfile.</li>
<li><strong>Cloud Build trigger</strong> &mdash; let GCP build/push instead of GitHub runners (<code>gcloud builds submit</code>); useful if you don&rsquo;t want to ship images out of the GCP perimeter.</li>
</ul>
<p><strong>2026 ops notes:</strong> always use <strong>WIF</strong> over JSON keys (which are deprecated for new projects in many orgs). Pair with <strong>Cloud Run jobs</strong> for migrations and <strong>Cloud Run sidecars</strong> for OTel collectors. Use <code>--service-account</code> with least-privilege roles, not the default Compute SA. Set <code>min-instances=1</code> only on latency-sensitive endpoints &mdash; otherwise you&rsquo;re paying for idle.</p>
'''

ANSWERS[77] = r'''<pre><code>#!/usr/bin/env bash
# pod-watchdog.sh &mdash; monitor &amp; restart unhealthy pods
# Usage: pod-watchdog.sh &lt;namespace&gt; [restart_threshold] [age_minutes]
# Example: pod-watchdog.sh prod 5 30
set -euo pipefail

NS="${1:-default}"
THRESH="${2:-5}"          # restart count threshold
AGE_MIN="${3:-15}"        # only act on pods older than this (avoid races)
SLACK="${SLACK_WEBHOOK_URL:-}"
DRY="${DRY_RUN:-false}"

now_epoch=$(date +%s)
notified=()

notify() {
  local msg="$1"
  echo "[$(date -Iseconds)] $msg"
  [[ -n "$SLACK" ]] &amp;&amp; curl -sS -X POST -H 'Content-type: application/json' \
       --data "{\"text\":\":fire: pod-watchdog: ${msg//\"/\\\"}\"}" "$SLACK" &gt;/dev/null || true
}

# Pull pods as JSON; jq does the filtering so we make exactly one API call.
kubectl get pods -n "$NS" -o json | jq -c '.items[]' | while read -r pod; do
  name=$(jq -r '.metadata.name'           &lt;&lt;&lt;"$pod")
  phase=$(jq -r '.status.phase'           &lt;&lt;&lt;"$pod")
  start=$(jq -r '.status.startTime // ""' &lt;&lt;&lt;"$pod")
  [[ -z "$start" ]] &amp;&amp; continue
  age_s=$(( now_epoch - $(date -d "$start" +%s) ))
  (( age_s &lt; AGE_MIN*60 )) &amp;&amp; continue           # too young, skip

  # 1) high restart count
  restarts=$(jq '[.status.containerStatuses[]?.restartCount] | add // 0' &lt;&lt;&lt;"$pod")
  reason=""
  if (( restarts &gt;= THRESH )); then
    reason="restart count ${restarts} &ge; ${THRESH}"
  fi

  # 2) stuck in CrashLoopBackOff / ImagePullBackOff / ErrImagePull
  bad=$(jq -r '[.status.containerStatuses[]?.state.waiting.reason // empty]
                | map(select(. == "CrashLoopBackOff" or . == "ImagePullBackOff" or . == "ErrImagePull"))
                | first // ""' &lt;&lt;&lt;"$pod")
  [[ -n "$bad" ]] &amp;&amp; reason="${reason:+$reason; }waiting: $bad"

  # 3) Running but not Ready for &gt; AGE_MIN minutes
  if [[ "$phase" == "Running" ]]; then
    ready=$(jq -r '.status.conditions[]? | select(.type=="Ready") | .status' &lt;&lt;&lt;"$pod")
    [[ "$ready" != "True" ]] &amp;&amp; reason="${reason:+$reason; }Running but NotReady"
  fi

  if [[ -n "$reason" ]]; then
    notify "$NS/$name &mdash; $reason &mdash; deleting (controller will respawn)"
    if [[ "$DRY" != "true" ]]; then
      kubectl delete pod -n "$NS" "$name" --grace-period=30 --wait=false
    fi
  fi
done
</code></pre>
<p><strong>How it works:</strong> one <code>kubectl get</code>, then <code>jq</code> evaluates three failure signals: high restart count, stuck waiting state, and Running-but-NotReady. Deleting the pod lets its controlling Deployment / StatefulSet / DaemonSet recreate it. <code>DRY_RUN=true</code> previews actions; Slack notifications go out unconditionally.</p>
<p><strong>Schedule it:</strong></p>
<pre><code>apiVersion: batch/v1
kind: CronJob
metadata: { name: pod-watchdog, namespace: kube-system }
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: pod-watchdog   # RBAC: pods get/list/delete
          restartPolicy: OnFailure
          containers:
          - name: watchdog
            image: ghcr.io/acme/pod-watchdog:1.0
            args: ["prod", "5", "30"]
            envFrom: [{ secretRef: { name: slack-webhook } }]
</code></pre>
<p><strong>2026 advice:</strong> in most cases this is a smell &mdash; if pods CrashLoop, fix probes / OOM limits / config rather than reaping. Use it as a safety net, not a feature. Better tools: <strong>Karpenter consolidation</strong> for capacity issues, <strong>kured</strong> for node reboots, <strong>kube-monkey / chaos-mesh</strong> for chaos testing, and <strong>Kured / Robusta</strong> for proper alerting and self-healing playbooks. For Argo CD users, <strong>Argo Rollouts</strong> auto-rollbacks on metric regressions which is far better than blind pod-reaping.</p>
'''

ANSWERS[78] = r'''<pre><code>// Jenkinsfile &mdash; Elixir/Phoenix to Heroku via container registry
pipeline {
  agent { docker { image 'hexpm/elixir:1.17.3-erlang-27.1-alpine-3.20' } }
  options { timestamps(); timeout(time: 25, unit: 'MINUTES') }
  environment {
    APP        = 'acme-phoenix'
    MIX_ENV    = 'prod'
    HEROKU_API_KEY = credentials('heroku-api-key')   // Heroku auth token
    REGISTRY   = "registry.heroku.com/${APP}/web"
  }
  stages {
    stage('Deps &amp; compile') {
      steps {
        sh 'mix local.hex --force &amp;&amp; mix local.rebar --force'
        sh 'mix deps.get --only $MIX_ENV'
        sh 'MIX_ENV=test mix deps.compile'
      }
    }
    stage('Test') {
      steps {
        sh 'MIX_ENV=test mix test --cover'
        sh 'mix format --check-formatted'
        sh 'mix credo --strict'
        sh 'mix dialyzer || true'             // warn-only; PLT cache lives in workspace
      }
    }
    stage('Build release') {
      steps {
        sh &apos;&apos;&apos;
          MIX_ENV=prod mix deps.compile
          MIX_ENV=prod mix assets.deploy      # esbuild + tailwind digesting
          MIX_ENV=prod mix release
        &apos;&apos;&apos;
      }
    }
    stage('Containerize &amp; push to Heroku registry') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          docker build -t $REGISTRY -f Dockerfile.heroku .
          echo "$HEROKU_API_KEY" | docker login --username=_ --password-stdin registry.heroku.com
          docker push $REGISTRY
        &apos;&apos;&apos;
      }
    }
    stage('Release on Heroku') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          IMAGE_ID=$(docker inspect $REGISTRY --format='{{.Id}}')
          curl -fsSL -X PATCH https://api.heroku.com/apps/$APP/formation \\
            -H "Authorization: Bearer $HEROKU_API_KEY" \\
            -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \\
            -H "Content-Type: application/json" \\
            -d "{\"updates\":[{\"type\":\"web\",\"docker_image\":\"$IMAGE_ID\"}]}"
        &apos;&apos;&apos;
      }
    }
    stage('Smoke + migrate') {
      when { branch 'main' }
      steps {
        sh 'curl -fsSL --retry 10 --retry-delay 6 https://${APP}.herokuapp.com/healthz'
        sh 'heroku run --exit-code "bin/${APP} eval \\"AcmeApp.Release.migrate\\"" -a $APP'
      }
    }
  }
  post { failure { slackSend(channel: '#ops', message: ":x: Phoenix deploy failed: ${env.BUILD_URL}") } }
}
</code></pre>
<p><strong>Companion Dockerfile.heroku:</strong></p>
<pre><code>FROM hexpm/elixir:1.17.3-erlang-27.1-alpine-3.20 AS build
ENV MIX_ENV=prod
WORKDIR /app
COPY mix.* ./
RUN mix local.hex --force &amp;&amp; mix local.rebar --force &amp;&amp; mix deps.get --only prod
COPY config ./config
RUN mix deps.compile
COPY priv priv
COPY assets assets
COPY lib lib
RUN mix assets.deploy &amp;&amp; mix release

FROM alpine:3.20
RUN apk add --no-cache openssl ncurses-libs libstdc++ tini &amp;&amp; \
    addgroup -S app &amp;&amp; adduser -S -G app app
WORKDIR /app
COPY --from=build --chown=app:app /app/_build/prod/rel/acme_phoenix ./
USER app
EXPOSE 4000
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["bin/acme_phoenix", "start"]
</code></pre>
<p><strong>Why these choices:</strong> Heroku&rsquo;s container registry is the cleanest path for Elixir &mdash; the buildpack works but is slow and fragile around OTP/asset pipelines. <code>mix release</code> produces a self-contained ERTS bundle. The post-deploy <code>heroku run</code> runs Ecto migrations safely after the new image is live (runs on a one-off dyno).</p>
<p><strong>2026 advice:</strong> consider <strong>Fly.io</strong> as a near drop-in for Phoenix &mdash; it has first-class clustering support (libcluster + DNSCluster), better LiveView latency thanks to edge regions, and is generally cheaper than Heroku at scale. <code>fly deploy</code> replaces the entire registry/release dance. <strong>Render</strong> and <strong>Gigalixir</strong> are also strong Phoenix-friendly options.</p>
'''

ANSWERS[79] = r'''<pre><code># quota-and-limits.yaml &mdash; namespace-scoped resource governance
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-alpha-quota
  namespace: team-alpha
spec:
  hard:
    # Compute
    requests.cpu:    "20"
    requests.memory: "40Gi"
    limits.cpu:      "40"
    limits.memory:   "80Gi"
    # Object counts
    pods:                            "100"
    services:                         "20"
    services.loadbalancers:            "2"
    persistentvolumeclaims:           "30"
    requests.storage:               "500Gi"
    count/deployments.apps:           "30"
    count/jobs.batch:                 "50"
    # Storage class quotas (per StorageClass)
    gp3.storageclass.storage.k8s.io/requests.storage:    "300Gi"
    gp3.storageclass.storage.k8s.io/persistentvolumeclaims: "20"
---
# Optional: scope a quota to specific PriorityClass / QoS / scope
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-alpha-batch-quota
  namespace: team-alpha
spec:
  hard:
    requests.cpu:    "10"
    requests.memory: "20Gi"
    pods:            "50"
  scopeSelector:
    matchExpressions:
      - operator: In
        scopeName: PriorityClass
        values: ["tier-batch"]
---
# Companion LimitRange &mdash; default requests/limits for pods that don't specify them
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: team-alpha }
spec:
  limits:
    - type: Container
      default:        { cpu: "500m", memory: "512Mi" }
      defaultRequest: { cpu: "100m", memory: "128Mi" }
      max:            { cpu: "4",    memory: "8Gi"   }
      min:            { cpu: "10m",  memory: "16Mi"  }
</code></pre>
<p><strong>How it works:</strong> ResourceQuota caps the <em>sum</em> of requested + limit values plus object counts in a namespace. Critically: <em>once a quota for compute exists, every pod in the namespace must declare requests/limits or admission fails</em>. That&rsquo;s why a LimitRange usually rides alongside &mdash; it injects defaults so devs don&rsquo;t have to remember.</p>
<p><strong>Verify:</strong></p>
<pre><code>kubectl get resourcequota -n team-alpha
kubectl describe resourcequota team-alpha-quota -n team-alpha   # shows used / hard
</code></pre>
<p><strong>scopeSelector tricks:</strong></p>
<ul>
<li><code>BestEffort</code> / <code>NotBestEffort</code> &mdash; quota only applies to pods without resource requests (or those with).</li>
<li><code>Terminating</code> / <code>NotTerminating</code> &mdash; restrict by activeDeadlineSeconds set vs unset.</li>
<li><code>PriorityClass</code> &mdash; per-tier quotas (so tier-batch can&rsquo;t starve tier-critical capacity).</li>
<li><code>CrossNamespacePodAffinity</code> &mdash; cap usage of cross-namespace topology constraints (1.24+).</li>
</ul>
<p><strong>2026 advice:</strong> pair ResourceQuota with <strong>VerticalPodAutoscaler</strong> (recommendation mode) so devs get suggested requests, and <strong>kube-resource-report / Goldilocks</strong> dashboards to spot under/over-provisioned namespaces. For multi-tenant cost allocation, <strong>OpenCost</strong> reads quota usage and produces per-team chargeback. If you&rsquo;re running shared GPU clusters, <strong>Kueue</strong> sits above ResourceQuota and gives proper queue-based fairness rather than first-come-first-serve.</p>
'''

ANSWERS[80] = r'''<pre><code># docker-compose.yml &mdash; RabbitMQ 4 with management UI, definitions, healthcheck
services:
  rabbitmq:
    image: rabbitmq:4.0-management-alpine
    container_name: rabbitmq
    hostname: rabbit-1                  # keep stable so Mnesia data survives restart
    restart: unless-stopped
    ports:
      - "127.0.0.1:5672:5672"           # AMQP
      - "127.0.0.1:15672:15672"         # management UI / HTTP API
      - "127.0.0.1:15692:15692"         # Prometheus metrics endpoint
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER:-admin}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASS:-devpass}
      RABBITMQ_DEFAULT_VHOST: /
      # Quorum queues by default (1 leader + N followers, Raft-replicated)
      RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS: "-rabbit default_queue_type quorum"
    volumes:
      - rabbit_data:/var/lib/rabbitmq
      - ./rabbit/definitions.json:/etc/rabbitmq/definitions.json:ro
      - ./rabbit/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
    healthcheck:
      test: ["CMD-SHELL", "rabbitmq-diagnostics -q check_running &amp;&amp; rabbitmq-diagnostics -q check_local_alarms"]
      interval: 15s
      timeout: 10s
      retries: 6
      start_period: 30s

volumes:
  rabbit_data:
</code></pre>
<p><strong>Companion <code>./rabbit/rabbitmq.conf</code>:</strong></p>
<pre><code>management.load_definitions = /etc/rabbitmq/definitions.json
prometheus.tcp.port = 15692
loopback_users = none
disk_free_limit.relative = 1.5
</code></pre>
<p><strong>Companion <code>./rabbit/definitions.json</code> (declarative seed):</strong></p>
<pre><code>{
  "users":[{"name":"app","password":"app","tags":""}],
  "vhosts":[{"name":"/"}],
  "permissions":[{"user":"app","vhost":"/","configure":".*","write":".*","read":".*"}],
  "queues":[{"name":"orders","vhost":"/","durable":true,"arguments":{"x-queue-type":"quorum"}}],
  "exchanges":[{"name":"orders.tx","vhost":"/","type":"topic","durable":true}],
  "bindings":[{"source":"orders.tx","vhost":"/","destination":"orders","destination_type":"queue","routing_key":"order.*"}]
}
</code></pre>
<p><strong>How it works:</strong> the <code>:management</code> tag pulls in the web UI on <code>:15672</code> (login admin / devpass) and exposes the HTTP API. The Prometheus plugin (built-in since 3.8) is enabled by adding the port. <code>definitions.json</code> auto-creates users, queues, exchanges and bindings on first boot &mdash; idempotent and version-controllable. Quorum queues replace classic mirrored queues (deprecated in 3.x, removed in 4.0).</p>
<p><strong>Scaling locally:</strong> for a 3-node test cluster, copy the service three times with shared <code>RABBITMQ_ERLANG_COOKIE</code>, <code>cluster_formation.peer_discovery_backend = classic_config</code> and <code>cluster_formation.classic_config.nodes.1 = rabbit@rabbit-1</code> etc. Easier alternative: the <strong>Bitnami RabbitMQ Cluster Helm chart</strong>.</p>
<p><strong>2026 advice:</strong> for greenfield event systems consider <strong>NATS JetStream</strong> (lighter, faster, simpler ops), <strong>Apache Kafka / Redpanda</strong> (log-based, replayable streams), or managed (<strong>CloudAMQP</strong> for hosted RabbitMQ, <strong>AWS MQ for RabbitMQ</strong>). RabbitMQ still shines for classic work-queue patterns with low latency and rich routing semantics &mdash; just use <strong>quorum queues</strong> and <strong>streams</strong> (the new log-style queue type), not the legacy classic/mirrored ones.</p>
'''

ANSWERS[81] = r'''<pre><code># .github/workflows/cpp-ec2.yml &mdash; build C++ binary &amp; deploy to AWS EC2
name: Deploy C++ to EC2
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions: { id-token: write, contents: read }

env:
  AWS_REGION: us-east-1
  ARTEFACT_BUCKET: acme-deploys
  APP_NAME: acme-cpp-svc
  CD_APP_NAME: acme-cpp-svc          # CodeDeploy application
  CD_DG: acme-cpp-svc-prod           # CodeDeploy deployment group

jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }

      - name: Cache vcpkg
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/vcpkg
            build/vcpkg_installed
          key: vcpkg-${{ runner.os }}-${{ hashFiles('vcpkg.json') }}

      - name: Install toolchain
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends \
            build-essential cmake ninja-build clang-18 clang-tidy-18 lld-18 ccache pkg-config

      - name: Configure (Release, ASan/UBSan-free, LTO)
        run: |
          cmake -S . -B build -G Ninja \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_C_COMPILER=clang-18 -DCMAKE_CXX_COMPILER=clang++-18 \
            -DCMAKE_EXE_LINKER_FLAGS="-fuse-ld=lld" \
            -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
            -DCMAKE_TOOLCHAIN_FILE="$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake"

      - name: Build &amp; test
        run: |
          cmake --build build --parallel
          ctest --test-dir build --output-on-failure --parallel

      - name: Package CodeDeploy bundle
        run: |
          mkdir -p bundle/bin
          cp build/${{ env.APP_NAME }} bundle/bin/
          cp -r deploy/{appspec.yml,scripts} bundle/
          tar -czf app.tgz -C bundle .

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Upload + start CodeDeploy
        run: |
          KEY="${{ env.APP_NAME }}/${{ github.sha }}.tgz"
          aws s3 cp app.tgz s3://${{ env.ARTEFACT_BUCKET }}/$KEY
          aws deploy create-deployment \
            --application-name ${{ env.CD_APP_NAME }} \
            --deployment-group-name ${{ env.CD_DG }} \
            --deployment-config-name CodeDeployDefault.OneAtATime \
            --s3-location bucket=${{ env.ARTEFACT_BUCKET }},key=$KEY,bundleType=tgz \
            --description "Commit ${{ github.sha }}"
</code></pre>
<p><strong>deploy/appspec.yml:</strong></p>
<pre><code>version: 0.0
os: linux
files:
  - source: bin/acme-cpp-svc
    destination: /opt/acme/bin
permissions:
  - object: /opt/acme/bin/acme-cpp-svc
    mode:   "0755"
    owner:  acme
    group:  acme
hooks:
  ApplicationStop:  [{ location: scripts/stop.sh,    timeout: 30, runas: root }]
  AfterInstall:     [{ location: scripts/configure.sh, timeout: 30, runas: root }]
  ApplicationStart: [{ location: scripts/start.sh,   timeout: 30, runas: root }]
  ValidateService:  [{ location: scripts/health.sh,  timeout: 60, runas: acme }]
</code></pre>
<p><strong>How it works:</strong> CodeDeploy on EC2 pulls the bundle from S3, runs the lifecycle hooks on each instance, and respects the deployment config (<em>OneAtATime / HalfAtATime / AllAtOnce / Canary10Percent5Minutes</em>). With an AutoScaling group, new instances re-run the latest deployment automatically. <code>vcpkg</code> + cache cuts cold builds from ~10 min to ~30 s; <code>clang+lld+LTO</code> produces a leaner binary with full link-time optimisation.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Containerise</strong> &mdash; build in CI, push to ECR, run as a SystemD-managed Docker service or use <strong>ECS / Fargate</strong> instead. Simpler for libstdc++ ABI mismatches across distros.</li>
<li><strong>Blue/green via CodeDeploy</strong> &mdash; spins up a fresh ASG, shifts ELB traffic, rolls back on healthcheck failure.</li>
<li><strong>SSM RunCommand</strong> &mdash; if you don&rsquo;t need lifecycle hooks, push the binary and run a one-shot SSM document.</li>
</ul>
<p><strong>2026 advice:</strong> <strong>raw EC2 + CodeDeploy is becoming legacy</strong> &mdash; for new C++ services consider <strong>ECS Fargate</strong> (no AMI baking, no SSH, scale-to-zero), or <strong>Karpenter on EKS</strong> if you have a polyglot fleet. Keep CodeDeploy for stateful single-tenant workloads where AMI immutability matters. Add <strong>Cosign-signed artefacts</strong> + <strong>SLSA provenance</strong> to harden the supply chain.</p>
'''

ANSWERS[82] = r'''<pre><code># mutating-webhook.yaml &mdash; inject a sidecar &amp; default labels into pods
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: sidecar-injector
webhooks:
  - name: sidecar-injector.acme.io
    admissionReviewVersions: ["v1"]
    sideEffects: None                    # pure JSON Patch, no external mutation
    timeoutSeconds: 5
    failurePolicy: Fail                  # Ignore is the lenient option
    reinvocationPolicy: IfNeeded         # re-run if other webhooks mutate after us
    matchPolicy: Equivalent
    namespaceSelector:                   # only target opted-in namespaces
      matchLabels:
        sidecar-injection: enabled
    objectSelector:                      # skip pods that already opt out
      matchExpressions:
        - { key: "sidecar.acme.io/skip", operator: NotIn, values: ["true"] }
    rules:
      - operations: ["CREATE"]
        apiGroups:   [""]
        apiVersions: ["v1"]
        resources:   ["pods"]
        scope:       "Namespaced"
    clientConfig:
      service:
        namespace: kube-system
        name: sidecar-injector-svc
        path: /mutate
        port: 443
      caBundle: |                        # base64 PEM &mdash; usually injected by cert-manager
        LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t...
</code></pre>
<p><strong>Server-side: minimal Go handler returning a JSON Patch:</strong></p>
<pre><code>// /mutate &mdash; receives AdmissionReview, returns AdmissionReview with patch
func mutate(w http.ResponseWriter, r *http.Request) {
    var review admissionv1.AdmissionReview
    _ = json.NewDecoder(r.Body).Decode(&amp;review)
    pod := &amp;corev1.Pod{}
    _ = json.Unmarshal(review.Request.Object.Raw, pod)

    patch := []map[string]any{
        {"op":"add","path":"/metadata/labels/injected-by","value":"sidecar-injector"},
        {"op":"add","path":"/spec/containers/-","value": map[string]any{
            "name": "envoy", "image": "envoyproxy/envoy:v1.32-latest",
            "ports": []map[string]any{{"containerPort": 15001}},
        }},
    }
    pb, _ := json.Marshal(patch)
    pt := admissionv1.PatchTypeJSONPatch
    review.Response = &amp;admissionv1.AdmissionResponse{
        UID: review.Request.UID, Allowed: true, Patch: pb, PatchType: &amp;pt,
    }
    json.NewEncoder(w).Encode(review)
}
</code></pre>
<p><strong>How it works:</strong> the API server calls your webhook over TLS during admission of every matching object. You return either an <code>AdmissionResponse</code> with <code>Allowed: false</code> (deny) or a <em>JSON Patch</em> the API server applies before persistence. Common uses: sidecar injection (Istio, Linkerd, Vault Agent), default tolerations, image rewriting, secret injection.</p>
<p><strong>Operational essentials:</strong></p>
<ul>
<li><strong>cert-manager + caInjector</strong> &mdash; auto-injects <code>caBundle</code> from a <code>Certificate</code>, no manual rotation.</li>
<li><strong><code>failurePolicy</code></strong> &mdash; <code>Fail</code> blocks pod creation if the webhook is down (safest for security webhooks); <code>Ignore</code> for opt-in features so a webhook outage doesn&rsquo;t stop deploys.</li>
<li><strong>HA</strong> &mdash; run at least 2 replicas of the webhook deployment with a PodDisruptionBudget; otherwise a node drain breaks the cluster.</li>
<li><strong>Exclude kube-system</strong> &mdash; never mutate cluster-critical components (use <code>namespaceSelector.matchExpressions</code> with <code>NotIn</code>).</li>
</ul>
<p><strong>2026 alternatives:</strong> for most policy/mutation needs, prefer <strong>Kyverno</strong> or <strong>OPA Gatekeeper</strong> &mdash; they declare mutations in YAML/Rego, generate the webhook config for you, and ship with audit/dry-run, exemptions, and policy reports. Roll your own webhook only for highly custom logic (e.g.&nbsp;bespoke sidecar injection).</p>
'''

ANSWERS[83] = r'''<pre><code>// Jenkinsfile &mdash; Rust to AWS Lambda (zip + AWS SAM optional)
pipeline {
  agent any
  options { timestamps(); timeout(time: 20, unit: 'MINUTES') }
  environment {
    AWS_REGION = 'us-east-1'
    FN_NAME    = 'rust-fn-prod'
    BUCKET     = 'acme-lambda-deploys'
    RUST_TARGET = 'aarch64-unknown-linux-musl'   // arm64 Graviton2 = ~20% cheaper
  }
  stages {
    stage('Toolchain') {
      steps {
        sh &apos;&apos;&apos;
          which cargo-lambda || (
            curl --proto =https --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.83
            cargo install --locked cargo-lambda
          )
          rustup target add ${RUST_TARGET}
        &apos;&apos;&apos;
      }
    }
    stage('Test &amp; lint') {
      steps {
        sh 'cargo fmt --all -- --check'
        sh 'cargo clippy --all-targets -- -D warnings'
        sh 'cargo test --all'
      }
    }
    stage('Build Lambda zip') {
      steps {
        // cargo-lambda cross-compiles via Zig + produces ./target/lambda/&lt;fn&gt;/bootstrap.zip
        sh 'cargo lambda build --release --arm64 --output-format zip'
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-deploy']]) {
          sh &apos;&apos;&apos;
            ZIP=target/lambda/${FN_NAME}/bootstrap.zip
            KEY=${FN_NAME}/${BUILD_NUMBER}-$(git rev-parse --short HEAD).zip
            aws s3 cp $ZIP s3://$BUCKET/$KEY

            # Update or create the function
            if aws lambda get-function --function-name ${FN_NAME} &gt;/dev/null 2&gt;&amp;1; then
              aws lambda update-function-code \\
                --function-name ${FN_NAME} \\
                --s3-bucket $BUCKET --s3-key $KEY \\
                --publish
              aws lambda wait function-updated --function-name ${FN_NAME}
            else
              aws lambda create-function \\
                --function-name ${FN_NAME} \\
                --runtime provided.al2023 \\
                --architectures arm64 \\
                --handler bootstrap \\
                --role arn:aws:iam::123456789012:role/lambda-rust-exec \\
                --code S3Bucket=$BUCKET,S3Key=$KEY \\
                --memory-size 256 --timeout 15 \\
                --environment "Variables={RUST_LOG=info}" \\
                --tracing-config Mode=Active \\
                --publish
            fi

            # Promote alias 'live' to the new version (atomic, supports rollback)
            VER=$(aws lambda publish-version --function-name ${FN_NAME} --query Version --output text)
            aws lambda update-alias --function-name ${FN_NAME} --name live --function-version $VER
          &apos;&apos;&apos;
        }
      }
    }
  }
  post {
    success { sh 'aws lambda invoke --function-name ${FN_NAME}:live --payload \'{"ping":true}\' /tmp/out.json &amp;&amp; cat /tmp/out.json' }
  }
}
</code></pre>
<p><strong>Why these choices:</strong> Rust cold starts on Lambda are already fast (~30-50 ms) but <strong>arm64 (Graviton)</strong> drops both latency and cost ~20%. <code>cargo-lambda</code> wraps cross-compilation, ABI compatibility, and Zig as the linker so you don&rsquo;t need a Linux build host. The <code>provided.al2023</code> runtime is the modern OS-only base (replaces deprecated <code>provided.al2</code> in late 2025). Aliases (<code>live</code>) give you blue/green flips and easy rollback (<code>--function-version $PREVIOUS</code>).</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>SAM</strong>: <code>sam build --beta-features &amp;&amp; sam deploy --no-confirm-changeset</code> &mdash; declarative IaC alongside the function.</li>
<li><strong>CDK</strong>: <code>RustFunction</code> construct from <code>aws-lambda-rust-runtime</code>; integrates with the rest of your CDK stack.</li>
<li><strong>Container image Lambda</strong>: <code>FROM public.ecr.aws/lambda/provided:al2023.arm64</code> with a <code>bootstrap</code> binary; required if your function exceeds the 250 MB unzipped limit.</li>
<li><strong>Lambda Function URLs / API Gateway / ALB</strong> &mdash; pick the trigger; FunctionURLs are simplest for public HTTPS endpoints.</li>
</ul>
<p><strong>2026 polish:</strong> add <strong>X-Ray tracing</strong> + <strong>Lambda Powertools for Rust</strong> for structured logs/metrics, gate the alias flip behind <strong>CodeDeploy <em>LambdaCanary10Percent5Minutes</em></strong> for safe rollouts, and pin the runtime to a specific provided runtime version (e.g.&nbsp;<code>provided.al2023</code>). Sign artefacts with <strong>AWS Signer</strong> + verify in the function&rsquo;s code-signing config to harden supply chain.</p>
'''

ANSWERS[84] = r'''<pre><code># Dockerfile &mdash; Phoenix (Elixir 1.17 / OTP 27) production image
ARG ELIXIR_VERSION=1.17.3
ARG OTP_VERSION=27.1
ARG ALPINE_VERSION=3.20

# ---------- Stage 1: build ----------
FROM hexpm/elixir:${ELIXIR_VERSION}-erlang-${OTP_VERSION}-alpine-${ALPINE_VERSION} AS build
ENV MIX_ENV=prod LANG=C.UTF-8
RUN apk add --no-cache build-base git nodejs npm
WORKDIR /app

# Copy manifests first for caching
COPY mix.exs mix.lock ./
COPY config config
RUN mix local.hex --force &amp;&amp; mix local.rebar --force &amp;&amp; \
    mix deps.get --only $MIX_ENV &amp;&amp; \
    mix deps.compile

# Source &amp; assets
COPY priv priv
COPY assets assets
COPY lib lib

# Build esbuild + tailwind, digest static, generate release
RUN mix assets.deploy &amp;&amp; \
    mix release

# ---------- Stage 2: runtime ----------
FROM alpine:${ALPINE_VERSION} AS runtime
RUN apk add --no-cache openssl ncurses-libs libstdc++ libgcc tini ca-certificates &amp;&amp; \
    addgroup -S app &amp;&amp; adduser -S -G app app
ENV LANG=C.UTF-8 \
    HOME=/app \
    PHX_SERVER=true \
    PORT=4000

WORKDIR /app
COPY --from=build --chown=app:app /app/_build/prod/rel/acme_app ./
USER app

EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s \
  CMD wget -qO- http://127.0.0.1:4000/healthz || exit 1
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["bin/acme_app", "start"]
</code></pre>
<p><strong>Required runtime config &mdash; <code>config/runtime.exs</code>:</strong></p>
<pre><code># Reads SECRET_KEY_BASE, DATABASE_URL, PHX_HOST etc. at boot
import Config
if config_env() == :prod do
  config :acme_app, AcmeAppWeb.Endpoint,
    http: [ip: {0, 0, 0, 0, 0, 0, 0, 0}, port: String.to_integer(System.get_env("PORT", "4000"))],
    server: true,
    secret_key_base: System.fetch_env!("SECRET_KEY_BASE")
  config :acme_app, AcmeApp.Repo,
    url: System.fetch_env!("DATABASE_URL"),
    pool_size: String.to_integer(System.get_env("POOL_SIZE", "10"))
end
</code></pre>
<p><strong>Why these choices:</strong> Phoenix releases (<code>mix release</code>) bundle ERTS so the runtime image needs only OpenSSL + ncurses (no Erlang install). <code>mix assets.deploy</code> runs esbuild + Tailwind in <code>--minify</code> mode and digests <code>priv/static</code>. <code>tini</code> reaps zombies and forwards signals so K8s rolling updates terminate cleanly (Phoenix&rsquo;s <code>Phoenix.Endpoint</code> handles <code>SIGTERM</code> gracefully when wired up). Final image: ~70 MB.</p>
<p><strong>Migrations:</strong> add a <code>release.ex</code> with <code>AcmeApp.Release.migrate/0</code> using <code>Ecto.Migrator</code>; run as a one-shot <code>bin/acme_app eval "AcmeApp.Release.migrate"</code> in a Kubernetes Job / Fly release_command / Heroku release phase before the new pods receive traffic.</p>
<p><strong>2026 polish:</strong></p>
<ul>
<li><strong>Distroless</strong> alternative: <code>FROM gcr.io/distroless/cc-debian12:nonroot</code> &mdash; smaller (~50 MB), no shell. Requires copying ERTS shared libs explicitly.</li>
<li><strong>libcluster + DNSCluster</strong> for multi-node Phoenix on Fly/Render/EKS &mdash; LiveView channels and PubSub work across nodes.</li>
<li><strong>OpenTelemetry</strong> via <code>opentelemetry_phoenix</code> + <code>opentelemetry_ecto</code>; ship to Honeycomb, Datadog, or any OTel collector.</li>
<li><strong>Fly.io</strong> remains the easiest host for Phoenix &mdash; <code>fly launch</code> generates this Dockerfile and a <code>fly.toml</code> with healthchecks pre-configured.</li>
</ul>
'''

ANSWERS[85] = r'''<pre><code># .github/workflows/perf.yml &mdash; performance regression gate
name: Performance Tests
on:
  pull_request:
    paths-ignore: ['docs/**', '*.md']
  workflow_dispatch:
    inputs:
      target_url:
        description: "URL to load-test (default: PR preview)"
        required: false

permissions: { pull-requests: write, contents: read, checks: write }

jobs:
  k6:
    name: API load test (k6)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Boot stack with Docker Compose
        run: docker compose -f docker-compose.test.yml up -d --wait

      - name: Run k6 with thresholds
        uses: grafana/setup-k6-action@v1
      - run: |
          k6 run --quiet --summary-export=k6-summary.json tests/load.js

      - name: Compare against baseline (fail on regression)
        run: node tests/perf-diff.js k6-summary.json baselines/k6-main.json

      - name: Tear down
        if: always()
        run: docker compose -f docker-compose.test.yml down -v

  lighthouse:
    name: Frontend (Lighthouse CI)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci &amp;&amp; npm run build
      - name: Run Lighthouse CI against the build
        run: |
          npm install -g @lhci/cli@0.14.x
          lhci autorun \
            --config=./.lighthouserc.json \
            --upload.target=temporary-public-storage
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
</code></pre>
<p><strong>Companion <code>tests/load.js</code> (k6):</strong></p>
<pre><code>import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = {
  scenarios: {
    smoke:   { executor: 'constant-vus', vus: 5,  duration: '30s' },
    rampup:  { executor: 'ramping-vus', startVUs: 0, startTime: '30s',
               stages: [{duration:'2m',target:50},{duration:'3m',target:50},{duration:'1m',target:0}] },
  },
  thresholds: {
    http_req_failed:   ['rate&lt;0.01'],          // &lt; 1 % errors
    http_req_duration: ['p(95)&lt;300', 'p(99)&lt;800'],
    'http_req_duration{group:::checkout}': ['p(95)&lt;500'],
  },
};
export default function () {
  const r = http.get(`${__ENV.TARGET_URL}/api/products`);
  check(r, { 'status 200': (x) =&gt; x.status === 200 });
  sleep(1);
}
</code></pre>
<p><strong>Companion <code>.lighthouserc.json</code>:</strong></p>
<pre><code>{
  "ci": {
    "collect": { "url": ["http://localhost:3000/", "http://localhost:3000/products"], "numberOfRuns": 3 },
    "assert":  { "preset": "lighthouse:recommended",
                 "assertions": {
                   "categories:performance":   ["error", { "minScore": 0.85 }],
                   "first-contentful-paint":   ["warn",  { "maxNumericValue": 1800 }],
                   "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
                   "total-blocking-time":      ["error", { "maxNumericValue": 200 }],
                   "cumulative-layout-shift":  ["error", { "maxNumericValue": 0.1 }]
                 } }
  }
}
</code></pre>
<p><strong>How it works:</strong> two parallel jobs &mdash; <strong>k6</strong> for API load (smoke + ramp), failing on threshold breaches via <code>thresholds</code>; <strong>Lighthouse CI</strong> for frontend Core Web Vitals against budgets you set per route. Both jobs comment results back on the PR via the GitHub App tokens. The <code>perf-diff.js</code> script compares the new summary against a <code>baselines/k6-main.json</code> committed from the main branch and fails if p95 regresses by &gt; X %.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Distributed k6</strong> &mdash; <code>k6 cloud run</code> or self-hosted <code>k6-operator</code> on K8s for &gt; 50k VUs.</li>
<li><strong>Artillery</strong> / <strong>Gatling</strong> / <strong>Locust</strong> &mdash; if your team already invested.</li>
<li><strong>Apache Bench / hey / wrk</strong> &mdash; one-off smoke tests in PRs.</li>
<li><strong>WebPageTest API</strong> &mdash; richer real-device measurements than Lighthouse for frontend.</li>
</ul>
<p><strong>2026 advice:</strong> run perf tests <em>only on labelled PRs</em> (<code>if: contains(github.event.pull_request.labels.*.name, 'perf')</code>) &mdash; they&rsquo;re slow and noisy; gating every PR creates a culture of bypassing the check. Keep an always-on nightly run that posts to a dashboard (Grafana + Prometheus or k6 Cloud). Compare results in <em>relative</em> terms (% delta vs the parent commit baseline), not absolute numbers, because GitHub runner perf varies by ~20%.</p>
'''

ANSWERS[86] = r'''<pre><code>#!/usr/bin/env bash
# kops-bootstrap.sh &mdash; create a production-ready K8s cluster on AWS with kops
# Usage: NAME=foo.k8s.local ZONES=us-east-1a,us-east-1b,us-east-1c ./kops-bootstrap.sh
set -euo pipefail

: "${NAME:?cluster name required, e.g. cluster.example.com}"
: "${ZONES:?comma-separated AZ list required, e.g. us-east-1a,us-east-1b,us-east-1c}"
: "${KOPS_STATE_STORE:?S3 URL required, e.g. s3://acme-kops-state}"
REGION="${REGION:-${ZONES%%,*}}"; REGION="${REGION%[a-z]}"   # strip AZ letter
K8S_VERSION="${K8S_VERSION:-1.31.2}"
NETWORKING="${NETWORKING:-cilium}"           # ebpf, no kube-proxy
NODE_TYPE="${NODE_TYPE:-m6i.large}"
NODE_COUNT="${NODE_COUNT:-3}"
CONTROL_TYPE="${CONTROL_TYPE:-m6i.large}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519.pub}"

echo "==&gt; Pre-flight: tools"
for bin in kops kubectl aws helm; do
  command -v "$bin" &gt;/dev/null || { echo "missing $bin"; exit 1; }
done
aws sts get-caller-identity &gt;/dev/null     # require valid AWS creds

echo "==&gt; Pre-flight: state store bucket"
BUCKET="${KOPS_STATE_STORE#s3://}"
aws s3api head-bucket --bucket "$BUCKET" 2&gt;/dev/null || \
  aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
    $( [[ "$REGION" != "us-east-1" ]] &amp;&amp; echo --create-bucket-configuration LocationConstraint=$REGION )
aws s3api put-bucket-versioning      --bucket "$BUCKET" --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption      --bucket "$BUCKET" \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws s3api put-public-access-block    --bucket "$BUCKET" \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo "==&gt; Generating cluster spec"
kops create cluster \
  --name="$NAME" \
  --cloud=aws \
  --zones="$ZONES" \
  --master-zones="$ZONES" \
  --kubernetes-version="$K8S_VERSION" \
  --networking="$NETWORKING" \
  --node-count="$NODE_COUNT" \
  --node-size="$NODE_TYPE" \
  --control-plane-count=3 \
  --control-plane-size="$CONTROL_TYPE" \
  --topology=private \
  --bastion \
  --api-loadbalancer-type=internal \
  --ssh-public-key="$SSH_KEY" \
  --discovery-store="s3://${BUCKET}/${NAME}/discovery" \
  --dns=private \
  --yes=false      # preview only; we&rsquo;ll review then apply

echo "==&gt; Editing cluster: enable etcd encryption + audit + IRSA"
kops edit cluster "$NAME" --set 'spec.encryptionConfig=true' \
                          --set 'spec.fileAssets[0].name=audit-policy' \
                          --set 'spec.fileAssets[0].path=/etc/kubernetes/audit/policy.yaml' \
                          --set 'spec.kubeAPIServer.auditPolicyFile=/etc/kubernetes/audit/policy.yaml'

echo "==&gt; Apply cluster (creates VPC, ASGs, ELB, Route53)"
kops update cluster "$NAME" --yes --admin
kops validate cluster --wait 15m

echo "==&gt; Post-install add-ons"
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/metrics-server/master/manifests/release/components.yaml
helm repo add eks https://aws.github.io/eks-charts &amp;&amp; helm repo update
helm upgrade --install aws-lb-controller eks/aws-load-balancer-controller \
  -n kube-system --set clusterName="$NAME" --set serviceAccount.create=true

echo "==&gt; Done. kubectl context: $(kubectl config current-context)"
</code></pre>
<p><strong>Why these choices:</strong> private topology + internal API LB + bastion = no public control-plane exposure. <code>--networking=cilium</code> uses eBPF, replaces kube-proxy, and unlocks NetworkPolicy + Hubble observability. 3 control-plane nodes across 3 AZs gives etcd quorum that survives an AZ outage. Versioned + encrypted S3 state lets you roll back malformed cluster spec edits.</p>
<p><strong>Day-2 ops:</strong></p>
<ul>
<li><code>kops rolling-update cluster --yes</code> &mdash; in-place upgrades node images / control plane.</li>
<li><code>kops edit ig nodes</code> &mdash; tune instance type, mixedInstancesPolicy (spot+on-demand), maxSize.</li>
<li><code>kops delete cluster $NAME --yes</code> &mdash; teardown including S3 state.</li>
</ul>
<p><strong>2026 advice:</strong> <strong>kops is rarely the right answer for new clusters in 2026.</strong> Pick one of:</p>
<ul>
<li><strong>EKS + Karpenter</strong> &mdash; managed control plane, autoscaling on demand. Use <code>eksctl</code> or <strong>Terraform terraform-aws-modules/eks</strong>.</li>
<li><strong>Cluster API (CAPI / CAPA)</strong> &mdash; declarative, GitOps-friendly K8s-managing-K8s.</li>
<li><strong>k3s / Talos Linux / kubeadm</strong> &mdash; for self-hosted needs. Talos in particular is popular for production self-managed clusters.</li>
</ul>
<p>Use kops only if you need self-managed control plane on AWS without going to CAPI, or are maintaining an existing kops fleet.</p>
'''

ANSWERS[87] = r'''<pre><code># vpa.yaml &mdash; right-size pod requests automatically
# Prereqs: install Vertical Pod Autoscaler operator (autoscaler/vertical-pod-autoscaler)
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-vpa
  namespace: prod
spec:
  targetRef:                          # what we right-size
    apiVersion: apps/v1
    kind: Deployment
    name: api
  updatePolicy:
    # Off       = recommendations only (use with HPA on CPU)
    # Initial   = set on pod creation, never update
    # Recreate  = evict + recreate when off-target (legacy)
    # Auto      = same as Recreate today; in-place resize lands behind a feature gate (1.27+ alpha, 1.33 GA-track)
    updateMode: "Auto"
    minReplicas: 2                    # don&rsquo;t evict if it&rsquo;d drop us below this
  resourcePolicy:
    containerPolicies:
      - containerName: '*'            # apply to all containers in the pod
        controlledResources: ["cpu", "memory"]
        controlledValues: RequestsAndLimits
        minAllowed:
          cpu: "100m"
          memory: "128Mi"
        maxAllowed:
          cpu: "4"
          memory: "8Gi"
      - containerName: 'istio-proxy'  # don&rsquo;t touch sidecars
        mode: "Off"
---
# Recommendation-only mode: pair safely with HPA
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata: { name: worker-vpa-rec, namespace: prod }
spec:
  targetRef: { apiVersion: apps/v1, kind: Deployment, name: worker }
  updatePolicy: { updateMode: "Off" }   # write recommendations to status only
</code></pre>
<p><strong>How it works:</strong> three VPA components run in <code>kube-system</code>: <em>recommender</em> (reads metrics-server / Prometheus and computes a target), <em>updater</em> (evicts pods whose actual usage drifts from the target), and <em>admission-controller</em> (mutates the pod spec at creation to inject the recommended requests/limits). <code>kubectl describe vpa api-vpa</code> shows the current recommendation under <code>status.recommendation</code>.</p>
<p><strong>Modes &mdash; what to use when:</strong></p>
<ul>
<li><strong>Off</strong> &mdash; recommendation only. Safe baseline, doesn&rsquo;t fight with HPA on CPU. Read with <code>kubectl get vpa -o yaml</code>.</li>
<li><strong>Initial</strong> &mdash; set requests at pod creation time, never modify. Good for batch jobs.</li>
<li><strong>Recreate / Auto</strong> &mdash; evicts pods to apply new sizing. Pairs <em>only</em> with <strong>memory-based</strong> HPA scaling, never CPU (otherwise they fight).</li>
</ul>
<p><strong>HPA + VPA together &mdash; the rule:</strong> never both control the same resource. Common safe pattern: <strong>VPA for memory, HPA for CPU</strong>, or <strong>VPA off-mode + HPA on custom metrics</strong> (RPS, queue depth).</p>
<p><strong>2026 alternatives:</strong></p>
<ul>
<li><strong>In-place pod resize</strong> (<code>resourcePolicy.resizePolicy</code>) &mdash; GA-track in 1.33; lets VPA adjust without eviction. Game-changer when stable.</li>
<li><strong>Goldilocks</strong> &mdash; UI dashboard built on top of VPA recommender; great for finding mis-sized workloads.</li>
<li><strong>KEDA</strong> &mdash; for event-driven scale; pairs with VPA off-mode for the right-sizing piece.</li>
<li><strong>Karpenter</strong> &mdash; complementary; VPA right-sizes pods, Karpenter right-sizes nodes.</li>
<li><strong>Datadog / Robusta KRR</strong> &mdash; historical, multi-week recommendation engines that often beat the in-cluster recommender.</li>
</ul>
'''

ANSWERS[88] = r'''<pre><code># .github/workflows/azure-app-service-java.yml
name: Deploy Java to Azure App Service
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions: { id-token: write, contents: read }   # OIDC =&gt; Azure (no client secret)

env:
  APP_NAME: acme-java-prod
  PLAN_RG:  acme-rg
  JAR:      target/acme-app.jar

jobs:
  build:
    runs-on: ubuntu-latest
    outputs: { artefact: ${{ steps.upload.outputs.artifact-name }} }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '21', cache: maven }

      - name: Test &amp; build
        run: |
          mvn -B -ntp verify
          mvn -B -ntp -DskipTests package
          ls -la target/

      - id: upload
        uses: actions/upload-artifact@v4
        with:
          name: app-jar
          path: ${{ env.JAR }}
          retention-days: 7

  staging-deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://${{ env.APP_NAME }}-staging.azurewebsites.net
    steps:
      - uses: actions/download-artifact@v4
        with: { name: app-jar }

      - uses: azure/login@v2
        with:
          client-id:       ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id:       ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Deploy to staging slot
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.APP_NAME }}
          slot-name: staging
          package: acme-app.jar

      - name: Smoke test staging
        run: |
          for i in 1 2 3 4 5; do
            curl -fsSL https://${{ env.APP_NAME }}-staging.azurewebsites.net/actuator/health &amp;&amp; break
            sleep 6
          done

  production-swap:
    needs: staging-deploy
    runs-on: ubuntu-latest
    environment:                            # GitHub Environment with required reviewers
      name: production
      url: https://${{ env.APP_NAME }}.azurewebsites.net
    steps:
      - uses: azure/login@v2
        with:
          client-id:       ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id:       ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Swap staging &harr; production (warm, zero-downtime)
        run: |
          az webapp deployment slot swap \
            -g ${{ env.PLAN_RG }} -n ${{ env.APP_NAME }} \
            --slot staging --target-slot production
</code></pre>
<p><strong>Why these choices:</strong> three jobs &mdash; build once, deploy to a <em>staging slot</em>, then <em>swap</em> into production. App Service slots are warm-up + atomic-swap with virtually zero downtime. The <code>environment: production</code> requires manual approval via GitHub Environments; you can also wire branch protection + WIF subject claims so only PRs from <code>main</code> can request the federated token.</p>
<p><strong>App Service Java specifics:</strong></p>
<ul>
<li>Set <strong>Java SE</strong> stack on the plan (<code>az webapp config set --java-version 21</code>); App Service runs the jar with <code>java -jar</code>. For embedded Tomcat / WAR, choose the Tomcat stack instead.</li>
<li>Configure <code>JAVA_OPTS</code> &mdash; e.g. <code>-XX:+UseG1GC -XX:MaxRAMPercentage=75</code> to scale heap with the SKU.</li>
<li>Spring Boot Actuator <code>/actuator/health</code> works as the health-check endpoint; configure under App Service &rarr; <em>Health Check</em>.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Container deploy</strong> &mdash; build a Distroless JRE image, push to ACR, deploy <code>azure/webapps-deploy@v3</code> with <code>type: image</code>. Same slots/swap mechanics.</li>
<li><strong>Azure Container Apps</strong> &mdash; for microservices / Dapr / KEDA-driven scale; better than App Service for event-driven workloads.</li>
<li><strong>AKS + ArgoCD</strong> &mdash; if you&rsquo;ve outgrown PaaS deployments.</li>
</ul>
<p><strong>2026 advice:</strong> always use <strong>OIDC</strong> for <code>azure/login</code> (no <code>creds:</code> with a JSON service principal). Pair slot swap with <strong>auto-swap rules</strong> only for low-risk apps; for anything stateful keep manual approval. <strong>App Service Premium V3</strong> SKUs give zone-redundancy on by default in 2026 &mdash; flip it on if you weren&rsquo;t already getting it.</p>
'''

ANSWERS[89] = r'''<pre><code>// Jenkinsfile &mdash; Node.js to IBM Cloud Code Engine (container) with Cloud Foundry fallback
pipeline {
  agent any
  options { timestamps(); timeout(time: 25, unit: 'MINUTES') }
  environment {
    APP_NAME   = 'acme-node-app'
    REGION     = 'us-south'
    RESOURCE_GROUP = 'default'
    CE_PROJECT = 'acme-prod'
    REGISTRY   = 'us.icr.io/acme'           // IBM Cloud Container Registry
    IMAGE      = "${REGISTRY}/${APP_NAME}"
    IBM_API_KEY = credentials('ibm-cloud-api-key')
  }
  stages {
    stage('Test') {
      agent { docker { image 'node:20-alpine' } }
      steps {
        sh 'npm ci --no-audit --no-fund'
        sh 'npm test -- --ci'
        sh 'npm audit --omit=dev --audit-level=high || true'
      }
    }
    stage('Build &amp; push image') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          docker build -t ${IMAGE}:${BUILD_NUMBER} \\
                       -t ${IMAGE}:latest .
          # IBM Cloud CLI + plug-ins
          curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
          ibmcloud plugin install -f code-engine container-registry
          ibmcloud login --apikey "$IBM_API_KEY" -r "$REGION" -g "$RESOURCE_GROUP"
          ibmcloud cr login
          docker push ${IMAGE}:${BUILD_NUMBER}
          docker push ${IMAGE}:latest
        &apos;&apos;&apos;
      }
    }
    stage('Deploy to Code Engine') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          ibmcloud ce project select -n "$CE_PROJECT"
          # idempotent create-or-update
          if ibmcloud ce app get -n ${APP_NAME} &gt;/dev/null 2&gt;&amp;1; then
            ibmcloud ce app update -n ${APP_NAME} \\
              --image ${IMAGE}:${BUILD_NUMBER} \\
              --port 8080 \\
              --cpu 0.5 --memory 1G \\
              --min-scale 0 --max-scale 10 --concurrency 80 \\
              --env NODE_ENV=production \\
              --env-from-secret app-secrets
          else
            ibmcloud ce app create -n ${APP_NAME} \\
              --image ${IMAGE}:${BUILD_NUMBER} \\
              --registry-secret ibm-cr-secret \\
              --port 8080 \\
              --cpu 0.5 --memory 1G \\
              --min-scale 0 --max-scale 10 --concurrency 80 \\
              --env NODE_ENV=production \\
              --env-from-secret app-secrets
          fi
        &apos;&apos;&apos;
      }
    }
    stage('Verify') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          URL=$(ibmcloud ce app get -n ${APP_NAME} --output url)
          echo "Deployed: $URL"
          for i in 1 2 3 4 5; do
            curl -fsSL "$URL/healthz" &amp;&amp; break
            sleep 6
          done
        &apos;&apos;&apos;
      }
    }
  }
  post {
    failure { mail to: 'ops@acme.io', subject: "IBM deploy failed #${BUILD_NUMBER}", body: "${BUILD_URL}" }
  }
}
</code></pre>
<p><strong>Why these choices:</strong> <strong>Code Engine</strong> is IBM&rsquo;s serverless container platform (Knative under the hood) &mdash; scale-to-zero, pay-per-request, no cluster to operate. Cleaner story than legacy <strong>Cloud Foundry</strong>, which IBM has wound down for new workloads. The IBM CR holds the image; the SA that Code Engine uses needs a registry-secret to pull. <code>--min-scale 0</code> = scale-to-zero; bump to 1 if cold start matters.</p>
<p><strong>Cloud Foundry alternative</strong> (still works for legacy apps):</p>
<pre><code>ibmcloud cf install
ibmcloud target --cf -o ORG -s SPACE
ibmcloud cf push acme-node-app -m 256M -i 2 -b nodejs_buildpack
</code></pre>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>IKS / OpenShift on IBM Cloud</strong> &mdash; full K8s; deploy with <code>kubectl apply</code> from the same Jenkinsfile.</li>
<li><strong>Code Engine batch jobs</strong> &mdash; for cron-style work, <code>ibmcloud ce job create / submit</code>.</li>
<li><strong>Function</strong> &mdash; if it&rsquo;s a single HTTP handler, <code>ibmcloud ce fn create</code> instead of an app (Knative Functions).</li>
</ul>
<p><strong>2026 advice:</strong> use <strong>IBM Cloud OIDC + service-id API keys</strong> stored in Jenkins credentials &mdash; rotate via Vault. For multi-cloud orgs, consider <strong>Code Engine + Backstage</strong> for self-service developer experience.</p>
'''

ANSWERS[90] = r'''<pre><code># NOTE: PodSecurityPolicy was REMOVED in Kubernetes 1.25 (April 2022).
# This answer shows the modern replacement: Pod Security Admission + a
# concrete Kyverno policy that gives equivalent fine-grained control.

# 1) Pod Security Admission &mdash; built-in, label-driven, namespace-scoped
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    pod-security.kubernetes.io/enforce: restricted   # rejects on create
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit:   restricted   # logs only
    pod-security.kubernetes.io/warn:    restricted   # warns on kubectl apply
---
# 2) Kyverno ClusterPolicy &mdash; finer rules + exemptions PSA can&rsquo;t express
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: pod-security-baseline }
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    # 2a) No privileged containers
    - name: disallow-privileged
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Privileged containers are not allowed"
        pattern:
          spec:
            =(initContainers): [{ =(securityContext): { =(privileged): "false" } }]
            containers:        [{ =(securityContext): { =(privileged): "false" } }]

    # 2b) Drop ALL caps; allow-list explicit ones if needed
    - name: drop-all-capabilities
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Containers must drop ALL capabilities"
        pattern:
          spec:
            containers:
              - securityContext:
                  capabilities:
                    drop: ["ALL"]

    # 2c) Run as non-root
    - name: must-run-as-non-root
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Containers must run as non-root"
        anyPattern:
          - spec: { securityContext: { runAsNonRoot: true } }
          - spec: { containers: [{ securityContext: { runAsNonRoot: true } }] }

    # 2d) Read-only root filesystem
    - name: readonly-rootfs
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Root filesystem must be read-only"
        pattern:
          spec:
            containers:
              - securityContext: { readOnlyRootFilesystem: true }

    # 2e) Block hostPath volumes
    - name: no-hostpath
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "hostPath volumes are not allowed"
        pattern:
          spec:
            =(volumes):
              - X(hostPath): "null"
</code></pre>
<p><strong>Why PSPs were removed:</strong> they conflated authorization (RBAC) with admission (mutation/validation), had subtle ordering bugs (mutating defaults could let restricted pods through), and required cluster-wide RBAC <code>use</code> verbs that few teams understood. PSA + a policy engine is simpler and more flexible.</p>
<p><strong>The three PSA standards:</strong></p>
<ul>
<li><strong>privileged</strong> &mdash; no restrictions (kube-system, GPU drivers).</li>
<li><strong>baseline</strong> &mdash; blocks the obviously dangerous (privileged, hostPath, hostNetwork, hostPID).</li>
<li><strong>restricted</strong> &mdash; hardened: non-root, dropAllCapabilities, seccomp RuntimeDefault, no privilege escalation. Default for new namespaces in any modern cluster.</li>
</ul>
<p><strong>Mode flags per namespace:</strong> <code>enforce</code> rejects, <code>audit</code> logs to API server audit, <code>warn</code> prints to <code>kubectl</code>. Run <code>warn + audit</code> first, then flip to <code>enforce</code> once nothing fires.</p>
<p><strong>2026 advice:</strong> don&rsquo;t write a PSP &mdash; you can&rsquo;t. Default to <strong>PSA = restricted</strong> and layer one of:</p>
<ul>
<li><strong>Kyverno</strong> &mdash; YAML rules, mutate + validate + generate. Best UX; pre-built policy library at <code>kyverno-policies</code>.</li>
<li><strong>OPA Gatekeeper</strong> &mdash; Rego policies; more powerful, steeper learning curve.</li>
<li><strong>Validating Admission Policy (CEL)</strong> &mdash; native, no operator needed (1.30+ GA). Good for simple invariants.</li>
</ul>
<p>Pair with <strong>Falco</strong> for runtime detection of policy bypasses (kernel-syscall level), <strong>Trivy/Cosign</strong> for image-supply-chain hardening.</p>
'''

ANSWERS[91] = r'''<pre><code># docker-compose.yml &mdash; Elasticsearch 8 single-node + Kibana, secured
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.3
    container_name: es
    environment:
      - node.name=es
      - cluster.name=acme-dev
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - xpack.security.enabled=true
      - xpack.security.http.ssl.enabled=false       # plain HTTP for local dev
      - ES_JAVA_OPTS=-Xms1g -Xmx1g                  # &le; 50% of available RAM
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-changeme}
    ulimits:
      memlock: { soft: -1, hard: -1 }              # required for memory_lock
      nofile:  { soft: 65536, hard: 65536 }
    ports:
      - "127.0.0.1:9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS -u elastic:${ELASTIC_PASSWORD:-changeme} http://localhost:9200/_cluster/health?wait_for_status=yellow&amp;timeout=5s"]
      interval: 15s
      timeout: 10s
      retries: 10
      start_period: 60s

  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.3
    container_name: kibana
    environment:
      ELASTICSEARCH_HOSTS:    "http://es:9200"
      ELASTICSEARCH_USERNAME: "kibana_system"
      ELASTICSEARCH_PASSWORD: "${KIBANA_PASSWORD:-kibana123}"
      SERVER_HOST:            "0.0.0.0"
    ports:
      - "127.0.0.1:5601:5601"
    depends_on:
      elasticsearch: { condition: service_healthy }

volumes:
  es_data:
</code></pre>
<p><strong>One-time setup &mdash; reset the kibana_system password</strong> (the bootstrap step you can&rsquo;t skip):</p>
<pre><code># after `docker compose up -d` succeeds:
docker exec -it es \
  bin/elasticsearch-reset-password -u kibana_system -i  # paste the same value into KIBANA_PASSWORD
docker compose restart kibana
</code></pre>
<p><strong>Sanity checks:</strong></p>
<pre><code>curl -u elastic:changeme http://localhost:9200
# {"name":"es","cluster_name":"acme-dev","cluster_uuid":"..","version":{"number":"8.15.3"},...}
open http://localhost:5601                          # login: elastic / changeme
</code></pre>
<p><strong>Why these settings:</strong> <code>discovery.type=single-node</code> skips election (otherwise ES expects 3+ master-eligible nodes); <code>bootstrap.memory_lock=true</code> + matching ulimits prevents swap thrashing; heap sized to half of container memory (and never &gt; 31 GB even on big hosts &mdash; compressed oops break above that). <code>xpack.security.enabled</code> is <em>required</em> in 8.x &mdash; the days of unauthenticated localhost ES are over.</p>
<p><strong>Common follow-ons:</strong></p>
<ul>
<li><strong>Logstash / Filebeat</strong> &mdash; add a service pulling from <code>./logs:/var/log:ro</code> and shipping to <code>http://es:9200</code>.</li>
<li><strong>Multi-node cluster</strong> &mdash; replicate the <code>elasticsearch</code> service 3&times; with <code>discovery.seed_hosts=es-1,es-2,es-3</code> and unique <code>node.name</code>; mind ulimits and heap on each.</li>
<li><strong>TLS</strong> &mdash; generate certs with <code>elasticsearch-certutil</code>, mount under <code>/usr/share/elasticsearch/config/certs</code>, enable <code>xpack.security.http.ssl.*</code>.</li>
</ul>
<p><strong>2026 alternatives:</strong> <strong>OpenSearch</strong> (Apache 2.0 fork) is now the default in many shops &mdash; same Compose recipe, image is <code>opensearchproject/opensearch:2.x</code>. For new search workloads, look at <strong>Meilisearch</strong> (typo-tolerant, instant), <strong>Typesense</strong> (light, fast), or <strong>Vespa</strong> for vector + lexical hybrid search at scale. Use Compose ES only for local dev / integration tests; production should be <strong>Elastic Cloud</strong>, <strong>OpenSearch Service</strong>, or a managed Elasticsearch operator (ECK on K8s).</p>
'''

ANSWERS[92] = r'''<pre><code># .github/workflows/dart-cloud-run.yml
# Build a Dart server (or a Flutter web release) and ship to Cloud Run.
name: Deploy Dart to Cloud Run
on:
  push: { branches: [main] }
  workflow_dispatch:

permissions: { id-token: write, contents: read }

env:
  PROJECT: acme-prod
  REGION:  us-central1
  SERVICE: dart-api
  IMAGE:   us-central1-docker.pkg.dev/acme-prod/acme-images/dart-api

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dart-lang/setup-dart@v1
        with: { sdk: '3.5.3' }

      - name: Resolve, analyze, test
        run: |
          dart pub get
          dart analyze --fatal-infos
          dart test --coverage=coverage
          dart pub global activate coverage
          dart pub global run coverage:format_coverage \
            --lcov -i coverage -o coverage/lcov.info

      - name: AOT compile to native binary
        run: |
          dart compile exe bin/server.dart -o build/server
          ls -lh build/server

      - name: Build container
        run: |
          cat &gt; Dockerfile &lt;&lt;'EOF'
          # Distroless final stage &mdash; ~25 MB total
          FROM debian:stable-slim AS runtime
          RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends ca-certificates \
              &amp;&amp; rm -rf /var/lib/apt/lists/*
          COPY build/server /app/server
          ENV PORT=8080
          EXPOSE 8080
          USER 65532:65532
          ENTRYPOINT ["/app/server"]
          EOF
          docker build -t ${IMAGE}:${{ github.sha }} -t ${IMAGE}:latest .

      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: deployer@acme-prod.iam.gserviceaccount.com

      - uses: google-github-actions/setup-gcloud@v2

      - name: Push &amp; deploy
        run: |
          gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
          docker push ${IMAGE}:${{ github.sha }}
          docker push ${IMAGE}:latest

          gcloud run deploy ${SERVICE} \
            --image=${IMAGE}:${{ github.sha }} \
            --region=${REGION} --project=${PROJECT} \
            --execution-environment=gen2 \
            --cpu=1 --memory=512Mi --concurrency=80 \
            --min-instances=0 --max-instances=20 \
            --set-env-vars=ENV=prod \
            --set-secrets=API_KEY=api-key:latest \
            --allow-unauthenticated --quiet

          # Smoke
          URL=$(gcloud run services describe ${SERVICE} --region=${REGION} --format='value(status.url)')
          curl -fsSL --retry 5 --retry-delay 5 "${URL}/healthz"
</code></pre>
<p><strong>Why these choices:</strong> Dart compiles AOT to a static-ish binary, so the Cloud Run image stays under 30 MB on a Debian-slim base (or even smaller on distroless). The handler typically uses <code>shelf</code>:</p>
<pre><code>// bin/server.dart
import 'package:shelf/shelf_io.dart' as io;
import 'package:shelf_router/shelf_router.dart';
void main() async {
  final app = Router()
    ..get('/healthz', (_) =&gt; Response.ok('ok'))
    ..get('/api/hello', (_) =&gt; Response.ok('{"message":"hi"}',
                                  headers: {'content-type': 'application/json'}));
  final port = int.parse(Platform.environment['PORT'] ?? '8080');
  await io.serve(app, '0.0.0.0', port);
}
</code></pre>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Flutter Web</strong> deploy &mdash; replace compile step with <code>flutter build web --release</code>; final image is <code>nginx:alpine</code> serving <code>build/web</code>. Or skip Cloud Run and use <strong>Firebase Hosting</strong> (<code>firebase deploy --only hosting</code>) which is the natural fit for Flutter Web.</li>
<li><strong>Cloud Functions for Firebase (2nd gen)</strong> &mdash; same Cloud Run platform underneath; useful when a function is the unit of deploy.</li>
<li><strong>Distroless static</strong> base &mdash; if you statically link, drop to <code>gcr.io/distroless/static-debian12:nonroot</code> for ~10 MB.</li>
</ul>
<p><strong>2026 polish:</strong> always use <strong>Workload Identity Federation</strong> (the OIDC step) instead of long-lived JSON keys. Add <strong>Cloud Trace</strong> via <code>package:opentelemetry</code>, and gate prod deploys behind a GitHub Environment with required reviewers. For Flutter mobile, separate workflow &mdash; <code>fastlane</code> + Apple/Play store credentials are still the cleanest path.</p>
'''

ANSWERS[93] = r'''<pre><code>// Jenkinsfile &mdash; Swift on Linux to AWS Lambda (custom runtime)
pipeline {
  agent { label 'linux' }
  options { timestamps(); timeout(time: 30, unit: 'MINUTES') }
  environment {
    AWS_REGION = 'us-east-1'
    FN_NAME    = 'swift-fn-prod'
    BUCKET     = 'acme-lambda-deploys'
    SWIFT_VER  = '5.10'
  }
  stages {
    stage('Build inside swift:5.10 (amazonlinux2 abi)') {
      steps {
        sh &apos;&apos;&apos;
          # Use the Swift AWS Lambda Runtime AL2-compatible image so symbols match Lambda's libc
          docker run --rm \\
            -v "$PWD":/workspace -w /workspace \\
            swift:${SWIFT_VER}-amazonlinux2 \\
            bash -c "swift test &amp;&amp; swift build -c release --static-swift-stdlib"
        &apos;&apos;&apos;
      }
    }
    stage('Package') {
      steps {
        sh &apos;&apos;&apos;
          # Bootstrap script Lambda invokes; symlink to the actual binary
          mkdir -p out
          cp .build/release/AcmeLambda out/bootstrap
          chmod +x out/bootstrap
          (cd out &amp;&amp; zip -q ../lambda.zip bootstrap)
          ls -lh lambda.zip
        &apos;&apos;&apos;
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-deploy']]) {
          sh &apos;&apos;&apos;
            KEY=${FN_NAME}/${BUILD_NUMBER}-$(git rev-parse --short HEAD).zip
            aws s3 cp lambda.zip s3://$BUCKET/$KEY

            if aws lambda get-function --function-name $FN_NAME &gt;/dev/null 2&gt;&amp;1; then
              aws lambda update-function-code \\
                --function-name $FN_NAME \\
                --s3-bucket $BUCKET --s3-key $KEY \\
                --publish
              aws lambda wait function-updated --function-name $FN_NAME
            else
              aws lambda create-function \\
                --function-name $FN_NAME \\
                --runtime provided.al2023 \\
                --architectures x86_64 \\
                --handler bootstrap \\
                --role arn:aws:iam::123456789012:role/lambda-swift-exec \\
                --code S3Bucket=$BUCKET,S3Key=$KEY \\
                --memory-size 512 --timeout 15 \\
                --tracing-config Mode=Active \\
                --publish
            fi

            VER=$(aws lambda publish-version --function-name $FN_NAME --query Version --output text)
            aws lambda update-alias --function-name $FN_NAME --name live --function-version $VER
          &apos;&apos;&apos;
        }
      }
    }
    stage('Smoke') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          aws lambda invoke --function-name ${FN_NAME}:live \\
            --payload '{"name":"world"}' --cli-binary-format raw-in-base64-out /tmp/out.json
          cat /tmp/out.json
        &apos;&apos;&apos;
      }
    }
  }
}
</code></pre>
<p><strong>Companion <code>Package.swift</code> handler:</strong></p>
<pre><code>// swift-tools-version:5.10
import AWSLambdaRuntime
import AWSLambdaEvents

@main
struct AcmeLambda: SimpleLambdaHandler {
    struct In:  Codable { let name: String }
    struct Out: Codable { let message: String }
    func handle(_ event: In, context: LambdaContext) async throws -&gt; Out {
        Out(message: "Hello, \(event.name) from Swift!")
    }
}
</code></pre>
<p><strong>Why these choices:</strong> Lambda&rsquo;s <code>provided.al2023</code> runtime expects an executable named <code>bootstrap</code>. Building inside <code>swift:5.10-amazonlinux2</code> guarantees glibc/ABI compatibility (Lambda&rsquo;s underlying OS). <code>--static-swift-stdlib</code> bundles the Swift stdlib so the binary runs without installing Swift on the function. <code>swift-aws-lambda-runtime</code> wraps event polling/JSON marshalling.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>arm64</strong> &mdash; rebuild with <code>swift:5.10-amazonlinux2</code> on ARM (use <code>--platform linux/arm64</code> on multi-arch hosts) for ~20% cost savings on Graviton.</li>
<li><strong>Container image Lambda</strong> &mdash; <code>FROM public.ecr.aws/lambda/provided:al2023</code>, <code>COPY bootstrap /var/runtime/bootstrap</code>; needed when the zip exceeds 250 MB unzipped.</li>
<li><strong>SAM</strong> &mdash; <code>sam build --beta-features --use-container</code> handles the Linux build automatically.</li>
</ul>
<p><strong>2026 advice:</strong> Swift on Lambda has matured but the ecosystem is still small. Use it when the rest of the org runs Swift (Apple-platform apps with shared models). For <strong>API Gateway + Lambda</strong>, prefer Lambda Function URLs unless you need API Gateway features (auth, throttling, custom domains via API Gateway). Cold starts hover at ~200&ndash;400 ms even with <code>--static-swift-stdlib</code>; provisioned concurrency or SnapStart-equivalent (not yet on Swift) is the only way to flatten that.</p>
'''

ANSWERS[94] = r'''<pre><code># hpa-cpu.yaml &mdash; classic CPU-based horizontal autoscaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3                    # always keep 3 alive (capacity reserve)
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization         # average across pods
          averageUtilization: 60    # scale to keep pods at ~60% of requested CPU
  behavior:                          # tame the autoscaler &mdash; production-essential
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - { type: Pods,    value: 4,   periodSeconds: 30 }   # +4 pods / 30 s
        - { type: Percent, value: 100, periodSeconds: 30 }   # or +100% / 30 s
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300                         # cool-off 5 min before shrinking
      policies:
        - { type: Pods,    value: 1,  periodSeconds: 60 }    # at most -1 pod / minute
        - { type: Percent, value: 10, periodSeconds: 60 }
      selectPolicy: Min
---
# Deployment must declare cpu requests &mdash; HPA has no target without them.
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  replicas: 3
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.0
          resources:
            requests: { cpu: "200m", memory: "256Mi" }
            limits:   { cpu: "1",    memory: "512Mi" }
          readinessProbe: { httpGet: { path: /healthz, port: 8080 }, periodSeconds: 5 }
</code></pre>
<p><strong>How it works:</strong> the HPA controller polls metrics-server (or any custom-metrics adapter) every 15 s. <em>Utilization</em> = current CPU usage / requested CPU. With <code>averageUtilization: 60</code> the controller targets 60% across all pods; if average climbs to 90% it scales up; below 60% it scales down. <code>requests</code> are mandatory &mdash; without them the ratio is undefined.</p>
<p><strong>Why <code>behavior</code> matters:</strong> the default scale-down can be aggressive and cause flapping under spiky traffic. The <code>scaleDown</code> stabilization window + per-minute caps prevent flapping; <code>scaleUp</code> is left fast (no stabilization) so the autoscaler reacts quickly to load spikes.</p>
<p><strong>Verify:</strong></p>
<pre><code>kubectl get hpa api-hpa -n prod
kubectl describe hpa api-hpa -n prod   # shows currentMetrics / decisions
kubectl top pods -n prod -l app=api    # confirms metrics-server installed
</code></pre>
<p><strong>Common variants:</strong></p>
<ul>
<li><strong>Memory-based</strong> &mdash; same shape with <code>name: memory</code>. Riskier because GC&rsquo;d languages (JVM, Node) hold steady high memory; not a good scale signal alone.</li>
<li><strong>Custom metrics</strong> &mdash; RPS or queue depth via <code>type: External</code> and the Prometheus Adapter. Almost always a better load signal than CPU.</li>
<li><strong>KEDA</strong> &mdash; event-driven autoscaling (Kafka lag, SQS depth, cron, &gt; 70 sources). Generates a managed HPA underneath. Use for event-driven workloads.</li>
</ul>
<p><strong>2026 advice:</strong> CPU-based HPA is the right starter, but most production teams move to <strong>RPS-per-pod</strong> or <strong>queue-depth</strong> autoscaling once they outgrow it &mdash; CPU correlates poorly with real demand for I/O-bound services. Pair HPA with <strong>VPA off-mode</strong> (recommendations) so you continuously right-size requests, and <strong>Karpenter</strong> at the node level so HPA-driven new pods don&rsquo;t pend waiting for capacity.</p>
'''

ANSWERS[95] = r'''<pre><code># Dockerfile &mdash; ASP.NET Core 9 production image
# ------- Stage 1: build -------
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Restore deps (cached layer if csproj/sln unchanged)
COPY ["AcmeApi.sln", "./"]
COPY ["src/AcmeApi/AcmeApi.csproj",       "src/AcmeApi/"]
COPY ["src/AcmeCore/AcmeCore.csproj",     "src/AcmeCore/"]
COPY ["test/AcmeApi.Tests/AcmeApi.Tests.csproj", "test/AcmeApi.Tests/"]
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet restore AcmeApi.sln

# Copy the rest, run tests, publish
COPY . .
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet test test/AcmeApi.Tests --no-restore --verbosity minimal
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet publish src/AcmeApi -c Release -o /app/publish \
      --no-restore \
      /p:PublishTrimmed=false \
      /p:GenerateDocumentationFile=true

# ------- Stage 2: chiseled (distroless) runtime -------
FROM mcr.microsoft.com/dotnet/aspnet:9.0-noble-chiseled-extra AS runtime
WORKDIR /app
COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://+:8080 \
    ASPNETCORE_HTTP_PORTS=8080 \
    DOTNET_RUNNING_IN_CONTAINER=true \
    DOTNET_GENERATE_ASPNET_CERTIFICATE=false \
    DOTNET_NOLOGO=true \
    DOTNET_USE_POLLING_FILE_WATCHER=true \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false

EXPOSE 8080
USER $APP_UID                              # built-in non-root in chiseled images
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
ENTRYPOINT ["dotnet", "AcmeApi.dll"]
</code></pre>
<p><strong>Why these choices:</strong></p>
<ul>
<li><strong>Multi-stage</strong> with the SDK image for build, slim <em>runtime</em> image for ship &mdash; from ~800 MB SDK to ~110 MB chiseled.</li>
<li><strong>Chiseled Ubuntu</strong> (<code>9.0-noble-chiseled-extra</code>) is Microsoft&rsquo;s distroless flavour: no shell, no package manager, non-root by default, &lt; 30 MB OS surface. The <code>-extra</code> tag adds <code>libstdc++/icu</code> for libraries that need them; use plain <code>9.0-noble-chiseled</code> if you don&rsquo;t.</li>
<li><strong>BuildKit cache mount</strong> on <code>/root/.nuget/packages</code> dramatically speeds CI rebuilds.</li>
<li><strong>Solution-level restore first</strong> caches layer deps separately from source; changing one C# file doesn&rsquo;t invalidate restore.</li>
</ul>
<p><strong>Companion <code>Program.cs</code> health endpoint:</strong></p>
<pre><code>var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHealthChecks();
var app = builder.Build();
app.MapHealthChecks("/healthz");
app.MapGet("/", () =&gt; Results.Ok(new { status = "ok" }));
app.Run();
</code></pre>
<p><strong>Build &amp; push:</strong></p>
<pre><code>docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/acme/api:1.0.0 \
  --push .
</code></pre>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Native AOT</strong> &mdash; <code>&lt;PublishAot&gt;true&lt;/PublishAot&gt;</code> + <code>dotnet publish -r linux-x64 -c Release</code>. Cold start drops to ~30 ms, image to ~25 MB on <code>aspnet-runtime-deps:9.0-noble-chiseled</code>; trade-off: no reflection-heavy libraries.</li>
<li><strong>Self-contained single file</strong> &mdash; <code>--self-contained -p:PublishSingleFile=true</code>; image still slim and you don&rsquo;t depend on the .NET runtime image.</li>
<li><strong>Trimmed deployment</strong> &mdash; <code>PublishTrimmed=true</code> drops unused IL; combine with AOT.</li>
</ul>
<p><strong>2026 polish:</strong> sign with <code>cosign sign --yes</code>, attach an SBOM (<code>syft</code>), enable <strong>OpenTelemetry .NET</strong> (<code>OpenTelemetry.Extensions.Hosting</code>), and use <strong>YARP</strong> if you need a reverse-proxy front end. For deployment platforms, <strong>Azure Container Apps</strong>, <strong>AWS App Runner</strong>, and <strong>Cloud Run</strong> are all great fits for ASP.NET Core containers &mdash; serverless container UX with managed scaling.</p>
'''

ANSWERS[96] = r'''<pre><code># .github/workflows/heroku-csharp.yml &mdash; ship a C#/ASP.NET Core app to Heroku
name: Deploy C# to Heroku
on:
  push: { branches: [main] }
  workflow_dispatch:

env:
  HEROKU_APP: acme-csharp-prod
  HEROKU_REGISTRY: registry.heroku.com

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '9.0.x' }
      - name: Restore + test
        run: |
          dotnet restore
          dotnet test --no-restore --verbosity minimal --logger "trx;LogFileName=results.trx"
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: test-results, path: '**/*.trx' }

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment:                              # gated env w/ required reviewers
      name: production
      url: https://${{ env.HEROKU_APP }}.herokuapp.com/
    steps:
      - uses: actions/checkout@v4

      - name: Build container image (Heroku-compatible)
        run: |
          # Heroku assigns a random PORT at runtime &mdash; the app must read it.
          # Heroku containers run as non-root with UID provided by the platform.
          cat &gt; Dockerfile.heroku &lt;&lt;'EOF'
          FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
          WORKDIR /src
          COPY . .
          RUN dotnet publish src/AcmeApi -c Release -o /app/publish

          FROM mcr.microsoft.com/dotnet/aspnet:9.0
          WORKDIR /app
          COPY --from=build /app/publish .
          ENV ASPNETCORE_URLS=http://+:${PORT:-5000}
          # Heroku appends "${PORT}" so we expand it via a shell entrypoint
          CMD ["/bin/sh","-c","dotnet AcmeApi.dll --urls http://+:${PORT}"]
          EOF
          docker build -t ${HEROKU_REGISTRY}/${HEROKU_APP}/web -f Dockerfile.heroku .

      - name: Login to Heroku container registry
        run: echo "${{ secrets.HEROKU_API_KEY }}" | docker login --username=_ --password-stdin $HEROKU_REGISTRY

      - name: Push image
        run: docker push ${HEROKU_REGISTRY}/${HEROKU_APP}/web

      - name: Release on Heroku
        run: |
          IMAGE_ID=$(docker inspect ${HEROKU_REGISTRY}/${HEROKU_APP}/web --format='{{.Id}}')
          curl -fsSL -X PATCH https://api.heroku.com/apps/${HEROKU_APP}/formation \
            -H "Authorization: Bearer ${{ secrets.HEROKU_API_KEY }}" \
            -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
            -H "Content-Type: application/json" \
            -d "{\"updates\":[{\"type\":\"web\",\"docker_image\":\"$IMAGE_ID\"}]}"

      - name: Smoke
        run: |
          for i in 1 2 3 4 5 6; do
            curl -fsSL https://${HEROKU_APP}.herokuapp.com/healthz &amp;&amp; break
            sleep 8
          done
</code></pre>
<p><strong>Why container-deploy over buildpack:</strong> the Microsoft <code>dotnet</code> buildpack is community-maintained and lags behind .NET releases. Container deploys give you control over the SDK version, base image, and reproducible builds. The trade-off: you maintain the Dockerfile.</p>
<p><strong>Heroku quirks worth knowing:</strong></p>
<ul>
<li><code>PORT</code> is injected at runtime &mdash; bind to <code>http://+:${PORT}</code>, not a fixed port.</li>
<li>Containers run as a non-root UID assigned by the platform; don&rsquo;t hard-code <code>USER</code>.</li>
<li>Heroku doesn&rsquo;t support <code>VOLUME</code>; the filesystem is ephemeral, restart-blanked.</li>
<li>Long requests are killed at 30 s &mdash; use background workers for slow jobs (separate Heroku formation type).</li>
</ul>
<p><strong>2026 alternatives (genuinely cheaper / nicer):</strong></p>
<ul>
<li><strong>Render</strong> &mdash; near drop-in for Heroku container deploys, often half the cost; native blueprint via <code>render.yaml</code>.</li>
<li><strong>Fly.io</strong> &mdash; multi-region edge, auto-stop dynos to scale-to-zero, <code>fly launch</code> generates this Dockerfile.</li>
<li><strong>Azure App Service</strong> / <strong>AWS App Runner</strong> / <strong>Cloud Run</strong> &mdash; all great PaaS hosts for .NET containers with first-party tooling.</li>
<li><strong>Railway</strong> &mdash; simplest UX of all of these; per-second pricing.</li>
</ul>
<p>If you&rsquo;re only on Heroku because of inertia, container deploys make migration trivial &mdash; the same image runs unchanged on any of the platforms above.</p>
'''

ANSWERS[97] = r'''<pre><code>#!/usr/bin/env bash
# cluster-autoscaler-bootstrap.sh &mdash; install + configure CA on EKS
# (For non-EKS clusters: section at the bottom shows the canonical Kubernetes Autoscaler manifests.)
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:?cluster name required}"
REGION="${REGION:-us-east-1}"
NAMESPACE="${NAMESPACE:-kube-system}"
CA_VERSION="${CA_VERSION:-1.31.0}"             # match your K8s minor version

echo "==&gt; Tag node-group ASGs (CA discovers them by tag)"
for ASG in $(aws autoscaling describe-auto-scaling-groups \
                --query "AutoScalingGroups[?contains(Tags[?Key=='eks:cluster-name']|[0].Value, '$CLUSTER_NAME')].AutoScalingGroupName" \
                --output text); do
  aws autoscaling create-or-update-tags --tags \
    "ResourceId=$ASG,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/enabled,Value=true,PropagateAtLaunch=true" \
    "ResourceId=$ASG,ResourceType=auto-scaling-group,Key=k8s.io/cluster-autoscaler/$CLUSTER_NAME,Value=owned,PropagateAtLaunch=true"
done

echo "==&gt; Create IAM Role for ServiceAccount (IRSA)"
eksctl create iamserviceaccount \
  --cluster "$CLUSTER_NAME" --region "$REGION" \
  --namespace "$NAMESPACE" --name cluster-autoscaler \
  --attach-policy-arn arn:aws:iam::aws:policy/AutoScalingFullAccess \
  --override-existing-serviceaccounts --approve

echo "==&gt; Install Cluster Autoscaler via Helm"
helm repo add autoscaler https://kubernetes.github.io/autoscaler &amp;&amp; helm repo update

helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler \
  --namespace "$NAMESPACE" \
  --version 9.43.0 \
  --set "autoDiscovery.clusterName=$CLUSTER_NAME" \
  --set "awsRegion=$REGION" \
  --set "image.tag=v$CA_VERSION" \
  --set "rbac.serviceAccount.create=false" \
  --set "rbac.serviceAccount.name=cluster-autoscaler" \
  --set "extraArgs.balance-similar-node-groups=true" \
  --set "extraArgs.skip-nodes-with-system-pods=false" \
  --set "extraArgs.skip-nodes-with-local-storage=false" \
  --set "extraArgs.expander=least-waste" \
  --set "extraArgs.scale-down-utilization-threshold=0.5" \
  --set "extraArgs.scale-down-unneeded-time=10m"

echo "==&gt; Verify"
kubectl -n "$NAMESPACE" rollout status deploy/cluster-autoscaler-aws-cluster-autoscaler --timeout=2m
kubectl -n "$NAMESPACE" logs -l app.kubernetes.io/name=aws-cluster-autoscaler --tail=20

# ----- Validation: deploy a workload that needs more capacity -----
cat &lt;&lt;'EOF' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata: { name: ca-test, namespace: default }
spec:
  replicas: 50
  selector: { matchLabels: { app: ca-test } }
  template:
    metadata: { labels: { app: ca-test } }
    spec:
      containers:
        - name: pause
          image: registry.k8s.io/pause:3.10
          resources:
            requests: { cpu: 500m, memory: 512Mi }
EOF

echo "==&gt; Watch CA scale ASG up; clean up:"
echo "    kubectl delete deploy ca-test"
</code></pre>
<p><strong>How it works:</strong> CA watches for <strong>pending pods</strong>; if one cannot be scheduled because no node has capacity, it simulates which ASG could fit it and sends an <code>increase-capacity</code> request to AWS. It also <em>drains and removes</em> nodes that have been under-utilised for &gt; <code>scale-down-unneeded-time</code> and whose pods could fit elsewhere. Discovery via tags lets you add new node groups without touching CA config.</p>
<p><strong>Tuning knobs that matter:</strong></p>
<ul>
<li><code>--expander</code> &mdash; <em>least-waste</em> (best fit), <em>random</em>, <em>most-pods</em>, <em>priority</em> (per-NodeGroup priority), <em>price</em> (cost-aware).</li>
<li><code>--balance-similar-node-groups=true</code> &mdash; spreads capacity across AZs.</li>
<li><code>--scale-down-utilization-threshold</code> &mdash; below this fraction, the node is a candidate for removal.</li>
<li><strong>PodDisruptionBudgets</strong> protect critical pods from being evicted during scale-down.</li>
<li><strong>Pod priority + safe-to-evict annotation</strong> (<code>cluster-autoscaler.kubernetes.io/safe-to-evict</code>) controls which pods block scale-down.</li>
</ul>
<p><strong>2026 advice:</strong> <strong>Karpenter is the modern replacement on AWS</strong> &mdash; it doesn&rsquo;t use ASGs, picks instance types per workload (instead of pre-shaped node groups), reacts in seconds rather than minutes, and consolidates aggressively. CA is still the right answer on GKE/AKS where Karpenter equivalents are less mature, or for clusters with regulatory constraints requiring fixed instance types per ASG. On Azure, look at <strong>Karpenter Azure provider</strong> (now GA) and <strong>NAP</strong> (Node Auto Provisioning) for a similar model.</p>
'''

ANSWERS[98] = r'''<pre><code>// Jenkinsfile &mdash; Perl app to Google Cloud Functions (2nd gen, Cloud Run-backed)
// Cloud Functions doesn&rsquo;t have a native Perl runtime, so we use a custom container.
pipeline {
  agent any
  options { timestamps(); timeout(time: 20, unit: 'MINUTES') }
  environment {
    PROJECT  = 'acme-prod'
    REGION   = 'us-central1'
    FN_NAME  = 'perl-fn'
    AR_REPO  = 'acme-images'
    IMAGE    = "us-central1-docker.pkg.dev/acme-prod/acme-images/perl-fn"
  }
  stages {
    stage('Toolchain &amp; auth') {
      steps {
        sh &apos;&apos;&apos;
          which gcloud || (
            curl https://sdk.cloud.google.com | bash &gt; /dev/null
            exec -l "$SHELL"
          )
          gcloud --version
        &apos;&apos;&apos;
        withCredentials([file(credentialsId: 'gcp-deployer-sa', variable: 'KEY')]) {
          sh 'gcloud auth activate-service-account --key-file="$KEY"'
        }
        sh 'gcloud config set project $PROJECT &amp;&amp; gcloud config set run/region $REGION'
      }
    }

    stage('Test') {
      agent { docker { image 'perl:5.40-slim' } }
      steps {
        sh &apos;&apos;&apos;
          cpanm --installdeps --notest .
          prove -lvr t/
          perlcritic --severity 4 lib/ &gt; perlcritic.txt || true
          perltidy --check-only lib/*.pm
        &apos;&apos;&apos;
        archiveArtifacts artifacts: 'perlcritic.txt', allowEmptyArchive: true
      }
    }

    stage('Build container') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          cat &gt; Dockerfile &lt;&lt;'EOF'
          FROM perl:5.40-slim
          WORKDIR /app
          ENV PORT=8080 PERL5LIB=/app/lib
          COPY cpanfile cpanfile.snapshot ./
          RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends \
                build-essential libssl-dev zlib1g-dev \
              &amp;&amp; cpanm --installdeps --notest --no-man-pages . \
              &amp;&amp; apt-get purge -y build-essential \
              &amp;&amp; apt-get autoremove -y \
              &amp;&amp; rm -rf /var/lib/apt/lists/*
          COPY . .
          # Functions Framework for Perl: HTTP wrapper that calls our handler
          EXPOSE 8080
          CMD ["plackup","-s","Starman","--port","8080","--workers","4","app.psgi"]
          EOF
          docker build -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .
        &apos;&apos;&apos;
      }
    }

    stage('Push') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
          docker push ${IMAGE}:${BUILD_NUMBER}
          docker push ${IMAGE}:latest
        &apos;&apos;&apos;
      }
    }

    stage('Deploy as gen2 function') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          gcloud functions deploy ${FN_NAME} \\
            --gen2 \\
            --region=${REGION} \\
            --runtime=docker \\
            --image=${IMAGE}:${BUILD_NUMBER} \\
            --entry-point=app \\
            --trigger-http --allow-unauthenticated \\
            --memory=256Mi --cpu=1 --timeout=60s \\
            --concurrency=80 --max-instances=20 --min-instances=0 \\
            --set-env-vars=APP_ENV=prod \\
            --set-secrets=DB_PASS=db-pass:latest
        &apos;&apos;&apos;
      }
    }

    stage('Smoke') {
      when { branch 'main' }
      steps {
        sh &apos;&apos;&apos;
          URL=$(gcloud functions describe ${FN_NAME} --gen2 --region=${REGION} --format='value(serviceConfig.uri)')
          for i in 1 2 3 4 5; do curl -fsSL "$URL/healthz" &amp;&amp; break; sleep 6; done
        &apos;&apos;&apos;
      }
    }
  }
}
</code></pre>
<p><strong>Companion <code>app.psgi</code>:</strong></p>
<pre><code>use strict; use warnings;
use Plack::Builder;
use JSON::PP;

my $app = sub {
    my $env = shift;
    if ($env-&gt;{PATH_INFO} eq '/healthz') {
        return [ 200, ['Content-Type','text/plain'], ['ok'] ];
    }
    my $body = encode_json({ message =&gt; 'hello from perl' });
    return [ 200, ['Content-Type','application/json'], [$body] ];
};

builder { enable 'AccessLog'; $app; };
</code></pre>
<p><strong>Why these choices:</strong> Cloud Functions 2nd gen runs on Cloud Run; you can supply <em>any</em> container as long as it listens on <code>$PORT</code>. We package Perl + dependencies via <code>cpanm</code> at build time (cached in CI) and run under <strong>Starman</strong> (high-perf preforking PSGI server) for parallelism. Concurrency 80 means each instance handles 80 in-flight requests &mdash; great for I/O-bound Perl handlers.</p>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Direct Cloud Run</strong> (<code>gcloud run deploy</code>) &mdash; if you don&rsquo;t need the Functions metadata abstraction (event-source bindings, IAM-per-function), Cloud Run is one fewer indirection.</li>
<li><strong>Pub/Sub trigger</strong> &mdash; <code>--trigger-topic</code> for event-driven Perl workers; the Functions Framework wraps Pub/Sub events in HTTP under the hood.</li>
<li><strong>App Engine flexible</strong> &mdash; supports custom runtimes too, slightly different scaling model.</li>
</ul>
<p><strong>2026 advice:</strong> use <strong>Workload Identity Federation</strong> instead of a downloaded SA key file (<code>--key-file</code> is officially deprecated). Pin Perl to a specific Docker digest for reproducibility, sign with <code>cosign</code>, and add <strong>Cloud Trace</strong> via OpenTelemetry. Honestly: in 2026, fresh greenfield work on Perl + Cloud Functions is rare &mdash; you&rsquo;re usually keeping a legacy CGI/Catalyst/Mojolicious app alive. If that&rsquo;s the case, Cloud Run gives you a cheap, scale-to-zero home for it without a rewrite.</p>
'''

ANSWERS[99] = r'''<pre><code># pdb.yaml &mdash; protect critical workloads from voluntary disruptions
# (PDBs only constrain VOLUNTARY evictions: drains, autoscaler scale-down, deployment
#  rolling updates that go through the eviction API. A node crash bypasses PDB.)

# Pattern A: minAvailable as an absolute number
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
  namespace: prod
spec:
  minAvailable: 2                      # always keep at least 2 pods up
  selector:
    matchLabels:
      app: api
---
# Pattern B: minAvailable as a percentage of currentReplicaCount
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: workers-pdb
  namespace: prod
spec:
  minAvailable: 75%                    # tolerate at most 25% disruption
  selector:
    matchLabels:
      app: workers
---
# Pattern C: maxUnavailable + unhealthyPodEvictionPolicy (1.27+ GA)
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb-strict
  namespace: prod
spec:
  maxUnavailable: 1                    # at most 1 pod down at a time
  selector:
    matchLabels:
      app: api
  unhealthyPodEvictionPolicy: AlwaysAllow   # let unhealthy pods be evicted
                                            # so a stuck pod can&rsquo;t block node drains
---
# Companion: a Deployment with surge so PDB + rollouts coexist nicely
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2                      # add 2 new pods
      maxUnavailable: 0                # never go below replicas during rollout
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: ghcr.io/acme/api:1.4.0
          readinessProbe: { httpGet: { path: /ready, port: 8080 }, periodSeconds: 5 }
</code></pre>
<p><strong>How it works:</strong> when something tries to evict a pod (kubectl drain, autoscaler removing a node, controller doing a rolling update), the API server checks the matching PDB before allowing it. If the eviction would breach <code>minAvailable</code> / <code>maxUnavailable</code>, it&rsquo;s rejected with HTTP 429 and the caller retries. Use <em>one or the other</em> &mdash; combining minAvailable + maxUnavailable on the same PDB is invalid.</p>
<p><strong>Verify:</strong></p>
<pre><code>kubectl get pdb -n prod
# NAME    MIN AVAILABLE  MAX UNAVAILABLE  ALLOWED DISRUPTIONS
# api-pdb 2              N/A              4              # 6 - 2 = 4 can drop
kubectl describe pdb api-pdb -n prod
# Triggers: status.disruptionsAllowed, currentHealthy, desiredHealthy
</code></pre>
<p><strong>Pitfalls:</strong></p>
<ul>
<li><strong>PDB doesn&rsquo;t apply to pod failure</strong> &mdash; only voluntary evictions. A node crash takes pods down ignoring PDB.</li>
<li><strong>Single-replica deployments</strong> + <code>minAvailable: 1</code> = <em>node drains hang forever</em>. Either run &ge; 2 replicas, or set <code>maxUnavailable: 1</code>.</li>
<li><strong>Stuck pending pods</strong> count toward currentHealthy in older versions. <code>unhealthyPodEvictionPolicy: AlwaysAllow</code> (1.27+) makes drains progress when pods are unhealthy.</li>
<li><strong>StatefulSets need extra care</strong> &mdash; PDB applies, but rolling-update of a StatefulSet is sequential, so practical safety also depends on <code>podManagementPolicy</code> and proper PreStop hooks.</li>
</ul>
<p><strong>Sensible defaults:</strong></p>
<ul>
<li><strong>Stateless services with &ge; 3 replicas</strong>: <code>maxUnavailable: 1</code>.</li>
<li><strong>Quorum systems</strong> (etcd, RabbitMQ, Kafka): <code>minAvailable: N - quorum + 1</code> &mdash; e.g. for 5 replicas with quorum 3: <code>minAvailable: 3</code>.</li>
<li><strong>Singletons</strong>: don&rsquo;t set a PDB at all (anything tighter than the existing replica count blocks drains).</li>
</ul>
<p><strong>2026 polish:</strong> pair PDBs with <strong>PriorityClasses</strong> so high-priority pods preempt without breaching the budget; use <strong>Karpenter consolidation</strong> which natively respects PDBs; alert on <code>kube_poddisruptionbudget_status_current_healthy &lt; kube_poddisruptionbudget_status_desired_healthy</code> in Prometheus &mdash; this is your early signal that drains are stalling.</p>
'''

ANSWERS[100] = r'''<pre><code># docker-compose.yml &mdash; MySQL 8.4 LTS for local dev with persistence + admin UI
services:
  mysql:
    image: mysql:8.4
    container_name: mysql
    restart: unless-stopped
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_0900_ai_ci
      - --default-authentication-plugin=caching_sha2_password
      - --innodb-buffer-pool-size=512M
      - --max-connections=200
      - --slow-query-log=ON
      - --long-query-time=1
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-rootpass}
      MYSQL_DATABASE:      ${MYSQL_DATABASE:-app}
      MYSQL_USER:          ${MYSQL_USER:-app}
      MYSQL_PASSWORD:      ${MYSQL_PASSWORD:-apppass}
      TZ:                  Etc/UTC
    ports:
      - "127.0.0.1:3306:3306"          # bind to localhost only, never 0.0.0.0
    volumes:
      - mysql_data:/var/lib/mysql
      - ./db/init:/docker-entrypoint-initdb.d:ro    # *.sql / *.sh run on first boot
      - ./db/conf.d:/etc/mysql/conf.d:ro
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "127.0.0.1", "-uroot", "-p$$MYSQL_ROOT_PASSWORD"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  adminer:
    image: adminer:5
    container_name: adminer
    restart: unless-stopped
    ports: ["127.0.0.1:8080:8080"]
    environment:
      ADMINER_DEFAULT_SERVER: mysql
      ADMINER_DESIGN: dracula
    depends_on:
      mysql: { condition: service_healthy }

volumes:
  mysql_data:
</code></pre>
<p><strong>Run &amp; connect:</strong></p>
<pre><code>docker compose up -d
docker compose exec mysql mysql -uapp -papppass app -e "SELECT VERSION();"
# Adminer UI:  http://localhost:8080  (Server: mysql, User: app, DB: app)
</code></pre>
<p><strong>Why these settings:</strong></p>
<ul>
<li><strong>MySQL 8.4 LTS</strong> &mdash; current Long-Term Support line in 2026 (8.0 is past initial GA support; 8.4 is supported through 2032).</li>
<li><strong><code>caching_sha2_password</code></strong> is the default in 8.x; old clients (mysql2 &lt; v3, PHP &lt; 7.4 with mysqlnd) need an upgrade or a dedicated user with <code>mysql_native_password</code>.</li>
<li><strong><code>utf8mb4</code></strong> with <code>utf8mb4_0900_ai_ci</code> is the right collation default &mdash; <code>utf8</code> alone is a 3-byte alias that breaks emoji.</li>
<li><strong><code>innodb-buffer-pool-size</code></strong> tuned for ~1 GB containers; bump to ~70% of available RAM in production.</li>
<li><strong>Slow query log</strong> with <code>long-query-time=1</code> catches queries &gt; 1 s &mdash; invaluable in dev.</li>
<li><strong>Init scripts</strong> in <code>./db/init</code> run only on the <em>first</em> boot when the data dir is empty &mdash; perfect for seeding schemas / fixtures.</li>
</ul>
<p><strong>Variants:</strong></p>
<ul>
<li><strong>Multi-replica with replication</strong> &mdash; use the Bitnami chart or <code>mysql/mysql-cluster</code>; for primary-replica testing, two services with <code>--server-id</code>, <code>--log-bin</code>, <code>CHANGE REPLICATION SOURCE</code>.</li>
<li><strong>MariaDB 11.x</strong> drop-in &mdash; same Compose file with <code>image: mariadb:11.4</code>; subtly different SQL extensions (sequences, JSON path, system-versioned tables).</li>
<li><strong>Percona Server / TiDB</strong> &mdash; for production-class extensions or distributed SQL.</li>
<li><strong>Testcontainers</strong> &mdash; <code>MySQLContainer("mysql:8.4")</code> per integration test for true isolation.</li>
</ul>
<p><strong>2026 advice:</strong> for production you almost certainly want <strong>RDS / Aurora MySQL / Cloud SQL / Azure Database for MySQL / PlanetScale</strong> &mdash; managed backups, point-in-time recovery, automated minor upgrades, parameter groups, and (for Aurora/PlanetScale) horizontal scale. Compose MySQL is for local dev and integration tests <em>only</em>; never run it for production. For local dev with a strict perf parity to RDS, pin the same engine version (<code>8.4.x</code>) and copy parameter group settings into <code>./db/conf.d/my.cnf</code>.</p>
'''
