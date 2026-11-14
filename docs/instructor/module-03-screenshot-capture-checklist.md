# Module 3 — Screenshot capture checklist

Placeholders are intentionally visible in the student's AsciiDoc lab until authentic screenshots are captured. They are **not** screenshots of a working environment. Each numbered SVG has a corresponding suggested PNG filename printed on it.

Capture screenshots **from the workshop's real OpenShift 5 / Gitea / GitOps UI** while rehearsing Modules 3 and 4, using a student-owned namespace. Redact passwords, tokens, URLs containing credentials, private user details, and unrelated student namespaces. Screenshots of AgenticRuns should be produced **only by an authorized instructor** and marked as instructor demonstrations. Where AgenticRuns or optional tools are unavailable, capture the documented read-only fallback instead; never invent AI output or outcomes.

To publish a captured PNG, add it to `content/modules/ROOT/images/` with the same basename as the SVG and change that one AsciiDoc image directive from `.svg` to `.png`. Keep the numbered step and descriptive alt text. Rehearse that screenshot's exact application state first (healthy, injected fault, diagnosis, or repaired)—do not reuse the same screenshot across different states.

| ID | Mission | Current placeholder SVG | Capture from a real lab session |
| --- | --- | --- | --- |
| S01 | 1 | `module03-s01-student-deployment-baseline.svg` | OpenShift terminal: -demo and -gitops Deployments; 3 GitOps workloads Ready; show the student identity |
| S02 | 1 | `module03-s02-resource-usage-quotas.svg` | Terminal: CPU/memory requests and limits per tier; Show quota or authorized applied-quota view, no secrets |
| S03 | 1 | `module03-s03-healthy-routes-endpoints.svg` | Terminal: ParksMap and API HTTP 200 and ready Service endpoints; Both routes must work before changing the source |
| S04 | 2 | `module03-s04-gitea-frontend-source.svg` | Gitea main: fullstack/04-parksmap-frontend.yaml; Highlight the Deployment readinessProbe in this file |
| S05 | 2 | `module03-s05-gitea-bad-readiness-probe.svg` | Gitea YAML editor: port 18080 instead of http; Keep containerPort 8080; do not alter resources |
| S06 | 2 | `module03-s06-gitea-fault-commit.svg` | Gitea: main branch commit for probe mismatch; Show commit message and changed line only |
| S07 | 2 | `module03-s07-argocd-stalled-rollout.svg` | Argo CD Application: source revision and rollout health; Sync status may be green while rollout is not complete |
| S08 | 2 | `module03-s08-new-pod-readiness-events.svg` | Pods, ReplicaSets and readiness failure events; New Pod Not Ready; old ready Pod may still serve |
| S09 | 3 | `module03-s09-lightspeed-troubleshooting-prompt.svg` | Lightspeed Troubleshooting mode with student-scoped prompt; Include namespace and read-only investigation request |
| S10 | 3 | `module03-s10-lightspeed-evidence-root-cause.svg` | Lightspeed read-only tool evidence and root-cause output; Show 18080 probe vs 8080 listener; no mutations |
| S11 | 4 | `module03-s11-agenticrun-student-rbac.svg` | Terminal: AgenticRun API and student can-i checks; Permission denied is normal; show instructor path |
| S12 | 4 | `module03-s12-agenticrun-analysis-proposal.svg` | Instructor view: AgenticRun phases and tool evidence; No execution stage; if unavailable show fallback evidence |
| S13 | 5 | `module03-s13-gitea-readiness-repair.svg` | Gitea commit: port http restored, old port removed; Keep repairs source-controlled in student main |
| S14 | 5 | `module03-s14-argocd-healthy-recovery.svg` | GitOps Synced / Healthy; new Pod Ready and map HTTP 200; Original -demo app remains working |

Acceptance: the screenshot corresponds to the adjacent student action, is readable at 850px rendered width, depicts only the intended namespace and actual tool output, and hides any credentials. Once all screenshots are captured, the remaining `SCREENSHOT NEEDED` SVG files can be removed in a later cleanup PR.
