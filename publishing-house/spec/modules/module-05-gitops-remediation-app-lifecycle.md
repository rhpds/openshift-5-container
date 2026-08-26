# Module 5: GitOps Remediation & App Lifecycle

### Brief Overview
This closing hands-on module has students act on what they validated in Module 4: they push the fix back through GitOps rather than applying it imperatively, then watch OpenShift GitOps (ArgoCD) roll it out and confirm the application recovers. The module reinforces that even urgent fixes on a shared platform should go through the same declarative, auditable path as the original onboarding.

### Audience and Time
- **Personas:** Platform engineers / SREs, intermediate level
- **Prerequisites for this module:** Module 4 completed (validated root cause and candidate fix identified); Module 2's GitOps workflow (commit → sync → verify)
- **Estimated duration:** 20 minutes, hands-on

### Learning Objectives
- Implement the fix validated in Module 4 declaratively by updating the sample application's manifests in the GitOps repository
- Implement the change through GitOps and confirm ArgoCD syncs the update to the live cluster
- Monitor rollout health and ArgoCD sync status while the rolling update proceeds
- Confirm the application has recovered from the injected incident

### Lab Structure
| Section | Title | Duration |
|---------|-------|----------|
| 1 | Translate the validated fix into a manifest change | 5 min |
| 2 | Commit and push the fix | 3 min |
| 3 | Monitor the ArgoCD sync and rollout | 6 min |
| 4 | Confirm recovery | 6 min |

### Detailed Steps
1. Revisit the root cause and candidate fix identified at the end of Module 4.
2. Locate the relevant manifest(s) in the GitOps repository for the sample application (e.g., deployment spec, config, or resource settings implicated by the root cause).
3. Edit the manifest(s) to encode the validated fix.
4. Commit and push the change to the GitOps repository.
5. Open the ArgoCD console/CLI and observe the Application transition into an out-of-sync state, then trigger (or wait for automatic) sync.
6. Watch the rolling update proceed, monitoring pod status transitions (e.g., new ReplicaSet scaling up, old ReplicaSet scaling down) and ArgoCD's sync/health status indicators throughout.
7. If ArgoCD reports a sync error or the rollout stalls, inspect the reported condition and correct the manifest, repeating the commit/sync cycle.
8. Once the sync reports Healthy/Synced, re-check the metrics, logs, and/or endpoint that showed the original incident symptom in Module 4.
9. Confirm the application is behaving normally (health checks passing, error rate/latency back to baseline, or endpoint reachable as expected).
10. Reflect on the end-to-end flow completed across the lab: onboard via GitOps → operate under contention → investigate with AI assistance → remediate via GitOps.

### Key Takeaways
- Remediation should follow the same GitOps discipline as onboarding — declared in Git, reconciled by ArgoCD, not applied by hand
- ArgoCD's sync and health status are the operational signal to watch during a rolling update, not just pod count
- Confirming recovery means re-checking the same signals that revealed the original incident, not just assuming the fix worked
- A platform team's job spans the full lifecycle: onboarding, operating under contention, investigating incidents, and remediating declaratively

### Infrastructure Notes
Relies on the same OpenShift GitOps (ArgoCD) bootstrap used in Module 2 and the sample application/fault workload from Module 4. Students confirm success visually via the OpenShift console (rollout status, ArgoCD sync status, application recovery) — this lab is trust-based with no solve/validate automation, per the design's assessment strategy. Exact rollout tuning parameters are TBD pending the infrastructure phase.
