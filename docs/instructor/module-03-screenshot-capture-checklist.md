# Module 3 — Workload Management screenshot checklist

Four original student captures document the operational baseline. S05 and S06 show ParksMap usage in the native OpenShift Metrics view.

| Step | Published PNG | Browser evidence |
| --- | --- | --- |
| S01 | `module03-s01-student-deployment-baseline.png` | Two healthy National Parks stacks and namespaced Deployment baseline |
| S02 | `module03-s02-resource-usage-quotas.png` | Requests/limits and authorized shared-quota view; **not** proof of live CPU/memory usage |
| S05 | `module03-s05-native-workload-memory.png` | Native Observe Metrics graph of the ParksMap memory working set in MiB |
| S06 | `module03-s06-native-cpu-usage.png` | Native Observe Metrics graph of ParksMap CPU usage in cores |
| S03 | `module03-s03-healthy-routes-endpoints.png` | Healthy Routes and independent original application after sizing decision |
| S04 | `module03-s04-gitea-frontend-source.png` | Student-owned canonical ParksMap YAML before or during a bounded resource-request edit |

## Perses capture still needed

The student project showed **No dashboards found**. The guide illustrates its native **Observe → Metrics** fallback. After the tenant-authorized datasource and `PersesDashboard/workshop-workloads` pass the [observability preflight](cluster-observability-workshop-preflight.md), capture the named dashboard with its project and time range (S05), and its ParksMap CPU and memory trends alongside verified resource requests (S06).
