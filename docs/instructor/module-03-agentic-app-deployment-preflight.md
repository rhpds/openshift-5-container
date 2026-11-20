# Module 3 — Workload Management and GitOps Right-Sizing: Instructor Preflight

## Mission and guardrail

Module 3 is now a **25-minute, five-mission workload-management lab**. Students compare existing shared quota and ParksMap resource allocations against measured usage, optionally make one **bounded, justified** request adjustment in their own Gitea workspace, then verify Argo CD and both applications remain healthy. The old Module 3 readiness-probe incident has been removed to avoid duplicating the WeatherNow readiness incident in Module 4.

**Student AgenticRuns remain deferred.** Do not create one, run the retired `automation/scripts/create-module03-agentic-run.sh`, grant broad sandbox/cluster RBAC or demonstrate cross-tenant reads. The script is historical instructor-only code and is **not part of the curriculum**. See `docs/instructor/agentic-student-isolation-gate.md`.

## Required tenant baseline

- `user-<guid>-demo` contains a healthy original National Parks stack.
- `user-<guid>-gitops` contains healthy `parksmap`, `nationalparks`, and `mongodb-nationalparks` Deployments, PVC Bound, and `Application/national-parks-settings` Synced/Healthy.
- Every student Gitea main contains a complete `national-parks/04-parksmap-frontend.yaml` with ParksMap requests **75m CPU, 192Mi memory**, limits **500m CPU, 768Mi memory**, and readiness port `http`.
- The **same** shared tenant ClusterResourceQuota covers both namespaces. Verify spare CPU/memory request and limit capacity for a rolling update; do not expect students to modify the quota.
- Only student-account read access to `AppliedClusterResourceQuota` is attempted; if denied, provide a sanitized snapshot. Never elevate student cluster privileges.
- Instructor has validated workload metrics and the optional COO/Perses project dashboard using `cluster-observability-workshop-preflight.md`. Students need **time range** and **actual** CPU/memory usage, not only requests and limits.

Instructor checks (use the correct student):
```bash
STUDENT=user-xxxxx
oc get deployments -n "$STUDENT-demo"
oc get deployments -n "$STUDENT-gitops"
oc get application national-parks-settings -n "$STUDENT-gitops" -o json | jq '{sync:.status.sync.status,health:.status.health.status,revision:.status.sync.revision}'
oc get deployment parksmap -n "$STUDENT-gitops" -o json | jq '.spec.template.spec.containers[0].resources'
oc describe clusterresourcequota "tenant-$STUDENT"
oc adm top pods -n "$STUDENT-gitops" --containers
```

## Sizing exercise

The worksheet deliberately allows **no change** when observations are inconclusive. A justified adjustment is narrow: ParksMap CPU request 75m -> **50m** or **100m**, or memory request 192Mi -> **256Mi** only when working-set evidence supports it. Preserve 500m/768Mi limits and other fields. GitOps, not `oc patch`, reconciles the student's commit.

Do not ask students to saturate the cluster, deploy stress workloads, change PriorityClass or expand the shared quota. A discussion of rolling-update surge and scheduler tradeoffs is the contention lesson; the safe resource edit is the practical skill.

## Acceptance

- [ ] Two healthy National Parks stacks and student Gitea full-stack repo exist.
- [ ] Quota headroom supports one ParksMap replacement Pod.
- [ ] Students can access actual per-project metrics or instructor-provided authentic evidence.
- [ ] COO/Perses dashboard queries cannot access another tenant; otherwise use native metrics instead.
- [ ] Students record usage, requests, limits, shared quota and a **reasoned sizing/no-change decision**.
- [ ] Any edit is source-controlled, appropriately bounded and reconciled through Argo CD.
- [ ] ParksMap Route is HTTP 200; GitOps is Synced/Healthy; original application remains intact.
- [ ] No student AgenticRun or cluster-wide policy change is required.

## Recovery

If a student makes an unsupported request edit or the rollout stalls, restore **only** the original requests (75m CPU / 192Mi memory) in that student's Gitea `national-parks/04-parksmap-frontend.yaml`, commit and verify Argo CD reconciliation. Do not edit live GitOps-managed Deployments or delete databases, PVCs or Secrets.

Module 4 begins from a **healthy** WeatherNow baseline and introduces the only readiness-probe incident in this workshop.
