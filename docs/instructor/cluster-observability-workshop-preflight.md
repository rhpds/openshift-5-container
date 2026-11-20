# Cluster Observability Operator and five-outcome workshop preflight

## Recommendation and scope

For OpenShift 5.0, provision a supported **Cluster Observability Operator (COO) 1.6** installation before the class, enable the monitoring UIPlugin with **Perses**, and expose an instructor-validated, tenant-scoped dashboard for ParksMap and WeatherNow. COO 1.5 or later supports Perses, but 1.6 is preferred when supported by the actual OCP build and OperatorHub catalog.

The COO is an **instructor/platform prerequisite**, not a student install step. Avoid one `MonitoringStack` per student (30 concurrent students would create substantial additional Prometheus load). Prefer existing OpenShift cluster monitoring/user workload metrics, correctly authorized datasources and a preconfigured Perses dashboard. COO does not, by itself, install Loki/Vector logging, Tempo tracing backends, or instrument the application. Do **not** claim logs, traces or signal correlation are available until separately provisioned and verified.

References:
- [Red Hat guide to observability with OpenShift 5](https://www.redhat.com/en/blog/guide-observability-red-hat-openshift-5)
- [COO overview](https://docs.redhat.com/en/documentation/red_hat_openshift_cluster_observability_operator/1-latest/html/about_red_hat_openshift_cluster_observability_operator/cluster-observability-operator-overview)
- [COO UI plugins / Perses](https://docs.redhat.com/en/documentation/red_hat_openshift_cluster_observability_operator/1-latest/html-single/ui_plugins_for_red_hat_openshift_cluster_observability_operator/index)

## Instructor setup (cluster-admin)

1. Check the **installed** COO and OCP versions and confirm their supported combination through the current Red Hat release notes; never assume installation from the workshop attributes.
2. Install COO using the supported OperatorHub workflow into its documented namespace if it is not already present. Choose a supported channel/version; do not perform cluster-wide operator installation from student namespaces.
3. Enable the COO monitoring UI and Perses using `automation/observability/monitoring-uiplugin.yaml` only after the operator is healthy. Review any existing `UIPlugin/monitoring` before applying; do not replace a differently configured production UIPlugin.
4. Reuse the existing Thanos-backed metrics source where practical. Provision dashboard access only to the tenant's own workload metrics; explicitly check **query** authorization, not just dashboard object RBAC. A cluster-wide datasource can otherwise expose metrics for other tenants. Never grant student `cluster-monitoring-view`, `cluster-reader`, or global Prometheus tokens merely to make a dashboard work.
5. Prepare a shared *dashboard design* (CPU usage, memory working set, Pod restart/ready count) but ensure student project context + namespace selectors are enforced server-side. Verify a student cannot change PromQL to query another student's namespace; if this cannot be proven, use console workload metrics instead and withhold the Perses dashboard.
6. Preflight the live metrics pipeline for at least one ParksMap and WeatherNow workload. Use actual data gathered during the exercise, not fabricated charts.

Read-only diagnostics (admin context):
```bash
oc get clusterversion
oc get csv -n openshift-cluster-observability-operator
oc get uiplugins.observability.openshift.io
oc get pods -n openshift-cluster-observability-operator
oc get persesdashboards.perses.dev -A
oc get pods -n openshift-monitoring
oc get pods -n openshift-user-workload-monitoring
```

Student checks (their existing identity; no extra roles):
```bash
oc whoami
oc adm top pods -n "$(oc whoami)-gitops" --containers
oc auth can-i get persesdashboards.perses.dev -n "$(oc whoami)-gitops"
```

If COO or metrics are not ready, Module 3 records the limitation and forbids guessed right-sizing. The instructor should supply an authentic, sanitized per-namespace metrics snapshot, or explicitly mark the right-size exercise unverified. Modules 4–5 still work through namespaced CLI/Events and GitOps; do not block the class on optional tracing.

## Five-outcome readiness gates

| Outcome | Live gate |
| --- | --- |
| GitOps | Student Gitea workspace imported and current; correct Argo CD source path; full three-tier stack Synced/Healthy; student can commit |
| Multitenancy | Student can create a **scoped canary** NetworkPolicy; before policy, same-tenant cross-namespace reachability passes; after policy, same-namespace passes and other namespace is denied. Separately test cross-**student** API and network access from authorized instructor probes |
| Workload | Shared quota has room for brief canary and one ParksMap RollingUpdate surge; applied quota view and real metrics accessible or sanitized instructor snapshot available |
| Investigation | WeatherNow bad readiness probe generates a new unready Pod; Events, Pod logs, CPU/memory metrics and actual ReplicaSet states are observable. Traces are optional only when instrumented |
| Lifecycle | Broken image tag produces ErrImagePull/ImagePullBackOff; Gitea repair commit appears as Argo CD revision; restored Pod Ready; HTTP Route works; both National Parks stacks untouched |

## Network canary safety

Module 2 only adds and removes `Deployment/workshop-netcheck`, `Service/workshop-netcheck`, and `NetworkPolicy/workshop-netcheck-ingress` in that student's `-gitops` namespace. Its policy selects only the canary label. Check that neither an existing policy nor SCC/image pull constraints prevent the **before** test. A pre-existing failure is not proof of policy isolation.

Use a separate instructor-driven test in two genuinely different tenant namespaces to validate cross-student isolation; Module 2's test uses `-demo` and `-gitops` for *one* student and cannot independently prove two students are isolated.

Confirm cleanup after each student and that quota allows the temporary Pod. Do not modify global NetworkPolicy, routes, Secrets or tenant quotas.

## Operational acceptance

- Run once using a real student and an instructor identity with restricted and approved permissions.
- Record actual Gitea clone/import, App revision, 5-module execution and rollback test results.
- Verify no data-leaking Perses datasource or elevated monitoring credentials.
- Confirm student AgenticRun creation is **not requested** and teacher/demo prompts are conceptual only.
- Validate screenshots for the updated Module 2 network canary and new Module 3 metrics/right-sizing workflow before publishing.

## Optional OpenShift 5 extension

COO 1.6 integrates with the Red Hat build of Perses and Lightspeed-generated dashboards. With an approved provider and properly scoped metrics datasource, an instructor can ask Lightspeed for a chart of workload CPU/memory and inspect the generated PromQL/time range. Do not make AI chart creation a student completion gate; availability is dependent on the installed build and configured integrations.
