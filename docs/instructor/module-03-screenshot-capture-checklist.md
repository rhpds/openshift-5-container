# Module 3 — Workload Management screenshot checklist

Module 3 now teaches quota-aware resource sizing rather than a duplicate ParksMap readiness incident. Only four already-captured **real** student screenshots are referenced; the obsolete S05–S14 AgenticRun and readiness-probe SVG assets remain in the image directory for historical reference but must **not** be shown as current Module 3 steps.

| ID | Asset | Student evidence |
| --- | --- | --- |
| S01 | `module03-s01-student-deployment-baseline.png` | Two healthy National Parks stacks and namespaced Deployment baseline |
| S02 | `module03-s02-resource-usage-quotas.png` | Requests/limits and authorized shared-quota view; **not** proof of live CPU/memory usage |
| S03 | `module03-s03-healthy-routes-endpoints.png` | Healthy Routes and independent original application after sizing decision |
| S04 | `module03-s04-gitea-frontend-source.png` | Student-owned canonical ParksMap YAML before or during a bounded resource-request edit |

## Recommended additional screenshots

Capture a **new**, appropriately named and reviewed screenshot of COO/Perses CPU/memory with project filter, time range, and evidence of tenant isolation; also capture the student Gitea request edit and Argo CD revision after any change. These are not yet committed or referenced by the student page, and **must not** be described as already captured.

Student screenshots must use a real student identity and their own namespace. Hide passwords, tokens, unrelated namespaces, private PromQL queries returning other tenants' data, and Secret values. Real screenshots are a release gate, not student homework.

See `docs/instructor/cluster-observability-workshop-preflight.md` for COO/Perses RBAC checks and `docs/instructor/module-03-agentic-app-deployment-preflight.md` for operational acceptance. AgenticRuns are deferred and should not appear as required student screenshots.
