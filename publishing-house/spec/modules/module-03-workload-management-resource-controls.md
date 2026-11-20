# Module 3 — Workload Management and Right-Sizing (Implemented)

## Purpose

Operate the existing complete National Parks GitOps stack after Module 2. Students compare actual CPU/memory measurements, existing requests/limits and shared tenant ClusterResourceQuota, then make a conservative, justified resource request adjustment through their *own Gitea* (or document why no change is appropriate). They verify Argo CD revision, Deployment health and original application unaffected.

## Duration and scope

25 minutes; 5 missions. Each student owns a `user-<guid>-demo` and `user-<guid>-gitops` namespace. No student may change cluster-scoped quotas, LimitRanges, PriorityClasses or other tenants' resources. No load-generation/stress test is run across the shared 30-person cluster.

## Learning objectives

1. Distinguish measured CPU/memory utilization from requests, limits and quota.
2. Observe actual workload metrics (COO/Perses when instructor-configured; OpenShift native metrics or authentic instructor snapshot fallback).
3. Describe the impact of Deployment rolling-update surge on quota headroom and scheduler capacity.
4. Choose a bounded request adjustment (CPU 75m -> 50m or 100m; memory 192Mi -> 256Mi) only when supported by observations; otherwise document *no change*.
5. Deliver any change through student Gitea and Argo CD, verify Ready/Synced/Healthy and Route, and leave two National Parks stacks healthy.

## Five missions

| Mission | Focus | Time |
| --- | --- | --- |
| 1 | Baseline, requests/limits | 4 min |
| 2 | Real workload CPU/memory metrics | 5 min |
| 3 | Shared quota headroom and tradeoff | 5 min |
| 4 | GitOps request tuning, if justified | 7 min |
| 5 | Deployment and endpoint verification | 4 min |

## Instructor release gates

Follow `docs/instructor/cluster-observability-workshop-preflight.md` and `docs/instructor/module-03-agentic-app-deployment-preflight.md`. Valid metrics and a tenant-scoped dashboard are preferred; if unavailable, no invented metric or unjustified change is allowed. Instructor verifies quota headroom before the commit and monitors for rollout surge failures.

The older Module 3 agentic readiness scenario is retired to avoid duplicating the readiness incident now in Module 4. Student AgenticRuns remain deferred pending the cross-namespace sandbox/isolation fix. No optional AgenticRun is required for completion.
