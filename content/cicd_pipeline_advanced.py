# CI/CD Pipeline — Advanced
# Mechanism-focused prose, internals + trade-off tables, 2026-current libraries.
# Style: 100-180 words, ~2,000-3,500 chars per answer.

ANSWERS: dict[int, str] = {}


ANSWERS[1] = r'''<p>Blue/green keeps two identical production environments &mdash; <em>blue</em> serves traffic while <em>green</em> receives the new version &mdash; and flips traffic in one atomic step. On Kubernetes the mechanism is a <strong>Service selector swap</strong>: two Deployments (<code>app=api,version=blue</code> and <code>app=api,version=green</code>) sit behind one Service whose selector currently points at <code>version=blue</code>. After green&rsquo;s pods are <em>Ready</em> and smoke-tested, you patch the selector to <code>version=green</code> and the kube-proxy / Ingress controller routes new connections instantly. Existing connections drain naturally.</p>
<table>
<thead><tr><th>Approach</th><th>Mechanism</th><th>When to pick</th></tr></thead>
<tbody>
<tr><td>Service selector swap</td><td>Patch one label on the Service</td><td>Single-region, simple stateless apps</td></tr>
<tr><td>Ingress weight (NGINX, Traefik)</td><td>Two Services, weighted routes</td><td>Need partial cutover or quick fallback</td></tr>
<tr><td>Argo Rollouts BlueGreen</td><td>Custom resource manages two ReplicaSets + preview Service + active Service</td><td>Production standard in 2026 &mdash; gives analysis runs, automated promotion, instant rollback</td></tr>
<tr><td>Service mesh (Istio, Linkerd)</td><td>VirtualService with subsets</td><td>Already running a mesh; need mTLS + observability per subset</td></tr>
</tbody>
</table>
<p><strong>Trade-offs:</strong> doubles compute cost during the switch (both colours running); database schema must be backward-compatible because both versions read/write concurrently for seconds-to-minutes; rollback is the same flip in reverse, so MTTR is near-zero. <strong>2026 default:</strong> Argo Rollouts with a <code>BlueGreenStrategy</code> &mdash; auto-promotion gated by Prometheus queries, plus <code>scaleDownDelaySeconds</code> for safe rollback windows.</p>
'''


ANSWERS[2] = r'''<p>Canary deployment routes a small percentage of live traffic to a new version, monitors signals (errors, latency, business metrics), and either promotes or aborts. In Jenkins the orchestration sits in a <code>Jenkinsfile</code>; the actual traffic-shifting happens in the platform (K8s + Argo Rollouts, or a service mesh, or a load balancer with weighted targets) &mdash; Jenkins is the conductor.</p>
<table>
<thead><tr><th>Stage</th><th>What Jenkins does</th></tr></thead>
<tbody>
<tr><td>Build</td><td><code>docker build</code> + push tagged image</td></tr>
<tr><td>Deploy canary</td><td><code>kubectl argo rollouts set image</code> or <code>helm upgrade</code> with canary values</td></tr>
<tr><td>Analyse</td><td>Query Prometheus / Datadog for error rate, p95 latency, RPS over a 10-min window</td></tr>
<tr><td>Decide</td><td>Promote (<code>kubectl argo rollouts promote</code>) or abort (<code>... abort</code>)</td></tr>
</tbody>
</table>
<p><strong>Modern stack (2026):</strong> Jenkins triggers, <strong>Argo Rollouts</strong> owns traffic shifting, and an <code>AnalysisTemplate</code> declares pass/fail thresholds. The Rollout resource auto-progresses through weight steps (<code>5% &rarr; 25% &rarr; 50% &rarr; 100%</code>) with pauses gated by analysis. Failures auto-rollback. Jenkins&rsquo;s only job becomes <em>"start the rollout, watch its status, fail the pipeline on abort"</em>.</p>
<p><strong>Anti-patterns:</strong> shifting weight via raw <code>kubectl scale</code> ratios &mdash; this works only for round-robin services and breaks with sticky sessions. Always shift at the routing layer (mesh / Ingress / Rollouts), not by replica count.</p>
'''


ANSWERS[3] = r'''<p>GitHub Actions manages IaC by treating Terraform / OpenTofu / Pulumi state as the source of truth and running plan/apply through workflows. The repository holds the desired state; PR runs <code>plan</code> and posts the diff as a comment; merge to <code>main</code> triggers <code>apply</code> behind a protected environment with required reviewers.</p>
<table>
<thead><tr><th>Concern</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Auth to cloud</td><td>OIDC federation (<code>id-token: write</code>) &mdash; <code>aws-actions/configure-aws-credentials</code>, <code>google-github-actions/auth</code>; <strong>no long-lived keys</strong></td></tr>
<tr><td>State backend</td><td>S3 + DynamoDB lock, GCS + lockfile, or Terraform Cloud / Spacelift / Env0 (managed runners with state, drift detection, policy)</td></tr>
<tr><td>Plan visibility</td><td><code>hashicorp/setup-terraform</code> + <code>terraform-plan-comment</code> action posts diff to PR</td></tr>
<tr><td>Policy</td><td>OPA / Conftest / Checkov / Trivy IaC scanning in the plan job</td></tr>
<tr><td>Drift</td><td>Nightly scheduled <code>terraform plan -detailed-exitcode</code>; non-zero opens a Slack alert</td></tr>
</tbody>
</table>
<p><strong>2026 ecosystem:</strong> <strong>OpenTofu</strong> has largely supplanted Terraform OSS after the BUSL relicense, with the same workflow shape. <strong>Pulumi</strong> uses the same plan/apply on real programming languages with stronger typing. <strong>Atlantis</strong> and <strong>Spacelift</strong> offer hosted Terraform-as-a-platform on top of GitHub Actions for richer policy + queueing.</p>
<p><strong>Trade-off:</strong> running <code>apply</code> on GitHub-hosted runners means cloud credentials (even short-lived OIDC) flow through GitHub-controlled infrastructure. High-security shops use self-hosted runners in private subnets, or fully delegate apply to Spacelift / TFC.</p>
'''


ANSWERS[4] = r'''<p>Securing Docker in CI/CD spans build-time, image-time, and runtime concerns. The core mechanism is <strong>shifting trust left</strong>: scan during build, sign before push, verify before run.</p>
<table>
<thead><tr><th>Stage</th><th>Tool</th><th>What it does</th></tr></thead>
<tbody>
<tr><td>Base image</td><td>Distroless / Chainguard / Wolfi / chiseled Ubuntu</td><td>Removes shells, package managers, CVE surface</td></tr>
<tr><td>Build</td><td>BuildKit + multi-stage</td><td>Drops build deps; non-root <code>USER</code> in final stage</td></tr>
<tr><td>Vuln scan</td><td><strong>Trivy</strong>, Grype, Snyk</td><td>CVE database lookup against image layers + lockfiles</td></tr>
<tr><td>Secrets scan</td><td>gitleaks, trufflehog, Trivy <code>--scanners secret</code></td><td>Catches embedded keys before push</td></tr>
<tr><td>SBOM</td><td>Syft, <code>docker sbom</code></td><td>Generates SPDX/CycloneDX inventory</td></tr>
<tr><td>Sign</td><td><strong>Cosign</strong> (Sigstore)</td><td>Keyless OIDC signature stored in registry</td></tr>
<tr><td>Provenance</td><td>SLSA Level 3+</td><td>Tamper-evident build attestation</td></tr>
<tr><td>Admission</td><td>Kyverno / Sigstore policy-controller / Connaisseur</td><td>K8s rejects unsigned or unscanned images at admission</td></tr>
</tbody>
</table>
<p><strong>2026 baseline:</strong> Cosign keyless signing + SLSA provenance + Kyverno cluster policy that enforces <em>only signatures from this OIDC issuer + this workflow are admitted</em>. Add <strong>Falco</strong> at runtime for syscall-level intrusion detection.</p>
<p><strong>Common pitfall:</strong> running scanners but never failing the build on findings. Set severity gates (<code>--exit-code 1 --severity HIGH,CRITICAL</code>) and an exception process via labels in the manifest, not "we&rsquo;ll fix it next sprint" tickets.</p>
'''


ANSWERS[5] = r'''<p>Infrastructure as Code defines servers, networks, IAM, DNS, and managed services as version-controlled declarative files. The runtime engine (Terraform/OpenTofu/Pulumi/CloudFormation/CDK) computes a diff between desired state (the code) and actual state (the cloud APIs), then converges. CI/CD value comes from coupling that engine to the same review/test/release pipeline as application code.</p>
<table>
<thead><tr><th>Benefit</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Reproducibility</td><td>Same code &rarr; same infra in dev/staging/prod (with workspace overrides)</td></tr>
<tr><td>Reviewability</td><td>Plan diff posted on PR; approvals are auditable</td></tr>
<tr><td>Disaster recovery</td><td>Lost region rebuilt by re-running apply against a fresh backend</td></tr>
<tr><td>Drift detection</td><td>Scheduled plan runs surface manual changes</td></tr>
<tr><td>Policy as code</td><td>OPA / Sentinel / Checkov gates risky changes pre-apply</td></tr>
</tbody>
</table>
<p><strong>2026 landscape:</strong> <strong>OpenTofu</strong> for OSS Terraform-compatible workflows; <strong>Pulumi</strong> for typed programming languages; <strong>CDKTF / AWS CDK</strong> for synth-to-Terraform/CloudFormation flows. Managed runners (Spacelift, Env0, Terraform Cloud) handle queueing, drift, and cost estimation. <strong>Crossplane</strong> brings IaC <em>into</em> Kubernetes as CRDs for teams already on a K8s control plane.</p>
<p><strong>Pitfalls:</strong> monolithic state files (one PR can break unrelated infra), state stored in a single account without backups, mixing manual <code>console-clicks</code> with code (drift becomes irrecoverable). Split state by blast radius, lock backends, and ban console writes via SCPs.</p>
'''


ANSWERS[6] = r'''<p>Jenkins Shared Libraries are reusable Groovy code that pipelines load at runtime, eliminating copy-paste across <code>Jenkinsfile</code>s. The library is its own Git repository with a fixed layout: <code>vars/</code> for global step functions (each <code>vars/foo.groovy</code> exposes <code>foo()</code> as a pipeline step), <code>src/</code> for classes following Java/Groovy package conventions, and <code>resources/</code> for non-Groovy assets (templates, configs).</p>
<table>
<thead><tr><th>Layer</th><th>Used for</th></tr></thead>
<tbody>
<tr><td><code>vars/buildAndPush.groovy</code></td><td>One-liner steps: <code>buildAndPush image: 'foo', tag: 'v1'</code></td></tr>
<tr><td><code>src/com/acme/Notifier.groovy</code></td><td>Stateful classes (Slack, Jira clients)</td></tr>
<tr><td><code>resources/Dockerfile.tpl</code></td><td>Templates loaded via <code>libraryResource()</code></td></tr>
</tbody>
</table>
<p><strong>Loading:</strong> globally in <em>Manage Jenkins &rarr; Configure System &rarr; Global Pipeline Libraries</em>, or per-pipeline with <code>@Library('acme-shared@v3.2') _</code>. Pin to tags for reproducibility; <code>@main</code> creates a moving target.</p>
<p><strong>Trust model:</strong> globally configured libraries run in <em>trusted</em> mode (no script approval needed); per-job libraries are sandboxed. Untrusted libraries hit Groovy script approval, which is why CI admins ship hardened libraries globally and keep app teams out of approval queues.</p>
<p><strong>2026 advice:</strong> shared libraries are still the right answer for orgs on Jenkins, but new teams increasingly skip Jenkins entirely &mdash; <strong>GitHub Actions reusable workflows</strong> + composite actions, <strong>Tekton</strong>, or <strong>Dagger</strong> (code-defined CI in TypeScript/Go/Python) cover the same reuse story without Groovy. Migrate when business cases align.</p>
'''


ANSWERS[7] = r'''<p>Microservice CI/CD on K8s + Docker hinges on three architectural choices: <em>per-service repos vs monorepo</em>, <em>per-service vs shared pipelines</em>, and <em>orchestration of cross-service contracts</em>. The mechanism is independent service deployability with shared platform guardrails.</p>
<table>
<thead><tr><th>Concern</th><th>Pattern</th></tr></thead>
<tbody>
<tr><td>Pipeline per service</td><td>Each service has a <code>Dockerfile</code> + <code>Chart/</code> (Helm) or <code>kustomization/</code>. CI builds + pushes to registry tagged by SHA.</td></tr>
<tr><td>Deploy</td><td><strong>Argo CD / Flux</strong> watches a config repo; CI updates image tags via PR or <code>argocd app set</code>; controller reconciles.</td></tr>
<tr><td>Contracts</td><td>Schema registry (Buf for protobuf, JSON Schema for REST); consumer-driven contract tests (Pact) gate merges.</td></tr>
<tr><td>Cross-service tests</td><td>Ephemeral preview envs per PR (vCluster, kind, Argo CD ApplicationSets) running the full graph.</td></tr>
<tr><td>Observability</td><td>OpenTelemetry traces tie deploys to error spikes; SLO dashboards drive auto-rollback (Argo Rollouts + Prometheus).</td></tr>
</tbody>
</table>
<p><strong>2026 stack:</strong> Argo CD ApplicationSets generate one Argo Application per service from a template; <strong>Argo Rollouts</strong> handles per-service progressive delivery; <strong>Backstage</strong> exposes a developer portal so teams self-serve new services. <strong>Dapr</strong> sidecars give consistent service-to-service comms (retries, mTLS, observability) without bespoke code.</p>
<p><strong>Anti-pattern:</strong> shared release trains for "the platform" &mdash; that recreates monolith coupling. Each service ships when its tests pass; the platform team owns the roads, not the cars.</p>
'''


ANSWERS[8] = r'''<p>GitOps manages Kubernetes by treating a Git repository as the <em>single source of truth</em> for cluster state. A controller running in-cluster continuously reconciles the live cluster toward the manifests in Git. <code>kubectl apply</code> from a developer&rsquo;s laptop is forbidden; all changes go through PRs.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Config repo</td><td>YAML / Helm / Kustomize for every namespace</td></tr>
<tr><td>Controller (Argo CD or Flux)</td><td>Polls or webhooks the repo, diffs, applies</td></tr>
<tr><td>Image updater</td><td>Argo CD Image Updater / Flux Image Automation Controller writes new image tags back to the config repo</td></tr>
<tr><td>App-of-apps / ApplicationSets</td><td>Templates one Application per service or environment</td></tr>
</tbody>
</table>
<p><strong>Pull vs push:</strong> the controller <em>pulls</em> from Git into the cluster; CI <em>pushes</em> only into Git. This means cluster credentials never leave the cluster, which is the security win. CI doesn&rsquo;t need <code>kubectl</code> access to prod.</p>
<p><strong>Argo CD vs Flux (2026):</strong> Argo CD has the richer UI, ApplicationSets, sync waves, and is the more popular default. Flux is more modular (image automation, Helm controller, Kustomize controller as separate operators), composes well with crossplane, and is favoured in CNCF/OSS-purist setups.</p>
<p><strong>Trade-off:</strong> drift is now a controller decision &mdash; manual hotfixes on the cluster get reverted within seconds. That&rsquo;s the feature, not the bug, but operators must accept that emergency changes happen via PR + auto-merge, not <code>kubectl edit</code>.</p>
'''


ANSWERS[9] = r'''<p>Docker multi-stage builds let one <code>Dockerfile</code> declare multiple <code>FROM</code> stages, each with its own base image, and <code>COPY --from=&lt;stage&gt;</code> pulls artefacts forward. The final image only contains what the last stage explicitly copies; toolchains, source code, build caches stay in earlier stages and never ship.</p>
<table>
<thead><tr><th>Without multi-stage</th><th>With multi-stage</th></tr></thead>
<tbody>
<tr><td>1.2 GB Node image with <code>npm</code>, dev deps, source</td><td>~120 MB final &mdash; only built artefacts + production deps</td></tr>
<tr><td>JDK in production for a Spring Boot jar</td><td>JRE-only (or distroless) final stage</td></tr>
<tr><td>build-essential / gcc shipped to prod</td><td>Compiled binary on <code>distroless/static</code></td></tr>
</tbody>
</table>
<p><strong>CI/CD benefits:</strong></p>
<ul>
<li><strong>Smaller images</strong> &mdash; faster pulls during rolling deploys, cheaper registry storage.</li>
<li><strong>Reduced CVE surface</strong> &mdash; fewer packages = fewer CVEs in the scan report.</li>
<li><strong>Better caching</strong> with BuildKit: each stage is independently cached; changing source doesn&rsquo;t re-download deps.</li>
<li><strong>Reproducibility</strong> &mdash; pin every <code>FROM</code> to a digest (<code>node:20-alpine@sha256:&hellip;</code>).</li>
<li><strong>Parallel stages</strong> &mdash; BuildKit builds independent stages concurrently.</li>
</ul>
<p><strong>2026 patterns:</strong> use <code>--mount=type=cache</code> for package manager caches that survive across builds; use <code>--mount=type=secret</code> for build-time credentials that never become layers; use <strong>Buildx + GHA cache backend</strong> (<code>type=gha</code>) so cache survives across CI runs. For non-Dockerfile builds, <strong>Cloud Native Buildpacks</strong> (Paketo, Heroku) give multi-stage benefits without writing a Dockerfile.</p>
'''


ANSWERS[10] = r'''<p>GitHub Actions secret management has three concentric scopes, plus a fourth integration pattern for cloud-native secrets.</p>
<table>
<thead><tr><th>Scope</th><th>Use case</th></tr></thead>
<tbody>
<tr><td>Repository secrets</td><td>Per-repo values (test API keys, build tokens)</td></tr>
<tr><td>Environment secrets</td><td>Gated per environment (<code>production</code>) with required reviewers + branch rules</td></tr>
<tr><td>Organisation secrets</td><td>Shared across selected repos (e.g. shared registry credentials)</td></tr>
<tr><td>External secret stores</td><td>Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager pulled at runtime</td></tr>
</tbody>
</table>
<p><strong>How they work:</strong> secrets are encrypted at rest with libsodium, decrypted only into the runner process, and masked in logs (any string matching a registered secret is replaced with <code>***</code>). They are never available to workflows triggered by <code>pull_request</code> from forks &mdash; this prevents drive-by exfiltration.</p>
<p><strong>Modern pattern (2026):</strong> the <em>only</em> secret in GitHub should be the OIDC trust relationship. Cloud creds, DB passwords, and registry tokens are fetched at runtime via OIDC federation:</p>
<ul>
<li><strong>AWS:</strong> <code>aws-actions/configure-aws-credentials@v4</code> with <code>role-to-assume</code> + <code>id-token: write</code>.</li>
<li><strong>GCP:</strong> Workload Identity Federation via <code>google-github-actions/auth</code>.</li>
<li><strong>Azure:</strong> federated credential on a managed identity.</li>
<li><strong>Vault:</strong> <code>hashicorp/vault-action</code> exchanges the OIDC token for short-lived secrets.</li>
</ul>
<p><strong>Hardening:</strong> require environments + reviewers for production deploys, scope OIDC subject claims to <code>repo:org/repo:ref:refs/heads/main</code>, audit secret use via the <em>workflow run</em> tab, and rotate any static secret on a schedule. Tools like <strong>Doppler</strong>, <strong>Infisical</strong>, and <strong>1Password Secrets Automation</strong> centralise secret distribution if you outgrow native scopes.</p>
'''


ANSWERS[11] = r'''<p>Kubernetes DR is a layered plan covering <em>etcd state</em>, <em>application data</em>, and <em>control-plane recoverability</em>. Each layer has its own RTO/RPO target.</p>
<table>
<thead><tr><th>Layer</th><th>Mechanism</th><th>Tool (2026)</th></tr></thead>
<tbody>
<tr><td>etcd</td><td>Encrypted snapshots to S3, hourly + on-demand</td><td><code>etcdctl snapshot save</code> in CronJob, or managed control plane (EKS/AKS/GKE handles this)</td></tr>
<tr><td>Cluster manifests</td><td>GitOps repo is the source of truth</td><td>Argo CD ApplicationSets &mdash; rebuild cluster by pointing controller at repo</td></tr>
<tr><td>Persistent volumes</td><td>Volume snapshots to object storage; CSI VolumeSnapshot CRD</td><td><strong>Velero</strong> + CSI driver, or <strong>Kasten K10</strong>, or <strong>TrilioVault</strong></td></tr>
<tr><td>App data (DBs)</td><td>Database-native backup (RDS PITR, MongoDB Atlas continuous backup, pg_basebackup + WAL)</td><td>Managed services preferred; self-hosted needs <strong>Velero hooks</strong> or <strong>operator backups</strong> (CloudNativePG, percona-server-mongodb-operator)</td></tr>
<tr><td>DNS &amp; ingress</td><td>External DNS records pointing to standby region</td><td>Route53 health-check failover, ExternalDNS controller</td></tr>
</tbody>
</table>
<p><strong>Strategies (RTO/RPO trade-off):</strong></p>
<ul>
<li><strong>Pilot light</strong> &mdash; standby cluster with infra but no workload; restore Velero on disaster. RTO hours, cheap.</li>
<li><strong>Warm standby</strong> &mdash; standby cluster running scaled-down workload + replicating data. RTO minutes.</li>
<li><strong>Active-active</strong> &mdash; multi-region with global load balancer + cross-region replication (e.g. Aurora Global Database). RTO seconds, expensive.</li>
</ul>
<p><strong>Test the plan:</strong> a DR plan you haven&rsquo;t rehearsed in 6 months is a fiction. Quarterly <em>Game Days</em> that delete the prod cluster and recover from backups are how mature teams keep RTOs honest.</p>
'''


ANSWERS[12] = r'''<p>A multibranch pipeline auto-discovers branches/PRs in a repo and creates one Jenkins job per branch from a <code>Jenkinsfile</code> at the branch&rsquo;s root. The mechanism is the <em>Multibranch Pipeline</em> project type plus a <em>SCM source</em> (GitHub Branch Source, Bitbucket, GitLab) that scans the repo on a schedule or via webhook.</p>
<table>
<thead><tr><th>Mechanism</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Discovery</td><td>SCM source lists branches matching include/exclude patterns; PRs become "PR-123" jobs</td></tr>
<tr><td>Per-branch <code>Jenkinsfile</code></td><td>Each branch can evolve its own pipeline; merging brings the change into <code>main</code></td></tr>
<tr><td>Branch-specific logic</td><td><code>when { branch 'main' }</code> for prod-only stages; <code>when { changeRequest target: 'main' }</code> for PR-only</td></tr>
<tr><td>Lifecycle</td><td>Deleted branch &rarr; job auto-removed (after orphan retention window)</td></tr>
</tbody>
</table>
<p><strong>Typical <code>Jenkinsfile</code> layout:</strong></p>
<ul>
<li>Always: lint, unit tests, build, container scan.</li>
<li>PR only: deploy to ephemeral preview env (<code>kubectl apply -k overlays/preview-${env.CHANGE_ID}</code>); post URL as a PR comment.</li>
<li><code>main</code>: build immutable artefact, push to registry, trigger Argo CD sync or Helm upgrade to staging; gated approval to prod.</li>
<li>Tags (<code>when { buildingTag() }</code>): release pipeline.</li>
</ul>
<p><strong>2026 reality:</strong> multibranch pipelines remain Jenkins&rsquo;s strongest feature, but most green-field teams replicate the pattern with <strong>GitHub Actions matrix + path filters</strong> or <strong>Buildkite/CircleCI</strong> dynamic pipelines. The branch-job-per-PR concept is identical; the implementation is YAML rather than Groovy.</p>
'''


ANSWERS[13] = r'''<p>HashiCorp Vault centralises secret issuance: instead of CI storing static credentials, it authenticates to Vault and receives short-lived dynamic secrets scoped to the job.</p>
<table>
<thead><tr><th>Mechanism</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Auth method</td><td><strong>JWT/OIDC</strong> &mdash; CI provider issues a signed token (GitHub OIDC, GitLab JWT); Vault verifies it against the IdP&rsquo;s JWKS and binds claims to a Vault role</td></tr>
<tr><td>Dynamic backends</td><td><code>database/creds/&lt;role&gt;</code> generates per-deploy DB users with TTL; <code>aws/creds/&lt;role&gt;</code> mints temporary AWS keys; <code>pki/issue</code> issues short-lived TLS certs</td></tr>
<tr><td>KV v2</td><td>Static secrets with versioning, soft-delete, deletion protection</td></tr>
<tr><td>Transit</td><td>Encryption-as-a-service &mdash; data never leaves the app, Vault never sees plaintext</td></tr>
</tbody>
</table>
<p><strong>CI flow (GitHub Actions example):</strong> workflow requests an OIDC token, exchanges it via <code>hashicorp/vault-action</code> for a Vault token bound to a role like <code>ci-deploy-prod</code>, then reads (or generates) just the secrets that role permits. TTL is minutes, not days.</p>
<p><strong>Trade-offs &amp; alternatives (2026):</strong></p>
<ul>
<li><strong>Vault Enterprise / HCP Vault</strong> &mdash; managed, multi-region replication, performance standby.</li>
<li><strong>OpenBao</strong> &mdash; LF-stewarded fork of Vault after the BUSL relicense; same APIs.</li>
<li><strong>Cloud-native</strong> &mdash; AWS Secrets Manager + IAM, Azure Key Vault + managed identity, GCP Secret Manager + WIF. Simpler, cloud-locked.</li>
<li><strong>Infisical / Doppler / 1Password Secrets Automation</strong> &mdash; SaaS alternatives focused on developer UX; lighter than Vault, less powerful for dynamic secrets.</li>
</ul>
<p><strong>Hardening:</strong> bind roles to specific OIDC subject claims (repo + ref + workflow), enable audit logs to a tamper-evident sink, never expose root tokens in CI, and rotate Vault unseal keys annually.</p>
'''


ANSWERS[14] = r'''<p>Docker build optimisation in CI hinges on <em>cache reuse</em>, <em>layer ordering</em>, and <em>build parallelism</em>. With BuildKit, three mechanisms dominate.</p>
<table>
<thead><tr><th>Mechanism</th><th>Effect</th></tr></thead>
<tbody>
<tr><td>Layer ordering</td><td>Copy <code>package.json</code> &amp; lockfile, run <code>npm ci</code>, <em>then</em> copy source. Source changes don&rsquo;t bust the dep layer.</td></tr>
<tr><td><code>--mount=type=cache</code></td><td>Persistent cache mounts (<code>/root/.npm</code>, <code>/root/.cargo</code>, <code>/root/.m2</code>) survive across runs; not committed to layers.</td></tr>
<tr><td>Remote cache backends</td><td><code>--cache-from type=gha</code> (GitHub Actions), <code>type=registry</code> (push cache to OCI registry), <code>type=s3</code>. Workers without local cache pull from remote.</td></tr>
<tr><td>Multi-stage parallelism</td><td>Independent stages build concurrently with BuildKit DAG scheduler.</td></tr>
<tr><td>Multi-arch via QEMU vs cross-compile</td><td>Cross-compile (Go, Rust) on a single arch and ship both binaries; QEMU emulation is 5-10&times; slower.</td></tr>
</tbody>
</table>
<p><strong>Practical setup (GitHub Actions):</strong></p>
<ul>
<li><code>docker/setup-buildx-action@v3</code> + <code>docker/build-push-action@v6</code> with <code>cache-from: type=gha</code> + <code>cache-to: type=gha,mode=max</code>.</li>
<li><code>mode=max</code> caches all stages, not just the final image.</li>
<li>Pin base images to digests so cache hits aren&rsquo;t invalidated by upstream tag moves.</li>
<li>Use <code>.dockerignore</code> aggressively &mdash; sending <code>node_modules</code> or <code>.git</code> in context wastes seconds and bloats remote cache.</li>
</ul>
<p><strong>2026 alternatives:</strong> <strong>Depot.dev</strong> and <strong>Docker Build Cloud</strong> offer remote BuildKit with persistent cache and native multi-arch (no QEMU); cuts cold builds from minutes to seconds. <strong>Bazel</strong> and <strong>Earthly</strong> address the same problem at a higher level by making the entire build graph reproducible and cacheable.</p>
'''


ANSWERS[15] = r'''<p>CRDs let you extend the Kubernetes API with new object types that <code>kubectl</code> treats as first-class resources. The CRD itself is a schema (OpenAPI v3); a <strong>controller</strong> (custom code) watches instances of that resource and reconciles cluster state to match. The pair &mdash; CRD + controller &mdash; is called an <em>Operator</em>.</p>
<table>
<thead><tr><th>Concept</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>CRD</td><td>Defines kind/group/versions, OpenAPI schema, scope (Namespaced/Cluster), shortNames, printer columns, validation rules</td></tr>
<tr><td>Custom Resource (CR)</td><td>An instance: <code>kind: Database</code> with <code>spec.engine: postgres</code></td></tr>
<tr><td>Controller</td><td>Long-running pod that lists/watches CRs and converges actual cluster state &mdash; e.g. provisions an RDS instance</td></tr>
<tr><td>Webhooks</td><td>Validating + mutating admission webhooks enforce invariants and inject defaults</td></tr>
</tbody>
</table>
<p><strong>Why CRDs:</strong> they expose domain concepts (Database, Topic, Certificate, GitRepository) at the same abstraction level as <code>Deployment</code>. Users get RBAC, YAML, GitOps, and <code>kubectl</code> semantics for free.</p>
<p><strong>Authoring (2026):</strong> use <strong>kubebuilder</strong> or <strong>Operator SDK</strong> &mdash; both scaffold a Go project with controller-runtime + CRD generation. <strong>Kopf</strong> (Python) and <strong>Metacontroller</strong> (any language via webhooks) are alternatives. <strong>kcl-lang</strong> + <strong>cuelang</strong> are gaining traction for typed CR validation.</p>
<p><strong>Production CRDs to know:</strong> cert-manager (<code>Certificate</code>, <code>Issuer</code>), Argo CD (<code>Application</code>, <code>ApplicationSet</code>), Istio (<code>VirtualService</code>, <code>DestinationRule</code>), Prometheus Operator (<code>ServiceMonitor</code>, <code>PrometheusRule</code>), Crossplane (<code>Composition</code>, <code>XR</code>), Knative (<code>Service</code>, <code>Revision</code>). The CNCF landscape is largely operator-driven now.</p>
'''

ANSWERS[16] = r'''<p>Monorepo CI/CD on GitHub Actions hinges on <strong>change detection</strong> &mdash; only build/test/deploy the services touched by a commit &mdash; combined with shared workflow logic. Three mechanisms cover 90% of cases.</p>
<table>
<thead><tr><th>Mechanism</th><th>Tool</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Path filters</td><td><code>paths:</code> trigger filter or <code>dorny/paths-filter</code> action</td><td>Triggers entire workflows by changed files; coarse but built-in</td></tr>
<tr><td>Affected detection</td><td><code>nx affected</code>, <code>turbo run --filter</code>, Bazel <code>--diff</code>, pnpm <code>--filter</code></td><td>Walks the dep graph; rebuilds only what depends on changed code</td></tr>
<tr><td>Reusable workflows</td><td><code>workflow_call</code> or composite actions</td><td>One canonical "build a service" workflow called per service</td></tr>
</tbody>
</table>
<p><strong>Pattern:</strong> a <em>dispatcher</em> workflow runs on every push, computes the affected service list (Nx, Turborepo, Bazel, or a custom script), and emits a matrix that fans out to <em>per-service</em> reusable workflows. Each service workflow runs the same shape (lint &rarr; test &rarr; build &rarr; image &rarr; deploy) parameterised by service name and Dockerfile path.</p>
<p><strong>2026 stack:</strong></p>
<ul>
<li><strong>Nx / Turborepo</strong> for JS/TS monorepos &mdash; remote caching dramatically cuts CI time.</li>
<li><strong>Bazel / Pants</strong> for polyglot monorepos at scale (tens of millions of LOC); steeper learning curve.</li>
<li><strong>Moon / Lerna-Lite</strong> as lighter alternatives.</li>
<li><strong>Depot remote cache</strong> for cross-CI build caching, language-agnostic.</li>
</ul>
<p><strong>Pitfalls:</strong> path filters that miss transitive deps (changing a shared lib doesn&rsquo;t trigger downstream service builds) &mdash; rely on the build tool&rsquo;s graph, not regex. Caching that includes machine-specific paths bursts the cache for nothing &mdash; standardise runner images. Sequential deploys when services are independent &mdash; use matrix concurrency, not chained <code>needs:</code>.</p>
'''


ANSWERS[17] = r'''<p>Jenkins integrates with external tooling through the Jenkins Plugin API plus webhooks; the architecture is <em>plugin in Jenkins</em> + <em>credentials in Jenkins credential store</em> + <em>steps in the Jenkinsfile</em>.</p>
<table>
<thead><tr><th>Tool</th><th>Plugin</th><th>Capabilities</th></tr></thead>
<tbody>
<tr><td>Slack</td><td>slack-plugin</td><td><code>slackSend(channel: '#ci', message: 'Build failed', color: 'danger')</code>; threads, attachments, blocks</td></tr>
<tr><td>Jira</td><td>jira-plugin / atlassian-jira-software-cloud</td><td>Auto-link issue keys (<code>PROJ-123</code>) in commits to the build; transition issues; post deploy comments</td></tr>
<tr><td>GitHub</td><td>github-branch-source / github-checks</td><td>Push commit-status checks visible on PRs; run multibranch discovery</td></tr>
<tr><td>SonarQube</td><td>sonar-scanner</td><td>Quality gate results posted as PR check; pipeline fails if gate is red</td></tr>
<tr><td>PagerDuty / Opsgenie</td><td>pagerduty-plugin</td><td>Auto-create incidents on red prod builds</td></tr>
</tbody>
</table>
<p><strong>Auth:</strong> Slack uses an OAuth bot token, Jira uses an API token (Atlassian Cloud) or PAT (DC). Store both in the Jenkins Credentials Store as <em>secret text</em>, reference by ID in the Jenkinsfile (<code>credentialsId: 'slack-bot'</code>) so secrets never appear in source.</p>
<p><strong>Webhooks the other direction:</strong> Slack slash commands and Jira automation trigger Jenkins jobs via the <em>Generic Webhook Trigger</em> plugin or the built-in <code>/buildByToken</code> endpoint &mdash; useful for chatops (<code>/deploy staging</code> in Slack).</p>
<p><strong>2026 reality:</strong> teams increasingly drop the plugin sprawl by moving to GitHub Actions / GitLab CI where Slack/Jira integrations are first-party (<code>slackapi/slack-github-action</code>, GitLab&rsquo;s Jira sync), or by routing notifications through a centralised hub (Opslevel, Backstage, Cortex) that subscribes to CI events instead of every job posting directly. Less plugin maintenance, fewer "my Slack credentials are everywhere" headaches.</p>
'''


ANSWERS[18] = r'''<p>RollingUpdate is the default Deployment strategy: pods are replaced incrementally, controlled by <code>maxSurge</code> (extra pods above desired during rollout) and <code>maxUnavailable</code> (pods that may be down). The Deployment controller creates a new ReplicaSet, scales it up while scaling the old one down, and respects readiness probes between steps.</p>
<table>
<thead><tr><th>Field</th><th>Effect</th></tr></thead>
<tbody>
<tr><td><code>maxSurge: 25%</code> / <code>maxUnavailable: 25%</code></td><td>Default; balances speed and capacity</td></tr>
<tr><td><code>maxSurge: 100%</code> / <code>maxUnavailable: 0</code></td><td>Zero-downtime &mdash; doubles capacity briefly; safest</td></tr>
<tr><td><code>maxSurge: 0</code> / <code>maxUnavailable: 1</code></td><td>No extra capacity (resource-constrained); brief downtime per pod</td></tr>
<tr><td><code>readinessProbe</code></td><td>Gates promotion of the new ReplicaSet &mdash; failing probe halts rollout</td></tr>
<tr><td><code>minReadySeconds</code></td><td>Pod must stay Ready for N seconds before counted as available; smooths flapping</td></tr>
<tr><td><code>progressDeadlineSeconds</code></td><td>Marks rollout failed if no progress within window; with <code>kubectl rollout undo</code>, gives auto-rollback</td></tr>
</tbody>
</table>
<p><strong>Mechanism:</strong> the Deployment controller writes spec updates as a new <code>ReplicaSet</code> with a hashed pod-template label. The selector splits old vs new pods. Kubelet starts new pods; once Ready, the controller scales down old ones &mdash; honouring both surge/unavailable limits and any PodDisruptionBudget.</p>
<p><strong>Best practice (2026):</strong></p>
<ul>
<li><strong>Always</strong> define readiness probes that reflect actual readiness (DB connections initialised, config loaded), not just <em>process is up</em>.</li>
<li>Add <code>preStop</code> hook (<code>sleep 15</code>) so endpoints deregister before SIGTERM &mdash; avoids 5xx during rollout.</li>
<li>Use <code>maxSurge: 100%, maxUnavailable: 0</code> for stateless services; sequential <code>OnDelete</code> for StatefulSets.</li>
<li>For richer control (analysis, traffic shaping, automated rollback), graduate to <strong>Argo Rollouts</strong> &mdash; its <code>Rollout</code> resource is a drop-in replacement with progressive delivery primitives baked in.</li>
</ul>
'''


ANSWERS[19] = r'''<p>Dynamic Jenkins agents on Kubernetes spawn one ephemeral Pod per build, run the job, and tear down. The mechanism is the <strong>Kubernetes plugin</strong>: Jenkins acts as a Pod controller, creating Pods that join as JNLP (now <em>inbound</em>) agents over a TCP tunnel.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Jenkins controller</td><td>Receives job; computes a Pod template (label + container spec)</td></tr>
<tr><td>Kubernetes cloud config</td><td>Holds API URL, credentials, namespace, default image</td></tr>
<tr><td>Pod template</td><td>YAML or Groovy template; can declare multiple containers (e.g. <code>maven</code>, <code>docker</code>, <code>kubectl</code>)</td></tr>
<tr><td>Inbound agent container</td><td>Default <code>jenkins/inbound-agent</code> sidecars dial back to controller; other containers run build steps</td></tr>
</tbody>
</table>
<p><strong>Per-pipeline pod spec:</strong></p>
<pre><code>pipeline {
  agent {
    kubernetes {
      yaml &apos;&apos;&apos;
        apiVersion: v1
        kind: Pod
        spec:
          serviceAccountName: jenkins-builder
          containers:
            - name: maven
              image: maven:3.9-eclipse-temurin-21
              command: [cat]
              tty: true
            - name: kaniko
              image: gcr.io/kaniko-project/executor:latest
              command: [sleep]
              args: ['9999999']
      &apos;&apos;&apos;
    }
  }
  stages {
    stage('Test')  { steps { container('maven')  { sh 'mvn test' } } }
    stage('Image') { steps { container('kaniko') { sh '/kaniko/executor ...' } } }
  }
}
</code></pre>
<p><strong>Benefits:</strong> per-build isolation (no leaked state), elastic capacity (cluster autoscaler / Karpenter provisions nodes on demand), polyglot builds (different containers per language without VM templates), and resource accountability (each build is a Pod with limits).</p>
<p><strong>2026 advice:</strong> use <strong>workspace volumes</strong> (<code>emptyDir</code> or PVC) shared across containers; pin agent image digest; set <code>idleMinutes</code> on cloud config to recycle stale pods; pair with <strong>Karpenter</strong> for spot-instance build farms (cuts CI cost 60-80%). For greenfield, consider <strong>Tekton</strong> or <strong>GitHub Actions self-hosted runners on K8s</strong> (via <code>actions-runner-controller</code>) &mdash; same Pod-per-job model, simpler ops.</p>
'''


ANSWERS[20] = r'''<p>Continuous security/compliance in GitHub Actions is implemented as <em>shift-left scanning gates</em> on every PR plus <em>scheduled audits</em> against <code>main</code>. Findings either block merges or open dependency-style alerts.</p>
<table>
<thead><tr><th>Concern</th><th>Tool</th><th>Hook</th></tr></thead>
<tbody>
<tr><td>Source SAST</td><td><strong>CodeQL</strong>, Semgrep, SonarCloud</td><td>PR check + Security tab</td></tr>
<tr><td>Dep CVEs</td><td>Dependabot, Renovate, Trivy fs, Snyk</td><td>Auto-PR for upgrades; PR fail on critical</td></tr>
<tr><td>Container CVEs</td><td>Trivy, Grype, Anchore</td><td>Image build job; <code>--exit-code 1 --severity HIGH,CRITICAL</code></td></tr>
<tr><td>Secrets in code</td><td>gitleaks, trufflehog, GitHub secret scanning + push protection</td><td>PR check + repo-level alert</td></tr>
<tr><td>IaC misconfig</td><td>Checkov, tfsec, Trivy IaC, KICS</td><td>PR check on Terraform / K8s manifests</td></tr>
<tr><td>License/SBOM</td><td>Syft + Grype, FOSSA</td><td>Generate SBOM, sign with cosign, attach to release</td></tr>
<tr><td>Compliance frameworks</td><td>Open Policy Agent, Conftest</td><td>Rego policies enforce SOC2/PCI/HIPAA invariants</td></tr>
<tr><td>SLSA / provenance</td><td><code>slsa-framework/slsa-github-generator</code></td><td>Tamper-evident build attestation</td></tr>
</tbody>
</table>
<p><strong>Workflow patterns:</strong></p>
<ul>
<li><strong>PR-time</strong>: fast scanners (Semgrep, Trivy fs) gate merges; slow ones (CodeQL full-DB) run async and post results.</li>
<li><strong>Scheduled</strong>: nightly full-repo scans against <code>main</code> populate the Security tab.</li>
<li><strong>Release-time</strong>: SBOM + cosign signature + SLSA attestation attached to the GitHub Release; admission controller verifies before deploy.</li>
</ul>
<p><strong>2026 best practice:</strong> centralise findings via <strong>GitHub Advanced Security</strong> code scanning + secret scanning + Dependabot, fed into a security-team owned dashboard. Pair with <strong>Kyverno admission policies</strong> in K8s so unscanned/unsigned images are rejected at deploy time, not merely flagged in CI. Compliance evidence (control attestations) auto-collected by <strong>Drata / Vanta / Secureframe</strong> from the same workflow runs.</p>
'''


ANSWERS[21] = r'''<p>Docker dependency management for multi-service apps treats each service as an independent build artefact while sharing common bases. The mechanism is <em>per-service Dockerfile + shared base image + lockfile-driven reproducibility</em>.</p>
<table>
<thead><tr><th>Pattern</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Shared base image</td><td>Internal <code>acme/node-base:20</code> with security patches, common tools, non-root user; rebuilt nightly. Service Dockerfiles <code>FROM acme/node-base:20</code></td></tr>
<tr><td>Lockfile in image</td><td>Always <code>COPY package.json package-lock.json</code> + <code>npm ci</code>, never <code>npm install</code>. Same for <code>poetry.lock</code>, <code>Cargo.lock</code>, <code>go.sum</code>.</td></tr>
<tr><td>Layer caching by stability</td><td>Slowest-changing layers first (OS deps), fastest-changing last (source). Cache hits dominate build time.</td></tr>
<tr><td>Multi-arch</td><td><code>buildx --platform linux/amd64,linux/arm64</code>; cross-compile in Go/Rust to skip QEMU.</td></tr>
<tr><td>Private registry</td><td>Internal Artifactory / ECR / Harbor; mirror DockerHub to avoid rate limits + supply-chain risk.</td></tr>
<tr><td>SBOM &amp; signing</td><td>Each pushed image carries SBOM (Syft) + cosign signature; admission policy verifies on pull.</td></tr>
</tbody>
</table>
<p><strong>Multi-service orchestration:</strong> Compose for local dev (<code>depends_on: condition: service_healthy</code> sequences startup); Helm umbrella charts or Argo CD ApplicationSets for K8s. <strong>Nx / Turborepo</strong> graph-aware <code>build --affected</code> rebuilds only changed services and their downstream consumers.</p>
<p><strong>2026 tooling:</strong></p>
<ul>
<li><strong>Renovate</strong> auto-PRs base-image bumps with grouped PRs across services.</li>
<li><strong>Docker Build Cloud / Depot</strong> share remote BuildKit cache across services and CI runs.</li>
<li><strong>Cloud Native Buildpacks (Paketo)</strong> sidestep Dockerfiles entirely; same lockfile mechanics, opinionated layering.</li>
<li><strong>Chainguard images</strong> as drop-in distroless bases &mdash; CVE-minimal, signed, daily-rebuilt.</li>
</ul>
<p><strong>Pitfall:</strong> floating <code>:latest</code> base tags. Pin to digest (<code>node:20-alpine@sha256:&hellip;</code>) and let Renovate handle bumps; otherwise builds become time-machine dependent.</p>
'''


ANSWERS[22] = r'''<p>Helm packages Kubernetes manifests as a <em>chart</em> (templates + values.yaml + Chart.yaml) and renders them at install time, producing a <em>release</em> tracked in cluster state. The mechanism is <em>parameterised templating + release lifecycle</em>.</p>
<table>
<thead><tr><th>Concept</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Chart</td><td>Versioned bundle: <code>templates/</code> (Go templates), <code>values.yaml</code> (defaults), <code>Chart.yaml</code> (metadata + deps), <code>charts/</code> (subcharts), <code>crds/</code> (CRDs installed before templates)</td></tr>
<tr><td>Values</td><td>Overlay: <code>helm install --values prod.yaml --set replicaCount=5</code>; merged left-to-right, CLI overrides win</td></tr>
<tr><td>Release</td><td>Stored as Secret in cluster (default); <code>helm upgrade</code> diffs vs previous, applies, increments revision; <code>helm rollback</code> reverts to a prior revision</td></tr>
<tr><td>Hooks</td><td><code>pre-install</code>, <code>post-upgrade</code>, etc. for migration jobs &mdash; ordered, with weights and deletion policies</td></tr>
<tr><td>Subcharts &amp; deps</td><td><code>Chart.yaml</code> <code>dependencies:</code> + <code>helm dep update</code>; subchart values namespaced under the dep name</td></tr>
</tbody>
</table>
<p><strong>CI/CD usage:</strong> push chart to OCI registry (<code>helm push acme-app-1.2.3.tgz oci://ghcr.io/acme/charts</code>); deploy via <code>helm upgrade --install --atomic --timeout 5m</code> (atomic rolls back on failure). For GitOps, store rendered manifests or <code>HelmRelease</code> CRs (Flux) / <code>Application</code> CRs (Argo CD) in Git; the controller renders + applies.</p>
<p><strong>Trade-offs (2026):</strong></p>
<ul>
<li><strong>Helm vs Kustomize</strong> &mdash; Helm wins for distributable, parameterised charts (third-party software). Kustomize wins for own-app overlays (no templating syntax to debug).</li>
<li><strong>Helm vs Timoni</strong> &mdash; Timoni uses CUE schemas for strong typing, replacing string-templated YAML.</li>
<li><strong>Helm vs Carvel ytt + kapp</strong> &mdash; ytt does pure-data templating; kapp manages release lifecycle without server-side state.</li>
</ul>
<p><strong>Pitfalls:</strong> Go templates over YAML are error-prone (whitespace, indentation); use <code>helm template | kubectl diff</code> in CI to catch surprises. Stored release size grows with chart size &mdash; Helm 3 compresses but very large charts can hit Secret size limits.</p>
'''


ANSWERS[23] = r'''<p>Tekton is a Kubernetes-native CI/CD framework where every primitive is a CRD. Pipelines run as Pods on the cluster you&rsquo;re building <em>for</em>, with no external orchestrator.</p>
<table>
<thead><tr><th>CRD</th><th>Role</th></tr></thead>
<tbody>
<tr><td><code>Task</code></td><td>Reusable unit; one or more <code>steps</code>, each a container</td></tr>
<tr><td><code>Pipeline</code></td><td>DAG of Task references with parameters, results, workspaces</td></tr>
<tr><td><code>TaskRun</code> / <code>PipelineRun</code></td><td>Instances; controller schedules Pods to execute them</td></tr>
<tr><td><code>Workspace</code></td><td>Shared volume (PVC, emptyDir, ConfigMap) bound at run time &mdash; how Tasks share artefacts</td></tr>
<tr><td><code>EventListener</code> + <code>Trigger</code> (Tekton Triggers)</td><td>Webhook receiver that creates PipelineRuns from external events (GitHub push, etc.)</td></tr>
<tr><td><code>Chains</code></td><td>Sigstore signing + SLSA provenance for every TaskRun, automatically</td></tr>
</tbody>
</table>
<p><strong>Mechanism:</strong> a <code>PipelineRun</code> creates a Pod per Task; steps within a Task share the Pod (sequential containers in the same spec). Workspaces mount across Tasks. Results flow between Tasks via parameter-style DAG edges. Failures stop dependent Tasks unless <code>finally</code> blocks define cleanup.</p>
<p><strong>Strengths:</strong></p>
<ul>
<li><strong>K8s-native</strong> &mdash; same RBAC, namespaces, network policies as your apps. No separate auth model.</li>
<li><strong>Catalog</strong> &mdash; <code>tektoncd/catalog</code> + Tekton Hub provide reusable Tasks (git-clone, buildah, kaniko, helm-upgrade, etc.).</li>
<li><strong>Dagger / Tekton Chains</strong> &mdash; SLSA provenance and signing built in.</li>
<li>Exposes the full Pod spec, so anything Kubernetes can run, Tekton can run.</li>
</ul>
<p><strong>2026 reality:</strong> Tekton is the engine inside <strong>Red Hat OpenShift Pipelines</strong>, <strong>Jenkins X</strong>, and <strong>IBM Cloud Continuous Delivery</strong>. As a standalone product its UX lags GitHub Actions / GitLab CI, so most teams pair it with <strong>Argo CD</strong> (CI = Tekton, CD = Argo) or use a thin frontend like <strong>Tekton Dashboard</strong> / <strong>Backstage</strong>. Best fit: regulated/airgapped environments where CI must run inside the same cluster as the workload.</p>
'''


ANSWERS[24] = r'''<p>Continuous deploy from Jenkins to EKS is a four-stage pipeline: <em>build &rarr; push &rarr; render &rarr; apply</em>. Jenkins owns build/push; rendering and apply use either <code>kubectl</code>/<code>helm</code> directly or, increasingly, push to a GitOps repo for Argo CD/Flux to converge.</p>
<table>
<thead><tr><th>Stage</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Build</td><td>Multi-stage Dockerfile in Kubernetes-plugin agent pod (kaniko or buildkit container)</td></tr>
<tr><td>Push to ECR</td><td>IRSA-bound ServiceAccount on the agent pod; <code>aws ecr get-login-password | docker login</code></td></tr>
<tr><td>Render</td><td><code>helm template</code> or <code>kustomize build</code>; lint with <code>kubeconform</code> + policy with <code>conftest</code></td></tr>
<tr><td>Apply</td><td><strong>Direct</strong>: <code>helm upgrade --install --atomic</code> via IRSA. <strong>GitOps</strong>: commit rendered tag bump to config repo; Argo CD syncs.</td></tr>
<tr><td>Verify</td><td><code>kubectl rollout status</code>, smoke test, then promotion gate</td></tr>
</tbody>
</table>
<p><strong>Auth pattern (2026):</strong> the Jenkins agent pod runs with a Kubernetes ServiceAccount annotated with an IAM role ARN (IRSA, or Pod Identity in newer EKS). AWS SDK in the pod auto-discovers credentials &mdash; no static keys, no <code>aws configure</code>. The same role can carry ECR push, EKS describe, and Secrets Manager read permissions, scoped per environment.</p>
<p><strong>Modern shape:</strong></p>
<ul>
<li><strong>Jenkins</strong> still owns build/push; GitOps owns deploy.</li>
<li><code>helmfile</code> or <strong>Argo CD ApplicationSets</strong> templates one app per environment.</li>
<li><strong>Argo Rollouts</strong> for canary/blue-green progressive delivery.</li>
<li><strong>Karpenter</strong> on the EKS data plane gives spot-instance build agents and workload nodes.</li>
</ul>
<p><strong>Pitfalls:</strong> embedding <code>kubectl</code> credentials in Jenkinsfile (<code>KUBECONFIG=...</code>) instead of IRSA &mdash; rotate friction + security risk. Long-lived deploy tokens in Jenkins credentials store &mdash; prefer per-build OIDC exchange via <strong>aws-actions</strong>-style helpers or the <strong>HashiCorp Vault Plugin</strong> for dynamic creds.</p>
'''


ANSWERS[25] = r'''<p>Prometheus scrapes metrics from in-cluster targets; Grafana queries Prometheus and visualises. The standard installation is the <strong>kube-prometheus-stack</strong> Helm chart, which bundles Prometheus Operator, Alertmanager, node-exporter, kube-state-metrics, and pre-built dashboards.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Prometheus Operator</td><td>Watches <code>ServiceMonitor</code> / <code>PodMonitor</code> CRs and auto-configures Prometheus scrape targets</td></tr>
<tr><td>kube-state-metrics</td><td>Exposes K8s object state (Deployment replicas, Pod phases) as metrics</td></tr>
<tr><td>node-exporter</td><td>Per-node DaemonSet exposing CPU, memory, disk, network stats</td></tr>
<tr><td>cAdvisor (in kubelet)</td><td>Per-container resource metrics</td></tr>
<tr><td>Alertmanager</td><td>Deduplicates, routes, silences alerts; integrates Slack/PagerDuty/Email</td></tr>
<tr><td>Grafana</td><td>Provisioned with K8s + node + ingress dashboards out of the box</td></tr>
</tbody>
</table>
<p><strong>Application metrics:</strong> apps expose <code>/metrics</code> in Prometheus format; a <code>ServiceMonitor</code> selects the Service by label and Prometheus auto-scrapes it. Define <strong>SLOs</strong> as <code>PrometheusRule</code> CRs (<code>recording rules</code> + <code>alerting rules</code>) versioned alongside the app.</p>
<p><strong>Storage trade-offs:</strong> Prometheus local TSDB is great for short-term (15d) but doesn&rsquo;t scale horizontally. For long-term + multi-cluster:</p>
<ul>
<li><strong>Thanos</strong> &mdash; sidecar uploads blocks to S3, global query layer.</li>
<li><strong>Mimir / Cortex</strong> &mdash; horizontally-scaled Prometheus-compatible TSDB.</li>
<li><strong>VictoriaMetrics</strong> &mdash; faster, lower resource use, drop-in PromQL.</li>
<li><strong>Managed</strong> &mdash; AMP (AWS Managed Prometheus), Grafana Cloud, Datadog (proprietary).</li>
</ul>
<p><strong>2026 stack additions:</strong> <strong>OpenTelemetry Collector</strong> normalises metrics+logs+traces from all sources; <strong>Loki</strong> for logs; <strong>Tempo / Jaeger</strong> for traces. Grafana 11+ unifies all three signals and supports correlated trace-to-logs-to-metrics navigation.</p>
'''


ANSWERS[26] = r'''<p>Test parallelism in GitHub Actions has two axes: <em>job parallelism</em> (matrix strategy) and <em>within-job parallelism</em> (test runner sharding).</p>
<table>
<thead><tr><th>Mechanism</th><th>Detail</th></tr></thead>
<tbody>
<tr><td><code>strategy.matrix</code></td><td>Fans one job out into N concurrent jobs across dimensions (OS, Node version, shard index)</td></tr>
<tr><td><code>strategy.max-parallel</code></td><td>Caps concurrency to avoid runner exhaustion</td></tr>
<tr><td><code>fail-fast: false</code></td><td>Continue all matrix jobs even if one fails &mdash; needed to see all shard failures, not just the first</td></tr>
<tr><td>Test runner sharding</td><td>Jest <code>--shard=$i/$N</code>, pytest-split, Go <code>go test -shuffle=on -count=1 ./pkg{1,2,3}/...</code></td></tr>
<tr><td>Concurrency groups</td><td><code>concurrency: { group: ${{ github.ref }}, cancel-in-progress: true }</code> stops superseded runs</td></tr>
</tbody>
</table>
<p><strong>Sharding pattern:</strong></p>
<pre><code>strategy:
  fail-fast: false
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: pnpm test --shard=${{ matrix.shard }}/4
</code></pre>
<p>Each shard runs ~25% of tests; total wall-clock time drops 4&times; (minus runner startup overhead).</p>
<p><strong>2026 ecosystem:</strong></p>
<ul>
<li><strong>Knapsack Pro / CircleCI test splitting / Buildkite test analytics</strong> &mdash; balance shards by historical timing, not file count, eliminating stragglers.</li>
<li><strong>Vitest workers</strong> + <code>--isolate=false</code> exploit per-job CPU.</li>
<li><strong>Bazel / Nx / Turbo</strong> only run tests affected by the diff &mdash; orthogonal to sharding.</li>
<li><strong>Larger runners</strong> (8/16-core GitHub-hosted, or self-hosted on EC2/Karpenter) trade shard count for vertical capacity.</li>
</ul>
<p><strong>Pitfalls:</strong> tests with shared global state break when parallelised (DB row collisions, port reuse, fixed temp paths). Fix: per-shard schemas (<code>app_test_${SHARD}</code>), randomised ports, <code>tmpfs</code> per worker. Flaky tests re-run via <code>--retries</code> hide real bugs &mdash; instrument retry rate as a quality metric.</p>
'''


ANSWERS[27] = r'''<p>Docker image tagging in CI/CD reflects two needs: <em>identity</em> (which build produced this) and <em>intent</em> (what role does this image play). The mechanism is multiple tags pointing at the same digest.</p>
<table>
<thead><tr><th>Tag</th><th>Purpose</th><th>Pattern</th></tr></thead>
<tbody>
<tr><td>Immutable identity</td><td>Bit-for-bit traceable</td><td><code>git-${COMMIT_SHA:0:12}</code> or <code>sha256:&hellip;</code> digest</td></tr>
<tr><td>Semantic version</td><td>Human-friendly release</td><td><code>v1.4.2</code>, <code>1.4</code>, <code>1</code> (cascading)</td></tr>
<tr><td>Branch tracker</td><td>Latest from a branch</td><td><code>main</code>, <code>release-1.4</code></td></tr>
<tr><td>Environment</td><td>What's deployed where</td><td><code>staging</code>, <code>prod</code> &mdash; updated by CD, never by build</td></tr>
<tr><td><code>latest</code></td><td>Avoid in CI/CD</td><td>Floating; breaks reproducibility</td></tr>
</tbody>
</table>
<p><strong>Best practice (2026):</strong></p>
<ul>
<li><strong>Always pin deploys to the digest</strong> (<code>image: registry/app@sha256:&hellip;</code>) &mdash; tags can be moved; digests cannot.</li>
<li><strong>Use git SHA tags</strong> for build outputs; environment tags only as pointers updated atomically by CD.</li>
<li><strong>SemVer</strong> for libraries / public images; <strong>CalVer</strong> (<code>2026.05.15-1234</code>) for app images that ship continuously.</li>
<li><strong>docker/metadata-action</strong> auto-generates a sensible tag set: branch, SHA, semver, plus <code>type=ref,event=tag</code>.</li>
</ul>
<p><strong>Promotion model:</strong> never rebuild between environments. Build once, scan, sign with cosign, push to registry; promotion is just <code>cosign verify</code> + <code>kubectl set image</code> with the digest. This eliminates "works in staging, fails in prod" caused by base-image drift between rebuilds.</p>
<p><strong>Storage hygiene:</strong> registries fill fast. Lifecycle policies retain (a) all signed release tags forever, (b) PR/branch images for 14 days, (c) untagged digests for 7 days then GC. <strong>Harbor</strong> and <strong>JFrog Artifactory</strong> expose richer retention policies than ECR/GCR.</p>
'''


ANSWERS[28] = r'''<p>Serverless CI/CD on GitHub Actions follows the <em>build-package-deploy-promote</em> shape but with framework-specific packaging. The deploy is API-driven (Lambda, Cloud Functions, Azure Functions) rather than container orchestration.</p>
<table>
<thead><tr><th>Stack</th><th>Tool</th><th>Deploy command</th></tr></thead>
<tbody>
<tr><td>AWS Lambda</td><td>SAM, AWS CDK, Serverless Framework, Terraform</td><td><code>sam deploy</code> / <code>cdk deploy</code> / <code>sls deploy</code></td></tr>
<tr><td>GCP Cloud Functions / Run</td><td>gcloud, Functions Framework</td><td><code>gcloud functions deploy</code> / <code>gcloud run deploy</code></td></tr>
<tr><td>Azure Functions</td><td>Azure Functions Core Tools, Bicep</td><td><code>azure/functions-action</code></td></tr>
<tr><td>Multi-cloud / portable</td><td>Knative, OpenFaaS, Pulumi</td><td>Pushes to K8s control plane</td></tr>
</tbody>
</table>
<p><strong>Pipeline shape:</strong></p>
<ol>
<li><strong>Test</strong> &mdash; unit; integration with LocalStack (AWS) or Firebase Emulator (GCP).</li>
<li><strong>Package</strong> &mdash; build artefact (zip, container image, or framework-managed bundle).</li>
<li><strong>Deploy to dev</strong> &mdash; ephemeral environment per PR (<code>--stack-name pr-${PR_NUMBER}</code>) torn down on merge/close.</li>
<li><strong>Promote to staging/prod</strong> &mdash; same artefact, different config; via <code>sam deploy --config-env prod</code> or alias updates.</li>
<li><strong>Progressive rollout</strong> &mdash; Lambda <code>publish-version</code> + <code>update-alias</code> with weighted alias (e.g. 10% to new version) gated by CloudWatch alarms; CodeDeploy <code>LambdaCanary10Percent5Minutes</code> automates this.</li>
</ol>
<p><strong>Auth (2026):</strong> OIDC federation everywhere &mdash; no long-lived cloud keys in repo secrets. <code>aws-actions/configure-aws-credentials</code>, <code>google-github-actions/auth</code>, <code>azure/login</code> all support it.</p>
<p><strong>Pitfalls:</strong> shared resources (databases, queues) created from CI without state management drift quickly &mdash; keep them in Terraform/CDK separate from function code. Cold start regressions slip in unnoticed &mdash; add a synthetic that measures p99 cold-start as a regression gate. Function permissions accumulate via "just add another <code>*</code> to make it work" &mdash; periodically run <strong>iam-policy-simulator</strong> or <strong>cloudsplaining</strong> to flag overprivileged roles.</p>
'''


ANSWERS[29] = r'''<p>Operators encapsulate operational expertise for a specific application as a Kubernetes controller plus CRDs. They reconcile actual cluster state to a declared spec, handling install, upgrade, backup, scaling, and failover that would otherwise be a runbook.</p>
<table>
<thead><tr><th>Capability</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>CRD</td><td>Domain object &mdash; <code>kind: Postgres</code> with <code>spec.replicas: 3, spec.version: 16</code></td></tr>
<tr><td>Reconcile loop</td><td>Watch &rarr; diff &rarr; act &rarr; status update; idempotent and level-driven</td></tr>
<tr><td>Lifecycle phases</td><td>Day-1 (install) + Day-2 (backup, restore, version upgrade, failover, scale)</td></tr>
<tr><td>Health</td><td>Status subresource; <code>kubectl get postgres</code> shows printer columns derived from status</td></tr>
<tr><td>OLM (Operator Lifecycle Manager)</td><td>Catalogs, subscriptions, automated upgrades; default in OpenShift, optional elsewhere</td></tr>
</tbody>
</table>
<p><strong>Capability levels (Operator SDK):</strong> Basic Install &rarr; Seamless Upgrades &rarr; Full Lifecycle &rarr; Deep Insights &rarr; Auto Pilot. Production operators (Cassandra, Kafka, Postgres) sit at level 4-5.</p>
<p><strong>Authoring (2026):</strong></p>
<ul>
<li><strong>kubebuilder</strong> &mdash; Go scaffold + <code>controller-runtime</code>; the de-facto standard.</li>
<li><strong>Operator SDK</strong> &mdash; layer on top with Helm/Ansible-based operator types for non-Go teams.</li>
<li><strong>Kopf</strong> (Python), <strong>shoot-operator</strong> (Java/Quarkus), <strong>kube-rs</strong> (Rust) for language-native authoring.</li>
<li><strong>Metacontroller</strong> &mdash; write operators as webhooks in any language without controller-runtime.</li>
</ul>
<p><strong>Production operators worth knowing:</strong> <strong>CloudNativePG</strong> (Postgres), <strong>Strimzi</strong> (Kafka), <strong>Velero</strong> (backup), <strong>cert-manager</strong> (TLS), <strong>Prometheus Operator</strong>, <strong>Crossplane</strong> (cloud resources as CRs), <strong>Argo CD</strong> (its own operator pattern). Buy-vs-build: prefer community operators with capability level &ge; 3 over rolling your own.</p>
<p><strong>Pitfalls:</strong> over-eager reconcile loops thrash the API server; always rate-limit + use <code>RequeueAfter</code>. Status without conditions makes debugging impossible &mdash; emit <code>type/status/reason/message</code> conditions like Kubernetes core controllers.</p>
'''


ANSWERS[30] = r'''<p>Jenkins X is an opinionated, Kubernetes-native CI/CD platform that wraps Tekton (build) + Argo CD (deploy) + Lighthouse (webhook handler) + jx CLI behind a GitOps-driven workflow. Every project lives in Git; every action is a PR.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Lighthouse</td><td>ChatOps webhook handler; replaces classic Prow; routes GitHub/GitLab events to Tekton</td></tr>
<tr><td>Tekton</td><td>Pipeline engine; runs build/test/image jobs as Pods</td></tr>
<tr><td>jx-pipelines (build packs)</td><td>Language-aware default pipelines; one <code>jx import</code> turns any repo into a working CI/CD pipeline</td></tr>
<tr><td>Argo CD / Flux (Jenkins X 3+)</td><td>Pulls promotions from environment repos; reconciles into clusters</td></tr>
<tr><td>Environment repos</td><td>One Git repo per env (staging, prod) holding helmfile state; promotion is a PR from one repo to the next</td></tr>
<tr><td><code>jx</code> CLI</td><td>Glue: <code>jx import</code>, <code>jx promote</code>, <code>jx preview</code></td></tr>
</tbody>
</table>
<p><strong>Workflow:</strong> <code>jx import</code> on a repo bootstraps Dockerfile, helm chart, Tekton pipeline, environment promotion. PR opens &rarr; preview env spun up automatically with the PR&rsquo;s image. Merge to <code>main</code> &rarr; image built, version bumped, PR opened against the staging env repo. Merge that PR &rarr; Argo CD deploys to staging. <code>jx promote --env production</code> opens a similar PR against prod.</p>
<p><strong>2026 reality:</strong> Jenkins X 3 (the rewrite) is fully GitOps and stable, but adoption is niche compared to plain <strong>Argo CD + GitHub Actions</strong> or <strong>Argo CD + Tekton</strong>. The "automatic preview env per PR" remains its standout feature, also achievable with <strong>vCluster + Argo CD ApplicationSets</strong> or <strong>Backstage scaffolder + Argo CD</strong>. Pick Jenkins X if the opinionated, batteries-included flow saves a platform team six months of integration work; otherwise compose the same parts yourself for full control.</p>
<p><strong>Migration path:</strong> classic Jenkins &rarr; Jenkins X is non-trivial &mdash; pipelines, plugins, credentials, and shared libraries don&rsquo;t carry over. Treat it as a green-field rebuild, not an upgrade.</p>
'''

ANSWERS[31] = r'''<p>Deploying to GKE from GitHub Actions hinges on Workload Identity Federation (WIF) for keyless auth and either direct <code>kubectl</code> apply or push-to-GitOps. The mechanism: GitHub OIDC token &rarr; GCP STS &rarr; impersonated service account.</p>
<table>
<thead><tr><th>Stage</th><th>Action / detail</th></tr></thead>
<tbody>
<tr><td>One-time setup</td><td>Create WIF pool + provider in GCP; bind to a deploy SA with <code>roles/container.developer</code> + <code>roles/artifactregistry.writer</code></td></tr>
<tr><td>Auth</td><td><code>google-github-actions/auth</code> with <code>workload_identity_provider</code> + <code>service_account</code>; outputs <code>access_token</code></td></tr>
<tr><td>Build/push</td><td><code>docker buildx build --push</code> to Artifact Registry; auth via <code>gcloud auth configure-docker</code></td></tr>
<tr><td>Cluster auth</td><td><code>google-github-actions/get-gke-credentials</code> writes <code>~/.kube/config</code> with the GKE Auth plugin (gke-gcloud-auth-plugin)</td></tr>
<tr><td>Deploy</td><td><code>kubectl apply -k overlays/prod</code> or <code>helm upgrade --install --atomic</code>; verify with <code>kubectl rollout status</code></td></tr>
</tbody>
</table>
<p><strong>GitOps alternative (preferred 2026):</strong> the workflow only writes the new image tag into the Argo CD / Flux config repo. The CD controller running in-cluster pulls the change and applies; CI never holds cluster credentials. Cleaner blast radius and audit trail.</p>
<p><strong>GKE-specific tooling:</strong></p>
<ul>
<li><strong>Config Sync</strong> (Anthos / GKE Enterprise) &mdash; Google&rsquo;s GitOps controller; tight integration with <em>Policy Controller</em> (Gatekeeper).</li>
<li><strong>Cloud Deploy</strong> &mdash; managed progressive delivery service; PR-style promotion across targets, integrated with Skaffold.</li>
<li><strong>Skaffold</strong> &mdash; local-and-CI dev loop; <code>skaffold render</code> + <code>skaffold deploy</code> usable inside Actions.</li>
<li><strong>GKE Autopilot</strong> &mdash; node management hidden, only pay for pod resources; CI deploys are identical.</li>
</ul>
<p><strong>Pitfalls:</strong> using a downloaded JSON SA key (<code>credentials_json</code>) instead of WIF &mdash; Google has flagged static keys as anti-pattern since 2023. Granting <code>roles/container.admin</code> instead of <code>developer</code> &mdash; namespace-scoped RBAC inside the cluster is finer-grained and safer.</p>
'''


ANSWERS[32] = r'''<p>Docker security best practices in CI/CD line up around build, image, registry, and runtime. Each layer adds defence-in-depth.</p>
<table>
<thead><tr><th>Practice</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Minimal base image</td><td>Distroless / Chainguard / chiseled / scratch &mdash; eliminates shells, pkg managers</td></tr>
<tr><td>Non-root <code>USER</code></td><td>Final stage runs as a fixed UID:GID; failing to do this means K8s <code>runAsNonRoot: true</code> rejects the pod</td></tr>
<tr><td>Multi-stage build</td><td>Build deps and source never reach the runtime image</td></tr>
<tr><td>Pin to digest</td><td><code>FROM node:20-alpine@sha256:&hellip;</code> &mdash; tags can move; digests cannot</td></tr>
<tr><td>No secrets in layers</td><td><code>--mount=type=secret</code> for build-time creds; never <code>ARG SECRET</code> + <code>ENV</code></td></tr>
<tr><td>Scan early, fail loudly</td><td>Trivy/Grype with <code>--exit-code 1 --severity HIGH,CRITICAL</code> in the build job</td></tr>
<tr><td>Sign &amp; verify</td><td>Cosign keyless signing in build; admission controller (Kyverno/Sigstore policy-controller) verifies in-cluster</td></tr>
<tr><td>SBOM + provenance</td><td>Syft generates SBOM; <code>slsa-github-generator</code> attaches build provenance</td></tr>
<tr><td>Read-only rootfs</td><td>K8s <code>securityContext.readOnlyRootFilesystem: true</code>; tmpfs for writable paths</td></tr>
<tr><td>Drop capabilities</td><td><code>capabilities.drop: ["ALL"]</code>; add specific ones only when proven necessary</td></tr>
<tr><td>Seccomp + AppArmor</td><td><code>seccompProfile.type: RuntimeDefault</code>; AppArmor on supported runtimes</td></tr>
<tr><td>Network policy</td><td>Default-deny; explicit allow for known service-to-service flows</td></tr>
</tbody>
</table>
<p><strong>Supply-chain hardening (2026):</strong> the SLSA framework formalises the above into <em>levels</em>; Level 3 requires hardened build platforms (GitHub-hosted runners with provenance), tamper-evident logs, and reproducible builds. <strong>in-toto attestations</strong> + <strong>Sigstore Rekor</strong> publish signatures to a transparency log so supply-chain compromise is detectable post-hoc.</p>
<p><strong>Runtime detection:</strong> <strong>Falco</strong> watches syscall events for anomalies (shell in container, mount events, sensitive file reads). Pair with <strong>Tetragon</strong> (eBPF-based) for kernel-level enforcement. Both feed SIEMs (Splunk, Datadog) for correlated detection.</p>
'''


ANSWERS[33] = r'''<p>Pipeline DSL is Jenkins&rsquo;s Groovy-flavoured scripting layer for declaring CI flows. Two flavours coexist: <strong>Declarative</strong> (the default, structured, opinionated) and <strong>Scripted</strong> (the older, free-form Groovy). Complex workflows usually combine both: a Declarative skeleton with embedded <code>script {}</code> blocks for imperative logic.</p>
<table>
<thead><tr><th>Construct</th><th>Detail</th></tr></thead>
<tbody>
<tr><td><code>parallel</code></td><td>Run stage groups concurrently; failed branches abort siblings unless <code>failFast: false</code></td></tr>
<tr><td><code>matrix</code></td><td>Cartesian product over axes (OS, JDK, etc.); each cell runs the same stages</td></tr>
<tr><td><code>when</code> conditions</td><td><code>branch</code>, <code>changeRequest</code>, <code>changeset</code>, <code>environment</code>, <code>expression</code> for fine-grained gating</td></tr>
<tr><td><code>input</code></td><td>Manual approval gate; can require submitters and capture parameters</td></tr>
<tr><td>Shared Libraries</td><td>Reusable Groovy code via <code>@Library('acme@v3')</code>; <code>vars/</code> for steps, <code>src/</code> for classes</td></tr>
<tr><td><code>options</code></td><td><code>timeout</code>, <code>retry</code>, <code>buildDiscarder</code>, <code>concurrentBuilds</code>, <code>throttleJobProperty</code></td></tr>
<tr><td><code>post</code></td><td><code>always</code>, <code>success</code>, <code>failure</code>, <code>changed</code>, <code>fixed</code> &mdash; cleanup and notifications</td></tr>
<tr><td><code>script {}</code></td><td>Imperative escape hatch; run any Groovy</td></tr>
</tbody>
</table>
<p><strong>Patterns for complex workflows:</strong></p>
<ul>
<li><strong>Fan-out/fan-in</strong>: parent job builds matrix of services in parallel, then a single integration-test stage depends on all.</li>
<li><strong>Manual gates</strong>: <code>input</code> step pauses prod deploy waiting for approval; combine with <code>timeout</code> so abandoned builds don&rsquo;t hold executors.</li>
<li><strong>Dynamic stages</strong>: build a list at runtime (<code>def stages = [:]</code>; populate from config), then call <code>parallel(stages)</code>.</li>
<li><strong>Restart from stage</strong>: enable in <code>options { preserveStashes() }</code> + <code>restartedRun</code> &mdash; recover from a flaky deploy without rerunning tests.</li>
</ul>
<p><strong>2026 advice:</strong> keep Groovy minimal; push complex logic into Shared Libraries (testable Groovy units) or even out of Jenkins entirely (Bash/Python scripts in the repo, called by simple <code>sh</code> steps). New teams more often choose <strong>GitHub Actions reusable workflows</strong> or <strong>Dagger</strong> (CI as code in TypeScript/Go/Python) which avoid the Groovy footgun.</p>
'''


ANSWERS[34] = r'''<p>Automated rollback in Kubernetes is mostly about <em>rollout halting</em> followed by <em>reverting the desired state</em>. The cluster never rolls back automatically on its own &mdash; <em>something</em> must observe failure and trigger the revert.</p>
<table>
<thead><tr><th>Layer</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Native Deployment</td><td><code>kubectl rollout undo deploy/api</code> reverts to the previous ReplicaSet; <code>progressDeadlineSeconds</code> marks rollout failed but does not auto-undo</td></tr>
<tr><td>Argo Rollouts</td><td><code>Rollout</code> resource with <code>analysis</code> steps queries Prometheus during a canary; failure aborts and traffic snaps back &mdash; closest thing to truly automatic</td></tr>
<tr><td>Flagger</td><td>Sister project to Linkerd/Istio; controls traffic shifting + auto-rollback based on success-rate and latency SLOs</td></tr>
<tr><td>Helm</td><td><code>helm upgrade --atomic --timeout 5m</code> rolls back the entire release on any failure during the upgrade</td></tr>
<tr><td>Argo CD</td><td><code>syncPolicy.automated.selfHeal</code> reverts manual drift; <code>resourceTrackingMethod</code> uses annotations to identify managed objects</td></tr>
<tr><td>Manual + paged</td><td>SLO burn-rate alert pages on-call &rarr; runbook step <code>kubectl rollout undo</code> &mdash; slowest, but always works as fallback</td></tr>
</tbody>
</table>
<p><strong>What "automatic" really means:</strong> the cluster needs three things &mdash; <em>signals</em> (metrics, traces, logs), a <em>policy</em> (thresholds defining "bad"), and an <em>actuator</em> (the controller that flips traffic or scale). Argo Rollouts and Flagger package all three. Without them, "auto-rollback" is just <code>helm --atomic</code>, which only catches Kubernetes-level failures (pods not starting), not application-level regressions.</p>
<p><strong>2026 best practice:</strong> ship with progressive delivery (Argo Rollouts/Flagger) for any user-facing service; define SLO-based <code>AnalysisTemplates</code> querying Prometheus / Datadog; require both a <em>technical</em> threshold (HTTP 5xx &lt; 0.5%) and a <em>product</em> threshold (conversion rate stable). Pair with feature flags (<strong>Unleash, OpenFeature, LaunchDarkly</strong>) so risky changes can be killed without redeploying.</p>
<p><strong>Pitfall:</strong> rollback breaks for irreversible changes &mdash; database schema migrations, message-format changes, deleted resources. Always design schema migrations in two phases (expand &rarr; deploy &rarr; contract) so any version delta between rolling pods is safe.</p>
'''


ANSWERS[35] = r'''<p>Build-and-deploy of containerised apps in GitHub Actions follows a canonical 5-step shape, with each step a well-known action.</p>
<table>
<thead><tr><th>Step</th><th>Action</th></tr></thead>
<tbody>
<tr><td>Checkout</td><td><code>actions/checkout@v4</code> (with <code>fetch-depth: 0</code> if you need git history)</td></tr>
<tr><td>Set up Buildx</td><td><code>docker/setup-buildx-action@v3</code> &mdash; modern multi-arch builder</td></tr>
<tr><td>Auth to registry</td><td><code>docker/login-action</code> for Docker Hub / GHCR; cloud-specific actions for ECR/GCR/ACR</td></tr>
<tr><td>Build &amp; push</td><td><code>docker/build-push-action@v6</code> with <code>cache-from/cache-to: type=gha,mode=max</code>; <code>docker/metadata-action</code> auto-generates tags</td></tr>
<tr><td>Deploy</td><td>Cloud-specific or <code>kubectl/helm</code> against the cluster &mdash; or push to a GitOps repo for Argo CD/Flux</td></tr>
</tbody>
</table>
<p><strong>Reference pipeline:</strong></p>
<pre><code>jobs:
  build:
    runs-on: ubuntu-latest
    permissions: { id-token: write, contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=,format=short
            type=ref,event=tag
            type=raw,value=latest,enable={{is_default_branch}}
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
          provenance: true
          sbom: true
</code></pre>
<p><strong>Hardening (2026):</strong> always set <code>provenance: true</code> + <code>sbom: true</code> &mdash; the action attaches SLSA attestation and SBOM as referrers in the registry. Add a <code>cosign sign --yes</code> step using GitHub OIDC (<code>permissions: id-token: write</code>) for keyless signing. Verify with <code>cosign verify --certificate-identity-regexp ...</code> at admission time via Kyverno.</p>
<p><strong>Speed levers:</strong> <code>cache-to: mode=max</code> caches all stages, not just final; pin base images to digests for stable cache keys; use <strong>Depot</strong> or <strong>Docker Build Cloud</strong> for cross-CI persistent cache + native multi-arch. Multi-stage Dockerfile alone often cuts cold-build time 50&mdash;80%.</p>
'''


ANSWERS[36] = r'''<p>Kustomize is template-free YAML composition: a <code>kustomization.yaml</code> declares <em>bases</em> (shared manifests) and <em>overlays</em> (environment-specific patches). The mechanism is <em>strategic merge patch</em> + <em>JSON patch</em> applied to base resources, producing rendered YAML that <code>kubectl apply -k</code> consumes.</p>
<table>
<thead><tr><th>Feature</th><th>Detail</th></tr></thead>
<tbody>
<tr><td><code>resources:</code></td><td>List of base manifests or other Kustomize dirs to compose</td></tr>
<tr><td><code>patches:</code></td><td>Strategic-merge or JSON-patch operations against named resources</td></tr>
<tr><td><code>configMapGenerator</code> / <code>secretGenerator</code></td><td>Generate ConfigMaps/Secrets with hash-suffix names; deps update automatically when content changes</td></tr>
<tr><td><code>commonLabels</code> / <code>commonAnnotations</code></td><td>Stamp labels across every resource (great for ownership labels)</td></tr>
<tr><td><code>images:</code></td><td>Override <code>image:</code> fields without editing each manifest &mdash; how CD updates the deployed tag</td></tr>
<tr><td><code>namespace:</code></td><td>Stamp namespace on every namespaced resource</td></tr>
<tr><td><code>replacements:</code></td><td>Cross-resource value injection (e.g. inject Service name into Deployment env)</td></tr>
<tr><td>Components</td><td>Reusable sub-bundles (e.g. "add Prometheus scraping") composable into multiple overlays</td></tr>
</tbody>
</table>
<p><strong>Typical layout:</strong></p>
<pre><code>k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── staging/   { kustomization.yaml &rarr; bases: [../../base], replicas patch, ConfigMap }
    └── prod/      { kustomization.yaml &rarr; bases: [../../base], replicas patch, HPA, PDB }
</code></pre>
<p><strong>vs Helm:</strong> Kustomize wins when you own the manifests (no templating syntax to escape, easier diffs); Helm wins for redistributable charts (parameters, values overlays for tenants, lifecycle hooks). Many teams use both: Helm for upstream ingress/cert-manager, Kustomize for own apps.</p>
<p><strong>2026 ecosystem:</strong> built into <code>kubectl</code> (<code>-k</code>), Argo CD, Flux, and OpenShift GitOps. <strong>kpt</strong> extends Kustomize with package management. <strong>Timoni</strong> brings CUE-typed bundles as a typed alternative. <strong>kustomize alpha localize</strong> resolves remote bases into a self-contained directory for airgapped use.</p>
<p><strong>Pitfalls:</strong> deeply nested bases &rarr; opaque output. Run <code>kustomize build overlays/prod</code> in CI and lint the result with <code>kubeconform</code> + <code>conftest</code>; the rendered YAML is what gets deployed.</p>
'''


ANSWERS[37] = r'''<p>Container startup time is dominated by image pull, runtime initialisation, and application warmup. Each has different optimisation levers.</p>
<table>
<thead><tr><th>Phase</th><th>Optimisation</th></tr></thead>
<tbody>
<tr><td>Image pull</td><td>Smaller images (distroless/chiseled), pre-pull on nodes via DaemonSet, <strong>image streaming</strong> (GKE Image Streaming, ECR pull-through cache), <code>imagePullPolicy: IfNotPresent</code>, registry mirror in-region</td></tr>
<tr><td>Container start</td><td>Static binaries (Go, Rust, GraalVM native-image) skip runtime/JIT; <code>CMD ["binary"]</code> not <code>CMD ["sh","-c","..."]</code>; <code>tini</code> only when you actually need PID 1 reaping</td></tr>
<tr><td>App warmup</td><td>JVM: AppCDS, CRaC checkpoint/restore. Node: cached <code>require</code> graph. Python: pre-imported modules. .NET: ReadyToRun + tiered JIT</td></tr>
<tr><td>Connection setup</td><td>Lazy-connect DBs/queues; readiness probe gates traffic until pools are warm</td></tr>
<tr><td>K8s scheduling</td><td>Topology spread + node affinity reduces pulls; PriorityClass speeds critical pods past noisy neighbours</td></tr>
</tbody>
</table>
<p><strong>2026 specific levers:</strong></p>
<ul>
<li><strong>JVM CRaC</strong> (Coordinated Restore at Checkpoint) &mdash; restore from a snapshot in milliseconds; supported by Spring Boot 3.2+, Quarkus, Helidon.</li>
<li><strong>GraalVM native-image</strong> &mdash; ahead-of-time compilation; ~50&mdash;100&times; faster startup at the cost of build time and reflection limitations.</li>
<li><strong>Lambda SnapStart</strong> for Java &mdash; same idea, AWS-managed.</li>
<li><strong>Lazy image pulling</strong> (<strong>SOCI snapshotter</strong> on EKS, <strong>stargz</strong>) &mdash; containers start before the full image is pulled.</li>
<li><strong>In-place pod resize</strong> (K8s 1.33 GA-track) &mdash; right-size requests without restart.</li>
</ul>
<p><strong>For CI/CD itself:</strong> agent pods (Jenkins K8s plugin, GH Actions runners) inherit the same gains. Pre-baked agent images with toolchain pre-installed cut per-build setup from minutes to seconds; pair with node-level image cache and Karpenter spot capacity.</p>
<p><strong>Measurement:</strong> instrument <code>container_start_time_seconds</code> + application <em>ready</em> timestamp in Prometheus; track p50/p99 cold-start as a deploy gate. Regressions usually trace to a base-image bump or a new heavy dependency.</p>
'''


ANSWERS[38] = r'''<p>Argo CD continuously reconciles a Kubernetes cluster toward declarative state in Git. The architecture: a Kubernetes-resident control plane (server, repo-server, application-controller, dex/sso) plus CRDs (<code>Application</code>, <code>ApplicationSet</code>, <code>AppProject</code>) that describe what to deploy, where, and from which Git source.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td><code>Application</code> CR</td><td>One app: source repo + path, target cluster + namespace, sync policy</td></tr>
<tr><td><code>ApplicationSet</code></td><td>Templates many Applications from generators (list, cluster, git directory, pull request)</td></tr>
<tr><td><code>AppProject</code></td><td>Tenant boundary: which sources, destinations, RBAC roles allowed</td></tr>
<tr><td>repo-server</td><td>Renders manifests from Helm/Kustomize/plain YAML/Jsonnet</td></tr>
<tr><td>application-controller</td><td>Watches live state vs desired; reports OutOfSync; applies if auto-sync enabled</td></tr>
<tr><td>argocd-server</td><td>API + web UI; SSO; CLI auth</td></tr>
</tbody>
</table>
<p><strong>Sync policies:</strong></p>
<ul>
<li><strong>Manual</strong> &mdash; controller observes only; humans click Sync.</li>
<li><strong>Automated</strong> &mdash; controller applies on each detected diff.</li>
<li><strong>Self-heal</strong> &mdash; reverts manual drift back to Git state.</li>
<li><strong>Prune</strong> &mdash; deletes resources removed from Git (off by default for safety).</li>
<li><strong>Sync waves &amp; hooks</strong> &mdash; ordered apply for CRDs &rarr; operators &rarr; instances.</li>
</ul>
<p><strong>Progressive delivery:</strong> pair with <strong>Argo Rollouts</strong> (sister project) for canary/blue-green of the underlying workload. Argo CD deploys the <code>Rollout</code> CR; Argo Rollouts handles traffic shifting and analysis.</p>
<p><strong>Multi-cluster (2026):</strong> ApplicationSet&rsquo;s cluster generator creates one Application per registered cluster; perfect for fleet rollouts. <strong>Argo CD Hub-and-Spoke</strong> with <strong>Cluster API</strong> (CAPI) for fleets &gt; 50 clusters. <strong>Kargo</strong> (CNCF, by the Argo team) layers promotion-pipeline semantics on top of Argo CD &mdash; PR-driven dev &rarr; staging &rarr; prod movement of pinned versions.</p>
<p><strong>Pitfalls:</strong> Helm charts with random/dynamic content (timestamps, generated names) cause endless OutOfSync &mdash; pin or use <code>ignoreDifferences</code>. Granting Argo CD <code>cluster-admin</code> on every cluster &mdash; scope per AppProject + per-namespace RBAC.</p>
'''


ANSWERS[39] = r'''<p>End-to-end testing in Jenkins runs the full deployed system &mdash; UI, API, DB, infra dependencies &mdash; against a realistic environment, after lower-level tests pass. The mechanism: stand up an ephemeral environment, run a slow but high-fidelity test suite, tear down.</p>
<table>
<thead><tr><th>Concern</th><th>Approach (2026)</th></tr></thead>
<tbody>
<tr><td>Environment</td><td>Ephemeral K8s namespace per build, or <strong>vCluster</strong> for full-cluster isolation; provisioned via Helm/Kustomize at start of stage, deleted in <code>post.always</code></td></tr>
<tr><td>Data</td><td>Anonymised prod snapshot restored to a fresh DB; or seed scripts; never share state across builds</td></tr>
<tr><td>Browser tests</td><td><strong>Playwright</strong> (preferred over Selenium); runs in headless container; reporters output JUnit XML for Jenkins</td></tr>
<tr><td>API contract tests</td><td><strong>Pact</strong>, <strong>Schemathesis</strong>, <strong>Postman/Newman</strong></td></tr>
<tr><td>Visual regression</td><td>Percy, Chromatic, Playwright snapshot mode</td></tr>
<tr><td>Mobile</td><td>Detox (RN), Maestro, Appium &mdash; usually runs against a deployed backend with mocked native shell</td></tr>
<tr><td>Reporting</td><td><code>publishHTML</code>, <code>junit</code>, <code>archiveArtifacts</code>; Allure plugin aggregates trends</td></tr>
</tbody>
</table>
<p><strong>Pipeline shape:</strong></p>
<ol>
<li>Build images, push to registry.</li>
<li><code>helm upgrade --install --namespace pr-${BUILD_ID}</code> &mdash; ephemeral env.</li>
<li>Wait for <code>kubectl rollout status</code> on all Deployments + readiness on Service URL.</li>
<li>Run E2E suite in parallel matrix (Playwright shards, separate browsers).</li>
<li>Capture videos/screenshots on failure as Jenkins artefacts; post summary to PR.</li>
<li>Tear down namespace in <code>post.always</code>.</li>
</ol>
<p><strong>Speed and stability:</strong> E2E tests are slow and flaky &mdash; treat them as a final gate, not a per-PR check on every change. Mark flaky tests via tags, retry sparingly (max 2&times;), surface flake rate as a quality metric. Use <strong>test impact analysis</strong> (Datadog CI Visibility, BuildPulse) to skip tests unaffected by the diff.</p>
<p><strong>2026 alternatives:</strong> teams increasingly run E2E in <strong>preview environments</strong> spun up automatically by Argo CD / Flux from PR branches, with the test suite triggered as a separate workflow. Decouples build-time from environment provisioning.</p>
'''


ANSWERS[40] = r'''<p>Multi-cloud deploys from GitHub Actions either fan one image out to multiple cloud targets in parallel or sequence cloud-specific deploys behind shared validation. The mechanism is <em>portable artefact + per-cloud auth + per-cloud deploy step</em>.</p>
<table>
<thead><tr><th>Cloud</th><th>Auth</th><th>Deploy</th></tr></thead>
<tbody>
<tr><td>AWS</td><td><code>aws-actions/configure-aws-credentials</code> via OIDC</td><td>EKS / ECS / Lambda / App Runner</td></tr>
<tr><td>GCP</td><td><code>google-github-actions/auth</code> via WIF</td><td>GKE / Cloud Run / Cloud Functions</td></tr>
<tr><td>Azure</td><td><code>azure/login</code> with federated credential</td><td>AKS / App Service / Container Apps / Functions</td></tr>
<tr><td>K8s anywhere</td><td>kubeconfig from secret manager, or in-cluster controller pulling from Git</td><td><code>kubectl apply</code> / <code>helm upgrade</code></td></tr>
</tbody>
</table>
<p><strong>Pattern A &mdash; Active/active fan-out:</strong> matrix job builds one image, pushes to multi-cloud registries (or one registry pulled by all clouds), then a deploy job per cloud runs in parallel. Suits global-traffic apps where each region serves users locally; the global router (Cloudflare / Fastly / Route 53 latency-based) directs traffic.</p>
<p><strong>Pattern B &mdash; Active/passive failover:</strong> primary cloud deploys first, smoke-passes, then secondary deploys. DR-shaped; saves cost.</p>
<p><strong>Pattern C &mdash; Per-tenant cloud:</strong> tenant config maps to a target cloud; matrix deploy across tenants.</p>
<p><strong>2026 enabling tooling:</strong></p>
<ul>
<li><strong>Crossplane</strong> &mdash; one Kubernetes control plane provisions cloud resources across all three; the workflow only needs <code>kubectl apply</code>.</li>
<li><strong>Terraform / OpenTofu / Pulumi</strong> with multi-cloud providers in one stack.</li>
<li><strong>Argo CD ApplicationSets</strong> with cluster generator &mdash; one Application per cluster, regardless of cloud; CI just updates Git.</li>
<li><strong>Fleet manager</strong> patterns &mdash; Rancher Fleet, Akuity, GitLab Agent &mdash; abstract per-cloud kubeconfig handling.</li>
</ul>
<p><strong>Pitfalls:</strong> divergent IAM models force per-cloud deploy code, multiplying maintenance. Cross-cloud egress is expensive &mdash; design data flows so each region stores and serves its own data. Compliance (data residency) often makes <em>true</em> active/active illegal; prefer regional active deploys with clear ownership per region.</p>
'''


ANSWERS[41] = r'''<p>Database migrations in CI/CD must be safe under concurrency (multiple app versions running during rollout) and reversible (or, more honestly, non-destructive). The mechanism is <em>versioned migrations + expand/contract pattern + automation</em>.</p>
<table>
<thead><tr><th>Concept</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Migration tool</td><td>Flyway, Liquibase (Java); Alembic (Python); <code>migrate</code>/<code>goose</code>/<code>atlas</code> (Go); Prisma, Drizzle, TypeORM (Node); Active Record (Rails); <strong>sqitch</strong> (DB-agnostic)</td></tr>
<tr><td>Version control</td><td>Migrations live alongside app code; numbered or timestamped; one-way only (no rollback files in prod)</td></tr>
<tr><td>When to run</td><td>Before app rollout, in a separate Job (K8s) / pre-release (Heroku) / hook (Helm)</td></tr>
<tr><td>Expand/contract</td><td>1) Add new column nullable; 2) Deploy app reading old + new; 3) Backfill; 4) Deploy app reading new only; 5) Drop old column. Each phase is a separate release.</td></tr>
<tr><td>Online schema change</td><td><code>pg-osc</code>, <code>gh-ost</code>, <code>pt-online-schema-change</code> for non-blocking large-table changes</td></tr>
</tbody>
</table>
<p><strong>K8s pattern:</strong> a <code>Job</code> with <code>restartPolicy: OnFailure</code> runs <code>flyway migrate</code> against the prod DB, gated to single-instance via a leader-elect mechanism. App Deployment&rsquo;s <code>readinessGate</code> (or Helm hook ordering) ensures app pods only start once migration completes.</p>
<p><strong>2026 advice:</strong></p>
<ul>
<li><strong>Atlas</strong> (Ariga) &mdash; declarative schema-as-code; CI computes diff vs target, prints planned changes, applies. Like Terraform for schemas.</li>
<li><strong>Bytebase / DbToolsBundle</strong> &mdash; database CD platforms with reviews, approvals, lint rules.</li>
<li><strong>Always-online migrations</strong> &mdash; large fintech/SaaS shops never take a maintenance window; expand/contract is the only legal pattern.</li>
<li><strong>Branch-per-developer DBs</strong> &mdash; <strong>Neon</strong>, <strong>PlanetScale</strong> branches give each PR a real schema branch; merge migrations as part of the PR.</li>
</ul>
<p><strong>Pitfalls:</strong> destructive migrations on rollback (drop a column the previous version still reads); long-running migrations that hold table locks; migrations conditional on data state, racing with live writes. Migration gates that block prod deploys for hours mean someone wrote 17 backfill statements in one file &mdash; refactor.</p>
'''


ANSWERS[42] = r'''<p>HPA scales pods horizontally between <code>minReplicas</code> and <code>maxReplicas</code> to keep one or more metrics near a target. Internals: an HPA controller polls metrics every 15s, computes <code>desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))</code>, and updates the Deployment&rsquo;s replica count subject to its <code>behavior</code> policy.</p>
<table>
<thead><tr><th>Metric type</th><th>Source</th><th>Use</th></tr></thead>
<tbody>
<tr><td>Resource (CPU, memory)</td><td>metrics-server</td><td>Default; CPU works well for compute-bound; memory is misleading for GC&rsquo;d languages</td></tr>
<tr><td>Pods (custom)</td><td>Custom Metrics API (Prometheus Adapter)</td><td>Per-pod metric averaged across pods, e.g. queue items per pod</td></tr>
<tr><td>Object</td><td>Custom Metrics API</td><td>Single metric on a non-pod object, e.g. Ingress RPS</td></tr>
<tr><td>External</td><td>External Metrics API (Prometheus Adapter, KEDA)</td><td>Outside-cluster signals, e.g. SQS depth, Kafka lag, Pub/Sub backlog</td></tr>
</tbody>
</table>
<p><strong>Behavior block:</strong> caps how fast HPA scales up vs down; <code>scaleDown.stabilizationWindowSeconds: 300</code> + per-minute pod caps prevents flapping. Defaults are aggressive on scale-down for many workloads.</p>
<p><strong>HPA + VPA together:</strong> never let both control the <em>same</em> resource. Pattern: <strong>VPA recommendation-only</strong> + <strong>HPA on CPU</strong>, or <strong>VPA-Initial on memory</strong> + <strong>HPA on a custom metric</strong>.</p>
<p><strong>2026 patterns:</strong></p>
<ul>
<li><strong>KEDA</strong> &mdash; event-driven autoscaling with 70+ built-in scalers (Kafka, NATS, RabbitMQ, SQS, Pub/Sub, Postgres, Cron, Prometheus). Generates a managed HPA underneath.</li>
<li><strong>HPA on custom RPS-per-pod</strong> &mdash; better correlation with real demand than CPU; requires Prometheus Adapter.</li>
<li><strong>Karpenter</strong> at the node level &mdash; HPA scaling drives Karpenter to provision nodes within seconds, not minutes.</li>
<li><strong>HPA + Argo Rollouts</strong> &mdash; the Rollout owns canary/blue-green; HPA scales each ReplicaSet independently.</li>
</ul>
<p><strong>Pitfalls:</strong> CPU target too high (90%) leaves no headroom for spikes; too low (30%) wastes money. Start at 60-70%. Missing readiness probes mean pods receive traffic before warmed up &mdash; HPA scales further to compensate, masking the problem.</p>
'''


ANSWERS[43] = r'''<p>Zero-downtime deploys require that <em>at all times</em> a healthy, ready pod is reachable and that the rollout itself does not drop in-flight requests. The mechanism layers across deployment strategy, traffic management, graceful shutdown, and database compatibility.</p>
<table>
<thead><tr><th>Layer</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Strategy</td><td>RollingUpdate with <code>maxSurge: 100%, maxUnavailable: 0</code>; or BlueGreen / Canary via Argo Rollouts</td></tr>
<tr><td>Health gates</td><td><code>readinessProbe</code> reflects true readiness (DB connected, caches warm); <code>livenessProbe</code> only catches deadlocks</td></tr>
<tr><td>Pre-stop drain</td><td><code>preStop: sleep 15</code> &mdash; lets endpoint controllers + load balancers deregister the pod before SIGTERM</td></tr>
<tr><td>Graceful shutdown</td><td>App handles SIGTERM: stop accepting new requests, finish in-flight, close pools, exit. <code>terminationGracePeriodSeconds</code> &gt; longest request</td></tr>
<tr><td>Connection draining</td><td>L4 LBs / Service mesh: deregister with pre-stop, drain on connection-level timeout</td></tr>
<tr><td>Schema compat</td><td>Expand/contract: app version N must be compatible with both old and new schema</td></tr>
<tr><td>Versioned APIs</td><td>Long-lived clients (mobile, partners) need contract stability across deploys</td></tr>
</tbody>
</table>
<p><strong>The pre-stop dance:</strong> Kubernetes is eventually consistent &mdash; when a pod terminates, the kubelet sends SIGTERM <em>and</em> the endpoints controller updates Service endpoints, but those happen concurrently. Without <code>preStop sleep N</code>, kube-proxy / Ingress controller may still route traffic to the dying pod for a few seconds. The sleep keeps the pod alive long enough for routes to converge.</p>
<p><strong>2026 polish:</strong></p>
<ul>
<li><strong>Argo Rollouts</strong> &mdash; canary with analysis runs against Prometheus; auto-abort on regression.</li>
<li><strong>Service mesh</strong> (Istio, Linkerd) &mdash; outlier detection ejects unhealthy pods within milliseconds.</li>
<li><strong>Topology-aware routing</strong> &mdash; keep traffic in-zone during partial rollout for lower latency.</li>
<li><strong>Feature flags</strong> &mdash; decouple deploy from release; risky behaviour rolls out behind a flag and can be killed instantly.</li>
</ul>
<p><strong>Pitfall:</strong> "zero downtime" claimed without measuring. Synthetic monitoring with 1-second resolution from a third location must show no error spike during deploys; if it does, the rollout strategy is theoretical.</p>
'''


ANSWERS[44] = r'''<p>Fluentd (and its lighter sibling Fluent Bit) collect, transform, and forward logs from Kubernetes pods to a central store. Architecture: a <strong>DaemonSet</strong> per node tails container logs from <code>/var/log/containers/*.log</code>, parses metadata, and ships to a backend.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Fluent Bit DaemonSet</td><td>Lightweight (C, ~5 MB) collector on every node; tails files, parses, forwards</td></tr>
<tr><td>Fluentd aggregators</td><td>Optional centralised tier (StatefulSet) for buffering, fan-out, expensive transforms; bigger memory footprint</td></tr>
<tr><td>Input plugins</td><td><code>tail</code> (containers), <code>systemd</code> (kubelet), <code>kubernetes_metadata</code> (decorate with pod labels)</td></tr>
<tr><td>Filter plugins</td><td>Parse JSON, redact PII, drop noisy lines, enrich with K8s metadata</td></tr>
<tr><td>Output plugins</td><td>Elasticsearch / OpenSearch, Loki, Splunk, S3, BigQuery, Datadog, Kafka</td></tr>
</tbody>
</table>
<p><strong>Standard installation (2026):</strong> the <strong>Fluent Operator</strong> manages Fluent Bit + Fluentd via CRDs (<code>FluentBit</code>, <code>ClusterInput</code>, <code>ClusterFilter</code>, <code>ClusterOutput</code>) &mdash; declarative, GitOps-friendly. Or use Helm chart <code>fluent/fluent-bit</code> for simpler setups.</p>
<p><strong>Fluentd vs Fluent Bit:</strong> Bit for collection (every node), Fluentd for aggregation/transform (a few replicas). Bit alone suffices for most setups; introduce Fluentd only when you need complex Ruby plugins or back-pressure smoothing.</p>
<p><strong>Storage backend trade-offs:</strong></p>
<ul>
<li><strong>Loki</strong> &mdash; index labels only, store body cheaply in S3; perfect for K8s logs (label = pod, namespace).</li>
<li><strong>Elasticsearch / OpenSearch</strong> &mdash; full-text search, expensive to operate; managed via OpenSearch Service / Elastic Cloud.</li>
<li><strong>Splunk / Datadog Logs / Sumo</strong> &mdash; SaaS, no ops, ingestion-priced; great until volume explodes.</li>
<li><strong>S3 + Athena / BigQuery</strong> &mdash; cold storage tier; cheapest, slowest queries.</li>
</ul>
<p><strong>2026 alternatives to Fluent stack:</strong> the <strong>OpenTelemetry Collector</strong> is rapidly absorbing log collection alongside metrics + traces &mdash; one agent, three signals. <strong>Vector</strong> (Datadog/Datadog) is a Rust-based, schema-aware competitor with strong performance. Fluent Bit remains the safest default for K8s but the field is consolidating around OpenTelemetry.</p>
'''


ANSWERS[45] = r'''<p>External-event triggers in GitHub Actions come from three primitives: <code>repository_dispatch</code>, <code>workflow_dispatch</code>, and <code>schedule</code> &mdash; plus webhook events GitHub already understands.</p>
<table>
<thead><tr><th>Trigger</th><th>Source</th><th>Use</th></tr></thead>
<tbody>
<tr><td><code>workflow_dispatch</code></td><td>UI / <code>gh workflow run</code> / API</td><td>Manual runs with typed inputs</td></tr>
<tr><td><code>repository_dispatch</code></td><td>External system POST to <code>/dispatches</code></td><td>Cross-repo signalling, third-party services</td></tr>
<tr><td><code>schedule</code></td><td>Cron expression</td><td>Periodic jobs (security scans, drift detection)</td></tr>
<tr><td><code>workflow_run</code></td><td>Another workflow finished</td><td>Chained pipelines</td></tr>
<tr><td><code>workflow_call</code></td><td>Reusable workflow invocation</td><td>Modularisation</td></tr>
<tr><td><code>pull_request_target</code></td><td>PR with secret access</td><td>Use carefully &mdash; runs in base repo context</td></tr>
<tr><td><code>release</code>, <code>discussion</code>, <code>issues</code>, <code>label</code></td><td>Built-in webhooks</td><td>Triggered by GitHub native events</td></tr>
</tbody>
</table>
<p><strong>External webhooks (2026 patterns):</strong></p>
<ul>
<li><strong>From a webhook to GitHub:</strong> external system POSTs to <code>https://api.github.com/repos/OWNER/REPO/dispatches</code> with a PAT or GitHub App token, custom <code>event_type</code>, and <code>client_payload</code>. Workflow listens with <code>on: repository_dispatch: types: [my-event]</code>.</li>
<li><strong>Cross-org / cross-repo:</strong> use a GitHub App (organisation-installed) to mint short-lived installation tokens, avoiding long-lived PATs.</li>
<li><strong>Datadog / PagerDuty / Slack</strong> &mdash; native integrations or webhook bridges; trigger remediation workflows from alerts.</li>
<li><strong>Argo Events</strong> &mdash; for Kubernetes-side bridging: any cloud event can fan into an Argo Workflow / Argo CD sync, then back to GitHub via PR.</li>
</ul>
<p><strong>Auth shape:</strong> incoming dispatch needs a token with <code>repo</code> scope (or <code>contents:write</code> for fine-grained PATs / GitHub App). Verify webhook signatures (HMAC) on any public-facing receiver to prevent forged triggers. Limit who can run <code>workflow_dispatch</code> via branch protection + required environments for sensitive flows.</p>
<p><strong>Pitfalls:</strong> <code>schedule</code> drifts &mdash; cron runs from a queue and can be delayed up to ~1 hour during GitHub-side incidents; don&rsquo;t use it for SLA-bound tasks. <code>pull_request_target</code> is dangerous if you check out the PR&rsquo;s code (RCE risk); use <code>pull_request</code> unless you specifically need secret access.</p>
'''


ANSWERS[46] = r'''<p>Multi-tenant CI/CD on Kubernetes isolates tenants at the namespace + RBAC + network + resource level, while sharing the cluster control plane. The CI/CD layer must respect those boundaries: per-tenant configs, per-tenant images, per-tenant deploys.</p>
<table>
<thead><tr><th>Isolation</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Namespace per tenant</td><td>Hard boundary for most resources</td></tr>
<tr><td>RBAC</td><td>Per-tenant <code>Role</code> + <code>RoleBinding</code>; ServiceAccounts scoped to namespace</td></tr>
<tr><td>NetworkPolicy</td><td>Default-deny; allow same-namespace + shared services</td></tr>
<tr><td>ResourceQuota + LimitRange</td><td>Cap CPU/memory/PVCs/object counts per tenant</td></tr>
<tr><td>PriorityClass</td><td>Different tiers per tenant; preemption follows class</td></tr>
<tr><td>Pod Security Admission</td><td><code>restricted</code> profile per namespace; Kyverno for finer rules</td></tr>
<tr><td>Multi-cluster (stronger)</td><td>vCluster, Capsule, Kamaji &mdash; virtual K8s control plane per tenant</td></tr>
</tbody>
</table>
<p><strong>CI/CD shape:</strong></p>
<ul>
<li><strong>Argo CD ApplicationSets</strong> with the cluster generator + tenant matrix &mdash; one Application per tenant per env auto-generated from a template.</li>
<li><strong>Per-tenant config</strong> in a tenants repo (Kustomize overlays or Helm values per tenant); CI never bakes tenant identity into images.</li>
<li><strong>Tenant onboarding as IaC</strong> &mdash; new tenant = PR adding a YAML row; controller provisions namespace + RBAC + quota + Argo Application.</li>
<li><strong>Image promotion</strong> &mdash; one base image, tenant-specific config injected at runtime via env/ConfigMap; never per-tenant Dockerfiles.</li>
</ul>
<p><strong>Operator-driven multi-tenancy:</strong> <strong>Capsule</strong> (CNCF) and <strong>Hierarchical Namespaces</strong> add a <code>Tenant</code> CR that automatically provisions namespace, RBAC, quotas, network policies. <strong>vCluster</strong> goes further: each tenant gets its own apiserver-as-a-pod inside a host namespace; tenant cluster-admin doesn&rsquo;t reach the host.</p>
<p><strong>2026 advice:</strong> namespace-per-tenant is fine for trusted tenants (internal teams, BU&rsquo;s); vCluster or full clusters per tenant for external/regulated/PII workloads. CI/CD platforms (<strong>Backstage</strong>, <strong>Port</strong>) provide self-service tenant onboarding with templated golden paths; expose only the controlled abstractions (Application, Database, Topic), not raw K8s primitives.</p>
'''


ANSWERS[47] = r'''<p>Jenkins Configuration as Code (JCasC) makes every Jenkins controller setting declarative YAML. The plugin reads <code>jenkins.yaml</code> (or a directory of YAMLs) at boot and applies it; the running configuration matches Git, full stop.</p>
<table>
<thead><tr><th>Domain</th><th>Configurable in YAML</th></tr></thead>
<tbody>
<tr><td>Global</td><td>System message, URL, executors, Markup formatter, environment variables</td></tr>
<tr><td>Security</td><td>Authorization strategy (Matrix, RBAC), security realm (LDAP, SAML, OIDC), CSRF, agent-master access control</td></tr>
<tr><td>Credentials</td><td>System and folder credentials sourced from Vault, AWS Secrets Manager, K8s Secrets via plugins</td></tr>
<tr><td>Tools</td><td>JDK, Maven, Gradle installations</td></tr>
<tr><td>Clouds</td><td>Kubernetes plugin pod templates; EC2 fleet templates</td></tr>
<tr><td>Plugins</td><td>Per-plugin schemas (Slack, Jira, GitHub, etc.)</td></tr>
<tr><td>Jobs</td><td>Via Job DSL plugin (separate but complementary)</td></tr>
</tbody>
</table>
<p><strong>Workflow:</strong> commit <code>jenkins.yaml</code> to a config repo; controller pod runs with <code>CASC_JENKINS_CONFIG</code> pointing at the file (or URL/folder). On boot, plugin applies. Live changes via UI are <em>discouraged</em> &mdash; either disable the UI for config or run <code>configuration-as-code reload</code> after edits to keep state in sync with YAML.</p>
<p><strong>Bootstrapping a fresh controller:</strong> a single command (Helm chart <code>jenkinsci/jenkins</code>, Operator Hub, or container with config volume) yields an identical Jenkins every time &mdash; same auth, same plugins, same agent pool. DR shrinks from <em>days</em> to <em>minutes</em>.</p>
<p><strong>2026 pattern:</strong></p>
<ul>
<li>YAML in Git, validated in CI by <code>jenkins-cli configuration-as-code check</code>.</li>
<li>Secrets via Vault / AWS Secrets Manager &mdash; never inline in YAML.</li>
<li>Plugin versions pinned in <code>plugins.txt</code>; install via <code>jenkins-plugin-cli</code> at image build.</li>
<li>Helm chart <code>jenkinsci/jenkins</code> with <code>controller.JCasC.configScripts</code> for K8s-native deploy.</li>
<li>Job DSL or <strong>Configuration as Code Plugin</strong> + <strong>shared-library</strong> for jobs themselves.</li>
</ul>
<p><strong>Honest 2026 advice:</strong> JCasC fixes the worst part of legacy Jenkins (untracked UI config), but it doesn&rsquo;t change Jenkins&rsquo;s fundamental architecture. Greenfield CI/CD increasingly skips Jenkins entirely &mdash; GitHub Actions / GitLab CI / Buildkite / Tekton are config-as-code by default. JCasC&rsquo;s value is highest in regulated environments where Jenkins is mandated.</p>
'''


ANSWERS[48] = r'''<p>Image security scanning in CI/CD compares image layers against CVE feeds and policy rules; failures gate the pipeline. Scans happen at build, registry push, and admission time &mdash; defence in depth.</p>
<table>
<thead><tr><th>Stage</th><th>Tool (2026)</th><th>What it does</th></tr></thead>
<tbody>
<tr><td>Build</td><td><strong>Trivy</strong>, Grype, Snyk, Anchore</td><td>Scan image filesystem + lockfiles for CVEs, secrets, IaC misconfig, license issues</td></tr>
<tr><td>SBOM generation</td><td>Syft, <code>docker sbom</code>, <code>buildx</code> with <code>sbom: true</code></td><td>SPDX/CycloneDX inventory attached to image as registry referrer</td></tr>
<tr><td>Sign</td><td>Cosign (Sigstore)</td><td>Keyless OIDC signature; verifiable in transparency log (Rekor)</td></tr>
<tr><td>Registry scan</td><td>Harbor, ECR enhanced scanning, Quay Clair, Docker Hub</td><td>Continuous re-scan as new CVEs are disclosed</td></tr>
<tr><td>Admission</td><td>Kyverno, Sigstore policy-controller, Connaisseur, Ratify</td><td>Cluster rejects unsigned/unscanned/policy-violating images</td></tr>
<tr><td>Runtime</td><td>Falco, Tetragon, Sysdig, Wiz Runtime</td><td>Detect anomalous syscalls, mounts, network egress on running containers</td></tr>
</tbody>
</table>
<p><strong>Failure gates:</strong> set severity thresholds (<code>--severity HIGH,CRITICAL</code>), exit-code 1 to fail the build. Allow exemptions only via labelled <code>.trivyignore</code> with expiry dates so they don&rsquo;t accumulate forever.</p>
<p><strong>SLSA + provenance (2026):</strong> the SLSA framework formalises supply-chain integrity. Level 3 requires hardened build platforms with tamper-evident provenance; <code>slsa-github-generator</code> attaches provenance attestation to images. Verifiers (Cosign, Kyverno, in-toto-attestation) check provenance + signer identity at admission.</p>
<p><strong>Reference build snippet:</strong></p>
<pre><code>- uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/acme/api:${{ github.sha }}
    format: sarif
    output: trivy.sarif
    exit-code: '1'
    severity: HIGH,CRITICAL
    ignore-unfixed: true
- uses: github/codeql-action/upload-sarif@v3
  with: { sarif_file: trivy.sarif }
</code></pre>
<p><strong>Common pitfall:</strong> running scanners but not failing the build, then ignoring the dashboard. CVEs accumulate; one day an exploited CVE blames the team for "knowing about it." Either gate the build or commit to a 30-day SLA on remediation, tracked in a security backlog.</p>
'''


ANSWERS[49] = r'''<p>NetworkPolicies are firewall rules <em>at the pod level</em> &mdash; the Kubernetes-native way to express "service A may talk to service B on port 5432" without iptables hand-rolling. Default behaviour is permissive; once a policy selects a pod, only matching traffic is allowed.</p>
<table>
<thead><tr><th>Concept</th><th>Detail</th></tr></thead>
<tbody>
<tr><td><code>podSelector</code></td><td>Which pods this policy applies to</td></tr>
<tr><td><code>policyTypes</code></td><td><code>Ingress</code>, <code>Egress</code>, or both</td></tr>
<tr><td><code>ingress.from</code> / <code>egress.to</code></td><td>Allowed peers: <code>podSelector</code>, <code>namespaceSelector</code>, <code>ipBlock</code></td></tr>
<tr><td><code>ports</code></td><td>Allowed protocols + port numbers</td></tr>
<tr><td>Default-deny</td><td>An empty <code>podSelector</code> + <code>policyTypes: [Ingress, Egress]</code> blocks everything not explicitly allowed</td></tr>
</tbody>
</table>
<p><strong>Best practice baseline (2026):</strong> apply <em>default-deny ingress + egress</em> in every namespace, then add explicit allow rules. Allow DNS to <code>kube-dns</code>, allow same-namespace within a tier, allow specific cross-namespace flows by label.</p>
<p><strong>What NetworkPolicy can&rsquo;t do natively:</strong> L7 (HTTP method, path, headers), encryption, identity beyond pod labels. For those:</p>
<ul>
<li><strong>Cilium NetworkPolicy / CiliumClusterwideNetworkPolicy</strong> &mdash; eBPF-based; adds L7 (HTTP, gRPC, Kafka) policies, FQDN-based egress (allow only <code>api.stripe.com</code>), and identity-based rules.</li>
<li><strong>Calico Enterprise / Tigera</strong> &mdash; richer policy + flow logs; multi-cluster federation.</li>
<li><strong>Service mesh (Istio AuthorizationPolicy, Linkerd)</strong> &mdash; mTLS-based identity; finer than IP/label.</li>
</ul>
<p><strong>CNI requirement:</strong> NetworkPolicy is implemented by the CNI plugin, not Kubernetes core. Calico, Cilium, Antrea, Weave Net all support it; Flannel without an extension does not. Most managed K8s (EKS with VPC CNI + add-on, GKE Dataplane v2, AKS) ship a supporting CNI.</p>
<p><strong>Operating pitfalls:</strong> empty selectors that accidentally match all pods (lockout), forgetting to allow DNS (every workload breaks), ingress without egress (one-way pain). Test with <code>kubectl exec ... -- nc -zv</code> from neighbour pods, and use <strong>Cilium Hubble</strong> or <strong>Antrea Theia</strong> for visibility before flipping default-deny.</p>
'''


ANSWERS[50] = r'''<p>AKS deploys from GitHub Actions follow the standard build-push-deploy pattern with Azure-specific auth and integration. Two paths: direct <code>kubectl</code>/<code>helm</code> apply, or push-to-GitOps (Argo CD/Flux).</p>
<table>
<thead><tr><th>Stage</th><th>Action / detail</th></tr></thead>
<tbody>
<tr><td>Auth</td><td><code>azure/login@v2</code> with federated credential (OIDC) on a User-Assigned Managed Identity; no client secret in repo</td></tr>
<tr><td>Build/push</td><td><code>docker buildx build --push</code> to Azure Container Registry (ACR); auth via <code>az acr login --name &lt;acr&gt;</code> after Azure login</td></tr>
<tr><td>Cluster credentials</td><td><code>az aks get-credentials -n &lt;cluster&gt; -g &lt;rg&gt;</code> writes kubeconfig with <code>kubelogin</code> + Entra ID auth</td></tr>
<tr><td>Deploy</td><td><code>kubectl apply -k overlays/prod</code> or <code>helm upgrade --install --atomic</code></td></tr>
<tr><td>Verify</td><td><code>kubectl rollout status</code> and smoke test</td></tr>
</tbody>
</table>
<p><strong>Reference workflow:</strong></p>
<pre><code>permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id:       ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id:       ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az acr login --name acmeacr
      - run: docker buildx build --push -t acmeacr.azurecr.io/api:${{ github.sha }} .
      - run: az aks get-credentials -n acme-aks -g acme-rg --overwrite-existing
      - run: kubectl set image deploy/api api=acmeacr.azurecr.io/api:${{ github.sha }}
      - run: kubectl rollout status deploy/api --timeout=5m
</code></pre>
<p><strong>AKS-specific levers (2026):</strong></p>
<ul>
<li><strong>Workload Identity</strong> &mdash; pod-level Entra ID auth (replaces deprecated AAD Pod Identity); the workload SA federates to a Managed Identity for Azure resource access.</li>
<li><strong>GitOps via Flux extension</strong> &mdash; built-in AKS extension installs Flux; Microsoft-supported, auto-updated.</li>
<li><strong>Azure Service Operator (ASO v2)</strong> &mdash; provision Azure resources (storage, DBs, queues) as Kubernetes CRs; one control plane.</li>
<li><strong>Karpenter Azure provider</strong> &mdash; GA in 2026; replaces Cluster Autoscaler with on-demand node provisioning; cuts capacity costs.</li>
<li><strong>NAP (Node Auto Provisioning)</strong> &mdash; Microsoft-managed Karpenter, no controller to operate.</li>
</ul>
<p><strong>Pitfalls:</strong> long-lived service principal secrets in repo &mdash; switch to OIDC. Granting <code>Contributor</code> at subscription scope &mdash; bind RBAC tightly to the resource group. Forgetting <code>kubelogin</code> when targeting Entra-integrated clusters &mdash; <code>az aks get-credentials</code> handles this since 2024 but older runners may need explicit <code>kubelogin convert-kubeconfig</code>.</p>
'''

ANSWERS[51] = r'''<p>Multi-stage deployments in Jenkins represent the journey of a build artefact through environments &mdash; usually <code>dev &rarr; qa &rarr; staging &rarr; prod</code> &mdash; with quality gates between each. The mechanism is <em>one immutable artefact, many environments, gated promotion</em>.</p>
<table>
<thead><tr><th>Stage</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Build (once)</td><td>Compile, test, package; emit one artefact tagged by commit SHA</td></tr>
<tr><td>Deploy to dev</td><td>Auto on merge to <code>main</code>; runs smoke + contract tests</td></tr>
<tr><td>Promote to QA</td><td><code>input</code> step requiring QA team approval; same artefact, different config</td></tr>
<tr><td>Promote to staging</td><td>Pre-prod load + E2E tests; auto-promote on green</td></tr>
<tr><td>Promote to prod</td><td>Manual <code>input</code> with required submitters; canary or blue/green within prod</td></tr>
</tbody>
</table>
<p><strong>Reference Declarative skeleton:</strong></p>
<pre><code>pipeline {
  options { timeout(time: 6, unit: 'HOURS') }
  stages {
    stage('Build')   { steps { sh 'make build && make image-push' } }
    stage('Dev')     { steps { sh 'helm upgrade api ./chart -f dev.yaml --set image.tag=$GIT_COMMIT' } }
    stage('QA Gate') { steps { input message: 'Promote to QA?', submitter: 'qa-team' } }
    stage('QA')      { steps { sh 'helm upgrade ... -f qa.yaml ...' } }
    stage('Staging') { steps { sh 'helm upgrade ... -f staging.yaml ...' } }
    stage('Prod Gate'){ steps { input message: 'Deploy to prod?', submitter: 'release-managers' } }
    stage('Prod')    { steps { sh 'kubectl argo rollouts set image rollout/api api=$IMAGE' } }
  }
  post { failure { slackSend(channel:'#deploys', color:'danger', message:"Failed: ${env.BUILD_URL}") } }
}
</code></pre>
<p><strong>2026 patterns:</strong></p>
<ul>
<li><strong>Promotion-as-PR</strong> &mdash; Jenkins opens a PR against the GitOps config repo bumping the image tag; merge triggers Argo CD sync. Better audit, no live <code>kubectl</code> from CI.</li>
<li><strong>Kargo</strong> (CNCF/Argo) &mdash; promotion pipelines as CRDs; replaces hand-rolled Jenkinsfiles for the gating logic, while Jenkins still does build.</li>
<li><strong>Spinnaker</strong> &mdash; specialised multi-cloud CD with pipelines as first-class objects; pair with Jenkins for build.</li>
</ul>
<p><strong>Pitfalls:</strong> rebuilding between stages &mdash; means staging and prod aren&rsquo;t bit-for-bit identical (base image drift, dep version drift). Build once, promote artefacts. Manual <code>input</code> blocks executors indefinitely; combine with <code>timeout</code> + auto-abort. Stages that touch shared resources (DB schema, queue topics) need cross-stage coordination &mdash; expand/contract pattern, not "let&rsquo;s migrate at staging".</p>
'''


ANSWERS[52] = r'''<p>DaemonSets ensure a copy of a Pod runs on <em>every</em> node (or every node matching a selector). They&rsquo;re the standard Kubernetes primitive for system-level workloads &mdash; one-per-node agents that need direct host access.</p>
<table>
<thead><tr><th>Use case</th><th>Examples (2026)</th></tr></thead>
<tbody>
<tr><td>Log collection</td><td>Fluent Bit, Vector, OpenTelemetry Collector (logs)</td></tr>
<tr><td>Metrics collection</td><td>node-exporter, cAdvisor (built into kubelet), DCGM exporter for GPUs</td></tr>
<tr><td>Networking</td><td>Cilium, Calico, kube-proxy (in non-eBPF setups), Multus</td></tr>
<tr><td>Storage</td><td>CSI node plugins (EBS, GCE-PD, Longhorn, Rook/Ceph)</td></tr>
<tr><td>Security</td><td>Falco, Tetragon, Trivy operator scanner, OSquery</td></tr>
<tr><td>Service mesh data plane</td><td>Istio Ambient ztunnel, Linkerd-CNI, Cilium service mesh</td></tr>
</tbody>
</table>
<p><strong>Mechanism:</strong> the DaemonSet controller watches Node objects; for each Node matching <code>spec.template.spec.nodeSelector</code> + tolerations, it creates a Pod with that node hard-pinned via <code>nodeAffinity</code>. New nodes auto-receive the Pod; deleted nodes&rsquo; Pods are GC&rsquo;d.</p>
<p><strong>Common spec features:</strong></p>
<ul>
<li><code>tolerations</code> &mdash; tolerate <code>node-role.kubernetes.io/control-plane</code>, <code>node.kubernetes.io/not-ready</code>, GPU taints; agents must run on <em>all</em> nodes including tainted ones.</li>
<li><code>hostNetwork: true</code> + <code>hostPID: true</code> &mdash; for agents that need to see host-level processes/sockets.</li>
<li><code>volumes: hostPath</code> &mdash; mount <code>/var/log/containers</code>, <code>/proc</code>, <code>/sys</code>; usually with <code>readOnly: true</code>.</li>
<li><code>updateStrategy: RollingUpdate</code> with <code>maxUnavailable: 1</code> for safe rollouts; <code>OnDelete</code> when version compatibility matters.</li>
<li><code>priorityClassName: system-node-critical</code> &mdash; protects critical agents from preemption.</li>
</ul>
<p><strong>Trade-offs:</strong> DaemonSets compete for node resources; large agents (full Datadog, full Splunk) measurably reduce app capacity. Pod Security Admission <code>restricted</code> doesn&rsquo;t allow <code>hostPath</code> &mdash; system-level DaemonSets need exemption labels (<code>pod-security.kubernetes.io/enforce: privileged</code>) on their namespace.</p>
<p><strong>2026 advice:</strong> consolidate on one OpenTelemetry Collector DaemonSet for logs+metrics+traces rather than three separate agents; use <strong>eBPF</strong> agents (Cilium, Pixie, Parca) for low-overhead instrumentation. Reserve DaemonSets for actual node-level needs &mdash; per-app sidecars belong as Pod sidecars (or service mesh injection), not DaemonSets.</p>
'''


ANSWERS[53] = r'''<p>Hybrid cloud CI/CD spans on-prem + cloud, often because data-residency or latency requires on-prem workloads while cloud handles bursty/global services. GitHub Actions sits in cloud; on-prem is reached via self-hosted runners or push-to-GitOps targeting both.</p>
<table>
<thead><tr><th>Pattern</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Self-hosted runners on-prem</td><td>Runner pods inside the on-prem K8s cluster; GitHub-hosted control plane dispatches jobs over outbound HTTPS &mdash; no inbound holes</td></tr>
<tr><td>Cloud-hosted runners + bastion</td><td>GitHub-hosted runner uses VPN / Tailscale / bastion to reach on-prem; simpler, more attack surface</td></tr>
<tr><td>GitOps both sides</td><td>Argo CD / Flux on both clusters; CI just commits manifests; controllers pull</td></tr>
<tr><td>Bridged via control-plane SaaS</td><td>Akuity, Codefresh, Spectro Cloud act as fleet manager spanning both; GH Actions pushes to them</td></tr>
</tbody>
</table>
<p><strong>2026 self-hosted runner stack:</strong></p>
<ul>
<li><strong>Actions Runner Controller (ARC)</strong> &mdash; official K8s operator; ephemeral runners as Pods, scaled by workflow demand; runs on-prem clusters or any K8s.</li>
<li><strong>Auto-scaling</strong> via webhook listener + <code>RunnerScaleSet</code>; idle runners cost nothing.</li>
<li><strong>Network egress only</strong>: runners dial out to <code>actions.github.com</code>; no inbound firewall changes.</li>
<li><strong>Hardening</strong>: ephemeral (one-job lifetime), seccomp/AppArmor profiles, network policies restricting egress to known endpoints, secrets via Vault/CSI driver.</li>
</ul>
<p><strong>Workflow shape:</strong> <code>runs-on: [self-hosted, on-prem, linux]</code> dispatches to on-prem runners that can reach private DNS, internal registries, on-prem K8s. Cloud-targeted jobs use GitHub-hosted runners with OIDC to AWS/GCP/Azure. Matrix and conditional <code>runs-on</code> let one workflow target both.</p>
<p><strong>Pitfalls:</strong> shared runners across teams &mdash; one team&rsquo;s leaked secret poisons the build cache. Use ephemeral runners with no persistent state. Static PATs as runner registration tokens &mdash; use GitHub App auth via <code>actions-runner-controller</code> instead. Network egress whitelist drift &mdash; document required GitHub IP ranges (Microsoft publishes them) and review quarterly.</p>
<p><strong>Honest 2026 advice:</strong> "hybrid cloud" pure-on-prem K8s + cloud K8s is mostly a transitional state; new workloads default cloud, legacy stays on-prem. The CI/CD lift is real but not unique &mdash; same patterns work for "cloud A + cloud B." Pick GitOps + ARC and the topology becomes mostly invisible to pipelines.</p>
'''


ANSWERS[54] = r'''<p>Container resource optimisation in CI/CD touches build speed (smaller images = faster pulls = faster deploys) and runtime cost (right-sized requests = better bin-packing). Both flow from instrumentation, not guesswork.</p>
<table>
<thead><tr><th>Lever</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Image size</td><td>Multi-stage builds, distroless / chiseled / scratch base, <code>.dockerignore</code>, AOT compile (Go, Rust, GraalVM)</td></tr>
<tr><td>Layer caching</td><td>BuildKit + <code>--mount=type=cache</code>, GHA cache backend, Buildx remote cache, Depot</td></tr>
<tr><td>Build parallelism</td><td>Multi-stage DAG; <strong>Bazel/Pants</strong> for cross-language graphs</td></tr>
<tr><td>Container runtime size</td><td>Static binaries, AOT compile, JVM CRaC / GraalVM, .NET ReadyToRun</td></tr>
<tr><td>Right-sizing requests</td><td>VPA in <em>recommend-only</em> mode + Goldilocks dashboard</td></tr>
<tr><td>Bin-packing</td><td>Karpenter consolidation, scheduler topology spread, <code>NodeAffinity</code></td></tr>
<tr><td>Spot capacity</td><td>Karpenter spot pools, preemption-tolerant workloads, PDBs</td></tr>
</tbody>
</table>
<p><strong>Right-sizing pipeline:</strong> deploy <strong>VPA</strong> in <code>updateMode: Off</code> (recommend only). After a week, read <code>VerticalPodAutoscaler</code> recommendations and update Deployment requests to the <code>target</code> values. Repeat monthly. <strong>Goldilocks</strong> from Fairwinds visualises this; <strong>Datadog Container Workload Recommendations</strong> and <strong>Kubecost</strong> automate it across the cluster.</p>
<p><strong>2026 specific:</strong></p>
<ul>
<li><strong>In-place pod resize</strong> (K8s 1.33 GA-track) &mdash; right-size requests without restart; combine with VPA in non-disruptive mode.</li>
<li><strong>Karpenter consolidation</strong> &mdash; bin-packs pods across spot/on-demand, evicts from underutilised nodes; cuts compute spend 30-60%.</li>
<li><strong>SOCI snapshotter</strong> &mdash; lazy image pulling; pods start before full pull completes.</li>
<li><strong>JVM CRaC + class-data sharing</strong> &mdash; Spring Boot startup &lt; 1s in production; lower memory footprint.</li>
<li><strong>WASM workloads</strong> (SpinKube, Fermyon) &mdash; sub-millisecond cold starts where applicable.</li>
</ul>
<p><strong>CI-side benefits:</strong> smaller images cut <em>kubelet image pull time</em> on rolling deploys (the largest contributor to deploy duration in many setups). Test it: instrument Prometheus metric <code>container_image_pull_seconds</code>, plot p99 over the last 7 days, and watch it fall when distroless lands.</p>
<p><strong>Pitfall:</strong> cargo-cult shrinking ("now we use scratch!") that breaks observability and debugging tools. Distroless <code>:debug</code> variants ship with a shell for emergencies; use them in dev images, strip in prod.</p>
'''


ANSWERS[55] = r'''<p>Spinnaker is a continuous-delivery platform purpose-built for multi-cloud, multi-cluster pipelines. The mechanism is <em>pipeline-as-data</em>: declarative pipelines (JSON / Pipelines-as-Code) executed by a microservices control plane, with first-class concepts for clouds, accounts, and deployment strategies.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Deck</td><td>UI</td></tr>
<tr><td>Gate</td><td>API gateway</td></tr>
<tr><td>Orca</td><td>Pipeline orchestrator</td></tr>
<tr><td>Clouddriver</td><td>Cloud abstraction (AWS/GCP/Azure/K8s/Cloud Foundry)</td></tr>
<tr><td>Front50</td><td>Pipeline / app metadata store (Cassandra, Redis, S3, GCS)</td></tr>
<tr><td>Igor / Echo / Kayenta / Halyard</td><td>CI integration / events / canary analysis / installer</td></tr>
</tbody>
</table>
<p><strong>Strengths:</strong></p>
<ul>
<li><strong>Deployment strategies</strong> &mdash; red/black, canary, rolling red/black, highlander &mdash; built in, configurable per stage.</li>
<li><strong>Automated canary analysis (Kayenta)</strong> &mdash; statistical comparison of canary vs baseline metrics from Prometheus / Datadog / Stackdriver.</li>
<li><strong>Multi-cloud</strong> &mdash; same pipeline targets EKS, GKE, AKS, Cloud Foundry, EC2, Cloud Run.</li>
<li><strong>Pipelines-as-Code</strong> &mdash; pipelines stored as JSON / Pipelines-as-Code YAML in Git; reviewed via PR.</li>
<li><strong>Manual judgments</strong> &mdash; explicit human approval gates with stakeholder routing.</li>
</ul>
<p><strong>K8s deploy flow:</strong> trigger (Jenkins build, GitHub webhook, Pub/Sub) &rarr; bake stage (Helm/Kustomize render) &rarr; deploy manifest stage &rarr; canary stage with Kayenta &rarr; manual judgment &rarr; deploy to next region.</p>
<p><strong>Honest 2026 reality:</strong> Spinnaker&rsquo;s heyday was 2018-2021 (Netflix, Pinterest, Salesforce). Operational complexity (~10 microservices, Cassandra, Redis, S3) is heavy; the modern equivalents are simpler:</p>
<ul>
<li><strong>Argo CD + Argo Rollouts + Kargo</strong> &mdash; covers most Spinnaker capabilities with a Kubernetes-native footprint.</li>
<li><strong>Harness CD</strong> &mdash; commercial Spinnaker successor; cleaner UX, AI-driven verifications.</li>
<li><strong>Codefresh GitOps Cloud (Argo)</strong> &mdash; managed Argo with promotion pipelines.</li>
<li><strong>Cloud Deploy</strong> (GCP) &mdash; managed delivery service.</li>
</ul>
<p>Pick Spinnaker only if you have multi-cloud (truly multi-cloud, not multi-region) <em>and</em> a platform team to operate it. Greenfield K8s shops should default to Argo CD + Argo Rollouts + Kargo.</p>
'''


ANSWERS[56] = r'''<p>Jenkins handles secrets and environment variables through a layered system: <strong>Credentials Plugin</strong> stores secrets, <strong>Pipeline syntax</strong> binds them, and <strong>external providers</strong> mint short-lived secrets at runtime.</p>
<table>
<thead><tr><th>Mechanism</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Credentials Store</td><td>Encrypted on disk; types: secret text, username/password, SSH key, certificate, file, AWS, Docker</td></tr>
<tr><td>Scope</td><td>Global, folder-level, or job-level &mdash; tighter scope = blast-radius reduction</td></tr>
<tr><td><code>environment {}</code></td><td>Declarative block injecting <code>credentials('id')</code> as env var; auto-masked in logs</td></tr>
<tr><td><code>withCredentials([...])</code></td><td>Scripted block; binds secret to a variable for nested steps only</td></tr>
<tr><td>External providers</td><td>HashiCorp Vault Plugin, AWS Secrets Manager Credentials Provider, Azure Key Vault, K8s Secrets via CredentialsBinding</td></tr>
</tbody>
</table>
<p><strong>Standard pattern (Declarative):</strong></p>
<pre><code>pipeline {
  agent any
  environment {
    DOCKER_CREDS = credentials('docker-hub')   // exposes USR + PSW
    DB_PASSWORD  = credentials('prod-db-pw')
  }
  stages {
    stage('Push') {
      steps {
        sh 'echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin'
        sh 'docker push acme/app:latest'
      }
    }
    stage('Migrate') {
      steps {
        withCredentials([string(credentialsId: 'vault-token', variable: 'VAULT_TOKEN')]) {
          sh &apos;&apos;&apos;
            export VAULT_ADDR=https://vault.internal
            DB_PW=$(vault kv get -field=password secret/db/prod)
            flyway -password="$DB_PW" migrate
          &apos;&apos;&apos;
        }
      }
    }
  }
}
</code></pre>
<p><strong>2026 hardening:</strong></p>
<ul>
<li><strong>Vault as primary store</strong> &mdash; Jenkins holds only a Vault auth credential; everything else fetched at job start with TTL minutes.</li>
<li><strong>OIDC + cloud secret managers</strong> &mdash; agents run with K8s ServiceAccounts annotated for IRSA / Workload Identity; AWS / GCP / Azure SDKs auto-discover, no Jenkins-stored cloud keys.</li>
<li><strong>Folder-scoped credentials</strong> &mdash; teams only see their own; combined with RBAC plugin.</li>
<li><strong>Mask Passwords + Pipeline log redaction</strong> &mdash; default; verify by including a known secret in test output and confirming <code>****</code>.</li>
</ul>
<p><strong>Pitfalls:</strong> echoing secrets via <code>env</code> command (logs everything) &mdash; never do this. Secrets in <code>parameters</code> (visible to anyone with build access) &mdash; use credential parameters or look up from Vault. Long-lived static creds &mdash; rotate, or eliminate via dynamic backends.</p>
'''


ANSWERS[57] = r'''<p>Kubernetes RBAC governs what subjects (users, groups, ServiceAccounts) can do on which resources. The mechanism is <em>Role + RoleBinding</em> within a namespace, or <em>ClusterRole + ClusterRoleBinding</em> cluster-wide. Authorization is additive &mdash; multiple bindings union; there&rsquo;s no deny.</p>
<table>
<thead><tr><th>Object</th><th>Scope</th><th>Use</th></tr></thead>
<tbody>
<tr><td>Role</td><td>Namespace</td><td>Allowed verbs (get, list, watch, create, update, patch, delete) on resources within the namespace</td></tr>
<tr><td>ClusterRole</td><td>Cluster</td><td>Same, but cluster-wide; also used for non-namespaced resources (Nodes, PVs, CRDs)</td></tr>
<tr><td>RoleBinding</td><td>Namespace</td><td>Binds Role (or ClusterRole) to subjects, scoped to the binding&rsquo;s namespace</td></tr>
<tr><td>ClusterRoleBinding</td><td>Cluster</td><td>Binds ClusterRole to subjects, cluster-wide</td></tr>
<tr><td>ServiceAccount</td><td>Namespace</td><td>Identity for pods; default token mounted unless <code>automountServiceAccountToken: false</code></td></tr>
</tbody>
</table>
<p><strong>Typical patterns:</strong></p>
<ul>
<li><strong>Per-namespace dev access</strong>: bind a <code>developer</code> ClusterRole (read pods/logs/exec, create configmaps) via RoleBinding in their namespace; admins use ClusterRoleBinding with the same ClusterRole only for cluster-admins.</li>
<li><strong>CI/CD ServiceAccount</strong>: namespace-scoped SA with permission to <code>create/update/patch deployments,services,ingresses</code> in its namespace; never <code>cluster-admin</code>.</li>
<li><strong>Aggregated ClusterRoles</strong>: <code>aggregationRule</code> auto-collects rules from labelled ClusterRoles; how the default <code>view/edit/admin/cluster-admin</code> roles work.</li>
</ul>
<p><strong>Auth flow:</strong> apiserver authenticates the request (X.509 cert, bearer token, OIDC, webhook), then runs the authorization chain (RBAC + others); RBAC checks every <code>verb</code>+<code>resource</code> against bindings. <code>kubectl auth can-i create deployments -n prod</code> tells you the answer for the current user.</p>
<p><strong>2026 hardening:</strong></p>
<ul>
<li><strong>OIDC integration</strong> &mdash; AWS IAM Identity Center, Entra ID, Google Workspace, Okta as identity provider; group memberships drive RBAC bindings, not per-user.</li>
<li><strong>Pod Identity / IRSA / Workload Identity Federation</strong> &mdash; pods get cloud IAM roles via SA annotations; no static cloud keys.</li>
<li><strong>OPA Gatekeeper / Kyverno</strong> &mdash; ABAC-style policy on top of RBAC for invariants RBAC can&rsquo;t express ("no privileged pods", "all images from approved registry").</li>
<li><strong>Audit logging</strong> to a SIEM &mdash; every <code>kubectl exec</code>/<code>delete</code> in prod is reviewed.</li>
</ul>
<p><strong>Pitfalls:</strong> wildcard verbs (<code>verbs: ["*"]</code>) on a "tools" namespace that someone hops into prod from. Granting permission on <code>secrets</code> when <code>configmaps</code> would do. ServiceAccount tokens projected into pods that don&rsquo;t need them &mdash; set <code>automountServiceAccountToken: false</code> by default.</p>
'''


ANSWERS[58] = r'''<p>Argo CD + GitHub Actions splits responsibilities cleanly: <strong>GitHub Actions = CI</strong> (build, test, push image, write manifest tag), <strong>Argo CD = CD</strong> (pull from Git, reconcile cluster). Neither tool needs the other&rsquo;s permissions.</p>
<table>
<thead><tr><th>Repo</th><th>Owner</th><th>Contents</th></tr></thead>
<tbody>
<tr><td>App repo</td><td>App team</td><td>Source code, Dockerfile, Helm chart values, CI workflow</td></tr>
<tr><td>Config repo</td><td>Platform / app team</td><td>Argo CD <code>Application</code> + <code>ApplicationSet</code> CRs; environment-specific Kustomize overlays / Helm values</td></tr>
</tbody>
</table>
<p><strong>Workflow:</strong></p>
<ol>
<li>Developer merges to <code>main</code>.</li>
<li>GitHub Actions builds image, pushes to registry tagged <code>git-${SHA}</code>.</li>
<li>Workflow either (a) commits a tag bump in the config repo, or (b) calls Argo CD&rsquo;s API directly with <code>argocd app set api --helm-set image.tag=${SHA}</code>, or (c) lets <strong>Argo CD Image Updater</strong> watch the registry and write the bump itself.</li>
<li>Argo CD application-controller observes the change, computes diff, applies to the target cluster.</li>
<li>Argo Rollouts (if used) progressively rolls out, halting on failed analysis.</li>
</ol>
<p><strong>Two integration models:</strong></p>
<ul>
<li><strong>Push (GH Actions writes config)</strong>: deterministic; full pipeline visible in Actions UI; SHA traceable from app repo &rarr; config commit &rarr; Argo sync.</li>
<li><strong>Pull (Image Updater watches registry)</strong>: lower coupling; CI doesn&rsquo;t need write access to config repo; harder to trace which app commit triggered which deploy.</li>
</ul>
<p><strong>Promotion across environments:</strong> dev tag bump auto-merged; staging/prod via PR with required reviewers (GitHub branch protection on the config repo). Or use <strong>Kargo</strong> &mdash; CRD-driven promotion pipelines that move pinned versions through stages declaratively.</p>
<p><strong>2026 reference workflow snippet (push model):</strong></p>
<pre><code>- name: Update GitOps repo
  run: |
    git clone https://x:${{ secrets.GITOPS_TOKEN }}@github.com/acme/gitops.git
    cd gitops/envs/staging
    yq -i '.image.tag = "${{ github.sha }}"' values.yaml
    git -c user.email=ci@acme.io commit -am "deploy api ${{ github.sha }}"
    git push
</code></pre>
<p><strong>Pitfalls:</strong> shared GitOps repo with no PR gates &mdash; lose change review. Image Updater rules that match too broadly (<code>regex: .*</code>) auto-deploy any tag, including stale ones. Argo CD <code>cluster-admin</code> on every target cluster &mdash; scope per <code>AppProject</code>.</p>
'''


ANSWERS[59] = r'''<p>Jenkins-to-Kubernetes deploys typically use <code>kubectl</code>, <code>helm</code>, or <code>kustomize</code> from a build agent that&rsquo;s authenticated to the target cluster. The tactical choice is <em>direct apply</em> versus <em>push-to-GitOps</em>; modern teams default to the latter.</p>
<table>
<thead><tr><th>Approach</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Direct kubectl apply</td><td>Agent has a kubeconfig (file credential) or in-cluster ServiceAccount; pipeline runs <code>kubectl apply -k overlays/prod</code></td></tr>
<tr><td>Helm install/upgrade</td><td><code>helm upgrade --install --atomic --timeout 5m</code>; rolls back on failure</td></tr>
<tr><td>Argo Rollouts CLI</td><td><code>kubectl argo rollouts set image rollout/api api=...</code> &rarr; rollout owns canary/blue-green progression</td></tr>
<tr><td>Push-to-GitOps</td><td>Pipeline commits image tag bump; Argo CD / Flux pulls and applies; CI never holds cluster credentials</td></tr>
</tbody>
</table>
<p><strong>Authentication patterns:</strong></p>
<ul>
<li><strong>K8s plugin agent in-cluster:</strong> agent pod runs with a ServiceAccount bound to a Role allowing apply in its namespace; <code>kubectl</code> auto-uses the projected token.</li>
<li><strong>External agent + cloud cluster:</strong> use cloud IAM &mdash; IRSA on EKS, Workload Identity on GKE, Workload Identity on AKS &mdash; mapped to a K8s RBAC binding.</li>
<li><strong>Kubeconfig in credentials store:</strong> simplest, but kubeconfig with admin certificate is a long-lived target; rotate often or replace with short-lived OIDC tokens.</li>
</ul>
<p><strong>Reference Declarative pipeline:</strong></p>
<pre><code>pipeline {
  agent {
    kubernetes {
      yaml &apos;&apos;&apos;
        spec:
          serviceAccountName: jenkins-deployer
          containers:
            - name: helm
              image: alpine/helm:3.15.0
              command: [cat]; tty: true
      &apos;&apos;&apos;
    }
  }
  stages {
    stage('Deploy') {
      steps {
        container('helm') {
          sh &apos;&apos;&apos;
            helm upgrade --install api ./chart \
              --namespace prod --create-namespace \
              --set image.tag=$GIT_COMMIT \
              --atomic --timeout 5m
            kubectl rollout status deploy/api -n prod
          &apos;&apos;&apos;
        }
      }
    }
  }
}
</code></pre>
<p><strong>2026 advice:</strong> use Jenkins for build/push only; let Argo CD / Flux deploy. The pipeline becomes simpler ("update tag in config repo, done"), the cluster has a single source of truth, and emergency hotfixes go through the same path as regular ones (PR + auto-merge). Keep direct <code>kubectl apply</code> from Jenkins only if your org doesn&rsquo;t yet run a GitOps controller.</p>
'''


ANSWERS[60] = r'''<p>Multi-cloud architectures from GitHub Actions distribute the same workload across AWS + GCP + Azure (or any subset) for resilience, cost arbitrage, or regulatory reasons. The CI/CD mechanism is <em>portable artefact + per-cloud auth + per-cloud deploy</em>, layered with cross-cloud orchestration.</p>
<table>
<thead><tr><th>Concern</th><th>Approach (2026)</th></tr></thead>
<tbody>
<tr><td>Image distribution</td><td>One central registry (GHCR, Docker Hub) pulled by all clouds; or per-cloud registry mirrors (ECR, Artifact Registry, ACR) populated from a single push</td></tr>
<tr><td>Auth per cloud</td><td>OIDC federation everywhere &mdash; <code>aws-actions/configure-aws-credentials</code>, <code>google-github-actions/auth</code>, <code>azure/login</code></td></tr>
<tr><td>Manifest portability</td><td>Vanilla Kubernetes manifests where possible; cloud-specific bits behind <strong>Crossplane</strong> compositions or <strong>External Secrets Operator</strong> abstractions</td></tr>
<tr><td>Cluster fleet</td><td>Argo CD ApplicationSets with <em>cluster generator</em>; one Application per cluster auto-created</td></tr>
<tr><td>Global routing</td><td>Cloudflare, Fastly, Route 53 latency / geolocation policies; or a service mesh federation (Cilium ClusterMesh, Istio Multi-Cluster)</td></tr>
<tr><td>Data layer</td><td>Cloud-native global DBs (Aurora Global, Spanner, Cosmos DB) or open-source (CockroachDB, YugabyteDB) self-managed</td></tr>
</tbody>
</table>
<p><strong>Pipeline pattern:</strong> matrix job over clouds runs in parallel after a single build:</p>
<pre><code>strategy:
  matrix:
    target:
      - { cloud: aws,   region: us-east-1, cluster: eks-use1 }
      - { cloud: gcp,   region: us-central1, cluster: gke-usc1 }
      - { cloud: azure, region: eastus,   cluster: aks-eus }
</code></pre>
<p>Each matrix leg authenticates to its cloud (OIDC), loads kubeconfig, and applies. Or &mdash; preferred &mdash; commits to a GitOps repo with overlays per cluster; Argo CD on each cluster pulls.</p>
<p><strong>Active-active vs active-passive:</strong> active-active needs cross-cloud data replication and global routing; cost is high. Active-passive (DR-shaped) keeps secondary cluster scaled to zero, restored on failover via Velero backups. Most "multi-cloud" deploys are active-passive in practice.</p>
<p><strong>2026 tooling:</strong></p>
<ul>
<li><strong>Crossplane</strong> &mdash; one K8s control plane provisions across clouds; CI just does <code>kubectl apply</code>.</li>
<li><strong>Pulumi / Terraform / OpenTofu</strong> &mdash; multi-cloud providers in one stack.</li>
<li><strong>Akuity / Codefresh GitOps Cloud</strong> &mdash; managed Argo across cluster fleet.</li>
<li><strong>OpenTofu workspaces</strong> &mdash; one stack per cloud, common modules.</li>
</ul>
<p><strong>Honest pitfall:</strong> "true" multi-cloud doubles infra ops burden and cuts cloud-native feature use to the lowest common denominator. Prefer multi-region within one cloud for HA; use multi-cloud only for data-residency / vendor-leverage requirements.</p>
'''


ANSWERS[61] = r'''<p>Linkerd is a CNCF service mesh emphasising simplicity and performance. Architecture: a Rust micro-proxy sidecar (<em>linkerd2-proxy</em>) injected into every pod, plus a control plane (destination, identity, proxy-injector). The mesh provides mTLS, traffic policy, and observability with minimal config and low overhead.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>linkerd2-proxy</td><td>Per-pod sidecar (Rust); ~10 MB resident, ~1 ms latency overhead</td></tr>
<tr><td>destination controller</td><td>Service discovery + endpoint resolution</td></tr>
<tr><td>identity controller</td><td>Issues short-lived TLS certs to proxies (mTLS by default)</td></tr>
<tr><td>proxy-injector</td><td>MutatingWebhook that adds the sidecar on pod creation</td></tr>
<tr><td>Linkerd Viz / Buoyant Cloud</td><td>Dashboards + golden metrics</td></tr>
</tbody>
</table>
<p><strong>Capabilities out of the box:</strong></p>
<ul>
<li><strong>mTLS by default</strong> &mdash; every meshed pod-to-pod call is authenticated and encrypted; identity from K8s SA.</li>
<li><strong>Golden metrics</strong> &mdash; success rate, RPS, latency p50/p95/p99 for every service, no app code change.</li>
<li><strong>Traffic policy</strong> &mdash; <code>HTTPRoute</code> + <code>AuthorizationPolicy</code> CRs (Gateway API); allow/deny by SA / namespace / route.</li>
<li><strong>Retries + timeouts + circuit breaking</strong> &mdash; declarative <code>ServiceProfile</code> CRs.</li>
<li><strong>Multi-cluster</strong> &mdash; <code>linkerd multicluster</code> federates services across clusters with mTLS.</li>
</ul>
<p><strong>Progressive delivery:</strong> Linkerd integrates with <strong>Flagger</strong> for automated canary releases &mdash; Flagger reads Linkerd&rsquo;s Prometheus metrics, shifts traffic via SMI/Gateway API, and aborts on regression. Common alternative to Argo Rollouts in Linkerd shops.</p>
<p><strong>Linkerd vs Istio (2026):</strong></p>
<ul>
<li><strong>Linkerd</strong> &mdash; simpler, Rust proxy, lower overhead, fewer features. Strong in mid-size orgs.</li>
<li><strong>Istio Ambient Mesh</strong> &mdash; Istio&rsquo;s sidecar-less architecture (ztunnel DaemonSet + waypoint proxies); narrows the simplicity gap.</li>
<li><strong>Cilium Service Mesh</strong> &mdash; eBPF-based, no sidecars; integrated with Cilium CNI.</li>
</ul>
<p><strong>Install:</strong> <code>linkerd install --crds | kubectl apply -f -</code> &amp; <code>linkerd install | kubectl apply -f -</code>; or Helm chart for production. Annotate namespaces with <code>linkerd.io/inject: enabled</code> for auto-mesh.</p>
<p><strong>Pitfall:</strong> service-mesh sidecar injection breaks Init-style migrations &mdash; the migration container exits but the proxy keeps running, blocking pod completion. Use <code>config.linkerd.io/proxy-await: enabled</code> + native sidecar (K8s 1.29+) which terminates with the pod.</p>
'''


ANSWERS[62] = r'''<p>Automated canary releases progressively shift traffic to the new version, observe SLO-relevant metrics, and either promote or roll back &mdash; without humans clicking. The mechanism: <em>traffic-shifting controller</em> + <em>analysis runs</em> + <em>auto-promotion or auto-abort</em>.</p>
<table>
<thead><tr><th>Tool</th><th>How it shifts traffic</th><th>How it analyses</th></tr></thead>
<tbody>
<tr><td>Argo Rollouts</td><td><code>Rollout</code> CR with weighted ReplicaSets, integrates with Service / Ingress / SMI / Gateway API / mesh</td><td><code>AnalysisTemplate</code> queries Prometheus / Datadog / NewRelic / Web; pass/fail thresholds</td></tr>
<tr><td>Flagger</td><td>Owns Service definitions; works with Linkerd, Istio, App Mesh, Contour, Skipper, Traefik, NGINX, Gloo, Open Service Mesh, Gateway API</td><td>Built-in Prometheus queries; webhooks for custom checks</td></tr>
<tr><td>Service mesh native (Istio VirtualService weight)</td><td>Manual or scripted weight updates; no auto-analysis without Flagger</td><td>External (Kiali, Datadog, custom)</td></tr>
</tbody>
</table>
<p><strong>Argo Rollouts canary spec:</strong></p>
<pre><code>apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 5m }
        - analysis:
            templates: [ { templateName: success-rate } ]
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
      trafficRouting:
        istio:
          virtualService: { name: api }
</code></pre>
<p><strong>AnalysisTemplate:</strong> queries Prometheus for <code>sum(rate(http_requests_total{status!~"5.."}[2m])) / sum(rate(http_requests_total[2m]))</code> &gt; 0.99; failure aborts the rollout, traffic snaps back to stable. Define both technical (5xx, p99 latency) and product (conversion, signups) metrics.</p>
<p><strong>2026 best practice:</strong></p>
<ul>
<li><strong>SLO-aligned analysis</strong> &mdash; thresholds derived from your error budget burn rate, not arbitrary 1%.</li>
<li><strong>Multiple analysis windows</strong> &mdash; short for catastrophic failures, long for slow regressions.</li>
<li><strong>Combine with feature flags</strong> &mdash; canary releases the binary; flags release the feature. Decouples deploy and exposure.</li>
<li><strong>Background analysis</strong> &mdash; <code>analysisRunMetadata</code> for Datadog/NR-driven verifications without blocking promotion.</li>
</ul>
<p><strong>Pitfalls:</strong> small canary weights with low traffic (5% of 100 RPS = 5 RPS) generate too few samples for statistical confidence; either send more traffic to the canary or extend the analysis window. Stateful workloads can&rsquo;t easily canary &mdash; canary the API in front, not the database.</p>
'''


ANSWERS[63] = r'''<p>Lambda deploys from GitHub Actions package and ship code/container/zip artefacts and update function configuration via the AWS API. Modern stacks use AWS SAM, AWS CDK, or Serverless Framework as the higher-level IaC; underneath it&rsquo;s all <code>UpdateFunctionCode</code> + <code>UpdateFunctionConfiguration</code>.</p>
<table>
<thead><tr><th>Tool</th><th>Strength</th></tr></thead>
<tbody>
<tr><td>AWS SAM</td><td>Native CloudFormation; <code>sam build</code> + <code>sam deploy</code>; great for stack-based Lambdas</td></tr>
<tr><td>AWS CDK</td><td>Typed programming languages (TS, Py, Go, Java, .NET); compose with arbitrary AWS resources</td></tr>
<tr><td>Serverless Framework</td><td>YAML config; multi-cloud; mature plugin ecosystem (now commercial)</td></tr>
<tr><td>Terraform / OpenTofu</td><td>If Lambda is one slice of a larger IaC estate; less function-specialised</td></tr>
<tr><td>Pulumi</td><td>Typed languages + multi-cloud; good for polyglot orgs</td></tr>
<tr><td>cargo-lambda / aws-sam-cli + container</td><td>Rust / Go AOT-compiled binaries; smallest cold start</td></tr>
</tbody>
</table>
<p><strong>OIDC auth (2026 default):</strong> no static IAM keys. Workflow assumes a deploy role via <code>aws-actions/configure-aws-credentials</code>:</p>
<pre><code>permissions: { id-token: write, contents: read }
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123:role/gh-actions-lambda-deploy
    aws-region: us-east-1
- run: sam build
- run: sam deploy --stack-name api --no-confirm-changeset --no-fail-on-empty-changeset
</code></pre>
<p><strong>Progressive deploy:</strong></p>
<ul>
<li><strong>Versions + aliases</strong> &mdash; publish version, point alias <code>live</code>; <code>UpdateAlias</code> with <code>RoutingConfig.AdditionalVersionWeights</code> shifts a percentage to the new version.</li>
<li><strong>CodeDeploy hooks</strong> &mdash; <code>LambdaCanary10Percent5Minutes</code> auto-shifts; auto-rollback on CloudWatch alarm. Defined in SAM as <code>DeploymentPreference</code>.</li>
<li><strong>Multi-environment</strong> &mdash; one stack per env (<code>api-dev</code>, <code>api-prod</code>); same artefact, different parameters.</li>
</ul>
<p><strong>2026 specific:</strong></p>
<ul>
<li><strong>Container Image runtime</strong> &mdash; up to 10 GB image; preferred for ML inference, large native deps.</li>
<li><strong>Provisioned concurrency + SnapStart</strong> &mdash; cold-start mitigation; SnapStart is now broadly available across runtimes.</li>
<li><strong>Lambda Runtime API + custom runtimes</strong> on <code>provided.al2023</code> &mdash; Rust (cargo-lambda), Swift, etc.</li>
<li><strong>Function URLs + IAM auth</strong> &mdash; skip API Gateway for simple HTTP handlers.</li>
<li><strong>Lambda Powertools</strong> (Python/TS/Java/.NET) &mdash; structured logging, tracing, metrics out of the box.</li>
</ul>
<p><strong>Pitfalls:</strong> <code>npm install</code> in CI runner builds against runner&rsquo;s arch; for ARM Lambda, build in a matching environment (Lambda <code>arm64</code> + GH Actions <code>arm64</code> runner, or Docker buildx). Function permissions accumulate &mdash; periodically prune via Access Analyzer.</p>
'''


ANSWERS[64] = r'''<p>Complex dependency graphs in Jenkins span artefacts (microservices, libraries) and execution order (which builds wait on which). Two mechanisms cover them: <em>upstream/downstream triggers</em> at the job level and <em>parallel/matrix</em> within a single pipeline.</p>
<table>
<thead><tr><th>Mechanism</th><th>Used for</th></tr></thead>
<tbody>
<tr><td><code>build job: 'foo', wait: true</code></td><td>Trigger another job and block until done</td></tr>
<tr><td><code>build job: 'bar', wait: false</code></td><td>Fan out without blocking (fire-and-forget)</td></tr>
<tr><td><code>parallel</code> step</td><td>Concurrent stages within one pipeline; failed branch aborts siblings unless <code>failFast: false</code></td></tr>
<tr><td><code>matrix</code> step</td><td>Cartesian product over axes (OS, JDK); each cell runs same stages</td></tr>
<tr><td><code>copyArtifacts</code></td><td>Pull an artefact from a previous build of another job</td></tr>
<tr><td>Lockable Resources plugin</td><td>Mutex on shared resources (a fixture cluster, an API key with quota)</td></tr>
<tr><td>Build Pipeline / Pipeline Multibranch</td><td>Visualise upstream/downstream relationships</td></tr>
</tbody>
</table>
<p><strong>Common shapes:</strong></p>
<ul>
<li><strong>Library &rarr; multiple consumers</strong> &mdash; <code>shared-utils</code> publishes a SNAPSHOT version, downstream services rebuild on the new version. <em>Mechanism</em>: <code>shared-utils</code> publishes Maven artifact, then <code>build job: 'service-a', wait: false</code> for each downstream.</li>
<li><strong>Microservices integration test</strong> &mdash; build all services in parallel, wait, then run a single integration job that pulls all artefacts.</li>
<li><strong>Fan-out/fan-in</strong> &mdash; matrix builds N variants in parallel, then aggregate stage post-processes.</li>
<li><strong>Conditional graph</strong> &mdash; <code>when</code> blocks gate stages by branch / changed files / parameters.</li>
</ul>
<p><strong>Reference complex pipeline:</strong></p>
<pre><code>parallel(
  'service-a': { build job: 'service-a', wait: true, parameters: [string(name: 'COMMIT', value: env.GIT_COMMIT)] },
  'service-b': { build job: 'service-b', wait: true, parameters: [string(name: 'COMMIT', value: env.GIT_COMMIT)] },
  failFast: true
)
build job: 'integration-tests', wait: true
parallel(
  'deploy-staging-eu': { build job: 'deploy', parameters: [...] },
  'deploy-staging-us': { build job: 'deploy', parameters: [...] }
)
</code></pre>
<p><strong>2026 advice:</strong> for graphs more than ~5 nodes, the Groovy quickly becomes brittle. Push graph orchestration into a higher-level tool: <strong>Argo Workflows</strong> (DAG-native CRDs), <strong>Tekton Pipelines</strong> (Task DAG), <strong>Dagster</strong> / <strong>Airflow</strong> for data graphs, or <strong>Nx / Bazel</strong> for build graphs. Jenkins becomes the trigger; the orchestrator owns the DAG.</p>
<p><strong>Pitfalls:</strong> implicit dependencies via shared filesystems &mdash; brittle when agents change. Pass artefacts explicitly via <code>copyArtifacts</code> or registries. Long parallel branches keeping executors busy &mdash; use queue-aware scheduling and per-team agent pools.</p>
'''


ANSWERS[65] = r'''<p>Istio is the most feature-rich service mesh in the CNCF graduated tier &mdash; mTLS, traffic management, observability, policy &mdash; running on Envoy as the data plane. Two architectures coexist in 2026: <strong>sidecar mode</strong> (classic) and <strong>Ambient Mesh</strong> (sidecar-less, lighter).</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>istiod</td><td>Control plane: pilot + citadel + galley merged; xDS to Envoy</td></tr>
<tr><td>Envoy sidecar (sidecar mode)</td><td>Per-pod proxy; ~50-100 MB resident</td></tr>
<tr><td>ztunnel (Ambient mode)</td><td>Per-node DaemonSet handling L4 + mTLS</td></tr>
<tr><td>waypoint proxy (Ambient mode)</td><td>Per-namespace L7 proxy when L7 features needed</td></tr>
<tr><td><code>VirtualService</code> / <code>DestinationRule</code></td><td>Traffic routing, weighted splits, retries, mirroring</td></tr>
<tr><td><code>AuthorizationPolicy</code> / <code>PeerAuthentication</code></td><td>L7 RBAC + mTLS modes</td></tr>
<tr><td>Gateway API support</td><td>Modern alternative to <code>Gateway</code> + <code>VirtualService</code> CRDs</td></tr>
</tbody>
</table>
<p><strong>Capabilities:</strong></p>
<ul>
<li><strong>mTLS everywhere</strong> &mdash; STRICT mode rejects plaintext; identity from SPIFFE / SVID via SA.</li>
<li><strong>Traffic management</strong> &mdash; weighted routing, header-based routing, fault injection (delay, abort), traffic mirroring.</li>
<li><strong>Resiliency</strong> &mdash; retries, timeouts, circuit breaking, outlier detection, bulkheads.</li>
<li><strong>Observability</strong> &mdash; Envoy metrics &rarr; Prometheus; OTLP traces &rarr; Tempo / Jaeger; access logs &rarr; Loki.</li>
<li><strong>Multi-cluster</strong> &mdash; primary-remote, primary-primary, external control plane modes for federation.</li>
</ul>
<p><strong>Ambient Mesh (2026):</strong> sidecars are heavy &mdash; memory, latency, lifecycle issues with init containers. Ambient splits responsibilities: <strong>ztunnel</strong> (DaemonSet, Rust) handles mTLS + L4 routing for every pod; <strong>waypoint proxies</strong> (per namespace, optional) provide L7 features only where needed. Result: 30-90% lower overhead, simpler upgrades, fewer compatibility issues.</p>
<p><strong>Istio vs alternatives:</strong></p>
<ul>
<li><strong>Linkerd</strong> &mdash; simpler, lighter; smaller feature surface.</li>
<li><strong>Cilium Service Mesh</strong> &mdash; eBPF; no sidecars at all; tightly coupled with Cilium CNI.</li>
<li><strong>Kuma</strong> &mdash; Kong-backed; multi-zone friendly.</li>
<li><strong>AWS App Mesh</strong> &mdash; AWS-managed; entering wind-down in favour of EKS-native options.</li>
</ul>
<p><strong>Install:</strong> <code>istioctl install --set profile=ambient</code> for Ambient mode; <code>--set profile=default</code> for sidecar. Annotate namespaces with <code>istio.io/dataplane-mode: ambient</code> (Ambient) or <code>istio-injection: enabled</code> (sidecar).</p>
<p><strong>Pitfall:</strong> turning on every Istio feature simultaneously &mdash; mTLS STRICT + AuthorizationPolicies + traffic shifting all at once breaks something on day one. Roll out incrementally: namespace by namespace, feature by feature.</p>
'''

ANSWERS[66] = r'''<p>Legacy app CI/CD on Docker + Kubernetes follows the <em>strangler</em> mindset: containerise as-is first, then incrementally modernise. Pure rewrites usually fail; this approach delivers the K8s benefits (scheduling, scaling, observability) without rewriting business logic.</p>
<table>
<thead><tr><th>Phase</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Containerise as-is</td><td>Wrap the existing binary/WAR/installer in a Dockerfile; preserve config-via-files; expose health endpoints if absent</td></tr>
<tr><td>Externalise state</td><td>Filesystem &rarr; PVC; local sessions &rarr; Redis; in-memory caches &rarr; managed cache</td></tr>
<tr><td>Externalise config</td><td>Hard-coded paths &rarr; env vars; properties files &rarr; ConfigMaps; secrets &rarr; Secrets / Vault</td></tr>
<tr><td>Add observability</td><td>JMX exporter / app-specific exporter &rarr; Prometheus; sidecar log shipper or stdout / stderr; OpenTelemetry auto-instrumentation</td></tr>
<tr><td>Decompose</td><td>Strangler pattern: route new endpoints to a new microservice via Ingress / mesh; legacy keeps serving the rest</td></tr>
<tr><td>Replace</td><td>Once shadow-traffic + tests confirm parity, decommission legacy</td></tr>
</tbody>
</table>
<p><strong>Common patches:</strong></p>
<ul>
<li><strong>Health endpoints</strong> &mdash; legacy with no <code>/health</code>: a sidecar exposes <code>/healthz</code> by checking <code>tcp://localhost:8080</code> or <code>ps</code>.</li>
<li><strong>Graceful shutdown</strong> &mdash; legacy ignoring SIGTERM: wrap in a small init that translates SIGTERM to whatever the app understands; or use <code>preStop</code> hook to call a shutdown URL.</li>
<li><strong>Stateful filesystem</strong> &mdash; legacy writing to local disk: <code>StatefulSet</code> + PVC, <code>ReadWriteOnce</code> volume; or refactor to S3 if possible.</li>
<li><strong>Long startup</strong> &mdash; legacy taking 5+ minutes: bigger <code>initialDelaySeconds</code> on liveness; CRaC / SnapStart / readiness gating.</li>
<li><strong>Hard dependencies</strong> &mdash; legacy requires X11, IPC, /dev access: privileged pod (last resort, security risk) or refactor.</li>
</ul>
<p><strong>CI/CD pipeline shape:</strong> standard build &rarr; image &rarr; registry &rarr; deploy. Skip ambitious test-driven refactors at first &mdash; aim for "the legacy runs in K8s and we can deploy it from a pipeline" before adding TDD. Incrementally introduce unit tests, contract tests, then integration tests.</p>
<p><strong>2026 enabling tools:</strong></p>
<ul>
<li><strong>OpenTelemetry auto-instrumentation</strong> &mdash; <code>opentelemetry-javaagent</code>, .NET auto-instrumentation, Python auto-instrumentation; observability without code changes.</li>
<li><strong>Backstage</strong> service catalog &mdash; visualise legacy + modernisation roadmap.</li>
<li><strong>Service mesh</strong> &mdash; mTLS and routing for the strangler pattern without app code.</li>
<li><strong>Kompose</strong> &mdash; converts <code>docker-compose</code> to K8s manifests for legacy compose-based apps.</li>
</ul>
<p><strong>Honest pitfall:</strong> legacy apps that <em>cannot</em> be containerised cleanly (Win32-only, hardware-locked, requires dedicated VM image) shouldn&rsquo;t be forced into K8s. Run them on VMs or bare metal; integrate the deploys via Ansible / Salt while everything else moves to K8s.</p>
'''


ANSWERS[67] = r'''<p>CI/CD pipeline speed and efficiency come from <em>doing less</em>, <em>doing in parallel</em>, and <em>not redoing what hasn&rsquo;t changed</em>. The mechanism is targeted at three bottlenecks: build, test, deploy.</p>
<table>
<thead><tr><th>Bottleneck</th><th>Lever</th></tr></thead>
<tbody>
<tr><td>Image build</td><td>BuildKit + remote cache (GHA / S3 / registry); multi-stage; pre-baked base images; native multi-arch via Depot/Build Cloud</td></tr>
<tr><td>Test runtime</td><td>Test sharding (matrix), parallel test runners, test impact analysis (skip unaffected), flake retry caps</td></tr>
<tr><td>Sequential stages</td><td>Use <code>parallel</code> / matrix; avoid implicit serialisation</td></tr>
<tr><td>Affected detection</td><td>Nx / Turbo / Bazel / pnpm <code>--filter</code> &mdash; rebuild/test only changed services</td></tr>
<tr><td>Slow deploys</td><td>Image streaming, smaller images, pre-warmed nodes, <code>maxSurge: 100%</code></td></tr>
<tr><td>Slow runners</td><td>Larger runners (8/16-core), self-hosted on Karpenter spot, persistent volume mounts for caches</td></tr>
<tr><td>Cold dependency installs</td><td>Lockfile + cache action (<code>actions/cache</code>) keyed on lockfile hash</td></tr>
</tbody>
</table>
<p><strong>Concrete tactics that consistently pay off:</strong></p>
<ul>
<li><strong>Cache-from = cache-to</strong> for Docker; <code>type=gha,mode=max</code> includes intermediate stages.</li>
<li><strong>actions/cache</strong> on <code>~/.npm</code>, <code>~/.cargo</code>, <code>~/.m2</code>, <code>__pycache__</code>; keyed on lockfile.</li>
<li><strong>Concurrency groups</strong>: <code>group: ${{ github.workflow }}-${{ github.ref }}</code> + <code>cancel-in-progress: true</code> kills superseded runs.</li>
<li><strong>Path filters</strong>: <code>on: push: paths: [&apos;services/api/**&apos;]</code> &mdash; don&rsquo;t run the API workflow when only the docs changed.</li>
<li><strong>Test parallelism</strong>: Jest <code>--shard=$i/$N</code>, pytest-split, Go <code>go test -p</code>.</li>
<li><strong>Pre-baked agent images</strong> with toolchain installed cuts per-build setup from minutes to seconds.</li>
<li><strong>Matrix exclusion</strong>: skip uncommon combinations on PRs, run them only on <code>main</code>.</li>
</ul>
<p><strong>Measurement first:</strong> instrument step durations (GitHub Actions exposes them in the API; Jenkins via build timestamps). Plot p50/p99 over the last 30 days. Optimise the longest step, not the cheapest. Tools: <strong>Trunk.io Analytics</strong>, <strong>Datadog CI Visibility</strong>, <strong>Buildkite Test Analytics</strong>.</p>
<p><strong>2026 specific:</strong></p>
<ul>
<li><strong>Depot remote builders</strong> &mdash; persistent BuildKit cache across runs and CIs.</li>
<li><strong>Nx Cloud / Turborepo Remote Cache</strong> &mdash; shared task cache for monorepos.</li>
<li><strong>Larger GitHub-hosted runners</strong> (16-core) &mdash; trade $/min for wall-clock time.</li>
<li><strong>WarpBuild / Blacksmith / RunsOn</strong> &mdash; cheaper, faster GH Actions-compatible runners on bare-metal.</li>
</ul>
<p><strong>Pitfalls:</strong> chasing minutes saved while ignoring queue time &mdash; if your fleet sits at 100% utilisation, build optimisation buys you nothing. Add capacity. Optimising for <code>main</code> while ignoring PR runs &mdash; PR feedback loop is what developers feel.</p>
'''


ANSWERS[68] = r'''<p>Blue Ocean is a redesigned UI for Jenkins focused on Pipeline visualisation: a per-stage view, parallel-stage rendering, log streaming per step, and pipeline-creation wizards for SCM repos. It does not change pipeline syntax; it&rsquo;s purely a UX layer.</p>
<table>
<thead><tr><th>Capability</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Stage visualisation</td><td>Each stage is a node; parallel branches rendered as concurrent paths; failures highlighted in red</td></tr>
<tr><td>Per-step logs</td><td>Click a step &mdash; just that step&rsquo;s output, not the whole console</td></tr>
<tr><td>Pipeline editor</td><td>Visual editor that produces a Declarative <code>Jenkinsfile</code> &mdash; can be useful for onboarding, less so for advanced</td></tr>
<tr><td>SCM-aware creation</td><td>Wizard to point at a GitHub / Bitbucket / GitLab repo and create a multibranch pipeline</td></tr>
<tr><td>Activity / branches / PR views</td><td>Filter by who triggered, branch state, PR-vs-branch context</td></tr>
</tbody>
</table>
<p><strong>Install:</strong> <code>blueocean</code> plugin (and dependencies); accessible at <code>/blue</code>. Most modern Jenkins distributions install it by default.</p>
<p><strong>Honest 2026 reality:</strong> Blue Ocean was Jenkins&rsquo;s answer to "Jenkins UI is from 2008" but development has slowed substantially &mdash; CloudBees focuses on commercial offerings (CloudBees CI / Jenkins X / CloudBees CD) and the OSS Blue Ocean rarely sees substantial features. The classic Jenkins UI (still the default) has caught up with stage-view plugins. Newer alternatives:</p>
<ul>
<li><strong>GitHub Actions UI</strong> &mdash; modern, integrated, no plugin needed.</li>
<li><strong>GitLab CI UI</strong> &mdash; pipeline graph + DAG view native.</li>
<li><strong>Buildkite</strong> &mdash; clean per-step UI, log search, annotations.</li>
<li><strong>Tekton Dashboard</strong> &mdash; for Tekton-based pipelines.</li>
<li><strong>Backstage</strong> + plugin &mdash; aggregates Jenkins/Actions/Argo views.</li>
</ul>
<p><strong>Strengths still worth using:</strong></p>
<ul>
<li>Per-step logs in noisy pipelines &mdash; classic console output buried errors mid-stream.</li>
<li>Visual representation of complex parallel/matrix structures &mdash; quickly spot which branch failed.</li>
<li>Lower cognitive load for non-CI engineers checking on a build.</li>
</ul>
<p><strong>Pitfall:</strong> Blue Ocean lags on showing <code>script {}</code> imperative blocks or dynamic <code>parallel</code> generated at runtime &mdash; complex DSL exposes Blue Ocean&rsquo;s rendering edge cases. For static Declarative pipelines it works well.</p>
<p><strong>Visual pipeline editor:</strong> tempting for onboarding, but the generated Groovy is awkward and rarely matches what an experienced engineer would write. Use it for first-pipeline scaffolding, then edit YAML/Groovy by hand.</p>
'''


ANSWERS[69] = r'''<p>Continuous testing in GitHub Actions runs <em>relevant tests on every change</em> at multiple granularities: unit on every push, integration on PR, contract on merge, E2E on staging deploy. The mechanism: parallelised workflows with appropriate gating.</p>
<table>
<thead><tr><th>Stage</th><th>Test type</th><th>Trigger</th></tr></thead>
<tbody>
<tr><td>Pre-commit hook</td><td>Lint, format, type-check, fast unit</td><td>Local; pre-push enforced via <code>lefthook</code> / <code>husky</code> / <code>pre-commit</code></td></tr>
<tr><td>PR open / push</td><td>Unit, integration (with services), security scan</td><td><code>on: pull_request</code></td></tr>
<tr><td>PR ready-for-merge</td><td>Contract tests (Pact), full E2E on ephemeral env</td><td><code>on: pull_request</code> + label <code>ready-for-review</code></td></tr>
<tr><td>Merge to main</td><td>Smoke + canary in staging; performance benchmarks</td><td><code>on: push: branches: [main]</code></td></tr>
<tr><td>Scheduled</td><td>Long-running soak, security audits, dependency scans</td><td><code>on: schedule</code></td></tr>
</tbody>
</table>
<p><strong>Test types and tools (2026):</strong></p>
<ul>
<li><strong>Unit</strong> &mdash; framework-native (Jest/Vitest, pytest, JUnit, Go testing); &lt; 30s ideally.</li>
<li><strong>Integration</strong> &mdash; <code>services</code> in workflow YAML (Postgres, Redis, MongoDB sidecars), or Testcontainers libraries for ephemeral containerised deps.</li>
<li><strong>Contract</strong> &mdash; Pact, Spring Cloud Contract, Schemathesis (OpenAPI fuzz).</li>
<li><strong>E2E</strong> &mdash; Playwright (preferred), Cypress; run against an ephemeral preview env.</li>
<li><strong>Performance</strong> &mdash; k6, Artillery, Gatling; thresholds gate the PR.</li>
<li><strong>Security</strong> &mdash; CodeQL, Semgrep, Trivy fs/image, gitleaks.</li>
<li><strong>Visual regression</strong> &mdash; Percy, Chromatic, Playwright snapshots.</li>
<li><strong>Mutation</strong> &mdash; Stryker, Pitest; quality of test suite, not the code.</li>
</ul>
<p><strong>Speed levers:</strong></p>
<ul>
<li><strong>Sharded matrix</strong> tests run 4-8&times; faster wall-clock.</li>
<li><strong>Test impact analysis</strong> (Datadog CI, BuildPulse, Knapsack Pro) &mdash; only run tests affected by the diff.</li>
<li><strong>Cache deps</strong> via <code>actions/cache</code> keyed on lockfile.</li>
<li><strong>Concurrency cancellation</strong> kills superseded runs.</li>
</ul>
<p><strong>Reporting &amp; quality:</strong> JUnit XML uploaded as artefact + parsed by <strong>dorny/test-reporter</strong> for PR annotations. Coverage to Codecov / Coveralls; <strong>flake rate</strong> tracked as a metric &mdash; tests with &gt; 1% flake should be quarantined or fixed, not just retried.</p>
<p><strong>2026 patterns:</strong></p>
<ul>
<li><strong>Ephemeral preview environments</strong> per PR &mdash; vCluster, Argo CD ApplicationSets, Vercel/Netlify previews; E2E runs against the actual deployed code.</li>
<li><strong>Shift-right testing</strong> &mdash; synthetic monitors run E2E continuously against staging/prod; failures reuse the same Playwright suites.</li>
<li><strong>AI-assisted test generation</strong> &mdash; Github Copilot / Cursor tests; review carefully &mdash; correlates with test, doesn&rsquo;t guarantee correctness.</li>
</ul>
'''


ANSWERS[70] = r'''<p>Kubernetes cluster upgrades in CI/CD treat the cluster itself as managed infrastructure: version-controlled, tested in lower environments, rolled out with the same care as application releases.</p>
<table>
<thead><tr><th>Concern</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Skew policy</td><td>Control plane &le; 1 minor version newer than kubelets; never skip minors. Cluster API enforces this for managed clusters</td></tr>
<tr><td>Order</td><td>Control plane first, then node pools, then DaemonSets that gate node behaviour</td></tr>
<tr><td>Node pool strategy</td><td>Surge upgrade: launch new-version nodes, cordon + drain old, terminate; PDBs prevent simultaneous evictions</td></tr>
<tr><td>Add-ons</td><td>Per K8s release notes, upgrade compatible versions of CNI, CSI, ingress, mesh, monitoring</td></tr>
<tr><td>Validation</td><td>Conformance tests, smoke deploys, Sonobuoy runs, chaos drills</td></tr>
</tbody>
</table>
<p><strong>Managed K8s upgrade flow (2026):</strong></p>
<ul>
<li><strong>EKS</strong> &mdash; <code>eksctl upgrade cluster</code> for control plane; <code>eksctl upgrade nodegroup</code> or Karpenter consolidation for nodes. Add-ons (VPC CNI, CoreDNS, kube-proxy) via <code>eksctl update addon</code>.</li>
<li><strong>GKE</strong> &mdash; release channels (Rapid / Regular / Stable); auto-upgrade with maintenance windows. <strong>Surge upgrade</strong> + <strong>maxUnavailable</strong> tunable per node pool.</li>
<li><strong>AKS</strong> &mdash; <code>az aks upgrade</code>; node images via <code>az aks nodepool upgrade --node-image-only</code>; auto-upgrade channels.</li>
<li><strong>Cluster API (CAPI)</strong> &mdash; for self-managed: declarative <code>KubeadmControlPlane</code> + <code>MachineDeployment</code>; PR a version bump, controllers reconcile.</li>
</ul>
<p><strong>Pre-upgrade checklist:</strong></p>
<ul>
<li>Run <code>kubectl deprecations</code> / <code>pluto</code> / <code>kubent</code> &mdash; surfaces removed/deprecated APIs in your manifests.</li>
<li>Read the K8s release notes for the target version &mdash; flag breaking changes (Pod Security Admission default, deprecated <code>v1beta1</code> APIs gone).</li>
<li>Stage upgrade in dev &rarr; QA &rarr; staging &rarr; prod; bake at each stage.</li>
<li>Verify add-on compatibility matrix.</li>
<li>Confirm PDBs allow disruption (otherwise drain stalls).</li>
</ul>
<p><strong>2026 tooling:</strong></p>
<ul>
<li><strong>kubent / pluto / kube-no-trouble</strong> &mdash; deprecated API scanners.</li>
<li><strong>k0sctl / kops / Talos / kubeadm</strong> &mdash; self-managed; declarative version specs.</li>
<li><strong>Argo CD self-heal</strong> &mdash; reconciles add-on manifests after upgrade.</li>
<li><strong>Chaos drills</strong> (Litmus, Chaos Mesh) &mdash; verify resilience before and after upgrade.</li>
</ul>
<p><strong>Pitfalls:</strong> upgrading prod first ("the others are too small") &mdash; never. Ignoring node-image patches between minor versions &mdash; node OSes need monthly security patches independent of K8s minor. PDBs that block all eviction (<code>maxUnavailable: 0</code>) &mdash; turns drain into infinite wait. Missing readiness probes &mdash; new pods receive traffic before warm-up, exposing users to elevated errors during the upgrade.</p>
'''


ANSWERS[71] = r'''<p>Distributed tracing follows a request across services, attaching a trace context (trace ID, span IDs) so the path is reconstructable in a backend like Tempo / Jaeger / Honeycomb / Datadog APM. The standard in 2026 is <strong>OpenTelemetry</strong>: language SDKs + Collector + W3C trace-context headers.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>OTel SDK in app</td><td>Emits spans (manual via API) or auto-instruments common libraries (HTTP server, DB driver, message broker)</td></tr>
<tr><td>OTel Collector</td><td>DaemonSet (agent) + Deployment (gateway); receives OTLP, batches, processes (sampling, filtering, redaction), exports</td></tr>
<tr><td>W3C trace-context</td><td><code>traceparent</code> + <code>tracestate</code> headers propagate across service boundaries</td></tr>
<tr><td>Backend</td><td>Tempo / Jaeger / Honeycomb / Datadog / NewRelic / Grafana Cloud Traces</td></tr>
<tr><td>Sampling</td><td>Head-based (decide at ingress) or tail-based (decide after seeing the trace) &mdash; tail keeps interesting traces (errors, slow); head keeps cost predictable</td></tr>
</tbody>
</table>
<p><strong>Mechanism:</strong> when service A receives a request, the SDK extracts the trace context from incoming headers (or starts a new trace if absent) and creates a server span. Outbound calls (HTTP, gRPC, DB, queue) get instrumented &mdash; the SDK injects context headers and creates client spans. Spans flow to the Collector via OTLP, which exports to backends.</p>
<p><strong>K8s-specific concerns:</strong></p>
<ul>
<li><strong>Service mesh integration</strong> &mdash; Istio / Linkerd auto-emit spans for every meshed call; pair with app-level spans for full coverage.</li>
<li><strong>Resource attributes</strong> &mdash; <code>service.name</code>, <code>k8s.pod.name</code>, <code>k8s.namespace.name</code> via <code>otel-operator</code> auto-injection or downward API.</li>
<li><strong>Cross-cluster traces</strong> &mdash; trace context flows naturally across cluster boundaries via HTTP/gRPC headers.</li>
<li><strong>eBPF-based agents</strong> (Pixie, Parca, Coroot) &mdash; auto-collect traces without code changes, useful for legacy or polyglot estates.</li>
</ul>
<p><strong>Sampling strategy (2026):</strong></p>
<ul>
<li><strong>Head sampling</strong> at the SDK: cheap, predictable cost, blind to importance.</li>
<li><strong>Tail sampling</strong> in the Collector: keep all error traces, slow traces, sample of the rest. Costs Collector memory but catches what matters.</li>
<li><strong>Always-sample for critical paths</strong> (checkout, payments) and aggressively sample others.</li>
</ul>
<p><strong>Practical setup:</strong> deploy the <strong>OpenTelemetry Operator</strong>, define a <code>Collector</code> CR per namespace (or DaemonSet for receiving), enable <code>sidecar</code> or <code>auto-instrumentation</code> annotations on Deployments. Back-end choice depends on org &mdash; Grafana Tempo (cheap, S3-backed) for self-hosted; Honeycomb / Datadog for high-cardinality query power.</p>
<p><strong>Pitfall:</strong> instrumenting only <em>some</em> services &mdash; broken traces look worse than no traces. Either instrument all or none of a critical path.</p>
'''


ANSWERS[72] = r'''<p>Shared Libraries are reusable Groovy code Jenkins pipelines load at runtime, eliminating copy-paste. The repository structure is fixed (<code>vars/</code>, <code>src/</code>, <code>resources/</code>) and gives both function-level reuse (<code>vars/</code>) and class-level reuse (<code>src/</code>).</p>
<table>
<thead><tr><th>Path</th><th>Use</th></tr></thead>
<tbody>
<tr><td><code>vars/buildAndPush.groovy</code></td><td>Global step: pipelines call <code>buildAndPush(image: 'foo', tag: 'v1')</code></td></tr>
<tr><td><code>vars/<em>foo</em>.txt</code></td><td>Help text shown in Pipeline Syntax</td></tr>
<tr><td><code>src/com/acme/Notifier.groovy</code></td><td>Java/Groovy package classes; stateful logic (Slack, Jira, Vault clients)</td></tr>
<tr><td><code>resources/Dockerfile.tpl</code></td><td>Non-Groovy assets loaded with <code>libraryResource()</code></td></tr>
<tr><td><code>test/</code></td><td>Tests with <strong>JenkinsPipelineUnit</strong> &mdash; unit-test pipelines without spinning up Jenkins</td></tr>
</tbody>
</table>
<p><strong>Loading:</strong></p>
<ul>
<li><strong>Global</strong> in <em>Manage Jenkins &rarr; Configure System &rarr; Global Pipeline Libraries</em>: trusted, no script approval; available to all jobs.</li>
<li><strong>Folder</strong>: per-folder library; trusted within that folder.</li>
<li><strong>Per-pipeline</strong>: <code>@Library('acme-shared@v3.2') _</code>; sandboxed unless library is configured trusted.</li>
<li><strong>Pin to tags</strong> (<code>@v3.2</code>) for reproducibility; <code>@main</code> creates a moving target that breaks builds the day a refactor lands.</li>
</ul>
<p><strong>Reference snippet:</strong></p>
<pre><code>// vars/buildAndPush.groovy
def call(Map cfg) {
  def image = cfg.image ?: error('image required')
  def tag   = cfg.tag   ?: env.GIT_COMMIT
  sh "docker build -t ${image}:${tag} ${cfg.context ?: '.'}"
  withCredentials([usernamePassword(credentialsId: 'docker-hub', usernameVariable: 'U', passwordVariable: 'P')]) {
    sh 'echo $P | docker login -u $U --password-stdin'
  }
  sh "docker push ${image}:${tag}"
}
</code></pre>
<p>Pipelines then call <code>buildAndPush image: 'acme/api', tag: env.BUILD_TAG</code>.</p>
<p><strong>Versioning &amp; testing:</strong></p>
<ul>
<li>Tag releases (<code>v1.0.0</code>); Jenkinsfiles pin via <code>@v1.0.0</code>.</li>
<li>Run <strong>JenkinsPipelineUnit</strong> in CI for the library itself: stub steps, assert behaviour without a Jenkins server.</li>
<li>Integration test by running a sample pipeline against the library on every PR.</li>
</ul>
<p><strong>2026 advice:</strong></p>
<ul>
<li>Keep libraries narrow; one library per concern (notifications, security, deploy) is easier than a god library.</li>
<li>Trust model: globally configured libraries skip script approval &mdash; <em>treat their authors as platform team</em>. App teams should propose changes via PR, not commit directly.</li>
<li>Greenfield teams more often skip Jenkins entirely &mdash; <strong>GitHub Actions reusable workflows + composite actions</strong> cover the same reuse story without Groovy. Migrate when business case allows.</li>
</ul>
<p><strong>Pitfall:</strong> stashing logic in <code>vars/</code> when it really belongs in <code>src/</code> classes &mdash; testability suffers, and Groovy semantic gotchas (binding scoping) bite.</p>
'''


ANSWERS[73] = r'''<p>Real-time apps using WebSockets on Kubernetes need long-lived connection support, sticky sessions, and graceful drain during deploys. The mechanism: TCP-aware load balancing + connection draining + horizontal scaling on appropriate metrics.</p>
<table>
<thead><tr><th>Concern</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Connection persistence</td><td>L4 LB (NLB / Network Load Balancer) or L7 Ingress with WebSocket support (NGINX, Traefik, HAProxy, Envoy)</td></tr>
<tr><td>Session stickiness</td><td>Cookie-based or source-IP affinity; or stateless via Redis Pub/Sub for fan-out</td></tr>
<tr><td>Long-lived connection drain</td><td><code>preStop: sleep N</code> + <code>terminationGracePeriodSeconds &gt; max-connection-lifetime</code>; app handles SIGTERM by sending close frames</td></tr>
<tr><td>Scaling signal</td><td>HPA on active connections (custom metric) or RPS, not CPU; KEDA for queue-driven workloads</td></tr>
<tr><td>State scale-out</td><td>Redis Pub/Sub, NATS JetStream, Kafka for cross-pod fan-out</td></tr>
<tr><td>Cross-pod broadcast</td><td>App joins channel on Redis; messages published once, all subscribers receive</td></tr>
</tbody>
</table>
<p><strong>Deploy concerns:</strong></p>
<ul>
<li><strong>Rolling update</strong> drops active connections on the old pod &mdash; clients should auto-reconnect (most WS libraries do); the cluster experiences a connection storm during deploy. Tune <code>maxSurge: 25%</code> (not 100%) so reconnects don&rsquo;t overwhelm new pods.</li>
<li><strong>preStop drain</strong>: app receives SIGTERM, stops accepting new connections, sends close frames to active clients with reason "redeploying", waits up to <code>terminationGracePeriodSeconds</code>, then exits. Clients reconnect within seconds.</li>
<li><strong>Connection rebalance</strong>: post-deploy, new pods get few connections (clients stay on existing pods). Optional: rolling drain (close 10% of connections per minute) to redistribute. Or accept eventual rebalance via natural client disconnect.</li>
</ul>
<p><strong>Architecture patterns:</strong></p>
<ul>
<li><strong>Stateful WS, stateless app:</strong> WS server holds per-connection state (subscriptions); shared state in Redis. Pods are interchangeable for new connections.</li>
<li><strong>Edge gateway:</strong> a dedicated WS gateway (e.g. <strong>Centrifugo</strong>, <strong>Phoenix Channels</strong>, <strong>Soketi</strong>, <strong>API Gateway WebSocket</strong>) terminates connections, app servers stay HTTP-only.</li>
<li><strong>Sidecar pattern:</strong> Envoy / Linkerd sidecar handles connection lifecycle; app focuses on logic.</li>
<li><strong>Server-Sent Events (SSE)</strong> &mdash; alternative to WS for server-push-only; simpler, plays nicer with HTTP infrastructure.</li>
</ul>
<p><strong>2026 stack:</strong></p>
<ul>
<li><strong>Cloudflare Durable Objects / Workers</strong>, <strong>AWS API Gateway WebSocket</strong>, <strong>Ably</strong>, <strong>Pusher</strong> &mdash; managed services that handle scale + drain.</li>
<li><strong>NATS JetStream</strong> for cross-pod messaging.</li>
<li><strong>HAProxy 3.0</strong> with native WebSocket support and connection-level routing.</li>
<li><strong>KEDA</strong> with the <code>http-add-on</code> scales pods on incoming connection rate.</li>
</ul>
<p><strong>Pitfall:</strong> using L7 Ingress with default 60s read timeout &mdash; idle WS connections close. Set <code>nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"</code>; for Envoy, configure the <code>idle_timeout</code> on the listener.</p>
'''


ANSWERS[74] = r'''<p>ML model deploys to Kubernetes from GitHub Actions are mostly identical to app deploys with two extra concerns: large artefact size (model weights) and inference-specific runtimes. The mechanism: <em>train artefact &rarr; sign / version &rarr; serve via inference framework &rarr; canary on quality metrics</em>.</p>
<table>
<thead><tr><th>Component</th><th>Role</th></tr></thead>
<tbody>
<tr><td>Model registry</td><td>MLflow, Weights &amp; Biases, Hugging Face Hub, S3 + DVC; versioned with checksums</td></tr>
<tr><td>Inference server</td><td><strong>KServe</strong>, <strong>Seldon Core</strong>, <strong>BentoML</strong>, <strong>NVIDIA Triton</strong>, <strong>Ray Serve</strong>, <strong>vLLM</strong> for LLMs</td></tr>
<tr><td>Hardware</td><td>GPU node pool (NVIDIA A10/A100/H100/L4) with <code>nvidia-device-plugin</code>; or CPU for lightweight; Inferentia / TPU for cloud-specific</td></tr>
<tr><td>Autoscaling</td><td>KEDA on queue depth or RPS; for GPU, scale-to-zero matters (Karpenter spot GPU)</td></tr>
<tr><td>Quality monitoring</td><td>Prediction monitoring, drift detection (Evidently, Fiddler, Arize, WhyLabs)</td></tr>
</tbody>
</table>
<p><strong>Pipeline shape:</strong></p>
<ol>
<li><strong>Train</strong> in CI/orchestrator (Kubeflow, Argo Workflows, Airflow, or just a training script on a beefy runner).</li>
<li><strong>Register</strong> the trained artefact in MLflow / W&amp;B with metadata (training data hash, hyperparameters, eval metrics).</li>
<li><strong>Bake</strong> a deployment-ready container or use a runtime that pulls from registry at boot (KServe StorageInitializer fetches from S3/GCS/MLflow).</li>
<li><strong>Validate</strong> on a held-out set; gate on accuracy / fairness thresholds.</li>
<li><strong>Deploy</strong> via Argo CD with Argo Rollouts canary; A/B traffic split with quality monitoring.</li>
<li><strong>Roll back</strong> automatically on quality drop (analysis run on prediction error rate or bias metrics).</li>
</ol>
<p><strong>2026 specific:</strong></p>
<ul>
<li><strong>vLLM</strong> + <strong>TGI</strong> &mdash; LLM-optimised inference servers with continuous batching and PagedAttention.</li>
<li><strong>KServe v0.13+</strong> &mdash; model autoscaling, canary, model explainability built in.</li>
<li><strong>Hugging Face TGI on K8s</strong> &mdash; container ships pre-tuned for inference.</li>
<li><strong>Karpenter GPU consolidation</strong> &mdash; shares GPUs across small models or scales to zero.</li>
<li><strong>Inference graphs</strong> (Seldon Core v2, KServe InferenceGraph) for ensembles or feature-extraction + model chains.</li>
<li><strong>OpenTelemetry for ML</strong> &mdash; traces show prompt &rarr; embedding &rarr; model &rarr; postprocess.</li>
</ul>
<p><strong>Pitfalls:</strong></p>
<ul>
<li>Baking 70 GB model into image &mdash; pulls take forever. Use <code>StorageInitializer</code> to fetch on pod start (cached on node) or PVC with model preloaded.</li>
<li>Single point of failure on the model registry &mdash; replicate or use cloud-managed.</li>
<li>Model drift unnoticed &mdash; observability for input/output distributions is non-negotiable.</li>
<li>Cost &mdash; GPU at $5+/hour, spot interruption, idle cost. Scale-to-zero, batching, and CPU fallback for low-RPS tiers all matter.</li>
</ul>
'''


ANSWERS[75] = r'''<p>Rancher provides a unified web UI + API for managing multiple Kubernetes clusters &mdash; a "K8s of K8s" control plane. It runs as a Kubernetes app itself (the Rancher Server cluster) and federates downstream clusters via an agent.</p>
<table>
<thead><tr><th>Capability</th><th>Detail</th></tr></thead>
<tbody>
<tr><td>Multi-cluster management</td><td>Register downstream clusters (RKE2, K3s, EKS, GKE, AKS, on-prem); single pane for kubectl, manifests, monitoring</td></tr>
<tr><td>Authentication</td><td>SSO (LDAP, SAML, OIDC, GitHub, Keycloak) federated to all clusters; RBAC mapped from external groups to per-cluster roles</td></tr>
<tr><td>Cluster provisioning</td><td>RKE2 / K3s installer (recommended) or import existing clusters; node templates for cloud providers</td></tr>
<tr><td>Catalog (apps)</td><td>Helm chart catalog &mdash; one-click installs of Prometheus, Longhorn, NeuVector, Istio, etc.</td></tr>
<tr><td>Monitoring</td><td>Prometheus + Grafana stack pre-packaged via Rancher Monitoring</td></tr>
<tr><td>Logging</td><td>Banzai Cloud Logging Operator (Fluent Bit + Fluentd) auto-configured</td></tr>
<tr><td>Fleet (GitOps)</td><td>Built-in GitOps engine; declarative cluster + workload state from Git</td></tr>
<tr><td>NeuVector</td><td>Container security; admission control, runtime scanning</td></tr>
<tr><td>Longhorn</td><td>Distributed block storage CSI</td></tr>
</tbody>
</table>
<p><strong>Strengths:</strong></p>
<ul>
<li><strong>UI-first</strong> &mdash; lower barrier for ops teams transitioning from VMs.</li>
<li><strong>Multi-cluster RBAC</strong> &mdash; consistent identity / authorisation across fleet.</li>
<li><strong>Edge / IoT</strong> &mdash; <strong>K3s</strong> + Rancher is a popular pattern for edge K8s; small footprint, central management.</li>
<li><strong>OSS</strong> &mdash; Rancher itself is OSS (SUSE-backed); no per-cluster license.</li>
</ul>
<p><strong>Honest 2026 reality:</strong> Rancher is strong in three niches:</p>
<ul>
<li>Edge / IoT fleets (K3s + Rancher).</li>
<li>Enterprises with mixed (cloud + on-prem) clusters wanting one UI.</li>
<li>Teams on RKE2 for self-managed K8s.</li>
</ul>
<p>For pure cloud K8s (EKS / GKE / AKS) shops, Rancher adds an extra layer that may not justify itself when each cloud provides its own console + IAM + CLI. <strong>Argo CD + Backstage + cluster-API operators</strong> covers similar ground via composition.</p>
<p><strong>vs alternatives:</strong></p>
<ul>
<li><strong>Akuity</strong>, <strong>Codefresh GitOps</strong>, <strong>Spectro Cloud Palette</strong> &mdash; managed GitOps + cluster fleet.</li>
<li><strong>Anthos / Azure Arc / EKS Anywhere</strong> &mdash; cloud-vendor multi-cluster managers.</li>
<li><strong>Cluster API (CAPI)</strong> &mdash; declarative cluster provisioning via CRDs; pairs with Argo CD.</li>
</ul>
<p><strong>Pitfalls:</strong> Rancher Server itself is a SPOF for fleet management &mdash; HA install (3+ nodes, embedded etcd or external DB) is mandatory in prod. Network paths between Rancher and downstream clusters &mdash; agents dial out via WebSocket; air-gapped installs need extra setup.</p>
'''


ANSWERS[76] = r'''<p>Jenkins server hardening covers identity, network, file system, plugin supply chain, and operational hygiene. The threat model: external attacker, malicious insider, supply-chain compromise.</p>
<table>
<thead><tr><th>Category</th><th>Hardening</th></tr></thead>
<tbody>
<tr><td>Identity</td><td>SSO via OIDC / SAML (Entra, Okta, Keycloak); MFA enforced at IdP; disable internal accounts</td></tr>
<tr><td>Authorization</td><td>Matrix or Role-Based Strategy plugin; <em>least privilege</em> per folder; no wildcard "anyone can build"</td></tr>
<tr><td>Network</td><td>Behind reverse proxy with TLS termination; restrict ingress to corporate VPN / SSO gateway; CSP / HSTS headers; agent-master isolation</td></tr>
<tr><td>File system</td><td>Run as non-root; <code>JENKINS_HOME</code> on encrypted volume; no shell access for the jenkins user beyond what&rsquo;s needed</td></tr>
<tr><td>Agent isolation</td><td>Agents in separate trust zone; no kubeconfig-with-cluster-admin on agents; ephemeral K8s agents preferred</td></tr>
<tr><td>Plugin hygiene</td><td>Pin versions; update monthly; review CVEs; minimise plugin count; only install from <code>jenkins.io/updates</code></td></tr>
<tr><td>Script approval</td><td>Limit Groovy execution to trusted libraries; sandbox untrusted</td></tr>
<tr><td>Secrets</td><td>External via Vault / cloud secret manager; never in <code>JENKINS_HOME</code> or <code>config.xml</code> in clear</td></tr>
<tr><td>Audit</td><td>Audit Trail plugin or external SIEM via webhook; all auth + config changes logged</td></tr>
<tr><td>Backup</td><td>Encrypted backups of <code>JENKINS_HOME</code>; periodic restore drill</td></tr>
<tr><td>JCasC</td><td>Configuration-as-Code in Git; no UI-only config; reduces drift surface</td></tr>
</tbody>
</table>
<p><strong>K8s-native hardening:</strong></p>
<ul>
<li>Run via the official <strong><code>jenkinsci/jenkins</code></strong> Helm chart with <code>controller.runAsUser: 1000</code>, <code>readOnlyRootFilesystem: true</code> (with writable <code>emptyDir</code> for caches), Pod Security Admission <code>restricted</code> profile (with documented exceptions).</li>
<li>NetworkPolicy: ingress only from ingress controller; egress to GitHub, registry, K8s API.</li>
<li>Agent pods spawn in a separate namespace with their own RBAC; can&rsquo;t see controller&rsquo;s namespace.</li>
<li>Use <strong>Trivy operator</strong> + <strong>Falco</strong> for continuous image / runtime scanning of the Jenkins controller.</li>
</ul>
<p><strong>Critical CVE classes to know:</strong></p>
<ul>
<li><strong>Script Console</strong> abuse &mdash; only <code>Overall/Administer</code> users; treat them as cluster-admin.</li>
<li><strong>Plugin RCE</strong> &mdash; subscribe to <code>jenkins-security-advisories</code>; auto-patch within SLA.</li>
<li><strong>Anonymous read</strong> &mdash; default-off, but check.</li>
<li><strong>SSH agent &amp; CLI port</strong> &mdash; disable if unused.</li>
</ul>
<p><strong>2026 advice:</strong> if you&rsquo;re hardening Jenkins from scratch in 2026, also evaluate replacement. For greenfield, GitHub Actions / GitLab CI / Buildkite / Tekton come with smaller attack surface (no plugin sprawl), managed (or simpler self-host), and SSO-native. Hardening Jenkins is well understood; the question is whether continued investment beats migration.</p>
'''


ANSWERS[77] = r'''<p>Admission Controllers intercept requests to the K8s API server <em>after</em> authentication and authorization but <em>before</em> object persistence. They enforce policy &mdash; reject, mutate, or audit objects. Two categories: <em>built-in</em> (compiled into apiserver, e.g. NamespaceLifecycle, LimitRanger) and <em>dynamic</em> (webhooks, the customisable kind).</p>
<table>
<thead><tr><th>Type</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>MutatingAdmissionWebhook</td><td>Modifies the object (inject sidecars, defaults, labels); runs before validating webhooks</td></tr>
<tr><td>ValidatingAdmissionWebhook</td><td>Reject or accept; cannot mutate</td></tr>
<tr><td>ValidatingAdmissionPolicy (CEL)</td><td>K8s 1.30+ native; CEL expressions, no webhook server &mdash; lower latency, fewer moving parts</td></tr>
<tr><td>MutatingAdmissionPolicy (CEL)</td><td>K8s 1.32 alpha &mdash; CEL-based mutation</td></tr>
</tbody>
</table>
<p><strong>Standard 2026 stack:</strong></p>
<ul>
<li><strong>Pod Security Admission</strong> (built-in) &mdash; namespace-level Pod Security Standards (<code>privileged</code>/<code>baseline</code>/<code>restricted</code>); replacement for the deprecated PSP.</li>
<li><strong>Kyverno</strong> &mdash; CRD-based policy (no Rego); validate, mutate, generate, cleanup. CNCF graduated; the dominant choice in 2026.</li>
<li><strong>OPA Gatekeeper</strong> &mdash; OPA/Rego policy via constraint templates; powerful but Rego learning curve.</li>
<li><strong>Sigstore policy-controller / Connaisseur / Ratify</strong> &mdash; image signature verification.</li>
<li><strong>cert-manager webhook</strong> &mdash; injects defaults into Certificate CRs.</li>
<li><strong>Linkerd / Istio injectors</strong> &mdash; sidecar injection.</li>
</ul>
<p><strong>Common policies:</strong></p>
<ul>
<li>Reject pods with <code>runAsRoot</code>, missing <code>readOnlyRootFilesystem</code>, missing resource limits.</li>
<li>Require <code>image: registry/...</code> from approved registries.</li>
<li>Verify cosign signatures + SLSA provenance before admission.</li>
<li>Stamp <code>cost-center</code> label on every Deployment from the namespace label.</li>
<li>Block deletion of resources tagged <code>protected</code> outside maintenance windows.</li>
<li>Auto-generate NetworkPolicy denying egress when a new namespace is created.</li>
</ul>
<p><strong>Performance:</strong> webhooks add latency to <em>every</em> matching API call. Critical operations (Pod create) on busy clusters multiply the cost. Mitigations:</p>
<ul>
<li><strong>Use ValidatingAdmissionPolicy (CEL)</strong> for simple rules &mdash; in-process, no network hop.</li>
<li>Keep webhooks <code>failurePolicy: Fail</code> only when necessary; <code>Ignore</code> for advisory; tag scope with <code>matchConditions</code>.</li>
<li>Run multiple webhook replicas with topology spread; set tight timeouts (5s default; lower if possible).</li>
<li>Avoid webhooks that hit external services synchronously.</li>
</ul>
<p><strong>Pitfalls:</strong> validating webhook with <code>failurePolicy: Fail</code> that depends on a Deployment in the same cluster &mdash; if the webhook pod crashes, all admissions fail, including its own restart. Self-bootstrap order matters. Always test with <code>kubectl apply --dry-run=server</code> against staging.</p>
'''


ANSWERS[78] = r'''<p>Multi-environment deploys promote the same artefact through <code>dev &rarr; qa &rarr; staging &rarr; prod</code>, with environment-specific config injected and quality gates between stages. The mechanism: <em>immutable artefact + per-env config overlay + gated promotion</em>.</p>
<table>
<thead><tr><th>Concern</th><th>Pattern</th></tr></thead>
<tbody>
<tr><td>Single artefact</td><td>Build once; image tag = git SHA; never rebuild between environments</td></tr>
<tr><td>Config overlay</td><td>Helm values file per env, or Kustomize overlay per env, or env-specific ConfigMaps generated by GitOps</td></tr>
<tr><td>Secret per env</td><td>Vault paths per env; External Secrets Operator pulls into the cluster; never bake into image</td></tr>
<tr><td>Gates</td><td>Auto-promote dev/qa; manual approval at staging&rarr;prod via PR + required reviewers, or CD platform manual gate</td></tr>
<tr><td>Drift detection</td><td>Argo CD compares actual vs Git; alerts on drift; <code>selfHeal</code> reverts</td></tr>
</tbody>
</table>
<p><strong>GitOps pattern (2026 default):</strong></p>
<ul>
<li>Application repo: source code, Dockerfile, base Helm chart.</li>
<li>Config repo (often per env or one repo with env subfolders): <code>envs/dev/values.yaml</code>, <code>envs/staging/values.yaml</code>, <code>envs/prod/values.yaml</code>.</li>
<li>CI builds image, opens PR in config repo bumping <code>envs/dev/values.yaml</code> tag &mdash; auto-merged.</li>
<li>Promotion to staging: PR copies the dev tag into <code>envs/staging/values.yaml</code>; required reviewers; once merged, Argo CD reconciles.</li>
<li>Promotion to prod: same shape; submitted by release manager during release window.</li>
<li>Tools that automate this: <strong>Kargo</strong>, <strong>Argo CD ApplicationSets</strong> with promotion-driven generators.</li>
</ul>
<p><strong>Cluster topology trade-offs:</strong></p>
<ul>
<li><strong>Single cluster, namespace per env</strong> &mdash; cheapest; bleed risk between envs (resource contention, RBAC mistakes).</li>
<li><strong>Cluster per env</strong> &mdash; isolation, easier blast-radius reasoning; Argo CD ApplicationSets generate one Application per cluster.</li>
<li><strong>Cluster per env per region</strong> &mdash; regulatory or HA-driven.</li>
<li><strong>vCluster</strong> &mdash; virtual control planes inside one host cluster; cheaper than full clusters, stronger than namespaces.</li>
</ul>
<p><strong>Test strategy per env:</strong> unit tests in CI (every push), integration on PR (against ephemeral env), E2E + load on staging, canary in prod with Argo Rollouts gating on SLOs.</p>
<p><strong>Promotion controls (2026):</strong></p>
<ul>
<li>Require <em>artifact provenance</em> &mdash; cosign verify + SLSA attestation before each promotion.</li>
<li>Require <em>same artefact</em> &mdash; CD platform refuses to promote a tag that hasn&rsquo;t passed staging.</li>
<li>Require <em>error-budget headroom</em> &mdash; SLO burn-rate gate blocks promotion if recent incidents drained budget.</li>
<li>Require <em>change windows</em> &mdash; deny prod merges between Friday 17:00 and Monday 09:00 unless emergency-tagged.</li>
</ul>
<p><strong>Pitfall:</strong> environment-specific source code branches (<code>main</code> &rarr; dev, <code>release</code> &rarr; staging, <code>prod</code> &rarr; prod). Drift, merge nightmares, lost commits. Trunk-based development with one immutable artefact promoted everywhere is the modern norm.</p>
'''


ANSWERS[79] = r'''<p>Mobile builds in GitHub Actions handle iOS and Android with platform-specific toolchains: macOS runners for iOS (Xcode), Linux/macOS runners for Android (Gradle + SDK). The mechanism: provision toolchain, build artefact (IPA / APK / AAB), sign, distribute.</p>
<table>
<thead><tr><th>Platform</th><th>Toolchain</th><th>Output</th></tr></thead>
<tbody>
<tr><td>iOS</td><td>macOS runner; Xcode (matched to project version); CocoaPods / SPM; <strong>fastlane</strong> for orchestration</td><td><code>.ipa</code> (App Store) or <code>.app</code> (TestFlight / Ad Hoc)</td></tr>
<tr><td>Android</td><td>Linux or macOS runner; Android SDK + NDK; Gradle; <strong>fastlane</strong> or <strong>gradle-play-publisher</strong></td><td><code>.aab</code> (Play Store) or <code>.apk</code> (sideload)</td></tr>
<tr><td>React Native / Flutter / Expo</td><td>Both above + JS/Dart toolchain; or <strong>EAS Build</strong> (Expo) / <strong>Codemagic</strong> / <strong>Bitrise</strong> hosted alternatives</td><td>Both</td></tr>
</tbody>
</table>
<p><strong>iOS signing &amp; distribution:</strong></p>
<ul>
<li><strong>App Store Connect API key</strong> stored as a GitHub secret; <code>fastlane</code> or <code>app-store-connect-cli</code> reads it.</li>
<li><strong>Match</strong> (fastlane) stores signing certs + provisioning profiles in a private Git repo, encrypted; runner clones + installs at build time.</li>
<li><strong>App Store / TestFlight upload</strong> via <code>fastlane pilot upload</code> or <code>xcrun altool</code> / <code>xcrun notarytool</code>.</li>
<li><strong>Internal distribution</strong>: Firebase App Distribution, App Center, TestFlight internal.</li>
</ul>
<p><strong>Android signing &amp; distribution:</strong></p>
<ul>
<li>Upload key + Google-managed signing key (Play App Signing).</li>
<li>Build <code>.aab</code> with <code>./gradlew bundleRelease</code>; sign with upload key.</li>
<li>Upload via <code>gradle-play-publisher</code> or <code>fastlane supply</code>; track = <code>internal</code> / <code>alpha</code> / <code>beta</code> / <code>production</code>.</li>
<li>Internal distribution: Firebase App Distribution, App Center, Google Play internal track.</li>
</ul>
<p><strong>2026 specific:</strong></p>
<ul>
<li><strong>Self-hosted Apple Silicon runners</strong> &mdash; iOS builds 2-3&times; faster on M-series; GitHub-hosted ARM macOS runners are GA.</li>
<li><strong>EAS Build</strong> (Expo) for React Native &mdash; managed iOS+Android builds without operating macOS runners.</li>
<li><strong>Codemagic / Bitrise</strong> &mdash; mobile-CI specialists with first-class signing UX and device labs.</li>
<li><strong>Detox / Maestro</strong> for E2E mobile tests; cloud device farms (BrowserStack, Sauce Labs, AWS Device Farm) for fan-out.</li>
<li><strong>Visual regression</strong> via Percy / Chromatic / Maestro snapshot mode.</li>
<li><strong>Versioned native modules</strong> &mdash; React Native New Architecture / Flutter Impeller GA.</li>
</ul>
<p><strong>Pitfalls:</strong> Xcode version drift (project requires 16.x but runner has 15.x); pin <code>xcode-version</code> in workflow. Provisioning profile expires silently &mdash; monitor expiry and rotate. Signing keys in plain GitHub secrets &mdash; use Match or keychain access groups for security. Long iOS build times (20+ min) &mdash; cache <code>~/Library/Caches/CocoaPods</code>, <code>~/Library/Developer/Xcode/DerivedData</code>, and SPM cache.</p>
'''


ANSWERS[80] = r'''<p>IoT app CI/CD on Docker + Kubernetes typically splits into <em>cloud backend</em> (standard K8s deployment) and <em>device firmware</em> (over-the-air updates). The cloud half resembles any SaaS app; device updates need extra care: bandwidth, reliability, offline rollback.</p>
<table>
<thead><tr><th>Layer</th><th>Mechanism</th></tr></thead>
<tbody>
<tr><td>Device firmware</td><td>Built in CI as cross-compiled image; signed; published to OTA service</td></tr>
<tr><td>OTA delivery</td><td>AWS IoT Jobs, Azure IoT Hub Device Update, Google Cloud IoT Core (deprecated &mdash; migrated to ClearBlade), <strong>Mender</strong>, <strong>RAUC</strong>, <strong>SWUpdate</strong>, <strong>balena</strong>, <strong>Eclipse hawkBit</strong></td></tr>
<tr><td>Cloud backend</td><td>Standard K8s deploy &mdash; ingestion (MQTT broker, Kafka), processing (stream processors), storage (TimescaleDB, InfluxDB, ClickHouse)</td></tr>
<tr><td>Edge compute</td><td><strong>K3s</strong>, <strong>MicroK8s</strong>, <strong>KubeEdge</strong>, <strong>Azure IoT Edge</strong>, <strong>AWS IoT Greengrass</strong> &mdash; K8s-shaped clusters at edge sites</td></tr>
<tr><td>Edge GitOps</td><td><strong>Fleet</strong> (Rancher) or <strong>Argo CD ApplicationSets</strong> targeting edge clusters via cluster generator</td></tr>
</tbody>
</table>
<p><strong>OTA update patterns:</strong></p>
<ul>
<li><strong>A/B partition</strong> &mdash; firmware writes new image to inactive partition; reboots into it; if health check fails, rolls back to active. Standard for embedded Linux (Mender, RAUC).</li>
<li><strong>Containerised firmware</strong> &mdash; balena, Azure IoT Edge: each application runs as Docker container; updates pull new image, rolling-restart.</li>
<li><strong>Differential updates</strong> &mdash; binary diff (bsdiff, casync) reduces bandwidth; critical for cellular IoT.</li>
<li><strong>Staged rollout</strong> &mdash; phased OTA: 1% &rarr; 10% &rarr; 50% &rarr; 100%, gated by device-side error reporting.</li>
</ul>
<p><strong>Edge K8s pattern:</strong></p>
<ul>
<li>Each store / factory / vehicle runs a small <strong>K3s</strong> cluster (single-node for low-end, 3-node for HA).</li>
<li>Argo CD or Fleet from a central control plane reconciles edge clusters.</li>
<li>Limited connectivity: pull-based GitOps survives offline; agents sync when network returns.</li>
<li><strong>Akri</strong> (CNCF) discovers leaf devices (USB, IP cameras) and exposes them as resources to scheduling.</li>
</ul>
<p><strong>CI pipeline shape:</strong></p>
<ol>
<li>Cloud backend &mdash; standard build/test/push/deploy via GH Actions / Argo CD.</li>
<li>Edge containers &mdash; cross-compile for ARM64/ARMv7 (<code>buildx --platform</code>); push to registry.</li>
<li>Firmware &mdash; per-board build (Yocto / Buildroot / Apertis); sign with hardware key (HSM or signed in CI via <code>cosign sign-blob</code>); publish to OTA.</li>
<li>Stage to canary device fleet (5%) &mdash; observe error rates, telemetry; promote.</li>
</ol>
<p><strong>2026 specific:</strong></p>
<ul>
<li><strong>SBOM + cosign</strong> on firmware artefacts; transparent supply chain even on tiny devices.</li>
<li><strong>OpenTelemetry on edge</strong> &mdash; OTLP push; cellular-tolerant batching.</li>
<li><strong>WebAssembly (SpinKube, WasmEdge)</strong> at the edge &mdash; smaller, cross-platform, simpler updates than full containers.</li>
<li><strong>Eclipse Symphony</strong> &mdash; CNCF-incubating edge AI/IoT orchestrator.</li>
</ul>
<p><strong>Pitfalls:</strong> bricking devices via untested firmware &mdash; canary devices in lab + staged rollout are non-negotiable. Bandwidth bills from naive full-image OTA &mdash; use diffs or layer-aware updates. Trust assumptions broken by physical access to device &mdash; secure boot, encrypted firmware, signed updates.</p>
'''

ANSWERS[81] = r'''<p>Optimising pod scheduling means giving the kube-scheduler enough signal to place pods on the right nodes the first time and the descheduler enough authority to evict bad placements. The kube-scheduler runs each pod through filter plugins (NodeResourcesFit, NodeAffinity, TaintToleration, VolumeBinding) then score plugins (NodeResourcesBalancedAllocation, ImageLocality, InterPodAffinity); you tune behaviour via <code>KubeSchedulerConfiguration</code> profiles or by writing custom plugins on the scheduler framework.</p>

<p>The everyday levers are <code>nodeSelector</code> for hard placement, <code>nodeAffinity</code> for soft+hard rules, <code>podAffinity</code>/<code>podAntiAffinity</code> for co-location or spreading, <code>topologySpreadConstraints</code> for AZ/zone balance, taints+tolerations for dedicated pools, and <code>PriorityClass</code>+preemption for tier-based eviction. For just-in-time node provisioning, Karpenter (now GA on AWS, Azure, GCP) replaces Cluster Autoscaler and bin-packs by reading pending pod requirements directly &mdash; far faster and cheaper than ASG-based scaling.</p>

<table>
<tr><th>Lever</th><th>When to reach for it</th></tr>
<tr><td>topologySpreadConstraints</td><td>Even spread across zones for HA</td></tr>
<tr><td>podAntiAffinity (required)</td><td>Hard rule: two replicas of a critical service on different nodes</td></tr>
<tr><td>Taints + tolerations</td><td>GPU nodes, spot-only pools, regulated workload isolation</td></tr>
<tr><td>PriorityClass</td><td>System-critical pods preempt batch under pressure</td></tr>
<tr><td>Karpenter NodePool</td><td>JIT bin-packed nodes that match exact pod shape</td></tr>
<tr><td>Descheduler</td><td>Rebalance after scale-up, drift, or unused affinity</td></tr>
</table>

<p>For 1.33+ clusters the in-place pod resize feature lets HPA/VPA adjust requests without recreating pods, which dramatically reduces churn. Avoid required pod-affinity at large scale &mdash; the scheduler&rsquo;s topology checks become O(N&times;M) and dominate scheduling latency.</p>'''

ANSWERS[82] = r'''<p>A Multibranch Pipeline tells Jenkins to scan an SCM repository, discover every branch and pull request that contains a <code>Jenkinsfile</code>, and create a child job for each &mdash; so the pipeline definition lives with the code rather than in Jenkins config. The job type is backed by the <em>workflow-multibranch</em> plugin and the <em>branch-api</em> plugin, with SCM connectors (Git, GitHub Branch Source, Bitbucket Branch Source) supplying the discovery logic.</p>

<p>You configure <em>Branch Sources</em> with credentials and traits: discover branches, discover PRs from origin, discover PRs from forks, filter by name regex, suppress automatic builds, build strategies (only branches with PRs, only tags, only specific names). The plugin installs an SCM webhook so pushes trigger immediate indexing; otherwise Jenkins falls back to a periodic scan interval. Each PR build exposes <code>env.CHANGE_ID</code>, <code>CHANGE_BRANCH</code>, <code>CHANGE_TARGET</code>, and <code>CHANGE_AUTHOR</code> so the Jenkinsfile can post status checks and gate merges.</p>

<table>
<tr><th>Concept</th><th>Detail</th></tr>
<tr><td>Branch Source</td><td>SCM + credentials + discovery traits</td></tr>
<tr><td>Build strategy</td><td>Filter which discovered items actually run</td></tr>
<tr><td>Orphaned item retention</td><td>Auto-delete jobs after N days of branch deletion</td></tr>
<tr><td>Property strategy</td><td>Apply per-branch parameters, retention rules</td></tr>
<tr><td>Organization Folder</td><td>One level up &mdash; auto-discovers <em>repos</em> in a GitHub org/Bitbucket project</td></tr>
</table>

<p>Best practice in 2026 is the Organization Folder pattern: point Jenkins at <code>github.com/your-org</code> and let it auto-onboard every repo with a <code>Jenkinsfile</code>. Pair with Configuration as Code so the folder, credentials, and shared library bindings are reproducible. For monorepos use the <code>scm.changeRequest()</code> when-clause and path filters in shared library helpers to skip unaffected services.</p>'''

ANSWERS[83] = r'''<p>Data-intensive workloads (databases, streaming, lakehouse, ML feature stores) need CI/CD that respects state &mdash; you can&rsquo;t just rolling-update Postgres or Kafka. The pattern is split: the control plane (operators, schemas, configs) ships through normal GitOps, while the data plane (instances, partitions, replicas) ships through operator-aware promotion with explicit backup, migration, and verification gates.</p>

<p>For databases, use operators that own lifecycle: CloudNativePG for Postgres, MariaDB Operator, Percona for MySQL/Mongo, Strimzi for Kafka, RabbitMQ Cluster Operator, Redis Operator. Schema migrations run as Argo Workflows or Jenkins jobs using Atlas (Ariga), Flyway, or Liquibase with expand/contract semantics &mdash; never destructive in a single deploy. For lakehouses (Iceberg, Delta, Hudi) the table format itself is your version control; CI runs <code>nessie</code> or <code>lakeFS</code> branch tests before merging to main.</p>

<table>
<tr><th>Concern</th><th>2026 tooling</th></tr>
<tr><td>Stateful workload lifecycle</td><td>StatefulSets + dedicated Operators (CloudNativePG, Strimzi)</td></tr>
<tr><td>Schema evolution</td><td>Atlas, Flyway, Liquibase &mdash; expand/contract</td></tr>
<tr><td>Backup &amp; PITR</td><td>Velero + CSI snapshots, Barman, Stash</td></tr>
<tr><td>DAG orchestration</td><td>Argo Workflows, Apache Airflow on K8s, Flyte</td></tr>
<tr><td>Data versioning</td><td>lakeFS, Nessie, Pachyderm, DVC</td></tr>
<tr><td>Disruption budget</td><td>PodDisruptionBudget with maxUnavailable: 0 for primaries</td></tr>
</table>

<p>Pre-deploy gates verify backup freshness and replica lag; post-deploy gates run smoke queries and compare row counts. For very large fleets, isolate per-tenant via separate clusters or vCluster &mdash; the blast radius of a bad migration on shared infrastructure is too high.</p>'''

ANSWERS[84] = r'''<p>On-prem delivery from GitHub Actions has two viable shapes &mdash; <em>pull</em> (the cluster reconciles from Git) and <em>push</em> (a runner inside your network applies changes). Pull is the safer default; push is occasionally unavoidable for non-K8s targets like VMware, bare-metal, or legacy Windows servers. Either way, you avoid exposing on-prem APIs to the public internet.</p>

<p>For pull: run Argo CD or Flux inside the on-prem cluster pointing at GitHub. CI builds and pushes images to your internal registry (Harbor, JFrog, ECR over Direct Connect), then bumps a manifest tag in a config repo &mdash; the on-prem GitOps controller pulls it. For push: install Actions Runner Controller (ARC) on a small K8s cluster behind the firewall, or self-hosted runners on hardened VMs, with ephemeral runners auto-recycled per job. Reach the data plane via Tailscale, Cloudflare Tunnel, Teleport, or AWS Site-to-Site VPN.</p>

<table>
<tr><th>Tool</th><th>Use case</th></tr>
<tr><td>Argo CD / Flux on-prem</td><td>Pull-based GitOps for K8s clusters</td></tr>
<tr><td>Actions Runner Controller</td><td>K8s-native ephemeral self-hosted runners</td></tr>
<tr><td>Tailscale / Cloudflare Tunnel</td><td>Zero-trust runner-to-target connectivity</td></tr>
<tr><td>step-security/harden-runner</td><td>Egress allow-list + audit on hosted runners</td></tr>
<tr><td>SPIRE / cert-manager</td><td>Workload identity for runners</td></tr>
</table>

<p>Hard rules: ephemeral runners only (never reuse a runner across jobs, lateral movement risk), pin the runner image by digest, lock down egress with harden-runner, and put network-sensitive jobs on runner groups with repository allow-lists. Audit GITHUB_TOKEN scope per workflow &mdash; default <code>permissions: read-all</code> with explicit elevation per job.</p>'''

ANSWERS[85] = r'''<p>Lambda + Jenkins management splits into three loops: deploy (IaC), observe (metrics/logs/traces), and rollback (alias traffic shift). Jenkins acts as the orchestrator while AWS-native tools own the runtime data. The deploy loop uses AWS SAM, Serverless Framework, AWS CDK, or Pulumi to package the function, push to S3 or ECR, and update an alias; CodeDeploy then performs canary or linear traffic shift between alias versions, watching CloudWatch alarms for automatic rollback.</p>

<p>For observability, enable Lambda Insights (extension, system-level metrics), AWS X-Ray (distributed tracing), and structured JSON logging via Powertools for AWS Lambda &mdash; which also provides idempotency, batch processing, and feature flags. Forward logs and metrics to your platform of choice (Datadog, New Relic, Grafana Cloud) via the OpenTelemetry Collector running as a Lambda extension, or via subscription filters. Set CloudWatch alarms on Errors, Throttles, IteratorAge (for stream sources), and p99 Duration; tie those to CodeDeploy hooks so a bad deploy auto-rolls back.</p>

<table>
<tr><th>Concern</th><th>Tooling</th></tr>
<tr><td>Package &amp; deploy</td><td>SAM, CDK, Serverless Framework, Pulumi</td></tr>
<tr><td>Traffic shift</td><td>CodeDeploy canary/linear with hooks</td></tr>
<tr><td>Tracing</td><td>X-Ray, OpenTelemetry Lambda layer</td></tr>
<tr><td>System metrics</td><td>Lambda Insights extension</td></tr>
<tr><td>SDK helpers</td><td>Powertools for AWS Lambda (Python/Node/Java/.NET)</td></tr>
<tr><td>Cold start mitigation</td><td>Provisioned Concurrency, SnapStart (Java/.NET/Python)</td></tr>
</table>

<p>Jenkins fits as the orchestrator: a multibranch pipeline runs <code>sam validate</code>, <code>sam build</code>, and <code>sam deploy --no-fail-on-empty-changeset</code>, then waits on a CloudWatch synthetic to clear before promoting the alias. Many shops have moved this entire flow to GitHub Actions with OIDC; Jenkins still wins where you have heavy on-prem orchestration alongside Lambda.</p>'''

ANSWERS[86] = r'''<p>Blockchain CI/CD has two layers: smart contracts (deterministic code that lives on-chain) and supporting services (indexers, frontends, off-chain workers). Contracts demand more aggressive testing because deployments are immutable; services pipeline like normal microservices on K8s.</p>

<p>For Solidity (Ethereum, L2s, EVM chains) the 2026 toolchain is Foundry &mdash; <code>forge build</code>, <code>forge test</code> with fuzzing and invariant tests, plus static analysis via Slither and Mythril, and formal verification via Certora or Halmos for critical paths. CI must run a full Anvil/Hardhat fork against mainnet state to catch integration regressions before deployment. For non-EVM, use Anchor (Solana), CosmWasm (Cosmos), or Move tooling (Sui/Aptos). Off-chain workers (indexers like The Graph, Subsquid; relayers; oracle adapters) build like ordinary containers and ship via Argo CD.</p>

<table>
<tr><th>Stage</th><th>Tools</th></tr>
<tr><td>Build/test contracts</td><td>Foundry, Hardhat, Truffle (declining)</td></tr>
<tr><td>Static analysis</td><td>Slither, Mythril, Aderyn, Wake</td></tr>
<tr><td>Formal verification</td><td>Certora, Halmos, Kontrol</td></tr>
<tr><td>Deployment</td><td>Foundry scripts, OpenZeppelin Defender</td></tr>
<tr><td>Indexers on K8s</td><td>The Graph, Subsquid, Goldsky</td></tr>
<tr><td>Storage</td><td>IPFS / Helia, Arweave, Filecoin</td></tr>
<tr><td>Permissioned chains</td><td>Hyperledger Fabric Operator, Besu</td></tr>
</table>

<p>For permissioned chains (Hyperledger Fabric, Besu, Quorum) on K8s, dedicated operators handle peer/orderer rollouts. Sign every artefact with Cosign, store SBOMs, and pin every dependency by hash &mdash; a single supply-chain compromise translates to direct fund loss, so the bar is materially higher than typical web service CI.</p>'''

ANSWERS[87] = r'''<p>&ldquo;Large-scale&rdquo; usually means hundreds of clusters or thousands of namespaces, where any single-cluster pattern collapses. The 2026 default is Argo CD ApplicationSets with the cluster generator, plus a fleet management tool &mdash; Cluster API (CAPI) for cluster lifecycle, Karmada or Open Cluster Management for workload distribution, and Kargo for promotion across stages.</p>

<p>ApplicationSets generate one Argo Application per (cluster &times; environment) combination from a template, so onboarding a new cluster means tagging it in the cluster registry &mdash; the Applications and child syncs fall out automatically. For progressive rollout across the fleet, use a wave generator with manual or automated promotion gates (Kargo Stages with verification queries against Prometheus/Datadog). Each cluster runs Argo Rollouts or Flagger locally so canaries observe real production traffic on that cluster.</p>

<table>
<tr><th>Concern</th><th>Tooling (2026)</th></tr>
<tr><td>Cluster lifecycle</td><td>Cluster API + cloud provider, Talos, Tinkerbell</td></tr>
<tr><td>Fleet GitOps</td><td>Argo CD ApplicationSets, Flux Helm Releases</td></tr>
<tr><td>Multi-cluster scheduling</td><td>Karmada, Open Cluster Management, Liqo</td></tr>
<tr><td>Promotion across stages</td><td>Kargo, Argo Workflows promotion pipelines</td></tr>
<tr><td>Per-cluster canary</td><td>Argo Rollouts, Flagger</td></tr>
<tr><td>Drift detection</td><td>Argo CD self-heal, Kyverno policy reports</td></tr>
</table>

<p>Bottlenecks at scale are the Argo CD repo-server cache and Redis &mdash; shard the controller (one per ~100 clusters) and use ApplicationSet&rsquo;s <code>strategy: RollingSync</code> with a small <code>maxUpdate</code> so a bad manifest doesn&rsquo;t pummel every cluster simultaneously. Always run Kyverno or Gatekeeper as an admission backstop; trust nothing about the manifests reaching each cluster.</p>'''

ANSWERS[88] = r'''<p>Configuration as Code (JCasC) replaces Jenkins&rsquo; clickable web admin with a YAML file describing every controller setting &mdash; security, credentials, clouds, tools, jobs, shared libraries, plugin configs &mdash; that loads at startup and on demand. The plugin <em>configuration-as-code</em> reads <code>jenkins.yaml</code> from <code>$CASC_JENKINS_CONFIG</code> (file or URL) and applies it. Combined with plugin pinning via <code>plugins.txt</code> and the official Jenkins container, you get a fully reproducible controller in a single repo.</p>

<p>The schema is generated dynamically from each plugin&rsquo;s <code>@DataBoundConstructor</code> &mdash; visit <code>/configuration-as-code/reference</code> on a running Jenkins to see every key it accepts. Secrets resolve via <code>${SECRET_NAME}</code> with backends for Vault, AWS Secrets Manager, K8s Secrets, file-based, or <code>casc</code> env vars. Run <code>jenkins.io/configuration-as-code-plugin</code> in <em>apply-only</em> mode in CI to validate without restarting.</p>

<table>
<tr><th>Layer</th><th>Tool</th></tr>
<tr><td>Controller config</td><td>jenkins.yaml + JCasC plugin</td></tr>
<tr><td>Plugin pinning</td><td>plugins.txt with jenkins-plugin-cli</td></tr>
<tr><td>Secrets</td><td>HashiCorp Vault, K8s Secret CSI, AWS SM</td></tr>
<tr><td>Container build</td><td>jenkins/jenkins:lts-jdk21 + COPY jenkins.yaml</td></tr>
<tr><td>Operator (K8s)</td><td>jenkinsci/jenkins-operator (custom resources)</td></tr>
<tr><td>Job DSL</td><td>job-dsl plugin or jobs in casc YAML</td></tr>
</table>

<p>For K8s the Jenkins Operator goes further: it owns CRDs for the controller and seed jobs, watches for drift, and re-applies CASC continuously &mdash; mirroring the GitOps experience you already have for app workloads. Most teams have started shifting to GitHub Actions or Tekton in 2026, but JCasC is what makes a managed Jenkins still defensible: no more &ldquo;Jenkins works because Steve clicked some boxes in 2017&rdquo;.</p>'''

ANSWERS[89] = r'''<p>Edge CI/CD has to cope with thousands of constrained sites that may go offline for hours and run on ARM hardware behind NAT. The pattern is GitOps with a lightweight Kubernetes distribution at the edge and a hub-and-spoke control plane in cloud or DC.</p>

<p>For the edge runtime, K3s, MicroK8s, k0s, and Talos Linux are the 2026 defaults &mdash; small footprint (50&ndash;100 MB), single-binary install, ARM-friendly. Layer KubeEdge, OpenYurt, or SUSE Rancher&rsquo;s Fleet on top for fleet sync and edge-specific autonomy (offline operation, bandwidth-aware sync). Akri exposes IoT devices (USB cameras, ONVIF, OPC UA) as K8s resources so workloads schedule against hardware. Build distroless or chiseled images, enable SOCI or eStargz image streaming so cold pulls finish in seconds, and sign everything with Cosign so the device can verify before run.</p>

<table>
<tr><th>Layer</th><th>Tooling</th></tr>
<tr><td>Edge OS</td><td>Talos, Flatcar, Bottlerocket</td></tr>
<tr><td>K8s distribution</td><td>K3s, MicroK8s, k0s</td></tr>
<tr><td>Edge orchestration</td><td>KubeEdge, OpenYurt, Akri</td></tr>
<tr><td>Fleet sync</td><td>Rancher Fleet, Flux + image automation</td></tr>
<tr><td>Image streaming</td><td>SOCI Snapshotter, eStargz</td></tr>
<tr><td>Vendor stacks</td><td>AWS Greengrass, Azure IoT Edge, Google Distributed Cloud Edge</td></tr>
</table>

<p>For messaging at the edge, MQTT (Mosquitto, EMQX) and Eclipse zenoh are dominant; for stream processing locally, Apache Beam Direct Runner or Bytewax. Always plan for the offline case: edge clusters must reconcile to a known-good state and never trust a partial sync. Stagger rollouts heavily &mdash; a bad image deployed to 10,000 sites simultaneously is the most expensive outage you&rsquo;ll ever see.</p>'''

ANSWERS[90] = r'''<p>The standard GitHub Actions to Fargate pipeline is: authenticate with OIDC, build and push to ECR, register a new task definition revision, then update the ECS service. There&rsquo;s no need for static IAM keys &mdash; the <code>aws-actions/configure-aws-credentials</code> action exchanges the workflow&rsquo;s OIDC token for short-lived STS credentials against an IAM role you trust to GitHub&rsquo;s OIDC issuer.</p>

<pre><code>jobs:
  deploy:
    runs-on: ubuntu-24.04
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-deployer
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2
      - name: Build &amp; push
        run: |
          docker buildx build --platform linux/arm64 \
            --tag $ECR/$REPO:$GITHUB_SHA --push .
      - uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task.json
          container-name: app
          image: $ECR/$REPO:$GITHUB_SHA
        id: task
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.task.outputs.task-definition }}
          service: api
          cluster: prod
          wait-for-service-stability: true
</code></pre>

<table>
<tr><th>Choice</th><th>2026 guidance</th></tr>
<tr><td>Auth</td><td>OIDC role assumption (never static keys)</td></tr>
<tr><td>Architecture</td><td>arm64 (Graviton) for ~30% cost savings</td></tr>
<tr><td>Deploy strategy</td><td>CodeDeploy blue/green with ALB target groups for canary</td></tr>
<tr><td>Alternative</td><td>App Runner for simple HTTP, Copilot CLI for opinionated CI</td></tr>
<tr><td>Image registry</td><td>ECR with lifecycle policy + scan on push</td></tr>
</table>

<p>For zero-downtime deploys add CodeDeploy with an Application+DeploymentGroup so traffic shifts between target groups; CloudWatch alarms attached to the deployment will auto-rollback on 5xx spikes or latency breach. ECS Exec stays useful for incident response &mdash; enable it on the service and gate access via SSM session manager.</p>'''

ANSWERS[91] = r'''<p>etcd is the consistent KV store at the heart of every Kubernetes cluster &mdash; the API server is stateless, but everything you ever <code>kubectl apply</code> ends up as a key in etcd. It uses the Raft consensus protocol across an odd-numbered cluster (3 or 5 members) to tolerate (N&minus;1)/2 failures, persists to disk, and exposes a transactional MVCC interface that the API server uses for optimistic concurrency.</p>

<p>Operationally there are five things to get right: TLS+RBAC on every member-to-member and client-to-member connection, encryption-at-rest for Secrets via the API server&rsquo;s <code>EncryptionConfiguration</code> (with KMS provider), regular snapshots via <code>etcdctl snapshot save</code> sent off-cluster, periodic defragmentation when DB size approaches the quota, and dedicated SSD-backed storage with low fsync latency &mdash; etcd is fsync-bound and a slow disk caps the entire cluster&rsquo;s write throughput.</p>

<table>
<tr><th>Concern</th><th>Action</th></tr>
<tr><td>Backup</td><td><code>etcdctl snapshot save</code> hourly &rarr; S3, with periodic restore drills</td></tr>
<tr><td>Defrag</td><td><code>etcdctl defrag</code> when DB size &gt; 70% of quota</td></tr>
<tr><td>Quota</td><td>Default 2 GiB; bump to 8 GiB only when justified</td></tr>
<tr><td>Storage</td><td>Local NVMe; never network storage with high latency</td></tr>
<tr><td>Encryption-at-rest</td><td>EncryptionConfiguration with kms provider (KMS v2 in 1.29+)</td></tr>
<tr><td>Alternative for tiny clusters</td><td>kine (k3s) backs SQLite/Postgres in place of etcd</td></tr>
</table>

<p>Managed offerings (EKS, GKE, AKS) hide etcd entirely &mdash; the trade-off is opacity if you have a performance issue. For self-managed control planes (kubeadm, Talos, CAPI), prefer Talos where etcd is supervised by the OS and snapshots are automated. Always run an external snapshot pipeline regardless of provider; cluster recovery from a corrupted etcd without a recent snapshot is rarely tractable.</p>'''

ANSWERS[92] = r'''<p>Jenkins X repackaged Kubernetes-native CI/CD into an opinionated stack: Lighthouse (a Prow-derived webhook handler) for SCM events, Tekton Pipelines for build/test, Kustomize/Helm for deployment manifests, and Argo CD or Flux for GitOps sync. The selling point was that you got an end-to-end pipeline by running <code>jx boot</code> and committing a few YAML files; under the hood you adopted a bunch of independent CNCF projects without having to wire them yourself.</p>

<p>In 2026 Jenkins X is firmly in the &ldquo;niche legacy&rdquo; bucket. The components it bundles (Tekton, Argo CD, Lighthouse) all stand on their own and are far more popular as standalone tools, while the Jenkins X glue layer has thin maintenance and a small community. Most teams either run plain Tekton + Argo CD directly, switch to GitHub Actions + Argo CD, or migrate to managed CI like CircleCI/Buildkite paired with GitOps.</p>

<table>
<tr><th>Component</th><th>Role</th><th>2026 alternative</th></tr>
<tr><td>Lighthouse</td><td>Webhook handler</td><td>GitHub Webhooks &rarr; Tekton EventListener, Argo Events</td></tr>
<tr><td>Tekton</td><td>Pipeline runtime</td><td>Tekton standalone, GitHub Actions, Buildkite</td></tr>
<tr><td>Argo CD</td><td>GitOps deploy</td><td>Argo CD or Flux directly</td></tr>
<tr><td>jx CLI</td><td>Bootstrap + promotion</td><td>Kargo for promotion, plain kubectl/helm for ops</td></tr>
</table>

<p>If you&rsquo;re standing up something new, skip Jenkins X &mdash; pick GitHub Actions or Tekton + Argo CD + Kargo directly. If you already run Jenkins X, plan a migration: extract the Tekton pipelines you actually use, point them at Argo CD without Lighthouse, and retire <code>jx</code>. The CNCF foundations are healthy; the wrapper is not.</p>'''

ANSWERS[93] = r'''<p>ML CI/CD is two pipelines glued together: one that ships <em>code</em> (training scripts, serving containers, feature transforms) and one that ships <em>artefacts</em> (model weights, datasets, feature snapshots). They have different change cadences, different review processes, and different rollback semantics &mdash; treating them as one is the most common ML platform mistake.</p>

<p>For experiment tracking and registries, MLflow, Weights &amp; Biases, and Hugging Face Hub dominate; DVC or lakeFS handle dataset and feature versioning. Training DAGs run on Kubeflow Pipelines, Argo Workflows, Flyte, or Metaflow with GPU scheduling via the NVIDIA GPU Operator. For inference on Kubernetes the leaders are KServe (formerly KFServing), Seldon Core v2, Ray Serve, and BentoML; for LLMs specifically vLLM, TensorRT-LLM, and Hugging Face TGI handle batching and KV-cache management. NVIDIA Triton remains the reference multi-framework server.</p>

<table>
<tr><th>Stage</th><th>Tooling (2026)</th></tr>
<tr><td>Experiment tracking</td><td>MLflow, Weights &amp; Biases, Comet</td></tr>
<tr><td>Dataset versioning</td><td>DVC, lakeFS, Pachyderm</td></tr>
<tr><td>Training orchestration</td><td>Kubeflow, Argo Workflows, Flyte, Metaflow</td></tr>
<tr><td>Feature store</td><td>Feast, Tecton, Hopsworks</td></tr>
<tr><td>Inference serving</td><td>KServe, Ray Serve, BentoML, vLLM</td></tr>
<tr><td>Drift detection</td><td>Evidently AI, NannyML, Arize, WhyLabs</td></tr>
<tr><td>GPU scheduling</td><td>NVIDIA GPU Operator + KAI/Volcano scheduler</td></tr>
</table>

<p>Promotion gates compare new model performance to the production model on a holdout slice, then canary on real traffic with shadow deploys. Rollback is fast: KServe&rsquo;s InferenceService stores the previous revision, so reverting is a label change. Always include data drift and prediction drift monitors in production &mdash; a model that scored beautifully in CI can degrade in days under distribution shift.</p>'''

ANSWERS[94] = r'''<p>Ingress controllers are the funnel for every external request &mdash; if they&rsquo;re slow or saturated, every backend looks slow. The 2026 landscape has moved beyond just NGINX: ingress-nginx remains popular but Envoy-based options (Envoy Gateway, Istio Gateway, Cilium Gateway API, Contour, Emissary) and HAProxy-based ones (HAProxy Ingress, Traefik) compete on protocol features and hot-reload behaviour.</p>

<p>Optimisation falls into four buckets: connection (keep-alive, HTTP/2/3, connection pools), worker tuning (CPU pinning, worker_processes, lua threads), data path (eBPF acceleration via Cilium, DPDK), and protocol (gRPC, WebSockets, server-sent events). The Gateway API has matured enough that new clusters should default to it over the legacy Ingress resource &mdash; it has first-class HTTPRoute, GRPCRoute, TLSRoute, and TCPRoute, plus header/path manipulation that Ingress annotations awkwardly bolted on.</p>

<table>
<tr><th>Lever</th><th>What it changes</th></tr>
<tr><td>HTTP/2 + HTTP/3 (QUIC)</td><td>Multiplexed streams, faster handshake, head-of-line elimination</td></tr>
<tr><td>worker_processes auto</td><td>One per CPU; pin via cpu-affinity</td></tr>
<tr><td>keep-alive connections</td><td>Reduce TCP+TLS reconnect cost upstream</td></tr>
<tr><td>External LB direct (proxyless)</td><td>AWS ALB Ingress / GCP GCLB skip the controller pod</td></tr>
<tr><td>Cilium L7 / Gateway</td><td>eBPF datapath, no separate ingress pod</td></tr>
<tr><td>WAF</td><td>Coraza (Envoy/NGINX), AWS WAF, Cloudflare</td></tr>
</table>

<p>Run two replicas minimum with topology spread across zones, set sensible <code>resources</code> requests, and benchmark with k6 or vegeta against a representative workload. For very high throughput, terminate TLS at the cloud LB (ALB, GCLB) and let the in-cluster ingress speak HTTP/2 cleartext upstream &mdash; CPU savings are substantial. Always observe upstream connection-pool exhaustion and 502s; those are early signs of misconfiguration before user-visible failure.</p>'''

ANSWERS[95] = r'''<p>Automated reviews in GitHub Actions stack lint, security, type-check, test coverage, and AI assistance behind required checks &mdash; the goal is that humans review architecture and intent while machines handle mechanical issues. The 2026 default toolset for a polyglot repo is super-linter or megalinter for breadth, then language-specific tools (Ruff for Python, Biome/ESLint for JS/TS, golangci-lint for Go, clippy for Rust) for depth, plus CodeQL, Semgrep, and Trivy for security.</p>

<pre><code>name: code-review
on: pull_request
permissions: { contents: read, pull-requests: write, security-events: write }
jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: super-linter/super-linter@v6
        env:
          DEFAULT_BRANCH: main
          VALIDATE_ALL_CODEBASE: false
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  codeql:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: 'javascript,python' }
      - uses: github/codeql-action/analyze@v3
  semgrep:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with: { config: 'p/owasp-top-ten p/r2c-security-audit' }
</code></pre>

<table>
<tr><th>Layer</th><th>Tools</th></tr>
<tr><td>Lint/style</td><td>super-linter, megalinter, Ruff, Biome</td></tr>
<tr><td>SAST</td><td>CodeQL, Semgrep, SonarCloud, Snyk</td></tr>
<tr><td>SCA / supply chain</td><td>Dependabot, Renovate, Trivy, OSV-Scanner</td></tr>
<tr><td>Coverage</td><td>Codecov, Coveralls, gocov</td></tr>
<tr><td>Secrets scan</td><td>gitleaks, trufflehog</td></tr>
<tr><td>AI review</td><td>Anthropic Claude Code Action, Aikido, CodeRabbit</td></tr>
<tr><td>Pre-commit</td><td>pre-commit.ci runs hooks server-side</td></tr>
</table>

<p>Wire all checks as required via branch protection so a PR can&rsquo;t merge red. Use <code>permissions</code> at the workflow level to lock down GITHUB_TOKEN scope, and keep AI reviewers in advisory mode &mdash; they&rsquo;re excellent at spotting subtle bugs but should never block merges unilaterally.</p>'''

ANSWERS[96] = r'''<p>OpenShift is Red Hat&rsquo;s opinionated Kubernetes distribution: vanilla K8s plus a curated set of upstream projects rebranded and integrated. The defining additions are Routes (TLS-aware HTTP ingress that predated the Gateway API), the integrated container registry, Source-to-Image (S2I) for build-from-Git, Operator Lifecycle Manager (OLM) for installing operators from OperatorHub, RBAC tightened so containers can&rsquo;t run as root by default, and the OpenShift Console &mdash; substantially more polished than the upstream dashboard.</p>

<p>For CI/CD, OpenShift Pipelines is Tekton with Red Hat support, OpenShift GitOps is Argo CD with the same, OpenShift Service Mesh is Istio, and OpenShift Serverless is Knative. The value proposition is a single supported stack with long-term backports rather than chasing upstream releases. ARO (Azure), ROSA (AWS), and IBM Cloud OpenShift give you managed control planes; OpenShift on bare metal still beats vanilla K8s for telco/edge use cases where the integrated installer matters.</p>

<table>
<tr><th>OpenShift component</th><th>Upstream equivalent</th></tr>
<tr><td>Routes</td><td>Ingress / Gateway API</td></tr>
<tr><td>BuildConfig + S2I</td><td>Tekton + Buildpacks / kaniko</td></tr>
<tr><td>OpenShift Pipelines</td><td>Tekton</td></tr>
<tr><td>OpenShift GitOps</td><td>Argo CD</td></tr>
<tr><td>Service Mesh</td><td>Istio</td></tr>
<tr><td>OLM + OperatorHub</td><td>operator-sdk + manual install</td></tr>
<tr><td>SCC (SecurityContextConstraint)</td><td>Pod Security Admission + Kyverno</td></tr>
</table>

<p>Trade-offs: licensing cost, opinionated defaults that don&rsquo;t always match upstream behaviour, slower feature uptake than vanilla K8s. Wins: enterprise support, SCCs that genuinely block escalations by default, and the Operator ecosystem. If you have Red Hat already and need certified support, OpenShift is a pragmatic choice; for greenfield cloud-native shops, vanilla EKS/GKE/AKS plus Argo CD is leaner.</p>'''

ANSWERS[97] = r'''<p>Event-driven systems shift the deployment problem from request paths to broker topology &mdash; you ship producers and consumers independently, and the broker (Kafka, NATS, RabbitMQ, EventBridge) is the contract. The CI/CD pipeline must guarantee schema compatibility, autoscale consumers off queue depth, and gate deploys on consumer lag.</p>

<p>For schemas, run a Schema Registry (Confluent, Apicurio, AWS Glue Schema Registry) and enforce backward/forward compatibility in CI &mdash; <code>kafka-schema-registry-maven-plugin</code> or Apicurio CLI fail the build on breaking changes. Use the CloudEvents specification for envelope-level standardisation across brokers. Contract test producers and consumers with Pact (HTTP/messaging) or Microcks (AsyncAPI) before integration. For autoscaling, KEDA reads broker metrics (Kafka lag, RabbitMQ queue depth, NATS pending, SQS messages) and scales consumer Deployments &mdash; far more accurate than CPU-based HPA.</p>

<table>
<tr><th>Concern</th><th>Tool</th></tr>
<tr><td>Brokers (K8s-native)</td><td>Strimzi (Kafka), NATS Operator, RabbitMQ Cluster Operator</td></tr>
<tr><td>Schema registry</td><td>Confluent, Apicurio, AWS Glue</td></tr>
<tr><td>Event-driven autoscale</td><td>KEDA (50+ scalers in 2026)</td></tr>
<tr><td>Workflow / Sagas</td><td>Knative Eventing, Argo Events, Temporal</td></tr>
<tr><td>Contract testing</td><td>Pact, Microcks (AsyncAPI)</td></tr>
<tr><td>Tracing</td><td>OpenTelemetry context propagation through headers</td></tr>
</table>

<p>For deployment, blue/green is harder than for HTTP &mdash; you can&rsquo;t cleanly stop the message stream. Patterns that work: dual-publish during cutover, consumer groups by version, and idempotency keys so reprocessing is safe. Always run pre-deploy load tests with k6 or Locust against a staging broker; subtle producer changes can saturate a partition unexpectedly.</p>'''

ANSWERS[98] = r'''<p>Jenkins Pipeline DSL extends from the basic Declarative/Scripted distinction into shared libraries, custom steps, and plugin-provided primitives. Complex workflows usually mean: cross-job orchestration, dynamic parallel matrices, library-packaged conventions, and resource-aware scheduling &mdash; all things that benefit from treating pipelines as a real codebase rather than ad-hoc scripts.</p>

<p>A shared library exposes three layers: <code>vars/</code> for global custom steps (each file becomes a callable like <code>deployToProd()</code>), <code>src/</code> for Groovy classes (testable with Spock/JUnit), and <code>resources/</code> for non-Groovy assets (Jenkinsfile templates, Helm value snippets, JSON policy). Configure libraries via JCasC with implicit loading or <code>@Library('platform@v3.2.1') _</code> for explicit version pinning. For complex matrix builds use Declarative <code>matrix</code> with <code>excludes</code> for sparse axes; for fully dynamic shapes, build a <code>Map</code> of branches and pass to <code>parallel</code>.</p>

<table>
<tr><th>Pattern</th><th>Use</th></tr>
<tr><td>Global vars</td><td>Reusable steps: <code>deployToProd()</code>, <code>runIntegrationTests()</code></td></tr>
<tr><td>Library classes (src/)</td><td>Real OO with unit tests</td></tr>
<tr><td>libraryResource</td><td>Pull templated YAML/Helm values into the workspace</td></tr>
<tr><td>parallel + Map</td><td>Dynamic fan-out (one branch per service in a monorepo)</td></tr>
<tr><td>build job + waitForBuild</td><td>Trigger downstream pipelines, gather results</td></tr>
<tr><td>lock + milestone</td><td>Serialise critical sections, allow only newest build to proceed</td></tr>
<tr><td>input + timeout</td><td>Manual approval gates with auto-abandon</td></tr>
</table>

<p>For correctness, write Spock unit tests against shared library classes &mdash; the JenkinsPipelineUnit project lets you simulate steps without a controller. Pin the library by tag in <code>@Library</code> and pin plugins via JCasC. Replay (build &rarr; replay last build with edits) is invaluable for debugging. The most common failure mode at scale is unbounded shared state in static fields &mdash; treat libraries as functional, never store state across builds.</p>'''

ANSWERS[99] = r'''<p>K8s autoscaling has three tiers: pods (HPA, VPA, KEDA), nodes (Cluster Autoscaler or Karpenter), and workload-specific controllers (Argo Rollouts replica adjustment, KEDA scaledobjects). For CI/CD pipelines &mdash; bursty by nature &mdash; the right answer in 2026 is Karpenter for nodes and KEDA for runner pods, because both react in seconds rather than minutes.</p>

<p>Karpenter, now GA on AWS, Azure, and GCP, replaces Cluster Autoscaler with a control loop that reads pending pods, computes the optimal node shape, and provisions it directly &mdash; bypassing ASGs/MIGs/VMSS. Spot/preemptible support is built in with automatic fallback. For pod-level scaling, KEDA bridges queue depth, CI/CD events (GitHub webhooks via the github-runner scaler), Prometheus metrics, and 50+ other sources &mdash; HPA never sees the underlying signal directly.</p>

<table>
<tr><th>Layer</th><th>2026 default</th></tr>
<tr><td>Pod autoscale (CPU/memory)</td><td>HPA + behavior block</td></tr>
<tr><td>Pod autoscale (events)</td><td>KEDA ScaledObject / ScaledJob</td></tr>
<tr><td>Right-sizing</td><td>VPA (Off mode + recommendations), Goldilocks, KRR</td></tr>
<tr><td>Node provisioning</td><td>Karpenter (GA on AWS/Azure/GCP)</td></tr>
<tr><td>Spot / mixed pools</td><td>Karpenter NodePool with multiple instance types</td></tr>
<tr><td>CI runner fleets</td><td>ARC + KEDA github-runner scaler</td></tr>
</table>

<p>For CI specifically, Actions Runner Controller (ARC) plus the KEDA GitHub Runner scaler is the gold standard: pending GitHub jobs scale up ephemeral runner pods, Karpenter scales nodes to match, jobs run, runners terminate, nodes consolidate. Watch out for image pull amplification &mdash; many simultaneous runner pods can DDoS your registry. Use SOCI image streaming and a registry mirror to mitigate, and pre-warm a small minReplicas pool to absorb the initial spike before Karpenter catches up.</p>'''

ANSWERS[100] = r'''<p>Compose was designed for single-host development; running it as a production deployment target in 2026 is a niche choice with viable narrow use cases (small services on a single VM, edge boxes, demos). GitHub Actions can drive Compose two ways &mdash; SSH into a target host and <code>docker compose up</code>, or convert Compose to a Kubernetes/ECS deployment and ship there. The honest answer is that &ldquo;deploying multi-container apps&rdquo; almost always wants the second path.</p>

<pre><code>name: deploy-compose
on:
  push: { branches: [main] }
permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/bake-action@v5
        with: { push: true }
      - name: Deploy to host
        uses: appleboy/ssh-action@v1
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

<table>
<tr><th>Path</th><th>When it fits</th></tr>
<tr><td>SSH + docker compose</td><td>Single host, small team, low traffic</td></tr>
<tr><td>Docker Swarm</td><td>Compose-native clustering &mdash; technically alive, ecosystem largely abandoned</td></tr>
<tr><td>kompose convert</td><td>One-shot port to K8s manifests; expect manual cleanup</td></tr>
<tr><td>Compose Bridge (Docker)</td><td>Modern Compose &rarr; K8s with Helm output</td></tr>
<tr><td>ECS Compose-X</td><td>Compose &rarr; ECS task definitions / CloudFormation</td></tr>
<tr><td>Azure Container Apps</td><td>Compose-native deploy via <code>az containerapp compose</code></td></tr>
</table>

<p>Production-grade for any non-trivial workload: convert to ECS, Container Apps, Cloud Run multi-container, or proper K8s with Helm/Kustomize. Use Compose for local development (pair with <code>compose.override.yaml</code> for environment-specific tweaks) and treat the production target as a separate concern. Hard truth: if you find yourself building elaborate Compose deployment automation, you&rsquo;ve outgrown Compose &mdash; the 2026 alternatives are cheaper to operate.</p>'''
