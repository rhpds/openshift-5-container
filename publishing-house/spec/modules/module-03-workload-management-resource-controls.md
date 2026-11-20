# Module 3 — Workload Management and Right-Sizing (Implemented)

### Brief Overview

Operate the existing complete National Parks GitOps stack after Module 2. Students compare actual CPU/memory measurements, existing requests/limits and shared tenant ClusterResourceQuota, then make a conservative, justified resource request adjustment through their *own Gitea* (or document why no change is appropriate). They verify Argo CD revision, Deployment health and original application unaffected.

### Audience and Time

25 minutes; 5 missions. Each student owns a `user-<guid>-demo` and `user-<guid>-gitops` namespace. No student may change cluster-scoped quotas, LimitRanges, PriorityClasses or other tenants' resources. No load-generation/stress test is run across the shared 30-person cluster.

### Learning Objectives

1. Distinguish measured CPU/memory utilization from requests, limits and quota.
2. Observe actual workload metrics (COO/Perses when instructor-configured; OpenShift native metrics or authentic instructor snapshot fallback).
3. Describe the impact of Deployment rolling-update surge on quota headroom and scheduler capacity.
4. Choose a bounded request adjustment (CPU 75m -> 50m or 100m; memory 192Mi -> 256Mi) only when supported by observations; otherwise document *no change*.
5. Deliver any change through student Gitea and Argo CD, verify Ready/Synced/Healthy and Route, and leave two National Parks stacks healthy.

### Lab Structure

| Mission | Focus | Time |
| --- | --- | --- |
| 1 | Baseline, requests/limits | 4 min |
| 2 | Real workload CPU/memory metrics | 5 min |
| 3 | Shared quota headroom and tradeoff | 5 min |
| 4 | GitOps request tuning, if justified | 7 min |
| 5 | Deployment and endpoint verification | 4 min |

### Detailed Steps

1. Record the original National Parks and GitOps Deployments, resource requests/limits, and tenant quota without modifying them.
2. Inspect an authenticated student-scoped COO/Perses CPU/memory dashboard or native workload metrics, recording time range and actual measurements.
3. Explain the temporary quota cost of old and replacement Pods during a RollingUpdate.
4. Choose bounded CPU/memory requests based on observation, or record why *no change* is the correct decision.
5. If justified, edit ParksMap requests in the student's own Gitea main and watch Argo CD reconcile. Never patch a live GitOps-managed Deployment.
6. Verify ParksMap, API, MongoDB, GitOps and the original -demo stack are healthy.

### Key Takeaways

Measured usage differs from scheduler reservations and enforced limits. Shared ClusterResourceQuota includes two namespaces, so values should not be double-counted. Safe right-sizing is a measured, reversible GitOps decision, not a forced change to prove activity.

### Infrastructure Notes

Follow `docs/instructor/cluster-observability-workshop-preflight.md` and `docs/instructor/module-03-agentic-app-deployment-preflight.md`. Valid metrics and a tenant-scoped dashboard are preferred; if unavailable, no invented metric or unjustified change is allowed. Instructor verifies quota headroom before the commit and monitors for rollout surge failures.

The older Module 3 agentic readiness scenario is retired to avoid duplicating the readiness incident now in Module 4. Student AgenticRuns remain deferred pending the cross-namespace sandbox/isolation fix. No optional AgenticRun is required for completion.
