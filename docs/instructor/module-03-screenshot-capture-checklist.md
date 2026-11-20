# Module 3 — Workload Management screenshot checklist

Module 3 now teaches quota-aware resource sizing rather than a duplicate ParksMap readiness incident. Four already-captured **real** student screenshots remain referenced. Two **new, clearly marked SVG placeholders** are reserved for the Perses student experience; previous AgenticRun/readiness assets with different filenames remain historical and must not be reused as new evidence.

| ID | Asset | Student evidence |
| --- | --- | --- |
| S01 | `module03-s01-student-deployment-baseline.png` | Two healthy National Parks stacks and namespaced Deployment baseline |
| S02 | `module03-s02-resource-usage-quotas.png` | Requests/limits and authorized shared-quota view; **not** proof of live CPU/memory usage |
| S03 | `module03-s03-healthy-routes-endpoints.png` | Healthy Routes and independent original application after sizing decision |
| S04 | `module03-s04-gitea-frontend-source.png` | Student-owned canonical ParksMap YAML before or during a bounded resource-request edit |
| S05 | `module03-s05-perses-workload-dashboard.svg` | **REPLACE:** student OpenShift 5 Observe → Dashboards (Perses), project `user-<guid>-gitops`, named *OpenShift 5 | National Parks & WeatherNow* dashboard, genuine panels and time window |
| S06 | `module03-s06-perses-metrics-comparison.svg` | **REPLACE:** actual CPU/memory working set trends from the student project with requests/limits observed separately (no invented values) |

## Recommended additional screenshots

S05 and S06 placeholders are **already linked** from Module 3. Capture genuine redacted PNGs with those basenames and switch only the corresponding `.svg` page references to `.png`. Additionally capture the student Gitea request edit and Argo CD revision if real evidence is available; do not link files before they exist. A screenshot of a project selector alone does **not** establish datasource query isolation: the instructor must separately record the tested authorization gate.

Student screenshots must use a real student identity and their own namespace. Hide passwords, tokens, unrelated namespaces, private PromQL queries returning other tenants' data, and Secret values. Real screenshots are a release gate, not student homework.

See `docs/instructor/cluster-observability-workshop-preflight.md` for COO/Perses RBAC checks and `docs/instructor/module-03-agentic-app-deployment-preflight.md` for operational acceptance. AgenticRuns are deferred and should not appear as required student screenshots.
