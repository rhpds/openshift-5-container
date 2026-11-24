# Cluster Observability Operator and five-outcome workshop preflight

## Recommendation and scope

For OpenShift 5.0, provision a supported **Cluster Observability Operator (COO) 1.5.5 or later** installation before the class, enable the monitoring UIPlugin with **Perses**, and expose an instructor-validated, tenant-scoped dashboard for ParksMap and WeatherNow. The 20 November 2026 class cluster was observed with COO **1.5.5**, UIPlugin/monitoring Reconciled=True/Available=True, Perses StatefulSet 1/1 and Bound storage. COO 1.6 is an optional upgrade only if offered and compatible.

The COO is an **instructor/platform prerequisite**, not a student install step. Avoid one `MonitoringStack` per student (30 concurrent students would create substantial additional Prometheus load). Prefer existing OpenShift cluster monitoring/user workload metrics, correctly authorized datasources and a preconfigured Perses dashboard. COO does not, by itself, install Loki/Vector logging, Tempo tracing backends, or instrument the application. Do **not** claim logs, traces or signal correlation are available until separately provisioned and verified.

References:
- [Red Hat guide to observability with OpenShift 5](https://www.redhat.com/en/blog/guide-observability-red-hat-openshift-5)
- [COO overview](https://docs.redhat.com/en/documentation/red_hat_openshift_cluster_observability_operator/1-latest/html/about_red_hat_openshift_cluster_observability_operator/cluster-observability-operator-overview)
- [COO UI plugins / Perses](https://docs.redhat.com/en/documentation/red_hat_openshift_cluster_observability_operator/1-latest/html-single/ui_plugins_for_red_hat_openshift_cluster_observability_operator/index)

## Instructor setup (cluster-admin)

1. Check the **installed** COO and OCP versions and confirm their supported combination through the current Red Hat release notes; never assume installation from the workshop attributes.
2. COO is installed by the infra GitOps chart (`automation/gitops/bootstrap-infra`): `cluster-observability-operator` on channel `stable`, sourced from the pinned RHPDS `redhat-operators` snapshot, into `openshift-cluster-observability-operator`. Confirm the CSV reaches `Succeeded` before relying on it; do not perform cluster-wide operator installation from student namespaces.
3. The chart also enables the COO monitoring UI and Perses at sync-wave 1 via `automation/gitops/bootstrap-infra/templates/cluster-observability/uiplugin-perses.yaml`. Review any existing `UIPlugin/monitoring` before the first sync; do not replace a differently configured production UIPlugin.
4. The per-seat Helm chart provisions `PersesDashboard/workshop-workloads` and `PersesDatasource/workshop-workloads` in the GitOps project. Its HTTP proxy uses the Thanos tenancy port (9092) with the project's namespace. It references the project-local Perses secret generated from the service CA. Confirm all four panels execute queries as the student.
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

## Instructor provisioning for the student Perses dashboard (COO 1.5.5)

**Observed on the class cluster:** The monitoring UIPlugin automatically created `PersesDatasource/accelerators-thanos-querier-datasource` in `openshift-cluster-observability-operator`. It is owner-managed by `UIPlugin/monitoring`, references an operator-managed authentication Secret and connects to `https://thanos-querier.openshift-monitoring.svc.cluster.local:9091`. That is **not** a student datasource, and the installed accelerator/APM dashboards are not workload CPU/memory panels for our uninstrumented applications. Do **not** clone its Secret, copy its token, change its controller ownerReference, or create a permissive `PersesGlobalDatasource`.

The tenant chart in `automation/gitops/bootstrap-tenant/templates/perses/` is the default installation. OpenShift's Thanos proxy maps a range-query POST to the RBAC verb `create` on `pods.metrics.k8s.io` in the requested namespace. The chart binds this permission only to the assigned user in their GitOps project. Workload Pods use the separate core API group.

For a seat previously installed from PR #72, reconcile the tenant chart with pruning and verify that the obsolete `<student>-cluster-monitoring-view` ClusterRoleBinding has been removed. With pruning disabled, the original binding can survive the update. The instructor should inspect its roleRef and subject before removing the old chart-owned binding. Run the following checks with instructor impersonation privileges and two dedicated workshop test namespaces:

```bash
oc auth can-i create pods.metrics.k8s.io -n "$STUDENT-gitops" --as="$STUDENT"  # yes
oc auth can-i create pods.metrics.k8s.io -n "$REFERENCE_NS" --as="$STUDENT"  # no
oc get clusterrolebinding "$STUDENT-cluster-monitoring-view"  # expect NotFound
```

If all panels report `x509: certificate signed by unknown authority`, check that `spec.config.plugin.spec.proxy.spec.secret` references `workshop-workloads-secret` and that `spec.client.tls.caCert.certPath` is `/ca/service-ca.crt`. If panels report `Forbidden` with `verb=create, resource=pods`, check the tenancy URL and namespaced RoleBinding. A successful query with data for a running workshop workload is the acceptance check. [COO user-defined dashboard example](https://github.com/rhobs/observability-operator/blob/a548f7411424ba265dda31e37593d9bbf0fc6377/docs/user-guides/perses-dashboards/user-defined-dashboard/01-datasource.yaml)

The following files also support installations with a separately managed tenant metrics backend:

- `automation/gitops/bootstrap-infra/templates/cluster-observability/uiplugin-perses.yaml` — managed by the infra chart; COO manages Perses
- `automation/observability/workshop-workloads-datasource.EXAMPLE.yaml` — **non-executable example** of a namespaced Prometheus/Thanos datasource *after* a backend-enforced tenant-specific proxy and its credentials have been independently provisioned
- `automation/observability/workshop-workloads-dashboard.yaml` — reusable `PersesDashboard` v1alpha2 template with CPU, memory working set, restarts and ready-state panels
- `automation/observability/prepare-student-perses-dashboard.sh` — **dry-run by default**, refuses an absent `PersesDatasource/workshop-workloads`, and refuses deployment without an explicit tenant-query-isolation attestation

Red Hat documents `PersesDashboard` and `PersesDatasource` as namespace-scoped CRs. A namespaced dashboard does **not** make the datasource's backend metrics automatically tenant-safe. Query authorization must be enforced *server-side*: for example, via an approved, individually authenticated metrics query proxy that rejects arbitrary PromQL requesting other tenant namespaces. Selecting `namespace="user-..." ` inside dashboard queries is a display convenience, **not access control**.

### Phase A — backend access and operator preflight

1. Confirm `oc get uiplugin monitoring`, `oc get pods -n openshift-cluster-observability-operator`, and a real student `oc adm top pods -n user-<guid>-gitops --containers`.
2. Check the chart-managed datasource against the Thanos tenancy endpoint. If using a separately managed backend, configure the namespaced datasource for that backend using the example. Its credential may only request metrics for the assigned tenant. Do not give students `cluster-reader`, `cluster-monitoring-view`, a reusable cluster-wide service token or access to any operator-managed Secret.
3. Confirm the datasource `Available=True` and test **real queries** for the approved namespace and for a different tenant, including custom/edited PromQL, variable changes and direct proxy API calls where applicable. An unauthorized query must be denied by the proxy/backend — a dashboard selector or empty result isn't proof.
4. Confirm student RBAC for the dashboard and datasource objects. Prefer read-only `RoleBinding` resources in `user-<guid>-gitops` referencing `persesdashboard-viewer-role` and `persesdatasource-viewer-role` if current tenant roles do not already suffice; never grant a ClusterRoleBinding globally.
5. Only after successful tenant-query isolation may an instructor publish the dashboard.

Useful diagnostic commands (run as admin; never print the Secret's data):

```bash
oc get persesdatasource accelerators-thanos-querier-datasource \
  -n openshift-cluster-observability-operator -o jsonpath='{.spec.config.display.name}{"\\n"}'
oc get svc thanos-querier -n openshift-monitoring
oc get persesdatasource workshop-workloads -n user-xxxxx-gitops
oc get persesdashboard workshop-workloads -n user-xxxxx-gitops
oc auth can-i get persesdashboards.perses.dev -n user-xxxxx-gitops --as=user-xxxxx
oc auth can-i get persesdatasources.perses.dev -n user-xxxxx-gitops --as=user-xxxxx
```

### Phase B — publish a tested dashboard per tenant

The tenant chart publishes the dashboard during provisioning. For a separately managed installation, the instructor can render or apply the dashboard from the workshop checkout:

```bash
bash automation/observability/prepare-student-perses-dashboard.sh user-xxxxx

bash automation/observability/prepare-student-perses-dashboard.sh \
  user-xxxxx --apply --tenant-query-isolation-verified
```

The first command is **read-only** and prints the rendered dashboard. The second applies a `PersesDashboard/workshop-workloads` only when its namespace datasource exists and the instructor explicitly attests query isolation. The helper does *not* provision or secure the metrics backend, create Secrets, or elevate RBAC.

Rehearse the exact student workflow: log in as the student, choose **Observe → Dashboards (Perses)**, select `user-xxxxx-gitops`, open **OpenShift 5 | National Parks & WeatherNow**, and record whether the four charts display *actual* workload data during baseline, WeatherNow failure, and recovery. Compare with `oc adm top`, Pod Events and `oc rollout status`.

### Phase C — screenshot capture and release gate

The student modules illustrate the native **Observe → Metrics** fallback. An earlier rehearsal seat showed **No dashboards found**. On 24 November 2026 a student seat with the service CA and project query role plotted all four Perses panels. The CPU and memory panels showed workload time series, restarts held at zero, and the readiness panel showed both 0 and 1 during the WeatherNow exercise. Verify the separate tenant-isolation checks above before publishing classroom screenshots.

| Module and figure | Published native evidence | Pending Perses capture |
| --- | --- | --- |
| 3 S05 | ParksMap memory working set | Named workload dashboard, project and time range |
| 3 S06 | ParksMap CPU usage | CPU and memory trends compared with resource requests |
| 4 S16 | Ready condition of both WeatherNow incident Pods | Readiness and restarts during the probe fault |
| 5 S13 | Serving WeatherNow Pod’s memory after recovery | Readiness and resource use during the repaired rollout |

Use the module capture checklists to publish each additional view only after the dashboard returns actual workload samples.

**Fail-closed teaching path:** If the tenant proxy or dashboard fails authorization/data preflight, do not expose it to students. Modules 3–5 remain completeable via the OpenShift native **Observe → Metrics**, `oc adm top`, `oc logs`, Events and Argo CD. Record Perses as *not enabled for students* rather than pretending dashboard availability.

## Five-outcome readiness gates

| Outcome | Live gate |
| --- | --- |
| GitOps | Student Gitea workspace imported and current; correct Argo CD source path; full three-tier stack Synced/Healthy; student can commit |
| Multitenancy | Exercise the scoped canary from the student's own pod and the independent reference tenant. Verify the named read grant/revocation and connectivity before, during and after policy. |
| Workload | Shared quota has room for brief canary and one ParksMap RollingUpdate surge; applied quota view and real metrics accessible or sanitized instructor snapshot available |
| Investigation | WeatherNow bad readiness probe generates a new unready Pod; Events, Pod logs, CPU/memory metrics and actual ReplicaSet states are observable. Traces are optional only when instrumented |
| Lifecycle | Broken image tag produces ErrImagePull/ImagePullBackOff; Gitea repair commit appears as Argo CD revision; restored Pod Ready; HTTP Route works; both National Parks stacks untouched |

## Network canary safety

Module 2 creates and removes the disposable canary, its Service and ingress policy, and the temporary `workshop-info-reader` Role and RoleBinding in the student's GitOps project. Its policy selects only the canary label. Check that neither an existing policy nor SCC/image pull constraints prevent the **before** test. A pre-existing failure is not proof of policy isolation.

The reference tenant provides an independent identity and namespace for single-seat runs. To verify the deployed boundary between two enrolled students as well, run the partner check in Module 2 with each student's own credentials.

Confirm cleanup after each student and that quota allows the temporary Pod. Do not modify global NetworkPolicy, routes, Secrets or tenant quotas.

## Operational acceptance

- Run once using a real student and an instructor identity with restricted and approved permissions.
- Record actual Gitea clone/import, App revision, 5-module execution and rollback test results.
- Verify no data-leaking Perses datasource or elevated monitoring credentials.
- Confirm student AgenticRun creation is **not requested** and teacher/demo prompts are conceptual only.
- Validate screenshots for the updated Module 2 network canary and new Module 3 metrics/right-sizing workflow before publishing.

## Optional OpenShift 5 extension

COO 1.6 may add Lightspeed-assisted Perses dashboard capabilities beyond the core COO 1.5.5 lab workflow. With an approved provider and properly scoped metrics datasource, an instructor can ask Lightspeed for a chart of workload CPU/memory and inspect the generated PromQL/time range. Do not make AI chart creation a student completion gate; availability is dependent on the installed build and configured integrations.
