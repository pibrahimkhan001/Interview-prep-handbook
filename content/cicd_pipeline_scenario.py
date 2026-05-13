"""Detailed answers for CI/CD Pipeline Scenario Based interview questions.

Each ANSWERS[n] is an HTML string suitable for embedding inside a chapter page.
Style: Situation / Approach / code block / Trade-offs table / Production polish,
with substantial code blocks and 2026-current vendor references throughout.
~4,500-5,500 chars per answer.
"""

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''<p><strong>Situation:</strong> a small team has a Node.js API on GitHub and needs a <strong>full CI/CD pipeline</strong> that runs tests on every PR, builds a container, deploys to staging on merge to <code>main</code>, and promotes to production via tag &mdash; without operating a self-hosted CI server.</p>

<p><strong>Approach:</strong> use <strong>GitHub Actions</strong> as the CI engine, push images to <strong>GitHub Container Registry (GHCR)</strong>, deploy to <strong>Fly.io</strong>/<strong>Render</strong>/<strong>Railway</strong> (or <strong>AWS App Runner</strong>/<strong>ECS Fargate</strong> for AWS shops). Authenticate with <strong>OIDC</strong> for cloud providers &mdash; no static keys. Run unit and integration tests with <strong>Vitest</strong>, lint with <strong>Biome</strong>, scan with <strong>Trivy</strong> and <strong>CodeQL</strong>, then sign images with <strong>Cosign</strong> and attach an SBOM via <strong>Syft</strong>.</p>

<pre><code>name: ci-cd
on:
  push: { branches: [main], tags: ["v*"] }
  pull_request:
permissions: { id-token: write, contents: read, packages: write }
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx biome ci .
      - run: npm test
      - uses: codecov/codecov-action@v4
  build:
    needs: test
    if: github.event_name == 'push'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
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
          provenance: true
          sbom: true
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    environment: staging
    steps:
      - uses: superfly/flyctl-actions/setup-flyctl@v1
      - run: flyctl deploy --app api-staging --image ghcr.io/${{ github.repository }}:${{ github.sha }}
        env: { FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }} }
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Tools</th></tr></thead><tbody>
<tr><td>Test gate</td><td>Required check on PRs, branch protection</td><td>Vitest, Biome, CodeQL</td></tr>
<tr><td>Image build</td><td>BuildKit with GHA cache, multi-stage, distroless</td><td>buildx, Chainguard, Wolfi</td></tr>
<tr><td>Supply chain</td><td>SBOM + Cosign keyless + provenance</td><td>Syft, Cosign, Sigstore</td></tr>
<tr><td>Secrets</td><td>GitHub Environments + OIDC; never long-lived keys</td><td>Environments, Vault, Doppler</td></tr>
<tr><td>Promotion</td><td>Tag &rarr; production environment with manual approval</td><td>environment protection rules</td></tr>
<tr><td>Rollback</td><td>Re-deploy previous image digest from GHCR</td><td>flyctl, gh CLI</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> protect <code>main</code> with required reviews and status checks; use <strong>environments</strong> with required reviewers for production; pin image tags to <strong>digests</strong> in deployment manifests, not floating tags; turn on <strong>Dependabot</strong> + <strong>Renovate</strong> with auto-merge for minor/patch; use <strong>step-security/harden-runner</strong> in audit mode first then enforce egress allow-list; emit traces with <strong>OpenTelemetry</strong> to <strong>Honeycomb</strong>/<strong>Datadog</strong>/<strong>Grafana Cloud</strong>; track DORA metrics (deployment frequency, lead time, MTTR, change-failure rate) automatically via <strong>OpenDORA</strong>/<strong>Sleuth</strong>/<strong>LinearB</strong>; for preview environments per PR use <strong>Fly Machines</strong>/<strong>Render Preview</strong>/<strong>Vercel Preview</strong>; if scale grows beyond a few services consider moving to <strong>Argo CD + GitHub Actions</strong> with <strong>Kustomize</strong> for envs; on AWS prefer <strong>OIDC + IAM Identity Center</strong> + <strong>aws-actions/configure-aws-credentials</strong> for short-lived STS sessions.</p>'''


ANSWERS[2] = r'''<p><strong>Situation:</strong> a team running a single Node.js monolith wants to migrate to <strong>microservices</strong> on Kubernetes &mdash; gradually, without big-bang outages. The CI/CD must handle many repos, fast feedback per service, GitOps-style deploys, and progressive delivery.</p>

<p><strong>Approach:</strong> adopt the <strong>strangler fig pattern</strong>: extract one bounded context at a time behind a routing layer (Envoy, Istio Gateway, or the original monolith reverse-proxying). Each new service gets its own repo with a <strong>GitHub Actions</strong> CI that builds and pushes to <strong>ECR</strong>/<strong>GHCR</strong>/<strong>Artifact Registry</strong>, plus a <strong>config repo</strong> watched by <strong>Argo CD</strong> with <strong>ApplicationSets</strong> for fan-out across environments. Promotion across stages is owned by <strong>Kargo</strong>; canaries by <strong>Argo Rollouts</strong> or <strong>Flagger</strong>. Service discovery and routing via <strong>Istio</strong> or <strong>Linkerd</strong>; observability via <strong>OpenTelemetry</strong> + <strong>Tempo</strong>/<strong>Jaeger</strong>.</p>

<pre><code># config-repo/apps/payments/base/kustomization.yaml
resources: [deployment.yaml, service.yaml, rollout.yaml, hpa.yaml]
images:
  - name: payments
    newTag: PLACEHOLDER  # bumped by service CI

# config-repo/argocd/applicationset.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: services }
spec:
  generators:
    - matrix:
        generators:
          - git:
              repoURL: https://github.com/org/config
              files: [{ path: "apps/*/config.json" }]
          - list:
              elements:
                - { env: staging, cluster: stg }
                - { env: prod,    cluster: prod }
  template:
    metadata: { name: '{{path.basename}}-{{env}}' }
    spec:
      destination: { server: '{{cluster}}', namespace: '{{path.basename}}' }
      source:
        repoURL: https://github.com/org/config
        path: 'apps/{{path.basename}}/overlays/{{env}}'
      syncPolicy: { automated: { prune: true, selfHeal: true } }
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Tools (2026)</th></tr></thead><tbody>
<tr><td>Service onboarding</td><td>Cookiecutter template repo + CODEOWNERS</td><td>Backstage, Port, Cortex</td></tr>
<tr><td>Per-service CI</td><td>Reusable workflow with build/test/scan/sign</td><td>GH Actions reusable workflows</td></tr>
<tr><td>Deploy mechanism</td><td>GitOps; CI bumps image tag in config repo</td><td>Argo CD, Flux</td></tr>
<tr><td>Promotion</td><td>Stage &rarr; canary &rarr; prod via PR</td><td>Kargo, Argo Rollouts, Flagger</td></tr>
<tr><td>Service mesh</td><td>mTLS, retries, timeouts, traffic split</td><td>Istio ambient, Linkerd, Cilium</td></tr>
<tr><td>Data extraction</td><td>Outbox + CDC, dual-writes only as last resort</td><td>Debezium, Conduit, Estuary Flow</td></tr>
<tr><td>Observability</td><td>Distributed traces required from day one</td><td>OpenTelemetry, Tempo, Honeycomb</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> stand up a <strong>developer portal</strong> (<strong>Backstage</strong>/<strong>Port</strong>/<strong>Cortex</strong>) so service owners discover templates, dashboards, and SLOs in one place; enforce architecture rules (deps, ports, auth) via <strong>OPA</strong>/<strong>Kyverno</strong> + <strong>Conftest</strong>; rate-limit at the edge via <strong>Cloudflare</strong>/<strong>Kong</strong>/<strong>Tyk</strong>; instrument the strangler boundary with <strong>OpenTelemetry baggage</strong> so you can trace a request across the legacy monolith and new services; use <strong>contract tests</strong> (<strong>Pact</strong>, <strong>Microcks</strong>) to catch breaking schema changes pre-merge; pair every extraction with a <strong>data ownership doc</strong> and CDC-based dual-read until the new service is canonical; budget for <strong>SLO error budgets</strong> per service so teams own reliability; for K8s itself, <strong>Karpenter</strong> + <strong>KEDA</strong> + <strong>Cilium</strong> are the 2026 baseline; add <strong>Kargo</strong>/<strong>Argo Workflows</strong> for cross-service promotion gates that wait on synthetics or business metrics.</p>'''


ANSWERS[3] = r'''<p><strong>Situation:</strong> a regulated workload runs on Kubernetes; deploys must be <strong>blue-green</strong> with instant rollback, controlled by Jenkins. The team wants the &ldquo;old&rdquo; and &ldquo;new&rdquo; pools running simultaneously, traffic flipped atomically once the new side is verified.</p>

<p><strong>Approach:</strong> the cleanest 2026 implementation is <strong>Argo Rollouts</strong> with <code>strategy.blueGreen</code> rather than rolling your own Service-selector swap. Jenkins remains the orchestrator that builds, tests, signs, and updates the Rollout&rsquo;s image; Argo Rollouts owns the active/preview Services, the analysis runs, the cutover, and the rollback window. If Argo Rollouts isn&rsquo;t available, Jenkins can swap the <code>spec.selector</code> on the production Service between two Deployments labelled <code>color: blue</code> and <code>color: green</code> &mdash; functional but you lose automated analysis and post-promotion scaledown timing.</p>

<pre><code>// Jenkinsfile (Argo Rollouts variant)
pipeline {
  agent { kubernetes { yaml libraryResource('agents/jnlp-kubectl.yaml') } }
  stages {
    stage('Build') { steps { sh 'docker buildx build --push -t $REG/api:$GIT_COMMIT .' } }
    stage('Sign')  { steps { sh 'cosign sign --yes $REG/api:$GIT_COMMIT' } }
    stage('Deploy preview') {
      steps {
        sh 'kubectl argo rollouts set image api api=$REG/api:$GIT_COMMIT -n prod'
        sh 'kubectl argo rollouts status api -n prod --watch=false'
      }
    }
    stage('Verify preview') {
      steps {
        sh 'k6 run --vus 50 --duration 2m smoke.js -e URL=https://preview.api.example.com'
      }
    }
    stage('Promote') {
      input message: 'Cut traffic to green?'
      steps { sh 'kubectl argo rollouts promote api -n prod' }
    }
  }
  post {
    failure { sh 'kubectl argo rollouts abort api -n prod' }
  }
}
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Tools</th></tr></thead><tbody>
<tr><td>Replica management</td><td>Two ReplicaSets owned by Rollout; preview = scaled-up new</td><td>Argo Rollouts</td></tr>
<tr><td>Traffic switch</td><td>Active Service selector swap on promote</td><td>Argo Rollouts, Service mesh hooks</td></tr>
<tr><td>Pre-promotion checks</td><td>AnalysisTemplate against Prometheus / Datadog / NR</td><td>Prometheus Operator, Datadog</td></tr>
<tr><td>Smoke tests</td><td>Run against preview Service URL before flip</td><td>k6, Playwright, Postman</td></tr>
<tr><td>Rollback window</td><td><code>scaleDownDelaySeconds</code> keeps blue alive after flip</td><td>Argo Rollouts</td></tr>
<tr><td>DB schema</td><td>Expand/contract; never destructive in same release</td><td>Atlas, Flyway, Liquibase</td></tr>
<tr><td>Cost</td><td>2x compute during overlap; budget &amp; alert</td><td>Kubecost, OpenCost</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> wire <strong>AnalysisTemplate</strong> queries against Prometheus to auto-abort if p99 latency, error rate, or saturation breach SLO during the verification window; use <strong>experiment</strong> CRD if you want to mirror traffic to preview before flipping; never schema-migrate in the same release as a code change &mdash; do <strong>expand</strong> (additive migration) one release ahead, then <strong>contract</strong> (drop old columns) one release behind, so blue and green can both run against the live schema; pair the Rollout with a <strong>PodDisruptionBudget</strong> and <strong>topologySpreadConstraints</strong> for AZ resilience; export Rollout events to <strong>Datadog</strong>/<strong>Honeycomb</strong> as deployment markers; if you can&rsquo;t afford 2x compute, use <strong>canary</strong> with weighted routing instead of pure blue-green &mdash; Argo Rollouts supports both with the same primitives, and <strong>Flagger</strong> is the closest alternative if you&rsquo;re on a Flux/Linkerd stack.</p>'''


ANSWERS[4] = r'''<p><strong>Situation:</strong> the security team needs <strong>shift-left</strong> security on every PR &mdash; SAST, secret scanning, dependency scanning, container scanning, IaC checks, and signed releases &mdash; without making CI miserably slow. Implementation must use GitHub Actions and integrate with the existing GitHub Advanced Security tier.</p>

<p><strong>Approach:</strong> stack <strong>CodeQL</strong> for SAST, <strong>Dependabot</strong> + <strong>OSV-Scanner</strong> for SCA, <strong>gitleaks</strong>/<strong>trufflehog</strong> for secrets, <strong>Trivy</strong>/<strong>Grype</strong> for containers, <strong>Checkov</strong>/<strong>tfsec</strong> for IaC, <strong>Semgrep</strong> for custom rules, and <strong>Cosign</strong>+<strong>SLSA</strong> generators for release attestation. Run cheap fast checks (lint, secrets) in PR jobs; offload heavyweight scans (CodeQL full analysis) to scheduled or push-only events; gate merges via required status checks.</p>

<pre><code>name: security
on:
  pull_request:
  push: { branches: [main] }
  schedule: [{ cron: '0 6 * * 1' }]
permissions: { contents: read, security-events: write, id-token: write }
jobs:
  secrets:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
  codeql:
    if: github.event_name != 'pull_request' || contains(github.event.pull_request.labels.*.name, 'codeql')
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: 'javascript,python', queries: security-extended }
      - uses: github/codeql-action/analyze@v3
  semgrep:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with: { config: 'p/owasp-top-ten p/r2c-security-audit' }
  deps:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: google/osv-scanner-action@v1
        with: { scan-args: --recursive --skip-git ./ }
  container:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: sarif
          exit-code: 1
          severity: CRITICAL,HIGH
          output: trivy.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: trivy.sarif }
  iac:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@master
</code></pre>

<table><thead><tr><th>Layer</th><th>Tools</th><th>When it runs</th></tr></thead><tbody>
<tr><td>Secrets</td><td>gitleaks, trufflehog</td><td>Every PR (cheap)</td></tr>
<tr><td>SAST</td><td>CodeQL, Semgrep</td><td>Push to main + scheduled (heavy)</td></tr>
<tr><td>SCA</td><td>OSV-Scanner, Dependabot, Snyk</td><td>Every PR + scheduled</td></tr>
<tr><td>Container</td><td>Trivy, Grype, Snyk</td><td>Post-build</td></tr>
<tr><td>IaC</td><td>Checkov, tfsec, kube-linter, Kyverno-CLI</td><td>Every PR</td></tr>
<tr><td>Signing</td><td>Cosign keyless, SLSA generator</td><td>On release</td></tr>
<tr><td>Runtime</td><td>Falco, Tetragon (post-deploy)</td><td>Continuous</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> require <strong>SARIF upload</strong> for every scanner so findings consolidate in <strong>GitHub Code Scanning</strong> with one triage UI; use <strong>severity-based gating</strong> (block CRITICAL/HIGH only) to avoid scanner fatigue; turn on <strong>step-security/harden-runner</strong> with an egress allow-list so a compromised dependency can&rsquo;t exfiltrate; sign every release with <strong>Cosign keyless</strong> (Sigstore Fulcio + Rekor) and produce <strong>SLSA Level 3</strong> provenance via <strong>slsa-github-generator</strong>; verify signatures at admission with <strong>Kyverno</strong> or <strong>Sigstore Policy Controller</strong>; pair with <strong>Falco</strong> or <strong>Tetragon</strong> for runtime threat detection; track findings in <strong>GitHub Security Center</strong> or <strong>DefectDojo</strong>; for compliance evidence, automate ATO/SOC2 controls via <strong>Vanta</strong>/<strong>Drata</strong>/<strong>Secureframe</strong>/<strong>Anecdotes</strong>; budget security checks against build time &mdash; if scans dominate, parallelise jobs and use scheduled deeper analyses rather than blocking every PR with the full battery.</p>'''


ANSWERS[5] = r'''<p><strong>Situation:</strong> a Kubernetes cluster hosts production workloads in one region; leadership wants a documented <strong>disaster recovery</strong> plan that covers cluster loss, AZ failure, accidental deletion, and data corruption, with explicit RTO/RPO targets.</p>

<p><strong>Approach:</strong> DR for K8s splits into three layers &mdash; <strong>cluster state</strong> (etcd), <strong>workload manifests</strong> (Git, the source of truth via GitOps), and <strong>persistent data</strong> (PVs and external databases). Use <strong>GitOps</strong> with <strong>Argo CD</strong>/<strong>Flux</strong> so re-creating workloads in a new cluster is a single bootstrap; back up volumes with <strong>Velero</strong> + <strong>CSI snapshots</strong>; managed cloud DBs (<strong>RDS Aurora</strong>, <strong>CloudSQL</strong>, <strong>Atlas</strong>) handle their own PITR. Run <strong>Cluster API (CAPI)</strong> to spin up replacement clusters declaratively, or pre-provision a warm standby in a second region.</p>

<pre><code># Velero schedule for hourly cluster-wide backup
apiVersion: velero.io/v1
kind: Schedule
metadata: { name: hourly, namespace: velero }
spec:
  schedule: "0 * * * *"
  template:
    ttl: 168h
    includedNamespaces: ["*"]
    excludedResources: ["events", "events.events.k8s.io"]
    storageLocation: aws-primary
    snapshotVolumes: true
    defaultVolumesToFsBackup: false   # use CSI snapshots
    hooks:
      resources:
        - name: db-quiesce
          includedNamespaces: [postgres]
          labelSelector: { matchLabels: { app: postgres } }
          pre:
            - exec:
                container: postgres
                command: ["/bin/sh", "-c", "psql -c CHECKPOINT"]
---
# Periodic restore drill (separate cluster) via CAPI bootstrap then velero restore
</code></pre>

<table><thead><tr><th>Failure mode</th><th>RPO target</th><th>RTO target</th><th>Mechanism</th></tr></thead><tbody>
<tr><td>Single AZ loss</td><td>0</td><td>&lt; 5 min</td><td>topology spread + multi-AZ control plane (managed K8s)</td></tr>
<tr><td>Cluster loss</td><td>1 hour</td><td>&lt; 1 hour</td><td>CAPI re-provision + Argo CD bootstrap + Velero restore</td></tr>
<tr><td>Region loss</td><td>5 min</td><td>&lt; 30 min</td><td>Pre-warmed second region + DB cross-region replica</td></tr>
<tr><td>Accidental delete</td><td>0</td><td>&lt; 15 min</td><td>Argo CD self-heal + Velero point-in-time restore</td></tr>
<tr><td>Data corruption</td><td>15 min</td><td>varies</td><td>DB PITR + Velero snapshot rollback</td></tr>
<tr><td>Ransomware</td><td>24 hr</td><td>varies</td><td>Immutable backups (Object Lock); air-gapped copy</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> never test DR by reading the runbook &mdash; schedule a quarterly <strong>Game Day</strong> where you destroy a staging cluster and rebuild it from Git + Velero; track <strong>actual</strong> RTO/RPO from those drills, not aspirational targets; use <strong>S3 Object Lock</strong>/<strong>GCS retention policies</strong>/<strong>Azure immutable blob</strong> on the backup bucket so ransomware can&rsquo;t encrypt your backups; keep <strong>Argo CD</strong>&rsquo;s own state in a separate cluster (or use the <strong>Argo CD Autopilot</strong> bootstrap pattern) so you can rebuild it without bootstrapping itself; managed databases get cross-region replicas (<strong>Aurora Global</strong>, <strong>Atlas Global Clusters</strong>, <strong>Spanner multi-region</strong>) &mdash; fail over with <strong>Route 53</strong>/<strong>Cloudflare</strong> health checks; for stateful K8s workloads consider <strong>Stash</strong> or <strong>Kasten K10</strong> (Veeam) which add application-aware backups; document the bootstrap order (cluster &rarr; storage classes &rarr; cert-manager &rarr; ingress &rarr; Argo CD &rarr; apps) and automate it with a single <strong>argocd-autopilot</strong> repo so a fresh region rebuild is one command, not a heroic effort.</p>'''


ANSWERS[6] = r'''<p><strong>Situation:</strong> a platform team wants <strong>GitOps</strong> for Kubernetes &mdash; manifests live in Git, a controller in the cluster reconciles state &mdash; with GitHub Actions handling CI (build/test/scan) and image bumps. The goal is auditability, easy rollback, and zero direct <code>kubectl apply</code> in production.</p>

<p><strong>Approach:</strong> use <strong>Argo CD</strong> as the in-cluster reconciler watching a dedicated <strong>config repo</strong> (separate from app source for blast-radius reasons). Application repos run <strong>GitHub Actions</strong> that build/test/scan/sign images and then open a PR (or auto-commit) to bump the image tag in the config repo. <strong>Argo CD ApplicationSets</strong> generate the per-environment Applications; <strong>Kargo</strong> handles promotion across stages with verification gates.</p>

<pre><code># app repo: .github/workflows/release.yml (excerpt)
- name: Build &amp; push
  uses: docker/build-push-action@v6
  with: { push: true, tags: $REG/api:${{ github.sha }}, provenance: true, sbom: true }
- name: Sign
  run: cosign sign --yes $REG/api:${{ github.sha }}
- name: Bump tag in config repo
  uses: peter-evans/repository-dispatch@v3
  with:
    token: ${{ secrets.CONFIG_REPO_PAT }}
    repository: org/config
    event-type: image-bump
    client-payload: |
      { "service": "api", "image": "$REG/api@sha256:${{ steps.build.outputs.digest }}",
        "env": "staging", "actor": "${{ github.actor }}", "sha": "${{ github.sha }}" }

# config repo: workflow that handles image-bump dispatch
on: { repository_dispatch: { types: [image-bump] } }
jobs:
  bump:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: mikefarah/yq@v4
        with: { cmd: "yq -i '.images[0].newName=\"${{ github.event.client_payload.image }}\"' apps/${{ github.event.client_payload.service }}/overlays/${{ github.event.client_payload.env }}/kustomization.yaml" }
      - uses: peter-evans/create-pull-request@v6
        with: { title: 'bump api to ${{ github.event.client_payload.sha }}', branch: bump-${{ github.event.client_payload.sha }} }
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Tools</th></tr></thead><tbody>
<tr><td>Source of truth</td><td>Config repo, separate from app code</td><td>GitHub, Argo CD</td></tr>
<tr><td>Sync mode</td><td>Auto-sync + self-heal in dev/staging; manual approve in prod</td><td>Argo CD sync policies</td></tr>
<tr><td>Image bump</td><td>CI commits/PR to config repo with digest reference</td><td>peter-evans/create-pull-request</td></tr>
<tr><td>Promotion</td><td>Stage &rarr; canary &rarr; prod with verification</td><td>Kargo, Argo Rollouts, Flagger</td></tr>
<tr><td>Drift detection</td><td>Argo CD self-heal + alerts</td><td>Argo CD Notifications, Slack</td></tr>
<tr><td>Secret management</td><td>External Secrets Operator + Vault/AWS SM</td><td>ESO, Vault, Sealed Secrets</td></tr>
<tr><td>Auth</td><td>SSO + RBAC; GitHub teams &rarr; AppProject roles</td><td>Argo CD AppProjects, Dex</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> always reference images by <strong>digest</strong> (<code>image@sha256:...</code>) not tag &mdash; tags are mutable, digests are not; sign images with <strong>Cosign</strong> and verify at admission via <strong>Kyverno</strong> or <strong>Sigstore Policy Controller</strong>; use <strong>External Secrets Operator</strong> with <strong>Vault</strong>/<strong>AWS Secrets Manager</strong>/<strong>GCP Secret Manager</strong> rather than committing encrypted blobs (Sealed Secrets is acceptable for small teams); use <strong>Argo CD ApplicationSets</strong> with cluster generators for fleet management; install <strong>argocd-image-updater</strong> if you prefer pull-based image bumps; for compliance, enable Argo CD&rsquo;s <strong>resource history</strong> and ship audit logs to <strong>Loki</strong>/<strong>OpenSearch</strong>; pair with <strong>Kargo</strong> for stage-aware promotion that validates synthetics before opening the next PR; for very large teams shard Argo CD with multiple <strong>application-controller</strong> replicas (one per ~100 apps) and a Redis cache, and use <strong>repo-server</strong> manifest caching aggressively.</p>'''


ANSWERS[7] = r'''<p><strong>Situation:</strong> a Python web service needs CI/CD with three test stages (unit, integration with Postgres+Redis, contract) and deployment to <strong>AWS Lambda</strong> via API Gateway. The team wants per-PR preview environments and automatic rollback on errors.</p>

<p><strong>Approach:</strong> use <strong>GitHub Actions</strong> with services containers for integration tests, package the Lambda with <strong>AWS SAM</strong> or <strong>AWS CDK</strong>, and rely on <strong>OIDC</strong> for cloud auth. Use <strong>Powertools for AWS Lambda (Python)</strong> for tracing/logging/idempotency, deploy to a stage alias, then use <strong>CodeDeploy</strong> with linear or canary traffic shifting and <strong>CloudWatch alarms</strong> as automated rollback triggers.</p>

<pre><code>name: ci-cd
on: { push: { branches: [main] }, pull_request: }
permissions: { id-token: write, contents: read, pull-requests: write }
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres: { image: postgres:16, env: { POSTGRES_PASSWORD: pw }, ports: ["5432:5432"], options: --health-cmd=pg_isready }
      redis:    { image: redis:7.4,  ports: ["6379:6379"] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.13', cache: pip }
      - run: pip install -e .[test]
      - run: ruff check . &amp;&amp; mypy src
      - run: pytest tests/unit --cov=src --cov-report=xml
      - run: pytest tests/integration
        env: { DATABASE_URL: postgresql://postgres:pw@localhost/test, REDIS_URL: redis://localhost }
      - run: pytest tests/contract
      - uses: codecov/codecov-action@v4
  deploy:
    needs: test
    runs-on: ubuntu-24.04
    environment: ${{ github.event_name == 'pull_request' &amp;&amp; format('preview-{0}', github.event.number) || 'prod' }}
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123:role/gha, aws-region: us-east-1 }
      - uses: aws-actions/setup-sam@v2
        with: { use-installer: true }
      - run: sam build --use-container
      - run: |
          STACK=api-${{ github.event_name == 'pull_request' &amp;&amp; format('pr-{0}', github.event.number) || 'prod' }}
          sam deploy --stack-name $STACK --no-confirm-changeset --resolve-s3 \
            --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset \
            --parameter-overrides Stage=$STACK
</code></pre>

<table><thead><tr><th>Stage</th><th>What it validates</th><th>Tools</th></tr></thead><tbody>
<tr><td>Lint/type</td><td>Style + static type errors</td><td>Ruff, mypy, pyright</td></tr>
<tr><td>Unit</td><td>Pure functions and isolated logic</td><td>pytest, hypothesis</td></tr>
<tr><td>Integration</td><td>DB queries, Redis, external clients</td><td>pytest + service containers</td></tr>
<tr><td>Contract</td><td>API consumers don&rsquo;t break</td><td>Pact, schemathesis</td></tr>
<tr><td>Deploy</td><td>Stage-pinned alias + traffic shift</td><td>SAM, CodeDeploy</td></tr>
<tr><td>Auto-rollback</td><td>CloudWatch alarms during shift</td><td>CodeDeploy hooks, alarms</td></tr>
<tr><td>Preview env</td><td>Per-PR stack with cleanup on close</td><td>GH Environments, sam delete</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> use <strong>Powertools for AWS Lambda</strong> for structured logs (Logger), distributed tracing (Tracer with X-Ray or OTEL), and <strong>idempotency</strong> &mdash; the last is critical for SQS/Kinesis triggers; turn on <strong>SnapStart</strong> for Java/.NET/Python (3.13+) to slash cold-start latency; ship logs and metrics to <strong>Datadog</strong>/<strong>New Relic</strong>/<strong>Grafana Cloud</strong> via the <strong>OpenTelemetry Lambda layer</strong> or a forwarder Lambda; instrument <strong>Lambda Insights</strong> for runtime metrics; use <strong>Provisioned Concurrency</strong> only for latency-critical paths (cost trade-off); for preview environments tear them down on PR close via a <code>workflow: closed</code> job calling <code>sam delete</code>; for schema-driven contract tests <strong>schemathesis</strong> auto-generates property-based tests from OpenAPI; pin Python deps via <code>uv pip compile</code> with hashes; use <strong>aws-actions/configure-aws-credentials</strong> with role-session tagging so you can audit which workflow assumed which role.</p>'''


ANSWERS[8] = r'''<p><strong>Situation:</strong> a team wants <strong>canary deployments</strong> on Kubernetes &mdash; route a small percentage of traffic to the new version, watch metrics, increase the percentage if healthy, abort if not. Jenkins is the existing CI/CD orchestrator.</p>

<p><strong>Approach:</strong> the right primitive is <strong>Argo Rollouts</strong> with <code>strategy.canary</code> &mdash; Jenkins drives the build and image push, Argo Rollouts owns the traffic-shifting state machine. For traffic management, Argo Rollouts integrates with <strong>Istio</strong>, <strong>Linkerd</strong>, <strong>Traefik</strong>, <strong>Nginx</strong>, <strong>SMI</strong>, <strong>AWS ALB</strong>, and <strong>Gateway API</strong>; pick whichever matches your existing mesh/ingress. Add <strong>AnalysisTemplate</strong> queries against <strong>Prometheus</strong>, <strong>Datadog</strong>, or <strong>New Relic</strong> for automated promotion/abort.</p>

<pre><code># Rollout: 5% &rarr; 25% &rarr; 50% &rarr; 100% with metric-gated steps
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: api }
spec:
  replicas: 10
  strategy:
    canary:
      canaryService: api-canary
      stableService: api-stable
      trafficRouting:
        istio:
          virtualService: { name: api, routes: [primary] }
      steps:
        - setWeight: 5
        - pause: { duration: 5m }
        - analysis: { templates: [{ templateName: success-rate }] }
        - setWeight: 25
        - pause: { duration: 10m }
        - analysis: { templates: [{ templateName: success-rate }, { templateName: latency }] }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: success-rate }
spec:
  metrics:
    - name: success-rate
      interval: 1m
      successCondition: result[0] &gt;= 0.99
      failureLimit: 2
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{service="api",status!~"5.."}[2m]))
            / sum(rate(http_requests_total{service="api"}[2m]))
</code></pre>

<table><thead><tr><th>Step</th><th>Owner</th><th>Action</th></tr></thead><tbody>
<tr><td>Build/test/sign</td><td>Jenkins</td><td>Standard pipeline + push image</td></tr>
<tr><td>Image bump</td><td>Jenkins</td><td><code>kubectl argo rollouts set image</code></td></tr>
<tr><td>Traffic split</td><td>Argo Rollouts</td><td>Update VirtualService weights</td></tr>
<tr><td>Metric checks</td><td>AnalysisTemplate</td><td>Prom/Datadog query at each step</td></tr>
<tr><td>Auto-abort</td><td>Argo Rollouts</td><td>On analysis failure or manual</td></tr>
<tr><td>Promotion</td><td>Argo Rollouts</td><td>setWeight: 100 + scaleDown old RS</td></tr>
<tr><td>Notifications</td><td>Argo Rollouts &rarr; Slack</td><td>argo-rollouts-notifications</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> tie analysis templates to the metrics you actually pay attention to in incidents &mdash; success rate, p99 latency, saturation &mdash; and set <code>failureLimit</code> so a single transient blip doesn&rsquo;t abort; use <strong>experiment</strong> CRD to mirror a small percentage of traffic to the canary without user impact, useful for read-only request validation; for stateful concerns (cookies, sessions) configure <strong>session affinity</strong> on the canary VirtualService so a user doesn&rsquo;t bounce between versions; pair with <strong>SLO error budgets</strong> &mdash; if you&rsquo;re burning budget, slow promotion automatically; <strong>Flagger</strong> is the Flux-stack equivalent and ties into <strong>Linkerd</strong>/<strong>Istio</strong>/<strong>App Mesh</strong>; for non-mesh setups <strong>Argo Rollouts</strong> can manipulate <strong>Nginx</strong> ingress weights directly via the <code>nginx</code> trafficRouting; emit <strong>OpenTelemetry</strong> deployment markers so traces are filterable by canary vs stable; document the abort runbook &mdash; <code>kubectl argo rollouts abort api</code> reverts traffic in seconds, but humans need to know the command exists at 3am.</p>'''


ANSWERS[9] = r'''<p><strong>Situation:</strong> a Jenkins controller has accumulated years of plugin configs, credentials, jobs, and shared library bindings. A disk failure or accidental config wipe would be catastrophic; backups must be automated, tested, and version-controlled.</p>

<p><strong>Approach:</strong> the right answer in 2026 is <strong>Configuration as Code (JCasC)</strong> + Git, not file-system snapshots. Convert the Jenkins controller config to a <code>jenkins.yaml</code> committed to a config repo; manage plugins via <code>plugins.txt</code> with the <strong>jenkins-plugin-cli</strong>; manage jobs via the <strong>job-dsl</strong> plugin or in JCasC itself. Run Jenkins in a container (or via the <strong>Jenkins Operator</strong> on K8s) so the controller is reproducible from Git in minutes. For job history, build artefacts, and credentials, periodic file-system backups still matter &mdash; use <strong>thinBackup</strong> or a sidecar that snapshots <code>$JENKINS_HOME</code> to S3 with versioning + Object Lock.</p>

<pre><code># Dockerfile for reproducible controller
FROM jenkins/jenkins:lts-jdk21
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt
COPY jenkins.yaml /var/jenkins_home/casc_configs/jenkins.yaml
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# K8s CronJob for $JENKINS_HOME snapshot to S3 with object lock
apiVersion: batch/v1
kind: CronJob
metadata: { name: jenkins-backup, namespace: jenkins }
spec:
  schedule: "0 */6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: jenkins-backup
          containers:
            - name: rclone
              image: rclone/rclone:1.68
              command: ["sh", "-c"]
              args:
                - |
                  rclone copy --exclude 'workspace/**' --exclude 'caches/**' \
                    /var/jenkins_home s3:my-jenkins-backups/$(date -u +%Y-%m-%dT%H)
              volumeMounts:
                - { name: jenkins-home, mountPath: /var/jenkins_home, readOnly: true }
          volumes:
            - { name: jenkins-home, persistentVolumeClaim: { claimName: jenkins-home } }
          restartPolicy: OnFailure
</code></pre>

<table><thead><tr><th>Layer</th><th>Backup mechanism</th><th>Notes</th></tr></thead><tbody>
<tr><td>Controller config</td><td>JCasC <code>jenkins.yaml</code> in Git</td><td>Reproducible, reviewable</td></tr>
<tr><td>Plugins</td><td><code>plugins.txt</code> pinned in Git</td><td>Use BOM with jenkins-plugin-cli</td></tr>
<tr><td>Job definitions</td><td>job-dsl scripts or pipeline-as-code</td><td>Multibranch reads Jenkinsfile from SCM</td></tr>
<tr><td>Credentials</td><td>External Vault/AWS SM</td><td>Never in $JENKINS_HOME</td></tr>
<tr><td>Build history</td><td>$JENKINS_HOME snapshot</td><td>Every 6h to S3 + Object Lock</td></tr>
<tr><td>Artefacts</td><td>External S3/Artifactory</td><td>Don&rsquo;t store on controller disk</td></tr>
<tr><td>Restore drill</td><td>Quarterly Game Day</td><td>Provision blank, restore, verify</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> stop storing credentials in <code>$JENKINS_HOME</code> &mdash; use <strong>HashiCorp Vault</strong>, <strong>AWS Secrets Manager</strong>, <strong>GCP Secret Manager</strong>, or <strong>Doppler</strong> via the appropriate Jenkins credential provider; pin every plugin to a tested version (snapshot the BOM in Git); use the <strong>Jenkins Operator</strong> on Kubernetes &mdash; it owns the controller via CRDs and reconciles drift, so re-creating is one <code>kubectl apply</code>; on AWS use <strong>S3 Versioning</strong> + <strong>Object Lock</strong> + cross-region replication so a ransomware event can&rsquo;t encrypt your backups; verify backups by running a quarterly restore drill into a staging cluster (test what you actually rely on); export controller logs to <strong>Loki</strong>/<strong>OpenSearch</strong>/<strong>Datadog</strong> rather than relying on local files; on the migration question &mdash; many teams in 2026 use this Jenkins refresh as a moment to evaluate <strong>GitHub Actions</strong>, <strong>Buildkite</strong>, <strong>CircleCI</strong>, or <strong>Tekton</strong>; if you stay on Jenkins, <strong>JCasC</strong> + <strong>Operator</strong> is the only sustainable shape.</p>'''


ANSWERS[10] = r'''<p><strong>Situation:</strong> the company is going <strong>multi-cloud</strong> &mdash; AWS for some workloads, Azure for others, with a longer-term plan to deploy critical services in both for vendor independence. The CI/CD pipeline must build once and ship the same artefacts to either cloud.</p>

<p><strong>Approach:</strong> use cloud-neutral primitives wherever possible &mdash; <strong>OCI containers</strong> as the universal artefact, <strong>Kubernetes</strong> as the universal runtime (EKS on AWS, AKS on Azure), <strong>Crossplane</strong> or <strong>Terraform/OpenTofu</strong> for IaC across clouds, and <strong>Argo CD ApplicationSets</strong> for fleet GitOps. Build once in <strong>GitHub Actions</strong>, push to a registry replicated across clouds (<strong>Harbor</strong> with replication, or push to both <strong>ECR</strong> and <strong>ACR</strong>), and use <strong>OIDC</strong> against each cloud&rsquo;s IAM.</p>

<pre><code>name: multi-cloud-deploy
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  build:
    runs-on: ubuntu-24.04
    outputs: { digest: ${{ steps.push.outputs.digest }} }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v6
        id: push
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          provenance: true
          sbom: true
      - run: cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.push.outputs.digest }}
  mirror:
    needs: build
    runs-on: ubuntu-24.04
    strategy: { matrix: { target: [aws, azure] } }
    steps:
      - uses: actions/checkout@v4
      - if: matrix.target == 'aws'
        uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123:role/gha, aws-region: us-east-1 }
      - if: matrix.target == 'azure'
        uses: azure/login@v2
        with: { client-id: ${{ secrets.AZ_CLIENT_ID }}, tenant-id: ${{ secrets.AZ_TENANT }}, subscription-id: ${{ secrets.AZ_SUB }} }
      - if: matrix.target == 'aws'
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ECR
          crane copy ghcr.io/${{ github.repository }}@${{ needs.build.outputs.digest }} $AWS_ECR/api@${{ needs.build.outputs.digest }}
      - if: matrix.target == 'azure'
        run: |
          az acr login --name myacr
          crane copy ghcr.io/${{ github.repository }}@${{ needs.build.outputs.digest }} myacr.azurecr.io/api@${{ needs.build.outputs.digest }}
  bump-config:
    needs: mirror
    runs-on: ubuntu-24.04
    steps:
      - run: |
          # bump per-cloud kustomization with the digest in config repo
          # Argo CD ApplicationSet then syncs to each cluster
</code></pre>

<table><thead><tr><th>Concern</th><th>Cloud-neutral choice</th><th>Trade-off</th></tr></thead><tbody>
<tr><td>Compute</td><td>K8s (EKS + AKS)</td><td>Common API; managed flavours diverge subtly</td></tr>
<tr><td>Identity</td><td>OIDC + per-cloud IAM</td><td>Two trust relationships to maintain</td></tr>
<tr><td>IaC</td><td>OpenTofu, Pulumi, Crossplane</td><td>Crossplane unifies via K8s CRDs; learning curve</td></tr>
<tr><td>Storage</td><td>App-level abstraction (S3 API via MinIO/CrossCloud)</td><td>Egress costs cross-cloud are real</td></tr>
<tr><td>DB</td><td>Postgres-compatible (RDS/Flexible Server) or distributed (CockroachDB, YugabyteDB, Spanner)</td><td>Active-active is hard; usually pick a primary cloud</td></tr>
<tr><td>Secrets</td><td>External Secrets Operator + per-cloud backend</td><td>Two backends; ESO unifies the K8s view</td></tr>
<tr><td>Observability</td><td>OpenTelemetry &rarr; Datadog/Grafana Cloud</td><td>Avoid CloudWatch/Azure Monitor lock-in</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> be honest with yourself about <em>why</em> you&rsquo;re multi-cloud &mdash; vendor independence costs real money in egress, dual-stack expertise, and complexity; the answer is rarely &ldquo;active-active across both at all times&rdquo; but more often &ldquo;active in one, ready to fail over to the other in a regional disaster&rdquo;; that operationally simpler shape (<strong>active/passive</strong>) avoids most cross-cloud data plane pain; for IaC, <strong>OpenTofu</strong> with cloud-specific modules + <strong>Atlantis</strong>/<strong>Spacelift</strong>/<strong>Terraform Cloud</strong>/<strong>env0</strong> for orchestration; for K8s standardise <strong>Cilium</strong> as CNI for consistent NetworkPolicy and Hubble observability; <strong>Karpenter</strong> is now GA on both AWS and Azure so node provisioning is the same primitive; for the registry, <strong>Harbor</strong> with replication or <strong>ORAS</strong>-based sync between ECR and ACR via <strong>regclient</strong>/<strong>crane</strong>; document the data residency story per workload &mdash; some workloads must live in one cloud only for regulatory reasons.</p>'''

ANSWERS[11] = r'''<p><strong>Situation:</strong> Docker image builds are taking 15&ndash;20 minutes in CI &mdash; node_modules and pip caches reinstall from scratch every run, layers don&rsquo;t cache, and the resulting image is 1.5 GB. The team needs builds under 3 minutes and images under 200 MB without changing the application.</p>

<p><strong>Approach:</strong> the wins stack across four levers &mdash; <strong>BuildKit</strong> features (cache mounts, parallel stages), <strong>multi-stage</strong> builds with a slim final image, <strong>layer ordering</strong> so dep installs cache properly, and <strong>distributed cache</strong> via GHA cache, registry cache, or a managed builder like <strong>Depot</strong>/<strong>Namespace</strong>/<strong>Blacksmith</strong>. Switch the base image to <strong>Chainguard</strong> or <strong>distroless</strong> for the final stage. For monorepos, <strong>Bake</strong> with parallel targets unblocks otherwise-serial work.</p>

<pre><code># syntax=docker/dockerfile:1.7
FROM node:22-bookworm AS deps
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --include=dev

FROM deps AS build
COPY . .
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/.next/cache \
    npm run build &amp;&amp; npm prune --omit=dev

FROM cgr.dev/chainguard/node:latest
WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER nonroot
ENTRYPOINT ["node", "dist/server.js"]

# .github/workflows/build.yml
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v6
  with:
    push: true
    tags: ghcr.io/org/api:${{ github.sha }}
    cache-from: type=gha,scope=api
    cache-to: type=gha,mode=max,scope=api
    platforms: linux/amd64,linux/arm64
    provenance: true
    sbom: true
</code></pre>

<table><thead><tr><th>Lever</th><th>What it changes</th><th>Typical win</th></tr></thead><tbody>
<tr><td>BuildKit cache mounts</td><td>Pip/npm/apt caches survive across runs</td><td>40&ndash;70% on dep-heavy builds</td></tr>
<tr><td>Layer ordering</td><td>COPY package.json before COPY .</td><td>10&ndash;90% on no-dep-change rebuilds</td></tr>
<tr><td>Multi-stage + distroless</td><td>Drop dev tools and shells from final image</td><td>5&ndash;10x size reduction</td></tr>
<tr><td>GHA cache (type=gha)</td><td>Cross-run cache, scoped per workflow</td><td>2&ndash;5x cold-cache scenarios</td></tr>
<tr><td>Registry cache</td><td>Cache layers in the registry itself</td><td>Useful across multiple runners</td></tr>
<tr><td>Managed builders</td><td>Depot/Namespace/Blacksmith persistent volume</td><td>2&ndash;4x vs GHA cache</td></tr>
<tr><td>Bake parallelism</td><td>Multi-target builds in parallel</td><td>2&ndash;3x for monorepos</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> always use <code>--mount=type=cache</code> for package managers (npm, pip, apt, go mod, cargo); switch the final stage to <strong>Chainguard</strong>/<strong>Wolfi</strong>/<strong>distroless</strong> images &mdash; smaller, fewer CVEs, fewer scanners screaming; use the <strong>build-push-action</strong> with <code>provenance: true</code> and <code>sbom: true</code> for free supply-chain hygiene; on monorepos use <strong>Docker Bake</strong> + a <code>docker-bake.hcl</code> with shared <code>contexts</code> so common base images build once; for heavy CI use <strong>Depot</strong> or <strong>Namespace</strong> &mdash; persistent BuildKit volumes blow GHA cache out of the water and pay for themselves quickly; consider <strong>buildah</strong> or <strong>kaniko</strong> only if you need rootless builds inside Kubernetes; profile slow builds with <code>BUILDKIT_PROGRESS=plain</code> and <code>--push</code> output to find which step actually dominates &mdash; the answer is often a single <code>RUN apt-get update</code> that invalidates everything below it.</p>'''


ANSWERS[12] = r'''<p><strong>Situation:</strong> a React SPA needs a CD workflow on GitHub Actions &mdash; lint and test on every PR, build and deploy to <strong>Vercel</strong>/<strong>Netlify</strong>/<strong>Cloudflare Pages</strong>/<strong>S3+CloudFront</strong> on merge to main, with preview environments per PR, atomic deploys, and instant rollback.</p>

<p><strong>Approach:</strong> static SPAs love edge platforms because they handle preview deploys, atomic rollouts, and rollback as first-class features &mdash; the GH Actions workflow becomes a thin glue layer. For a Vite + React app, build once, run unit tests with <strong>Vitest</strong>, run E2E with <strong>Playwright</strong>, then deploy via the platform&rsquo;s official action. Use <strong>Cloudflare Pages</strong> if you want global edge by default, <strong>Vercel</strong> if you want best-in-class DX with framework-specific optimisations, or <strong>S3 + CloudFront + OAC</strong> if you must stay in AWS.</p>

<pre><code>name: cd-react
on: { push: { branches: [main] }, pull_request: }
permissions: { id-token: write, contents: read, pull-requests: write, deployments: write }
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run test -- --coverage
      - uses: actions/upload-artifact@v4
        with: { name: coverage, path: coverage }
  build:
    needs: test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci &amp;&amp; npm run build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist }
  e2e:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: dist, path: dist }
      - run: npx playwright install --with-deps
      - run: npx serve dist &amp; sleep 2
      - run: npx playwright test
  deploy:
    needs: e2e
    runs-on: ubuntu-24.04
    environment: ${{ github.event_name == 'pull_request' &amp;&amp; 'preview' || 'production' }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: dist, path: dist }
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          command: pages deploy dist --project-name=app --branch=${{ github.head_ref || 'main' }}
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Tools</th></tr></thead><tbody>
<tr><td>Preview per PR</td><td>Branch deploys auto-comment URL on PR</td><td>Cloudflare Pages, Vercel, Netlify</td></tr>
<tr><td>Atomic deploy</td><td>New version on a fresh deployment ID; flip alias</td><td>All edge platforms support this</td></tr>
<tr><td>Rollback</td><td>Promote a previous deployment</td><td>Platform UI / CLI</td></tr>
<tr><td>E2E gate</td><td>Playwright + Lighthouse CI before deploy</td><td>microsoft/playwright-github-action</td></tr>
<tr><td>SPA routing</td><td>SPA fallback to index.html on 404</td><td>_redirects, vercel.json rewrites</td></tr>
<tr><td>API auth</td><td>OIDC for AWS S3, platform tokens elsewhere</td><td>configure-aws-credentials@v4</td></tr>
<tr><td>Cache busting</td><td>Hashed filenames + long Cache-Control</td><td>Vite/Webpack default</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> set <strong>Content Security Policy</strong> headers via the platform&rsquo;s response headers config (Vercel <code>headers</code>, Cloudflare Pages <code>_headers</code>) &mdash; reflects supply-chain best practice; instrument <strong>Real User Monitoring</strong> with <strong>Vercel Analytics</strong>, <strong>Cloudflare Web Analytics</strong>, <strong>SpeedCurve</strong>, or <strong>Datadog RUM</strong> &mdash; track <strong>INP</strong>, <strong>LCP</strong>, <strong>CLS</strong> directly because they correlate with conversion; run <strong>Lighthouse CI</strong> in the workflow with budgets so PRs that regress performance fail the check; turn on <strong>Renovate</strong>/<strong>Dependabot</strong> for npm; for E2E split tests into shards across the matrix to keep wall-clock under 5 minutes; for non-Cloudflare options, <strong>Vercel</strong> integrates the deepest with Next.js, <strong>Netlify</strong> and <strong>Cloudflare Pages</strong> are platform-agnostic; if you must self-host, <strong>S3 + CloudFront + OAC</strong> with <strong>cloudfront invalidation</strong> on deploy is fine but you give up preview environments unless you wire them yourself; use <strong>Sentry</strong>/<strong>Honeybadger</strong>/<strong>Highlight</strong> for client-side error tracking and source maps.</p>'''


ANSWERS[13] = r'''<p><strong>Situation:</strong> a Jenkins-driven team running Kubernetes Deployments wants <strong>rolling updates</strong> with bounded surge, controlled disruption, and good signals into pipeline status &mdash; without adopting Argo Rollouts or Flagger.</p>

<p><strong>Approach:</strong> the native <code>RollingUpdate</code> strategy is sufficient when paired with <strong>readiness probes</strong>, <strong>preStop hooks</strong>, <strong>PodDisruptionBudgets</strong>, and <strong>topologySpreadConstraints</strong>. Jenkins triggers the rollout via <code>kubectl set image</code> or <code>helm upgrade --atomic</code>, then watches with <code>kubectl rollout status</code> for completion or auto-rollback on failure. Tune <code>maxSurge</code> and <code>maxUnavailable</code> for your throughput vs availability trade-off.</p>

<pre><code># Deployment rollingUpdate config
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 25%, maxUnavailable: 0 }
  minReadySeconds: 10
  revisionHistoryLimit: 5
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: api } }
      containers:
        - name: api
          image: ghcr.io/org/api:placeholder
          readinessProbe:
            httpGet: { path: /healthz, port: 8080 }
            periodSeconds: 5
            failureThreshold: 3
          lifecycle:
            preStop:
              exec: { command: ["sh", "-c", "sleep 10 &amp;&amp; nginx -s quit"] }
          terminationGracePeriodSeconds: 60
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api }
spec: { minAvailable: 80%, selector: { matchLabels: { app: api } } }
</code></pre>

<pre><code>// Jenkinsfile
pipeline {
  agent { kubernetes { yaml libraryResource('agents/jnlp-kubectl.yaml') } }
  stages {
    stage('Set image') {
      steps { sh 'kubectl set image deploy/api api=$REG/api:$GIT_COMMIT -n prod --record' }
    }
    stage('Wait for rollout') {
      steps {
        timeout(time: 10, unit: 'MINUTES') {
          sh 'kubectl rollout status deploy/api -n prod --timeout=10m'
        }
      }
    }
  }
  post {
    failure { sh 'kubectl rollout undo deploy/api -n prod' }
  }
}
</code></pre>

<table><thead><tr><th>Concern</th><th>Setting</th><th>Why</th></tr></thead><tbody>
<tr><td>Surge</td><td>maxSurge: 25%</td><td>Headroom for parallel new pods</td></tr>
<tr><td>Disruption</td><td>maxUnavailable: 0</td><td>Always keep capacity at 100%</td></tr>
<tr><td>Readiness</td><td>HTTP probe on /healthz</td><td>Endpoints flip in only when ready</td></tr>
<tr><td>preStop</td><td>sleep + graceful shutdown</td><td>Drain in-flight requests on terminate</td></tr>
<tr><td>terminationGracePeriod</td><td>60s &gt; preStop + drain</td><td>SIGTERM never wins the race</td></tr>
<tr><td>PDB</td><td>minAvailable: 80%</td><td>Bounds voluntary eviction during node ops</td></tr>
<tr><td>Spread</td><td>topologySpreadConstraints</td><td>AZ resilience during rollout</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> the most common rolling-update failure isn&rsquo;t the rollout itself &mdash; it&rsquo;s a missing <code>preStop sleep</code>, so the kube-proxy iptables rules still send traffic to a terminating pod that&rsquo;s closed its listener; the <code>preStop sleep 10</code> + matching <code>terminationGracePeriodSeconds</code> fixes that across nginx/Envoy/Node/Java; couple <code>kubectl rollout status</code> with explicit timeouts so a hung rollout fails the pipeline; use <code>helm upgrade --atomic --wait --timeout 10m</code> if you&rsquo;re on Helm &mdash; it auto-rolls back on failure; for Argo CD-managed workloads use <strong>sync waves</strong> and <strong>health checks</strong> instead; for canary semantics on top of native rolling updates, <strong>Argo Rollouts</strong> or <strong>Flagger</strong> remain the better path; ship rollout events to <strong>Datadog</strong>/<strong>Honeycomb</strong> as deployment markers; consider <strong>HorizontalPodAutoscaler</strong> with <code>behavior</code> tuned so a scale-down doesn&rsquo;t race the rollout; on Kubernetes 1.33+, <strong>in-place pod resize</strong> can update CPU/memory without recreating pods, which is occasionally useful when paired with VPA recommendations.</p>'''


ANSWERS[14] = r'''<p><strong>Situation:</strong> the security team requires that <em>no</em> long-lived cloud credentials live in GitHub Actions; build secrets, deploy credentials, and runtime config must use short-lived tokens, with secret rotation, audit logs, and least-privilege scoping per workflow.</p>

<p><strong>Approach:</strong> use <strong>OIDC federation</strong> for cloud auth (AWS, GCP, Azure all accept GitHub&rsquo;s OIDC tokens); use <strong>Environments</strong> to scope deploy secrets to specific branches with required reviewers; pull runtime secrets from <strong>HashiCorp Vault</strong>, <strong>AWS Secrets Manager</strong>, <strong>Doppler</strong>, or <strong>1Password</strong> at deploy time, never store them in GitHub; lock down the <code>GITHUB_TOKEN</code> with explicit <code>permissions:</code>; pin actions to commit SHAs and use <strong>step-security/harden-runner</strong> with an egress allow-list.</p>

<pre><code>name: deploy
on: { push: { branches: [main] } }

# Lock down default token
permissions:
  contents: read
  id-token: write   # required for OIDC

jobs:
  deploy:
    runs-on: ubuntu-24.04
    environment: production    # required reviewers + branch policy
    steps:
      - uses: step-security/harden-runner@v2
        with:
          egress-policy: block
          allowed-endpoints: |
            github.com:443
            api.github.com:443
            sts.amazonaws.com:443
            secretsmanager.us-east-1.amazonaws.com:443
            ecr.us-east-1.amazonaws.com:443

      - uses: actions/checkout@v4

      # OIDC -&gt; AWS, no long-lived keys
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-deployer
          role-session-name: gha-${{ github.run_id }}
          aws-region: us-east-1

      # Pull runtime secret from AWS Secrets Manager at deploy time
      - id: secret
        run: |
          DB_URL=$(aws secretsmanager get-secret-value --secret-id prod/db --query SecretString --output text)
          echo "::add-mask::$DB_URL"
          echo "DB_URL=$DB_URL" &gt;&gt; $GITHUB_OUTPUT

      - run: ./deploy.sh
        env: { DB_URL: ${{ steps.secret.outputs.DB_URL }} }
</code></pre>

<table><thead><tr><th>Layer</th><th>Recommended</th><th>Anti-pattern</th></tr></thead><tbody>
<tr><td>Cloud auth</td><td>OIDC federation, role assumption</td><td>Long-lived AWS_ACCESS_KEY_ID in repo secrets</td></tr>
<tr><td>Runtime config</td><td>Vault / AWS SM / Doppler at deploy time</td><td>Plaintext repo secret per env</td></tr>
<tr><td>Default token</td><td>Explicit <code>permissions:</code> per job</td><td>Default <code>write-all</code></td></tr>
<tr><td>Action pinning</td><td>Pin to full commit SHA</td><td>Pin to tag (mutable)</td></tr>
<tr><td>Network egress</td><td>harden-runner allow-list</td><td>Open egress to anywhere</td></tr>
<tr><td>Audit</td><td>Workflow logs + cloud audit (CloudTrail)</td><td>No correlation between actor and action</td></tr>
<tr><td>Rotation</td><td>Vault dynamic creds (DB, AWS)</td><td>Manual rotation, often skipped</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> the highest-leverage controls are <strong>OIDC</strong> + <strong>harden-runner</strong> &mdash; the first eliminates the long-lived-key class of incidents, the second blocks exfiltration if a malicious dependency lands; pin actions to commit SHA (<code>uses: actions/checkout@b4ffde6...</code>) so a tag move can&rsquo;t silently swap behaviour, then use <strong>Renovate</strong> or <strong>Dependabot</strong> to PR updates; for runtime secrets prefer <strong>dynamic credentials</strong> &mdash; Vault DB engine issues a per-deploy DB user, AWS STS issues a 15-minute role; use <strong>environments</strong> with required reviewers and <em>branch policy</em> for production so a PR can&rsquo;t self-deploy; emit <strong>SLSA Level 3 provenance</strong> via <strong>slsa-github-generator</strong> and verify at admission with <strong>Kyverno</strong>/<strong>Sigstore Policy Controller</strong>; for cross-org secrets share via <strong>External Secrets Operator</strong> in K8s rather than copying values across repos; rotate periodically with <strong>secret scanning push protection</strong> as a safety net &mdash; GitHub will reject pushes containing known secret formats; for advanced setups <strong>Doppler</strong>, <strong>1Password Secrets Automation</strong>, and <strong>Akeyless</strong> bring policy and rotation as managed services.</p>'''


ANSWERS[15] = r'''<p><strong>Situation:</strong> a Java service (Spring Boot, Maven) needs CI/CD with <strong>static analysis</strong> (SpotBugs, SonarCloud), unit + integration tests, container build, and deployment to <strong>Google Cloud Run</strong>. The team uses GitHub Actions and wants OIDC-based auth to GCP.</p>

<p><strong>Approach:</strong> use <strong>actions/setup-java</strong> with Maven cache, run tests with <strong>JUnit 5</strong> and <strong>Testcontainers</strong> for integration, run <strong>SpotBugs</strong>/<strong>PMD</strong> via Maven plugins, push results to <strong>SonarCloud</strong>, build the image with <strong>Spring Boot Buildpacks</strong> (no Dockerfile required) or <strong>Jib</strong>, push to <strong>Artifact Registry</strong>, and deploy with <strong>google-github-actions/deploy-cloudrun</strong> using <strong>Workload Identity Federation</strong>.</p>

<pre><code>name: java-cd
on: { push: { branches: [main] }, pull_request: }
permissions: { id-token: write, contents: read, pull-requests: write }
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # SonarCloud needs full history
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '21', cache: maven }
      - run: ./mvnw -B verify spotbugs:check pmd:check
      - run: ./mvnw -B sonar:sonar -Dsonar.token=${{ secrets.SONAR_TOKEN }}
        env: { GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }} }
  build-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '21', cache: maven }
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh
          service_account: gha@my-proj.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker us-central1-docker.pkg.dev
      - run: ./mvnw -B -DskipTests \
              -Dspring-boot.build-image.imageName=us-central1-docker.pkg.dev/my-proj/api/api:$GITHUB_SHA \
              spring-boot:build-image
      - run: docker push us-central1-docker.pkg.dev/my-proj/api/api:$GITHUB_SHA
      - uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: api
          region: us-central1
          image: us-central1-docker.pkg.dev/my-proj/api/api:$GITHUB_SHA
          flags: --min-instances=1 --concurrency=80 --cpu=1 --memory=512Mi
</code></pre>

<table><thead><tr><th>Stage</th><th>Tool</th><th>Notes</th></tr></thead><tbody>
<tr><td>Build/test</td><td>Maven + JUnit 5</td><td>./mvnw verify runs unit + integration</td></tr>
<tr><td>Static analysis</td><td>SpotBugs, PMD, ErrorProne</td><td>Run as Maven plugins; fail build on issues</td></tr>
<tr><td>Quality gate</td><td>SonarCloud / SonarQube</td><td>PR decoration, code coverage from JaCoCo</td></tr>
<tr><td>Image build</td><td>Spring Boot Buildpacks or Jib</td><td>Reproducible, daemonless, no Dockerfile</td></tr>
<tr><td>Auth</td><td>Workload Identity Federation</td><td>OIDC, no JSON key files</td></tr>
<tr><td>Registry</td><td>Artifact Registry</td><td>Per-repo IAM; vulnerability scan included</td></tr>
<tr><td>Deploy</td><td>Cloud Run</td><td>Revision-based, traffic split, instant rollback</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> Cloud Run revisions are first-class deploy units &mdash; every deploy creates a new revision; route traffic with <code>--no-traffic</code> + a manual <code>gcloud run services update-traffic</code> for canaries; rollback is <code>gcloud run services update-traffic --to-revisions=PREV=100</code>; for cold start mitigation use <code>--min-instances=1</code> and consider <strong>Spring Boot CRaC</strong> with Java 21 or <strong>GraalVM native-image</strong> via <code>spring-boot:build-image -Pnative</code> &mdash; sub-100ms startup for typical APIs; trace via <strong>OpenTelemetry</strong> Java agent and forward to <strong>Cloud Trace</strong>/<strong>Datadog</strong>/<strong>Honeycomb</strong>; for richer pipelines, replace SonarCloud with <strong>Snyk</strong>/<strong>Semgrep</strong>/<strong>CodeQL</strong> and add <strong>Dependency-Check</strong>/<strong>Maven Versions Plugin</strong>; use <strong>Renovate</strong> with auto-merge for patch updates; <strong>Cloud Run Jobs</strong> handles scheduled work without spinning up Cloud Scheduler + GKE; for IaC of the whole project, <strong>Terraform</strong>/<strong>OpenTofu</strong> with the Google provider or <strong>Pulumi</strong>; if budget allows, add <strong>Cloud Deploy</strong> as a managed promotion layer over Cloud Run.</p>'''


ANSWERS[16] = r'''<p><strong>Situation:</strong> a deployment occasionally introduces a regression that only manifests under real traffic. The team needs <strong>automated rollback</strong> when health degrades &mdash; no human paging required &mdash; with the rollback decision tied to real metrics, not just pod readiness.</p>

<p><strong>Approach:</strong> the cleanest implementation in 2026 is <strong>Argo Rollouts</strong> with <strong>AnalysisTemplate</strong> queries against Prometheus/Datadog/New Relic during the canary phase &mdash; if a metric breaches threshold, Rollouts automatically aborts and traffic returns to the stable replica set. For Helm-based deploys without Argo Rollouts, <code>helm upgrade --atomic --wait --timeout</code> rolls back on any pod-level failure, but doesn&rsquo;t see business metrics. For richer signals add <strong>Prometheus Alertmanager</strong> webhooks or <strong>Keptn</strong>/<strong>Flagger</strong>.</p>

<pre><code># AnalysisTemplate watches success rate and latency
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: rollout-checks }
spec:
  args: [{ name: service-name }]
  metrics:
    - name: success-rate
      interval: 30s
      successCondition: result[0] &gt;= 0.995
      failureCondition: result[0] &lt; 0.97
      failureLimit: 1
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[2m]))
            / sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))
    - name: p99-latency
      interval: 30s
      successCondition: result[0] &lt; 0.5
      failureCondition: result[0] &gt; 1.0
      failureLimit: 1
      provider:
        prometheus:
          query: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket{service="{{args.service-name}}"}[2m])) by (le))
---
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: api }
spec:
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: { duration: 5m }
        - analysis:
            templates: [{ templateName: rollout-checks }]
            args: [{ name: service-name, value: api }]
        - setWeight: 50
        - pause: { duration: 10m }
        - analysis: { templates: [{ templateName: rollout-checks }], args: [{ name: service-name, value: api }] }
        - setWeight: 100
</code></pre>

<table><thead><tr><th>Trigger</th><th>Mechanism</th><th>Tool</th></tr></thead><tbody>
<tr><td>Pod readiness fail</td><td>kubelet probe + ReplicaSet health</td><td>Native K8s</td></tr>
<tr><td>Helm release fail</td><td>helm upgrade --atomic on any error</td><td>Helm</td></tr>
<tr><td>Metric breach</td><td>Prometheus query during analysis</td><td>Argo Rollouts, Flagger, Keptn</td></tr>
<tr><td>External monitor</td><td>Datadog monitor / New Relic alert</td><td>Webhook to abort Rollout</td></tr>
<tr><td>Manual</td><td><code>kubectl argo rollouts abort</code> or <code>kubectl rollout undo</code></td><td>Native + Argo Rollouts</td></tr>
<tr><td>Schema</td><td>Expand/contract; never destructive same release</td><td>Atlas, Flyway, Liquibase</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> the trick to robust auto-rollback is <strong>realistic thresholds</strong> &mdash; set them just outside normal noise; too tight and every minor blip aborts, too loose and you ship genuine regressions; use <code>failureLimit</code> &gt; 1 so a single transient sample doesn&rsquo;t flip the verdict; pair with <strong>SLO error budgets</strong> &mdash; if you&rsquo;re burning budget, slow promotion automatically by adding longer <code>pause</code> steps; rollback should never be the only safety mechanism &mdash; <strong>feature flags</strong> (LaunchDarkly, ConfigCat, Statsig, OpenFeature, Unleash) let you disable code paths without re-deploying, often the faster fix; for stateful concerns, schema migrations must use <strong>expand/contract</strong> so rollback doesn&rsquo;t encounter a dropped column; instrument deploys as <strong>OpenTelemetry events</strong> in Datadog/Honeycomb so on-call sees deployment markers on dashboards; for blast-radius limitation, deploy region-by-region with explicit gates rather than worldwide-at-once; <strong>Flagger</strong> on Flux+Linkerd is the closest alternative if you&rsquo;re not on Argo CD; <strong>Keptn</strong> adds quality gates on top of either.</p>'''


ANSWERS[17] = r'''<p><strong>Situation:</strong> a small team has a multi-service application defined in <strong>Docker Compose</strong> &mdash; web, API, worker, Postgres, Redis &mdash; and wants to ship from a single repo with automated tests, image builds, and deployment to a single VPS or Container service. They are not yet on Kubernetes.</p>

<p><strong>Approach:</strong> use <strong>GitHub Actions</strong> to build all images with <code>docker compose build</code> + <strong>BuildKit</strong>, run integration tests against the full Compose stack inside CI, push to <strong>GHCR</strong>/<strong>ECR</strong>/<strong>ACR</strong>, then deploy by SSHing to the host and running <code>docker compose pull &amp;&amp; docker compose up -d</code>. For a more managed alternative, use <strong>AWS ECS Compose-X</strong> or <strong>Azure Container Apps</strong>&rsquo; native Compose support so you don&rsquo;t SSH into a VM. Treat Compose-on-VM as a viable shape for low-traffic services and a stepping stone to K8s.</p>

<pre><code># compose.yaml
services:
  web:
    image: ghcr.io/org/web:${TAG:-latest}
    ports: ["80:8080"]
    depends_on: [api]
  api:
    image: ghcr.io/org/api:${TAG:-latest}
    environment: { DATABASE_URL: postgresql://app:pw@db/app, REDIS_URL: redis://cache }
    depends_on: [db, cache]
  worker:
    image: ghcr.io/org/api:${TAG:-latest}
    command: ["node", "worker.js"]
    depends_on: [db, cache]
  db:
    image: postgres:16
    environment: { POSTGRES_PASSWORD: pw, POSTGRES_USER: app }
    volumes: [pgdata:/var/lib/postgresql/data]
  cache: { image: redis:7.4 }
volumes: { pgdata: {} }

# .github/workflows/deploy.yml
name: deploy
on: { push: { branches: [main] } }
permissions: { contents: read, packages: write, id-token: write }
jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - run: TAG=$GITHUB_SHA docker compose build --push
  test:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: TAG=$GITHUB_SHA docker compose up -d
      - run: ./scripts/integration-tests.sh
      - run: docker compose down -v
  deploy:
    needs: test
    runs-on: ubuntu-24.04
    environment: production
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/app
            export TAG=${{ github.sha }}
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Notes</th></tr></thead><tbody>
<tr><td>Build</td><td>docker compose build --push</td><td>BuildKit, GHA cache</td></tr>
<tr><td>Test</td><td>compose up + integration script</td><td>Real Postgres/Redis, faster feedback</td></tr>
<tr><td>Deploy</td><td>SSH + docker compose</td><td>Single host; consider ECS/Container Apps for managed</td></tr>
<tr><td>State</td><td>Named volumes for DB</td><td>Backup nightly; or use managed DB</td></tr>
<tr><td>Secrets</td><td>SSH-injected env file from Vault</td><td>Never bake into images</td></tr>
<tr><td>Rollback</td><td>Re-deploy previous SHA</td><td>Keep last 5 image tags</td></tr>
<tr><td>Migration to K8s</td><td>kompose convert / Compose Bridge</td><td>One-shot port; expect cleanup</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> Compose-on-VM is a fine deployment shape until you outgrow it &mdash; the moment you need horizontal scaling, blue/green, multi-host, or anything but single-instance failover, move to K8s or a managed container service; before then, the operational essentials are <strong>watchtower</strong> or systemd-based image pulls (avoid SSH if possible), <strong>healthchecks</strong> in compose so a broken container restarts, <strong>logs</strong> shipped to <strong>Loki</strong>/<strong>OpenSearch</strong>/<strong>Datadog</strong> via <strong>Vector</strong>/<strong>Fluent Bit</strong>, and <strong>backups</strong> of the DB volume to S3 with <strong>restic</strong>/<strong>borg</strong>/<strong>pgBackRest</strong>; switch the Postgres container for a <strong>managed DB</strong> (RDS, Cloud SQL, Atlas) the moment data matters &mdash; Compose volumes on a single VM are the easiest way to lose customer data; for production-grade Compose orchestration, <strong>Docker Swarm</strong> works but its momentum is gone; <strong>ECS Compose-X</strong> converts Compose to ECS task defs cleanly; <strong>Azure Container Apps</strong> ingests Compose files directly via <code>az containerapp compose</code>; <strong>Fly.io</strong> and <strong>Railway</strong> deploy Compose-shaped apps with sensible defaults if you want to skip infra entirely.</p>'''


ANSWERS[18] = r'''<p><strong>Situation:</strong> Jenkins builds have crept from 3 minutes to 25 minutes over a year as the codebase grew, agents got busier, and plugins accumulated. Developers are losing flow waiting on PR feedback. Diagnose and fix.</p>

<p><strong>Approach:</strong> profile before optimising. Enable the <strong>Pipeline Stage View</strong> and <strong>Blue Ocean</strong> visualisation, and add <code>timestamps()</code> to capture per-step duration. Look at five common culprits: agent provisioning latency, dependency download time, test execution, Docker layer cache misses, and serial-when-parallel-possible stages. Also check controller load (CPU, IO, plugin count) &mdash; a slow controller starves all jobs.</p>

<pre><code>// Jenkinsfile with diagnostic instrumentation
options { timestamps(); ansiColor('xterm') }
pipeline {
  agent { kubernetes { yaml libraryResource('agents/jnlp.yaml') } }
  stages {
    stage('Parallel') {
      parallel {
        stage('Lint') {
          steps { sh 'npm run lint' }
        }
        stage('Unit') {
          steps { sh 'npm run test:unit' }
        }
        stage('Build image') {
          steps {
            sh &apos;&apos;&apos;
              docker buildx build --push \\
                --tag $REG/api:$GIT_COMMIT \\
                --cache-from type=registry,ref=$REG/api:cache \\
                --cache-to   type=registry,ref=$REG/api:cache,mode=max .
            &apos;&apos;&apos;
          }
        }
      }
    }
    stage('Integration') {
      // depends on the image above
      steps { sh 'docker run $REG/api:$GIT_COMMIT npm run test:integration' }
    }
  }
}
</code></pre>

<table><thead><tr><th>Bottleneck</th><th>Diagnostic</th><th>Fix</th></tr></thead><tbody>
<tr><td>Agent provisioning</td><td>Pipeline Stage View shows long &ldquo;waiting for agent&rdquo;</td><td>Pre-warmed pool, K8s plugin retentionTimeout, Karpenter</td></tr>
<tr><td>Dep installs</td><td>npm install 3+ minutes</td><td>BuildKit cache mounts, pnpm with shared store, Verdaccio mirror</td></tr>
<tr><td>Tests</td><td>Single test stage 10+ minutes</td><td>Parallel via matrix, shard with --shard, run-affected only</td></tr>
<tr><td>Docker cache</td><td>BUILDKIT_PROGRESS=plain shows cache miss</td><td>Layer ordering, registry/GHA cache, Depot</td></tr>
<tr><td>Serial stages</td><td>Stage view shows long single column</td><td><code>parallel { ... }</code> across independent work</td></tr>
<tr><td>Controller load</td><td>CPU/IO saturated; long queue times</td><td>Bigger controller, fewer plugins, agent-only Groovy</td></tr>
<tr><td>Plugin overhead</td><td>Long startup, GC pauses</td><td>Audit plugins.txt; remove unused</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> the highest-leverage win is almost always <strong>parallelism</strong> &mdash; lint, unit tests, and image build are independent and should run side-by-side, not sequentially; for tests beyond a few minutes, shard them &mdash; <code>jest --shard=$INDEX/$TOTAL</code>, <code>vitest --shard</code>, <code>pytest-xdist</code>, <strong>knapsack-pro</strong> for time-balanced sharding; for image builds, use <strong>BuildKit cache mounts</strong> (<code>--mount=type=cache</code>), GHA-style registry cache, or <strong>Depot</strong>/<strong>Namespace</strong>/<strong>Blacksmith</strong> persistent BuildKit volumes &mdash; the speedup is usually 3&ndash;5x on dep-heavy projects; for agent provisioning use the <strong>Kubernetes plugin</strong>&rsquo;s pod templates with a <strong>warmedNumber</strong> of pre-built agents waiting; for the controller itself, prune unused plugins (each adds startup time), give it 4&ndash;8 GB heap minimum, store <code>$JENKINS_HOME</code> on fast SSD, and offload heavy logs to S3; if Jenkins itself is the bottleneck and migration is feasible, <strong>GitHub Actions</strong>, <strong>Buildkite</strong>, and <strong>CircleCI</strong> all run rings around a poorly-tuned Jenkins on similar workloads &mdash; sometimes the best fix is exit.</p>'''


ANSWERS[19] = r'''<p><strong>Situation:</strong> a serverless application (AWS Lambda + API Gateway + DynamoDB + EventBridge) needs CI/CD via GitHub Actions, with environment-per-PR for previews, staged production releases with traffic shifting, and observability that catches errors before they reach users.</p>

<p><strong>Approach:</strong> use <strong>AWS SAM</strong> or <strong>SST v3</strong> as the IaC layer, <strong>GitHub Actions</strong> with OIDC for AWS auth, <strong>CodeDeploy</strong> for traffic shifting between Lambda alias versions, and <strong>CloudWatch alarms</strong> as auto-rollback triggers. Each PR gets its own stack (<code>api-pr-123</code>) deployed automatically and torn down on close. Production deploys promote the version through linear traffic shifting (<code>Linear10PercentEvery1Minute</code>).</p>

<pre><code># template.yaml (SAM)
Globals:
  Function:
    Runtime: python3.13
    Architectures: [arm64]
    Tracing: Active
    Environment:
      Variables: { POWERTOOLS_SERVICE_NAME: api, LOG_LEVEL: INFO }
Resources:
  Api:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.handler
      AutoPublishAlias: live
      DeploymentPreference:
        Type: Linear10PercentEvery1Minute
        Alarms: [!Ref ApiErrorsAlarm, !Ref ApiLatencyAlarm]
        Hooks: { PreTraffic: !Ref PreTrafficHook, PostTraffic: !Ref PostTrafficHook }
  ApiErrorsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      MetricName: Errors
      Namespace: AWS/Lambda
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold

# .github/workflows/cd.yml (excerpt)
- uses: aws-actions/configure-aws-credentials@v4
  with: { role-to-assume: arn:aws:iam::123:role/gha, aws-region: us-east-1 }
- uses: aws-actions/setup-sam@v2
- run: sam build --use-container
- run: |
    STACK=api-${{ github.event_name == 'pull_request' &amp;&amp; format('pr-{0}', github.event.number) || 'prod' }}
    sam deploy --stack-name $STACK --no-confirm-changeset --resolve-s3 \
      --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset
- if: github.event.action == 'closed' &amp;&amp; github.event_name == 'pull_request'
  run: sam delete --stack-name api-pr-${{ github.event.number }} --no-prompts
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Tools</th></tr></thead><tbody>
<tr><td>IaC</td><td>SAM, SST v3, CDK, Serverless Framework</td><td>SAM is the AWS-native canonical</td></tr>
<tr><td>Auth</td><td>OIDC role assumption</td><td>configure-aws-credentials@v4</td></tr>
<tr><td>Preview env per PR</td><td>Per-PR stack name + workflow on close</td><td>SAM, CDK</td></tr>
<tr><td>Traffic shift</td><td>CodeDeploy Linear/Canary on alias</td><td>SAM AutoPublishAlias + DeploymentPreference</td></tr>
<tr><td>Auto-rollback</td><td>CloudWatch alarms during shift</td><td>Errors, Throttles, p99 Duration</td></tr>
<tr><td>Pre-traffic hook</td><td>Lambda smoke test before shift</td><td>SAM PreTraffic hook</td></tr>
<tr><td>Observability</td><td>Powertools + X-Ray + OTEL layer</td><td>Datadog, Honeycomb, NR</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> use <strong>Powertools for AWS Lambda</strong> for structured logs, X-Ray traces, idempotency, and feature flags &mdash; the idempotency module is essential for SQS/Kinesis triggers where retries are guaranteed; turn on <strong>SnapStart</strong> for Java/.NET/Python (3.13+) to slash cold-start latency; for shared dependencies use <strong>Lambda Layers</strong> or container image deploys; <strong>arm64</strong> (Graviton) saves ~30% versus x86 with no migration cost for most languages; ship logs and metrics to your platform via the <strong>OpenTelemetry Lambda Layer</strong> or <strong>ADOT</strong> (AWS Distro for OpenTelemetry); for higher-level orchestration <strong>EventBridge Pipes</strong> + <strong>Step Functions</strong> simplify multi-step flows; for queueing <strong>SQS</strong> with batching is more reliable than direct invocations; <strong>SST v3</strong> gives the best developer experience if you want hot-reload deploys; <strong>API Gateway</strong> alternatives include <strong>Function URLs</strong> with CloudFront for HTTP-only, <strong>AppSync</strong> for GraphQL, <strong>Lambda integrated with ALB</strong> for stateful HTTP; track <strong>cold-start percentages</strong> as a top-level SLO &mdash; provisioned concurrency or SnapStart only if it&rsquo;s breaching.</p>'''


ANSWERS[20] = r'''<p><strong>Situation:</strong> the platform team manages complex stateful applications (Postgres clusters, Kafka, Elastic) and wants to use <strong>Kubernetes Operators</strong> to encode operational knowledge declaratively. Operators must be lifecycle-managed via CI/CD, not installed by hand.</p>

<p><strong>Approach:</strong> install operators via <strong>Operator Lifecycle Manager (OLM)</strong> or via Helm charts pinned in Git; manage Custom Resources via the same GitOps pipeline as application workloads (Argo CD ApplicationSets reading from a config repo). Pick mature operators rather than building your own &mdash; <strong>CloudNativePG</strong> for Postgres, <strong>Strimzi</strong> for Kafka, <strong>ECK</strong> for Elastic, <strong>RabbitMQ Cluster Operator</strong>, <strong>Prometheus Operator</strong>, <strong>cert-manager</strong> for TLS. For custom domains, scaffold with <strong>kubebuilder</strong>, write a controller, ship as a containerised manifest, and follow the operator <em>capability levels</em> (basic install &rarr; auto upgrade &rarr; full lifecycle).</p>

<pre><code># config-repo/operators/cnpg/install.yaml (CloudNativePG via Helm via Argo CD)
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: cnpg, namespace: argocd }
spec:
  project: platform
  source:
    repoURL: https://cloudnative-pg.github.io/charts
    chart: cloudnative-pg
    targetRevision: 0.22.1
    helm: { releaseName: cnpg, valueFiles: [values.yaml] }
  destination: { namespace: cnpg-system, server: https://kubernetes.default.svc }
  syncPolicy: { automated: { prune: true, selfHeal: true } }
---
# config-repo/apps/customers-db/cluster.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata: { name: customers, namespace: customers }
spec:
  instances: 3
  postgresql: { parameters: { max_connections: "200" } }
  bootstrap: { initdb: { database: customers, owner: app } }
  storage: { size: 100Gi, storageClass: gp3 }
  backup:
    barmanObjectStore:
      destinationPath: s3://my-pg-backups/customers
      s3Credentials: { accessKeyId: { name: pg-s3, key: ID }, secretAccessKey: { name: pg-s3, key: SECRET } }
    retentionPolicy: 30d
</code></pre>

<table><thead><tr><th>Concern</th><th>Approach</th><th>Notes</th></tr></thead><tbody>
<tr><td>Operator install</td><td>OLM or Helm chart pinned in Git</td><td>OLM auto-handles upgrades; Helm simpler</td></tr>
<tr><td>CR lifecycle</td><td>GitOps with Argo CD/Flux</td><td>Same flow as apps; one source of truth</td></tr>
<tr><td>Custom operator dev</td><td>kubebuilder + Go (or Operator SDK + Helm/Ansible)</td><td>Aim for capability level 4&ndash;5</td></tr>
<tr><td>Validation</td><td>OpenAPI schema in CRD + admission webhook</td><td>Reject malformed CRs before they hit the controller</td></tr>
<tr><td>Versioning</td><td>CRD versions + conversion webhooks</td><td>Safe upgrade across breaking changes</td></tr>
<tr><td>Monitoring</td><td>Operator metrics + ServiceMonitor</td><td>kube-prometheus-stack scrapes</td></tr>
<tr><td>RBAC</td><td>Least-privilege ServiceAccount</td><td>Controller-only access to its CRDs</td></tr>
</tbody></table>

<p><strong>Production polish:</strong> the highest-impact decision is <em>which</em> operators to adopt &mdash; pick projects in the <strong>CNCF</strong> Sandbox/Incubating/Graduated stages with active maintainers; <strong>CloudNativePG</strong>, <strong>Strimzi</strong>, <strong>ECK</strong>, <strong>cert-manager</strong>, <strong>External Secrets Operator</strong>, <strong>Crossplane</strong>, and <strong>kube-prometheus-stack</strong> are the 2026 baseline; check capability levels per <strong>OperatorHub</strong> &mdash; you want <em>auto-pilot</em> (level 4) or <em>seamless upgrades</em> (level 5), not just <em>basic install</em>; treat the operator&rsquo;s own version as part of the platform release train &mdash; pin to a specific chart version, test upgrades in staging first, and document the rollback procedure (operator downgrades can leave CRs orphaned); for custom operators write tests with <strong>envtest</strong> (kubebuilder&rsquo;s in-process etcd+API server) and end-to-end with <strong>kuttl</strong>; emit <strong>OpenTelemetry</strong> traces from controller reconciliation; ship operator logs structured to <strong>Loki</strong>/<strong>OpenSearch</strong>; for cluster-wide policy on what CRs are valid, <strong>Kyverno</strong> or <strong>Gatekeeper</strong> enforce constraints (e.g., every Cluster must have a <code>backup</code> stanza); avoid building a custom operator unless you genuinely have novel logic &mdash; most use cases are better served by an existing one + a thin wrapper Helm chart.</p>'''

ANSWERS[21] = r'''<p><strong>Situation:</strong> a Node.js service has long install times because <code>npm ci</code> downloads the full registry on every CI run. The team wants <strong>continuous integration</strong> in GitHub Actions with effective dependency caching that survives across branches and PR runs while staying secure against cache poisoning.</p>

<p><strong>Approach:</strong> use the official <code>actions/setup-node@v4</code> with <code>cache: &#39;npm&#39;</code> to wire <strong>actions/cache</strong> automatically, keyed on <code>package-lock.json</code> hash. Pin Node by version in <code>.nvmrc</code> so the matrix and the cache key align. For monorepos with <strong>pnpm</strong> or <strong>yarn</strong> the same pattern applies (<code>cache: &#39;pnpm&#39;</code>, <code>cache: &#39;yarn&#39;</code>); use <strong>Turborepo Remote Cache</strong> or <strong>Nx Cloud</strong> for build artefacts on top of the dependency cache. Run <strong>npm audit</strong>, <strong>Snyk</strong>, or <strong>Socket.dev</strong> in parallel with tests so a vulnerable dependency fails the PR.</p>

<pre><code># .github/workflows/ci.yml
name: ci
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    strategy:
      matrix: { node: [20, 22] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
          cache-dependency-path: package-lock.json
      - run: npm ci --prefer-offline --no-audit
      - run: npm run lint
      - run: npm test -- --reporter=junit --reporter-options output=junit.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: junit-${{ matrix.node }}, path: junit.xml }
  audit:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'npm' }
      - run: npm ci --prefer-offline --ignore-scripts
      - run: npm audit --audit-level=high
      - uses: snyk/actions/node@master
        env: { SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} }
</code></pre>

<table>
<tr><th>Choice</th><th>Trade-off</th></tr>
<tr><td><code>actions/setup-node</code> built-in cache</td><td>Simple, official, restores in seconds; sometimes lags newer cache backend features</td></tr>
<tr><td>Manual <code>actions/cache</code></td><td>More control over keys/paths but needs hashFiles boilerplate</td></tr>
<tr><td>Self-hosted runners + warm <code>~/.npm</code></td><td>Fastest, but cache poisoning risk; rotate runners ephemerally</td></tr>
<tr><td><code>npm ci --ignore-scripts</code></td><td>Mitigates malicious postinstall; some packages legitimately need scripts</td></tr>
<tr><td>Turborepo / Nx remote cache</td><td>Skips work entirely on cache hit; needs trust boundary &mdash; never restore in PR builds from forks</td></tr>
</table>

<p><strong>Production polish:</strong> always run <code>npm ci</code> not <code>npm install</code> &mdash; <code>ci</code> respects the lockfile exactly, fails on drift, and clears <code>node_modules</code> first so a poisoned local copy can&rsquo;t survive; pass <code>--prefer-offline</code> so cached tarballs are reused without metadata refresh; add <code>--no-audit</code> on the install step (audit runs as a separate job so a registry stall doesn&rsquo;t fail the build); set <code>permissions: { contents: read }</code> at workflow level so a leaked GITHUB_TOKEN can&rsquo;t push code; for forks, use <code>pull_request_target</code> only with extreme care &mdash; restrict it to label-based gates and never check out fork code in that workflow; restrict the cache scope (the GHA cache is per-repo+branch with read access from any base branch &mdash; treat it as untrusted for security-sensitive steps); pin actions by SHA (<code>actions/checkout@b4ffde65...</code>) not by tag for supply-chain protection; use <strong>Dependabot</strong> or <strong>Renovate</strong> with <strong>group: { major }</strong> rules to bundle updates and reduce PR noise; run <strong>OSV-Scanner</strong> alongside Snyk &mdash; OSV catches things commercial scanners miss because it pulls from the OSV.dev database directly.</p>'''

ANSWERS[22] = r'''<p><strong>Situation:</strong> the team merges fast and wants the pipeline to enforce <strong>code quality</strong> &mdash; consistent formatting via <strong>Prettier</strong>, lint rules via <strong>ESLint</strong>, type-checking via TypeScript, and security scans &mdash; without slowing PRs to a crawl. Reviewers should focus on logic, not whitespace.</p>

<p><strong>Approach:</strong> push checks left to <strong>pre-commit hooks</strong> (lefthook, husky+lint-staged) so devs catch failures locally, then re-run the same checks in CI for trust. Use <strong>Biome</strong> as a single fast tool replacing ESLint+Prettier where the team agrees; otherwise run ESLint with <code>--cache</code> and <code>--max-warnings=0</code> alongside <code>prettier --check</code>. Wire branch protection so <strong>required checks</strong> include lint, type-check, and tests. For PR-only runs, use <code>actions/cache</code> on <code>.eslintcache</code> and <code>tsc --incremental</code> output to keep CI under 60 seconds.</p>

<pre><code># .github/workflows/quality.yml
name: quality
on:
  pull_request: { branches: [main] }
permissions: { contents: read, pull-requests: write, checks: write }
concurrency:
  group: quality-${{ github.ref }}
  cancel-in-progress: true
jobs:
  lint-format:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'npm' }
      - run: npm ci --prefer-offline
      - uses: actions/cache@v4
        with:
          path: |
            .eslintcache
            node_modules/.cache
          key: lint-${{ runner.os }}-${{ hashFiles('**/package-lock.json', '.eslintrc*') }}
      - run: npx eslint . --cache --max-warnings=0 --format @microsoft/eslint-formatter-sarif --output-file eslint.sarif
      - run: npx prettier --check 'src/**/*.{ts,tsx,js,jsx,json,md}'
      - run: npx tsc --noEmit
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with: { sarif_file: eslint.sarif }
  reviewdog:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: reviewdog/action-eslint@v1
        with: { reporter: github-pr-review, eslint_flags: 'src/' }
</code></pre>

<table>
<tr><th>Tool</th><th>When it fits</th></tr>
<tr><td>ESLint + Prettier (classic)</td><td>Mature plugin ecosystem; slowest</td></tr>
<tr><td>Biome (single-binary)</td><td>10&times; faster; smaller plugin ecosystem; great for greenfield</td></tr>
<tr><td>oxc-lint</td><td>Newest, Rust-based; preview/experimental for many rules</td></tr>
<tr><td>reviewdog</td><td>Inline PR comments instead of opaque CI failure</td></tr>
<tr><td>SonarCloud / CodeRabbit</td><td>Bigger picture (cyclomatic complexity, AI review)</td></tr>
</table>

<p><strong>Production polish:</strong> use <strong>concurrency cancellation</strong> (above) so a new push cancels the in-flight job &mdash; saves runner minutes on rapid-fire commits; output <strong>SARIF</strong> from ESLint and upload via <code>github/codeql-action/upload-sarif</code> so findings appear in the GitHub Security tab and code-scanning alerts; treat the lint config (<code>.eslintrc</code>, <code>biome.json</code>, <code>prettier.config.js</code>) as code in a shared package the org publishes (e.g., <code>@org/eslint-config</code>) so all repos stay aligned; enforce via <strong>tsconfig.json</strong> with <code>strict: true</code>, <code>noUncheckedIndexedAccess</code>, and <code>noImplicitOverride</code> &mdash; type-checking catches more real bugs than any linter; run <strong>knip</strong> or <strong>dpdm</strong> to find unused exports/dependencies; gate merges on the GitHub <em>Required Checks</em> rule plus <em>Require branches to be up to date</em> so stale PRs don&rsquo;t merge with broken main; pin the lint rule version with <code>--no-cache</code> in the security-critical job to prevent cache abuse; add a <strong>commitlint</strong> + <strong>conventional commits</strong> hook so changelogs and semantic-release work cleanly downstream.</p>'''

ANSWERS[23] = r'''<p><strong>Situation:</strong> a Go service must ship to <strong>AWS ECS Fargate</strong> with an opinionated CI/CD pipeline: race-detector tests, integration tests against a real Postgres, vulnerability scans, multi-arch container images, and zero-downtime rolling deploys. No static IAM keys.</p>

<p><strong>Approach:</strong> standard layered pipeline &mdash; lint+test in one job, build+push image in another, deploy via the official ECS deploy action. Use <strong>OIDC</strong> federation to a least-privilege IAM role for AWS auth. Use <strong>buildx</strong> with QEMU for arm64+amd64 multi-arch (Graviton saves ~30% on Fargate). Run <strong>govulncheck</strong> and <strong>Trivy</strong> on every PR; gate on high-severity findings. Render the ECS task definition from a template, register a new revision, and let ECS handle the rolling update with health-check based replacement.</p>

<pre><code># .github/workflows/deploy.yml
name: deploy
on:
  push: { branches: [main] }
permissions: { id-token: write, contents: read }
env:
  AWS_REGION: ap-south-1
  ECR_REPO: ${{ secrets.ECR_REPO }}
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_PASSWORD: test }
        options: --health-cmd "pg_isready" --health-interval 10s
        ports: [5432:5432]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.24', cache: true }
      - run: go mod download
      - run: go test -race -coverprofile=cover.out ./...
        env: { DATABASE_URL: postgres://postgres:test@localhost/postgres?sslmode=disable }
      - run: go run golang.org/x/vuln/cmd/govulncheck@latest ./...
  deploy:
    needs: test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-deployer
          aws-region: ${{ env.AWS_REGION }}
      - uses: aws-actions/amazon-ecr-login@v2
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ env.ECR_REPO }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true
      - uses: aquasecurity/trivy-action@v0
        with:
          image-ref: ${{ env.ECR_REPO }}:${{ github.sha }}
          severity: HIGH,CRITICAL
          exit-code: '1'
      - uses: aws-actions/amazon-ecs-render-task-definition@v1
        id: task
        with:
          task-definition: deploy/task-definition.json
          container-name: api
          image: ${{ env.ECR_REPO }}:${{ github.sha }}
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.task.outputs.task-definition }}
          service: api
          cluster: prod
          wait-for-service-stability: true
</code></pre>

<table>
<tr><th>Choice</th><th>Trade-off</th></tr>
<tr><td>ECS Fargate</td><td>No node management; higher per-vCPU cost than EKS+Karpenter at scale</td></tr>
<tr><td>OIDC federation</td><td>No long-lived keys; needs trust policy setup with thumbprint pinning</td></tr>
<tr><td>arm64 (Graviton)</td><td>~30% cost savings; needs multi-arch build for dev parity</td></tr>
<tr><td>CodeDeploy blue/green</td><td>Cleanest rollback; adds ~minutes to deploy and needs ALB target groups</td></tr>
<tr><td>App Runner</td><td>Even simpler than ECS; less control over networking</td></tr>
</table>

<p><strong>Production polish:</strong> tag images with both <code>:sha</code> and <code>:semver</code> (immutable identity vs human-readable); enable <strong>ECR scan-on-push</strong> with <strong>Inspector v2</strong> for continuous CVE scanning &mdash; PRs get pre-merge feedback, prod gets continuous; ship <strong>SLSA provenance</strong> via <code>provenance: true</code> in buildx so consumers can verify the build path; sign images with <strong>Cosign keyless</strong> (Sigstore Fulcio) using the same OIDC token; gate ECS service updates with <strong>CodeDeploy</strong> for canary 10/30/60/100 traffic shift and tie CloudWatch alarms (5xx, p99 latency) to auto-rollback; configure <strong>ECS Exec</strong> for SSM-based shell access in incidents; set <strong>HealthCheckGracePeriod</strong> on the service so slow-starting tasks don&rsquo;t flap; use <strong>X-Ray</strong> with the X-Amzn-Trace-Id header propagation for end-to-end tracing; for secrets, use <strong>SSM Parameter Store</strong> or <strong>Secrets Manager</strong> referenced from the task definition &mdash; never bake secrets into the image.</p>'''

ANSWERS[24] = r'''<p><strong>Situation:</strong> a Kubernetes platform team needs end-to-end <strong>monitoring and alerting</strong> for clusters and the apps on them. Requirements: cluster + workload metrics, customised dashboards, multi-tenant access, long retention, and PagerDuty/Slack alerting. Must scale to 10+ clusters without operator burnout.</p>

<p><strong>Approach:</strong> install <strong>kube-prometheus-stack</strong> (the Helm chart that bundles Prometheus, Alertmanager, Grafana, kube-state-metrics, and node-exporter) per cluster via Argo CD, and federate to a central tier &mdash; <strong>Thanos</strong>, <strong>Grafana Mimir</strong>, or <strong>VictoriaMetrics Cluster</strong> &mdash; for global query, long retention (years), and HA. Use <strong>Prometheus Operator CRDs</strong> (<code>ServiceMonitor</code>, <code>PodMonitor</code>, <code>PrometheusRule</code>) so app teams declare their own scrape targets and alerts in their own namespaces. Centralise dashboards in <strong>Grafana</strong> with per-tenant data sources via <strong>Grafana Cloud</strong> or self-hosted with <strong>Grafana Mimir Multi-tenant</strong>.</p>

<pre><code># config-repo/monitoring/values.yaml (kube-prometheus-stack)
prometheus:
  prometheusSpec:
    retention: 7d
    retentionSize: 50GiB
    walCompression: true
    enableAdminAPI: false
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    storageSpec:
      volumeClaimTemplate:
        spec: { storageClassName: gp3, resources: { requests: { storage: 200Gi } } }
    remoteWrite:
      - url: https://mimir.platform.svc/api/v1/push
        headers: { X-Scope-OrgID: cluster-prod-eu }
alertmanager:
  config:
    route:
      receiver: slack-default
      group_by: ['alertname','cluster','service']
      routes:
        - matchers: [severity="critical"]
          receiver: pagerduty
    receivers:
      - name: slack-default
        slack_configs: [ { api_url: $SLACK_URL, channel: '#alerts' } ]
      - name: pagerduty
        pagerduty_configs: [ { service_key: $PD_KEY } ]
grafana:
  adminPassword: ${GRAFANA_ADMIN}
  sidecar: { dashboards: { enabled: true, searchNamespace: ALL } }
---
# app-repo/checkout/monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata: { name: checkout, namespace: checkout }
spec:
  selector: { matchLabels: { app: checkout } }
  endpoints: [ { port: metrics, path: /metrics, interval: 30s } ]
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata: { name: checkout-slo, namespace: checkout }
spec:
  groups:
    - name: checkout.rules
      rules:
        - alert: CheckoutHighErrorRate
          expr: sum(rate(http_requests_total{app="checkout",code=~"5.."}[5m]))
            / sum(rate(http_requests_total{app="checkout"}[5m])) > 0.05
          for: 10m
          labels: { severity: critical, team: payments }
          annotations: { summary: "Checkout 5xx > 5% for 10m" }
</code></pre>

<table>
<tr><th>Layer</th><th>Tool (2026)</th></tr>
<tr><td>Per-cluster collection</td><td>Prometheus Operator + kube-state-metrics + node-exporter</td></tr>
<tr><td>Long-term + global query</td><td>Thanos, Grafana Mimir, VictoriaMetrics Cluster</td></tr>
<tr><td>Logs</td><td>Loki, OpenSearch, Grafana Loki Cloud</td></tr>
<tr><td>Traces</td><td>Tempo, Jaeger, OpenTelemetry Collector</td></tr>
<tr><td>Profiles</td><td>Pyroscope (now Grafana Pyroscope)</td></tr>
<tr><td>Routing/alerting</td><td>Alertmanager &rarr; PagerDuty / Slack / Opsgenie</td></tr>
<tr><td>SLOs</td><td>Sloth or Pyrra to generate SLI/SLO PrometheusRules</td></tr>
</table>

<p><strong>Production polish:</strong> design alerts around <strong>SLOs</strong> (error budget burn rate) using <strong>Sloth</strong> or <strong>Pyrra</strong> &mdash; multi-window multi-burn-rate alerts page only on real customer impact, not symptom noise; route <strong>severity: critical</strong> to PagerDuty and <strong>warning</strong> to Slack so on-call is awakened only for real incidents; ensure Alertmanager is HA across at least 2 replicas and use <strong>cluster.peer</strong> with proper service discovery; deduplicate per-cluster alerts at the federation tier; send everything to <strong>OpenTelemetry Collector</strong> first so logs/metrics/traces share resource attributes; consume Mimir/Tempo/Loki via Grafana with <strong>Exemplars</strong> wired so a metric spike one-clicks into the trace; back up Prometheus WAL nightly and verify restore drills; keep alert <strong>runbook URLs</strong> in the annotation field so the on-call gets a link to remediation; for cost control, use <strong>Mimir&rsquo;s</strong> per-tenant retention policies and <strong>downsampling</strong> (5m and 1h aggregations) so historical queries are fast and cheap.</p>'''

ANSWERS[25] = r'''<p><strong>Situation:</strong> a SaaS product needs to deploy a <strong>multi-tenant application</strong> on Kubernetes &mdash; some tenants share infrastructure (cost), some demand isolation (compliance). The CI/CD pipeline must support both shapes, onboard new tenants without operator intervention, and prevent any one tenant from impacting another.</p>

<p><strong>Approach:</strong> three deployment shapes &mdash; <em>silo</em> (one cluster per tenant), <em>pool</em> (shared cluster, shared namespace, tenant-id discriminator), and <em>bridge</em> (shared cluster, dedicated namespace). The pipeline picks the shape from a tenant manifest in Git; <strong>Argo CD ApplicationSet</strong> with the list/git generator creates the right Application(s). For pool and bridge, use <strong>Capsule</strong> or <strong>vCluster</strong> to enforce tenant isolation; for silo, manage clusters via <strong>Cluster API</strong>. Wire <strong>RBAC + NetworkPolicy + ResourceQuota + LimitRange + PodSecurity</strong> consistently regardless of shape.</p>

<pre><code># tenants.yaml &mdash; the source of truth
tenants:
  - id: acme
    plan: enterprise
    shape: bridge
    region: eu
  - id: globex
    plan: starter
    shape: pool
    region: us
  - id: regulated-co
    plan: dedicated
    shape: silo
    region: us
---
# Argo CD ApplicationSet driven by tenants.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: tenants, namespace: argocd }
spec:
  generators:
    - git:
        repoURL: https://github.com/org/config
        revision: main
        files: [{ path: tenants/*.yaml }]
  template:
    metadata: { name: 'tenant-{{ id }}' }
    spec:
      project: tenants
      source:
        repoURL: https://github.com/org/charts
        chart: tenant
        targetRevision: 1.4.0
        helm:
          parameters:
            - { name: tenant.id, value: '{{ id }}' }
            - { name: tenant.plan, value: '{{ plan }}' }
      destination:
        namespace: 'tenant-{{ id }}'
        server: '{{ cluster.server }}'
      syncPolicy: { automated: { prune: true, selfHeal: true } }
---
# Capsule Tenant CR for bridge/pool shape
apiVersion: capsule.clastix.io/v1beta2
kind: Tenant
metadata: { name: acme }
spec:
  owners: [{ kind: Group, name: acme-admins }]
  namespaceOptions: { quota: 5 }
  resourceQuotas:
    items:
      - hard: { requests.cpu: "20", requests.memory: 40Gi, limits.cpu: "40" }
  networkPolicies:
    items:
      - podSelector: {}
        ingress:
          - from: [ { podSelector: {} }, { namespaceSelector: { matchLabels: { tenant: acme } } } ]
</code></pre>

<table>
<tr><th>Shape</th><th>Cost</th><th>Isolation</th><th>Best for</th></tr>
<tr><td>Pool (shared NS)</td><td>Lowest</td><td>Logical only</td><td>Free/starter plans, low data sensitivity</td></tr>
<tr><td>Bridge (shared cluster, NS-per-tenant)</td><td>Medium</td><td>NS+RBAC+NetworkPolicy</td><td>Most paid plans</td></tr>
<tr><td>Silo (cluster-per-tenant)</td><td>Highest</td><td>Strong (kernel boundary at cluster scope)</td><td>Regulated/dedicated, large tenants</td></tr>
<tr><td>vCluster</td><td>Medium-low</td><td>Cluster-API illusion in shared physical</td><td>Tenants needing CRD-level isolation cheaply</td></tr>
</table>

<p><strong>Production polish:</strong> enforce isolation in depth &mdash; <strong>NetworkPolicy</strong> default-deny per namespace plus <strong>Cilium L7 + FQDN egress rules</strong>, <strong>ResourceQuota</strong> + <strong>LimitRange</strong> to prevent noisy neighbours, <strong>PodSecurity Admission</strong> at <em>restricted</em>, and <strong>Kyverno</strong> policies that mandate every tenant pod has the correct labels and runs as non-root; for storage, use per-tenant <strong>StorageClasses</strong> with separate encryption keys (KMS); for egress, separate <strong>NAT gateways</strong> or <strong>Cilium Egress Gateway</strong> per tenant so source IPs are tenant-scoped; meter usage via <strong>OpenCost</strong> labelled by tenant for accurate billing; isolate observability per tenant via <strong>Mimir</strong> tenant headers, <strong>Loki</strong> X-Scope-OrgID, and Grafana org-per-tenant; tenant onboarding becomes a single PR adding to <code>tenants.yaml</code> &mdash; the ApplicationSet picks it up, Capsule provisions, and Argo CD reconciles in minutes; document tenant offboarding (delete from tenants.yaml &rarr; Argo CD prunes &rarr; final backup snapshot) clearly so customer departures aren&rsquo;t scary.</p>'''

ANSWERS[26] = r'''<p><strong>Situation:</strong> the platform must deploy the same application to <strong>AWS, Azure, and GCP</strong> for resilience and customer-region requirements. Build once, deploy many. Single source of truth for manifests, no per-cloud forks, but allow cloud-specific overrides where genuinely different.</p>

<p><strong>Approach:</strong> use <strong>OIDC federation</strong> for each cloud (no static keys), build a single multi-arch image and push to a primary registry replicated to ECR/ACR/GAR, and deploy via cloud-agnostic abstractions where possible (<strong>Crossplane</strong> for cloud infra, <strong>Argo CD</strong> for K8s workloads). Tag the workflow matrix with the cloud and let Argo CD ApplicationSets handle the per-cluster differences. For DNS-level traffic distribution, use <strong>NS1</strong>, <strong>Cloudflare Load Balancing</strong>, or <strong>AWS Route 53 ARC</strong>.</p>

<pre><code># .github/workflows/multicloud.yml
name: multicloud
on: { push: { tags: ['v*'] } }
permissions: { id-token: write, contents: read }
jobs:
  build:
    runs-on: ubuntu-24.04
    outputs: { tag: ${{ steps.meta.outputs.tag }} }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - id: meta
        run: echo "tag=${GITHUB_REF_NAME}" &gt;&gt; $GITHUB_OUTPUT
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - uses: docker/build-push-action@v6
        with:
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ghcr.io/org/app:${{ steps.meta.outputs.tag }}
          provenance: true
          sbom: true
  deploy:
    needs: build
    strategy:
      matrix:
        target:
          - { cloud: aws,   region: ap-south-1,    role: arn:aws:iam::1:role/deploy }
          - { cloud: azure, region: westeurope,    sub:  ${{ vars.AZ_SUB }} }
          - { cloud: gcp,   region: europe-west4,  wif:  projects/p/locations/global/workloadIdentityPools/gha }
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - if: matrix.target.cloud == 'aws'
        uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: ${{ matrix.target.role }}, aws-region: ${{ matrix.target.region }} }
      - if: matrix.target.cloud == 'azure'
        uses: azure/login@v2
        with: { client-id: ${{ vars.AZ_CLIENT }}, tenant-id: ${{ vars.AZ_TENANT }}, subscription-id: ${{ matrix.target.sub }} }
      - if: matrix.target.cloud == 'gcp'
        uses: google-github-actions/auth@v2
        with: { workload_identity_provider: ${{ matrix.target.wif }}, service_account: deploy@p.iam.gserviceaccount.com }
      - run: |
          # Bump tag in the cloud-specific config repo path; Argo CD per cluster reconciles
          gh api repos/org/config/dispatches -f event_type=bump \
            -f client_payload='{"cloud":"${{ matrix.target.cloud }}","tag":"${{ needs.build.outputs.tag }}"}'
        env: { GH_TOKEN: ${{ secrets.CONFIG_REPO_PAT }} }
</code></pre>

<table>
<tr><th>Concern</th><th>Tooling</th></tr>
<tr><td>Auth</td><td>OIDC + WIF (AWS/Azure/GCP all support it)</td></tr>
<tr><td>Image distribution</td><td>Single registry + replication, or push to all three (ECR/ACR/GAR)</td></tr>
<tr><td>Manifest abstraction</td><td>Argo CD + Helm/Kustomize per environment</td></tr>
<tr><td>Cloud infra</td><td>Crossplane Compositions or OpenTofu modules per cloud</td></tr>
<tr><td>Traffic steering</td><td>Cloudflare LB, NS1, Route 53 ARC, GCP Cloud DNS routing policies</td></tr>
<tr><td>Cost monitoring</td><td>OpenCost (per-cluster), Vantage / Cloudability (cross-cloud)</td></tr>
</table>

<p><strong>Production polish:</strong> use <strong>Active/Active</strong> only when state syncing is solved (CRDB, Spanner, DynamoDB Global Tables, CosmosDB multi-region) &mdash; otherwise default to <strong>Active/Passive</strong> with documented failover; egress costs eat budgets quickly &mdash; pin database reads to the local region and route only writes cross-cloud via a single primary; SLAs differ across clouds &mdash; track per-cloud availability separately and alert on the worst-performing region; for GitOps, run <strong>Argo CD</strong> in each cluster (no shared central control plane that becomes a multi-cloud SPOF); replicate registries with <strong>Harbor replication</strong> or native registry-to-registry mirroring; sign images once and verify everywhere with <strong>Cosign</strong> + <strong>Sigstore policy-controller</strong>; for failover testing, run <strong>chaos drills</strong> quarterly using <strong>Chaos Mesh</strong> or <strong>Litmus</strong>; keep cloud-specific code minimal &mdash; if you find yourself with three different deployment YAML trees, consolidate via Crossplane Compositions or accept that you have three separate products.</p>'''

ANSWERS[27] = r'''<p><strong>Situation:</strong> a data science team needs <strong>CI/CD for an ML model</strong> &mdash; train on a versioned dataset, evaluate against a baseline, register the artefact, deploy to staging+prod with traffic shadowing, and monitor for drift. Reproducibility is non-negotiable; rollback must be a label change, not a re-train.</p>

<p><strong>Approach:</strong> separate the <em>model pipeline</em> from the <em>application pipeline</em>. The model pipeline runs in <strong>Kubeflow Pipelines</strong>, <strong>Argo Workflows</strong>, <strong>Flyte</strong>, or <strong>Metaflow</strong>: ingest dataset (versioned via <strong>DVC</strong>, <strong>lakeFS</strong>, or <strong>Pachyderm</strong>), preprocess, train (with GPUs scheduled by <strong>NVIDIA GPU Operator</strong>), evaluate against a champion model, and register the new candidate in <strong>MLflow</strong> or the <strong>Hugging Face Hub</strong>. The serving pipeline deploys via <strong>KServe</strong>, <strong>Seldon Core</strong>, <strong>BentoML</strong>, or <strong>Ray Serve</strong>, with canary rollout and shadow traffic via <strong>Istio</strong> or <strong>Knative</strong>.</p>

<pre><code># pipeline.py (Kubeflow Pipelines v2 SDK)
from kfp import dsl, compiler
@dsl.component(packages_to_install=['mlflow==2.16','dvc[s3]','scikit-learn'])
def train(data_uri: str, exp: str) -&gt; str:
    import mlflow, dvc.api, joblib
    with dvc.api.open(data_uri, repo='https://github.com/org/data') as f:
        X, y = load(f)
    mlflow.set_experiment(exp)
    with mlflow.start_run() as r:
        clf = train_model(X, y)
        mlflow.log_metric('accuracy', score(clf))
        mlflow.sklearn.log_model(clf, 'model', registered_model_name='fraud-detector')
        return r.info.run_id
@dsl.component(packages_to_install=['mlflow==2.16'])
def gate(run_id: str) -&gt; str:
    import mlflow
    cand = mlflow.get_run(run_id).data.metrics['accuracy']
    champ = champion_score()
    if cand &lt; champ * 0.99:
        raise RuntimeError(f'candidate {cand} fails gate vs {champ}')
    return run_id
@dsl.pipeline(name='fraud-train')
def fraud(data: str = 's3://lake/fraud/2026-04.parquet'):
    t = train(data_uri=data, exp='fraud')
    gate(run_id=t.output)
compiler.Compiler().compile(fraud, 'fraud.yaml')
---
# kserve InferenceService promoted via GitOps after gate passes
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata: { name: fraud }
spec:
  predictor:
    canaryTrafficPercent: 10
    sklearn: { storageUri: s3://models/fraud/2026-04-29 }
</code></pre>

<table>
<tr><th>Stage</th><th>Tooling (2026)</th></tr>
<tr><td>Dataset versioning</td><td>DVC, lakeFS, Pachyderm</td></tr>
<tr><td>Experiment tracking</td><td>MLflow, Weights &amp; Biases, Comet</td></tr>
<tr><td>Pipeline orchestration</td><td>Kubeflow Pipelines, Argo Workflows, Flyte, Metaflow</td></tr>
<tr><td>Feature store</td><td>Feast, Tecton, Hopsworks</td></tr>
<tr><td>Model registry</td><td>MLflow Registry, Hugging Face Hub, Vertex AI Model Registry</td></tr>
<tr><td>Serving</td><td>KServe, Seldon Core v2, BentoML, Ray Serve, vLLM/TGI for LLMs</td></tr>
<tr><td>Drift / monitoring</td><td>Evidently AI, NannyML, Arize, WhyLabs</td></tr>
</table>

<p><strong>Production polish:</strong> reproducibility comes from pinning dataset hash + code commit + container digest + hyperparameters &mdash; record all four in MLflow per run; promote with explicit <strong>quality gates</strong> (accuracy, F1, fairness metrics, latency on representative inputs) &mdash; never auto-promote on accuracy alone; use <strong>shadow deploys</strong> first &mdash; route 5&ndash;10% of production traffic to the new model with results discarded, compare distributions, then graduate to canary; monitor <strong>data drift</strong> (input feature distributions) and <strong>concept drift</strong> (prediction quality vs labels when feedback arrives) using Evidently or NannyML; for LLMs, run <strong>regression evals</strong> with <strong>promptfoo</strong>, <strong>DeepEval</strong>, or <strong>Ragas</strong> on a fixed test set per release; maintain a <strong>rollback pointer</strong> in the registry so demoting a model is a label change, not a retrain; capture <strong>SHAP/LIME</strong> explanations for regulated domains; for very large models, use <strong>SOCI</strong> image streaming and pre-warmed pods so cold-start doesn&rsquo;t blow the SLO budget; handle PII in datasets via masking + access controls in lakeFS; document the model card alongside the model artefact for auditability.</p>'''

ANSWERS[28] = r'''<p><strong>Situation:</strong> security insists every Docker image entering production goes through <strong>vulnerability scanning</strong> in CI/CD. Currently nothing scans &mdash; CVEs land in production unnoticed. The fix must integrate with Jenkins, gate merges/deploys, and produce auditable evidence (SBOM, scan reports) without grinding pipeline times into oblivion.</p>

<p><strong>Approach:</strong> shift left with <strong>Trivy</strong> or <strong>Grype</strong> on every build, gate on <strong>HIGH/CRITICAL</strong> findings, generate an <strong>SBOM</strong> with <strong>Syft</strong> in <strong>SPDX</strong> or <strong>CycloneDX</strong> format, sign the image with <strong>Cosign keyless</strong> via Sigstore, and publish results to the central security platform (<strong>Defect Dojo</strong>, <strong>Dependency-Track</strong>, or <strong>Wiz</strong>). Add an admission-time check with <strong>Kyverno</strong> or <strong>Connaisseur</strong> so the cluster refuses unsigned/un-scanned images. Run continuous post-deploy scans with <strong>Trivy Operator</strong> so newly-disclosed CVEs are caught even after the image was built clean.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent { kubernetes { yaml &apos;&apos;&apos;
spec:
  containers:
    - { name: kaniko, image: gcr.io/kaniko-project/executor:debug, command: [sleep], args: [99d] }
    - { name: trivy,  image: aquasec/trivy:0.55,  command: [sleep], args: [99d] }
    - { name: cosign, image: gcr.io/projectsigstore/cosign:v2.4, command: [sleep], args: [99d] }
&apos;&apos;&apos; } }
  stages {
    stage('Build') {
      steps { container('kaniko') {
        sh 'kaniko --dockerfile=Dockerfile --destination=$REGISTRY/$IMG:$GIT_SHA --tarPath=/workspace/img.tar --no-push'
      } }
    }
    stage('SBOM + Scan') {
      parallel {
        stage('SBOM') { steps { container('trivy') {
          sh 'trivy image --input /workspace/img.tar --format cyclonedx --output sbom.cdx.json'
          archiveArtifacts 'sbom.cdx.json'
        } } }
        stage('Scan') { steps { container('trivy') {
          sh 'trivy image --input /workspace/img.tar --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed --format sarif --output scan.sarif'
          archiveArtifacts 'scan.sarif'
        } } }
      }
    }
    stage('Push + Sign') {
      when { branch 'main' }
      steps {
        container('kaniko') { sh 'kaniko --dockerfile=Dockerfile --destination=$REGISTRY/$IMG:$GIT_SHA' }
        container('cosign') {
          withCredentials([string(credentialsId: 'oidc-token', variable: 'OIDC')]) {
            sh 'cosign sign --yes $REGISTRY/$IMG:$GIT_SHA'
            sh 'cosign attest --yes --predicate sbom.cdx.json --type cyclonedx $REGISTRY/$IMG:$GIT_SHA'
          }
        }
      }
    }
  }
}
</code></pre>

<table>
<tr><th>Layer</th><th>Tool</th></tr>
<tr><td>Image scan</td><td>Trivy, Grype, Snyk Container, Wiz, Prisma Cloud</td></tr>
<tr><td>SBOM generation</td><td>Syft, Trivy (CycloneDX/SPDX)</td></tr>
<tr><td>Signing</td><td>Cosign keyless (Sigstore Fulcio + Rekor)</td></tr>
<tr><td>Provenance</td><td>SLSA Level 3 via in-toto attestations</td></tr>
<tr><td>Admission</td><td>Kyverno, Connaisseur, Sigstore policy-controller</td></tr>
<tr><td>Continuous</td><td>Trivy Operator (in-cluster), Wiz, Prisma</td></tr>
<tr><td>Triage</td><td>Defect Dojo, Dependency-Track</td></tr>
</table>

<p><strong>Production polish:</strong> use <strong>distroless</strong> or <strong>Chainguard images</strong> as base &mdash; they ship with near-zero CVEs by construction; pass <code>--ignore-unfixed</code> to Trivy so the gate only fails on actionable CVEs (someone has a fix available); maintain a <code>.trivyignore</code> with explicit expiry dates and ticket links for every accepted risk; layer scans &mdash; <strong>SCA</strong> in dependency files, <strong>SAST</strong> via CodeQL/Semgrep, <strong>image scan</strong> at build, <strong>continuous</strong> scan via Trivy Operator, <strong>runtime</strong> via Falco or Tetragon; gate Argo CD syncs on <strong>Cosign verified attestations</strong> via the policy-controller webhook so an unsigned image cannot deploy; rotate the Sigstore Rekor entries into your own append-only log if you need legal evidentiary value; for compliance-heavy environments, ship CIS Docker Benchmark reports and CIS K8s reports via <strong>kube-bench</strong> on a schedule; train teams to read SARIF in the GitHub Security tab rather than log scraping; and treat the SBOM as a release artefact &mdash; future CVE disclosures can be matched against your historical SBOMs to find affected deployments quickly.</p>'''

ANSWERS[29] = r'''<p><strong>Situation:</strong> the operations team manages clusters across on-prem, AWS EKS, Azure AKS, and edge sites, and wants a single pane of glass for cluster lifecycle, RBAC, observability, and app deployment via <strong>Rancher</strong>. CI/CD pipelines (GitHub Actions, Jenkins) need to interoperate with Rancher cleanly &mdash; not bypass it.</p>

<p><strong>Approach:</strong> install <strong>Rancher</strong> on a dedicated management cluster and import existing clusters via the Rancher agent. Use <strong>Rancher Fleet</strong> for GitOps across the fleet (it&rsquo;s the upstream Argo-CD-like controller built into Rancher). CI/CD pipelines push manifest changes to a config repo; Fleet reconciles; Rancher provides audit, RBAC, and the UI. For cluster lifecycle, use <strong>Rancher Provisioning v2</strong> with Cluster API providers (<strong>RKE2</strong>, <strong>K3s</strong>, or downstream EKS/AKS via cloud APIs).</p>

<pre><code># fleet.yaml at the root of an app repo
namespace: payments
helm:
  chart: ./chart
  values:
    image: { tag: ${{ env.IMAGE_TAG }} }
targetCustomizations:
  - name: prod-eu
    clusterSelector: { matchLabels: { env: prod, region: eu } }
    helm: { values: { replicas: 5 } }
  - name: edge
    clusterSelector: { matchLabels: { class: edge } }
    helm: { values: { replicas: 1, resources: { limits: { cpu: 200m, memory: 256Mi } } } }
---
# Bundle / GitRepo CR &mdash; Rancher Fleet&rsquo;s entry point
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata: { name: payments, namespace: fleet-default }
spec:
  repo: https://github.com/org/payments-config
  branch: main
  paths: [.]
  targets:
    - name: prod-clusters
      clusterSelector: { matchLabels: { env: prod } }
---
# .github/workflows/release.yml &mdash; CI bumps the tag in the config repo
- name: Bump tag in config repo
  run: |
    gh api repos/org/payments-config/contents/values.yaml \
      -X PUT -F message="bump to ${{ github.sha }}" \
      -F content=$(yq e '.image.tag = "${{ github.sha }}"' -o=json values.yaml | base64)
  env: { GH_TOKEN: ${{ secrets.CONFIG_PAT }} }
</code></pre>

<table>
<tr><th>Rancher feature</th><th>Use</th></tr>
<tr><td>Rancher Fleet</td><td>GitOps across fleet of clusters</td></tr>
<tr><td>Rancher Provisioning v2</td><td>Cluster lifecycle (RKE2, K3s, hosted)</td></tr>
<tr><td>Rancher RBAC</td><td>Centralised role bindings across clusters</td></tr>
<tr><td>Rancher Monitoring</td><td>kube-prometheus-stack pre-integrated</td></tr>
<tr><td>Rancher Logging</td><td>Fluent Bit/Fluentd to backends</td></tr>
<tr><td>Rancher Backups</td><td>Velero-based scheduled backups</td></tr>
<tr><td>Hardened RKE2 / K3s</td><td>Edge-friendly K8s distros, FIPS-validatable</td></tr>
</table>

<p><strong>Production polish:</strong> run Rancher itself with HA across 3 control-plane nodes &mdash; the management cluster is now critical infrastructure; back up the management cluster via Velero with off-region snapshots and test the restore quarterly; use <strong>Rancher SSO</strong> with your IdP (Okta, Azure AD, Keycloak) and map IdP groups to Rancher project roles &mdash; never rely on local users in prod; pin <strong>Rancher version</strong> across the fleet via the upgrade controller and follow the SUSE-recommended upgrade order (Rancher &rarr; downstream clusters); enable <strong>audit logging</strong> on Rancher to capture every API action and ship to your SIEM; for edge, prefer <strong>K3s</strong> + <strong>Fleet</strong> and design for offline operation &mdash; Fleet syncs idempotently; secret management routes through <strong>Rancher External Secrets</strong> or directly via <strong>External Secrets Operator</strong> with Vault/AWS SM/Azure KV; for compliance, the <strong>CIS scan</strong> built into Rancher generates per-cluster reports &mdash; schedule them; finally, when you outgrow Rancher (multi-tenant SaaS scale), the migration path is Argo CD ApplicationSets + Crossplane &mdash; plan it early rather than late.</p>'''

ANSWERS[30] = r'''<p><strong>Situation:</strong> the org wants a clean <strong>GitOps workflow</strong> for Kubernetes resources &mdash; CI builds and tests; CD reconciles from Git declaratively. The chosen stack is <strong>Argo CD</strong> for sync and <strong>GitHub Actions</strong> for build, with strict separation of concerns: the app repo never has cluster credentials, the config repo never has source code.</p>

<p><strong>Approach:</strong> two repos &mdash; <em>app</em> (source code, Dockerfile, unit tests, GH Actions for build/push) and <em>config</em> (Kustomize/Helm manifests, Argo CD Applications). CI in app repo builds the image, signs it (Cosign), and writes a single PR to the config repo bumping the image tag. Config repo PRs are reviewed (or auto-merged for non-prod), Argo CD watches the config repo, and reconciles to clusters. For multi-cluster, use <strong>ApplicationSet</strong>; for promotion across stages, use <strong>Kargo</strong>.</p>

<pre><code># app-repo .github/workflows/release.yml
on: { push: { branches: [main] } }
permissions: { contents: read, id-token: write }
jobs:
  build:
    runs-on: ubuntu-24.04
    outputs: { sha: ${{ github.sha }} }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/org/api:${{ github.sha }}
          provenance: true
          sbom: true
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/org/api:${{ github.sha }}
  bump:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          repository: org/config
          token: ${{ secrets.CONFIG_PAT }}
          path: config
      - run: |
          cd config/apps/api
          yq e -i '.spec.template.spec.containers[0].image = "ghcr.io/org/api:${{ github.sha }}"' deployment.yaml
          git config user.name 'gha-bot'
          git config user.email 'bot@org'
          git checkout -b bump/${{ github.sha }}
          git commit -am 'bump api to ${{ github.sha }}'
          git push origin bump/${{ github.sha }}
          gh pr create --title 'bump api' --body 'auto-promotion' --base main
        env: { GH_TOKEN: ${{ secrets.CONFIG_PAT }} }
---
# config-repo apps/api/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: api, namespace: argocd }
spec:
  project: prod
  source:
    repoURL: https://github.com/org/config
    path: apps/api
    targetRevision: HEAD
  destination: { namespace: api, server: https://kubernetes.default.svc }
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true, ApplyOutOfSyncOnly=true]
</code></pre>

<table>
<tr><th>Concern</th><th>2026 choice</th></tr>
<tr><td>GitOps controller</td><td>Argo CD (UI, multi-tenancy) or Flux (CRD-native, lighter)</td></tr>
<tr><td>Manifest packaging</td><td>Kustomize for envs, Helm for shared charts</td></tr>
<tr><td>Multi-cluster fan-out</td><td>Argo CD ApplicationSet + cluster generator</td></tr>
<tr><td>Promotion across stages</td><td>Kargo (formerly bake-off Argo CD-only PR-based)</td></tr>
<tr><td>Image automation</td><td>Argo CD Image Updater or Flux Image Automation</td></tr>
<tr><td>Drift backstop</td><td>Argo CD selfHeal + Kyverno admission policies</td></tr>
</table>

<p><strong>Production polish:</strong> the app repo never has cluster credentials &mdash; the only privilege it needs is a fine-scoped PAT to the config repo (or, better, a <strong>GitHub App</strong> token with contents: write only on that repo); review the bump PR for prod (auto-merge for staging) so a human is in the loop on production change; use <strong>Argo CD&rsquo;s</strong> <em>sync waves</em> and <em>health checks</em> to order CRDs &rarr; namespaces &rarr; controllers &rarr; apps &rarr; jobs; combine with <strong>Argo Rollouts</strong> for canary semantics; configure <strong>Argo CD diff customisations</strong> for fields managed by autoscalers (HPA replicas, VPA resources) so they don&rsquo;t flap; lock down the config repo with <strong>CODEOWNERS</strong> and <strong>required reviews</strong>; for promotion across dev &rarr; staging &rarr; prod use <strong>Kargo Stages</strong> with verification queries (Prometheus/Datadog) so promotion happens only when canary metrics are clean; pin the Argo CD version per cluster, run <strong>argocd-image-updater</strong> only in non-prod, and enforce signed images at admission via <strong>Kyverno verifyImages</strong> or <strong>Connaisseur</strong>; for secrets, use <strong>External Secrets Operator</strong> &mdash; never put plaintext secrets in the config repo; finally, run drift detection alerts (Argo CD <em>OutOfSync</em> webhook to Slack) so manual cluster edits are visible immediately.</p>'''

ANSWERS[31] = r'''<p><strong>Situation:</strong> a mobile app (React Native or Flutter) needs CI/CD that builds iOS+Android, runs unit and instrumented tests, signs builds, and uploads to <strong>App Store Connect</strong> and <strong>Google Play</strong>. The team wants automated TestFlight/Internal-track uploads on every merge and gated production rollouts.</p>

<p><strong>Approach:</strong> use <strong>Fastlane</strong> as the orchestrator (industry standard, both stores), <strong>EAS Build</strong> (Expo) or <strong>Xcode Cloud</strong> for managed iOS, and run on <strong>macOS runners</strong> in GitHub Actions for iOS, <strong>ubuntu-24.04</strong> for Android. Sign with <strong>fastlane match</strong> (encrypted Git repo of certificates) for iOS and a Play-managed signing key for Android. Test on real devices via <strong>BrowserStack App Live</strong>, <strong>AWS Device Farm</strong>, or <strong>Firebase Test Lab</strong>. Track crashes via <strong>Sentry</strong> or <strong>Firebase Crashlytics</strong>.</p>

<pre><code># .github/workflows/release-mobile.yml
name: release-mobile
on:
  push:
    tags: ['v*']
permissions: { contents: read }
jobs:
  ios:
    runs-on: macos-15
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.3', bundler-cache: true }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'yarn' }
      - run: yarn install --frozen-lockfile
      - run: bundle exec fastlane ios beta
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          APP_STORE_CONNECT_API_KEY_KEY: ${{ secrets.ASC_API_KEY }}
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          APP_STORE_CONNECT_API_KEY_ISSUER_ID: ${{ secrets.ASC_ISSUER }}
  android:
    runs-on: ubuntu-24.04
    timeout-minutes: 40
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '21' }
      - uses: gradle/actions/setup-gradle@v3
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'yarn' }
      - run: yarn install --frozen-lockfile
      - run: yarn jest --ci --coverage
      - run: bundle exec fastlane android internal
        env:
          PLAY_SERVICE_ACCOUNT_JSON: ${{ secrets.PLAY_SA_JSON }}
          ANDROID_KEYSTORE_B64: ${{ secrets.KEYSTORE_B64 }}
</code></pre>

<table>
<tr><th>Tool</th><th>Use</th></tr>
<tr><td>Fastlane match</td><td>Provisioning &amp; signing certs across team via encrypted Git</td></tr>
<tr><td>App Store Connect API</td><td>Replaces fragile Apple ID auth; OIDC-style key-based auth</td></tr>
<tr><td>EAS Build (Expo)</td><td>Managed builds; simplifies React Native release</td></tr>
<tr><td>Xcode Cloud</td><td>Apple-native CI; tighter integration but less flexible</td></tr>
<tr><td>BrowserStack / Device Farm / Test Lab</td><td>Real-device E2E testing</td></tr>
<tr><td>Detox / Maestro / Appium</td><td>UI testing frameworks for React Native</td></tr>
<tr><td>Sentry / Crashlytics</td><td>Crash reporting + symbolication</td></tr>
</table>

<p><strong>Production polish:</strong> use <strong>App Store Connect API key</strong> (not Apple ID + 2FA) for non-interactive uploads &mdash; rotate the key annually; with <strong>fastlane match</strong>, store the cert repo separately from app code with a different read group; encrypt build artefacts and upload to GitHub Releases for forensic recovery; for Android, prefer <strong>Play App Signing</strong> with an upload key in CI &mdash; lose the upload key, you can recover; lose the signing key, your app is dead; use <strong>staged rollouts</strong> on both stores (5%, 20%, 50%, 100%) and watch crash-free sessions via Sentry/Crashlytics &mdash; halt rollout if &lt;99.5%; for code-push style hotfixes (RN/Flutter only) use <strong>Expo Updates</strong> or <strong>App Center CodePush</strong> for JS-only changes &mdash; never abuse it for binary changes; gate iOS releases on TestFlight for at least 24 hours of internal testing; redact secrets in logs (Fastlane has a sensitive-output filter); finally, version your binary deterministically &mdash; use the <code>github.run_number</code> as the build number on Android and <code>increment_build_number</code> on iOS, with the semver tag as the human-readable version.</p>'''

ANSWERS[32] = r'''<p><strong>Situation:</strong> the platform team uses <strong>Custom Resource Definitions (CRDs)</strong> to model app config (e.g., a <code>Microservice</code> CRD that bundles Deployment + Service + HPA + ServiceMonitor). CI/CD must lint, version, and roll out CRDs cleanly without breaking existing custom resources.</p>

<p><strong>Approach:</strong> treat CRDs as a contract: schema-first design, semver, conversion webhooks for migration, and admission policies (Kyverno/Gatekeeper) to enforce required fields. Build CRDs with <strong>kubebuilder</strong> or <strong>operator-sdk</strong>; lint with <strong>kubeconform</strong> + <strong>kube-linter</strong>; render canonical YAML with <strong>controller-gen</strong>; ship the operator (controller binary + CRDs) as a Helm chart pinned per cluster via Argo CD. Use the <strong>v1alpha1 &rarr; v1beta1 &rarr; v1</strong> ladder for breaking changes with conversion webhooks.</p>

<pre><code># Makefile targets
manifests: ## Generate CRDs &amp; RBAC into config/crd
	controller-gen rbac:roleName=manager-role crd webhook \
	  paths="./..." output:crd:artifacts:config=config/crd/bases

# .github/workflows/operator.yml
name: operator
on: { push: { branches: [main] }, pull_request: {} }
permissions: { id-token: write, contents: read, packages: write }
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.24', cache: true }
      - run: make manifests
      - run: git diff --exit-code config/crd # fail if regenerated CRDs drift
      - run: make test # uses envtest (in-process etcd+API)
      - run: |
          go install sigs.k8s.io/kubebuilder/v4/test/e2e@latest
          make e2e
  lint-crd:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          curl -L https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz | tar xz
          ./kubeconform -strict -summary -schema-location default \
            -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{ .Group }}/{{ .ResourceKind }}_{{ .ResourceAPIVersion }}.json' \
            config/samples/*.yaml
  release:
    needs: [test, lint-crd]
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v6
        with: { push: true, tags: ghcr.io/org/microservice-operator:${{ github.ref_name }} }
      - run: helm package charts/microservice-operator
      - run: helm push *.tgz oci://ghcr.io/org/charts
</code></pre>

<table>
<tr><th>Concern</th><th>Practice</th></tr>
<tr><td>Schema design</td><td>OpenAPI v3 schema with required fields, enums, defaults</td></tr>
<tr><td>Versioning</td><td>v1alpha1 &rarr; v1beta1 &rarr; v1 with conversion webhooks</td></tr>
<tr><td>Validation</td><td>CEL validation rules in CRD (1.29+); admission webhook for cross-CR checks</td></tr>
<tr><td>Defaulting</td><td>Mutating webhook or schema defaults</td></tr>
<tr><td>Status subresource</td><td>Always enabled; spec/status separation prevents user races</td></tr>
<tr><td>Tests</td><td>envtest (kubebuilder), kuttl for end-to-end</td></tr>
<tr><td>Policy</td><td>Kyverno ClusterPolicy validating CRs at admission</td></tr>
</table>

<p><strong>Production polish:</strong> never reuse a field name with a different type across versions &mdash; if you need to change a field, deprecate, add the new one, write the conversion, then remove in a later major; CRD upgrades are global cluster mutations &mdash; test conversion webhooks with realistic stored objects via <strong>kuttl</strong> or <strong>chainsaw</strong>; emit Kubernetes Events from your controller for every state transition so users can <code>kubectl describe</code> and see what happened; expose Prometheus metrics from the controller-runtime metrics endpoint and create a default <strong>ServiceMonitor</strong>; ship a default <strong>PrometheusRule</strong> alerting on reconciliation failures and queue length; document the &ldquo;what happens if you delete the CR&rdquo; semantics &mdash; finalisers must be idempotent and bounded (don&rsquo;t block deletion forever on a transient external API); for security, the controller&rsquo;s ServiceAccount needs least-privilege RBAC limited to its own namespaces; use <strong>controller-runtime field selectors</strong> to scope watches; ship the operator at <strong>capability level 4 (Auto Pilot)</strong> per OperatorHub criteria where feasible; finally, when shipping breaking changes, communicate via <code>kubectl get crd &lt;name&gt; -o yaml</code> deprecation warnings and a release note checklist for cluster operators.</p>'''

ANSWERS[33] = r'''<p><strong>Situation:</strong> a <strong>Ruby on Rails</strong> monolith needs a CI/CD pipeline that runs RSpec unit + Capybara feature tests, lints with RuboCop, scans with Brakeman, and deploys to <strong>Heroku</strong> on green main &mdash; with database migrations executed safely.</p>

<p><strong>Approach:</strong> use GitHub Actions with <strong>service containers</strong> for Postgres + Redis, Ruby cache via <code>ruby/setup-ruby</code>, Selenium on a Chromium service container for system tests, parallelism via the official <code>parallel_tests</code> gem or Knapsack Pro for time-balanced sharding. For deploy, use Heroku&rsquo;s Container Registry (deprecating buildpacks for new apps) with a slim Dockerfile, and run migrations via a <code>release</code> phase command before traffic shifts.</p>

<pre><code># .github/workflows/rails.yml
name: rails
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres: { image: postgres:16-alpine, env: { POSTGRES_PASSWORD: postgres }, ports: [5432:5432], options: --health-cmd pg_isready }
      redis:    { image: redis:7-alpine, ports: [6379:6379] }
    strategy: { matrix: { ci_node_index: [0,1,2,3], ci_node_total: [4] } }
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.4', bundler-cache: true }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: 'yarn' }
      - run: yarn install --frozen-lockfile
      - run: bundle exec rails db:setup
        env: { DATABASE_URL: postgres://postgres:postgres@localhost/test, RAILS_ENV: test }
      - run: bundle exec rubocop --parallel
      - run: bundle exec brakeman --no-pager --exit-on-warn
      - run: bundle exec rspec --tag ~slow
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost/test
          REDIS_URL: redis://localhost:6379/0
          CI_NODE_INDEX: ${{ matrix.ci_node_index }}
          CI_NODE_TOTAL: ${{ matrix.ci_node_total }}
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          docker build -t registry.heroku.com/${{ secrets.HEROKU_APP }}/web .
          echo "${{ secrets.HEROKU_API_KEY }}" | docker login --username=_ --password-stdin registry.heroku.com
          docker push registry.heroku.com/${{ secrets.HEROKU_APP }}/web
          curl -n -X PATCH https://api.heroku.com/apps/${{ secrets.HEROKU_APP }}/formation \
            -H "Authorization: Bearer ${{ secrets.HEROKU_API_KEY }}" \
            -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
            -d "{\"updates\":[{\"type\":\"web\",\"docker_image\":\"$(docker inspect registry.heroku.com/${{ secrets.HEROKU_APP }}/web --format={{.Id}})\"}]}"
</code></pre>

<table>
<tr><th>Choice</th><th>Trade-off</th></tr>
<tr><td>GH Actions matrix sharding</td><td>Free-ish, simple; manually balance buckets</td></tr>
<tr><td>Knapsack Pro</td><td>Time-balanced auto-sharding; paid; saves real wall-clock</td></tr>
<tr><td>Heroku Container Registry</td><td>Modern; works with Dockerfile</td></tr>
<tr><td>Heroku release phase</td><td>Runs migrations before slug rollout; standard Rails pattern</td></tr>
<tr><td>Render / Fly.io / Railway</td><td>2026 Heroku replacements; cheaper, modern feature set</td></tr>
</table>

<p><strong>Production polish:</strong> Heroku is past its peak &mdash; for new Rails apps in 2026 evaluate <strong>Render</strong>, <strong>Fly.io</strong>, or <strong>Railway</strong> first (cheaper, faster region availability, modern feature flags); but for existing Heroku apps the workflow is solid; set the Heroku <strong>release phase</strong> command to <code>bundle exec rails db:migrate</code> in <code>Procfile</code> &mdash; release runs <em>before</em> dynos restart, so migrations finish before traffic flips; use <strong>strong_migrations</strong> gem to fail CI on dangerous patterns (e.g., adding a NOT NULL column without default on a large table); for zero-downtime, use the <strong>expand/contract</strong> pattern &mdash; deploy compatible code, run migration in a separate release, then deploy code that uses the new schema; cache <strong>node_modules</strong> + <strong>vendor/bundle</strong> via <code>bundler-cache: true</code> + <code>cache: 'yarn'</code>; run <strong>system tests</strong> in headless Chrome via <code>selenium-webdriver</code>; ship the asset pipeline (<code>esbuild</code> or Vite + jsbundling-rails) inside the Docker image to avoid Heroku&rsquo;s slow asset compile; use <strong>Sentry</strong> for errors and the <strong>Heroku Postgres metrics dashboard</strong> for DB health; configure <strong>Heroku review apps</strong> for PR previews so QA happens on real infrastructure; finally, version your slug with <code>HEROKU_SLUG_COMMIT</code> echoed at app boot so production logs always know which commit is running.</p>'''

ANSWERS[34] = r'''<p><strong>Situation:</strong> the security team mandates <strong>end-to-end encryption</strong> for data at rest and in transit across all environments. CI/CD must enforce TLS for every service, encrypt persistent volumes with customer-managed keys, manage secrets via a vault, and prove (auditably) that no plaintext data ever crosses an untrusted boundary.</p>

<p><strong>Approach:</strong> use <strong>cert-manager</strong> + a private CA (Vault PKI, AWS Private CA, smallstep) to issue certificates for every Service; enable <strong>mTLS by default</strong> via a service mesh (<strong>Istio ambient mode</strong>, <strong>Linkerd</strong>, or <strong>Cilium Service Mesh</strong>). Encrypt at rest via <strong>EBS/Disk encryption with KMS CMKs</strong>, K8s <strong>Secrets encryption-at-rest with KMS v2</strong>, and database TDE. Manage secrets via <strong>HashiCorp Vault</strong>, <strong>AWS Secrets Manager</strong>, or <strong>External Secrets Operator</strong>; never let plaintext secrets touch Git or container images.</p>

<pre><code># cert-manager Issuer + automatic Service mesh certificate
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: vault-pki }
spec:
  vault:
    server: https://vault.platform.svc:8200
    path: pki/sign/internal
    auth: { kubernetes: { role: cert-manager, mountPath: /v1/auth/kubernetes } }
---
# Istio ambient PeerAuthentication forces mTLS strict
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: istio-system }
spec: { mtls: { mode: STRICT } }
---
# K8s API server EncryptionConfiguration with KMS v2
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources: [secrets, configmaps]
    providers:
      - kms:
          apiVersion: v2
          name: aws-kms
          endpoint: unix:///var/run/kmsplugin/socket.sock
      - identity: {}
---
# External Secrets Operator pulling from Vault
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: db-creds, namespace: api }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: vault, kind: ClusterSecretStore }
  target: { name: db-creds }
  data:
    - { secretKey: url, remoteRef: { key: secret/data/api/db, property: url } }
</code></pre>

<table>
<tr><th>Plane</th><th>Mechanism (2026)</th></tr>
<tr><td>In-transit (external)</td><td>TLS 1.3 only via cloud LB; HSTS preload</td></tr>
<tr><td>In-transit (mesh)</td><td>mTLS via Istio ambient / Linkerd / Cilium</td></tr>
<tr><td>At rest (volumes)</td><td>EBS/Disk/PD encryption with customer-managed KMS keys</td></tr>
<tr><td>At rest (Secrets)</td><td>K8s EncryptionConfiguration with KMS v2 (1.29+)</td></tr>
<tr><td>At rest (DB)</td><td>TDE + per-tenant column-level encryption where required</td></tr>
<tr><td>Secret management</td><td>Vault + External Secrets Operator</td></tr>
<tr><td>Key rotation</td><td>Vault transit, KMS automatic rotation, cert-manager renewBefore</td></tr>
</table>

<p><strong>Production polish:</strong> default to <strong>STRICT mTLS</strong> in the mesh and explicitly allow plaintext only at well-documented boundaries (legacy services); rotate certificates with short TTL (24h&ndash;72h) so a compromise window is small; rotate KMS CMKs annually with automatic key rotation enabled; never let CI logs print plaintext &mdash; use <code>::add-mask::</code> in GH Actions and Jenkins <code>maskPasswords</code>; gate on <strong>kube-bench</strong>, <strong>kubescape</strong>, and CIS scans in CI to verify cluster encryption settings remain on; export <strong>access logs from the cloud LB</strong> and audit logs from the K8s API server, ship to immutable storage (S3 Object Lock); enforce TLS 1.3 minimum and disable old ciphers via Envoy/NGINX tuning; for FIPS-required workloads, use FIPS-validated builds (Red Hat OpenShift, Bottlerocket FIPS, Talos FIPS); run <strong>tlsx</strong> or <strong>testssl.sh</strong> in CI against staging endpoints to verify configuration; for client/server cert chain debugging, ship a <strong>certificate inventory dashboard</strong> from <strong>cert-manager metrics</strong> showing issuer, expiry, owner; finally, add a <strong>Kyverno policy</strong> that rejects any Service without a TLS-terminating annotation and any PVC without a KMS-backed StorageClass &mdash; the easiest way to prevent regression.</p>'''

ANSWERS[35] = r'''<p><strong>Situation:</strong> a blockchain product (smart contracts plus indexer + frontend) needs CI/CD that compiles Solidity, runs forge tests with fuzzing, performs static analysis, deploys contracts via signed transactions, and ships supporting services to AWS. Bugs in deployed contracts cost real money, so the bar is materially higher than typical web CI.</p>

<p><strong>Approach:</strong> use <strong>Foundry</strong> as the toolchain &mdash; <code>forge build</code>, <code>forge test</code> with invariant + fuzz testing, <code>forge coverage</code>, <strong>Slither</strong> + <strong>Mythril</strong> for static analysis, optionally <strong>Halmos</strong> or <strong>Certora</strong> for formal verification of critical paths. Run a <strong>mainnet fork</strong> in CI to catch integration regressions. Deploy contracts via <strong>OpenZeppelin Defender</strong> or <strong>Foundry scripts</strong> using a hardware-wallet-backed key (Frame, Ledger, or AWS KMS via <code>cast wallet</code>). Off-chain services (indexer, frontend, oracle relayer) ship as containers to ECS/EKS via the standard pattern.</p>

<pre><code># .github/workflows/contracts.yml
name: contracts
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }
jobs:
  forge:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: foundry-rs/foundry-toolchain@v1
      - run: forge build --sizes
      - run: forge test --gas-report --fuzz-runs 10000
        env: { FOUNDRY_PROFILE: ci }
      - run: forge coverage --report lcov
      - uses: codecov/codecov-action@v4
        with: { files: lcov.info }
  static:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: crytic/slither-action@v0.4
        with: { sarif: slither.sarif, fail-on: high }
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: slither.sarif }
  fork-test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: foundry-rs/foundry-toolchain@v1
      - run: forge test --fork-url ${{ secrets.MAINNET_RPC }} --match-contract Integration
  deploy-staging:
    needs: [forge, static, fork-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions: { id-token: write }
    steps:
      - uses: actions/checkout@v4
      - uses: foundry-rs/foundry-toolchain@v1
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: ${{ secrets.AWS_KMS_ROLE }}, aws-region: us-east-1 }
      - run: |
          forge script script/Deploy.s.sol --rpc-url $SEPOLIA_RPC \
            --aws --keystore-account-name deployer-staging \
            --broadcast --verify
</code></pre>

<table>
<tr><th>Stage</th><th>Tooling (2026)</th></tr>
<tr><td>Build/test</td><td>Foundry, Hardhat (declining), Truffle (deprecated)</td></tr>
<tr><td>Static analysis</td><td>Slither, Aderyn, Wake, Mythril</td></tr>
<tr><td>Formal verification</td><td>Halmos, Kontrol, Certora</td></tr>
<tr><td>Deployment signing</td><td>OpenZeppelin Defender, AWS KMS, Ledger via Frame</td></tr>
<tr><td>Off-chain services</td><td>Containers on ECS/EKS, Argo CD GitOps</td></tr>
<tr><td>Indexers</td><td>The Graph hosted/self-hosted, Subsquid, Goldsky</td></tr>
<tr><td>Monitoring</td><td>OpenZeppelin Defender Sentinels, Tenderly Alerts</td></tr>
</table>

<p><strong>Production polish:</strong> deployments are immutable &mdash; require multi-sig (Safe / Gnosis Safe) for mainnet writes, never a single-key deployment role; use <strong>timelocks</strong> (24&ndash;48h) for upgradeable contracts so the community can audit pending changes; pin every dep by hash including Solc compiler version (<code>solc-bin</code> attestations); audit every external call with <strong>checks-effects-interactions</strong> and reentrancy guards; run <strong>Echidna</strong> in addition to Foundry fuzzing for adversarial property testing; produce a <strong>deployment plan document</strong> auto-generated by the script with target addresses, constructor args, and verifier links &mdash; humans review before mainnet broadcast; use <strong>Etherscan/Sourcify verification</strong> in CI so the source code is immediately visible after deploy; emit events generously &mdash; indexers depend on them; for upgrades, prefer the <strong>UUPS proxy</strong> pattern with a state-migration script; for the supporting services, the off-chain CI/CD is conventional &mdash; Docker image, ECS deploy, OIDC auth &mdash; but ensure the relayer&rsquo;s signing keys live in <strong>KMS</strong> with strict access control and the indexer can recover from chain reorgs (idempotent processing keyed on tx hash + log index).</p>'''

ANSWERS[36] = r'''<p><strong>Situation:</strong> the QA team wants <strong>continuous testing</strong> in the CI/CD pipeline &mdash; unit, integration, contract, and full E2E browser tests &mdash; orchestrated by Jenkins with <strong>Selenium</strong> for cross-browser checks. The current setup runs E2E only nightly, missing regressions until release day.</p>

<p><strong>Approach:</strong> shift the test pyramid into the pipeline: unit on every commit (seconds), integration on PR (minutes), E2E in parallel on PR + post-deploy smoke (minutes via a Selenium Grid). Run the Selenium Grid on Kubernetes via the <strong>Zalando Selenium Operator</strong> or the official <strong>Aerokube Selenoid/Moon</strong> stack, dynamically scaling browser pods. Modern alternatives &mdash; <strong>Playwright</strong>, <strong>Cypress</strong>, <strong>WebdriverIO</strong> &mdash; are usually preferable to raw Selenium for new projects; this answer covers Selenium because it&rsquo;s the named tool.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent { kubernetes { yaml &apos;&apos;&apos;
spec:
  containers:
    - { name: builder,    image: maven:3.9-eclipse-temurin-21, command: [sleep], args: [99d] }
    - { name: kubectl,    image: bitnami/kubectl:1.31,         command: [sleep], args: [99d] }
&apos;&apos;&apos; } }
  stages {
    stage('Unit') {
      steps { container('builder') { sh 'mvn -B -T 1C test' } }
      post { always { junit 'target/surefire-reports/*.xml' } }
    }
    stage('Integration') {
      steps { container('builder') { sh 'mvn -B verify -DskipUnitTests' } }
      post { always { junit 'target/failsafe-reports/*.xml' } }
    }
    stage('Deploy preview') {
      steps { container('kubectl') {
        sh 'kubectl apply -f preview/namespace-${BUILD_NUMBER}.yaml'
        sh 'kubectl rollout status deploy/api -n preview-${BUILD_NUMBER} --timeout=5m'
      } }
    }
    stage('Selenium E2E') {
      parallel {
        stage('chrome') {
          steps { container('builder') {
            sh 'mvn -B -P e2e -Dbrowser=chrome -Dgrid=http://selenium-hub.test:4444 verify'
          } }
        }
        stage('firefox') {
          steps { container('builder') {
            sh 'mvn -B -P e2e -Dbrowser=firefox -Dgrid=http://selenium-hub.test:4444 verify'
          } }
        }
      }
    }
    stage('Tear down preview') {
      steps { container('kubectl') {
        sh 'kubectl delete ns preview-${BUILD_NUMBER}'
      } }
    }
  }
}
---
# Selenium Grid Helm values (aerokube/moon or selenium/standalone)
# Run on K8s with autoscaling browser pods per session
selenium-hub: { replicas: 2 }
chrome:  { replicas: 0, autoscaling: { minReplicas: 0, maxReplicas: 50 } }
firefox: { replicas: 0, autoscaling: { minReplicas: 0, maxReplicas: 20 } }
</code></pre>

<table>
<tr><th>Layer</th><th>Tool / approach</th></tr>
<tr><td>Unit</td><td>JUnit5/Vitest/pytest, runs on every commit</td></tr>
<tr><td>Integration</td><td>Testcontainers (real DBs in Docker), runs on PR</td></tr>
<tr><td>Contract</td><td>Pact, Spring Cloud Contract, runs on PR</td></tr>
<tr><td>E2E browser</td><td>Selenium Grid, Playwright, Cypress &mdash; on preview env per PR</td></tr>
<tr><td>Visual</td><td>Percy, Applitools, Chromatic</td></tr>
<tr><td>Performance</td><td>k6, Locust, Lighthouse CI</td></tr>
<tr><td>Smoke (post-deploy)</td><td>Health checks + critical user journeys, &lt; 2 min</td></tr>
</table>

<p><strong>Production polish:</strong> use <strong>preview environments</strong> per PR (vCluster, ephemeral namespace, or Kustomize overlay) so each E2E run gets a clean stack &mdash; flaky tests caused by shared state evaporate; report Selenium failures with a <strong>screenshot + video + page source</strong> archived to S3 for forensic analysis (Selenium 4 records natively, Aerokube Moon makes it easy); split E2E by tag (<code>@smoke</code>, <code>@regression</code>, <code>@nightly</code>) so PRs run smoke and regression while heavy suites run nightly; flake quarantine &mdash; auto-detect tests that fail intermittently and tag them, run separately with retries, and require fixing within a SLA (otherwise prune); use <strong>retry-on-failure once</strong> for E2E (cope with browser flakiness) but never for unit tests (mask real bugs); shift visual regression via <strong>Percy</strong> or <strong>Applitools</strong> &mdash; far stronger than DOM assertions; ship Lighthouse CI results to monitor performance budgets; for new projects in 2026, prefer <strong>Playwright</strong> over Selenium &mdash; faster, native auto-wait, tracing built in; finally, treat E2E failures as production-impacting incidents &mdash; investigate within 24 hours, never just retry until green.</p>'''

ANSWERS[37] = r'''<p><strong>Situation:</strong> a workload&rsquo;s scaling driver is not CPU but a <strong>custom metric</strong> &mdash; queue depth, in-flight requests, GPU utilisation, or a SaaS provider&rsquo;s rate limit budget. CI/CD must deploy autoscaling rules that react fast and accurately, including scale-to-zero for cost.</p>

<p><strong>Approach:</strong> use <strong>KEDA</strong> (Kubernetes Event-Driven Autoscaler) &mdash; it has 60+ scalers in 2026 (Kafka, RabbitMQ, NATS, SQS, Redis, Prometheus, Datadog, Cron, GitHub Actions, etc.) and can scale Deployments down to zero. For metrics that aren&rsquo;t in a built-in scaler, use the <strong>Prometheus scaler</strong> with a query that returns the desired signal. Wire <strong>HPA</strong> or <strong>ScaledJob</strong> via KEDA&rsquo;s <code>ScaledObject</code> CRD; ship the YAML through GitOps. Pair with <strong>Karpenter</strong> for just-in-time node provisioning so pod scale-up doesn&rsquo;t starve.</p>

<pre><code># ScaledObject driving by Kafka consumer lag
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata: { name: order-consumer, namespace: orders }
spec:
  scaleTargetRef: { name: order-consumer }
  minReplicaCount: 0
  maxReplicaCount: 200
  pollingInterval: 15
  cooldownPeriod: 120
  advanced:
    horizontalPodAutoscalerConfig:
      behavior:
        scaleDown:
          policies: [{ type: Percent, value: 50, periodSeconds: 60 }]
          stabilizationWindowSeconds: 300
        scaleUp:
          policies: [{ type: Percent, value: 100, periodSeconds: 15 }]
          stabilizationWindowSeconds: 0
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka.kafka.svc:9092
        consumerGroup: orders
        topic: orders
        lagThreshold: '50'
---
# ScaledObject driving by a Prometheus query (custom SaaS rate-limit budget)
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata: { name: webhook-fanout, namespace: integrations }
spec:
  scaleTargetRef: { name: webhook-fanout }
  minReplicaCount: 1
  maxReplicaCount: 30
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prom.monitoring.svc:9090
        threshold: '0.7'
        query: |
          (saas_remaining_quota / saas_quota_limit)
</code></pre>

<table>
<tr><th>Lever</th><th>Effect</th></tr>
<tr><td>minReplicaCount: 0</td><td>Scale to zero when idle &mdash; cost win for spiky workloads</td></tr>
<tr><td>scaleUp 100% per 15s</td><td>Aggressive scale-out for queue spikes</td></tr>
<tr><td>scaleDown 50% per 60s + 300s window</td><td>Avoid thrash on bursty traffic</td></tr>
<tr><td>pollingInterval: 15</td><td>Lower = faster reaction, higher = less metric API load</td></tr>
<tr><td>ScaledJob (vs ScaledObject)</td><td>Use for one-shot work (Lambda-like batch processors)</td></tr>
<tr><td>Karpenter NodePool</td><td>Provisions matching nodes when KEDA scales pods up</td></tr>
</table>

<p><strong>Production polish:</strong> always pair KEDA with <strong>HPA-aware</strong> handling of <em>graceful shutdown</em> &mdash; consumers must drain their batch within <code>terminationGracePeriodSeconds</code> on scale-down, otherwise messages double-process; for queue workloads, configure <strong>idempotency keys</strong> on the consumer so retries are safe; size <strong>maxReplicaCount</strong> to match the broker&rsquo;s partition count (Kafka) or queue concurrency limit (SQS) &mdash; provisioning more pods than partitions wastes resources; observe the <strong>desired/current</strong> replica gauges from KEDA in Grafana to tune behavior parameters; for ScaledJobs, set <code>maxReplicaCount</code> sensibly to avoid runaway parallelism; for Prometheus-driven scaling, write a recording rule for the metric so the scaler queries a fast, pre-computed series; combine with <strong>Pod Disruption Budgets</strong> so cluster-autoscaler can&rsquo;t evict the entire fleet during scale-down; use <strong>VPA in recommend mode</strong> (Off, then read recommendations) to right-size pod CPU/memory requests so HPA decisions reflect real headroom; finally, surface scaling decisions as Kubernetes Events and ship to Slack so on-call sees auto-scaling in real time &mdash; mystery scale events erode trust quickly.</p>'''

ANSWERS[38] = r'''<p><strong>Situation:</strong> the team needs CI/CD that delivers to <strong>on-premise environments</strong> from GitHub Actions &mdash; air-gapped, behind firewalls, no inbound access to the cluster API. The deploy must be auditable and survive temporary network outages.</p>

<p><strong>Approach:</strong> default to <strong>pull-based GitOps</strong> &mdash; CI builds and pushes images to an on-prem registry (Harbor, JFrog, or a registry mirror), then writes a manifest tag bump to a config repo. <strong>Argo CD</strong> or <strong>Flux</strong> running inside the on-prem cluster watches the config repo and reconciles. CI never touches the cluster API directly. For air-gapped, mirror images via <strong>Harbor replication</strong> over a one-way diode or via signed bundles with <strong>oras</strong>.</p>

<pre><code># .github/workflows/onprem.yml
name: onprem
on: { push: { branches: [main] } }
permissions: { contents: read }
jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: harbor.corp.example.com
          username: ${{ secrets.HARBOR_USER }}
          password: ${{ secrets.HARBOR_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: harbor.corp.example.com/apps/api:${{ github.sha }}
          provenance: true
          sbom: true
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes harbor.corp.example.com/apps/api:${{ github.sha }}
  bump-config:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { repository: org/onprem-config, token: ${{ secrets.CONFIG_PAT }} }
      - run: |
          yq e -i '.spec.template.spec.containers[0].image = "harbor.corp.example.com/apps/api:${{ github.sha }}"' apps/api/deploy.yaml
          git config user.email bot@org
          git config user.name gha-bot
          git commit -am 'bump api ${{ github.sha }}'
          git push
---
# On-prem cluster: Argo CD pulls from internal git mirror
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: api, namespace: argocd }
spec:
  source: { repoURL: https://gitlab.corp.example.com/onprem-config, path: apps/api }
  destination: { namespace: api, server: https://kubernetes.default.svc }
  syncPolicy: { automated: { prune: true, selfHeal: true } }
</code></pre>

<table>
<tr><th>Pattern</th><th>When it fits</th></tr>
<tr><td>Pull-based GitOps (Argo CD/Flux)</td><td>Default; cluster reaches out, no inbound rules</td></tr>
<tr><td>Self-hosted runners + ARC</td><td>For non-K8s targets (VMware, bare metal, Windows)</td></tr>
<tr><td>Tailscale / Cloudflare Tunnel / Teleport</td><td>Zero-trust mesh for runner-to-target</td></tr>
<tr><td>Harbor replication</td><td>One-way image sync into air-gapped registry</td></tr>
<tr><td>oras + signed bundles</td><td>Manual ferry across diodes; verify signatures on import</td></tr>
<tr><td>Internal Git mirror</td><td>Argo CD reads from on-prem GitLab/Gitea, not GitHub directly</td></tr>
</table>

<p><strong>Production polish:</strong> air-gapped environments have multiple regulatory drivers &mdash; document explicitly which controls (FedRAMP, ITAR, GDPR data residency) apply and design accordingly; for one-way diode networks, mirror images and config bundles via <strong>oras</strong>, sign every artefact with <strong>Cosign keyless</strong> in cloud and verify with <strong>Sigstore policy-controller</strong> on the on-prem side; Argo CD running on-prem must point at an <strong>on-prem Git</strong> mirror (GitLab CE, Gitea, or an internal GitHub Enterprise) &mdash; mirrored from the cloud Git via a controlled sync job; secrets land via <strong>Vault</strong> (on-prem instance) accessed by External Secrets Operator &mdash; never copy plaintext secrets across the boundary; for runner connectivity (when push is unavoidable), use <strong>step-security/harden-runner</strong> with strict egress allow-lists, ephemeral runners, and rotate the runner image weekly; audit every cross-boundary action via the on-prem SIEM; for high-security environments, consider <strong>Talos Linux</strong> (no SSH, KubeAPI-only management) as the K8s distribution; finally, run <strong>chaos drills</strong> simulating WAN outage &mdash; the cluster should keep serving traffic and reconcile when connectivity returns; if reconciliation re-orders things badly, fix the manifests.</p>'''

ANSWERS[39] = r'''<p><strong>Situation:</strong> an event-driven application using Kafka topics and gRPC services on Kubernetes needs a CI/CD pipeline that handles schema compatibility, autoscales consumers off lag, and supports independent deployment of producers and consumers without dropping events.</p>

<p><strong>Approach:</strong> separate <em>schema</em>, <em>producer</em>, <em>consumer</em>, and <em>broker</em> lifecycles. Schemas live in a <strong>Schema Registry</strong> (Confluent, Apicurio, AWS Glue) with backward+forward compatibility enforced in CI. Producers/consumers ship as containers via standard GitOps. Brokers run on K8s via <strong>Strimzi</strong> (Kafka), <strong>NATS Operator</strong>, or <strong>RabbitMQ Cluster Operator</strong>. Use <strong>KEDA</strong> for consumer autoscaling driven by lag/queue depth. For workflow orchestration above raw events, use <strong>Temporal</strong>, <strong>Knative Eventing</strong>, or <strong>Argo Events</strong>.</p>

<pre><code># Strimzi KafkaTopic CRD &mdash; topic config in Git
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata: { name: orders, namespace: kafka, labels: { strimzi.io/cluster: prod } }
spec: { partitions: 24, replicas: 3, config: { retention.ms: '604800000' } }
---
# CI: schema compatibility check
- name: Schema compat
  run: |
    docker run --rm -v $PWD:/work confluentinc/cp-schema-registry-client:7.6 \
      schema-registry-client check-compatibility --subject orders-value \
      --schema-file /work/schemas/orders-v3.avsc \
      --url http://schema-registry:8081
---
# KEDA scaling on Kafka lag (defined earlier in Q37)
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata: { name: order-projector, namespace: projections }
spec:
  scaleTargetRef: { name: order-projector }
  minReplicaCount: 0
  maxReplicaCount: 24  # match partition count
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: prod-kafka-bootstrap:9092
        consumerGroup: order-projector
        topic: orders
        lagThreshold: '100'
---
# Argo Events Sensor: trigger workflow on incoming event
apiVersion: argoproj.io/v1alpha1
kind: Sensor
metadata: { name: order-fulfilment, namespace: argo-events }
spec:
  dependencies:
    - name: order-event
      eventSourceName: kafka
      eventName: orders
  triggers:
    - template:
        name: fulfil
        argoWorkflow:
          operation: submit
          source: { resource: { ... } }
</code></pre>

<table>
<tr><th>Concern</th><th>Tooling (2026)</th></tr>
<tr><td>Brokers on K8s</td><td>Strimzi, RabbitMQ Cluster Operator, NATS Operator</td></tr>
<tr><td>Schema registry</td><td>Confluent, Apicurio, AWS Glue Schema Registry</td></tr>
<tr><td>Event spec</td><td>CloudEvents (envelope standard)</td></tr>
<tr><td>Workflows / Sagas</td><td>Temporal, Knative Eventing, Argo Events</td></tr>
<tr><td>Autoscaling</td><td>KEDA (Kafka, RabbitMQ, NATS, SQS scalers)</td></tr>
<tr><td>Contract testing</td><td>Pact, Microcks (AsyncAPI)</td></tr>
<tr><td>Tracing</td><td>OpenTelemetry context propagation in headers</td></tr>
</table>

<p><strong>Production polish:</strong> use a <strong>schema registry</strong> with strict <strong>BACKWARD_TRANSITIVE</strong> compatibility &mdash; new producer schemas must be readable by all currently deployed consumers; add a CI step that diffs the new schema vs the registered one and fails on incompatible changes; for major version bumps that <em>are</em> incompatible, dual-publish (old+new versions on different topics) until consumers migrate; design every consumer to be <strong>idempotent</strong> on (event ID + offset) keys &mdash; redeploys, restarts, and partition rebalances cause replays; never use <em>at-most-once</em> for business events &mdash; <em>at-least-once</em> + idempotency is correct; instrument <strong>OpenTelemetry</strong> with W3C trace context propagated through Kafka headers (<code>traceparent</code>, <code>tracestate</code>) so distributed traces span async boundaries; alert on consumer lag SLOs &mdash; not raw lag (which spikes are normal) but the burn rate of the lag SLO; for <strong>Sagas</strong> (multi-step workflows), use <strong>Temporal</strong> for durable execution rather than rolling your own state machine; partition assignment changes during deploy &mdash; use the cooperative-sticky assignor in modern Kafka clients to avoid stop-the-world rebalances; finally, exercise broker upgrades quarterly via the Strimzi upgrade procedure with a real test workload &mdash; major version bumps occasionally surface protocol issues that quiet topics never reveal.</p>'''

ANSWERS[40] = r'''<p><strong>Situation:</strong> the team wants <strong>automated canary releases</strong> on Kubernetes orchestrated by Jenkins &mdash; ship a small percentage of traffic to the new version, observe metrics, and roll back automatically if SLOs degrade. No more 3am pager events from bad deploys.</p>

<p><strong>Approach:</strong> install <strong>Argo Rollouts</strong> or <strong>Flagger</strong> in-cluster &mdash; both replace the Deployment controller with a progressive-delivery controller that integrates with the service mesh or ingress for traffic shifting and queries Prometheus/Datadog for analysis. Jenkins triggers the deploy by updating the Rollout image; Argo Rollouts owns the canary lifecycle. Avoid implementing canary in Jenkins itself &mdash; mesh+controller is far more reliable than imperative kubectl loops.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent any
  stages {
    stage('Build') { steps { sh 'docker build -t $REG/api:$GIT_SHA . &amp;&amp; docker push $REG/api:$GIT_SHA' } }
    stage('Promote canary') {
      steps {
        sh &apos;&apos;&apos;
          kubectl argo rollouts set image api api=$REG/api:$GIT_SHA -n prod
          kubectl argo rollouts status api -n prod --watch --timeout 30m
        &apos;&apos;&apos;
      }
    }
  }
  post {
    failure {
      sh 'kubectl argo rollouts abort api -n prod || true'
    }
  }
}
---
# Argo Rollout: canary 5% -&gt; 25% -&gt; 50% -&gt; 100% with metric analysis
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: api, namespace: prod }
spec:
  replicas: 10
  strategy:
    canary:
      canaryService: api-canary
      stableService: api-stable
      trafficRouting: { istio: { virtualService: { name: api } } }
      steps:
        - setWeight: 5
        - pause: { duration: 5m }
        - analysis: { templates: [{ templateName: success-rate }] }
        - setWeight: 25
        - pause: { duration: 5m }
        - analysis: { templates: [{ templateName: success-rate }, { templateName: latency-p99 }] }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: success-rate, namespace: prod }
spec:
  metrics:
    - name: success-rate
      successCondition: result[0] &gt;= 0.99
      failureLimit: 1
      provider:
        prometheus:
          address: http://prom.monitoring.svc:9090
          query: |
            sum(rate(http_requests_total{service="api",code!~"5.."}[2m]))
            / sum(rate(http_requests_total{service="api"}[2m]))
</code></pre>

<table>
<tr><th>Choice</th><th>Trade-off</th></tr>
<tr><td>Argo Rollouts</td><td>UI, integrates well with Argo CD, Anthropic-friendly</td></tr>
<tr><td>Flagger</td><td>Older, Flux-friendly, very flexible mesh integrations</td></tr>
<tr><td>Service mesh traffic shift</td><td>Most accurate but requires mesh (Istio, Linkerd)</td></tr>
<tr><td>Ingress controller weights</td><td>NGINX/Traefik weighted backends; simpler, less precise</td></tr>
<tr><td>analysis on Prometheus</td><td>Default; pluggable to Datadog, NewRelic, CloudWatch</td></tr>
</table>

<p><strong>Production polish:</strong> always run <strong>analysis steps</strong> with both a success metric (error rate &lt; 1%, e.g.) and a latency metric (p99 &lt; baseline + N%) &mdash; either failing aborts the rollout; set <code>failureLimit: 1</code> so a single bad measurement halts before damage spreads; choose the <strong>weight steps</strong> conservatively for sensitive workloads (1%, 5%, 25%, 50%, 100%) and aggressively for low-stakes (10%, 50%, 100%); pair canary with <strong>preStop hooks</strong> + <code>terminationGracePeriodSeconds</code> so old pods drain cleanly; use <strong>experimental analysis runs</strong> (kayenta-style) on baseline vs canary &mdash; same load split between identical hardware to control for noise; for stateful workloads, canary with care &mdash; database schema changes use expand/contract, not canary; emit Kubernetes Events on every Rollout phase and ship to Slack so the team sees the rollout progressing live; for instant rollback, <code>kubectl argo rollouts abort</code> aborts and shifts 100% back to stable in seconds; finally, keep a <strong>post-deploy verification dashboard</strong> with a 24-hour lookback &mdash; sometimes regressions only surface under daily traffic patterns and you want explicit confirmation that the deploy is healthy.</p>'''

ANSWERS[41] = r'''<p><strong>Situation:</strong> a PHP application (Laravel or Symfony) needs a CI/CD pipeline with PHPUnit unit + integration tests, PHPStan static analysis, code style via PHP-CS-Fixer, and deployment to <strong>Azure Web App for Containers</strong>. Migrations must run pre-traffic-flip; secrets via Azure Key Vault.</p>

<p><strong>Approach:</strong> use GitHub Actions with the <strong>shivammathur/setup-php</strong> action for fast PHP installs, <strong>service containers</strong> for Postgres/Redis, <strong>Composer</strong> caching keyed on <code>composer.lock</code>. Build a slim multi-stage Docker image with <code>php:8.3-fpm-alpine</code> + <strong>Caddy</strong> or <strong>Nginx Unit</strong>. Push to <strong>Azure Container Registry</strong>; deploy via <strong>azure/webapps-deploy@v3</strong> using <strong>OIDC</strong> federation. Run migrations in a deployment slot before swapping into production.</p>

<pre><code># .github/workflows/php.yml
name: php
on: { push: { branches: [main] }, pull_request: {} }
permissions: { id-token: write, contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres: { image: postgres:16-alpine, env: { POSTGRES_PASSWORD: t }, ports: [5432:5432] }
      redis:    { image: redis:7-alpine, ports: [6379:6379] }
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with: { php-version: '8.3', extensions: 'pdo_pgsql, redis, mbstring, intl', coverage: pcov }
      - uses: actions/cache@v4
        with:
          path: ~/.composer/cache
          key: composer-${{ hashFiles('composer.lock') }}
      - run: composer install --prefer-dist --no-progress --no-interaction
      - run: vendor/bin/php-cs-fixer fix --dry-run --diff
      - run: vendor/bin/phpstan analyse --memory-limit=1G
      - run: vendor/bin/phpunit --coverage-clover=coverage.xml
        env: { DATABASE_URL: postgresql://postgres:t@localhost/test, REDIS_URL: redis://localhost:6379 }
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with: { client-id: ${{ vars.AZ_CLIENT }}, tenant-id: ${{ vars.AZ_TENANT }}, subscription-id: ${{ vars.AZ_SUB }} }
      - uses: azure/docker-login@v2
        with: { login-server: ${{ vars.ACR }}, username: ${{ secrets.ACR_USER }}, password: ${{ secrets.ACR_PASS }} }
      - run: |
          docker buildx build --platform linux/amd64 --push \
            -t ${{ vars.ACR }}/php-app:${{ github.sha }} .
      - uses: azure/webapps-deploy@v3
        with:
          app-name: my-php-app
          slot-name: staging
          images: ${{ vars.ACR }}/php-app:${{ github.sha }}
      - run: |
          az webapp ssh -n my-php-app -g rg-prod --slot staging --command "php artisan migrate --force"
          az webapp deployment slot swap -n my-php-app -g rg-prod --slot staging --target-slot production
</code></pre>

<table>
<tr><th>Choice</th><th>Trade-off</th></tr>
<tr><td>Azure Web App for Containers</td><td>PaaS simplicity; less flexible than AKS</td></tr>
<tr><td>Deployment slots + swap</td><td>Zero-downtime; warmup before swap</td></tr>
<tr><td>OIDC federation</td><td>No static creds; needs federated identity setup</td></tr>
<tr><td>php-fpm + Caddy/Unit</td><td>Modern PHP serving; better than Apache+mod_php</td></tr>
<tr><td>Composer cache via actions/cache</td><td>Saves 30&ndash;90s per build</td></tr>
<tr><td>Azure Key Vault refs in app settings</td><td>Secrets injected at runtime; never in image</td></tr>
</table>

<p><strong>Production polish:</strong> use Azure <strong>Deployment Slots</strong> with a warmup probe (Web App setting <code>WEBSITE_WARMUP_PATH=/health</code>) so the slot serves a few synthetic requests before the swap &mdash; eliminates cold-start failures on the critical first request; reference Key Vault secrets via <code>@Microsoft.KeyVault(SecretUri=...)</code> app settings instead of raw values; opcache + <strong>JIT</strong> on PHP 8.3 dramatically improves CPU-bound endpoints &mdash; ship <code>opcache.preload</code> for framework files; pin <strong>php-fpm</strong> worker counts based on memory + p99 latency observations, never default; for migrations use <code>--force</code> in production but require <em>strong_migrations</em>-style guards in CI to fail dangerous patterns (NOT NULL on a large table without default); enable <strong>Application Insights</strong> for distributed tracing &mdash; PHP SDK ships with it; set <strong>ALWAYS_ON</strong> on the App Service plan to prevent cold starts; for cost, consider <strong>Azure Container Apps</strong> as an alternative &mdash; per-second billing, scale-to-zero, KEDA-driven; and for high-traffic, <strong>AKS + Karpenter</strong> beats Web Apps on price/perf at scale; finally, run <strong>Composer audit</strong> in CI and gate on high-severity vulnerabilities; ship CSP headers and <strong>Roadrunner</strong> for long-running PHP processes if you have heavy WebSocket or SSE traffic.</p>'''

ANSWERS[42] = r'''<p><strong>Situation:</strong> the team writes serverless functions in Node.js/Python and wants GitHub Actions to deploy them to <strong>Google Cloud Functions</strong> (gen 2) on every merge to main, with environment promotion (dev &rarr; staging &rarr; prod) and traffic-split rollback support.</p>

<p><strong>Approach:</strong> use <strong>Cloud Functions gen 2</strong> &mdash; effectively Cloud Run under the hood, with HTTP and event triggers. Authenticate via <strong>Workload Identity Federation</strong> (no JSON keys), package source as a zip uploaded to GCS, then call <code>gcloud functions deploy --gen2</code>. Pin runtime versions, set min/max instances, and use traffic-split for canary on Cloud Run revisions.</p>

<pre><code># .github/workflows/gcf.yml
name: deploy-gcf
on:
  push: { branches: [main] }
permissions: { id-token: write, contents: read }
env:
  PROJECT: my-project
  REGION: europe-west4
jobs:
  deploy:
    strategy:
      matrix:
        env: [dev, staging, prod]
    runs-on: ubuntu-24.04
    environment: ${{ matrix.env }} # gates prod via required reviewers
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gha/providers/github
          service_account: deploy-${{ matrix.env }}@my-project.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - run: |
          gcloud functions deploy api-${{ matrix.env }} \
            --gen2 \
            --runtime=nodejs22 \
            --region=$REGION \
            --source=. \
            --entry-point=handler \
            --trigger-http \
            --no-allow-unauthenticated \
            --min-instances=${{ matrix.env == 'prod' &amp;&amp; 2 || 0 }} \
            --max-instances=100 \
            --memory=512Mi \
            --concurrency=80 \
            --set-env-vars=ENV=${{ matrix.env }} \
            --set-secrets=DB_URL=projects/$PROJECT/secrets/db-url-${{ matrix.env }}:latest \
            --service-account=runtime-${{ matrix.env }}@$PROJECT.iam.gserviceaccount.com \
            --no-traffic # deploy without shifting traffic; canary in next step
      - if: matrix.env == 'prod'
        run: |
          # Canary 10% to new revision
          NEW_REV=$(gcloud run services describe api-prod --region=$REGION --format='value(status.latestCreatedRevisionName)')
          gcloud run services update-traffic api-prod \
            --region=$REGION \
            --to-revisions=$NEW_REV=10
          sleep 300
          # Promote to 100% if canary clean (gate manually or via metrics)
          gcloud run services update-traffic api-prod --region=$REGION --to-latest
</code></pre>

<table>
<tr><th>Concern</th><th>Setting</th></tr>
<tr><td>Auth</td><td>Workload Identity Federation; no JSON keys</td></tr>
<tr><td>Runtime version</td><td>Pin (nodejs22, python312); Google deprecates older</td></tr>
<tr><td>Cold starts</td><td>min-instances &gt; 0 for prod; CPU boost option</td></tr>
<tr><td>Concurrency</td><td>Per-instance request count; tune to memory budget</td></tr>
<tr><td>Secrets</td><td>--set-secrets pulls from Secret Manager at boot</td></tr>
<tr><td>Traffic split</td><td>--to-revisions for canary, --to-latest to promote</td></tr>
<tr><td>Triggers</td><td>HTTP, Eventarc (Pub/Sub, GCS, Firestore, Audit logs)</td></tr>
</table>

<p><strong>Production polish:</strong> Cloud Functions gen 2 is just Cloud Run with extra packaging &mdash; you can drop down to <code>gcloud run deploy</code> directly for more control (custom Dockerfile, sidecars); use <strong>Eventarc</strong> for event triggers, not direct Pub/Sub subscriptions &mdash; cleaner abstractions and at-least-once guarantees; gate prod with <strong>GitHub Environments</strong> + required reviewers so deploys pause until human approval; pre-warm with <code>min-instances</code> matched to baseline traffic &mdash; cold starts on Node 22 are ~150&ndash;400ms but compound with chained calls; structured logs go to <strong>Cloud Logging</strong> automatically when output as JSON to stdout; trace via <strong>OpenTelemetry</strong> with the GCP exporter; for cost control, set explicit <code>--max-instances</code> &mdash; runaway autoscaling on Pub/Sub spikes can be painful; pin <strong>VPC Connector</strong> if functions need private network access (Cloud SQL, Memorystore); stage deploys in a dedicated <em>staging</em> project, not the same project, to isolate IAM and quotas; ship the SLOs as <strong>Cloud Monitoring SLO</strong> resources alongside the function for end-to-end visibility; finally, treat traffic-split rollback as primary &mdash; one <code>gcloud run services update-traffic --to-revisions=&lt;previous&gt;=100</code> reverts in seconds.</p>'''

ANSWERS[43] = r'''<p><strong>Situation:</strong> a data-intensive application (high-volume Kafka pipeline, Postgres + ClickHouse, Spark batch jobs) needs CI/CD on Kubernetes that respects state, runs schema migrations safely, and deploys streaming jobs without dropping events.</p>

<p><strong>Approach:</strong> separate <em>data plane</em> (Strimzi Kafka, CloudNativePG, ClickHouse Operator, Spark Operator, Apache Flink Operator) from <em>application logic</em> (consumers, transformers, dashboards). Schemas evolve through expand/contract; data jobs deploy as Argo Workflows or Flink Jobs via <strong>Flink Kubernetes Operator</strong>; lakehouse tables version via <strong>Iceberg</strong>, <strong>Delta Lake</strong>, or <strong>Hudi</strong>; Argo CD reconciles all CRDs from a config repo. For dataset versioning use <strong>lakeFS</strong> or <strong>Nessie</strong>.</p>

<pre><code># Flink Kubernetes Operator FlinkDeployment for a streaming job
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata: { name: orders-aggregator, namespace: flink }
spec:
  image: ghcr.io/org/orders-aggregator:${IMAGE_TAG}
  flinkVersion: v1_19
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: '4'
    state.backend: rocksdb
    state.checkpoints.dir: s3://lake/checkpoints/orders
    execution.checkpointing.interval: '60s'
  serviceAccount: flink
  jobManager: { resource: { memory: 2048m, cpu: 1 } }
  taskManager: { resource: { memory: 4096m, cpu: 2 }, replicas: 4 }
  job:
    jarURI: local:///opt/flink/usrlib/orders-aggregator.jar
    parallelism: 8
    upgradeMode: savepoint   # savepoint then restore on update -&gt; no event loss
    state: running
---
# Atlas migration step in CI
- name: Schema diff &amp; apply
  run: |
    atlas migrate diff --env ci
    atlas migrate apply --env staging --baseline 20240101 --tx-mode all
---
# CloudNativePG cluster with point-in-time recovery
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata: { name: events, namespace: data }
spec:
  instances: 3
  postgresql: { parameters: { wal_level: replica, max_connections: '200' } }
  bootstrap:
    initdb: { database: events, owner: app }
  backup:
    barmanObjectStore:
      destinationPath: s3://backups/events
      s3Credentials: { accessKeyId: { name: backup-creds, key: AWS_KEY }, secretAccessKey: { name: backup-creds, key: AWS_SECRET } }
    retentionPolicy: '30d'
</code></pre>

<table>
<tr><th>Concern</th><th>2026 tooling</th></tr>
<tr><td>Brokers</td><td>Strimzi (Kafka), Pulsar Operator, NATS Operator</td></tr>
<tr><td>OLTP DBs</td><td>CloudNativePG, MariaDB Operator, Percona Operator</td></tr>
<tr><td>Analytical</td><td>ClickHouse Operator, Trino Operator, Apache Pinot Operator</td></tr>
<tr><td>Stream processing</td><td>Flink Operator, Spark Operator, Beam on Flink</td></tr>
<tr><td>Schema migrations</td><td>Atlas (Ariga), Liquibase, Flyway</td></tr>
<tr><td>Lakehouse format</td><td>Iceberg, Delta Lake, Hudi</td></tr>
<tr><td>Dataset versioning</td><td>lakeFS, Nessie, Pachyderm, DVC</td></tr>
<tr><td>Backup</td><td>Velero + CSI snapshots, Barman, Stash</td></tr>
</table>

<p><strong>Production polish:</strong> for streaming jobs, always upgrade via <strong>savepoint &rarr; restore</strong> &mdash; the Flink Operator&rsquo;s <code>upgradeMode: savepoint</code> handles this automatically; never just delete-and-recreate (loses state); for Kafka, configure <strong>Cruise Control</strong> via Strimzi to rebalance partitions and detect anomalies; back up Kafka topic configs (KafkaTopic CRDs in Git) and offset commits separately; for OLTP, run Postgres failover drills monthly using CloudNativePG&rsquo;s <code>cnpg-controller failover</code>; for OLAP, partition tables aggressively (by day or hour) so old partitions can be archived to object storage cheaply; size <strong>PodDisruptionBudgets</strong> with <code>maxUnavailable: 0</code> for primary databases &mdash; one node drain is one too many; use <strong>topology spread constraints</strong> + <strong>anti-affinity</strong> to avoid co-locating replicas; expose <strong>OpenTelemetry</strong> tracing through the pipeline so a slow query in ClickHouse traces back to the originating Kafka event; for cost, separate <em>hot</em> from <em>cold</em> data &mdash; recent days in fast storage, history in S3 Glacier or GCS Nearline; finally, run <strong>data quality</strong> checks (Great Expectations, Soda) in the pipeline so corrupt input is caught before it propagates downstream &mdash; debugging analytical errors weeks later is far worse than failing fast at ingestion.</p>'''

ANSWERS[44] = r'''<p><strong>Situation:</strong> a Rust application with a long crate compile graph needs <strong>continuous integration</strong> in GitHub Actions, with effective dependency caching so iterative PR builds finish in 1&ndash;2 minutes rather than 15. Targets include cross-compilation to musl and ARM.</p>

<p><strong>Approach:</strong> use <strong>Swatinem/rust-cache</strong> &mdash; the standard cache action that handles <code>~/.cargo</code>, <code>target/</code>, and selective key derivation from <code>Cargo.lock</code>. Pair with <strong>cargo-chef</strong> for Docker builds (separates dependency build from app build). For ARM/musl, use <strong>cross</strong> or <strong>cargo-zigbuild</strong>. Run <strong>clippy</strong>, <strong>cargo-deny</strong>, <strong>cargo-audit</strong>, and <strong>cargo-llvm-cov</strong> in parallel.</p>

<pre><code># .github/workflows/rust.yml
name: rust
on: { push: { branches: [main] }, pull_request: {} }
permissions: { contents: read }
env:
  CARGO_TERM_COLOR: always
  RUST_BACKTRACE: 1
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with: { components: clippy, rustfmt }
      - uses: Swatinem/rust-cache@v2
        with: { shared-key: rust-test }
      - run: cargo fmt --check
      - run: cargo clippy --all-targets --all-features -- -D warnings
      - run: cargo test --all-features --workspace
  audit:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
        with: { shared-key: rust-audit }
      - run: cargo install cargo-deny cargo-audit --locked
      - run: cargo audit
      - run: cargo deny check
  cross:
    needs: test
    if: github.ref == 'refs/heads/main'
    strategy:
      matrix:
        target: [aarch64-unknown-linux-musl, x86_64-unknown-linux-musl]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with: { targets: ${{ matrix.target }} }
      - uses: Swatinem/rust-cache@v2
        with: { shared-key: rust-cross-${{ matrix.target }} }
      - run: cargo install cargo-zigbuild --locked
      - run: cargo zigbuild --release --target ${{ matrix.target }}
      - uses: actions/upload-artifact@v4
        with: { name: bin-${{ matrix.target }}, path: target/${{ matrix.target }}/release/app }
</code></pre>

<table>
<tr><th>Cache strategy</th><th>Benefit</th></tr>
<tr><td>Swatinem/rust-cache</td><td>Handles target/ + ~/.cargo; key on Cargo.lock</td></tr>
<tr><td>shared-key per workflow</td><td>Avoid cache thrash between unrelated jobs</td></tr>
<tr><td>cargo-chef in Dockerfile</td><td>Separate <em>cook</em> (deps) from <em>build</em> layer</td></tr>
<tr><td>sccache + GitHub cache</td><td>Compiler-cache; biggest wins on monorepos with many crates</td></tr>
<tr><td>cargo-zigbuild</td><td>Cross-compile musl/aarch64 without cross+QEMU</td></tr>
<tr><td>cranelift backend</td><td>~30% faster debug builds (nightly only)</td></tr>
</table>

<p><strong>Production polish:</strong> use <strong>cargo-chef</strong> in the production Dockerfile &mdash; the <em>plan</em> &rarr; <em>cook</em> &rarr; <em>build</em> sequence means dependencies recompile only when <code>Cargo.lock</code> changes, which is the dominant cost saving; for very large workspaces, install <strong>sccache</strong> with the GitHub Actions cache backend &mdash; saves more than rust-cache alone but needs a custom env setup; pin the toolchain via <code>rust-toolchain.toml</code> so all CI/dev/prod use the same compiler; run <strong>cargo-deny</strong> with a curated <code>deny.toml</code> to block unwanted licences (GPL into proprietary), known-bad versions, and duplicate dependencies; <strong>cargo-audit</strong> hits the RustSec advisory DB; for FFI-heavy crates, cache <code>~/.cargo/registry/cache</code> and Apple framework caches; ship binaries as static musl + UPX-compressed for tiny container images (single-binary <code>FROM scratch</code> at &lt;5MB); for release pipelines use <strong>cargo-release</strong> + <strong>release-please</strong> for changelog automation; gate merges on <strong>required checks</strong> = test + audit + clippy; finally, profile real CI runs &mdash; the <a href="https://github.com/EmbarkStudios/rust-build-helper">embark</a> blog series has good writeups on what actually moves Rust CI times, and the answer is almost always &ldquo;cache the right things, parallelise the rest&rdquo;.</p>'''

ANSWERS[45] = r'''<p><strong>Situation:</strong> the platform owner has been burned by deploys that drop in-flight requests &mdash; users see 502s during rolling updates. The mandate is <strong>zero-downtime deployments</strong> on Kubernetes for every workload, with provable connection draining and schema-compatible migrations.</p>

<p><strong>Approach:</strong> seven parts &mdash; (1) readiness probes that gate traffic, (2) <code>preStop</code> hook with <code>sleep</code> to absorb in-flight requests after pod removal from Endpoints, (3) <code>terminationGracePeriodSeconds</code> long enough for graceful shutdown, (4) <code>maxUnavailable: 0</code> on rolling updates, (5) Pod Disruption Budgets to protect against simultaneous evictions during node drain, (6) schema migrations using <em>expand/contract</em>, never destructive, (7) progressive delivery via Argo Rollouts or Flagger so traffic shifts only when SLOs are clean.</p>

<pre><code># Deployment with full zero-downtime configuration
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: prod }
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: api
          image: ghcr.io/org/api:v1.42.0
          ports: [{ containerPort: 8080 }]
          readinessProbe:
            httpGet: { path: /ready, port: 8080 }
            periodSeconds: 5
            failureThreshold: 2
          livenessProbe:
            httpGet: { path: /healthz, port: 8080 }
            periodSeconds: 10
            failureThreshold: 6
            initialDelaySeconds: 30
          startupProbe:
            httpGet: { path: /healthz, port: 8080 }
            periodSeconds: 5
            failureThreshold: 30
          lifecycle:
            preStop:
              exec: { command: ["/bin/sh","-c","sleep 15"] }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api, namespace: prod }
spec:
  minAvailable: 80%
  selector: { matchLabels: { app: api } }
  unhealthyPodEvictionPolicy: AlwaysAllow # 1.27+
</code></pre>

<table>
<tr><th>Mechanism</th><th>What it prevents</th></tr>
<tr><td>readinessProbe</td><td>Traffic to a pod before it can serve</td></tr>
<tr><td>preStop sleep 15s</td><td>Race between Endpoints removal propagation and SIGTERM</td></tr>
<tr><td>terminationGracePeriodSeconds 60s</td><td>SIGKILL before drain completes</td></tr>
<tr><td>maxUnavailable: 0</td><td>Replica count dipping during rollout</td></tr>
<tr><td>PodDisruptionBudget</td><td>Multiple pods evicted simultaneously during node drain</td></tr>
<tr><td>topologySpreadConstraints</td><td>All replicas on one zone &rarr; one AZ failure = outage</td></tr>
<tr><td>Argo Rollouts canary</td><td>Bad code reaching 100% of traffic</td></tr>
<tr><td>expand/contract migrations</td><td>Schema change incompatible with previous code</td></tr>
</table>

<p><strong>Production polish:</strong> the <strong>preStop sleep</strong> exists because Kubernetes&rsquo; pod removal from the Service Endpoints is eventually consistent &mdash; some kube-proxy/Cilium agents will keep sending traffic for a few seconds after a pod enters Terminating; sleep 10&ndash;20s, then SIGTERM, drains in-flight cleanly; ensure the application <strong>handles SIGTERM</strong> &mdash; close listening sockets, finish in-flight requests with a deadline, then exit; for HTTP/2 with long-lived streams, send <code>GOAWAY</code> first; for gRPC, drain via the official graceful stop; for WebSockets, signal connection migration to clients; <strong>schema migrations</strong> must always be backward compatible with the previous code version &mdash; add columns nullable, deploy new code that uses them, then remove the old code, then drop old columns in a separate release; <strong>Argo Rollouts</strong> with metric analysis (Prometheus error rate &lt; 1%) is the safety net &mdash; canaries catch what unit tests can&rsquo;t; spread replicas across at least 3 zones via <code>topologySpreadConstraints</code> with <code>whenUnsatisfiable: DoNotSchedule</code>; finally, exercise the actual rollout regularly under realistic load using <strong>k6</strong> or <strong>locust</strong> &mdash; you only know the rollout is zero-downtime when a real load test sees zero failed requests during a real deploy.</p>'''

ANSWERS[46] = r'''<p><strong>Situation:</strong> the security team has tagged compliance gaps that map to NIST 800-53, CIS Benchmarks, and (depending on industry) PCI-DSS, HIPAA, or FedRAMP. Manual audits aren&rsquo;t cutting it &mdash; controls drift between audits. The mandate is to <strong>shift compliance left</strong> so every PR runs the same checks an external auditor would, with evidence stored for the next audit window.</p>

<p><strong>Approach:</strong> compliance breaks into four layers in the pipeline &mdash; (1) <strong>OS / image hardening</strong> via OpenSCAP scanning Dockerfiles and base images against DISA STIG and CIS profiles, (2) <strong>config and infrastructure</strong> via Chef InSpec or Open Policy Agent (OPA) profiles tested against deployed clusters, (3) <strong>policy-as-code</strong> via Kyverno or Gatekeeper running both in CI (kyverno test) and at admission, (4) <strong>evidence collection</strong> via SBOMs (Syft), provenance (SLSA, in-toto), and signed audit trails (Sigstore Rekor).</p>

<pre><code>name: compliance
on: pull_request
permissions: { contents: read, security-events: write }
jobs:
  openscap:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t app:${{ github.sha }} .
      - name: OpenSCAP CIS scan
        run: |
          docker run --rm -v $PWD:/work \
            ghcr.io/openscap/openscap-scanner:latest \
            oscap-docker image app:${{ github.sha }} \
              xccdf eval --profile xccdf_org.ssgproject.content_profile_cis \
              --results /work/scap-results.xml \
              /usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: scap-results.xml }

  inspec:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Run InSpec profile
        run: |
          inspec exec compliance/cis-kubernetes \
            --target k8s:// --reporter cli json:inspec.json
      - uses: actions/upload-artifact@v4
        with: { name: inspec-results, path: inspec.json }

  kyverno:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Test policies against manifests
        run: |
          kyverno test ./policies
          kyverno apply ./policies --resource ./manifests --audit-warn

  sbom-attest:
    runs-on: ubuntu-24.04
    permissions: { id-token: write, packages: write }
    steps:
      - uses: anchore/sbom-action@v0
        with: { image: app:${{ github.sha }}, format: cyclonedx-json }
      - uses: sigstore/cosign-installer@v3
      - run: |
          cosign attest --predicate sbom.json --type cyclonedx \
            ghcr.io/org/app:${{ github.sha }}
</code></pre>

<table>
<tr><th>Control family</th><th>Tool (2026)</th></tr>
<tr><td>OS / image baseline</td><td>OpenSCAP, Chainguard image attestations</td></tr>
<tr><td>Config / infra</td><td>Chef InSpec, OPA Conftest, Checkov</td></tr>
<tr><td>K8s policy</td><td>Kyverno, Gatekeeper, Kubescape</td></tr>
<tr><td>Supply chain</td><td>Syft (SBOM), Cosign (sign), Rekor (transparency log)</td></tr>
<tr><td>Runtime</td><td>Falco, Tetragon, KubeArmor</td></tr>
</table>

<p><strong>Trade-offs:</strong> compliance scans add 5&ndash;15 minutes to PR pipelines &mdash; mitigate with caching profiles and parallel jobs. False positives are routine on InSpec/OpenSCAP &mdash; commit a per-repo waiver file with expiry dates. Kyverno&rsquo;s admission rules can break legitimate deploys; run in <code>audit</code> mode for two weeks before flipping to <code>enforce</code>.</p>

<p><strong>Production polish:</strong> wire SARIF upload to GitHub Advanced Security so violations show in the Security tab; export evidence (SBOMs, scan results, attestations) to a tamper-evident store (Rekor + S3 with Object Lock); generate a quarterly compliance report from pipeline metadata via a scheduled workflow that hits the GitHub API. Auditors love a clean audit trail derived automatically from CI.</p>'''

ANSWERS[47] = r'''<p><strong>Situation:</strong> a numerical-heavy C++ service (think trading systems, scientific compute, game backends) needs CI/CD with cross-platform builds, automated GoogleTest/Catch2 runs, address/thread sanitiser passes, and deployment to AWS EC2. The team values reproducible binaries and reasonable build times despite C++ compile cost.</p>

<p><strong>Approach:</strong> CMake + Ninja for build, vcpkg or Conan for deps, ccache or sccache for compile caching, GitHub Actions matrix for compiler/OS combinations, and CodeDeploy with a hosted EC2 deployment group for prod rollout. Sanitisers run on a separate non-blocking job because they&rsquo;re slow but invaluable.</p>

<pre><code>name: cpp-cicd
on:
  push: { branches: [main] }
  pull_request:
permissions: { id-token: write, contents: read }

jobs:
  build-test:
    strategy:
      matrix:
        os: [ubuntu-24.04, ubuntu-24.04-arm]
        build_type: [Release, Debug]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: lukka/get-cmake@latest
      - uses: lukka/run-vcpkg@v11
        with: { vcpkgGitCommitId: 'a42af01b72c28a8e1d7b48107b33e4f286a55ef6' }
      - name: ccache
        uses: hendrikmuhs/ccache-action@v1
        with: { key: ${{ matrix.os }}-${{ matrix.build_type }} }
      - name: Configure
        run: |
          cmake --preset=ninja-release \
            -DCMAKE_C_COMPILER_LAUNCHER=ccache \
            -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
            -DCMAKE_BUILD_TYPE=${{ matrix.build_type }}
      - name: Build
        run: cmake --build --preset=ninja-release --parallel
      - name: Test
        working-directory: build
        run: ctest --output-on-failure --parallel 4

  sanitisers:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - name: Build with ASan + UBSan
        run: |
          cmake -B build -G Ninja \
            -DCMAKE_BUILD_TYPE=Debug \
            -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -g -O1"
          cmake --build build --parallel
      - run: ctest --test-dir build --output-on-failure

  package-deploy:
    needs: [build-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/download-artifact@v4
        with: { name: app-binary }
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123:role/cpp-deployer, aws-region: ap-south-1 }
      - run: |
          tar czf bundle.tgz app appspec.yml scripts/
          aws s3 cp bundle.tgz s3://cpp-artifacts/${{ github.sha }}/bundle.tgz
          aws deploy create-deployment \
            --application-name cpp-svc \
            --deployment-group-name prod \
            --s3-location bucket=cpp-artifacts,key=${{ github.sha }}/bundle.tgz,bundleType=tgz \
            --deployment-config-name CodeDeployDefault.EC2AllAtOnce
</code></pre>

<table>
<tr><th>Concern</th><th>Choice</th></tr>
<tr><td>Build system</td><td>CMake + Ninja with presets (CMakePresets.json)</td></tr>
<tr><td>Dependency manager</td><td>vcpkg (manifest mode) or Conan 2</td></tr>
<tr><td>Compile cache</td><td>ccache local; sccache for distributed</td></tr>
<tr><td>Static analysis</td><td>clang-tidy, cppcheck, IWYU, PVS-Studio</td></tr>
<tr><td>Sanitisers</td><td>ASan, UBSan, TSan, MSan</td></tr>
<tr><td>Deploy</td><td>CodeDeploy in-place or blue/green ASG</td></tr>
</table>

<p><strong>Trade-offs:</strong> matrix builds multiply minute consumption &mdash; trim to the platforms you actually ship to. Sanitiser builds 2&ndash;5x slower than release, so run nightly rather than per-PR if budget is tight. CodeDeploy has a learning curve; if you can move to ECS or App Runner with a static binary, the operational story is simpler.</p>

<p><strong>Production polish:</strong> ship a stripped binary with separate debug info uploaded to a symbol server (Sentry, Crashpad, Backtrace.io) so production crashes resolve to source. Use <code>aws ssm send-command</code> in the deploy hooks to run smoke tests on each instance after install. Sign release binaries with Cosign so tampering is detectable. Build ARM64 (Graviton3) variants &mdash; for compute-bound C++ the price/performance gain is substantial.</p>'''

ANSWERS[48] = r'''<p><strong>Situation:</strong> a multi-service application on Kubernetes occasionally degrades after deploys &mdash; a bad image, a wrong env var, or a schema mismatch causes elevated 5xx or latency that humans only notice minutes later. The team wants <strong>automated rollbacks</strong> wired into Jenkins so a failed deploy reverses without paging anyone.</p>

<p><strong>Approach:</strong> use Argo Rollouts (or Flagger) for the actual rollback mechanics &mdash; Jenkins should not be in the data path of canary analysis, it just kicks off the Rollout and waits. The Rollout&rsquo;s analysis template queries Prometheus / Datadog for SLO breaches; on failure it auto-aborts and traffic stays on the stable revision. Jenkins polls the Rollout status and reports back.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent { kubernetes { yaml libraryResource('agents/argo-rollouts.yaml') } }
  environment { IMAGE = "ghcr.io/org/api:${env.GIT_COMMIT.take(8)}" }
  stages {
    stage('Build &amp; push') {
      steps {
        container('buildkit') {
          sh &apos;&apos;&apos;
            buildctl build --frontend dockerfile.v0 \
              --local context=. --local dockerfile=. \
              --output type=image,name=$IMAGE,push=true
          &apos;&apos;&apos;
        }
      }
    }
    stage('Update Rollout') {
      steps {
        container('kubectl') {
          sh &apos;&apos;&apos;
            kubectl-argo-rollouts set image api api=$IMAGE -n prod
          &apos;&apos;&apos;
        }
      }
    }
    stage('Watch analysis') {
      steps {
        container('kubectl') {
          script {
            timeout(time: 30, unit: 'MINUTES') {
              sh &apos;&apos;&apos;
                kubectl-argo-rollouts get rollout api -n prod --watch \
                  | tee rollout.log &amp;
                WATCH_PID=$!
                while true; do
                  STATUS=$(kubectl-argo-rollouts status api -n prod --timeout 30s)
                  case "$STATUS" in
                    *Healthy*) kill $WATCH_PID; exit 0 ;;
                    *Degraded*|*Aborted*) kill $WATCH_PID; exit 1 ;;
                  esac
                  sleep 10
                done
              &apos;&apos;&apos;
            }
          }
        }
      }
    }
  }
  post {
    failure {
      container('kubectl') {
        sh 'kubectl-argo-rollouts undo api -n prod || true'
        slackSend channel: '#ops', color: 'danger',
          message: "Rollback executed for api (build ${env.BUILD_NUMBER})"
      }
    }
  }
}</code></pre>

<table>
<tr><th>Mechanism</th><th>What it does</th></tr>
<tr><td>Argo Rollouts AnalysisTemplate</td><td>Prometheus query &rarr; auto-abort on SLO breach</td></tr>
<tr><td>Flagger</td><td>Same idea, integrated with Linkerd/Istio/Contour</td></tr>
<tr><td>Helm <code>--atomic</code></td><td>Built-in revert on failed install/upgrade</td></tr>
<tr><td>kubectl rollout undo</td><td>Last-resort manual rollback for plain Deployments</td></tr>
<tr><td>Jenkins post.failure</td><td>Notify + audit trail; never the primary mechanism</td></tr>
</table>

<p><strong>Trade-offs:</strong> Argo Rollouts adds a CRD and one controller pod, but the trade-off is well worth it &mdash; rolling back a plain Deployment via Jenkins &lsquo;rollout undo&rsquo; is racy when you&rsquo;re mid-rollout. Don&rsquo;t couple Jenkins too tightly to rollback decisions; the controller is closer to traffic and reacts in seconds.</p>

<p><strong>Production polish:</strong> separate <em>code</em> rollback (image revert) from <em>schema</em> rollback (DB migration revert) &mdash; the second one is rarely safe, so use expand/contract migrations so the previous app version still works against the new schema. Page humans only after auto-rollback completes; the alarm is that something broke, not that rollback failed. Annotate the Rollout with the Jenkins build URL so on-call traces directly back to the failed pipeline.</p>'''

ANSWERS[49] = r'''<p><strong>Situation:</strong> a Dart / Flutter team has a backend service written in Dart (Shelf, Conduit, Serverpod, or Dart Frog), and wants a CI/CD pipeline that runs unit tests, integration tests, and deploys to Google Cloud Run. They want fast cold starts (Dart AOT compiles to native) and reproducible container builds.</p>

<p><strong>Approach:</strong> compile Dart with <code>dart compile exe</code> to a static-ish native binary, then ship in a distroless container; Cloud Run reads the artefact registry image and deploys via <code>gcloud run deploy</code>. CI uses GitHub Actions with a Dart toolchain action, runs <code>dart test</code> for units, spins up a Postgres service container for integration, and authenticates to GCP via Workload Identity Federation.</p>

<pre><code># Dockerfile
FROM dart:3.5 AS build
WORKDIR /src
COPY pubspec.* ./
RUN dart pub get --no-precompile
COPY . .
RUN dart pub get --offline
RUN dart compile exe bin/server.dart -o /out/server

FROM gcr.io/distroless/cc-debian12:nonroot
COPY --from=build /out/server /server
COPY --from=build /runtime/ /
EXPOSE 8080
ENV PORT=8080
USER nonroot
ENTRYPOINT ["/server"]</code></pre>

<pre><code>name: dart-cicd
on:
  push: { branches: [main] }
  pull_request:
permissions: { id-token: write, contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test }
        ports: ['5432:5432']
        options: --health-cmd pg_isready
    steps:
      - uses: actions/checkout@v4
      - uses: dart-lang/setup-dart@v1
        with: { sdk: '3.5.0' }
      - run: dart pub get
      - run: dart format --set-exit-if-changed .
      - run: dart analyze --fatal-infos
      - run: dart test --coverage=coverage
      - run: dart pub global activate coverage
      - run: dart pub global run coverage:format_coverage \
            --report-on=lib --lcov -i coverage -o coverage/lcov.info
      - uses: codecov/codecov-action@v4

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gha/providers/gh
          service_account: deployer@proj.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker ap-south1-docker.pkg.dev
      - name: Build &amp; push
        run: |
          IMG=ap-south1-docker.pkg.dev/proj/repo/dart-svc:${{ github.sha }}
          docker build -t $IMG .
          docker push $IMG
          echo "IMAGE=$IMG" &gt;&gt; $GITHUB_ENV
      - name: Deploy
        run: |
          gcloud run deploy dart-svc \
            --image $IMAGE \
            --region asia-south1 \
            --concurrency 80 --cpu 1 --memory 512Mi \
            --min-instances 1 --max-instances 50 \
            --execution-environment gen2 \
            --no-allow-unauthenticated</code></pre>

<table>
<tr><th>Concern</th><th>Choice</th></tr>
<tr><td>Compile</td><td>dart compile exe (AOT to native, ~50ms cold start)</td></tr>
<tr><td>Base image</td><td>distroless/cc &mdash; small, no shell, runtime libs only</td></tr>
<tr><td>Auth</td><td>Workload Identity Federation (no JSON key)</td></tr>
<tr><td>Min instances</td><td>1 to avoid cold starts on critical path</td></tr>
<tr><td>Test orch</td><td>GitHub Actions service containers for Postgres/Redis</td></tr>
<tr><td>Coverage</td><td>dart test --coverage + coverage:format_coverage</td></tr>
</table>

<p><strong>Trade-offs:</strong> Dart on the server is niche &mdash; smaller talent pool, fewer libraries, but excellent for Flutter shops sharing models. AOT binaries are tied to the build platform&rsquo;s glibc &mdash; build inside the same base image you ship. <code>min-instances 1</code> incurs idle cost; for genuinely bursty workloads accept cold starts and stay at 0.</p>

<p><strong>Production polish:</strong> add OpenTelemetry instrumentation via <code>package:opentelemetry</code> and export to Cloud Trace; structure logs with <code>package:logging</code> + a JSON formatter so Cloud Logging parses fields cleanly. Use Cloud Run <em>revisions</em> with traffic splitting (10/90 then 50/50 then 100/0) for canaries; <code>gcloud run services update-traffic</code> shifts traffic without redeploy.</p>'''

ANSWERS[50] = r'''<p><strong>Situation:</strong> the team is moving a containerised service from EC2/ECS-on-EC2 to AWS Fargate &mdash; serverless containers, no EC2 to manage, billed per second of vCPU and memory. They want GitHub Actions to handle build, push to ECR, register a new task definition, and deploy with health-check-aware traffic shifting.</p>

<p><strong>Approach:</strong> the canonical four-stage flow is OIDC auth &rarr; ECR push &rarr; render task definition &rarr; deploy ECS service. For zero-downtime swaps add CodeDeploy with an ALB in front, two target groups, and a deployment group set to <code>CodeDeployDefault.ECSCanary10Percent5Minutes</code> &mdash; this shifts 10% traffic, waits, then promotes if CloudWatch alarms stay green.</p>

<pre><code>name: fargate-cd
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
env:
  AWS_REGION: ap-south-1
  ECR_REPO: 123.dkr.ecr.ap-south-1.amazonaws.com/api
  CLUSTER: prod
  SERVICE: api
jobs:
  deploy:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-fargate
          aws-region: ${{ env.AWS_REGION }}
      - uses: aws-actions/amazon-ecr-login@v2
      - uses: docker/setup-buildx-action@v3
      - name: Build &amp; push (linux/arm64 on Graviton)
        run: |
          docker buildx build --platform linux/arm64 \
            --tag $ECR_REPO:${{ github.sha }} \
            --cache-from type=gha --cache-to type=gha,mode=max \
            --push .
      - name: Render new task def
        id: render
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: aws/task-definition.json
          container-name: api
          image: ${{ env.ECR_REPO }}:${{ github.sha }}
      - name: Deploy via CodeDeploy
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.render.outputs.task-definition }}
          service: ${{ env.SERVICE }}
          cluster: ${{ env.CLUSTER }}
          codedeploy-appspec: aws/appspec.yaml
          codedeploy-application: api
          codedeploy-deployment-group: prod
          wait-for-service-stability: true</code></pre>

<pre><code># aws/appspec.yaml
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: &lt;TASK_DEFINITION&gt;
        LoadBalancerInfo: { ContainerName: api, ContainerPort: 8080 }
Hooks:
  - BeforeAllowTraffic: arn:aws:lambda:ap-south-1:123:function:smoke-test
  - AfterAllowTraffic: arn:aws:lambda:ap-south-1:123:function:notify-slack</code></pre>

<table>
<tr><th>Choice</th><th>Recommendation</th></tr>
<tr><td>Auth</td><td>OIDC role assumption (zero static keys)</td></tr>
<tr><td>Architecture</td><td>arm64 (Graviton3) for ~30% cost savings on Fargate</td></tr>
<tr><td>Deploy strategy</td><td>CodeDeploy ECSCanary10Percent5Minutes for prod</td></tr>
<tr><td>Health gate</td><td>CloudWatch alarms attached to deployment group</td></tr>
<tr><td>Hooks</td><td>Lambda BeforeAllowTraffic for smoke tests</td></tr>
<tr><td>Task sizing</td><td>Even vCPU/memory ratios (0.25/0.5GiB, 1/2GiB&hellip;)</td></tr>
</table>

<p><strong>Trade-offs:</strong> Fargate is more expensive per vCPU than spot EC2, but the ops simplicity is a real saving. Cold starts on first task are ~30&ndash;60s including image pull; mitigate with <em>minimum healthy percent</em> 100 and ECS Service Connect / Cloud Map for warm DNS. CodeDeploy adds complexity; for non-critical services <code>aws-actions/amazon-ecs-deploy-task-definition</code> alone (no CodeDeploy) is fine.</p>

<p><strong>Production polish:</strong> attach CloudWatch alarms on ALB 5xx rate and target latency to the deployment group so canary auto-rolls back. Use ECS Exec for incident debugging and gate it via SSM session manager. Right-size task definitions with <code>aws ecs describe-tasks</code> historical data &mdash; oversized tasks dominate Fargate costs. App Runner is a simpler alternative for HTTP-only services if you don&rsquo;t need ECS-specific features.</p>'''

ANSWERS[51] = r'''<p><strong>Situation:</strong> a real-time application (chat, collaboration, multiplayer game, trading dashboard) uses WebSockets for bidirectional comms and runs on Kubernetes. Standard rolling deploys break sessions &mdash; sticky connections die when their pod terminates, and reconnect storms hammer the new pods. The team needs a CI/CD pipeline that respects WebSocket lifecycle.</p>

<p><strong>Approach:</strong> three pillars &mdash; (1) <strong>graceful drain</strong> via long <code>preStop</code> hook that signals the app to stop accepting new WebSocket upgrades, then waits for existing sessions to migrate or expire, (2) <strong>session migration</strong> via a coordinator (Redis pub/sub, NATS JetStream, or a managed service like Pusher/Ably/Centrifugo) so clients can reconnect to a different pod and resume state, (3) <strong>progressive rollout</strong> with very low <code>maxSurge</code>/<code>maxUnavailable</code> and a long <code>terminationGracePeriodSeconds</code>.</p>

<pre><code># WebSocket-aware Deployment
apiVersion: apps/v1
kind: Deployment
metadata: { name: ws-api, namespace: prod }
spec:
  replicas: 8
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    spec:
      terminationGracePeriodSeconds: 600   # 10min drain window
      containers:
        - name: ws
          image: ghcr.io/org/ws-api:v2.3.0
          ports: [{ containerPort: 8080 }]
          readinessProbe:
            httpGet: { path: /ready, port: 8080 }
          lifecycle:
            preStop:
              exec:
                command:
                  - /bin/sh
                  - -c
                  - |
                    curl -X POST localhost:8080/admin/drain
                    while [ $(curl -s localhost:8080/metrics/active_ws) -gt 0 ]; do
                      sleep 5
                    done
---
apiVersion: v1
kind: Service
metadata:
  name: ws-api
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-attributes: deletion_protection.enabled=true
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP
  sessionAffinityConfig: { clientIP: { timeoutSeconds: 10800 } }
  ports: [{ port: 443, targetPort: 8080, protocol: TCP }]
  selector: { app: ws-api }</code></pre>

<table>
<tr><th>Layer</th><th>2026 tooling</th></tr>
<tr><td>WS server</td><td>Centrifugo, SocketIO, Phoenix Channels, ws (Node), gorilla/websocket</td></tr>
<tr><td>Coordinator</td><td>Redis Streams/Pub-Sub, NATS JetStream, Kafka</td></tr>
<tr><td>Managed alt</td><td>Ably, Pusher, AWS API Gateway WebSocket, Azure SignalR</td></tr>
<tr><td>L4 LB</td><td>NLB / GCP TCP LB &mdash; preserve client IP, long idle timeout</td></tr>
<tr><td>Progressive deploy</td><td>Argo Rollouts with WebSocket-aware analysis</td></tr>
</table>

<p><strong>Trade-offs:</strong> long drain windows mean rolling updates take much longer (10+ minutes), so feature deploys feel slow &mdash; teams sometimes use blue/green at the namespace level instead. Sticky sessions plus autoscaling don&rsquo;t mix well; HPA scaling decisions can&rsquo;t evict drained pods quickly. Managed services (Ably, Pusher) externalise the problem entirely &mdash; expensive at scale but operationally trivial.</p>

<p><strong>Production polish:</strong> emit a Prometheus gauge for active WebSocket count and use it in the Argo Rollouts AnalysisTemplate to gate promotion (only promote if connection growth on new revision matches old). Implement client-side exponential backoff on reconnect with jitter to prevent thundering herd. Use HTTP/2 Server Push or, better, WebTransport (HTTP/3) for new builds &mdash; QUIC&rsquo;s connection migration is genuinely useful for mobile clients on flaky networks.</p>'''

ANSWERS[52] = r'''<p><strong>Situation:</strong> the security and engineering teams have agreed to enforce code quality and security gates on every PR &mdash; SonarQube for quality and coverage, Snyk for SCA and container scanning. The mandate is hard fails for new high/critical issues, soft warnings for existing debt.</p>

<p><strong>Approach:</strong> SonarQube runs as a hosted instance (SonarCloud or self-hosted) with the GitHub App installed for PR decoration; Snyk runs via its GitHub Action with separate jobs for code (snyk code), open source (snyk test), container (snyk container), and IaC (snyk iac). Both tools support <em>quality gates</em> based on new code, which is what the pipeline enforces.</p>

<pre><code>name: code-quality-security
on:
  pull_request:
  push: { branches: [main] }
permissions: { contents: read, pull-requests: write, security-events: write }
jobs:
  sonar:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test -- --coverage
      - uses: SonarSource/sonarqube-scan-action@v4
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: https://sonarcloud.io
        with:
          args: |
            -Dsonar.projectKey=org_repo
            -Dsonar.organization=org
            -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info
            -Dsonar.qualitygate.wait=true

  snyk-code:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/setup@master
      - run: snyk code test --severity-threshold=high --sarif-file-output=snyk-code.sarif
        env: { SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} }
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: snyk-code.sarif }

  snyk-deps:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/node@master
        with: { args: --severity-threshold=high --fail-on=upgradable }
        env: { SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} }

  snyk-container:
    needs: [sonar, snyk-code]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app:${{ github.sha }} .
      - uses: snyk/actions/docker@master
        with:
          image: app:${{ github.sha }}
          args: --severity-threshold=high --file=Dockerfile
        env: { SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} }
        continue-on-error: true   # advisory until base image is clean

  snyk-iac:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/iac@master
        with: { args: --severity-threshold=high }
        env: { SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} }</code></pre>

<table>
<tr><th>Concern</th><th>Tool</th><th>Gate</th></tr>
<tr><td>Quality &amp; coverage</td><td>SonarQube / SonarCloud</td><td>Sonar Way quality gate on new code</td></tr>
<tr><td>SAST</td><td>Snyk Code (DeepCode)</td><td>--severity-threshold=high</td></tr>
<tr><td>SCA (deps)</td><td>Snyk Open Source</td><td>--fail-on=upgradable</td></tr>
<tr><td>Container scan</td><td>Snyk Container or Trivy</td><td>Advisory until base image clean</td></tr>
<tr><td>IaC scan</td><td>Snyk IaC, Checkov, KICS</td><td>High-severity blocks</td></tr>
<tr><td>License compliance</td><td>Snyk License, FOSSA</td><td>Block on copyleft if needed</td></tr>
</table>

<p><strong>Trade-offs:</strong> Snyk is excellent but commercial; OSS alternatives are Trivy (containers + IaC + SCA), grype (containers), and Semgrep (SAST). SonarCloud is fast to set up but expensive at scale; self-hosted Sonar requires babysitting. Quality gates on the entire codebase are too noisy &mdash; always set them on <em>new code</em> only.</p>

<p><strong>Production polish:</strong> upload SARIF to GitHub Advanced Security for unified security findings; require both Sonar and Snyk PR checks in branch protection; add a weekly scheduled scan of the default branch so you catch newly disclosed CVEs without waiting for a PR. Tune Sonar profiles per language &mdash; defaults flag too much for established codebases. Add Renovate for automated dependency upgrades that close Snyk findings.</p>'''

ANSWERS[53] = r'''<p><strong>Situation:</strong> a Swift backend (Vapor or Hummingbird framework) needs CI/CD with unit/integration tests and deployment to AWS Lambda. Swift on Lambda runs via the AWS Lambda Runtime for Swift, packaged as a custom runtime layer or as a container image &mdash; the latter is easier to ship from CI.</p>

<p><strong>Approach:</strong> use the Swift AWS Lambda Runtime, build inside the official Swift toolchain image (<code>swift:5.10-amazonlinux2</code>) so the binary is statically linkable to AL2&rsquo;s glibc, package as a container image targeting <code>linux/arm64</code> for Graviton, push to ECR, and update the function via <code>aws lambda update-function-code</code>. CI runs <code>swift test</code> for both unit and integration suites with a Postgres service for integration.</p>

<pre><code># Dockerfile (multi-stage, arm64 Graviton)
FROM --platform=linux/arm64 swift:5.10-amazonlinux2 AS build
WORKDIR /src
COPY Package.* ./
RUN swift package resolve
COPY . .
RUN swift build -c release --static-swift-stdlib \
    --product LambdaHandler \
    -Xswiftc -O -Xswiftc -wmo

FROM public.ecr.aws/lambda/provided:al2023-arm64
COPY --from=build /src/.build/release/LambdaHandler /var/runtime/bootstrap
CMD ["bootstrap"]</code></pre>

<pre><code>name: swift-lambda
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test }
        ports: ['5432:5432']
    container: swift:5.10
    steps:
      - uses: actions/checkout@v4
      - run: swift package resolve
      - run: swift test --enable-code-coverage
      - run: |
          llvm-cov export -format=lcov \
            .build/debug/AppPackageTests.xctest \
            -instr-profile=.build/debug/codecov/default.profdata > coverage.lcov
      - uses: codecov/codecov-action@v4

  deploy:
    needs: test
    runs-on: ubuntu-24.04-arm
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/swift-lambda-deployer
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - name: Build and push image
        run: |
          IMG=123.dkr.ecr.ap-south-1.amazonaws.com/swift-lambda:${{ github.sha }}
          docker build --platform linux/arm64 -t $IMG .
          docker push $IMG
          echo "IMAGE=$IMG" &gt;&gt; $GITHUB_ENV
      - name: Update Lambda
        run: |
          aws lambda update-function-code \
            --function-name swift-api \
            --image-uri $IMAGE
          aws lambda wait function-updated --function-name swift-api
      - name: Publish version &amp; shift alias
        run: |
          VER=$(aws lambda publish-version --function-name swift-api --query Version --output text)
          aws lambda update-alias --function-name swift-api --name live \
            --function-version $VER \
            --routing-config AdditionalVersionWeights={"$VER"=0.1}</code></pre>

<table>
<tr><th>Choice</th><th>Recommendation</th></tr>
<tr><td>Runtime</td><td>swift-aws-lambda-runtime (Apple-maintained)</td></tr>
<tr><td>Architecture</td><td>arm64 / Graviton &mdash; ~25% cheaper</td></tr>
<tr><td>Package mode</td><td>Container image &mdash; simpler than custom runtime layer</td></tr>
<tr><td>Build base</td><td>swift:5.10-amazonlinux2 (matches Lambda OS ABI)</td></tr>
<tr><td>Cold start mitigation</td><td>Provisioned concurrency or SnapStart (Java/.NET only currently)</td></tr>
<tr><td>Routing</td><td>Alias with weighted versions for canary</td></tr>
</table>

<p><strong>Trade-offs:</strong> Swift on Lambda is niche &mdash; the runtime works well but is less battle-tested than Node/Python. Cold starts are good (~150ms for arm64 native) but Provisioned Concurrency is what eliminates them on critical paths. Vapor is heavier than the bare Lambda runtime; Hummingbird is the lighter option designed with Lambda in mind.</p>

<p><strong>Production polish:</strong> push CloudWatch Logs to a centralised log platform via subscription filter; add X-Ray tracing through <code>swift-aws-lambda-events</code> middleware. Use the alias weighted-routing pattern for canaries so a bad deploy only impacts 10% of traffic for the first 5 minutes. Sign images with Cosign keyless OIDC so Lambda&rsquo;s container scanner attests provenance.</p>'''

ANSWERS[54] = r'''<p><strong>Situation:</strong> the org runs production workloads on Azure Kubernetes Service (AKS) and wants GitHub Actions to handle build, push, and deploy with no static credentials in the repo. The pipeline must support staging and prod, run smoke tests, and roll back on failure.</p>

<p><strong>Approach:</strong> federated identity via Workload Identity Federation between GitHub OIDC and Azure AD (no client secrets), Azure Container Registry (ACR) for image storage, Helm or Kustomize for manifests, and either <code>azure/k8s-deploy</code> or Argo CD for the actual rollout. For prod use Argo Rollouts on the cluster so canary analysis happens locally and the workflow just bumps a tag.</p>

<pre><code>name: aks-cd
on:
  push: { branches: [main] }
  workflow_dispatch:
permissions: { id-token: write, contents: read }
env:
  ACR: myorg.azurecr.io
  RG: prod-rg
  CLUSTER: prod-aks
jobs:
  build-push:
    runs-on: ubuntu-24.04
    outputs: { tag: ${{ steps.meta.outputs.tag }} }
    steps:
      - uses: actions/checkout@v4
      - id: meta
        run: echo "tag=${{ github.sha }}" &gt;&gt; $GITHUB_OUTPUT
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az acr login --name ${ACR%.azurecr.io}
      - uses: docker/setup-buildx-action@v3
      - run: |
          docker buildx build --platform linux/amd64 \
            -t $ACR/api:${{ steps.meta.outputs.tag }} \
            --cache-from type=gha --cache-to type=gha,mode=max \
            --push .

  deploy-staging:
    needs: build-push
    runs-on: ubuntu-24.04
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az aks get-credentials -n $CLUSTER -g $RG --overwrite-existing
      - uses: azure/setup-helm@v4
      - run: |
          helm upgrade --install api ./charts/api \
            --namespace staging --create-namespace \
            --set image.tag=${{ needs.build-push.outputs.tag }} \
            --atomic --timeout 5m

  deploy-prod:
    needs: deploy-staging
    runs-on: ubuntu-24.04
    environment: prod   # required reviewers gate
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az aks get-credentials -n $CLUSTER -g $RG --overwrite-existing
      - run: |
          kubectl-argo-rollouts set image api \
            api=$ACR/api:${{ needs.build-push.outputs.tag }} -n prod
          kubectl-argo-rollouts status api -n prod --timeout 30m</code></pre>

<table>
<tr><th>Choice</th><th>Why</th></tr>
<tr><td>Auth</td><td>Workload Identity Federation &mdash; no JSON secrets in GitHub</td></tr>
<tr><td>Registry</td><td>ACR with content trust + scanning</td></tr>
<tr><td>Manifest tool</td><td>Helm with --atomic for staging; Argo Rollouts for prod</td></tr>
<tr><td>Approval gate</td><td>GitHub Environments with required reviewers for prod</td></tr>
<tr><td>Autoscaling</td><td>Karpenter for Azure (now GA) + KEDA for event scale</td></tr>
<tr><td>Identity to pods</td><td>Azure Workload Identity (replaces AAD Pod Identity)</td></tr>
</table>

<p><strong>Trade-offs:</strong> running Argo Rollouts adds a CRD and controller; if the workload is small a plain Helm <code>--atomic</code> upgrade might suffice. AKS-managed Karpenter (NAP &mdash; Node Auto Provisioning) is simpler than self-installed Karpenter but newer; pin to a stable AKS version before relying on it.</p>

<p><strong>Production polish:</strong> use GitHub Environments to gate prod with required reviewers and a deployment branch policy (main only). Wire AKS Container Insights to a central Log Analytics workspace. Use Azure Policy for AKS to enforce baselines (no privileged pods, image signature required). Push a SLSA provenance attestation alongside the image so admission controllers can verify build origin.</p>'''

ANSWERS[55] = r'''<p><strong>Situation:</strong> a Haskell backend (Servant, IHP, or Yesod) needs CI/CD with thorough testing &mdash; Haskell&rsquo;s strong type system catches a lot at compile time, but unit and integration tests still matter &mdash; and deployment to Google Cloud Functions (now via Cloud Run for second-gen functions, since Cloud Functions gen2 runs on Cloud Run under the hood). The team values reproducible builds and fast cold starts.</p>

<p><strong>Approach:</strong> use Stack or Cabal for the build, build inside <code>haskell:9.6</code> with caching of <code>~/.stack</code> and <code>.stack-work</code>, run <code>stack test</code> for HSpec / Tasty suites, package as a static binary in a distroless image (Haskell binaries link a lot of native libs &mdash; static linking via <code>--ghc-options=-static -optl-static</code> simplifies the runtime), and deploy to Cloud Run via <code>gcloud run deploy</code>.</p>

<pre><code># Dockerfile (Stack-based, static binary, distroless)
FROM haskell:9.6 AS build
WORKDIR /src
COPY stack.yaml stack.yaml.lock package.yaml ./
RUN stack setup &amp;&amp; stack build --only-dependencies
COPY . .
RUN stack install --local-bin-path /out \
    --ghc-options="-O2 -static -optl-static -optl-pthread"

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/server /server
EXPOSE 8080
ENV PORT=8080
USER nonroot
ENTRYPOINT ["/server"]</code></pre>

<pre><code>name: haskell-cf
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    container: haskell:9.6
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with:
          path: |
            ~/.stack
            .stack-work
          key: stack-${{ hashFiles('stack.yaml.lock', 'package.yaml') }}
          restore-keys: stack-
      - run: stack build --test --no-run-tests
      - run: stack test --coverage
      - run: stack hpc report --all

  deploy:
    needs: test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gha/providers/gh
          service_account: deployer@proj.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker asia-south1-docker.pkg.dev
      - name: Build and push
        run: |
          IMG=asia-south1-docker.pkg.dev/proj/repo/haskell-fn:${{ github.sha }}
          docker build -t $IMG .
          docker push $IMG
          echo "IMAGE=$IMG" &gt;&gt; $GITHUB_ENV
      - name: Deploy to Cloud Functions gen2 (Cloud Run)
        run: |
          gcloud run deploy haskell-fn \
            --image $IMAGE \
            --region asia-south1 \
            --concurrency 80 --cpu 1 --memory 512Mi \
            --min-instances 1 --max-instances 100 \
            --execution-environment gen2 \
            --no-allow-unauthenticated</code></pre>

<table>
<tr><th>Choice</th><th>Why</th></tr>
<tr><td>Build tool</td><td>Stack (LTS resolver) for reproducibility; Cabal works too</td></tr>
<tr><td>Compiler</td><td>GHC 9.6 LTS &mdash; stable, well-supported</td></tr>
<tr><td>Static linking</td><td>-static -optl-static for distroless deploys</td></tr>
<tr><td>Test framework</td><td>HSpec, Tasty, QuickCheck for property tests</td></tr>
<tr><td>Coverage</td><td>HPC (built-in) + stack hpc report</td></tr>
<tr><td>Deploy target</td><td>Cloud Run (gen2 Functions are Cloud Run under the hood)</td></tr>
</table>

<p><strong>Trade-offs:</strong> Haskell builds are slow without caching (5&ndash;10 min from cold) &mdash; cache <code>.stack</code> and <code>.stack-work</code> aggressively. Static binaries are large (50&ndash;100 MB); accept the size for ops simplicity. Cloud Functions gen1 has limited Haskell support; using gen2 (Cloud Run) sidesteps the limitation.</p>

<p><strong>Production polish:</strong> use <code>weeder</code> to detect unused exports, <code>hlint</code> for style, and <code>stan</code> for static analysis &mdash; all run in CI. Profile production with GHC eventlog and ship traces to a tracing backend. Set <code>min-instances 1</code> on Cloud Run for latency-sensitive endpoints; Haskell cold starts are 200&ndash;500ms which is fine for batch but noticeable on user-facing APIs.</p>'''

ANSWERS[56] = r'''<p><strong>Situation:</strong> a Kotlin team (Spring Boot, Ktor, or Micronaut) wants fast PR feedback &mdash; Kotlin/JVM compiles slowly without caching, and the gradle dependency graph is large. The mandate is sub-5-minute CI for typical PRs by aggressive caching of Gradle wrapper, dependencies, and build outputs.</p>

<p><strong>Approach:</strong> three layers of caching &mdash; (1) <strong>Gradle build cache</strong> (local and remote) for compiled task outputs, (2) <strong>dependency cache</strong> for resolved jars in <code>~/.gradle/caches</code>, and (3) <strong>Gradle daemon reuse</strong> via the gradle/actions setup. Use <code>gradle/actions/setup-gradle@v4</code> which handles all three automatically and writes a build scan link to the PR.</p>

<pre><code>name: kotlin-ci
on:
  pull_request:
  push: { branches: [main] }
permissions: { contents: read, checks: write, pull-requests: write }
jobs:
  build-test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 21 }
      - uses: gradle/actions/setup-gradle@v4
        with:
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}
          gradle-home-cache-cleanup: true
          dependency-graph: generate-and-submit
      - name: Build &amp; test
        run: ./gradlew build --build-cache --parallel
      - name: Detekt (static analysis)
        run: ./gradlew detekt
      - name: Test report
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: 'JUnit'
          path: '**/build/test-results/**/*.xml'
          reporter: 'java-junit'

  ktlint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 21 }
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew ktlintCheck</code></pre>

<table>
<tr><th>Cache layer</th><th>Detail</th></tr>
<tr><td>Gradle build cache</td><td>Local (per runner) + remote (e.g., Develocity, S3, GCS)</td></tr>
<tr><td>Dependency cache</td><td>~/.gradle/caches managed by setup-gradle</td></tr>
<tr><td>Gradle daemon</td><td>Reused across tasks for warm JVM</td></tr>
<tr><td>Configuration cache</td><td>--configuration-cache for skipping config phase</td></tr>
<tr><td>Worker reuse</td><td>org.gradle.workers.max in gradle.properties</td></tr>
<tr><td>Toolchain auto-provision</td><td>org.gradle.java.installations.auto-detect=true</td></tr>
</table>

<p><strong>Trade-offs:</strong> read-only cache on PRs prevents poisoning from forks but means PRs always read the main branch&rsquo;s cache. A remote build cache (Develocity, GCS, S3) is the single largest speedup for monorepos &mdash; small repos see less benefit. The Gradle dependency-graph submission feeds Dependabot but adds a small overhead.</p>

<p><strong>Production polish:</strong> generate a build scan (<code>--scan</code>) and post the URL on PRs for slow-build investigation. Use Kotlin compiler&rsquo;s <em>-Xuse-fir-lt</em> compiler when stable for faster compilation. Build native images with GraalVM <code>native-image</code> for production releases &mdash; cold start drops from seconds to milliseconds, which matters when paired with Cloud Run / Lambda. Run <code>./gradlew bootBuildImage</code> to produce CNB images that include CDS for faster JVM startup if you stay on the JVM.</p>'''

ANSWERS[57] = r'''<p><strong>Situation:</strong> the security team is reviewing the Jenkins controller and finds the usual suspects &mdash; admin-equivalent &ldquo;build&rdquo; users, plugins last updated in 2019, build agents running as root, secrets in build logs, no audit trail for config changes. The mandate is to <strong>harden the Jenkins server</strong> end-to-end without breaking productivity.</p>

<p><strong>Approach:</strong> seven hardening layers &mdash; (1) <strong>identity</strong> via SSO (SAML/OIDC) only, no local accounts, (2) <strong>authorisation</strong> via Matrix Authorisation or Role Strategy with least-privilege folders, (3) <strong>agent isolation</strong> via Kubernetes pod templates running non-root with seccomp, (4) <strong>secrets</strong> via HashiCorp Vault or external secrets only, never master.key, (5) <strong>plugin governance</strong> via JCasC + plugins.txt with a quarterly update cadence, (6) <strong>audit log</strong> via the Audit Trail plugin shipped to a SIEM, (7) <strong>script approval</strong> tightly governed; sandbox enabled.</p>

<pre><code># jenkins.yaml (JCasC excerpt)
jenkins:
  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: admin
            permissions: [Overall/Administer]
            assignments: [platform-admins]
          - name: developer
            permissions:
              - Overall/Read
              - Job/Build
              - Job/Read
              - Job/Cancel
            pattern: ".*"
            assignments: [authenticated]
  securityRealm:
    saml:
      idpMetadataConfiguration: { url: 'https://idp.example.com/metadata' }
      usernameAttributeName: 'NameID'
      groupsAttributeName: 'http://schemas.xmlsoap.org/claims/Group'
  remotingSecurity: { enabled: true }
  agentProtocols: ['JNLP4-connect']
  crumbIssuer:
    standard: { excludeClientIPFromCrumb: false }
unclassified:
  scriptApproval:
    approvedSignatures: []
    aclApprovedSignatures: []
  auditTrailConfiguration:
    loggers:
      - syslogLogger:
          syslogServerHostname: siem.internal
          syslogServerPort: 514
          appName: jenkins
credentials:
  system:
    domainCredentials:
      - credentials:
          - vaultAppRole:
              namespace: secrets
              path: jenkins
              roleId: ${VAULT_ROLE_ID}
              secretId: ${VAULT_SECRET_ID}</code></pre>

<table>
<tr><th>Layer</th><th>Control</th></tr>
<tr><td>Network</td><td>Behind reverse proxy (NGINX/Envoy) with TLS, IP allow-list to admin endpoints</td></tr>
<tr><td>Identity</td><td>SAML/OIDC via Keycloak, Okta, or Azure AD; MFA enforced</td></tr>
<tr><td>Authorisation</td><td>Role Strategy plugin, folder-scoped roles</td></tr>
<tr><td>Agents</td><td>Ephemeral K8s pods, non-root, seccomp, NetworkPolicy</td></tr>
<tr><td>Secrets</td><td>Vault plugin with AppRole/JWT auth, dynamic credentials</td></tr>
<tr><td>Plugins</td><td>JCasC plugins.txt, quarterly review, monitoring CVEs via plugin manager</td></tr>
<tr><td>Audit</td><td>Audit Trail plugin &rarr; SIEM (Splunk/Elastic/Sumo)</td></tr>
<tr><td>Backup</td><td>thinBackup or ThinBackup plugin to encrypted S3 daily</td></tr>
</table>

<p><strong>Trade-offs:</strong> tight script approval slows down advanced pipelines &mdash; balance with shared libraries that are pre-approved. Locking down agents to non-root breaks builds that need root (Docker daemon, package installs); use rootless Buildah/Kaniko/BuildKit instead. SSO-only excludes break-glass admin access; keep one well-protected emergency local account in a sealed envelope.</p>

<p><strong>Production polish:</strong> run Jenkins on the Jenkins Operator on Kubernetes &mdash; the operator enforces JCasC continuously and treats drift as policy violation. Schedule monthly CIS Jenkins benchmark scans via <code>jenkins-cli</code> and a custom evaluator. Migrate to GitHub Actions or Tekton for new workloads; Jenkins makes most sense as a long-tail legacy CI rather than greenfield.</p>'''

ANSWERS[58] = r'''<p><strong>Situation:</strong> the org has compliance obligations (PCI-DSS, HIPAA, SOC 2, FedRAMP) that require Docker images shipped to production to meet specific baselines &mdash; no high-severity CVEs, no root user, signed by a trusted key, with an SBOM and provenance attestation. The Jenkins pipeline has to enforce these checks before any image reaches a production registry.</p>

<p><strong>Approach:</strong> four pipeline gates &mdash; (1) <strong>vulnerability scan</strong> via Trivy or Grype with severity threshold, (2) <strong>policy scan</strong> via Conftest/OPA against Dockerfile (no <code>USER root</code>, no <code>:latest</code> base, etc.), (3) <strong>SBOM + signing</strong> via Syft and Cosign keyless OIDC, (4) <strong>admission backstop</strong> via Kyverno requiring signature on production cluster.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent { kubernetes { yaml libraryResource('agents/buildkit.yaml') } }
  environment {
    REGISTRY  = 'registry.example.com'
    IMAGE     = "${env.REGISTRY}/api:${env.GIT_COMMIT.take(8)}"
    COSIGN_EXPERIMENTAL = '1'
  }
  stages {
    stage('Lint Dockerfile') {
      steps {
        container('hadolint') { sh 'hadolint Dockerfile' }
        container('conftest') {
          sh 'conftest test --policy policy/dockerfile Dockerfile'
        }
      }
    }
    stage('Build &amp; push') {
      steps {
        container('buildkit') {
          sh &apos;&apos;&apos;
            buildctl build --frontend dockerfile.v0 \
              --local context=. --local dockerfile=. \
              --output type=image,name=$IMAGE,push=true \
              --opt build-arg:SOURCE_COMMIT=$GIT_COMMIT
          &apos;&apos;&apos;
        }
      }
    }
    stage('Vulnerability scan') {
      steps {
        container('trivy') {
          sh &apos;&apos;&apos;
            trivy image --severity HIGH,CRITICAL \
              --exit-code 1 --ignore-unfixed \
              --format sarif --output trivy.sarif $IMAGE
          &apos;&apos;&apos;
          recordIssues tools: [sarif(pattern: 'trivy.sarif')]
        }
      }
    }
    stage('SBOM &amp; sign') {
      steps {
        container('cosign') {
          sh &apos;&apos;&apos;
            syft $IMAGE -o cyclonedx-json &gt; sbom.json
            cosign sign --yes $IMAGE
            cosign attest --yes --predicate sbom.json --type cyclonedx $IMAGE
            cosign attest --yes --predicate provenance.json --type slsaprovenance $IMAGE
          &apos;&apos;&apos;
        }
      }
    }
    stage('Promote to prod registry') {
      when { branch 'main' }
      steps {
        container('crane') {
          sh 'crane copy $IMAGE ${REGISTRY}-prod/api:${GIT_COMMIT}'
        }
      }
    }
  }
}</code></pre>

<table>
<tr><th>Gate</th><th>Tool</th></tr>
<tr><td>Dockerfile lint</td><td>hadolint</td></tr>
<tr><td>Dockerfile policy</td><td>Conftest / OPA Rego</td></tr>
<tr><td>Vuln scan</td><td>Trivy, Grype</td></tr>
<tr><td>SBOM</td><td>Syft (CycloneDX or SPDX)</td></tr>
<tr><td>Signing</td><td>Cosign keyless via OIDC (Sigstore)</td></tr>
<tr><td>Provenance</td><td>SLSA Level 3 via in-toto attestations</td></tr>
<tr><td>Admission</td><td>Kyverno verifyImages or Sigstore Policy Controller</td></tr>
<tr><td>Base image hygiene</td><td>Chainguard images, Wolfi, distroless</td></tr>
</table>

<p><strong>Trade-offs:</strong> CVE noise is a real problem &mdash; ignore-unfixed and waiver files with expiry dates are essential. Cosign keyless requires an OIDC identity provider; in air-gapped environments use cosign with KMS keys instead. Kyverno admission can break legitimate deploys during the rollout; run audit-mode for two weeks before enforce.</p>

<p><strong>Production polish:</strong> push SBOMs to Dependency-Track for continuous monitoring &mdash; Trivy at build time only catches what was known then, but Dependency-Track watches for newly disclosed CVEs in already-shipped artefacts. Move to Chainguard or Wolfi base images: most distroless-equivalent images ship with zero CVEs, dramatically reducing scan noise. Push a SLSA Level 3 provenance and verify in admission &mdash; this is the supply-chain assurance auditors really care about now.</p>'''

ANSWERS[59] = r'''<p><strong>Situation:</strong> a Svelte / SvelteKit frontend team wants automated tests, accessibility checks, and deployment to AWS Amplify (which handles SSR, custom domains, and previews on PR branches). The pipeline must support both PR previews and production deploys with PR comments showing the preview URL.</p>

<p><strong>Approach:</strong> Amplify itself handles deployment from a Git push if connected, but a GitHub Actions pipeline gives more control &mdash; run unit tests with Vitest, e2e with Playwright, accessibility with axe, then trigger Amplify via the AWS API for explicit deploys. PR previews use Amplify&rsquo;s built-in branch deployments.</p>

<pre><code>name: svelte-amplify
on:
  pull_request:
  push: { branches: [main] }
permissions: { id-token: write, contents: read, pull-requests: write }
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run check         # svelte-check + tsc
      - run: npm run test:unit     # vitest
      - run: npx playwright install --with-deps chromium
      - run: npm run test:e2e      # playwright
      - run: npm run test:a11y     # axe-playwright
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/

  build:
    needs: test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with: { name: build, path: build/ }

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/amplify-deployer
          aws-region: ap-south-1
      - name: Trigger Amplify deploy
        run: |
          DEPLOY=$(aws amplify start-deployment \
            --app-id $AMPLIFY_APP_ID \
            --branch-name main \
            --query 'jobSummary.jobId' --output text)
          aws amplify get-job --app-id $AMPLIFY_APP_ID \
            --branch-name main --job-id $DEPLOY \
            --query 'job.summary.status'

  pr-preview-comment:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            const url = `https://pr-${context.issue.number}.${process.env.APP_ID}.amplifyapp.com`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `Preview: ${url}`
            });</code></pre>

<table>
<tr><th>Concern</th><th>Choice</th></tr>
<tr><td>Test framework</td><td>Vitest (unit) + Playwright (e2e) + axe (a11y)</td></tr>
<tr><td>Type check</td><td>svelte-check + tsc with strict mode</td></tr>
<tr><td>Adapter</td><td>@sveltejs/adapter-auto picks Amplify-compatible adapter</td></tr>
<tr><td>Auth</td><td>OIDC role assumption</td></tr>
<tr><td>Preview deploys</td><td>Amplify branch deployments per PR</td></tr>
<tr><td>SSR runtime</td><td>Amplify Gen 2 with SSR support</td></tr>
</table>

<p><strong>Trade-offs:</strong> Amplify adds AWS lock-in and a layer of magic over a vanilla S3+CloudFront+Lambda@Edge stack. For pure static SvelteKit, S3+CloudFront is cheaper and faster to deploy. Vercel and Cloudflare Pages handle SvelteKit very well too &mdash; Amplify makes most sense if you&rsquo;re already deep in AWS.</p>

<p><strong>Production polish:</strong> run Lighthouse CI in the pipeline against the preview URL; fail PR if performance budget regresses. Set the Amplify build cache to include <code>node_modules</code> and <code>.svelte-kit</code>. For real-world performance, enable Brotli compression on CloudFront, set immutable cache headers on hashed assets, and use Amplify&rsquo;s custom rewrites to handle SPA fallback. Monitor Core Web Vitals via SpeedCurve or PageSpeed Insights API.</p>'''

ANSWERS[60] = r'''<p><strong>Situation:</strong> a microservices stack (10+ services) on Kubernetes wants automated <strong>canary releases</strong> for the whole stack &mdash; a new feature might span 3 services, and the team wants to canary all three together with a single pipeline trigger and unified analysis. Jenkins orchestrates the canary; Argo Rollouts handles per-service traffic shifting.</p>

<p><strong>Approach:</strong> model each service as an independent Argo Rollout, but tag the canary cohort with a shared label (e.g., <code>release: 2026.05.0</code>) so analysis queries can correlate failures across services. Jenkins kicks off all three Rollouts in parallel, polls their status, and uses a shared AnalysisRun that checks aggregated SLOs. If any service&rsquo;s analysis fails, all three roll back together.</p>

<pre><code>// Jenkinsfile (multi-service canary)
pipeline {
  agent { kubernetes { yaml libraryResource('agents/argo-rollouts.yaml') } }
  parameters {
    string(name: 'RELEASE_TAG', defaultValue: '2026.05.0')
    string(name: 'IMAGE_TAG', defaultValue: 'auto')
  }
  stages {
    stage('Promote canaries in parallel') {
      parallel {
        stage('checkout-svc') {
          steps {
            container('kubectl') {
              sh "kubectl-argo-rollouts set image checkout checkout=ghcr.io/org/checkout:${IMAGE_TAG} -n prod"
            }
          }
        }
        stage('payments-svc') {
          steps {
            container('kubectl') {
              sh "kubectl-argo-rollouts set image payments payments=ghcr.io/org/payments:${IMAGE_TAG} -n prod"
            }
          }
        }
        stage('inventory-svc') {
          steps {
            container('kubectl') {
              sh "kubectl-argo-rollouts set image inventory inventory=ghcr.io/org/inventory:${IMAGE_TAG} -n prod"
            }
          }
        }
      }
    }
    stage('Wait for promotion or abort') {
      steps {
        container('kubectl') {
          script {
            timeout(time: 60, unit: 'MINUTES') {
              waitUntil {
                def states = ['checkout','payments','inventory'].collect { svc -&gt;
                  sh(script: "kubectl-argo-rollouts status ${svc} -n prod --timeout 30s", returnStatus: true)
                }
                if (states.any { it != 0 }) {
                  // any failure aborts all
                  sh "kubectl-argo-rollouts abort checkout payments inventory -n prod"
                  error("Multi-service canary aborted")
                }
                return states.every { it == 0 }
              }
            }
          }
        }
      }
    }
  }
}</code></pre>

<pre><code># AnalysisTemplate shared across services
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: cross-service-slo, namespace: prod }
spec:
  args: [{ name: release-tag }]
  metrics:
    - name: error-rate
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{release="{{args.release-tag}}",status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{release="{{args.release-tag}}"}[5m]))
      successCondition: result[0] &lt; 0.01
      interval: 1m
      count: 5</code></pre>

<table>
<tr><th>Pattern</th><th>Detail</th></tr>
<tr><td>Independent Rollouts</td><td>Each service has its own Rollout CRD</td></tr>
<tr><td>Shared release label</td><td>release=2026.05.0 set on canary template</td></tr>
<tr><td>Aggregated AnalysisRun</td><td>Prometheus query filters by release label</td></tr>
<tr><td>All-or-nothing abort</td><td>Jenkins coordinates: any failure aborts every Rollout</td></tr>
<tr><td>Service mesh integration</td><td>Istio/Linkerd traffic split for HTTP-aware routing</td></tr>
<tr><td>Feature flags as alternative</td><td>LaunchDarkly/Flagsmith for per-user canary</td></tr>
</table>

<p><strong>Trade-offs:</strong> coordinating Rollouts across services is conceptually clean but operationally complex &mdash; one slow Rollout blocks the whole release. Many teams opt for feature flags instead: deploy code dark to all services simultaneously, then flip the flag on for a small user cohort. The flag approach decouples deploy from release and is far easier to roll back.</p>

<p><strong>Production polish:</strong> add a <em>release readiness</em> dashboard showing all Rollouts on one screen with their current canary weight and analysis status. Annotate every Rollout with the Jenkins build URL and Slack channel. For services that share a database, pre-deploy schema migrations using expand/contract so both old and new versions work concurrently. Consider Kargo for promoting releases through stages with manual gates.</p>'''

ANSWERS[61] = r'''<p><strong>Situation:</strong> a TypeScript application (Node.js backend, NestJS or Fastify) needs CI/CD with strict type checking, unit and integration tests, and deployment to Heroku. The team values fast PR feedback and reproducible builds; Heroku is the chosen platform for ops simplicity even though container alternatives exist.</p>

<p><strong>Approach:</strong> a standard Node.js GitHub Actions pipeline with caching, plus deployment via the official <code>akhileshns/heroku-deploy</code> action or by using Heroku Container Registry (which supports Docker-based deploys, allowing fully reproducible builds). For 2026, container-based Heroku deploys are the recommended path &mdash; you build the image once and Heroku just runs it.</p>

<pre><code># Dockerfile (multi-stage, slim production image)
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

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/main.js"]</code></pre>

<pre><code>name: ts-heroku
on:
  pull_request:
  push: { branches: [main] }
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: test }
        ports: ['5432:5432']
        options: --health-cmd pg_isready
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test
      - run: npm run test:integration
        env: { DATABASE_URL: postgres://postgres:test@localhost:5432/test }
      - uses: codecov/codecov-action@v4

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Login to Heroku Container Registry
        run: echo ${{ secrets.HEROKU_API_KEY }} | docker login --username=_ --password-stdin registry.heroku.com
      - name: Build &amp; push container
        run: |
          docker build -t registry.heroku.com/${{ secrets.HEROKU_APP }}/web .
          docker push registry.heroku.com/${{ secrets.HEROKU_APP }}/web
      - name: Release container
        env: { HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }} }
        run: |
          IMAGE_ID=$(docker inspect registry.heroku.com/${{ secrets.HEROKU_APP }}/web --format='{{.Id}}')
          curl -X PATCH https://api.heroku.com/apps/${{ secrets.HEROKU_APP }}/formation \
            -d "{\"updates\":[{\"type\":\"web\",\"docker_image\":\"$IMAGE_ID\"}]}" \
            -H "Content-Type: application/json" \
            -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
            -H "Authorization: Bearer $HEROKU_API_KEY"</code></pre>

<table>
<tr><th>Choice</th><th>Why</th></tr>
<tr><td>Container-based Heroku</td><td>Reproducible; matches local dev exactly</td></tr>
<tr><td>Multi-stage Dockerfile</td><td>Small runtime image, no dev deps</td></tr>
<tr><td>Postgres service</td><td>Real DB for integration tests</td></tr>
<tr><td>Type check separate from build</td><td>Faster failure on type errors</td></tr>
<tr><td>Strict TypeScript</td><td>strict, noUncheckedIndexedAccess</td></tr>
<tr><td>Test runner</td><td>Vitest or Jest; native --experimental-test-runner for greenfield</td></tr>
</table>

<p><strong>Trade-offs:</strong> Heroku in 2026 is a niche choice &mdash; pricing has risen, free tier is gone, dyno performance lags Fly/Render/Railway. For new apps, those alternatives are cheaper and faster. Heroku still wins on add-on ecosystem (Heroku Postgres, Redis, Scheduler) and is hands-off operationally. If the team prioritises ops simplicity over cost, Heroku remains rational.</p>

<p><strong>Production polish:</strong> use Heroku review apps so each PR gets a temporary instance for QA. Configure release phase commands for migrations (<code>release: npx prisma migrate deploy</code>). Push logs to Papertrail or Logtail; metrics to Heroku Metrics or Datadog. Consider migrating to Render or Fly when growth makes Heroku&rsquo;s Performance dyno costs uncomfortable.</p>'''

ANSWERS[62] = r'''<p><strong>Situation:</strong> the data science team has stable training pipelines and now wants to ship models reliably to Kubernetes &mdash; with versioned model artefacts, GPU-aware deployment, canary rollouts, and continuous performance monitoring. Models live in MLflow Model Registry; serving uses KServe; CI/CD uses GitHub Actions.</p>

<p><strong>Approach:</strong> separate <strong>code</strong> (training scripts, serving image) from <strong>artefacts</strong> (model weights). When a new model is registered in MLflow with the &ldquo;Production&rdquo; alias, a webhook triggers a GitHub Actions workflow that updates the KServe InferenceService manifest in the GitOps repo, which Argo CD picks up and deploys with traffic split for canary.</p>

<pre><code>name: ml-deploy
on:
  workflow_dispatch:
    inputs:
      model_name: { required: true }
      model_version: { required: true }
  repository_dispatch:
    types: [mlflow-promotion]
permissions: { id-token: write, contents: write }
jobs:
  deploy:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { repository: org/k8s-manifests, token: ${{ secrets.GITOPS_PAT }} }
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/mlflow-reader
          aws-region: ap-south-1
      - name: Fetch model URI from MLflow
        id: mlflow
        run: |
          URI=$(curl -s -H "Authorization: Bearer ${{ secrets.MLFLOW_TOKEN }}" \
            "$MLFLOW_HOST/api/2.0/mlflow/model-versions/get?name=${{ inputs.model_name }}&amp;version=${{ inputs.model_version }}" \
            | jq -r .model_version.source)
          echo "uri=$URI" &gt;&gt; $GITHUB_OUTPUT
      - name: Update InferenceService manifest
        run: |
          yq -i ".spec.predictor.model.storageUri = \"${{ steps.mlflow.outputs.uri }}\"" \
            inference/${{ inputs.model_name }}/inferenceservice.yaml
          yq -i ".metadata.annotations.modelVersion = \"${{ inputs.model_version }}\"" \
            inference/${{ inputs.model_name }}/inferenceservice.yaml
      - run: |
          git config user.email "ci@org.com"; git config user.name "ci"
          git add . &amp;&amp; git commit -m "Bump ${{ inputs.model_name }} to v${{ inputs.model_version }}"
          git push</code></pre>

<pre><code># InferenceService with canary
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata: { name: fraud-classifier, namespace: ml }
spec:
  predictor:
    model:
      modelFormat: { name: sklearn }
      storageUri: s3://mlflow/artifacts/12/fraud-v42/model
      runtime: kserve-sklearnserver
      resources:
        requests: { cpu: '1', memory: 2Gi, nvidia.com/gpu: '1' }
        limits:   { cpu: '2', memory: 4Gi, nvidia.com/gpu: '1' }
    canaryTrafficPercent: 10
    minReplicas: 1
    maxReplicas: 10
  transformer:
    containers:
      - image: ghcr.io/org/feature-transformer:1.4.0
        name: transformer</code></pre>

<table>
<tr><th>Concern</th><th>Tool (2026)</th></tr>
<tr><td>Model registry</td><td>MLflow, Hugging Face Hub, W&amp;B</td></tr>
<tr><td>Serving on K8s</td><td>KServe, Seldon Core v2, Ray Serve, BentoML</td></tr>
<tr><td>LLM serving</td><td>vLLM, TensorRT-LLM, TGI</td></tr>
<tr><td>GPU scheduling</td><td>NVIDIA GPU Operator + KAI/Volcano scheduler</td></tr>
<tr><td>Drift detection</td><td>Evidently AI, NannyML, Arize, WhyLabs</td></tr>
<tr><td>Feature store</td><td>Feast, Tecton, Hopsworks</td></tr>
<tr><td>Promotion gate</td><td>Holdout eval &gt; production model on key metric</td></tr>
</table>

<p><strong>Trade-offs:</strong> KServe handles autoscaling and canary natively; rolling your own with raw Deployments quickly turns into a custom platform. GPU costs dominate at scale &mdash; consider quantisation (int8/int4), batching, and CPU fallback for low-throughput models. For LLMs specifically, vLLM&rsquo;s continuous batching and PagedAttention deliver order-of-magnitude throughput improvements.</p>

<p><strong>Production polish:</strong> add post-deploy drift monitoring &mdash; data drift (input distribution change) and prediction drift (output distribution change) catch silent regressions that accuracy on holdout doesn&rsquo;t. Use shadow deploys to compare new model predictions against current model on real traffic without serving them. Sign model artefacts with Cosign and verify in admission so a tampered model can&rsquo;t be loaded.</p>'''

ANSWERS[63] = r'''<p><strong>Situation:</strong> the org has chosen multi-cloud for resilience and to avoid lock-in &mdash; production runs on both AWS (EKS) and GCP (GKE) with active-active or active-passive routing. CI/CD pipelines must deploy the same containerised workloads to both, with consistent IaC, policies, and observability.</p>

<p><strong>Approach:</strong> Crossplane or OpenTofu for cloud-agnostic IaC, a single container registry mirrored across clouds (or a federated registry like Harbor with replication), Argo CD ApplicationSets generating one Application per (cluster &times; environment), and a global service mesh (Istio multi-cluster, Cilium ClusterMesh, or Linkerd multi-cluster) for cross-cluster service discovery.</p>

<pre><code># ApplicationSet generating per-cluster Applications
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: api, namespace: argocd }
spec:
  generators:
    - clusters:
        selector:
          matchLabels: { env: prod }
  template:
    metadata: { name: 'api-{{name}}' }
    spec:
      project: default
      source:
        repoURL: https://github.com/org/manifests
        targetRevision: HEAD
        path: 'apps/api/overlays/{{metadata.labels.cloud}}'
      destination:
        server: '{{server}}'
        namespace: prod
      syncPolicy:
        automated: { prune: true, selfHeal: true }
        syncOptions: [CreateNamespace=true]</code></pre>

<pre><code>name: multi-cloud-build
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: write }
jobs:
  build:
    runs-on: ubuntu-24.04
    outputs: { tag: ${{ steps.meta.outputs.tag }} }
    steps:
      - uses: actions/checkout@v4
      - id: meta
        run: echo "tag=${{ github.sha }}" &gt;&gt; $GITHUB_OUTPUT
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - run: |
          docker buildx build --platform linux/amd64,linux/arm64 \
            -t ghcr.io/org/api:${{ steps.meta.outputs.tag }} \
            --cache-from type=gha --cache-to type=gha,mode=max \
            --push .

  mirror-aws:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/registry-mirror
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          crane copy ghcr.io/org/api:${{ needs.build.outputs.tag }} \
            123.dkr.ecr.ap-south-1.amazonaws.com/api:${{ needs.build.outputs.tag }}

  mirror-gcp:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gha/providers/gh
          service_account: registry@proj.iam.gserviceaccount.com
      - run: |
          gcloud auth configure-docker asia-south1-docker.pkg.dev
          crane copy ghcr.io/org/api:${{ needs.build.outputs.tag }} \
            asia-south1-docker.pkg.dev/proj/repo/api:${{ needs.build.outputs.tag }}

  promote:
    needs: [mirror-aws, mirror-gcp]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { repository: org/manifests, token: ${{ secrets.GITOPS_PAT }} }
      - run: |
          for cloud in aws gcp; do
            yq -i ".images[0].newTag = \"${{ needs.build.outputs.tag }}\"" apps/api/overlays/$cloud/kustomization.yaml
          done
          git config user.email ci@org.com; git config user.name ci
          git add . &amp;&amp; git commit -m "api ${{ needs.build.outputs.tag }}" &amp;&amp; git push</code></pre>

<table>
<tr><th>Layer</th><th>Multi-cloud tool (2026)</th></tr>
<tr><td>IaC</td><td>OpenTofu, Pulumi, Crossplane</td></tr>
<tr><td>K8s</td><td>EKS + GKE + AKS, all GitOps&rsquo;d via Argo CD</td></tr>
<tr><td>Registry</td><td>Single source (GHCR/Harbor) + crane mirror, or replicated</td></tr>
<tr><td>Service mesh</td><td>Istio multi-cluster, Cilium ClusterMesh, Linkerd multi-cluster</td></tr>
<tr><td>DNS / routing</td><td>Cloudflare load balancing, AWS Route53 latency routing</td></tr>
<tr><td>Identity</td><td>SPIFFE/SPIRE for cross-cloud workload identity</td></tr>
<tr><td>Observability</td><td>OpenTelemetry &rarr; Grafana Cloud / Datadog / New Relic</td></tr>
</table>

<p><strong>Trade-offs:</strong> multi-cloud&rsquo;s biggest cost isn&rsquo;t infrastructure but cognitive load &mdash; engineers must learn two everything (IAM, networking, service catalogues). For most orgs, single-cloud with a clear DR runbook is cheaper than true multi-cloud. Pursue multi-cloud only when regulatory, customer, or vendor-leverage requirements compel it.</p>

<p><strong>Production polish:</strong> use SLSA Level 3 provenance signing so admission controllers can verify images regardless of which cloud they pulled from. For data plane, plan for cross-cloud egress costs (terabytes/month is brutal) &mdash; prefer regional locality and async replication. Run chaos engineering exercises that fail over from one cloud to the other quarterly; failover paths that are never exercised never work.</p>'''

ANSWERS[64] = r'''<p><strong>Situation:</strong> a serverless application (Lambda + API Gateway + DynamoDB, or Cloud Functions + Firestore) needs the same security and compliance bar as the rest of the org &mdash; SAST, SCA, IaC scanning, and runtime policy. Serverless removes some attack surface (no OS, no patching) but introduces new ones: function permissions, event injection, dependency-laden zips.</p>

<p><strong>Approach:</strong> shift-left with five gates &mdash; (1) <strong>SAST</strong> via Semgrep with serverless rules, (2) <strong>SCA</strong> via Snyk or OSV-Scanner on dependency manifest, (3) <strong>IaC scanning</strong> via Checkov on SAM/Terraform/CDK templates, (4) <strong>function permissions linting</strong> via cfn-lint or AWS Config rules to flag wildcards, (5) <strong>secret scanning</strong> via gitleaks. Add runtime policy via AWS Lambda Powertools idempotency and AWS WAF on API Gateway.</p>

<pre><code>name: serverless-security
on:
  pull_request:
  push: { branches: [main] }
permissions: { contents: read, security-events: write, id-token: write }
jobs:
  sast:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: |
            p/serverless
            p/owasp-top-ten
            p/security-audit

  sca:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci --omit=dev
      - uses: snyk/actions/node@master
        with: { args: --severity-threshold=high --fail-on=upgradable }
        env: { SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} }
      - run: npx osv-scanner --lockfile package-lock.json

  iac-scan:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: serverless,cloudformation,terraform
          output_format: sarif
          soft_fail: false
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with: { sarif_file: results.sarif }

  permissions-lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          pip install cfn-lint
          cfn-lint --include-checks I -t template.yaml

  policy-test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          docker run --rm -v $PWD:/work openpolicyagent/conftest \
            test --policy /work/policy /work/template.yaml</code></pre>

<table>
<tr><th>Risk</th><th>Mitigation</th></tr>
<tr><td>Over-broad IAM (Action: *)</td><td>cfn-lint, IAM Access Analyzer, OPA policy</td></tr>
<tr><td>Vulnerable dependencies</td><td>Snyk, Dependabot, OSV-Scanner</td></tr>
<tr><td>Insecure code</td><td>Semgrep, CodeQL with serverless rules</td></tr>
<tr><td>Event injection</td><td>Schema validation via Powertools, AJV</td></tr>
<tr><td>Public buckets / open APIs</td><td>Checkov, AWS Config managed rules</td></tr>
<tr><td>Secrets in code</td><td>gitleaks, trufflehog, AWS git-secrets</td></tr>
<tr><td>Cold-start side channels</td><td>Use SnapStart (Java/.NET/Python) carefully</td></tr>
</table>

<p><strong>Trade-offs:</strong> serverless security tools are noisier than traditional ones because IaC frameworks generate boilerplate that triggers warnings. Maintain per-repo waiver files with expiry. Snyk + Checkov is paid; OSV-Scanner + Trivy + Conftest is the OSS-only stack and works well.</p>

<p><strong>Production polish:</strong> wire AWS GuardDuty Lambda Protection (or its equivalent on GCP) for runtime detection of malicious behaviour. Use AWS WAF in front of API Gateway with managed rule groups (Common, Known Bad Inputs, Linux OS, SQLi). Enable Lambda Function URL signing or rely on API Gateway authorisers; never accept unauthenticated Lambda invocations except through a signed gateway. SLSA-attest deployment artefacts and verify in OPA before <code>aws lambda update-function-code</code> runs.</p>'''

ANSWERS[65] = r'''<p><strong>Situation:</strong> a Scala backend (Akka HTTP, Play, http4s, or ZIO HTTP) needs CI/CD with automated tests and deployment to AWS Lambda. Scala on Lambda is feasible via two paths: GraalVM native-image for fast cold starts, or the JVM with SnapStart for warm-pool optimisation. The team picks GraalVM for predictable sub-second cold starts.</p>

<p><strong>Approach:</strong> use sbt with sbt-native-packager and sbt-native-image, build a static-ish Linux binary with GraalVM, package as a Lambda container image, and deploy to Lambda&rsquo;s arm64 (Graviton) runtime. The CI runs <code>sbt test</code>, builds the native image, and ships via <code>aws lambda update-function-code</code>.</p>

<pre><code>// build.sbt
enablePlugins(NativeImagePlugin)
ThisBuild / scalaVersion := "3.5.0"
nativeImageVersion := "21.0.2"
nativeImageOptions ++= Seq(
  "--no-fallback",
  "--enable-url-protocols=https",
  "--initialize-at-build-time",
  "-H:+ReportExceptionStackTraces",
  "-H:IncludeResources=.*\\.conf$"
)
nativeImageJvm := "graalvm-community"</code></pre>

<pre><code># Dockerfile (multi-stage: GraalVM build, Lambda runtime)
FROM ghcr.io/graalvm/native-image-community:21 AS build
WORKDIR /src
RUN curl -L https://github.com/sbt/sbt/releases/download/v1.10.0/sbt-1.10.0.tgz | tar xz -C /opt
ENV PATH="/opt/sbt/bin:${PATH}"
COPY . .
RUN sbt nativeImage

FROM public.ecr.aws/lambda/provided:al2023-arm64
COPY --from=build /src/target/native-image/app /var/runtime/bootstrap
RUN chmod +x /var/runtime/bootstrap
CMD ["bootstrap"]</code></pre>

<pre><code>name: scala-lambda
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: graalvm-community, java-version: '21' }
      - uses: sbt/setup-sbt@v1
      - uses: actions/cache@v4
        with:
          path: |
            ~/.sbt
            ~/.coursier
          key: sbt-${{ hashFiles('**/*.sbt', 'project/**') }}
      - run: sbt scalafmtCheckAll test

  build-deploy:
    needs: test
    runs-on: ubuntu-24.04-arm
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/scala-lambda-deployer
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - name: Build native image &amp; push
        run: |
          IMG=123.dkr.ecr.ap-south-1.amazonaws.com/scala-lambda:${{ github.sha }}
          docker build --platform linux/arm64 -t $IMG .
          docker push $IMG
          aws lambda update-function-code \
            --function-name scala-api --image-uri $IMG
          aws lambda wait function-updated --function-name scala-api</code></pre>

<table>
<tr><th>Choice</th><th>Why</th></tr>
<tr><td>Scala 3 + JDK 21</td><td>Modern toolchain; better GraalVM compat</td></tr>
<tr><td>GraalVM native-image</td><td>~50ms cold start vs ~500ms+ on JVM</td></tr>
<tr><td>arm64 / Graviton</td><td>~25% cost savings; native-image cross-compiles fine</td></tr>
<tr><td>Lambda container image</td><td>Simpler than custom runtime layer for native binaries</td></tr>
<tr><td>HTTP framework</td><td>http4s or ZIO HTTP &mdash; native-image friendly</td></tr>
<tr><td>Effect system</td><td>Cats Effect 3 or ZIO 2</td></tr>
</table>

<p><strong>Trade-offs:</strong> native-image build is slow (5&ndash;15 min) and memory-hungry &mdash; cache aggressively. Reflection-heavy libraries (Jackson default config, Scala macros) require explicit native-image config; reachability metadata helps but isn&rsquo;t bulletproof. Akka HTTP and Play are reflection-heavy and harder to native-compile than http4s; pick the framework with this in mind.</p>

<p><strong>Production polish:</strong> SnapStart is now an option for non-native JVM deploys with sub-second cold starts &mdash; consider that path if native-image proves problematic. Use Lambda function aliases with weighted routing for canary deploys. Push CloudWatch Logs to a centralised analytics platform via subscription filter, and instrument with OpenTelemetry for traces. Build an arm64-native runner (<code>ubuntu-24.04-arm</code>) for fastest builds.</p>'''

ANSWERS[66] = r'''<p><strong>Situation:</strong> the team wants GitHub Actions to deliver to Google Kubernetes Engine continuously &mdash; build a container, push to Artifact Registry, and roll out to a GKE Autopilot or Standard cluster across staging and production with proper auth and progressive delivery.</p>

<p><strong>Approach:</strong> use Workload Identity Federation (WIF) so the workflow assumes a Google service account without static keys; build with Buildx targeting <code>linux/amd64,linux/arm64</code> and push to Artifact Registry; render Kustomize manifests with the new image digest; promote via Argo CD or use the official <code>google-github-actions/get-gke-credentials</code> + <code>kubectl apply</code> for simpler shops. Cloud Deploy is the GCP-native progressive delivery option for canary/blue-green across targets.</p>

<pre><code>name: deploy-gke
on:
  push: { branches: [main] }
permissions: { id-token: write, contents: write }
jobs:
  ship:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh
          service_account: gha-deployer@proj.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker asia-south1-docker.pkg.dev
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          push: true
          platforms: linux/amd64
          tags: asia-south1-docker.pkg.dev/proj/repo/api:${{ github.sha }}
          provenance: true
          sbom: true
      - uses: google-github-actions/get-gke-credentials@v2
        with: { cluster_name: prod, location: asia-south1 }
      - run: |
          cd k8s/overlays/prod
          kustomize edit set image api=asia-south1-docker.pkg.dev/proj/repo/api:${{ github.sha }}
          git -c user.email=ci@x -c user.name=ci commit -am "deploy ${{ github.sha }}"
          git push   # Argo CD picks it up
</code></pre>

<table>
<tr><th>Choice</th><th>2026 default</th></tr>
<tr><td>Auth</td><td>WIF (never JSON keys)</td></tr>
<tr><td>Cluster type</td><td>GKE Autopilot for hands-off; Standard for custom node pools</td></tr>
<tr><td>Registry</td><td>Artifact Registry with vulnerability scanning enabled</td></tr>
<tr><td>Sync strategy</td><td>Argo CD with image automation, or Cloud Deploy</td></tr>
<tr><td>Progressive delivery</td><td>Argo Rollouts or Cloud Deploy canary</td></tr>
<tr><td>Policy</td><td>Binary Authorization gates pods to signed images</td></tr>
</table>

<p><strong>Trade-offs:</strong> direct <code>kubectl apply</code> is simpler but loses GitOps drift detection &mdash; Argo CD adds operational overhead but pays off the first time someone hand-edits a Deployment. Cloud Deploy is GCP-locked but integrates with Cloud Build and audit logs cleanly. Autopilot prices per pod-second and removes node management; Standard wins for spot pools, GPU, and aggressive bin-packing.</p>

<p><strong>Production polish:</strong> require Cosign signatures and verify with Binary Authorization &mdash; unsigned images don&rsquo;t deploy. Enable GKE Backup for cluster restore and Config Sync for fleet-wide policy. Push pod logs to Cloud Logging via the Logging agent, and set Cloud Trace via OpenTelemetry. Run Kyverno or Gatekeeper for policy at admission, complementing Binary Authorization at image pull. Tag images with both the SHA and a semver tag so rollback by version is one Argo CD parameter change.</p>'''

ANSWERS[67] = r'''<p><strong>Situation:</strong> an Elixir/Phoenix application needs CI/CD with unit and integration tests plus deployment to Heroku. Elixir compiles to BEAM bytecode, runs with hot upgrades natively, and benefits from a release-based packaging approach (<code>mix release</code>) rather than running <code>mix phx.server</code> in production.</p>

<p><strong>Approach:</strong> use GitHub Actions with a matrix on Elixir/OTP versions, cache <code>deps</code> and <code>_build</code> directories, run <code>mix format --check-formatted</code>, Credo for static analysis, Dialyzer for typing, ExUnit for tests, and Wallaby or Hound for browser-based integration tests. For Heroku, use the official Elixir buildpack or container deploys via the Container Registry &mdash; the latter gives you full control of the runtime image.</p>

<pre><code>name: phoenix
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: postgres }
        options: --health-cmd "pg_isready"
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: erlef/setup-beam@v1
        with: { otp-version: '27', elixir-version: '1.17' }
      - uses: actions/cache@v4
        with:
          path: |
            deps
            _build
            priv/plts
          key: mix-${{ hashFiles('mix.lock') }}
      - run: mix deps.get
      - run: mix format --check-formatted
      - run: mix credo --strict
      - run: mix dialyzer
      - run: mix ecto.create &amp;&amp; mix ecto.migrate
      - run: mix test --cover
      - uses: codecov/codecov-action@v4

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "machine api.heroku.com login _ password ${{ secrets.HEROKU_API_KEY }}" &gt;&gt; ~/.netrc
          echo "machine git.heroku.com login _ password ${{ secrets.HEROKU_API_KEY }}" &gt;&gt; ~/.netrc
          heroku stack:set container -a phoenix-prod
          heroku container:login
          heroku container:push web -a phoenix-prod
          heroku container:release web -a phoenix-prod
          heroku run -a phoenix-prod "POOL_SIZE=2 ./bin/myapp eval 'MyApp.Release.migrate()'"
</code></pre>

<table>
<tr><th>Choice</th><th>Detail</th></tr>
<tr><td>Buildpack vs container</td><td>Container for full runtime control; buildpack for simplicity</td></tr>
<tr><td>Release type</td><td><code>mix release</code> for a self-contained tarball with ERTS bundled</td></tr>
<tr><td>DB migrations</td><td>Run via Heroku release phase or manual <code>heroku run</code></td></tr>
<tr><td>Connection pool</td><td>Set <code>POOL_SIZE</code> via env to match Heroku Postgres tier</td></tr>
<tr><td>Static analysis</td><td>Credo + Dialyzer + Sobelow (security)</td></tr>
</table>

<p><strong>Trade-offs:</strong> Heroku is on the decline in 2026 &mdash; Render, Fly.io, and Railway are cheaper and more developer-friendly. Fly.io in particular maps almost 1:1 to Phoenix releases (LiveView WebSocket-friendly, multi-region). Hot upgrades via <code>:appup</code> files are powerful but rarely worth the complexity; rolling restarts via <code>heroku ps:restart</code> are simpler.</p>

<p><strong>Production polish:</strong> use Phoenix LiveDashboard for runtime introspection, AppSignal or New Relic for APM, and Logflare for log aggregation. Configure <code>:libcluster</code> for distributed Erlang in multi-dyno setups (Fly.io DNS topology works out of the box; Heroku requires manual node names). Cache compiled assets across builds with <code>mix assets.deploy</code>. Strongly consider migrating to Fly.io: Phoenix performs noticeably better there, and per-region deploys are trivial.</p>'''

ANSWERS[68] = r'''<p><strong>Situation:</strong> a Go service has slow CI because <code>go mod download</code> and the build run from scratch each push. Go module caching plus build caching can cut a 5-minute job to under a minute on incremental changes.</p>

<p><strong>Approach:</strong> Go has two cache directories &mdash; <code>$GOPATH/pkg/mod</code> for downloaded modules (keyed by go.sum) and <code>$GOCACHE</code> for compiled object files (keyed by source content). The <code>actions/setup-go</code> action handles both automatically when you set <code>cache: true</code>; for finer control use <code>actions/cache</code> with explicit keys. Combined with build constraints and parallel <code>go test</code>, builds become near-instantaneous.</p>

<pre><code>name: go-ci
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true   # caches both pkg/mod and GOCACHE

      - name: Verify modules
        run: go mod verify

      - name: Lint
        uses: golangci/golangci-lint-action@v6
        with: { version: v1.64 }

      - name: Vet
        run: go vet ./...

      - name: Race tests
        run: go test -race -coverprofile=cover.out ./...

      - name: Coverage
        uses: codecov/codecov-action@v4
        with: { files: cover.out }

      - name: Build
        run: |
          CGO_ENABLED=0 GOOS=linux go build \
            -ldflags="-s -w -X main.version=${{ github.sha }}" \
            -trimpath \
            -o bin/api ./cmd/api

      - name: Govulncheck
        uses: golang/govulncheck-action@v1

      - name: Build container
        uses: docker/build-push-action@v5
        with:
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          push: ${{ github.ref == 'refs/heads/main' }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
</code></pre>

<table>
<tr><th>Cache layer</th><th>Hit ratio impact</th></tr>
<tr><td>$GOPATH/pkg/mod</td><td>Skips network downloads on go.sum unchanged</td></tr>
<tr><td>$GOCACHE</td><td>Skips re-compile of unchanged packages</td></tr>
<tr><td>Buildx GHA cache</td><td>Skips Docker layer rebuild</td></tr>
<tr><td>actions/setup-go cache: true</td><td>Bundles both Go caches</td></tr>
<tr><td>Build matrix</td><td>One cache per (OS, Go version) tuple</td></tr>
</table>

<p><strong>Trade-offs:</strong> GHA cache is 10 GB per repo branch and evicts old entries &mdash; very large monorepos may need a dedicated cache backend (BuildKit with S3, Actuated). Module cache hit ratio drops to zero on go.sum churn; group dep updates via Renovate or Dependabot weekly batching. Build cache is content-addressed so flag-only changes (e.g., <code>-tags=integration</code>) get a fresh cache slot.</p>

<p><strong>Production polish:</strong> add <code>govulncheck</code> as a required check &mdash; it scans both modules <em>and</em> the build call graph, surfacing only actually-reachable CVEs. Use <code>-trimpath</code> in builds for reproducible binaries. For arm64 deploys (Graviton, Cloud Run, Fargate) build with <code>--platform=linux/arm64</code> on <code>ubuntu-24.04-arm</code> runners &mdash; native arm64 builds are dramatically faster than QEMU emulation. Keep test binaries with <code>go test -c</code> for parallel sharding across runners on huge suites.</p>'''

ANSWERS[69] = r'''<p><strong>Situation:</strong> Jenkins ships container images to production and the security team requires defence-in-depth: signing, SBOM, vulnerability scanning, base-image hygiene, and admission policy &mdash; not just &ldquo;Trivy on the side&rdquo;.</p>

<p><strong>Approach:</strong> implement five gates in the Jenkinsfile &mdash; (1) build with a hardened base (Chainguard, distroless, or scratch) using BuildKit, (2) generate SBOM with Syft and store it as a build artefact, (3) scan with Trivy for CVEs and Grype as a second opinion, (4) sign with Cosign keyless via OIDC, (5) attest provenance via SLSA build-level statements. At admission, Kyverno verifies the signature and SBOM against policy.</p>

<pre><code>pipeline {
  agent { kubernetes { yaml podYaml } }   // BuildKit pod with cosign+syft
  options { timestamps() }
  environment {
    REGISTRY = 'harbor.corp/team'
    IMAGE    = "${REGISTRY}/api:${env.GIT_COMMIT.take(7)}"
    COSIGN_EXPERIMENTAL = '1'
  }
  stages {
    stage('Build') {
      steps {
        sh &apos;&apos;&apos;
          buildctl build \
            --frontend dockerfile.v0 \
            --local context=. --local dockerfile=. \
            --opt build-arg:VERSION=$GIT_COMMIT \
            --output type=image,name=$IMAGE,push=true
        &apos;&apos;&apos;
      }
    }
    stage('SBOM') {
      steps { sh 'syft $IMAGE -o spdx-json &gt; sbom.spdx.json' }
      post { always { archiveArtifacts 'sbom.spdx.json' } }
    }
    stage('Scan') {
      parallel {
        stage('Trivy') { steps { sh 'trivy image --severity HIGH,CRITICAL --exit-code 1 $IMAGE' } }
        stage('Grype') { steps { sh 'grype $IMAGE --fail-on high' } }
      }
    }
    stage('Sign &amp; attest') {
      steps {
        sh &apos;&apos;&apos;
          cosign sign --yes $IMAGE
          cosign attest --yes --predicate sbom.spdx.json --type spdxjson $IMAGE
          cosign attest --yes --predicate provenance.json --type slsaprovenance $IMAGE
        &apos;&apos;&apos;
      }
    }
  }
}
</code></pre>

<table>
<tr><th>Practice</th><th>Tool (2026)</th></tr>
<tr><td>Hardened base</td><td>Chainguard Images, distroless, Wolfi</td></tr>
<tr><td>SBOM</td><td>Syft (SPDX or CycloneDX)</td></tr>
<tr><td>Vulnerability scan</td><td>Trivy + Grype, plus registry scan (Harbor, ECR, GAR)</td></tr>
<tr><td>Signing</td><td>Cosign keyless via OIDC + Sigstore Rekor</td></tr>
<tr><td>Provenance</td><td>SLSA Level 3 attestation, GitHub OIDC for build identity</td></tr>
<tr><td>Admission policy</td><td>Kyverno verifyImages, Connaisseur, Gatekeeper</td></tr>
<tr><td>Runtime</td><td>Falco / Tetragon for syscall monitoring</td></tr>
</table>

<p><strong>Trade-offs:</strong> aggressive policy (block on HIGH+CRITICAL) breaks builds frequently and creates pressure to suppress findings; pair scanning with auto-remediation via Renovate to keep dependencies fresh. Keyless Cosign requires Rekor uptime; keyed Cosign needs KMS. Distroless is excellent for production but inconvenient for debugging &mdash; ship a debug variant that includes a shell.</p>

<p><strong>Production polish:</strong> store SBOMs in your registry alongside images via Cosign attestations &mdash; consumers can fetch them with <code>cosign download attestation</code>. Wire Falco or Tetragon at runtime to detect anomalous syscalls and feed alerts to your SIEM. Audit base image age weekly; pin to digests, not tags, in Dockerfiles. Rotate sigstore certificates by re-signing on every build &mdash; ephemeral keys with auditable transparency log entries are the modern best practice.</p>'''

ANSWERS[70] = r'''<p><strong>Situation:</strong> the org needs continuous compliance for Kubernetes &mdash; CIS Benchmarks, NIST 800-190, internal policies (no privileged pods, all images from approved registries, mandatory labels) &mdash; enforced both at PR time and at admission, with evidence for auditors.</p>

<p><strong>Approach:</strong> stack three layers &mdash; (1) static manifest scanning in GitHub Actions before merge, (2) admission control on the cluster, (3) continuous reporting and drift detection. The 2026 leaders are Kyverno (YAML policies, easier than Rego), Gatekeeper (OPA, more flexible), and KubeLinter for static analysis. Layer Kubescape or Trivy K8s for compliance reports.</p>

<pre><code>name: k8s-compliance
on: [pull_request]
jobs:
  manifests:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - name: kubeconform schema check
        run: |
          curl -sL https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz | tar xz
          ./kubeconform -strict -summary -kubernetes-version 1.31.0 k8s/

      - name: kube-linter best practices
        uses: stackrox/kube-linter-action@v1
        with: { directory: k8s/ }

      - name: Kyverno test policies (locally)
        run: |
          curl -sL https://github.com/kyverno/kyverno/releases/latest/download/kyverno-cli_v1.13.0_linux_x86_64.tar.gz | tar xz
          ./kyverno test policies/

      - name: Trivy compliance (CIS K8s)
        uses: aquasecurity/trivy-action@0.27.0
        with:
          scan-type: 'config'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: trivy-results.sarif }

  cluster-evidence:
    runs-on: ubuntu-24.04
    needs: manifests
    steps:
      - uses: azure/setup-kubectl@v4
      - run: |
          kubectl get policies.kyverno.io -A -o json &gt; kyverno-policies.json
          kubectl get policyreports -A -o json &gt; policy-reports.json
          # Upload as compliance evidence to S3 / GCS
</code></pre>

<table>
<tr><th>Layer</th><th>Tool</th></tr>
<tr><td>Schema check</td><td>kubeconform (faster than kubeval)</td></tr>
<tr><td>Static lint</td><td>KubeLinter, Datree</td></tr>
<tr><td>Policy author</td><td>Kyverno (YAML), Gatekeeper (Rego)</td></tr>
<tr><td>Compliance frameworks</td><td>Kubescape (NSA, MITRE, CIS), Trivy K8s</td></tr>
<tr><td>Drift detection</td><td>Argo CD diff, Kyverno reports controller</td></tr>
<tr><td>Pod security</td><td>Pod Security Admission (baseline / restricted)</td></tr>
<tr><td>Network policy</td><td>Cilium with default-deny + L7</td></tr>
</table>

<p><strong>Trade-offs:</strong> Kyverno is far easier to write than Gatekeeper but slightly less expressive; for cross-resource invariants (e.g., &ldquo;every Deployment has a matching ServiceMonitor&rdquo;) Gatekeeper&rsquo;s ConstraintTemplates are more powerful. Audit-only mode is essential during rollout &mdash; turning on enforcement immediately on a busy cluster generates ticket storms.</p>

<p><strong>Production polish:</strong> ship policy reports to a SIEM (Splunk, Elastic, Datadog) so auditors can pull evidence on demand. Use the Kyverno reports controller to expose violations as Prometheus metrics; alert on policy regression. For multi-cluster, push policies via Argo CD ApplicationSets so all clusters share the same baseline. Run Kubescape weekly against every cluster and stash the reports as long-lived artefacts &mdash; auditors love a date-stamped trail. Consider Cluster Compliance Operator (OpenShift) or Polaris for a UI-driven view.</p>'''

ANSWERS[71] = r'''<p><strong>Situation:</strong> an Elixir/Phoenix application needs to run on AWS Lambda. BEAM and Lambda&rsquo;s execution model are awkward together &mdash; Lambda expects per-request handlers, while Phoenix is built around long-lived processes. Two viable paths: package <code>mix release</code> with a custom runtime layer, or front Lambda with API Gateway and run Phoenix inside a container function image.</p>

<p><strong>Approach:</strong> use Lambda container images with the AWS Lambda Runtime Interface Emulator for local testing. Compile a <code>mix release</code> with a custom <code>bootstrap</code> shim that calls Phoenix&rsquo;s endpoint module per invocation. For most production cases, Fly.io or AWS App Runner is a far better fit &mdash; Lambda for Phoenix is a niche choice you should justify explicitly.</p>

<pre><code># Dockerfile (Lambda container image)
FROM hexpm/elixir:1.17.3-erlang-27.1-alpine-3.20 AS build
WORKDIR /app
ENV MIX_ENV=prod
RUN mix local.hex --force &amp;&amp; mix local.rebar --force
COPY mix.* ./
RUN mix deps.get --only prod
COPY config config
RUN mix deps.compile
COPY priv priv
COPY lib lib
RUN mix compile &amp;&amp; mix release

FROM public.ecr.aws/lambda/provided:al2023
COPY --from=build /app/_build/prod/rel/myapp /opt/myapp
COPY bootstrap /var/runtime/bootstrap
RUN chmod +x /var/runtime/bootstrap
CMD ["myapp.handler"]
</code></pre>

<pre><code>name: deploy-phoenix-lambda
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-lambda
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker buildx build --platform linux/arm64 \
            --tag $ECR/phoenix:${{ github.sha }} --push .
      - run: |
          aws lambda update-function-code \
            --function-name phoenix-api \
            --image-uri $ECR/phoenix:${{ github.sha }} \
            --architectures arm64
          aws lambda wait function-updated --function-name phoenix-api
</code></pre>

<table>
<tr><th>Concern</th><th>Reality on Lambda</th></tr>
<tr><td>Cold start</td><td>BEAM startup ~500ms; Provisioned Concurrency required for low-latency APIs</td></tr>
<tr><td>WebSockets / LiveView</td><td>Need API Gateway WebSocket; awkward for Phoenix Channels</td></tr>
<tr><td>Long-running processes</td><td>Lambda timeout 15 min; GenServers reset per cold start</td></tr>
<tr><td>OTP supervision tree</td><td>Restarts inside one invocation only</td></tr>
<tr><td>Database connection pool</td><td>Use RDS Proxy to handle Lambda&rsquo;s connection storms</td></tr>
</table>

<p><strong>Trade-offs:</strong> you lose most of what makes Phoenix special &mdash; LiveView, presence, Channels, distributed Erlang &mdash; if you go to Lambda. The use case where this makes sense is short-lived REST APIs that happen to be in Elixir. For real Phoenix workloads, Fly.io maps almost 1:1 to releases with multi-region distributed Erlang and per-app machines that scale to zero. AWS App Runner (or ECS Fargate) is the next-best fit on AWS.</p>

<p><strong>Production polish:</strong> use Provisioned Concurrency for predictable latency, Lambda SnapStart isn&rsquo;t yet available for custom runtimes. Use RDS Proxy to absorb connection bursts to Postgres. Wire OpenTelemetry Lambda layer to push traces to X-Ray or Tempo. Honestly evaluate Fly.io as an alternative &mdash; if cold start, Channels, or Cluster.distribute matter at all to your app, Lambda is the wrong target.</p>'''

ANSWERS[72] = r'''<p><strong>Situation:</strong> a microservice fleet on Kubernetes deploys via Jenkins. A bad rollout in any service should self-heal &mdash; rollback automatically when health metrics regress, before the on-call notices. The challenge is detecting failure quickly across services without false-positive rollbacks during legitimate deploys.</p>

<p><strong>Approach:</strong> use Argo Rollouts per service with an <em>analysis template</em> that queries Prometheus for error rate and latency, plus a <em>kayenta-style</em> comparison against the baseline. Jenkins triggers the rollout (image bump in Git or direct CRD update), then the in-cluster controller drives the canary and rollback &mdash; Jenkins doesn&rsquo;t make the rollback decision because Jenkins doesn&rsquo;t see real production traffic.</p>

<pre><code>// Jenkinsfile snippet
pipeline {
  agent any
  parameters { string(name: 'SERVICE', defaultValue: 'api') }
  stages {
    stage('Promote') {
      steps {
        sh &apos;&apos;&apos;
          kubectl patch rollout ${SERVICE} -n prod --type='merge' \
            -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","image":"reg/'"${SERVICE}"':'"${GIT_COMMIT}"'"}]}}}}'
        &apos;&apos;&apos;
      }
    }
    stage('Wait') {
      steps {
        sh &apos;&apos;&apos;
          kubectl argo rollouts get rollout ${SERVICE} -n prod --watch --timeout 600s
        &apos;&apos;&apos;
      }
    }
  }
  post {
    failure {
      sh 'kubectl argo rollouts abort ${SERVICE} -n prod'
      slackSend "Rollout aborted for ${SERVICE}; auto-rollback in progress"
    }
  }
}
</code></pre>

<pre><code># AnalysisTemplate the Rollout references at each step
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: success-rate, namespace: prod }
spec:
  args:
    - name: service-name
  metrics:
    - name: error-rate
      interval: 1m
      successCondition: result[0] &lt; 0.01
      failureLimit: 2
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{service=&quot;{{args.service-name}}&quot;,status=~&quot;5..&quot;}[2m]))
            /
            sum(rate(http_requests_total{service=&quot;{{args.service-name}}&quot;}[2m]))
</code></pre>

<table>
<tr><th>Component</th><th>Role</th></tr>
<tr><td>Argo Rollouts</td><td>Owns canary steps and rollback decisions</td></tr>
<tr><td>AnalysisTemplate</td><td>Reusable metric queries (error rate, latency, custom)</td></tr>
<tr><td>Prometheus</td><td>Metric source &mdash; or Datadog/New Relic via provider</td></tr>
<tr><td>Service mesh / Ingress</td><td>Traffic split (Istio, Linkerd, NGINX, ALB)</td></tr>
<tr><td>Jenkins</td><td>Triggers rollout; doesn&rsquo;t decide rollback</td></tr>
<tr><td>Notifier</td><td>Argo Rollouts notifications &rarr; Slack/PagerDuty</td></tr>
</table>

<p><strong>Trade-offs:</strong> letting Jenkins drive rollback (poll <code>kubectl rollout undo</code>) is brittle &mdash; the Jenkins agent might lose connectivity at the worst moment. Argo Rollouts owns this in-cluster, so even if Jenkins crashes, rollback completes. The trade is an extra controller; for a single service this might be overkill, but for 20+ services the consistency is invaluable. Flagger is the Flux-based alternative with similar features.</p>

<p><strong>Production polish:</strong> standardise the AnalysisTemplate across services so every team gets the same SLO-based gate; tune <code>failureLimit</code> per service tier. Wire Argo Rollouts notifications to Slack so the team sees auto-rollback events with reasoning. Keep the previous ReplicaSet warm so rollback is instant (no image pull). For multi-region or multi-cluster, use Kargo to coordinate promotion across stages so a regression in staging blocks production.</p>'''

ANSWERS[73] = r'''<p><strong>Situation:</strong> a Vue.js (Nuxt or plain) SPA needs CI/CD that runs unit tests with Vitest, integration tests with Cypress or Playwright, builds the static bundle, and deploys to Netlify with branch previews and atomic deploys.</p>

<p><strong>Approach:</strong> use GitHub Actions with cached <code>node_modules</code> via pnpm, run Vitest in parallel shards, run Playwright against the dev server, and deploy with <code>netlify-cli</code>. Netlify&rsquo;s GitHub integration handles preview deploys natively, so the workflow exists mainly for testing &mdash; the deploy step is optional if you use Netlify&rsquo;s built-in CI.</p>

<pre><code>name: vue-netlify
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint
      - run: pnpm run typecheck
      - name: Unit tests
        run: pnpm run test --shard=${{ matrix.shard }}/4
        strategy:
          matrix: { shard: [1, 2, 3, 4] }
      - uses: codecov/codecov-action@v4

  e2e:
    needs: test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps chromium
      - run: pnpm run build
      - run: pnpm exec playwright test

  deploy:
    needs: e2e
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm run build
      - uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=dist --message "${{ github.sha }}"
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID:    ${{ secrets.NETLIFY_SITE_ID }}
</code></pre>

<table>
<tr><th>Concern</th><th>2026 default</th></tr>
<tr><td>Test runner</td><td>Vitest (faster, Vite-native)</td></tr>
<tr><td>E2E</td><td>Playwright (cross-browser, native parallelism)</td></tr>
<tr><td>Package manager</td><td>pnpm with workspace support</td></tr>
<tr><td>Bundler</td><td>Vite (default for Vue 3)</td></tr>
<tr><td>SSR option</td><td>Nuxt 3 with Nitro adapters per host</td></tr>
<tr><td>Deploy target</td><td>Netlify, Vercel, Cloudflare Pages, Bunny Edge</td></tr>
</table>

<p><strong>Trade-offs:</strong> running deploys from GitHub Actions instead of Netlify&rsquo;s built-in CI gives you full control (matrix tests, parallel jobs) but loses some Netlify niceties (deploy previews on PR comments, build caching). For most teams the built-in CI plus a separate Actions workflow for tests is simpler than reproducing Netlify&rsquo;s deploy behaviour in Actions. Cloudflare Pages and Vercel offer comparable DX with often-cheaper egress.</p>

<p><strong>Production polish:</strong> enable Netlify split testing for canary releases via traffic split. Use Netlify Edge Functions for personalisation without a backend. Configure Lighthouse CI with budgets to fail PRs that regress Core Web Vitals; add bundle-size guards via <code>size-limit</code>. For Nuxt SSR, deploy to Cloudflare Workers via Nitro for global edge serving with sub-50ms latency. Pre-warm Playwright browsers via <code>actions/cache</code> on <code>~/.cache/ms-playwright</code> to cut E2E startup time in half.</p>'''

ANSWERS[74] = r'''<p><strong>Situation:</strong> a blockchain application (smart contracts plus an off-chain indexer/API) needs CI/CD that compiles and tests Solidity contracts, runs static analysis and fuzzing, deploys to a testnet for verification, and ships the off-chain components to AWS via GitHub Actions.</p>

<p><strong>Approach:</strong> separate the on-chain and off-chain pipelines &mdash; contracts have different review cadence and immutability constraints than services. For Solidity in 2026 the toolchain is Foundry (forge build/test/script with fuzzing and invariants), Slither and Aderyn for SAST, and optionally Halmos or Certora for symbolic execution. Off-chain components ship as containers via OIDC to ECR, deployed to ECS or EKS through standard pipelines.</p>

<pre><code>name: blockchain
on: [pull_request]
jobs:
  contracts:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: foundry-rs/foundry-toolchain@v1
      - run: forge build --sizes
      - run: forge test -vvv --gas-report
      - run: forge fmt --check
      - name: Slither
        uses: crytic/slither-action@v0.4.0
      - name: Coverage
        run: forge coverage --report lcov &amp;&amp; lcov --remove lcov.info "test/*" -o lcov.info
      - uses: codecov/codecov-action@v4
      - name: Halmos symbolic exec
        run: pip install halmos &amp;&amp; halmos
      - name: Mythril
        run: docker run -v $PWD:/src mythril/myth analyze /src/contracts/Vault.sol --solv 0.8.28

  testnet-deploy:
    needs: contracts
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: foundry-rs/foundry-toolchain@v1
      - run: |
          forge script script/Deploy.s.sol \
            --rpc-url ${{ secrets.SEPOLIA_RPC }} \
            --private-key ${{ secrets.DEPLOYER_KEY }} \
            --broadcast --verify \
            --etherscan-api-key ${{ secrets.ETHERSCAN_KEY }}

  indexer-deploy:
    needs: contracts
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-blockchain
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker buildx build --platform linux/arm64 \
            -t $ECR/indexer:${{ github.sha }} --push ./indexer
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2
</code></pre>

<table>
<tr><th>Layer</th><th>Tool (2026)</th></tr>
<tr><td>Contract build/test</td><td>Foundry (forge)</td></tr>
<tr><td>Static analysis</td><td>Slither, Aderyn, Wake</td></tr>
<tr><td>Symbolic / formal</td><td>Halmos, Certora, Kontrol</td></tr>
<tr><td>Indexer</td><td>The Graph, Subsquid, Goldsky</td></tr>
<tr><td>Storage</td><td>Helia (IPFS) for metadata, Arweave for permanence</td></tr>
<tr><td>Deployment management</td><td>OpenZeppelin Defender</td></tr>
<tr><td>Hardware key signing</td><td>Frame, Fireblocks, AWS KMS for raw signing</td></tr>
</table>

<p><strong>Trade-offs:</strong> mainnet deploys must never auto-deploy &mdash; gate behind manual approval and a hardware-key signing flow (Defender, Fireblocks). Foundry has eclipsed Hardhat for serious development; Hardhat remains useful for TypeScript-heavy testing. Symbolic execution (Halmos, Certora) is slow but catches bugs unit tests never will; budget for it on critical paths.</p>

<p><strong>Production polish:</strong> sign every artefact (contracts and indexer images) with Cosign and store SBOMs in a transparent log. Use OpenZeppelin Defender for safe upgradeable proxies and timelocked admin actions. Rate-limit the indexer&rsquo;s RPC calls via dedicated nodes (Alchemy, Infura, QuickNode) with separate API keys per environment. Always run a full mainnet fork test in CI before any deploy &mdash; integration regressions hide in real on-chain state.</p>'''

ANSWERS[75] = r'''<p><strong>Situation:</strong> an IoT product has thousands of devices in the field and needs CI/CD that builds firmware-equivalent containers, signs them, and ships to edge sites running K3s or KubeEdge, plus a cloud-side data ingest pipeline. Bandwidth is constrained, devices may be offline, and rollback must work without an operator visiting the site.</p>

<p><strong>Approach:</strong> hub-and-spoke architecture &mdash; build and sign in cloud CI (GitHub Actions), publish to a global registry with edge mirrors, and let each edge site pull via GitOps. Use K3s (or MicroK8s) for the edge runtime with KubeEdge or OpenYurt for offline tolerance. Akri exposes IoT hardware as K8s resources. SOCI image streaming reduces cold-pull time on slow links.</p>

<pre><code>name: iot-edge-deploy
on: { push: { branches: [main], paths: ['edge/**'] } }
permissions: { id-token: write, contents: write, packages: write }
jobs:
  build:
    runs-on: ubuntu-24.04-arm   # arm64 native, faster than emulation
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          context: edge/sensor-collector
          tags: ghcr.io/org/sensor-collector:${{ github.sha }}
          platforms: linux/arm64,linux/arm/v7
          push: true
          provenance: true
          sbom: true
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Sign
        uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/org/sensor-collector:${{ github.sha }}

      - name: Bump manifest
        run: |
          cd manifests/edge
          kustomize edit set image sensor-collector=ghcr.io/org/sensor-collector:${{ github.sha }}
          git config user.email ci@x &amp;&amp; git config user.name ci
          git commit -am "edge sensor ${{ github.sha }}"
          git push

  # Each edge site runs Flux pulling from Git; no push needed
</code></pre>

<table>
<tr><th>Layer</th><th>Tool (2026)</th></tr>
<tr><td>Edge K8s</td><td>K3s, MicroK8s, k0s</td></tr>
<tr><td>Edge OS</td><td>Talos, Flatcar, Bottlerocket OS, Ubuntu Core</td></tr>
<tr><td>Offline tolerance</td><td>KubeEdge, OpenYurt, Rancher Fleet</td></tr>
<tr><td>Hardware abstraction</td><td>Akri (USB cameras, ONVIF, OPC UA)</td></tr>
<tr><td>Image streaming</td><td>SOCI Snapshotter, eStargz</td></tr>
<tr><td>Messaging</td><td>MQTT (Mosquitto, EMQX), Eclipse zenoh</td></tr>
<tr><td>Vendor stacks</td><td>AWS Greengrass, Azure IoT Edge, Google Distributed Cloud Edge</td></tr>
</table>

<p><strong>Trade-offs:</strong> push-based deploy from CI to thousands of edges is fragile &mdash; pull-based GitOps with Flux or Rancher Fleet is the correct primitive. Image size matters far more than at cloud scale; use distroless or chiseled bases and ship arm64-native (RPi, Jetson) rather than emulating amd64. Without SOCI, a 200 MB image over a 4G link is a 5-minute outage. KubeEdge is great for offline but adds operational complexity; many shops use plain Flux with longer reconcile windows instead.</p>

<p><strong>Production polish:</strong> stagger rollouts heavily &mdash; never push the same image to all sites simultaneously. Use Flux <code>ImagePolicy</code> with <code>ImageRepository</code> for deterministic version progression and Rancher Fleet&rsquo;s <code>maxUnavailable</code> for fleet-wide control. Ingest device telemetry via OpenTelemetry Collector at the edge, batched to cloud Prometheus or Tempo. For firmware-style updates (where containers aren&rsquo;t enough), pair with Mender or RAUC. Always design for offline: edge clusters must reconcile from a known state and never trust partial syncs.</p>'''

ANSWERS[76] = r'''<p><strong>Situation:</strong> a mobile app (iOS Swift, Android Kotlin, or React Native/Flutter cross-platform) needs CI checks for code quality and security. Mobile adds platform-specific concerns &mdash; SAST for Swift/Kotlin, supply chain via CocoaPods/Gradle, secrets in <code>Info.plist</code> or <code>AndroidManifest.xml</code>, and obfuscation/anti-tamper requirements.</p>

<p><strong>Approach:</strong> stack five gates in GitHub Actions &mdash; (1) static analysis (SwiftLint + SwiftFormat for iOS, ktlint + Detekt for Android), (2) dependency scanning (CocoaPods Audit, Gradle dependency-check, Renovate for updates), (3) SAST (Semgrep with mobile rulesets, MobSF for binary analysis), (4) secret scanning (gitleaks), (5) IPA/APK signing verification. Use macOS runners for iOS (Apple silicon now standard) and Linux for Android.</p>

<pre><code>name: mobile-quality
on: [pull_request]
jobs:
  ios:
    runs-on: macos-15-large   # M-series Apple silicon
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with: { path: Pods, key: pods-${{ hashFiles('Podfile.lock') }} }
      - run: brew install swiftlint swiftformat
      - run: swiftlint --strict
      - run: swiftformat --lint .
      - name: Semgrep mobile
        uses: returntocorp/semgrep-action@v1
        with: { config: 'p/swift p/mobile' }
      - run: pod install
      - run: |
          xcodebuild -workspace App.xcworkspace -scheme App \
            -destination 'platform=iOS Simulator,name=iPhone 16' \
            -resultBundlePath TestResults clean test \
            CODE_SIGNING_ALLOWED=NO

  android:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 21 }
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew ktlintCheck detekt
      - run: ./gradlew dependencyCheckAggregate
      - run: ./gradlew testDebugUnitTest
      - name: MobSF binary scan
        run: |
          ./gradlew assembleDebug
          docker run -v $PWD:/data opensecurity/mobsf:latest \
            python -c "from mobsf.MobSF.cli_scan import scan; scan('/data/app/build/outputs/apk/debug/app-debug.apk')"

  shared:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2
      - uses: github/codeql-action/init@v3
        with: { languages: 'java,javascript' }
      - uses: github/codeql-action/analyze@v3
</code></pre>

<table>
<tr><th>Concern</th><th>Tool</th></tr>
<tr><td>iOS lint</td><td>SwiftLint, SwiftFormat</td></tr>
<tr><td>Android lint</td><td>ktlint, Detekt, Android Lint</td></tr>
<tr><td>SAST</td><td>Semgrep, MobSF, CodeQL</td></tr>
<tr><td>SCA (deps)</td><td>OWASP DC, Renovate, Snyk</td></tr>
<tr><td>Binary scan</td><td>MobSF on IPA/APK</td></tr>
<tr><td>Secret scan</td><td>gitleaks, trufflehog</td></tr>
<tr><td>Distribution</td><td>Fastlane (iOS) + Gradle Play Publisher</td></tr>
<tr><td>Mac CI alternatives</td><td>Xcode Cloud (Apple), MacStadium, Bitrise</td></tr>
</table>

<p><strong>Trade-offs:</strong> macOS runners on GitHub-hosted are pricey (10x Linux); for high-volume iOS, self-hosted Apple silicon Macs or Xcode Cloud may pay back. MobSF is brilliant but slow &mdash; run it nightly rather than per-PR. SAST tools can be noisy on mobile-specific patterns; tune rulesets aggressively to keep false positives manageable.</p>

<p><strong>Production polish:</strong> require code-signing on every build with Match (Fastlane) for shared signing identity. Use App Store Connect API keys (not Apple ID passwords) for upload &mdash; rotate quarterly. Layer Crashlytics and OpenTelemetry for runtime observability. For React Native or Flutter cross-platform, run unit tests once on Linux and reserve macOS runners for iOS-specific build/test only &mdash; significant cost savings. Add ProGuard/R8 (Android) and Strip (iOS) for code shrinking and basic obfuscation.</p>'''

ANSWERS[77] = r'''<p><strong>Situation:</strong> an Angular SPA (likely Angular 18+ with standalone components and signals) needs CI/CD that runs Karma/Jest unit tests, Cypress or Playwright E2E, and deploys to AWS Amplify Hosting with branch-aware preview deployments and atomic releases.</p>

<p><strong>Approach:</strong> Amplify Hosting handles build and deploy natively when wired to GitHub via <code>amplify.yml</code>; you can leave the entire pipeline to Amplify or use GitHub Actions for richer testing and let Amplify pull pre-built artefacts. The hybrid pattern &mdash; tests in Actions, deploy in Amplify &mdash; is the most common in 2026.</p>

<pre><code>name: angular-amplify
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npx ng test --watch=false --browsers=ChromeHeadless --code-coverage
      - uses: codecov/codecov-action@v4
        with: { files: coverage/lcov.info }
      - run: npx ng build --configuration production

  e2e:
    needs: test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx ng e2e --port 4201

  deploy:
    needs: e2e
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions: { id-token: write, contents: read }
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-amplify
          aws-region: ap-south-1
      - run: |
          aws amplify start-job \
            --app-id ${{ secrets.AMPLIFY_APP_ID }} \
            --branch-name main \
            --job-type RELEASE
</code></pre>

<pre><code># amplify.yml (lives in repo root)
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npx ng build --configuration production
  artifacts:
    baseDirectory: dist/app/browser
    files: ['**/*']
  cache:
    paths: ['node_modules/**/*']
</code></pre>

<table>
<tr><th>Choice</th><th>Detail</th></tr>
<tr><td>Build target</td><td>Angular 18+ Vite (esbuild-based) for faster builds</td></tr>
<tr><td>SSR option</td><td>Angular Universal via Amplify SSR or AWS Lambda@Edge</td></tr>
<tr><td>Preview branches</td><td>Amplify auto-creates per-PR preview URL</td></tr>
<tr><td>Custom domain + TLS</td><td>Managed via Route 53; Amplify provisions ACM cert</td></tr>
<tr><td>Atomic deploys</td><td>Amplify ships per-job; failed jobs don&rsquo;t serve</td></tr>
<tr><td>Alternative hosts</td><td>CloudFront + S3, Vercel, Cloudflare Pages, Netlify</td></tr>
</table>

<p><strong>Trade-offs:</strong> Amplify Hosting is convenient but slightly opinionated &mdash; very custom build setups (server-side rendering with custom edge logic, mixed monorepos) sometimes outgrow it. CloudFront + S3 with a custom GitHub Actions deploy gives identical performance with more control but more wiring. Amplify&rsquo;s pricing per build minute can stack up on large repos &mdash; offload tests to Actions to avoid double-billing.</p>

<p><strong>Production polish:</strong> enable Amplify&rsquo;s rewrite rules for SPA routing (<code>404 -&gt; /index.html</code>). Configure Lighthouse CI against the Amplify preview URL on every PR &mdash; perf regressions get blocked before merge. Use Amplify environment variables tied to branch (staging vs prod API URLs). For SSR, evaluate Vercel or Cloudflare Pages with Pages Functions; Amplify SSR works but has rougher edges than dedicated SSR hosts. Pair with WAF and Bot Control if the app is consumer-facing.</p>'''

ANSWERS[78] = r'''<p><strong>Situation:</strong> the team trains ML models offline (or fine-tunes LLMs) and wants to deploy them to AKS with proper versioning, rollback, GPU scheduling, and monitoring. The pipeline must handle model artefacts (large files in registries) and serve them with autoscaling under bursty traffic.</p>

<p><strong>Approach:</strong> separate the artefact pipeline (model in MLflow or Hugging Face Hub) from the service pipeline (KServe InferenceService manifest). GitHub Actions builds the inference container, packages the model reference, then bumps the InferenceService manifest in a GitOps repo &mdash; Argo CD deploys to AKS. KServe handles autoscaling (scale-to-zero, GPU sharing) and provides a standard prediction protocol.</p>

<pre><code>name: ml-aks
on:
  push: { branches: [main], paths: ['serving/**', 'manifests/**'] }
permissions: { id-token: write, contents: write }
jobs:
  build-server:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUB_ID }}
      - uses: azure/docker-login@v2
        with: { login-server: ${{ secrets.ACR }} }
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          context: serving
          tags: ${{ secrets.ACR }}/llm-server:${{ github.sha }}
          push: true
          provenance: true
          sbom: true

  bump-manifest:
    needs: build-server
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          cd manifests/serving
          yq -i '.spec.predictor.containers[0].image = "${{ secrets.ACR }}/llm-server:${{ github.sha }}"' isvc.yaml
          git config user.email ci@x
          git config user.name  ci
          git commit -am "bump server to ${{ github.sha }}"
          git push
</code></pre>

<pre><code># InferenceService for KServe
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata: { name: llm, namespace: ml }
spec:
  predictor:
    minReplicas: 0
    maxReplicas: 10
    scaleTarget: 80
    scaleMetric: concurrency
    nodeSelector: { nvidia.com/gpu.product: NVIDIA-H100 }
    tolerations: [{ key: nvidia.com/gpu, operator: Exists }]
    containers:
      - name: kserve-container
        image: <FROM CI>
        resources:
          requests: { cpu: '4', memory: 16Gi, nvidia.com/gpu: '1' }
          limits:   { cpu: '8', memory: 32Gi, nvidia.com/gpu: '1' }
        env:
          - name: MODEL_URI
            value: hf://meta-llama/Llama-3.3-70B-Instruct
</code></pre>

<table>
<tr><th>Concern</th><th>Tool (2026)</th></tr>
<tr><td>Inference framework</td><td>KServe, Seldon Core v2, BentoML, Ray Serve</td></tr>
<tr><td>LLM serving</td><td>vLLM, TensorRT-LLM, Hugging Face TGI</td></tr>
<tr><td>Model registry</td><td>MLflow, Hugging Face Hub, S3/Azure Blob</td></tr>
<tr><td>GPU scheduling</td><td>NVIDIA GPU Operator + Volcano/KAI scheduler</td></tr>
<tr><td>Autoscaling</td><td>Knative (KServe default), KEDA on queue depth</td></tr>
<tr><td>Drift detection</td><td>Evidently AI, NannyML, Arize, WhyLabs</td></tr>
<tr><td>Tracing</td><td>OpenTelemetry + Tempo/Jaeger</td></tr>
</table>

<p><strong>Trade-offs:</strong> KServe&rsquo;s scale-to-zero saves cost but has cold-start cost (model load can be minutes for large LLMs) &mdash; for low-latency consumer apps keep <code>minReplicas: 1</code>. AKS spot node pools dramatically cut GPU cost but eviction is brutal mid-inference; use them for batch/training, not online serving. NVIDIA H100/A100 capacity is constrained &mdash; reserve quota in advance and consider AMD MI300X as the 2026 alternative.</p>

<p><strong>Production polish:</strong> instrument with OpenTelemetry to capture token-level latency and KV-cache hit rate. Layer drift detection via Evidently AI on prediction distribution; alert when drift exceeds a baseline. Use vLLM or TensorRT-LLM for throughput &mdash; raw HuggingFace pipelines are 5-10x slower. For multi-model serving, consider Triton with concurrent model execution. Always shadow-deploy new model versions before flipping traffic; ML changes that look fine in offline eval can regress in production distribution.</p>'''

ANSWERS[79] = r'''<p><strong>Situation:</strong> a Perl service needs to ship to Google Cloud Functions with unit and integration tests. Cloud Functions doesn&rsquo;t natively support Perl, so the only viable path in 2026 is the second-generation runtime (Cloud Run-backed) with a custom container image &mdash; effectively running Cloud Run with Functions-Framework semantics layered on top.</p>

<p><strong>Approach:</strong> use Plack/Starman or Mojolicious as the HTTP layer, package as a container with the Functions-Framework HTTP contract (listen on <code>$PORT</code>, plain HTTP), and deploy via gen2 Functions or directly to Cloud Run. Test in CI with <code>prove</code> for unit tests and Test::Mojo or <code>plackup</code> + curl for integration tests; coverage via Devel::Cover.</p>

<pre><code># Dockerfile
FROM perl:5.40-slim
WORKDIR /app
RUN apt-get update &amp;&amp; apt-get install -y --no-install-recommends build-essential \
    &amp;&amp; rm -rf /var/lib/apt/lists/*
COPY cpanfile cpanfile.snapshot ./
RUN cpanm --installdeps --notest .
COPY . .
ENV PORT=8080
CMD ["starman", "--port", "8080", "--workers", "4", "app.psgi"]
</code></pre>

<pre><code>name: perl-cf
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    container: perl:5.40
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with: { path: ~/perl5, key: cpanm-${{ hashFiles('cpanfile.snapshot') }} }
      - run: cpanm --installdeps --notest .
      - run: prove -lvr t/
      - name: Coverage
        run: cover -test -report codecov
      - uses: codecov/codecov-action@v4
      - name: Lint
        run: perlcritic --severity 4 lib/

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF }}
          service_account: gha@proj.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker asia-south1-docker.pkg.dev
      - uses: docker/build-push-action@v5
        with:
          tags: asia-south1-docker.pkg.dev/proj/repo/perl-fn:${{ github.sha }}
          push: true
      - run: |
          gcloud run deploy perl-fn \
            --image asia-south1-docker.pkg.dev/proj/repo/perl-fn:${{ github.sha }} \
            --region asia-south1 --allow-unauthenticated \
            --memory 512Mi --cpu 1 --concurrency 80
</code></pre>

<table>
<tr><th>Choice</th><th>Detail</th></tr>
<tr><td>HTTP framework</td><td>Plack + Starman, or Mojolicious::Lite</td></tr>
<tr><td>Test framework</td><td>Test::More, Test::Mojo, Test::Most</td></tr>
<tr><td>Lint</td><td>Perl::Critic, Perl::Tidy</td></tr>
<tr><td>Deploy target</td><td>Cloud Run (gen2 Functions wraps Cloud Run anyway)</td></tr>
<tr><td>Concurrency</td><td>Starman workers + Cloud Run concurrency setting</td></tr>
<tr><td>Cold start</td><td>Larger than Go/Rust; consider <code>min-instances</code> setting</td></tr>
</table>

<p><strong>Trade-offs:</strong> Perl is a niche choice for greenfield serverless and not officially supported &mdash; expect to maintain the runtime image yourself. The Functions-Framework HTTP contract is straightforward, so practically any language that speaks HTTP works on gen2. Cold start is meaningful (Perl startup + module load); pay for <code>min-instances: 1</code> if latency matters.</p>

<p><strong>Production polish:</strong> use Carton or cpanfile.snapshot for reproducible dependency installs &mdash; Perl&rsquo;s <code>cpanm</code> without a snapshot can pull different versions per build. Layer OpenTelemetry::SDK for traces (instrumentation is lightweight but needs manual wiring). Cache CPAN modules in a separate base image rebuilt weekly; the bulk of build time is dependency resolution. Honestly evaluate whether a Perl rewrite to Go or Python would be cheaper than maintaining a custom Perl serverless runtime &mdash; for most teams it would be.</p>'''

ANSWERS[80] = r'''<p><strong>Situation:</strong> a Dart application (likely a Flutter mobile app or a server-side Dart binary) needs CI with dependency caching to keep <code>dart pub get</code> and Flutter tool downloads off the critical path. Without caching every PR re-fetches the SDK and pub packages, adding 60&ndash;90 seconds per job.</p>

<p><strong>Approach:</strong> cache three things &mdash; the Flutter/Dart SDK install (heavy, ~1GB), the pub-cache directory (<code>~/.pub-cache</code>), and the per-project <code>.dart_tool</code> build cache. The <code>subosito/flutter-action</code> handles SDK caching automatically; pub and build caches need explicit <code>actions/cache</code> entries keyed on <code>pubspec.lock</code> and <code>pubspec.yaml</code>.</p>

<pre><code>name: dart-ci
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          channel: stable
          flutter-version: 3.27.0
          cache: true   # caches the SDK install

      - name: Cache pub
        uses: actions/cache@v4
        with:
          path: |
            ~/.pub-cache
            .dart_tool
          key: pub-${{ runner.os }}-${{ hashFiles('**/pubspec.lock') }}
          restore-keys: |
            pub-${{ runner.os }}-

      - run: flutter pub get
      - run: dart format --output=none --set-exit-if-changed .
      - run: dart analyze --fatal-infos
      - run: flutter test --coverage
      - uses: codecov/codecov-action@v4
        with: { files: coverage/lcov.info }

      - name: Build APK (release)
        if: github.ref == 'refs/heads/main'
        run: flutter build apk --release --split-per-abi

      - name: Build iOS (no codesign)
        if: github.ref == 'refs/heads/main'
        runs-on: macos-15
        run: flutter build ios --release --no-codesign
</code></pre>

<table>
<tr><th>Cache</th><th>What it skips</th></tr>
<tr><td>Flutter SDK</td><td>~1 GB SDK download; biggest single saving</td></tr>
<tr><td>~/.pub-cache</td><td>Dependency tarballs from pub.dev</td></tr>
<tr><td>.dart_tool/</td><td>Per-project resolved package config + build artefacts</td></tr>
<tr><td>~/.gradle/caches (Android)</td><td>Gradle dep cache for Android builds</td></tr>
<tr><td>~/Library/Developer/Xcode/DerivedData (iOS)</td><td>Xcode build cache for iOS</td></tr>
</table>

<p><strong>Trade-offs:</strong> aggressive caching can mask issues &mdash; a build that works in CI may break for new contributors who do clean checkouts. Run a weekly &ldquo;clean-cache&rdquo; job that wipes caches and rebuilds from scratch to catch this early. Cache size on GHA is 10GB per repo branch; large Flutter projects with both iOS and Android caches can exceed this &mdash; consider self-hosted runners or BuildKit registry caching for monorepos.</p>

<p><strong>Production polish:</strong> use <code>flutter pub get --enforce-lockfile</code> in CI to fail on lockfile drift. Run <code>dart pub deps</code> against an allow-list to catch unauthorised dependencies. For Android release builds, configure ProGuard/R8 with shrinking and obfuscation; for iOS, use Match (Fastlane) for shared signing identity. Consider Codemagic or Bitrise for mobile-specific CI &mdash; they handle Apple silicon, signing, and store uploads more elegantly than DIY GitHub Actions, especially for Flutter where you build for two platforms simultaneously.</p>'''

ANSWERS[81] = r'''<p><strong>Situation:</strong> the security team requires hardened Kubernetes clusters with continuous evidence: every cluster passes CIS benchmarks, runs only signed images, denies privileged pods by default, and exports compliance reports for auditors &mdash; all enforced and validated through GitHub Actions before merges hit production.</p>

<p><strong>Approach:</strong> three-layer defence &mdash; (1) IaC scan for cluster bootstrap (Terraform/CDKTF) via Checkov and tfsec, (2) manifest-time policy via Kyverno test in PRs, (3) admission-time enforcement via Kyverno or Gatekeeper plus Pod Security Admission baseline/restricted. Run kube-bench against each cluster nightly and ship results to the SIEM.</p>

<pre><code>name: k8s-security
on: [pull_request, schedule]
permissions: { id-token: write, contents: read, security-events: write }
jobs:
  iac:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@v12
        with: { framework: terraform, output_format: sarif }
      - uses: aquasecurity/tfsec-sarif-action@v0.1.4
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: results.sarif }

  manifests:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Kyverno test policies
        run: |
          curl -sL https://github.com/kyverno/kyverno/releases/latest/download/kyverno-cli_v1.13.0_linux_x86_64.tar.gz | tar xz
          ./kyverno test policies/

      - name: Trivy K8s scan
        uses: aquasecurity/trivy-action@0.27.0
        with:
          scan-type: 'config'
          severity: 'CRITICAL,HIGH'
          format: 'sarif'
          output: 'trivy.sarif'
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: trivy.sarif }

  cluster-evidence:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-24.04
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-eks
          aws-region: ap-south-1
      - run: aws eks update-kubeconfig --name prod
      - name: kube-bench
        run: |
          kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job-eks.yaml
          kubectl wait --for=condition=complete job/kube-bench --timeout=10m
          kubectl logs job/kube-bench &gt; kube-bench.txt
      - name: Kubescape NSA framework
        run: |
          curl -sLO https://github.com/kubescape/kubescape/releases/latest/download/kubescape-ubuntu-latest
          chmod +x kubescape-ubuntu-latest
          ./kubescape-ubuntu-latest scan framework nsa --output sarif --output-file kubescape.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: kubescape.sarif }
</code></pre>

<table>
<tr><th>Layer</th><th>Tool</th></tr>
<tr><td>IaC scan</td><td>Checkov, tfsec, KICS</td></tr>
<tr><td>Manifest policy</td><td>Kyverno (YAML), Gatekeeper (Rego)</td></tr>
<tr><td>Pod security</td><td>Pod Security Admission (baseline/restricted)</td></tr>
<tr><td>Image signing</td><td>Cosign + Kyverno verifyImages</td></tr>
<tr><td>Network</td><td>Cilium NetworkPolicy default-deny + L7 + FQDN</td></tr>
<tr><td>Runtime</td><td>Falco, Tetragon for syscall observability</td></tr>
<tr><td>CIS bench</td><td>kube-bench scheduled CronJob</td></tr>
<tr><td>Compliance frameworks</td><td>Kubescape (NSA, MITRE, CIS)</td></tr>
</table>

<p><strong>Trade-offs:</strong> turning on Pod Security Admission &ldquo;restricted&rdquo; on a brownfield cluster breaks workloads that ran as root or required hostPath volumes &mdash; phased rollout with audit-only mode first is essential. Kyverno is easier to author but has fewer cross-resource invariants than Gatekeeper. Falco generates significant volume; tune rules and pipe through a SIEM to avoid alert fatigue.</p>

<p><strong>Production polish:</strong> stitch results into a single dashboard via SARIF upload to GitHub Code Scanning &mdash; auditors get a per-PR security view. Schedule kube-bench and Kubescape nightly across every cluster and archive reports to S3 or GCS with object-lock for audit trails. For multi-cluster fleets, push policies via Argo CD ApplicationSets so the baseline is identical everywhere. Layer Cilium Tetragon for kernel-level observability and runtime enforcement; it catches things admission control alone cannot.</p>'''

ANSWERS[82] = r'''<p><strong>Situation:</strong> serverless deploys (Lambda, Cloud Functions, Azure Functions) skip the OS layer but still need compliance &mdash; least-privilege IAM, encrypted env vars, scoped triggers, no over-permissioned roles, no plaintext secrets, no internet egress unless required. The goal: enforce these in Jenkins before deploy, with evidence stored centrally.</p>

<p><strong>Approach:</strong> Jenkinsfile gates four checks before the deploy stage &mdash; (1) IaC scan via Checkov on SAM/Serverless Framework/CDK templates, (2) IAM policy review via cfn-lint custom rules and IAM Access Analyzer, (3) function-level SAST via Semgrep with serverless rules, (4) secret scan via gitleaks. After deploy, an AWS Config or Azure Policy rule continuously verifies drift.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent { kubernetes { yaml podYaml } }
  stages {
    stage('Checkov IaC') {
      steps {
        sh 'checkov -d . --framework serverless,cloudformation --output sarif --output-file-path checkov.sarif'
      }
    }
    stage('cfn-lint + IAM Access Analyzer') {
      steps {
        sh 'cfn-lint template.yaml'
        sh &apos;&apos;&apos;
          aws accessanalyzer validate-policy \
            --policy-document file://iam.json \
            --policy-type IDENTITY_POLICY
        &apos;&apos;&apos;
      }
    }
    stage('SAST Semgrep') {
      steps {
        sh 'semgrep --config p/serverless --config p/owasp-top-ten --error src/'
      }
    }
    stage('Secret scan gitleaks') {
      steps { sh 'gitleaks detect --source . --redact --verbose' }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        withAWS(role: 'arn:aws:iam::123:role/jenkins-deploy', region: 'ap-south-1') {
          sh 'sam build --use-container'
          sh 'sam deploy --no-fail-on-empty-changeset --no-confirm-changeset --capabilities CAPABILITY_IAM'
        }
      }
    }
    stage('Post-deploy compliance') {
      steps {
        sh &apos;&apos;&apos;
          aws config get-compliance-details-by-resource \
            --resource-type AWS::Lambda::Function \
            --resource-id my-fn &gt; compliance.json
        &apos;&apos;&apos;
        archiveArtifacts 'compliance.json'
      }
    }
  }
}
</code></pre>

<table>
<tr><th>Concern</th><th>Tool</th></tr>
<tr><td>IaC scan</td><td>Checkov, cfn-nag, KICS</td></tr>
<tr><td>IAM analysis</td><td>IAM Access Analyzer, parliament, iamlive</td></tr>
<tr><td>SAST</td><td>Semgrep (serverless rules), CodeQL</td></tr>
<tr><td>Secret detection</td><td>gitleaks, trufflehog</td></tr>
<tr><td>Runtime</td><td>AWS Config rules, Azure Policy, Cloud Asset Inventory</td></tr>
<tr><td>Encryption</td><td>KMS for env vars, customer-managed keys for at-rest</td></tr>
<tr><td>Image scanning</td><td>Trivy on container images for image-based functions</td></tr>
<tr><td>Powertools</td><td>AWS Lambda Powertools (idempotency, tracing, parameters)</td></tr>
</table>

<p><strong>Trade-offs:</strong> blocking builds on every Checkov finding generates pressure to suppress; pair with a triage workflow that classifies findings by severity. IAM Access Analyzer&rsquo;s validate-policy is gold for catching wildcard actions before deploy &mdash; surprisingly many production policies fail the basic check. Semgrep&rsquo;s serverless ruleset misses some platform-specific concerns; complement with custom rules for your patterns.</p>

<p><strong>Production polish:</strong> store SARIF outputs in S3 or GCS with object-lock for audit retention. Use AWS Config conformance packs (or Azure Policy initiatives) for continuous evaluation; alert via SNS/EventBridge on drift. Wire Lambda Powertools idempotency to avoid duplicate side effects on retries. For very strict environments use AWS GovCloud + STIG-hardened AMIs for self-hosted Jenkins; for less strict, the standard AWS region with VPC endpoints is fine. Always rotate Jenkins-to-AWS roles with short-lived OIDC tokens, never static keys.</p>'''

ANSWERS[83] = r'''<p><strong>Situation:</strong> a Rust service (Actix Web, Axum, or Rocket) needs CI/CD with cargo-based unit and integration tests and deployment to AWS Lambda. Rust is excellent on Lambda &mdash; tiny cold starts, low memory, and the <code>provided.al2023</code> custom runtime is straightforward via <code>cargo lambda</code>.</p>

<p><strong>Approach:</strong> use <code>cargo lambda</code> (the maintained tool replacing older <code>aws-lambda-rust-runtime</code> manual setups) for build/test/deploy, run cargo nextest for parallel test execution, cache <code>~/.cargo</code> and <code>target/</code> aggressively, and deploy via OIDC. Build for arm64 (Graviton) by default &mdash; ~25% cost savings with no compatibility issues.</p>

<pre><code>name: rust-lambda
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with: { components: rustfmt, clippy }
      - uses: Swatinem/rust-cache@v2
      - run: cargo fmt --all -- --check
      - run: cargo clippy --all-targets --all-features -- -D warnings
      - uses: taiki-e/install-action@nextest
      - run: cargo nextest run --all-features
      - name: Coverage
        run: cargo install cargo-llvm-cov &amp;&amp; cargo llvm-cov nextest --lcov --output-path lcov.info
      - uses: codecov/codecov-action@v4
        with: { files: lcov.info }
      - name: cargo-audit
        run: cargo install cargo-audit &amp;&amp; cargo audit
      - name: cargo-deny
        uses: EmbarkStudios/cargo-deny-action@v2

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04-arm   # arm64 native; faster than x86 + cross
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo install cargo-lambda
      - run: cargo lambda build --release --arm64
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-rust-lambda
          aws-region: ap-south-1
      - run: |
          cargo lambda deploy api \
            --iam-role arn:aws:iam::123:role/lambda-exec \
            --memory 512 --timeout 30 \
            --tag git=${{ github.sha }}
</code></pre>

<table>
<tr><th>Choice</th><th>Detail</th></tr>
<tr><td>Build tool</td><td><code>cargo lambda</code> (zigbuild for cross-compile)</td></tr>
<tr><td>Architecture</td><td>arm64/Graviton (cheaper, slightly faster)</td></tr>
<tr><td>Runtime</td><td><code>provided.al2023</code> with custom binary</td></tr>
<tr><td>Test runner</td><td>cargo nextest (parallel by default)</td></tr>
<tr><td>HTTP framework</td><td>Axum + tower (most idiomatic for Lambda)</td></tr>
<tr><td>Cold start</td><td>~5&ndash;30ms; among the best on Lambda</td></tr>
<tr><td>Audit</td><td>cargo-audit, cargo-deny, cargo-vet</td></tr>
</table>

<p><strong>Trade-offs:</strong> Rust&rsquo;s build times in CI are notoriously slow without aggressive caching &mdash; <code>Swatinem/rust-cache@v2</code> is essential. arm64 native runners (<code>ubuntu-24.04-arm</code>) avoid cross-compile pain; before they existed you had to use <code>cargo zigbuild</code>. Fewer crates have arm64 support than amd64, but the gap has narrowed dramatically; check <code>cargo build --target aarch64-unknown-linux-gnu</code> for any runtime-loaded native libraries.</p>

<p><strong>Production polish:</strong> use Axum + Lambda runtime extension for routing, with <code>tower-http</code> for middleware (tracing, compression). Wire <code>tracing-opentelemetry</code> with the OTLP exporter pointed at Tempo or X-Ray. Use Lambda function URLs for simple HTTP endpoints (no API Gateway needed). For background work, pair with SQS or EventBridge triggers; Rust is excellent for high-throughput stream processing on Lambda. Add cargo-deny config files to enforce licence restrictions and dependency provenance &mdash; supply-chain hygiene matters more in compiled languages where one transitive dep can pull in unexpected code.</p>'''

ANSWERS[84] = r'''<p><strong>Situation:</strong> a real-time application (WebSocket-based chat, live video signalling, IoT command channel) needs canary releases on Kubernetes orchestrated by Jenkins. The challenge: long-lived connections don&rsquo;t round-robin across versions cleanly, and abrupt termination on traffic shift breaks user sessions. Standard HTTP canary techniques don&rsquo;t apply directly.</p>

<p><strong>Approach:</strong> use Argo Rollouts with a service mesh (Istio or Linkerd) for header-based traffic split &mdash; route a subset of new connections to the canary while existing connections drain naturally. Jenkins triggers the rollout; Argo Rollouts manages traffic shifting based on connection success rate and disconnection rate. Connection-affinity ensures returning users hit the same version for a session.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent any
  stages {
    stage('Promote canary') {
      steps {
        sh &apos;&apos;&apos;
          kubectl argo rollouts set image realtime-app \
            app=registry/realtime-app:${GIT_COMMIT} -n prod
          kubectl argo rollouts get rollout realtime-app -n prod --watch --timeout 1800s
        &apos;&apos;&apos;
      }
    }
  }
  post {
    failure { sh 'kubectl argo rollouts abort realtime-app -n prod' }
  }
}
</code></pre>

<pre><code># Argo Rollouts CRD with Istio integration
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: realtime-app, namespace: prod }
spec:
  strategy:
    canary:
      canaryService: realtime-canary
      stableService: realtime-stable
      trafficRouting:
        istio:
          virtualService:
            name: realtime-vs
            routes: [primary]
      steps:
        - setWeight: 5
        - pause: { duration: 5m }
        - analysis:
            templates: [{ templateName: ws-health }]
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: ws-health, namespace: prod }
spec:
  metrics:
    - name: connection-error-rate
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(websocket_connection_errors_total{version=&quot;canary&quot;}[2m]))
            / sum(rate(websocket_connections_total{version=&quot;canary&quot;}[2m]))
      successCondition: result[0] &lt; 0.02
      failureLimit: 2
</code></pre>

<table>
<tr><th>Concern</th><th>Pattern</th></tr>
<tr><td>Long-lived connections</td><td>terminationGracePeriodSeconds: 600+ for clean drain</td></tr>
<tr><td>Connection affinity</td><td>Cookie or sticky session via Istio DestinationRule</td></tr>
<tr><td>Sub-protocol changes</td><td>Version negotiation in handshake; never break wire format mid-rollout</td></tr>
<tr><td>Backpressure</td><td>Limit concurrent canary connections via rate limit</td></tr>
<tr><td>Metrics</td><td>Custom counters: connections_total, connection_errors, latency_p99</td></tr>
<tr><td>Reconnect storms</td><td>Stagger termination with preStop sleep + backoff guidance to clients</td></tr>
</table>

<p><strong>Trade-offs:</strong> WebSocket canary is harder than HTTP canary because metrics observe the connection lifecycle, not request rate &mdash; tune analysis templates accordingly. Without a service mesh, you can&rsquo;t do header-based routing cleanly; Linkerd is lighter than Istio if you don&rsquo;t need Istio&rsquo;s extra features. For very latency-sensitive use cases, consider Centrifugo or Phoenix Channels which were designed for this; standard rolling updates are often acceptable if your protocol gracefully reconnects.</p>

<p><strong>Production polish:</strong> set <code>terminationGracePeriodSeconds: 600</code> with a preStop hook that closes the listener but lets in-flight connections finish. Emit metrics from the application: connections, connection_errors, message_latency, reconnect_count &mdash; these are the canary&rsquo;s real signals. Layer client-side exponential backoff so users reconnect without thundering. For multi-region setups, use AnyCast IPs (Cloudflare, AWS Global Accelerator) and shift traffic at the DNS or LB layer rather than at the cluster.</p>'''

ANSWERS[85] = r'''<p><strong>Situation:</strong> a Next.js application (React with SSR/SSG/RSC) needs CI/CD with unit tests, integration tests, and deployment to Heroku. Heroku is awkward for Next.js because the framework is tightly coupled to Vercel&rsquo;s edge runtime; deploying to Heroku means giving up some optimisations but keeping the deployment story simple.</p>

<p><strong>Approach:</strong> build a standalone Next.js output (<code>output: 'standalone'</code> in <code>next.config.js</code>) so the deploy artefact is self-contained. Use the Heroku Container Registry for full runtime control, run Vitest or Jest for unit tests, Playwright for integration. The honest 2026 alternative is Vercel, Cloudflare Pages, or Netlify &mdash; Next.js works best where the host knows the framework.</p>

<pre><code># next.config.js
module.exports = {
  output: 'standalone',
  experimental: { serverActions: { bodySizeLimit: '2mb' } },
}
</code></pre>

<pre><code># Dockerfile (production)
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/public ./public
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
EXPOSE 3000
USER node
CMD ["node", "server.js"]
</code></pre>

<pre><code>name: nextjs-heroku
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test -- --coverage
      - uses: codecov/codecov-action@v4
      - run: npx playwright install --with-deps chromium
      - run: npm run build
      - run: npm run test:e2e

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "machine api.heroku.com login _ password ${{ secrets.HEROKU_API_KEY }}" &gt;&gt; ~/.netrc
          echo "machine git.heroku.com login _ password ${{ secrets.HEROKU_API_KEY }}" &gt;&gt; ~/.netrc
          heroku container:login
          heroku stack:set container -a nextjs-prod
          heroku container:push web -a nextjs-prod
          heroku container:release web -a nextjs-prod
</code></pre>

<table>
<tr><th>Concern</th><th>Detail</th></tr>
<tr><td>Build output</td><td><code>output: 'standalone'</code> &mdash; bundles minimal node_modules</td></tr>
<tr><td>Server</td><td>Next.js own server; no separate Express needed</td></tr>
<tr><td>Image size</td><td>~150 MB with alpine; ~80 MB with distroless</td></tr>
<tr><td>SSR perf</td><td>Heroku dyno spins up cold; consider Performance dyno</td></tr>
<tr><td>ISR / on-demand revalidation</td><td>Works but no edge cache like Vercel</td></tr>
<tr><td>Image optimisation</td><td>Use sharp; or proxy to Cloudinary/imgix</td></tr>
</table>

<p><strong>Trade-offs:</strong> Heroku for Next.js gives up the Vercel platform&rsquo;s edge runtime, automatic ISR cache invalidation, image optimisation CDN, and middleware-at-edge &mdash; you&rsquo;ll re-implement these with CloudFront or Cloudflare in front of Heroku. Pricing: Heroku Performance dynos for an SSR site can be more expensive than Vercel Pro for similar traffic. Render or Fly.io are better Heroku alternatives in 2026 with comparable simplicity and lower costs.</p>

<p><strong>Production polish:</strong> wire OpenTelemetry (<code>@vercel/otel</code> works on any host) for traces. Use a CDN in front of Heroku (Cloudflare, Fastly) for static asset caching and image optimisation. Configure middleware for auth/redirects judiciously &mdash; on Heroku, middleware runs in the Node.js process, not at edge, so it adds latency to every request. Honestly evaluate Vercel or Cloudflare Pages with Next.js on Pages Functions: for a Next.js app, the Vercel-native experience saves engineering time worth the platform cost.</p>'''

ANSWERS[86] = r'''<p><strong>Situation:</strong> an IoT solution sends device telemetry to AWS through GitHub Actions-driven pipelines that build the device-side firmware containers, deploy AWS IoT Core rules, and ship the cloud ingest services (Lambda for filtering, Kinesis for streaming, Timestream/InfluxDB for storage). The deploy must be auditable and reversible across thousands of devices.</p>

<p><strong>Approach:</strong> separate the device-side and cloud-side pipelines. Cloud side uses CDK or SAM for IoT Core rules, Lambda functions, and IAM. Device side builds container images for edge runtimes (Greengrass v2 component or KubeEdge); shipping to fleets uses Greengrass deployment groups or AWS Systems Manager. OIDC federation eliminates static credentials.</p>

<pre><code>name: iot-aws
on:
  push: { branches: [main] }
permissions: { id-token: write, contents: read }
jobs:
  cloud:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-iot
          aws-region: ap-south-1
      - run: npm ci
      - run: npx cdk synth
      - run: npx cdk diff
      - run: npx cdk deploy --all --require-approval never

  device-component:
    runs-on: ubuntu-24.04-arm
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-iot
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker buildx build --platform linux/arm64 \
            --tag $ECR/sensor-collector:${{ github.sha }} \
            --provenance true --sbom true --push device/sensor-collector
      - name: Greengrass component recipe
        run: |
          envsubst &lt; recipe.yaml.tpl &gt; recipe.yaml
          aws greengrassv2 create-component-version \
            --inline-recipe fileb://recipe.yaml
      - name: Staged deployment
        run: |
          aws greengrassv2 create-deployment \
            --target-arn arn:aws:iot:ap-south-1:123:thinggroup/canary \
            --components '{"com.example.SensorCollector": {"componentVersion": "${{ github.sha }}"}}' \
            --deployment-policies file://canary-policy.json
</code></pre>

<table>
<tr><th>Layer</th><th>Tool (2026)</th></tr>
<tr><td>Edge runtime</td><td>AWS IoT Greengrass v2, AWS IoT Core, KubeEdge on K3s</td></tr>
<tr><td>Telemetry ingest</td><td>IoT Core MQTT &rarr; Kinesis Firehose</td></tr>
<tr><td>Stream processing</td><td>Kinesis Data Streams &rarr; Lambda or Flink (KDA)</td></tr>
<tr><td>Storage</td><td>Timestream, InfluxDB, S3 + Iceberg</td></tr>
<tr><td>Device shadows</td><td>IoT Core Device Shadow for desired/reported state</td></tr>
<tr><td>OTA updates</td><td>Greengrass deployments, AWS IoT Jobs</td></tr>
<tr><td>Visualisation</td><td>Grafana + Timestream, AWS IoT SiteWise</td></tr>
</table>

<p><strong>Trade-offs:</strong> Greengrass v2 is opinionated &mdash; it works beautifully if you fit the model (component-based, MQTT-centric, AWS-locked). For non-AWS or polyglot fleets, KubeEdge or pure K3s + Flux is more portable but heavier. AWS IoT Core MQTT pricing is per-message and adds up at scale; Kinesis Data Streams has shard limits that can throttle bursty fleets. Always test deployments on a canary device group before fleet-wide release.</p>

<p><strong>Production polish:</strong> use Greengrass deployment policies with safe-deploy rollout (success threshold, time-based promotion). Layer Sigstore signing on Greengrass component artefacts; the device verifies before installing. For data tier, partition Timestream by tenant and use S3 Glacier for cold tiers. Wire AWS IoT Device Defender for anomaly detection (auth failures, unusual message rates). Plan for offline operation: edge components must function without cloud connectivity and reconcile when reconnected. Stagger deployments heavily &mdash; pushing to 10,000 devices simultaneously is the most expensive outage you&rsquo;ll experience.</p>'''

ANSWERS[87] = r'''<p><strong>Situation:</strong> the org runs workloads across on-prem and one or more clouds (AWS + Azure, or AWS + on-prem). The CI/CD pipeline must deploy the same containerised workload to all targets with consistent observability, security policy, and rollback semantics &mdash; without forking pipelines per environment.</p>

<p><strong>Approach:</strong> abstract behind GitOps with Argo CD ApplicationSets &mdash; each cluster registers itself, and ApplicationSets generate per-cluster Applications from a single template. Build once in CI, push to a globally accessible registry (Harbor with replication, or per-cloud mirrors), and let each cluster pull. Crossplane abstracts cloud-specific resources (RDS vs Azure Database) behind composite resources so manifests reference logical infrastructure, not vendor APIs.</p>

<pre><code># ApplicationSet for hybrid fleet
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: api-fleet, namespace: argocd }
spec:
  generators:
    - clusters:
        selector:
          matchLabels: { tier: prod }
  template:
    metadata: { name: 'api-{{name}}' }
    spec:
      project: prod
      source:
        repoURL: https://git.corp/manifests
        targetRevision: HEAD
        path: 'overlays/{{metadata.labels.cloud}}'
      destination:
        server: '{{server}}'
        namespace: api
      syncPolicy:
        automated: { prune: true, selfHeal: true }
        syncOptions: [CreateNamespace=true]
</code></pre>

<pre><code>name: hybrid-build
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: write }
jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: harbor.corp, username: ci, password: ${{ secrets.HARBOR }} }
      - uses: docker/build-push-action@v5
        with:
          tags: |
            harbor.corp/api/api:${{ github.sha }}
            harbor.corp/api/api:latest
          push: true
          provenance: true
          platforms: linux/amd64,linux/arm64
      - name: Bump manifest
        run: |
          cd manifests
          for cloud in aws azure onprem; do
            (cd overlays/$cloud &amp;&amp; kustomize edit set image api=harbor.corp/api/api:${{ github.sha }})
          done
          git config user.email ci@x &amp;&amp; git config user.name ci
          git commit -am "deploy ${{ github.sha }}"
          git push
</code></pre>

<table>
<tr><th>Concern</th><th>2026 default</th></tr>
<tr><td>Container registry</td><td>Harbor with cross-region replication, or per-cloud ECR/ACR/GAR mirrors</td></tr>
<tr><td>GitOps controller</td><td>Argo CD with ApplicationSets per cluster</td></tr>
<tr><td>Cross-cloud abstraction</td><td>Crossplane (cloud-agnostic CRDs)</td></tr>
<tr><td>Network</td><td>Cilium ClusterMesh or Submariner for cross-cluster service discovery</td></tr>
<tr><td>Secrets</td><td>Vault on-prem or External Secrets Operator with multi-backend</td></tr>
<tr><td>Observability</td><td>OpenTelemetry Collector per cluster &rarr; central Grafana/Datadog</td></tr>
<tr><td>Identity</td><td>SPIRE/SPIFFE for workload identity across all clusters</td></tr>
</table>

<p><strong>Trade-offs:</strong> &ldquo;same workload everywhere&rdquo; is harder than it sounds &mdash; cloud-specific managed services (RDS, CosmosDB, Cloud SQL) inevitably differ in behaviour. Crossplane levels the API surface but doesn&rsquo;t hide all behavioural differences. Per-cloud Helm value overrides remain necessary. For data-heavy workloads, the network latency between on-prem and cloud often forces co-locating data and compute &mdash; full active/active is rare in practice; active/passive with controlled failover is more common.</p>

<p><strong>Production polish:</strong> establish a clear network topology &mdash; ClusterMesh (Cilium) or Submariner for pod-to-pod across clusters, with strict NetworkPolicies. Use SPIRE/SPIFFE for cross-cluster mTLS identity. Centralise observability via OTEL Collector on every cluster pushing to a single Grafana stack with cluster-aware labelling. Run drift detection in Argo CD with self-heal off in production until you trust the pattern; once trusted, turn it on cluster-by-cluster. Plan failover drills quarterly; the first cross-cloud failover always reveals overlooked dependencies.</p>'''

ANSWERS[88] = r'''<p><strong>Situation:</strong> blockchain applications need stricter security and compliance than typical web services &mdash; smart contracts are immutable post-deployment, fund loss is direct, and regulatory frameworks (MiCA in EU, evolving US rules) require AML/KYC checks. GitHub Actions must enforce contract auditing, key management hygiene, and on-chain compliance gates.</p>

<p><strong>Approach:</strong> stack four mandatory gates &mdash; (1) static analysis with Slither, Aderyn, and Mythril; (2) formal verification via Halmos or Certora on critical paths; (3) gas analysis to catch DoS vectors; (4) dependency provenance via Cosign signatures and SBOMs. For deployment, never auto-deploy to mainnet &mdash; gate behind a Gnosis Safe / OpenZeppelin Defender multi-sig with timelock.</p>

<pre><code>name: blockchain-security
on: [pull_request]
permissions: { contents: read, security-events: write }
jobs:
  static:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: foundry-rs/foundry-toolchain@v1
      - run: forge build --sizes
      - name: Slither
        uses: crytic/slither-action@v0.4.0
        with: { sarif: slither.sarif, fail-on: high }
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: slither.sarif }
      - name: Aderyn (Cyfrin)
        run: |
          curl -sL https://raw.githubusercontent.com/Cyfrin/aderyn/main/cyfrinup/install | sh
          aderyn .

  fuzz-and-invariant:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: foundry-rs/foundry-toolchain@v1
      - run: forge test --fuzz-runs 100000 --invariant-runs 5000

  formal:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: pip install halmos
      - run: halmos --function check_

  gas:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: foundry-rs/foundry-toolchain@v1
      - run: forge test --gas-report

  compliance:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Sanctions list check on addresses in code
        run: |
          # Check hardcoded addresses against Chainalysis sanctions list
          python3 .ci/check_sanctions.py contracts/

  cosign-and-sbom:
    needs: [static, fuzz-and-invariant, formal, gas, compliance]
    runs-on: ubuntu-24.04
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: foundry-rs/foundry-toolchain@v1
      - run: forge build
      - uses: anchore/sbom-action@v0
        with: { path: . }
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign-blob --yes --output-signature out.sig out/contracts.json
</code></pre>

<table>
<tr><th>Layer</th><th>Tool (2026)</th></tr>
<tr><td>Static analysis</td><td>Slither, Aderyn, Wake, Mythril</td></tr>
<tr><td>Symbolic / formal</td><td>Halmos, Certora, Kontrol</td></tr>
<tr><td>Fuzzing / invariants</td><td>Foundry forge test</td></tr>
<tr><td>Gas / DoS</td><td>forge gas-report, Tenderly</td></tr>
<tr><td>Sanctions / compliance</td><td>Chainalysis API, TRM Labs, custom address checks</td></tr>
<tr><td>Multi-sig + timelock</td><td>Gnosis Safe, OpenZeppelin Defender</td></tr>
<tr><td>Provenance</td><td>Cosign + SBOM + Rekor transparency log</td></tr>
<tr><td>Hardware key signing</td><td>Fireblocks, Ledger Enterprise, AWS KMS raw signing</td></tr>
</table>

<p><strong>Trade-offs:</strong> formal verification (Certora especially) is expensive but catches classes of bugs unit tests never will &mdash; budget for it on critical financial logic. Multi-sig timelock slows incident response when a critical bug needs urgent patching; balance speed against guard-rails carefully. Sanctions screening is a moving target; subscribe to a service rather than maintaining your own list.</p>

<p><strong>Production polish:</strong> require a documented audit (Trail of Bits, OpenZeppelin, ConsenSys Diligence, Spearbit) before any mainnet deploy holding meaningful TVL. Use OpenZeppelin Defender Sentinels for runtime monitoring of contract state. Layer The Graph or Subsquid for indexing &mdash; CI must verify subgraph queries against new contract versions before deploy. Always run a full mainnet fork test in CI for upgradeable proxies; storage layout breaks are catastrophic and silent.</p>'''

ANSWERS[89] = r'''<p><strong>Situation:</strong> a Haskell service needs CI/CD with cabal/stack-based tests and deployment to AWS Lambda. Haskell on Lambda is unusual but viable &mdash; the JVM-style cold start is mitigated by GHC&rsquo;s native compilation, and the strong type system catches a class of errors before runtime.</p>

<p><strong>Approach:</strong> use Cabal or Stack as the build tool, package as a Lambda container image based on <code>provided.al2023</code>, and use the <code>aws-lambda-haskell-runtime</code> library for the handler shim. Test with HSpec and tasty in CI; deploy via OIDC. Build for arm64 (Graviton) for cost savings.</p>

<pre><code># Dockerfile
FROM haskell:9.10.1-slim AS build
WORKDIR /app
COPY *.cabal cabal.project ./
RUN cabal update &amp;&amp; cabal build --only-dependencies --enable-executable-static
COPY . .
RUN cabal build exe:bootstrap --enable-executable-static \
    &amp;&amp; cp $(cabal list-bin exe:bootstrap) /tmp/bootstrap

FROM public.ecr.aws/lambda/provided:al2023
COPY --from=build /tmp/bootstrap /var/runtime/bootstrap
RUN chmod +x /var/runtime/bootstrap
CMD ["bootstrap"]
</code></pre>

<pre><code>name: haskell-lambda
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: haskell-actions/setup@v2
        with: { ghc-version: '9.10.1', cabal-version: '3.12' }
      - uses: actions/cache@v4
        with:
          path: |
            ~/.cabal/store
            dist-newstyle
          key: cabal-${{ hashFiles('**/*.cabal', 'cabal.project') }}
      - run: cabal update
      - run: cabal build all --enable-tests
      - run: cabal test all --test-show-details=streaming
      - run: cabal check
      - name: HLint
        uses: haskell-actions/hlint-run@v2
      - name: weeder (dead code)
        run: cabal install weeder &amp;&amp; weeder

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04-arm
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-haskell-lambda
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker buildx build --platform linux/arm64 \
            --tag $ECR/haskell-fn:${{ github.sha }} --push .
      - run: |
          aws lambda update-function-code \
            --function-name haskell-api \
            --image-uri $ECR/haskell-fn:${{ github.sha }} \
            --architectures arm64
          aws lambda wait function-updated --function-name haskell-api
</code></pre>

<table>
<tr><th>Choice</th><th>Detail</th></tr>
<tr><td>Build tool</td><td>Cabal (modern) or Stack (curated package sets)</td></tr>
<tr><td>Runtime library</td><td>aws-lambda-haskell-runtime</td></tr>
<tr><td>HTTP framework</td><td>Servant or wai-extra for routing</td></tr>
<tr><td>Test framework</td><td>HSpec, tasty, QuickCheck for property tests</td></tr>
<tr><td>Static binary</td><td>--enable-executable-static for a self-contained bootstrap</td></tr>
<tr><td>Cold start</td><td>~50-200ms; better than Java but worse than Go/Rust</td></tr>
</table>

<p><strong>Trade-offs:</strong> Haskell on Lambda is a niche choice &mdash; few production references, smaller library ecosystem for AWS SDKs. The build is slow (Cabal solver + GHC) and benefits dramatically from caching. For high-throughput services, GHC&rsquo;s garbage collector can pause longer than Go&rsquo;s; tune <code>+RTS -A256m -RTS</code> for short pauses. Most teams using Haskell run it on Fargate or EKS rather than Lambda &mdash; long-lived containers play to Haskell&rsquo;s strengths.</p>

<p><strong>Production polish:</strong> use HLS (Haskell Language Server) and ormolu/fourmolu for consistent formatting in CI. Add weeder to detect dead code. Use Servant&rsquo;s type-level routes to enforce API contracts at compile time &mdash; this is one of Haskell&rsquo;s strongest cards. Wire OpenTelemetry via <code>otel-exporter-otlp</code> for traces. Honestly evaluate whether Lambda is the right target; for any sustained traffic, ECS Fargate with auto-scaling tasks is usually cheaper and a better cultural fit for Haskell&rsquo;s strengths.</p>'''

ANSWERS[90] = r'''<p><strong>Situation:</strong> the team wants continuous delivery to Google Cloud Run from GitHub Actions. Cloud Run is the simpler GCP target for stateless containers &mdash; scale-to-zero, request-based billing, automatic HTTPS &mdash; and pairs beautifully with GitHub Actions via Workload Identity Federation.</p>

<p><strong>Approach:</strong> three-step pipeline &mdash; (1) authenticate with WIF (no JSON keys ever), (2) build and push to Artifact Registry, (3) deploy via <code>gcloud run deploy</code>. For canary releases, use Cloud Run revisions with traffic splitting (<code>--no-traffic</code> on deploy, then progressive shift). For more elaborate progressive delivery, layer Cloud Deploy.</p>

<pre><code>name: cloud-run
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  ship:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh
          service_account: gha@proj.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker asia-south1-docker.pkg.dev

      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: asia-south1-docker.pkg.dev/proj/svc/api:${{ github.sha }}
          platforms: linux/amd64
          provenance: true
          sbom: true
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Deploy canary (no traffic)
        run: |
          gcloud run deploy api \
            --image asia-south1-docker.pkg.dev/proj/svc/api:${{ github.sha }} \
            --region asia-south1 \
            --tag canary --no-traffic \
            --revision-suffix ${{ github.sha }} \
            --memory 512Mi --cpu 1 \
            --concurrency 80 --max-instances 50 \
            --service-account run-app@proj.iam.gserviceaccount.com

      - name: Smoke test canary
        run: |
          URL=$(gcloud run services describe api --region asia-south1 \
            --format "value(status.traffic[?(@.tag=='canary')].url)")
          for i in 1 2 3; do curl -fsS $URL/healthz; done

      - name: Promote 10% &rarr; 100%
        run: |
          gcloud run services update-traffic api --region asia-south1 \
            --to-tags canary=10
          sleep 300   # bake time
          gcloud run services update-traffic api --region asia-south1 \
            --to-tags canary=100
</code></pre>

<table>
<tr><th>Choice</th><th>Detail</th></tr>
<tr><td>Auth</td><td>Workload Identity Federation; no JSON keys</td></tr>
<tr><td>Image registry</td><td>Artifact Registry with vulnerability scanning</td></tr>
<tr><td>CPU allocation</td><td>Always-allocated for sub-second background jobs; per-request for cost</td></tr>
<tr><td>Concurrency</td><td>80 (default) &mdash; tune to memory/CPU profile</td></tr>
<tr><td>Min instances</td><td>0 for cost; ge;1 to avoid cold starts</td></tr>
<tr><td>Progressive delivery</td><td>Revision tags + traffic split, or Cloud Deploy</td></tr>
<tr><td>Provenance</td><td>SLSA attestation + Binary Authorization</td></tr>
</table>

<p><strong>Trade-offs:</strong> Cloud Run scale-to-zero saves cost dramatically for low-traffic services but introduces 1&ndash;5 second cold starts for cold instances; <code>--min-instances=1</code> eliminates this at the cost of a continuous bill. Cloud Run service-to-service via Cloud Run gen2 (sidecar) is GCP-locked but enables internal-only services and zero-trust networking. For very long-running connections (WebSockets), Cloud Run supports them but ALB-style health checks and request timeouts behave differently than on EKS &mdash; test carefully.</p>

<p><strong>Production polish:</strong> enable Binary Authorization to block unsigned images at deploy. Use VPC connector for private IP access to Cloud SQL or Memorystore. Wire Cloud Trace via OpenTelemetry &mdash; the GCP OpenTelemetry exporter integrates seamlessly. For multi-region failover, deploy the same service to multiple regions and front with a Global External Load Balancer; Cloud Run regional services don&rsquo;t auto-failover. Always set <code>--max-instances</code> to bound runaway billing during traffic spikes; the default cap is generous enough to bankrupt a side project overnight.</p>'''

ANSWERS[91] = r'''<p><strong>Situation:</strong> a team has a <strong>C# / ASP.NET Core 9</strong> service. Leadership prefers <strong>Heroku</strong> as the runtime for fast iteration, with <strong>unit tests</strong>, <strong>integration tests</strong>, and gated promotion through review and production apps.</p>

<p><strong>Approach:</strong> build with <strong>GitHub Actions</strong> using the official <strong>setup-dotnet</strong> action, run tests with <strong>xUnit</strong> plus <strong>Testcontainers for .NET</strong> for real Postgres/Redis dependencies, publish the app, and deploy via the <strong>Heroku Container Registry</strong> (more flexible than Heroku&rsquo;s Git buildpack for .NET). Use a <strong>chiseled distroless</strong> base image to keep the container tiny and reduce CVE surface. Production polish: <strong>Heroku Review Apps</strong> for every PR, <strong>Pipeline Promotion</strong> from staging to prod so the same image hash crosses environments, <strong>Heroku Postgres</strong> for the DB, and structured logging to <strong>Datadog</strong> via the log drain.</p>

<pre><code>name: ci-cd
on:
  push: { branches: [main] }
  pull_request:
permissions: { id-token: write, contents: read }
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '9.0.x' }
      - run: dotnet restore
      - run: dotnet build --no-restore -c Release
      - run: dotnet test --no-build -c Release --logger trx --collect:"XPlat Code Coverage"
      - uses: codecov/codecov-action@v5

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Login to Heroku registry
        run: echo "${{ secrets.HEROKU_API_KEY }}" | docker login registry.heroku.com -u _ --password-stdin
      - name: Build &amp; push image
        run: |
          docker buildx build --platform linux/amd64 \
            --tag registry.heroku.com/$HEROKU_APP/web:${{ github.sha }} \
            --tag registry.heroku.com/$HEROKU_APP/web:latest \
            --push .
        env:
          HEROKU_APP: my-csharp-staging
      - name: Release to Heroku
        run: |
          curl -n -X PATCH https://api.heroku.com/apps/$HEROKU_APP/formation \
            -d '{"updates":[{"type":"web","docker_image":"'"$(docker inspect registry.heroku.com/$HEROKU_APP/web:latest --format '{{index .Id}}')"'"}]}' \
            -H "Content-Type: application/json" \
            -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
            -H "Authorization: Bearer ${{ secrets.HEROKU_API_KEY }}"
</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Choice</th><th>Why</th><th>Cost</th></tr>
<tr><td>Heroku Container Registry</td><td>Full Dockerfile control, supports .NET 9 properly</td><td>No free tier; Eco/Basic dyno pricing</td></tr>
<tr><td>Chiseled Ubuntu image</td><td>~110 MB final image, near-zero CVEs</td><td>Slightly harder local debugging</td></tr>
<tr><td>Testcontainers for .NET</td><td>Real Postgres/Redis in CI; no flaky in-memory fakes</td><td>~30 s slower test runs</td></tr>
<tr><td>Pipeline Promotion</td><td>Same image hash from staging to prod</td><td>Requires Heroku Teams plan</td></tr>
<tr><td>Review Apps</td><td>Each PR gets a real URL reviewers can poke</td><td>Burns dyno hours</td></tr>
</table>

<p><strong>Production polish:</strong> enable <strong>Heroku Auto-Scaling</strong> on web dynos (Performance tier), wire <strong>Datadog APM</strong> with the .NET tracer, set <strong>health checks</strong> via the <strong>release phase</strong> to run EF Core migrations safely, gate deploys on <strong>required status checks</strong> (test + Trivy + Snyk SCA) with branch protection, and keep the <strong>Heroku API key</strong> short-lived by rotating via GitHub <strong>OIDC + Heroku Federated Identity</strong> where possible. In 2026 many shops have moved off Heroku entirely &mdash; if cost or container limits start hurting, the natural migration path is <strong>Render</strong>, <strong>Fly.io</strong>, or <strong>Railway</strong>; all three accept the same Dockerfile with minimal config change.</p>'''

ANSWERS[92] = r'''<p><strong>Situation:</strong> a team writes <strong>Dart</strong> services (server-side Dart or Flutter web/mobile) and needs <strong>continuous integration</strong> with aggressive <strong>dependency caching</strong> so each CI run is fast despite <strong>pub.dev</strong> being slow over flaky network paths.</p>

<p><strong>Approach:</strong> use <strong>GitHub Actions</strong> with <strong>dart-lang/setup-dart</strong>, cache the <strong>pub cache</strong> (<code>$HOME/.pub-cache</code>) keyed by <code>pubspec.lock</code>, cache the <strong>build_runner</strong> outputs (<code>.dart_tool/build</code>) keyed by source-tree hash, and run analyzer + tests + format check in parallel. For Flutter, also cache the Flutter SDK and the Gradle/Pods caches. Use the matrix strategy to run on multiple Dart channels (<code>stable</code>, <code>beta</code>) when releasing a package, single-channel for an app.</p>

<pre><code>name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - uses: dart-lang/setup-dart@v1
        with: { sdk: stable }

      - name: Cache pub
        uses: actions/cache@v4
        with:
          path: |
            ~/.pub-cache
            .dart_tool
          key: pub-${{ runner.os }}-${{ hashFiles('**/pubspec.lock') }}
          restore-keys: pub-${{ runner.os }}-

      - run: dart pub get
      - run: dart analyze --fatal-infos
      - run: dart format --output=none --set-exit-if-changed .
      - run: dart pub run build_runner build --delete-conflicting-outputs
      - run: dart test --coverage=coverage --reporter expanded
      - run: dart pub global activate coverage &amp;&amp; dart pub global run coverage:format_coverage --packages=.dart_tool/package_config.json --report-on=lib --in=coverage --lcov --out=coverage/lcov.info
      - uses: codecov/codecov-action@v5
        with: { files: coverage/lcov.info }
</code></pre>

<p>For Flutter add <code>flutter-actions/setup-flutter@v2</code> with the channel and a cache step for <code>~/.pub-cache</code>, <code>~/.gradle/caches</code>, <code>~/Library/Caches/CocoaPods</code>. The <strong>melos</strong> tool is the standard for Dart monorepos &mdash; it knows which packages changed and skips unchanged ones, which compounds well with the cache.</p>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Pattern</th><th>Win</th><th>Risk</th></tr>
<tr><td>pub-cache caching</td><td>Skip pub.dev fetch &mdash; saves 30&ndash;60 s per job</td><td>Stale cache after pubspec.lock edits if key not refreshed</td></tr>
<tr><td>.dart_tool caching</td><td>Skip codegen on unchanged sources</td><td>Spurious incremental bugs &mdash; clear cache on schema change</td></tr>
<tr><td>melos for monorepos</td><td>Only tests packages whose deps changed</td><td>Requires disciplined workspace structure</td></tr>
<tr><td>matrix on channels</td><td>Catch breakage before stable upgrade</td><td>Doubles CI minutes</td></tr>
</table>

<p><strong>Production polish:</strong> for Flutter, run <strong>integration_test</strong> with <strong>Firebase Test Lab</strong> for real-device coverage; for backend Dart, pair with <strong>shelf_test</strong> or <strong>spanner_test</strong>. Add <strong>very_good_analysis</strong> as the lint baseline (stricter than <code>package:lints/recommended.yaml</code>), enforce <strong>dependabot</strong> for pub updates with grouped weekly PRs, and consider <strong>Bazel</strong> if the monorepo grows past 30 packages &mdash; melos hits a ceiling around there. For supply chain, run <strong>OSV-Scanner</strong> against <code>pubspec.lock</code> in every PR; vulnerability data for Dart improved a lot in 2025&ndash;2026 thanks to Google&rsquo;s OSV pipeline.</p>'''

ANSWERS[93] = r'''<p><strong>Situation:</strong> a security team wants <strong>Docker container security best practices</strong> enforced consistently across every Jenkins pipeline &mdash; not just &ldquo;recommendations in a Confluence page&rdquo; but actually <strong>failing builds</strong> when policy is violated, with a clear path for engineers to fix issues.</p>

<p><strong>Approach:</strong> shift security left in three layers: <strong>build-time</strong> (small base image, no root, no shell, pinned packages, build attestations), <strong>scan-time</strong> (vulnerability + secret + license + IaC scanning), and <strong>admission-time</strong> (signed images only, policies via OPA/Kyverno on the cluster). Drive it through a <strong>Jenkins Shared Library</strong> so every team gets the same policy by importing one line.</p>

<pre><code>// vars/secureContainerBuild.groovy in your shared library
def call(Map args) {
  def image = args.image
  def dockerfile = args.dockerfile ?: 'Dockerfile'
  def severity = args.severity ?: 'HIGH,CRITICAL'

  stage('Dockerfile lint') {
    sh "hadolint --failure-threshold error ${dockerfile}"
  }

  stage('Build with provenance') {
    sh &apos;&apos;&apos;
      docker buildx build \
        --provenance=mode=max \
        --sbom=true \
        --attest=type=sbom \
        --attest=type=provenance,mode=max \
        --output type=image,name=$IMAGE,push=true \
        -f $DOCKERFILE .
    &apos;&apos;&apos;
  }

  stage('Vulnerability scan') {
    sh "trivy image --severity ${severity} --exit-code 1 --ignore-unfixed ${image}"
    sh "grype ${image} --fail-on high"
  }

  stage('Secret scan') {
    sh "trivy fs --scanners secret --exit-code 1 ."
  }

  stage('Sign image') {
    withCredentials([file(credentialsId: 'cosign-key', variable: 'COSIGN_KEY')]) {
      sh "cosign sign --key ${COSIGN_KEY} ${image} --yes"
    }
  }

  stage('SBOM &amp; attest') {
    sh "syft ${image} -o spdx-json &gt; sbom.json"
    sh "cosign attest --predicate sbom.json --type spdx --key ${COSIGN_KEY} ${image} --yes"
  }
}
</code></pre>

<p>The Dockerfile baseline pins everything: <code>FROM cgr.dev/chainguard/static:latest@sha256:...</code> for a non-root, no-shell, minimal image. For interpreted runtimes, Chainguard&rsquo;s distroless images for Python, Node, Java, .NET are similar. Set <code>USER 65532</code>, <code>HEALTHCHECK NONE</code> (let K8s probes do it), and use multi-stage builds so build tools never reach the final image.</p>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Control</th><th>Why</th><th>Friction</th></tr>
<tr><td>hadolint</td><td>Catches Dockerfile smells (root user, latest tags)</td><td>Some false positives &mdash; allowlist intentional cases</td></tr>
<tr><td>Trivy + Grype</td><td>Two scanners catch what one misses; Grype tracks NVD differently</td><td>Slows pipeline ~30 s</td></tr>
<tr><td>Cosign keyless</td><td>OIDC-based signing; no key to manage</td><td>Requires Sigstore Rekor trust</td></tr>
<tr><td>SBOM + provenance attestation</td><td>SLSA Level 3 capable; auditors love it</td><td>Adds ~15 MB of metadata per image</td></tr>
<tr><td>Kyverno admission</td><td>Cluster refuses unsigned/unscanned images</td><td>Bricks deploys if signing is broken</td></tr>
</table>

<p><strong>Production polish:</strong> wire the cluster side &mdash; <strong>Kyverno</strong> with <code>verifyImages</code> and <code>imageReferences</code> rules ensures only signed images from your registry deploy; <strong>Falco</strong> watches runtime behaviour for syscall anomalies; <strong>Tetragon</strong> (eBPF) does the same with less overhead. For the policy lifecycle, store Kyverno policies in their own repo synced via Argo CD so policy changes also go through PR review. Wave new policies in <strong>audit mode</strong> first, then promote to <strong>enforce</strong> after a quiet week.</p>'''

ANSWERS[94] = r'''<p><strong>Situation:</strong> the security and platform teams want <strong>compliance checks</strong> (CIS Kubernetes Benchmark, PCI DSS, SOC 2 controls) enforced for every Kubernetes deployment &mdash; with auditable evidence trails &mdash; using <strong>GitHub Actions</strong> as the CI engine.</p>

<p><strong>Approach:</strong> compliance has three loops: <strong>pre-deploy</strong> (lint manifests, run policy as code), <strong>at-deploy</strong> (admission controller blocks non-compliant resources), and <strong>continuous</strong> (cluster auditor scans live resources, reports drift). GitHub Actions owns the pre-deploy loop with <strong>kube-linter</strong>, <strong>Kyverno CLI</strong>, <strong>Checkov</strong>, and <strong>kubescape</strong>; Argo CD applies manifests; <strong>Kyverno</strong> on cluster enforces at admission; <strong>kube-bench</strong> and <strong>Trivy Operator</strong> run continuous compliance scans.</p>

<pre><code>name: compliance
on:
  pull_request:
    paths: ['k8s/**', 'helm/**']
permissions: { contents: read, pull-requests: write, security-events: write }
jobs:
  policy:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - name: Render Helm charts
        run: |
          helm dependency build helm/myapp
          helm template myapp helm/myapp --values helm/myapp/values-prod.yaml &gt; rendered.yaml

      - name: kube-linter
        run: |
          curl -L https://github.com/stackrox/kube-linter/releases/latest/download/kube-linter-linux.tar.gz | tar xz
          ./kube-linter lint rendered.yaml --config .kube-linter.yaml

      - name: Kyverno policy test
        uses: kyverno/action-install-cli@v1
      - run: |
          kyverno apply policies/ --resource rendered.yaml \
            --policy-report --output-format=junit &gt; kyverno-report.xml

      - name: Checkov (CIS, NIST, PCI)
        uses: bridgecrewio/checkov-action@v12
        with:
          framework: kubernetes
          quiet: true
          soft_fail: false
          output_format: sarif
          output_file_path: checkov.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: checkov.sarif }

      - name: kubescape NSA + MITRE framework
        run: |
          curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
          kubescape scan framework nsa,mitre rendered.yaml --format sarif --output kubescape.sarif --fail-threshold high

      - name: Upload kubescape SARIF
        uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: kubescape.sarif }
</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Tool</th><th>Strength</th><th>Weakness</th></tr>
<tr><td>kube-linter</td><td>Fast YAML lint, opinionated defaults</td><td>Limited custom policy language</td></tr>
<tr><td>Kyverno</td><td>Same policies for CI &amp; admission &mdash; single source of truth</td><td>YAML-only DSL feels limiting for complex logic</td></tr>
<tr><td>Checkov</td><td>Multi-framework (PCI, NIST 800-53, CIS); rich rule library</td><td>Some rules outdated for K8s 1.30+</td></tr>
<tr><td>kubescape</td><td>NSA/CISA, MITRE ATT&amp;CK frameworks built-in</td><td>Slower; CLI changes between minor versions</td></tr>
<tr><td>Gatekeeper / OPA</td><td>Rego is more expressive than Kyverno YAML</td><td>Higher learning curve; two tools to maintain</td></tr>
</table>

<p><strong>Production polish:</strong> for evidence, route SARIF outputs to <strong>GitHub Code Scanning</strong> (auditors see findings, fixes, and dismissals over time). On cluster, deploy <strong>Trivy Operator</strong> and <strong>Falco</strong> for continuous runtime compliance; reports flow to <strong>OpenPolicyAgent&rsquo;s policy reports</strong> or a SIEM (Splunk, Sumo Logic, Grafana). Run <strong>kube-bench</strong> as a CronJob to assess CIS controls hourly; alarm on regressions. For SOC 2 specifically, the audit trail benefits enormously from <strong>signed commits</strong> (Sigstore gitsign), <strong>required reviews</strong>, and <strong>Argo CD&rsquo;s sync history</strong> &mdash; auditors can correlate every cluster change to a reviewed, signed PR.</p>'''

ANSWERS[95] = r'''<p><strong>Situation:</strong> a Swift codebase compiles a small set of <strong>microservice-style functions</strong> targeting <strong>AWS Lambda</strong> (image moderation, signed-URL generation, webhook ingestion). The team wants a <strong>CI/CD pipeline</strong> with unit tests on Linux and automatic deploys per environment.</p>

<p><strong>Approach:</strong> use the <strong>Swift AWS Lambda Runtime</strong>, compile in a Linux build container (Lambda is Linux-only), package as a <code>provided.al2023</code> custom runtime ZIP or a container image, run tests with <strong>swift-testing</strong>, and deploy via <strong>AWS SAM</strong> or <strong>Serverless Framework</strong>. Build on <strong>arm64</strong> (Graviton) for ~30% cost savings &mdash; native Swift on aarch64 is rock-solid as of 2026.</p>

<pre><code>name: ci-cd
on:
  push: { branches: [main] }
  pull_request:
permissions: { id-token: write, contents: read }
jobs:
  build:
    runs-on: ubuntu-24.04
    container:
      image: swift:5.10-jammy
    steps:
      - uses: actions/checkout@v4
      - name: Cache build artefacts
        uses: actions/cache@v4
        with:
          path: .build
          key: swift-${{ runner.os }}-${{ hashFiles('Package.resolved') }}
      - run: swift test --enable-code-coverage
      - run: |
          swift build -c release \
            -Xswiftc -static-stdlib \
            --product MyFunction
      - name: Package for Lambda
        run: |
          mkdir -p .lambda
          cp .build/release/MyFunction .lambda/bootstrap
          cd .lambda &amp;&amp; zip -r ../lambda.zip .
      - uses: actions/upload-artifact@v4
        with: { name: lambda, path: lambda.zip }

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-lambda-deployer
          aws-region: ap-south-1
      - uses: actions/download-artifact@v4
        with: { name: lambda }
      - name: Deploy via SAM
        run: |
          sam deploy --no-fail-on-empty-changeset \
            --stack-name swift-fns-prod \
            --parameter-overrides "ImageTag=${{ github.sha }}" \
            --capabilities CAPABILITY_IAM
</code></pre>

<p>The <code>template.yaml</code> declares <code>Runtime: provided.al2023</code>, <code>Architectures: [arm64]</code>, <code>MemorySize: 512</code>, and CodeDeploy traffic shifting via <code>DeploymentPreference: Canary10Percent5Minutes</code> so a bad release rolls back automatically on CloudWatch alarms.</p>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Choice</th><th>Why</th><th>Watch out for</th></tr>
<tr><td>Custom runtime (provided.al2023)</td><td>Smaller cold start than container images; native Swift</td><td>Manual <code>bootstrap</code> entrypoint</td></tr>
<tr><td>arm64 (Graviton)</td><td>~30% cheaper, plenty fast for Swift</td><td>Must build on aarch64 CI</td></tr>
<tr><td>-static-stdlib</td><td>No glibc surprises across Lambda image refreshes</td><td>Larger binary (~30 MB)</td></tr>
<tr><td>SAM Canary10Percent5Minutes</td><td>Auto-rollback on alarm</td><td>5 min minimum bake adds release latency</td></tr>
<tr><td>swift-testing</td><td>Modern (Swift 5.10+) macro-based testing</td><td>Some XCTest features still nicer</td></tr>
</table>

<p><strong>Production polish:</strong> add <strong>X-Ray</strong> tracing via the Lambda extension (or OpenTelemetry Lambda layer for cross-vendor portability), pipe logs to <strong>CloudWatch Logs Insights</strong> with structured JSON, set CloudWatch alarms on <code>Errors</code>, <code>Throttles</code>, and p99 <code>Duration</code> &mdash; CodeDeploy hooks into those for auto-rollback. For cold start, enable <strong>Provisioned Concurrency</strong> on hot paths and consider <strong>SnapStart</strong>-equivalent techniques (preinitialise resources in a global) &mdash; the Swift runtime starts fast enough that most workloads don&rsquo;t need PC, saving cost over Java/.NET equivalents.</p>'''

ANSWERS[96] = r'''<p><strong>Situation:</strong> a <strong>real-time application</strong> (chat, collaboration, live tracking) on Kubernetes with <strong>WebSockets</strong> and <strong>persistent in-memory sessions</strong>. A bad deploy causes user-visible disconnects, so the team needs <strong>automated rollback</strong> on health regression &mdash; orchestrated by Jenkins.</p>

<p><strong>Approach:</strong> use <strong>Argo Rollouts</strong> as the deployment engine (Jenkins doesn&rsquo;t roll back deployments itself &mdash; it triggers them and watches outcomes), with <strong>AnalysisTemplates</strong> that compare error rate, connection failure rate, and p95 message latency against the previous version. Rollouts auto-aborts and reverts on regression. Jenkins drives the pipeline: build, push, update the Rollout, wait for promotion or abort, report status to the team.</p>

<pre><code>// Jenkinsfile
pipeline {
  agent { kubernetes { yaml libraryResource('agents/buildkit.yaml') } }
  environment {
    IMAGE = "ghcr.io/acme/realtime-api:${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Build &amp; sign') {
      steps {
        sh "buildctl build --frontend=dockerfile.v0 --local context=. --local dockerfile=. --output type=image,name=$IMAGE,push=true"
        withCredentials([file(credentialsId: 'cosign-key', variable: 'COSIGN_KEY')]) {
          sh "cosign sign --key $COSIGN_KEY $IMAGE --yes"
        }
      }
    }

    stage('Trigger canary rollout') {
      steps {
        sh "kubectl argo rollouts set image realtime-api app=$IMAGE -n realtime"
      }
    }

    stage('Watch rollout') {
      steps {
        script {
          def status = sh(
            script: "kubectl argo rollouts status realtime-api -n realtime --timeout 20m",
            returnStatus: true
          )
          if (status != 0) {
            error "Rollout failed or was auto-rolled back"
          }
        }
      }
    }
  }
  post {
    failure {
      slackSend channel: '#deploys', color: 'danger',
        message: "Realtime API rollback executed for ${env.IMAGE}. AnalysisTemplate exceeded thresholds."
    }
  }
}
</code></pre>

<p>The Rollout spec uses canary strategy with weight steps (10%, 25%, 50%, 100%) and an <strong>AnalysisTemplate</strong> that queries <strong>Prometheus</strong> for WebSocket error rate and connection drops:</p>

<pre><code>apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: ws-canary-quality }
spec:
  metrics:
    - name: ws-error-rate
      interval: 30s
      successCondition: result &lt; 0.01
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(ws_messages_failed_total{rollouts_pod_template_hash="{{args.canary-hash}}"}[1m]))
            /
            sum(rate(ws_messages_total{rollouts_pod_template_hash="{{args.canary-hash}}"}[1m]))
</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Aspect</th><th>Decision</th><th>Reasoning</th></tr>
<tr><td>Rollout engine</td><td>Argo Rollouts over Flagger</td><td>Better Jenkins/Argo CD integration in 2026; mature dashboard</td></tr>
<tr><td>Traffic routing</td><td>NGINX or Istio TrafficSplit</td><td>Real WebSocket-aware load balancing; sticky to canary pod once connected</td></tr>
<tr><td>Session handling</td><td>Externalise to Redis/Valkey</td><td>So a rollback doesn&rsquo;t lose in-flight sessions</td></tr>
<tr><td>Drain on rollback</td><td>preStop hook + terminationGracePeriodSeconds: 90</td><td>Existing WS connections drain cleanly</td></tr>
<tr><td>Jenkins role</td><td>Trigger + watch only</td><td>Rollback decision lives in Rollouts, not in Groovy</td></tr>
</table>

<p><strong>Production polish:</strong> add a <strong>shadow traffic</strong> step before any user-visible canary &mdash; replay 5% of production traffic through the new version with no response delivered to clients, comparing message processing rate and error patterns. WebSocket-specific: ensure the <strong>load balancer</strong> supports <strong>sticky sessions</strong> by pod hash, and that <strong>cluster autoscaler / Karpenter</strong> doesn&rsquo;t drain canary pods mid-canary. For observability, push WebSocket lifecycle events (<code>connect</code>, <code>disconnect</code>, <code>error</code>) to Prometheus with the rollouts_pod_template_hash label &mdash; that&rsquo;s how Argo Rollouts attributes signal to the canary vs stable side. Run <strong>chaos tests</strong> via <strong>Chaos Mesh</strong> on staging to validate the rollback path actually works before relying on it in prod.</p>'''

ANSWERS[97] = r'''<p><strong>Situation:</strong> a team has a <strong>Go backend</strong> built with <strong>go-chi</strong> or <strong>fiber</strong>, paired with a <strong>static frontend</strong> that lives on <strong>Netlify</strong>. Strictly speaking Netlify hosts the SPA/frontend; the Go API runs elsewhere &mdash; but the pipeline must build, test, and ship both in lockstep.</p>

<p><strong>Approach:</strong> use <strong>GitHub Actions</strong> with two parallel jobs: <strong>backend</strong> builds Go, runs <code>go test ./... -race -cover</code>, builds a Linux binary, pushes to <strong>Fly.io</strong> or <strong>Render</strong> (or AWS ECS if you must), and <strong>frontend</strong> builds the static bundle and deploys to <strong>Netlify</strong> via the <strong>Netlify CLI</strong>. A third <strong>integration</strong> job runs after both, hitting the deployed services with <strong>k6</strong> smoke tests.</p>

<pre><code>name: ci-cd
on:
  push: { branches: [main] }
  pull_request:
permissions: { id-token: write, contents: read }

jobs:
  backend:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.22', cache: true }
      - run: go mod download
      - run: go vet ./...
      - run: go test ./... -race -coverprofile=coverage.out
      - run: go build -ldflags="-s -w" -o api ./cmd/api
      - uses: codecov/codecov-action@v5
      - name: Deploy to Fly.io
        if: github.ref == 'refs/heads/main'
        uses: superfly/flyctl-actions/setup-flyctl@master
      - if: github.ref == 'refs/heads/main'
        run: flyctl deploy --remote-only
        env: { FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }} }

  frontend:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm, cache-dependency-path: web/pnpm-lock.yaml }
      - working-directory: web
        run: |
          pnpm install --frozen-lockfile
          pnpm test --run
          pnpm build
      - uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: 'web/dist'
          production-branch: main
          deploy-message: ${{ github.event.head_commit.message }}
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}

  integration:
    needs: [backend, frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - run: k6 run scripts/smoke.js
        env: { API_BASE: https://api.example.com }
</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Pattern</th><th>Win</th><th>Cost</th></tr>
<tr><td>Two-track pipeline</td><td>Backend and frontend deploy independently</td><td>Need explicit coordination for breaking API changes</td></tr>
<tr><td>Netlify for frontend</td><td>Atomic deploys, instant rollback, edge CDN included</td><td>Build minutes meter; cold cache on big bundles</td></tr>
<tr><td>Fly.io for Go API</td><td>Global anycast, fast cold start, simple CLI</td><td>Less mature than ECS/Cloud Run for compliance-heavy shops</td></tr>
<tr><td>k6 post-deploy smoke</td><td>Catches deploy-only bugs (env vars, secrets)</td><td>Doesn&rsquo;t replace real integration tests in CI</td></tr>
<tr><td>Codecov + race detector</td><td>Catches concurrency bugs early</td><td>Race tests are 2&ndash;5x slower</td></tr>
</table>

<p><strong>Production polish:</strong> use <strong>Netlify Deploy Previews</strong> for every PR &mdash; reviewers get a real URL. For the Go API, point <strong>OpenTelemetry</strong> at <strong>Grafana Cloud</strong> or <strong>Honeycomb</strong> for traces + metrics + logs in one place; export structured logs with <strong>slog</strong>. Use <strong>GoReleaser</strong> if you also distribute CLI binaries &mdash; it integrates with Cosign for signed releases. Schedule <strong>govulncheck</strong> daily against the codebase to catch newly disclosed Go ecosystem CVEs without waiting for a release. For breaking API changes, run a <strong>contract test</strong> (Pact or Schemathesis against the OpenAPI spec) in the integration job so frontend and backend stay in sync.</p>'''

ANSWERS[98] = r'''<p><strong>Situation:</strong> a data science team wants to <strong>continuously deploy AI/ML models</strong> &mdash; classifiers, embedders, fine-tuned LLMs &mdash; to <strong>Google Kubernetes Engine (GKE)</strong> via <strong>GitHub Actions</strong>. They need GPU-aware deploys, model versioning, drift monitoring, and easy rollback.</p>

<p><strong>Approach:</strong> separate the <strong>model artefact pipeline</strong> (training, evaluation, registry promotion) from the <strong>serving pipeline</strong> (container build, GKE rollout). Use <strong>MLflow</strong> or <strong>Vertex AI Model Registry</strong> for model versioning, <strong>KServe</strong> for serving (or <strong>vLLM</strong> for LLMs specifically), <strong>Argo CD</strong> for GitOps deploy, and <strong>Workload Identity Federation</strong> so GitHub Actions auths to GCP without static keys.</p>

<pre><code>name: deploy-model
on:
  workflow_dispatch:
    inputs:
      model_version:
        description: 'Model version in registry'
        required: true
  push:
    paths: ['serving/**', 'k8s/inference/**']
permissions: { id-token: write, contents: read }

jobs:
  evaluate:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh
          service_account: ml-deployer@my-project.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@v2
      - name: Download model artefacts
        run: gsutil -m cp -r gs://my-model-registry/${{ inputs.model_version }} ./model
      - name: Evaluation gate
        run: |
          python eval/run.py --model ./model --suite holdout-v3 \
            --min-accuracy 0.91 --max-p95-latency-ms 250

  build-serve:
    needs: evaluate
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh
          service_account: ml-deployer@my-project.iam.gserviceaccount.com
      - run: gcloud auth configure-docker us-central1-docker.pkg.dev
      - name: Build inference image
        run: |
          docker buildx build --platform linux/amd64 \
            --tag us-central1-docker.pkg.dev/my-project/ml/serving:${{ inputs.model_version }} \
            --push -f serving/Dockerfile .

  promote:
    needs: build-serve
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { repository: acme/config, token: ${{ secrets.CONFIG_REPO_PAT }} }
      - name: Bump InferenceService image
        run: |
          yq -i '.spec.predictor.containers[0].image = "us-central1-docker.pkg.dev/my-project/ml/serving:${{ inputs.model_version }}"' \
            inference/values.yaml
      - run: |
          git config user.email gha@noreply
          git config user.name 'GitHub Actions'
          git commit -am "Promote model ${{ inputs.model_version }}"
          git push
</code></pre>

<p>KServe&rsquo;s <code>InferenceService</code> describes the model with a <strong>canary</strong> spec that splits traffic between the previous and new model. GPU nodes are provisioned via <strong>Karpenter</strong> NodePool with <code>g2-standard-8</code> or <code>a3-highgpu-1g</code>, taints applied so only GPU workloads schedule there.</p>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Choice</th><th>Win</th><th>Cost</th></tr>
<tr><td>KServe</td><td>Standard CRD, model-server agnostic, canary built in</td><td>Slightly more complex than raw Deployment</td></tr>
<tr><td>vLLM (for LLMs)</td><td>PagedAttention, continuous batching, OpenAI-compatible API</td><td>GPU memory tuning is fiddly</td></tr>
<tr><td>WIF over JSON keys</td><td>No long-lived secrets in GitHub</td><td>Initial pool/provider setup is intricate</td></tr>
<tr><td>Argo CD GitOps</td><td>Cluster always matches Git; rollback = git revert</td><td>Two-step deploy (PR &rarr; sync)</td></tr>
<tr><td>Evaluation gate in CI</td><td>Bad model never reaches a canary</td><td>Eval suite must be representative</td></tr>
</table>

<p><strong>Production polish:</strong> wire <strong>Evidently AI</strong> or <strong>NannyML</strong> for drift detection &mdash; both prediction drift and feature drift &mdash; with alerts to Slack and an automated rollback hook into Argo CD. Add <strong>shadow inference</strong> so the new model scores live traffic without affecting users, then compare distributions. For LLMs specifically, run <strong>regression evals</strong> (Promptfoo, LangSmith) on each deploy with a fixed prompt set so prompt-level quality is part of the gate. Cost guard rail: a <strong>VPA in Off mode</strong> recommends GPU sizing changes, and <strong>Karpenter consolidation</strong> packs GPU pods tightly so you&rsquo;re not paying for idle accelerators. Finally, sign model artefacts and container images with <strong>Cosign</strong> &mdash; ML supply chain is an emerging attack surface, and provenance over training data + weights is increasingly demanded by EU AI Act compliance.</p>'''

ANSWERS[99] = r'''<p><strong>Situation:</strong> a SaaS team runs a <strong>multi-tenant application</strong> on Kubernetes &mdash; one codebase, many customer organisations &mdash; with strict requirements for <strong>tenant isolation</strong>, <strong>per-tenant scaling</strong>, and <strong>blast-radius control</strong> when shipping changes. CI/CD must accommodate all three.</p>

<p><strong>Approach:</strong> pick a tenancy model first &mdash; <strong>namespace-per-tenant</strong> (shared cluster, RBAC + NetworkPolicy + ResourceQuota), <strong>cluster-per-tenant</strong> (full isolation, highest cost), or <strong>vCluster-per-tenant</strong> (virtual clusters, balanced). Most B2B SaaS lands on namespace-per-tenant with strong defaults; high-compliance shops use vCluster or full clusters. Use <strong>Argo CD ApplicationSets</strong> to project the same app across all tenants from one template, then ship <strong>progressive rollouts</strong> per tenant tier (canary tenants first, then GA wave).</p>

<pre><code># ApplicationSet: one App per tenant, generated from a tenants/ folder
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: saas-app, namespace: argocd }
spec:
  generators:
    - git:
        repoURL: https://github.com/acme/config
        revision: HEAD
        directories:
          - path: tenants/*
  template:
    metadata:
      name: 'app-{{path.basename}}'
    spec:
      project: saas
      source:
        repoURL: https://github.com/acme/config
        targetRevision: HEAD
        path: '{{path}}'
        helm:
          valueFiles: [ 'values.yaml' ]
      destination:
        server: 'https://kubernetes.default.svc'
        namespace: 'tenant-{{path.basename}}'
      syncPolicy:
        automated: { selfHeal: true, prune: true }
        syncOptions: [ CreateNamespace=true, ServerSideApply=true ]
</code></pre>

<p>Each tenant folder holds its own <code>values.yaml</code> (resource limits, feature flags, domain). The Helm chart includes per-tenant defaults: a <strong>ResourceQuota</strong>, <strong>LimitRange</strong>, default-deny <strong>NetworkPolicy</strong>, dedicated <strong>ServiceAccount</strong>, and Pod Security Admission set to <code>restricted</code>. Karpenter NodePools can be tagged so high-tier tenants land on dedicated nodes via taints + tolerations.</p>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Tenancy</th><th>Isolation</th><th>Cost</th><th>Best for</th></tr>
<tr><td>Namespace-per-tenant</td><td>Soft (RBAC + NetworkPolicy + Quotas)</td><td>Low (shared control plane)</td><td>Most SaaS</td></tr>
<tr><td>vCluster-per-tenant</td><td>Hard (separate API server + etcd)</td><td>Medium</td><td>Mid-compliance or noisy neighbour issues</td></tr>
<tr><td>Cluster-per-tenant</td><td>Full</td><td>High</td><td>Regulated industries, sovereign data</td></tr>
<tr><td>Capsule operator</td><td>Tenant CRD wraps namespaces, simplifies governance</td><td>Operator overhead</td><td>Many tenants, want self-service onboarding</td></tr>
</table>

<p>For CI/CD specifically:</p>

<table>
<tr><th>Concern</th><th>Implementation</th></tr>
<tr><td>Schema migrations</td><td>Per-tenant DB &mdash; run migrations as a Job in tenant namespace; track per-tenant version</td></tr>
<tr><td>Feature flags</td><td>OpenFeature + Flagsmith/Unleash; flag changes don&rsquo;t require deploys</td></tr>
<tr><td>Rollout waves</td><td>Canary tenants (small, opt-in) &rarr; GA wave; Kargo Stages for promotion</td></tr>
<tr><td>Per-tenant config</td><td>External Secrets Operator pulls per-tenant secrets from Vault/AWS SM</td></tr>
<tr><td>Noisy neighbours</td><td>ResourceQuota + LimitRange + priority classes; topology spread</td></tr>
</table>

<p><strong>Production polish:</strong> instrument with <strong>per-tenant Prometheus labels</strong> so dashboards and alerts attribute usage and errors correctly &mdash; without this, on-call gets paged for &ldquo;errors&rdquo; that are actually one bad tenant. Use <strong>OpenCost</strong> to break down cluster spend by namespace so finance can attribute COGS per customer. For data plane isolation, run a <strong>Cilium NetworkPolicy</strong> at L7 (FQDN egress allow-lists, no east-west by default) and verify with <strong>Hubble</strong>. Onboarding/offboarding: write a tenant lifecycle operator that creates/deletes a Git folder in the config repo; ApplicationSet picks up the change automatically. For data residency, pair the multi-tenant app with <strong>region-specific clusters</strong> federated via Argo CD ApplicationSets with cluster generators &mdash; that&rsquo;s how you serve EU/US/IN customers from in-region clusters from one codebase.</p>'''

ANSWERS[100] = r'''<p><strong>Situation:</strong> an ML platform team wants to apply the same <strong>code quality and security rigour</strong> to model code, training pipelines, and inference services as they do to any application &mdash; lint, type-check, unit-test, security-scan, model-evaluate, all gated through <strong>GitHub Actions</strong>.</p>

<p><strong>Approach:</strong> treat ML code as code &mdash; same Python linting and typing rigour &mdash; but add ML-specific gates: <strong>data validation</strong> (Great Expectations, Pandera), <strong>model evaluation</strong> on a held-out set, <strong>fairness/bias checks</strong> (Fairlearn), <strong>model artefact security</strong> (model signing, supply-chain attestation), and <strong>prompt regression</strong> for LLM use. Quality gates run in parallel; the slowest path defines critical path.</p>

<pre><code>name: ml-quality
on:
  pull_request:
  push: { branches: [main] }
permissions: { contents: read, security-events: write, pull-requests: write }

jobs:
  code-quality:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy src/
      - run: uv run pytest -q --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v5

  data-validation:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen
      - run: uv run python -m great_expectations checkpoint run training-data-checkpoint

  security:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: python }
      - uses: github/codeql-action/analyze@v3
      - uses: returntocorp/semgrep-action@v1
        with: { config: 'p/python p/security-audit p/ml-security' }
      - name: OSV-Scanner (incl. PyTorch, transformers CVEs)
        uses: google/osv-scanner-action@v1
      - name: Pickle file scan
        run: |
          pip install picklescan
          picklescan --path models/ --recursive

  model-eval:
    runs-on: ubuntu-24.04-gpu
    if: contains(github.event.pull_request.labels.*.name, 'model-change')
    steps:
      - uses: actions/checkout@v4
        with: { lfs: true }
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen
      - run: |
          uv run python eval/run.py \
            --model-path models/candidate \
            --baseline models/production \
            --regression-threshold 0.02 \
            --fairness-check
      - uses: actions/upload-artifact@v4
        with:
          name: eval-report
          path: eval/report.html

  prompt-regression:
    runs-on: ubuntu-24.04
    if: contains(github.event.pull_request.changed_files, 'prompts/')
    steps:
      - uses: actions/checkout@v4
      - uses: promptfoo/promptfoo-action@v1
        with:
          prompts: prompts/
          providers: providers.yaml
          tests: tests/prompts.yaml
</code></pre>

<p><strong>Trade-offs:</strong></p>

<table>
<tr><th>Gate</th><th>Catches</th><th>Cost</th></tr>
<tr><td>Ruff + mypy</td><td>Style, type errors, common bugs</td><td>~5 s; near-free</td></tr>
<tr><td>Great Expectations / Pandera</td><td>Schema drift, null surges, range violations</td><td>Suite design effort</td></tr>
<tr><td>CodeQL + Semgrep (ML rules)</td><td>SQL/SSRF/path injection; ML-specific patterns (unsafe pickle, model deserialisation)</td><td>5&ndash;10 min CodeQL</td></tr>
<tr><td>picklescan</td><td>Malicious code embedded in serialised model files</td><td>~1 s; high value</td></tr>
<tr><td>Model eval with baseline + fairness</td><td>Regression vs prod; demographic disparate impact</td><td>GPU minutes</td></tr>
<tr><td>Promptfoo prompt regression</td><td>Drift in LLM behaviour from prompt edits</td><td>API costs per test</td></tr>
<tr><td>OSV-Scanner</td><td>PyTorch, transformers, vLLM CVEs</td><td>~10 s</td></tr>
</table>

<p><strong>Production polish:</strong> add <strong>model card</strong> generation as a required artefact &mdash; auto-populated from eval results with metrics, fairness slice analysis, intended use, and limitations. Sign final model files with <strong>Cosign</strong> and store SBOMs that include <em>dataset</em> versions (not just package versions) &mdash; lineage matters for EU AI Act and similar regimes. For LLMs specifically, run <strong>guardrails</strong> tests (toxicity, PII leakage, prompt injection resistance via Garak or PyRIT) in the CI flow. For long-term safety, instrument the deployed model with <strong>NannyML</strong> or <strong>Evidently AI</strong> so production drift triggers a regression CI run that compares current vs baseline distribution &mdash; closing the loop between training-time quality and serving-time reality. Finally, treat model promotion as a <strong>change-controlled deployment</strong>: model version bumps are PRs in the config repo, signed and reviewed, with Argo CD applying them &mdash; the same audit-trail discipline you&rsquo;d apply to a database schema change.</p>'''
