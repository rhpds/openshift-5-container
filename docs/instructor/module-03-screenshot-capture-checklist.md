# Module 3 — Screenshot capture checklist

**S01–S04 are now authentic screenshots from the student OpenShift lab**, committed as PNGs in `content/modules/ROOT/images/`. S05–S14 remain clearly marked SVG placeholders pending further student rehearsal.

Capture screenshots **from the workshop's real OpenShift 5 / Gitea / GitOps UI** while rehearsing Modules 3 and 4, using a student-owned namespace. Redact passwords, tokens, URLs containing credentials, private user details, and unrelated student namespaces. Screenshots of AgenticRuns may show a **student-owned analysis-only run only after the tenant-isolation gate has passed**. Otherwise capture the instructor demonstration or the student's permission-denied fallback; never imply student rights that are not enabled. Where AgenticRuns or optional tools are unavailable, capture the documented read-only fallback instead; never invent AI output or outcomes.

For the **remaining S05–S14** placeholders, capture a real screenshot in the appropriate state (healthy, injected fault, diagnosis, or repaired), add a PNG with the same basename to `content/modules/ROOT/images/`, and change its reference from `.svg` to `.png`. Do not reuse screenshots from unrelated steps.

| ID | Mission | Image asset | Capture from a real lab session |
| --- | --- | --- | --- |
| S01 | 1 | `module03-s01-student-deployment-baseline.png` | OpenShift terminal: -demo and -gitops Deployments; 3 GitOps workloads Ready; show the student identity |
| S02 | 1 | `module03-s02-resource-usage-quotas.png` | Terminal: CPU/memory requests and limits per tier; Show quota or authorized applied-quota view, no secrets |
| S03 | 1 | `module03-s03-healthy-routes-endpoints.png` | Terminal: ParksMap and API HTTP 200 and ready Service endpoints; Both routes must work before changing the source |
| S04 | 2 | `module03-s04-gitea-frontend-source.png` | Gitea main: 04-parksmap-frontend.yaml; captures the real student source file before the readiness-port edit |
| S05 | 2 | `module03-s05-gitea-bad-readiness-probe.svg` | Gitea YAML editor: port 18080 instead of http; Keep containerPort 8080; do not alter resources |
| S06 | 2 | `module03-s06-gitea-fault-commit.svg` | Gitea: main branch commit for probe mismatch; Show commit message and changed line only |
| S07 | 2 | `module03-s07-argocd-stalled-rollout.svg` | Argo CD Application: source revision and rollout health; Sync status may be green while rollout is not complete |
| S08 | 2 | `module03-s08-new-pod-readiness-events.svg` | Pods, ReplicaSets and readiness failure events; New Pod Not Ready; old ready Pod may still serve |
| S09 | 3 | `module03-s09-lightspeed-troubleshooting-prompt.svg` | Lightspeed Troubleshooting mode with student-scoped prompt; Include namespace and read-only investigation request |
| S10 | 3 | `module03-s10-lightspeed-evidence-root-cause.svg` | Lightspeed read-only tool evidence and root-cause output; Show 18080 probe vs 8080 listener; no mutations |
| S11 | 4 | `module03-s11-agenticrun-student-rbac.svg` | Terminal: AgenticRun API and student can-i checks; Permission denied is normal; show instructor path |
| S12 | 4 | `module03-s12-agenticrun-analysis-proposal.svg` | Authorized student analysis-only AgenticRun or instructor view; Show actual evidence and no execution stage; otherwise document restricted-access fallback |
| S13 | 5 | `module03-s13-gitea-readiness-repair.svg` | Gitea commit: port http restored, old port removed; Keep repairs source-controlled in student main |
| S14 | 5 | `module03-s14-argocd-healthy-recovery.svg` | GitOps Synced / Healthy; new Pod Ready and map HTTP 200; Original -demo app remains working |

Acceptance: the screenshot corresponds to the adjacent student action, is readable at 850px rendered width, depicts only the intended namespace and actual tool output, and hides any credentials. Once all screenshots are captured, the remaining `SCREENSHOT NEEDED` SVG files can be removed in a later cleanup PR.
