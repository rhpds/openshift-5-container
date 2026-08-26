# Module 3: Workload Management & Resource Controls

### Brief Overview
With the sample application onboarded, this hands-on module puts students in the position of managing resource contention on a shared cluster where many workloads compete for the same capacity. Students apply ResourceQuotas and LimitRanges to their namespace, use PriorityClasses to influence scheduling behavior under contention, and then analyze actual resource usage to right-size their deployment.

### Audience and Time
- **Personas:** Platform engineers / SREs, intermediate level
- **Prerequisites for this module:** Module 2 completed (application onboarded, namespace/RBAC/NetworkPolicy in place); familiarity with basic OpenShift resource requests/limits concepts
- **Estimated duration:** 20 minutes, hands-on

### Learning Objectives
- Manage resource contention across shared workloads by configuring ResourceQuotas and LimitRanges on the student's namespace
- Configure PriorityClasses so critical workloads are favored by the scheduler when the shared cluster is under contention
- Analyze workload resource usage (requests/limits vs. actual consumption) on the shared cluster using OpenShift console/CLI metrics
- Right-size the sample application's deployment based on the observed usage data

### Lab Structure
| Section | Title | Duration |
|---------|-------|----------|
| 1 | Observe baseline contention on the shared cluster | 3 min |
| 2 | Apply a ResourceQuota and LimitRange to the namespace | 5 min |
| 3 | Apply a PriorityClass to the sample application | 4 min |
| 4 | Analyze actual resource usage | 4 min |
| 5 | Right-size the deployment | 4 min |

### Detailed Steps
1. Review the sample application's current deployment manifest and note that it has no resource requests/limits defined, or has values inherited from defaults.
2. Use the OpenShift console (or `oc adm top` / metrics dashboards) to observe current resource pressure on the shared cluster and where the student's workload sits relative to other tenants.
3. Author and apply a ResourceQuota manifest scoping total CPU/memory consumption for the student's namespace.
4. Author and apply a LimitRange manifest establishing default and max/min request-limit values for containers in the namespace.
5. Attempt to deploy or scale a workload that exceeds the quota and observe that OpenShift rejects it, confirming the quota is enforced.
6. Author and apply a PriorityClass, then assign it to the sample application's pod spec so it is prioritized appropriately relative to lower-priority workloads sharing the cluster.
7. Simulate contention (e.g., scale a lower-priority companion workload) and observe scheduling behavior — the prioritized workload continues to be scheduled/retained while lower-priority pods are preempted or pending.
8. Use the OpenShift console/CLI to compare the sample application's actual CPU/memory usage against its configured requests and limits.
9. Adjust the deployment's resource requests/limits to better match observed usage and reapply (via GitOps, consistent with the onboarding pattern from Module 2, or directly if the module treats this as a live tuning exercise).
10. Confirm the updated deployment is scheduled successfully and usage now tracks more closely with the configured requests/limits.

### Key Takeaways
- ResourceQuotas cap total namespace consumption; LimitRanges set per-container defaults and bounds — both are needed to manage a shared cluster responsibly
- PriorityClasses determine which workloads win when the scheduler must make trade-offs under contention
- Resource requests/limits should be informed by observed usage, not guessed at onboarding time
- Right-sizing is an iterative operating practice, not a one-time setup step

### Infrastructure Notes
Assumes a shared, multi-user cluster already under some baseline load from other concurrent students (per design: up to 30 concurrent students on one cluster), which is what makes contention observable. Exact quota/limit values, PriorityClass tiers, and cluster sizing are TBD pending the infrastructure phase; this module should reference relative levels (e.g., "a lower-priority companion workload") rather than fixed numbers until those are confirmed.
