# Module 4 — Screenshot capture checklist

Placeholders are intentionally visible in the student's AsciiDoc lab until authentic screenshots are captured. They are **not** screenshots of a working environment. Each numbered SVG has a corresponding suggested PNG filename printed on it.

Capture screenshots **from the workshop's real OpenShift 5 / Gitea / GitOps UI** while rehearsing Modules 3 and 4, using a student-owned namespace. Redact passwords, tokens, URLs containing credentials, private user details, and unrelated student namespaces. Screenshots of AgenticRuns should be produced **only by an authorized instructor** and marked as instructor demonstrations. Where AgenticRuns or optional tools are unavailable, capture the documented read-only fallback instead; never invent AI output or outcomes.

To publish a captured PNG, add it to `content/modules/ROOT/images/` with the same basename as the SVG and change that one AsciiDoc image directive from `.svg` to `.png`. Keep the numbered step and descriptive alt text. Rehearse that screenshot's exact application state first (healthy, injected fault, diagnosis, or repaired)—do not reuse the same screenshot across different states.

| ID | Mission | Current placeholder SVG | Capture from a real lab session |
| --- | --- | --- | --- |
| S01 | 1 | `module04-s01-healthy-api-routes.svg` | Terminal or browser: ParksMap, health and data HTTP 200; Healthy baseline before touching Gitea |
| S02 | 1 | `module04-s02-parks-record-count.svg` | Terminal: /ws/data/all returns a non-empty JSON array; Record count; do not rerun data loader |
| S03 | 2 | `module04-s03-gitea-backend-source.svg` | Student Gitea main: 02-nationalparks-backend.yaml; Highlight Deployment, not BuildConfig or ImageStream |
| S04 | 2 | `module04-s04-gitea-wrong-db-host.svg` | Gitea editor: explicit env DATABASE_SERVICE_NAME; Wrong mongodb-national-parks vs correct Service name |
| S05 | 2 | `module04-s05-gitea-commit-and-argocd.svg` | Student Gitea commit and Argo CD new revision; Do not manually Sync; watch Application status |
| S06 | 2 | `module04-s06-healthy-pods-broken-data.svg` | Backend health vs /ws/data/all timeout or error; Show actual status, not an invented fixed HTTP code |
| S07 | 3 | `module04-s07-lightspeed-data-path-prompt.svg` | Lightspeed Troubleshooting prompt for student namespace; Live read-only tool requests; no Secrets |
| S08 | 3 | `module04-s08-backend-env-vs-mongodb-service.svg` | OpenShift console or terminal: explicit env and Service; Confirm bad host override and correct Service name |
| S09 | 3 | `module04-s09-dns-and-backend-log-evidence.svg` | Backend logs and optional read-only DNS checks; Only show observed output; no fabricated tool results |
| S10 | 3 | `module04-s10-lightspeed-db-root-cause.svg` | Lightspeed tool evidence about env-over-envFrom precedence; Recommend removing explicit override, not editing Secret |
| S11 | 4 | `module04-s11-agenticrun-capability-check.svg` | Terminal: API present; student RBAC and CLI results; Student Forbidden / absent CLI is an expected result |
| S12 | 4 | `module04-s12-agenticrun-db-investigation.svg` | Instructor AgenticRun analysis, evidence and proposal; No execution; fallback if permissions are restricted |
| S13 | 5 | `module04-s13-gitea-remove-bad-override.svg` | Gitea repair commit removing the explicit env block; Keep envFrom Secret reference; never show credentials |
| S14 | 5 | `module04-s14-argocd-backend-recovery.svg` | Argo CD Synced / Healthy with repaired backend Pod; No explicit bad env; no direct workload patch |
| S15 | 5 | `module04-s15-restored-parks-map-markers.svg` | API non-empty park count and ParksMap with markers; Original and GitOps stacks healthy after recovery |

Acceptance: the screenshot corresponds to the adjacent student action, is readable at 850px rendered width, depicts only the intended namespace and actual tool output, and hides any credentials. Once all screenshots are captured, the remaining `SCREENSHOT NEEDED` SVG files can be removed in a later cleanup PR.
